"""`EvidenceReference` -- the tagged union defined by V5.0 DR-R2-04 / R3 /
V5.1 R1 SS6.

Four `ref_type`s (`entity`, `source`, `source_span`, `textual`) plus an
optional `legacy_ref` string. A reference is never allowed to silently
become "valid" when it is not: `resolve_against` always either succeeds or
raises `BrokenEvidenceReferenceError` -- there is no third, ambiguous
outcome.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

REF_TYPES = ("entity", "source", "source_span", "textual")


class BrokenEvidenceReferenceError(ValueError):
    """Raised when an `EvidenceReference` cannot be resolved against a store.

    Never caught and silently downgraded to a warning by this package --
    callers that want to tolerate broken references (there is no such
    caller in V5.1) must catch this explicitly and decide what "tolerate"
    means themselves.
    """


@dataclass(frozen=True)
class EvidenceReference:
    """A tagged union over the four reference shapes V4.3's real evidence
    already needs (V5.1 R1 SS6, grounded in R2's `EVIDENCE REFERENCE
    VALIDATION` measurement): an id of another normalized entity, a source
    location with an optional fragment, a reserved span for a future
    adapter that produces real columns, or a textual citation when neither
    an id nor a precise location exists. `legacy_ref` is available on any
    of the four, to preserve `CALL-`/`PAR-`/`UNRES-` without ever treating
    them as this reference's identity.
    """

    ref_type: str
    entity_kind: str | None = None
    entity_id: str | None = None
    source_id: str | None = None
    line: int | None = None
    excerpt: str | None = None
    start_line: int | None = None
    start_column: int | None = None
    end_line: int | None = None
    end_column: int | None = None
    text: str | None = None
    origin: str | None = None
    legacy_ref: str | None = None

    def __post_init__(self) -> None:
        if self.ref_type not in REF_TYPES:
            raise ValueError(f"invalid ref_type: {self.ref_type!r}, must be one of {REF_TYPES}")
        if self.ref_type == "entity" and not (self.entity_kind and self.entity_id):
            raise ValueError("ref_type='entity' requires both entity_kind and entity_id")
        if self.ref_type in ("source", "source_span") and not self.source_id:
            raise ValueError(f"ref_type={self.ref_type!r} requires source_id")
        if self.ref_type == "textual" and not self.text:
            raise ValueError("ref_type='textual' requires text")

    @classmethod
    def entity(cls, entity_kind: str, entity_id: str, *, legacy_ref: str | None = None) -> "EvidenceReference":
        return cls(ref_type="entity", entity_kind=entity_kind, entity_id=entity_id, legacy_ref=legacy_ref)

    @classmethod
    def source(cls, source_id: str, *, line: int | None = None, excerpt: str | None = None, legacy_ref: str | None = None) -> "EvidenceReference":
        return cls(ref_type="source", source_id=source_id, line=line, excerpt=excerpt, legacy_ref=legacy_ref)

    @classmethod
    def source_span(
        cls, source_id: str, *, start_line: int, start_column: int, end_line: int, end_column: int,
        excerpt: str | None = None, legacy_ref: str | None = None,
    ) -> "EvidenceReference":
        return cls(
            ref_type="source_span", source_id=source_id, start_line=start_line, start_column=start_column,
            end_line=end_line, end_column=end_column, excerpt=excerpt, legacy_ref=legacy_ref,
        )

    @classmethod
    def textual(cls, text: str, *, origin: str | None = None, legacy_ref: str | None = None) -> "EvidenceReference":
        return cls(ref_type="textual", text=text, origin=origin, legacy_ref=legacy_ref)

    def to_dict(self) -> dict:
        return {key: value for key, value in asdict(self).items() if value is not None}


class EvidenceReferenceStore:
    """The minimal lookup surface `resolve_against` needs: "does this
    entity id exist" and "does this source id exist". A thin adapter over
    whatever in-memory index the caller already has -- this class holds no
    data of its own beyond the two lookup sets given to it.
    """

    def __init__(self, entity_ids: set[tuple[str, str]], source_ids: set[str]) -> None:
        self._entity_ids = entity_ids
        self._source_ids = source_ids

    def has_entity(self, entity_kind: str, entity_id: str) -> bool:
        return (entity_kind, entity_id) in self._entity_ids

    def has_source(self, source_id: str) -> bool:
        return source_id in self._source_ids


def resolve_against(ref: EvidenceReference, store: EvidenceReferenceStore) -> None:
    """Verifies `ref` resolves against `store`; raises
    `BrokenEvidenceReferenceError` otherwise. `textual` references have no
    external referent to verify and always pass (they are exactly the
    reference shape reserved for evidence with no id and no precise
    location -- rejecting them would contradict their own purpose).
    """
    if ref.ref_type == "entity":
        if not store.has_entity(ref.entity_kind, ref.entity_id):
            raise BrokenEvidenceReferenceError(f"entity reference does not resolve: {ref.entity_kind}:{ref.entity_id}")
    elif ref.ref_type in ("source", "source_span"):
        if not store.has_source(ref.source_id):
            raise BrokenEvidenceReferenceError(f"source reference does not resolve: {ref.source_id}")
