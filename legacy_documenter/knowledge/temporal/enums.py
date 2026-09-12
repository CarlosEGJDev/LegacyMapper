"""Closed vocabulary for the V4 temporal-separation layer.

`TemporalBucket` is a projection-level concept only; it is NOT a fourth
`TemporalState` enum value. R1's `TemporalState` (`AS_IS`, `TO_BE`,
`HISTORICAL`) remains unchanged and unextended.
"""
from enum import Enum


class TemporalBucket(str, Enum):
    """Represents where a material structurally falls once separated by temporal state.

    Derived only from `MaterialItem.temporal_state` via a fixed, mechanical
    mapping (see `service.bucket_for`): `AS_IS`/`TO_BE`/`HISTORICAL` map to
    the identically named bucket, and `None` maps to `UNSPECIFIED`. This is
    structural projection, never semantic inference.
    """

    AS_IS = "AS_IS"
    TO_BE = "TO_BE"
    HISTORICAL = "HISTORICAL"
    UNSPECIFIED = "UNSPECIFIED"
