"""`docs` command: audience-level human documentation from an EXISTING deterministic output (post-V5 H2).

Thin adapter over `legacy_documenter.documentation_v52`. It accepts a deterministic OUTPUT directory (produced by
`full`/`analyze`), never a source repository: it does not scan, parse or analyze anything and never calls a provider.
It reuses the H1 baseline gate, so an invalid baseline is refused before anything is written.
"""
from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

from legacy_documenter.documentation_v52.engine import AUDIENCE_PROFILES

_HELP = (
    "Generate audience-level human documentation (executive, functional, technical_overview) from an ALREADY "
    "generated, valid deterministic output (a directory produced by `full` or `analyze`). It does NOT rescan the "
    "repository, does NOT rebuild Evidence and NEVER calls an AI provider. Output goes to <baseline>/audience_docs "
    "(or --output); the deterministic baseline is not modified. Optionally include AI proposals / canonical knowledge "
    "from an AI run directory (--ai-run), always labelled apart from confirmed facts."
)


def add_docs_parser(subparsers) -> None:
    parser = subparsers.add_parser("docs", help=_HELP, description=_HELP)
    parser.add_argument("baseline", help="Existing deterministic output directory (NOT a source repository)")
    parser.add_argument("--output", default=None, help="Directory to write documentation_v52/<audience>/ into. Default: <baseline>/audience_docs")
    parser.add_argument("--audience", action="append", choices=AUDIENCE_PROFILES, default=None,
                        help="Audience to generate (repeatable). Default: all three")
    parser.add_argument("--ai-run", default=None, help="AI run directory (from `interpret` or `full --allow-ai-interpretation`) whose proposals/canonical records are shown, clearly labelled")
    parser.add_argument("--verify-evidence", choices=["fast", "hash"], default="fast",
                        help="fast (default): presence/size of evidence partitions; hash: re-hash them against EVIDENCE_MANIFEST.json")
    parser.add_argument("--long-paths", action="store_true", help="Windows only: write through extended-length paths")


def run_docs(args: Namespace) -> tuple[int, str]:
    """Returns (exit_code, JSON message). 0 success; 4 invalid baseline/output (nothing written)."""
    from time import perf_counter

    from legacy_documenter.documentation_v52.audience import load_knowledge_overlay
    from legacy_documenter.documentation_v52.engine import generate_documentation_v52, source_from_indexes
    from legacy_documenter.orchestration._run_evidence_io import load_indexes
    from legacy_documenter.orchestration.ai_only import BaselineInvalid, validate_baseline

    started = perf_counter()
    try:
        info = validate_baseline(args.baseline, args.verify_evidence)
        baseline = info.baseline_dir
        output = Path(args.output) if args.output else baseline / "audience_docs"
        if output.resolve() == baseline.resolve():
            raise BaselineInvalid("DOCS_OUTPUT_IS_BASELINE", "use a separate --output or the default audience_docs")
        knowledge = None
        if args.ai_run:
            if not Path(args.ai_run).is_dir():
                raise BaselineInvalid("AI_RUN_NOT_FOUND", str(args.ai_run))
            knowledge = load_knowledge_overlay(args.ai_run)
        external_path = baseline / "evidence" / "external_dependencies.json"
        external = json.loads(external_path.read_text(encoding="utf-8")) if external_path.is_file() else []
        source = source_from_indexes(load_indexes(baseline), external)
    except BaselineInvalid as exc:
        reason = f"{exc.reason}:{exc.detail}" if exc.detail else exc.reason
        return 4, json.dumps({"status": "DOCS_INPUT_INVALID", "reason": reason, "provider_calls": 0, "source_scanned": False},
                             ensure_ascii=False, sort_keys=True, indent=2)
    profiles = tuple(args.audience or AUDIENCE_PROFILES)
    result = generate_documentation_v52(
        source, output, profiles=profiles, long_paths=args.long_paths, knowledge=knowledge,
        deep_reference=(baseline / "documentation_v52" / "developer").is_dir(),
    )
    payload = {
        "status": "SUCCESS", "output": str(result.output_dir),
        "profiles": {pid: {k: data[k] for k in ("files", "bytes", "max_file_bytes", "output_dir")} for pid, data in result.profiles.items()},
        "ai_proposals_shown": len(knowledge["proposals"]) if knowledge else 0,
        "canonical_records_shown": len(knowledge["canonical"]) if knowledge else 0,
        "warnings": result.warnings, "provider_calls": 0, "source_scanned": False, "baseline_modified": False,
        "seconds": round(perf_counter() - started, 3),
    }
    return 0, json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
