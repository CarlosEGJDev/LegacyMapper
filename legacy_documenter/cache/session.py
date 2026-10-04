"""One run's use of the V5.3 cache (R2.4): decide the mode, build the current File State, compare, persist.

R2.4 only *records* the outcome (mode cold/warm/fallback_full, reason, diff counts, timings -- logged at INFO);
nothing is skipped or reused yet and no output changes. The cache can never break a run: every failure here is
caught and logged as a warning, and the run proceeds exactly as without a cache. The previous manifest is
removed as soon as the comparison is done, so an interrupted or unsuccessful run leaves no valid cache.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any

from .context import CacheContext, build_context
from .diff import FileStateDiff, diff_file_states
from .extraction import ExtractionCache
from .file_state import FileRecord, build_file_state
from .run_metrics import now_iso
from .run_report import write_metrics
from .manifest import (
    CACHE_DIRNAME, MODE_FALLBACK_FULL, MODE_WARM, CacheValidationResult, validate_cache,
)
from .store import invalidate_manifest, sweep_temporary_files, write_cache

LOG = logging.getLogger(__name__)

CACHE_MODES = ("auto", "off", "refresh")
MODE_OFF = "off"
#: R2.5 gate (docs/V5/V5_3_R2_5_EXTRACTION_CACHE.md): whether the extraction cache is consumed/written by default.
EXTRACTION_CACHE_DEFAULT_ENABLED = True


@dataclass
class CacheSession:
    """What this run knows about the cache. `enabled=False` makes `persist` a no-op."""

    enabled: bool = False
    mode: str = MODE_OFF
    reason: str | None = None
    cache_dir: Path | None = None
    context: CacheContext | None = None
    records: list[FileRecord] | None = None
    validation: CacheValidationResult | None = None
    diff: FileStateDiff | None = None
    extraction: ExtractionCache | None = None
    timings: dict = field(default_factory=dict)
    started_at: str = ""

    def finish(
        self, final_status: str, total_seconds: float, extraction_outcome: Any = None,
        dependency_outcome: list[dict] | None = None,
    ) -> None:
        """End of run (V5.3-R2.7): persist the cache after a SUCCESS run, then write `RUN_METRICS.json` for any status."""
        if final_status == "SUCCESS":
            self.persist()  # manifest written last; a PARTIAL/FAILED run leaves no valid cache
        write_metrics(self, final_status, total_seconds, extraction_outcome, dependency_outcome)

    def persist(self) -> bool:
        """Writes the new cache (call only after a SUCCESS run). Failure is logged, never raised."""
        if not self.enabled or self.context is None or self.records is None or self.cache_dir is None:
            return False
        started = perf_counter()
        try:
            write_cache(self.cache_dir, self.context, self.records, self.extraction)
        except Exception as exc:  # the main output is already valid; a cache failure must not change that
            LOG.warning("cache: no se pudo escribir %s (%s: %s); la corrida sigue siendo válida", self.cache_dir, exc.__class__.__name__, exc)
            return False
        LOG.info("cache: written %s", {"files": len(self.records), "persist_seconds": round(perf_counter() - started, 3)})
        if self.extraction is not None:
            LOG.info("cache: extraction %s", self.extraction.summary())
            self.extraction.release()
        return True


def begin_cache_session(
    repo_root: str | Path, output_dir: str | Path, files: list, excludes: list[str] | None, flow_max_depth: int,
    cache_mode: str = "auto", cache_dir: str | Path | None = None, extraction_cache: bool | None = None,
) -> CacheSession:
    """Validates any previous cache, builds the current File State and diffs them. Never raises."""
    if cache_mode == MODE_OFF:
        return CacheSession()
    if cache_mode not in CACHE_MODES:
        LOG.warning("cache: modo desconocido %r; caché desactivada para esta corrida", cache_mode)
        return CacheSession()
    try:
        target = Path(cache_dir) if cache_dir else Path(output_dir) / CACHE_DIRNAME
        timings: dict[str, float] = {}
        started_iso = now_iso()
        started = perf_counter()
        context = build_context(repo_root, excludes, flow_max_depth)
        swept = sweep_temporary_files(target)
        validation = (
            CacheValidationResult(False, MODE_FALLBACK_FULL, "REFRESH_REQUESTED") if cache_mode == "refresh"
            else validate_cache(target, context)
        )
        timings["validate_seconds"] = round(perf_counter() - started, 3)
        started = perf_counter()
        records = build_file_state(Path(repo_root).resolve(), files)
        timings["file_state_build_seconds"] = round(perf_counter() - started, 3)
        diff = None
        if validation.mode == MODE_WARM:
            started = perf_counter()
            diff = diff_file_states(validation.records, records)
            timings["diff_seconds"] = round(perf_counter() - started, 3)
        extraction = None
        if EXTRACTION_CACHE_DEFAULT_ENABLED if extraction_cache is None else extraction_cache:
            extraction = ExtractionCache(context, records)
            if validation.mode == MODE_WARM:  # cold / fallback_full: nothing to reuse, shards are (re)generated
                extraction.load(target, validation.manifest)
        invalidate_manifest(target)
        session = CacheSession(
            True, validation.mode, validation.reason, target, context, records, validation, diff, extraction, timings, started_iso,
        )
        LOG.info("cache: %s", {
            "mode": session.mode, "reason": session.reason, "files": len(records), "temporaries_removed": swept,
            "diff": diff.counts() if diff else None,
            "informational_differences": validation.informational_differences, **timings,
            "extraction_cache": extraction.summary() if extraction else None,
            "extraction_reuse_disabled_reason": extraction.reuse_disabled_reason if extraction else None,
        })
        return session
    except Exception as exc:
        LOG.warning("cache: desactivada para esta corrida (%s: %s)", exc.__class__.__name__, exc)
        return CacheSession()
