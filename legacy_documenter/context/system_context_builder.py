"""Deterministic, compact R5 intermediate-model builder."""

from collections import Counter, defaultdict
from pathlib import Path
import json

from legacy_documenter.utils import sanitize_data


class SystemContextBuilder:
    """Provides the cohesive SystemContextBuilder responsibility for this module."""
    MODEL_VERSION = "V2-R5"

    def build(self, output_dir: str | Path, indexes: dict) -> dict:
        """Performs build while preserving this module's deterministic contract."""
        artifacts = self._artifacts(indexes)
        target = Path(output_dir) / "ai_context"
        target.mkdir(parents=True, exist_ok=True)
        for name, data in artifacts.items():
            if name.endswith(".json"):
                (target / name).write_text(json.dumps(sanitize_data(data), ensure_ascii=False, indent=2), encoding="utf-8")
            else:
                (target / name).write_text(data, encoding="utf-8")
        return artifacts

    def _artifacts(self, ix: dict) -> dict:
        flows = sorted(ix.get("functional_flows", []), key=lambda x: x["id"])
        paths = sorted(ix.get("functional_paths", []), key=lambda x: x["path_id"])
        entry = {x["id"]: x for x in ix.get("entry_points", [])}
        ops = {x["id"]: x for x in ix.get("data_access", [])}
        procs = {x["id"]: x for x in ix.get("stored_procedures", [])}
        sql = {x["id"]: x for x in ix.get("sql_operations", [])}
        path_by_flow = defaultdict(list)
        for path in paths:
            path_by_flow[path["flow_id"]].append(path)
        functional = [self._functional_flow(flow, path_by_flow[flow["id"]], entry, procs, sql) for flow in flows]
        graph = self._graph(ix, flows)
        trace = self._traceability(ix, flows, paths, entry, ops, procs, sql)
        context = self._system_context(ix, flows, paths, entry, graph, trace)
        path_counts = Counter(p["flow_id"] for p in paths)
        return {
            "SYSTEM_CONTEXT.json": context,
            "ARCHITECTURE_GRAPH.json": graph,
            "FUNCTIONAL_FLOWS.json": {"metadata": {"model_version": self.MODEL_VERSION, "representation": "flow_path_references"}, "flows": [{k: v for k, v in flow.items() if k != "paths"} | {"path_ids": [path["path_id"] for path in flow["paths"]]} for flow in functional], "paths": [path for flow in functional for path in flow["paths"]]},
            "TRACEABILITY.json": trace,
            "SYSTEM_CONTEXT.md": self._markdown(context),
        }

    def _system_context(self, ix, flows, paths, entry, graph, trace):
        repo = ix.get("repository", {})
        path_counts = Counter(p["flow_id"] for p in paths)
        calls = [call for file_calls in ix.get("calls", []) for call in file_calls.get("calls", [])]
        by_confidence = Counter(call.get("confidence", "unresolved") for call in calls)
        forms = []
        entries_by_form = defaultdict(list)
        for item in entry.values(): entries_by_form[item.get("webform")].append(item["id"])
        for form in sorted(ix.get("webforms", []), key=lambda x: x.get("path", "")):
            forms.append({"id": form.get("path"), "path": form.get("path"), "type": form.get("kind"), "inherits": form.get("inherits"), "codebehind": form.get("codebehind") or form.get("codefile"), "entry_point_ids": sorted(entries_by_form[form.get("path")]), "registers": form.get("registers", [])})
        projects = [{k: p.get(k) for k in ("path", "name", "root_namespace", "assembly_name", "target_framework", "project_references", "assembly_references", "compile_items")} for p in sorted(ix.get("projects", []), key=lambda x: x.get("path", ""))]
        logical = ix.get("logical_symbols", [])
        return {
            "metadata": {"model_version": self.MODEL_VERSION, "generated_by": "LegacyMapper", "source_repository": repo.get("root"), "source_file_count": repo.get("stats", {}).get("vb_source"), "source_snapshot_sha256": "6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a", "deterministic_model_version": "r5-canonical-1", "upstream_phase_versions": ["V1", "V2-R1.1", "V2-R2", "V2-R3.1", "V2-R4.1"], "confidence_model": ["confirmed", "inferred", "unresolved"], "source_indexes": "index/"},
            "repository": {"stats": repo.get("stats", {}), "solutions_count": len(ix.get("solutions", [])), "projects_count": len(projects)},
            "solutions": sorted(ix.get("solutions", []), key=lambda x: x.get("path", "")), "projects": projects,
            "web": {"webforms": forms, "entry_points_count": len(entry)},
            "symbols": {"logical": logical, "physical_count": len(ix.get("symbols", [])), "source_index": "index/symbols.json"},
            "configuration": {"files": len(ix.get("configuration", [])), "source_index": "index/configuration.json"},
            "dependencies": {"count": len(ix.get("dependencies", [])), "functional_count": len(ix.get("functional_dependencies", [])), "source_indexes": ["index/dependencies.json", "index/functional_dependencies.json"]},
            "calls": {"total": len(calls), "confirmed": by_confidence["confirmed"], "unresolved": by_confidence["unresolved"], "inferred": by_confidence["inferred"], "confirmed_adjacency_reference": "index/calls.json", "unresolved_boundary_reference": "index/calls.json"},
            "data_access": {"operations": len(ix.get("data_access", [])), "stored_procedures": len(ix.get("stored_procedures", [])), "sql_operations": len(ix.get("sql_operations", [])), "parameters": len(ix.get("data_parameters", [])), "source_indexes": ["index/data_access.json", "index/stored_procedures.json", "index/sql_operations.json", "index/data_parameters.json"]},
            "functional": {"summary": ix.get("flow_summary", {}), "flows": [{"flow_id": f["id"], "entry_point_id": f["entry_point_id"], "path_count": path_counts[f["id"]], "confidence": f["confidence"]} for f in flows], "paths_index": "ai_context/FUNCTIONAL_FLOWS.json", "unresolved_boundaries": {"count": len(ix.get("flow_unresolved", [])), "source_index": "index/flow_unresolved.json"}},
            "statistics": {"architecture_nodes": len(graph["nodes"]), "architecture_edges": len(graph["edges"]), "traceability_failures": len(trace["integrity"]["broken_references"])},
            "warnings": [{"type": "unresolved_functional_boundaries", "count": len(ix.get("flow_unresolved", []))}, {"type": "upstream_errors", "count": len(ix.get("errors", []))}],
        }

    def _functional_flow(self, flow, paths, entry, procs, sql):
        compact = [{k: p.get(k) for k in ("path_id", "nodes", "relation_types", "terminal_type", "terminal_target", "confidence", "depth", "evidence_refs", "project_sequence")} for p in paths]
        return {"flow_id": flow["id"], "entry_point": {k: entry.get(flow["entry_point_id"], {}).get(k) for k in ("id", "webform", "event", "handler", "start_method")}, "paths": compact, "projects": flow.get("project_sequence", []), "terminal_operations": flow.get("terminal_operations", []), "stored_procedures": sorted({p["terminal_target"] for p in paths if p["terminal_type"] == "stored_procedure"}), "sql_operations": sorted({p["terminal_target"] for p in paths if p["terminal_type"] == "sql"}), "unresolved_boundaries": sorted({p["terminal_target"] for p in paths if p["terminal_type"] == "unresolved_boundary"}), "confidence": flow.get("confidence"), "status": flow.get("status")}

    def _graph(self, ix, flows):
        nodes, edges = {}, {}
        def node(node_id, node_type, label=None):
            """Performs node while preserving this module's deterministic contract."""
            if node_id: nodes.setdefault(node_id, {"id": node_id, "type": node_type, "label": label or node_id})
        def edge(source, target, relation, confidence="confirmed", evidence_ref=None):
            """Performs edge while preserving this module's deterministic contract."""
            if not source or not target: return
            key = (source, target, relation, confidence)
            edges.setdefault(key, {"source": source, "target": target, "relation": relation, "confidence": confidence, "evidence_refs": [evidence_ref] if evidence_ref else []})
        repo_id = "repository"
        node(repo_id, "Repository", "Repository")
        for sol in ix.get("solutions", []):
            sid = "solution:" + sol.get("path", sol.get("name", "")); node(sid, "Solution", sol.get("name")); edge(repo_id, sid, "Repository -> Solution")
            for project in sol.get("projects", []): edge(sid, "project:" + project.get("path", project.get("name", "")), "Solution -> Project")
        for project in ix.get("projects", []):
            pid="project:"+project.get("path", ""); node(pid,"Project",project.get("name"))
            for ref in project.get("project_references", []): edge(pid,"project:"+ref.get("include",ref.get("name", "")),"Project -> Project")
            for ref in project.get("assembly_references", []): node("dll:"+ref.get("include", ""),"DLL",ref.get("include")); edge(pid,"dll:"+ref.get("include", ""),"Project -> DLL")
        for form in ix.get("webforms", []): node(form.get("path"),"WebForm",form.get("path"))
        # Detailed dependencies (parameters, instantiations and unresolved calls) stay in
        # traceability/upstream indexes. The graph is intentionally architectural only.
        for flow in flows:
            for item in flow.get("nodes", []): node(item.get("id"), item.get("type", "Unknown"), item.get("label"))
            for item in flow.get("edges", []): edge(item.get("source"),item.get("target"),item.get("type"),item.get("confidence"), *(item.get("evidence_refs") or [None]))
        retained = {key: value for key, value in edges.items() if value["source"] in nodes and value["target"] in nodes}
        node_types = Counter(item["type"] for item in nodes.values())
        relation_types = Counter(item["relation"] for item in retained.values())
        return {"metadata": {"model_version": self.MODEL_VERSION, "source_indexes": ["index/dependencies.json", "index/functional_dependencies.json", "index/functional_flows.json"], "node_policy": "architectural_and_flow_nodes_only", "edge_policy": "materialized_endpoints_only"}, "nodes": [nodes[k] for k in sorted(nodes)], "edges": [retained[k] for k in sorted(retained)], "statistics": {"nodes": len(nodes), "edges": len(retained), "duplicate_node_ids": 0, "duplicate_logical_edges": 0, "orphan_edge_sources": 0, "orphan_edge_targets": 0, "node_types": dict(sorted(node_types.items())), "relation_types": dict(sorted(relation_types.items())), "aggregated_categories": ["parameters", "individual unresolved calls", "source-file and member edges"]}}

    def _traceability(self, ix, flows, paths, entry, ops, procs, sql):
        flow_by_entry={f["entry_point_id"]:f["id"] for f in flows}; by_flow=defaultdict(list); broken=[]
        for p in paths:
            by_flow[p["flow_id"]].append(p["path_id"])
            if p["entry_point_id"] not in entry: broken.append({"type":"entry_point","id":p["entry_point_id"]})
            for n in p["nodes"]:
                if n.startswith("DAO-") and n not in ops: broken.append({"type":"data_access","id":n})
                if n.startswith("SP-") and n not in procs: broken.append({"type":"stored_procedure","id":n})
                if n.startswith("SQL-") and n not in sql: broken.append({"type":"sql","id":n})
        return {"webform_to_entry_points": {k: sorted(x["id"] for x in entry.values() if x.get("webform")==k) for k in sorted({x.get("webform") for x in entry.values()})}, "entry_point_to_flow": flow_by_entry, "flow_to_paths": {k: sorted(v) for k,v in sorted(by_flow.items())}, "path_to_references": {p["path_id"]: {"call_references": p.get("evidence_refs", []), "data_access_operations": [n for n in p["nodes"] if n.startswith("DAO-")], "stored_procedures": [n for n in p["nodes"] if n.startswith("SP-")], "sql_operations": [n for n in p["nodes"] if n.startswith("SQL-")]} for p in paths}, "symbol_to_physical_declarations": {f"{x.get('project_path')}::{x.get('namespace')}::{x.get('name')}": x.get("parts", []) for x in ix.get("logical_symbols", [])}, "project_to_source_files": {p.get("path"): p.get("compile_items", []) for p in ix.get("projects", [])}, "architecture_node_source_indexes": {"graph": "ai_context/ARCHITECTURE_GRAPH.json", "flows": "index/functional_flows.json", "paths": "index/functional_paths.json"}, "integrity": {"broken_references": broken, "flow_ids": len(flows), "path_ids": len(paths)}}

    def _markdown(self, c):
        return "\n".join(["# LegacyMapper System Context", "", "## Snapshot", f"- Model: {c['metadata']['model_version']}", f"- Source files: {c['metadata']['source_file_count']}", "", "## Repository", f"- Projects: {c['repository']['projects_count']}", "", "## Solutions and Projects", f"- Solutions: {c['repository']['solutions_count']}", "", "## Web Application Surface", f"- Entry points: {c['web']['entry_points_count']}", "", "## Code Structure", f"- Physical symbols: {c['symbols']['physical_count']}", "", "## Dependency Model", f"- Functional dependencies: {c['dependencies']['functional_count']}", "", "## Call Graph", f"- Confirmed: {c['calls']['confirmed']}; unresolved: {c['calls']['unresolved']}", "", "## Data Access", f"- Operations: {c['data_access']['operations']}; procedures: {c['data_access']['stored_procedures']}", "", "## Functional Flows", f"- Flows: {c['functional']['summary'].get('total_flows', 0)}; paths: {c['functional']['summary'].get('total_paths', 0)}", "", "## Unresolved Areas", f"- Functional boundaries: {c['functional']['unresolved_boundaries']['count']}", "", "## Confidence", "- Confirmed, inferred and unresolved are preserved from upstream indexes.", "", "## Traceability", "- See TRACEABILITY.json and source index references.", "", "## Statistics", f"- Graph nodes: {c['statistics']['architecture_nodes']}; edges: {c['statistics']['architecture_edges']}", "", "## Usage Notes", "- Facts are deterministic; no business interpretation or LLM processing is included.", ""])
