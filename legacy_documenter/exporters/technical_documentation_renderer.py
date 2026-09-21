"""Deterministic Markdown renderers over already-produced in-memory analysis data.

Covers the technical views V4.2-R0 identified as missing from `MarkdownExporter`'s
existing six documents: web entry points, functional flows, database access, and
a consolidated unresolved-findings view. Every renderer here is a pure function
of the `indexes` dict `analyze_repository`/`full` already assembles -- no file is
re-read from disk, no LLM/provider is called, and nothing here infers a
relationship, business meaning, or schema fact that the deterministic analyzers
did not themselves discover (see docs/V4_2/V4_2_R3_DETERMINISTIC_TECHNICAL_DOCUMENTATION_RESULT.md).

V4.2-R8 adds a navigation/detail split for `FUNCTIONAL_FLOWS.md`/
`DATABASE_ACCESS.md`/`UNRESOLVED_FINDINGS.md` (R7 found these unusably large
as single flat documents at real-repository scale -- see
docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md FINDINGS NOISE_OR_SCALE_ISSUES):
`*_navigation()` renders the small top-level summary/index document (the one
still written at the historical fixed filename, per R8 section 10's backward-
compatibility requirement), and `*_partitions()` renders the same evidence
`*()` already rendered, split by a stable semantic group (project, or
category), for `documentation/<doc>/<safe-name>.md`. The original flat
`*()` methods are unchanged and still available (used directly by
tests/test_v4_2_r3_deterministic_technical_documentation.py and by callers
that want one complete document); both code paths share the same per-item
rendering helpers below so the partitioned and flat renderings can never
drift apart.

V4.3-R4 (a narrowly-scoped post-implementation correction to that round's own
result, see docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md section 12)
extends this same navigation/detail split to `WEB_ENTRY_POINTS.md`:
`web_entry_points_navigation()`/`web_entry_points_partitions()`, grouped by
each entry point's WebForm-owning folder (`_web_entry_point_group_key`,
delegating to the shared
`legacy_documenter.exporters._documentation_partitioning.webform_owner_group_key`).
`PROJECT_DEPENDENCIES.md` was reopened at the same time, but it lives in
`legacy_documenter.exporters.markdown_exporter.MarkdownExporter` instead
(a different class/write path); `WEBFORMS_MAP.md` was evaluated and
deliberately left unpartitioned (see that result's section 12 for the
evidence and reasoning behind each of these three decisions). The flat
`web_entry_points()` method is unchanged and still available, same as the
other three documents.
"""
from __future__ import annotations

from legacy_documenter.exporters._documentation_partitioning import (
    build_partition_filenames,
    webform_owner_group_key,
)
from legacy_documenter.exporters.markdown_exporter import _repository_display_label


