"""Post-V5 H4-R5: AI behavioral interpretation over a bounded context + observable-usage classification.

Providers here are test doubles only; the real provider run is an explicit, separate step (never part of the suite).
"""
from __future__ import annotations

import copy
import json
import unittest
from types import SimpleNamespace

from legacy_documenter.behavior import ai as A
from legacy_documenter.behavior import render as R
from legacy_documenter.behavior import usage as U
from legacy_documenter.behavior import validate as V
from legacy_documenter.behavior.model import AI_INTERPRETATION, CONFIRMED, ViewInvocation
from legacy_documenter.behavior.prototype import run_ai
from legacy_documenter.llm.contracts import LLMCapabilities, LLMModelInfo, LLMProvider, LLMResponse, Usage
from tests.test_post_v5_h4_r4_behavioral import BehaviorBase


class ScriptedProvider(LLMProvider):
    """Returns the scripted JSON object for each request (test double; never a real provider)."""

    def __init__(self, answers: list[dict | None]) -> None:
        self.answers = list(answers)
        self.requests = []

    def capabilities(self):
        return LLMCapabilities(context_window=100000, max_output_tokens=4000, structured_output=True, json_mode=True)

    def model_info(self):
        return LLMModelInfo("scripted", "scripted-1", "scripted", "TEST", self.capabilities())

    def generate(self, request):
        return self.structured_generate(request, request.output_contract or {})

    def structured_generate(self, request, schema):
        self.requests.append(request)
        out = self.answers.pop(0) if self.answers else None
        status = "SUCCESS" if out is not None else "INVALID_STRUCTURED_OUTPUT"
        return LLMResponse(request.request_id, f"RESP-{len(self.requests)}", "scripted", "scripted-1", status, content=json.dumps(out) if out else "",
                           usage=Usage(output_tokens=10), parsed_output=out, schema_validation_status="VALID_STRUCTURED_OUTPUT" if out else "INVALID_STRUCTURED_OUTPUT")


def item(text, refs=(), basis="lectura del contexto", entities=()):
    return {"text": text, "source_refs": list(refs), "reasoning_basis": basis, "entities": [dict(e) for e in entities]}


def inv(file="Web\\CustomerPage.aspx.vb", line=10, exists=True):
    return ViewInvocation(source_view=file[:-3], target_view="Web\\PickCustomer.ascx", mechanism="window_open", parameters=["selrow"], file=file, line=line,
                          target_exists=exists, source_refs=[f"src:{file}:{line}"])


