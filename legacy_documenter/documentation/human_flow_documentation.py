"""Human-readable FLOW documentation in Spanish (V4.3-R3).

Implements the `HUMAN_DOCUMENTATION_PROJECTION 1.0` surface fixed by V4.3-R1
(`docs/V4_3/V4_3_R1_CONSUMABLE_PROJECTION_CONTRACT_RESULT.md`, section 5.1) for the
code-evidence origin: it renders a hydrated FLOW record, exactly as produced by
`legacy_documenter.context.hydration.EvidenceHydrator.hydrate_flow`, into a Spanish
Markdown document a human can read without opening `FUNCTIONAL_FLOWS.json` or any
other exhaustive index.

Structure and rules come directly from `prompts/V4_3/V4_3_R3_HUMAN_DOCUMENTATION.md`:
the seven required sections (what/where, entry event, what it does per evidence,
services/layers, data/SP/SQL, what remains unresolved, evidence/traceability), and
six rules (no mechanical JSON translation; technical IDs are never the main
explanation -- resolved names are; technical names stay intact; AI only ever
contributes content tagged `INTERPRETED`; useful deterministic documentation must
exist without any AI; limits are declared explicitly).

This module is a pure function of the hydrated record it receives. It never imports
`legacy_documenter.llm`, never calls a provider, never reads or writes a file, and is
not wired into `legacy_documenter.cli` -- exactly the same runtime-independence
posture as `legacy_documenter.context.hydration` (R2). An optional, clearly
separated `INTERPRETED` section can be attached by a caller that already has an AI
interpretation in hand; this module never produces one itself.

**V4.3-R8 correction (external pilot findings P-02/P-03,
`docs/V4_3/V4_3_R8_EXTERNAL_PILOT_CORRECTIONS_RESULT.md`)**: the real pilot found a
flow with 94 paths whose document led with an almost-complete listing of all 94 --
including dozens of low-human-value technical/infrastructure calls
(`DesplegarError`, `SetVisibleColumns`, `LimpiaNullDataset`, `dbc.BeginTrans`/
`Commit`/`Rollback`/`Close`, ...) -- before repeating uncertainties and then the full
`PATH`-by-`PATH` traceability again, making the document technically correct but not
consumable as a human summary. This module is now summary-first: section 3 is a
short deterministic summary, section 4 shows only confirmed, non-technical "main"
paths, and the exhaustive per-path listing (every path, including technical/
infrastructure ones, exactly as before) moves into the final detail section
(section 8), alongside traceability -- nothing is removed or truncated, only
reordered. Section 7 additionally separates a functionally relevant unresolved
boundary from one already recognized, by name, as known infrastructure (e.g. a
transaction-control or connection-lifecycle call) -- presentation-only, never a
change to confidence, `technical_noise_candidate`, or `terminal_type` on the
hydrated record itself, and never a promotion of an unresolved boundary to
confirmed.
"""

CONFIDENCE_LABELS_ES = {
    "confirmed": "confirmado",
    "inferred": "inferido",
    "unresolved": "no resuelto",
}

TERMINAL_TYPE_LABELS_ES = {
    "stored_procedure": "procedimiento almacenado",
    "sql": "operación SQL",
    "unresolved_boundary": "límite no resuelto",
}

#: Presentation-only (V4.3-R8, findings P-02/P-03): a broader, renderer-local
#: name list than `EvidenceHydrator.TECHNICAL_NOISE_METHOD_NAMES` (V4.3-R3,
#: deliberately left unmodified by this correction -- see the module
#: docstring). This governs *only* which already-hydrated paths/terminals
#: this renderer relegates to a secondary "técnico/infraestructura"
#: presentation -- it never changes confidence, `technical_noise_candidate`,
#: or `terminal_type` on the hydrated record, and it is applied only to an
#: already-resolved method-name string, never inferred from an id or a
#: narrative label.
PRESENTATION_TECHNICAL_METHOD_NAMES = frozenset({
    "InitializeComponent", "Dispose", "InitializeCulture",
    "BeginTrans", "BeginTransaction", "Commit", "Rollback", "Close", "Open",
    "DesplegarError", "Left", "values", "SetCheckBox", "SetVisibleColumns",
    "LimpiaNullDataset", "parametrosURL",
})