class TechnicalDocumentationRenderer:
    """Renders WEB_ENTRY_POINTS.md, FUNCTIONAL_FLOWS.md, DATABASE_ACCESS.md and
    UNRESOLVED_FINDINGS.md from `indexes`. Each method is side-effect free; writing
    to disk is the caller's responsibility (see `legacy_documenter.cli.pipeline_stages.render_documentation`),
    so one document's write failure never prevents another's content from being computed.
    """

    def web_entry_points(self, indexes: dict) -> str:
        """Renders WEB_ENTRY_POINTS.md from `entry_points`/`event_bindings`/`webforms`."""
        entry_points = indexes.get("entry_points", [])
        event_bindings = indexes.get("event_bindings", [])
        confirmed = [e for e in entry_points if e.get("confidence") == "confirmed"]
        unresolved = [e for e in entry_points if e.get("confidence") != "confirmed"]

        lines = ["# Web Entry Points", ""]
        lines.append(
            f"Discovered {len(entry_points)} entry point(s) across "
            f"{len({e.get('webform') for e in entry_points})} WebForm(s) "
            f"({len(confirmed)} confirmed, {len(unresolved)} unresolved), "
            f"from {len(event_bindings)} raw UI event binding(s)."
        )
        lines.append("")

        if not entry_points:
            lines.append("No web entry points were discovered.")
            lines.append("")
            return "\n".join(lines) + "\n"

        by_webform: dict[str, list[dict]] = {}
        for entry in entry_points:
            by_webform.setdefault(entry.get("webform") or "(unknown WebForm)", []).append(entry)

        lines.append("## By WebForm")
        lines.append("")
        for webform in sorted(by_webform):
            lines.append(f"### {_code(webform)}")
            lines.append("")
            lines.append("| Control | Event | Type | Handler | Confidence |")
            lines.append("|---|---|---|---|---|")
            rows = sorted(
                by_webform[webform],
                key=lambda e: (e.get("control") or "", e.get("event") or "", e.get("id") or ""),
            )
            for entry in rows:
                control = entry.get("control") or "_(page)_"
                lines.append(
                    f"| {_cell(control)} | {_cell(entry.get('event'))} | {_cell(entry.get('type'))} "
                    f"| {_cell(entry.get('handler'))} | {_cell(entry.get('confidence'))} |"
                )
            lines.append("")

        if unresolved:
            lines.append("## Unresolved Entry Points")
            lines.append("")
            lines.append(
                "These entry points could not be resolved to exactly one class/handler "
                "with confirmed evidence; they are listed here for visibility, not inferred further."
            )
            lines.append("")
            lines.append("| WebForm | Control | Event | Handler |")
            lines.append("|---|---|---|---|")
            for entry in sorted(unresolved, key=lambda e: (e.get("webform") or "", e.get("id") or "")):
                lines.append(
                    f"| {_cell(entry.get('webform'))} | {_cell(entry.get('control') or '_(page)_')} "
                    f"| {_cell(entry.get('event'))} | {_cell(entry.get('handler'))} |"
                )
            lines.append("")

        return "\n".join(lines) + "\n"

    def web_entry_points_navigation(self, indexes: dict) -> str:
        """Renders the WEB_ENTRY_POINTS.md navigation/summary document (V4.3-R4
        correction section 12): the same discovery summary as `web_entry_points()`,
        plus a link per WebForm-owner group into `web_entry_points/<safe-name>.md`
        instead of the full per-WebForm detail. Reopened for partitioning by the
        same empirical scale evidence already cited for FUNCTIONAL_FLOWS.md/etc.
        (V4.2-R7: ~25,595 lines / 1.2MB at real-repository scale).

        Grouping reuses the exact same three-tier rule
        `legacy_documenter.documentation.human_documentation_scaling.flow_group_key`
        applies to hydrated FLOW records, via the shared
        `webform_owner_group_key` helper -- never a locally reinvented rule.

        V4.3-R4 correction (human-documentation-in-Spanish-by-default gate):
        this navigation document is human-facing prose over `human_documentation`-
        adjacent output introduced by R4, so it renders in Spanish, like every
        other R4-authored human-facing document (`human_documentation_scaling.py`).
        This does not extend to `web_entry_points()` (the pre-existing flat
        renderer, unchanged, still English) -- see the module docstring/R3 section
        8 for why that renderer's language is a separate, not-yet-made decision.
        WebForm paths, control ids, handler names and confidence values are never
        translated; only the surrounding prose/headers are.
        """
        entry_points = indexes.get("entry_points", [])
        event_bindings = indexes.get("event_bindings", [])
        confirmed = [e for e in entry_points if e.get("confidence") == "confirmed"]
        unresolved = [e for e in entry_points if e.get("confidence") != "confirmed"]

        lines = ["# Puntos de entrada web", ""]
        lines.append(
            f"Se descubrieron {len(entry_points)} punto(s) de entrada en "
            f"{len({e.get('webform') for e in entry_points})} WebForm(s) "
            f"({len(confirmed)} confirmado(s), {len(unresolved)} no resuelto(s)), "
            f"a partir de {len(event_bindings)} evento(s) de UI en bruto."
        )
        lines.append("")

        if not entry_points:
            lines.append("No se descubrieron puntos de entrada web.")
            lines.append("")
            return "\n".join(lines) + "\n"

        groups = _group_by(entry_points, _web_entry_point_group_key)
        filenames = build_partition_filenames(sorted(groups))
        lines.append("## Grupos de puntos de entrada")
        lines.append("")
        lines.append(
            "El detalle completo por WebForm (tablas de Control/Evento/Tipo/Manejador/Confianza, "
            "y cualquier punto de entrada no resuelto) está particionado por grupo propietario "
            "del WebForm abajo."
        )
        lines.append("")
        lines.append("| Grupo | WebForms | Puntos de entrada | Confirmados | No resueltos | Detalle |")
        lines.append("|---|---|---|---|---|---|")
        for key in sorted(groups):
            group_entries = groups[key]
            webform_count = len({e.get("webform") for e in group_entries})
            confirmed_n = len([e for e in group_entries if e.get("confidence") == "confirmed"])
            unresolved_n = len(group_entries) - confirmed_n
            filename = filenames[key]
            link = f"web_entry_points/{filename}"
            lines.append(
                f"| {_cell(key)} | {webform_count} | {len(group_entries)} | {confirmed_n} | {unresolved_n} "
                f"| [{filename}]({link}) |"
            )
        lines.append("")
        return "\n".join(lines) + "\n"

    def web_entry_points_partitions(self, indexes: dict) -> dict[str, str]:
        """Renders one `web_entry_points/<safe-name>.md` document per WebForm-owner
        group, each with the same "Por WebForm"/"Puntos de entrada no resueltos"
        tables `web_entry_points()` already renders for its group's own entries
        only -- every entry point from `web_entry_points()` appears in exactly one
        partition, never duplicated or dropped.

        V4.3-R4 correction: rendered in Spanish (see `web_entry_points_navigation`
        docstring). WebForm paths, control ids, handler names and confidence
        values are preserved verbatim -- never translated.
        """
        entry_points = indexes.get("entry_points", [])
        if not entry_points:
            return {}
        groups = _group_by(entry_points, _web_entry_point_group_key)
        filenames = build_partition_filenames(sorted(groups))

        result: dict[str, str] = {}
        for key, group_entries in groups.items():
            lines = [
                f"# Puntos de entrada web — {key}", "",
                f"{len(group_entries)} punto(s) de entrada en este grupo.", "",
            ]
            by_webform: dict[str, list[dict]] = {}
            for entry in group_entries:
                by_webform.setdefault(entry.get("webform") or "(WebForm desconocido)", []).append(entry)

            lines.append("## Por WebForm")
            lines.append("")
            for webform in sorted(by_webform):
                lines.append(f"### {_code(webform)}")
                lines.append("")
                lines.append("| Control | Evento | Tipo | Manejador | Confianza |")
                lines.append("|---|---|---|---|---|")
                rows = sorted(
                    by_webform[webform],
                    key=lambda e: (e.get("control") or "", e.get("event") or "", e.get("id") or ""),
                )
                for entry in rows:
                    control = entry.get("control") or "_(página)_"
                    lines.append(
                        f"| {_cell(control)} | {_cell(entry.get('event'))} | {_cell(entry.get('type'))} "
                        f"| {_cell(entry.get('handler'))} | {_cell(entry.get('confidence'))} |"
                    )
                lines.append("")

            group_unresolved = [e for e in group_entries if e.get("confidence") != "confirmed"]
            if group_unresolved:
                lines.append("## Puntos de entrada no resueltos")
                lines.append("")
                lines.append(
                    "Estos puntos de entrada no pudieron resolverse a exactamente una clase/manejador "
                    "con evidencia confirmada; se listan aquí por visibilidad, sin inferir más."
                )
                lines.append("")
                lines.append("| WebForm | Control | Evento | Manejador |")
                lines.append("|---|---|---|---|")
                for entry in sorted(group_unresolved, key=lambda e: (e.get("webform") or "", e.get("id") or "")):
                    lines.append(
                        f"| {_cell(entry.get('webform'))} | {_cell(entry.get('control') or '_(página)_')} "
                        f"| {_cell(entry.get('event'))} | {_cell(entry.get('handler'))} |"
                    )
                lines.append("")
            result[filenames[key]] = "\n".join(lines) + "\n"
        return result

    # ------------------------------------------------------------------
    # Functional Flows
    # ------------------------------------------------------------------

    _FUNCTIONAL_FLOWS_INTRO = (
        "A flow's top-level `Status`/`Confidence` are a worst-case aggregation across "
        "every traced execution path: a single unrelated unresolved call anywhere in the "
        "sequence downgrades them, even when another path in the same flow reached a "
        "real, `confirmed` database/stored-procedure terminal. Read `Confirmed terminal "
        "reached` alongside `Status` for the fact `Status` alone can hide: a flow can "
        "read `status: unresolved_boundary` and still have reached confirmed terminal "
        "evidence -- both facts are preserved independently, never one at the expense of "
        "the other."
    )

    def functional_flows(self, indexes: dict) -> str:
        """Renders the complete, flat FUNCTIONAL_FLOWS.md (every flow in one document).

        Kept for direct callers/tests that want the full, unpartitioned document;
        the `full`/`analyze` pipeline itself uses `functional_flows_navigation`
        plus `functional_flows_partitions` instead (V4.2-R8) once the flow count
        makes a single document impractically large.
        """
        flows = indexes.get("functional_flows", [])
        paths_by_flow = _group_paths_by_flow(indexes.get("functional_paths", []))
        summary = indexes.get("flow_summary") or {}
        unresolved = indexes.get("flow_unresolved", [])

        lines = ["# Functional Flows", "", self._FUNCTIONAL_FLOWS_INTRO, ""]
        if summary:
            lines += _summary_table_lines(summary)

        if not flows:
            lines.append("No functional flows were discovered.")
            lines.append("")
            return "\n".join(lines) + "\n"

        lines.append("## Discovered Flows")
        lines.append("")
        ordered_flows = sorted(
            flows, key=lambda f: (f.get("webform") or "", f.get("handler") or "", f.get("id") or "")
        )
        for flow in ordered_flows:
            lines.extend(_render_flow_entry_lines(flow, paths_by_flow))

        if unresolved:
            flow_by_id = {f.get("id"): f for f in flows}
            lines.append("## Unresolved Boundaries")
            lines.append("")
            lines.append(
                "Execution paths that could not be traced to a confirmed stored procedure, "
                "SQL operation, or other resolved endpoint. Unresolved boundaries are preserved "
                "as unresolved -- they are never converted into an assumed call."
            )
            lines.append("")
            lines.extend(_unresolved_boundary_table_lines(unresolved, flow_by_id))
            lines.append("")

        return "\n".join(lines) + "\n"

    def functional_flows_navigation(self, indexes: dict) -> str:
        """Renders the FUNCTIONAL_FLOWS.md navigation/summary document (V4.2-R8), in
        Spanish since V4.3-R7 BLOQUEO 2 (human-readable/product-facing documentation
        is Spanish by default): the same intro/summary as `functional_flows()`, plus
        a link per project group into `functional_flows/<safe-name>.md` instead of
        the full detail. Field/status/identifier values are never translated -- only
        the surrounding prose/headers are. The flat `functional_flows()` renderer is
        unchanged and stays English (kept for existing English-language test/API
        callers that want one complete document, not part of `full`/`analyze`
        output -- see the module docstring).
        """
        flows = indexes.get("functional_flows", [])
        summary = indexes.get("flow_summary") or {}

        lines = ["# Flujos funcionales", "", _FUNCTIONAL_FLOWS_INTRO_ES, ""]
        if summary:
            lines += _summary_table_lines_es(summary)

        if not flows:
            lines.append("No se descubrieron flujos funcionales.")
            lines.append("")
            return "\n".join(lines) + "\n"

        groups = _group_by(flows, _flow_group_key)
        filenames = build_partition_filenames(sorted(groups))
        lines.append("## Grupos de flujos")
        lines.append("")
        lines.append(
            "El detalle completo por flujo (cadenas de ruta, los hechos `Confirmed terminal "
            "reached`/`Unresolved boundary remains` de F-01) está particionado por proyecto abajo."
        )
        lines.append("")
        lines.append("| Grupo | Flujos | Terminal confirmado | Límite no resuelto | Detalle |")
        lines.append("|---|---|---|---|---|")
        for key in sorted(groups):
            group_flows = groups[key]
            confirmed_n = len([f for f in group_flows if f.get("has_confirmed_terminal")])
            unresolved_n = len([f for f in group_flows if f.get("has_unresolved_boundary")])
            filename = filenames[key]
            link = f"functional_flows/{filename}"
            lines.append(
                f"| {_cell(key)} | {len(group_flows)} | {confirmed_n} | {unresolved_n} "
                f"| [{filename}]({link}) |"
            )
        lines.append("")
        return "\n".join(lines) + "\n"

    def functional_flows_partitions(self, indexes: dict) -> dict[str, str]:
        """Renders one `functional_flows/<safe-name>.md` document per project group,
        in Spanish (V4.3-R7 BLOQUEO 2). Identifiers/paths/status values are preserved
        verbatim.
        """
        flows = indexes.get("functional_flows", [])
        if not flows:
            return {}
        paths_by_flow = _group_paths_by_flow(indexes.get("functional_paths", []))
        unresolved = indexes.get("flow_unresolved", [])
        flow_by_id = {f.get("id"): f for f in flows}
        groups = _group_by(flows, _flow_group_key)
        filenames = build_partition_filenames(sorted(groups))

        result: dict[str, str] = {}
        for key, group_flows in groups.items():
            lines = [f"# Flujos funcionales — {key}", "", f"{len(group_flows)} flujo(s) en este grupo.", ""]
            ordered = sorted(
                group_flows, key=lambda f: (f.get("webform") or "", f.get("handler") or "", f.get("id") or "")
            )
            for flow in ordered:
                lines.extend(_render_flow_entry_lines_es(flow, paths_by_flow))

            group_flow_ids = {f.get("id") for f in group_flows}
            group_unresolved = [p for p in unresolved if p.get("flow_id") in group_flow_ids]
            if group_unresolved:
                lines.append("## Límites no resueltos")
                lines.append("")
                lines.extend(_unresolved_boundary_table_lines_es(group_unresolved, flow_by_id))
                lines.append("")
            result[filenames[key]] = "\n".join(lines) + "\n"
        return result

    # ------------------------------------------------------------------
    # Database Access
    # ------------------------------------------------------------------

    _DATABASE_ACCESS_CLASSIFICATION = (
        "- `stored_procedure`: a named Oracle package/procedure is invoked (the exact "
        "name is known from source evidence).\n"
        "- `sql_operation`: a raw/dynamic SQL statement is executed (no named procedure).\n"
        "- `transaction`: a bare `BeginTrans`/`Commit`/`Rollback` sequence with no "
        "procedure or SQL text captured.\n"
        "- `confidence`: `confirmed` (backed by exact source evidence) or `unresolved` "
        "(the call exists but its exact target could not be established "
        "deterministically -- never guessed)."
    )

    def database_access(self, indexes: dict) -> str:
        """Renders the complete, flat DATABASE_ACCESS.md (every operation in one document)."""
        data_access = indexes.get("data_access", [])
        stored_procedures = indexes.get("stored_procedures", [])
        sql_operations = indexes.get("sql_operations", [])
        data_parameters = indexes.get("data_parameters", [])

        lines = ["# Database Access", ""]
        lines.append(_database_access_summary_sentence(data_access, stored_procedures, sql_operations, data_parameters))
        lines.append("")

        if not any((data_access, stored_procedures, sql_operations)):
            lines.append("No database access was discovered.")
            lines.append("")
            return "\n".join(lines) + "\n"

        if data_access:
            lines.append("## Access Points")
            lines.append("")
            lines.extend(_data_access_table_lines(data_access))
            lines.append("")

        if stored_procedures:
            lines.append("## Stored Procedures")
            lines.append("")
            lines.extend(_stored_procedure_table_lines(stored_procedures))
            lines.append("")

        if sql_operations:
            lines.append("## SQL Operations")
            lines.append("")
            lines.extend(_sql_operation_table_lines(sql_operations))
            lines.append("")

        if data_parameters:
            lines.append("## Parameters")
            lines.append("")
            lines.extend(_parameter_table_lines(data_parameters))
            lines.append("")

        return "\n".join(lines) + "\n"

    _DATABASE_ACCESS_CLASSIFICATION_ES = (
        "- `stored_procedure`: se invoca un paquete/procedimiento con nombre en Oracle (el nombre "
        "exacto se conoce por evidencia de origen).\n"
        "- `sql_operation`: se ejecuta una sentencia SQL en bruto/dinámica (sin procedimiento con "
        "nombre).\n"
        "- `transaction`: una secuencia `BeginTrans`/`Commit`/`Rollback` simple, sin procedimiento "
        "ni texto SQL capturado.\n"
        "- `confidence`: `confirmed` (respaldado por evidencia de origen exacta) o `unresolved` "
        "(la llamada existe pero su objetivo exacto no pudo establecerse de forma determinista -- "
        "nunca se adivina)."
    )

    def database_access_navigation(self, indexes: dict) -> str:
        """Renders the DATABASE_ACCESS.md navigation/summary document (V4.2-R8), in
        Spanish since V4.3-R7 BLOQUEO 2: summary, classification explanation, and a
        link per project group into `database_access/<safe-name>.md`. `## Parámetros`
        is small and already grouped by caller, so it stays here rather than being
        partitioned. Identifiers/status values are preserved verbatim.
        """
        data_access = indexes.get("data_access", [])
        stored_procedures = indexes.get("stored_procedures", [])
        sql_operations = indexes.get("sql_operations", [])
        data_parameters = indexes.get("data_parameters", [])

        lines = ["# Acceso a base de datos", ""]
        lines.append(
            _database_access_summary_sentence_es(data_access, stored_procedures, sql_operations, data_parameters)
        )
        lines.append("")
        lines.append("## Clasificación")
        lines.append("")
        lines.append(self._DATABASE_ACCESS_CLASSIFICATION_ES)
        lines.append("")

        if not any((data_access, stored_procedures, sql_operations)):
            lines.append("No se descubrió acceso a base de datos.")
            lines.append("")
            return "\n".join(lines) + "\n"

        groups = _group_database_access(data_access, stored_procedures, sql_operations)
        filenames = build_partition_filenames(sorted(groups))
        lines.append("## Grupos de acceso")
        lines.append("")
        lines.append(
            "La evidencia completa (puntos de acceso, procedimientos almacenados, operaciones SQL) "
            "está particionada por proyecto abajo."
        )
        lines.append("")
        lines.append("| Grupo | Puntos de acceso | Procedimientos almacenados | Operaciones SQL | Detalle |")
        lines.append("|---|---|---|---|---|")
        for key in sorted(groups):
            group = groups[key]
            filename = filenames[key]
            link = f"database_access/{filename}"
            lines.append(
                f"| {_cell(key)} | {len(group['data_access'])} | {len(group['stored_procedures'])} "
                f"| {len(group['sql_operations'])} | [{filename}]({link}) |"
            )
        lines.append("")

        if data_parameters:
            lines.append("## Parámetros")
            lines.append("")
            lines.extend(_parameter_table_lines_es(data_parameters))
            lines.append("")

        return "\n".join(lines) + "\n"

    def database_access_partitions(self, indexes: dict) -> dict[str, str]:
        """Renders one `database_access/<safe-name>.md` document per project group,
        in Spanish (V4.3-R7 BLOQUEO 2).
        """
        data_access = indexes.get("data_access", [])
        stored_procedures = indexes.get("stored_procedures", [])
        sql_operations = indexes.get("sql_operations", [])
        if not any((data_access, stored_procedures, sql_operations)):
            return {}
        groups = _group_database_access(data_access, stored_procedures, sql_operations)
        filenames = build_partition_filenames(sorted(groups))

        result: dict[str, str] = {}
        for key, group in groups.items():
            lines = [f"# Acceso a base de datos — {key}", ""]
            if group["data_access"]:
                lines.append("## Puntos de acceso")
                lines.append("")
                lines.extend(_data_access_table_lines_es(group["data_access"]))
                lines.append("")
            if group["stored_procedures"]:
                lines.append("## Procedimientos almacenados")
                lines.append("")
                lines.extend(_stored_procedure_table_lines_es(group["stored_procedures"]))
                lines.append("")
            if group["sql_operations"]:
                lines.append("## Operaciones SQL")
                lines.append("")
                lines.extend(_sql_operation_table_lines_es(group["sql_operations"]))
                lines.append("")
            result[filenames[key]] = "\n".join(lines) + "\n"
        return result

    # ------------------------------------------------------------------
    # Unresolved Findings
    # ------------------------------------------------------------------

    _UNRESOLVED_FINDINGS_INTRO = (
        "What LegacyMapper could not establish deterministically. Nothing in this document "
        "is an inferred fact -- every row here is an explicit gap in the evidence, preserved "
        "as unresolved rather than guessed."
    )

    def unresolved_findings(self, indexes: dict) -> str:
        """Renders the complete, flat UNRESOLVED_FINDINGS.md (every category in one document)."""
        categories = _unresolved_categories(indexes)
        lines = ["# Unresolved Findings", "", self._UNRESOLVED_FINDINGS_INTRO, ""]
        lines.extend(_unresolved_category_count_table_lines(categories))
        lines.append("")

        if not any(items for _, _, _, items in categories):
            lines.append("No unresolved findings were recorded for this run.")
            lines.append("")
            return "\n".join(lines) + "\n"

        for key, _count_label, heading, items in categories:
            if not items:
                continue
            lines.append(f"## {heading}")
            lines.append("")
            lines.extend(_render_unresolved_category_body(key, items))
            lines.append("")

        return "\n".join(lines) + "\n"

    def unresolved_findings_navigation(self, indexes: dict) -> str:
        """Renders the UNRESOLVED_FINDINGS.md navigation/summary document (V4.2-R8),
        in Spanish since V4.3-R7 BLOQUEO 2: the same category-count table, with a
        link per nonempty category into `unresolved_findings/<category>.md`.
        """
        categories = _unresolved_categories(indexes)
        lines = ["# Hallazgos no resueltos", "", _UNRESOLVED_FINDINGS_INTRO_ES, ""]

        if not any(items for _, _, _, items in categories):
            lines.extend(_unresolved_category_count_table_lines_es(categories))
            lines.append("")
            lines.append("No se registraron hallazgos no resueltos para esta corrida.")
            lines.append("")
            return "\n".join(lines) + "\n"

        keys = [key for key, _, _, items in categories if items]
        filenames = build_partition_filenames(keys)
        lines.append("| Categoría | Cantidad | Detalle |")
        lines.append("|---|---|---|")
        for key, _count_label, _heading, items in categories:
            label_es, _heading_es = _UNRESOLVED_CATEGORY_LABELS_ES[key]
            if items:
                filename = filenames[key]
                link = f"unresolved_findings/{filename}"
                lines.append(f"| {label_es} | {len(items)} | [{filename}]({link}) |")
            else:
                lines.append(f"| {label_es} | 0 | _ninguno_ |")
        lines.append("")
        return "\n".join(lines) + "\n"

    def unresolved_findings_partitions(self, indexes: dict) -> dict[str, str]:
        """Renders one `unresolved_findings/<category>.md` document per nonempty
        category, in Spanish (V4.3-R7 BLOQUEO 2).
        """
        categories = _unresolved_categories(indexes)
        keys = [key for key, _, _, items in categories if items]
        if not keys:
            return {}
        filenames = build_partition_filenames(keys)
        result: dict[str, str] = {}
        for key, _count_label, _heading, items in categories:
            if not items:
                continue
            _label_es, heading_es = _UNRESOLVED_CATEGORY_LABELS_ES[key]
            lines = [
                f"# Hallazgos no resueltos — {heading_es}", "",
                f"{len(items)} elemento(s) en esta categoría.", "",
            ]
            lines.extend(_render_unresolved_category_body_es(key, items))
            lines.append("")
            result[filenames[key]] = "\n".join(lines) + "\n"
        return result

    def documentation_readme(self, indexes: dict) -> str:
        """Renders `documentation/README.md` (V4.2-R8 section 6), in Spanish since
        V4.3-R7 BLOQUEO 2: the single top-level navigation document telling a
        developer what was analyzed, where each area is documented, what
        confirmed/unresolved mean, and how to reach machine-readable evidence for
        more detail. Never embeds an absolute analyst path or credential.
        """
        repo = indexes.get("repository") or {}
        label = _repository_display_label(repo.get("root"))
        lines = [
            "# Documentación de LegacyMapper",
            "",
            f"Este paquete documenta el análisis determinista de `{label}`. "
            "Empiece aquí y luego siga los enlaces de abajo hacia el área que necesite.",
            "",
            "| Documento | Cubre |",
            "|---|---|",
            "| [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) | Escala del repositorio por tipo de archivo. |",
            "| [SOLUTION_STRUCTURE.md](SOLUTION_STRUCTURE.md) | Soluciones y sus proyectos miembro. |",
            "| [PROJECT_DEPENDENCIES.md](PROJECT_DEPENDENCIES.md) | Aristas de dependencia de proyecto/DLL "
            "(índice; detalle completo bajo `project_dependencies/`). |",
            "| [WEBFORMS_MAP.md](WEBFORMS_MAP.md) | Metadatos de markup de WebForms (code-behind, "
            "registers, master pages). |",
            "| [WEB_ENTRY_POINTS.md](WEB_ENTRY_POINTS.md) | Cada punto de entrada de control/evento/"
            "manejador de UI descubierto (índice; detalle completo bajo `web_entry_points/`). |",
            "| [FUNCTIONAL_FLOWS.md](FUNCTIONAL_FLOWS.md) | Flujos de ejecución UI → BL → base de datos "
            "(índice; detalle completo bajo `functional_flows/`). |",
            "| [DATABASE_ACCESS.md](DATABASE_ACCESS.md) | Evidencia de procedimientos almacenados/SQL/"
            "transacciones (índice; detalle completo bajo `database_access/`). |",
            "| [UNRESOLVED_FINDINGS.md](UNRESOLVED_FINDINGS.md) | Todo lo que LegacyMapper no pudo "
            "establecer de forma determinista (índice; detalle completo bajo `unresolved_findings/`). |",
            "| [CONFIGURATION_SUMMARY.md](CONFIGURATION_SUMMARY.md) | Conteos de `Web.config` únicamente "
            "— nunca valores secretos. |",
            "| [ANALYSIS_WARNINGS.md](ANALYSIS_WARNINGS.md) | Errores de extracción capturados durante "
            "esta corrida. |",
            "| [HUMAN_DOCUMENTATION.md](HUMAN_DOCUMENTATION.md) | Documentación humana en español por "
            "flujo (índice; detalle completo bajo `flujos_humanos/`). |",
            "",
            "## \"Confirmado\" vs \"No resuelto\"",
            "",
            "`confirmed` significa que una relación o un valor está respaldado por evidencia de origen "
            "exacta y citada (un archivo y una línea). `unresolved` significa que LegacyMapper encontró "
            "la llamada/referencia pero no pudo establecer de forma determinista su objetivo o valor -- "
            "esto se preserva explícitamente, nunca se adivina ni se fabrica. Vea FUNCTIONAL_FLOWS.md "
            "para ver cómo un mismo flujo puede llevar a la vez un hecho confirmado y uno no resuelto.",
            "",
            "## Evidencia machine-readable",
            "",
            "Cada documento de arriba es una proyección humana de `index/*.json` (y `ai_context/*.json`), "
            "que siguen siendo la evidencia autoritativa — consúltelos directamente para cualquier "
            "detalle que esta proyección no muestre.",
            "",
        ]
        return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------
