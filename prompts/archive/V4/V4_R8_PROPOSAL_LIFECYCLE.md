# LegacyMapper V4 — R8 Proposal Lifecycle

TASK=V4_R8_PROPOSAL_LIFECYCLE

MODE=DETERMINISTIC_PROPOSAL_LIFECYCLE

IMPLEMENTATION_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false

PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false

GIT_PUSH_ALLOWED=false

---

# Objective

Implement the V4 Proposal Lifecycle.

R8 introduces a formal pre-approval object representing a proposed interpretation, resolution, correction, reconciliation, selection, additional-information request, migration recommendation, or other knowledge action.

A Proposal is deliberately **not approved knowledge**.

R8 must allow LegacyMapper to represent:

```text
"Given this material/evidence/relation/context,
this is a proposed action or conclusion."
```

without converting that proposal into:

```text
truth
approval
authority
decision
canonical knowledge
implementation
completed work
```

R8 owns the lifecycle of proposals.

R9 will own Technical Lead approval.

R10 will own Canonical Knowledge Composition.

---

# Fundamental Pipeline

The conceptual boundary is:

```text
MATERIAL
   ↓
EVIDENCE / CONTEXT
   ↓
CLASSIFICATION / TEMPORAL / RELATIONS
   ↓
PROPOSAL                    <- R8
   ↓
TECHNICAL LEAD APPROVAL     <- R9
   ↓
CANONICAL KNOWLEDGE         <- R10
```

The following distinctions are mandatory:

```text
RELATION != PROPOSAL

PROPOSAL != APPROVAL
PROPOSAL != DECISION
PROPOSAL != TRUTH
PROPOSAL != AUTHORITY
PROPOSAL != CANONICAL KNOWLEDGE
PROPOSAL != IMPLEMENTATION
PROPOSAL != COMPLETED WORK
```

Most importantly:

```text
CREATING A PROPOSAL MUST NEVER APPROVE IT.
```

---

# Current Authorized Baseline

The Technical Lead has explicitly approved and formally closed:

```text
V4-R1
V4-R1.1
V4-R2
V4-R3
V4-R4
V4-R5
V4-R6
V4-R7
```

Expected repository state:

```text
latest_completed_round = V4-R7
latest_approved_round = V4-R7

current_round_in_progress = null

round_status = V4-R7_APPROVED
next = V4-R8

tests >= 928
readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do not reinterpret previous approvals.

---

# Required Reading

Before modifying anything read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_CONTRACT_FOUNDATION.md`
6. `docs/V4/V4_AI_HANDOVER.md`
7. `docs/V4/V4_PROPOSED_ROADMAP.md`
8. `docs/V4/V4_R1_KNOWLEDGE_DOMAIN_MODEL_RESULT.md`
9. `output/v4_r1/V4_KNOWLEDGE_DOMAIN_MODEL_CONTRACT.json`
10. `docs/V4/V4_R2_INPUT_SOURCE_CONTRACTS_RESULT.md`
11. `output/v4_r2/V4_INPUT_SOURCE_CONTRACTS.json`
12. `docs/V4/V4_R3_PROVENANCE_RESULT.md`
13. `output/v4_r3/V4_PROVENANCE_CONTRACT.json`
14. `docs/V4/V4_R4_HUMAN_SUPPLIED_MATERIAL_INGESTION_RESULT.md`
15. `output/v4_r4/V4_HUMAN_MATERIAL_INGESTION_CONTRACT.json`
16. `docs/V4/V4_R5_KNOWLEDGE_CLASSIFICATION_RESULT.md`
17. `output/v4_r5/V4_KNOWLEDGE_CLASSIFICATION_CONTRACT.json`
18. `docs/V4/V4_R6_AS_IS_TO_BE_SEPARATION_RESULT.md`
19. `output/v4_r6/V4_TEMPORAL_SEPARATION_CONTRACT.json`
20. `docs/V4/V4_R7_GAP_AND_CONFLICT_REPRESENTATION_RESULT.md`
21. `output/v4_r7/V4_GAP_CONFLICT_RELATION_CONTRACT.json`
22. `docs/V4/V4_R7_CLOSURE_AND_VERSIONING_RESULT.md`
23. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
24. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Inspect:

```text
legacy_documenter/knowledge/domain/
legacy_documenter/knowledge/input/
legacy_documenter/knowledge/provenance/
legacy_documenter/knowledge/ingestion/
legacy_documenter/knowledge/classification/
legacy_documenter/knowledge/temporal/
legacy_documenter/knowledge/relations/
```

Reuse existing deterministic identity, validation, sanitization, batch, and serialization conventions.

Do not redesign approved contracts merely to simplify R8.

---

# Entry Gate

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=928 PASS
```

Then:

```text
python -m legacy_documenter.knowledge.readiness
```

Expected:

```text
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

Verify:

```text
V4_R7=APPROVED
PROJECT_STATE.next=V4-R8
```

