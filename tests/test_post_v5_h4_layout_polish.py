"""H4 final layout / overflow polish: structural layout invariants (no pixel tests, no provider, no scanner)."""
from __future__ import annotations

import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from legacy_documenter.behavior import flowboxes, svgtext
from legacy_documenter.behavior import render as R
from legacy_documenter.deliver import html as H
from legacy_documenter.deliver.markdown import Para, Run, Table
from legacy_documenter.deliver.pdf import PdfDocument, _identifier_parts, _safe_cuts, text_width

TEXT_OP = re.compile(r"BT [\d. ]+ rg /(F\d) ([\d.]+) Tf ([-\d.]+) ([-\d.]+) Td \((.*)\) Tj ET")
RECT_OP = re.compile(r"([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) re")


def unescape(s: str) -> str:
    return s.replace("\\\\", "\x00").replace("\\(", "(").replace("\\)", ")").replace("\x00", "\\")


def page_overflows(pdf: PdfDocument, margin: float = 36.0) -> list[tuple]:
    """Every drawn text / rectangle whose horizontal extent leaves the usable page width (renderer measurements)."""
    bad = []
    for number, page in enumerate(pdf.pages, 1):
        for op in page.ops:
            m = TEXT_OP.match(op)
            if m:
                font, size, x, text = m.group(1), float(m.group(2)), float(m.group(3)), unescape(m.group(5))
                right = x + text_width(text, font, size)
                if x < margin - 0.5 or right > page.width - margin + 0.5:
                    bad.append((number, "text", round(x), round(right), text[:40]))
                continue
            for r in RECT_OP.finditer(op):
                x, _y, w, _h = (float(v) for v in r.groups())
                if w >= page.width - 1:
                    continue
                if x < margin - 0.5 or x + w > page.width - margin + 0.5:
                    bad.append((number, "rect", round(x), round(x + w), ""))
    return bad


def long_flow(rows: int = 8) -> dict:
    layers = lambda i: [
        {"layer": "event", "label": f"radGrafico{i}.CheckedChanged -> radGrafico{i}_CheckedChanged", "status": "CONFIRMED", "source_refs": []},
        {"layer": "business", "label": "Lógica de negocio no seguida: PrePrevencion.txcargacomboactecoxprofesional (+1)", "status": "UNRESOLVED", "source_refs": []},
        {"layer": "dao", "label": "Destino de datos no resuelto", "status": "UNRESOLVED", "source_refs": []}]
    return {"view": "ucPreEstadisticasAccidentes", "rows": [{"action": f"Al pulsar «Gráfico {i}»", "handler": "h", "layers": layers(i)} for i in range(rows)]}


class IdentifierWrappingTests(unittest.TestCase):
    def test_camel_case_identifiers_wrap_at_word_boundaries(self):
        parts = _identifier_parts("ucPreCargaArchivoAsignacion")
        self.assertEqual("".join(parts), "ucPreCargaArchivoAsignacion")
        self.assertEqual(parts, ["uc", "Pre", "Carga", "Archivo", "Asignacion"])
        self.assertEqual(_identifier_parts("short"), ["short"])

    def test_pdf_table_never_splits_an_identifier_by_characters(self):
        pdf = PdfDocument("t")
        pdf.new_page()
        names = ["ucPreCargaArchivoAsignacion", "ucPreCatastroDiagRiesgoErgonomico", "ucPreCertificadosAccidentabilidad2"]
        pdf.table(Table([[Run("Vista")], [Run("Título visible")], [Run("Qué parece hacer")], [Run("Uso observable")]],
                        [[[Run(n, code=True)], [Run("Carga de Archivo Asignación")], [Run("Con acciones que llaman a lógica")], [Run("Uso no resuelto")]] for n in names]))
        words = set()
        for page in pdf.pages:
            for op in page.ops:
                m = TEXT_OP.match(op)
                if m and m.group(1) == "F4":
                    words.add(unescape(m.group(5)))
        for name in names:                            # every camelCase piece of each name is drawn whole
            for piece in _identifier_parts(name):
                self.assertTrue(any(piece in w for w in words), piece)
        self.assertEqual(page_overflows(pdf), [])

    def test_html_identifiers_get_soft_break_opportunities(self):
        out = H.soft_breaks("PPRE_GES_JERARQUIA.TRAER_SUPERVISORES y ucPreMantEmpadronamiento <x>")
        self.assertIn("<wbr>", out)
        self.assertEqual(re.sub(r"<wbr>", "", out).replace("&lt;", "<").replace("&gt;", ">"), "PPRE_GES_JERARQUIA.TRAER_SUPERVISORES y ucPreMantEmpadronamiento <x>")
        self.assertNotIn("<wbr>", H.soft_breaks("palabra corta"))

    def test_svg_text_wraps_at_camel_case(self):
        lines = svgtext.wrap("ucPreEstadisticasAccidentes", 110, 12, bold=True)
        self.assertEqual("".join(lines), "ucPreEstadisticasAccidentes")
        self.assertGreater(len(lines), 1)
        self.assertTrue(all(l[0].isupper() or l.startswith("uc") for l in lines))


