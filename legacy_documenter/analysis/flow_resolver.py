from collections import defaultdict


class FunctionalFlowResolver:
    def __init__(self, max_depth: int = 12) -> None:
        self.max_depth = max_depth

    def resolve(
        self,
        entry_points: list[dict],
        calls: list[dict],
        data_access: list[dict],
        stored_procedures: list[dict],
        sql_operations: list[dict],
        dependencies: list[dict],
        errors: list[dict] | None = None,
    ) -> tuple[list[dict], list[dict], dict, list[dict]]:
        self.method_calls, self.unresolved_calls = self._index_calls(calls)
        self.data_by_method = self._index_data_access(data_access)
        self.proc_by_operation, self.sql_by_operation = self._index_terminals(dependencies, stored_procedures, sql_operations)
        flows = []
        all_paths: dict[tuple, dict] = {}
        unresolved = []

        for entry in entry_points:
            if entry.get("confidence") != "confirmed" or not entry.get("handler_method"):
                continue
            start = self._entry_method_key(entry)
            if not start:
                continue
            flow_id = self._stable_id("FLOW", entry.get("id"), entry.get("handler_method"))
            path_bucket: dict[tuple, dict] = {}
            graph_nodes: dict[str, dict] = {}
            graph_edges: dict[tuple, dict] = {}
            self._add_node(graph_nodes, self._node("WebForm", entry.get("webform"), entry.get("webform")))
            event_node = f"{entry.get('webform')}::{entry.get('control') or '<page>'}.{entry.get('event')}"
            self._add_node(graph_nodes, self._node("Event", event_node, event_node))
            handler_node = f"handler::{entry.get('handler')}"
            self._add_node(graph_nodes, self._node("Handler", handler_node, entry.get("handler")))
            self._add_edge(graph_edges, entry.get("webform"), event_node, "WebForm -> Event", entry.get("confidence"), entry.get("id"))
            self._add_edge(graph_edges, event_node, handler_node, "Event -> Handler", entry.get("confidence"), entry.get("id"))
            self._add_edge(graph_edges, handler_node, self._method_label(start), "Handler -> Method", entry.get("confidence"), entry.get("id"))
            self._walk(entry, start, [self._method_label(start)], [], graph_nodes, graph_edges, path_bucket)
            paths = list(path_bucket.values())
            flow_confidence = "unresolved" if any(path["confidence"] != "confirmed" for path in paths) else "confirmed"
            status = self._flow_status(paths)
            terminal_ops = sorted({p["terminal_target"] for p in paths if p["terminal_type"] in {"stored_procedure", "sql", "data_operation"}})
            flow = {
                "id": flow_id,
                "entry_point_id": entry.get("id"),
                "webform": entry.get("webform"),
                "event": entry.get("event"),
                "handler": entry.get("handler"),
                "start_method": entry.get("handler_method"),
                "nodes": list(graph_nodes.values()),
                "edges": list(graph_edges.values()),
                "terminal_operations": terminal_ops,
                "confidence": flow_confidence,
                "status": status,
                "depth": max((path["depth"] for path in paths), default=0),
                "project_sequence": self._project_sequence(paths),
                "evidence": [{"entry_point_id": entry.get("id")}],
            }
            flows.append(flow)
            for path in paths:
                path["flow_id"] = flow_id
                all_paths[(path["path_id"], flow_id)] = path
            unresolved.extend(path for path in paths if path["terminal_type"] in {"external_boundary", "unresolved_boundary", "cycle", "truncated_depth"})

        path_list = list(all_paths.values())
        summary = self._summary(entry_points, flows, path_list, errors or [])
        return flows, path_list, summary, unresolved

    def _walk(self, entry, method_key, node_path, edge_refs, graph_nodes, graph_edges, paths) -> None:
        method_label = self._method_label(method_key)
        self._add_node(graph_nodes, self._node("Method", method_label, method_label, method_key[0]))
        if len(node_path) > self.max_depth:
            self._add_path(paths, entry, node_path, "truncated_depth", method_label, "unresolved", edge_refs)
            return
        data_ops = self.data_by_method.get(method_key, [])
        for operation in data_ops:
            op_id = operation.get("id")
            self._add_node(graph_nodes, self._node("DataAccessOperation", op_id, op_id, operation.get("project")))
            self._add_edge(graph_edges, method_label, op_id, "Method -> DataAccessOperation", operation.get("confidence", "confirmed"), op_id)
            terminal_nodes = self._terminal_nodes(operation)
            if terminal_nodes:
                for terminal_type, terminal_id, confidence in terminal_nodes:
                    node_type = "StoredProcedure" if terminal_type == "stored_procedure" else "SQL"
                    self._add_node(graph_nodes, self._node(node_type, terminal_id, terminal_id))
                    edge_type = "DataAccessOperation -> StoredProcedure" if terminal_type == "stored_procedure" else "DataAccessOperation -> SQL"
                    self._add_edge(graph_edges, op_id, terminal_id, edge_type, confidence, op_id)
                    self._add_path(paths, entry, node_path + [op_id, terminal_id], terminal_type, terminal_id, self._weakest([operation.get("confidence"), confidence]), edge_refs + [op_id])
            else:
                self._add_path(paths, entry, node_path + [op_id], "data_operation", op_id, operation.get("confidence", "confirmed"), edge_refs + [op_id])

        followed = False
        for call in self.method_calls.get(method_key, []):
            target_key = self._resolved_method_key(call)
            call_ref = self._call_ref(call)
            if not target_key:
                continue
            target_label = self._method_label(target_key)
            self._add_node(graph_nodes, self._node("Method", target_label, target_label, call.get("resolved_project")))
            self._add_edge(graph_edges, method_label, target_label, "Method -> Method", call.get("confidence", "confirmed"), call_ref)
            if target_label in node_path:
                self._add_path(paths, entry, node_path + [target_label], "cycle", target_label, "unresolved", edge_refs + [call_ref])
                followed = True
                continue
            followed = True
            self._walk(entry, target_key, node_path + [target_label], edge_refs + [call_ref], graph_nodes, graph_edges, paths)

        for call in self.unresolved_calls.get(method_key, []):
            boundary_id = self._stable_id("UNRES", self._call_ref(call), call.get("expression"))
            self._add_node(graph_nodes, self._node("UnresolvedCall", boundary_id, call.get("expression")))
            self._add_edge(graph_edges, method_label, boundary_id, "Method -> UnresolvedCall", "unresolved", self._call_ref(call))
            self._add_path(paths, entry, node_path + [boundary_id], "unresolved_boundary", call.get("expression") or boundary_id, "unresolved", edge_refs + [self._call_ref(call)])
            followed = True

        if not data_ops and not followed:
            self._add_path(paths, entry, node_path, "dead_end", method_label, "confirmed", edge_refs)

    def _index_calls(self, calls: list[dict]) -> tuple[dict[tuple, list[dict]], dict[tuple, list[dict]]]:
        confirmed = defaultdict(list)
        unresolved = defaultdict(list)
        for file_calls in calls:
            file_name = file_calls.get("file")
            for call in file_calls.get("calls", []):
                key = self._method_key(call.get("containing_class"), call.get("containing_method"), None)
                if not key:
                    continue
                item = {**call, "file": file_name}
                if call.get("confidence") == "confirmed" and call.get("resolved_target"):
                    confirmed[key].append(item)
                elif call.get("confidence") == "unresolved":
                    unresolved[key].append(item)
        return confirmed, unresolved

    def _index_data_access(self, data_access: list[dict]) -> dict[tuple, list[dict]]:
        result = defaultdict(list)
        for operation in data_access:
            key = self._method_key(operation.get("class"), operation.get("method"), operation.get("project"))
            if key:
                result[key].append(operation)
                result[(key[0], key[1], None)].append(operation)
        return result

    def _index_terminals(self, dependencies: list[dict], stored: list[dict], sql: list[dict]) -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
        stored_ids = {item["id"]: item for item in stored}
        sql_ids = {item["id"]: item for item in sql}
        proc_by_op = defaultdict(list)
        sql_by_op = defaultdict(list)
        for dep in dependencies:
            if dep.get("dependency_type") == "DataAccessOperation -> StoredProcedure" and dep.get("target") in stored_ids:
                proc_by_op[dep["source"]].append(stored_ids[dep["target"]])
            elif dep.get("dependency_type") == "DataAccessOperation -> SQL" and dep.get("target") in sql_ids:
                sql_by_op[dep["source"]].append(sql_ids[dep["target"]])
        return proc_by_op, sql_by_op

    def _terminal_nodes(self, operation: dict) -> list[tuple[str, str, str]]:
        result = []
        for proc in self.proc_by_operation.get(operation.get("id"), []):
            result.append(("stored_procedure", proc.get("id"), proc.get("confidence", "confirmed")))
        for sql in self.sql_by_operation.get(operation.get("id"), []):
            result.append(("sql", sql.get("id"), sql.get("confidence", "confirmed")))
        if not result and operation.get("stored_procedure"):
            result.append(("stored_procedure", operation["stored_procedure"], operation.get("confidence", "confirmed")))
        if not result and operation.get("sql_operation"):
            result.append(("sql", operation.get("id"), operation.get("confidence", "confirmed")))
        return result

    def _entry_method_key(self, entry: dict) -> tuple | None:
        handler_method = entry.get("handler_method") or ""
        if "." not in handler_method:
            return None
        class_name, method = handler_method.rsplit(".", 1)
        return self._method_key(class_name, method, entry.get("project"))

    def _resolved_method_key(self, call: dict) -> tuple | None:
        target = call.get("resolved_target") or ""
        parts = target.split(".")
        if len(parts) < 2:
            return None
        return self._method_key(parts[-2], parts[-1], call.get("resolved_project"))

    def _method_key(self, class_name: str | None, method: str | None, project: str | None) -> tuple | None:
        if not class_name or not method:
            return None
        return (class_name.lower(), method.lower(), project)

    def _method_label(self, key: tuple) -> str:
        return f"{key[2] or '<unknown>'}::{key[0]}.{key[1]}"

    def _node(self, node_type: str, node_id: str | None, label: str | None, project: str | None = None) -> dict:
        return {"id": node_id or "", "type": node_type, "label": label or node_id or "", "project": project}

    def _add_node(self, nodes: dict[str, dict], node: dict) -> None:
        if node["id"]:
            nodes.setdefault(node["id"], node)

    def _add_edge(self, edges: dict[tuple, dict], source: str | None, target: str | None, edge_type: str, confidence: str | None, evidence_ref: str | None) -> None:
        if not source or not target:
            return
        key = (source, target, edge_type, evidence_ref)
        edges.setdefault(key, {"source": source, "target": target, "type": edge_type, "confidence": confidence or "confirmed", "evidence_refs": [evidence_ref] if evidence_ref else []})

    def _add_path(self, paths: dict[tuple, dict], entry: dict, nodes: list[str], terminal_type: str, terminal_target: str, confidence: str, evidence_refs: list[str]) -> None:
        key = (entry.get("id"), tuple(nodes), terminal_type, terminal_target)
        if key in paths:
            return
        paths[key] = {
            "flow_id": None,
            "path_id": self._stable_id("PATH", *key),
            "entry_point_id": entry.get("id"),
            "nodes": nodes,
            "terminal_type": terminal_type,
            "terminal_target": terminal_target,
            "confidence": confidence,
            "depth": max(0, len(nodes) - 1),
            "evidence_refs": [ref for ref in evidence_refs if ref],
            "project_sequence": self._project_sequence_from_nodes(nodes),
        }

    def _call_ref(self, call: dict) -> str:
        evidence = call.get("evidence") or {}
        return self._stable_id("CALL", call.get("file"), evidence.get("line"), call.get("expression"), call.get("resolved_target"))

    def _weakest(self, confidences: list[str | None]) -> str:
        return "unresolved" if any(item == "unresolved" for item in confidences) else "confirmed"

    def _flow_status(self, paths: list[dict]) -> str:
        if not paths:
            return "dead_end"
        order = ["truncated_depth", "cycle", "unresolved_boundary", "data_endpoint", "dead_end"]
        statuses = {p["terminal_type"] if p["terminal_type"] in {"truncated_depth", "cycle", "unresolved_boundary", "dead_end"} else "data_endpoint" for p in paths}
        return next(status for status in order if status in statuses)

    def _project_sequence(self, paths: list[dict]) -> list[str]:
        result = []
        for path in paths:
            for project in path.get("project_sequence", []):
                if project not in result:
                    result.append(project)
        return result

    def _project_sequence_from_nodes(self, nodes: list[str]) -> list[str]:
        result = []
        for node in nodes:
            if "::" not in node:
                continue
            project = node.split("::", 1)[0]
            if project != "<unknown>" and project not in result:
                result.append(project)
        return result

    def _summary(self, entries: list[dict], flows: list[dict], paths: list[dict], errors: list[dict]) -> dict:
        terminal_counts = defaultdict(int)
        for path in paths:
            terminal_counts[path["terminal_type"]] += 1
        return {
            "total_entry_points_considered": len([e for e in entries if e.get("confidence") == "confirmed"]),
            "entry_points_with_flows": len(flows),
            "total_flows": len(flows),
            "total_paths": len(paths),
            "paths_to_stored_procedure": terminal_counts["stored_procedure"],
            "paths_to_sql": terminal_counts["sql"],
            "paths_to_data_operation": terminal_counts["data_operation"],
            "unresolved_boundaries": terminal_counts["unresolved_boundary"],
            "external_boundaries": terminal_counts["external_boundary"],
            "dead_end_paths": terminal_counts["dead_end"],
            "cycle_paths": terminal_counts["cycle"],
            "truncated_paths": terminal_counts["truncated_depth"],
            "unique_terminal_stored_procedures": len({p["terminal_target"] for p in paths if p["terminal_type"] == "stored_procedure"}),
            "unique_terminal_sql_operations": len({p["terminal_target"] for p in paths if p["terminal_type"] == "sql"}),
            "cross_project_flows": len([f for f in flows if len(f.get("project_sequence", [])) > 1]),
            "max_observed_depth": max((p["depth"] for p in paths), default=0),
            "average_path_depth": round(sum(p["depth"] for p in paths) / len(paths), 3) if paths else 0,
            "errors": len(errors),
        }

    def _stable_id(self, prefix: str, *parts: object) -> str:
        raw = "|".join("" if part is None else str(part) for part in parts)
        value = 0
        for char in raw:
            value = (value * 33 + ord(char)) % 1000000007
        return f"{prefix}-{value:010d}"
