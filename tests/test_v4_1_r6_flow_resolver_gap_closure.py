"""V4.1-R6 Gate A -- FunctionalFlowResolver characterization gap closure.

Closes the four FunctionalFlowResolver gaps R5 left open (see
docs/V4_1/V4_1_R5_RISKY_ORCHESTRATORS_CHARACTERIZATION_RESULT.md and
output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json ->
flow_resolver.r6_readiness_missing_characterization). No production code is
modified by this file.
"""
from __future__ import annotations

import unittest

from legacy_documenter.analysis.flow_resolver import FunctionalFlowResolver


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


class Gap1StableIdPinnedValuesTests(unittest.TestCase):
    """Gap 1: `_stable_id` pinned to exact deterministic known values."""

    def setUp(self) -> None:
        self.resolver = FunctionalFlowResolver()

    def test_pinned_flow_id_values(self) -> None:
        self.assertEqual(self.resolver._stable_id("FLOW", "EP-1", "Page.Handler"), "FLOW-0306391063")
        self.assertEqual(self.resolver._stable_id("FLOW", "EP-2", "Page.Handler"), "FLOW-0472419520")

    def test_pinned_call_and_unresolved_id_values(self) -> None:
        self.assertEqual(self.resolver._stable_id("CALL", "S.vb", 1, "X()", None), "CALL-0187743453")
        self.assertEqual(self.resolver._stable_id("UNRES", "CALL-x", "helper.Dyn()"), "UNRES-0976356111")

    def test_same_input_yields_exact_same_id_cross_run(self) -> None:
        first = self.resolver._stable_id("FLOW", "EP-1", "Page.Handler")
        second = FunctionalFlowResolver()._stable_id("FLOW", "EP-1", "Page.Handler")
        self.assertEqual(first, second)
        self.assertEqual(first, "FLOW-0306391063")

    def test_no_parts_yields_pinned_zero_value(self) -> None:
        self.assertEqual(self.resolver._stable_id("PREFIX"), "PREFIX-0000000000")
        self.assertEqual(self.resolver._stable_id("PREFIX", None), "PREFIX-0000000000")

    def test_different_canonical_identity_yields_different_id(self) -> None:
        self.assertNotEqual(
            self.resolver._stable_id("FLOW", "EP-1", "Page.Handler"),
            self.resolver._stable_id("FLOW", "EP-1", "Page.Other"),
        )


class Gap2OverlappingEntryPointsTests(unittest.TestCase):
    """Gap 2: two entry points sharing an overlapping call graph in one resolve() call."""

    def test_shared_downstream_method_produces_two_independent_flows_with_no_cross_contamination(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [
            entry("EP-1", "Default.aspx", "Click", "btn1", "Page.Shared"),
            entry("EP-2", "Default.aspx", "Click", "btn2", "Page.Shared"),
        ]
        calls = files_calls(call("Page", "Shared", "Page.Target", "confirmed", line=1, expression="Target()"))
        data_access = [{"id": "DAO-1", "class": "Page", "method": "Target", "project": None, "confidence": "confirmed"}]
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, data_access, [], [], [])

        self.assertEqual(len(flows), 2)
        self.assertEqual({f["entry_point_id"] for f in flows}, {"EP-1", "EP-2"})
        # Each flow independently rebuilds the full node set for its own
        # traversal (graph_nodes/graph_edges/paths are fresh dicts created
        # per entry point inside resolve()'s for-loop) -- both flows see the
        # same shared method node, but neither flow's node list is polluted
        # by the other entry point's data.
        for flow in flows:
            node_ids = {n["id"] for n in flow["nodes"]}
            self.assertIn("<unknown>::page.shared", node_ids)
            self.assertIn("<unknown>::page.target", node_ids)

        self.assertEqual(len(paths), 2)
        self.assertEqual({p["entry_point_id"] for p in paths}, {"EP-1", "EP-2"})
        # Path identity includes entry_point_id, so the two paths -- despite
        # traversing the identical underlying method chain -- get distinct
        # path ids and are never merged into one.
        self.assertNotEqual(paths[0]["path_id"], paths[1]["path_id"])

    def test_flows_remain_sorted_by_flow_id_regardless_of_entry_order(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [
            entry("EP-2", "Default.aspx", "Click", "btn2", "Page.Shared"),
            entry("EP-1", "Default.aspx", "Click", "btn1", "Page.Shared"),
        ]
        flows, *_ = resolver.resolve(entries, [], [], [], [], [])
        self.assertEqual(flows, sorted(flows, key=lambda item: item["id"]))


class Gap3FlowStatusPrecedenceTests(unittest.TestCase):
    """Gap 3: `_flow_status` precedence when cycle and truncated_depth coexist."""

    def test_cycle_and_truncated_depth_can_coexist_in_one_flow_and_truncated_depth_wins(self) -> None:
        # This combination IS structurally possible (not NOT_APPLICABLE):
        # one branch from the entry method reaches a short cycle before
        # max_depth is hit, while a second, independent branch is a longer
        # chain that gets truncated. Both paths land in the same flow.
        resolver = FunctionalFlowResolver(max_depth=3)
        entries = [entry("EP-1", "Default.aspx", "Click", "btn1", "Page.A")]
        calls = files_calls(
            call("Page", "A", "Page.Loop", "confirmed", line=1, expression="Loop()"),
            call("Page", "Loop", "Page.A", "confirmed", line=2, expression="A()"),
            call("Page", "A", "Page.D1", "confirmed", line=3, expression="D1()"),
            call("Page", "D1", "Page.D2", "confirmed", line=4, expression="D2()"),
            call("Page", "D2", "Page.D3", "confirmed", line=5, expression="D3()"),
            call("Page", "D3", "Page.D4", "confirmed", line=6, expression="D4()"),
        )
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, [], [], [], [])
        terminal_types = {p["terminal_type"] for p in paths}
        self.assertEqual(terminal_types, {"cycle", "truncated_depth"})
        # Fixed precedence order (truncated_depth > cycle > unresolved_boundary
        # > data_endpoint > dead_end) is preserved: truncated_depth wins.
        self.assertEqual(flows[0]["status"], "truncated_depth")


class Gap4MixedDataAccessAndOutgoingCallsTests(unittest.TestCase):
    """Gap 4: a method with both direct data-access operations and outgoing calls."""

    def test_both_the_data_access_path_and_the_call_path_survive_independently(self) -> None:
        resolver = FunctionalFlowResolver()
        entries = [entry("EP-1", "Default.aspx", "Click", "btn1", "Page.Mixed")]
        calls = files_calls(call("Page", "Mixed", "Page.Other", "confirmed", line=1, expression="Other()"))
        data_access = [{"id": "DAO-1", "class": "Page", "method": "Mixed", "project": None, "confidence": "confirmed"}]
        flows, paths, summary, unresolved = resolver.resolve(entries, calls, data_access, [], [], [])

        self.assertEqual(len(paths), 2)
        terminal_types = {p["terminal_type"] for p in paths}
        self.assertEqual(terminal_types, {"dead_end", "data_operation"})
        # data_endpoint (from the data_operation path) outranks dead_end in
        # the fixed _flow_status precedence order, so the flow as a whole is
        # reported as data_endpoint even though one of its two paths is a
        # dead end.
        self.assertEqual(flows[0]["status"], "data_endpoint")
        self.assertEqual(summary["total_paths"], 2)
        self.assertEqual(summary["paths_to_data_operation"], 1)
        self.assertEqual(summary["dead_end_paths"], 1)


if __name__ == "__main__":
    unittest.main()