MODEL_VERSION = "V4.3-R3"
SCHEMA_NAME = "HUMAN_DOCUMENTATION_PROJECTION"
SCHEMA_VERSION = "1.0"


class InvalidInterpretationError(ValueError):
    """Raised when an attached AI interpretation violates the `INTERPRETED`-only rule.

    An interpretation item is invalid if it lacks `evidence_refs`, or if it declares
    any `status` other than `INTERPRETED` -- this module never lets attached AI
    content claim `CONFIRMED`/`UNRESOLVED`, both of which are reserved for
    deterministic evidence already present in the hydrated record.
    """


def render_flow_document(record: dict, interpretations: list[dict] | None = None) -> str:
    """Renders one hydrated FLOW record as a Spanish Markdown human document.

    `record` must be the dict returned by `EvidenceHydrator.hydrate_flow`. Every
    sentence of the deterministic sections below is derived exclusively from fields
    already present in `record`; nothing is invented. `interpretations`, if given, is
    a list of `{"statement": str, "evidence_refs": [str, ...]}` items -- each must
    reference only `evidence_refs` already present in `record`'s paths, is rendered
    in a clearly separated final section tagged `INTERPRETED`, and never edits or
    replaces any deterministic section above it.
    """
    entry = record.get("entry_point", {})
    lines = [
        f"# Flujo {record.get('flow_id')}: {_entry_title(entry)}",
        "",
        f"*Documento generado de forma determinista (sin IA), esquema `{SCHEMA_NAME} {SCHEMA_VERSION}`, "
        f"modelo `{MODEL_VERSION}`.*",
        "",
        *_section_1_what_and_where(record, entry),
        "",
        *_section_2_entry_event(entry),
        "",
        *_section_3_functional_summary(record),
        "",
        *_section_4_confirmed_main_paths(record),
        "",
        *_section_5_services_and_layers(record),
        "",
        *_section_6_data_sp_sql(record),
        "",
        *_section_7_unresolved(record),
        "",
        *_section_8_detail_and_traceability(record),
        "",
        *_section_limits(record),
    ]
    if interpretations:
        lines += ["", *_section_interpreted(record, interpretations)]
    return "\n".join(lines) + "\n"


def _entry_title(entry: dict) -> str:
    """Renders the document's title line from the hydrated entry point, declaring any gap explicitly."""
    webform = entry.get("webform") or "(formulario web no determinado)"
    event = entry.get("event") or "(evento no determinado)"
    return f"{webform} → {event}"


def _section_1_what_and_where(record: dict, entry: dict) -> list[str]:
    """Section 1 (`qué es / dónde está`): webform, involved projects/layers, overall flow confidence."""
    projects = ", ".join(record.get("projects", [])) or "no determinado"
    return [
        "## 1. Qué es y dónde está",
        "",
        f"- Formulario web: `{entry.get('webform') or 'no determinado'}`",
        f"- Proyectos/capas del sistema involucrados: {projects}",
        f"- Confianza general del flujo: {_confidence_es(record.get('confidence'))}",
    ]


def _section_2_entry_event(entry: dict) -> list[str]:
    """Section 2 (`evento/entrada inicial`): the event, handler and start method that begin the flow."""
    event = entry.get("event") or "no determinado"
    handler = entry.get("handler") or "no determinado"
    start_method = entry.get("start_method")
    lines = [
        "## 2. Evento/entrada inicial",
        "",
        f"El flujo se inicia con el evento `{event}`, manejado por `{handler}`.",
    ]
    if start_method and start_method != handler:
        lines.append(f"El método de inicio identificado es `{start_method}`.")
    if not entry.get("event") and not entry.get("handler"):
        lines.append("El evento/manejador de entrada no pudo determinarse a partir de la evidencia disponible.")
    return lines


