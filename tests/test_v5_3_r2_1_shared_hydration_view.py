"""V5.3-R2.1: run-scoped, indexed and memoizing `HydrationView`.

The hydration output must be identical to the pre-R2.1 implementation: that
implementation (rebuild five dicts + scan every path and every data parameter on
each call) is reproduced below as `_reference_hydrate_flow`, the oracle.
"""
from __future__ import annotations

import ast
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from legacy_documenter.cli import pipeline_stages
from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.context.consumer_projection import ConsumerProjectionBuilder
from legacy_documenter.context import hydration, hydration_view
from legacy_documenter.context.hydration import EvidenceHydrator, UnknownFlowError
from legacy_documenter.context.hydration_view import HydrationView
from legacy_documenter.documentation.human_documentation_scaling import render_human_documentation_index
from legacy_documenter.main import analyze_repository

ROOT = Path(__file__).resolve().parent.parent
FULL_SAMPLE = ROOT / "tests" / "fixtures" / "v4_2_r7_full_sample"


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _reference_hydrate_flow(flow_id: str, ix: dict) -> dict:
    """The hydration exactly as implemented before V5.3-R2.1 (oracle for equivalence)."""
    hydrator = EvidenceHydrator()
    flows = {f["id"]: f for f in ix.get("functional_flows", [])}
    flow = flows.get(flow_id)
    if flow is None:
        raise UnknownFlowError(flow_id)
    entry_points = {e["id"]: e for e in ix.get("entry_points", [])}
    entry = entry_points.get(flow.get("entry_point_id"), {})
    data_access = {d["id"]: d for d in ix.get("data_access", []) if d.get("id")}
    stored_procedures = {p["id"]: p for p in ix.get("stored_procedures", []) if p.get("id")}
    sql_operations = {s["id"]: s for s in ix.get("sql_operations", []) if s.get("id")}
    data_parameters = ix.get("data_parameters", [])
    raw_paths = [p for p in ix.get("functional_paths", []) if p.get("flow_id") == flow_id]
    groups = hydrator.select_and_deduplicate_paths(raw_paths)
    hydrated_paths = [hydrator._hydrate_path_group(g, data_access, stored_procedures, sql_operations) for g in groups]

    callers = sorted({n["caller"] for p in hydrated_paths for n in p["nodes"] if n.get("type") == "data_access" and n.get("caller")})
    by_caller: dict[str, set] = {}
    for param in data_parameters:
        caller = f"{param.get('class')}.{param.get('method')}"
        if caller in callers:
            by_caller.setdefault(caller, set()).add(param.get("name") or "(unnamed)")
    parameters = [{"caller": c, "names": sorted(by_caller[c])} for c in callers if by_caller.get(c)]

    return {
        "model_version": hydrator.MODEL_VERSION,
        "flow_id": flow_id,
        "entry_point": {
            "id": flow.get("entry_point_id"), "webform": entry.get("webform"), "event": entry.get("event"),
            "handler": entry.get("handler"), "start_method": entry.get("start_method"), "project": entry.get("project"),
        },
        "projects": list(flow.get("project_sequence", [])),
        "paths": hydrated_paths,
        "terminals": hydrator._terminals(hydrated_paths),
        "transactions": hydrator._transactions(hydrated_paths),
        "data_operations": hydrator._data_operations(hydrated_paths),
        "parameters": parameters,
        "confidence": flow.get("confidence"),
        "unresolved": [p["path_ids"][0] for p in hydrated_paths if p["terminal_type"] == "unresolved_boundary"],
        "provenance": {
            "source_indexes": [
                "index/functional_flows.json", "index/functional_paths.json", "index/entry_points.json",
                "index/data_access.json", "index/stored_procedures.json", "index/sql_operations.json",
                "index/data_parameters.json",
            ],
            "flow_source_index_pointer": f"index/functional_flows.json#{flow_id}",
        },
        "selection": {
            "input_path_count": len(raw_paths), "output_path_count": len(hydrated_paths),
            "deduplicated_path_count": len(raw_paths) - len(hydrated_paths),
            "priority_policy": "confirmed_before_inferred_before_unresolved",
        },
    }


