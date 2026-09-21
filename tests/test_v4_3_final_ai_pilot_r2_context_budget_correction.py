"""V4.3 final AI pilot R2 context-budget regression correction: verification tests.

The V4.3 final AI pilot R2 rerun failed both `AI_INTERPRETATION` attempts with
`CONTEXT_TOO_LARGE: budget_insufficient:profile=SMALL; budget_insufficient:profile=TINY`,
even though `ai_invoked` was `false` (the provider was never reached -- the
failure happened entirely inside the deterministic selection/budgeting layer).

Root cause (reproduced here and in the result document): the diversity
correction from the previous round (`ai_projection._bucketed_order` +
`_flow_richness_bucket`/`_record_richness_bucket`) orders richer candidates
first, but `AiProjectionBuilder.package`'s greedy character-budget loop used
to `break` on the FIRST candidate that did not fit, rather than skipping it
and trying the next one. A single very large, richness-prioritized record
could therefore block every smaller candidate that came after it in the
ordering, producing `BUDGET_INSUFFICIENT` at both `SMALL` and `TINY` even
though plenty of individually small candidates would have fit comfortably.

The fix changes that one `break` to a `continue`: an oversized candidate is
skipped, not fatal, and packaging keeps trying later candidates. This module
covers T1-T11 from the correction prompt using only synthetic fixtures --
no real Copilot call, no network, no LLM provider is reachable except through
`FakeLLMProvider`/`_ExplodingProvider`, exactly like the pre-existing R5 tests.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from legacy_documenter.context import ai_projection as aip
from legacy_documenter.context.hydration import EvidenceHydrator
from legacy_documenter.llm.core import FakeLLMProvider, ProviderConfig, measure_request_payload
from legacy_documenter.main import analyze_repository
from legacy_documenter.orchestration import ai_interpretation as ai

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "v4_2_r3_sample"

VALID_STRUCTURED_RESPONSE = {
    "findings": [{"statement": "x", "confidence": "CONFIRMED", "evidence_refs": []}]
}


def _fake_provider(**kwargs) -> FakeLLMProvider:
    config = ProviderConfig("FAKE", "fake-1", "fake-model", capabilities={"structured_output": True})
    return FakeLLMProvider(config, **kwargs)


class _ExplodingProvider(FakeLLMProvider):
    """Fails loudly if a test path ever reaches the provider when it must not."""

    def structured_generate(self, request, schema):  # pragma: no cover - must never run
        raise AssertionError("provider must not be called")


def _flow(fid: str, confidence: str = "confirmed", proj: list | None = None) -> dict:
    return {"id": fid, "entry_point_id": f"EP-{fid}", "confidence": confidence, "project_sequence": proj or ["P"]}


def _entry(fid: str) -> dict:
    return {"id": f"EP-{fid}", "webform": f"web/{fid}.ascx", "event": "Click", "handler": f"h_{fid}", "start_method": f"S_{fid}"}


def _oversized_rich_ix() -> dict:
    """T1 fixture: A (bucket 0, individually too large for SMALL/TINY), B (bucket
    0, fits), C (bucket 1, fits), D (bucket 3, fits if room remains)."""
    big_nodes = [f"DAO-BIG-{i}" for i in range(400)]
    paths = [
        {"path_id": "PATH-A", "flow_id": "FLOW-A", "nodes": big_nodes, "terminal_type": "stored_procedure",
         "terminal_target": "SP-A", "confidence": "confirmed", "evidence_refs": []},
        {"path_id": "PATH-B", "flow_id": "FLOW-B", "nodes": [], "terminal_type": "stored_procedure",
         "terminal_target": "SP-B", "confidence": "confirmed", "evidence_refs": []},
        {"path_id": "PATH-C", "flow_id": "FLOW-C", "nodes": ["DAO-C"], "terminal_type": "unresolved_boundary",
         "terminal_target": "DAO-C", "confidence": "confirmed", "evidence_refs": []},
        {"path_id": "PATH-D", "flow_id": "FLOW-D", "nodes": [], "terminal_type": "unresolved_boundary",
         "terminal_target": "UNRESOLVED-D", "confidence": "unresolved", "evidence_refs": []},
    ]
    data_access = [
        {"id": n, "class": "Repo", "method": "Save", "operation_kind": "write",
         "sql_operation": "INSERT", "confidence": "confirmed"} for n in big_nodes
    ] + [{"id": "DAO-C", "class": "Repo", "method": "Get", "operation_kind": "read",
          "sql_operation": "SELECT", "confidence": "confirmed"}]
    return {
        "functional_flows": [
            _flow("FLOW-A"), _flow("FLOW-B"), _flow("FLOW-C"), _flow("FLOW-D", confidence="unresolved"),
        ],
        "entry_points": [_entry("FLOW-A"), _entry("FLOW-B"), _entry("FLOW-C"), _entry("FLOW-D")],
        "functional_paths": paths,
        "data_access": data_access,
        "stored_procedures": [
            {"id": "SP-A", "name": "PKG.A", "package": "PKG", "procedure": "A"},
            {"id": "SP-B", "name": "PKG.B", "package": "PKG", "procedure": "B"},
        ],
        "sql_operations": [], "data_parameters": [],
    }


def _all_oversized_ix() -> dict:
    """T2 fixture: every flow, individually, is too large for SMALL and TINY."""
    ix = {"functional_flows": [], "entry_points": [], "functional_paths": [],
          "data_access": [], "stored_procedures": [], "sql_operations": [], "data_parameters": []}
    for i in range(3):
        fid = f"FLOW-BIG-{i}"
        nodes = [f"DAO-{fid}-{n}" for n in range(400)]
        ix["functional_flows"].append(_flow(fid))
        ix["entry_points"].append(_entry(fid))
        ix["functional_paths"].append({
            "path_id": f"PATH-{fid}", "flow_id": fid, "nodes": nodes, "terminal_type": "stored_procedure",
            "terminal_target": f"SP-{fid}", "confidence": "confirmed", "evidence_refs": [],
        })
        ix["data_access"].extend(
            {"id": n, "class": "Repo", "method": "Save", "operation_kind": "write",
             "sql_operation": "INSERT", "confidence": "confirmed"} for n in nodes
        )
        ix["stored_procedures"].append({"id": f"SP-{fid}", "name": f"PKG.{fid}", "package": "PKG", "procedure": fid})
    return ix


def _uniform_ix(count: int) -> dict:
    """A uniform set of small-but-nontrivial flows: each fits comfortably within
    TINY's own character budget individually, so only the record COUNT differs
    between SMALL (80) and TINY (20) -- never an individually oversized record."""
    ix = {"functional_flows": [], "entry_points": [], "functional_paths": [],
          "data_access": [], "stored_procedures": [], "sql_operations": [], "data_parameters": []}
    for i in range(count):
        fid = f"FLOW-{i:04d}"
        ix["functional_flows"].append(_flow(fid))
        ix["entry_points"].append(_entry(fid))
        ix["functional_paths"].append({
            "path_id": f"PATH-{fid}", "flow_id": fid, "nodes": [f"DAO-{fid}"], "terminal_type": "unresolved_boundary",
            "terminal_target": f"DAO-{fid}", "confidence": "confirmed", "evidence_refs": [f"REF-{fid}"],
        })
        ix["data_access"].append({
            "id": f"DAO-{fid}", "class": "Repo", "method": "Get", "operation_kind": "read",
            "sql_operation": "SELECT", "confidence": "confirmed",
        })
    return ix


class T1RichOversizedFirstCandidateTests(unittest.TestCase):
    """T1 -- an oversized bucket-0 candidate must be skipped, not block everything after it."""

    def test_oversized_candidate_is_excluded_but_smaller_ones_are_selected(self) -> None:
        ix = _oversized_rich_ix()
        records = [EvidenceHydrator().hydrate_flow(fid, ix) for fid in ("FLOW-A", "FLOW-B", "FLOW-C", "FLOW-D")]
        package = aip.AiProjectionBuilder().package(records, profile="SMALL")
        selected = {r["flow_id"] for r in package["records"]}
        self.assertNotIn("FLOW-A", selected)
        self.assertIn("FLOW-B", selected)
        self.assertIn("FLOW-C", selected)
        self.assertNotEqual(package["statistics"]["completeness"], "BUDGET_INSUFFICIENT")

    def test_tiny_profile_also_skips_the_oversized_candidate_and_still_selects_others(self) -> None:
        ix = _oversized_rich_ix()
        records = [EvidenceHydrator().hydrate_flow(fid, ix) for fid in ("FLOW-A", "FLOW-B", "FLOW-C", "FLOW-D")]
        package = aip.AiProjectionBuilder().package(records, profile="TINY")
        selected = {r["flow_id"] for r in package["records"]}
        self.assertNotIn("FLOW-A", selected)
        self.assertTrue(selected, "at least one smaller candidate must still be selected")
        self.assertNotEqual(package["statistics"]["completeness"], "BUDGET_INSUFFICIENT")


class T2NoCandidateFitsTests(unittest.TestCase):
    """T2 -- when every candidate individually exceeds the budget, fail closed without calling the provider."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = cls._tmp.name
        analyze_repository(FIXTURE, cls.out, None, 12)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_all_oversized_candidates_yield_budget_insufficient_directly(self) -> None:
        ix = _all_oversized_ix()
        records = [EvidenceHydrator().hydrate_flow(f["id"], ix) for f in ix["functional_flows"]]
        for profile in ("SMALL", "TINY"):
            package = aip.AiProjectionBuilder().package(records, profile=profile)
            self.assertEqual(package["statistics"]["completeness"], "BUDGET_INSUFFICIENT")
            self.assertEqual(package["records"], [])

    def test_context_too_large_is_reported_without_a_provider_call(self) -> None:
        indexes = ai._load_indexes(self.out)
        oversized = _all_oversized_ix()
        indexes = {**indexes, **oversized}
        source_snapshot = ai._load_source_snapshot(self.out)
        package, request, metrics, rejection = ai._build_within_budget(
            indexes, source_snapshot, None, "SMALL", limit=10 ** 9,
        )
        self.assertIsNotNone(rejection)
        self.assertIn("budget_insufficient:profile=SMALL", rejection)
        self.assertIn("budget_insufficient:profile=TINY", rejection)