def _presentation_method_name(name: str | None) -> str | None:
    """Extracts the bare method name from a resolved caller/terminal name
    (e.g. `"CobDAO.BeginTrans"` -> `"BeginTrans"`) for presentation-only
    technical/infrastructure classification (V4.3-R8). Returns `None` when
    there is nothing to classify."""
    if not name:
        return None
    method = name.rsplit(".", 1)[-1]
    return method[:-2] if method.endswith("()") else method


def _is_presentation_technical_name(name: str | None) -> bool:
    """`True` when `name`'s bare method matches `PRESENTATION_TECHNICAL_METHOD_NAMES`
    -- a presentation-only signal (V4.3-R8, findings P-02/P-03), never a change
    to the hydrated record's own `technical_noise_candidate`/confidence."""
    return _presentation_method_name(name) in PRESENTATION_TECHNICAL_METHOD_NAMES


def _path_is_presentation_technical(path: dict) -> bool:
    """`True` when `path` is already flagged `technical_noise_candidate`
    (V4.3-R3, `EvidenceHydrator`) or when any of its nodes/terminal resolve to
    a presentation-only technical/infrastructure name (V4.3-R8). Used only to
    decide *where* an already-hydrated path is shown, never whether it is
    shown -- see the module docstring."""
    if path.get("technical_noise_candidate"):
        return True
    if any(
        n.get("type") == "data_access" and _is_presentation_technical_name(n.get("caller"))
        for n in path.get("nodes", [])
    ):
        return True
    terminal = path.get("terminal") or {}
    return _is_presentation_technical_name(terminal.get("resolved_name"))


def _path_is_confirmed_main(path: dict) -> bool:
    """`True` when `path` belongs in section 4 (`rutas confirmadas principales`,
    V4.3-R8): `confirmed` confidence, a resolved terminal (stored procedure or
    SQL operation -- never `unresolved_boundary`), and not classified
    technical/infrastructure by `_path_is_presentation_technical`."""
    return (
        path.get("confidence") == "confirmed"
        and path.get("terminal_type") in ("stored_procedure", "sql")
        and not _path_is_presentation_technical(path)
    )


def _section_3_functional_summary(record: dict) -> list[str]:
    """Section 3 (`resumen funcional determinista`, V4.3-R8 correction of finding
    P-02): a short, deterministic count-based summary shown *before* any path
    detail, so a reader gets the shape of the flow without scrolling through an
    exhaustive listing first. Never invents a narrative -- every number is a
    direct count over already-hydrated `record["paths"]`; the exhaustive
    per-path listing itself (including technical/infrastructure paths) is
    deferred to section 8, never duplicated here.
    """
    paths = record.get("paths", [])
    lines = ["## 3. Resumen funcional determinista", ""]
    if not paths:
        lines.append("No se encontraron caminos de ejecución evidenciados para este flujo.")
        return lines
    main = len([p for p in paths if _path_is_confirmed_main(p)])
    technical = len([p for p in paths if _path_is_presentation_technical(p)])
    unresolved = len([p for p in paths if p.get("terminal_type") == "unresolved_boundary"])
    lines += [
        f"- {len(paths)} camino(s) de ejecución evidenciado(s) en total.",
        f"- {main} camino(s) confirmado(s) principal(es) (detalle en la sección 4).",
        f"- {unresolved} camino(s) con un límite no resuelto (detalle en la sección 7).",
        f"- {technical} camino(s) adicional(es) corresponden a infraestructura o código técnico/generado, "
        "no a lógica de negocio.",
        "",
        "El detalle exhaustivo de todos los caminos -- incluyendo los técnicos/de infraestructura -- está "
        "en la sección 8; esta sección resume solo lo funcionalmente relevante.",
    ]
    return lines


