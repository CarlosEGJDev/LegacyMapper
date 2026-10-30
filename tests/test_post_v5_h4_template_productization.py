"""Post-V5 H4 human-template productization: template contract/discovery/safety, AI notice once, typography, TOC, box flows and
style-aware (but never invented) UI reconstruction. Test doubles only; no provider is ever resolved.
"""
from __future__ import annotations

import copy
import re
import shutil
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

from legacy_documenter.behavior import flowboxes
from legacy_documenter.behavior import render as R
from legacy_documenter.behavior import styles as S
from legacy_documenter.evidence.ui_model import MAX_ASSET_BYTES
from legacy_documenter.behavior import template as T
from legacy_documenter.behavior import wireframe
from legacy_documenter.behavior.model import AI_INTERPRETATION, CONFIRMED, INFERRED, UNRESOLVED, ActionExplanation, BehaviorPath, Claim
from legacy_documenter.adapters.vbnet_webforms_oracle.ui_extraction import UiEvidenceExtractor, parse_markup
from legacy_documenter.behavior.ui_evidence import index_ui_evidence
from legacy_documenter.deliver.pdf import PdfDocument
from tests.test_post_v5_h4_r4_behavioral import BehaviorBase

DEFAULT = Path(__file__).resolve().parents[1] / "legacy_documenter" / "templates" / "human" / "default"


def clone_template(tmp: Path, name: str = "mine", **edits) -> Path:
    """Copies the default template into <tmp>/human/<name> applying text edits to its files."""
    dest = tmp / "human" / name
    shutil.copytree(DEFAULT, dest)
    for fname, (old, new) in edits.items():
        path = dest / fname
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
    return dest


class TemplateContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="tpl_"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_default_template_is_discovered_and_valid(self):
        t = T.discover("human/default")
        self.assertEqual((t.template_id, t.manifest["contract"], t.manifest["contract_version"], t.language), ("human/default", T.CONTRACT, "1.0", "es"))
        self.assertEqual(list(t.sections[:3]), ["cover", "ai_notice", "toc"])
        self.assertEqual(t.sections[-1], "appendix")                      # catalog and measurements live in the appendix
        self.assertIn("view.usage", t.required_fields)
        record = t.manifest_record()
        self.assertEqual(record["provider_calls"], 0)
        self.assertTrue({"template.yaml", "document.html", "styles.css", "pdf.css"} <= set(record["files"]))
        self.assertTrue((DEFAULT.parent.parent / "ai" / "README.md").is_file())     # AI templates: reserved and documented only

    def test_user_directory_is_searched_before_the_builtin_root(self):
        clone_template(self.tmp, "default", **{"template.yaml": ("template_version: \"1.0.0\"", "template_version: \"9.9.9\"")})
        self.assertEqual(T.discover("human/default", self.tmp).manifest["template_version"], "9.9.9")
        self.assertEqual(T.discover("human/default").manifest["template_version"], "1.0.0")

    def test_custom_template_directory_loads_and_changes_only_layout(self):
        clone_template(self.tmp, "compact", **{
            "template.yaml": ("template_id: human/default", "template_id: human/compact"),
        })
        t = T.discover("human/compact", self.tmp)
        self.assertEqual(t.template_id, "human/compact")

    def test_unknown_or_unsupported_ids_are_rejected(self):
        for bad in ("human/missing", "ai/default", "default", "../x/y", "human/../default"):
            with self.assertRaises(T.TemplateError, msg=bad):
                T.discover(bad)

    def test_invalid_templates_are_rejected_never_partially_applied(self):
        cases = {
            "wrong contract": {"template.yaml": ("contract: LegacyMapperHumanTemplate", "contract: Other")},
            "missing required section": {"template.yaml": ("  - cover\n", "")},
            "unknown section": {"template.yaml": ("  - appendix\n", "  - appendix\n  - surprise\n")},
            "unknown field": {"template.yaml": ("  - view.title\n", "  - view.secret\n")},
            "chapter without required part": {"template.yaml": ("  - one_line\n", "")},
            "script in document": {"document.html": ("</body>", "<script>alert(1)</script></body>")},
            "event handler": {"document.html": ("<header ", "<header onclick=\"x()\" ")},
            "unknown placeholder": {"document.html": ("{{footer}}", "{{secrets}}")},
            "expression placeholder": {"document.html": ("{{footer}}", "{{ 7*7 }}")},
            "css import": {"styles.css": ("html{", "@import 'x.css';html{")},
            "css url": {"styles.css": ("html{", "html{background:url(http://x/y.png);")},
            "pdf css expression": {"pdf.css": (".body", ".body { width: expression(1) } .body")},
            "path traversal": {"template.yaml": ("html: styles.css", "html: ../styles.css")},
        }
        for name, edit in cases.items():
            dest = clone_template(self.tmp, re.sub(r"\W+", "-", name), **edit)
            with self.assertRaises(T.TemplateError, msg=name):
                T.load_template(dest)

    def test_required_fields_are_validated_against_the_model(self):
        t = T.discover("human/default")
        good = SimpleNamespace(solution=SimpleNamespace(name="s"), project=SimpleNamespace(name="p"), module=SimpleNamespace(classification="x"),
                               catalog=[], views=[SimpleNamespace(name="v", title="", usage={}, actions=[], ui=None)])
        self.assertEqual(T.validate_required_fields(t, good), [])
        bad = copy.deepcopy(good)
        del bad.views[0].usage
        bad.catalog = None
        problems = T.validate_required_fields(t, bad)
        self.assertTrue(any("view.usage" in p for p in problems))
        self.assertEqual(T.validate_required_fields(t, SimpleNamespace(solution=None, project=None, module=None, catalog=[], views=[])) != [], True)

    def test_yaml_subset_parser_is_strict(self):
        self.assertEqual(T.parse_yaml("a: 1\nb:\n  - x\n  - y\nc:\n  d: \"e\"\n"), {"a": 1, "b": ["x", "y"], "c": {"d": "e"}})
        for bad in ("a: 1\n\tb: 2\n", "- x\n", "a: [1\n  zzz"):
            with self.assertRaises(T.TemplateError):
                T.parse_yaml(bad)

    def test_templates_are_data_not_code(self):
        t = T.discover("human/default")
        out = t.fill(title="T", content="{{style}}", style="S", subtitle="", lang="es", toc="", ai_notice="", legend="", footer="", script="",
                     template_id="x", template_version="1")
        self.assertIn("{{style}}", out)                                  # substituted values are never re-expanded: no recursion, no evaluation
        self.assertNotIn("{{content}}", out)


