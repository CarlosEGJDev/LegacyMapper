"""Write-if-changed for LegacyMapper's generated outputs (V5.3-R2.6).

Principle: *recompute for correctness; skip identical writes for savings.* The caller always renders the
final content; this module only decides whether the bytes already on disk are exactly those bytes. The
decision is a byte-for-byte comparison of the destination with the bytes about to be written -- never
`mtime`, never size alone, never a previous cache or manifest. A missing or different file is written with
the existing atomic primitive (`atomic_write_bytes`: temp sibling + fsync + replace, temp removed on failure).

Text keeps the newline behavior of the writers it replaces: `newline=None` (default) reproduces what
`Path.write_text`/`atomic_write_text` do (each `\\n` becomes `os.linesep`), `newline="\\n"` writes the text
unchanged. `write_bytes_if_changed` never touches the content. Counters are per output *family* and live
in memory only (`LEDGER`); the pipeline logs them, nothing is persisted.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

from .atomic_write import atomic_write_bytes

LOG = logging.getLogger("legacy_documenter")


@dataclass
class FamilyStats:
    """Counters of one output family (see module docstring)."""

    generated: int = 0
    written: int = 0
    skipped_identical: int = 0
    bytes_generated: int = 0
    bytes_written: int = 0
    compare_seconds: float = 0.0
    write_seconds: float = 0.0

    def as_dict(self) -> dict:
        """Counters with rounded timings."""
        return {**self.__dict__, "compare_seconds": round(self.compare_seconds, 3), "write_seconds": round(self.write_seconds, 3)}


@dataclass
class WriteLedger:
    """Run-scoped, in-memory counters by family. Reset at the start of a run."""

    families: dict[str, FamilyStats] = field(default_factory=dict)

    def stats(self, family: str) -> FamilyStats:
        """The (created on demand) counters of `family`."""
        return self.families.setdefault(family, FamilyStats())

    def reset(self) -> None:
        """Forgets every counter."""
        self.families.clear()

    def snapshot(self) -> dict[str, dict]:
        """`{family: counters}` sorted by family."""
        return {name: self.families[name].as_dict() for name in sorted(self.families)}


#: The pipeline runs single-threaded per process; one ledger per run keeps call sites free of plumbing.
LEDGER = WriteLedger()


def log_write_ledger() -> None:
    """Logs the counters of the current run at INFO (no file is produced)."""
    LOG.info("write-skip: %s", LEDGER.snapshot())


def _identical(path: Path, content: bytes) -> bool:
    """True only if `path` is a readable regular file holding exactly `content`."""
    try:
        if os.stat(path).st_size != len(content):
            return False
        return path.read_bytes() == content
    except OSError:
        return False


def write_bytes_if_changed(path: str | Path, content: bytes, family: str = "other") -> bool:
    """Atomically writes `content` unless `path` already holds exactly those bytes; returns whether it wrote."""
    path = Path(path)
    stats = LEDGER.stats(family)
    stats.generated += 1
    stats.bytes_generated += len(content)
    started = perf_counter()
    identical = _identical(path, content)
    stats.compare_seconds += perf_counter() - started
    if identical:
        stats.skipped_identical += 1
        return False
    started = perf_counter()
    try:
        atomic_write_bytes(path, content)
    finally:
        stats.write_seconds += perf_counter() - started
    stats.written += 1
    stats.bytes_written += len(content)
    return True


def write_text_if_changed(
    path: str | Path, content: str, family: str = "other", encoding: str = "utf-8", newline: str | None = None,
) -> bool:
    """`write_bytes_if_changed` for text; `newline=None` keeps the platform translation of `write_text`."""
    if newline is None and os.linesep != "\n":
        content = content.replace("\n", os.linesep)
    return write_bytes_if_changed(path, content.encode(encoding), family)
