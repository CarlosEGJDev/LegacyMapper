"""`interpret-system` and `project-system`: full-system hierarchical AI interpretation and its deterministic projection.

Both commands accept a deterministic OUTPUT directory (never a source repository): nothing here scans, parses or opens source code.
`interpret-system` may call the configured AI provider (explicit opt-in); `project-system` NEVER does.
"""
from __future__ import annotations

import json
import os
from argparse import Namespace
from pathlib import Path

_INTERPRET_HELP = (
    "Full-system hierarchical AI interpretation (system > solution > project > view / cross-project flow / data) over an ALREADY "
    "generated, valid deterministic output. Every project ends in exactly one coverage state; every provider exchange is persisted "
    "immediately under --state-dir with a stable request identity, so a re-run (or a run after quota exhaustion) replays accepted "
    "responses with 0 provider calls and continues the remaining work. Real providers require --allow-ai-interpretation."
)
_PROJECT_HELP = (
    "Project the persisted full-system interpretation into the human product (navigable HTML + PDF) and the machine product "
    "(structured JSON) deterministically. It NEVER calls a provider and never reads source code."
)


def add_system_parsers(subparsers) -> None:
    p = subparsers.add_parser("interpret-system", help=_INTERPRET_HELP, description=_INTERPRET_HELP)
    p.add_argument("baseline", help="Existing deterministic output directory (NOT a source repository)")
    p.add_argument("--state-dir", default=None, help="Interpretation state (requests, attempts, coverage). Default: <baseline>/system_ai")
    p.add_argument("--provider", default=os.environ.get("LEGACYMAPPER_LLM_PROVIDER", "COPILOT"), help="COPILOT (real) or STUB (offline, synthetic dry run)")
    p.add_argument("--model", default=os.environ.get("LEGACYMAPPER_LLM_MODEL", ""), help="Model id; empty = the provider's default")
    p.add_argument("--allow-ai-interpretation", action="store_true", help="Explicit consent to call a real AI provider (quota)")
    p.add_argument("--resume", action="store_true", help="Require an existing state in --state-dir (fails if there is none); resuming is automatic either way")
    p.add_argument("--expect-account", default=None, help="Refuse to run unless the provider is authenticated as this account")
    p.add_argument("--max-requests", type=int, default=None, help="Stop cleanly after this many provider requests (resume later)")
    p.add_argument("--max-retries", type=int, default=2, help="Bounded retries per request (default 2)")
    p.add_argument("--max-consecutive-failures", type=int, default=5, help="Stop cleanly after this many consecutive failed attempts")
    p.add_argument("--verify-evidence", choices=["hash", "fast"], default="hash")
    p.add_argument("--knowledge-output", default=None, help="Also project the human + machine product here after interpreting (no provider)")

    q = subparsers.add_parser("project-system", help=_PROJECT_HELP, description=_PROJECT_HELP)
    q.add_argument("baseline", help="Existing deterministic output directory (NOT a source repository)")
    q.add_argument("--state-dir", default=None, help="Interpretation state. Default: <baseline>/system_ai")
    q.add_argument("--output", required=True, help="Directory for human/, ai/, internal/ and ACCEPTANCE_MANIFEST.json")
    q.add_argument("--verify-evidence", choices=["hash", "fast"], default="hash")


def _dump(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)


def _state_dir(args: Namespace) -> Path:
    return Path(args.state_dir) if args.state_dir else Path(args.baseline) / "system_ai"


def make_provider(provider_type: str, model: str):
    from legacy_documenter.llm.contracts import ProviderConfig
    from legacy_documenter.llm.registry import ProviderRegistry, ensure_provider_available
    from legacy_documenter.system.stub_provider import StubProvider

    kind = provider_type.upper()
    config = ProviderConfig(kind, f"{kind.lower()}-local", model or "", max_output_tokens=3500, options={"timeout": 240}, timeout_s=240)
    registry = ProviderRegistry()
    registry.register("STUB", lambda cfg, **kw: StubProvider(cfg))
    ensure_provider_available(config)
    return registry.create(config), config


def project_if_requested(args: Namespace, state_dir: Path) -> dict | None:
    if not getattr(args, "knowledge_output", None):
        return None
    from legacy_documenter.system.product import project_system

    return project_system(args.baseline, state_dir, args.knowledge_output, verify=args.verify_evidence)


