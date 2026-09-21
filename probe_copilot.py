import asyncio
import traceback

from copilot import CopilotClient


async def main():
    client = None

    try:
        print("1. Creando CopilotClient...")
        client = CopilotClient(use_logged_in_user=True)

        print("2. client.start()...")
        await client.start()
        print("   OK")

        print("3. list_models()...")
        models = await client.list_models()

        print(f"   Modelos encontrados: {len(models)}")

        for i, model in enumerate(models):
            print(
                i,
                "id=",
                getattr(model, "id", None),
                "model_id=",
                getattr(model, "model_id", None),
                "name=",
                getattr(model, "name", None),
            )

    except Exception as exc:
        print()
        print("ERROR REAL:")
        print(type(exc).__name__)
        print(repr(exc))
        print(str(exc))
        traceback.print_exc()

    finally:
        if client is not None:
            try:
                await client.stop()
            except Exception:
                pass


asyncio.run(main())