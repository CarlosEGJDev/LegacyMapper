"""Shared AI diagnostic sanitizer layered on the centralized evidence sanitizer.

The historical vendor patterns live here rather than in an implementation.
Never pass a request, prompt, environment dump or raw response to diagnostics.
"""
import re
from legacy_documenter.utils.sanitizer import sanitize_data, sanitize_text

_SECRET_VALUE_PATTERNS = [re.compile(p, re.IGNORECASE) for p in (
    r"bearer\s+\S+",
    r"(gh|github|copilot_github)?_?token\s*[:=]\s*\S+",
    r"(api[_-]?key|session[_-]?token|oauth[_-]?secret|[a-z0-9_\-]*secret[a-z0-9_\-]*)\s*[:=]\s*\S+",
    r"cookie\s*[:=]\s*\S+",
    r"\bgh[pousr]_[A-Za-z0-9]{10,}\b",
    r"(?i)(authorization|password|pwd|credential)\s*[:=]\s*\S+",
)]


def sanitize_diagnostic(message: str) -> str:
    out = sanitize_text(str(message))
    for pattern in _SECRET_VALUE_PATTERNS:
        out = pattern.sub("[REDACTED]", out)
    return out


def safe_diagnostic_data(value):
    value = sanitize_data(value)
    if isinstance(value, str):
        return sanitize_diagnostic(value)
    if isinstance(value, list):
        return [safe_diagnostic_data(v) for v in value]
    if isinstance(value, dict):
        return {k: safe_diagnostic_data(v) for k, v in value.items()}
    return value


def error_category(error) -> str:
    """Normalize diagnostics without exporting arbitrary exception/request text."""
    code = error if isinstance(error, str) else str(getattr(error, "error_code", ""))
    if code in {"TIMEOUT", "CANCELLED", "RATE_LIMITED", "UNSUPPORTED_CAPABILITY", "INVALID_REQUEST", "CONTEXT_TOO_LARGE", "INVALID_STRUCTURED_OUTPUT", "MODEL_UNAVAILABLE", "PROVIDER_CONFIGURATION_ERROR", "AUTHENTICATION_ERROR", "PROVIDER_UNAVAILABLE"}:
        return code
    if isinstance(error, TimeoutError):
        return "TIMEOUT"
    if isinstance(error, (ImportError, ConnectionError)):
        return "PROVIDER_UNAVAILABLE"
    return "PROVIDER_ERROR"
