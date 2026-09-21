"""V4.3-R5 -- AI Context Budgeting & Strict Grounding: verification tests.

Covers, one rule per test:

1. `legacy_documenter.context.ai_projection` builds an
   `AI_HYDRATED_PROJECTION 1.0` package of **hydrated** records with an
   `AIP-` package id, reusing `composer.PROFILES` and rejecting `FULL`.
2. The budget is mandatory and real: record/character ceilings truncate,
   `BUDGET_INSUFFICIENT` is reported rather than silently ignored, and no
   bulk `continuation_refs` list is ever carried.
3. The FINAL serialized request payload is measured by one shared,
   provider-neutral function that the Copilot adapter itself delegates to,
   so the measured string is the string that would be sent.
4. `run_ai_interpretation` (the only production path to a provider) now uses
   that projection, gates on the measured payload before calling, returns
   the pre-existing `CONTEXT_TOO_LARGE` status without calling the provider
   when it does not fit, and keeps `INVALID_STRUCTURED_OUTPUT` as a distinct
   post-call safe failure.
5. `SYSTEM_INSTRUCTION` explicitly forbids tools/file inspection/shell and
   demands only the requested structure (V4.3-R0 `D-04`, `EEE-05`).
6. Evidence refs validate against the hydrated records' own deterministic ids.

REAL_AI_RUNTIME_CALL_ALLOWED=false: every test here injects
`legacy_documenter.llm.core.FakeLLMProvider` (or a deliberately exploding
subclass) explicitly -- no test reaches `_resolve_provider`/`ProviderRegistry`
with a real `provider_type`.
"""
from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path

from legacy_documenter.context import ai_projection as aip
from legacy_documenter.context.composer import PROFILES, ContextComposer
from legacy_documenter.context.hydration import EvidenceHydrator
from legacy_documenter.llm.core import (
    STATUSES,
    FakeLLMProvider,
    LLMRequest,
    ProviderConfig,
    measure_request_payload,
    render_request_payload,
)
from legacy_documenter.llm.providers.copilot import CopilotProvider
from legacy_documenter.main import analyze_repository
from legacy_documenter.orchestration import ai_interpretation as ai

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "v4_2_r3_sample"

VALID_STRUCTURED_RESPONSE = {
    "findings": [
        {"statement": "The Save button reaches a stored procedure.", "confidence": "CONFIRMED",
         "evidence_refs": ["DAO-0197413858"]}
    ]
}


def _fake_provider(**kwargs) -> FakeLLMProvider:
    config = ProviderConfig("FAKE", "fake-1", "fake-model", capabilities={"structured_output": True})
    return FakeLLMProvider(config, **kwargs)


def _windowed_provider(context_window: int, **kwargs) -> FakeLLMProvider:
    config = ProviderConfig(
        "FAKE", "fake-1", "fake-model",
        capabilities={"structured_output": True, "context_window": context_window},
    )
    return FakeLLMProvider(config, **kwargs)


def _reserved_provider(context_window: int, max_output_tokens: int, **kwargs) -> FakeLLMProvider:
    config = ProviderConfig(
        "FAKE", "fake-1", "fake-model",
        capabilities={
            "structured_output": True, "context_window": context_window,
            "max_output_tokens": max_output_tokens,
        },
    )
    return FakeLLMProvider(config, **kwargs)


class _ExplodingProvider(FakeLLMProvider):
    """Fails loudly if a test path ever reaches the provider when it must not."""

    def structured_generate(self, request, schema):  # pragma: no cover - must never run
        raise AssertionError("provider must not be called")


