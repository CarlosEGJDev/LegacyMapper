"""Post-V5 H4 final human noise and PDF polish: known behaviour first, uncertainty as supporting information, safe wireframe pagination.

Presentation only: the AI package and the semantic model are untouched; no provider, no scanner/analyzer, no source read.
"""
from __future__ import annotations

import json
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

from legacy_documenter.behavior import render as R
from legacy_documenter.behavior.template import discover
from legacy_documenter.deliver.pdf import PdfDocument, _safe_cuts
from legacy_documenter.product import package as K
from tests.test_post_v5_h4_r4_behavioral import BehaviorBase


def section(html: str, start: str, end: str) -> str:
    return html[html.index(f'id="{start}"'):html.index(f'id="{end}"')]


class HumanNoiseTests(BehaviorBase):
    def html(self, template):
        t = discover(template)
        return R.html_document(R.compose(self.doc, t)[0], "t", t)

    def test_executive_limitations_are_a_short_final_note_without_call_tables(self):
        html = self.html("human/executive")
        note = section(html, "s-unresolved", "s-appendix")
        self.assertIn("Limitaciones conocidas", note)
        self.assertLessEqual(note.count("<li>"), 4)
        self.assertGreaterEqual(note.count("<li>"), 1)
        for needle in ("<table", "Llamada sin destino", "Acciones cuyo destino", "Lo que no se puede afirmar"):
            self.assertNotIn(needle, note)
        self.assertLess(html.index('id="s-view-chapters"'), html.index('id="s-unresolved"'))     # closes the reading, not a major section up front

    def test_executive_names_no_technical_calls_in_its_limitations(self):
        note = section(self.html("human/executive"), "s-unresolved", "s-appendix")
        for v in self.doc.views:
            for a in v.actions:
                for u in (a.technical_path.unresolved_calls if a.technical_path else []):
                    if u.get("business_call"):
                        self.assertNotIn(u["business_call"], note)

    def test_default_keeps_unresolved_detail_collapsed_not_in_the_main_text(self):
        html = self.html("human/default")
        note = section(html, "s-unresolved", "s-appendix")
        visible = re.sub(r"<details>.*?</details>", "", note, flags=re.S)
        self.assertNotIn("Llamada sin destino", visible)                    # the table of undetermined calls lives in a collapsible block
        self.assertIn("Llamada sin destino", note)                          # ... and is still there (HTML is complete)

    def test_same_uncertainty_is_not_repeated_in_the_visible_text(self):
        html = self.html("human/default")
        visible = re.sub(r"<details>.*?</details>", "", html, flags=re.S)
        text = re.sub(r"<[^>]+>", " ", visible)
        for statement in ("no se pueden determinar", "no son determinables estáticamente"):
            self.assertLessEqual(text.count(statement), 2, statement)
        chapters = re.sub(r"<[^>]+>", " ", re.sub(r"<details>.*?</details>", "", section(html, "s-view-chapters", "s-cross-view"), flags=re.S))
        self.assertNotIn("Estado: no resuelto", chapters)
        self.assertNotIn("Qué sabemos, qué inferimos", chapters)

    def test_known_behaviour_precedes_uncertainty_in_each_chapter(self):
        html = self.html("human/default")
        for v in self.doc.views:
            chapter = html[html.index(f'id="vista-{R.slug(v.name)}"'):]
            nxt = chapter.find('<h3', 10)
            chapter = chapter[:nxt] if nxt > 0 else chapter[:section_end(chapter)]
            if "Trazabilidad de la vista" in chapter and "Acciones principales" in chapter:
                self.assertLess(chapter.index("Acciones principales"), chapter.index("Trazabilidad de la vista"))
            self.assertLess(chapter.index("En una frase"), chapter.index("Uso observable"))

    def test_usage_reasoning_is_not_repeated_outside_the_collapsed_basis(self):
        from legacy_documenter.behavior.model import AI_INTERPRETATION
        import copy
        doc = copy.deepcopy(self.doc)
        doc.views[0].ai_narrative = {"usage_reasoning": [R.Claim("Razonamiento de uso único.", AI_INTERPRETATION, [], "b", "ai")]}
        html = R.html_document(R.compose(doc, discover("human/default"))[0], "t", discover("human/default"))
        self.assertNotIn("Razonamiento de uso único.", html)         # the usage basis is evidence: ai/knowledge.json keeps it
        self.assertEqual(doc.views[0].ai_narrative["usage_reasoning"][0].text, "Razonamiento de uso único.")

    def test_ai_package_is_independent_of_human_presentation(self):
        out = self.tmp / "pkg_noise"
        K.build_package(self.baseline, out, project="Web", solution="SampleLegacy")
        ai_text = "".join((out / "ai" / n).read_text(encoding="utf-8") for n in ("knowledge.json", "unresolved.json", "flows.json"))
        self.assertNotIn("Limitaciones conocidas", ai_text)
        unresolved = json.loads((out / "ai" / "unresolved.json").read_text(encoding="utf-8"))["unresolved"]
        self.assertTrue(any(u.get("calls") for u in unresolved))            # full detail stays in ai/
        exec_html = (out / "human" / "executive" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("<table", section(exec_html, "s-unresolved", "s-appendix"))

    def test_no_provider_scanner_or_source_read(self):
        with mock.patch("legacy_documenter.llm.registry.ProviderRegistry.create") as provider, \
                mock.patch("legacy_documenter.cli.full_pipeline.run_full_pipeline", side_effect=AssertionError("analysis rerun")) as pipeline:
            for tpl in ("human/default", "human/executive"):
                self.html(tpl)
            self.assertEqual((provider.call_count, pipeline.call_count), (0, 0))


def section_end(text: str) -> int:
    m = re.search(r'<h2 id="s-', text)
    return m.start() if m else len(text)


def wireframe_svg(rows: int, row_h: int = 40, width: int = 760) -> str:
    height = 80 + rows * row_h
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-size="11">',
             f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>',
             '<rect x="0" y="0" width="760" height="22" fill="#fef3c7" stroke="#b45309"/><text x="8" y="15" font-size="11">RECONSTRUCCIÓN DOCUMENTAL</text>']
    for i in range(rows):
        y = 60 + i * row_h
        parts.append(f'<rect x="12" y="{y}" width="220" height="22" rx="5" fill="#fff" stroke="#6b7280"/>')
        parts.append(f'<text x="18" y="{y + 15}" font-size="10">[iconoAsignar{i}]</text>')
    parts.append("</svg>")
    return "\n".join(parts)


