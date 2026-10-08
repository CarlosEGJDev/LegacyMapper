"""Read-only access to the artifacts of one run directory (V5.8).

This is the one place of the consumer layer that knows the physical layout of a run (`index/`,
`documentation_v52/`, `consumer_projection/`). Consumers never see paths: they get kinds, ids and records.
Everything is lazy, cached per instance, and strictly read-only.
"""
from __future__ import annotations

import json
from pathlib import Path

from legacy_documenter.utils.sanitizer import sanitize_data

from .contracts import ConsumerError, ConsumerErrorCode

#: index file (also the hydration key) -> (evidence kind exposed to consumers, id field). Mirrors what hydration
#: and review already treat as the primary owner of an id.
EVIDENCE_SOURCES = {
    "entry_points": ("ENTRY_POINT", "id"),
    "functional_flows": ("FLOW", "id"),
    "functional_paths": ("PATH", "path_id"),
    "data_access": ("DATA_ACCESS", "id"),
    "sql_operations": ("SQL_OPERATION", "id"),
    "stored_procedures": ("STORED_PROCEDURE", "id"),
    "data_parameters": ("DATA_PARAMETER", "id"),
}
HUMAN_DOC_MANIFEST = Path("documentation_v52") / "MANIFEST.json"
CONSUMER_PROJECTION_MANIFEST = Path("consumer_projection") / "CONSUMER_PROJECTION.json"
CONSUMER_PROJECTION_DIR = Path("consumer_projection")
DOCUMENTATION_DIR = Path("documentation_v52")


def _unavailable(detail: str) -> ConsumerError:
    return ConsumerError(ConsumerErrorCode.SOURCE_UNAVAILABLE, detail)


class RunArtifacts:
    """Lazy, cached, read-only view of one run (`--output`) directory."""

    def __init__(self, run_dir: str | Path) -> None:
        self.run_dir = Path(run_dir)
        self._ix: dict[str, list] = {}
        self._evidence: dict[str, list[tuple[str, dict]]] | None = None
        self._json: dict[Path, object] = {}

    def read_json(self, relative: Path) -> object:
        """Parsed JSON of a fixed, known artifact (cached); missing/unreadable -> SOURCE_UNAVAILABLE."""
        if relative not in self._json:
            target = self.run_dir / relative
            if not target.is_file():
                raise _unavailable(f"artifact_missing:{relative.as_posix()}")
            try:
                self._json[relative] = json.loads(target.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                raise _unavailable(f"artifact_unreadable:{relative.as_posix()}") from None
        return self._json[relative]

    def read_text(self, relative: Path) -> str:
        """UTF-8 text of an artifact path already validated against a manifest (never caller-built)."""
        try:
            return (self.run_dir / relative).read_text(encoding="utf-8")
        except (OSError, ValueError):
            raise _unavailable(f"artifact_unreadable:{relative.as_posix()}") from None

    def ix(self) -> dict[str, list]:
        """The hydration/AI index mapping (`{name: [records]}`), loaded once and shared across requests."""
        for name in EVIDENCE_SOURCES:
            if name not in self._ix:
                data = self.read_json(Path("index") / f"{name}.json")
                if not isinstance(data, list):
                    raise _unavailable(f"index_not_a_list:{name}")
                self._ix[name] = data
        return self._ix

    def evidence(self) -> dict[str, list[tuple[str, dict]]]:
        """`{id: [(kind, record)]}` over every primary-owner index; built once, O(1) lookups afterwards."""
        if self._evidence is None:
            lookup: dict[str, list[tuple[str, dict]]] = {}
            ix = self.ix()
            for name in sorted(EVIDENCE_SOURCES):
                kind, key = EVIDENCE_SOURCES[name]
                for record in ix[name]:
                    value = record.get(key) if isinstance(record, dict) else None
                    if isinstance(value, str) and value:
                        lookup.setdefault(value, []).append((kind, record))
            self._evidence = lookup
        return self._evidence


def scrub(value: object) -> object:
    """Central sanitizer over anything handed to a consumer (credentials, connection strings)."""
    return sanitize_data(value)
