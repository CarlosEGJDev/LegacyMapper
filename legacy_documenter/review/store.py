"""Append-only, atomic, deterministic persistence of decisions and canonical records (V5.7).

Layout under the run directory (created only when a human first decides):

    knowledge/decisions/DEC-<sha256>.json
    knowledge/canonical/CAN-<sha256>.json

Files are never deleted or overwritten with different content: an identical write is a no-op, a different
payload for an existing id is a conflict. Readback re-validates ids against content.
"""
from __future__ import annotations

from pathlib import Path

import json

from legacy_documenter.utils.atomic_write import atomic_write_text
from legacy_documenter.utils.json_rendering import render_deterministic_json

from .baseline import ProposalSnapshot, ReviewBaseline
from .models import CanonicalKnowledgeRecord, HumanDecision, ReviewError, ReviewErrorCode

DECISIONS_DIR = Path("knowledge") / "decisions"
CANONICAL_DIR = Path("knowledge") / "canonical"
BASELINES_DIR = Path("knowledge") / "baselines"
SNAPSHOTS_DIR = Path("knowledge") / "review_snapshots"


class ReviewStore:
    """Filesystem store rooted at one run (`--output`) directory."""

    def __init__(self, run_dir: str | Path) -> None:
        self.run_dir = Path(run_dir)
        self.decisions_dir = self.run_dir / DECISIONS_DIR
        self.canonical_dir = self.run_dir / CANONICAL_DIR
        self.baselines_dir = self.run_dir / BASELINES_DIR
        self.snapshots_dir = self.run_dir / SNAPSHOTS_DIR

    # -- writes -----------------------------------------------------------------------------------
    def _write_new(self, target: Path, payload: dict, conflict_code: ReviewErrorCode) -> bool:
        """Creates `target`; returns False on identical replay; raises on conflicting content."""
        text = render_deterministic_json(payload) + "\n"
        if target.exists():
            if target.read_text(encoding="utf-8") == text:
                return False
            raise ReviewError(conflict_code, f"existing_record_differs:{target.stem}")
        target.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(target, text)
        return True

    def write_decision(self, decision: HumanDecision) -> bool:
        """Appends a decision; False on identical replay, DUPLICATE_DECISION on conflicting content."""
        return self._write_new(self.decisions_dir / f"{decision.decision_id}.json", decision.to_dict(), ReviewErrorCode.DUPLICATE_DECISION)

    def write_canonical(self, record: CanonicalKnowledgeRecord) -> bool:
        """Appends a canonical record; False on identical replay, CANONICAL_CONFLICT on conflicting content."""
        return self._write_new(self.canonical_dir / f"{record.canonical_id}.json", record.to_dict(), ReviewErrorCode.CANONICAL_CONFLICT)

    def write_baseline(self, baseline: ReviewBaseline) -> bool:
        """Appends a baseline; False on identical replay (reviewer/time of the first preparation are kept)."""
        target = self.baselines_dir / f"{baseline.baseline_id}.json"
        if target.exists():
            return False
        return self._write_new(target, baseline.to_dict(), ReviewErrorCode.BASELINE_REQUIRED)

    def write_snapshot(self, snapshot: ProposalSnapshot) -> bool:
        """Appends the reviewed-proposal snapshot; same id with different fingerprint is PROPOSAL_TAMPERED."""
        target = self.snapshots_dir / f"{snapshot.proposal_id}.json"
        if target.exists():
            if json.loads(target.read_text(encoding="utf-8")).get("proposal_fingerprint") != snapshot.proposal_fingerprint:
                raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, f"snapshot_fingerprint_conflict:{snapshot.proposal_id}")
            return False
        return self._write_new(target, snapshot.to_dict(), ReviewErrorCode.PROPOSAL_TAMPERED)

    # -- reads ------------------------------------------------------------------------------------
    @staticmethod
    def _read_all(directory: Path, loader) -> list:
        if not directory.is_dir():
            return []
        items = []
        for path in sorted(directory.glob("*.json")):
            item = loader(json.loads(path.read_text(encoding="utf-8")))
            items.append(item)
        return items

    def decisions(self) -> list[HumanDecision]:
        """All decisions, stable order (decided_at, decision_id)."""
        return sorted(self._read_all(self.decisions_dir, HumanDecision.from_dict), key=lambda d: (d.decided_at, d.decision_id))

    def decisions_for(self, proposal_id: str) -> list[HumanDecision]:
        """Decision history of one proposal in chain order (each links to its previous decision)."""
        items = {d.decision_id: d for d in self.decisions() if d.proposal_id == proposal_id}
        ordered: list[HumanDecision] = []
        previous = None
        while True:
            nxt = [d for d in items.values() if d.previous_decision_id == previous]
            if not nxt:
                break
            if len(nxt) > 1:
                raise ReviewError(ReviewErrorCode.DUPLICATE_DECISION, f"forked_decision_history:{proposal_id}")
            ordered.append(nxt[0])
            previous = nxt[0].decision_id
        if len(ordered) != len(items):
            raise ReviewError(ReviewErrorCode.DUPLICATE_DECISION, f"broken_decision_history:{proposal_id}")
        return ordered

    def canonical_records(self) -> list[CanonicalKnowledgeRecord]:
        """All canonical records ordered by canonical_id."""
        return sorted(self._read_all(self.canonical_dir, CanonicalKnowledgeRecord.from_dict), key=lambda r: r.canonical_id)

    def canonical_by_id(self, canonical_id: str) -> CanonicalKnowledgeRecord | None:
        """The record with this id, or None."""
        return next((r for r in self.canonical_records() if r.canonical_id == canonical_id), None)

    def canonical_for_proposal(self, proposal_id: str) -> list[CanonicalKnowledgeRecord]:
        """Canonical records derived from this proposal."""
        return [r for r in self.canonical_records() if r.source_proposal_id == proposal_id]

    def canonical_by_evidence_ref(self, ref: str) -> list[CanonicalKnowledgeRecord]:
        """Canonical records citing this evidence ref."""
        return [r for r in self.canonical_records() if ref in r.evidence_refs]

    def baselines_for(self, proposal_id: str) -> list[ReviewBaseline]:
        """Baselines pinned for this proposal, stable order."""
        items = self._read_all(self.baselines_dir, ReviewBaseline.from_dict)
        return sorted((b for b in items if b.proposal_id == proposal_id), key=lambda b: b.baseline_id)

    def snapshot_for(self, proposal_id: str) -> ProposalSnapshot | None:
        """The immutable reviewed-proposal snapshot, or None before the first decision."""
        target = self.snapshots_dir / f"{proposal_id}.json"
        return ProposalSnapshot.from_dict(json.loads(target.read_text(encoding="utf-8"))) if target.is_file() else None

    def audit_chain(self, decision_id: str) -> dict:
        """Reconstructs decision -> proposal snapshot -> baseline/evidence (+ canonical), verifying every link."""
        decision = next((d for d in self.decisions() if d.decision_id == decision_id), None)
        if decision is None:
            raise ReviewError(ReviewErrorCode.INVALID_DECISION, f"decision_not_found:{decision_id}")
        snapshot = self.snapshot_for(decision.proposal_id)
        baseline = next((b for b in self.baselines_for(decision.proposal_id) if b.baseline_id == decision.baseline_id), None)
        if snapshot is None or baseline is None:
            raise ReviewError(ReviewErrorCode.PROPOSAL_NOT_FOUND, "audit_chain_incomplete")
        if (snapshot.proposal_fingerprint != decision.proposal_fingerprint or baseline.proposal_fingerprint != decision.proposal_fingerprint
                or snapshot.baseline_id != baseline.baseline_id):
            raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, "audit_chain_fingerprint_mismatch")
        canonical = next((r for r in self.canonical_for_proposal(decision.proposal_id) if r.decision_id == decision_id), None)
        return {"decision": decision, "proposal_snapshot": snapshot, "baseline": baseline, "canonical": canonical,
                "evidence_fingerprint": baseline.evidence_fingerprint}

    def metrics(self) -> dict:
        """Safe counters only: never rationale or correction text."""
        decisions = self.decisions()
        counts = {action: 0 for action in ("APPROVE", "REJECT", "CORRECT", "DEFER")}
        for decision in decisions:
            counts[decision.action.value] += 1
        return {"reviewed_proposals": len({d.proposal_id for d in decisions}), "decisions": len(decisions), "by_action": counts,
                "canonical_records": len(self.canonical_records()),
                "proposal_snapshots": len(list(self.snapshots_dir.glob("*.json"))) if self.snapshots_dir.is_dir() else 0}
