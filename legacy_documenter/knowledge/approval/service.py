"""Deterministic explicit-decision-recording service and in-memory collection (V4-R9).

Pipeline: `ApprovalRequest` (explicit caller input) + the current R8
`Proposal` (read-only) -> `ApprovalDecision`. No proposal content, kind,
method, relation kind, confidence, evidence count, or origin is ever read to
decide `decision`/`authority`/`decided_by` — those must already be present,
explicitly, in the request. This module performs no file, network, database,
provider, or directory-scan I/O, and never calls an LLM/provider.

This module never mutates the `Proposal` it reads (`ProposalStatus` stays
R8-only), never mutates any referenced relation/material/classification/
temporal/provenance record or R1 knowledge status, and never creates a
`KnowledgeStatement` or any canonical Knowledge Source content. `APPROVED`
only makes a proposal eligible for R10 composition; that composition itself
is out of scope for R9.
"""
from dataclasses import dataclass, field

from legacy_documenter.knowledge.approval.enums import (
    TERMINAL_DECISIONS,
    ApprovalAuthority,
    ApprovalDecisionType,
)
from legacy_documenter.knowledge.approval.models import (
    ApprovalDecision,
    ApprovalValidationError,
    new_decision_id,
)
from legacy_documenter.knowledge.proposals.enums import ProposalStatus
from legacy_documenter.knowledge.proposals.models import Proposal
from legacy_documenter.utils.sanitizer import sanitize_data, sanitize_text

#: The only R8 proposal status a decision may be recorded against. Necessary
#: but not sufficient: an explicit Technical Lead decision is still required.
ELIGIBLE_PROPOSAL_STATUS = ProposalStatus.READY_FOR_REVIEW


class ApprovalRejectedError(ValueError):
    """Raised when a requested approval decision cannot be accepted.

    In practice this happens for a structurally invalid request (missing
    `decided_by`, unknown `decision`/`authority`, an authority other than
    `TECHNICAL_LEAD`), a `proposal_id` mismatch against the supplied
    `Proposal`, a `Proposal` whose current status is not
    `READY_FOR_REVIEW`, a conflicting duplicate decision identity, or a
    second decision attempt against a `proposal_id` that already has a
    recorded decision. It never happens because of the decision's textual
    rationale/correction_instructions content.
    """


@dataclass
class ApprovalRequest:
    """Represents one explicit caller request to record a Technical Lead decision.

    `decision`, `authority`, and `decided_by` must always be supplied
    explicitly by the caller; none of them is ever inferred from
    `proposal_method`, `proposal_kind`, proposal content, source type,
    relation kind, confidence, evidence count, origin, dates, or previous
    decisions.
    """

    proposal_id: str
    decision: ApprovalDecisionType
    authority: ApprovalAuthority
    decided_by: str
    rationale: str | None = None
    correction_instructions: str | None = None
    previous_decision_id: str | None = None
    metadata: dict = field(default_factory=dict)


class ApprovalService:
    """Deterministic boundary that constructs an `ApprovalDecision` only from an explicit request.

    Stateless: every call is independent and produces the same output for the
    same request and proposal-status fields. Never inspects
    `ProposalMethod`, `ProposalKind`, `RelationKind`, `KnowledgeNature`,
    `TemporalState`, or `KnowledgeStatus` to decide an outcome, and never
    mutates the `Proposal` it reads. `record_decision` only *constructs* a
    validated `ApprovalDecision`; storing it (and enforcing the duplicate/
    re-decision policy) is `ApprovalCollection.record_decision`'s
    responsibility.
    """

    def record_decision(self, request: ApprovalRequest, proposal: Proposal) -> ApprovalDecision:
        """Constructs one `ApprovalDecision` from an explicit `ApprovalRequest` and the current `Proposal`.

        Raises `ApprovalRejectedError` for an unknown `decision`/`authority`,
        an `authority` other than `TECHNICAL_LEAD`, a missing/blank
        `decided_by`, a missing/blank `proposal_id`, a `proposal_id` that
        does not match `proposal.proposal_id`, or a `proposal.status` other
        than `READY_FOR_REVIEW`. Never mutates `proposal`.
        """
        if not request.proposal_id or not request.proposal_id.strip():
            raise ApprovalRejectedError("proposal_id_required")
        if not isinstance(request.decision, ApprovalDecisionType):
            raise ApprovalRejectedError("invalid_decision_type")
        if not isinstance(request.authority, ApprovalAuthority):
            raise ApprovalRejectedError("invalid_authority")
        if request.authority != ApprovalAuthority.TECHNICAL_LEAD:
            raise ApprovalRejectedError("authority_must_be_technical_lead")
        if not request.decided_by or not request.decided_by.strip():
            raise ApprovalRejectedError("decided_by_required")

        if proposal is None or not isinstance(proposal, Proposal):
            raise ApprovalRejectedError("proposal_required")
        if proposal.proposal_id != request.proposal_id:
            raise ApprovalRejectedError("proposal_id_mismatch")
        if proposal.status != ELIGIBLE_PROPOSAL_STATUS:
            raise ApprovalRejectedError(f"invalid_proposal_status_for_decision:{proposal.status.value}")

        decided_by = sanitize_text(request.decided_by)
        rationale = sanitize_text(request.rationale) if request.rationale else None
        correction_instructions = (
            sanitize_text(request.correction_instructions) if request.correction_instructions else None
        )
        metadata = sanitize_data(dict(request.metadata))

        decision = ApprovalDecision(
            decision_id=new_decision_id(
                request.proposal_id, request.decision, request.authority, decided_by,
                rationale, correction_instructions, request.previous_decision_id,
            ),
            proposal_id=request.proposal_id,
            decision=request.decision,
            authority=request.authority,
            decided_by=decided_by,
            rationale=rationale,
            correction_instructions=correction_instructions,
            previous_decision_id=request.previous_decision_id,
            metadata=metadata,
        )
        try:
            decision.validate()
        except ApprovalValidationError as exc:
            raise ApprovalRejectedError(str(exc)) from exc
        return decision


