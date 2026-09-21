"""Console and Markdown presentation for `python main.py full` (V4.2-R5/R6).

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

V4.2-R6 additionally moved the "does the persisted RUN_SUMMARY represent
the true final run state" responsibility here
(`finalize_and_write_run_summary`) -- see that function's docstring for why
`compute_output_locations` was changed from a filesystem-existence check
into a stage-outcome check as part of the same fix.

Deliberately standard library only (see V4.2-R5 section 14): no third-party
CLI/table/color dependency is introduced for this.
"""
from __future__ import annotations

import dataclasses
from pathlib import Path

from legacy_documenter.cli.execution_model import RunResult, RunStatus, StageError, StageResult, StageStatus
from legacy_documenter.cli.serialization import render_run_result
from legacy_documenter.cli.stage_identity import StageId
from legacy_documenter.utils.atomic_write import atomic_write_text

_DETERMINISTIC_STAGE_IDS: tuple[StageId, ...] = (
    StageId.SCAN, StageId.EXTRACTION, StageId.CALL_RESOLUTION, StageId.WEB_ENTRY_RESOLUTION,
    StageId.DATABASE_RESOLUTION, StageId.FLOW_RESOLUTION, StageId.DEPENDENCY_RESOLUTION,
    StageId.EXPORT, StageId.CONTEXT,
)


def compute_output_locations(result: RunResult) -> list[str]:
    """Lists the well-known result locations THIS run actually produced.

    V4.2-R6 section 5/6: deliberately NOT a filesystem-existence check
    (that was R5's original implementation). Existence alone cannot tell
    "this run produced it" apart from "a stale artifact from an earlier
    run into the same `--output` directory is still sitting there" -- a
    real case (`full --allow-ai-interpretation` followed by a plain `full`
    into the same directory) that made a rerun's own summary list
    `proposals` as if it were current. Each location is reported only when
    the stage(s) that produce it succeeded in *this* run, so a rerun's
    summary can never describe output an earlier, different run made.
    """
    locations: list[str] = []
    if _stage_status(result, StageId.EXPORT) is StageStatus.SUCCESS:
        locations += ["documentation", "index"]
    if _stage_status(result, StageId.CONTEXT) is StageStatus.SUCCESS:
        # V4.3-R6 added `consumer_projection/` to what `build_context_artifacts`
        # writes, under the same CONTEXT failure boundary as `ai_context/` --
        # missed here until this V4.3-R7 acceptance pass caught it: a rerun's
        # summary/console output never told an operator that surface exists.
        locations += ["ai_context", "consumer_projection"]
    if result.proposal_review_status is not None:
        locations.append("proposals")
    if _stage_status(result, StageId.FINAL_SUMMARY) is StageStatus.SUCCESS:
        locations += ["RUN_SUMMARY.json", "RUN_SUMMARY.md"]
    return locations


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
    """Renders `result` as the durable `RUN_SUMMARY.md` record (V4.2-R5 section 8),
    in Spanish by default since the V4.3-R7 BLOQUEO 2 follow-up correction:
    `RUN_SUMMARY.md` is generated by the product, designed for human reading, and
    is exactly what `V4_3_REAL_PILOT_INSTRUCTIONS.md` tells an external pilot
    operator to consult to diagnose a `PARTIAL`/`FAILED` run -- it is
    human-readable/product-facing, so it follows the same Spanish-by-default rule
    every other such document already follows (`markdown_exporter.py`/
    `technical_documentation_renderer.py`).

    Pure formatting, no new logic: every value comes from `result` itself.
    Deliberately does not duplicate the technical documentation -- only the
    run outcome, stage table, AI/proposal/approval status, key artifacts, and
    next action.

    Only prose/headers/labels are translated. `StageId` values (`stage.stage.value`,
    e.g. `SCAN`/`EXPORT`), `RunStatus`/`StageStatus` values (e.g. `SUCCESS`/
    `PARTIAL`/`FAILED`), `stage.error.category`/`stage.error.message` (raw
    exception class names/messages -- technical, never translated), every
    `output_locations` path/filename, and `result.command` are preserved exactly
    as `RUN_SUMMARY.json` itself reports them (see `_derive_next_action_es` for
    why `result.next_action` itself, the JSON-contract field, is never read here).
    """
    lines = [
        "# Resumen de ejecución de LegacyMapper",
        "",
        f"- Comando: `{result.command}`",
        f"- Estado: **{result.status.value}**",
        f"- IA solicitada: {result.ai_requested}",
        f"- IA invocada: {result.ai_invoked}",
        f"- Cantidad de propuestas: {result.proposal_count}",
        f"- Estado de revisión de propuestas: {result.proposal_review_status or 'N/A'}",
        f"- Conocimiento canónico producido: {result.canonical_knowledge_produced}",
        f"- Aprobación del Líder Técnico: {result.technical_lead_approval}",
        "",
        "## Etapas",
        "",
        "| Etapa | Estado | Error |",
        "|---|---|---|",
    ]
    for stage in result.stages:
        error_text = f"{stage.error.category}: {stage.error.message}" if stage.error else ""
        lines.append(f"| {stage.stage.value} | {stage.status.value} | {error_text} |")
    lines.append("")
    if result.output_locations:
        lines.append("## Ubicaciones de salida")
        lines.append("")
        lines += [f"- `{location}`" for location in result.output_locations]
        lines.append("")
    lines.append("## Próxima acción")
    lines.append("")
    lines.append(_derive_next_action_es(result) or "")
    lines.append("")
    return "\n".join(lines)


