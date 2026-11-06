"""Behavioral documentation prototype runner (post-V5 H4-R4).

    python -m legacy_documenter.behavior.prototype <baseline> --output <dir> [--project <name>] [--solution <name>]

Reads ONLY the persisted deterministic baseline (Evidence Core, including the UI / navigation / style Evidence written at analysis
time; post-V5 Gate B), builds the structured explanation, validates it, and writes HTML + PDF + explanation JSON + wireframe assets.
The legacy source repository is not needed and is never opened. No AI provider is resolved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from legacy_documenter.visuals.package import load_context

from . import ai as A
from . import explain as E
from . import render as R
from . import validate as V
from .evidence import VIEW_EXT, BehaviorContext, solution_has_project
from . import usage as U
from legacy_documenter.evidence.ui_model import norm_logical_path
from .ui_evidence import UiEvidenceUnavailable
from .model import CONFIRMED, INFERRED, UNRESOLVED, BehavioralDocument, ViewExplanation

KIND_ES = {"user_control": "control de usuario", "page": "página"}


def select_pilot(explained: dict[str, ViewExplanation], count: int = 5) -> list[tuple[str, str]]:
    """Deterministic choice of representative views: (view path, why). Not chosen for being easy: each slot maximises its own criterion."""
    rows = [(p, v.metrics, v) for p, v in explained.items() if v.metrics["actions"] > 0]
    chosen: list[tuple[str, str]] = []
    taken: set[str] = set()

    def pick(why: str, candidates, key):
        pool = [r for r in candidates if r[0] not in taken]
        if not pool:
            return
        best = max(pool, key=lambda r: (key(r), r[0].lower() == r[0].lower(), -len(r[0]), r[0].lower()))
        chosen.append((best[0], why))
        taken.add(best[0])

    writes = {"create", "update", "delete", "mixed"}
    pick("persistencia de datos: la vista con más operaciones de escritura distintas alcanzadas",
         [r for r in rows if set(r[1]["effects"]) & writes and not r[1]["dialog"]], lambda r: (len(set(r[1]["effects"]) & writes), r[1]["distinct_procedures"]))
    pick("ventana emergente de búsqueda/selección: la más invocada por otras vistas",
         [r for r in rows if r[1]["dialog"]], lambda r: (r[1]["incoming"], r[1]["actions"]))
    pick("lógica significativa: la que alcanza más procedimientos y clases distintas",
         [r for r in rows if r[1]["reaches_dao"] and not r[1]["dialog"]], lambda r: (r[1]["distinct_procedures"] + len(r[2].classes), r[1]["actions"]))
    pick("flujo complejo/no resuelto: la que más llamadas no resueltas (sin ruido de infraestructura) acumula",
         [r for r in rows if r[1]["unresolved_calls_non_infra"] > 0], lambda r: (r[1]["unresolved_calls_non_infra"], r[1]["actions"]))
    pick("página ordinaria: consulta sin escritura y pocas acciones",
         [r for r in rows if set(r[1]["effects"]) <= {"read"} and not r[1]["dialog"] and 2 <= r[1]["actions"] <= 5 and r[1]["wireframe"]],
         lambda r: (r[1]["actions"] == 3, -r[1]["actions"], r[1]["incoming"]))
    return chosen[:count]


def catalog_row(v: ViewExplanation, detailed: bool) -> dict:
    m = v.metrics
    effects = set(m["effects"])
    if m["dialog"]:
        purpose = "Diálogo de búsqueda/selección (inferido)"
    elif effects & {"create", "update", "delete", "mixed"}:
        purpose = "Mantenimiento de datos (inferido)"
    elif "read" in effects:
        purpose = "Consulta (inferido)"
    elif m["business_calls"]:
        purpose = "Con acciones que llaman a lógica de negocio no resuelta (propósito no determinado)"
    elif m["actions"]:
        purpose = "Con acciones; destino de datos no resuelto"
    else:
        purpose = "Sin eventos propios; propósito no determinado"
    reached = f"{m['incoming']} vista(s) la abre(n)" if m["incoming"] else "no resuelto (shell/menú)"
    return {"view": v.view, "name": v.name, "kind_es": KIND_ES.get(v.kind, v.kind), "family": v.family, "title": v.title, "purpose": purpose,
            "reached": reached, "actions": str(m["actions"]), "reads": "sí" if "read" in effects else "no",
            "writes": "sí" if effects & {"create", "update", "delete", "mixed"} else "no", "opens": str(m["outgoing"]),
            "status": INFERRED if (m["dialog"] or effects) else UNRESOLVED, "usage_label": v.usage.get("label", "—"), "detailed": detailed, "effects": sorted(effects), "incoming": m["incoming"]}


def measure(explained: dict[str, ViewExplanation], bc: BehaviorContext, module) -> dict:
    ms = [v.metrics for v in explained.values()]
    n = len(ms)
    return {
        "vistas_del_proyecto": n, "grupos_o_modulos_candidatos": f"{module.classification} ({len(module.families)} familias por prefijo)",
        "con_code_behind": sum(m["has_code_behind"] for m in ms), "con_marcado": sum(m["has_markup"] for m in ms),
        "con_eventos_o_acciones": sum(1 for m in ms if m["actions"]), "alcanzan_clase_de_negocio_o_dao": sum(m["reaches_business_or_dao"] for m in ms),
        "alcanzan_operacion_de_datos": sum(m["reaches_dao"] for m in ms), "alcanzan_procedimiento_o_sql": sum(m["reaches_procedure"] for m in ms),
        "con_invocaciones_entrantes": sum(1 for m in ms if m["incoming"]), "con_invocaciones_salientes": sum(1 for m in ms if m["outgoing"]),
        "soportan_wireframe_documental": sum(m["wireframe"] for m in ms),
        "estructuralmente_no_resueltas (acciones sin ruta confirmada)": sum(1 for m in ms if m["unresolved_paths"]),
        "dialogos_de_busqueda_inferidos": sum(1 for m in ms if m["dialog"]),
    }


def classify_usage(bc: BehaviorContext, explained: dict[str, ViewExplanation]) -> dict:
    """Observable-usage classification of every project view (positive evidence only) + a summary.

    Name references come from persisted UI Evidence (`UiDocument.mentions_views`: the view's markup/code-behind text mentions the name
    of another view of the same project), computed once at analysis time -- no file is opened here.
    """
    mentions = {path: bc.ui.mentions(path) for path in explained}
    shell = sum(1 for v in explained.values() if v.reached_by)           # views opened by name through default.aspx?url=…
    by_status: Counter = Counter()
    for path, v in explained.items():
        key = norm_logical_path(path)
        refs = sum(1 for other, found in mentions.items() if other != path and key in found)
        behavior = bool(v.actions) and (v.metrics["reaches_dao"] or v.metrics["business_calls"] or v.metrics["actions"] >= 2)
        v.usage = U.classify(v, shell_evidence=shell, name_references=refs, behavior=behavior)
        by_status[v.usage["status"]] += 1
    return {"by_status": dict(sorted(by_status.items())), "shell_pattern_views": shell,
            "note": "Absence of observable usage evidence is not evidence of obsolescence."}


class SelectionError(Exception):
    """The project/solution to document cannot be chosen safely: stable `code`, human `detail` and the candidates found."""

    def __init__(self, code: str, detail: str, candidates: list[str] | None = None) -> None:
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.candidates = code, detail, sorted(candidates or [], key=str.lower)

    def to_dict(self) -> dict:
        return {"status": "SELECTION_ERROR", "code": self.code, "message": self.detail, "candidates": self.candidates}


def _view_projects(src: dict) -> list[str]:
    """Projects whose content/compile items declare at least one view (`.ascx`/`.aspx`): the only ones this document can explain."""
    return sorted({str(p.get("name")) for p in src["projects"]
                   if any(str(i).lower().endswith(VIEW_EXT) for i in list(p.get("content_items") or []) + list(p.get("compile_items") or []))},
                  key=str.lower)


def select_project_and_solution(ctx, project: str | None, solution: str | None) -> tuple[str, str, dict]:
    """No developer-specific defaults: 0 candidates -> error, 1 -> deterministic selection (recorded), >1 -> explicit choice required."""
    src = ctx.source
    names = sorted({str(p.get("name")) for p in src["projects"]}, key=str.lower)
    record: dict = {}
    if project:
        if project not in names:
            raise SelectionError("PROJECT_NOT_FOUND", f"project '{project}' is not in the baseline", names)
        record["project"] = "explicit"
    else:
        candidates = _view_projects(src)
        if not candidates:
            raise SelectionError("NO_BEHAVIORAL_PROJECT_CANDIDATES", "the baseline declares no project with views (.ascx/.aspx); nothing to document", [])
        if len(candidates) > 1:
            raise SelectionError("PROJECT_SELECTION_REQUIRED", "several projects declare views; choose one with --project", candidates)
        project = candidates[0]
        record["project"] = "deterministic_single_candidate"
    project_path = str(next(p for p in src["projects"] if p.get("name") == project)["path"])
    in_solutions = sorted({str(s.get("name")) for s in src["solutions"] if solution_has_project(s, project_path)}, key=str.lower)
    if solution:
        if solution not in in_solutions:
            same_name = sum(1 for p in src["projects"] if str(p.get("name")) == project)
            hint = f" ({same_name} projects share this name; the first one in the baseline is used)" if same_name > 1 else ""
            raise SelectionError("SOLUTION_NOT_FOUND_FOR_PROJECT", f"solution '{solution}' does not contain project '{project}'{hint}", in_solutions)
        record["solution"] = "explicit"
    else:
        if not in_solutions:
            raise SelectionError("NO_SOLUTION_CANDIDATES", f"no solution in the baseline contains project '{project}'", [])
        if len(in_solutions) > 1:
            raise SelectionError("SOLUTION_SELECTION_REQUIRED", f"several solutions contain project '{project}'; choose one with --solution", in_solutions)
        solution = in_solutions[0]
        record["solution"] = "deterministic_single_candidate"
    return project, solution, record


def build(baseline: Path, repo: Path | None = None, project: str | None = None, solution: str | None = None, pilot_count: int = 5,
          pilot_views: list[str] | None = None, provider=None, domain_knowledge: list[dict] | None = None) -> tuple[BehavioralDocument, BehaviorContext, list[V.Violation], dict]:
    """`repo` is a deprecated, IGNORED compatibility parameter (pre-Gate-B signature): the source repository is never read."""
    ctx = load_context(baseline)
    project, solution, selection = select_project_and_solution(ctx, project, solution)
    bc = BehaviorContext(ctx, baseline, project)
    explained: dict[str, ViewExplanation] = {p: E.explain_view(bc, p) for p in bc.view_paths}
    refs = V.ReferenceIndex(bc)
    violations: list[V.Violation] = []
    for v in explained.values():
        violations += V.validate_view(refs, v)
    usage_summary = classify_usage(bc, explained)
    families = Counter(v.family for v in explained.values())
    module = E.explain_modules(bc, families)
    if pilot_views:
        chosen = [(next(p for p in explained if p.lower().endswith(name.lower() + ".ascx")), "elegida explícitamente") for name in pilot_views]
    else:
        chosen = select_pilot(explained, pilot_count)
    detailed_paths = [p for p, _ in chosen]
    catalog = [catalog_row(v, p in detailed_paths) for p, v in sorted(explained.items(), key=lambda kv: kv[1].name.lower())]
    sol, proj = E.explain_solution_and_project(bc, ctx, next((s.slug for s in ctx.model.solutions if s.values["name"] == solution), None),
                                               list(explained.values()), catalog, module)
    in_project = {p.lower() for p in bc.view_paths}
    cross = []
    for v in explained.values():
        for inv in v.reaches:
            if inv.target_view.lower() in in_project:
                cross.append(inv)
    cross.sort(key=lambda i: (i.source_view.lower(), i.line))
    ai_manifest: dict = {"status": "NOT_RUN", "reason": "no provider supplied"}
    if provider is not None:
        ai_manifest = run_ai(provider, bc, refs, explained, detailed_paths, proj, module, measure(explained, bc, module), usage_summary, violations,
                             {"solution": solution, "project": project, "path": bc.project_path,
                              "refs": [r.get("name") for r in bc.project.get("project_references", [])],
                              "domain_knowledge": list(domain_knowledge or [])},
                             getattr(ctx, "portable_evidence_sha256", None) or ctx.manifest_sha256)
    doc = BehavioralDocument(solution=sol, project=proj, module=module, views=[explained[p] for p in detailed_paths], catalog=catalog, cross_view=cross,
                             measurements=measure(explained, bc, module), usage_summary=usage_summary, ai_manifest=ai_manifest,
                             baseline={**({"evidence_manifest_sha256": ctx.manifest_sha256} if not getattr(ctx, "portable_evidence_sha256", None) else {}),
                                       "portable_evidence_sha256": getattr(ctx, "portable_evidence_sha256", None),
                                       "logical_snapshot_sha256": getattr(ctx, "logical_snapshot_sha256", None), "project": project, "solution": solution,
                                       "pilot_selection": [{"view": p, "criterion": why} for p, why in chosen],
                                       "project_solution_selection": selection},
                             domain_knowledge=list(domain_knowledge or []))
    return doc, bc, violations, explained


def run_ai(provider, bc, refs, explained, detailed_paths, proj, module, measurements, usage_summary, violations, project_info, snapshot) -> dict:
    """One bounded request per pilot view + one for the project. Validated claims are attached; nothing is replaced by templates."""
    run = A.AiRun()
    per_view = []
    for path in detailed_paths:
        v = explained[path]
        ctx_dict, scope = A.view_context(bc, v, project_info)
        parsed = A.call(provider, "view", v.name, ctx_dict, snapshot, A.VIEW_SCHEMA, run)
        vs = A.merge_view(v, parsed, scope, refs)
        violations.extend(vs)
        kept = sum(len(c) for c in v.ai_narrative.values()) + sum(len(c) for c in v.ai_action_notes.values())
        per_view.append({"view": v.name, "facts": len(ctx_dict["facts"]), "controls": len(ctx_dict["controls"]), "accepted_claims": kept,
                         "rejected_claims": [{"code": x.code, "where": x.where, "detail": x.detail} for x in vs if x.action == "rejected"],
                         "noted": [{"code": x.code, "detail": x.detail} for x in vs if x.action == "noted"], "got_output": parsed is not None})
    pctx, pscope = A.project_context([explained[p] for p in detailed_paths], project_info, module, measurements, usage_summary)
    parsed = A.call(provider, "project", project_info["project"], pctx, snapshot, A.PROJECT_SCHEMA, run, max_tokens=2500)
    pvs = A.merge_project(proj, parsed, pscope, refs)
    violations.extend(pvs)
    per_view.append({"view": "(project)", "facts": len(pctx["facts"]), "accepted_claims": len(proj.ai_summary),
                     "rejected_claims": [{"code": x.code, "where": x.where, "detail": x.detail} for x in pvs if x.action == "rejected"],
                     "noted": [], "got_output": parsed is not None})
    ok = [r for r in run.requests if r["status"] == "SUCCESS"]
    return {"status": "COMPLETED" if ok else "FAILED", "provider_id": run.provider_id, "model_id": run.model_id, "request_count": len(run.requests),
            "successful_requests": len(ok), "input_chars_total": sum(r["input_chars"] for r in run.requests),
            "output_chars_total": sum(r["output_chars"] for r in run.requests), "requests": run.requests, "validation": per_view,
            "ai_status_policy": "all AI narrative is AI_INTERPRETATION; never promoted", "raw_responses": run.raw,
            **({"replayed_from_real_run": True, "original_requests": provider.original_requests,
                "note": "answers of the real provider run re-validated with the final validator; no new provider calls"}
               if isinstance(provider, A.ReplayProvider) else {})}


def ui_navigation_evidence(bc, explained: dict) -> dict:
    """DERIVED projection (debug / compatibility / audit) of the UI and navigation facts of the views, with the sha256 of each analyzed
    source file taken from the persisted `source_artifacts` partition. NOT authoritative: the facts live in Evidence Core
    (`evidence/ui_*.json`); this sidecar can be regenerated from it at any time and nothing reads it back as input."""
    hashes = {k.lower(): v for k, v in bc.ui.source_hashes().items()}
    views = {}
    for path, v in sorted(explained.items()):
        ev = bc.view(path)
        files = {}
        for rel in (ev.markup_file, ev.code_file):
            sha = hashes.get(rel.replace("\\", "/").lower()) if rel else None
            if sha:
                files[rel] = sha
        views[path] = {
            "source_files": files, "controls": [{"id": c.id, "kind": c.kind, "label": c.label, "visible_initially": c.visible_initially, "line": c.line}
                                                 for c in (v.ui.controls if v.ui else [])],
            "receives": [{"name": r["name"], "via": r["via"], "line": r["line"]} for r in (ev.code.receives if ev.code else [])],
            "messages": [{"kind": m["kind"], "text": m["text"], "event": m["event"], "line": m["line"]} for m in (ev.code.messages if ev.code else [])],
            "navigation_out": [{"target": f"{h.folder}/{h.view}", "mechanism": h.mechanism, "parameters": h.params, "file": h.file, "line": h.line} for h in ev.outgoing],
            "navigation_in": [{"from": h.file, "mechanism": h.mechanism, "parameters": h.params, "line": h.line} for h in ev.incoming],
            "ui_fidelity": v.ui.fidelity if v.ui else None,
        }
    return {"contract": "LegacyMapperUiNavigationEnrichment", "contract_version": "2.0", "authoritative": False,
            "role": "derived_projection", "derived_from": "evidence/ui_*.json (UI / navigation / style Evidence in Evidence Core)",
            "origin": "projection of persisted Evidence; the source repository was not read", "evidence_core_modified": False, "views": views}


def write_package(doc: BehavioralDocument, out: Path, violations: list[V.Violation], *, make_pdf: bool = True, template=None, bc=None,
                  explained: dict | None = None) -> dict:
    from .template import discover, validate_required_fields
    out.mkdir(parents=True, exist_ok=True)
    template = template or discover("human/default")
    problems = validate_required_fields(template, doc)
    if problems:
        from .template import TemplateError
        raise TemplateError("required fields missing: " + "; ".join(problems[:5]))
    blocks, assets = R.compose(doc, template)
    files: dict[str, str] = {}

    def put(rel: str, text: str | bytes) -> None:
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        data = text.encode("utf-8") if isinstance(text, str) else text
        target.write_bytes(data)
        files[rel] = hashlib.sha256(data).hexdigest()

    for rel, (svg, _kind) in sorted(assets.items()):
        put(rel, svg)
    put("index.html", R.html_document(blocks, f"Entendiendo {doc.project.name}", template))
    put("TEMPLATE_MANIFEST.json", json.dumps(template.manifest_record(), ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    style_report = {v.name: {"fidelity": v.ui.fidelity, **v.ui.style_report} for v in doc.views if v.ui and v.ui.status == "DOCUMENTARY_RECONSTRUCTION"}
    if explained:
        counts: Counter = Counter(v.ui.fidelity for v in explained.values() if v.ui)
        style_report = {"pilot_views": style_report, "project_fidelity_distribution": dict(sorted(counts.items())),
                        "views_with_wireframe": sum(1 for v in explained.values() if v.ui and v.ui.status == "DOCUMENTARY_RECONSTRUCTION"),
                        "note": "STYLE_HIGH_CONFIDENCE is only claimed when nearly all visible controls have confirmed styles, icons resolve and layout is not runtime-driven."}
    put("style_reconstruction_report.json", json.dumps(style_report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    if bc is not None and explained is not None:
        put("ui_navigation_evidence.json", json.dumps(ui_navigation_evidence(bc, explained), ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    raw = doc.ai_manifest.pop("raw_responses", None) if isinstance(doc.ai_manifest, dict) else None
    explanation = asdict(doc)
    put("explanations.json", json.dumps(explanation, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    if raw:
        put("ai_raw_responses.json", json.dumps(raw, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    put("AI_INTERPRETATION_MANIFEST.json", json.dumps(doc.ai_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    put("validation_report.json", json.dumps({"violations": [asdict(v) for v in violations]}, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    wireframes = {v.name: {"status": v.ui.status, "controls": [asdict(c) for c in v.ui.controls], "rows": v.ui.rows} for v in doc.views if v.ui}
    put("wireframe_models.json", json.dumps(wireframes, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    stats = {}
    if make_pdf:
        brief = template.manifest.get("audience") == "executive"
        meta = [s for s in [R.provenance_sentence(doc.ai_manifest, brief=brief)] if s]      # fingerprints / provider details stay in ai/ and internal/
        data, stats = R.build_pdf(blocks, f"Entendiendo {doc.project.name}", out, meta, template)
        put(f"Entendiendo_{doc.project.name}.pdf", data)
    return {"files": files, "pdf": stats}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("baseline")
    ap.add_argument("--source", default=None, help="DEPRECATED and ignored (pre-Gate-B): UI Evidence is read from the baseline; the repository is never opened")
    ap.add_argument("--output", required=True)
    ap.add_argument("--project", default=None, help="project to document; optional only when exactly one project in the baseline declares views")
    ap.add_argument("--solution", default=None, help="solution containing the project; optional only when exactly one contains it")
    ap.add_argument("--view", action="append", default=None, help="explicit pilot view name (repeatable); default: deterministic selection")
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--template", default="human/default", help="human template id (<kind>/<name>), default human/default")
    ap.add_argument("--template-dir", default=None, help="optional user template directory searched before the built-in templates packaged with LegacyMapper")
    ap.add_argument("--ai-replay", default=None, help="re-apply validation to the saved answers of an earlier real run (directory with ai_raw_responses.json); no provider call")
    ap.add_argument("--domain-knowledge", default=None, help="JSON file with human-confirmed domain terms ({\"terms\": [{term, meaning, status: CANONICAL, source: human}]})")
    ap.add_argument("--ai", action="store_true", help="call the configured AI provider (existing architecture) over the bounded behavioral context")
    args = ap.parse_args(argv)
    from legacy_documenter.utils.path_contract import PathContractError, validate_output_directory
    try:  # Gate A path contract: refuse an invalid output before any provider or model work
        validate_output_directory(args.output)
    except PathContractError as exc:
        print(json.dumps(exc.to_dict(), ensure_ascii=False, sort_keys=True))
        return 4
    provider = A.make_provider() if args.ai else None
    if args.ai_replay:
        d = Path(args.ai_replay)
        provider = A.ReplayProvider(d / "ai_raw_responses.json", d / "AI_INTERPRETATION_MANIFEST.json")
    try:
        from legacy_documenter.product import domain
        doc, bc, violations, explained = build(Path(args.baseline), None, args.project, args.solution, pilot_views=args.view, provider=provider,
                                               domain_knowledge=domain.load(args.domain_knowledge))
    except (SelectionError, UiEvidenceUnavailable) as exc:
        print(json.dumps(exc.to_dict(), ensure_ascii=False, sort_keys=True))
        return 4
    from .template import TemplateError, discover
    try:
        template = discover(args.template, args.template_dir)
    except TemplateError as exc:
        print(json.dumps({"status": "TEMPLATE_INVALID", "reason": str(exc)}, ensure_ascii=False))
        return 4
    info = write_package(doc, Path(args.output), violations, make_pdf=not args.no_pdf, template=template, bc=bc, explained=explained)
    print(json.dumps({"status": "SUCCESS", "views_in_project": len(explained), "pilot": [v.name for v in doc.views], "module": doc.module.classification,
                      "violations": len(violations), "files": sorted(info["files"]), "provider_calls": 0}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
