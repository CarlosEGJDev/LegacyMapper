"""Deterministic serialization for the CLI execution/result model.

Reuses `legacy_documenter.utils.json_rendering.render_deterministic_json`
(the same sorted-keys, fixed-separators renderer the V4 knowledge sub-packages
already share) instead of introducing a second deterministic-JSON writer.
"""
from __future__ import annotations

from legacy_documenter.cli.execution_model import RunResult
from legacy_documenter.utils.json_rendering import render_deterministic_json


def render_run_result(result: RunResult) -> str:
    """Serializes `result` to deterministic JSON text.

    The same `RunResult` value always renders to the exact same bytes: no
    timestamp, UUID, random identifier, or machine-specific absolute path is
    part of the model (see `execution_model.py`), so identity comes entirely
    from the fields the caller set.
    """
    return render_deterministic_json(result.to_dict())
