import json,unittest
from pathlib import Path
from legacy_documenter.documentation.coverage import CoveragePlanner,DIMENSIONS
from legacy_documenter.documentation.systematic import _package,_global_package,_global_rules
from legacy_documenter.documentation.aggregation import aggregate,hierarchical_aggregate,evidence_closed
from legacy_documenter.documentation.renderer import render

def local_claim(cid="C",status="CONFIRMED",source="DETERMINISTIC_CODE_FACT"):
 return {"claim_id":cid,"statement":"S","status":status,"source_type":source,"evidence_refs":["E1"],"context_package_ids":["P1"],"section":"Resumen funcional del aplicativo"}
def local_assessment(c=None): return {"claims":[c or local_claim()],"missing_information":[],"context_package_ids":["P1"]}
def local_package(pid="P1"):
 return {"package_id":pid,"source_snapshot":"SNAP","records":[{"ref":"E1"}],"provenance":{}}

class CoveragePlannerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.planner=CoveragePlanner(Path("output/v2_r5_1_full")); cls.plan=cls.planner.plan(); cls.batches=cls.planner.batches(cls.plan,8,35)
 def test_01_project_plan_deterministic(self): self.assertEqual(self.plan["projects"],self.planner.plan()["projects"])
 def test_02_all_projects_classified(self): self.assertEqual(len(self.plan["projects"]),self.plan["metrics"]["total_projects"])
 def test_03_states_valid(self): self.assertTrue(all(x["state"] in {"COVERED","PARTIALLY_COVERED","NO_USABLE_EVIDENCE","UNRESOLVED_OWNERSHIP"} for x in self.plan["projects"]))
 def test_04_batch_split_deterministic(self): self.assertEqual(self.batches,self.planner.batches(self.plan,8,35))
 def test_05_batch_limit(self): self.assertTrue(all(len(x)+1<=35 for x in self.batches))
 def test_06_p0_preserved(self): self.assertEqual({x["unit_id"] for x in self.plan["units"] if x["priority"]=="P0"},{x["unit_id"] for b in self.batches for x in b if x["priority"]=="P0"})
 def test_07_deterministic_grouping(self): self.assertTrue(all(x["provenance"]["deterministic"] for x in self.plan["units"]))
 def test_08_no_ai_grouping(self): self.assertNotIn("AI",json.dumps([x["provenance"] for x in self.plan["units"]]))
 def test_09_webform_accounting(self): self.assertEqual(self.plan["metrics"]["represented_webforms"],self.plan["metrics"]["total_webforms"])
 def test_10_flow_accounting(self): self.assertEqual(self.plan["metrics"]["represented_flows"],self.plan["metrics"]["total_flows"])
 def test_11_data_accounting(self): self.assertLessEqual(self.plan["metrics"]["linked_data_operations"],self.plan["metrics"]["total_data_operations"])
 def test_12_procedure_accounting(self): self.assertLessEqual(self.plan["metrics"]["linked_stored_procedures"],self.plan["metrics"]["total_stored_procedures"])
 def test_13_unresolved_accounting(self): self.assertEqual(self.plan["metrics"]["represented_unresolved_relationships"],self.plan["metrics"]["unresolved_relationships"])
 def test_14_representatives_deterministic(self): self.assertEqual([x["unit_id"] for x in self.plan["units"]],[x["unit_id"] for x in self.planner.plan()["units"]])
 def test_15_no_duplicate_units(self):
  ids=[x["unit_id"] for x in self.plan["units"]]; self.assertEqual(len(ids),len(set(ids)))
 def test_16_all_dimensions(self): self.assertTrue(set(DIMENSIONS)<=set(x["category"] for x in self.plan["units"]))
 def test_17_metrics_deterministic(self): self.assertEqual(self.plan["metrics"],self.planner.plan()["metrics"])
 def test_18_structural_interpretation_separate(self): self.assertIn("semantic_coverage_percent",self.plan["metrics"]["interpretation_coverage"])
 def test_19_v2_lookup_recorded(self): self.assertTrue(self.plan["v2_lookup_completed"])
 def test_20_package_budget(self):
  ps=[_package("functional",i,b,self.plan["snapshot"],self.plan["metrics"]) for i,b in enumerate(self.batches)]; self.assertTrue(all(p["statistics"]["estimated_tokens"]<=5000 for p in ps))

class HierarchyTests(unittest.TestCase):
 def test_21_invalid_local_excluded(self): self.assertEqual(aggregate([local_assessment(local_claim(source="BAD"))],[local_package()])["claims"],[])
 def test_22_status_preserved(self): self.assertEqual(aggregate([local_assessment(local_claim(status="INTERPRETED",source="AI_INTERPRETATION"))],[local_package()])["claims"][0]["status"],"INTERPRETED")
 def test_23_no_global_promotion(self):
  gp={"records":[{"ref":"L","source_type":"AI_INTERPRETATION","fact":{"status":"INTERPRETED"}}]}; result={"claims":[{"status":"CONFIRMED","evidence_refs":["L"]}]}; self.assertIn("global status promotion",_global_rules(result,gp))
 def test_24_missing_dedup(self):
  m={"request_id":"R","question":"Q","related_claim_ids":[],"related_evidence_ids":["E1"]}; self.assertEqual(len(aggregate([{"claims":[],"missing_information":[m]},{"claims":[],"missing_information":[m]}],[local_package()])["missing_information"]),1)
 def test_25_global_input_compact(self):
  gp=_global_package("functional",[local_assessment()],[local_package()],"SNAP",{}); self.assertEqual(len(gp["records"]),1)
 def test_26_hierarchical_closure(self):
  lp=local_package(); la=local_assessment(); gp=_global_package("functional",[la],[lp],"SNAP",{}); ref=gp["records"][0]["ref"]; ga={"claims":[{"claim_id":"G","statement":"S","status":"CONFIRMED","source_type":"DETERMINISTIC_CODE_FACT","evidence_refs":[ref],"context_package_ids":[gp["package_id"]],"section":"Resumen funcional del aplicativo"}],"missing_information":[],"context_package_ids":[gp["package_id"]]}; d=hierarchical_aggregate(ga,gp,[la],[lp],{}); self.assertTrue(evidence_closed(d))
 def test_27_global_local_traceability(self):
  lp=local_package(); la=local_assessment(); gp=_global_package("functional",[la],[lp],"SNAP",{}); ref=gp["records"][0]["ref"]; ga={"claims":[{"claim_id":"G","statement":"S","status":"CONFIRMED","source_type":"DETERMINISTIC_CODE_FACT","evidence_refs":[ref],"context_package_ids":[gp["package_id"]],"section":"Resumen funcional del aplicativo"}],"missing_information":[]}; d=hierarchical_aggregate(ga,gp,[la],[lp],{}); self.assertIn(ref,d["hierarchical_traceability"])
 def test_28_architecture_not_forced(self): self.assertNotIn("arquitectura confirmada",render(aggregate([local_assessment()],[local_package()]),"technical","m").lower())
 def test_29_draft_and_ai_gate(self):
  text=render(aggregate([local_assessment()],[local_package()]),"functional","m"); self.assertIn("STATUS=DRAFT",text); self.assertIn("AI_KNOWLEDGE_ALLOWED=false",text)
 def test_30_render_deterministic(self):
  d=aggregate([local_assessment()],[local_package()]); d["coverage_metrics"]={"structural_coverage":{},"interpretation_coverage":{}}; self.assertEqual(render(d,"functional","m"),render(d,"functional","m"))

if __name__=="__main__": unittest.main()
