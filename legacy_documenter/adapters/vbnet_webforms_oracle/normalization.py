"""`NormalizedEvidenceBuilder` -- wraps an already-produced `indexes` dict
(exactly what `legacy_documenter.cli.pipeline_stages` already holds in
memory before `EXPORT`, and exactly what a completed run's `index/*.json`
files deserialize back into) into the Normalized Evidence Core defined by
`docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md`.

This module never re-parses source code and never re-implements any
extractor/resolver logic (D-04: "envolver, no reescribir"). Every legacy
record it wraps is preserved byte-for-byte inside the wrapping entity's
`extensions` -- see `entities.py`'s module docstring for why that is what
makes the legacy projection lossless.

**Technology Adapter boundary (V5.1 R2.1-05):** this class *is* the
reference Technology Adapter's wrapping layer (R1's `ADAPTER CONTRACT`:
"Adapter de referencia `vbnet-webforms-oracle`: envuelve `extractors/*` y
`analysis/*`..."). `REFERENCE_ADAPTER_ID`/`REFERENCE_ADAPTER_VERSION` live
here, not in `entities.py`, because `entities.py` is meant to stay adapter-
agnostic (usable by a future, different adapter without modification); this
module is the one place that actually knows which adapter it is wrapping,
and it says so explicitly by passing `adapter_id`/`adapter_version` into
every entity it constructs.
"""
from __future__ import annotations

import hashlib
from collections import Counter
from legacy_documenter.evidence.bundle import NormalizedEvidence
from pathlib import Path

from legacy_documenter.evidence.entities import (
    CallIdentity,
    Component,
    DataObject,
    ExternalDependency,
    Instantiation,
    ScanSummary,
    Solution,
    SourceArtifact,
    UnresolvedBoundary,
)
from legacy_documenter.evidence.identity import (
    DuplicateOrdinalAssigner, normalize_repository_id, poly33_id, sha256_id, source_artifact_id,
)
from legacy_documenter.evidence.reference import EvidenceReference

#: The only Technology Adapter V5.1 implements: wraps the existing VB.NET/
#: WebForms/Oracle extractors and resolvers, unmodified (D-04).
REFERENCE_ADAPTER_ID = "vbnet-webforms-oracle"
REFERENCE_ADAPTER_VERSION = "1.0"

#: Index keys this builder reads verbatim and passes through unchanged --
#: entities whose identity/shape V5.0 already fixed as preserved-as-is
#: (`EP-`, `EVB-`, `FLOW-`, `DAO-`, `PATH-`) or whose contract is
#: "derived projection" (recomputable, not additional canonical evidence).
#: Stored as-is in `NormalizedEvidence.passthrough[key]`; the legacy
#: projector returns them unmodified, in their original order.
PASSTHROUGH_INDEX_KEYS = (
    "entry_points",
    "event_bindings",
    "functional_flows",
    "functional_paths",
    "flow_unresolved",
    "data_access",
    "data_parameters",
    "calls",
    "dependencies",
    "functional_dependencies",
    "configuration",
    "errors",
    "logical_symbols",
    "flow_summary",
)

_TERMINAL_UNRESOLVED_TYPES = {"unresolved_boundary", "cycle", "truncated_depth", "external_boundary"}




