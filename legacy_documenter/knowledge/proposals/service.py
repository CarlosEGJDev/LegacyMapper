"""Deterministic explicit-proposal-creation service and in-memory collection (V4-R8).

Pipeline: `ProposalRequest` (explicit caller input) -> `Proposal`, using only
caller-supplied fields. No material, relation, classification, temporal, or
provenance content is ever read to decide `proposal_kind` or `statement` —
those must already be present in the request. This module performs no file,
network, database, provider, or directory-scan I/O, and never calls an
LLM/provider even when `proposal_method=AI_PROPOSED`.
"""
from dataclasses import dataclass, field

from legacy_documenter.knowledge.proposals.enums import ProposalKind, ProposalMethod, ProposalStatus
from legacy_documenter.knowledge.proposals.models import (
    Proposal,
    ProposalTransitionError,
    ProposalValidationError,
    canonicalize_refs,
    new_proposal_id,
    transition_proposal,
)
from legacy_documenter.utils.sanitizer import sanitize_data, sanitize_text


class ProposalRejectedError(ValueError):
    """Raised when a requested proposal/operation cannot be accepted.

    In practice this happens for a structurally invalid request (missing
    statement, missing basis, unknown kind/method/status), a conflicting
    duplicate identity, an unknown proposal id, a self-supersession, or a
    detected supersession cycle. It never happens because of the proposal's
    textual statement/rationale content.
    """


@dataclass
class ProposalRequest:
    """Represents one explicit caller request to create a `Proposal`.

    `statement` must be supplied by the caller; it is never auto-generated
    from `material_ids`/`relation_ids`/`evidence_refs`. At least one of
    `material_ids`/`relation_ids`/`evidence_refs` is required as basis.
    """

    proposal_kind: ProposalKind
    statement: str
    proposal_method: ProposalMethod
    material_ids: tuple[str, ...] = ()
    relation_ids: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    rationale: str | None = None
    proposed_by: str | None = None
    supersedes_proposal_id: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class ProposalRejection:
    """Represents one rejected batch item: an invalid request or conflicting duplicate identity."""

    index: int
    reason: str


@dataclass
class ProposalBatchResult:
    """Represents the outcome of `create_proposal_batch`: accepted proposals and isolated rejections.

    `accepted` preserves original input order (with exact duplicates
    collapsed per the documented idempotent policy); `rejected` preserves the
    original index of each rejected item. No accepted item is ever dropped
    because another item in the same batch was rejected.
    """

    accepted: list[Proposal] = field(default_factory=list)
    rejected: list[ProposalRejection] = field(default_factory=list)


class ProposalService:
    """Deterministic boundary that creates a `Proposal` only from an explicit request.

    Stateless: every call is independent and produces the same output for the
    same request fields. Never inspects `SourceType`, `KnowledgeNature`,
    `TemporalState`, `KnowledgeStatus`, or `RelationKind` to decide a
    proposal's kind or statement, and never mutates any referenced record.
    Creation always starts at `ProposalStatus.DRAFT`; it never approves and
    never creates canonical knowledge.
    """

    def create_proposal(self, request: ProposalRequest) -> Proposal:
        """Creates one `Proposal` in `DRAFT` status from an explicit `ProposalRequest`.

        Raises `ProposalRejectedError` for an unknown kind/method, a missing
        or blank statement, or a request with no basis reference at all.
        """
        if not isinstance(request.proposal_kind, ProposalKind):
            raise ProposalRejectedError("invalid_proposal_kind")
        if not isinstance(request.proposal_method, ProposalMethod):
            raise ProposalRejectedError("invalid_proposal_method")
        if not request.statement or not request.statement.strip():
            raise ProposalRejectedError("statement_required")

        statement = sanitize_text(request.statement)
        material_ids = canonicalize_refs(request.material_ids)
        relation_ids = canonicalize_refs(request.relation_ids)
        evidence_refs = canonicalize_refs(request.evidence_refs)

        proposal = Proposal(
            proposal_id=new_proposal_id(
                request.proposal_kind, statement, request.proposal_method,
                material_ids, relation_ids, evidence_refs,
            ),
            proposal_kind=request.proposal_kind,
            statement=statement,
            proposal_method=request.proposal_method,
            status=ProposalStatus.DRAFT,
            material_ids=material_ids,
            relation_ids=relation_ids,
            evidence_refs=evidence_refs,
            rationale=sanitize_text(request.rationale) if request.rationale else None,
            proposed_by=sanitize_text(request.proposed_by) if request.proposed_by else None,
            supersedes_proposal_id=request.supersedes_proposal_id,
            metadata=sanitize_data(dict(request.metadata)),
        )
        try:
            proposal.validate()
        except ProposalValidationError as exc:
            raise ProposalRejectedError(str(exc)) from exc
        return proposal

    def create_proposal_batch(self, requests: list[ProposalRequest]) -> ProposalBatchResult:
        """Creates each proposal independently, isolating failures.

        Duplicate policy: a repeated identical proposal (same `proposal_id`
        and same full content) is an idempotent no-op (only the first is kept
        in `accepted`); a repeated `proposal_id` with *different* content
        (for example different `rationale`/`proposed_by`/`metadata`/
        `supersedes_proposal_id`) is rejected as a conflicting duplicate
        identity rather than silently overwritten.
        """
        result = ProposalBatchResult()
        seen: dict[str, Proposal] = {}
        for index, request in enumerate(requests):
            try:
                proposal = self.create_proposal(request)
            except ProposalRejectedError as exc:
                result.rejected.append(ProposalRejection(index=index, reason=str(exc)))
                continue

            existing = seen.get(proposal.proposal_id)
            if existing is not None:
                if existing != proposal:
                    result.rejected.append(ProposalRejection(
                        index=index, reason=f"conflicting_duplicate_proposal_id:{proposal.proposal_id}"))
                continue  # exact duplicate: idempotent no-op

            seen[proposal.proposal_id] = proposal
            result.accepted.append(proposal)
        return result


