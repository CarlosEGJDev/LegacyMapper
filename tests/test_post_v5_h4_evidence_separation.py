"""Post-V5 H4 final human interpretation / evidence separation: humans read the interpretation; ai/ and internal/ keep the proof.

Presentation-layer only: no scanner, no analyzer, no provider call, no source read while rendering.
"""
from __future__ import annotations

import copy
import io
import json
import re
import unittest
from unittest import mock

from legacy_documenter.behavior import render as R
from legacy_documenter.behavior.model import AI_INTERPRETATION, CONFIRMED, INFERRED, UNRESOLVED
from legacy_documenter.behavior.template import discover
from legacy_documenter.product import package as K
from tests.test_post_v5_h4_r4_behavioral import BehaviorBase

NOISE = re.compile(r"\bEP-\d+|\bFLOW-\d+|\bCALL-\d+|\bDAO-\d+|src:|Base de las afirmaciones|Referencias:|Respaldo de la interpretación|"
                   r"huella|sha256|copilot-local|request_id|\.vb:\d+|\.ascx:\d+|\.aspx:\d+")
AI_REF = "src:Web\\X.ascx:1"
AI_FLOW = "FLOW-0000000001"


class SeparationBase(BehaviorBase):
    def with_ai(self):
        doc, explained = copy.deepcopy((self.doc, self.explained))
        view = doc.views[0]
        view.ai_narrative = {
            "simple_summary": [R.Claim("Esta pantalla permite trabajar con clientes.", AI_INTERPRETATION, [AI_REF], "porque el título lo dice", "ai")],
            "observable_purpose": [R.Claim("Al abrirse prepara los campos.", AI_INTERPRETATION, [AI_FLOW], "razonamiento interno", "ai")],
            "usage_reasoning": [R.Claim("Se usa desde otra pantalla.", AI_INTERPRETATION, [AI_FLOW], "razonamiento de uso", "ai")]}
        doc.ai_manifest = {"status": "COMPLETED", "provider_id": "copilot-local", "model_id": "scripted-1", "request_count": 1, "successful_requests": 1,
                           "replayed_from_real_run": True}
        return doc, explained

    def html(self, doc=None, template="human/default"):
        t = discover(template)
        # `<wbr>` soft-break hints (layout polish) are presentation only: the text content is compared without them
        return R.html_document(R.compose(doc or self.with_ai()[0], t)[0], "t", t).replace("<wbr>", "")

    def pdf(self, template="human/default"):
        import pypdf
        t = discover(template)
        blocks, assets = R.compose(self.with_ai()[0], t)
        d = self.tmp / ("sep_" + template.split("/")[1])
        d.mkdir(exist_ok=True)
        for rel, (svg, _k) in assets.items():
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            (d / rel).write_text(svg, encoding="utf-8")
        data, _ = R.build_pdf(blocks, "t", d, [R.provenance_sentence({"status": "COMPLETED"})], t)
        return " ".join((p.extract_text() or "") for p in pypdf.PdfReader(io.BytesIO(data)).pages)


class HumanDocumentHasNoEvidenceMachinery(SeparationBase):
    def test_no_ids_paths_or_provenance_in_html(self):
        for template in ("human/default", "human/executive"):
            html = self.html(template=template)
            self.assertIsNone(NOISE.search(html), (template, NOISE.search(html) and NOISE.search(html).group(0)))
            self.assertNotIn("Metadatos del análisis", html)

    def test_no_ids_paths_or_provenance_in_pdf(self):
        for template in ("human/default", "human/executive"):
            text = self.pdf(template)
            self.assertIsNone(NOISE.search(text), (template, NOISE.search(text) and NOISE.search(text).group(0)))
            self.assertNotIn("Afirmación Estado", text)

    def test_svg_diagrams_carry_no_support_ids(self):
        _blocks, assets = R.compose(self.with_ai()[0])
        self.assertTrue(assets)
        for rel, (svg, _kind) in assets.items():
            self.assertIsNone(re.search(r"\bEP-\d|\bFLOW-\d|\bCALL-\d|\bDAO-\d|src:", svg), rel)

    def test_message_table_has_no_line_numbers(self):
        self.assertNotIn('<th scope="col">Línea</th>', self.html())
        self.assertNotIn("Dónde (archivo:línea)", self.html())

    def test_claim_base_is_not_repeated_under_the_claim(self):
        html = self.html()
        self.assertNotIn("Base de las afirmaciones", html)
        self.assertEqual(html.count('<th scope="col">Afirmación</th><th scope="col">Estado</th>'), 0)
        self.assertEqual(html.count('<th scope="col">Base</th>'), 0)
        solution = html[html.index("1. La solución"):]
        card = solution.index("Confirmado")
        text = re.search(r"<p>(La solución «[^<]+)</p>", solution).group(1)
        self.assertEqual(html.count(text), 1)                         # a statement is shown once
        self.assertLess(solution.index(text), solution.index("Capa (inferida)"))
        self.assertGreater(card, -1)

    def test_provider_and_model_never_reach_the_human_document(self):
        html = self.html()
        self.assertNotIn("scripted-1", html)
        self.assertNotIn("copilot-local", html)
        self.assertNotIn("solicitudes", html)


