"""Deterministic canonical composition service and in-memory Canonical Knowledge Source (V4-R10).

Pipeline: `CanonicalCompositionRequest` (an explicit, read-only R8 `Proposal`
+ R9 `ApprovalDecision`, plus explicit composition semantics) ->
`CanonicalKnowledgeEntry`. No proposal/approval content, kind, method,
authority, relation kind, confidence, evidence count, or origin is ever read
to *infer* `source_type`/`nature`/`knowledge_status`/`temporal_state` — those
must already be present, explicitly, in the request. `statement` is never
re-derived from free text: it is taken verbatim from the already-sanitized,
already-approved `Proposal.statement`.

This module performs no file, network, database, provider, or directory-scan
I/O, and never calls an LLM/provider. It never mutates the `Proposal` or
`ApprovalDecision` it reads, never mutates any referenced
relation/material/classification/temporal/provenance record, and never
resolves an R7 `KnowledgeRelation` (CONFLICT/GAP/DIFFERENCE/
TEMPORAL_EVOLUTION remain historical, immutable evidence).
"""
from dataclasses import dataclass, field

from legacy_documenter.knowledge.approval.enums import ApprovalAuthority, ApprovalDecisionType
from legacy_documenter.knowledge.approval.models import ApprovalDecision
from legacy_documenter.knowledge.canonical.models import (
    CanonicalKnowledgeEntry,
    CanonicalValidationError,
    canonicalize_ids,
    new_knowledge_id,
)
from legacy_documenter.knowledge.domain.enums import KnowledgeNature, KnowledgeStatus, SourceType, TemporalState
from legacy_documenter.knowledge.domain.models import EvidenceRef, Provenance
from legacy_documenter.knowledge.proposals.enums import ProposalStatus
from legacy_documenter.knowledge.proposals.models import Proposal
from legacy_documenter.utils.sanitizer import sanitize_data

#: The only R8 proposal status a canonical composition may be attempted
#: against. Necessary but not sufficient: an APPROVED/TECHNICAL_LEAD decision
#: matching the same proposal_id is still required.
ELIGIBLE_PROPOSAL_STATUS = ProposalStatus.READY_FOR_REVIEW


class CanonicalCompositionRejectedError(ValueError):
    """Raised when a requested canonical composition cannot be accepted.

    In practice this happens for a structurally invalid request (missing
    proposal/approval decision, invalid `source_type`/`nature`/
    `knowledge_status`/`temporal_state`), a `Proposal` whose status is not
    `READY_FOR_REVIEW`, an `ApprovalDecision` for a different `proposal_id`,
    a decision that is not `APPROVED`, a decision whose authority is not
    `TECHNICAL_LEAD`, a violated R1 evidence/status invariant (e.g.
    `CONFIRMED` without authoritative evidence), or a conflicting duplicate
    composition attempt for a `proposal_id` that already has a differently
    composed canonical entry. It never happens because of the proposal's or
    decision's textual content.
    """


@dataclass
class CanonicalCompositionRequest:
    """Represents one explicit caller request to compose a `CanonicalKnowledgeEntry`.

    All semantic values (`source_type`, `nature`, `knowledge_status`,
    `temporal_state`, `evidence_refs`, `provenance`, `related_statement_ids`)
    must be supplied explicitly by the caller or already present in the
    referenced immutable `proposal`/`approval_decision` records. None of them
    is ever derived from free text or inferred by this module.
    """

    proposal: Proposal
    approval_decision: ApprovalDecision
    source_type: SourceType
    nature: KnowledgeNature
    knowledge_status: KnowledgeStatus
    temporal_state: TemporalState | None = None
    evidence_refs: tuple[EvidenceRef, ...] = ()
    provenance: Provenance | None = None
    related_statement_ids: tuple[str, ...] = ()
    metadata: dict = field(default_factory=dict)