# Shared rendering helpers (used by both the flat and partitioned methods)
# ----------------------------------------------------------------------


def _summary_table_lines(summary: dict) -> list[str]:
    lines = ["## Summary", "", "| Metric | Value |", "|---|---|"]
    for key in sorted(summary):
        lines.append(f"| {_cell(key)} | {_cell(summary[key])} |")
    lines.append("")
    return lines


# ----------------------------------------------------------------------
# Spanish-language counterparts (V4.3-R7 BLOQUEO 2): used only by the
# `*_navigation`/`*_partitions` methods, which are the ones `full`/`analyze`
# actually write to `documentation/`. The flat `functional_flows()`/
# `database_access()`/`unresolved_findings()` methods above are unchanged
# and stay English -- they are not part of `full`/`analyze` output (see the
# module docstring), only kept for existing English-language test/API
# callers that want one complete, unpartitioned document. Every function
# below mirrors its English counterpart's structure/data exactly; only
# prose/headers are translated -- identifiers, paths, JSON field names and
# status values (`confirmed`/`unresolved`/etc.) are always passed through
# unchanged via the same `_cell`/`_code` helpers.
# ----------------------------------------------------------------------

_FUNCTIONAL_FLOWS_INTRO_ES = (
    "El `Status`/`Confidence` de nivel superior de un flujo son una agregación de peor caso entre "
    "cada ruta de ejecución rastreada: una única llamada no resuelta y no relacionada en cualquier "
    "punto de la secuencia los degrada, incluso cuando otra ruta del mismo flujo alcanzó un terminal "
    "real y `confirmed` de base de datos/procedimiento almacenado. Lea `Confirmed terminal reached` "
    "junto con `Status` para el hecho que `Status` por sí solo puede ocultar: un flujo puede tener "
    "`status: unresolved_boundary` y aun así haber alcanzado evidencia de terminal confirmada — ambos "
    "hechos se preservan de forma independiente, nunca uno a costa del otro."
)


