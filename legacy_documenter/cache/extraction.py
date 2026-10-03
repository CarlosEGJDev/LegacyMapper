"""Per-file extraction cache (V5.3-R2.5): reuse of extractor output for unchanged files.

Scope: ONLY the raw per-file output of the extractors (before `apply_project_namespaces`, partial-class
consolidation and every resolver). The pipeline hands this object to its EXTRACTION stage, which calls
`lookup` (hit -> an independent record parsed from disk, miss -> `None`) and `store` (the freshly extracted
record, serialized immediately, i.e. before any in-place normalization can mutate it). The cache knows nothing
about extractors or resolvers: a record is an opaque JSON-able dict.

Entry key (all must match, none is an mtime): the file's comparison hash (semantic for analyzed types) and its
`file_type`, plus `ANALYZER_VERSION`, the analyzer code fingerprint and the analysis-config fingerprint.

Safety rules:
- Before persisting, a record must (a) survive a JSON round trip unchanged and (b) be unchanged by the
  centralized `sanitize_data`; otherwise the file is `cache_bypass` (never persisted, re-extracted every run).
  A record that depends on something other than the file's bytes (an `OSError`) is bypassed too.
- One invalid shard (missing, checksum mismatch, malformed) only turns its files into misses; more than one
  disables reuse for the whole run. Nothing here ever raises into the pipeline.
- Only shards that changed are rewritten; the manifest (written last by `store.write_cache`) lists each
  shard's SHA-256.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from time import perf_counter

from legacy_documenter.fingerprints import ANALYZED_FILE_TYPES
from legacy_documenter.utils.sanitizer import sanitize_data

from .context import CacheContext
from .diff import _comparison_key
from .extraction_shards import EXTRACTION_DIRNAME, SHARD_COUNT, shard_index
from .extraction_store import SectionInvalid, load_shards, write_changed_shards
from .file_state import FileRecord

LOG = logging.getLogger(__name__)

#: More invalid shards than this and the whole cache is distrusted (contract: one corrupt shard is a partial miss).
MAX_INVALID_SHARDS = 1

_METRIC_KEYS = (
    "extraction_cache_enabled", "extraction_cache_hits", "extraction_cache_misses", "extraction_cache_bypass",
    "shards_loaded", "shards_invalid", "shards_rewritten", "files_reused", "files_extracted",
    "load_seconds", "validate_seconds", "parse_seconds", "assemble_seconds", "extraction_seconds",
    "persist_seconds", "cache_size_bytes",
)


class ExtractionCache:
    """One run's view of the extraction cache: loaded shards, hit/miss decisions and entries to persist."""

    def __init__(self, context: CacheContext, records: list[FileRecord]) -> None:
        self._keys: dict[str, dict] = {}
        for record in records:
            comparison = _comparison_key(record)
            if record.file_type in ANALYZED_FILE_TYPES and comparison is not None:
                self._keys[record.path] = {
                    "file_type": record.file_type, "basis": comparison[0], "hash": comparison[1],
                    "analyzer_version": context.analyzer_version,
                    "analyzer_code_fingerprint": context.analyzer_code_fingerprint.sha256,
                    "analysis_config_fingerprint": context.analysis_config_fingerprint,
                }
        self._analyzed_paths = {r.path for r in records if r.file_type in ANALYZED_FILE_TYPES}
        self._old: dict[int, dict[str, dict]] = {}
        self._old_sha: dict[int, str] = {}
        self._old_count: dict[int, int] = {}
        self._hits: set[str] = set()
        self._dirty: set[int] = set(range(SHARD_COUNT))
        self._new: dict[int, dict[str, str]] = {}
        self.metrics: dict = {key: 0 for key in _METRIC_KEYS}
        self.metrics["extraction_cache_enabled"] = True
        self.metrics.update({k: 0.0 for k in _METRIC_KEYS if k.endswith("_seconds")})
        self.reuse_disabled_reason: str | None = None

    def load(self, cache_dir: str | Path, manifest: dict) -> None:
        """Loads and validates the shards listed by a (validated) manifest. Never raises; on trouble, reuse is off."""
        try:
            self._load(Path(cache_dir) / EXTRACTION_DIRNAME, manifest.get("extraction"))
        except Exception as exc:
            LOG.warning("cache: extracción persistida no utilizable (%s: %s); se extrae todo", exc.__class__.__name__, exc)
            self._reset_reuse("LOAD_ERROR")

    def _reset_reuse(self, reason: str) -> None:
        self._old.clear()
        self._old_sha.clear()
        self._old_count.clear()
        self._hits.clear()
        self._dirty = set(range(SHARD_COUNT))
        self.reuse_disabled_reason = reason

    def _load(self, directory: Path, section) -> None:
        try:
            entries, checksums, invalid = load_shards(directory, section, self.metrics)
        except SectionInvalid as exc:
            self._reset_reuse(str(exc))
            return
        self.metrics["shards_invalid"] = len(invalid)
        if len(invalid) > MAX_INVALID_SHARDS:
            self._reset_reuse("MULTIPLE_SHARDS_INVALID")
            return
        self._old, self._old_sha = entries, checksums
        self._old_count = {index: len(shard) for index, shard in entries.items()}
        self._plan(invalid)

    def _plan(self, invalid: list[int]) -> None:
        """Decides hits up front and which shards will differ from disk (their reused entries get re-serialized)."""
        dirty = set(invalid)
        for path in self._analyzed_paths:
            index = shard_index(path)
            entry = self._old.get(index, {}).get(path)
            if entry is not None and path in self._keys and entry["key"] == self._keys[path]:
                self._hits.add(path)
            else:
                dirty.add(index)
        for index, entries in self._old.items():
            if any(path not in self._analyzed_paths for path in entries):  # deleted/renamed/retyped files: purge
                dirty.add(index)
        self._dirty = dirty | (set(range(SHARD_COUNT)) - set(self._old))

    def lookup(self, relative_path: str) -> dict | None:
        """The cached record of an unchanged file (independent of anything kept here), or `None` (miss)."""
        started = perf_counter()
        try:
            path = relative_path.replace("\\", "/")
            if path not in self._hits:
                self.metrics["extraction_cache_misses"] += 1
                return None
            index = shard_index(path)
            entry = self._old[index].pop(path)
            if index in self._dirty:
                self._new.setdefault(index, {})[path] = _render_entry(entry)
            self.metrics["extraction_cache_hits"] += 1
            self.metrics["files_reused"] += 1
            return entry["record"]
        except Exception as exc:
            LOG.warning("cache: lookup falló para %s (%s); se extrae", relative_path, exc.__class__.__name__)
            self.metrics["extraction_cache_misses"] += 1
            return None
        finally:
            self.metrics["assemble_seconds"] += perf_counter() - started

    def store(self, relative_path: str, record: dict, cacheable: bool = True) -> None:
        """Serializes a freshly extracted record now (before any normalization mutates it), or marks `cache_bypass`."""
        self.metrics["files_extracted"] += 1
        started = perf_counter()
        try:
            path = relative_path.replace("\\", "/")
            key = self._keys.get(path)
            if key is None:
                return
            text = _persistable_entry_text(key, record) if cacheable else None
            if text is None:
                self.metrics["extraction_cache_bypass"] += 1
                return
            self._new.setdefault(shard_index(path), {})[path] = text
        except Exception as exc:
            LOG.warning("cache: no se pudo preparar %s (%s); se omite", relative_path, exc.__class__.__name__)
            self.metrics["extraction_cache_bypass"] += 1
        finally:
            self.metrics["persist_seconds"] += perf_counter() - started

    def record_extraction_seconds(self, seconds: float) -> None:
        """Wall time the pipeline spent extracting the misses (reported with the other metrics)."""
        self.metrics["extraction_seconds"] = round(seconds, 3)

    def write_shards(self, cache_dir: str | Path) -> dict:
        """Writes the shards that changed, removes stale ones and returns the manifest's `extraction` section."""
        started = perf_counter()
        section = write_changed_shards(
            Path(cache_dir) / EXTRACTION_DIRNAME, self._new, self._dirty, self._old_sha, self._old_count, self.metrics,
        )
        self.metrics["persist_seconds"] = round(self.metrics["persist_seconds"] + perf_counter() - started, 3)
        return section

    def release(self) -> None:
        """Drops everything held in memory (serialized entries and parsed shards)."""
        self._old.clear()
        self._new.clear()
        self._hits.clear()

    def summary(self) -> dict:
        """Metrics rounded for logging."""
        return {key: (round(value, 3) if isinstance(value, float) else value) for key, value in self.metrics.items()}


def _render_entry(entry: dict) -> str:
    return json.dumps(entry, separators=(",", ":"), ensure_ascii=True)


def _persistable_entry_text(key: dict, record: dict) -> str | None:
    """Canonical entry text, or `None` if the record would not be reproduced exactly or is changed by sanitizing."""
    text = _render_entry({"key": key, "record": record})
    if json.loads(text)["record"] != record:
        return None
    if sanitize_data(record) != record:
        return None
    return text
