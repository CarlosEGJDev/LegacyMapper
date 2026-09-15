"""V4.2-R6 -- Robustness, Recovery, Security and Approval-Surface Design: verification tests.

Covers, at minimum (section 19):

1. successful rerun same output; partial -> rerun; failed -> rerun
2. AI -> non-AI same output; non-AI -> AI same output
3. stale proposals cannot appear current; AI failure after a prior success
   removes stale proposals safely
4. unknown user files under `proposals/` are preserved
5. source repository untouched (rerun/cleanup never targets it)
6. RUN_SUMMARY represents the current run (including its own FINAL_SUMMARY
   row -- the R5 self-reference gap this round closes)
7. summary write failure and proposal write failure are both structured,
   never a raw traceback / uncaught exception
8. a representative filesystem failure (unwritable output) is contained
9. path traversal is impossible through proposal/provider content
10. real provider resolution stays blocked in tests; no credential leakage
11. no approval produced; no canonical knowledge produced
12. exit codes remain 0/1/2/4; legacy/analyze unchanged

REAL_AI_RUNTIME_CALL_ALLOWED=false: every AI-path test here uses
`legacy_documenter.llm.core.FakeLLMProvider`; the test-suite-wide guard in
`tests/__init__.py` additionally fails loudly if any test unexpectedly
reaches real provider resolution.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.cli.artifact_lifecycle import reset_stale_proposal_artifacts
from legacy_documenter.cli.execution_model import RunStatus, StageStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.cli.router import EXIT_FAILED, EXIT_PARTIAL, EXIT_SUCCESS
from legacy_documenter.cli.stage_identity import StageId
from legacy_documenter.llm.core import FakeLLMProvider, ProviderConfig
from legacy_documenter.main import analyze_repository, main
from legacy_documenter.utils.atomic_write import atomic_write_text

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


def _stage(result, stage_id: StageId):
    return next(s for s in result.stages if s.stage is stage_id)


class RerunSameOutputTests(unittest.TestCase):
    """A user must be able to safely run `full` again into the same --output."""

    def test_successful_run_then_successful_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            first = run_full_pipeline(FIXTURE, out, None, 12)
            second = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertEqual(first.status, RunStatus.SUCCESS)
        self.assertEqual(second.status, RunStatus.SUCCESS)

    def test_partial_run_then_rerun_recovers(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            with patch("legacy_documenter.cli.full_pipeline.stages.build_context_artifacts", side_effect=OSError("boom")):
                partial = run_full_pipeline(FIXTURE, out, None, 12)
            recovered = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertEqual(partial.status, RunStatus.PARTIAL)
        self.assertEqual(recovered.status, RunStatus.SUCCESS)

    def test_failed_run_then_rerun_recovers(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            with patch("legacy_documenter.cli.full_pipeline.stages.export_artifacts", side_effect=OSError("disk full")):
                failed = run_full_pipeline(FIXTURE, out, None, 12)
            recovered = run_full_pipeline(FIXTURE, out, None, 12)
            self.assertTrue((Path(out) / "index" / "repository.json").exists())
        self.assertEqual(failed.status, RunStatus.FAILED)
        self.assertEqual(recovered.status, RunStatus.SUCCESS)

    def test_ai_enabled_run_then_deterministic_rerun_same_output(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
            second = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertEqual(second.status, RunStatus.SUCCESS)
        self.assertFalse(second.ai_requested)
        self.assertEqual(second.proposal_count, 0)

    def test_deterministic_run_then_ai_enabled_rerun_same_output(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            second = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertEqual(second.status, RunStatus.SUCCESS)
        self.assertTrue(second.ai_requested)
        self.assertGreater(second.proposal_count, 0)


class StaleProposalSafetyTests(unittest.TestCase):
    """The scenario V4.2-R6 section 5 calls out as 'especially important'."""

    def test_ai_run_then_non_ai_rerun_does_not_appear_to_have_current_proposals(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out:
            run_a = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
            self.assertGreater(run_a.proposal_count, 0)
            self.assertTrue((Path(out) / "proposals" / "AI_PROPOSALS.json").exists())

            run_b = run_full_pipeline(FIXTURE, out, None, 12)  # no AI opt-in this time

            # The stale files themselves must also be gone, not merely
            # unreferenced -- a human browsing the output tree directly must
            # not find run A's proposals sitting there looking untouched.
            self.assertFalse((Path(out) / "proposals" / "AI_PROPOSALS.json").exists())
            self.assertFalse((Path(out) / "proposals" / "AI_PROPOSALS_PENDING_REVIEW.md").exists())

            summary = json.loads((Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["proposal_count"], 0)
            self.assertNotIn("proposals", summary["output_locations"])

        self.assertFalse(run_b.ai_requested)
        self.assertEqual(run_b.proposal_count, 0)
        self.assertIsNone(run_b.proposal_review_status)
        self.assertNotIn("proposals", run_b.output_locations)
        self.assertNotIn("pending Technical Lead review", run_b.next_action)

    def test_ai_failure_after_prior_successful_ai_run_produces_a_fresh_no_proposals_envelope(self) -> None:
        # Run B's own AI stage genuinely runs (it does not raise -- a forced
        # provider status is a normal, structured failure) and its proposal
        # write step still executes, overwriting run A's stale, pending-
        # review envelope with a fresh one that accurately says nothing was
        # generated THIS run -- never leaving the OLD "pending review"
        # content sitting there looking current (V4.2-R6 section 5).
        success_provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        failing_provider = _fake_provider(forced_status="PROVIDER_ERROR")
        with tempfile.TemporaryDirectory() as out:
            run_a = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=success_provider)
            self.assertGreater(run_a.proposal_count, 0)

            run_b = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=failing_provider)

            envelope = json.loads((Path(out) / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8"))
            self.assertEqual(envelope["status"], "NO_PROPOSALS_GENERATED")
            self.assertEqual(envelope["proposals"], [])

        self.assertEqual(_stage(run_b, StageId.AI_INTERPRETATION).status, StageStatus.FAILED)
        self.assertEqual(run_b.proposal_count, 0)
        self.assertEqual(run_b.proposal_review_status, "NO_PROPOSALS_GENERATED")
        self.assertNotIn("pending Technical Lead review", run_b.next_action)

    def test_unknown_user_file_under_proposals_directory_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            proposals_dir = Path(out) / "proposals"
            proposals_dir.mkdir(parents=True)
            (proposals_dir / "AI_PROPOSALS.json").write_text("{}", encoding="utf-8")
            (proposals_dir / "notes_from_a_human.txt").write_text("do not delete me", encoding="utf-8")

            reset_stale_proposal_artifacts(Path(out))

            self.assertFalse((proposals_dir / "AI_PROPOSALS.json").exists())
            self.assertTrue((proposals_dir / "notes_from_a_human.txt").exists())
            self.assertEqual((proposals_dir / "notes_from_a_human.txt").read_text(encoding="utf-8"), "do not delete me")
            self.assertTrue(proposals_dir.is_dir())  # not empty -- never removed

    def test_reset_is_a_no_op_when_proposals_directory_does_not_exist(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            reset_stale_proposal_artifacts(Path(out))  # must not raise
            self.assertFalse((Path(out) / "proposals").exists())


class SummaryIntegrityTests(unittest.TestCase):
    """RUN_SUMMARY.json/.md must represent the CURRENT run, including its own outcome."""

    def test_persisted_summary_includes_its_own_final_summary_stage(self) -> None:
        # The R5-documented gap: the file used to omit FINAL_SUMMARY
        # entirely because it was written before that stage was known to
        # have succeeded. V4.2-R6 closes this by building the true final
        # state in memory first and only persisting it once the write is
        # known to succeed (see run_summary_presenter.finalize_and_write_run_summary).
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            payload = json.loads((Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
        stage_names = {stage["stage"] for stage in payload["stages"]}
        self.assertIn("FINAL_SUMMARY", stage_names)
        final_summary = next(s for s in payload["stages"] if s["stage"] == "FINAL_SUMMARY")
        self.assertEqual(final_summary["status"], "SUCCESS")

    def test_persisted_summary_output_locations_include_run_summary_itself(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            payload = json.loads((Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
        self.assertIn("RUN_SUMMARY.json", payload["output_locations"])
        self.assertIn("RUN_SUMMARY.md", payload["output_locations"])

    def test_summary_write_failure_is_structured_not_a_crash(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.run_summary_presenter.atomic_write_text", side_effect=OSError("disk full")):
            result = run_full_pipeline(FIXTURE, out, None, 12)  # must not raise
            # deterministic analysis remains available even though the
            # summary write itself failed
            self.assertTrue((Path(out) / "index" / "repository.json").exists())
        self.assertEqual(_stage(result, StageId.FINAL_SUMMARY).status, StageStatus.FAILED)
        self.assertEqual(_stage(result, StageId.FINAL_SUMMARY).error.category, "OSError")
        self.assertEqual(result.status, RunStatus.PARTIAL)

    def test_summary_write_failure_never_leaves_a_lying_success_file(self) -> None:
        # First run succeeds and writes a real summary; a second run whose
        # own write fails must not overwrite it with fabricated content --
        # `finalize_and_write_run_summary` only ever writes once the render
        # is known-good and the atomic write itself succeeds.
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            before = (Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8")
            with patch("legacy_documenter.cli.run_summary_presenter.atomic_write_text", side_effect=OSError("disk full")):
                run_full_pipeline(FIXTURE, out, None, 12)
            after = (Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8")
        self.assertEqual(before, after)


class ProposalWriteFailureTests(unittest.TestCase):
    def test_proposal_write_failure_is_structured_not_a_crash(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.full_pipeline.atomic_write_text", side_effect=OSError("disk full")):
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertEqual(_stage(result, StageId.PROPOSAL_GENERATION).status, StageStatus.FAILED)
        self.assertEqual(_stage(result, StageId.PROPOSAL_GENERATION).error.category, "OSError")
        self.assertEqual(result.proposal_count, 0)
        self.assertIsNone(result.proposal_review_status)
        self.assertNotIn("proposals", result.output_locations)
        self.assertEqual(result.status, RunStatus.PARTIAL)  # never silently FAILED->SUCCESS or crashed


class AtomicWriteTests(unittest.TestCase):
    def test_atomic_write_replaces_content_and_leaves_no_temp_file(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            path = Path(out) / "file.txt"
            atomic_write_text(path, "first")
            atomic_write_text(path, "second")
            self.assertEqual(path.read_text(encoding="utf-8"), "second")
            leftovers = [p for p in Path(out).iterdir() if p.name != "file.txt"]
            self.assertEqual(leftovers, [])

    def test_atomic_write_failure_cleans_up_temp_file_and_preserves_original(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            path = Path(out) / "file.txt"
            atomic_write_text(path, "original")
            with patch("legacy_documenter.utils.atomic_write.os.replace", side_effect=OSError("boom")):
                with self.assertRaises(OSError):
                    atomic_write_text(path, "new content that must never land")
            self.assertEqual(path.read_text(encoding="utf-8"), "original")
            leftovers = [p for p in Path(out).iterdir() if p.name != "file.txt"]
            self.assertEqual(leftovers, [])


class FilesystemFailureContainmentTests(unittest.TestCase):
    def test_unwritable_output_directory_is_a_structured_failure_not_a_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.pipeline_stages.JSONExporter.export", side_effect=PermissionError("denied")):
            result = run_full_pipeline(FIXTURE, out, None, 12)  # must not raise
        self.assertEqual(_stage(result, StageId.EXPORT).status, StageStatus.FAILED)
        self.assertEqual(_stage(result, StageId.EXPORT).error.category, "PermissionError")
        self.assertEqual(result.status, RunStatus.FAILED)  # EXPORT is required for minimal usefulness

    def test_dependent_stages_skip_rather_than_crash_on_upstream_failure(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.full_pipeline.stages.resolve_calls", side_effect=RuntimeError("boom")):
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertEqual(_stage(result, StageId.CALL_RESOLUTION).status, StageStatus.FAILED)
        self.assertEqual(_stage(result, StageId.WEB_ENTRY_RESOLUTION).status, StageStatus.SKIPPED_DUE_TO_UPSTREAM_FAILURE)
        self.assertEqual(_stage(result, StageId.FLOW_RESOLUTION).status, StageStatus.SKIPPED_DUE_TO_UPSTREAM_FAILURE)
        # independent stages continue
        self.assertEqual(_stage(result, StageId.DATABASE_RESOLUTION).status, StageStatus.SUCCESS)
        self.assertEqual(_stage(result, StageId.DEPENDENCY_RESOLUTION).status, StageStatus.SUCCESS)
        self.assertEqual(_stage(result, StageId.FINAL_SUMMARY).status, StageStatus.SUCCESS)


class SourceImmutabilityTests(unittest.TestCase):
    def test_fixture_untouched_across_rerun_partial_and_stale_proposal_cleanup(self) -> None:
        fixture_files = sorted(FIXTURE.rglob("*"))
        before = {p: p.read_bytes() for p in fixture_files if p.is_file()}
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.full_pipeline.stages.build_context_artifacts", side_effect=OSError("boom")):
            run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
        after = {p: p.read_bytes() for p in fixture_files if p.is_file()}
        self.assertEqual(before, after)

    def test_reset_stale_proposal_artifacts_never_touches_the_source_repository(self) -> None:
        # `reset_stale_proposal_artifacts` only ever descends into
        # `<output>/proposals` -- passing the fixture's own root proves it
        # cannot reach anything under the analyzed repository even if
        # misused, since the fixture has no `proposals/` directory of its
        # own for it to find.
        before = sorted(FIXTURE.rglob("*"))
        reset_stale_proposal_artifacts(FIXTURE)
        after = sorted(FIXTURE.rglob("*"))
        self.assertEqual(before, after)


class PathSafetyTests(unittest.TestCase):
    """AI/provider-controlled content must never control a filesystem path."""

    def test_proposal_filenames_are_fixed_regardless_of_ai_statement_content(self) -> None:
        malicious_response = {
            "findings": [
                {
                    "statement": "../../escape/attempt/../../etc/passwd",
                    "confidence": "UNCERTAIN",
                    "evidence_refs": ["DAO-0197413858"],
                }
            ]
        }
        provider = _fake_provider(structured_response=malicious_response)
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
            proposals_dir = Path(out) / "proposals"
            self.assertEqual(
                sorted(p.name for p in proposals_dir.iterdir()),
                ["AI_PROPOSALS.json", "AI_PROPOSALS_PENDING_REVIEW.md"],
            )
            # the traversal-shaped text is present only as JSON/Markdown VALUE content
            envelope = json.loads((proposals_dir / "AI_PROPOSALS.json").read_text(encoding="utf-8"))
            self.assertIn("../../escape/attempt/../../etc/passwd", envelope["proposals"][0]["statement"])
        self.assertGreater(result.proposal_count, 0)

    def test_output_never_written_outside_the_selected_output_directory(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as parent:
            out = Path(parent) / "chosen_output"
            run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
            written = {p for p in Path(parent).rglob("*") if p.is_file()}
            self.assertTrue(all(str(out) in str(p) for p in written))


class ApprovalAndCanonicalBoundaryTests(unittest.TestCase):
    def test_no_approval_and_no_canonical_knowledge_produced(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
            self.assertFalse((Path(out) / "approvals").exists())
            self.assertFalse((Path(out) / "canonical").exists())
        self.assertFalse(result.technical_lead_approval)
        self.assertFalse(result.canonical_knowledge_produced)


class ExitCodeAndLegacyUnchangedTests(unittest.TestCase):
    def test_exit_codes_remain_0_1_2_4(self) -> None:
        self.assertEqual(EXIT_SUCCESS, 0)
        self.assertEqual(EXIT_PARTIAL, 1)
        self.assertEqual(EXIT_FAILED, 4)
        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(main(["full", str(FIXTURE), "--output", out]), 0)

    def test_analyze_and_legacy_behavior_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            indexes = analyze_repository(FIXTURE, out, None, 12)
            self.assertFalse((Path(out) / "RUN_SUMMARY.json").exists())
        self.assertEqual(indexes["errors"], [])


if __name__ == "__main__":
    unittest.main()