def _summary_table_lines_es(summary: dict) -> list[str]:
    lines = ["## Resumen", "", "| Métrica | Valor |", "|---|---|"]
    for key in sorted(summary):
        lines.append(f"| {_cell(key)} | {_cell(summary[key])} |")
    lines.append("")
    return lines


def _render_flow_entry_lines_es(flow: dict, paths_by_flow: dict[str, list[dict]]) -> list[str]:
    node_labels = _flow_node_labels(flow)
    lines = [f"### {_code(flow.get('webform'))} → `{flow.get('event')}` → {_code(flow.get('handler'))}", ""]
    lines.append(
        f"- Estado: `{flow.get('status')}` | Confianza: `{flow.get('confidence')}` | "
        f"Terminal confirmado alcanzado: `{'sí' if flow.get('has_confirmed_terminal') else 'no'}` | "
        f"Límite no resuelto pendiente: `{'sí' if flow.get('has_unresolved_boundary') else 'no'}` | "
        f"Profundidad: `{flow.get('depth')}` | Operación(es) terminal(es): "
        f"{', '.join(_code(op) for op in sorted(flow.get('terminal_operations', []))) or '_ninguna_'}"
    )
    lines.append("")
    flow_paths = paths_by_flow.get(flow.get("id"), [])
    if not flow_paths:
        lines.append("_No se descubrió ninguna ruta de ejecución para este flujo._")
        lines.append("")
        return lines
    for path in sorted(flow_paths, key=lambda p: p.get("path_id") or ""):
        lines.append(f"- {_render_path_chain(node_labels, path)}")
    lines.append("")
    return lines