class UsageClassificationTests(unittest.TestCase):
    def view(self, *invs, name="PickCustomer"):
        return SimpleNamespace(name=name, reached_by=list(invs))

    def test_active_requires_a_confirmed_incoming_invocation(self):
        res = U.classify(self.view(inv()), shell_evidence=3, name_references=0, behavior=True)
        self.assertEqual(res["status"], U.ACTIVE)
        self.assertEqual(res["ladder"], U.OBSERVABLY_USED)
        self.assertEqual(res["reasons"][0].status, CONFIRMED)
        self.assertTrue(res["reasons"][0].source_refs)
        for no_incoming in (self.view(), self.view(inv(exists=False)), self.view(inv(file="proyectos\\Backup\\X.ascx.vb"))):
            self.assertNotEqual(U.classify(no_incoming, shell_evidence=3, name_references=0, behavior=True)["status"], U.ACTIVE)

    def test_backup_copies_are_reported_but_never_counted_as_use(self):
        res = U.classify(self.view(inv(file="proyectos\\Backup\\X.ascx.vb")), shell_evidence=3, name_references=0, behavior=True)
        self.assertEqual(res["counts"]["incoming_from_backups"], 1)
        self.assertTrue(any("respaldo" in r.text for r in res["reasons"]))

    def test_shell_dynamic_loading_gives_unresolved_usage(self):
        res = U.classify(self.view(), shell_evidence=5, name_references=0, behavior=True)
        self.assertEqual(res["status"], U.UNRESOLVED_USAGE)
        self.assertIn("dinámicamente desde el shell", res["wording"])

    def test_isolated_does_not_become_obsolete(self):
        res = U.classify(self.view(), shell_evidence=0, name_references=0, behavior=False)
        self.assertEqual(res["status"], U.ISOLATED)
        self.assertIn("No se encontró evidencia observable de uso en el alcance analizado", res["wording"])
        text = " ".join([res["wording"]] + [r.text for r in res["reasons"]])
        self.assertIsNone(U.FORBIDDEN_WORDS.search(text.replace("no significa que esté obsoleta", "").replace("obsolescencia", "")))

    def test_legacy_candidate_needs_all_indicators_and_stays_cautious(self):
        copyish = SimpleNamespace(name="ucMantenedor2", reached_by=[])
        res = U.classify(copyish, shell_evidence=5, name_references=0, behavior=False)
        self.assertEqual(res["status"], U.LEGACY)
        self.assertIn("no es una conclusión", res["label"])
        self.assertIn("solo una candidata", res["wording"])
        for kwargs in ({"name_references": 2, "behavior": False}, {"name_references": 0, "behavior": True}):
            self.assertNotEqual(U.classify(copyish, shell_evidence=5, **kwargs)["status"], U.LEGACY)
        plain_name = SimpleNamespace(name="ucMantenedor", reached_by=[])
        self.assertNotEqual(U.classify(plain_name, shell_evidence=5, name_references=0, behavior=False)["status"], U.LEGACY)

    def test_possibly_active_needs_behavior_and_an_indirect_reference(self):
        res = U.classify(self.view(), shell_evidence=5, name_references=3, behavior=True)
        self.assertEqual((res["status"], res["ladder"]), (U.POSSIBLE, U.REACHABLE))

    def test_no_state_ever_says_unused_dead_or_obsolete(self):
        for kwargs in ({"shell_evidence": 0}, {"shell_evidence": 4}, {"shell_evidence": 4, "behavior": True}):
            base = {"name_references": 0, "behavior": False, **kwargs}
            res = U.classify(self.view(), **base)
            self.assertIsNone(U.FORBIDDEN_WORDS.search(res["wording"]))
        self.assertEqual(set(U.USAGE_STATES), {"ACTIVE_OBSERVABLE", "POSSIBLY_ACTIVE", "ISOLATED", "LEGACY_CANDIDATE", "UNRESOLVED_USAGE"})