class SingleNoticeAndColours(SeparationBase):
    def test_one_ai_notice_and_no_repeated_badges(self):
        html = self.html()
        self.assertEqual(html.count('<aside class="ai-notice"'), 1)
        self.assertEqual(html.count("Interpretación asistida por IA"), 1)
        self.assertIn("Este documento presenta una interpretación generada a partir del análisis de IST. Las afirmaciones se distinguen como "
                      "Confirmadas, Inferidas o No resueltas.", html)
        self.assertNotIn(R.AI_BASIS_SENTENCE, html)
        self.assertNotIn('<p class="callout-title">IA</p>', html)
        self.assertGreaterEqual(html.count('class="callout callout-ai" data-status="AI_INTERPRETATION"'), 2)    # the AI text keeps its status in the markup
        self.assertNotRegex(html, r"callout-title\">[^<]*IA[^<]*</p>")

    def test_legend_appears_once_near_the_beginning(self):
        html = self.html()
        body = html[html.index("<main"):]
        for label, meaning in (("Confirmado", "Lo demuestra el código analizado."), ("Inferido", "Deducido con una regla estructural"),
                               ("No resuelto", "El análisis no pudo determinarlo.")):
            self.assertEqual(body.count(meaning), 1, label)
            self.assertLess(body.index(meaning), body.index("1. La solución"))
        self.assertNotIn("legend-mini", html)

    def test_confirmed_inferred_unresolved_stay_visually_distinct(self):
        html = self.html()
        for cls in ("callout-note", "callout-semantic", "callout-unresolved"):
            self.assertIn(f'class="callout {cls}"', html)
        css = discover("human/default").styles_css
        for cls in (".callout-note", ".callout-semantic", ".callout-unresolved"):
            self.assertIn(cls, css)
        self.assertNotRegex(css, r"\.callout-ai \.callout-title")

    def test_claims_are_cards_known_first(self):
        cards = R.claim_cards([R.Claim("c3", UNRESOLVED, [], "b", "d"), R.Claim("c2", INFERRED, [], "b", "d"), R.Claim("c1", CONFIRMED, ["EP-1"], "b", "d")])
        self.assertEqual([c.title for c in cards], ["Confirmado", "Inferido", "No resuelto"])
        self.assertEqual([c.kind for c in cards], ["note", "semantic", "unresolved"])
        self.assertNotIn("EP-1", json.dumps([[r.text for r in p.runs] for c in cards for p in c.blocks]))

    def test_without_ai_the_notice_says_so(self):
        html = self.html(self.doc)
        self.assertIn(R.NO_AI_SENTENCE, html)
        self.assertNotIn("Este documento presenta una interpretación generada por IA", html)


class TechnicalRoutesRemain(SeparationBase):
    def test_routes_and_names_are_still_in_html_and_pdf(self):
        html = self.html()
        flat = re.sub(r"\s+", "", self.pdf())
        routes = [R.route_text(a) for v in self.doc.views for a in v.actions]
        self.assertTrue(routes)
        for route in routes:
            self.assertIn(route.replace("&", "&amp;"), html)
            self.assertIn(route.split(" → ")[0].replace(" ", ""), flat)
        for v in self.doc.views:
            self.assertIn(v.name, html)

    def test_path_labels_lose_only_the_support_id(self):
        self.assertEqual(R.step_label("Svc.cargar (DAO-0287808812)"), "Svc.cargar")
        self.assertEqual(R.step_label("PPRE_GES_JERARQUIA.CREAR"), "PPRE_GES_JERARQUIA.CREAR")


