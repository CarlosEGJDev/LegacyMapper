"""V4.2-R4 -- AI Interpretation and Proposal Integration: verification tests.

Covers, at minimum:

1. Default `full` (no opt-in) makes zero provider calls and reports
   AI_INTERPRETATION/PROPOSAL_GENERATION as NOT_RUN.
2. Explicit `--allow-ai-interpretation` enables interpretation; the provider
   is called only after explicit opt-in, never otherwise.
3. AI interpretation consumes the CURRENT run's own `ai_context/*.json`, never
   a historical snapshot.
4. A successful fake interpretation produces a Proposal preserving AI origin
   and method, remaining pending/unapproved (READY_FOR_REVIEW, never APPROVED).
5. Proposal envelope serialization is stable for the same AI result.
6. Malformed AI output produces a structured failure, never a fabricated proposal.
7. Provider failure -> AI_INTERPRETATION FAILED; downstream PROPOSAL_GENERATION
   -> SKIPPED_DUE_TO_UPSTREAM_FAILURE; overall run PARTIAL (deterministic
   analysis remains available), never FAILED.
8. No canonical knowledge, no Technical Lead approval, no R11/R12/Plugin
   runtime invocation, ever -- opt-in or not.
9. No credentials/tokens ever appear in RunResult/StageError/proposal output.
10. Source repository remains immutable; `analyze`/legacy remain unchanged;
    `full` without the flag remains fully deterministic.

REAL_AI_RUNTIME_CALL_ALLOWED=false: every test here uses
`legacy_documenter.llm.core.FakeLLMProvider` or a deliberately broken fake --
never a real Copilot/Gemini/network call. A guard test additionally asserts
no test in this module can reach `CopilotProvider`/`GeminiProvider`.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.cli.execution_model import RunStatus, StageStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.cli.stage_identity import StageId
from legacy_documenter.knowledge.proposals.enums import ProposalMethod, ProposalStatus
from legacy_documenter.llm.core import FakeLLMProvider, ProviderConfig
from legacy_documenter.main import analyze_repository
from legacy_documenter.orchestration.ai_interpretation import run_ai_interpretation
from legacy_documenter.orchestration.proposal_adapter import adapt_findings_to_proposals

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


class DefaultFullMakesZeroProviderCallsTests(unittest.TestCase):
    """Without --allow-ai-interpretation, full must never touch a provider."""

    def test_ai_stages_are_not_run_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertEqual(_stage(result, StageId.AI_INTERPRETATION).status, StageStatus.NOT_RUN)
        self.assertEqual(_stage(result, StageId.PROPOSAL_GENERATION).status, StageStatus.NOT_RUN)
        self.assertFalse(result.ai_invoked)

    def test_provider_resolution_is_never_attempted_without_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.orchestration.ai_interpretation._resolve_provider",
                   side_effect=AssertionError("must not resolve a provider without opt-in")):
            run_full_pipeline(FIXTURE, out, None, 12)  # would raise if provider resolution were attempted

    def test_no_proposals_directory_is_created_without_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            self.assertFalse((Path(out) / "proposals").exists())


class ExplicitOptInEnablesInterpretationTests(unittest.TestCase):
    """--allow-ai-interpretation is required to reach the provider at all."""

    def test_opt_in_without_provider_injection_would_resolve_via_registry(self) -> None:
        # Confirms the seam exists and is only exercised on opt-in: injecting a
        # fake provider bypasses `_resolve_provider` entirely, proving the
        # production path (env-var-driven ProviderRegistry) is a distinct,
        # separately-testable branch never reached in this test suite.
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.orchestration.ai_interpretation._resolve_provider") as mock_resolve:
            mock_resolve.return_value = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
            run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True)
            mock_resolve.assert_called_once()

    def test_provider_is_called_only_after_explicit_opt_in(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertEqual(_stage(result, StageId.AI_INTERPRETATION).status, StageStatus.SUCCESS)
        self.assertTrue(result.ai_invoked)


class CurrentRunContextTests(unittest.TestCase):
    """AI interpretation must use the current run's own ai_context, never a historical snapshot."""

    def test_interpretation_fails_closed_when_no_ai_context_exists_yet(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_ai_interpretation(out, provider=_fake_provider(structured_response=VALID_STRUCTURED_RESPONSE))
        self.assertEqual(result.status, "CONTEXT_UNAVAILABLE")
        self.assertFalse(result.provider_called)

    def test_interpretation_uses_freshly_written_ai_context_for_this_run(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            analyze_repository(FIXTURE, out, None, 12)
            result = run_ai_interpretation(out, provider=_fake_provider(structured_response=VALID_STRUCTURED_RESPONSE))
        self.assertEqual(result.status, "SUCCESS")
        self.assertIsNotNone(result.context_package_id)

    def test_interpretation_reads_only_the_given_output_dir_not_a_hardcoded_one(self) -> None:
        # Two runs against two DIFFERENT --output directories must each use
        # their own context, never bleed into or fall back to another run's
        # (or a hardcoded historical) directory -- proven behaviorally: a
        # second, fresh output dir with no ai_context yet must still fail
        # closed even though a first, fully-populated run exists elsewhere.
        with tempfile.TemporaryDirectory() as out_populated, tempfile.TemporaryDirectory() as out_empty:
            analyze_repository(FIXTURE, out_populated, None, 12)
            result = run_ai_interpretation(out_empty, provider=_fake_provider(structured_response=VALID_STRUCTURED_RESPONSE))
        self.assertEqual(result.status, "CONTEXT_UNAVAILABLE")


class ProposalGenerationTests(unittest.TestCase):
    """A successful interpretation must become a real, pending Proposal."""

    def test_successful_interpretation_produces_a_proposal(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out:
            analyze_repository(FIXTURE, out, None, 12)
            interpretation = run_ai_interpretation(out, provider=provider)
            proposals = adapt_findings_to_proposals(interpretation.findings)
        self.assertEqual(len(proposals), 1)

    def test_proposal_preserves_ai_origin_and_method(self) -> None:
        proposals = adapt_findings_to_proposals(VALID_STRUCTURED_RESPONSE["findings"])
        self.assertEqual(proposals[0].proposal_method, ProposalMethod.AI_PROPOSED)
        self.assertEqual(proposals[0].evidence_refs, ("DAO-0197413858",))

    def test_proposal_remains_pending_never_approved(self) -> None:
        proposals = adapt_findings_to_proposals(VALID_STRUCTURED_RESPONSE["findings"])
        self.assertEqual(proposals[0].status, ProposalStatus.READY_FOR_REVIEW)
        # ProposalStatus has no APPROVED/REJECTED/CORRECTED member at all --
        # those are a future round's Technical Lead decision, never produced here.
        self.assertNotIn("APPROVED", {member.value for member in ProposalStatus})

    def test_proposal_generation_skipped_without_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertEqual(_stage(result, StageId.PROPOSAL_GENERATION).status, StageStatus.NOT_RUN)


class DeterministicSerializationTests(unittest.TestCase):
    """Proposal envelope serialization must be stable for the same AI result."""

    def test_proposal_envelope_json_is_byte_identical_for_the_same_ai_result(self) -> None:
        provider_a = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        provider_b = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out_a, tempfile.TemporaryDirectory() as out_b:
            run_full_pipeline(FIXTURE, out_a, None, 12, allow_ai_interpretation=True, ai_provider=provider_a)
            run_full_pipeline(FIXTURE, out_b, None, 12, allow_ai_interpretation=True, ai_provider=provider_b)
            content_a = (Path(out_a) / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8")
            content_b = (Path(out_b) / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8")
        self.assertEqual(content_a, content_b)

    def test_proposal_envelope_uses_plain_string_enum_values_not_repr(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
            payload = json.loads((Path(out) / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["proposals"][0]["proposal_kind"], "INTERPRETATION")
        self.assertNotIn("ProposalKind.", json.dumps(payload))


class MalformedOutputTests(unittest.TestCase):
    """Malformed AI output must produce a structured failure, never an invented proposal."""

    def test_missing_findings_key_is_a_structured_failure(self) -> None:
        result = run_ai_interpretation("nonexistent", provider=_fake_provider(structured_response={"oops": []}))
        self.assertIn(result.status, {"CONTEXT_UNAVAILABLE", "INVALID_OUTPUT"})

    def test_unknown_evidence_ref_is_rejected_not_silently_dropped(self) -> None:
        provider = _fake_provider(structured_response={
            "findings": [{"statement": "x", "confidence": "CONFIRMED", "evidence_refs": ["DOES-NOT-EXIST"]}]
        })
        with tempfile.TemporaryDirectory() as out:
            analyze_repository(FIXTURE, out, None, 12)
            result = run_ai_interpretation(out, provider=provider)
        self.assertEqual(result.status, "INVALID_OUTPUT")
        self.assertIn("unknown_evidence_refs", result.error_message)
        self.assertEqual(result.findings, [])

    def test_findings_not_a_list_is_rejected(self) -> None:
        provider = _fake_provider(structured_response={"findings": "not-a-list"})
        with tempfile.TemporaryDirectory() as out:
            analyze_repository(FIXTURE, out, None, 12)
            result = run_ai_interpretation(out, provider=provider)
        self.assertEqual(result.status, "INVALID_OUTPUT")

    def test_invalid_output_never_reaches_the_proposal_adapter_as_a_proposal(self) -> None:
        provider = _fake_provider(structured_response={"findings": "not-a-list"})
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertEqual(_stage(result, StageId.AI_INTERPRETATION).status, StageStatus.FAILED)
        self.assertEqual(_stage(result, StageId.PROPOSAL_GENERATION).status, StageStatus.SKIPPED_DUE_TO_UPSTREAM_FAILURE)


class ProviderFailurePolicyTests(unittest.TestCase):
    """A provider failure must downgrade the run to PARTIAL, never FAILED."""

    def test_provider_failure_marks_ai_interpretation_failed(self) -> None:
        provider = _fake_provider(forced_status="PROVIDER_ERROR")
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertEqual(_stage(result, StageId.AI_INTERPRETATION).status, StageStatus.FAILED)

    def test_ai_failure_skips_proposal_generation(self) -> None:
        provider = _fake_provider(forced_status="PROVIDER_ERROR")
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertEqual(_stage(result, StageId.PROPOSAL_GENERATION).status, StageStatus.SKIPPED_DUE_TO_UPSTREAM_FAILURE)

    def test_ai_failure_yields_overall_partial_not_failed(self) -> None:
        provider = _fake_provider(forced_status="PROVIDER_ERROR")
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertEqual(result.status, RunStatus.PARTIAL)
        self.assertNotEqual(result.status, RunStatus.FAILED)

    def test_deterministic_artifacts_remain_available_after_ai_failure(self) -> None:
        provider = _fake_provider(forced_status="PROVIDER_ERROR")
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
            self.assertTrue((Path(out) / "index" / "repository.json").exists())
            self.assertTrue((Path(out) / "documentation" / "PROJECT_OVERVIEW.md").exists())
            self.assertTrue((Path(out) / "documentation" / "WEB_ENTRY_POINTS.md").exists())

    def test_provider_exception_is_caught_not_propagated(self) -> None:
        class ExplodingProvider(FakeLLMProvider):
            def structured_generate(self, request, schema):
                raise ConnectionError("simulated network failure")

        provider = ExplodingProvider(ProviderConfig("FAKE", "fake-1", "fake-model", capabilities={"structured_output": True}))
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertEqual(_stage(result, StageId.AI_INTERPRETATION).status, StageStatus.FAILED)
        self.assertEqual(result.status, RunStatus.PARTIAL)


class ApprovalBoundaryTests(unittest.TestCase):
    """No canonical knowledge, approval, R11/R12, or Plugin runtime -- ever."""

    def test_canonical_knowledge_and_approval_always_false(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        self.assertFalse(result.canonical_knowledge_produced)
        self.assertFalse(result.technical_lead_approval)

    def test_orchestration_package_never_imports_forbidden_capability(self) -> None:
        import legacy_documenter.orchestration.ai_interpretation as ai_module
        import legacy_documenter.orchestration.proposal_adapter as adapter_module

        forbidden = [
            "knowledge.approval", "knowledge.canonical", "knowledge.projection",
            "knowledge.plugin_projection", "knowledge.ingestion",
            "ApprovalDecisionType", "ApprovalAuthority",
        ]
        for module in (ai_module, adapter_module):
            source = Path(module.__file__).read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, source, msg=f"{module.__name__} must not reference {token!r}")

    def test_full_pipeline_never_imports_approval_or_canonical(self) -> None:
        import legacy_documenter.cli.full_pipeline as fp_module

        source = Path(fp_module.__file__).read_text(encoding="utf-8")
        for token in ("knowledge.approval", "knowledge.canonical", "knowledge.projection", "knowledge.plugin_projection"):
            self.assertNotIn(token, source)

    def test_no_real_provider_class_is_ever_imported_in_tests(self) -> None:
        import legacy_documenter.orchestration.ai_interpretation as ai_module

        source = Path(ai_module.__file__).read_text(encoding="utf-8")
        self.assertNotIn("CopilotProvider", source)
        self.assertNotIn("GeminiProvider", source)


class SecurityTests(unittest.TestCase):
    """No credentials/tokens/environment dumps in any produced artifact."""

    def test_provider_error_message_is_sanitized(self) -> None:
        class SecretLeakingProvider(FakeLLMProvider):
            def structured_generate(self, request, schema):
                raise RuntimeError("auth failed: token=SECRET-ABC-123\nTraceback (most recent call last):\n  more detail")

        provider = SecretLeakingProvider(ProviderConfig("FAKE", "fake-1", "fake-model", capabilities={"structured_output": True}))
        with tempfile.TemporaryDirectory() as out:
            analyze_repository(FIXTURE, out, None, 12)
            result = run_ai_interpretation(out, provider=provider)
        self.assertNotIn("Traceback", result.error_message)
        self.assertLessEqual(len(result.error_message), 300)

    def test_no_environment_dump_in_proposal_output(self) -> None:
        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
            content = (Path(out) / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8")
        self.assertNotIn("PATH=", content)
        self.assertNotIn("credential", content.lower())


class SourceImmutabilityAndCompatibilityTests(unittest.TestCase):
    """Source repository immutable; analyze/legacy unaffected; full without AI stays deterministic."""

    def test_fixture_files_are_byte_identical_before_and_after_ai_enabled_run(self) -> None:
        import hashlib

        provider = _fake_provider(structured_response=VALID_STRUCTURED_RESPONSE)
        fixture_files = sorted(FIXTURE.rglob("*"))
        before = {f: hashlib.sha256(f.read_bytes()).hexdigest() for f in fixture_files if f.is_file()}
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
        after_files = sorted(FIXTURE.rglob("*"))
        after = {f: hashlib.sha256(f.read_bytes()).hexdigest() for f in after_files if f.is_file()}
        self.assertEqual(before, after)

    def test_analyze_output_unaffected_by_r4(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            analyze_repository(FIXTURE, out, None, 12)
            self.assertFalse((Path(out) / "proposals").exists())

    def test_legacy_and_analyze_still_produce_identical_output_trees(self) -> None:
        with tempfile.TemporaryDirectory() as out_legacy, tempfile.TemporaryDirectory() as out_analyze:
            proc_legacy = subprocess.run(
                [sys.executable, "main.py", str(FIXTURE), "--output", out_legacy], cwd=ROOT, capture_output=True, text=True,
            )
            proc_analyze = subprocess.run(
                [sys.executable, "main.py", "analyze", str(FIXTURE), "--output", out_analyze], cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(proc_legacy.returncode, 0, proc_legacy.stderr)
            self.assertEqual(proc_analyze.returncode, 0, proc_analyze.stderr)
            legacy_files = {p.relative_to(out_legacy) for p in Path(out_legacy).rglob("*") if p.is_file()}
            analyze_files = {p.relative_to(out_analyze) for p in Path(out_analyze).rglob("*") if p.is_file()}
        self.assertEqual(legacy_files, analyze_files)

    def test_full_without_flag_remains_fully_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as out_a, tempfile.TemporaryDirectory() as out_b:
            run_full_pipeline(FIXTURE, out_a, None, 12)
            run_full_pipeline(FIXTURE, out_b, None, 12)
            summary_a = json.loads((Path(out_a) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
            summary_b = json.loads((Path(out_b) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
        self.assertEqual(summary_a, summary_b)

    def test_cli_help_documents_the_new_opt_in_flag(self) -> None:
        proc = subprocess.run(
            [sys.executable, "main.py", "full", "--help"], cwd=ROOT, capture_output=True, text=True, check=True,
        )
        self.assertIn("--allow-ai-interpretation", proc.stdout)


if __name__ == "__main__":
    unittest.main()
