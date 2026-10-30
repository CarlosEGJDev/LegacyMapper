"""Deterministic UI / navigation / style extraction for VB.NET WebForms (post-V5 Gate B, DT-03).

This is the ONLY place that reads view markup, code-behind, stylesheets and icons for documentary purposes. It runs once, during the
deterministic analysis (Evidence build), and persists what it finds as the `ui_*` partitions of Evidence Core. Behavioral documentation,
AI context, templates and delivery consume those partitions and never reopen the source repository.

Facts only: a control exists only if its tag is in the markup; a target is CONFIRMED only when exactly one view matches the literal;
dynamic values stay dynamic; nothing is rendered, executed or resolved by a browser engine.
"""
from __future__ import annotations

import base64
import hashlib
import html
import json
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

from legacy_documenter.evidence.identity import DuplicateOrdinalAssigner, normalize_repository_id, sha256_id, source_artifact_id
from legacy_documenter.evidence.ui_css import parse_css, parse_declarations
from legacy_documenter.evidence.ui_model import (
    ASSET_EXTENSIONS, CONFIRMED, ID_PREFIX, INFERRED, MAX_ASSET_BYTES, PARTITION_ASSETS, PARTITION_CONTROLS, PARTITION_DOCUMENTS,
    PARTITION_EVENTS, PARTITION_MESSAGES, PARTITION_NAVIGATION, PARTITION_PARAMETERS, PARTITION_STYLES, UI_KINDS, UI_PARTITIONS,
    UNRESOLVED, CodeFacts, MarkupControl, NavHit,
)

UI_EXTRACTOR_ID = "vbnet-webforms-ui"
UI_EXTRACTOR_VERSION = "1.1"
VIEW_EXTENSIONS = (".aspx", ".ascx", ".master")
CODE_EXT = (".vb", ".ascx", ".aspx", ".js", ".master", ".htm", ".html")
SCHEMA_VERSION = "1.1"
SHELL_CANDIDATES = ("default.aspx",)

_URL = re.compile(r"url=([A-Za-z0-9_.\-]+)/([A-Za-z0-9_.\-]+)((?:&[A-Za-z0-9_]+=?[^'\"&]*)*)", re.I)
_PARAM = re.compile(r"&([A-Za-z0-9_]+)=")
_SUB = re.compile(r"^\s*(?:Private|Public|Protected|Friend)?\s*(?:Shared\s+)?(Sub|Function)\s+([A-Za-z0-9_]+)", re.I)
_HANDLES = re.compile(r"Handles\s+([A-Za-z0-9_.]+)", re.I)
_WITHEVENTS = re.compile(r"WithEvents\s+([A-Za-z0-9_]+)\s+As\s+([A-Za-z0-9_.]+)", re.I)
_MSGBOX = re.compile(r"""\b(MsgBox|MessageBox\.Show)\s*\(\s*(?:"((?:[^"]|"")*)")?""", re.I)
_ALERT = re.compile(r"""\balert\s*\(\s*(?:\\?['"]([^'"]*)['"])?""", re.I)
_PARAM_URL = re.compile(r"""parametrosURL\s*\(\s*"([A-Za-z0-9_]+)"\s*\)""", re.I)
_QS = re.compile(r"""Request\.QueryString(?:\.Item)?\s*\(\s*"([A-Za-z0-9_]+)"\s*\)""", re.I)
_SESSION = re.compile(r"""Session\s*\(\s*"([A-Za-z0-9_]+)"\s*\)""", re.I)
_IMPORTS = re.compile(r"^\s*Imports\s+([A-Za-z0-9_.]+)", re.I | re.M)
_DESPLEGAR = re.compile(r"\bDesplegarError\s*\(", re.I)
_LOADCONTROL = re.compile(r"""LoadControl\s*\(\s*"([^"]+\.ascx)"\s*\)""", re.I)
_LINK_CSS = re.compile(r"<link[^>]+href=[\"']([^\"']+\.css)[\"']", re.I)
_ATTR = re.compile(r"""([A-Za-z_][\w:.-]*)\s*=\s*"([^"]*)\"""")
_CONFIG_TARGET_ATTRS = ("navigateurl", "url", "href", "src", "path", "page", "value", "target", "link")
_CONFIG_PATH = re.compile(r"^[~./\\\w\- ]+\.(?:aspx|ascx)(?:\?.*)?$", re.I)
_CONFIG_EXTENSIONS = (".xml", ".config", ".sitemap")
_THEME = re.compile(r"""<%@\s*Page\b[^%]*?\b(?:StyleSheetTheme|Theme)\s*=\s*"([^"]+)\"""", re.I | re.S)


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1")


# ---------------------------------------------------------------- markup
KIND_BY_TAG = {
    "label": "label", "textbox": "text", "textboxadv": "text", "rutadv": "text", "fechaadv": "text", "numeroadv": "text", "textarea": "text",
    "input": "text", "dropdownlist": "dropdown", "select": "dropdown", "listbox": "dropdown", "button": "button", "imagebutton": "button",
    "hyperlink": "link", "linkbutton": "link", "a": "link", "tablapaginada": "grid", "datagrid": "grid", "gridview": "grid", "datapanel": "panel",
    "panel": "panel", "checkbox": "check", "checkboxlist": "check", "radiobutton": "check", "radiobuttonlist": "check", "image": "image",
    "img": "image", "validationsummary": "validator", "requiredfieldvalidator": "validator", "regularexpressionvalidator": "validator",
    "comparevalidator": "validator", "customvalidator": "validator", "rangevalidator": "validator", "tabstrip": "panel", "multipage": "panel",
}
_ATTR_LABEL = ("Etiqueta", "Text", "Titulo", "Caption", "ToolTip", "Title", "Texto", "hlnk_Texto")


