"""V5.7-R1: HumanDecision + CanonicalKnowledgeRecord over persisted AI proposals (synthetic, provider-free)."""
from __future__ import annotations

import ast
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from legacy_documenter.cli.full_pipeline import _proposal_to_dict
from legacy_documenter.review.models import DecisionAction, ReviewError, ReviewErrorCode
from legacy_documenter.review.render import pending_proposals, render_view
from legacy_documenter.review.service import ApprovalService
from legacy_documenter.review.store import ReviewStore
from legacy_documenter.main import main as cli_main
from legacy_documenter.orchestration.proposal_adapter import adapt_findings_to_proposals

ROOT = Path(__file__).resolve().parents[1]
FIXED = lambda: "2026-10-07T12:00:00Z"  # noqa: E731
SEGMENT = {
    "parent_flow_id": "FLOW-1", "segment_id": "SEG-abc", "partial": True, "completeness": "PARTIAL", "ordinal": 1,
    "included_paths": ["PATH-0000", "PATH-0001"], "omitted_paths": ["PATH-0002"], "overlap_paths": [],
}


def tree_hash(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(item.read_bytes())
    return digest.hexdigest()


def build_run(root: Path) -> dict[str, str]:
    """A tiny but realistic run directory: index/*.json + proposals/AI_PROPOSALS.json."""
    index = root / "index"
    index.mkdir(parents=True)
    paths = [{"flow_id": "FLOW-1", "path_id": f"PATH-000{i}", "nodes": [f"DAO-000{i}"], "terminal_type": "sql",
              "terminal_target": f"DAO-000{i}", "confidence": "confirmed", "evidence_refs": [f"DAO-000{i}"]} for i in range(3)]
    files = {
        "functional_paths.json": paths,
        "functional_flows.json": [{"id": "FLOW-1", "entry_point_id": "EP-1", "confidence": "confirmed"}],
        "entry_points.json": [{"id": "EP-1", "handler": "Page_Load"}],
        "data_access.json": [{"id": f"DAO-000{i}", "class": "Dao", "method": f"M{i}"} for i in range(3)],
    }
    for name, data in files.items():
        (index / name).write_text(json.dumps(data), encoding="utf-8")
    findings = [
        {"statement": f"Statement {name}", "confidence": "UNCERTAIN", "evidence_refs": ["DAO-0000"]}
        for name in ("approve", "reject", "defer", "correct", "other")
    ]
    segmented = {"statement": "Statement segmented", "confidence": "UNCERTAIN", "evidence_refs": ["DAO-0001"],
                 "flow_segment": SEGMENT, "ai_request_identity": {"request_id": "REQ-1", "ai_config_fingerprint": "AICFG-1"}}
    proposals = adapt_findings_to_proposals(findings + [segmented])
    envelope = {"schema_version": "1.0", "status": "PENDING_TECHNICAL_LEAD_REVIEW", "ai_interpretation_status": "SUCCESS",
                "provider_id": "fake-provider", "model_id": "fake-model", "context_package_id": "AIP-1",
                "proposals": [_proposal_to_dict(p) for p in proposals]}
    (root / "proposals").mkdir()
    (root / "proposals" / "AI_PROPOSALS.json").write_text(json.dumps(envelope, sort_keys=True), encoding="utf-8")
    return {p.statement.replace("Statement ", "").split(":")[-1].strip(): p.proposal_id for p in proposals} | {
        "segmented": proposals[-1].proposal_id}


class ReviewTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.run_dir = self.tmp / "run"
        self.ids = build_run(self.run_dir)
        self.service = ApprovalService(self.run_dir, clock=FIXED)
        self.store = ReviewStore(self.run_dir)

    def decide(self, name: str, action: str, reviewer: str = "Ana Reviewer", **kw):
        self.service.prepare(self.ids[name], reviewer)  # R2: a verifiable review baseline precedes every first decision
        return self.service.decide(self.ids[name], action, reviewer, **kw)

    def assertCode(self, code: ReviewErrorCode, func, *args, **kwargs):
        with self.assertRaises(ReviewError) as ctx:
            func(*args, **kwargs)
        self.assertEqual(ctx.exception.code, code)

    def rewrite_proposals(self, mutate) -> None:
        path = self.run_dir / "proposals" / "AI_PROPOSALS.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        mutate(data)
        path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")


class ApproveTests(ReviewTestCase):
    def test_grounded_approve_creates_canonical_with_provenance(self) -> None:
        out = self.decide("approve", "APPROVE", rationale="looks right")
        self.assertFalse(out.idempotent_replay)
        record = out.canonical
        self.assertEqual(record.source_proposal_id, self.ids["approve"])
        self.assertEqual(record.decision_id, out.decision.decision_id)
        self.assertEqual(record.evidence_refs, ("DAO-0000",))
        self.assertEqual(record.provenance["decided_by"], "Ana Reviewer")
        self.assertEqual(record.provenance["provider_id"], "fake-provider")
        self.assertEqual(record.provenance["context_package_id"], "AIP-1")
        self.assertEqual(record.provenance["authored_by"], "AI_PROPOSAL_ACCEPTED_BY_HUMAN")
        self.assertEqual(self.store.canonical_by_id(record.canonical_id), record)

    def test_repeated_same_decision_is_idempotent_and_byte_stable(self) -> None:
        first = self.decide("approve", "APPROVE")
        before = tree_hash(self.run_dir / "knowledge")
        second = ApprovalService(self.run_dir, clock=lambda: "2030-01-01T00:00:00Z").decide(self.ids["approve"], "APPROVE", "Ana Reviewer")
        self.assertTrue(second.idempotent_replay)
        self.assertEqual(second.canonical.canonical_id, first.canonical.canonical_id)
        self.assertEqual(second.decision.decided_at, first.decision.decided_at)
        self.assertEqual(before, tree_hash(self.run_dir / "knowledge"))
        self.assertEqual(len(self.store.canonical_records()), 1)

    def test_stale_when_reviewer_view_fingerprint_differs(self) -> None:
        self.assertCode(ReviewErrorCode.PROPOSAL_STALE, self.decide, "approve", "APPROVE", expected_evidence_fingerprint="0" * 64)
        self.assertEqual(self.store.decisions(), [])

    def test_matching_expected_fingerprint_is_accepted(self) -> None:
        row = next(r for r in pending_proposals(self.run_dir) if r["proposal_id"] == self.ids["approve"])
        self.decide("approve", "APPROVE", expected_evidence_fingerprint=row["evidence_fingerprint"])

    def test_stale_when_evidence_changes_after_previous_decision(self) -> None:
        self.decide("defer", "DEFER", rationale="later")
        access = self.run_dir / "index" / "data_access.json"
        data = json.loads(access.read_text(encoding="utf-8"))
        data[0]["method"] = "Changed"
        access.write_text(json.dumps(data), encoding="utf-8")
        self.assertCode(ReviewErrorCode.PROPOSAL_STALE, self.decide, "defer", "APPROVE")
        self.assertEqual(self.store.canonical_records(), [])

    def test_tampered_statement_is_rejected(self) -> None:
        def mutate(data):
            data["proposals"][0]["statement"] = "Silently edited"
        self.rewrite_proposals(mutate)
        self.assertCode(ReviewErrorCode.PROPOSAL_TAMPERED, self.decide, "approve", "APPROVE")

    def test_tampered_partial_flag_is_rejected(self) -> None:
        def mutate(data):
            data["proposals"][-1]["metadata"]["flow_segment"]["partial"] = False
        self.rewrite_proposals(mutate)
        self.assertCode(ReviewErrorCode.PROPOSAL_TAMPERED, self.decide, "segmented", "APPROVE")

    def test_tampered_after_previous_decision_is_rejected(self) -> None:
        self.decide("defer", "DEFER")
        def mutate(data):
            data["proposals"][2]["metadata"] = {"injected": True}
        self.rewrite_proposals(mutate)
        self.assertCode(ReviewErrorCode.PROPOSAL_TAMPERED, self.decide, "defer", "APPROVE")

    def test_missing_evidence_is_rejected(self) -> None:
        (self.run_dir / "index" / "data_access.json").write_text("[]", encoding="utf-8")
        (self.run_dir / "index" / "functional_paths.json").write_text("[]", encoding="utf-8")
        self.assertCode(ReviewErrorCode.MISSING_EVIDENCE, self.decide, "approve", "APPROVE")

    def test_unknown_proposal(self) -> None:
        self.assertCode(ReviewErrorCode.PROPOSAL_NOT_FOUND, self.service.decide, "PRP-nope", "APPROVE", "Ana")


class RejectDeferTests(ReviewTestCase):
    def test_reject_persists_without_canonical_and_retains_proposal(self) -> None:
        proposals_before = (self.run_dir / "proposals" / "AI_PROPOSALS.json").read_bytes()
        out = self.decide("reject", "REJECT", rationale="wrong")
        self.assertIsNone(out.canonical)
        self.assertEqual(self.store.canonical_records(), [])
        self.assertEqual(self.store.decisions_for(self.ids["reject"])[0].action, DecisionAction.REJECT)
        self.assertEqual(proposals_before, (self.run_dir / "proposals" / "AI_PROPOSALS.json").read_bytes())

    def test_defer_keeps_non_canonical_and_allows_later_review(self) -> None:
        out = self.decide("defer", "DEFER", rationale="need more info")
        self.assertIsNone(out.canonical)
        self.assertEqual(out.decision.rationale, "need more info")
        self.assertIn(self.ids["defer"], [r["proposal_id"] for r in pending_proposals(self.run_dir)])
        later = self.decide("defer", "APPROVE")
        self.assertEqual(later.decision.previous_decision_id, out.decision.decision_id)
        self.assertIsNotNone(later.canonical)
        self.assertEqual([d.action.value for d in self.store.decisions_for(self.ids["defer"])], ["DEFER", "APPROVE"])

    def test_defer_is_not_reject_and_repeated_defer_needs_new_rationale(self) -> None:
        self.decide("defer", "DEFER", rationale="one")
        self.assertCode(ReviewErrorCode.DUPLICATE_DECISION, self.decide, "defer", "DEFER", reviewer="Ben")
        self.decide("defer", "DEFER", reviewer="Ben", rationale="two")


class CorrectTests(ReviewTestCase):
    def test_correction_required(self) -> None:
        self.assertCode(ReviewErrorCode.CORRECTION_REQUIRED, self.decide, "correct", "CORRECT")

    def test_valid_correction_creates_human_authored_canonical(self) -> None:
        out = self.decide("correct", "CORRECT", correction={"statement": "Human wording", "evidence_refs": ["DAO-0001"]})
        record = out.canonical
        self.assertEqual(record.content["statement"], "Human wording")
        self.assertEqual(record.evidence_refs, ("DAO-0001",))
        self.assertEqual(record.corrected_from["statement"], "Statement correct")
        self.assertEqual(record.corrected_from["evidence_refs"], ["DAO-0000"])
        self.assertEqual(record.provenance["authored_by"], "HUMAN_CORRECTION")
        self.assertEqual(record.provenance["decided_by"], "Ana Reviewer")
        self.assertEqual(out.decision.correction["statement"], "Human wording")
        self.assertNotEqual(record.content["statement"], self.store.decisions()[0].provenance.get("statement"))

    def test_correction_without_refs_keeps_proposal_refs(self) -> None:
        out = self.decide("correct", "CORRECT", correction={"statement": "Only text"})
        self.assertEqual(out.canonical.evidence_refs, ("DAO-0000",))

    def test_invalid_correction_payloads(self) -> None:
        for payload in ({}, {"statement": ""}, {"statement": "x", "extra": 1}, {"statement": "x", "evidence_refs": []},
                        {"statement": "x", "evidence_refs": ["DAO-0000", "DAO-0000"]}, {"statement": "x", "evidence_refs": [5]}, "text"):
            with self.subTest(payload=payload):
                self.assertCode(ReviewErrorCode.CORRECTION_INVALID, self.decide, "correct", "CORRECT", correction=payload)

    def test_correction_with_unknown_ref_is_rejected(self) -> None:
        self.assertCode(ReviewErrorCode.MISSING_EVIDENCE, self.decide, "correct", "CORRECT",
                        correction={"statement": "x", "evidence_refs": ["DAO-9999"]})

    def test_segment_correction_cannot_cite_omitted_path_evidence(self) -> None:
        self.assertCode(ReviewErrorCode.INVALID_GROUNDING, self.decide, "segmented", "CORRECT",
                        correction={"statement": "x", "evidence_refs": ["DAO-0002"]})
        self.assertEqual(self.store.decisions(), [])

    def test_correction_only_with_correct_action(self) -> None:
        self.assertCode(ReviewErrorCode.INVALID_DECISION, self.decide, "approve", "APPROVE", correction={"statement": "x"})

    def test_correction_is_data_not_executed(self) -> None:
        out = self.decide("correct", "CORRECT", correction={"statement": "__import__('os').system('x'); ${jndi}"})
        self.assertIn("__import__", out.canonical.content["statement"])


class TransitionTests(ReviewTestCase):
    def test_terminal_decisions_cannot_change_action(self) -> None:
        self.decide("approve", "APPROVE")
        self.assertCode(ReviewErrorCode.INVALID_TRANSITION, self.decide, "approve", "REJECT")
        self.decide("reject", "REJECT")
        self.assertCode(ReviewErrorCode.INVALID_TRANSITION, self.decide, "reject", "APPROVE")
        self.assertEqual(len(self.store.canonical_records()), 1)

    def test_second_approve_by_other_reviewer_is_duplicate_and_creates_no_second_canonical(self) -> None:
        self.decide("approve", "APPROVE")
        self.assertCode(ReviewErrorCode.DUPLICATE_DECISION, self.decide, "approve", "APPROVE", reviewer="Other Person")
        self.assertEqual(len(self.store.canonical_records()), 1)

    def test_canonical_conflict_is_fail_closed(self) -> None:
        out = self.decide("approve", "APPROVE")
        fresh = ApprovalService(self.run_dir, clock=FIXED)
        decisions_dir = self.run_dir / "knowledge" / "decisions"
        (decisions_dir / f"{out.decision.decision_id}.json").unlink()
        self.assertCode(ReviewErrorCode.CANONICAL_CONFLICT, fresh.decide, self.ids["approve"], "APPROVE", "Zed")
        self.assertEqual(len(self.store.canonical_records()), 1)

    def test_store_never_overwrites_different_content(self) -> None:
        out = self.decide("approve", "APPROVE")
        target = self.run_dir / "knowledge" / "decisions" / f"{out.decision.decision_id}.json"
        target.write_text("{}", encoding="utf-8")
        self.assertCode(ReviewErrorCode.DUPLICATE_DECISION, self.store.write_decision, out.decision)

    def test_invalid_action(self) -> None:
        self.assertCode(ReviewErrorCode.INVALID_DECISION, self.decide, "approve", "AUTO_APPROVE")


class ReviewerAndSecurityTests(ReviewTestCase):
    def test_reviewer_required_and_never_automatic(self) -> None:
        self.assertCode(ReviewErrorCode.REVIEWER_REQUIRED, self.decide, "approve", "APPROVE", reviewer="  ")
        for forbidden in ("AUTO", "system", "AI", "fake-provider", "FAKE-MODEL", "llm"):
            with self.subTest(reviewer=forbidden):
                self.assertCode(ReviewErrorCode.INVALID_DECISION, self.decide, "approve", "APPROVE", reviewer=forbidden)
        self.assertEqual(self.store.decisions(), [])

    def test_secrets_are_redacted_before_persisting(self) -> None:
        secret = "password=Hunter2Secret Bearer abcdefghijklmnop12345 api_key: ZZZ999 ghp_abcdefghijklmnopqrstuv"
        out = self.decide("approve", "APPROVE", rationale=secret)
        text = "".join(p.read_text(encoding="utf-8") for p in (self.run_dir / "knowledge").rglob("*.json"))
        for leaked in ("Hunter2Secret", "abcdefghijklmnop12345", "ZZZ999", "ghp_abcdefghijklmnopqrstuv"):
            self.assertNotIn(leaked, text)
        self.assertIn("********", out.decision.rationale)

    def test_correction_secrets_are_redacted(self) -> None:
        out = self.decide("correct", "CORRECT", correction={"statement": "connect with pwd=SuperSecret1"})
        self.assertNotIn("SuperSecret1", json.dumps(out.canonical.to_dict()))

    def test_artifacts_contain_no_raw_source_or_prompts(self) -> None:
        self.decide("approve", "APPROVE")
        text = "".join(p.read_text(encoding="utf-8") for p in (self.run_dir / "knowledge").rglob("*.json")).lower()
        for marker in ("system_instruction", "prompt", "api_key", "authorization"):
            self.assertNotIn(marker, text)


class PartialAndEvidenceTests(ReviewTestCase):
    def test_segment_approval_stays_partial_in_decision_and_canonical(self) -> None:
        out = self.decide("segmented", "APPROVE")
        for scope in (out.decision.scope, out.canonical.scope):
            self.assertTrue(scope["partial"])
            self.assertEqual(scope["parent_flow_id"], "FLOW-1")
            self.assertEqual(scope["segment_id"], "SEG-abc")
            self.assertEqual(scope["included_paths"], ["PATH-0000", "PATH-0001"])
            self.assertEqual(scope["omitted_path_count"], 1)
        self.assertEqual(out.canonical.content["statement_scope"], "PARTIAL")
        self.assertEqual(out.canonical.provenance["ai_request_identity"]["request_id"], "REQ-1")
        view = render_view(self.run_dir)
        self.assertIn("PARTIAL", view)
        self.assertIn("SEG-abc", view)

    def test_no_semantic_merge_across_segments(self) -> None:
        self.decide("segmented", "APPROVE")
        self.assertEqual(len(self.store.canonical_records()), 1)
        self.assertTrue(all(r.scope["partial"] for r in self.store.canonical_records()))

    def test_canonical_write_leaves_evidence_and_proposals_untouched(self) -> None:
        before = tree_hash(self.run_dir / "index"), tree_hash(self.run_dir / "proposals")
        self.decide("approve", "APPROVE")
        self.decide("correct", "CORRECT", correction={"statement": "x"})
        self.decide("segmented", "APPROVE")
        self.assertEqual(before, (tree_hash(self.run_dir / "index"), tree_hash(self.run_dir / "proposals")))

    def test_no_knowledge_directory_without_review(self) -> None:
        pending_proposals(self.run_dir)
        self.assertFalse((self.run_dir / "knowledge").exists())

    def test_approval_never_resolves_a_provider(self) -> None:
        from legacy_documenter.orchestration import ai_interpretation

        original = ai_interpretation._resolve_provider
        calls = []
        ai_interpretation._resolve_provider = lambda: calls.append(1)
        try:
            self.decide("approve", "APPROVE")
        finally:
            ai_interpretation._resolve_provider = original
        self.assertEqual(calls, [])


class DeterminismAndQueryTests(ReviewTestCase):
    def test_fixed_clock_gives_identical_bytes_across_independent_runs(self) -> None:
        other = self.tmp / "other"
        build_run(other)
        for target in (self.run_dir, other):
            service = ApprovalService(target, clock=FIXED)
            for key in ("approve", "correct", "reject"):
                service.prepare(self.ids[key], "Ana")
            service.decide(self.ids["approve"], "APPROVE", "Ana", rationale="r")
            service.decide(self.ids["correct"], "CORRECT", "Ana", correction={"statement": "S", "evidence_refs": ["DAO-0001"]})
            service.decide(self.ids["reject"], "REJECT", "Ana")
        self.assertEqual(tree_hash(self.run_dir / "knowledge"), tree_hash(other / "knowledge"))

    def test_real_clock_changes_only_decided_at_and_created_at(self) -> None:
        first = ApprovalService(self.run_dir, clock=lambda: "2026-01-01T00:00:00Z")
        first.prepare(self.ids["approve"], "Ana")
        a = first.decide(self.ids["approve"], "APPROVE", "Ana")
        other = self.tmp / "other"
        build_run(other)
        second = ApprovalService(other, clock=lambda: "2027-01-01T00:00:00Z")
        second.prepare(self.ids["approve"], "Ana")
        b = second.decide(self.ids["approve"], "APPROVE", "Ana")
        da, db = a.decision.to_dict(), b.decision.to_dict()
        self.assertEqual({k: v for k, v in da.items() if k != "decided_at"}, {k: v for k, v in db.items() if k != "decided_at"})
        self.assertEqual(a.canonical.canonical_id, b.canonical.canonical_id)

    def test_queries(self) -> None:
        a = self.decide("approve", "APPROVE").canonical
        self.decide("segmented", "APPROVE")
        self.assertEqual(self.store.canonical_by_id(a.canonical_id), a)
        self.assertEqual(self.store.canonical_for_proposal(self.ids["approve"]), [a])
        self.assertEqual([r.source_proposal_id for r in self.store.canonical_by_evidence_ref("DAO-0001")], [self.ids["segmented"]])
        self.assertEqual(self.store.canonical_records(), sorted(self.store.canonical_records(), key=lambda r: r.canonical_id))
        self.assertEqual(self.store.metrics()["by_action"]["APPROVE"], 2)
        self.assertNotIn("rationale", json.dumps(self.store.metrics()))


class CliTests(ReviewTestCase):
    def run_cli(self, *argv: str) -> tuple[int, str]:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = cli_main(list(argv))
        return code, buffer.getvalue()

    def test_reviewer_is_mandatory_argument(self) -> None:
        with self.assertRaises(SystemExit) as ctx, redirect_stderr(io.StringIO()):
            cli_main(["review", "decide", "--output", str(self.run_dir), "--proposal", self.ids["approve"], "--action", "APPROVE"])
        self.assertEqual(ctx.exception.code, 2)

    def test_decide_and_list_roundtrip(self) -> None:
        code, out = self.run_cli("review", "decide", "--output", str(self.run_dir), "--proposal", self.ids["approve"],
                                 "--action", "APPROVE", "--reviewer", "Ana")
        self.assertEqual((code, json.loads(out)["error_code"]), (4, "BASELINE_REQUIRED"))
        code, out = self.run_cli("review", "prepare", "--output", str(self.run_dir), "--proposal", self.ids["approve"], "--reviewer", "Ana")
        self.assertEqual(code, 0)
        code, out = self.run_cli("review", "decide", "--output", str(self.run_dir), "--proposal", self.ids["approve"],
                                 "--action", "APPROVE", "--reviewer", "Ana")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["provider_calls"], 0)
        code, out = self.run_cli("review", "canonical", "--output", str(self.run_dir), "--proposal", self.ids["approve"])
        self.assertEqual(len(json.loads(out)["canonical"]), 1)
        self.assertTrue((self.run_dir / "knowledge" / "REVIEW_VIEW.md").is_file())

    def test_rejection_exit_code_and_code(self) -> None:
        code, out = self.run_cli("review", "decide", "--output", str(self.run_dir), "--proposal", "PRP-x", "--action", "APPROVE", "--reviewer", "Ana")
        self.assertEqual(code, 4)
        self.assertEqual(json.loads(out)["error_code"], "PROPOSAL_NOT_FOUND")