class AiBehavioralTests(BehaviorBase):
    def setUp(self):
        self.refs = V.ReferenceIndex(self.bc)
        self.project = {"solution": "SampleLegacy", "project": "Web", "path": self.bc.project_path, "refs": []}
        self.view_obj = copy.deepcopy(self.view("CustomerPage"))
        self.ctx, self.scope = A.view_context(self.bc, self.view_obj, self.project)

    def good_answer(self):
        ep = next(f for f in self.ctx["facts"] if f["kind"] == "event")
        save = next(a for a in self.view_obj.actions if a.handler.lower() == "btnsave_click")
        return {
            "view_id": self.view_obj.view,
            "simple_summary": item("Esta pantalla permite guardar un cliente y notificar.", [ep["ref"]], entities=[{"type": "view", "name": self.view_obj.name}]),
            "observable_purpose": item("Al pulsar «btnSave» se ejecuta «btnSave_Click».", [ep["ref"]],
                                       entities=[{"type": "control", "name": "btnSave"}, {"type": "method", "name": "btnSave_Click"}]),
            "usage_status": "ACTIVE_OBSERVABLE",
            "usage_reasoning": item("No hay invocaciones entrantes observadas; el uso permanece sin resolver.", []),
            "inputs": [], "main_actions": [{"action_key": save.handler, "explanation": item("Guardar pasa por la clase de negocio.", [ep["ref"]])}],
            "data_behavior": item("Los datos pasan al repositorio.", []),
            "known": [], "inferred": [], "unresolved": [item("El propósito de negocio no está resuelto.")],
        }

    def test_context_is_bounded_and_every_fact_carries_a_resolvable_ref(self):
        self.assertLess(len(json.dumps(self.ctx, ensure_ascii=False)), 40000)
        self.assertTrue(self.ctx["facts"])
        for fact in self.ctx["facts"]:
            self.assertIn(fact["ref"], self.scope["allowed_refs"])
            self.assertTrue(self.refs.ref_ok(fact["ref"]), fact)
        self.assertEqual({c["id"] for c in self.ctx["controls"]}, {"btnSave", "btnNotify"})
        self.assertEqual(self.ctx["usage"]["deterministic_status"], self.view_obj.usage["status"])

    def test_schema_requires_the_behavioral_fields(self):
        for key in ("view_id", "simple_summary", "observable_purpose", "usage_reasoning", "main_actions", "data_behavior"):
            self.assertIn(key, A.VIEW_SCHEMA["required"])
        for key in ("inputs", "related_classes", "messages_popups", "known", "inferred", "unresolved", "usage_status"):
            self.assertIn(key, A.VIEW_SCHEMA["properties"])
        self.assertEqual(set(A.ENTITY_TYPES) >= {"control", "event", "method", "class", "procedure", "view"}, True)

    def test_valid_narrative_is_kept_and_always_ai_interpretation(self):
        answer = self.good_answer()
        answer["simple_summary"]["status"] = "CONFIRMED"           # the model cannot self-promote
        vs = A.merge_view(self.view_obj, answer, self.scope, self.refs)
        self.assertEqual([v for v in vs if v.action == "rejected"], [])
        sections = self.view_obj.ai_narrative
        self.assertEqual(set(sections), {"simple_summary", "observable_purpose", "usage_reasoning", "data_behavior", "unresolved"})
        for claims in list(sections.values()) + list(self.view_obj.ai_action_notes.values()):
            for c in claims:
                self.assertEqual((c.status, c.origin), (AI_INTERPRETATION, "ai"))
        self.assertIn("AI_USAGE_STATUS_OVERRIDDEN", {v.code for v in vs})   # deterministic usage wins
        self.assertEqual(self.view_obj.usage["status"], "UNRESOLVED_USAGE")

    def test_fabricated_symbols_procedures_refs_and_obsolescence_are_rejected_but_the_rest_survives(self):
        answer = self.good_answer()
        ep = next(f for f in self.ctx["facts"] if f["kind"] == "event")["ref"]
        answer["inputs"] = [
            item("Usa «btnFantasma» para pagar.", [ep]),                                           # unknown symbol
            item("Llama a un procedimiento.", [ep], entities=[{"type": "procedure", "name": "PKG.NO_EXISTE"}]),   # fabricated procedure
            item("Según el flujo.", ["FLOW-0000000000"]),                                          # ref not offered
            item("Esta vista está obsoleta.", [ep]),                                               # obsolescence claim
            item("Muestra el campo «btnSave».", [ep], entities=[{"type": "control", "name": "btnSave"}]),   # valid
        ]
        answer["main_actions"].append({"action_key": "btnInventado_Click", "explanation": item("Hace algo.", [ep])})
        vs = A.merge_view(self.view_obj, answer, self.scope, self.refs)
        codes = [v.code for v in vs if v.action == "rejected"]
        self.assertEqual(sorted(codes), ["AI_OBSOLESCENCE_CLAIM", "AI_REF_NOT_PROVIDED", "AI_UNKNOWN_ENTITY", "AI_UNKNOWN_ENTITY", "AI_UNKNOWN_SYMBOL"])
        self.assertEqual([c.text for c in self.view_obj.ai_narrative["inputs"]], ["Muestra el campo «btnSave»."])
        self.assertIn("simple_summary", self.view_obj.ai_narrative)                                # the safe part is preserved

    def test_references_to_the_wireframe_must_exist_in_the_evidence(self):
        answer = self.good_answer()
        answer["inputs"] = [item("El control «txtCustomerId» recibe el código.", entities=[{"type": "control", "name": "txtCustomerId"}])]
        vs = A.merge_view(self.view_obj, answer, self.scope, self.refs)
        self.assertNotIn("inputs", self.view_obj.ai_narrative)
        self.assertTrue(any(v.code in ("AI_UNKNOWN_ENTITY", "AI_UNKNOWN_SYMBOL") for v in vs))

    def test_unusable_provider_output_records_a_validation_issue_and_adds_nothing(self):
        vs = A.merge_view(self.view_obj, None, self.scope, self.refs)
        self.assertEqual([v.code for v in vs], ["AI_NO_USABLE_OUTPUT"])
        self.assertEqual(self.view_obj.ai_narrative, {})

    def test_run_ai_records_provider_requests_validation_and_never_templates_in_place_of_ai(self):
        explained = copy.deepcopy(self.explained)
        page = next(p for p, v in explained.items() if v.name == "CustomerPage")
        pick = next(p for p, v in explained.items() if v.name == "PickCustomer")
        ctx, _ = A.view_context(self.bc, explained[page], self.project)
        ep = next(f for f in ctx["facts"] if f["kind"] == "event")["ref"]
        ans_page = self.good_answer()
        ans_page["view_id"] = explained[page].view
        provider = ScriptedProvider([ans_page, None, {"project_summary": item("Proyecto web de la solución.", []), "role_in_solution": item("Presentación.", []),
                                                      "how_it_is_used": item("Se abre por nombre.", []), "unresolved": []}])
        violations: list = []
        manifest = run_ai(provider, self.bc, self.refs, explained, [page, pick], copy.deepcopy(self.doc.project), self.doc.module, self.doc.measurements,
                          {"by_status": {}}, violations, self.project, "SNAP-TEST")
        self.assertEqual((manifest["provider_id"], manifest["model_id"], manifest["request_count"], manifest["successful_requests"]), ("scripted", "scripted-1", 3, 2))
        self.assertEqual(manifest["status"], "COMPLETED")
        by_view = {r["view"]: r for r in manifest["validation"]}
        self.assertTrue(by_view["CustomerPage"]["got_output"] and by_view["CustomerPage"]["accepted_claims"] > 0)
        self.assertFalse(by_view["PickCustomer"]["got_output"])                       # no AI output: nothing is invented in its place
        self.assertEqual(explained[pick].ai_narrative, {})
        self.assertTrue(all(r["input_chars"] > 0 and "output_chars" in r for r in manifest["requests"]))
        self.assertTrue(any(v.code == "AI_NO_USABLE_OUTPUT" for v in violations))
        for req in provider.requests[:2]:
            self.assertEqual(req.purpose, "FUNCTIONAL_INTERPRETATION")
            self.assertLess(len(json.dumps(req.context)), 40000)
        del ep


