"""Final knowledge package (post-V5 H4): `human/`, `ai/`, `internal/` + `KNOWLEDGE_PACKAGE.json`.

Projects the persisted baseline and the saved AI answers of ONE semantic model into the public product layout. It never scans, never
analyzes, never reads source files and never calls a provider (the saved answers are re-validated with `ReplayProvider`).

    python -m legacy_documenter.product.package <baseline> --output <dir> [--ai-run <dir>] [--project P] [--solution S]
                                                   [--domain-knowledge terms.json]
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import shutil
import sys
import tempfile
from pathlib import Path

from legacy_documenter.behavior import ai as A
from legacy_documenter.behavior import prototype as P
from legacy_documenter.behavior.template import discover
from legacy_documenter.product import domain

SCHEMA = "LegacyMapperKnowledgePackage"
SCHEMA_VERSION = "1.0"
KNOWLEDGE_CONTRACT = "LegacyMapperAiKnowledge"
KNOWLEDGE_VERSION = "1.0"
UNKNOWN_TAIL = "destino posterior indeterminado"


def _dump(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _claim(c) -> dict:
    return {"text": c.text, "status": c.status, "source_refs": list(c.source_refs), "basis": c.basis}


def _invocation(i) -> dict:
    return {"source_view": i.source_view, "target_view": i.target_view, "mechanism": i.mechanism, "parameters": list(i.parameters),
            "file": i.file, "line": i.line, "target_exists": i.target_exists, "status": i.status, "source_refs": list(i.source_refs)}


def _traceability(v) -> dict:
    """What the human document no longer shows inline (evidence ids, source locations, validation support) stays machine-readable here."""
    refs = sorted({r for a in v.actions for r in a.source_refs} | {r for i in v.reached_by + v.reaches for r in i.source_refs})
    return {"source_refs": refs,
            "invocations_in": [_invocation(i) for i in v.reached_by], "invocations_out": [_invocation(i) for i in v.reaches],
            "usage_reasons": [_claim(c) for c in (v.usage or {}).get("reasons", [])],
            "markup_controls": [{"id": c.id, "kind": c.kind, "visible_initially": c.visible_initially} for c in (v.ui.controls if v.ui else [])],
            "ui": {"status": v.ui.status, "fidelity": v.ui.fidelity, "style_report": v.ui.style_report} if v.ui else None}


def _vid(project: str, name: str) -> str:
    return f"view:{project}/{name}"


# ---------------------------------------------------------------- AI projections (one model + small indexes)
def ai_projections(doc, explained: dict, bc, terms: list[dict]) -> dict[str, dict]:
    project = doc.project.name
    detailed = {v.view for v in doc.views}
    views, flows, data, unresolved = [], [], {}, []
    for path, v in sorted(explained.items(), key=lambda kv: kv[1].name.lower()):
        vid = _vid(project, v.name)
        actions = []
        for a in v.actions:
            aid = f"action:{project}/{v.name}/{a.handler}"
            steps = [{"kind": s["kind"], "label": s["label"], "status": s.get("status", "CONFIRMED"), "source_refs": list(s.get("source_refs", []))}
                     for s in (a.technical_path.steps if a.technical_path else [])]
            reaches_data = any(s["kind"] in ("procedure", "data_operation") for s in steps)
            route = {"id": f"flow:{project}/{v.name}/{a.handler}", "view": vid, "action": aid, "label": a.action,
                     "event": f"{a.trigger}.{a.event}" if a.trigger and a.trigger != "MyBase" else a.event, "handler": a.handler, "steps": steps,
                     "boundary": None if reaches_data else {"status": "UNRESOLVED", "label": UNKNOWN_TAIL},
                     "status": a.status, "source_refs": list(a.source_refs)}
            flows.append(route)
            pending = [u["business_call"] or u["label"] for u in (a.technical_path.unresolved_calls if a.technical_path else [])
                       if not u["infrastructure"] and u["business_call"]]
            for d in a.data:
                entry = data.setdefault(d.object_name, {"id": f"data:{d.object_name}", "name": d.object_name, "kind": d.kind, "effect": d.effect,
                                                        "effect_status": d.effect_status, "reached_via": [], "used_by_actions": [], "used_by_views": []})
                entry["reached_via"] = sorted(set(entry["reached_via"]) | {d.via})
                entry["used_by_actions"] = sorted(set(entry["used_by_actions"]) | {aid})
                entry["used_by_views"] = sorted(set(entry["used_by_views"]) | {vid})
            if pending:
                unresolved.append({"id": f"unresolved:{project}/{v.name}/{a.handler}", "kind": "undetermined_call_destination", "view": vid, "action": aid,
                                   "calls": sorted(set(pending)), "status": "UNRESOLVED"})
            actions.append({"id": aid, "label": a.action, "event": route["event"], "handler": a.handler, "flow": route["id"],
                            "data": sorted({d.object_name for d in a.data}), "results": [_claim(r) for r in a.result], "status": a.status})
        entry = {"id": vid, "name": v.name, "title": v.title, "kind": v.kind, "file": v.view, "family": v.family, "usage": {
                     "status": v.usage.get("status"), "label": v.usage.get("label")} if v.usage else None,
                 "opened_by": sorted({i.source_view.rsplit("\\", 1)[-1] for i in v.reached_by}),
                 "opens": sorted({i.target_view.rsplit("\\", 1)[-1] for i in v.reaches}),
                 "missing_targets": sorted({i.target_view for i in v.reaches if not i.target_exists}),
                 "classes": [{"name": c.name, "role": c.role, "status": c.status} for c in v.classes],
                 "actions": actions, "detailed": path in detailed}
        if v.name in {x.name for x in doc.views}:
            entry["explanation"] = {k: [_claim(c) for c in cs] for k, cs in sorted(v.ai_narrative.items())}
            entry["action_notes"] = {k: [_claim(c) for c in cs] for k, cs in sorted(v.ai_action_notes.items())}
            entry["deterministic_claims"] = [_claim(c) for c in v.what_it_does + v.receives]
            entry["traceability"] = _traceability(v)
        views.append(entry)
    scope = [c for c in doc.solution.not_inferable + doc.project.unresolved.unresolved]
    if doc.module.claim.status == "UNRESOLVED":
        scope.append(doc.module.claim)
    unresolved.insert(0, {"id": "unresolved:scope", "kind": "scope_limits", "claims": [_claim(c) for c in scope], "status": "UNRESOLVED"})
    projects = [{"id": f"project:{p['name']}", "name": p["name"], "path": p["path"], "layer": p["layer"], "layer_status": p["layer_status"]}
                for p in doc.solution.projects]
    architecture = {"solution": {"id": f"solution:{doc.solution.name}", "name": doc.solution.name,
                                 "projects": [p["id"] for p in projects]},
                    "projects": projects, "documented_project": f"project:{project}",
                    "project_references": [r for r in doc.project.facts.get("referencias_de_proyecto", [])],
                    "module_structure": {"classification": doc.module.classification, "claim": _claim(doc.module.claim),
                                         "name_families": [{"family": f["family"], "views": f["views"], "status": f["status"]} for f in doc.module.families]},
                    "claims": [_claim(c) for c in doc.solution.summary + doc.project.summary + doc.project.role_in_solution + doc.project.dependencies]}
    m = doc.ai_manifest or {}
    provenance = {"baseline": {k: v for k, v in sorted(doc.baseline.items()) if k not in ("pilot_selection",)},
                  "selection_criteria": [dict(x) for x in doc.baseline.get("pilot_selection", [])],
                  "measurements": dict(doc.measurements),
                  "module_evidence": {"classification": doc.module.classification, "claim": _claim(doc.module.claim),
                                      "evidence_considered": doc.module.evidence_considered},
                  "validation_report": "internal/behavioral/validation_report.json",
                  "human_document_policy": "the human document carries interpretation only; evidence ids, source locations, hashes, provider details and "
                                          "validation diagnostics are kept here and under internal/",
                  "ai": {"status": m.get("status"), "provider_id": m.get("provider_id"), "model_id": m.get("model_id"),
                         "request_count": m.get("request_count"), "successful_requests": m.get("successful_requests"),
                         "requests": [{"request_id": r.get("request_id"), "kind": r.get("kind"), "target": r.get("target"), "status": r.get("status")}
                                      for r in m.get("requests", [])],
                         "replayed_from_real_run": bool(m.get("replayed_from_real_run")), "status_policy": "AI narrative is AI_INTERPRETATION; never confirmed"},
                  "origins": {"deterministic_evidence": "CONFIRMED / INFERRED / UNRESOLVED claims derive from the persisted analyzer baseline",
                              "ai_interpretation": "AI_INTERPRETATION claims, validated deterministically, never promoted",
                              "human_confirmed": "domain_knowledge.terms (origin HUMAN_CONFIRMED, status CANONICAL)"},
                  "contract": KNOWLEDGE_CONTRACT, "contract_version": KNOWLEDGE_VERSION}
    knowledge = {
        "contract": KNOWLEDGE_CONTRACT, "contract_version": KNOWLEDGE_VERSION,
        "role": "authoritative machine-readable knowledge model; the other files of ai/ are projections / indexes of it",
        "solution": architecture["solution"], "projects": projects, "views": views,
        "flows": [f["id"] for f in flows], "data": [data[k]["id"] for k in sorted(data)], "unresolved": [u["id"] for u in unresolved],
        "project_summary": [_claim(c) for c in doc.project.ai_summary],
        "domain_knowledge": {"origin": domain.ORIGIN, "terms": terms,
                             "appears_in": domain.appears_in(terms, [v["name"] for v in views] + [project])},
        "status_vocabulary": {"CONFIRMED": "deterministic evidence", "INFERRED": "deterministic rule, not proven", "UNRESOLVED": "known gap",
                              "AI_INTERPRETATION": "AI text, validated, not approved", "CANONICAL": "human-approved"},
        "projections": {"architecture": "architecture.json", "views": "views.json", "flows": "flows.json", "data": "data.json",
                        "unresolved": "unresolved.json", "provenance": "provenance.json"},
    }
    index = [{"id": v["id"], "name": v["name"], "title": v["title"], "kind": v["kind"], "usage": (v["usage"] or {}).get("status"),
              "opens": v["opens"], "opened_by": v["opened_by"], "actions": [a["id"] for a in v["actions"]], "detailed": v["detailed"]} for v in views]
    return {"knowledge.json": knowledge, "architecture.json": architecture, "views.json": {"views": index},
            "flows.json": {"flows": flows}, "data.json": {"data": [data[k] for k in sorted(data)]},
            "unresolved.json": {"unresolved": unresolved}, "provenance.json": provenance}


# ---------------------------------------------------------------- human entry point
LANDING = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>LegacyMapper — {project}</title>
<style>body{{font-family:"Segoe UI",system-ui,Arial,sans-serif;max-width:760px;margin:48px auto;padding:0 20px;color:#1b2430;line-height:1.55}}
h1{{font-size:2.2rem;margin-bottom:.2em}}p.sub{{color:#5b6575;margin-top:0}}.card{{border:1px solid #d6dbe3;border-radius:8px;padding:14px 20px;margin:16px 0}}
.card a{{font-weight:700;font-size:1.1rem;color:#0f5132}}.card p{{margin:.3em 0 0;color:#5b6575}}</style></head>
<body><h1>{project}</h1><p class="sub">Solución «{solution}» · documentación generada por LegacyMapper</p>
<div class="card"><a href="guide/index.html">Guía de funcionamiento (HTML)</a><p>Funcional y técnica: vistas, qué hace cada una, acciones, rutas técnicas, relaciones entre pantallas y datos.</p></div>
<div class="card"><a href="LegacyMapper.pdf">Guía de funcionamiento (PDF)</a><p>La misma guía, para imprimir o compartir.</p></div>
<div class="card"><a href="executive/index.html">Resumen ejecutivo (HTML)</a><p>El sistema, sus proyectos, capacidades principales e impacto en datos.</p></div>
<div class="card"><a href="executive.pdf">Resumen ejecutivo (PDF)</a><p>Versión para imprimir.</p></div>
<div class="card"><a href="diagrams/index.html">Diagramas</a><p>Reconstrucciones documentales, flujos, rutas e invocaciones por vista.</p></div>
</body></html>
"""


