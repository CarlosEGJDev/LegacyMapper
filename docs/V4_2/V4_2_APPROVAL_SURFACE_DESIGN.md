# LegacyMapper V4.2 — Approval Surface Design

IMPLEMENTATION_STATUS=NOT_IMPLEMENTED

This is a design artifact only (V4.2-R6 section 13/14). It defines the
human approval surface a future round (R7 or later, explicitly out of R6's
scope) would build on top of R4/R5/R6's existing proposal pipeline. No
`approve` command, no persistence format, and no CLI wiring exists yet.
Nothing in this document authorizes implementing it.

---

## 1. What already exists (grounding, not new design)

Three domain packages already implement the *pieces* this surface would
compose, in complete isolation from the CLI:

- **`legacy_documenter.knowledge.proposals`** — `Proposal` (frozen
  dataclass: `proposal_id, proposal_kind, statement, proposal_method,
  status, material_ids, relation_ids, evidence_refs, rationale,
  proposed_by, supersedes_proposal_id, metadata`), `ProposalStatus`
  (`DRAFT, READY_FOR_REVIEW, WITHDRAWN, SUPERSEDED` — no `APPROVED`/
  `REJECTED` value exists here at all), and `transition_proposal`'s fixed
  transition map. Every AI-generated proposal `full --allow-ai-
  interpretation` writes to `proposals/AI_PROPOSALS.json` is already
  `READY_FOR_REVIEW` (`orchestration.proposal_adapter`).
- **`legacy_documenter.knowledge.approval`** — `ApprovalDecision` (frozen:
  `decision_id, proposal_id, decision, authority, decided_by, rationale,
  correction_instructions, previous_decision_id, metadata`),
  `ApprovalDecisionType` (`APPROVED, REJECTED, CORRECTION_REQUESTED`),
  `ApprovalAuthority` (closed to the single value `TECHNICAL_LEAD`), and
  `ApprovalService.record_decision(request, proposal)`, which only accepts
  a decision against a `Proposal` whose `status == READY_FOR_REVIEW`.
  `ApprovalCollection` enforces "at most one decision per `proposal_id`,
  ever" in memory.
- **`legacy_documenter.knowledge.canonical`** — `CanonicalCompositionService
  .compose(...)` builds an immutable `CanonicalKnowledgeEntry` from a
  `Proposal` + a matching `APPROVED` `ApprovalDecision` (same
  `proposal_id`) plus explicit caller-supplied provenance fields.

