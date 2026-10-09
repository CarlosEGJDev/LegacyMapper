"""python-generic -> Normalized Evidence Core (V5.1 contracts, unchanged).

Wraps the adapter's own `indexes` (common index shape) into the neutral entities. No Python-specific entity is added to
the core: modules and classes are `Component`s, third-party imports are `ExternalDependency`s, file operations stay in the
`data_access` passthrough, and technology metadata lives only in `extensions` / adapter provenance.
"""
from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

from legacy_documenter.evidence.bundle import NormalizedEvidence
from legacy_documenter.evidence.entities import (
    CallIdentity, Component, ExternalDependency, Instantiation, ScanSummary, SourceArtifact, UnresolvedBoundary,
)
from legacy_documenter.evidence.identity import DuplicateOrdinalAssigner, normalize_repository_id, poly33_id, sha256_id, source_artifact_id
from legacy_documenter.evidence.reference import EvidenceReference

ADAPTER_ID = "python-generic"
ADAPTER_VERSION = "1.0"

PASSTHROUGH_INDEX_KEYS = (
    "entry_points", "event_bindings", "functional_flows", "functional_paths", "flow_unresolved", "data_access", "data_parameters",
    "calls", "dependencies", "functional_dependencies", "configuration", "errors", "logical_symbols", "flow_summary",
)


