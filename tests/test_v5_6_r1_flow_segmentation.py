"""Offline contract, whole-path coverage, neutral budget and scoped proposal proof."""
import ast
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import shutil
import unittest
from unittest.mock import patch

from legacy_documenter.context.ai_projection import AiProjectionBuilder, package_reference_ids, record_reference_ids
from legacy_documenter.context.hydration import EvidenceHydrator
from legacy_documenter.context.flow_segmentation import FlowSegmenter, SegmentationPolicy, SegmentationError, canonical, validate_segment
from legacy_documenter.llm import FakeAIProvider, ProviderConfig
from legacy_documenter.orchestration.ai_interpretation import run_ai_interpretation, _build_request, _build_within_budget, FINDING_SCHEMA
from legacy_documenter.orchestration.segmented_context import build_segmented_context
from legacy_documenter.orchestration.proposal_adapter import adapt_findings_to_proposals
from legacy_documenter.llm.payload import measure_request_payload
from legacy_documenter.cli.full_pipeline import _write_proposal_output

ROOT = Path(__file__).resolve().parents[1]


def indexes(count=30, padding=0):
    return {
        "functional_flows": [{"id": "FLOW-SYN", "entry_point_id": "ENTRY-SYN", "confidence": "confirmed", "project_sequence": ["Synthetic"]}],
        "entry_points": [{"id": "ENTRY-SYN", "project": "Synthetic", "handler": "Start", "event": "Click"}],
        "functional_paths": [{"flow_id": "FLOW-SYN", "path_id": f"PATH-{i:04}", "nodes": [f"DAO-{i:04}"], "terminal_type": "unresolved_boundary" if i % 2 else "sql", "terminal_target": f"DAO-{i:04}", "confidence": "unresolved" if i % 2 else "confirmed", "evidence_refs": [f"DAO-{i:04}"]} for i in range(count)],
        "data_access": [{"id": f"DAO-{i:04}", "class": "Synthetic" + "x" * padding, "method": f"Read{i}", "confidence": "unresolved" if i % 2 else "confirmed", "operation_kind": "sql", "sql_operation": "SELECT"} for i in range(count)],
        "stored_procedures": [], "sql_operations": [], "data_parameters": [],
    }


def parent(count=30, padding=0):
    return EvidenceHydrator().hydrate_flow("FLOW-SYN", indexes(count, padding))


def fake(model="offline-model", window=16000):
    return FakeAIProvider(ProviderConfig("FAKE", "v56-fake", model, context_window=window, max_output_tokens=2000, capabilities={"structured_output": True}), structured_response={"findings": [{"statement": "An included path reaches its recorded operation.", "confidence": "UNCERTAIN", "evidence_refs": ["DAO-0000"]}]})


def output_fixture(path, ix):
    (path / "index").mkdir()
    for key, value in ix.items():
        (path / "index" / (key + ".json")).write_text(json.dumps(value), encoding="utf-8")
    (path / "ai_context").mkdir()
    (path / "ai_context/SYSTEM_CONTEXT.json").write_text(json.dumps({"metadata": {"source_snapshot_sha256": "synthetic-snapshot"}}), encoding="utf-8")


class SegmentContractTests(unittest.TestCase):
    def setUp(self):
        self.parent = parent()
        self.policy = SegmentationPolicy(max_characters=7000)
        self.segments = FlowSegmenter().segment(self.parent, self.policy)

    def test_required_fields_exact_partition_no_overlap(self):
        seen = []
        all_ids = {pid for p in self.parent["paths"] for pid in p["path_ids"]}
        for ordinal, s in enumerate(self.segments, 1):
            validate_segment(s, self.parent, self.policy)
            self.assertTrue(s["partial"])
            self.assertEqual(s["parent_flow_id"], "FLOW-SYN")
            self.assertEqual(s["ordinal"], ordinal)
            self.assertTrue(s["included_paths"])
            self.assertTrue(s["omitted_paths"])
            self.assertEqual(set(s["omitted_paths"]), all_ids - set(s["included_paths"]))
            self.assertEqual(s["overlap_paths"], [])
            self.assertLessEqual(len(canonical(s)), 7000)
            seen.extend(s["included_paths"])
        self.assertEqual(set(seen), all_ids)
        self.assertEqual(len(seen), len(all_ids))

    def test_paths_provenance_confidence_and_refs_preserved(self):
        original = {p["path_ids"][0]: p for p in self.parent["paths"]}
        for s in self.segments:
            self.assertEqual(s["confidence"], self.parent["confidence"])
            for p in s["paths"]:
                self.assertEqual(p, original[p["path_ids"][0]])
            self.assertEqual(set(s["evidence_refs"]), record_reference_ids(s))
            self.assertLessEqual(set(s["evidence_refs"]), record_reference_ids(self.parent))
            self.assertEqual(s["unresolved"], [pid for pid in self.parent["unresolved"] if pid in s["included_paths"]])

    def test_deterministic_repeat_input_order_no_mutation(self):
        snapshot = deepcopy(self.parent)
        reversed_parent = deepcopy(self.parent)
        reversed_parent["paths"].reverse()
        self.assertEqual(self.segments, FlowSegmenter().segment(reversed_parent, self.policy))
        self.assertEqual(self.segments, FlowSegmenter().segment(self.parent, self.policy))
        self.assertEqual(snapshot, self.parent)

    def test_policy_version_changes_identity(self):
        changed = FlowSegmenter().segment(self.parent, replace(self.policy, version="flow-segmentation-v2"))
        self.assertTrue(set(s["segment_id"] for s in changed).isdisjoint(s["segment_id"] for s in self.segments))

    def test_small_and_exact_boundary_unchanged(self):
        for record in (parent(1), self.parent):
            limit = len(canonical(record))
            self.assertEqual(FlowSegmenter().segment(record, SegmentationPolicy(max_characters=limit)), [])
            self.assertEqual(FlowSegmenter().segment(record, SegmentationPolicy(max_characters=limit + 1)), [])

    def test_just_over_boundary_segments(self):
        segments = FlowSegmenter().segment(self.parent, SegmentationPolicy(max_characters=len(canonical(self.parent)) - 1))
        self.assertGreaterEqual(len(segments), 2)

    def test_shared_refs_not_new_evidence(self):
        record = deepcopy(self.parent)
        for p in record["paths"]:
            p["evidence_refs"].append("DAO-0000")
        for s in FlowSegmenter().segment(record, self.policy):
            self.assertLessEqual(set(s["evidence_refs"]), record_reference_ids(record))

    def test_extensions_kept_as_parent_context_and_selected_path_extensions(self):
        record = deepcopy(self.parent)
        record["extensions"] = {"adapter": {"scope": "parent"}}
        for p in record["paths"]:
            p["extensions"] = {"adapter": {"path": p["path_ids"][0]}}
        for s in FlowSegmenter().segment(record, self.policy):
            self.assertEqual(s["extensions"], record["extensions"])
            self.assertTrue(all(p["extensions"]["adapter"]["path"] in s["included_paths"] for p in s["paths"]))

    def test_single_oversized_path_explicit(self):
        with self.assertRaisesRegex(SegmentationError, "SINGLE_PATH_OVERSIZED"):
            FlowSegmenter().segment(parent(1, 8000), self.policy)

    def test_one_oversized_atomic_path_aborts_plan(self):
        record = deepcopy(self.parent)
        record["paths"][-1]["nodes"][0]["caller"] = "x" * 10000
        with self.assertRaisesRegex(SegmentationError, "SINGLE_PATH_OVERSIZED"):
            FlowSegmenter().segment(record, self.policy)

    def test_metadata_budget_impossible(self):
        with self.assertRaisesRegex(SegmentationError, "BUDGET_IMPOSSIBLE_AFTER_SEGMENTATION"):
            FlowSegmenter().segment(self.parent, self.policy, lambda _: False)

    def test_tampering_rejected(self):
        for key, value in [("partial", False), ("parent_flow_id", "FLOW-OTHER"), ("omitted_paths", []), ("included_paths", ["UNKNOWN"]), ("evidence_refs", ["UNKNOWN"]), ("ordinal", 999), ("segment_id", "SEG-fake"), ("unresolved", []), ("completeness", "COMPLETE")]:
            altered = deepcopy(self.segments[0]);altered[key] = value
            with self.subTest(key=key), self.assertRaises(SegmentationError):
                validate_segment(altered, self.parent, self.policy)

    def test_duplicate_or_missing_path_provenance_rejected(self):
        for edit in (lambda r: r["paths"].append(deepcopy(r["paths"][0])), lambda r: r["paths"][0].pop("path_provenance")):
            altered = deepcopy(self.parent);edit(altered)
            with self.assertRaisesRegex(SegmentationError, "INCOMPLETE_PROVENANCE"):
                FlowSegmenter().segment(altered, self.policy)

    def test_invalid_policy_and_partial_parent(self):
        for values in ({"max_characters": 0}, {"input_token_limit": True}, {"overlap": "YES"}, {"ordering": "AI"}):
            with self.assertRaises(SegmentationError):SegmentationPolicy(**values)
        altered = deepcopy(self.parent);altered["partial"] = True
        with self.assertRaisesRegex(SegmentationError, "INVALID_PARENT_FLOW"):
            FlowSegmenter().segment(altered, self.policy)

    def test_deduplicated_original_path_ids_remain_atomic(self):
        ix = indexes()
        duplicate = deepcopy(ix["functional_paths"][0]);duplicate["path_id"] = "PATH-EXTRA"
        ix["functional_paths"].append(duplicate)
        record = EvidenceHydrator().hydrate_flow("FLOW-SYN", ix)
        groups = FlowSegmenter().segment(record, self.policy)
        for s in groups:
            self.assertEqual("PATH-0000" in s["included_paths"], "PATH-EXTRA" in s["included_paths"])
            validate_segment(s, record, self.policy)

    def test_parameters_data_operations_and_unresolved_are_selected_only(self):
        record = deepcopy(self.parent)
        record["parameters"] = [{"caller": p["nodes"][0]["caller"], "names": ["p"]} for p in record["paths"]]
        for s in FlowSegmenter().segment(record, self.policy):
            callers = {n["caller"] for p in s["paths"] for n in p["nodes"]}
            self.assertTrue(all(p["caller"] in callers for p in s["parameters"]))
            nodes = {n["id"] for p in s["paths"] for n in p["nodes"]}
            self.assertTrue(all(op["id"] in nodes for op in s["data_operations"]))

    def test_partial_requires_boolean_true(self):
        altered = deepcopy(self.segments[0]);altered["partial"] = 1
        with self.assertRaises(SegmentationError):validate_segment(altered, self.parent, self.policy)

    def test_segmentation_source_and_policy_do_not_change_analyzer_fingerprint(self):
        from legacy_documenter.fingerprints import analyzer_code_fingerprint
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "legacy_documenter"
            shutil.copytree(ROOT / "legacy_documenter", copied, ignore=shutil.ignore_patterns("__pycache__"))
            before = analyzer_code_fingerprint(copied)
            path = copied / "context/flow_segmentation.py"
            path.write_text(path.read_text(encoding="utf-8") + "\n# different projection policy implementation\n", encoding="utf-8")
            self.assertEqual(before, analyzer_code_fingerprint(copied))


class SegmentedAiTests(unittest.TestCase):
    def test_small_package_and_request_byte_contract_unchanged(self):
        ix = indexes(1)
        package, request, metrics, rejection = _build_within_budget(ix, "s", ["FLOW-SYN"], "SMALL", 16000)
        expected = AiProjectionBuilder().build(["FLOW-SYN"], ix, source_snapshot="s", profile="SMALL")
        self.assertEqual(package, expected)
        self.assertEqual(request, _build_request(expected))
        self.assertNotIn("segmentation", metrics)
        self.assertIsNone(rejection)

    def test_segment_package_explicit_partial_and_under_input_limit(self):
        package, request, metrics, rejection = _build_within_budget(indexes(), "s", ["FLOW-SYN"], "SMALL", 16000)
        self.assertEqual(package["contract_name"], "AI_SEGMENT_PROJECTION")
        self.assertEqual(package["statistics"]["completeness"], "PARTIAL")
        self.assertTrue(request.metadata["flow_segment"]["partial"])
        self.assertIn("PARTIAL FLOW SEGMENT", request.system_instruction)
        self.assertLessEqual(measure_request_payload(request, FINDING_SCHEMA)["payload_estimated_tokens"], 16000)
        self.assertTrue(package["segmentation"]["omitted_paths"])
        self.assertIsNone(rejection)

    def test_explicit_ordinal_different_package_and_identity(self):
        ix = indexes()
        first = _build_within_budget(ix, "s", ["FLOW-SYN"], "SMALL", 16000, segment_ordinal=1)
        second = _build_within_budget(ix, "s", ["FLOW-SYN"], "SMALL", 16000, segment_ordinal=2)
        self.assertNotEqual(first[0]["package_id"], second[0]["package_id"])
        self.assertNotEqual(first[1].request_id, second[1].request_id)

    def test_omitted_paths_do_not_expand_grounding(self):
        package, *_ = _build_within_budget(indexes(), "s", ["FLOW-SYN"], "SMALL", 16000)
        self.assertTrue(set(package["segmentation"]["omitted_paths"]).isdisjoint(package_reference_ids(package)))

    def test_fake_segmented_productive_proposals_pending_and_scoped(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp);output_fixture(out, indexes());provider = fake()
            with patch("legacy_documenter.orchestration.ai_interpretation._resolve_provider", side_effect=AssertionError("real forbidden")):
                result = run_ai_interpretation(out, provider, flow_ids=["FLOW-SYN"])
            self.assertEqual(result.status, "SUCCESS")
            self.assertEqual(len(provider.requests), 1)
            self.assertTrue(provider.closed)
            self.assertTrue(result.findings[0]["flow_segment"]["partial"])
            proposals = adapt_findings_to_proposals(result.findings)
            self.assertTrue(proposals[0].statement.startswith("Partial segment SEG-"))
            self.assertEqual(proposals[0].metadata["flow_segment"]["parent_flow_id"], "FLOW-SYN")
            self.assertEqual(_write_proposal_output(out, result, proposals), "PENDING_TECHNICAL_LEAD_REVIEW")
            md = (out / "proposals/AI_PROPOSALS_PENDING_REVIEW.md").read_text()
            self.assertIn("**PARTIAL**", md)
            self.assertFalse((out / "canonical").exists())

    def test_provider_cannot_supply_scope_or_cite_omitted_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp);output_fixture(out, indexes());provider = fake()
            provider.structured["findings"][0]["evidence_refs"] = ["PATH-0029"]
            result = run_ai_interpretation(out, provider, flow_ids=["FLOW-SYN"])
            self.assertEqual(result.status, "INVALID_OUTPUT")
            self.assertEqual(result.findings, [])

    def test_aicfg_changes_segment_request_identity_not_segment_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp);output_fixture(out, indexes())
            a, b = fake("A"), fake("B")
            run_ai_interpretation(out, a, flow_ids=["FLOW-SYN"])
            run_ai_interpretation(out, b, flow_ids=["FLOW-SYN"])
            self.assertEqual(a.requests[0].context["segmentation"]["segment_id"], b.requests[0].context["segmentation"]["segment_id"])
            self.assertNotEqual(a.requests[0].request_id, b.requests[0].request_id)

    def test_impossible_budget_deterministic_error_no_call_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp);output_fixture(out, indexes());provider = fake(window=2200)
            result = run_ai_interpretation(out, provider, flow_ids=["FLOW-SYN"])
            self.assertEqual(result.status, "CONTEXT_TOO_LARGE")
            self.assertFalse(result.provider_called)
            self.assertEqual(provider.requests, [])
            self.assertTrue(provider.closed)
            self.assertEqual(result.failure_category, "BUDGET_IMPOSSIBLE_AFTER_SEGMENTATION")

    def test_invalid_segment_selection_no_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp);output_fixture(out, indexes());provider = fake()
            result = run_ai_interpretation(out, provider, flow_ids=["FLOW-SYN"], segment_ordinal=999)
            self.assertFalse(result.provider_called)
            self.assertEqual(result.failure_category, "INVALID_SEGMENT")

    def test_architecture_no_concrete_technology_or_provider(self):
        for name in ("context/flow_segmentation.py", "orchestration/segmented_context.py"):
            tree = ast.parse((ROOT / "legacy_documenter" / name).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                imports = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""] if isinstance(node, ast.ImportFrom) else []
                self.assertFalse(any(word in name.lower() for name in imports for word in ("copilot", "oracle", "webforms", "providers")))


if __name__ == "__main__":unittest.main()
