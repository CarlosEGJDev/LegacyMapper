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


def webform_owner_group_key(webform: object) -> str:
    """Derives the deterministic "owner" group key for a WebForm path (V4.3-R4
    correction). Shared by `legacy_documenter.documentation.human_documentation_scaling`
    (`flow_group_key`) and `legacy_documenter.exporters.technical_documentation_renderer`
    (`web_entry_points_navigation`/`web_entry_points_partitions`) so the same
    grouping rule is never reimplemented twice.

    Purely structural over `webform` itself -- never a name-based heuristic
    (no list of "DAL"/"BL"/"Infrastructure" project names to exclude), and
    never a substitute drawn from graph-traversal data (e.g. which layer a
    flow's resolved call chain happened to reach first): three deterministic
    tiers, in order:

    1. **Primary rule**: `webform` is a non-empty string containing a path
       separator (`\\` or `/`, checked after normalizing `\\` to `/` so both
       are handled identically regardless of platform) -> its first path
       segment, i.e. the folder that directly contains the `.ascx`/`.aspx`
       file -- the WebForm's real owning module/subsystem.
    2. **Fallback (tier 2)**: `webform` is non-empty but has no path
       separator (an edge case: a WebForm file recorded at the root, with no
       containing folder) -> its filename without extension. This is still
       direct evidence of the entry point itself, only at coarser
       granularity than tier 1 -- it exists so a rootless WebForm still gets
       a stable, non-`"unassigned"` group instead of being silently lumped
       together with every other rootless WebForm.
    3. **`"unassigned"` (tier 3, last resort)**: `webform` is `None`, absent,
       or an empty/whitespace-only string -- i.e. there genuinely is no
       WebForm evidence to group by. This is the only case that produces
       `"unassigned"`.
    """
    text = str(webform).strip() if webform else ""
    if not text:
        return "unassigned"
    normalized = text.replace("\\", "/")
    if "/" in normalized:
        first_segment = normalized.split("/", 1)[0]
        return first_segment or "unassigned"
    stem = normalized.rsplit(".", 1)[0] if "." in normalized else normalized
    return stem or "unassigned"


def owning_project_group_key(project_path: object, webform: object) -> str:
    """Derives the deterministic owner group key for a hydrated flow, preferring
    its resolved owning `.vbproj` project over the WebForm path's first folder
    segment (V4.3-R8 correction of external pilot finding P-01).

    `webform_owner_group_key`'s tier-1 rule (first path segment) collapses into
    a generic *container* folder -- not a functional/project unit -- for a
    deeply nested real repository layout such as
    `proyectos/WebApplication1/WebApplication1/WebWPF/...` or
    `proyectos/slnInformesSubsidios/Backup/WebInformesSubsidios/...`: both
    produce the key `"proyectos"`, which groups thousands of unrelated flows
    together (the exact real-pilot defect P-01 reports).

    `project_path` is the flow's hydrated `entry_point.project` (V4.3-R8
    addition to `EvidenceHydrator.hydrate_flow`): the `.vbproj` file path
    `WebEntryResolver` already resolves structurally, from the WebForm's
    code-behind symbol's unique compile-item match -- never a name-based
    heuristic and never inferred from the WebForm path itself. When present,
    this function groups by that project file's stem (e.g.
    `C:/repo/proyectos/.../WebInformesSubsidios.vbproj` -> `"WebInformesSubsidios"`),
    which is the real owning-project identity, regardless of how deeply the
    WebForm itself is nested under a shared container folder.

    Falls back to `webform_owner_group_key(webform)` whenever there is no
    resolved project evidence (`project_path` is `None`/empty/whitespace-only)
    -- exactly the same three-tier WebForm-path rule already in place, never
    weakened or replaced, only pre-empted by a stronger signal when one
    exists.
    """
    text = str(project_path).strip() if project_path else ""
    if text:
        normalized = text.replace("\\", "/").rstrip("/")
        stem = normalized.rsplit("/", 1)[-1]
        stem = stem.rsplit(".", 1)[0] if "." in stem else stem
        if stem:
            return stem
    return webform_owner_group_key(webform)


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
