"""V4.2-R1 -- CLI Contract and Execution Model: verification tests.

Covers, at minimum:

1. The legacy bare-positional invocation (`python main.py <repository> ...`)
   still parses to an `analyze` command with identical option handling.
2. The explicit `analyze` subcommand is accepted with the same flags.
3. `--exclude`/`--verbose`/`--flow-max-depth` all still reach `analyze`.
4. `full` is parsed and routed to the deterministic orchestrator (implemented
   in V4.2-R2; this module only checks routing/plumbing -- it never calls the
   legacy `analyze_repository` implementation and the implementation never
   touches any AI/knowledge capability). Full behavioral coverage of the
   orchestrator itself is in
   tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py.
5. `readiness` routes to the existing `legacy_documenter.knowledge.readiness`
   capability without duplicating its logic.
6. `python -m legacy_documenter.knowledge.readiness` keeps working unchanged.
7. The RunStatus/StageStatus/StageResult/RunResult execution model.
8. The structured StageError model (no raw traceback, no secrets).
9. Deterministic RunResult serialization (same model -> same bytes).
10. No CLI route can produce automatic approval or canonical knowledge.

This module characterizes the R1 parsing/routing/execution-model contract;
V4.2-R2 added real `full` orchestration behind the same contract without
changing anything this module asserts about parsing/routing/the model itself.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from legacy_documenter.cli.execution_model import RunResult, RunStatus, StageError, StageResult, StageStatus
from legacy_documenter.cli.parser import build_parser, normalize_argv
from legacy_documenter.cli.router import EXIT_SUCCESS, route
from legacy_documenter.cli.serialization import render_run_result
from legacy_documenter.cli.stage_identity import StageId

ROOT = Path(__file__).parents[1]


class NormalizeArgvTests(unittest.TestCase):
    """The legacy bare-positional invocation must keep working unchanged."""

    def test_bare_repository_is_rewritten_to_analyze(self) -> None:
        self.assertEqual(normalize_argv(["C:/repo"]), ["analyze", "C:/repo"])

    def test_bare_repository_with_flags_is_rewritten_to_analyze(self) -> None:
        argv = ["C:/repo", "--output", "out", "--verbose"]
        self.assertEqual(normalize_argv(argv), ["analyze", *argv])

    def test_flag_before_positional_is_rewritten_to_analyze(self) -> None:
        # A legacy invocation may place options before the positional repository.
        argv = ["--output", "out", "C:/repo"]
        self.assertEqual(normalize_argv(argv), ["analyze", *argv])

    def test_explicit_analyze_is_left_untouched(self) -> None:
        argv = ["analyze", "C:/repo", "--output", "out"]
        self.assertEqual(normalize_argv(argv), argv)

    def test_explicit_full_is_left_untouched(self) -> None:
        argv = ["full", "C:/repo"]
        self.assertEqual(normalize_argv(argv), argv)

    def test_explicit_readiness_is_left_untouched(self) -> None:
        self.assertEqual(normalize_argv(["readiness"]), ["readiness"])

    def test_no_arguments_is_rewritten_to_analyze(self) -> None:
        self.assertEqual(normalize_argv([]), ["analyze"])


class ParserTests(unittest.TestCase):
    """Explicit subcommands must accept the same options the legacy parser accepted."""

    def test_legacy_positional_invocation_parses_as_analyze(self) -> None:
        args = build_parser().parse_args(normalize_argv(["C:/repo", "--output", "out"]))
        self.assertEqual(args.command, "analyze")
        self.assertEqual(args.repository, "C:/repo")
        self.assertEqual(args.output, "out")

    def test_analyze_accepts_all_existing_flags(self) -> None:
        argv = ["analyze", "C:/repo", "--output", "out", "--exclude", "bin", "--exclude", "obj",
                "--verbose", "--flow-max-depth", "5"]
        args = build_parser().parse_args(argv)
        self.assertEqual(args.repository, "C:/repo")
        self.assertEqual(args.output, "out")
        self.assertEqual(args.exclude, ["bin", "obj"])
        self.assertTrue(args.verbose)
        self.assertEqual(args.flow_max_depth, 5)

    def test_analyze_defaults_match_legacy_defaults(self) -> None:
        args = build_parser().parse_args(["analyze", "C:/repo"])
        self.assertEqual(args.output, "output")
        self.assertEqual(args.exclude, [])
        self.assertFalse(args.verbose)
        self.assertEqual(args.flow_max_depth, 12)

    def test_full_accepts_the_same_analysis_options(self) -> None:
        args = build_parser().parse_args(["full", "C:/repo", "--output", "out"])
        self.assertEqual(args.command, "full")
        self.assertEqual(args.repository, "C:/repo")
        self.assertEqual(args.output, "out")

    def test_readiness_takes_no_positional_arguments(self) -> None:
        args = build_parser().parse_args(["readiness"])
        self.assertEqual(args.command, "readiness")

    def test_unknown_command_is_rejected(self) -> None:
        with self.assertRaises(SystemExit):
            build_parser().parse_args(["bogus", "C:/repo"])


class RouteAnalyzeTests(unittest.TestCase):
    """`analyze` must call the existing analysis implementation, unchanged."""

    def test_analyze_calls_the_injected_implementation_with_exact_arguments(self) -> None:
        calls: list[tuple] = []

        def fake_analyze_repository(repo_root, output_dir, excludes=None, flow_max_depth=12):
            calls.append((repo_root, output_dir, excludes, flow_max_depth))
            return {}

        args = Namespace(command="analyze", repository="C:/repo", output="out", exclude=["bin"], flow_max_depth=7)
        exit_code, result = route(args, fake_analyze_repository)

        self.assertEqual(exit_code, EXIT_SUCCESS)
        self.assertEqual(result.command, "analyze")
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertEqual(calls, [("C:/repo", "out", ["bin"], 7)])


class RouteFullTests(unittest.TestCase):
    """`full` routes to the V4.2-R2 deterministic orchestrator, never the legacy
    `analyze_repository` implementation. Full behavioral coverage of the
    orchestrator itself lives in
    tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py; this
    module only characterizes routing/plumbing, which is still R1's scope."""

    def test_full_never_calls_the_legacy_analyze_implementation(self) -> None:
        def fake_analyze_repository(*args, **kwargs):
            raise AssertionError("full must not call the legacy analyze_repository implementation")

        fixture = str(ROOT / "tests" / "fixtures" / "v2_r1_sample")
        with tempfile.TemporaryDirectory() as out:
            args = Namespace(command="full", repository=fixture, output=out, exclude=[], flow_max_depth=12)
            exit_code, result = route(args, fake_analyze_repository)

        self.assertEqual(result.command, "full")
        self.assertIn(result.status, {RunStatus.SUCCESS, RunStatus.PARTIAL, RunStatus.FAILED})

    def test_full_never_reaches_approval_canonical_or_projection_modules(self) -> None:
        # `router.py`/`pipeline_stages.py` must never touch approval, canonical
        # knowledge, projection, Plugin, or knowledge ingestion -- opt-in AI or
        # not. `full_pipeline.py` legitimately gained `knowledge.proposals`/`llm`
        # references in V4.2-R4 for the opt-in AI_INTERPRETATION/PROPOSAL_GENERATION
        # stages (gated by `allow_ai_interpretation`; see
        # docs/V4_2/V4_2_R4_AI_INTERPRETATION_AND_PROPOSAL_INTEGRATION_RESULT.md);
        # it is checked separately, still forbidding the truly off-limits domains.
        import legacy_documenter.cli.router as router_module
        import legacy_documenter.cli.pipeline_stages as pipeline_stages_module

        forbidden = [
            "deep_interpretation", "knowledge.proposals", "knowledge.approval",
            "knowledge.canonical", "knowledge.projection", "knowledge.plugin_projection",
            "knowledge.ingestion",
        ]
        for module in (router_module, pipeline_stages_module):
            source = Path(module.__file__).read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, source, msg=f"{module.__name__} must not reference {token!r}")

        import legacy_documenter.cli.full_pipeline as full_pipeline_module

        still_forbidden = [
            "deep_interpretation", "knowledge.approval", "knowledge.canonical",
            "knowledge.projection", "knowledge.plugin_projection", "knowledge.ingestion",
        ]
        source = Path(full_pipeline_module.__file__).read_text(encoding="utf-8")
        for token in still_forbidden:
            self.assertNotIn(token, source, msg=f"full_pipeline.py must not reference {token!r}")


