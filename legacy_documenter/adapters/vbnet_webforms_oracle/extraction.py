"""Reference adapter extraction and global technology normalization; original ordering preserved."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from legacy_documenter.models import SourceFile
from legacy_documenter.adapters.vbnet_webforms_oracle.extractors.call_extractor import CallExtractor
from legacy_documenter.adapters.vbnet_webforms_oracle.extractors.database_extractor import DatabaseExtractor
from legacy_documenter.adapters.vbnet_webforms_oracle.extractors.solution_extractor import SolutionExtractor
from legacy_documenter.adapters.vbnet_webforms_oracle.extractors.vbnet_extractor import VBNetExtractor
from legacy_documenter.adapters.vbnet_webforms_oracle.extractors.vbproj_extractor import VBProjExtractor
from legacy_documenter.adapters.vbnet_webforms_oracle.extractors.web_event_extractor import WebEventExtractor
from legacy_documenter.adapters.vbnet_webforms_oracle.extractors.webconfig_extractor import WebConfigExtractor
from legacy_documenter.adapters.vbnet_webforms_oracle.extractors.webforms_extractor import WebFormsExtractor


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
