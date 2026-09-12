import unittest
from legacy_documenter.documentation.interpretation import *
class R5Tests(unittest.TestCase):
 def pkg(self,state="COMPLETE"): return {"package_id":"CTX","source_snapshot":"snap","records":[{"ref":"E1","priority":"P0"}],"unresolved_refs":["U1"],"statistics":{"completeness":state,"estimated_tokens":10,"budget_profile":"SMALL"}}
 def test_profiles_and_prompt_determinism(self):
  for p in [FUNCTIONAL_PROFILE,TECHNICAL_PROFILE]:
   a=DocumentationPrompt(p,[self.pkg()]); self.assertEqual(a.prompt_id,a.prompt_id); r=a.to_request(); self.assertNotEqual(r.system_instruction,r.user_instruction); self.assertEqual(r.metadata["profile_id"],p.profile_id)
 def test_context_limit_and_unresolved_exposed(self):
  r=DocumentationPrompt(FUNCTIONAL_PROFILE,[self.pkg("TRUNCATED")]).to_request(); self.assertEqual(r.context["completeness"],["TRUNCATED"]); self.assertEqual(r.context["unresolved_refs"],["U1"])
 def test_valid_and_invalid_claims(self):
  base={"assessment_id":"A","profile_id":"FUNCTIONAL_ASSESSMENT","context_package_ids":["CTX"],"source_snapshots":["snap"],"status":"GENERATED"}; v=AssessmentValidator()
  good=base|{"claims":[{"claim_id":"C","status":"CONFIRMED","source_type":"DETERMINISTIC_CODE_FACT","evidence_refs":["E1"]}]}; self.assertTrue(v.validate(good,FUNCTIONAL_PROFILE,[self.pkg()])["valid"])
  bad=base|{"claims":[{"claim_id":"C","status":"CONFIRMED","source_type":"AI_INTERPRETATION","evidence_refs":[]}]}; self.assertEqual(v.validate(bad,FUNCTIONAL_PROFILE,[self.pkg()])["status"],"INVALID")
 def test_unknown_evidence_and_duplicate_rejected(self):
  x={"assessment_id":"A","profile_id":"TECHNICAL_ASSESSMENT","context_package_ids":["CTX"],"source_snapshots":["snap"],"status":"GENERATED","claims":[{"claim_id":"C","status":"INTERPRETED","source_type":"AI_INTERPRETATION","evidence_refs":["BAD"]},{"claim_id":"C","status":"UNRESOLVED","evidence_refs":[]}]}; self.assertFalse(AssessmentValidator().validate(x,TECHNICAL_PROFILE,[self.pkg()])["valid"])
