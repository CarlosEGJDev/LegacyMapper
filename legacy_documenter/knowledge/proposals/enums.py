"""Closed vocabularies for the V4-R8 proposal lifecycle.

None of these enums are derived from R1 `SourceType`/`KnowledgeNature`, R5
`ClassificationRecord`, R6 `TemporalState`, or R7 `RelationKind`: a proposal's
kind and method are always supplied explicitly by the caller, never inferred.
"""
from enum import Enum


class ProposalKind(str, Enum):
    """The closed V4-R8 proposal taxonomy. No other kind is supported in this round.

    Each kind proposes an action or conclusion; none of them performs it.
    `RESOLUTION` does not resolve a relation, `MIGRATION` does not migrate
    anything, `CORRECTION` does not correct source material, and
    `KNOWLEDGE_ADDITION` does not create canonical knowledge.
    """

    INTERPRETATION = "INTERPRETATION"
    RESOLUTION = "RESOLUTION"
    CORRECTION = "CORRECTION"
    RECONCILIATION = "RECONCILIATION"
    SELECTION = "SELECTION"
    ADDITIONAL_INFORMATION = "ADDITIONAL_INFORMATION"
    MIGRATION = "MIGRATION"
    KNOWLEDGE_ADDITION = "KNOWLEDGE_ADDITION"


class ProposalStatus(str, Enum):
    """The closed V4-R8 pre-approval lifecycle status.

    Deliberately excludes `APPROVED`/`REJECTED`/`CORRECTED`: those are R9
    Technical Lead approval outcomes, never produced by this module.
    `READY_FOR_REVIEW` means only "structurally ready to be presented to the
    Technical Lead" — never approved, accepted, validated as true, or
    canonical.
    """

    DRAFT = "DRAFT"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    WITHDRAWN = "WITHDRAWN"
    SUPERSEDED = "SUPERSEDED"


class ProposalMethod(str, Enum):
    """Records how a proposal originated. Never implies approval or authority.

    `AI_PROPOSED` is representable so future LegacyMapper workflows may use an
    LLM to draft a proposal, but this module never performs that call and
    never upgrades `AI_PROPOSED` into `HUMAN_PROPOSED`/`DETERMINISTIC_RULE`
    merely because a proposal passes structural validation.
    """

    HUMAN_PROPOSED = "HUMAN_PROPOSED"
    DETERMINISTIC_RULE = "DETERMINISTIC_RULE"
    AI_PROPOSED = "AI_PROPOSED"


VALID_TRANSITIONS: dict[ProposalStatus, frozenset[ProposalStatus]] = {
    ProposalStatus.DRAFT: frozenset({
        ProposalStatus.READY_FOR_REVIEW, ProposalStatus.WITHDRAWN, ProposalStatus.SUPERSEDED,
    }),
    ProposalStatus.READY_FOR_REVIEW: frozenset({
        ProposalStatus.SUPERSEDED, ProposalStatus.WITHDRAWN,
    }),
    ProposalStatus.WITHDRAWN: frozenset(),
    ProposalStatus.SUPERSEDED: frozenset(),
}
