"""V4.3-R6 -- AI integration and consumer projection: verification tests.

Covers, per `prompts/V4_3/V4_3_R6_AI_AND_CONSUMER_PROJECTION.md` and its
post-implementation scalability correction:

1. `legacy_documenter.context.consumer_projection` builds a small
   `LegacyMapperConsumerProjection 1.0` manifest (`CPJ-` prefix) plus a
   deterministic, complete set of self-contained partitions -- independent
   of `ai_projection`/`human_documentation`/`llm`, with
   `SILENT_ENTRY_OMISSION` forbidden and no data loss from partitioning.
2. Both are materialized to disk (`consumer_projection/CONSUMER_PROJECTION.json`
   + `consumer_projection/parts/part-NNNNNN.json`) as part of the existing,
   always-run CONTEXT stage -- for both `analyze` and `full`, never opt-in,
   never touching a provider -- with stale partitions from an earlier, larger
   run removed on rerun.
3. The pre-existing AI integration invariants (findings cite included
   evidence, AI synthesis is never `CONFIRMED`, proposals are
   `READY_FOR_REVIEW`, AI failure never invalidates deterministic
   documentation or `consumer_projection`) hold end-to-end in one real run.

REAL_AI_RUNTIME_CALL_ALLOWED=false: every test here injects
`legacy_documenter.llm.core.FakeLLMProvider` explicitly -- no test reaches
`_resolve_provider`/`ProviderRegistry` with a real `provider_type`.
"""
from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path

from legacy_documenter.cli.full_pipeline import run_full_pipeline
from legacy_documenter.context import consumer_projection as cpj
from legacy_documenter.knowledge.proposals.enums import ProposalMethod, ProposalStatus
from legacy_documenter.llm.core import FakeLLMProvider, ProviderConfig
from legacy_documenter.main import analyze_repository

ROOT = Path(__file__).parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "v4_2_r3_sample"

VALID_STRUCTURED_RESPONSE = {
    "findings": [
        {"statement": "The Save button reaches a stored procedure.", "confidence": "CONFIRMED",
         "evidence_refs": ["DAO-0197413858"]}
    ]
}


def _synthetic_ix(flow_count: int = 2, confidence: str = "confirmed") -> dict:
    """A minimal `ix` indexes dict of the exact shape `EvidenceHydrator` consumes."""
    flows, entry_points, paths = [], [], []
    for index in range(flow_count):
        flow_id = f"FLOW-{index:04d}"
        entry_id = f"EP-{index:04d}"
        flows.append({"id": flow_id, "entry_point_id": entry_id, "confidence": confidence, "project_sequence": ["P"]})
        entry_points.append({
            "id": entry_id, "webform": f"web\\form{index}.ascx", "event": "Click",
            "handler": f"btn{index}_Click", "start_method": f"Start{index}",
        })
        paths.append({
            "path_id": f"PATH-{index:04d}", "flow_id": flow_id, "entry_point_id": entry_id, "nodes": ["DAO-1"],
            "terminal_type": "stored_procedure", "terminal_target": "SP-1",
            "confidence": confidence, "evidence_refs": [f"CALL-{index:04d}"],
        })
    return {
        "functional_flows": flows, "entry_points": entry_points, "functional_paths": paths,
        "data_access": [{"id": "DAO-1", "class": "Repo", "method": "Save",
                         "operation_kind": "stored_procedure", "confidence": "confirmed"}],
        "stored_procedures": [{"id": "SP-1", "name": "PKG.SAVE", "package": "PKG", "procedure": "SAVE"}],
        "sql_operations": [], "data_parameters": [],
    }


def _all_partition_flow_ids(partitions: dict[str, dict]) -> list[str]:
    return [record["flow_id"] for body in partitions.values() for record in body["records"]]