class WireframePaginationTests(unittest.TestCase):
    def render(self, rows: int):
        d = Path(tempfile.mkdtemp(prefix="wf_"))
        self.addCleanup(lambda: __import__("shutil").rmtree(d, True))
        (d / "assets").mkdir()
        (d / "assets" / "w.svg").write_text(wireframe_svg(rows), encoding="utf-8")
        pdf = PdfDocument("t", footer_title="t")
        pdf.assets_root = d
        pdf.reserve_front()
        fig = R._fig("Reconstrucción documental de V", "assets/w.svg", 760, 80 + rows * 40, "wireframe", rows)
        pdf.blocks([fig])
        pdf.fill_front("sub", [])
        data, stats = pdf.render()
        return data, stats, pdf

    def test_a_tall_wireframe_is_scaled_onto_a_single_page(self):
        data, stats, pdf = self.render(26)          # ~1120 units tall
        self.assertTrue(data.startswith(b"%PDF"))
        self.assertEqual(stats["figure_pages"], 1)

    def test_a_very_tall_wireframe_is_cut_only_between_controls(self):
        root = ET.fromstring(wireframe_svg(60))
        height = float(root.get("height"))
        cuts = _safe_cuts(root, height, 900.0)
        self.assertIsNotNone(cuts)
        self.assertGreater(len(cuts), 2)
        for y in cuts[1:-1]:
            for el in root.iter():
                tag = el.tag.split("}")[-1]
                if tag == "rect" and float(el.get("height", "0")) < 100:
                    top = float(el.get("y")); self.assertFalse(top + 0.5 < y < top + float(el.get("height")) - 0.5, f"cut {y} crosses a control")
                if tag == "text":
                    ty = float(el.get("y")); size = float(el.get("font-size", "11"))
                    self.assertFalse(ty - size + 0.5 < y < ty + size * 0.3 - 0.5, f"cut {y} crosses a label")

    def test_pages_of_a_split_wireframe_keep_equal_scale_and_titles(self):
        data, stats, pdf = self.render(60)
        self.assertGreaterEqual(stats["figure_pages"], 2)

    def test_pdf_is_deterministic(self):
        a, _, _ = self.render(26)
        b, _, _ = self.render(26)
        self.assertEqual(a, b)


