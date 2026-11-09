"""Compact synthetic baseline for the full-system interpretation tests (no source code, no analyzer, no provider)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ADAPTER = {"id": "vbnet-webforms-oracle", "version": "1.0"}


def _pid(name: str) -> str:
    return "PRJ-" + hashlib.sha256(name.encode()).hexdigest()


def _project(name: str, path: str, refs=(), output="Library") -> dict:
    return {"id": _pid(path), "kind": "Project", "name": name, "path": path, "adapter": ADAPTER,
            "extensions": {ADAPTER["id"]: {"root_namespace": f"Acme.{name}", "output_type": output,
                                           "project_references": [{"name": r} for r in refs]}}}


PROJECTS = [
    _project("WebAlpha", "web/WebAlpha.vbproj", ["blAlpha"], "WinExe"),
    _project("blAlpha", "bl/blAlpha.vbproj"),
    _project("Shared", "a/Shared.vbproj"),
    _project("Shared", "b/Shared.vbproj"),
    _project("blBeta", "bl/blBeta.vbproj", ["Shared"]),
    _project("EmptyLib", "lib/EmptyLib.vbproj"),
    _project("Orphan", "orphan/Orphan.vbproj"),
]
P = {p["path"]: p["id"] for p in PROJECTS}


def _solution(name: str, path: str, paths: list[str]) -> dict:
    return {"id": "SOL-" + hashlib.sha256(path.encode()).hexdigest(), "kind": "Solution", "name": name, "path": path,
            "project_refs": [P[x] for x in paths]}


def _path_solution(name: str, path: str, listed: list[str]) -> dict:
    """Real baselines list projects relative to the solution directory and carry no usable project ids."""
    return {"id": "SOL-" + hashlib.sha256(path.encode()).hexdigest(), "kind": "Solution", "name": name, "path": path, "adapter": ADAPTER,
            "project_refs": ["PRJ-unresolvable-" + str(i) for i in range(len(listed))],
            "extensions": {ADAPTER["id"]: {"projects": [{"name": x, "path": x} for x in listed]}}}


SOLUTIONS = [
    _solution("Alpha", "Alpha/Alpha.sln", ["web/WebAlpha.vbproj", "bl/blAlpha.vbproj", "a/Shared.vbproj"]),
    _path_solution("Beta", "Beta\\Beta.sln", ["..\\bl\\blBeta.vbproj", "..\\b\\Shared.vbproj", "..\\lib\\EmptyLib.vbproj"]),
]


def _flow(i: int, view: str, event: str, terminals: list[str]) -> dict:
    return {"id": f"FLOW-{i:010d}", "entry_point_id": f"EP-{i:010d}", "webform": f"web\\{view}.aspx", "event": event, "handler": f"{view}_{event}",
            "start_method": f"{view}.{event}", "terminal_operations": terminals, "has_confirmed_terminal": True, "has_unresolved_boundary": i % 2 == 0,
            "depth": 3, "project_sequence": ["web/WebAlpha.vbproj", "bl/blAlpha.vbproj"], "nodes": [], "edges": []}


FLOWS = [_flow(1, "Home", "Load", ["DAO-0000000001"]), _flow(2, "Home", "Click", ["DAO-0000000002"]), _flow(3, "Detail", "Load", ["DAO-0000000001"])]
DATA = [
    {"id": "DAO-0000000001", "operation_kind": "stored_procedure", "stored_procedure": "PKG_ALPHA.GET_ITEMS", "sql_operation": None,
     "class": "ItemsBl", "method": "Load", "project": "bl/blAlpha.vbproj", "dynamic_sql": False, "confidence": "confirmed"},
    {"id": "DAO-0000000002", "operation_kind": "sql", "stored_procedure": None, "sql_operation": "SELECT",
     "class": "ItemsBl", "method": "Find", "project": "bl/blAlpha.vbproj", "dynamic_sql": True, "confidence": "confirmed"},
]


def _xpc(i: int, src: str, tgt: str | None, status: str) -> dict:
    return {"id": f"XPC-{i:010d}", "kind": "CrossProjectCall", "source_symbol": f"Caller{i}.Do{i}", "target_symbol": f"Callee{i}.Run{i}" if tgt else None,
            "source_project": src, "target_project": tgt, "status": status}


XPC = [_xpc(1, "web/WebAlpha.vbproj", "bl/blAlpha.vbproj", "CONFIRMED"), _xpc(2, "web/WebAlpha.vbproj", "bl/blAlpha.vbproj", "CONFIRMED"),
       _xpc(3, "bl/blAlpha.vbproj", "a/Shared.vbproj", "INFERRED"), _xpc(4, "bl/blBeta.vbproj", "b/Shared.vbproj", "CONFIRMED"),
       _xpc(5, "bl/blBeta.vbproj", None, "UNRESOLVED")]
UI = [{"id": "UID-0000000001", "kind": "UiDocument", "logical_source_path": "web/Home.aspx"}]


def build_baseline(root: str | Path) -> Path:
    root = Path(root)
    ev = root / "evidence"
    ev.mkdir(parents=True, exist_ok=True)
    parts = {"solutions": SOLUTIONS, "projects": PROJECTS, "functional_flows": FLOWS, "data_access": DATA,
             "cross_project_calls": XPC, "ui_documents": UI}
    hashes = {}
    for name, value in parts.items():
        raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
        (ev / f"{name}.json").write_bytes(raw)
        hashes[name] = hashlib.sha256(raw).hexdigest()
    manifest = {"evidence_schema_version": "1.0", "partition_sha256": hashes, "entity_counts": {k: len(v) for k, v in parts.items()},
                "source_provenance": {"portable_evidence_sha256": "ab" * 32, "logical_snapshot_sha256": "cd" * 32}}
    (ev / "EVIDENCE_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root
