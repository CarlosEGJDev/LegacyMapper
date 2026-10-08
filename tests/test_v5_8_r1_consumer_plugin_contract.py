"""V5.8-R1: Consumer Contract + Plugin Contract (declarative, read-only, no plugin runtime, no provider)."""
from __future__ import annotations

import ast
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from legacy_documenter.consumers import facade as facade_module
from legacy_documenter.consumers.contracts import (
    CAPABILITY_SPECS, CONTRACT_VERSION, ConsumerCapability, ConsumerDescriptor, ConsumerError, ConsumerErrorCode,
    ConsumerRequest, negotiate_contract_version,
)
from legacy_documenter.consumers.facade import HUMAN_DOC_DIRECTORIES, ConsumerFacade
from legacy_documenter.consumers.registry import ConsumerRegistry, builtin_registry
from legacy_documenter.context.consumer_projection import ConsumerProjectionBuilder
from legacy_documenter.fingerprints import analyzer_code_fingerprint
from legacy_documenter.plugins.validation import descriptor_from_manifest, register_manifests, validate_manifest
from legacy_documenter.review.service import ApprovalService
from legacy_documenter.versions import ANALYZER_VERSION
from tests.test_v5_7_r1_human_review import build_run, tree_hash

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "legacy_documenter"
CONTRACT_PACKAGES = ("consumers", "plugins")
FIXED = lambda: "2026-10-08T12:00:00Z"  # noqa: E731
BUILTIN = {
    "evidence": "builtin.evidence-reader", "flow": "builtin.flow-reader", "ai": "builtin.ai-context",
    "canonical": "builtin.canonical-reader", "review": "builtin.review-history-reader", "docs": "builtin.human-docs",
    "export": "builtin.json-export",
}