class _Markup(HTMLParser):
    """Collects controls and the table/row/cell skeleton of an .ascx/.aspx file. HTML tags without runat/ID/Tipo semantics are ignored
    unless they are form controls; nothing is invented: a control exists only if its tag is in the markup."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.controls: list[MarkupControl] = []
        self.rows: list[list[list[str]]] = []
        self.placeholders: list[dict] = []
        self._tables: list[dict] = []
        self._open: list[tuple[str, MarkupControl | None]] = []
        self._text_for: MarkupControl | None = None
        self.table_count = 0

    def _cell(self):
        if not self._tables:
            return None
        table = self._tables[-1]
        if not table["rows"]:
            table["rows"].append({"cells": []})
        row = table["rows"][-1]
        if not row["cells"]:
            row["cells"].append({"items": []})
        return row["cells"][-1]

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        line = self.getpos()[0]
        name = tag.split(":")[-1].lower()
        if tag == "table":
            node = {"type": "table", "rows": [], "attrs": {k: a[k] for k in ("class", "style", "bgcolor", "width", "border", "cellpadding") if a.get(k)}}
            cell = self._cell()
            (cell["items"] if cell is not None else self.rows_root()).append(node)
            self._tables.append(node)
            self.table_count += 1
        elif tag == "tr" and self._tables:
            self._tables[-1]["rows"].append({"cells": []})
        elif tag in ("td", "th") and self._tables:
            row = self._tables[-1]["rows"][-1] if self._tables[-1]["rows"] else None
            if row is None:
                self._tables[-1]["rows"].append({"cells": []})
                row = self._tables[-1]["rows"][-1]
            row["cells"].append({"items": [], "width": a.get("width") or _style_width(a.get("style", "")),
                                 "attrs": {k: a[k] for k in ("class", "style", "bgcolor", "align", "valign") if a.get(k)}})
        if ":" in tag and name in ("content", "contentplaceholder"):
            self.placeholders.append({"tag": tag, "id": a.get("id", ""), "content_placeholder_id": a.get("contentplaceholderid", ""), "line": line})
        ctl = None
        is_prefixed = ":" in tag and not tag.startswith("asp:listitem") and name not in ("listitem", "tablapaginadacolumna", "content", "contentplaceholder")
        is_form = tag in ("input", "select", "textarea", "button", "img", "a")
        if (is_prefixed or is_form) and (a.get("id") or is_prefixed):
            kind = KIND_BY_TAG.get(name, "other")
            if tag == "input":
                kind = {"button": "button", "submit": "button", "image": "button", "checkbox": "check", "radio": "check", "hidden": "hidden"}.get(a.get("type", "text").lower(), "text")
            if kind != "hidden":
                label = next((a[k.lower()] for k in _ATTR_LABEL if a.get(k.lower())), "")
                ctl = MarkupControl(id=a.get("id", ""), tag=tag, kind=kind, label=label.strip(), line=line,
                                    visible=a.get("visible", "true").lower() != "false", attrs=a,
                                    bound_to=(f'{a.get("nombrecompletoclase", "")}.{a.get("nombremetodo", "")}'.strip(".") if a.get("nombremetodo") else ""))
                self.controls.append(ctl)
                cell = self._cell()
                if cell is not None:
                    cell["items"].append(ctl.id or f"{tag}@{line}")
                else:
                    self.rows_root().append(ctl.id or f"{tag}@{line}")
                self._text_for = ctl
        if name == "tablapaginadacolumna" and self.controls:
            grid = next((c for c in reversed(self.controls) if c.kind == "grid"), None)
            if grid is not None and a.get("visible", "true").lower() != "false" and a.get("titulo"):
                grid.columns.append(a["titulo"].strip())
        self._open.append((tag, ctl))

    def rows_root(self):
        if not hasattr(self, "_root"):
            self._root: list = []
        return self._root

    def handle_endtag(self, tag):
        while self._open:
            t, _ = self._open.pop()
            if t == tag:
                break
        if tag == "table" and self._tables:
            self._tables.pop()
        self._text_for = None if not self._open or self._open[-1][1] is None else self._open[-1][1]

    def handle_data(self, data):
        ctl = self._text_for
        if ctl is not None and ctl.kind in ("label", "link", "button") and not ctl.label:
            text = " ".join(data.split())
            if text:
                ctl.label = text

    def skeleton(self) -> list:
        return getattr(self, "_root", [])


def _style_width(style: str) -> str:
    m = re.search(r"width\s*:\s*([0-9]+(?:px|%))", style or "", re.I)
    return m.group(1) if m else ""


def parse_markup(text: str) -> _Markup:
    parser = _Markup()
    # the HTML parser lowercases attribute names; Register/Control directives are not controls
    parser.feed(re.sub(r"<%@.*?%>", "", text, flags=re.S))
    parser.close()
    return parser


# ---------------------------------------------------------------- code-behind
def parse_codebehind(text: str, rel: str) -> CodeFacts:
    facts = CodeFacts(file=rel)
    lines = text.splitlines()
    current = None
    session: dict[str, int] = {}
    for i, line in enumerate(lines, 1):
        stripped = line.split("'")[0] if "'" in line and '"' not in line else line
        m = _SUB.match(stripped)
        if m and not re.match(r"^\s*(End|Exit)\b", stripped, re.I):
            current = {"name": m.group(2), "kind": m.group(1).lower(), "line": i, "handles": [h for h in _HANDLES.findall(stripped)]}
            facts.subs.append(current)
        if re.match(r"^\s*End\s+(Sub|Function)\b", line, re.I) and current:
            current["end"] = i
            current = None
        w = _WITHEVENTS.search(line)
        if w:
            facts.declared.append({"id": w.group(1), "type": w.group(2), "line": i})
        for key in _PARAM_URL.findall(line):
            facts.receives.append({"name": key, "line": i, "via": "parametrosURL"})
        for key in _QS.findall(line):
            facts.receives.append({"name": key, "line": i, "via": "QueryString"})
        for key in _SESSION.findall(line):
            session.setdefault(key, i)
        event = current["name"] if current else "(declaración)"
        for mm in _MSGBOX.finditer(line):
            text_literal = (mm.group(2) or "").replace('""', '"')
            facts.messages.append({"kind": "msgbox", "text": text_literal, "line": i, "event": event})
        for mm in _ALERT.finditer(line):
            facts.messages.append({"kind": "alert", "text": mm.group(1) or "", "line": i, "event": event})
        if _DESPLEGAR.search(line):
            facts.messages.append({"kind": "error_display", "text": "", "line": i, "event": event})
        if "RegisterClientScriptBlock" in line or "RegisterStartupScript" in line:
            facts.script_blocks += 1
        if re.search(r"\.Visible\s*=", line):
            facts.visible_toggles += 1
    facts.session_keys = sorted(session)
    facts.session_lines = session  # type: ignore[attr-defined]  # first line of each key; persisted as evidence of the read
    facts.imports = sorted(set(_IMPORTS.findall(text)))
    return facts


def scan_navigation(repo_root: Path, relative_files: list[str]) -> list[NavHit]:
    """Every `url=<folder>/<view>` literal of the repository's code/markup files, with its parameters and mechanism."""
    hits: list[NavHit] = []
    for rel in relative_files:
        hits.extend(_navigation_of_file(repo_root, rel))
    return hits