class T3SmallFailsTinySucceedsTests(unittest.TestCase):
    """T3 -- the existing reduce-once-then-fail-closed fallback (SMALL -> TINY) still works."""

    def test_a_tight_final_payload_limit_between_small_and_tiny_falls_back_to_tiny(self) -> None:
        ix = _uniform_ix(100)
        small_package, _, small_metrics, small_rejection = ai._build_within_budget(ix, None, None, "SMALL", 10 ** 9)
        _, _, tiny_metrics, tiny_rejection = ai._build_within_budget(ix, None, None, "TINY", 10 ** 9)
        self.assertIsNone(small_rejection)
        self.assertIsNone(tiny_rejection)
        self.assertGreater(small_metrics["payload_estimated_tokens"], tiny_metrics["payload_estimated_tokens"])

        limit = (small_metrics["payload_estimated_tokens"] + tiny_metrics["payload_estimated_tokens"]) // 2
        package, request, metrics, rejection = ai._build_within_budget(ix, None, None, "SMALL", limit)
        self.assertIsNone(rejection)
        self.assertEqual(package["selection_policy"]["budget_profile"], "TINY")
        self.assertLessEqual(metrics["payload_estimated_tokens"], limit)


class T4SmallSucceedsTests(unittest.TestCase):
    """T4 -- a mixed, budget-friendly dataset succeeds on the first (SMALL) attempt; no TINY retry."""

    def test_small_succeeds_without_falling_back_to_tiny(self) -> None:
        profiles: list[str] = []
        original = aip.AiProjectionBuilder.build

        def spy(self, flow_ids, ix, source_snapshot=None, profile="SMALL", budget=None):
            profiles.append(profile)
            return original(self, flow_ids, ix, source_snapshot=source_snapshot, profile=profile, budget=budget)

        aip.AiProjectionBuilder.build = spy
        try:
            ix = _oversized_rich_ix()
            package, request, metrics, rejection = ai._build_within_budget(ix, None, None, "SMALL", 10 ** 9)
        finally:
            aip.AiProjectionBuilder.build = original
        self.assertIsNone(rejection)
        self.assertEqual(profiles, ["SMALL"])


