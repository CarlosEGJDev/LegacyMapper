"""Post-V5 H4 final knowledge productization: human/ai/internal package, human-confirmed domain knowledge, AI prompt contract.

Automated tests never use a real provider (scripted doubles only) and never scan or analyze: the package is projected from a persisted baseline.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from legacy_documenter.behavior import ai as A
from legacy_documenter.behavior import render as R
from legacy_documenter.behavior.prototype import build
from legacy_documenter.product import domain
from legacy_documenter.product import package as K
from tests.test_post_v5_h4_r4_behavioral import BehaviorBase
from tests.test_post_v5_h4_r5_behavioral_ai import ScriptedProvider

TERMS = {"terms": [{"term": "Customer", "meaning": "Significado confirmado por una persona", "status": "CANONICAL", "source": "human"}]}


class DomainKnowledgeTests(unittest.TestCase):
    def write(self, data) -> Path:
        d = Path(tempfile.mkdtemp(prefix="dk_"))
        self.addCleanup(shutil.rmtree, d, True)
        p = d / "terms.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        return p

    def test_valid_terms_load_with_explicit_human_origin(self):
        terms = domain.load(self.write(TERMS))
        self.assertEqual(terms, [{"term": "Customer", "meaning": "Significado confirmado por una persona", "status": "CANONICAL", "source": "human", "origin": "HUMAN_CONFIRMED"}])
        self.assertEqual(domain.load(None), [])

    def test_only_explicit_human_canonical_terms_are_accepted(self):
        bad = [{"terms": [{"term": "COB", "meaning": "Cobranza", "status": "INFERRED", "source": "human"}]},
               {"terms": [{"term": "COB", "meaning": "Cobranza", "status": "CANONICAL", "source": "ai"}]},
               {"terms": [{"term": "COB", "meaning": "", "status": "CANONICAL", "source": "human"}]},
               {"terms": [TERMS["terms"][0], TERMS["terms"][0]]}, {"nothing": []}]
        for data in bad:
            with self.assertRaises(domain.DomainKnowledgeError):
                domain.load(self.write(data))

    def test_nothing_is_prepopulated(self):
        self.assertEqual(domain.load(None), [])
        body = Path(domain.__file__).read_text(encoding="utf-8").split('"""')[2]       # code after the module docstring
        for word in ("Cobranza", "Morosidad", "Mantencion", "WebCob"):
            self.assertNotIn(word, body)


