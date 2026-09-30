"""Normalized Evidence Core entities that do not already exist as a V4.3
dataclass (V5.1 R1 SS2-3): `SourceArtifact`, `Solution`, `Component`,
`ExternalDependency`, `DataObject`, `UnresolvedBoundary`, `CallIdentity`,
`Instantiation`, `ScanSummary`.

Every entity that wraps an existing legacy record carries `extensions`: the
**complete, untouched** original dict, namespaced under whichever adapter
produced it. Nothing is dropped or renamed inside it. This is what makes the
legacy compatibility projection (`projection.py`) trivially lossless -- the
projector never has to reconstruct a legacy shape from scratch, it returns
exactly what is already sitting in `extensions`, unmodified, in the original
order.

**Technology Adapter boundary (V5.1 R2.1-05):** `adapter_id`/`adapter_version`
are per-instance fields, supplied by whoever constructs the entity (the
adapter/builder doing the wrapping) -- never a module-level constant baked
into this "core" module. A core entity module that hardcoded one fixed
adapter id would make it structurally impossible for V5.4 to compose a
different adapter (e.g. a language adapter paired with a different database
adapter, which R1's Adapter Contract already anticipates) without editing
this file; requiring the id at construction time closes that gap now,
without implementing any second adapter yet.

**Provenance (V5.1 R3.2 D-4):** every entity below except `SourceArtifact`
(the root of provenance itself, per V5.0 R3's own exception) carries
`provenance: list[EvidenceReference]`, built in `builder.py` from evidence
already present in the wrapped legacy record -- never fabricated. See
`invariants.py::validate_evidence` for the production gate that requires
each of these lists to be non-empty and to resolve (I-4/I-5).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .reference import EvidenceReference

EVIDENCE_SCHEMA_VERSION = "1.0"


def _adapter_dict(adapter_id: str, adapter_version: str) -> dict:
    return {"id": adapter_id, "version": adapter_version}


def is_sha256_hex(value: object) -> bool:
    """True for a SHA-256 hex digest as `hashlib` renders it (64 lowercase hex chars)."""
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)


@dataclass
class SourceArtifact:
    """CORE_ENTITY. Identity: `SRC-`+SHA-256(path). `sha256` is new
    information V4.3 never had (only `size`): the SHA-256 of the artifact's
    real content, **mandatory** (V5.1 R3.1 D-2) -- measured primary
    evidence, never `None`, empty or fabricated. Validated on construction.
    """

    id: str
    path: str
    size_bytes: int
    artifact_kind: str
    adapter_id: str
    adapter_version: str
    sha256: str
    extensions: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not is_sha256_hex(self.sha256):
            raise ValueError(f"SourceArtifact {self.path!r}: sha256 must be 64 lowercase hex chars, got {self.sha256!r}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": "SourceArtifact",
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "path": self.path,
            "size_bytes": self.size_bytes,
            "artifact_kind": self.artifact_kind,
            "sha256": self.sha256,
            "adapter": _adapter_dict(self.adapter_id, self.adapter_version),
            "extensions": {self.adapter_id: self.extensions},
        }


@dataclass
class Solution:
    """CORE_RELATION (grouping) + ADAPTER_EXTENSION (`.sln`-specific
    fields). Identity: `SOL-`+SHA-256(path) -- V5.1 R2 SS3.1 resolution of
    R1's open decision (see the R2 result document for the justification: no
    consumer references a `Solution` id today, so minting one fresh carries
    no compatibility risk, and the pattern mirrors `Project`/`PRJ-` exactly).
    """

    id: str
    name: str
    path: str
    adapter_id: str
    adapter_version: str
    project_refs: list[str] = field(default_factory=list)
    provenance: list[EvidenceReference] = field(default_factory=list)
    extensions: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": "Solution",
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "name": self.name,
            "path": self.path,
            "project_refs": self.project_refs,
            "provenance": [ref.to_dict() for ref in self.provenance],
            "adapter": _adapter_dict(self.adapter_id, self.adapter_version),
            "extensions": {self.adapter_id: self.extensions},
        }


@dataclass
class Component:
    """CORE_ENTITY (name/component_kind/source_ref/parent_id/members) +
    ADAPTER_EXTENSION (namespace/modifiers/inherits/implements for VB.NET;
    directives/codebehind/... for WebForms). Fuses what V4.3 keeps as two
    separate, unrelated collections (`Symbol`, `WebForm`) into one neutral
    entity, per V5.1 R1 SS2 (`Component`).

    Identity: `CMP-`+SHA-256(component_kind, source_ref, name,
    discriminator). `discriminator` is the ordinal position (0-based) of
    this record among every other record sharing the exact same
    `(source_ref, name, component_kind)` triple, counted in the same
    deterministic order the source list already has -- this is the
    resolution of R1's open decision SS3.3, measured against the one real
    duplicate the target repository has (`cc\\cc\\ccTMP.vb`/`ccRma1`,
    `class`, 2 records).
    """

    id: str
    name: str
    component_kind: str
    project_id: str | None
    source_ref: str | None
    state: str
    adapter_id: str
    adapter_version: str
    discriminator: int = 0
    parent_id: str | None = None
    members: list = field(default_factory=list)
    provenance: list[EvidenceReference] = field(default_factory=list)
    extensions: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": "Component",
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "name": self.name,
            "component_kind": self.component_kind,
            "project_id": self.project_id,
            "source_ref": self.source_ref,
            "state": self.state,
            "discriminator": self.discriminator,
            "parent_id": self.parent_id,
            "members": self.members,
            "provenance": [ref.to_dict() for ref in self.provenance],
            "adapter": _adapter_dict(self.adapter_id, self.adapter_version),
            "extensions": {self.adapter_id: self.extensions},
        }


@dataclass
class ExternalDependency:
    """CORE_ENTITY. Identity: `XDP-`+SHA-256(dependency_kind, source,
    target, stable metadata, duplicate_ordinal). Covers both assembly
    references (`Project -> DLL` edges in V4.3's `dependencies.json`) and the
    `CONN-` connection targets V5.1 R2 SS3.4 resolves (measured on real IST:
    only 1 distinct connection identifier across the whole target).

    `duplicate_ordinal` (V5.1 R3.1 D-1): 0-based ordinal among the
    dependencies of one source sharing the same base tuple -- same scheme as
    `CallIdentity.duplicate_ordinal`. Distinguishes repeated occurrences
    (e.g. several `<Reference>` elements with an empty `Include` in one
    project file) without any global position, timestamp or randomness.
    """

    id: str
    name: str
    dependency_kind: str
    adapter_id: str
    adapter_version: str
    version: str | None = None
    source_ref: str | None = None
    legacy_ref: str | None = None
    duplicate_ordinal: int = 0
    provenance: list[EvidenceReference] = field(default_factory=list)
    extensions: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": "ExternalDependency",
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "name": self.name,
            "dependency_kind": self.dependency_kind,
            "version": self.version,
            "source_ref": self.source_ref,
            "legacy_ref": self.legacy_ref,
            "duplicate_ordinal": self.duplicate_ordinal,
            "provenance": [ref.to_dict() for ref in self.provenance],
            "adapter": _adapter_dict(self.adapter_id, self.adapter_version),
            "extensions": {self.adapter_id: self.extensions},
        }


@dataclass
class DataObject:
    """CORE_ENTITY. Wraps a stored procedure (`SP-`, preserved) or a SQL
    operation (`SQL-`, preserved) -- the terminal object of a `DataOperation`.
    """

    id: str
    object_kind: str  # "stored_procedure" | "sql"
    name: str
    state: str
    adapter_id: str
    adapter_version: str
    provenance: list[EvidenceReference] = field(default_factory=list)
    extensions: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": "DataObject",
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "object_kind": self.object_kind,
            "name": self.name,
            "state": self.state,
            "provenance": [ref.to_dict() for ref in self.provenance],
            "adapter": _adapter_dict(self.adapter_id, self.adapter_version),
            "extensions": {self.adapter_id: self.extensions},
        }


@dataclass
class UnresolvedBoundary:
    """CORE_ENTITY. Identity derived stably from `path_id` (+
    `boundary_target`/`reason_code` when more than one boundary shares a
    path) -- never `UNRES-` (V5.0 DR-R2-01). `state` is always
    `"unresolved"`: this entity exists specifically to make the absence of
    a resolution a first-class, queryable fact, never a value that can
    silently become `"confirmed"`. No adapter/extensions fields: a boundary
    is a structural fact about the flow resolver's own graph, not
    technology-specific content, so it carries nothing an adapter produced.
    """

    id: str
    path_id: str
    boundary_target: str
    reason_code: str
    state: str = "unresolved"
    candidates: list = field(default_factory=list)
    provenance: list[EvidenceReference] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.state != "unresolved":
            raise ValueError(f"UnresolvedBoundary.state must always be 'unresolved', got {self.state!r}")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": "UnresolvedBoundary",
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "path_id": self.path_id,
            "boundary_target": self.boundary_target,
            "reason_code": self.reason_code,
            "state": self.state,
            "candidates": self.candidates,
            "provenance": [ref.to_dict() for ref in self.provenance],
        }


@dataclass
class CallIdentity:
    """A side-table entry for one `Call` record's V5 identity -- **not**
    embedded into the original `calls.json` record (that would contaminate
    the legacy projection; see `builder.py`). Identity: `CAL-`+SHA-256(
    source_artifact, containing_symbol, line, expression, resolved_target,
    duplicate_ordinal) -- V5.1 R2 SS4.1's corrected, insertion-stable
    formula. `legacy_ref` preserves the transient poly33 `CALL-` V4.3 never
    persists.
    """

    id: str
    legacy_ref: str
    source_artifact: str
    containing_symbol: tuple
    line: int | None
    expression: str
    resolved_target: str | None
    duplicate_ordinal: int
    state: str
    provenance: list[EvidenceReference] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": "Call",
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "legacy_ref": self.legacy_ref,
            "source_artifact": self.source_artifact,
            "containing_symbol": list(self.containing_symbol),
            "line": self.line,
            "expression": self.expression,
            "resolved_target": self.resolved_target,
            "duplicate_ordinal": self.duplicate_ordinal,
            "state": self.state,
            "provenance": [ref.to_dict() for ref in self.provenance],
        }


@dataclass
class Instantiation:
    """CORE_ENTITY (V5.1 R2.1-04: materialized as its own partition; R1 had
    left it embedded inside `calls.json`'s per-file `instantiations[]`).

    No canonical V5 identity, per R1's contract: an `Instantiation` is a
    child, positional fact about its `SourceArtifact` (like `DataParameter`
    is a child of its `DataOperation`), not an entity anything else
    references by id. Traceability instead comes from `source_artifact` +
    `position` (the 0-based ordinal of this record within its own file's
    `instantiations[]`, in the deterministic order the extractor already
    emits -- never a global counter across files).
    """

    source_artifact: str
    position: int
    type_name: str
    variable_name: str | None
    containing_symbol: tuple
    resolved_type: str | None
    state: str
    adapter_id: str
    adapter_version: str
    provenance: list[EvidenceReference] = field(default_factory=list)
    extensions: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "kind": "Instantiation",
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "source_artifact": self.source_artifact,
            "position": self.position,
            "type_name": self.type_name,
            "variable_name": self.variable_name,
            "containing_symbol": list(self.containing_symbol),
            "resolved_type": self.resolved_type,
            "state": self.state,
            "provenance": [ref.to_dict() for ref in self.provenance],
            "adapter": _adapter_dict(self.adapter_id, self.adapter_version),
            "extensions": {self.adapter_id: self.extensions},
        }


@dataclass
class ScanSummary:
    """DERIVED_PROJECTION. `duration_seconds` is deliberately excluded --
    LEGACY_ONLY, outside `evidence/`, per D-01 (R0 confirmed it is the only
    field that differs between two equivalent runs of the same input).
    """

    root: str
    total_files: int
    by_type: dict
    ignored: list

    def to_dict(self) -> dict:
        return {
            "kind": "ScanSummary",
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "root": self.root,
            "total_files": self.total_files,
            "by_type": self.by_type,
            "ignored": self.ignored,
        }
