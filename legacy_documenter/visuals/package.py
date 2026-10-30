"""Visual package generation from a persisted deterministic baseline (post-V5 H3).

Validates the baseline with the H1 gate, rebuilds the SAME audience model H2 uses from `index/` + `evidence/` (no source scan,
no provider), builds validated `VisualProjection`s and writes, per diagram, a deterministic `.svg` and its machine-readable
`.json` model plus one `VISUALS_MANIFEST.json` (stable relative paths, hashes, counts, partial/omission info) that H4 can embed.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

from legacy_documenter.documentation_v52.audience import enrich_for_audiences
from legacy_documenter.documentation_v52.config import ConfigRegistry
from legacy_documenter.documentation_v52.engine import source_from_indexes
from legacy_documenter.documentation_v52.transform import AudienceTransformer
from legacy_documenter.orchestration._run_evidence_io import load_indexes
from legacy_documenter.orchestration.ai_only import BaselineInvalid, validate_baseline

from .builders import (
    MAX_NODES, VisualContext, build_data_interaction_map, build_dependency_map, build_observable_flow, build_project_layer_map, build_system_map,
)
from .decompose import build_data_interaction_maps, build_dependency_maps
from .model import KINDS, VisualProjection, validate_projection
from .svg import render_svg

MANIFEST_NAME = "VISUALS_MANIFEST.json"
MANIFEST_CONTRACT = "LegacyMapperVisualsManifest"
AREA_KINDS = ("system-map", "project-layer-map", "dependency-map", "data-interaction-map")
PROJECT_KINDS = ("project-layer-map", "dependency-map", "data-interaction-map")


@dataclass
class VisualsResult:
    output: Path
    diagrams: list[dict] = field(default_factory=list)
    selection: dict = field(default_factory=dict)
    seconds: float = 0.0


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def load_knowledge_refs(ai_run_dir: str | Path) -> dict:
    """File-level, read-only view of an AI run (proposals pending review + canonical records) WITH their evidence refs."""
    root = Path(ai_run_dir)
    envelope = _read_json(root / "proposals" / "AI_PROPOSALS.json") or {}
    records = [r for r in (_read_json(p) for p in sorted((root / "knowledge" / "canonical").glob("*.json"))) if isinstance(r, dict) and r.get("status", "ACTIVE") == "ACTIVE"]
    decisions = [d for d in (_read_json(p) for p in sorted((root / "knowledge" / "decisions").glob("*.json"))) if isinstance(d, dict)]
    canonical_ids = {r.get("source_proposal_id") for r in records}
    rejected = {d.get("proposal_id") for d in decisions if d.get("action") == "REJECT"}
    return {
        "proposals": [{"statement": p.get("statement"), "evidence_refs": list(p.get("evidence_refs") or [])}
                      for p in (envelope.get("proposals") or []) if isinstance(p, dict) and p.get("proposal_id") not in canonical_ids | rejected],
        "canonical": [{"statement": (r.get("content") or {}).get("statement", ""), "evidence_refs": list(r.get("evidence_refs") or [])} for r in records],
    }


def load_context(baseline: str | Path, knowledge: dict | None = None, verify_evidence: str = "fast", max_nodes: int = MAX_NODES,
                 max_children: int = 30) -> VisualContext:
    info = validate_baseline(baseline, verify_evidence)
    root = info.baseline_dir
    external_path = root / "evidence" / "external_dependencies.json"
    external = _read_json(external_path) or [] if external_path.is_file() else []
    source = source_from_indexes(load_indexes(root), external)
    registry = ConfigRegistry()
    profile = registry.profile("technical_overview")
    catalog = registry.catalog(profile.language)
    policy = registry.noise_policy(profile.noise_policy)
    model = AudienceTransformer(policy, catalog.text("unassigned_module"), catalog.text("origin_unknown"), catalog.text("file_ownership_shared")).transform(source)
    enrich_for_audiences(model, source, None, False)
    ids = {"projects": {}, "solutions": {}}
    for kind, filename in (("projects", "projects.json"), ("solutions", "solutions.json")):
        for rec in _read_json(root / "evidence" / filename) or []:
            if isinstance(rec, dict) and rec.get("path") and rec.get("id"):
                ids[kind].setdefault(rec["path"], rec["id"])
    context = VisualContext(model, source, ids, info.evidence_manifest_sha256, knowledge, max_nodes, max_children)
    context.portable_evidence_sha256, context.logical_snapshot_sha256 = info.portable_evidence_sha256, info.logical_snapshot_sha256
    return context


def representative_flow(ctx: VisualContext, area: str) -> str | None:
    """Smallest evidence-backed flow of the area that reaches a stored procedure and has a readable size (deterministic)."""
    paths = {m.values["path"] for m in ctx.area_modules(area)}
    best = None
    for flow in ctx.flows.values():
        if ctx.ep_project.get(flow.get("entry_point_id")) not in paths:
            continue
        kinds = {n["type"] for n in flow["nodes"]}
        if "StoredProcedure" not in kinds:
            continue
        size = len([n for n in flow["nodes"] if n["type"] != "Project"])
        if 6 <= size <= 40 and (best is None or (size, flow["id"]) < best[0]):
            best = ((size, flow["id"]), flow["id"])
    return best[1] if best else None


def _write(root: Path, rel: str, text: str) -> str:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _child_name(projection: VisualProjection) -> str:
    scope = projection.scope
    return f"{scope['focal_project']}--{scope['part']}" if scope.get("focal_project") else str(scope.get("part") or scope["id"]).replace(":", "--")


def _emit(root: Path, folder: str, projection: VisualProjection, stem: str | None = None) -> dict | None:
    validate_projection(projection)
    if not projection.nodes:  # nothing to draw for this scope (e.g. a project without screens): reported, not written
        return None
    svg, model_json = render_svg(projection), projection.to_json()
    stem = stem or f"{folder}/{projection.kind}"
    svg_hash, model_hash = _write(root, f"{stem}.svg", svg), _write(root, f"{stem}.json", model_json)
    statuses = {}
    for item in [*projection.nodes, *projection.edges]:
        statuses[item.status] = statuses.get(item.status, 0) + 1
    width, height = re.search(r'width="(\d+)" height="(\d+)"', svg[:600]).groups()
    out_degree: dict[str, int] = {}
    for edge in projection.edges:
        out_degree[edge.source] = out_degree.get(edge.source, 0) + 1
    entry = {"id": projection.id, "kind": projection.kind, "scope": projection.scope, "title": projection.title, "audience": projection.audience,
             "svg": f"{stem}.svg", "model": f"{stem}.json", "nodes": len(projection.nodes), "edges": len(projection.edges), "groups": len(projection.groups),
             "partial": projection.partial, "status_counts": dict(sorted(statuses.items())), "unresolved_nodes": len(projection.unresolved),
             "svg_bytes": len(svg.encode("utf-8")), "svg_sha256": svg_hash, "model_sha256": model_hash,
             "metrics": {"canvas_width": int(width), "canvas_height": int(height), "edges_per_node": round(len(projection.edges) / max(1, len(projection.nodes)), 2),
                         "max_out_degree": max(out_degree.values(), default=0)}}
    if projection.decomposition is not None:
        entry["decomposition"] = projection.decomposition
    return entry


def _resolve(ctx: VisualContext, wanted: list[str], table: dict, label: str) -> list[str]:
    out = []
    for name in wanted:
        if name in table:
            out.append(name)
            continue
        hits = sorted(slug for slug, obj in table.items() if obj.values["name"] == name)
        if not hits:
            raise KeyError(f"{label} not found in the baseline: {name}")
        out.extend(hits)
    return out


def generate_visuals(
    ctx: VisualContext, output: str | Path, *, areas: list[str] | None = None, projects: list[str] | None = None, flows: list[str] | None = None,
    kinds: list[str] | None = None, top_areas: int = 3, all_areas: bool = False, include_ai: bool = False,
) -> VisualsResult:
    started = perf_counter()
    root = Path(output)
    wanted_kinds = set(kinds or KINDS)
    ranked = [i.values["slug"] for i in ctx.model.slots["areas"]]
    if all_areas:
        area_slugs = ranked
    elif areas:
        area_slugs = _resolve(ctx, areas, ctx.solutions, "area")
    elif projects or flows:
        area_slugs = []
    else:
        area_slugs = ranked[:top_areas]
    project_slugs = _resolve(ctx, projects or [], ctx.modules, "project")
    flow_ids = list(flows or [])
    for fid in flow_ids:
        if fid not in ctx.flows:
            raise KeyError(f"flow not found in the baseline: {fid}")
    if not areas and not projects and not flows:
        flow_ids = [f for f in (representative_flow(ctx, a) for a in area_slugs) if f]
    result = VisualsResult(output=root)
    skipped: list[str] = []

    def emit(folder: str, projection: VisualProjection) -> None:
        entry = _emit(root, folder, projection)
        if entry is None:
            skipped.append(f"{folder}/{projection.kind}")
        else:
            result.diagrams.append(entry)

    def emit_many(folder: str, projections: list[VisualProjection]) -> None:
        """First item is the summary/single diagram (normal path); the rest are its detail diagrams under `<kind>.details/`."""
        head, details = projections[0], projections[1:]
        emit(folder, head)
        for child in details:
            entry = _emit(root, folder, child, f"{folder}/{child.kind}.details/{_child_name(child)}")
            if entry is not None:
                entry["parent_id"] = head.id
                result.diagrams.append(entry)

    if "system-map" in wanted_kinds:
        emit("system", build_system_map(ctx))
    builders = {"system-map": lambda a: [build_system_map(ctx, a)], "project-layer-map": lambda a: [build_project_layer_map(ctx, area=a)],
                "dependency-map": lambda a: build_dependency_maps(ctx, area=a), "data-interaction-map": lambda a: build_data_interaction_maps(ctx, area=a)}
    for slug in area_slugs:
        for kind in AREA_KINDS:
            if kind in wanted_kinds:
                emit_many(f"areas/{slug}", builders[kind](slug))
    pbuilders = {"project-layer-map": lambda s: [build_project_layer_map(ctx, project=s)], "dependency-map": lambda s: build_dependency_maps(ctx, project=s),
                 "data-interaction-map": lambda s: build_data_interaction_maps(ctx, project=s)}
    for slug in project_slugs:
        for kind in PROJECT_KINDS:
            if kind in wanted_kinds:
                emit_many(f"projects/{slug}", pbuilders[kind](slug))
    if "observable-flow" in wanted_kinds:
        for fid in sorted(flow_ids):
            emit(f"flows/{fid}", build_observable_flow(ctx, fid, include_ai=include_ai))
    result.diagrams.sort(key=lambda d: d["svg"])
    summaries = [d for d in result.diagrams if d.get("decomposition", {}).get("role") == "summary"]
    result.selection = {
        "areas_rendered": len(area_slugs), "areas_total": len(ranked), "projects_rendered": len(project_slugs), "flows_rendered": len(flow_ids),
        "areas_not_rendered": max(0, len(ranked) - len(area_slugs)) if not areas else None, "kinds": sorted(wanted_kinds), "ai_included": bool(include_ai),
        "node_limit": ctx.max_nodes, "max_children": ctx.max_children, "decomposed_diagrams": len(summaries),
        "detail_diagrams": sum(d["decomposition"]["child_count"] for d in summaries), "skipped_empty": sorted(skipped), "note": "Diagrams are bounded; use --area/--project/--flow-id/--all-areas to choose scopes. Nothing is dropped silently: aggregates and partial info are in each model.",
    }
    manifest = {"contract": MANIFEST_CONTRACT, "contract_version": "1.0", "evidence_manifest_sha256": ctx.manifest_sha256, "selection": result.selection,
                "diagrams": result.diagrams}
    _write(root, MANIFEST_NAME, json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    result.seconds = round(perf_counter() - started, 3)
    return result