def _unresolved_boundary_table_lines_es(paths: list[dict], flow_by_id: dict[str, dict]) -> list[str]:
    lines = ["| Flujo | Tipo de terminal | Objetivo del terminal | Confianza |", "|---|---|---|---|"]
    for path in sorted(paths, key=lambda p: (p.get("flow_id") or "", p.get("path_id") or "")):
        flow = flow_by_id.get(path.get("flow_id"), {})
        flow_label = f"{flow.get('webform', '?')} / {flow.get('handler', '?')}"
        lines.append(
            f"| {_cell(flow_label)} | {_cell(path.get('terminal_type'))} "
            f"| {_cell(path.get('terminal_target'))} | {_cell(path.get('confidence'))} |"
        )
    return lines


def _database_access_summary_sentence_es(
    data_access: list, stored_procedures: list, sql_operations: list, data_parameters: list
) -> str:
    return (
        f"Se descubrieron {len(data_access)} operación(es) de acceso a base de datos, "
        f"{len(stored_procedures)} referencia(s) a procedimiento(s) almacenado(s), "
        f"{len(sql_operations)} operación(es) SQL, y {len(data_parameters)} parámetro(s)."
    )


def _data_access_table_lines_es(data_access: list[dict]) -> list[str]:
    lines = [
        "| Clase.Método | Proyecto | Tipo de operación | Objetivo | Confianza | Origen |",
        "|---|---|---|---|---|---|",
    ]
    for entry in sorted(data_access, key=lambda e: (e.get("class") or "", e.get("method") or "", e.get("id") or "")):
        target = entry.get("stored_procedure") or entry.get("sql_operation") or entry.get("command_text") or ""
        caller = f"{entry.get('class', '?')}.{entry.get('method', '?')}"
        lines.append(
            f"| {_cell(caller)} | {_cell(entry.get('project'))} | {_cell(entry.get('operation_kind'))} "
            f"| {_cell(target)} | {_cell(entry.get('confidence'))} | {_cell(_first_evidence(entry))} |"
        )
    return lines


