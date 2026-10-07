"""Composition boundary: lazy factories, explicit selection and environment config.

FAKE is only selected explicitly. The historical production default remains
COPILOT; an unknown explicit provider never falls back to that default.
No factory loads credentials during construction or while AI is disabled.
"""
from __future__ import annotations

import os
from collections.abc import Callable, Mapping

from .contracts import LLMProvider, ProviderConfig


def _fake(config, **kwargs):
    from .fake import FakeLLMProvider
    return FakeLLMProvider(config, **kwargs)


def _copilot(config, **kwargs):
    from .providers.copilot import CopilotProvider
    return CopilotProvider(config, **kwargs)


class ProviderRegistry:
    """Instance-scoped factories; register explicit implementations without plugin discovery."""

    def __init__(self):
        self._factories: dict[str, Callable] = {"FAKE": _fake, "COPILOT": _copilot}

    def register(self, provider_type: str, factory: Callable) -> None:
        if not provider_type or not callable(factory):
            raise ValueError("invalid provider factory")
        key = provider_type.upper()
        if key in self._factories:
            raise ValueError("duplicate provider factory")
        self._factories[key] = factory

    def create(self, config: ProviderConfig, **kwargs) -> LLMProvider:
        factory = self._factories.get(config.provider_type.upper())
        if factory is None:
            raise ValueError("unknown provider")
        return factory(config, **kwargs)


def config_from_environment(environ: Mapping[str, str] | None = None, *, max_output_tokens: int = 2000, timeout_s: float = 120) -> ProviderConfig:
    env = os.environ if environ is None else environ
    provider_type = env.get("LEGACYMAPPER_LLM_PROVIDER", "COPILOT")
    provider_id = env.get("LEGACYMAPPER_LLM_PROVIDER_ID", f"{provider_type.lower()}-local")
    model_id = env.get("LEGACYMAPPER_LLM_MODEL", "")
    try:
        window = int(env["LEGACYMAPPER_LLM_CONTEXT_WINDOW"]) if "LEGACYMAPPER_LLM_CONTEXT_WINDOW" in env else None
        output = int(env.get("LEGACYMAPPER_LLM_MAX_OUTPUT_TOKENS", max_output_tokens))
        timeout = float(env.get("LEGACYMAPPER_LLM_TIMEOUT", timeout_s))
        if (window is not None and window <= 0) or output <= 0:
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError("invalid provider limits") from None
    return ProviderConfig(provider_type, provider_id, model_id, context_window=window, max_output_tokens=output, options={"timeout": timeout}, timeout_s=timeout)


def resolve_provider(*, enabled: bool, config: ProviderConfig | None = None, registry: ProviderRegistry | None = None, **kwargs):
    if not enabled:
        return None
    return (registry or ProviderRegistry()).create(config or config_from_environment(), **kwargs)


def resolve_documentation_provider(*, max_output_tokens: int):
    """Legacy documentation composition; retain model preflight inside this boundary."""
    config = config_from_environment(max_output_tokens=max_output_tokens)
    if config.provider_type.upper() == "COPILOT" and not config.model_id:
        import asyncio
        from .copilot_pilot import discover_model
        config.model_id = asyncio.run(discover_model())
    return ProviderRegistry().create(config)
