import hashlib,inspect,json,tempfile
from pathlib import Path
import unittest
from legacy_documenter.analysis.targeted_exhaustion import *
from legacy_documenter.analysis.targeted_exhaustion import _safe_path

ROOT=Path(__file__).parents[1]

class TargetedTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  r=json.loads((ROOT/"output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json").read_text())["items"]
  cls.defs=recover_definitions((ROOT/"output/LEVANTAMIENTO_FUNCIONAL.md").read_text(encoding="utf-8"),(ROOT/"output/LEVANTAMIENTO_TECNICO.md").read_text(encoding="utf-8"),r)
 def test_01_three_targets(self): self.assertEqual(TARGETS,("FMI-007","TMI-001","TMI-011"))
 def test_02_definitions_recovered(self): self.assertTrue(all(x["definition_status"]=="RECOVERED" for x in self.defs))
 def test_03_questions_present(self): self.assertTrue(all(x["description"] for x in self.defs))
 def test_04_missing_not_external(self): self.assertEqual(exhaustion_status({"definition_status":"TARGET_DEFINITION_MISSING"},True,{"applicable":False},["x"])[0],"TARGET_DEFINITION_MISSING")
 def test_05_existing_first(self): self.assertIn("CHECK_V1_V2_R7_R8_R8_1_R8_2",inspect.getsource(run))
 def test_06_bounded_lookup(self): self.assertEqual(targeted_data_lookup(".",[],12),[])
 def test_07_max_files(self): self.assertIn("max_files=12",inspect.getsource(targeted_data_lookup))
 def test_08_no_rescan(self): self.assertNotIn("analyze_repository",inspect.getsource(run))
 def test_09_exact_safe_path(self):
  with tempfile.TemporaryDirectory() as d: self.assertEqual(_safe_path(d,"a.txt"),Path(d,"a.txt").resolve())
 def test_10_outside_rejected(self):
  with tempfile.TemporaryDirectory() as d: self.assertRaises(ValueError,_safe_path,d,"../outside")
 def test_11_no_nearest(self): self.assertNotIn("similar",inspect.getsource(targeted_data_lookup).lower())
 def test_12_presence_not_purpose(self): self.assertIn("Business purpose cannot be confirmed",inspect.getsource(run))
 def test_13_runtime_not_inferred(self): self.assertNotIn("RUNTIME_BEHAVIOR_CONFIRMED",inspect.getsource(run))
 def test_14_sanitize(self): self.assertNotIn("clave",sanitize_text("Password=clave"))
 def test_15_exhaustion_requires_definition(self): self.assertFalse(exhaustion_status({"definition_status":"TARGET_DEFINITION_MISSING"},True,{"applicable":False},["x"])[1])
 def test_16_external_not_premature(self): self.assertEqual(exhaustion_status({"definition_status":"RECOVERED"},False,{"applicable":False},["x"])[0],"PARTIALLY_RESOLVED")
 def test_17_lookup_required_when_applicable(self): self.assertEqual(exhaustion_status({"definition_status":"RECOVERED"},True,{"applicable":True,"performed":False},["x"])[0],"PARTIALLY_RESOLVED")
 def test_18_external_after_exhaustion(self): self.assertEqual(exhaustion_status({"definition_status":"RECOVERED"},True,{"applicable":True,"performed":True},["x"])[0],"EXTERNAL_INFORMATION_REQUIRED")
 def test_19_llm_optional(self): self.assertNotIn("Provider",inspect.getsource(run))
 def test_20_no_llm_discovery(self): self.assertNotIn("structured_generate",inspect.getsource(run))
 def test_21_semantic_confirmed_absent(self): self.assertNotIn("CONFIRMED\"]",inspect.getsource(run))
 def test_22_previous_human(self): self.assertTrue(all(x["human_disposition"]=="NEEDS_ANALYSIS" for x in self.defs))
 def test_23_no_knowledge(self): self.assertIn('"ai_knowledge_allowed":False',inspect.getsource(run).replace(" ",""))
 def test_24_runtime_callable(self): self.assertTrue(callable(run))
 def test_25_canonical_architecture_meaning(self): self.assertTrue(all("arquitect" in x["description"].lower() for x in self.defs if x["target_id"].startswith("TMI")))
 def test_26_allowed_statuses(self): self.assertIn("EXTERNAL_INFORMATION_REQUIRED",ALLOWED)
 def test_27_no_approval(self): self.assertNotIn("APPROVED",inspect.getsource(run))
 def test_28_profile_exact(self): self.assertEqual([x["document_profile"] for x in self.defs],["functional","technical","technical"])

if __name__=="__main__": unittest.main()
