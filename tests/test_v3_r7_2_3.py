import copy,json,unittest
from pathlib import Path
from legacy_documenter.documentation.evidence_catalog import *
from legacy_documenter.documentation.envelope import compose_envelope,semantic_unchanged
from legacy_documenter.documentation.generator import _strict,SECTIONS
from legacy_documenter.documentation.interpretation import FUNCTIONAL_PROFILE,AssessmentValidator
from legacy_documenter.documentation.synthesis import compact_assessments,SynthesisPlanner,canonical_hash
from legacy_documenter.documentation.aggregation import aggregate,evidence_closed
from legacy_documenter.documentation.renderer import render

def package(refs=("CAN-A","CAN-B")):
 return {"package_id":"P","source_snapshot":"S","scope":{"coverage_batch":0},"records":[{"ref":r,"category":"PROJECT","fact":{"name":"N","count":1},"source_type":"DETERMINISTIC_CODE_FACT"} for r in refs],"unresolved_refs":[],"statistics":{"estimated_tokens":20}}
def semantic(keys=("E01",),status="CONFIRMED",source="DETERMINISTIC_CODE_FACT"):
 return {"status":"PARTIAL","summary":"S","claims":[{"claim_id":"C","statement":"T","status":status,"source_type":source,"evidence_keys":list(keys),"section":SECTIONS["functional"][0]}],"missing_information":[{"request_id":"R","section":SECTIONS["functional"][-1],"question":"Q","reason":"R","blocking_level":"IMPORTANT","related_claim_ids":["C"],"related_evidence_keys":["E02"]}]}