class PythonEvidenceBuilder:
    """Builds a `NormalizedEvidence` from a python-generic `indexes` dict."""

    def __init__(self, repo_root: str | Path | None = None, adapter_id: str = ADAPTER_ID, adapter_version: str = ADAPTER_VERSION) -> None:
        self._repo_root = Path(repo_root) if repo_root else None
        self._adapter_id, self._adapter_version = adapter_id, adapter_version
        self._repository_id: str | None = None

    def build(self, indexes: dict) -> NormalizedEvidence:
        evidence = NormalizedEvidence()
        evidence.repository = indexes.get("repository", {})
        self._repository_id = normalize_repository_id(evidence.repository.get("repository_id"))  # None = undeclared: V5.1 ids
        stats = dict(evidence.repository.get("stats", {}))
        evidence.scan_summary = ScanSummary(root=evidence.repository.get("root", ""), total_files=stats.pop("total_files", 0), by_type=stats,
                                            ignored=list(evidence.repository.get("ignored", [])))
        root = self._repo_root or (Path(evidence.repository["root"]) if evidence.repository.get("root") else None)
        evidence.source_artifacts = self._artifacts(indexes.get("files", []), root)
        evidence.projects = self._projects(indexes.get("projects", []))
        project_ids = {p["path"]: p["id"] for p in evidence.projects}
        evidence.components = self._components(indexes.get("symbols", []), project_ids)
        evidence.external_dependencies = self._external_dependencies(indexes.get("projects", []), project_ids)
        evidence.call_identities = self._call_identities(indexes.get("calls", []))
        evidence.instantiations = self._instantiations(indexes.get("calls", []))
        evidence.unresolved_boundaries = self._unresolved(indexes.get("flow_unresolved", []))
        for key in PASSTHROUGH_INDEX_KEYS:
            if key in indexes:
                evidence.passthrough[key] = indexes[key]
        return evidence

    def _src(self, path: str | None) -> str:
        return source_artifact_id(path, self._repository_id)

    def _artifacts(self, files: list[dict], root: Path | None) -> list[SourceArtifact]:
        if files and root is None:
            raise ValueError("SourceArtifact.sha256 is mandatory: no repo_root given and indexes['repository']['root'] is empty")
        result = []
        for record in files:
            path = record["relative_path"].replace("\\", "/")
            with (root / record["relative_path"]).open("rb") as handle:
                digest = hashlib.file_digest(handle, "sha256").hexdigest()
            result.append(SourceArtifact(id=source_artifact_id(path, self._repository_id), path=path, size_bytes=record.get("size", 0), artifact_kind=record.get("file_type", "other"),
                                         adapter_id=self._adapter_id, adapter_version=self._adapter_version, sha256=digest, extensions=record))
        return result

    def _projects(self, projects: list[dict]) -> list[dict]:
        return [{
            "id": sha256_id("PRJ", record["path"]), "kind": "Project", "name": record["name"], "path": record["path"],
            "provenance": [EvidenceReference.source(self._src(record["path"]))],
            "adapter": {"id": self._adapter_id, "version": self._adapter_version}, "extensions": {self._adapter_id: record},
        } for record in projects]

    def _components(self, symbols: list[dict], project_ids: dict[str, str]) -> list[Component]:
        counts: Counter[tuple] = Counter()
        result = []
        for record in symbols:
            key = (record.get("file"), record.get("name"), record.get("kind"))
            discriminator = counts[key]
            counts[key] += 1
            source_ref = self._src(record.get("file"))
            result.append(Component(
                id=sha256_id("CMP", "python-symbol", *key, discriminator), name=record["name"], component_kind=record["kind"],
                project_id=project_ids.get(record.get("project_path")), source_ref=source_ref, state=record.get("namespace_confidence", "unresolved"),
                adapter_id=self._adapter_id, adapter_version=self._adapter_version, discriminator=discriminator, members=record.get("members", []),
                provenance=[EvidenceReference.source(source_ref, line=record.get("line"))], extensions=record))
        return result

    def _external_dependencies(self, projects: list[dict], project_ids: dict[str, str]) -> list[ExternalDependency]:
        assigner, result = DuplicateOrdinalAssigner(), []
        for record in projects:
            project_id = project_ids[record["path"]]
            for ref in record.get("assembly_references", []):
                base = ("package", record["path"], ref["include"], ref.get("hint_path"))
                ordinal = assigner.assign(base)
                result.append(ExternalDependency(
                    id=sha256_id("XDP", *base, ordinal), name=ref["include"], dependency_kind="package", adapter_id=self._adapter_id,
                    adapter_version=self._adapter_version, source_ref=project_id, duplicate_ordinal=ordinal,
                    provenance=[EvidenceReference.entity("Project", project_id)], extensions=ref))
        return result

    def _call_identities(self, groups: list[dict]) -> list[CallIdentity]:
        assigner, result = DuplicateOrdinalAssigner(), []
        for group in groups:
            file_name = group.get("file")
            for call in group.get("calls", []):
                line = (call.get("evidence") or {}).get("line")
                symbol = (call.get("containing_class"), call.get("containing_method"))
                base = (file_name, symbol, line, call.get("expression"), call.get("resolved_target"))
                ordinal = assigner.assign(base)
                source = self._src(file_name)
                result.append(CallIdentity(
                    id=sha256_id("CAL", file_name, list(symbol), line, call.get("expression"), call.get("resolved_target"), ordinal),
                    legacy_ref=poly33_id("CALL", file_name, line, call.get("expression"), call.get("resolved_target")), source_artifact=source,
                    containing_symbol=symbol, line=line, expression=call.get("expression"), resolved_target=call.get("resolved_target"),
                    duplicate_ordinal=ordinal, state=call.get("confidence", "unresolved"),
                    provenance=[EvidenceReference.source(source, line=line, excerpt=call.get("expression"))]))
        return result

    def _instantiations(self, groups: list[dict]) -> list[Instantiation]:
        result = []
        for group in groups:
            source = self._src(group.get("file"))
            for position, record in enumerate(group.get("instantiations", [])):
                evidence = record.get("evidence") or {}
                result.append(Instantiation(
                    source_artifact=source, position=position, type_name=record.get("type_name"), variable_name=record.get("variable_name"),
                    containing_symbol=(record.get("containing_class"), record.get("containing_method")), resolved_type=record.get("resolved_type"),
                    state=record.get("confidence", "unresolved"), adapter_id=self._adapter_id, adapter_version=self._adapter_version,
                    provenance=[EvidenceReference.source(source, line=evidence.get("line"), excerpt=evidence.get("expression"))], extensions=record))
        return result

    def _unresolved(self, flow_unresolved: list[dict]) -> list[UnresolvedBoundary]:
        result = []
        for record in flow_unresolved:
            terminal_type = record.get("terminal_type", "unresolved_boundary")
            target = record.get("terminal_target", record["path_id"])
            result.append(UnresolvedBoundary(
                id=sha256_id("UNB", record["path_id"], terminal_type, target), path_id=record["path_id"], boundary_target=target,
                reason_code=terminal_type, candidates=[], provenance=[EvidenceReference.entity("FunctionalPath", record["path_id"])]))
        return result