class ManifestContractTests(unittest.TestCase):
    """The manifest must match the V4.3-R1 section 5.3 contract and stay small."""

    def setUp(self) -> None:
        self.ix = _synthetic_ix(2)
        self.builder = cpj.ConsumerProjectionBuilder()

    def test_manifest_package_id_uses_the_cpj_prefix(self) -> None:
        manifest, _ = self.builder.build(self.ix)
        self.assertTrue(manifest["package_id"].startswith("CPJ-"))
        self.assertEqual(len(manifest["package_id"]), len("CPJ-") + 64)

    def test_manifest_declares_the_contract_name_and_version(self) -> None:
        manifest, _ = self.builder.build(self.ix)
        self.assertEqual(manifest["contract_name"], "LegacyMapperConsumerProjection")
        self.assertEqual(manifest["contract_version"], "1.0")

    def test_manifest_carries_source_snapshot(self) -> None:
        manifest, _ = self.builder.build(self.ix, source_snapshot="abc123")
        self.assertEqual(manifest["source_snapshot"], "abc123")

    def test_manifest_declares_completeness_and_totals(self) -> None:
        manifest, _ = self.builder.build(self.ix)
        self.assertEqual(manifest["statistics"]["completeness"], "COMPLETE")
        self.assertEqual(manifest["statistics"]["flow_count"], 2)
        self.assertEqual(manifest["statistics"]["path_count"], 2)

    def test_manifest_declares_the_partitioning_strategy(self) -> None:
        manifest, _ = self.builder.build(self.ix)
        self.assertEqual(manifest["partitioning"]["strategy"], "FIXED_SIZE_BY_FLOW_COUNT")
        self.assertIn("partition_size", manifest["partitioning"])
        self.assertEqual(manifest["partitioning"]["partition_count"], len(manifest["partitions"]))

    def test_manifest_lists_each_partition_id_flow_count_and_path(self) -> None:
        manifest, partitions = self.builder.build(self.ix)
        entry = manifest["partitions"][0]
        for key in ("index", "relative_path", "partition_id", "flow_count"):
            self.assertIn(key, entry)
        self.assertIn(entry["relative_path"], partitions)

    def test_manifest_has_no_records_field(self) -> None:
        manifest, _ = self.builder.build(self.ix)
        self.assertNotIn("records", manifest)

    def test_manifest_is_deterministic(self) -> None:
        first, _ = self.builder.build(self.ix)
        second, _ = self.builder.build(self.ix)
        self.assertEqual(first, second)

    def test_manifest_package_id_changes_when_content_changes(self) -> None:
        one, _ = self.builder.build(self.ix, flow_ids=["FLOW-0000"])
        two, _ = self.builder.build(self.ix, flow_ids=["FLOW-0000", "FLOW-0001"])
        self.assertNotEqual(one["package_id"], two["package_id"])


