"""Builds output/v4_1_r8/V4_1_R8_NAMING_DOCUMENTATION_EQUIVALENCE.json deterministically.

Not part of the production package; a one-off generator script for the
V4.1-R8 result artifact, following the same pattern as tools/v4_1_r7_build_artifact.py.
"""
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "output" / "v4_1_r8" / "V4_1_R8_NAMING_DOCUMENTATION_EQUIVALENCE.json"


def build_artifact() -> dict:
    return {
        "round": "V4.1-R8",
        "entry_gate": {
            "v4_formally_closed": True,
            "v4_1_r0_through_r7_approved": True,
            "git_status_clean_except_prompt": True,
            "baseline_tests": "1566_PASS_0_FAIL_0_SKIP",
            "readiness": "READY",
            "provider_calls": 0,
            "real_llm_calls": 0,
            "result": "PASS",
        },
        "candidate_inventory": [
            {
                "path": "legacy_documenter/knowledge/classification/service.py",
                "symbol": "requests parameter",
                "current_name": "requests",
                "r8_classification": "DO_NOT_CHANGE",
                "note": "Already resolved by V4.1-R3 (renamed to classification_requests/proposal_requests/relation_requests); no further action.",
            },
            {
                "path": "legacy_documenter/quality/maintainability_audit.py",
                "symbol": "audit",
                "current_name": "audit",
                "r8_classification": "DO_NOT_CHANGE",
                "note": "Already resolved by V4.1-R3 (build_maintainability_inventory alias added, audit kept as compatibility name); no further action.",
            },
            {
                "path": "legacy_documenter/llm/copilot_pilot.py",
                "symbol": "module file name",
                "current_name": "copilot_pilot.py",
                "candidate_name": "copilot_session.py",
                "public_or_private": "public (imported across package boundaries)",
                "runtime_imported": True,
                "keyword_callers": False,
                "reflection_or_dynamic_access": False,
                "test_references": True,
                "monkeypatch_dependency": False,
                "serialized_name_dependency": False,
                "compatibility_risk": "MEDIUM",
                "documentation_gap": False,
                "type_hint_gap": False,
                "r8_classification": "CHARACTERIZED_BUT_DEFER",
                "copilot_pilot_sub_decision": "DEFER",
                "note": (
                    "discover_model is imported directly by 4 production modules "
                    "(documentation/generator.py, hierarchical.py, systematic.py, resume.py) "
                    "plus this module's own run(). A rename would require updating all 4 "
                    "import sites and adding a REEXPORT compatibility wrapper at the old path "
                    "-- exactly the 'still requires compatibility shims or broad changes' case "
                    "this round says to prefer DEFER for. A file rename is not required for R8 success."
                ),
            },
            {
                "path": "legacy_documenter/context/__init__.py",
                "symbol": "package docstring",
                "current_name": None,
                "public_or_private": "public (package docstring)",
                "runtime_imported": True,
                "keyword_callers": False,
                "reflection_or_dynamic_access": False,
                "test_references": False,
                "monkeypatch_dependency": False,
                "serialized_name_dependency": False,
                "compatibility_risk": "NONE",
                "documentation_gap": True,
                "type_hint_gap": False,
                "r8_classification": "DOCUMENTATION_ONLY",
                "note": "Expanded to explain the write-stage/read-stage relationship among composer.py/resolver.py/context_builder.py/system_context_builder.py, addressing R0's naming_candidates note that the entry point is hard to guess; no file moved or renamed.",
            },
            {
                "path": "legacy_documenter/context/composer.py",
                "symbol": "module docstring",
                "current_name": None,
                "public_or_private": "public",
                "runtime_imported": True,
                "keyword_callers": False,
                "reflection_or_dynamic_access": False,
                "test_references": False,
                "monkeypatch_dependency": False,
                "serialized_name_dependency": False,
                "compatibility_risk": "NONE",
                "documentation_gap": True,
                "type_hint_gap": False,
                "r8_classification": "DOCUMENTATION_ONLY",
                "note": "Module had no module-level docstring; added one describing its read-stage budget-composition responsibility.",
            },
            {
                "path": "legacy_documenter/context/context_builder.py",
                "symbol": "module docstring",
                "current_name": None,
                "public_or_private": "public",
                "runtime_imported": True,
                "keyword_callers": False,
                "reflection_or_dynamic_access": False,
                "test_references": False,
                "monkeypatch_dependency": False,
                "serialized_name_dependency": False,
                "compatibility_risk": "NONE",
                "documentation_gap": True,
                "type_hint_gap": False,
                "r8_classification": "DOCUMENTATION_ONLY",
                "note": "Module had no module-level docstring; added one describing its write-stage project-summary responsibility.",
            },
            {
                "path": "legacy_documenter/context/resolver.py",
                "symbol": "module docstring",
                "current_name": None,
                "public_or_private": "public",
                "r8_classification": "DO_NOT_CHANGE",
                "note": "Already has a clear module docstring ('Read-only V3-R2 deterministic context package resolver.'); no change needed.",
            },
            {
                "path": "legacy_documenter/context/system_context_builder.py",
                "symbol": "module docstring",
                "current_name": None,
                "public_or_private": "public",
                "r8_classification": "DO_NOT_CHANGE",
                "note": "Already has a clear module docstring ('Deterministic, compact R5 intermediate-model builder.'); no change needed.",
            },
            {
                "path": "legacy_documenter/extractors/_database_classification.py",
                "symbol": "matched_type(match)",
                "current_name": "match (untyped parameter)",
                "candidate_name": "match: re.Match[str]",
                "public_or_private": "private (internal R6 helper module)",
                "runtime_imported": True,
                "keyword_callers": False,
                "reflection_or_dynamic_access": False,
                "test_references": False,
                "monkeypatch_dependency": False,
                "serialized_name_dependency": False,
                "compatibility_risk": "NONE",
                "documentation_gap": False,
                "type_hint_gap": True,
                "r8_classification": "SAFE_TYPE_HINT",
                "note": "Sole call sites (database_extractor.py::_matched_type) always pass a regex Match object obtained from a successful re.match/re.search; type hint only, no behavior change.",
            },
            {
                "path": "legacy_documenter/knowledge/_readiness_io.py, _readiness_parsing.py, _readiness_evidence.py (V4.1-R4)",
                "symbol": "module contents",
                "r8_classification": "DO_NOT_CHANGE",
                "note": "Already fully typed and documented; no gap found.",
            },
            {
                "path": "legacy_documenter/extractors/_database_line_scanner.py, _database_token_parsing.py (V4.1-R6)",
                "symbol": "module contents",
                "r8_classification": "DO_NOT_CHANGE",
                "note": "Already fully typed and documented; no gap found.",
            },
            {
                "path": "legacy_documenter/analysis/_flow_graph_construction.py, _flow_key_labels.py, _flow_report_composition.py (V4.1-R6)",
                "symbol": "module contents",
                "r8_classification": "DO_NOT_CHANGE",
                "note": "Already fully typed and documented; no gap found.",
            },
            {
                "path": "legacy_documenter/main.py",
                "symbol": "_extract_into (V4.1-R7)",
                "r8_classification": "DO_NOT_CHANGE",
                "note": "Already fully typed and documented by R7; R6/R7 Preservation Fence forbids altering its behavior.",
            },
        ],
        "changes": {
            "private_renames": [],
            "local_renames": [],
            "documentation_changes": [
                {
                    "path": "legacy_documenter/context/__init__.py",
                    "change": "Expanded package docstring describing the write-stage/read-stage module relationship.",
                },
                {
                    "path": "legacy_documenter/context/composer.py",
                    "change": "Added module-level docstring.",
                },
                {
                    "path": "legacy_documenter/context/context_builder.py",
                    "change": "Added module-level docstring.",
                },
            ],
            "type_hint_changes": [
                {
                    "path": "legacy_documenter/extractors/_database_classification.py",
                    "symbol": "matched_type",
                    "change": "Added `match: re.Match[str]` parameter type hint (added `import re`).",
                }
            ],
            "deferred_candidates": [
                {
                    "path": "legacy_documenter/llm/copilot_pilot.py",
                    "reason": "Rename requires updating 4 production import sites plus a REEXPORT wrapper; broad change, deferred per this round's own rule.",
                }
            ],
            "do_not_change": [
                "legacy_documenter/knowledge/classification/service.py (requests param, already resolved R3)",
                "legacy_documenter/quality/maintainability_audit.py (audit, already resolved R3)",
                "legacy_documenter/context/resolver.py",
                "legacy_documenter/context/system_context_builder.py",
                "legacy_documenter/knowledge/_readiness_io.py",
                "legacy_documenter/knowledge/_readiness_parsing.py",
                "legacy_documenter/knowledge/_readiness_evidence.py",
                "legacy_documenter/extractors/_database_line_scanner.py",
                "legacy_documenter/extractors/_database_token_parsing.py",
                "legacy_documenter/analysis/_flow_graph_construction.py",
                "legacy_documenter/analysis/_flow_key_labels.py",
                "legacy_documenter/analysis/_flow_report_composition.py",
                "legacy_documenter/main.py::_extract_into",
            ],
        },
        "compatibility": {
            "public_imports": "PASS",
            "public_signatures": "PASS",
            "positional_calls": "NOT_APPLICABLE",
            "keyword_calls": "NOT_APPLICABLE",
            "return_values": "NOT_APPLICABLE",
            "exceptions": "NOT_APPLICABLE",
            "serialized_outputs": "PASS",
        },
        "r6_deferred_groups_preserved": "PASS",
        "r7_exception_boundaries_preserved": "PASS",
        "copilot_pilot_decision": "DEFER",
        "context_package_decision": "DOCUMENTATION_ONLY",
        "td_005_status": "PARTIALLY_RESOLVED",
        "production_files_added": [],
        "production_files_modified": [
            "legacy_documenter/context/__init__.py",
            "legacy_documenter/context/composer.py",
            "legacy_documenter/context/context_builder.py",
            "legacy_documenter/extractors/_database_classification.py",
        ],
        "approved_artifact_integrity": "PASS",
        "r0_frozen_inventory_modified": False,
        "tests": "1566_PASS_0_FAIL_0_SKIP",
        "readiness": "READY",
        "production_code_changed": True,
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
