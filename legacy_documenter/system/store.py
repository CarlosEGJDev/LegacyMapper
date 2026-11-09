"""Crash-safe persistence of every provider exchange, keyed by stable request identity.

`requests/<KIND>/<identity>.json` holds the ACCEPTED record (written atomically the moment a response is accepted);
`attempts/<identity>.jsonl` appends every attempt, including failures and rejections. An accepted record is never overwritten:
a later run that finds it replays it and calls the provider 0 times.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from legacy_documenter.utils.atomic_write import atomic_write_text

from .models import KINDS, canonical


class RequestStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def _accepted_path(self, kind: str, identity: str) -> Path:
        return self.root / "requests" / kind / f"{identity}.json"

    def get(self, kind: str, identity: str) -> dict | None:
        path = self._accepted_path(kind, identity)
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None            # missing or corrupt -> treated as not persisted (never trusted)
        if not isinstance(record, dict) or record.get("identity") != identity or record.get("accepted") is not True:
            return None
        return record

    def put_accepted(self, record: dict) -> None:
        path = self._accepted_path(record["kind"], record["identity"])
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(path, json.dumps(record, ensure_ascii=False, sort_keys=True, indent=1) + "\n")

    def append_attempt(self, identity: str, entry: dict) -> None:
        path = self.root / "attempts" / f"{identity}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(canonical(entry) + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def iter_accepted(self):
        for kind in KINDS:
            folder = self.root / "requests" / kind
            if folder.is_dir():
                for path in sorted(folder.glob("*.json")):
                    record = self.get(kind, path.stem)
                    if record:
                        yield record

    # -- coverage / checkpoint file -------------------------------------------------------------
    @property
    def coverage_path(self) -> Path:
        return self.root / "FULL_SYSTEM_COVERAGE.json"

    def load_state(self) -> dict:
        try:
            value = json.loads(self.coverage_path.read_text(encoding="utf-8"))
            return value if isinstance(value, dict) else {}
        except (OSError, ValueError):
            return {}

    def save_state(self, state: dict) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        atomic_write_text(self.coverage_path, json.dumps(state, ensure_ascii=False, sort_keys=True, indent=1) + "\n")
