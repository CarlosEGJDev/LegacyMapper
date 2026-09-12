"""Builds the two V4.1-R0 deterministic artifacts.

`build_inventory()` -> `output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json`
`build_plan()`      -> `output/v4_1_r0/V4_1_REFACTOR_PLAN.json`

Both functions are pure (no filesystem write) so they can be called twice in
one process, or across two processes, to prove determinism byte-for-byte.
The mechanical parts (file/line/class/function counts, dependency edges,
exception-boundary counts, docstring/type-hint ratios) come from `inventory.py`
re-parsing the current source tree. The qualitative parts (which duplication
is safe to consolidate, which module mixes responsibilities, which name is
confusing, the roadmap) are curated findings recorded here as data, grounded
in the specific evidence cited in each entry's `evidence` field -- these are
judgment calls a mechanical scan cannot make safely, per the R0 spec's
explicit warning against pattern-matching abstraction recommendations.
"""
from __future__ import annotations

from pathlib import Path

from . import inventory as inv

SCHEMA_VERSION = "V4.1-R0-1"


def _production_inventory(root: Path) -> tuple[list[dict[str, object]], list[Path]]:
    files = inv.iter_production_files(root)
    records = [inv.analyze_file(p, root) for p in files]
    return records, files


def _largest_modules(records: list[dict[str, object]], top_n: int = 20) -> list[dict[str, object]]:
    ranked = sorted(records, key=lambda r: (-r["line_count"], r["path"]))[:top_n]
    out = []
    for r in ranked:
        if r["line_count"] > 300:
            status = "REFACTOR_CANDIDATE"
        elif r["line_count"] > 200:
            status = "REVIEW"
        else:
            status = "OK"
        if r["path"] in _DO_NOT_TOUCH:
            status = "DO_NOT_TOUCH_WITHOUT_DESIGN_DECISION"
        elif r["path"] in _CHARACTERIZATION_FIRST:
            status = "CHARACTERIZATION_REQUIRED"
        out.append({"path": r["path"], "line_count": r["line_count"], "classification": status})
    return out


# Historical, weakly-characterized orchestration/parsing modules identified by
# direct inspection (large, many responsibility signals, few/no dedicated
# unit tests targeting internal seams) -- see the R0 result document.
_DO_NOT_TOUCH = {
    "legacy_documenter/extractors/database_extractor.py",
    "legacy_documenter/analysis/flow_resolver.py",
}
_CHARACTERIZATION_FIRST = {
    "legacy_documenter/knowledge/readiness.py",
    "legacy_documenter/documentation/consistency.py",
    "legacy_documenter/documentation/resume.py",
    "legacy_documenter/documentation/hierarchical.py",
}


def _largest_classes(root: Path, files: list[Path]) -> list[dict[str, object]]:
    ranked = inv.largest_classes(root, files, 20)
    for r in ranked:
        if r["method_count"] >= 20:
            r["classification"] = "DO_NOT_TOUCH_WITHOUT_DESIGN_DECISION" if r["path"] in _DO_NOT_TOUCH else "REFACTOR_CANDIDATE"
        elif r["method_count"] >= 10:
            r["classification"] = "REVIEW"
        else:
            r["classification"] = "OK"
    return ranked


def _largest_functions(root: Path, files: list[Path]) -> list[dict[str, object]]:
    ranked = inv.largest_functions(root, files, 20)
    for r in ranked:
        if r["qualified_name"].startswith(("build_", "render_")):
            r["classification"] = "REVIEW"  # deterministic, low-risk, but long
        elif r["line_count"] >= 100:
            r["classification"] = "CHARACTERIZATION_REQUIRED"
        elif r["line_count"] >= 50:
            r["classification"] = "REVIEW"
        else:
            r["classification"] = "OK"
    return ranked


def _responsibility_candidates(records: list[dict[str, object]]) -> list[dict[str, object]]:
    """Modules that mix real, distinct concerns -- cohesion-based, not a
    line-count trigger (per R0 spec section D)."""
    curated = [
        {
            "path": "legacy_documenter/knowledge/readiness.py",
            "responsibilities": ["document parsing", "evidence-closure computation", "file I/O", "gate orchestration"],
            "evidence": "Single module reads manuals/artifacts from disk, computes closure/eligibility over records, and writes four fixed output files, per DEBT-002 (docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md).",
            "classification": "REFACTOR_CANDIDATE",
            "risk": "MEDIUM",
        },
        {
            "path": "legacy_documenter/extractors/database_extractor.py",
            "responsibilities": ["VB.NET/SQL text parsing", "domain classification of database access", "heuristic inference"],
            "evidence": "Largest class in the repository (DatabaseExtractor, 27 methods, 395 lines); mixes low-level text scanning with higher-level interpretation decisions in the same class.",
            "classification": "CHARACTERIZATION_REQUIRED",
            "risk": "VERY_HIGH",
        },
        {
            "path": "legacy_documenter/analysis/flow_resolver.py",
            "responsibilities": ["control-flow graph construction", "cross-file call resolution", "narrative/report text assembly"],
            "evidence": "FunctionalFlowResolver (24 methods, 316 lines) combines structural resolution with output formatting in one class.",
            "classification": "CHARACTERIZATION_REQUIRED",
            "risk": "VERY_HIGH",
        },
        {
            "path": "legacy_documenter/documentation/resume.py",
            "responsibilities": ["orchestration/resume-state tracking", "aggregation", "file I/O"],
            "evidence": "6 exception handlers incl. 1 broad `except Exception`; combines checkpoint/resume state with aggregation and disk access. No dedicated unit test module targets it directly by name.",
            "classification": "CHARACTERIZATION_REQUIRED",
            "risk": "HIGH",
        },
        {
            "path": "legacy_documenter/main.py",
            "responsibilities": ["CLI argument handling", "pipeline orchestration", "broad exception-to-exit-code translation"],
            "evidence": "4 broad `except Exception` handlers translate internal stage failures into CLI exit behavior; this is a legitimate top-level boundary (see exception_candidates) but it also decides pipeline ordering, which is a second responsibility.",
            "classification": "REVIEW",
            "risk": "MEDIUM",
        },
        {
            "path": "legacy_documenter/llm/providers/copilot.py",
            "responsibilities": ["provider protocol/HTTP-shaped adapter logic", "response parsing", "error translation"],
            "evidence": "4 broad `except Exception` handlers around asyncio/subprocess-shaped provider calls; appropriate for an adapter boundary (see exception_candidates) but combined with response-shape parsing in the same class.",
            "classification": "REVIEW",
            "risk": "MEDIUM",
        },
        {
            "path": "legacy_documenter/analysis/deep_source.py",
            "responsibilities": ["source-text parsing", "domain-object construction", "filesystem access", "provider-shaped invocation", "serialization", "validation", "orchestration"],
            "evidence": "Highest responsibility-signal count of any file in the repository (7 distinct signals in only 163 lines); "
                        "small size does not offset the number of distinct concerns present -- a genuine cohesion "
                        "finding, not a line-count trigger.",
            "classification": "REFACTOR_CANDIDATE",
            "risk": "HIGH",
        },
    ]
    known_paths = {r["path"] for r in records}
    return [c for c in curated if c["path"] in known_paths]


