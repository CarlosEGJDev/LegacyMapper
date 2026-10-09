"""python-generic EXTRACTION: per-file static parse (cacheable) plus deterministic project assembly.

Mirrors the reference adapter's contract: each file's record is plain data, an unchanged file's record may come from
the extraction cache, and assembly always runs afterwards over the full set so output order never depends on the cache.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from time import perf_counter

from legacy_documenter.models import SourceFile

from ._names import STDLIB_MODULES
from .source_parser import parse_python_source

ADAPTER_ID = "python-generic"
PYTHON_SOURCE_KIND = "python_source"
ROOT_PROJECT_NAME = "(root)"


@dataclass
class ExtractionOutcome:
    """Same field names as the reference adapter's outcome, so the common pipeline reads either one."""

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
    adapter_id: str = ADAPTER_ID


def extract_repository(files: list[SourceFile], root: Path, extraction_cache=None) -> ExtractionOutcome:
    """Parses every `python_source` file (cache-aware) and assembles projects, symbols, calls, entries and file operations."""
    outcome = ExtractionOutcome()
    started = perf_counter()
    records: list[tuple[SourceFile, dict]] = []
    for source in files:
        if source.file_type != PYTHON_SOURCE_KIND:
            continue
        record = extraction_cache.lookup(source.relative_path) if extraction_cache is not None else None
        if record is None:
            record, cacheable = _extract_file(source, root)
            if extraction_cache is not None:
                extraction_cache.store(source.relative_path, record, cacheable)
        records.append((source, record))
    if extraction_cache is not None:
        extraction_cache.record_extraction_seconds(perf_counter() - started)

    parsed = []
    for source, record in records:
        if record["error"] is not None:
            outcome.errors.append(record["error"])
        else:
            parsed.append(record["value"])
    outcome.projects = build_projects(parsed)
    owner = _project_by_file(outcome.projects)
    for item in parsed:
        project_path = owner.get(_key(item["file"]))
        root_namespace = next((p["root_namespace"] for p in outcome.projects if p["path"] == project_path), None)
        for symbol in item["symbols"]:
            symbol["project_path"], symbol["root_namespace"] = project_path, root_namespace
            outcome.symbols.append(symbol)
        outcome.calls.append({"file": item["file"], "module": item["module"], "package_init": item["package_init"], "imports": item["imports"],
                              "instantiations": [], "calls": item["calls"]})
        if item["entries"]:
            outcome.web_events.append({"file": item["file"], "module": item["module"], "entries": item["entries"]})
        if item["file_operations"]:
            outcome.data_access_indexes.append({"file": item["file"], "module": item["module"], "operations": item["file_operations"]})
    return outcome


def _extract_file(source: SourceFile, root: Path) -> tuple[dict, bool]:
    """One file's cacheable record. An OS error is not cacheable (it depends on more than the file's bytes)."""
    record = {"value": None, "error": None}
    try:
        record["value"] = parse_python_source((root / source.relative_path).read_bytes(), source.relative_path)
        return record, True
    except Exception as exc:  # noqa: BLE001 - one bad file never fails the stage; only its class and position are kept, never source text
        line = getattr(exc, "lineno", None)
        record["error"] = {"file": source.relative_path, "extractor": "PythonSourceParser",
                           "error": exc.__class__.__name__ + (f" at line {line}" if line else "")}
        return record, not isinstance(exc, OSError)


def _key(path: str) -> str:
    return path.replace("\\", "/")


def _project_by_file(projects: list[dict]) -> dict[str, str]:
    owner: dict[str, str] = {}
    for project in projects:
        base = PurePosixPath(_key(project["path"])).parent
        for item in project["compile_items"]:
            owner[_key(str(base / _key(item)))] = project["path"]
    return owner


def build_projects(parsed: list[dict]) -> list[dict]:
    """Groups files by top-level directory (root-level scripts form the `(root)` project); deterministic and path-based only."""
    groups: dict[str, list[dict]] = {}
    for item in parsed:
        parts = PurePosixPath(_key(item["file"])).parts
        groups.setdefault(parts[0] if len(parts) > 1 else "", []).append(item)
    internal_roots = {name for name in groups if name} | {item["module"].split(".")[0] for item in groups.get("", [])}
    projects = []
    for directory in sorted(groups):
        items = sorted(groups[directory], key=lambda i: _key(i["file"]))
        init = next((i for i in items if i["file"] and _key(i["file"]) == f"{directory}/__init__.py"), None)
        anchor = (init or items[0])["file"]
        base = PurePosixPath(_key(anchor)).parent
        sep = "\\" if "\\" in anchor else "/"
        imported = sorted({_top_level(i) for item in items for i in item["imports"] if i["level"] == 0 and (i["module"] or "")})
        projects.append({
            "name": directory or ROOT_PROJECT_NAME, "path": anchor, "assembly_name": directory or ROOT_PROJECT_NAME,
            "root_namespace": directory or None, "target_framework": None, "output_type": "Package" if init else "Scripts",
            "compile_items": [sep.join(PurePosixPath(_key(i["file"])).relative_to(base).parts) for i in items],
            "project_references": [], "assembly_references": [{"include": name, "hint_path": None} for name in imported
                                                              if name not in internal_roots and name not in STDLIB_MODULES],
            "_imported": imported,
        })
    anchors = {p["root_namespace"] or ROOT_PROJECT_NAME: p for p in projects}
    root_modules = {item["module"].split(".")[0] for item in groups.get("", [])}
    for project in projects:
        own = project["root_namespace"] or ROOT_PROJECT_NAME
        targets = {}
        for name in project.pop("_imported"):
            target = anchors.get(name) if name in anchors else (anchors.get(ROOT_PROJECT_NAME) if name in root_modules else None)
            if target is not None and (target["root_namespace"] or ROOT_PROJECT_NAME) != own:
                targets[target["path"]] = target
        project["project_references"] = [{"include": t["path"], "name": t["name"], "project": t["path"]} for _, t in sorted(targets.items())]
    return projects


def _top_level(record: dict) -> str:
    return (record["module"] or "").split(".")[0]
