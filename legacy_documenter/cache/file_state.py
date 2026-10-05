"""File State (V5.3-R2.4): per-file path/size/hashes/type of the scanned repository, persisted as `file_state.json`.

Holds only relative paths, sizes, hashes, types and mtimes -- never source content, extracted data or secrets.
The raw hash is the SHA-256 of the real bytes (the same value as `SourceArtifact.sha256`); the semantic hash
comes from `fingerprints.semantic_content_sha256` for analyzed types and is `None` otherwise. Each file is read
once for both hashes (analyzed text files in memory, everything else streamed).
"""
from __future__ import annotations

import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from legacy_documenter.fingerprints import ANALYZED_FILE_TYPES, semantic_content_sha256

FILE_STATE_FILENAME = "file_state.json"
FILE_STATE_CONTRACT = "LegacyMapperFileState"
FILE_STATE_SCHEMA_VERSION = "1"
#: Bounded pool for hashing (I/O bound, order-independent, joined before returning).
HASH_WORKERS = 8
_RECORD_KEYS = {"path", "size", "sha256_raw", "sha256_semantic", "file_type", "mtime_ns", "readable"}


@dataclass(frozen=True)
class FileRecord:
    """One scanned file. `readable=False` records carry `None` hashes and never compare as unchanged."""

    path: str
    size: int
    sha256_raw: str | None
    sha256_semantic: str | None
    file_type: str
    mtime_ns: int | None
    readable: bool = True

    def to_dict(self) -> dict:
        """The persisted shape of this record."""
        return {
            "path": self.path, "size": self.size, "sha256_raw": self.sha256_raw,
            "sha256_semantic": self.sha256_semantic, "file_type": self.file_type,
            "mtime_ns": self.mtime_ns, "readable": self.readable,
        }


def normalize_relative_path(relative_path: str) -> str:
    """Relative path with `/` separators."""
    return str(relative_path).replace("\\", "/")


def _record_for(root: Path, relative_path: str, file_type: str, trusted: dict | None = None) -> FileRecord:
    """Stats and hashes one file; any OS error yields an unreadable record instead of raising.

    `trusted` (`--trust-mtime`, V5.3-R2.8) maps path -> previous record of a *valid, compatible* cache: when path,
    type, size and `mtime_ns` all match, that record is returned without reading the file. Anything else is hashed.
    """
    path = normalize_relative_path(relative_path)
    full = root / relative_path
    try:
        stat = os.stat(full)
        previous = trusted.get(path) if trusted else None
        if (
            previous is not None and previous.readable and previous.mtime_ns is not None
            and previous.file_type == file_type and previous.size == stat.st_size and previous.mtime_ns == stat.st_mtime_ns
        ):
            return previous
        if file_type in ANALYZED_FILE_TYPES:
            data = full.read_bytes()
            return FileRecord(path, len(data), hashlib.sha256(data).hexdigest(),
                              semantic_content_sha256(data, file_type), file_type, stat.st_mtime_ns)
        with open(full, "rb") as handle:
            raw = hashlib.file_digest(handle, "sha256").hexdigest()
        return FileRecord(path, stat.st_size, raw, None, file_type, stat.st_mtime_ns)
    except OSError:
        return FileRecord(path, 0, None, None, file_type, None, readable=False)


def build_file_state(
    root: str | Path, files: Iterable, workers: int = HASH_WORKERS, trusted: dict[str, FileRecord] | None = None,
) -> list[FileRecord]:
    """Hashes every scanned file (`files` are scanner `SourceFile`s) and returns records sorted by path.

    `trusted` is the opt-in `--trust-mtime` prefilter (see `_record_for`); `None` (the default) hashes everything.
    """
    base = Path(root)
    items = [(f.relative_path, f.file_type) for f in files]
    if workers <= 1:
        records = [_record_for(base, rel, kind, trusted) for rel, kind in items]
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            records = list(pool.map(lambda item: _record_for(base, item[0], item[1], trusted), items))
    return sorted(records, key=lambda record: record.path)


def render_file_state(records: Iterable[FileRecord]) -> bytes:
    """Canonical `file_state.json` bytes: sorted keys, compact separators, ASCII, records sorted by path."""
    ordered = sorted(records, key=lambda record: record.path)
    payload = {
        "contract": FILE_STATE_CONTRACT,
        "schema_version": FILE_STATE_SCHEMA_VERSION,
        "file_count": len(ordered),
        "files": [record.to_dict() for record in ordered],
    }
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def parse_file_state(raw: bytes) -> list[FileRecord]:
    """Records from `file_state.json` bytes; `ValueError` on anything malformed."""
    try:
        data = json.loads(raw.decode("utf-8"))
        if data["contract"] != FILE_STATE_CONTRACT or data["schema_version"] != FILE_STATE_SCHEMA_VERSION:
            raise ValueError("contrato o schema de file_state no reconocido")
        records = []
        for entry in data["files"]:
            if set(entry) != _RECORD_KEYS:
                raise ValueError("registro de file_state con claves inesperadas")
            records.append(FileRecord(**entry))
        if data["file_count"] != len(records):
            raise ValueError("file_count no coincide")
        return records
    except (KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"file_state inválido: {exc}") from exc