def _duplication_candidates() -> list[dict[str, object]]:
    return [
        {
            "id": "DUP-001",
            "pattern": "JSON contract renderer (`render_<x>_contract_json`)",
            "files": [
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
            "evidence": "All 11 render_* functions have the identical one-line body "
                        "`json.dumps(build_X(), ensure_ascii=False, sort_keys=True, separators=(\",\", \":\"))` "
                        "-- verified by direct grep across every knowledge sub-package's contract_report.py, "
                        "differing only in which builder function is called.",
            "classification": "SAFE_TO_CONSOLIDATE",
            "risk": "LOW",
            "tracked_as": "DEBT-001",
            "recommended_action": "Extract a single `render_contract_json(builder) -> str` helper "
                                   "(e.g. `legacy_documenter/knowledge/_shared/json_rendering.py`) and have each "
                                   "contract_report.py call it; output is byte-identical because the call is textually "
                                   "identical today. Each package's `build_<x>_contract()` stays where it is -- only the "
                                   "serialization line moves.",
        },
        {
            "id": "DUP-002",
            "pattern": "`build_<x>_contract()` plain-dict-builder shape",
            "files": [
                "legacy_documenter/knowledge/*/contract_report.py",
                "legacy_documenter/knowledge/*/example_report.py",
            ],
            "evidence": "Each builder assembles a hand-written nested dict describing that round's own contract; "
                        "field names, nesting, and semantics differ per round (R7 relation contract vs R10 canonical "
                        "contract vs R12 plugin contract are not interchangeable).",
            "classification": "SIMILAR_BUT_SEMANTICALLY_DISTINCT",
            "risk": "MEDIUM",
            "tracked_as": "TD-003",
            "recommended_action": "Do not merge builder bodies. A shared *shape* (e.g. a TypedDict for the envelope "
                                   "fields common to every contract report) could be introduced without touching "
                                   "per-round field content, but only after per-round field-set equivalence is "
                                   "explicitly verified round by round.",
        },
        {
            "id": "DUP-003",
            "pattern": "generic `requests` batch-parameter naming",
            "files": [
                "legacy_documenter/knowledge/classification/service.py",
                "legacy_documenter/knowledge/proposals/service.py",
                "legacy_documenter/knowledge/relations/service.py",
            ],
            "evidence": "`classify_batch(self, requests: list[ClassificationRequest])`, "
                        "`create_proposal_batch(self, requests: list[ProposalRequest])`, "
                        "`create_relation_batch(self, requests: list[RelationRequest])` -- confirmed by direct grep; "
                        "matches DEBT-003 exactly.",
            "classification": "NEEDS_CHARACTERIZATION",
            "risk": "LOW",
            "tracked_as": "DEBT-003",
            "recommended_action": "Not a behavior duplication at all -- three distinct methods that happen to reuse a "
                                   "generic parameter name. Rename the parameter only (e.g. `classification_requests`), "
                                   "which is source-only and has no serialized-contract impact; still requires a full "
                                   "regression run since it is a public method signature.",
        },
        {
            "id": "DUP-004",
            "pattern": "per-package `models.py` + `service.py` + `enums.py` V4 round layout",
            "files": ["legacy_documenter/knowledge/*/models.py", "legacy_documenter/knowledge/*/service.py"],
            "evidence": "Every V4 round package (approval, canonical, classification, ingestion, projection, "
                        "plugin_projection, proposals, provenance, relations, temporal) follows the same file-role "
                        "convention, confirmed by directory listing; this is intentional consistency, not duplication.",
            "classification": "DO_NOT_CONSOLIDATE",
            "risk": "LOW",
            "tracked_as": None,
            "recommended_action": "Keep as-is. This is the desired 'one recognizable module role per round' pattern "
                                   "the development standard asks for, not code to merge.",
        },
    ]


def _type_safety_candidates(records: list[dict[str, object]]) -> list[dict[str, object]]:
    weakest = sorted(
        [r for r in records if r["function_count"] > 0],
        key=lambda r: (r["typed_functions_percent"], r["path"]),
    )[:15]
    return [
        {
            "path": r["path"],
            "typed_functions_percent": r["typed_functions_percent"],
            "function_count": r["function_count"],
            "note": "Below-average return/parameter annotation coverage for this file; a diagnostic signal, "
                    "not a lint failure -- `-> None` and dunder methods are sometimes legitimately unannotated.",
        }
        for r in weakest
    ]


def _documentation_candidates(records: list[dict[str, object]]) -> list[dict[str, object]]:
    weakest = sorted(records, key=lambda r: (r["docstring_coverage_percent"], r["path"]))[:15]
    return [
        {
            "path": r["path"],
            "docstring_coverage_percent": r["docstring_coverage_percent"],
            "module_docstring_present": r["module_docstring_present"],
        }
        for r in weakest
    ]


def _naming_candidates() -> list[dict[str, object]]:
    return [
        {
            "current_name": "requests (parameter)",
            "locations": [
                "legacy_documenter/knowledge/classification/service.py:classify_batch",
                "legacy_documenter/knowledge/proposals/service.py:create_proposal_batch",
                "legacy_documenter/knowledge/relations/service.py:create_relation_batch",
            ],
            "reason": "Generic name shadows the well-known `requests` HTTP library and gives no hint of which "
                      "request type; confirmed distinct per DUP-003/DEBT-003.",
            "suggested_name": "classification_requests / proposal_requests / relation_requests",
            "public_api_impact": "Parameter rename only; positional callers unaffected, keyword callers (if any) "
                                  "would need updating -- verify via repository-wide grep before renaming.",
            "compatibility_strategy": "NO_WRAPPER (parameter names are not part of the JSON contract; grep confirmed "
                                       "no keyword-argument call site uses `requests=`).",
        },
        {
            "current_name": "copilot_pilot.py / CopilotPilot-shaped helpers",
            "locations": ["legacy_documenter/llm/copilot_pilot.py"],
            "reason": "'Pilot' does not describe a responsibility (adapter, client, session?); a C#-background "
                      "reader cannot infer behavior from the name alone.",
            "suggested_name": "copilot_session.py (module), matching its actual role driving a Copilot Chat session",
            "public_api_impact": "Internal to legacy_documenter.llm; verify no external import path is documented "
                                  "in the V4 manuals before moving.",
            "compatibility_strategy": "REEXPORT (keep a thin `copilot_pilot.py` module re-exporting from the new "
                                       "location for one round, per the standard's 'small wrappers when moving "
                                       "implementation' rule).",
        },
        {
            "current_name": "legacy_documenter/quality/maintainability_audit.py: `audit`",
            "locations": ["legacy_documenter/quality/maintainability_audit.py"],
            "reason": "`audit()` is a generic verb with no object; unclear from the call site alone what it audits "
                      "or returns without opening the module.",
            "suggested_name": "build_maintainability_inventory",
            "public_api_impact": "Referenced only from `__main__` in the same file and from its own historical V3 "
                                  "round tests; grep found no cross-package import.",
            "compatibility_strategy": "COMPATIBILITY_WRAPPER (keep `audit = build_maintainability_inventory` alias "
                                       "for one round; V3 round result documents may reference the literal name).",
        },
        {
            "current_name": "legacy_documenter/context/composer.py, resolver.py, context_builder.py, "
                             "system_context_builder.py (four *_builder/composer/resolver names in one package)",
            "locations": ["legacy_documenter/context/"],
            "reason": "Four similarly-named orchestration files in one package (`composer`, `resolver`, "
                      "`context_builder`, `system_context_builder`) make it hard to guess which one is the entry "
                      "point without reading all four.",
            "suggested_name": "No rename proposed yet -- first characterize which module is the public entry point, "
                               "then consider renaming the others to reflect their narrower role (e.g. "
                               "`file_context_resolver.py`).",
            "public_api_impact": "Unknown until characterized; historical V1-V2 package with no dedicated per-file "
                                  "test module found by name.",
            "compatibility_strategy": "DO_NOT_MOVE (until a characterization pass exists for this package).",
        },
    ]


def _exception_candidates(records: list[dict[str, object]]) -> list[dict[str, object]]:
    curated_class = {
        "legacy_documenter/main.py": ("JUSTIFIED_BOUNDARY", "Top-level CLI entry point translating internal stage failures into a safe exit path; this is the documented outermost boundary."),
        "legacy_documenter/llm/providers/copilot.py": ("JUSTIFIED_BOUNDARY", "Provider adapter boundary converting external Copilot Chat/subprocess failures into a domain `ProviderError`, matching TD-002's own stated plan."),
        "legacy_documenter/llm/providers/gemini.py": ("JUSTIFIED_BOUNDARY", "Provider adapter boundary converting external HTTP/urllib failures into a domain `ProviderError`, matching TD-002."),
        "legacy_documenter/llm/copilot_pilot.py": ("JUSTIFIED_BOUNDARY", "Wraps an external interactive session; single broad handler at the outer call boundary."),
        "legacy_documenter/documentation/generator.py": ("HISTORICAL_COMPATIBILITY", "V1-era orchestrator; broad handler predates the V4 domain-exception style. No behavior regression found, but a future round should verify it isn't silently swallowing an error worth surfacing."),
        "legacy_documenter/documentation/hierarchical.py": ("HISTORICAL_COMPATIBILITY", "Same V1-era orchestration pattern as generator.py."),
        "legacy_documenter/documentation/resume.py": ("REFACTOR_CANDIDATE", "6 handlers in one module including a broad one guarding checkpoint/resume I/O; higher handler density than peers, worth narrowing to specific exception types once characterization tests exist."),
        "legacy_documenter/documentation/systematic.py": ("HISTORICAL_COMPATIBILITY", "Same V1-era orchestration pattern as generator.py."),
    }
    out = []
    for r in records:
        obs = r.get("exception_boundary_observations", {})
        if obs.get("except_exception") or obs.get("bare_except"):
            classification, note = curated_class.get(r["path"], ("REFACTOR_CANDIDATE", "Broad exception handler found; not individually reviewed in R0, needs a closer look before any change."))
            out.append({
                "path": r["path"],
                "except_exception_count": obs.get("except_exception", 0),
                "bare_except_count": obs.get("bare_except", 0),
                "classification": classification,
                "note": note,
            })
    return out


def _side_effect_candidates(records: list[dict[str, object]]) -> list[dict[str, object]]:
    fs = sorted(r["path"] for r in records if r["filesystem_access"])
    net = sorted(r["path"] for r in records if r["network_or_provider_access"])
    return [
        {
            "kind": "filesystem_access",
            "file_count": len(fs),
            "files": fs,
            "observation": "Filesystem access is spread across extractors/scanner (reading the read-only legacy "
                            "repository), documentation/exporters (writing generated output), and two isolated "
                            "knowledge-package writers (`projection/disk_io.py`, `readiness.py`) -- consistent with "
                            "R13's own finding that only those two knowledge modules touch disk.",
        },
        {
            "kind": "network_or_provider_access",
            "file_count": len(net),
            "files": net,
            "observation": "Network/provider access is confined to `legacy_documenter/llm/` (core, providers/, "
                            "copilot_pilot.py) plus name-hint matches inside knowledge services that only *reference* "
                            "provider-shaped types (e.g. `AI_INTERPRETATION` provenance) without importing a network "
                            "module -- verified no `legacy_documenter/knowledge/**` file imports urllib/requests/socket "
                            "per V4-R13's own AST scan, which this inventory's import list corroborates.",
        },
    ]


def _known_debt() -> list[dict[str, object]]:
    return [
        {
            "id": "TD-001", "source": "output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json",
            "original_description": "Reformatting historical R7/R8 one-line contracts would create broad noisy diffs without semantic benefit.",
            "current_relevance": "Still accurate; R7-R12 contract_report.py files still use compact literal formatting.",
            "affected_files": ["legacy_documenter/knowledge/*/contract_report.py"],
            "risk": "LOW", "recommended_round": "V4.1-R8",
            "recommended_action": "Reformat only opportunistically inside a round that already touches the file for another reason (per its own original plan); do not run a repository-wide reformat.",
        },
        {
            "id": "TD-002", "source": "output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json",
            "original_description": "Broad boundaries deliberately convert external SDK/HTTP failures into safe domain responses.",
            "current_relevance": "Still accurate and confirmed in this round's exception scan: legacy_documenter/llm/providers/{copilot,gemini}.py and llm/copilot_pilot.py hold every remaining broad `except Exception` at the true provider boundary.",
            "affected_files": ["legacy_documenter/llm/providers/copilot.py", "legacy_documenter/llm/providers/gemini.py", "legacy_documenter/llm/copilot_pilot.py"],
            "risk": "LOW", "recommended_round": "V4.1-R7",
            "recommended_action": "Keep the boundary; consider narrowing to a documented provider-specific exception tuple once each provider's real failure taxonomy is contract-tested, exactly as originally planned. No behavior change without new characterization tests proving the narrower catch still degrades safely.",
        },
        {
            "id": "TD-003", "source": "output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json",
            "original_description": "Similar helpers have different validated round semantics and cannot be merged by textual similarity.",
            "current_relevance": "Still accurate; DUP-002 in this inventory found per-round `build_<x>_contract()` builders are textually similar but semantically distinct (see duplication_candidates).",
            "affected_files": ["legacy_documenter/knowledge/*/contract_report.py", "legacy_documenter/knowledge/*/example_report.py"],
            "risk": "MEDIUM", "recommended_round": "V4.1-R6",
            "recommended_action": "Only the JSON-serialization tail (DUP-001/DEBT-001) is safe to consolidate. Builder bodies (DUP-002) stay separate unless a future round explicitly verifies field-by-field equivalence for a specific pair.",
        },
        {
            "id": "TD-004", "source": "output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json",
            "original_description": "Splitting discovery and historical round orchestration now risks ordering and output compatibility.",
            "current_relevance": "Still accurate; `legacy_documenter/main.py`, `documentation/resume.py`, `documentation/hierarchical.py` remain large multi-responsibility orchestrators with no dedicated characterization test module targeting their internal ordering.",
            "affected_files": ["legacy_documenter/main.py", "legacy_documenter/documentation/resume.py", "legacy_documenter/documentation/hierarchical.py", "legacy_documenter/documentation/generator.py"],
            "risk": "VERY_HIGH", "recommended_round": "V4.1-R5 (characterization first)",
            "recommended_action": "Add characterization tests capturing current end-to-end output for representative fixtures before any extraction; extract only behind those tests, in small steps, per the item's own original plan.",
        },
        {
            "id": "TD-005", "source": "output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json",
            "original_description": "Ambiguous nested historical JSON shapes were not annotated with misleading object/Any types.",
            "current_relevance": "Still accurate; type_safety_candidates in this inventory shows the lowest-annotation-coverage files remain concentrated in the historical `documentation/`, `analysis/`, and `extractors/` packages.",
            "affected_files": ["legacy_documenter/documentation/*.py", "legacy_documenter/analysis/*.py", "legacy_documenter/extractors/*.py"],
            "risk": "MEDIUM", "recommended_round": "V4.1-R2 / V4.1-R4 (incremental, per touched boundary)",
            "recommended_action": "Introduce narrow TypedDict/dataclass models only at boundaries a round is already modifying for another reason; do not retrofit typing repository-wide in one pass.",
        },
        {
            "id": "DEBT-001", "source": "docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md",
            "original_description": "every R7-R12 package repeats the same plain-dict-builder + sorted-key JSON-renderer pattern in its contract_report.py. No behavioral defect; a shared thin helper is a safe future refactor candidate.",
            "current_relevance": "Confirmed with hard evidence in this round: DUP-001 shows all 11 `render_*_contract_json` functions share an identical one-line body.",
            "affected_files": ["legacy_documenter/knowledge/*/contract_report.py"],
            "risk": "LOW", "recommended_round": "V4.1-R1",
            "recommended_action": "Extract the shared renderer helper described in DUP-001. Output is byte-identical; verify with the existing per-round contract/example artifact hash tests.",
        },
        {
            "id": "DEBT-002", "source": "docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md",
            "original_description": "legacy_documenter/knowledge/readiness.py (the historical V3-R9 gate) mixes document parsing, evidence-closure computation, and file I/O in one large module. Unmodified V3 code; left as-is.",
            "current_relevance": "Still accurate; readiness.py is 292 lines, VERY_HIGH risk_category in this inventory (multiple responsibility signals + broad-ish orchestration), and is exercised by the entry-gate command every round.",
            "affected_files": ["legacy_documenter/knowledge/readiness.py"],
            "risk": "HIGH", "recommended_round": "V4.1-R4",
            "recommended_action": "Decompose into parsing / evidence-closure computation / file I/O modules behind a compatibility wrapper that preserves `python -m legacy_documenter.knowledge.readiness` and the `run()` entry point exactly.",
        },
        {
            "id": "DEBT-003", "source": "docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md",
            "original_description": "generic requests/request batch-parameter naming repeats across proposals/relations/classification services; harmless, but a shared naming-convention note could help future readers.",
            "current_relevance": "Confirmed with hard evidence in this round: DUP-003/naming_candidates lists the exact three method signatures.",
            "affected_files": ["legacy_documenter/knowledge/classification/service.py", "legacy_documenter/knowledge/proposals/service.py", "legacy_documenter/knowledge/relations/service.py"],
            "risk": "LOW", "recommended_round": "V4.1-R8",
            "recommended_action": "Rename the parameter (not the type) to a request-kind-specific name; parameter names are not part of the JSON contract, so this is a documentation-grade, low-risk rename.",
        },
        {
            "id": "REG-002-CANDIDATE", "source": "V4.1-R0 entry gate (this round)",
            "original_description": "`tests/test_v4_r14_manuals_and_final_baseline.py::DeterminismTests.test_baseline_matches_on_disk_artifact` fails on a clean current checkout: it rebuilds `V4_FINAL_BASELINE.json` live from the *current* `PROJECT_STATE.json` (`latest_approved_round=V4-R14`) and compares it to the frozen on-disk artifact, which was generated and hashed before V4-R14 itself was approved (`latest_approved_round=V4-R13` at generation time). Same defect shape as REG-001 (R13): a generated snapshot compared against a moving-target live value.",
            "current_relevance": "Newly discovered by this round's entry gate (1379 PASS / 1 FAIL out of 1380, not the expected clean 1380 PASS). Not fixed here: R0 is analysis-only and TEST_SEMANTIC_MODIFICATION_ALLOWED=false.",
            "affected_files": ["tests/test_v4_r14_manuals_and_final_baseline.py", "output/v4_r14/V4_FINAL_BASELINE.json"],
            "risk": "LOW", "recommended_round": "V4.1-R1 (test-only fix, first)",
            "recommended_action": "Apply the same fix shape as REG-001: change the test to compare against the round-in-progress-at-generation-time value recorded inside the frozen artifact itself, or treat `latest_approved_round` as an 'as of generation' field excluded from the live-rebuild comparison, instead of asserting live-vs-frozen equality on a field that is expected to advance. Test-only change; no production code or contract touched.",
        },
    ]


def _characterization_needs() -> list[dict[str, object]]:
    return [
        {
            "path": "legacy_documenter/extractors/database_extractor.py",
            "classification": "TOO_RISKY_WITHOUT_DESIGN_REVIEW",
            "behaviors_to_freeze": [
                "exact set and ordering of detected database access findings for a representative VB.NET fixture",
                "classification labels assigned to ambiguous/ADO.NET-shaped access patterns",
            ],
        },
        {
            "path": "legacy_documenter/analysis/flow_resolver.py",
            "classification": "TOO_RISKY_WITHOUT_DESIGN_REVIEW",
            "behaviors_to_freeze": [
                "resolved call graph shape for a representative multi-file fixture",
                "narrative/report text emitted for at least one branch/loop/error-path scenario",
            ],
        },
        {
            "path": "legacy_documenter/knowledge/readiness.py",
            "classification": "ADDITIONAL_CHARACTERIZATION_REQUIRED",
            "behaviors_to_freeze": [
                "the four fixed output files' exact content for the existing fixture set",
                "the ineligible-record count and every `checks` boolean for at least one PASS and one FAIL scenario",
            ],
        },
        {
            "path": "legacy_documenter/documentation/resume.py",
            "classification": "ADDITIONAL_CHARACTERIZATION_REQUIRED",
            "behaviors_to_freeze": [
                "checkpoint/resume state transitions across an interrupted-then-resumed run",
                "which of the 6 exception paths is exercised by which failure fixture",
            ],
        },
        {
            "path": "legacy_documenter/analysis/deep_source.py",
            "classification": "ADDITIONAL_CHARACTERIZATION_REQUIRED",
            "behaviors_to_freeze": [
                "the exact set of interpreted findings for a representative deep-source fixture",
                "which findings are attributed to which of its 7 mixed responsibilities, so extraction can be verified per concern",
            ],
        },
        {
            "path": "legacy_documenter/knowledge/*/contract_report.py (DUP-001 extraction)",
            "classification": "EXISTING_TESTS_SUFFICIENT",
            "behaviors_to_freeze": [
                "existing per-round contract/example SHA-256 hash tests already pin the exact serialized bytes; "
                "the DUP-001 extraction changes only where the identical `json.dumps(...)` call is written, not its arguments or output",
            ],
        },
    ]


def _public_compatibility(records: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {"symbol": "legacy_documenter.main.main / analyze_repository", "usage_evidence": "Imported by top-level main.py and tests/test_v1*.py.", "compatibility_strategy": "DO_NOT_MOVE"},
        {"symbol": "legacy_documenter.knowledge.readiness.run (module __main__ + `python -m ...`)", "usage_evidence": "Documented CLI entry point in docs/PROJECT_RECOVERY.md and every round's entry gate.", "compatibility_strategy": "COMPATIBILITY_WRAPPER"},
        {"symbol": "legacy_documenter.knowledge.*.contract_report.render_*_contract_json / build_*_contract", "usage_evidence": "Referenced by each package's own contract/example hash tests (grep-confirmed).", "compatibility_strategy": "REEXPORT (keep function name and location; only its internal serialization call moves to the shared helper)"},
        {"symbol": "legacy_documenter.quality.maintainability_audit.audit / write_audit", "usage_evidence": "Referenced from its own `__main__` block only; grep found no cross-package import.", "compatibility_strategy": "COMPATIBILITY_WRAPPER"},
        {"symbol": "legacy_documenter.llm.* (facade re-export of .core)", "usage_evidence": "`legacy_documenter/llm/providers/copilot.py` imports from the `legacy_documenter.llm` facade rather than `legacy_documenter.llm.core` directly (see dependency_findings self-loop).", "compatibility_strategy": "NO_WRAPPER (already public via the facade; a provider importing from `.core` directly instead of the facade is an internal-only clarity change)"},
    ]


def _risk_summary(records: list[dict[str, object]]) -> dict[str, object]:
    counts: dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "VERY_HIGH": 0}
    for r in records:
        counts[r["risk_category"]] = counts.get(r["risk_category"], 0) + 1
    return {
        "files_by_risk_category": counts,
        "very_high_risk_files": sorted(r["path"] for r in records if r["risk_category"] == "VERY_HIGH"),
        "high_risk_files": sorted(r["path"] for r in records if r["risk_category"] == "HIGH"),
    }


