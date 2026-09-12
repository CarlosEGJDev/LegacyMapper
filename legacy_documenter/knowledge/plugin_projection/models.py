"""In-memory Plugin-facing payload models for V4-R12.

`PluginKnowledgeEntry`/`PluginKnowledgeManifest`/`PluginCanonicalSourceDescriptor`/
`PluginKnowledgePayload` are projection-layer concepts only, exactly like R11's
`DocumentProjection`/`ProjectionManifest`. None of them is a canonical-domain
concept: they never appear in `legacy_documenter/knowledge/canonical/`, never
mutate a `CanonicalKnowledgeEntry`, and never redefine
`KnowledgeStatus`/`SourceType`/`KnowledgeNature`/`TemporalState`.

`PluginKnowledgeEntry.knowledge_id` is always exactly the source
`CanonicalKnowledgeEntry.knowledge_id` — no second Plugin-specific identity is
ever minted for a knowledge entry.

This module performs no file, network, database, provider, or directory-scan
I/O, and never calls an LLM/provider.
"""
from dataclasses import dataclass

from legacy_documenter.knowledge.canonical.models import CanonicalKnowledgeEntry
from legacy_documenter.knowledge.domain.enums import KnowledgeNature, KnowledgeStatus, SourceType, TemporalState
from legacy_documenter.knowledge.domain.models import EvidenceRef, Provenance

#: Explicit, closed contract identity constants. Never derived from the current date, a Git
#: hash, the repository test count, or any other runtime/environment state. A future
#: incompatible contract change requires an intentional bump of `CONTRACT_VERSION`.
CONTRACT_NAME = "LegacyMapperPluginKnowledge"
CONTRACT_VERSION = "1.0"

#: The canonical source this payload is a projection *of* (R10), never itself presented as a
#: second canonical/truth store.
SOURCE_KIND = "CANONICAL_KNOWLEDGE_SOURCE"

#: What kind of projection this payload is (a Plugin-facing machine-readable projection),
#: distinct from R11's human-readable Markdown projection.
PROJECTION_KIND = "PLUGIN_MACHINE_READABLE"

#: The label used for `temporal_state_counts`/manifest keys when a canonical entry carries no
#: temporal state. Deliberately distinct from any `TemporalState` enum value so it is never
#: confused with, or silently treated as, `AS_IS`.
UNSPECIFIED_TEMPORAL_STATE_LABEL = "UNSPECIFIED"


class PluginProjectionValidationError(ValueError):
    """Raised when a `PluginKnowledgeEntry`/`PluginKnowledgePayload` violates its structural contract.

    Deliberately structural only: never a semantic/truth judgment about the projected
    knowledge, and never itself an approval or rejection of it.
    """


@dataclass(frozen=True)
class PluginCanonicalSourceDescriptor:
    """Declares, structurally, that this payload's entries originate from the R10 Canonical Knowledge Source.

    Fixed values only (`SOURCE_KIND`/`PROJECTION_KIND`); never derived from free text and
    never named `truth`/`source_of_truth`/`plugin_truth`.
    """

    source_kind: str = SOURCE_KIND
    projection_kind: str = PROJECTION_KIND

    def validate(self) -> bool:
        """Rejects any descriptor whose kinds are not exactly the fixed closed values."""
        if self.source_kind != SOURCE_KIND:
            raise PluginProjectionValidationError("invalid_canonical_source_kind")
        if self.projection_kind != PROJECTION_KIND:
            raise PluginProjectionValidationError("invalid_projection_kind")
        return True


