"""Deterministic Markdown renderers over already-produced in-memory analysis data.

Covers the technical views V4.2-R0 identified as missing from `MarkdownExporter`'s
existing six documents: web entry points, functional flows, database access, and
a consolidated unresolved-findings view. Every renderer here is a pure function
of the `indexes` dict `analyze_repository`/`full` already assembles -- no file is
re-read from disk, no LLM/provider is called, and nothing here infers a
relationship, business meaning, or schema fact that the deterministic analyzers
did not themselves discover (see docs/V4_2/V4_2_R3_DETERMINISTIC_TECHNICAL_DOCUMENTATION_RESULT.md).
"""
from __future__ import annotations


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

    def functional_flows(self, indexes: dict) -> str:
        """Renders FUNCTIONAL_FLOWS.md from `functional_flows`/`functional_paths`/`flow_summary`/`flow_unresolved`."""
        flows = indexes.get("functional_flows", [])
        paths_by_flow = _group_paths_by_flow(indexes.get("functional_paths", []))
        summary = indexes.get("flow_summary") or {}
        unresolved = indexes.get("flow_unresolved", [])

        lines = ["# Functional Flows", ""]
        lines.append(
            "A flow's top-level `Status`/`Confidence` are a worst-case aggregation across "
            "every traced execution path: a single unrelated unresolved call anywhere in the "
            "sequence downgrades them, even when another path in the same flow reached a "
            "real, `confirmed` database/stored-procedure terminal. Read `Confirmed terminal "
            "reached` alongside `Status` for the fact `Status` alone can hide: a flow can "
            "read `status: unresolved_boundary` and still have reached confirmed terminal "
            "evidence -- both facts are preserved independently, never one at the expense of "
            "the other."
        )
        lines.append("")
        if summary:
            lines.append("## Summary")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|---|---|")
            for key in sorted(summary):
                lines.append(f"| {_cell(key)} | {_cell(summary[key])} |")
            lines.append("")

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
            node_labels = _flow_node_labels(flow)
            lines.append(f"### {_code(flow.get('webform'))} → `{flow.get('event')}` → {_code(flow.get('handler'))}")
            lines.append("")
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
                continue
            for path in sorted(flow_paths, key=lambda p: p.get("path_id") or ""):
                lines.append(f"- {_render_path_chain(node_labels, path)}")
            lines.append("")

        if unresolved:
            lines.append("## Unresolved Boundaries")
            lines.append("")
            lines.append(
                "Execution paths that could not be traced to a confirmed stored procedure, "
                "SQL operation, or other resolved endpoint. Unresolved boundaries are preserved "
                "as unresolved -- they are never converted into an assumed call."
            )
            lines.append("")
            lines.append("| Flow | Terminal Type | Terminal Target | Confidence |")
            lines.append("|---|---|---|---|")
            flow_by_id = {f.get("id"): f for f in flows}
            for path in sorted(unresolved, key=lambda p: (p.get("flow_id") or "", p.get("path_id") or "")):
                flow = flow_by_id.get(path.get("flow_id"), {})
                flow_label = f"{flow.get('webform', '?')} / {flow.get('handler', '?')}"
                lines.append(
                    f"| {_cell(flow_label)} | {_cell(path.get('terminal_type'))} "
                    f"| {_cell(path.get('terminal_target'))} | {_cell(path.get('confidence'))} |"
                )
            lines.append("")

        return "\n".join(lines) + "\n"

    def database_access(self, indexes: dict) -> str:
        """Renders DATABASE_ACCESS.md from `data_access`/`stored_procedures`/`sql_operations`/`data_parameters`."""
        data_access = indexes.get("data_access", [])
        stored_procedures = indexes.get("stored_procedures", [])
        sql_operations = indexes.get("sql_operations", [])
        data_parameters = indexes.get("data_parameters", [])

        lines = ["# Database Access", ""]
        lines.append(
            f"Discovered {len(data_access)} database access operation(s), "
            f"{len(stored_procedures)} stored procedure reference(s), "
            f"{len(sql_operations)} SQL operation(s), and {len(data_parameters)} parameter(s)."
        )
        lines.append("")

        if not any((data_access, stored_procedures, sql_operations)):
            lines.append("No database access was discovered.")
            lines.append("")
            return "\n".join(lines) + "\n"

        if data_access:
            lines.append("## Access Points")
            lines.append("")
            lines.append("| Class.Method | Project | Operation Kind | Target | Confidence | Source |")
            lines.append("|---|---|---|---|---|---|")
            for entry in sorted(
                data_access, key=lambda e: (e.get("class") or "", e.get("method") or "", e.get("id") or "")
            ):
                target = entry.get("stored_procedure") or entry.get("sql_operation") or entry.get("command_text") or ""
                caller = f"{entry.get('class', '?')}.{entry.get('method', '?')}"
                lines.append(
                    f"| {_cell(caller)} | {_cell(entry.get('project'))} | {_cell(entry.get('operation_kind'))} "
                    f"| {_cell(target)} | {_cell(entry.get('confidence'))} | {_cell(_first_evidence(entry))} |"
                )
            lines.append("")

        if stored_procedures:
            lines.append("## Stored Procedures")
            lines.append("")
            lines.append("| Name | Package | Procedure | Confidence | Source |")
            lines.append("|---|---|---|---|---|")
            for proc in sorted(stored_procedures, key=lambda p: (p.get("name") or "", p.get("id") or "")):
                lines.append(
                    f"| {_cell(proc.get('name'))} | {_cell(proc.get('package'))} | {_cell(proc.get('procedure'))} "
                    f"| {_cell(proc.get('confidence'))} | {_cell(_first_evidence(proc))} |"
                )
            lines.append("")

        if sql_operations:
            lines.append("## SQL Operations")
            lines.append("")
            lines.append("| Operation | Command Text | Dynamic SQL | Confidence | Source |")
            lines.append("|---|---|---|---|---|")
            for op in sorted(sql_operations, key=lambda o: (o.get("operation") or "", o.get("id") or "")):
                lines.append(
                    f"| {_cell(op.get('operation'))} | {_cell(_truncate(op.get('command_text')))} "
                    f"| {_cell(op.get('dynamic_sql'))} | {_cell(op.get('confidence'))} | {_cell(_first_evidence(op))} |"
                )
            lines.append("")

        if data_parameters:
            lines.append("## Parameters")
            lines.append("")
            lines.append(
                "Grouped by caller; full detail (direction, type, size) is available in "
                "`index/data_parameters.json`."
            )
            lines.append("")
            by_caller: dict[str, list[str]] = {}
            for param in data_parameters:
                caller = f"{param.get('class', '?')}.{param.get('method', '?')}"
                by_caller.setdefault(caller, []).append(param.get("name") or "(unnamed)")
            lines.append("| Class.Method | Parameters |")
            lines.append("|---|---|")
            for caller in sorted(by_caller):
                names = ", ".join(_code(n) for n in sorted(set(by_caller[caller])))
                lines.append(f"| {_cell(caller)} | {names} |")
            lines.append("")

        return "\n".join(lines) + "\n"

    def unresolved_findings(self, indexes: dict) -> str:
        """Renders UNRESOLVED_FINDINGS.md: what LegacyMapper could not establish deterministically,
        consolidated across extraction errors, unresolved flow boundaries, and unresolved
        entry points/database access -- a cross-cutting view ANALYSIS_WARNINGS.md (extraction
        errors only) does not provide.
        """
        errors = indexes.get("errors", [])
        flow_unresolved = indexes.get("flow_unresolved", [])
        unresolved_entry_points = [e for e in indexes.get("entry_points", []) if e.get("confidence") != "confirmed"]
        unresolved_data_access = [d for d in indexes.get("data_access", []) if d.get("confidence") != "confirmed"]

        lines = ["# Unresolved Findings", ""]
        lines.append(
            "What LegacyMapper could not establish deterministically. Nothing in this document "
            "is an inferred fact -- every row here is an explicit gap in the evidence, preserved "
            "as unresolved rather than guessed."
        )
        lines.append("")
        lines.append("| Category | Count |")
        lines.append("|---|---|")
        lines.append(f"| Extraction errors | {len(errors)} |")
        lines.append(f"| Unresolved flow boundaries | {len(flow_unresolved)} |")
        lines.append(f"| Unresolved entry points | {len(unresolved_entry_points)} |")
        lines.append(f"| Unresolved database access | {len(unresolved_data_access)} |")
        lines.append("")

        if not any((errors, flow_unresolved, unresolved_entry_points, unresolved_data_access)):
            lines.append("No unresolved findings were recorded for this run.")
            lines.append("")
            return "\n".join(lines) + "\n"

        if errors:
            lines.append("## Extraction Errors")
            lines.append("")
            lines.append("| File | Extractor | Error |")
            lines.append("|---|---|---|")
            for error in sorted(errors, key=lambda e: (e.get("file") or "", e.get("extractor") or "")):
                lines.append(
                    f"| {_cell(error.get('file'))} | {_cell(error.get('extractor'))} | {_cell(error.get('error'))} |"
                )
            lines.append("")

        if flow_unresolved:
            lines.append("## Unresolved Flow Boundaries")
            lines.append("")
            lines.append("See `FUNCTIONAL_FLOWS.md` for full per-flow detail; summarized here:")
            lines.append("")
            lines.append("| Flow ID | Terminal Type | Terminal Target |")
            lines.append("|---|---|---|")
            for path in sorted(flow_unresolved, key=lambda p: (p.get("flow_id") or "", p.get("path_id") or "")):
                lines.append(
                    f"| {_cell(path.get('flow_id'))} | {_cell(path.get('terminal_type'))} "
                    f"| {_cell(path.get('terminal_target'))} |"
                )
            lines.append("")

        if unresolved_entry_points:
            lines.append("## Unresolved Entry Points")
            lines.append("")
            lines.append("See `WEB_ENTRY_POINTS.md` for full detail; summarized here:")
            lines.append("")
            lines.append(f"{len(unresolved_entry_points)} entry point(s) could not be resolved to a single confirmed handler.")
            lines.append("")

        if unresolved_data_access:
            lines.append("## Unresolved Database Access")
            lines.append("")
            lines.append("| Class.Method | Project |")
            lines.append("|---|---|")
            for entry in sorted(unresolved_data_access, key=lambda e: (e.get("class") or "", e.get("method") or "")):
                caller = f"{entry.get('class', '?')}.{entry.get('method', '?')}"
                lines.append(f"| {_cell(caller)} | {_cell(entry.get('project'))} |")
            lines.append("")

        return "\n".join(lines) + "\n"


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