def _synthetic_ix(flow_count: int = 1, confidence: str = "confirmed", node_padding: int = 0) -> dict:
    """A minimal `ix` indexes dict of the exact shape `EvidenceHydrator` consumes."""
    flows, entry_points, paths = [], [], []
    for index in range(flow_count):
        flow_id = f"FLOW-{index:03d}"
        entry_id = f"EP-{index:03d}"
        flows.append({"id": flow_id, "entry_point_id": entry_id, "confidence": confidence, "project_sequence": ["P"]})
        entry_points.append({
            "id": entry_id, "webform": f"web\\form{index}.ascx", "event": "Click",
            "handler": f"btn{index}_Click", "start_method": f"Start{index}",
        })
        paths.append({
            "path_id": f"PATH-{index:03d}", "flow_id": flow_id,
            "nodes": ["DAO-1"] + [f"PADDING-NODE-{n:04d}" for n in range(node_padding)],
            "terminal_type": "stored_procedure", "terminal_target": "SP-1",
            "confidence": confidence, "evidence_refs": [f"CALL-{index:03d}"],
        })
    return {
        "functional_flows": flows, "entry_points": entry_points, "functional_paths": paths,
        "data_access": [{"id": "DAO-1", "class": "Repo", "method": "Save",
                         "operation_kind": "stored_procedure", "confidence": "confirmed"}],
        "stored_procedures": [{"id": "SP-1", "name": "PKG.SAVE", "package": "PKG", "procedure": "SAVE"}],
        "sql_operations": [], "data_parameters": [],
    }


class AiProjectionContractTests(unittest.TestCase):
    """The package must match the V4.3-R1 section 5.2 contract exactly."""

    def setUp(self) -> None:
        self.ix = _synthetic_ix(3)
        self.builder = aip.AiProjectionBuilder()

    def test_package_id_uses_the_aip_prefix(self) -> None:
        package = self.builder.build(["FLOW-000"], self.ix)
        self.assertTrue(package["package_id"].startswith("AIP-"))
        self.assertEqual(len(package["package_id"]), len("AIP-") + 64)

    def test_package_declares_the_contract_name_and_version(self) -> None:
        package = self.builder.build(["FLOW-000"], self.ix)
        self.assertEqual(package["contract_name"], "AI_HYDRATED_PROJECTION")
        self.assertEqual(package["contract_version"], "1.0")

    def test_records_are_hydrated_records_not_bare_references(self) -> None:
        package = self.builder.build(["FLOW-000"], self.ix)
        record = package["records"][0]
        self.assertNotIn("ref", record)
        self.assertEqual(record["entry_point"]["handler"], "btn0_Click")
        self.assertEqual(record["terminals"]["stored_procedures"][0]["resolved_name"], "PKG.SAVE")

    def test_records_are_exactly_what_the_hydrator_produces(self) -> None:
        package = self.builder.build(["FLOW-000"], self.ix)
        self.assertEqual(package["records"][0], EvidenceHydrator().hydrate_flow("FLOW-000", self.ix))

    def test_envelope_carries_the_same_fields_as_the_existing_package_envelope(self) -> None:
        package = self.builder.build(["FLOW-000"], self.ix, source_snapshot="abc")
        for key in ("package_type", "schema_version", "package_id", "source_snapshot", "statistics", "truncation"):
            self.assertIn(key, package)
        self.assertEqual(package["source_snapshot"], "abc")

    def test_full_profile_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.builder.build(["FLOW-000"], self.ix, profile="FULL")

    def test_unknown_profile_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.builder.build(["FLOW-000"], self.ix, profile="ENORMOUS")

    def test_allowed_profiles_are_reused_from_composer_not_redefined(self) -> None:
        self.assertEqual(set(aip.ALLOWED_PROFILES), set(PROFILES) - {"FULL"})
        for name in aip.ALLOWED_PROFILES:
            self.assertIn(name, PROFILES)

    def test_flow_ids_are_mandatory(self) -> None:
        with self.assertRaises(ValueError):
            self.builder.build(None, self.ix)

    def test_package_is_deterministic_for_the_same_input(self) -> None:
        first = self.builder.build(["FLOW-000", "FLOW-001"], self.ix)
        second = self.builder.build(["FLOW-001", "FLOW-000"], self.ix)
        self.assertEqual(first, second)

    def test_package_id_changes_when_content_changes(self) -> None:
        one = self.builder.build(["FLOW-000"], self.ix)
        two = self.builder.build(["FLOW-000", "FLOW-001"], self.ix)
        self.assertNotEqual(one["package_id"], two["package_id"])

    def test_confidence_is_never_altered_or_invented(self) -> None:
        ix = _synthetic_ix(1, confidence="unresolved")
        package = self.builder.build(["FLOW-000"], ix)
        self.assertEqual(package["records"][0]["confidence"], "unresolved")
        self.assertEqual(package["statistics"]["confirmed_flow_count"], 0)
        self.assertEqual(package["statistics"]["unresolved_flow_count"], 1)

    def test_interpreted_content_is_rejected(self) -> None:
        record = EvidenceHydrator().hydrate_flow("FLOW-000", self.ix)
        record["interpretations"] = [{"statement": "invented"}]
        with self.assertRaises(aip.InterpretedContentError):
            self.builder.package([record])

    def test_ai_interpretation_confidence_value_is_rejected(self) -> None:
        record = EvidenceHydrator().hydrate_flow("FLOW-000", self.ix)
        record["source_type"] = "AI_INTERPRETATION"
        with self.assertRaises(aip.InterpretedContentError):
            self.builder.package([record])


