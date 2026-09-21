from legacy_documenter.llm.core import (
    ProviderConfig,
    LLMRequest,
)
from legacy_documenter.llm.providers.copilot import CopilotProvider


config = ProviderConfig(
    provider_type="COPILOT",
    provider_id="copilot-local",
    model_id="",
    context_window=128000,
    max_output_tokens=2000,
    options={
        "timeout": 60,
    },
)

provider = CopilotProvider(config)

request = LLMRequest(
    purpose="TEST",
    system_instruction=(
        "Eres una prueba de integración de LegacyMapper. "
        "Debes responder únicamente usando la evidencia suministrada."
    ),
    user_instruction=(
        "Devuelve el estado de la prueba y el identificador recibido."
    ),
    context={
        "records": [
            {
                "ref": "TEST-EVIDENCE-001",
                "value": "LegacyMapper Copilot provider test",
            }
        ]
    },
    context_package_id="TEST-CONTEXT-001",
    context_schema_version="1.0",
    source_snapshot="TEST-SNAPSHOT",
    max_output_tokens=500,
    structured_output=True,
    metadata={
        "evidence_policy": {
            "allow_only_context_evidence": True
        },
        "claim_policy": {
            "allow_only_context_evidence": True
        },
        "missing_information_policy": {
            "do_not_invent": True
        },
    },
)

schema = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "status",
        "evidence_ref",
        "message",
    ],
    "properties": {
        "status": {
            "type": "string",
            "enum": ["OK"],
        },
        "evidence_ref": {
            "type": "string",
            "const": "TEST-EVIDENCE-001",
        },
        "message": {
            "type": "string",
        },
    },
}

response = provider.structured_generate(request, schema)

print("STATUS:")
print(response.status)

print()
print("PROVIDER:")
print(response.provider_id)

print()
print("MODEL:")
print(response.model_id)

print()
print("SCHEMA STATUS:")
print(response.schema_validation_status)

print()
print("PARSED OUTPUT:")
print(response.parsed_output)

print()
print("VALIDATION ERRORS:")
print(response.validation_errors)

print()
print("RAW CONTENT:")
print(response.content)

print()
print("ERROR:")
print(response.error)