def _stored_procedure_table_lines_es(stored_procedures: list[dict]) -> list[str]:
    lines = ["| Nombre | Paquete | Procedimiento | Confianza | Origen |", "|---|---|---|---|---|"]
    for proc in sorted(stored_procedures, key=lambda p: (p.get("name") or "", p.get("id") or "")):
        lines.append(
            f"| {_cell(proc.get('name'))} | {_cell(proc.get('package'))} | {_cell(proc.get('procedure'))} "
            f"| {_cell(proc.get('confidence'))} | {_cell(_first_evidence(proc))} |"
        )
    return lines


def _sql_operation_table_lines_es(sql_operations: list[dict]) -> list[str]:
    lines = ["| Operación | Texto del comando | SQL dinámico | Confianza | Origen |", "|---|---|---|---|---|"]
    for op in sorted(sql_operations, key=lambda o: (o.get("operation") or "", o.get("id") or "")):
        lines.append(
            f"| {_cell(op.get('operation'))} | {_cell(_truncate(op.get('command_text')))} "
            f"| {_cell(op.get('dynamic_sql'))} | {_cell(op.get('confidence'))} | {_cell(_first_evidence(op))} |"
        )
    return lines


def _parameter_table_lines_es(data_parameters: list[dict]) -> list[str]:
    lines = [
        "Agrupado por quien invoca; el detalle completo (dirección, tipo, tamaño) está disponible en "
        "`index/data_parameters.json`.",
        "",
    ]
    by_caller: dict[str, list[str]] = {}
    for param in data_parameters:
        caller = f"{param.get('class', '?')}.{param.get('method', '?')}"
        by_caller.setdefault(caller, []).append(param.get("name") or "(sin nombre)")
    lines.append("| Clase.Método | Parámetros |")
    lines.append("|---|---|")
    for caller in sorted(by_caller):
        names = ", ".join(_code(n) for n in sorted(set(by_caller[caller])))
        lines.append(f"| {_cell(caller)} | {names} |")
    return lines


_UNRESOLVED_FINDINGS_INTRO_ES = (
    "Lo que LegacyMapper no pudo establecer de forma determinista. Nada en este documento es un "
    "hecho inferido -- cada fila aquí es una brecha explícita en la evidencia, preservada como no "
    "resuelta en lugar de adivinada."
)

# Spanish (count_label, heading) per category key, keyed identically to
# `_unresolved_categories`'s own `key` -- item derivation itself is purely
# structural and stays shared with the English flat renderer via that
# function; only the human-facing label/heading text is duplicated here.
_UNRESOLVED_CATEGORY_LABELS_ES = {
    "extraction_errors": ("Errores de extracción", "Errores de extracción"),
    "unresolved_flow_boundaries": ("Límites de flujo no resueltos", "Límites de flujo no resueltos"),
    "unresolved_entry_points": ("Puntos de entrada no resueltos", "Puntos de entrada no resueltos"),
    "unresolved_database_access": ("Acceso a base de datos no resuelto", "Acceso a base de datos no resuelto"),
}


def _unresolved_category_count_table_lines_es(categories: list[tuple[str, str, str, list[dict]]]) -> list[str]:
    lines = ["| Categoría | Cantidad |", "|---|---|"]
    for key, _count_label, _heading, items in categories:
        label_es, _heading_es = _UNRESOLVED_CATEGORY_LABELS_ES[key]
        lines.append(f"| {label_es} | {len(items)} |")
    return lines


def _render_unresolved_category_body_es(key: str, items: list[dict]) -> list[str]:
    if key == "extraction_errors":
        lines = ["| Archivo | Extractor | Error |", "|---|---|---|"]
        for error in sorted(items, key=lambda e: (e.get("file") or "", e.get("extractor") or "")):
            lines.append(
                f"| {_cell(error.get('file'))} | {_cell(error.get('extractor'))} | {_cell(error.get('error'))} |"
            )
        return lines

    if key == "unresolved_flow_boundaries":
        boilerplate = [p for p in items if p.get("terminal_target") in _BOILERPLATE_TERMINAL_TARGETS]
        other = [p for p in items if p.get("terminal_target") not in _BOILERPLATE_TERMINAL_TARGETS]
        lines: list[str] = ["Ver `FUNCTIONAL_FLOWS.md` para el detalle completo por flujo; resumido aquí:", ""]
        if other:
            lines.append("### Otros límites no resueltos")
            lines.append("")
            lines.extend(_flow_boundary_table_lines_es(other))
            lines.append("")
        if boilerplate:
            lines.append("### Código repetitivo generado por el framework/diseñador")
            lines.append("")
            lines.append(
                "Llamadas rutinarias generadas por el diseñador (p. ej. `InitializeComponent()`), "
                "agrupadas por separado por legibilidad -- se preservan igualmente como evidencia no "
                "resuelta, nunca se descartan (F-06, PRESERVED_OBSERVATION)."
            )
            lines.append("")
            lines.extend(_flow_boundary_table_lines_es(boilerplate))
        if lines and not lines[-1]:
            lines.pop()
        return lines

    if key == "unresolved_entry_points":
        return [
            "Ver `WEB_ENTRY_POINTS.md` para el detalle completo; resumido aquí:",
            "",
            f"{len(items)} punto(s) de entrada no pudieron resolverse a un único manejador confirmado.",
        ]

    # unresolved_database_access
    lines = ["| Clase.Método | Proyecto |", "|---|---|"]
    for entry in sorted(items, key=lambda e: (e.get("class") or "", e.get("method") or "")):
        caller = f"{entry.get('class', '?')}.{entry.get('method', '?')}"
        lines.append(f"| {_cell(caller)} | {_cell(entry.get('project'))} |")
    return lines


