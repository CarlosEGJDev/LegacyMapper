"""Deterministic comparison of two File States (V5.3-R2.4).

Per path: `unchanged`, `modified`, `added`, `deleted`. A file is unchanged when its `file_type` and *comparison
hash* match: the semantic hash for analyzed types (so a CRLF/LF-only change is unchanged -- extraction would
read the same text; it is also listed in `line_ending_only`), the raw hash otherwise. Unreadable files are
never unchanged. `rename = deleted + added` (ids derive from the path); `renamed_candidates` is diagnostic
metadata only and never implies reuse.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .file_state import FileRecord


@dataclass
class FileStateDiff:
    """Result of comparing the previous File State with the current one (all lists sorted)."""

    unchanged: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    renamed_candidates: list[dict] = field(default_factory=list)
    line_ending_only: list[str] = field(default_factory=list)

    def counts(self) -> dict:
        """Sizes of each list (for logs)."""
        return {
            "unchanged": len(self.unchanged), "modified": len(self.modified), "added": len(self.added),
            "deleted": len(self.deleted), "renamed_candidates": len(self.renamed_candidates),
            "line_ending_only": len(self.line_ending_only),
        }


def _comparison_key(record: FileRecord) -> tuple[str, str] | None:
    """`(basis, hash)` used to decide sameness; `None` for unreadable records."""
    if not record.readable:
        return None
    if record.sha256_semantic is not None:
        return ("semantic", record.sha256_semantic)
    return ("raw", record.sha256_raw) if record.sha256_raw is not None else None


def diff_file_states(previous: Iterable[FileRecord], current: Iterable[FileRecord]) -> FileStateDiff:
    """Classifies every path of `previous` and `current`."""
    before = {record.path: record for record in previous}
    now = {record.path: record for record in current}
    diff = FileStateDiff()
    for path in sorted(set(before) & set(now)):
        old, new = before[path], now[path]
        old_key, new_key = _comparison_key(old), _comparison_key(new)
        if old_key is not None and old_key == new_key and old.file_type == new.file_type:
            diff.unchanged.append(path)
            if old.sha256_raw != new.sha256_raw:
                diff.line_ending_only.append(path)
        else:
            diff.modified.append(path)
    diff.added = sorted(set(now) - set(before))
    diff.deleted = sorted(set(before) - set(now))
    diff.renamed_candidates = _renamed_candidates([before[p] for p in diff.deleted], [now[p] for p in diff.added])
    return diff


def _renamed_candidates(deleted: list[FileRecord], added: list[FileRecord]) -> list[dict]:
    """Pairs a deleted and an added file of the same type and comparison hash (empty files excluded: every empty
    file shares one hash, which says nothing). Pairing is deterministic: both sides sorted by path, zipped."""
    gone: dict[tuple, list[str]] = {}
    for record in deleted:
        key = _comparison_key(record)
        if key is not None and record.size > 0:
            gone.setdefault((record.file_type, *key), []).append(record.path)
    pairs = []
    for record in added:
        key = _comparison_key(record)
        if key is None or record.size == 0:
            continue
        candidates = gone.get((record.file_type, *key))
        if candidates:
            pairs.append({"from": candidates.pop(0), "to": record.path, "basis": key[0]})
    return sorted(pairs, key=lambda pair: (pair["from"], pair["to"]))