If any entry gate fails:

STOP.

Do not implement R8.

---

# Scope

R8 must provide a source-neutral Proposal model and deterministic lifecycle.

At minimum it must support proposals originating from:

```text
one or more MaterialItem ids
one or more KnowledgeRelation ids
explicit EvidenceRef ids/references where appropriate
```

A proposal must not require source code.

A proposal must not require R7 relationships.

A proposal must not require classification.

A proposal must not require temporal placement.

This is essential for:

```text
CODE_ONLY
CODE_AND_HUMAN_INFORMATION
HUMAN_INFORMATION_ONLY
PARTIAL_INFORMATION
```

---

# Proposal Kinds

Introduce a small closed proposal taxonomy.

Recommended minimum:

```text
INTERPRETATION
RESOLUTION
CORRECTION
RECONCILIATION
SELECTION
ADDITIONAL_INFORMATION
MIGRATION
KNOWLEDGE_ADDITION
```

Semantics:

## INTERPRETATION

Proposes an interpretation of available material/evidence.

Does not make the interpretation true.

---

## RESOLUTION

Proposes a way to resolve an explicitly represented issue/relation.

Does not resolve it automatically.

---

## CORRECTION

Proposes that existing knowledge/material should be corrected.

Does not modify the source material or canonical knowledge.

---

## RECONCILIATION

Proposes how multiple materials or statements could be reconciled.

Does not merge or replace them automatically.

---

## SELECTION

Proposes selecting one candidate/alternative over another.

Does not establish a winner or authority.

---

## ADDITIONAL_INFORMATION

Proposes requesting or supplying additional information before proceeding.

Does not automatically make the underlying material `MISSING` or `UNRESOLVED`.

---

## MIGRATION

Proposes a migration/change from one explicitly identified state to another.

Does not imply migration is approved, scheduled, started, or completed.

---

## KNOWLEDGE_ADDITION

Proposes that a new knowledge statement/content should eventually be incorporated.

Does not create canonical knowledge.

---

# Proposal Status

Introduce a closed lifecycle status owned by R8.

Recommended:

```text
DRAFT
READY_FOR_REVIEW
WITHDRAWN
SUPERSEDED
```

Do NOT include:

```text
APPROVED
REJECTED
CORRECTED
```

as R8 approval outcomes if doing so would overlap R9.

R9 owns the Technical Lead decision.

The preferred R8 lifecycle is therefore:

```text
DRAFT
   ↓
READY_FOR_REVIEW
```

with optional lifecycle branches:

```text
DRAFT -> WITHDRAWN

DRAFT -> SUPERSEDED
READY_FOR_REVIEW -> SUPERSEDED
```

A proposal in `READY_FOR_REVIEW` means only:

```text
structurally ready to be presented to the Technical Lead
```

It does NOT mean:

```text
approved
accepted
validated as true
canonical
```

---

# Proposal Status vs R1 ApprovalStatus

Do not reuse R1 `ApprovalStatus` as the R8 proposal lifecycle.

They represent different concerns.

R1 approval concepts exist at the knowledge-domain level.

R8 lifecycle describes the state of a proposal before R9's approval workflow.

Required distinction:

```text
ProposalStatus.READY_FOR_REVIEW
    != ApprovalStatus.APPROVED
```

---

# Proposal Record

Introduce a source-neutral record conceptually similar to:

```text
Proposal
    proposal_id
    proposal_kind
    status
    statement
    material_ids
    relation_ids
    evidence_refs
    rationale
    proposed_by
    supersedes_proposal_id?
    metadata
```

Exact shape may differ if repository conventions justify it.

Keep it small.

Do not turn Proposal into a universal workflow object.

---

# Proposal Content

A Proposal must contain an explicit proposed statement/action.

Examples:

```text
"Adopt architecture B as the target architecture."

"Request confirmation of the applicable authentication standard."

"Reconcile requirement A and requirement B by limiting A to internal users."

"Add the documented minimum income requirement to the canonical knowledge source."
```

The proposal content must be supplied explicitly.

R8 must NOT autonomously generate proposal prose from:

```text
materials
relations
classifications
temporal states
evidence
```

No semantic generation occurs in this round.

---

# Proposal Origin / Method

Represent how the proposal originated.

Recommended closed taxonomy:

```text
HUMAN_PROPOSED
DETERMINISTIC_RULE
AI_PROPOSED
```

Optionally:

```text
IMPORTED
```

if repository conventions justify it.

Important:

`AI_PROPOSED` must be representable because future LegacyMapper workflows may use an LLM.

But:

```text
R8 itself MUST NOT call an LLM.
```

A proposal supplied with:

```text
proposal_method = AI_PROPOSED
```

is data describing its origin.

It does not cause an AI call.

---

# AI Proposal Semantics

An AI-generated proposal must remain visibly AI-originated.

Never convert:

