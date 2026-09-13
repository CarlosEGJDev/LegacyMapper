"""Provider/direction/type classification and normalization helpers (V4.1-R6)."""


def matched_type(match) -> str | None:
    """Returns whichever of a multi-alternative regex match's type groups fired."""
    for name in ("type1", "type2", "type3", "type4"):
        value = match.groupdict().get(name)
        if value:
            return value
    return None


def direction(value: str) -> str:
    """Normalizes an ADO.NET parameter direction keyword."""
    normalized = value.strip().lower()
    if normalized in {"out", "output"}:
        return "Output"
    if normalized in {"inout", "inputoutput"}:
        return "InputOutput"
    if normalized in {"return", "returnvalue"}:
        return "ReturnValue"
    return "Input" if normalized == "in" else value.strip()


def provider(type_name: str) -> str:
    """Classifies a fully/partially qualified ADO.NET type name to its provider."""
    lowered = type_name.lower()
    if "oracle" in lowered:
        return "Oracle"
    if "oledb" in lowered:
        return "OleDb"
    return type_name.rsplit(".", 1)[-1]