def _diagrams_page(guide: Path) -> str:
    items = sorted(p.name for p in (guide / "assets").glob("*.svg")) if (guide / "assets").is_dir() else []
    groups = {"wireframe": "Reconstrucción documental", "flujo": "Flujo simple", "ruta": "Ruta técnica", "invocaciones": "Invocaciones"}
    rows = []
    for n in items:
        kind = next((v for k, v in groups.items() if n.endswith(f"-{k}.svg")), "Diagrama")
        rows.append(f'<li><a href="../guide/assets/{html.escape(n)}">{html.escape(n[:-4])}</a> <span style="color:#5b6575">· {kind}</span></li>')
    return ('<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Diagramas</title></head>'
            '<body style="font-family:Segoe UI,Arial,sans-serif;max-width:900px;margin:32px auto;padding:0 20px"><h1>Diagramas</h1>'
            '<p><a href="../index.html">← Inicio</a></p><ul>' + "".join(rows) + "</ul></body></html>\n")


# ---------------------------------------------------------------- machine-only (projects without views)
NO_UI_REASON = "the project declares no views (.ascx/.aspx); the screen/view model is not applicable, so only machine-readable knowledge is produced"
NO_DETAIL_REASON = ("the project declares views but none has observable actions to explain in detail; the human guide is not applicable and only "
                    "machine-readable knowledge is produced")


