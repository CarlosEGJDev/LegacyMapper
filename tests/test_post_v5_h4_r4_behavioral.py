"""Post-V5 H4-R4: behavioral documentation prototype (structured explanation, deterministic validation, wireframe, rendering).

Networkless and deterministic. The prototype reads a persisted baseline plus the view sources read-only; no provider is resolved.
"""
from __future__ import annotations

import contextlib
import copy
import io
import json
import shutil
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.behavior import explain as E
from legacy_documenter.behavior import render as R
from legacy_documenter.behavior import validate as V
from legacy_documenter.behavior import wireframe
from legacy_documenter.behavior.model import (
    AI_INTERPRETATION, CANONICAL, CONFIRMED, INFERRED, MODULE_NONE, UNRESOLVED, WIREFRAME_UNAVAILABLE, Claim,
)
from legacy_documenter.behavior.prototype import build, write_package
from legacy_documenter.adapters.vbnet_webforms_oracle.ui_extraction import parse_codebehind, parse_markup, scan_navigation
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.orchestration import ai_interpretation

FIXTURE = Path(__file__).parent / "fixtures" / "v4_2_r7_full_sample"

PICK_ASCX = """<%@ Control Language="vb" CodeBehind="PickCustomer.ascx.vb" Inherits="SampleLegacy.Web.PickCustomer" %>
<table id="tabMain"><tr><td><snt:Label ID="lblTitulo" Tipo="Titulo" runat="server">Buscar Cliente</snt:Label></td></tr>
<tr><td><snt:Label ID="lblCrit" runat="server">Criterio</snt:Label></td><td><snt:DropDownList ID="drpCrit" runat="server"></snt:DropDownList></td></tr>
<tr><td><snt:TextBoxAdv ID="txtHidden" Visible="False" runat="server"></snt:TextBoxAdv></td>
<td><asp:Button ID="btnSearch" runat="server" Text="Buscar" OnClick="btnSearch_Click" /></td></tr>
<tr><td colspan="2"><snt:TablaPaginada ID="grdCust" runat="server" NombreMetodo="txbuscarclientes" NombreCompletoClase="SampleLegacy.BL.CustomerService">
<snt:TablaPaginadaColumna Titulo="Codigo" /><snt:TablaPaginadaColumna Titulo="Nombre" /><snt:TablaPaginadaColumna Visible="False" Titulo="Interno" />
</snt:TablaPaginada></td></tr></table>
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
    End Sub
End Class
"""
PAGE_VB_EXTRA = """
    Protected Sub lnkPick_Prepare()
        Me.lnkPick.Attributes("href") = "javascript:OnClickWindowOpen('default.aspx?url=Web/PickCustomer&selrow=S&ctrvis=" & Me.txtCustomerId.ClientID & "','vPick','600','400');"
        Me.lnkGhost.Attributes("href") = "javascript:OnClickWindowOpen('default.aspx?url=Web/GhostView&selrow=S','vGhost','600','400');"
    End Sub
"""


def quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a, **k)


class BehaviorBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="h4r4_"))
        cls.repo = cls.tmp / "repo"
        shutil.copytree(FIXTURE, cls.repo)
        web = cls.repo / "Web"
        (web / "PickCustomer.ascx").write_text(PICK_ASCX, encoding="utf-8")
        (web / "PickCustomer.ascx.vb").write_text(PICK_VB, encoding="utf-8")
        page_vb = (web / "CustomerPage.aspx.vb").read_text(encoding="utf-8")
        (web / "CustomerPage.aspx.vb").write_text(page_vb.replace("End Class", PAGE_VB_EXTRA + "End Class"), encoding="utf-8")
        proj = web / "Web.vbproj"
        proj.write_text(proj.read_text(encoding="utf-8").replace('<Compile Include="CustomerPage.aspx.vb" />',
                                                                '<Compile Include="CustomerPage.aspx.vb" /><Compile Include="PickCustomer.ascx.vb" />'
                                                                '<Content Include="CustomerPage.aspx" /><Content Include="PickCustomer.ascx" />'), encoding="utf-8")
        cls.baseline = cls.tmp / "baseline"
        assert quiet(run_full_pipeline, cls.repo, cls.baseline, [], 12).status.value == "SUCCESS"
        with patch.object(ai_interpretation, "_resolve_provider", side_effect=AssertionError("provider forbidden")) as guard:
            cls.doc, cls.bc, cls.violations, cls.explained = build(cls.baseline, cls.repo, project="Web", solution="SampleLegacy", pilot_count=3)
            cls.provider_calls = guard.call_count

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def view(self, name: str):
        return next(v for v in self.explained.values() if v.name == name)


