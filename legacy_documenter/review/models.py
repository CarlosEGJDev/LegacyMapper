"""HumanDecision / CanonicalKnowledgeRecord contracts, error model and deterministic identities (V5.7)."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum

from legacy_documenter.documentation.contracts import stable_id

DECISION_SCHEMA = "HUMAN_DECISION"
CANONICAL_SCHEMA = "CANONICAL_KNOWLEDGE"
SCHEMA_VERSION = "1.0"
MAX_TEXT_CHARS = 4000
MAX_REVIEWER_CHARS = 120


class DecisionAction(str, Enum):
    """The four explicit human outcomes. No automatic origin exists."""

    APPROVE = "APPROVE"
    REJECT = "REJECT"
    CORRECT = "CORRECT"
    DEFER = "DEFER"


#: Actions that end a proposal's review history. DEFER is the only non-terminal one.
TERMINAL_ACTIONS = frozenset({DecisionAction.APPROVE, DecisionAction.REJECT, DecisionAction.CORRECT})
#: Actions that materialize canonical knowledge.
CANONICAL_ACTIONS = frozenset({DecisionAction.APPROVE, DecisionAction.CORRECT})


class ReviewErrorCode(str, Enum):
    """Fail-closed error vocabulary of the review layer."""

    PROPOSAL_NOT_FOUND = "PROPOSAL_NOT_FOUND"
    PROPOSAL_STALE = "PROPOSAL_STALE"
    PROPOSAL_TAMPERED = "PROPOSAL_TAMPERED"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    INVALID_GROUNDING = "INVALID_GROUNDING"
    INVALID_DECISION = "INVALID_DECISION"
    INVALID_TRANSITION = "INVALID_TRANSITION"
    REVIEWER_REQUIRED = "REVIEWER_REQUIRED"
    CORRECTION_REQUIRED = "CORRECTION_REQUIRED"
    CORRECTION_INVALID = "CORRECTION_INVALID"
    CANONICAL_CONFLICT = "CANONICAL_CONFLICT"
    DUPLICATE_DECISION = "DUPLICATE_DECISION"
    BASELINE_REQUIRED = "BASELINE_REQUIRED"


class ReviewError(Exception):
    """Raised for every rejected review operation; `code` is the stable machine-readable reason."""

    def __init__(self, code: ReviewErrorCode, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code.value}: {detail}" if detail else code.value)


#: Reviewer names that can never denote a human decision-maker.
FORBIDDEN_REVIEWERS = frozenset({"auto", "automatic", "system", "ai", "llm", "model", "provider", "bot", "none", "null", "unknown", "n/a"})
_CONTROL = re.compile(r"[\x00-\x1f\x7f]")
_TOKEN_PATTERNS = (
    re.compile(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(r"(?i)\b(api[_-]?key|secret|authorization|auth[_-]?token|access[_-]?token)\s*[:=]\s*\S+"),
    re.compile(r"\b(?:sk-|ghp_|gho_|xox[bap]-)[A-Za-z0-9_-]{16,}"),
)


def canonical_json(value: object) -> str:
    """Deterministic JSON used for every fingerprint."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    """SHA-256 hex digest of UTF-8 text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fingerprint(value: object) -> str:
    """Fingerprint of a JSON-serializable value over its canonical JSON."""
    return sha256_text(canonical_json(value))


def decision_id_for(proposal_id: str, action: str, reviewer: str, rationale: str | None, correction: dict | None,
                    proposal_fingerprint: str, evidence_fingerprint: str) -> str:
    """Stable `DEC-` id; excludes `decided_at` so replaying the same human decision is idempotent."""
    return stable_id("DEC", proposal_id, action, reviewer, rationale or "", canonical_json(correction) if correction else "",
                     proposal_fingerprint, evidence_fingerprint)


def canonical_id_for(proposal_id: str, decision_id: str, content: dict, evidence_refs: list[str]) -> str:
    """Stable `CAN-` id from proposal + decision + final content + refs; no time, random or provider data."""
    return stable_id("CAN", proposal_id, decision_id, canonical_json(content), list(evidence_refs))


