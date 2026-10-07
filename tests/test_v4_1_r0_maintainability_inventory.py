"""V4.1-R0 -- Maintainability Inventory and Refactor Plan: tooling tests.

This is an analysis/planning round: no production capability is added or
changed. These tests validate the *analysis tooling* under `tools/v4_1_r0/`
(deterministic AST inventory + refactor-plan generation) -- not production
semantics. They do not modify, weaken, or duplicate any existing semantic
test.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.v4_1_r0 import inventory as inv
from tools.v4_1_r0 import report

REPO_ROOT = Path(__file__).resolve().parent.parent


class ProductionFileDiscoveryTests(unittest.TestCase):
    """The inventory must see every production file, and only production files."""

    def test_finds_known_production_files(self) -> None:
        files = inv.iter_production_files(REPO_ROOT)
        relative = {p.relative_to(REPO_ROOT).as_posix() for p in files}
        self.assertIn("legacy_documenter/main.py", relative)
        self.assertIn("legacy_documenter/knowledge/readiness.py", relative)
        self.assertIn("legacy_documenter/knowledge/canonical/service.py", relative)

    def test_excludes_pycache_and_tests(self) -> None:
        files = inv.iter_production_files(REPO_ROOT)
        for path in files:
            self.assertNotIn("__pycache__", path.parts)
            self.assertNotIn("tests", path.parts)

    def test_file_count_matches_r14_baseline_observation(self) -> None:
        # The V4-R14 closure baseline recorded 143 production modules under
        # legacy_documenter/ (output/v4_r14/V4_FINAL_BASELINE.json ->
        # production_python_module_count). V4.1-R1 added one new production
        # module (legacy_documenter/utils/json_rendering.py, the DUP-001
        # shared deterministic-JSON-rendering helper), making 144. V4.1-R4
        # (DEBT-002) added three new internal readiness helper modules
        # (legacy_documenter/knowledge/_readiness_io.py, _readiness_parsing.py,
        # _readiness_evidence.py) behind readiness.py's unchanged
        # compatibility facade, making 147. V4.1-R6 added three new internal
        # DatabaseExtractor helper modules (_database_line_scanner.py,
        # _database_token_parsing.py, _database_classification.py) and three
        # new internal FunctionalFlowResolver helper modules
        # (_flow_key_labels.py, _flow_graph_construction.py,
        # _flow_report_composition.py), both behind unchanged compatibility
        # facades, making 153. V4.2-R1 added the new `legacy_documenter/cli/`
        # package (parser.py, router.py, execution_model.py, stage_identity.py,
        # serialization.py, __init__.py -- six new production modules
        # implementing the analyze/full/readiness CLI contract), making 159.
        # V4.2-R2 added two more `legacy_documenter/cli/` modules
        # (pipeline_stages.py -- the deterministic stage functions extracted
        # out of `legacy_documenter/main.py` -- and full_pipeline.py, the
        # resilient orchestrator built on them), making 161. V4.2-R3 added
        # one new production module
        # (legacy_documenter/exporters/technical_documentation_renderer.py,
        # the deterministic Markdown renderers for WEB_ENTRY_POINTS/
        # FUNCTIONAL_FLOWS/DATABASE_ACCESS/UNRESOLVED_FINDINGS), making 162.
        # V4.2-R4 added the new `legacy_documenter/orchestration/` package
        # (__init__.py, ai_interpretation.py, proposal_adapter.py -- three new
        # production modules implementing the opt-in AI interpretation and
        # proposal-adaptation integration), making 165. V4.2-R5 added one new
        # production module (legacy_documenter/cli/run_summary_presenter.py --
        # the console/Markdown presentation layer: next-action derivation,
        # output-location discovery, console summary rendering -- extracted
        # so `full_pipeline.py` did not have to grow to hold R5's UX logic),
        # making 166. V4.2-R6 added two new production modules:
        # legacy_documenter/utils/atomic_write.py (the temp-sibling +
        # os.replace crash-safe write helper, section 7) and
        # legacy_documenter/cli/artifact_lifecycle.py (the narrowly-scoped
        # stale-proposal reset used for rerun safety, section 4/5), making
        # 168. V4.2-R8 added one new production module
        # (legacy_documenter/exporters/_documentation_partitioning.py --
        # deterministic, safe partition-filename derivation for the
        # navigation/detail documentation split), making 169. V4.3-R2 added one
        # new production module (legacy_documenter/context/hydration.py --
        # the deterministic FLOW/PATH/DAO/SP evidence selection and
        # hydration service implementing the V4.3-R1 `AI_HYDRATED_PROJECTION`
        # contract; see
        # docs/V4_3/V4_3_R2_EVIDENCE_HYDRATION_AND_SELECTION_RESULT.md),
        # making 170. V4.3-R3 added one new production module
        # (legacy_documenter/documentation/human_flow_documentation.py --
        # the deterministic Spanish `HUMAN_DOCUMENTATION_PROJECTION 1.0`
        # renderer for hydrated FLOW records; see
        # docs/V4_3/V4_3_R3_HUMAN_DOCUMENTATION_RESULT.md), making 171. V4.3-R4
        # added one new production module
        # (legacy_documenter/documentation/human_documentation_scaling.py --
        # the deterministic system-scale navigation/partition aggregation
        # layer over many `render_flow_document` calls, implementing the
        # `human_documentation` surface at system scale R3 left out of
        # scope; see docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md),
        # making 173. V4.3-R5 added two new production modules
        # (legacy_documenter/context/ai_projection.py -- the budgeted
        # `AI_HYDRATED_PROJECTION 1.0` package builder over hydrated FLOW
        # records; and legacy_documenter/orchestration/_run_evidence_io.py --
        # the small internal index/snapshot loader kept out of
        # ai_interpretation.py so that module retains a single
        # responsibility, the same `_readiness_io.py`/`_database_*.py`
        # pattern earlier rounds already used; see
        # docs/V4_3/V4_3_R5_AI_CONTEXT_BUDGETING_RESULT.md), making the
        # current unmodified-checkout count 174. R0 itself
        # analyzed the pre-R1 tree and is not being re-run or re-approved
        # here; this count simply tracks the live repository, the same way
        # `production_python_module_count` does in the final baseline.
        # V5.1 R2 added the new `legacy_documenter/evidence/` package
        # implementing the Normalized Evidence Core defined by
        # docs/V5/V5_1_R1_NORMALIZED_EVIDENCE_CONTRACT.md (__init__.py,
        # identity.py, reference.py, entities.py, builder.py, persistence.py,
        # projection.py, invariants.py -- eight new production modules),
        # making 184. V5.2 R2 then added the new
        # `legacy_documenter/documentation_v52/` package (Profiles/Templates/
        # Markdown Renderer, docs/V5/V5_2_R1_DOCUMENTATION_CONTRACT_DESIGN.md:
        # __init__.py, categories.py, config.py, engine.py, noise.py,
        # renderer.py, structure.py, template.py, transform.py -- nine new
        # production modules), making 193. V5.3 R2.1 then added
        # `legacy_documenter/context/hydration_view.py` (the run-scoped,
        # indexed and memoizing `HydrationView`, kept out of `hydration.py`
        # so that module does not grow -- one new production module),
        # making 194. V5.3 R2.2 then added `legacy_documenter/utils/
        # path_limits.py` (the reusable Windows output-path preflight and
        # extended-length helper, one new production module), making 195.
        # V5.3 R2.2.1 then extracted the `documentation_v52` write phase from
        # `engine.py` into `documentation_v52/writer.py` (one new production
        # module), making 196. V5.3 R2.3 then added `legacy_documenter/versions.py`
        # and the `legacy_documenter/fingerprints/` package (`__init__`, `_common`,
        # `code`, `configuration`, `semantic`, `templates`) -- seven new production
        # modules, making 203. V5.3 R2.4 then added the `legacy_documenter/cache/`
        # package (`__init__`, `identity`, `file_state`, `diff`, `context`,
        # `manifest`, `store`, `session`) -- eight new production modules, making 211. V5.3
        # R2.5 then added `cache/extraction.py`, `cache/extraction_shards.py` and
        # `cache/extraction_store.py` (the per-file extraction cache, its deterministic sharding and
        # its disk side), making 214. V5.3 R2.6 then added `utils/write_if_changed.py` and
        # `fingerprints/extraction_contract.py` (write-skip helper and the extraction-cache guardian), making 216. V5.3
        # R2.7 then added `cache/scope.py`, `cache/run_metrics.py`, `cache/run_report.py` and
        # `utils/stage_timings.py` (scope analysis, run metrics, end-of-run report, stage timings), making 220. V5.3
        # R2.8 then added `cache/options.py`, `cache/verify.py` and `utils/write_policy.py` (cache controls, strict
        # verification, run-wide write policy), making 223.
        files = inv.iter_production_files(REPO_ROOT)
        # V5.4 R1 adds 33 modules: the adapter boundary, neutral evidence
        # bundle and neutral flow traversal. Historical artifacts stay frozen.
        # V5.5 R1 separates seven AI contract/composition helpers and adds
        # context/request_budget.py: eight new modules, 264 in total.
        # V5.6 R1 adds neutral flow segmentation and its request-budget
        # composition boundary (two modules; no upstream analysis change).
        self.assertEqual(len(files), 266)


class FileAnalysisTests(unittest.TestCase):
    """Per-file metrics must be internally consistent and deterministic."""

    def test_analyze_file_is_deterministic(self) -> None:
        path = REPO_ROOT / "legacy_documenter" / "knowledge" / "readiness.py"
        first = inv.analyze_file(path, REPO_ROOT)
        second = inv.analyze_file(path, REPO_ROOT)
        self.assertEqual(first, second)

    def test_analyze_file_reports_plausible_metrics(self) -> None:
        path = REPO_ROOT / "legacy_documenter" / "knowledge" / "canonical" / "service.py"
        record = inv.analyze_file(path, REPO_ROOT)
        self.assertGreater(record["line_count"], 0)
        self.assertGreaterEqual(record["class_count"], 1)
        self.assertGreaterEqual(record["function_count"], 1)
        self.assertIn(record["risk_category"], {"LOW", "MEDIUM", "HIGH", "VERY_HIGH"})
        self.assertTrue(0.0 <= record["docstring_coverage_percent"] <= 100.0)
        self.assertTrue(0.0 <= record["typed_functions_percent"] <= 100.0)

    def test_internal_dependencies_are_subset_of_imports(self) -> None:
        for path in inv.iter_production_files(REPO_ROOT):
            record = inv.analyze_file(path, REPO_ROOT)
            for dep in record["internal_dependencies"]:
                self.assertIn(dep, record["imports"], msg=f"{record['path']}: {dep}")

    def test_no_file_reports_a_parse_error(self) -> None:
        # Every production file in this repository is expected to be valid
        # Python; a parse error here would itself be a maintainability
        # finding worth surfacing, not something to hide.
        for path in inv.iter_production_files(REPO_ROOT):
            record = inv.analyze_file(path, REPO_ROOT)
            self.assertNotIn("parse_error", record, msg=record.get("path"))


class DependencyGraphTests(unittest.TestCase):
    def test_knowledge_domain_direction_still_acyclic_between_projection_siblings(self) -> None:
        files = inv.iter_production_files(REPO_ROOT)
        edges = inv.dependency_edges(REPO_ROOT, files)
        plugin_deps = edges.get("legacy_documenter.knowledge.plugin_projection.service", [])
        projection_deps = edges.get("legacy_documenter.knowledge.projection.service", [])
        self.assertFalse(any("plugin_projection" in dep for dep in projection_deps))
        self.assertFalse(any(dep == "legacy_documenter.knowledge.projection.service" for dep in plugin_deps))

    def test_find_cycles_is_deterministic_and_sorted(self) -> None:
        files = inv.iter_production_files(REPO_ROOT)
        edges = inv.dependency_edges(REPO_ROOT, files)
        first = inv.find_cycles(edges)
        second = inv.find_cycles(edges)
        self.assertEqual(first, second)
        self.assertEqual(first, sorted(first))


class InventoryPayloadTests(unittest.TestCase):
    """The full inventory payload must be valid, deterministic JSON with the
    required top-level sections (V4.1-R0 spec, 'Required Artifact 1')."""

    REQUIRED_KEYS = {
        "baseline", "production_inventory", "largest_modules", "largest_classes",
        "largest_functions", "responsibility_candidates", "duplication_candidates",
        "type_safety_candidates", "documentation_candidates", "naming_candidates",
        "exception_candidates", "side_effect_candidates", "dependency_findings",
        "known_debt", "characterization_needs", "public_compatibility", "risk_summary",
    }

    def test_inventory_has_all_required_sections(self) -> None:
        payload = report.build_inventory(REPO_ROOT)
        missing = self.REQUIRED_KEYS - payload.keys()
        self.assertEqual(missing, set())

    def test_inventory_is_json_serializable_and_no_absolute_paths(self) -> None:
        payload = report.build_inventory(REPO_ROOT)
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        self.assertNotIn(str(REPO_ROOT), text)
        self.assertNotIn(str(REPO_ROOT).replace("\\", "/"), text)
        # round-trips cleanly
        json.loads(text)

    def test_inventory_build_is_deterministic(self) -> None:
        first = json.dumps(report.build_inventory(REPO_ROOT), sort_keys=True)
        second = json.dumps(report.build_inventory(REPO_ROOT), sort_keys=True)
        self.assertEqual(first, second)

    def test_known_debt_covers_all_carried_forward_ids(self) -> None:
        payload = report.build_inventory(REPO_ROOT)
        ids = {item["id"] for item in payload["known_debt"]}
        for expected in ("TD-001", "TD-002", "TD-003", "TD-004", "TD-005", "DEBT-001", "DEBT-002", "DEBT-003"):
            self.assertIn(expected, ids)

    def test_largest_modules_are_sorted_descending(self) -> None:
        payload = report.build_inventory(REPO_ROOT)
        lines = [m["line_count"] for m in payload["largest_modules"]]
        self.assertEqual(lines, sorted(lines, reverse=True))

    def test_duplication_candidates_have_required_classification(self) -> None:
        payload = report.build_inventory(REPO_ROOT)
        allowed = {"SAFE_TO_CONSOLIDATE", "SIMILAR_BUT_SEMANTICALLY_DISTINCT", "NEEDS_CHARACTERIZATION", "DO_NOT_CONSOLIDATE"}
        for item in payload["duplication_candidates"]:
            self.assertIn(item["classification"], allowed)


class PlanPayloadTests(unittest.TestCase):
    """The refactor-plan payload must be valid, deterministic, and every
    round must carry the fields required by the V4.1-R0 spec's 'Round
    Design Requirements'."""

    REQUIRED_ROUND_KEYS = {
        "round_id", "title", "objective", "primary_files", "debt_items_addressed",
        "allowed_changes", "forbidden_changes", "characterization_required",
        "expected_tests", "risk", "rollback_boundary", "human_review_gate",
    }

    def test_plan_has_required_top_level_fields(self) -> None:
        payload = report.build_plan(REPO_ROOT)
        for key in ("phase", "goal", "behavior_change", "rounds", "global_invariants", "baseline_tests", "required_final_validation", "deferred_items"):
            self.assertIn(key, payload)
        self.assertEqual(payload["phase"], "V4.1")
        self.assertEqual(payload["goal"], "READABILITY_AND_MAINTAINABILITY")
        self.assertEqual(payload["behavior_change"], "FORBIDDEN")

    def test_every_round_has_required_fields(self) -> None:
        payload = report.build_plan(REPO_ROOT)
        for round_ in payload["rounds"]:
            missing = self.REQUIRED_ROUND_KEYS - round_.keys()
            self.assertEqual(missing, set(), msg=round_.get("round_id"))

    def test_round_ids_are_unique_and_ordered(self) -> None:
        payload = report.build_plan(REPO_ROOT)
        ids = [r["round_id"] for r in payload["rounds"]]
        self.assertEqual(len(ids), len(set(ids)))
        numeric = [int(round_id.rsplit("R", 1)[1]) for round_id in ids]
        self.assertEqual(numeric, sorted(numeric))

    def test_plan_build_is_deterministic(self) -> None:
        first = json.dumps(report.build_plan(REPO_ROOT), sort_keys=True)
        second = json.dumps(report.build_plan(REPO_ROOT), sort_keys=True)
        self.assertEqual(first, second)

    def test_plan_never_allows_provider_calls_or_git_operations(self) -> None:
        payload = report.build_plan(REPO_ROOT)
        text = json.dumps(payload).lower()
        self.assertNotIn("real llm call is allowed", text)
        self.assertNotIn("git push", text)
        self.assertNotIn("git commit", text)


