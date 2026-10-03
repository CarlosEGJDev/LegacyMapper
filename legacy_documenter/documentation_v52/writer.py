"""V5.3-R2.2.1 persistence phase of `documentation_v52` (extracted verbatim from `engine.py`).

Everything that touches the disk lives here: strict-content verification, write-skip, atomic
document writes, orphan/empty-directory cleanup, the final `MANIFEST.json` and the write counters.
Render, templates and configuration stay in `engine.py`; this module does not import it, not even for typing
(single dependency direction: `engine` -> `writer`; `result` is a `DocumentationV52Result`).
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import perf_counter
from typing import Any

from legacy_documenter.utils.atomic_write import _replace_with_retry
from legacy_documenter.utils.path_limits import check_output_paths

MANIFEST_FILENAME = "MANIFEST.json"
MANIFEST_CONTRACT = "LegacyMapperDocumentationV52"
#: How an existing document is proven identical before skipping its write (V5.3-R2.2): its bytes
#: are compared with the bytes about to be written. Never `size`/`mtime` alone, never the old manifest alone.
VERIFICATION_MODE = "strict_content"
#: Bounded pool for the content verification (I/O bound, order-independent, joined before returning).
VERIFY_WORKERS = 8


def _atomic_write(path: Path, text: str) -> None:
    """Crash-safe write of exact UTF-8 bytes with LF newlines on every platform
    (the manifest hashes these bytes; `atomic_write_text` would translate `\n` on Windows)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(text.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        _replace_with_retry(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _load_previous_manifest(root: Path) -> tuple[str, dict[str, str]]:
    """The previous run's `{path: sha256}` and its status (`valid`/`absent`/`corrupt`).

    Used only to *classify* what changed for the counters; correctness of a skipped write never
    depends on it (see `_verify_existing`).
    """
    path = root / MANIFEST_FILENAME
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return "absent", {}
    except OSError:
        return "corrupt", {}
    try:
        manifest = json.loads(raw.decode("utf-8"))
        if not isinstance(manifest, dict) or manifest.get("contract") != MANIFEST_CONTRACT:
            return "corrupt", {}
        entries = {}
        for entry in manifest["files"]:
            entries[entry["path"]] = entry["sha256"]
        return "valid", entries
    except (ValueError, KeyError, TypeError):
        return "corrupt", {}


def _verify_existing(root: Path, expected: dict[str, bytes], workers: int) -> dict[str, str]:
    """Proves, per document, whether the file on disk already holds exactly the expected bytes.

    `match` only when the file exists, has the expected size and its content is byte-for-byte equal
    to what would be written. `missing` when it does not exist; `different` for anything else
    (other size, other bytes, unreadable, not a regular file) -- all of which are rewritten.
    The check is order-independent, so a bounded thread pool gives the same result as a loop.
    """
    def check(relative: str) -> str:
        path = root / relative
        try:
            size = os.stat(path).st_size
        except (FileNotFoundError, NotADirectoryError):
            return "missing"
        except OSError:
            return "different"
        if size != len(expected[relative]):
            return "different"
        try:
            return "match" if path.read_bytes() == expected[relative] else "different"
        except OSError:
            return "different"

    relatives = sorted(expected)
    if workers <= 1:
        return {relative: check(relative) for relative in relatives}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return dict(zip(relatives, pool.map(check, relatives)))


def _prune_orphans(root: Path, wanted: set[str]) -> int:
    """Removes `.md` files under `root` that this run no longer produces; returns how many."""
    removed = 0
    for existing in sorted(root.rglob("*.md")):
        if existing.relative_to(root).as_posix() not in wanted:
            existing.unlink()
            removed += 1
    return removed


def _prune_empty_directories(root: Path, files: dict[str, str]) -> None:
    """Prunes directories left empty (children first).

    A directory that holds an expected document can never be empty, so trying `rmdir` on it only
    produced a failing syscall per directory (about 20 s on IST); only directories outside the
    expected set are tried -- the same directories the former blanket sweep could actually remove.
    """
    expected_dirs = {""}
    for relative in files:
        parts = relative.split("/")[:-1]
        expected_dirs.update("/".join(parts[:depth]) for depth in range(1, len(parts) + 1))
    for dirpath, _dirnames, _filenames in os.walk(root, topdown=False):
        if os.path.relpath(dirpath, root).replace(os.sep, "/") in expected_dirs or dirpath == str(root):
            continue
        try:
            os.rmdir(dirpath)
        except OSError:
            pass


def _write_documents(
    root: Path, files: dict[str, str], raw_by_path: dict[str, bytes], digest_by_path: dict[str, str],
    statuses: dict[str, str],
) -> tuple[list[dict], int, int]:
    """Writes only the documents not already identical on disk; returns (manifest entries, written, skipped)."""
    manifest_files = []
    written = skipped = 0
    for relative in sorted(files):
        if statuses[relative] == "match":
            skipped += 1
        else:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write(target, files[relative])
            written += 1
        manifest_files.append(
            {"path": relative, "size_bytes": len(raw_by_path[relative]), "sha256": digest_by_path[relative]}
        )
    return manifest_files, written, skipped


def _write_manifest(root: Path, result: Any, manifest_files: list[dict]) -> None:
    """Builds `MANIFEST.json` from the current output only (never from the disk state) and writes it."""
    manifest = {
        "schema_version": "1.0",
        "contract": MANIFEST_CONTRACT,
        "profiles": result.profiles,
        "file_count": len(manifest_files),
        "total_bytes": sum(e["size_bytes"] for e in manifest_files),
        "warnings": result.warnings,
        "gaps": result.gaps,
        "files": manifest_files,
    }
    _atomic_write(root / MANIFEST_FILENAME, json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _write_counters(
    files: dict[str, str], digest_by_path: dict[str, str], statuses: dict[str, str],
    previous: dict[str, str], written: int, skipped: int,
) -> dict:
    """The document counters of one write phase (in-memory characterization, never persisted)."""
    missing = sum(1 for status in statuses.values() if status == "missing")
    return {
        "documents_total": len(files),
        "documents_written": written,
        "documents_skipped_write": skipped,
        "documents_missing": missing,
        "documents_changed": written - missing,
        "documents_verified": sum(1 for status in statuses.values() if status != "missing"),
        "documents_changed_vs_previous_manifest": sum(1 for r in files if previous.get(r) != digest_by_path[r]),
        "documents_disk_mismatch_with_same_previous_manifest": sum(
            1 for r in files if statuses[r] == "different" and previous.get(r) == digest_by_path[r]
        ),
    }


def write_tree(
    root: Path, files: dict[str, str], result: Any, *,
    logical_root: Path | None = None, output_dir: Path | None = None,
    path_limit: int | None = None, verify_workers: int = VERIFY_WORKERS,
) -> None:
    """Writes files deterministically and removes stale LegacyMapper-owned `.md`
    files (and the manifest) a previous run left under this tree.

    V5.3-R2.2: (1) every destination path (plus the atomic temp name) is measured against
    `path_limit` before anything is written or deleted; (2) a document whose bytes on disk are
    already exactly the expected ones is not rewritten (no temp file, no `fsync`, no replace);
    anything missing or different is written with the existing atomic mechanism. The manifest
    is built from the current output only and written last, so it is identical to a full rewrite's.
    """
    total_started = perf_counter()
    lowered: dict[str, str] = {}
    for relative in files:
        clash = lowered.setdefault(relative.lower(), relative)
        if clash != relative:
            raise ValueError(f"nombres de archivo que solo difieren en mayúsculas/minúsculas: {clash!r} y {relative!r}")
    check_output_paths(
        logical_root if logical_root is not None else root, [*files, MANIFEST_FILENAME], path_limit,
        output_root=output_dir,
    )
    raw_by_path = {relative: files[relative].encode("utf-8") for relative in files}
    digest_by_path = {relative: hashlib.sha256(raw).hexdigest() for relative, raw in raw_by_path.items()}
    previous_status, previous = _load_previous_manifest(root)

    root.mkdir(parents=True, exist_ok=True)
    started = perf_counter()
    orphans_removed = _prune_orphans(root, set(files))
    orphan_seconds = perf_counter() - started

    started = perf_counter()
    statuses = _verify_existing(root, raw_by_path, verify_workers)
    verify_seconds = perf_counter() - started

    started = perf_counter()
    manifest_files, written, skipped = _write_documents(root, files, raw_by_path, digest_by_path, statuses)
    write_seconds = perf_counter() - started
    result.files = [entry["path"] for entry in manifest_files]

    started = perf_counter()
    _write_manifest(root, result, manifest_files)
    manifest_seconds = perf_counter() - started

    started = perf_counter()
    _prune_empty_directories(root, files)
    cleanup_seconds = orphan_seconds + (perf_counter() - started)

    result.write_stats = {
        **_write_counters(files, digest_by_path, statuses, previous, written, skipped),
        "orphans_removed": orphans_removed,
        "previous_manifest": previous_status,
        "verification_mode": VERIFICATION_MODE,
        "verify_workers": verify_workers,
        "verify_seconds": round(verify_seconds, 3),
        "write_seconds": round(write_seconds, 3),
        "cleanup_seconds": round(cleanup_seconds, 3),
        "manifest_seconds": round(manifest_seconds, 3),
        "write_phase_seconds": round(perf_counter() - total_started, 3),
    }
