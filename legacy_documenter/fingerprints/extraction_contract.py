"""Guardian fingerprint of the extraction-cache persisted contract (V5.3-R2.6).

The extraction cache has its own contract (shard format, entry structure, entry key, `cache_bypass` rules,
loading/validation/writing), versioned by `versions.EXTRACTION_CACHE_SCHEMA_VERSION` -- deliberately separate
from `ANALYZER_VERSION`/`analyzer_code_fingerprint` (what extraction *produces*) and from the manifest schema.

This fingerprint is the SHA-256 of the *normalized syntax trees* of the modules that define that contract:
comments, blank lines, formatting and docstrings do not change it; any change to executable code does
(conservative strategy: it cannot tell a logging tweak from a format change, so a human decides). It is not
consumed by the runtime cache -- the runtime compares `EXTRACTION_CACHE_SCHEMA_VERSION`; a guard test compares
this fingerprint with the value recorded next to that version and fails when the contract code changed
without the version being reviewed.
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

from ._common import FINGERPRINT_ALGORITHM, length_prefixed

#: Package-relative modules whose executable code defines the persisted contract.
EXTRACTION_CONTRACT_FILES = ("cache/extraction.py", "cache/extraction_shards.py", "cache/extraction_store.py")


def _strip_docstrings(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                node.body = body[1:] or [ast.Pass()]


def extraction_contract_fingerprint(package_root: str | Path | None = None) -> str | None:
    """Hex digest of the normalized contract modules, or `None` if any is unreadable/unparsable."""
    root = Path(package_root) if package_root is not None else Path(__file__).resolve().parents[1]
    digest = hashlib.sha256(f"EXTRACTION_CONTRACT_FINGERPRINT/{FINGERPRINT_ALGORITHM}\n".encode("ascii"))
    try:
        for relative in sorted(EXTRACTION_CONTRACT_FILES):
            tree = ast.parse((root / relative).read_bytes().decode("utf-8"))
            _strip_docstrings(tree)
            digest.update(length_prefixed(relative, ast.dump(tree, annotate_fields=True, include_attributes=False).encode("utf-8")))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None
    return digest.hexdigest()