class TraceabilityRemainsMachineReadable(SeparationBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        doc, explained = cls_with_ai(cls)
        cls.projections = K.ai_projections(doc, explained, cls.bc, [])

    def test_ai_claims_keep_refs_and_basis(self):
        views = {v["name"]: v for v in self.projections["knowledge.json"]["views"]}
        first = self.doc.views[0].name
        summary = views[first]["explanation"]["simple_summary"][0]
        self.assertEqual(summary["source_refs"], [AI_REF])
        self.assertEqual(summary["basis"], "porque el título lo dice")
        self.assertEqual(views[first]["explanation"]["usage_reasoning"][0]["basis"], "razonamiento de uso")
        self.assertIn(AI_FLOW, json.dumps(views[first]["explanation"]))

    def test_views_carry_evidence_invocations_controls_and_fidelity(self):
        views = self.projections["knowledge.json"]["views"]
        detailed = [v for v in views if "traceability" in v]
        self.assertTrue(detailed)
        keys = {"source_refs", "invocations_in", "invocations_out", "usage_reasons", "markup_controls", "ui"}
        for v in detailed:
            self.assertEqual(set(v["traceability"]), keys)
        with_refs = [v for v in detailed if v["traceability"]["source_refs"]]
        self.assertTrue(with_refs)
        invocations = [i for v in detailed for i in v["traceability"]["invocations_in"] + v["traceability"]["invocations_out"]]
        for i in invocations:
            self.assertTrue({"file", "line", "mechanism", "parameters", "source_refs", "status"} <= set(i))
        self.assertTrue(any(v["traceability"]["markup_controls"] for v in detailed))

    def test_flows_keep_step_evidence(self):
        flows = self.projections["flows.json"]["flows"]
        self.assertTrue(flows)
        self.assertTrue(any(f["source_refs"] and any(s["source_refs"] for s in f["steps"]) for f in flows))

    def test_provenance_keeps_what_the_human_document_dropped(self):
        p = self.projections["provenance.json"]
        self.assertEqual(p["ai"]["provider_id"], "copilot-local")
        self.assertEqual(p["ai"]["request_count"], 1)
        self.assertIn("measurements", p)
        self.assertTrue(p["measurements"])
        self.assertTrue(p["selection_criteria"])
        self.assertIn("evidence_considered", p["module_evidence"])
        self.assertTrue(p["baseline"])
        self.assertEqual(p["validation_report"], "internal/behavioral/validation_report.json")

    def test_human_simplification_does_not_change_the_model_or_evidence(self):
        before = json.dumps(self.projections["knowledge.json"], sort_keys=True, default=str)
        doc, explained = cls_with_ai(self)
        R.compose(doc)
        R.html_document(R.compose(doc)[0], "t")
        self.assertEqual(json.dumps(K.ai_projections(doc, explained, self.bc, [])["knowledge.json"], sort_keys=True, default=str), before)


def cls_with_ai(owner):
    doc, explained = copy.deepcopy((owner.doc, owner.explained))
    doc.views[0].ai_narrative = {
        "simple_summary": [R.Claim("Esta pantalla permite trabajar con clientes.", AI_INTERPRETATION, [AI_REF], "porque el título lo dice", "ai")],
        "observable_purpose": [R.Claim("Al abrirse prepara los campos.", AI_INTERPRETATION, [AI_FLOW], "razonamiento interno", "ai")],
        "usage_reasoning": [R.Claim("Se usa desde otra pantalla.", AI_INTERPRETATION, [AI_FLOW], "razonamiento de uso", "ai")]}
    doc.ai_manifest = {"status": "COMPLETED", "provider_id": "copilot-local", "model_id": "scripted-1", "request_count": 1, "successful_requests": 1}
    return doc, explained


class PackageDoesNotCallAnything(SeparationBase):
    def test_package_build_makes_no_provider_call_and_no_analysis(self):
        out = self.tmp / "sep_package"
        with mock.patch("legacy_documenter.llm.registry.ProviderRegistry.create") as provider, \
                mock.patch("legacy_documenter.cli.full_pipeline.run_full_pipeline", side_effect=AssertionError("analysis rerun")) as pipeline:
            K.build_package(self.baseline, out, project="Web", solution="SampleLegacy")
            self.assertEqual((provider.call_count, pipeline.call_count), (0, 0))
        guide = (out / "human" / "guide" / "index.html").read_text(encoding="utf-8")
        self.assertIsNone(NOISE.search(guide))
        k = json.loads((out / "ai" / "knowledge.json").read_text(encoding="utf-8"))
        self.assertTrue(any(v.get("traceability", {}).get("source_refs") for v in k["views"]))
        self.assertTrue((out / "internal" / "behavioral" / "validation_report.json").is_file())


if __name__ == "__main__":
    unittest.main()
