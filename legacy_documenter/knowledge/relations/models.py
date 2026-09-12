"""Source-neutral relation record for the V4-R7 gap/conflict representation layer.

`KnowledgeRelation` links back to R4/R1 `MaterialItem`s by `material_id` only
(no payload duplication) and carries exactly one canonical relation fact
(`relation_kind`, `participants`) plus its mechanical directionality
projection (`directionality`) — never two independently editable truths.
It carries no approval, canonical, winner/loser or truth field.
"""
from dataclasses import dataclass, field

from legacy_documenter.documentation.contracts import stable_id
from legacy_documenter.knowledge.relations.enums import (
    EXPECTED_DIRECTIONALITY,
    RelationBasis,
    RelationDirectionality,
    RelationKind,
)


class RelationValidationError(ValueError):
    """Raised when a `KnowledgeRelation` violates its structural contract."""


def directionality_for(relation_kind: RelationKind) -> RelationDirectionality:
    """Returns the fixed, mechanical `RelationDirectionality` for a `RelationKind`.

    `DIFFERENCE`/`CONFLICT` are always `SYMMETRIC`; `GAP`/`TEMPORAL_EVOLUTION`
    are always `DIRECTIONAL`. This is a closed structural mapping, never a
    per-instance choice and never inferred from participant content.
    """
    if not isinstance(relation_kind, RelationKind):
        raise RelationValidationError(f"invalid_relation_kind:{relation_kind!r}")
    return EXPECTED_DIRECTIONALITY[relation_kind]


def canonical_participants(relation_kind: RelationKind, material_a: str, material_b: str) -> tuple[str, str]:
    """Orders two participant ids according to `relation_kind`'s directionality.

    Symmetric kinds are canonically sorted so `(A, B)` and `(B, A)` always
    produce the identical pair; directional kinds preserve caller-supplied
    `(FROM, TO)` order verbatim, since direction must be explicit, never
    inferred from participant ordering.
    """
    if directionality_for(relation_kind) == RelationDirectionality.SYMMETRIC:
        return tuple(sorted((material_a, material_b)))
    return (material_a, material_b)


@dataclass
class KnowledgeRelation:
    """Represents one explicitly established relation between exactly two materials.

    Required properties enforced by `validate()`: deterministic identity, no
    approval/canonical/truth/winner-loser field, participants are never
    mutated by this module, and self-relations are always rejected.
    """

    relation_id: str
    relation_kind: RelationKind
    directionality: RelationDirectionality
    participants: tuple[str, str]
    basis: RelationBasis = RelationBasis.EXPLICIT
    notes: str | None = None
    evidence_refs: tuple[str, ...] = ()
    metadata: dict = field(default_factory=dict)

    @property
    def from_id(self) -> str:
        """Returns the first canonical participant (sorted for symmetric kinds, FROM for directional)."""
        return self.participants[0]

    @property
    def to_id(self) -> str:
        """Returns the second canonical participant (sorted for symmetric kinds, TO for directional)."""
        return self.participants[1]

    def validate(self) -> bool:
        """Performs the full structural contract check for a `KnowledgeRelation`."""
        if not self.relation_id or not self.relation_id.strip():
            raise RelationValidationError("relation_id_required")
        if not isinstance(self.relation_kind, RelationKind):
            raise RelationValidationError("invalid_relation_kind")
        if not isinstance(self.directionality, RelationDirectionality):
            raise RelationValidationError("invalid_directionality")
        if directionality_for(self.relation_kind) != self.directionality:
            raise RelationValidationError("directionality_inconsistent_with_relation_kind")

        if len(self.participants) != 2:
            raise RelationValidationError("relation_requires_exactly_two_participants")
        material_a, material_b = self.participants
        if not material_a or not material_a.strip() or not material_b or not material_b.strip():
            raise RelationValidationError("participant_id_required")
        if material_a == material_b:
            raise RelationValidationError("self_relation_rejected")

        if not isinstance(self.basis, RelationBasis):
            raise RelationValidationError("invalid_basis")
        for evidence_ref in self.evidence_refs:
            if not evidence_ref or not evidence_ref.strip():
                raise RelationValidationError("evidence_ref_required")
        return True


def new_relation_id(relation_kind: RelationKind, participants: tuple[str, str]) -> str:
    """Derives a stable `REL-` id from `relation_kind` and canonical `participants` only.

    Reuses the existing V3 `stable_id` hashing contract. Deliberately excludes
    `basis`, `notes`, `evidence_refs`, and `metadata` from identity: those are
    explanatory/attribution data, not part of what makes two relations the
    same semantic fact. Equivalent relations (same kind, same canonical
    participants) always produce the same id; it never depends on current
    time, randomness, or object identity.
    """
    return stable_id("REL", relation_kind.value, participants[0], participants[1])
