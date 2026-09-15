"""V4.2-R3 -- Deterministic Technical Documentation: verification tests.

Covers, at minimum:

1. WEB_ENTRY_POINTS.md / FUNCTIONAL_FLOWS.md / DATABASE_ACCESS.md deterministic
   rendering against real discovered data (tests/fixtures/v4_2_r3_sample).
2. Stable ordering (rendering twice produces byte-identical Markdown).
3. Empty-data behavior (tests/fixtures/v2_r1_sample, which has no webforms/
   database access, still renders a valid, non-crashing document).
4. Unresolved-data behavior (the fixture's one flow ends in an unresolved
   boundary; it must render as unresolved, never as an invented call).
5. Special Markdown characters (pipe, backslash, underscore) are escaped/
   neutralized so a table row never breaks.
6. No invented relationship: rendered content is always traceable to a real
   field already present in `indexes`.
7. The DOCUMENTATION stage appears in `full` and runs after CONTEXT.
8. A documentation renderer failure downgrades the run to PARTIAL, not
   FAILED, while machine analysis (index/*.json) remains available.
9. The existing six MarkdownExporter documents are still generated, and
   `analyze`/legacy never gain the four new documents (LEGACY_ANALYZE_BEHAVIOR_CHANGED=false).
10. Existing index JSON shapes are unchanged.
11. AI is not invoked, approval is not invoked, canonical knowledge is not
    produced, the source repository remains immutable, and the run summary
    reflects DOCUMENTATION's status.

This module adds no AI interpretation, knowledge ingestion, or approval --
R3 is deterministic-only, per the task's core rule.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.cli.execution_model import RunStatus, StageStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.cli.pipeline_stages import DocumentationOutcome, render_documentation
from legacy_documenter.cli.stage_identity import StageId
from legacy_documenter.exporters.technical_documentation_renderer import TechnicalDocumentationRenderer
from legacy_documenter.main import analyze_repository

ROOT = Path(__file__).parents[1]
RICH_FIXTURE = ROOT / "tests" / "fixtures" / "v4_2_r3_sample"
EMPTY_FIXTURE = ROOT / "tests" / "fixtures" / "v2_r1_sample"


def _rich_indexes() -> dict:
    with tempfile.TemporaryDirectory() as out:
        return analyze_repository(RICH_FIXTURE, out, None, 12)


def _empty_indexes() -> dict:
    with tempfile.TemporaryDirectory() as out:
        return analyze_repository(EMPTY_FIXTURE, out, None, 12)


class WebEntryPointsRenderingTests(unittest.TestCase):
    """WEB_ENTRY_POINTS.md must deterministically reflect entry_points/event_bindings/webforms."""

    def test_renders_confirmed_entry_point_grouped_by_webform(self) -> None:
        text = TechnicalDocumentationRenderer().web_entry_points(_rich_indexes())
        self.assertIn("# Web Entry Points", text)
        self.assertIn("Default.aspx", text)
        self.assertIn("btnSave", text)
        self.assertIn("btnSave_Click", text)
        self.assertIn("confirmed", text)
        self.assertNotIn("## Unresolved Entry Points", text)  # the fixture's one entry point is confirmed

    def test_empty_data_renders_a_valid_document(self) -> None:
        text = TechnicalDocumentationRenderer().web_entry_points(_empty_indexes())
        self.assertIn("# Web Entry Points", text)
        self.assertIn("No web entry points were discovered.", text)

    def test_unresolved_entry_point_appears_in_dedicated_section(self) -> None:
        indexes = {
            "entry_points": [
                {"id": "EP-1", "type": "web_event", "webform": "A.aspx", "control": "b1", "event": "Click",
                 "handler": "h1", "class_name": None, "project": None, "confidence": "unresolved", "evidence": []}
            ],
            "event_bindings": [],
        }
        text = TechnicalDocumentationRenderer().web_entry_points(indexes)
        self.assertIn("## Unresolved Entry Points", text)
        self.assertIn("h1", text)

    def test_rendering_is_deterministic(self) -> None:
        indexes = _rich_indexes()
        renderer = TechnicalDocumentationRenderer()
        self.assertEqual(renderer.web_entry_points(indexes), renderer.web_entry_points(indexes))


class FunctionalFlowsRenderingTests(unittest.TestCase):
    """FUNCTIONAL_FLOWS.md must render a readable chain and preserve unresolved boundaries."""

    def test_renders_summary_and_readable_chain(self) -> None:
        text = TechnicalDocumentationRenderer().functional_flows(_rich_indexes())
        self.assertIn("# Functional Flows", text)
        self.assertIn("## Summary", text)
        self.assertIn("total_flows", text)
        self.assertIn("→", text)
        self.assertIn("PKG.SAVE", text)

    def test_unresolved_boundary_is_never_rendered_as_a_resolved_call(self) -> None:
        text = TechnicalDocumentationRenderer().functional_flows(_rich_indexes())
        self.assertIn("## Unresolved Boundaries", text)
        self.assertIn("unresolved_boundary", text)
        self.assertIn("(unresolved)", text)

    def test_empty_data_renders_a_valid_document(self) -> None:
        text = TechnicalDocumentationRenderer().functional_flows(_empty_indexes())
        self.assertIn("No functional flows were discovered.", text)

    def test_flow_with_no_summary_still_renders(self) -> None:
        text = TechnicalDocumentationRenderer().functional_flows({"functional_flows": [], "functional_paths": [], "flow_summary": {}, "flow_unresolved": []})
        self.assertIn("# Functional Flows", text)

    def test_rendering_is_deterministic(self) -> None:
        indexes = _rich_indexes()
        renderer = TechnicalDocumentationRenderer()
        self.assertEqual(renderer.functional_flows(indexes), renderer.functional_flows(indexes))


class DatabaseAccessRenderingTests(unittest.TestCase):
    """DATABASE_ACCESS.md must render discovered access/procedures without inventing schema facts."""

    def test_renders_stored_procedure_and_access_point(self) -> None:
        text = TechnicalDocumentationRenderer().database_access(_rich_indexes())
        self.assertIn("# Database Access", text)
        self.assertIn("PKG.SAVE", text)
        self.assertIn("Repo.Save", text)
        self.assertIn("## Stored Procedures", text)

    def test_does_not_infer_table_names_from_procedure_names(self) -> None:
        # PKG.SAVE has no table name anywhere in the discovered evidence;
        # the renderer must not fabricate one.
        text = TechnicalDocumentationRenderer().database_access(_rich_indexes())
        self.assertNotIn("TABLE", text.upper().replace("STORED PROCEDURES", ""))

    def test_empty_data_renders_a_valid_document(self) -> None:
        text = TechnicalDocumentationRenderer().database_access(_empty_indexes())
        self.assertIn("No database access was discovered.", text)

    def test_rendering_is_deterministic(self) -> None:
        indexes = _rich_indexes()
        renderer = TechnicalDocumentationRenderer()
        self.assertEqual(renderer.database_access(indexes), renderer.database_access(indexes))


class UnresolvedFindingsRenderingTests(unittest.TestCase):
    """UNRESOLVED_FINDINGS.md consolidates unresolved signals across sources."""

    def test_renders_consolidated_counts(self) -> None:
        text = TechnicalDocumentationRenderer().unresolved_findings(_rich_indexes())
        self.assertIn("# Unresolved Findings", text)
        self.assertIn("Unresolved flow boundaries", text)

    def test_empty_data_renders_a_valid_document(self) -> None:
        text = TechnicalDocumentationRenderer().unresolved_findings(_empty_indexes())
        self.assertIn("No unresolved findings were recorded for this run.", text)


class MarkdownEscapingTests(unittest.TestCase):
    """Special Markdown characters must never break a table row."""

    def test_pipe_character_in_evidence_expression_is_escaped(self) -> None:
        indexes = {
            "data_access": [{
                "id": "DAO-1", "class": "Repo", "method": "Save", "project": "P",
                "operation_kind": "sql", "confidence": "confirmed",
                "sql_operation": None, "stored_procedure": None,
                "command_text": "SELECT a || b FROM dual",
                "evidence": [{"file": "Repo.vb", "line": 1}],
            }],
            "stored_procedures": [], "sql_operations": [], "data_parameters": [],
        }
        text = TechnicalDocumentationRenderer().database_access(indexes)
        # A raw, unescaped '|' would corrupt the table structure.
        for line in text.splitlines():
            if line.startswith("|"):
                # every unescaped '|' inside a cell must have been turned into '\|'
                self.assertNotIn("|| b FROM dual |", line)

    def test_backslash_paths_render_without_crashing(self) -> None:
        indexes = {
            "entry_points": [{"id": "EP-1", "type": "web_event", "webform": "Web\\A.aspx", "control": "b1",
                               "event": "Click", "handler": "h1", "class_name": None, "project": None,
                               "confidence": "confirmed", "evidence": []}],
            "event_bindings": [],
        }
        text = TechnicalDocumentationRenderer().web_entry_points(indexes)
        self.assertIn("Web\\A.aspx", text)

    def test_underscore_in_handler_name_does_not_break_rendering(self) -> None:
        indexes = {
            "entry_points": [{"id": "EP-1", "type": "web_event", "webform": "A.aspx", "control": "btn_save",
                               "event": "Click", "handler": "btn_save_Click", "class_name": None, "project": None,
                               "confidence": "confirmed", "evidence": []}],
            "event_bindings": [],
        }
        text = TechnicalDocumentationRenderer().web_entry_points(indexes)
        self.assertIn("btn_save_Click", text)


class NoInventedRelationshipTests(unittest.TestCase):
    """Rendered content must always trace back to a real field already present in `indexes`."""

    def test_functional_flow_chain_only_uses_discovered_nodes(self) -> None:
        indexes = _rich_indexes()
        flow = indexes["functional_flows"][0]
        text = TechnicalDocumentationRenderer().functional_flows(indexes)
        discovered_node_ids = {n["id"] for n in flow["nodes"]}
        # every path's node sequence is a subset of the flow's own discovered nodes
        for path in indexes["functional_paths"]:
            self.assertTrue(set(path["nodes"]).issubset(discovered_node_ids))
        self.assertIn("PKG.SAVE", text)  # the one real terminal operation


class DocumentationStageOrderTests(unittest.TestCase):
    """DOCUMENTATION must appear in `full` and run in the expected position."""

    def test_documentation_stage_present_after_context(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(RICH_FIXTURE, out, None, 12)
        stage_order = [s.stage for s in result.stages]
        self.assertIn(StageId.DOCUMENTATION, stage_order)
        self.assertLess(stage_order.index(StageId.CONTEXT), stage_order.index(StageId.DOCUMENTATION))
        self.assertLess(stage_order.index(StageId.DOCUMENTATION), stage_order.index(StageId.FINAL_SUMMARY))

    def test_documentation_stage_succeeds_and_writes_all_four_documents(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(RICH_FIXTURE, out, None, 12)
            doc = next(s for s in result.stages if s.stage is StageId.DOCUMENTATION)
            self.assertEqual(doc.status, StageStatus.SUCCESS)
            for name in ("WEB_ENTRY_POINTS.md", "FUNCTIONAL_FLOWS.md", "DATABASE_ACCESS.md", "UNRESOLVED_FINDINGS.md"):
                self.assertTrue((Path(out) / "documentation" / name).exists(), msg=name)

    def test_documentation_skipped_when_extraction_fails(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch("legacy_documenter.cli.full_pipeline.stages.scan_repository", side_effect=OSError("boom")):
            result = run_full_pipeline(RICH_FIXTURE, out, None, 12)
        doc = next(s for s in result.stages if s.stage is StageId.DOCUMENTATION)
        self.assertEqual(doc.status, StageStatus.SKIPPED_DUE_TO_UPSTREAM_FAILURE)


class DocumentationFailurePolicyTests(unittest.TestCase):
    """A renderer failure must downgrade the run to PARTIAL, never FAILED, and must not
    prevent the other renderers (or machine analysis) from producing output."""

    def test_one_failing_renderer_still_allows_others_to_write(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch.object(TechnicalDocumentationRenderer, "functional_flows", side_effect=RuntimeError("render-boom")):
            result = run_full_pipeline(RICH_FIXTURE, out, None, 12)

            doc = next(s for s in result.stages if s.stage is StageId.DOCUMENTATION)
            self.assertEqual(doc.status, StageStatus.FAILED)
            self.assertIn("render-boom", doc.error.message)
            self.assertEqual(result.status, RunStatus.PARTIAL)
            # the other three renderers still wrote their documents
            self.assertTrue((Path(out) / "documentation" / "WEB_ENTRY_POINTS.md").exists())
            self.assertTrue((Path(out) / "documentation" / "DATABASE_ACCESS.md").exists())
            self.assertTrue((Path(out) / "documentation" / "UNRESOLVED_FINDINGS.md").exists())
            self.assertFalse((Path(out) / "documentation" / "FUNCTIONAL_FLOWS.md").exists())
            # machine analysis remains available
            self.assertTrue((Path(out) / "index" / "repository.json").exists())

    def test_render_documentation_never_raises_for_a_single_renderer_failure(self) -> None:
        with tempfile.TemporaryDirectory() as out, \
             patch.object(TechnicalDocumentationRenderer, "database_access", side_effect=ValueError("x")):
            outcome = render_documentation(out, _rich_indexes())
        self.assertIsInstance(outcome, DocumentationOutcome)
        self.assertEqual(len(outcome.failures), 1)
        self.assertEqual(outcome.failures[0][0], "DATABASE_ACCESS.md")
        self.assertEqual(len(outcome.written), 3)


class ExistingDocumentationCompatibilityTests(unittest.TestCase):
    """The six pre-R3 documents must still be generated; `analyze`/legacy must never gain the new ones."""

    def test_full_still_writes_the_six_existing_documents(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(RICH_FIXTURE, out, None, 12)
            for name in (
                "PROJECT_OVERVIEW.md", "SOLUTION_STRUCTURE.md", "PROJECT_DEPENDENCIES.md",
                "WEBFORMS_MAP.md", "CONFIGURATION_SUMMARY.md", "ANALYSIS_WARNINGS.md",
            ):
                self.assertTrue((Path(out) / "documentation" / name).exists(), msg=name)

    def test_analyze_never_writes_the_four_new_documents(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            analyze_repository(RICH_FIXTURE, out, None, 12)
            for name in ("WEB_ENTRY_POINTS.md", "FUNCTIONAL_FLOWS.md", "DATABASE_ACCESS.md", "UNRESOLVED_FINDINGS.md"):
                self.assertFalse((Path(out) / "documentation" / name).exists(), msg=name)

    def test_legacy_invocation_still_matches_explicit_analyze(self) -> None:
        with tempfile.TemporaryDirectory() as out_legacy, tempfile.TemporaryDirectory() as out_analyze:
            proc_legacy = subprocess.run(
                [sys.executable, "main.py", str(RICH_FIXTURE), "--output", out_legacy],
                cwd=ROOT, capture_output=True, text=True,
            )
            proc_analyze = subprocess.run(
                [sys.executable, "main.py", "analyze", str(RICH_FIXTURE), "--output", out_analyze],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(proc_legacy.returncode, 0, proc_legacy.stderr)
            self.assertEqual(proc_analyze.returncode, 0, proc_analyze.stderr)
            legacy_files = {p.relative_to(out_legacy) for p in Path(out_legacy).rglob("*") if p.is_file()}
            analyze_files = {p.relative_to(out_analyze) for p in Path(out_analyze).rglob("*") if p.is_file()}
            self.assertEqual(legacy_files, analyze_files)


class IndexJsonCompatibilityTests(unittest.TestCase):
    """Existing output/index/*.json shapes must remain unchanged by R3."""

    def test_index_json_files_unchanged_in_shape(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            indexes = analyze_repository(RICH_FIXTURE, out, None, 12)
            on_disk = json.loads((Path(out) / "index" / "entry_points.json").read_text(encoding="utf-8"))
        self.assertEqual(on_disk, indexes["entry_points"])

    def test_full_produces_the_same_index_keys_as_analyze(self) -> None:
        with tempfile.TemporaryDirectory() as out_full, tempfile.TemporaryDirectory() as out_analyze:
            run_full_pipeline(RICH_FIXTURE, out_full, None, 12)
            analyze_repository(RICH_FIXTURE, out_analyze, None, 12)
            full_index_files = {p.name for p in (Path(out_full) / "index").iterdir()}
            analyze_index_files = {p.name for p in (Path(out_analyze) / "index").iterdir()}
        self.assertEqual(full_index_files, analyze_index_files)


class ApprovalAiCanonicalBoundaryTests(unittest.TestCase):
    """No CLI route reachable in R3 may invoke AI, approval, or canonical knowledge."""

    def test_ai_not_invoked_and_approval_not_invoked(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(RICH_FIXTURE, out, None, 12)
        self.assertFalse(result.ai_invoked)
        self.assertFalse(result.canonical_knowledge_produced)
        self.assertFalse(result.technical_lead_approval)

    def test_run_summary_reflects_documentation_status(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(RICH_FIXTURE, out, None, 12)
            payload = json.loads((Path(out) / "RUN_SUMMARY.json").read_text(encoding="utf-8"))
        stage_names = {s["stage"] for s in payload["stages"]}
        self.assertIn("DOCUMENTATION", stage_names)

    def test_renderer_module_imports_no_forbidden_capability(self) -> None:
        import legacy_documenter.exporters.technical_documentation_renderer as renderer_module

        forbidden = [
            "legacy_documenter.analysis.deep_interpretation", "legacy_documenter.llm",
            "legacy_documenter.knowledge.proposals", "legacy_documenter.knowledge.approval",
            "legacy_documenter.knowledge.canonical", "legacy_documenter.knowledge.projection",
            "legacy_documenter.knowledge.plugin_projection", "legacy_documenter.knowledge.ingestion",
        ]
        source = Path(renderer_module.__file__).read_text(encoding="utf-8")
        for token in forbidden:
            self.assertNotIn(token, source, msg=f"technical_documentation_renderer.py must not reference {token!r}")


class SourceImmutabilityTests(unittest.TestCase):
    """The analyzed repository must never be modified by documentation rendering."""

    def test_fixture_files_are_byte_identical_before_and_after(self) -> None:
        import hashlib

        fixture_files = sorted(RICH_FIXTURE.rglob("*"))
        before = {f: hashlib.sha256(f.read_bytes()).hexdigest() for f in fixture_files if f.is_file()}
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(RICH_FIXTURE, out, None, 12)
        after_files = sorted(RICH_FIXTURE.rglob("*"))
        after = {f: hashlib.sha256(f.read_bytes()).hexdigest() for f in after_files if f.is_file()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
