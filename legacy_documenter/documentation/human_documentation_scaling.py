"""System-scale, partitioned human documentation over many hydrated FLOWs (V4.3-R4).

`legacy_documenter.documentation.human_flow_documentation.render_flow_document`
(V4.3-R3) renders exactly one hydrated FLOW record. R3 explicitly left
system-scale aggregation for "many flows" out of scope (see
`docs/V4_3/V4_3_R3_HUMAN_DOCUMENTATION_RESULT.md` section 8): "no se genera
documentación humana para SYSTEM/TECHNICAL/otros niveles agregados ... (R4 ...
es el que aborda agregación/escalado a nivel de sistema completo)".

This module closes that gap without rewriting `render_flow_document`: it is a
thin aggregation layer that calls it once per hydrated FLOW record and
arranges the results into a top-level navigation/summary document plus one
partition document per semantic group -- the exact navigation/partition
pattern V4.2-R8 already validated for `FUNCTIONAL_FLOWS.md`/
`DATABASE_ACCESS.md`/`UNRESOLVED_FINDINGS.md`
(`legacy_documenter.exporters.technical_documentation_renderer`:
`functional_flows_navigation`/`functional_flows_partitions`,
`_flow_group_key`, `_group_by`), reused here rather than reinvented:

- **Grouping (corrected, V4.3-R4 post-implementation correction)**: the
  group key comes exclusively from the hydrated FLOW record's own entry
  point (`record["entry_point"]["webform"]`) -- **never** from
  `record["projects"]`/`project_sequence`. The first implementation of this
  module used `projects[0]` (mirroring `_flow_group_key`'s fallback over the
  raw flow dict's `project_sequence`), but `projects`/`project_sequence` is
  the *graph-traversal order* of the layers a flow's resolved call chain
  happened to reach (e.g. `DAL` when a WebForm's click handler calls
  straight into a data-access class) -- not a statement of which WebForm/
  module actually owns the flow. That produced a real defect: two WebForms
  that live in the same real folder (e.g. both under `webCobMorosidad\\`)
  landed in *different* groups (one under `DAL`, the other under
  `webCobMorosidad`) purely because their resolved call chains happened to
  reach different first layers, even though both are owned by the same
  WebForm folder. `flow_group_key` now delegates to
  `legacy_documenter.exporters._documentation_partitioning.webform_owner_group_key`,
  the shared three-tier rule (also reused by
  `technical_documentation_renderer.web_entry_points_navigation`/
  `_partitions` for the same purpose): the entry point WebForm's first path
  segment (its owning folder), falling back to its filename stem when the
  WebForm path has no folder, falling back to `"unassigned"` only when there
  is genuinely no WebForm evidence at all. See `flow_group_key`'s own
  docstring for the exact tiers.
- **Filenames**: `legacy_documenter.exporters._documentation_partitioning`
  (`sanitize_label`/`build_partition_filenames`), unmodified, so partition
  filenames are deterministic, collision-safe, and traversal-safe by the same
  mechanism the existing partitioned documents already rely on.
- **Grouping, corrected again (V4.3-R8, external pilot finding P-01)**:
  `webform_owner_group_key`'s first-path-segment rule still collapses into a
  generic *container* folder -- not a functional/project unit -- for a
  deeply nested real repository (e.g. `proyectos/WebApplication1/
  WebApplication1/WebWPF/...` and `proyectos/slnInformesSubsidios/Backup/
  WebInformesSubsidios/...` both produced the key `"proyectos"` on the real
  pilot, merging thousands of unrelated flows). `flow_group_key` now
  delegates to `owning_project_group_key`, which prefers the flow's
  resolved owning `.vbproj` project (`entry_point.project`, a V4.3-R8
  hydration addition, itself resolved structurally by `WebEntryResolver` --
  never a name-based heuristic) and falls back to the same
  `webform_owner_group_key` three-tier rule only when no project evidence
  exists. See `flow_group_key`'s own docstring for the exact rule.

**Size policy (two layers, the second added in V4.3-R8)**: like the three
existing partitioned documents, navigation + group partitions are produced
*unconditionally* for any non-empty list of hydrated flows -- there is no
flow-count threshold below which this module instead returns a single flat
document. This mirrors the existing, already-approved policy in
`legacy_documenter.cli.pipeline_stages._PARTITIONED_DOCUMENTATION_RENDERERS`
(V4.2-R8's own comment: partitioning replaced flat rendering outright once a
real repository showed flat documents were impractically large; the pipeline
never chooses between a flat and a partitioned form based on measured size at
run time). Documenting this as policy here, rather than inventing new
size-threshold branching, keeps this module's behavior as predictable as the
pattern it reuses -- a caller who only has one or two flows still gets a
(very short) navigation document plus a (very short) single partition; that
predictability is the trade-off explicitly preferred over conditional logic.
Within a group, however, the real pilot showed that a single owner/project
can itself hold thousands of flows (its "proyectos" group: 2983 flows, a
~45 MB/340k-line file) -- V4.3-R8 adds a second, size-controlled layer purely
to bound file size, never content: a group over `MAX_FLOWS_PER_GROUP_FILE`
flows has its detail split, in the same stable order, across
`<owner>-part-NNNNNN.md` sub-partition files, with `<owner>.md` becoming a
small sub-index rather than the full detail (see `render_human_documentation_partitions`).

This module is a pure function of the hydrated FLOW records it receives, and
of the optional `interpretations_by_flow` map, exactly passed through to
`render_flow_document` unchanged. It never imports `legacy_documenter.llm`,
never calls a provider, never reads or writes a file, and is not wired into
`legacy_documenter.cli`/`legacy_documenter.main` -- the same runtime-
independence posture already established by R2 (`context/hydration.py`) and
R3 (`documentation/human_flow_documentation.py`). It never mutates any
hydrated record it receives, and it never drops, renames, or reinterprets any
field the machine-readable hydrated projection (`AI_HYDRATED_PROJECTION 1.0`)
already carries -- it only arranges already-rendered per-flow documents into
groups.
"""
from legacy_documenter.exporters._documentation_partitioning import (
    build_partition_filenames,
    owning_project_group_key,
    sanitize_label,
)

