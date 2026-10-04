"""Disk side of the extraction cache (V5.3-R2.5): validated shard loading and changed-shard writing.

Kept apart from `extraction` (keys, hit/miss, serialization policy) so each module has one responsibility.
Functions take the run's `metrics` dict and add their timings/counters to it; nothing here decides what a
hit is.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from time import perf_counter

from legacy_documenter.utils.atomic_write import atomic_write_bytes

from .extraction_shards import SHARD_COUNT, parse_shard, render_shard, shard_filename


class SectionInvalid(ValueError):
    """The manifest's `extraction` section is not something this version can read."""


def schema_incompatibility(manifest: dict, expected: int) -> str | None:
    """Why the manifest's extraction cache cannot be reused for the current contract version, or `None`."""
    found = manifest.get("versions", {}).get("extraction_cache_schema_version")
    if found is None:
        return "EXTRACTION_CACHE_SCHEMA_MISSING"
    return None if found == expected else "EXTRACTION_CACHE_SCHEMA_MISMATCH"


def load_shard(directory: Path, index: int, expected_sha: str, metrics: dict) -> dict[str, dict] | None:
    """Entries of one shard, or `None` if it is missing, fails its checksum or is malformed."""
    started = perf_counter()
    try:
        raw = (directory / shard_filename(index)).read_bytes()
    except OSError:
        return None
    finally:
        metrics["load_seconds"] += perf_counter() - started
    started = perf_counter()
    checksum_ok = hashlib.sha256(raw).hexdigest() == expected_sha
    metrics["validate_seconds"] += perf_counter() - started
    if not checksum_ok:
        return None
    started = perf_counter()
    try:
        return parse_shard(raw, index)
    except ValueError:
        return None
    finally:
        metrics["parse_seconds"] += perf_counter() - started
        metrics["cache_size_bytes"] += len(raw)


def load_shards(directory: Path, section, metrics: dict) -> tuple[dict[int, dict[str, dict]], dict[int, str], list[int]]:
    """`(entries per valid shard, checksum per valid shard, indexes of invalid shards)` listed by the manifest.

    Raises `SectionInvalid` if the section itself is unusable (wrong shard count/shape, bad indexes).
    """
    if not isinstance(section, dict):
        raise SectionInvalid("NO_EXTRACTION_CACHE")
    listed = section.get("shards")
    if section.get("shard_count") != SHARD_COUNT or not isinstance(listed, dict):
        raise SectionInvalid("EXTRACTION_SECTION_INVALID")
    entries: dict[int, dict[str, dict]] = {}
    checksums: dict[int, str] = {}
    invalid: list[int] = []
    for name, expected in sorted(listed.items()):
        try:
            index = int(name)
        except ValueError:
            raise SectionInvalid("EXTRACTION_SECTION_INVALID") from None
        if not 0 <= index < SHARD_COUNT or not isinstance(expected, str):
            raise SectionInvalid("EXTRACTION_SECTION_INVALID")
        loaded = load_shard(directory, index, expected, metrics)
        if loaded is None:
            invalid.append(index)
        else:
            entries[index], checksums[index] = loaded, expected
            metrics["shards_loaded"] += 1
    return entries, checksums, invalid


def write_changed_shards(
    directory: Path, new_entries: dict[int, dict[str, str]], dirty: set[int], old_sha: dict[int, str],
    old_count: dict[int, int], metrics: dict,
) -> dict:
    """Writes only the shards whose bytes changed, removes stale ones and returns the manifest section."""
    shards: dict[str, str] = {}
    entry_count = rewritten = size = 0
    for index in range(SHARD_COUNT):
        target = directory / shard_filename(index)
        if index not in dirty and index in old_sha:
            shards[f"{index:03d}"] = old_sha[index]
            entry_count += old_count[index]
            size += _size(target)
            continue
        entries = new_entries.get(index, {})
        if not entries:
            _remove(target)
            continue
        content = render_shard(index, entries)
        digest = hashlib.sha256(content).hexdigest()
        if old_sha.get(index) != digest:
            atomic_write_bytes(target, content)
            rewritten += 1
        shards[f"{index:03d}"] = digest
        entry_count += len(entries)
        size += len(content)
    _remove_unlisted(directory, shards)
    metrics["shards_rewritten"] = rewritten
    metrics["cache_size_bytes"] = size
    return {"shard_count": SHARD_COUNT, "entry_count": entry_count, "shards": shards}


def _remove_unlisted(directory: Path, listed: dict[str, str]) -> None:
    """Deletes shard files that do not belong to the new cache (e.g. left by a previous incompatible one)."""
    if not directory.is_dir():
        return
    keep = {shard_filename(int(name)) for name in listed}
    for path in directory.glob("ex-*.json"):
        if path.name not in keep:
            _remove(path)


def _size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _remove(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass
