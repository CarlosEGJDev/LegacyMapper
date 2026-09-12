"""Deterministic explicit-relation-creation service (V4-R7).

Pipeline: `RelationRequest` (explicit caller input) -> `KnowledgeRelation`,
using only `relation_kind`, `material_a`, `material_b`, and optional
attribution fields. No material, classification, or temporal-placement
content is ever read to decide `relation_kind` — that decision must already
be present in the request. This module performs no file, network, database,
provider, or directory-scan I/O.
"""
from dataclasses import dataclass, field

from legacy_documenter.knowledge.classification.models import ClassificationRecord
from legacy_documenter.knowledge.relations.enums import RelationBasis, RelationKind
from legacy_documenter.knowledge.relations.models import (
    KnowledgeRelation,
    RelationValidationError,
    canonical_participants,
    directionality_for,
    new_relation_id,
)
from legacy_documenter.knowledge.temporal.models import TemporalPlacement
from legacy_documenter.utils.sanitizer import sanitize_data, sanitize_text


class RelationRejectedError(ValueError):
    """Raised by `create_relation()` when a requested relation cannot be accepted.

    In practice this happens only for a structurally invalid request (unknown
    kind, missing participant, self-relation, or a conflicting duplicate
    identity in `RelationCollection.add`/`create_relation_batch`); it never
    happens because of the relation's textual notes or metadata content.
    """


@dataclass
class RelationRequest:
    """Represents one explicit caller request to create a `KnowledgeRelation`.

    For symmetric kinds (`DIFFERENCE`, `CONFLICT`) `material_a`/`material_b`
    order is irrelevant. For directional kinds (`GAP`, `TEMPORAL_EVOLUTION`)
    `material_a` is FROM and `material_b` is TO; the caller must supply that
    direction explicitly, since it is never inferred.
    """

    relation_kind: RelationKind
    material_a: str
    material_b: str
    basis: RelationBasis = RelationBasis.EXPLICIT
    notes: str | None = None
    evidence_refs: tuple[str, ...] = ()
    metadata: dict = field(default_factory=dict)


@dataclass
class RelationRejection:
    """Represents one rejected batch item: an invalid request or conflicting duplicate identity."""

    index: int
    reason: str


@dataclass
class RelationBatchResult:
    """Represents the outcome of `create_relation_batch`: accepted relations and isolated rejections.

    `accepted` preserves original input order (with exact duplicates
    collapsed per the documented idempotent policy); `rejected` preserves the
    original index of each rejected item. No accepted item is ever dropped
    because another item in the same batch was rejected.
    """

    accepted: list[KnowledgeRelation] = field(default_factory=list)
    rejected: list[RelationRejection] = field(default_factory=list)


class RelationService:
    """Deterministic boundary that creates a `KnowledgeRelation` only from an explicit request.

    Stateless: every call is independent and produces the same output for the
    same request fields. Never inspects material prose, `SourceType`,
    `KnowledgeNature`, or `TemporalState` to decide a relation's kind, and
    never mutates any participant record.
    """

    def create_relation(self, request: RelationRequest) -> KnowledgeRelation:
        """Creates one `KnowledgeRelation` from an explicit `RelationRequest`.

        Raises `RelationRejectedError` for an unknown kind, a missing/blank
        participant, or a self-relation (same id on both sides).
        """
        try:
            directionality = directionality_for(request.relation_kind)
        except RelationValidationError as exc:
            raise RelationRejectedError(str(exc)) from exc

        material_a, material_b = request.material_a, request.material_b
        if not material_a or not material_a.strip() or not material_b or not material_b.strip():
            raise RelationRejectedError("participant_id_required")
        if material_a == material_b:
            raise RelationRejectedError("self_relation_rejected")

        participants = canonical_participants(request.relation_kind, material_a, material_b)
        relation = KnowledgeRelation(
            relation_id=new_relation_id(request.relation_kind, participants),
            relation_kind=request.relation_kind,
            directionality=directionality,
            participants=participants,
            basis=request.basis,
            notes=sanitize_text(request.notes) if request.notes else None,
            evidence_refs=tuple(request.evidence_refs),
            metadata=sanitize_data(dict(request.metadata)),
        )
        try:
            relation.validate()
        except RelationValidationError as exc:
            raise RelationRejectedError(str(exc)) from exc
        return relation

    def create_relation_batch(self, requests: list[RelationRequest]) -> RelationBatchResult:
        """Creates each relation independently, isolating failures.

        Duplicate policy: a repeated identical relation (same `relation_id`
        and same attribution fields) is an idempotent no-op (only the first
        is kept in `accepted`); a repeated `relation_id` with *different*
        attribution fields is rejected as a conflicting duplicate identity
        rather than silently overwritten.
        """
        result = RelationBatchResult()
        seen: dict[str, KnowledgeRelation] = {}
        for index, request in enumerate(requests):
            try:
                relation = self.create_relation(request)
            except RelationRejectedError as exc:
                result.rejected.append(RelationRejection(index=index, reason=str(exc)))
                continue

            existing = seen.get(relation.relation_id)
            if existing is not None:
                if existing != relation:
                    result.rejected.append(RelationRejection(
                        index=index, reason=f"conflicting_duplicate_relation_id:{relation.relation_id}"))
                continue  # exact duplicate: idempotent no-op

            seen[relation.relation_id] = relation
            result.accepted.append(relation)
        return result


