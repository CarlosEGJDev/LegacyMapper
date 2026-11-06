"""Manual listing of Copilot models for the authenticated user (REAL provider). See README.md."""
import asyncio
from copilot import CopilotClient

async def main():
    client = CopilotClient(use_logged_in_user=True)
    await client.start()

    try:
        models = await client.list_models()

        for i, model in enumerate(models):
            print("INDEX:", i)
            print("ID:", getattr(model, "id", None))
            print("MODEL_ID:", getattr(model, "model_id", None))
            print("NAME:", getattr(model, "name", None))
            print("DISPLAY_NAME:", getattr(model, "display_name", None))
            print("RAW:", model)
            print("-" * 80)

    finally:
        await client.stop()

asyncio.run(main())