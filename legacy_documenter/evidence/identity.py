"""Identity primitives for the Normalized Evidence Core (V5.1 R2).

Two distinct id schemes coexist, by design (V5.0 D-02, V5.1 R1 SS4):

* `sha256_id` -- full SHA-256 over a canonical JSON encoding of the identity
  parts. This is how every *new* V5 identity is minted (`PRJ-`, `CMP-`,
  `XDP-`, `CAL-`, `SOL-`, the derived identity of `UnresolvedBoundary`). It is
  also exactly how V4.3 already derives `PATH-`
  (`legacy_documenter/analysis/flow_resolver.py::_path_id`) -- the one
  precedent V4.3 already has for a full-SHA-256 id, reused here rather than
  invented.
* `poly33_id` -- a byte-identical reimplementation of the legacy
  `_stable_id` helper duplicated across `analysis/flow_resolver.py`,
  `analysis/database_resolver.py` and `analysis/web_entry_resolver.py`. It
  exists here only to *recompute or validate* ids that legacy code produces
  (`EP-`, `EVB-`, `FLOW-`, `DAO-`, `SP-`, `SQL-`, and the transient/unpersisted
  `CALL-`/`UNRES-`), never to mint a new V5 identity -- new identities always
  use `sha256_id`.

`detect_collisions` implements the `id_unique_per_kind` invariant (I-1):
the same id on more than one record of the same entity kind is a collision,
whatever the records' content (V5.1 R3.1 D-1 correction).
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass


def sha256_id(prefix: str, *parts: object) -> str:
    """Full-SHA-256 identity: `{prefix}-{64 hex chars}`.

    `parts` are encoded as a canonical JSON array (`ensure_ascii=False`,
    compact separators, insertion order preserved -- order is part of the
    identity's own semantics and must never be silently reordered by the
    caller) and hashed whole.
    """
    canonical = json.dumps(list(parts), ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"{prefix}-{digest}"


_REPOSITORY_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def normalize_repository_id(value: object) -> str | None:
    """A declared logical repository id, or `None` (undeclared). Never a path: no separators, spaces or control characters.

    This is a *declared name* chosen by a person (V5.9 R2), independent of where the repository lives on disk, of the
    machine and of the user, so moving or copying the same repository never changes any identity derived from it.
    """
    if value is None:
        return None
    if not isinstance(value, str) or not _REPOSITORY_ID_RE.match(value):
        raise ValueError("repository_id must be 1-128 chars of letters, digits and . _ : - (no path separators or spaces)")
    return value


def source_artifact_id(path: str, repository_id: str | None = None) -> str:
    """`SRC-` identity of a source file.

    Undeclared repository (default): `sha256_id("SRC", path)` exactly as V5.1 fixed it (IDENTITY_COMPATIBLE, every existing
    baseline keeps its ids). Declared repository: `sha256_id("SRC", repository_id, path)`, so the same relative path in two
    different logical repositories can never share an id. `path` is the repository-relative POSIX path.
    """
    posix = (path or "").replace("\\", "/")
    rid = normalize_repository_id(repository_id)
    return sha256_id("SRC", posix) if rid is None else sha256_id("SRC", rid, posix)


def poly33_id(prefix: str, *parts: object) -> str:
    """Legacy poly33 identity: `{prefix}-{10 digit zero-padded value}`.

    Byte-identical to the `_stable_id` helper already duplicated in
    `flow_resolver.py`/`database_resolver.py`/`web_entry_resolver.py`. Used
    here only to recompute a legacy id for `legacy_ref` purposes or to
    cross-validate a persisted legacy id -- never to mint a V5 identity.
    """
    raw = "|".join("" if part is None else str(part) for part in parts)
    value = 0
    for char in raw:
        value = (value * 33 + ord(char)) % 1_000_000_007
    return f"{prefix}-{value:010d}"


@dataclass(frozen=True)
class Collision:
    """One id shared by two or more records of the same entity kind.
    `count` is the number of records carrying that id."""

    id: str
    count: int


def detect_duplicate_ids(ids: Iterable[object]) -> list[Collision]:
    """I-1 over a plain sequence of ids: every id seen more than once is a
    collision. Result sorted by `str(id)` for deterministic reporting."""
    counts = Counter(ids)
    return [Collision(id=key, count=count) for key, count in sorted(counts.items(), key=lambda item: str(item[0])) if count > 1]


def detect_collisions(records: list[dict], id_field: str = "id") -> list[Collision]:
    """Implements invariant I-1 (`id_unique_per_kind`).

    A collision is the same `id_field` value appearing on more than one
    record of the same kind -- **including byte-identical records** (V5.1
    R3.1 D-1: R2/R2.1 exempted exact duplicates, which hid 5 repeated `XDP-`
    ids / 31 extra records on real IST). A canonical id names exactly one
    record; two identical records under one id are still two records.
    """
    return detect_duplicate_ids(record.get(id_field) for record in records)


def collision_summary(collisions: list[Collision]) -> dict:
    """Reportable figures for a `detect_*` result: distinct duplicated ids,
    records carrying one of them, and records in excess of one per id."""
    return {
        "duplicate_ids": len(collisions),
        "records_involved": sum(c.count for c in collisions),
        "extra_records": sum(c.count - 1 for c in collisions),
    }


class DuplicateOrdinalAssigner:
    """Assigns a stable `duplicate_ordinal` to records sharing an identical
    base identity tuple (V5.1 R2 SS4.1 correction to R1's proposal).

    The ordinal is computed **only** from the relative order of records that
    share the exact same base tuple -- never from a global position counter
    over an unrelated superset of records. Concretely: `assign` is called
    once per record, in the deterministic overall iteration order (file
    order, then in-file order -- already the order V4.3 emits `calls[]` in,
    per D-01); it returns `0` for the first record ever seen with a given
    base tuple, `1` for the second, and so on. Because the ordinal only
    depends on the relative order *among records sharing that exact tuple*,
    inserting an unrelated record `X` anywhere in the overall sequence can
    never change the ordinal of any `A`/`B` pair that already existed --
    `X` simply never enters their group.
    """

    def __init__(self) -> None:
        self._next_ordinal: dict[tuple, int] = {}

    def assign(self, base_tuple: tuple) -> int:
        ordinal = self._next_ordinal.get(base_tuple, 0)
        self._next_ordinal[base_tuple] = ordinal + 1
        return ordinal