class CanonicalCompositionService:
    """Deterministic boundary that composes a `CanonicalKnowledgeEntry` only from an explicit approved request.

    Stateless: every call is independent and produces the same output for
    the same request fields. Never inspects `ProposalMethod`, `ProposalKind`,
    `RelationKind`, or decision `rationale`/`correction_instructions` to
    decide eligibility or composed semantics, and never mutates the
    `Proposal`/`ApprovalDecision` it reads. `compose` only *constructs* a
    validated `CanonicalKnowledgeEntry`; storing it (and enforcing the
    duplicate/idempotency policy) is `CanonicalKnowledgeCollection`'s
    responsibility.
    """

    def compose(self, request: CanonicalCompositionRequest) -> CanonicalKnowledgeEntry:
        """Composes one `CanonicalKnowledgeEntry` from an explicit `CanonicalCompositionRequest`.

        Raises `CanonicalCompositionRejectedError` for every eligibility or
        structural violation described in the class/module docstrings. Never
        mutates `request.proposal` or `request.approval_decision`.
        """
        proposal = request.proposal
        decision = request.approval_decision

        if not isinstance(proposal, Proposal):
            raise CanonicalCompositionRejectedError("proposal_required")
        if not isinstance(decision, ApprovalDecision):
            raise CanonicalCompositionRejectedError("approval_decision_required")

        # Eligibility policy (R10 spec "Fundamental Rule" / "Eligibility Validation"):
        # composition is allowed only when all four conditions hold. No automatic
        # repair of a failed condition is ever attempted.
        if proposal.status != ELIGIBLE_PROPOSAL_STATUS:
            raise CanonicalCompositionRejectedError(
                f"proposal_not_ready_for_review:{proposal.status.value}"
            )
        if decision.proposal_id != proposal.proposal_id:
            raise CanonicalCompositionRejectedError("approval_decision_proposal_id_mismatch")
        if decision.decision != ApprovalDecisionType.APPROVED:
            raise CanonicalCompositionRejectedError(f"approval_not_approved:{decision.decision.value}")
        if decision.authority != ApprovalAuthority.TECHNICAL_LEAD:
            raise CanonicalCompositionRejectedError("approval_authority_not_technical_lead")

        if not isinstance(request.source_type, SourceType):
            raise CanonicalCompositionRejectedError("invalid_source_type")
        if not isinstance(request.nature, KnowledgeNature):
            raise CanonicalCompositionRejectedError("invalid_knowledge_nature")
        if not isinstance(request.knowledge_status, KnowledgeStatus):
            raise CanonicalCompositionRejectedError("invalid_knowledge_status")
        if request.temporal_state is not None and not isinstance(request.temporal_state, TemporalState):
            raise CanonicalCompositionRejectedError("invalid_temporal_state")

        evidence_refs = tuple(request.evidence_refs)
        evidence_ids = canonicalize_ids(tuple(ref.evidence_id for ref in evidence_refs))
        related_ids = canonicalize_ids(request.related_statement_ids)
        metadata = sanitize_data(dict(request.metadata)) if request.metadata else {}

        knowledge_id = new_knowledge_id(
            proposal.proposal_id,
            decision.decision_id,
            request.source_type,
            request.nature,
            request.knowledge_status,
            request.temporal_state,
            evidence_ids,
            related_ids,
        )

        entry = CanonicalKnowledgeEntry(
            knowledge_id=knowledge_id,
            statement=proposal.statement,
            source_type=request.source_type,
            nature=request.nature,
            status=request.knowledge_status,
            proposal_id=proposal.proposal_id,
            approval_decision_id=decision.decision_id,
            temporal_state=request.temporal_state,
            evidence_refs=evidence_refs,
            provenance=request.provenance,
            related_statement_ids=related_ids,
            metadata=metadata,
        )
        try:
            entry.validate()
        except CanonicalValidationError as exc:
            raise CanonicalCompositionRejectedError(str(exc)) from exc
        return entry