class CatalogTests(unittest.TestCase):
 def setUp(self): self.p=package(); self.c=build_catalog(self.p)
 def test_01_deterministic(self): self.assertEqual(self.c,build_catalog(self.p))
 def test_02_order(self): self.assertEqual([x["canonical_id"] for x in self.c],["CAN-A","CAN-B"])
 def test_03_keys(self): self.assertEqual([x["key"] for x in self.c],["E01","E02"])
 def test_04_current_only(self): self.assertEqual({x["canonical_id"] for x in self.c},{r["ref"] for r in self.p["records"]})
 def test_05_duplicate_key(self): self.assertRaises(EvidenceCatalogError,validate_catalog,[self.c[0],self.c[0]],self.p)
 def test_06_unknown_canonical(self):
  x=copy.deepcopy(self.c); x[0]["canonical_id"]="BAD"; self.assertRaises(EvidenceCatalogError,validate_catalog,x,self.p)
 def test_07_visible_no_ids(self): self.assertNotIn("canonical_id",json.dumps(visible_catalog(self.c)))
 def test_08_resolve_one(self): self.assertEqual(resolve_payload(semantic(),self.c)["claims"][0]["evidence_refs"],["CAN-A"])
 def test_09_resolve_many(self): self.assertEqual(resolve_payload(semantic(("E02","E01")),self.c)["claims"][0]["evidence_refs"],["CAN-B","CAN-A"])
 def test_10_unknown_rejected(self): self.assertRaises(EvidenceCatalogError,resolve_payload,semantic(("E99",)),self.c)
 def test_11_unknown_not_removed(self):
  x=semantic(("E99",)); self.assertRaises(EvidenceCatalogError,resolve_payload,x,self.c); self.assertEqual(x["claims"][0]["evidence_keys"],["E99"])
 def test_12_no_nearest_match(self): self.assertRaises(EvidenceCatalogError,resolve_payload,semantic(("E1",)),self.c)
 def test_13_claim_resolution(self): self.assertIn("evidence_refs",resolve_payload(semantic(),self.c)["claims"][0])
 def test_14_missing_resolution(self): self.assertEqual(resolve_payload(semantic(),self.c)["missing_information"][0]["related_evidence_ids"],["CAN-B"])
 def test_15_unknown_missing_rejected(self):
  x=semantic(); x["missing_information"][0]["related_evidence_keys"]=["BAD"]; self.assertRaises(EvidenceCatalogError,resolve_payload,x,self.c)
 def test_16_canonical_has_refs(self): self.assertIn("evidence_refs",resolve_payload(semantic(),self.c)["claims"][0])
 def test_17_no_temp_keys(self): self.assertNotIn("evidence_keys",resolve_payload(semantic(),self.c)["claims"][0])
 def test_18_statement_unchanged(self): self.assertEqual(resolve_payload(semantic(),self.c)["claims"][0]["statement"],"T")
 def test_19_status_unchanged(self): self.assertEqual(resolve_payload(semantic(),self.c)["claims"][0]["status"],"CONFIRMED")
 def test_20_source_unchanged(self): self.assertEqual(resolve_payload(semantic(),self.c)["claims"][0]["source_type"],"DETERMINISTIC_CODE_FACT")
 def test_21_promotion_still_rejected(self):
  r=resolve_payload(semantic(status="CONFIRMED",source="AI_INTERPRETATION"),self.c); a=compose_envelope(r,FUNCTIONAL_PROFILE,self.p,"H","LOCAL"); self.assertIn("status promotion",_strict(a,FUNCTIONAL_PROFILE,self.p))
 def test_22_source_still_rejected(self):
  x=semantic(source="OTHER"); x["claims"][0]["source_type"]="OTHER"; r=resolve_payload(x,self.c); self.assertIn("source type",_strict(compose_envelope(r,FUNCTIONAL_PROFILE,self.p,"H","LOCAL"),FUNCTIONAL_PROFILE,self.p))
 def test_23_interpreted_keys(self): self.assertEqual(resolve_payload(semantic(status="INTERPRETED",source="AI_INTERPRETATION"),self.c)["claims"][0]["status"],"INTERPRETED")
 def test_24_unresolved_keys(self): self.assertEqual(resolve_payload(semantic(status="UNRESOLVED",source="UNRESOLVED"),self.c)["claims"][0]["status"],"UNRESOLVED")
 def test_25_dynamic_enum(self): self.assertEqual(catalog_schema(FUNCTIONAL_PROFILE,self.c,SECTIONS["functional"])["properties"]["claims"]["items"]["properties"]["evidence_keys"]["items"]["enum"],["E01","E02"])
 def test_26_foreign_excluded(self): self.assertNotIn("FOREIGN",json.dumps(catalog_schema(FUNCTIONAL_PROFILE,self.c,SECTIONS["functional"])))
 def test_27_preflight(self): self.assertTrue(validate_catalog(self.c,self.p))
 def test_28_bad_prevents_use(self): self.assertRaises(EvidenceCatalogError,validate_catalog,[{"key":"E01","canonical_id":"BAD","description":"x"}],self.p)
 def test_29_description_stable(self): self.assertEqual(self.c[0]["description"],build_catalog(self.p)[0]["description"])
 def test_30_no_llm_description(self): self.assertNotIn("llm",self.c[0]["description"].lower())
 def test_31_catalog_small(self): self.assertLess(len(json.dumps(visible_catalog(self.c)))//4,5000)
 def test_32_resolution_integrity(self): self.assertTrue(resolution_preserves_semantics(semantic(),resolve_payload(semantic(),self.c)))

class ResumeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.items=json.loads(Path("output/v3_r7_2/LOCAL_ASSESSMENTS.json").read_text(encoding="utf-8"))["assessments"]
 def test_33_local_checkpoint_complete(self): self.assertEqual(len(self.items),16)
 def test_34_cache_valid(self): self.assertTrue(all(x["validation_status"]=="VALID" for x in self.items))
 def test_35_functional_complete(self): self.assertEqual(sum(x["stage"]=="LOCAL_FUNCTIONAL" for x in self.items),8)
 def test_36_technical_complete(self): self.assertEqual(sum(x["stage"]=="LOCAL_TECHNICAL" for x in self.items),8)
 def test_37_missing_technical_zero(self): self.assertEqual(8-sum(x["stage"]=="LOCAL_TECHNICAL" for x in self.items),0)
 def test_38_hashes_valid(self): self.assertTrue(all(x["content_hash"]==canonical_hash({k:v for k,v in x.items() if k!="content_hash"}) for x in self.items))
 def test_39_failed_not_cached(self): self.assertTrue(all(x.get("validation_status")=="VALID" for x in self.items))
 def test_40_intermediate_catalog(self): self.assertEqual(build_catalog(package(("SYN-A","SYN-B")))[0]["key"],"E01")
 def test_41_intermediate_resolution(self): self.assertEqual(resolve_payload(semantic(),build_catalog(package(("SYN-A","SYN-B"))))["claims"][0]["evidence_refs"],["SYN-A"])
 def test_42_global_catalog_stable(self): self.assertEqual(build_catalog(package(("SYN-A",))),build_catalog(package(("SYN-A",))))
 def test_43_trace_canonical(self):
  p=package(); c=build_catalog(p); a=compose_envelope(resolve_payload(semantic(),c),FUNCTIONAL_PROFILE,p,"H","LOCAL"); self.assertTrue(AssessmentValidator().validate(a,FUNCTIONAL_PROFILE,[p])["valid"])
 def test_44_no_long_id_required(self): self.assertNotIn("CAN-A",json.dumps(visible_catalog(build_catalog(package()))))
 def test_45_validator_unchanged(self): self.assertTrue(hasattr(AssessmentValidator(),"validate"))
 def test_46_no_repair(self): self.assertTrue(resolution_preserves_semantics(semantic(),resolve_payload(semantic(),build_catalog(package()))))
 def test_47_renderer_canonical(self):
  p=package(); a=compose_envelope(resolve_payload(semantic(),build_catalog(p)),FUNCTIONAL_PROFILE,p,"H","LOCAL"); self.assertIn("CAN-A",render(aggregate([a],[p]),"functional","m"))
 def test_48_draft(self):
  p=package(); a=compose_envelope(resolve_payload(semantic(),build_catalog(p)),FUNCTIONAL_PROFILE,p,"H","LOCAL"); self.assertIn("STATUS=DRAFT",render(aggregate([a],[p]),"functional","m"))
 def test_49_ai_blocked(self):
  p=package(); a=compose_envelope(resolve_payload(semantic(),build_catalog(p)),FUNCTIONAL_PROFILE,p,"H","LOCAL"); self.assertIn("AI_KNOWLEDGE_ALLOWED=false",render(aggregate([a],[p]),"functional","m"))
 def test_50_source_immutable(self): self.assertNotIn("operacional",Path("legacy_documenter/documentation/evidence_catalog.py").read_text())
 def test_51_provider_neutral(self): self.assertNotIn("Copilot",Path("legacy_documenter/documentation/evidence_catalog.py").read_text())
 def test_52_model_not_hardcoded(self): self.assertNotIn("gpt-5.6-luna",Path("legacy_documenter/documentation/evidence_resume.py").read_text())
 def test_53_no_fixed_failure_policy(self): self.assertNotIn("failure_count",Path("legacy_documenter/documentation/evidence_resume.py").read_text())

if __name__=="__main__": unittest.main()
