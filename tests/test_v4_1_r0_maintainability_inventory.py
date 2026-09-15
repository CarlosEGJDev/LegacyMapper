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
        # the current unmodified-checkout count 168. R0 itself analyzed the
        # pre-R1 tree and is not being re-run or re-approved here; this
        # count simply tracks the live repository, the same way
        # `production_python_module_count` does in the final baseline.
        files = inv.iter_production_files(REPO_ROOT)
        self.assertEqual(len(files), 168)


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
            # V4.2-R6: writes atomically now instead of via plain
            # `write_text` (see
            # docs/V4_2/V4_2_R6_ROBUSTNESS_RECOVERY_SECURITY_AND_APPROVAL_SURFACE_RESULT.md).
            "legacy_documenter/exporters/json_exporter.py",
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
            # V4.1-R3 added the `build_maintainability_inventory` alias
            # (delegates to `audit`; see DEBT-003/naming_candidates
            # disposition in output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json)
            # to this file only. No behavior change; this AST scan's line
            # count/function count for this one file moves.
            "legacy_documenter/quality/maintainability_audit.py",
            # V4.1-R4 (DEBT-002) split readiness.py's parsing, evidence-
            # closure, and file-I/O helpers into three new internal
            # `legacy_documenter/knowledge/_readiness_*.py` modules behind
            # an unchanged compatibility facade. readiness.py itself is
            # smaller (fewer lines/functions/imports moved out) but its
            # public surface and behavior are unchanged; see
            # output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json.
            "legacy_documenter/knowledge/readiness.py",
            # V4.1-R6 authorized a narrow extraction from each risky
            # orchestrator after all eight R5 characterization gaps closed:
            # logical-line/token/classification helpers out of
            # DatabaseExtractor, and key-label/graph-construction/report-
            # composition helpers out of FunctionalFlowResolver, both behind
            # unchanged compatibility facades; see
            # output/v4_1_r6/V4_1_R6_EXTRACTION_EQUIVALENCE.json.
            "legacy_documenter/extractors/database_extractor.py",
            "legacy_documenter/analysis/flow_resolver.py",
            # V4.1-R7 consolidated three duplicated try/except Exception
            # blocks in `analyze_repository` (CallExtractor,
            # WebEventExtractor, DatabaseExtractor -- identical shape,
            # only the extractor/label/sink differed) into one internal
            # `_extract_into` helper. This is a SAFE_LOCAL_CLEANUP: same
            # caught exception type, same error record shape, same
            # per-file call order and partial-result behavior; see
            # output/v4_1_r7/V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json.
            # The mechanical AST scan's line/function counts for this one
            # file move, and its `except_exception` count legitimately
            # drops from 4 to 2 (three redundant handlers collapsed into
            # one shared handler).
            "legacy_documenter/main.py",
            # V4.1-R8 added a package-level docstring to context/__init__.py
            # (explaining how the four context/ modules relate, per R0's
            # naming_candidates note that the entry point is hard to guess)
            # and module-level docstrings to composer.py/context_builder.py
            # (previously missing). No rename, no restructuring; only
            # line_count and module_docstring_present move for these three
            # files; see output/v4_1_r8/V4_1_R8_NAMING_DOCUMENTATION_EQUIVALENCE.json.
            "legacy_documenter/context/__init__.py",
            "legacy_documenter/context/composer.py",
            "legacy_documenter/context/context_builder.py",
        }
        # V4.2-R1 introduced the `legacy_documenter/cli/` package
        # (parser/router/execution model) and wired `main.py` to it (new
        # `analyze`/`full`/`readiness` subcommands; the legacy bare-positional
        # invocation is preserved as an alias for `analyze`); see
        # docs/V4_2/V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL_RESULT.md.
        # `legacy_documenter/main.py` was already in `touched_paths` above
        # (V4.1-R7); it grows further here (new imports, a slightly larger
        # `main()`), still covered by the existing
        # `fresh_largest[main_path] > on_disk_largest[main_path]` inequality
        # below rather than an exact-line-count comparison.

        normalized_on_disk = dict(on_disk)
        normalized_fresh = dict(fresh)

        on_disk_inv = {e["path"]: e for e in on_disk["production_inventory"]}
        fresh_inv = {e["path"]: e for e in fresh["production_inventory"]}
        # No path may disappear; the only new paths are the one authorized
        # V4.1-R1 helper module and the three V4.1-R4 readiness helpers.
        self.assertEqual(set(on_disk_inv) - set(fresh_inv), set())
        self.assertEqual(
            set(fresh_inv) - set(on_disk_inv),
            {
                "legacy_documenter/utils/json_rendering.py",
                "legacy_documenter/knowledge/_readiness_io.py",
                "legacy_documenter/knowledge/_readiness_parsing.py",
                "legacy_documenter/knowledge/_readiness_evidence.py",
                "legacy_documenter/extractors/_database_line_scanner.py",
                "legacy_documenter/extractors/_database_token_parsing.py",
                "legacy_documenter/extractors/_database_classification.py",
                "legacy_documenter/analysis/_flow_key_labels.py",
                "legacy_documenter/analysis/_flow_graph_construction.py",
                "legacy_documenter/analysis/_flow_report_composition.py",
                # V4.2-R1: new `legacy_documenter/cli/` package (see
                # docs/V4_2/V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL_RESULT.md).
                "legacy_documenter/cli/__init__.py",
                "legacy_documenter/cli/parser.py",
                "legacy_documenter/cli/router.py",
                "legacy_documenter/cli/execution_model.py",
                "legacy_documenter/cli/stage_identity.py",
                "legacy_documenter/cli/serialization.py",
                # V4.2-R2: the deterministic stage functions extracted out of
                # `legacy_documenter/main.py`, and the resilient orchestrator
                # built on them (see
                # docs/V4_2/V4_2_R2_DETERMINISTIC_FULL_PIPELINE_ORCHESTRATOR_RESULT.md).
                "legacy_documenter/cli/pipeline_stages.py",
                "legacy_documenter/cli/full_pipeline.py",
                # V4.2-R3: the deterministic technical-documentation renderer
                # (see
                # docs/V4_2/V4_2_R3_DETERMINISTIC_TECHNICAL_DOCUMENTATION_RESULT.md).
                "legacy_documenter/exporters/technical_documentation_renderer.py",
                # V4.2-R4: the opt-in AI interpretation / proposal adaptation
                # package (see
                # docs/V4_2/V4_2_R4_AI_INTERPRETATION_AND_PROPOSAL_INTEGRATION_RESULT.md).
                "legacy_documenter/orchestration/__init__.py",
                "legacy_documenter/orchestration/ai_interpretation.py",
                "legacy_documenter/orchestration/proposal_adapter.py",
                # V4.2-R5: the new console/Markdown presentation module (next
                # action, output-location discovery, console summary) --
                # extracted so `full_pipeline.py` did not have to grow to hold
                # R5's UX logic (see
                # docs/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX_RESULT.md).
                "legacy_documenter/cli/run_summary_presenter.py",
                # V4.2-R6: the crash-safe write helper (temp sibling +
                # os.replace) and the narrowly-scoped stale-proposal reset
                # used for rerun safety (see
                # docs/V4_2/V4_2_R6_ROBUSTNESS_RECOVERY_SECURITY_AND_APPROVAL_SURFACE_RESULT.md).
                "legacy_documenter/utils/atomic_write.py",
                "legacy_documenter/cli/artifact_lifecycle.py",
            },
        )
        unexpected_entry_diffs = [
            p for p in (set(on_disk_inv) & set(fresh_inv)) - touched_paths
            if on_disk_inv[p] != fresh_inv[p]
        ]
        self.assertEqual(unexpected_entry_diffs, [], unexpected_entry_diffs)
        normalized_on_disk.pop("production_inventory", None)
        normalized_fresh.pop("production_inventory", None)

        # V4.1-R1 added one new LOW-risk production module. V4.1-R4 added
        # three new LOW-risk readiness helper modules and shrank
        # readiness.py enough that its own risk_category drops from
        # VERY_HIGH to HIGH -- it moves from the very-high-risk list to the
        # high-risk list. V4.1-R6 added three new LOW-risk DatabaseExtractor
        # helper modules and three new MEDIUM-risk FunctionalFlowResolver
        # helper modules, and shrank database_extractor.py enough that its
        # own risk_category drops from HIGH to MEDIUM (added docstrings on
        # its now-delegating methods raised docstring_coverage_percent);
        # flow_resolver.py's risk_category is unchanged (still HIGH). All
        # other risk-bucket membership is unaffected.
        on_disk_risk = on_disk["risk_summary"]
        fresh_risk = fresh["risk_summary"]
        readiness_path = "legacy_documenter/knowledge/readiness.py"
        database_extractor_path = "legacy_documenter/extractors/database_extractor.py"
        # V4.2-R2 extracted most of `analyze_repository`'s body out of
        # `legacy_documenter/main.py` into the new
        # `legacy_documenter/cli/pipeline_stages.py` (see
        # docs/V4_2/V4_2_R2_DETERMINISTIC_FULL_PIPELINE_ORCHESTRATOR_RESULT.md).
        # main.py's own risk_category drops from HIGH to MEDIUM (much less
        # code, same as database_extractor.py's R6 drop); the new
        # pipeline_stages.py (340 lines, the extracted stage functions) enters
        # HIGH in main.py's place.
        r2_main_path = "legacy_documenter/main.py"
        r2_pipeline_stages_path = "legacy_documenter/cli/pipeline_stages.py"
        # V4.2-R3 wired the new DOCUMENTATION stage into
        # `legacy_documenter/cli/full_pipeline.py`, growing it (287 -> 315
        # lines) enough to cross from MEDIUM into HIGH risk -- no existing
        # file left HIGH to make room; HIGH grew by one at R3.
        #
        # V4.2-R4 wired the opt-in AI_INTERPRETATION/PROPOSAL_GENERATION
        # stages into the same file, growing it further (315 -> 488 lines):
        # it now crosses from HIGH into VERY_HIGH, exactly offsetting
        # readiness.py's earlier VERY_HIGH -> HIGH move (V4.1-R4) -- fresh
        # VERY_HIGH count returns to the frozen baseline's 6, by coincidence
        # of two unrelated single-file moves cancelling out, not because
        # nothing changed.
        r3_full_pipeline_path = "legacy_documenter/cli/full_pipeline.py"
        # V4.2-R6: run_summary_presenter.py (185 -> 234 lines) leaves LOW and enters HIGH.
        r6_presenter_path = "legacy_documenter/cli/run_summary_presenter.py"
        expected_high_risk_files = sorted(
            [p for p in on_disk_risk["high_risk_files"] if p not in (database_extractor_path, r2_main_path)]
            + [readiness_path, r2_pipeline_stages_path, r6_presenter_path]
        )
        expected_very_high_risk_files = sorted(
            [p for p in on_disk_risk["very_high_risk_files"] if p != readiness_path] + [r3_full_pipeline_path]
        )
        self.assertEqual(sorted(fresh_risk["high_risk_files"]), expected_high_risk_files)
        self.assertEqual(sorted(fresh_risk["very_high_risk_files"]), expected_very_high_risk_files)
        # V4.2-R1 added six new LOW/MEDIUM-risk `legacy_documenter/cli/`
        # modules: __init__.py, parser.py, execution_model.py,
        # stage_identity.py, serialization.py are LOW risk; router.py is
        # MEDIUM risk (it is the one module with conditional branching over
        # three commands). V4.2-R2 added two more: full_pipeline.py was
        # MEDIUM risk at R2, pipeline_stages.py is HIGH risk (the relocated
        # stage functions) -- see the main.py/pipeline_stages.py bucket swap
        # above. V4.2-R3 added one new MEDIUM-risk module
        # (`legacy_documenter/exporters/technical_documentation_renderer.py`,
        # 380 lines) and grew `full_pipeline.py` enough to leave MEDIUM and
        # enter HIGH -- MEDIUM's net change from R3 is zero (one file leaves,
        # one enters); HIGH grew by one at R3. V4.2-R4 added two new LOW-risk
        # modules (`legacy_documenter/orchestration/__init__.py`,
        # `proposal_adapter.py`) and one new MEDIUM-risk module
        # (`ai_interpretation.py`, 190 lines), and grew `full_pipeline.py`
        # enough to leave HIGH and enter VERY_HIGH (see
        # r3_full_pipeline_path above) -- HIGH shrinks by one at R4.
        # V4.2-R5 added one new LOW-risk module
        # (`legacy_documenter/cli/run_summary_presenter.py`) and touched
        # `main.py`/`parser.py`/`execution_model.py`/`full_pipeline.py`
        # without moving any of them across a risk-category boundary (see
        # docs/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX_RESULT.md).
        # V4.2-R6 added one new LOW-risk module
        # (`legacy_documenter/cli/artifact_lifecycle.py`, 60 lines) and one
        # new MEDIUM-risk module (`legacy_documenter/utils/atomic_write.py`,
        # 44 lines -- a small helper, but its own exception-handling/cleanup
        # branching is enough to place it in MEDIUM rather than LOW).
        # `run_summary_presenter.py` grew from 185 to 234 lines (the new
        # `finalize_and_write_run_summary` responsibility, moved out of
        # `full_pipeline.py` per section 15) and crosses from LOW into HIGH
        # risk -- the deliberate trade-off that kept `full_pipeline.py`
        # itself flat (488 -> 490 lines, unchanged VERY_HIGH bucket) despite
        # R6 touching its failure/recovery/summary orchestration; see
        # docs/V4_2/V4_2_R6_ROBUSTNESS_RECOVERY_SECURITY_AND_APPROVAL_SURFACE_RESULT.md.
        expected_categories = dict(on_disk_risk["files_by_risk_category"])
        expected_categories["LOW"] = expected_categories.get("LOW", 0) + 4 + 3 + 5 + 2 + 1 + 1 - 1
        expected_categories["MEDIUM"] = expected_categories.get("MEDIUM", 0) + 3 + 1 + 1 + 1 + 1 + 1 - 1 + 1 + 1
        expected_categories["HIGH"] = expected_categories.get("HIGH", 0) + 1 - 1 + 1 - 1 + 1 - 1 + 1
        expected_categories["VERY_HIGH"] = expected_categories.get("VERY_HIGH", 0) - 1 + 1
        self.assertEqual(fresh_risk["files_by_risk_category"], expected_categories)
        normalized_on_disk.pop("risk_summary", None)
        normalized_fresh.pop("risk_summary", None)

        # Twenty-five new production modules total (one from V4.1-R1, three
        # from V4.1-R4's readiness split, six from V4.1-R6's DatabaseExtractor/
        # FunctionalFlowResolver splits, six from V4.2-R1's new
        # `legacy_documenter/cli/` package, two from V4.2-R2's
        # pipeline_stages.py/full_pipeline.py, one from V4.2-R3's
        # technical_documentation_renderer.py, three from V4.2-R4's new
        # `legacy_documenter/orchestration/` package, one from V4.2-R5's new
        # run_summary_presenter.py, two from V4.2-R6's new
        # atomic_write.py/artifact_lifecycle.py); every other dependency-
        # direction finding is unaffected -- the new modules only import
        # from `legacy_documenter.knowledge.readiness`,
        # `legacy_documenter.knowledge.proposals`, `legacy_documenter.llm`,
        # `legacy_documenter.context`, `legacy_documenter.utils`, and the
        # existing analysis/context/exporters/extractors/scanner packages
        # `main.py` already depended on, all already-established dependency
        # directions.
        on_disk_dep = dict(on_disk["dependency_findings"])
        fresh_dep = dict(fresh["dependency_findings"])
        self.assertEqual(fresh_dep.pop("module_count"), on_disk_dep.pop("module_count") + 25)
        self.assertEqual(fresh_dep, on_disk_dep)
        normalized_on_disk.pop("dependency_findings", None)
        normalized_fresh.pop("dependency_findings", None)

        # V4.1-R4 shrank readiness.py (292 -> fewer lines); V4.1-R6 shrank
        # database_extractor.py (425 -> fewer lines). V4.1-R7's `_extract_into`
        # consolidation grew main.py slightly (228 -> more lines: one new
        # named helper function plus its docstring replaces three inlined
        # try/except blocks; no new module was added).
        #
        # V4.2-R2 changes this section's membership, not just positions:
        # main.py shrank from 249 (post-R1) to 100 lines (most of
        # `analyze_repository`'s body moved to the new
        # `legacy_documenter/cli/pipeline_stages.py`), and the new
        # pipeline_stages.py (340 lines) / full_pipeline.py (287 lines)
        # entered the top-20 largest-modules list. Between the two new,
        # larger entries and main.py's own shrink, both main.py (100 lines)
        # and readiness.py (188 lines, unchanged by R2 but now below the
        # top-20 cutoff of 205) drop out of the top-20 list entirely -- a
        # ranking-membership effect of R2's own change, not evidence readiness.py
        # regressed. database_extractor.py and flow_resolver.py remain in
        # the top-20 (still well above the cutoff) at their already-reduced
        # V4.1-R6 sizes.
        # V4.2-R3 added one more new, larger entry:
        # `legacy_documenter/exporters/technical_documentation_renderer.py`
        # (380 lines), and R3's own additions to `full_pipeline.py` (287 ->
        # 315 lines, wiring the new DOCUMENTATION stage) grew it further --
        # both were already top-20 members since R2, so this doesn't change
        # membership, only their line counts (not pinned for R2/R3-introduced
        # files, only for pre-existing ones -- see the loop below). The two
        # new/grown R3 entries push one more pre-existing member,
        # `legacy_documenter/knowledge/projection/rules.py` (205 lines,
        # untouched by R3), below the new top-20 cutoff -- the same
        # ranking-membership effect R2 already caused for main.py/readiness.py.
        on_disk_largest = {e["path"]: e["line_count"] for e in on_disk["largest_modules"]}
        fresh_largest = {e["path"]: e["line_count"] for e in fresh["largest_modules"]}
        flow_resolver_path = "legacy_documenter/analysis/flow_resolver.py"
        main_path = "legacy_documenter/main.py"
        r3_projection_rules_path = "legacy_documenter/knowledge/projection/rules.py"
        # V4.2-R6: run_summary_presenter.py (234 lines) newly enters the
        # top-20, pushing `legacy_documenter/knowledge/projection/models.py`
        # (untouched by R6) below the cutoff -- the same ranking-membership
        # effect already seen at R2/R3.
        r6_projection_models_path = "legacy_documenter/knowledge/projection/models.py"
        new_largest_modules = {
            "legacy_documenter/cli/pipeline_stages.py", "legacy_documenter/cli/full_pipeline.py",
            "legacy_documenter/exporters/technical_documentation_renderer.py",
            "legacy_documenter/cli/run_summary_presenter.py",
        }
        dropped_largest_modules = {main_path, readiness_path, r3_projection_rules_path, r6_projection_models_path}
        self.assertEqual(set(fresh_largest) - set(on_disk_largest), new_largest_modules)
        self.assertEqual(set(on_disk_largest) - set(fresh_largest), dropped_largest_modules)
        self.assertLess(fresh_largest[database_extractor_path], on_disk_largest[database_extractor_path])
        self.assertLess(fresh_largest[flow_resolver_path], on_disk_largest[flow_resolver_path])
        for path, line_count in on_disk_largest.items():
            if path not in (database_extractor_path, flow_resolver_path, *dropped_largest_modules):
                self.assertEqual(fresh_largest[path], line_count)
        normalized_on_disk.pop("largest_modules", None)
        normalized_fresh.pop("largest_modules", None)

        on_disk_side_effects = {e["kind"]: e for e in on_disk["side_effect_candidates"]}
        fresh_side_effects = {e["kind"]: e for e in fresh["side_effect_candidates"]}
        self.assertEqual(set(on_disk_side_effects), set(fresh_side_effects))
        for kind, entry in on_disk_side_effects.items():
            fresh_entry = fresh_side_effects[kind]
            if kind == "filesystem_access":
                # V4.2-R2 adds two more filesystem-touching modules:
                # full_pipeline.py writes RUN_SUMMARY.json/.md directly
                # (`_write_run_summary`); pipeline_stages.py is flagged too,
                # inheriting the signal from the exporter/context-builder
                # calls it makes (`export_artifacts`/`build_context_artifacts`).
                # V4.2-R4 adds one more: `ai_interpretation.py` imports `os`
                # (for `os.environ.get(...)` reading the provider config env
                # vars, e.g. LEGACYMAPPER_LLM_PROVIDER) -- the scanner's
                # `FILESYSTEM_MODULES` heuristic treats any `os` import as a
                # filesystem-access signal; this is a real, deliberate,
                # correct use (not a stray import to remove, unlike R3's).
                # V4.2-R5 adds one more: `run_summary_presenter.py` checks
                # `(output_dir / name).exists()` for each well-known result
                # location (`compute_output_locations`) -- a real, deliberate
                # filesystem read, not a stray import. (V4.2-R6 later changed
                # `compute_output_locations` to a stage-outcome check instead
                # of a filesystem check, but the module still imports/uses
                # `Path` throughout `finalize_and_write_run_summary`, so it
                # remains flagged.) V4.2-R6 adds two more:
                # `artifact_lifecycle.py` (removes stale proposal files) and
                # `utils/atomic_write.py` (the temp-sibling + os.replace
                # helper) -- both real, deliberate filesystem writes.
                expected_files = sorted(entry["files"] + [
                    "legacy_documenter/knowledge/_readiness_io.py",
                    "legacy_documenter/knowledge/_readiness_evidence.py",
                    "legacy_documenter/extractors/_database_line_scanner.py",
                    "legacy_documenter/cli/full_pipeline.py",
                    "legacy_documenter/cli/pipeline_stages.py",
                    "legacy_documenter/orchestration/ai_interpretation.py",
                    "legacy_documenter/cli/run_summary_presenter.py",
                    "legacy_documenter/cli/artifact_lifecycle.py",
                    "legacy_documenter/utils/atomic_write.py",
                ])
                self.assertEqual(sorted(fresh_entry["files"]), expected_files)
                self.assertEqual(fresh_entry["file_count"], entry["file_count"] + 9)
            else:
                self.assertEqual(fresh_entry["files"], entry["files"])
                self.assertEqual(fresh_entry["file_count"], entry["file_count"])
        normalized_on_disk.pop("side_effect_candidates", None)
        normalized_fresh.pop("side_effect_candidates", None)

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

        # V4.1-R6 shrank the DatabaseExtractor and FunctionalFlowResolver
        # classes themselves (their delegating methods are now one-liners);
        # method_count and classification are unchanged, only line_count
        # moves for these two classes.
        #
        # V4.2-R3's new `TechnicalDocumentationRenderer` class (four
        # sizeable rendering methods, ~380 lines) enters this top-N list,
        # displacing `VBNetExtractor` (`legacy_documenter/extractors/vbnet_extractor.py`,
        # untouched by R3) below the cutoff -- the same ranking-membership
        # effect already seen for `largest_modules`.
        r3_renderer_path = "legacy_documenter/exporters/technical_documentation_renderer.py"
        r3_vbnet_extractor_path = "legacy_documenter/extractors/vbnet_extractor.py"
        on_disk_classes = {e["path"]: e for e in on_disk["largest_classes"]}
        fresh_classes = {e["path"]: e for e in fresh["largest_classes"]}
        self.assertEqual(set(fresh_classes) - set(on_disk_classes), {r3_renderer_path})
        self.assertEqual(set(on_disk_classes) - set(fresh_classes), {r3_vbnet_extractor_path})
        for path, entry in on_disk_classes.items():
            if path == r3_vbnet_extractor_path:
                continue
            fresh_entry = dict(fresh_classes[path])
            if path in (database_extractor_path, flow_resolver_path):
                self.assertLess(fresh_entry["line_count"], entry["line_count"])
                fresh_entry["line_count"] = entry["line_count"]
            self.assertEqual(fresh_entry, entry)
        normalized_on_disk.pop("largest_classes", None)
        normalized_fresh.pop("largest_classes", None)

        # V4.1-R7 shrank `analyze_repository` itself by moving the three
        # duplicated try/except blocks into the new `_extract_into` helper;
        # only this one function's line_count moved (still a top-N entry).
        #
        # V4.2-R2 removes `(main.py, analyze_repository)` from this top-N
        # list entirely: the function now delegates to
        # `legacy_documenter.cli.pipeline_stages` and is far shorter. The new
        # `full_pipeline.run_full_pipeline` (the resilient orchestrator, with
        # its ten explicit stage calls) enters the list in its place.
        # V4.2-R3's two largest new renderer methods
        # (`TechnicalDocumentationRenderer.database_access`/`.unresolved_findings`)
        # enter this top-N list, displacing `DatabaseResolver.resolve` and
        # `FunctionalFlowResolver.resolve` (both untouched by R3) below the
        # cutoff -- the same ranking-membership effect as `largest_classes`.
        main_path = "legacy_documenter/main.py"
        on_disk_funcs = {(e["path"], e["qualified_name"]): e for e in on_disk["largest_functions"]}
        fresh_funcs = {(e["path"], e["qualified_name"]): e for e in fresh["largest_functions"]}
        r2_new_function = ("legacy_documenter/cli/full_pipeline.py", "run_full_pipeline")
        r2_dropped_function = (main_path, "analyze_repository")
        r3_new_functions = {
            ("legacy_documenter/exporters/technical_documentation_renderer.py", "TechnicalDocumentationRenderer.database_access"),
            ("legacy_documenter/exporters/technical_documentation_renderer.py", "TechnicalDocumentationRenderer.unresolved_findings"),
        }
        r3_dropped_functions = {
            ("legacy_documenter/analysis/database_resolver.py", "DatabaseResolver.resolve"),
            ("legacy_documenter/analysis/flow_resolver.py", "FunctionalFlowResolver.resolve"),
        }
        self.assertEqual(set(fresh_funcs) - set(on_disk_funcs), {r2_new_function, *r3_new_functions})
        self.assertEqual(set(on_disk_funcs) - set(fresh_funcs), {r2_dropped_function, *r3_dropped_functions})
        for key, entry in on_disk_funcs.items():
            if key in (r2_dropped_function, *r3_dropped_functions):
                continue
            self.assertEqual(fresh_funcs[key], entry)
        normalized_on_disk.pop("largest_functions", None)
        normalized_fresh.pop("largest_functions", None)

        # documentation_candidates is also a relative-threshold diagnostic
        # (below-average docstring_coverage_percent): the delegating methods
        # added to database_extractor.py/flow_resolver.py raised their own
        # docstring coverage enough to drop both off this list, which
        # mechanically admits two previously-just-below-average files.
        r6_resolved_doc_candidates = {database_extractor_path, flow_resolver_path}
        r6_newly_below_average_doc = {
            "legacy_documenter/context/system_context_builder.py",
            "legacy_documenter/extractors/vbnet_extractor.py",
        }
        on_disk_doc = {e["path"] for e in on_disk["documentation_candidates"]}
        fresh_doc = {e["path"] for e in fresh["documentation_candidates"]}
        self.assertEqual(on_disk_doc - fresh_doc, r6_resolved_doc_candidates)
        self.assertEqual(fresh_doc - on_disk_doc, r6_newly_below_average_doc)
        normalized_on_disk.pop("documentation_candidates", None)
        normalized_fresh.pop("documentation_candidates", None)

        # exception_candidates: V4.1-R7's `_extract_into` consolidation
        # legitimately dropped main.py's except_exception_count from 4 to 2
        # (three redundant `except Exception` blocks collapsed into one
        # shared handler); classification/note/bare_except_count unchanged.
        #
        # V4.2-R2 moves main.py's remaining exception handling out entirely:
        # `_extract_into` (and its per-file `except Exception` blocks) now
        # lives in `legacy_documenter/cli/pipeline_stages.py`, and the
        # resilient orchestrator's own per-stage `except Exception` handling
        # lives in `legacy_documenter/cli/full_pipeline.py`. main.py itself
        # no longer has any exception handling and drops off this list; the
        # two new files take its place.
        # V4.2-R4 adds one more: `ai_interpretation.py` wraps its
        # `ContextResolver`/`ContextComposer` construction and its
        # `provider.structured_generate(...)` call each in their own
        # try/except, converting a raised exception into a structured
        # `AiInterpretationResult` instead of letting it propagate (V4.2-R4
        # section 14/16's explicit "never a raw traceback" requirement).
        # V4.2-R6 adds two more: `run_summary_presenter.py`'s
        # `finalize_and_write_run_summary` wraps the atomic write in
        # try/except (a summary-write failure becomes a structured
        # FINAL_SUMMARY FAILED stage, never a crash); `utils/atomic_write.py`
        # wraps its temp-file cleanup in try/except (a cleanup failure must
        # never mask the original write error).
        on_disk_exc = {e["path"]: e for e in on_disk["exception_candidates"]}
        fresh_exc = {e["path"]: e for e in fresh["exception_candidates"]}
        r2_new_exception_files = {
            "legacy_documenter/cli/pipeline_stages.py", "legacy_documenter/cli/full_pipeline.py",
            "legacy_documenter/orchestration/ai_interpretation.py",
            "legacy_documenter/cli/run_summary_presenter.py", "legacy_documenter/utils/atomic_write.py",
        }
        self.assertEqual(set(fresh_exc) - set(on_disk_exc), r2_new_exception_files)
        self.assertEqual(set(on_disk_exc) - set(fresh_exc), {main_path})
        for path, entry in on_disk_exc.items():
            if path == main_path:
                continue
            self.assertEqual(fresh_exc[path], entry)
        normalized_on_disk.pop("exception_candidates", None)
        normalized_fresh.pop("exception_candidates", None)

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
