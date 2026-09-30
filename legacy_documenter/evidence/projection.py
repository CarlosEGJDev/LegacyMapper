"""`LegacyIndexProjector` -- reconstructs a V4.3-compatible `indexes` dict
(exactly the shape `legacy_documenter.exporters.json_exporter.JSONExporter`
already serializes to `index/*.json`) from a `NormalizedEvidence`, without
re-analyzing anything (V5.0 D-04: `evidence/` -> `index/` is a projection,
never a re-derivation).

Every projected index is either (a) returned verbatim from
`NormalizedEvidence.passthrough` for entities V5.1 keeps untouched, or (b)
rebuilt from the untouched `extensions` dict each wrapping entity already
carries (see `entities.py`) -- never reconstructed field-by-field from the
normalized core's own core fields, which is exactly what would risk losing
or reordering something on the way back out.
"""
from __future__ import annotations

from .builder import REFERENCE_ADAPTER_ID, NormalizedEvidence

_SYMBOL_KINDS = {"class", "interface", "module", "structure", "enum"}
_WEBFORM_KINDS = {"aspx", "ascx", "master"}


class LegacyProjectionError(ValueError):
    """Raised when the evidence held does not contain enough information to
    reconstruct a requested legacy index -- never silently produces a
    partial or guessed reconstruction."""


class LegacyIndexProjector:
    """Projects a `NormalizedEvidence` back into the V4.3 `indexes` dict
    shape. `adapter_id` must match whichever adapter produced the evidence's
    `extensions` -- defaults to `builder.REFERENCE_ADAPTER_ID`, the only
    adapter V5.1 implements; a future adapter (V5.4) passes its own id."""

    def __init__(self, adapter_id: str = REFERENCE_ADAPTER_ID) -> None:
        self._adapter_id = adapter_id

    def project(self, evidence: NormalizedEvidence) -> dict:
        indexes: dict = dict(evidence.passthrough)
        indexes["files"] = [artifact.extensions for artifact in evidence.source_artifacts]
        indexes["solutions"] = [solution.extensions for solution in evidence.solutions]
        indexes["projects"] = [record["extensions"][self._adapter_id] for record in evidence.projects]
        indexes["symbols"] = [c.extensions for c in evidence.components if c.component_kind in _SYMBOL_KINDS]
        indexes["webforms"] = [c.extensions for c in evidence.components if c.component_kind in _WEBFORM_KINDS]
        indexes["stored_procedures"] = [d.extensions for d in evidence.data_objects if d.object_kind == "stored_procedure"]
        indexes["sql_operations"] = [d.extensions for d in evidence.data_objects if d.object_kind == "sql"]
        indexes["repository"] = evidence.repository
        return indexes