def _ix() -> dict:
    return {
        "functional_flows": [
            {"id": "FLOW-A", "entry_point_id": "EP-A", "confidence": "confirmed", "project_sequence": ["DAL", "WEB"]},
            {"id": "FLOW-B", "entry_point_id": "EP-B", "confidence": "unresolved", "project_sequence": ["WEB"]},
            {"id": "FLOW-C", "entry_point_id": "EP-MISSING", "confidence": "inferred", "project_sequence": []},
            {"id": "FLOW-D", "entry_point_id": "EP-D", "confidence": "confirmed", "project_sequence": ["DAL"]},
        ],
        "functional_paths": [
            {"path_id": "PATH-1", "flow_id": "FLOW-A", "nodes": ["DAO-1"], "terminal_type": "stored_procedure", "terminal_target": "SP-1", "confidence": "confirmed", "evidence_refs": ["EVR-1"]},
            {"path_id": "PATH-2", "flow_id": "FLOW-A", "nodes": ["DAO-1"], "terminal_type": "stored_procedure", "terminal_target": "SP-1", "confidence": "inferred", "evidence_refs": ["EVR-2"]},
            {"path_id": "PATH-3", "flow_id": "FLOW-A", "nodes": ["DAO-2"], "terminal_type": "unresolved_boundary", "terminal_target": "UnknownHelper.Execute", "confidence": "unresolved", "evidence_refs": []},
            {"path_id": "PATH-4", "flow_id": "FLOW-B", "nodes": [], "terminal_type": "unresolved_boundary", "terminal_target": "unknown", "confidence": "unresolved", "evidence_refs": []},
            # FLOW-D: a transaction, a SQL terminal and a data-access terminal.
            {"path_id": "PATH-5", "flow_id": "FLOW-D", "nodes": ["DAO-3", "SQL-1"], "terminal_type": "sql", "terminal_target": "SQL-1", "confidence": "confirmed", "evidence_refs": ["EVR-5"]},
            {"path_id": "PATH-6", "flow_id": "FLOW-D", "nodes": ["DAO-3"], "terminal_type": "data_access", "terminal_target": "DAO-3", "confidence": "confirmed", "evidence_refs": []},
        ],
        "entry_points": [
            {"id": "EP-A", "webform": "a.ascx", "event": "Click", "handler": "btn_Click", "start_method": "btn_Click", "project": "WEB.vbproj"},
            {"id": "EP-B", "webform": "b.ascx", "event": "Load", "handler": "Page_Load", "start_method": "Page_Load"},
            {"id": "EP-D", "webform": "d.ascx", "event": "Click", "handler": "btnD_Click", "start_method": "btnD_Click"},
        ],
        "data_access": [
            {"id": "DAO-1", "class": "CobDAO", "method": "Actualizar", "operation_kind": "call", "confidence": "confirmed", "evidence": [{"file": "CobDAO.vb", "line": 5}]},
            {"id": "DAO-2", "class": "CobDAO", "method": "InitializeComponent", "operation_kind": "call", "confidence": "unresolved", "evidence": []},
            {"id": "DAO-3", "class": "TxDAO", "method": "Grabar", "operation_kind": "transaction", "sql_operation": "UPDATE", "confidence": "confirmed", "evidence": [{"file": "TxDAO.vb", "line": 9, "expression": "cn.BeginTransaction()"}]},
            {"class": "NoIdDAO", "method": "Ignored", "operation_kind": "call"},
        ],
        "stored_procedures": [
            {"id": "SP-1", "name": "spActualizarSaldo", "package": "PKG_COB", "procedure": "PR_SALDO", "confidence": "confirmed"},
        ],
        "sql_operations": [{"id": "SQL-1", "operation": "SELECT * FROM T", "confidence": "confirmed"}],
        "data_parameters": [
            {"class": "CobDAO", "method": "Actualizar", "name": "pIdCliente"},
            {"class": "CobDAO", "method": "Actualizar", "name": "pMonto"},
            {"class": "CobDAO", "method": "Actualizar", "name": "pMonto"},
            {"class": "CobDAO", "method": "Actualizar"},
            {"class": "TxDAO", "method": "Grabar", "name": ""},
            {"class": "OtherDAO", "method": "Unrelated", "name": "pIgnored"},
        ],
    }


def _full_sample_indexes() -> dict:
    with tempfile.TemporaryDirectory() as out:
        return analyze_repository(FULL_SAMPLE, out, None, 12)


