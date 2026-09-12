"""Deterministic temporal-separation service (V4-R6).

Pipeline: `MaterialItem` (R4) -> `TemporalPlacement`, using only
`material.material_id` and `material.temporal_state`. No other field is
read, so no content, metadata, reference, or origin is inspected — R6 never
needs to, since it never infers anything from them.
"""
from dataclasses import dataclass, field

from legacy_documenter.knowledge.classification.models import ClassificationRecord
from legacy_documenter.knowledge.domain.models import MaterialItem
from legacy_documenter.knowledge.temporal.enums import TemporalBucket
from legacy_documenter.knowledge.temporal.models import (
    TemporalPlacement,
    TemporalValidationError,
    bucket_for,
    new_placement_id,
)


class TemporalSeparationRejectedError(ValueError):
    """Raised by `separate()` when a material cannot be temporally placed.

    In practice this only happens if `material.temporal_state` itself is
    structurally invalid; a valid `MaterialItem` is always placeable,
    including into `UNSPECIFIED`.
    """


@dataclass
class TemporalSeparationRejection:
    """Represents one rejected batch item: a conflicting duplicate identity or invalid material."""

    index: int
    reason: str


@dataclass
class TemporalSeparationResult:
    """Represents the outcome of `separate_batch`: accepted placements and isolated rejections.

    `accepted` preserves original input order (with exact duplicates
    collapsed per the documented idempotent policy); `rejected` preserves
    the original index of each rejected item. No accepted item is ever
    dropped because another item in the same batch was rejected.
    """

    accepted: list[TemporalPlacement] = field(default_factory=list)
    rejected: list[TemporalSeparationRejection] = field(default_factory=list)

    def by_bucket(self) -> dict[TemporalBucket, list[TemporalPlacement]]:
        """Groups accepted placements by bucket, preserving each bucket's relative input order."""
        grouped: dict[TemporalBucket, list[TemporalPlacement]] = {bucket: [] for bucket in TemporalBucket}
        for placement in self.accepted:
            grouped[placement.bucket].append(placement)
        return grouped


class TemporalSeparationService:
    """Deterministic boundary that places a `MaterialItem` into a `TemporalPlacement`.

    Stateless: every call is independent and produces the same output for
    the same `(material_id, temporal_state)` pair. Never mutates the
    `MaterialItem` it reads.
    """

    def separate(self, material: MaterialItem) -> TemporalPlacement:
        """Places one `MaterialItem`, returning its `TemporalPlacement`.

        Reads only `material.material_id` and `material.temporal_state`.
        """
        try:
            bucket = bucket_for(material.temporal_state)
        except TemporalValidationError as exc:
            raise TemporalSeparationRejectedError(str(exc)) from exc

        placement = TemporalPlacement(
            placement_id=new_placement_id(material.material_id, bucket),
            material_id=material.material_id,
            temporal_state=material.temporal_state,
            bucket=bucket,
        )
        try:
            placement.validate()
        except TemporalValidationError as exc:
            raise TemporalSeparationRejectedError(str(exc)) from exc
        return placement

    def separate_batch(self, materials: list[MaterialItem]) -> TemporalSeparationResult:
        """Separates each material independently, isolating failures.

        Duplicate policy: a repeated `material_id` with the *same*
        `temporal_state` is an idempotent no-op (only the first placement is
        kept in `accepted`); a repeated `material_id` with a *different*
        `temporal_state` is rejected as a conflicting duplicate identity
        rather than silently overwritten.
        """
        result = TemporalSeparationResult()
        seen: dict[str, TemporalPlacement] = {}
        for index, material in enumerate(materials):
            try:
                placement = self.separate(material)
            except TemporalSeparationRejectedError as exc:
                result.rejected.append(TemporalSeparationRejection(index=index, reason=str(exc)))
                continue

            existing = seen.get(placement.material_id)
            if existing is not None:
                if existing.temporal_state != placement.temporal_state:
                    result.rejected.append(TemporalSeparationRejection(
                        index=index, reason=f"conflicting_duplicate_material_id:{placement.material_id}"))
                continue  # exact duplicate: idempotent no-op

            seen[placement.material_id] = placement
            result.accepted.append(placement)
        return result


def correlate_with_classification(
    placement: TemporalPlacement, classification: ClassificationRecord | None = None
) -> dict:
    """Returns a read-only, non-mutating correlation view of a placement and an optional classification.

    Never merges or mutates either record; classification is entirely
    optional, since R6 must work for unclassified R4 material. Raises
    `ValueError` if a supplied classification's `material_id` does not match
    the placement's, since that would silently correlate unrelated records.
    """
    if classification is not None and classification.material_id != placement.material_id:
        raise ValueError("classification_material_id_does_not_match_placement")
    return {
        "material_id": placement.material_id,
        "temporal_state": placement.temporal_state.value if placement.temporal_state else None,
        "bucket": placement.bucket.value,
        "selected_nature": (
            classification.selected_nature.value
            if classification is not None and classification.selected_nature is not None
            else None
        ),
        "classification_status": classification.status.value if classification is not None else None,
    }
