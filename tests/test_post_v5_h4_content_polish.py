"""Post-V5 H4 final human content polish: names and relations over counts, grouped uncertainty, audience-specific output, internals kept internal.

Presentation-layer only: no scanner, no analyzer, no provider call, no source read while rendering.
"""
from __future__ import annotations

import copy
import re
import unittest
from unittest import mock

from legacy_documenter.behavior import render as R
from legacy_documenter.behavior.model import AI_INTERPRETATION, UNRESOLVED
from legacy_documenter.behavior.template import discover
from tests.test_post_v5_h4_r4_behavioral import BehaviorBase


class ContentPolishTests(BehaviorBase):
    templates: dict = {}

    def doc_with_ai(self):
        doc = copy.deepcopy(self.doc)
        view = doc.views[0]
        view.ai_narrative = {
            "simple_summary": [R.Claim("Esta pantalla permite trabajar con clientes.", AI_INTERPRETATION, ["src:Web\\X.ascx:1"], "porque el título lo dice", "ai")],
            "observable_purpose": [R.Claim("Al abrirse prepara los campos.", AI_INTERPRETATION, ["FLOW-0000000001"], "razonamiento interno", "ai")]}
        doc.ai_manifest = {"status": "COMPLETED", "provider_id": "scripted", "model_id": "scripted-1", "request_count": 1, "successful_requests": 1,
                           "replayed_from_real_run": True}
        return doc

    def html(self, doc=None, template="human/default"):
        t = self.templates.get(template) or discover(template)
        return R.html_document(R.compose(doc or self.doc_with_ai(), t)[0], "t", t)

    def test_ai_references_and_reasoning_are_collapsed_not_interleaved(self):
        html = self.html()
        self.assertNotIn("Basada en:", html)
        self.assertNotIn("Razonamiento:", html)
        self.assertNotIn("Respaldo de la interpretación", html)    # references / reasoning are machine provenance (ai/, internal/), not human text
        self.assertNotIn("razonamiento interno", html)
        self.assertNotIn("src:Web", html)

    def test_counts_are_not_the_primary_narrative(self):
        html = self.html()
        self.assertNotRegex(html, r"operación\(es\)")
        self.assertNotRegex(html, r"\(x\d+\)")
        self.assertNotIn("Invocaciones entrantes confirmadas (", html)
        for v in self.doc.views:
            for a in v.actions:
                if a.simple:
                    self.assertNotRegex(a.simple.text, r"\d+ operaci")
            for c in v.unresolved.unresolved:
                self.assertNotRegex(c.text, r"\(x\d+\)")

    def test_actions_show_a_route_with_real_symbol_names(self):
        for v in self.doc.views:
            for a in v.actions:
                route = R.route_text(a)
                self.assertIn(" → ", route) if a.handler and len(route.split(" → ")) > 1 else None
                self.assertIn(a.handler, route)
                self.assertNotIn("MyBase.", route)
                parts = route.split(" → ")
                self.assertEqual(len(parts), len(set(p.lower() for p in parts)), route)       # no repeated hop
        html = self.html()
        self.assertIn('<th scope="col">Acción</th><th scope="col">Ruta</th>', html)
        self.assertTrue(re.search(r"→", html))

    def test_open_end_of_a_route_is_written_once_without_explanations(self):
        a = next(a for v in self.doc.views for a in v.actions if not a.data)
        route = R.route_text(a)
        self.assertTrue(route.endswith("destino posterior indeterminado"))
        self.assertEqual(route.count("indeterminado"), 1)

    def test_uncertainty_is_grouped_and_not_repeated_per_view(self):
        html = self.html()
        self.assertNotIn("Estado: no resuelto.", html)
        generic = "El propósito de negocio de esta pantalla no se puede determinar"
        # the generic statement lives in the (collapsed) deterministic claims of each view at most; the unresolved section states the general limit once
        section = html[html.index('id="s-unresolved"'):html.index('id="s-appendix"')]
        self.assertEqual(section.count("no son determinables estáticamente"), 1)
        self.assertNotIn(generic, section)
        chapters = html[html.index('id="s-view-chapters"'):html.index('id="s-unresolved"')]
        visible = re.sub(r"<details>.*?</details>", "", chapters, flags=re.S)
        self.assertNotIn(generic, visible)

    def test_unresolved_is_preserved_in_the_semantic_model(self):
        self.assertTrue(any(c.status == UNRESOLVED for v in self.doc.views for c in v.unresolved.unresolved))
        self.assertTrue(all(c.status == UNRESOLVED for v in self.doc.views for c in v.unresolved.unresolved))
        html = self.html()
        self.assertIn("No resuelto", html)

    def test_executive_excludes_technical_internals(self):
        html = self.html(template="human/executive")
        for needle in ("Respaldo de la interpretación", "Referencias y controles", "Línea base", "FLOW-", "EP-0", "Rol observado", "Base de las afirmaciones",
                       "Mediciones de cobertura", "Capacidad:"):
            self.assertNotIn(needle, html, needle)
        for v in self.doc.views:
            for a in v.actions:
                if a.handler:
                    self.assertNotIn(a.handler, html)         # no handler / method names in the executive reading
        self.assertIn("Impacto en datos", html)

    def test_default_keeps_routes_and_the_executive_has_none(self):
        default, executive = self.html(), self.html(template="human/executive")
        self.assertIn("destino posterior indeterminado", default)
        self.assertNotIn("destino posterior indeterminado", executive)
        self.assertNotEqual(default, executive)

    def test_executive_cover_has_no_provider_or_model_names(self):
        html = self.html(template="human/executive")
        self.assertNotIn("scripted-1", html)
        self.assertNotIn('class="provenance"', html)                    # the single AI note replaces the cover provenance sentence
        self.assertIn("Interpretación asistida por IA", html)

    def test_internal_diagnostics_stay_available_in_the_model(self):
        doc = self.doc_with_ai()
        self.assertEqual(doc.ai_manifest["request_count"], 1)
        claim = doc.views[0].ai_narrative["simple_summary"][0]
        self.assertEqual(claim.source_refs, ["src:Web\\X.ascx:1"])
        self.assertEqual(claim.basis, "porque el título lo dice")
        self.assertNotIn("Metadatos del análisis", self.html())             # coverage metrics: model / ai/ only, never the human document
        self.assertTrue(doc.measurements)

    def test_rendering_calls_no_provider_and_reads_no_source(self):
        self.templates = {n: discover(n) for n in ("human/default", "human/executive")}
        with mock.patch("legacy_documenter.llm.registry.ProviderRegistry.create") as provider, \
                mock.patch("pathlib.Path.read_text", side_effect=AssertionError("source read")) as reader:
            for template in ("human/default", "human/executive"):
                self.html(template=template)
            self.assertEqual(provider.call_count, 0)
            self.assertEqual(reader.call_count, 0)

    def test_templates_preserve_semantic_truth(self):
        before = copy.deepcopy(self.doc_with_ai())
        doc = self.doc_with_ai()
        for template in ("human/default", "human/executive"):
            self.html(doc, template)
        from legacy_documenter.behavior.model import to_dict
        self.assertEqual(to_dict(doc), to_dict(before))

    def test_pdf_leaves_out_collapsed_backing(self):
        names = {"Respaldo de la interpretación", "Base de las afirmaciones", "Base del uso observable", "Por qué se eligieron estas vistas"}
        self.assertTrue(names <= R.PDF_SKIP_DETAILS)


if __name__ == "__main__":
    unittest.main()
