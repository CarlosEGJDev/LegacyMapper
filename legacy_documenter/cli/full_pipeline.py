"""Resilient orchestration for `python main.py full <repository> --output <dir>`.

Implements the V4.2 full pipeline boundary:

    SCAN -> EXTRACTION -> CALL_RESOLUTION -> WEB_ENTRY_RESOLUTION ->
    DATABASE_RESOLUTION -> FLOW_RESOLUTION -> DEPENDENCY_RESOLUTION ->
    EXPORT -> CONTEXT -> DOCUMENTATION -> AI_INTERPRETATION ->
    PROPOSAL_GENERATION -> FINAL_SUMMARY

The first nine stages (through DOCUMENTATION) are deterministic and always
run, reusing the exact stage functions `analyze_repository` uses
(`legacy_documenter.cli.pipeline_stages`) wrapped so one stage's failure does
not abort stages that do not depend on it (see
docs/V4_2/V4_2_R0_FULL_PIPELINE_ARCHITECTURE_AND_INVENTORY_RESULT.md's
partial-failure policy). AI_INTERPRETATION and PROPOSAL_GENERATION
(V4.2-R4) are explicitly opt-in (`allow_ai_interpretation=True`, wired from
`--allow-ai-interpretation`) -- without opt-in they report `NOT_RUN` and no
provider is ever contacted. This module contains no AI/proposal logic of its
own: it only calls into `legacy_documenter.orchestration.ai_interpretation`
and `legacy_documenter.orchestration.proposal_adapter`, the same way it calls
into `pipeline_stages` for the deterministic stages, per V4.2-R4's explicit
instruction to keep this file free of AI domain logic. Neither this module
nor the orchestration package it calls ever invokes knowledge/approval,
canonical knowledge, or R11/R12 projection.
"""
from __future__ import annotations

import dataclasses
from pathlib import Path
from time import perf_counter
from typing import Callable, TypeVar

from legacy_documenter.cli import pipeline_stages as stages
from legacy_documenter.cli.execution_model import RunResult, RunStatus, StageError, StageResult, StageStatus
from legacy_documenter.cli.run_summary_presenter import (
    compute_output_locations, derive_next_action, render_markdown_summary,
)
from legacy_documenter.cli.serialization import render_run_result
from legacy_documenter.cli.stage_identity import StageId
from legacy_documenter.knowledge.proposals.models import Proposal
from legacy_documenter.llm.core import LLMProvider
from legacy_documenter.orchestration import ai_interpretation, proposal_adapter
from legacy_documenter.orchestration.ai_interpretation import AiInterpretationResult
from legacy_documenter.utils.json_rendering import render_deterministic_json

RUN_SUMMARY_JSON = "RUN_SUMMARY.json"
RUN_SUMMARY_MARKDOWN = "RUN_SUMMARY.md"

_T = TypeVar("_T")