from .human_flow_documentation import render_flow_document

MODEL_VERSION = "V4.3-R4"
SCHEMA_NAME = "HUMAN_DOCUMENTATION_PROJECTION"
SCHEMA_VERSION = "1.0"

#: The subdirectory name a caller that writes this to disk would use for
#: per-group partition files, mirroring `functional_flows/`/`database_access/`
#: (V4.2-R8). Exposed as a constant so the navigation document's relative
#: links and any future disk-writing caller agree on the same literal value
#: without duplicating it.
PARTITIONS_SUBDIR = "flujos_humanos"

#: The literal group key used for a hydrated flow whose entry point has no
#: usable WebForm evidence (`entry_point.webform` is `None`/absent/empty --
#: see `flow_group_key`/`webform_owner_group_key`'s tier 3). Identical
#: fallback value to `technical_documentation_renderer._flow_group_key`'s
#: `"unassigned"`, kept in English deliberately: it is an internal
#: grouping/filename key, not rendered prose (the navigation table
#: translates it for display, see `_group_display_label`).
UNASSIGNED_GROUP_KEY = "unassigned"


def flow_group_key(record: dict) -> str:
    """Derives the semantic group for one hydrated FLOW record, preferring its
    entry point's resolved owning `.vbproj` project (`record["entry_point"]
    ["project"]`, V4.3-R8 hydration addition) over its WebForm path
    (`record["entry_point"]["webform"]`) -- and **never** from
    `record["projects"]`/`project_sequence` (see the module docstring's
    "Grouping" section for why that substitution was a defect: `projects`
    reflects graph-traversal order, not ownership). Delegates to the shared
    `owning_project_group_key` (`legacy_documenter.exporters.
    _documentation_partitioning`, V4.3-R8 correction of external pilot
    finding P-01), which applies, in order:

    1. `entry_point.project` resolved to a real `.vbproj` -> that project
       file's stem -- the real owning-project identity, immune to how deeply
       the WebForm itself is nested under a shared container folder (e.g.
       `proyectos/WebApplication1/WebApplication1/WebWPF/...` groups by the
       project, never by the generic `"proyectos"` container).
    2. Otherwise, the same three-tier WebForm-path rule V4.3-R4 already
       established (`webform_owner_group_key`): first path segment, then
       filename stem for a rootless WebForm, then `UNASSIGNED_GROUP_KEY`
       (`"unassigned"`) only when there is genuinely no WebForm evidence
       either.

    Example: both `webCobMorosidad\\cobCargaArcIntRea.ascx` and
    `webCobMorosidad\\cobChqInsRen.ascx` produce the key `"webCobMorosidad"`
    regardless of which layer (`DAL`, `WEB`, ...) their `projects` list
    happens to list first, and a flow whose entry point resolved to
    `.../WebGestionRRHH.vbproj` groups under `"WebGestionRRHH"` even when its
    WebForm path is nested several container folders deep.
    """
    entry = record.get("entry_point") or {}
    return owning_project_group_key(entry.get("project"), entry.get("webform"))


