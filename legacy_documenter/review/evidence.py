"""Read-only evidence resolution for review: ref -> fingerprint, and segment scope (V5.7).

Reads exactly the deterministic `<run>/index/*.json` files the AI projection was built from. Never writes,
never mutates, never calls a provider. Fingerprints change when a referenced record changes, which is the
deterministic signal behind STALE detection.
"""
from __future__ import annotations

import json
from pathlib import Path

from .models import ReviewError, ReviewErrorCode, fingerprint

#: Index file -> keys that make a record the primary owner of that id.
_PRIMARY_KEYS = {
    "entry_points.json": ("id",),
    "functional_flows.json": ("id",),
    "functional_paths.json": ("path_id",),
    "data_access.json": ("id",),
    "sql_operations.json": ("id",),
    "stored_procedures.json": ("id",),
    "data_parameters.json": ("id",),
}


class EvidenceIndex:
    """Resolves evidence refs of one run directory against its own index files."""

    def __init__(self, run_dir: str | Path) -> None:
        self.run_dir = Path(run_dir)
        self._primary: dict[str, list[str]] = {}
        self._secondary: dict[str, list[str]] = {}
        self._paths: dict[str, dict] = {}
        self._flows: dict[str, dict] = {}
        self._signature = self._stat_signature()
        self._load()

    def _stat_signature(self) -> tuple:
        index_dir = self.run_dir / "index"
        return tuple((n, s.st_size, s.st_mtime_ns) for n in sorted(_PRIMARY_KEYS)
                     if (s := (index_dir / n).stat() if (index_dir / n).is_file() else None) is not None)

    def is_unchanged(self) -> bool:
        """Cheap optimistic check: no index file changed (size/mtime) since this index was loaded."""
        return self._stat_signature() == self._signature

    def _load(self) -> None:
        index_dir = self.run_dir / "index"
        if not index_dir.is_dir():
            raise ReviewError(ReviewErrorCode.MISSING_EVIDENCE, "run_index_directory_missing")
        for name, keys in _PRIMARY_KEYS.items():
            path = index_dir / name
            if not path.is_file():
                continue
            records = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(records, list):
                raise ReviewError(ReviewErrorCode.MISSING_EVIDENCE, f"index_not_a_list:{name}")
            for record in records:
                digest = fingerprint(record)
                for key in keys:
                    value = record.get(key)
                    if isinstance(value, str) and value:
                        self._primary.setdefault(value, []).append(digest)
                if name == "functional_paths.json":
                    self._paths[record["path_id"]] = record
                    for ref in (*record.get("nodes", []), record.get("terminal_target"), *record.get("evidence_refs", [])):
                        if isinstance(ref, str) and ref:
                            self._secondary.setdefault(ref, []).append(digest)
                if name == "functional_flows.json":
                    self._flows[record["id"]] = record

    def ref_fingerprint(self, ref: str) -> str | None:
        """Fingerprint of the record(s) owning `ref`; `None` when the ref does not resolve in this run."""
        digests = self._primary.get(ref) or self._secondary.get(ref)
        if not digests:
            return None
        return fingerprint(sorted(digests))

    def snapshot(self, refs: list[str] | tuple[str, ...]) -> dict[str, str]:
        """`{ref: fingerprint}` for every ref; raises MISSING_EVIDENCE listing unresolved refs."""
        result: dict[str, str] = {}
        missing: list[str] = []
        for ref in sorted(set(refs)):
            digest = self.ref_fingerprint(ref)
            if digest is None:
                missing.append(ref)
            else:
                result[ref] = digest
        if missing:
            raise ReviewError(ReviewErrorCode.MISSING_EVIDENCE, ",".join(missing[:5]) + ("..." if len(missing) > 5 else ""))
        return result

    def segment_scope_refs(self, segment: dict) -> set[str]:
        """Every ref reachable from the segment's INCLUDED paths (never from omitted ones)."""
        allowed: set[str] = set()
        parent = segment.get("parent_flow_id")
        if parent:
            allowed.add(parent)
            flow = self._flows.get(parent)
            if flow and flow.get("entry_point_id"):
                allowed.add(flow["entry_point_id"])
        for path_id in segment.get("included_paths", []):
            record = self._paths.get(path_id)
            if record is None:
                raise ReviewError(ReviewErrorCode.MISSING_EVIDENCE, f"segment_path_not_in_index:{path_id}")
            allowed.add(path_id)
            allowed.update(ref for ref in (*record.get("nodes", []), record.get("terminal_target"), *record.get("evidence_refs", [])) if isinstance(ref, str) and ref)
        return allowed


def evidence_fingerprint(snapshot: dict[str, str]) -> str:
    """Single fingerprint over a ref snapshot."""
    return fingerprint(dict(sorted(snapshot.items())))
