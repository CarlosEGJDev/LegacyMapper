"""Safe manual verification for `full`, including `--allow-ai-interpretation` (V4.2-R5.1).

The R5 disclosure that prompted this tool: a human ran
`python main.py full <repo> --output <dir> --allow-ai-interpretation`
directly for ad hoc console-UX verification, and because this development
environment has a real, locally logged-in Copilot client available, that
command actually reached it -- a real AI provider call, forbidden whenever
a round declares `REAL_AI_RUNTIME_CALL_ALLOWED=false`.

Rule going forward (see AGENTS.md "Manual AI-Path Verification"): whenever
real AI calls are forbidden, manual verification of the AI-enabled path
MUST go through this script (or an equivalent explicit `FakeLLMProvider`
injection), never through `python main.py full ... --allow-ai-interpretation`
directly -- that command always resolves a real provider via
`ProviderRegistry`/`_resolve_provider` when no provider is injected, exactly
like it does in production, because that path must keep working for actual
authorized use.

This script always injects `legacy_documenter.llm.core.FakeLLMProvider` --
it can never reach a real provider, no matter what CLI flags are passed.

Usage:
    python -m tools.manual_verify_full_pipeline <repository> --output <dir> \\
        [--allow-ai-interpretation] [--forced-status PROVIDER_ERROR]
"""
from __future__ import annotations

import argparse
import json

from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.cli.run_summary_presenter import render_console_summary
from legacy_documenter.llm.core import FakeLLMProvider, ProviderConfig

_DEFAULT_STRUCTURED_RESPONSE = {
    "findings": [
        {"statement": "Manual verification finding (FakeLLMProvider, no real call).", "confidence": "UNCERTAIN", "evidence_refs": []}
    ]
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repository")
    parser.add_argument("--output", default="output")
    parser.add_argument("--allow-ai-interpretation", action="store_true")
    parser.add_argument(
        "--forced-status", default=None,
        help="Force FakeLLMProvider to a specific status (e.g. PROVIDER_ERROR) to verify failure UX.",
    )
    parser.add_argument("--flow-max-depth", type=int, default=12)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    provider = None
    if args.allow_ai_interpretation:
        config = ProviderConfig("FAKE", "manual-verify-fake", "fake-model", capabilities={"structured_output": True})
        provider = FakeLLMProvider(config, structured_response=_DEFAULT_STRUCTURED_RESPONSE, forced_status=args.forced_status)
    result = run_full_pipeline(
        args.repository, args.output, None, args.flow_max_depth,
        allow_ai_interpretation=args.allow_ai_interpretation, ai_provider=provider,
    )
    print(render_console_summary(result, args.repository, args.output, verbose=True))
    print()
    print("(FakeLLMProvider only -- no real AI provider was ever reachable from this script.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
