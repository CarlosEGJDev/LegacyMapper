"""V5.7-R2: review baseline (stale on first decision) and immutable proposal snapshots (synthetic, provider-free)."""
from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout

from legacy_documenter.cli.artifact_lifecycle import reset_stale_proposal_artifacts
from legacy_documenter.main import main as cli_main
from legacy_documenter.review.baseline import ProposalSnapshot
from legacy_documenter.review.models import ReviewErrorCode
from legacy_documenter.review.render import pending_proposals, render_view
from legacy_documenter.review.service import ApprovalService
from tests.test_v5_7_r1_human_review import FIXED, ReviewTestCase, tree_hash


def change_evidence_keep_refs(run_dir) -> None:
    """Same ids/refs, different underlying evidence record."""
    access = run_dir / "index" / "data_access.json"
    data = json.loads(access.read_text(encoding="utf-8"))
    for record in data:
        record["method"] = "ChangedAfterProposal"
    access.write_text(json.dumps(data), encoding="utf-8")


class BaselineRequiredTests(ReviewTestCase):
    def test_no_baseline_no_decision_of_any_kind(self) -> None:
        for name, action, extra in (("approve", "APPROVE", {}), ("correct", "CORRECT", {"correction": {"statement": "x"}}),
                                    ("reject", "REJECT", {}), ("defer", "DEFER", {})):
            with self.subTest(action=action):
                self.assertCode(ReviewErrorCode.BASELINE_REQUIRED, self.service.decide, self.ids[name], action, "Ana", **extra)
        self.assertFalse((self.run_dir / "knowledge").exists())

    def test_prepare_is_idempotent_and_pins_proposal_and_evidence(self) -> None:
        first = self.service.prepare(self.ids["approve"], "Ana")
        before = tree_hash(self.run_dir / "knowledge")
        again = ApprovalService(self.run_dir, clock=lambda: "2031-01-01T00:00:00Z").prepare(self.ids["approve"], "Other Reviewer")
        self.assertEqual(again, first)
        self.assertEqual(before, tree_hash(self.run_dir / "knowledge"))
        self.assertEqual(first.reviewer, "Ana")
        self.assertEqual(first.created_at, "2026-10-07T12:00:00Z")
        self.assertEqual(set(first.evidence_snapshot), {"DAO-0000"})
        self.assertFalse(first.scope["partial"])

    def test_prepare_validates_reviewer(self) -> None:
        self.assertCode(ReviewErrorCode.REVIEWER_REQUIRED, self.service.prepare, self.ids["approve"], " ")
        self.assertCode(ReviewErrorCode.INVALID_DECISION, self.service.prepare, self.ids["approve"], "AUTO")
        self.assertCode(ReviewErrorCode.PROPOSAL_NOT_FOUND, self.service.prepare, "PRP-none", "Ana")

    def test_baseline_does_not_touch_evidence_or_proposals(self) -> None:
        before = tree_hash(self.run_dir / "index"), tree_hash(self.run_dir / "proposals")
        self.service.prepare(self.ids["approve"], "Ana")
        self.assertEqual(before, (tree_hash(self.run_dir / "index"), tree_hash(self.run_dir / "proposals")))


