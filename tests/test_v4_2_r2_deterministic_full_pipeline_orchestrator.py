"""V4.2-R2 -- Deterministic Full Pipeline Orchestrator: verification tests.

Covers, at minimum:

1. `full` executes the real deterministic pipeline (no longer the R1 placeholder).
2. Stage ordering matches SCAN -> EXTRACTION -> CALL_RESOLUTION ->
   WEB_ENTRY_RESOLUTION -> DATABASE_RESOLUTION -> FLOW_RESOLUTION ->
   DEPENDENCY_RESOLUTION -> EXPORT -> CONTEXT -> FINAL_SUMMARY.
3. A clean run -> SUCCESS; a recoverable stage failure -> PARTIAL; a failure
   that prevents EXTRACTION or EXPORT from completing -> FAILED.
4. An upstream stage failure marks its dependents
   SKIPPED_DUE_TO_UPSTREAM_FAILURE without executing them, while an
   independent downstream stage still runs.
5. Extraction errors are preserved and downgrade the run to PARTIAL.
6. Structured errors never carry a raw traceback.
7. The RUN_SUMMARY.json artifact is deterministic (same inputs -> same bytes).
8. AI_INVOKED / CANONICAL_KNOWLEDGE_PRODUCED / TECHNICAL_LEAD_APPROVAL are
   always false in R2.
9. The analyzed repository is never modified.
10. `analyze`/legacy/`readiness` remain compatible; `full` never imports or
    calls AI/knowledge/approval/canonical/projection/Plugin capability.

This module adds no new production capability; it only characterizes the R2
deterministic orchestrator built on the R1 execution model.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.analysis.call_resolver import CallResolver
from legacy_documenter.analysis.dependency_resolver import DependencyResolver
from legacy_documenter.cli.execution_model import RunStatus, StageStatus
from legacy_documenter.cli.full_pipeline import RUN_SUMMARY_JSON, RUN_SUMMARY_MARKDOWN, run_full_pipeline
from legacy_documenter.cli.stage_identity import StageId
from legacy_documenter.extractors.call_extractor import CallExtractor
from legacy_documenter.main import analyze_repository

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "v2_r1_sample"

# V4.2-R3 added the DOCUMENTATION stage between CONTEXT and FINAL_SUMMARY;
# V4.2-R4 added AI_INTERPRETATION/PROPOSAL_GENERATION between DOCUMENTATION
# and FINAL_SUMMARY, always present in the stage list (NOT_RUN unless
# --allow-ai-interpretation was passed -- see
# docs/V4_2/V4_2_R4_AI_INTERPRETATION_AND_PROPOSAL_INTEGRATION_RESULT.md).
# This constant tracks the live `full` stage order, the same way the
# R1/R2/R3 maintainability-inventory deltas track the live production tree.
EXPECTED_STAGE_ORDER = (
    StageId.SCAN, StageId.EXTRACTION, StageId.CALL_RESOLUTION, StageId.WEB_ENTRY_RESOLUTION,
    StageId.DATABASE_RESOLUTION, StageId.FLOW_RESOLUTION, StageId.DEPENDENCY_RESOLUTION,
    StageId.EXPORT, StageId.CONTEXT, StageId.DOCUMENTATION, StageId.AI_INTERPRETATION,
    StageId.PROPOSAL_GENERATION, StageId.FINAL_SUMMARY,
)
# This R2 test module never passes --allow-ai-interpretation, so these two
# stages are always NOT_RUN here, not SUCCESS -- unlike every deterministic
# stage in R2/R3's scope.
_NOT_RUN_WITHOUT_AI_OPT_IN = {StageId.AI_INTERPRETATION, StageId.PROPOSAL_GENERATION}


def _stage_status(result, stage_id: StageId) -> StageStatus:
    for stage in result.stages:
        if stage.stage is stage_id:
            return stage.status
    raise AssertionError(f"{stage_id} missing from stages: {[s.stage for s in result.stages]}")


class CleanRunTests(unittest.TestCase):
    """A clean run against the committed fixture must succeed end to end."""

    def test_full_reports_success_with_every_stage_succeeding(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertEqual(tuple(s.stage for s in result.stages), EXPECTED_STAGE_ORDER)
        for stage in result.stages:
            if stage.stage in _NOT_RUN_WITHOUT_AI_OPT_IN:
                self.assertEqual(stage.status, StageStatus.NOT_RUN, msg=f"{stage.stage} was not NOT_RUN")
            else:
                self.assertEqual(stage.status, StageStatus.SUCCESS, msg=f"{stage.stage} was not SUCCESS")

    def test_full_writes_run_summary_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            self.assertTrue((Path(out) / RUN_SUMMARY_JSON).exists())
            self.assertTrue((Path(out) / RUN_SUMMARY_MARKDOWN).exists())

    def test_approval_boundary_invariants_are_always_false(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertFalse(result.ai_invoked)
        self.assertFalse(result.canonical_knowledge_produced)
        self.assertFalse(result.technical_lead_approval)

        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            payload = json.loads((Path(out) / RUN_SUMMARY_JSON).read_text(encoding="utf-8"))
        self.assertEqual(payload["ai_invoked"], False)
        self.assertEqual(payload["canonical_knowledge_produced"], False)
        self.assertEqual(payload["technical_lead_approval"], False)


class UpstreamFailureTests(unittest.TestCase):
    """An upstream stage failure must skip its dependents, not fake them or crash the run."""

    def test_call_resolution_failure_skips_web_entry_and_flow_but_not_database_or_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch.object(CallResolver, "resolve", side_effect=RuntimeError("call-resolver-boom")):
            result = run_full_pipeline(FIXTURE, out, None, 12)

        self.assertEqual(_stage_status(result, StageId.CALL_RESOLUTION), StageStatus.FAILED)
        self.assertEqual(_stage_status(result, StageId.WEB_ENTRY_RESOLUTION), StageStatus.SKIPPED_DUE_TO_UPSTREAM_FAILURE)
        self.assertEqual(_stage_status(result, StageId.FLOW_RESOLUTION), StageStatus.SKIPPED_DUE_TO_UPSTREAM_FAILURE)
        # DATABASE_RESOLUTION and DEPENDENCY_RESOLUTION only depend on EXTRACTION,
        # not on CALL_RESOLUTION -- they must still run.
        self.assertEqual(_stage_status(result, StageId.DATABASE_RESOLUTION), StageStatus.SUCCESS)
        self.assertEqual(_stage_status(result, StageId.DEPENDENCY_RESOLUTION), StageStatus.SUCCESS)
        # EXTRACTION succeeded and EXPORT can still run with partial data -> PARTIAL, not FAILED.
        self.assertEqual(_stage_status(result, StageId.EXPORT), StageStatus.SUCCESS)
        self.assertEqual(result.status, RunStatus.PARTIAL)

    def test_skipped_stage_error_names_the_blocking_stage(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch.object(CallResolver, "resolve", side_effect=RuntimeError("boom")):
            result = run_full_pipeline(FIXTURE, out, None, 12)
        web_entry = next(s for s in result.stages if s.stage is StageId.WEB_ENTRY_RESOLUTION)
        self.assertIsNotNone(web_entry.error)
        self.assertIn("CALL_RESOLUTION", web_entry.error.message)


class FatalFailureTests(unittest.TestCase):
    """A failure that prevents a minimally useful output package must report FAILED."""

    def test_export_failure_makes_the_run_failed(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.full_pipeline.stages.export_artifacts", side_effect=OSError("disk full")):
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertEqual(_stage_status(result, StageId.EXPORT), StageStatus.FAILED)
        self.assertEqual(result.status, RunStatus.FAILED)

    def test_scan_failure_skips_everything_downstream_of_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.full_pipeline.stages.scan_repository", side_effect=OSError("cannot read repository")):
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertEqual(_stage_status(result, StageId.SCAN), StageStatus.FAILED)
        self.assertEqual(_stage_status(result, StageId.EXTRACTION), StageStatus.SKIPPED_DUE_TO_UPSTREAM_FAILURE)
        self.assertEqual(_stage_status(result, StageId.EXPORT), StageStatus.SKIPPED_DUE_TO_UPSTREAM_FAILURE)
        self.assertEqual(result.status, RunStatus.FAILED)
        # Even a FAILED run still gets a run summary written -- FINAL_SUMMARY still executes.
        self.assertEqual(_stage_status(result, StageId.FINAL_SUMMARY), StageStatus.SUCCESS)


class ExtractionErrorTests(unittest.TestCase):
    """Per-file extraction errors must be preserved and downgrade the run to PARTIAL."""

    def test_extractor_failure_is_preserved_in_exported_errors_and_downgrades_to_partial(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch.object(CallExtractor, "extract", side_effect=ValueError("call-extract-boom")):
            result = run_full_pipeline(FIXTURE, out, None, 12)
            self.assertEqual(result.status, RunStatus.PARTIAL)
            errors_path = Path(out) / "index" / "errors.json"
            errors = json.loads(errors_path.read_text(encoding="utf-8"))

        self.assertGreaterEqual(len(errors), 1)
        self.assertEqual(errors[0]["extractor"], "CallExtractor")
        self.assertIn("call-extract-boom", errors[0]["error"])


class StructuredErrorTests(unittest.TestCase):
    """Stage errors must be a structured contract, never a raw traceback."""

    def test_stage_error_message_has_no_traceback_markers(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch.object(DependencyResolver, "resolve", side_effect=RuntimeError("dependency-resolver-boom")):
            result = run_full_pipeline(FIXTURE, out, None, 12)
        dependency_stage = next(s for s in result.stages if s.stage is StageId.DEPENDENCY_RESOLUTION)
        self.assertIsNotNone(dependency_stage.error)
        self.assertNotIn("Traceback", dependency_stage.error.message)
        self.assertNotIn('  File "', dependency_stage.error.message)
        self.assertEqual(dependency_stage.error.category, "RuntimeError")


class DeterminismTests(unittest.TestCase):
    """The RUN_SUMMARY.json artifact must be byte-identical for equivalent runs."""

    def test_run_summary_json_is_identical_across_two_runs(self) -> None:
        with tempfile.TemporaryDirectory() as out_a, tempfile.TemporaryDirectory() as out_b:
            run_full_pipeline(FIXTURE, out_a, None, 12)
            run_full_pipeline(FIXTURE, out_b, None, 12)
            content_a = (Path(out_a) / RUN_SUMMARY_JSON).read_text(encoding="utf-8")
            content_b = (Path(out_b) / RUN_SUMMARY_JSON).read_text(encoding="utf-8")
        self.assertEqual(content_a, content_b)

    def test_run_summary_json_has_no_uuid_or_timestamp_fields(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            payload = json.loads((Path(out) / RUN_SUMMARY_JSON).read_text(encoding="utf-8"))
        rendered_keys = set(payload) | {k for stage in payload["stages"] for k in stage}
        for key in rendered_keys:
            self.assertNotIn("uuid", key.lower())
            self.assertNotIn("timestamp", key.lower())


class SourceImmutabilityTests(unittest.TestCase):
    """The analyzed repository must never be modified by `full`."""

    def test_fixture_files_are_byte_identical_before_and_after(self) -> None:
        fixture_files = sorted(FIXTURE.rglob("*"))
        before = {f: hashlib.sha256(f.read_bytes()).hexdigest() for f in fixture_files if f.is_file()}
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
        after_files = sorted(FIXTURE.rglob("*"))
        after = {f: hashlib.sha256(f.read_bytes()).hexdigest() for f in after_files if f.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(set(before), set(after))


class AnalyzeEquivalenceTests(unittest.TestCase):
    """`analyze` (and the legacy bare invocation) must remain behaviorally unchanged by R2's refactor."""

    def test_analyze_output_matches_pre_r2_shape_on_the_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            indexes = analyze_repository(FIXTURE, out, None, 12)
            self.assertEqual(indexes["errors"], [])
            self.assertEqual(len(indexes["symbols"]), 2)
            self.assertEqual(len(indexes["projects"]), 1)
            self.assertTrue((Path(out) / "index" / "repository.json").exists())
            self.assertTrue((Path(out) / "documentation" / "PROJECT_OVERVIEW.md").exists())
            self.assertTrue((Path(out) / "context" / "projects.json").exists())
            self.assertTrue((Path(out) / "ai_context" / "SYSTEM_CONTEXT.json").exists())
            # `analyze` must never write a run summary -- that is `full`-only.
            self.assertFalse((Path(out) / RUN_SUMMARY_JSON).exists())

    def test_legacy_and_explicit_analyze_produce_identical_output_trees(self) -> None:
        with tempfile.TemporaryDirectory() as out_legacy, tempfile.TemporaryDirectory() as out_analyze:
            proc_legacy = subprocess.run(
                [sys.executable, "main.py", str(FIXTURE), "--output", out_legacy],
                cwd=ROOT, capture_output=True, text=True,
            )
            proc_analyze = subprocess.run(
                [sys.executable, "main.py", "analyze", str(FIXTURE), "--output", out_analyze],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(proc_legacy.returncode, 0, proc_legacy.stderr)
            self.assertEqual(proc_analyze.returncode, 0, proc_analyze.stderr)

            legacy_files = {p.relative_to(out_legacy) for p in Path(out_legacy).rglob("*") if p.is_file()}
            analyze_files = {p.relative_to(out_analyze) for p in Path(out_analyze).rglob("*") if p.is_file()}
            self.assertEqual(legacy_files, analyze_files)

            for rel in sorted(legacy_files):
                legacy_bytes = (Path(out_legacy) / rel).read_bytes()
                analyze_bytes = (Path(out_analyze) / rel).read_bytes()
                if rel == Path("index") / "repository.json":
                    # duration_seconds is wall-clock and legitimately not
                    # guaranteed identical between two separate process runs;
                    # every other field must still match exactly.
                    legacy_json = json.loads(legacy_bytes)
                    analyze_json = json.loads(analyze_bytes)
                    legacy_json["duration_seconds"] = None
                    analyze_json["duration_seconds"] = None
                    self.assertEqual(legacy_json, analyze_json, msg=str(rel))
                else:
                    self.assertEqual(legacy_bytes, analyze_bytes, msg=str(rel))


class ReadinessCompatibilityTests(unittest.TestCase):
    """`readiness` (both routes) must remain unaffected by the R2 orchestrator change."""

    def test_module_entry_point_still_prints_matching_json(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "legacy_documenter.knowledge.readiness"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["readiness"], "READY")
        self.assertEqual(payload["provider_calls"], 0)
        self.assertEqual(payload["real_llm_calls"], 0)

    def test_cli_readiness_command_still_works(self) -> None:
        proc = subprocess.run(
            [sys.executable, "main.py", "readiness"], cwd=ROOT, capture_output=True, text=True, check=True,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["readiness"], "READY")


class NoAiOrKnowledgeCapabilityTests(unittest.TestCase):
    """`pipeline_stages.py` (the deterministic stage functions `analyze` also
    uses) must never gain AI/knowledge capability, opt-in or not. `full_pipeline.py`
    legitimately gained `llm`/`knowledge.proposals` references in V4.2-R4 (the
    opt-in AI_INTERPRETATION/PROPOSAL_GENERATION wiring, gated by
    `allow_ai_interpretation`) -- see
    docs/V4_2/V4_2_R4_AI_INTERPRETATION_AND_PROPOSAL_INTEGRATION_RESULT.md for
    the updated boundary. Approval/canonical/projection/Plugin capability
    remains forbidden in both files unconditionally, opt-in or not.
    """

    def test_pipeline_stages_module_imports_no_forbidden_capability(self) -> None:
        import legacy_documenter.cli.pipeline_stages as pipeline_stages_module

        forbidden = [
            "legacy_documenter.analysis.deep_interpretation",
            "legacy_documenter.llm",
            "legacy_documenter.knowledge.proposals",
            "legacy_documenter.knowledge.approval",
            "legacy_documenter.knowledge.canonical",
            "legacy_documenter.knowledge.projection",
            "legacy_documenter.knowledge.plugin_projection",
            "legacy_documenter.knowledge.ingestion",
        ]
        source = Path(pipeline_stages_module.__file__).read_text(encoding="utf-8")
        for token in forbidden:
            self.assertNotIn(token, source, msg=f"pipeline_stages.py must not reference {token!r}")

    def test_full_pipeline_module_never_imports_approval_canonical_or_projection(self) -> None:
        import legacy_documenter.cli.full_pipeline as full_pipeline_module

        forbidden = [
            "legacy_documenter.analysis.deep_interpretation",
            "legacy_documenter.knowledge.approval",
            "legacy_documenter.knowledge.canonical",
            "legacy_documenter.knowledge.projection",
            "legacy_documenter.knowledge.plugin_projection",
            "legacy_documenter.knowledge.ingestion",
        ]
        source = Path(full_pipeline_module.__file__).read_text(encoding="utf-8")
        for token in forbidden:
            self.assertNotIn(token, source, msg=f"full_pipeline.py must not reference {token!r}")


if __name__ == "__main__":
    unittest.main()