def _navigation_of_file(repo_root: Path, rel: str) -> list[NavHit]:
    if not rel.lower().endswith((".vb", ".ascx", ".aspx", ".master")):
        return []
    path = repo_root / rel
    try:
        raw = path.read_bytes()
    except OSError:
        return []
    if b"url=" not in raw.lower():
        return []
    hits: list[NavHit] = []
    text = read_text(path)
    for i, line in enumerate(text.splitlines(), 1):
        for m in _URL.finditer(line):
            low = line.lower()
            mech = ("window_open" if ("onclickwindowopen" in low or "window.open" in low or "windowopen" in low)
                    else "navigate_url" if "navigateurl" in low else "url_literal")
            hits.append(NavHit(rel, i, m.group(1), m.group(2), _PARAM.findall(m.group(3) or ""), mech))
    return hits


# ---------------------------------------------------------------- Evidence extraction
def _posix(path: str) -> str:
    return str(path or "").replace("\\", "/")


def _key(path: str) -> str:
    return _posix(path).lower()


def _line_count(raw: bytes) -> int:
    return len(raw.splitlines())


#: Attributes that name another control / data source of the same document (relationship facts, not presentation).
_REFERENCE_ATTRS = ("controltovalidate", "targetcontrolid", "popupcontrolid", "associatedcontrolid", "forcontrol", "datasourceid",
                    "contentplaceholderid", "skinid", "controltocompare")
_STYLE_ATTRS = ("cssclass", "class", "tipo", "style", "width", "height", "bgcolor", "skinid")