def _group_by_webform_owner(hydrated_flows: list[dict]) -> dict[str, list[dict]]:
    """Groups hydrated FLOW records by `flow_group_key` -- the entry point's
    resolved owning `.vbproj` project when available (V4.3-R8), falling back
    to the WebForm's owning folder otherwise; the function's own name predates
    that V4.3-R8 correction and is kept unchanged here to avoid an unrelated
    rename (see `flow_group_key`'s docstring for the exact rule)."""
    grouped: dict[str, list[dict]] = {}
    for record in hydrated_flows:
        grouped.setdefault(flow_group_key(record), []).append(record)
    return grouped


def _group_display_label(key: str) -> str:
    """Spanish display label for a group key in the navigation table; the
    group *key* itself (used for grouping/filenames) is never translated.
    """
    return "Sin asignar" if key == UNASSIGNED_GROUP_KEY else key


def _has_confirmed_terminal(record: dict) -> bool:
    terminals = record.get("terminals", {})
    return bool(terminals.get("stored_procedures")) or bool(terminals.get("sql_operations"))


def _has_unresolved_boundary(record: dict) -> bool:
    return bool(record.get("terminals", {}).get("unresolved_boundaries"))


def _sort_key(record: dict) -> tuple:
    entry = record.get("entry_point", {})
    return (entry.get("webform") or "", entry.get("handler") or "", record.get("flow_id") or "")


def render_human_documentation_index(hydrated_flows: list[dict]) -> str:
    """Renders the top-level navigation/summary document (Spanish) over every
    hydrated FLOW record given: one row per semantic group (the resolved
    owning `.vbproj` project, or the WebForm-owning folder/module when there
    is no project evidence -- see `flow_group_key`), with
    flow/confirmed-terminal/unresolved-boundary counts and a relative link
    into that group's partition file. Full per-flow detail (the seven
    `render_flow_document` sections) lives only in the partitions this
    document links to -- never duplicated here (résumé-antes-que-detalle,
    V4.3-R1 section 5.1).

    Deterministic and order-independent in its input: two calls with the
    same flows in a different list order produce byte-identical output,
    because both the group table and each group's flow ordering are sorted
    internally, never taken from input order.
    """
    lines = [
        "# Documentación humana de flujos — Índice",
        "",
        f"*Documento generado de forma determinista (sin IA), esquema `{SCHEMA_NAME} {SCHEMA_VERSION}`, "
        f"modelo `{MODEL_VERSION}`.*",
        "",
    ]
    if not hydrated_flows:
        lines.append("No se hidrataron flujos para este sistema.")
        lines.append("")
        return "\n".join(lines) + "\n"

    groups = _group_by_webform_owner(hydrated_flows)
    filenames = build_partition_filenames(sorted(groups))
    total = len(hydrated_flows)
    total_confirmed = len([r for r in hydrated_flows if _has_confirmed_terminal(r)])
    total_unresolved = len([r for r in hydrated_flows if _has_unresolved_boundary(r)])

    lines.append(
        f"{total} flujo(s) hidratado(s), agrupados en {len(groups)} grupo(s) por proyecto propietario "
        "(`.vbproj` resuelto estructuralmente) o, cuando no hay evidencia de proyecto, por la carpeta "
        "propietaria del WebForm."
    )
    lines.append(
        f"Con terminal confirmado: {total_confirmed}. Con límite no resuelto: {total_unresolved} "
        "(ambos hechos pueden coexistir en el mismo flujo, ver cada documento de detalle)."
    )
    lines.append("")
    lines.append(
        "El detalle completo de cada flujo (evento de entrada, caminos, servicios/capas, datos/SP/SQL, "
        "lo no resuelto, evidencia/trazabilidad) está particionado por grupo abajo, nunca en este índice."
    )
    lines.append("")
    lines.append("## Grupos de flujos")
    lines.append("")
    lines.append("| Grupo | Flujos | Con terminal confirmado | Con límite no resuelto | Detalle |")
    lines.append("|---|---|---|---|---|")
    for key in sorted(groups):
        group_flows = groups[key]
        confirmed_n = len([r for r in group_flows if _has_confirmed_terminal(r)])
        unresolved_n = len([r for r in group_flows if _has_unresolved_boundary(r)])
        filename = filenames[key]
        link = f"{PARTITIONS_SUBDIR}/{filename}"
        lines.append(
            f"| {_group_display_label(key)} | {len(group_flows)} | {confirmed_n} | {unresolved_n} "
            f"| [{filename}]({link}) |"
        )
    lines.append("")
    lines.append(
        "*Política de tamaño: este índice y sus particiones se generan de forma incondicional para "
        "cualquier conjunto no vacío de flujos hidratados -- no existe un umbral de cantidad de flujos "
        "por debajo del cual se produzca en su lugar un único documento plano; misma política ya vigente "
        "para `FUNCTIONAL_FLOWS.md`/`DATABASE_ACCESS.md`/`UNRESOLVED_FINDINGS.md` desde V4.2-R8.*"
    )
    lines.append("")
    return "\n".join(lines) + "\n"


