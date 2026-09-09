import argparse
import logging
from pathlib import Path
from time import perf_counter

from legacy_documenter.analysis.dependency_resolver import DependencyResolver
from legacy_documenter.analysis.call_resolver import CallResolver
from legacy_documenter.analysis.database_resolver import DatabaseResolver
from legacy_documenter.analysis.web_entry_resolver import WebEntryResolver
from legacy_documenter.context.context_builder import ContextBuilder
from legacy_documenter.exporters.json_exporter import JSONExporter
from legacy_documenter.exporters.markdown_exporter import MarkdownExporter
from legacy_documenter.extractors.solution_extractor import SolutionExtractor
from legacy_documenter.extractors.call_extractor import CallExtractor
from legacy_documenter.extractors.database_extractor import DatabaseExtractor
from legacy_documenter.extractors.web_event_extractor import WebEventExtractor
from legacy_documenter.extractors.vbnet_extractor import VBNetExtractor
from legacy_documenter.extractors.vbproj_extractor import VBProjExtractor
from legacy_documenter.extractors.webconfig_extractor import WebConfigExtractor
from legacy_documenter.extractors.webforms_extractor import WebFormsExtractor
from legacy_documenter.scanner.file_classifier import FileClassifier
from legacy_documenter.scanner.repository_scanner import RepositoryScanner


LOG = logging.getLogger("legacy_documenter")


def analyze_repository(repo_root: str | Path, output_dir: str | Path, excludes: list[str] | None = None) -> dict:
    start = perf_counter()
    root = Path(repo_root).resolve()
    output = Path(output_dir).resolve()
    scanner = RepositoryScanner(excludes)
    files = scanner.scan(root)
    classifier = FileClassifier()
    errors: list[dict] = []
    solutions: list[dict] = []
    projects: list[dict] = []
    symbols: list[dict] = []
    webforms: list[dict] = []
    configuration: list[dict] = []
    calls: list[dict] = []
    web_events: list[dict] = []
    data_access_indexes: list[dict] = []

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
                solutions.append(extracted)
            elif source.file_type == "vb_project":
                projects.append(extracted.to_dict())
            elif source.file_type == "vb_source":
                symbols.extend(item.to_dict() for item in extracted)
            elif source.file_type in {"aspx", "ascx", "master"}:
                webforms.append(extracted.to_dict())
            elif source.file_type == "web_config":
                configuration.append(extracted)
        except Exception as exc:
            errors.append({"file": source.relative_path, "extractor": extractor.__class__.__name__, "error": str(exc)})

    call_extractor = CallExtractor()
    web_event_extractor = WebEventExtractor()
    database_extractor = DatabaseExtractor()
    for source in files:
        if source.file_type != "vb_source":
            continue
        full_path = root / source.relative_path
        try:
            calls.append(call_extractor.extract(full_path, root))
        except Exception as exc:
            errors.append({"file": source.relative_path, "extractor": "CallExtractor", "error": str(exc)})
        try:
            web_events.append(web_event_extractor.extract(full_path, root))
        except Exception as exc:
            errors.append({"file": source.relative_path, "extractor": "WebEventExtractor", "error": str(exc)})
        try:
            data_access_indexes.append(database_extractor.extract(full_path, root))
        except Exception as exc:
            errors.append({"file": source.relative_path, "extractor": "DatabaseExtractor", "error": str(exc)})

    apply_project_namespaces(symbols, projects)
    logical_symbols = consolidate_partial_symbols(symbols, webforms)
    calls, functional_dependencies = CallResolver().resolve(calls, symbols)
    entry_points, event_bindings, web_functional_dependencies = WebEntryResolver().resolve(webforms, symbols, web_events, calls)
    functional_dependencies = functional_dependencies + web_functional_dependencies
    data_access, stored_procedures, sql_operations, data_parameters, data_dependencies = DatabaseResolver().resolve(data_access_indexes, projects)
    functional_dependencies = functional_dependencies + data_dependencies
    dependencies = [dep.to_dict() for dep in DependencyResolver().resolve(solutions, projects, symbols, webforms)]
    indexes = {
        "repository": {
            "root": str(root),
            "stats": classifier.stats([item.to_dict() for item in files]),
            "ignored": scanner.ignored,
            "duration_seconds": round(perf_counter() - start, 3),
        },
        "files": [item.to_dict() for item in files],
        "solutions": solutions,
        "projects": projects,
        "symbols": symbols,
        "logical_symbols": logical_symbols,
        "calls": calls,
        "entry_points": entry_points,
        "event_bindings": event_bindings,
        "data_access": data_access,
        "stored_procedures": stored_procedures,
        "sql_operations": sql_operations,
        "data_parameters": data_parameters,
        "functional_dependencies": functional_dependencies,
        "webforms": webforms,
        "configuration": configuration,
        "dependencies": dependencies,
        "errors": errors,
    }
    JSONExporter().export(output, indexes)
    ContextBuilder().build_project_contexts(output, indexes)
    MarkdownExporter().export(output, indexes)
    LOG.info("Analysis finished: %s files, %s errors", len(files), len(errors))
    return indexes


def apply_project_namespaces(symbols: list[dict], projects: list[dict]) -> None:
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Legacy .NET Documentation Analyzer V1")
    parser.add_argument("repository", help="Repository path to analyze")
    parser.add_argument("--output", default="output", help="Output directory")
    parser.add_argument("--exclude", action="append", default=[], help="Additional folder name to exclude")
    parser.add_argument("--verbose", action="store_true", help="Enable info logging")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s: %(message)s")
    analyze_repository(args.repository, args.output, args.exclude)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
