"""ApprovalService: validates and applies one explicit human decision (V5.7).

Deterministic and provider-free: no LLM, network or provider object is ever imported or called here.
The proposal artifact and Evidence are read-only inputs; this service only appends decision/canonical
records through `ReviewStore`. It is never invoked by the pipeline: a human must call it (CLI or API).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from legacy_documenter.knowledge.proposals.enums import ProposalKind, ProposalMethod, ProposalStatus
from legacy_documenter.knowledge.proposals.models import new_proposal_id

from .baseline import ProposalSnapshot, ReviewBaseline, baseline_id_for
from .evidence import EvidenceIndex, evidence_fingerprint
from .models import (
    CANONICAL_ACTIONS, TERMINAL_ACTIONS, CanonicalKnowledgeRecord, DecisionAction, HumanDecision, ReviewError,
    ReviewErrorCode, canonical_id_for, clean_text, decision_id_for, fingerprint, validate_reviewer,
)
from .store import ReviewStore

PROPOSALS_FILE = Path("proposals") / "AI_PROPOSALS.json"
CORRECTION_KEYS = {"statement", "evidence_refs"}


def utc_clock() -> str:
    """Default human-act clock (UTC, seconds). Tests inject a fixed clock."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class DecisionOutcome:
    """Result of `ApprovalService.decide`."""

    decision: HumanDecision
    canonical: CanonicalKnowledgeRecord | None
    idempotent_replay: bool


def load_proposals(run_dir: str | Path) -> tuple[dict, list[dict]]:
    """Reads the persisted proposal envelope (read-only)."""
    path = Path(run_dir) / PROPOSALS_FILE
    if not path.is_file():
        raise ReviewError(ReviewErrorCode.PROPOSAL_NOT_FOUND, "proposals_artifact_missing")
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
        proposals = envelope["proposals"]
    except (ValueError, KeyError, TypeError):
        raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, "proposals_artifact_unreadable") from None
    if not isinstance(proposals, list):
        raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, "proposals_not_a_list")
    return envelope, proposals


def scope_of(proposal: dict) -> dict:
    """Deterministic scope summary: COMPLETE, or PARTIAL with parent/segment and included/omitted counts."""
    segment = (proposal.get("metadata") or {}).get("flow_segment")
    if not segment:
        return {"partial": False, "completeness": "COMPLETE"}
    return {
        "partial": True, "completeness": "PARTIAL", "parent_flow_id": segment["parent_flow_id"], "segment_id": segment["segment_id"],
        "included_paths": list(segment["included_paths"]), "omitted_path_count": len(segment["omitted_paths"]),
        "included_path_count": len(segment["included_paths"]),
    }


def verify_integrity(proposal: dict) -> str:
    """Raises PROPOSAL_TAMPERED unless the proposal still matches its own identity and partial semantics.

    Returns the whole-proposal fingerprint (content + metadata) recorded in every decision.
    """
    try:
        recomputed = new_proposal_id(
            ProposalKind(proposal["proposal_kind"]), proposal["statement"], ProposalMethod(proposal["proposal_method"]),
            tuple(proposal.get("material_ids", [])), tuple(proposal.get("relation_ids", [])), tuple(proposal.get("evidence_refs", [])),
        )
    except (KeyError, ValueError):
        raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, "proposal_malformed") from None
    if recomputed != proposal.get("proposal_id"):
        raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, "proposal_id_does_not_match_content")
    if proposal.get("status") != ProposalStatus.READY_FOR_REVIEW.value:
        raise ReviewError(ReviewErrorCode.INVALID_TRANSITION, f"proposal_not_ready_for_review:{proposal.get('status')}")
    segment = (proposal.get("metadata") or {}).get("flow_segment")
    if segment is not None:
        included, omitted = set(segment.get("included_paths") or []), set(segment.get("omitted_paths") or [])
        if (segment.get("partial") is not True or not included or not omitted or included & omitted
                or not segment.get("segment_id") or not segment.get("parent_flow_id")):
            raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, "segment_partial_semantics_violated")
        if proposal["statement"].split(":", 1)[0] != f"Partial segment {segment['segment_id']} of {segment['parent_flow_id']}":
            raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, "segment_scope_label_missing")
    return fingerprint(proposal)


