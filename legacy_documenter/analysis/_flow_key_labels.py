"""Method-key and display-label derivation helpers for flow resolution (V4.1-R6)."""


def method_key(class_name: str | None, method: str | None, project: str | None) -> tuple | None:
    """Builds the canonical (class, method, project) lookup key, or None if incomplete."""
    if not class_name or not method:
        return None
    return (class_name.lower(), method.lower(), project)


def method_label(key: tuple) -> str:
    """Formats a method key into its display label."""
    return f"{key[2] or '<unknown>'}::{key[0]}.{key[1]}"


def class_id(key: tuple) -> str:
    """Formats a method key's owning class into its display label."""
    return f"{key[2] or '<unknown>'}::{key[0]}"


def entry_method_key(entry: dict) -> tuple | None:
    """Derives the method key an entry point's handler_method resolves to."""
    handler_method = entry.get("handler_method") or ""
    if "." not in handler_method:
        return None
    class_name, method = handler_method.rsplit(".", 1)
    return method_key(class_name, method, entry.get("project"))


def resolved_method_key(call: dict) -> tuple | None:
    """Derives the method key a resolved call target points to."""
    target = call.get("resolved_target") or ""
    parts = target.split(".")
    if len(parts) < 2:
        return None
    return method_key(parts[-2], parts[-1], call.get("resolved_project"))