def _section_4_confirmed_main_paths(record: dict) -> list[str]:
    """Section 4 (`rutas confirmadas principales`, V4.3-R8 correction of finding
    P-02): only `confirmed`, non-technical/infrastructure paths
    (`_path_is_confirmed_main`), described the same way section 3 used to
    describe every path (`_describe_path`) -- the summary-first main view a
    human reads first. Every path is still shown somewhere: none excluded
    here is dropped, only deferred to the exhaustive section 8.
    """
    lines = ["## 4. Rutas confirmadas principales", ""]
    main_paths = [p for p in record.get("paths", []) if _path_is_confirmed_main(p)]
    if not main_paths:
        lines.append(
            "No hay caminos confirmados principales distintos de los técnicos/de infraestructura para este "
            "flujo (ver el detalle exhaustivo en la sección 8)."
        )
        return lines
    for path in main_paths:
        lines.append(f"- {_describe_path(path)}")
    return lines


def _describe_path(path: dict) -> str:
    """Renders one hydrated path group as a single prose sentence: confidence, chain, resolved terminal."""
    confidence = _confidence_es(path.get("confidence"))
    chain = " → ".join(_describe_node(n) for n in path.get("nodes", [])) or "(sin pasos intermedios evidenciados)"
    terminal = _describe_terminal(path.get("terminal_type"), path.get("terminal"))
    noise = " *(coincide con un patrón de código técnico/generado, no confirmado como lógica de negocio)*" if path.get("technical_noise_candidate") else ""
    return f"Camino {confidence}: {chain} termina en {terminal}.{noise}"


def _describe_node(node: dict) -> str:
    """Renders one hydrated path node by its resolved name, never its bare id, when a name exists."""
    if node.get("type") == "data_access":
        return f"`{node.get('caller')}`{_evidence_suffix(node)}"
    if node.get("type") in ("stored_procedure", "sql_operation") and node.get("resolved_name"):
        return f"`{node.get('resolved_name')}`"
    return f"`{node.get('id')}` (no resuelto)"


def _describe_terminal(terminal_type: str | None, terminal: dict | None) -> str:
    """Renders a resolved terminal by its Spanish type label and resolved name, or declares it unresolved."""
    terminal = terminal or {}
    label = TERMINAL_TYPE_LABELS_ES.get(terminal_type, terminal_type or "destino no determinado")
    resolved_name = terminal.get("resolved_name")
    if resolved_name:
        return f"{label} `{resolved_name}`{_evidence_suffix(terminal)}"
    return f"{label} sin nombre resuelto (`{terminal.get('id')}`)"


def _evidence_suffix(item: dict) -> str:
    """Appends transaction/data-operation evidence (V4.3-R3) to a node/terminal description, if present.

    Both fields come straight from the hydrated record (`transaction_evidence`,
    `data_operation_kind`) -- this never inspects `resolved_name`/`caller` to guess
    a nature the index did not already confirm (R0 acceptance case C).
    """
    parts = []
    transaction_evidence = item.get("transaction_evidence")
    if transaction_evidence is not None:
        verb = transaction_evidence.get("verb")
        parts.append(f"evidencia transaccional confirmada (`{verb}`)" if verb else "evidencia transaccional confirmada (verbo no determinado)")
    data_operation_kind = item.get("data_operation_kind")
    if data_operation_kind:
        parts.append(f"operación de datos confirmada: `{data_operation_kind}`")
    return f" ({'; '.join(parts)})" if parts else ""