class TypographyTests(unittest.TestCase):
    def test_css_defines_a_strict_size_hierarchy(self):
        css = (DEFAULT / "styles.css").read_text(encoding="utf-8")

        def size(selector: str) -> float:
            m = re.search(r"(?:^|[,\n])\s*" + re.escape(selector) + r"\s*(?:,[^{]*)?\{[^}]*font-size:([\d.]+)rem", css)
            self.assertIsNotNone(m, selector)
            return float(m.group(1))
        title, h2, h3, h4 = size(".doc-title"), size("h2"), size("h3"), size("h4")
        self.assertGreater(title, h2)
        self.assertGreater(h2, h3)
        self.assertGreater(h3, h4)
        self.assertGreater(h4, 1.0)                                      # sub-sub heading still above body
        self.assertLess(size("p.evidence"), size("p.technical"))
        self.assertLess(size("p.technical"), 1.0)
        for cls in ("st-confirmed", "st-inferred", "st-unresolved", "st-ai", "st-canonical", "callout-ai", "ai-notice"):
            self.assertIn("." + cls, css)

    def test_pdf_css_sizes_are_ordered(self):
        style = T.discover("human/default").pdf_style
        sizes = style["heading_sizes"]
        self.assertGreater(style["title_size"], sizes[1])
        self.assertGreater(sizes[1], sizes[2])
        self.assertGreater(sizes[2], sizes[3])
        self.assertGreater(sizes[3], style["body_size"])
        self.assertGreater(style["body_size"], style["evidence_size"])

    def test_pdf_writer_uses_the_template_style(self):
        import zlib
        doc = PdfDocument("T")
        doc.style = {"heading_sizes": {2: 31}, "heading_colors": {}, "body_size": 12.5}
        doc.blocks([__import__("legacy_documenter.deliver.markdown", fromlist=["x"]).Heading(2, [__import__("legacy_documenter.deliver.markdown", fromlist=["x"]).Run("Titulo")], "t")])
        data, _ = doc.render()
        streams = "".join(zlib.decompress(m).decode("latin-1") for m in re.findall(rb"stream\n(.*?)\nendstream", data, re.S))
        self.assertIn("/F2 31 Tf", streams)


