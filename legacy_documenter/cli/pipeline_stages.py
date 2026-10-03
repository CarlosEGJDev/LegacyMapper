"""Deterministic pipeline stage functions shared by `analyze` and `full`.

Extracted from the pre-V4.2-R2 `legacy_documenter.main.analyze_repository`
without changing any stage's internal logic, so both orchestration styles
call the exact same implementation:

- `analyze` (compatibility orchestration, `legacy_documenter.main.analyze_repository`)
  calls these functions back-to-back with no extra exception handling, exactly
  as the pre-R2 inline code did -- an unexpected failure still aborts the run.
- `full` (resilient orchestration, `legacy_documenter.cli.full_pipeline`) calls
  the same functions but wraps each resolver/output stage in its own
  try/except, recording a `StageError` and skipping dependents instead of
  aborting the whole run.

No stage function here decides what happens when it fails; that policy lives
entirely in the two orchestrators. This module has no knowledge of `RunResult`
or exit codes.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

from legacy_documenter.cli.artifact_lifecycle import (
    sync_generated_json_partition_directory,
    sync_generated_partition_directory,
)
from legacy_documenter.analysis.call_resolver import CallResolver
from legacy_documenter.analysis.database_resolver import DatabaseResolver
from legacy_documenter.analysis.dependency_resolver import DependencyResolver
from legacy_documenter.analysis.flow_resolver import FunctionalFlowResolver
from legacy_documenter.analysis.web_entry_resolver import WebEntryResolver
from legacy_documenter.context.consumer_projection import ConsumerProjectionBuilder
from legacy_documenter.context.context_builder import ContextBuilder
from legacy_documenter.context.hydration_view import HydrationView
from legacy_documenter.context.system_context_builder import SystemContextBuilder
from legacy_documenter.documentation.human_documentation_scaling import (
    render_human_documentation_index,
    render_human_documentation_partitions,
)
from legacy_documenter.documentation_v52.engine import generate_documentation_v52, source_from_indexes
from legacy_documenter.evidence.builder import NormalizedEvidenceBuilder
from legacy_documenter.evidence.invariants import validate_evidence
from legacy_documenter.evidence.persistence import EVIDENCE_MANIFEST_FILENAME, write_evidence
from legacy_documenter.exporters.json_exporter import JSONExporter
from legacy_documenter.exporters.markdown_exporter import MarkdownExporter
from legacy_documenter.exporters.technical_documentation_renderer import TechnicalDocumentationRenderer
from legacy_documenter.extractors.call_extractor import CallExtractor
from legacy_documenter.extractors.database_extractor import DatabaseExtractor
from legacy_documenter.extractors.solution_extractor import SolutionExtractor
from legacy_documenter.extractors.vbnet_extractor import VBNetExtractor
from legacy_documenter.extractors.vbproj_extractor import VBProjExtractor
from legacy_documenter.extractors.web_event_extractor import WebEventExtractor
from legacy_documenter.extractors.webconfig_extractor import WebConfigExtractor
from legacy_documenter.extractors.webforms_extractor import WebFormsExtractor
from legacy_documenter.models import SourceFile
from legacy_documenter.scanner.file_classifier import FileClassifier
from legacy_documenter.scanner.repository_scanner import RepositoryScanner
from legacy_documenter.utils.atomic_write import atomic_write_text
from legacy_documenter.utils.json_rendering import render_deterministic_json
from legacy_documenter.utils.sanitizer import sanitize_data

LOG = logging.getLogger("legacy_documenter")


@dataclass
class ScanOutcome:
    """Result of the SCAN stage."""

    root: Path
    files: list[SourceFile]
    classifier: FileClassifier
    scanner: RepositoryScanner


def scan_repository(repo_root: str | Path, excludes: list[str] | None) -> ScanOutcome:
    """Runs the SCAN stage: discovers and classifies every file under `repo_root`.

    `repo_root` is resolved to an absolute path here (once), so every later
    stage and the final `indexes["repository"]["root"]` value agree on it.
    """
    root = Path(repo_root).resolve()
    scanner = RepositoryScanner(excludes)
    files = scanner.scan(root)
    return ScanOutcome(root=root, files=files, classifier=FileClassifier(), scanner=scanner)


@dataclass
class ExtractionOutcome:
    """Result of the EXTRACTION stage (raw extraction plus deterministic normalization)."""

    errors: list[dict] = field(default_factory=list)
    solutions: list[dict] = field(default_factory=list)
    projects: list[dict] = field(default_factory=list)
    symbols: list[dict] = field(default_factory=list)
    logical_symbols: list[dict] = field(default_factory=list)
    webforms: list[dict] = field(default_factory=list)
    configuration: list[dict] = field(default_factory=list)
    calls: list[dict] = field(default_factory=list)
    web_events: list[dict] = field(default_factory=list)
    data_access_indexes: list[dict] = field(default_factory=list)


def extract_repository(files: list[SourceFile], root: Path, extraction_cache=None) -> ExtractionOutcome:
    """Runs the EXTRACTION stage.

    Per-file extraction stays tolerant of individual file failures exactly as
    before V4.2 (a bad file is recorded in `errors` and extraction continues);
    only a failure in the surrounding orchestration itself (not a per-file
    one) can make this stage fail as a whole. Namespace resolution and
    partial-class consolidation run last, over the fully extracted symbol/
    webform lists -- this is the "deterministic normalization/consolidation"
    step from the V4.2-R2 pipeline description; it has no separate `StageId`
    because it only operates on EXTRACTION's own in-memory output and has no
    independent failure boundary worth reporting apart from EXTRACTION itself.

    V5.3-R2.5: each file's extractor output is a self-contained record (`_extract_file`). With an
    `extraction_cache` (`legacy_documenter.cache.ExtractionCache`), an unchanged file's record comes from the
    cache and a fresh one is handed to it (serialized immediately) -- always BEFORE the in-place normalization
    below and any resolver. The records are then assembled in the original two passes (all primary results and
    errors in scan order, then the per-`.vb` calls/web events/data access), so output order is identical with
    or without a cache. Normalization always runs over the assembled lists.
    """
    outcome = ExtractionOutcome()
    extractors = _extractors()
    started = perf_counter()
    records: list[tuple[SourceFile, dict]] = []
    for source in files:
        if source.file_type not in extractors:
            continue
        record = extraction_cache.lookup(source.relative_path) if extraction_cache is not None else None
        if record is None:
            record, cacheable = _extract_file(source, root, extractors)
            if extraction_cache is not None:
                extraction_cache.store(source.relative_path, record, cacheable)
        records.append((source, record))
    if extraction_cache is not None:
        extraction_cache.record_extraction_seconds(perf_counter() - started)

    for source, record in records:
        if record["error"] is not None:
            outcome.errors.append(record["error"])
            continue
        value = record["value"]
        if source.file_type == "solution":
            outcome.solutions.append(value)
        elif source.file_type == "vb_project":
            outcome.projects.append(value)
        elif source.file_type == "vb_source":
            outcome.symbols.extend(value)
        elif source.file_type in {"aspx", "ascx", "master"}:
            outcome.webforms.append(value)
        elif source.file_type == "web_config":
            outcome.configuration.append(value)
    for source, record in records:
        if source.file_type != "vb_source":
            continue
        for slot, sink in (("calls", outcome.calls), ("web_events", outcome.web_events), ("data_access_indexes", outcome.data_access_indexes)):
            if record[slot] is not None:
                sink.append(record[slot])
        outcome.errors.extend(record["secondary_errors"])

    apply_project_namespaces(outcome.symbols, outcome.projects)
    outcome.logical_symbols = consolidate_partial_symbols(outcome.symbols, outcome.webforms)
    return outcome


def _extractors() -> dict:
    return {
        "solution": SolutionExtractor(),
        "vb_project": VBProjExtractor(),
        "vb_source": VBNetExtractor(),
        "aspx": WebFormsExtractor(),
        "ascx": WebFormsExtractor(),
        "master": WebFormsExtractor(),
        "web_config": WebConfigExtractor(),
    }


def _primary_value(file_type: str, extracted):
    """The JSON-able form of one extractor result (what `extract_repository` has always appended)."""
    if file_type == "solution" or file_type == "web_config":
        return extracted
    if file_type == "vb_source":
        return [item.to_dict() for item in extracted]
    return extracted.to_dict()


def _extract_file(source: SourceFile, root: Path, extractors: dict) -> tuple[dict, bool]:
    """Runs every extractor that applies to one file; returns `(record, cacheable)`.

    The record is plain data: `value`/`error` (primary extractor) and, for `.vb` files, `calls`/`web_events`/
    `data_access_indexes` plus `secondary_errors`. `cacheable` is False when an error came from the OS (it
    depends on more than the file's bytes).
    """
    record = {"value": None, "error": None, "calls": None, "web_events": None, "data_access_indexes": None, "secondary_errors": []}
    cacheable = True
    extractor = extractors[source.file_type]
    full_path = root / source.relative_path
    try:
        record["value"] = _primary_value(source.file_type, extractor.extract(full_path, root))
    except Exception as exc:
        record["error"] = {"file": source.relative_path, "extractor": extractor.__class__.__name__, "error": str(exc)}
        cacheable = cacheable and not isinstance(exc, OSError)
    if source.file_type == "vb_source":
        for slot, label, secondary in (
            ("calls", "CallExtractor", CallExtractor()),
            ("web_events", "WebEventExtractor", WebEventExtractor()),
            ("data_access_indexes", "DatabaseExtractor", DatabaseExtractor()),
        ):
            try:
                record[slot] = secondary.extract(full_path, root)
            except Exception as exc:
                record["secondary_errors"].append({"file": source.relative_path, "extractor": label, "error": str(exc)})
                cacheable = cacheable and not isinstance(exc, OSError)
    return record, cacheable


def apply_project_namespaces(symbols: list[dict], projects: list[dict]) -> None:
    """Resolves each symbol's effective namespace from its owning project, in place."""
    by_file: dict[str, list[dict]] = {}
    for project in projects:
        project_dir = Path(project["path"]).parent
        for item in project.get("compile_items", []):
            normalized = _norm_path(str(project_dir / item))
            by_file.setdefault(normalized, []).append(project)
    for symbol in symbols:
        matches = by_file.get(_norm_path(symbol["file"]), [])
        if len(matches) != 1:
            if not symbol.get("declared_namespace"):
                symbol["effective_namespace"] = None
            symbol["namespace_confidence"] = "unresolved"
            continue
        project = matches[0]
        root_namespace = project.get("root_namespace") or None
        declared = symbol.get("declared_namespace")
        symbol["project_path"] = project.get("path")
        symbol["root_namespace"] = root_namespace
        if root_namespace and declared:
            symbol["effective_namespace"] = f"{root_namespace}.{declared}"
        elif root_namespace:
            symbol["effective_namespace"] = root_namespace
        else:
            symbol["effective_namespace"] = declared
        symbol["namespace_confidence"] = "confirmed"


def consolidate_partial_symbols(symbols: list[dict], webforms: list[dict]) -> list[dict]:
    """Groups `Partial` classes declared across multiple files into logical symbols."""
    codebehind_files = {_norm_path(form.get("codebehind", "")) for form in webforms if form.get("codebehind")}
    codebehind_files.update({_norm_path(form.get("codefile", "")) for form in webforms if form.get("codefile")})
    groups: dict[tuple, list[dict]] = {}
    for symbol in symbols:
        if symbol.get("kind") != "class" or "Partial" not in symbol.get("modifiers", []):
            continue
        key = (symbol.get("project_path"), symbol.get("effective_namespace"), symbol.get("name"))
        groups.setdefault(key, []).append(symbol)
    logical = []
    for (project_path, namespace, name), parts in groups.items():
        files = sorted({part["file"] for part in parts})
        if len(files) < 2:
            continue
        evidence = "Partial declarations"
        normalized_files = {_norm_path(file) for file in files}
        if normalized_files & codebehind_files:
            evidence += "; WebForm code-behind association"
        logical.append(
            {
                "name": name,
                "kind": "class",
                "partial": True,
                "namespace": namespace,
                "project_path": project_path,
                "parts": files,
                "evidence": evidence,
                "confidence": "confirmed" if project_path and namespace else "unresolved",
            }
        )
    return logical


def _norm_path(value: str) -> str:
    return value.replace("\\", "/").strip("./").lower()


@dataclass
class CallResolutionOutcome:
    """Result of the CALL_RESOLUTION stage."""

    calls: list[dict]
    functional_dependencies: list[dict]


def resolve_calls(calls: list[dict], symbols: list[dict]) -> CallResolutionOutcome:
    """Runs the CALL_RESOLUTION stage. Depends only on EXTRACTION's output."""
    resolved_calls, functional_dependencies = CallResolver().resolve(calls, symbols)
    return CallResolutionOutcome(calls=resolved_calls, functional_dependencies=functional_dependencies)


@dataclass
class WebEntryResolutionOutcome:
    """Result of the WEB_ENTRY_RESOLUTION stage."""

    entry_points: list[dict]
    event_bindings: list[dict]
    functional_dependencies: list[dict]


def resolve_web_entries(webforms: list[dict], symbols: list[dict], web_events: list[dict], resolved_calls: list[dict]) -> WebEntryResolutionOutcome:
    """Runs the WEB_ENTRY_RESOLUTION stage.

    Depends on CALL_RESOLUTION: `resolved_calls` must be CALL_RESOLUTION's
    output, not the raw extracted calls -- this mirrors the pre-R2 code,
    which reassigned `calls` to the resolved value before this call.
    """
    entry_points, event_bindings, functional_dependencies = WebEntryResolver().resolve(webforms, symbols, web_events, resolved_calls)
    return WebEntryResolutionOutcome(entry_points=entry_points, event_bindings=event_bindings, functional_dependencies=functional_dependencies)


@dataclass
class DatabaseResolutionOutcome:
    """Result of the DATABASE_RESOLUTION stage."""

    data_access: list[dict]
    stored_procedures: list[dict]
    sql_operations: list[dict]
    data_parameters: list[dict]
    functional_dependencies: list[dict]


def resolve_database(data_access_indexes: list[dict], projects: list[dict]) -> DatabaseResolutionOutcome:
    """Runs the DATABASE_RESOLUTION stage. Depends only on EXTRACTION's output,
    independently of CALL_RESOLUTION/WEB_ENTRY_RESOLUTION."""
    data_access, stored_procedures, sql_operations, data_parameters, functional_dependencies = DatabaseResolver().resolve(data_access_indexes, projects)
    return DatabaseResolutionOutcome(
        data_access=data_access, stored_procedures=stored_procedures, sql_operations=sql_operations,
        data_parameters=data_parameters, functional_dependencies=functional_dependencies,
    )


@dataclass
class FlowResolutionOutcome:
    """Result of the FLOW_RESOLUTION stage."""

    functional_flows: list[dict]
    functional_paths: list[dict]
    flow_summary: dict
    flow_unresolved: list[dict]


def resolve_flows(
    entry_points: list[dict],
    resolved_calls: list[dict],
    data_access: list[dict],
    stored_procedures: list[dict],
    sql_operations: list[dict],
    functional_dependencies: list[dict],
    errors: list[dict],
    flow_max_depth: int,
) -> FlowResolutionOutcome:
    """Runs the FLOW_RESOLUTION stage.

    Depends on CALL_RESOLUTION, WEB_ENTRY_RESOLUTION and DATABASE_RESOLUTION
    all three: it needs resolved calls, entry points, and resolved database
    access together. `errors` is mutated in place (unresolved flow findings
    are appended to the same list extraction uses), matching pre-R2 behavior.
    """
    functional_flows, functional_paths, flow_summary, flow_unresolved = FunctionalFlowResolver(flow_max_depth).resolve(
        entry_points, resolved_calls, data_access, stored_procedures, sql_operations, functional_dependencies, errors
    )
    return FlowResolutionOutcome(
        functional_flows=functional_flows, functional_paths=functional_paths,
        flow_summary=flow_summary, flow_unresolved=flow_unresolved,
    )


def resolve_dependencies(solutions: list[dict], projects: list[dict], symbols: list[dict], webforms: list[dict]) -> list[dict]:
    """Runs the DEPENDENCY_RESOLUTION stage. Depends only on EXTRACTION's output,
    independently of every resolver stage above."""
    return [dep.to_dict() for dep in DependencyResolver().resolve(solutions, projects, symbols, webforms)]


def export_artifacts(output: str | Path, indexes: dict) -> None:
    """Runs the EXPORT stage: writes `output/index/*.json` and `output/documentation/*.md`.

    Covers both `JSONExporter` and `MarkdownExporter`: they always run
    together as one deterministic output step over the same `indexes`, with
    no independent failure boundary between them (see V4.2-R1 `StageId.EXPORT`
    docstring).

    Also builds and persists `output/evidence/` (V5.1 R2.1-01: the
    Normalized Evidence Core is part of the real `analyze`/`full` product
    flow) -- see `build_evidence_artifacts`: its failure fails this stage.
    """
    JSONExporter().export(output, indexes)
    MarkdownExporter().export(output, indexes)
    build_evidence_artifacts(output, indexes)


def build_evidence_artifacts(output: str | Path, indexes: dict) -> None:
    """Builds, validates and persists the Normalized Evidence Core under
    `output/evidence/` from this run's own `indexes` (no re-scan).

    Mandatory (V5.1 R3.1 D-3): any build/validation/persistence failure
    propagates, so `full` records EXPORT as FAILED (run FAILED, error in
    `RUN_SUMMARY.json`) and `analyze` aborts, exactly like any other EXPORT
    writer. `index/`/`documentation/` already written above are kept for
    diagnosis; the run is just not a valid V5 run. A previous run's
    `EVIDENCE_MANIFEST.json` is removed first, so a stale manifest can never
    vouch for evidence this run failed to produce -- the manifest is written
    last, only after every partition.

    `SourceArtifact.sha256` is always computed (D-2) from the files under
    `indexes["repository"]["root"]`. `validate_evidence` also enforces I-4/
    I-5 (V5.1 R3.2 D-4): every entity's `provenance` is non-empty and
    resolves against this run's own evidence, before anything is persisted.
    """
    stale_manifest = Path(output) / "evidence" / EVIDENCE_MANIFEST_FILENAME
    stale_manifest.unlink(missing_ok=True)
    started = perf_counter()
    evidence = NormalizedEvidenceBuilder(repo_root=indexes.get("repository", {}).get("root")).build(indexes)
    built = perf_counter()
    validate_evidence(evidence)
    validated = perf_counter()
    write_evidence(evidence, output)
    LOG.info(
        "Evidence Core: build %.1fs, validate %.1fs, persist %.1fs (%s source artifacts)",
        built - started, validated - built, perf_counter() - validated, len(evidence.source_artifacts),
    )


def create_run_flow_source(indexes: dict) -> HydrationView:
    """Creates the run's single, lazy, memoizing source of hydrated flows (V5.3-R2.1).

    The orchestrator creates it once and passes the same handle to every stage that hydrates
    flows (`build_context_artifacts` -> `consumer_projection`, `render_documentation` ->
    `HUMAN_DOCUMENTATION`), so each flow is hydrated at most once per run. Nothing is
    indexed until a consumer first asks for a flow, inside that consumer's own stage.
    """
    return HydrationView(indexes)


def log_run_flow_source_stats(source: HydrationView) -> None:
    """Logs the in-memory hydration counters of the run (how many flows were hydrated vs. served from memo)."""
    LOG.info("Hydration: %s", source.stats)


def build_context_artifacts(output: str | Path, indexes: dict, hydration_view: HydrationView | None = None) -> None:
    """Runs the CONTEXT stage: writes `output/context/*.json`, `output/ai_context/*`,
    and `output/consumer_projection/` (V4.3-R6, partitioned per its
    post-implementation correction -- see `_write_consumer_projection`).

    All three writers run under the same CONTEXT failure boundary (see
    `StageId.CONTEXT`'s docstring: `EXPORT` already covers two writers the same
    way). `consumer_projection` is deterministic and always materialized here --
    unlike `AI_INTERPRETATION`, it is never opt-in and reaches no AI/LLM service --
    so both `analyze` and `full` (which both call this same function) produce it.
    """
    ContextBuilder().build_project_contexts(output, indexes)
    system_context_artifacts = SystemContextBuilder().build(output, indexes)
    source_snapshot = system_context_artifacts["SYSTEM_CONTEXT.json"]["metadata"]["source_snapshot_sha256"]
    _write_consumer_projection(output, indexes, source_snapshot, hydration_view)


def _write_consumer_projection(
    output: str | Path, indexes: dict, source_snapshot: str, hydration_view: HydrationView | None = None,
) -> None:
    """Materializes the partitioned `LegacyMapperConsumerProjection 1.0` package (V4.3-R6).

    Projects every flow `indexes` contains (`SILENT_ENTRY_OMISSION=FORBIDDEN`,
    see `legacy_documenter.context.consumer_projection`) into one small
    manifest (`consumer_projection/CONSUMER_PROJECTION.json`) plus a
    deterministic set of self-contained partition files
    (`consumer_projection/parts/part-NNNNNN.json`) -- never one unbounded
    file, so a real repository's full evidence set never forces a single
    monolithic JSON. Both the manifest and every partition are sanitized the
    same way every other exported evidence artifact is (`AGENTS.md` "Use the
    centralized sanitizer for exported evidence"), and written atomically
    like the rest of LegacyMapper's authoritative machine artifacts.
    A rerun into the same `--output` directory with fewer flows (and
    therefore fewer partitions) removes the now-stale extra partition files
    via `sync_generated_json_partition_directory`, the same rerun-safety
    mechanism V4.2-R8 already established for partitioned Markdown
    documentation, generalized here to JSON (V4.2-R6 section 5's rerun-safety
    principle applied to this new surface).
    """
    # V5.3-R2.1: the run's shared `HydrationView` (indexed once, memoized) when the orchestrator
    # passes one; a default builder still indexes once per call, never per flow.
    builder = ConsumerProjectionBuilder(hydrator=hydration_view) if hydration_view is not None else ConsumerProjectionBuilder()
    manifest, partitions = builder.build(indexes, source_snapshot=source_snapshot)
    target = Path(output) / "consumer_projection"
    target.mkdir(parents=True, exist_ok=True)
    atomic_write_text(target / "CONSUMER_PROJECTION.json", render_deterministic_json(sanitize_data(manifest)))
    serialized_partitions = {
        Path(path).name: render_deterministic_json(sanitize_data(body)) for path, body in partitions.items()
    }
    sync_generated_json_partition_directory(target / "parts", serialized_partitions)


# Method names, not bound/unbound method objects: a captured function reference
# would freeze the renderer implementation at import time, which is both
# surprising for future maintenance and untestable via `unittest.mock.patch.object`
# (which replaces the *class attribute*, not any reference captured earlier).
# Looking the method up by name on the instance at call time keeps this ordinary.
_DOCUMENTATION_RENDERERS = ()

# V4.2-R8: FUNCTIONAL_FLOWS.md/DATABASE_ACCESS.md/UNRESOLVED_FINDINGS.md became
# navigation/summary documents over partitioned detail (R7 found these too
# large as single flat documents at real-repository scale -- see
# docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md FINDINGS
# NOISE_OR_SCALE_ISSUES). Each entry is (top-level filename, generated
# subdirectory name, navigation-renderer method, partitions-renderer method).
# V4.3-R4 (post-implementation correction, see
# docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md section 12) moves
# WEB_ENTRY_POINTS.md into this same list, using the exact same transition
# V4.2-R8 already applied to the other three -- it is no longer in
# `_DOCUMENTATION_RENDERERS` above.
_PARTITIONED_DOCUMENTATION_RENDERERS = (
    ("FUNCTIONAL_FLOWS.md", "functional_flows", "functional_flows_navigation", "functional_flows_partitions"),
    ("DATABASE_ACCESS.md", "database_access", "database_access_navigation", "database_access_partitions"),
    ("UNRESOLVED_FINDINGS.md", "unresolved_findings", "unresolved_findings_navigation", "unresolved_findings_partitions"),
    ("WEB_ENTRY_POINTS.md", "web_entry_points", "web_entry_points_navigation", "web_entry_points_partitions"),
)


@dataclass
class DocumentationOutcome:
    """Result of the DOCUMENTATION stage: which technical documents were written,
    and which failed. One renderer's failure never prevents the others from
    running -- see `render_documentation`.
    """

    written: list[str] = field(default_factory=list)
    failures: list[tuple[str, str]] = field(default_factory=list)


def render_documentation(
    output: str | Path, indexes: dict, hydration_view: HydrationView | None = None, long_paths: bool = False,
) -> DocumentationOutcome:
    """Runs the DOCUMENTATION stage (V4.2-R3): deterministic technical-documentation
    renderers over already-produced in-memory `indexes` data -- no file is re-read
    from disk. This is `full`-only; `analyze` never calls this function, so its
    output tree is unchanged from before R3.

    Each renderer (WEB_ENTRY_POINTS, FUNCTIONAL_FLOWS, DATABASE_ACCESS,
    UNRESOLVED_FINDINGS, and -- since V4.3-R7 -- HUMAN_DOCUMENTATION, the
    Spanish per-flow narrative documentation designed at V4.3-R3/R4 and
    wired here) runs independently, wrapped in its own try/except: one
    renderer's failure is recorded in `DocumentationOutcome.failures` and does not
    prevent the remaining renderers from producing their document, per the R3
    partial-failure policy ("a failure in one new renderer should not necessarily
    destroy all other documentation").
    """
    renderer = TechnicalDocumentationRenderer()
    outcome = DocumentationOutcome()
    doc_dir = Path(output) / "documentation"
    doc_dir.mkdir(parents=True, exist_ok=True)

    try:
        readme_text = renderer.documentation_readme(indexes)
        (doc_dir / "README.md").write_text(readme_text, encoding="utf-8")
        outcome.written.append("README.md")
    except Exception as exc:
        outcome.failures.append(("README.md", str(exc)))

    for filename, method_name in _DOCUMENTATION_RENDERERS:
        try:
            text = getattr(renderer, method_name)(indexes)
            (doc_dir / filename).write_text(text, encoding="utf-8")
            outcome.written.append(filename)
        except Exception as exc:
            outcome.failures.append((filename, str(exc)))

    for filename, subdir_name, nav_method, partitions_method in _PARTITIONED_DOCUMENTATION_RENDERERS:
        try:
            nav_text = getattr(renderer, nav_method)(indexes)
            partitions = getattr(renderer, partitions_method)(indexes)
            (doc_dir / filename).write_text(nav_text, encoding="utf-8")
            sync_generated_partition_directory(doc_dir / subdir_name, partitions)
            outcome.written.append(filename)
        except Exception as exc:
            outcome.failures.append((filename, str(exc)))

    try:
        # V4.3-R7 wiring decision (deliberately deferred by both R3 and R4 --
        # see "Fuera de alcance" in docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md
        # section 9): top-level filename `HUMAN_DOCUMENTATION.md`, generated
        # dedicated flow-list, not to skip omission (unlike `ai_projection`/
        # `consumer_projection`, this call is unbudgeted -- it hydrates every
        # flow, the same as `consumer_projection` does, since human
        # documentation at system scale has no LLM payload to bound either).
        # `interpretations_by_flow` is omitted: this stage is purely
        # deterministic, exactly like every other DOCUMENTATION renderer --
        # no AI content is generated or required here.
        # V5.3-R2.1: the run's shared `HydrationView` (a flow already hydrated by
        # `consumer_projection` is served from its memo, not hydrated again); without
        # one, a run-local view still indexes once instead of once per flow.
        hydrator = hydration_view if hydration_view is not None else HydrationView(indexes)
        hydrated_flows = [
            hydrator.hydrate_flow(flow["id"], indexes)
            for flow in indexes.get("functional_flows", []) if flow.get("id")
        ]
        human_index_text = render_human_documentation_index(hydrated_flows)
        human_partitions = render_human_documentation_partitions(hydrated_flows)
        (doc_dir / "HUMAN_DOCUMENTATION.md").write_text(human_index_text, encoding="utf-8")
        sync_generated_partition_directory(doc_dir / "flujos_humanos", human_partitions)
        outcome.written.append("HUMAN_DOCUMENTATION.md")
    except Exception as exc:
        outcome.failures.append(("HUMAN_DOCUMENTATION.md", str(exc)))

    _render_documentation_v52(output, indexes, outcome, long_paths)
    return outcome


def _render_documentation_v52(
    output: str | Path, indexes: dict, outcome: DocumentationOutcome, long_paths: bool = False,
) -> None:
    """V5.2-R2: additive human documentation under `documentation_v52/`
    (Profiles/Templates/Markdown Renderer). Coexists with the legacy
    `documentation/` tree, which it never reads or writes (D-52-05). A
    failure is recorded like any other renderer failure -- visible in the
    DOCUMENTATION stage, never swallowed."""
    try:
        result = generate_documentation_v52(
            source_from_indexes(indexes, _load_external_dependencies(output)), output, long_paths=long_paths,
        )
        for warning in result.warnings:
            LOG.warning("documentation_v52: %s", warning)
        LOG.info("documentation_v52 write: %s", result.write_stats)
        outcome.written.append("documentation_v52/README.md")
    except Exception as exc:
        outcome.failures.append(("documentation_v52", f"{exc.__class__.__name__}: {exc}"))


def _load_external_dependencies(output: str | Path) -> list:
    """Evidence Core `ExternalDependency` records persisted by the EXPORT stage
    (`output/evidence/external_dependencies.json`); empty when absent."""
    path = Path(output) / "evidence" / "external_dependencies.json"
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8"))
