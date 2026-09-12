import hashlib
from pathlib import Path
import unittest

from legacy_documenter.documentation.human_review import run


ROOT=Path(__file__).parents[1]
RESPONSE=ROOT/"codex/V3/V3_R8_RESPUESTA_REVISION.md"
RECORD=ROOT/"codex/V3/V3_R8_REVISION_REGISTRADA.md"


class TestV3R8Decision(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.response=RESPONSE.read_text(encoding="utf-8"); cls.record=RECORD.read_text(encoding="utf-8")
 def test_01_functional_decision(self): self.assertIn("FUNCTIONAL_DECISION=NEEDS_MORE_INFORMATION",self.response)
 def test_02_technical_decision(self): self.assertIn("TECHNICAL_DECISION=NEEDS_MORE_INFORMATION",self.response)
 def test_03_c04_confirmed(self): self.assertIn("HUMAN_CONFIRMED_CLAIMS=C04",self.response)
 def test_04_all_fmi(self): self.assertTrue(all(f"FMI-{i:03d}=NEEDS_ANALYSIS" in self.response for i in range(1,9)))
 def test_05_all_tmi(self): self.assertTrue(all(f"TMI-{i:03d}=NEEDS_ANALYSIS" in self.response for i in range(1,13)))
 def test_06_exact_fmi_count(self): self.assertEqual(self.response.count("FMI-") ,8)
 def test_07_exact_tmi_count(self): self.assertEqual(self.response.count("TMI-") ,12)
 def test_08_knowledge_blocked(self): self.assertIn("AI_KNOWLEDGE_ALLOWED=false",self.record)
 def test_09_not_approved(self): self.assertIn("DOCUMENTS_APPROVED=false",self.record)
 def test_10_architecture_unknown(self): self.assertIn("ARCHITECTURE_HUMAN_KNOWLEDGE=NOT_PROVIDED",self.record)
 def test_11_no_mvc_assumption(self): self.assertIn("no se asume MVC",self.record)
 def test_12_next_state(self): self.assertIn("NEXT=DEEPER_SOURCE_ANALYSIS_DESIGN",self.record)
 def test_13_status(self): self.assertIn("STATUS=V3-R8_HUMAN_REVIEW_RECORDED_NEEDS_ANALYSIS",self.record)
 def test_14_reexecution_preserves_response(self):
  before=hashlib.sha256(RESPONSE.read_bytes()).digest(); run(ROOT); self.assertEqual(before,hashlib.sha256(RESPONSE.read_bytes()).digest())
 def test_15_no_analysis_started(self): self.assertIn("análisis profundo no se inicia",self.record)


if __name__=="__main__": unittest.main()