```text
AI_PROPOSED
```

into:

```text
HUMAN_PROPOSED
DETERMINISTIC_RULE
APPROVED
CONFIRMED
CANONICAL
```

merely because it passes structural validation.

This is important for future provenance and auditing.

---

# Source References

A proposal may reference:

```text
material_ids
relation_ids
evidence_refs
```

The Proposal must preserve these references.

Do not duplicate full source payloads.

Do not invent missing references.

At least one meaningful basis should normally exist.

Preferred validation:

```text
at least one material_id
OR
at least one relation_id
OR
at least one evidence reference
```

A proposal with no basis at all should be rejected.

---

# Relation Integration

R7 relations may be used as proposal basis.

Examples:

```text
CONFLICT(A,B)
    ↓
Proposal(kind=RESOLUTION)
```

or:

```text
GAP(A->B)
    ↓
Proposal(kind=MIGRATION)
```

However, this mapping is NEVER automatic.

Forbidden:

```text
CONFLICT -> automatic RESOLUTION proposal

GAP -> automatic MIGRATION proposal

DIFFERENCE -> automatic RECONCILIATION proposal

TEMPORAL_EVOLUTION -> automatic MIGRATION proposal
```

The caller must explicitly supply the proposal kind and content.

R8 may validate references to known R7 relation ids.

It must not infer a proposal from them.

---

# Proposal Does Not Resolve Relation

If a proposal references:

```text
CONFLICT(A,B)
```

and proposes:

```text
"Select A."
```

R8 records only:

```text
PROPOSAL:
    kind = SELECTION
    statement = "Select A."
    relation = CONFLICT(A,B)
```

The R7 conflict remains unchanged.

Do not mark:

```text
conflict.resolved=true
```

Do not remove the conflict.

Do not modify participants.

R9/R10 or later workflow owns resolution consequences.

---

# Gap Example

Given:

```text
GAP(A -> B)
```

R8 may explicitly receive:

```text
Proposal:
    kind = MIGRATION
    statement = "Migrate capability A to capability B."
```

R8 records that proposal.

It does NOT create:

```text
task
project
schedule
budget
implementation
approval
```

---

# Additional Information Proposal

This kind is important for uncertain knowledge.

Example:

```text
Proposal:
    kind = ADDITIONAL_INFORMATION
    statement =
        "Request confirmation of which authentication standard applies."
```

This proposal may reference:

```text
UNRESOLVED material
CONFLICT relation
PARTIAL material
```

but it must not require those statuses.

Likewise:

```text
UNRESOLVED
```

must not automatically create an `ADDITIONAL_INFORMATION` proposal.

---

# Lifecycle Transitions

Implement explicit deterministic lifecycle transitions.

Recommended valid transitions:

```text
DRAFT -> READY_FOR_REVIEW
DRAFT -> WITHDRAWN
DRAFT -> SUPERSEDED

READY_FOR_REVIEW -> SUPERSEDED
```

Potentially:

```text
READY_FOR_REVIEW -> WITHDRAWN
```

if clearly justified and documented.

Invalid transitions should be rejected.

Examples:

```text
WITHDRAWN -> READY_FOR_REVIEW
SUPERSEDED -> READY_FOR_REVIEW
```

should normally be invalid.

Do not introduce R9 outcomes.

---

# Initial Status

Preferred:

```text
new Proposal -> DRAFT
```

Creation must not automatically produce `READY_FOR_REVIEW` unless explicitly requested through a separate validated transition.

This keeps lifecycle visible and auditable.

---

# Ready for Review Validation

Transitioning:

```text
DRAFT -> READY_FOR_REVIEW
```

must require the proposal to be structurally reviewable.

At minimum:

```text
proposal_kind present
statement meaningful
proposal_method present
at least one explicit basis reference
```

Do not perform semantic truth validation.

Do not ask whether the proposed solution is good.

Do not determine whether the proposal should be approved.

---

# Withdrawal

`WITHDRAWN` means:

```text
this proposal is no longer being advanced for review
```

It does NOT mean:

```text
false
rejected by Technical Lead
incorrect
deleted
```

Do not delete withdrawn proposals.

Preserve them for traceability.

---

# Supersession

`SUPERSEDED` means:

```text
another proposal explicitly replaces this proposal in the proposal lifecycle
```

Supersession must be explicit.

Do not infer supersession from:

```text
creation date
newer proposal
same relation
same material
same proposal kind
different text
```

If Proposal B supersedes Proposal A:

```text
B.supersedes_proposal_id = A
```

or an equivalent explicit structure must establish the relationship.

Do not automatically delete or mutate historical content of A.

---

# Supersession Integrity

Reject:

```text
A supersedes A
```

Reject references to unknown proposals when the service has sufficient repository/collection context to validate them.

Avoid cycles such as:

```text
A supersedes B
B supersedes A
```

If the implementation provides a ProposalCollection capable of checking this.

