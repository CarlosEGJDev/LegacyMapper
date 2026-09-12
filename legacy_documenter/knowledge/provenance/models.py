"""Provenance node/edge records for the V4 lineage graph.

Source-neutral: no field requires a filesystem path, a code symbol, a
project, a language, a framework, or a repository scanner. Code-derived
lineage is one representable case among several (human requirement, user
story, corporate standard, business context, technical constraint, project
document, external document, approved decision, AI interpretation, unresolved
information), never a precondition for a valid node.
"""
from dataclasses import dataclass, field, replace

from legacy_documenter.documentation.contracts import stable_id
from legacy_documenter.knowledge.domain.enums import SourceType
from legacy_documenter.knowledge.domain.models import Origin
from legacy_documenter.knowledge.input.contracts import SourceInputValidationError
from legacy_documenter.knowledge.input.normalization import validate_metadata
from legacy_documenter.knowledge.provenance.enums import (
    EdgeRelationship,
    LineageCompleteness,
    NodeKind,
    TransformationType,
)
from legacy_documenter.utils.sanitizer import sanitize_text


class ProvenanceValidationError(ValueError):
    """Raised when a provenance node/edge, or the graph they belong to, violates its contract."""


@dataclass
class ProvenanceNode:
    """Represents one identifiable participant in a lineage graph.

    `provenance_status` is declared explicitly by the caller who knows what
    lineage is domain-expected for this node; the graph never infers
    `COMPLETE` merely because one parent edge exists, and never infers
    `PARTIAL`/`UNRESOLVED` either — silence about completeness defaults to
    `UNRESOLVED` rather than a fabricated `COMPLETE`.
    """

    node_id: str
    node_kind: NodeKind
    source_type: SourceType | None = None
    reference: str | None = None
    origin: Origin | None = None
    metadata: dict = field(default_factory=dict)
    provenance_status: LineageCompleteness = LineageCompleteness.UNRESOLVED

    def validate(self) -> bool:
        """Performs the minimal structural check every `ProvenanceNode` must satisfy."""
        if not self.node_id or not self.node_id.strip():
            raise ProvenanceValidationError("node_id_required")
        if not isinstance(self.node_kind, NodeKind):
            raise ProvenanceValidationError("invalid_node_kind")
        if self.source_type is not None and not isinstance(self.source_type, SourceType):
            raise ProvenanceValidationError("invalid_source_type")
        if not isinstance(self.provenance_status, LineageCompleteness):
            raise ProvenanceValidationError("invalid_provenance_status")
        if self.origin is not None:
            self.origin.validate()
        return True


@dataclass
class ProvenanceEdge:
    """Represents one lineage relationship from an earlier/source node to a later/derived node.

    `transformation` is `None` when no transformation is explicitly known;
    R3 never guesses one. See `graph.py` for the canonical edge direction.
    """

    edge_id: str
    from_node_id: str
    to_node_id: str
    relationship: EdgeRelationship
    transformation: TransformationType | None = None
    metadata: dict = field(default_factory=dict)

    def validate(self) -> bool:
        """Performs the minimal structural check every `ProvenanceEdge` must satisfy."""
        if not self.edge_id or not self.edge_id.strip():
            raise ProvenanceValidationError("edge_id_required")
        if not self.from_node_id or not self.from_node_id.strip():
            raise ProvenanceValidationError("from_node_id_required")
        if not self.to_node_id or not self.to_node_id.strip():
            raise ProvenanceValidationError("to_node_id_required")
        if not isinstance(self.relationship, EdgeRelationship):
            raise ProvenanceValidationError("invalid_relationship")
        if self.transformation is not None and not isinstance(self.transformation, TransformationType):
            raise ProvenanceValidationError("invalid_transformation")
        return True


def _validate_metadata(metadata: dict) -> dict:
    """Wraps R2's metadata validator, re-raising as `ProvenanceValidationError` for a single error surface."""
    try:
        return validate_metadata(metadata)
    except SourceInputValidationError as exc:
        raise ProvenanceValidationError(str(exc)) from exc


def normalize_node(node: ProvenanceNode) -> ProvenanceNode:
    """Returns a sanitized, validated copy of `node`; never mutates the input.

    Reuses `legacy_documenter.knowledge.input.normalization.validate_metadata`
    (R2) rather than a second, subtly different metadata validator.
    """
    reference = sanitize_text(node.reference) if node.reference else node.reference
    normalized = replace(node, reference=reference, metadata=_validate_metadata(node.metadata))
    normalized.validate()
    return normalized


def normalize_edge(edge: ProvenanceEdge) -> ProvenanceEdge:
    """Returns a sanitized, validated copy of `edge`; never mutates the input."""
    normalized = replace(edge, metadata=_validate_metadata(edge.metadata))
    normalized.validate()
    return normalized


def new_node_id(*parts: object) -> str:
    """Derives a stable `PRN-` id, reusing the existing V3 `stable_id` hashing contract.

    Equivalent normalized parts always produce the same id; it never depends
    on current time, randomness, or object identity.
    """
    return stable_id("PRN", *parts)


def new_edge_id(*parts: object) -> str:
    """Derives a stable `PED-` id, reusing the existing V3 `stable_id` hashing contract."""
    return stable_id("PED", *parts)
