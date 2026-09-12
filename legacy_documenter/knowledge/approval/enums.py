"""Closed vocabularies for the V4-R9 Technical Lead approval layer.

Neither enum is derived from R8 `ProposalKind`/`ProposalMethod`, R7
`RelationKind`, R5 `ClassificationRecord`, R6 `TemporalState`, or R1
`SourceType`/`KnowledgeNature`: a decision's outcome and authority are always
supplied explicitly by the caller, never inferred from proposal content or
origin.
"""
from enum import Enum


class ApprovalDecisionType(str, Enum):
    """The closed V4-R9 Technical Lead decision taxonomy. No other outcome is supported.

    Deliberately excludes `AI_APPROVED`, `SYSTEM_APPROVED`, `AUTO_APPROVED`,
    and `RULE_APPROVED`: V4 recognizes no automatic decision origin.
    `APPROVED` never itself creates canonical knowledge (`APPROVED !=
    CANONICALIZED`). `REJECTED` never itself marks the underlying statement,
    source, or relation as objectively false (`REJECTED != FALSE`).
    `CORRECTION_REQUESTED` never itself rejects, mutates the reviewed
    proposal, or changes canonical knowledge (`CORRECTION_REQUESTED !=
    REJECTED`).
    """

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CORRECTION_REQUESTED = "CORRECTION_REQUESTED"


class ApprovalAuthority(str, Enum):
    """The closed V4 approval-authority vocabulary: `TECHNICAL_LEAD` only.

    Intentionally excludes `ADMIN`, `MANAGER`, `REVIEWER`, `AI`, and
    `SYSTEM`: V4 has no RBAC and no automatic approval authority. Recording
    `authority=TECHNICAL_LEAD` means the caller explicitly supplied this
    decision as a Technical Lead decision; it never means this module itself
    acted as the Technical Lead.
    """

    TECHNICAL_LEAD = "TECHNICAL_LEAD"


TERMINAL_DECISIONS: frozenset[ApprovalDecisionType] = frozenset({
    ApprovalDecisionType.APPROVED,
    ApprovalDecisionType.REJECTED,
})
