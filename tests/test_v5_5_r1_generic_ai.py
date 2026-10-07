"""V5.5 generic provider/context contract. All clients and responses are offline."""
from __future__ import annotations

import ast
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.context.ai_projection import AiProjectionBuilder, package_reference_ids, select_flow_ids
from legacy_documenter.context.request_budget import payload_token_limit
from legacy_documenter.fingerprints import analyzer_code_fingerprint
from legacy_documenter.fingerprints.code import ANALYZER_CODE_DIRECTORIES, ANALYZER_CODE_FILES, PIPELINE_STAGES_FILE
from legacy_documenter.llm import AIProvider, AIRequest, AIResponse, FakeAIProvider, LLMProvider, LLMRequest, LLMResponse, ProviderCapabilities, ProviderConfig, ProviderError
from legacy_documenter.llm.identity import provider_identity
from legacy_documenter.llm.payload import measure_request_payload, render_request_payload
from legacy_documenter.llm.registry import ProviderRegistry, config_from_environment, resolve_provider
from legacy_documenter.llm.security import error_category, sanitize_diagnostic
from legacy_documenter.llm.contracts import LLMModelInfo, sid
from legacy_documenter.orchestration import ai_interpretation as ai

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests/fixtures/v4_2_r3_sample"


def indexes():
    return {
        "functional_flows": [{"id": "FLOW-1", "entry_point_id": "EP-1", "confidence": "unresolved", "project_sequence": ["P"]}],
        "entry_points": [{"id": "EP-1", "project": "P", "webform": "Form", "event": "Click", "handler": "Handle", "start_method": "Start"}],
        "functional_paths": [{"path_id": "PATH-1", "flow_id": "FLOW-1", "nodes": ["M-1"], "terminal_type": "unresolved", "terminal_target": "UNKNOWN-1", "confidence": "unresolved", "evidence_refs": []}],
        "data_access": [], "stored_procedures": [], "sql_operations": [], "data_parameters": [],
    }


def request(**kwargs):
    return AIRequest("TEST", "system", "task", {}, "CTX", "1.0", "SNAP", **kwargs)


def fake(**kwargs):
    config = kwargs.pop("config", ProviderConfig("FAKE", "fake-v55", "offline", context_window=16000, max_output_tokens=2000, capabilities={"structured_output": True}))
    return FakeAIProvider(config, **kwargs)


def interpret(provider, ix=None, **kwargs):
    with patch.object(ai, "_load_indexes", return_value=ix or indexes()), patch.object(ai, "_load_source_snapshot", return_value="SNAP"):
        return ai.run_ai_interpretation("unused", provider=provider, **kwargs)


VALID = {"findings": [{"statement": "The recorded boundary remains unresolved.", "confidence": "UNCERTAIN", "evidence_refs": ["PATH-1"]}]}


class GenerateOnly(AIProvider):
    """A second implementation proves the contract without a vendor-specific method."""
    def __init__(self):
        self.requests = []
        self.closed = False

    def capabilities(self):
        return ProviderCapabilities(context_window=16000, max_output_tokens=2000, structured_output=True, provider_id="synthetic", model_id="synthetic-model")

    def model_info(self):
        return LLMModelInfo("synthetic", "synthetic-model", "Synthetic", "SYNTHETIC", self.capabilities())

    def generate(self, req):
        self.requests.append(deepcopy(req))
        return AIResponse(req.request_id, sid("RESP", req.request_id), "synthetic", "synthetic-model", "SUCCESS", json.dumps(VALID))

    def close(self):
        self.closed = True


