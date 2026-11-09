"""Deterministic machine projection (`ai/`, `internal/`) of the persisted semantic model. Never calls a provider."""
from __future__ import annotations

import json
from pathlib import Path

from legacy_documenter.utils.atomic_write import atomic_write_text

from . import planner as P
from .inventory import Inventory
from .models import SCHEMA_VERSION

KNOWLEDGE_CONTRACT = "LegacyMapperSystemKnowledge"


def _w(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, sort_keys=True, indent=1) + "\n")


def machine_claims(record: dict | None) -> dict:
    """section -> [{claim_id, text, status, subject, fact_ids}] with fact ids qualified by the record identity."""
    if not record:
        return {}
    out = {}
    for section, claims in record["semantic"].items():
        out[section] = [{"claim_id": c["claim_id"], "text": c["text"], "status": c["status"], "subject": c.get("subject", ""),
                         "fact_ids": [f"{record['identity']}:{r}" for r in c["refs"]]} for c in claims]
    return out


def _sem_id(record: dict | None) -> str | None:
    return "SEM-" + record["identity"] if record else None


def build_machine(inv: Inventory, a: P.Assessment, state: dict, out: Path, records: list[dict]) -> dict:
    ai = out / "ai"
    internal = out / "internal"
    index_by_pid = {pid: pc for pid, pc in a.projects.items()}
    called_by = {pid: sorted(inv.callers.get(pid, {})) for pid in inv.projects}
    calls = {pid: sorted(inv.callees.get(pid, {})) for pid in inv.projects}

    projects, views, data = [], [], []
    for pc in a.projects.values():
        p = pc.project
        main = (pc.record("PROJECT") or [None])[0]
        vrecs = pc.record("VIEW")
        drec = (pc.record("DATA") or [None])[0]
        for v in vrecs:
            views.append({"view_set_id": "VIEW-" + v["identity"][4:24], "project_id": p.id, "chunk": v["meta"].get("chunk"),
                          "semantic_artifact_id": _sem_id(v), "semantic": machine_claims(v)})
        if drec:
            data.append({"data_interaction_id": "DATA-" + drec["identity"][4:24], "project_id": p.id,
                         "semantic_artifact_id": _sem_id(drec), "semantic": machine_claims(drec)})
        projects.append({
            "project_id": p.id, "stable_identity": p.identity, "name": p.name, "display": p.display, "path": p.path, "slug": p.slug,
            "solution_ids": list(p.solution_ids), "state": pc.state, "reason": pc.reason,
            "human_documentation_applicable": pc.state == "HUMAN_AND_MACHINE_DOCUMENTED",
            "has_user_interface": bool(vrecs) or bool(inv.flows_owned.get(p.id)),
            "references": list(p.reference_names), "calls_project_ids": calls[p.id], "called_by_project_ids": called_by[p.id],
            "semantic_artifact_id": _sem_id(main), "semantic": machine_claims(main),
            "view_set_ids": ["VIEW-" + v["identity"][4:24] for v in vrecs], "data_interaction_id": ("DATA-" + drec["identity"][4:24]) if drec else None,
            "views_not_interpreted": pc.omitted_views})
    solutions, flows = [], []
    for s in inv.solutions:
        u = a.solutions[s.id]
        flow = u.flow.record if u.flow else None
        if flow:
            flows.append({"flow_set_id": "FLOW-" + flow["identity"][4:24], "solution_id": s.id, "semantic_artifact_id": _sem_id(flow),
                          "semantic": machine_claims(flow)})
        rec = u.item.record if u.item else None
        solutions.append({"solution_id": s.id, "name": s.name, "display": s.display, "path": s.path, "slug": s.slug,
                          "project_ids": list(s.project_ids), "state": u.state, "reason": u.reason,
                          "semantic_artifact_id": _sem_id(rec), "semantic": machine_claims(rec),
                          "flow_set_id": ("FLOW-" + flow["identity"][4:24]) if flow else None})
    srec = a.system.item.record if a.system.item else None
    system = {"system_id": "SYSTEM", "state": a.system.state, "reason": a.system.reason, "solution_ids": [s.id for s in inv.solutions],
              "semantic_artifact_id": _sem_id(srec), "semantic": machine_claims(srec)}

    unresolved = []
    for rec in records:
        for section, claims in rec["semantic"].items():
            for c in claims:
                if c["status"] == "UNRESOLVED":
                    unresolved.append({"claim_id": c["claim_id"], "level": rec["kind"], "entity_id": rec["entity_id"], "section": section,
                                       "text": c["text"], "semantic_artifact_id": _sem_id(rec)})
    exceptions = [{"level": "PROJECT", "entity_id": pc.project.id, "state": pc.state, "reason": pc.reason}
                  for pc in a.projects.values() if pc.state not in ("HUMAN_AND_MACHINE_DOCUMENTED",)]
    exceptions += [{"level": "PROJECT_VIEWS", "entity_id": pc.project.id, "state": "BOUNDED_CONTEXT", "reason": f"{pc.omitted_views} vistas sin interpretar"}
                   for pc in a.projects.values() if pc.omitted_views]

    provenance = []
    for rec in records:
        provenance.append({
            "semantic_artifact_id": _sem_id(rec), "request_identity": rec["identity"], "level": rec["kind"], "entity_id": rec["entity_id"],
            "input_hash": rec["input_hash"], "dependency_hashes": rec["dependency_hashes"], "response_sha256": rec["response"]["content_sha256"],
            "provider": rec["provider"], "validation": {k: rec["validation"][k] for k in ("schema_ok", "accepted_claims", "downgraded_to_inferred")},
            "rejected_claim_reasons": sorted({r["reason"] for r in rec["validation"]["rejected_claims"]}),
            "facts": [{"fact_id": f"{rec['identity']}:{f['ref']}", "kind": f["kind"], "certainty": f["certainty"], "text": f["text"],
                       "evidence_ids": f["evidence"]} for f in rec["facts"]]})

    coverage = {k: state[k] for k in ("contract", "schema_version", "baseline", "policy", "complete", "counts", "pending", "projects", "solutions", "system") if k in state}
    coverage["run_status"] = state.get("run_status")
    knowledge = {"contract": KNOWLEDGE_CONTRACT, "schema_version": SCHEMA_VERSION, "complete": a.complete,
                 "synthetic_provider": any(r["provider"].get("synthetic") for r in records),
                 "baseline": inv.identity.as_dict(), "system_id": "SYSTEM", "solution_ids": [s["solution_id"] for s in solutions],
                 "project_ids": [p["project_id"] for p in projects], "view_set_ids": sorted(v["view_set_id"] for v in views),
                 "flow_set_ids": sorted(f["flow_set_id"] for f in flows), "data_interaction_ids": sorted(d["data_interaction_id"] for d in data),
                 "files": ["system.json", "solutions.json", "projects.json", "views.json", "flows.json", "data.json", "unresolved.json", "provenance.json", "coverage.json"],
                 "claim_count": sum(len(c) for e in [system, *solutions, *projects, *views, *flows, *data] for c in e["semantic"].values())}
    for name, value in (("system", system), ("solutions", solutions), ("projects", projects), ("views", views), ("flows", flows), ("data", data),
                        ("unresolved", {"claims": sorted(unresolved, key=lambda u: u["claim_id"]), "coverage_exceptions": exceptions}),
                        ("provenance", provenance), ("coverage", coverage), ("knowledge", knowledge)):
        _w(ai / f"{name}.json", value)

    _w(internal / "baseline_identity.json", inv.identity.as_dict())
    _w(internal / "requests_index.json", sorted(({"identity": r["identity"], "kind": r["kind"], "entity_id": r["entity_id"],
                                                  "provider": r["provider"]} for r in records), key=lambda r: r["identity"]))
    _w(internal / "run_metrics.json", {"runs": state.get("runs", []), "cumulative_metrics": state.get("cumulative_metrics", {}),
                                      "preflight": state.get("preflight"), "controlled_errors": state.get("errors", {})})
    return {"projects": len(projects), "solutions": len(solutions), "views": len(views), "flows": len(flows), "data": len(data), "unresolved": len(unresolved)}