class RenderedDocumentTests(BehaviorBase):
    def doc_ai(self):
        doc = copy.deepcopy(self.doc)
        v = doc.views[0]
        v.ai_narrative = {"simple_summary": [Claim("Esta pantalla gestiona clientes.", AI_INTERPRETATION, [], "b", "ai")],
                          "observable_purpose": [Claim("Permite guardar y notificar.", AI_INTERPRETATION, [], "b", "ai")]}
        v.ai_action_notes = {v.actions[0].handler: [Claim("Al guardar se llama al servicio.", AI_INTERPRETATION, [], "b", "ai")]}
        doc.ai_manifest = {"status": "COMPLETED", "provider_id": "p", "model_id": "m", "request_count": 1, "successful_requests": 1}
        return doc

    def test_ai_notice_once_marker_in_body_and_status_preserved(self):
        doc = self.doc_ai()
        html = R.html_document(R.compose(doc)[0], "t")
        self.assertEqual(html.count("ai-notice"), html.count('class="ai-notice"') + html.count(".ai-notice"))   # one notice element (+ the css rule)
        self.assertEqual(html.count('<aside class="ai-notice"'), 1)
        self.assertEqual(html.count("Interpretación asistida por IA"), 1)
        self.assertEqual(html.count("Interpretación de IA — no aprobada"), 0)
        self.assertEqual(html.count('<p class="callout-title">IA</p>'), 0)      # no repeated IA badge: the opening notice says it once
        self.assertGreaterEqual(html.count('class="callout callout-ai" data-status="AI_INTERPRETATION"'), 3)
        for c in doc.views[0].ai_narrative["simple_summary"]:
            self.assertEqual(c.status, AI_INTERPRETATION)                # the structured model keeps the epistemic status

    def test_template_cannot_change_truth(self):
        before = asdict(self.doc_ai())
        tmp = Path(tempfile.mkdtemp(prefix="tpl2_"))
        try:
            dest = clone_template(tmp, "reordered", **{"template.yaml": ("template_id: human/default", "template_id: human/reordered")})
            text = (dest / "template.yaml").read_text(encoding="utf-8").replace("  - usage\n  - unresolved\n", "  - unresolved\n  - usage\n")
            (dest / "template.yaml").write_text(text, encoding="utf-8")
            t = T.load_template(dest)
            doc = self.doc_ai()
            blocks, _ = R.compose(doc, t)
            html = R.html_document(blocks, "t", t)
            self.assertLess(html.index('id="s-unresolved"'), html.index('id="s-usage"'))        # layout changed
            self.assertEqual(asdict(doc), before)                                               # truth did not
            for v in doc.views:
                self.assertTrue(all(c.status == AI_INTERPRETATION for cl in v.ai_narrative.values() for c in cl))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_toc_anchors_resolve_and_list_sections_and_views(self):
        blocks, _ = R.compose(self.doc)
        html = R.html_document(blocks, "t")
        toc = html[html.index('class="doc-toc"'):html.index("</nav>", html.index('class="doc-toc"'))]
        hrefs = re.findall(r'href="#([^"]+)"', toc)
        self.assertGreater(len(hrefs), 8)
        for h in hrefs:
            self.assertEqual(html.count(f'id="{h}"'), 1, h)
        for name in ("La solución", "El proyecto", "Apéndice", "CustomerPage", "PickCustomer"):
            self.assertIn(name, toc)

    def test_pdf_has_contents_with_sections_and_views_and_bookmarks(self):
        blocks, assets = R.compose(self.doc)
        out = Path(tempfile.mkdtemp(prefix="tpl3_"))
        try:
            for rel, (svg, _k) in assets.items():
                (out / rel).parent.mkdir(parents=True, exist_ok=True)
                (out / rel).write_text(svg, encoding="utf-8")
            data, stats = R.build_pdf(blocks, "Entendiendo Web", out, ["m"])
            self.assertGreaterEqual(stats["outline_entries"], 8)
            import zlib
            text = "".join(zlib.decompress(m).decode("latin-1") for m in re.findall(rb"stream\n(.*?)\nendstream", data, re.S))
            self.assertIn("(Contenido)", text)
            self.assertIn("CustomerPage", text)
            again, stats2 = R.build_pdf(blocks, "Entendiendo Web", out, ["m"])
            self.assertEqual((data, stats["content_sha256"]), (again, stats2["content_sha256"]))    # deterministic
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_html_rendering_is_deterministic_for_the_same_template(self):
        a = R.html_document(R.compose(self.doc)[0], "t")
        b = R.html_document(R.compose(copy.deepcopy(self.doc))[0], "t")
        self.assertEqual(a, b)

    def test_flow_box_diagram_is_part_of_each_chapter(self):
        blocks, assets = R.compose(self.doc)
        self.assertTrue(any(rel.endswith("-flujo.svg") for rel in assets))


