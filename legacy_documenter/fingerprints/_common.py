"""Shared primitives of the fingerprint modules (V5.3-R2.3): algorithm tag, canonical JSON, record framing."""
from __future__ import annotations

import hashlib
import json

#: Bump when the *algorithm* of a fingerprint changes (it is mixed into the hash).
FINGERPRINT_ALGORITHM = "v1"


def length_prefixed(label: str, content: bytes) -> bytes:
    """One hash record; the length prefixes make concatenations of records unambiguous."""
    name = label.encode("utf-8")
    return b"%d:" % len(name) + name + b"%d:" % len(content) + content


def normalize_newlines(data: bytes) -> bytes:
    """CRLF and lone CR become LF; nothing else changes."""
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def canonical_json(value: object) -> str:
    """Deterministic JSON text: sorted keys, compact separators, ASCII only."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_json(kind: str, payload: dict) -> str:
    """SHA-256 of the canonical JSON of `payload`, tagged with the fingerprint kind and algorithm."""
    body = canonical_json({"kind": kind, "algorithm": FINGERPRINT_ALGORITHM, **payload})
    return hashlib.sha256(body.encode("ascii")).hexdigest()