class GeneratedArtifactOnDiskTests(unittest.TestCase):
    """If the artifacts have been generated to disk, they must match a
    fresh in-memory build exactly (proves the committed/generated copy is
    not stale relative to the tooling that produced it)."""

    def test_on_disk_inventory_matches_fresh_build_if_present(self) -> None:
        """Pin the complete live inventory; preserve the historical V4.1 artifact.

        V5.6 R1 adds two neutral segmentation/composition modules. Its live
        snapshot checks every file and aggregate; approved V4.1/V5.4/V5.5
        snapshots remain historical and unchanged.
        """
        historical = REPO_ROOT / "output" / "v4_1_r0" / "V4_1_MAINTAINABILITY_INVENTORY.json"
        if not historical.exists():
            self.skipTest("V4_1_MAINTAINABILITY_INVENTORY.json not yet generated")
        path = REPO_ROOT / "docs" / "V5" / "V5_6_R1_FLOW_SEGMENTATION_INVENTORY.json"
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(snapshot["round"], "V5.6 R1")
        self.assertFalse(snapshot["historical_artifacts_modified"])
        self.assertEqual(report.build_inventory(REPO_ROOT), snapshot["inventory"])

    def test_on_disk_plan_matches_fresh_build_if_present(self) -> None:
        path = REPO_ROOT / "output" / "v4_1_r0" / "V4_1_REFACTOR_PLAN.json"
        if not path.exists():
            self.skipTest("V4_1_REFACTOR_PLAN.json not yet generated")
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        fresh = report.build_plan(REPO_ROOT)
        self.assertEqual(on_disk, fresh)


if __name__ == "__main__":
    unittest.main()
