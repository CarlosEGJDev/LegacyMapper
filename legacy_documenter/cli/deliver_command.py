"""`deliver` command: the final human package (HTML site + PDFs) from an EXISTING deterministic output (post-V5 H4).

Thin adapter over `legacy_documenter.deliver`. It accepts a deterministic OUTPUT directory (produced by `full`/`analyze`), never
a source repository: it does not scan, parse or analyze anything and never calls a provider. It reuses the H1 baseline gate, so
an invalid baseline is refused before anything is written. H2 audience documentation and H3 visuals are generated from the
persisted baseline into a staging area (or consumed from `--docs-dir` / `--visuals-dir`), then composed into one package.
"""
from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from legacy_documenter.documentation_v52.engine import AUDIENCE_PROFILES

_HELP = (
    "Generate the final human package from an ALREADY generated, valid deterministic output: a static offline HTML site "
    "(executive / functional / technical, the ten delivery surfaces and the H3 diagrams) plus PDFs. It does NOT rescan the "
    "repository, does NOT rebuild Evidence and NEVER calls an AI provider. Output goes to <baseline>/human_package (or --output); "
    "the deterministic baseline is not modified. Open index.html from disk; the manifest is DELIVERABLES_MANIFEST.json."
)


def add_deliver_parser(subparsers) -> None:
    parser = subparsers.add_parser("deliver", help=_HELP, description=_HELP)
    parser.add_argument("baseline", help="Existing deterministic output directory (NOT a source repository)")
    parser.add_argument("--output", default=None, help="Directory for the package. Default: <baseline>/human_package")
    parser.add_argument("--audience", action="append", choices=AUDIENCE_PROFILES, default=None, help="Audience to include (repeatable). Default: all three")
    parser.add_argument("--docs-dir", default=None, help="Consume existing `docs` output (a directory holding documentation_v52/ or the profiles) instead of generating it")
    parser.add_argument("--visuals-dir", default=None, help="Consume an existing `visuals` package (must come from the same baseline) instead of generating it")
    parser.add_argument("--ai-run", default=None, help="AI run directory whose proposals/canonical records are shown, always labelled apart")
    parser.add_argument("--include-ai", action="store_true", help="Also draw AI interpretations / canonical knowledge on observable-flow diagrams (requires --ai-run)")
    parser.add_argument("--area", action="append", default=None, help="Area (solution name or slug) to render diagrams for (repeatable)")
    parser.add_argument("--project", action="append", default=None, help="Project (name or slug) to render diagrams for (repeatable)")
    parser.add_argument("--flow-id", action="append", default=None, help="Flow id for an observable-flow diagram (repeatable)")
    parser.add_argument("--top-areas", type=int, default=10, help="Without --area/--project/--flow-id: diagrams for the N most active areas (default 10)")
    parser.add_argument("--all-areas", action="store_true", help="Diagrams for every area (many files)")
    parser.add_argument("--max-nodes", type=int, default=40, help="Node bound per diagram; the rest is aggregated, never dropped silently (default 40)")
    parser.add_argument("--max-children", type=int, default=30, help="Bound of detail diagrams per decomposed diagram (default 30)")
    parser.add_argument("--no-pdf", action="store_true", help="Do not generate the PDF documents")
    parser.add_argument("--pdf-row-cap", type=int, default=30, help="Rows shown per table in the PDFs; the HTML always has the full list (default 30)")
    parser.add_argument("--verify-evidence", choices=["fast", "hash"], default="fast", help="fast (default) or hash re-verification of evidence partitions")


def run_deliver(args: Namespace) -> tuple[int, str]:
    """Returns (exit_code, JSON message). 0 success; 4 invalid baseline/arguments (nothing written)."""
    from legacy_documenter.deliver.package import DeliveryInvalid, generate_delivery
    from legacy_documenter.orchestration.ai_only import BaselineInvalid
    from legacy_documenter.visuals.model import VisualModelError

    def refuse(reason: str) -> tuple[int, str]:
        return 4, json.dumps({"status": "DELIVER_INPUT_INVALID", "reason": reason, "provider_calls": 0, "source_scanned": False},
                             ensure_ascii=False, sort_keys=True, indent=2)

    if args.max_nodes < 4:
        return refuse("MAX_NODES_TOO_SMALL")
    if args.pdf_row_cap < 1:
        return refuse("PDF_ROW_CAP_TOO_SMALL")
    baseline = Path(args.baseline)
    output = Path(args.output) if args.output else baseline / "human_package"
    try:
        result = generate_delivery(
            baseline, output, audiences=tuple(args.audience or AUDIENCE_PROFILES), docs_dir=args.docs_dir, visuals_dir=args.visuals_dir,
            ai_run=args.ai_run, include_ai=args.include_ai, areas=args.area, projects=args.project, flows=args.flow_id, top_areas=args.top_areas,
            all_areas=args.all_areas, max_nodes=args.max_nodes, max_children=args.max_children, make_pdf=not args.no_pdf, row_cap=args.pdf_row_cap,
            verify_evidence=args.verify_evidence)
    except (BaselineInvalid, DeliveryInvalid) as exc:
        return refuse(f"{exc.reason}:{exc.detail}" if exc.detail else exc.reason)
    except KeyError as exc:
        return refuse(f"SCOPE_NOT_FOUND:{exc.args[0]}")
    except VisualModelError as exc:
        return 4, json.dumps({"status": "VISUAL_MODEL_INVALID", "reason": str(exc)}, ensure_ascii=False, sort_keys=True, indent=2)
    counts = result.manifest["counts"]
    payload = {
        "status": "SUCCESS", "output": str(result.output), "entry": "index.html", "manifest": "DELIVERABLES_MANIFEST.json", **counts,
        "pdfs": sorted(result.pdfs), "deliverables": len(result.manifest["deliverables"]),
        "diagrams": result.manifest["visual_package"]["diagrams"], "partial_diagrams": result.manifest["visual_package"]["partial_diagrams"],
        "unresolvable_references": result.manifest["unresolvable_references"]["count"],
        "provider_calls": 0, "source_scanned": False, "baseline_modified": False, "seconds": result.seconds,
    }
    return 0, json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