def _section_5_services_and_layers(record: dict) -> list[str]:
    """Section 5 (`servicios/capas`): distinct data-access callers, business callers separated from
    technical/auxiliary noise (V4.3-R3 correction, human review of the generated samples).

    A caller is treated as noise, never mixed into the main business list, when either:

    - it is flagged `technical_noise_candidate` on any of its reached nodes (the
      deterministic, name-based flag `EvidenceHydrator` already computes -- never
      re-derived here), or
    - its bare method name matches `PRESENTATION_TECHNICAL_METHOD_NAMES` (V4.3-R8
      correction of external pilot finding P-03 follow-up: `EvidenceHydrator`'s own
      `TECHNICAL_NOISE_METHOD_NAMES` is deliberately narrow/conservative and stays
      unmodified, but this renderer's broader presentation-only list -- already used
      by sections 3/4/7 -- must classify a caller the same way everywhere in this
      document, not only in the sections added by V4.3-R8).

    Either way, it is preserved, visible, and traceable, but in its own separate
    subsection, so a reader never mistakes `InitializeComponent`/`DesplegarError`/
    etc. for a business service.
    """
    lines = ["## 5. Servicios/capas", ""]
    noise_by_caller: dict[str, bool] = {}
    for p in record.get("paths", []):
        for n in p.get("nodes", []):
            if n.get("type") == "data_access" and n.get("caller"):
                is_noise = bool(n.get("technical_noise_candidate")) or _is_presentation_technical_name(n.get("caller"))
                noise_by_caller[n["caller"]] = noise_by_caller.get(n["caller"], False) or is_noise
    if not noise_by_caller:
        lines.append("No se identificaron servicios/clases de acceso a datos en la cadena de este flujo.")
        return lines
    business_callers = sorted(c for c, noise in noise_by_caller.items() if not noise)
    noise_callers = sorted(c for c, noise in noise_by_caller.items() if noise)
    if business_callers:
        for caller in business_callers:
            lines.append(f"- `{caller}`")
    else:
        lines.append("No se identificaron servicios/clases de negocio en la cadena de este flujo, aparte de los elementos técnicos/auxiliares listados abajo.")
    if noise_callers:
        lines.append("")
        lines.append("### Elementos técnicos/auxiliares (no lógica de negocio)")
        lines.append("")
        lines.append("*Coinciden con un patrón de código técnico/generado (p. ej. métodos del diseñador de "
                      "WebForms). Se conservan como evidencia, con su confianza y trazabilidad intactas; no "
                      "deben interpretarse como servicios de negocio.*")
        lines.append("")
        for caller in noise_callers:
            lines.append(f"- `{caller}`")
    return lines


def _section_6_data_sp_sql(record: dict) -> list[str]:
    """Section 6 (`datos/SP/SQL`): resolved stored procedures, SQL operations, and reached parameters."""
    lines = ["## 6. Datos/SP/SQL", ""]
    terminals = record.get("terminals", {})
    stored = terminals.get("stored_procedures", [])
    sql = terminals.get("sql_operations", [])
    if stored:
        lines.append("### Procedimientos almacenados")
        for sp in stored:
            package_procedure = f" (paquete `{sp['package']}`, procedimiento `{sp['procedure']}`)" if sp.get("package") or sp.get("procedure") else ""
            lines.append(f"- `{sp.get('resolved_name') or sp.get('id')}`{package_procedure}")
        lines.append("")
    if sql:
        lines.append("### Operaciones SQL")
        for s in sql:
            lines.append(f"- `{s.get('resolved_name') or s.get('id')}`")
        lines.append("")
    if not stored and not sql:
        lines.append("No se confirmó acceso a procedimientos almacenados ni operaciones SQL para este flujo.")
        lines.append("")
    lines += _data_operations_and_transactions(record)
    parameters = record.get("parameters", [])
    if parameters:
        lines.append("### Parámetros disponibles por invocador alcanzado")
        for p in parameters:
            names = ", ".join(f"`{n}`" for n in p.get("names", []))
            lines.append(f"- `{p.get('caller')}`: {names}")
    return lines


