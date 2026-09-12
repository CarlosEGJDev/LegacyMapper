import hashlib
import inspect
import json
from pathlib import Path
import unittest

from legacy_documenter.knowledge.readiness import *
from legacy_documenter.knowledge.readiness import _hash, _safe

ROOT = Path(__file__).parents[1]


class KnowledgeReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run(ROOT)
        cls.f = (ROOT / "output/LEVANTAMIENTO_FUNCIONAL.md").read_text(encoding="utf-8")
        cls.t = (ROOT / "output/LEVANTAMIENTO_TECNICO.md").read_text(encoding="utf-8")
        cls.htext = (ROOT / "codex/V3/V3_R8_4_REVISION_HUMANA_APROBADA.md").read_text(encoding="utf-8")
        cls.review = parse_human_record(cls.htext)
        cls.projection = json.loads((ROOT / "output/v3_r9/KNOWLEDGE_PROJECTION.json").read_text(encoding="utf-8"))["records"]
        cls.boundary = json.loads((ROOT / "output/v3_r9/KNOWLEDGE_BOUNDARY.json").read_text(encoding="utf-8"))
        cls.trace = json.loads((ROOT / "output/v3_r9/READINESS_TRACEABILITY.json").read_text(encoding="utf-8"))

    def test_01_functional_approved_required(self): self.assertIn("document_status=APPROVED", self.f)
    def test_02_technical_approved_required(self): self.assertIn("document_status=APPROVED", self.t)
    def test_03_functional_eligible(self): self.assertIn("knowledge_source_eligible=true", self.f)
    def test_04_technical_eligible(self): self.assertIn("knowledge_source_eligible=true", self.t)
    def test_05_complete_review(self): self.assertEqual(len(self.review["decisions"]), 20)
    def test_06_exact_dispositions(self): self.assertEqual(self.review["decisions"], EXPECTED)
    def test_07_c04(self): self.assertEqual(self.review["c04"], "HUMAN_CONFIRMED")
    def test_08_fmi008(self): self.assertEqual(self.review["decisions"]["FMI-008"], "HUMAN_CONFIRMED")
    def test_09_tmi002(self): self.assertEqual(self.review["decisions"]["TMI-002"], "HUMAN_CONFIRMED")
    def test_10_tmi005(self): self.assertEqual(self.review["decisions"]["TMI-005"], "HUMAN_CONFIRMED")
    def test_11_partial_exact(self): self.assertEqual({x for x,v in self.review["decisions"].items() if v=="ACCEPTED_AS_PARTIAL"}, PARTIAL)
    def test_12_external_exact(self): self.assertEqual({x for x,v in self.review["decisions"].items() if v=="ACCEPTED_AS_UNRESOLVED_EXTERNAL"}, EXTERNAL)
    def test_13_external_exhausted(self): self.assertEqual(self.review["external_exhausted"], EXTERNAL)
    def test_14_external_does_not_block(self): self.assertEqual(self.result["readiness"], "READY")
    def test_15_claim_authority(self): self.assertTrue(self.result["checks"]["claim_integrity"])
    def test_16_interpreted_preserved(self): self.assertTrue(any(x["semantic_status"]=="INTERPRETED" for x in self.projection))
    def test_17_unresolved_preserved(self): self.assertTrue(any(x["semantic_status"]=="UNRESOLVED" for x in self.projection))
    def test_18_evidence_closure(self): self.assertTrue(self.result["checks"]["evidence_closure"])
    def test_19_snapshot_closure(self): self.assertFalse(self.trace["unresolved_aliases"]["snapshots"])
    def test_20_assessment_closure(self): self.assertFalse(self.trace["unresolved_aliases"]["assessments"])
    def test_21_no_aliases(self): self.assertTrue(all(not x for x in self.trace["unresolved_aliases"].values()))
    def test_22_quantitative(self): self.assertTrue(self.result["checks"]["quantitative_integrity"])
    def test_23_scopes(self): self.assertTrue(quantitative_valid({"f":self.f,"t":self.t}))
    def test_24_architecture_uncertain(self): self.assertIn("No se encontró declaración formal autoritativa", self.htext)
    def test_25_mvc_not_inferred(self): self.assertIn("MVC no está establecido", self.htext)
    def test_26_no_formal_architecture(self): self.assertIn("no permite confirmar un patrón", self.t)
    def test_27_projection_classification(self): self.assertTrue({x["knowledge_eligibility"] for x in self.projection} <= {"ELIGIBLE_FACT","ELIGIBLE_INTERPRETATION","ELIGIBLE_PARTIAL","ELIGIBLE_UNRESOLVED_LIMITATION","INELIGIBLE"})
    def test_28_unresolved_projection(self): self.assertEqual({x["source_claim_id"] for x in self.projection if x["knowledge_eligibility"]=="ELIGIBLE_UNRESOLVED_LIMITATION"}, EXTERNAL)
    def test_29_boundary(self): self.assertTrue(self.result["checks"]["knowledge_boundary"])
    def test_30_prohibited(self): self.assertEqual(self.boundary["WHAT_IS_NOT_ALLOWED_TO_BE_ASSERTED"], PROHIBITED_ASSERTIONS)
    def test_31_unsupported_ineligible(self): self.assertGreater(self.result["ineligible_records"], 0)
    def test_32_secrets_excluded(self): self.assertTrue(_safe(self.projection))
    def test_33_no_llm(self): self.assertEqual(self.result["real_llm_calls"], 0)
    def test_34_no_provider(self): self.assertNotIn("provider.", inspect.getsource(run).lower())
    def test_35_no_source_access(self): self.assertNotIn("operacional", inspect.getsource(run))
    def test_36_previous_evidence_immutable(self):
        files=[p for d in ("v3_r8_1","v3_r8_2","v3_r8_3") for p in (ROOT/"output"/d).rglob("*") if p.is_file()]; before={p:_hash(p) for p in files}; run(ROOT); self.assertEqual(before,{p:_hash(p) for p in files})
    def test_37_document_immutable(self):
        files=[ROOT/"output/LEVANTAMIENTO_FUNCIONAL.md",ROOT/"output/LEVANTAMIENTO_TECNICO.md"]; before=[_hash(p) for p in files]; run(ROOT); self.assertEqual(before,[_hash(p) for p in files])
    def test_38_ready_flag(self): self.assertTrue(self.result["ai_knowledge_allowed"])
    def test_39_nonready_flag(self): self.assertFalse(validate_preconditions(self.f.replace("document_status=APPROVED","document_status=DRAFT"),self.t,self.review))
    def test_40_not_generated(self): self.assertFalse(self.result["ai_knowledge_generated"])
    def test_41_deterministic(self):
        files=sorted((ROOT/"output/v3_r9").glob("*.json")); before=[_hash(p) for p in files]; run(ROOT); self.assertEqual(before,[_hash(p) for p in files])
    def test_42_regression_status(self): self.assertEqual(self.result["status"], "V3-R9_KNOWLEDGE_READINESS_GATE_COMPLETE")
    def test_43_projection_fields(self): self.assertTrue(all({"record_id","source_document","source_claim_id","semantic_status","human_disposition","statement","evidence_ids","source_snapshot_ids","provenance_type","uncertainty","knowledge_eligibility"} <= set(x) for x in self.projection))
    def test_44_no_ai_knowledge_artifact(self): self.assertFalse((ROOT/"output/v3_r9/AI_KNOWLEDGE.json").exists())
    def test_45_c04_provenance(self): self.assertEqual(next(x for x in self.projection if x["record_id"]=="KR-FUNCTIONAL-C04")["provenance_type"], "HUMAN_REVIEW_CONFIRMED_INTERPRETATION")


if __name__ == "__main__": unittest.main()
