"""ReviewBaseline and immutable proposal snapshots (V5.7 R2).

A `ReviewBaseline` pins, before any decision, the exact proposal and the exact evidence it was reviewed
against. A `ProposalSnapshot` keeps the reviewed proposal inside `knowledge/` so the audit chain
(canonical -> decision -> proposal -> evidence) survives a later `full` run that clears `proposals/`.
Both are append-only: identical rewrites are no-ops, different content for the same identity is a conflict.
"""
from __future__ import annotations

from dataclasses import dataclass

from legacy_documenter.documentation.contracts import stable_id

from .models import SCHEMA_VERSION, ReviewError, ReviewErrorCode

BASELINE_SCHEMA = "REVIEW_BASELINE"
SNAPSHOT_SCHEMA = "REVIEW_PROPOSAL_SNAPSHOT"


def baseline_id_for(proposal_id: str, proposal_fingerprint: str, evidence_fingerprint: str) -> str:
    """Stable `BAS-` id; excludes reviewer and time so preparing the same state twice is idempotent."""
    return stable_id("BAS", proposal_id, proposal_fingerprint, evidence_fingerprint)


@dataclass(frozen=True)
class ReviewBaseline:
    """Immutable pre-decision pin of proposal + evidence state."""

    baseline_id: str
    proposal_id: str
    proposal_fingerprint: str
    evidence_snapshot: dict
    evidence_fingerprint: str
    scope: dict
    reviewer: str
    created_at: str

    def to_dict(self) -> dict:
        """Persisted JSON shape (schema REVIEW_BASELINE 1.0)."""
        return {
            "schema": BASELINE_SCHEMA, "schema_version": SCHEMA_VERSION, "baseline_id": self.baseline_id,
            "proposal_id": self.proposal_id, "proposal_fingerprint": self.proposal_fingerprint,
            "evidence_snapshot": dict(sorted(self.evidence_snapshot.items())), "evidence_fingerprint": self.evidence_fingerprint,
            "scope": self.scope, "reviewer": self.reviewer, "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewBaseline":
        """Rebuilds a baseline from persisted JSON, rejecting unknown schemas."""
        if data.get("schema") != BASELINE_SCHEMA or data.get("schema_version") != SCHEMA_VERSION:
            raise ReviewError(ReviewErrorCode.BASELINE_REQUIRED, "unsupported_baseline_schema")
        return cls(data["baseline_id"], data["proposal_id"], data["proposal_fingerprint"], data["evidence_snapshot"],
                   data["evidence_fingerprint"], data["scope"], data["reviewer"], data["created_at"])


@dataclass(frozen=True)
class ProposalSnapshot:
    """Immutable copy of the reviewed proposal (full normalized dict) with its provenance and baseline link."""

    proposal_id: str
    proposal_fingerprint: str
    proposal: dict
    original_status: str
    scope: dict
    provenance: dict
    baseline_id: str
    evidence_snapshot: dict
    evidence_fingerprint: str

    def to_dict(self) -> dict:
        """Persisted JSON shape (schema REVIEW_PROPOSAL_SNAPSHOT 1.0)."""
        return {
            "schema": SNAPSHOT_SCHEMA, "schema_version": SCHEMA_VERSION, "proposal_id": self.proposal_id,
            "proposal_fingerprint": self.proposal_fingerprint, "proposal": self.proposal, "original_status": self.original_status,
            "scope": self.scope, "provenance": self.provenance, "baseline_id": self.baseline_id,
            "evidence_snapshot": dict(sorted(self.evidence_snapshot.items())), "evidence_fingerprint": self.evidence_fingerprint,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProposalSnapshot":
        """Rebuilds a snapshot from persisted JSON, rejecting unknown schemas."""
        if data.get("schema") != SNAPSHOT_SCHEMA or data.get("schema_version") != SCHEMA_VERSION:
            raise ReviewError(ReviewErrorCode.PROPOSAL_TAMPERED, "unsupported_snapshot_schema")
        return cls(data["proposal_id"], data["proposal_fingerprint"], data["proposal"], data["original_status"], data["scope"],
                   data["provenance"], data["baseline_id"], data["evidence_snapshot"], data["evidence_fingerprint"])
