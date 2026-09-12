"""Deterministic synthetic example fixture for the V4-R8 proposal lifecycle.

Every id below is a synthetic, hand-authored constant (not derived from any
real repository content), used only to demonstrate the six R8 example
scenarios required by the active prompt.
"""
import json

from legacy_documenter.knowledge.proposals.enums import ProposalKind, ProposalMethod, ProposalStatus
from legacy_documenter.knowledge.proposals.service import ProposalCollection, ProposalRequest, ProposalService

SCHEMA_VERSION = "V4-R8"

_SERVICE = ProposalService()


def build_proposal_example() -> dict:
    """Builds the full deterministic R8 example-fixture payload as a plain dict."""
    material_income = "MAT-EXAMPLE-INCOME-REQUIREMENT"
    material_a = "MAT-EXAMPLE-A"
    material_b = "MAT-EXAMPLE-B"
    relation_conflict = "REL-EXAMPLE-CONFLICT-AB"
    relation_gap = "REL-EXAMPLE-GAP-AB"
    material_auth = "MAT-EXAMPLE-AUTH-STANDARD"

    # Example 1 — human proposal, then explicit DRAFT -> READY_FOR_REVIEW transition.
    human_proposal_draft = _SERVICE.create_proposal(ProposalRequest(
        proposal_kind=ProposalKind.KNOWLEDGE_ADDITION,
        statement="Add the minimum income requirement to the knowledge source.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_income,),
        proposed_by="technical_lead_example",
    ))
    collection_1 = ProposalCollection()
    collection_1.add(human_proposal_draft)
    human_proposal_ready = collection_1.transition(human_proposal_draft.proposal_id, ProposalStatus.READY_FOR_REVIEW)

    # Example 2 — explicit conflict-resolution proposal (relation stays unchanged).
    resolution_proposal = _SERVICE.create_proposal(ProposalRequest(
        proposal_kind=ProposalKind.RESOLUTION,
        statement="Apply requirement A to internal users and B to external users.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_a, material_b),
        relation_ids=(relation_conflict,),
    ))

    # Example 3 — explicit gap-migration proposal.
    migration_proposal = _SERVICE.create_proposal(ProposalRequest(
        proposal_kind=ProposalKind.MIGRATION,
        statement="Migrate capability A toward capability B.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        relation_ids=(relation_gap,),
    ))

    # Example 4 — additional-information request proposal.
    additional_information_proposal = _SERVICE.create_proposal(ProposalRequest(
        proposal_kind=ProposalKind.ADDITIONAL_INFORMATION,
        statement="Request confirmation of the applicable authentication standard.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_auth,),
    ))

    # Example 5 — AI-originated proposal: data only, zero AI calls performed here.
    ai_proposal = _SERVICE.create_proposal(ProposalRequest(
        proposal_kind=ProposalKind.INTERPRETATION,
        statement="Interpret the ambiguous clause as referring to the internal-user population.",
        proposal_method=ProposalMethod.AI_PROPOSED,
        material_ids=(material_a,),
    ))

    # Example 6 — explicit supersession: B supersedes A.
    proposal_a = _SERVICE.create_proposal(ProposalRequest(
        proposal_kind=ProposalKind.SELECTION,
        statement="Select architecture option A.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_a, material_b),
    ))
    proposal_b = _SERVICE.create_proposal(ProposalRequest(
        proposal_kind=ProposalKind.SELECTION,
        statement="Select architecture option B instead of option A.",
        proposal_method=ProposalMethod.HUMAN_PROPOSED,
        material_ids=(material_a, material_b),
        supersedes_proposal_id=proposal_a.proposal_id,
    ))
    collection_6 = ProposalCollection()
    collection_6.add(proposal_a)
    collection_6.add(proposal_b)
    superseded_a = collection_6.supersede(proposal_b.proposal_id)

    return {
        "kind": "PROPOSAL_LIFECYCLE_EXAMPLE_FIXTURE",
        "schema_version": SCHEMA_VERSION,
        "example_1_human_proposal": {
            "proposal_id": human_proposal_draft.proposal_id,
            "kind": human_proposal_draft.proposal_kind.value,
            "method": human_proposal_draft.proposal_method.value,
            "statement": human_proposal_draft.statement,
            "initial_status": human_proposal_draft.status.value,
            "approval": "NOT_PERFORMED",
            "canonical_knowledge": "NOT_CREATED",
            "after_transition": {
                "proposal_id": human_proposal_ready.proposal_id,
                "status": human_proposal_ready.status.value,
                "same_proposal_id": human_proposal_ready.proposal_id == human_proposal_draft.proposal_id,
                "approval": "NOT_PERFORMED",
            },
        },
        "example_2_conflict_resolution_proposal": {
            "proposal_id": resolution_proposal.proposal_id,
            "kind": resolution_proposal.proposal_kind.value,
            "statement": resolution_proposal.statement,
            "relation_id": relation_conflict,
            "relation": "UNCHANGED",
            "winner": "NOT_SELECTED",
            "approval": "NOT_PERFORMED",
        },
        "example_3_gap_migration_proposal": {
            "proposal_id": migration_proposal.proposal_id,
            "kind": migration_proposal.proposal_kind.value,
            "statement": migration_proposal.statement,
            "relation_id": relation_gap,
            "task": "NOT_CREATED",
            "migration_started": False,
            "approval": "NOT_PERFORMED",
        },
        "example_4_additional_information_proposal": {
            "proposal_id": additional_information_proposal.proposal_id,
            "kind": additional_information_proposal.proposal_kind.value,
            "statement": additional_information_proposal.statement,
            "request_proposed": True,
            "external_request_executed": False,
            "approval": "NOT_PERFORMED",
        },
        "example_5_ai_originated_proposal": {
            "proposal_id": ai_proposal.proposal_id,
            "kind": ai_proposal.proposal_kind.value,
            "method": ai_proposal.proposal_method.value,
            "statement": ai_proposal.statement,
            "AI_CALL_PERFORMED": False,
            "AI_ORIGIN_PRESERVED": True,
            "APPROVAL": "NOT_PERFORMED",
        },
        "example_6_supersession": {
            "proposal_a_id": proposal_a.proposal_id,
            "proposal_b_id": proposal_b.proposal_id,
            "proposal_b_supersedes_proposal_a_id": proposal_b.supersedes_proposal_id,
            "proposal_a_status_after": superseded_a.status.value,
            "proposal_b_status_after": proposal_b.status.value,
            "proposal_a_deleted": False,
            "proposal_a_approved": False,
            "proposal_b_approved": False,
        },
    }


def render_proposal_example_json() -> str:
    """Renders the example fixture as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return json.dumps(build_proposal_example(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