class StaleFirstReviewTests(ReviewTestCase):
    def test_first_approve_is_stale_when_evidence_changes_but_refs_remain(self) -> None:
        self.service.prepare(self.ids["approve"], "Ana")
        change_evidence_keep_refs(self.run_dir)
        self.assertCode(ReviewErrorCode.PROPOSAL_STALE, self.service.decide, self.ids["approve"], "APPROVE", "Ana")
        self.assertEqual((self.store.decisions(), self.store.canonical_records(), self.store.snapshot_for(self.ids["approve"])), ([], [], None))

    def test_first_correct_is_stale_too(self) -> None:
        self.service.prepare(self.ids["correct"], "Ana")
        change_evidence_keep_refs(self.run_dir)
        self.assertCode(ReviewErrorCode.PROPOSAL_STALE, self.service.decide, self.ids["correct"], "CORRECT", "Ana",
                        correction={"statement": "x", "evidence_refs": ["DAO-0000"]})
        self.assertEqual(self.store.canonical_records(), [])

    def test_first_reject_and_defer_are_stale_too(self) -> None:
        for name, action in (("reject", "REJECT"), ("defer", "DEFER")):
            self.service.prepare(self.ids[name], "Ana")
        change_evidence_keep_refs(self.run_dir)
        for name, action in (("reject", "REJECT"), ("defer", "DEFER")):
            self.assertCode(ReviewErrorCode.PROPOSAL_STALE, self.service.decide, self.ids[name], action, "Ana")

    def test_prepare_after_evidence_change_does_not_rebaseline(self) -> None:
        self.service.prepare(self.ids["approve"], "Ana")
        change_evidence_keep_refs(self.run_dir)
        self.assertCode(ReviewErrorCode.PROPOSAL_STALE, self.service.prepare, self.ids["approve"], "Ana")
        self.assertEqual(len(self.store.baselines_for(self.ids["approve"])), 1)

    def test_proposal_change_is_tampered_not_stale(self) -> None:
        self.service.prepare(self.ids["approve"], "Ana")
        def mutate(data):
            data["proposals"][0]["rationale"] = "edited after baseline"
        self.rewrite_proposals(mutate)
        self.assertCode(ReviewErrorCode.PROPOSAL_TAMPERED, self.service.decide, self.ids["approve"], "APPROVE", "Ana")

    def test_unchanged_evidence_succeeds_and_decision_links_baseline(self) -> None:
        baseline = self.service.prepare(self.ids["reject"], "Ana")
        out = self.service.decide(self.ids["reject"], "REJECT", "Ana")
        self.assertEqual(out.decision.baseline_id, baseline.baseline_id)
        self.assertEqual(out.decision.evidence_fingerprint, baseline.evidence_fingerprint)
        self.assertEqual(out.decision.evidence_snapshot, baseline.evidence_snapshot)

    def test_expected_fingerprint_is_an_additional_guard(self) -> None:
        baseline = self.service.prepare(self.ids["approve"], "Ana")
        self.assertCode(ReviewErrorCode.PROPOSAL_STALE, self.service.decide, self.ids["approve"], "APPROVE", "Ana",
                        expected_evidence_fingerprint="0" * 64)
        out = self.service.decide(self.ids["approve"], "APPROVE", "Ana", expected_evidence_fingerprint=baseline.evidence_fingerprint)
        self.assertIsNotNone(out.canonical)

    def test_recheck_right_before_write_catches_a_race(self) -> None:
        run_dir = self.run_dir

        class Racy(ApprovalService):
            def _before_write(self) -> None:
                change_evidence_keep_refs(run_dir)

        Racy(run_dir, clock=FIXED).prepare(self.ids["approve"], "Ana")
        self.assertCode(ReviewErrorCode.PROPOSAL_STALE, Racy(run_dir, clock=FIXED).decide, self.ids["approve"], "APPROVE", "Ana")
        self.assertEqual((self.store.decisions(), self.store.canonical_records(), self.store.snapshot_for(self.ids["approve"])), ([], [], None))

    def test_unchanged_index_skips_full_recompute(self) -> None:
        self.service.prepare(self.ids["approve"], "Ana")
        calls = []
        original = ApprovalService._assert_baseline_current
        ApprovalService._assert_baseline_current = staticmethod(lambda *a: (calls.append(1), original(*a))[1])
        try:
            self.service.decide(self.ids["approve"], "APPROVE", "Ana")
        finally:
            ApprovalService._assert_baseline_current = staticmethod(original)
        self.assertEqual(len(calls), 1)

    def test_fixed_clock_makes_baseline_and_decision_bytes_deterministic(self) -> None:
        other = self.tmp / "other"
        from tests.test_v5_7_r1_human_review import build_run

        build_run(other)
        for target in (self.run_dir, other):
            svc = ApprovalService(target, clock=FIXED)
            svc.prepare(self.ids["approve"], "Ana")
            svc.decide(self.ids["approve"], "APPROVE", "Ana", rationale="r")
        self.assertEqual(tree_hash(self.run_dir / "knowledge"), tree_hash(other / "knowledge"))


