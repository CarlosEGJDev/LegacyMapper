"""End-of-run reporting (V5.3-R2.7): scope analysis + `RUN_METRICS.json` for one cache session.

Pure observability layered on a finished run (`session` is the run's `CacheSession`, typed `Any` to keep this module
from importing `session`, which imports it). It reads the session's facts (mode, diff, timings), the run's
in-memory ledgers (write-skip, stage timings) and the extraction/dependency outcomes the pipeline already holds
(no extra index is built, nothing is copied). It never raises into the pipeline and never decides anything: no stage
is skipped and no output changes because of it.
"""
from __future__ import annotations

import logging
from time import perf_counter
from typing import Any

from legacy_documenter.utils.stage_timings import TIMINGS
from legacy_documenter.utils.write_if_changed import LEDGER

from .run_metrics import build_run_metrics, write_run_metrics
from .scope import ScopeAnalysisResult, analyze_scope

LOG = logging.getLogger(__name__)


def _session_mode(session: Any) -> str:
    return "refresh" if session.reason == "REFRESH_REQUESTED" else session.mode


def compute_scope(session: Any, extraction_outcome: Any, dependency_outcome: list[dict] | None) -> ScopeAnalysisResult:
    """The scope analysis of this run (full-mode result when there is no usable previous state)."""
    previous = {record.path: record.file_type for record in session.validation.records} if session.validation else {}
    file_types = {**previous, **{record.path: record.file_type for record in session.records}}
    projects = extraction_outcome.projects if extraction_outcome is not None else None
    reason = session.reason if session.diff is None else None
    if projects is None and reason is None:
        reason = "EXTRACTION_UNAVAILABLE"
    return analyze_scope(
        session.diff, reason, file_types, projects, dependency_outcome,
        extraction_outcome.symbols if extraction_outcome is not None else None,
    )


def write_metrics(
    session: Any, final_status: str, total_seconds: float, extraction_outcome: Any,
    dependency_outcome: list[dict] | None,
) -> bool:
    """Builds and writes `RUN_METRICS.json` into the session's cache directory. Failure is logged, never raised."""
    if not session.enabled or session.context is None or session.cache_dir is None:
        return False
    try:
        started = perf_counter()
        scope = compute_scope(session, extraction_outcome, dependency_outcome)
        scope_seconds = perf_counter() - started
        started = perf_counter()
        document = build_run_metrics(
            session_mode=_session_mode(session), fallback_reason=session.reason, context=session.context,
            started_at=session.started_at, total_seconds=total_seconds, final_status=final_status,
            file_count=len(session.records or []), diff_counts=session.diff.counts() if session.diff else None,
            timings=session.timings, extraction=session.extraction.summary() if session.extraction else None,
            reuse_disabled_reason=session.extraction.reuse_disabled_reason if session.extraction else None,
            stage_snapshot=TIMINGS.snapshot(), write_skip=LEDGER.snapshot(), scope=scope.to_dict(),
            overhead_seconds={"scope_analysis": round(scope_seconds, 3)},
        )
        build_seconds = perf_counter() - started
        started = perf_counter()
        write_run_metrics(session.cache_dir, document)
        document["overhead_seconds"].update(
            {"metrics_build": round(build_seconds, 3), "metrics_write": round(perf_counter() - started, 3)},
        )
        LOG.info("run metrics: scope=%s overhead=%s", scope.mode, document["overhead_seconds"])
        return True
    except Exception as exc:  # observability must never change a run
        LOG.warning("cache: no se pudieron escribir las métricas (%s: %s)", exc.__class__.__name__, exc)
        return False