def _data_operations_and_transactions(record: dict) -> list[str]:
    """Renders confirmed transaction/data-operation evidence (V4.3-R3, R0 acceptance case C).

    Both lists (`record["transactions"]`, `record["data_operations"]`) come from
    `EvidenceHydrator` and only ever contain entries backed by a literal, already-
    recorded index field (`operation_kind == "transaction"` + a matched evidence
    keyword; `sql_operation`) -- never a stored procedure resolved by name alone.
    """
    lines: list[str] = []
    transactions = record.get("transactions", [])
    if transactions:
        lines.append("### Evidencia transaccional")
        for tx in transactions:
            verb = f"`{tx['verb']}`" if tx.get("verb") else "verbo no determinado"
            lines.append(f"- `{tx['id']}`: evidencia transaccional confirmada ({verb})")
        lines.append("")
    data_operations = record.get("data_operations", [])
    if data_operations:
        lines.append("### Operaciones de datos confirmadas")
        for op in data_operations:
            lines.append(f"- `{op['id']}`: operación de datos confirmada `{op['operation']}`")
        lines.append("")
    return lines


def _describe_boundary(b: dict, node_caller: str | None = None) -> str:
    """Renders one unresolved-boundary terminal by its resolved name when the
    hydrator found one (e.g. a DAO call that itself resolved, even though the
    path's own terminal type is `unresolved_boundary`), falling back to its
    bare id otherwise -- never inventing a name that was not already resolved.

    `node_caller`, if given (V4.3-R8 follow-up correction of finding P-03), is
    the presentation-technical caller name found on the reaching path's own
    nodes when the terminal itself is opaque (`resolved_name` is `None`) --
    appended only as a transparency annotation explaining *why* this boundary
    was classified as infrastructure; it never replaces or edits the
    terminal's own id.
    """
    name = b.get("resolved_name")
    base = f"`{name}` (`{b.get('id')}`)" if name else f"`{b.get('id')}`"
    if not name and node_caller:
        return f"{base} (ruido técnico detectado en el camino vía `{node_caller}`)"
    return base


def _path_presentation_technical_node_caller(path: dict) -> str | None:
    """Returns the first presentation-technical data-access caller name found
    among `path`'s own nodes (V4.3-R8 follow-up correction of finding P-03),
    or `None` when none match. Evidence already present on the hydrated path
    -- never inferred from the terminal's id/name itself."""
    for n in path.get("nodes", []):
        if n.get("type") == "data_access" and _is_presentation_technical_name(n.get("caller")):
            return n.get("caller")
    return None


def _unresolved_boundary_node_callers(record: dict) -> dict[object, str]:
    """Maps an unresolved-boundary terminal id to the presentation-technical
    caller name found on a path reaching it (V4.3-R8 follow-up correction of
    finding P-03): an opaque terminal (no `resolved_name`, e.g.
    `DesplegarError`/`LimpiaNullDataset` called on a form that itself doesn't
    resolve to a further terminal) can still be recognized as infrastructure
    when the path reaching it unambiguously contains a known technical/
    infrastructure call among its own nodes -- never guessed from the
    terminal id/name in isolation. A terminal whose own `resolved_name`
    already matches (e.g. `dbc.BeginTrans`) does not need this map; it is
    classified directly in `_section_7_unresolved`.
    """
    found: dict[object, str] = {}
    for path in record.get("paths", []):
        if path.get("terminal_type") != "unresolved_boundary":
            continue
        terminal_id = (path.get("terminal") or {}).get("id")
        if terminal_id is None or terminal_id in found:
            continue
        caller = _path_presentation_technical_node_caller(path)
        if caller:
            found[terminal_id] = caller
    return found


