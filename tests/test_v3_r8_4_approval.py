from pathlib import Path
import inspect,re,unittest
from legacy_documenter.documentation.human_review import parse_document

ROOT=Path(__file__).parents[1]; RESPONSE=ROOT/"codex/V3/V3_R8_4_RESPUESTA_REVISION.md"; RECORD=ROOT/"codex/V3/V3_R8_4_REVISION_HUMANA_APROBADA.md"

class ApprovalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.response=RESPONSE.read_text(encoding="utf-8"); cls.record=RECORD.read_text(encoding="utf-8"); cls.f=(ROOT/"output/LEVANTAMIENTO_FUNCIONAL.md").read_text(encoding="utf-8"); cls.t=(ROOT/"output/LEVANTAMIENTO_TECNICO.md").read_text(encoding="utf-8")
 def test_01_no_pending_items(self): self.assertNotIn("DECISION=PENDING",self.response)
 def test_02_exact_twenty(self): self.assertEqual(len(re.findall(r"^DECISION=",self.response,re.M)),20)
 def test_03_c04(self): self.assertIn("C04=HUMAN_CONFIRMED",self.record)
 def test_04_fmi8(self): self.assertIn("FMI-008=HUMAN_CONFIRMED",self.record)
 def test_05_tmi2(self): self.assertIn("TMI-002=HUMAN_CONFIRMED",self.record)
 def test_06_tmi5(self): self.assertIn("TMI-005=HUMAN_CONFIRMED",self.record)
 def test_07_fourteen_partial(self): self.assertEqual(self.response.count("DECISION=ACCEPTED_AS_PARTIAL"),14)
 def test_08_three_external(self): self.assertEqual(self.response.count("DECISION=ACCEPTED_AS_UNRESOLVED_EXTERNAL"),3)
 def test_09_external_not_resolved(self): self.assertNotIn("FMI-007=HUMAN_CONFIRMED",self.record)
 def test_10_exhausted_three(self): self.assertEqual(self.record.count("evidence_exhausted=true"),3)
 def test_11_partial_no_claim_promotion(self): self.assertIn("no promueve ningún claim",self.record)
 def test_12_docs_approved(self): self.assertTrue(all(x in self.response for x in ("FUNCTIONAL_DOCUMENT_DECISION=APPROVED","TECHNICAL_DOCUMENT_DECISION=APPROVED")))
 def test_13_arch_limits(self): self.assertIn("No se encontró declaración formal",self.record)
 def test_14_no_formal_pattern(self): self.assertNotIn("ARCHITECTURE_PATTERN=CONFIRMED",self.record)
 def test_15_no_mvc(self): self.assertIn("MVC no está establecido",self.record)
 def test_16_record_canonical(self): self.assertIn("STATUS=V3-R8_4_SECOND_HUMAN_REVIEW_APPROVED",self.record)
 def test_17_no_llm(self): self.assertNotIn("REAL_LLM_CALLS=1",self.record)
 def test_18_no_scan(self): self.assertNotIn("source\\IST_40",self.record)
 def test_19_eligible(self): self.assertTrue(all("knowledge_source_eligible=true" in x for x in (self.f,self.t)))
 def test_20_ai_blocked(self): self.assertTrue(all("AI_KNOWLEDGE_ALLOWED=false" in x for x in (self.f,self.t,self.record)))
 def test_21_lifecycle(self): self.assertTrue(all("document_status=APPROVED" in x for x in (self.f,self.t)))
 def test_22_claim_counts(self): self.assertEqual((len(parse_document(self.f)["claims"]),len(parse_document(self.t)["claims"])),(13,14))
 def test_23_statement_exact(self): self.assertIn("Apruebo la segunda revisión humana",self.response)
 def test_24_next_r9(self): self.assertIn("NEXT=V3-R9_KNOWLEDGE_READINESS_GATE",self.record)
 def test_25_not_global_allowed(self): self.assertNotIn("AI_KNOWLEDGE_ALLOWED=true",self.record)

if __name__=="__main__": unittest.main()
