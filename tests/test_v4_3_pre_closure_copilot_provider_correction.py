"""V4.3 pre-closure Copilot provider correction: verification tests.

Covers the three real-pilot defects (F-01 dependency, F-02 diagnostics,
F-03/F-04 lost `attempted_model` and secret leakage) with mocks only --
no test here performs a real GitHub Copilot SDK call or requires the
`copilot` package to be installed.
"""
import json,sys,unittest
from dataclasses import asdict
from types import SimpleNamespace

from legacy_documenter.llm import LLMRequest,ProviderConfig
from legacy_documenter.llm.providers.copilot import CopilotProvider


def request() -> LLMRequest:
    return LLMRequest(
        "TEST","SYS","TASK",{"records":[{"ref":"E1"}]},"P1","3.1.0","S1",
        structured_output=True,metadata={},
    )


def config(model: str = "requested-model") -> ProviderConfig:
    return ProviderConfig("COPILOT","copilot-local",model,capabilities={})


class FailingSession:
    def __init__(self, error: Exception | None = None):
        self.error = error

    async def send_and_wait(self, prompt, timeout=60):
        if self.error:
            raise self.error
        return SimpleNamespace(
            data=SimpleNamespace(content='{"assessment_id":"A","claims":[]}', model="gpt-5.6-luna", output_tokens=4)
        )

    async def disconnect(self):
        pass


class FailingClient:
    def __init__(self, start_error=None, list_models_error=None, create_session_error=None,
                 models=None, session=None):
        self.start_error = start_error
        self.list_models_error = list_models_error
        self.create_session_error = create_session_error
        self.models = models if models is not None else [SimpleNamespace(id="auto")]
        self.session = session or FailingSession()

    async def start(self):
        if self.start_error:
            raise self.start_error

    async def stop(self):
        pass

    async def list_models(self):
        if self.list_models_error:
            raise self.list_models_error
        return self.models

    def create_session(self, **options):
        if self.create_session_error:
            raise self.create_session_error
        return self.session


class T1ProviderAvailableWithoutRealCopilotPackage(unittest.TestCase):
    def test_provider_works_via_injected_client_even_when_copilot_module_is_absent(self):
        # `from copilot import CopilotClient` is deferred to inside `_generate`,
        # never imported at module load time -- so the provider class itself
        # must be usable, with an injected client, even in an environment
        # where the real `copilot` package is not installed.
        self.assertNotIn("copilot", sys.modules)
        client = FailingClient()
        out = CopilotProvider(config(), lambda: client).generate(request())
        self.assertEqual(out.status, "SUCCESS")


class T2ClientInitFailure(unittest.TestCase):
    def test_client_init_failure_reports_phase_and_exception_type(self):
        def factory():
            raise RuntimeError("boom")
        out = CopilotProvider(config(), factory).generate(request())
        self.assertEqual(out.error.error_code, "PROVIDER_ERROR")
        self.assertEqual(out.error.details["phase"], "client_init")
        self.assertEqual(out.error.details["exception_type"], "RuntimeError")
        self.assertFalse(any("credential" in k.lower() or "token" in k.lower() for k in out.error.details))


class T3ClientStartFailure(unittest.TestCase):
    def test_client_start_failure_reports_phase(self):
        client = FailingClient(start_error=RuntimeError("start failed"))
        out = CopilotProvider(config(), lambda: client).generate(request())
        self.assertEqual(out.error.details["phase"], "client_start")
        self.assertEqual(out.error.details["exception_type"], "RuntimeError")


class T4ListModelsAuthFailure(unittest.TestCase):
    def test_list_models_auth_failure_is_diagnosable_and_sanitized(self):
        err = RuntimeError("JsonRpcError: Not authenticated. Please authenticate first.")
        client = FailingClient(list_models_error=err)
        out = CopilotProvider(config(""), lambda: client).generate(request())
        self.assertEqual(out.error.details["phase"], "list_models")
        self.assertEqual(out.error.details["exception_type"], "RuntimeError")
        self.assertIn("Not authenticated", out.error.details.get("sanitized_message",""))


class T5DynamicModelPreserved(unittest.TestCase):
    def test_attempted_model_survives_a_later_phase_failure(self):
        client = FailingClient(models=[SimpleNamespace(id="auto")], create_session_error=RuntimeError("session failed"))
        out = CopilotProvider(config(""), lambda: client).generate(request())
        self.assertEqual(out.error.details["attempted_model"], "auto")
        self.assertEqual(out.model_id, "auto")
        self.assertEqual(out.error.model_id, "auto")


class T6CreateSessionFailure(unittest.TestCase):
    def test_create_session_failure_reports_phase(self):
        client = FailingClient(create_session_error=RuntimeError("cs failed"))
        out = CopilotProvider(config(), lambda: client).generate(request())
        self.assertEqual(out.error.details["phase"], "create_session")


class T7SendAndWaitFailure(unittest.TestCase):
    def test_send_and_wait_failure_reports_phase(self):
        session = FailingSession(error=RuntimeError("saw failed"))
        client = FailingClient(session=session)
        out = CopilotProvider(config(), lambda: client).generate(request())
        self.assertEqual(out.error.details["phase"], "send_and_wait")


class T8ExistingSuccessPathPreserved(unittest.TestCase):
    def test_success_preserves_structured_output_and_actual_model(self):
        client = FailingClient()
        out = CopilotProvider(config(), lambda: client).structured_generate(
            request(), {"required":["assessment_id","claims"]}
        )
        self.assertEqual(out.status, "SUCCESS")
        self.assertEqual(out.schema_validation_status, "VALID_STRUCTURED_OUTPUT")
        self.assertEqual(out.model_id, "gpt-5.6-luna")
        self.assertIsNone(out.error)


class T9SecretsNeverLeak(unittest.TestCase):
    def test_secret_shaped_substrings_are_redacted_from_details_and_serialized_result(self):
        err = RuntimeError("Authorization: Bearer SECRET_TOKEN failed; GH_TOKEN=SECRET also present")
        client = FailingClient(start_error=err)
        out = CopilotProvider(config(), lambda: client).generate(request())
        serialized = json.dumps(asdict(out.error))
        self.assertNotIn("SECRET_TOKEN", serialized)
        self.assertNotIn("SECRET", serialized)
        self.assertIn("[REDACTED]", out.error.details.get("sanitized_message",""))


if __name__ == "__main__":
    unittest.main()