def _derive_next_action_es(result: RunResult) -> str:
    """Spanish counterpart of `derive_next_action`, used only by `render_markdown_summary`.

    Mirrors `derive_next_action`'s exact decision logic -- never a second,
    independently-maintained rule, only its rendered sentence differs -- so the
    two can never silently diverge on *when* each message applies, only on the
    language of the message itself. `result.next_action` (the field
    `RUN_SUMMARY.json` and the console summary read, computed by
    `derive_next_action`) is never touched or read by this function: it stays
    exactly what `derive_next_action` already produces, in English, the
    established machine-adjacent `RUN_SUMMARY.json` contract field (V4.2-R5) this
    correction does not alter. Filenames/paths mentioned (`RUN_SUMMARY.json`,
    `proposals/AI_PROPOSALS_PENDING_REVIEW.md`) are preserved verbatim.
    """
    if result.status is RunStatus.FAILED:
        return "El análisis no produjo el mínimo de salida útil. Revise RUN_SUMMARY.json."
    if result.proposal_count > 0:
        return (
            "Hay propuestas de IA pendientes de revisión del Líder Técnico. "
            "Ver proposals/AI_PROPOSALS_PENDING_REVIEW.md."
        )
    ai_stage_status = _stage_status(result, StageId.AI_INTERPRETATION)
    if result.ai_requested and ai_stage_status is StageStatus.FAILED:
        return (
            "La documentación determinista está disponible; la interpretación de IA falló. "
            "Ver RUN_SUMMARY.json para más detalle."
        )
    if result.status is RunStatus.PARTIAL:
        return (
            "La documentación determinista está disponible, pero algunas etapas fueron "
            "parciales. Revise RUN_SUMMARY.json."
        )
    return "Documentación técnica generada correctamente."


def finalize_and_write_run_summary(
    output: Path, result: RunResult, json_filename: str, markdown_filename: str,
) -> StageResult:
    """Runs the FINAL_SUMMARY stage: atomically writes `RUN_SUMMARY.json`/`.md` (V4.2-R6).

    `result` is the run's outcome *before* FINAL_SUMMARY itself is known to
    have succeeded -- a file cannot describe its own write's outcome before
    that write happens. V4.2-R5 resolved this by simply omitting the
    FINAL_SUMMARY row from the persisted file, a real, documented gap
    against section 6's "persisted RUN_SUMMARY represents the final
    completed run state" invariant. V4.2-R6 closes it without introducing
    any actual self-reference: it builds the complete, true final state
    *in memory* first -- `result`'s stages plus one hypothetical
    `FINAL_SUMMARY: SUCCESS` entry, with `next_action`/`output_locations`
    recomputed against that complete stage list -- and renders exactly that
    to disk. This is sound precisely because nothing is persisted unless
    the write actually succeeds: if the atomic write itself raises, this
    function returns a FAILED stage result instead, and the "SUCCESS"
    content that was only ever held in memory is never written -- the
    previous run's last complete summary (if any) is left exactly as it
    was, never overwritten with a lie (see `atomic_write_text`).
    """
    final_stage = StageResult(stage=StageId.FINAL_SUMMARY, status=StageStatus.SUCCESS)
    complete = dataclasses.replace(result, stages=result.stages + (final_stage,))
    complete = dataclasses.replace(
        complete,
        next_action=derive_next_action(complete, complete.ai_requested, complete.proposal_count),
        output_locations=tuple(compute_output_locations(complete)),
    )
    try:
        atomic_write_text(output / json_filename, render_run_result(complete))
        atomic_write_text(output / markdown_filename, render_markdown_summary(complete))
    except Exception as exc:
        error = StageError(stage=StageId.FINAL_SUMMARY, category=exc.__class__.__name__, message=str(exc))
        return StageResult(stage=StageId.FINAL_SUMMARY, status=StageStatus.FAILED, error=error)
    return final_stage
