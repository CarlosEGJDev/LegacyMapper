import json,unittest
from legacy_documenter.documentation.generator import _request,_schema,_strict,prevalidate_request,SECTIONS
from legacy_documenter.documentation.interpretation import FUNCTIONAL_PROFILE,TECHNICAL_PROFILE,ASSESSMENT_STATUSES,FACT_STATUSES,MODEL_SOURCE_TYPES,CLAIM_FIELDS,MISSING_INFORMATION_FIELDS
from legacy_documenter.documentation.aggregation import aggregate
from legacy_documenter.documentation.renderer import render
from legacy_documenter.llm import ProviderConfig
from legacy_documenter.llm.providers.copilot import CopilotProvider

def pkg(kind="functional"):
 return {"package_id":"CTX-EXACT-"+kind,"source_snapshot":"SNAP-EXACT","records":[{"ref":"E1","priority":"P0","fact":"fact"},{"ref":"E2","priority":"P3","fact":"unresolved"}],"unresolved_refs":["E2"],"statistics":{"completeness":"PARTIAL"},"provenance":{}}
def valid(profile=FUNCTIONAL_PROFILE,kind="functional"):
 p=pkg(kind); return {"assessment_id":"A","profile_id":profile.profile_id,"context_package_ids":[p["package_id"]],"source_snapshots":[p["source_snapshot"]],"status":"PARTIAL","summary":"S","claims":[{"claim_id":"C1","statement":"F","status":"CONFIRMED","source_type":"DETERMINISTIC_CODE_FACT","evidence_refs":["E1"],"context_package_ids":[p["package_id"]],"section":SECTIONS[kind][0]}],"missing_information":[{"request_id":"R1","document":profile.profile_id,"section":SECTIONS[kind][-1],"question":"Q","reason":"R","blocking_level":"IMPORTANT","related_claim_ids":["C1"],"related_evidence_ids":["E2"]}]}

class ContractSerializationTests(unittest.TestCase):
 def check(self,profile,kind):
  p=pkg(kind); r=_request(profile,p,kind); s=_schema(profile,p,kind); self.assertEqual(prevalidate_request(r,s,profile,p),[]); return p,r,s
 def test_01_functional_profile_exact(self): self.assertEqual(self.check(FUNCTIONAL_PROFILE,"functional")[2]["properties"]["profile_id"]["const"],"FUNCTIONAL_ASSESSMENT")
 def test_02_technical_profile_exact(self): self.assertEqual(self.check(TECHNICAL_PROFILE,"technical")[2]["properties"]["profile_id"]["const"],"TECHNICAL_ASSESSMENT")
 def test_03_assessment_status_enum(self): self.assertEqual(set(self.check(FUNCTIONAL_PROFILE,"functional")[2]["properties"]["status"]["enum"]),ASSESSMENT_STATUSES)
 def test_04_claim_status_enum(self): self.assertEqual(set(self.check(FUNCTIONAL_PROFILE,"functional")[2]["properties"]["claims"]["items"]["properties"]["status"]["enum"]),FACT_STATUSES)
 def test_05_source_enum(self): self.assertEqual(set(self.check(FUNCTIONAL_PROFILE,"functional")[2]["properties"]["claims"]["items"]["properties"]["source_type"]["enum"]),MODEL_SOURCE_TYPES)
 def test_06_forbidden_sources_absent(self): self.assertNotIn("APPROVED_",json.dumps(self.check(FUNCTIONAL_PROFILE,"functional")[2]))
 def test_07_claim_schema_complete(self): self.assertEqual(set(self.check(FUNCTIONAL_PROFILE,"functional")[2]["properties"]["claims"]["items"]["required"]),set(CLAIM_FIELDS))
 def test_08_missing_schema_complete(self): self.assertEqual(set(self.check(FUNCTIONAL_PROFILE,"functional")[2]["properties"]["missing_information"]["items"]["required"]),set(MISSING_INFORMATION_FIELDS))
 def test_09_evidence_exact(self): self.assertEqual(self.check(FUNCTIONAL_PROFILE,"functional")[2]["properties"]["claims"]["items"]["properties"]["evidence_refs"]["items"]["enum"],["E1","E2"])
 def test_10_package_exact(self): self.assertEqual(self.check(FUNCTIONAL_PROFILE,"functional")[2]["properties"]["context_package_ids"]["const"],["CTX-EXACT-functional"])
 def test_11_snapshot_exact(self): self.assertEqual(self.check(FUNCTIONAL_PROFILE,"functional")[2]["properties"]["source_snapshots"]["const"],["SNAP-EXACT"])
 def test_12_promotion_unambiguous(self): self.assertIn("AI_INTERPRETATION MUST use INTERPRETED, never CONFIRMED",self.check(FUNCTIONAL_PROFILE,"functional")[1].user_instruction)
 def test_13_json_only(self): self.assertIn("one JSON object only",self.check(FUNCTIONAL_PROFILE,"functional")[1].user_instruction)
 def test_14_serialization_deterministic(self): self.assertEqual(_request(FUNCTIONAL_PROFILE,pkg(),"functional").user_instruction,_request(FUNCTIONAL_PROFILE,pkg(),"functional").user_instruction)
 def test_15_record_limit(self): self.assertLessEqual(len(pkg()["records"]),40)

class ContractRejectionTests(unittest.TestCase):
 def test_16_malformed_rejected(self): self.assertIn("claim schema",_strict(valid()|{"claims":[{}]},FUNCTIONAL_PROFILE,pkg()))
 def test_17_profile_mismatch(self): self.assertIn("profile",_strict(valid()|{"profile_id":"BAD"},FUNCTIONAL_PROFILE,pkg()))
 def test_18_unknown_source(self):
  x=valid(); x["claims"][0]["source_type"]="OTHER"; self.assertIn("source type",_strict(x,FUNCTIONAL_PROFILE,pkg()))
 def test_19_incomplete_claim(self):
  x=valid(); del x["claims"][0]["section"]; self.assertIn("claim schema",_strict(x,FUNCTIONAL_PROFILE,pkg()))
 def test_20_incomplete_missing(self):
  x=valid(); del x["missing_information"][0]["reason"]; self.assertIn("missing schema",_strict(x,FUNCTIONAL_PROFILE,pkg()))
 def test_21_invented_evidence(self):
  x=valid(); x["claims"][0]["evidence_refs"]=["BAD"]; self.assertIn("evidence closure",_strict(x,FUNCTIONAL_PROFILE,pkg()))
 def test_22_ai_cannot_confirm(self):
  x=valid(); x["claims"][0]["source_type"]="AI_INTERPRETATION"; self.assertIn("status promotion",_strict(x,FUNCTIONAL_PROFILE,pkg()))
 def test_23_unresolved_cannot_confirm(self):
  x=valid(); x["claims"][0]["source_type"]="UNRESOLVED"; self.assertIn("status promotion",_strict(x,FUNCTIONAL_PROFILE,pkg()))
 def test_24_valid_functional(self): self.assertEqual(_strict(valid(),FUNCTIONAL_PROFILE,pkg()),[])
 def test_25_valid_technical_and_renderer(self):
  x=valid(TECHNICAL_PROFILE,"technical"); self.assertEqual(_strict(x,TECHNICAL_PROFILE,pkg("technical")),[]); d=aggregate([x],[pkg("technical")]); self.assertIn("STATUS=DRAFT",render(d,"technical","m"))

if __name__=="__main__": unittest.main()
