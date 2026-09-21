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
        files = inv.iter_production_files(REPO_ROOT)
        self.assertEqual(len(files), 176)


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
                # V4.2-R8: deterministic, safe partition-filename derivation
                # for the navigation/detail documentation split (section 12).
                "legacy_documenter/exporters/_documentation_partitioning.py",
                # V4.3-R2: deterministic FLOW/PATH/DAO/SP evidence selection
                # and hydration (see
                # docs/V4_3/V4_3_R2_EVIDENCE_HYDRATION_AND_SELECTION_RESULT.md).
                "legacy_documenter/context/hydration.py",
                # V4.3-R3: deterministic Spanish `HUMAN_DOCUMENTATION_PROJECTION`
                # renderer for hydrated FLOW records (see
                # docs/V4_3/V4_3_R3_HUMAN_DOCUMENTATION_RESULT.md).
                "legacy_documenter/documentation/human_flow_documentation.py",
                # V4.3-R4: deterministic system-scale navigation/partition
                # aggregation over many hydrated FLOW records, reusing
                # `render_flow_document` per flow and the V4.2-R8
                # `sanitize_label`/`build_partition_filenames` helpers (see
                # docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md).
                "legacy_documenter/documentation/human_documentation_scaling.py",
                # V4.3-R5: the budgeted `AI_HYDRATED_PROJECTION 1.0` package
                # builder (mandatory ceiling, `FULL` rejected) and the small
                # internal index/snapshot loader extracted out of
                # `ai_interpretation.py` (see
                # docs/V4_3/V4_3_R5_AI_CONTEXT_BUDGETING_RESULT.md).
                "legacy_documenter/context/ai_projection.py",
                "legacy_documenter/orchestration/_run_evidence_io.py",
                # V4.3-R6: the complete, unbudgeted `LegacyMapperConsumerProjection
                # 1.0` package builder -- independent of `ai_projection`/
                # `human_documentation`, no `SILENT_ENTRY_OMISSION` (see
                # docs/V4_3/V4_3_R6_AI_AND_CONSUMER_PROJECTION_RESULT.md).
                "legacy_documenter/context/consumer_projection.py",
                # V4.3-R7: the deterministic per-run output-tree manifest
                # builder for external pilot handoff (see
                # docs/V4_3/V4_3_R7_INTERNAL_ACCEPTANCE_RESULT.md).
                "legacy_documenter/cli/output_manifest.py",
            },
        )
        # V4.2-R7.1 corrected four real-pilot presentation/aggregation
        # findings (F-01 through F-04; see
        # docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md): FunctionalFlowResolver
        # gained two additive flow-level fields
        # (`has_confirmed_terminal`/`has_unresolved_boundary`, F-01) without
        # changing its existing status/confidence enum, and MarkdownExporter's
        # PROJECT_OVERVIEW.md/SOLUTION_STRUCTURE.md/WEBFORMS_MAP.md renderers
        # were corrected (F-04/F-02/F-03). `flow_resolver.py` and
        # `technical_documentation_renderer.py` were already in this set from
        # earlier rounds; `markdown_exporter.py` is added here for the first
        # time -- its line_count moves, no rename/restructuring.
        touched_paths = touched_paths | {"legacy_documenter/exporters/markdown_exporter.py"}
        # V4.3-R5 deduplicated the final-request-payload wrapper: the
        # construction that only existed inside `CopilotProvider._prompt`
        # moved verbatim to `legacy_documenter/llm/core.py` as
        # `render_request_payload`/`measure_request_payload` (so the size a
        # caller measures is the size actually sent), and `copilot.py`'s
        # `_prompt` now delegates to it. Both files' line counts/imports move;
        # neither is renamed, restructured, or changes behavior. See
        # docs/V4_3/V4_3_R5_AI_CONTEXT_BUDGETING_RESULT.md.
        touched_paths = touched_paths | {
            "legacy_documenter/llm/core.py", "legacy_documenter/llm/providers/copilot.py",
        }
        # V4.3-R7 acceptance-blocker correction (BLOQUEO 1/2): `router.py`
        # gained the new `output-manifest` subcommand route (BLOQUEO 1) and
        # `parser.py` gained its subparser; `main.py` gained the extra
        # `output-manifest` branch in its result-printing condition.
        # `markdown_exporter.py`/`technical_documentation_renderer.py` grew
        # their Spanish-by-default navigation/partition rendering (BLOQUEO 2)
        # further beyond the V4.2-R7.1/V4.3-R4 state already accounted for
        # above. None of these are renamed or restructured; only their
        # line counts/imports move.
        touched_paths = touched_paths | {
            "legacy_documenter/cli/router.py",
            "legacy_documenter/cli/parser.py",
            "legacy_documenter/exporters/technical_documentation_renderer.py",
        }
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
        # V4.3-R3 added one new HIGH-risk module
        # (`legacy_documenter/documentation/human_flow_documentation.py`, 335
        # lines after the round's own transaction/data-operation evidence
        # correction -- over the 200-line threshold, module-level rendering
        # functions well above two (`responsibility_count` > 2), and under
        # `legacy_documenter/documentation/`, one of the paths this tool's
        # heuristic always treats as historical; the combination reaches the
        # HIGH threshold even though the module has no branching complex
        # enough for VERY_HIGH and is a pure function with no I/O).
        r3_human_flow_documentation_path = "legacy_documenter/documentation/human_flow_documentation.py"
        # V4.3-R4 added one new HIGH-risk module
        # (`legacy_documenter/documentation/human_documentation_scaling.py`,
        # 239 lines -- over the 200-line threshold, and under
        # `legacy_documenter/documentation/`, the same historical-path
        # heuristic that already places `human_flow_documentation.py` in
        # HIGH rather than MEDIUM).
        r4_human_documentation_scaling_path = "legacy_documenter/documentation/human_documentation_scaling.py"
        # V4.3-R5 added one new HIGH-risk module
        # (`legacy_documenter/context/ai_projection.py`, 304 lines -- over the
        # 200-line threshold plus the historical-package +1 this tool's
        # heuristic applies to everything under `legacy_documenter/context/`,
        # the same combination that already places `hydration.py` above LOW).
        #
        # `legacy_documenter/orchestration/ai_interpretation.py` moved twice
        # within this same round, before R6 started: R5's initial projection/
        # gate/retry policy grew it from 190 to 348 lines (crossing MEDIUM ->
        # HIGH), and R5's own follow-up correction -- reserving output
        # capacity out of a declared `context_window` instead of handing the
        # whole window to the input payload, plus the `OutputReservationGateTests`
        # coverage that correction required (see
        # docs/V4_3/V4_3_R5_AI_CONTEXT_BUDGETING_RESULT.md section 3.2) -- grew
        # it further to 402 lines, crossing HIGH -> VERY_HIGH. The net result
        # is a single MEDIUM -> VERY_HIGH move for this one file, not a HIGH
        # entry: it belongs in `expected_very_high_risk_files` below, not in
        # `expected_high_risk_files`. It does not become an eighth
        # `responsibility_signals` category or gain a fifth responsibility
        # signal -- the index/snapshot loading responsibility remains
        # extracted into `_run_evidence_io.py` (see the new-path set above);
        # the VERY_HIGH classification here comes from line count and
        # `except_exception` handler count crossing this tool's thresholds,
        # not from a new responsibility.
        r5_ai_projection_path = "legacy_documenter/context/ai_projection.py"
        r5_ai_interpretation_path = "legacy_documenter/orchestration/ai_interpretation.py"
        # V4.3-R6 wired the new `legacy_documenter/context/consumer_projection.py`
        # (see the new-path set above) into the existing CONTEXT stage
        # (`pipeline_stages.build_context_artifacts`), which both `analyze` and
        # `full` already called: `consumer_projection` is deterministic and
        # never opt-in, so it is materialized unconditionally, alongside
        # `context/*.json` and `ai_context/*`, rather than as a new pipeline
        # stage identity (avoiding a ripple through `StageId`/`RunResult`/every
        # existing stage-list assertion for a file-write that shares CONTEXT's
        # exact failure boundary). That one new call plus its three new
        # imports (`ConsumerProjectionBuilder`, `atomic_write_text`,
        # `render_deterministic_json`, `sanitize_data`) grew
        # `pipeline_stages.py` from 421 to 454 lines and added a fourth
        # `responsibility_signals` category (this tool's own
        # `provider_or_network` name-hint heuristic fires on the word "LLM" in
        # this function's own docstring, explaining that `consumer_projection`
        # -- unlike `AI_INTERPRETATION` -- reaches no AI/LLM service; the
        # heuristic has no notion of negation, so it flags the mention rather
        # than real provider/network access, the same class of false positive
        # already accepted for other modules' docstrings in earlier rounds
        # rather than rewritten around). Four responsibility signals crosses
        # this tool's threshold from HIGH to VERY_HIGH.
        #
        # V4.3-R6's own follow-up correction (still before R7 started) --
        # partitioning `consumer_projection` deterministically instead of one
        # unbounded file, see
        # docs/V4_3/V4_3_R6_AI_AND_CONSUMER_PROJECTION_RESULT.md -- grew
        # `consumer_projection.py` from 142 to 283 lines (the manifest/
        # partition split, the losslessness guards, the deterministic
        # filename helpers) and `pipeline_stages.py` further, from 454 to 473
        # lines (serializing and syncing a dict of partitions instead of one
        # package). `consumer_projection.py` crosses from MEDIUM to HIGH
        # (`filesystem`/`validation` join the pre-existing
        # `provider_or_network`/`serialization` signals -- `filesystem` from
        # its own docstring mentioning `write_text`/`read_text` while
        # explaining that the module itself never calls them, another
        # instance of the same name-hint false positive; `validation` from
        # the module's own `raise ValueError`/`ConsumerProjectionError` fail-
        # closed guards, which are real). `pipeline_stages.py` stays
        # VERY_HIGH (it already crossed into that bucket at the step above;
        # this correction does not move it a second time).
        r6_consumer_projection_path = "legacy_documenter/context/consumer_projection.py"
        # V4.3-R7 BLOQUEO 1: the new `output-manifest` subcommand route added
        # a fourth top-level command branch plus its own manifest-building
        # helper function to `router.py`'s existing conditional-branching
        # dispatch, crossing it from MEDIUM (the pre-existing three-command
        # dispatch cited above) to HIGH.
        r7_router_path = "legacy_documenter/cli/router.py"
        # V4.3-R8 correction of external pilot findings P-02/P-03
        # (`docs/V4_3/V4_3_R8_EXTERNAL_PILOT_CORRECTIONS_RESULT.md`) restructured
        # `human_flow_documentation.py` to be summary-first (new sections 3/4,
        # a presentation-only technical/infrastructure name list, and a split
        # "qué queda no resuelto" section), growing it from 335 to 549 lines
        # and to four `responsibility_signals` categories (the same
        # docstring-name-hint false positive already accepted for other
        # modules in earlier rounds -- this module still never touches the
        # filesystem/network/a real serializer; `validation`/`filesystem`/
        # `provider_or_network` all fire on words used only to *explain*, in
        # prose, what this module does *not* do). Four signals crosses this
        # tool's threshold from HIGH to VERY_HIGH -- the same move R3's own
        # `ai_interpretation.py`/R6's `consumer_projection.py` growth already
        # made for the same reason; no restructuring/rename, no behavior
        # change to the underlying deterministic rendering logic.
        r8_human_flow_documentation_path = "legacy_documenter/documentation/human_flow_documentation.py"
        expected_high_risk_files = sorted(
            [p for p in on_disk_risk["high_risk_files"] if p not in (database_extractor_path, r2_main_path)]
            + [readiness_path, r6_presenter_path,
               r4_human_documentation_scaling_path, r5_ai_projection_path, r6_consumer_projection_path,
               r7_router_path]
        )
        expected_very_high_risk_files = sorted(
            [p for p in on_disk_risk["very_high_risk_files"] if p != readiness_path]
            + [r3_full_pipeline_path, r5_ai_interpretation_path, r2_pipeline_stages_path,
               r8_human_flow_documentation_path]
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
        # V4.2-R8 added one new LOW-risk module
        # (`legacy_documenter/exporters/_documentation_partitioning.py`, 65
        # lines -- deterministic filename derivation only, no branching
        # complex enough to leave LOW) and grew
        # `technical_documentation_renderer.py`/`markdown_exporter.py`/
        # `pipeline_stages.py`/`artifact_lifecycle.py` for the navigation/
        # detail documentation split without moving any of them across a
        # risk-category boundary.
        # V4.3-R2 added one new MEDIUM-risk module
        # (`legacy_documenter/context/hydration.py`, 204 lines -- over the
        # 200-line MEDIUM threshold and under the historical-package +1
        # this tool's heuristic applies to everything under
        # `legacy_documenter/context/`; no branching complex enough to
        # reach HIGH). V4.3-R3 added one new HIGH-risk module (see
        # r3_human_flow_documentation_path above) and, in its own
        # transaction/data-operation evidence correction, grew
        # `hydration.py` to 290 lines -- still MEDIUM (`responsibility_count`
        # stays low; no new branching complex enough for HIGH); MEDIUM's net
        # change from R3 is zero (no MEDIUM-bucket module added or removed),
        # HIGH grows by one.
        # V4.3-R4's Spanish-by-default correction (see
        # docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md section 13)
        # translated `project_dependencies_navigation`/
        # `project_dependencies_partitions`'s human-facing prose/headers into
        # Spanish, growing their docstrings/text enough that
        # `markdown_exporter.py` crosses from 112 to 204 lines -- over the
        # same 200-line MEDIUM threshold `hydration.py` already crossed at
        # R2 (no branching complex enough for HIGH) -- so it leaves LOW and
        # enters MEDIUM. This is the file's only category move from this
        # correction; `technical_documentation_renderer.py`'s own Spanish
        # translation (`web_entry_points_navigation`/`_partitions`) does not
        # cross a boundary (it was already well past any line-count
        # threshold and stays MEDIUM, per the V4.2-R3 comment above).
        # V4.3-R6's `consumer_projection.py` lands directly on HIGH (see the
        # comment above `expected_high_risk_files`) as a new path -- it never
        # touches MEDIUM at all (its post-partitioning line count/
        # responsibility signals already cross HIGH), so the MEDIUM
        # expression below carries no term for it.
        # V4.3-R7 adds one more new LOW-risk module: `cli/output_manifest.py`
        # (62 lines, pure filesystem enumeration/hashing, no branching).
        expected_categories = dict(on_disk_risk["files_by_risk_category"])
        expected_categories["LOW"] = expected_categories.get("LOW", 0) + 4 + 3 + 5 + 2 + 1 + 1 - 1 + 1 - 1 + 1
        expected_categories["MEDIUM"] = (
            expected_categories.get("MEDIUM", 0) + 3 + 1 + 1 + 1 + 1 + 1 - 1 + 1 + 1 + 1 + 1 - 1
        )
        # V4.3-R4's one new HIGH-risk module adds one more to this count.
        # V4.3-R5 adds one more: the new `context/ai_projection.py` (HIGH).
        # `orchestration/ai_interpretation.py` does NOT add to HIGH here --
        # see the comment above `r5_ai_interpretation_path`: across R5's
        # initial change and its own follow-up output-reservation correction
        # it crosses all the way from MEDIUM to VERY_HIGH, passing through
        # HIGH only transiently. MEDIUM's net change from R5 is zero:
        # `ai_interpretation.py` leaves it and the new
        # `orchestration/_run_evidence_io.py` enters it, so the MEDIUM
        # expression above is unchanged.
        # V4.3-R6's `pipeline_stages.py` HIGH -> VERY_HIGH move (see the
        # comment above `expected_high_risk_files`) removes one more from HIGH
        # -- it was counted as an R2 HIGH entrant in this expression (one of
        # the trailing `+ 1` terms) and no longer belongs there. The new
        # `consumer_projection.py` (same round's own follow-up correction)
        # adds one back: a new HIGH-risk path, net zero against the removal.
        # V4.3-R7's `router.py` MEDIUM -> HIGH move (see the comment above
        # `expected_high_risk_files`) adds one more; MEDIUM's own net change
        # for this same move is folded into the MEDIUM expression above via
        # its trailing `- 1`.
        # V4.3-R8's `human_flow_documentation.py` HIGH -> VERY_HIGH move (see
        # `r8_human_flow_documentation_path` above) removes one more from
        # HIGH -- it was counted as an R3 HIGH entrant in this expression
        # (one of the leading `+ 1` terms) and no longer belongs there.
        expected_categories["HIGH"] = (
            expected_categories.get("HIGH", 0) + 1 - 1 + 1 - 1 + 1 - 1 + 1 + 1 + 1 + 1 + 1 - 1
        )
        # `ai_interpretation.py`'s MEDIUM -> VERY_HIGH move (see above) is one
        # `+ 1` here, on top of the pre-existing readiness.py/full_pipeline.py
        # swap (`- 1 + 1`, net zero); `pipeline_stages.py`'s HIGH -> VERY_HIGH
        # move (this same round) is another; V4.3-R8's
        # `human_flow_documentation.py` HIGH -> VERY_HIGH move (see above) is
        # the last `+ 1`.
        expected_categories["VERY_HIGH"] = expected_categories.get("VERY_HIGH", 0) - 1 + 1 + 1 + 1 + 1
        self.assertEqual(fresh_risk["files_by_risk_category"], expected_categories)
        normalized_on_disk.pop("risk_summary", None)
        normalized_fresh.pop("risk_summary", None)

        # Twenty-nine new production modules total (one from V4.1-R1, three
        # from V4.1-R4's readiness split, six from V4.1-R6's DatabaseExtractor/
        # FunctionalFlowResolver splits, six from V4.2-R1's new
        # `legacy_documenter/cli/` package, two from V4.2-R2's
        # pipeline_stages.py/full_pipeline.py, one from V4.2-R3's
        # technical_documentation_renderer.py, three from V4.2-R4's new
        # `legacy_documenter/orchestration/` package, one from V4.2-R5's new
        # run_summary_presenter.py, two from V4.2-R6's new
        # atomic_write.py/artifact_lifecycle.py, one from V4.2-R8's new
        # _documentation_partitioning.py, one from V4.3-R2's new
        # hydration.py, one from V4.3-R3's new human_flow_documentation.py,
        # one from V4.3-R4's new human_documentation_scaling.py); every
        # other dependency-direction finding is unaffected -- the new
        # modules only import from `legacy_documenter.knowledge.readiness`,
        # `legacy_documenter.knowledge.proposals`, `legacy_documenter.llm`,
        # `legacy_documenter.context`, `legacy_documenter.utils`, and the
        # existing analysis/context/exporters/extractors/scanner packages
        # `main.py` already depended on, all already-established dependency
        # directions. `hydration.py` itself imports only the stdlib
        # `collections` module, `human_flow_documentation.py` imports
        # nothing beyond its own module, and `human_documentation_scaling.py`
        # imports only its own sibling module
        # (`.human_flow_documentation`) and
        # `legacy_documenter.exporters._documentation_partitioning` -- an
        # already-established dependency direction
        # (`legacy_documenter/exporters/technical_documentation_renderer.py`
        # already imports the same module) -- so none of these is a new
        # internal dependency direction.
        on_disk_dep = dict(on_disk["dependency_findings"])
        fresh_dep = dict(fresh["dependency_findings"])
        # V4.3-R5 adds two more (ai_projection.py, _run_evidence_io.py): 31.
        # `ai_projection.py` imports only its own siblings
        # (`.composer`, `.hydration`) and the stdlib; `_run_evidence_io.py`
        # imports only the stdlib; `ai_interpretation.py` now additionally
        # imports `legacy_documenter.context.ai_projection` -- the same
        # already-established `orchestration -> context` direction it already
        # had via `context.composer`/`context.resolver`.
        # V4.3-R6 adds one more (consumer_projection.py): 32.
        # `consumer_projection.py` imports only its own sibling `.hydration`
        # -- the same already-established `context -> context` sibling
        # direction `ai_projection.py` already uses; `pipeline_stages.py` now
        # additionally imports `legacy_documenter.context.consumer_projection`
        # (already-established `cli -> context`, same as its existing
        # `context_builder`/`system_context_builder` imports) and
        # `legacy_documenter.utils.atomic_write`/`.json_rendering`/
        # `.sanitizer` (already-established `cli -> utils`, the same
        # direction `full_pipeline.py` already uses for the first two) -- so
        # none of these is a new internal dependency direction either.
        # V4.3-R7 adds one more (`cli/output_manifest.py`, stdlib-only, no
        # internal imports at all): 33. `pipeline_stages.py` also gains
        # `legacy_documenter.context.hydration` (already-established
        # `cli -> context`) and, for the first time, `legacy_documenter
        # .documentation.human_documentation_scaling` -- a genuinely new
        # `cli -> documentation` direction (the R3/R4 human-documentation
        # renderers were pure library capabilities with no `cli` caller
        # until this round's wiring decision). `find_cycles`/the acyclic
        # `knowledge_domain_direction` check are both unaffected: this is an
        # acyclic, one-way, human-facing-only addition (`documentation` still
        # never imports anything under `cli`), so it does not appear in
        # `cycles_detected` and does not change `dependency_findings` beyond
        # `module_count`.
        self.assertEqual(fresh_dep.pop("module_count"), on_disk_dep.pop("module_count") + 33)
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
        # V4.3-R3: `legacy_documenter/documentation/human_flow_documentation.py`
        # (335 lines, after the same round's later transaction/data-operation
        # evidence correction) newly enters the top-20, pushing
        # `legacy_documenter/knowledge/provenance/graph.py` (untouched by R3)
        # below the cutoff -- the same ranking-membership effect already
        # seen at R2/R3/R6. That same correction also grew
        # `legacy_documenter/context/hydration.py` (204 -> 290 lines: the new
        # `_transaction_evidence`/`_transactions`/`_data_operations` methods,
        # see docs/V4_3/V4_3_R3_HUMAN_DOCUMENTATION_RESULT.md) enough to enter
        # the top-20 too, pushing
        # `legacy_documenter/knowledge/projection/example_report.py`
        # (untouched by R3) below the cutoff.
        r3_provenance_graph_path = "legacy_documenter/knowledge/provenance/graph.py"
        r3_example_report_path = "legacy_documenter/knowledge/projection/example_report.py"
        # V4.3-R4: `human_documentation_scaling.py` (239 lines) newly enters
        # the top-20, pushing `legacy_documenter/knowledge/plugin_projection/
        # models.py` (untouched by R4) below the cutoff -- the same
        # ranking-membership effect already seen at R2/R3/R6.
        r4_human_documentation_scaling_path = "legacy_documenter/documentation/human_documentation_scaling.py"
        r4_plugin_projection_models_path = "legacy_documenter/knowledge/plugin_projection/models.py"
        new_largest_modules = {
            "legacy_documenter/cli/pipeline_stages.py", "legacy_documenter/cli/full_pipeline.py",
            "legacy_documenter/exporters/technical_documentation_renderer.py",
            "legacy_documenter/cli/run_summary_presenter.py",
            "legacy_documenter/documentation/human_flow_documentation.py",
            "legacy_documenter/context/hydration.py",
            r4_human_documentation_scaling_path,
            # V4.3-R5: `ai_projection.py` (304 lines) and the grown
            # `ai_interpretation.py` (402 lines after R5's own follow-up
            # output-reservation correction; see the comment above
            # `r5_ai_interpretation_path`) newly enter the top-20,
            # pushing `legacy_documenter/analysis/web_entry_resolver.py` and
            # `legacy_documenter/knowledge/approval/service.py` (neither
            # touched by R5) below the cutoff -- the same ranking-membership
            # effect already seen at R2/R3/R6/R4.
            r5_ai_projection_path,
            r5_ai_interpretation_path,
            # V4.3-R6's own follow-up correction (partitioning): the grown
            # `consumer_projection.py` (283 lines, see the comment above
            # `r6_consumer_projection_path`) also newly enters the top-20,
            # pushing one more untouched file below the cutoff.
            "legacy_documenter/context/consumer_projection.py",
        }
        r5_web_entry_resolver_path = "legacy_documenter/analysis/web_entry_resolver.py"
        r5_approval_service_path = "legacy_documenter/knowledge/approval/service.py"
        r6_relations_service_path = "legacy_documenter/knowledge/relations/service.py"
        dropped_largest_modules = {
            main_path, readiness_path, r3_projection_rules_path, r6_projection_models_path,
            r3_provenance_graph_path, r3_example_report_path, r4_plugin_projection_models_path,
            r5_web_entry_resolver_path, r5_approval_service_path, r6_relations_service_path,
        }
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
                    # V4.3-R5: the internal index/snapshot loader that reads
                    # this run's own `index/*.json` and
                    # `ai_context/SYSTEM_CONTEXT.json` -- a real, deliberate
                    # filesystem read, extracted out of `ai_interpretation.py`
                    # (which remains flagged for its own `os` import).
                    "legacy_documenter/orchestration/_run_evidence_io.py",
                    # V4.3-R7: the deterministic per-run output-tree manifest
                    # builder -- reads and hashes every file already under
                    # `--output`, a real, deliberate filesystem read.
                    "legacy_documenter/cli/output_manifest.py",
                    # V4.3-R7 acceptance-blocker correction (BLOQUEO 1): the
                    # new `output-manifest` route (`_route_output_manifest`)
                    # imports `Path` and calls `atomic_write_text` directly
                    # to write `OUTPUT_MANIFEST.json` -- a real, deliberate
                    # filesystem write, not a stray import.
                    "legacy_documenter/cli/router.py",
                ])
                self.assertEqual(sorted(fresh_entry["files"]), expected_files)
                self.assertEqual(fresh_entry["file_count"], entry["file_count"] + 12)
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
        # V4.2-R7.1 corrected F-02/F-03/F-04 in `MarkdownExporter` (safe
        # repository display label, duplicate-solution disambiguation,
        # register-field rendering); its class grows (new helper logic),
        # unlike database_extractor.py/flow_resolver.py above, which shrank.
        # V4.3-R4's correction (section 12) adds
        # `project_dependencies_navigation`/`project_dependencies_partitions`
        # to the same class (PROJECT_DEPENDENCIES.md reopened for
        # partitioning): two more methods (8 -> 10) and enough more lines
        # that `MarkdownExporter` crosses this tool's method-count threshold
        # for its own classification, moving from `OK` to `REVIEW` -- a
        # class-shape observation this heuristic already makes for other
        # sizeable classes, not evidence of a defect.
        markdown_exporter_path = "legacy_documenter/exporters/markdown_exporter.py"
        # V4.3-R2's new `EvidenceHydrator` class (204-line module; the whole
        # deterministic selection/hydration/resolution surface lives on one
        # class) enters this top-N list too, displacing
        # `WebEventExtractor` (`legacy_documenter/extractors/web_event_extractor.py`,
        # untouched by R2) below the cutoff -- the same ranking-membership
        # effect as `r3_renderer_path`/`r3_vbnet_extractor_path` above.
        r2_hydrator_path = "legacy_documenter/context/hydration.py"
        r2_web_event_extractor_path = "legacy_documenter/extractors/web_event_extractor.py"
        # V4.3-R5: `CopilotProvider._prompt`'s inline payload construction moved
        # verbatim to the shared `legacy_documenter.llm.core.render_request_payload`
        # and the method now delegates to it with a docstring explaining why --
        # net +5 lines on the class, same method_count, same classification, no
        # behavior change (a dedicated test asserts `_prompt` returns exactly
        # `render_request_payload`'s output).
        r5_copilot_provider_path = "legacy_documenter/llm/providers/copilot.py"
        on_disk_classes = {e["path"]: e for e in on_disk["largest_classes"]}
        fresh_classes = {e["path"]: e for e in fresh["largest_classes"]}
        self.assertEqual(set(fresh_classes) - set(on_disk_classes), {r3_renderer_path, r2_hydrator_path})
        self.assertEqual(set(on_disk_classes) - set(fresh_classes), {r3_vbnet_extractor_path, r2_web_event_extractor_path})
        for path, entry in on_disk_classes.items():
            if path in (r3_vbnet_extractor_path, r2_web_event_extractor_path):
                continue
            fresh_entry = dict(fresh_classes[path])
            if path in (database_extractor_path, flow_resolver_path):
                self.assertLess(fresh_entry["line_count"], entry["line_count"])
                fresh_entry["line_count"] = entry["line_count"]
            elif path == markdown_exporter_path:
                self.assertGreater(fresh_entry["line_count"], entry["line_count"])
                self.assertGreater(fresh_entry["method_count"], entry["method_count"])
                fresh_entry["line_count"] = entry["line_count"]
                fresh_entry["method_count"] = entry["method_count"]
                fresh_entry["classification"] = entry["classification"]
            elif path == r5_copilot_provider_path:
                self.assertGreater(fresh_entry["line_count"], entry["line_count"])
                self.assertEqual(fresh_entry["method_count"], entry["method_count"])
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
        # R3 had grown `TechnicalDocumentationRenderer.database_access`/
        # `.unresolved_findings`/`.functional_flows` (the last one further at
        # R7.1) enough to enter this top-N list, temporarily displacing
        # `DatabaseResolver.resolve`/`FunctionalFlowResolver.resolve`/
        # `CanonicalCompositionService.compose`/`build_projection_example`
        # below the cutoff. V4.2-R8 extracted each renderer's per-item
        # rendering into shared helper functions (`_render_flow_entry_lines`,
        # `_data_access_table_lines`, `_render_unresolved_category_body`, ...)
        # reused by both the flat and the new partitioned/navigation methods
        # -- this shrinks the three top-level flat methods back down enough
        # that none of them are in this top-N list any more, and the four
        # temporarily-displaced functions are back, restoring the exact
        # pre-R3 top-N membership net of R2's own two changes. Only
        # `FunctionalFlowResolver.resolve` (which R8 did not touch) remains
        # genuinely grown relative to on-disk, handled below via
        # `r7_1_regrown_function`.
        r7_1_regrown_function = ("legacy_documenter/analysis/flow_resolver.py", "FunctionalFlowResolver.resolve")
        # V4.3-R5: two functions newly enter this top-N list --
        # `AiProjectionBuilder.package` (the budget application: ordering,
        # exact character accounting, statistics, truncation) and the grown
        # `run_ai_interpretation` (projection + payload gate + validation).
        # They displace `DatabaseResolver.resolve` and
        # `CanonicalCompositionService.compose` (neither touched by R5) below
        # the cutoff -- the same ranking-membership effect as `largest_modules`.
        r5_new_functions = {
            ("legacy_documenter/context/ai_projection.py", "AiProjectionBuilder.package"),
            ("legacy_documenter/orchestration/ai_interpretation.py", "run_ai_interpretation"),
        }
        r5_dropped_functions = {
            ("legacy_documenter/analysis/database_resolver.py", "DatabaseResolver.resolve"),
            ("legacy_documenter/knowledge/canonical/service.py", "CanonicalCompositionService.compose"),
        }
        self.assertEqual(set(fresh_funcs) - set(on_disk_funcs), {r2_new_function} | r5_new_functions)
        self.assertEqual(set(on_disk_funcs) - set(fresh_funcs), {r2_dropped_function} | r5_dropped_functions)
        for key, entry in on_disk_funcs.items():
            if key in (r2_dropped_function, *r5_dropped_functions):
                continue
            fresh_entry = dict(fresh_funcs[key])
            if key == r7_1_regrown_function:
                self.assertGreater(fresh_entry["line_count"], entry["line_count"])
                fresh_entry["line_count"] = entry["line_count"]
            self.assertEqual(fresh_entry, entry)
        normalized_on_disk.pop("largest_functions", None)
        normalized_fresh.pop("largest_functions", None)

        # documentation_candidates is also a relative-threshold diagnostic
        # (below-average docstring_coverage_percent): the delegating methods
        # added to database_extractor.py/flow_resolver.py raised their own
        # docstring coverage enough to drop both off this list, which
        # mechanically admits two previously-just-below-average files.
        # V4.3-R7 acceptance-blocker correction (BLOQUEO 1/2): `copilot.py`'s
        # own docstring coverage rose (V4.3-R5's `_prompt` now documents its
        # delegation to the shared `render_request_payload`), dropping it off
        # this list too; `technical_documentation_renderer.py` newly admits
        # itself, its own docstring coverage diluted by the many new
        # `*_es`-suffixed Spanish-rendering helper functions this correction
        # added (each already documented, but the file's function count grew
        # faster than its docstring count).
        r6_resolved_doc_candidates = {
            database_extractor_path, flow_resolver_path, "legacy_documenter/llm/providers/copilot.py",
        }
        r6_newly_below_average_doc = {
            "legacy_documenter/context/system_context_builder.py",
            "legacy_documenter/extractors/vbnet_extractor.py",
            "legacy_documenter/exporters/technical_documentation_renderer.py",
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