def machine_only_projections(doc, bc, terms: list[dict], cross_calls: list[dict], explained: dict | None = None) -> dict[str, dict]:
    """Same `ai/` contract for a project without UI: architecture, data reached by the project's own code and cross-project calls, with the
    scope limits kept as UNRESOLVED. No view, action or screen is invented."""
    reason = NO_DETAIL_REASON if explained else NO_UI_REASON
    base = ai_projections(doc, explained or {}, bc, terms)
    project, path = doc.project.name, str(bc.project_path)
    objects: dict[str, dict] = {}
    for d in bc.ctx.source.get("data_access", []):
        if str(d.get("project")) != path:
            continue
        name = d.get("stored_procedure") or d.get("sql_operation") or f"({d.get('operation_kind') or d.get('access_kind') or 'operation'} sin objeto resuelto)"
        kind = "procedure" if d.get("stored_procedure") else ("sql_operation" if d.get("sql_operation") else "unresolved_operation")
        e = objects.setdefault(str(name), {"id": f"data:{name}", "name": str(name), "kind": kind, "operation_kinds": set(), "used_by_classes": set(),
                                           "status": "UNRESOLVED" if kind == "unresolved_operation" else "CONFIRMED", "operations": 0})
        e["operation_kinds"].add(str(d.get("operation_kind") or d.get("access_kind")))
        e["used_by_classes"].add(f"{d.get('class')}.{d.get('method')}")
        e["operations"] += 1
    data = [{**e, "operation_kinds": sorted(e["operation_kinds"]), "used_by_classes": sorted(e["used_by_classes"])} for _, e in sorted(objects.items())]
    own = [c for c in cross_calls if path in (c.get("source_project"), c.get("target_project")) or project in (c.get("source_project"), c.get("target_project"))]
    by_status: dict[str, int] = {}
    for c in own:
        by_status[str(c.get("status"))] = by_status.get(str(c.get("status")), 0) + 1
    base["data.json"] = {"data": data}
    base["cross_project_calls.json"] = {"project": f"project:{project}", "summary": dict(sorted(by_status.items())),
                                        "calls": [{"id": c["id"], "source_symbol": c.get("source_symbol"), "target_symbol": c.get("target_symbol"),
                                                   "source_project": c.get("source_project"), "target_project": c.get("target_project"),
                                                   "status": c.get("status"), "resolution_code": c.get("resolution_code")} for c in own]}
    knowledge = base["knowledge.json"]
    knowledge["data"] = [d["id"] for d in data]
    knowledge["human_documentation"] = {"applicable": False, "reason": reason}
    knowledge["projections"]["cross_project_calls"] = "cross_project_calls.json"
    base["unresolved.json"]["unresolved"][0]["claims"].append({"text": reason, "status": "UNRESOLVED", "source_refs": [], "basis": "no views declared" if not explained else "no view with observable actions"})
    return base


