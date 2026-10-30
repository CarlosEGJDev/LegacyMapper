"""`visuals` command: structured visual projections from an EXISTING deterministic output (post-V5 H3).

Why a separate command (and not `docs --visuals`): `docs` writes Markdown audience documentation; visuals write SVG + machine
readable models + a manifest and have their own scope controls (area / project / flow). Both read the same persisted
baseline through the same gate. No repository rescan, no AI provider, no free-form drawing.
"""
from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from legacy_documenter.visuals.model import KINDS

_HELP = (
    "Generate structured visual projections (SVG + machine-readable model + manifest) from an ALREADY generated, valid "
    "deterministic output: system-map, project-layer-map, dependency-map, observable-flow and data-interaction-map. It does NOT "
    "rescan the repository, does NOT rebuild Evidence and NEVER calls an AI provider. Every node/edge carries an epistemic status "
    "(confirmed / inferred / unresolved / AI interpretation / canonical) and traceable references. Output goes to <baseline>/visuals "
    "(or --output); the deterministic baseline is not modified."
)


def add_visuals_parser(subparsers) -> None:
    parser = subparsers.add_parser("visuals", help=_HELP, description=_HELP)
    parser.add_argument("baseline", help="Existing deterministic output directory (NOT a source repository)")
    parser.add_argument("--output", default=None, help="Directory for the visual package. Default: <baseline>/visuals")
    parser.add_argument("--area", action="append", default=None, help="Area (solution name or slug) to render (repeatable)")
    parser.add_argument("--project", action="append", default=None, help="Project (name or slug) to render (repeatable)")
    parser.add_argument("--flow-id", action="append", default=None, help="Flow id for an observable-flow diagram (repeatable)")
    parser.add_argument("--top-areas", type=int, default=3, help="Without --area/--project/--flow-id: render the N most active areas (default 3)")
    parser.add_argument("--all-areas", action="store_true", help="Render every area (many files)")
    parser.add_argument("--kind", action="append", choices=KINDS, default=None, help="Only these diagram kinds (repeatable)")
    parser.add_argument("--max-nodes", type=int, default=40, help="Node bound per diagram; the rest is aggregated, never dropped silently (default 40)")
    parser.add_argument("--max-children", type=int, default=30, help="Bound of detail diagrams per decomposed (dense) diagram; unexpanded ones are recorded in the summary (default 30)")
    parser.add_argument("--ai-run", default=None, help="AI run directory whose proposals/canonical records may be drawn (only with --include-ai)")
    parser.add_argument("--include-ai", action="store_true", help="Draw AI interpretations / canonical knowledge on observable-flow diagrams, always labelled apart")
    parser.add_argument("--verify-evidence", choices=["fast", "hash"], default="fast", help="fast (default) or hash re-verification of evidence partitions")


def run_visuals(args: Namespace) -> tuple[int, str]:
    """Returns (exit_code, JSON message). 0 success; 4 invalid baseline/arguments (nothing written)."""
    from legacy_documenter.orchestration.ai_only import BaselineInvalid
    from legacy_documenter.visuals.model import VisualModelError
    from legacy_documenter.visuals.package import generate_visuals, load_context, load_knowledge_refs

    def refuse(reason: str) -> tuple[int, str]:
        return 4, json.dumps({"status": "VISUALS_INPUT_INVALID", "reason": reason, "provider_calls": 0, "source_scanned": False},
                             ensure_ascii=False, sort_keys=True, indent=2)

    try:
        if args.include_ai and not args.ai_run:
            return refuse("INCLUDE_AI_REQUIRES_AI_RUN")
        if args.ai_run and not Path(args.ai_run).is_dir():
            return refuse(f"AI_RUN_NOT_FOUND:{args.ai_run}")
        if args.max_nodes < 4:
            return refuse("MAX_NODES_TOO_SMALL")
        knowledge = load_knowledge_refs(args.ai_run) if args.ai_run and args.include_ai else None
        ctx = load_context(args.baseline, knowledge, args.verify_evidence, args.max_nodes, args.max_children)
        baseline = Path(args.baseline)
        output = Path(args.output) if args.output else baseline / "visuals"
        if output.resolve() == baseline.resolve():
            return refuse("VISUALS_OUTPUT_IS_BASELINE")
        result = generate_visuals(ctx, output, areas=args.area, projects=args.project, flows=args.flow_id, kinds=args.kind,
                                  top_areas=args.top_areas, all_areas=args.all_areas, include_ai=args.include_ai)
    except BaselineInvalid as exc:
        return refuse(f"{exc.reason}:{exc.detail}" if exc.detail else exc.reason)
    except KeyError as exc:
        return refuse(f"SCOPE_NOT_FOUND:{exc.args[0]}")
    except VisualModelError as exc:
        return 4, json.dumps({"status": "VISUAL_MODEL_INVALID", "reason": str(exc)}, ensure_ascii=False, sort_keys=True, indent=2)
    payload = {
        "status": "SUCCESS", "output": str(result.output), "manifest": "VISUALS_MANIFEST.json", "diagrams": len(result.diagrams),
        "largest_svg_bytes": max((d["svg_bytes"] for d in result.diagrams), default=0), "partial_diagrams": sum(1 for d in result.diagrams if d["partial"]["partial"]),
        "selection": result.selection, "provider_calls": 0, "source_scanned": False, "baseline_modified": False, "seconds": result.seconds,
    }
    return 0, json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