class SourceParsingTests(unittest.TestCase):
    def test_markup_controls_grid_columns_and_hidden(self):
        m = parse_markup(PICK_ASCX)
        ids = {c.id: c for c in m.controls}
        self.assertEqual(set(ids), {"lblTitulo", "lblCrit", "drpCrit", "txtHidden", "btnSearch", "grdCust"})
        self.assertEqual(ids["lblTitulo"].label, "Buscar Cliente")
        self.assertFalse(ids["txtHidden"].visible)
        self.assertEqual(ids["grdCust"].columns, ["Codigo", "Nombre"])           # the hidden column is not drawn
        self.assertEqual(ids["grdCust"].bound_to, "SampleLegacy.BL.CustomerService.txbuscarclientes")

    def test_codebehind_receives_messages_and_subs_are_literal(self):
        f = parse_codebehind(PICK_VB, "Web\\PickCustomer.ascx.vb")
        self.assertEqual([r["name"] for r in f.receives], ["ctrvis"])
        self.assertEqual(f.session_keys, ["ID_USER"])
        self.assertEqual([(m["kind"], m["text"], m["event"]) for m in f.messages], [("msgbox", "Sin resultados para el criterio", "btnSearch_Click")])
        self.assertEqual({s["name"]: s["handles"] for s in f.subs}["btnSearch_Click"], ["btnSearch.Click"])

    def test_navigation_literals_carry_file_line_and_parameters(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "A.vb").write_text("x\nOnClickWindowOpen('default.aspx?url=Web/Pick&selrow=S&ctrvis=1')\n", encoding="utf-8")
            hits = scan_navigation(root, ["A.vb", "B.txt"])
        self.assertEqual([(h.file, h.line, h.folder, h.view, h.params, h.mechanism) for h in hits],
                         [("A.vb", 2, "Web", "Pick", ["selrow", "ctrvis"], "window_open")])


