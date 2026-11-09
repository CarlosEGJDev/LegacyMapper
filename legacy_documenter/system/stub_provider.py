"""Offline deterministic provider for dry runs and tests. It never talks to a network, SDK or credential store.

It "interprets" by quoting the supplied facts: every claim cites the fact it repeats, so the output is grounded by construction.
Everything it produces is marked synthetic (provider id `stub-local`); it is NOT AI interpretation and must never be presented
as such. Use it to exercise the whole pipeline (planning, persistence, resume, projections) at zero provider cost.
"""
from __future__ import annotations

import json

from legacy_documenter.llm.contracts import (LLMModelInfo, LLMProvider, LLMResponse, ProviderCapabilities, ProviderConfig, Usage, sid)

from .models import SECTIONS

STUB_PROVIDER_ID = "stub-local"
STUB_MODEL_ID = "deterministic-stub"
_SECTION_KINDS = {
    "purpose": ("structure", "view", "child"), "summary": ("child", "structure"), "responsibilities": ("flow", "data", "view"),
    "behavior": ("view",), "interactions": ("data",), "relations": ("relation",), "consumers": ("relation",),
    "dependencies": ("reference", "relation"), "business_flow": ("flow",), "data_interactions": ("data",), "subsystems": ("child",),
    "data": ("data", "child"), "solutions": ("child",), "interaction_paths": ("child", "relation"), "cross_project": ("relation", "child"),
}


class StubProvider(LLMProvider):
    def __init__(self, config: ProviderConfig, **_ignored) -> None:
        self.config = config
        self.calls = 0

    def capabilities(self):
        return ProviderCapabilities(context_window=self.config.context_window, max_output_tokens=self.config.max_output_tokens,
                                    structured_output=True, json_mode=True, temperature_control=False,
                                    provider_id=STUB_PROVIDER_ID, model_id=STUB_MODEL_ID)

    def model_info(self):
        return LLMModelInfo(STUB_PROVIDER_ID, STUB_MODEL_ID, STUB_MODEL_ID, "STUB", self.capabilities(), {"synthetic": True})

    def _kind_from(self, request) -> str:
        return request.context_package_id.split("-")[2]

    def build(self, kind: str, facts: list[dict]) -> dict:
        out: dict = {}
        for section in SECTIONS[kind]:
            claims = []
            if section == "unresolved":
                pool = [f for f in facts if f["kind"] == "unresolved" or f["certainty"] == "unresolved"]
                for f in pool[:3]:
                    claims.append({"text": f["fact"], "status": "UNRESOLVED", "refs": [f["ref"]]})
            else:
                kinds = _SECTION_KINDS.get(section, ("flow",))
                pool = [f for f in facts if f["kind"] in kinds and f["kind"] != "name"]
                for f in pool[:3]:
                    status = "CONFIRMED" if f["certainty"] == "confirmed" else "INFERRED" if f["certainty"] == "inferred" else "UNRESOLVED"
                    claims.append({"text": f["fact"], "status": status, "refs": [f["ref"]]})
            out[section] = claims
        return out

    def generate(self, request):
        self.calls += 1
        facts = (request.context or {}).get("facts", [])
        parsed = self.build(self._kind_from(request), facts)
        content = json.dumps(parsed, ensure_ascii=False, sort_keys=True)
        return LLMResponse(request.request_id, sid("RESP", [request.request_id, content]), STUB_PROVIDER_ID, STUB_MODEL_ID, "SUCCESS",
                           content=content, usage=Usage(estimated=True, token_count_method="stub"), parsed_output=parsed,
                           metadata={"synthetic": True}, schema_validation_status="VALID_STRUCTURED_OUTPUT")
