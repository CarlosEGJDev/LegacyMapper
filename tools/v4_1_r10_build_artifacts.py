"""Builds output/v4_1_r10/V4_1_FINAL_BASELINE.json and V4_1_FINAL_MANIFEST.json deterministically.

Not part of the production package; a one-off generator script for the
V4.1-R10 final baseline/manifest, following the pattern of the earlier
tools/v4_1_r*_build_artifact.py scripts. No production code is read or
modified; only repository-relative paths and content hashes of existing,
already-approved artifacts are recorded.
"""
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "output" / "v4_1_r10"
BASELINE_PATH = OUT_DIR / "V4_1_FINAL_BASELINE.json"
MANIFEST_PATH = OUT_DIR / "V4_1_FINAL_MANIFEST.json"


def sha256_of(rel_path: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel_path).read_bytes()).hexdigest()


def build_baseline() -> dict:
    return {
        "version": "V4.1",
        "status": "READY_FOR_TECHNICAL_LEAD_FINAL_APPROVAL",
        "v4_status": "FORMALLY_CLOSED",
        "approved_rounds": {
            "r0": "APPROVED",
            "r1": "APPROVED",
            "r2": "APPROVED",
            "r3": "APPROVED",
            "r4": "APPROVED",
            "r5": "APPROVED",
            "r6": "APPROVED",
            "r7": "APPROVED",
            "r8": "APPROVED",
            "r9": "APPROVED",
        },
        "tests": "1566_PASS_0_FAIL_0_SKIP",
        "readiness": "READY",
        "behavior": {
            "refactor_goal": "READABILITY_AND_MAINTAINABILITY",
            "behavior_change_forbidden": True,
            "production_behavior_changed": False,
        },
        "compatibility": {
            "public_imports": "PASS",
            "public_signatures": "PASS",
            "positional_calls": "PASS",
            "keyword_calls": "PASS",
            "deterministic_identifiers": "PASS",
            "deterministic_ordering": "PASS",
            "serialized_outputs": "PASS",
            "exception_behavior": "PASS",
            "partial_results": "PASS",
            "state_reuse": "PASS",
        },
        "canonical_knowledge": {
            "one_canonical_source": "PASS",
            "technical_lead_authority": "PASS",
            "source_code_optional": "PASS",
            "provenance": "PASS",
            "uncertainty": "PASS",
            "temporal_semantics": "PASS",
            "ai_interpretation_self_approval": "NOT_SELF_APPROVING",
        },
        "r11": "PASS",
        "r12": "PASS",
        "plugin_contract": {
            "name": "LegacyMapperPluginKnowledge",
            "version": "1.0",
            "runtime_implemented": False,
        },
        "security": {
            "no_secret_values_introduced": True,
            "no_source_tree_mutation": True,
            "no_unsafe_path_traversal_regression": True,
            "no_provider_calls": True,
            "no_real_llm_calls": True,
            "no_hidden_external_network_requirement_introduced": True,
            "status": "PASS",
        },
        "debt": {
            "DUP_001": "RESOLVED",
            "DUP_002": "PRESERVED_DISTINCT",
            "DUP_003": "UNTOUCHED",
            "DUP_004": "UNTOUCHED",
            "DEBT_001": "RESOLVED",
            "DEBT_002": "RESOLVED",
            "DEBT_003": "RESOLVED",
            "REG_002_CANDIDATE": "RESOLVED",
            "TD_001": "OPEN",
            "TD_002": "DEFERRED",
            "TD_003": "PRESERVED_DISTINCT",
            "TD_004": "PARTIALLY_RESOLVED",
            "TD_005": "PARTIALLY_RESOLVED",
        },
        "v5_boundary": {
            "implemented": False,
            "scope": [
                "programming_language_agnostic",
                "framework_agnostic",
                "project_layout_agnostic",
                "architecture_pattern_agnostic",
                "database_persistence_technology_agnostic",
                "ai_provider_agnostic",
                "ai_model_agnostic",
            ],
            "note": (
                "V4.1 is a maintainability refactor of the existing VB.NET/Oracle/Copilot-specific "
                "implementation; it did not implement any of these transformations. No provider "
                "abstraction was introduced, no extractor was redesigned for agnosticism, and no "
                "Copilot-specific module was renamed."
            ),
        },
        "provider_calls": 0,
        "real_llm_calls": 0,
    }


