"""Source-neutral classification record for the V4 knowledge-classification layer.

`ClassificationRecord` links back to an R4 `MaterialItem` by `material_id`
only (no payload duplication) and preserves the material's original
`SourceType` without mutating it. It never carries approval, canonical, or
authoritative-truth semantics.
"""
from dataclasses import dataclass, field

from legacy_documenter.documentation.contracts import stable_id
from legacy_documenter.knowledge.classification.enums import ClassificationMethod, ClassificationStatus
from legacy_documenter.knowledge.domain.enums import KnowledgeNature, SourceType


class ClassificationValidationError(ValueError):
    """Raised when a `ClassificationRecord` violates its structural contract."""


@dataclass
class ClassificationRecord:
    """Represents one classification decision (or explicit non-decision) about a `MaterialItem`.

    Invariants enforced by `validate()`:

    * `CLASSIFIED` requires exactly one `selected_nature` and no `candidate_natures`.
    * `UNCLASSIFIED` requires `selected_nature is None` and no `candidate_natures`.
    * `AMBIGUOUS` requires `selected_nature is None` and at least two distinct `candidate_natures`.

    `candidate_natures` is always stored as a canonically sorted tuple
    (by `.value`) with no duplicates, so two classifications built from the
    same candidate set in different input orders are structurally identical.
    """

    classification_id: str
    material_id: str
    source_type: SourceType
    status: ClassificationStatus
    classification_method: ClassificationMethod
    selected_nature: KnowledgeNature | None = None
    candidate_natures: tuple[KnowledgeNature, ...] = ()
    rationale: str | None = None
    classified_by: str | None = None
    metadata: dict = field(default_factory=dict)

    def validate(self) -> bool:
        """Performs the full structural contract check for a `ClassificationRecord`."""
        if not self.classification_id or not self.classification_id.strip():
            raise ClassificationValidationError("classification_id_required")
        if not self.material_id or not self.material_id.strip():
            raise ClassificationValidationError("material_id_required")
        if not isinstance(self.source_type, SourceType):
            raise ClassificationValidationError("invalid_source_type")
        if not isinstance(self.status, ClassificationStatus):
            raise ClassificationValidationError("invalid_classification_status")
        if not isinstance(self.classification_method, ClassificationMethod):
            raise ClassificationValidationError("invalid_classification_method")
        if self.selected_nature is not None and not isinstance(self.selected_nature, KnowledgeNature):
            raise ClassificationValidationError("invalid_selected_nature")

        candidate_values = [c.value for c in self.candidate_natures]
        if len(candidate_values) != len(set(candidate_values)):
            raise ClassificationValidationError("duplicate_candidate_natures")
        for candidate in self.candidate_natures:
            if not isinstance(candidate, KnowledgeNature):
                raise ClassificationValidationError("invalid_candidate_nature")

        if self.status == ClassificationStatus.CLASSIFIED:
            if self.selected_nature is None:
                raise ClassificationValidationError("classified_requires_selected_nature")
            if self.candidate_natures:
                raise ClassificationValidationError("classified_must_not_carry_candidate_natures")
        elif self.status == ClassificationStatus.UNCLASSIFIED:
            if self.selected_nature is not None:
                raise ClassificationValidationError("unclassified_must_not_carry_selected_nature")
            if self.candidate_natures:
                raise ClassificationValidationError("unclassified_must_not_carry_candidate_natures")
        elif self.status == ClassificationStatus.AMBIGUOUS:
            if self.selected_nature is not None:
                raise ClassificationValidationError("ambiguous_must_not_carry_selected_nature")
            if len(self.candidate_natures) < 2:
                raise ClassificationValidationError("ambiguous_requires_at_least_two_distinct_candidates")

        return True


def new_classification_id(
    material_id: str,
    status: ClassificationStatus,
    selected_nature: KnowledgeNature | None,
    candidate_natures: tuple[KnowledgeNature, ...],
    classification_method: ClassificationMethod,
) -> str:
    """Derives a stable `CLS-` id from the semantically load-bearing classification fields.

    Reuses the existing V3 `stable_id` hashing contract. Deliberately excludes
    `rationale`, `classified_by`, and `metadata` from identity: those are
    explanatory/attribution data, not part of what makes two classifications
    the same decision. Equivalent normalized classification semantics
    (same material, status, selection/candidates, method) always produce the
    same id; it never depends on current time, randomness, or object identity.
    """
    return stable_id(
        "CLS",
        material_id,
        status.value,
        selected_nature.value if selected_nature is not None else None,
        tuple(c.value for c in candidate_natures),
        classification_method.value,
    )