class ExplanationTests(BehaviorBase):
    def test_module_level_is_not_invented(self):
        self.assertEqual(self.doc.module.classification, MODULE_NONE)
        self.assertEqual(self.doc.module.claim.status, UNRESOLVED)
        self.assertNotIn("módulo de negocio", self.doc.module.claim.text.lower().replace("no son módulos", ""))
        self.assertTrue(all(f["status"] == INFERRED and "no un módulo" in f["note"] for f in self.doc.module.families))

    def test_views_exist_and_come_from_the_project_content_items(self):
        names = {v.name for v in self.explained.values()}
        self.assertEqual(names, {"CustomerPage", "PickCustomer"})
        for path in self.explained:
            self.assertIn(path.lower().replace("/", "\\"), self.bc.webforms)

    def test_popup_invocation_is_traceable_and_dangling_targets_are_noted(self):
        pick = self.view("PickCustomer")
        self.assertEqual(len(pick.reached_by), 1)
        inv = pick.reached_by[0]
        self.assertEqual((inv.mechanism, inv.parameters, inv.status), ("window_open", ["selrow", "ctrvis"], CONFIRMED))
        self.assertTrue(inv.source_refs and V.ReferenceIndex(self.bc).ref_ok(inv.source_refs[0]))
        self.assertEqual(inv.line, next(i for i, line in enumerate((self.repo / inv.file).read_text(encoding="utf-8").splitlines(), 1) if "url=Web/PickCustomer" in line))
        page = self.view("CustomerPage")
        self.assertEqual({i.target_view.rsplit("\\", 1)[-1] for i in page.reaches}, {"PickCustomer.ascx", "GhostView"})
        ghost = next(i for i in page.reaches if "GhostView" in i.target_view)
        self.assertFalse(ghost.target_exists)
        self.assertIn("INVOCATION_TARGET_MISSING", {v.code for v in self.violations})
        self.assertTrue(pick.metrics["dialog"] and any("diálogo" in c.text.lower() for c in pick.what_it_does))

    def test_behavior_path_is_evidence_backed_and_refs_resolve(self):
        page = self.view("CustomerPage")
        save = next(a for a in page.actions if "Save" in a.action or "btnSave" in a.trigger or a.handler == "btnSave_Click")
        kinds = [s["kind"] for s in save.technical_path.steps]
        self.assertEqual(kinds[0], "view")
        self.assertIn("event", kinds)
        self.assertIn("handler", kinds)
        refs = V.ReferenceIndex(self.bc)
        for a in page.actions:
            for s in a.technical_path.steps:
                self.assertTrue(all(refs.ref_ok(r) for r in s["source_refs"]), s)
        self.assertEqual([v for v in self.violations if v.action == "rejected"], [])          # the deterministic explainer never fabricates

    def test_data_effect_is_inferred_from_the_name_and_reach_is_confirmed(self):
        page = self.view("CustomerPage")
        data = [d for a in page.actions for d in a.data]
        self.assertTrue(data)
        for d in data:
            self.assertEqual(d.status, CONFIRMED)
            self.assertIn(d.effect_status, (INFERRED, UNRESOLVED))
        unknown = [d for d in data if d.effect == "unknown"]
        self.assertTrue(all(d.effect_status == UNRESOLVED for d in unknown))

    def test_unresolved_remains_unresolved_and_business_purpose_is_never_stated(self):
        for v in self.explained.values():
            statuses = {c.status for c in v.what_it_does}
            self.assertIn(UNRESOLVED, statuses)
            self.assertTrue(any("propósito de negocio" in c.text for c in v.what_it_does if c.status == UNRESOLVED))
            self.assertTrue(v.unresolved.unresolved)
        self.assertEqual(self.provider_calls, 0)

    def test_messages_are_literals_only(self):
        pick = self.view("PickCustomer")
        self.assertEqual([(m.kind, m.text, m.event) for m in pick.messages], [("msgbox", "Sin resultados para el criterio", "btnSearch_Click")])
        page = self.view("CustomerPage")
        self.assertEqual(page.messages, [])                                                  # nothing is fabricated when the code has none

    def test_receives_are_literal_reads(self):
        pick = self.view("PickCustomer")
        self.assertTrue(any("«ctrvis»" in c.text and c.status == CONFIRMED for c in pick.receives))


class WireframeTests(BehaviorBase):
    def test_only_evidenced_controls_are_drawn(self):
        pick = self.view("PickCustomer")
        self.assertEqual(pick.ui.status, "DOCUMENTARY_RECONSTRUCTION")
        drawn = {c.id for c in pick.ui.controls}
        self.assertEqual(drawn, {"lblTitulo", "lblCrit", "drpCrit", "txtHidden", "btnSearch", "grdCust"})
        self.assertIn("RECONSTRUCCIÓN DOCUMENTAL — NO ES UNA CAPTURA DE PANTALLA", pick.ui.svg)
        self.assertIn("Buscar Cliente", pick.ui.svg)
        self.assertIn("Nombre", pick.ui.svg)
        self.assertNotIn("Interno", pick.ui.svg)             # hidden grid column is not reconstructed
        self.assertIn("txtHidden", pick.ui.svg)              # listed only as an initially hidden field
        self.assertNotIn("[txtHidden]", pick.ui.svg)
        ET = __import__("xml.etree.ElementTree", fromlist=["x"])
        ET.fromstring(pick.ui.svg)

    def test_unavailable_when_markup_has_no_controls(self):
        ui = wireframe.build("X.ascx", parse_markup("<div>sin controles</div>"), "X.ascx", set())
        self.assertEqual(ui.status, WIREFRAME_UNAVAILABLE)
        self.assertEqual(wireframe.build("Y.ascx", None, "", set()).status, WIREFRAME_UNAVAILABLE)

    def test_wireframe_is_deterministic(self):
        a = wireframe.build("P", parse_markup(PICK_ASCX), "P", set())
        b = wireframe.build("P", parse_markup(PICK_ASCX), "P", set())
        self.assertEqual(a.svg, b.svg)

    def test_validator_rejects_a_control_that_is_not_in_the_markup(self):
        v = copy.deepcopy(self.view("PickCustomer"))
        from legacy_documenter.behavior.model import UIControl
        v.ui.controls.append(UIControl(id="btnInvented", tag="asp:button", kind="button", label="Pagar"))
        out = V.validate_view(V.ReferenceIndex(self.bc), v)
        self.assertIn("WIREFRAME_CONTROL_NOT_IN_EVIDENCE", {x.code for x in out})
        self.assertNotIn("btnInvented", {c.id for c in v.ui.controls})