class CanonicalKnowledgeCollection:
    """Deterministic in-memory Canonical Knowledge Source. No external storage is used.

    This is the single logical canonical knowledge source for V4: no
    parallel `human_truth`/`plugin_truth`/`technical_truth`/`functional_truth`/
    `AI_truth` store exists anywhere in this module or package. R11 and R12
    are expected to project this same collection later; neither is
    implemented here.

    Entries are stored by `knowledge_id` and indexed by `proposal_id`.
    `compose()`/`add()` enforce: (1) exact recomposition of the same
    `proposal_id` with the same composition semantics is an idempotent
    no-op; (2) a conflicting composition attempt for a `proposal_id` that
    already has a canonical entry with *different* semantics is rejected,
    never silently overwritten — this also enforces the "one approved
    proposal, at most one canonical entry" rule (no automatic splitting).
    No entry is ever mutated, deleted, or physically overwritten in place.
    """

    def __init__(self) -> None:
        self._entries: dict[str, CanonicalKnowledgeEntry] = {}
        self._knowledge_id_by_proposal: dict[str, str] = {}

    def compose(
        self, service: CanonicalCompositionService, request: CanonicalCompositionRequest
    ) -> CanonicalKnowledgeEntry:
        """Composes `request` via `service`, then stores the result through `add()`."""
        entry = service.compose(request)
        return self.add(entry)

    def add(self, entry: CanonicalKnowledgeEntry) -> CanonicalKnowledgeEntry:
        """Adds a validated `CanonicalKnowledgeEntry`, enforcing the duplicate/idempotency policy.

        Raises `CanonicalCompositionRejectedError` when `entry.proposal_id`
        already has a stored canonical entry with a *different*
        `knowledge_id` (conflicting semantics), or when `entry.knowledge_id`
        is already stored with different content (defense in depth; in
        practice unreachable since `knowledge_id` is a deterministic hash of
        that same content).
        """
        entry.validate()

        existing_knowledge_id = self._knowledge_id_by_proposal.get(entry.proposal_id)
        if existing_knowledge_id is not None:
            if existing_knowledge_id == entry.knowledge_id:
                return self._entries[existing_knowledge_id]  # exact recomposition: idempotent no-op
            raise CanonicalCompositionRejectedError(
                f"conflicting_canonical_composition_for_proposal_id:{entry.proposal_id}"
            )

        existing_entry = self._entries.get(entry.knowledge_id)
        if existing_entry is not None and existing_entry != entry:
            raise CanonicalCompositionRejectedError(
                f"conflicting_duplicate_knowledge_id:{entry.knowledge_id}"
            )

        self._entries[entry.knowledge_id] = entry
        self._knowledge_id_by_proposal[entry.proposal_id] = entry.knowledge_id
        return entry

    def get(self, knowledge_id: str) -> CanonicalKnowledgeEntry | None:
        """Returns the canonical entry with `knowledge_id`, or `None` if absent."""
        return self._entries.get(knowledge_id)

    def list(self) -> list[CanonicalKnowledgeEntry]:
        """Returns every stored canonical entry, in insertion order."""
        return list(self._entries.values())

    def contains(self, knowledge_id: str) -> bool:
        """Reports whether `knowledge_id` is already stored."""
        return knowledge_id in self._entries

    def by_source_type(self, source_type: SourceType) -> list[CanonicalKnowledgeEntry]:
        """Returns every stored entry with `source_type`, in insertion order."""
        return [entry for entry in self._entries.values() if entry.source_type == source_type]

    def by_nature(self, nature: KnowledgeNature) -> list[CanonicalKnowledgeEntry]:
        """Returns every stored entry with `nature`, in insertion order."""
        return [entry for entry in self._entries.values() if entry.nature == nature]

    def by_status(self, status: KnowledgeStatus) -> list[CanonicalKnowledgeEntry]:
        """Returns every stored entry with `status`, in insertion order."""
        return [entry for entry in self._entries.values() if entry.status == status]

    def by_temporal_state(self, temporal_state: TemporalState) -> list[CanonicalKnowledgeEntry]:
        """Returns every stored entry with `temporal_state`, in insertion order."""
        return [entry for entry in self._entries.values() if entry.temporal_state == temporal_state]

    def by_proposal_id(self, proposal_id: str) -> CanonicalKnowledgeEntry | None:
        """Returns the canonical entry composed from `proposal_id`, or `None` if none exists.

        At most one canonical entry may ever exist per `proposal_id`
        (enforced by `add()`), so this is a single lookup rather than a list.
        """
        knowledge_id = self._knowledge_id_by_proposal.get(proposal_id)
        return self._entries.get(knowledge_id) if knowledge_id is not None else None


def is_eligible_for_canonical_composition(proposal: Proposal, approval_decision: ApprovalDecision | None) -> bool:
    """Reports whether `(proposal, approval_decision)` satisfies the R10 eligibility policy.

    Deterministic query only, mirroring R9's
    `is_eligible_for_canonical_composition` shape: it never composes,
    creates, or mutates a canonical entry, and never mutates its inputs.
    Returns `True` only when `proposal.status == READY_FOR_REVIEW` AND
    `approval_decision` is present AND `approval_decision.proposal_id ==
    proposal.proposal_id` AND `approval_decision.decision == APPROVED` AND
    `approval_decision.authority == TECHNICAL_LEAD`.
    """
    if not isinstance(proposal, Proposal):
        return False
    if proposal.status != ELIGIBLE_PROPOSAL_STATUS:
        return False
    if approval_decision is None or not isinstance(approval_decision, ApprovalDecision):
        return False
    if approval_decision.proposal_id != proposal.proposal_id:
        return False
    if approval_decision.decision != ApprovalDecisionType.APPROVED:
        return False
    return approval_decision.authority == ApprovalAuthority.TECHNICAL_LEAD
