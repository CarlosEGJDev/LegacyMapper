"""V4.3 final AI pilot proposal quality correction: verification tests.

The V4.3 final real AI pilot (`docs/V4_3/V4_3_FINAL_AI_PILOT_PROPOSAL_QUALITY_
CORRECTION_RESULT.md`) found that all 8 proposals produced by `PROPOSAL_GENERATION`
followed the same pattern -- "<entry point> has no recorded data operations and
ends at an unresolved node" -- even though the repository contained flows with
confirmed stored procedures, transactions and write evidence. Root cause: the
deterministic candidate selection in `legacy_documenter.context.ai_projection`
(`select_flow_ids`, `AiProjectionBuilder.package`) ordered flows/records purely by
`(confidence, flow_id)`, a key that never looked at data-operation/terminal
richness, so a small budget could be exhausted entirely by "no recorded data
operations, unresolved terminal" flows.

These tests cover T1-T9 from the correction prompt using only synthetic fixtures
of the exact shape `EvidenceHydrator`/`select_flow_ids` already consume -- no real
Copilot call, no network, no LLM provider is reachable from this module.
"""
from __future__ import annotations

import unittest

from legacy_documenter.context import ai_projection as aip
from legacy_documenter.context.hydration import EvidenceHydrator


def _flow(flow_id: str, confidence: str = "unresolved", project_sequence: list | None = None) -> dict:
    return {
        "id": flow_id, "entry_point_id": f"EP-{flow_id}", "confidence": confidence,
        "project_sequence": project_sequence or ["P"],
    }


def _entry_point(flow_id: str) -> dict:
    return {
        "id": f"EP-{flow_id}", "webform": f"web\\{flow_id}.ascx", "event": "Click",
        "handler": f"btn_{flow_id}_Click", "start_method": f"Start_{flow_id}",
    }


def _trivial_path(flow_id: str) -> dict:
    """A path that resolves nothing: an `unresolved_boundary` terminal, no data operations."""
    return {
        "path_id": f"PATH-{flow_id}", "flow_id": flow_id, "nodes": [],
        "terminal_type": "unresolved_boundary", "terminal_target": f"UNRESOLVED-{flow_id}",
        "confidence": "unresolved", "evidence_refs": [],
    }


def _stored_procedure_path(flow_id: str) -> dict:
    """A path that reaches a resolved stored procedure terminal."""
    return {
        "path_id": f"PATH-{flow_id}", "flow_id": flow_id, "nodes": [],
        "terminal_type": "stored_procedure", "terminal_target": f"SP-{flow_id}",
        "confidence": "confirmed", "evidence_refs": [f"CALL-{flow_id}"],
    }


def _transaction_path(flow_id: str) -> dict:
    """A path whose terminal is a confirmed transaction data-access operation."""
    return {
        "path_id": f"PATH-{flow_id}", "flow_id": flow_id, "nodes": [f"DAO-TX-{flow_id}"],
        "terminal_type": "unresolved_boundary", "terminal_target": f"DAO-TX-{flow_id}",
        "confidence": "confirmed", "evidence_refs": [],
    }


def _write_path(flow_id: str) -> dict:
    """A path whose terminal is a confirmed write (`INSERT`) data-access operation."""
    return {
        "path_id": f"PATH-{flow_id}", "flow_id": flow_id, "nodes": [f"DAO-W-{flow_id}"],
        "terminal_type": "unresolved_boundary", "terminal_target": f"DAO-W-{flow_id}",
        "confidence": "confirmed", "evidence_refs": [],
    }


def _mixed_path(flow_id: str) -> dict:
    """One confirmed non-data path plus one unresolved path for the same flow."""
    return [
        {
            "path_id": f"PATH-{flow_id}-A", "flow_id": flow_id, "nodes": [],
            "terminal_type": "unresolved_boundary", "terminal_target": f"MIXED-A-{flow_id}",
            "confidence": "confirmed", "evidence_refs": [f"REF-{flow_id}-1", f"REF-{flow_id}-2"],
        },
        {
            "path_id": f"PATH-{flow_id}-B", "flow_id": flow_id, "nodes": [],
            "terminal_type": "unresolved_boundary", "terminal_target": f"MIXED-B-{flow_id}",
            "confidence": "unresolved", "evidence_refs": [],
        },
    ]


