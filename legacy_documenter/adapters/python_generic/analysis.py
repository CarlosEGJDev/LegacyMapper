"""python-generic data-operation, dependency and flow projection.

File-system operations are the data boundary this adapter can establish statically (`DataAccessOperation` records in the
common index shape). Flows reuse the technology-neutral traversal; this module only prepares normalized facts for it.
"""
from __future__ import annotations

from pathlib import PurePosixPath

from legacy_documenter.analysis._neutral_graph import node
from legacy_documenter.analysis.normalized_flow import NormalizedFlowResolver
from legacy_documenter.evidence.identity import poly33_id

from .extraction import _project_by_file


def resolve_database(groups: list[dict], projects: list[dict]) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict]]:
    """File operations -> `DAO-` records; no stored procedures, SQL or parameters exist in this boundary."""
    owner = _project_by_file(projects)
    records: list[dict] = []
    dependencies: list[dict] = []
    seen: dict[tuple, int] = {}
    for group in groups:
        project = owner.get(group["file"].replace("\\", "/"))
        for op in group["operations"]:
            parts = (group["file"], op["line"], op["operation_kind"], op["expression"])
            ordinal = seen[parts] = seen.get(parts, -1) + 1
            op_id = poly33_id("DAO", *parts, ordinal or None)
            evidence = [{"file": group["file"], "line": op["line"], "expression": op["expression"], "class_name": op["class"],
                         "method": op["method"], "project": project}]
            records.append({
                "id": op_id, "operation_kind": op["operation_kind"], "access_kind": "filesystem", "provider": op["provider"],
                "command_variable": None, "command_type": "file", "command_text": None, "stored_procedure": None, "sql_operation": None,
                "connection": None, "connection_name": None, "dynamic_sql": False, "class": op["class"], "method": op["method"],
                "project": project, "confidence": op["confidence"], "evidence": evidence,
            })
            dependencies.append({"source": f"{op['class']}.{op['method']}", "target": op_id, "dependency_type": "Method -> DataAccessOperation",
                                 "source_file": group["file"], "evidence": op["expression"], "confidence": op["confidence"],
                                 "evidence_samples": [op["expression"]], "evidence_count": 1})
    return sorted(records, key=lambda r: r["id"]), [], [], [], dependencies


def resolve_dependencies(projects: list[dict]) -> list[dict]:
    """Project -> Project / Project -> DLL (third-party package) / Project -> SourceFile, in the common dependency shape."""
    result = []
    for project in projects:
        base = PurePosixPath(project["path"].replace("\\", "/")).parent
        for ref in project["project_references"]:
            result.append({"source": project["path"], "target": ref["include"], "dependency_type": "Project -> Project",
                           "source_file": project["path"], "evidence": ref["name"], "confidence": "confirmed"})
        for ref in project["assembly_references"]:
            result.append({"source": project["path"], "target": ref["include"], "dependency_type": "Project -> DLL",
                           "source_file": project["path"], "evidence": ref["include"], "confidence": "confirmed"})
        for item in project["compile_items"]:
            result.append({"source": project["path"], "target": item, "dependency_type": "Project -> SourceFile",
                           "source_file": str(base / item.replace("\\", "/")), "evidence": item, "confidence": "confirmed"})
    return result


class PythonFlowResolver(NormalizedFlowResolver):
    """Projects Python entry/call/file-operation facts into the neutral traversal; labels stay in this adapter."""

    def resolve(self, entry_points, calls, data_access, stored_procedures, sql_operations, dependencies, errors=None):
        entries = []
        for entry in entry_points:
            handler_method = entry.get("handler_method") or ""
            owner, _, member = handler_method.rpartition(".")
            start = (owner.lower(), member.lower(), entry.get("project")) if owner and member else None
            source, event, handler = entry.get("webform"), f"{entry.get('webform')}::{entry.get('event')}", f"handler::{entry.get('handler')}"
            label = self._method_label(start) if start else None
            entries.append({
                "id": entry.get("id"), "confidence": entry.get("confidence"), "start_ref": handler_method or None, "method_key": start,
                "source_ref": source, "trigger_label": entry.get("event"), "handler_ref": entry.get("handler"),
                "initial_nodes": [node("Module", source, source), node("EntryPoint", event, event), node("Handler", handler, entry.get("handler"))],
                "initial_edges": [{"source": a, "target": b, "type": kind, "confidence": entry.get("confidence"), "evidence_ref": entry.get("id")}
                                  for a, b, kind in [(source, event, "Module -> EntryPoint"), (event, handler, "EntryPoint -> Handler"), (handler, label, "Handler -> Method")]],
            })
        normalized = []
        for group in calls:
            records = []
            for call in group.get("calls", []):
                target = (call["resolved_owner"].lower(), call["resolved_member"].lower(), call.get("resolved_project")) if call.get("resolved_owner") else None
                records.append({
                    "owner_symbol": (call.get("containing_class") or "").lower(), "owner_member": (call.get("containing_method") or "").lower(),
                    "confidence": call.get("confidence") if call.get("resolution_kind") != "external" else "external",
                    "resolved_target": call.get("resolved_target"), "resolved_project": call.get("resolved_project"), "target_key": target,
                    "expression": call.get("expression"),
                    "call_reference": poly33_id("CALL", group.get("file"), (call.get("evidence") or {}).get("line"), call.get("expression"), call.get("resolved_target")),
                })
            normalized.append({"file": group.get("file"), "calls": records})
        operations = [{"owner_symbol": (op.get("class") or "").lower(), "owner_member": (op.get("method") or "").lower(),
                       **{k: op[k] for k in ("id", "project", "stored_procedure", "sql_operation", "confidence") if k in op}} for op in data_access]
        flows, paths, summary, unresolved = super().resolve(entries, normalized, operations, [], [], [], errors)
        aliases = {"source_ref": "webform", "trigger_label": "event", "handler_ref": "handler", "start_ref": "start_method"}
        return [{aliases.get(k, k): v for k, v in flow.items()} for flow in flows], paths, summary, unresolved

    def _entry_method_key(self, entry):
        return entry.get("method_key")

    def _resolved_method_key(self, call):
        return call.get("target_key")

    def _call_ref(self, call):
        return call["call_reference"]
