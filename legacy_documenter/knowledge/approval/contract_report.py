"""Deterministic contract-projection report for the V4-R9 Technical Lead approval layer.

Projects the code-level explicit-decision contract for human/tool
consumption. Not canonical Knowledge Source content and carries no canonical
Knowledge Source composition semantics of its own.
"""
from legacy_documenter.knowledge.approval.enums import ApprovalAuthority, ApprovalDecisionType
from legacy_documenter.utils.json_rendering import render_deterministic_json

SCHEMA_VERSION = "V4-R9"


def build_approval_contract() -> dict:
    """Builds the full deterministic R9 Technical Lead approval-layer contract-projection payload as a plain dict."""
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_kind": "TECHNICAL_LEAD_APPROVAL_CONTRACT_PROJECTION",
        "module": "legacy_documenter.knowledge.approval",
        "note": "ONLY_TECHNICAL_LEAD_MAY_AUTHORIZE_APPROVAL. READY_FOR_REVIEW_IS_NOT_APPROVED. "
                "APPROVED_IS_NOT_CANONICALIZED. REJECTED_IS_NOT_FALSE. "
                "CORRECTION_REQUESTED_IS_NOT_REJECTED. PROPOSAL_METHOD_DOES_NOT_DETERMINE_DECISION. "
                "AI_NEVER_APPROVES. SYSTEM_NEVER_APPROVES. R9_RECORDS_HUMAN_AUTHORITY. "
                "R9_DOES_NOT_CREATE_HUMAN_AUTHORITY. APPROVED_ONLY_MAKES_PROPOSAL_ELIGIBLE_FOR_R10. "
                "R10_OWNS_CANONICAL_KNOWLEDGE_COMPOSITION.",
        "decision_types": sorted(decision.value for decision in ApprovalDecisionType),
        "authority_types": sorted(authority.value for authority in ApprovalAuthority),
        "decision_semantics": {
            "APPROVED": "The Technical Lead explicitly accepts the proposal for later canonical composition. "
                        "Does not itself create canonical knowledge. APPROVED != CANONICALIZED.",
            "REJECTED": "The Technical Lead explicitly decides this proposal should not proceed. Does not mean "
                        "the proposal statement, source material, relation, or underlying requirement is "
                        "objectively false. REJECTED != FALSE.",
            "CORRECTION_REQUESTED": "The Technical Lead does not approve the proposal in its current form and "
                                    "requests correction before another approval decision. Does not mean "
                                    "permanently rejected, false, or that canonical knowledge changed. "
                                    "CORRECTION_REQUESTED != REJECTED.",
        },
        "authority_semantics": {
            "TECHNICAL_LEAD": "The sole valid V4 approval authority. Recording authority=TECHNICAL_LEAD means the "
                              "caller explicitly supplied this decision as a Technical Lead decision; it never "
                              "means this module itself acted as the Technical Lead. No RBAC, no ADMIN/MANAGER/"
                              "REVIEWER/AI/SYSTEM authority exists in V4.",
        },
        "proposal_status_precondition": "READY_FOR_REVIEW_ONLY. A decision may only be recorded against an R8 "
                                        "Proposal whose current status is ProposalStatus.READY_FOR_REVIEW. "
                                        "DRAFT/WITHDRAWN/SUPERSEDED are rejected deterministically. "
                                        "READY_FOR_REVIEW is necessary but not sufficient: an explicit Technical "
                                        "Lead decision is still required.",
        "explicit_decision_policy": "REQUIRED. decision, authority, and decided_by must always be supplied "
                                    "explicitly by the caller. Never inferred from proposal_method, proposal_kind, "
                                    "proposal content, source type, relation kind, confidence, evidence count, "
                                    "human/AI origin, dates, or previous decisions.",
        "automatic_decision_policy": "NONE. No AI_APPROVED/SYSTEM_APPROVED/AUTO_APPROVED/RULE_APPROVED decision "
                                     "origin exists; no code path infers or fabricates a decision.",
        "approval_record_model": {
            "decision_id": "Deterministic APR- id derived from immutable semantic fields only.",
            "proposal_id": "The R8 Proposal id being decided on. Never mutated.",
            "decision": "One of the closed decision_types.",
            "authority": "One of the closed authority_types (TECHNICAL_LEAD only).",
            "decided_by": "Explicit human identifier. Required. Never inferred from OS/Git/environment.",
            "rationale": "Optional free text, sanitized before storage.",
            "correction_instructions": "Optional free text, sanitized before storage.",
            "previous_decision_id": "Optional, for tracing a redecision recorded against a new proposal version "
                                    "after correction.",
            "metadata": "Optional JSON-compatible dict, sanitized before storage.",
        },
        "decision_identity_policy": "decision_id is derived via stable_id (APR- prefix) from (proposal_id, "
                                    "decision, authority, decided_by, rationale, correction_instructions, "
                                    "previous_decision_id) only. metadata, current time, randomness, machine "
                                    "identity, and object identity are excluded from identity.",
        "duplicate_policy": {
            "exact_duplicate": "IDEMPOTENT_NO_OP (same decision_id and same full content; the existing record is "
                               "returned unchanged)",
            "conflicting_duplicate_identity": "REJECTED (same decision_id, different content is never silently "
                                              "overwritten; unreachable in practice because decision_id is a "
                                              "deterministic hash of that same content, but guarded explicitly)",
            "second_decision_for_decided_proposal": "REJECTED (a different decision against a proposal_id that "
                                                    "already has any recorded decision is never accepted as an "
                                                    "overwrite)",
        },
        "decision_history_policy": "PRESERVED. No operation overwrites or deletes a stored ApprovalDecision. "
                                   "ApprovalCollection.list()/for_proposal()/by_decision() return every decision "
                                   "ever recorded, in insertion order.",
        "redecision_policy": "ONE_DECISION_PER_PROPOSAL_ID. A specific immutable proposal_id may receive at most "
                             "one recorded ApprovalDecision (APPROVED, REJECTED, or CORRECTION_REQUESTED); a "
                             "second, non-identical decision attempt against the same proposal_id is rejected "
                             "deterministically, never silently replacing the first. After CORRECTION_REQUESTED, "
                             "the same proposal_id does not receive a further terminal decision either: the "
                             "expected path is a new, distinct R8 proposal version (created via R8 supersession, "
                             "out of R9 scope) that receives its own separate decision under its own proposal_id, "
                             "optionally linked back via previous_decision_id.",
        "correction_policy": "CORRECTION_REQUESTED never mutates the reviewed Proposal's statement in place; the "
                             "reviewed proposal remains historical evidence of what was reviewed. This module "
                             "never automatically creates a corrected Proposal or a supersession; that remains an "
                             "explicit R8 caller action.",
        "proposal_immutability_policy": "NONE. Recording a decision never sets proposal.status, never mutates any "
                                        "Proposal field, and never calls transition_proposal/supersede.",
        "relation_mutation_policy": "NONE",
        "material_mutation_policy": "NONE",
        "classification_mutation_policy": "NONE",
        "temporal_mutation_policy": "NONE",
        "provenance_mutation_policy": "NONE",
        "knowledge_status_mutation_policy": "NONE",
        "approval_vs_truth": "REJECTED != FALSE. A decision never determines whether the proposal statement, "
                            "referenced material, or referenced relation is objectively true or false.",
        "approval_vs_authority": "authority=TECHNICAL_LEAD records that the caller explicitly supplied this "
                                 "decision as a Technical Lead decision; it never means this module acted as the "
                                 "Technical Lead or fabricated the record during normal processing.",
        "approval_vs_proposal_origin": "HUMAN_PROPOSED != APPROVED. AI_PROPOSED != REJECTED. "
                                       "DETERMINISTIC_RULE != APPROVED. proposal_method has no automatic influence "
                                       "on decision.",
        "approval_vs_canonical_knowledge": "APPROVED != CANONICALIZED. Even an APPROVED ApprovalDecision never "
                                           "produces a KnowledgeStatement, a canonical Knowledge Source, a Plugin "
                                           "payload, or a canonical document. R10 owns Canonical Knowledge "
                                           "Composition; R9 only makes the proposal eligible for it.",
        "canonical_eligibility_policy": "is_eligible_for_canonical_composition(collection, proposal_id): "
                                        "APPROVED -> true, REJECTED -> false, CORRECTION_REQUESTED -> false, "
                                        "no recorded decision -> false. Reports eligibility only; never composes, "
                                        "creates, or mutates canonical knowledge.",
        "R10_boundary": "R9 ends at ApprovalDecision(decision=APPROVED), meaning only that the proposal is "
                        "eligible for canonical composition. No KnowledgeStatement creation, canonical Knowledge "
                        "Source update, human-readable canonical projection, or Plugin knowledge generation occurs "
                        "anywhere in this module; those belong to V4-R10.",
        "AI_boundary": "No LLM/provider call occurs anywhere in this module. AI must never determine approval; "
                       "AI_PROPOSED proposal origin is preserved as data but never upgraded into an approval "
                       "outcome.",
        "security_policy": "All decision input is treated as untrusted. decided_by, rationale, and "
                           "correction_instructions are passed through the shared text sanitizer and metadata "
                           "through the shared JSON-compatible data sanitizer before being stored; no eval/exec/"
                           "dynamic import/shell/template execution occurs anywhere in this module, so "
                           "prompt-injection-shaped text inside these fields remains inert. Exception messages use "
                           "fixed codes only and never echo untrusted decision content.",
        "external_io_policy": "No file, network, provider, database, or directory-scan activity occurs anywhere "
                              "in this module. It operates only on an explicit ApprovalRequest and an "
                              "already-available, read-only R8 Proposal object.",
    }


def render_approval_contract_json() -> str:
    """Renders the report as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return render_deterministic_json(build_approval_contract())
