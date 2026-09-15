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
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path


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
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
