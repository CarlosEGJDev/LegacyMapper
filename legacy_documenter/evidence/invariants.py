"""The 11 invariants fixed by `docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`
SS12 (I-1..I-11), implemented as callables `tests/` can invoke directly and
name identically to the contract, so a failing test maps to a contract
clause without translation.

Each check either passes silently or raises `InvariantViolation` with a
message naming the invariant and the offending record(s) -- never returns a
boolean that a caller might ignore.
"""
from __future__ import annotations

from .builder import NormalizedEvidence
from .entities import is_sha256_hex
from .identity import Collision, collision_summary, detect_collisions, detect_duplicate_ids
from .reference import BrokenEvidenceReferenceError, EvidenceReference, EvidenceReferenceStore, resolve_against

#: I-1: kinds whose id must be unique per V5.0 D-02 (preserved legacy ids +
#: the four new V5 ids + UnresolvedBoundary's derived id). `PAR`/`CALL`/
#: `UNRES` are deliberately excluded -- I-2 covers them instead.
IDENTITY_PRESERVING_KINDS = ("EP", "EVB", "FLOW", "DAO", "SP", "SQL", "PATH")


#: I-1 over a built `NormalizedEvidence` (V5.1 R3.1 SS15.1): every entity
#: kind with a canonical id -> (partition, id field). For each,
#: records == distinct ids must hold.
CANONICAL_ID_KINDS = {
    "SourceArtifact": ("source_artifacts", "id"),
    "Solution": ("solutions", "id"),
    "Project": ("projects", "id"),
    "Component": ("components", "id"),
    "EntryPoint": ("entry_points", "id"),
    "EventBinding": ("event_bindings", "id"),
    "CallIdentity": ("call_identities", "id"),
    "DataOperation": ("data_access", "id"),
    "DataObject": ("data_objects", "id"),
    "FunctionalPath": ("functional_paths", "path_id"),
    "FunctionalFlow": ("functional_flows", "id"),
    "ExternalDependency": ("external_dependencies", "id"),
    "UnresolvedBoundary": ("unresolved_boundaries", "id"),
}


#: V5.1 R3.2 D-4: entity kinds carrying `provenance` (every canonical kind
#: except `SourceArtifact`, the root of provenance itself, per V5.0 R3's own
#: exception) -> (partition, id field used only for error messages).
PROVENANCE_KINDS = {
    "Solution": ("solutions", "id"),
    "Project": ("projects", "id"),
    "Component": ("components", "id"),
    "ExternalDependency": ("external_dependencies", "id"),
    "DataObject": ("data_objects", "id"),
    "CallIdentity": ("call_identities", "id"),
    "Instantiation": ("instantiations", None),  # no canonical id; reported by (source_artifact, position)
    "UnresolvedBoundary": ("unresolved_boundaries", "id"),
}


class InvariantViolation(AssertionError):
    """Raised by any I-1..I-11 check that fails. Named after the invariant
    it enforces, e.g. `InvariantViolation("I-3: ...")`."""


def check_i1_id_unique_per_kind(records: list[dict], kind_label: str, id_field: str = "id") -> None:
    collisions: list[Collision] = detect_collisions(records, id_field=id_field)
    if collisions:
        raise InvariantViolation(f"I-1: {kind_label} has {len(collisions)} id collision(s): {collisions[:5]}")


def _canonical_ids(evidence: NormalizedEvidence, partition: str, id_field: str) -> list:
    if partition in evidence.passthrough:
        return [record.get(id_field) for record in evidence.passthrough[partition]]
    records = getattr(evidence, partition, None) or []
    return [record[id_field] if isinstance(record, dict) else getattr(record, id_field) for record in records]


def identity_report(evidence: NormalizedEvidence) -> dict[str, dict]:
    """Per canonical kind: records, distinct ids, and collision figures."""
    report = {}
    for kind, (partition, id_field) in CANONICAL_ID_KINDS.items():
        ids = _canonical_ids(evidence, partition, id_field)
        collisions = detect_duplicate_ids(ids)
        report[kind] = {"records": len(ids), "unique_ids": len(set(ids)), **collision_summary(collisions)}
    return report


def _entity_label(kind: str, record: object, id_field: str | None) -> str:
    if id_field is None:  # Instantiation: no canonical id, identify by its own FK + position
        return f"{kind}(source_artifact={record.source_artifact!r}, position={record.position})"
    entity_id = record[id_field] if isinstance(record, dict) else getattr(record, id_field)
    return f"{kind}:{entity_id!r}"