class NormalizedEvidenceBuilder:
    """Builds a `NormalizedEvidence` from an `indexes` dict.

    `repo_root`: filesystem root of the scanned repository, used to compute
    `SourceArtifact.sha256` from each file's real bytes. `sha256` is
    mandatory (V5.1 R3.1 D-2): it is always computed, in production too.
    When `repo_root` is omitted, the run's own `indexes["repository"]["root"]`
    (the absolute root SCAN resolved) is used; if neither exists while there
    are files to hash, or a listed file cannot be read, `build` raises --
    never a `None`/fabricated digest.

    `adapter_id`/`adapter_version`: identify which Technology Adapter this
    builder wraps. Default to the reference adapter (`REFERENCE_ADAPTER_ID`);
    a future adapter (V5.4) passes its own.
    """

    def __init__(
        self,
        repo_root: str | Path | None = None,
        adapter_id: str = REFERENCE_ADAPTER_ID,
        adapter_version: str = REFERENCE_ADAPTER_VERSION,
    ) -> None:
        self._repo_root = Path(repo_root) if repo_root else None
        self._adapter_id = adapter_id
        self._adapter_version = adapter_version
        self._repository_id: str | None = None

    def build(self, indexes: dict) -> NormalizedEvidence:
        evidence = NormalizedEvidence()
        evidence.repository = indexes.get("repository", {})
        self._repository_id = normalize_repository_id(evidence.repository.get("repository_id"))  # None = undeclared: V5.1 ids
        evidence.scan_summary = self._build_scan_summary(evidence.repository)
        evidence.source_artifacts = self._build_source_artifacts(indexes.get("files", []), self._resolve_repo_root(evidence.repository))
        evidence.solutions = self._build_solutions(indexes.get("solutions", []))
        evidence.projects = self._build_projects(indexes.get("projects", []))
        evidence.components = self._build_components(indexes.get("symbols", []), indexes.get("webforms", []))
        evidence.external_dependencies = self._build_external_dependencies(
            indexes.get("projects", []), indexes.get("functional_dependencies", [])
        )
        evidence.data_objects = self._build_data_objects(
            indexes.get("stored_procedures", []), indexes.get("sql_operations", [])
        )
        evidence.call_identities = self._build_call_identities(indexes.get("calls", []))
        evidence.instantiations = self._build_instantiations(indexes.get("calls", []))
        evidence.unresolved_boundaries = self._build_unresolved_boundaries(indexes.get("flow_unresolved", []))
        for key in PASSTHROUGH_INDEX_KEYS:
            if key in indexes:
                evidence.passthrough[key] = indexes[key]
        return evidence

    # -- SourceArtifact ---------------------------------------------------

    def _resolve_repo_root(self, repository: dict) -> Path | None:
        if self._repo_root is not None:
            return self._repo_root
        root = repository.get("root")
        return Path(root) if root else None

    def _build_source_artifacts(self, files: list[dict], repo_root: Path | None) -> list[SourceArtifact]:
        if files and repo_root is None:
            raise ValueError("SourceArtifact.sha256 is mandatory: no repo_root given and indexes['repository']['root'] is empty")
        result = []
        for record in files:
            path_posix = record["relative_path"].replace("\\", "/")
            artifact_id = source_artifact_id(path_posix, self._repository_id)
            result.append(
                SourceArtifact(
                    id=artifact_id,
                    path=path_posix,
                    size_bytes=record.get("size", 0),
                    artifact_kind=record.get("file_type", "other"),
                    adapter_id=self._adapter_id,
                    adapter_version=self._adapter_version,
                    sha256=_hash_file(repo_root / record["relative_path"]),
                    extensions=record,
                )
            )
        return result

    # -- Solution -----------------------------------------------------------

    def _build_solutions(self, solutions: list[dict]) -> list[Solution]:
        result = []
        for record in solutions:
            solution_id = sha256_id("SOL", record["path"])
            project_refs = [sha256_id("PRJ", project.get("path", "")) for project in record.get("projects", [])]
            result.append(
                Solution(
                    id=solution_id, name=record["name"], path=record["path"],
                    adapter_id=self._adapter_id, adapter_version=self._adapter_version,
                    project_refs=project_refs, provenance=[_whole_file_source_ref(record["path"], self._repository_id)], extensions=record,
                )
            )
        return result

    # -- Project --------------------------------------------------------

    def _build_projects(self, projects: list[dict]) -> list[dict]:
        result = []
        for record in projects:
            project_id = sha256_id("PRJ", record["path"])
            result.append({
                "id": project_id, "kind": "Project", "name": record["name"], "path": record["path"],
                "provenance": [_whole_file_source_ref(record["path"], self._repository_id)],
                "adapter": {"id": self._adapter_id, "version": self._adapter_version},
                "extensions": {self._adapter_id: record},
            })
        return result

    def _project_id_by_path(self, projects: list[dict]) -> dict[str, str]:
        return {record["path"]: sha256_id("PRJ", record["path"]) for record in projects}

    # -- Component (Symbol + WebForm fusion) -----------------------------

    def _build_components(self, symbols: list[dict], webforms: list[dict]) -> list[Component]:
        assigner_key_counts: Counter[tuple] = Counter()
        result: list[Component] = []

        for record in symbols:
            key = (record.get("file"), record.get("name"), record.get("kind"))
            discriminator = assigner_key_counts[key]
            assigner_key_counts[key] += 1
            component_id = sha256_id("CMP", "class-like", record.get("file"), record.get("name"), record.get("kind"), discriminator)
            source_ref = source_artifact_id(record.get("file"), self._repository_id)
            result.append(
                Component(
                    id=component_id,
                    name=record["name"],
                    component_kind=record["kind"],
                    project_id=None,  # V4.3 symbols carry `project_path`, resolved in extensions; no direct Project FK in the source record itself.
                    source_ref=source_ref,
                    state=record.get("namespace_confidence", "unresolved"),
                    adapter_id=self._adapter_id,
                    adapter_version=self._adapter_version,
                    discriminator=discriminator,
                    members=record.get("members", []),
                    provenance=[EvidenceReference.source(source_ref)],
                    extensions=record,
                )
            )

        for record in webforms:
            key = (record.get("path"), record.get("path"), record.get("kind"))  # webform "name" = its own path; guaranteed unique (R0: 3346/3346)
            discriminator = assigner_key_counts[key]
            assigner_key_counts[key] += 1
            component_id = sha256_id("CMP", "webform", record.get("path"), record.get("kind"), discriminator)
            source_ref = source_artifact_id(record.get("path"), self._repository_id)
            result.append(
                Component(
                    id=component_id,
                    name=record["path"],
                    component_kind=record["kind"],
                    project_id=None,
                    source_ref=source_ref,
                    state="confirmed",  # WebForms carry no per-record confidence in V4.3; their existence is directly observed, never inferred.
                    adapter_id=self._adapter_id,
                    adapter_version=self._adapter_version,
                    discriminator=discriminator,
                    provenance=[EvidenceReference.source(source_ref)],
                    extensions=record,
                )
            )
        return result

    # -- ExternalDependency ------------------------------------------------

    def _build_external_dependencies(self, projects: list[dict], functional_dependencies: list[dict]) -> list[ExternalDependency]:
        result = []
        project_ids = self._project_id_by_path(projects)
        # V5.1 R3.1 D-1: identity = kind + source (project path) + target
        # (Include) + stable metadata (HintPath) + duplicate_ordinal among
        # identical base tuples -- same insertion-stable scheme as CAL-.
        # Without the ordinal, repeated `<Reference>` elements in one project
        # (real IST: 5 projects with empty-Include references) shared one id.
        assigner = DuplicateOrdinalAssigner()
        for record in projects:
            project_id = project_ids[record["path"]]
            for ref in record.get("assembly_references", []):
                name = ref.get("include", "")
                base_tuple = ("assembly", record["path"], name, ref.get("hint_path"))
                duplicate_ordinal = assigner.assign(base_tuple)
                dependency_id = sha256_id("XDP", *base_tuple, duplicate_ordinal)
                result.append(
                    ExternalDependency(
                        id=dependency_id,
                        name=name,
                        dependency_kind="assembly",
                        adapter_id=self._adapter_id,
                        adapter_version=self._adapter_version,
                        version=None,
                        source_ref=project_id,
                        duplicate_ordinal=duplicate_ordinal,
                        # Provenance: an assembly reference's origin is the
                        # <Reference> element inside its owning .vbproj --
                        # already identified precisely by `source_ref`
                        # (the Project this entity's own FK already points
                        # to; the Project's own provenance in turn traces to
                        # the .vbproj SourceArtifact, see `_build_projects`).
                        provenance=[EvidenceReference.entity("Project", project_id)],
                        extensions=ref,
                    )
                )
        # V5.1 R2 SS3.4 resolution: `CONN-` connection targets become
        # ExternalDependency(dependency_kind="database_connection"),
        # deduplicated by their legacy `CONN-` target id (measured on real
        # IST: 1 distinct value across the whole target, 0 collisions).
        seen_connections: set[str] = set()
        for record in functional_dependencies:
            if record.get("dependency_type") != "DataAccessOperation -> Connection":
                continue
            legacy_conn_id = record.get("target")
            if not legacy_conn_id or legacy_conn_id in seen_connections:
                continue
            seen_connections.add(legacy_conn_id)
            dependency_id = sha256_id("XDP", "database_connection", legacy_conn_id)
            result.append(
                ExternalDependency(
                    id=dependency_id,
                    name=legacy_conn_id,
                    dependency_kind="database_connection",
                    adapter_id=self._adapter_id,
                    adapter_version=self._adapter_version,
                    legacy_ref=legacy_conn_id,
                    # Provenance: the first real occurrence of this connection
                    # target that `resolve_database` already recorded
                    # (`source_file`/`evidence`, the same fields the
                    # `functional_dependencies` edge itself carries) --
                    # never a second/invented instance.
                    provenance=[_connection_provenance(record, self._repository_id)],
                    extensions={},
                )
            )
        return result

    # -- DataObject (StoredProcedure / SQL) --------------------------------

    def _build_data_objects(self, stored_procedures: list[dict], sql_operations: list[dict]) -> list[DataObject]:
        result = []
        for record in stored_procedures:
            result.append(
                DataObject(
                    id=record["id"], object_kind="stored_procedure", name=record["name"],
                    state=record.get("confidence", "unresolved"),
                    adapter_id=self._adapter_id, adapter_version=self._adapter_version,
                    provenance=_evidence_list_provenance(record.get("evidence"), self._repository_id), extensions=record,
                )
            )
        for record in sql_operations:
            name = record.get("operation") or record["id"]
            result.append(
                DataObject(
                    id=record["id"], object_kind="sql", name=name,
                    state=record.get("confidence", "unresolved"),
                    adapter_id=self._adapter_id, adapter_version=self._adapter_version,
                    provenance=_evidence_list_provenance(record.get("evidence"), self._repository_id), extensions=record,
                )
            )
        return result

    # -- Call identity (side-table, never mutates calls.json records) -----

    def _build_call_identities(self, calls_by_file: list[dict]) -> list[CallIdentity]:
        assigner = DuplicateOrdinalAssigner()
        result = []
        for file_entry in calls_by_file:
            file_name = file_entry.get("file")
            for call in file_entry.get("calls", []):
                evidence = call.get("evidence") or {}
                line = evidence.get("line")
                expression = call.get("expression")
                resolved_target = call.get("resolved_target")
                containing_symbol = (call.get("containing_class"), call.get("containing_method"))
                base_tuple = (file_name, containing_symbol, line, expression, resolved_target)
                duplicate_ordinal = assigner.assign(base_tuple)
                legacy_ref = poly33_id("CALL", file_name, line, expression, resolved_target)
                call_id = sha256_id("CAL", file_name, list(containing_symbol), line, expression, resolved_target, duplicate_ordinal)
                source_artifact = source_artifact_id(file_name, self._repository_id)
                result.append(
                    CallIdentity(
                        id=call_id,
                        legacy_ref=legacy_ref,
                        source_artifact=source_artifact,
                        containing_symbol=containing_symbol,
                        line=line,
                        expression=expression,
                        resolved_target=resolved_target,
                        duplicate_ordinal=duplicate_ordinal,
                        state=call.get("confidence", "unresolved"),
                        provenance=[EvidenceReference.source(source_artifact, line=line, excerpt=expression)],
                    )
                )
        return result

    # -- Instantiation (V5.1 R2.1-04: own partition, no canonical id) -----

    def _build_instantiations(self, calls_by_file: list[dict]) -> list[Instantiation]:
        result = []
        for file_entry in calls_by_file:
            file_name = file_entry.get("file")
            source_artifact = source_artifact_id(file_name, self._repository_id)
            for position, record in enumerate(file_entry.get("instantiations", [])):
                evidence = record.get("evidence") or {}
                containing_symbol = (
                    record.get("containing_class") or evidence.get("class_name"),
                    record.get("containing_method") or evidence.get("method"),
                )
                result.append(
                    Instantiation(
                        source_artifact=source_artifact,
                        position=position,
                        type_name=record.get("type_name"),
                        variable_name=record.get("variable_name"),
                        containing_symbol=containing_symbol,
                        resolved_type=record.get("resolved_type"),
                        state=record.get("confidence", "unresolved"),
                        adapter_id=self._adapter_id,
                        adapter_version=self._adapter_version,
                        provenance=[EvidenceReference.source(source_artifact, line=evidence.get("line"), excerpt=evidence.get("expression"))],
                        extensions=record,
                    )
                )
        return result

    # -- UnresolvedBoundary -------------------------------------------------

    def _build_unresolved_boundaries(self, flow_unresolved: list[dict]) -> list[UnresolvedBoundary]:
        result = []
        for record in flow_unresolved:
            path_id = record["path_id"]
            terminal_type = record.get("terminal_type", "unresolved_boundary")
            terminal_target = record.get("terminal_target", path_id)
            boundary_id = sha256_id("UNB", path_id, terminal_type, terminal_target)
            result.append(
                UnresolvedBoundary(
                    id=boundary_id,
                    path_id=path_id,
                    boundary_target=terminal_target,
                    reason_code=terminal_type,
                    candidates=[],
                    # Provenance: the FunctionalPath this boundary terminates
                    # -- already the entity `flow_resolver` recorded this
                    # boundary against (`path_id`), never a second lookup.
                    provenance=[EvidenceReference.entity("FunctionalPath", path_id)],
                )
            )
        return result

    # -- ScanSummary --------------------------------------------------------

    def _build_scan_summary(self, repository: dict) -> ScanSummary:
        stats = dict(repository.get("stats", {}))
        total_files = stats.pop("total_files", 0)
        return ScanSummary(root=repository.get("root", ""), total_files=total_files, by_type=stats, ignored=list(repository.get("ignored", [])))


