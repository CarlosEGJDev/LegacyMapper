"""Console and Markdown presentation for `python main.py full` (V4.2-R5).

R5 is UX/composition only: this module derives no new analysis, AI, or
approval outcomes -- it only reads the same `RunResult` fields
`full_pipeline.py` already computes (`ai_requested`, `ai_invoked`,
`proposal_count`, `proposal_review_status`, `canonical_knowledge_produced`,
`technical_lead_approval`) and renders them for two audiences: a concise
human console summary (`render_console_summary`) and the durable
`RUN_SUMMARY.md` record (`render_markdown_summary`, moved here from
`full_pipeline.py` per V4.2-R5 section 12's maintainability guard). It also
derives the two other additive fields R5 introduces: `next_action`
(`derive_next_action`) and `output_locations` (`compute_output_locations`).

Deliberately standard library only (see V4.2-R5 section 14): no third-party
CLI/table/color dependency is introduced for this.
"""
from __future__ import annotations

from pathlib import Path

from legacy_documenter.cli.execution_model import RunResult, RunStatus, StageResult, StageStatus
from legacy_documenter.cli.stage_identity import StageId

# Well-known result locations a `full` run may produce, in the order they are
# most useful to a developer who has never seen LegacyMapper's internals:
# documentation first (what they came for), then evidence, then the AI-review
# artifact (when it exists), then the two run-summary files themselves.
_OUTPUT_LOCATIONS_TO_CHECK: tuple[str, ...] = (
    "documentation",
    "index",
    "ai_context",
    "proposals",
    "RUN_SUMMARY.json",
    "RUN_SUMMARY.md",
)

_DETERMINISTIC_STAGE_IDS: tuple[StageId, ...] = (
    StageId.SCAN, StageId.EXTRACTION, StageId.CALL_RESOLUTION, StageId.WEB_ENTRY_RESOLUTION,
    StageId.DATABASE_RESOLUTION, StageId.FLOW_RESOLUTION, StageId.DEPENDENCY_RESOLUTION,
    StageId.EXPORT, StageId.CONTEXT,
)


def compute_output_locations(output_dir: Path) -> list[str]:
    """Lists, relative to `output_dir`, the well-known result locations that actually exist.

    A location not produced by this run (e.g. `proposals/` when
    `--allow-ai-interpretation` was never passed) is simply absent -- this is
    an existence check, not a description of what `full` is supposed to do.
    """
    return [name for name in _OUTPUT_LOCATIONS_TO_CHECK if (output_dir / name).exists()]


def _stage_status(result: RunResult, stage_id: StageId) -> StageStatus | None:
    for stage in result.stages:
        if stage.stage is stage_id:
            return stage.status
    return None


def _deterministic_analysis_status(result: RunResult) -> str:
    """Summarizes the nine always-run deterministic stages as one status word."""
    statuses = [status for status in (_stage_status(result, sid) for sid in _DETERMINISTIC_STAGE_IDS) if status]
    if not statuses:
        return "UNKNOWN"
    if all(status is StageStatus.SUCCESS for status in statuses):
        return "SUCCESS"
    extraction_ok = _stage_status(result, StageId.EXTRACTION) is StageStatus.SUCCESS
    export_ok = _stage_status(result, StageId.EXPORT) is StageStatus.SUCCESS
    return "PARTIAL" if extraction_ok and export_ok else "FAILED"


def _documentation_status(result: RunResult) -> str:
    status = _stage_status(result, StageId.DOCUMENTATION)
    return status.value if status else "UNKNOWN"


