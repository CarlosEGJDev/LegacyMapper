"""`RUN_METRICS.json` (V5.3-R2.7, R1 section 13): persisted observability of one run.

Lives in the cache directory next to the manifest but is NOT part of it: it is not listed in
`CACHE_MANIFEST.json`, no checksum covers it, nothing reads it at run time (a corrupt, missing or stale file changes
no decision and is simply overwritten by the next run) and it is excluded from every product comparison. It is
deliberately non-deterministic (timestamps, seconds); only its *structure* is stable and tested.

Holds counters, seconds, relative paths and reason codes -- never source content or symbol payloads; the final
document goes through the centralized sanitizer anyway.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from legacy_documenter.utils.atomic_write import atomic_write_bytes
from legacy_documenter.utils.sanitizer import sanitize_data

from .context import CacheContext

METRICS_FILENAME = "RUN_METRICS.json"
METRICS_CONTRACT = "LegacyMapperRunMetrics"
METRICS_SCHEMA_VERSION = "1"
#: Every top-level key of a metrics document, in the order they are documented.
TOP_LEVEL_KEYS = (
    "contract", "schema_version", "mode", "session_mode", "fallback_reason", "started_at", "completed_at",
    "total_seconds", "final_status", "file_state", "extraction_cache", "stage_seconds", "extraction_postprocess_seconds",
    "write_skip", "hydration", "scope", "versions", "cache_controls", "cache_verification", "peak_memory_bytes", "overhead_seconds",
)
#: R1 vocabulary for `mode`; the internal cold/warm/fallback_full stays in `session_mode`.
_R1_MODE = {"cold": "full", "fallback_full": "full", "warm": "incremental", "refresh": "refresh", "off": "off"}


def now_iso() -> str:
    """UTC timestamp, second precision."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def peak_memory_bytes() -> int | None:
    """Peak resident memory of this process, or `None` if the platform offers no standard way (R1 section 13)."""
    try:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes

            class Counters(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD), ("PeakWorkingSetSize", ctypes.c_size_t)]
                _fields_ += [(name, ctypes.c_size_t) for name in (
                    "WorkingSetSize", "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                    "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]

            kernel, psapi = ctypes.WinDLL("kernel32"), ctypes.WinDLL("psapi")
            kernel.GetCurrentProcess.restype = wintypes.HANDLE
            psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
            info = Counters()
            info.cb = ctypes.sizeof(info)
            ok = psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(info), info.cb)
            return int(info.PeakWorkingSetSize) if ok else None
        import resource

        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(peak if sys.platform == "darwin" else peak * 1024)
    except Exception:  # observability must never fail a run
        return None


def build_run_metrics(
    *, session_mode: str, fallback_reason: str | None, context: CacheContext, started_at: str, total_seconds: float,
    final_status: str, file_count: int, diff_counts: dict | None, timings: dict, extraction: dict | None,
    reuse_disabled_reason: str | None, stage_snapshot: dict, write_skip: dict, scope: dict, overhead_seconds: dict,
    cache_controls: dict | None = None,
) -> dict:
    """Assembles the metrics document (see `TOP_LEVEL_KEYS`); every section is plain JSON-able data."""
    stage_seconds = dict(stage_snapshot.get("stage_seconds", {}))
    postprocess = None
    if extraction and "EXTRACTION" in stage_seconds:  # assembly + namespace/partial normalization, derived
        in_loop = extraction.get("assemble_seconds", 0.0) + extraction.get("extraction_seconds", 0.0)
        postprocess = round(max(stage_seconds["EXTRACTION"] - in_loop, 0.0), 3)
    counts = diff_counts or {}
    document = {
        "contract": METRICS_CONTRACT,
        "schema_version": METRICS_SCHEMA_VERSION,
        "mode": _R1_MODE.get(session_mode, session_mode),
        "session_mode": session_mode,
        "fallback_reason": fallback_reason,
        "started_at": started_at,
        "completed_at": now_iso(),
        "total_seconds": round(total_seconds, 3),
        "final_status": final_status,
        "file_state": {
            "files_total": file_count,
            "unchanged": counts.get("unchanged"), "modified": counts.get("modified"), "added": counts.get("added"),
            "deleted": counts.get("deleted"), "renamed_candidates": counts.get("renamed_candidates"),
            "line_ending_only": counts.get("line_ending_only"),
            "validate_seconds": timings.get("validate_seconds"),
            "file_state_build_seconds": timings.get("file_state_build_seconds"),
            "diff_seconds": timings.get("diff_seconds"),
        },
        "extraction_cache": {**(extraction or {}), "reuse_disabled_reason": reuse_disabled_reason} if extraction is not None else None,
        "stage_seconds": stage_seconds,
        "extraction_postprocess_seconds": postprocess,
        "write_skip": write_skip,
        "hydration": stage_snapshot.get("extras", {}).get("hydration"),
        "scope": scope,
        "versions": {
            "analyzer_version": context.analyzer_version,
            "analyzer_code_fingerprint": context.analyzer_code_fingerprint.sha256,
            "extraction_cache_schema_version": context.extraction_cache_schema_version,
            "evidence_schema_version": context.evidence_schema_version,
            "renderer_versions": context.renderer_versions,
            "template_profile_fingerprint": context.template_profile_fingerprint,
            "analysis_config_fingerprint": context.analysis_config_fingerprint,
        },
        "cache_controls": cache_controls,
        "cache_verification": "byte_compare",
        "peak_memory_bytes": peak_memory_bytes(),
        "overhead_seconds": overhead_seconds,
    }
    return sanitize_data(document)


def render_run_metrics(document: dict) -> bytes:
    """Canonical bytes (sorted keys, ASCII, LF)."""
    return (json.dumps(document, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def write_run_metrics(cache_dir: str | Path, document: dict) -> Path:
    """Atomically writes `RUN_METRICS.json` into `cache_dir` (created if needed) and returns its path."""
    target = Path(cache_dir) / METRICS_FILENAME
    atomic_write_bytes(target, render_run_metrics(document))
    return target


def read_run_metrics(cache_dir: str | Path) -> dict | None:
    """Diagnostic reader: the document, or `None` if missing/corrupt/foreign. The pipeline never calls it."""
    try:
        document = json.loads((Path(cache_dir) / METRICS_FILENAME).read_bytes().decode("utf-8"))
    except (OSError, ValueError):
        return None
    return document if isinstance(document, dict) and document.get("contract") == METRICS_CONTRACT else None
