"""Deterministic synthetic example fixture for the V4-R10 canonical knowledge composition layer.

Every id, proposal, and decision below is synthetic, hand-authored, and built
directly via the R8/R9 services (not derived from any real repository
content), used only to demonstrate the eight R10 example scenarios required
by the active prompt.
"""
import json

from legacy_documenter.knowledge.approval.enums import ApprovalAuthority, ApprovalDecisionType
from legacy_documenter.knowledge.approval.service import ApprovalCollection, ApprovalRequest, ApprovalService
from legacy_documenter.knowledge.canonical.service import (
    CanonicalCompositionRejectedError,
    CanonicalCompositionRequest,
    CanonicalCompositionService,
    CanonicalKnowledgeCollection,
)
from legacy_documenter.knowledge.domain.enums import KnowledgeNature, KnowledgeStatus, SourceType, TemporalState
from legacy_documenter.knowledge.domain.models import EvidenceRef
from legacy_documenter.knowledge.proposals.enums import ProposalKind, ProposalMethod, ProposalStatus
from legacy_documenter.knowledge.proposals.service import ProposalCollection, ProposalRequest, ProposalService

SCHEMA_VERSION = "V4-R10"

_PROPOSAL_SERVICE = ProposalService()
_APPROVAL_SERVICE = ApprovalService()
_CANONICAL_SERVICE = CanonicalCompositionService()


def _ready_proposal(**kwargs):
    """Builds one R8 proposal and transitions it to READY_FOR_REVIEW via a dedicated collection."""
    collection = ProposalCollection()
    draft = _PROPOSAL_SERVICE.create_proposal(ProposalRequest(**kwargs))
    collection.add(draft)
    return collection.transition(draft.proposal_id, ProposalStatus.READY_FOR_REVIEW)


def _approve(proposal, **decision_kwargs):
    """Records an APPROVED/TECHNICAL_LEAD decision against `proposal` in a dedicated collection."""
    approvals = ApprovalCollection()
    decision = _APPROVAL_SERVICE.record_decision(
        ApprovalRequest(
            proposal_id=proposal.proposal_id,
            decision=ApprovalDecisionType.APPROVED,
            authority=ApprovalAuthority.TECHNICAL_LEAD,
            decided_by=decision_kwargs.pop("decided_by", "technical_lead_example"),
            **decision_kwargs,
        ),
        proposal,
    )
    approvals.record_decision(decision)
    return approvals, decision