def run_interpret_system(args: Namespace) -> tuple[int, str, bool]:
    """Returns (exit_code, JSON, provider_called). 0 complete; 1 partial/interrupted; 2 usage; 4 refused/failed."""
    from legacy_documenter.system.inventory import SystemBaselineInvalid
    from legacy_documenter.system.orchestrator import RunOptions, run_system_interpretation
    from legacy_documenter.system.preflight import check_account
    from legacy_documenter.system.store import RequestStore

    kind = args.provider.upper()
    if kind != "STUB" and not args.allow_ai_interpretation:
        return 2, _dump({"status": "USAGE", "reason": "a real AI provider needs --allow-ai-interpretation (or use --provider STUB for an offline dry run)"}), False
    state_dir = _state_dir(args)
    if args.resume and not RequestStore(state_dir).load_state():
        return 2, _dump({"status": "USAGE", "reason": f"--resume given but no interpretation state exists in {state_dir}"}), False
    try:
        provider, config = make_provider(kind, args.model)
    except ImportError:
        return 4, _dump({"status": "PROVIDER_UNAVAILABLE", "reason": "the configured AI provider SDK is not installed", "provider_called": False}), False
    except ValueError as exc:
        return 4, _dump({"status": "PROVIDER_CONFIGURATION_ERROR", "reason": str(exc), "provider_called": False}), False
    preflight = check_account(kind, expect=args.expect_account)
    if args.expect_account is not None and not preflight["matches_expected"]:
        return 4, _dump({"status": "ACCOUNT_MISMATCH", "reason": "authenticated account does not match --expect-account (nothing was requested)",
                         "preflight": preflight, "provider_called": False}), False
    print(f"Provider {kind}: authenticated as {preflight['account'] or 'unknown'}" + (f" ({preflight['detail']})" if preflight["detail"] else ""))
    policy = {"provider_type": kind, "model": args.model or ""}
    options = RunOptions(args.max_requests, args.max_retries, args.max_consecutive_failures)
    try:
        result = run_system_interpretation(args.baseline, state_dir, provider, policy, options, verify=args.verify_evidence, preflight=preflight)
    except SystemBaselineInvalid as exc:
        return 4, _dump({"status": "SYSTEM_BASELINE_INVALID", "reason": exc.reason, "detail": exc.detail, "provider_called": False}), False
    finally:
        provider.close()
    m = result.metrics.as_dict()
    payload = {"status": result.status, "state_dir": str(state_dir), "coverage": str(result.coverage_path), "counts": result.state["counts"],
               "pending": result.state["pending"][:20], "pending_total": len(result.state["pending"]), "this_run": m,
               "cumulative": result.state["cumulative_metrics"], "controlled_errors": len(result.state["errors"]), "preflight": preflight,
               "provider_called": m["provider_requests"] > 0, "canonical_knowledge_produced": False, "source_scanned": False}
    if result.status.startswith("INTERRUPTED"):
        payload["next"] = "re-run the same command: accepted responses are replayed with 0 provider calls and the remaining work continues"
    product = project_if_requested(args, state_dir)
    if product is not None:
        payload["product"] = {"output": args.knowledge_output, "validation": product["validation"], "complete": product["complete"]}
    return result.exit_code, _dump(payload), m["provider_requests"] > 0


def run_project_system(args: Namespace) -> tuple[int, str]:
    """Returns (exit_code, JSON). 0 complete and valid; 1 partial or validation defects; 4 refused."""
    from legacy_documenter.system.inventory import SystemBaselineInvalid
    from legacy_documenter.system.product import ProjectionError, project_system

    try:
        doc = project_system(args.baseline, _state_dir(args), args.output, verify=args.verify_evidence)
    except SystemBaselineInvalid as exc:
        return 4, _dump({"status": "SYSTEM_BASELINE_INVALID", "reason": exc.reason, "detail": exc.detail, "provider_calls": 0})
    except ProjectionError as exc:
        return 4, _dump({"status": exc.reason, "detail": exc.detail, "provider_calls": 0})
    payload = {"status": "SUCCESS" if doc["complete"] and not doc["validation"]["defects"] else "PARTIAL", "output": str(args.output),
               "complete": doc["complete"], "synthetic_provider": doc["synthetic_provider"], "counts": doc["counts"], "machine": doc["machine"],
               "validation": doc["validation"], "provider_calls": 0, "source_scanned": False}
    return (0 if payload["status"] == "SUCCESS" else 1), _dump(payload)
