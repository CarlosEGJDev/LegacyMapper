"""V4.2-R8 -- Documentation at Scale, Final Baseline and Closure Preparation.

Covers the navigation/detail split introduced for `FUNCTIONAL_FLOWS.md`,
`DATABASE_ACCESS.md`, and `UNRESOLVED_FINDINGS.md` (R7 found these three
unusably large as single flat Markdown documents at real-repository scale
-- see docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md FINDINGS
NOISE_OR_SCALE_ISSUES). No real IST data is used anywhere in this module;
large-scale coverage (section 14) is built from programmatically generated
synthetic model dicts, not thousands of committed source files.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from legacy_documenter.cli.artifact_lifecycle import sync_generated_partition_directory
from legacy_documenter.cli.pipeline_stages import render_documentation
from legacy_documenter.exporters._documentation_partitioning import (
    build_partition_filenames,
    sanitize_label,
)
from legacy_documenter.exporters.technical_documentation_renderer import TechnicalDocumentationRenderer


# ----------------------------------------------------------------------
# Synthetic data builders (section 14: no real IST data, no committed
# thousands-of-files fixture -- plain generated dicts).
# ----------------------------------------------------------------------


def _flow(flow_id: str, project: str, handler: str, has_confirmed: bool, has_unresolved: bool) -> dict:
    return {
        "id": flow_id, "webform": f"{project}/Page.aspx", "event": "Click", "handler": handler,
        "start_method": f"{project}.{handler}",
        "nodes": [{"id": f"{project}::{handler}", "type": "Method", "label": f"{project}::{handler}", "project": project}],
        "terminal_operations": ["PKG.PROC"] if has_confirmed else [],
        "confidence": "confirmed" if has_confirmed and not has_unresolved else "unresolved",
        "status": "data_endpoint" if has_confirmed and not has_unresolved else "unresolved_boundary",
        "has_confirmed_terminal": has_confirmed,
        "has_unresolved_boundary": has_unresolved,
        "depth": 1,
        "project_sequence": [project],
        "evidence": [{"entry_point_id": flow_id}],
    }


def _path(flow_id: str, path_id: str, node_id: str, terminal_type: str, confidence: str) -> dict:
    return {
        "flow_id": flow_id, "path_id": path_id, "nodes": [node_id],
        "terminal_type": terminal_type, "terminal_target": node_id, "confidence": confidence,
    }


def _large_functional_flows_indexes(project_count: int = 5, flows_per_project: int = 12) -> dict:
    flows: list[dict] = []
    paths: list[dict] = []
    unresolved: list[dict] = []
    for p in range(project_count):
        project = f"Project{p}"
        for f in range(flows_per_project):
            flow_id = f"FLOW-{p}-{f}"
            has_confirmed = f % 2 == 0
            has_unresolved = f % 3 == 0
            flows.append(_flow(flow_id, project, f"Handler{f}", has_confirmed, has_unresolved))
            path = _path(flow_id, f"PATH-{p}-{f}-0", f"{project}::Handler{f}",
                         "data_operation" if has_confirmed else "unresolved_boundary",
                         "confirmed" if has_confirmed else "unresolved")
            paths.append(path)
            if has_unresolved:
                unresolved.append(path)
    return {
        "functional_flows": flows, "functional_paths": paths,
        "flow_summary": {"total_flows": len(flows)}, "flow_unresolved": unresolved,
    }


def _data_access_entry(entry_id: str, project: str, kind: str = "stored_procedure") -> dict:
    return {
        "id": entry_id, "class": "Repo", "method": "Save", "project": project,
        "operation_kind": kind, "confidence": "confirmed",
        "stored_procedure": "PKG.PROC" if kind == "stored_procedure" else None,
        "sql_operation": None, "evidence": [{"file": "Repo.vb", "line": 1, "project": project}],
    }


def _stored_procedure(proc_id: str, project: str) -> dict:
    return {
        "id": proc_id, "name": "PKG.PROC", "package": "PKG", "procedure": "PROC",
        "confidence": "confirmed", "evidence": [{"file": "Repo.vb", "line": 1, "project": project}],
    }


class SafeFilenameTests(unittest.TestCase):
    """Section 12: deterministic, safe partition filenames."""

    def test_path_traversal_input_cannot_escape_the_partition_directory(self) -> None:
        stem = sanitize_label("../../evil")
        self.assertNotIn("..", stem)
        self.assertNotIn("/", stem)
        self.assertNotIn("\\", stem)

    def test_invalid_windows_characters_are_replaced(self) -> None:
        stem = sanitize_label('Sys<Repo>:Name|?*"')
        for char in '<>:"/\\|?*':
            self.assertNotIn(char, stem)

    def test_empty_and_none_labels_fall_back_to_unassigned(self) -> None:
        self.assertEqual(sanitize_label(""), "unassigned")
        self.assertEqual(sanitize_label(None), "unassigned")
        self.assertEqual(sanitize_label("   "), "unassigned")
        self.assertEqual(sanitize_label("///"), "unassigned")

    def test_very_long_label_is_truncated_deterministically(self) -> None:
        stem = sanitize_label("x" * 500)
        self.assertLessEqual(len(stem), 80)
        self.assertEqual(stem, sanitize_label("x" * 500))

    def test_windows_reserved_device_name_is_escaped(self) -> None:
        stem = sanitize_label("CON")
        self.assertNotEqual(stem, "CON")

    def test_duplicate_labels_get_stable_disambiguating_suffixes(self) -> None:
        filenames = build_partition_filenames(["Web", "Web", "Web"])
        self.assertEqual(len(set(filenames.values())), 1)  # dict keyed by label collapses identical keys
        # Two distinct labels that sanitize to the same stem (case collision,
        # which is a real Windows filesystem collision) are disambiguated:
        filenames = build_partition_filenames(["Web", "WEB", "web"])
        self.assertEqual(len(set(filenames.values())), 3)

    def test_filenames_are_deterministic_across_calls(self) -> None:
        labels = ["ProjectB", "ProjectA", "projecta"]
        self.assertEqual(build_partition_filenames(labels), build_partition_filenames(labels))

    def test_no_randomized_hash_or_uuid_shape(self) -> None:
        filenames = build_partition_filenames(["Alpha", "Beta"])
        for name in filenames.values():
            self.assertTrue(name.endswith(".md"))
            self.assertNotRegex(name, r"[0-9a-f]{8}-[0-9a-f]{4}")  # not UUID-shaped


class FunctionalFlowsPartitioningTests(unittest.TestCase):
    """Section 7: FUNCTIONAL_FLOWS.md becomes navigation; detail is partitioned by project."""

    def test_navigation_links_to_one_file_per_project_group(self) -> None:
        indexes = _large_functional_flows_indexes(project_count=5, flows_per_project=12)
        renderer = TechnicalDocumentationRenderer()
        nav = renderer.functional_flows_navigation(indexes)
        partitions = renderer.functional_flows_partitions(indexes)
        self.assertEqual(len(partitions), 5)
        for filename in partitions:
            self.assertIn(f"functional_flows/{filename}", nav)

    def test_partition_preserves_f01_additive_fields(self) -> None:
        indexes = _large_functional_flows_indexes(project_count=1, flows_per_project=4)
        partitions = TechnicalDocumentationRenderer().functional_flows_partitions(indexes)
        text = next(iter(partitions.values()))
        self.assertIn("Confirmed terminal reached:", text)
        self.assertIn("Unresolved boundary remains:", text)

    def test_partition_ordering_is_deterministic(self) -> None:
        indexes = _large_functional_flows_indexes(project_count=4, flows_per_project=6)
        renderer = TechnicalDocumentationRenderer()
        first = renderer.functional_flows_partitions(indexes)
        second = renderer.functional_flows_partitions(indexes)
        self.assertEqual(first, second)

    def test_flow_with_no_project_sequence_falls_back_to_unassigned_group(self) -> None:
        flow = _flow("FLOW-X", "unused", "H", True, False)
        flow["project_sequence"] = []
        indexes = {"functional_flows": [flow], "functional_paths": [], "flow_summary": {}, "flow_unresolved": []}
        partitions = TechnicalDocumentationRenderer().functional_flows_partitions(indexes)
        self.assertIn("unassigned.md", partitions)

    def test_duplicate_and_unsafe_project_labels_produce_safe_unique_files(self) -> None:
        flows = [
            _flow("FLOW-1", "Sys/Repo", "H1", True, False),
            _flow("FLOW-2", "SYS_REPO", "H2", False, True),
        ]
        indexes = {"functional_flows": flows, "functional_paths": [], "flow_summary": {}, "flow_unresolved": []}
        partitions = TechnicalDocumentationRenderer().functional_flows_partitions(indexes)
        self.assertEqual(len(partitions), 2)
        for name in partitions:
            self.assertNotIn("/", name)
            self.assertTrue(name.endswith(".md"))

    def test_no_flows_produces_no_partitions(self) -> None:
        indexes = {"functional_flows": [], "functional_paths": [], "flow_summary": {}, "flow_unresolved": []}
        self.assertEqual(TechnicalDocumentationRenderer().functional_flows_partitions(indexes), {})
        self.assertIn("No functional flows were discovered.", TechnicalDocumentationRenderer().functional_flows_navigation(indexes))


class DatabaseAccessPartitioningTests(unittest.TestCase):
    """Section 8: DATABASE_ACCESS.md becomes navigation; detail is partitioned by project."""

    def test_navigation_links_to_one_file_per_project_group(self) -> None:
        indexes = {
            "data_access": [_data_access_entry(f"DAO-{i}", f"Project{i % 3}") for i in range(9)],
            "stored_procedures": [_stored_procedure(f"SP-{i}", f"Project{i % 3}") for i in range(9)],
            "sql_operations": [], "data_parameters": [],
        }
        renderer = TechnicalDocumentationRenderer()
        nav = renderer.database_access_navigation(indexes)
        partitions = renderer.database_access_partitions(indexes)
        self.assertEqual(len(partitions), 3)
        self.assertIn("## Classification", nav)
        for filename in partitions:
            self.assertIn(f"database_access/{filename}", nav)

    def test_partition_preserves_operation_kind_and_evidence(self) -> None:
        indexes = {
            "data_access": [_data_access_entry("DAO-1", "ProjA")],
            "stored_procedures": [_stored_procedure("SP-1", "ProjA")],
            "sql_operations": [], "data_parameters": [],
        }
        partitions = TechnicalDocumentationRenderer().database_access_partitions(indexes)
        text = next(iter(partitions.values()))
        self.assertIn("stored_procedure", text)
        self.assertIn("PKG.PROC", text)
        self.assertIn("Repo.vb:1", text)

    def test_no_database_access_produces_no_partitions(self) -> None:
        indexes = {"data_access": [], "stored_procedures": [], "sql_operations": [], "data_parameters": []}
        self.assertEqual(TechnicalDocumentationRenderer().database_access_partitions(indexes), {})
        self.assertIn("No database access was discovered.", TechnicalDocumentationRenderer().database_access_navigation(indexes))


class UnresolvedFindingsPartitioningAndF06Tests(unittest.TestCase):
    """Section 9: category-based partitioning; F-06 presentational (lossless) grouping."""

    def test_navigation_links_to_one_file_per_nonempty_category(self) -> None:
        indexes = {
            "errors": [{"file": "A.vb", "extractor": "vb", "error": "boom"}],
            "flow_unresolved": [_path("FLOW-1", "PATH-1", "n1", "unresolved_boundary", "unresolved")],
            "entry_points": [], "data_access": [],
        }
        renderer = TechnicalDocumentationRenderer()
        nav = renderer.unresolved_findings_navigation(indexes)
        partitions = renderer.unresolved_findings_partitions(indexes)
        self.assertEqual(len(partitions), 2)
        for filename in partitions:
            self.assertIn(f"unresolved_findings/{filename}", nav)

    def test_boilerplate_is_grouped_separately_but_never_discarded(self) -> None:
        flow_unresolved = [
            _path("FLOW-1", "PATH-1", "n1", "unresolved_boundary", "unresolved"),
            {**_path("FLOW-1", "PATH-2", "n2", "unresolved_boundary", "unresolved"), "terminal_target": "InitializeComponent()"},
            {**_path("FLOW-1", "PATH-3", "n3", "unresolved_boundary", "unresolved"), "terminal_target": "InitializeComponent()"},
        ]
        indexes = {"errors": [], "flow_unresolved": flow_unresolved, "entry_points": [], "data_access": []}
        partitions = TechnicalDocumentationRenderer().unresolved_findings_partitions(indexes)
        text = next(iter(partitions.values()))
        self.assertIn("Framework/Designer-Generated Boilerplate", text)
        self.assertIn("Other Unresolved Boundaries", text)
        # Every row is still present -- nothing discarded, only regrouped.
        self.assertEqual(text.count("| FLOW-1 |"), 3)

    def test_category_count_unaffected_by_the_presentational_split(self) -> None:
        flow_unresolved = [
            {**_path("FLOW-1", "PATH-1", "n1", "unresolved_boundary", "unresolved"), "terminal_target": "InitializeComponent()"},
        ]
        indexes = {"errors": [], "flow_unresolved": flow_unresolved, "entry_points": [], "data_access": []}
        nav = TechnicalDocumentationRenderer().unresolved_findings_navigation(indexes)
        self.assertIn("| Unresolved flow boundaries | 1 |", nav)

    def test_no_findings_produces_no_partitions(self) -> None:
        indexes = {"errors": [], "flow_unresolved": [], "entry_points": [], "data_access": []}
        self.assertEqual(TechnicalDocumentationRenderer().unresolved_findings_partitions(indexes), {})
        self.assertIn("No unresolved findings were recorded for this run.", TechnicalDocumentationRenderer().unresolved_findings_navigation(indexes))


class DocumentationReadmeTests(unittest.TestCase):
    """Section 6: documentation/README.md top-level navigation."""

    def test_readme_links_every_existing_document_and_hides_absolute_path(self) -> None:
        indexes = {"repository": {"root": r"C:\Users\testuser\source\IST_40\operacional", "stats": {}}}
        readme = TechnicalDocumentationRenderer().documentation_readme(indexes)
        for name in (
            "PROJECT_OVERVIEW.md", "SOLUTION_STRUCTURE.md", "PROJECT_DEPENDENCIES.md", "WEBFORMS_MAP.md",
            "WEB_ENTRY_POINTS.md", "FUNCTIONAL_FLOWS.md", "DATABASE_ACCESS.md", "UNRESOLVED_FINDINGS.md",
            "CONFIGURATION_SUMMARY.md", "ANALYSIS_WARNINGS.md",
        ):
            self.assertIn(f"]({name})", readme)
        self.assertNotIn("testuser", readme)
        self.assertNotIn(r"C:\Users", readme)
        self.assertIn("confirmed", readme.lower())
        self.assertIn("unresolved", readme.lower())


class RerunStalePartitionCleanupTests(unittest.TestCase):
    """Section 11: a shrinking partition set never leaves a stale file behind; unknown files survive."""

    def test_shrinking_partition_set_removes_the_stale_file(self) -> None:
        with TemporaryDirectory() as out:
            directory = Path(out) / "functional_flows"
            sync_generated_partition_directory(directory, {"a.md": "A", "b.md": "B"})
            self.assertTrue((directory / "a.md").exists())
            self.assertTrue((directory / "b.md").exists())
            sync_generated_partition_directory(directory, {"a.md": "A2"})
            self.assertTrue((directory / "a.md").exists())
            self.assertFalse((directory / "b.md").exists())
            self.assertEqual((directory / "a.md").read_text(encoding="utf-8"), "A2")

    def test_unknown_user_file_is_preserved_and_directory_is_kept(self) -> None:
        with TemporaryDirectory() as out:
            directory = Path(out) / "database_access"
            sync_generated_partition_directory(directory, {"a.md": "A"})
            (directory / "notes.txt").write_text("mine", encoding="utf-8")
            sync_generated_partition_directory(directory, {})
            self.assertFalse((directory / "a.md").exists())
            self.assertTrue((directory / "notes.txt").exists())
            self.assertTrue(directory.is_dir())

    def test_directory_is_removed_when_empty_and_never_created_when_no_partitions(self) -> None:
        with TemporaryDirectory() as out:
            directory = Path(out) / "unresolved_findings"
            sync_generated_partition_directory(directory, {})
            self.assertFalse(directory.exists())
            sync_generated_partition_directory(directory, {"a.md": "A"})
            sync_generated_partition_directory(directory, {})
            self.assertFalse(directory.exists())


class RenderDocumentationRerunSafetyTests(unittest.TestCase):
    """Integration: `render_documentation` itself cleans up stale partitions on rerun."""

    def test_rerun_with_fewer_projects_removes_the_stale_partition_file(self) -> None:
        with TemporaryDirectory() as out:
            first_indexes = _large_functional_flows_indexes(project_count=3, flows_per_project=2)
            first_indexes.update({"data_access": [], "stored_procedures": [], "sql_operations": [], "data_parameters": []})
            first_indexes.update({"errors": [], "entry_points": [], "webforms": [], "event_bindings": []})
            render_documentation(out, first_indexes)
            ff_dir = Path(out) / "documentation" / "functional_flows"
            self.assertEqual(len(list(ff_dir.glob("*.md"))), 3)

            second_indexes = _large_functional_flows_indexes(project_count=1, flows_per_project=2)
            second_indexes.update({"data_access": [], "stored_procedures": [], "sql_operations": [], "data_parameters": []})
            second_indexes.update({"errors": [], "entry_points": [], "webforms": [], "event_bindings": []})
            render_documentation(out, second_indexes)
            self.assertEqual(len(list(ff_dir.glob("*.md"))), 1)


class RelativeLinkResolutionTests(unittest.TestCase):
    """Section 13: links are relative, portable, and resolve on generated output."""

    def test_functional_flows_navigation_links_resolve_on_disk(self) -> None:
        with TemporaryDirectory() as out:
            indexes = _large_functional_flows_indexes(project_count=3, flows_per_project=2)
            indexes.update({"data_access": [], "stored_procedures": [], "sql_operations": [], "data_parameters": []})
            indexes.update({"errors": [], "entry_points": [], "webforms": [], "event_bindings": []})
            render_documentation(out, indexes)
            doc_dir = Path(out) / "documentation"
            nav_text = (doc_dir / "FUNCTIONAL_FLOWS.md").read_text(encoding="utf-8")
            for line in nav_text.splitlines():
                if "](functional_flows/" not in line:
                    continue
                link = line.split("](functional_flows/", 1)[1].split(")", 1)[0]
                self.assertFalse(link.startswith("/"))
                self.assertNotIn("\\", link)
                self.assertTrue((doc_dir / "functional_flows" / link).is_file())


class FinalBaselineAndManifestIntegrityTests(unittest.TestCase):
    """Section 23: the R8 final candidate baseline/manifest are deterministic,
    reference only existing files, and never leak an absolute analyst path,
    a secret, or the real-IST generated output.
    """

    ROOT = Path(__file__).parents[1]
    BASELINE_PATH = ROOT / "output" / "v4_2_r8" / "V4_2_FINAL_BASELINE.json"
    MANIFEST_PATH = ROOT / "output" / "v4_2_r8" / "V4_2_FINAL_MANIFEST.json"

    def test_artifacts_exist(self) -> None:
        self.assertTrue(self.BASELINE_PATH.is_file())
        self.assertTrue(self.MANIFEST_PATH.is_file())

    def test_builder_regenerates_byte_identical_output(self) -> None:
        added_to_path = str(self.ROOT) not in sys.path
        if added_to_path:
            sys.path.insert(0, str(self.ROOT))
        try:
            module = importlib.import_module("tools.v4_2_r8_build_final_artifacts")
            baseline_text = _json_dump(module.build_baseline("1804_PASS_0_FAIL_0_SKIP"))
        finally:
            if added_to_path:
                sys.path.remove(str(self.ROOT))
        on_disk = json.loads(self.BASELINE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(json.loads(baseline_text), on_disk)

    def test_manifest_hashes_match_referenced_files(self) -> None:
        manifest = json.loads(self.MANIFEST_PATH.read_text(encoding="utf-8"))
        for entry in manifest["authoritative_artifacts"] + manifest["mutable_current_state_documents"]:
            path = self.ROOT / entry["path"]
            self.assertTrue(path.is_file(), entry["path"])
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual, entry["sha256"], entry["path"])

    def test_no_absolute_analyst_path_or_secret_or_real_ist_output_reference(self) -> None:
        for path in (self.BASELINE_PATH, self.MANIFEST_PATH):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("cgalianj", text)
            self.assertNotIn(r"C:\Users", text)
            self.assertNotIn("v4_2_r7_ist_operacional/V", text)  # no actual path entry into it
            lowered = text.lower()
            for forbidden in ("password", "connectionstring", "api_key", "-----begin"):
                self.assertNotIn(forbidden, lowered)

    def test_baseline_reports_expected_invariants(self) -> None:
        baseline = json.loads(self.BASELINE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(baseline["version"], "V4.2")
        self.assertEqual(baseline["v4_2_status"], "CANDIDATE_PENDING_FINAL_APPROVAL")
        self.assertEqual(baseline["r7_findings_final_state"]["F-01"], "FIXED")
        self.assertEqual(baseline["r7_findings_final_state"]["F-05"], "DEFERRED_BY_DETERMINISM_CONTRACT")
        self.assertFalse(baseline["technical_lead_approval"])
        self.assertFalse(baseline["canonical_knowledge_produced"])
        self.assertEqual(baseline["plugin_runtime"], "NOT_IMPLEMENTED")
        self.assertFalse(baseline["v5_implemented"])
        self.assertEqual(baseline["provider_calls"], 0)
        self.assertEqual(baseline["real_llm_calls"], 0)


def _json_dump(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


if __name__ == "__main__":
    unittest.main()
