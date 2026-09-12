"""Pure in-memory V4-R12 projection service: canonical knowledge -> `PluginKnowledgePayload`.

`PluginProjectionService.project` performs zero file, network, database, provider, or
directory-scan I/O. It reads a `CanonicalKnowledgeCollection` (never mutating it) and returns
a purely in-memory `PluginKnowledgePayload`. No LLM/provider call occurs anywhere in this
module. This module never imports `legacy_documenter.knowledge.projection` (R11) and never
reads Markdown: its only input is the R10 `CanonicalKnowledgeCollection`.

Completeness policy: `ALL_CANONICAL_ENTRIES_PROJECTED`. Every canonical entry present in the
collection must appear in the resulting payload; if any entry cannot be projected under the
Plugin contract, projection fails explicitly (`PluginProjectionError`) rather than silently
omitting it.
"""
from legacy_documenter.knowledge.canonical.service import CanonicalKnowledgeCollection
from legacy_documenter.knowledge.plugin_projection.models import (
    CONTRACT_NAME,
    CONTRACT_VERSION,
    PluginCanonicalSourceDescriptor,
    PluginKnowledgeEntry,
    PluginKnowledgeManifest,
    PluginKnowledgePayload,
    PluginProjectionValidationError,
)


class PluginProjectionError(ValueError):
    """Raised when a canonical entry cannot be projected into the Plugin contract, or the
    resulting payload would silently omit a canonical entry.

    This is always an explicit failure: `SILENT_ENTRY_OMISSION` is forbidden by contract, so
    an entry that cannot be serialized never simply disappears from the payload.
    """


class PluginProjectionService:
    """Stateless, pure in-memory service that projects R10 canonical knowledge into a Plugin payload.

    Never mutates `CanonicalKnowledgeCollection`, any `CanonicalKnowledgeEntry`, any R8
    `Proposal`, or any R9 `ApprovalDecision`. Never changes
    `KnowledgeStatus`/`SourceType`/`KnowledgeNature`/`TemporalState`. Never reads R11's
    `legacy_documenter.knowledge.projection` package or any R11 Markdown output.
    """

    def project(self, collection: CanonicalKnowledgeCollection) -> PluginKnowledgePayload:
        """Projects every entry in `collection` into one deterministic `PluginKnowledgePayload`.

        Entries are ordered by `knowledge_id` (never insertion order, filesystem enumeration,
        or object identity). Raises `PluginProjectionError` if any canonical entry cannot be
        projected, or if the projected entry count would not equal the canonical entry count
        (silent omission is forbidden).
        """
        canonical_entries = sorted(collection.list(), key=lambda entry: entry.knowledge_id)
        canonical_entry_count = len(canonical_entries)

        seen_knowledge_ids: set[str] = set()
        projected_entries: list[PluginKnowledgeEntry] = []
        for entry in canonical_entries:
            if entry.knowledge_id in seen_knowledge_ids:
                # Defense in depth: CanonicalKnowledgeCollection already enforces knowledge_id
                # uniqueness, but the Plugin contract independently rejects duplicates too.
                raise PluginProjectionError(f"duplicate_canonical_knowledge_id:{entry.knowledge_id}")
            seen_knowledge_ids.add(entry.knowledge_id)
            try:
                plugin_entry = PluginKnowledgeEntry.from_canonical(entry)
                plugin_entry.validate()
            except PluginProjectionValidationError as exc:
                raise PluginProjectionError(f"entry_projection_failed:{entry.knowledge_id}") from exc
            projected_entries.append(plugin_entry)

        if len(projected_entries) != canonical_entry_count:
            # Unreachable under the loop above (every canonical entry either projects or
            # raises), kept as an explicit, fail-loud completeness guard per contract.
            raise PluginProjectionError("silent_entry_omission_detected")

        manifest = PluginKnowledgeManifest.build(tuple(projected_entries), canonical_entry_count)
        payload = PluginKnowledgePayload(
            contract_name=CONTRACT_NAME,
            contract_version=CONTRACT_VERSION,
            canonical_source=PluginCanonicalSourceDescriptor(),
            entries=tuple(projected_entries),
            manifest=manifest,
        )
        payload.validate()
        return payload
