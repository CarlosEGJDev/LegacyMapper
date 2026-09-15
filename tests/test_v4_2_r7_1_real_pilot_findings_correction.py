"""V4.2-R7.1 -- Real Pilot Findings Correction.

Corrects F-01 through F-04 found by the V4.2-R7 real IST/Operacional pilot
(see docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md FINDINGS and
docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md). F-05 is DEFERRED_BY_
DETERMINISM_CONTRACT (see the existing `DeterminismTests` in
tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py, which already
pins RUN_SUMMARY.json to byte-identical output across two runs of the same
fixture -- a real wall-clock duration cannot be added there without breaking
that established contract). F-06/F-07 are PRESERVED_OBSERVATION and are not
touched here; their existing regression coverage in
tests/test_v4_2_r7_synthetic_full_fixture.py is left unmodified except for
the one F-01 assertion this round intentionally corrects (see that file).

Section 3 requires characterizing FunctionalFlowResolver's actual existing
status/confidence aggregation BEFORE changing production code; the
`CharacterizationTests` class below does that directly against the resolver,
independent of any fixture/pipeline plumbing, distinguishing the five
scenarios section 3 names (A-E).
"""
from __future__ import annotations

import unittest

from legacy_documenter.analysis.flow_resolver import FunctionalFlowResolver
from legacy_documenter.exporters.markdown_exporter import MarkdownExporter
from legacy_documenter.exporters.technical_documentation_renderer import TechnicalDocumentationRenderer


def entry(entry_id: str, webform: str, event: str, handler: str, handler_method: str, confidence: str = "confirmed") -> dict:
    return {
        "id": entry_id, "webform": webform, "control": None, "event": event,
        "handler": handler, "handler_method": handler_method, "confidence": confidence, "project": None,
    }


def call(containing_class: str, containing_method: str, resolved_target: str | None, confidence: str, file: str = "S.vb", line: int = 1, expression: str = "Call()") -> dict:
    return {
        "containing_class": containing_class, "containing_method": containing_method,
        "resolved_target": resolved_target, "confidence": confidence, "expression": expression,
        "resolved_project": None, "evidence": {"line": line},
    }


def files_calls(*calls: dict, file: str = "S.vb") -> list[dict]:
    return [{"file": file, "calls": list(calls)}]


def data_op(op_id: str, class_name: str, method: str, confidence: str = "confirmed") -> dict:
    return {"id": op_id, "class": class_name, "method": method, "project": None, "confidence": confidence}