def run_full_pipeline(
    repo_root: str | Path,
    output_dir: str | Path,
    excludes: list[str] | None,
    flow_max_depth: int,
    allow_ai_interpretation: bool = False,
    ai_provider: LLMProvider | None = None,
) -> RunResult:
    """Executes the full pipeline and writes the run summary artifact.

    `allow_ai_interpretation` is the only thing that can make AI_INTERPRETATION/
    PROPOSAL_GENERATION run at all -- it defaults to `False`, so a plain
    `run_full_pipeline(...)` call remains 100% deterministic and makes zero
    provider calls (V4.2-R4 section 3). `ai_provider`, when supplied, replaces
    provider resolution entirely -- this is the seam tests use so no real
    provider/network call ever occurs; production code never passes it,
    letting `orchestration.ai_interpretation` resolve a real provider through
    the existing `ProviderRegistry`.

    Returns the final `RunResult` (also what was written, pre-`FINAL_SUMMARY`,
    to `RUN_SUMMARY.json`/`.md` under `output_dir`). See `_compute_status` for
    the exact, non-subjective definition of SUCCESS/PARTIAL/FAILED.
    """
    start = perf_counter()
    output = Path(output_dir).resolve()
    stage_results: list[StageResult] = []

    scan_outcome, scan_result = _run_stage(StageId.SCAN, lambda: stages.scan_repository(repo_root, excludes))
    stage_results.append(scan_result)
    scan_ok = scan_result.status is StageStatus.SUCCESS

    extraction_outcome = None
    if scan_ok:
        extraction_outcome, extraction_result = _run_stage(
            StageId.EXTRACTION, lambda: stages.extract_repository(scan_outcome.files, scan_outcome.root)
        )
    else:
        extraction_result = _skipped(StageId.EXTRACTION, StageId.SCAN)
    stage_results.append(extraction_result)
    extraction_ok = extraction_result.status is StageStatus.SUCCESS

    call_outcome = None
    if extraction_ok:
        call_outcome, call_result = _run_stage(
            StageId.CALL_RESOLUTION, lambda: stages.resolve_calls(extraction_outcome.calls, extraction_outcome.symbols)
        )
    else:
        call_result = _skipped(StageId.CALL_RESOLUTION, StageId.EXTRACTION)
    stage_results.append(call_result)
    call_ok = call_result.status is StageStatus.SUCCESS

    web_entry_outcome = None
    if call_ok:
        web_entry_outcome, web_entry_result = _run_stage(
            StageId.WEB_ENTRY_RESOLUTION,
            lambda: stages.resolve_web_entries(
                extraction_outcome.webforms, extraction_outcome.symbols, extraction_outcome.web_events, call_outcome.calls
            ),
        )
    else:
        web_entry_result = _skipped(StageId.WEB_ENTRY_RESOLUTION, StageId.CALL_RESOLUTION)
    stage_results.append(web_entry_result)
    web_entry_ok = web_entry_result.status is StageStatus.SUCCESS

    database_outcome = None
    if extraction_ok:
        database_outcome, database_result = _run_stage(
            StageId.DATABASE_RESOLUTION,
            lambda: stages.resolve_database(extraction_outcome.data_access_indexes, extraction_outcome.projects),
        )
    else:
        database_result = _skipped(StageId.DATABASE_RESOLUTION, StageId.EXTRACTION)
    stage_results.append(database_result)
    database_ok = database_result.status is StageStatus.SUCCESS

    functional_dependencies: list[dict] = []
    if call_ok:
        functional_dependencies = functional_dependencies + call_outcome.functional_dependencies
    if web_entry_ok:
        functional_dependencies = functional_dependencies + web_entry_outcome.functional_dependencies
    if database_ok:
        functional_dependencies = functional_dependencies + database_outcome.functional_dependencies

    flow_outcome = None
    if call_ok and web_entry_ok and database_ok:
        flow_outcome, flow_result = _run_stage(
            StageId.FLOW_RESOLUTION,
            lambda: stages.resolve_flows(
                web_entry_outcome.entry_points, call_outcome.calls, database_outcome.data_access,
                database_outcome.stored_procedures, database_outcome.sql_operations,
                functional_dependencies, extraction_outcome.errors if extraction_outcome else [], flow_max_depth,
            ),
        )
    else:
        blocked_by = [
            stage for stage, ok in (
                (StageId.CALL_RESOLUTION, call_ok),
                (StageId.WEB_ENTRY_RESOLUTION, web_entry_ok),
                (StageId.DATABASE_RESOLUTION, database_ok),
            ) if not ok
        ]
        flow_result = _skipped(StageId.FLOW_RESOLUTION, *blocked_by)
    stage_results.append(flow_result)

    dependency_outcome = None
    if extraction_ok:
        dependency_outcome, dependency_result = _run_stage(
            StageId.DEPENDENCY_RESOLUTION,
            lambda: stages.resolve_dependencies(
                extraction_outcome.solutions, extraction_outcome.projects, extraction_outcome.symbols, extraction_outcome.webforms
            ),
        )
    else:
        dependency_result = _skipped(StageId.DEPENDENCY_RESOLUTION, StageId.EXTRACTION)
    stage_results.append(dependency_result)

    if extraction_ok:
        indexes = _assemble_indexes(
            scan_outcome, extraction_outcome, call_outcome, web_entry_outcome, database_outcome,
            flow_outcome, dependency_outcome, functional_dependencies, round(perf_counter() - start, 3),
        )
        _, export_result = _run_stage(StageId.EXPORT, lambda: stages.export_artifacts(output, indexes))
        _, context_result = _run_stage(StageId.CONTEXT, lambda: stages.build_context_artifacts(output, indexes))
        documentation_result = _run_documentation_stage(output, indexes)
    else:
        export_result = _skipped(StageId.EXPORT, StageId.EXTRACTION)
        context_result = _skipped(StageId.CONTEXT, StageId.EXTRACTION)
        documentation_result = _skipped(StageId.DOCUMENTATION, StageId.EXTRACTION)
    stage_results.append(export_result)
    stage_results.append(context_result)
    stage_results.append(documentation_result)

    ai_result: AiInterpretationResult | None = None
    ai_invoked = False
    if allow_ai_interpretation:
        # AI_INTERPRETATION's real prerequisite is CONTEXT succeeding -- it reads
        # `output/ai_context/*.json`, which only CONTEXT writes (see
        # `legacy_documenter.orchestration.ai_interpretation`'s context-boundary
        # requirement: current-run evidence only, never a historical snapshot).
        if context_result.status is StageStatus.SUCCESS:
            ai_result, ai_stage_result = _run_ai_interpretation_stage(output, ai_provider)
            ai_invoked = bool(ai_result and ai_result.provider_called)
        else:
            ai_stage_result = _skipped(StageId.AI_INTERPRETATION, StageId.CONTEXT)
    else:
        ai_stage_result = StageResult(stage=StageId.AI_INTERPRETATION, status=StageStatus.NOT_RUN)
    stage_results.append(ai_stage_result)

    proposals: list[Proposal] = []
    if allow_ai_interpretation:
        if ai_stage_result.status is StageStatus.SUCCESS:
            proposal_outcome, proposal_stage_result = _run_stage(
                StageId.PROPOSAL_GENERATION,
                lambda: proposal_adapter.adapt_findings_to_proposals(ai_result.findings),
            )
            proposals = proposal_outcome or []
        else:
            proposal_stage_result = _skipped(StageId.PROPOSAL_GENERATION, StageId.AI_INTERPRETATION)
    else:
        proposal_stage_result = StageResult(stage=StageId.PROPOSAL_GENERATION, status=StageStatus.NOT_RUN)
    stage_results.append(proposal_stage_result)

    proposal_review_status: str | None = None
    if allow_ai_interpretation and ai_result is not None:
        proposal_review_status = _write_proposal_output(output, ai_result, proposals)

    proposal_count = len(proposals) if allow_ai_interpretation else 0
    has_extraction_errors = bool(extraction_outcome.errors) if extraction_outcome else False
    status = _compute_status(stage_results, has_extraction_errors)
    preliminary_result = RunResult(
        command="full", status=status, stages=tuple(stage_results), ai_invoked=ai_invoked,
        ai_requested=allow_ai_interpretation, proposal_count=proposal_count,
        proposal_review_status=proposal_review_status,
    )
    preliminary_result = dataclasses.replace(
        preliminary_result,
        next_action=derive_next_action(preliminary_result, allow_ai_interpretation, proposal_count),
        output_locations=tuple(compute_output_locations(output)),
    )

    summary_result = _write_run_summary(output, preliminary_result)
    all_stage_results = stage_results + [summary_result]
    final_status = _compute_status(all_stage_results, has_extraction_errors)
    message = (
        f"full run {final_status.value}: {len(all_stage_results)} stage(s) reported"
        + (f", {len(proposals)} proposal(s) pending Technical Lead review" if allow_ai_interpretation else "")
        + f"; summary written to {output / RUN_SUMMARY_JSON}"
    )
    final_result = RunResult(
        command="full", status=final_status, stages=tuple(all_stage_results), message=message, ai_invoked=ai_invoked,
        ai_requested=allow_ai_interpretation, proposal_count=proposal_count,
        proposal_review_status=proposal_review_status,
    )
    return dataclasses.replace(
        final_result,
        next_action=derive_next_action(final_result, allow_ai_interpretation, proposal_count),
        output_locations=tuple(compute_output_locations(output)),
    )


