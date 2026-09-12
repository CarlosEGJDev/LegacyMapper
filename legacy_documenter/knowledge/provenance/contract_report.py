"""Deterministic contract-projection report for the V4 provenance/lineage layer.

Projects the code-level provenance contract for human/tool consumption. Not
canonical Knowledge Source content and carries no approval semantics.
"""
import json

from legacy_documenter.knowledge.provenance.enums import (
    EdgeRelationship,
    LineageCompleteness,
    NodeKind,
    TransformationType,
)

SCHEMA_VERSION = "V4-R3"


def build_provenance_contract() -> dict:
    """Builds the full deterministic provenance contract-projection payload as a plain dict."""
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_kind": "PROVENANCE_CONTRACT_PROJECTION",
        "module": "legacy_documenter.knowledge.provenance",
        "note": "This artifact is a contract projection, not canonical Knowledge Source content. "
                "Provenance answers where material came from; it never answers whether it is true, "
                "approved, current, or canonical.",
        "node_kinds": sorted(k.value for k in NodeKind),
        "edge_relationships": sorted(r.value for r in EdgeRelationship),
        "transformation_types": sorted(t.value for t in TransformationType),
        "completeness_states": sorted(c.value for c in LineageCompleteness),
        "edge_direction": "EARLIER_SOURCE_TO_LATER_DERIVED",
        "identity_rules": {
            "node_id_prefix": "PRN-",
            "edge_id_prefix": "PED-",
            "hashing": "reuses legacy_documenter.documentation.contracts.stable_id (SHA-256 over canonical JSON parts)",
            "depends_on": ["node/edge semantic fields only"],
            "never_depends_on": ["current time", "random UUID", "memory address",
                                  "semantically irrelevant traversal order", "machine-specific paths"],
        },
        "cycle_policy": "REJECT_SELF_CYCLE_AND_TRANSITIVE_CYCLE_AT_ADD_EDGE_TIME",
        "dangling_reference_policy": "REJECT_EDGE_REFERENCING_UNKNOWN_FROM_OR_TO_NODE",
        "duplicate_policy": {
            "duplicate_node_same_content": "IDEMPOTENT_NO_OP",
            "duplicate_node_conflicting_content": "FAIL",
            "duplicate_edge_exact": "IDEMPOTENT_NO_OP",
            "duplicate_edge_conflicting_content": "FAIL",
        },
        "authority_distinction": "TRACEABLE != AUTHORITATIVE. Neither ProvenanceNode nor ProvenanceEdge "
                                  "carries an authority/authoritative field; roots are not privileged.",
        "approval_distinction": "TRACEABLE != APPROVED. Completeness (COMPLETE/PARTIAL/UNRESOLVED/INVALID) "
                                 "is a lineage-knowledge statement only, never a Technical Lead approval signal.",
        "ai_ancestry_semantics": "has_ai_ancestry(node_id) is true if the node itself or any transitive "
                                  "ancestor has source_type=AI_INTERPRETATION. AI ancestry does not "
                                  "invalidate knowledge; it must remain traceable through arbitrarily "
                                  "many derivation levels.",
        "r1_provenance_relationship": "legacy_documenter.knowledge.domain.models.Provenance is a compact, "
                                       "per-KnowledgeStatement provenance summary (origin + material_ids + "
                                       "evidence_ids + contributor + notes). ProvenanceGraph is the full "
                                       "deterministic multi-node/multi-edge lineage structure. Both are valid "
                                       "and may coexist: R1 Provenance is authoritative for a single "
                                       "statement's compact summary; ProvenanceGraph is authoritative for full "
                                       "graph traversal, ancestry, root discovery, and AI-ancestry queries.",
        "r2_input_relationship": "legacy_documenter.knowledge.provenance.graph.material_node_from_source_input "
                                  "represents a validated R2 SourceInput as a MATERIAL-kind ProvenanceNode, "
                                  "demonstrating SourceInput -> Material linkage without performing R4 ingestion.",
    }


def render_provenance_contract_json() -> str:
    """Renders the report as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return json.dumps(build_provenance_contract(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
