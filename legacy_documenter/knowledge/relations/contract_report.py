"""Deterministic contract-projection report for the V4-R7 relation layer.

Projects the code-level explicit-relation contract for human/tool
consumption. Not canonical Knowledge Source content and carries no approval,
canonical, or resolution semantics.
"""
import json

from legacy_documenter.knowledge.relations.enums import RelationKind

SCHEMA_VERSION = "V4-R7"


def build_relation_contract() -> dict:
    """Builds the full deterministic R7 relation contract-projection payload as a plain dict."""
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_kind": "GAP_CONFLICT_RELATION_CONTRACT_PROJECTION",
        "module": "legacy_documenter.knowledge.relations",
        "note": "R7_REPRESENTS_EXPLICIT_RELATIONSHIPS. R7_DOES_NOT_DISCOVER_THEM_FROM_NATURAL_LANGUAGE_CONTENT. "
                "DIFFERENCE_IS_NOT_GAP. DIFFERENCE_IS_NOT_CONFLICT. GAP_IS_NOT_CONFLICT. "
                "AS_IS_TO_BE_IS_NOT_AUTOMATICALLY_GAP. AS_IS_TO_BE_IS_NOT_AUTOMATICALLY_CONFLICT. "
                "AS_IS_TO_BE_IS_NOT_AUTOMATICALLY_TEMPORAL_EVOLUTION. "
                "CONFLICT_DOES_NOT_SELECT_A_WINNER. GAP_DOES_NOT_CREATE_A_PROPOSAL. "
                "RELATION_DOES_NOT_IMPLY_APPROVAL. RELATION_DOES_NOT_MUTATE_KNOWLEDGE_STATUS.",
        "relation_kinds": sorted(kind.value for kind in RelationKind),
        "difference_semantics": "Two or more related materials express different values, descriptions, states, "
                                 "constraints, or perspectives. Neutral: does not mean one is incorrect, "
                                 "superseding, a gap, a conflict, an error, or a required migration.",
        "gap_semantics": "An explicitly established separation between an observed/provided condition and a "
                          "required/desired/expected condition. Never inferred merely because materials are "
                          "AS_IS/TO_BE or because their content differs. Does not mean MISSING, UNRESOLVED, error, "
                          "failure, non-compliance, or rejection.",
        "conflict_semantics": "An explicitly established incompatibility between two applicable materials. Never "
                               "derived by comparing prose. Does not determine which participant is correct, has "
                               "greater authority, should be rejected, or should become canonical, and does not "
                               "determine whether either statement is false.",
        "temporal_evolution_semantics": "An explicitly declared evolution/change between knowledge states over "
                                         "time or between temporal perspectives. R6 temporal placement alone never "
                                         "creates this relation. Does not automatically mean migration required, "
                                         "supersession, approval, or implementation completed/planned.",
        "explicit_relation_policy": "REQUIRED. A relation is created only from an explicit RelationRequest "
                                     "(relation_kind + two participant material ids); no relation is ever created "
                                     "merely because two materials exist or are correlated.",
        "semantic_detection_policy": "NOT_PERFORMED. No keyword matching, regex, text similarity, embeddings, LLM, "
                                      "classifier, filename, or directory inspection is used anywhere in this "
                                      "module to decide a relation_kind.",
        "participant_model": "Each relation references exactly two participants by MaterialItem.material_id only; "
                              "no material payload is duplicated inside a KnowledgeRelation.",
        "participant_cardinality": "EXACTLY_TWO. A relation cannot reference zero or one unique participant.",
        "self_relation_policy": "REJECTED. A relation with the same material id on both sides is always rejected "
                                 "for all four relation kinds.",
        "directionality_policy": "Fixed per relation_kind, never inferred from TemporalState, SourceType, "
                                  "KnowledgeNature, dates, or participant input ordering.",
        "symmetric_relation_policy": "DIFFERENCE and CONFLICT are SYMMETRIC: participants are canonically sorted, "
                                      "so REL(A,B) and REL(B,A) always produce the identical relation.",
        "directional_relation_policy": "GAP and TEMPORAL_EVOLUTION are DIRECTIONAL: material_a is FROM and "
                                        "material_b is TO, exactly as supplied by the caller; REL(A->B) and "
                                        "REL(B->A) are always distinct relations.",
        "duplicate_policy": {
            "exact_duplicate": "IDEMPOTENT_NO_OP (only the first relation is kept)",
            "conflicting_duplicate_identity": "REJECTED (same relation_id, different basis/notes/evidence/metadata "
                                               "is never silently overwritten)",
            "symmetric_reversed_input": "SAME_RELATION (canonicalized before identity is computed)",
            "directional_reversed_input": "DISTINCT_RELATION (direction is part of identity)",
        },
        "identity_policy": "relation_id is derived via stable_id from (relation_kind, canonical participants) "
                            "only; basis, notes, evidence_refs, and metadata are excluded from identity. Never "
                            "depends on current time, randomness, or object identity.",
        "ordering_policy": "create_relation_batch preserves original input order in both accepted and rejected "
                            "lists; RelationCollection.list()/by_kind()/relations_for() preserve insertion order. "
                            "Never depends on Python set/dict iteration order for semantic output.",
        "serialization_policy": "Two KnowledgeRelations built from the same (relation_kind, canonical "
                                 "participants) are structurally identical and serialize byte-identically.",
        "source_type_independence": "Relation kind is never derived from MaterialItem.source_type; this module "
                                     "never reads or requires SourceType.",
        "classification_independence": "KnowledgeRelation never reads or mutates an R5 ClassificationRecord. "
                                        "Optional correlation (relations.service.correlate_with_classification) "
                                        "joins by material_id only, in a read-only, non-mutating view, and never "
                                        "requires classification to exist.",
        "temporal_independence": "Relation kind is never derived from R6 TemporalState/TemporalBucket. Optional "
                                  "correlation (relations.service.correlate_with_temporal) joins by material_id "
                                  "only, in a read-only, non-mutating view.",
        "provenance_independence": "This module never creates, reads, or mutates R3 ProvenanceGraph state.",
        "knowledge_status_distinction": "A relation never mutates a participant's KnowledgeStatus. CONFLICT != "
                                         "automatic CONFLICTING; GAP != automatic MISSING; TEMPORAL_EVOLUTION != "
                                         "automatic SUPERSEDED.",
        "approval_distinction": "A KnowledgeRelation carries no approved/accepted field; its existence never "
                                 "means the Technical Lead approved the relation, its participants, or a "
                                 "resolution.",
        "authority_distinction": "A relation never determines which participant has greater authority.",
        "proposal_distinction": "R7 creates no Proposal object. A relation is relational evidence/context only; "
                                 "resolution, correction, selection, reconciliation, migration, or an "
                                 "additional-information request belongs to R8 or later.",
        "canonical_knowledge_distinction": "This module never creates a KnowledgeStatement or any canonical "
                                            "Knowledge Source content, and never sets a canonical=true field.",
        "AI_boundary": "No LLM/provider call occurs anywhere in this module. AI_PROPOSED is representable in "
                        "RelationBasis for future compatibility only; R7 itself never produces it.",
        "security_policy": "All relation input is treated as untrusted. notes are passed through the shared text "
                            "sanitizer and metadata through the shared JSON-compatible data sanitizer before being "
                            "stored; no eval/exec/dynamic import/shell/template execution occurs anywhere in this "
                            "module, so prompt-injection-shaped text inside notes/metadata remains inert.",
        "external_io_policy": "No file, network, provider, database, or directory-scan activity occurs anywhere "
                               "in this module. It operates only on already-ingested in-memory records and "
                               "explicit relation requests.",
    }


def render_relation_contract_json() -> str:
    """Renders the report as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return json.dumps(build_relation_contract(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