def _flow_boundary_table_lines_es(paths: list[dict]) -> list[str]:
    lines = ["| ID de flujo | Tipo de terminal | Objetivo del terminal |", "|---|---|---|"]
    for path in sorted(paths, key=lambda p: (p.get("flow_id") or "", p.get("path_id") or "")):
        lines.append(
            f"| {_cell(path.get('flow_id'))} | {_cell(path.get('terminal_type'))} "
            f"| {_cell(path.get('terminal_target'))} |"
        )
    return lines


def _flow_group_key(flow: dict) -> str:
    sequence = flow.get("project_sequence") or []
    return sequence[0] if sequence else "unassigned"


def _web_entry_point_group_key(entry: dict) -> str:
    """WEB_ENTRY_POINTS.md's group key (V4.3-R4 correction section 12): the
    entry point's own WebForm-owning folder, via the shared
    `webform_owner_group_key` -- the same rule
    `human_documentation_scaling.flow_group_key` applies to hydrated FLOW
    records, reused here rather than reinvented.
    """
    return webform_owner_group_key(entry.get("webform"))


def _group_by(items: list[dict], key_fn) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for item in items:
        grouped.setdefault(key_fn(item), []).append(item)
    return grouped


def _render_flow_entry_lines(flow: dict, paths_by_flow: dict[str, list[dict]]) -> list[str]:
    node_labels = _flow_node_labels(flow)
    lines = [f"### {_code(flow.get('webform'))} → `{flow.get('event')}` → {_code(flow.get('handler'))}", ""]
    lines.append(
        f"- Status: `{flow.get('status')}` | Confidence: `{flow.get('confidence')}` | "
        f"Confirmed terminal reached: `{'yes' if flow.get('has_confirmed_terminal') else 'no'}` | "
        f"Unresolved boundary remains: `{'yes' if flow.get('has_unresolved_boundary') else 'no'}` | "
        f"Depth: `{flow.get('depth')}` | Terminal operation(s): "
        f"{', '.join(_code(op) for op in sorted(flow.get('terminal_operations', []))) or '_none_'}"
    )
    lines.append("")
    flow_paths = paths_by_flow.get(flow.get("id"), [])
    if not flow_paths:
        lines.append("_No discovered execution path for this flow._")
        lines.append("")
        return lines
    for path in sorted(flow_paths, key=lambda p: p.get("path_id") or ""):
        lines.append(f"- {_render_path_chain(node_labels, path)}")
    lines.append("")
    return lines


def _unresolved_boundary_table_lines(paths: list[dict], flow_by_id: dict[str, dict]) -> list[str]:
    lines = ["| Flow | Terminal Type | Terminal Target | Confidence |", "|---|---|---|---|"]
    for path in sorted(paths, key=lambda p: (p.get("flow_id") or "", p.get("path_id") or "")):
        flow = flow_by_id.get(path.get("flow_id"), {})
        flow_label = f"{flow.get('webform', '?')} / {flow.get('handler', '?')}"
        lines.append(
            f"| {_cell(flow_label)} | {_cell(path.get('terminal_type'))} "
            f"| {_cell(path.get('terminal_target'))} | {_cell(path.get('confidence'))} |"
        )
    return lines