def _mixed_diverse_ix() -> dict:
    """T2/T14 fixture: one trivial flow per letter plus the richer categories A-F from section 14."""
    flows = [
        _flow("FLOW-A", confidence="unresolved"),
        _flow("FLOW-B", confidence="confirmed"),
        _flow("FLOW-C", confidence="confirmed"),
        _flow("FLOW-D", confidence="confirmed"),
        _flow("FLOW-E", confidence="confirmed", project_sequence=["P1", "P2"]),
        _flow("FLOW-F", confidence="unresolved"),
    ]
    entry_points = [_entry_point(f["id"]) for f in flows]
    paths = [
        _trivial_path("FLOW-A"),
        _stored_procedure_path("FLOW-B"),
        _transaction_path("FLOW-C"),
        _write_path("FLOW-D"),
        *_mixed_path("FLOW-E"),
        _trivial_path("FLOW-F"),
    ]
    return {
        "functional_flows": flows, "entry_points": entry_points, "functional_paths": paths,
        "data_access": [
            {"id": "DAO-TX-FLOW-C", "class": "Repo", "method": "Begin", "operation_kind": "transaction",
             "confidence": "confirmed", "evidence": [{"expression": "BeginTrans"}]},
            {"id": "DAO-W-FLOW-D", "class": "Repo", "method": "Save", "operation_kind": "write",
             "sql_operation": "INSERT", "confidence": "confirmed"},
        ],
        "stored_procedures": [{"id": "SP-FLOW-B", "name": "PKG.SAVE", "package": "PKG", "procedure": "SAVE"}],
        "sql_operations": [], "data_parameters": [],
    }


def _homogeneous_trivial_ix(count: int = 5) -> dict:
    """T1 fixture: every flow is unresolved with no recorded data operations."""
    flows = [_flow(f"FLOW-{i:03d}", confidence="unresolved") for i in range(count)]
    entry_points = [_entry_point(f["id"]) for f in flows]
    paths = [_trivial_path(f["id"]) for f in flows]
    return {
        "functional_flows": flows, "entry_points": entry_points, "functional_paths": paths,
        "data_access": [], "stored_procedures": [], "sql_operations": [], "data_parameters": [],
    }


class T1HomogeneousTrivialSetTests(unittest.TestCase):
    """T1 -- a dataset with only unresolved, no-data-operation flows must still select safely."""

    def test_selection_succeeds_and_uses_all_available_candidates_within_the_limit(self) -> None:
        ix = _homogeneous_trivial_ix(5)
        selected = aip.select_flow_ids(ix, 3)
        self.assertEqual(len(selected), 3)
        self.assertTrue(set(selected).issubset({f["id"] for f in ix["functional_flows"]}))

    def test_selection_is_deterministic_on_a_homogeneous_set(self) -> None:
        ix = _homogeneous_trivial_ix(5)
        self.assertEqual(aip.select_flow_ids(ix, 3), aip.select_flow_ids(ix, 3))

    def test_selection_does_not_raise_when_nothing_but_trivial_flows_exist(self) -> None:
        ix = _homogeneous_trivial_ix(1)
        self.assertEqual(aip.select_flow_ids(ix, 5), ["FLOW-000"])


class T2MixedCandidateSetTests(unittest.TestCase):
    """T2 -- a mixed dataset must not let the trivial category consume every slot."""

    def test_a_small_selection_includes_richer_flows_before_all_trivial_slots(self) -> None:
        ix = _mixed_diverse_ix()
        selected = aip.select_flow_ids(ix, 4)
        self.assertEqual(len(selected), 4)
        trivial = {"FLOW-A", "FLOW-F"}
        self.assertLess(len(set(selected) & trivial), 4)
        self.assertTrue(set(selected) - trivial, "richer flows must be represented")

    def test_full_selection_still_contains_every_flow_when_the_limit_allows_it(self) -> None:
        ix = _mixed_diverse_ix()
        selected = aip.select_flow_ids(ix, 6)
        self.assertEqual(set(selected), {"FLOW-A", "FLOW-B", "FLOW-C", "FLOW-D", "FLOW-E", "FLOW-F"})

    def test_richer_flows_are_not_all_excluded_by_a_tight_character_budget(self) -> None:
        ix = _mixed_diverse_ix()
        builder = aip.AiProjectionBuilder()
        flow_ids = aip.select_flow_ids(ix, 6)
        records = [EvidenceHydrator().hydrate_flow(fid, ix) for fid in flow_ids]
        full = builder.package(records)
        tight = builder.package(records, budget={"max_records": 3})
        selected_flow_ids = {r["flow_id"] for r in tight["records"]}
        self.assertLessEqual(len(tight["records"]), 3)
        self.assertTrue(
            selected_flow_ids - {"FLOW-A", "FLOW-F"},
            "package() truncation must not drop every richer record before the trivial ones",
        )
        self.assertGreaterEqual(len(full["records"]), len(tight["records"]))


