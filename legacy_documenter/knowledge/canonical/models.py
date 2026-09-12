"""Source-neutral `CanonicalKnowledgeEntry` domain model for V4-R10 canonical composition.

`CanonicalKnowledgeEntry` deliberately does not duplicate `KnowledgeStatement`
(R1). Instead it *reuses* `KnowledgeStatement.validate()` internally so R1's
already-approved structural and evidence invariants (in particular:
`CONFIRMED` requires at least one authoritative `EvidenceRef`) are enforced
identically here, never weakened or re-implemented, and never bypassed merely
because a Technical Lead approved the originating proposal.

`CanonicalKnowledgeEntry` adds exactly what R1's `KnowledgeStatement` does not
carry: explicit, permanent traceability to the R8 `proposal_id` and the R9
`approval_decision_id` that authorized its composition. Both fields are
required and are never erased, defaulted away, or overwritten.

This module performs no file, network, database, provider, or directory-scan
I/O. It operates only on already-available in-memory records.
"""
from dataclasses import dataclass, field

from legacy_documenter.documentation.contracts import stable_id
from legacy_documenter.knowledge.domain.enums import KnowledgeNature, KnowledgeStatus, SourceType, TemporalState
from legacy_documenter.knowledge.domain.models import DomainValidationError, EvidenceRef, KnowledgeStatement, Provenance


class CanonicalValidationError(ValueError):
    """Raised when a `CanonicalKnowledgeEntry` violates its structural contract.

    Deliberately structural only: never a semantic/truth judgment about
    whether the composed statement is correct, and never itself a source of
    Technical Lead authority.
    """


@dataclass(frozen=True)
class CanonicalKnowledgeEntry:
    """Represents one immutable, source-neutral entry in the Canonical Knowledge Source.

    `knowledge_id` is deterministic (see `new_knowledge_id`), derived only
    from immutable semantic content — never from current time, randomness, a
    UUID, or machine/object identity. `proposal_id` and `approval_decision_id`
    are required and permanent: composing a canonical entry never erases the
    fact that a specific R8 proposal and a specific R9 Technical Lead
    decision authorized it. `status` (a `KnowledgeStatus`) is orthogonal to
    the R9 approval decision that authorized composition — approval never
    replaces or upgrades it.
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
    provenance: Provenance | None = None
    related_statement_ids: tuple[str, ...] = ()
    metadata: dict = field(default_factory=dict)

    def validate(self) -> bool:
        """Performs the full structural contract check for a `CanonicalKnowledgeEntry`.

        Raises `CanonicalValidationError` on any violation instead of
        repairing or silently accepting an incomplete/invalid record. Reuses
        `KnowledgeStatement.validate()` (R1) for the shared structural and
        evidence-authority rules rather than re-implementing them.
        """
        if not self.knowledge_id or not self.knowledge_id.strip():
            raise CanonicalValidationError("knowledge_id_required")
        if not self.proposal_id or not self.proposal_id.strip():
            raise CanonicalValidationError("proposal_id_required")
        if not self.approval_decision_id or not self.approval_decision_id.strip():
            raise CanonicalValidationError("approval_decision_id_required")
        if len(self.related_statement_ids) != len(set(self.related_statement_ids)):
            raise CanonicalValidationError("duplicate_related_statement_id")

        # Reuse R1's own KnowledgeStatement structural/evidence invariants
        # (e.g. CONFIRMED requiring authoritative evidence) rather than
        # re-implementing them: Technical Lead approval must never weaken an
        # already-approved R1 rule.
        projection = KnowledgeStatement(
            statement_id=self.knowledge_id,
            statement=self.statement,
            source_type=self.source_type,
            nature=self.nature,
            status=self.status,
            evidence_refs=list(self.evidence_refs),
            provenance=self.provenance,
            temporal_state=self.temporal_state,
            related_statement_ids=list(self.related_statement_ids),
        )
        try:
            projection.validate()
        except DomainValidationError as exc:
            raise CanonicalValidationError(str(exc)) from exc
        return True


def canonicalize_ids(ids: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    """Canonicalizes an unordered id collection into a sorted, unique, deterministic tuple.

    Equivalent evidence/related-statement references supplied in different
    input order must never change canonical identity; this is the single
    place that guarantee is enforced for this module.
    """
    if not ids:
        return ()
    return tuple(sorted(set(ids)))


def new_knowledge_id(
    proposal_id: str,
    approval_decision_id: str,
    source_type: SourceType,
    nature: KnowledgeNature,
    status: KnowledgeStatus,
    temporal_state: TemporalState | None,
    evidence_ids: tuple[str, ...],
    related_statement_ids: tuple[str, ...],
) -> str:
    """Derives a stable `KNO-` id from immutable semantic composition content only.

    Reuses the existing V3/V4 `stable_id` hashing contract. Identity is tied
    to the exact `(proposal_id, approval_decision_id)` pair plus the explicit
    composition semantics (`source_type`, `nature`, `status`,
    `temporal_state`, canonical evidence/related-statement id sets):
    composing the *same* approved proposal with the *same* semantics twice
    yields the same `knowledge_id` (idempotent no-op); composing it again
    with *different* semantics yields a different `knowledge_id`, which the
    collection layer (`CanonicalKnowledgeCollection`) rejects as a
    conflicting duplicate for that `proposal_id`. Never depends on current
    time, randomness, a UUID, or machine/object identity.
    """
    return stable_id(
        "KNO",
        proposal_id,
        approval_decision_id,
        source_type.value,
        nature.value,
        status.value,
        temporal_state.value if temporal_state is not None else "",
        list(evidence_ids),
        list(related_statement_ids),
    )