Keep this deterministic and simple.

Do not build an unnecessarily complex workflow engine.

---

# Proposal Identity

Use deterministic identity.

Suggested prefix:

```text
PRP-
```

Reuse existing:

```text
stable_id
```

Identity should include semantically relevant immutable creation fields such as:

```text
proposal_kind
statement
proposal_method
canonical material ids
canonical relation ids
canonical evidence refs
```

Do not include mutable lifecycle state in the identity.

Therefore:

```text
DRAFT Proposal P
```

and:

```text
READY_FOR_REVIEW Proposal P
```

must retain the same:

```text
proposal_id
```

Likewise withdrawal/supersession must not silently create a new identity for the same proposal.

Do not include:

```text
current time
random UUID
machine path
memory address
status
```

in identity.

---

# Reference Ordering

Canonicalize unordered reference collections deterministically.

For example:

```text
material_ids = sorted unique ids
relation_ids = sorted unique ids
evidence_refs = deterministic canonical order
```

Equivalent proposal basis supplied in different input order must not change proposal identity.

Do not silently discard semantically conflicting duplicates.

---

# Proposal Immutability / Lifecycle Representation

Prefer not to mutate a Proposal object in-place if existing project style favors immutable/frozen domain records.

A lifecycle transition may return:

```text
a new Proposal instance
```

with:

```text
same proposal_id
new status
same immutable proposal content/basis
```

This is preferable if it fits existing conventions.

If controlled mutation is used instead, document and test it carefully.

Do not mutate source materials, relations, classifications, temporal placements, or provenance.

---

# Proposal Collection

Provide a deterministic in-memory collection/service if useful.

Suggested operations:

```text
add
get
list
by_status
by_kind
proposals_for_material
proposals_for_relation
transition
supersede
```

No database.

No persistence layer.

No external workflow engine.

---

# Duplicate Proposal Policy

Define and test deterministic duplicate behavior.

Recommended:

An exact semantic duplicate proposal receives the same `proposal_id`.

Adding the same proposal again:

```text
IDEMPOTENT_NO_OP
```

If the same deterministic identity somehow arrives with incompatible immutable semantics:

```text
REJECT
```

Do not silently overwrite.

Lifecycle status differences for the same proposal identity must be handled through explicit lifecycle transitions, not duplicate creation.

---

# Proposal Method Is Not Authority

Required:

```text
HUMAN_PROPOSED != APPROVED

DETERMINISTIC_RULE != APPROVED

AI_PROPOSED != APPROVED
```

Likewise:

```text
HUMAN_PROPOSED != automatically authoritative

AI_PROPOSED != automatically untrustworthy

DETERMINISTIC_RULE != automatically canonical
```

Proposal method records origin, not approval/truth.

---

# Evidence and Provenance

Do not invent evidence.

Proposal evidence references must be explicitly supplied.

R8 may correlate with R3 provenance where useful, but must not mutate historical provenance.

If a proposal is AI-originated, preserve that fact explicitly.

Do not manufacture:

```text
complete provenance
human approval
authority
```

simply to satisfy a structural contract.

A proposal can legitimately have incomplete upstream context if its explicit basis satisfies the R8 contract.

---

# R1 KnowledgeStatement Boundary

Do NOT create canonical `KnowledgeStatement` objects merely because a proposal exists or reaches `READY_FOR_REVIEW`.

Required:

```text
Proposal
    != KnowledgeStatement
```

R10 owns canonical Knowledge Composition after R9 approval.

Do not use `KnowledgeStatus.CONFIRMED` as a proposal lifecycle status.

---

# R7 Independence

Creating a Proposal from a relation must not mutate:

```text
KnowledgeRelation
MaterialItem
ClassificationRecord
TemporalPlacement
ProvenanceGraph
```

R7 relations remain evidence/context.

---

# R9 Boundary

R8 must stop before Technical Lead approval.

Do NOT implement:

```text
approve_proposal()
reject_proposal()
correct_and_approve()
```

Do not add an approval authority to R8 transitions.

Do not set:

```text
APPROVED
REJECTED
CORRECTED
```

as Technical Lead outcomes.

R9 owns those operations.

A Proposal in:

```text
READY_FOR_REVIEW
```

is the handoff boundary from R8 to R9.

---

# R10 Boundary

R8 must not compose canonical knowledge.

Even:

```text
ProposalStatus.READY_FOR_REVIEW
```

does not permit:

```text
KnowledgeStatement(status=CONFIRMED)
canonical=true
Knowledge Source insertion
```

R10 owns that after R9 approval.

---

# No Autonomous Proposal Generation

R8 does NOT inspect:

```text
CONFLICT
GAP
DIFFERENCE
TEMPORAL_EVOLUTION
```

and generate proposals automatically.

It also does not inspect:

```text
SourceType
KnowledgeNature
TemporalState
KnowledgeStatus
content
dates
filenames
directories
```

