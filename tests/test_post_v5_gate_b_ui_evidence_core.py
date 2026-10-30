"""Post-V5 pre-H5 Gate B: UI / navigation / style facts are authoritative, versioned Evidence Core; downstream never rereads source.

Directed tests only. No real provider is ever resolved or called. The repository used for the analysis is PHYSICALLY RENAMED away
right after the deterministic run, so every downstream assertion in this module runs with the source unavailable.
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from legacy_documenter.adapters.vbnet_webforms_oracle.ui_extraction import UiEvidenceExtractor, parse_codebehind, parse_markup, scan_navigation
from legacy_documenter.behavior import ai as A
from legacy_documenter.behavior.prototype import build, main as behavior_main, write_package
from legacy_documenter.behavior.ui_evidence import UiEvidenceUnavailable, index_ui_evidence, load_ui_evidence
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.evidence.invariants import InvariantViolation, validate_ui_evidence
from legacy_documenter.evidence.bundle import NormalizedEvidence
from legacy_documenter.evidence.ui_model import UI_PARTITIONS, UI_EVIDENCE_SCHEMA_VERSION
from legacy_documenter.main import main as cli_main

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "legacy_documenter"
FIXTURE = Path(__file__).parent / "fixtures" / "v4_2_r7_full_sample"

SITE_CSS = ".Boton{background-color:#2E75B6;color:#FFFFFF;width:120px}\n.Titulo{font:bold 15px Arial;color:#661a87}\n"
SHELL = '<html><head><link href="Web/Styles/site.css" type="text/css" rel="stylesheet"></head><body></body></html>'
MASTER = ('<%@ Master Language="VB" %>\n<html><head><link href="Styles/site.css" rel="stylesheet"></head><body>'
          '<asp:ContentPlaceHolder ID="cphMain" runat="server"></asp:ContentPlaceHolder></body></html>')
PICK_ASCX = """<%@ Control Language="vb" CodeBehind="PickCustomer.ascx.vb" Inherits="SampleLegacy.Web.PickCustomer" %>
<asp:Panel ID="pnlFiltro" runat="server" CssClass="Titulo">
<table id="tabMain"><tr><td><snt:Label ID="lblTitulo" Tipo="Titulo" runat="server">Buscar Cliente</snt:Label></td></tr>
<tr><td><snt:TextBoxAdv ID="txtCrit" runat="server"></snt:TextBoxAdv>
<asp:RequiredFieldValidator ID="rfvCrit" ControlToValidate="txtCrit" ErrorMessage="Debe indicar un criterio" runat="server" /></td>
<td><asp:Button ID="btnSearch" runat="server" Text="Buscar" OnClick="btnSearch_Click" CssClass="Boton Inexistente" style="width:90px" />
<snt:HyperLink ID="icoOk" runat="server" ImageUrl="img/ok.gif" /><snt:HyperLink ID="icoMiss" runat="server" ImageUrl="img/missing.gif" /></td></tr>
<tr><td colspan="2"><snt:TablaPaginada ID="grdCust" runat="server" NombreMetodo="txbuscarclientes" NombreCompletoClase="SampleLegacy.BL.CustomerService">
<snt:TablaPaginadaColumna Titulo="Codigo" /><snt:TablaPaginadaColumna Titulo="Nombre" /></snt:TablaPaginada></td></tr></table></asp:Panel>
"""
PICK_VB = """Public Class PickCustomer
    Inherits System.Web.UI.UserControl
    Protected WithEvents btnSearch As System.Web.UI.WebControls.Button
    Private Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles MyBase.Load
        Dim target As String = Request.QueryString.Item("ctrvis")
        Dim who As String = CStr(Session("ID_USER"))
    End Sub
    Private Sub btnSearch_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnSearch.Click
        MsgBox("Sin resultados para el criterio")
        MsgBox(texto)
    End Sub
End Class
"""
HOST_ONE = """<%@ Page Language="VB" MasterPageFile="Site.master" CodeBehind="HostOne.aspx.vb" Inherits="SampleLegacy.Web.HostOne" %>
<%@ Register TagPrefix="uc" TagName="Pick" Src="PickCustomer.ascx" %>
<asp:Content ID="c1" ContentPlaceHolderID="cphMain" runat="server"><uc:Pick ID="pk" runat="server" /></asp:Content>
"""
HOST_ONE_VB = """Public Class HostOne
    Protected Sub Open_Click()
        Me.lnkPick.Attributes("href") = "javascript:OnClickWindowOpen('default.aspx?url=Web/PickCustomer&selrow=S&ctrvis=1','vPick','600','400');"
        Me.lnkGhost.Attributes("href") = "javascript:OnClickWindowOpen('default.aspx?url=Web/GhostView&selrow=S','vGhost','600','400');"
        Me.lnkDup.NavigateUrl = "default.aspx?url=Area/Dup&id=1"
    End Sub