class ApprovalService:
    """Applies explicit human decisions to persisted proposals of one run directory."""

    def __init__(self, run_dir: str | Path, clock: Callable[[], str] = utc_clock) -> None:
        self.run_dir = Path(run_dir)
        self.store = ReviewStore(self.run_dir)
        self.clock = clock

    def _resolve_proposal(self, proposal_id: str) -> tuple[dict, dict]:
        """(envelope provenance, proposal) from `proposals/` or, once cleared by a later `full`, the review snapshot."""
        snapshot = self.store.snapshot_for(proposal_id)
        try:
            envelope, proposals = load_proposals(self.run_dir)
        except ReviewError as exc:
            if exc.code is not ReviewErrorCode.PROPOSAL_NOT_FOUND or snapshot is None:
                raise
            envelope, proposals = {}, []
        proposal = next((p for p in proposals if isinstance(p, dict) and p.get("proposal_id") == proposal_id), None)
        if proposal is not None:
            if snapshot is not None and fingerprint(proposal) != snapshot.proposal_fingerprint:
                raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, "proposal_differs_from_review_snapshot")
            return {k: envelope.get(k) for k in ("provider_id", "model_id", "context_package_id")}, proposal
        if snapshot is None:
            raise ReviewError(ReviewErrorCode.PROPOSAL_NOT_FOUND, str(proposal_id))
        if fingerprint(snapshot.proposal) != snapshot.proposal_fingerprint:
            raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, "review_snapshot_content_altered")
        return {k: snapshot.provenance.get(k) for k in ("provider_id", "model_id", "context_package_id")}, snapshot.proposal

    def prepare(self, proposal_id: str, reviewer: str) -> ReviewBaseline:
        """Pins the review baseline (proposal + evidence fingerprints). Required before the first decision.

        Idempotent for an unchanged state; if evidence already differs from an existing baseline the
        proposal is STALE and no new baseline is ever created over it.
        """
        envelope, proposal = self._resolve_proposal(proposal_id)
        reviewer = validate_reviewer(reviewer, {envelope.get("provider_id"), envelope.get("model_id")})
        proposal_fp = verify_integrity(proposal)
        index = EvidenceIndex(self.run_dir)
        snapshot = index.snapshot(proposal.get("evidence_refs", []))
        scope = scope_of(proposal)
        self._check_grounding(proposal, index, list(proposal.get("evidence_refs", [])), scope)
        evidence_fp = evidence_fingerprint(snapshot)
        existing = self.store.baselines_for(proposal_id)
        for baseline in existing:
            if baseline.proposal_fingerprint != proposal_fp:
                raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, "proposal_changed_since_baseline")
            if baseline.evidence_fingerprint != evidence_fp:
                raise ReviewError(ReviewErrorCode.PROPOSAL_STALE, "evidence_changed_since_baseline")
        if existing:
            return existing[0]
        baseline = ReviewBaseline(baseline_id_for(proposal_id, proposal_fp, evidence_fp), proposal_id, proposal_fp, snapshot,
                                  evidence_fp, scope, reviewer, self.clock())
        self.store.write_baseline(baseline)
        return baseline

    def _before_write(self) -> None:
        """Seam executed right before persistence (tests use it to simulate a concurrent evidence change)."""

    def decide(self, proposal_id: str, action: DecisionAction | str, reviewer: str, *, rationale: str | None = None,
               correction: dict | None = None, expected_evidence_fingerprint: str | None = None) -> DecisionOutcome:
        """Validates and persists one decision (and canonical knowledge for APPROVE/CORRECT). Fails closed.

        Every decision, first or later, needs a verifiable `ReviewBaseline` (see `prepare`): without it
        nothing is written. The current evidence must still match that baseline, immediately before writing too.
        """
        action = self._action(action)
        envelope, proposal = self._resolve_proposal(proposal_id)
        provenance = self._provenance(envelope, proposal)
        reviewer = validate_reviewer(reviewer, {provenance.get("provider_id"), provenance.get("model_id")})
        rationale = clean_text(rationale, "rationale", ReviewErrorCode.INVALID_DECISION)
        if action is not DecisionAction.CORRECT and correction is not None:
            raise ReviewError(ReviewErrorCode.INVALID_DECISION, "correction_only_allowed_with_CORRECT")
        proposal_fp = verify_integrity(proposal)
        scope = scope_of(proposal)

        baselines = self.store.baselines_for(proposal_id)
        if not baselines:
            raise ReviewError(ReviewErrorCode.BASELINE_REQUIRED, "run_review_prepare_before_the_first_decision")
        baseline = baselines[0]
        if baseline.proposal_fingerprint != proposal_fp:
            raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, "proposal_changed_since_baseline")

        index = EvidenceIndex(self.run_dir)
        final_refs = list(proposal.get("evidence_refs", []))
        clean_correction = None
        if action is DecisionAction.CORRECT:
            clean_correction = self._validate_correction(correction)
            final_refs = clean_correction.get("evidence_refs") or final_refs
        refs_to_snapshot = sorted(set(proposal.get("evidence_refs", [])) | set(final_refs))
        snapshot = index.snapshot(refs_to_snapshot)
        self._check_grounding(proposal, index, final_refs, scope)
        evidence_fp = evidence_fingerprint(snapshot)
        self._assert_baseline_current(baseline, proposal, snapshot)

        history = self.store.decisions_for(proposal_id)
        for earlier in history:
            if earlier.proposal_fingerprint != proposal_fp:
                raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, "proposal_changed_since_previous_decision")
        seen = evidence_fingerprint({r: snapshot[r] for r in proposal.get("evidence_refs", [])})
        if expected_evidence_fingerprint is not None and expected_evidence_fingerprint != seen:
            raise ReviewError(ReviewErrorCode.PROPOSAL_STALE, "evidence_changed_since_reviewer_view")
        for earlier in history:
            shared = {r for r in snapshot if r in earlier.evidence_snapshot}
            if any(snapshot[r] != earlier.evidence_snapshot[r] for r in shared):
                raise ReviewError(ReviewErrorCode.PROPOSAL_STALE, "evidence_changed_since_previous_decision")

        decision_id = decision_id_for(proposal_id, action.value, reviewer, rationale, clean_correction, proposal_fp, evidence_fp)
        replay = next((d for d in history if d.decision_id == decision_id), None)
        if replay is not None:
            record = self._build_canonical(replay, proposal, self._final_refs(replay, proposal)) if replay.action in CANONICAL_ACTIONS else None
            if record is not None:
                self.store.write_canonical(record)  # idempotent; repairs a crash between decision and canonical writes
            return DecisionOutcome(replay, record, True)
        if history and history[-1].action in TERMINAL_ACTIONS:
            code = ReviewErrorCode.DUPLICATE_DECISION if history[-1].action is action else ReviewErrorCode.INVALID_TRANSITION
            raise ReviewError(code, f"proposal_already_{history[-1].action.value}")
        if history and history[-1].action is DecisionAction.DEFER and action is DecisionAction.DEFER and not rationale:
            raise ReviewError(ReviewErrorCode.DUPLICATE_DECISION, "repeated_defer_requires_new_rationale")

        decision = HumanDecision(
            decision_id=decision_id, proposal_id=proposal_id, action=action, reviewer=reviewer, decided_at=self.clock(),
            proposal_fingerprint=proposal_fp, evidence_snapshot=snapshot, evidence_fingerprint=evidence_fp, scope=scope,
            provenance=provenance, rationale=rationale, correction=clean_correction,
            previous_decision_id=history[-1].decision_id if history else None, baseline_id=baseline.baseline_id,
        )
        record = self._build_canonical(decision, proposal, final_refs) if action in CANONICAL_ACTIONS else None
        if record is not None:
            existing = self.store.canonical_for_proposal(proposal_id)
            if existing:
                raise ReviewError(ReviewErrorCode.CANONICAL_CONFLICT, f"canonical_already_exists:{existing[0].canonical_id}")
        proposal_snapshot = ProposalSnapshot(
            proposal_id, proposal_fp, proposal, proposal.get("status"), scope, provenance, baseline.baseline_id,
            baseline.evidence_snapshot, baseline.evidence_fingerprint)
        self._before_write()
        # Optimistic recheck right before persisting: cheap stat check, full recompute only if an index file changed.
        if not index.is_unchanged():
            fresh = EvidenceIndex(self.run_dir)
            self._assert_baseline_current(baseline, proposal, fresh.snapshot(refs_to_snapshot))
        if [d.decision_id for d in self.store.decisions_for(proposal_id)] != [d.decision_id for d in history]:
            raise ReviewError(ReviewErrorCode.DUPLICATE_DECISION, "concurrent_decision_detected")
        self.store.write_snapshot(proposal_snapshot)
        self.store.write_decision(decision)
        if record is not None:
            self.store.write_canonical(record)
        return DecisionOutcome(decision, record, False)

    @staticmethod
    def _assert_baseline_current(baseline: ReviewBaseline, proposal: dict, current: dict) -> None:
        """PROPOSAL_STALE unless the proposal's evidence still fingerprints exactly as it did at baseline."""
        refs = proposal.get("evidence_refs", [])
        if evidence_fingerprint({r: current[r] for r in refs}) != baseline.evidence_fingerprint:
            raise ReviewError(ReviewErrorCode.PROPOSAL_STALE, "evidence_changed_since_baseline")

    # -- helpers ----------------------------------------------------------------------------------
    @staticmethod
    def _action(action: object) -> DecisionAction:
        try:
            return action if isinstance(action, DecisionAction) else DecisionAction(str(action).upper())
        except ValueError:
            raise ReviewError(ReviewErrorCode.INVALID_DECISION, "action_must_be_APPROVE_REJECT_CORRECT_or_DEFER") from None

    @staticmethod
    def _provenance(envelope: dict, proposal: dict) -> dict:
        metadata = proposal.get("metadata") or {}
        return {
            "proposal_method": proposal.get("proposal_method"), "proposal_kind": proposal.get("proposal_kind"),
            "provider_id": envelope.get("provider_id"), "model_id": envelope.get("model_id"),
            "context_package_id": envelope.get("context_package_id"),
            "ai_request_identity": metadata.get("ai_request_identity"), "source": PROPOSALS_FILE.as_posix(),
        }

    @staticmethod
    def _final_refs(decision: HumanDecision, proposal: dict) -> list[str]:
        if decision.action is DecisionAction.CORRECT and decision.correction.get("evidence_refs"):
            return list(decision.correction["evidence_refs"])
        return list(proposal.get("evidence_refs", []))

    @staticmethod
    def _validate_correction(correction: object) -> dict:
        if correction is None:
            raise ReviewError(ReviewErrorCode.CORRECTION_REQUIRED, "CORRECT_requires_human_correction_payload")
        if not isinstance(correction, dict) or set(correction) - CORRECTION_KEYS or "statement" not in correction:
            raise ReviewError(ReviewErrorCode.CORRECTION_INVALID, "payload_must_be_object_with_statement_and_optional_evidence_refs")
        statement = clean_text(correction["statement"], "correction_statement", ReviewErrorCode.CORRECTION_INVALID, required=True)
        result: dict = {"statement": statement}
        if "evidence_refs" in correction:
            refs = correction["evidence_refs"]
            if (not isinstance(refs, list) or not refs or any(not isinstance(r, str) or not r.strip() for r in refs)
                    or len(set(refs)) != len(refs)):
                raise ReviewError(ReviewErrorCode.CORRECTION_INVALID, "evidence_refs_must_be_unique_non_empty_strings")
            result["evidence_refs"] = sorted(r.strip() for r in refs)
        return result

    @staticmethod
    def _check_grounding(proposal: dict, index: EvidenceIndex, final_refs: list[str], scope: dict) -> None:
        if not proposal.get("evidence_refs") or not final_refs:
            raise ReviewError(ReviewErrorCode.INVALID_GROUNDING, "proposal_has_no_evidence_refs")
        if scope["partial"]:
            allowed = index.segment_scope_refs((proposal["metadata"])["flow_segment"])
            outside = sorted((set(proposal["evidence_refs"]) | set(final_refs)) - allowed)
            if outside:
                raise ReviewError(ReviewErrorCode.INVALID_GROUNDING, "refs_outside_segment_scope:" + ",".join(outside[:5]))

    def _build_canonical(self, decision: HumanDecision, proposal: dict, final_refs: list[str]) -> CanonicalKnowledgeRecord:
        corrected = decision.action is DecisionAction.CORRECT
        content = {"statement": decision.correction["statement"] if corrected else proposal["statement"], "kind": proposal["proposal_kind"]}
        if decision.scope.get("partial"):
            content["statement_scope"] = "PARTIAL"
        refs = tuple(sorted(final_refs))
        provenance = ({
            **decision.provenance, "decided_by": decision.reviewer, "decided_at": decision.decided_at,
            "proposal_fingerprint": decision.proposal_fingerprint, "evidence_fingerprint": decision.evidence_fingerprint,
            "authored_by": "HUMAN_CORRECTION" if corrected else "AI_PROPOSAL_ACCEPTED_BY_HUMAN",
        })
        return CanonicalKnowledgeRecord(
            canonical_id=canonical_id_for(decision.proposal_id, decision.decision_id, content, list(refs)),
            source_proposal_id=decision.proposal_id, decision_id=decision.decision_id, decision_action=decision.action,
            content=content, evidence_refs=refs, scope=decision.scope, provenance=provenance, created_at=decision.decided_at,
            corrected_from={"statement": proposal["statement"], "evidence_refs": list(proposal.get("evidence_refs", []))} if corrected else None,
        )
