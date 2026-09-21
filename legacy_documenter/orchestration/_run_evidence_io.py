"""Reads the CURRENT run's own deterministic evidence off disk (V4.3-R5).

Internal helper module for `legacy_documenter.orchestration.ai_interpretation`,
following the same "small internal `_*` module behind an unchanged facade"
pattern already established by `legacy_documenter/knowledge/_readiness_io.py`
and `legacy_documenter/extractors/_database_*.py`. It exists so the
orchestration module keeps a single responsibility (build, gate, call,
validate) and does not additionally own JSON/file deserialization.

Everything here reads exclusively from the `output_dir` it is given -- this run's
own `--output` directory -- and never from `output/v2_r5_1_full/`, `output/v3_*`
or `codex/V3/` (the V4.2-R4 context-boundary requirement). Both functions fail
closed with `FileNotFoundError` rather than returning an empty structure, so a
run whose EXPORT/CONTEXT stage did not complete can never be interpreted
against partial evidence.
"""
from __future__ import annotations

import json
from pathlib import Path


def load_indexes(output_dir: str | Path) -> dict:
    """Loads this run's `index/*.json` into the `ix` dict shape hydration consumes.

    Each file's stem is its key (`functional_flows.json` ->
    `functional_flows`), which is exactly the shape
    `legacy_documenter.context.system_context_builder.SystemContextBuilder`
    and `legacy_documenter.context.hydration.EvidenceHydrator` already expect --
    no renaming, filtering or reshaping happens here.
    """
    index_dir = Path(output_dir) / "index"
    if not index_dir.is_dir():
        raise FileNotFoundError(index_dir)
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(index_dir.glob("*.json"))}


def load_source_snapshot(output_dir: str | Path) -> str:
    """Reads this run's own `ai_context/SYSTEM_CONTEXT.json` source snapshot hash."""
    path = Path(output_dir) / "ai_context" / "SYSTEM_CONTEXT.json"
    if not path.is_file():
        raise FileNotFoundError(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    return str((payload.get("metadata") or {}).get("source_snapshot_sha256") or "")
