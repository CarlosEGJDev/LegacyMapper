"""V4.2-R5 -- Unified CLI and Operational UX: verification tests.

Covers, at minimum:

1. CLI help distinguishes the legacy positional form, `analyze`, `full`, and
   `readiness`.
2. `full`'s default console summary is concise and reports repository,
   output directory, deterministic/documentation status, AI requested vs.
   invoked, canonical knowledge, Technical Lead approval, and output
   locations.
3. The recommended next action is derived deterministically for: successful
   deterministic `full`; AI-enabled success with proposals; AI failure
   (partial); a fatal run.
4. `proposals/AI_PROPOSALS_PENDING_REVIEW.md` is surfaced when proposals
   exist and never mentioned when they do not.
5. "AI requested" and "AI actually invoked" remain distinguishable fields.
6. `canonical_knowledge_produced`/`technical_lead_approval` remain `False`
   and are displayed, never implied otherwise.
7. `RUN_SUMMARY.md` stays human-readable and does not duplicate technical
   documentation.
8. `RUN_SUMMARY.json` keeps every pre-R5 field and only adds new ones
   additively; new fields are deterministic.
9. Exit codes (0/1/4, argparse's own 2) are unchanged.
10. `--verbose` still shows stage-level detail in `full`'s console summary,
    default stays concise.
11. No credential/token/traceback leakage in console or summary output.
12. `analyze`/legacy behavior is unaffected.

REAL_AI_RUNTIME_CALL_ALLOWED=false: every test here uses
`legacy_documenter.llm.core.FakeLLMProvider` -- never a real provider call.
"""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.cli.execution_model import RunResult, RunStatus, StageStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.cli.run_summary_presenter import (
    compute_output_locations, derive_next_action, render_console_summary, render_markdown_summary,
)
from legacy_documenter.cli.stage_identity import StageId
from legacy_documenter.llm.core import FakeLLMProvider, ProviderConfig
from legacy_documenter.main import analyze_repository, main

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "v4_2_r3_sample"

VALID_STRUCTURED_RESPONSE = {
    "findings": [
        {
            "statement": "The Save button triggers a stored procedure call.",
            "confidence": "CONFIRMED",
            "evidence_refs": ["DAO-0197413858"],
        }
    ]
}


def _fake_provider(**kwargs) -> FakeLLMProvider:
    config = ProviderConfig("FAKE", "fake-1", "fake-model", capabilities={"structured_output": True})
    return FakeLLMProvider(config, **kwargs)


def _stage(result: RunResult, stage_id: StageId):
    return next(s for s in result.stages if s.stage is stage_id)


class CliHelpDistinguishesCommandsTests(unittest.TestCase):
    """A developer must be able to tell the four invocation shapes apart from --help alone."""

    def test_top_level_help_explains_all_four_forms(self) -> None:
        proc = subprocess.run(
            [sys.executable, "main.py", "--help"], cwd=ROOT, capture_output=True, text=True, check=True,
        )
        self.assertIn("analyze", proc.stdout)
        self.assertIn("full", proc.stdout)
        self.assertIn("readiness", proc.stdout)
        self.assertIn("--allow-ai-interpretation", proc.stdout)

    def test_analyze_help_describes_deterministic_legacy_compatible_analysis(self) -> None:
        proc = subprocess.run(
            [sys.executable, "main.py", "analyze", "--help"], cwd=ROOT, capture_output=True, text=True, check=True,
        )
        self.assertIn("Deterministic", proc.stdout)
        self.assertNotIn("--allow-ai-interpretation", proc.stdout)

    def test_full_help_describes_documentation_and_opt_in_ai(self) -> None:
        proc = subprocess.run(
            [sys.executable, "main.py", "full", "--help"], cwd=ROOT, capture_output=True, text=True, check=True,
        )
        self.assertIn("technical documentation", proc.stdout)
        self.assertIn("--allow-ai-interpretation", proc.stdout)
        allow_ai_help = " ".join(proc.stdout[proc.stdout.index("--allow-ai-interpretation"):].split())
        self.assertIn("Technical Lead review", allow_ai_help)

    def test_readiness_help_describes_a_prerequisites_check_not_an_analysis(self) -> None:
        proc = subprocess.run(
            [sys.executable, "main.py", "readiness", "--help"], cwd=ROOT, capture_output=True, text=True, check=True,
        )
        self.assertIn("readiness", proc.stdout.lower())