def build_inventory(root: Path) -> dict[str, object]:
    """Builds the full V4.1-R0 maintainability inventory payload (no I/O)."""
    records, files = _production_inventory(root)
    edges = inv.dependency_edges(root, files)
    cycles = inv.find_cycles(edges)
    return {
        "schema_version": SCHEMA_VERSION,
        "baseline": {
            "phase": "V4.1", "round": "V4.1-R0",
            "v4_status": "FORMALLY_CLOSED", "latest_completed_round": "V4-R14",
            "latest_approved_round": "V4-R14",
            "baseline_test_count": 1380,
            "readiness": "READY", "ai_knowledge_allowed": True, "ai_knowledge_generated": False,
            "provider_calls": 0, "real_llm_calls": 0,
            "entry_gate_result": "PASS_WITH_ONE_PRE_EXISTING_TEST_FAILURE",
            "entry_gate_note": "1379 PASS / 1 FAIL out of 1380 collected tests; see known_debt REG-002-CANDIDATE. "
                                "No production code, contract, or test semantics were changed to investigate this.",
        },
        "production_inventory": records,
        "largest_modules": _largest_modules(records),
        "largest_classes": _largest_classes(root, files),
        "largest_functions": _largest_functions(root, files),
        "responsibility_candidates": _responsibility_candidates(records),
        "duplication_candidates": _duplication_candidates(),
        "type_safety_candidates": _type_safety_candidates(records),
        "documentation_candidates": _documentation_candidates(records),
        "naming_candidates": _naming_candidates(),
        "exception_candidates": _exception_candidates(records),
        "side_effect_candidates": _side_effect_candidates(records),
        "dependency_findings": {
            "module_count": len(edges),
            "cycles_detected": cycles,
            "cycle_note": "The single reported cycle (legacy_documenter.llm <-> .core <-> .providers.copilot) is a "
                          "package-facade self-loop: llm/__init__.py does `from .core import *`, and "
                          "providers/copilot.py imports from the `legacy_documenter.llm` facade instead of "
                          "`legacy_documenter.llm.core` directly. There is no real circular import at module-init "
                          "time (providers is a separate sub-package imported after llm/__init__ completes); this "
                          "is a naming/import-clarity finding, not a behavioral defect.",
            "knowledge_domain_direction_reverified": "PASS",
            "knowledge_domain_direction_note": "plugin_projection.service imports only canonical.service/models and "
                                                "domain; projection.service imports only canonical.service/models, "
                                                "projection.models and domain; neither imports the other, confirming "
                                                "the R13-established acyclic direction still holds.",
        },
        "known_debt": _known_debt(),
        "characterization_needs": _characterization_needs(),
        "public_compatibility": _public_compatibility(records),
        "risk_summary": _risk_summary(records),
    }