class RouteReadinessTests(unittest.TestCase):
    """`readiness` must be a thin route to the existing readiness gate."""

    def test_readiness_routes_through_existing_readiness_run(self) -> None:
        import legacy_documenter.cli.router as router_module

        original_run = router_module.run_readiness
        try:
            router_module.run_readiness = lambda: {"readiness": "READY", "status": "FAKE"}
            args = Namespace(command="readiness")
            exit_code, result = route(args, analyze_repository=None)
        finally:
            router_module.run_readiness = original_run

        self.assertEqual(exit_code, EXIT_SUCCESS)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        payload = json.loads(result.message)
        self.assertEqual(payload["readiness"], "READY")
        self.assertEqual(payload["status"], "FAKE")

    def test_readiness_reports_partial_when_not_ready(self) -> None:
        import legacy_documenter.cli.router as router_module

        original_run = router_module.run_readiness
        try:
            router_module.run_readiness = lambda: {"readiness": "BLOCKED"}
            args = Namespace(command="readiness")
            exit_code, result = route(args, analyze_repository=None)
        finally:
            router_module.run_readiness = original_run

        self.assertNotEqual(exit_code, EXIT_SUCCESS)
        self.assertEqual(result.status, RunStatus.PARTIAL)

    def test_readiness_does_not_reimplement_the_gate(self) -> None:
        # The router must call the existing service, not re-derive readiness checks.
        import legacy_documenter.cli.router as router_module

        source = Path(router_module.__file__).read_text(encoding="utf-8")
        self.assertIn("from legacy_documenter.knowledge.readiness import run as run_readiness", source)


