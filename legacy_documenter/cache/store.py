"""Safe persistence of the cache (V5.3-R2.4).

Write order (V5.3 R1 section 7): (1) delete the previous manifest, (1b) write the changed extraction shards (R2.5), (2) write `file_state.json` atomically,
(3) re-read it and verify its SHA-256, (4) build the manifest, (5) write `CACHE_MANIFEST.json` LAST. A run
interrupted before step 5 leaves no manifest, so the cache does not exist and the next run is a full one.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

from legacy_documenter.utils.atomic_write import atomic_write_bytes

from .context import CacheContext
from .extraction_shards import EXTRACTION_DIRNAME
from .file_state import FILE_STATE_FILENAME, FileRecord, render_file_state
from .manifest import MANIFEST_FILENAME, build_manifest, render_manifest


class CacheWriteError(RuntimeError):
    """The cache could not be written consistently (never fatal for the run; see `session`)."""


def invalidate_manifest(cache_dir: str | Path) -> None:
    """Removes the manifest so an interrupted run cannot leave a cache that looks valid."""
    try:
        (Path(cache_dir) / MANIFEST_FILENAME).unlink()
    except FileNotFoundError:
        pass


def sweep_temporary_files(cache_dir: str | Path) -> int:
    """Removes orphaned atomic-write temporaries (`.<name>.<random>.tmp`) directly under the cache directory."""
    base = Path(cache_dir)
    removed = 0
    if base.is_dir():
        for path in [*base.glob(".*.tmp"), *(base / EXTRACTION_DIRNAME).glob(".*.tmp")]:
            if path.is_file():
                try:
                    path.unlink()
                    removed += 1
                except OSError:
                    pass
    return removed


def write_cache(cache_dir: str | Path, context: CacheContext, records: Iterable[FileRecord], extraction=None) -> dict:
    """Persists the extraction shards (if any), `file_state.json` and then the manifest; returns the manifest.
    Raises `CacheWriteError`."""
    base = Path(cache_dir)
    if context.analyzer_code_fingerprint.status != "available":
        raise CacheWriteError("fuentes del analizador no disponibles: no se escribe caché")
    records = list(records)
    invalidate_manifest(base)
    extraction_section = extraction.write_shards(base) if extraction is not None else None
    content = render_file_state(records)
    expected = hashlib.sha256(content).hexdigest()
    state_path = base / FILE_STATE_FILENAME
    atomic_write_bytes(state_path, content)
    if hashlib.sha256(state_path.read_bytes()).hexdigest() != expected:
        raise CacheWriteError("file_state.json no coincide con lo escrito")
    manifest = build_manifest(context, expected, len(records), extraction_section)
    atomic_write_bytes(base / MANIFEST_FILENAME, render_manifest(manifest))
    return manifest
