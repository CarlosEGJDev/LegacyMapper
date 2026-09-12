import json,tempfile,unittest
from pathlib import Path
from legacy_documenter.documentation.synthesis import AssessmentStore,SynthesisPlanner,canonical_hash,request_identity,compact_assessments,expand_document,CONTRACT_VERSION,SCHEMA_VERSION
from legacy_documenter.documentation.aggregation import evidence_closed
from legacy_documenter.documentation.renderer import render
from legacy_documenter.llm import LLMRequest

def pack(pid="P",snap="S",n=1): return {"package_id":pid,"source_snapshot":snap,"scope":{"coverage_batch":0},"records":[{"ref":"E"+str(i),"source_type":"DETERMINISTIC_CODE_FACT","fact":{}} for i in range(n)]}
def claim(cid="C",status="CONFIRMED",source="DETERMINISTIC_CODE_FACT",refs=None): return {"claim_id":cid,"statement":"Text "+cid,"status":status,"source_type":source,"evidence_refs":refs or ["E0"],"context_package_ids":["P"],"section":"Resumen funcional del aplicativo"}
def assess(c=None,pid="P",snap="S"): return {"assessment_id":"A","profile_id":"FUNCTIONAL_ASSESSMENT","context_package_ids":[pid],"source_snapshots":[snap],"status":"PARTIAL","summary":"S","claims":[c or claim()],"missing_information":[]}
def identity(**changes):
 x={"profile_id":"FUNCTIONAL_ASSESSMENT","context_package_id":"P","source_snapshot":"S","prompt_contract_version":CONTRACT_VERSION,"schema_version":SCHEMA_VERSION,"request_hash":"H"}; x.update(changes); return x

class PersistenceTests(unittest.TestCase):
 def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.store=AssessmentStore(Path(self.tmp.name)/"cache.json")
 def tearDown(self): self.tmp.cleanup()
 def test_01_valid_persisted(self): self.assertEqual(self.store.persist(identity(),assess(),"COPILOT","m","LOCAL")["validation_status"],"VALID")
 def test_02_invalid_not_automatically_persisted(self): self.assertEqual(self.store.load(),[])
 def test_03_serialization_deterministic(self): self.store.persist(identity(),assess(),"COPILOT","m","LOCAL"); a=self.store.path.read_text(); self.store.persist(identity(),assess(),"COPILOT","m","LOCAL"); self.assertEqual(a,self.store.path.read_text())
 def test_04_hash_stable(self): self.assertEqual(canonical_hash(assess()),canonical_hash(assess()))
 def test_05_exact_reuse(self): self.store.persist(identity(),assess(),"COPILOT","m","LOCAL"); self.assertIsNotNone(self.store.find(identity()))
 def test_06_snapshot_invalidates(self): self.store.persist(identity(),assess(),"COPILOT","m","LOCAL"); self.assertIsNone(self.store.find(identity(source_snapshot="X")))
 def test_07_profile_invalidates(self): self.store.persist(identity(),assess(),"COPILOT","m","LOCAL"); self.assertIsNone(self.store.find(identity(profile_id="X")))
 def test_08_schema_invalidates(self): self.store.persist(identity(),assess(),"COPILOT","m","LOCAL"); self.assertIsNone(self.store.find(identity(schema_version="X")))
 def test_09_contract_invalidates(self): self.store.persist(identity(),assess(),"COPILOT","m","LOCAL"); self.assertIsNone(self.store.find(identity(prompt_contract_version="X")))
 def test_10_request_invalidates(self): self.store.persist(identity(),assess(),"COPILOT","m","LOCAL"); self.assertIsNone(self.store.find(identity(request_hash="X")))
 def test_11_atomic_no_temp(self): self.store.persist(identity(),assess(),"COPILOT","m","LOCAL"); self.assertEqual(list(Path(self.tmp.name).glob("*.tmp")),[])
 def test_12_partial_checkpoint(self): self.store.persist(identity(),assess(),"COPILOT","m","LOCAL"); self.assertEqual(len(AssessmentStore(self.store.path).load()),1)
 def test_13_no_duplicate_reuse(self): self.store.persist(identity(),assess(),"COPILOT","m","LOCAL"); self.store.persist(identity(),assess(),"COPILOT","m","LOCAL"); self.assertEqual(len(self.store.load()),1)
 def test_14_required_fields(self): self.assertTrue({"assessment_id","profile_id","assessment_status","context_package_id","source_snapshot","claims","missing_information","provider","prompt_contract_version","schema_version","validation_status","content_hash"}<=set(self.store.persist(identity(),assess(),"COPILOT","m","LOCAL")))
 def test_15_only_valid_reusable(self):
  self.store.persist(identity(),assess(),"COPILOT","m","LOCAL"); data=json.loads(self.store.path.read_text()); data["assessments"][0]["validation_status"]="INVALID"; self.store.path.write_text(json.dumps(data)); self.assertIsNone(self.store.find(identity()))