class T5FinalSerializedPayloadTests(unittest.TestCase):
    """T5 -- the budget decision is made on the same final serialized request measurement."""

    def test_metrics_come_from_measure_request_payload_on_the_built_request(self) -> None:
        ix = _uniform_ix(10)
        package, request, metrics, rejection = ai._build_within_budget(ix, None, None, "SMALL", 10 ** 9)
        self.assertIsNone(rejection)
        self.assertEqual(metrics, measure_request_payload(request, ai.FINDING_SCHEMA))


class T6StableOutputTests(unittest.TestCase):
    """T6 -- the same input always yields the same selected ids, order, profile and measurement."""

    def test_build_within_budget_is_stable_across_repeated_calls(self) -> None:
        ix = _oversized_rich_ix()
        first = ai._build_within_budget(ix, None, None, "SMALL", 10 ** 9)
        for _ in range(5):
            again = ai._build_within_budget(ix, None, None, "SMALL", 10 ** 9)
            self.assertEqual(again[0], first[0])
            self.assertEqual(again[2], first[2])
            self.assertEqual(again[3], first[3])


class T7DiversitySurvivesBudgetPruningTests(unittest.TestCase):
    """T7 -- budget pruning must not collapse the final selection down to only the trivial bucket."""

    def test_final_package_still_carries_richer_flows_after_pruning(self) -> None:
        ix = _oversized_rich_ix()
        package, request, metrics, rejection = ai._build_within_budget(ix, None, None, "SMALL", 10 ** 9)
        self.assertIsNone(rejection)
        selected = {r["flow_id"] for r in package["records"]}
        self.assertTrue({"FLOW-B", "FLOW-C"} & selected, "richer flows must survive budget pruning")
        self.assertNotEqual(selected, {"FLOW-D"})