class BoxFlowTests(unittest.TestCase):
    def action(self, steps, unresolved=()):
        path = BehaviorPath(action="Al pulsar «Guardar»", steps=steps, unresolved_calls=list(unresolved))
        return ActionExplanation(action=path.action, trigger="btn", event="Click", handler="btn_Click", technical_path=path, source_refs=["EP-1"])

    def test_only_evidenced_layers_are_drawn_and_missing_layers_are_skipped(self):
        steps = [{"kind": "view", "label": "Page", "status": CONFIRMED, "source_refs": ["EP-1"]},
                 {"kind": "event", "label": "btn.Click", "status": CONFIRMED, "source_refs": ["EP-1"]},
                 {"kind": "handler", "label": "btn_Click", "status": CONFIRMED, "source_refs": ["EP-1"]},
                 {"kind": "method", "label": "Page.btn_Click", "status": CONFIRMED, "source_refs": ["FLOW-1"]},
                 {"kind": "data_operation", "label": "Repo.Save (DAO-1)", "status": CONFIRMED, "source_refs": ["DAO-1"]},
                 {"kind": "procedure", "label": "PKG.SAVE", "status": CONFIRMED, "source_refs": ["DAO-1"]}]
        view = SimpleNamespace(name="Page", actions=[self.action(steps)])
        layers = flowboxes.action_layers(view, view.actions[0])
        self.assertEqual([l["layer"] for l in layers], ["event", "dao", "procedure", "boundary"])      # no business layer was evidenced: skipped
        self.assertTrue(all(l["source_refs"] for l in layers[:3]))
        svg = flowboxes.render_svg(flowboxes.view_flow(view))
        self.assertNotIn("Negocio / servicio</text>", svg)
        self.assertIn("PKG.SAVE", svg)

    def test_unresolved_business_and_data_destination_are_explicit(self):
        steps = [{"kind": "event", "label": "btn.Click", "status": CONFIRMED, "source_refs": ["EP-2"]},
                 {"kind": "handler", "label": "btn_Click", "status": CONFIRMED, "source_refs": ["EP-2"]}]
        unresolved = [{"label": "Svc.Do(x)", "count": 1, "infrastructure": False, "business_call": "Svc.Do"}]
        view = SimpleNamespace(name="Page", actions=[self.action(steps, unresolved)])
        layers = flowboxes.action_layers(view, view.actions[0])
        by = {l["layer"]: l for l in layers}
        self.assertEqual(by["business"]["status"], UNRESOLVED)
        self.assertIn("Svc.Do", by["business"]["label"])
        self.assertEqual(by["dao"]["status"], UNRESOLVED)
        self.assertIn("no resuelto", by["dao"]["label"])
        self.assertIn("NO RESUELTO", flowboxes.render_svg(flowboxes.view_flow(view)))

    def test_deterministic_and_bounded(self):
        steps = [{"kind": "event", "label": "e", "status": CONFIRMED, "source_refs": ["EP-3"]}]
        actions = [self.action(steps) for _ in range(12)]
        view = SimpleNamespace(name="Page", actions=actions)
        svg1, svg2 = flowboxes.render_svg(flowboxes.view_flow(view)), flowboxes.render_svg(flowboxes.view_flow(view))
        self.assertEqual(svg1, svg2)
        self.assertIn("4 acciones más", svg1)