def _run_stage(stage_id: StageId, action: Callable[[], _T]) -> tuple[_T | None, StageResult]:
    """Runs one stage's action, converting any exception into a `StageError` rather than propagating it."""
    try:
        outcome = action()
    except Exception as exc:
        error = StageError(stage=stage_id, category=exc.__class__.__name__, message=str(exc))
        return None, StageResult(stage=stage_id, status=StageStatus.FAILED, error=error)
    return outcome, StageResult(stage=stage_id, status=StageStatus.SUCCESS)


def _skipped(stage_id: StageId, *blocked_by: StageId) -> StageResult:
    """Builds a SKIPPED_DUE_TO_UPSTREAM_FAILURE result naming the stage(s) responsible."""
    names = ", ".join(stage.value for stage in blocked_by)
    error = StageError(
        stage=stage_id, category="UPSTREAM_DEPENDENCY_FAILED",
        message=f"Skipped because required upstream stage(s) did not succeed: {names}.",
    )
    return StageResult(stage=stage_id, status=StageStatus.SKIPPED_DUE_TO_UPSTREAM_FAILURE, error=error)


def _run_documentation_stage(output: Path, indexes: dict) -> StageResult:
    """Runs the DOCUMENTATION stage (V4.2-R3).

    `stages.render_documentation` never raises for an individual renderer's
    failure -- it records each in `DocumentationOutcome.failures` internally,
    per the "one bad renderer must not destroy the others" policy -- so this
    wrapper (unlike `_run_stage`) inspects that outcome rather than relying on
    exception propagation to detect failure. A genuinely unexpected exception
    from `render_documentation` itself (e.g. the `documentation/` directory
    cannot be created at all) is still caught and reported the normal way.
    """
    try:
        outcome = stages.render_documentation(output, indexes)
    except Exception as exc:
        error = StageError(stage=StageId.DOCUMENTATION, category=exc.__class__.__name__, message=str(exc))
        return StageResult(stage=StageId.DOCUMENTATION, status=StageStatus.FAILED, error=error)
    if not outcome.failures:
        return StageResult(stage=StageId.DOCUMENTATION, status=StageStatus.SUCCESS)
    message = "; ".join(f"{name}: {reason}" for name, reason in outcome.failures)
    error = StageError(stage=StageId.DOCUMENTATION, category="RENDERER_FAILURE", message=message)
    return StageResult(stage=StageId.DOCUMENTATION, status=StageStatus.FAILED, error=error)