class ArchitectureGuardTests(unittest.TestCase):
    @staticmethod
    def imports(path: Path) -> set[str]:
        found: set[str] = set()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                found.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                found.add(("." * node.level) + (node.module or ""))
        return found

    def test_review_package_has_no_provider_or_llm_or_pipeline_imports(self) -> None:
        for path in (ROOT / "legacy_documenter" / "review").glob("*.py"):
            for name in self.imports(path):
                self.assertFalse(name.startswith("legacy_documenter.llm"), (path.name, name))
                self.assertNotIn("copilot", name.lower(), (path.name, name))
                self.assertFalse(name.startswith("legacy_documenter.orchestration"), (path.name, name))
                self.assertFalse(name.startswith("legacy_documenter.cli"), (path.name, name))

    def test_pipeline_evidence_and_segmentation_never_reach_review(self) -> None:
        guarded = [*(ROOT / "legacy_documenter" / "evidence").glob("*.py"), *(ROOT / "legacy_documenter" / "knowledge").rglob("*.py"), *(ROOT / "legacy_documenter" / "orchestration").glob("*.py"),
                   *(ROOT / "legacy_documenter" / "llm").rglob("*.py"), ROOT / "legacy_documenter" / "context" / "flow_segmentation.py",
                   ROOT / "legacy_documenter" / "cli" / "full_pipeline.py", ROOT / "legacy_documenter" / "adapters" / "__init__.py"]
        for path in guarded:
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("legacy_documenter.review", text, path.name)
            # V4's in-memory knowledge/approval layer owns a different class with the same name; only guard V5 call sites.
            if "knowledge" not in path.parts:
                self.assertNotIn("ApprovalService", text, path.name)

    def test_only_review_command_imports_the_service(self) -> None:
        users = [p.name for p in (ROOT / "legacy_documenter").rglob("*.py")
                 if "legacy_documenter.review" in p.read_text(encoding="utf-8") and "review" not in p.parent.name]
        # V5.8: the read-only consumer facade reads decisions/canonical through `review.store` and `review.models`
        # (never the service); the mutating service stays reachable only from the explicit human CLI.
        self.assertEqual(sorted(users), ["facade.py", "review_command.py"])
        service_users = [p.name for p in (ROOT / "legacy_documenter").rglob("*.py")
                         if "legacy_documenter.review.service" in p.read_text(encoding="utf-8") and "review" not in p.parent.name]
        self.assertEqual(sorted(service_users), ["review_command.py"])


if __name__ == "__main__":
    unittest.main()
