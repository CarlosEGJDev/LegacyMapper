"""V4 core domain records: MaterialItem, EvidenceRef and KnowledgeStatement.

These types are source-neutral and projection-neutral: none of them require a
filesystem path, a code symbol, a repository scan, a language, a framework, or
a specific document format (Markdown, the V3 levantamientos, or any future
Plugin output) merely to be instantiated. Code is one supported source among
several, never a precondition for valid knowledge.

Validation here is intentionally limited to structural and contractual
integrity (non-empty ids, closed enum membership, no duplicate references,
`CONFIRMED` requiring authoritative evidence). Classification, provenance
enrichment, gap/conflict detection, proposal lifecycle and Technical Lead
approval workflows belong to later V4 rounds and are not implemented here.
"""
from dataclasses import dataclass, field

from legacy_documenter.documentation.contracts import stable_id
from legacy_documenter.knowledge.domain.enums import (
    ApprovalStatus,
    KnowledgeNature,
    KnowledgeStatus,
    SourceType,
    TemporalState,
)


class DomainValidationError(ValueError):
    """Raised when a V4 domain record violates its structural contract."""


@dataclass
class Origin:
    """Identifies where a `MaterialItem` or `EvidenceRef` ultimately came from.

    `kind` is a short free-text discriminator (for example `CODE_REPOSITORY`,
    `HUMAN_INPUT`, `EXTERNAL_DOCUMENT`, `COPIED_TEXT`, `STRUCTURED_IMPORT`) so
    later rounds can add new origin kinds without a schema migration.
    `reference` is optional and may be a filesystem path, a URL, a document
    name, or any other locator; it is never required, because directly
    supplied human content has no locator beyond its own text.
    """

    kind: str
    reference: str | None = None
    contributor: str | None = None
    captured_at: str | None = None

    def validate(self) -> bool:
        """Rejects an origin with no discriminator; all other fields stay optional."""
        if not self.kind or not self.kind.strip():
            raise DomainValidationError("origin_kind_required")
        return True


@dataclass
class MaterialItem:
    """Represents material supplied to or discovered by LegacyMapper before approval.

    A `MaterialItem` may be code-derived, but it may equally be a paragraph of
    text a Technical Lead pasted in directly. `content` and `reference` are
    both optional individually; at least one of them must be present so the
    item carries something to evaluate. `temporal_state` (added in V4-R4) is
    optional and defaults to `None`, preserving every pre-existing call site;
    it exists because R4 ingestion may receive an explicitly supplied
    AS_IS/TO_BE/HISTORICAL declaration on the *material itself* (for example
    "this document describes the target/TO_BE process"), which has nowhere
    else in R1 to live without being hidden inside `metadata`.
    """

    material_id: str
    source_type: SourceType
    title: str | None = None
    content: str | None = None
    reference: str | None = None
    origin: Origin | None = None
    metadata: dict = field(default_factory=dict)
    temporal_state: TemporalState | None = None

    def validate(self) -> bool:
        """Performs the minimal structural check every `MaterialItem` must satisfy."""
        if not self.material_id or not self.material_id.strip():
            raise DomainValidationError("material_id_required")
        if not isinstance(self.source_type, SourceType):
            raise DomainValidationError("invalid_source_type")
        if self.content is None and self.reference is None:
            raise DomainValidationError("material_requires_content_or_reference")
        if self.temporal_state is not None and not isinstance(self.temporal_state, TemporalState):
            raise DomainValidationError("invalid_temporal_state")
        if self.origin is not None:
            self.origin.validate()
        return True


@dataclass
class EvidenceRef:
    """Represents traceable evidence supporting a knowledge statement.

    Unlike `legacy_documenter.models.evidence.Evidence`, which is scoped to
    code (`file`, `line`, `class_name`, `method`), an `EvidenceRef` may point
    to code-derived evidence, a requirement, a user story, a document, a
    standard, a decision, business information, Technical-Lead-supplied
    material, or unresolved source material. `locator` is a free-form,
    source-appropriate pointer (`file:line`, a document section id, a
    requirement id) rather than a code-specific field, so it stays meaningful
    across every V4 source type.
    """

    evidence_id: str
    source_type: SourceType
    origin: Origin | None = None
    locator: str | None = None
    excerpt: str | None = None
    authoritative: bool = False

    def validate(self) -> bool:
        """Performs the minimal structural check every `EvidenceRef` must satisfy."""
        if not self.evidence_id or not self.evidence_id.strip():
            raise DomainValidationError("evidence_id_required")
        if not isinstance(self.source_type, SourceType):
            raise DomainValidationError("invalid_source_type")
        if self.origin is not None:
            self.origin.validate()
        return True


