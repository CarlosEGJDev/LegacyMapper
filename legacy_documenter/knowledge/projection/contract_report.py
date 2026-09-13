"""Deterministic contract-projection report for the V4-R11 human-readable document projection layer.

Follows the same established R7/R8/R9/R10 pattern: a plain-dict builder plus a canonical,
sorted-key, whitespace-free JSON renderer. This is R11's own contract projection describing
how canonical knowledge is projected into Markdown; it is not itself canonical knowledge and
not an R12 Plugin-facing payload.
"""
from legacy_documenter.knowledge.domain.enums import KnowledgeNature, KnowledgeStatus, SourceType, TemporalState
from legacy_documenter.knowledge.projection.markdown_renderer import EMPTY_DOCUMENT_MARKER
from legacy_documenter.knowledge.projection.rules import ALL_TARGETS, PROJECTION_CATEGORIES
from legacy_documenter.utils.json_rendering import render_deterministic_json

SCHEMA_VERSION = "V4-R11"


def build_projection_contract() -> dict:
    """Builds the full deterministic R11 human-readable-document-projection contract payload."""
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_kind": "HUMAN_READABLE_DOCUMENT_PROJECTION_CONTRACT",
        "module": "legacy_documenter.knowledge.projection",
        "ONE_CANONICAL_KNOWLEDGE_SOURCE": "The R10 CanonicalKnowledgeCollection remains the single canonical "
                                          "knowledge source. This module never creates a second "
                                          "human_truth/document_truth/functional_truth/technical_truth/"
                                          "markdown_truth store.",
        "MARKDOWN_IS_PROJECTION": True,
        "MARKDOWN_IS_NOT_CANONICAL_KNOWLEDGE": True,
        "CANONICAL_INPUT_READ_ONLY": True,
        "DOCUMENT_STRUCTURE_IS_PROJECTION_CONCERN": True,
        "DOCUMENT_STRUCTURE_IS_NOT_DOMAIN_MODEL": True,
        "NO_FREE_TEXT_SEMANTIC_MAPPING": True,
        "UNMAPPED_ENTRIES_ARE_PRESERVED": True,
        "MULTIPLE_DOCUMENT_PROJECTIONS_DO_NOT_DUPLICATE_CANONICAL_KNOWLEDGE": True,
        "EVERY_PROJECTED_ITEM_RETAINS_CANONICAL_KNOWLEDGE_ID": True,
        "EMPTY_DOCUMENTS_DO_NOT_INVENT_KNOWLEDGE": True,
        "R11_DOES_NOT_IMPLEMENT_PLUGIN_PAYLOAD": True,
        "AI_NEVER_DECIDES_DOCUMENT_MAPPING": True,
        "projection_model": "DocumentProjection(target: ProjectionTarget, entries: tuple[CanonicalKnowledgeEntry, "
                             "...]) is a purely in-memory, read-only view over already-approved canonical "
                             "entries. It never stores a mutated copy of an entry and never invents an entry.",
        "projection_rule_model": "ProjectionRule(rule_id, target, category=None, source_type=None, nature=None, "
                                  "status=None, temporal_state=None) declares an explicit AND of one or more "
                                  "structured conditions over already-approved CanonicalKnowledgeEntry fields "
                                  "only (source_type, nature, status, temporal_state, and the explicit closed "
                                  "metadata['projection_categories'] tag set). A rule with zero conditions is "
                                  "rejected at construction time. A rule never reads or evaluates entry.statement.",
        "target_model": "ProjectionTarget(document_path, family, title, purpose) is one closed, validated target "
                         "document. document_path is validated by validate_target_path against the fixed "
                         "ALLOWED_FAMILY_PREFIXES closed set (00-el-area/ through 09-capacitacion/); absolute "
                         "paths, drive-qualified paths, and '..' traversal segments are rejected. A target path "
                         "is never derived from untrusted free text.",
        "manifest_model": "ProjectionManifest reports canonical_entry_count, projected_canonical_entry_count, "
                           "unmapped_canonical_entry_count, document_count, non_empty_document_count, "
                           "empty_document_count, projection_occurrence_count, "
                           "knowledge_id_to_document_paths (knowledge_id -> sorted document path list), and "
                           "unmapped_knowledge_ids (sorted). It is projection metadata only, never canonical "
                           "knowledge.",
        "canonical_input_policy": "ProjectionService.project reads CanonicalKnowledgeCollection.list() only; it "
                                   "never calls add()/compose() and never constructs a CanonicalKnowledgeEntry. "
                                   "The collection instance passed in is never mutated.",
        "canonical_mutation_policy": "NONE. This module never mutates a CanonicalKnowledgeEntry, an R8 Proposal, "
                                      "an R9 ApprovalDecision, or an R7 KnowledgeRelation, and never changes "
                                      "KnowledgeStatus/SourceType/KnowledgeNature/TemporalState.",
        "document_structure_policy": "PROJECTION_ONLY. The 00-09 information architecture is one flat, closed "
                                      "tuple of ProjectionTarget values (rules.ALL_TARGETS); it is a "
                                      "projection/navigation concern, never the canonical domain model.",
        "document_structure_is_domain_model": False,
        "mapping_policy": "EXPLICIT_STRUCTURED_RULES_ONLY. Every ProjectionRule condition reads only "
                           "source_type/nature/status/temporal_state/metadata['projection_categories']. No rule "
                           "ever parses, tokenizes, or keyword-matches entry.statement text.",
        "free_text_inference_policy": "FORBIDDEN. No component in this package performs semantic inference over "
                                       "entry.statement to decide a document mapping.",
        "unmapped_policy": "PRESERVE_AND_REPORT. A canonical entry matched by zero rules becomes UNMAPPED: it is "
                            "never an error, never deleted, and never auto-classified. Its knowledge_id is "
                            "reported in ProjectionManifest.unmapped_knowledge_ids for later configuration/review.",
        "multi_projection_policy": "ALLOWED_WITH_SAME_CANONICAL_ID. One canonical entry matched by rules pointing "
                                    "at more than one target document is rendered, verbatim, in every one of "
                                    "those documents. Every occurrence retains the identical knowledge_id. This "
                                    "never creates a second canonical copy; R10's CanonicalKnowledgeCollection "
                                    "remains the single source.",
        "traceability_policy": "Every rendered non-empty item is followed by an HTML comment traceability marker "
                                "in the fixed format '<!-- knowledge_id: KNO-... -->', chosen because it is inert "
                                "in rendered Markdown/HTML previews, non-invasive to normal reading, and fully "
                                "deterministic.",
        "traceability_marker_format": "<!-- knowledge_id: {knowledge_id} -->",
        "canonical_id_visibility_policy": "The knowledge_id is always shown as a plain heading "
                                           "('### KNO-...') and repeated in the trailing traceability comment; no "
                                           "other internal canonical metadata (proposal_id, approval_decision_id, "
                                           "evidence_refs) is rendered into the human document.",
        "human_readability_policy": "Every non-empty document includes a title, a short fixed projection-metadata "
                                     "block (document_path/family/purpose/projection_kind/"
                                     "canonical_knowledge_source), and one section per canonical item with its "
                                     "nature/source_type/status and, when present, its temporal_state label. No "
                                     "AI-generated explanatory prose is ever added.",
        "canonical_statement_preservation_policy": "Every rendered statement is the exact "
                                                    "CanonicalKnowledgeEntry.statement string, unparaphrased and "
                                                    "unsummarized, rendered inside a Markdown blockquote as inert "
                                                    "display text.",
        "empty_document_policy": "GENERATE_EMPTY_DOCUMENT_WITH_EXPLICIT_NO_APPROVED_KNOWLEDGE_MARKER. A "
                                  f"configured target with zero matching entries is still rendered, with the "
                                  f"fixed marker text: \"{EMPTY_DOCUMENT_MARKER}\" This marker is projection "
                                  "metadata, never invented domain knowledge.",
        "ordering_policy": "Entries within one document are sorted by (temporal_state rank [AS_IS, TO_BE, "
                            "HISTORICAL, none], knowledge nature value, knowledge_id) — a fixed, explicit, "
                            "content-derived order. Never insertion timing, filesystem enumeration order, Python "
                            "object identity, current date/time, or locale-dependent sorting.",
        "deterministic_identity_policy": "Rendering never consults current time, randomness, a UUID, or "
                                          "machine/object identity. Identical canonical input and projection "
                                          "configuration always render byte-identical Markdown.",
        "file_io_boundary": "ProjectionService (service.py) and MarkdownRenderer (markdown_renderer.py) perform "
                             "zero file I/O; they operate purely in memory. Writing the synthetic example "
                             "Markdown tree to disk is isolated in disk_io.write_markdown_tree, which performs no "
                             "projection/mapping decisions of its own.",
        "R12_boundary": "R11 implements no Plugin payload, Plugin schema, Plugin consumer API, agent context "
                         "package, or machine-readable Plugin contract. R12 is expected to independently project "
                         "the same R10 CanonicalKnowledgeCollection; R12_SOURCE=CANONICAL_KNOWLEDGE_SOURCE, "
                         "R12_SOURCE!=R11_MARKDOWN — R12 must never consume this module's Markdown as its source.",
        "AI_policy": "Zero LLM/provider calls anywhere in this package; no provider SDK is imported. If a "
                      "canonical entry lacks sufficient structured mapping information the outcome is UNMAPPED, "
                      "never an AI-driven classification guess.",
        "provider_policy": "REAL_LLM_CALLS=0. PROVIDER_CALLS=0. No Copilot/Gemini/OpenAI/Anthropic/Ollama or any "
                            "other provider is invoked anywhere in this package.",
        "security_policy": "entry.statement and entry.metadata are treated as untrusted display data only: this "
                            "module never eval()s, exec()s, dynamically imports, shell-executes, or "
                            "template-executes any of it, so prompt-injection-shaped and HTML/Markdown-shaped "
                            "canonical content renders as inert display text. Target document paths are accepted "
                            "only from the closed, validated ProjectionTarget configuration "
                            "(validate_target_path rejects '../', absolute paths, and drive-qualified paths on "
                            "every path-accepting surface in this package). Exception messages use fixed, "
                            "non-echoing codes only and never include untrusted statement/metadata content, so no "
                            "secret can leak through an exception.",
        "path_safety_policy": "validate_target_path (models.py) is the single choke point for every path-accepting "
                               "surface in this package: it rejects empty/blank paths, absolute paths (leading "
                               "'/' or '\\\\'), drive-qualified paths (e.g. 'C:'), any '..' path-traversal "
                               "segment, and any path outside the fixed ALLOWED_FAMILY_PREFIXES closed set.",
        "governance_source_of_truth_note": "01-gobernanza/fuente-de-verdad.md is only a human-facing filename "
                                            "retained from the target information architecture. It does not "
                                            "redefine, replace, or compete with the R10 architectural concept "
                                            "'Canonical Knowledge Source', which remains exactly the R10 "
                                            "CanonicalKnowledgeCollection.",
        "catalog_vs_norm_policy": "CATALOG != NORM. A KnowledgeNature.CATALOG entry (current inventory / "
                                   "levantamiento) is projected only into 06-catalogo/catalogo.md; it is never "
                                   "automatically promoted into a 01-gobernanza or 03-desarrollo-de-software NORMA "
                                   "document.",
        "historical_vs_superseded_policy": "HISTORICAL != SUPERSEDED. TemporalState.HISTORICAL entries render "
                                            "with a plain 'Histórico (HISTORICAL)' label; this module never "
                                            "changes their KnowledgeStatus to SUPERSEDED and never marks a "
                                            "08-historial entry superseded merely because it appears in that "
                                            "family.",
        "agent_vs_capability_note": "Where canonical knowledge explicitly distinguishes AGENT from CAPABILITY "
                                     "concepts (04-arquitecturas-de-referencia), this module renders that "
                                     "distinction verbatim from the canonical statement/metadata; it never "
                                     "manufactures the distinction when canonical knowledge does not contain it.",
        "closed_target_document_count": len(ALL_TARGETS),
        "closed_target_document_paths": sorted(target.document_path for target in ALL_TARGETS),
        "closed_projection_categories": sorted(PROJECTION_CATEGORIES),
        "source_type_values": sorted(value.value for value in SourceType),
        "knowledge_nature_values": sorted(value.value for value in KnowledgeNature),
        "knowledge_status_values": sorted(value.value for value in KnowledgeStatus),
        "temporal_state_values": sorted(value.value for value in TemporalState),
    }


def render_projection_contract_json() -> str:
    """Renders the report as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return render_deterministic_json(build_projection_contract())
