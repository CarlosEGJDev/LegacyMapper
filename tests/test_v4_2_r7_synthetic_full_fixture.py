"""V4.2-R7 -- Real IST Pilot and Committable Full Fixture: synthetic fixture tests.

`tests/fixtures/v4_2_r7_full_sample/` is a small, entirely synthetic
.NET/VB.NET/WebForms/Oracle-shaped fixture (no real IST source, class
names, project names, connection strings, or business data) that
exercises the same deterministic V4.2 `full` capabilities validated
against the real IST/Operacional pilot, so a committable regression
example survives without ever committing IST-derived data (section 13).

It also happens to reproduce, in miniature, one of the pilot's concrete
findings: `WebEntryResolver` never attaches `outgoing_calls` to an
entry point bound via ASPX markup (`OnClick="..."`) rather than a
code-behind `Handles` clause, because it looks up the call graph under
the `.aspx` markup file path instead of the actual code-behind `.vb`
file the calls were extracted from (see
`docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md` FINDINGS). This test
module asserts the pipeline's actual current behavior, including that
quirk -- V4.2-R7 forbids production code changes
(`PRODUCTION_CODE_CHANGE_ALLOWED=false`), so no test here may assert an
idealized behavior the code does not actually implement yet.

REAL_AI_RUNTIME_CALL_ALLOWED=false: no test in this module invokes AI at
all (`--allow-ai-interpretation` is never passed) -- it is not required to
exercise this fixture's objective (deterministic capabilities only).
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from legacy_documenter.cli.execution_model import RunStatus, StageStatus
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.cli.stage_identity import StageId
from legacy_documenter.main import analyze_repository

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "v4_2_r7_full_sample"


def _stage(result, stage_id: StageId):
    return next(s for s in result.stages if s.stage is stage_id)


def _load(output: Path, name: str):
    return json.loads((output / "index" / name).read_text(encoding="utf-8"))


class FixtureFullRunTests(unittest.TestCase):
    """`full` against the synthetic fixture must exit SUCCESS with every deterministic stage green."""

    def test_full_run_is_success_with_all_deterministic_stages_succeeding(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertEqual(result.status, RunStatus.SUCCESS)
        for stage_id in (
            StageId.SCAN, StageId.EXTRACTION, StageId.CALL_RESOLUTION, StageId.WEB_ENTRY_RESOLUTION,
            StageId.DATABASE_RESOLUTION, StageId.FLOW_RESOLUTION, StageId.DEPENDENCY_RESOLUTION,
            StageId.EXPORT, StageId.CONTEXT, StageId.DOCUMENTATION, StageId.FINAL_SUMMARY,
        ):
            self.assertEqual(_stage(result, stage_id).status, StageStatus.SUCCESS, stage_id.value)
        # AI is opt-in only and was never requested
        self.assertEqual(_stage(result, StageId.AI_INTERPRETATION).status, StageStatus.NOT_RUN)
        self.assertEqual(_stage(result, StageId.PROPOSAL_GENERATION).status, StageStatus.NOT_RUN)

    def test_no_ai_no_proposals_no_canonical_no_approval(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertFalse(result.ai_requested)
        self.assertFalse(result.ai_invoked)
        self.assertEqual(result.proposal_count, 0)
        self.assertIsNone(result.proposal_review_status)
        self.assertFalse(result.canonical_knowledge_produced)
        self.assertFalse(result.technical_lead_approval)


class SolutionProjectDiscoveryTests(unittest.TestCase):
    def test_solution_and_three_projects_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            solutions = _load(Path(out), "solutions.json")
            projects = _load(Path(out), "projects.json")
        self.assertEqual(len(solutions), 1)
        self.assertEqual(solutions[0]["name"], "SampleLegacy")
        self.assertEqual(
            {p["name"] for p in solutions[0]["projects"]},
            {"Web", "CustomerService", "CustomerRepository"},
        )
        self.assertEqual(len(projects), 3)


class CallAndBlServiceRelationshipTests(unittest.TestCase):
    """UI -> BL -> repository call resolution (Web.CustomerPage -> Bl.CustomerService -> Sys.CustomerRepository)."""

    def test_ui_to_bl_call_is_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            calls = _load(Path(out), "calls.json")
        page_file = next(c for c in calls if c["file"].endswith("CustomerPage.aspx.vb"))
        save_call = next(c for c in page_file["calls"] if c["method_name"] == "Save" and c["containing_method"] == "btnSave_Click")
        self.assertEqual(save_call["confidence"], "confirmed")
        self.assertEqual(save_call["resolved_target"], "SampleLegacy.Bl.CustomerService.save")

    def test_bl_to_repository_call_is_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            calls = _load(Path(out), "calls.json")
        service_file = next(c for c in calls if c["file"].endswith("CustomerService.vb"))
        save_call = next(c for c in service_file["calls"] if c["method_name"] == "Save")
        self.assertEqual(save_call["confidence"], "confirmed")
        self.assertEqual(save_call["resolved_target"], "SampleLegacy.Sys.CustomerRepository.save")

    def test_unresolved_external_call_remains_explicit_never_fabricated(self) -> None:
        # ExternalMailer is not defined anywhere in the fixture -- this call
        # must stay explicitly unresolved, never guessed at.
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            calls = _load(Path(out), "calls.json")
        page_file = next(c for c in calls if c["file"].endswith("CustomerPage.aspx.vb"))
        notify_call = next(c for c in page_file["calls"] if c["method_name"] == "Send")
        self.assertEqual(notify_call["confidence"], "unresolved")
        self.assertIsNone(notify_call["resolved_target"])
        self.assertEqual(notify_call["candidates"], [])


class DatabaseAccessTests(unittest.TestCase):
    """Oracle stored-procedure access discovered in the repository layer."""

    def test_stored_procedure_is_discovered_with_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            data_access = _load(Path(out), "data_access.json")
            stored_procedures = _load(Path(out), "stored_procedures.json")
        self.assertEqual(len(data_access), 1)
        dao = data_access[0]
        self.assertEqual(dao["operation_kind"], "stored_procedure")
        self.assertEqual(dao["stored_procedure"], "PKG_CUSTOMER.SAVE_CUSTOMER")
        self.assertEqual(dao["confidence"], "confirmed")
        self.assertGreaterEqual(dao["evidence_count"], 1)
        self.assertEqual(len(stored_procedures), 1)
        self.assertEqual(stored_procedures[0]["package"], "PKG_CUSTOMER")
        self.assertEqual(stored_procedures[0]["procedure"], "SAVE_CUSTOMER")


class FunctionalFlowTests(unittest.TestCase):
    """One functional flow per entry point, unresolved evidence kept explicit."""

    def test_three_flows_one_per_entry_point(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            flows = _load(Path(out), "functional_flows.json")
        self.assertEqual({f["handler"] for f in flows}, {"Page_Load", "btnSave_Click", "btnNotify_Click"})

    def test_bl_to_database_flow_reaches_the_real_stored_procedure(self) -> None:
        # The UI -> BL -> repository -> Oracle chain is fully traced: the
        # flow's own terminal_operations correctly names the real stored
        # procedure, with a confirmed edge at every hop.
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            flows = _load(Path(out), "functional_flows.json")
        flow = next(f for f in flows if f["handler"] == "btnSave_Click")
        self.assertEqual(flow["terminal_operations"], ["PKG_CUSTOMER.SAVE_CUSTOMER"])
        confirmed_edges = [e for e in flow["edges"] if e["confidence"] == "confirmed"]
        self.assertGreaterEqual(len(confirmed_edges), 4)

    def test_bl_to_database_flow_status_still_downgrades_but_now_says_so_explicitly(self) -> None:
        # V4.2-R7.1 F-01 correction: this flow's own `cmd.ExecuteNonQuery()`
        # call is unresolved, so the pre-existing `status`/`confidence`
        # fields still (correctly, and unchanged) downgrade to
        # unresolved_boundary/unresolved -- this is NOT hidden or forced to a
        # false SUCCESS. What changes is that the flow now ALSO carries an
        # additive, independent fact: it reached a real, confirmed database
        # terminal despite that downgrade, distinguishing it from a flow that
        # genuinely resolved nothing (see btnNotify_Click below).
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            flows = _load(Path(out), "functional_flows.json")
        flow = next(f for f in flows if f["handler"] == "btnSave_Click")
        self.assertEqual(flow["status"], "unresolved_boundary")
        self.assertEqual(flow["confidence"], "unresolved")
        self.assertTrue(flow["has_confirmed_terminal"])
        self.assertTrue(flow["has_unresolved_boundary"])

    def test_unresolved_finding_remains_explicit_not_guessed(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            flows = _load(Path(out), "functional_flows.json")
        flow = next(f for f in flows if f["handler"] == "btnNotify_Click")
        self.assertEqual(flow["status"], "unresolved_boundary")
        self.assertEqual(flow["confidence"], "unresolved")
        # Unlike btnSave_Click (F-01 correction, above), this flow genuinely
        # reached no confirmed database terminal at all.
        self.assertFalse(flow["has_confirmed_terminal"])
        self.assertTrue(flow["has_unresolved_boundary"])

    def test_markup_bound_handler_reproduces_the_known_outgoing_calls_gap(self) -> None:
        # Documents the pilot finding precisely, as current (unfixed)
        # behavior: `btnSave`/`btnNotify` are bound via ASPX markup
        # (`OnClick="..."`), and `WebEntryResolver` never attaches
        # `outgoing_calls` for a markup-bound handler (it looks the call
        # graph up under the .aspx path, not the code-behind .vb path the
        # calls were actually extracted from) -- see
        # docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md FINDINGS.
        # `calls.json`/`functional_flows.json` still resolve the chain
        # correctly (see the tests above); only the entry point's own
        # embedded `outgoing_calls` list is affected.
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            entry_points = _load(Path(out), "entry_points.json")
        btn_save = next(e for e in entry_points if e["handler"] == "btnSave_Click")
        self.assertEqual(btn_save["outgoing_calls"], [])
        # Page_Load is bound via a code-behind `Handles Me.Load` clause,
        # not markup -- its outgoing_calls ARE attached correctly.
        page_load = next(e for e in entry_points if e["handler"] == "Page_Load")
        self.assertEqual(len(page_load["outgoing_calls"]), 1)


class GeneratedDocumentationTests(unittest.TestCase):
    def test_technical_documentation_package_is_generated(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
            doc_dir = Path(out) / "documentation"
            for name in (
                "PROJECT_OVERVIEW.md", "SOLUTION_STRUCTURE.md", "PROJECT_DEPENDENCIES.md",
                "WEBFORMS_MAP.md", "CONFIGURATION_SUMMARY.md", "ANALYSIS_WARNINGS.md",
                "WEB_ENTRY_POINTS.md", "FUNCTIONAL_FLOWS.md", "DATABASE_ACCESS.md",
                "UNRESOLVED_FINDINGS.md",
            ):
                self.assertTrue((doc_dir / name).is_file(), name)
            db_doc = (doc_dir / "DATABASE_ACCESS.md").read_text(encoding="utf-8")
            self.assertIn("PKG_CUSTOMER.SAVE_CUSTOMER", db_doc)
            unresolved_doc = (doc_dir / "UNRESOLVED_FINDINGS.md").read_text(encoding="utf-8")
            self.assertIn("Unresolved flow boundaries", unresolved_doc)


class SourceImmutabilityAndRerunTests(unittest.TestCase):
    def test_fixture_files_are_byte_identical_before_and_after(self) -> None:
        fixture_files = sorted(FIXTURE.rglob("*"))
        before = {p: p.read_bytes() for p in fixture_files if p.is_file()}
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12)
        after = {p: p.read_bytes() for p in fixture_files if p.is_file()}
        self.assertEqual(before, after)

    def test_rerun_into_the_same_output_remains_safe(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            first = run_full_pipeline(FIXTURE, out, None, 12)
            second = run_full_pipeline(FIXTURE, out, None, 12)
        self.assertEqual(first.status, RunStatus.SUCCESS)
        self.assertEqual(second.status, RunStatus.SUCCESS)

    def test_legacy_analyze_path_also_succeeds_on_the_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            indexes = analyze_repository(FIXTURE, out, None, 12)
        self.assertEqual(indexes["errors"], [])
        self.assertEqual(len(indexes["solutions"]), 1)
        self.assertEqual(len(indexes["projects"]), 3)


if __name__ == "__main__":
    unittest.main()