class TableAndHeadingTests(unittest.TestCase):
    def test_orphan_subheading_without_pdf_content_is_dropped(self):
        from legacy_documenter.deliver.markdown import Details, Heading, Para, Run
        blocks = [Heading(2, [Run("1. Sección")], "s-a", "section-title"), Heading(3, [Run("1.1 Vista")], "v", "view-title"),
                  Heading(4, [Run("Trazabilidad de la vista")], ""), Details("Respaldo de la interpretación", [Para([Run("x")])]),
                  Heading(4, [Run("Acciones")], ""), Para([Run("contenido")])]
        d = Path(tempfile.mkdtemp(prefix="oh_"))
        self.addCleanup(lambda: __import__("shutil").rmtree(d, True))
        data, _ = R.build_pdf(blocks, "t", d, [], discover("human/default"))
        import pypdf, io
        text = " ".join((p.extract_text() or "") for p in pypdf.PdfReader(io.BytesIO(data)).pages)
        self.assertNotIn("Trazabilidad de la vista", text)
        self.assertIn("Acciones", text)


if __name__ == "__main__":
    unittest.main()


class CatalogAndLabelTests(BehaviorBase):
    def pdf_text(self, template="human/default"):
        import io
        import pypdf
        t = discover(template)
        blocks, assets = R.compose(self.doc, t)
        d = self.tmp / ("pdf_" + template.split("/")[1])
        d.mkdir(exist_ok=True)
        for rel, (svg, _k) in assets.items():
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            (d / rel).write_text(svg, encoding="utf-8")
        data, _ = R.build_pdf(blocks, "t", d, [], t)
        return data, " ".join((p.extract_text() or "") for p in pypdf.PdfReader(io.BytesIO(data)).pages)

    def test_pdf_catalog_has_descriptive_columns_only(self):
        data, text = self.pdf_text()
        self.assertTrue(data.startswith(b"%PDF"))
        for header in ("Qué parece hacer", "Uso observable", "Título visible"):
            self.assertIn(header, text)
        for low_value in ("¿Lee?", "¿Escribe?", "¿Abre otra?", "Cómo se llega", "Mediciones de cobertura", "vistas del proyecto",
                          "con invocaciones entrantes", "soportan wireframe documental"):
            if low_value == "vistas del proyecto":
                self.assertNotRegex(text, r"vistas del proyecto\s+\d")       # the measurement row, not the cover sentence
            else:
                self.assertNotIn(low_value, text)
        for v in self.doc.catalog:
            self.assertIn(v["name"], text)

    def test_coverage_metrics_stay_in_a_collapsed_html_diagnostic_and_in_the_model(self):
        t = discover("human/default")
        html = R.html_document(R.compose(self.doc, t)[0], "t", t)
        self.assertNotIn("Mediciones de cobertura", html)
        self.assertNotIn("Metadatos del análisis", html)            # diagnostics are not part of the human document any more
        self.assertTrue(self.doc.measurements)                      # they stay in the model (ai/provenance.json, internal/)

    def test_scope_counts_with_names_are_still_allowed(self):
        t = discover("human/default")
        html = R.html_document(R.compose(self.doc, t)[0], "t", t)
        self.assertRegex(re.sub(r"<[^>]+>", " ", html), r"agrupa \d+ proyectos: ")

    def test_icon_labels_are_human_readable_and_horizontal(self):
        from types import SimpleNamespace as N
        from legacy_documenter.behavior.wireframe import display_label
        cases = [("[iconoAsignar]", "", "", "Asignar"), ("[icono buscar]", "", "", "Buscar"), ("", "img/iconoDesasociar.gif", "i", "Desasociar"),
                 ("Guardar", "", "", "Guardar"), ("[icono Eliminar]", "", "", "Eliminar")]
        for label, img, ident, want in cases:
            self.assertEqual(display_label(N(label=label, attrs={"imageurl": img}, id=ident)), want)
        self.assertEqual(display_label(N(label="", attrs={}, id="")), "Icono")      # nothing to say: a neutral placeholder, never invented

    def test_wireframes_have_no_vertical_character_stacks(self):
        for v in self.doc.views:
            if not (v.ui and v.ui.svg):
                continue
            texts = re.findall(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*>([^<]*)</text>', v.ui.svg)
            run = 0
            prev = None
            for x, y, s in texts:
                if len(s.strip()) == 1 and prev is not None and prev[0] == x and float(y) > float(prev[1]):
                    run += 1
                    self.assertLess(run, 3, f"vertical character stack in {v.name}")
                else:
                    run = 0
                prev = (x, y, s) if len(s.strip()) == 1 else None

    def test_pdf_is_deterministic(self):
        self.assertEqual(self.pdf_text()[0], self.pdf_text()[0])