class UiEvidenceExtractor:
    """Builds the `ui_*` Evidence partitions from the scanned file list and the repository root. Deterministic: sorted inputs, no clock,
    identities from the logical repository id (when declared) and repository-relative paths only."""

    def __init__(self, repo_root: str | Path, files: list[dict], webforms: list[dict], projects: list[dict],
                 repository_id: str | None = None) -> None:
        self.root = Path(repo_root)
        self.files = files
        self.webforms = {_key(w.get("path", "")): w for w in webforms or []}
        self.projects = projects or []
        self.rid = normalize_repository_id(repository_id)
        self._assigner = DuplicateOrdinalAssigner()
        self._resolved_root = self.root.resolve()
        self._basenames: dict = {}
        self.summary: dict = {}
        self._app_roots: dict[str, set] = defaultdict(set)         # document key -> application roots (project directories) that declare it
        for project in self.projects:
            pdir = _posix(str(project.get("path", ""))).rpartition("/")[0]
            for item in list(project.get("content_items") or []) + list(project.get("compile_items") or []):
                self._app_roots[_key(_normalize_posix((pdir + "/" if pdir else "") + _posix(str(item))))].add(pdir)

    # ---- identity helpers
    def _id(self, partition: str, *parts: object) -> str:
        """`<prefix>-<sha256>` over (logical repository id when declared, entity parts, duplicate ordinal among identical base tuples).
        Never a physical path, working directory or machine value."""
        ordinal = self._assigner.assign((partition, *parts))
        head = (self.rid,) if self.rid else ()
        return sha256_id(ID_PREFIX[partition], *head, *parts, ordinal)

    def _src(self, path: str) -> str:
        return source_artifact_id(_posix(path), self.rid)

    def _record(self, partition: str, rid: str, path: str, status: str, properties: dict, relationships: dict | None = None,
                source_refs: list[str] | None = None) -> dict:
        child = (partition in (PARTITION_CONTROLS, PARTITION_EVENTS, PARTITION_MESSAGES, PARTITION_PARAMETERS)
                 or properties.get("style_kind") in ("stylesheet_link", "theme_reference")
                 or properties.get("asset_kind") == "asset_reference")
        if child and relationships and relationships.get("document_id"):
            # schema 1.1: a child fact does not repeat its document's path/provenance; `document_id` + `source_scope` resolve them
            scope = "code_behind" if _posix(path).lower().endswith(".vb") else "markup"
            return {"id": rid, "kind": UI_KINDS[partition], "status": status, "properties": properties,
                    "relationships": {**relationships, "source_scope": scope}}
        return {"id": rid, "kind": UI_KINDS[partition], "schema_version": SCHEMA_VERSION, "logical_source_path": _posix(path),
                "source_refs": source_refs if source_refs is not None else [self._src(path)], "status": status,
                "properties": properties, "relationships": relationships or {}}

    # ---- main
    def extract(self) -> dict[str, list[dict]]:
        out: dict[str, list[dict]] = {name: [] for name in UI_PARTITIONS}
        scanned = {_key(f["relative_path"]): f["relative_path"] for f in self.files}
        listed = [f["relative_path"] for f in self.files if f["relative_path"].lower().endswith(VIEW_EXTENSIONS)]
        view_files = sorted((r for r in listed if (self.root / r).is_file()), key=lambda p: (_posix(p).lower(), _posix(p)))
        self.summary = {"documents_listed": len(listed), "documents_extracted": len(view_files),
                        "unreadable_documents": sorted(_posix(r) for r in listed if not (self.root / r).is_file())}
        doc_by_key = {_key(rel): self._id(PARTITION_DOCUMENTS, _posix(rel)) for rel in view_files}
        view_index: dict[str, list[str]] = defaultdict(list)       # stem(lower) -> logical paths
        for rel in view_files:
            if rel.lower().endswith((".aspx", ".ascx")):
                view_index[PurePosixPath(_posix(rel)).stem.lower()].append(_posix(rel))
        css_files: dict[str, dict] = {}                              # logical css path -> record
        asset_files: dict[str, dict] = {}
        style_profiles: dict[str, dict] = {}                         # canonical style content -> shared profile record
        texts: dict[str, str] = {}                                    # lowercased markup+code text per document (for name mentions)
        hosts: dict[str, list[dict]] = defaultdict(list)
        doc_records: dict[str, dict] = {}
        controls_by_doc: dict[str, list[tuple[dict, MarkupControl]]] = {}

        for rel in view_files:
            path = self.root / rel
            try:
                raw = path.read_bytes()
            except OSError:
                continue
            posix = _posix(rel)
            doc_id = doc_by_key[_key(rel)]
            text = read_text(path)
            extraction_error = ""
            try:
                markup = parse_markup(text)
            except Exception as exc:                  # malformed markup must not abort the analysis: recorded, not silenced
                markup, extraction_error = _Markup(), exc.__class__.__name__
            code_rel = rel + ".vb"
            code_path = self.root / code_rel
            code: CodeFacts | None = None
            code_raw = b""
            if code_path.is_file():
                code_raw = code_path.read_bytes()
                code = parse_codebehind(read_text(code_path), _posix(code_rel))
            web = self.webforms.get(_key(rel), {})
            doc_refs = [self._src(posix)] + ([self._src(_posix(code_rel))] if code is not None and _key(code_rel) in scanned else [])
            texts[posix] = (raw.decode("utf-8", errors="ignore").lower() + "\n" + code_raw.decode("utf-8", errors="ignore").lower()) if True else ""
            containers = _container_map(markup.skeleton())

            # -- controls
            control_ids: list[tuple[dict, MarkupControl]] = []
            for ctl in markup.controls:
                key = ctl.id or f"{ctl.tag}@{ctl.line}"
                cid = self._id(PARTITION_CONTROLS, posix, ctl.tag, key)
                refs = {a: ctl.attrs[a] for a in _REFERENCE_ATTRS if ctl.attrs.get(a)}
                server_side = ctl.attrs.get("runat", "").lower() == "server"
                handlers = {a: ctl.attrs[a] for a in sorted(ctl.attrs) if server_side and a.startswith("on") and a != "onclientclick"
                            and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", ctl.attrs[a] or "")}
                rec = self._record(PARTITION_CONTROLS, cid, posix, CONFIRMED, {
                    "control_id": ctl.id, "tag": ctl.tag, "control_kind": ctl.kind, "label": ctl.label, "line": ctl.line,
                    "visible_initially": ctl.visible, "attrs": dict(sorted(ctl.attrs.items())), "columns": list(ctl.columns),
                    "bound_to": ctl.bound_to, "skeleton_key": key, "container": containers.get(key),
                }, {"document_id": doc_id, "references": refs,
                    "validates": ctl.attrs.get("controltovalidate", "") if ctl.kind == "validator" else "",
                    "server_events": handlers}, doc_refs[:1])
                out[PARTITION_CONTROLS].append(rec)
                control_ids.append((rec, ctl))
            controls_by_doc[doc_id] = control_ids

            # -- code facts: event bindings, messages, parameters
            sub_names = {s["name"].lower() for s in (code.subs if code else [])}
            declared = {d["id"].lower() for d in (code.declared if code else [])}
            control_names = {c.id.lower() for c in markup.controls if c.id}
            code_path_posix = _posix(code_rel)
            code_refs = doc_refs[-1:] if (code is not None and _key(code_rel) in scanned) else doc_refs[:1]
            for s in (code.subs if code else []):
                for handle in s["handles"]:
                    ctrl, _, event = handle.rpartition(".")
                    known = ctrl.lower() in control_names or ctrl.lower() in declared or ctrl.lower() in ("mybase", "me", "")
                    out[PARTITION_EVENTS].append(self._record(PARTITION_EVENTS, self._id(PARTITION_EVENTS, code_path_posix, s["name"], handle, s["line"]),
                        code_path_posix, CONFIRMED, {"origin": "handles_clause", "handler": s["name"], "handler_line": s["line"], "control": ctrl,
                                                      "event": event, "control_declared": bool(known)}, {"document_id": doc_id}, code_refs))
            for rec, ctl in control_ids:
                for attr, handler in rec["relationships"]["server_events"].items():
                    defined = handler.lower() in sub_names
                    out[PARTITION_EVENTS].append(self._record(PARTITION_EVENTS, self._id(PARTITION_EVENTS, posix, ctl.tag, rec["properties"]["skeleton_key"],
                        attr, handler), posix, CONFIRMED if defined else UNRESOLVED,
                        {"origin": "markup_attribute", "attribute": attr, "handler": handler, "handler_defined": defined,
                         "control": ctl.id, "line": ctl.line}, {"document_id": doc_id, "control_record": rec["id"]}, doc_refs[:1]))
            for m in (code.messages if code else []):
                out[PARTITION_MESSAGES].append(self._record(PARTITION_MESSAGES, self._id(PARTITION_MESSAGES, code_path_posix, m["line"], m["kind"], m["event"]),
                    code_path_posix, CONFIRMED, {"origin": "code_behind", "message_kind": m["kind"], "text": m["text"], "event": m["event"],
                                                  "line": m["line"], "text_kind": "literal" if m["text"] else "dynamic"}, {"document_id": doc_id}, code_refs))
            for rec, ctl in control_ids:
                if ctl.kind == "validator" and ctl.attrs.get("errormessage"):
                    out[PARTITION_MESSAGES].append(self._record(PARTITION_MESSAGES, self._id(PARTITION_MESSAGES, posix, rec["id"], "errormessage"),
                        posix, CONFIRMED, {"origin": "markup_validator", "message_kind": "validator_message", "text": ctl.attrs["errormessage"],
                                           "event": "", "line": ctl.line, "text_kind": "literal"}, {"document_id": doc_id, "control_record": rec["id"]}))
            for r in (code.receives if code else []):
                out[PARTITION_PARAMETERS].append(self._record(PARTITION_PARAMETERS, self._id(PARTITION_PARAMETERS, code_path_posix, r["via"], r["name"], r["line"]),
                    code_path_posix, CONFIRMED, {"name": r["name"], "via": r["via"], "line": r["line"], "direction": "received"}, {"document_id": doc_id}, code_refs))
            for key, line in sorted(getattr(code, "session_lines", {}).items()):
                out[PARTITION_PARAMETERS].append(self._record(PARTITION_PARAMETERS, self._id(PARTITION_PARAMETERS, code_path_posix, "Session", key),
                    code_path_posix, CONFIRMED, {"name": key, "via": "Session", "line": line, "direction": "context_key"}, {"document_id": doc_id}, code_refs))

            # -- assets (images referenced by controls)
            for rec, ctl in control_ids:
                image = ctl.attrs.get("imageurl", "")
                if image:
                    out[PARTITION_ASSETS].append(self._asset_reference(posix, doc_id, rec, image, asset_files, doc_refs[:1], scanned))

            # -- style references
            hrefs = _LINK_CSS.findall(raw.decode("cp1252", errors="ignore"))
            links = []
            for href in hrefs:
                resolved = self._resolve_in_repo(path.parent, href)
                status, reason, target = (UNRESOLVED, "OUTSIDE_REPOSITORY", None)
                if resolved is not None and not isinstance(resolved, str):
                    status, reason, target = (CONFIRMED, "", resolved) if resolved.is_file() else (UNRESOLVED, "NOT_FOUND", None)
                file_id = None
                logical = None
                if target is not None:
                    logical = target.relative_to(self._resolved_root).as_posix()
                    if logical not in css_files:
                        css_bytes = target.read_bytes()
                        css_rec = self._record(PARTITION_STYLES, self._id(PARTITION_STYLES, "stylesheet_file", logical), logical, CONFIRMED,
                                               {"style_kind": "stylesheet_file", "rules": dict(sorted(parse_css(css_bytes.decode("cp1252", errors="ignore")).items())),
                                                "size_bytes": len(css_bytes), "sha256": hashlib.sha256(css_bytes).hexdigest()},
                                               {}, [self._src(logical)] if _key(logical) in scanned else doc_refs[:1])
                        css_files[logical] = css_rec
                    file_id = css_files[logical]["id"]
                link = self._record(PARTITION_STYLES, self._id(PARTITION_STYLES, "stylesheet_link", posix, href, len(links)), posix, status,
                                    {"style_kind": "stylesheet_link", "href": href, "resolved_logical_path": logical, "reason": reason,
                                     "shell_candidate": _key(posix) in SHELL_CANDIDATES, "order": len(links)},
                                    {"document_id": doc_id, "stylesheet_file": file_id}, doc_refs[:1])
                links.append(link)
                out[PARTITION_STYLES].append(link)
            theme = _THEME.search(text)
            if theme:
                name = theme.group(1)
                found = any(f"app_themes/{name.lower()}/" in _key(k) for k in scanned)
                out[PARTITION_STYLES].append(self._record(PARTITION_STYLES, self._id(PARTITION_STYLES, "theme_reference", posix, name), posix,
                    CONFIRMED if found else UNRESOLVED, {"style_kind": "theme_reference", "theme": name}, {"document_id": doc_id}, doc_refs[:1]))
            for rec, ctl in control_ids:
                refs = self._control_style_refs(ctl)
                if refs:
                    canonical = json.dumps(refs, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
                    if canonical not in style_profiles:
                        style_profiles[canonical] = {"id": self._id(PARTITION_STYLES, "style_profile", canonical), "kind": UI_KINDS[PARTITION_STYLES],
                                                     "status": CONFIRMED, "properties": {"style_kind": "style_profile", **refs},
                                                     "relationships": {"source_scope": "shared"}}
                    rec["relationships"]["style_profile"] = style_profiles[canonical]["id"]

            # -- master / registered controls / loaded controls
            master_literal = str(web.get("master_page") or _directive_attr(text, "masterpagefile") or "")
            relationships: dict = {}
            master = self._resolve_logical(master_literal, posix, scanned) if master_literal else None
            relationships["master_page"] = ({"literal": master_literal, **self._edge_target(master, doc_by_key)} if master_literal else None)
            registered = []
            for reg in (web.get("registers") or []):
                norm = reg.get("_normalized") or {k.lower(): v for k, v in reg.items()}
                src_literal = str(norm.get("src") or "")
                if not src_literal:
                    continue
                target = self._resolve_logical(src_literal, posix, scanned)
                registered.append({"tag_prefix": norm.get("tagprefix", ""), "tag_name": norm.get("tagname", ""), "literal": src_literal,
                                   **self._edge_target(target, doc_by_key)})
            relationships["registered_controls"] = registered
            relationships["stylesheets"] = [{"href": l["properties"]["href"], "status": l["status"], "resolved_logical_path": l["properties"]["resolved_logical_path"]}
                                            for l in links]
            loaded = []
            if code is not None:
                for i, line in enumerate(read_text(code_path).splitlines(), 1):
                    for literal in _LOADCONTROL.findall(line):
                        target = self._resolve_logical(literal, posix, scanned)
                        loaded.append({"literal": literal, "line": i, **self._edge_target(target, doc_by_key)})
            relationships["loaded_controls"] = loaded
            for edge in registered:
                for tid in edge["target_document_ids"]:
                    hosts[tid].append({"document_id": doc_id, "logical_source_path": posix, "mechanism": "register_directive"})
            for edge in loaded:
                for tid in edge["target_document_ids"]:
                    hosts[tid].append({"document_id": doc_id, "logical_source_path": posix, "mechanism": "load_control", "line": edge["line"]})
            doc_records[posix] = self._record(PARTITION_DOCUMENTS, doc_id, posix, UNRESOLVED if extraction_error else CONFIRMED, {
                "document_kind": posix.rsplit(".", 1)[-1].lower(), "file_as_scanned": rel, "line_count": _line_count(raw),
                "extraction_error": extraction_error,
                "code_behind": ({"logical_source_path": code_path_posix, "source_ref": self._src(code_path_posix) if _key(code_rel) in scanned else None,
                                 "line_count": _line_count(code_raw)} if code is not None else None),
                "control_count": len(markup.controls), "table_count": markup.table_count, "skeleton": markup.skeleton(),
                "placeholders": markup.placeholders, "declared_controls": list(code.declared) if code else [],
                "subs": list(code.subs) if code else [], "imports": list(code.imports) if code else [],
                "script_blocks": code.script_blocks if code else 0, "visible_toggles": code.visible_toggles if code else 0,
                "mentions_views": [],
            }, relationships, doc_refs)

        # -- host chain (user control -> hosts), resolved after every document is known
        for posix, rec in doc_records.items():
            found = hosts.get(rec["id"], [])
            seen, unique = set(), []
            for h in sorted(found, key=lambda x: (x["logical_source_path"].lower(), x["mechanism"], x.get("line", 0))):
                k = (h["document_id"], h["mechanism"], h.get("line", 0))
                if k not in seen:
                    seen.add(k)
                    unique.append(h)
            distinct = {h["document_id"] for h in unique}
            rec["relationships"]["hosts"] = unique
            rec["relationships"]["host_resolution"] = ("NONE" if not distinct else "SINGLE" if len(distinct) == 1 else "AMBIGUOUS")
            rec["relationships"]["host_status"] = (UNRESOLVED if not distinct else CONFIRMED if len(distinct) == 1 else INFERRED)

        # -- name mentions inside each project's views (usage evidence): view A's text mentions the name of view B of the same project
        for project in self.projects:
            pdir = _posix(str(project.get("path", ""))).rpartition("/")[0]
            items = list(project.get("content_items") or []) + list(project.get("compile_items") or [])
            canonical = {_key(p): p for p in doc_records}
            members = sorted({canonical[_key((pdir + "/" if pdir else "") + _posix(i))] for i in items if str(i).lower().endswith((".ascx", ".aspx"))
                              and _key((pdir + "/" if pdir else "") + _posix(i)) in canonical}, key=str.lower)
            names = {m: PurePosixPath(m).stem.lower() for m in members}
            for a in members:
                found = sorted({b for b in members if b != a and names[b] in texts[a]}, key=str.lower)
                prev = doc_records[a]["properties"]["mentions_views"]
                doc_records[a]["properties"]["mentions_views"] = sorted(set(prev) | set(found), key=str.lower)

        out[PARTITION_DOCUMENTS] = [doc_records[p] for p in sorted(doc_records, key=lambda x: (x.lower(), x))]

        # -- navigation: literal invocations (repo-wide) + structural relations
        folder_of = {p: PurePosixPath(p).parent.name.lower() for p in doc_records}
        for rel in (f["relative_path"] for f in self.files):          # scanner (index) order: identical to the historical repo-wide scan
            hits = _navigation_of_file(self.root, rel)
            if not hits:
                continue
            posix = _posix(rel)
            line_total = _line_count((self.root / rel).read_bytes())  # only files that carry literals are read again
            src_doc = doc_by_key.get(_key(rel))
            if src_doc is None and posix.lower().endswith(".vb"):
                src_doc = doc_by_key.get(_key(posix[:-3]))
            for h in hits:
                cands = sorted((p for p in view_index.get(h.view.lower(), []) if not h.folder or folder_of.get(p) == h.folder.lower()), key=str.lower)
                status = CONFIRMED if len(cands) == 1 else INFERRED if len(cands) > 1 else UNRESOLVED
                out[PARTITION_NAVIGATION].append(self._record(PARTITION_NAVIGATION,
                    self._id(PARTITION_NAVIGATION, "invocation", posix, h.line, h.folder, h.view, h.mechanism), posix, status, {
                        "relation": "invocation", "mechanism": h.mechanism, "target_literal": f"{h.folder}/{h.view}", "target_folder": h.folder,
                        "target_view": h.view, "parameters": h.params, "line": h.line, "file_as_scanned": rel, "source_line_count": line_total,
                        "target_candidates": cands,
                    }, {"source_document_id": src_doc, "target_document_ids": [doc_by_key[_key(c)] for c in cands]}))
        for posix, rec in sorted(doc_records.items(), key=lambda kv: kv[0].lower()):
            rels = rec["relationships"]
            if rels.get("master_page"):
                m = rels["master_page"]
                out[PARTITION_NAVIGATION].append(self._record(PARTITION_NAVIGATION, self._id(PARTITION_NAVIGATION, "uses_master", posix, m["literal"]), posix,
                    m["status"], {"relation": "uses_master", "mechanism": "master_page_directive", "target_literal": m["literal"],
                                  "target_candidates": m["target_candidates"], "line": 1},
                    {"source_document_id": rec["id"], "target_document_ids": m["target_document_ids"]}))
            for i, reg in enumerate(rels["registered_controls"]):
                out[PARTITION_NAVIGATION].append(self._record(PARTITION_NAVIGATION, self._id(PARTITION_NAVIGATION, "hosts_user_control", posix, reg["literal"], i), posix,
                    reg["status"], {"relation": "hosts_user_control", "mechanism": "register_directive", "target_literal": reg["literal"],
                                    "tag_prefix": reg["tag_prefix"], "tag_name": reg["tag_name"], "target_candidates": reg["target_candidates"], "line": 1},
                    {"source_document_id": rec["id"], "target_document_ids": reg["target_document_ids"]}))
            for i, ld in enumerate(rels["loaded_controls"]):
                out[PARTITION_NAVIGATION].append(self._record(PARTITION_NAVIGATION, self._id(PARTITION_NAVIGATION, "loads_user_control", posix, ld["literal"], ld["line"], i),
                    rec["properties"]["code_behind"]["logical_source_path"] if rec["properties"]["code_behind"] else posix, ld["status"],
                    {"relation": "loads_user_control", "mechanism": "load_control", "target_literal": ld["literal"], "target_candidates": ld["target_candidates"],
                     "line": ld["line"]}, {"source_document_id": rec["id"], "target_document_ids": ld["target_document_ids"]},
                    rec["source_refs"][-1:] if rec["properties"]["code_behind"] and rec["properties"]["code_behind"]["source_ref"] else rec["source_refs"][:1]))
        out[PARTITION_ASSETS] = sorted(asset_files.values(), key=lambda r: r["logical_source_path"].lower()) + out[PARTITION_ASSETS]
        out[PARTITION_STYLES] = (sorted(css_files.values(), key=lambda r: r["logical_source_path"].lower())
                                 + sorted(style_profiles.values(), key=lambda r: r["id"]) + out[PARTITION_STYLES])
        self._config_navigation(scanned, doc_by_key, view_index, folder_of, out)
        return out

    # ---- helpers
    def _resolve_in_repo(self, base: Path, literal: str):
        """Absolute path of `literal` relative to `base` inside the repository; `'outside'` when it escapes; never raises."""
        try:
            target = (base / _posix(literal)).resolve()
            target.relative_to(self._resolved_root)
        except (ValueError, OSError):
            return "outside"
        return target

    def _resolve_logical(self, literal: str, from_path: str, scanned: dict) -> list[str]:
        """Candidate logical paths of a `~/x/y.ascx` / relative literal among the scanned files (all candidates; ambiguity preserved)."""
        lit = _posix(literal.strip())
        if lit.startswith("~/"):
            lit = lit[2:]
            rel_first = []
        else:
            base = PurePosixPath(from_path).parent
            direct = _normalize_posix(str(base / lit))
            rel_first = [scanned[_key(direct)]] if _key(direct) in scanned else []
        if rel_first:
            return [_posix(p) for p in rel_first]
        wanted = _normalize_posix(lit).lower()
        suffix = "/" + wanted
        index = self._basenames.get(id(scanned))
        if index is None:
            index = self._basenames[id(scanned)] = defaultdict(list)
            for k, orig in scanned.items():
                index[k.rsplit("/", 1)[-1]].append((k, orig))
        found = sorted({_posix(orig) for k, orig in index.get(wanted.rsplit("/", 1)[-1], []) if ("/" + k).endswith(suffix)}, key=str.lower)
        return found

    def _edge_target(self, candidates: list[str] | None, doc_by_key: dict) -> dict:
        candidates = [c for c in (candidates or []) if _key(c) in doc_by_key]
        status = CONFIRMED if len(candidates) == 1 else INFERRED if len(candidates) > 1 else UNRESOLVED
        return {"status": status, "target_candidates": candidates, "target_document_ids": [doc_by_key[_key(c)] for c in candidates]}

    def _control_style_refs(self, ctl: MarkupControl) -> dict | None:
        a = ctl.attrs
        if not any(a.get(k) for k in _STYLE_ATTRS):
            return None
        classes = []
        for key, origin in (("cssclass", "cssclass"), ("class", "class"), ("tipo", "tipo")):
            for name in str(a.get(key, "")).split():
                classes.append({"name": name, "source_attribute": origin, "inferred_from_tipo": origin == "tipo"})
        out: dict = {"classes": classes}
        if a.get("style"):
            out["inline_style"] = a["style"]
            out["inline_declarations"] = parse_declarations(str(a["style"]))
        dims = {k: a[k] for k in ("width", "height", "bgcolor") if a.get(k)}
        if dims:
            out["dimensions"] = dims
        if a.get("skinid"):
            out["skin_id"] = a["skinid"]
        return out

    def _asset_reference(self, posix: str, doc_id: str, ctl_rec: dict, literal: str, asset_files: dict, refs: list[str], scanned: dict) -> dict:
        status, reason, file_id, logical = UNRESOLVED, "", None, None
        basis: dict = {"mode": "relative_to_document"}
        target = None
        stripped = literal.strip()
        if stripped.startswith(("~/", "~\\")):
            roots = self._app_roots.get(_key(posix), set())
            if not roots:
                reason, basis = "APPLICATION_ROOT_UNKNOWN", {"mode": "application_root", "application_roots": []}
            elif len(roots) > 1:
                reason, basis = "AMBIGUOUS_APPLICATION_ROOT", {"mode": "application_root", "application_roots": sorted(roots)}
            else:
                root = next(iter(roots))
                candidate = _normalize_posix((root + "/" if root else "") + _posix(stripped[2:]))
                basis = {"mode": "application_root", "application_roots": [root], "resolved_candidate": candidate}
                original = scanned.get(_key(candidate))
                suffix_ok = candidate.lower().endswith(ASSET_EXTENSIONS)
                if original is None or not suffix_ok or not (self.root / original).is_file():
                    reason = "ASSET_NOT_FOUND"
                else:
                    target = (self.root / original).resolve()
        else:
            resolved = self._resolve_in_repo((self.root / posix).parent, literal)
            if resolved == "outside":
                reason = "OUTSIDE_REPOSITORY"
            elif resolved.suffix.lower() not in ASSET_EXTENSIONS or not resolved.is_file():
                reason = "NOT_FOUND"
            else:
                target = resolved
        if target is not None:
            logical = target.relative_to(self._resolved_root).as_posix()
            data = target.read_bytes()
            if logical not in asset_files:
                mime = {".gif": "image/gif", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}[target.suffix.lower()]
                embedded = len(data) <= MAX_ASSET_BYTES
                asset_files[logical] = self._record(PARTITION_ASSETS, self._id(PARTITION_ASSETS, "asset_file", logical), logical, CONFIRMED,
                    {"asset_kind": "asset_file", "mime": mime, "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                     "embedded": embedded, "data_base64": base64.b64encode(data).decode("ascii") if embedded else ""},
                    {}, [self._src(logical)] if _key(logical) in scanned else refs)
            file_id = asset_files[logical]["id"]
            if len(data) > MAX_ASSET_BYTES:
                reason = "TOO_LARGE_TO_EMBED"
            else:
                status = CONFIRMED
        return self._record(PARTITION_ASSETS, self._id(PARTITION_ASSETS, "asset_reference", ctl_rec["id"], literal), posix, status,
                            {"asset_kind": "asset_reference", "literal": literal, "resolved_logical_path": logical, "reason": reason,
                             "resolution_basis": basis, "control_id": ctl_rec["properties"]["control_id"],
                             "skeleton_key": ctl_rec["properties"]["skeleton_key"]},
                            {"document_id": doc_id, "control_record": ctl_rec["id"], "asset_file": file_id}, refs)

    def _config_navigation(self, scanned: dict, doc_by_key: dict, view_index: dict, folder_of: dict, out: dict) -> None:
        """Menu / configuration -> view edges, only for literal targets in XML-like configuration files (no crawler, no filename inference)."""
        for f in self.files:
            rel = f["relative_path"]
            if not rel.lower().endswith(_CONFIG_EXTENSIONS):
                continue
            path = self.root / rel
            try:
                if path.stat().st_size > 2_000_000:
                    continue
                text = read_text(path)
            except OSError:
                continue
            if "url=" not in text.lower() and ".aspx" not in text.lower() and ".ascx" not in text.lower():
                continue
            posix = _posix(rel)
            total_lines = len(text.splitlines())
            for line_no, line in enumerate(text.splitlines(), 1):
                attrs = [(n, html.unescape(v)) for n, v in _ATTR.findall(line)]
                label = next((v for n, v in attrs if n.lower() in ("text", "title", "name", "caption")), "")
                for name, value in attrs:
                    if name.lower() not in _CONFIG_TARGET_ATTRS:
                        continue
                    dynamic = any(tok in value for tok in ("<%", "{0}", "$(", "${", "%s"))
                    m = _URL.search(value)
                    cands: list[str] = []
                    params: list[str] = []
                    if m:
                        mechanism, literal = "config_url_literal", f"{m.group(1)}/{m.group(2)}"
                        params = _PARAM.findall(m.group(3) or "")
                        cands = sorted((p for p in view_index.get(m.group(2).lower(), []) if folder_of.get(p) == m.group(1).lower()), key=str.lower)
                    elif _CONFIG_PATH.match(value.strip()):
                        mechanism, literal = "config_path_literal", value.strip()
                        cands = [c for c in self._resolve_logical(literal.split("?")[0], posix, scanned) if _key(c) in doc_by_key]
                    else:
                        continue
                    status = UNRESOLVED if dynamic else CONFIRMED if len(cands) == 1 else INFERRED if len(cands) > 1 else UNRESOLVED
                    out[PARTITION_NAVIGATION].append(self._record(PARTITION_NAVIGATION,
                        self._id(PARTITION_NAVIGATION, "menu_entry", posix, line_no, name.lower(), literal), posix, status, {
                            "relation": "menu_entry", "mechanism": mechanism, "target_literal": literal, "parameters": params, "line": line_no,
                            "label": label, "attribute": name, "source_line_count": total_lines, "reason": "DYNAMIC_TARGET" if dynamic else ("" if cands else "TARGET_NOT_FOUND"),
                            "target_candidates": [] if dynamic else cands},
                        {"source_document_id": None, "target_document_ids": [] if dynamic else [doc_by_key[_key(c)] for c in cands]}))


def _normalize_posix(path: str) -> str:
    parts: list[str] = []
    for piece in _posix(path).split("/"):
        if piece in ("", "."):
            continue
        if piece == "..":
            if parts:
                parts.pop()
            continue
        parts.append(piece)
    return "/".join(parts)


def _directive_attr(text: str, name: str) -> str:
    m = re.search(r"<%@\s*(?:Page|Master|Control)\b[^%]*?\b" + re.escape(name) + r"""\s*=\s*"([^"]*)\"""", text, re.I | re.S)
    return m.group(1) if m else ""


def _container_map(skeleton: list) -> dict[str, dict]:
    """Control key -> {table, row, cell, parent_table, depth} (document-order table ordinals); derived from the persisted skeleton."""
    result: dict[str, dict] = {}
    counter = [0]

    def walk(items, parent_table, depth, row, cell):
        for item in items:
            if isinstance(item, dict):
                counter[0] += 1
                me = counter[0]
                for r, row_node in enumerate(item.get("rows", [])):
                    for c, cell_node in enumerate(row_node.get("cells", [])):
                        walk(cell_node.get("items", []), me, depth + 1, r, c)
            elif isinstance(item, str):
                result.setdefault(item, {"table": parent_table, "row": row, "cell": cell, "depth": depth})

    walk(skeleton, 0, 0, 0, 0)
    return result