ROUNDS = [
    {
        "round_id": "V4.1-R1", "title": "Entry-Gate Fix + Shared Reporting/Serialization Cleanup",
        "objective": "Fix the newly discovered REG-002-CANDIDATE stale-snapshot test defect (test-only), then "
                     "extract the shared JSON contract-renderer helper (DEBT-001/DUP-001).",
        "primary_files": ["tests/test_v4_r14_manuals_and_final_baseline.py",
                           "legacy_documenter/knowledge/*/contract_report.py"],
        "debt_items_addressed": ["REG-002-CANDIDATE", "DEBT-001", "TD-001"],
        "allowed_changes": ["test assertion correction (round-ordinal style, matching REG-001's fix shape)",
                             "new shared internal helper module for JSON rendering", "call-site update to use it"],
        "forbidden_changes": ["any change to a builder function's dict shape", "any contract/example hash change"],
        "characterization_required": False,
        "expected_tests": "All existing per-round contract/example hash tests must still pass unchanged; add tests for the new shared helper.",
        "risk": "LOW",
        "rollback_boundary": "Single commit; revert restores both the prior test and the per-package renderer bodies.",
        "human_review_gate": True,
    },
    {
        "round_id": "V4.1-R2", "title": "Type Safety at Service/Contract Boundaries (Incremental)",
        "objective": "Improve annotation coverage at public service boundaries in the lowest-scoring files "
                     "(type_safety_candidates), and introduce narrow TypedDict models only where TD-005 already "
                     "flagged ambiguous nested JSON at a boundary a round is touching.",
        "primary_files": ["files listed in type_safety_candidates"],
        "debt_items_addressed": ["TD-005"],
        "allowed_changes": ["adding type hints", "adding TypedDict/dataclass models for existing dict shapes"],
        "forbidden_changes": ["changing runtime behavior of any annotated function", "renaming any public symbol"],
        "characterization_required": False,
        "expected_tests": "Full suite unchanged; mypy/typing is diagnostic only (no new dependency), so no new gate is added.",
        "risk": "LOW",
        "rollback_boundary": "Per-file commits; each file's annotations can be reverted independently.",
        "human_review_gate": True,
    },
    {
        "round_id": "V4.1-R3", "title": "Naming Pass Part 1 (Low-Risk Parameter/Internal Renames)",
        "objective": "Apply the naming_candidates entries with NO_WRAPPER/REEXPORT compatibility strategy "
                     "(DEBT-003 requests-parameter rename; maintainability_audit.audit alias).",
        "primary_files": ["legacy_documenter/knowledge/classification/service.py",
                           "legacy_documenter/knowledge/proposals/service.py",
                           "legacy_documenter/knowledge/relations/service.py",
                           "legacy_documenter/quality/maintainability_audit.py"],
        "debt_items_addressed": ["DEBT-003"],
        "allowed_changes": ["parameter renames", "adding a compatibility alias for a renamed function"],
        "forbidden_changes": ["changing any method's positional/keyword calling contract observed by tests",
                               "removing the old name without a wrapper"],
        "characterization_required": False,
        "expected_tests": "Full suite unchanged; add a test asserting the compatibility alias still resolves.",
        "risk": "LOW",
        "rollback_boundary": "Per-file commits.",
        "human_review_gate": True,
    },
    {
        "round_id": "V4.1-R4", "title": "Readiness Module Decomposition",
        "objective": "Split legacy_documenter/knowledge/readiness.py (DEBT-002) into parsing / evidence-closure "
                     "computation / file-I/O modules behind a compatibility wrapper, only after characterization "
                     "tests freeze its current output for the existing fixture set.",
        "primary_files": ["legacy_documenter/knowledge/readiness.py"],
        "debt_items_addressed": ["DEBT-002"],
        "allowed_changes": ["splitting into new internal modules", "adding a `readiness.py` compatibility wrapper "
                             "re-exporting `run()` and the CLI `__main__` behavior unchanged"],
        "forbidden_changes": ["changing any of the four output files' schema or content",
                               "changing the `checks`/`readiness` boolean logic"],
        "characterization_required": True,
        "expected_tests": "New characterization tests pinning current output for at least one PASS and one FAIL "
                           "fixture, added before the split; full suite must still pass after.",
        "risk": "MEDIUM",
        "rollback_boundary": "Single round, single revert; wrapper keeps the public entry point stable throughout.",
        "human_review_gate": True,
    },
    {
        "round_id": "V4.1-R5", "title": "Large Historical Orchestrators -- Characterization Only",
        "objective": "Add characterization tests for the highest-risk historical modules: the mechanical "
                     "VERY_HIGH set (deep_source.py, documentation/{generator,hierarchical,resume,systematic}.py, "
                     "knowledge/readiness.py -- readiness.py is covered separately in R4) plus the two HIGH-risk, "
                     "oversized-class modules found by direct reading (database_extractor.py's 27-method class, "
                     "flow_resolver.py's 24-method class). Perform NO extraction/splitting in this round -- "
                     "characterization first, extraction only in a later, separately scoped round once tests exist "
                     "and a design decision is made per module.",
        "primary_files": ["legacy_documenter/extractors/database_extractor.py",
                           "legacy_documenter/analysis/flow_resolver.py",
                           "legacy_documenter/analysis/deep_source.py",
                           "legacy_documenter/documentation/resume.py",
                           "legacy_documenter/documentation/hierarchical.py",
                           "legacy_documenter/documentation/generator.py",
                           "legacy_documenter/documentation/systematic.py"],
        "debt_items_addressed": ["TD-004"],
        "allowed_changes": ["adding characterization tests only"],
        "forbidden_changes": ["any production code change"],
        "characterization_required": True,
        "expected_tests": "New characterization test modules for each of the four files, run against existing fixtures.",
        "risk": "LOW (test-only round)",
        "rollback_boundary": "New test files only; trivially revertible.",
        "human_review_gate": True,
    },
    {
        "round_id": "V4.1-R6", "title": "Extraction Behind Characterization (Design-Reviewed, Per Module)",
        "objective": "For each VERY_HIGH-risk module characterized in R5, and only after an explicit Technical "
                     "Lead design decision on the target shape, extract responsibilities in small, independently "
                     "reviewable steps (e.g. separate DatabaseExtractor's text-scanning from its classification "
                     "decisions).",
        "primary_files": ["one module per sub-round; not batched"],
        "debt_items_addressed": ["TD-004 (continued)"],
        "allowed_changes": ["extraction into new internal collaborator classes/modules within the same package",
                             "compatibility wrapper preserving the existing public class/function"],
        "forbidden_changes": ["any change to characterization-test-observed output", "any contract change"],
        "characterization_required": True,
        "expected_tests": "R5's characterization tests plus the full suite must pass unchanged after each extraction.",
        "risk": "HIGH",
        "rollback_boundary": "One module per commit/PR; each is independently revertible.",
        "human_review_gate": True,
    },
    {
        "round_id": "V4.1-R7", "title": "Exception Boundary Review (Non-Provider Modules Only)",
        "objective": "Review the HISTORICAL_COMPATIBILITY-classified broad exception handlers in "
                     "documentation/generator.py, hierarchical.py, systematic.py, and the REFACTOR_CANDIDATE in "
                     "resume.py, narrowing only where characterization tests (from R5) prove the narrower catch "
                     "still degrades safely. Provider boundaries (TD-002) are explicitly left alone in this round.",
        "primary_files": ["legacy_documenter/documentation/generator.py", "legacy_documenter/documentation/hierarchical.py",
                           "legacy_documenter/documentation/systematic.py", "legacy_documenter/documentation/resume.py"],
        "debt_items_addressed": ["TD-002 (documented as intentionally deferred, not addressed)"],
        "allowed_changes": ["narrowing an except clause's exception type where a characterization test proves it safe",
                             "adding an explanatory comment per the development standard's exception-boundary rule"],
        "forbidden_changes": ["touching legacy_documenter/llm/providers/* or copilot_pilot.py (provider boundary, "
                               "deliberately out of scope per TD-002)"],
        "characterization_required": True,
        "expected_tests": "R5 characterization tests plus new negative-path tests proving the narrowed exception "
                           "still surfaces the same safe behavior.",
        "risk": "MEDIUM",
        "rollback_boundary": "Per-file commits.",
        "human_review_gate": True,
    },
    {
        "round_id": "V4.1-R8", "title": "Naming Pass Part 2 + Documentation/Formatting Pass",
        "objective": "Apply the remaining naming_candidates (copilot_pilot.py rename with REEXPORT wrapper, "
                     "context/ package entry-point clarification once characterized), close out TD-001's cosmetic "
                     "reformat opportunistically, and fill documentation_candidates gaps.",
        "primary_files": ["legacy_documenter/llm/copilot_pilot.py", "legacy_documenter/context/*",
                           "files listed in documentation_candidates"],
        "debt_items_addressed": ["TD-001", "remaining naming_candidates"],
        "allowed_changes": ["file rename with re-export wrapper", "adding/expanding docstrings",
                             "cosmetic reformatting of a file already touched for another reason"],
        "forbidden_changes": ["repository-wide reformat", "moving a context/ file without a prior characterization round"],
        "characterization_required": "Only for legacy_documenter/context/* moves",
        "expected_tests": "Full suite unchanged.",
        "risk": "LOW",
        "rollback_boundary": "Per-file commits.",
        "human_review_gate": True,
    },
    {
        "round_id": "V4.1-R9", "title": "Comprehensive Regression & Behavioral Equivalence",
        "objective": "Re-run and extend the V4-R13-style regression/security methodology across every V4.1-R1..R8 "
                     "change: re-hash every approved artifact, re-verify architectural invariants, re-verify the "
                     "knowledge-domain dependency direction, and prove no serialized-contract byte changed except "
                     "where explicitly and intentionally allowed (none are expected).",
        "primary_files": ["repository-wide, read-only verification"],
        "debt_items_addressed": [],
        "allowed_changes": ["new regression/verification test module only"],
        "forbidden_changes": ["any production code change"],
        "characterization_required": False,
        "expected_tests": "Full suite + new V4.1 regression suite, all passing.",
        "risk": "LOW (verification round)",
        "rollback_boundary": "New test file only.",
        "human_review_gate": True,
    },
    {
        "round_id": "V4.1-R10", "title": "Maintainability Final Baseline & Closure",
        "objective": "Regenerate the maintainability diagnostic baseline (not any V4 contract artifact), compare "
                     "it against this round's V4_1_MAINTAINABILITY_INVENTORY.json to show measurable improvement "
                     "against the success criteria, and formally close V4.1 pending Technical Lead approval.",
        "primary_files": ["output/v4_1_r10/*"],
        "debt_items_addressed": ["closes out any remaining LOW-risk items accepted as permanently deferred"],
        "allowed_changes": ["new closure artifacts and result document"],
        "forbidden_changes": ["any production code change in this round itself"],
        "characterization_required": False,
        "expected_tests": "Full suite passing at closure.",
        "risk": "LOW",
        "rollback_boundary": "New artifacts/docs only.",
        "human_review_gate": True,
    },
]


