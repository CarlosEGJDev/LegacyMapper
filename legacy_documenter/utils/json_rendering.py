"""Canonical, deterministic JSON serialization shared by the V4 knowledge
contract/example reporters.

Every R7-R12 knowledge sub-package's `contract_report.py` independently
wrote the same one-line serialization call (`json.dumps(..., ensure_ascii=False,
sort_keys=True, separators=(",", ":"))`) after building its own round-specific
payload (see the V4.1-R0 maintainability inventory, DUP-001/DEBT-001). This
module extracts that single, purely mechanical serialization step so it is
written once; it has no knowledge of what a "contract" or "example" is, no
round-specific behavior, and no I/O.
"""
from __future__ import annotations

import json
from typing import Mapping


def render_deterministic_json(payload: Mapping[str, object]) -> str:
    """Serializes `payload` as canonical, deterministic JSON text.

    Keys are sorted and separators are fixed (no whitespace drift), so the
    same payload always serializes to the exact same bytes. Non-ASCII text
    is emitted as literal UTF-8 characters rather than `\\uXXXX` escapes.
    """
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
