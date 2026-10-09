from __future__ import annotations

import itertools
import json
import os
import random
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter import cache as cache_pkg
from legacy_documenter.cache import (
    CACHE_DIRNAME, MANIFEST_FILENAME, METRICS_FILENAME, METRICS_SCHEMA_VERSION, analyze_scope, read_run_metrics,
    validate_cache, write_run_metrics,
)
from legacy_documenter.cache import context as cache_context, run_metrics
from legacy_documenter.cache.diff import FileStateDiff
from legacy_documenter.cache.scope import GLOBAL_RESOLUTION, LIST_LIMIT, MODE_FULL, MODE_PARTIAL
from legacy_documenter.cli import pipeline_stages as stages
from legacy_documenter.cli.execution_model import RunStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.cli.output_manifest import build_output_manifest
from legacy_documenter.utils.stage_timings import TIMINGS

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "legacy_documenter"
FULL_SAMPLE = ROOT / "tests" / "fixtures" / "v4_2_r7_full_sample"
NONDETERMINISTIC = {"RUN_SUMMARY.json", "RUN_SUMMARY.md", "repository.json"}
STAGES = {
    "SCAN", "EXTRACTION", "CALL_RESOLUTION", "WEB_ENTRY_RESOLUTION", "DATABASE_RESOLUTION", "FLOW_RESOLUTION",
    "DEPENDENCY_RESOLUTION", "EXPORT", "CONTEXT", "DOCUMENTATION",
}


def _tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*"))
            if p.is_file() and p.name not in NONDETERMINISTIC and p.relative_to(root).parts[0] != CACHE_DIRNAME}


def _diff(modified=(), added=(), deleted=(), renamed=()) -> FileStateDiff:
    return FileStateDiff(modified=list(modified), added=list(added), deleted=list(deleted), renamed_candidates=list(renamed))


PROJECTS = [
    {"path": "Bl\\Bl.vbproj", "compile_items": ["A.vb", "Sub\\B.vb"], "content_items": ["Web.config", "page.aspx"]},
    {"path": "Web\\Web.vbproj", "compile_items": ["Page.vb"], "content_items": []},
    {"path": "Top\\Top.vbproj", "compile_items": ["T.vb"], "content_items": []},
    {"path": "Lone\\Lone.vbproj", "compile_items": ["L.vb"], "content_items": []},
]
DEPENDENCIES = [
    {"dependency_type": "Project -> Project", "source": "Web\\Web.vbproj", "target": "..\\Bl\\Bl.vbproj"},
    {"dependency_type": "Project -> Project", "source": "Top\\Top.vbproj", "target": "..\\Web\\Web.vbproj"},
    {"dependency_type": "Project -> SourceFile", "source": "Bl\\Bl.vbproj", "target": "A.vb"},
]
TYPES = {
    "Bl/A.vb": "vb_source", "Bl/Sub/B.vb": "vb_source", "Bl/Web.config": "web_config", "Bl/page.aspx": "aspx",
    "Web/Page.vb": "vb_source", "Top/T.vb": "vb_source", "Lone/L.vb": "vb_source", "Bl/Bl.vbproj": "vb_project",
    "Web/Web.vbproj": "vb_project", "S.sln": "solution", "Bl/logo.png": "image", "Orphan/O.vb": "vb_source",
}


def _scope(diff, **kwargs):
    args = dict(fallback_reason=None, file_types=TYPES, projects=PROJECTS, dependencies=DEPENDENCIES, symbols=[])
    args.update(kwargs)
    return analyze_scope(diff, **args)