def _group_paths_by_flow(paths: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for path in paths:
        grouped.setdefault(path.get("flow_id"), []).append(path)
    return grouped


def _flow_node_labels(flow: dict) -> dict[str, str]:
    return {node["id"]: node.get("label") or node["id"] for node in flow.get("nodes", [])}


def _render_path_chain(node_labels: dict[str, str], path: dict) -> str:
    """Renders one execution path as a readable `A → B → C` chain.

    The path's own `nodes` list already ends at the terminal node (a resolved
    stored-procedure/SQL node, or an unresolved-call/cycle/boundary node);
    `terminal_type` only decides how that last node is styled, never adds a
    node that isn't already in the discovered path.
    """
    node_ids = path.get("nodes", [])
    if not node_ids:
        return "_(no chain recorded)_"
    labels = [_short_label(node_labels.get(node_id, node_id)) for node_id in node_ids]
    resolved_terminal = path.get("terminal_type") in {"stored_procedure", "sql", "data_operation"}
    body = " → ".join(_code(label) for label in labels[:-1])
    last = _code(labels[-1])
    last_rendered = f"**{last}**" if resolved_terminal else f"_{last} (unresolved)_"
    return f"{body} → {last_rendered}" if body else last_rendered


def _short_label(label: object) -> str:
    """Trims a `project::qualified.name` internal identifier to its trailing segment for
    readability, without inventing a new name -- the full identifier remains traceable via
    the underlying `index/*.json` artifacts.
    """
    text = str(label)
    return text.rsplit("::", 1)[-1] if "::" in text else text


def _database_access_summary_sentence(data_access: list, stored_procedures: list, sql_operations: list, data_parameters: list) -> str:
    return (
        f"Discovered {len(data_access)} database access operation(s), "
        f"{len(stored_procedures)} stored procedure reference(s), "
        f"{len(sql_operations)} SQL operation(s), and {len(data_parameters)} parameter(s)."
    )


def _access_group_key(entry: dict) -> str:
    return entry.get("project") or "unassigned"


def _evidence_group_key(entry: dict) -> str:
    evidence = entry.get("evidence") or []
    if evidence:
        project = evidence[0].get("project")
        if project:
            return project
    return "unassigned"


def _group_database_access(data_access: list[dict], stored_procedures: list[dict], sql_operations: list[dict]) -> dict[str, dict]:
    groups: dict[str, dict] = {}

    def bucket(key: str) -> dict:
        return groups.setdefault(key, {"data_access": [], "stored_procedures": [], "sql_operations": []})

    for entry in data_access:
        bucket(_access_group_key(entry))["data_access"].append(entry)
    for proc in stored_procedures:
        bucket(_evidence_group_key(proc))["stored_procedures"].append(proc)
    for op in sql_operations:
        bucket(_evidence_group_key(op))["sql_operations"].append(op)
    return groups


def _data_access_table_lines(data_access: list[dict]) -> list[str]:
    lines = ["| Class.Method | Project | Operation Kind | Target | Confidence | Source |", "|---|---|---|---|---|---|"]
    for entry in sorted(data_access, key=lambda e: (e.get("class") or "", e.get("method") or "", e.get("id") or "")):
        target = entry.get("stored_procedure") or entry.get("sql_operation") or entry.get("command_text") or ""
        caller = f"{entry.get('class', '?')}.{entry.get('method', '?')}"
        lines.append(
            f"| {_cell(caller)} | {_cell(entry.get('project'))} | {_cell(entry.get('operation_kind'))} "
            f"| {_cell(target)} | {_cell(entry.get('confidence'))} | {_cell(_first_evidence(entry))} |"
        )
    return lines


def _stored_procedure_table_lines(stored_procedures: list[dict]) -> list[str]:
    lines = ["| Name | Package | Procedure | Confidence | Source |", "|---|---|---|---|---|"]
    for proc in sorted(stored_procedures, key=lambda p: (p.get("name") or "", p.get("id") or "")):
        lines.append(
            f"| {_cell(proc.get('name'))} | {_cell(proc.get('package'))} | {_cell(proc.get('procedure'))} "
            f"| {_cell(proc.get('confidence'))} | {_cell(_first_evidence(proc))} |"
        )
    return lines


def _sql_operation_table_lines(sql_operations: list[dict]) -> list[str]:
    lines = ["| Operation | Command Text | Dynamic SQL | Confidence | Source |", "|---|---|---|---|---|"]
    for op in sorted(sql_operations, key=lambda o: (o.get("operation") or "", o.get("id") or "")):
        lines.append(
            f"| {_cell(op.get('operation'))} | {_cell(_truncate(op.get('command_text')))} "
            f"| {_cell(op.get('dynamic_sql'))} | {_cell(op.get('confidence'))} | {_cell(_first_evidence(op))} |"
        )
    return lines


def _parameter_table_lines(data_parameters: list[dict]) -> list[str]:
    lines = [
        "Grouped by caller; full detail (direction, type, size) is available in "
        "`index/data_parameters.json`.",
        "",
    ]
    by_caller: dict[str, list[str]] = {}
    for param in data_parameters:
        caller = f"{param.get('class', '?')}.{param.get('method', '?')}"
        by_caller.setdefault(caller, []).append(param.get("name") or "(unnamed)")
    lines.append("| Class.Method | Parameters |")
    lines.append("|---|---|")
    for caller in sorted(by_caller):
        names = ", ".join(_code(n) for n in sorted(set(by_caller[caller])))
        lines.append(f"| {_cell(caller)} | {names} |")
    return lines


# Unresolved-findings category keys, titles, and how to derive each category's
# item list from `indexes` -- the single source of truth for the flat
# renderer, the navigation renderer, and the partitioned renderer alike.
def _unresolved_categories(indexes: dict) -> list[tuple[str, str, str, list[dict]]]:
    """Returns `(key, count_label, heading, items)` per category -- `count_label`
    preserves the exact pre-R8 phrasing used in the summary count table (kept
    byte-identical for backward compatibility with existing R3 assertions),
    `heading` preserves the exact pre-R8 `##`/`#` section title.
    """
    errors = indexes.get("errors", [])
    flow_unresolved = indexes.get("flow_unresolved", [])
    unresolved_entry_points = [e for e in indexes.get("entry_points", []) if e.get("confidence") != "confirmed"]
    unresolved_data_access = [d for d in indexes.get("data_access", []) if d.get("confidence") != "confirmed"]
    return [
        ("extraction_errors", "Extraction errors", "Extraction Errors", errors),
        ("unresolved_flow_boundaries", "Unresolved flow boundaries", "Unresolved Flow Boundaries", flow_unresolved),
        ("unresolved_entry_points", "Unresolved entry points", "Unresolved Entry Points", unresolved_entry_points),
        ("unresolved_database_access", "Unresolved database access", "Unresolved Database Access", unresolved_data_access),
    ]


def _unresolved_category_count_table_lines(categories: list[tuple[str, str, str, list[dict]]]) -> list[str]:
    lines = ["| Category | Count |", "|---|---|"]
    for _key, count_label, _heading, items in categories:
        lines.append(f"| {count_label} | {len(items)} |")
    return lines


# F-06 (PRESERVED_OBSERVATION): `InitializeComponent()` designer boilerplate
# dilutes genuinely interesting unresolved flow boundaries. This purely
# PRESENTATIONAL split (V4.2-R8 section 9) separates it into its own
# subsection without discarding or reclassifying a single row -- every
# boundary that was in the flat document is still here, under one heading
# or the other, and the category's own total count is unchanged.
_BOILERPLATE_TERMINAL_TARGETS = frozenset({"InitializeComponent()"})


def _render_unresolved_category_body(key: str, items: list[dict]) -> list[str]:
    if key == "extraction_errors":
        lines = ["| File | Extractor | Error |", "|---|---|---|"]
        for error in sorted(items, key=lambda e: (e.get("file") or "", e.get("extractor") or "")):
            lines.append(
                f"| {_cell(error.get('file'))} | {_cell(error.get('extractor'))} | {_cell(error.get('error'))} |"
            )
        return lines

    if key == "unresolved_flow_boundaries":
        boilerplate = [p for p in items if p.get("terminal_target") in _BOILERPLATE_TERMINAL_TARGETS]
        other = [p for p in items if p.get("terminal_target") not in _BOILERPLATE_TERMINAL_TARGETS]
        lines: list[str] = ["See `FUNCTIONAL_FLOWS.md` for full per-flow detail; summarized here:", ""]
        if other:
            lines.append("### Other Unresolved Boundaries")
            lines.append("")
            lines.extend(_flow_boundary_table_lines(other))
            lines.append("")
        if boilerplate:
            lines.append("### Framework/Designer-Generated Boilerplate")
            lines.append("")
            lines.append(
                "Routine designer-generated calls (e.g. `InitializeComponent()`), grouped "
                "separately for readability -- still preserved as unresolved evidence, "
                "never discarded (F-06, PRESERVED_OBSERVATION)."
            )
            lines.append("")
            lines.extend(_flow_boundary_table_lines(boilerplate))
        if lines and not lines[-1]:
            lines.pop()
        return lines

    if key == "unresolved_entry_points":
        return [
            "See `WEB_ENTRY_POINTS.md` for full detail; summarized here:",
            "",
            f"{len(items)} entry point(s) could not be resolved to a single confirmed handler.",
        ]

    # unresolved_database_access
    lines = ["| Class.Method | Project |", "|---|---|"]
    for entry in sorted(items, key=lambda e: (e.get("class") or "", e.get("method") or "")):
        caller = f"{entry.get('class', '?')}.{entry.get('method', '?')}"
        lines.append(f"| {_cell(caller)} | {_cell(entry.get('project'))} |")
    return lines


def _flow_boundary_table_lines(paths: list[dict]) -> list[str]:
    lines = ["| Flow ID | Terminal Type | Terminal Target |", "|---|---|---|"]
    for path in sorted(paths, key=lambda p: (p.get("flow_id") or "", p.get("path_id") or "")):
        lines.append(
            f"| {_cell(path.get('flow_id'))} | {_cell(path.get('terminal_type'))} "
            f"| {_cell(path.get('terminal_target'))} |"
        )
    return lines


def _first_evidence(entry: dict) -> str:
    evidence = entry.get("evidence") or []
    if not evidence:
        return ""
    first = evidence[0]
    file = first.get("file")
    line = first.get("line")
    if file and line:
        return f"{file}:{line}"
    return file or ""


def _truncate(value: object, limit: int = 120) -> str:
    text = "" if value is None else str(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _cell(value: object) -> str:
    """Escapes one value for a Markdown table cell: collapses newlines, escapes `|`."""
    if value is None or value == "":
        return "_none_"
    text = str(value).replace("\r\n", " ").replace("\n", " ").replace("|", "\\|")
    return text


def _code(value: object) -> str:
    """Wraps a value in an inline code span so path separators/underscores/asterisks render literally."""
    text = "" if value is None else str(value)
    return f"`{text}`" if text else "_none_"