class ExistingReadinessModuleEntryPointTests(unittest.TestCase):
    """`python -m legacy_documenter.knowledge.readiness` must remain valid, unchanged."""

    def test_module_entry_point_still_prints_matching_json(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "legacy_documenter.knowledge.readiness"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["readiness"], "READY")
        self.assertEqual(payload["provider_calls"], 0)
        self.assertEqual(payload["real_llm_calls"], 0)


class ExecutionModelTests(unittest.TestCase):
    """RunStatus/StageStatus/StageResult/RunResult must support SUCCESS/PARTIAL/FAILED
    and stage states equivalent to SUCCESS/FAILED/SKIPPED_DUE_TO_UPSTREAM_FAILURE/NOT_RUN."""

    def test_run_status_members(self) -> None:
        self.assertEqual({member.value for member in RunStatus}, {"SUCCESS", "PARTIAL", "FAILED"})

    def test_stage_status_members(self) -> None:
        self.assertEqual(
            {member.value for member in StageStatus},
            {"SUCCESS", "FAILED", "SKIPPED_DUE_TO_UPSTREAM_FAILURE", "NOT_RUN"},
        )

    def test_stage_id_is_stable_and_covers_candidate_stages(self) -> None:
        expected = {
            "SCAN", "EXTRACTION", "CALL_RESOLUTION", "WEB_ENTRY_RESOLUTION", "DATABASE_RESOLUTION",
            "FLOW_RESOLUTION", "DEPENDENCY_RESOLUTION", "EXPORT", "CONTEXT", "DOCUMENTATION",
            "AI_INTERPRETATION", "PROPOSAL_GENERATION", "FINAL_SUMMARY",
        }
        self.assertEqual({member.value for member in StageId}, expected)

    def test_run_result_to_dict_shape(self) -> None:
        stage = StageResult(stage=StageId.SCAN, status=StageStatus.SUCCESS)
        result = RunResult(command="analyze", status=RunStatus.SUCCESS, stages=(stage,))
        payload = result.to_dict()
        self.assertEqual(payload["command"], "analyze")
        self.assertEqual(payload["status"], "SUCCESS")
        self.assertEqual(payload["stages"], [{"stage": "SCAN", "status": "SUCCESS"}])
        self.assertNotIn("message", payload)

    def test_run_result_is_immutable(self) -> None:
        result = RunResult(command="analyze", status=RunStatus.SUCCESS)
        with self.assertRaises(Exception):
            result.status = RunStatus.FAILED  # type: ignore[misc]


