"""H4 final screen-reconstruction and narrative micro-polish: structural invariants (no provider, no scanner, no source reads)."""
from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET

from legacy_documenter.behavior import render as R
from legacy_documenter.behavior import wireframe
from legacy_documenter.behavior.humanize import humanize_blocks, humanize_text
from legacy_documenter.behavior.template import discover
from legacy_documenter.behavior.ui_evidence import PersistedMarkup
from legacy_documenter.deliver.markdown import Para, Run
from legacy_documenter.deliver.pdf import text_width
from legacy_documenter.evidence.ui_model import MarkupControl
from tests.test_post_v5_h4_evidence_separation import SeparationBase

NS = "{http://www.w3.org/2000/svg}"


def ctl(id_: str, kind: str, label: str = "", tag: str = "snt:label", line: int = 1) -> MarkupControl:
    return MarkupControl(id=id_, tag=tag, kind=kind, label=label, line=line, attrs={})


def cell(items, width: str = "") -> dict:
    return {"items": items, "width": width, "attrs": {}}


def table(rows, width: str = "100%") -> dict:
    return {"rows": [{"cells": r} for r in rows], "attrs": {"width": width}}


def build_svg(controls: list, skeleton: list) -> tuple[str, object]:
    ui = wireframe.build("Web\\V", PersistedMarkup(controls, skeleton, 1, []), "Web\\V.ascx", set())
    return ui.svg, ui


def texts(svg: str) -> list[tuple[float, float, str, float, bool]]:
    out = []
    for el in ET.fromstring(svg).iter(NS + "text"):
        if (el.text or "").strip():
            out.append((float(el.get("x")), float(el.get("y")), el.text, float(el.get("font-size", "11")), el.get("font-weight") == "bold"))
    return out


def rects(svg: str) -> list[tuple[float, float, float, float]]:
    return [tuple(float(r.get(k)) for k in ("x", "y", "width", "height")) for r in ET.fromstring(svg).iter(NS + "rect")]


def jerarquia() -> tuple[list, list]:
    controls = [ctl("lblDepend", "label", "Empleados Dependientes"), ctl("lblIndepen", "label", "Empleados NO dependientes"),
                ctl("lstDepend", "dropdown", tag="asp:listbox"), ctl("lstNoDepend", "dropdown", tag="asp:listbox"),
                ctl("lblMensaje1", "label", ""), ctl("hypAsignar", "link", "", tag="snt:hyperlink"), ctl("Label1", "label", "<"),
                ctl("Label2", "label", ">>"), ctl("HypDesasociar", "link", "", tag="snt:hyperlink"), ctl("lblMensaje2", "label", "")]
    transfer = table([[cell([]), cell(["hypAsignar"]), cell(["Label1"])], [cell([]), cell([]), cell([])], [cell(["Label2"]), cell(["HypDesasociar"]), cell([])]], "106")
    centre = table([[cell(["lblMensaje1"])], [cell([transfer])], [cell(["lblMensaje2"])]], "97")
    outer = table([[cell(["lblDepend"], "328px"), cell([], "104px"), cell(["lblIndepen"])],
                   [cell(["lstDepend"], "328px"), cell([centre], "104px"), cell(["lstNoDepend"])]], "560")
    return controls, [outer]