class ContractTests(unittest.TestCase):
    def test_legacy_type_identity(self):
        self.assertIs(AIProvider, LLMProvider)
        self.assertIs(AIRequest, LLMRequest)
        self.assertIs(AIResponse, LLMResponse)
        from legacy_documenter.llm.core import FakeLLMProvider
        self.assertIs(FakeAIProvider, FakeLLMProvider)

    def test_capabilities_declare_identity_limits_and_version(self):
        caps = fake().capabilities()
        self.assertEqual((caps.provider_id, caps.model_id, caps.context_window, caps.structured_output, caps.provider_version), ("fake-v55", "offline", 16000, True, "1.0"))
        self.assertEqual(fake().context_window, 16000)
        self.assertTrue(fake().structured_output)

    def test_legacy_request_id_unchanged_for_optional_defaults(self):
        req = request()
        old = {k: v for k, v in asdict(req).items() if k not in {"request_id", "output_contract", "model_id", "timeout_s"}}
        self.assertEqual(req.request_id, sid("REQ", old))

    def test_request_schema_model_timeout_affect_identity(self):
        self.assertNotEqual(request().request_id, request(output_contract={"required": ["x"]}).request_id)
        self.assertNotEqual(request().request_id, request(model_id="other").request_id)
        self.assertNotEqual(request().request_id, request(timeout_s=10).request_id)

    def test_embedded_contract_is_measured_and_rendered(self):
        req = request(output_contract={"required": ["x"]})
        self.assertEqual(render_request_payload(req), render_request_payload(req, req.output_contract))
        self.assertTrue(measure_request_payload(req)["schema_included"])

    def test_generate_only_provider_structured_fallback(self):
        provider = GenerateOnly()
        result = interpret(provider)
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(provider.requests[0].output_contract, ai.FINDING_SCHEMA)
        self.assertTrue(provider.closed)

    def test_generate_only_unsupported_never_invokes(self):
        class Plain(GenerateOnly):
            def capabilities(self):
                return ProviderCapabilities(structured_output=False)
        provider = Plain()
        response = provider.structured_generate(request(), {})
        self.assertEqual(response.status, "UNSUPPORTED_CAPABILITY")
        self.assertEqual(provider.requests, [])

    def test_generic_local_parser_rejects_invalid_json(self):
        provider = GenerateOnly()
        with patch.object(provider, "generate", return_value=AIResponse("R", "S", "p", "m", "SUCCESS", "bad json")):
            self.assertEqual(provider.structured_generate(request(), {}).status, "INVALID_STRUCTURED_OUTPUT")

    def test_config_timeout_legacy_and_explicit(self):
        config = ProviderConfig("FAKE", "p", "m", options={"timeout": 9})
        self.assertEqual(config.timeout, 9)
        config.timeout_s = 3
        self.assertEqual(config.timeout, 3)

    def test_invalid_timeout_config_is_explicit(self):
        for value in (0, -1, float("nan"), float("inf"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                ProviderConfig("FAKE", "p", "m", timeout_s=value)

    def test_context_manager_closes_idempotently(self):
        provider = fake()
        with provider:
            pass
        provider.close()
        self.assertTrue(provider.closed)


class RegistryTests(unittest.TestCase):
    def test_fake_is_explicit(self):
        self.assertIsInstance(resolve_provider(enabled=True, config=ProviderConfig("FAKE", "f", "m")), FakeAIProvider)

    def test_unknown_never_falls_back(self):
        with self.assertRaisesRegex(ValueError, "unknown provider"):
            resolve_provider(enabled=True, config=ProviderConfig("UNKNOWN", "p", "m"))

    def test_disabled_never_reads_environment_or_constructs(self):
        with patch("legacy_documenter.llm.registry.config_from_environment", side_effect=AssertionError), patch.object(ProviderRegistry, "create", side_effect=AssertionError):
            self.assertIsNone(resolve_provider(enabled=False))

    def test_custom_factory_without_vendor(self):
        registry = ProviderRegistry()
        registry.register("SYNTHETIC", lambda config: GenerateOnly())
        self.assertEqual(interpret(registry.create(ProviderConfig("SYNTHETIC", "p", "m"))).status, "SUCCESS")

    def test_duplicate_factory_fails(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            ProviderRegistry().register("FAKE", lambda config: None)

    def test_registry_registration_is_instance_scoped(self):
        first = ProviderRegistry()
        first.register("CUSTOM", lambda config: GenerateOnly())
        with self.assertRaises(ValueError):
            ProviderRegistry().create(ProviderConfig("CUSTOM", "p", "m"))

    def test_environment_defaults_preserved(self):
        config = config_from_environment({})
        self.assertEqual((config.provider_type, config.provider_id, config.model_id, config.context_window, config.max_output_tokens, config.timeout), ("COPILOT", "copilot-local", "", None, 2000, 120))

    def test_environment_explicit_model_budget_and_timeout(self):
        config = config_from_environment({"LEGACYMAPPER_LLM_PROVIDER": "FAKE", "LEGACYMAPPER_LLM_MODEL": "model", "LEGACYMAPPER_LLM_CONTEXT_WINDOW": "100", "LEGACYMAPPER_LLM_MAX_OUTPUT_TOKENS": "10", "LEGACYMAPPER_LLM_TIMEOUT": "5"})
        self.assertEqual((config.provider_type, config.model_id, config.context_window, config.max_output_tokens, config.timeout), ("FAKE", "model", 100, 10, 5))

    def test_invalid_env_does_not_echo_value(self):
        with self.assertRaises(ValueError) as caught:
            config_from_environment({"LEGACYMAPPER_LLM_TIMEOUT": "token=SECRET"})
        self.assertNotIn("SECRET", str(caught.exception))

    def test_gemini_remains_unregistered(self):
        with self.assertRaises(ValueError):
            ProviderRegistry().create(ProviderConfig("GEMINI", "g", "m"))

    def test_actual_provider_lazy_construction_has_no_sdk_calls(self):
        from legacy_documenter.llm.providers.copilot import CopilotProvider
        factory = lambda: self.fail("client must not be constructed")
        provider = ProviderRegistry().create(ProviderConfig("COPILOT", "c", "m"), client_factory=factory)
        self.assertIsInstance(provider, CopilotProvider)
        self.assertEqual(provider.capabilities().provider_id, "c")
        provider.close()


class FakeAndBudgetTests(unittest.TestCase):
    def test_plain_fake_deterministic(self):
        provider = fake(fixed_response="hello")
        self.assertEqual(provider.generate(request()), provider.generate(request()))

    def test_fake_structured_generate_and_neutral_generate(self):
        provider = fake(structured_response={"x": 1})
        self.assertEqual(provider.generate(request(output_contract={"required": ["x"]})).parsed_output, {"x": 1})
        self.assertEqual(provider.structured_generate(request(), {"required": ["x"]}).parsed_output, {"x": 1})

    def test_fake_records_copies(self):
        provider = fake()
        req = request()
        provider.generate(req)
        req.context["mutated"] = True
        self.assertNotIn("mutated", provider.requests[0].context)

    def test_fake_response_cannot_mutate_next_result(self):
        provider = fake(structured_response={"x": []})
        response = provider.structured_generate(request(), {})
        response.parsed_output["x"].append(1)
        self.assertEqual(provider.structured_generate(request(), {}).parsed_output, {"x": []})

    def test_forced_timeout_is_normalized(self):
        result = interpret(fake(forced_status="TIMEOUT"))
        self.assertEqual((result.status, result.error_message, result.provider_called), ("PROVIDER_ERROR", "TIMEOUT", True))

    def test_injected_error(self):
        result = interpret(fake(error=ProviderError("AUTHENTICATION_ERROR", "token=SECRET", "f", "m")))
        self.assertEqual(result.error_message, "AUTHENTICATION_ERROR")
        self.assertNotIn("SECRET", json.dumps(result.metrics))

    def test_rate_limit_and_cancellation_have_no_retry_loop(self):
        for code in ("RATE_LIMITED", "CANCELLED"):
            with self.subTest(code=code):
                provider = fake(error=ProviderError(code, "safe", "f", "m", retryable=True, details={"retry_after": 1}))
                result = interpret(provider)
                self.assertEqual(result.error_message, code)
                self.assertEqual(len(provider.requests), 1)

    def test_small_context_fails_before_invocation_and_closes(self):
        provider = fake(config=ProviderConfig("FAKE", "f", "m", context_window=10, capabilities={"structured_output": True}))
        result = interpret(provider)
        self.assertEqual(result.status, "CONTEXT_TOO_LARGE")
        self.assertFalse(result.provider_called)
        self.assertEqual(provider.requests, [])
        self.assertTrue(provider.closed)
        self.assertEqual(len(result.metrics["budget_attempts"]), 2)

    def test_output_reservation_exhausts_window(self):
        provider = fake(config=ProviderConfig("FAKE", "f", "m", context_window=10, max_output_tokens=10, capabilities={"structured_output": True}))
        self.assertEqual(payload_token_limit(provider), 0)
        self.assertFalse(interpret(provider).provider_called)

    def test_budget_unknown_window_uses_approved_ceiling(self):
        self.assertEqual(payload_token_limit(fake(config=ProviderConfig("FAKE", "f", "m"))), 16000)

    def test_capability_mismatch_before_call(self):
        provider = fake(config=ProviderConfig("FAKE", "f", "m"))
        result = interpret(provider)
        self.assertEqual(result.error_message, "UNSUPPORTED_CAPABILITY")
        self.assertEqual(provider.requests, [])

    def test_success_metrics_have_budget_counts_without_prompt(self):
        result = interpret(fake(structured_response=VALID))
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(result.metrics["request_count"], 1)
        self.assertEqual(result.metrics["success_count"], 1)
        self.assertLessEqual(result.metrics["payload_estimated_tokens"], result.metrics["input_token_limit"])
        for forbidden in ("system_instruction", "user_instruction", "records", "context"):
            self.assertNotIn(forbidden, result.metrics)

    def test_selection_is_deterministic_and_evidence_unchanged(self):
        ix = indexes()
        before = deepcopy(ix)
        self.assertEqual(select_flow_ids(ix, 1), select_flow_ids(ix, 1))
        one = AiProjectionBuilder().build(["FLOW-1"], ix)
        two = AiProjectionBuilder().build(["FLOW-1"], ix)
        self.assertEqual(one, two)
        self.assertEqual(ix, before)

    def test_omissions_are_explicit(self):
        package = AiProjectionBuilder().build(["FLOW-1"], indexes(), budget={"max_characters": 1})
        self.assertEqual(package["statistics"]["completeness"], "BUDGET_INSUFFICIENT")
        self.assertEqual(package["truncation"]["excluded_record_count"], 1)
        self.assertEqual(package_reference_ids(package), set())


class GroundingAndSecurityTests(unittest.TestCase):
    def test_unknown_refs_rejected_without_echoing_provider_text(self):
        output = deepcopy(VALID)
        output["findings"][0]["evidence_refs"] = ["token=SECRET"]
        result = interpret(fake(structured_response=output))
        self.assertEqual(result.status, "INVALID_OUTPUT")
        self.assertNotIn("SECRET", result.error_message)

    def test_malformed_reference_type_is_invalid_output(self):
        output = deepcopy(VALID)
        output["findings"][0]["evidence_refs"] = [{}]
        result = interpret(fake(structured_response=output))
        self.assertEqual((result.status, result.provider_called), ("INVALID_OUTPUT", True))

    def test_provider_cannot_change_evidence(self):
        class Mutating(FakeAIProvider):
            def structured_generate(self, req, schema):
                req.context["records"][0]["confidence"] = "confirmed"
                return super().structured_generate(req, schema)
        ix = indexes()
        original = deepcopy(ix)
        provider = Mutating(fake().config, structured_response=VALID)
        self.assertEqual(interpret(provider, ix).status, "SUCCESS")
        self.assertEqual(ix, original)
        self.assertEqual(ix["functional_flows"][0]["confidence"], "unresolved")

    def test_wrong_request_response_cannot_be_reused(self):
        class Wrong(FakeAIProvider):
            def structured_generate(self, req, schema):
                response = super().structured_generate(req, schema)
                response.request_id = "OTHER"
                return response
        result = interpret(Wrong(fake().config, structured_response=VALID))
        self.assertEqual(result.status, "INVALID_OUTPUT")

    def test_exception_diagnostics_never_echo_request_or_secret(self):
        class Leaking(FakeAIProvider):
            def structured_generate(self, req, schema):
                raise RuntimeError("raw prompt token=SECRET Authorization: Bearer SECRET2")
        provider = Leaking(fake().config)
        result = interpret(provider)
        self.assertEqual(result.error_message, "PROVIDER_ERROR")
        self.assertNotIn("SECRET", json.dumps(asdict(result)))
        self.assertTrue(provider.closed)

    def test_shared_sanitizer_redacts_vendor_and_central_patterns(self):
        text = sanitize_diagnostic("password=SECRET; GH_TOKEN=SECRET2; api_key: SECRET3; Authorization: Bearer SECRET4")
        self.assertNotIn("SECRET", text)

    def test_error_taxonomy(self):
        self.assertEqual(error_category(TimeoutError("SECRET")), "TIMEOUT")
        self.assertEqual(error_category(ConnectionError("SECRET")), "PROVIDER_UNAVAILABLE")
        self.assertEqual(error_category(ValueError("SECRET")), "PROVIDER_ERROR")

    def test_cleanup_failure_preserves_primary_result(self):
        class BadClose(FakeAIProvider):
            def close(self):
                raise RuntimeError("SECRET")
        result = interpret(BadClose(fake().config, structured_response=VALID))
        self.assertEqual(result.status, "SUCCESS")
        self.assertEqual(result.metrics["cleanup_error"], "PROVIDER_ERROR")

    def test_missing_context_still_closes_injected_provider(self):
        provider = fake()
        with tempfile.TemporaryDirectory() as out:
            result = ai.run_ai_interpretation(out, provider=provider)
        self.assertEqual(result.status, "CONTEXT_UNAVAILABLE")
        self.assertTrue(provider.closed)
        self.assertEqual(provider.requests, [])


class IdentityAndArchitectureTests(unittest.TestCase):
    def test_provider_model_configuration_identities_differ(self):
        providers = [fake(), fake(config=ProviderConfig("FAKE", "other", "offline")), fake(config=ProviderConfig("FAKE", "fake-v55", "other"))]
        self.assertEqual(len({provider_identity(p)["ai_config_fingerprint"] for p in providers}), 3)

    def test_ai_identity_does_not_export_options_or_credentials(self):
        provider = fake(config=ProviderConfig("FAKE", "f", "m", options={"api_key": "SECRET"}, credential_source="SECRET_ENV"))
        self.assertNotIn("SECRET", json.dumps(provider_identity(provider)))

    def test_assessment_identity_distinguishes_provider_and_model(self):
        from legacy_documenter.documentation.synthesis import request_identity
        req = request(metadata={"profile_id": "p"})
        self.assertNotEqual(request_identity(req, {}, fake()), request_identity(req, {}, fake(config=ProviderConfig("FAKE", "f", "other"))))

    def test_provider_source_and_configuration_do_not_invalidate_analyzer(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for directory in ANALYZER_CODE_DIRECTORIES:
                shutil.copytree(ROOT / "legacy_documenter" / directory, root / directory, ignore=shutil.ignore_patterns("__pycache__"))
            for relative in (*ANALYZER_CODE_FILES, PIPELINE_STAGES_FILE):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / "legacy_documenter" / relative, target)
            before = analyzer_code_fingerprint(root)
            (root / "llm/providers").mkdir(parents=True)
            (root / "llm/providers/custom.py").write_text("PROVIDER='new'\nMODEL='new'\n", encoding="utf-8")
            with patch.dict("os.environ", {"LEGACYMAPPER_LLM_PROVIDER": "FAKE", "LEGACYMAPPER_LLM_MODEL": "changed"}):
                self.assertEqual(analyzer_code_fingerprint(root), before)
            self.assertEqual(before, analyzer_code_fingerprint())

    def test_no_concrete_imports_in_neutral_boundaries(self):
        violations = []
        for folder in ("evidence", "context", "knowledge", "orchestration", "documentation"):
            for path in (ROOT / "legacy_documenter" / folder).rglob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8-sig"))
                for node in ast.walk(tree):
                    names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
                    if any("llm.providers" in name or "copilot" in name or "gemini" in name for name in names):
                        violations.append(path.relative_to(ROOT).as_posix())
                    if folder == "evidence" and any("legacy_documenter.llm" in name for name in names):
                        violations.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(violations, [])

    def test_contract_imports_no_implementation_or_registry(self):
        for name in ("contracts", "payload"):
            tree = ast.parse((ROOT / f"legacy_documenter/llm/{name}.py").read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    self.assertFalse(any(token in (node.module or "") for token in ("providers", "registry", "fake")))


class ProductivePipelineTests(unittest.TestCase):
    def test_actual_provider_neutral_request_uses_configured_model_timeout_and_schema(self):
        from types import SimpleNamespace
        from legacy_documenter.llm.providers.copilot import CopilotProvider
        class Session:
            async def send_and_wait(self, prompt, timeout):
                self.prompt, self.timeout = prompt, timeout
                return SimpleNamespace(data=SimpleNamespace(content='{"x":1}', model="requested", output_tokens=1))
            async def disconnect(self):
                self.closed = True
        class Client:
            def __init__(self):
                self.session = Session()
            async def start(self):
                pass
            async def stop(self):
                self.closed = True
            def create_session(self, **options):
                self.options = options
                return self.session
        client = Client()
        provider = CopilotProvider(ProviderConfig("COPILOT", "c", "configured", timeout_s=20), lambda: client)
        response = provider.generate(request(model_id="requested", timeout_s=5, output_contract={"required": ["x"]}))
        self.assertEqual(response.parsed_output, {"x": 1})
        self.assertEqual(client.options["model"], "requested")
        self.assertEqual(client.session.timeout, 5)
        self.assertIn("<output_contract>", client.session.prompt)
        self.assertTrue(client.closed and client.session.closed)

    def test_actual_provider_capability_mismatch_does_not_construct_client(self):
        from legacy_documenter.llm.providers.copilot import CopilotProvider
        provider = CopilotProvider(ProviderConfig("COPILOT", "c", "m", capabilities={"structured_output": False}), lambda: self.fail("client called"))
        self.assertEqual(provider.structured_generate(request(), {}).status, "UNSUPPORTED_CAPABILITY")

    def test_fake_pipeline_artifacts_metrics_grounding_and_source_immutability(self):
        provider = fake(structured_response={"findings": [{"statement": "The Save button reaches a stored procedure.", "confidence": "CONFIRMED", "evidence_refs": ["DAO-0197413858"]}]})
        before = {p.relative_to(FIXTURE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in FIXTURE.rglob("*") if p.is_file()}
        with tempfile.TemporaryDirectory() as out, patch.object(ai, "_resolve_provider", side_effect=AssertionError("real provider forbidden")):
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
            metrics = json.loads((Path(out) / "_cache_v53/RUN_METRICS.json").read_text())["ai"]
            proposals = json.loads((Path(out) / "proposals/AI_PROPOSALS.json").read_text())
            self.assertEqual(result.status.value, "SUCCESS")
            self.assertEqual(metrics["request_count"], 1)
            self.assertEqual(proposals["status"], "PENDING_TECHNICAL_LEAD_REVIEW")
            self.assertEqual(len(provider.requests), 1)
            self.assertTrue(provider.closed)
            self.assertFalse(result.canonical_knowledge_produced)
            self.assertFalse(result.technical_lead_approval)
            self.assertLessEqual(metrics["payload_estimated_tokens"], metrics["input_token_limit"])
        after = {p.relative_to(FIXTURE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in FIXTURE.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_legacy_missing_evidence_does_not_resolve_provider(self):
        from legacy_documenter.documentation import generator
        with tempfile.TemporaryDirectory() as workspace, patch.object(generator, "resolve_documentation_provider", side_effect=AssertionError("preflight must precede provider")):
            self.assertEqual(generator.run(workspace)["status"], "V3-R7_BLOCKED_MISSING_V2_EVIDENCE")

    def test_ai_disabled_no_credentials_and_no_ai_metrics(self):
        with tempfile.TemporaryDirectory() as out, patch.object(ProviderRegistry, "create", side_effect=AssertionError("disabled")):
            result = run_full_pipeline(FIXTURE, out, None, 12)
            metrics = json.loads((Path(out) / "_cache_v53/RUN_METRICS.json").read_text())
            self.assertFalse(result.ai_invoked)
            self.assertNotIn("ai", metrics)

    def test_failure_metrics_and_exit_semantics_preserved(self):
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=fake(forced_status="TIMEOUT"))
            metrics = json.loads((Path(out) / "_cache_v53/RUN_METRICS.json").read_text())["ai"]
            self.assertEqual(result.status.value, "PARTIAL")
            self.assertEqual(metrics["failure_count"], 1)
            self.assertEqual(metrics["error_category"], "TIMEOUT")


if __name__ == "__main__":
    unittest.main()
