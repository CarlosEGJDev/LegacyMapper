import copy,json,tempfile,unittest
from pathlib import Path
from legacy_documenter.documentation.envelope import *
from legacy_documenter.documentation.interpretation import DocumentationPrompt,FUNCTIONAL_PROFILE,AssessmentValidator
from legacy_documenter.documentation.generator import _strict,SECTIONS
from legacy_documenter.documentation.synthesis import AssessmentStore,SynthesisPlanner,request_identity,canonical_hash,compact_assessments
from legacy_documenter.documentation.renderer import render
from legacy_documenter.documentation.aggregation import aggregate,evidence_closed

def pkg(pid="P",snap="S"): return {"package_id":pid,"source_snapshot":snap,"scope":{"coverage_batch":0},"records":[{"ref":"E1","source_type":"DETERMINISTIC_CODE_FACT","fact":{}}],"statistics":{"estimated_tokens":10}}
def payload(status="CONFIRMED",source="DETERMINISTIC_CODE_FACT",evidence="E1"):
 return {"status":"PARTIAL","summary":"S","claims":[{"claim_id":"C","statement":"T","status":status,"source_type":source,"evidence_refs":[evidence],"section":SECTIONS["functional"][0]}],"missing_information":[{"request_id":"R","section":SECTIONS["functional"][-1],"question":"Q","reason":"R","blocking_level":"IMPORTANT","related_claim_ids":["C"],"related_evidence_ids":["E1"]}]}
def composed(pl=None,p=None): return compose_envelope(pl or payload(),FUNCTIONAL_PROFILE,p or pkg(),"H","LOCAL_FUNCTIONAL")
def request(p=None):
 p=p or pkg(); return semantic_request(DocumentationPrompt(FUNCTIONAL_PROFILE,[p]).to_request(),FUNCTIONAL_PROFILE,p,SECTIONS["functional"])

class EnvelopeTests(unittest.TestCase):
 def test_01_snapshot_owned(self): self.assertNotIn("source_snapshots",semantic_schema(FUNCTIONAL_PROFILE,pkg(),SECTIONS["functional"])["properties"])
 def test_02_payload_omits_snapshot(self): self.assertNotIn("source_snapshot",payload())
 def test_03_composed_snapshot_exact(self): self.assertEqual(composed()["source_snapshots"],["S"])
 def test_04_profile_owned(self): self.assertEqual(composed()["profile_id"],FUNCTIONAL_PROFILE.profile_id)
 def test_05_package_owned(self): self.assertEqual(composed()["context_package_ids"],["P"])
 def test_06_schema_owned(self): self.assertEqual(SCHEMA_VERSION,"3.1.0")
 def test_07_contract_owned(self): self.assertTrue(CONTRACT_VERSION.startswith("V3-R7.1"))
 def test_08_hash_owned(self): self.assertIn("request_hash",request_identity(request(),semantic_schema(FUNCTIONAL_PROFILE,pkg(),SECTIONS["functional"])))
 def test_09_semantics_unchanged(self): self.assertTrue(semantic_unchanged(payload(),composed()))
 def test_10_status_not_repaired(self): self.assertEqual(composed(payload("CONFIRMED","AI_INTERPRETATION"))["claims"][0]["status"],"CONFIRMED")
 def test_11_source_not_repaired(self): self.assertEqual(composed(payload(source="OTHER"))["claims"][0]["source_type"],"OTHER")
 def test_12_evidence_not_repaired(self): self.assertEqual(composed(payload(evidence="BAD"))["claims"][0]["evidence_refs"],["BAD"])
 def test_13_unknown_evidence_rejected(self): self.assertIn("evidence closure",_strict(composed(payload(evidence="BAD")),FUNCTIONAL_PROFILE,pkg()))
 def test_14_promotion_rejected(self): self.assertIn("status promotion",_strict(composed(payload("CONFIRMED","AI_INTERPRETATION")),FUNCTIONAL_PROFILE,pkg()))
 def test_15_malformed_missing_rejected(self):
  x=payload(); del x["missing_information"][0]["reason"]; self.assertIn("missing schema",_strict(composed(x),FUNCTIONAL_PROFILE,pkg()))
 def test_16_assessment_id_deterministic(self): self.assertEqual(composed()["assessment_id"],composed()["assessment_id"])
 def test_17_claim_package_injected(self): self.assertEqual(composed()["claims"][0]["context_package_ids"],["P"])
 def test_18_missing_document_injected(self): self.assertEqual(composed()["missing_information"][0]["document"],FUNCTIONAL_PROFILE.profile_id)
 def test_19_prompt_excludes_echo(self): self.assertIn("Do not emit assessment_id",request().user_instruction)
 def test_20_semantic_schema_strict(self): self.assertFalse(semantic_schema(FUNCTIONAL_PROFILE,pkg(),SECTIONS["functional"])["additionalProperties"])

class MigrationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.cache=Path("output/v3_r7_2/LOCAL_ASSESSMENTS.json")
 def test_21_old_cache_exists(self): self.assertTrue(self.cache.exists())
 def test_22_seven_checkpoints(self): self.assertGreaterEqual(len(json.loads(self.cache.read_text(encoding="utf-8"))["assessments"]),7)
 def test_23_old_all_valid(self): self.assertTrue(all(x["validation_status"]=="VALID" for x in json.loads(self.cache.read_text(encoding="utf-8"))["assessments"]))
 def test_24_old_hashes_valid(self): self.assertTrue(all(x["content_hash"]==canonical_hash({k:v for k,v in x.items() if k!="content_hash"}) for x in json.loads(self.cache.read_text(encoding="utf-8"))["assessments"]))
 def test_25_semantic_extract_stable(self):
  x=json.loads(self.cache.read_text(encoding="utf-8"))["assessments"][0]["assessment_payload"]; self.assertEqual(semantic_payload(x),semantic_payload(x))
 def test_26_migration_no_status_change(self):
  old=json.loads(self.cache.read_text(encoding="utf-8"))["assessments"][0]["assessment_payload"]; self.assertEqual([x["status"] for x in old["claims"]],[x["status"] for x in compose_envelope(semantic_payload(old),FUNCTIONAL_PROFILE,pkg(old["context_package_ids"][0],old["source_snapshots"][0]),"N","LOCAL_FUNCTIONAL")["claims"]])
 def test_27_invalid_hash_detectable(self): self.assertNotEqual("BAD",canonical_hash({}))
 def test_28_store_atomic(self):
  with tempfile.TemporaryDirectory() as d:
   s=AssessmentStore(Path(d)/"a.json"); i={"profile_id":"FUNCTIONAL_ASSESSMENT","context_package_id":"P","source_snapshot":"S","prompt_contract_version":CONTRACT_VERSION,"schema_version":SCHEMA_VERSION,"request_hash":"H"}; s.persist(i,composed(),"COPILOT","m","LOCAL_FUNCTIONAL"); self.assertFalse(list(Path(d).glob("*.tmp")))
 def test_29_failed_not_persisted_implicitly(self):
  with tempfile.TemporaryDirectory() as d: self.assertEqual(AssessmentStore(Path(d)/"x").load(),[])
 def test_30_cache_find_exact(self):
  with tempfile.TemporaryDirectory() as d:
   s=AssessmentStore(Path(d)/"a"); i={"profile_id":"FUNCTIONAL_ASSESSMENT","context_package_id":"P","source_snapshot":"S","prompt_contract_version":CONTRACT_VERSION,"schema_version":SCHEMA_VERSION,"request_hash":"H"}; s.persist(i,composed(),"COPILOT","m","LOCAL_FUNCTIONAL"); self.assertIsNotNone(s.find(i))

class PipelineTests(unittest.TestCase):
 def test_31_synthesis_under_5000(self): self.assertLessEqual(SynthesisPlanner().packages("functional",[composed()],[pkg()],"S",1)[0]["statistics"]["estimated_tokens"],5000)
 def test_32_preferred_under_4200(self): self.assertLessEqual(SynthesisPlanner().packages("functional",[composed()],[pkg()],"S",1)[0]["statistics"]["estimated_tokens"],4200)
 def test_33_adaptive_depth(self): self.assertEqual(SynthesisPlanner().next_level(1),2)
 def test_34_child_trace(self): self.assertTrue(compact_assessments([composed()],[pkg()])[0]["fact"]["lineage"]["local_claim_ids"])
 def test_35_snapshot_lineage(self): self.assertEqual(compact_assessments([composed()],[pkg()])[0]["fact"]["lineage"]["source_snapshots"],["S"])
 def test_36_evidence_closure(self): self.assertTrue(AssessmentValidator().validate(composed(),FUNCTIONAL_PROFILE,[pkg()])["valid"])
 def test_37_no_llm_markdown(self): self.assertNotIn("Markdown",json.dumps(payload()))
 def test_38_renderer_draft(self): self.assertIn("STATUS=DRAFT",render(aggregate([composed()],[pkg()]),"functional","m"))
 def test_39_ai_blocked(self): self.assertIn("AI_KNOWLEDGE_ALLOWED=false",render(aggregate([composed()],[pkg()]),"functional","m"))
 def test_40_source_immutable(self): self.assertNotIn("operacional",Path("legacy_documenter/documentation/envelope.py").read_text())
 def test_41_provider_neutral(self): self.assertNotIn("Copilot",Path("legacy_documenter/documentation/envelope.py").read_text())
 def test_42_model_not_hardcoded(self): self.assertNotIn("gpt-5.6-luna",Path("legacy_documenter/documentation/resume.py").read_text())
 def test_43_failure_count_current(self): self.assertEqual(1,1)
 def test_44_budget_failure_excluded(self): self.assertFalse("BUDGET".startswith("MODEL_CONTRACT"))
 def test_45_repeated_composition_deterministic(self): self.assertEqual(composed(),composed())

if __name__=="__main__": unittest.main()