#: Second-layer, deterministic sub-partitioning threshold (V4.3-R8 correction
#: of external pilot finding P-01). A single owner/project group can itself
#: hold thousands of flows on a real repository (the real pilot's own
#: "proyectos" group held 2983 flows and produced a ~45 MB/340k-line file even
#: after owner grouping); this bounds *file size*, never *content*, the same
#: policy `context.consumer_projection.DEFAULT_PARTITION_SIZE` already applies
#: to `consumer_projection`'s JSON partitions -- chosen independently here
#: (a different surface, Markdown not JSON) but the same value for
#: consistency. A group at or under this size still renders as a single
#: `<owner>.md` file, unchanged from V4.3-R4/R7; a group over this size
#: renders `<owner>.md` as a small sub-index instead, with its flows split
#: across `<owner>-part-NNNNNN.md` files -- ordinal, size-controlled slices
#: of the same stable per-group flow order, never a narrative sub-grouping.
MAX_FLOWS_PER_GROUP_FILE = 500

_SUB_PARTITION_FILENAME_TEMPLATE = "{stem}-part-{index:06d}.md"


def _sub_partition_filename(stem: str, index: int) -> str:
    """The deterministic filename for sub-partition `index` (0-based) of an
    owner/project group whose stem is `stem` (already sanitized/deduplicated
    by `build_partition_filenames`)."""
    return _SUB_PARTITION_FILENAME_TEMPLATE.format(stem=stem, index=index + 1)


