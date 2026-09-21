"""Argument parsing for the LegacyMapper CLI.

Introduces explicit `analyze` / `full` / `readiness` subcommands while
preserving the legacy bare-positional invocation
(`python main.py <repository> [options]`) unchanged, by rewriting it into an
explicit `analyze` invocation before argparse ever sees it (see
`normalize_argv`). This module only decides how the command line is spelled;
`router.py` decides what a parsed command does.
"""
from __future__ import annotations

import argparse
import sys

COMMANDS = ("analyze", "full", "readiness", "output-manifest")


def normalize_argv(argv: list[str] | None) -> list[str]:
    """Rewrites a legacy bare-positional invocation into an explicit `analyze` one.

    Only an argument list whose first token is already a known subcommand name
    is left untouched. Everything else — a repository path, a flag such as
    `--output`/`--verbose`, or no arguments at all — is treated as the
    pre-V4.2 invocation shape and gets `analyze` prepended, so a single
    subparser-based grammar can handle both forms without special-casing them
    downstream. This is what keeps `python main.py <repository> ...` a hard
    backward-compatibility guarantee rather than a second parsing path.

    `-h`/`--help` as the first token is also left untouched (V4.2-R5): without
    this exception, a bare `python main.py --help` would silently become
    `analyze --help` and a first-time user could never see the top-level
    help text that explains `analyze`/`full`/`readiness` (see `_EPILOG`
    below) -- they would only ever see `analyze`'s own subparser help.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if args and (args[0] in COMMANDS or args[0] in ("-h", "--help")):
        return args
    return ["analyze", *args]


def _add_analysis_arguments(subparser: argparse.ArgumentParser) -> None:
    """Adds the analysis options shared by `analyze` and `full`.

    Kept identical to the pre-V4.2 top-level parser's options so existing
    scripts see no behavioral difference once routed through `analyze`.
    """
    subparser.add_argument("repository", help="Repository path to analyze")
    subparser.add_argument("--output", default="output", help="Output directory")
    subparser.add_argument("--exclude", action="append", default=[], help="Additional folder name to exclude")
    subparser.add_argument("--verbose", action="store_true", help="Enable info logging")
    subparser.add_argument(
        "--flow-max-depth", type=int, default=12, help="Maximum confirmed method-call depth for R4 flows"
    )


_EPILOG = """\
Which command should I use?

  python main.py <repository> ...
      Legacy shorthand for `analyze <repository> ...` (kept for existing
      scripts). No AI, no documentation rendering, no run summary.

  python main.py analyze <repository> --output <dir>
      Deterministic, legacy-compatible code analysis only. Produces the
      index/context artifacts under <dir>. This is the pre-V4.2 behavior;
      it does not render technical documentation and writes no run summary.

  python main.py full <repository> --output <dir>
      Deterministic analysis + technical documentation + a run summary
      (RUN_SUMMARY.json/.md under <dir>). Makes zero AI/provider calls.
      This is the recommended default for a new user.

  python main.py full <repository> --output <dir> --allow-ai-interpretation
      Everything `full` does, plus one opt-in AI interpretation pass over
      this run's own evidence. Any resulting proposals are written pending
      Technical Lead review -- never auto-approved, never canonical
      knowledge. Without this flag, `full` never contacts an AI provider.

  python main.py readiness
      Checks LegacyMapper's own knowledge/readiness prerequisites -- it does
      not analyze a repository at all.

  python main.py output-manifest <output-dir>
      Writes <output-dir>/OUTPUT_MANIFEST.json: the path/size/SHA-256 of every
      file already under <output-dir> from a completed `full`/`analyze` run.
      Verification only -- never re-runs analysis. Available from a clean,
      runtime-only distribution (main.py + legacy_documenter/ alone), with no
      dependency on this development repository's docs/tests/tools/.
"""


def build_parser() -> argparse.ArgumentParser:
    """Builds the top-level LegacyMapper CLI parser with its three subcommands."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="LegacyMapper Documentation Analyzer",
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_help = (
        "Deterministic legacy-compatible analysis only (the pre-V4.2 default behavior). "
        "No documentation rendering, no AI, no run summary."
    )
    analyze_parser = subparsers.add_parser("analyze", help=analyze_help, description=analyze_help)
    _add_analysis_arguments(analyze_parser)

    full_help = (
        "Deterministic analysis + technical documentation + a RUN_SUMMARY under --output. "
        "Recommended default. AI interpretation is opt-in only -- see --allow-ai-interpretation."
    )
    full_parser = subparsers.add_parser("full", help=full_help, description=full_help)
    _add_analysis_arguments(full_parser)
    full_parser.add_argument(
        "--allow-ai-interpretation",
        action="store_true",
        help=(
            "Opt in to an additional AI interpretation pass over this run's own evidence. May "
            "call the configured AI provider. Produces proposals pending Technical Lead review -- "
            "never approved automatically. Off by default: without this flag, `full` makes zero "
            "AI/provider calls, exactly like `analyze`."
        ),
    )

    readiness_help = (
        "Validates LegacyMapper's own knowledge/readiness prerequisites "
        "(thin route to legacy_documenter.knowledge.readiness.run) -- does not analyze a repository."
    )
    subparsers.add_parser("readiness", help=readiness_help, description=readiness_help)

    output_manifest_help = (
        "Writes <output-dir>/OUTPUT_MANIFEST.json: path/size/SHA-256 of every file already under "
        "<output-dir> from a completed run. Verification only -- never re-runs analysis. Part of the "
        "runtime package (legacy_documenter.cli.output_manifest), so it travels with a clean, "
        "development-repository-independent distribution."
    )
    output_manifest_parser = subparsers.add_parser(
        "output-manifest", help=output_manifest_help, description=output_manifest_help
    )
    output_manifest_parser.add_argument("output_dir", help="The --output directory of a completed run")

    return parser