def request(consumer: str, capability: str, scope: str = "ENTITIES", ids=(), profile=None, options=None, version="1.0") -> dict:
    data = {"consumer_id": consumer, "contract_version": version, "capability": capability, "scope": scope, "entity_ids": list(ids)}
    if profile is not None:
        data["profile"] = profile
    if options is not None:
        data["options"] = options
    return data


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_full_run(root: Path) -> dict:
    """Index (all seven files, three distinct paths), proposals, human docs and consumer_projection."""
    ids = build_run(root)
    for name in ("sql_operations", "stored_procedures", "data_parameters"):
        (root / "index" / f"{name}.json").write_text("[]", encoding="utf-8")
    docs = {"general/README.md": "# General\nfunctional overview\n", "general/system.md": "# System\n",
            "developer/README.md": "# Developer\n", "developer/modules.md": "# Modules\n", "README.md": "# Root\n"}
    for relative, text in docs.items():
        target = root / "documentation_v52" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))
    manifest = {"contract": "LegacyMapperDocumentationV52", "file_count": len(docs), "files": [
        {"path": p, "sha256": sha(t), "size_bytes": len(t.encode())} for p, t in sorted(docs.items())]}
    (root / "documentation_v52" / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    ix = {n: json.loads((root / "index" / f"{n}.json").read_text(encoding="utf-8")) for n in (
        "functional_flows", "functional_paths", "entry_points", "data_access", "sql_operations", "stored_procedures", "data_parameters")}
    projection, parts = ConsumerProjectionBuilder(partition_size=1).build(ix)
    out = root / "consumer_projection"
    (out / "parts").mkdir(parents=True)
    (out / "CONSUMER_PROJECTION.json").write_text(json.dumps(projection), encoding="utf-8")
    for relative, body in parts.items():
        (out / relative).write_text(json.dumps(body), encoding="utf-8")
    return ids


class ContractTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.run_dir = self.tmp / "run"
        self.ids = build_full_run(self.run_dir)
        self.facade = ConsumerFacade(self.run_dir)

    def ask(self, key: str, capability: str, *args, **kwargs):
        return self.facade.handle(request(BUILTIN[key], capability, *args, **kwargs))

    def approve(self, name: str = "approve") -> str:
        service = ApprovalService(self.run_dir, clock=FIXED)
        service.prepare(self.ids[name], "Ana Reviewer")
        return service.decide(self.ids[name], "APPROVE", "Ana Reviewer", rationale="ok").canonical.canonical_id

    def assertError(self, result, code: ConsumerErrorCode) -> None:
        self.assertEqual(result.status, "ERROR", result.to_dict())
        self.assertEqual(result.error["code"], code.value, result.error)
        self.assertIsNone(result.payload)
        self.assertNotIn("Traceback", result.to_json())


class DescriptorTests(unittest.TestCase):
    VALID = {
        "consumer_id": "acme.reader", "consumer_version": "1.2.0", "contract_version": "1.0", "capabilities_required": ["READ_FLOW", "READ_EVIDENCE"],
        "input_kinds": ["FLOW_ID"], "output_kinds": ["FLOW_RECORD"], "read_only": True,
    }

    def test_valid_descriptor_is_normalized_and_roundtrips(self) -> None:
        descriptor = ConsumerDescriptor.from_dict(self.VALID)
        self.assertEqual([c.value for c in descriptor.capabilities_required], ["READ_EVIDENCE", "READ_FLOW"])
        self.assertTrue(descriptor.read_only)
        self.assertEqual(ConsumerDescriptor.from_dict(descriptor.to_dict()), descriptor)

    def test_invalid_descriptors_fail_closed(self) -> None:
        cases = {
            "unknown_key": ({**self.VALID, "extra": 1}, ConsumerErrorCode.INVALID_DESCRIPTOR),
            "missing_key": ({k: v for k, v in self.VALID.items() if k != "input_kinds"}, ConsumerErrorCode.INVALID_DESCRIPTOR),
            "bad_id": ({**self.VALID, "consumer_id": "Bad Id"}, ConsumerErrorCode.INVALID_DESCRIPTOR),
            "bad_version": ({**self.VALID, "contract_version": "one"}, ConsumerErrorCode.INVALID_DESCRIPTOR),
            "unknown_capability": ({**self.VALID, "capabilities_required": ["READ_EVERYTHING"]}, ConsumerErrorCode.UNSUPPORTED_CAPABILITY),
            "write_capability": ({**self.VALID, "capabilities_required": ["APPROVE_PROPOSAL"]}, ConsumerErrorCode.READ_ONLY_VIOLATION),
            "not_read_only": ({**self.VALID, "read_only": False}, ConsumerErrorCode.READ_ONLY_VIOLATION),
            "unknown_kind": ({**self.VALID, "input_kinds": ["SECRET"]}, ConsumerErrorCode.INVALID_DESCRIPTOR),
            "empty_capabilities": ({**self.VALID, "capabilities_required": []}, ConsumerErrorCode.INVALID_DESCRIPTOR),
        }
        for name, (data, code) in cases.items():
            with self.subTest(name), self.assertRaises(ConsumerError) as ctx:
                ConsumerDescriptor.from_dict(data)
            self.assertEqual(ctx.exception.code, code)

    def test_registry_is_immutable_sorted_and_rejects_duplicates(self) -> None:
        base = builtin_registry()
        extra = ConsumerDescriptor.from_dict(self.VALID)
        grown = base.with_descriptors(extra)
        self.assertEqual(len(base), 7)
        self.assertEqual(len(grown), 8)
        self.assertEqual(list(grown.ids()), sorted(grown.ids()))
        with self.assertRaises(ConsumerError) as ctx:
            grown.with_descriptors(extra)
        self.assertEqual(ctx.exception.code, ConsumerErrorCode.INVALID_DESCRIPTOR)
        self.assertEqual(base.to_dict(), builtin_registry().to_dict())
        with self.assertRaises(ConsumerError):
            ConsumerRegistry().get("nobody")

    def test_builtin_descriptors_cover_every_capability_with_spec_kinds(self) -> None:
        granted = {c for did in builtin_registry().ids() for c in builtin_registry().get(did).capabilities_required}
        self.assertEqual(granted, set(ConsumerCapability))
        for did in builtin_registry().ids():
            descriptor = builtin_registry().get(did)
            specs = [CAPABILITY_SPECS[c] for c in descriptor.capabilities_required]
            self.assertEqual(set(descriptor.output_kinds), {k for s in specs for k in s.output_kinds})

    def test_version_negotiation(self) -> None:
        self.assertEqual(negotiate_contract_version("1.0"), "1.0")
        self.assertEqual(negotiate_contract_version("1.7"), "1.0")  # minor is additive: resolves to the supported minor
        for bad in ("2.0", "0.9", "1", "x.y", None, 1.0):
            with self.subTest(bad), self.assertRaises(ConsumerError):
                negotiate_contract_version(bad)


class RequestTests(ContractTestCase):
    def test_unknown_consumer_and_versions(self) -> None:
        self.assertError(self.facade.handle(request("ghost.reader", "READ_FLOW", ids=["FLOW-1"])), ConsumerErrorCode.UNKNOWN_CONSUMER)
        self.assertError(self.ask("flow", "READ_FLOW", ids=["FLOW-1"], version="2.0"), ConsumerErrorCode.UNSUPPORTED_CONTRACT_VERSION)
        self.assertError(self.ask("flow", "READ_FLOW", ids=["FLOW-1"], version="abc"), ConsumerErrorCode.INVALID_REQUEST)
        self.assertTrue(self.ask("flow", "READ_FLOW", ids=["FLOW-1"], version="1.9").ok)

    def test_capability_rules(self) -> None:
        self.assertError(self.ask("flow", "READ_EVERYTHING", ids=["FLOW-1"]), ConsumerErrorCode.UNSUPPORTED_CAPABILITY)
        self.assertError(self.ask("flow", "READ_EVIDENCE", ids=["FLOW-1"]), ConsumerErrorCode.UNSUPPORTED_CAPABILITY)  # not granted
        for write in ("APPROVE_PROPOSAL", "WRITE_EVIDENCE", "CREATE_CANONICAL", "MODIFY_CACHE", "INVOKE_PROVIDER", "EXECUTE_PLUGIN"):
            with self.subTest(write):
                self.assertError(self.ask("flow", write, ids=["FLOW-1"]), ConsumerErrorCode.READ_ONLY_VIOLATION)

    def test_scope_and_shape_validation(self) -> None:
        self.assertError(self.ask("flow", "READ_FLOW", scope="ENTITIES", ids=[]), ConsumerErrorCode.INVALID_SCOPE)
        self.assertError(self.ask("flow", "READ_FLOW", scope="RUN"), ConsumerErrorCode.INVALID_SCOPE)
        self.assertError(self.ask("flow", "READ_FLOW", scope="GALAXY", ids=["FLOW-1"]), ConsumerErrorCode.INVALID_SCOPE)
        self.assertError(self.ask("canonical", "READ_CANONICAL", scope="RUN", ids=["CAN-1"]), ConsumerErrorCode.INVALID_SCOPE)
        self.assertError(self.ask("flow", "READ_FLOW", ids=[f"FLOW-{i}" for i in range(51)]), ConsumerErrorCode.INVALID_SCOPE)
        for bad in ({}, {"consumer_id": "x"}, {**request(BUILTIN["flow"], "READ_FLOW", ids=["FLOW-1"]), "code": "print(1)"}, "READ_FLOW", None):
            with self.subTest(str(bad)[:30]):
                self.assertError(self.facade.handle(bad), ConsumerErrorCode.INVALID_REQUEST)

    def test_requests_cannot_carry_code_or_unknown_options(self) -> None:
        for options in ({"callback": lambda: 1}, {"nested": {"a": 1}}, {"items": [1]}, {"x": 1.5}, {"max_characters": "9"}, {"unknown": 1}):
            with self.subTest(str(options)):
                result = self.ask("flow", "READ_PARTIAL_FLOW", ids=["FLOW-1"], options=options)
                self.assertEqual(result.status, "ERROR")
                self.assertEqual(result.error["code"], "INVALID_REQUEST")
        self.assertError(self.ask("flow", "READ_FLOW", ids=["FLOW-1"], profile="SMALL"), ConsumerErrorCode.INVALID_REQUEST)
        self.assertError(self.ask("docs", "RENDER_HUMAN_DOC", scope="RUN"), ConsumerErrorCode.INVALID_REQUEST)
        self.assertError(self.ask("docs", "RENDER_HUMAN_DOC", scope="RUN", profile="human-secret"), ConsumerErrorCode.INVALID_REQUEST)

    def test_error_results_are_contractual_not_tracebacks(self) -> None:
        result = self.ask("flow", "READ_FLOW", ids=["FLOW-NOPE"])
        self.assertError(result, ConsumerErrorCode.ENTITY_NOT_FOUND)
        self.assertEqual(result.provenance["completeness"], "NOT_APPLICABLE")
        self.assertTrue(result.result_id.startswith("CRES-"))
        broken = ConsumerFacade(self.run_dir)
        with mock.patch.object(facade_module.ConsumerFacade, "_read_flow", side_effect=RuntimeError("secret internals /x/y")):
            broken._handlers[ConsumerCapability.READ_FLOW] = broken._read_flow
            internal = broken.handle(request(BUILTIN["flow"], "READ_FLOW", ids=["FLOW-1"]))
        self.assertError(internal, ConsumerErrorCode.INTERNAL_ERROR)
        self.assertEqual(internal.error["detail"], "RuntimeError")
        self.assertNotIn("secret", internal.to_json())


class EvidenceAndFlowTests(ContractTestCase):
    def test_evidence_read_preserves_ids_kinds_and_fingerprints(self) -> None:
        result = self.ask("evidence", "READ_EVIDENCE", ids=["PATH-0001", "DAO-0000", "FLOW-1"])
        self.assertTrue(result.ok, result.error)
        items = result.payload["evidence"]
        self.assertEqual([(i["ref"], i["kind"]) for i in items], [("DAO-0000", "DATA_ACCESS"), ("FLOW-1", "FLOW"), ("PATH-0001", "PATH")])
        self.assertTrue(all(len(i["record_fingerprint"]) == 64 for i in items))
        self.assertEqual(items[1]["record"]["id"], "FLOW-1")
        self.assertEqual(len(result.provenance["source_identities"]), 3)
        self.assertTrue(result.provenance["read_only"])
        self.assertError(self.ask("evidence", "READ_EVIDENCE", ids=["DAO-0000", "DAO-9999"]), ConsumerErrorCode.ENTITY_NOT_FOUND)

    def test_complete_flow(self) -> None:
        result = self.ask("flow", "READ_FLOW", ids=["FLOW-1"])
        self.assertTrue(result.ok, result.error)
        flow = result.payload["flows"][0]
        self.assertEqual((flow["flow_id"], flow["partial"], flow["completeness"]), ("FLOW-1", False, "COMPLETE"))
        self.assertEqual(len(flow["paths"]), 3)
        self.assertFalse(result.provenance["partial"])

    def test_partial_flow_never_hides_partial(self) -> None:
        result = self.ask("flow", "READ_PARTIAL_FLOW", ids=["FLOW-1"], options={"max_characters": 2600})
        self.assertTrue(result.ok, result.error)
        self.assertTrue(result.provenance["partial"])
        self.assertEqual(result.provenance["completeness"], "PARTIAL")
        entry = result.payload["flows"][0]
        self.assertTrue(entry["partial"])
        segments = entry["segments"]
        self.assertGreaterEqual(len(segments), 2)
        union: set = set()
        for segment in segments:
            self.assertTrue(segment["partial"] and segment["record"]["partial"])
            self.assertEqual(segment["parent_flow_id"], "FLOW-1")
            self.assertTrue(segment["segment_id"].startswith("SEG-"))
            self.assertTrue(segment["included_paths"] and segment["omitted_paths"] and segment["evidence_refs"])
            self.assertFalse(set(segment["included_paths"]) & set(segment["omitted_paths"]))
            union |= set(segment["included_paths"])
        self.assertEqual(union, {"PATH-0000", "PATH-0001", "PATH-0002"})
        wanted = segments[0]["segment_id"]
        only = self.ask("flow", "READ_PARTIAL_FLOW", ids=["FLOW-1"], options={"max_characters": 2600, "segment_id": wanted})
        self.assertEqual([s["segment_id"] for s in only.payload["flows"][0]["segments"]], [wanted])
        self.assertError(self.ask("flow", "READ_PARTIAL_FLOW", ids=["FLOW-1"], options={"max_characters": 2600, "segment_id": "SEG-x"}),
                         ConsumerErrorCode.ENTITY_NOT_FOUND)

    def test_partial_not_supported_when_flow_fits_or_cannot_be_segmented(self) -> None:
        self.assertError(self.ask("flow", "READ_PARTIAL_FLOW", ids=["FLOW-1"]), ConsumerErrorCode.PARTIAL_NOT_SUPPORTED)
        self.assertError(self.ask("flow", "READ_PARTIAL_FLOW", ids=["FLOW-1"], options={"max_characters": 5}), ConsumerErrorCode.PARTIAL_NOT_SUPPORTED)
        self.assertError(self.ask("flow", "READ_PARTIAL_FLOW", ids=["FLOW-1"], options={"max_characters": 0}), ConsumerErrorCode.INVALID_REQUEST)


class AiContextTests(ContractTestCase):
    def test_ai_context_wraps_existing_projection_without_provider(self) -> None:
        from legacy_documenter.context.ai_projection import build_ai_projection
        result = self.ask("ai", "READ_AI_CONTEXT", ids=["FLOW-1"], profile="SMALL")
        self.assertTrue(result.ok, result.error)
        package = result.payload["package"]
        ix = {n: json.loads((self.run_dir / "index" / f"{n}.json").read_text(encoding="utf-8")) for n in (
            "functional_flows", "functional_paths", "entry_points", "data_access", "sql_operations", "stored_procedures", "data_parameters")}
        self.assertEqual(package, build_ai_projection(["FLOW-1"], ix, profile="SMALL"))  # no budget/grounding duplicated
        self.assertEqual(result.provenance["provider_calls"], 0)
        self.assertEqual(result.provenance["source_identities"], [f"AI_PROJECTION:{package['package_id']}"])
        self.assertError(self.ask("ai", "READ_AI_CONTEXT", ids=["FLOW-9"]), ConsumerErrorCode.ENTITY_NOT_FOUND)
        self.assertError(self.ask("ai", "READ_AI_CONTEXT", ids=["FLOW-1"], profile="FULL"), ConsumerErrorCode.INVALID_REQUEST)
        with mock.patch("legacy_documenter.orchestration.ai_interpretation._resolve_provider", side_effect=AssertionError("provider")) as guard:
            self.assertTrue(self.ask("ai", "READ_AI_CONTEXT", ids=["FLOW-1"], profile="TINY").ok)
            guard.assert_not_called()


class CanonicalAndReviewTests(ContractTestCase):
    def test_canonical_not_available_without_decisions_and_no_directory_created(self) -> None:
        self.assertError(self.ask("canonical", "READ_CANONICAL", scope="RUN"), ConsumerErrorCode.CANONICAL_NOT_AVAILABLE)
        self.assertError(self.ask("canonical", "READ_CANONICAL", ids=["CAN-1"]), ConsumerErrorCode.CANONICAL_NOT_AVAILABLE)
        self.assertError(self.ask("review", "READ_REVIEW_HISTORY", ids=[self.ids["approve"]]), ConsumerErrorCode.ENTITY_NOT_FOUND)
        self.assertFalse((self.run_dir / "knowledge").exists())

    def test_canonical_read_preserves_provenance_and_lookups(self) -> None:
        canonical_id = self.approve()
        by_id = self.ask("canonical", "READ_CANONICAL", ids=[canonical_id])
        self.assertTrue(by_id.ok, by_id.error)
        record = by_id.payload["canonical"][0]
        self.assertEqual(record["canonical_id"], canonical_id)
        self.assertEqual(record["source_proposal_id"], self.ids["approve"])
        self.assertEqual(record["decision_action"], "APPROVE")
        self.assertEqual(record["evidence_refs"], ["DAO-0000"])
        self.assertEqual(record["provenance"]["decided_by"], "Ana Reviewer")
        self.assertFalse(record["partial"])
        self.assertFalse(by_id.provenance["partial"])
        for by, value in (("evidence_ref", "DAO-0000"), ("proposal_id", self.ids["approve"])):
            found = self.ask("canonical", "READ_CANONICAL", ids=[value], options={"by": by})
            self.assertEqual([r["canonical_id"] for r in found.payload["canonical"]], [canonical_id])
        listing = self.ask("canonical", "READ_CANONICAL", scope="RUN")
        self.assertEqual(listing.payload["page"], {"total": 1, "offset": 0, "limit": 100})
        self.assertError(self.ask("canonical", "READ_CANONICAL", ids=["CAN-nope"]), ConsumerErrorCode.ENTITY_NOT_FOUND)
        self.assertError(self.ask("canonical", "READ_CANONICAL", ids=["x"], options={"by": "file_name"}), ConsumerErrorCode.INVALID_REQUEST)

    def test_partial_canonical_stays_partial(self) -> None:
        canonical_id = self.approve("segmented")
        result = self.ask("canonical", "READ_CANONICAL", ids=[canonical_id])
        record = result.payload["canonical"][0]
        self.assertTrue(record["partial"] and record["scope"]["partial"])
        self.assertEqual(record["scope"]["parent_flow_id"], "FLOW-1")
        self.assertEqual(record["content"]["statement_scope"], "PARTIAL")
        self.assertTrue(result.provenance["partial"])

    def test_review_history_and_audit_chain_are_read_only(self) -> None:
        canonical_id = self.approve()
        before = tree_hash(self.run_dir)
        result = self.ask("review", "READ_REVIEW_HISTORY", ids=[self.ids["approve"]], options={"include_audit_chain": True})
        self.assertTrue(result.ok, result.error)
        entry = result.payload["history"][0]
        self.assertEqual([d["action"] for d in entry["decisions"]], ["APPROVE"])
        self.assertEqual(len(entry["baselines"]), 1)
        self.assertEqual(entry["proposal_snapshot"]["proposal_id"], self.ids["approve"])
        self.assertEqual(entry["audit_chain"][0]["canonical_id"], canonical_id)
        self.assertTrue(entry["audit_chain"][0]["links_verified"])
        listing = self.ask("review", "READ_REVIEW_HISTORY", scope="RUN")
        self.assertEqual(listing.payload["history"][0]["proposal_id"], self.ids["approve"])
        self.assertEqual(tree_hash(self.run_dir), before)

    def test_review_history_loads_each_collection_once_not_per_proposal(self) -> None:
        """No O(N^2): decisions, baselines and canonical records are read once per request, however many proposals."""
        from legacy_documenter.review.store import ReviewStore
        for name in ("approve", "reject", "defer", "correct"):
            service = ApprovalService(self.run_dir, clock=FIXED)
            service.prepare(self.ids[name], "Ana Reviewer")
            service.decide(self.ids[name], "DEFER" if name == "defer" else "REJECT" if name == "reject" else "APPROVE", "Ana Reviewer")
        calls = []
        original = ReviewStore._read_all
        with mock.patch.object(ReviewStore, "_read_all", staticmethod(lambda directory, loader: calls.append(directory.name) or original(directory, loader))):
            result = self.ask("review", "READ_REVIEW_HISTORY", scope="RUN", options={"include_audit_chain": True})
        self.assertTrue(result.ok, result.error)
        self.assertEqual(len(result.payload["history"]), 4)
        self.assertEqual(sorted(calls), ["baselines", "canonical", "decisions"])

    def test_store_bulk_helpers_match_the_per_proposal_api(self) -> None:
        from legacy_documenter.review.store import ReviewStore
        self.approve()
        store = ReviewStore(self.run_dir)
        proposal_id = self.ids["approve"]
        decisions = store.decisions()
        self.assertEqual(ReviewStore.chain_of(decisions, proposal_id), store.decisions_for(proposal_id))
        self.assertEqual([b for b in store.baselines() if b.proposal_id == proposal_id], store.baselines_for(proposal_id))
        decision = decisions[0]
        bulk = ReviewStore.verify_audit_chain(decision, store.snapshot_for(proposal_id), store.baselines_for(proposal_id),
                                              store.canonical_for_proposal(proposal_id))
        self.assertEqual(bulk, store.audit_chain(decision.decision_id))

    def test_tampered_store_is_a_contractual_error(self) -> None:
        self.approve()
        (next((self.run_dir / "knowledge" / "decisions").glob("*.json"))).write_text("{not json", encoding="utf-8")
        self.assertError(self.ask("review", "READ_REVIEW_HISTORY", scope="RUN"), ConsumerErrorCode.SOURCE_UNAVAILABLE)


class DocumentationAndExportTests(ContractTestCase):
    def test_human_profiles_map_to_shipped_profile_directories(self) -> None:
        defaults = PACKAGE / "documentation_v52" / "defaults" / "profiles"
        mapping = {"human-functional": "general_overview", "human-technical": "developer_technical"}
        for consumer_profile, profile_id in mapping.items():
            data = json.loads((defaults / f"{profile_id}.json").read_text(encoding="utf-8"))
            self.assertEqual(HUMAN_DOC_DIRECTORIES[consumer_profile], data["output_dir"])

    def test_human_functional_and_technical(self) -> None:
        for profile, directory in HUMAN_DOC_DIRECTORIES.items():
            with self.subTest(profile):
                result = self.ask("docs", "RENDER_HUMAN_DOC", scope="RUN", profile=profile)
                self.assertTrue(result.ok, result.error)
                paths = [d["path"] for d in result.payload["documents"]]
                self.assertTrue(paths and all(p.startswith(directory + "/") for p in paths))
                self.assertIn(directory.capitalize(), result.payload["index_document"]["content"])
        fetched = self.ask("docs", "RENDER_HUMAN_DOC", ids=["general/system.md"], profile="human-functional")
        self.assertEqual(fetched.payload["documents"][0]["content"], "# System\n")
        self.assertError(self.ask("docs", "RENDER_HUMAN_DOC", ids=["developer/modules.md"], profile="human-functional"), ConsumerErrorCode.ENTITY_NOT_FOUND)
        self.assertError(self.ask("docs", "RENDER_HUMAN_DOC", ids=["../index/entry_points.json"], profile="human-functional"), ConsumerErrorCode.ENTITY_NOT_FOUND)

    def test_document_hash_mismatch_fails_closed(self) -> None:
        (self.run_dir / "documentation_v52" / "general" / "system.md").write_text("# tampered\n", encoding="utf-8")
        result = self.ask("docs", "RENDER_HUMAN_DOC", ids=["general/system.md"], profile="human-functional")
        self.assertError(result, ConsumerErrorCode.SOURCE_UNAVAILABLE)
        self.assertIn("document_hash_mismatch", result.error["detail"])

    def test_json_export_wraps_consumer_projection(self) -> None:
        manifest = self.ask("export", "EXPORT_JSON", scope="RUN")
        self.assertTrue(manifest.ok, manifest.error)
        on_disk = json.loads((self.run_dir / "consumer_projection" / "CONSUMER_PROJECTION.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest.payload["manifest"], on_disk)
        relative = on_disk["partitions"][0]["relative_path"]
        part = self.ask("export", "EXPORT_JSON", ids=[relative])
        self.assertEqual(part.payload["partitions"][0]["partition_id"], on_disk["partitions"][0]["partition_id"])
        self.assertError(self.ask("export", "EXPORT_JSON", ids=["parts/part-999999.json"]), ConsumerErrorCode.ENTITY_NOT_FOUND)

    def test_missing_artifacts_are_source_unavailable(self) -> None:
        shutil.rmtree(self.run_dir / "documentation_v52")
        shutil.rmtree(self.run_dir / "consumer_projection")
        self.assertError(self.ask("docs", "RENDER_HUMAN_DOC", scope="RUN", profile="human-technical"), ConsumerErrorCode.SOURCE_UNAVAILABLE)
        self.assertError(self.ask("export", "EXPORT_JSON", scope="RUN"), ConsumerErrorCode.SOURCE_UNAVAILABLE)
        shutil.rmtree(self.run_dir / "index")
        self.assertError(self.ask("flow", "READ_FLOW", ids=["FLOW-1"]), ConsumerErrorCode.SOURCE_UNAVAILABLE)


class DeterminismAndReadOnlyTests(ContractTestCase):
    def every_request(self) -> list[dict]:
        canonical = self.approve()
        return [
            request(BUILTIN["evidence"], "READ_EVIDENCE", ids=["PATH-0000", "FLOW-1"]), request(BUILTIN["flow"], "READ_FLOW", ids=["FLOW-1"]),
            request(BUILTIN["flow"], "READ_PARTIAL_FLOW", ids=["FLOW-1"], options={"max_characters": 2600}),
            request(BUILTIN["ai"], "READ_AI_CONTEXT", ids=["FLOW-1"], profile="MEDIUM"),
            request(BUILTIN["canonical"], "READ_CANONICAL", ids=[canonical]), request(BUILTIN["canonical"], "READ_CANONICAL", scope="RUN"),
            request(BUILTIN["review"], "READ_REVIEW_HISTORY", ids=[self.ids["approve"]], options={"include_audit_chain": True}),
            request(BUILTIN["docs"], "RENDER_HUMAN_DOC", scope="RUN", profile="human-functional"),
            request(BUILTIN["docs"], "RENDER_HUMAN_DOC", ids=["developer/README.md"], profile="human-technical"),
            request(BUILTIN["export"], "EXPORT_JSON", scope="RUN"),
        ]

    def test_same_request_same_bytes_across_instances_and_orders(self) -> None:
        requests = self.every_request()
        first = [self.facade.handle(r).to_json() for r in requests]
        second = [ConsumerFacade(self.run_dir).handle(r).to_json() for r in reversed(requests)][::-1]
        self.assertEqual(first, second)
        for text in first:
            self.assertEqual(json.loads(text)["status"], "OK", text[:200])
        reordered = request(BUILTIN["evidence"], "READ_EVIDENCE", ids=["FLOW-1", "PATH-0000"])
        self.assertEqual(self.facade.handle(reordered).result_id, self.facade.handle(requests[0]).result_id)

    def test_result_identity_tracks_request_and_source(self) -> None:
        a = self.ask("evidence", "READ_EVIDENCE", ids=["DAO-0000"])
        b = self.ask("evidence", "READ_EVIDENCE", ids=["DAO-0001"])
        c = self.ask("evidence", "READ_EVIDENCE", ids=["DAO-0000"], version="1.3")
        self.assertNotEqual(a.result_id, b.result_id)
        self.assertEqual(a.result_id, c.result_id)  # same resolved contract version, same request, same sources
        (self.run_dir / "index" / "data_access.json").write_text(json.dumps(
            [{"id": f"DAO-000{i}", "class": "Dao", "method": f"Changed{i}"} for i in range(3)]), encoding="utf-8")
        d = ConsumerFacade(self.run_dir).handle(request(BUILTIN["evidence"], "READ_EVIDENCE", ids=["DAO-0000"]))
        self.assertNotEqual(a.result_id, d.result_id)

    def test_serving_every_capability_writes_nothing(self) -> None:
        requests = self.every_request()
        before = tree_hash(self.run_dir)
        for item in requests:
            self.assertTrue(self.facade.handle(item).ok)
        self.assertEqual(tree_hash(self.run_dir), before)

    def test_no_secrets_leave_the_facade(self) -> None:
        data = json.loads((self.run_dir / "index" / "data_access.json").read_text(encoding="utf-8"))
        data[0]["note"] = "Server=db;Password=hunter2secret;"
        (self.run_dir / "index" / "data_access.json").write_text(json.dumps(data), encoding="utf-8")
        result = ConsumerFacade(self.run_dir).handle(request(BUILTIN["evidence"], "READ_EVIDENCE", ids=["DAO-0000"]))
        self.assertNotIn("hunter2secret", result.to_json())


class PluginContractTests(ContractTestCase):
    MANIFEST = {
        "plugin_id": "fake.docs-summary", "plugin_version": "0.1.0", "plugin_contract_version": "1.0",
        "requires": {"consumer_contract": "1.0", "capabilities": ["READ_FLOW", "READ_EVIDENCE"], "optional_capabilities": []},
        "provides": {"input_kinds": ["FLOW_ID", "EVIDENCE_REF"], "output_kinds": ["FLOW_RECORD", "EVIDENCE_RECORD"]},
        "read_only": True, "entrypoint_metadata": {"kind": "python", "reference": "os.system('boom') ; import evil"},
    }

    def manifest(self, **changes) -> dict:
        data = json.loads(json.dumps(self.MANIFEST))
        for key, value in changes.items():
            if "." in key:
                outer, inner = key.split(".")
                data[outer][inner] = value
            else:
                data[key] = value
        return data

    def assertRejected(self, data, code: ConsumerErrorCode) -> None:
        with self.assertRaises(ConsumerError) as ctx:
            validate_manifest(data)
        self.assertEqual(ctx.exception.code, code, ctx.exception)

    def test_valid_manifest_is_accepted_and_never_executed(self) -> None:
        with mock.patch("importlib.import_module") as imported, mock.patch("builtins.exec") as executed, mock.patch("builtins.eval") as evaluated:
            for patched in (imported, executed, evaluated):
                patched.reset_mock()  # mock.patch's own setup imports modules; only the validation itself is under test
            outcome = validate_manifest(self.manifest())
            descriptor = descriptor_from_manifest(outcome)
        imported.assert_not_called()
        executed.assert_not_called()
        evaluated.assert_not_called()
        self.assertEqual(outcome.resolved_plugin_contract_version, "1.0")
        self.assertEqual(outcome.ignored_optional_capabilities, ())
        self.assertEqual(descriptor.consumer_id, "plugin.fake.docs-summary")
        self.assertEqual([c.value for c in descriptor.capabilities_required], ["READ_EVIDENCE", "READ_FLOW"])
        self.assertEqual(dict(outcome.manifest.entrypoint_metadata)["kind"], "python")  # stored as inert text
        self.assertNotIn("evil", sys.modules)

    def test_rejections_fail_closed(self) -> None:
        cases = {
            "unknown_required_capability": (self.manifest(**{"requires.capabilities": ["READ_FLOW", "READ_TELEPATHY"]}), ConsumerErrorCode.UNSUPPORTED_CAPABILITY),
            "write_required": (self.manifest(**{"requires.capabilities": ["READ_FLOW", "APPROVE_PROPOSAL"]}), ConsumerErrorCode.READ_ONLY_VIOLATION),
            "write_optional": (self.manifest(**{"requires.optional_capabilities": ["WRITE_EVIDENCE"]}), ConsumerErrorCode.READ_ONLY_VIOLATION),
            "not_read_only": (self.manifest(read_only=False), ConsumerErrorCode.READ_ONLY_VIOLATION),
            "plugin_major": (self.manifest(plugin_contract_version="2.0"), ConsumerErrorCode.PLUGIN_INCOMPATIBLE),
            "consumer_major": (self.manifest(**{"requires.consumer_contract": "2.1"}), ConsumerErrorCode.PLUGIN_INCOMPATIBLE),
            "malformed_version": (self.manifest(plugin_contract_version="v1"), ConsumerErrorCode.PLUGIN_MANIFEST_INVALID),
            "unknown_key": ({**self.manifest(), "postinstall": "rm -rf /"}, ConsumerErrorCode.PLUGIN_MANIFEST_INVALID),
            "missing_key": ({k: v for k, v in self.manifest().items() if k != "provides"}, ConsumerErrorCode.PLUGIN_MANIFEST_INVALID),
            "bad_id": (self.manifest(plugin_id="../Evil"), ConsumerErrorCode.PLUGIN_MANIFEST_INVALID),
            "empty_required": (self.manifest(**{"requires.capabilities": []}), ConsumerErrorCode.PLUGIN_MANIFEST_INVALID),
            "unknown_kind": (self.manifest(**{"provides.input_kinds": ["SOURCE_CODE"]}), ConsumerErrorCode.PLUGIN_MANIFEST_INVALID),
            "bad_entrypoint_key": (self.manifest(entrypoint_metadata={"command": "x"}), ConsumerErrorCode.PLUGIN_MANIFEST_INVALID),
            "entrypoint_not_text": (self.manifest(entrypoint_metadata={"kind": ["a"]}), ConsumerErrorCode.PLUGIN_MANIFEST_INVALID),
            "not_a_dict": ("manifest", ConsumerErrorCode.PLUGIN_MANIFEST_INVALID),
        }
        for name, (data, code) in cases.items():
            with self.subTest(name):
                self.assertRejected(data, code)

    def test_compatibility_rules(self) -> None:
        minor = validate_manifest(self.manifest(plugin_contract_version="1.7", **{"requires.consumer_contract": "1.4"}))
        self.assertEqual((minor.resolved_plugin_contract_version, minor.resolved_consumer_contract_version), ("1.0", "1.0"))
        optional = validate_manifest(self.manifest(**{"requires.optional_capabilities": ["READ_CANONICAL", "READ_FUTURE_THING"]}))
        self.assertEqual(optional.ignored_optional_capabilities, ("READ_FUTURE_THING",))
        self.assertIn("READ_CANONICAL", descriptor_from_manifest(optional).to_dict()["capabilities_required"])
        self.assertNotIn("READ_FUTURE_THING", descriptor_from_manifest(optional).to_dict()["capabilities_required"])

    def test_fake_plugin_end_to_end_manifest_to_result(self) -> None:
        registry = register_manifests(builtin_registry(), [self.manifest()])
        facade = ConsumerFacade(self.run_dir, registry)
        flow = facade.handle(request("plugin.fake.docs-summary", "READ_FLOW", ids=["FLOW-1"]))
        evidence = facade.handle(request("plugin.fake.docs-summary", "READ_EVIDENCE", ids=["DAO-0000"]))
        self.assertTrue(flow.ok and evidence.ok, (flow.error, evidence.error))
        self.assertEqual(flow.consumer_id, "plugin.fake.docs-summary")
        self.assertEqual(json.loads(flow.to_json())["contract_version"], CONTRACT_VERSION)
        # capabilities the manifest did not declare are not granted
        self.assertError(facade.handle(request("plugin.fake.docs-summary", "READ_CANONICAL", scope="RUN")), ConsumerErrorCode.UNSUPPORTED_CAPABILITY)
        self.assertError(facade.handle(request("plugin.fake.docs-summary", "APPROVE_PROPOSAL", ids=["x"])), ConsumerErrorCode.READ_ONLY_VIOLATION)
        # a rejected manifest registers nothing, and the original registry is untouched
        with self.assertRaises(ConsumerError):
            register_manifests(builtin_registry(), [self.manifest(), self.manifest(plugin_id="bad", plugin_contract_version="9.0")])
        self.assertEqual(len(builtin_registry()), 7)
        self.assertEqual(facade.handle(request("plugin.fake.docs-summary", "READ_FLOW", ids=["FLOW-1"])).to_json(), flow.to_json())


def _python_files(*packages: str) -> list[Path]:
    return sorted(p for pkg in packages for p in (PACKAGE / pkg).rglob("*.py"))


def _imports(path: Path) -> set[str]:
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            found.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            found.add(("." * node.level) + (node.module or ""))
    return found


class ArchitectureGuardTests(unittest.TestCase):
    """No plugin runtime, no provider/technology coupling, read-only, approval and upstream boundaries."""

    FORBIDDEN_IMPORTS = ("importlib", "pkgutil", "runpy", "subprocess", "socket", "urllib", "http", "requests", "ftplib", "ssl",
                         "multiprocessing", "ctypes", "pip", "shutil", "tempfile", "zipimport", "imp", "os")
    FORBIDDEN_CALLS = {"exec", "eval", "__import__", "system", "popen", "walk", "scandir", "listdir", "glob", "rglob", "iterdir",
                       "write_text", "write_bytes", "mkdir", "unlink", "rmdir", "rename", "touch", "rmtree", "atomic_write_text",
                       "import_module", "spawn", "fork", "urlopen"}
    FORBIDDEN_NAMES = {"ApprovalService", "write_decision", "write_canonical", "write_baseline", "write_snapshot", "prepare", "decide",
                       "ProviderRegistry", "_resolve_provider", "CopilotProvider", "GeminiProvider"}
    LAYERS_BELOW = ("evidence", "cache", "adapters", "analysis", "extractors", "scanner", "review", "knowledge", "orchestration", "llm",
                    "context", "documentation", "documentation_v52", "exporters", "fingerprints", "cli", "models", "quality", "utils")

    def test_contract_packages_have_no_runtime_capabilities(self) -> None:
        for path in _python_files(*CONTRACT_PACKAGES):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for module in _imports(path):
                root = module.lstrip(".").split(".")[0]
                self.assertNotIn(root, self.FORBIDDEN_IMPORTS, f"{path.name} imports {module}")
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    name = func.id if isinstance(func, ast.Name) else func.attr if isinstance(func, ast.Attribute) else ""
                    self.assertNotIn(name, self.FORBIDDEN_CALLS, f"{path.name}:{node.lineno} calls {name}")
                    if isinstance(func, ast.Name):
                        self.assertNotEqual(name, "compile", f"{path.name}:{node.lineno} calls compile")
                    if name == "open":
                        self.assertLessEqual(len(node.args) + len(node.keywords), 1, f"{path.name}:{node.lineno} open() with mode")
                if isinstance(node, ast.Name | ast.Attribute):
                    ident = node.id if isinstance(node, ast.Name) else node.attr
                    self.assertNotIn(ident, self.FORBIDDEN_NAMES, f"{path.name}:{node.lineno} uses {ident}")

    def test_contract_modules_do_not_depend_on_technology_or_provider(self) -> None:
        pure = _python_files("plugins") + [PACKAGE / "consumers" / n for n in ("contracts.py", "registry.py", "__init__.py")]
        for path in pure:
            for module in _imports(path):
                absolute = module.lstrip(".")
                if module.startswith("legacy_documenter."):
                    self.assertTrue(absolute.startswith(("legacy_documenter.consumers", "legacy_documenter.plugins")), f"{path.name} imports {module}")
        allowed = ("context.ai_projection", "context.flow_segmentation", "context.hydration", "review.models", "review.store", "utils.sanitizer")
        for path in _python_files("consumers"):
            for module in _imports(path):
                if module.startswith("legacy_documenter.") and not module.startswith(("legacy_documenter.consumers", "legacy_documenter.plugins")):
                    self.assertTrue(module.removeprefix("legacy_documenter.").startswith(allowed), f"{path.name} imports {module}")
                for banned in ("llm", "adapters", "extractors", "orchestration", "cli", "evidence", "cache", "analysis", "scanner"):
                    self.assertFalse(module.startswith(f"legacy_documenter.{banned}"), f"{path.name} imports {module}")

    def test_core_never_depends_on_the_consumer_or_plugin_layer(self) -> None:
        for path in sorted(PACKAGE.rglob("*.py")):
            relative = path.relative_to(PACKAGE).parts
            if relative[0] in CONTRACT_PACKAGES:
                continue
            for module in _imports(path):
                self.assertFalse(module.lstrip(".").startswith(("legacy_documenter.consumers", "legacy_documenter.plugins", "consumers", "plugins")),
                                 f"{path} imports {module}")

    def test_plugin_layer_does_not_import_the_facade(self) -> None:
        for path in _python_files("plugins"):
            self.assertFalse(any("facade" in m or "sources" in m for m in _imports(path)), path.name)

    def test_main_and_cli_expose_no_consumer_or_plugin_command(self) -> None:
        for path in sorted((PACKAGE / "cli").rglob("*.py")) + [PACKAGE / "main.py", ROOT / "main.py"]:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("legacy_documenter.consumers", text)
            self.assertNotIn("legacy_documenter.plugins", text)

    def test_existing_plugin_like_tooling_is_isolated(self) -> None:
        """Legacy `knowledge/plugin_projection` is an in-memory projection (no loading); the only dynamic-import hits are not plugin code."""
        dynamic = []
        for path in sorted(PACKAGE.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            if any(token in text for token in ("importlib", "pkgutil", "__import__(")):
                dynamic.append(path.relative_to(PACKAGE).as_posix())
        self.assertEqual(dynamic, ["documentation/renderer.py", "llm/copilot_pilot.py"])

    def test_analysis_fingerprint_and_version_are_unchanged(self) -> None:
        self.assertEqual(ANALYZER_VERSION, 3)
        self.assertEqual(analyzer_code_fingerprint().sha256, "4f7600f0fa351674878d66940352e9569de2b0f620643a3124b5c94545eb1ec6")

    def test_facade_is_read_only_by_construction(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        run = tmp / "run"
        build_full_run(run)
        before = tree_hash(run)
        ConsumerFacade(run).handle(request(BUILTIN["flow"], "READ_FLOW", ids=["FLOW-1"]))
        self.assertEqual(tree_hash(run), before)
        self.assertFalse(any(name in vars(ConsumerFacade) for name in ("write", "approve", "decide", "persist", "save")))

    def test_spec_table_and_request_dataclass_are_consistent(self) -> None:
        self.assertEqual(set(CAPABILITY_SPECS), set(ConsumerCapability))
        with self.assertRaises(ConsumerError):
            ConsumerRequest.from_dict({"consumer_id": "x", "contract_version": "1.0", "capability": "READ_FLOW", "scope": "ENTITIES",
                                       "options": {"fn": object()}})


if __name__ == "__main__":
    unittest.main()