class ProposalSnapshotTests(ReviewTestCase):
    def original(self, name: str) -> dict:
        data = json.loads((self.run_dir / "proposals" / "AI_PROPOSALS.json").read_text(encoding="utf-8"))
        return next(p for p in data["proposals"] if p["proposal_id"] == self.ids[name])

    def test_first_decision_creates_snapshot_with_exact_readback(self) -> None:
        self.assertIsNone(self.store.snapshot_for(self.ids["approve"]))
        out = self.decide("approve", "APPROVE")
        snap = self.store.snapshot_for(self.ids["approve"])
        self.assertEqual(snap.proposal, self.original("approve"))
        self.assertEqual(snap.original_status, "READY_FOR_REVIEW")
        self.assertEqual(snap.proposal_fingerprint, out.decision.proposal_fingerprint)
        self.assertEqual(snap.provenance["provider_id"], "fake-provider")
        self.assertEqual(snap.provenance["context_package_id"], "AIP-1")
        self.assertEqual(snap.evidence_fingerprint, out.decision.evidence_fingerprint)
        self.assertEqual(snap.proposal["evidence_refs"], ["DAO-0000"])
        self.assertEqual(ProposalSnapshot.from_dict(snap.to_dict()), snap)

    def test_all_four_actions_preserve_a_snapshot(self) -> None:
        self.decide("approve", "APPROVE")
        self.decide("reject", "REJECT")
        self.decide("correct", "CORRECT", correction={"statement": "Human"})
        self.decide("defer", "DEFER")
        files = sorted(p.name for p in (self.run_dir / "knowledge" / "review_snapshots").glob("*.json"))
        self.assertEqual(files, sorted(f"{self.ids[n]}.json" for n in ("approve", "reject", "correct", "defer")))

    def test_repeated_decision_and_later_decisions_do_not_duplicate_snapshot(self) -> None:
        self.decide("defer", "DEFER", rationale="later")
        self.decide("defer", "DEFER", rationale="later")
        self.decide("defer", "APPROVE")
        self.assertEqual(len(list((self.run_dir / "knowledge" / "review_snapshots").glob("*.json"))), 1)
        self.assertEqual(self.store.metrics()["proposal_snapshots"], 1)

    def test_same_proposal_id_with_different_fingerprint_is_a_conflict(self) -> None:
        self.decide("approve", "APPROVE")
        snap = self.store.snapshot_for(self.ids["approve"])
        forged = ProposalSnapshot(snap.proposal_id, "f" * 64, snap.proposal, snap.original_status, snap.scope, snap.provenance,
                                  snap.baseline_id, snap.evidence_snapshot, snap.evidence_fingerprint)
        self.assertCode(ReviewErrorCode.PROPOSAL_TAMPERED, self.store.write_snapshot, forged)
        self.assertFalse(self.store.write_snapshot(snap))

    def test_altered_snapshot_is_detected_when_artifact_is_gone(self) -> None:
        self.decide("defer", "DEFER")
        reset_stale_proposal_artifacts(self.run_dir)
        target = self.run_dir / "knowledge" / "review_snapshots" / f"{self.ids['defer']}.json"
        data = json.loads(target.read_text(encoding="utf-8"))
        data["proposal"]["statement"] = "edited"
        target.write_text(json.dumps(data), encoding="utf-8")
        self.assertCode(ReviewErrorCode.PROPOSAL_TAMPERED, self.service.decide, self.ids["defer"], "APPROVE", "Ana")

    def test_artifact_differing_from_snapshot_is_tampered(self) -> None:
        self.decide("defer", "DEFER")
        def mutate(data):
            data["proposals"][2]["metadata"] = {"x": 1}
        self.rewrite_proposals(mutate)
        self.assertCode(ReviewErrorCode.PROPOSAL_TAMPERED, self.service.decide, self.ids["defer"], "APPROVE", "Ana")

    def test_segment_snapshot_keeps_partial_metadata(self) -> None:
        self.decide("segmented", "APPROVE")
        snap = self.store.snapshot_for(self.ids["segmented"])
        segment = snap.proposal["metadata"]["flow_segment"]
        self.assertTrue(segment["partial"])
        self.assertEqual((segment["parent_flow_id"], segment["segment_id"]), ("FLOW-1", "SEG-abc"))
        self.assertEqual((segment["included_paths"], segment["omitted_paths"]), (["PATH-0000", "PATH-0001"], ["PATH-0002"]))
        self.assertTrue(snap.scope["partial"])
        self.assertEqual(snap.proposal["metadata"]["ai_request_identity"]["request_id"], "REQ-1")

    def test_snapshot_has_no_secrets_prompts_or_auth(self) -> None:
        self.decide("approve", "APPROVE", rationale="password=Zzz999 Bearer abcdefghijklmnop12345")
        text = "".join(p.read_text(encoding="utf-8") for p in (self.run_dir / "knowledge").rglob("*.json")).lower()
        for marker in ("zzz999", "abcdefghijklmnop12345", "system_instruction", "authorization", "api_key"):
            self.assertNotIn(marker, text)