def _provenance_entities(evidence: NormalizedEvidence):
    """Yields `(label, provenance)` for every entity V5.1 R3.2 requires to
    carry `provenance` (`PROVENANCE_KINDS`) -- `SourceArtifact` is
    deliberately excluded (root exception, V5.0 R3)."""
    for kind, (partition, id_field) in PROVENANCE_KINDS.items():
        for record in getattr(evidence, partition, None) or []:
            provenance = record["provenance"] if isinstance(record, dict) else record.provenance
            yield _entity_label(kind, record, id_field), provenance


def build_reference_store(evidence: NormalizedEvidence) -> EvidenceReferenceStore:
    """The `EvidenceReferenceStore` production `provenance` resolves
    against: every `SourceArtifact` id as a valid `source`/`source_span`
    target, plus the entity kinds `provenance` actually cites by id today
    (`Project` via `ExternalDependency`'s assembly provenance,
    `FunctionalPath` via `UnresolvedBoundary`'s). Extending this to a new
    entity kind is only needed the day some `provenance` actually cites it."""
    source_ids = {artifact.id for artifact in evidence.source_artifacts}
    entity_ids = {("Project", project["id"]) for project in evidence.projects}
    entity_ids |= {("FunctionalPath", path["path_id"]) for path in evidence.passthrough.get("functional_paths", [])}
    return EvidenceReferenceStore(entity_ids=entity_ids, source_ids=source_ids)


def provenance_report(evidence: NormalizedEvidence, store: EvidenceReferenceStore) -> dict:
    """I-4/I-5 over every real `provenance`-bearing entity in `evidence`:
    entities checked, entities with empty `provenance` (I-4), and broken
    references (I-5), by `ref_type`. Never raises -- `validate_provenance`
    below is the raising gate; this is the reportable figures behind it."""
    entities_checked = 0
    empty_provenance: list[str] = []
    broken: list[tuple[str, EvidenceReference]] = []
    ref_type_counts: dict[str, int] = {}
    for label, provenance in _provenance_entities(evidence):
        entities_checked += 1
        if not provenance:
            empty_provenance.append(label)
            continue
        for ref in provenance:
            ref_type_counts[ref.ref_type] = ref_type_counts.get(ref.ref_type, 0) + 1
            try:
                resolve_against(ref, store)
            except BrokenEvidenceReferenceError:
                broken.append((label, ref))
    return {
        "entities_checked": entities_checked,
        "entities_with_empty_provenance": len(empty_provenance),
        "empty_provenance_sample": empty_provenance[:5],
        "total_references": sum(ref_type_counts.values()),
        "references_by_type": ref_type_counts,
        "broken_references": len(broken),
        "broken_references_sample": [(label, ref.to_dict()) for label, ref in broken[:5]],
    }


def validate_provenance(evidence: NormalizedEvidence, store: EvidenceReferenceStore | None = None) -> dict:
    """Production gate for I-4/I-5 (V5.1 R3.2 D-4): every entity that must
    carry `provenance` has at least one (I-4), and every `EvidenceReference`
    in it resolves against `store` (I-5) -- a broken reference never passes
    silently, it raises `InvariantViolation` here, the same failure-closed
    shape `validate_evidence` already uses for I-1/`sha256`."""
    store = store if store is not None else build_reference_store(evidence)
    report = provenance_report(evidence, store)
    if report["entities_with_empty_provenance"]:
        raise InvariantViolation(
            f"I-4: {report['entities_with_empty_provenance']} entity(ies) have no provenance EvidenceReference: "
            f"{report['empty_provenance_sample']}"
        )
    if report["broken_references"]:
        raise InvariantViolation(
            f"I-5: {report['broken_references']} provenance EvidenceReference(s) do not resolve: "
            f"{report['broken_references_sample']}"
        )
    return report


def validate_evidence(evidence: NormalizedEvidence) -> dict[str, dict]:
    """Production gate run before `evidence/` is persisted (V5.1 R3.1 D-3,
    extended by V5.1 R3.2 D-4): I-1 over every canonical kind, mandatory
    `SourceArtifact.sha256` (D-2), and I-4/I-5 over every entity's
    `provenance`. Raises `InvariantViolation` on the first failing rule;
    returns the identity + provenance report when everything holds."""
    report = identity_report(evidence)
    failing = {kind: figures for kind, figures in report.items() if figures["duplicate_ids"]}
    if failing:
        raise InvariantViolation(f"I-1: canonical id collision(s): {failing}")
    unhashed = [artifact.path for artifact in evidence.source_artifacts if not is_sha256_hex(artifact.sha256)]
    if unhashed:
        raise InvariantViolation(f"SourceArtifact.sha256 missing/invalid for {len(unhashed)} artifact(s): {unhashed[:5]}")
    validate_provenance(evidence)  # I-4/I-5 -- raises InvariantViolation on empty/broken provenance
    return report


