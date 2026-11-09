"""Provider/account preflight: report the authenticated identity before any real request. Never prints or stores secrets."""
from __future__ import annotations

import asyncio
import os


def check_account(provider_type: str, *, expect: str | None = None, timeout_s: float = 60.0) -> dict:
    """Returns {provider_type, checked, authenticated, account, matches_expected, detail}. Offline providers need no account."""
    kind = provider_type.upper()
    result = {"provider_type": kind, "checked": False, "authenticated": None, "account": None, "matches_expected": None, "detail": ""}
    if kind in ("STUB", "FAKE"):
        result.update(checked=True, authenticated=True, account="(offline provider)", detail="no account involved")
        return result
    if kind != "COPILOT":
        result["detail"] = "no account preflight available for this provider"
        return result
    try:
        from copilot import CopilotClient
    except ImportError:
        result["detail"] = "provider SDK is not installed"
        return result

    async def probe():
        client = CopilotClient(use_logged_in_user=True)
        await client.start()
        try:
            return await client.get_auth_status()
        finally:
            await client.stop()

    try:
        status = asyncio.run(asyncio.wait_for(probe(), timeout_s))
        result.update(checked=True, authenticated=bool(getattr(status, "isAuthenticated", False)), account=getattr(status, "login", None))
    except Exception as exc:                      # unreachable CLI, timeout, auth failure: report, never guess
        result["detail"] = f"identity unavailable ({type(exc).__name__}); set COPILOT_CLI_PATH if the CLI is not on the default path" \
            if "COPILOT_CLI_PATH" not in os.environ else f"identity unavailable ({type(exc).__name__})"
    if expect is not None:
        result["matches_expected"] = bool(result["account"]) and str(result["account"]).lower() == expect.lower()
    return result