class ApprovalCollection:
    """Deterministic in-memory approval-decision repository. No external storage is used.

    Preserves insertion order for `list()`/`for_proposal()`/`by_decision()`.
    Every recorded decision is preserved forever: there is no operation that
    overwrites or deletes a stored `ApprovalDecision`.

    Re-decision policy: at most one `ApprovalDecision` may be recorded per
    `proposal_id` (a proposal identity, per R8, is already an immutable
    version). A second, non-identical decision attempt against a
    `proposal_id` that already has any recorded decision — whether that
    prior decision was `APPROVED`, `REJECTED`, or `CORRECTION_REQUESTED` — is
    rejected rather than silently overwritten. After `CORRECTION_REQUESTED`,
    the expected path is a new, distinct R8 proposal version (created via R8
    supersession, out of R9's scope) that receives its own, separate
    decision under its own `proposal_id`.
    """

    def __init__(self) -> None:
        self._decisions: dict[str, ApprovalDecision] = {}

    def record_decision(self, decision: ApprovalDecision) -> ApprovalDecision:
        """Records `decision`, enforcing the duplicate and re-decision policies.

        Exact duplicate (`decision_id` already stored with identical
        content): idempotent no-op, returns the existing record. Same
        `decision_id` with different content: `ApprovalRejectedError`
        (unreachable in practice, since `decision_id` is a deterministic hash
        of the immutable content, but guarded explicitly for defense in
        depth). Any other decision against a `proposal_id` that already has
        a recorded decision: `ApprovalRejectedError`.
        """
        decision.validate()
        existing = self._decisions.get(decision.decision_id)
        if existing is not None:
            if existing != decision:
                raise ApprovalRejectedError(f"conflicting_duplicate_decision_id:{decision.decision_id}")
            return existing  # exact duplicate: idempotent no-op

        prior = self.for_proposal(decision.proposal_id)
        if prior:
            raise ApprovalRejectedError(f"proposal_already_has_recorded_decision:{decision.proposal_id}")

        self._decisions[decision.decision_id] = decision
        return decision

    def get(self, decision_id: str) -> ApprovalDecision | None:
        """Returns the decision with `decision_id`, or `None` if absent."""
        return self._decisions.get(decision_id)

    def list(self) -> list[ApprovalDecision]:
        """Returns every stored decision in insertion order."""
        return list(self._decisions.values())

    def for_proposal(self, proposal_id: str) -> list[ApprovalDecision]:
        """Returns every stored decision for `proposal_id`, in insertion order."""
        return [decision for decision in self._decisions.values() if decision.proposal_id == proposal_id]

    def latest_for_proposal(self, proposal_id: str) -> ApprovalDecision | None:
        """Returns the most recently recorded decision for `proposal_id`, or `None`.

        Under the current re-decision policy at most one decision ever exists
        per `proposal_id`, so this is equivalent to `for_proposal(...)[0]`
        when non-empty; it is expressed as "latest" for forward-compatibility
        with any future explicitly-approved policy change.
        """
        matches = self.for_proposal(proposal_id)
        return matches[-1] if matches else None

    def by_decision(self, decision_type: ApprovalDecisionType) -> list[ApprovalDecision]:
        """Returns every stored decision of `decision_type`, in insertion order."""
        return [decision for decision in self._decisions.values() if decision.decision == decision_type]


def is_eligible_for_canonical_composition(collection: ApprovalCollection, proposal_id: str) -> bool:
    """Reports whether `proposal_id` is eligible for R10 canonical composition.

    Deterministic query only: `APPROVED` -> `True`; `REJECTED`,
    `CORRECTION_REQUESTED`, or no recorded decision -> `False`. This
    function never creates a `KnowledgeStatement`, a canonical Knowledge
    Source, or any other R10 artifact — it only reports eligibility computed
    from already-recorded decisions.
    """
    decision = collection.latest_for_proposal(proposal_id)
    if decision is None:
        return False
    return decision.decision == ApprovalDecisionType.APPROVED
