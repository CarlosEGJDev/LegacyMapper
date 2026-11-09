"""Hierarchical request planning, stable request identity and coverage assessment (no provider, no source access).

Identity is derived only from semantic inputs: schema/prompt versions, interpretation type, stable entity identity, the exact
selected Evidence facts, the semantic hashes of the dependencies and the provider/model *policy*. Never from timestamps or
machine-local paths, so the same baseline content yields the same identities on any machine.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import context as C
from .inventory import Inventory, Project, Solution
from .models import (CONTROLLED_ERROR, FINAL_STATES, HUMAN_AND_MACHINE, MACHINE_ONLY, PENDING, PROMPT_VERSION, SCHEMA_VERSION,
                     UNRESOLVED_NO_SOLUTION, Fact, sha256_object)

HUMAN_SECTIONS = ("purpose", "responsibilities", "consumers", "dependencies", "business_flow", "data_interactions")
NO_SOLUTION_REASON = "NO_RESOLVABLE_SOLUTION"
INSUFFICIENT_REASON = "INSUFFICIENT_EVIDENCE"


@dataclass
class Plan:
    kind: str
    entity_id: str                  # stable entity key, e.g. project id, "<project id>#v0", solution id, "SYSTEM"
    label: str
    facts: list
    deps: list = field(default_factory=list)       # semantic hashes of accepted dependencies
    meta: dict = field(default_factory=dict)

    def identity(self, policy: dict) -> str:
        return "SYS-" + sha256_object({
            "schema": SCHEMA_VERSION, "prompt": PROMPT_VERSION, "kind": self.kind, "entity": self.entity_id,
            "facts": [f.identity_view() for f in self.facts], "deps": sorted(self.deps), "policy": policy})[:40]

    @property
    def key(self) -> str:
        return f"{self.kind}|{self.entity_id}"


@dataclass
class Item:
    plan: Plan
    identity: str
    record: dict | None = None
    error: str | None = None

    @property
    def terminal(self) -> bool:
        return self.record is not None or self.error is not None


@dataclass
class ProjectCoverage:
    project: Project
    state: str = PENDING
    reason: str = ""
    items: list = field(default_factory=list)
    omitted_views: int = 0

    def record(self, kind: str):
        return [i.record for i in self.items if i.plan.kind == kind and i.record]


@dataclass
class UnitCoverage:
    state: str = PENDING
    reason: str = ""
    item: Item | None = None
    flow: Item | None = None


@dataclass
class Assessment:
    projects: dict = field(default_factory=dict)
    solutions: dict = field(default_factory=dict)
    system: UnitCoverage = field(default_factory=UnitCoverage)

    @property
    def pending(self) -> list:
        out = [f"PROJECT {c.project.display}" for c in self.projects.values() if c.state == PENDING]
        out += [f"SOLUTION {k}" for k, c in self.solutions.items() if c.state == PENDING]
        if self.system.state == PENDING:
            out.append("SYSTEM")
        return out

    @property
    def complete(self) -> bool:
        return not self.pending


def semantic_hash(record: dict | None) -> str:
    return sha256_object(record["semantic"]) if record else "none"


def plan_project(inv: Inventory, p: Project) -> Plan | None:
    facts = C.project_facts(inv, p)
    if not C.has_sufficient_evidence(facts):
        return None
    return Plan("PROJECT", p.id, p.display, facts, meta={"project_id": p.id})


def plan_views(inv: Inventory, p: Project) -> tuple[list[Plan], int]:
    chunks, omitted = C.view_chunks(inv, p)
    return [Plan("VIEW", f"{p.id}#v{i}", f"{p.display} · vistas {i + 1}", facts, meta={"project_id": p.id, "chunk": i})
            for i, facts in enumerate(chunks)], omitted


def plan_data(inv: Inventory, p: Project) -> Plan | None:
    facts = C.data_facts(inv, p)
    return Plan("DATA", p.id, p.display, facts, meta={"project_id": p.id}) if facts else None


def plan_flow(inv: Inventory, s: Solution) -> Plan | None:
    facts = C.flow_facts(inv, s)
    return Plan("FLOW", s.id, s.display, facts, meta={"solution_id": s.id}) if facts else None


def _children_for_solution(inv: Inventory, s: Solution, cov: dict, flow_record: dict | None) -> tuple[list, list]:
    children, deps = [], []
    for pid in s.project_ids:
        pc = cov[pid]
        rec = (pc.record("PROJECT") or [None])[0]
        text, cert = C.semantic_fact_text(f"Proyecto {pc.project.display}", rec, pc.reason or "")
        children.append(("child", text, cert, (pid,)))
        deps.append(f"{pid}:{semantic_hash(rec)}")
    if flow_record:
        for claim in flow_record["semantic"].get("relations", [])[:12]:
            if claim["status"] != "UNRESOLVED":
                children.append(("child", C._clip(f"Relación entre proyectos [{claim['status'].capitalize()}]: {claim['text']}"),
                                 "confirmed" if claim["status"] == "CONFIRMED" else "inferred", (s.id,)))
        deps.append(f"{s.id}:flow:{semantic_hash(flow_record)}")
    return children, deps


def plan_solution(inv: Inventory, s: Solution, cov: dict, flow_record: dict | None) -> Plan:
    children, deps = _children_for_solution(inv, s, cov, flow_record)
    facts = C.child_facts(Fact("", "name", "confirmed", f"Nombre de la solución: {s.name}.", (s.id,)), children)
    return Plan("SOLUTION", s.id, s.display, facts, deps=deps, meta={"solution_id": s.id})


def plan_system(inv: Inventory, units: dict) -> Plan:
    children, deps = [], []
    for s in inv.solutions:
        unit = units[s.id]
        rec = unit.item.record if unit.item else None
        text, cert = C.semantic_fact_text(f"Solución {s.display}", rec, unit.reason or "")
        children.append(("child", text, cert, (s.id,)))
        deps.append(f"{s.id}:{semantic_hash(rec)}")
    facts = C.child_facts(Fact("", "name", "confirmed", "Sistema legado analizado.", ()), children)
    return Plan("SYSTEM", "SYSTEM", "Sistema", facts, deps=deps)


def _project_state(item: Item) -> tuple[str, str]:
    if item.record:
        sem = item.record["semantic"]
        meaningful = any(c["status"] in ("CONFIRMED", "INFERRED") for s in HUMAN_SECTIONS for c in sem.get(s, []))
        return (HUMAN_AND_MACHINE, "") if meaningful else (MACHINE_ONLY, "NO_CONFIRMED_OR_INFERRED_CLAIMS")
    if item.error:
        return CONTROLLED_ERROR, item.error
    return PENDING, ""


def assess(inv: Inventory, store, policy: dict, errors: dict) -> Assessment:
    """Pure function of (baseline, persisted records, controlled errors): shared by the orchestrator and the projections."""
    out = Assessment()

    def item_for(plan: Plan) -> Item:
        ident = plan.identity(policy)
        return Item(plan, ident, store.get(plan.kind, ident), errors.get(f"{plan.key}|{ident}"))

    for p in inv.ordered_projects():
        pc = ProjectCoverage(p)
        out.projects[p.id] = pc
        if not p.solution_ids:
            pc.state, pc.reason = UNRESOLVED_NO_SOLUTION, NO_SOLUTION_REASON
            continue
        main = plan_project(inv, p)
        if main is None:
            pc.state, pc.reason = MACHINE_ONLY, INSUFFICIENT_REASON
            continue
        pc.items.append(item_for(main))
        views, pc.omitted_views = plan_views(inv, p)
        pc.items.extend(item_for(v) for v in views)
        data = plan_data(inv, p)
        if data:
            pc.items.append(item_for(data))
        pc.state, pc.reason = _project_state(pc.items[0])
        if pc.state != PENDING and any(not i.terminal for i in pc.items[1:]):
            pc.state, pc.reason = PENDING, "CHILD_REQUESTS_PENDING"

    for s in inv.solutions:
        unit = UnitCoverage()
        out.solutions[s.id] = unit
        if not s.project_ids:
            unit.state, unit.reason = MACHINE_ONLY, "NO_PROJECTS"
            continue
        if any(out.projects[pid].state == PENDING for pid in s.project_ids):
            unit.reason = "PROJECTS_PENDING"
            continue
        fplan = plan_flow(inv, s)
        unit.flow = item_for(fplan) if fplan else None
        if unit.flow and not unit.flow.terminal:
            unit.reason = "FLOW_PENDING"
            continue
        flow_record = unit.flow.record if unit.flow else None
        unit.item = item_for(plan_solution(inv, s, out.projects, flow_record))
        unit.state, unit.reason = (("DOCUMENTED", "") if unit.item.record else (CONTROLLED_ERROR, unit.item.error) if unit.item.error else (PENDING, ""))

    if inv.solutions and all(u.state != PENDING for u in out.solutions.values()):
        usable = {k: u for k, u in out.solutions.items()}
        sysitem = item_for(plan_system(inv, usable))
        out.system.item = sysitem
        out.system.state, out.system.reason = (("DOCUMENTED", "") if sysitem.record else (CONTROLLED_ERROR, sysitem.error) if sysitem.error else (PENDING, ""))
    elif not inv.solutions:
        out.system.state, out.system.reason = MACHINE_ONLY, "NO_SOLUTIONS"
    else:
        out.system.reason = "SOLUTIONS_PENDING"
    return out


def final_state_ok(state: str) -> bool:
    return state in FINAL_STATES