def _section_7_unresolved(record: dict) -> list[str]:
    """Section 7 (`qué queda no resuelto`): unresolved boundaries and uncertain paths, never hidden.

    **V4.3-R8 correction (finding P-03)**: a boundary already recognized, by its
    resolved name, as a known infrastructure/lifecycle call (e.g. `dbc.BeginTrans`/
    `Commit`/`Rollback`/`Close` -- `_is_presentation_technical_name`) is
    presentation-only relegated to a secondary subsection instead of the main
    list, so a reader never confuses a known transaction/connection-lifecycle
    boundary with a functionally relevant gap in the analysis.

    **V4.3-R8 follow-up correction (human review of the R8 samples)**: the same
    classification must not depend solely on the terminal's own `resolved_name`
    when that terminal is opaque (`resolved_name is None`). A path reaching an
    opaque boundary can still unambiguously contain a recognized technical/
    infrastructure call among its own nodes (e.g. a path whose only node is
    `Formulario.DesplegarError`, ending in an unrelated opaque id) --
    `_unresolved_boundary_node_callers` surfaces that node-level evidence, so
    this boundary is relegated to the same infrastructure subsection, with its
    real terminal id and full traceability preserved, instead of being left in
    the main functional list purely because the terminal itself has no
    resolved name. This never changes `terminal_type`/confidence/
    `technical_noise_candidate`, and never promotes an unresolved boundary to
    confirmed -- both boundaries remain, in full, under "qué queda no
    resuelto"; only their subsection differs.
    """
    lines = ["## 7. Qué queda no resuelto", ""]
    unresolved = record.get("unresolved", [])
    boundaries = record.get("terminals", {}).get("unresolved_boundaries", [])
    if not unresolved and not boundaries:
        lines.append("No quedan caminos ni límites sin resolver para este flujo, según la evidencia disponible.")
        return lines
    node_callers = _unresolved_boundary_node_callers(record)

    def _is_infrastructure(b: dict) -> bool:
        return _is_presentation_technical_name(b.get("resolved_name")) or b.get("id") in node_callers

    functional = [b for b in boundaries if not _is_infrastructure(b)]
    infrastructure = [b for b in boundaries if _is_infrastructure(b)]
    if functional:
        for b in functional:
            lines.append(f"- Límite no resuelto: {_describe_boundary(b)} — no se pudo confirmar su destino real.")
    elif boundaries:
        lines.append(
            "No quedan límites no resueltos funcionalmente relevantes -- ver la subsección de "
            "infraestructura/técnico abajo."
        )
    if unresolved:
        lines.append("")
        lines.append(f"Caminos con incertidumbre (`path_id`): {', '.join(f'`{p}`' for p in unresolved)}.")
    lines.append("")
    lines.append("Ninguna de estas ausencias se completa con una suposición: se declaran explícitamente como no resueltas.")
    if infrastructure:
        lines.append("")
        lines.append("### Límites técnicos/infraestructura (no resueltos, de naturaleza conocida)")
        lines.append("")
        lines.append(
            "*Corresponden a llamadas de infraestructura/ciclo de vida (p. ej. control transaccional, cierre "
            "de conexión) reconocidas por su nombre, o a un límite cuyo propio camino contiene inequívocamente "
            "una llamada técnica/de infraestructura reconocida; se conservan como límite no resuelto, con su "
            "trazabilidad intacta, pero no representan una incertidumbre funcional del negocio.*"
        )
        lines.append("")
        for b in infrastructure:
            lines.append(f"- {_describe_boundary(b, node_caller=node_callers.get(b.get('id')))}")
    return lines


def _section_8_detail_and_traceability(record: dict) -> list[str]:
    """Section 8 (`evidencia técnica detallada / trazabilidad`, V4.3-R8 correction of
    finding P-02): the exhaustive per-path listing every path used to get up front
    in section 3 (V4.3-R3), plus `path_id`s, `evidence_refs`, and a complete origin
    pointer for every deduplicated `path_id` -- never only the first one (V4.3-R3
    correction, human review of the generated samples: a path group merging
    `PATH-A`/`PATH-B` must show both origins, not just A's).

    Nothing is removed relative to the pre-R8 sections 3+7 combined: every path
    (including technical/infrastructure ones already summarized/deferred in
    sections 3/4) is described here in full, exactly as `_describe_path` always
    rendered it, immediately followed by its own traceability -- this is the
    single exhaustive detail surface the summary sections above point to,
    never a second, separately-duplicated full listing.
    """
    lines = ["## 8. Evidencia técnica detallada / trazabilidad", ""]
    paths = record.get("paths", [])
    if not paths:
        lines.append("No se encontraron caminos de ejecución evidenciados para este flujo.")
        return lines
    lines.append("### Todos los caminos (detalle exhaustivo)")
    lines.append("")
    for path in paths:
        lines.append(f"- {_describe_path(path)}")
    lines.append("")
    lines.append("### Trazabilidad por camino")
    lines.append("")
    for path in record.get("paths", []):
        ids = ", ".join(f"`{pid}`" for pid in path.get("path_ids", []))
        refs = ", ".join(f"`{r}`" for r in path.get("evidence_refs", [])) or "(sin referencias de evidencia)"
        lines.append(f"- `PATH` {ids} — evidencia: {refs}")
        for entry in path.get("path_provenance", []):
            lines.append(f"  - `{entry.get('path_id')}` → `{entry.get('source_index_pointer')}`")
    provenance = record.get("provenance", {})
    lines.append("")
    lines.append(f"Puntero de origen del flujo: `{provenance.get('flow_source_index_pointer')}`")
    lines.append(f"Índices exhaustivos de origen: {', '.join(f'`{i}`' for i in provenance.get('source_indexes', []))}")
    return lines


