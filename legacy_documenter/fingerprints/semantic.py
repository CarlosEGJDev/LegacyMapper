"""Semantic content hash of analyzed text files (V5.3-R2.3).

SHA-256 of the bytes with CRLF and lone CR turned into LF; nothing else. It never replaces the raw
`SourceArtifact.sha256` (integrity) and exists only for analyzed text types.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from ._common import normalize_newlines


#: `file_type`s that have an extractor (the keys of `extract_repository`'s extractor map; a guard test keeps
#: this set equal to them). Only these get a semantic hash; everything else is raw-hash only.
ANALYZED_FILE_TYPES = frozenset({"solution", "vb_project", "vb_source", "aspx", "ascx", "master", "web_config"})


def semantic_content_sha256(content: bytes, file_type: str) -> str | None:
    """Semantic hash of an analyzed text file, or `None` for any other `file_type` (contract: no semantic hash;
    callers use the raw `SourceArtifact.sha256`, which this never replaces).

    Only CRLF and lone CR become LF. BOM, trailing/other whitespace and encoding bytes are preserved, so a
    BOM or whitespace difference changes the hash. The work is on bytes (no decoding), hence deterministic;
    UTF-16 files are hashed byte-wise too (they simply do not get CRLF/LF equivalence, which only costs a
    re-extraction, never a wrong reuse).
    """
    if file_type not in ANALYZED_FILE_TYPES:
        return None
    return hashlib.sha256(normalize_newlines(content)).hexdigest()


def semantic_file_sha256(path: str | Path, file_type: str) -> str | None:
    """`semantic_content_sha256` of a file on disk (reads it only if its type is analyzed)."""
    if file_type not in ANALYZED_FILE_TYPES:
        return None
    return semantic_content_sha256(Path(path).read_bytes(), file_type)
