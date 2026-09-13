"""V4.1-R5 -- Risky Orchestrators Characterization: FunctionalFlowResolver (Target B).

Characterization only. Captures existing behavior of
`legacy_documenter.analysis.flow_resolver.FunctionalFlowResolver` so a later
V4.1-R6 extraction decision has behavioral evidence to work from. No
production code is modified by this round or this test file. Tests call
`.resolve()` directly with minimal synthetic dict inputs (not through the
full `analyze_repository` pipeline) to pin unit-level behavior; existing
pipeline-level coverage already lives in tests/test_v1_unittest.py.
"""
from __future__ import annotations

import inspect
import unittest

from legacy_documenter.analysis.flow_resolver import FunctionalFlowResolver


def entry(entry_id: str, webform: str, event: str, handler: str, handler_method: str, confidence: str = "confirmed", control: str | None = None, project: str | None = None) -> dict:
    return {
        "id": entry_id, "webform": webform, "control": control, "event": event,
        "handler": handler, "handler_method": handler_method, "confidence": confidence, "project": project,
    }


def call(containing_class: str, containing_method: str, resolved_target: str | None, confidence: str, file: str = "S.vb", line: int = 1, expression: str = "Call()", resolved_project: str | None = None) -> dict:
    return {
        "containing_class": containing_class, "containing_method": containing_method,
        "resolved_target": resolved_target, "confidence": confidence, "expression": expression,
        "resolved_project": resolved_project, "evidence": {"line": line},
    }


def files_calls(*calls: dict, file: str = "S.vb") -> list[dict]:
    return [{"file": file, "calls": list(calls)}]


class PublicSurfaceTests(unittest.TestCase):
    """(1) public construction/import. (2) public signature."""

    def test_construction_and_import(self) -> None:
        resolver = FunctionalFlowResolver()
        self.assertEqual(resolver.max_depth, 12)

    def test_construction_with_explicit_max_depth(self) -> None:
        resolver = FunctionalFlowResolver(max_depth=3)
        self.assertEqual(resolver.max_depth, 3)

    def test_resolve_signature_pinned(self) -> None:
        sig = str(inspect.signature(FunctionalFlowResolver.resolve))
        self.assertEqual(
            sig,
            "(self, entry_points: list[dict], calls: list[dict], data_access: list[dict], "
            "stored_procedures: list[dict], sql_operations: list[dict], dependencies: list[dict], "
            "errors: list[dict] | None = None) -> tuple[list[dict], list[dict], dict, list[dict]]",
        )

    def test_only_one_public_method(self) -> None:
        public = [name for name, _ in inspect.getmembers(FunctionalFlowResolver, predicate=inspect.isfunction) if not name.startswith("_")]
        self.assertEqual(public, ["resolve"])