# =========================== scope analysis (unit) ============================================================
class ScopeUnitTests(unittest.TestCase):
    def test_no_changes(self):
        result = _scope(_diff())
        self.assertEqual((result.mode, result.impacted_projects, result.transitive_projects), (MODE_PARTIAL, [], []))
        self.assertEqual(result.reasons, {"NO_CHANGES": 1})

    def test_modified_file_maps_to_its_project_and_dependents(self):
        result = _scope(_diff(modified=["Bl/A.vb"]))
        self.assertEqual(result.mode, MODE_FULL)  # code can change global name resolution: never a bound
        self.assertEqual(result.unknowns, [])
        self.assertEqual(result.impacted_projects, ["Bl/Bl.vbproj"])  # the known floor is still reported
        self.assertEqual(result.transitive_projects, ["Top/Top.vbproj", "Web/Web.vbproj"])  # transitive closure
        self.assertEqual(result.reasons, {"SOURCE_IN_PROJECT": 1})
        self.assertEqual(result.unassertable, [GLOBAL_RESOLUTION])
        self.assertEqual(result.changed_files, {"modified": ["Bl/A.vb"]})

    def test_added_and_deleted_mapped_files(self):
        result = _scope(_diff(added=["Web/Page.vb"], deleted=["Lone/L.vb"]))
        self.assertEqual(result.mode, MODE_FULL)
        self.assertEqual(result.impacted_projects, ["Lone/Lone.vbproj", "Web/Web.vbproj"])
        self.assertEqual(result.transitive_projects, ["Top/Top.vbproj"])
        self.assertEqual(set(result.changed_files), {"added", "deleted"})

    def test_rename_is_deleted_plus_added_and_candidates_never_reduce_scope(self):
        diff = _diff(added=["Orphan/Renamed.vb"], deleted=["Lone/L.vb"], renamed=[{"from": "Lone/L.vb", "to": "Orphan/Renamed.vb", "basis": "semantic"}])
        result = _scope(diff, file_types={**TYPES, "Orphan/Renamed.vb": "vb_source"})
        self.assertEqual(result.mode, MODE_FULL)  # the new path is listed by no project
        self.assertIn("UNMAPPED_ANALYZED_FILE", result.unknowns)
        self.assertEqual(set(result.changed_files), {"added", "deleted"})

    def test_file_to_project_mapping_is_case_and_separator_insensitive(self):
        result = _scope(_diff(modified=["bl/sub/b.vb"]), file_types={"bl/sub/b.vb": "vb_source"})
        self.assertEqual(result.impacted_projects, ["Bl/Bl.vbproj"])

    def test_unknown_mapping_means_full(self):
        result = _scope(_diff(modified=["Orphan/O.vb"]))
        self.assertEqual((result.mode, result.unknowns), (MODE_FULL, ["UNMAPPED_ANALYZED_FILE"]))

    def test_unknown_file_type_means_full(self):
        result = _scope(_diff(added=["Mystery/x.bin"]), file_types={})
        self.assertEqual((result.mode, result.unknowns), (MODE_FULL, ["UNKNOWN_FILE_TYPE"]))

    def test_vbproj_change_covers_the_whole_project_and_its_dependents(self):
        result = _scope(_diff(modified=["Web/Web.vbproj"]))
        self.assertEqual(result.mode, MODE_FULL)  # RootNamespace/Compile changes reach other projects (measured on IST)
        self.assertEqual(result.unassertable, [GLOBAL_RESOLUTION])
        self.assertEqual(result.impacted_projects, ["Web/Web.vbproj"])
        self.assertEqual(result.transitive_projects, ["Top/Top.vbproj"])
        self.assertEqual(result.reasons, {"PROJECT_FILE": 1})

    def test_solution_change_is_conservative(self):
        result = _scope(_diff(modified=["S.sln"]))
        self.assertEqual((result.mode, result.unknowns), (MODE_FULL, ["SOLUTION_CHANGED"]))

    def test_web_config_maps_through_content_items_else_full(self):
        mapped = _scope(_diff(modified=["Bl/Web.config"]))
        self.assertEqual((mapped.mode, mapped.impacted_projects, mapped.reasons), (MODE_PARTIAL, ["Bl/Bl.vbproj"], {"WEB_CONFIG_IN_PROJECT": 1}))
        unmapped = _scope(_diff(modified=["Other/web.config"]), file_types={"Other/web.config": "web_config"})
        self.assertEqual((unmapped.mode, unmapped.reasons), (MODE_FULL, {"UNMAPPED_WEB_CONFIG": 1}))

    def test_only_bounded_changes_are_partial_candidates(self):
        for diff in (_diff(), _diff(modified=["Bl/Web.config"]), _diff(modified=["Bl/logo.png"]), _diff(added=["Bl/logo2.png"])):
            result = _scope(diff, file_types={**TYPES, "Bl/logo2.png": "image"})
            self.assertEqual((result.mode, result.unassertable, result.to_dict()["reach"]), (MODE_PARTIAL, [], "bounded"), diff)
        for diff in (_diff(modified=["Bl/A.vb"]), _diff(modified=["Bl/page.aspx"]), _diff(modified=["Web/Web.vbproj"]), _diff(modified=["S.sln"])):
            result = _scope(diff)
            self.assertEqual((result.mode, result.unassertable, result.to_dict()["reach"]), (MODE_FULL, [GLOBAL_RESOLUTION], "global_resolution"), diff)

    def test_unanalyzed_files_are_inventory_only(self):
        result = _scope(_diff(modified=["Bl/logo.png"]))
        self.assertEqual((result.mode, result.inventory_only, result.impacted_projects), (MODE_PARTIAL, ["Bl/logo.png"], []))
        self.assertEqual(result.unassertable, [])  # cannot alter extraction or resolution
        self.assertEqual(result.reasons, {"INVENTORY_ONLY": 1})

    def test_transitive_closure_follows_chains_and_stops_on_cycles(self):
        deps = [*DEPENDENCIES, {"dependency_type": "Project -> Project", "source": "Bl\\Bl.vbproj", "target": "..\\Top\\Top.vbproj"}]
        result = _scope(_diff(modified=["Lone/L.vb", "Top/T.vb"]), dependencies=deps)
        self.assertEqual(result.impacted_projects, ["Lone/Lone.vbproj", "Top/Top.vbproj"])
        self.assertEqual(result.transitive_projects, ["Bl/Bl.vbproj", "Web/Web.vbproj"])

    def test_references_resolve_by_file_name_when_the_relative_path_misses_and_external_ones_are_counted(self):
        deps = [
            *DEPENDENCIES,
            # written relative to the solution root (old solutions): resolved by file name -> widening
            {"dependency_type": "Project -> Project", "source": "Top\\Top.vbproj", "target": "Elsewhere\\Lone\\Lone.vbproj"},
            {"dependency_type": "Project -> Project", "source": "Web\\Web.vbproj", "target": "..\\Gone\\Gone.vbproj"},
        ]
        result = _scope(_diff(modified=["Lone/L.vb"]), dependencies=deps)
        self.assertEqual((result.mode, result.impacted_projects, result.transitive_projects), (MODE_FULL, ["Lone/Lone.vbproj"], ["Top/Top.vbproj"]))
        self.assertEqual(result.external_project_references, 1)  # Gone.vbproj is not in the repository
        self.assertEqual(result.to_dict()["external_project_references"], 1)

    def test_deterministic_ordering_and_duplicate_input(self):
        base = ["Web/Page.vb", "Bl/A.vb", "Lone/L.vb", "Bl/Sub/B.vb", "Bl/Web.config"]
        expected = _scope(_diff(modified=sorted(base))).to_dict()
        rng = random.Random(7)
        for _ in range(5):
            shuffled = base * 2  # duplicates
            rng.shuffle(shuffled)
            self.assertEqual(_scope(_diff(modified=shuffled)).to_dict(), expected)
        self.assertEqual(expected["changed_files"]["modified"]["items"], sorted(base))

    def test_symbols_in_changed_files_are_counted_without_payloads(self):
        symbols = [{"file": "Bl\\A.vb", "name": "X", "secret": "Password=abc"}, {"file": "Bl\\A.vb", "name": "Y"}, {"file": "Web\\Page.vb", "name": "Z"}]
        result = _scope(_diff(modified=["Bl/A.vb"]), symbols=symbols)
        self.assertEqual(result.symbols_in_changed_files, {"Bl/A.vb": 2})
        self.assertNotIn("abc", json.dumps(result.to_dict()))

    def test_incompatible_or_missing_cache_means_full(self):
        for reason in ("NO_CACHE", "ANALYSIS_CONFIG_MISMATCH", "ANALYZER_CODE_FINGERPRINT_MISMATCH"):
            result = analyze_scope(None, reason, TYPES, None, None, None)
            self.assertEqual((result.mode, result.fallback_reason), (MODE_FULL, reason))

    def test_persisted_lists_are_capped_but_counts_are_exact(self):
        files = [f"Lone/F{i:04d}.vb" for i in range(LIST_LIMIT + 50)]
        result = _scope(_diff(modified=files), file_types={f: "image" for f in files})
        payload = result.to_dict()["changed_files"]["modified"]
        self.assertEqual((payload["count"], len(payload["items"]), payload["truncated"]), (LIST_LIMIT + 50, LIST_LIMIT, True))


