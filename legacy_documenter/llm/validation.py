"""Local deterministic structure validation; semantic grounding remains in the domain."""
from __future__ import annotations

import json


def validate_structured_response(response, schema: dict):
    if response.status != "SUCCESS":
        return response
    value = response.parsed_output
    if value is None:
        try:
            value = json.loads(response.content)
        except (TypeError, ValueError):
            response.status = "INVALID_STRUCTURED_OUTPUT"
            response.schema_validation_status = "INVALID_STRUCTURED_OUTPUT"
            response.validation_errors = ["invalid json"]
            return response
    errors = [] if isinstance(value, dict) else ["expected object"]
    errors.extend("missing:" + key for key in schema.get("required", []) if not isinstance(value, dict) or key not in value)
    response.parsed_output = value if not errors else None
    response.validation_errors = errors
    response.schema_validation_status = "INVALID_STRUCTURED_OUTPUT" if errors else "VALID_STRUCTURED_OUTPUT"
    if errors:
        response.status = "INVALID_STRUCTURED_OUTPUT"
    return response
