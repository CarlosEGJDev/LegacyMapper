"""Deterministic contract-projection report for the V4 human-material ingestion boundary.

Projects the code-level ingestion contract for human/tool consumption. Not
canonical Knowledge Source content and carries no approval semantics.
"""
import json

from legacy_documenter.knowledge.domain.enums import SourceType
from legacy_documenter.knowledge.ingestion.service import HUMAN_SUPPLIED_SOURCE_TYPES

SCHEMA_VERSION = "V4-R4"

REJECTED_SOURCE_TYPES = sorted(st.value for st in set(SourceType) - HUMAN_SUPPLIED_SOURCE_TYPES)


def build_ingestion_contract() -> dict:
    """Builds the full deterministic ingestion contract-projection payload as a plain dict."""
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_kind": "HUMAN_MATERIAL_INGESTION_CONTRACT_PROJECTION",
        "module": "legacy_documenter.knowledge.ingestion",
        "note": "INGESTED_MATERIAL_IS_NOT_APPROVED_KNOWLEDGE. Ingestion produces traceable material; "
                "it never produces approved, current, complete, or canonical knowledge.",
        "accepted_source_types": sorted(st.value for st in HUMAN_SUPPLIED_SOURCE_TYPES),
        "rejected_source_types": REJECTED_SOURCE_TYPES,
        "rejected_source_types_reason": {
            "DETERMINISTIC_CODE_FACT": "belongs to the deterministic code pipeline, not the human-ingestion boundary",
            "AI_INTERPRETATION": "not human-supplied material, regardless of whether its payload reads as text",
        },
        "input_contract": "Reuses legacy_documenter.knowledge.input.validator.validate_source_input (R2) "
                           "unchanged; R4 never weakens or duplicates R2 rules.",
        "material_contract": "Reuses legacy_documenter.knowledge.domain.models.MaterialItem (R1), extended in "
                              "V4-R4 with an optional temporal_state field (backward compatible, defaults to None).",
        "provenance_contract": "Reuses legacy_documenter.knowledge.provenance.graph.material_node_from_source_input "
                                "(R3) to produce a single MATERIAL-kind ProvenanceNode per ingested item; R4 never "
                                "creates EVIDENCE, STATEMENT, INTERPRETATION, PROPOSAL, or KNOWLEDGE nodes.",
        "normalization_policy": "DETERMINISTIC_NON_SEMANTIC: whitespace/blank-to-absent canonicalization and "
                                 "sanitization only (via R2 normalization and the existing sanitizer). No "
                                 "summarization, paraphrasing, requirement/actor/rule extraction, or inference.",
        "identity_policy": "material_id is derived deterministically via "
                            "legacy_documenter.knowledge.domain.models.new_material_id from "
                            "(source_type, normalized content, normalized reference, normalized title); "
                            "the MATERIAL provenance node reuses the same id, so the two records always correlate.",
        "temporal_policy": "An explicitly supplied AS_IS/TO_BE/HISTORICAL is preserved verbatim on MaterialItem. "
                            "Missing temporal_state remains missing (None). Never inferred from prose.",
        "origin_policy": "Human contributor/origin is preserved verbatim (sanitized, never rewritten). Missing "
                          "origin remains missing; LegacyMapper's own processing identity never replaces the "
                          "original contributor.",
        "batch_policy": "Each item is ingested independently; accepted and rejected lists both preserve original "
                         "input order. All accepted items in one ingest_batch call share one ProvenanceGraph.",
        "duplicate_policy": "DETERMINISTIC_EXACT_ONLY: same normalized identity produces the same material_id and "
                             "the same MATERIAL node id; adding an exact duplicate node to the shared batch graph "
                             "is an idempotent no-op per R3's documented policy. No semantic/fuzzy deduplication.",
        "failure_isolation_policy": "One invalid batch item is rejected with a sanitized, deterministic reason; "
                                     "it never removes or corrupts another item's acceptance.",
        "classification_boundary": "R4 never assigns KnowledgeNature. Source type and knowledge nature remain "
                                    "distinct dimensions; classification is R5's responsibility.",
        "approval_boundary": "R4 never sets any approval/authoritative state. Submission and Technical Lead "
                              "approval are distinct lifecycle events (R9).",
        "knowledge_boundary": "R4 produces MaterialItem + a MATERIAL provenance node only; it never produces a "
                               "KnowledgeStatement, a PROPOSAL, or canonical Knowledge Source content.",
        "ai_boundary": "AI_INTERPRETATION is rejected by the human-ingestion boundary before R2 validation runs, "
                       "so it is never silently accepted merely because its payload is text.",
        "security_policy": "All content/reference/title/contributor/metadata is sanitized (reusing the existing "
                            "sanitizer and R2's metadata validator) before storage; Origin fields, untouched by R2, "
                            "are separately sanitized at the ingestion boundary without modifying R1's Origin type.",
        "prompt_injection_policy": "All ingested content is DATA. Instruction-like or prompt-injection-style text "
                                    "(e.g. \"Ignore previous instructions...\") is stored verbatim (after routine "
                                    "sanitization) as inert material; it is never executed, never obeyed, and never "
                                    "triggers a provider/LLM call, by construction (no code path in this module "
                                    "interprets material content as instructions).",
        "external_io_policy": "No file open, network fetch, SharePoint/Confluence/Bitbucket query, provider call, "
                               "or directory scan occurs anywhere in this module. A reference is stored and "
                               "sanitized as a string only.",
    }


def render_ingestion_contract_json() -> str:
    """Renders the report as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return json.dumps(build_ingestion_contract(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