# =========================== run metrics (unit) ===============================================================
class _Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.repo = self.tmp / "repo"
        shutil.copytree(FULL_SAMPLE, self.repo)
        self.out = self.tmp / "out"

    def run_pipeline(self, **kwargs):
        return run_full_pipeline(self.repo, self.out, kwargs.pop("excludes", None), 12, **kwargs)

    def metrics(self) -> dict:
        return json.loads((self.out / CACHE_DIRNAME / METRICS_FILENAME).read_text(encoding="utf-8"))

    def reference(self) -> dict[str, bytes]:
        ref = self.tmp / "reference"
        if not ref.exists():
            run_full_pipeline(self.repo, ref, None, 12, cache_mode="off")
        return _tree(ref)


class RunMetricsTests(_Case):
    def test_schema_is_stable(self):
        self.run_pipeline()
        document = self.metrics()
        self.assertEqual(set(document), set(run_metrics.TOP_LEVEL_KEYS))
        self.assertEqual((document["contract"], document["schema_version"]), ("LegacyMapperRunMetrics", METRICS_SCHEMA_VERSION))
        self.assertEqual(set(document["file_state"]), {
            "files_total", "unchanged", "modified", "added", "deleted", "renamed_candidates", "line_ending_only",
            "validate_seconds", "file_state_build_seconds", "diff_seconds"})
        self.assertEqual(document["cache_verification"], "byte_compare")
        self.assertEqual(document["total_seconds"] >= 0, True)
        self.assertTrue(document["started_at"] <= document["completed_at"])

    def test_cold_run(self):
        self.run_pipeline()
        document = self.metrics()
        self.assertEqual((document["mode"], document["session_mode"], document["final_status"]), ("full", "cold", "SUCCESS"))
        self.assertEqual(document["fallback_reason"], "NO_CACHE")
        self.assertEqual(document["scope"]["mode"], "full")
        self.assertEqual(document["file_state"]["unchanged"], None)  # no previous state to compare

    def test_warm_run_without_changes(self):
        self.run_pipeline()
        self.run_pipeline()
        document = self.metrics()
        self.assertEqual((document["mode"], document["session_mode"]), ("incremental", "warm"))
        state = document["file_state"]
        self.assertEqual((state["unchanged"], state["modified"], state["added"], state["deleted"]), (state["files_total"], 0, 0, 0))
        self.assertEqual((document["scope"]["mode"], document["scope"]["reasons"]), ("partial_candidate", {"NO_CHANGES": 1}))

    def test_fallback_run_records_the_reason(self):
        self.run_pipeline()
        (self.out / CACHE_DIRNAME / MANIFEST_FILENAME).write_bytes(b"corrupt")
        self.run_pipeline()
        document = self.metrics()
        self.assertEqual((document["mode"], document["session_mode"], document["fallback_reason"]), ("full", "fallback_full", "MANIFEST_CORRUPT"))
        self.run_pipeline(cache_mode="refresh")
        self.assertEqual(self.metrics()["mode"], "refresh")

    def test_file_state_counters_after_a_change(self):
        self.run_pipeline()
        target = self.repo / "Bl" / "CustomerService.vb"
        target.write_text(target.read_text(encoding="utf-8") + "\r\n' changed\r\n", encoding="utf-8")
        (self.repo / "Bl" / "New.vb").write_text("Public Class New1\r\nEnd Class\r\n", encoding="utf-8")
        self.run_pipeline()
        state = self.metrics()["file_state"]
        self.assertEqual((state["modified"], state["added"], state["deleted"]), (1, 1, 0))
        self.assertEqual(state["unchanged"] + 2, state["files_total"])

    def test_extraction_cache_metrics(self):
        self.run_pipeline()
        self.run_pipeline()
        extraction = self.metrics()["extraction_cache"]
        for key in ("extraction_cache_hits", "extraction_cache_misses", "extraction_cache_bypass", "files_reused", "files_extracted",
                    "shards_loaded", "shards_invalid", "shards_rewritten", "load_seconds", "parse_seconds", "validate_seconds",
                    "persist_seconds", "reuse_disabled_reason"):
            self.assertIn(key, extraction)
        self.assertGreater(extraction["files_reused"], 0)
        self.assertEqual(extraction["extraction_cache_misses"], 0)

    def test_write_skip_metrics_per_family(self):
        self.run_pipeline()
        self.run_pipeline()
        write_skip = self.metrics()["write_skip"]
        self.assertTrue({"index", "evidence", "consumer_projection", "ai_context", "documentation"} <= set(write_skip))
        for counters in write_skip.values():
            self.assertEqual(set(counters), {"generated", "written", "skipped_identical", "bytes_generated", "bytes_written", "compare_seconds", "write_seconds"})
        self.assertEqual(write_skip["ai_context"]["written"], 0)

    def test_stage_timings_use_real_stage_names(self):
        self.run_pipeline()
        document = self.metrics()
        self.assertTrue(STAGES <= set(document["stage_seconds"]))
        self.assertTrue(all(value >= 0 for value in document["stage_seconds"].values()))
        self.assertIsNotNone(document["extraction_postprocess_seconds"])
        self.assertIn("distinct_flows_hydrated", document["hydration"])

    def test_metrics_do_not_affect_outputs_hashes_or_the_cache(self):
        self.run_pipeline()
        before = _tree(self.out)
        self.run_pipeline()
        self.assertEqual(_tree(self.out), before)
        context = cache_context.build_context(self.repo.resolve(), None, 12)
        self.assertTrue(validate_cache(self.out / CACHE_DIRNAME, context).valid)
        manifest = (self.out / CACHE_DIRNAME / MANIFEST_FILENAME).read_text(encoding="utf-8")
        self.assertNotIn("RUN_METRICS", manifest)
        self.assertEqual(_tree(self.out), self.reference())

    def test_corrupt_metrics_are_ignored_and_replaced(self):
        self.run_pipeline()
        path = self.out / CACHE_DIRNAME / METRICS_FILENAME
        path.write_bytes(b"{not json")
        self.assertIsNone(read_run_metrics(self.out / CACHE_DIRNAME))
        context = cache_context.build_context(self.repo.resolve(), None, 12)
        self.assertTrue(validate_cache(self.out / CACHE_DIRNAME, context).valid)  # cache unaffected
        self.run_pipeline()
        self.assertEqual(self.metrics()["session_mode"], "warm")
        self.assertIsNotNone(read_run_metrics(self.out / CACHE_DIRNAME))

    def test_deleting_metrics_is_harmless(self):
        self.run_pipeline()
        (self.out / CACHE_DIRNAME / METRICS_FILENAME).unlink()
        self.run_pipeline()
        self.assertEqual(self.metrics()["session_mode"], "warm")
        self.assertEqual(_tree(self.out), self.reference())

    def test_metrics_are_written_atomically(self):
        cache_dir = self.tmp / "cache"
        write_run_metrics(cache_dir, {"contract": "LegacyMapperRunMetrics", "a": 1})
        before = (cache_dir / METRICS_FILENAME).read_bytes()
        with patch("legacy_documenter.utils.atomic_write.os.replace", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                write_run_metrics(cache_dir, {"contract": "LegacyMapperRunMetrics", "a": 2})
        self.assertEqual((cache_dir / METRICS_FILENAME).read_bytes(), before)
        self.assertEqual([p.name for p in cache_dir.iterdir()], [METRICS_FILENAME])

    def test_a_metrics_failure_never_fails_the_run(self):
        with patch.object(run_metrics, "write_run_metrics", side_effect=OSError("disk full")), \
             patch("legacy_documenter.cache.run_report.write_run_metrics", side_effect=OSError("disk full")):
            result = self.run_pipeline()
        self.assertEqual(result.status, RunStatus.SUCCESS)
        self.assertFalse((self.out / CACHE_DIRNAME / METRICS_FILENAME).exists())
        self.assertTrue((self.out / CACHE_DIRNAME / MANIFEST_FILENAME).is_file())

    def test_failed_run_still_reports_without_leaving_a_valid_cache(self):
        self.run_pipeline()
        with patch.object(stages, "render_documentation", side_effect=RuntimeError("boom")):
            result = self.run_pipeline()
        self.assertNotEqual(result.status, RunStatus.SUCCESS)
        self.assertEqual(self.metrics()["final_status"], result.status.value)
        self.assertFalse((self.out / CACHE_DIRNAME / MANIFEST_FILENAME).exists())

    def test_cache_off_writes_no_metrics(self):
        self.run_pipeline(cache_mode="off")
        self.assertFalse((self.out / CACHE_DIRNAME).exists())

    def test_document_holds_no_source_content_or_secrets(self):
        (self.repo / "Bl" / "Secrets.vb").write_text(
            'Public Class Secrets\r\n    Dim cs As String = "Password=TopSecret123"\r\nEnd Class\r\n', encoding="utf-8")
        self.run_pipeline()
        self.run_pipeline()
        raw = (self.out / CACHE_DIRNAME / METRICS_FILENAME).read_text(encoding="utf-8")
        self.assertNotIn("TopSecret123", raw)
        self.assertNotIn("Public Class", raw)
        self.assertNotIn(str(self.repo.resolve()), raw)

    def test_peak_memory_is_a_positive_int_or_none(self):
        peak = run_metrics.peak_memory_bytes()
        self.assertTrue(peak is None or (isinstance(peak, int) and peak > 0))


# =========================== integration ======================================================================
class IntegrationTests(_Case):
    def test_scope_follows_real_changes_and_nothing_is_skipped(self):
        self.run_pipeline()
        target = self.repo / "Sys" / "CustomerRepository.vb"
        target.write_text(target.read_text(encoding="utf-8") + "\r\nPublic Class Another\r\nEnd Class\r\n", encoding="utf-8")
        with patch.object(stages, "resolve_calls", wraps=stages.resolve_calls) as calls, \
             patch.object(stages, "resolve_web_entries", wraps=stages.resolve_web_entries) as web, \
             patch.object(stages, "resolve_database", wraps=stages.resolve_database) as db, \
             patch.object(stages, "resolve_flows", wraps=stages.resolve_flows) as flows, \
             patch.object(stages, "resolve_dependencies", wraps=stages.resolve_dependencies) as deps, \
             patch.object(stages, "export_artifacts", wraps=stages.export_artifacts) as export, \
             patch.object(stages, "build_context_artifacts", wraps=stages.build_context_artifacts) as context, \
             patch.object(stages, "render_documentation", wraps=stages.render_documentation) as docs:
            self.run_pipeline()
        for spy in (calls, web, db, flows, deps, export, context, docs):
            spy.assert_called_once()
        scope = self.metrics()["scope"]
        self.assertEqual((scope["mode"], scope["reach"]), ("full", "global_resolution"))
        self.assertEqual(scope["impacted_projects"]["items"], ["Sys/CustomerRepository.vbproj"])
        self.assertEqual(scope["changed_files"]["modified"]["items"], ["Sys/CustomerRepository.vb"])
        self.assertEqual(scope["symbols_in_changed_files"]["total"], 2)
        self.assertEqual(_tree(self.out), self._reference_for_current())

    def _reference_for_current(self):
        ref = self.tmp / "reference_current"
        run_full_pipeline(self.repo, ref, None, 12, cache_mode="off")
        return _tree(ref)

    def test_config_change_overrides_scope_with_the_contractual_full(self):
        self.run_pipeline()
        self.run_pipeline(excludes=["nonexistent_dir"])
        document = self.metrics()
        self.assertEqual((document["mode"], document["fallback_reason"]), ("full", "ANALYSIS_CONFIG_MISMATCH"))
        self.assertEqual((document["scope"]["mode"], document["scope"]["fallback_reason"]), ("full", "ANALYSIS_CONFIG_MISMATCH"))

    def test_extraction_cache_guardian_and_write_skip_keep_working(self):
        self.run_pipeline()
        self.run_pipeline()
        document = self.metrics()
        self.assertGreater(document["extraction_cache"]["files_reused"], 0)
        self.assertIsNone(document["extraction_cache"]["reuse_disabled_reason"])
        self.assertEqual(document["versions"]["extraction_cache_schema_version"],
                         json.loads((self.out / CACHE_DIRNAME / MANIFEST_FILENAME).read_text(encoding="utf-8"))["versions"]["extraction_cache_schema_version"])
        self.assertEqual(document["write_skip"]["consumer_projection"]["written"], 0)

    def test_metrics_and_scope_are_not_in_the_output_manifest_or_the_product(self):
        self.run_pipeline()
        manifest = build_output_manifest(self.out)
        names = json.dumps(manifest)
        self.assertNotIn("RUN_METRICS", names)
        self.assertNotIn(CACHE_DIRNAME, names)
        evidence = (self.out / "evidence" / "EVIDENCE_MANIFEST.json").read_text(encoding="utf-8")
        self.assertNotIn("scope", evidence)

    def test_run_summary_is_untouched(self):
        self.run_pipeline()
        summary = (self.out / "RUN_SUMMARY.json").read_text(encoding="utf-8")
        self.assertNotIn("scope", summary)
        self.assertNotIn("RUN_METRICS", summary)

    def test_stage_timings_reset_each_run(self):
        self.run_pipeline()
        first = dict(TIMINGS.seconds)
        self.run_pipeline(cache_mode="off")
        self.assertTrue(set(first) <= set(TIMINGS.seconds))
        self.assertNotEqual(first, TIMINGS.seconds)


class RuntimeIndependenceTests(unittest.TestCase):
    def test_new_modules_depend_only_on_runtime_code(self):
        for relative in ("cache/scope.py", "cache/run_metrics.py", "cache/run_report.py", "utils/stage_timings.py"):
            text = (PACKAGE / relative).read_text(encoding="utf-8")
            for forbidden in ("tests", "prompts", "docs/", "legacy_documenter.cli", "legacy_documenter.analysis",
                              "legacy_documenter.extractors", "import subprocess", "import anthropic", "import openai"):
                self.assertNotIn(f"import {forbidden}", text, f"{relative}: {forbidden}")
                self.assertNotIn(f"from {forbidden}", text, f"{relative}: {forbidden}")

    def test_metrics_are_never_read_by_runtime_code(self):
        for path in PACKAGE.rglob("*.py"):
            if path.name in {"run_metrics.py", "__init__.py"}:
                continue
            self.assertNotIn("read_run_metrics", path.read_text(encoding="utf-8"), str(path))

    def test_scope_analysis_never_gates_a_stage(self):
        text = (PACKAGE / "cli" / "full_pipeline.py").read_text(encoding="utf-8")
        self.assertNotIn("analyze_scope", text)
        self.assertNotIn("compute_scope", text)

    def test_analyzed_types_still_equal_the_extractor_map(self):
        # the INVENTORY_ONLY rule relies on this equality (guarded since R2.3)
        from legacy_documenter.fingerprints import ANALYZED_FILE_TYPES
        from legacy_documenter.adapters.python_generic.adapter import PythonGenericAdapter  # V5.9: union of adapters' kinds
        self.assertEqual(set(ANALYZED_FILE_TYPES), set(stages._extractors()) | PythonGenericAdapter.descriptor.source_kinds)

    def test_exports(self):
        for name in ("analyze_scope", "ScopeAnalysisResult", "write_run_metrics", "read_run_metrics"):
            self.assertTrue(hasattr(cache_pkg, name), name)


if __name__ == "__main__":
    unittest.main()