class EquivalenceWithPreviousImplementationTests(unittest.TestCase):
    def test_every_flow_of_the_fixture_is_identical_to_the_previous_implementation(self):
        ix = _ix()
        view = HydrationView(ix)
        hydrator = EvidenceHydrator()
        for flow in ix["functional_flows"]:
            expected = _canonical(_reference_hydrate_flow(flow["id"], ix))
            self.assertEqual(_canonical(view.hydrate_flow(flow["id"])), expected, flow["id"])
            self.assertEqual(_canonical(hydrator.hydrate_flow(flow["id"], ix)), expected, flow["id"])

    def test_every_flow_of_a_real_pipeline_sample_is_identical(self):
        ix = _full_sample_indexes()
        self.assertGreater(len(ix["functional_flows"]), 0)
        view = HydrationView(ix)
        for flow in ix["functional_flows"]:
            self.assertEqual(_canonical(view.hydrate_flow(flow["id"])), _canonical(_reference_hydrate_flow(flow["id"], ix)))

    def test_all_relevant_fields_are_present_and_equal(self):
        ix = _ix()
        record = HydrationView(ix).hydrate_flow("FLOW-A")
        reference = _reference_hydrate_flow("FLOW-A", ix)
        self.assertEqual(list(record), list(reference))
        for key in reference:
            self.assertEqual(record[key], reference[key], key)
        self.assertEqual(record["provenance"]["flow_source_index_pointer"], "index/functional_flows.json#FLOW-A")
        self.assertEqual(record["selection"]["deduplicated_path_count"], 1)

    def test_parameters_are_resolved_per_caller_like_before(self):
        record = HydrationView(_ix()).hydrate_flow("FLOW-A")
        # Unnamed parameters collapse to "(unnamed)"; duplicates collapse; unreached callers are excluded.
        self.assertEqual(record["parameters"], [{"caller": "CobDAO.Actualizar", "names": ["(unnamed)", "pIdCliente", "pMonto"]}])
        record_d = HydrationView(_ix()).hydrate_flow("FLOW-D")
        self.assertEqual(record_d["parameters"], [{"caller": "TxDAO.Grabar", "names": ["(unnamed)"]}])

    def test_flow_without_paths_and_without_entry_point(self):
        ix = _ix()
        record = HydrationView(ix).hydrate_flow("FLOW-C")
        self.assertEqual(record, _reference_hydrate_flow("FLOW-C", ix))
        self.assertEqual(record["paths"], [])
        self.assertEqual(record["selection"], {
            "input_path_count": 0, "output_path_count": 0, "deduplicated_path_count": 0,
            "priority_policy": "confirmed_before_inferred_before_unresolved",
        })
        self.assertIsNone(record["entry_point"]["webform"])

    def test_flow_with_unresolved_is_preserved(self):
        record = HydrationView(_ix()).hydrate_flow("FLOW-A")
        self.assertEqual(record["unresolved"], ["PATH-3"])
        self.assertEqual(record["confidence"], "confirmed")

    def test_flow_with_data_access_stored_procedure_and_sql(self):
        ix = _ix()
        view = HydrationView(ix)
        a = view.hydrate_flow("FLOW-A")
        self.assertEqual(a["terminals"]["stored_procedures"][0]["resolved_name"], "spActualizarSaldo")
        d = view.hydrate_flow("FLOW-D")
        self.assertEqual(d["terminals"]["sql_operations"][0]["resolved_name"], "SELECT * FROM T")
        self.assertEqual(d["transactions"][0]["verb"], "BeginTransaction")
        self.assertEqual(d["data_operations"][0]["operation"], "UPDATE")

    def test_unknown_flow_raises_like_before(self):
        with self.assertRaises(UnknownFlowError):
            HydrationView(_ix()).hydrate_flow("FLOW-MISSING")
        with self.assertRaises(UnknownFlowError):
            EvidenceHydrator().hydrate_flow("FLOW-MISSING", _ix())

    def test_output_does_not_depend_on_input_list_order(self):
        ix = _ix()
        shuffled = copy.deepcopy(ix)
        shuffled["functional_paths"].reverse()
        shuffled["data_parameters"].reverse()
        for flow in ix["functional_flows"]:
            self.assertEqual(HydrationView(ix).hydrate_flow(flow["id"]), HydrationView(shuffled).hydrate_flow(flow["id"]))

    def test_deterministic_across_views(self):
        ix = _ix()
        first = {f["id"]: _canonical(HydrationView(ix).hydrate_flow(f["id"])) for f in ix["functional_flows"]}
        second = {f["id"]: _canonical(HydrationView(ix).hydrate_flow(f["id"])) for f in ix["functional_flows"]}
        self.assertEqual(first, second)

    def test_model_version_is_unchanged(self):
        self.assertEqual(EvidenceHydrator.MODEL_VERSION, "V4.3-R3")
        self.assertEqual(hydration.MODEL_VERSION, "V4.3-R3")
        self.assertEqual(HydrationView(_ix()).hydrate_flow("FLOW-A")["model_version"], "V4.3-R3")


