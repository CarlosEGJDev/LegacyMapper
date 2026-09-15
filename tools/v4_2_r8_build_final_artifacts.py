"""Builds output/v4_2_r8/V4_2_FINAL_BASELINE.json and V4_2_FINAL_MANIFEST.json deterministically.

Not part of the production package; a one-off generator script for the
V4.2-R8 final candidate baseline/manifest, following the pattern of
tools/v4_1_r10_build_artifacts.py. No production code is read or modified;
only repository-relative paths and content hashes of existing, already-
produced artifacts are recorded. This is a CANDIDATE baseline -- V4.2 is
not formally closed by this script or by V4.2-R8 itself (Technical Lead
review is still required; see docs/V4_2/V4_2_R8_DOCUMENTATION_AT_SCALE_
FINAL_BASELINE_AND_CLOSURE_PREPARATION_RESULT.md).
"""
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "output" / "v4_2_r8"
BASELINE_PATH = OUT_DIR / "V4_2_FINAL_BASELINE.json"
MANIFEST_PATH = OUT_DIR / "V4_2_FINAL_MANIFEST.json"


def sha256_of(rel_path: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel_path).read_bytes()).hexdigest()


def build_baseline(tests: str) -> dict:
    return {
        "version": "V4.2",
        "status": "READY_FOR_TECHNICAL_LEAD_FINAL_REVIEW",
        "v4_2_status": "CANDIDATE_PENDING_FINAL_APPROVAL",
        "latest_completed_round_candidate": "V4.2-R8",
        "approved_rounds": {
            "r0": "APPROVED", "r1": "APPROVED", "r2": "APPROVED", "r3": "APPROVED",
            "r4": "APPROVED", "r5": "APPROVED", "r5_1": "APPROVED", "r6": "APPROVED",
            "r7": "APPROVED", "r7_1": "APPROVED", "r8": "CANDIDATE",
        },
        "tests": tests,
        "readiness": "READY",
        "authoritative_exit_code_contract": "SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4",
        "cli": {
            "commands": ["analyze", "full", "readiness"],
            "legacy_bare_invocation_alias_of": "analyze",
            "full_deterministic_pipeline_available": True,
            "ai_interpretation_opt_in_available": True,
            "ai_interpretation_default": False,
        },
        "approval_boundary": {
            "design_status": "APPROVED_DESIGN_ONLY",
            "implementation_status": "NOT_IMPLEMENTED",
            "run_id": "NOT_IMPLEMENTED",
            "approve_reject_request_correction_commands": "NOT_IMPLEMENTED",
            "approval_decision_persistence": "NOT_IMPLEMENTED",
            "r11_r12_orchestration": "NOT_IMPLEMENTED",
        },
        "canonical_knowledge_produced": False,
        "technical_lead_approval": False,
        "plugin_runtime": "NOT_IMPLEMENTED",
        "v5_implemented": False,
        "v5_boundary": {
            "implemented": False,
            "scope": [
                "programming_language_agnostic",
                "framework_agnostic",
                "project_layout_agnostic",
                "database_persistence_technology_agnostic",
                "ai_provider_agnostic",
                "ai_model_agnostic",
            ],
        },
        "r7_real_pilot": {
            "status": "COMPLETED",
            "selected_source_note": (
                "AGENTS.md 'Legacy Source Repository' names the single authoritative path (not "
                "repeated here to avoid embedding an absolute analyst path in a versioned baseline); "
                "it was accessed only during the R7 real pilot itself, never by R7.1 or R8."
            ),
            "real_ist_accessed_in_r8": False,
        },
        "r7_findings_final_state": {
            "F-01": "FIXED", "F-02": "FIXED", "F-03": "FIXED", "F-04": "FIXED",
            "F-05": "DEFERRED_BY_DETERMINISM_CONTRACT",
            "F-06": "PRESERVED_OBSERVATION", "F-07": "PRESERVED_OBSERVATION",
        },
        "documentation_navigation": {
            "top_level_readme": "documentation/README.md",
            "fixed_top_level_filenames_preserved": True,
            "top_level_filenames": [
                "PROJECT_OVERVIEW.md", "SOLUTION_STRUCTURE.md", "PROJECT_DEPENDENCIES.md",
                "WEBFORMS_MAP.md", "CONFIGURATION_SUMMARY.md", "ANALYSIS_WARNINGS.md",
                "WEB_ENTRY_POINTS.md", "FUNCTIONAL_FLOWS.md", "DATABASE_ACCESS.md",
                "UNRESOLVED_FINDINGS.md",
            ],
            "navigation_plus_partitioned_detail": [
                {"top_level": "FUNCTIONAL_FLOWS.md", "detail_directory": "documentation/functional_flows/", "group_unit": "project"},
                {"top_level": "DATABASE_ACCESS.md", "detail_directory": "documentation/database_access/", "group_unit": "project"},
                {"top_level": "UNRESOLVED_FINDINGS.md", "detail_directory": "documentation/unresolved_findings/", "group_unit": "category"},
            ],
            "rerun_removes_stale_partitions": True,
            "unknown_user_files_preserved": True,
        },
        "known_limitations": [
            "F-05 DEFERRED_BY_DETERMINISM_CONTRACT",
            "F-06 PRESERVED_OBSERVATION",
            "F-07 PRESERVED_OBSERVATION",
            "WEB_ENTRY_POINTS.md and PROJECT_DEPENDENCIES.md remain single documents; a future real "
            "pilot could still find them too large at greater scale",
        ],
        "provider_calls": 0,
        "real_llm_calls": 0,
        "v4_1_reopened": False,
    }