class HtmlContainmentTests(unittest.TestCase):
    def test_stylesheet_contains_wide_content(self):
        css = H.CSS
        for rule in ("th,td{", "code{"):                           # tables and identifiers: no character-by-character wrapping
            self.assertNotIn("anywhere", css[css.index(rule):css.index("}", css.index(rule))])
        self.assertIn(".table-wrap{overflow-x:auto;max-width:100%", css)   # wide tables scroll locally, never the page
        self.assertRegex(css, r"pre\{white-space:pre-wrap")
        self.assertIn("figure.diagram img{max-width:100%;height:auto", css)
        self.assertIn("minmax(min(240px,100%),1fr)", css)
        self.assertRegex(css, r"\.st\{[^}]*white-space:normal")

    def test_rendered_table_and_code_carry_breaks(self):
        html = H.render_blocks([Table([[Run("Ruta")]], [[[Run("a.b.ucPreMantEmpadronamientoControlLargo.metodo", code=True)]]])], "x/index.html")
        self.assertIn("table-wrap", html)
        self.assertIn("<wbr>", html)


class FlowDiagramTests(unittest.TestCase):
    def test_boxes_contain_their_text_and_the_canvas_contains_the_boxes(self):
        svg, w, h = flowboxes.render(long_flow())
        root = ET.fromstring(svg)
        rects, texts = [], []
        for el in root.iter():
            tag = el.tag.split("}")[-1]
            if tag == "rect":
                x, y, rw, rh = (float(el.get(k)) for k in ("x", "y", "width", "height"))
                if rw < w:
                    rects.append((x, y, rw, rh))
                    self.assertTrue(0 <= x and x + rw <= w and 0 <= y and y + rh <= h)
            elif tag == "text" and (el.text or "").strip():
                texts.append((float(el.get("x")), float(el.get("y")), float(el.get("font-size", "12")), el.text, el.get("text-anchor"), el.get("font-weight")))
        for x, y, size, text, anchor, weight in texts:
            width = text_width(text, "F2" if weight == "bold" else "F1", size)
            left = x - width / 2 if anchor == "middle" else x
            self.assertTrue(left >= 0 and left + width <= w + 0.5, text)
            box = [r for r in rects if r[0] - 1 <= left <= r[0] + r[2] and r[1] <= y <= r[1] + r[3] + 1]
            if box:
                r = min(box, key=lambda b: b[2] * b[3])
                self.assertLessEqual(left + width, r[0] + r[2] + 0.5, text)

    def test_long_unbreakable_identifier_widens_the_box_instead_of_splitting(self):
        flow = long_flow(2)
        flow["rows"][0]["layers"][1]["label"] = "txcargacomboactecoxprofesionalmuylargo"
        _svg, w, _h = flowboxes.render(flow)
        narrow, nw, _ = flowboxes.render(long_flow(2))
        self.assertGreater(w, nw - 1)
        self.assertLessEqual(flowboxes._box_width(flow["rows"], flow["view"]), flowboxes.MAX_BW)

    def test_origin_node_and_its_connectors_are_tagged(self):
        svg, _w, _h = flowboxes.render(long_flow(3))
        self.assertEqual(svg.count('data-role="view"'), 1)
        self.assertEqual(svg.count('data-from="view"'), 3)


class PdfFigureTests(unittest.TestCase):
    def build(self, flow: dict, kind="box-flow"):
        svg, w, h = flowboxes.render(flow)
        d = Path(tempfile.mkdtemp(prefix="fig_"))
        self.addCleanup(lambda: shutil.rmtree(d, True))
        (d / "assets").mkdir()
        (d / "assets" / "f.svg").write_text(svg, encoding="utf-8")
        pdf = PdfDocument("t")
        pdf.assets_root = d
        pdf.reserve_front()
        pdf.blocks([R._fig("Flujo simple de V", "assets/f.svg", w, h, kind, len(flow["rows"]))])
        pdf.fill_front("sub", [])
        return pdf, w, h

    def test_every_figure_page_fits_the_printable_width(self):
        for rows in (3, 8):
            pdf, _w, _h = self.build(long_flow(rows))
            self.assertGreaterEqual(pdf.stats["figure_pages"], 1)
            self.assertEqual(page_overflows(pdf), [])

    def test_a_sliced_flow_repeats_its_origin_node_on_every_part(self):
        flow = long_flow(8)
        for row in flow["rows"]:
            row["layers"][0]["label"] = "radGraficoUnoDosTres.CheckedChanged -> radGraficoUnoDosTres_CheckedChanged -> otraFuncionAdicional_Handler -> mas" * 2
        pdf, w, h = self.build(flow)
        parts = [p for p in pdf.pages[2:] if any("Vista" in op for op in p.ops)]
        self.assertGreaterEqual(len(parts), 2)
        for p in parts:
            self.assertTrue(any("Vista" in op for op in p.ops))
        self.assertEqual(page_overflows(pdf), [])

    def test_state_legend_wraps_inside_a_portrait_page(self):
        pdf, _w, _h = self.build(long_flow(8))
        portrait = [p for p in pdf.pages if p.width == 595.0 and any("Estados" in op for op in p.ops)]
        if portrait:
            self.assertEqual(page_overflows(pdf), [])

    def test_wireframe_parts_are_balanced(self):
        h = 1500
        parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="%d" viewBox="0 0 760 %d">' % (h, h)]
        for i in range(60):
            parts.append(f'<rect x="12" y="{20 + i * 24}" width="200" height="18" rx="4" fill="#fff" stroke="#000"/>')
        parts.append("</svg>")
        cuts = _safe_cuts(ET.fromstring("".join(parts)), h, 1000.0)
        self.assertEqual(len(cuts), 3)
        sizes = [b - a for a, b in zip(cuts, cuts[1:])]
        self.assertTrue(all(s <= 1000.5 for s in sizes))
        self.assertGreater(min(sizes), 400)           # no short orphan part


