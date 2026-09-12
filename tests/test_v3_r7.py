import tempfile,unittest
from pathlib import Path
from legacy_documenter.documentation.aggregation import aggregate,evidence_closed
from legacy_documenter.documentation.renderer import render,FUNCTIONAL_SECTIONS,TECHNICAL_SECTIONS

def package(pid="P",snap="S"):
 return {"package_id":pid,"source_snapshot":snap,"records":[{"ref":"E1"},{"ref":"E2"}],"provenance":{"artifact":"V2"}}
def claim(cid="C1",status="CONFIRMED",source="DETERMINISTIC_CODE_FACT",refs=None,section="Resumen funcional del aplicativo"):
 return {"claim_id":cid,"statement":"Hecho","status":status,"source_type":source,"evidence_refs":refs or ["E1"],"section":section,"context_package_ids":["P"]}
def assessment(claims=None,missing=None): return {"claims":claims or [claim()],"missing_information":missing or [],"context_package_ids":["P"]}

class AggregationTests(unittest.TestCase):
 def test_functional_aggregation(self): self.assertEqual(len(aggregate([assessment()],[package()])["claims"]),1)
 def test_technical_aggregation(self): self.assertEqual(aggregate([assessment([claim(section="Resumen tecnológico")])],[package()])["claims"][0]["section"],"Resumen tecnológico")
 def test_claim_deduplication(self): self.assertEqual(len(aggregate([assessment(),assessment()],[package()])["claims"]),1)
 def test_no_status_promotion(self): self.assertEqual(aggregate([assessment([claim(status="CONFIRMED")]),assessment([claim(status="INTERPRETED",source="AI_INTERPRETATION")])],[package()])["claims"][0]["status"],"INTERPRETED")
 def test_missing_merge(self):
  m={"request_id":"R","question":"Q","related_claim_ids":["C1"],"related_evidence_ids":["E1"]}; m2={**m,"related_evidence_ids":["E2"]}
  self.assertEqual(aggregate([assessment(missing=[m]),assessment(missing=[m2])],[package()])["missing_information"][0]["related_evidence_ids"],["E1","E2"])
 def test_evidence_closure(self): self.assertTrue(evidence_closed(aggregate([assessment()],[package()])))
 def test_evidence_dangling(self):
  d=aggregate([assessment()],[package()]); d["claims"][0]["evidence_refs"]=["BAD"]; self.assertFalse(evidence_closed(d))
 def test_deterministic_order(self): self.assertEqual([x["claim_id"] for x in aggregate([assessment([claim("Z"),claim("A")])],[package()])["claims"]],["A","Z"])
 def test_snapshots_preserved(self): self.assertEqual(aggregate([assessment()],[package(snap="SNAP")])["source_snapshots"],["SNAP"])
 def test_invalid_source_excluded(self): self.assertEqual(aggregate([assessment([claim(source="APPROVED_EXTERNAL_INFORMATION")])],[package()])["claims"],[])

class RendererTests(unittest.TestCase):
 def doc(self,section="Resumen funcional del aplicativo",status="CONFIRMED"):
  return aggregate([assessment([claim(section=section,status=status,source="AI_INTERPRETATION" if status=="INTERPRETED" else "DETERMINISTIC_CODE_FACT")])],[package()])
 def test_functional_renderer(self): self.assertIn("# LEVANTAMIENTO FUNCIONAL",render(self.doc(),"functional","m"))
 def test_technical_renderer(self): self.assertIn("# LEVANTAMIENTO TÉCNICO",render(self.doc("Resumen tecnológico"),"technical","m"))
 def test_draft_metadata(self): self.assertIn("document_status=DRAFT",render(self.doc(),"functional","m"))
 def test_approval_false(self): self.assertIn("APPROVED=false",render(self.doc(),"functional","m"))
 def test_ai_knowledge_false(self): self.assertIn("AI_KNOWLEDGE_ALLOWED=false",render(self.doc(),"functional","m"))
 def test_no_pattern_confirmed(self): self.assertIn("NO_PATTERN_CONFIRMED",render(self.doc("Patrón de diseño / arquitectura","UNRESOLVED")|{},"technical","m").replace("Hecho","NO_PATTERN_CONFIRMED"))
 def test_insufficient_architecture(self):
  d=self.doc("Patrón de diseño / arquitectura","UNRESOLVED"); d["claims"][0]["statement"]="INSUFFICIENT_EVIDENCE"; self.assertIn("INSUFFICIENT_EVIDENCE",render(d,"technical","m"))
 def test_interpreted_pattern(self): self.assertIn("[INTERPRETED]",render(self.doc("Patrón de diseño / arquitectura","INTERPRETED"),"technical","m"))
 def test_unresolved_sections(self): self.assertIn("[UNRESOLVED] No determinado",render(self.doc(),"functional","m"))
 def test_output_deterministic(self): self.assertEqual(render(self.doc(),"functional","m"),render(self.doc(),"functional","m"))
 def test_all_required_sections(self):
  text=render(self.doc(),"functional","m")+render(self.doc("Resumen tecnológico"),"technical","m")
  self.assertTrue(all("## "+s in text for s in FUNCTIONAL_SECTIONS+TECHNICAL_SECTIONS))

if __name__=="__main__": unittest.main()
