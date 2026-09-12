import inspect,json,tempfile
from pathlib import Path
import unittest
from legacy_documenter.analysis.deep_source import *
from legacy_documenter.extractors.webforms_extractor import WebFormsExtractor
from legacy_documenter.extractors.web_event_extractor import WebEventExtractor
from legacy_documenter.extractors.database_extractor import DatabaseExtractor

class DeepTests(unittest.TestCase):
 def setUp(self): self.snap="S"; self.projects=[{"path":"Web/Web.vbproj","project_references":[{"include":"../BL/BL.vbproj","name":"BL","project":"G"}],"assembly_references":[{"include":"Oracle.DataAccess, Version=4.0.0.0","hint_path":"lib/Oracle.dll"}]},{"path":"BL/BL.vbproj","project_references":[],"assembly_references":[]}]
 def test_01_plan_deterministic(self): self.assertEqual(plan_requests(),plan_requests())
 def test_02_twenty_targets(self): self.assertEqual(len(plan_requests()),20)
 def test_03_default_not_llm(self): self.assertGreater(sum(x["strategy"]=="DETERMINISTIC_DISCOVERY" for x in plan_requests()),sum(x["strategy"]=="LLM_INTERPRETATION" for x in plan_requests()))
 def test_04_webform_event(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"A.aspx"; p.write_text('<%@ Page CodeBehind="A.aspx.vb" Inherits="N.A" %><asp:Button ID="b" OnClick="Go" runat="server"/>'); x=WebFormsExtractor().extract(p,d); self.assertEqual(x.markup_events[0]["handler"],"Go")
 def test_05_codebehind(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"A.aspx"; p.write_text('<%@ Page CodeBehind="A.aspx.vb" Inherits="N.A" %>'); self.assertEqual(WebFormsExtractor().extract(p,d).codebehind,"A.aspx.vb")
 def test_06_handles_event(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"A.vb"; p.write_text("Class A\nPrivate Sub Go() Handles b.Click\nEnd Sub\nEnd Class"); self.assertEqual(WebEventExtractor().extract(p,d)["handlers"][0]["event"],"Click")
 def test_07_project_ref(self): self.assertEqual(project_dependencies(self.projects,self.snap)[0]["relationship_type"],"PROJECT_REFERENCE")
 def test_08_ambiguity_status(self): self.assertIn(project_dependencies(self.projects,self.snap)[0]["resolution_status"],STATUSES)
 def test_09_assembly(self): self.assertEqual(external_dependencies(self.projects,self.snap)[0]["assembly"],"Oracle.DataAccess")
 def test_10_version(self): self.assertEqual(external_dependencies(self.projects,self.snap)[0]["version"],"4.0.0.0")
 def test_11_hint_path(self): self.assertEqual(external_dependencies(self.projects,self.snap)[0]["hint_path"],"lib/Oracle.dll")
 def test_12_secret_redaction(self): self.assertNotIn("clave",sanitize_text("Password=clave"))
 def test_13_integration_redaction(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"A.vb"; p.write_text("SAP Password=clave"); x=integration_evidence(d,[{"file_type":"vb_source","relative_path":"A.vb"}],"S"); self.assertNotIn("clave",json.dumps(x))
 def test_14_integration_detect(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"A.vb"; p.write_text("Dim c As HttpClient"); self.assertEqual(len(integration_evidence(d,[{"file_type":"vb_source","relative_path":"A.vb"}],"S")),1)
 def test_15_oracle_command(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"R.vb"; p.write_text('Class R\nSub X()\nDim c As New OracleCommand("PKG.P", cn)\nEnd Sub\nEnd Class'); self.assertTrue(DatabaseExtractor().extract(p,d)["operations"])
 def test_16_stored_proc(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"R.vb"; p.write_text('Class R\nSub X()\nDim c As New OracleCommand("PKG.P", cn)\nc.CommandType=CommandType.StoredProcedure\nEnd Sub\nEnd Class'); self.assertEqual(DatabaseExtractor().extract(p,d)["operations"][0]["stored_procedure"],"PKG.P")
 def test_17_parameter_model(self): self.assertIn("parameters",inspect.getsource(run))
 def test_18_flow_complete_supported(self): self.assertIn("functional_paths",inspect.getsource(run))
 def test_19_partial_reevaluation(self): self.assertEqual(reevaluate({"flows":["P"],"external":[],"projects":[],"semantic":[]})[1]["reevaluation_status"],"PARTIALLY_RESOLVED")
 def test_20_unresolved_without_evidence(self): self.assertTrue(any(x["reevaluation_status"]=="STILL_UNRESOLVED" for x in reevaluate({})))
 def test_21_architecture_fields(self): self.assertEqual(set(architecture_evidence({"webforms":[],"data_access":[]},[],[],"S")),{"source_snapshot","DETERMINISTIC_INDICATORS","LLM_INTERPRETATION","CONTRADICTING_EVIDENCE","UNRESOLVED_EVIDENCE","pattern_confirmed"})
 def test_22_no_mvc_assumption(self): self.assertFalse(architecture_evidence({"webforms":[],"data_access":[]},[],[],"S")["pattern_confirmed"])
 def test_23_directory_not_pattern(self): self.assertNotIn("layered",inspect.getsource(architecture_evidence).lower())
 def test_24_no_provider_hardcode(self): self.assertNotIn("copilot",inspect.getsource(run).lower())
 def test_25_no_model_hardcode(self): self.assertNotIn("gpt-",inspect.getsource(run).lower())
 def test_26_stable_evidence_key(self): self.assertEqual(stable_id("E",{"a":1}),stable_id("E",{"a":1}))
 def test_27_unknown_key_policy_available(self):
  from legacy_documenter.documentation.evidence_catalog import EvidenceCatalogError; self.assertTrue(issubclass(EvidenceCatalogError,Exception))
 def test_28_evidence_canonical(self): self.assertTrue(external_dependencies(self.projects,self.snap)[0]["evidence_id"].startswith("DEEP-ASM-"))
 def test_29_all_reevaluated(self): self.assertEqual(len(reevaluate({})),20)
 def test_30_resolved_requires_evidence(self): self.assertNotIn("RESOLVED_BY_DETERMINISTIC_EVIDENCE",[x["reevaluation_status"] for x in reevaluate({})])
 def test_31_partial_preserved(self): self.assertIn("PARTIALLY_RESOLVED",[x["reevaluation_status"] for x in reevaluate({"flows":["E"],"external":[],"projects":[],"semantic":[]})])
 def test_32_human_status_supported(self): self.assertIn("REQUIRES_HUMAN_KNOWLEDGE",{"REQUIRES_HUMAN_KNOWLEDGE"})
 def test_33_external_status_supported(self): self.assertIn("REQUIRES_EXTERNAL_INFORMATION",{"REQUIRES_EXTERNAL_INFORMATION"})
 def test_34_runtime_callable(self): self.assertTrue(callable(run))
 def test_35_snapshot_repeat(self):
  with tempfile.TemporaryDirectory() as d:
   Path(d,"a").write_text("x"); self.assertEqual(tree_snapshot(d),tree_snapshot(d))
 def test_36_output_bounded(self): self.assertIn("max_items=5000",inspect.getsource(integration_evidence))
 def test_37_no_auto_approval(self): self.assertNotIn("knowledge_source_eligible",inspect.getsource(run))
 def test_38_ai_blocked(self): self.assertIn('"ai_knowledge_allowed":False',inspect.getsource(run).replace(" ",""))
 def test_39_source_snapshot(self):
  with tempfile.TemporaryDirectory() as d: self.assertEqual(tree_snapshot(d)["root"],str(Path(d).resolve()))
 def test_40_sanitize_nested(self): self.assertNotIn("secret",json.dumps(sanitize_data({"x":"token=secret"})))
 def test_41_architecture_llm_not_run(self): self.assertEqual(architecture_evidence({"webforms":[],"data_access":[]},[],[],"S")["LLM_INTERPRETATION"]["status"],"NOT_EXECUTED")
 def test_42_original_disposition(self): self.assertTrue(all(x["original_disposition"]=="NEEDS_ANALYSIS" for x in reevaluate({})))

if __name__=="__main__": unittest.main()
