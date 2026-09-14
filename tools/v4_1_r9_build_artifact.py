"""Builds output/v4_1_r9/V4_1_R9_COMPREHENSIVE_EQUIVALENCE.json deterministically.

Not part of the production package; a one-off generator script for the
V4.1-R9 comprehensive verification artifact, following the pattern of
tools/v4_1_r7_build_artifact.py and tools/v4_1_r8_build_artifact.py.
"""
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "output" / "v4_1_r9" / "V4_1_R9_COMPREHENSIVE_EQUIVALENCE.json"


def build_artifact() -> dict:
    return {
        "round": "V4.1-R9",
        "entry_gate": {
            "v4_formally_closed": True,
            "v4_1_r0_through_r8_approved": True,
            "git_status_clean_except_prompt": True,
            "baseline_tests": "1566_PASS_0_FAIL_0_SKIP",
            "readiness": "READY",
            "provider_calls": 0,
            "real_llm_calls": 0,
            "result": "PASS",
        },
        "v4_baseline_integrity": "PASS",
        "v4_manifest_integrity": "PASS",
        "historical_artifact_integrity": {
            "r1": "PASS",
            "r2": "PASS",
            "r3": "PASS",
            "r4": "PASS",
            "r5": "PASS",
            "r6": "PASS",
            "r7": "PASS",
            "r8": "PASS",
        },
        "r0_frozen_inventory_modified": False,
        "approval_chain": [
            {"round": "V4.1-R0", "status": "APPROVED", "tests_at_closure": 1380},
            {"round": "V4.1-R1", "status": "APPROVED", "tests_at_closure": 1424},
            {"round": "V4.1-R2", "status": "APPROVED", "tests_at_closure": 1442},
            {"round": "V4.1-R3", "status": "APPROVED", "tests_at_closure": 1468},
            {"round": "V4.1-R4", "status": "APPROVED", "tests_at_closure": 1486},
            {"round": "V4.1-R5", "status": "APPROVED", "tests_at_closure": 1536},
            {"round": "V4.1-R6", "status": "APPROVED", "tests_at_closure": 1561},
            {"round": "V4.1-R7", "status": "APPROVED", "tests_at_closure": 1566},
            {"round": "V4.1-R8", "status": "APPROVED", "tests_at_closure": 1566},
        ],
        "cumulative_change_inventory": [
            {
                "round": "V4.1-R1",
                "production_files_added": ["legacy_documenter/utils/json_rendering.py"],
                "production_files_modified": [
                    "legacy_documenter/utils/__init__.py",
                    "legacy_documenter/knowledge/approval/contract_report.py",
                    "legacy_documenter/knowledge/canonical/contract_report.py",
                    "legacy_documenter/knowledge/classification/contract_report.py",
                    "legacy_documenter/knowledge/ingestion/contract_report.py",
                    "legacy_documenter/knowledge/input/contract_report.py",
                    "legacy_documenter/knowledge/plugin_projection/contract_report.py",
                    "legacy_documenter/knowledge/projection/contract_report.py",
                    "legacy_documenter/knowledge/proposals/contract_report.py",
                    "legacy_documenter/knowledge/provenance/contract_report.py",
                    "legacy_documenter/knowledge/relations/contract_report.py",
                    "legacy_documenter/knowledge/temporal/contract_report.py",
                ],
                "public_surface_changed": False,
                "structural_change": True,
                "documentation_only_change": False,
                "typing_change": False,
                "characterization_only": False,
                "behavior_change_claim": False,
                "equivalence_artifact": "output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json",
                "approved": True,
            },
            {
                "round": "V4.1-R2",
                "production_files_added": [],
                "production_files_modified": [
                    "legacy_documenter/analysis/deep_interpretation.py",
                    "legacy_documenter/analysis/targeted_exhaustion.py",
                    "legacy_documenter/documentation/aggregation.py",
                    "legacy_documenter/documentation/consistency.py",
                    "legacy_documenter/documentation/contracts.py",
                    "legacy_documenter/documentation/coverage.py",
                    "legacy_documenter/documentation/envelope.py",
                    "legacy_documenter/documentation/evidence_catalog.py",
                    "legacy_documenter/documentation/human_review.py",
                    "legacy_documenter/documentation/interpretation.py",
                    "legacy_documenter/documentation/renderer.py",
                ],
                "public_surface_changed": True,
                "structural_change": False,
                "documentation_only_change": False,
                "typing_change": True,
                "characterization_only": False,
                "behavior_change_claim": False,
                "equivalence_artifact": "output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json",
                "approved": True,
            },
            {
                "round": "V4.1-R3",
                "production_files_added": [],
                "production_files_modified": [
                    "legacy_documenter/knowledge/classification/service.py",
                    "legacy_documenter/knowledge/proposals/service.py",
                    "legacy_documenter/knowledge/relations/service.py",
                    "legacy_documenter/quality/maintainability_audit.py",
                ],
                "public_surface_changed": True,
                "structural_change": False,
                "documentation_only_change": False,
                "typing_change": False,
                "characterization_only": False,
                "behavior_change_claim": False,
                "equivalence_artifact": "output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json",
                "approved": True,
            },
            {
                "round": "V4.1-R4",
                "production_files_added": [
                    "legacy_documenter/knowledge/_readiness_io.py",
                    "legacy_documenter/knowledge/_readiness_parsing.py",
                    "legacy_documenter/knowledge/_readiness_evidence.py",
                ],
                "production_files_modified": ["legacy_documenter/knowledge/readiness.py"],
                "public_surface_changed": False,
                "structural_change": True,
                "documentation_only_change": False,
                "typing_change": False,
                "characterization_only": False,
                "behavior_change_claim": False,
                "equivalence_artifact": "output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json",
                "approved": True,
            },
            {
                "round": "V4.1-R5",
                "production_files_added": [],
                "production_files_modified": [],
                "public_surface_changed": False,
                "structural_change": False,
                "documentation_only_change": False,
                "typing_change": False,
                "characterization_only": True,
                "behavior_change_claim": False,
                "equivalence_artifact": "output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json",
                "approved": True,
            },
            {
                "round": "V4.1-R6",
                "production_files_added": [
                    "legacy_documenter/extractors/_database_line_scanner.py",
                    "legacy_documenter/extractors/_database_token_parsing.py",
                    "legacy_documenter/extractors/_database_classification.py",
                    "legacy_documenter/analysis/_flow_graph_construction.py",
                    "legacy_documenter/analysis/_flow_key_labels.py",
                    "legacy_documenter/analysis/_flow_report_composition.py",
                ],
                "production_files_modified": [
                    "legacy_documenter/extractors/database_extractor.py",
                    "legacy_documenter/analysis/flow_resolver.py",
                ],
                "public_surface_changed": False,
                "structural_change": True,
                "documentation_only_change": False,
                "typing_change": False,
                "characterization_only": False,
                "behavior_change_claim": False,
                "equivalence_artifact": "output/v4_1_r6/V4_1_R6_EXTRACTION_EQUIVALENCE.json",
                "approved": True,
            },
            {
                "round": "V4.1-R7",
                "production_files_added": [],
                "production_files_modified": ["legacy_documenter/main.py"],
                "public_surface_changed": False,
                "structural_change": True,
                "documentation_only_change": False,
                "typing_change": False,
                "characterization_only": False,
                "behavior_change_claim": False,
                "equivalence_artifact": "output/v4_1_r7/V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json",
                "approved": True,
            },
            {
                "round": "V4.1-R8",
                "production_files_added": [],
                "production_files_modified": [
                    "legacy_documenter/context/__init__.py",
                    "legacy_documenter/context/composer.py",
                    "legacy_documenter/context/context_builder.py",
                    "legacy_documenter/extractors/_database_classification.py",
                ],
                "public_surface_changed": False,
                "structural_change": False,
                "documentation_only_change": True,
                "typing_change": True,
                "characterization_only": False,
                "behavior_change_claim": False,
                "equivalence_artifact": "output/v4_1_r8/V4_1_R8_NAMING_DOCUMENTATION_EQUIVALENCE.json",
                "approved": True,
            },
        ],
        "contract_verification_matrix": [
            {"contract": "public import paths", "evidence": "R1-R8 closures each recorded PUBLIC_IMPORT(S)_PRESERVED=PASS; full regression green", "rounds_affecting": "R1,R3,R4,R6,R7,R8", "verification": "re-ran full suite + targeted characterization/security tests", "status": "PASS"},
            {"contract": "public callable signatures", "evidence": "R1-R8 closures each recorded PUBLIC_SIGNATURE_COMPATIBILITY=PASS", "rounds_affecting": "R1,R3,R4,R6,R7,R8", "verification": "re-ran full suite", "status": "PASS"},
            {"contract": "positional-call compatibility", "evidence": "R3 POSITIONAL_CALL_COMPATIBILITY=PASS", "rounds_affecting": "R3", "verification": "re-ran full suite", "status": "PASS"},
            {"contract": "keyword-call compatibility", "evidence": "R3 KEYWORD_CALL_COMPATIBILITY=PASS", "rounds_affecting": "R3", "verification": "re-ran full suite", "status": "PASS"},
            {"contract": "deterministic identifiers", "evidence": "R6 FLOW_IDENTIFIER_EQUIVALENCE=PASS; test_no_projection_invents_a_kno_id passes", "rounds_affecting": "R6", "verification": "re-ran tests.test_v4_r13_regression_and_security", "status": "PASS"},
            {"contract": "deterministic ordering", "evidence": "R6 DATABASE/FLOW_ORDERING_EQUIVALENCE=PASS; R7 ORDERING_EQUIVALENCE=PASS", "rounds_affecting": "R6,R7", "verification": "re-ran tests.test_v4_1_r6_*, tests.test_v4_1_r7_*", "status": "PASS"},
            {"contract": "serialized output structures", "evidence": "R1 CONTRACT_JSON_BYTE_EQUIVALENCE=PASS; R2/R4/R7/R8 SERIALIZED_OUTPUT_EQUIVALENCE=PASS", "rounds_affecting": "R1,R2,R4,R7,R8", "verification": "re-ran full suite + readiness gate twice", "status": "PASS"},
            {"contract": "exception behavior", "evidence": "R3 EXCEPTION_BEHAVIOR_EQUIVALENCE=PASS; R4 READINESS_EXCEPTION_EQUIVALENCE=PASS; R6 DATABASE/FLOW_EXCEPTION_EQUIVALENCE=PASS; R7 EXCEPTION_TYPE/MESSAGE_EQUIVALENCE=PASS", "rounds_affecting": "R3,R4,R6,R7", "verification": "re-ran characterization tests", "status": "PASS"},
            {"contract": "partial-result behavior", "evidence": "R6 characterization; R7 PARTIAL_RESULT_EQUIVALENCE=PASS", "rounds_affecting": "R6,R7", "verification": "re-ran tests.test_v4_1_r7_exception_boundaries_characterization", "status": "PASS"},
            {"contract": "state reuse/reset semantics", "evidence": "R6 FLOW_STATE_REUSE_EQUIVALENCE=PASS", "rounds_affecting": "R6", "verification": "re-ran tests.test_v4_1_r6_flow_resolver_gap_closure", "status": "PASS"},
            {"contract": "readiness behavior", "evidence": "R4 READINESS_RESULT_EQUIVALENCE=PASS", "rounds_affecting": "R4", "verification": "re-ran python -m legacy_documenter.knowledge.readiness twice, identical output", "status": "PASS"},
            {"contract": "canonical knowledge behavior", "evidence": "status/temporal preservation tests pass unchanged", "rounds_affecting": "none (V4 contract, untouched by V4.1)", "verification": "re-ran tests.test_v4_r13_regression_and_security", "status": "PASS"},
            {"contract": "R11 human projection boundary", "evidence": "R11 ids subset of canonical ids; human projection never imports plugin_projection", "rounds_affecting": "none (V4 contract, untouched)", "verification": "re-ran SiblingProjectionTests", "status": "PASS"},
            {"contract": "R12 Plugin projection boundary", "evidence": "R12 ids equal canonical ids; plugin projection never imports human projection; no Plugin runtime class/function defined", "rounds_affecting": "none (V4 contract, untouched)", "verification": "re-ran SiblingProjectionTests, ProviderAndRuntimeBoundaryTests", "status": "PASS"},
            {"contract": "security invariants", "evidence": "no eval/exec/compile, no risky primitive calls, path-traversal rejection, prompt-injection inertness", "rounds_affecting": "none (V4 contract, untouched)", "verification": "re-ran NoDynamicExecutionTests, PathSafetyTests, PromptInjectionInertnessTests", "status": "PASS"},
            {"contract": "source-code optionality", "evidence": "common models have no forbidden required fields; human-information-only material valid without code locator", "rounds_affecting": "none (V4 contract, untouched)", "verification": "re-ran SourceCodeOptionalityTests", "status": "PASS"},
            {"contract": "Technical Lead approval authority", "evidence": "every R1-R8 closure doc recorded APPROVAL_AUTHORITY=TECHNICAL_LEAD; no self-approval by the development agent occurred at any round", "rounds_affecting": "R1,R2,R3,R4,R5,R6,R7,R8", "verification": "read all 8 closure documents", "status": "PASS"},
        ],
        "determinism": {
            "readiness_rerun_twice_identical": True,
            "inventory_build_deterministic_test_passing": True,
            "r7_equivalence_artifact_determinism_previously_proven": True,
            "r8_equivalence_artifact_determinism_previously_proven": True,
            "status": "PASS",
        },
        "database_extractor": {
            "behavior_equivalence": "PASS",
            "ordering_equivalence": "PASS",
            "exception_equivalence": "PASS",
            "r6_deferred_groups_preserved": "PASS",
            "evidence": "tests.test_v4_1_r5_database_extractor_characterization and tests.test_v4_1_r6_database_extractor_gap_closure re-run and pass; git diff --stat against database_extractor.py is empty since R6",
        },
        "flow_resolver": {
            "behavior_equivalence": "PASS",
            "ordering_equivalence": "PASS",
            "identifier_equivalence": "PASS",
            "exception_equivalence": "PASS",
            "state_reuse_equivalence": "PASS",
            "r6_deferred_groups_preserved": "PASS",
            "evidence": "tests.test_v4_1_r5_flow_resolver_characterization and tests.test_v4_1_r6_flow_resolver_gap_closure re-run and pass; _path_id/_path_identities/_add_path/_call_ref/_stable_id untouched; git diff --stat against flow_resolver.py is empty since R6",
        },
        "r7_exception_boundaries": {
            "preserved": "PASS",
            "provider_boundary_production_changes": 0,
            "evidence": "tests.test_v4_1_r7_exception_boundaries_characterization re-run and pass; git diff --stat against main.py is empty since R7",
        },
        "r8_readability": {
            "copilot_pilot_rename": "DEFERRED",
            "context_package_structure_unchanged": "PASS",
            "td_005_status": "PARTIALLY_RESOLVED",
        },
        "canonical_knowledge": {
            "one_canonical_knowledge_source": "PASS",
            "technical_lead_final_approval_authority": "PASS",
            "source_code_optional": "PASS",
            "provenance_preserved": "PASS",
            "uncertainty_preserved": "PASS",
            "as_is_to_be_historical_semantics_preserved": "PASS",
            "ai_interpretation_not_self_approving": "PASS",
        },
        "r11_boundary": "PASS",
        "r12_boundary": "PASS",
        "security": {
            "no_secret_values_introduced": True,
            "no_source_tree_mutation": True,
            "no_unsafe_path_traversal_regression": True,
            "no_provider_calls": True,
            "no_real_llm_calls": True,
            "no_hidden_external_network_requirement_introduced": True,
            "status": "PASS",
        },
        "debt_state": {
            "DUP_001": "RESOLVED",
            "DEBT_001": "RESOLVED",
            "DEBT_002": "RESOLVED",
            "DEBT_003": "RESOLVED",
            "DUP_002": "PRESERVED_DISTINCT",
            "DUP_003": "UNTOUCHED",
            "DUP_004": "UNTOUCHED",
            "TD_001": "OPEN (recommended_round V4.1-R8 in the original R0 plan; the R8 actually executed used a different, narrower scope and did not address it; not silently marked resolved)",
            "TD_002": "DEFERRED (provider boundary kept unchanged by design; R7 explicitly out of scope per Provider Boundary Fence)",
            "TD_003": "PRESERVED_DISTINCT (same as DUP-002)",
            "TD_004": "PARTIALLY_RESOLVED (6 of 15 R5-identified groups extracted in R6; 9 remain deferred)",
            "TD_005": "PARTIALLY_RESOLVED",
            "REG_002_CANDIDATE": "RESOLVED (R1, test-only fix)",
            "status": "PASS",
        },
        "v5_boundary": {
            "language_agnostic": False,
            "framework_agnostic": False,
            "project_layout_agnostic": False,
            "architecture_pattern_agnostic": False,
            "database_agnostic": False,
            "ai_provider_agnostic": False,
            "ai_model_agnostic": False,
            "implemented": False,
            "note": (
                "V4.1 was a maintainability refactor of the existing VB.NET/Oracle/Copilot-specific "
                "implementation; it did not and was not required to introduce runtime/domain agnosticism. "
                "V5 remains responsible for language, framework, project-layout, architecture-pattern, "
                "database/persistence-technology, AI-provider, and AI-model agnosticism. No provider "
                "abstraction, Copilot-specific rename, or extraction-architecture change for agnosticism "
                "was made in R1-R9."
            ),
        },
        "tests": "1566_PASS_0_FAIL_0_SKIP",
        "readiness": "READY",
        "production_code_changed": False,
        "production_behavior_changed": False,
    }


def main() -> None:
    payload = build_artifact()
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print(digest)


if __name__ == "__main__":
    main()
