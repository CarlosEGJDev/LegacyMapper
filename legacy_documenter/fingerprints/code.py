"""Analyzer code fingerprint (V5.3-R2.3): SHA-256 of the sources that govern the analysis.

Sorted `(label, content)` records; sources use LF newlines so a checkout's line-ending conversion does not
change it; labels are package-relative POSIX paths. Reads no docs, prompts, tests, Git state or timestamps.
"""
from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from ._common import FINGERPRINT_ALGORITHM, length_prefixed, normalize_newlines


#: Package-relative directories whose every `*.py` file governs the analysis.
ANALYZER_CODE_DIRECTORIES = ("extractors", "analysis", "scanner", "models", "adapters")
#: Package-relative single files that govern the analysis.
ANALYZER_CODE_FILES = ("utils/sanitizer.py", "config.py", "evidence/bundle.py")
#: Only these functions of `cli/pipeline_stages.py` (extraction/normalization/resolution orchestration) are
#: fingerprinted -- the rest of that module is rendering/writing and must not invalidate an extraction.
PIPELINE_STAGES_FILE = "cli/pipeline_stages.py"
PIPELINE_STAGES_FUNCTIONS = (
    "scan_repository", "extract_repository", "_extractors", "_primary_value", "_extract_file", "apply_project_namespaces",
    "consolidate_partial_symbols", "_norm_path", "resolve_calls", "resolve_web_entries", "resolve_database",
    "resolve_flows", "resolve_dependencies",
)

AVAILABLE = "available"
UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class CodeFingerprint:
    """`status == "available"` carries `sha256`; otherwise the future cache must NOT reuse extraction."""

    status: str
    sha256: str | None
    file_count: int
    reason: str | None = None


def _package_root() -> Path:
    """The `legacy_documenter` package directory this module belongs to."""
    return Path(__file__).resolve().parents[1]


def _function_segments(source_path: Path, names: Iterable[str]) -> dict[str, bytes]:
    """Source text (LF newlines) of the named top-level functions; `LookupError` if any is missing."""
    text = normalize_newlines(source_path.read_bytes()).decode("utf-8")
    tree = ast.parse(text)
    wanted = set(names)
    found: dict[str, bytes] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in wanted:
            segment = ast.get_source_segment(text, node)
            if segment is not None:
                found[node.name] = segment.encode("utf-8")
    missing = wanted - set(found)
    if missing:
        raise LookupError(f"funciones no encontradas en {source_path.name}: {sorted(missing)}")
    return found


def analyzer_code_fingerprint(package_root: str | Path | None = None) -> CodeFingerprint:
    """SHA-256 of the sources that govern the analysis, or an explicit `unavailable` status.

    Included: `ANALYZER_CODE_DIRECTORIES` (all `*.py`), `ANALYZER_CODE_FILES` and the
    `PIPELINE_STAGES_FUNCTIONS` source segments. Any unreadable/missing/pyc-only source yields
    `unavailable` (never a partial hash).
    """
    root = Path(package_root) if package_root is not None else _package_root()
    try:
        records: dict[str, bytes] = {}
        for directory in ANALYZER_CODE_DIRECTORIES:
            files = sorted(p for p in (root / directory).rglob("*.py") if p.is_file())
            if not files:
                return CodeFingerprint(UNAVAILABLE, None, 0, f"sin fuentes .py en {directory}/")
            for path in files:
                records[path.relative_to(root).as_posix()] = normalize_newlines(path.read_bytes())
        for relative in ANALYZER_CODE_FILES:
            records[relative] = normalize_newlines((root / relative).read_bytes())
        for name, segment in _function_segments(root / PIPELINE_STAGES_FILE, PIPELINE_STAGES_FUNCTIONS).items():
            records[f"{PIPELINE_STAGES_FILE}::{name}"] = segment
    except (OSError, SyntaxError, UnicodeDecodeError, LookupError) as exc:
        return CodeFingerprint(UNAVAILABLE, None, 0, f"{exc.__class__.__name__}: {exc}")
    digest = hashlib.sha256(f"ANALYZER_CODE_FINGERPRINT/{FINGERPRINT_ALGORITHM}\n".encode("ascii"))
    for label in sorted(records):
        digest.update(length_prefixed(label, records[label]))
    return CodeFingerprint(AVAILABLE, digest.hexdigest(), len(records))
