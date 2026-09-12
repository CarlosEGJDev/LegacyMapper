"""Deterministic knowledge-classification service (V4-R5).

Pipeline: `MaterialItem` (R4) + an explicitly supplied selection/candidate
set -> `ClassificationRecord`. No step infers meaning from prose, maps
`SourceType` to `KnowledgeNature` automatically, or creates a
`KnowledgeStatement`. No AI/provider call occurs anywhere in this module.
"""
from dataclasses import dataclass, field

from legacy_documenter.knowledge.classification.enums import ClassificationMethod, ClassificationStatus
from legacy_documenter.knowledge.classification.models import (
    ClassificationRecord,
    ClassificationValidationError,
    new_classification_id,
)
from legacy_documenter.knowledge.domain.enums import KnowledgeNature
from legacy_documenter.knowledge.domain.models import MaterialItem
from legacy_documenter.knowledge.input.contracts import SourceInputValidationError
from legacy_documenter.knowledge.input.normalization import validate_metadata
from legacy_documenter.utils.sanitizer import sanitize_text


class ClassificationRejectedError(ValueError):
    """Raised by `classify()` when a classification request cannot be accepted.

    The message is always built from sanitized, deterministic reason codes —
    never from raw rejected input.
    """


@dataclass
class ClassificationRequest:
    """Represents one caller-supplied classification request for a `MaterialItem`.

    Supply at most one of `selected_nature` or `candidate_natures`:

    * `selected_nature` only -> resolves to `CLASSIFIED`.
    * `candidate_natures` only (>=2 distinct) -> resolves to `AMBIGUOUS`.
    * neither -> resolves to `UNCLASSIFIED`.

    Supplying both is rejected as a contradictory request (a classification
    cannot simultaneously be resolved and left as multiple open candidates).
    """

    material: MaterialItem
    selected_nature: KnowledgeNature | None = None
    candidate_natures: list[KnowledgeNature] | None = None
    rationale: str | None = None
    classified_by: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ClassificationRejection:
    """Represents one rejected batch classification request, with a sanitized, deterministic reason."""

    index: int
    reason: str


@dataclass
class ClassificationBatchResult:
    """Represents the outcome of `classify_batch`: accepted records and isolated rejections.

    Both lists preserve the original input order. No accepted item is ever
    silently dropped because another item in the same batch was rejected.
    """

    accepted: list[ClassificationRecord] = field(default_factory=list)
    rejected: list[ClassificationRejection] = field(default_factory=list)

    @property
    def accepted_count(self) -> int:
        """Returns the number of accepted records."""
        return len(self.accepted)

    @property
    def rejected_count(self) -> int:
        """Returns the number of rejected requests."""
        return len(self.rejected)


def _canonicalize_candidates(candidates: list[KnowledgeNature] | None) -> tuple[KnowledgeNature, ...]:
    if not candidates:
        return ()
    for candidate in candidates:
        if not isinstance(candidate, KnowledgeNature):
            raise ClassificationRejectedError(f"invalid_candidate_nature:{candidate!r}")
    unique = sorted(set(candidates), key=lambda nature: nature.value)
    return tuple(unique)


def _sanitize_metadata(metadata: dict) -> dict:
    try:
        return validate_metadata(metadata)
    except SourceInputValidationError as exc:
        raise ClassificationRejectedError(str(exc)) from exc


def _sanitize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed = value.strip()
    return sanitize_text(trimmed) if trimmed else None


class KnowledgeClassificationService:
    """Deterministic boundary that turns an explicit classification request into a `ClassificationRecord`.

    Stateless: every call is independent and produces the same output for
    the same normalized input.
    """

    def classify(self, request: ClassificationRequest) -> ClassificationRecord:
        """Classifies one `MaterialItem`, returning its `ClassificationRecord`.

        Raises `ClassificationRejectedError` if the request is structurally
        invalid (e.g. both `selected_nature` and `candidate_natures`
        supplied, an unknown enum value, or fewer than two distinct
        candidates for an ambiguous request).
        """
        if request.selected_nature is not None and request.candidate_natures:
            raise ClassificationRejectedError("selected_nature_and_candidate_natures_are_mutually_exclusive")

        rationale = _sanitize_optional_text(request.rationale)
        classified_by = _sanitize_optional_text(request.classified_by)
        metadata = _sanitize_metadata(request.metadata)

        if request.selected_nature is not None:
            if not isinstance(request.selected_nature, KnowledgeNature):
                raise ClassificationRejectedError(f"invalid_selected_nature:{request.selected_nature!r}")
            status = ClassificationStatus.CLASSIFIED
            method = ClassificationMethod.EXPLICIT
            selected_nature = request.selected_nature
            candidate_natures: tuple[KnowledgeNature, ...] = ()
        elif request.candidate_natures:
            candidate_natures = _canonicalize_candidates(request.candidate_natures)
            if len(candidate_natures) < 2:
                raise ClassificationRejectedError("ambiguous_requires_at_least_two_distinct_candidates")
            status = ClassificationStatus.AMBIGUOUS
            method = ClassificationMethod.EXPLICIT
            selected_nature = None
        else:
            status = ClassificationStatus.UNCLASSIFIED
            method = ClassificationMethod.UNRESOLVED
            selected_nature = None
            candidate_natures = ()

        classification_id = new_classification_id(
            request.material.material_id, status, selected_nature, candidate_natures, method
        )
        record = ClassificationRecord(
            classification_id=classification_id,
            material_id=request.material.material_id,
            source_type=request.material.source_type,
            status=status,
            classification_method=method,
            selected_nature=selected_nature,
            candidate_natures=candidate_natures,
            rationale=rationale,
            classified_by=classified_by,
            metadata=metadata,
        )
        try:
            record.validate()
        except ClassificationValidationError as exc:
            raise ClassificationRejectedError(str(exc)) from exc
        return record

    def classify_batch(self, requests: list[ClassificationRequest]) -> ClassificationBatchResult:
        """Classifies each request independently, isolating failures.

        One invalid request never removes a valid result from `accepted`;
        both lists preserve the original input order.
        """
        result = ClassificationBatchResult()
        for index, request in enumerate(requests):
            try:
                record = self.classify(request)
            except ClassificationRejectedError as exc:
                result.rejected.append(ClassificationRejection(index=index, reason=sanitize_text(str(exc))))
                continue
            result.accepted.append(record)
        return result
