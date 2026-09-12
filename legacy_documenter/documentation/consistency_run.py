"""Offline V3-R7.2.4 execution using only validated persisted assessments."""
import json
from pathlib import Path

from legacy_documenter.documentation.aggregation import evidence_closed
from legacy_documenter.documentation.consistency import (build_metric_index, canonicalize_missing,
    missing_records, qualify_quantitative_claims, traceability_closed, validate_quantitative_consistency)
from legacy_documenter.documentation.coverage import CoveragePlanner
from legacy_documenter.documentation.interpretation import FUNCTIONAL_PROFILE, TECHNICAL_PROFILE
from legacy_documenter.documentation.renderer import render
from legacy_documenter.documentation.synthesis import AssessmentStore, SynthesisPlanner, expand_document
from legacy_documenter.documentation.systematic import _package


def _entry_map(path):
    return {x["context_package_id"]: x["assessment_payload"] for x in AssessmentStore(path).load()}


def _inputs(workspace):
    root = workspace / "output" / "v2_r5_1_full"
    planner = CoveragePlanner(root)
    coverage = planner.plan()
    batches = planner.batches(coverage, 8, 35)
    profiles = {"functional": FUNCTIONAL_PROFILE, "technical": TECHNICAL_PROFILE}
    leaf = {kind: [_package(kind, i, batch, coverage["snapshot"], coverage["metrics"])
                  for i, batch in enumerate(batches)] for kind in profiles}
    local_map = _entry_map(workspace / "output" / "v3_r7_2" / "LOCAL_ASSESSMENTS.json")
    synthesis_map = _entry_map(workspace / "output" / "v3_r7_2" / "INTERMEDIATE_ASSESSMENTS.json")
    synth = SynthesisPlanner()
    result = {}
    for kind in profiles:
        local_a = [local_map[p["package_id"]] for p in leaf[kind]]
        level_one = synth.packages(kind, local_a, leaf[kind], coverage["snapshot"], 1, coverage["metrics"])
        intermediate = [synthesis_map[p["package_id"]] for p in level_one]
        global_packages = synth.packages(kind, intermediate, level_one, coverage["snapshot"], 2, coverage["metrics"])
        if len(global_packages) != 1:
            raise ValueError("VALIDATED_HIERARCHY_MISMATCH")
        global_a = synthesis_map[global_packages[0]["package_id"]]
        result[kind] = (global_a, global_packages[0], local_a + intermediate + [global_a],
                        leaf[kind] + level_one + global_packages)
    return coverage, result


def run(workspace="."):
    """Performs run while preserving this module's deterministic contract."""
    workspace = Path(workspace)
    coverage, inputs = _inputs(workspace)
    all_leaf_packages = inputs["functional"][3][:8]
    metric_index = build_metric_index(coverage, all_leaf_packages)
    documents = {}
    input_counts = {}
    output_counts = {}
    for kind, (global_a, global_p, assessments, packages) in inputs.items():
        document = expand_document(global_a, global_p, assessments, packages, coverage["metrics"])
        originals = missing_records(assessments, packages)
        canonical = canonicalize_missing(originals, kind)
        if not traceability_closed(canonical, originals):
            raise ValueError("TRACEABILITY_FAILURE")
        document["missing_information"] = canonical
        document = qualify_quantitative_claims(document, metric_index)
        if not evidence_closed(document) or not validate_quantitative_consistency(document):
            raise ValueError("METRIC_CONSISTENCY_FAILURE")
        model = "gpt-5.6-luna"
        text = render(document, kind, model)
        path = workspace / "output" / ("LEVANTAMIENTO_FUNCIONAL.md" if kind == "functional" else "LEVANTAMIENTO_TECNICO.md")
        path.write_text(text, encoding="utf-8")
        documents[kind] = {"path": str(path), "bytes": len(text.encode()), "claims": len(document["claims"]),
                           "missing": len(canonical), "closed": True}
        input_counts[kind] = len(originals)
        output_counts[kind] = len(canonical)
    return {"status": "V3-R7_2_4_READY_FOR_HUMAN_REVIEW", "calls": 0,
            "documents": documents, "missing_input": input_counts, "missing_output": output_counts,
            "metric_facts": len(metric_index)}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, sort_keys=True, indent=2))