class TransferControlsTests(unittest.TestCase):
    def setUp(self):
        controls, skeleton = jerarquia()
        self.svg, self.ui = build_svg(controls, skeleton)
        self.t = texts(self.svg)

    def test_transfer_buttons_read_as_whole_words_without_arrow_debris(self):
        captions = [s for _x, _y, s, _z, _b in self.t]
        self.assertIn("Asignar", captions)
        self.assertIn("Desasociar", captions)
        for debris in ("<", ">", ">>", "<<"):
            self.assertNotIn(debris, captions)             # direction cannot be established safely: no arrows are drawn

    def test_the_two_actions_share_one_width_and_do_not_overlap(self):
        by_text = {s: (x, y) for x, y, s, _z, _b in self.t}
        ax, ay = by_text["Asignar"]
        dx, dy = by_text["Desasociar"]
        self.assertGreater(dy, ay)                          # stacked, Asignar above Desasociar
        self.assertAlmostEqual(ax, dx, delta=1)             # aligned in one action column
        buttons = [r for r in rects(self.svg) if r[3] < 40 and abs(r[0] - (ax - 8)) < 6]
        self.assertGreaterEqual(len(buttons), 2)
        self.assertEqual(len({round(b[2]) for b in buttons}), 1)
        buttons.sort(key=lambda r: r[1])
        for a, b in zip(buttons, buttons[1:]):
            self.assertLessEqual(a[1] + a[3], b[1] + 0.5)

    def test_captions_fit_inside_their_buttons(self):
        for x, y, s, size, bold in self.t:
            if s in ("Asignar", "Desasociar"):
                width = text_width(s, "F2" if bold else "F1", size)
                box = [r for r in rects(self.svg) if r[0] <= x <= r[0] + r[2] and r[1] <= y <= r[1] + r[3] and r[3] < 40]
                self.assertTrue(box)
                self.assertLessEqual(x + width, min(box, key=lambda r: r[2])[0] + min(box, key=lambda r: r[2])[2])

    def test_message_placeholders_read_below_the_actions(self):
        by_text = {s: y for _x, y, s, _z, _b in self.t}
        self.assertGreater(by_text["lblMensaje1"], by_text["Desasociar"])
        self.assertGreater(by_text["lblMensaje2"], by_text["lblMensaje1"])

    def test_the_machine_model_keeps_every_control(self):
        ids = {c.id for c in self.ui.controls}
        self.assertTrue({"Label1", "Label2", "hypAsignar", "HypDesasociar", "lblMensaje1"} <= ids)   # raw identity stays in the model


class WholeWordTests(unittest.TestCase):
    def one_row(self, labels_and_widths):
        controls, cells = [], []
        for i, (kind, label, width) in enumerate(labels_and_widths):
            controls.append(ctl(f"c{i}", kind, label, tag="asp:textbox" if kind == "text" else "snt:label"))
            cells.append(cell([f"c{i}"], width))
        return build_svg(controls, [table([cells])])[0]

    def test_criterio_in_a_14px_cell_is_not_stacked(self):
        svg = self.one_row([("label", "Criterio", "14px"), ("dropdown", "", "174px"), ("text", "", "")])
        t = texts(svg)
        self.assertIn("Criterio", [s for _x, _y, s, _z, _b in t])
        self.assertFalse([s for _x, _y, s, _z, _b in t if s in ("Cr", "ite", "rio")])

    def test_hasta_between_two_dates_stays_horizontal_with_minimum_width(self):
        controls = [ctl("fec_ini", "text", tag="asp:textbox"), ctl("Label4", "label", "Hasta"), ctl("fec_fin", "text", tag="asp:textbox")]
        inner = table([[cell(["fec_ini"]), cell(["Label4"], "5%"), cell(["fec_fin"])]], "")
        outer = table([[cell([], "15%"), cell([inner], "20%"), cell([], "10%"), cell([], "15%")]])
        svg, _ui = build_svg(controls, [outer])
        t = {s: (x, y) for x, y, s, _z, _b in texts(svg)}
        self.assertIn("Hasta", t)
        self.assertFalse([s for s in t if s in ("H", "as", "ta")])
        ini = next(v for k, v in t.items() if k.startswith("[fec_ini"))
        fin = next(v for k, v in t.items() if k.startswith("[fec_fin"))
        self.assertLess(ini[0], t["Hasta"][0])
        self.assertLess(t["Hasta"][0], fin[0])
        self.assertAlmostEqual(ini[1], t["Hasta"][1], delta=14)    # same line: reads "[fec_ini]  Hasta  [fec_fin]"
        hasta_cell = [r for r in rects(svg) if r[0] <= t["Hasta"][0] <= r[0] + r[2] and r[1] <= t["Hasta"][1] <= r[1] + r[3]]
        self.assertGreaterEqual(min(hasta_cell, key=lambda r: r[2])[2], text_width("Hasta", "F1", 11))

    def test_no_label_word_is_ever_split_across_text_lines(self):
        words = ["Clasificación", "Profesional", "Desasociar", "Criterio", "Hasta", "Acción", "Fecha"]
        controls = [ctl(f"l{i}", "label", w) for i, w in enumerate(words)]
        svg, _ui = build_svg(controls, [table([[cell([f"l{i}"], "6%") for i in range(len(words))]])])
        got = [s for _x, _y, s, _z, _b in texts(svg)]
        for w in words:
            self.assertIn(w, got)