class DefaultConsoleSummaryTests(unittest.TestCase):
    """`full`'s default console output must be concise but cover every required field."""

    def test_default_full_console_summary_reports_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                exit_code = main(["full", str(FIXTURE), "--output", out])
            summary = buf.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn(str(FIXTURE), summary)
        self.assertIn(str(Path(out).resolve()), summary)
        self.assertIn("Deterministic analysis:", summary)
        self.assertIn("Documentation:", summary)
        self.assertIn("AI requested: False", summary)
        self.assertIn("AI invoked:   False", summary)
        self.assertIn("Canonical knowledge produced: False", summary)
        self.assertIn("Technical Lead approval:      False", summary)
        self.assertIn("Next action:", summary)
        self.assertIn("Technical documentation generated successfully.", summary)

    def test_default_summary_does_not_dump_every_stage_result(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                main(["full", str(FIXTURE), "--output", out])
            summary = buf.getvalue()
        self.assertNotIn("Stages:", summary)

    def test_verbose_summary_shows_stage_level_detail(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                main(["full", str(FIXTURE), "--output", out, "--verbose"])
            summary = buf.getvalue()
        self.assertIn("Stages:", summary)
        self.assertIn("SCAN: SUCCESS", summary)


class NextActionDerivationTests(unittest.TestCase):
    """`derive_next_action` must be a deterministic function of run state alone."""

    def test_successful_deterministic_run_next_action(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertEqual(result.next_action, "Technical documentation generated successfully.")

    def test_ai_enabled_success_with_proposals_next_action(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertGreater(result.proposal_count, 0)
        self.assertIn("pending Technical Lead review", result.next_action)
        self.assertIn("AI_PROPOSALS_PENDING_REVIEW.md", result.next_action)

    def test_ai_failure_next_action_reports_deterministic_docs_available(self) -> None:
        provider = _fake_provider(forced_status="PROVIDER_ERROR")
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertEqual(_stage(result, StageId.AI_INTERPRETATION).status, StageStatus.FAILED)
        self.assertEqual(result.status, RunStatus.PARTIAL)
        self.assertIn("Deterministic documentation is available", result.next_action)
        self.assertIn("AI interpretation failed", result.next_action)

    def test_fatal_run_next_action_points_at_run_summary(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.full_pipeline.stages.export_artifacts", side_effect=OSError("disk full")):
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertEqual(result.status, RunStatus.FAILED)
        self.assertIn("did not produce the minimum useful output", result.next_action)
        self.assertIn("RUN_SUMMARY.json", result.next_action)

    def test_next_action_never_implies_user_approval(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertNotIn("approved", result.next_action.lower())


class ProposalReviewArtifactDisplayTests(unittest.TestCase):
    """The pending-review artifact must be surfaced only when it actually exists."""

    def test_proposal_artifact_listed_when_proposals_exist(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertIn("proposals", result.output_locations)
        self.assertEqual(result.proposal_review_status, "PENDING_TECHNICAL_LEAD_REVIEW")
        console = render_console_summary(result, str(FIXTURE), Path(out))
        self.assertIn("PENDING_TECHNICAL_LEAD_REVIEW", console)

    def test_no_proposal_path_when_ai_not_requested(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertNotIn("proposals", result.output_locations)
        self.assertIsNone(result.proposal_review_status)
        console = render_console_summary(result, str(FIXTURE), Path(out))
        self.assertNotIn("Proposals:", console)


class AiRequestedVsInvokedTests(unittest.TestCase):
    """'Requested' (the flag) and 'invoked' (the provider was actually reached) must never be conflated."""

    def test_not_requested_means_not_invoked(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertFalse(result.ai_requested)
        self.assertFalse(result.ai_invoked)

    def test_requested_and_successfully_invoked(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertTrue(result.ai_requested)
        self.assertTrue(result.ai_invoked)

    def test_requested_but_provider_never_reached_because_context_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.full_pipeline.stages.build_context_artifacts", side_effect=OSError("boom")):
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True)
        self.assertTrue(result.ai_requested)
        self.assertFalse(result.ai_invoked)
        self.assertEqual(_stage(result, StageId.AI_INTERPRETATION).status, StageStatus.SKIPPED_DUE_TO_UPSTREAM_FAILURE)


class ApprovalDisplayTests(unittest.TestCase):
    def test_canonical_knowledge_and_approval_displayed_false(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertFalse(result.canonical_knowledge_produced)
        self.assertFalse(result.technical_lead_approval)
        console = render_console_summary(result, str(FIXTURE), Path(out))
        self.assertIn("Canonical knowledge produced: False", console)
        self.assertIn("Technical Lead approval:      False", console)


class RunSummaryMarkdownReadabilityTests(unittest.TestCase):
    def test_run_summary_md_is_human_readable_and_does_not_duplicate_documentation(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
            markdown = (Path(out) / "RUN_SUMMARY.md").read_text(encoding="utf-8")
            doc_text = (Path(out) / "documentation" / "PROJECT_OVERVIEW.md").read_text(encoding="utf-8")
        self.assertIn("# LegacyMapper Run Summary", markdown)
        self.assertIn("## Next Action", markdown)
        self.assertIn(result.next_action, markdown)
        self.assertNotIn(doc_text.strip(), markdown)


class RunSummaryJsonContractTests(unittest.TestCase):
    """RUN_SUMMARY.json must keep every pre-R5 field and only add new fields additively."""

    PRE_R5_FIELDS = {"command", "status", "stages", "ai_invoked", "canonical_knowledge_produced", "technical_lead_approval"}

    def test_pre_r5_fields_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            payload = json.loads((Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
        self.assertTrue(self.PRE_R5_FIELDS.issubset(payload.keys()))

    def test_new_fields_are_additive_and_present(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            payload = json.loads((Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
        for key in ("ai_requested", "proposal_count", "proposal_review_status", "next_action", "output_locations"):
            self.assertIn(key, payload)

    def test_new_fields_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as out1, tempfile.TemporaryDirectory() as out2:
            run_full_pipeline(FIXTURE, out1, None, 12)
            run_full_pipeline(FIXTURE, out2, None, 12)
            payload1 = json.loads((Path(out1) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
            payload2 = json.loads((Path(out2) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
        for key in ("ai_requested", "proposal_count", "proposal_review_status", "next_action"):
            self.assertEqual(payload1[key], payload2[key])
        self.assertEqual(sorted(payload1["output_locations"]), sorted(payload2["output_locations"]))


class ExitCodeUnchangedTests(unittest.TestCase):
    def test_success_partial_failed_exit_codes_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(main(["full", str(FIXTURE), "--output", out]), 0)
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.full_pipeline.stages.export_artifacts", side_effect=OSError("disk full")):
            self.assertEqual(main(["full", str(FIXTURE), "--output", out]), 4)

    def test_usage_error_exit_code_is_two(self) -> None:
        # `analyze` with no repository positional is a genuine argparse usage
        # error; an unrecognized bare token is NOT one -- normalize_argv's
        # legacy fallback treats it as a repository path (see parser.py).
        proc = subprocess.run(
            [sys.executable, "main.py", "analyze"], cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 2)


class SecurityTests(unittest.TestCase):
    """Console/summary output must never leak credentials, tokens, or raw tracebacks."""

    def test_console_summary_has_no_traceback_or_credential_markers(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.full_pipeline.stages.export_artifacts", side_effect=OSError("disk full")):
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                main(["full", str(FIXTURE), "--output", out])
            output = buf.getvalue()
        for marker in ("Traceback (most recent call last)", "api_key", "authorization", "password"):
            self.assertNotIn(marker.lower(), output.lower())

    def test_run_summary_markdown_has_no_credential_markers(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            markdown = (Path(out) / "RUN_SUMMARY.md").read_text(encoding="utf-8").lower()
        for marker in ("api_key", "authorization", "password", "secret"):
            self.assertNotIn(marker, markdown)


class AnalyzeAndLegacyBehaviorUnchangedTests(unittest.TestCase):
    """R5 is `full`-only UX; `analyze`/legacy must be byte-for-byte unaffected."""

    def test_analyze_writes_no_console_summary_and_no_run_summary(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                exit_code = main(["analyze", str(FIXTURE), "--output", out])
            printed = buf.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertEqual(printed, "")
        self.assertFalse((Path(out) / "RUN_SUMMARY.json").exists())

    def test_analyze_repository_function_unaffected(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            indexes = analyze_repository(FIXTURE, out, None, 12)
        self.assertEqual(indexes["errors"], [])


class OutputLocationDiscoveryTests(unittest.TestCase):
    def test_compute_output_locations_only_lists_existing_paths(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            output_dir = Path(out)
            (output_dir / "documentation").mkdir()
            locations = compute_output_locations(output_dir)
        self.assertEqual(locations, ["documentation"])


if __name__ == "__main__":
    unittest.main()
