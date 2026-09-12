"""Explicit deterministic validation for a serialized V4-R12 Plugin payload dict.

Validates the *serialized* (plain-dict) form produced by `serializer.payload_to_dict`, so it
can validate a payload built in-process or one deserialized from a JSON artifact/file/wire
message with no additional trust assumptions. Every error is a fixed, non-echoing code: no
exception message here ever includes untrusted `statement`/`metadata`/`provenance` content, so
no secret embedded in canonical content can leak through a validation error.

Uses only the standard library and this repository's own closed enums — no new schema-
validation dependency is introduced, consistent with the rest of the repository.
"""
from legacy_documenter.knowledge.domain.enums import KnowledgeNature, KnowledgeStatus, SourceType, TemporalState
from legacy_documenter.knowledge.plugin_projection.models import (
    CONTRACT_NAME,
    CONTRACT_VERSION,
    PROJECTION_KIND,
    SOURCE_KIND,
    UNSPECIFIED_TEMPORAL_STATE_LABEL,
)

REQUIRED_ENTRY_FIELDS: tuple[str, ...] = (
    "knowledge_id",
    "statement",
    "source_type",
    "nature",
    "status",
    "temporal_state",
    "evidence_refs",
    "related_statement_ids",
    "proposal_id",
    "approval_decision_id",
    "provenance",
)

_VALID_SOURCE_TYPES = {member.value for member in SourceType}
_VALID_NATURES = {member.value for member in KnowledgeNature}
_VALID_STATUSES = {member.value for member in KnowledgeStatus}
_VALID_TEMPORAL_STATES = {member.value for member in TemporalState}
_MANIFEST_COUNT_FIELDS: tuple[tuple[str, set], ...] = (
    ("status_counts", _VALID_STATUSES),
    ("source_type_counts", _VALID_SOURCE_TYPES),
    ("nature_counts", _VALID_NATURES),
)


class PluginPayloadValidationError(ValueError):
    """Raised when a serialized Plugin payload dict violates the V4-R12 contract.

    Always a fixed, non-echoing error code — never the rejected untrusted content itself.
    """


def validate_payload_dict(data: dict) -> bool:
    """Validates a serialized Plugin payload dict against the full V4-R12 contract.

    Raises `PluginPayloadValidationError` on the first violation found instead of repairing or
    silently accepting an incomplete/invalid payload. Returns `True` when every check passes.
    """
    if not isinstance(data, dict):
        raise PluginPayloadValidationError("invalid_payload_shape")

    if data.get("contract_name") != CONTRACT_NAME:
        raise PluginPayloadValidationError("invalid_contract_name")
    if data.get("contract_version") != CONTRACT_VERSION:
        raise PluginPayloadValidationError("invalid_contract_version")

    canonical_source = data.get("canonical_source")
    if not isinstance(canonical_source, dict):
        raise PluginPayloadValidationError("invalid_canonical_source_shape")
    if canonical_source.get("source_kind") != SOURCE_KIND:
        raise PluginPayloadValidationError("invalid_canonical_source_kind")
    if canonical_source.get("projection_kind") != PROJECTION_KIND:
        raise PluginPayloadValidationError("invalid_projection_kind")

    entries = data.get("entries")
    if not isinstance(entries, list):
        raise PluginPayloadValidationError("invalid_entries_shape")

    seen_knowledge_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise PluginPayloadValidationError("invalid_entry_shape")
        for field_name in REQUIRED_ENTRY_FIELDS:
            if field_name not in entry:
                raise PluginPayloadValidationError("missing_required_entry_field")

        knowledge_id = entry["knowledge_id"]
        if not isinstance(knowledge_id, str) or not knowledge_id.strip():
            raise PluginPayloadValidationError("invalid_knowledge_id")
        if knowledge_id in seen_knowledge_ids:
            raise PluginPayloadValidationError("duplicate_knowledge_id")
        seen_knowledge_ids.add(knowledge_id)

        if not isinstance(entry["statement"], str) or not entry["statement"].strip():
            raise PluginPayloadValidationError("invalid_statement")
        if entry["source_type"] not in _VALID_SOURCE_TYPES:
            raise PluginPayloadValidationError("invalid_source_type_enum")
        if entry["nature"] not in _VALID_NATURES:
            raise PluginPayloadValidationError("invalid_nature_enum")
        if entry["status"] not in _VALID_STATUSES:
            raise PluginPayloadValidationError("invalid_status_enum")
        temporal_state = entry["temporal_state"]
        if temporal_state is not None and temporal_state not in _VALID_TEMPORAL_STATES:
            raise PluginPayloadValidationError("invalid_temporal_state_enum")

        if not isinstance(entry["proposal_id"], str) or not entry["proposal_id"].strip():
            raise PluginPayloadValidationError("missing_proposal_id_traceability")
        if not isinstance(entry["approval_decision_id"], str) or not entry["approval_decision_id"].strip():
            raise PluginPayloadValidationError("missing_approval_decision_id_traceability")

        evidence_refs = entry["evidence_refs"]
        if not isinstance(evidence_refs, list):
            raise PluginPayloadValidationError("invalid_evidence_refs_shape")
        evidence_ids = [ref.get("evidence_id") if isinstance(ref, dict) else None for ref in evidence_refs]
        if any(eid is None for eid in evidence_ids) or len(evidence_ids) != len(set(evidence_ids)):
            raise PluginPayloadValidationError("invalid_or_duplicate_evidence_reference")

        related_ids = entry["related_statement_ids"]
        if not isinstance(related_ids, list) or len(related_ids) != len(set(related_ids)):
            raise PluginPayloadValidationError("invalid_or_duplicate_related_statement_id")

    manifest = data.get("manifest")
    if not isinstance(manifest, dict):
        raise PluginPayloadValidationError("invalid_manifest_shape")
    if manifest.get("canonical_entry_count") != len(entries):
        raise PluginPayloadValidationError("manifest_canonical_entry_count_mismatch")
    if manifest.get("projected_entry_count") != len(entries):
        raise PluginPayloadValidationError("manifest_projected_entry_count_mismatch")
    if sorted(manifest.get("knowledge_ids") or []) != sorted(seen_knowledge_ids):
        raise PluginPayloadValidationError("manifest_knowledge_ids_mismatch")

    for count_field, valid_values in _MANIFEST_COUNT_FIELDS:
        counts = manifest.get(count_field)
        if not isinstance(counts, dict):
            raise PluginPayloadValidationError("invalid_manifest_counts_shape")
        if not set(counts.keys()) <= valid_values:
            raise PluginPayloadValidationError("manifest_counts_invalid_enum_key")
        if sum(counts.values()) != len(entries):
            raise PluginPayloadValidationError("manifest_counts_total_mismatch")

    temporal_counts = manifest.get("temporal_state_counts")
    if not isinstance(temporal_counts, dict):
        raise PluginPayloadValidationError("invalid_manifest_counts_shape")
    if not set(temporal_counts.keys()) <= (_VALID_TEMPORAL_STATES | {UNSPECIFIED_TEMPORAL_STATE_LABEL}):
        raise PluginPayloadValidationError("manifest_counts_invalid_enum_key")
    if sum(temporal_counts.values()) != len(entries):
        raise PluginPayloadValidationError("manifest_counts_total_mismatch")

    return True
