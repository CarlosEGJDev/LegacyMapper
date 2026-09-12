import hashlib,inspect,json,tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from legacy_documenter.analysis.deep_interpretation import *

ROOT=Path(__file__).parents[1]

class InvalidConfirmedProvider:
 def structured_generate(self,request,schema):
  aliases=[x["alias"] for x in request.context["records"]]; alias=aliases[0]
  if "TMI-001" in request.metadata["target_ids"]:
   nonauth=next((x["alias"] for x in request.context["records"] if x.get("authoritative") is False),alias)
  else: nonauth=alias
  values=[]
  for target in request.metadata["target_ids"]: values.append({"target_id":target,"interpretation_status":"VALID","semantic_summary":"x","claim_candidates":[{"statement":"x","status":"CONFIRMED","evidence_aliases":[nonauth]}],"evidence_aliases":[nonauth],"unresolved_aspects":[],"recommended_next_status":"PARTIALLY_RESOLVED_WITH_INTERPRETATION"})
  return SimpleNamespace(parsed_output={"interpretations":values},validation_errors=[],provider_id="P",model_id="M",request_id=request.request_id)

class CorrectionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.plans=plan_requests(ROOT/"output/v3_r8_1")
 def statuses(self,p): return p["schema"]["properties"]["interpretations"]["items"]["properties"]["claim_candidates"]["items"]["properties"]["status"]["enum"]
 def test_01_semantic_excludes_confirmed(self): self.assertTrue(all("CONFIRMED" not in self.statuses(p) for p in self.plans))
 def test_02_architecture_excludes_confirmed(self): self.assertNotIn("CONFIRMED",self.statuses(self.plans[1]))
 def test_03_pattern_not_claim_status(self): self.assertNotIn("PATTERN_SUPPORTED",self.statuses(self.plans[1]))
 def test_04_deterministic_separated(self): self.assertIn("deterministic_facts",inspect.getsource(run_deep_interpretation))
 def test_05_facts_unchanged(self):
  p=self.plans[0]; self.assertEqual(p["catalog"],plan_requests(ROOT/"output/v3_r8_1")[0]["catalog"])
 def test_06_prompt_no_promotion(self): self.assertIn("Never upgrade",self.plans[0]["request"].system_instruction)
 def test_07_validator_rejects_confirmed_nonauthority(self):
  p=self.plans[1]; payload=InvalidConfirmedProvider().structured_generate(p["request"],p["schema"]).parsed_output; self.assertRaisesRegex(ValueError,"AUTHORITY",resolve_result,payload,p)
 def test_08_no_silent_downgrade(self): self.assertNotIn("INTERPRETED\" if",inspect.getsource(resolve_result))
 def test_09_schema_deterministic(self): self.assertEqual(self.plans[1]["schema"],plan_requests(ROOT/"output/v3_r8_1")[1]["schema"])
 def test_10_purpose_enum(self): self.assertEqual(self.statuses(self.plans[0]),["INTERPRETED","UNRESOLVED"])
 def test_11_group_b_regression(self): self.assertEqual(self.statuses(self.plans[1]),["INTERPRETED","UNRESOLVED"])
 def test_12_provider_telemetry_failure(self):
  with tempfile.TemporaryDirectory() as d: self.assertEqual(run_deep_interpretation(ROOT/"output/v3_r8_1",d,InvalidConfirmedProvider())["effective_provider"],"P")
 def test_13_model_telemetry_failure(self):
  with tempfile.TemporaryDirectory() as d: self.assertEqual(run_deep_interpretation(ROOT/"output/v3_r8_1",d,InvalidConfirmedProvider())["effective_model"],"M")
 def test_14_model_not_guessed(self): self.assertEqual(run_deep_interpretation.__defaults__[2],None)
 def test_15_atomic_publication(self):
  with tempfile.TemporaryDirectory() as d:
   run_deep_interpretation(ROOT/"output/v3_r8_1",d,InvalidConfirmedProvider()); self.assertFalse(list(Path(d).glob("*.json")))
 def test_16_rejected_not_persisted(self):
  with tempfile.TemporaryDirectory() as d:
   r=run_deep_interpretation(ROOT/"output/v3_r8_1",d,InvalidConfirmedProvider()); self.assertEqual(r["status"],"V3-R8_2_NEEDS_CORRECTION")
 def test_17_r81_read_only(self): self.assertNotIn("write_text",inspect.getsource(evidence_pool))
 def test_18_no_raw_scan(self): self.assertNotIn("rglob",inspect.getsource(run_deep_interpretation))
 def test_19_no_approval(self): self.assertNotIn("APPROVED",inspect.getsource(run_deep_interpretation))
 def test_20_ai_blocked(self): self.assertIn('"ai_knowledge_allowed":False',inspect.getsource(run_deep_interpretation).replace(" ",""))

if __name__=="__main__": unittest.main()
