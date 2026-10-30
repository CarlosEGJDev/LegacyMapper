"""Behavioral context package (post-V5 H4-R4): per-view evidence assembled ONLY from the persisted baseline.

Deterministic. Gate B: UI structure, code-behind facts, navigation, messages, parameters, styles and assets come from the persisted
UI Evidence (`evidence/ui_*.json`); the source repository is neither a parameter nor a fallback. Every fact carries a reference that
`validate.ReferenceIndex` can resolve: baseline ids (`EP-`, `FLOW-`, `DAO-`, `CALL-`), procedure names, and
`src:<relative file>:<line>` for source-level facts (line ranges are validated against the persisted line counts).
"""
from __future__ import annotations

import json
import posixpath
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from legacy_documenter.documentation_v52.audience import classify_target

from .source import CodeFacts, NavHit
from .ui_evidence import UiEvidence, load_cross_project_calls, load_ui_evidence

VIEW_EXT = (".ascx", ".aspx")


def norm_path(p: str) -> str:
    return str(p or "").replace("/", "\\").lower()


def short_label(node: dict) -> str:
    label = str(node.get("label") or node.get("id") or "")
    return label.split("::")[-1] if "::" in label else label


@dataclass
class EventEvidence:
    ep_id: str
    control: str
    event: str
    handler: str
    handler_method: str
    kind: str                           # web_event | web_lifecycle
    confidence: str
    flow_id: str = ""
    chains: list[list[dict]] = field(default_factory=list)       # confirmed chains from the event to leaves
    data_ops: list[dict] = field(default_factory=list)           # {dao_id, class, method, procedure, effect}
    unresolved: list[dict] = field(default_factory=list)         # {label, from, refs}
    line: int = 0
    file: str = ""


@dataclass
class ViewEvidence:
    path: str
    name: str
    codebehind: str
    inherits: str
    events: list[EventEvidence] = field(default_factory=list)
    markup: object | None = None
    code: CodeFacts | None = None
    markup_file: str = ""
    code_file: str = ""
    incoming: list[NavHit] = field(default_factory=list)
    outgoing: list[NavHit] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def solution_has_project(solution: dict, project_path: str) -> bool:
    """Whether a persisted solution record lists the project file (shared by the explainer and the selection rule)."""
    blob = json.dumps(solution.get("projects") or solution, ensure_ascii=False).lower()
    return project_path.lower().replace("\\", "\\\\") in blob or project_path.lower() in blob