class AiRenderingTests(BehaviorBase):
    def doc_with_ai(self):
        doc = copy.deepcopy(self.doc)
        view = doc.views[0]
        view.ai_narrative = {"simple_summary": [R.Claim("Esta pantalla permite trabajar con clientes.", AI_INTERPRETATION, [], "basis", "ai")],
                             "observable_purpose": [R.Claim("Al abrirse prepara los campos y al guardar los envía al servicio.", AI_INTERPRETATION, [], "basis", "ai")]}
        doc.ai_manifest = {"status": "COMPLETED", "provider_id": "scripted", "model_id": "scripted-1", "request_count": 1, "successful_requests": 1}
        return doc

    def test_ai_text_uses_a_compact_marker_and_precedes_technical_names(self):
        html = R.html_document(R.compose(self.doc_with_ai())[0], "t")
        self.assertIn('class="callout callout-ai" data-status="AI_INTERPRETATION"', html)     # the status stays in the markup
        self.assertNotIn('<p class="callout-title">IA</p>', html)                               # no repeated badge
        self.assertEqual(html.count("Interpretación de IA — no aprobada"), 0)                  # no repeated long label
        self.assertEqual(html.count("Interpretación asistida por IA"), 1)                      # the notice appears once
        start = html.index("En una frase")
        chapter = html[start:html.index("Apéndice", start)]
        self.assertLess(chapter.index("Esta pantalla permite trabajar con clientes."), chapter.index("Vistas y ventanas relacionadas"))
        self.assertLess(chapter.index("Qué hace y cómo se usa"), chapter.index("Acciones principales"))

    def test_deterministic_rendering_from_the_validated_explanation(self):
        a = R.html_document(R.compose(self.doc_with_ai())[0], "t")
        b = R.html_document(R.compose(self.doc_with_ai())[0], "t")
        self.assertEqual(a, b)

    def test_without_ai_the_document_says_so_and_does_not_fake_narrative(self):
        html = R.html_document(R.compose(self.doc)[0], "t")
        self.assertIn("No hay interpretación de IA para esta vista", html)
        self.assertNotIn('class="callout callout-ai"', html)
        self.assertIn("no incluye interpretaciones de IA", html)

    def test_usage_section_distinguishes_existence_use_and_unresolved(self):
        html = R.html_document(R.compose(self.doc)[0], "t")
        self.assertIn("Existir en el código no implica uso en producción", html)
        self.assertIn("la ausencia de indicios de uso no se interpreta como obsolescencia", html)
        self.assertNotRegex(html.lower(), r"esta vista no se usa|código muerto|\bobsoleta\b es")


if __name__ == "__main__":
    unittest.main()