@dataclass
class Provenance:
    """Records where a `KnowledgeStatement`'s supporting material came from.

    This is foundational structure for the future V4-R3 provenance round: it
    lets a statement point back to the `MaterialItem`s and `EvidenceRef`s that
    produced it, and to the contributor who supplied or authorized it, without
    implementing provenance resolution logic here.
    """

    origin: Origin
    material_ids: list[str] = field(default_factory=list)
    evidence_ids: list[str] = field(default_factory=list)
    contributor: str | None = None
    notes: str | None = None

    def validate(self) -> bool:
        """Validates the embedded origin; reference lists are otherwise unconstrained here."""
        self.origin.validate()
        return True


@dataclass
class ApprovalInfo:
    """Holds Technical Lead approval data without implementing the R9 approval workflow.

    `approval_status` defaults to `NOT_APPROVED`; nothing in this module
    transitions it automatically.
    """

    approval_status: ApprovalStatus = ApprovalStatus.NOT_APPROVED
    approver: str | None = None
    approved_at: str | None = None
    correction_notes: str | None = None

    def validate(self) -> bool:
        """Rejects an approval status outside the closed `ApprovalStatus` vocabulary."""
        if not isinstance(self.approval_status, ApprovalStatus):
            raise DomainValidationError("invalid_approval_status")
        return True


@dataclass
class KnowledgeStatement:
    """Represents one semantically meaningful, source-neutral knowledge statement.

    A statement always declares `source_type`, `nature` and `status` from
    their respective closed vocabularies. `temporal_state` is optional because
    not every statement carries an AS_IS/TO_BE distinction (a glossary entry,
    for instance, usually does not). `evidence_refs` may be empty only for
    non-`CONFIRMED` statuses: a `CONFIRMED` statement must be backed by at
    least one authoritative `EvidenceRef`, preserving the V3 rule that
    confirmed claims require authoritative evidence.
    """

    statement_id: str
    statement: str
    source_type: SourceType
    nature: KnowledgeNature
    status: KnowledgeStatus
    evidence_refs: list[EvidenceRef] = field(default_factory=list)
    provenance: Provenance | None = None
    temporal_state: TemporalState | None = None
    related_statement_ids: list[str] = field(default_factory=list)
    approval: ApprovalInfo = field(default_factory=ApprovalInfo)
    metadata: dict = field(default_factory=dict)

    def validate(self) -> bool:
        """Performs the full structural contract check for a `KnowledgeStatement`.

        Raises `DomainValidationError` on any violation instead of repairing
        or silently accepting an incomplete record.
        """
        if not self.statement_id or not self.statement_id.strip():
            raise DomainValidationError("statement_id_required")
        if not self.statement or not self.statement.strip():
            raise DomainValidationError("statement_text_required")
        if not isinstance(self.source_type, SourceType):
            raise DomainValidationError("invalid_source_type")
        if not isinstance(self.nature, KnowledgeNature):
            raise DomainValidationError("invalid_knowledge_nature")
        if not isinstance(self.status, KnowledgeStatus):
            raise DomainValidationError("invalid_knowledge_status")
        if self.temporal_state is not None and not isinstance(self.temporal_state, TemporalState):
            raise DomainValidationError("invalid_temporal_state")

        evidence_ids = [ref.evidence_id for ref in self.evidence_refs]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise DomainValidationError("duplicate_evidence_reference")
        for ref in self.evidence_refs:
            ref.validate()

        if self.status == KnowledgeStatus.CONFIRMED and not any(ref.authoritative for ref in self.evidence_refs):
            raise DomainValidationError("confirmed_statement_requires_authoritative_evidence")

        if self.provenance is not None:
            self.provenance.validate()
        self.approval.validate()
        return True


def new_statement_id(*parts: object) -> str:
    """Derives a stable `KST-` prefixed id from arbitrary content, reusing the V3 hashing contract."""
    return stable_id("KST", *parts)


def new_material_id(*parts: object) -> str:
    """Derives a stable `MAT-` prefixed id from arbitrary content, reusing the V3 hashing contract."""
    return stable_id("MAT", *parts)


def new_evidence_id(*parts: object) -> str:
    """Derives a stable `EVR-` prefixed id from arbitrary content, reusing the V3 hashing contract."""
    return stable_id("EVR", *parts)