def _run_ai_interpretation_stage(
    output: Path, provider: LLMProvider | None
) -> tuple[AiInterpretationResult | None, StageResult]:
    """Runs the AI_INTERPRETATION stage (V4.2-R4), only ever reached when the
    caller explicitly opted in and CONTEXT succeeded.

    `orchestration.ai_interpretation.run_ai_interpretation` never raises for a
    provider/validation failure -- it returns an `AiInterpretationResult` with
    `status != "SUCCESS"` instead -- so, like `_run_documentation_stage`, this
    wrapper inspects that result rather than relying on exception propagation.
    The result is still returned (not discarded) on failure so
    `result.provider_called` can inform `RunResult.ai_invoked` even when
    interpretation itself failed after actually reaching the provider.
    """
    try:
        result = ai_interpretation.run_ai_interpretation(output, provider=provider)
    except Exception as exc:
        error = StageError(stage=StageId.AI_INTERPRETATION, category=exc.__class__.__name__, message=str(exc))
        return None, StageResult(stage=StageId.AI_INTERPRETATION, status=StageStatus.FAILED, error=error)
    if result.status == "SUCCESS":
        return result, StageResult(stage=StageId.AI_INTERPRETATION, status=StageStatus.SUCCESS)
    error = StageError(
        stage=StageId.AI_INTERPRETATION, category=result.status, message=result.error_message or result.status,
    )
    return result, StageResult(stage=StageId.AI_INTERPRETATION, status=StageStatus.FAILED, error=error)