class T3StableOrderingTests(unittest.TestCase):
    """T3 -- the same input must always produce the same selected ids in the same order."""

    def test_select_flow_ids_is_stable_across_repeated_calls(self) -> None:
        ix = _mixed_diverse_ix()
        first = aip.select_flow_ids(ix, 4)
        for _ in range(5):
            self.assertEqual(aip.select_flow_ids(ix, 4), first)

    def test_select_flow_ids_is_stable_regardless_of_input_flow_order(self) -> None:
        ix = _mixed_diverse_ix()
        shuffled = dict(ix)
        shuffled["functional_flows"] = list(reversed(ix["functional_flows"]))
        self.assertEqual(aip.select_flow_ids(ix, 4), aip.select_flow_ids(shuffled, 4))

    def test_package_ordering_is_stable_across_repeated_calls(self) -> None:
        ix = _mixed_diverse_ix()
        records = [EvidenceHydrator().hydrate_flow(fid, ix) for fid in aip.select_flow_ids(ix, 6)]
        builder = aip.AiProjectionBuilder()
        first = builder.package(records)
        for _ in range(5):
            self.assertEqual(builder.package(records), first)


class T4TieBreakTests(unittest.TestCase):
    """T4 -- candidates tied on richness bucket and confidence break ties by flow_id."""

    def test_two_equally_trivial_flows_break_ties_by_ascending_flow_id(self) -> None:
        ix = _homogeneous_trivial_ix(2)
        self.assertEqual(aip.select_flow_ids(ix, 1), ["FLOW-000"])

    def test_two_equally_rich_flows_break_ties_by_ascending_flow_id(self) -> None:
        flows = [_flow("FLOW-B", confidence="confirmed"), _flow("FLOW-A", confidence="confirmed")]
        ix = {
            "functional_flows": flows,
            "entry_points": [_entry_point("FLOW-A"), _entry_point("FLOW-B")],
            "functional_paths": [_stored_procedure_path("FLOW-A"), _stored_procedure_path("FLOW-B")],
            "data_access": [], "sql_operations": [], "data_parameters": [],
            "stored_procedures": [
                {"id": "SP-FLOW-A", "name": "PKG.A", "package": "PKG", "procedure": "A"},
                {"id": "SP-FLOW-B", "name": "PKG.B", "package": "PKG", "procedure": "B"},
            ],
        }
        self.assertEqual(aip.select_flow_ids(ix, 1), ["FLOW-A"])


class T5NoConfidenceMutationTests(unittest.TestCase):
    """T5 -- selection/ranking never mutates flow, path, or terminal confidence."""

    def test_flow_confidence_is_unchanged_after_selection(self) -> None:
        ix = _mixed_diverse_ix()
        before = {f["id"]: f["confidence"] for f in ix["functional_flows"]}
        aip.select_flow_ids(ix, 4)
        after = {f["id"]: f["confidence"] for f in ix["functional_flows"]}
        self.assertEqual(before, after)

    def test_path_confidence_is_unchanged_after_packaging(self) -> None:
        ix = _mixed_diverse_ix()
        records = [EvidenceHydrator().hydrate_flow(fid, ix) for fid in aip.select_flow_ids(ix, 6)]
        before = [{p["path_ids"][0]: p["confidence"] for p in r["paths"]} for r in records]
        aip.AiProjectionBuilder().package(records)
        after = [{p["path_ids"][0]: p["confidence"] for p in r["paths"]} for r in records]
        self.assertEqual(before, after)

    def test_terminal_confidence_bearing_fields_are_unchanged_after_packaging(self) -> None:
        ix = _mixed_diverse_ix()
        records = [EvidenceHydrator().hydrate_flow(fid, ix) for fid in aip.select_flow_ids(ix, 6)]
        before = [r["terminals"] for r in records]
        aip.AiProjectionBuilder().package(records)
        after = [r["terminals"] for r in records]
        self.assertEqual(before, after)


