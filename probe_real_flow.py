import json
from pathlib import Path

from legacy_documenter.llm.core import (
    ProviderConfig,
    LLMRequest,
    measure_request_payload,
)
from legacy_documenter.llm.providers.copilot import CopilotProvider


FLOW_ID = "FLOW-0343552547"

PART_FILE = Path(
    r"E:\IAProyectos\LegacyMapper_Pilot_Output"
    r"\operaciones_v4_3_ai"
    r"\consumer_projection"
    r"\parts"
    r"\part-000008.json"
)


def find_flow(value):
    if isinstance(value, dict):
        if value.get("flow_id") == FLOW_ID:
            return value

        for child in value.values():
            found = find_flow(child)
            if found is not None:
                return found

    elif isinstance(value, list):
        for child in value:
            found = find_flow(child)
            if found is not None:
                return found

    return None


print("1. Cargando consumer projection...")

with PART_FILE.open("r", encoding="utf-8") as f:
    part = json.load(f)

flow = find_flow(part)

if flow is None:
    raise RuntimeError(f"No se encontró {FLOW_ID}")

print("   FLOW encontrado.")
print()

print("2. Tamaño de la unidad seleccionada:")

flow_json = json.dumps(
    flow,
    ensure_ascii=False,
    separators=(",", ":"),
)

print("   bytes:", len(flow_json.encode("utf-8")))
print("   chars:", len(flow_json))
print("   estimated tokens:", (len(flow_json) + 3) // 4)
print()


config = ProviderConfig(
    provider_type="COPILOT",
    provider_id="copilot-local",
    model_id="",
    context_window=128000,
    max_output_tokens=4000,
    options={
        "timeout": 120,
    },
)

provider = CopilotProvider(config)


request = LLMRequest(
    purpose="FUNCTIONAL_INTERPRETATION",

    system_instruction=(
        "Eres un analista de software legacy. "
        "Debes interpretar exclusivamente la evidencia determinista "
        "suministrada. "
        "No inventes clases, procedimientos almacenados, operaciones SQL, "
        "flujos, llamadas ni comportamiento no presente en la evidencia. "
        "Toda afirmación técnica debe poder trazarse a una referencia "
        "existente en el contexto."
    ),

    user_instruction=(
        "Interpreta funcionalmente este único flujo legacy. "
        "Explica en español qué inicia el flujo, qué componentes participan, "
        "qué operaciones de datos confirmadas ejecuta, qué comportamiento "
        "funcional puede afirmarse y qué información permanece incierta. "
        "Distingue explícitamente evidencia confirmada de inferencias. "
        "No completes huecos con conocimiento externo."
    ),

    context={
        "selected_flow": flow,
    },

    context_package_id=f"REAL-FLOW-{FLOW_ID}",
    context_schema_version="1.0",
    source_snapshot="operaciones_v4_3_ai",

    max_output_tokens=2500,
    structured_output=True,

    metadata={
        "evidence_policy": {
            "only_context_evidence": True,
            "no_external_knowledge": True,
            "no_new_identifiers": True,
        },
        "claim_policy": {
            "technical_claims_require_evidence": True,
        },
        "missing_information_policy": {
            "declare_unknown": True,
            "never_invent": True,
        },
    },
)


schema = {
    "type": "object",
    "additionalProperties": False,

    "required": [
        "flow_id",
        "summary",
        "entry_point",
        "confirmed_behavior",
        "confirmed_data_operations",
        "uncertainties",
        "evidence_refs",
    ],

    "properties": {
        "flow_id": {
            "type": "string",
            "const": FLOW_ID,
        },

        "summary": {
            "type": "string",
        },

        "entry_point": {
            "type": "string",
        },

        "confirmed_behavior": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },

        "confirmed_data_operations": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },

        "uncertainties": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },

        "evidence_refs": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
}


print("3. Midiendo payload final...")

measurement = measure_request_payload(
    request,
    schema,
)

for key, value in measurement.items():
    print(f"   {key}: {value}")

print()


print("4. Invocando CopilotProvider...")

response = provider.structured_generate(
    request,
    schema,
)

print()
print("STATUS:")
print(response.status)

print()
print("MODEL:")
print(response.model_id)

print()
print("SCHEMA STATUS:")
print(response.schema_validation_status)

print()
print("VALIDATION ERRORS:")
print(response.validation_errors)

print()
print("PARSED OUTPUT:")
print(
    json.dumps(
        response.parsed_output,
        indent=2,
        ensure_ascii=False,
    )
)

print()
print("RAW CONTENT:")
print(response.content)

print()
print("ERROR:")
print(response.error)