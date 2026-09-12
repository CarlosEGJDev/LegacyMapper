import hashlib
import inspect
import json
from pathlib import Path
import unittest

from legacy_documenter.documentation.human_review import *


ROOT = Path(__file__).parents[1]


class TestV3R8(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fp=ROOT/"output/LEVANTAMIENTO_FUNCIONAL.md"; cls.tp=ROOT/"output/LEVANTAMIENTO_TECNICO.md"
        cls.fa=ROOT/"output/v3_r7_2/LOCAL_ASSESSMENTS.json"; cls.ia=ROOT/"output/v3_r7_2/INTERMEDIATE_ASSESSMENTS.json"
        cls.f=cls.fp.read_text(encoding="utf-8"); cls.t=cls.tp.read_text(encoding="utf-8")
        cls.parent=(ROOT/"codex/V3/V3_R7_2_4_RESULTADO.md").read_text(encoding="utf-8")
        cls.metrics=json.loads((ROOT/"output/v3_r7_2/COVERAGE_INDEX.json").read_text(encoding="utf-8"))["metrics"]
        cls.package=build_package(cls.f,cls.t,cls.metrics); cls.response=response_template()
        cls.pf=parse_document(cls.f); cls.pt=parse_document(cls.t)

    def test_01_functional_approved_lifecycle(self): self.assertIn("document_status=APPROVED",self.f)
    def test_02_technical_approved_lifecycle(self): self.assertIn("document_status=APPROVED",self.t)
    def test_03_functional_review_closed(self): self.assertIn("human_review_required=false",self.f)
    def test_04_technical_review_closed(self): self.assertIn("human_review_required=false",self.t)
    def test_05_approved_true(self): self.assertTrue(all("approved=true" in x for x in (self.f,self.t)))
    def test_06_knowledge_eligible(self): self.assertTrue(all("knowledge_source_eligible=true" in x for x in (self.f,self.t)))
    def test_07_deterministic(self): self.assertEqual(self.package,build_package(self.f,self.t,self.metrics))
    def test_08_coverage(self): self.assertIn("PROJECTS_CLASSIFIED=259",self.package)
    def test_09_structural_warning(self): self.assertIn("STRUCTURAL_COVERAGE != COMPLETE_SEMANTIC_UNDERSTANDING",self.package)
    def test_10_functional_confirmed(self): self.assertTrue(any(x["status"]=="CONFIRMED" and x["claim_id"] in self.package for x in self.pf["claims"]))
    def test_11_functional_interpreted(self): self.assertTrue(any(x["status"]=="INTERPRETED" and x["claim_id"] in self.package for x in self.pf["claims"]))
    def test_12_functional_unresolved(self): self.assertTrue(any(x["status"]=="UNRESOLVED" and x["claim_id"] in self.package for x in self.pf["claims"]))
    def test_13_fmi(self): self.assertTrue(all(x["request_id"] in self.package for x in self.pf["missing_information"]))
    def test_14_functional_checklist_empty(self): self.assertEqual(self.package.count("- [ ]"),20)
    def test_15_technical_confirmed(self): self.assertTrue(any(x["status"]=="CONFIRMED" and x["claim_id"] in self.package for x in self.pt["claims"]))
    def test_16_technical_interpreted(self): self.assertTrue(any(x["status"]=="INTERPRETED" and x["claim_id"] in self.package for x in self.pt["claims"]))
    def test_17_technical_unresolved(self): self.assertTrue(any(x["status"]=="UNRESOLVED" and x["claim_id"] in self.package for x in self.pt["claims"]))
    def test_18_tmi(self): self.assertTrue(all(x["request_id"] in self.package for x in self.pt["missing_information"]))
    def test_19_technical_checklist_empty(self): self.assertNotIn("- [x]",self.package.lower())
    def test_20_scope_distinction(self): self.assertIn("alcances deterministas diferentes",self.package)
    def test_21_2009(self): self.assertIn("data_access_partition_count=2009",self.package)
    def test_22_19159(self): self.assertIn("linked_data_operations=19159",self.package)
    def test_23_674(self): self.assertIn("stored_procedures_partition_count=674",self.package)
    def test_24_5389(self): self.assertIn("linked_stored_procedures=5389",self.package)
    def test_25_functional_blocker(self): self.assertIn("FMI-002",self.package.split("TECHNICAL_BLOCKING_ITEMS")[0])
    def test_26_technical_blocker(self): self.assertIn("TMI-001",self.package.split("TECHNICAL_BLOCKING_ITEMS")[1])
    def test_27_response_template(self): self.assertIn("GENERAL_COMMENTS=",self.response)
    def test_28_functional_pending(self): self.assertIn("FUNCTIONAL_DECISION=PENDING",self.response)
    def test_29_technical_pending(self): self.assertIn("TECHNICAL_DECISION=PENDING",self.response)
    def test_30_no_selected_approval(self): self.assertNotIn("DECISION=APPROVED",self.response)
    def test_31_no_knowledge_promotion(self): self.assertIn("AI_KNOWLEDGE_ALLOWED=false",self.package)

    def test_32_source_docs_unchanged(self):
        before=(hashlib.sha256(self.fp.read_bytes()).digest(),hashlib.sha256(self.tp.read_bytes()).digest()); run(ROOT); self.assertEqual(before,(hashlib.sha256(self.fp.read_bytes()).digest(),hashlib.sha256(self.tp.read_bytes()).digest()))
    def test_33_assessments_unchanged(self):
        before=(hashlib.sha256(self.fa.read_bytes()).digest(),hashlib.sha256(self.ia.read_bytes()).digest()); run(ROOT); self.assertEqual(before,(hashlib.sha256(self.fa.read_bytes()).digest(),hashlib.sha256(self.ia.read_bytes()).digest()))
    def test_34_v2_not_written(self): self.assertNotIn("v2_r5_1_full",inspect.getsource(run))
    def test_35_no_provider(self): self.assertNotIn("provider",inspect.getsource(run).lower())
    def test_36_no_llm(self): self.assertNotIn("llm",inspect.getsource(run).lower())
    def test_37_no_raw_scan(self): self.assertNotIn("rglob",inspect.getsource(run))
    def test_38_no_legacy_source(self): self.assertNotIn("operacional",inspect.getsource(run))
    def test_39_traceability_refs(self): self.assertIn("TRACEABILITY_AVAILABLE=true",self.package)
    def test_40_explicit_human(self): self.assertIn("decisiones humanas explícitas",self.package)
    def test_41_both_approved_ready(self): self.assertTrue(knowledge_ready("APPROVED","APPROVED"))
    def test_42_one_pending_blocked(self): self.assertFalse(knowledge_ready("APPROVED","PENDING"))
    def test_43_tests_not_approval(self): self.assertIn("PASS de tests",self.package)
    def test_44_codex_not_approval(self): self.assertIn("estado de Codex",self.package)
    def test_45_package_not_approval(self): self.assertIn("creación de este paquete",self.package)
    def test_46_first_review_preconditions_closed(self): self.assertFalse(validate_preconditions(self.f,self.t,self.parent))
    def test_47_claim_counts(self): self.assertEqual((len(self.pf["claims"]),len(self.pt["claims"])),(13,14))
    def test_48_missing_counts(self): self.assertEqual((len(self.pf["missing_information"]),len(self.pt["missing_information"])),(8,12))


if __name__ == "__main__": unittest.main()
