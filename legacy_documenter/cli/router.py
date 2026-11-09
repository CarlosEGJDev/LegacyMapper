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
from pathlib import Path
from typing import Protocol

from legacy_documenter.cli.execution_model import RunResult, RunStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.cli.output_manifest import MANIFEST_FILENAME, build_output_manifest
from legacy_documenter.knowledge.readiness import run as run_readiness
from legacy_documenter.utils.atomic_write import atomic_write_text
from legacy_documenter.utils.json_rendering import render_deterministic_json
from legacy_documenter.utils.path_contract import (
    OUTPUT_MANIFEST_INPUT_NOT_DIRECTORY, OUTPUT_MANIFEST_INPUT_NOT_FOUND, validate_existing_output_directory,
)

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
        self, repo_root: str, output_dir: str, excludes: list[str] | None = None, flow_max_depth: int = 12, **identity: object
    ) -> dict: ...


def route(args: Namespace, analyze_repository: AnalyzeRepository) -> tuple[int, RunResult]:
    """Dispatches one parsed command to its implementation and returns (exit_code, RunResult)."""
    if args.command == "analyze":
        return _route_analyze(args, analyze_repository)
    if args.command == "full":
        return _route_full(args)
    if args.command == "readiness":
        return _route_readiness()
    if args.command == "output-manifest":
        return _route_output_manifest(args)
    if args.command == "review":
        return _route_review(args)
    if args.command == "interpret":
        return _route_interpret(args)
    if args.command == "docs":
        return _route_docs(args)
    if args.command == "visuals":
        return _route_visuals(args)
    if args.command == "deliver":
        return _route_deliver(args)
    if args.command == "interpret-system":
        return _route_interpret_system(args)
    if args.command == "project-system":
        return _route_project_system(args)
    raise ValueError(f"Unknown command: {args.command!r}")


def _identity_kwargs(args: Namespace) -> dict:
    """`repository_id` is forwarded only when declared, so undeclared runs call the pipelines exactly as before."""
    repository_id = getattr(args, "repository_id", None)
    return {"repository_id": repository_id} if repository_id else {}


def _route_analyze(args: Namespace, analyze_repository: AnalyzeRepository) -> tuple[int, RunResult]:
    """Runs the existing deterministic analysis pipeline unchanged."""
    analyze_repository(args.repository, args.output, args.exclude, args.flow_max_depth, **_identity_kwargs(args))
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
        long_paths=getattr(args, "long_paths", False),
        cache_mode=getattr(args, "cache_mode", "auto"),
        cache_dir=getattr(args, "cache_dir", None),
        verify_cache=getattr(args, "verify_cache", "fast"),
        trust_mtime=getattr(args, "trust_mtime", False),
        incremental_max_changed_ratio=getattr(args, "incremental_max_changed_ratio", None),
        **_identity_kwargs(args),
    )
    return _EXIT_CODE_BY_STATUS[result.status], result


def _route_readiness() -> tuple[int, RunResult]:
    """Thin route to the existing readiness gate; does not duplicate its logic."""
    payload = run_readiness()
    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
    status = RunStatus.SUCCESS if payload.get("readiness") == "READY" else RunStatus.PARTIAL
    exit_code = EXIT_SUCCESS if status is RunStatus.SUCCESS else EXIT_PARTIAL
    return exit_code, RunResult(command="readiness", status=status, message=rendered)


def _route_output_manifest(args: Namespace) -> tuple[int, RunResult]:
    """Builds and writes `<output_dir>/OUTPUT_MANIFEST.json` (V4.3-R7 BLOQUEO 1).

    Thin route to `legacy_documenter.cli.output_manifest.build_output_manifest`,
    the same deterministic manifest builder `tools/v4_3_r7_build_output_manifest.py`
    already wrapped for development-repository use -- this route is its runtime
    equivalent, part of the `legacy_documenter` package itself, so it travels with
    a clean, development-repository-independent distribution
    (`tools/v4_3_r7_build_pilot_distribution.py`; see
    docs/V4_3/V4_3_REAL_PILOT_INSTRUCTIONS.md). `FileNotFoundError` (missing/
    non-directory `output_dir`) is CLI usage error territory, not a pipeline
    failure -- it propagates uncaught, the same way argparse's own usage errors
    do, rather than being mapped to `RunStatus.FAILED`. Since pre-H5 Gate A.1 the CLI route validates the directory first with the
    shared path contract, so the expected invalid input surfaces as a controlled `PathContractError` (exit 4, JSON on stderr).
    """
    # Gate A.1: an expected-input error is a PathContractError (stderr JSON + exit 4 in `main`), never a raw traceback,
    # and it is raised before anything is written.
    validate_existing_output_directory(
        args.output_dir, not_found_code=OUTPUT_MANIFEST_INPUT_NOT_FOUND, not_directory_code=OUTPUT_MANIFEST_INPUT_NOT_DIRECTORY, writable=True)
    manifest = build_output_manifest(args.output_dir)
    target = Path(args.output_dir) / MANIFEST_FILENAME
    atomic_write_text(target, render_deterministic_json(manifest))
    message = f"Wrote {target}: {manifest['file_count']} file(s), {manifest['total_bytes']} byte(s) total."
    return EXIT_SUCCESS, RunResult(command="output-manifest", status=RunStatus.SUCCESS, message=message)