def build_canonical_example() -> dict:
    """Builds the full deterministic R10 example-fixture payload as a plain dict."""
    material_income = "MAT-EXAMPLE-INCOME-REQUIREMENT"
    material_a = "MAT-EXAMPLE-A"
    material_b = "MAT-EXAMPLE-B"
    material_auth = "MAT-EXAMPLE-AUTH-STANDARD"

    # Example 1 - approved human proposal composes successfully.
    proposal_1 = _ready_proposal(
        proposal_kind=ProposalKind.KNOWLEDGE_ADDITION,
        statement="The minimum income requirement is 3x the monthly rent.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_income,),
    )
    approvals_1, decision_1 = _approve(proposal_1, rationale="Requirement is well-evidenced and unambiguous.")
    collection_1 = CanonicalKnowledgeCollection()
    entry_1 = collection_1.compose(_CANONICAL_SERVICE, CanonicalCompositionRequest(
        proposal=proposal_1,
        approval_decision=decision_1,
        source_type=SourceType.HUMAN_REQUIREMENT,
        nature=KnowledgeNature.REQUIREMENT,
        knowledge_status=KnowledgeStatus.INTERPRETED,
    ))

    # Example 2 - approved AI-origin proposal: origin and approval remain separately visible.
    proposal_2 = _ready_proposal(
        proposal_kind=ProposalKind.INTERPRETATION,
        statement="Interpret the ambiguous clause as referring to the internal-user population.",
        proposal_method=ProposalMethod.AI_PROPOSED,
        material_ids=(material_a,),
    )
    approvals_2, decision_2 = _approve(
        proposal_2, rationale="Reviewed the AI-drafted interpretation and confirmed it independently.",
    )
    collection_2 = CanonicalKnowledgeCollection()
    entry_2 = collection_2.compose(_CANONICAL_SERVICE, CanonicalCompositionRequest(
        proposal=proposal_2,
        approval_decision=decision_2,
        source_type=SourceType.AI_INTERPRETATION,
        nature=KnowledgeNature.BUSINESS_RULE,
        knowledge_status=KnowledgeStatus.INTERPRETED,
    ))

    # Example 3 - rejected proposal: composition must be rejected, no entry created.
    proposal_3 = _ready_proposal(
        proposal_kind=ProposalKind.RESOLUTION,
        statement="Apply requirement A to internal users and B to external users.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_a, material_b),
    )
    approvals_3 = ApprovalCollection()
    decision_3 = _APPROVAL_SERVICE.record_decision(
        ApprovalRequest(
            proposal_id=proposal_3.proposal_id,
            decision=ApprovalDecisionType.REJECTED,
            authority=ApprovalAuthority.TECHNICAL_LEAD,
            decided_by="technical_lead_example",
            rationale="Scope is broader than the current review cycle should decide.",
        ),
        proposal_3,
    )
    approvals_3.record_decision(decision_3)
    collection_3 = CanonicalKnowledgeCollection()
    example_3_result = "UNEXPECTED_ACCEPTANCE"
    try:
        collection_3.compose(_CANONICAL_SERVICE, CanonicalCompositionRequest(
            proposal=proposal_3,
            approval_decision=decision_3,
            source_type=SourceType.HUMAN_REQUIREMENT,
            nature=KnowledgeNature.RESOLUTION,
            knowledge_status=KnowledgeStatus.INTERPRETED,
        ))
    except CanonicalCompositionRejectedError:
        example_3_result = "REJECTED_BY_VALIDATION"

    # Example 4 - correction requested: composition must be rejected, no entry created.
    proposal_4 = _ready_proposal(
        proposal_kind=ProposalKind.ADDITIONAL_INFORMATION,
        statement="Request confirmation of the applicable authentication standard.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_auth,),
    )
    approvals_4 = ApprovalCollection()
    decision_4 = _APPROVAL_SERVICE.record_decision(
        ApprovalRequest(
            proposal_id=proposal_4.proposal_id,
            decision=ApprovalDecisionType.CORRECTION_REQUESTED,
            authority=ApprovalAuthority.TECHNICAL_LEAD,
            decided_by="technical_lead_example",
            correction_instructions="Clarify which standard version applies with a source citation.",
        ),
        proposal_4,
    )
    approvals_4.record_decision(decision_4)
    collection_4 = CanonicalKnowledgeCollection()
    example_4_result = "UNEXPECTED_ACCEPTANCE"
    try:
        collection_4.compose(_CANONICAL_SERVICE, CanonicalCompositionRequest(
            proposal=proposal_4,
            approval_decision=decision_4,
            source_type=SourceType.HUMAN_REQUIREMENT,
            nature=KnowledgeNature.CONSTRAINT,
            knowledge_status=KnowledgeStatus.UNRESOLVED,
        ))
    except CanonicalCompositionRejectedError:
        example_4_result = "REJECTED_BY_VALIDATION"

    # Example 5 - no approval at all: composition must be rejected, no entry created.
    proposal_5 = _ready_proposal(
        proposal_kind=ProposalKind.INTERPRETATION,
        statement="Interpret clause X per the fallback default.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_a,),
    )
    collection_5 = CanonicalKnowledgeCollection()
    example_5_result = "UNEXPECTED_ACCEPTANCE"
    try:
        collection_5.compose(_CANONICAL_SERVICE, CanonicalCompositionRequest(
            proposal=proposal_5,
            approval_decision=None,
            source_type=SourceType.HUMAN_REQUIREMENT,
            nature=KnowledgeNature.BUSINESS_RULE,
            knowledge_status=KnowledgeStatus.INTERPRETED,
        ))
    except CanonicalCompositionRejectedError:
        example_5_result = "REJECTED_BY_VALIDATION"

    # Example 6 - duplicate approved proposal composed twice: idempotent no-op.
    proposal_6 = _ready_proposal(
        proposal_kind=ProposalKind.KNOWLEDGE_ADDITION,
        statement="Session timeout is 30 minutes of inactivity.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_a,),
    )
    approvals_6, decision_6 = _approve(proposal_6)
    collection_6 = CanonicalKnowledgeCollection()
    request_6 = CanonicalCompositionRequest(
        proposal=proposal_6,
        approval_decision=decision_6,
        source_type=SourceType.TECHNICAL_CONSTRAINT,
        nature=KnowledgeNature.CONSTRAINT,
        knowledge_status=KnowledgeStatus.INTERPRETED,
    )
    entry_6_first = collection_6.compose(_CANONICAL_SERVICE, request_6)
    entry_6_second = collection_6.compose(_CANONICAL_SERVICE, request_6)

    # Example 7 - CONFIRMED requested without required authoritative evidence: rejected.
    proposal_7 = _ready_proposal(
        proposal_kind=ProposalKind.KNOWLEDGE_ADDITION,
        statement="Passwords must be rotated every 90 days.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_a,),
    )
    approvals_7, decision_7 = _approve(proposal_7)
    collection_7 = CanonicalKnowledgeCollection()
    example_7_result = "UNEXPECTED_ACCEPTANCE"
    try:
        collection_7.compose(_CANONICAL_SERVICE, CanonicalCompositionRequest(
            proposal=proposal_7,
            approval_decision=decision_7,
            source_type=SourceType.CORPORATE_STANDARD,
            nature=KnowledgeNature.NORM,
            knowledge_status=KnowledgeStatus.CONFIRMED,
            evidence_refs=(),
        ))
    except CanonicalCompositionRejectedError:
        example_7_result = "REJECTED_BY_VALIDATION"
    # Same proposal, with explicit authoritative evidence supplied: succeeds, proving
    # approval alone never bypasses the R1 CONFIRMED-evidence invariant.
    authoritative_evidence = EvidenceRef(
        evidence_id="EVR-EXAMPLE-CORPORATE-STANDARD-90-DAYS",
        source_type=SourceType.CORPORATE_STANDARD,
        authoritative=True,
    )
    entry_7_with_evidence = collection_7.compose(_CANONICAL_SERVICE, CanonicalCompositionRequest(
        proposal=proposal_7,
        approval_decision=decision_7,
        source_type=SourceType.CORPORATE_STANDARD,
        nature=KnowledgeNature.NORM,
        knowledge_status=KnowledgeStatus.CONFIRMED,
        evidence_refs=(authoritative_evidence,),
    ))

    # Example 8 - AS_IS / TO_BE coexistence: two explicitly approved entries, no auto-conflict.
    proposal_8_as_is = _ready_proposal(
        proposal_kind=ProposalKind.KNOWLEDGE_ADDITION,
        statement="Currently, approval requires two manual signatures.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_a,),
    )
    approvals_8_as_is, decision_8_as_is = _approve(proposal_8_as_is)
    proposal_8_to_be = _ready_proposal(
        proposal_kind=ProposalKind.KNOWLEDGE_ADDITION,
        statement="The target process requires a single digital signature.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_b,),
    )
    approvals_8_to_be, decision_8_to_be = _approve(proposal_8_to_be)
    collection_8 = CanonicalKnowledgeCollection()
    entry_8_as_is = collection_8.compose(_CANONICAL_SERVICE, CanonicalCompositionRequest(
        proposal=proposal_8_as_is,
        approval_decision=decision_8_as_is,
        source_type=SourceType.BUSINESS_CONTEXT,
        nature=KnowledgeNature.PROCESS,
        knowledge_status=KnowledgeStatus.INTERPRETED,
        temporal_state=TemporalState.AS_IS,
    ))
    entry_8_to_be = collection_8.compose(_CANONICAL_SERVICE, CanonicalCompositionRequest(
        proposal=proposal_8_to_be,
        approval_decision=decision_8_to_be,
        source_type=SourceType.BUSINESS_CONTEXT,
        nature=KnowledgeNature.PROCESS,
        knowledge_status=KnowledgeStatus.INTERPRETED,
        temporal_state=TemporalState.TO_BE,
    ))

    return {
        "kind": "CANONICAL_KNOWLEDGE_COMPOSITION_EXAMPLE_FIXTURE",
        "schema_version": SCHEMA_VERSION,
        "example_1_approved_human_proposal": {
            "proposal_id": proposal_1.proposal_id,
            "proposal_status": proposal_1.status.value,
            "approval_decision_id": decision_1.decision_id,
            "canonical_knowledge_id": entry_1.knowledge_id,
            "canonical_entry_created": True,
            "proposal_id_retained": entry_1.proposal_id == proposal_1.proposal_id,
            "approval_decision_id_retained": entry_1.approval_decision_id == decision_1.decision_id,
        },
        "example_2_approved_ai_origin_proposal": {
            "proposal_id": proposal_2.proposal_id,
            "proposal_method": proposal_2.proposal_method.value,
            "approval_decision_id": decision_2.decision_id,
            "approval_authority": decision_2.authority.value,
            "canonical_knowledge_id": entry_2.knowledge_id,
            "canonical_entry_created": True,
            "AI_ORIGIN_PRESERVED": proposal_2.proposal_method == ProposalMethod.AI_PROPOSED,
            "HUMAN_APPROVAL_PRESERVED": decision_2.authority == ApprovalAuthority.TECHNICAL_LEAD,
            "AI_APPROVAL": False,
        },
        "example_3_rejected_proposal": {
            "proposal_id": proposal_3.proposal_id,
            "approval_decision": decision_3.decision.value,
            "result": example_3_result,
            "canonical_entry_created": False,
        },
        "example_4_correction_requested": {
            "proposal_id": proposal_4.proposal_id,
            "approval_decision": decision_4.decision.value,
            "result": example_4_result,
            "canonical_entry_created": False,
        },
        "example_5_no_approval": {
            "proposal_id": proposal_5.proposal_id,
            "approval_decision": "NONE",
            "result": example_5_result,
            "canonical_entry_created": False,
        },
        "example_6_duplicate_approved_proposal": {
            "proposal_id": proposal_6.proposal_id,
            "approval_decision_id": decision_6.decision_id,
            "first_composition_knowledge_id": entry_6_first.knowledge_id,
            "second_composition_knowledge_id": entry_6_second.knowledge_id,
            "same_knowledge_id": entry_6_first.knowledge_id == entry_6_second.knowledge_id,
            "canonical_count": len(collection_6.list()),
            "result": "IDEMPOTENT_NO_OP",
        },
        "example_7_confirmed_without_authoritative_evidence": {
            "proposal_id": proposal_7.proposal_id,
            "requested_status": KnowledgeStatus.CONFIRMED.value,
            "without_evidence_result": example_7_result,
            "with_authoritative_evidence_knowledge_id": entry_7_with_evidence.knowledge_id,
            "with_authoritative_evidence_status": entry_7_with_evidence.status.value,
            "approval_bypasses_evidence_rule": False,
        },
        "example_8_as_is_to_be_coexistence": {
            "as_is_knowledge_id": entry_8_as_is.knowledge_id,
            "as_is_temporal_state": entry_8_as_is.temporal_state.value,
            "to_be_knowledge_id": entry_8_to_be.knowledge_id,
            "to_be_temporal_state": entry_8_to_be.temporal_state.value,
            "both_present": collection_8.contains(entry_8_as_is.knowledge_id)
            and collection_8.contains(entry_8_to_be.knowledge_id),
            "automatic_conflict_created": False,
            "automatic_supersession_applied": False,
        },
    }


def render_canonical_example_json() -> str:
    """Renders the example fixture as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return json.dumps(build_canonical_example(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
