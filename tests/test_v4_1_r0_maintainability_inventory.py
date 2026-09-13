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
        # shared deterministic-JSON-rendering helper), so the current
        # unmodified-checkout count is 144. R0 itself analyzed the
        # pre-R1 tree and is not being re-run or re-approved here; this
        # count simply tracks the live repository, the same way
        # `production_python_module_count` does in the final baseline.
        files = inv.iter_production_files(REPO_ROOT)
        self.assertEqual(len(files), 144)


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
        """V4.1-R0's inventory is a frozen, historical AST scan of the
        repository tree as it existed when V4.1-R0 was approved. A later
        round can legitimately change that live tree in small, explicitly
        authorized ways -- e.g. V4.1-R1 adding the DUP-001 shared
        deterministic-JSON-rendering helper module and updating the eleven
        `contract_report.py` renderers (plus `utils/__init__.py`) to use it
        -- which changes this AST scan's per-file line counts/imports and
        aggregate module/risk counts. Asserting live-vs-frozen byte equality
        on those fields is the same defect class this round's own REG-002 /
        round-ordinal-parsing fixes address (a generated snapshot compared
        against a moving-target live value).

        This test still asserts every *other* section (duplication
        candidates, known debt, naming candidates, exception candidates,
        documentation candidates, largest classes/functions/modules,
        characterization needs, baseline) is byte-identical, and narrowly
        verifies the three sections a DUP-001-shaped change can touch
        (`production_inventory`, `risk_summary`, `dependency_findings`)
        moved in exactly the expected direction rather than skipping them
        outright.
        """
        path = REPO_ROOT / "output" / "v4_1_r0" / "V4_1_MAINTAINABILITY_INVENTORY.json"
        if not path.exists():
            self.skipTest("V4_1_MAINTAINABILITY_INVENTORY.json not yet generated")
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        fresh = report.build_inventory(REPO_ROOT)
        if on_disk == fresh:
            return

        # Fields expected to legitimately change due to the authorized
        # V4.1-R1 DUP-001 shared-renderer extraction.
        touched_paths = {
            "legacy_documenter/utils/json_rendering.py",  # new
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
            # V4.1-R2 added narrow, safe return-type annotations (see
            # output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json)
            # to functions in these R0-identified type_safety_candidates
            # files. No parameter typing of ambiguous nested JSON shapes,
            # no behavior change; only typed_functions_percent/line_count
            # for these six files move.
            "legacy_documenter/documentation/contracts.py",
            "legacy_documenter/documentation/interpretation.py",
            "legacy_documenter/documentation/consistency.py",
            "legacy_documenter/documentation/coverage.py",
            "legacy_documenter/documentation/human_review.py",
            "legacy_documenter/documentation/evidence_catalog.py",
        }

        normalized_on_disk = dict(on_disk)
        normalized_fresh = dict(fresh)

        on_disk_inv = {e["path"]: e for e in on_disk["production_inventory"]}
        fresh_inv = {e["path"]: e for e in fresh["production_inventory"]}
        # No path may disappear; the only new path must be the one new
        # authorized helper module.
        self.assertEqual(set(on_disk_inv) - set(fresh_inv), set())
        self.assertEqual(set(fresh_inv) - set(on_disk_inv), {"legacy_documenter/utils/json_rendering.py"})
        unexpected_entry_diffs = [
            p for p in (set(on_disk_inv) & set(fresh_inv)) - touched_paths
            if on_disk_inv[p] != fresh_inv[p]
        ]
        self.assertEqual(unexpected_entry_diffs, [], unexpected_entry_diffs)
        normalized_on_disk.pop("production_inventory", None)
        normalized_fresh.pop("production_inventory", None)

        # One new LOW-risk production module; all other risk buckets and
        # the named high/very-high-risk file lists are unaffected.
        on_disk_risk = on_disk["risk_summary"]
        fresh_risk = fresh["risk_summary"]
        self.assertEqual(fresh_risk["high_risk_files"], on_disk_risk["high_risk_files"])
        self.assertEqual(fresh_risk["very_high_risk_files"], on_disk_risk["very_high_risk_files"])
        expected_categories = dict(on_disk_risk["files_by_risk_category"])
        expected_categories["LOW"] = expected_categories.get("LOW", 0) + 1
        self.assertEqual(fresh_risk["files_by_risk_category"], expected_categories)
        normalized_on_disk.pop("risk_summary", None)
        normalized_fresh.pop("risk_summary", None)

        # One new production module; every other dependency-direction
        # finding is unaffected.
        on_disk_dep = dict(on_disk["dependency_findings"])
        fresh_dep = dict(fresh["dependency_findings"])
        self.assertEqual(fresh_dep.pop("module_count"), on_disk_dep.pop("module_count") + 1)
        self.assertEqual(fresh_dep, on_disk_dep)
        normalized_on_disk.pop("dependency_findings", None)
        normalized_fresh.pop("dependency_findings", None)

        # V4.1-R2 raised typed_functions_percent for a handful of
        # below-average files (see touched_paths above). type_safety_
        # candidates is a relative-threshold diagnostic: improving those
        # files' coverage shifts the repository-wide average the threshold
        # is computed against, which mechanically drops the now-improved
        # files off the candidate list and mechanically admits a few
        # previously-just-above-average files onto it. This is an
        # expected side effect of a relative diagnostic, not a behavior
        # change -- assert the shift landed exactly where expected rather
        # than skip the section outright.
        r2_resolved_candidates = {
            "legacy_documenter/documentation/contracts.py",
            "legacy_documenter/documentation/interpretation.py",
            "legacy_documenter/documentation/consistency.py",
            "legacy_documenter/documentation/coverage.py",
            "legacy_documenter/documentation/human_review.py",
        }
        r2_newly_below_average = {
            "legacy_documenter/documentation/synthesis.py",
            "legacy_documenter/llm/copilot_pilot.py",
            "legacy_documenter/documentation/systematic.py",
            "legacy_documenter/documentation/resume.py",
            "legacy_documenter/documentation/second_review.py",
        }
        on_disk_ts = {e["path"] for e in on_disk["type_safety_candidates"]}
        fresh_ts = {e["path"] for e in fresh["type_safety_candidates"]}
        self.assertEqual(on_disk_ts - fresh_ts, r2_resolved_candidates)
        self.assertEqual(fresh_ts - on_disk_ts, r2_newly_below_average)
        normalized_on_disk.pop("type_safety_candidates", None)
        normalized_fresh.pop("type_safety_candidates", None)

        self.assertEqual(normalized_on_disk, normalized_fresh)

    def test_on_disk_plan_matches_fresh_build_if_present(self) -> None:
        path = REPO_ROOT / "output" / "v4_1_r0" / "V4_1_REFACTOR_PLAN.json"
        if not path.exists():
            self.skipTest("V4_1_REFACTOR_PLAN.json not yet generated")
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        fresh = report.build_plan(REPO_ROOT)
        self.assertEqual(on_disk, fresh)


if __name__ == "__main__":
    unittest.main()
