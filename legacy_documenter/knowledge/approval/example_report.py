"""Deterministic synthetic example fixture for the V4-R9 Technical Lead approval layer.

Every id and proposal below is synthetic, hand-authored, and built directly
via the R8 `ProposalService`/`ProposalCollection` (not derived from any real
repository content), used only to demonstrate the six R9 example scenarios
required by the active prompt.
"""
import json

from legacy_documenter.knowledge.approval.enums import ApprovalAuthority, ApprovalDecisionType
from legacy_documenter.knowledge.approval.service import (
    ApprovalCollection,
    ApprovalRejectedError,
    ApprovalRequest,
    ApprovalService,
    is_eligible_for_canonical_composition,
)
from legacy_documenter.knowledge.proposals.enums import ProposalKind, ProposalMethod, ProposalStatus
from legacy_documenter.knowledge.proposals.service import ProposalCollection, ProposalRequest, ProposalService

SCHEMA_VERSION = "V4-R9"

_PROPOSAL_SERVICE = ProposalService()
_APPROVAL_SERVICE = ApprovalService()


def _ready_proposal(**kwargs):
    """Builds one R8 proposal and transitions it to READY_FOR_REVIEW via a dedicated collection."""
    collection = ProposalCollection()
    draft = _PROPOSAL_SERVICE.create_proposal(ProposalRequest(**kwargs))
    collection.add(draft)
    return collection.transition(draft.proposal_id, ProposalStatus.READY_FOR_REVIEW)


