"""Temporal placement record for the V4 temporal-separation layer.

`TemporalPlacement` links back to an R4 `MaterialItem` by `material_id` only
and carries exactly one canonical temporal fact (`temporal_state`) plus its
mechanical projection (`bucket`) — never two independently editable temporal
truths.
"""
from dataclasses import dataclass

from legacy_documenter.documentation.contracts import stable_id
from legacy_documenter.knowledge.domain.enums import TemporalState
from legacy_documenter.knowledge.temporal.enums import TemporalBucket

_EXPECTED_BUCKET = {
    TemporalState.AS_IS: TemporalBucket.AS_IS,
    TemporalState.TO_BE: TemporalBucket.TO_BE,
    TemporalState.HISTORICAL: TemporalBucket.HISTORICAL,
    None: TemporalBucket.UNSPECIFIED,
}


class TemporalValidationError(ValueError):
    """Raised when a `TemporalPlacement` violates its structural contract."""


@dataclass
class TemporalPlacement:
    """Represents one material's deterministic temporal placement.

    `bucket` must always be the mechanical projection of `temporal_state`
    (see `_EXPECTED_BUCKET`); `validate()` rejects any placement where the
    two disagree, so a canonical temporal fact can never be duplicated into
    two independently editable states.
    """

    placement_id: str
    material_id: str
    temporal_state: TemporalState | None
    bucket: TemporalBucket

    def validate(self) -> bool:
        """Performs the full structural contract check for a `TemporalPlacement`."""
        if not self.placement_id or not self.placement_id.strip():
            raise TemporalValidationError("placement_id_required")
        if not self.material_id or not self.material_id.strip():
            raise TemporalValidationError("material_id_required")
        if self.temporal_state is not None and not isinstance(self.temporal_state, TemporalState):
            raise TemporalValidationError("invalid_temporal_state")
        if not isinstance(self.bucket, TemporalBucket):
            raise TemporalValidationError("invalid_bucket")
        if _EXPECTED_BUCKET[self.temporal_state] != self.bucket:
            raise TemporalValidationError("bucket_inconsistent_with_temporal_state")
        return True


def bucket_for(temporal_state: TemporalState | None) -> TemporalBucket:
    """Returns the fixed, mechanical `TemporalBucket` projection of `temporal_state`.

    `AS_IS`/`TO_BE`/`HISTORICAL` map to their identically named bucket;
    `None` maps to `UNSPECIFIED`. Structural projection only — no inference.
    """
    if temporal_state is not None and not isinstance(temporal_state, TemporalState):
        raise TemporalValidationError(f"invalid_temporal_state:{temporal_state!r}")
    return _EXPECTED_BUCKET[temporal_state]


def new_placement_id(material_id: str, bucket: TemporalBucket) -> str:
    """Derives a stable `TMP-` id from `material_id` and `bucket`, reusing the V3 `stable_id` contract.

    Equivalent placements (same material, same bucket) always produce the
    same id; it never depends on current time, randomness, or object identity.
    """
    return stable_id("TMP", material_id, bucket.value)