to determine a proposal.

The proposal must be explicitly supplied.

This round implements the **contract and lifecycle**, not proposal intelligence.

---

# Future AI Compatibility

R8 must nevertheless support future AI-generated proposals.

The future flow may be:

```text
Context Resolver
      ↓
LLM
      ↓
AI_PROPOSED Proposal
      ↓
R8 deterministic validation/lifecycle
      ↓
READY_FOR_REVIEW
      ↓
R9 Technical Lead Approval
```

R8 therefore acts as the deterministic envelope around future AI output.

The AI will not be allowed to bypass R8/R9.

---

# No AI Calls

Do not call:

```text
Claude
GitHub Copilot
Gemini
OpenAI
Ollama
any LLM/provider
```

Expected:

```text
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

---

# No External I/O

The R8 proposal module must not:

```text
read source files
read referenced documents
fetch URLs
scan directories
query databases
invoke Git
call providers
```

It operates on explicit already-available domain records/ids.

Contract/example generation may write deterministic artifacts through established repository mechanisms.

---

# Security

Proposal content, rationale, proposed_by, and metadata are untrusted data.

Reuse existing sanitization.

No:

```text
eval
exec
dynamic import
shell execution
template execution
```

Prompt-injection-shaped content must remain inert.

Secret-like values must be sanitized consistently with existing V4 behavior.

Do not leak untrusted proposal content into exception messages without sanitization.

---

# Suggested Implementation Location

Prefer:

```text
legacy_documenter/
└── knowledge/
    ├── domain/
    ├── input/
    ├── provenance/
    ├── ingestion/
    ├── classification/
    ├── temporal/
    ├── relations/
    └── proposals/
```

Possible modules:

```text
proposals/
├── __init__.py
├── enums.py
├── models.py
├── service.py
├── lifecycle.py
├── contract_report.py
└── example_report.py
```

Use fewer files if that is clearer.

Do not create empty abstractions merely to match this suggestion.

Follow:

`docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

---

# Contract Artifact

Generate:

```text
output/v4_r8/V4_PROPOSAL_LIFECYCLE_CONTRACT.json
```

It must document at minimum:

```text
contract_kind
schema_version
module

proposal_kinds
proposal_statuses
proposal_methods

proposal_semantics
proposal_basis_policy

creation_policy
initial_status

valid_transitions
invalid_transition_policy

ready_for_review_semantics
withdrawn_semantics
superseded_semantics
supersession_policy

identity_policy
reference_ordering_policy
duplicate_policy
serialization_policy

relation_integration
relation_mutation_policy

material_mutation_policy
classification_mutation_policy
temporal_mutation_policy
provenance_mutation_policy

approval_distinction
authority_distinction
truth_distinction
decision_distinction
canonical_knowledge_distinction
implementation_distinction

AI_proposal_policy
AI_boundary

R9_boundary
R10_boundary

security_policy
external_io_policy
```

Include semantic statements equivalent to:

```text
PROPOSAL_IS_NOT_APPROVAL
PROPOSAL_IS_NOT_DECISION
PROPOSAL_IS_NOT_TRUTH
PROPOSAL_IS_NOT_AUTHORITY
PROPOSAL_IS_NOT_CANONICAL_KNOWLEDGE
PROPOSAL_IS_NOT_IMPLEMENTATION

READY_FOR_REVIEW_IS_NOT_APPROVED

HUMAN_PROPOSED_IS_NOT_APPROVED
DETERMINISTIC_RULE_IS_NOT_APPROVED
AI_PROPOSED_IS_NOT_APPROVED

CONFLICT_DOES_NOT_AUTOMATICALLY_CREATE_RESOLUTION_PROPOSAL
GAP_DOES_NOT_AUTOMATICALLY_CREATE_MIGRATION_PROPOSAL

PROPOSAL_DOES_NOT_RESOLVE_RELATION
PROPOSAL_DOES_NOT_MUTATE_SOURCE_MATERIAL

R9_OWNS_TECHNICAL_LEAD_APPROVAL
R10_OWNS_CANONICAL_KNOWLEDGE_COMPOSITION
```

---

# Example Artifact

Generate:

```text
output/v4_r8/V4_PROPOSAL_LIFECYCLE_EXAMPLE.json
```

Use synthetic data only.

Include at minimum:

## Example 1 — Human proposal

Explicit proposal:

```text
kind = KNOWLEDGE_ADDITION
method = HUMAN_PROPOSED
statement =
"Add the minimum income requirement to the knowledge source."
```

Show:

```text
initial_status = DRAFT
approval = NOT_PERFORMED
canonical_knowledge = NOT_CREATED
```

Then explicit transition:

```text
DRAFT -> READY_FOR_REVIEW
```

Show:

```text
same proposal_id
approval = NOT_PERFORMED
```

---

## Example 2 — Conflict resolution proposal

Synthetic:

```text
CONFLICT(A,B)
```

Explicit proposal:

```text
kind = RESOLUTION
statement =
"Apply requirement A to internal users and B to external users."
```

Show:

```text
relation = UNCHANGED
winner = NOT_SELECTED
approval = NOT_PERFORMED
```

---

## Example 3 — Gap migration proposal

Synthetic:

```text
GAP(A -> B)
```

Explicit proposal:

```text
kind = MIGRATION
statement =
"Migrate capability A toward capability B."
```

Show:

```text
task = NOT_CREATED
migration_started = false
approval = NOT_PERFORMED
```

---

## Example 4 — Additional information

Explicit:

```text
kind = ADDITIONAL_INFORMATION
statement =
"Request confirmation of the applicable authentication standard."
```

Show:

```text
request_proposed = true
external_request_executed = false
approval = NOT_PERFORMED
```

---

## Example 5 — AI-originated proposal

Synthetic externally supplied proposal:

```text
method = AI_PROPOSED
```

Show:

```text
AI_CALL_PERFORMED=false
AI_ORIGIN_PRESERVED=true
APPROVAL=NOT_PERFORMED
```

---

## Example 6 — Supersession

Create:

```text
Proposal A
Proposal B
```

Explicitly establish:

```text
B supersedes A
```

Show:

```text
A.status = SUPERSEDED
B.status = DRAFT or READY_FOR_REVIEW according to explicit lifecycle

A.deleted = false
A.approved = false
B.approved = false
```

---

# Required Tests

Add focused deterministic R8 tests.

At minimum cover:

## Proposal taxonomy

Verify exact closed proposal kinds.

Verify exact R8 statuses.

Verify proposal methods.

---

## Creation

New proposal begins:

```text
DRAFT
```

unless repository conventions provide an equally explicit safe mechanism.

Creation never approves.

Creation never creates canonical knowledge.

---

## Explicit content

Proposal statement must be explicitly supplied and meaningful.

No automatic statement generation from source material/relation.

---

## Basis validation

Reject proposal with no:

```text
material id
relation id
evidence reference
```

unless a clearly documented stronger repository contract justifies otherwise.

---

## Relation independence

Creating a proposal referencing a R7 relation:

* does not mutate relation;
* does not resolve relation;
* does not select winner;
* does not alter participants.

---

## No automatic relation mapping

Prove:

```text
CONFLICT != automatic RESOLUTION
GAP != automatic MIGRATION
DIFFERENCE != automatic RECONCILIATION
TEMPORAL_EVOLUTION != automatic MIGRATION
```

No proposal exists unless explicit proposal input is supplied.

---

## Lifecycle

Valid transitions succeed.

Invalid transitions reject deterministically.

`proposal_id` remains unchanged through lifecycle transitions.

---

## Ready for review

`READY_FOR_REVIEW` means structurally ready only.

It must not create approval/canonical fields.

---

## Withdrawal

Withdrawn proposal remains preserved.

Withdrawal does not mean rejected/false.

---

## Supersession

Supersession explicit only.

No date/newer-text inference.

Reject self-supersession.

Prevent simple supersession cycles if ProposalCollection owns that validation.

Superseded proposal remains available.

---

## Identity

Equivalent proposals with same semantic creation fields get same deterministic id.

Reference input ordering does not change identity.

Lifecycle status does not change identity.

---

## Duplicate policy

Exact duplicate is idempotent.

Conflicting immutable semantics are rejected.

Status changes occur only through lifecycle transition.

---

## Proposal method

Verify:

```text
HUMAN_PROPOSED != APPROVED
DETERMINISTIC_RULE != APPROVED
AI_PROPOSED != APPROVED
```

`AI_PROPOSED` performs zero AI calls.

---

## Source type independence

Proposal kind must not be inferred from `SourceType`.

---

## Classification independence

Proposal kind must not be inferred from `KnowledgeNature`.

---

## Temporal independence

Proposal kind must not be inferred from `TemporalState`.

---

## KnowledgeStatus independence

Proposal lifecycle must not mutate or infer R1 KnowledgeStatus.

---

## Material immutability

No proposal operation mutates MaterialItem.

---

## Relation immutability

No proposal operation mutates KnowledgeRelation.

---

## Classification immutability

Optional correlation never mutates ClassificationRecord.

---

## Temporal immutability

Optional correlation never mutates TemporalPlacement.

---

## Provenance immutability

No proposal operation mutates ProvenanceGraph.

---

## Approval boundary

R8 exposes no Technical Lead approval operation.

No `approve_proposal`.

No automatic `APPROVED`.

---

## Canonical boundary

No Proposal operation creates:

```text
KnowledgeStatement
canonical Knowledge Source
```

---

## Security

Secret-like values sanitized.

Prompt-injection-shaped statement/rationale remains inert.

No execution.

---

## No I/O

No file/network/database/provider I/O.

---

## Batch behavior

If batch creation is implemented:

* deterministic order;
* failure isolation;
* no item loss;
* deterministic accepted/rejected results;
* duplicate policy respected.

---

## Determinism

Generate contract twice independently.

Generate example twice independently.

Require byte-identical output.

---

## Regression

Run all tests.

Expected:

```text
>928 PASS
```

Report exact final count.

---

# Deterministic Serialization

Proposal serialization must be deterministic.

Canonicalize unordered references.

Do not rely on Python set/dict traversal for semantic ordering.

Lifecycle status may appear in serialized current proposal state but MUST NOT influence `proposal_id`.

---

# Determinism Verification

Generate:

```text
output/v4_r8/V4_PROPOSAL_LIFECYCLE_CONTRACT.json
```

twice independently.

Required:

```text
CONTRACT_DETERMINISM=PASS
```

Generate:

```text
output/v4_r8/V4_PROPOSAL_LIFECYCLE_EXAMPLE.json
```

twice independently.

Required:

```text
EXAMPLE_DETERMINISM=PASS
```

Compute SHA-256 values for both.

---

# Final Regression

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>928 PASS
```

Then:

```text
python -m legacy_documenter.knowledge.readiness
```

Expected:

```text
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

---

# Production Behavior

R8 must be additive.

Expected:

```text
V3_BEHAVIOR_CHANGED=false

V4_R1_BEHAVIOR_CHANGED=false
V4_R2_BEHAVIOR_CHANGED=false
V4_R3_BEHAVIOR_CHANGED=false
V4_R4_BEHAVIOR_CHANGED=false
V4_R5_BEHAVIOR_CHANGED=false
V4_R6_BEHAVIOR_CHANGED=false
V4_R7_BEHAVIOR_CHANGED=false
```

If an actual defect in an approved contract blocks R8:

STOP.

Document the blocker.

Do not silently alter previous semantics.

---

# PROJECT_STATE Update

After successful implementation and validation update:

```text
PROJECT_STATE.json
```

to:

```text
latest_completed_round = V4-R8
latest_approved_round = V4-R7

current_round_in_progress =
"V4-R8 (pending Technical Lead review)"

round_status =
V4-R8_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R8

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do NOT mark R8 approved.

---

# Required Result

Create:

```text
docs/V4/V4_R8_PROPOSAL_LIFECYCLE_RESULT.md
```

Report at minimum:

```text
STATUS
ENTRY_GATE
BASELINE_TESTS
FINAL_TESTS

PROPOSAL_MODEL
PROPOSAL_KINDS
PROPOSAL_STATUSES
PROPOSAL_METHODS

CREATION_POLICY
INITIAL_STATUS
PROPOSAL_BASIS_POLICY

VALID_TRANSITIONS
INVALID_TRANSITION_POLICY

READY_FOR_REVIEW_SEMANTICS
WITHDRAWN_SEMANTICS
SUPERSEDED_SEMANTICS
SUPERSESSION_POLICY

RELATION_INTEGRATION
AUTOMATIC_RELATION_TO_PROPOSAL_MAPPING

IDENTITY
REFERENCE_ORDERING
DUPLICATE_POLICY
SERIALIZATION

MATERIAL_MUTATION
RELATION_MUTATION
CLASSIFICATION_MUTATION
TEMPORAL_MUTATION
PROVENANCE_MUTATION
KNOWLEDGE_STATUS_MUTATION

APPROVAL_DISTINCTION
AUTHORITY_DISTINCTION
TRUTH_DISTINCTION
DECISION_DISTINCTION
CANONICAL_KNOWLEDGE_DISTINCTION
IMPLEMENTATION_DISTINCTION

AI_PROPOSAL_SUPPORT
AI_CALLS

R9_BOUNDARY
R10_BOUNDARY

BATCH_PROPOSALS

SANITIZATION
PROMPT_INJECTION_BOUNDARY
SECURITY
NO_IO

CONTRACT_ARTIFACT
CONTRACT_SHA256
EXAMPLE_ARTIFACT
EXAMPLE_SHA256

CONTRACT_DETERMINISM
EXAMPLE_DETERMINISM

V3_REGRESSION
V4_R1_REGRESSION
V4_R2_REGRESSION
V4_R3_REGRESSION
V4_R4_REGRESSION
V4_R5_REGRESSION
V4_R6_REGRESSION
V4_R7_REGRESSION

READINESS
AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE
PRODUCTION_BEHAVIOR_CHANGED
TECHNICAL_DEBT

DECISION
NEXT
```

Also include:

```text
## Reused Components
## New Components
## Proposal Invariants
## Lifecycle Semantics
## Relation Integration
## AI Proposal Boundary
## R9 Boundary
## R10 Boundary
## Security Notes
## Out of Scope
```

---

# Expected Success State

```text
STATUS=V4_R8_PROPOSAL_LIFECYCLE_COMPLETE
ENTRY_GATE=PASS