def check_machine(ai: Path) -> dict:
    """Machine validation: valid JSON, unique ids, no dangling references. Returns {invalid_json, dangling_ids, ...}."""
    result = {"invalid_json": 0, "dangling_ids": 0, "duplicate_ids": 0, "details": []}
    loaded = {}
    for path in sorted(ai.glob("*.json")):
        try:
            loaded[path.stem] = json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            result["invalid_json"] += 1
            result["details"].append(f"invalid json: {path.name}")
    if result["invalid_json"]:
        return result
    projects = {p["project_id"] for p in loaded["projects"]}
    solutions = {s["solution_id"] for s in loaded["solutions"]}
    if len(projects) != len(loaded["projects"]) or len(solutions) != len(loaded["solutions"]):
        result["duplicate_ids"] += 1
    facts = {f["fact_id"] for rec in loaded["provenance"] for f in rec["facts"]}
    artifacts = {rec["semantic_artifact_id"] for rec in loaded["provenance"]}
    view_sets = {v["view_set_id"] for v in loaded["views"]}
    flow_sets = {f["flow_set_id"] for f in loaded["flows"]}
    data_ids = {d["data_interaction_id"] for d in loaded["data"]}

    def need(ok: bool, what: str) -> None:
        if not ok:
            result["dangling_ids"] += 1
            result["details"].append(what)

    for s in loaded["solutions"]:
        for pid in s["project_ids"]:
            need(pid in projects, f"solution->project {pid}")
        need(s["flow_set_id"] is None or s["flow_set_id"] in flow_sets, f"solution->flow {s['flow_set_id']}")
    for p in loaded["projects"]:
        for sid in p["solution_ids"]:
            need(sid in solutions, f"project->solution {sid}")
        for other in p["calls_project_ids"] + p["called_by_project_ids"]:
            need(other in projects, f"project->project {other}")
        for vid in p["view_set_ids"]:
            need(vid in view_sets, f"project->view {vid}")
        need(p["data_interaction_id"] is None or p["data_interaction_id"] in data_ids, "project->data")
    for entity in [loaded["system"], *loaded["solutions"], *loaded["projects"], *loaded["views"], *loaded["flows"], *loaded["data"]]:
        need(entity.get("semantic_artifact_id") is None or entity["semantic_artifact_id"] in artifacts, f"entity->artifact {entity.get('semantic_artifact_id')}")
        for claims in entity.get("semantic", {}).values():
            for c in claims:
                for fid in c["fact_ids"]:
                    need(fid in facts, f"claim->fact {fid}")
    for v in loaded["views"] + loaded["data"]:
        need(v["project_id"] in projects, "view/data->project")
    for f in loaded["flows"]:
        need(f["solution_id"] in solutions, "flow->solution")
    cov_projects = {p["project_id"] for p in loaded["coverage"].get("projects", [])}
    need(cov_projects == projects, "coverage projects != projects")
    return result
