import re
from copy import deepcopy
from typing import Any


SECRET_ASSIGN_RE = re.compile(
    r'(?i)\b(password|pwd|user\s*id|userid|uid|username|credentials?|tokens?)\s*=\s*([^;,\)"\'\s<>]+)'
)
CONNECTION_STRING_RE = re.compile(
    r'(?i)(connectionstring|defaultsettingvalueattribute)\s*\(\s*"([^"]*)"\s*\)'
)


def sanitize_text(value: str) -> str:
    """Performs sanitize text while preserving this module's deterministic contract."""
    sanitized = SECRET_ASSIGN_RE.sub(lambda match: f"{match.group(1)}=********", value)
    sanitized = CONNECTION_STRING_RE.sub(lambda match: f'{match.group(1)}("********")', sanitized)
    return sanitized


def sanitize_data(value: Any) -> Any:
    """Performs sanitize data while preserving this module's deterministic contract."""
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        return [sanitize_data(item) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_data(item) for item in value)
    if isinstance(value, dict):
        return {key: sanitize_data(item) for key, item in value.items()}
    return deepcopy(value)
