"""Deterministic, idempotent normalization for `SourceInput`.

Only meaning-preserving normalization happens here: trimming meaningless
outer whitespace, canonicalizing blank-to-absent strings, validating metadata
is JSON-compatible, and sanitizing obvious secrets via the existing
`legacy_documenter.utils.sanitizer`. Normalization never rewrites, summarizes,
translates, or infers anything the caller did not supply.
"""
from dataclasses import replace
from typing import Any

from legacy_documenter.knowledge.input.contracts import SourceInput, SourceInputValidationError
from legacy_documenter.utils.sanitizer import sanitize_data, sanitize_text

_JSON_PRIMITIVES = (str, int, float, bool, type(None))


def _normalize_optional_text(value: str | None) -> str | None:
    """Trims outer whitespace and canonicalizes a blank string to `None`.

    Idempotent: re-normalizing an already-normalized value returns it unchanged.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        raise SourceInputValidationError("text_field_must_be_string_or_none")
    trimmed = value.strip()
    return sanitize_text(trimmed) if trimmed else None


def validate_metadata(metadata: Any) -> dict:
    """Rejects metadata that is not a JSON-compatible dict, then sanitizes its text values.

    Nested lists/dicts are walked recursively; any value that is not a
    JSON-compatible primitive or container (for example a set, a function, or
    an arbitrary object) is rejected deterministically rather than coerced.
    """
    if not isinstance(metadata, dict):
        raise SourceInputValidationError("metadata_must_be_a_dict")
    _assert_json_compatible(metadata)
    return sanitize_data(metadata)


def _assert_json_compatible(value: Any) -> None:
    if isinstance(value, _JSON_PRIMITIVES):
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise SourceInputValidationError("metadata_keys_must_be_strings")
            _assert_json_compatible(item)
        return
    if isinstance(value, list):
        for item in value:
            _assert_json_compatible(item)
        return
    raise SourceInputValidationError(f"unsupported_metadata_value_type:{type(value).__name__}")


def normalize_source_input(raw: SourceInput) -> SourceInput:
    """Returns a normalized copy of `raw`; never mutates the input in place.

    `normalize_source_input(normalize_source_input(x))` always equals
    `normalize_source_input(x)` for any structurally valid `SourceInput`.
    """
    return replace(
        raw,
        content=_normalize_optional_text(raw.content),
        reference=_normalize_optional_text(raw.reference),
        title=_normalize_optional_text(raw.title),
        contributor=_normalize_optional_text(raw.contributor),
        authority_scope=_normalize_optional_text(raw.authority_scope),
        metadata=validate_metadata(raw.metadata),
    )
