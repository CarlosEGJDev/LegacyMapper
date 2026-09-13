"""Deterministic contract-projection report for the V4-R12 Plugin-facing machine-readable output.

Follows the same established R7-R11 pattern: a plain-dict builder plus a canonical,
sorted-key, whitespace-free JSON renderer. This is R12's own contract projection describing
how R10 canonical knowledge is projected into the Plugin-facing machine-readable payload; it
is not itself canonical knowledge, not the R11 human-readable projection contract, and not a
Plugin runtime/agent/orchestration specification.
"""
from legacy_documenter.knowledge.domain.enums import KnowledgeNature, KnowledgeStatus, SourceType, TemporalState
from legacy_documenter.knowledge.plugin_projection.models import (
    CONTRACT_NAME,
    CONTRACT_VERSION,
    PROJECTION_KIND,
    SOURCE_KIND,
    UNSPECIFIED_TEMPORAL_STATE_LABEL,
)
from legacy_documenter.utils.json_rendering import render_deterministic_json

SCHEMA_VERSION = "V4-R12"


def build_plugin_contract() -> dict:
    """Builds the full deterministic R12 Plugin-facing machine-readable output contract payload."""
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_kind": "PLUGIN_FACING_MACHINE_READABLE_OUTPUT_CONTRACT",
        "module": "legacy_documenter.knowledge.plugin_projection",
        "contract_name": CONTRACT_NAME,
        "contract_version": CONTRACT_VERSION,
        "ONE_CANONICAL_KNOWLEDGE_SOURCE": "The R10 CanonicalKnowledgeCollection remains the single canonical "
                                          "knowledge source. This module never creates a second "
                                          "human_truth/document_truth/plugin_truth/functional_truth/"
                                          "technical_truth/AI_truth store.",
        "PLUGIN_PAYLOAD_IS_PROJECTION": True,
        "PLUGIN_PAYLOAD_IS_NOT_CANONICAL_KNOWLEDGE": True,
        "R12_SOURCE_IS_R10_CANONICAL_KNOWLEDGE": True,
        "R12_SOURCE_IS_NOT_R11_MARKDOWN": True,
        "CANONICAL_INPUT_READ_ONLY": True,
        "ALL_CANONICAL_ENTRIES_PROJECTED": True,
        "SILENT_ENTRY_OMISSION_FORBIDDEN": True,
        "PLUGIN_ENTRY_ID_IS_CANONICAL_KNOWLEDGE_ID": True,
        "APPROVAL_DOES_NOT_CHANGE_KNOWLEDGE_STATUS": True,
        "PROVENANCE_REMAINS_DISTINCT_FROM_APPROVAL": True,
        "SOURCE_CODE_IS_OPTIONAL": True,
        "PLUGIN_CONTRACT_IS_NOT_VBNET_SPECIFIC": True,
        "R12_DOES_NOT_USE_R11_MAPPING_RULES": True,
        "R12_DOES_NOT_IMPLEMENT_PLUGIN_RUNTIME": True,
        "AI_NEVER_DECIDES_PLUGIN_PROJECTION": True,
        "payload_model": "PluginKnowledgePayload(contract_name, contract_version, canonical_source, entries, "
                          "manifest) is a purely in-memory, read-only, frozen projection over already-approved "
                          "R10 canonical entries produced by PluginProjectionService.project(). It never stores a "
                          "mutated copy of an entry and never invents an entry. It is never named "
                          "truth/source_of_truth/plugin_truth.",
        "entry_model": "PluginKnowledgeEntry(knowledge_id, statement, source_type, nature, status, proposal_id, "
                        "approval_decision_id, temporal_state=None, evidence_refs=(), related_statement_ids=(), "
                        "provenance=None) is built only via from_canonical(), which copies every field verbatim "
                        "from the source CanonicalKnowledgeEntry. knowledge_id is always exactly the canonical "
                        "KNO- id; no second Plugin-specific identity is ever minted.",
        "manifest_model": "PluginKnowledgeManifest(canonical_entry_count, projected_entry_count, knowledge_ids, "
                           "status_counts, source_type_counts, nature_counts, temporal_state_counts) is derived "
                           "deterministically only from already-projected PluginKnowledgeEntry values. It is "
                           "projection metadata only, never canonical knowledge, and introduces no metric "
                           "requiring semantic interpretation.",
        "canonical_source_policy": "ONE_CANONICAL_KNOWLEDGE_SOURCE. PluginProjectionService.project reads "
                                    "CanonicalKnowledgeCollection.list() only; it never calls add()/compose() and "
                                    "never constructs a CanonicalKnowledgeEntry. The collection instance passed in "
                                    "is never mutated.",
        "projection_policy": f"canonical_source.source_kind is always the fixed constant '{SOURCE_KIND}' and "
                              f"canonical_source.projection_kind is always the fixed constant '{PROJECTION_KIND}'. "
                              "Neither value is ever derived from free text, current time, or environment state.",
        "canonical_mutation_policy": "NONE. This module never mutates a CanonicalKnowledgeEntry, an R8 Proposal, "
                                      "an R9 ApprovalDecision, or an R7 KnowledgeRelation, and never changes "
                                      "KnowledgeStatus/SourceType/KnowledgeNature/TemporalState. It never resolves "
                                      "a gap/conflict and never infers new knowledge.",
        "identity_policy": "PLUGIN_ENTRY_ID_IS_CANONICAL_KNOWLEDGE_ID. "
                            "machine_entry.knowledge_id == canonical_entry.knowledge_id always. No second "
                            "identity namespace exists anywhere in this package.",
        "completeness_policy": "ALL_CANONICAL_ENTRIES_PROJECTED. Every canonical entry in the input collection "
                                "must appear in the resulting payload; PluginProjectionService.project raises "
                                "PluginProjectionError('duplicate_canonical_knowledge_id:...' / "
                                "'entry_projection_failed:...' / 'silent_entry_omission_detected') rather than "
                                "silently omitting any entry.",
        "silent_omission_policy": "FORBIDDEN. See completeness_policy: a canonical entry that cannot be "
                                   "serialized under the Plugin contract fails the whole projection explicitly.",
        "source_code_policy": "OPTIONAL. No PluginKnowledgeEntry field requires a source file, repository path, "
                               "project path, symbol, method, language, framework, assembly, or database. Code is "
                               "one supported evidence/source_type value among several, never a precondition.",
        "technology_specificity_policy": "NOT_VBNET_SPECIFIC. Every field name and enum value in this contract is "
                                          "technology-neutral; the same contract serializes code-origin, "
                                          "human-information-only, and mixed-source canonical knowledge with no "
                                          "VB.NET-specific field.",
        "statement_policy": "VERBATIM. PluginKnowledgeEntry.statement is always the exact "
                             "CanonicalKnowledgeEntry.statement string, unparaphrased and unsummarized; it is "
                             "treated as untrusted display/data text and is never evaluated or executed, only "
                             "placed inside a JSON string value.",
        "status_policy": "PRESERVE. Every closed KnowledgeStatus value (CONFIRMED/INTERPRETED/PARTIAL/UNRESOLVED/"
                          "MISSING/CONFLICTING/SUPERSEDED) is preserved exactly. Approval never forces CONFIRMED: "
                          "an APPROVED canonical entry may legitimately carry any valid KnowledgeStatus, and this "
                          "module never rewrites it.",
        "temporal_policy": "PRESERVE. AS_IS/TO_BE/HISTORICAL/unspecified (None) are all preserved exactly. "
                            f"Unspecified is reported under the manifest label '{UNSPECIFIED_TEMPORAL_STATE_LABEL}' "
                            "- never silently treated as AS_IS. HISTORICAL is never auto-superseded; AS_IS is "
                            "never auto-conflicted with TO_BE; TO_BE is never auto-promoted to current.",
        "evidence_policy": "PRESERVE_REFERENCES. Every EvidenceRef is rendered structurally "
                            "(evidence_id/source_type/origin/locator/excerpt/authoritative) exactly as carried by "
                            "the canonical entry. No evidence is invented, dropped, expanded by inference, marked "
                            "authoritative differently, fetched externally, or resolved at projection time.",
        "provenance_policy": "PRESERVE_WHEN_PRESENT. Provenance is rendered structurally "
                              "(origin/material_ids/evidence_ids/contributor/notes) when the canonical entry "
                              "carries one, and stays exactly None/absent when it does not. Provenance, approval, "
                              "authority, status, and source_type remain distinct concepts: AI-originated material "
                              "later approved by the Technical Lead remains traceable as AI-originated via "
                              "provenance.origin while approval_decision_id records the separate human-approval "
                              "fact. Approval never rewrites provenance.",
        "relationship_policy": "PRESERVE_REFERENCES. related_statement_ids is preserved deterministically "
                                "(sorted) exactly as carried by the canonical entry. This module performs no "
                                "graph reasoning and infers no additional relationship.",
        "approval_traceability_policy": "PRESERVE. proposal_id and approval_decision_id are always present "
                                         "(required fields on CanonicalKnowledgeEntry) and are always projected "
                                         "verbatim. This module never creates a second Plugin approval state and "
                                         "never reinterprets the R9 approval decision.",
        "metadata_policy": "NOT_PROJECTED_BY_DEFAULT (CANONICAL_METADATA_DEFAULT=NOT_PROJECTED). Arbitrary R10 "
                            "canonical entry.metadata is never copied into the Plugin payload: only the "
                            "explicitly contracted fields listed in entry_model are projected. This avoids "
                            "turning arbitrary internal metadata into an unstable Plugin API and avoids any "
                            "conflict between exact-preservation and secret-safety for content this contract does "
                            "not commit to projecting at all. See docs/V4/"
                            "V4_R12_PLUGIN_FACING_MACHINE_READABLE_OUTPUT_CONTRACT_RESULT.md DESIGN_DECISIONS for "
                            "the full boundary discussion.",
        "serialization_policy": "DETERMINISTIC_JSON. UTF-8, sort_keys=True, fixed separators=(',', ':'), no "
                                 "timestamp, no UUID, no runtime object identity, no machine-specific path, no "
                                 "locale-dependent output. Repeated calls in the same process or a separate "
                                 "process produce byte-identical output for equal input.",
        "ordering_policy": "Entries are ordered by knowledge_id. evidence_refs are ordered by evidence_id. "
                            "related_statement_ids/material_ids/evidence_ids lists are sorted. Manifest count "
                            "dicts are rendered with sorted keys. No ordering is ever derived from insertion "
                            "timing, filesystem enumeration, or Python object identity.",
        "validation_policy": "STRICT_CONTRACT_VALIDATION via validator.validate_payload_dict: contract "
                              "name/version, canonical source/projection kind, entry identity (duplicate "
                              "knowledge_id rejected), required entry fields, closed enum membership, "
                              "canonical/projected count equality, manifest internal consistency, and required "
                              "traceability fields (proposal_id/approval_decision_id) are all checked explicitly. "
                              "Every validation failure raises PluginPayloadValidationError with a fixed, "
                              "non-echoing error code.",
        "compatibility_policy": f"For contract_version {CONTRACT_VERSION!r}: consumers may rely on every required "
                                 "field listed in entry_model/manifest_model. A future compatible revision may add "
                                 "new optional fields but must never silently alter the semantics of an existing "
                                 "required field. Removing, renaming, or reinterpreting a required field, or "
                                 "expanding a closed enum, requires an intentional contract_version bump. No "
                                 "migration framework is implemented in R12; this is a policy statement only.",
        "R11_independence": "R12 imports only legacy_documenter.knowledge.canonical and "
                             "legacy_documenter.knowledge.domain. It never imports "
                             "legacy_documenter.knowledge.projection (R11), never reads output/v4_r11/example_docs "
                             "Markdown, and never reuses R11's ProjectionRule/mapping configuration. Changing R11 "
                             "rendering/configuration can never change an R12 payload for identical R10 canonical "
                             "input.",
        "Plugin_boundary": "CONTRACT_ONLY_NO_RUNTIME. This package implements only the payload/contract: no "
                            "Plugin runtime, agent, orchestration engine, task planner, code generator, project "
                            "modifier, autonomous executor, model selector, provider router, prompt executor, or "
                            "external-system action exists anywhere in it.",
        "AI_policy": "Zero LLM/provider calls anywhere in this package; no provider SDK is imported. Every "
                     "projection decision (which fields to project, how to order them, how to count them) is a "
                     "fixed, explicit, deterministic rule; AI never decides Plugin projection.",
        "provider_policy": "REAL_LLM_CALLS=0. PROVIDER_CALLS=0. No Copilot/Gemini/OpenAI/Anthropic/Ollama or any "
                            "other provider is invoked anywhere in this package.",
        "security_policy": "entry.statement, evidence identifiers/locators/excerpts, provenance identifiers/"
                            "notes, and related_statement_ids are treated as untrusted display/data content only: "
                            "this module never eval()s, exec()s, dynamically imports, shell-executes, or "
                            "template-executes any of it, so prompt-injection-shaped and HTML/Markdown-shaped "
                            "canonical content always serializes as inert JSON string data. Arbitrary R10 "
                            "canonical metadata (the surface where an unvetted secret could most plausibly live) "
                            "is never projected into this payload at all (see metadata_policy), so no secret can "
                            "leak through it. Validation error codes in validator.py are fixed and non-echoing: "
                            "no exception message ever includes rejected statement/metadata/provenance content.",
        "closed_source_type_values": sorted(value.value for value in SourceType),
        "closed_knowledge_nature_values": sorted(value.value for value in KnowledgeNature),
        "closed_knowledge_status_values": sorted(value.value for value in KnowledgeStatus),
        "closed_temporal_state_values": sorted(value.value for value in TemporalState),
        "unspecified_temporal_state_label": UNSPECIFIED_TEMPORAL_STATE_LABEL,
    }


def render_plugin_contract_json() -> str:
    """Renders the report as canonical, deterministic JSON text (stable key order, no whitespace drift)."""
    return render_deterministic_json(build_plugin_contract())
