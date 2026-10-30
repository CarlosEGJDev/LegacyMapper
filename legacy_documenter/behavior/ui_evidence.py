"""Persisted UI / navigation / style Evidence reader for the behavioral layer (post-V5 Gate B).

The ONLY input is `<baseline>/evidence/ui_*.json` (verified against `EVIDENCE_MANIFEST.json`). Nothing here -- or anywhere under
`legacy_documenter/behavior/` -- opens the source repository: the facts were discovered once, by the deterministic adapter, and
persisted. A baseline that predates the extension fails explicitly (`UI_EVIDENCE_MISSING`); it is never silently reinterpreted and
there is no fallback that rereads source files.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .styles import StyleCatalog
from legacy_documenter.evidence.ui_model import (
    CONFIRMED, PARTITION_ASSETS, PARTITION_CONTROLS, PARTITION_DOCUMENTS, PARTITION_EVENTS, PARTITION_MESSAGES, PARTITION_NAVIGATION,
    PARTITION_PARAMETERS, PARTITION_STYLES, UI_EVIDENCE_SCHEMA_VERSION, UI_PARTITIONS, CodeFacts, MarkupControl, NavHit, norm_logical_path,
)

_ICON_REASONS = {"OUTSIDE_REPOSITORY": "fuera del repositorio", "NOT_FOUND": "no encontrada", "TOO_LARGE_TO_EMBED": "demasiado grande para incrustar",
                 "ASSET_NOT_FOUND": "no encontrada", "AMBIGUOUS_APPLICATION_ROOT": "raíz de aplicación ambigua",
                 "APPLICATION_ROOT_UNKNOWN": "raíz de aplicación desconocida"}
_CODE_MESSAGE_KINDS = ("msgbox", "alert", "error_display")


class UiEvidenceUnavailable(Exception):
    """The baseline cannot supply UI evidence: stable `code`, human `detail` and the corrective action."""

    def __init__(self, code: str, detail: str, action: str = "") -> None:
        super().__init__(f"{code}: {detail}")
        self.code, self.detail = code, detail
        self.action = action or "re-run `analyze`/`full` once on the source repository with this LegacyMapper version to persist UI Evidence"

    def to_dict(self) -> dict:
        return {"status": "UI_EVIDENCE_UNAVAILABLE", "code": self.code, "message": self.detail, "action": self.action}


class PersistedMarkup:
    """Control tree of one view rebuilt from persisted Evidence (same surface the wireframe uses: `controls`, `skeleton()`, `table_count`)."""

    def __init__(self, controls: list[MarkupControl], skeleton: list, table_count: int, placeholders: list[dict]) -> None:
        self.controls, self._skeleton, self.table_count, self.placeholders = controls, skeleton, table_count, placeholders

    def skeleton(self) -> list:
        return self._skeleton


@dataclass
class UiEvidence:
    """Indexed view of the persisted `ui_*` partitions plus the manifest provenance."""

    baseline_dir: Path
    manifest: dict
    documents: dict = field(default_factory=dict)            # norm logical path -> UiDocument record
    controls: dict = field(default_factory=lambda: defaultdict(list))      # document id -> [UiControl]
    events: dict = field(default_factory=lambda: defaultdict(list))
    messages: dict = field(default_factory=lambda: defaultdict(list))
    parameters: dict = field(default_factory=lambda: defaultdict(list))
    navigation: list = field(default_factory=list)           # invocation edges, scanner order
    structural_edges: list = field(default_factory=list)     # uses_master / hosts_user_control / loads_user_control
    stylesheet_files: dict = field(default_factory=dict)     # record id -> stylesheet_file
    stylesheet_links: dict = field(default_factory=lambda: defaultdict(list))   # document id -> [link]
    style_profiles: dict = field(default_factory=dict)       # profile id -> shared style profile record
    asset_files: dict = field(default_factory=dict)          # record id -> asset_file
    asset_refs: dict = field(default_factory=dict)           # (norm document path, literal) -> asset_reference
    asset_refs_by_doc: dict = field(default_factory=lambda: defaultdict(list))
    theme_refs: dict = field(default_factory=lambda: defaultdict(list))
    line_counts: dict = field(default_factory=dict)          # norm logical path -> number of lines (for `src:file:line` validation)

    # ---- per-view reconstruction (same shapes the explainer already consumed)
    def document(self, path: str) -> dict | None:
        return self.documents.get(norm_logical_path(path))

    def markup(self, doc: dict) -> PersistedMarkup:
        controls = []
        for rec in self.controls.get(doc["id"], []):
            p = rec["properties"]
            controls.append(MarkupControl(id=p["control_id"], tag=p["tag"], kind=p["control_kind"], label=p["label"], line=p["line"],
                                          visible=p["visible_initially"], attrs=dict(p["attrs"]), columns=list(p["columns"]), bound_to=p["bound_to"]))
        props = doc["properties"]
        return PersistedMarkup(controls, props["skeleton"], props["table_count"], props.get("placeholders", []))

    def code_facts(self, doc: dict, code_file: str) -> CodeFacts:
        props = doc["properties"]
        facts = CodeFacts(file=code_file, subs=[dict(s) for s in props["subs"]], declared=[dict(d) for d in props["declared_controls"]],
                          imports=list(props["imports"]), script_blocks=props["script_blocks"], visible_toggles=props["visible_toggles"])
        for rec in self.parameters.get(doc["id"], []):
            p = rec["properties"]
            if p["via"] == "Session":
                facts.session_keys.append(p["name"])
            else:
                facts.receives.append({"name": p["name"], "line": p["line"], "via": p["via"]})
        facts.session_keys = sorted(set(facts.session_keys))
        for rec in self.messages.get(doc["id"], []):
            p = rec["properties"]
            if p["origin"] == "code_behind" and p["message_kind"] in _CODE_MESSAGE_KINDS:
                facts.messages.append({"kind": p["message_kind"], "text": p["text"], "line": p["line"], "event": p["event"]})
        return facts

    def navigation_hits(self) -> list[NavHit]:
        return [NavHit(r["properties"]["file_as_scanned"], r["properties"]["line"], r["properties"]["target_folder"], r["properties"]["target_view"],
                       list(r["properties"]["parameters"]), r["properties"]["mechanism"]) for r in self.navigation]

    def menu_entries_for(self, doc: dict) -> list[dict]:
        """Menu / configuration entries whose literal target resolves (CONFIRMED or ambiguous) to this document."""
        return [e for e in self.structural_edges if e["properties"]["relation"] == "menu_entry" and doc["id"] in e["relationships"]["target_document_ids"]]

    def mentions(self, path: str) -> set[str]:
        doc = self.document(path)
        return {norm_logical_path(m) for m in (doc["properties"]["mentions_views"] if doc else [])}

    def lines_of(self, rel: str) -> int:
        return self.line_counts.get(norm_logical_path(rel), 0)

    def style_catalog(self):
        cat = StyleCatalog.from_evidence(self)
        cat.icon_resolver = lambda view_file, url: icon_of(self, view_file, url)   # data flows ui_evidence -> styles, never back
        return cat

    def view_summary(self, doc: dict) -> dict:
        """Bounded, structured summary of the persisted host chain / assets / style references of one view (used by the AI context)."""
        rel = doc["relationships"]
        refs = self.asset_refs_by_doc.get(doc["id"], [])
        known = {name for rec in self.stylesheet_files.values() for name in rec["properties"]["rules"]}
        classes, undefined = set(), set()
        for ctl in self.controls.get(doc["id"], []):
            style = self.style_profiles.get(ctl["relationships"].get("style_profile") or "")
            for c in (style["properties"]["classes"] if style else []):
                if not c["inferred_from_tipo"]:
                    classes.add(c["name"])
                    if c["name"] not in known:
                        undefined.add(c["name"])
        master = rel.get("master_page") or {}
        return {
            "hosts": sorted({h["logical_source_path"] for h in rel.get("hosts", [])}, key=str.lower), "host_resolution": rel.get("host_resolution", "NONE"),
            "master_literal": master.get("literal", ""), "master_status": master.get("status", ""),
            "registered_controls": [{"literal": r["literal"], "status": r["status"]} for r in rel.get("registered_controls", [])],
            "assets_total": len(refs), "assets_unresolved": sorted({r["properties"]["literal"] for r in refs if r["status"] != CONFIRMED}),
            "stylesheets": [l["properties"]["href"] for l in self.stylesheet_links.get(doc["id"], [])],
            "css_classes": sorted(classes), "css_classes_undefined": sorted(undefined),
        }

    def source_hashes(self) -> dict:
        """Logical path -> sha256 of the analyzed source file (from the persisted `source_artifacts` partition)."""
        path = self.baseline_dir / "evidence" / "source_artifacts.json"
        try:
            return {a["path"]: a["sha256"] for a in json.loads(path.read_text(encoding="utf-8"))}
        except (OSError, ValueError, KeyError):
            return {}


def _read_partition(evidence_dir: Path, name: str, expected_sha: str) -> list[dict]:
    path = evidence_dir / f"{name}.json"
    if not path.is_file():
        raise UiEvidenceUnavailable("UI_EVIDENCE_PARTITION_MISSING", name)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise UiEvidenceUnavailable("UI_EVIDENCE_PARTITION_CORRUPT", name, "the partition does not match EVIDENCE_MANIFEST.json; regenerate the baseline")
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, list):
        raise UiEvidenceUnavailable("UI_EVIDENCE_PARTITION_CORRUPT", f"{name}: not a list")
    return data


def load_cross_project_calls(baseline_dir: str | Path) -> list[dict]:
    """Persisted cross-project call resolutions (Gate C); empty list for baselines that predate the partition. Hash-verified."""
    evidence_dir = Path(baseline_dir) / "evidence"
    try:
        manifest = json.loads((evidence_dir / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    expected = (manifest.get("partition_sha256") or {}).get("cross_project_calls")
    if not expected:
        return []
    return _read_partition(evidence_dir, "cross_project_calls", expected)


def load_ui_evidence(baseline_dir: str | Path) -> UiEvidence:
    root = Path(baseline_dir)
    evidence_dir = root / "evidence"
    manifest_path = evidence_dir / "EVIDENCE_MANIFEST.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise UiEvidenceUnavailable("EVIDENCE_MANIFEST_MISSING", str(manifest_path.name)) from None
    version = manifest.get("ui_evidence_schema_version")
    hashes = manifest.get("partition_sha256") or {}
    if version is None or any(name not in hashes for name in UI_PARTITIONS):
        raise UiEvidenceUnavailable("UI_EVIDENCE_MISSING", "the baseline predates the UI/navigation/style Evidence extension (Gate B)")
    if str(version) != UI_EVIDENCE_SCHEMA_VERSION:
        raise UiEvidenceUnavailable("UI_EVIDENCE_SCHEMA_UNSUPPORTED", f"{version}!={UI_EVIDENCE_SCHEMA_VERSION}",
                                    "regenerate the baseline with a LegacyMapper version that writes this UI Evidence schema")
    partitions = {name: _read_partition(evidence_dir, name, hashes[name]) for name in UI_PARTITIONS}
    return index_ui_evidence(partitions, root, manifest)


def index_ui_evidence(partitions: dict, baseline_dir: str | Path = ".", manifest: dict | None = None) -> UiEvidence:
    """Indexes `ui_*` partitions (already verified, or produced in memory by the extractor in tests) into a `UiEvidence`."""
    ui = UiEvidence(Path(baseline_dir), manifest or {})
    for rec in partitions[PARTITION_DOCUMENTS]:
        ui.documents[norm_logical_path(rec["logical_source_path"])] = rec
        ui.line_counts[norm_logical_path(rec["logical_source_path"])] = rec["properties"]["line_count"]
        cb = rec["properties"].get("code_behind")
        if cb:
            ui.line_counts[norm_logical_path(cb["logical_source_path"])] = cb["line_count"]
    for rec in partitions[PARTITION_CONTROLS]:
        ui.controls[rec["relationships"]["document_id"]].append(rec)
    for rec in partitions[PARTITION_EVENTS]:
        ui.events[rec["relationships"]["document_id"]].append(rec)
    for rec in partitions[PARTITION_MESSAGES]:
        ui.messages[rec["relationships"]["document_id"]].append(rec)
    for rec in partitions[PARTITION_PARAMETERS]:
        ui.parameters[rec["relationships"]["document_id"]].append(rec)
    for rec in partitions[PARTITION_NAVIGATION]:
        if rec["properties"]["relation"] == "invocation":
            ui.navigation.append(rec)
            ui.line_counts.setdefault(norm_logical_path(rec["logical_source_path"]), rec["properties"]["source_line_count"])
        else:
            ui.structural_edges.append(rec)
            if rec["properties"]["relation"] == "menu_entry":
                ui.line_counts.setdefault(norm_logical_path(rec["logical_source_path"]), rec["properties"]["source_line_count"])
    docs_by_id = {d["id"]: d for d in ui.documents.values()}
    for rec in partitions[PARTITION_STYLES]:
        kind = rec["properties"]["style_kind"]
        if kind == "stylesheet_file":
            ui.stylesheet_files[rec["id"]] = rec
        elif kind == "stylesheet_link":
            ui.stylesheet_links[rec["relationships"]["document_id"]].append(rec)
        elif kind == "style_profile":
            ui.style_profiles[rec["id"]] = rec
        elif kind == "theme_reference":
            ui.theme_refs[rec["relationships"]["document_id"]].append(rec)
    for rec in partitions[PARTITION_ASSETS]:
        if rec["properties"]["asset_kind"] == "asset_file":
            ui.asset_files[rec["id"]] = rec
        else:
            doc = docs_by_id.get(rec["relationships"]["document_id"])
            ui.asset_refs[(norm_logical_path(doc["logical_source_path"]) if doc else "", rec["properties"]["literal"])] = rec
            ui.asset_refs_by_doc[rec["relationships"]["document_id"]].append(rec)
    return ui


def icon_of(ui: UiEvidence, view_markup_file: str, image_url: str) -> tuple[str | None, str]:
    """(data URI or None, reason) from persisted asset evidence; the message vocabulary is the one the wireframe report already used."""
    if not image_url:
        return None, "sin imagen"
    ref = ui.asset_refs.get((norm_logical_path(view_markup_file), image_url))
    if ref is None:
        return None, "sin evidencia persistida"
    p = ref["properties"]
    if ref["status"] != CONFIRMED:
        return None, _ICON_REASONS.get(p.get("reason", ""), "no encontrada")
    asset = ui.asset_files.get(ref["relationships"]["asset_file"])
    if asset is None or not asset["properties"]["embedded"]:
        return None, _ICON_REASONS["TOO_LARGE_TO_EMBED"]
    return f"data:{asset['properties']['mime']};base64,{asset['properties']['data_base64']}", "resuelta"
