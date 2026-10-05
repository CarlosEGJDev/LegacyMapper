"""Strict cache verification, `--verify-cache=hash` (V5.3-R2.8).

The normal (`fast`) validation already checks the manifest, the `file_state.json` checksum, the versions, the repository
identity and the config fingerprint, and *tolerates* one damaged extraction shard (that shard is simply re-extracted).
`hash` is the diagnostic/strict level: it re-reads and re-hashes every shard the manifest lists -- whether or not this
run would use it -- and refuses the whole cache on any inconsistency, so the run is a safe full one that rebuilds it.
It never repairs anything and never raises for a bad cache.
"""
from __future__ import annotations

from pathlib import Path

from .extraction_shards import EXTRACTION_DIRNAME, SHARD_COUNT, shard_filename
from .extraction_store import load_shard

VERIFY_FAILED = "VERIFY_CACHE_FAILED"


def _scratch() -> dict:
    return {"load_seconds": 0.0, "validate_seconds": 0.0, "parse_seconds": 0.0, "cache_size_bytes": 0}


def verify_cache_deep(cache_dir: str | Path, manifest: dict, records: list) -> str | None:
    """`None` if the persisted cache is fully consistent, else a short failure code (the first one found)."""
    paths = [record.path for record in records]
    if len(set(paths)) != len(paths):
        return "FILE_STATE_DUPLICATE_PATHS"
    if any(p.startswith("/") or ":" in p or ".." in p.split("/") for p in paths):
        return "FILE_STATE_UNSAFE_PATH"
    section = manifest.get("extraction")
    if section is None:
        return None  # extraction cache was not enabled when this cache was written: nothing more to verify
    directory = Path(cache_dir) / EXTRACTION_DIRNAME
    listed = section.get("shards") if isinstance(section, dict) else None
    if not isinstance(listed, dict) or section.get("shard_count") != SHARD_COUNT:
        return "EXTRACTION_SECTION_INVALID"
    entry_total = 0
    scratch = _scratch()
    for name, expected in sorted(listed.items()):
        try:
            index = int(name)
        except ValueError:
            return "EXTRACTION_SECTION_INVALID"
        entries = load_shard(directory, index, expected, scratch) if 0 <= index < SHARD_COUNT and isinstance(expected, str) else None
        if entries is None:
            return f"SHARD_INVALID:{index:03d}"
        entry_total += len(entries)
    if entry_total != section.get("entry_count"):
        return "ENTRY_COUNT_MISMATCH"
    if directory.is_dir():
        known = {shard_filename(int(name)) for name in listed}
        if any(path.name not in known for path in directory.glob("ex-*.json")):
            return "UNLISTED_SHARD_FILE"
    return None
