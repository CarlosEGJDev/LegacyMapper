"""Owner acceptance remediation R2 (BD-1): provider truth-state prefixes never reach the human product.

Offline stubs only: real provider calls = 0, scanner/analyzer = 0. Realistic provider output ("CONFIRMED: ...", mixed claims,
dash separators) is injected through the scripted stub; the persisted-record case rewrites accepted records the way the real
acceptance run stored them.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))

from system_fixtures import build_baseline  # noqa: E402
from test_owner_acc01_full_system_ai import POLICY, Scripted, Work  # noqa: E402

from legacy_documenter.system.models import (CLAIM_STATUSES, HUMAN_STATUS_VALUES, KINDS, Fact, normalize_claim_text,  # noqa: E402
                                              normalize_record_semantic, validate_semantic)
from legacy_documenter.system.orchestrator import RunOptions, run_system_interpretation  # noqa: E402
from legacy_documenter.system.product import project_system  # noqa: E402
from legacy_documenter.system.store import RequestStore  # noqa: E402

ENGLISH_STATE = re.compile(r"\b(CONFIRMED|INFERRED|UNRESOLVED)\b")


def _visible(page: Path) -> str:
    import html
    return html.unescape(re.sub(r"<[^>]+>", " ", page.read_text(encoding="utf-8")))


def prefixing(style: str = "colon"):
    """Provider mutation: every claim text starts with its own English state marker (as the real provider wrote them)."""
    sep = {"colon": ": ", "dash": " — "}[style]

    def mutate(kind, parsed, facts):
        return {sec: [{**c, "text": f"{c['status']}{sep}{c['text']}"} for c in claims] for sec, claims in parsed.items()}
    return mutate


class NormalizationUnitTests(unittest.TestCase):
    def test_leading_marker_is_removed_and_state_is_not_part_of_prose(self):
        self.assertEqual(normalize_claim_text("CONFIRMED: The project calls X."), "The project calls X.")
        self.assertEqual(normalize_claim_text("INFERRED: algo"), "algo")
        self.assertEqual(normalize_claim_text("UNRESOLVED: No se puede determinar."), "No se puede determinar.")
        self.assertEqual(normalize_claim_text("  **CONFIRMED**: negrita"), "negrita")
        self.assertEqual(normalize_claim_text("CONFIRMED — Desde A se invoca B."), "Desde A se invoca B.")
        self.assertEqual(normalize_claim_text("INFERRED - guion"), "guion")

    def test_mixed_claims_keep_the_distinction_in_the_human_vocabulary(self):
        out = normalize_claim_text("CONFIRMED: A invoca B. INFERRED: permite solicitar esa operacion.")
        self.assertEqual(out, "A invoca B. Inferido: permite solicitar esa operacion.")
        self.assertEqual(normalize_claim_text("CONFIRMED: hecho; UNRESOLVED: causa"), "hecho; No resuelto: causa")

    def test_a_state_word_in_prose_is_translated_never_deleted(self):
        self.assertEqual(normalize_claim_text("esa atribucion es INFERRED, no esta confirmada"), "esa atribucion es Inferido, no esta confirmada")
        self.assertEqual(normalize_claim_text("CONFIRMED no; INFERRED: x"), "Confirmado no; Inferido: x")

    def test_unrelated_text_is_not_touched(self):
        for text in ("El componente UNCONFIRMEDX y preconfirmed no cambian.", "Confirmado: ya esta en vocabulario humano.",
                     "inferred en minuscula no es un marcador", "Texto normal sin marcadores."):
            self.assertEqual(normalize_claim_text(text), text)

    def test_normalization_is_idempotent_and_total(self):
        for text in ("CONFIRMED: a. INFERRED: b. y es UNRESOLVED.", "CONFIRMED:", "", "x"):
            once = normalize_claim_text(text)
            self.assertEqual(normalize_claim_text(once), once)
        self.assertEqual(normalize_claim_text(None), None)


class ValidationBoundaryTests(unittest.TestCase):
    FACTS = [Fact("F01", "name", "confirmed", "Nombre del proyecto: X."), Fact("F02", "flow", "confirmed", "Una vista abre un manejador."),
             Fact("F03", "flow", "inferred", "Un clic alcanza un procedimiento.")]

    def _parsed(self, kind, texts):
        from legacy_documenter.system.models import SECTIONS
        sections = SECTIONS[kind]
        statuses = ["CONFIRMED", "INFERRED", "UNRESOLVED"]
        parsed = {s: [] for s in sections}
        for i, (text, st) in enumerate(zip(texts, statuses)):
            refs = ["F02"] if st == "CONFIRMED" else ["F03"] if st == "INFERRED" else []
            parsed[sections[i % len(sections)]].append({"text": text, "status": st, "refs": refs, "subject": ""})
        return parsed

    def test_every_level_keeps_status_refs_and_claim_identity_while_prose_is_clean(self):
        for kind in KINDS:
            raw = ["CONFIRMED: Hecho uno.", "INFERRED: Deduccion dos.", "UNRESOLVED: No se determina tres."]
            v = validate_semantic(kind, self._parsed(kind, raw), self.FACTS, "SYS-x")
            claims = [c for cs in v.accepted.values() for c in cs]
            self.assertEqual(len(claims), 3, kind)
            self.assertEqual(sorted(c["status"] for c in claims), ["CONFIRMED", "INFERRED", "UNRESOLVED"], kind)
            for c in claims:
                self.assertFalse(ENGLISH_STATE.search(c["text"]), (kind, c["text"]))
            # claim ids are derived from the provider's raw text, so they match what the real acceptance run persisted
            plain = validate_semantic(kind, self._parsed(kind, [t.split(": ", 1)[1] for t in raw]), self.FACTS, "SYS-x")
            self.assertEqual([c["text"] for cs in plain.accepted.values() for c in cs], [c["text"] for cs in v.accepted.values() for c in cs])
            self.assertEqual(sum(len(cs) for cs in v.accepted.values()), plain.accepted_count)

    def test_state_is_neither_promoted_nor_demoted_by_the_prefix(self):
        parsed = self._parsed("PROJECT", ["CONFIRMED: dice confirmado pero solo respalda lo inferido.", "INFERRED: x", "UNRESOLVED: y"])
        parsed["purpose"][0]["refs"] = ["F03"]                       # only an inferred fact supports it
        v = validate_semantic("PROJECT", parsed, self.FACTS, "SYS-x")
        first = v.accepted["purpose"][0]
        self.assertEqual(first["status"], "INFERRED")                # downgraded by the validator, not by text
        self.assertEqual(v.downgraded, 1)

    def test_a_claim_that_is_only_a_marker_is_rejected(self):
        parsed = self._parsed("PROJECT", ["CONFIRMED:", "INFERRED: ok", "UNRESOLVED: ok"])
        v = validate_semantic("PROJECT", parsed, self.FACTS, "SYS-x")
        self.assertIn("EMPTY_TEXT", {r["reason"] for r in v.rejected})

    def test_record_normalization_copies_and_never_mutates_the_persisted_record(self):
        record = {"semantic": {"purpose": [{"claim_id": "CL-1", "text": "CONFIRMED: hola", "status": "CONFIRMED", "refs": ["F01"], "subject": ""}]}, "identity": "SYS-1"}
        out = normalize_record_semantic(record)
        self.assertEqual(record["semantic"]["purpose"][0]["text"], "CONFIRMED: hola")
        self.assertEqual(out["semantic"]["purpose"][0]["text"], "hola")
        self.assertEqual({k: v for k, v in out["semantic"]["purpose"][0].items() if k != "text"},
                         {k: v for k, v in record["semantic"]["purpose"][0].items() if k != "text"})


class EndToEndTests(Work):
    def _assert_clean_product(self, doc, out):
        v = doc["validation"]
        self.assertEqual(v["defects"], 0, v["details"])
        self.assertEqual(v["invalid_human_states"], 0)
        for page in (out / "human").rglob("*.html"):
            self.assertIsNone(ENGLISH_STATE.search(_visible(page)), page.name)
            visible = _visible(page)
            self.assertNotRegex(visible, r"Confirmado\s*[—:-]?\s*Confirmado")        # no double state label

    def test_prefixed_provider_output_projects_clean_human_pages_for_every_level(self):
        for style in ("colon", "dash"):
            with self.subTest(style=style):
                state = self.tmp / f"state_{style}"
                out = self.tmp / f"out_{style}"
                r = self.run_sys(Scripted(mutate=prefixing(style)), state=state)
                self.assertEqual(r.status, "COMPLETE")
                doc = project_system(self.baseline, state, out)
                self._assert_clean_product(doc, out)
                human_text = " ".join(_visible(p) for p in (out / "human").rglob("*.html"))
                for label in HUMAN_STATUS_VALUES:
                    self.assertIn(label, human_text)
                knowledge = json.loads((out / "ai" / "knowledge.json").read_text(encoding="utf-8"))
                self.assertGreater(knowledge["claim_count"], 0)

    def test_machine_claims_keep_state_and_provenance_and_carry_no_prefix(self):
        state = self.tmp / "s"
        self.run_sys(Scripted(mutate=prefixing()), state=state)
        out = self.tmp / "o"
        project_system(self.baseline, state, out)
        for name in ("projects", "solutions", "system", "views", "flows", "data"):
            entities = json.loads((out / "ai" / f"{name}.json").read_text(encoding="utf-8"))
            entities = entities if isinstance(entities, list) else entities.get(name) or entities.get("entities") or [entities]
            for entity in entities:
                for claims in (entity.get("semantic") or {}).values():
                    for c in claims:
                        self.assertIn(c["status"], CLAIM_STATUSES)
                        self.assertIsNone(re.match(r"\s*(CONFIRMED|INFERRED|UNRESOLVED)\b", c["text"]), c["text"])
                        self.assertTrue(c["claim_id"].startswith("CL-"))
                        if c["status"] != "UNRESOLVED":
                            self.assertTrue(c["fact_ids"], "supported claims keep their fact provenance")

    def test_previously_persisted_prefixed_records_replay_with_zero_calls_and_project_clean(self):
        """The real acceptance run stored prefixed prose (and parent identities derived from it). Those accepted records must stay
        reusable with 0 provider calls and project clean. The legacy behaviour is reproduced by disabling normalization while storing."""
        with mock.patch("legacy_documenter.system.models.normalize_claim_text", lambda text: text.strip()):
            self.run_sys(Scripted(mutate=prefixing()))
        store = RequestStore(self.state)
        stored = list(store.iter_accepted())
        self.assertTrue(any(c["text"].startswith(("CONFIRMED:", "INFERRED:", "UNRESOLVED:")) for r in stored for cs in r["semantic"].values() for c in cs))
        raw_before = {p: p.read_bytes() for p in (self.state / "requests").rglob("*.json")}
        again = Scripted()
        r = self.run_sys(again)
        self.assertEqual((r.metrics.requests, again.seen), (0, []), "identity must not depend on presentation")
        self.assertEqual(r.metrics.replays, len(stored))
        doc = project_system(self.baseline, self.state, self.out)
        self._assert_clean_product(doc, self.out)
        self.assertEqual({p: p.read_bytes() for p in raw_before}, raw_before, "persisted accepted records are never rewritten")
        self.assertEqual(doc["counts"], r.state["counts"])

    def test_mixed_claim_survives_with_human_vocabulary_and_unchanged_status(self):
        def mutate(kind, parsed, facts):
            parsed = {s: list(v) for s, v in parsed.items()}
            for sec, claims in parsed.items():
                if claims and claims[0]["status"] == "INFERRED":
                    claims[0] = {**claims[0], "text": "CONFIRMED: A invoca B. INFERRED: permite solicitar la operacion."}
            return parsed
        state = self.tmp / "sm"
        self.run_sys(Scripted(mutate=mutate), state=state)
        out = self.tmp / "om"
        doc = project_system(self.baseline, state, out)
        self.assertEqual(doc["validation"]["defects"], 0, doc["validation"]["details"])
        text = " ".join(_visible(p) for p in (out / "human").rglob("*.html"))
        self.assertIn("A invoca B. Inferido: permite solicitar la operacion.", text)


class CoverageDriftAndSubjectTests(Work):
    def test_project_with_only_unresolved_claims_is_machine_only_for_a_stated_reason_and_keeps_its_page(self):
        """R2 coverage drift (WebAmbiente): an all-UNRESOLVED answer is a legitimate AI result, not a product bug."""
        target = {"name": None}

        def mutate(kind, parsed, facts):
            if kind == "PROJECT" and target["name"] is None:
                target["name"] = True
                return {sec: [{**c, "status": "UNRESOLVED", "refs": []} for c in claims] for sec, claims in parsed.items()}
            return parsed
        state = self.tmp / "sd"
        r = self.run_sys(Scripted(mutate=mutate), state=state)
        self.assertEqual(r.state["counts"].get("MACHINE_ONLY_DOCUMENTED", 0) >= 1, True)
        coverage = json.loads((state / "FULL_SYSTEM_COVERAGE.json").read_text(encoding="utf-8"))
        machine_only = [p for p in coverage["projects"] if p["state"] == "MACHINE_ONLY_DOCUMENTED" and p["reason"] == "NO_CONFIRMED_OR_INFERRED_CLAIMS"]
        self.assertTrue(machine_only)
        self.assertEqual(coverage["counts"]["PENDING_INTERPRETATION"], 0)
        out = self.tmp / "od"
        doc = project_system(self.baseline, state, out)
        self.assertEqual(doc["validation"]["silent_project_omissions"], 0)
        self.assertEqual(doc["validation"]["defects"], 0, doc["validation"]["details"])

    def test_claims_without_subject_render_without_a_dangling_separator(self):
        def mutate(kind, parsed, facts):
            return {sec: [{k: v for k, v in c.items() if k != "subject"} for c in claims] for sec, claims in parsed.items()}
        state = self.tmp / "ss"
        self.run_sys(Scripted(mutate=mutate), state=state)
        out = self.tmp / "os"
        doc = project_system(self.baseline, state, out)
        self.assertEqual(doc["validation"]["defects"], 0, doc["validation"]["details"])
        for page in (out / "human").rglob("*.html"):
            visible = _visible(page)
            self.assertNotIn("None", visible)
            self.assertNotRegex(visible, r"(Confirmado|Inferido|No resuelto)\s*:\s*[A-ZÁÉÍÓÚ]?\s*—")
        projects = json.loads((out / "ai" / "projects.json").read_text(encoding="utf-8"))
        projects = projects if isinstance(projects, list) else projects.get("projects", [])
        subjects = [c["subject"] for e in projects for cl in (e.get("semantic") or {}).values() for c in cl]
        self.assertTrue(subjects)
        self.assertEqual(set(subjects), {""})


if __name__ == "__main__":
    unittest.main()
