"""AI-output configuration identities, deliberately separate from analyzer fingerprints."""
from .contracts import sid


def provider_identity(provider) -> dict:
    info = provider.model_info()
    caps = provider.capabilities()
    config = getattr(provider, "config", None)
    # Hash limits and public capabilities only. No endpoint, credentials or arbitrary options.
    descriptor = {
        "provider_id": info.provider_id, "model_id": info.model_id,
        "provider_type": info.provider_type, "provider_version": getattr(caps, "provider_version", "legacy"),
        "context_window": caps.context_window, "max_output_tokens": caps.max_output_tokens,
        "structured_output": caps.structured_output,
        "timeout_s": config.timeout if config is not None else None,
    }
    return {"ai_config_fingerprint": sid("AICFG", descriptor)}