def build_manifest(baseline_sha256: str) -> dict:
    docs = [
        ("docs/V4_2/V4_2_R0_FULL_PIPELINE_ARCHITECTURE_AND_INVENTORY_RESULT.md", "R0 result document"),
        ("docs/V4_2/V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL_RESULT.md", "R1 result document"),
        ("docs/V4_2/V4_2_R2_DETERMINISTIC_FULL_PIPELINE_ORCHESTRATOR_RESULT.md", "R2 result document"),
        ("docs/V4_2/V4_2_R3_DETERMINISTIC_TECHNICAL_DOCUMENTATION_RESULT.md", "R3 result document"),
        ("docs/V4_2/V4_2_R4_AI_INTERPRETATION_AND_PROPOSAL_INTEGRATION_RESULT.md", "R4 result document"),
        ("docs/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX_RESULT.md", "R5 result document"),
        ("docs/V4_2/V4_2_R5_1_EXIT_CODE_CONTRACT_AND_REAL_PROVIDER_GUARD_RESULT.md", "R5.1 result document"),
        ("docs/V4_2/V4_2_R5_R5_1_CLOSURE_AND_VERSIONING_RESULT.md", "R5/R5.1 closure and versioning result (Technical Lead approved)"),
        ("docs/V4_2/V4_2_R6_ROBUSTNESS_RECOVERY_SECURITY_AND_APPROVAL_SURFACE_RESULT.md", "R6 result document"),
        ("docs/V4_2/V4_2_R6_CLOSURE_AND_VERSIONING_RESULT.md", "R6 closure and versioning result (Technical Lead approved)"),
        ("docs/V4_2/V4_2_R7_REAL_IST_PILOT_AND_COMMITTABLE_FIXTURE_RESULT.md", "R7 real pilot result document"),
        ("docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md", "R7 real pilot documentation review"),
        ("docs/V4_2/V4_2_R7_SYNTHETIC_FIXTURE_VALIDATION.md", "R7 synthetic fixture validation"),
        ("docs/V4_2/V4_2_R7_1_REAL_PILOT_FINDINGS_CORRECTION_RESULT.md", "R7.1 findings correction result document"),
        ("docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md", "R7.1 findings verification"),
        ("docs/V4_2/V4_2_R7_R7_1_CLOSURE_AND_VERSIONING_RESULT.md", "R7/R7.1 closure and versioning result (Technical Lead approved)"),
        ("docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md", "Approved approval-surface design (APPROVED_DESIGN_ONLY)"),
        ("docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md", "R8 user manual"),
        ("docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md", "R8 technical manual"),
    ]
    production = [
        ("legacy_documenter/analysis/flow_resolver.py", "F-01 additive flow fields (R7.1)"),
        ("legacy_documenter/analysis/_flow_report_composition.py", "F-01 additive flow-summary counters (R7.1)"),
        ("legacy_documenter/exporters/technical_documentation_renderer.py", "navigation/partition renderers (R8); F-01 doc correction (R7.1); R3 origin"),
        ("legacy_documenter/exporters/markdown_exporter.py", "F-02/F-03/F-04 corrections (R7.1)"),
        ("legacy_documenter/exporters/_documentation_partitioning.py", "safe deterministic partition filenames (R8)"),
        ("legacy_documenter/cli/pipeline_stages.py", "DOCUMENTATION stage orchestration, including R8 partitioned writes"),
        ("legacy_documenter/cli/artifact_lifecycle.py", "rerun/recovery ownership, including R8 partition sync (R6 origin)"),
        ("legacy_documenter/cli/full_pipeline.py", "resilient full-pipeline orchestrator (R2 origin)"),
    ]
    tests = [
        ("tests/test_v4_2_r7_1_real_pilot_findings_correction.py", "R7.1 characterization/correction tests"),
        ("tests/test_v4_2_r7_synthetic_full_fixture.py", "R7 synthetic fixture regression tests"),
        ("tests/fixtures/v4_2_r7_full_sample/SampleLegacy.sln", "R7 committable synthetic fixture (entry file)"),
    ]
    # tests/test_v4_2_r8_documentation_at_scale.py is deliberately NOT hashed
    # here: it is the very test module that reads this manifest to verify its
    # own hashes, so including it would make every edit to this file
    # self-invalidate its own manifest entry.
    entries = [
        {"path": path, "sha256": sha256_of(path), "role": role}
        for path, role in (docs + production + tests)
    ]
    entries.append({
        "path": "output/v4_2_r8/V4_2_FINAL_BASELINE.json",
        "sha256": baseline_sha256,
        "role": "R8 final candidate baseline (this closure-preparation round's own output)",
    })
    mutable = [
        ("PROJECT_STATE.json", "mutable current-state pointer; not immutable evidence"),
        ("docs/PROJECT_RECOVERY.md", "mutable authoritative recovery/orientation document; not immutable evidence"),
    ]
    mutable_entries = [{"path": path, "sha256": sha256_of(path), "role": role} for path, role in mutable]
    return {
        "version": "V4.2",
        "candidate_round": "V4.2-R8",
        "authoritative_artifacts": entries,
        "mutable_current_state_documents": mutable_entries,
        "note": (
            "authoritative_artifacts are already-produced, already-reviewed evidence for the V4.2 "
            "candidate state; they are not modified by this script, only hashed. "
            "mutable_current_state_documents intentionally change as the project advances and their "
            "hashes here are a point-in-time snapshot, not an integrity requirement. No real-IST "
            "generated output (output/v4_2_r7_ist_operacional/) is referenced anywhere in this "
            "manifest."
        ),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    baseline_text = json.dumps(build_baseline("1804_PASS_0_FAIL_0_SKIP"), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
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