class T8AtomicEvidenceTests(unittest.TestCase):
    """T8 -- an included candidate keeps its full, untruncated evidence; nothing is partially cut."""

    def test_included_records_are_byte_identical_to_a_fresh_hydration(self) -> None:
        ix = _oversized_rich_ix()
        package, request, metrics, rejection = ai._build_within_budget(ix, None, None, "SMALL", 10 ** 9)
        self.assertIsNone(rejection)
        for record in package["records"]:
            expected = EvidenceHydrator().hydrate_flow(record["flow_id"], ix)
            self.assertEqual(record, expected)


class T9NoConfidenceMutationTests(unittest.TestCase):
    """T9 -- selection/budgeting never mutates flow, path, or terminal confidence."""

    def test_flow_confidence_is_unchanged_after_budget_aware_selection(self) -> None:
        ix = _oversized_rich_ix()
        before = {f["id"]: f["confidence"] for f in ix["functional_flows"]}
        ai._build_within_budget(ix, None, None, "SMALL", 10 ** 9)
        after = {f["id"]: f["confidence"] for f in ix["functional_flows"]}
        self.assertEqual(before, after)


class T10NoLLMDependencyTests(unittest.TestCase):
    """T10 -- selection/budgeting runs and fails closed without any network, Copilot, or provider call."""

    def test_context_too_large_never_calls_the_exploding_provider(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            analyze_repository(FIXTURE, out, None, 12)
            indexes = ai._load_indexes(out)
            oversized = _all_oversized_ix()
            indexes.update(oversized)
            source_snapshot = ai._load_source_snapshot(out)
            package, request, metrics, rejection = ai._build_within_budget(
                indexes, source_snapshot, None, "SMALL", limit=10 ** 9,
            )
            self.assertIsNotNone(rejection)

    def test_run_ai_interpretation_reports_context_too_large_without_invoking_the_provider(self) -> None:
        # Directly exercises the production entry point with an exploding provider:
        # if the budget gate were ever bypassed, this would fail loudly rather
        # than silently reaching a real/simulated provider.
        with tempfile.TemporaryDirectory() as out:
            analyze_repository(FIXTURE, out, None, 12)
            original_load_indexes = ai._load_indexes
            oversized = _all_oversized_ix()

            def patched_load_indexes(output_dir):
                indexes = original_load_indexes(output_dir)
                indexes.update(oversized)
                return indexes

            ai._load_indexes = patched_load_indexes
            try:
                result = ai.run_ai_interpretation(
                    out, provider=_ExplodingProvider(
                        ProviderConfig("FAKE", "f", "m", capabilities={"structured_output": True})),
                )
            finally:
                ai._load_indexes = original_load_indexes
            self.assertEqual(result.status, "CONTEXT_TOO_LARGE")
            self.assertFalse(result.provider_called)


class T11RegressionTests(unittest.TestCase):
    """T11 -- R5/R6/R7/R8 and the proposal-quality correction's public surface are preserved."""

    def test_ai_projection_public_surface_is_preserved(self) -> None:
        for name in ("select_flow_ids", "AiProjectionBuilder", "PROFILE_REDUCTION", "ALLOWED_PROFILES"):
            self.assertTrue(hasattr(aip, name))

    def test_ai_interpretation_public_surface_is_preserved(self) -> None:
        for name in ("run_ai_interpretation", "_build_within_budget", "FINDING_SCHEMA"):
            self.assertTrue(hasattr(ai, name))


if __name__ == "__main__":
    unittest.main()