def derive_next_action(result: RunResult, ai_requested: bool, proposal_count: int) -> str:
    """Derives one deterministic recommended-next-action sentence from run state.

    Never implies the user has approved anything (V4.2-R5 section 6/11) and
    never auto-runs another command -- this only returns text.
    """
    if result.status is RunStatus.FAILED:
        return "Analysis did not produce the minimum useful output. Inspect RUN_SUMMARY.json."
    if proposal_count > 0:
        return (
            "AI proposals are pending Technical Lead review. "
            "See proposals/AI_PROPOSALS_PENDING_REVIEW.md."
        )
    ai_stage_status = _stage_status(result, StageId.AI_INTERPRETATION)
    if ai_requested and ai_stage_status is StageStatus.FAILED:
        return (
            "Deterministic documentation is available; AI interpretation failed. "
            "See RUN_SUMMARY.json for details."
        )
    if result.status is RunStatus.PARTIAL:
        return "Deterministic documentation is available, but some stages were partial. Review RUN_SUMMARY.json."
    return "Technical documentation generated successfully."


def render_console_summary(
    result: RunResult, repository: str, output_dir: Path, verbose: bool = False,
) -> str:
    """Renders the concise human console summary printed after `full` (V4.2-R5 section 5).

    Reads only fields already on `result` (never re-derives AI/approval
    outcomes) plus the two paths the caller has and `result` does not
    (`repository`, `output_dir`). Verbose mode additionally lists every stage.
    """
    lines = [
        f"LegacyMapper full run: {result.status.value}",
        f"  Repository: {repository}",
        f"  Output:     {output_dir}",
        "",
        f"  Deterministic analysis: {_deterministic_analysis_status(result)}",
        f"  Documentation:          {_documentation_status(result)}",
        "",
        f"  AI requested: {result.ai_requested}",
        f"  AI invoked:   {result.ai_invoked}",
    ]
    if result.ai_requested:
        proposal_line = f"  Proposals:    {result.proposal_review_status or 'UNAVAILABLE'}"
        if result.proposal_count:
            proposal_line += f" ({result.proposal_count} pending)"
        lines.append(proposal_line)
    lines += [
        "",
        f"  Canonical knowledge produced: {result.canonical_knowledge_produced}",
        f"  Technical Lead approval:      {result.technical_lead_approval}",
    ]
    if result.output_locations:
        lines.append("")
        lines.append("  Output locations (relative to output directory):")
        lines += [f"    - {location}" for location in result.output_locations]
    if verbose:
        lines.append("")
        lines.append("  Stages:")
        for stage in result.stages:
            detail = f" ({stage.error.category}: {stage.error.message})" if stage.error else ""
            lines.append(f"    - {stage.stage.value}: {stage.status.value}{detail}")
    lines.append("")
    lines.append(f"Next action: {result.next_action or derive_next_action(result, result.ai_requested, result.proposal_count)}")
    return "\n".join(lines)


def render_markdown_summary(result: RunResult) -> str:
    """Renders `result` as the durable `RUN_SUMMARY.md` record (V4.2-R5 section 8).

    Pure formatting, no new logic: every value comes from `result` itself.
    Deliberately does not duplicate the technical documentation -- only the
    run outcome, stage table, AI/proposal/approval status, key artifacts, and
    next action.
    """
    lines = [
        "# LegacyMapper Run Summary",
        "",
        f"- Command: `{result.command}`",
        f"- Status: **{result.status.value}**",
        f"- AI requested: {result.ai_requested}",
        f"- AI invoked: {result.ai_invoked}",
        f"- Proposal count: {result.proposal_count}",
        f"- Proposal review status: {result.proposal_review_status or 'N/A'}",
        f"- Canonical knowledge produced: {result.canonical_knowledge_produced}",
        f"- Technical Lead approval: {result.technical_lead_approval}",
        "",
        "## Stages",
        "",
        "| Stage | Status | Error |",
        "|---|---|---|",
    ]
    for stage in result.stages:
        error_text = f"{stage.error.category}: {stage.error.message}" if stage.error else ""
        lines.append(f"| {stage.stage.value} | {stage.status.value} | {error_text} |")
    lines.append("")
    if result.output_locations:
        lines.append("## Output Locations")
        lines.append("")
        lines += [f"- `{location}`" for location in result.output_locations]
        lines.append("")
    lines.append("## Next Action")
    lines.append("")
    lines.append(result.next_action or "")
    lines.append("")
    return "\n".join(lines)