class MemoizationAndSharingTests(unittest.TestCase):
    def test_same_flow_requested_twice_is_hydrated_once(self):
        view = HydrationView(_ix())
        first = view.hydrate_flow("FLOW-A")
        second = view.hydrate_flow("FLOW-A")
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertEqual((view.stats["requests"], view.stats["hydrations"], view.stats["memo_hits"]), (2, 1, 1))

    def test_view_is_lazy_and_indexes_once(self):
        ix = _ix()
        view = HydrationView(ix)
        self.assertEqual(view.stats["build_seconds"], 0.0)
        with patch.object(hydration_view, "_HydrationLookups", wraps=hydration_view._HydrationLookups) as lookups:
            for flow in ix["functional_flows"]:
                view.hydrate_flow(flow["id"])
            self.assertEqual(lookups.call_count, 1)

    def test_two_consumers_share_one_view_and_hydrate_each_flow_once(self):
        ix = _full_sample_indexes()
        count = len(ix["functional_flows"])
        view = HydrationView(ix)
        ConsumerProjectionBuilder(hydrator=view).build(ix, source_snapshot="s")
        self.assertEqual(view.stats["hydrations"], count)
        human = [view.hydrate_flow(f["id"], ix) for f in ix["functional_flows"] if f.get("id")]
        render_human_documentation_index(human)
        self.assertEqual(view.stats["hydrations"], count)
        self.assertEqual(view.stats["memo_hits"], count)
        self.assertEqual(view.stats["requests"], 2 * count)
        self.assertEqual(view.stats["distinct_flows_hydrated"], count)

    def test_view_is_bound_to_its_indexes(self):
        view = HydrationView(_ix())
        with self.assertRaises(ValueError):
            view.hydrate_flow("FLOW-A", _ix())
        view.hydrate_flow("FLOW-A", view.ix)

    def test_consumers_do_not_mutate_shared_records(self):
        ix = _full_sample_indexes()
        view = HydrationView(ix)
        ids = [f["id"] for f in ix["functional_flows"]]
        before = {i: _canonical(view.hydrate_flow(i)) for i in ids}
        ConsumerProjectionBuilder(hydrator=view).build(ix, source_snapshot="s")
        render_human_documentation_index([view.hydrate_flow(i) for i in ids])
        after = {i: _canonical(view.hydrate_flow(i)) for i in ids}
        self.assertEqual(before, after)

    def test_a_consumer_mutating_its_record_never_contaminates_another_request(self):
        ix = _ix()
        view = HydrationView(ix)
        first = view.hydrate_flow("FLOW-A")
        first["paths"].clear()
        first["entry_point"]["id"] = "TAMPERED"
        first["selection"]["input_path_count"] = -1
        second = view.hydrate_flow("FLOW-A")          # memo hit
        self.assertEqual(second, _reference_hydrate_flow("FLOW-A", ix))
        second["terminals"]["stored_procedures"].clear()
        self.assertEqual(view.hydrate_flow("FLOW-A"), _reference_hydrate_flow("FLOW-A", ix))

    def test_legacy_hydrator_returns_independent_records_each_call(self):
        ix = _ix()
        hydrator = EvidenceHydrator()
        first = hydrator.hydrate_flow("FLOW-A", ix)
        first["paths"].clear()
        first["entry_point"]["id"] = "TAMPERED"
        second = hydrator.hydrate_flow("FLOW-A", ix)
        self.assertEqual(second, _reference_hydrate_flow("FLOW-A", ix))

    def test_legacy_hydrator_indexes_once_per_indexes_object(self):
        ix = _ix()
        hydrator = EvidenceHydrator()
        with patch.object(hydration, "_HydrationLookups", wraps=hydration._HydrationLookups) as lookups:
            for _ in range(3):
                for flow in ix["functional_flows"]:
                    hydrator.hydrate_flow(flow["id"], ix)
            self.assertEqual(lookups.call_count, 1)
            hydrator.hydrate_flow("FLOW-A", _ix())  # another indexes object -> re-indexed, never stale
            self.assertEqual(lookups.call_count, 2)

    def test_legacy_hydrator_notices_a_replaced_or_resized_list(self):
        ix = _ix()
        hydrator = EvidenceHydrator()
        hydrator.hydrate_flow("FLOW-D", ix)
        ix["functional_paths"].append(
            {"path_id": "PATH-7", "flow_id": "FLOW-D", "nodes": [], "terminal_type": "unresolved_boundary",
             "terminal_target": "x", "confidence": "unresolved", "evidence_refs": []}
        )
        self.assertEqual(hydrator.hydrate_flow("FLOW-D", ix), _reference_hydrate_flow("FLOW-D", ix))


