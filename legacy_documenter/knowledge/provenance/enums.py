"""Closed vocabularies for the V4 provenance/lineage layer.

Each enum is a deterministic, closed contract, per the same discipline as
`legacy_documenter.knowledge.domain.enums`. Free-form strings are rejected
wherever one of these types applies.
"""
from enum import Enum


class NodeKind(str, Enum):
    """Categorizes a provenance participant. These are lineage categories, not workflow stages.

    Their presence here does not imply the corresponding V4 lifecycle round
    (classification, proposal, approval, composition) is implemented.
    """

    SOURCE = "SOURCE"
    MATERIAL = "MATERIAL"
    EVIDENCE = "EVIDENCE"
    STATEMENT = "STATEMENT"
    INTERPRETATION = "INTERPRETATION"
    PROPOSAL = "PROPOSAL"
    KNOWLEDGE = "KNOWLEDGE"


class EdgeRelationship(str, Enum):
    """Closed catalog of lineage relationships between two provenance nodes.

    Direction is always earlier/source -> later/derived (see `graph.py`
    module docstring for the canonical direction statement).
    """

    ORIGINATES_FROM = "ORIGINATES_FROM"
    MATERIALIZED_FROM = "MATERIALIZED_FROM"
    EVIDENCE_FROM = "EVIDENCE_FROM"
    DERIVED_FROM = "DERIVED_FROM"
    INTERPRETED_FROM = "INTERPRETED_FROM"
    REFERENCES = "REFERENCES"


class TransformationType(str, Enum):
    """Closed catalog of known transformations that may occur along a lineage edge.

    An edge's `transformation` field is `None` when no transformation is
    explicitly known — never guessed or inferred from context.
    """

    DETERMINISTIC_EXTRACTION = "DETERMINISTIC_EXTRACTION"
    NORMALIZATION = "NORMALIZATION"
    HUMAN_SUPPLIED = "HUMAN_SUPPLIED"
    AI_INTERPRETATION = "AI_INTERPRETATION"
    AGGREGATION = "AGGREGATION"
    MANUAL_CORRECTION = "MANUAL_CORRECTION"


class LineageCompleteness(str, Enum):
    """Represents how much of a node's expected lineage is currently known.

    This is a caller-declared classification (see `ProvenanceNode.provenance_status`),
    never inferred from parent count: knowing one parent does not make lineage
    `COMPLETE`, and lacking one does not make it `INVALID`. Only
    `ProvenanceGraph.validate_graph()` can determine `INVALID` from an actual
    structural violation.
    """

    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    UNRESOLVED = "UNRESOLVED"
    INVALID = "INVALID"
