import asyncio
import traceback

from copilot import CopilotClient


async def main():
    client = None
    session = None

    try:
        print("1. Creando CopilotClient...")
        client = CopilotClient(use_logged_in_user=True)

        print("2. client.start()...")
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

        model = getattr(models[0], "id", None) or getattr(
            models[0], "model_id", None
        )

        print("4. Modelo seleccionado:", model)

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

        print("6. send_and_wait()...")

        event = await session.send_and_wait(
            "Responde exclusivamente con este JSON: "
            '{"status":"OK","message":"Copilot funciona"}',
            timeout=60,
        )

        print("   OK")
        print()
        print("RESPUESTA:")
        print(event.data.content)

        print()
        print("MODELO REAL:")
        print(getattr(event.data, "model", None))

    except Exception as exc:
        print()
        print("ERROR REAL:")
        print(type(exc).__name__)
        print(repr(exc))
        print(str(exc))
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