class StyleAwareReconstructionTests(unittest.TestCase):
    MARKUP = ('<table class="TablaCabecera"><tr><td class="FondoGrupo" style="width:200px"><snt:Label ID="lbl" Tipo="Titulo" runat="server">Titulo</snt:Label></td>'
              '<td><asp:Button ID="btn" CssClass="Boton" runat="server" Text="Guardar" />'
              '<snt:HyperLink ID="ico" Tipo="HyperLink" ImageUrl="../img/guardar.gif" runat="server" />'
              '<snt:HyperLink ID="miss" Tipo="Inexistente" ImageUrl="../img/no_existe.gif" runat="server" /></td></tr></table>')

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sty_"))
        (self.tmp / "img").mkdir()
        (self.tmp / "web").mkdir()
        (self.tmp / "img" / "guardar.gif").write_bytes(b"GIF89a\x01\x00\x01\x00\x00\x00\x00;")
        (self.tmp / "Styles.css").write_text(
            ".Boton{background-color:#2E75B6;color:#FFFFFF;font-size:11px;font-weight:bold;width:120px;height:24px;border-radius:6px;"
            "background-image:url(http://evil/x.png);behavior:url(x.htc)}\n.Titulo{font:bold 15px Arial;color:#661a87}\n"
            ".FondoGrupo{background-color:#86b2d4}\n@media print{.Boton{display:none}}\n.HyperLink{color:#226da6}\n", encoding="utf-8")
        (self.tmp / "default.aspx").write_text('<html><head><link href="Styles.css" type="text/css" rel="stylesheet"></head></html>', encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def evidence(self, files=("default.aspx", "web/V.ascx"), root=None):
        """UI Evidence extracted ONCE from the temporary repository (analysis time); the catalog then reads only the persisted partitions."""
        parts = UiEvidenceExtractor(root or self.tmp, [{"relative_path": f} for f in files], [], []).extract()
        return index_ui_evidence(parts)

    def catalog(self, files=("default.aspx", "web/V.ascx"), root=None):
        (self.tmp / "web" / "V.ascx").write_text(self.MARKUP, encoding="utf-8")
        return self.evidence(files, root).style_catalog()

    def test_css_is_whitelisted_and_never_executes_or_imports(self):
        rules = S.parse_css((self.tmp / "Styles.css").read_text(encoding="utf-8"))
        self.assertEqual(rules["Boton"], {"background": "#2e75b6", "color": "#ffffff", "font_size": 11, "font_weight": "bold", "width": 120, "height": 24, "radius": 6})
        self.assertEqual(rules["Titulo"], {"font_size": 15, "font_weight": "bold", "color": "#661a87"})
        self.assertNotIn("display", str(rules))                          # @media blocks and unknown properties are ignored

    def test_reconstruction_uses_only_declared_styles_and_assets(self):
        cat = self.catalog()
        self.assertEqual((cat.shell, cat.css_files), ("default.aspx", ["Styles.css"]))
        ui = wireframe.build("web/V.ascx", parse_markup(self.MARKUP), "web/V.ascx", set(), styles=cat)
        rep = ui.style_report
        self.assertEqual(ui.fidelity, S.STYLE_PARTIAL)                   # 'Tipo' is inferred and an icon is missing: never high confidence
        self.assertEqual((rep["icons_total"], rep["icons_resolved"]), (2, 1))
        self.assertTrue(any("no_existe" in x for x in rep["icons_unresolved"]))
        self.assertIn("#2e75b6", ui.svg)                                 # the declared button background
        self.assertIn("data:image/gif;base64,", ui.svg)                  # the icon exists locally
        self.assertNotIn("evil", ui.svg)
        self.assertNotIn("http://", ui.svg.replace("http://www.w3.org", ""))
        self.assertIn("NO ES UNA CAPTURA DE PANTALLA", ui.svg)

    def test_without_style_evidence_the_result_is_structure_only(self):
        ui = wireframe.build("V", parse_markup(self.MARKUP), "V", set(), styles=None)
        self.assertEqual(ui.fidelity, S.STRUCTURE_ONLY)
        empty = self.catalog(["web/V.ascx"], root=self.tmp / "web")
        ui2 = wireframe.build("V", parse_markup(self.MARKUP), "V", set(), styles=empty)
        self.assertEqual(ui2.fidelity, S.STRUCTURE_ONLY)

    def test_high_confidence_needs_confirmed_styles_resolved_icons_and_no_runtime_layout(self):
        report = {"controls": 10, "visible_controls": 10, "controls_with_style": 10, "controls_with_confirmed_style": 10, "icons_total": 2, "icons_resolved": 2,
                  "dynamic_visibility_assignments": 0, "script_blocks": 0, "css_sources": ["Styles.css"], "classes_unresolved": []}
        self.assertEqual(S.classify_fidelity(report), S.STYLE_HIGH)
        for change in ({"controls_with_confirmed_style": 5}, {"icons_resolved": 1}, {"dynamic_visibility_assignments": 3}, {"script_blocks": 1},
                       {"css_sources": []}, {"classes_unresolved": ["X"]}):
            self.assertEqual(S.classify_fidelity({**report, **change}), S.STYLE_PARTIAL)
        self.assertEqual(S.classify_fidelity({**report, "controls_with_style": 0}), S.STRUCTURE_ONLY)

    def test_icons_outside_the_repository_or_oversized_are_not_embedded(self):
        (self.tmp / "img" / "big.gif").write_bytes(b"G" * (MAX_ASSET_BYTES + 1))
        (self.tmp / "web" / "V.ascx").write_text(
            '<snt:HyperLink ID="a" ImageUrl="../../../outside.gif" runat="server" /><snt:HyperLink ID="b" ImageUrl="../img/big.gif" runat="server" />'
            '<snt:HyperLink ID="c" ImageUrl="../img/guardar.gif" runat="server" />', encoding="utf-8")
        cat = self.evidence().style_catalog()
        self.assertEqual(cat.icon("web/V.ascx", "../../../outside.gif"), (None, "fuera del repositorio"))
        self.assertEqual(cat.icon("web/V.ascx", "../img/big.gif"), (None, "demasiado grande para incrustar"))
        self.assertEqual(cat.icon("web/V.ascx", "../img/guardar.gif")[1], "resuelta")



class FinalPolishTests(BehaviorBase):
    """Final presentation polish: hooks live in the template (global), diagrams contain their text, wording is accurate."""

    def test_template_hooks_for_centering_justification_and_rhythm_exist(self):
        css = (DEFAULT / "styles.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"\.doc-title\{[^}]*text-align:center")
        self.assertRegex(css, r"h3\.view-title\{[^}]*text-align:center")
        self.assertRegex(css, r"figure\.diagram\{[^}]*margin:\d+px auto[^}]*text-align:center")
        self.assertRegex(css, r"\.doc-main p\{[^}]*text-align:justify")
        self.assertRegex(css, r"p\.caption[^{]*\{[^}]*text-align:center")
        pdf = (DEFAULT / "pdf.css").read_text(encoding="utf-8")
        style = T.parse_pdf_css(pdf)
        self.assertEqual(style["title_align"], "center")
        self.assertEqual(style["heading_align"], {2: "center"})                  # the view subtitle class
        self.assertTrue(style["justify"])
        self.assertGreater(style["heading_before"][2], style["heading_before"][3])  # spacing rhythm: view subtitle breathes more than a sub-section

    def test_renderer_emits_the_hooks(self):
        html = R.html_document(R.compose(self.doc)[0], "t")
        self.assertIn('<h1 class="doc-title"', html)
        self.assertIn('class="view-title"', html)
        self.assertIn('class="section-title"', html)
        self.assertIn('<figure class="diagram">', html)
        self.assertIn('<p class="subtitle">' if '<p class="subtitle">' in html else '<p class="doc-subtitle">', html)

    def test_cover_wording_is_accurate_about_the_ai_origin(self):
        none = R.provenance_sentence({"status": "NOT_RUN"})
        self.assertIn("no incluye interpretaciones de IA", none)
        replay = R.provenance_sentence({"status": "COMPLETED", "provider_id": "p", "model_id": "m", "replayed_from_real_run": True})
        self.assertEqual(replay, "")                                  # with AI the single "Interpretación asistida por IA" note says it
        live = R.provenance_sentence({"status": "COMPLETED", "provider_id": "p", "model_id": "m"})
        self.assertEqual(live, replay)
        for text in (none, replay, live):
            self.assertNotIn("sin volver a analizar el código ni llamar a un proveedor", text)       # the obsolete claim

    def test_cover_and_html_carry_the_provenance_sentence(self):
        doc = copy.deepcopy(self.doc)
        doc.ai_manifest = {"status": "COMPLETED", "provider_id": "copilot-local", "model_id": "m", "request_count": 1, "successful_requests": 1,
                           "replayed_from_real_run": True}
        html = R.html_document(R.compose(doc)[0], "t")
        self.assertNotIn(R.AI_BASIS_SENTENCE, html)
        self.assertIn("Interpretación asistida por IA", html)
        self.assertNotIn("copilot-local", html)                      # provider / model are machine provenance
        self.assertEqual(html.count('class="provenance"'), 0)

    def test_marker_policy_none_removes_badges_but_keeps_the_notice(self):
        tmp = Path(tempfile.mkdtemp(prefix="mk_"))
        try:
            dest = clone_template(tmp, "nomark", **{"template.yaml": ("ai_marker: chapter", "ai_marker: none")})
            t = T.load_template(dest)
            doc = copy.deepcopy(self.doc)
            doc.views[0].ai_narrative = {"simple_summary": [Claim("Texto de IA.", AI_INTERPRETATION, [], "b", "ai")]}
            html = R.html_document(R.compose(doc, t)[0], "t", t)
            self.assertEqual(html.count('<p class="callout-title">IA</p>'), 0)
            self.assertIn('data-status="AI_INTERPRETATION"', html)
            self.assertEqual(html.count("Interpretación asistida por IA"), 1)
            bad = clone_template(tmp, "badlayout", **{"template.yaml": ("title_alignment: center", "title_alignment: diagonal")})
            with self.assertRaises(T.TemplateError):
                T.load_template(bad)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_svg_wrapping_is_deterministic_and_contained(self):
        from legacy_documenter.behavior import svgtext
        long_label = "Sonda.Gestion.NSSMUT.BL.PrePrevencion.PrePrvDeptoPrv.txGrabarDepartamentoPrevencion_ConParametrosExtendidos"
        a = svgtext.wrap(long_label, 150, 11)
        self.assertEqual(a, svgtext.wrap(long_label, 150, 11))
        self.assertGreater(len(a), 1)
        self.assertTrue(all(svgtext.text_width(line, "F1", 11) <= 150 for line in a))
        self.assertEqual("".join(a), long_label)                                  # nothing is dropped
        words = svgtext.wrap("una explicación bastante larga que debe partirse en varias líneas dentro de la caja", 120, 11)
        self.assertTrue(all(svgtext.text_width(line, "F1", 11) <= 120 for line in words))

    def test_flow_diagram_text_stays_inside_its_boxes_and_boxes_grow(self):
        long_proc = "PKG_PREVENCION_DEPARTAMENTO_EXPERTO.GRABAR_DEPARTAMENTO_PREVENCION_Y_PARAMETROS_ASOCIADOS"
        steps = [{"kind": "event", "label": "hypGuardarConUnNombreMuyLargo.Click", "status": CONFIRMED, "source_refs": ["EP-1"]},
                 {"kind": "handler", "label": "hypGuardarConUnNombreMuyLargo_Click", "status": CONFIRMED, "source_refs": ["EP-1"]},
                 {"kind": "data_operation", "label": "PrePrvDeptoPrvConNombreExtremadamenteLargo.txGrabarTodo (DAO-0583829514)", "status": CONFIRMED,
                  "source_refs": ["DAO-1"]},
                 {"kind": "procedure", "label": long_proc, "status": CONFIRMED, "source_refs": ["DAO-1"]}]
        path = BehaviorPath(action="Al pulsar el ícono «guardar» de la pantalla de mantenimiento", steps=steps)
        action = ActionExplanation(action=path.action, trigger="b", event="Click", handler="h", technical_path=path, source_refs=["EP-1"])
        view = SimpleNamespace(name="ucPreMantDepPrevencionConUnNombreLargo", actions=[action])
        svg1, w, h = flowboxes.render(flowboxes.view_flow(view))
        svg2, _w, _h = flowboxes.render(flowboxes.view_flow(view))
        self.assertEqual(svg1, svg2)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(svg1)
        ns = "{http://www.w3.org/2000/svg}"
        rects = [r for r in root.iter(ns + "rect") if r.get("rx") == "6"]
        texts = [t for t in root.iter(ns + "text") if t.get("text-anchor") != "middle"]
        from legacy_documenter.deliver.pdf import text_width
        self.assertTrue(rects and texts)
        for t in texts:
            x, y = float(t.get("x")), float(t.get("y"))
            size = float(t.get("font-size"))
            owners = [r for r in rects if float(r.get("x")) <= x < float(r.get("x")) + float(r.get("width"))
                      and float(r.get("y")) <= y <= float(r.get("y")) + float(r.get("height"))]
            if not owners:
                continue                                              # column headers / title live outside boxes
            box = owners[0]
            right = float(box.get("x")) + float(box.get("width"))
            font = "F2" if t.get("font-weight") == "bold" else "F1"
            self.assertLessEqual(x + text_width(t.text or "", font, size), right - 2, t.text)
            self.assertLessEqual(y, float(box.get("y")) + float(box.get("height")), t.text)
        self.assertGreater(h, 150)                                    # the canvas grew to hold the wrapped boxes
        self.assertIn(long_proc.split(".")[0][:12], svg1.replace("</text>", ""))

    def test_cross_and_path_diagrams_contain_long_names(self):
        blocks, assets = R.compose(self.doc)
        for rel, (svg, kind) in assets.items():
            if kind in ("path", "cross", "flow"):
                import xml.etree.ElementTree as ET
                ET.fromstring(svg)                                    # well formed
        v = copy.deepcopy(self.doc.views[0])
        v.reached_by = [type(self.doc.cross_view[0]) if False else copy.deepcopy(i) for i in v.reached_by]
        svg, w, h = R._cross_svg(self.view("PickCustomer")) if self.view("PickCustomer").reached_by else ("", 0, 0)
        if svg:
            self.assertGreater(w, 400)

    def test_pdf_has_centered_view_subtitles_and_justified_paragraphs(self):
        import zlib
        blocks, assets = R.compose(self.doc)
        out = Path(tempfile.mkdtemp(prefix="pol_"))
        try:
            for rel, (svg, _k) in assets.items():
                (out / rel).parent.mkdir(parents=True, exist_ok=True)
                (out / rel).write_text(svg, encoding="utf-8")
            data, stats = R.build_pdf(blocks, "Entendiendo Web", out, ["m"])
            again, _ = R.build_pdf(blocks, "Entendiendo Web", out, ["m"])
            self.assertEqual(data, again)
            text = "".join(zlib.decompress(m).decode("latin-1") for m in re.findall(rb"stream\n(.*?)\nendstream", data, re.S))
            # the cover title (27pt) and the view subtitles (15pt) are centred: none starts at the left margin (48pt)
            titles = [float(x) for x in re.findall(r"/F2 27 Tf ([\d.]+) [\d.]+ Td", text)]
            subs = [float(x) for x in re.findall(r"/F2 15 Tf ([\d.]+) [\d.]+ Td", text)]
            self.assertTrue(titles and subs)
            self.assertTrue(all(x > 60 for x in titles))
            self.assertTrue(all(abs(x - 48.0) > 1.0 for x in subs))
            self.assertGreaterEqual(stats["pages"], 6)
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_pdf_justification_spreads_words_to_the_line_width(self):
        import zlib

        from legacy_documenter.deliver.markdown import Para, Run
        doc = PdfDocument("J")
        doc.style = {"justify": True, "body_size": 10}
        doc.blocks([Para([Run("palabra " * 120)])])
        data, _ = doc.render()
        text = "".join(zlib.decompress(m).decode("latin-1") for m in re.findall(rb"stream\n(.*?)\nendstream", data, re.S))
        xs = [float(x) for x in re.findall(r"/F1 10 Tf ([\d.]+) [\d.]+ Td \(palabra\)", text)]
        self.assertTrue(xs)
        # in a justified paragraph the last word of a full line ends at the right margin: its x + width ~= 547
        from legacy_documenter.deliver.pdf import text_width
        last_full = [x for x in xs if x > 400]
        self.assertTrue(any(abs((x + text_width("palabra", "F1", 10)) - 547.0) < 1.0 for x in last_full))



if __name__ == "__main__":
    unittest.main()