class KnowledgePackageTests(BehaviorBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.terms_file = cls.tmp / "terms.json"
        cls.terms_file.write_text(json.dumps(TERMS), encoding="utf-8")
        cls.out = cls.tmp / "package"
        with mock.patch("legacy_documenter.llm.registry.ProviderRegistry.create") as provider, \
                mock.patch("legacy_documenter.cli.full_pipeline.run_full_pipeline", side_effect=AssertionError("analysis rerun")) as pipeline:
            cls.manifest = K.build_package(cls.baseline, cls.out, project="Web", solution="SampleLegacy", domain_knowledge=cls.terms_file)
            cls.provider_calls, cls.pipeline_calls = provider.call_count, pipeline.call_count

    def read(self, rel):
        return json.loads((self.out / rel).read_text(encoding="utf-8"))

    def test_final_structure_is_human_ai_internal_with_one_entry_point(self):
        top = {p.name for p in self.out.iterdir()}
        self.assertEqual(top, {"human", "ai", "internal", "KNOWLEDGE_PACKAGE.json"})
        self.assertTrue((self.out / "human" / "index.html").is_file())
        for pdf in ("LegacyMapper.pdf", "executive.pdf"):
            self.assertTrue((self.out / "human" / pdf).read_bytes().startswith(b"%PDF"))
        self.assertTrue((self.out / "human" / "executive" / "index.html").is_file())
        landing = (self.out / "human" / "index.html").read_text(encoding="utf-8")
        for target in ("guide/index.html", "LegacyMapper.pdf", "executive/index.html", "executive.pdf", "diagrams/index.html"):
            self.assertIn(f'href="{target}"', landing)
        for legacy in ("human_default", "human_executive", "docs", "visuals", "behavioral", "package"):
            self.assertFalse((self.out / legacy).exists(), legacy)

    def test_manifest_points_to_existing_entry_points_and_hashes_files(self):
        m = self.read("KNOWLEDGE_PACKAGE.json")
        for key in ("human_entry_point", "ai_entry_point"):
            self.assertTrue((self.out / m[key]).is_file(), key)
        self.assertTrue((self.out / m["internal_artifacts_path"]).is_dir())
        self.assertEqual(m["source"]["solution"], "SampleLegacy")
        self.assertIn("evidence_fingerprint", m)
        self.assertNotIn("generated_at", json.dumps(m))
        for rel, digest in m["files"].items():
            import hashlib
            self.assertEqual(hashlib.sha256((self.out / rel).read_bytes()).hexdigest(), digest, rel)

    def test_internal_artifacts_are_separated_from_the_public_products(self):
        internal = {p.name for p in (self.out / "internal" / "behavioral").iterdir()}
        for name in ("explanations.json", "validation_report.json", "AI_INTERPRETATION_MANIFEST.json", "ui_navigation_evidence.json"):
            self.assertIn(name, internal)
            self.assertFalse((self.out / "human" / name).exists())
            self.assertFalse((self.out / "ai" / name).exists())
        self.assertTrue((self.out / "internal" / "baseline_reference.json").is_file())

    def test_ai_knowledge_is_one_model_plus_projections(self):
        k = self.read("ai/knowledge.json")
        self.assertEqual(k["contract"], "LegacyMapperAiKnowledge")
        for name in k["projections"].values():
            self.assertTrue((self.out / "ai" / name).is_file(), name)
        ids = {v["id"] for v in k["views"]}
        self.assertTrue({v["id"] for v in self.read("ai/views.json")["views"]} <= ids)
        flows = self.read("ai/flows.json")["flows"]
        self.assertTrue(flows and all(f["view"] in ids for f in flows))
        for f in flows:                                        # every route ends at data or at an explicit, unresolved boundary
            self.assertTrue(f["boundary"] is None or f["boundary"]["status"] == "UNRESOLVED")
        self.assertIn("UNRESOLVED", json.dumps(self.read("ai/unresolved.json")))

    def test_human_and_ai_projections_share_the_same_truth(self):
        k = self.read("ai/knowledge.json")
        guide = (self.out / "human" / "guide" / "index.html").read_text(encoding="utf-8").replace("<wbr>", "")
        catalog_names = {r["name"] for r in self.doc.catalog}
        self.assertEqual({v["name"] for v in k["views"]}, catalog_names)
        flows = self.read("ai/flows.json")["flows"]
        for v in self.doc.views:
            for a in v.actions:
                self.assertIn(R.route_text(a).split(" → ")[-1].replace("&", "&amp;"), guide)
                self.assertTrue(any(f["handler"] == a.handler and f["view"].endswith("/" + v.name) for f in flows))

    def test_human_confirmed_knowledge_is_distinct_from_evidence(self):
        k = self.read("ai/knowledge.json")
        self.assertEqual(k["domain_knowledge"]["origin"], "HUMAN_CONFIRMED")
        self.assertEqual([t["term"] for t in k["domain_knowledge"]["terms"]], ["Customer"])
        self.assertNotIn("Significado confirmado", json.dumps(k["views"]))           # never mixed into evidence-derived claims
        guide = (self.out / "human" / "guide" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Terminología confirmada por una persona", guide)
        self.assertIn("no provienen del código", guide)
        self.assertEqual(self.read("KNOWLEDGE_PACKAGE.json")["human_confirmed_domain_knowledge"]["terms"], ["Customer"])
        self.assertIn("HUMAN_CONFIRMED", json.dumps(self.read("ai/provenance.json")))

    def test_no_provider_call_and_no_analysis_rerun(self):
        self.assertEqual(self.provider_calls, 0)
        self.assertEqual(self.pipeline_calls, 0)

    def test_non_empty_output_is_refused(self):
        with self.assertRaises(FileExistsError):
            K.build_package(self.baseline, self.out, project="Web", solution="SampleLegacy")


class PromptContractTests(BehaviorBase):
    def run_scripted(self, terms):
        provider = ScriptedProvider([None] * 8)
        build(self.baseline, None, "Web", "SampleLegacy", pilot_count=2, provider=provider, domain_knowledge=terms)
        return provider.requests

    def test_prompt_asks_for_simple_name_focused_prose_without_analysis_metrics(self):
        text = A.SYSTEM + A.INSTRUCTION
        for needle in ("conteos", "nombres", "Evidence", "breve", "vista → evento → manejador"):
            self.assertIn(needle, text)

    def test_contexts_carry_no_analysis_counts(self):
        requests = self.run_scripted([])
        self.assertTrue(requests)
        for r in requests:
            blob = json.dumps(r.context, ensure_ascii=False)
            self.assertNotIn("totals_for_reference_only", blob)
            self.assertNotIn("sitio(s)", blob)
            self.assertNotIn('"counts"', blob)
            self.assertNotIn("Cobertura:", blob)
            self.assertIn("conteos", r.system_instruction)

    def test_confirmed_terms_reach_the_ai_context_and_are_labelled(self):
        terms = domain.load(self._file())
        requests = self.run_scripted(terms)
        project_req = next(r for r in requests if r.context_package_id.startswith("CTX-BEHAVIOR-project"))
        self.assertEqual(project_req.context["human_confirmed_domain_knowledge"][0]["origin"], "HUMAN_CONFIRMED")
        self.assertIn("human_confirmed_domain_knowledge", project_req.system_instruction)

    def _file(self):
        p = self.tmp / "terms2.json"
        p.write_text(json.dumps(TERMS), encoding="utf-8")
        return p


if __name__ == "__main__":
    unittest.main()