BASELINE_TESTS=928_PASS
FINAL_TESTS=>928_PASS

PROPOSAL_KINDS=
INTERPRETATION,
RESOLUTION,
CORRECTION,
RECONCILIATION,
SELECTION,
ADDITIONAL_INFORMATION,
MIGRATION,
KNOWLEDGE_ADDITION

PROPOSAL_STATUSES=
DRAFT,
READY_FOR_REVIEW,
WITHDRAWN,
SUPERSEDED

PROPOSAL_METHODS=
HUMAN_PROPOSED,
DETERMINISTIC_RULE,
AI_PROPOSED

CREATION_POLICY=EXPLICIT_ONLY
INITIAL_STATUS=DRAFT

AUTOMATIC_RELATION_TO_PROPOSAL_MAPPING=NONE

IDENTITY=DETERMINISTIC
REFERENCE_ORDERING=DETERMINISTIC
SERIALIZATION=DETERMINISTIC

MATERIAL_MUTATION=NONE
RELATION_MUTATION=NONE
CLASSIFICATION_MUTATION=NONE
TEMPORAL_MUTATION=NONE
PROVENANCE_MUTATION=NONE
KNOWLEDGE_STATUS_MUTATION=NONE

APPROVAL_DISTINCTION=PASS
AUTHORITY_DISTINCTION=PASS
TRUTH_DISTINCTION=PASS
DECISION_DISTINCTION=PASS
CANONICAL_KNOWLEDGE_DISTINCTION=PASS
IMPLEMENTATION_DISTINCTION=PASS

AI_PROPOSAL_SUPPORT=REPRESENTABLE
AI_CALLS=0

R9_BOUNDARY=PASS
R10_BOUNDARY=PASS

PROMPT_INJECTION_BOUNDARY=PASS
SECURITY=PASS
NO_IO=PASS

CONTRACT_ARTIFACT=VALID
EXAMPLE_ARTIFACT=VALID
CONTRACT_DETERMINISM=PASS
EXAMPLE_DETERMINISM=PASS

V3_REGRESSION=PASS
V4_R1_REGRESSION=PASS
V4_R2_REGRESSION=PASS
V4_R3_REGRESSION=PASS
V4_R4_REGRESSION=PASS
V4_R5_REGRESSION=PASS
V4_R6_REGRESSION=PASS
V4_R7_REGRESSION=PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW

PRODUCTION_BEHAVIOR_CHANGED=V4_ADDITIVE_ONLY

DECISION=V4_R8_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R8
```

---

# Critical R9 Boundary

R8 ends at:

```text
Proposal(
    status=READY_FOR_REVIEW
)
```

It MUST NOT proceed to:

```text
APPROVED
REJECTED
CORRECTED_AND_APPROVED
```

It MUST NOT decide:

```text
Technical Lead accepts proposal
Technical Lead rejects proposal
proposal becomes authoritative
proposal becomes canonical knowledge
```

Those operations belong to:

```text
V4-R9 — Technical Lead Approval
```

---

# Critical R10 Boundary

Even after:

```text
Proposal.status = READY_FOR_REVIEW
```

R8 must not create:

```text
KnowledgeStatement
Canonical Knowledge Source
Plugin knowledge
human-readable canonical documentation
```

R10 owns Canonical Knowledge Composition after R9 approval.

---

# Out of Scope

Do NOT implement:

* autonomous proposal generation;
* LLM proposal generation;
* semantic conflict resolution;
* semantic gap resolution;
* winner/loser selection;
* Technical Lead approval;
* proposal approval/rejection;
* canonical Knowledge Source composition;
* source material modification;
* relation resolution;
* task generation;
* project generation;
* migration execution;
* external information requests;
* notifications;
* database persistence;
* workflow engine;
* R9 Technical Lead Approval;
* R10 Canonical Knowledge Composition;
* R11 Human-Readable Projection;
* R12 Plugin-Facing Output;
* R13 Regression/Security closure;
* R14 Manuals/Final Baseline;
* V5 technology/language/framework agnosticism.

---

# Stop Condition

STOP after:

1. implementing the Proposal domain model;
2. implementing deterministic proposal creation;
3. implementing deterministic pre-approval lifecycle;
4. supporting explicit proposal basis references;
5. supporting AI_PROPOSED as origin data without calling AI;
6. proving no automatic relation-to-proposal mapping;
7. proving source records and R7 relations are not mutated;
8. proving READY_FOR_REVIEW is not approval;
9. proving R9/R10 boundaries;
10. generating deterministic contract/example artifacts;
11. running all tests;
12. confirming readiness;
13. creating the R8 result;
14. updating PROJECT_STATE to pending Technical Lead review.

Do NOT:

* approve R8;
* commit;
* push;
* begin R9.

Wait for Technical Lead review.

Expected final state:

```text
V4_R8=READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R8
```