def build_manifest(baseline_sha256: str) -> dict:
    immutable = [
        ("output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json", "R0 frozen maintainability inventory (historical AST scan)"),
        ("output/v4_1_r0/V4_1_REFACTOR_PLAN.json", "R0 frozen refactor plan"),
        ("output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json", "R1 approved behavioral-equivalence evidence"),
        ("output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json", "R2 approved type/contract equivalence evidence"),
        ("output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json", "R3 approved naming compatibility evidence"),
        ("output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json", "R4 approved readiness decomposition equivalence evidence"),
        ("output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json", "R5 approved orchestrator characterization evidence"),
        ("output/v4_1_r6/V4_1_R6_EXTRACTION_EQUIVALENCE.json", "R6 approved controlled extraction equivalence evidence"),
        ("output/v4_1_r7/V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json", "R7 approved exception boundary equivalence evidence"),
        ("output/v4_1_r8/V4_1_R8_NAMING_DOCUMENTATION_EQUIVALENCE.json", "R8 approved naming/documentation equivalence evidence"),
        ("output/v4_1_r9/V4_1_R9_COMPREHENSIVE_EQUIVALENCE.json", "R9 approved comprehensive regression/behavioral equivalence evidence"),
        ("output/v4_r14/V4_FINAL_BASELINE.json", "V4 final approved baseline (unchanged by V4.1)"),
        ("output/v4_r14/V4_FINAL_MANIFEST.json", "V4 final approved manifest (unchanged by V4.1)"),
        ("docs/V4_1/V4_1_R0_MAINTAINABILITY_INVENTORY_AND_REFACTOR_PLAN_RESULT.md", "R0 implementation result document"),
        ("docs/V4_1/V4_1_R0_CLOSURE_AND_VERSIONING_RESULT.md", "R0 closure and versioning result (Technical Lead approved)"),
        ("docs/V4_1/V4_1_R1_CLOSURE_AND_VERSIONING_RESULT.md", "R1 closure and versioning result (Technical Lead approved)"),
        ("docs/V4_1/V4_1_R2_CLOSURE_AND_VERSIONING_RESULT.md", "R2 closure and versioning result (Technical Lead approved)"),
        ("docs/V4_1/V4_1_R3_CLOSURE_AND_VERSIONING_RESULT.md", "R3 closure and versioning result (Technical Lead approved)"),
        ("docs/V4_1/V4_1_R4_CLOSURE_AND_VERSIONING_RESULT.md", "R4 closure and versioning result (Technical Lead approved)"),
        ("docs/V4_1/V4_1_R5_CLOSURE_AND_VERSIONING_RESULT.md", "R5 closure and versioning result (Technical Lead approved)"),
        ("docs/V4_1/V4_1_R6_CLOSURE_AND_VERSIONING_RESULT.md", "R6 closure and versioning result (Technical Lead approved)"),
        ("docs/V4_1/V4_1_R7_CLOSURE_AND_VERSIONING_RESULT.md", "R7 closure and versioning result (Technical Lead approved)"),
        ("docs/V4_1/V4_1_R8_CLOSURE_AND_VERSIONING_RESULT.md", "R8 closure and versioning result (Technical Lead approved)"),
        ("docs/V4_1/V4_1_R9_CLOSURE_AND_VERSIONING_RESULT.md", "R9 closure and versioning result (Technical Lead approved)"),
        ("docs/V4/V4_FINAL_CLOSURE_RESULT.md", "V4 final closure result (unchanged by V4.1)"),
    ]
    manifest_entries = [
        {"path": path, "sha256": sha256_of(path), "role": role}
        for path, role in immutable
    ]
    manifest_entries.append(
        {"path": "output/v4_1_r10/V4_1_FINAL_BASELINE.json", "sha256": baseline_sha256, "role": "R10 final V4.1 baseline (this closure round's own output)"}
    )
    mutable = [
        ("PROJECT_STATE.json", "mutable current-state pointer (latest_completed_round/latest_approved_round/round_status/next); not immutable evidence"),
        ("docs/PROJECT_RECOVERY.md", "mutable authoritative recovery/orientation document for a fresh session; not immutable evidence"),
        ("docs/GENERATED_ARTIFACT_POLICY.md", "mutable policy document governing generated-artifact handling; not immutable evidence"),
        ("docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md", "mutable repository-continuity contract document; not immutable evidence"),
    ]
    mutable_entries = [
        {"path": path, "sha256": sha256_of(path), "role": role}
        for path, role in mutable
    ]
    return {
        "version": "V4.1",
        "immutable_artifacts": manifest_entries,
        "mutable_current_state_documents": mutable_entries,
        "note": (
            "immutable_artifacts are approved historical evidence and must never be regenerated or "
            "edited; mutable_current_state_documents intentionally change as the project advances and "
            "their hashes here are a point-in-time snapshot, not an integrity requirement."
        ),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    baseline_text = json.dumps(build_baseline(), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    with BASELINE_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(baseline_text)
    baseline_sha256 = hashlib.sha256(baseline_text.encode("utf-8")).hexdigest()

    manifest_text = json.dumps(build_manifest(baseline_sha256), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(manifest_text)
    manifest_sha256 = hashlib.sha256(manifest_text.encode("utf-8")).hexdigest()

    print("BASELINE_SHA256=" + baseline_sha256)
    print("MANIFEST_SHA256=" + manifest_sha256)


if __name__ == "__main__":
    main()
