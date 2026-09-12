import hashlib,inspect,tempfile
from pathlib import Path
import unittest
from legacy_documenter.documentation.second_review import *

ROOT=Path(__file__).parents[1]

class SecondReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.items=build_items(ROOT); cls.package=build_package(cls.items); cls.response=response_template(cls.items)
 def test_01_twenty(self): self.assertEqual(len(self.items),20)
 def test_02_resolved(self): self.assertEqual({x["id"] for x in self.items if x["id"] in RESOLVED},RESOLVED)
 def test_03_partial(self): self.assertEqual(len(PARTIAL),14)
 def test_04_external(self): self.assertEqual(EXTERNAL,{"FMI-007","TMI-001","TMI-011"})
 def test_05_c04(self): self.assertIn("C04=HUMAN_CONFIRMED",self.package)
 def test_06_recommendation_not_decision(self): self.assertIn("Las recomendaciones son informativas",self.package)
 def test_07_all_pending_package(self): self.assertEqual(self.package.count("Decisión humana: `PENDING`"),20)
 def test_08_all_pending_response(self): self.assertEqual(self.response.count("DECISION=PENDING"),22)
 def test_09_allowed(self): self.assertTrue(all(validate_item_decision(x) for x in ITEM_DECISIONS))
 def test_10_invalid_rejected(self): self.assertFalse(validate_item_decision("APPROVED"))
 def test_11_external_not_resolved(self): self.assertTrue(all(x["candidate_status"]=="EXTERNAL_INFORMATION_REQUIRED" for x in self.items if x["id"] in EXTERNAL))
 def test_12_approval_with_limits(self): self.assertTrue(document_can_be_approved(["HUMAN_CONFIRMED","ACCEPTED_AS_PARTIAL","ACCEPTED_AS_UNRESOLVED_EXTERNAL"]))
 def test_13_more_analysis_blocks(self): self.assertFalse(document_can_be_approved(["NEEDS_MORE_ANALYSIS"]))
 def test_14_architecture_uncertain(self): self.assertIn("No se encontró declaración formal",self.package)
 def test_15_no_mvc_confirmation(self): self.assertIn("MVC no está establecido",self.package)
 def test_16_bounded_evidence(self): self.assertTrue(all(len(x["evidence_basis"])<=5 for x in self.items))
 def test_17_traceability(self): self.assertEqual(self.package.count("- Trazabilidad:"),20)
 def test_18_no_llm(self): self.assertNotIn("Provider",inspect.getsource(run))
 def test_19_ai_blocked(self): self.assertIn("AI_KNOWLEDGE_ALLOWED=false",self.package)
 def test_20_no_selected_document_decision(self): self.assertNotIn("DOCUMENT_DECISION=APPROVED",self.response)
 def test_21_deterministic(self): self.assertEqual(self.package,build_package(build_items(ROOT)))
 def test_22_profiles(self): self.assertEqual((sum(x["profile"]=="functional" for x in self.items),sum(x["profile"]=="technical" for x in self.items)),(8,12))
 def test_23_recommendations(self): self.assertTrue(all(x["recommended_human_disposition"]==recommendation(x["id"]) for x in self.items))
 def test_24_no_source_access(self): self.assertNotIn("operacional",inspect.getsource(run))

if __name__=="__main__": unittest.main()