class LongRouteTests(unittest.TestCase):
    def test_a_long_route_wraps_at_step_boundaries_without_overflow(self):
        route = " -> ".join(["drpJefes.SelectedIndexChanged", "drpJefes_SelectedIndexChanged", "PreGesJerarquia.txTraerUsuario",
                             "sysPreGesJerarquia.traerSupervisores", "PPRE_GES_JERARQUIA.TRAER_SUPERVISORES", "destino posterior indeterminado"])
        pdf = PdfDocument("t")
        pdf.new_page()
        pdf.table(Table([[Run("Acción")], [Run("Ruta")]], [[[Run("Al pulsar «drpJefes»")], [Run(route, code=True)]]]))
        self.assertEqual(page_overflows(pdf, margin=40.0), [])
        drawn = [unescape(TEXT_OP.match(op).group(5)) for p in pdf.pages for op in p.ops if TEXT_OP.match(op) and TEXT_OP.match(op).group(1) == "F4"]
        self.assertGreater(len(drawn), 2)
        for symbol in ("PPRE_", "GES_", "JERARQUIA."):
            self.assertTrue(any(symbol in d for d in drawn))


class FinalCandidateIconRules(unittest.TestCase):
    """H4 cleanup + final candidate: a wide button-face bitmap is never squeezed into the 16px icon slot; square icons stay."""

    @staticmethod
    def _gif(w: int, h: int) -> str:
        import base64, struct
        return "data:image/gif;base64," + base64.b64encode(b"GIF87a" + struct.pack("<HH", w, h) + bytes(16)).decode()

    def test_wide_button_face_is_not_an_icon(self):
        from legacy_documenter.behavior.wireframe import is_glyph_icon
        self.assertFalse(is_glyph_icon(self._gif(110, 20)))
        self.assertTrue(is_glyph_icon(self._gif(16, 16)))
        self.assertTrue(is_glyph_icon(self._gif(20, 16)))

    def test_ai_notice_wording_is_the_single_human_note(self):
        from pathlib import Path as P
        for audience in ("default", "executive"):
            y = (P(R.__file__).parent.parent / "templates" / "human" / audience / "template.yaml").read_text(encoding="utf-8")
            self.assertIn("Las afirmaciones se distinguen como Confirmadas, Inferidas o No resueltas.", y)
            self.assertNotIn("conservan su estado de confianza", y)

    def test_human_text_names_views_without_source_files(self):
        from legacy_documenter.behavior.humanize import humanize_blocks, humanize_text
        self.assertEqual(humanize_text("La abren: ucBusSuc.ascx, ucPreX.ascx y otras."), "La abren: ucBusSuc, ucPreX y otras.")
        out = humanize_blocks([Para([Run("ucBusSuc.ascx", code=True), Run(" abre ucPreX.aspx")])])[0]
        self.assertEqual("".join(r.text for r in out.runs), "ucBusSuc abre ucPreX")

    def test_wireframe_header_and_title_carry_no_source_path(self):
        from legacy_documenter.behavior import wireframe
        from legacy_documenter.behavior.ui_evidence import PersistedMarkup
        from legacy_documenter.evidence.ui_model import MarkupControl
        ctl = MarkupControl(id="txtA", tag="snt:textbox", kind="text", label="", line=1, attrs={})
        ui = wireframe.build("WebX\\ucBusSuc.ascx", PersistedMarkup([ctl], [{"rows": [{"cells": [{"items": ["txtA"], "width": "", "attrs": {}}]}], "attrs": {}}], 1, []),
                             "WebX\\ucBusSuc.ascx", set())
        self.assertNotIn(".ascx", ui.svg)
        self.assertNotIn("WebX", ui.svg)
        self.assertIn("ucBusSuc", ui.svg)


if __name__ == "__main__":
    unittest.main()