def _route_review(args: Namespace) -> tuple[int, RunResult]:
    """Thin route to the explicit human review command (V5.7); never reached by `full`/`analyze`."""
    from legacy_documenter.cli.review_command import run_review

    exit_code, message = run_review(args)
    status = RunStatus.SUCCESS if exit_code == EXIT_SUCCESS else RunStatus.FAILED
    return exit_code, RunResult(command="review", status=status, message=message)


def _route_interpret(args: Namespace) -> tuple[int, RunResult]:
    """Thin route to the AI-only command (post-V5 H1); never scans or analyzes a repository."""
    from legacy_documenter.cli.interpret_command import run_interpret

    exit_code, message, ai_invoked = run_interpret(args)
    status = {EXIT_SUCCESS: RunStatus.SUCCESS, EXIT_PARTIAL: RunStatus.PARTIAL}.get(exit_code, RunStatus.FAILED)
    return exit_code, RunResult(command="interpret", status=status, message=message, ai_invoked=ai_invoked, ai_requested=True)


def _route_docs(args: Namespace) -> tuple[int, RunResult]:
    """Thin route to the audience documentation command (post-V5 H2); no analysis, no provider."""
    from legacy_documenter.cli.docs_command import run_docs

    exit_code, message = run_docs(args)
    status = RunStatus.SUCCESS if exit_code == EXIT_SUCCESS else RunStatus.FAILED
    return exit_code, RunResult(command="docs", status=status, message=message)


def _route_visuals(args: Namespace) -> tuple[int, RunResult]:
    """Thin route to the structured visual projections command (post-V5 H3); no analysis, no provider."""
    from legacy_documenter.cli.visuals_command import run_visuals

    exit_code, message = run_visuals(args)
    status = RunStatus.SUCCESS if exit_code == EXIT_SUCCESS else RunStatus.FAILED
    return exit_code, RunResult(command="visuals", status=status, message=message)


def _route_interpret_system(args: Namespace) -> tuple[int, RunResult]:
    """Thin route to the full-system hierarchical interpretation (owner acceptance remediation R1); never scans a repository."""
    from legacy_documenter.cli.system_command import run_interpret_system

    exit_code, message, ai_invoked = run_interpret_system(args)
    status = {EXIT_SUCCESS: RunStatus.SUCCESS, EXIT_PARTIAL: RunStatus.PARTIAL}.get(exit_code, RunStatus.FAILED)
    return exit_code, RunResult(command="interpret-system", status=status, message=message, ai_invoked=ai_invoked, ai_requested=True)


def _route_project_system(args: Namespace) -> tuple[int, RunResult]:
    """Thin route to the deterministic human + machine system projection; no analysis, no provider."""
    from legacy_documenter.cli.system_command import run_project_system

    exit_code, message = run_project_system(args)
    status = {EXIT_SUCCESS: RunStatus.SUCCESS, EXIT_PARTIAL: RunStatus.PARTIAL}.get(exit_code, RunStatus.FAILED)
    return exit_code, RunResult(command="project-system", status=status, message=message)


def _route_deliver(args: Namespace) -> tuple[int, RunResult]:
    """Thin route to the final human package command (post-V5 H4); no analysis, no provider."""
    from legacy_documenter.cli.deliver_command import run_deliver

    exit_code, message = run_deliver(args)
    status = RunStatus.SUCCESS if exit_code == EXIT_SUCCESS else RunStatus.FAILED
    return exit_code, RunResult(command="deliver", status=status, message=message)