class PartitioningLosslessnessTests(unittest.TestCase):
    """Partitioning bounds file size only, never content: union == source, intersection == empty."""

    def test_zero_flows_produces_an_empty_but_valid_manifest(self) -> None:
        ix = {"functional_flows": [], "entry_points": [], "functional_paths": [],
              "data_access": [], "stored_procedures": [], "sql_operations": [], "data_parameters": []}
        manifest, partitions = cpj.ConsumerProjectionBuilder().build(ix)
        self.assertEqual(manifest["statistics"]["flow_count"], 0)
        self.assertEqual(manifest["statistics"]["completeness"], "COMPLETE")
        self.assertEqual(manifest["partitions"], [])
        self.assertEqual(partitions, {})

    def test_one_flow_produces_exactly_one_partition(self) -> None:
        manifest, partitions = cpj.ConsumerProjectionBuilder().build(_synthetic_ix(1))
        self.assertEqual(len(manifest["partitions"]), 1)
        self.assertEqual(len(partitions), 1)

    def test_more_flows_than_partition_size_produces_multiple_partitions(self) -> None:
        manifest, partitions = cpj.ConsumerProjectionBuilder(partition_size=3).build(_synthetic_ix(10))
        self.assertEqual(manifest["partitioning"]["partition_count"], 4)  # 3+3+3+1
        self.assertEqual(len(partitions), 4)

    def test_every_flow_appears_in_the_partitions_union(self) -> None:
        ix = _synthetic_ix(10)
        _, partitions = cpj.ConsumerProjectionBuilder(partition_size=3).build(ix)
        expected = {f["id"] for f in ix["functional_flows"]}
        self.assertEqual(set(_all_partition_flow_ids(partitions)), expected)

    def test_no_flow_is_duplicated_across_partitions(self) -> None:
        ix = _synthetic_ix(10)
        _, partitions = cpj.ConsumerProjectionBuilder(partition_size=3).build(ix)
        ids = _all_partition_flow_ids(partitions)
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_flow_is_silently_omitted(self) -> None:
        ix = _synthetic_ix(10)
        _, partitions = cpj.ConsumerProjectionBuilder(partition_size=3).build(ix)
        self.assertEqual(len(_all_partition_flow_ids(partitions)), 10)

    def test_unknown_flow_id_fails_closed_rather_than_silently_omitting(self) -> None:
        from legacy_documenter.context.hydration import UnknownFlowError
        with self.assertRaises(UnknownFlowError):
            cpj.ConsumerProjectionBuilder().build(_synthetic_ix(1), flow_ids=["FLOW-9999"])

    def test_duplicate_records_passed_to_package_are_rejected(self) -> None:
        from legacy_documenter.context.hydration import EvidenceHydrator
        ix = _synthetic_ix(1)
        record = EvidenceHydrator().hydrate_flow("FLOW-0000", ix)
        with self.assertRaises(cpj.ConsumerProjectionError):
            cpj.ConsumerProjectionBuilder().package([record, dict(record)])


class DeterministicNamingAndHashingTests(unittest.TestCase):
    """Names, order, and hashes must be deterministic."""

    def test_partition_filenames_are_zero_padded_and_ascending(self) -> None:
        manifest, partitions = cpj.ConsumerProjectionBuilder(partition_size=1).build(_synthetic_ix(3))
        paths = [entry["relative_path"] for entry in manifest["partitions"]]
        self.assertEqual(paths, ["parts/part-000000.json", "parts/part-000001.json", "parts/part-000002.json"])
        self.assertEqual(set(paths), set(partitions))

    def test_partition_order_matches_flow_id_ascending(self) -> None:
        ix = _synthetic_ix(4)
        manifest, partitions = cpj.ConsumerProjectionBuilder(partition_size=2).build(ix)
        first_partition = partitions[manifest["partitions"][0]["relative_path"]]
        self.assertEqual([r["flow_id"] for r in first_partition["records"]], ["FLOW-0000", "FLOW-0001"])

    def test_partition_ids_are_deterministic_across_builds(self) -> None:
        ix = _synthetic_ix(5)
        manifest_a, _ = cpj.ConsumerProjectionBuilder(partition_size=2).build(ix)
        manifest_b, _ = cpj.ConsumerProjectionBuilder(partition_size=2).build(ix)
        self.assertEqual(
            [p["partition_id"] for p in manifest_a["partitions"]],
            [p["partition_id"] for p in manifest_b["partitions"]],
        )

    def test_partition_id_changes_when_that_partitions_content_changes(self) -> None:
        ix_a, ix_b = _synthetic_ix(1), _synthetic_ix(1)
        ix_b["functional_flows"][0]["confidence"] = "unresolved"
        manifest_a, _ = cpj.ConsumerProjectionBuilder().build(ix_a)
        manifest_b, _ = cpj.ConsumerProjectionBuilder().build(ix_b)
        self.assertNotEqual(manifest_a["partitions"][0]["partition_id"], manifest_b["partitions"][0]["partition_id"])


class ManifestPointsOnlyAtRealPartitionsTests(unittest.TestCase):
    def test_every_manifest_entry_has_a_matching_partition(self) -> None:
        manifest, partitions = cpj.ConsumerProjectionBuilder(partition_size=3).build(_synthetic_ix(10))
        for entry in manifest["partitions"]:
            self.assertIn(entry["relative_path"], partitions)

    def test_no_partition_exists_without_a_manifest_entry(self) -> None:
        manifest, partitions = cpj.ConsumerProjectionBuilder(partition_size=3).build(_synthetic_ix(10))
        listed = {entry["relative_path"] for entry in manifest["partitions"]}
        self.assertEqual(listed, set(partitions))


class PartitionSelfContainmentTests(unittest.TestCase):
    """A consumer must be able to read one partition standalone and reconstruct
    flow -> entry point -> paths -> terminals/evidence/provenance, without any
    LegacyMapper class and without reading another partition."""

    def test_partition_carries_its_own_contract_and_provenance(self) -> None:
        _, partitions = cpj.ConsumerProjectionBuilder().build(_synthetic_ix(1))
        body = next(iter(partitions.values()))
        self.assertEqual(body["contract_name"], "LegacyMapperConsumerProjection")
        self.assertEqual(body["contract_version"], "1.0")
        self.assertIn("source_snapshot", body)
        self.assertIn("provenance", body)

    def test_partition_reconstructs_flow_entry_point_paths_and_terminals(self) -> None:
        _, partitions = cpj.ConsumerProjectionBuilder().build(_synthetic_ix(1))
        record = next(iter(partitions.values()))["records"][0]
        self.assertEqual(record["flow_id"], "FLOW-0000")
        self.assertEqual(record["entry_point"]["handler"], "btn0_Click")
        self.assertEqual(record["terminals"]["stored_procedures"][0]["resolved_name"], "PKG.SAVE")
        self.assertTrue(record["paths"])

    def test_partition_body_is_plain_json_primitives(self) -> None:
        _, partitions = cpj.ConsumerProjectionBuilder().build(_synthetic_ix(1))
        body = next(iter(partitions.values()))
        json.dumps(body)  # raises TypeError if anything is not a JSON primitive

    def test_partition_needs_no_other_partition(self) -> None:
        _, partitions = cpj.ConsumerProjectionBuilder(partition_size=1).build(_synthetic_ix(3))
        for path, body in partitions.items():
            other_records = [r for p, b in partitions.items() if p != path for r in b["records"]]
            other_flow_ids = {r["flow_id"] for r in other_records}
            own_flow_ids = {r["flow_id"] for r in body["records"]}
            # Every record this partition needs to reconstruct flow -> entry
            # point -> paths -> terminals/evidence/provenance is already
            # inside `body` itself; none of its own flow ids appears only in
            # another partition.
            self.assertEqual(own_flow_ids & other_flow_ids, set())
            self.assertTrue(all(key in record for record in body["records"]
                                 for key in ("flow_id", "entry_point", "paths", "terminals", "provenance")))


class RuntimeIndependenceTests(unittest.TestCase):
    """`consumer_projection` stays independent of `ai_projection`/`human_documentation`/`llm`."""

    def test_never_imports_ai_projection_human_documentation_or_llm(self) -> None:
        tree = ast.parse(Path(cpj.__file__).read_text(encoding="utf-8"))
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported += [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        joined = " ".join(imported)
        self.assertNotIn("ai_projection", joined)
        self.assertNotIn("documentation", joined)
        self.assertNotIn("llm", joined)

    def test_never_reads_or_writes_a_file(self) -> None:
        source = Path(cpj.__file__).read_text(encoding="utf-8")
        for token in ("open(", "Path(", "write_text", "read_text"):
            self.assertNotIn(token, source)

    def test_does_not_reimplement_hydration(self) -> None:
        source = Path(cpj.__file__).read_text(encoding="utf-8")
        self.assertIn("from .hydration import", source)
        self.assertNotIn("def hydrate_flow", source)


class PipelineMaterializationTests(unittest.TestCase):
    """`consumer_projection` is materialized deterministically, for both commands."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = cls._tmp.name
        analyze_repository(FIXTURE, cls.out, None, 12)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_analyze_writes_the_manifest_and_at_least_one_partition(self) -> None:
        base = Path(self.out) / "consumer_projection"
        manifest_path = base / "CONSUMER_PROJECTION.json"
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest["partitions"]:
            self.assertTrue((base / entry["relative_path"]).is_file())

    def test_consumer_projection_carries_the_run_source_snapshot(self) -> None:
        manifest = json.loads((Path(self.out) / "consumer_projection" / "CONSUMER_PROJECTION.json")
                               .read_text(encoding="utf-8"))
        context = json.loads((Path(self.out) / "ai_context" / "SYSTEM_CONTEXT.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["source_snapshot"], context["metadata"]["source_snapshot_sha256"])
        partition_path = Path(self.out) / "consumer_projection" / manifest["partitions"][0]["relative_path"]
        partition = json.loads(partition_path.read_text(encoding="utf-8"))
        self.assertEqual(partition["source_snapshot"], manifest["source_snapshot"])

    def test_full_command_also_writes_consumer_projection_without_ai_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12)
            self.assertFalse(result.ai_requested)
            self.assertTrue((Path(out) / "consumer_projection" / "CONSUMER_PROJECTION.json").is_file())


class RerunStalePartitionCleanupTests(unittest.TestCase):
    """A rerun with fewer flows must remove now-stale partition files (V4.2-R6 rerun safety, applied to JSON)."""

    def test_rerun_with_fewer_flows_removes_stale_partitions(self) -> None:
        from legacy_documenter.cli.pipeline_stages import build_context_artifacts

        with tempfile.TemporaryDirectory() as out:
            # `DEFAULT_PARTITION_SIZE` (500) is the real, unpatched default
            # `build_context_artifacts` uses -- crossing it for real (601 vs.
            # 1 flow) proves the rerun-cleanup wiring itself, not a smaller
            # test-only partition size.
            wide_ix = _synthetic_ix(601)
            build_context_artifacts(out, {**wide_ix, "repository": {}, "solutions": [], "projects": [],
                                           "symbols": [], "logical_symbols": [], "calls": [], "webforms": [],
                                           "configuration": [], "dependencies": [], "functional_dependencies": [],
                                           "flow_summary": {}, "flow_unresolved": []})
            parts_dir = Path(out) / "consumer_projection" / "parts"
            with_many = set(p.name for p in parts_dir.glob("*.json"))
            self.assertGreater(len(with_many), 0)

            narrow_ix = _synthetic_ix(1)
            build_context_artifacts(out, {**narrow_ix, "repository": {}, "solutions": [], "projects": [],
                                           "symbols": [], "logical_symbols": [], "calls": [], "webforms": [],
                                           "configuration": [], "dependencies": [], "functional_dependencies": [],
                                           "flow_summary": {}, "flow_unresolved": []})
            with_few = set(p.name for p in parts_dir.glob("*.json"))
            self.assertLess(len(with_few), len(with_many))
            manifest = json.loads((Path(out) / "consumer_projection" / "CONSUMER_PROJECTION.json")
                                   .read_text(encoding="utf-8"))
            self.assertEqual({Path(e["relative_path"]).name for e in manifest["partitions"]}, with_few)


class ManifestStaysSmallAtScaleTests(unittest.TestCase):
    """Synthetic-scale proof: the manifest stays small and detail spreads across
    many files as the flow count grows (V4.3-R6 correction requirement 10)."""

    def test_manifest_size_is_near_constant_while_partition_count_grows(self) -> None:
        small_manifest, small_partitions = cpj.ConsumerProjectionBuilder(partition_size=50).build(_synthetic_ix(50))
        large_manifest, large_partitions = cpj.ConsumerProjectionBuilder(partition_size=50).build(_synthetic_ix(2000))

        small_bytes = len(json.dumps(small_manifest))
        large_bytes = len(json.dumps(large_manifest))
        self.assertEqual(len(small_partitions), 1)
        self.assertEqual(len(large_partitions), 40)
        # 40x more flows and 40x more partitions, but the manifest itself
        # (one small entry per partition, not per flow/path) grows far less
        # than proportionally to the flow count.
        self.assertLess(large_bytes, small_bytes * 40)
        self.assertLess(large_bytes, 20_000)

    def test_no_single_partition_holds_every_flow_at_scale(self) -> None:
        manifest, partitions = cpj.ConsumerProjectionBuilder(partition_size=50).build(_synthetic_ix(2000))
        self.assertEqual(manifest["statistics"]["flow_count"], 2000)
        self.assertTrue(all(len(body["records"]) <= 50 for body in partitions.values()))
        self.assertEqual(sum(len(body["records"]) for body in partitions.values()), 2000)


class AiFailureDoesNotInvalidateDeterministicOutputTests(unittest.TestCase):
    """AI failure must never invalidate deterministic documentation or `consumer_projection`
    (V4.3-R6 prompt: "fallo AI no invalida documentación determinista")."""

    def test_ai_failure_leaves_documentation_and_consumer_projection_intact(self) -> None:
        failing_provider = FakeLLMProvider(
            ProviderConfig("FAKE", "f", "m", capabilities={"structured_output": True}),
            forced_status="PROVIDER_ERROR",
        )
        with tempfile.TemporaryDirectory() as out:
            result = run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=failing_provider)
            stage_status = {stage.stage.value: stage.status.value for stage in result.stages}
            self.assertEqual(stage_status["DOCUMENTATION"], "SUCCESS")
            self.assertEqual(stage_status["AI_INTERPRETATION"], "FAILED")
            self.assertTrue((Path(out) / "documentation").is_dir())
            self.assertTrue((Path(out) / "consumer_projection" / "CONSUMER_PROJECTION.json").is_file())
            self.assertEqual(result.status.value, "PARTIAL")


class AiIntegrationInvariantTests(unittest.TestCase):
    """Re-verifies the R6 prompt's `IA` invariants end-to-end in one real run
    (most already implemented and tested individually at V4.2-R4/V4.3-R5;
    this class certifies they still hold together)."""

    def test_proposals_are_ready_for_review_and_ai_proposed(self) -> None:
        provider = FakeLLMProvider(
            ProviderConfig("FAKE", "f", "m", capabilities={"structured_output": True}),
            structured_response=VALID_STRUCTURED_RESPONSE,
        )
        with tempfile.TemporaryDirectory() as out:
            run_full_pipeline(FIXTURE, out, None, 12, allow_ai_interpretation=True, ai_provider=provider)
            proposals = json.loads((Path(out) / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8"))
            self.assertEqual(proposals["proposals"][0]["status"], ProposalStatus.READY_FOR_REVIEW.value)
            self.assertEqual(proposals["proposals"][0]["proposal_method"], ProposalMethod.AI_PROPOSED.value)
            self.assertNotEqual(proposals["proposals"][0]["status"], "APPROVED")

    def test_findings_must_cite_evidence_actually_included_in_the_package(self) -> None:
        from legacy_documenter.orchestration import ai_interpretation as ai
        with tempfile.TemporaryDirectory() as out:
            analyze_repository(FIXTURE, out, None, 12)
            unknown_ref_provider = FakeLLMProvider(
                ProviderConfig("FAKE", "f", "m", capabilities={"structured_output": True}),
                structured_response={"findings": [
                    {"statement": "x", "confidence": "CONFIRMED", "evidence_refs": ["NOT-IN-PACKAGE"]}
                ]},
            )
            result = ai.run_ai_interpretation(out, provider=unknown_ref_provider)
            self.assertEqual(result.status, "INVALID_OUTPUT")

    def test_unresolved_evidence_is_preserved_in_the_consumer_projection(self) -> None:
        ix = _synthetic_ix(1, confidence="unresolved")
        ix["functional_paths"][0]["terminal_type"] = "unresolved_boundary"
        ix["functional_paths"][0]["terminal_target"] = "UNRESOLVED-1"
        _, partitions = cpj.ConsumerProjectionBuilder().build(ix)
        record = next(iter(partitions.values()))["records"][0]
        self.assertEqual(record["confidence"], "unresolved")
        self.assertIn("PATH-0000", record["unresolved"])


if __name__ == "__main__":
    unittest.main()
