"""Deterministic manifest of everything a run wrote under `--output` (V4.3-R7).

Enumerates every file already on disk under `output_dir` (excluding this
manifest's own filename, in case a stale one from an earlier run is still
present) with its path relative to `output_dir`, size in bytes, and
SHA-256 -- so a Technical Lead or an external pilot operator can verify
exactly what one run produced, and detect any accidental modification
after the fact, without re-running LegacyMapper or diffing directories by
hand.

Pure filesystem enumeration: this module never inspects file content beyond
hashing it, never sanitizes (every listed file was already sanitized by its
own writer -- `legacy_documenter.utils.sanitize_data`/`sanitize_text` -- when
it was first written), and never orders by filesystem enumeration order
(always sorted by relative path, so the manifest itself is byte-identical
across two enumerations of the same unchanged tree, on any OS).

Deliberately NOT wired into `legacy_documenter.cli.full_pipeline
.run_full_pipeline` automatically: `run_full_pipeline`'s stage contract
(`StageId`, `RunResult`) is already stable and heavily tested (V4.2-R1
onward); this is an explicit, opt-in post-run step instead (see
`tools/v4_3_r7_build_output_manifest.py` and
`docs/V4_3/V4_3_REAL_PILOT_INSTRUCTIONS.md`), so it can be produced (or
skipped) without touching that contract.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

SCHEMA_VERSION = "1.0"
CONTRACT_NAME = "LegacyMapperOutputManifest"
MANIFEST_FILENAME = "OUTPUT_MANIFEST.json"


def build_output_manifest(output_dir: str | Path) -> dict:
    """Builds the manifest for every file currently under `output_dir`.

    Raises `FileNotFoundError` if `output_dir` does not exist or is not a
    directory -- never silently reports an empty manifest for a run that
    never happened.
    """
    root = Path(output_dir)
    if not root.is_dir():
        raise FileNotFoundError(root)
    entries: list[dict] = []
    total_bytes = 0
    for path in sorted(
        (p for p in root.rglob("*") if p.is_file() and p.name != MANIFEST_FILENAME),
        key=lambda p: p.relative_to(root).as_posix(),
    ):
        size = path.stat().st_size
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append({"path": path.relative_to(root).as_posix(), "size_bytes": size, "sha256": digest})
        total_bytes += size
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_name": CONTRACT_NAME,
        "file_count": len(entries),
        "total_bytes": total_bytes,
        "files": entries,
    }