class SurvivalAndAuditChainTests(ReviewTestCase):
    def decide_all(self) -> dict:
        outs = {"approve": self.decide("approve", "APPROVE"), "reject": self.decide("reject", "REJECT"),
                "correct": self.decide("correct", "CORRECT", correction={"statement": "Human", "evidence_refs": ["DAO-0001"]}),
                "defer": self.decide("defer", "DEFER"), "segmented": self.decide("segmented", "APPROVE")}
        return outs

    def test_full_cleanup_leaves_snapshots_decisions_and_canonical_intact(self) -> None:
        outs = self.decide_all()
        before = tree_hash(self.run_dir / "knowledge")
        reset_stale_proposal_artifacts(self.run_dir)  # what the next `full` does first
        self.assertFalse((self.run_dir / "proposals").exists())
        self.assertEqual(before, tree_hash(self.run_dir / "knowledge"))
        fresh = ApprovalService(self.run_dir, clock=FIXED).store
        self.assertEqual(len(fresh.decisions()), 5)
        self.assertEqual([r.canonical_id for r in fresh.canonical_records()], sorted(o.canonical.canonical_id for o in outs.values() if o.canonical))
        self.assertEqual(pending_proposals(self.run_dir), [])
        self.assertIn("Decisions", render_view(self.run_dir))

    def test_audit_chain_resolves_for_every_action_after_cleanup(self) -> None:
        outs = self.decide_all()
        reset_stale_proposal_artifacts(self.run_dir)
        for name, out in outs.items():
            with self.subTest(name=name):
                chain = self.store.audit_chain(out.decision.decision_id)
                self.assertEqual(chain["decision"], out.decision)
                self.assertEqual(chain["proposal_snapshot"].proposal_id, self.ids[name])
                self.assertEqual(chain["baseline"].baseline_id, out.decision.baseline_id)
                self.assertEqual(chain["evidence_fingerprint"], chain["baseline"].evidence_fingerprint)
                self.assertEqual(chain["canonical"], out.canonical)
                if out.canonical:
                    self.assertEqual(out.canonical.decision_id, chain["decision"].decision_id)

    def test_review_can_continue_after_cleanup_using_the_snapshot(self) -> None:
        self.decide("defer", "DEFER")
        reset_stale_proposal_artifacts(self.run_dir)
        out = self.service.decide(self.ids["defer"], "APPROVE", "Ana")
        self.assertIsNotNone(out.canonical)
        self.assertEqual(out.canonical.provenance["provider_id"], "fake-provider")
        self.assertEqual(self.store.audit_chain(out.decision.decision_id)["proposal_snapshot"].proposal_id, self.ids["defer"])

    def test_broken_audit_chain_is_detected(self) -> None:
        out = self.decide("approve", "APPROVE")
        target = self.run_dir / "knowledge" / "baselines"
        for path in target.glob("*.json"):
            path.unlink()
        self.assertCode(ReviewErrorCode.PROPOSAL_NOT_FOUND, self.store.audit_chain, out.decision.decision_id)

    def test_evidence_index_untouched_by_baseline_decision_canonical_and_snapshot(self) -> None:
        before = tree_hash(self.run_dir / "index")
        self.decide_all()
        reset_stale_proposal_artifacts(self.run_dir)
        self.assertEqual(before, tree_hash(self.run_dir / "index"))

    def test_no_provider_is_resolved(self) -> None:
        from legacy_documenter.orchestration import ai_interpretation

        original = ai_interpretation._resolve_provider
        calls = []
        ai_interpretation._resolve_provider = lambda: calls.append(1)
        try:
            self.decide_all()
        finally:
            ai_interpretation._resolve_provider = original
        self.assertEqual(calls, [])


class CliTests(ReviewTestCase):
    def run_cli(self, *argv: str) -> tuple[int, dict]:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = cli_main(list(argv))
        return code, json.loads(buffer.getvalue())

    def test_prepare_decide_and_chain(self) -> None:
        out_dir = str(self.run_dir)
        code, payload = self.run_cli("review", "prepare", "--output", out_dir, "--reviewer", "Ana")
        self.assertEqual(code, 0)
        self.assertEqual(len(payload["baselines"]), 6)  # every pending proposal
        fingerprint = payload["baselines"][0]["evidence_fingerprint"]
        proposal_id = payload["baselines"][0]["proposal_id"]
        code, payload = self.run_cli("review", "decide", "--output", out_dir, "--proposal", proposal_id, "--action", "APPROVE",
                                     "--reviewer", "Ana", "--expected-evidence-fingerprint", fingerprint)
        self.assertEqual((code, payload["provider_calls"]), (0, 0))
        code, payload = self.run_cli("review", "canonical", "--output", out_dir, "--id", payload["canonical_id"], "--chain")
        chain = payload["audit_chain"]
        self.assertEqual(chain["proposal_snapshot"]["proposal_id"], proposal_id)
        self.assertEqual(chain["baseline"]["evidence_fingerprint"], chain["evidence_fingerprint"])

    def test_list_reports_baseline_state(self) -> None:
        code, payload = self.run_cli("review", "list", "--output", str(self.run_dir))
        self.assertTrue(all(row["baseline_prepared"] is False for row in payload["pending"]))
        self.service.prepare(self.ids["approve"], "Ana")
        code, payload = self.run_cli("review", "list", "--output", str(self.run_dir))
        self.assertEqual(sum(row["baseline_prepared"] for row in payload["pending"]), 1)


if __name__ == "__main__":
    unittest.main()