class StageErrorModelTests(unittest.TestCase):
    """The structured error model must never carry a raw traceback or secrets."""

    def test_error_to_dict_carries_only_declared_fields(self) -> None:
        error = StageError(stage=StageId.FLOW_RESOLUTION, category="TIMEOUT", message="flow resolution exceeded depth")
        payload = error.to_dict()
        self.assertEqual(set(payload), {"stage", "category", "message"})

    def test_error_to_dict_includes_reference_only_when_set(self) -> None:
        error = StageError(
            stage=StageId.EXTRACTION, category="PARSE_ERROR", message="could not parse file", reference="Foo.vb"
        )
        payload = error.to_dict()
        self.assertEqual(payload["reference"], "Foo.vb")

    def test_stage_result_embeds_error_dict(self) -> None:
        error = StageError(stage=StageId.SCAN, category="IO_ERROR", message="path not found")
        stage_result = StageResult(stage=StageId.SCAN, status=StageStatus.FAILED, error=error)
        payload = stage_result.to_dict()
        self.assertEqual(payload["error"]["category"], "IO_ERROR")

    def test_error_message_has_no_traceback_markers(self) -> None:
        error = StageError(stage=StageId.SCAN, category="IO_ERROR", message="path not found")
        self.assertNotIn("Traceback", error.message)
        self.assertNotIn("  File \"", error.message)


class SerializationTests(unittest.TestCase):
    """Result serialization must be deterministic: same model -> same bytes."""

    def test_same_model_serializes_identically(self) -> None:
        stage = StageResult(stage=StageId.SCAN, status=StageStatus.SUCCESS)
        result_a = RunResult(command="analyze", status=RunStatus.SUCCESS, stages=(stage,))
        result_b = RunResult(command="analyze", status=RunStatus.SUCCESS, stages=(stage,))
        self.assertEqual(render_run_result(result_a), render_run_result(result_b))

    def test_serialization_has_sorted_keys_and_no_whitespace_drift(self) -> None:
        result = RunResult(command="analyze", status=RunStatus.SUCCESS)
        rendered = render_run_result(result)
        # V4.2-R2 added the always-rendered approval-boundary fields
        # (ai_invoked/canonical_knowledge_produced/technical_lead_approval).
        # V4.2-R5 added five more always-rendered, additive UX fields
        # (ai_requested/proposal_count/proposal_review_status/next_action/
        # output_locations -- see docs/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX_RESULT.md).
        # sorted-keys/no-whitespace determinism is unchanged.
        self.assertEqual(
            rendered,
            '{"ai_invoked":false,"ai_requested":false,"canonical_knowledge_produced":false,'
            '"command":"analyze","next_action":null,"output_locations":[],"proposal_count":0,'
            '"proposal_review_status":null,"stages":[],"status":"SUCCESS","technical_lead_approval":false}',
        )

    def test_serialization_has_no_uuid_or_timestamp_fields(self) -> None:
        result = RunResult(command="full", status=RunStatus.FAILED)
        payload = json.loads(render_run_result(result))
        for key in payload:
            self.assertNotIn("id", key.lower())
            self.assertNotIn("time", key.lower())


class ApprovalBoundaryTests(unittest.TestCase):
    """No CLI route may manufacture Technical Lead approval or canonical knowledge."""

    def test_no_cli_subcommand_is_named_approve(self) -> None:
        parser = build_parser()
        subparsers_action = next(
            action for action in parser._actions if action.dest == "command"
        )
        self.assertNotIn("approve", subparsers_action.choices)

    def test_router_module_never_imports_approval_or_canonical(self) -> None:
        import legacy_documenter.cli.router as router_module

        source = Path(router_module.__file__).read_text(encoding="utf-8")
        self.assertNotIn("ApprovalAuthority", source)
        self.assertNotIn("CanonicalKnowledgeEntry", source)


if __name__ == "__main__":
    unittest.main()