@dataclass(frozen=True)
class PluginKnowledgeEntry:
    """One Plugin-facing projection of exactly one R10 `CanonicalKnowledgeEntry`.

    Every field is copied verbatim from the source canonical entry: `statement` is never
    paraphrased, `status`/`temporal_state`/`source_type`/`nature` are never promoted or
    reinterpreted, `evidence_refs`/`related_statement_ids` are preserved exactly (never
    invented, dropped, or resolved), and `provenance` is preserved structurally when present
    and stays absent when absent. `knowledge_id` is always the canonical `KNO-` id — no second
    Plugin-specific identity is ever created for it.
    """

    knowledge_id: str
    statement: str
    source_type: SourceType
    nature: KnowledgeNature
    status: KnowledgeStatus
    proposal_id: str
    approval_decision_id: str
    temporal_state: TemporalState | None = None
    evidence_refs: tuple[EvidenceRef, ...] = ()
    related_statement_ids: tuple[str, ...] = ()
    provenance: Provenance | None = None

    @classmethod
    def from_canonical(cls, entry: CanonicalKnowledgeEntry) -> "PluginKnowledgeEntry":
        """Projects `entry` field-for-field. Never mutates `entry`; never mints a new identity."""
        return cls(
            knowledge_id=entry.knowledge_id,
            statement=entry.statement,
            source_type=entry.source_type,
            nature=entry.nature,
            status=entry.status,
            proposal_id=entry.proposal_id,
            approval_decision_id=entry.approval_decision_id,
            temporal_state=entry.temporal_state,
            evidence_refs=tuple(entry.evidence_refs),
            related_statement_ids=tuple(entry.related_statement_ids),
            provenance=entry.provenance,
        )

    def validate(self) -> bool:
        """Performs the minimal structural check every projected Plugin entry must satisfy.

        This never re-validates R1/R10 evidence-authority semantics (already enforced and
        already approved at composition time); it only checks that the fields required by the
        Plugin contract are present and well-typed.
        """
        if not self.knowledge_id or not self.knowledge_id.strip():
            raise PluginProjectionValidationError("knowledge_id_required")
        if not self.statement or not self.statement.strip():
            raise PluginProjectionValidationError("statement_required")
        if not isinstance(self.source_type, SourceType):
            raise PluginProjectionValidationError("invalid_source_type")
        if not isinstance(self.nature, KnowledgeNature):
            raise PluginProjectionValidationError("invalid_knowledge_nature")
        if not isinstance(self.status, KnowledgeStatus):
            raise PluginProjectionValidationError("invalid_knowledge_status")
        if self.temporal_state is not None and not isinstance(self.temporal_state, TemporalState):
            raise PluginProjectionValidationError("invalid_temporal_state")
        if not self.proposal_id or not self.proposal_id.strip():
            raise PluginProjectionValidationError("proposal_id_required")
        if not self.approval_decision_id or not self.approval_decision_id.strip():
            raise PluginProjectionValidationError("approval_decision_id_required")
        if len(self.related_statement_ids) != len(set(self.related_statement_ids)):
            raise PluginProjectionValidationError("duplicate_related_statement_id")
        evidence_ids = [ref.evidence_id for ref in self.evidence_refs]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise PluginProjectionValidationError("duplicate_evidence_reference")
        return True


@dataclass(frozen=True)
class PluginKnowledgeManifest:
    """Deterministic, projection-only report describing one Plugin payload's composition.

    This manifest is projection metadata; it is never itself canonical knowledge. Every count
    is derived purely from the already-projected `PluginKnowledgeEntry` values, never from
    filesystem enumeration, insertion timing, or object identity.
    """

    canonical_entry_count: int
    projected_entry_count: int
    knowledge_ids: tuple[str, ...]
    status_counts: dict
    source_type_counts: dict
    nature_counts: dict
    temporal_state_counts: dict

    @classmethod
    def build(cls, entries: tuple[PluginKnowledgeEntry, ...], canonical_entry_count: int) -> "PluginKnowledgeManifest":
        """Derives a manifest deterministically from already-projected `entries`."""
        status_counts: dict[str, int] = {}
        source_type_counts: dict[str, int] = {}
        nature_counts: dict[str, int] = {}
        temporal_state_counts: dict[str, int] = {}
        for entry in entries:
            status_counts[entry.status.value] = status_counts.get(entry.status.value, 0) + 1
            source_type_counts[entry.source_type.value] = source_type_counts.get(entry.source_type.value, 0) + 1
            nature_counts[entry.nature.value] = nature_counts.get(entry.nature.value, 0) + 1
            temporal_key = entry.temporal_state.value if entry.temporal_state is not None else UNSPECIFIED_TEMPORAL_STATE_LABEL
            temporal_state_counts[temporal_key] = temporal_state_counts.get(temporal_key, 0) + 1
        return cls(
            canonical_entry_count=canonical_entry_count,
            projected_entry_count=len(entries),
            knowledge_ids=tuple(sorted(entry.knowledge_id for entry in entries)),
            status_counts=status_counts,
            source_type_counts=source_type_counts,
            nature_counts=nature_counts,
            temporal_state_counts=temporal_state_counts,
        )


@dataclass(frozen=True)
class PluginKnowledgePayload:
    """The top-level deterministic Plugin-facing machine-readable envelope.

    Never named `truth`/`source_of_truth`/`plugin_truth`. `canonical_source` states, in a
    fixed structural form, that every entry originates from the R10 Canonical Knowledge
    Source. `entries` and `manifest` are pure projections; this dataclass never stores a
    mutated copy of canonical content.
    """

    contract_name: str
    contract_version: str
    canonical_source: PluginCanonicalSourceDescriptor
    entries: tuple[PluginKnowledgeEntry, ...]
    manifest: PluginKnowledgeManifest

    def validate(self) -> bool:
        """Performs the minimal structural check every payload must satisfy before serialization."""
        if self.contract_name != CONTRACT_NAME:
            raise PluginProjectionValidationError("invalid_contract_name")
        if self.contract_version != CONTRACT_VERSION:
            raise PluginProjectionValidationError("invalid_contract_version")
        self.canonical_source.validate()
        knowledge_ids = [entry.knowledge_id for entry in self.entries]
        if len(knowledge_ids) != len(set(knowledge_ids)):
            raise PluginProjectionValidationError("duplicate_knowledge_id")
        for entry in self.entries:
            entry.validate()
        if self.manifest.canonical_entry_count != self.manifest.projected_entry_count:
            raise PluginProjectionValidationError("canonical_projected_count_mismatch")
        if self.manifest.projected_entry_count != len(self.entries):
            raise PluginProjectionValidationError("manifest_entry_count_mismatch")
        return True