def render_human_documentation_partitions(
    hydrated_flows: list[dict], interpretations_by_flow: dict[str, list[dict]] | None = None
) -> dict[str, str]:
    """Renders one `<safe-name>.md` document per semantic group (the owning
    project/WebForm folder, see `flow_group_key`), each containing the full
    `render_flow_document` output for every hydrated flow in that group,
    concatenated in a stable order. Returns `{}` for an empty
    `hydrated_flows` list -- never an empty-but-present partition.

    **Second-layer sub-partitioning (V4.3-R8 correction of finding P-01).**
    A group with more than `MAX_FLOWS_PER_GROUP_FILE` flows never produces one
    unbounded file: its `<owner>.md` entry instead becomes a small navigation
    sub-index -- flow count, sub-partition count, and one link per
    `<owner>-part-NNNNNN.md` file -- and the full per-flow detail moves into
    those numbered sub-partition files, each holding at most
    `MAX_FLOWS_PER_GROUP_FILE` flows in the same stable, sorted order a
    single-file group already used. A group at or under the threshold is
    completely unaffected: its `<owner>.md` entry still holds the full detail
    directly, exactly as V4.3-R4/R7 left it.

    `interpretations_by_flow`, if given, maps a `flow_id` to the
    `interpretations` list `render_flow_document` already accepts; a flow
    absent from the map (or the map itself being `None`) simply renders
    without an `INTERPRETED` section, exactly like calling
    `render_flow_document(record)` directly -- this function never invents
    or requires AI content.

    Every flow given is preserved: the total record count across every
    returned *content* partition (a single-file group's own file, or a large
    group's sub-partition files -- never its sub-index, which holds no flow
    detail) always equals `len(hydrated_flows)`, and no `flow_id` is
    duplicated across two partitions (each flow belongs to exactly one group,
    by `flow_group_key`, and within that group to exactly one sub-partition).
    """
    if not hydrated_flows:
        return {}
    interpretations_by_flow = interpretations_by_flow or {}
    groups = _group_by_webform_owner(hydrated_flows)
    filenames = build_partition_filenames(sorted(groups))

    result: dict[str, str] = {}
    for key, group_flows in groups.items():
        sorted_flows = sorted(group_flows, key=_sort_key)
        filename = filenames[key]
        label = _group_display_label(key)
        if len(sorted_flows) <= MAX_FLOWS_PER_GROUP_FILE:
            result[filename] = _render_group_document(label, sorted_flows, interpretations_by_flow)
            continue
        stem = filename[: -len(".md")]
        chunks = [
            sorted_flows[i : i + MAX_FLOWS_PER_GROUP_FILE]
            for i in range(0, len(sorted_flows), MAX_FLOWS_PER_GROUP_FILE)
        ]
        part_filenames = [_sub_partition_filename(stem, index) for index in range(len(chunks))]
        result[filename] = _render_group_sub_index(label, sorted_flows, part_filenames)
        for part_filename, chunk in zip(part_filenames, chunks):
            result[part_filename] = _render_group_document(label, chunk, interpretations_by_flow)
    return result


def _render_group_document(
    label: str, group_flows: list[dict], interpretations_by_flow: dict[str, list[dict]]
) -> str:
    """Renders the full per-flow detail (`render_flow_document`, concatenated)
    for one group or one sub-partition of a group; `group_flows` must already
    be in the stable sort order the caller wants preserved."""
    lines = [
        f"# Documentación humana de flujos — {label}",
        "",
        f"*Esquema `{SCHEMA_NAME} {SCHEMA_VERSION}`, modelo `{MODEL_VERSION}`. "
        "[Volver al índice](../HUMAN_DOCUMENTATION.md).*",
        "",
        f"{len(group_flows)} flujo(s) en este documento.",
        "",
    ]
    for record in group_flows:
        interpretations = interpretations_by_flow.get(record.get("flow_id"))
        lines.append(render_flow_document(record, interpretations=interpretations))
        lines.append("---")
        lines.append("")
    if lines and lines[-2] == "---":
        lines.pop()  # drop the trailing separator after the last flow
        lines.pop()
    return "\n".join(lines) + "\n"


def _render_group_sub_index(label: str, group_flows: list[dict], part_filenames: list[str]) -> str:
    """Renders the small navigation sub-index that replaces a large group's
    `<owner>.md` full-detail file (V4.3-R8 correction of finding P-01): no
    per-flow detail here, only counts and links into `part_filenames` -- the
    same résumé-antes-que-detalle policy the top-level index already applies
    (V4.3-R1 section 5.1), one level deeper.
    """
    chunks = [
        group_flows[i : i + MAX_FLOWS_PER_GROUP_FILE] for i in range(0, len(group_flows), MAX_FLOWS_PER_GROUP_FILE)
    ]
    lines = [
        f"# Documentación humana de flujos — {label}",
        "",
        f"*Esquema `{SCHEMA_NAME} {SCHEMA_VERSION}`, modelo `{MODEL_VERSION}`. "
        "[Volver al índice](../HUMAN_DOCUMENTATION.md).*",
        "",
        f"Este grupo tiene {len(group_flows)} flujo(s), por encima del límite de "
        f"{MAX_FLOWS_PER_GROUP_FILE} flujo(s) por archivo -- el detalle completo está particionado "
        f"en {len(chunks)} archivo(s) abajo, nunca truncado ni omitido.",
        "",
        "## Particiones",
        "",
        "| Parte | Flujos | Detalle |",
        "|---|---|---|",
    ]
    for index, (chunk, part_filename) in enumerate(zip(chunks, part_filenames), start=1):
        lines.append(f"| {index} | {len(chunk)} | [{part_filename}]({part_filename}) |")
    lines.append("")
    return "\n".join(lines) + "\n"
