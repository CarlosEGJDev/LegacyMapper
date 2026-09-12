"""Operational result records for the R4 human-material ingestion boundary.

`IngestedMaterial` and `IngestionRejection`/`IngestionBatchResult` are result
objects only — they carry no new knowledge-domain semantics beyond R1's
`MaterialItem` and R3's `ProvenanceNode`.
"""
from dataclasses import dataclass, field

from legacy_documenter.knowledge.domain.models import MaterialItem
from legacy_documenter.knowledge.provenance.models import ProvenanceNode


class IngestionRejectedError(ValueError):
    """Raised by `ingest()` when a single item cannot be accepted as human-supplied material.

    The message is always built from sanitized, deterministic reason codes —
    never from raw rejected input — so it is always safe to log or display.
    """


@dataclass
class IngestedMaterial:
    """Represents one successfully ingested unit: its `MaterialItem` plus its `MATERIAL` provenance node.

    `material.material_id == provenance_node.node_id` by construction, so the
    two objects always correlate 1:1.
    """

    material: MaterialItem
    provenance_node: ProvenanceNode


@dataclass
class IngestionRejection:
    """Represents one rejected batch item, with a sanitized, deterministic reason.

    `index` is the item's position in the original batch input list, so a
    caller can correlate a rejection back to its source without LegacyMapper
    ever re-emitting the raw rejected content.
    """

    index: int
    reason: str


@dataclass
class IngestionBatchResult:
    """Represents the outcome of `ingest_batch`: accepted materials and isolated rejections.

    Both lists preserve the original input order. No accepted item is ever
    silently dropped because another item in the same batch was rejected.
    """

    accepted: list[IngestedMaterial] = field(default_factory=list)
    rejected: list[IngestionRejection] = field(default_factory=list)

    @property
    def accepted_count(self) -> int:
        """Returns the number of accepted items."""
        return len(self.accepted)

    @property
    def rejected_count(self) -> int:
        """Returns the number of rejected items."""
        return len(self.rejected)