class PipelineWiringTests(unittest.TestCase):
    def test_full_run_hydrates_each_flow_once_and_serves_the_second_consumer_from_memo(self):
        captured: list[HydrationView] = []

        class SpyView(HydrationView):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                captured.append(self)

        with tempfile.TemporaryDirectory() as out, patch.object(pipeline_stages, "HydrationView", SpyView):
            result = run_full_pipeline(FULL_SAMPLE, Path(out), None, 12)
            self.assertEqual(result.status.value, "SUCCESS")
            partition_dir = Path(out) / "consumer_projection" / "parts"
            self.assertTrue(any(partition_dir.iterdir()))
            human_dir = Path(out) / "documentation" / "flujos_humanos"
            self.assertTrue(human_dir.exists() and any(human_dir.iterdir()))
        self.assertEqual(len(captured), 1)
        stats = captured[0].stats
        flows = stats["distinct_flows_hydrated"]
        self.assertEqual(flows, 3)
        self.assertEqual(stats["hydrations"], flows)           # hydrated once, not twice
        self.assertEqual(stats["requests"], 2 * flows)         # consumer_projection + HUMAN_DOCUMENTATION
        self.assertEqual(stats["memo_hits"], flows)

    def test_outputs_are_byte_identical_to_the_previous_hydration(self):
        """Full run with the new wiring vs a run whose hydration is the previous, unindexed implementation."""

        def previous_hydrate(self, flow_id, ix):
            return _reference_hydrate_flow(flow_id, ix)

        def snapshot(root: Path) -> dict:
            return {
                p.relative_to(root).as_posix(): p.read_bytes()
                for p in sorted(root.rglob("*")) if p.is_file()
                and p.relative_to(root).parts[0] in {"consumer_projection", "ai_context", "documentation", "index", "evidence"}
                and p.name != "repository.json"
            }

        with tempfile.TemporaryDirectory() as new_out, tempfile.TemporaryDirectory() as old_out:
            run_full_pipeline(FULL_SAMPLE, Path(new_out), None, 12)
            with patch.object(HydrationView, "hydrate_flow", lambda self, flow_id, ix=None: previous_hydrate(self, flow_id, self.ix)):
                run_full_pipeline(FULL_SAMPLE, Path(old_out), None, 12)
            new, old = snapshot(Path(new_out)), snapshot(Path(old_out))
        self.assertEqual(sorted(new), sorted(old))
        self.assertGreater(len(new), 10)
        for name in new:
            self.assertEqual(new[name], old[name], name)


class RuntimeIndependenceTests(unittest.TestCase):
    def test_hydration_modules_import_only_stdlib_and_each_other_and_perform_no_io(self):
        for module in (hydration, hydration_view):
            tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
            stdlib, relative, called = set(), set(), set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    stdlib.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    (relative if node.level else stdlib).add((node.module or "").split(".")[0])
                elif isinstance(node, ast.Call):
                    func = node.func
                    called.add(func.id if isinstance(func, ast.Name) else getattr(func, "attr", ""))
            # Standard library only, plus these two sibling modules: no llm/provider/copilot, nothing else.
            self.assertLessEqual(stdlib, {"collections", "copy", "time"}, module.__name__)
            self.assertLessEqual(relative, {"hydration", "hydration_view"}, module.__name__)
            # No file or process access (governance files, docs, prompts, tests, PROJECT_STATE).
            self.assertFalse(called & {"open", "read_text", "read_bytes", "write_text", "Path", "listdir", "walk", "getenv"})


if __name__ == "__main__":
    unittest.main()