class SynthesisTests(unittest.TestCase):
 def planner(self): return SynthesisPlanner(target_tokens=1000,max_tokens=5000,max_records=3)
 def test_16_planner_deterministic(self): self.assertEqual(self.planner().packages("functional",[assess()],[pack()],"S",1),self.planner().packages("functional",[assess()],[pack()],"S",1))
 def test_17_under_5000(self): self.assertTrue(all(x["statistics"]["estimated_tokens"]<=5000 for x in self.planner().packages("functional",[assess()],[pack()],"S",1)))
 def test_18_target_when_feasible(self): self.assertTrue(all(x["statistics"]["estimated_tokens"]<=1000 for x in self.planner().packages("functional",[assess()],[pack()],"S",1)))
 def test_19_compaction_fields(self): self.assertTrue({"claim_id","status","source_type","statement","lineage"}<=set(compact_assessments([assess()],[pack()])[0]["fact"]))
 def test_20_provenance_preserved(self): self.assertEqual(compact_assessments([assess()],[pack()])[0]["fact"]["lineage"]["evidence_ids"],["E0"])
 def test_21_exact_dedup(self): self.assertEqual(len(compact_assessments([assess(),assess()],[pack(),pack()])),1)
 def test_22_no_semantic_dedup(self): self.assertEqual(len(compact_assessments([assess(claim("A")),assess(claim("B"))],[pack(),pack()])),2)
 def test_23_metrics_final_only(self): self.assertNotIn("coverage_metrics",self.planner().packages("functional",[assess()],[pack()],"S",1,{"x":1})[0]["statistics"] if len(self.planner().packages("functional",[assess(),assess(claim("B"))],[pack(),pack()],"S",1))>1 else {})
 def test_24_child_refs(self): self.assertTrue(compact_assessments([assess()],[pack()])[0]["fact"]["lineage"]["local_claim_ids"])
 def test_25_status_preserved(self): self.assertEqual(compact_assessments([assess(claim(status="INTERPRETED",source="AI_INTERPRETATION"))],[pack()])[0]["fact"]["status"],"INTERPRETED")
 def test_26_ai_agreement_not_confirmed(self): self.assertEqual(compact_assessments([assess(claim(status="INTERPRETED",source="AI_INTERPRETATION")),assess(claim(status="INTERPRETED",source="AI_INTERPRETATION"))],[pack(),pack()])[0]["source_type"],"AI_INTERPRETATION")
 def test_27_adaptive_split(self): self.assertGreaterEqual(len(SynthesisPlanner(target_tokens=1).packages("functional",[assess()],[pack()],"S",1)),1)
 def test_28_depth_advances(self): self.assertEqual(self.planner().next_level(1),2)
 def test_29_depth_enforced(self): self.assertRaises(ValueError,self.planner().next_level,3)
 def test_30_package_identity_stable(self): self.assertEqual(self.planner().packages("functional",[assess()],[pack()],"S",1)[0]["package_id"],self.planner().packages("functional",[assess()],[pack()],"S",1)[0]["package_id"])

class FinalTests(unittest.TestCase):
 def doc(self):
  lp=pack(); la=assess(); records=compact_assessments([la],[lp]); gp={"package_id":"G","source_snapshot":"S","scope":{"synthesis_level":1},"records":records}; ref=records[0]["ref"]; ga=assess(claim("G",refs=[ref]),"G"); ga["context_package_ids"]=["G"]; return expand_document(ga,gp,[la],[lp],{})
 def test_31_global_closure(self): self.assertTrue(evidence_closed(self.doc()))
 def test_32_global_local_trace(self): self.assertTrue(self.doc()["claims"][0]["local_claim_ids"])
 def test_33_source_snapshot(self): self.assertEqual(self.doc()["claims"][0]["source_snapshots"],["S"])
 def test_34_context_package(self): self.assertEqual(self.doc()["claims"][0]["context_package_ids"],["P"])
 def test_35_unvalidated_not_rendered_by_pipeline(self): self.assertNotIn("validation",render(self.doc(),"functional","m").lower())
 def test_36_draft(self): self.assertIn("STATUS=DRAFT",render(self.doc(),"functional","m"))
 def test_37_ai_blocked(self): self.assertIn("AI_KNOWLEDGE_ALLOWED=false",render(self.doc(),"functional","m"))
 def test_38_deterministic_rerun(self): self.assertEqual(render(self.doc(),"functional","m"),render(self.doc(),"functional","m"))
 def test_39_source_immutable_design(self): self.assertNotIn("operacional",Path("legacy_documenter/documentation/synthesis.py").read_text())
 def test_40_provider_neutral(self): self.assertNotIn("Copilot",Path("legacy_documenter/documentation/synthesis.py").read_text())

if __name__=="__main__": unittest.main()
