"""Deterministic contract-projection report for the V4-R8 proposal lifecycle.

Projects the code-level explicit-proposal contract for human/tool
consumption. Not canonical Knowledge Source content and carries no approval,
authority, or canonical-knowledge semantics.
"""
from legacy_documenter.knowledge.proposals.enums import ProposalKind, ProposalMethod, ProposalStatus
from legacy_documenter.utils.json_rendering import render_deterministic_json

SCHEMA_VERSION = "V4-R8"


def build_proposal_contract() -> dict:
    """Builds the full deterministic R8 proposal-lifecycle contract-projection payload as a plain dict."""
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_kind": "PROPOSAL_LIFECYCLE_CONTRACT_PROJECTION",
        "module": "legacy_documenter.knowledge.proposals",
        "note": "PROPOSAL_IS_NOT_APPROVAL. PROPOSAL_IS_NOT_DECISION. PROPOSAL_IS_NOT_TRUTH. "
                "PROPOSAL_IS_NOT_AUTHORITY. PROPOSAL_IS_NOT_CANONICAL_KNOWLEDGE. "
                "PROPOSAL_IS_NOT_IMPLEMENTATION. READY_FOR_REVIEW_IS_NOT_APPROVED. "
                "HUMAN_PROPOSED_IS_NOT_APPROVED. DETERMINISTIC_RULE_IS_NOT_APPROVED. "
                "AI_PROPOSED_IS_NOT_APPROVED. "
                "CONFLICT_DOES_NOT_AUTOMATICALLY_CREATE_RESOLUTION_PROPOSAL. "
                "GAP_DOES_NOT_AUTOMATICALLY_CREATE_MIGRATION_PROPOSAL. "
                "PROPOSAL_DOES_NOT_RESOLVE_RELATION. PROPOSAL_DOES_NOT_MUTATE_SOURCE_MATERIAL. "
                "R9_OWNS_TECHNICAL_LEAD_APPROVAL. R10_OWNS_CANONICAL_KNOWLEDGE_COMPOSITION.",
        "proposal_kinds": sorted(kind.value for kind in ProposalKind),
        "proposal_statuses": sorted(status.value for status in ProposalStatus),
        "proposal_methods": sorted(method.value for method in ProposalMethod),
        "proposal_semantics": {
            "INTERPRETATION": "Proposes an interpretation of available material/evidence. Does not make the "
                               "interpretation true.",
            "RESOLUTION": "Proposes a way to resolve an explicitly represented issue/relation. Does not resolve "
                          "it automatically.",
            "CORRECTION": "Proposes that existing knowledge/material should be corrected. Does not modify the "
                          "source material or canonical knowledge.",
            "RECONCILIATION": "Proposes how multiple materials or statements could be reconciled. Does not merge "
                              "or replace them automatically.",
            "SELECTION": "Proposes selecting one candidate/alternative over another. Does not establish a winner "
                        "or authority.",
            "ADDITIONAL_INFORMATION": "Proposes requesting or supplying additional information before proceeding. "
                                      "Does not automatically make the underlying material MISSING or UNRESOLVED.",
            "MIGRATION": "Proposes a migration/change from one explicitly identified state to another. Does not "
                        "imply migration is approved, scheduled, started, or completed.",
            "KNOWLEDGE_ADDITION": "Proposes that a new knowledge statement/content should eventually be "
                                  "incorporated. Does not create canonical knowledge.",
        },
        "proposal_basis_policy": "REQUIRED. At least one of material_ids, relation_ids, or evidence_refs must be "
                                  "non-empty; a proposal with no basis at all is rejected. Basis references are "
                                  "preserved verbatim (never invented) and never duplicate full source payloads.",
        "creation_policy": "EXPLICIT_ONLY. proposal_kind, statement, and proposal_method must be supplied by the "
                            "caller. No proposal prose is ever auto-generated from materials, relations, "
                            "classifications, temporal states, or evidence.",
        "initial_status": "DRAFT. Creation never automatically produces READY_FOR_REVIEW; that requires a "
                           "separate explicit, validated transition.",
        "valid_transitions": {
            "DRAFT": sorted(["READY_FOR_REVIEW", "WITHDRAWN", "SUPERSEDED"]),
            "READY_FOR_REVIEW": sorted(["SUPERSEDED", "WITHDRAWN"]),
            "WITHDRAWN": [],
            "SUPERSEDED": [],
        },
        "invalid_transition_policy": "REJECTED_DETERMINISTICALLY. Any transition outside the closed "
                                      "valid_transitions map (for example WITHDRAWN->READY_FOR_REVIEW or "
                                      "SUPERSEDED->READY_FOR_REVIEW) raises ProposalTransitionError. proposal_id "
                                      "and all immutable content are preserved through every valid transition.",
        "ready_for_review_semantics": "Structural readiness only: proposal_kind present, statement meaningful, "
                                       "proposal_method present, at least one basis reference present. Never a "
                                       "semantic/truth validation and never an approval decision. "
                                       "READY_FOR_REVIEW != approved, accepted, validated as true, or canonical.",
        "withdrawn_semantics": "This proposal is no longer being advanced for review. Does not mean false, "
                                "rejected by the Technical Lead, incorrect, or deleted. Withdrawn proposals are "
                                "preserved, never deleted, for traceability.",
        "superseded_semantics": "Another proposal explicitly replaces this proposal in the proposal lifecycle. "
                                 "Never inferred from creation date, a newer proposal, the same relation, the "
                                 "same material, or the same proposal kind. The superseded proposal's historical "
                                 "content is never mutated or deleted.",
        "supersession_policy": "EXPLICIT_ONLY via Proposal.supersedes_proposal_id, applied through "
                                "ProposalCollection.supersede(). Self-supersession (A supersedes A) is rejected "
                                "at both construction and collection level. A simple two-proposal cycle "
                                "(A supersedes B, B supersedes A) is rejected by ProposalCollection when both "
                                "proposals are present.",
        "identity_policy": "proposal_id is derived via stable_id (PRP- prefix) from (proposal_kind, statement, "
                            "proposal_method, canonical sorted material_ids, canonical sorted relation_ids, "
                            "canonical sorted evidence_refs) only. status, rationale, proposed_by, "
                            "supersedes_proposal_id, metadata, current time, randomness, and object identity are "
                            "excluded from identity. A DRAFT proposal and its READY_FOR_REVIEW/WITHDRAWN/"
                            "SUPERSEDED transitions all retain the same proposal_id.",
        "reference_ordering_policy": "material_ids, relation_ids, and evidence_refs are canonicalized to sorted, "
                                      "unique tuples before identity is computed; input ordering never changes "
                                      "proposal identity.",
        "duplicate_policy": {
            "exact_duplicate": "IDEMPOTENT_NO_OP (same proposal_id and same full content; only the first is kept)",
            "conflicting_duplicate_identity": "REJECTED (same proposal_id, different rationale/proposed_by/"
                                               "supersedes_proposal_id/metadata is never silently overwritten)",
            "status_change_mechanism": "LIFECYCLE_TRANSITION_ONLY (never duplicate creation)",
        },
        "serialization_policy": "Two Proposals built from the same (proposal_kind, statement, proposal_method, "
                                 "canonical material_ids/relation_ids/evidence_refs) are structurally identical "
                                 "and serialize byte-identically regardless of input reference ordering.",
        "relation_integration": "A proposal may reference zero or more R7 KnowledgeRelation ids as basis. "
                                 "Referencing a relation never mutates it, never resolves it, never selects a "
                                 "winner, and never alters its participants.",
        "relation_mutation_policy": "NONE",
        "material_mutation_policy": "NONE",
        "classification_mutation_policy": "NONE",
        "temporal_mutation_policy": "NONE",
        "provenance_mutation_policy": "NONE",
        "approval_distinction": "A Proposal carries no approved/accepted field; READY_FOR_REVIEW never means the "
                                 "Technical Lead approved the proposal, its basis, or a resolution.",
        "authority_distinction": "proposal_method records origin, not authority: HUMAN_PROPOSED is never "
                                  "automatically authoritative, AI_PROPOSED is never automatically untrustworthy, "
                                  "and DETERMINISTIC_RULE is never automatically canonical.",
        "truth_distinction": "A Proposal never determines whether its statement, or the relation/material it "
                              "references, is true.",
        "decision_distinction": "Creating or transitioning a Proposal is never itself a Technical Lead decision.",
        "canonical_knowledge_distinction": "This module never creates a KnowledgeStatement or any canonical "
                                            "Knowledge Source content, and never sets a canonical=true field, "
                                            "even for a READY_FOR_REVIEW proposal.",
        "implementation_distinction": "A MIGRATION or CORRECTION proposal never creates a task, project, "
                                       "schedule, budget, or implementation record, and never marks migration as "
                                       "started or completed.",
        "AI_proposal_policy": "AI_PROPOSED is representable as proposal_method for future compatibility only. It "
                               "is data describing origin; it never causes an AI/LLM call and is never silently "
                               "upgraded into HUMAN_PROPOSED, DETERMINISTIC_RULE, APPROVED, CONFIRMED, or "
                               "CANONICAL merely because it passes structural validation.",
        "AI_boundary": "No LLM/provider call occurs anywhere in this module.",
        "R9_boundary": "R8 ends at Proposal(status=READY_FOR_REVIEW). No approve_proposal, reject_proposal, or "
                        "correct_and_approve operation exists in this module; APPROVED/REJECTED/CORRECTED are R9 "
                        "Technical Lead approval outcomes never produced here.",
        "R10_boundary": "Even a READY_FOR_REVIEW proposal never causes creation of a KnowledgeStatement, a "
                         "canonical Knowledge Source, or human-readable canonical documentation; R10 owns "
                         "Canonical Knowledge Composition after R9 approval.",
        "security_policy": "All proposal input is treated as untrusted. statement, rationale, and proposed_by are "
                            "passed through the shared text sanitizer and metadata through the shared "
                            "JSON-compatible data sanitizer before being stored; no eval/exec/dynamic import/"
                            "shell/template execution occurs anywhere in this module, so prompt-injection-shaped "
                            "text inside statement/rationale/metadata remains inert. Exception messages use fixed "
                            "codes only and never echo untrusted proposal content.",
        "external_io_policy": "No file, network, provider, database, or directory-scan activity occurs anywhere "
                               "in this module. It operates only on already-available in-memory records and "
                               "explicit proposal requests.",
    }


def render_proposal_contract_json() -> str:
    """Renders the report as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return render_deterministic_json(build_proposal_contract())