def build_approval_example() -> dict:
    """Builds the full deterministic R9 example-fixture payload as a plain dict."""
    material_income = "MAT-EXAMPLE-INCOME-REQUIREMENT"
    material_a = "MAT-EXAMPLE-A"
    material_b = "MAT-EXAMPLE-B"

    # Example 1 - approved proposal.
    proposal_1 = _ready_proposal(
        proposal_kind=ProposalKind.KNOWLEDGE_ADDITION,
        statement="Add the minimum income requirement to the knowledge source.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_income,),
    )
    approvals_1 = ApprovalCollection()
    decision_1 = _APPROVAL_SERVICE.record_decision(
        ApprovalRequest(
            proposal_id=proposal_1.proposal_id,
            decision=ApprovalDecisionType.APPROVED,
            authority=ApprovalAuthority.TECHNICAL_LEAD,
            decided_by="technical_lead_example",
            rationale="Requirement is well-evidenced and unambiguous.",
        ),
        proposal_1,
    )
    approvals_1.record_decision(decision_1)

    # Example 2 - rejected proposal.
    proposal_2 = _ready_proposal(
        proposal_kind=ProposalKind.RESOLUTION,
        statement="Apply requirement A to internal users and B to external users.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_a, material_b),
    )
    approvals_2 = ApprovalCollection()
    decision_2 = _APPROVAL_SERVICE.record_decision(
        ApprovalRequest(
            proposal_id=proposal_2.proposal_id,
            decision=ApprovalDecisionType.REJECTED,
            authority=ApprovalAuthority.TECHNICAL_LEAD,
            decided_by="technical_lead_example",
            rationale="Scope is broader than the current review cycle should decide.",
        ),
        proposal_2,
    )
    approvals_2.record_decision(decision_2)

    # Example 3 - correction requested, then conceptual supersession illustration.
    proposal_3a = _ready_proposal(
        proposal_kind=ProposalKind.INTERPRETATION,
        statement="Interpret the ambiguous clause as referring to the internal-user population.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_a,),
    )
    approvals_3 = ApprovalCollection()
    decision_3a = _APPROVAL_SERVICE.record_decision(
        ApprovalRequest(
            proposal_id=proposal_3a.proposal_id,
            decision=ApprovalDecisionType.CORRECTION_REQUESTED,
            authority=ApprovalAuthority.TECHNICAL_LEAD,
            decided_by="technical_lead_example",
            correction_instructions="Clarify which population the clause addresses with a source citation.",
        ),
        proposal_3a,
    )
    approvals_3.record_decision(decision_3a)
    # Conceptual illustration only: proposal_3b/decision_3b are constructed to show the
    # expected NEXT-ROUND shape (a new proposal id, linked via previous_decision_id) without
    # this module creating that new proposal on the caller's behalf - R8 supersession is out
    # of R9's scope, so proposal_3b is never added to an R8 ProposalCollection here.
    proposal_3b = _PROPOSAL_SERVICE.create_proposal(ProposalRequest(
        proposal_kind=ProposalKind.INTERPRETATION,
        statement="Interpret the clause as referring to the internal-user population, per policy doc section 4.2.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_a,),
        supersedes_proposal_id=proposal_3a.proposal_id,
    ))

    # Example 4 - AI-originated proposal approved by a human Technical Lead.
    proposal_4 = _ready_proposal(
        proposal_kind=ProposalKind.INTERPRETATION,
        statement="Interpret the ambiguous clause per the deterministic-rule fallback default.",
        proposal_method=ProposalMethod.AI_PROPOSED,
        material_ids=(material_a,),
    )
    approvals_4 = ApprovalCollection()
    decision_4 = _APPROVAL_SERVICE.record_decision(
        ApprovalRequest(
            proposal_id=proposal_4.proposal_id,
            decision=ApprovalDecisionType.APPROVED,
            authority=ApprovalAuthority.TECHNICAL_LEAD,
            decided_by="technical_lead_example",
            rationale="Reviewed the AI-drafted interpretation and confirmed it independently.",
        ),
        proposal_4,
    )
    approvals_4.record_decision(decision_4)

    # Example 5 - invalid proposal status (DRAFT) rejected deterministically.
    proposal_5 = _PROPOSAL_SERVICE.create_proposal(ProposalRequest(
        proposal_kind=ProposalKind.INTERPRETATION,
        statement="Interpret clause X.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_a,),
    ))
    approvals_5 = ApprovalCollection()
    example_5_result = "UNEXPECTED_ACCEPTANCE"
    try:
        _APPROVAL_SERVICE.record_decision(
            ApprovalRequest(
                proposal_id=proposal_5.proposal_id,
                decision=ApprovalDecisionType.APPROVED,
                authority=ApprovalAuthority.TECHNICAL_LEAD,
                decided_by="technical_lead_example",
            ),
            proposal_5,
        )
    except ApprovalRejectedError:
        example_5_result = "REJECTED_BY_VALIDATION"

    # Example 6 - duplicate/second terminal decision rejected.
    proposal_6 = _ready_proposal(
        proposal_kind=ProposalKind.SELECTION,
        statement="Select architecture option A.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_a, material_b),
    )
    approvals_6 = ApprovalCollection()
    decision_6a = _APPROVAL_SERVICE.record_decision(
        ApprovalRequest(
            proposal_id=proposal_6.proposal_id,
            decision=ApprovalDecisionType.APPROVED,
            authority=ApprovalAuthority.TECHNICAL_LEAD,
            decided_by="technical_lead_example",
        ),
        proposal_6,
    )
    approvals_6.record_decision(decision_6a)
    example_6_result = "UNEXPECTED_ACCEPTANCE"
    try:
        second_decision = _APPROVAL_SERVICE.record_decision(
            ApprovalRequest(
                proposal_id=proposal_6.proposal_id,
                decision=ApprovalDecisionType.REJECTED,
                authority=ApprovalAuthority.TECHNICAL_LEAD,
                decided_by="technical_lead_example",
            ),
            proposal_6,
        )
        approvals_6.record_decision(second_decision)
    except ApprovalRejectedError:
        example_6_result = "REJECTED_BY_VALIDATION"

    return {
        "kind": "TECHNICAL_LEAD_APPROVAL_EXAMPLE_FIXTURE",
        "schema_version": SCHEMA_VERSION,
        "example_1_approved_proposal": {
            "proposal_id": proposal_1.proposal_id,
            "proposal_status": proposal_1.status.value,
            "decision_id": decision_1.decision_id,
            "decision": decision_1.decision.value,
            "authority": decision_1.authority.value,
            "decided_by": decision_1.decided_by,
            "proposal_mutated": False,
            "canonical_knowledge_created": False,
            "eligible_for_R10": is_eligible_for_canonical_composition(approvals_1, proposal_1.proposal_id),
        },
        "example_2_rejected_proposal": {
            "proposal_id": proposal_2.proposal_id,
            "proposal_status": proposal_2.status.value,
            "decision_id": decision_2.decision_id,
            "decision": decision_2.decision.value,
            "proposal_false": "NOT_DETERMINED",
            "source_false": "NOT_DETERMINED",
            "canonical_knowledge_created": False,
            "eligible_for_R10": is_eligible_for_canonical_composition(approvals_2, proposal_2.proposal_id),
        },
        "example_3_correction_requested": {
            "proposal_a_id": proposal_3a.proposal_id,
            "proposal_a_status": proposal_3a.status.value,
            "decision_id": decision_3a.decision_id,
            "decision": decision_3a.decision.value,
            "correction_instructions": decision_3a.correction_instructions,
            "original_proposal_preserved": True,
            "proposal_content_mutated": False,
            "eligible_for_R10": is_eligible_for_canonical_composition(approvals_3, proposal_3a.proposal_id),
            "conceptual_next_round": {
                "note": "Illustrates the expected shape only; this module never creates proposal_b or its "
                        "supersession on the caller's behalf - that remains an explicit R8 caller action.",
                "proposal_b_id": proposal_3b.proposal_id,
                "proposal_b_supersedes_proposal_a_id": proposal_3b.supersedes_proposal_id,
                "proposal_b_added_to_r8_collection": False,
                "decision_b_recorded": False,
            },
        },
        "example_4_ai_originated_proposal_approved_by_human": {
            "proposal_id": proposal_4.proposal_id,
            "proposal_method": proposal_4.proposal_method.value,
            "decision_id": decision_4.decision_id,
            "decision": decision_4.decision.value,
            "AI_APPROVAL": False,
            "AI_ORIGIN_PRESERVED": proposal_4.proposal_method == ProposalMethod.AI_PROPOSED,
            "HUMAN_DECISION_RECORDED": decision_4.authority == ApprovalAuthority.TECHNICAL_LEAD,
        },
        "example_5_invalid_proposal_status": {
            "proposal_id": proposal_5.proposal_id,
            "proposal_status": proposal_5.status.value,
            "attempted_decision": ApprovalDecisionType.APPROVED.value,
            "result": example_5_result,
            "approval_record_created": False,
        },
        "example_6_duplicate_second_terminal_decision": {
            "proposal_id": proposal_6.proposal_id,
            "first_decision_id": decision_6a.decision_id,
            "first_decision": decision_6a.decision.value,
            "attempted_second_decision": ApprovalDecisionType.REJECTED.value,
            "result": example_6_result,
            "original_decision_preserved": approvals_6.get(decision_6a.decision_id) is not None
            and approvals_6.get(decision_6a.decision_id).decision == ApprovalDecisionType.APPROVED,
            "decision_count_for_proposal": len(approvals_6.for_proposal(proposal_6.proposal_id)),
        },
    }


def render_approval_example_json() -> str:
    """Renders the example fixture as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return json.dumps(build_approval_example(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
