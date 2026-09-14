"""Builds output/v4_1_r7/V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json deterministically.

Not part of the production package; a one-off generator script for the
V4.1-R7 result artifact, following the same pattern as tools/v4_1_r0.
"""
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = REPO_ROOT / "output" / "v4_1_r7" / "V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json"


def build_artifact() -> dict:
    return {
        "round": "V4.1-R7",
        "entry_gate": {
            "v4_formally_closed": True,
            "v4_1_r0_through_r6_approved": True,
            "git_status_clean_except_prompt": True,
            "baseline_tests": "1561_PASS_0_FAIL_0_SKIP",
            "readiness": "READY",
            "provider_calls": 0,
            "real_llm_calls": 0,
            "result": "PASS",
        },
        "inventory": {
            "exception_boundaries": [
                {
                    "path": "legacy_documenter/documentation/generator.py",
                    "handler_count": 1,
                    "r0_classification": "HISTORICAL_COMPATIBILITY",
                },
                {
                    "path": "legacy_documenter/documentation/hierarchical.py",
                    "handler_count": 3,
                    "r0_classification": "HISTORICAL_COMPATIBILITY",
                },
                {
                    "path": "legacy_documenter/documentation/resume.py",
                    "handler_count": 6,
                    "r0_classification": "REFACTOR_CANDIDATE",
                },
                {
                    "path": "legacy_documenter/documentation/systematic.py",
                    "handler_count": 1,
                    "r0_classification": "HISTORICAL_COMPATIBILITY",
                },
                {
                    "path": "legacy_documenter/llm/copilot_pilot.py",
                    "handler_count": 1,
                    "r0_classification": "JUSTIFIED_BOUNDARY",
                },
                {
                    "path": "legacy_documenter/llm/providers/copilot.py",
                    "handler_count": 4,
                    "r0_classification": "JUSTIFIED_BOUNDARY",
                },
                {
                    "path": "legacy_documenter/llm/providers/gemini.py",
                    "handler_count": 2,
                    "r0_classification": "JUSTIFIED_BOUNDARY",
                },
                {
                    "path": "legacy_documenter/main.py",
                    "handler_count": 4,
                    "r0_classification": "JUSTIFIED_BOUNDARY",
                },
            ],
            "adapters": [
                {
                    "path": "legacy_documenter/main.py",
                    "symbol": "analyze_repository",
                    "note": (
                        "Three near-identical try/except Exception blocks converting a "
                        "per-file extractor failure into a structured error record "
                        "(CallExtractor, WebEventExtractor, DatabaseExtractor); a fourth, "
                        "differently-shaped block in the same function (solution/vb_project/"
                        "vb_source/webform/web_config extraction) was left unchanged "
                        "(DIFFERENT, not SEMANTICALLY_IDENTICAL to the other three)."
                    ),
                }
            ],
            "provider_boundaries": [
                "legacy_documenter/documentation/generator.py",
                "legacy_documenter/documentation/hierarchical.py",
                "legacy_documenter/documentation/systematic.py",
                "legacy_documenter/llm/copilot_pilot.py",
                "legacy_documenter/llm/providers/copilot.py",
                "legacy_documenter/llm/providers/gemini.py",
            ],
            "high_risk_boundaries": [
                "legacy_documenter/documentation/resume.py",
                "legacy_documenter/extractors/database_extractor.py",
                "legacy_documenter/analysis/flow_resolver.py",
                "legacy_documenter/analysis/deep_source.py",
            ],
        },
        "candidates": {
            "in_scope": [
                {
                    "path": "legacy_documenter/main.py",
                    "symbol": "analyze_repository (CallExtractor/WebEventExtractor/DatabaseExtractor blocks)",
                    "r7_scope_classification": "IN_SCOPE",
                }
            ],
            "out_of_scope_provider": [
                {
                    "path": "legacy_documenter/documentation/generator.py",
                    "reason": "Sole except Exception directly wraps asyncio.run(discover_model()); R0's per-file HISTORICAL_COMPATIBILITY label described overall file style, not this catch site's live provider dependency.",
                },
                {
                    "path": "legacy_documenter/documentation/hierarchical.py",
                    "reason": "Same discover_model() provider-discovery catch as generator.py; the module's other two handlers (except ValueError / except RuntimeError) unwind a try block that also calls provider.structured_generate, so they are provider-entangled control flow, not a standalone local adapter.",
                },
                {
                    "path": "legacy_documenter/documentation/systematic.py",
                    "reason": "Same discover_model() provider-discovery catch as generator.py.",
                },
                {
                    "path": "legacy_documenter/llm/copilot_pilot.py",
                    "reason": "R0 JUSTIFIED_BOUNDARY; wraps asyncio.run(discover_model()) itself, classifying real Copilot auth/access failures. Explicitly excluded from renaming/restructuring by this round's Scope Fence.",
                },
                {
                    "path": "legacy_documenter/llm/providers/copilot.py",
                    "reason": "R0 JUSTIFIED_BOUNDARY; converts external Copilot Chat/subprocess failures into a domain ProviderError (TD-002's own stated plan).",
                },
                {
                    "path": "legacy_documenter/llm/providers/gemini.py",
                    "reason": "R0 JUSTIFIED_BOUNDARY; converts external HTTP/urllib failures into a domain ProviderError.",
                },
            ],
            "out_of_scope_high_risk": [
                {
                    "path": "legacy_documenter/documentation/resume.py",
                    "reason": "Named in this round's High-Risk Fence (default DEFER). Live inspection: all 6 handlers sit inside a try block that also calls provider.structured_generate and store.persist; the R0 REFACTOR_CANDIDATE note's 'checkpoint/resume I/O' framing understates the provider entanglement. No tiny isolated handler independent of the provider call sequence was found, so no exception-scope narrowing is authorized this round.",
                }
            ],
            "needs_characterization": [],
        },
        "characterization": {
            "exception_map": [
                {
                    "path": "legacy_documenter/main.py",
                    "symbol": "analyze_repository",
                    "operation": "CallExtractor.extract(full_path, root)",
                    "input_condition": "extractor raises any Exception subclass",
                    "exception_type": "Exception",
                    "message_or_pattern": "str(exc)",
                    "propagates": False,
                    "converted_to": '{"file": source.relative_path, "extractor": "CallExtractor", "error": str(exc)}',
                    "partial_result_preserved": True,
                    "side_effects": "none in the handler itself",
                    "caller_visible": True,
                    "existing_test": False,
                    "new_characterization_test": "tests/test_v4_1_r7_exception_boundaries_characterization.py::test_call_extractor_failure_is_recorded_as_structured_error_and_others_still_run",
                    "cleanup_candidate": True,
                },
                {
                    "path": "legacy_documenter/main.py",
                    "symbol": "analyze_repository",
                    "operation": "WebEventExtractor.extract(full_path, root)",
                    "input_condition": "extractor raises any Exception subclass",
                    "exception_type": "Exception",
                    "message_or_pattern": "str(exc)",
                    "propagates": False,
                    "converted_to": '{"file": source.relative_path, "extractor": "WebEventExtractor", "error": str(exc)}',
                    "partial_result_preserved": True,
                    "side_effects": "none in the handler itself",
                    "caller_visible": True,
                    "existing_test": False,
                    "new_characterization_test": "tests/test_v4_1_r7_exception_boundaries_characterization.py::test_web_event_extractor_failure_is_recorded_as_structured_error",
                    "cleanup_candidate": True,
                },
                {
                    "path": "legacy_documenter/main.py",
                    "symbol": "analyze_repository",
                    "operation": "DatabaseExtractor.extract(full_path, root)",
                    "input_condition": "extractor raises any Exception subclass",
                    "exception_type": "Exception",
                    "message_or_pattern": "str(exc)",
                    "propagates": False,
                    "converted_to": '{"file": source.relative_path, "extractor": "DatabaseExtractor", "error": str(exc)}',
                    "partial_result_preserved": True,
                    "side_effects": "none in the handler itself",
                    "caller_visible": True,
                    "existing_test": False,
                    "new_characterization_test": "tests/test_v4_1_r7_exception_boundaries_characterization.py::test_database_extractor_failure_is_recorded_as_structured_error",
                    "cleanup_candidate": True,
                },
                {
                    "path": "legacy_documenter/main.py",
                    "symbol": "analyze_repository",
                    "operation": "extractor.extract(full_path, root) for solution/vb_project/vb_source/webform/web_config file types",
                    "input_condition": "extractor raises any Exception subclass",
                    "exception_type": "Exception",
                    "message_or_pattern": "str(exc)",
                    "propagates": False,
                    "converted_to": '{"file": source.relative_path, "extractor": extractor.__class__.__name__, "error": str(exc)}',
                    "partial_result_preserved": True,
                    "side_effects": "none in the handler itself",
                    "caller_visible": True,
                    "existing_test": False,
                    "new_characterization_test": None,
                    "cleanup_candidate": False,
                },
                {
                    "path": "legacy_documenter/documentation/generator.py",
                    "symbol": "run",
                    "operation": "asyncio.run(discover_model())",
                    "input_condition": "provider model discovery fails",
                    "exception_type": "Exception",
                    "message_or_pattern": None,
                    "propagates": False,
                    "converted_to": '{"status": "V3-R7_BLOCKED_PROVIDER", "calls": 0}',
                    "partial_result_preserved": False,
                    "side_effects": "none",
                    "caller_visible": True,
                    "existing_test": True,
                    "new_characterization_test": None,
                    "cleanup_candidate": False,
                },
                {
                    "path": "legacy_documenter/documentation/hierarchical.py",
                    "symbol": "run",
                    "operation": "asyncio.run(discover_model())",
                    "input_condition": "provider model discovery fails",
                    "exception_type": "Exception",
                    "message_or_pattern": None,
                    "propagates": False,
                    "converted_to": '{"status": "V3-R7_2_BLOCKED_PROVIDER", "calls": 0}',
                    "partial_result_preserved": False,
                    "side_effects": "none",
                    "caller_visible": True,
                    "existing_test": True,
                    "new_characterization_test": None,
                    "cleanup_candidate": False,
                },
                {
                    "path": "legacy_documenter/documentation/systematic.py",
                    "symbol": "run",
                    "operation": "asyncio.run(discover_model())",
                    "input_condition": "provider model discovery fails",
                    "exception_type": "Exception",
                    "message_or_pattern": None,
                    "propagates": False,
                    "converted_to": '{"status": "V3-R7_2_1_BLOCKED_PROVIDER", "calls": 0}',
                    "partial_result_preserved": False,
                    "side_effects": "none",
                    "caller_visible": True,
                    "existing_test": True,
                    "new_characterization_test": None,
                    "cleanup_candidate": False,
                },
            ],
            "behavior_contracts": (
                "For each IN_SCOPE handler, exact exception type (Exception), exact "
                "success/failure outputs, error-record shape, and per-file call order "
                "were pinned by tests/test_v4_1_r7_exception_boundaries_characterization.py "
                "before the main.py cleanup; the same tests were re-run unchanged after "
                "the cleanup and still pass."
            ),
            "tests_added": [
                "tests/test_v4_1_r7_exception_boundaries_characterization.py"
            ],
        },
        "cleanup_gate": "OPEN",
        "authorized_cleanups": [
            {
                "path": "legacy_documenter/main.py",
                "symbol": "analyze_repository",
                "classification": "SAFE_LOCAL_CLEANUP",
                "shape": "replace duplicated tiny local patterns with one internal helper",
            }
        ],
        "deferred_cleanups": [
            {
                "path": "legacy_documenter/documentation/resume.py",
                "classification": "CHARACTERIZED_BUT_DEFER",
                "reason": "High-risk fence; all handlers entangled with provider call sequence.",
            }
        ],
        "cleanups_performed": 1,
        "compatibility": {
            "public_imports": "PASS",
            "public_signatures": "PASS",
            "success_results": "PASS",
            "failure_results": "PASS",
            "exception_types": "PASS",
            "exception_messages": "PASS",
            "ordering": "PASS",
            "side_effects": "PASS",
            "partial_results": "PASS",
        },
        "provider_boundary_changes": 0,
        "r6_deferred_groups_preserved": "PASS",
        "production_files_added": [],
        "production_files_modified": ["legacy_documenter/main.py"],
        "approved_artifact_integrity": "PASS",
        "r0_frozen_inventory_modified": False,
        "tests": "1566_PASS_0_FAIL_0_SKIP",
        "readiness": "READY",
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