End Class
"""
HOST_TWO = """<%@ Page Language="VB" %>
<%@ Register TagPrefix="uc" TagName="Pick" Src="PickCustomer.ascx" %>
<uc:Pick ID="pk2" runat="server" />
"""
DUP = '<%@ Control Language="vb" %>\n<asp:Label ID="lblDup" runat="server" Text="Dup" />\n'
GIF = b"GIF89a\x01\x00\x01\x00\x00\x00\x00;"


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a, **k)


def make_repo(parent: Path, name: str = "repo") -> Path:
    repo = parent / name
    shutil.copytree(FIXTURE, repo)
    web = repo / "Web"
    (repo / "default.aspx").write_text(SHELL, encoding="utf-8")
    (web / "Styles").mkdir()
    (web / "Styles" / "site.css").write_text(SITE_CSS, encoding="utf-8")
    (web / "img").mkdir()
    (web / "img" / "ok.gif").write_bytes(GIF)
    (web / "Site.master").write_text(MASTER, encoding="utf-8")
    (web / "PickCustomer.ascx").write_text(PICK_ASCX, encoding="utf-8")
    (web / "PickCustomer.ascx.vb").write_text(PICK_VB, encoding="utf-8")
    (web / "HostOne.aspx").write_text(HOST_ONE, encoding="utf-8")
    (web / "HostOne.aspx.vb").write_text(HOST_ONE_VB, encoding="utf-8")
    (web / "HostTwo.aspx").write_text(HOST_TWO, encoding="utf-8")
    for folder in ("Web/Area", "Other/Area"):
        (repo / folder).mkdir(parents=True, exist_ok=True)
        (repo / folder / "Dup.ascx").write_text(DUP, encoding="utf-8")
    items = "".join(f'<Content Include="{n}" />' for n in ("CustomerPage.aspx", "PickCustomer.ascx", "HostOne.aspx", "HostTwo.aspx", "Area\\Dup.ascx"))
    (web / "Web.vbproj").write_text(
        '<Project><PropertyGroup><RootNamespace>SampleLegacy.Web</RootNamespace></PropertyGroup><ItemGroup>'
        '<Compile Include="CustomerPage.aspx.vb" /><Compile Include="PickCustomer.ascx.vb" /><Compile Include="HostOne.aspx.vb" />' + items +
        '</ItemGroup></Project>', encoding="utf-8")
    return repo


def read_partitions(baseline: Path) -> dict[str, list[dict]]:
    return {name: json.loads((baseline / "evidence" / f"{name}.json").read_text(encoding="utf-8")) for name in UI_PARTITIONS}


class GateBBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="gateb_"))
        cls.repo = make_repo(cls.tmp)
        cls.baseline = cls.tmp / "baseline"
        assert quiet(run_full_pipeline, cls.repo, cls.baseline, [], 12).status.value == "SUCCESS"
        cls.removed = cls.tmp / "repo.removed"
        cls.repo.rename(cls.removed)                         # the source repository is now physically unavailable
        cls.parts = read_partitions(cls.baseline)
        cls.manifest = json.loads((cls.baseline / "evidence" / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def doc(self, name: str) -> dict:
        return next(d for d in self.parts["ui_documents"] if d["logical_source_path"].lower().endswith(name.lower()))

    def controls_of(self, doc: dict) -> dict:
        return {c["properties"]["control_id"]: c for c in self.parts["ui_controls"] if c["relationships"]["document_id"] == doc["id"]}


class PersistedUiEvidenceTests(GateBBase):
    def test_manifest_declares_the_additive_ui_extension_and_core_schema_is_unchanged(self):
        self.assertEqual(self.manifest["evidence_schema_version"], "1.0")
        self.assertEqual(self.manifest["ui_evidence_schema_version"], UI_EVIDENCE_SCHEMA_VERSION)
        self.assertEqual(self.manifest["ui_evidence"]["partitions"], list(UI_PARTITIONS))
        for name in UI_PARTITIONS:
            data = (self.baseline / "evidence" / f"{name}.json").read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), self.manifest["partition_sha256"][name])

    def test_every_record_carries_the_minimum_contract(self):
        for name in UI_PARTITIONS:
            for rec in self.parts[name]:
                for key in ("id", "kind", "status", "properties", "relationships"):
                    self.assertIn(key, rec, (name, key))
                if "source_refs" in rec:                                    # self-sourced record
                    self.assertTrue(rec["source_refs"])
                    self.assertIn("logical_source_path", rec)
                else:                                                       # child fact: provenance through its document (schema 1.1)
                    self.assertIn(rec["relationships"].get("source_scope"), ("markup", "code_behind", "shared"))
                    if rec["relationships"]["source_scope"] != "shared":
                        self.assertIn(rec["relationships"]["document_id"], {d["id"] for d in self.parts["ui_documents"]})
                self.assertIn(rec["status"], ("CONFIRMED", "INFERRED", "UNRESOLVED"))

    def test_controls_labels_and_kinds_are_persisted(self):
        ctl = self.controls_of(self.doc("PickCustomer.ascx"))
        self.assertEqual({"pnlFiltro", "lblTitulo", "txtCrit", "rfvCrit", "btnSearch", "icoOk", "icoMiss", "grdCust"}, set(ctl))
        self.assertEqual(ctl["lblTitulo"]["properties"]["label"], "Buscar Cliente")
        self.assertEqual(ctl["btnSearch"]["properties"]["control_kind"], "button")
        self.assertEqual(ctl["grdCust"]["properties"]["control_kind"], "grid")
        self.assertEqual(ctl["grdCust"]["properties"]["columns"], ["Codigo", "Nombre"])
        self.assertEqual(ctl["grdCust"]["properties"]["bound_to"], "SampleLegacy.BL.CustomerService.txbuscarclientes")
        self.assertEqual(ctl["pnlFiltro"]["properties"]["control_kind"], "panel")

    def test_container_relations_validator_and_event_attribute_are_persisted(self):
        ctl = self.controls_of(self.doc("PickCustomer.ascx"))
        self.assertIsNotNone(ctl["txtCrit"]["properties"]["container"])
        self.assertEqual(ctl["txtCrit"]["properties"]["container"]["row"], 1)
        self.assertEqual(ctl["rfvCrit"]["relationships"]["validates"], "txtCrit")
        self.assertEqual(ctl["btnSearch"]["relationships"]["server_events"], {"onclick": "btnSearch_Click"})
        self.assertGreaterEqual(self.doc("PickCustomer.ascx")["properties"]["table_count"], 1)

    def test_event_bindings_cover_handles_clauses_and_markup_attributes(self):
        doc = self.doc("PickCustomer.ascx")
        events = [e for e in self.parts["ui_event_bindings"] if e["relationships"]["document_id"] == doc["id"]]
        origins = {(e["properties"]["origin"], e["properties"]["handler"]) for e in events}
        self.assertIn(("handles_clause", "btnSearch_Click"), origins)
        self.assertIn(("handles_clause", "Page_Load"), origins)
        self.assertIn(("markup_attribute", "btnSearch_Click"), origins)
        markup = next(e for e in events if e["properties"]["origin"] == "markup_attribute")
        self.assertTrue(markup["properties"]["handler_defined"])
        self.assertEqual(markup["status"], "CONFIRMED")

    def test_messages_literal_dynamic_and_validator_are_distinguished(self):
        doc = self.doc("PickCustomer.ascx")
        msgs = [m["properties"] for m in self.parts["ui_messages"] if m["relationships"]["document_id"] == doc["id"]]
        by_kind = {(m["message_kind"], m["text_kind"], m["text"]) for m in msgs}
        self.assertIn(("msgbox", "literal", "Sin resultados para el criterio"), by_kind)
        self.assertIn(("msgbox", "dynamic", ""), by_kind)                     # MsgBox(texto): not a static message, never invented
        self.assertIn(("validator_message", "literal", "Debe indicar un criterio"), by_kind)

    def test_parameters_querystring_and_session_keys_are_persisted(self):
        doc = self.doc("PickCustomer.ascx")
        params = {(p["properties"]["via"], p["properties"]["name"]) for p in self.parts["ui_parameters"] if p["relationships"]["document_id"] == doc["id"]}
        self.assertEqual(params, {("QueryString", "ctrvis"), ("Session", "ID_USER")})

    def test_navigation_keeps_confirmed_inferred_and_unresolved_targets(self):
        inv = [n for n in self.parts["ui_navigation"] if n["properties"]["relation"] == "invocation"]
        by_target = {n["properties"]["target_literal"]: n for n in inv}
        self.assertEqual(by_target["Web/PickCustomer"]["status"], "CONFIRMED")
        self.assertEqual(by_target["Web/PickCustomer"]["properties"]["mechanism"], "window_open")
        self.assertEqual(by_target["Web/PickCustomer"]["properties"]["parameters"], ["selrow", "ctrvis"])
        ghost = by_target["Web/GhostView"]
        self.assertEqual(ghost["status"], "UNRESOLVED")                      # a missing target is preserved, never dropped
        self.assertEqual(ghost["properties"]["target_candidates"], [])
        self.assertEqual(ghost["relationships"]["target_document_ids"], [])
        dup = by_target["Area/Dup"]
        self.assertEqual(dup["status"], "INFERRED")                          # ambiguous: two views match, none is chosen
        self.assertEqual(len(dup["properties"]["target_candidates"]), 2)
        self.assertEqual(dup["properties"]["mechanism"], "navigate_url")

    def test_structural_relations_master_register_and_host_chain(self):
        nav = self.parts["ui_navigation"]
        uses_master = [n for n in nav if n["properties"]["relation"] == "uses_master"]
        self.assertTrue(any(n["logical_source_path"].endswith("HostOne.aspx") and n["status"] == "CONFIRMED" for n in uses_master))
        hosts = [n for n in nav if n["properties"]["relation"] == "hosts_user_control"]
        self.assertEqual(sorted(n["logical_source_path"].rsplit("/", 1)[-1] for n in hosts), ["HostOne.aspx", "HostTwo.aspx"])
        pick = self.doc("PickCustomer.ascx")
        self.assertEqual(pick["relationships"]["host_resolution"], "AMBIGUOUS")  # two hosts: no host is chosen without evidence
        self.assertEqual(pick["relationships"]["host_status"], "INFERRED")
        self.assertEqual(len(pick["relationships"]["hosts"]), 2)
        self.assertEqual(self.doc("HostOne.aspx")["relationships"]["master_page"]["status"], "CONFIRMED")

    def test_style_references_classes_inline_stylesheet_chain_and_undefined_classes(self):
        files = {r["logical_source_path"]: r for r in self.parts["ui_style_references"] if r["properties"]["style_kind"] == "stylesheet_file"}
        self.assertEqual(list(files), ["Web/Styles/site.css"])
        self.assertIn("Boton", files["Web/Styles/site.css"]["properties"]["rules"])
        links = [r for r in self.parts["ui_style_references"] if r["properties"]["style_kind"] == "stylesheet_link"]
        docs = {d["id"]: d["logical_source_path"] for d in self.parts["ui_documents"]}
        self.assertEqual({(docs[l["relationships"]["document_id"]], l["properties"]["resolved_logical_path"]) for l in links},
                         {("default.aspx", "Web/Styles/site.css"), ("Web/Site.master", "Web/Styles/site.css")})
        self.assertTrue(next(l for l in links if docs[l["relationships"]["document_id"]] == "default.aspx")["properties"]["shell_candidate"])
        ctl = self.controls_of(self.doc("PickCustomer.ascx"))
        style = next(r for r in self.parts["ui_style_references"] if r["id"] == ctl["btnSearch"]["relationships"]["style_profile"])
        self.assertEqual([c["name"] for c in style["properties"]["classes"]], ["Boton", "Inexistente"])
        self.assertEqual(style["properties"]["inline_style"], "width:90px")
        self.assertEqual(style["properties"]["inline_declarations"], {"width": 90})
        ui = load_ui_evidence(self.baseline)
        summary = ui.view_summary(ui.document("Web/PickCustomer.ascx"))
        self.assertEqual(summary["css_classes_undefined"], ["Inexistente"])    # defined nowhere in the persisted sheets: preserved
        self.assertEqual(summary["host_resolution"], "AMBIGUOUS")

    def test_assets_resolved_and_unresolved_are_persisted_with_content_hash(self):
        refs = {a["properties"]["literal"]: a for a in self.parts["ui_assets"] if a["properties"]["asset_kind"] == "asset_reference"}
        self.assertEqual(refs["img/ok.gif"]["status"], "CONFIRMED")
        self.assertEqual(refs["img/missing.gif"]["status"], "UNRESOLVED")
        self.assertEqual(refs["img/missing.gif"]["properties"]["reason"], "NOT_FOUND")
        asset = next(a for a in self.parts["ui_assets"] if a["properties"]["asset_kind"] == "asset_file")
        self.assertEqual(asset["logical_source_path"], "Web/img/ok.gif")
        self.assertEqual(asset["properties"]["sha256"], hashlib.sha256(GIF).hexdigest())

    def test_name_mentions_for_usage_classification_are_persisted(self):
        host = self.doc("HostOne.aspx")
        self.assertIn("Web/PickCustomer.ascx", host["properties"]["mentions_views"])


class ParityWithDirectSourceParseTests(GateBBase):
    """The persisted records reproduce exactly what the previous read-the-source flow produced (same parsers, same order)."""

    def test_controls_code_facts_and_navigation_match_a_direct_parse(self):
        ui = load_ui_evidence(self.baseline)
        for rel, code_rel in (("Web/PickCustomer.ascx", "Web/PickCustomer.ascx.vb"), ("Web/HostOne.aspx", "Web/HostOne.aspx.vb")):
            text = (self.removed / rel).read_text(encoding="utf-8")
            direct = parse_markup(text)
            persisted = ui.markup(ui.document(rel))
            self.assertEqual([(c.id, c.tag, c.kind, c.label, c.line, c.visible, c.attrs, c.columns, c.bound_to) for c in persisted.controls],
                             [(c.id, c.tag, c.kind, c.label, c.line, c.visible, c.attrs, c.columns, c.bound_to) for c in direct.controls])
            self.assertEqual(json.loads(json.dumps(persisted.skeleton())), json.loads(json.dumps(direct.skeleton())))
            code = parse_codebehind((self.removed / code_rel).read_text(encoding="utf-8"), code_rel)
            facts = ui.code_facts(ui.document(rel), code_rel)
            self.assertEqual((facts.subs, facts.declared, facts.receives, facts.session_keys, facts.messages, facts.imports, facts.script_blocks,
                              facts.visible_toggles),
                             (code.subs, code.declared, code.receives, code.session_keys, code.messages, code.imports, code.script_blocks, code.visible_toggles))
        files = json.loads((self.baseline / "index" / "files.json").read_text(encoding="utf-8"))
        hits = scan_navigation(self.removed, [f["relative_path"] for f in files])
        self.assertEqual([(h.file, h.line, h.folder, h.view, h.params, h.mechanism) for h in ui.navigation_hits()],
                         [(h.file, h.line, h.folder, h.view, h.params, h.mechanism) for h in hits])


class AnalyzeOnceDownstreamTests(GateBBase):
    """Gate B hard gate: analyze, persist, remove the source, then run every downstream command from the persisted output."""

    def guarded(self, fn):
        read_attempts: list[str] = []
        roots = (str(self.repo), str(self.removed))
        original = {name: getattr(Path, name) for name in ("read_bytes", "read_text", "open", "is_file", "exists", "stat", "iterdir")}

        def spy(name):
            def wrapper(self_path, *a, **k):
                if str(self_path).startswith(roots):
                    read_attempts.append(f"{name}:{self_path}")
                return original[name](self_path, *a, **k)
            return wrapper

        patches = [mock.patch.object(Path, n, spy(n)) for n in original]
        seams = {"scan": mock.patch("legacy_documenter.scanner.repository_scanner.RepositoryScanner.scan"),
                 "extract": mock.patch("legacy_documenter.cli.pipeline_stages.extract_repository"),
                 "provider": mock.patch("legacy_documenter.llm.registry.ProviderRegistry.create")}
        started = {k: m.start() for k, m in seams.items()}
        for p in patches:
            p.start()
        try:
            result = fn()
        finally:
            for p in patches:
                p.stop()
            for m in seams.values():
                m.stop()
        return result, read_attempts, started

    def test_behavioral_documentation_runs_with_the_source_gone_and_zero_source_reads(self):
        self.assertFalse(self.repo.exists())
        out = self.tmp / "behavior_out"
        (code, read_attempts, seams) = self.guarded(lambda: quiet(behavior_main, [str(self.baseline), "--output", str(out), "--no-pdf"]))
        self.assertEqual(code, 0)
        self.assertEqual(read_attempts, [])                                   # source_reads = 0
        for seam in seams.values():
            seam.assert_not_called()                                         # scanner = 0, analyzer = 0, provider = 0
        names = {p.name for p in out.iterdir()}
        self.assertIn("index.html", names)
        sidecar = json.loads((out / "ui_navigation_evidence.json").read_text(encoding="utf-8"))
        self.assertFalse(sidecar["authoritative"])
        self.assertEqual(sidecar["role"], "derived_projection")

    def test_build_ignores_a_stale_repository_argument(self):
        doc, bc, _violations, explained = build(self.baseline, self.removed / "does-not-exist", project="Web", solution="SampleLegacy", pilot_count=2)
        self.assertEqual(bc.source_reads, 0)
        self.assertTrue(explained)
        pick = next(v for v in explained.values() if v.name == "PickCustomer")
        self.assertEqual(pick.ui.status, "DOCUMENTARY_RECONSTRUCTION")
        self.assertEqual(sorted(i.mechanism for i in pick.reached_by), ["window_open"])
        self.assertTrue(any(i.target_exists is False for v in explained.values() for i in v.reaches))   # GhostView stays a dangling target
        icon_report = pick.ui.style_report
        self.assertEqual((icon_report["icons_total"], icon_report["icons_resolved"]), (2, 1))
        self.assertIn("data:image/gif;base64,", pick.ui.svg)                 # the icon bytes come from Evidence, not from disk

    def test_docs_visuals_deliver_and_interpret_run_from_persisted_output(self):
        def run():
            results = {}
            results["docs"] = cli_main(["docs", str(self.baseline), "--output", str(self.tmp / "docs")])
            results["visuals"] = cli_main(["visuals", str(self.baseline), "--output", str(self.tmp / "visuals")])
            results["deliver"] = cli_main(["deliver", str(self.baseline), "--output", str(self.tmp / "deliver")])
            return results

        results, read_attempts, seams = self.guarded(lambda: quiet(run))
        self.assertEqual(results, {"docs": 0, "visuals": 0, "deliver": 0})
        self.assertEqual(read_attempts, [])
        for name in ("scan", "extract"):
            seams[name].assert_not_called()

    def test_interpret_runs_over_the_persisted_baseline_with_the_source_gone(self):
        from legacy_documenter.orchestration.ai_only import run_ai_only
        from tests.test_post_v5_h4_r5_behavioral_ai import ScriptedProvider
        provider = ScriptedProvider([])                                       # test double: no real provider is ever resolved
        with mock.patch("legacy_documenter.scanner.repository_scanner.RepositoryScanner.scan") as scan,                 mock.patch("legacy_documenter.cli.pipeline_stages.extract_repository") as extract:
            result = quiet(run_ai_only, self.baseline, self.tmp / "ai_run", provider)
        self.assertNotEqual(result.status, "AI_ONLY_INPUT_INVALID")          # the persisted baseline is a valid, complete input
        scan.assert_not_called()
        extract.assert_not_called()

    def test_ai_context_is_built_from_persisted_evidence(self):
        doc, bc, _v, explained = build(self.baseline, None, project="Web", solution="SampleLegacy", pilot_count=2)
        pick = next(v for v in explained.values() if v.name == "PickCustomer")
        context, scope = A.view_context(bc, pick, {"solution": "SampleLegacy", "project": "Web", "path": bc.project_path, "refs": []})
        kinds = {f["kind"] for f in context["facts"]}
        self.assertTrue({"host_chain", "assets", "styles", "message", "parameter"} <= kinds)
        host = next(f for f in context["facts"] if f["kind"] == "host_chain")
        self.assertIn("AMBIGUOUS", host["fact"])
        self.assertIn(host["ref"], scope["allowed_refs"])                    # the validator still accepts only real references
        self.assertLess(len(json.dumps(context, ensure_ascii=False)), 20000) # bounded, structured; no raw repository files


class SchemaAndCompatibilityTests(GateBBase):
    def clone(self, mutate) -> Path:
        target = self.tmp / f"clone_{len(list(self.tmp.glob('clone_*')))}"
        shutil.copytree(self.baseline, target, ignore=shutil.ignore_patterns("_cache_v53"))
        mutate(target)
        return target

    def test_old_baseline_without_ui_evidence_fails_explicitly(self):
        def mutate(root):
            m = json.loads((root / "evidence" / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))
            for key in ("ui_evidence_schema_version", "ui_evidence"):
                m.pop(key)
            for name in UI_PARTITIONS:
                m["partition_sha256"].pop(name)
                m["entity_counts"].pop(name)
                (root / "evidence" / f"{name}.json").unlink()
            (root / "evidence" / "EVIDENCE_MANIFEST.json").write_text(json.dumps(m, separators=(",", ":")), encoding="utf-8")
        old = self.clone(mutate)
        with self.assertRaises(UiEvidenceUnavailable) as ctx:
            load_ui_evidence(old)
        self.assertEqual(ctx.exception.code, "UI_EVIDENCE_MISSING")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = behavior_main([str(old), "--output", str(self.tmp / "old_out"), "--no-pdf"])
        self.assertEqual(code, 4)
        payload = json.loads(out.getvalue())
        self.assertEqual((payload["status"], payload["code"]), ("UI_EVIDENCE_UNAVAILABLE", "UI_EVIDENCE_MISSING"))
        self.assertIn("re-run", payload["action"])
        self.assertFalse((self.tmp / "old_out" / "index.html").exists())

    def test_unsupported_ui_schema_version_is_not_silently_accepted(self):
        def mutate(root):
            path = root / "evidence" / "EVIDENCE_MANIFEST.json"
            m = json.loads(path.read_text(encoding="utf-8"))
            m["ui_evidence_schema_version"] = "9.9"
            path.write_text(json.dumps(m, separators=(",", ":")), encoding="utf-8")
        with self.assertRaises(UiEvidenceUnavailable) as ctx:
            load_ui_evidence(self.clone(mutate))
        self.assertEqual(ctx.exception.code, "UI_EVIDENCE_SCHEMA_UNSUPPORTED")

    def test_tampered_partition_is_detected_against_the_manifest(self):
        def mutate(root):
            path = root / "evidence" / "ui_controls.json"
            path.write_text(path.read_text(encoding="utf-8").replace("Buscar Cliente", "Otro"), encoding="utf-8")
        with self.assertRaises(UiEvidenceUnavailable) as ctx:
            load_ui_evidence(self.clone(mutate))
        self.assertEqual(ctx.exception.code, "UI_EVIDENCE_PARTITION_CORRUPT")

    def test_invariants_reject_unresolvable_provenance_and_unknown_status(self):
        ev = NormalizedEvidence()
        record = {"id": "UIC-1", "kind": "UiControl", "logical_source_path": "a", "source_refs": ["SRC-nope"], "status": "CONFIRMED",
                  "properties": {}, "relationships": {"document_id": "x"}}
        ev.ui = {name: [] for name in UI_PARTITIONS}
        ev.ui["ui_controls"] = [record]
        with self.assertRaises(InvariantViolation) as ctx:
            validate_ui_evidence(ev)
        self.assertIn("UI-4", str(ctx.exception))
        record["source_refs"] = []
        record["status"] = "MAYBE"
        with self.assertRaises(InvariantViolation) as ctx:
            validate_ui_evidence(ev)
        self.assertIn("UI-3", str(ctx.exception))


class LogicalProvenanceAndDeterminismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="gateb_loc_"))
        cls.runs = {}
        for label, rel in (("a", "first place/ñ one"), ("b", "second/deeper/place")):
            parent = cls.tmp / rel
            parent.mkdir(parents=True)
            repo = make_repo(parent)
            base = cls.tmp / f"base_{label}"
            assert quiet(run_full_pipeline, repo, base, [], 12).status.value == "SUCCESS"
            cls.runs[label] = (repo, base)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_ui_partitions_are_byte_identical_across_physical_locations(self):
        (_, a), (_, b) = self.runs["a"], self.runs["b"]
        for name in UI_PARTITIONS:
            self.assertEqual((a / "evidence" / f"{name}.json").read_bytes(), (b / "evidence" / f"{name}.json").read_bytes(), name)

    def test_ids_do_not_embed_the_physical_path_and_records_carry_no_absolute_path(self):
        repo, base = self.runs["a"]
        needles = {str(repo), str(repo).replace("\\", "/"), str(self.tmp), str(self.tmp).replace("\\", "/")}
        for name in UI_PARTITIONS:
            text = (base / "evidence" / f"{name}.json").read_text(encoding="utf-8")
            for needle in needles:
                self.assertNotIn(needle, text, name)

    def test_logical_source_provenance_is_portable_and_physical_root_is_compatibility_metadata(self):
        (_, a), (_, b) = self.runs["a"], self.runs["b"]
        ma = json.loads((a / "evidence" / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))["source_provenance"]
        mb = json.loads((b / "evidence" / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8"))["source_provenance"]
        self.assertEqual(ma, mb)
        self.assertEqual(ma["physical_root"]["role"], "compatibility_metadata_not_identity")
        self.assertNotIn(str(self.tmp), json.dumps(ma))

    def test_declared_repository_id_changes_ids_but_never_uses_the_path(self):
        repo, _ = self.runs["a"]
        files = json.loads((self.runs["a"][1] / "index" / "files.json").read_text(encoding="utf-8"))
        webforms = json.loads((self.runs["a"][1] / "index" / "webforms.json").read_text(encoding="utf-8"))
        plain = UiEvidenceExtractor(repo, files, webforms, [], None).extract()
        named = UiEvidenceExtractor(repo, files, webforms, [], "sample-repo").extract()
        again = UiEvidenceExtractor(repo, files, webforms, [], "sample-repo").extract()
        self.assertEqual(named, again)
        self.assertNotEqual([d["id"] for d in plain["ui_documents"]], [d["id"] for d in named["ui_documents"]])
        self.assertEqual(len(plain["ui_documents"]), len(named["ui_documents"]))


class ArchitectureBoundaryTests(unittest.TestCase):
    """Source parsing belongs to the deterministic adapter; the behavior, AI, template and deliver layers never read repository files."""

    FORBIDDEN_CALLS = {"read_bytes", "read_text", "open", "scandir", "listdir", "rglob", "glob", "walk"}

    def test_behavior_package_has_no_repository_access_and_no_source_parsers(self):
        for path in sorted((PACKAGE / "behavior").glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr == "repo_root":
                    self.fail(f"{path.name}: repo_root is not part of the behavioral flow")
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in self.FORBIDDEN_CALLS:
                    if path.name == "ai.py" and node.func.attr == "read_text":
                        continue        # ReplayProvider reads the saved answers of an earlier AI run (JSON), never repository files
                    if path.name == "template.py" and node.func.attr in ("read_text", "read_bytes"):
                        continue        # human template resources (template.yaml/document.html/css), not the analyzed repository
                    receiver = ast.unparse(node.func.value)
                    if node.func.attr in ("read_text", "read_bytes") and any(k in receiver for k in ("baseline_dir", "evidence_dir", "manifest_path"))                             or (path.name == "ui_evidence.py" and node.func.attr in ("read_text", "read_bytes") and receiver in ("path", "manifest_path")):
                        continue        # persisted baseline files (index/, evidence/ partitions), never the source repository
                    self.fail(f"{path.name}:{node.lineno}: file access `{node.func.attr}` in the behavioral layer")
                if isinstance(node, ast.ImportFrom) and node.module and "ui_extraction" in node.module:
                    self.fail(f"{path.name}: must not import the deterministic extractor")

    def test_source_parsers_live_in_the_adapter_not_in_behavior(self):
        import legacy_documenter.behavior.source as behavior_source
        for name in ("parse_markup", "parse_codebehind", "scan_navigation", "read_text"):
            self.assertFalse(hasattr(behavior_source, name), name)
        text = (PACKAGE / "behavior" / "styles.py").read_text(encoding="utf-8")
        self.assertNotIn("discover(", text)
        self.assertNotIn("read_bytes", text)

    def test_deliver_ai_and_template_layers_do_not_import_the_extractor(self):
        for folder in ("deliver", "behavior", "templates", "visuals"):
            for path in (PACKAGE / folder).rglob("*.py"):
                for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        self.assertNotIn("ui_extraction", node.module, str(path))
                    if isinstance(node, ast.Import):
                        self.assertFalse(any("ui_extraction" in a.name for a in node.names), str(path))

    def test_extractor_is_in_the_fingerprinted_adapter_layer(self):
        from legacy_documenter import fingerprints
        self.assertIn("adapters", fingerprints.ANALYZER_CODE_DIRECTORIES)
        self.assertTrue((PACKAGE / "adapters" / "vbnet_webforms_oracle" / "ui_extraction.py").is_file())


if __name__ == "__main__":
    unittest.main()
