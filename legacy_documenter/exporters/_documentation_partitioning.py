"""Deterministic, safe filename derivation for partitioned documentation (V4.2-R8).

`FUNCTIONAL_FLOWS.md`/`DATABASE_ACCESS.md`/`UNRESOLVED_FINDINGS.md` become
navigation/summary documents whose detail is partitioned into
`documentation/<doc>/<safe-name>.md` files, one per semantic group (e.g. a
project). Every partition filename produced here comes exclusively from
deterministic, trusted code over already-discovered model data -- never from
AI/provider content, a wall-clock timestamp, a UUID, or Python's randomized
`hash()`. See docs/V4_2/V4_2_R8 section 12.
"""
from __future__ import annotations

import re

_UNSAFE_CHARS_RE = re.compile(r"[^A-Za-z0-9_-]+")
_RESERVED_WINDOWS_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)
MAX_STEM_LENGTH = 80


def sanitize_label(label: object) -> str:
    """Derives a filesystem-safe stem from an arbitrary group label.

    Every character outside `[A-Za-z0-9_-]` (including `/`, `\\`, `..`, `:`,
    control characters, and whitespace) becomes `_`, which also makes path
    traversal structurally impossible: a sanitized stem can never contain a
    path separator or a `..` segment. Falls back to `"unassigned"` for an
    empty/`None` label, a label that sanitizes to nothing (e.g. all-symbol
    input), or a Windows-reserved device name; long labels are truncated to
    `MAX_STEM_LENGTH` characters (still deterministic -- a pure function of
    the input).
    """
    text = _UNSAFE_CHARS_RE.sub("_", str(label or "").strip())
    text = text.strip("_-")
    if not text:
        return "unassigned"
    text = text[:MAX_STEM_LENGTH].strip("_-") or "unassigned"
    if text.upper() in _RESERVED_WINDOWS_NAMES:
        text = f"_{text}"
    return text


def build_partition_filenames(group_keys: list[str]) -> dict[str, str]:
    """Maps each group key (already in the caller's final deterministic order)
    to a unique `<safe-name>.md` filename.

    Two different group keys that sanitize to the same stem (a genuine
    duplicate label, or a Windows case-insensitive collision such as `"Web"`
    vs `"web"`) are disambiguated with a stable, order-derived numeric
    suffix (`-2`, `-3`, ...) -- never a hash, timestamp, or UUID. Calling
    this twice with the same `group_keys` list always yields the same
    mapping.
    """
    used_lower: dict[str, int] = {}
    result: dict[str, str] = {}
    for key in group_keys:
        stem = sanitize_label(key)
        lower = stem.lower()
        seen = used_lower.get(lower, 0)
        used_lower[lower] = seen + 1
        result[key] = f"{stem}.md" if seen == 0 else f"{stem}-{seen + 1}.md"
    return result