**Crucially: approving a proposal never changes `Proposal.status`.**
`APPROVED`/`REJECTED` are not `ProposalStatus` values — they exist only as
the `decision` field of a separate `ApprovalDecision` record that
*references* `proposal_id`. A proposal stays `READY_FOR_REVIEW` forever
(or moves to `WITHDRAWN`/`SUPERSEDED` via unrelated lifecycle actions) even
after it is approved. This is a deliberate existing separation this design
preserves, not something R7+ needs to change: **approval provenance
(who decided, when, why) is structurally distinct from source provenance
(where the proposal's evidence came from)** — exactly section 13's
"approval provenance remains separate from source provenance" requirement,
already satisfied by the existing model.

All three packages are fully unit-tested in isolation but **completely
unreachable from `python main.py full`** today: nothing under `cli/` or
`orchestration/` imports `knowledge.approval` or `knowledge.canonical`, and
none of the three packages persists anything to disk. This design is about
building the missing surface between them and a human, not about changing
any of their existing contracts.

---

## 2. What the Technical Lead must review

For each proposal in `proposals/AI_PROPOSALS.json`/`.md`, the review
surface must show, at minimum:

| Field | Source (already exists) |
|---|---|
| Proposal identity | `proposal.proposal_id` (deterministic hash, never AI free text) |
| Statement | `proposal.statement` (the AI's claim, verbatim) |
| Proposal kind / method | `proposal.proposal_kind` / `proposal.proposal_method` (always `INTERPRETATION` / `AI_PROPOSED` for this pipeline today) |
| Evidence references | `proposal.evidence_refs` — must resolve to real records the *same run's* `ai_context/*.json` actually contains (already enforced by `_validate_findings` before a proposal is ever created) |
| AI interpretation context | `ai_interpretation_status`, `provider_id`, `model_id`, `context_package_id` from the `AI_PROPOSALS.json` envelope |
| Current proposal status | `proposal.status` (today always `READY_FOR_REVIEW` for this pipeline) |
| Run identity | which `full` run produced it (see section 6 — not yet tracked explicitly; a gap this design flags) |

The review surface must **never** show a proposal as already decided, and
must never let the Technical Lead review a `WITHDRAWN`/`SUPERSEDED`
proposal as if it were still pending (`ApprovalService` already enforces
the `READY_FOR_REVIEW`-only precondition; a future CLI surface must read
proposal status before offering a decision, not merely trust the file).

## 3. Possible future decisions

Exactly the three `ApprovalDecisionType` values already defined — no new
value should be invented:

- **APPROVED** — the proposal, as stated, is accepted.
- **REJECTED** — the proposal is rejected outright; it must never be
  eligible for canonical promotion afterward.
- **CORRECTION_REQUESTED** — the proposal's substance is on the right
  track but needs a human-authored correction before it could be
  approved; `ApprovalDecision.correction_instructions` already exists to
  carry that.

A future round must **not** add an "auto-approve"/"bulk-approve" action,
per section 13's "AI cannot approve" and "Technical Lead = sole final
approval authority" — every `ApprovalDecision.authority` is (and must
remain) `ApprovalAuthority.TECHNICAL_LEAD`, `decided_by` a specific human
identity, never a service account or "system."

## 4. How a decision binds to an exact proposal

`ApprovalDecision.decision_id` is already a deterministic hash over
`(proposal_id, decision, authority, decided_by, rationale, ...)` — the
binding is by `proposal_id`, the same deterministic hash already computed
from the proposal's own kind/statement/method/evidence at creation time
(`stable_id("PRP", ...)`, `knowledge/proposals/models.py`). A future
persistence format must record decisions **keyed by `proposal_id`**, never
by array position or filename — `ApprovalCollection`'s existing "one
decision per `proposal_id`, ever" invariant should carry over unchanged
into whatever persists it to disk.

## 5. Corrected/rejected proposals

- **REJECTED**: the `ApprovalDecision` alone is sufficient; the `Proposal`
  itself is never mutated (no code path deletes or edits a `Proposal`
  today, and this design does not introduce one). A rejected proposal
  must never appear in a future "pending review" listing again, and must
  never be eligible for `CanonicalCompositionService.compose(...)`.
- **CORRECTION_REQUESTED**: this is **not** an edit-in-place. The existing
  `Proposal.supersedes_proposal_id` field already models "a new proposal
  that replaces an old one" — a future round should have the *next* AI run
  (or a human-authored proposal, `ProposalMethod.HUMAN_PROPOSED`) create a
  **new** `Proposal` carrying `supersedes_proposal_id` pointing at the
  corrected one, and transition the old one to `SUPERSEDED`
  (`transition_proposal` already permits `READY_FOR_REVIEW -> SUPERSEDED`).
  The original AI statement and the original `ApprovalDecision` both
  remain on record, immutable — corrections are additive history, never a
  silent rewrite.

## 6. Distinguishing stale proposals from a previous run

**This is the one real gap this design must flag rather than paper over.**
V4.2-R6 (production code, not this design) fixed the *console/summary*
side of staleness: a rerun that does not itself produce proposals now
removes the previous run's `proposals/` files
(`legacy_documenter.cli.artifact_lifecycle.reset_stale_proposal_artifacts`)
and `RUN_SUMMARY`'s own fields never describe a different run's proposals
as current. But **neither `Proposal` nor `AI_PROPOSALS.json`'s envelope
currently carries a run identifier at all** — nothing in the existing
domain model timestamps or run-scopes a proposal.

A future approval surface therefore needs one additive field before it can
safely let a Technical Lead act on a specific run's proposals with
confidence — for example, a deterministic `run_id` (not a wall-clock
timestamp; consistent with this codebase's "no UUID/timestamp in
versioned artifacts" convention — e.g. a hash of the run's own
`context_package_id` plus repository root) stamped onto both
`AI_PROPOSALS.json`'s envelope and, ideally, into `Proposal.metadata`
(already an open `dict`, so this would be additive, not a schema break).
An approval CLI would then refuse to record a decision against a proposal
whose `run_id` does not match the `AI_PROPOSALS.json` currently on disk
under the selected `--output`, closing the risk of a Technical Lead
approving a proposal from a run that has since been superseded by a
rerun. **This round does not implement that field** — it is named here as
the specific prerequisite the next round touching approval must add first.

## 7. Data required before canonical promotion

`CanonicalCompositionService.compose(...)` already requires, structurally:

- a `Proposal` with `status == READY_FOR_REVIEW`;
- a matching `ApprovalDecision` with `decision == APPROVED`,
  `authority == ApprovalAuthority.TECHNICAL_LEAD`, and the same
  `proposal_id`;
- explicit caller-supplied `source_type`/`nature`/`knowledge_status`/etc.
  (never inferred/defaulted).

A future approval surface must supply all of the above **and** the
run-scoping data from section 6, so canonical promotion can never target a
proposal whose originating run is ambiguous or stale. No automatic
trigger should ever call `compose(...)` — it must remain reachable only
through an explicit human action recorded as its own auditable step,
separate from the approval decision itself (approval and promotion are
two distinct human-authorized actions in the existing domain model, and
this design preserves that separation rather than collapsing them).

## 8. Explicit non-goals (preserved from section 13)

- **Technical Lead = sole final approval authority.** `ApprovalAuthority`
  stays closed to `TECHNICAL_LEAD`; no future round should widen it to a
  service account, a different role, or an automated policy.
- **AI cannot approve.** No code path may ever construct an
  `ApprovalDecision` from AI/provider output; every decision's
  `decided_by` must be a real human identity supplied through an explicit,
  interactive (or at minimum explicitly human-invoked) action.
- **Approval provenance stays separate from source provenance** — already
  true structurally (section 1) and preserved by this design's every
  recommendation.
- **No enterprise RBAC.** `ApprovalAuthority` is intentionally a closed
  one-value enum, not a role/permission system; this design adds no
  users/groups/permissions model of any kind.

## 9. Explicitly deferred (not part of this design)

- The actual `approve`/`reject`/`request-correction` CLI command(s).
- Any on-disk persistence format for `ApprovalDecision`/
  `CanonicalKnowledgeEntry` (today both are in-memory only).
- The `run_id` field itself (section 6) — named as a prerequisite, not
  specified in full (exact hash inputs, exact `metadata` key name) here.
- R11/R12 orchestration, canonical knowledge querying/export, and any
  Plugin runtime integration.

IMPLEMENTATION_STATUS=NOT_IMPLEMENTED
