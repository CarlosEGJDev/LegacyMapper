"""Deterministic contract-projection report for the V4 input/source contract layer.

Produces the machine-readable description of every registered
`SourceContractPolicy`. This report is a projection of the code-level
contract for human/tool consumption; it is not canonical Knowledge Source
content and carries no approval semantics of its own.
"""
import json

from legacy_documenter.knowledge.domain.enums import SourceType
from legacy_documenter.knowledge.input.catalog import SourceContractCatalog

SCHEMA_VERSION = "V4-R2"


def _policy_entry(source_type: SourceType) -> dict:
    policy = SourceContractCatalog.get(source_type)
    required: list[str] = []
    optional: list[str] = ["title", "contributor", "temporal_state", "metadata"]

    if policy.requires_code_traceability:
        required += ["reference (code locator)", "origin.kind (code repository/scanner)"]
    elif policy.requires_origin_traceability:
        required += ["content_or_reference"]
        optional += ["reference or origin.reference (at least one required for traceability)"]
    elif policy.requires_story_structure:
        required += ["content_or_reference"]
        optional += ["metadata.actor", "metadata.goal", "metadata.benefit "
                     "(structured form accepted only when free-form content is absent)"]
    elif policy.requires_decision_identity:
        required += ["content_or_reference",
                     "reference or metadata.decision_id",
                     "metadata.approver or origin.contributor or origin.reference"]
    elif policy.requires_model_traceability:
        required += ["content",
                     "origin.reference or metadata.model or metadata.process"]
    elif policy.requires_explicit_content:
        required += ["content (explicit explanation of what is unresolved)"]
    else:
        required += ["content_or_reference"]

    return {
        "source_type": source_type.value,
        "description": policy.description,
        "required": sorted(set(required)),
        "optional": sorted(set(optional)),
        "code_dependency": bool(policy.requires_code_traceability),
        "human_only_operation_supported": policy.human_only_supported,
        "traceability_requirement": {
            "code_traceable": policy.requires_code_traceability,
            "origin_traceable": policy.requires_origin_traceability,
            "story_structure": policy.requires_story_structure,
            "decision_identity": policy.requires_decision_identity,
            "model_traceable": policy.requires_model_traceability,
            "explicit_content": policy.requires_explicit_content,
        },
        "authority_semantics": {
            "authority_allowed": policy.authority_allowed,
            "authority_scope": policy.authority_scope,
        },
        "temporal_state_behavior": "optional_closed_enum_never_inferred",
        "validation_behavior": "deterministic_structural_validation_only; not approval; not truth",
        "sanitization_behavior": "content/reference/title/contributor/metadata sanitized via "
                                  "legacy_documenter.utils.sanitizer before validation",
    }


def build_source_contract_report() -> dict:
    """Builds the full deterministic contract-projection payload as a plain dict."""
    SourceContractCatalog.assert_complete()
    return {
        "schema_version": SCHEMA_VERSION,
        "module": "legacy_documenter.knowledge.input",
        "contract_kind": "INPUT_SOURCE_CONTRACT_PROJECTION",
        "note": "This artifact is a contract projection, not canonical Knowledge Source content. "
                "A valid input means LegacyMapper can safely and deterministically understand the "
                "material as its declared source type; it does not mean the material is true, "
                "approved, or belongs in canonical knowledge.",
        "source_types": [_policy_entry(st) for st in sorted(SourceType, key=lambda s: s.value)],
    }


def render_source_contract_report_json() -> str:
    """Renders the report as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return json.dumps(build_source_contract_report(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
