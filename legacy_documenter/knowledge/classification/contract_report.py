"""Deterministic contract-projection report for the V4 knowledge-classification layer.

Projects the code-level classification contract for human/tool consumption.
Not canonical Knowledge Source content and carries no approval semantics.
"""
import json

from legacy_documenter.knowledge.classification.catalog import KnowledgeNatureCatalog
from legacy_documenter.knowledge.classification.enums import ClassificationMethod, ClassificationStatus
from legacy_documenter.knowledge.domain.enums import KnowledgeNature

SCHEMA_VERSION = "V4-R5"


def _nature_entry(nature: KnowledgeNature) -> dict:
    semantics = KnowledgeNatureCatalog.get(nature)
    return {
        "nature": nature.value,
        "semantic_role": semantics.semantic_role,
        "prescriptive_or_descriptive": semantics.prescriptive_or_descriptive,
        "notes": semantics.notes,
    }


def build_classification_contract() -> dict:
    """Builds the full deterministic classification contract-projection payload as a plain dict."""
    KnowledgeNatureCatalog.assert_complete()
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_kind": "KNOWLEDGE_CLASSIFICATION_CONTRACT_PROJECTION",
        "module": "legacy_documenter.knowledge.classification",
        "note": "SOURCE_TYPE_IS_NOT_KNOWLEDGE_NATURE. CLASSIFIED_IS_NOT_APPROVED_KNOWLEDGE. "
                "Classification records what semantic nature has been explicitly established for "
                "already-ingested material; it never establishes truth, currency, approval, or "
                "canonical status.",
        "knowledge_natures": [_nature_entry(n) for n in sorted(KnowledgeNature, key=lambda n: n.value)],
        "classification_statuses": sorted(s.value for s in ClassificationStatus),
        "classification_methods": sorted(m.value for m in ClassificationMethod),
        "classification_record_contract": "ClassificationRecord{classification_id, material_id, source_type, "
                                           "status, classification_method, selected_nature?, candidate_natures[], "
                                           "rationale?, classified_by?, metadata}. CLASSIFIED requires exactly one "
                                           "selected_nature and no candidates; UNCLASSIFIED requires neither; "
                                           "AMBIGUOUS requires no selected_nature and >=2 distinct candidates.",
        "material_linkage": "By material_id only (legacy_documenter.knowledge.domain.models.MaterialItem.material_id); "
                             "no material payload is duplicated inside a ClassificationRecord.",
        "source_type_distinction": "source_type is copied from the classified MaterialItem and never mutated. "
                                    "It is preserved for correlation only, never used to derive selected_nature.",
        "temporal_distinction": "Classification never reads or infers MaterialItem.temporal_state; the same "
                                 "selected_nature is valid regardless of AS_IS/TO_BE/HISTORICAL/None.",
        "provenance_distinction": "Classification never creates, rewrites, or reads R3 ProvenanceGraph state; "
                                   "the two concerns are independent and both keyed by material_id only.",
        "approval_distinction": "ClassificationRecord carries no approved/approval_status/authoritative_truth "
                                 "field. CLASSIFIED is a resolution state, not a Technical Lead approval (R9).",
        "canonical_knowledge_distinction": "Classification never creates a KnowledgeStatement or any canonical "
                                            "Knowledge Source content (R10).",
        "candidate_policy": "candidate_natures is canonicalized to a duplicate-free tuple sorted by enum value "
                             "before storage; unknown/invalid enum values are rejected, never coerced.",
        "ambiguity_policy": "AMBIGUOUS requires at least two distinct candidates and never auto-selects a winner.",
        "unclassified_policy": "UNCLASSIFIED requires no selected_nature and no candidates; it is a legitimate, "
                                "permanent-until-revisited lifecycle state, not an error or a default fallback.",
        "identity_policy": "classification_id is derived via stable_id from (material_id, status, selected_nature, "
                            "canonical candidate tuple, classification_method) only — rationale/classified_by/"
                            "metadata are excluded from identity as attribution/explanatory data, not decision data.",
        "serialization_policy": "candidate_natures is always stored pre-sorted; two ClassificationRecords built "
                                 "from the same candidate set in different input orders are structurally identical "
                                 "and serialize byte-identically.",
        "batch_policy": "classify_batch evaluates each request independently and preserves original input order "
                         "in both accepted and rejected lists.",
        "failure_isolation_policy": "One invalid batch request is rejected with a sanitized, deterministic reason; "
                                     "it never removes or corrupts another request's acceptance.",
        "ai_boundary": "AI_PROPOSED is reserved in the ClassificationMethod enum for a future round; R5 never "
                       "produces it and makes no LLM/provider call.",
        "security_policy": "rationale, classified_by, and metadata are sanitized (reusing the existing sanitizer "
                            "and R2's metadata validator) before storage.",
        "external_io_policy": "No file open, network fetch, API call, or directory scan occurs anywhere in this "
                               "module. Classification operates only on an already-ingested MaterialItem and "
                               "explicitly supplied enum values/text.",
    }


def render_classification_contract_json() -> str:
    """Renders the report as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return json.dumps(build_classification_contract(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
