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

from legacy_documenter.cache.options import CACHE_MODES, VERIFY_LEVELS, ratio_argument

COMMANDS = ("analyze", "full", "readiness", "output-manifest", "review")


def normalize_cache_argv(argv: list[str]) -> list[str]:
    """Make bare --verify-cache unambiguous without inspecting the next token.

    Preserve positional tokens after argparse's end-of-options marker.
    The caller's list is never modified.
    """
    args = []
    positional_only = False
    for token in argv:
        if token == "--":
            positional_only = True
        args.append("--verify-cache=hash" if token == "--verify-cache" and not positional_only else token)
    return args


class _CacheArgumentParser(argparse.ArgumentParser):
    """Normalize cache flags for both direct parser users and the CLI entry point."""

    def parse_known_args(self, args=None, namespace=None):
        argv = list(sys.argv[1:] if args is None else args)
        return super().parse_known_args(normalize_cache_argv(argv), namespace)


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


def _add_cache_arguments(full_parser: argparse.ArgumentParser) -> None:
    """V5.3-R2.8 cache controls of `full` (R1 section 19/21); every one maps 1:1 to a `run_full_pipeline` parameter."""
    cache_group = full_parser.add_argument_group(
        "cache controls (V5.3)",
        "How much of a previous run's persisted cache (<output>/_cache_v53 by default) this run may reuse. None of "
        "them changes what the analysis produces: the output is the same as a full run's.",
    )
    cache_group.add_argument(
        "--cache-mode", choices=CACHE_MODES, default="auto",
        help=(
            "auto (default): validate and reuse the cache when compatible, otherwise run full and rebuild it. "
            "off: neither read nor write the cache and write every output (the V5.2 path). "
            "refresh: ignore any existing cache, run full and write a new one after a SUCCESS run."
        ),
    )
    cache_group.add_argument(
        "--cache-dir", default=None, metavar="DIR",
        help=(
            "Directory of the cache (default: <output>/_cache_v53). It must be outside the repository and must not be "
            "the output directory or one of its ancestors; use one directory per repository."
        ),
    )
    cache_group.add_argument(
        "--verify-cache", nargs="?", const="hash", default="fast", choices=VERIFY_LEVELS, metavar="{fast,hash}",
        help=(
            "fast (default): normal checksum validation, one damaged extraction shard is tolerated. "
            "hash (also bare --verify-cache): re-read and hash every persisted shard and refuse the whole cache on "
            "any inconsistency (the run is then a safe full one that rebuilds it). Costs one extra read of the cache. "
            "Use =fast or =hash for an explicit level; bare --verify-cache never consumes the next argument."
        ),
    )
    cache_group.add_argument(
        "--trust-mtime", action="store_true",
        help=(
            "Opt-in, off by default: a file whose path, size and mtime_ns equal the cached ones is not re-hashed. "
            "Unsafe if file bytes can change while size and mtime are preserved (restored backups, tools that reset "
            "mtimes): such a change is then NOT detected. Only applied to a valid, compatible cache."
        ),
    )
    cache_group.add_argument(
        "--incremental-max-changed-ratio", type=ratio_argument, default=None, metavar="RATIO",
        help=(
            "Between 0 and 1; disabled by default. If (modified + added + deleted) / files in the previous cache is "
            "greater than RATIO, the run is full (fallback_reason CHANGED_RATIO_EXCEEDED) and the cache is rebuilt. "
            "Only affects efficiency, never correctness."
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    """Builds the top-level LegacyMapper CLI parser with its three subcommands."""
    parser = _CacheArgumentParser(
        prog="main.py",
        description="LegacyMapper Documentation Analyzer",
        epilog=_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True, parser_class=argparse.ArgumentParser)

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

    full_parser.add_argument(
        "--long-paths",
        action="store_true",
        help=(
            "Windows only, opt-in: write documentation_v52 through extended-length paths (\\\\?\\) so an "
            "--output whose documents exceed the 260-character limit still works. Document names, links and "
            "manifest paths are unchanged. Other tools (Explorer, editors, antivirus) may not open such paths. "
            "Without it, a path that would not fit is reported as OUTPUT_PATH_TOO_LONG before anything is written. "
            "Has no effect on other platforms."
        ),
    )

    _add_cache_arguments(full_parser)

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

    from legacy_documenter.cli.review_command import add_review_parser

    add_review_parser(subparsers)

    return parser
