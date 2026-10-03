"""Deterministic sharding and canonical JSON of the per-file extraction cache (V5.3-R2.5).

Pure data: no knowledge of extractors, pipeline or sanitization. A file's shard is a function of its normalized
relative path only (SHA-256 prefix modulo `SHARD_COUNT`), so it is stable across runs and machines and a change
to one file touches one shard. A shard is `{"contract","schema_version","shard","entries":{path: entry}}`,
entries sorted by path, compact separators, ASCII. Entry bodies are rendered by the caller with insertion order
preserved on purpose: the record's key order is part of the extractor's output and must survive a round trip.
"""
from __future__ import annotations

import hashlib
import json

EXTRACTION_DIRNAME = "extraction"
SHARD_COUNT = 256
SHARD_CONTRACT = "LegacyMapperExtractionShard"
SHARD_SCHEMA_VERSION = "1"


def shard_index(normalized_path: str, shard_count: int = SHARD_COUNT) -> int:
    """Stable shard of a normalized relative path."""
    return int.from_bytes(hashlib.sha256(normalized_path.encode("utf-8")).digest()[:4], "big") % shard_count


def shard_filename(index: int) -> str:
    """`ex-000.json` ... `ex-255.json`."""
    return f"ex-{index:03d}.json"


def render_shard(index: int, entry_texts: dict[str, str]) -> bytes:
    """Canonical shard bytes from already-rendered (ASCII, compact) entry JSON texts, sorted by path."""
    body = ",".join(f"{json.dumps(path, ensure_ascii=True)}:{entry_texts[path]}" for path in sorted(entry_texts))
    head = f'{{"contract":"{SHARD_CONTRACT}","schema_version":"{SHARD_SCHEMA_VERSION}","shard":{index},"entries":{{'
    return f"{head}{body}}}}}\n".encode("ascii")


def parse_shard(raw: bytes, index: int, shard_count: int = SHARD_COUNT) -> dict[str, dict]:
    """Entries (`path -> {"key","record"}`) of a shard; `ValueError` on anything malformed or misplaced."""
    try:
        data = json.loads(raw.decode("utf-8"))
        if data["contract"] != SHARD_CONTRACT or data["schema_version"] != SHARD_SCHEMA_VERSION or data["shard"] != index:
            raise ValueError("contrato, schema o índice de shard no reconocido")
        entries = data["entries"]
        if not isinstance(entries, dict):
            raise ValueError("entries no es un objeto")
        for path, entry in entries.items():
            if shard_index(path, shard_count) != index:
                raise ValueError("entrada en el shard equivocado")
            if not isinstance(entry, dict) or set(entry) != {"key", "record"} or not isinstance(entry["key"], dict):
                raise ValueError("entrada malformada")
        return entries
    except (KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"shard inválido: {exc}") from exc
