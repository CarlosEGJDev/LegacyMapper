"""Explicit deterministic provider; no transport, SDK or credential access."""
from copy import deepcopy
from dataclasses import replace
import json

from .contracts import LLMProvider, LLMModelInfo, LLMResponse, ProviderCapabilities, ProviderConfig, ProviderError, Usage, STATUSES, sid
from .validation import validate_structured_response


class FakeLLMProvider(LLMProvider):
    """Configurable responses and failure injection with isolated request recording."""

    def __init__(self, config: ProviderConfig, fixed_response="ok", structured_response=None, forced_status=None, error: ProviderError | None = None):
        self.config = config
        self.fixed = fixed_response
        self.structured = deepcopy(structured_response)
        self.forced = forced_status
        self.error = error
        self.requests = []
        self.closed = False

    def capabilities(self):
        values = dict(context_window=self.config.context_window, max_output_tokens=self.config.max_output_tokens)
        values.update(self.config.capabilities)
        values.update(provider_id=self.config.provider_id, model_id=self.config.model_id)
        return ProviderCapabilities(**values)

    def model_info(self):
        return LLMModelInfo(self.config.provider_id, self.config.model_id, self.config.model_id, self.config.provider_type, self.capabilities())

    def _status(self, request):
        caps = self.capabilities()
        estimate = (request.context.get("statistics") or {}).get("estimated_tokens", 0)
        if (request.structured_output or request.output_contract is not None) and not caps.structured_output:
            return "UNSUPPORTED_CAPABILITY"
        if caps.context_window and estimate > caps.context_window:
            return "CONTEXT_TOO_LARGE"
        if caps.max_output_tokens and request.max_output_tokens and request.max_output_tokens > caps.max_output_tokens:
            return "INVALID_REQUEST"
        if request.temperature is not None and not caps.temperature_control:
            return "UNSUPPORTED_CAPABILITY"
        return self.forced or (self.error.error_code if self.error and self.error.error_code in STATUSES else "PROVIDER_ERROR" if self.error else "SUCCESS")

    def generate(self, request):
        self.requests.append(deepcopy(request))
        status = self._status(request)
        content = self.fixed if status == "SUCCESS" else None
        response = LLMResponse(
            request.request_id, sid("RESP", [request.request_id, self.config.provider_id, self.config.model_id, content, status]),
            self.config.provider_id, self.config.model_id, status, content,
            usage=Usage(estimated=True, token_count_method="context_estimate"),
            metadata={"context_package_id": request.context_package_id, "source_snapshot": request.source_snapshot}, error=deepcopy(self.error),
        )
        if request.output_contract is not None and status == "SUCCESS":
            response.content = json.dumps(self.structured, sort_keys=True)
            response.parsed_output = deepcopy(self.structured)
            return validate_structured_response(response, request.output_contract)
        return response

    def structured_generate(self, request, schema):
        request.structured_output = True
        return self.generate(replace(request, output_contract=schema))

    def close(self):
        self.closed = True


FakeAIProvider = FakeLLMProvider