class ValidationTests(BehaviorBase):
    def setUp(self):
        self.refs = V.ReferenceIndex(self.bc)

    def test_confirmed_claim_requires_support(self):
        c, vs = V.check_claim(Claim("Algo.", CONFIRMED, [], "x"), self.refs, "t")
        self.assertEqual((c.status, vs[0].code), (UNRESOLVED, "CONFIRMED_WITHOUT_SUPPORT"))

    def test_inferred_claim_keeps_status_with_basis_and_is_downgraded_without(self):
        ok, _ = V.check_claim(Claim("Parece X.", INFERRED, [], "regla de nombre"), self.refs, "t")
        self.assertEqual(ok.status, INFERRED)
        bad, vs = V.check_claim(Claim("Parece X.", INFERRED, [], ""), self.refs, "t")
        self.assertEqual((bad.status, vs[0].code), (UNRESOLVED, "INFERRED_WITHOUT_BASIS"))

    def test_unresolved_stays_unresolved(self):
        c, vs = V.check_claim(Claim("No se sabe.", UNRESOLVED, [], ""), self.refs, "t")
        self.assertEqual((c.status, vs), (UNRESOLVED, []))

    def test_fabricated_refs_and_entities_are_rejected(self):
        for claim in (Claim("x", CONFIRMED, ["FLOW-9999999999"], "b"), Claim("x", CONFIRMED, ["src:Web\\CustomerPage.aspx.vb:99999"], "b"),
                      Claim("x", CONFIRMED, ["src:Web\\Nope.vb:1"], "b"),
                      Claim("x", INFERRED, [], "b", entities=[{"type": "view", "name": "Web\\Invented.ascx"}]),
                      Claim("x", INFERRED, [], "b", entities=[{"type": "class", "name": "NoSuchClass"}]),
                      Claim("x", INFERRED, [], "b", entities=[{"type": "procedure", "name": "PKG.NOPE"}])):
            out, vs = V.check_claim(claim, self.refs, "t", "Web\\CustomerPage.aspx")
            self.assertIsNone(out, claim)
            self.assertEqual(vs[0].action, "rejected")

    def test_existing_entities_and_refs_pass(self):
        page = self.view("CustomerPage")
        ep = next(e for e in self.bc.view(page.view).events if e.kind == "web_event")
        claim = Claim("El botón existe.", CONFIRMED, [ep.ep_id], "evento persistido",
                      entities=[{"type": "view", "name": page.view}, {"type": "event", "name": f"{ep.control}.{ep.event}"}, {"type": "method", "name": ep.handler}])
        out, vs = V.check_claim(claim, self.refs, "t", page.view)
        self.assertEqual((out.status, vs), (CONFIRMED, []))

    def test_ai_overlay_is_always_ai_interpretation_and_never_confirmed(self):
        page = copy.deepcopy(self.view("CustomerPage"))
        ep = next(e for e in self.bc.view(page.view).events if e.kind == "web_event")
        vs = V.apply_ai_overlay(self.refs, page, [
            {"text": "Guarda al cliente.", "status": "CONFIRMED", "source_refs": [ep.ep_id], "basis": "lectura del manejador"},
            {"text": "Tiene un campo inventado.", "status": "CONFIRMED", "source_refs": ["FLOW-0000000000"], "basis": "x"},
            {"text": "Cita una clase falsa.", "status": "INFERRED", "source_refs": [], "basis": "x", "entities": [{"type": "class", "name": "Ghost"}]},
            {"text": "Aprobado.", "status": CANONICAL, "source_refs": [ep.ep_id], "basis": "x"},
            {"text": "  ", "status": "INFERRED"},
        ])
        self.assertEqual([c.text for c in page.ai_interpretation], ["Guarda al cliente.", "Aprobado."])
        self.assertTrue(all(c.status == AI_INTERPRETATION and c.origin == "ai" for c in page.ai_interpretation))
        self.assertEqual({v.code for v in vs}, {"AI_CLAIM_DOWNGRADED", "UNRESOLVED_SOURCE_REF", "UNKNOWN_ENTITY", "EMPTY_CLAIM"})
        html = R.html_document(R.compose(self._doc_with(page))[0], "t")
        self.assertIn('data-status="AI_INTERPRETATION"', html)      # the epistemic status stays in the markup; no repeated visible label

    def _doc_with(self, view):
        d = copy.deepcopy(self.doc)
        d.views = [view]
        return d

    def test_canonical_cannot_come_from_the_explainer(self):
        c, vs = V.check_claim(Claim("Canon.", CANONICAL, ["x"], "b"), self.refs, "t")
        self.assertIsNone(c)           # unresolvable ref is rejected first
        c, vs = V.check_claim(Claim("Canon.", CANONICAL, [], "b"), self.refs, "t")
        self.assertEqual((c.status, vs[0].code), (AI_INTERPRETATION, "CANONICAL_NOT_FROM_EVIDENCE"))