class BudgetTests(unittest.TestCase):
    """The budget must be real: it truncates, reports, and fails closed."""

    def setUp(self) -> None:
        self.builder = aip.AiProjectionBuilder()

    def test_max_records_truncates_and_reports_counts(self) -> None:
        ix = _synthetic_ix(5)
        package = self.builder.build([f"FLOW-{i:03d}" for i in range(5)], ix, budget={"max_records": 2})
        self.assertEqual(len(package["records"]), 2)
        self.assertEqual(package["statistics"]["records_excluded"], 3)
        self.assertEqual(package["statistics"]["completeness"], "TRUNCATED")

    def test_character_budget_truncates_records(self) -> None:
        ix = _synthetic_ix(5)
        full = self.builder.build([f"FLOW-{i:03d}" for i in range(5)], ix)
        half = self.builder.build(
            [f"FLOW-{i:03d}" for i in range(5)], ix,
            budget={"max_characters": full["statistics"]["character_count"] // 2},
        )
        self.assertLess(len(half["records"]), len(full["records"]))
        self.assertTrue(half["truncation"]["truncated"])

    def test_estimated_token_budget_also_constrains_characters(self) -> None:
        ix = _synthetic_ix(5)
        package = self.builder.build([f"FLOW-{i:03d}" for i in range(5)], ix, budget={"max_estimated_tokens": 200})
        self.assertLessEqual(package["statistics"]["max_characters"], 200 * 4)

    def test_budget_insufficient_when_even_one_record_does_not_fit(self) -> None:
        ix = _synthetic_ix(1)
        package = self.builder.build(["FLOW-000"], ix, budget={"max_characters": 10})
        self.assertEqual(package["statistics"]["completeness"], "BUDGET_INSUFFICIENT")
        self.assertEqual(package["records"], [])
        self.assertTrue(package["truncation"]["truncated"])

    def test_statistics_character_count_matches_the_serialized_body(self) -> None:
        package = self.builder.build(["FLOW-000"], _synthetic_ix(1))
        body = {k: v for k, v in package.items() if k not in ("statistics", "truncation", "package_id")}
        self.assertEqual(package["statistics"]["character_count"],
                         len(json.dumps(body, sort_keys=True, separators=(",", ":"))))

    def test_truncation_never_carries_a_continuation_refs_list(self) -> None:
        ix = _synthetic_ix(5)
        package = self.builder.build([f"FLOW-{i:03d}" for i in range(5)], ix, budget={"max_records": 1})
        self.assertNotIn("continuation_refs", package["truncation"])
        self.assertFalse(package["truncation"]["continuation_refs_included"])
        self.assertEqual(package["truncation"]["excluded_record_count"], 4)

    def test_existing_composer_still_carries_continuation_refs_unchanged(self) -> None:
        # The omission above is a property of this new surface only; the
        # pre-existing reference-package contract is not weakened by R5.
        source = Path(ContextComposer.__module__.replace(".", "/") + ".py")
        self.assertIn("continuation_refs", (ROOT / source).read_text(encoding="utf-8"))

    def test_confirmed_records_survive_a_tight_budget_before_unresolved_ones(self) -> None:
        ix = _synthetic_ix(2, confidence="unresolved")
        ix["functional_flows"][1]["confidence"] = "confirmed"
        package = self.builder.build(["FLOW-000", "FLOW-001"], ix, budget={"max_records": 1})
        self.assertEqual(package["records"][0]["flow_id"], "FLOW-001")


class SelectFlowIdsTests(unittest.TestCase):
    """Flow selection must be bounded, deterministic, and evidence-prioritized."""

    def test_selection_is_bounded(self) -> None:
        self.assertEqual(len(aip.select_flow_ids(_synthetic_ix(10), 3)), 3)

    def test_selection_is_deterministic(self) -> None:
        ix = _synthetic_ix(10)
        self.assertEqual(aip.select_flow_ids(ix, 4), aip.select_flow_ids(ix, 4))

    def test_non_positive_limit_is_rejected(self) -> None:
        for limit in (0, -1, None):
            with self.assertRaises(ValueError):
                aip.select_flow_ids(_synthetic_ix(3), limit)

    def test_confirmed_flows_are_selected_before_unresolved_ones(self) -> None:
        ix = _synthetic_ix(3, confidence="unresolved")
        ix["functional_flows"][2]["confidence"] = "confirmed"
        self.assertEqual(aip.select_flow_ids(ix, 1), ["FLOW-002"])


class PayloadMeasurementTests(unittest.TestCase):
    """The measured payload must be the payload a provider actually sends."""

    def _request(self, context: dict | None = None) -> LLMRequest:
        return LLMRequest(
            purpose="TEST", system_instruction="SYS", user_instruction="USER",
            context=context if context is not None else {"records": []},
            context_package_id="AIP-x", context_schema_version="1.0", source_snapshot="snap",
        )

    def test_copilot_prompt_delegates_to_the_shared_renderer(self) -> None:
        provider = CopilotProvider(ProviderConfig("COPILOT", "c", "m"))
        request = self._request()
        self.assertEqual(provider._prompt(request, {"required": ["findings"]}),
                         render_request_payload(request, {"required": ["findings"]}))

    def test_copilot_module_no_longer_holds_its_own_copy_of_the_wrapper(self) -> None:
        source = Path(CopilotProvider.__module__.replace(".", "/") + ".py")
        text = (ROOT / source).read_text(encoding="utf-8")
        self.assertNotIn("<system_instruction>", text)
        self.assertIn("render_request_payload", text)

    def test_measurement_counts_instructions_envelope_and_schema(self) -> None:
        request = self._request()
        without = measure_request_payload(request, None)
        with_schema = measure_request_payload(request, {"required": ["findings"]})
        self.assertGreater(with_schema["payload_characters"], without["payload_characters"])
        self.assertIn("SYS", render_request_payload(request, None))
        self.assertIn("USER", render_request_payload(request, None))

    def test_measured_payload_exceeds_the_packages_own_estimate(self) -> None:
        # The exact V4.3-R0 D-01 defect: a package within its own budget still
        # produces a strictly larger real payload once wrapped.
        ix = _synthetic_ix(3)
        package = aip.AiProjectionBuilder().build([f"FLOW-{i:03d}" for i in range(3)], ix)
        metrics = measure_request_payload(ai._build_request(package), ai.FINDING_SCHEMA)
        self.assertGreater(metrics["payload_estimated_tokens"], package["statistics"]["estimated_tokens"])

    def test_measurement_is_deterministic(self) -> None:
        request = self._request()
        self.assertEqual(measure_request_payload(request, ai.FINDING_SCHEMA),
                         measure_request_payload(request, ai.FINDING_SCHEMA))

    def test_measurement_never_sends_anything(self) -> None:
        provider = _ExplodingProvider(ProviderConfig("FAKE", "f", "m", capabilities={"structured_output": True}))
        measure_request_payload(self._request(), ai.FINDING_SCHEMA)  # no provider involved at all
        self.assertIsNotNone(provider)


class ProductionPathProjectionTests(unittest.TestCase):
    """`run_ai_interpretation` must build and send an `ai_projection` package."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = cls._tmp.name
        analyze_repository(FIXTURE, cls.out, None, 12)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_interpretation_uses_an_ai_projection_package(self) -> None:
        result = ai.run_ai_interpretation(self.out, provider=_fake_provider(structured_response=VALID_STRUCTURED_RESPONSE))
        self.assertEqual(result.status, "SUCCESS")
        self.assertTrue(result.context_package_id.startswith("AIP-"))

    def test_sent_request_context_is_the_hydrated_projection(self) -> None:
        captured: list[LLMRequest] = []

        class Capturing(FakeLLMProvider):
            def structured_generate(self, request, schema):
                captured.append(request)
                return super().structured_generate(request, schema)

        provider = Capturing(ProviderConfig("FAKE", "f", "m", capabilities={"structured_output": True}),
                             structured_response=VALID_STRUCTURED_RESPONSE)
        ai.run_ai_interpretation(self.out, provider=provider)
        context = captured[0].context
        self.assertEqual(context["contract_name"], "AI_HYDRATED_PROJECTION")
        self.assertIn("entry_point", context["records"][0])

    def test_request_carries_no_bulk_metadata(self) -> None:
        package = aip.AiProjectionBuilder().build(
            aip.select_flow_ids(ai._load_indexes(self.out), 80), ai._load_indexes(self.out),
        )
        request = ai._build_request(package)
        self.assertEqual(request.metadata, {})
        # The bulk list itself is absent; only the declarative
        # `continuation_refs_included: false` marker and the counts remain.
        self.assertNotIn('"continuation_refs":', render_request_payload(request, ai.FINDING_SCHEMA))

    def test_flow_ids_parameter_scopes_the_projection(self) -> None:
        indexes = ai._load_indexes(self.out)
        flow_id = indexes["functional_flows"][0]["id"]
        result = ai.run_ai_interpretation(
            self.out, provider=_fake_provider(structured_response=VALID_STRUCTURED_RESPONSE), flow_ids=[flow_id],
        )
        self.assertEqual(result.status, "SUCCESS")

    def test_evidence_refs_validate_against_hydrated_record_ids(self) -> None:
        result = ai.run_ai_interpretation(self.out, provider=_fake_provider(structured_response=VALID_STRUCTURED_RESPONSE))
        self.assertEqual(result.findings[0]["evidence_refs"], ["DAO-0197413858"])

    def test_unknown_evidence_ref_is_still_rejected(self) -> None:
        provider = _fake_provider(structured_response={
            "findings": [{"statement": "x", "confidence": "CONFIRMED", "evidence_refs": ["NOPE-1"]}]
        })
        result = ai.run_ai_interpretation(self.out, provider=provider)
        self.assertEqual(result.status, "INVALID_OUTPUT")
        self.assertIn("unknown_evidence_refs", result.error_message)

    def test_missing_index_directory_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as empty:
            result = ai.run_ai_interpretation(empty, provider=_ExplodingProvider(
                ProviderConfig("FAKE", "f", "m", capabilities={"structured_output": True})))
        self.assertEqual(result.status, "CONTEXT_UNAVAILABLE")
        self.assertFalse(result.provider_called)

    def test_invalid_structured_output_remains_a_distinct_post_call_failure(self) -> None:
        provider = _fake_provider(structured_response={"oops": []})
        result = ai.run_ai_interpretation(self.out, provider=provider)
        self.assertEqual(result.status, "INVALID_OUTPUT")
        self.assertTrue(result.provider_called)


class PayloadGateTests(unittest.TestCase):
    """The gate must fire before the provider, never after."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = cls._tmp.name
        analyze_repository(FIXTURE, cls.out, None, 12)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def _exploding(self, context_window: int | None = None) -> FakeLLMProvider:
        capabilities = {"structured_output": True}
        if context_window is not None:
            capabilities["context_window"] = context_window
        return _ExplodingProvider(ProviderConfig("FAKE", "f", "m", capabilities=capabilities))

    def test_oversized_payload_returns_context_too_large_without_calling_the_provider(self) -> None:
        result = ai.run_ai_interpretation(self.out, provider=self._exploding(context_window=10))
        self.assertEqual(result.status, "CONTEXT_TOO_LARGE")
        self.assertFalse(result.provider_called)

    def test_context_too_large_is_an_already_existing_status(self) -> None:
        self.assertIn("CONTEXT_TOO_LARGE", STATUSES)

    def test_budget_insufficient_never_continues_to_the_provider(self) -> None:
        result = ai.run_ai_interpretation(self.out, provider=self._exploding(), profile="TINY")
        self.assertEqual(result.status, "CONTEXT_TOO_LARGE")
        self.assertIn("budget_insufficient", result.error_message)
        self.assertFalse(result.provider_called)

    def test_gate_reports_the_measured_payload_size_it_rejected(self) -> None:
        result = ai.run_ai_interpretation(self.out, provider=self._exploding(context_window=10))
        self.assertIn("payload_estimated_tokens", result.error_message)
        self.assertIn("limit=10", result.error_message)

    def test_provider_context_window_is_preferred_over_the_default_limit(self) -> None:
        self.assertEqual(ai._payload_token_limit(_windowed_provider(4321)), 4321)

    def test_default_limit_applies_when_the_provider_declares_no_window(self) -> None:
        self.assertEqual(ai._payload_token_limit(_fake_provider()), ai.DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS)

    def test_default_limit_is_bounded_and_above_the_empirically_useful_size(self) -> None:
        # EEE-04: ~5.6k tokens was enough for a useful interpretation; EEE-02:
        # ~3.6M tokens was the failure mode this ceiling exists to prevent.
        self.assertGreater(ai.DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS, 5600)
        self.assertLess(ai.DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS, 3_600_000)

    def test_reduce_then_retry_is_attempted_exactly_once(self) -> None:
        profiles: list[str] = []
        original = aip.AiProjectionBuilder.build

        def spy(self, flow_ids, ix, source_snapshot=None, profile="SMALL", budget=None):
            profiles.append(profile)
            return original(self, flow_ids, ix, source_snapshot=source_snapshot, profile=profile, budget=budget)

        aip.AiProjectionBuilder.build = spy
        try:
            ai.run_ai_interpretation(self.out, provider=self._exploding(context_window=10))
        finally:
            aip.AiProjectionBuilder.build = original
        self.assertEqual(profiles, ["SMALL", "TINY"])


class OutputReservationGateTests(unittest.TestCase):
    """V4.3-R5 correction: `context_window` must be shared with declared output,
    never handed to the input payload whole."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = cls._tmp.name
        analyze_repository(FIXTURE, cls.out, None, 12)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_effective_limit_reserves_the_declared_max_output_tokens(self) -> None:
        # context_window=16000, max_output_tokens=2000 -> the input payload's
        # own ceiling is the remainder, 14000, never the full 16000.
        provider = _reserved_provider(16000, 2000)
        self.assertEqual(ai._payload_token_limit(provider), 14000)

    def test_a_smaller_request_max_output_tokens_narrows_the_reservation_further(self) -> None:
        provider = _reserved_provider(16000, 2000)
        self.assertEqual(ai._payload_token_limit(provider, request_max_output_tokens=500), 15500)
        # A request declaring MORE than the provider's own ceiling never
        # widens the reservation past what the provider actually declared.
        self.assertEqual(ai._payload_token_limit(provider, request_max_output_tokens=9000), 14000)

    def test_payload_fitting_under_the_window_but_not_under_the_reserved_limit_is_rejected(self) -> None:
        # Fits under the raw context_window (16000) but not under the
        # effective, reserved limit (16000 - 2000 = 14000): must still be
        # CONTEXT_TOO_LARGE, and the provider must never be called.
        original = ai.measure_request_payload
        ai.measure_request_payload = lambda request, schema=None: {
            **original(request, schema), "payload_estimated_tokens": 15000,
        }
        try:
            result = ai.run_ai_interpretation(self.out, provider=self._exploding_reserved(16000, 2000))
        finally:
            ai.measure_request_payload = original
        self.assertEqual(result.status, "CONTEXT_TOO_LARGE")
        self.assertFalse(result.provider_called)
        self.assertIn("limit=14000", result.error_message)

    def test_payload_fitting_under_the_reserved_limit_is_accepted(self) -> None:
        original = ai.measure_request_payload
        ai.measure_request_payload = lambda request, schema=None: {
            **original(request, schema), "payload_estimated_tokens": 13000,
        }
        try:
            result = ai.run_ai_interpretation(
                self.out, provider=_reserved_provider(16000, 2000, structured_response=VALID_STRUCTURED_RESPONSE),
            )
        finally:
            ai.measure_request_payload = original
        self.assertEqual(result.status, "SUCCESS")

    def test_reservation_consuming_the_whole_window_fails_closed_without_calling_the_provider(self) -> None:
        result = ai.run_ai_interpretation(self.out, provider=self._exploding_reserved(2000, 2000))
        self.assertEqual(result.status, "CONTEXT_TOO_LARGE")
        self.assertFalse(result.provider_called)

    def test_reservation_larger_than_the_window_also_fails_closed(self) -> None:
        result = ai.run_ai_interpretation(self.out, provider=self._exploding_reserved(2000, 5000))
        self.assertEqual(result.status, "CONTEXT_TOO_LARGE")
        self.assertFalse(result.provider_called)
        self.assertEqual(ai._payload_token_limit(_reserved_provider(2000, 5000)), -3000)

    def test_provider_without_context_window_keeps_the_default_input_payload_ceiling(self) -> None:
        # No context_window declared at all -> LegacyMapper's own
        # DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS (16000) still applies, unwidened
        # by any max_output_tokens the provider might separately declare.
        config = ProviderConfig("FAKE", "f", "m", capabilities={"structured_output": True, "max_output_tokens": 2000})
        provider = FakeLLMProvider(config)
        self.assertEqual(ai._payload_token_limit(provider), ai.DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS)
        self.assertEqual(ai.DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS, 16000)

    def test_gate_still_measures_the_real_final_serialized_payload(self) -> None:
        # The reservation changes the threshold compared against, never what
        # is measured: it is still the actual rendered request string.
        result = ai.run_ai_interpretation(
            self.out, provider=_reserved_provider(16000, 2000, structured_response=VALID_STRUCTURED_RESPONSE),
        )
        self.assertEqual(result.status, "SUCCESS")

    def _exploding_reserved(self, context_window: int, max_output_tokens: int) -> FakeLLMProvider:
        capabilities = {
            "structured_output": True, "context_window": context_window,
            "max_output_tokens": max_output_tokens,
        }
        return _ExplodingProvider(ProviderConfig("FAKE", "f", "m", capabilities=capabilities))


class StrictGroundingInstructionTests(unittest.TestCase):
    """D-04/EEE-05: the system instruction itself must forbid tools."""

    def test_system_instruction_forbids_tool_use(self) -> None:
        self.assertIn("Tool use is prohibited", ai.SYSTEM_INSTRUCTION)

    def test_system_instruction_forbids_file_inspection(self) -> None:
        for token in ("inspect", "open", "read", "file"):
            self.assertIn(token, ai.SYSTEM_INSTRUCTION.lower())

    def test_system_instruction_forbids_shell_execution(self) -> None:
        self.assertIn("Do not execute shell commands or code", ai.SYSTEM_INSTRUCTION)

    def test_system_instruction_requires_only_the_requested_structure(self) -> None:
        self.assertIn("Return only the requested structure", ai.SYSTEM_INSTRUCTION)
        self.assertIn("chain-of-thought", ai.SYSTEM_INSTRUCTION)

    def test_prohibition_travels_in_the_payload_independently_of_the_provider(self) -> None:
        package = aip.AiProjectionBuilder().build(["FLOW-000"], _synthetic_ix(1))
        payload = render_request_payload(ai._build_request(package), ai.FINDING_SCHEMA)
        self.assertIn("Tool use is prohibited", payload.split("</system_instruction>")[0])

    def test_evidence_grounding_rules_are_preserved(self) -> None:
        self.assertIn("Never invent", ai.SYSTEM_INSTRUCTION)
        self.assertIn("Cite only", ai.SYSTEM_INSTRUCTION)


class RuntimeIndependenceTests(unittest.TestCase):
    """`ai_projection` stays a pure, provider-free layer, like `hydration`."""

    def test_ai_projection_never_imports_the_llm_package(self) -> None:
        # Checked on the parsed import statements, not on raw text, so the
        # module docstring may still explain how the gate in `llm.core`
        # complements this module without that counting as a dependency.
        tree = ast.parse(Path(aip.__file__).read_text(encoding="utf-8"))
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported += [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        self.assertFalse([name for name in imported if "llm" in name], imported)

    def test_ai_projection_never_reads_or_writes_a_file(self) -> None:
        source = Path(aip.__file__).read_text(encoding="utf-8")
        for token in ("open(", "Path(", "write_text", "read_text"):
            self.assertNotIn(token, source)

    def test_ai_projection_does_not_reimplement_hydration(self) -> None:
        source = Path(aip.__file__).read_text(encoding="utf-8")
        self.assertIn("from .hydration import", source)
        self.assertNotIn("def hydrate_flow", source)

    def test_no_real_provider_class_is_reachable_from_these_tests(self) -> None:
        source = Path(ai.__file__).read_text(encoding="utf-8")
        self.assertNotIn("CopilotProvider", source)
        self.assertNotIn("GeminiProvider", source)


if __name__ == "__main__":
    unittest.main()
