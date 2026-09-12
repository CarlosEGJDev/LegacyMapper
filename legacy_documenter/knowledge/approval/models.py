"""Source-neutral `ApprovalDecision` domain model for the V4-R9 Technical Lead approval layer.

An `ApprovalDecision` records that a Technical Lead explicitly decided
`decision` for the R8 `Proposal` identified by `proposal_id`. It carries no
payload duplication of the reviewed proposal's content and never mutates it.
This module never infers `decision`/`authority`/`decided_by` from proposal
content, origin, or any other record, and never performs a Technical Lead
approval on the caller's behalf — it only represents one already supplied by
the caller.

`ApprovalDecision` is frozen: once recorded, its fields never change. A
re-decision against the same `proposal_id` is a new, separate
`ApprovalDecision` record (or, per the V4-R9 re-decision policy, rejected)
rather than a mutation of an existing one — see
`legacy_documenter/knowledge/approval/service.py`.
"""
from dataclasses import dataclass, field

from legacy_documenter.documentation.contracts import stable_id
from legacy_documenter.knowledge.approval.enums import ApprovalAuthority, ApprovalDecisionType


class ApprovalValidationError(ValueError):
    """Raised when an `ApprovalDecision` violates its structural contract."""


@dataclass(frozen=True)
class ApprovalDecision:
    """Represents one explicit, source-neutral Technical Lead approval decision.

    `proposal_id` identifies the R8 `Proposal` version being decided on; this
    model never stores or mutates that `Proposal` object. `authority` is
    closed to `ApprovalAuthority.TECHNICAL_LEAD` in V4 — no other value ever
    validates. `decided_by` must be supplied explicitly by the caller; it is
    never inferred from OS/Git/environment identity.
    """

    decision_id: str
    proposal_id: str
    decision: ApprovalDecisionType
    authority: ApprovalAuthority
    decided_by: str
    rationale: str | None = None
    correction_instructions: str | None = None
    previous_decision_id: str | None = None
    metadata: dict = field(default_factory=dict)

    def validate(self) -> bool:
        """Performs the full structural contract check for an `ApprovalDecision`.

        Deliberately structural only: never a semantic/truth judgment about
        whether the decision was the "right" decision, and never itself a
        source of approval authority.
        """
        if not self.decision_id or not self.decision_id.strip():
            raise ApprovalValidationError("decision_id_required")
        if not self.proposal_id or not self.proposal_id.strip():
            raise ApprovalValidationError("proposal_id_required")
        if not isinstance(self.decision, ApprovalDecisionType):
            raise ApprovalValidationError("invalid_decision_type")
        if not isinstance(self.authority, ApprovalAuthority):
            raise ApprovalValidationError("invalid_authority")
        if self.authority != ApprovalAuthority.TECHNICAL_LEAD:
            # Unreachable via the closed ApprovalAuthority enum today, but kept as an
            # explicit structural guard in case the enum is ever widened by mistake.
            raise ApprovalValidationError("authority_must_be_technical_lead")
        if not self.decided_by or not self.decided_by.strip():
            raise ApprovalValidationError("decided_by_required")
        if self.previous_decision_id is not None and not self.previous_decision_id.strip():
            raise ApprovalValidationError("previous_decision_id_blank")
        if self.previous_decision_id == self.decision_id:
            raise ApprovalValidationError("self_referential_previous_decision_rejected")
        return True


def new_decision_id(
    proposal_id: str,
    decision: ApprovalDecisionType,
    authority: ApprovalAuthority,
    decided_by: str,
    rationale: str | None,
    correction_instructions: str | None,
    previous_decision_id: str | None,
) -> str:
    """Derives a stable `APR-` id from immutable semantic fields only.

    Reuses the existing V3/V4 `stable_id` hashing contract. Deliberately
    excludes `metadata` and any timestamp from identity: those are
    attribution/telemetry data, not part of what makes two decisions the same
    semantic outcome. Never depends on current time, randomness, or object
    identity.
    """
    return stable_id(
        "APR",
        proposal_id,
        decision.value,
        authority.value,
        decided_by,
        rationale or "",
        correction_instructions or "",
        previous_decision_id or "",
    )
