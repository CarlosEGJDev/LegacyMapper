"""Closed vocabulary for the V4-R7 explicit knowledge-relation layer.

`RelationKind` is deliberately independent from R1's `SourceType`,
`KnowledgeNature`, `KnowledgeStatus` and `TemporalState`: none of those
vocabularies are read to derive a relation kind anywhere in this package.
"""
from enum import Enum


class RelationKind(str, Enum):
    """The four R7 relation kinds. No other kind is supported in this round.

    `DIFFERENCE` and `CONFLICT` are neutral/incompatibility statements with no
    inherent order; `GAP` and `TEMPORAL_EVOLUTION` carry an explicit
    FROM -> TO direction. See `directionality_for`.
    """

    DIFFERENCE = "DIFFERENCE"
    GAP = "GAP"
    CONFLICT = "CONFLICT"
    TEMPORAL_EVOLUTION = "TEMPORAL_EVOLUTION"


class RelationDirectionality(str, Enum):
    """Whether a `RelationKind` treats its two participants as ordered."""

    SYMMETRIC = "SYMMETRIC"
    DIRECTIONAL = "DIRECTIONAL"


class RelationBasis(str, Enum):
    """How a relation record came to exist. Never implies truth or approval.

    `AI_PROPOSED` is representable for future compatibility only; R7 itself
    never produces a relation with this basis, since no AI call occurs here.
    """

    EXPLICIT = "EXPLICIT"
    DETERMINISTIC_RULE = "DETERMINISTIC_RULE"
    AI_PROPOSED = "AI_PROPOSED"
    UNRESOLVED = "UNRESOLVED"


EXPECTED_DIRECTIONALITY: dict[RelationKind, RelationDirectionality] = {
    RelationKind.DIFFERENCE: RelationDirectionality.SYMMETRIC,
    RelationKind.CONFLICT: RelationDirectionality.SYMMETRIC,
    RelationKind.GAP: RelationDirectionality.DIRECTIONAL,
    RelationKind.TEMPORAL_EVOLUTION: RelationDirectionality.DIRECTIONAL,
}
