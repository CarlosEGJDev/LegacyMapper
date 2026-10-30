"""`interpret` command: AI-only interpretation over an existing deterministic output (post-V5 H1).

Thin adapter over `legacy_documenter.orchestration.ai_only`. Accepts a deterministic OUTPUT directory,
never a source repository; it does not scan, parse or analyze anything.
"""
from __future__ import annotations

import json
from argparse import Namespace

from legacy_documenter.context.composer import PROFILES

_HELP = (
    "AI-only: run AI interpretation + proposal generation over an ALREADY generated, valid deterministic output "
    "(a directory produced by `analyze` or `full`). It does NOT rescan the repository, does NOT rebuild Evidence or "
    "documentation, and requires a valid existing baseline: an invalid one is refused with AI_ONLY_INPUT_INVALID "
    "before any provider call. It may call the configured AI provider. Proposals are written to a separate AI run "
    "directory (default <baseline>/ai_runs/<run-id>), pending human review -- never approved, never canonical."
)


def add_interpret_parser(subparsers) -> None:
    parser = subparsers.add_parser("interpret", help=_HELP, description=_HELP)
    parser.add_argument("baseline", help="Existing deterministic output directory (NOT a source repository)")
    parser.add_argument("--output", default=None, help="AI run directory (must be new/empty). Default: <baseline>/ai_runs/<run-id>")
    parser.add_argument("--profile", choices=[p for p in PROFILES if p != "FULL"], default="SMALL", help="Context budget profile (default SMALL)")
    parser.add_argument("--flow-id", action="append", default=None, help="Scope to this flow id (repeatable); default: bounded deterministic selection")
    parser.add_argument("--verify-evidence", choices=["hash", "fast"], default="hash",
                        help="hash (default): re-hash every evidence partition against EVIDENCE_MANIFEST.json; fast: presence/size only")


def run_interpret(args: Namespace) -> tuple[int, str, bool]:
    """Returns (exit_code, JSON message, ai_invoked). 0 success; 1 AI stage failed after a valid baseline; 4 invalid input."""
    from legacy_documenter.orchestration.ai_only import AI_ONLY_INPUT_INVALID, run_ai_only

    result = run_ai_only(args.baseline, args.output, flow_ids=args.flow_id, profile=args.profile, verify_evidence=args.verify_evidence)
    payload = {"status": result.status, "reason": result.reason, "provider_called": result.provider_called,
               "proposal_count": result.proposal_count, "proposal_review_status": result.proposal_review_status,
               "ai_run_dir": str(result.ai_run_dir) if result.ai_run_dir else None,
               "canonical_knowledge_produced": False, "source_scanned": False, "seconds": result.seconds}
    if result.status == "SUCCESS":
        payload["next"] = f"review list --output {result.ai_run_dir}"
        return 0, json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2), result.provider_called
    code = 4 if result.status.startswith("AI_ONLY_") else 1
    return code, json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2), result.provider_called
