"""Routes parsed CLI arguments to the appropriate existing capability.

This module decides *which* already-implemented capability a command calls;
it must never re-implement analysis, knowledge, or readiness logic itself
(see V4.2-R0's "CLI is an orchestration boundary, not a second domain layer").
`full` routes to `legacy_documenter.cli.full_pipeline.run_full_pipeline`
(V4.2-R2's resilient deterministic orchestrator) — the router itself contains
no pipeline logic, only the exit-code mapping for its `RunStatus`.
"""
from __future__ import annotations

import json
from argparse import Namespace
from typing import Protocol

from legacy_documenter.cli.execution_model import RunResult, RunStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.knowledge.readiness import run as run_readiness

# Exit-code contract, established V4.2-R2 and explicitly reaffirmed as
# authoritative by the Technical Lead at V4.2-R5.1 (scripts must be able to
# distinguish all four):
#   0 = SUCCESS            (analyze/full/readiness)
#   1 = PARTIAL             (full/readiness)
#   2 = CLI_USAGE_ERROR     (argparse itself, e.g. unknown command/missing argument -- not assigned here)
#   4 = FAILED               (full)
# 3 (NOT_IMPLEMENTED_FOR_R1) was `full`'s R1 placeholder code; it is retired
# now that `full` is implemented and is deliberately not reused for anything
# else, so an R1-era script checking for exit code 3 fails loudly instead of
# misreading a real R2 outcome.
# V4.2-R5's own prompt document momentarily stated a different, incorrect
# 0/4/5/2 contract; the Technical Lead's V4.2-R5.1 review resolved this in
# favor of the contract actually implemented and tested since R2 (this one)
# -- see docs/V4_2/V4_2_R5_1_EXIT_CODE_CONTRACT_AND_REAL_PROVIDER_GUARD_RESULT.md.
# Runtime behavior below was not changed by that resolution.
EXIT_SUCCESS = 0
EXIT_PARTIAL = 1
EXIT_FAILED = 4

_EXIT_CODE_BY_STATUS = {
    RunStatus.SUCCESS: EXIT_SUCCESS,
    RunStatus.PARTIAL: EXIT_PARTIAL,
    RunStatus.FAILED: EXIT_FAILED,
}


class AnalyzeRepository(Protocol):
    """Shape of `legacy_documenter.main.analyze_repository`, injected to avoid a circular import."""

    def __call__(
        self, repo_root: str, output_dir: str, excludes: list[str] | None = None, flow_max_depth: int = 12
    ) -> dict: ...


def route(args: Namespace, analyze_repository: AnalyzeRepository) -> tuple[int, RunResult]:
    """Dispatches one parsed command to its implementation and returns (exit_code, RunResult)."""
    if args.command == "analyze":
        return _route_analyze(args, analyze_repository)
    if args.command == "full":
        return _route_full(args)
    if args.command == "readiness":
        return _route_readiness()
    raise ValueError(f"Unknown command: {args.command!r}")


def _route_analyze(args: Namespace, analyze_repository: AnalyzeRepository) -> tuple[int, RunResult]:
    """Runs the existing deterministic analysis pipeline unchanged."""
    analyze_repository(args.repository, args.output, args.exclude, args.flow_max_depth)
    return EXIT_SUCCESS, RunResult(command="analyze", status=RunStatus.SUCCESS)


def _route_full(args: Namespace) -> tuple[int, RunResult]:
    """Runs the full pipeline.

    `allow_ai_interpretation` only ever becomes `True` here when the caller
    passed `--allow-ai-interpretation` explicitly (V4.2-R4); without it, no
    provider is ever contacted. Knowledge ingestion, approval, canonical
    knowledge, and R11/R12 projection are never invoked from this route at
    all, opt-in or not.
    """
    allow_ai_interpretation = getattr(args, "allow_ai_interpretation", False)
    result = run_full_pipeline(
        args.repository, args.output, args.exclude, args.flow_max_depth,
        allow_ai_interpretation=allow_ai_interpretation,
    )
    return _EXIT_CODE_BY_STATUS[result.status], result


def _route_readiness() -> tuple[int, RunResult]:
    """Thin route to the existing readiness gate; does not duplicate its logic."""
    payload = run_readiness()
    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
    status = RunStatus.SUCCESS if payload.get("readiness") == "READY" else RunStatus.PARTIAL
    exit_code = EXIT_SUCCESS if status is RunStatus.SUCCESS else EXIT_PARTIAL
    return exit_code, RunResult(command="readiness", status=status, message=rendered)
