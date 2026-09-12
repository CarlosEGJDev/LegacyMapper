"""Deterministic contract-projection report for the V4 temporal-separation layer.

Projects the code-level temporal-separation contract for human/tool
consumption. Not canonical Knowledge Source content and carries no approval
semantics.
"""
import json

from legacy_documenter.knowledge.domain.enums import TemporalState
from legacy_documenter.knowledge.temporal.enums import TemporalBucket

SCHEMA_VERSION = "V4-R6"


def build_temporal_contract() -> dict:
    """Builds the full deterministic temporal-separation contract-projection payload as a plain dict."""
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_kind": "TEMPORAL_SEPARATION_CONTRACT_PROJECTION",
        "module": "legacy_documenter.knowledge.temporal",
        "note": "TEMPORAL_STATE_IS_NOT_TRUTH. TEMPORAL_STATE_IS_NOT_APPROVAL. "
                "TEMPORAL_STATE_IS_NOT_KNOWLEDGE_NATURE. "
                "AS_IS_TO_BE_DIFFERENCE_IS_NOT_AUTOMATICALLY_CONFLICT. "
                "HISTORICAL_IS_NOT_AUTOMATICALLY_SUPERSEDED. UNSPECIFIED_IS_VALID.",
        "temporal_states": sorted(s.value for s in TemporalState),
        "unspecified_representation": "MaterialItem.temporal_state is None",
        "temporal_buckets": sorted(b.value for b in TemporalBucket),
        "material_linkage": "By material_id only (legacy_documenter.knowledge.domain.models.MaterialItem.material_id); "
                             "no material payload is duplicated inside a TemporalPlacement.",
        "classification_independence": "TemporalPlacement never reads or mutates an R5 ClassificationRecord. "
                                        "Optional correlation (temporal.service.correlate_with_classification) "
                                        "joins the two by material_id only, in a read-only, non-mutating view.",
        "source_type_independence": "TemporalPlacement is derived only from MaterialItem.temporal_state; "
                                     "MaterialItem.source_type is never read by this module.",
        "provenance_independence": "This module never creates, reads, or mutates R3 ProvenanceGraph state.",
        "temporal_mapping": {
            "AS_IS": "AS_IS", "TO_BE": "TO_BE", "HISTORICAL": "HISTORICAL", "None": "UNSPECIFIED",
        },
        "inference_policy": "NONE. Only material.temporal_state (as already explicitly supplied to R4) is read. "
                             "No keyword matching, regex inference, filename/folder inference, SourceType mapping, "
                             "KnowledgeNature mapping, provenance-origin mapping, classifier mapping, date "
                             "inference, or LLM interpretation occurs anywhere in this module.",
        "as_is_semantics": "The material explicitly describes or belongs to the current/existing-state "
                            "perspective. Does not mean the statement is true, verified, authoritative, or approved.",
        "to_be_semantics": "The material explicitly describes or belongs to an intended/target/future-state "
                            "perspective. Does not mean the target is approved, will be implemented, or is canonical.",
        "historical_semantics": "The material explicitly belongs to a historical context. Does not automatically "
                                 "mean obsolete, superseded, incorrect, or irrelevant.",
        "unspecified_semantics": "No temporal state has been explicitly established. A valid, permanent-until-"
                                  "revisited state, never an error and never guessed away.",
        "conflict_distinction": "Separating AS_IS from TO_BE material is not conflict detection; no conflict "
                                 "object or status is ever created by this module.",
        "gap_distinction": "This module never detects or represents a gap between AS_IS and TO_BE material; "
                            "that is R7's responsibility.",
        "supersession_distinction": "HISTORICAL never implies or sets KnowledgeStatus.SUPERSEDED.",
        "approval_distinction": "TemporalPlacement carries no approval/approved/canonical field; a placement is "
                                 "never approved or promoted to canonical knowledge by existing.",
        "canonical_knowledge_distinction": "This module never creates a KnowledgeStatement or any canonical "
                                            "Knowledge Source content.",
        "identity_policy": "placement_id is derived via stable_id from (material_id, bucket) only; equivalent "
                            "placements always produce the same id, and it never depends on current time, "
                            "randomness, or object identity.",
        "ordering_policy": "separate_batch preserves original input order in both accepted and rejected lists; "
                            "by_bucket() groups accepted placements preserving each bucket's relative input order.",
        "serialization_policy": "Two TemporalPlacements built from the same (material_id, temporal_state) are "
                                 "structurally identical and serialize byte-identically.",
        "batch_policy": "Each material is separated independently; one invalid item never removes a valid result.",
        "duplicate_policy": {
            "same_material_id_same_temporal_state": "IDEMPOTENT_NO_OP (only the first placement is kept)",
            "same_material_id_different_temporal_state": "REJECTED_AS_CONFLICTING_DUPLICATE_IDENTITY",
        },
        "ai_boundary": "No LLM/provider call occurs anywhere in this module.",
        "security_policy": "R6 does not copy or inspect material content, metadata, references, rationale, or "
                            "classifier identity; it reads only material_id and temporal_state, so there is "
                            "nothing untrusted to sanitize in its own output.",
        "external_io_policy": "No file, network, provider, or directory-scan activity occurs anywhere in this "
                               "module. It operates only on already-ingested in-memory MaterialItem records.",
    }


def render_temporal_contract_json() -> str:
    """Renders the report as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return json.dumps(build_temporal_contract(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
