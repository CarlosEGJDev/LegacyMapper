import inspect,json,tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from legacy_documenter.analysis.deep_interpretation import *

ROOT=Path(__file__).parents[1]

class FakeProvider:
 def __init__(self,bad=False): self.calls=0; self.bad=bad
 def structured_generate(self,request,schema):
  self.calls+=1; aliases=[x["alias"] for x in request.context["records"]]; values=[]
  for target in request.metadata["target_ids"]:
   values.append({"target_id":target,"interpretation_status":"VALID","semantic_summary":"Interpretación cautelosa basada solo en evidencia.","claim_candidates":[{"statement":"La evidencia permite una interpretación parcial.","status":"INTERPRETED","evidence_aliases":[aliases[0]]}],"evidence_aliases":[aliases[0]],"unresolved_aspects":["Requiere revisión humana."],"recommended_next_status":"PARTIALLY_RESOLVED_WITH_INTERPRETATION"})
  return SimpleNamespace(parsed_output={"interpretations":values},validation_errors=[],provider_id="FAKE",model_id="fake-model")

class R82Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.plans=plan_requests(ROOT/"output/v3_r8_1")
 def test_01_planner_deterministic(self): self.assertEqual([(x["request"].request_id,x["estimated_tokens"]) for x in self.plans],[(x["request"].request_id,x["estimated_tokens"]) for x in plan_requests(ROOT/"output/v3_r8_1")])
 def test_02_eight_targets(self): self.assertEqual({x for p in self.plans for x in p["target_ids"]},set(TARGETS))
 def test_03_only_eight(self): self.assertEqual(sum(len(x["target_ids"]) for x in self.plans),8)
 def test_04_three_groups(self): self.assertEqual(len(self.plans),3)
 def test_05_model_not_hardcoded(self): self.assertNotIn("gpt-",inspect.getsource(run_deep_interpretation).lower())
 def test_06_envelope_python(self): self.assertTrue(all(x["request"].context_package_id.startswith("CTX-R82-") for x in self.plans))
 def test_07_local_aliases(self): self.assertTrue(all(p["catalog"][0]["alias"]=="E01" for p in self.plans))
 def test_08_unknown_rejected(self):
  p=self.plans[0]; payload=FakeProvider().structured_generate(p["request"],p["schema"]).parsed_output; payload["interpretations"][0]["evidence_aliases"]=["BAD"]; self.assertRaisesRegex(ValueError,"UNKNOWN",resolve_result,payload,p)
 def test_09_canonical_mapping(self):
  p=self.plans[0]; out=resolve_result(FakeProvider().structured_generate(p["request"],p["schema"]).parsed_output,p); self.assertTrue(out[0]["canonical_evidence_ids"])
 def test_10_no_source_discovery_prompt(self): self.assertIn("Do not discover",self.plans[0]["request"].system_instruction)
 def test_11_confirmed_requires_evidence(self):
  p=self.plans[0]; payload=FakeProvider().structured_generate(p["request"],p["schema"]).parsed_output; payload["interpretations"][0]["claim_candidates"][0]={"statement":"x","status":"CONFIRMED","evidence_aliases":[]}; self.assertRaises(ValueError,resolve_result,payload,p)
 def test_12_interpretation_is_interpreted(self): self.assertEqual(FakeProvider().structured_generate(self.plans[0]["request"],self.plans[0]["schema"]).parsed_output["interpretations"][0]["claim_candidates"][0]["status"],"INTERPRETED")
 def test_13_unresolved_allowed(self): self.assertIn("UNRESOLVED",CLAIM)
 def test_14_no_forced_mvc(self): self.assertIn("never force MVC",self.plans[1]["request"].user_instruction)
 def test_15_absence_not_proof(self): self.assertFalse(any(x["kind"]=="ARCHITECTURE_INDICATOR" and x["fact"].get("indicator")=="MVC_FRAMEWORK_REFERENCE" and x["fact"].get("status")=="SUPPORTED" for x in self.plans[1]["catalog"]))
 def test_16_component_uncertainty(self): self.assertIn("preserve uncertainty",self.plans[2]["request"].system_instruction)
 def test_17_budget(self): self.assertTrue(all(x["estimated_tokens"]<=4200 for x in self.plans))
 def test_18_preferred_budget(self): self.assertTrue(all(x["estimated_tokens"]<4200 for x in self.plans))
 def test_19_partitioning(self): self.assertEqual(tuple(tuple(x["target_ids"]) for x in self.plans),GROUPS)
 def test_20_single_retry_code(self): self.assertIn('validation_errors==["invalidjson"]',inspect.getsource(run_deep_interpretation).replace(" ",""))
 def test_21_no_semantic_retry(self): self.assertEqual(inspect.getsource(run_deep_interpretation).count("structured_generate"),2)
 def test_22_failure_classification(self): self.assertIn("EVIDENCE_SELECTION",inspect.getsource(run_deep_interpretation))
 def test_23_merge_all_twenty(self):
  r=json.loads((ROOT/"output/v3_r8_1/MISSING_INFORMATION_REEVALUATION.json").read_text())["items"]; vals=[]
  for p in self.plans: vals+=resolve_result(FakeProvider().structured_generate(p["request"],p["schema"]).parsed_output,p)
  self.assertEqual(len(merge_reevaluation(r,vals)),20)
 def test_24_disposition_unchanged(self):
  r=json.loads((ROOT/"output/v3_r8_1/MISSING_INFORMATION_REEVALUATION.json").read_text())["items"]; self.assertTrue(all(x["human_disposition"]=="NEEDS_ANALYSIS" for x in merge_reevaluation(r,[])))
 def test_25_no_approval(self): self.assertNotIn("APPROVED",inspect.getsource(run_deep_interpretation))
 def test_26_ai_blocked(self): self.assertIn('"ai_knowledge_allowed":False',inspect.getsource(run_deep_interpretation).replace(" ",""))
 def test_27_callable(self): self.assertTrue(callable(run_deep_interpretation))
 def test_28_no_codex_dependency(self): self.assertNotIn("codex",inspect.getsource(run_deep_interpretation).lower())
 def test_29_secret_safe(self): self.assertNotIn("password",json.dumps([x["request"].context for x in self.plans]).lower())
 def test_30_fake_execution_three_calls(self):
  with tempfile.TemporaryDirectory() as d:
   f=FakeProvider(); result=run_deep_interpretation(ROOT/"output/v3_r8_1",d,f); self.assertEqual((result["status"],f.calls),("V3-R8_2_INTERPRETATION_COMPLETE",3))
 def test_31_outputs_present(self):
  with tempfile.TemporaryDirectory() as d:
   run_deep_interpretation(ROOT/"output/v3_r8_1",d,FakeProvider()); self.assertEqual(len(list(Path(d).glob("*.json"))),5)
 def test_32_r81_not_written(self): self.assertNotIn("write_text",inspect.getsource(evidence_pool))

if __name__=="__main__": unittest.main()