class BehaviorContext:
    """Everything the explainer reads. Built once per project from a loaded `VisualContext` and the persisted UI Evidence."""

    def __init__(self, ctx, baseline_dir: Path, project_name: str, ui: UiEvidence | None = None) -> None:
        self.ctx, self.baseline_dir = ctx, Path(baseline_dir)
        self.ui = ui if ui is not None else load_ui_evidence(self.baseline_dir)
        src = ctx.source
        self.project = next(p for p in src["projects"] if p.get("name") == project_name)
        self.project_path = str(self.project["path"])
        self.project_dir = posixpath.dirname(self.project_path.replace("\\", "/"))
        self.solutions = [s for s in src["solutions"] if self._solution_has_project(s)]
        self.webforms = {norm_path(w["path"]): w for w in src["webforms"]}
        self.eps_by_webform: dict[str, list[dict]] = defaultdict(list)
        for ep in src["entry_points"]:
            self.eps_by_webform[norm_path(ep.get("webform"))].append(ep)
        self.flows_by_ep = {f.get("entry_point_id"): f for f in src["functional_flows"]}
        self.dao = {d["id"]: d for d in src["data_access"]}
        self.known_refs: set[str] = set()
        self.view_paths = self._project_views()
        self.files = json.loads((self.baseline_dir / "index" / "files.json").read_text(encoding="utf-8"))
        self.rel_files = [f["relative_path"] for f in self.files]
        self._nav: list[NavHit] | None = None
        self.cross_project_calls = load_cross_project_calls(self.baseline_dir)   # persisted Gate C resolutions (no source involved)
        self.source_reads = 0                      # contract: stays 0; no code path of this class opens a source file
        self._views: dict[str, ViewEvidence] = {}
        self._styles = None

    # ---- project membership (explicit: the project file's content items)
    def _solution_has_project(self, solution: dict) -> bool:
        return solution_has_project(solution, self.project_path)

    def _project_views(self) -> list[str]:
        items = list(self.project.get("content_items") or []) + list(self.project.get("compile_items") or [])
        base = self.project_dir.replace("/", "\\")
        views = sorted({(base + "\\" if base else "") + str(i).replace("/", "\\") for i in items if str(i).lower().endswith(VIEW_EXT)}, key=str.lower)
        return views

    @property
    def styles(self):
        """Stylesheet evidence linked by the shell page (persisted); empty catalog when none is declared."""
        if self._styles is None:
            self._styles = self.ui.style_catalog()
        return self._styles

    # ---- navigation (repo-wide literals persisted at analysis time)
    @property
    def navigation(self) -> list[NavHit]:
        if self._nav is None:
            self._nav = self.ui.navigation_hits()
        return self._nav

    def view_folder_and_name(self, path: str) -> tuple[str, str]:
        p = path.replace("\\", "/")
        folder, _, leaf = p.rpartition("/")
        return folder.rpartition("/")[2] if folder else "", leaf.rsplit(".", 1)[0]

    # ---- per-view evidence
    def view(self, path: str) -> ViewEvidence:
        key = norm_path(path)
        if key in self._views:
            return self._views[key]
        web = self.webforms.get(key, {})
        ev = ViewEvidence(path=path, name=path.replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0],
                          codebehind=str(web.get("codebehind") or ""), inherits=str(web.get("inherits") or ""))
        markup_rel = path
        doc = self.ui.document(path)
        cb_rel = path + ".vb"
        if doc is not None:
            ev.markup_file = markup_rel
            ev.markup = self.ui.markup(doc)
            if doc["properties"].get("code_behind"):
                ev.code_file = cb_rel
                ev.code = self.ui.code_facts(doc, cb_rel)
        if ev.code is None:
            ev.notes.append("code-behind no encontrado en el origen")
        for ep in self.eps_by_webform.get(key, []):
            ev.events.append(self._event(ep))
        ev.events.sort(key=lambda e: (e.kind != "web_lifecycle", e.line, e.event, e.handler))
        folder, name = self.view_folder_and_name(path)
        for hit in self.navigation:
            if hit.view.lower() == name.lower() and (not folder or hit.folder.lower() == folder.lower()):
                ev.incoming.append(hit)
            if hit.file.replace("/", "\\").lower() in (markup_rel.lower(), cb_rel.lower()):
                ev.outgoing.append(hit)
        self._views[key] = ev
        return ev

    def _event(self, ep: dict) -> EventEvidence:
        evid = (ep.get("evidence") or [{}])[0]
        e = EventEvidence(ep_id=ep["id"], control=str(ep.get("control") or ""), event=str(ep.get("event") or ""), handler=str(ep.get("handler") or ""),
                          handler_method=str(ep.get("handler_method") or ""), kind=str(ep.get("type") or ""), confidence=str(ep.get("confidence") or ""),
                          line=int(evid.get("line") or 0), file=str(evid.get("file") or ""))
        flow = self.flows_by_ep.get(ep["id"])
        self.known_refs.add(ep["id"])
        if not flow:
            return e
        e.flow_id = flow["id"]
        self.known_refs.add(flow["id"])
        nodes = {n["id"]: n for n in flow["nodes"]}
        out: dict[str, list[dict]] = defaultdict(list)
        for edge in flow["edges"]:
            out[edge["source"]].append(edge)
        starts = [n for n in flow["nodes"] if n["type"] == "Event"]
        kind_map = {"Event": "event", "Handler": "handler", "Method": "method", "DataAccessOperation": "data_operation", "StoredProcedure": "procedure",
                    "SqlOperation": "procedure", "Class": "class"}

        def walk(node_id: str, trail: list[dict], seen: set) -> None:
            node = nodes[node_id]
            step = {"kind": kind_map.get(node["type"], node["type"].lower()), "label": short_label(node), "node_id": node_id,
                    "status": "CONFIRMED", "source_refs": []}
            trail = trail + [step]
            nexts = [x for x in out.get(node_id, []) if nodes.get(x["target"], {}).get("type") != "UnresolvedCall" and x.get("confidence") != "unresolved"
                     and x["target"] not in seen]
            if not nexts or len(trail) > 14:
                e.chains.append(trail)
                return
            for edge in sorted(nexts, key=lambda x: (nodes[x["target"]]["type"], x["target"])):
                refs = [r for r in edge.get("evidence_refs", [])]
                tgt = walk_edge(edge, trail, refs, seen | {node_id})
                del tgt

        def walk_edge(edge, trail, refs, seen):
            if trail:
                trail = trail[:-1] + [{**trail[-1], "source_refs": sorted(set(trail[-1]["source_refs"]) | set(refs))}]
            walk(edge["target"], trail, seen)

        for s in starts:
            walk(s["id"], [], set())
        e.chains = e.chains[:8]
        for chain in e.chains:
            for step in chain:
                step["source_refs"] = sorted({r for r in step["source_refs"] if r}) or [flow["id"]]
                self.known_refs.update(step["source_refs"])
        procs = {n["label"] for n in flow["nodes"] if n["type"] in ("StoredProcedure",)}
        for n in flow["nodes"]:
            if n["type"] == "DataAccessOperation":
                d = self.dao.get(n["label"]) or self.dao.get(n["id"])
                if d is None:
                    continue
                self.known_refs.add(d["id"])
                linked = sorted({nodes[x["target"]]["label"] for x in out.get(n["id"], []) if nodes.get(x["target"], {}).get("type") == "StoredProcedure"})
                proc = d.get("stored_procedure") or (linked[0] if linked else "")
                if not proc and d.get("operation_kind") == "transaction":
                    continue
                e.data_ops.append({"dao_id": d["id"], "class": d.get("class") or "", "method": d.get("method") or "", "procedure": proc,
                                   "kind": d.get("operation_kind"), "effect": classify_target(proc or f'{d.get("class")}.{d.get("method")}')})
        known_procs = {d["procedure"] for d in e.data_ops}
        for name in sorted(procs - known_procs):
            e.data_ops.append({"dao_id": "", "class": "", "method": "", "procedure": name, "kind": "stored_procedure", "effect": classify_target(name)})
        for edge in flow["edges"]:
            tgt = nodes.get(edge["target"], {})
            if tgt.get("type") == "UnresolvedCall":
                e.unresolved.append({"label": short_label(tgt), "from": short_label(nodes.get(edge["source"], {})),
                                     "refs": [r for r in edge.get("evidence_refs", [])] or [flow["id"]]})
        for u in e.unresolved:
            self.known_refs.update(u["refs"])
        return e

    # ---- helpers for validation
    def all_class_names(self) -> set[str]:
        return {str(d.get("class") or "").lower() for d in self.dao.values()} | {v.name.lower() for v in self._views.values()}