def _section_limits(record: dict) -> list[str]:
    """Declares this document's limits: deterministic-only, IDs are not the explanation, noise is kept."""
    selection = record.get("selection", {})
    return [
        "## Límites de esta documentación",
        "",
        "- Generada exclusivamente a partir de evidencia determinista ya extraída por LegacyMapper; no se "
        "invoca ningún proveedor de IA para producir el contenido anterior.",
        "- Los identificadores técnicos (`FLOW-*`, `PATH-*`, `DAO-*`, `SP-*`, `SQL-*`) se conservan intactos "
        "como referencia de trazabilidad, pero no son la explicación principal: la explicación usa nombres "
        "resueltos cuando existen.",
        f"- De {selection.get('input_path_count', 0)} camino(s) determinista(s) original(es), "
        f"{selection.get('deduplicated_path_count', 0)} fueron cadenas equivalentes fusionadas (sin pérdida de "
        f"`path_id` ni evidencia); este documento describe los {selection.get('output_path_count', 0)} "
        "camino(s) resultantes.",
        "- Ningún elemento marcado como ruido técnico/generado (`technical_noise_candidate`) fue eliminado: "
        "permanece visible arriba, solo señalado para no confundirlo con lógica de negocio.",
        "- La evidencia transaccional y el tipo de operación de datos (sección 6) solo se muestran cuando el "
        "índice determinista ya los registró explícitamente; nunca se clasifica un procedimiento almacenado "
        "como 'escritura' a partir de su nombre.",
        "- Este documento no contiene interpretación de IA salvo que se indique explícitamente en una sección "
        "separada, etiquetada `INTERPRETED`, al final.",
    ]


def _section_interpreted(record: dict, interpretations: list[dict]) -> list[str]:
    """Renders the optional, separately-tagged `INTERPRETED` section; validates each item before rendering."""
    known_refs = {r for p in record.get("paths", []) for r in p.get("evidence_refs", [])}
    lines = [
        "## Interpretación de IA (`INTERPRETED`)",
        "",
        "*El contenido de esta sección es una interpretación de IA, no evidencia determinista. Nunca "
        "sustituye ni reescribe las secciones anteriores.*",
        "",
    ]
    for item in interpretations:
        status = item.get("status", "INTERPRETED")
        if status != "INTERPRETED":
            raise InvalidInterpretationError(f"status debe ser INTERPRETED, recibido: {status!r}")
        refs = item.get("evidence_refs") or []
        if not refs or any(r not in known_refs for r in refs):
            raise InvalidInterpretationError(f"evidence_refs inválidas o ausentes: {refs!r}")
        statement = item.get("statement", "")
        lines.append(f"- **[INTERPRETED]** {statement} — evidencia: {', '.join(f'`{r}`' for r in refs)}")
    return lines


def _confidence_es(confidence: str | None) -> str:
    """Translates a deterministic confidence label (`confirmed`/`inferred`/`unresolved`) to Spanish."""
    return CONFIDENCE_LABELS_ES.get(confidence, confidence or "no determinado")