class RenderingTests(BehaviorBase):
    def test_same_structured_explanation_renders_identically(self):
        b1, a1 = R.compose(self.doc)
        b2, a2 = R.compose(copy.deepcopy(self.doc))
        self.assertEqual(R.html_document(b1, "t"), R.html_document(b2, "t"))
        self.assertEqual({k: v[0] for k, v in a1.items()}, {k: v[0] for k, v in a2.items()})

    def test_package_has_html_pdf_json_and_deterministic_bytes(self):
        out1, out2 = self.tmp / "p1", self.tmp / "p2"
        i1 = write_package(self.doc, out1, self.violations)
        i2 = write_package(copy.deepcopy(self.doc), out2, self.violations)
        self.assertEqual(i1["files"], i2["files"])
        names = set(i1["files"])
        self.assertTrue({"index.html", "explanations.json", "wireframe_models.json", "validation_report.json", "Entendiendo_Web.pdf"} <= names)
        data = (out1 / "Entendiendo_Web.pdf").read_bytes()
        self.assertTrue(data.startswith(b"%PDF") and data.rstrip().endswith(b"%%EOF"))
        explanation = json.loads((out1 / "explanations.json").read_text(encoding="utf-8"))
        self.assertEqual(explanation["contract"], "LegacyMapperBehavioralExplanation")
        self.assertEqual(explanation["module"]["classification"], MODULE_NONE)
        self.assertEqual(asdict(self.doc), explanation)

    def test_reading_order_is_macro_to_micro_and_catalog_is_an_appendix(self):
        blocks, _ = R.compose(self.doc)
        heads = [b.runs[0].text for b in blocks if getattr(b, "level", 0) == 2]
        self.assertEqual([h.split(".")[0] for h in heads], [str(n) for n in range(1, 11)])
        html = R.html_document(blocks, "t")
        anchors = ["s-solution", "s-project", "s-modules", "s-important-views", "s-view-chapters", "s-cross-view", "s-data", "s-usage", "s-unresolved",
                   "s-appendix", "catalogo"]
        positions = [html.index(f'id="{a}"') for a in anchors]
        self.assertEqual(positions, sorted(positions))                     # the full catalog comes after the narrative, as an appendix

    def test_chapter_has_the_required_parts_in_template_order(self):
        html = R.html_document(R.compose(self.doc)[0], "t")
        needles = ["En una frase", "Qué hace y cómo se usa", "Uso observable", "Reconstrucción visual aproximada", "Flujo técnico simple",
                   "Acciones principales", "Clases relacionadas", "Vistas y ventanas relacionadas"]
        self.assertNotIn("Evidencia técnica", html)                 # evidence machinery is not a chapter of the human document
        self.assertNotIn("Trazabilidad de la vista", html)
        start = html.index("En una frase")
        pos = [html.index(n, start) for n in needles]
        self.assertEqual(pos, sorted(pos))
        self.assertIn("NO ES UNA CAPTURA DE PRODUCCIÓN", html)

    def test_measurements_are_reported_separately(self):
        m = self.doc.measurements
        self.assertEqual(m["vistas_del_proyecto"], 2)
        self.assertEqual(m["con_invocaciones_entrantes"], 1)
        self.assertEqual(m["soportan_wireframe_documental"], 2)


if __name__ == "__main__":
    unittest.main()
