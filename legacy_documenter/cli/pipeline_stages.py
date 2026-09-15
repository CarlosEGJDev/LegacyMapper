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

from dataclasses import dataclass, field
from pathlib import Path

from legacy_documenter.analysis.call_resolver import CallResolver
from legacy_documenter.analysis.database_resolver import DatabaseResolver
from legacy_documenter.analysis.dependency_resolver import DependencyResolver
from legacy_documenter.analysis.flow_resolver import FunctionalFlowResolver
from legacy_documenter.analysis.web_entry_resolver import WebEntryResolver
from legacy_documenter.context.context_builder import ContextBuilder
from legacy_documenter.context.system_context_builder import SystemContextBuilder
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


def extract_repository(files: list[SourceFile], root: Path) -> ExtractionOutcome:
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
    """
    outcome = ExtractionOutcome()

    extractors = {
        "solution": SolutionExtractor(),
        "vb_project": VBProjExtractor(),
        "vb_source": VBNetExtractor(),
        "aspx": WebFormsExtractor(),
        "ascx": WebFormsExtractor(),
        "master": WebFormsExtractor(),
        "web_config": WebConfigExtractor(),
    }

    for source in files:
        extractor = extractors.get(source.file_type)
        if not extractor:
            continue
        full_path = root / source.relative_path
        try:
            extracted = extractor.extract(full_path, root)
            if source.file_type == "solution":
                outcome.solutions.append(extracted)
            elif source.file_type == "vb_project":
                outcome.projects.append(extracted.to_dict())
            elif source.file_type == "vb_source":
                outcome.symbols.extend(item.to_dict() for item in extracted)
            elif source.file_type in {"aspx", "ascx", "master"}:
                outcome.webforms.append(extracted.to_dict())
            elif source.file_type == "web_config":
                outcome.configuration.append(extracted)
        except Exception as exc:
            outcome.errors.append({"file": source.relative_path, "extractor": extractor.__class__.__name__, "error": str(exc)})

    call_extractor = CallExtractor()
    web_event_extractor = WebEventExtractor()
    database_extractor = DatabaseExtractor()
    for source in files:
        if source.file_type != "vb_source":
            continue
        full_path = root / source.relative_path
        _extract_into(call_extractor, "CallExtractor", source, full_path, root, outcome.calls, outcome.errors)
        _extract_into(web_event_extractor, "WebEventExtractor", source, full_path, root, outcome.web_events, outcome.errors)
        _extract_into(database_extractor, "DatabaseExtractor", source, full_path, root, outcome.data_access_indexes, outcome.errors)

    apply_project_namespaces(outcome.symbols, outcome.projects)
    outcome.logical_symbols = consolidate_partial_symbols(outcome.symbols, outcome.webforms)
    return outcome


def _extract_into(
    extractor: CallExtractor | WebEventExtractor | DatabaseExtractor,
    label: str,
    source: SourceFile,
    full_path: Path,
    root: Path,
    sink: list,
    errors: list[dict],
) -> None:
    """Runs one per-file extractor, appending its result to `sink` or a structured error to `errors`."""
    try:
        sink.append(extractor.extract(full_path, root))
    except Exception as exc:
        errors.append({"file": source.relative_path, "extractor": label, "error": str(exc)})


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
    """
    JSONExporter().export(output, indexes)
    MarkdownExporter().export(output, indexes)


def build_context_artifacts(output: str | Path, indexes: dict) -> None:
    """Runs the CONTEXT stage: writes `output/context/*.json` and `output/ai_context/*`."""
    ContextBuilder().build_project_contexts(output, indexes)
    SystemContextBuilder().build(output, indexes)


# Method names, not bound/unbound method objects: a captured function reference
# would freeze the renderer implementation at import time, which is both
# surprising for future maintenance and untestable via `unittest.mock.patch.object`
# (which replaces the *class attribute*, not any reference captured earlier).
# Looking the method up by name on the instance at call time keeps this ordinary.
_DOCUMENTATION_RENDERERS = (
    ("WEB_ENTRY_POINTS.md", "web_entry_points"),
    ("FUNCTIONAL_FLOWS.md", "functional_flows"),
    ("DATABASE_ACCESS.md", "database_access"),
    ("UNRESOLVED_FINDINGS.md", "unresolved_findings"),
)


@dataclass
class DocumentationOutcome:
    """Result of the DOCUMENTATION stage: which technical documents were written,
    and which failed. One renderer's failure never prevents the others from
    running -- see `render_documentation`.
    """

    written: list[str] = field(default_factory=list)
    failures: list[tuple[str, str]] = field(default_factory=list)


def render_documentation(output: str | Path, indexes: dict) -> DocumentationOutcome:
    """Runs the DOCUMENTATION stage (V4.2-R3): deterministic technical-documentation
    renderers over already-produced in-memory `indexes` data -- no file is re-read
    from disk. This is `full`-only; `analyze` never calls this function, so its
    output tree is unchanged from before R3.

    Each of the four renderers (WEB_ENTRY_POINTS, FUNCTIONAL_FLOWS, DATABASE_ACCESS,
    UNRESOLVED_FINDINGS) runs independently, wrapped in its own try/except: one
    renderer's failure is recorded in `DocumentationOutcome.failures` and does not
    prevent the remaining renderers from producing their document, per the R3
    partial-failure policy ("a failure in one new renderer should not necessarily
    destroy all other documentation").
    """
    renderer = TechnicalDocumentationRenderer()
    outcome = DocumentationOutcome()
    doc_dir = Path(output) / "documentation"
    for filename, method_name in _DOCUMENTATION_RENDERERS:
        try:
            text = getattr(renderer, method_name)(indexes)
            doc_dir.mkdir(parents=True, exist_ok=True)
            (doc_dir / filename).write_text(text, encoding="utf-8")
            outcome.written.append(filename)
        except Exception as exc:
            outcome.failures.append((filename, str(exc)))
    return outcome