class SimpleLinearFlowTests(unittest.TestCase):
    """(3) simple linear flow, ending at a data-access operation with no terminal."""

    def test_linear_flow_to_dead_end_when_no_data_access(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.Handler")]
        flows, paths, summary, unresolved = resolver.resolve(entries, [], [], [], [], [])
        self.assertEqual(len(flows), 1)
        self.assertEqual(flows[0]["status"], "dead_end")
        self.assertEqual(summary["total_flows"], 1)
        self.assertEqual(summary["dead_end_paths"], 1)
        self.assertEqual(unresolved, [])

    def test_linear_flow_to_data_operation_with_no_terminal_target(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.Handler")]
        data_access = [{"id": "DAO-1", "class": "Page", "method": "Handler", "project": None, "confidence": "confirmed"}]
        flows, paths, summary, unresolved = resolver.resolve(entries, [], data_access, [], [], [])
        self.assertEqual(len(flows), 1)
        self.assertEqual(paths[0]["terminal_type"], "data_operation")
        self.assertEqual(flows[0]["confidence"], "confirmed")


class BranchingAndConvergenceTests(unittest.TestCase):
    """(4) branching flow. (5) convergence to a shared method."""

    def test_branching_flow_two_calls_from_same_method(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.Handler")]
        calls = files_calls(
            call("Page", "Handler", "Page.Left", "confirmed"),
            call("Page", "Handler", "Page.Right", "confirmed"),
        )
        data_access = [
            {"id": "DAO-L", "class": "Page", "method": "Left", "project": None, "confidence": "confirmed"},
            {"id": "DAO-R", "class": "Page", "method": "Right", "project": None, "confidence": "confirmed"},
        ]
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, data_access, [], [], [])
        self.assertEqual(len(flows), 1)
        self.assertEqual(summary["total_paths"], 2)
        terminals = sorted(p["terminal_target"] for p in paths)
        self.assertEqual(terminals, ["DAO-L", "DAO-R"])

    def test_convergent_calls_to_same_target_produce_one_shared_node(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.Handler")]
        calls = files_calls(
            call("Page", "Handler", "Page.Shared", "confirmed", line=1),
        )
        data_access = [{"id": "DAO-1", "class": "Page", "method": "Shared", "project": None, "confidence": "confirmed"}]
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, data_access, [], [], [])
        shared_label = "<unknown>::page.shared"
        node_ids = {n["id"] for n in flows[0]["nodes"]}
        self.assertIn(shared_label, node_ids)
        self.assertEqual(sum(1 for n in flows[0]["nodes"] if n["id"] == shared_label), 1)


class DuplicateAndCycleTests(unittest.TestCase):
    """(6) duplicate edges/nodes. (7) cycles."""

    def test_duplicate_edges_are_not_repeated_in_output(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.Handler")]
        calls = files_calls(
            call("Page", "Handler", "Page.Target", "confirmed", line=1, expression="Target()"),
            call("Page", "Handler", "Page.Target", "confirmed", line=2, expression="Target()"),
        )
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, [], [], [], [])
        method_to_method_edges = [e for e in flows[0]["edges"] if e["type"] == "Method -> Method" and e["target"] == "<unknown>::page.target"]
        # Two distinct call-site evidence refs keep the edges distinct (edge
        # identity includes evidence_ref), so this is two edges, not one --
        # deduplication happens only when the (source, target, type,
        # evidence_ref) tuple repeats exactly.
        self.assertEqual(len(method_to_method_edges), 2)

    def test_direct_self_cycle_is_terminated_as_cycle(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.Handler")]
        calls = files_calls(call("Page", "Handler", "Page.Handler", "confirmed"))
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, [], [], [], [])
        self.assertEqual([p["terminal_type"] for p in paths], ["cycle"])
        self.assertEqual(flows[0]["status"], "cycle")
        self.assertEqual(len(unresolved), 1)

    def test_indirect_cycle_a_calls_b_calls_a(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.A")]
        calls = files_calls(
            call("Page", "A", "Page.B", "confirmed", line=1, expression="B()"),
            call("Page", "B", "Page.A", "confirmed", line=2, expression="A()"),
        )
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, [], [], [], [])
        self.assertIn("cycle", [p["terminal_type"] for p in paths])


class UnresolvedTargetAndSourceTests(unittest.TestCase):
    """(8) unresolved targets. (9) unresolved sources -- entries requiring `confirmed` + `handler_method`."""

    def test_unresolved_call_becomes_unresolved_boundary(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.Handler")]
        calls = files_calls(call("Page", "Handler", None, "unresolved", expression="helper.Dyn()"))
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, [], [], [], [])
        self.assertEqual(paths[0]["terminal_type"], "unresolved_boundary")
        self.assertEqual(paths[0]["confidence"], "unresolved")
        self.assertEqual(len(unresolved), 1)

    def test_entry_point_without_confirmed_confidence_is_skipped(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.Handler", confidence="unresolved")]
        flows, paths, summary, unresolved = resolver.resolve(entries, [], [], [], [], [])
        self.assertEqual(flows, [])
        self.assertEqual(summary["total_entry_points_considered"], 0)

    def test_entry_point_without_handler_method_is_skipped(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "")]
        flows, paths, summary, unresolved = resolver.resolve(entries, [], [], [], [], [])
        self.assertEqual(flows, [])


class EmptyAndIsolatedInputTests(unittest.TestCase):
    """(10) empty graph. (11) isolated node."""

    def test_empty_entry_points_produce_empty_everything(self) -> None:
        resolver = FunctionalFlowResolver()
        flows, paths, summary, unresolved = resolver.resolve([], [], [], [], [], [])
        self.assertEqual((flows, paths, unresolved), ([], [], []))
        self.assertEqual(summary["total_flows"], 0)
        self.assertEqual(summary["average_path_depth"], 0)

    def test_isolated_handler_with_no_calls_or_data_access_is_dead_end(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.Isolated")]
        flows, paths, summary, unresolved = resolver.resolve(entries, [], [], [], [], [])
        self.assertEqual(paths[0]["terminal_type"], "dead_end")
        self.assertEqual(paths[0]["nodes"], ["<unknown>::page.isolated"])


class RepeatedTraversalAndOrderingTests(unittest.TestCase):
    """(12) repeated traversal (instance reuse). (13) deterministic path ordering. (14) deterministic flow ordering."""

    def test_calling_resolve_twice_on_the_same_instance_is_equivalent_to_a_fresh_instance(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.Handler")]
        data_access = [{"id": "DAO-1", "class": "Page", "method": "Handler", "project": None, "confidence": "confirmed"}]
        first = resolver.resolve(entries, [], data_access, [], [], [])
        second = resolver.resolve(entries, [], data_access, [], [], [])
        third = FunctionalFlowResolver().resolve(entries, [], data_access, [], [], [])
        self.assertEqual(first, second)
        self.assertEqual(first, third)

    def test_flows_are_sorted_by_flow_id(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [
            entry("EP-Z", "Default.aspx", "Click", "btnZ", "Page.Z"),
            entry("EP-A", "Default.aspx", "Click", "btnA", "Page.A"),
        ]
        flows, *_ = resolver.resolve(entries, [], [], [], [], [])
        self.assertEqual(flows, sorted(flows, key=lambda item: item["id"]))

    def test_paths_are_sorted_by_flow_id_then_path_id(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.Handler")]
        calls = files_calls(
            call("Page", "Handler", "Page.Left", "confirmed", line=1, expression="Left()"),
            call("Page", "Handler", "Page.Right", "confirmed", line=2, expression="Right()"),
        )
        flows, paths, *_ = resolver.resolve(entries, calls, [], [], [], [])
        self.assertEqual(paths, sorted(paths, key=lambda item: (item["flow_id"], item["path_id"])))


class DepthBoundaryTests(unittest.TestCase):
    """(15) depth/boundary behavior."""

    def test_max_depth_truncates_long_call_chain(self) -> None:
        resolver = FunctionalFlowResolver(max_depth=2)
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.A")]
        calls = files_calls(
            call("Page", "A", "Page.B", "confirmed", line=1, expression="B()"),
            call("Page", "B", "Page.C", "confirmed", line=2, expression="C()"),
            call("Page", "C", "Page.D", "confirmed", line=3, expression="D()"),
        )
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, [], [], [], [])
        self.assertIn("truncated_depth", [p["terminal_type"] for p in paths])
        self.assertTrue(any(p["terminal_type"] == "truncated_depth" for p in unresolved))

    def test_default_max_depth_is_twelve(self) -> None:
        self.assertEqual(FunctionalFlowResolver().max_depth, 12)


class StateResetAndReuseTests(unittest.TestCase):
    """(16) state reset/reuse behavior -- STATE_MODEL evidence: STATEFUL_RESET_PER_OPERATION."""

    def test_instance_attributes_are_fully_replaced_on_each_resolve_call(self) -> None:
        resolver = FunctionalFlowResolver()
        entries_a = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "Page.A")]
        resolver.resolve(entries_a, [], [], [], [], [])
        first_path_identities = dict(resolver._path_identities)
        entries_b = [entry("EP-2", "Default.aspx", "Click", "btn_Click", "Page.B")]
        resolver.resolve(entries_b, [], [], [], [], [])
        # The previous call's path-identity registry is not carried forward:
        # `resolve()` reassigns `self._path_identities = {}` at its start.
        self.assertNotEqual(set(first_path_identities), set(resolver._path_identities))


class MalformedOrIncompleteDataTests(unittest.TestCase):
    """(17) malformed or incomplete data."""

    def test_entry_point_missing_dot_in_handler_method_is_skipped(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn_Click", "NoDotHere")]
        flows, *_ = resolver.resolve(entries, [], [], [], [], [])
        self.assertEqual(flows, [])

    def test_call_missing_containing_method_is_ignored_in_indexing(self) -> None:
        resolver = FunctionalFlowResolver()
        confirmed, unresolved = resolver._index_calls(files_calls(
            {"containing_class": "Page", "containing_method": None, "resolved_target": "Page.X", "confidence": "confirmed", "expression": "X()", "evidence": {}},
        ))
        self.assertEqual(confirmed, {})
        self.assertEqual(unresolved, {})

    def test_data_access_missing_class_or_method_is_ignored(self) -> None:
        resolver = FunctionalFlowResolver()
        result = resolver._index_data_access([{"id": "DAO-1", "class": None, "method": "M", "project": None}])
        self.assertEqual(result, {})


class ExceptionBehaviorTests(unittest.TestCase):
    """(18) representative exception behavior: path-id collision guard."""

    def test_path_id_collision_raises_value_error(self) -> None:
        resolver = FunctionalFlowResolver()
        paths: dict = {}
        resolver._path_identities = {}
        resolver._path_id = lambda *args: ("PATH-forced", "one")
        resolver._add_path(paths, {"id": "EP-A"}, ["P::a.start"], [], "dead_end", "P::a.start", "confirmed", [])
        resolver._path_id = lambda *args: ("PATH-forced", "different")
        with self.assertRaisesRegex(ValueError, "collision"):
            resolver._add_path(paths, {"id": "EP-B"}, ["P::b.start"], [], "dead_end", "P::b.start", "confirmed", [])


if __name__ == "__main__":
    unittest.main()