def build_plan(root: Path) -> dict[str, object]:
    """Builds the full V4.1-R0 refactor-plan payload (no I/O)."""
    return {
        "schema_version": SCHEMA_VERSION,
        "phase": "V4.1",
        "goal": "READABILITY_AND_MAINTAINABILITY",
        "behavior_change": "FORBIDDEN",
        "rounds": ROUNDS,
        "global_invariants": [
            "V4 contracts (R7-R14) remain byte-identical unless a round explicitly proves contract/behavioral "
            "equivalence and a Technical Lead approves the change.",
            "Technical-Lead-only approval authority is never altered.",
            "provenance/temporal/relation semantics, proposal/approval lifecycles, deterministic ID derivation, "
            "and the Plugin boundary (R11/R12 non-import direction) are never altered.",
            "Source-code optionality and the read-only legacy-source-repository rule are never altered.",
            "No round introduces a new third-party dependency.",
            "No round performs a real LLM/provider call.",
            "Every round preserves the full existing test suite; a round never weakens or removes an assertion "
            "to force a PASS.",
        ],
        "baseline_tests": 1380,
        "required_final_validation": [
            "python -m unittest discover -s tests (>= current test count, 0 failures)",
            "python -m legacy_documenter.knowledge.readiness (READY, ai_knowledge_generated=false, "
            "provider_calls=0, real_llm_calls=0)",
            "re-hash every artifact listed in output/v4_r10/, output/v4_r11/, output/v4_r12/, output/v4_r13/, "
            "output/v4_r14/ and confirm equality with the SHA-256 values recorded in their closure documents",
            "re-run the V4-R13-style architectural/security invariant scan (Plugin-runtime absence, "
            "plugin_projection/projection non-import, canonical id superset/subset relationship, no "
            "auto-approve function, frozen dataclass immutability)",
            "compare this round's V4_1_MAINTAINABILITY_INVENTORY.json against the R10 closure inventory on the "
            "specific, non-gameable success criteria below",
        ],
        "deferred_items": [
            "TD-002 (provider exception taxonomy narrowing) -- deliberately not addressed in V4.1; revisit only "
            "when a future round introduces contract-tested provider-specific exception types.",
            "DUP-002 / TD-003 builder-body consolidation -- deliberately not merged; only the shared renderer tail "
                "(DUP-001) is extracted in V4.1-R1.",
            "legacy_documenter/context/* package renames -- deferred until a dedicated characterization pass "
                "identifies the true entry point (see naming_candidates).",
            "Any extraction of legacy_documenter/extractors/database_extractor.py or "
                "legacy_documenter/analysis/flow_resolver.py beyond characterization -- explicitly deferred to a "
                "design-reviewed sub-round of V4.1-R6, one module at a time.",
        ],
        "behavior_preservation_strategy": {
            "behavioral_equivalence": "Same observable outcome for the same input (e.g. the same knowledge ids, "
                                       "the same PASS/FAIL readiness verdict) even if internal steps changed.",
            "serialized_contract_equivalence": "Byte-identical JSON/Markdown output for every existing "
                                                "contract/example artifact, proven by the existing SHA-256 tests.",
            "artifact_equivalence": "A specific historical file (e.g. output/v4_r12/V4_PLUGIN_FACING_OUTPUT_EXAMPLE.json) "
                                     "remains byte-identical on disk; V4.1 never regenerates a closed historical artifact.",
            "implementation_equivalence": "NOT required -- V4.1's entire purpose is to change implementation "
                                           "structure (module layout, class boundaries, naming) while preserving the "
                                           "three equivalences above.",
            "minimum_proof_per_round": ["full test suite pass", "readiness gate pass",
                                         "unchanged hash for every artifact the round did not intend to touch",
                                         "new characterization tests pass where required"],
        },
        "deterministic_artifact_preservation": {
            "IMMUTABLE_HISTORICAL_ARTIFACT": ["output/v4_r10/*.json", "output/v4_r11/*.json", "output/v4_r12/*.json",
                                               "output/v4_r13/*.json", "output/v3_final/V3_FINAL_BASELINE.json"],
            "REGENERATABLE_WITH_EQUAL_HASH_REQUIRED": ["output/v4_r14/V4_FINAL_BASELINE.json (only if a future "
                                                        "round intentionally advances it; must reproduce the same "
                                                        "hash unless the Technical Lead explicitly approves a new one)"],
            "CURRENT_STATE_ARTIFACT": ["output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json",
                                        "output/v4_1_r0/V4_1_REFACTOR_PLAN.json",
                                        "PROJECT_STATE.json"],
            "NOT_APPLICABLE": ["output/v1_r1_full/, output/v2_r4_full/, ... (excluded from git; not part of V4.1 scope)"],
        },
        "maintainability_success_criteria": [
            "Zero behavior regressions: full test suite passes at every round, readiness stays READY.",
            "Zero contract/hash drift on every artifact not explicitly and intentionally touched.",
            "DEBT-001/DUP-001 duplication eliminated (one shared renderer, 11 call sites) without any output byte change.",
            "DEBT-002 resolved: readiness.py's three responsibilities separated behind an unchanged public entry point.",
            "DEBT-003 resolved: no remaining generic `requests` parameter name in classification/proposals/relations services.",
            "Reduced VERY_HIGH risk_category file count from this round's baseline (risk_summary.very_high_risk_files: "
            "legacy_documenter/analysis/deep_source.py, legacy_documenter/documentation/{generator,hierarchical,"
            "resume,systematic}.py, legacy_documenter/knowledge/readiness.py) only after each has characterization "
            "tests -- not by reclassification alone. database_extractor.py and flow_resolver.py score HIGH (not "
            "VERY_HIGH) on the mechanical file-level heuristic despite their oversized single classes, which is why "
            "responsibility_candidates/characterization_needs track them separately by class-cohesion evidence "
            "rather than by risk_category alone.",
            "No new oversized orchestrator introduced (no new file added to largest_modules top 5 by line count).",
            "Every symbol whose path moves has an explicit compatibility strategy from public_compatibility, "
            "verified by a passing test exercising the old path.",
            "These criteria are evaluated against re-run inventory numbers, not self-reported percentages, to "
            "avoid gaming (e.g. a file cannot claim reduced responsibility_count by deleting its docstring-derived "
            "signals).",
        ],
    }