def _write_proposal_output(output: Path, ai_result: AiInterpretationResult, proposals: list[Proposal]) -> str:
    """Persists AI-generated proposals under `output/proposals/`, deliberately
    separate from `output/index/` (which represents deterministic analysis only).

    Writes `AI_PROPOSALS.json` (authoritative, deterministic -- reuses the same
    `render_deterministic_json` helper the rest of V4.2 already shares) and a
    small human-readable `AI_PROPOSALS_PENDING_REVIEW.md`. Every proposal here
    is `ProposalStatus.READY_FOR_REVIEW`: the envelope's own `status` field
    states `PENDING_TECHNICAL_LEAD_REVIEW` explicitly -- never approved, never
    canonical. Called only when `--allow-ai-interpretation` was passed and AI
    interpretation actually returned a result; `analyze` never calls this, so
    its output tree is unaffected. Returns the envelope's `status` string
    (V4.2-R5's `RunResult.proposal_review_status`), so the caller does not
    have to recompute `bool(proposals)` a second time.
    """
    proposals_dir = output / "proposals"
    proposals_dir.mkdir(parents=True, exist_ok=True)
    envelope = {
        "schema_version": "1.0",
        "status": "PENDING_TECHNICAL_LEAD_REVIEW" if proposals else "NO_PROPOSALS_GENERATED",
        "ai_interpretation_status": ai_result.status,
        "provider_id": ai_result.provider_id,
        "model_id": ai_result.model_id,
        "context_package_id": ai_result.context_package_id,
        "proposals": [_proposal_to_dict(proposal) for proposal in proposals],
    }
    (proposals_dir / "AI_PROPOSALS.json").write_text(render_deterministic_json(envelope), encoding="utf-8")
    (proposals_dir / "AI_PROPOSALS_PENDING_REVIEW.md").write_text(_render_proposal_markdown(envelope), encoding="utf-8")
    return envelope["status"]


def _proposal_to_dict(proposal: Proposal) -> dict:
    """Renders one `Proposal` as a plain, JSON-primitive dict.

    `dataclasses.asdict` alone leaves `proposal_kind`/`proposal_method`/`status`
    as live `(str, Enum)` instances -- `json.dumps` happens to render those
    correctly (it takes the str fast path), but an f-string does not (Enum's
    own `__str__` prints `"ClassName.MEMBER"`, not the plain value) -- so this
    explicitly normalizes to `.value` up front, once, for both the JSON
    envelope and the Markdown rendering to share safely.
    """
    payload = dataclasses.asdict(proposal)
    payload["proposal_kind"] = proposal.proposal_kind.value
    payload["proposal_method"] = proposal.proposal_method.value
    payload["status"] = proposal.status.value
    return payload


def _render_proposal_markdown(envelope: dict) -> str:
    """Renders a short human-readable pending-review listing (pure formatting, no new logic)."""
    lines = [
        "# AI Proposals -- Pending Technical Lead Review",
        "",
        f"- Status: **{envelope['status']}**",
        f"- AI interpretation status: `{envelope['ai_interpretation_status']}`",
        f"- Provider: `{envelope.get('provider_id') or 'n/a'}` / Model: `{envelope.get('model_id') or 'n/a'}`",
        "",
    ]
    if not envelope["proposals"]:
        lines.append("No proposals were generated in this run.")
        lines.append("")
        return "\n".join(lines)
    lines.append("## Proposals")
    lines.append("")
    for proposal in envelope["proposals"]:
        lines.append(f"### {proposal['proposal_id']}")
        lines.append("")
        lines.append(
            f"- Kind: `{proposal['proposal_kind']}` | Method: `{proposal['proposal_method']}` | "
            f"Status: `{proposal['status']}`"
        )
        lines.append(f"- Statement: {proposal['statement']}")
        if proposal.get("rationale"):
            lines.append(f"- Rationale: {proposal['rationale']}")
        refs = ", ".join(f"`{ref}`" for ref in proposal.get("evidence_refs", []))
        lines.append(f"- Evidence: {refs or '_none_'}")
        lines.append("")
    lines.append(
        "**This document does not constitute approval.** Every proposal above is "
        "PENDING_TECHNICAL_LEAD_REVIEW; only a human Technical Lead decision (a future round) "
        "can approve, reject, or correct it."
    )
    lines.append("")
    return "\n".join(lines)