def _build_machine_only(doc, bc, output: Path, baseline: Path, terms: list[dict], explained: dict | None = None) -> dict:
    from legacy_documenter.behavior.ui_evidence import load_cross_project_calls
    ai_dir, internal = output / "ai", output / "internal"
    for d in (ai_dir, internal):
        d.mkdir(parents=True, exist_ok=True)
    for name, obj in machine_only_projections(doc, bc, terms, load_cross_project_calls(baseline), explained).items():
        (ai_dir / name).write_text(_dump(obj), encoding="utf-8")
    (internal / "baseline_reference.json").write_text(_dump({"baseline_path": str(Path(baseline).resolve()),
                                                            "note": "the persisted analyzer baseline (Evidence Core) is referenced, not copied",
                                                            "fingerprints": {k: v for k, v in doc.baseline.items() if k.endswith("_sha256")}}), encoding="utf-8")
    files = {f.relative_to(output).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(output.rglob("*")) if f.is_file()}
    manifest = {"schema": SCHEMA, "schema_version": SCHEMA_VERSION,
                "source": {"solution": doc.solution.name, "project": doc.project.name, "logical_snapshot_sha256": doc.baseline.get("logical_snapshot_sha256"),
                           "portable_evidence_sha256": doc.baseline.get("portable_evidence_sha256")},
                "human_entry_point": None, "human_documents": {}, "human_documentation": {"applicable": False, "reason": NO_DETAIL_REASON if explained else NO_UI_REASON},
                "ai_entry_point": "ai/knowledge.json", "internal_artifacts_path": "internal/",
                "coverage": {"solutions": [doc.solution.name], "projects": [p["name"] for p in doc.solution.projects], "documented_project": doc.project.name,
                             "views_in_project": len(explained or {}), "views_explained_in_detail": []},
                "ai_provenance": {"status": "NOT_APPLICABLE", "provider_id": None, "model_id": None, "replayed_from_real_run": False},
                "human_confirmed_domain_knowledge": {"origin": domain.ORIGIN, "terms": [t["term"] for t in terms]},
                "evidence_fingerprint": doc.baseline.get("portable_evidence_sha256") or doc.baseline.get("evidence_manifest_sha256"), "files": files}
    (output / "KNOWLEDGE_PACKAGE.json").write_text(_dump(manifest), encoding="utf-8")
    return manifest


