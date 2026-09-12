import hashlib
import inspect
import json
from pathlib import Path
import unittest

from legacy_documenter.documentation.consistency import *
from legacy_documenter.documentation.consistency_run import _inputs, run
from legacy_documenter.documentation.renderer import render
from legacy_documenter.documentation.synthesis import expand_document


ROOT = Path(__file__).parents[1]


def fact(value=1, scope=SYSTEM_TOTAL, name="total_projects", refs=("COV-SYSTEM-METRICS",)):
    return MetricFact(name, value, scope, "PROJECTS", "unique_projects", refs, "SNAP")


def missing(ref="A:R", question="¿Qué patrón arquitectónico aplica?", section="Patrón de diseño / arquitectura",
            level="IMPORTANT", evidence=("E1",), claims=("A:C",), packages=("P1",), snapshots=("S1",)):
    return {"source_request_ref": ref, "request_id": ref.split(":")[-1], "section": section,
            "question": question, "reason": "Falta evidencia determinista del patrón arquitectónico.",
            "blocking_level": level, "related_claim_refs": list(claims),
            "related_evidence_ids": list(evidence), "context_package_ids": list(packages),
            "source_snapshots": list(snapshots)}


class TestV3R724(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.coverage, cls.inputs = _inputs(ROOT)
        cls.index = build_metric_index(cls.coverage, cls.inputs["functional"][3][:8])
        cls.documents = {}
        cls.originals = {}
        for kind, (ga, gp, assessments, packages) in cls.inputs.items():
            doc = expand_document(ga, gp, assessments, packages, cls.coverage["metrics"])
            cls.originals[kind] = missing_records(assessments, packages)
            doc["missing_information"] = canonicalize_missing(cls.originals[kind], kind)
            cls.documents[kind] = qualify_quantitative_claims(doc, cls.index)

    def test_01_metric_serialization_deterministic(self):
        self.assertEqual(fact().to_dict(), fact().to_dict())

    def test_02_metric_scope_preserved(self): self.assertEqual(fact(scope=SYSTEM_LINKED).to_dict()["scope"], SYSTEM_LINKED)
    def test_03_metric_provenance_preserved(self): self.assertEqual(fact(refs=("E1", "P1")).to_dict()["source_refs"], ["E1", "P1"])
    def test_04_system_metric_from_coverage(self): self.assertTrue(any(x.metric_name == "total_projects" and x.value == 259 for x in self.index))
    def test_05_equivalent_same_pass(self): self.assertTrue(validate_equivalent(fact(), fact()))
    def test_06_equivalent_different_fail(self): self.assertFalse(validate_equivalent(fact(1), fact(2)))
    def test_07_different_scope_allowed(self): self.assertTrue(validate_equivalent(fact(1), fact(2, COVERAGE_PARTITION)))

    def test_08_different_scope_rendered(self):
        d = {**self.documents["technical"], "claims": [self.documents["technical"]["claims"][4]], "missing_information": []}
        self.assertIn("alcance=", render(d, "technical", "m"))

    def test_09_unresolved_not_system(self): self.assertEqual(resolve_claim_metrics({"statement":"Hay 77 elementos","evidence_refs":[],"source_snapshots":["S"]}, self.index)[0].scope, UNRESOLVED_SCOPE)
    def test_10_2009_not_silent_system(self): self.assertEqual(next(f for c in self.documents["technical"]["claims"] if c["claim_id"]=="C007" for f in c["metric_facts"])["scope"], COVERAGE_PARTITION)
    def test_11_674_not_silent_system(self): self.assertEqual(next(f for c in self.documents["technical"]["claims"] if c["claim_id"]=="C009" for f in c["metric_facts"])["scope"], COVERAGE_PARTITION)
    def test_12_authority_not_overwrite_partition(self): self.assertNotEqual(next(f for c in self.documents["technical"]["claims"] if c["claim_id"]=="C007" for f in c["metric_facts"])["value"], 19159)
    def test_13_quantitative_evidence(self): self.assertTrue(all(f["source_refs"] for c in self.documents["technical"]["claims"] for f in c["metric_facts"]))
    def test_14_quantitative_snapshot(self): self.assertTrue(all(f["source_snapshot"] for c in self.documents["technical"]["claims"] for f in c["metric_facts"]))

    def test_15_functional_family(self):
        x=missing(question="¿Qué WebForm es punto de entrada de cada flujo?",section="Flujos funcionales identificados"); self.assertEqual(classify_missing(x,"functional"),"FUNCTIONAL_ENTRY_FLOW_MAPPING")
    def test_16_architecture_family(self): self.assertEqual(classify_missing(missing(),"technical"),"TECHNICAL_ARCHITECTURE_PATTERN")
    def test_17_project_dependency_family(self):
        x=missing(question="¿Qué referencias y dependencias existen entre proyectos?",section="Dependencias entre proyectos"); self.assertEqual(classify_missing(x,"technical"),"TECHNICAL_PROJECT_DEPENDENCIES")
    def test_18_external_dependency_family(self):
        x=missing(question="¿Qué paquetes externos, versiones y ensamblados se usan?",section="Dependencias externas y ensamblados"); self.assertEqual(classify_missing(x,"technical"),"TECHNICAL_EXTERNAL_DEPENDENCIES")
    def test_19_end_to_end_family(self):
        x=missing(question="¿Qué recorrido de flujo une punto de entrada y punto final?",section="Flujos técnicos representativos"); self.assertEqual(classify_missing(x,"technical"),"TECHNICAL_END_TO_END_FLOW")
    def test_20_uncertain_separate(self):
        x=missing(question="¿Qué falta?",section="Otra"); x["reason"]="No determinado."; self.assertIsNone(classify_missing(x,"technical"))
    def test_21_same_family_merges(self): self.assertEqual(len(canonicalize_missing([missing("A:R"),missing("B:R")],"technical")),1)
    def test_22_different_families_separate(self):
        ext=missing("B:R","¿Qué paquetes externos, versiones y ensamblados se usan?","Dependencias externas y ensamblados"); self.assertEqual(len(canonicalize_missing([missing(),ext],"technical")),2)
    def test_23_preserves_source_ids(self): self.assertEqual(len(canonicalize_missing([missing("A:R"),missing("B:R")],"technical")[0]["source_request_ids"]),2)
    def test_24_preserves_evidence(self): self.assertEqual(canonicalize_missing([missing(evidence=("E1",)),missing("B:R",evidence=("E2",))],"technical")[0]["related_evidence_ids"],["E1","E2"])
    def test_25_preserves_claims(self): self.assertEqual(len(canonicalize_missing([missing(claims=("A:C",)),missing("B:R",claims=("B:C",))],"technical")[0]["related_claim_ids"]),2)
    def test_26_preserves_packages(self): self.assertEqual(len(canonicalize_missing([missing(packages=("P1",)),missing("B:R",packages=("P2",))],"technical")[0]["context_package_ids"]),2)
    def test_27_preserves_snapshots(self): self.assertEqual(len(canonicalize_missing([missing(snapshots=("S1",)),missing("B:R",snapshots=("S2",))],"technical")[0]["source_snapshots"]),2)
    def test_28_strongest_blocking(self): self.assertEqual(canonicalize_missing([missing(level="INFORMATIONAL"),missing("B:R",level="BLOCKING_FOR_APPROVAL")],"technical")[0]["blocking_level"],"BLOCKING_FOR_APPROVAL")
    def test_29_original_levels(self): self.assertEqual(canonicalize_missing([missing(level="IMPORTANT"),missing("B:R",level="BLOCKING_FOR_APPROVAL")],"technical")[0]["original_blocking_levels"],["IMPORTANT","BLOCKING_FOR_APPROVAL"])
    def test_30_functional_ids(self): self.assertTrue(all(x["request_id"].startswith("FMI-") for x in self.documents["functional"]["missing_information"]))
    def test_31_technical_ids(self): self.assertTrue(all(x["request_id"].startswith("TMI-") for x in self.documents["technical"]["missing_information"]))
    def test_32_duplicate_local_ids_safe(self): self.assertEqual(len({x["source_request_ref"] for x in self.originals["technical"]}),len(self.originals["technical"]))
    def test_33_canonical_order(self): self.assertEqual([x["request_id"] for x in self.documents["technical"]["missing_information"]],sorted(x["request_id"] for x in self.documents["technical"]["missing_information"]))
    def test_34_no_llm_dedup(self): self.assertNotIn("llm", inspect.getsource(canonicalize_missing).lower())
    def test_35_no_llm_metrics(self): self.assertNotIn("provider", inspect.getsource(resolve_claim_metrics).lower())
    def test_36_no_llm_renderer(self): self.assertNotIn("generate", inspect.getsource(render).lower())

    def test_37_global_statements_unchanged(self):
        ga=self.inputs["technical"][0]; self.assertEqual([x["statement"] for x in ga["claims"]],[x["statement"] for x in self.documents["technical"]["claims"]])
    def test_38_status_not_promoted(self):
        ga=self.inputs["technical"][0]; self.assertEqual([x["status"] for x in ga["claims"]],[x["status"] for x in self.documents["technical"]["claims"]])
    def test_39_source_type_preserved(self):
        ga=self.inputs["technical"][0]; self.assertEqual([x["source_type"] for x in ga["claims"]],[x["source_type"] for x in self.documents["technical"]["claims"]])
    def test_40_conflict_provenance(self): self.assertIn("COV-DATA_ACCESS",json.dumps(self.documents["technical"]["claims"],ensure_ascii=False))
    def test_41_functional_coverage(self): self.assertEqual(self.documents["functional"]["coverage_metrics"]["total_projects"],259)
    def test_42_technical_coverage(self): self.assertEqual(self.documents["technical"]["coverage_metrics"]["linked_stored_procedures"],5389)
    def test_43_structural_semantic_distinction(self): self.assertIn("INTERPRETATION_COVERAGE",render(self.documents["functional"],"functional","m"))
    def test_44_traceability_closure(self): self.assertTrue(traceability_closed(self.documents["technical"]["missing_information"],self.originals["technical"]))
    def test_45_no_dangling_original_refs(self):
        self.assertEqual({x["source_request_ref"] for x in self.originals["functional"]},{r for x in self.documents["functional"]["missing_information"] for r in x["source_request_ids"]})
    def test_46_functional_draft(self): self.assertIn("document_status=DRAFT",render(self.documents["functional"],"functional","m"))
    def test_47_technical_draft(self): self.assertIn("STATUS=DRAFT",render(self.documents["technical"],"technical","m"))
    def test_48_human_review(self): self.assertIn("HUMAN_REVIEW_REQUIRED=true",render(self.documents["functional"],"functional","m"))
    def test_49_not_knowledge_eligible(self): self.assertIn("knowledge_source_eligible=false",render(self.documents["functional"],"functional","m"))
    def test_50_ai_knowledge_blocked(self): self.assertIn("AI_KNOWLEDGE_ALLOWED=false",render(self.documents["technical"],"technical","m"))
    def test_51_legacy_source_not_targeted(self): self.assertNotIn("source\\IST_40",inspect.getsource(run))

    def test_52_v2_read_only(self):
        source=inspect.getsource(run)+inspect.getsource(_inputs); self.assertNotIn("v2_r5_1_full\").write",source)

    def run_without_persisting_documents(self):
        paths = [ROOT/"output/LEVANTAMIENTO_FUNCIONAL.md", ROOT/"output/LEVANTAMIENTO_TECNICO.md"]
        originals = {path: path.read_bytes() for path in paths}
        try:
            return run(ROOT)
        finally:
            for path, content in originals.items():
                path.write_bytes(content)

    def test_53_local_unchanged(self):
        p=ROOT/"output/v3_r7_2/LOCAL_ASSESSMENTS.json"; before=hashlib.sha256(p.read_bytes()).digest(); self.run_without_persisting_documents(); self.assertEqual(before,hashlib.sha256(p.read_bytes()).digest())
    def test_54_synthesis_unchanged(self):
        p=ROOT/"output/v3_r7_2/INTERMEDIATE_ASSESSMENTS.json"; before=hashlib.sha256(p.read_bytes()).digest(); self.run_without_persisting_documents(); self.assertEqual(before,hashlib.sha256(p.read_bytes()).digest())
    def test_55_repeat_render_identical(self): self.assertEqual(render(self.documents["functional"],"functional","m"),render(self.documents["functional"],"functional","m"))
    def test_56_zero_provider_calls(self): self.assertEqual(self.run_without_persisting_documents()["calls"],0)
    def test_57_model_policy_unaffected(self): self.assertNotIn("discover_model",inspect.getsource(run))
    def test_58_functional_reduced(self): self.assertLess(len(self.documents["functional"]["missing_information"]),len(self.originals["functional"]))
    def test_59_technical_reduced(self): self.assertLess(len(self.documents["technical"]["missing_information"]),len(self.originals["technical"]))
    def test_60_quantitative_consistency(self): self.assertTrue(all(validate_quantitative_consistency(x) for x in self.documents.values()))


if __name__ == "__main__":
    unittest.main()
