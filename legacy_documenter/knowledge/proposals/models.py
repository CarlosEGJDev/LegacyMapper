"""Source-neutral `Proposal` domain model for the V4-R8 pre-approval lifecycle.

A `Proposal` references material/relation/evidence ids only (no payload
duplication) and carries an explicit, caller-supplied `statement`. This
module never generates that statement from material/relation/classification/
temporal content, never mutates the records it references, and never
performs a Technical Lead approval or canonical-knowledge decision.

`Proposal` is frozen: a lifecycle transition (`transition_proposal`) returns a
new instance with the same `proposal_id` and the same immutable content,
never mutating the original in place. This mirrors the repository's existing
V4-R7 relation-layer convention of treating identity as separate from
lifecycle state.
"""
import dataclasses
from dataclasses import dataclass, field

from legacy_documenter.documentation.contracts import stable_id
from legacy_documenter.knowledge.proposals.enums import (
    VALID_TRANSITIONS,
    ProposalKind,
    ProposalMethod,
    ProposalStatus,
)


class ProposalValidationError(ValueError):
    """Raised when a `Proposal` violates its structural contract."""


class ProposalTransitionError(ValueError):
    """Raised when a requested lifecycle transition is not deterministically valid."""


@dataclass(frozen=True)
class Proposal:
    """Represents one explicit, source-neutral pre-approval proposal.

    `material_ids`/`relation_ids`/`evidence_refs` must already be canonical
    (sorted, unique) by the time a `Proposal` is constructed — see
    `canonicalize_refs`. At least one of the three must be non-empty: a
    proposal with no basis at all is rejected by `validate()`. `status`
    defaults to `DRAFT` and is intentionally excluded from `proposal_id`
    identity so lifecycle transitions never change identity.
    """

    proposal_id: str
    proposal_kind: ProposalKind
    statement: str
    proposal_method: ProposalMethod
    status: ProposalStatus = ProposalStatus.DRAFT
    material_ids: tuple[str, ...] = ()
    relation_ids: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    rationale: str | None = None
    proposed_by: str | None = None
    supersedes_proposal_id: str | None = None
    metadata: dict = field(default_factory=dict)

    def validate(self) -> bool:
        """Performs the full structural contract check for a `Proposal`.

        Deliberately structural only: never a semantic/truth judgment about
        whether the proposed statement is correct, good, or should be
        approved.
        """
        if not self.proposal_id or not self.proposal_id.strip():
            raise ProposalValidationError("proposal_id_required")
        if not isinstance(self.proposal_kind, ProposalKind):
            raise ProposalValidationError("invalid_proposal_kind")
        if not isinstance(self.status, ProposalStatus):
            raise ProposalValidationError("invalid_proposal_status")
        if not isinstance(self.proposal_method, ProposalMethod):
            raise ProposalValidationError("invalid_proposal_method")
        if not self.statement or not self.statement.strip():
            raise ProposalValidationError("statement_required")

        for ref_name, refs in (
            ("material_ids", self.material_ids),
            ("relation_ids", self.relation_ids),
            ("evidence_refs", self.evidence_refs),
        ):
            for ref in refs:
                if not ref or not ref.strip():
                    raise ProposalValidationError(f"empty_reference_in_{ref_name}")
            if len(refs) != len(set(refs)):
                raise ProposalValidationError(f"duplicate_reference_in_{ref_name}")

        if not (self.material_ids or self.relation_ids or self.evidence_refs):
            raise ProposalValidationError("proposal_requires_at_least_one_basis_reference")

        if self.supersedes_proposal_id is not None:
            if not self.supersedes_proposal_id.strip():
                raise ProposalValidationError("supersedes_proposal_id_blank")
            if self.supersedes_proposal_id == self.proposal_id:
                raise ProposalValidationError("self_supersession_rejected")

        return True


def canonicalize_refs(refs: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    """Canonicalizes an unordered reference collection into a sorted, unique, deterministic tuple.

    Equivalent proposal basis supplied in different input order must never
    change proposal identity; this is the single place that guarantee is
    enforced.
    """
    if not refs:
        return ()
    return tuple(sorted(set(refs)))


def new_proposal_id(
    proposal_kind: ProposalKind,
    statement: str,
    proposal_method: ProposalMethod,
    material_ids: tuple[str, ...],
    relation_ids: tuple[str, ...],
    evidence_refs: tuple[str, ...],
) -> str:
    """Derives a stable `PRP-` id from immutable semantic fields only.

    Reuses the existing V3/V4 `stable_id` hashing contract. Deliberately
    excludes `status`, `rationale`, `proposed_by`, `supersedes_proposal_id`,
    and `metadata` from identity: those are lifecycle/attribution data, not
    part of what makes two proposals the same semantic basis+statement+kind+
    method. Never depends on current time, randomness, or object identity.
    """
    return stable_id(
        "PRP",
        proposal_kind.value,
        statement,
        proposal_method.value,
        list(material_ids),
        list(relation_ids),
        list(evidence_refs),
    )


def transition_proposal(proposal: Proposal, new_status: ProposalStatus) -> Proposal:
    """Returns a new `Proposal` with `new_status`, preserving id and immutable content.

    Raises `ProposalTransitionError` for any transition not present in the
    closed `VALID_TRANSITIONS` map (for example `WITHDRAWN -> READY_FOR_REVIEW`
    or `SUPERSEDED -> READY_FOR_REVIEW`). Transitioning into
    `READY_FOR_REVIEW` additionally requires the proposal to be structurally
    reviewable (kind present, statement meaningful, method present, at least
    one basis reference) — a purely structural check, never a semantic/truth
    or approval decision.
    """
    if not isinstance(new_status, ProposalStatus):
        raise ProposalTransitionError("invalid_target_status")

    allowed = VALID_TRANSITIONS.get(proposal.status, frozenset())
    if new_status not in allowed:
        raise ProposalTransitionError(
            f"invalid_transition:{proposal.status.value}->{new_status.value}"
        )

    if new_status == ProposalStatus.READY_FOR_REVIEW:
        _validate_ready_for_review(proposal)

    return dataclasses.replace(proposal, status=new_status)


def _validate_ready_for_review(proposal: Proposal) -> None:
    """Performs the purely structural READY_FOR_REVIEW readiness check.

    Never a semantic truth validation, never an approval decision — only
    confirms the record is complete enough to hand to the Technical Lead.
    """
    if not isinstance(proposal.proposal_kind, ProposalKind):
        raise ProposalTransitionError("ready_for_review_requires_proposal_kind")
    if not proposal.statement or not proposal.statement.strip():
        raise ProposalTransitionError("ready_for_review_requires_meaningful_statement")
    if not isinstance(proposal.proposal_method, ProposalMethod):
        raise ProposalTransitionError("ready_for_review_requires_proposal_method")
    if not (proposal.material_ids or proposal.relation_ids or proposal.evidence_refs):
        raise ProposalTransitionError("ready_for_review_requires_at_least_one_basis_reference")