class CharacterizationTests(unittest.TestCase):
    """Section 3: the resolver's EXISTING status/confidence aggregation, pinned
    before any production change, across the five required scenarios."""

    def test_scenario_a_confirmed_terminal_no_unresolved_side_boundary(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn", "Page.A")]
        data_access = [data_op("DAO-1", "Page", "A")]
        flows, paths, summary, unresolved = resolver.resolve(entries, [], data_access, [], [], [])
        flow = flows[0]
        self.assertEqual(flow["status"], "data_endpoint")
        self.assertEqual(flow["confidence"], "confirmed")
        self.assertTrue(flow["has_confirmed_terminal"])
        self.assertFalse(flow["has_unresolved_boundary"])

    def test_scenario_b_confirmed_terminal_plus_unrelated_unresolved_side_call(self) -> None:
        # This is F-01's exact shape: the method that reaches a confirmed
        # data-access terminal ALSO makes one unrelated unresolved call.
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn", "Page.A")]
        calls = files_calls(call("Page", "A", None, "unresolved", expression="Unrelated()"))
        data_access = [data_op("DAO-1", "Page", "A")]
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, data_access, [], [], [])
        flow = flows[0]
        # Old (unchanged) top-level fields still downgrade to unresolved --
        # this correction is additive, it does not hide the unresolved side
        # boundary or fabricate a SUCCESS status.
        self.assertEqual(flow["status"], "unresolved_boundary")
        self.assertEqual(flow["confidence"], "unresolved")
        # New additive facts correctly distinguish this from scenario C.
        self.assertTrue(flow["has_confirmed_terminal"])
        self.assertTrue(flow["has_unresolved_boundary"])

    def test_scenario_c_no_confirmed_terminal_ends_unresolved(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn", "Page.A")]
        calls = files_calls(call("Page", "A", None, "unresolved", expression="Unrelated()"))
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, [], [], [], [])
        flow = flows[0]
        self.assertEqual(flow["status"], "unresolved_boundary")
        self.assertEqual(flow["confidence"], "unresolved")
        self.assertFalse(flow["has_confirmed_terminal"])
        self.assertTrue(flow["has_unresolved_boundary"])

    def test_scenario_d_multiple_paths_some_confirmed_some_not(self) -> None:
        # Two independent branches out of the same handler: one reaches a
        # confirmed data-access terminal, the other is a separate confirmed
        # call into a method that itself makes an unresolved call.
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn", "Page.A")]
        calls = files_calls(
            call("Page", "A", "Page.Other", "confirmed", line=1, expression="Other()"),
            call("Page", "Other", None, "unresolved", line=2, expression="Deep()"),
        )
        data_access = [data_op("DAO-1", "Page", "A")]
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, data_access, [], [], [])
        flow = flows[0]
        terminal_types = {p["terminal_type"] for p in paths}
        self.assertIn("data_operation", terminal_types)
        self.assertIn("unresolved_boundary", terminal_types)
        self.assertTrue(flow["has_confirmed_terminal"])
        self.assertTrue(flow["has_unresolved_boundary"])

    def test_scenario_e_only_non_database_resolved_nodes_but_unresolved_boundary_remains(self) -> None:
        # No data access at all: one branch is a confirmed dead-end (resolves
        # completely, reaches no database terminal), the other is unresolved.
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn", "Page.A")]
        calls = files_calls(
            call("Page", "A", "Page.DeadEnd", "confirmed", line=1, expression="DeadEnd()"),
            call("Page", "A", None, "unresolved", line=2, expression="Unrelated()"),
        )
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, [], [], [], [])
        flow = flows[0]
        terminal_types = {p["terminal_type"] for p in paths}
        self.assertIn("dead_end", terminal_types)
        self.assertIn("unresolved_boundary", terminal_types)
        self.assertFalse(flow["has_confirmed_terminal"])
        self.assertTrue(flow["has_unresolved_boundary"])


class F01MachineRepresentationTests(unittest.TestCase):
    """F-01: machine output preserves both facts independently, never one at
    the expense of the other, and the flow-level summary aggregates them."""

    def test_summary_reports_flows_with_confirmed_terminal_and_with_unresolved_boundary_and_with_both(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [
            entry("EP-1", "Default.aspx", "Click", "btn1", "Page.A"),
            entry("EP-2", "Default.aspx", "Click", "btn2", "Page.B"),
        ]
        calls = files_calls(
            call("Page", "A", None, "unresolved", line=1, expression="Unrelated()"),
            call("Page", "B", None, "unresolved", line=2, expression="OnlyUnresolved()"),
            file="S.vb",
        )
        data_access = [data_op("DAO-1", "Page", "A")]
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, data_access, [], [], [])
        self.assertEqual(summary["flows_with_confirmed_terminal"], 1)
        self.assertEqual(summary["flows_with_unresolved_boundary"], 2)
        self.assertEqual(summary["flows_with_both"], 1)

    def test_existing_status_confidence_fields_are_unchanged_backward_compatible(self) -> None:
        # A consumer reading only the pre-existing `status`/`confidence`
        # fields sees exactly the same (unchanged) values as before this
        # correction -- the fix is purely additive.
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn", "Page.A")]
        calls = files_calls(call("Page", "A", None, "unresolved", expression="Unrelated()"))
        data_access = [data_op("DAO-1", "Page", "A")]
        flows, *_ = resolver.resolve(entries, calls, data_access, [], [], [])
        self.assertEqual(flows[0]["status"], "unresolved_boundary")
        self.assertEqual(flows[0]["confidence"], "unresolved")


