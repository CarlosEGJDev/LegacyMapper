"""Adapts validated AI interpretation findings into knowledge Proposals (V4.2-R4).

Uses the EXISTING `knowledge/proposals` domain model and service unchanged --
no second proposal model is invented, and nothing here approves, promotes to
canonical knowledge, or grants Technical Lead authority. AI interpretation is
a proposal, never a fact (V4.2-R4 section 9).
"""
from __future__ import annotations

from legacy_documenter.knowledge.proposals.enums import ProposalKind, ProposalMethod, ProposalStatus
from legacy_documenter.knowledge.proposals.models import Proposal, transition_proposal
from legacy_documenter.knowledge.proposals.service import ProposalRequest, ProposalService


def adapt_findings_to_proposals(findings: list[dict]) -> list[Proposal]:
    """Converts each already-validated interpretation finding into one Proposal.

    Every proposal is created with `proposal_kind=ProposalKind.INTERPRETATION`
    and `proposal_method=ProposalMethod.AI_PROPOSED` (preserving AI origin and
    method, per V4.2-R4 section 9), carries the finding's `evidence_refs` as
    its basis, and is transitioned from `DRAFT` to `READY_FOR_REVIEW` --  a
    purely structural "complete enough to show the Technical Lead" transition
    already defined by the existing `transition_proposal` lifecycle function,
    never an approval. `findings` must already be validated (see
    `orchestration.ai_interpretation._validate_findings`); this function
    performs no further semantic judgment of its own.
    """
    service = ProposalService()
    proposals: list[Proposal] = []
    for finding in findings:
        request = ProposalRequest(
            proposal_kind=ProposalKind.INTERPRETATION,
            statement=finding["statement"],
            proposal_method=ProposalMethod.AI_PROPOSED,
            evidence_refs=tuple(finding["evidence_refs"]),
            rationale=f"AI-proposed interpretation (confidence: {finding.get('confidence', 'UNCERTAIN')}).",
        )
        proposal = service.create_proposal(request)
        proposal = transition_proposal(proposal, ProposalStatus.READY_FOR_REVIEW)
        proposals.append(proposal)
    return proposals
