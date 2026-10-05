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
from .manifest import MODE_FALLBACK_FULL, MODE_WARM, CacheValidationResult, validate_cache
from .options import (
    CACHE_MODES, VERIFY_FAST, VERIFY_HASH, CacheOptionError, CacheOptions, describe_location, resolve_cache_dir,
)
from .verify import VERIFY_FAILED, verify_cache_deep
from .store import invalidate_manifest, sweep_temporary_files, write_cache

LOG = logging.getLogger(__name__)

MODE_OFF = "off"
CHANGED_RATIO_EXCEEDED = "CHANGED_RATIO_EXCEEDED"
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
    options: CacheOptions | None = None
    controls: dict = field(default_factory=dict)  # R2.8: what the cache controls did this run (for RUN_METRICS)

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


def _verified(target: Path, validation: CacheValidationResult, options: CacheOptions, controls: dict, timings: dict) -> CacheValidationResult:
    """`--verify-cache=hash`: a warm cache with any inconsistency is refused (strict, see `verify`); else unchanged."""
    controls["verify_cache"] = options.verify
    if options.verify != VERIFY_HASH or validation.mode != MODE_WARM:
        return validation
    started = perf_counter()
    failure = verify_cache_deep(target, validation.manifest, validation.records)
    timings["verify_seconds"] = round(perf_counter() - started, 3)
    controls["verify_seconds"] = timings["verify_seconds"]
    controls["verify_result"] = "ok" if failure is None else "failed"
    if failure is None:
        return validation
    controls["verify_failure"] = failure
    return CacheValidationResult(False, MODE_FALLBACK_FULL, VERIFY_FAILED)


def _current_file_state(repo_root: str | Path, files: list, validation: CacheValidationResult, options: CacheOptions, controls: dict) -> list[FileRecord]:
    """The File State of this run; with `--trust-mtime` and a warm cache, unchanged (size, mtime_ns) files are not re-hashed."""
    trusted = {r.path: r for r in validation.records} if options.trust_mtime and validation.mode == MODE_WARM else None
    records = build_file_state(Path(repo_root).resolve(), files, trusted=trusted)
    count = sum(1 for r in records if trusted and trusted.get(r.path) is r)
    controls["trust_mtime"] = {"enabled": options.trust_mtime, "files_trusted": count, "files_hashed": len(records) - count}
    return records


def _after_diff(validation: CacheValidationResult, diff: FileStateDiff, options: CacheOptions, controls: dict) -> CacheValidationResult:
    """Records the observed change ratio; above `--incremental-max-changed-ratio` the warm cache is refused (a safe full run)."""
    controls["incremental_max_changed_ratio"] = options.max_changed_ratio
    controls["observed_changed_ratio"] = None
    if not validation.records:  # previous file count 0: the ratio is undefined and never triggers
        return validation
    counts = diff.counts()
    observed = round((counts["modified"] + counts["added"] + counts["deleted"]) / len(validation.records), 6)
    controls["observed_changed_ratio"] = observed
    if options.max_changed_ratio is not None and observed > options.max_changed_ratio:
        return CacheValidationResult(False, MODE_FALLBACK_FULL, CHANGED_RATIO_EXCEEDED)
    return validation


def begin_cache_session(
    repo_root: str | Path, output_dir: str | Path, files: list, excludes: list[str] | None, flow_max_depth: int,
    cache_mode: str = "auto", cache_dir: str | Path | None = None, extraction_cache: bool | None = None,
    *, verify_cache: str = VERIFY_FAST, trust_mtime: bool = False, max_changed_ratio: float | None = None,
) -> CacheSession:
    """Validates any previous cache, builds the current File State and diffs them. Never raises.

    The R2.8 controls (see `options.CacheOptions`) only decide how much of a *valid* cache is trusted: `off` touches
    nothing, `refresh` ignores the old cache, `verify_cache="hash"` refuses a cache with any inconsistency,
    `trust_mtime` lets unchanged `(size, mtime_ns)` skip hashing, `max_changed_ratio` turns a too-changed warm run into
    a full one. None of them changes what a full run would produce.
    """
    if cache_mode == MODE_OFF:
        return CacheSession()
    try:
        options = CacheOptions(cache_mode, cache_dir, verify_cache, trust_mtime, max_changed_ratio).validate()
        target = resolve_cache_dir(repo_root, output_dir, cache_dir)
    except CacheOptionError as exc:
        LOG.warning("cache: %s; caché desactivada para esta corrida", exc)
        return CacheSession()
    try:
        timings: dict[str, float] = {}
        controls: dict = {"requested_mode": options.mode, **describe_location(target, output_dir)}
        started_iso = now_iso()
        started = perf_counter()
        context = build_context(repo_root, excludes, flow_max_depth)
        swept = sweep_temporary_files(target)
        validation = (
            CacheValidationResult(False, MODE_FALLBACK_FULL, "REFRESH_REQUESTED") if options.mode == "refresh"
            else validate_cache(target, context)
        )
        timings["validate_seconds"] = round(perf_counter() - started, 3)
        validation = _verified(target, validation, options, controls, timings)
        started = perf_counter()
        records = _current_file_state(repo_root, files, validation, options, controls)
        timings["file_state_build_seconds"] = round(perf_counter() - started, 3)
        diff = None
        controls.update({"incremental_max_changed_ratio": options.max_changed_ratio, "observed_changed_ratio": None})
        if validation.mode == MODE_WARM:
            started = perf_counter()
            diff = diff_file_states(validation.records, records)
            timings["diff_seconds"] = round(perf_counter() - started, 3)
            validation = _after_diff(validation, diff, options, controls)
        extraction = None
        if EXTRACTION_CACHE_DEFAULT_ENABLED if extraction_cache is None else extraction_cache:
            extraction = ExtractionCache(context, records)
            if validation.mode == MODE_WARM:  # cold / fallback_full: nothing to reuse, shards are (re)generated
                extraction.load(target, validation.manifest)
        invalidate_manifest(target)
        session = CacheSession(
            True, validation.mode, validation.reason, target, context, records, validation, diff, extraction, timings, started_iso,
            options, controls,
        )
        LOG.info("cache: %s", {
            "mode": session.mode, "reason": session.reason, "files": len(records), "temporaries_removed": swept,
            "diff": diff.counts() if diff else None,
            "informational_differences": validation.informational_differences, **timings,
            "extraction_cache": extraction.summary() if extraction else None,
            "extraction_reuse_disabled_reason": extraction.reuse_disabled_reason if extraction else None,
            "controls": controls,
        })
        return session
    except Exception as exc:
        LOG.warning("cache: desactivada para esta corrida (%s: %s)", exc.__class__.__name__, exc)
        return CacheSession()