class HumanProseTests(unittest.TestCase):
    def test_source_line_suffixes_are_removed_from_prose(self):
        self.assertEqual(humanize_text("Puede mostrar el mensaje «Debe Ingresar Fecha de Inicio» (línea 146)."),
                         "Puede mostrar el mensaje «Debe Ingresar Fecha de Inicio».")
        self.assertEqual(humanize_text("abre «x/y» (ventana emergente; línea 12)."), "abre «x/y» (ventana emergente).")

    def test_audit_language_becomes_documentary_language(self):
        self.assertEqual(humanize_text("La evidencia muestra una vista."), "Se observa una vista.")
        self.assertEqual(humanize_text("La evidencia no precisa qué hace."), "El análisis no precisa qué hace.")
        self.assertEqual(humanize_text("pero la evidencia no identifica los datos"), "pero el análisis no identifica los datos")
        self.assertEqual(humanize_text("La evidencia confirma que llega al manejador"), "El análisis confirma que llega al manejador")
        self.assertEqual(humanize_text("Evidencia de uso"), "Uso observable")

    def test_code_runs_and_figures_are_untouched(self):
        blocks = humanize_blocks([Para([Run("La evidencia muestra "), Run("a(línea 3)", code=True)])])
        self.assertEqual(blocks[0].runs[0].text, "Se observa ")
        self.assertEqual(blocks[0].runs[1].text, "a(línea 3)")


class HumanDocumentTests(SeparationBase):
    def html(self, doc=None, template="human/default"):
        t = discover(template)
        return R.html_document(R.compose(doc or self.with_ai()[0], t)[0], "t", t)

    def visible(self, html: str) -> str:
        import html as h
        return h.unescape(re.sub(r"<[^>]+>", " ", html.replace("<wbr>", "")))

    def test_no_line_numbers_and_no_evidencia_de_uso_in_human_html_and_pdf(self):
        for template in ("human/default", "human/executive"):
            text = self.visible(self.html(template=template))
            self.assertIsNone(re.search(r"línea \d+", text), template)
            self.assertNotIn("Evidencia de uso", text)
        self.assertIsNone(re.search(r"línea \d+", self.pdf()))
        self.assertNotIn("Evidencia de uso", self.pdf())

    def test_line_numbers_remain_in_the_shared_knowledge_model(self):
        doc = self.with_ai()[0]
        refs = [r for v in self.explained.values() for a in v.actions for c in a.result for r in c.source_refs]
        self.assertTrue(any(re.search(r":\d+$", r) for r in refs))          # `src:file:line` survives for ai/ and internal/
        in_model = [c.text for v in self.explained.values() for a in v.actions for c in a.result]
        self.assertTrue(any("línea" in t for t in in_model))                # the model is not rewritten; only the human prose is
        self.assertIsNotNone(doc)

    def test_human_legend_has_three_states_and_exactly_one_ai_notice(self):
        html = self.html()
        self.assertEqual(html.count('class="ai-notice"'), 1)
        for state in ("Confirmado", "Inferido", "No resuelto"):
            self.assertIn(state, html)
        text = self.visible(html)
        self.assertNotIn("Canónico", text)
        self.assertNotIn("AI_INTERPRETATION", text)
        pdf = self.pdf()
        self.assertNotIn("Canónico", pdf)
        self.assertNotIn("no aprobada", pdf)


if __name__ == "__main__":
    unittest.main()