@dataclass(frozen=True)
class HumanDecision:
    """One persisted human decision over one proposal version. Frozen; history is append-only."""

    decision_id: str
    proposal_id: str
    action: DecisionAction
    reviewer: str
    decided_at: str
    proposal_fingerprint: str
    evidence_snapshot: dict
    evidence_fingerprint: str
    scope: dict
    provenance: dict
    rationale: str | None = None
    correction: dict | None = None
    previous_decision_id: str | None = None
    baseline_id: str | None = None

    def to_dict(self) -> dict:
        """Persisted JSON shape (schema HUMAN_DECISION 1.0)."""
        return {
            "schema": DECISION_SCHEMA, "schema_version": SCHEMA_VERSION, "decision_id": self.decision_id,
            "proposal_id": self.proposal_id, "action": self.action.value, "reviewer": self.reviewer,
            "decided_at": self.decided_at, "rationale": self.rationale, "correction": self.correction,
            "previous_decision_id": self.previous_decision_id, "baseline_id": self.baseline_id, "proposal_fingerprint": self.proposal_fingerprint,
            "evidence_snapshot": dict(sorted(self.evidence_snapshot.items())), "evidence_fingerprint": self.evidence_fingerprint,
            "scope": self.scope, "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HumanDecision":
        """Rebuilds a decision from its persisted JSON, rejecting unknown schema versions."""
        if data.get("schema") != DECISION_SCHEMA or data.get("schema_version") != SCHEMA_VERSION:
            raise ReviewError(ReviewErrorCode.INVALID_DECISION, "unsupported_decision_schema")
        return cls(
            decision_id=data["decision_id"], proposal_id=data["proposal_id"], action=DecisionAction(data["action"]),
            reviewer=data["reviewer"], decided_at=data["decided_at"], proposal_fingerprint=data["proposal_fingerprint"],
            evidence_snapshot=data["evidence_snapshot"], evidence_fingerprint=data["evidence_fingerprint"],
            scope=data["scope"], provenance=data["provenance"], rationale=data.get("rationale"),
            correction=data.get("correction"), previous_decision_id=data.get("previous_decision_id"),
            baseline_id=data.get("baseline_id"),
        )


@dataclass(frozen=True)
class CanonicalKnowledgeRecord:
    """Accepted knowledge: separate from Evidence and from the historical proposal; references both."""

    canonical_id: str
    source_proposal_id: str
    decision_id: str
    decision_action: DecisionAction
    content: dict
    evidence_refs: tuple[str, ...]
    scope: dict
    provenance: dict
    created_at: str
    version: int = 1
    status: str = "ACTIVE"
    supersedes: str | None = None
    corrected_from: dict | None = None

    def to_dict(self) -> dict:
        """Persisted JSON shape (schema CANONICAL_KNOWLEDGE 1.0)."""
        return {
            "schema": CANONICAL_SCHEMA, "schema_version": SCHEMA_VERSION, "canonical_id": self.canonical_id,
            "source_proposal_id": self.source_proposal_id, "decision_id": self.decision_id,
            "decision_action": self.decision_action.value, "content": self.content, "evidence_refs": list(self.evidence_refs),
            "scope": self.scope, "provenance": self.provenance, "created_at": self.created_at, "version": self.version,
            "status": self.status, "supersedes": self.supersedes, "corrected_from": self.corrected_from,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CanonicalKnowledgeRecord":
        """Rebuilds a canonical record from its persisted JSON, rejecting unknown schema versions."""
        if data.get("schema") != CANONICAL_SCHEMA or data.get("schema_version") != SCHEMA_VERSION:
            raise ReviewError(ReviewErrorCode.CANONICAL_CONFLICT, "unsupported_canonical_schema")
        return cls(
            canonical_id=data["canonical_id"], source_proposal_id=data["source_proposal_id"], decision_id=data["decision_id"],
            decision_action=DecisionAction(data["decision_action"]), content=data["content"],
            evidence_refs=tuple(data["evidence_refs"]), scope=data["scope"], provenance=data["provenance"],
            created_at=data["created_at"], version=data["version"], status=data["status"],
            supersedes=data.get("supersedes"), corrected_from=data.get("corrected_from"),
        )


def redact_secrets(text: str) -> str:
    """Centralized sanitizer plus token/auth-header patterns; control characters become spaces."""
    from legacy_documenter.utils.sanitizer import sanitize_text

    text = sanitize_text(text)
    for pattern in _TOKEN_PATTERNS:
        text = pattern.sub("********", text)
    return _CONTROL.sub(" ", text)


def clean_text(value: object, field_name: str, code: ReviewErrorCode, *, required: bool = False) -> str | None:
    """Sanitizes human free text (rationale/correction): treated as data, secret-redacted, bounded."""
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            raise ReviewError(code, f"{field_name}_required")
        return None
    if not isinstance(value, str):
        raise ReviewError(code, f"{field_name}_must_be_text")
    text = redact_secrets(value.strip())
    if len(text) > MAX_TEXT_CHARS:
        raise ReviewError(code, f"{field_name}_too_long")
    return text


def validate_reviewer(reviewer: object, provenance_names: set[str]) -> str:
    """A reviewer must be an explicit, non-automatic, non-provider/model human identity."""
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ReviewError(ReviewErrorCode.REVIEWER_REQUIRED, "reviewer_must_be_explicit")
    name = reviewer.strip()
    if _CONTROL.search(name) or len(name) > MAX_REVIEWER_CHARS:
        raise ReviewError(ReviewErrorCode.INVALID_DECISION, "reviewer_invalid_format")
    lowered = name.lower()
    if lowered in FORBIDDEN_REVIEWERS or lowered in {n.lower() for n in provenance_names if n}:
        raise ReviewError(ReviewErrorCode.INVALID_DECISION, "reviewer_cannot_be_automatic_or_provider")
    return redact_secrets(name)