class T6EvidencePreservationTests(unittest.TestCase):
    """T6 -- selected candidates keep their original evidence ids untouched."""

    def test_selected_flow_ids_are_exactly_original_ids(self) -> None:
        ix = _mixed_diverse_ix()
        original_ids = {f["id"] for f in ix["functional_flows"]}
        selected = aip.select_flow_ids(ix, 6)
        self.assertTrue(set(selected).issubset(original_ids))
        self.assertEqual(len(selected), len(set(selected)))

    def test_packaged_records_preserve_evidence_refs(self) -> None:
        ix = _mixed_diverse_ix()
        records = [EvidenceHydrator().hydrate_flow(fid, ix) for fid in aip.select_flow_ids(ix, 6)]
        expected = {r["flow_id"]: aip.record_reference_ids(r) for r in records}
        package = aip.AiProjectionBuilder().package(records)
        for record in package["records"]:
            self.assertEqual(aip.record_reference_ids(record), expected[record["flow_id"]])


class T7CandidateLimitTests(unittest.TestCase):
    """T7 -- the selection contract still caps at the requested limit."""

    def test_select_flow_ids_never_exceeds_max_flows(self) -> None:
        ix = _mixed_diverse_ix()
        for limit in (1, 2, 3, 4, 5, 6, 10):
            self.assertLessEqual(len(aip.select_flow_ids(ix, limit)), limit)

    def test_package_never_exceeds_max_records(self) -> None:
        ix = _mixed_diverse_ix()
        records = [EvidenceHydrator().hydrate_flow(fid, ix) for fid in aip.select_flow_ids(ix, 6)]
        package = aip.AiProjectionBuilder().package(records, budget={"max_records": 2})
        self.assertLessEqual(len(package["records"]), 2)


class T8NoLLMDependencyTests(unittest.TestCase):
    """T8 -- the selector/packager must work without copilot, network, or any LLM provider."""

    def test_ai_projection_module_never_imports_the_llm_package(self) -> None:
        import ast
        import inspect
        tree = ast.parse(inspect.getsource(aip))
        imported_modules = [
            alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names
        ] + [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        self.assertFalse(any(m.startswith("legacy_documenter.llm") for m in imported_modules))
        self.assertFalse(any("copilot" in m.lower() for m in imported_modules))

    def test_selection_and_packaging_run_to_completion_with_no_provider_involved(self) -> None:
        ix = _mixed_diverse_ix()
        selected = aip.select_flow_ids(ix, 4)
        records = [EvidenceHydrator().hydrate_flow(fid, ix) for fid in selected]
        package = aip.AiProjectionBuilder().package(records)
        self.assertEqual(package["contract_name"], "AI_HYDRATED_PROJECTION")


class T9ExistingRegressionTests(unittest.TestCase):
    """T9 -- the pre-existing V4.3-R5 selection/packaging contract tests must still pass."""

    def test_the_r5_budgeting_module_still_imports_and_exposes_its_public_surface(self) -> None:
        self.assertTrue(callable(aip.select_flow_ids))
        self.assertTrue(callable(aip.AiProjectionBuilder))
        for name in ("PROFILE_REDUCTION", "ALLOWED_PROFILES", "CONTRACT_NAME", "CONTRACT_VERSION"):
            self.assertTrue(hasattr(aip, name))


class RichnessBucketDiversityTests(unittest.TestCase):
    """Section 14 -- with a small limit, the selector must not choose exclusively A/F when B-E exist."""

    def test_selection_of_four_from_six_prefers_richer_categories_over_pure_trivial(self) -> None:
        ix = _mixed_diverse_ix()
        selected = set(aip.select_flow_ids(ix, 4))
        self.assertNotEqual(selected, {"FLOW-A", "FLOW-F"})
        self.assertTrue({"FLOW-B", "FLOW-C", "FLOW-D", "FLOW-E"} & selected)

    def test_richness_bucket_ranks_resolved_terminal_above_mixed_above_trivial(self) -> None:
        ix = _mixed_diverse_ix()
        paths_by_flow: dict = {}
        for path in ix["functional_paths"]:
            paths_by_flow.setdefault(path["flow_id"], []).append(path)
        data_access = {d["id"]: d for d in ix["data_access"]}
        flows = {f["id"]: f for f in ix["functional_flows"]}
        bucket_b = aip._flow_richness_bucket(flows["FLOW-B"], paths_by_flow, data_access)
        bucket_e = aip._flow_richness_bucket(flows["FLOW-E"], paths_by_flow, data_access)
        bucket_a = aip._flow_richness_bucket(flows["FLOW-A"], paths_by_flow, data_access)
        self.assertLess(bucket_b, bucket_e)
        self.assertLess(bucket_e, bucket_a)


if __name__ == "__main__":
    unittest.main()
