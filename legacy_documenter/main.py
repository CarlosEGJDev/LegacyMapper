import logging
from pathlib import Path
from time import perf_counter

from legacy_documenter.cli.parser import build_parser, normalize_argv
from legacy_documenter.cli.router import route
from legacy_documenter.cli import pipeline_stages as stages
from legacy_documenter.cli.run_summary_presenter import render_console_summary


LOG = logging.getLogger("legacy_documenter")


def analyze_repository(repo_root: str | Path, output_dir: str | Path, excludes: list[str] | None = None, flow_max_depth: int = 12) -> dict:
    """Runs the deterministic analysis pipeline end to end (the `analyze` compatibility orchestration).

    Calls the same stage functions `full` uses (`legacy_documenter.cli.pipeline_stages`
    and `legacy_documenter.cli.full_pipeline`), but with no stage-level exception
    handling of its own: an unresolved error in any resolver/export stage still
    aborts the whole run uncaught, exactly as before V4.2-R2. This is what keeps
    `analyze`'s observable behavior byte-for-byte equivalent to the pre-R2 CLI.
    """
    start = perf_counter()
    scan = stages.scan_repository(repo_root, excludes)
    output = Path(output_dir).resolve()

    extraction = stages.extract_repository(scan.files, scan.root)
    call_resolution = stages.resolve_calls(extraction.calls, extraction.symbols)
    web_entry_resolution = stages.resolve_web_entries(
        extraction.webforms, extraction.symbols, extraction.web_events, call_resolution.calls
    )
    functional_dependencies = call_resolution.functional_dependencies + web_entry_resolution.functional_dependencies
    database_resolution = stages.resolve_database(extraction.data_access_indexes, extraction.projects)
    functional_dependencies = functional_dependencies + database_resolution.functional_dependencies
    flow_resolution = stages.resolve_flows(
        web_entry_resolution.entry_points, call_resolution.calls, database_resolution.data_access,
        database_resolution.stored_procedures, database_resolution.sql_operations,
        functional_dependencies, extraction.errors, flow_max_depth,
    )
    dependencies = stages.resolve_dependencies(extraction.solutions, extraction.projects, extraction.symbols, extraction.webforms)

    indexes = {
        "repository": {
            "root": str(scan.root),
            "stats": scan.classifier.stats([item.to_dict() for item in scan.files]),
            "ignored": scan.scanner.ignored,
            "duration_seconds": round(perf_counter() - start, 3),
        },
        "files": [item.to_dict() for item in scan.files],
        "solutions": extraction.solutions,
        "projects": extraction.projects,
        "symbols": extraction.symbols,
        "logical_symbols": extraction.logical_symbols,
        "calls": call_resolution.calls,
        "entry_points": web_entry_resolution.entry_points,
        "event_bindings": web_entry_resolution.event_bindings,
        "data_access": database_resolution.data_access,
        "stored_procedures": database_resolution.stored_procedures,
        "sql_operations": database_resolution.sql_operations,
        "data_parameters": database_resolution.data_parameters,
        "functional_dependencies": functional_dependencies,
        "functional_flows": flow_resolution.functional_flows,
        "functional_paths": flow_resolution.functional_paths,
        "flow_summary": flow_resolution.flow_summary,
        "flow_unresolved": flow_resolution.flow_unresolved,
        "webforms": extraction.webforms,
        "configuration": extraction.configuration,
        "dependencies": dependencies,
        "errors": extraction.errors,
    }
    stages.export_artifacts(output, indexes)
    stages.build_context_artifacts(output, indexes)
    LOG.info("Analysis finished: %s files, %s errors", len(scan.files), len(extraction.errors))
    return indexes


def main(argv: list[str] | None = None) -> int:
    """Parses CLI arguments and routes to analyze/full/readiness.

    The legacy bare-positional invocation (`python main.py <repository> ...`)
    is preserved unchanged: `normalize_argv` rewrites it into an explicit
    `analyze` invocation before parsing (see `legacy_documenter/cli/parser.py`).
    """
    args = build_parser().parse_args(normalize_argv(argv))
    logging.basicConfig(
        level=logging.INFO if getattr(args, "verbose", False) else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )
    if args.command == "full" and getattr(args, "allow_ai_interpretation", False):
        # V4.2-R5 section 10: make the opt-in explicit at the point of use too,
        # not only in --help -- this run may call the configured AI provider.
        print("AI interpretation requested: this run may call the configured AI provider.")
    exit_code, result = route(args, analyze_repository)
    if result.command in ("readiness", "output-manifest") and result.message is not None:
        print(result.message)
    elif result.command == "full":
        summary = render_console_summary(
            result, args.repository, Path(args.output).resolve(), verbose=getattr(args, "verbose", False)
        )
        if result.status.value == "FAILED":
            LOG.error(summary)
        else:
            print(summary)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