# ---------------------------------------------------------------- assembly
def build_package(baseline: Path, output: Path, *, ai_run: Path | None = None, project: str | None = None, solution: str | None = None,
                  domain_knowledge: Path | None = None) -> dict:
    """Builds the package. `ai_run` = directory with `ai_raw_responses.json` (+ manifest) of a real run; no provider is ever called here."""
    from legacy_documenter.utils.path_contract import validate_output_directory
    validate_output_directory(str(output))
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    terms = domain.load(domain_knowledge)
    provider = None
    if ai_run:
        provider = A.ReplayProvider(Path(ai_run) / "ai_raw_responses.json", Path(ai_run) / "AI_INTERPRETATION_MANIFEST.json")
    doc, bc, violations, explained = P.build(Path(baseline), None, project, solution, provider=provider, domain_knowledge=terms)
    if not doc.views:                                                                   # nothing to explain on screen: machine-only package, no screen model forced
        return _build_machine_only(doc, bc, output, Path(baseline), terms, explained)
    stage = Path(tempfile.mkdtemp(prefix="lm_pkg_", dir=str(output)))
    try:
        P.write_package(doc, stage / "default", violations, make_pdf=True, template=discover("human/default"), bc=bc, explained=explained)
        P.write_package(doc, stage / "executive", violations, make_pdf=True, template=discover("human/executive"), bc=bc, explained=explained)
        human, ai_dir, internal = output / "human", output / "ai", output / "internal"
        for d in (human, ai_dir, internal / "behavioral"):
            d.mkdir(parents=True, exist_ok=True)
        shutil.copytree(stage / "default" / "assets", human / "guide" / "assets") if (stage / "default" / "assets").is_dir() else (human / "guide").mkdir(parents=True)
        shutil.copy2(stage / "default" / "index.html", human / "guide" / "index.html")
        (human / "executive").mkdir()
        shutil.copy2(stage / "executive" / "index.html", human / "executive" / "index.html")
        shutil.copy2(next((stage / "default").glob("*.pdf")), human / "LegacyMapper.pdf")
        shutil.copy2(next((stage / "executive").glob("*.pdf")), human / "executive.pdf")
        (human / "diagrams").mkdir()
        (human / "diagrams" / "index.html").write_text(_diagrams_page(human / "guide"), encoding="utf-8")
        (human / "index.html").write_text(LANDING.format(project=html.escape(doc.project.name), solution=html.escape(doc.solution.name)), encoding="utf-8")
        for f in sorted((stage / "default").iterdir()):                                  # support artifacts -> internal/
            if f.is_file() and f.suffix == ".json":
                shutil.copy2(f, internal / "behavioral" / f.name)
        projections = ai_projections(doc, explained, bc, terms)
        for name, obj in projections.items():
            (ai_dir / name).write_text(_dump(obj), encoding="utf-8")
        baseline_ref = {"baseline_path": str(Path(baseline).resolve()), "note": "the persisted analyzer baseline (Evidence Core) is referenced, not copied",
                        "fingerprints": {k: v for k, v in doc.baseline.items() if k.endswith("_sha256")}}
        (internal / "baseline_reference.json").write_text(_dump(baseline_ref), encoding="utf-8")
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    files = {}
    for f in sorted(output.rglob("*")):
        if f.is_file():
            files[f.relative_to(output).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
    m = doc.ai_manifest or {}
    manifest = {
        "schema": SCHEMA, "schema_version": SCHEMA_VERSION,
        "source": {"solution": doc.solution.name, "project": doc.project.name,
                   "logical_snapshot_sha256": doc.baseline.get("logical_snapshot_sha256"),
                   "portable_evidence_sha256": doc.baseline.get("portable_evidence_sha256")},
        "human_entry_point": "human/index.html", "human_documents": {"guide_pdf": "human/LegacyMapper.pdf", "executive_pdf": "human/executive.pdf",
                                                                     "executive_html": "human/executive/index.html", "guide_html": "human/guide/index.html"},
        "ai_entry_point": "ai/knowledge.json", "internal_artifacts_path": "internal/",
        "coverage": {"solutions": [doc.solution.name], "projects": [p["name"] for p in doc.solution.projects],
                     "documented_project": doc.project.name, "views_in_project": len(explained), "views_explained_in_detail": [v.name for v in doc.views]},
        "ai_provenance": {"status": m.get("status"), "provider_id": m.get("provider_id"), "model_id": m.get("model_id"),
                          "replayed_from_real_run": bool(m.get("replayed_from_real_run"))},
        "human_confirmed_domain_knowledge": {"origin": domain.ORIGIN, "terms": [t["term"] for t in terms]},
        "evidence_fingerprint": doc.baseline.get("portable_evidence_sha256") or doc.baseline.get("evidence_manifest_sha256"),
        "files": files,
    }
    (output / "KNOWLEDGE_PACKAGE.json").write_text(_dump(manifest), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("baseline")
    ap.add_argument("--output", required=True)
    ap.add_argument("--ai-run", default=None, help="directory of a saved real AI run (ai_raw_responses.json); re-validated, no provider call")
    ap.add_argument("--project", default=None)
    ap.add_argument("--solution", default=None)
    ap.add_argument("--domain-knowledge", default=None)
    a = ap.parse_args(argv)
    try:
        manifest = build_package(Path(a.baseline), Path(a.output), ai_run=Path(a.ai_run) if a.ai_run else None, project=a.project,
                                 solution=a.solution, domain_knowledge=Path(a.domain_knowledge) if a.domain_knowledge else None)
    except (P.SelectionError, FileExistsError, domain.DomainKnowledgeError) as exc:
        print(json.dumps({"status": "FAILED", "reason": str(exc)}, ensure_ascii=False))
        return 4
    print(json.dumps({"status": "SUCCESS", "human_entry_point": manifest["human_entry_point"], "ai_entry_point": manifest["ai_entry_point"],
                      "provider_calls": 0}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
