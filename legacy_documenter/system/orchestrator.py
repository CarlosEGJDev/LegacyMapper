"""Full-system hierarchical AI orchestration with persistence, bounded retries, quota-safe interruption and resume.

Order (the order is the contract): PROJECT -> VIEW -> DATA (per project), FLOW -> SOLUTION (per solution group, checkpoint after
each group), SYSTEM. An accepted persisted response for the same request identity is replayed with 0 provider calls.
The provider is never called per source file and never with the whole corpus: every request carries a bounded fact set.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from legacy_documenter.llm.contracts import LLMRequest

from . import planner as P
from .inventory import Inventory, load_inventory
from .models import (CONTEXT_SCHEMA_VERSION, COVERAGE_CONTRACT, FINAL_STATES, KINDS, PENDING, PROMPT_VERSION, SCHEMA_VERSION,
                     SEMANTIC_MODELS, SECTIONS, output_schema, sha256_text, validate_semantic, canonical, sha256_object)
from .store import RequestStore

SYSTEM_INSTRUCTION = (
    "Eres un analista que explica a personas no técnicas cómo se comporta un sistema legado, a partir de hechos estáticos "
    "extraídos por un analizador determinista. Explica COMPORTAMIENTO y responsabilidades, no resumas archivos ni cuentes elementos. "
    "Escribe en español claro. Usa SOLO los hechos del contexto y cita en `refs` los `ref` de los hechos que respaldan cada afirmación. "
    "No inventes actores, requisitos, módulos, sistemas externos ni significado de negocio; no deduzcas el área de negocio solo por "
    "el nombre de un proyecto o carpeta. Existir no es estar alcanzable, estar alcanzable no es usarse observablemente y la ausencia "
    "de evidencia de uso NO es obsolescencia: nunca llames obsoleto, muerto o sin uso a un componente. Cada afirmación lleva un estado: "
    "CONFIRMED (lo respalda un hecho confirmado), INFERRED (deducción razonable, nunca la presentes como confirmada) o UNRESOLVED "
    "(lo que no se puede determinar; no lo ocultes). No uses identificadores de Evidencia, rutas de archivos ni números de línea. "
    "Responde únicamente con un objeto JSON que cumpla el esquema.")
USER_INSTRUCTIONS = {
    "PROJECT": "Explica qué hace el proyecto descrito en `facts`: propósito observable, responsabilidades, quién lo consume, de qué depende, flujo de negocio y de datos. Si no tiene interfaz, no inventes pantallas.",
    "VIEW": "Explica el comportamiento observable de cada vista de `facts` (qué ocurre al abrirla y al accionar sus eventos). Pon el nombre de la vista en `subject`.",
    "DATA": "Explica con qué datos y procedimientos interactúa el proyecto y desde qué componentes, sin inferir significado de negocio solo por nombres.",
    "FLOW": "Explica las relaciones entre proyectos de la solución: quién invoca a quién y qué papel cumple esa relación.",
    "SOLUTION": "Explica qué hace la solución a partir de las interpretaciones de sus proyectos: subsistemas, responsabilidades, interacciones y datos importantes.",
    "SYSTEM": "Explica qué parece hacer el sistema completo a partir de sus soluciones: soluciones principales, rutas de interacción importantes, datos y relaciones entre proyectos.",
}
QUOTA = re.compile(r"(?i)quota|rate.?limit|too many requests|\b429\b|usage limit|exhaust|premium request")
RETRYABLE = {"INVALID_STRUCTURED_OUTPUT", "TIMEOUT", "PROVIDER_ERROR", "VALIDATION_REJECTED_ALL"}
UNAVAILABLE = {"PROVIDER_CONFIGURATION_ERROR"}


class InterruptRun(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass
class RunOptions:
    max_requests: int | None = None
    max_retries: int = 2
    max_consecutive_failures: int = 5


@dataclass
class Metrics:
    requests: int = 0
    successes: int = 0
    retries: int = 0
    replays: int = 0
    failures: int = 0
    by_kind: dict = field(default_factory=lambda: {k: {"requests": 0, "successes": 0, "replays": 0, "failures": 0} for k in KINDS})

    def as_dict(self) -> dict:
        return {"provider_requests": self.requests, "provider_successes": self.successes, "provider_retries": self.retries,
                "provider_replays": self.replays, "provider_failures": self.failures, "by_kind": self.by_kind}


@dataclass
class RunResult:
    status: str                      # COMPLETE | COMPLETE_WITH_CONTROLLED_ERRORS | INTERRUPTED_<reason>
    exit_code: int
    metrics: Metrics
    assessment: P.Assessment
    coverage_path: Path
    state: dict


def _parse(resp) -> dict | None:
    if isinstance(resp.parsed_output, dict):
        return resp.parsed_output
    body = (resp.content or "").strip()
    if body.startswith("```"):
        body = body.strip("`")
        body = body[body.find("{"):]
    try:
        value = json.loads(body, strict=False)
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


class Orchestrator:
    def __init__(self, inv: Inventory, store: RequestStore, provider, policy: dict, options: RunOptions) -> None:
        self.inv, self.store, self.provider, self.policy, self.opts = inv, store, provider, policy, options
        self.m = Metrics()
        self.errors: dict[str, str] = {}
        self.consecutive = 0
        prior = store.load_state()
        self.prior = prior
        self.snapshot = (inv.identity.portable_evidence_sha256 or inv.identity.manifest_sha256 or "")[:32]

    # ------------------------------------------------------------------ one request
    def _build_request(self, plan: P.Plan, identity: str, schema: dict) -> LLMRequest:
        context = {"entity": plan.label, "level": plan.kind, "facts": [f.for_provider() for f in plan.facts], "sections": list(SECTIONS[plan.kind])}
        return LLMRequest(
            purpose="FUNCTIONAL_INTERPRETATION", system_instruction=SYSTEM_INSTRUCTION, user_instruction=USER_INSTRUCTIONS[plan.kind],
            context=context, context_package_id=f"CTX-SYSTEM-{plan.kind}-{identity[-16:]}", context_schema_version=CONTEXT_SCHEMA_VERSION,
            source_snapshot=self.snapshot, max_output_tokens=3500, structured_output=True, output_contract=schema,
            metadata={"identity": identity, "claim_policy": {"status": ["CONFIRMED", "INFERRED", "UNRESOLVED"],
                                                             "forbidden": ["obsolete", "unused", "invented actors/use cases/modules"]}})

    def _call(self, request: LLMRequest, schema: dict):
        started = time.perf_counter()
        try:
            resp = self.provider.structured_generate(request, schema)
            return resp, None, round(time.perf_counter() - started, 2)
        except Exception as exc:                                    # a raising provider is a failure, never a crash
            return None, type(exc).__name__, round(time.perf_counter() - started, 2)

    def execute(self, plan: P.Plan) -> P.Item:
        identity = plan.identity(self.policy)
        existing = self.store.get(plan.kind, identity)
        if existing:
            self.m.replays += 1
            self.m.by_kind[plan.kind]["replays"] += 1
            return P.Item(plan, identity, existing)
        schema = output_schema(plan.kind)
        request = self._build_request(plan, identity, schema)
        reason = "NOT_ATTEMPTED"
        for attempt in range(1, self.opts.max_retries + 2):
            if self.opts.max_requests is not None and self.m.requests >= self.opts.max_requests:
                raise InterruptRun("REQUEST_BUDGET_REACHED")
            self.m.requests += 1
            self.m.by_kind[plan.kind]["requests"] += 1
            if attempt > 1:
                self.m.retries += 1
            resp, exc_name, seconds = self._call(request, schema)
            status = resp.status if resp is not None else "PROVIDER_ERROR"
            message = ""
            if resp is not None and resp.error is not None:
                message = f"{resp.error.error_code} {(resp.error.details or {}).get('sanitized_message') or resp.error.message}"
            if exc_name:
                message = f"provider raised {exc_name}"
            entry = {"identity": identity, "kind": plan.kind, "entity": plan.entity_id, "attempt": attempt, "status": status, "seconds": seconds}
            if status == "RATE_LIMITED" or (status != "SUCCESS" and QUOTA.search(message)):
                self.store.append_attempt(identity, {**entry, "outcome": "QUOTA_EXHAUSTED"})
                raise InterruptRun("QUOTA_EXHAUSTED")
            if status in UNAVAILABLE:
                self.store.append_attempt(identity, {**entry, "outcome": "PROVIDER_UNAVAILABLE"})
                raise InterruptRun("PROVIDER_UNAVAILABLE")
            if status == "SUCCESS":
                parsed = _parse(resp)
                validation = validate_semantic(plan.kind, parsed, plan.facts, identity)
                if validation.accepted_count > 0:
                    record = self._record(plan, identity, request, resp, validation, attempt)
                    self.store.put_accepted(record)
                    self.store.append_attempt(identity, {**entry, "outcome": "ACCEPTED", "rejected": len(validation.rejected)})
                    self.m.successes += 1
                    self.m.by_kind[plan.kind]["successes"] += 1
                    self.consecutive = 0
                    return P.Item(plan, identity, record)
                status = "VALIDATION_REJECTED_ALL"
                message = ",".join(sorted({r["reason"] for r in validation.rejected})) or "EMPTY"
            self.m.failures += 1
            self.m.by_kind[plan.kind]["failures"] += 1
            self.consecutive += 1
            reason = f"{status}" + (f": {message}" if message else "")
            self.store.append_attempt(identity, {**entry, "outcome": "FAILED", "status": status, "detail": message[:300]})
            if self.consecutive >= self.opts.max_consecutive_failures:
                raise InterruptRun("PROVIDER_FAILING_REPEATEDLY")
            if status not in RETRYABLE:
                break
        self.errors[f"{plan.key}|{identity}"] = reason
        return P.Item(plan, identity, None, reason)

    def _record(self, plan, identity, request, resp, validation, attempt) -> dict:
        info = self.provider.model_info()
        content = resp.content or ""
        return {
            "identity": identity, "kind": plan.kind, "entity_id": plan.entity_id, "label": plan.label, "accepted": True,
            "semantic_model": SEMANTIC_MODELS[plan.kind], "schema_version": SCHEMA_VERSION, "prompt_version": PROMPT_VERSION,
            "input_hash": sha256_object({"facts": [f.identity_view() for f in plan.facts], "deps": sorted(plan.deps)}),
            "dependency_hashes": sorted(plan.deps), "policy": self.policy, "meta": plan.meta,
            "facts": [f.identity_view() for f in plan.facts],
            "request": {"llm_request_id": request.request_id, "context_package_id": request.context_package_id, "attempt": attempt},
            "response": {"content": content, "content_sha256": sha256_text(content), "status": resp.status},
            "validation": {"schema_ok": validation.schema_ok, "accepted_claims": validation.accepted_count,
                           "rejected_claims": validation.rejected, "downgraded_to_inferred": validation.downgraded},
            "semantic": validation.accepted,
            "provider": {"provider_id": getattr(info, "provider_id", ""), "model_id": resp.model_id or getattr(info, "model_id", ""),
                         "synthetic": bool((getattr(info, "metadata", None) or {}).get("synthetic"))},
            "usage": {"input_tokens": getattr(resp.usage, "input_tokens", None), "output_tokens": getattr(resp.usage, "output_tokens", None)} if resp.usage else {},
        }

    # ------------------------------------------------------------------ hierarchy
    def do_project(self, pid: str) -> None:
        p = self.inv.projects[pid]
        plan = P.plan_project(self.inv, p)
        if plan is None:
            return
        self.execute(plan)
        views, _ = P.plan_views(self.inv, p)
        for v in views:
            self.execute(v)
        data = P.plan_data(self.inv, p)
        if data:
            self.execute(data)

    def run_hierarchy(self) -> None:
        done: set[str] = set()
        for s in self.inv.solutions:
            for pid in s.project_ids:
                if pid not in done:
                    done.add(pid)
                    self.do_project(pid)
            self.checkpoint("RUNNING")
            flow = P.plan_flow(self.inv, s)
            flow_item = self.execute(flow) if flow else None
            a = P.assess(self.inv, self.store, self.policy, self.errors)
            if s.project_ids and a.solutions[s.id].reason not in ("PROJECTS_PENDING", "FLOW_PENDING"):
                self.execute(P.plan_solution(self.inv, s, a.projects, flow_item.record if flow_item else None))
            self.checkpoint("RUNNING")
        a = P.assess(self.inv, self.store, self.policy, self.errors)
        if self.inv.solutions and all(u.state != PENDING for u in a.solutions.values()):
            self.execute(P.plan_system(self.inv, a.solutions))

    # ------------------------------------------------------------------ checkpoint
    def checkpoint(self, run_status: str, preflight: dict | None = None) -> dict:
        a = P.assess(self.inv, self.store, self.policy, self.errors)
        state = coverage_manifest(self.inv, a, self.policy, self.errors, run_status)
        prior_metrics = (self.prior.get("cumulative_metrics") or {})
        state["this_run_metrics"] = self.m.as_dict()
        state["cumulative_metrics"] = _add_metrics(prior_metrics, self.m.as_dict())
        state["runs"] = list(self.prior.get("runs") or [])
        if run_status != "RUNNING":
            state["runs"].append({"run_index": len(state["runs"]) + 1, "status": run_status, **self.m.as_dict()})
        if preflight is not None:
            state["preflight"] = preflight
        elif self.prior.get("preflight"):
            state["preflight"] = self.prior["preflight"]
        self.store.save_state(state)
        return state


def _add_metrics(prior: dict, now: dict) -> dict:
    out = {k: int(prior.get(k, 0)) + int(now.get(k, 0)) for k in ("provider_requests", "provider_successes", "provider_retries", "provider_replays", "provider_failures")}
    by = {}
    for kind in KINDS:
        base = (prior.get("by_kind") or {}).get(kind, {})
        cur = (now.get("by_kind") or {}).get(kind, {})
        by[kind] = {k: int(base.get(k, 0)) + int(cur.get(k, 0)) for k in ("requests", "successes", "replays", "failures")}
    out["by_kind"] = by
    return out


def coverage_manifest(inv: Inventory, a: P.Assessment, policy: dict, errors: dict, run_status: str) -> dict:
    projects = []
    for pc in a.projects.values():
        p = pc.project
        projects.append({
            "project_id": p.id, "stable_identity": p.identity, "name": p.name, "display": p.display, "path": p.path,
            "solution_ids": list(p.solution_ids), "state": pc.state, "reason": pc.reason,
            "human_documentation_applicable": pc.state == "HUMAN_AND_MACHINE_DOCUMENTED",
            "provider_request_ids": [i.identity for i in pc.items], "semantic_artifact_ids": ["SEM-" + i.identity for i in pc.items if i.record],
            "pending_request_ids": [i.identity for i in pc.items if not i.terminal],
            "error_request_ids": {i.identity: i.error for i in pc.items if i.error}, "views_not_interpreted": pc.omitted_views})
    solutions = []
    for s in inv.solutions:
        u = a.solutions[s.id]
        solutions.append({"solution_id": s.id, "name": s.name, "display": s.display, "path": s.path, "project_ids": list(s.project_ids),
                          "state": u.state, "reason": u.reason,
                          "provider_request_ids": [i.identity for i in (u.flow, u.item) if i],
                          "semantic_artifact_ids": ["SEM-" + i.identity for i in (u.flow, u.item) if i and i.record]})
    counts = {state: sum(1 for c in a.projects.values() if c.state == state) for state in (*FINAL_STATES, PENDING)}
    counts["projects_total"] = len(a.projects)
    counts["solutions_total"] = len(inv.solutions)
    system = a.system
    return {
        "contract": COVERAGE_CONTRACT, "schema_version": SCHEMA_VERSION, "baseline": inv.identity.as_dict(), "policy": policy,
        "run_status": run_status, "complete": a.complete, "counts": counts, "pending": a.pending, "errors": dict(sorted(errors.items())),
        "projects": projects, "solutions": solutions,
        "system": {"state": system.state, "reason": system.reason,
                   "provider_request_ids": [system.item.identity] if system.item else [],
                   "semantic_artifact_ids": ["SEM-" + system.item.identity] if system.item and system.item.record else []},
    }


def run_system_interpretation(baseline: str | Path, state_dir: str | Path, provider, policy: dict, options: RunOptions | None = None,
                              *, verify: str = "hash", preflight: dict | None = None) -> RunResult:
    """Interprets the whole system hierarchically. Reads only persisted Evidence; resumes automatically from `state_dir`."""
    opts = options or RunOptions()
    inv = load_inventory(baseline, verify)
    store = RequestStore(state_dir)
    orch = Orchestrator(inv, store, provider, policy, opts)
    status = "COMPLETE"
    try:
        orch.run_hierarchy()
    except InterruptRun as stop:
        status = f"INTERRUPTED_{stop.reason}"
    final = orch.checkpoint(status if status.startswith("INTERRUPTED") else "COMPLETE", preflight)
    a = P.assess(inv, store, policy, orch.errors)
    if not status.startswith("INTERRUPTED"):
        if not a.complete:
            status = "INTERRUPTED_PENDING_WORK"
        elif orch.errors:
            status = "COMPLETE_WITH_CONTROLLED_ERRORS"
    exit_code = 0 if status == "COMPLETE" else 1
    return RunResult(status, exit_code, orch.m, a, store.coverage_path, final)