def _hash_file(target: Path) -> str:
    """SHA-256 of `target`'s bytes. Raises `OSError` if unreadable: a file
    SCAN listed but that can no longer be read fails the Evidence Core
    (V5.1 R3.1 D-2/D-3) instead of yielding an unhashed SourceArtifact."""
    with target.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def _whole_file_source_ref(path: str, repository_id: str | None = None) -> EvidenceReference:
    """A `source` `EvidenceReference` for a whole file, identified the same
    way `SourceArtifact.id`/`Component.source_ref` already are (V5.1 R3.2):
    `sha256_id("SRC", path posix)`. Used for entities whose real origin is
    an entire source file (`Solution`, `Project`) rather than one line."""
    return EvidenceReference.source(source_artifact_id(path, repository_id))


def _evidence_list_provenance(evidence: list[dict] | None, repository_id: str | None = None) -> list[EvidenceReference]:
    """Builds provenance from a legacy `evidence[]` list already attached
    to the record (stored procedures/SQL operations carry one real
    occurrence per element: `file`/`line`/`expression`) -- uses the first
    occurrence, in the resolver's own deterministic order, never a second,
    aggregated or synthesized one."""
    if not evidence:
        return []
    first = evidence[0]
    file_ = first.get("file")
    if not file_:
        return []
    source_id = source_artifact_id(file_, repository_id)
    return [EvidenceReference.source(source_id, line=first.get("line"), excerpt=first.get("expression"))]


def _connection_provenance(functional_dependency: dict, repository_id: str | None = None) -> EvidenceReference:
    """Provenance for a `database_connection` `ExternalDependency`, from the
    same `functional_dependencies` edge record (`DataAccessOperation ->
    Connection`) that already carries `source_file`/`evidence` -- the real
    occurrence `database_resolver` recorded when it found this connection,
    not a second lookup. Falls back to a `textual` reference (still the
    edge's own real evidence text, never invented) when `source_file` is
    absent."""
    source_file = functional_dependency.get("source_file")
    excerpt = functional_dependency.get("evidence")
    if source_file:
        return EvidenceReference.source(source_artifact_id(source_file, repository_id), excerpt=excerpt)
    return EvidenceReference.textual(excerpt or f"target={functional_dependency.get('target')!r}", origin="functional_dependencies")