def check_i2_no_legacy_ref_as_identity(entity_dicts: list[dict], legacy_prefixes: tuple[str, ...] = ("PAR-", "CALL-", "UNRES-")) -> None:
    for record in entity_dicts:
        entity_id = record.get("id")
        if isinstance(entity_id, str) and entity_id.startswith(legacy_prefixes):
            raise InvariantViolation(f"I-2: legacy_ref-only id used as canonical identity: {entity_id!r}")


def check_i3_entry_point_to_flow_cardinality(entry_points: list[dict], flows: list[dict]) -> None:
    flow_ids = {flow["id"] for flow in flows}
    flow_entry_point_ids = {flow["entry_point_id"] for flow in flows}
    if len(flow_entry_point_ids) > len(flow_ids):
        raise InvariantViolation("I-3: more than one FunctionalFlow shares the same entry_point_id (violates 1:0..1)")
    # A flow's entry_point_id must exist among the given entry points --
    # otherwise the "0..1" side of the cardinality is unverifiable.
    entry_point_ids = {ep["id"] for ep in entry_points}
    dangling = flow_entry_point_ids - entry_point_ids
    if dangling:
        raise InvariantViolation(f"I-3: FunctionalFlow(s) reference unknown entry_point_id(s): {sorted(dangling)[:5]}")


def check_i4_traceability(entity_refs: dict[str, list[EvidenceReference]], store: EvidenceReferenceStore) -> None:
    for entity_id, refs in entity_refs.items():
        if not refs:
            raise InvariantViolation(f"I-4: entity {entity_id!r} has no provenance EvidenceReference")
        for ref in refs:
            resolve_against(ref, store)  # raises BrokenEvidenceReferenceError -> caught by I-5's own test, not swallowed here


def check_i5_evidence_reference_resolves_or_fails_explicitly(refs: list[EvidenceReference], store: EvidenceReferenceStore) -> list[EvidenceReference]:
    """Returns the list of refs that failed to resolve (explicitly, as data
    the caller must act on) instead of raising on the first one -- I-5 is
    about detection being explicit, not about stopping at the first broken
    reference."""
    broken = []
    for ref in refs:
        try:
            resolve_against(ref, store)
        except BrokenEvidenceReferenceError:
            broken.append(ref)
    return broken


def check_i6_no_invented_relations(projected_ids: set[str], evidence_ids: set[str]) -> None:
    invented = projected_ids - evidence_ids
    if invented:
        raise InvariantViolation(f"I-6: projection cites id(s) absent from evidence: {sorted(invented)[:5]}")


def check_i7_no_promotion_without_basis(records: list[dict], state_field: str = "state", basis_field: str = "promotion_basis") -> None:
    for record in records:
        if record.get(state_field) == "confirmed" and record.get("_promoted_from_unresolved") and not record.get(basis_field):
            raise InvariantViolation(f"I-7: record {record.get('id')!r} promoted to confirmed without promotion_basis")


def check_i8_state_immutable_across_projections(evidence_states: dict[str, str], projection_states: dict[str, str]) -> None:
    for entity_id, evidence_state in evidence_states.items():
        projected_state = projection_states.get(entity_id)
        if projected_state is not None and projected_state != evidence_state:
            raise InvariantViolation(f"I-8: state mismatch for {entity_id!r}: evidence={evidence_state!r} projection={projected_state!r}")


def check_i9_legacy_projection_byte_equivalence(rebuilt: dict, original: dict, excluded_keys: tuple[str, ...] = ()) -> None:
    for key in original:
        if key in excluded_keys:
            continue
        if key not in rebuilt:
            raise InvariantViolation(f"I-9: projected index is missing key {key!r}")
        if rebuilt[key] != original[key]:
            raise InvariantViolation(f"I-9: projected index {key!r} differs from the on-disk legacy index")


def check_i10_determinism(build_once: object, build_again: object) -> None:
    if build_once != build_again:
        raise InvariantViolation("I-10: two builds of the same input produced different normalized evidence")


def check_i11_segmentation_fields_consistent(flow: dict) -> None:
    included = set(flow.get("included_paths", []) or [])
    omitted = set(flow.get("omitted_paths", []) or [])
    if included & omitted:
        raise InvariantViolation(f"I-11: included_paths and omitted_paths overlap for flow {flow.get('id')!r}: {included & omitted}")
    if flow.get("partial") and not omitted:
        raise InvariantViolation(f"I-11: flow {flow.get('id')!r} has partial=true but omitted_paths is empty")
    if not flow.get("partial") and omitted:
        raise InvariantViolation(f"I-11: flow {flow.get('id')!r} has partial=false but omitted_paths is non-empty")
