"""V4.2-R5.1 -- Exit-Code Contract and Real-Provider Guard: verification tests.

Covers:

1. One consolidated, explicit test of all four externally observable exit
   codes (`SUCCESS -> 0`, `PARTIAL -> 1`, `FAILED -> 4`, argparse usage
   error -> `2`), so this contract cannot drift accidentally.
2. The real-provider guard installed by `tests/__init__.py`: any attempt
   to resolve a real provider through
   `legacy_documenter.orchestration.ai_interpretation._resolve_provider`
   during a test run fails loudly (`RuntimeError`), never silently reaches
   a real provider.
3. `run_full_pipeline(..., allow_ai_interpretation=True)` with no injected
   provider still fails safely (a structured `FAILED` `AI_INTERPRETATION`
   stage, overall `PARTIAL`) rather than crashing the whole process or
   reaching a real provider.
4. The documented safe manual-verification path
   (`tools/manual_verify_full_pipeline`) never reaches `_resolve_provider`.

REAL_AI_RUNTIME_CALL_ALLOWED=false: no test here uses a real provider; the
guard test in this module deliberately calls the blocked seam directly to
prove it raises, rather than relying on an accidental real call.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.cli.execution_model import RunStatus, StageStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.cli.router import EXIT_FAILED, EXIT_PARTIAL, EXIT_SUCCESS
from legacy_documenter.cli.stage_identity import StageId
from legacy_documenter.main import main
from legacy_documenter.orchestration import ai_interpretation

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "v4_2_r3_sample"


def _stage(result, stage_id: StageId):
    return next(s for s in result.stages if s.stage is stage_id)


class ExitCodeContractTests(unittest.TestCase):
    """The authoritative contract (Technical Lead, V4.2-R5.1): 0/1/4, argparse's own 2."""

    def test_router_constants_match_the_authoritative_contract(self) -> None:
        self.assertEqual(EXIT_SUCCESS, 0)
        self.assertEqual(EXIT_PARTIAL, 1)
        self.assertEqual(EXIT_FAILED, 4)

    def test_all_four_externally_observable_exit_codes(self) -> None:
        # SUCCESS -> 0
        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(main(["full", str(FIXTURE), "--output", out]), 0)

        # PARTIAL -> 1 (readiness's own SUCCESS/PARTIAL mapping, established R1)
        proc_readiness_ok = subprocess.run(
            [sys.executable, "main.py", "readiness"], cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(proc_readiness_ok.returncode, 0)

        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.full_pipeline.stages.build_context_artifacts", side_effect=OSError("boom")):
            self.assertEqual(main(["full", str(FIXTURE), "--output", out]), 1)

        # FAILED -> 4
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.full_pipeline.stages.export_artifacts", side_effect=OSError("disk full")):
            self.assertEqual(main(["full", str(FIXTURE), "--output", out]), 4)

        # argparse usage error -> 2 (never reassigned by this project's own code)
        proc_usage_error = subprocess.run(
            [sys.executable, "main.py", "analyze"], cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(proc_usage_error.returncode, 2)

    def test_no_stale_r1_placeholder_code_reused(self) -> None:
        # Exit code 3 (R1's retired NOT_IMPLEMENTED_FOR_R1 placeholder) must
        # never reappear as a mapped value for any RunStatus.
        from legacy_documenter.cli.router import _EXIT_CODE_BY_STATUS
        self.assertNotIn(3, _EXIT_CODE_BY_STATUS.values())


class RealProviderGuardTests(unittest.TestCase):
    """`tests/__init__.py` must have replaced `_resolve_provider` with a raising stub."""

    def test_resolve_provider_is_blocked_for_the_test_suite(self) -> None:
        with self.assertRaises(RuntimeError) as ctx:
            ai_interpretation._resolve_provider()
        self.assertIn("REAL_AI_RUNTIME_CALL_ALLOWED=false", str(ctx.exception))

    def test_full_pipeline_without_injected_provider_fails_safely_not_silently(self) -> None:
        # No `ai_provider=` passed -- if the guard were absent, this would
        # attempt to resolve (and, in an environment with one available,
        # actually reach) a real provider. With the guard installed, it
        # must instead surface a structured, non-fatal failure.
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True)
        self.assertEqual(_stage(result, StageId.AI_INTERPRETATION).status, StageStatus.FAILED)
        self.assertEqual(
            _stage(result, StageId.PROPOSAL_GENERATION).status, StageStatus.SKIPPED_DUE_TO_UPSTREAM_FAILURE,
        )
        self.assertEqual(result.status, RunStatus.PARTIAL)
        self.assertIn("RuntimeError", _stage(result, StageId.AI_INTERPRETATION).error.category)

    def test_explicit_patch_of_resolve_provider_still_works_on_top_of_the_guard(self) -> None:
        # V4.2-R4's own tests patch `_resolve_provider` explicitly (to assert
        # it is/isn't called); `unittest.mock.patch` must still layer cleanly
        # on top of this module's baseline stub.
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.orchestration.ai_interpretation._resolve_provider",
                   side_effect=AssertionError("must not resolve a provider without opt-in")):
            run_full_pipeline(FIXTURE, out, None, 12)  # would raise if provider resolution were attempted

    def test_guard_does_not_block_direct_copilot_or_gemini_class_construction(self) -> None:
        # Existing unit tests (test_v3_r6.py, test_v3_r6_1.py) construct
        # CopilotProvider/GeminiProvider directly with an injected fake
        # client/transport -- the guard must target only the real-provider
        # *resolution* seam, never these classes themselves.
        from legacy_documenter.llm.core import ProviderConfig
        from legacy_documenter.llm.providers.copilot import CopilotProvider
        provider = CopilotProvider(ProviderConfig("COPILOT", "c", "m"), client_factory=lambda: object())
        self.assertIsInstance(provider, CopilotProvider)


class SafeManualVerificationTests(unittest.TestCase):
    """`tools/manual_verify_full_pipeline` must be usable and never reach a real provider."""

    def test_manual_verification_tool_never_calls_resolve_provider(self) -> None:
        from tools.manual_verify_full_pipeline import main as manual_main
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.orchestration.ai_interpretation._resolve_provider",
                   side_effect=AssertionError("manual verification tool must never resolve a real provider")):
            exit_code = manual_main([str(FIXTURE), "--output", out, "--allow-ai-interpretation"])
        self.assertEqual(exit_code, 0)

    def test_manual_verification_tool_can_demonstrate_success_and_failure(self) -> None:
        from tools.manual_verify_full_pipeline import main as manual_main
        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(
                manual_main([str(FIXTURE), "--output", out, "--allow-ai-interpretation", "--forced-status", "PROVIDER_ERROR"]),
                0,
            )


if __name__ == "__main__":
    unittest.main()