class RelationCollection:
    """Deterministic in-memory relation repository. No external storage is used.

    Preserves insertion order for `list()`/`by_kind()`; `add()` enforces the
    same conflicting-duplicate-identity policy as `create_relation_batch`.
    """

    def __init__(self) -> None:
        self._relations: dict[str, KnowledgeRelation] = {}

    def add(self, relation: KnowledgeRelation) -> None:
        """Adds a validated relation. Exact duplicates are idempotent; conflicting duplicates are rejected."""
        relation.validate()
        existing = self._relations.get(relation.relation_id)
        if existing is not None and existing != relation:
            raise RelationRejectedError(f"conflicting_duplicate_relation_id:{relation.relation_id}")
        self._relations[relation.relation_id] = relation

    def get(self, relation_id: str) -> KnowledgeRelation | None:
        """Returns the relation with `relation_id`, or `None` if absent."""
        return self._relations.get(relation_id)

    def list(self) -> list[KnowledgeRelation]:
        """Returns every stored relation in insertion order."""
        return list(self._relations.values())

    def by_kind(self, relation_kind: RelationKind) -> list[KnowledgeRelation]:
        """Returns every stored relation of `relation_kind`, in insertion order."""
        return [relation for relation in self._relations.values() if relation.relation_kind == relation_kind]

    def relations_for(self, material_id: str) -> list[KnowledgeRelation]:
        """Returns every stored relation that references `material_id` as a participant, in insertion order."""
        return [relation for relation in self._relations.values() if material_id in relation.participants]


def correlate_with_classification(
    relation: KnowledgeRelation,
    classification_by_material_id: dict[str, ClassificationRecord] | None = None,
) -> dict:
    """Returns a read-only, non-mutating correlation view of a relation and optional R5 classifications.

    Never merges or mutates any `ClassificationRecord`; classification is
    entirely optional, since a relation can exist over unclassified material.
    Correlation is by `material_id` lookup only — it never selects or filters
    which relation kind is valid for which `KnowledgeNature`.
    """
    classification_by_material_id = classification_by_material_id or {}
    return {
        "relation_id": relation.relation_id,
        "relation_kind": relation.relation_kind.value,
        "participants": {
            participant_id: (
                classification_by_material_id[participant_id].selected_nature.value
                if participant_id in classification_by_material_id
                and classification_by_material_id[participant_id].selected_nature is not None
                else None
            )
            for participant_id in relation.participants
        },
    }


def correlate_with_temporal(
    relation: KnowledgeRelation,
    temporal_by_material_id: dict[str, TemporalPlacement] | None = None,
) -> dict:
    """Returns a read-only, non-mutating correlation view of a relation and optional R6 temporal placements.

    Never merges or mutates any `TemporalPlacement`. This correlation is
    descriptive only: an `AS_IS`/`TO_BE` pairing visible here is never used to
    infer or change `relation.relation_kind`.
    """
    temporal_by_material_id = temporal_by_material_id or {}
    return {
        "relation_id": relation.relation_id,
        "relation_kind": relation.relation_kind.value,
        "participants": {
            participant_id: (
                temporal_by_material_id[participant_id].bucket.value
                if participant_id in temporal_by_material_id
                else None
            )
            for participant_id in relation.participants
        },
    }
