import asyncio
import json
import traceback
from pathlib import Path

from copilot import CopilotClient

from legacy_documenter.llm.core import (
    ProviderConfig,
    LLMRequest,
    render_request_payload,
)


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


with PART_FILE.open("r", encoding="utf-8") as f:
    part = json.load(f)

flow = find_flow(part)

if flow is None:
    raise RuntimeError(f"No se encontró {FLOW_ID}")


request = LLMRequest(
    purpose="FUNCTIONAL_INTERPRETATION",

    system_instruction=(
        "Eres un analista de software legacy. "
        "Debes interpretar exclusivamente la evidencia determinista suministrada. "
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
            "items": {"type": "string"},
        },
        "confirmed_data_operations": {
            "type": "array",
            "items": {"type": "string"},
        },
        "uncertainties": {
            "type": "array",
            "items": {"type": "string"},
        },
        "evidence_refs": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
}


prompt = render_request_payload(request, schema)

print("Payload chars:", len(prompt))
print("Payload bytes:", len(prompt.encode("utf-8")))
print("Estimated tokens:", (len(prompt) + 3) // 4)
print()


async def main():
    client = None
    session = None

    try:
        print("1. Creando cliente...")
        client = CopilotClient(use_logged_in_user=True)

        print("2. start()...")
        await client.start()
        print("   OK")

        print("3. list_models()...")
        models = await client.list_models()

        for model in models:
            print(
                "   id=",
                getattr(model, "id", None),
                "model_id=",
                getattr(model, "model_id", None),
                "name=",
                getattr(model, "name", None),
            )

        model = (
            getattr(models[0], "id", None)
            or getattr(models[0], "model_id", None)
        )

        print("4. Modelo:", model)

        async def deny(_request):
            from copilot.generated.rpc import PermissionDecisionDeniedByRules
            return PermissionDecisionDeniedByRules(rules=[])

        print("5. create_session()...")

        session = client.create_session(
            model=model,
            on_permission_request=deny,
            tools=[],
            available_tools=[],
            enable_file_change_tracking=False,
            skip_custom_instructions=True,
            enable_config_discovery=False,
            enable_on_demand_instruction_discovery=False,
            enable_file_hooks=False,
            enable_host_git_operations=False,
            enable_skills=False,
            enable_mcp_apps=False,
            enable_session_store=False,
        )

        if asyncio.iscoroutine(session):
            session = await session

        print("   OK")

        print("6. send_and_wait() con payload real...")

        event = await session.send_and_wait(
            prompt,
            timeout=120,
        )

        print("   OK")
        print()

        print("MODELO REAL:")
        print(getattr(event.data, "model", None))

        print()
        print("RESPUESTA:")
        print(event.data.content)

    except Exception as exc:
        print()
        print("=" * 70)
        print("ERROR REAL DEL SDK")
        print("=" * 70)
        print("TYPE:", type(exc).__name__)
        print("REPR:", repr(exc))
        print("STR :", str(exc))
        print()
        traceback.print_exc()

    finally:
        if session is not None:
            try:
                await session.disconnect()
            except Exception:
                pass

        if client is not None:
            try:
                await client.stop()
            except Exception:
                pass


asyncio.run(main())