class ProposalCollection:
    """Deterministic in-memory proposal repository. No external storage is used.

    Preserves insertion order for `list()`/`by_status()`/`by_kind()`; `add()`
    enforces the same conflicting-duplicate-identity policy as
    `create_proposal_batch`. `transition()` and `supersede()` are the only
    ways a stored proposal's status changes; both replace the stored entry
    with a new frozen instance carrying the same `proposal_id`.
    """

    def __init__(self) -> None:
        self._proposals: dict[str, Proposal] = {}

    def add(self, proposal: Proposal) -> None:
        """Adds a validated proposal. Exact duplicates are idempotent; conflicting duplicates are rejected."""
        proposal.validate()
        existing = self._proposals.get(proposal.proposal_id)
        if existing is not None and existing != proposal:
            raise ProposalRejectedError(f"conflicting_duplicate_proposal_id:{proposal.proposal_id}")
        self._proposals[proposal.proposal_id] = proposal

    def get(self, proposal_id: str) -> Proposal | None:
        """Returns the proposal with `proposal_id`, or `None` if absent."""
        return self._proposals.get(proposal_id)

    def list(self) -> list[Proposal]:
        """Returns every stored proposal in insertion order."""
        return list(self._proposals.values())

    def by_status(self, status: ProposalStatus) -> list[Proposal]:
        """Returns every stored proposal with `status`, in insertion order."""
        return [proposal for proposal in self._proposals.values() if proposal.status == status]

    def by_kind(self, proposal_kind: ProposalKind) -> list[Proposal]:
        """Returns every stored proposal of `proposal_kind`, in insertion order."""
        return [proposal for proposal in self._proposals.values() if proposal.proposal_kind == proposal_kind]

    def proposals_for_material(self, material_id: str) -> list[Proposal]:
        """Returns every stored proposal whose `material_ids` includes `material_id`, in insertion order."""
        return [proposal for proposal in self._proposals.values() if material_id in proposal.material_ids]

    def proposals_for_relation(self, relation_id: str) -> list[Proposal]:
        """Returns every stored proposal whose `relation_ids` includes `relation_id`, in insertion order."""
        return [proposal for proposal in self._proposals.values() if relation_id in proposal.relation_ids]

    def transition(self, proposal_id: str, new_status: ProposalStatus) -> Proposal:
        """Applies a deterministic lifecycle transition to the stored proposal and returns the updated record.

        Raises `ProposalRejectedError` for an unknown `proposal_id`, or
        `ProposalTransitionError` for a transition outside the closed
        `VALID_TRANSITIONS` map.
        """
        proposal = self.get(proposal_id)
        if proposal is None:
            raise ProposalRejectedError("unknown_proposal_id")
        updated = transition_proposal(proposal, new_status)
        self._proposals[proposal_id] = updated
        return updated

    def supersede(self, proposal_id: str) -> Proposal:
        """Applies the supersession explicitly declared by `proposal.supersedes_proposal_id`.

        Reads `proposal_id`'s `supersedes_proposal_id` (set explicitly at
        creation) and transitions that target proposal to `SUPERSEDED`.
        Never infers supersession from dates, newer text, or shared
        material/relation. Rejects self-supersession, an undeclared
        supersession, an unknown target, and a simple two-proposal cycle
        (`A.supersedes_proposal_id == B` and `B.supersedes_proposal_id == A`).
        The superseded proposal is preserved (not deleted or mutated in
        place) and remains retrievable via `get()`.
        """
        proposal = self.get(proposal_id)
        if proposal is None:
            raise ProposalRejectedError("unknown_proposal_id")

        target_id = proposal.supersedes_proposal_id
        if not target_id:
            raise ProposalRejectedError("no_supersession_declared")
        if target_id == proposal_id:
            raise ProposalRejectedError("self_supersession_rejected")

        target = self.get(target_id)
        if target is None:
            raise ProposalRejectedError("unknown_superseded_proposal")
        if target.supersedes_proposal_id == proposal_id:
            raise ProposalRejectedError("supersession_cycle_detected")

        try:
            updated_target = transition_proposal(target, ProposalStatus.SUPERSEDED)
        except ProposalTransitionError as exc:
            raise ProposalRejectedError(str(exc)) from exc

        self._proposals[target_id] = updated_target
        return updated_target
