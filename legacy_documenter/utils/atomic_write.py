"""Crash-safe text writes for LegacyMapper's authoritative machine artifacts (V4.2-R6).

Writes to a temporary sibling file first, flushes/`fsync`s it, then
`os.replace`s it onto the final destination -- so a process interrupted
mid-write can never leave the destination partially written or corrupted;
the destination is always either the previous complete content or the new
complete content, never a truncated mix of the two. `os.replace` is atomic
on both POSIX and Windows when source and destination are on the same
filesystem (true here: the temp file is created as a sibling of the real
destination), which is what actually makes this safe rather than merely
reducing the odds of a torn write.

Applied narrowly to `RUN_SUMMARY.json`/`.md`, the AI proposal JSON/Markdown
pair, and `index/*.json` (V4.2-R6 section 7's explicit minimum) -- this is
one small standard-library primitive, not a transactional-write framework.

`_replace_with_retry` (PRE-V5.1 rerun-intermittency investigation fix):
on Windows, `os.replace` onto an existing destination can intermittently
raise `PermissionError` ("[WinError 5] Access is denied") when another
process (most commonly real-time antivirus scanning, or the search
indexer) transiently holds a read handle open on the destination file
right after it was rewritten by a previous run into the same `--output`
directory -- observed here specifically on rerun-into-same-output
scenarios, never on a first write to a fresh path. This is an
external, transient lock, not a logic error: the destination content is
never corrupted by it (the failed attempt still leaves the previous
complete content in place, exactly as any other unattempted replace
would), so a small bounded retry with a short backoff is a safe,
minimal, standard mitigation -- it changes only how long a genuinely
transient lock is tolerated before the same `PermissionError` is
re-raised, never what gets written or how atomicity is achieved.
"""
from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

_REPLACE_RETRY_ATTEMPTS = 5
_REPLACE_RETRY_INITIAL_DELAY_S = 0.05


def _replace_with_retry(tmp_name: str, path: Path) -> None:
    delay = _REPLACE_RETRY_INITIAL_DELAY_S
    for attempt in range(1, _REPLACE_RETRY_ATTEMPTS + 1):
        try:
            os.replace(tmp_name, path)
            return
        except PermissionError:
            if attempt == _REPLACE_RETRY_ATTEMPTS:
                raise
            time.sleep(delay)
            delay *= 2


def atomic_write_bytes(path: str | Path, content: bytes) -> None:
    """Atomically replaces `path` with the exact `content` bytes (V5.3-R2.4).

    Same temp-sibling + `fsync` + `os.replace` mechanism as `atomic_write_text`, but with no newline
    translation, so a checksum computed over `content` is the checksum of what lands on disk.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        _replace_with_retry(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def atomic_write_text(path: str | Path, content: str, encoding: str = "utf-8") -> None:
    """Atomically replaces `path` with `content` (temp sibling + `os.replace`).

    Creates parent directories if needed. On any failure, the temporary file
    is removed and the original `path` is left exactly as it was.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        _replace_with_retry(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