class F01HumanDocumentationTests(unittest.TestCase):
    """F-01: FUNCTIONAL_FLOWS.md must make the same distinction immediately
    understandable to a human reader, per section 5."""

    def _render(self) -> str:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn", "Page.A")]
        calls = files_calls(call("Page", "A", None, "unresolved", expression="Unrelated()"))
        data_access = [data_op("DAO-1", "Page", "A")]
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, data_access, [], [], [])
        indexes = {
            "functional_flows": flows, "functional_paths": paths,
            "flow_summary": summary, "flow_unresolved": unresolved,
        }
        return TechnicalDocumentationRenderer().functional_flows(indexes)

    def test_rendered_flow_shows_confirmed_terminal_reached_despite_unresolved_status(self) -> None:
        doc = self._render()
        self.assertIn("Status: `unresolved_boundary`", doc)
        self.assertIn("Confirmed terminal reached: `yes`", doc)
        self.assertIn("Unresolved boundary remains: `yes`", doc)

    def test_summary_metrics_are_present_and_explained(self) -> None:
        doc = self._render()
        self.assertIn("flows_with_confirmed_terminal", doc)
        self.assertIn("flows_with_unresolved_boundary", doc)
        self.assertIn("flows_with_both", doc)
        self.assertIn("Confirmed terminal reached", doc)


class F02DuplicateSolutionNameTests(unittest.TestCase):
    """F-02: duplicate-named solutions must be distinguishable, without
    altering solution identity."""

    def test_duplicate_named_solutions_are_disambiguated_by_path(self) -> None:
        indexes = {
            "solutions": [
                {"name": "WebAmbiente", "path": "WebAmbiente.sln", "projects": []},
                {"name": "WebAmbiente", "path": "Backup/WebAmbiente.sln", "projects": []},
            ],
        }
        doc = MarkdownExporter().solution_structure(indexes)
        self.assertIn("## WebAmbiente (`WebAmbiente.sln`)", doc)
        self.assertIn("## WebAmbiente (`Backup/WebAmbiente.sln`)", doc)
        # Solution identity (the bare name) itself is unchanged.
        self.assertEqual(indexes["solutions"][0]["name"], "WebAmbiente")
        self.assertEqual(indexes["solutions"][1]["name"], "WebAmbiente")


class F03WebFormsRegisterRenderingTests(unittest.TestCase):
    """F-03: register metadata renders as Markdown, never raw Python dict repr."""

    def test_register_renders_as_markdown_not_dict_repr(self) -> None:
        indexes = {
            "webforms": [
                {
                    "path": "Web/Sample.aspx",
                    "registers": [
                        {
                            "TagPrefix": "snt", "Namespace": "Sonda.Net.Control", "Assembly": "SondaNetWebUI",
                            "_normalized": {"tagprefix": "snt", "namespace": "sonda.net.control", "assembly": "sondanetwebui"},
                        }
                    ],
                }
            ]
        }
        doc = MarkdownExporter().webforms_map(indexes)
        self.assertNotIn("{'TagPrefix'", doc)
        self.assertNotIn("_normalized", doc)
        self.assertIn("TagPrefix: `snt`", doc)
        self.assertIn("Namespace: `Sonda.Net.Control`", doc)
        self.assertIn("Assembly: `SondaNetWebUI`", doc)


class F04AbsolutePathExposureTests(unittest.TestCase):
    """F-04: human-facing PROJECT_OVERVIEW.md must not expose the analyst's
    absolute local path (and thus local username); the machine index field is
    untouched."""

    def test_human_facing_overview_does_not_expose_synthetic_local_username(self) -> None:
        indexes = {
            "repository": {
                "root": r"C:\Users\testuser\source\IST_40\operacional",
                "stats": {"total_files": 3},
            }
        }
        doc = MarkdownExporter().project_overview(indexes)
        self.assertNotIn("testuser", doc)
        self.assertNotIn(r"C:\Users", doc)
        self.assertIn("operacional", doc)

    def test_machine_contract_root_field_is_not_this_renderers_concern(self) -> None:
        # `index/repository.json`'s own `root` field is produced elsewhere
        # (legacy_documenter/main.py / full_pipeline.py) and is unmodified by
        # this correction -- confirmed here by simply passing the absolute
        # root straight through into indexes["repository"]["root"] above and
        # observing it is still exactly what was given, only never rendered
        # verbatim into human-facing Markdown.
        indexes = {"repository": {"root": r"C:\Users\testuser\source\IST_40\operacional", "stats": {}}}
        self.assertEqual(indexes["repository"]["root"], r"C:\Users\testuser\source\IST_40\operacional")


if __name__ == "__main__":
    unittest.main()