def _compute_status(stage_results: list[StageResult], has_extraction_errors: bool) -> RunStatus:
    """Derives RunStatus non-subjectively.

    "Minimally useful deterministic analysis package" = EXTRACTION completed
    AND EXPORT completed -- i.e. real analysis artifacts exist under
    `--output`. Without that, the run is FAILED regardless of anything else.
    With it, any recorded per-file extraction error, any FAILED stage, or any
    SKIPPED_DUE_TO_UPSTREAM_FAILURE stage downgrades the run to PARTIAL rather
    than silently reporting SUCCESS.
    """
    by_stage = {result.stage: result.status for result in stage_results}
    extraction_ok = by_stage.get(StageId.EXTRACTION) is StageStatus.SUCCESS
    export_ok = by_stage.get(StageId.EXPORT) is StageStatus.SUCCESS
    if not extraction_ok or not export_ok:
        return RunStatus.FAILED
    any_trouble = has_extraction_errors or any(
        status in (StageStatus.FAILED, StageStatus.SKIPPED_DUE_TO_UPSTREAM_FAILURE) for status in by_stage.values()
    )
    return RunStatus.PARTIAL if any_trouble else RunStatus.SUCCESS


def _assemble_indexes(
    scan_outcome, extraction_outcome, call_outcome, web_entry_outcome, database_outcome,
    flow_outcome, dependency_outcome, functional_dependencies: list[dict], duration_seconds: float,
) -> dict:
    """Builds the same `indexes` shape `analyze_repository` builds, from whatever
    stages actually succeeded. A field whose producing stage failed/was skipped
    is an empty container -- an honest "nothing produced", never invented data.
    `calls` is the one exception: it falls back to the raw extracted (unresolved)
    calls when CALL_RESOLUTION itself did not succeed, because extraction did
    produce real call data even though it could not be resolved.
    """
    calls = call_outcome.calls if call_outcome else extraction_outcome.calls
    return {
        "repository": {
            "root": str(scan_outcome.root),
            "stats": scan_outcome.classifier.stats([item.to_dict() for item in scan_outcome.files]),
            "ignored": scan_outcome.scanner.ignored,
            "duration_seconds": duration_seconds,
        },
        "files": [item.to_dict() for item in scan_outcome.files],
        "solutions": extraction_outcome.solutions,
        "projects": extraction_outcome.projects,
        "symbols": extraction_outcome.symbols,
        "logical_symbols": extraction_outcome.logical_symbols,
        "calls": calls,
        "entry_points": web_entry_outcome.entry_points if web_entry_outcome else [],
        "event_bindings": web_entry_outcome.event_bindings if web_entry_outcome else [],
        "data_access": database_outcome.data_access if database_outcome else [],
        "stored_procedures": database_outcome.stored_procedures if database_outcome else [],
        "sql_operations": database_outcome.sql_operations if database_outcome else [],
        "data_parameters": database_outcome.data_parameters if database_outcome else [],
        "functional_dependencies": functional_dependencies,
        "functional_flows": flow_outcome.functional_flows if flow_outcome else [],
        "functional_paths": flow_outcome.functional_paths if flow_outcome else [],
        "flow_summary": flow_outcome.flow_summary if flow_outcome else {},
        "flow_unresolved": flow_outcome.flow_unresolved if flow_outcome else [],
        "webforms": extraction_outcome.webforms,
        "configuration": extraction_outcome.configuration,
        "dependencies": dependency_outcome if dependency_outcome is not None else [],
        "errors": extraction_outcome.errors,
    }


def _write_run_summary(output: Path, result: RunResult) -> StageResult:
    """Runs the FINAL_SUMMARY stage: writes the deterministic run-summary artifacts.

    `RUN_SUMMARY.json` (authoritative, machine-readable, deterministic -- reuses
    the same `render_run_result` the R1 execution model already defines) and
    `RUN_SUMMARY.md` (a small human-readable rendering of the same data, no
    separate logic). Both are written to `output_dir`, never inside the
    analyzed repository.
    """
    try:
        output.mkdir(parents=True, exist_ok=True)
        (output / RUN_SUMMARY_JSON).write_text(render_run_result(result), encoding="utf-8")
        (output / RUN_SUMMARY_MARKDOWN).write_text(render_markdown_summary(result), encoding="utf-8")
    except Exception as exc:
        error = StageError(stage=StageId.FINAL_SUMMARY, category=exc.__class__.__name__, message=str(exc))
        return StageResult(stage=StageId.FINAL_SUMMARY, status=StageStatus.FAILED, error=error)
    return StageResult(stage=StageId.FINAL_SUMMARY, status=StageStatus.SUCCESS)
