# LegacyMapper V4 — R9 Technical Lead Approval

TASK=V4_R9_TECHNICAL_LEAD_APPROVAL

MODE=DETERMINISTIC_HUMAN_APPROVAL_WORKFLOW

IMPLEMENTATION_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false

PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false

GIT_PUSH_ALLOWED=false

---

# Objective

Implement the formal Technical Lead approval layer for V4.

R9 owns the transition from:

```text
Proposal(status=READY_FOR_REVIEW)
```

to an explicit human decision.

Only the Technical Lead may provide that decision.

R9 must formalize and record approval outcomes without creating canonical knowledge.

Canonical Knowledge Composition remains R10.

The pipeline is:

```text
MATERIAL / EVIDENCE / RELATIONS
              ↓
           PROPOSAL
              ↓
      READY_FOR_REVIEW
              ↓
     TECHNICAL LEAD DECISION     <- R9
              ↓
       APPROVAL RECORD
              ↓
   CANONICAL KNOWLEDGE           <- R10
```

---

# Core Authority Rule

This rule is absolute:

```text
ONLY THE TECHNICAL LEAD MAY AUTHORIZE
INCORPORATION INTO CANONICAL KNOWLEDGE.
```

The system may:

```text
validate
record
trace
serialize
report
```

a decision.

The system may NOT:

```text
grant approval
infer approval
simulate approval
assume approval
upgrade a proposal automatically
```

---

# Fundamental Distinctions

Required:

```text
PROPOSAL != DECISION

READY_FOR_REVIEW != APPROVED

DECISION != CANONICAL KNOWLEDGE

APPROVED != CANONICAL KNOWLEDGE

REJECTED != FALSE

CORRECTION_REQUESTED != REJECTED

AI_PROPOSED != AI_APPROVED

HUMAN_PROPOSED != HUMAN_APPROVED
```

Most importantly:

```text
R9 RECORDS HUMAN AUTHORITY.
R9 DOES NOT CREATE HUMAN AUTHORITY.
```

---

# Authorized Baseline

Before implementation R8 must be formally closed.

Expected:

```text
latest_completed_round = V4-R8
latest_approved_round = V4-R8

current_round_in_progress = null

round_status = V4-R8_APPROVED
next = V4-R9

tests >= 1022
readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

If R8 is not formally closed:

STOP.

Do not implement R9.

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_CONTRACT_FOUNDATION.md`
6. `docs/V4/V4_AI_HANDOVER.md`
7. `docs/V4/V4_PROPOSED_ROADMAP.md`
8. `docs/V4/V4_R8_PROPOSAL_LIFECYCLE_RESULT.md`
9. `docs/V4/V4_R8_CLOSURE_AND_VERSIONING_RESULT.md`
10. `output/v4_r8/V4_PROPOSAL_LIFECYCLE_CONTRACT.json`
11. `docs/V4/V4_R7_GAP_AND_CONFLICT_REPRESENTATION_RESULT.md`
12. `output/v4_r7/V4_GAP_CONFLICT_RELATION_CONTRACT.json`
13. `docs/V4/V4_R3_PROVENANCE_RESULT.md`
14. `output/v4_r3/V4_PROVENANCE_CONTRACT.json`
15. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
16. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Inspect:

```text
legacy_documenter/knowledge/proposals/
legacy_documenter/knowledge/domain/
legacy_documenter/knowledge/provenance/
```

Reuse existing deterministic identity, sanitization, serialization, and validation conventions.

Do not redesign R8.

---

# Entry Gate

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=1022 PASS
```

Then:

```text
python -m legacy_documenter.knowledge.readiness
```

Required:

```text
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

Verify:

```text
V4_R8=APPROVED
PROJECT_STATE.next=V4-R9
```

If any gate fails:

STOP.

---

# Scope

R9 must provide:

```text
Technical Lead decision model
decision validation
decision recording
decision history
correction workflow representation
approval/rejection semantics
proposal-to-decision traceability
deterministic serialization
```

R9 must NOT provide:

```text
canonical Knowledge Source composition
KnowledgeStatement creation from approval
Plugin output
human-readable canonical projections
LLM decision making
automatic approval
```

---

# Approval Decision Taxonomy

Introduce a small closed taxonomy.

Recommended:

```text
APPROVED
REJECTED
CORRECTION_REQUESTED
```

Semantics:

## APPROVED

The Technical Lead explicitly accepts the proposal for later canonical composition.

It does NOT itself create canonical knowledge.

Required distinction:

```text
APPROVED != CANONICALIZED
```

---

## REJECTED

The Technical Lead explicitly decides that this proposal should not proceed.

It means:

```text
proposal rejected
```

It does NOT necessarily mean:

```text
proposal statement is objectively false
source material is false
relation is false
underlying requirement is invalid
```

Required:

```text
REJECTED != FALSE
```

---

## CORRECTION_REQUESTED

The Technical Lead does not approve the proposal in its current form and requests correction.

It means:

```text
proposal must be revised before another approval decision
```

It does NOT mean:

```text
proposal permanently rejected
proposal is false
canonical knowledge changed
```

---

# Approval Record

Introduce a source-neutral deterministic record conceptually similar to:

```text
ApprovalDecision
    decision_id
    proposal_id
    decision
    authority
    decided_by
    rationale
    correction_instructions?
    previous_decision_id?
    metadata
```

Exact field names may vary if repository conventions justify it.

Keep it small.

---

# Authority

R9 must explicitly represent authority.

Recommended closed authority enum:

```text
TECHNICAL_LEAD
```

For V4, this is intentionally the only valid approval authority.

Do NOT build RBAC.

Do NOT add:

```text
ADMIN
MANAGER
REVIEWER
AI
SYSTEM
```

as approval authorities.

The user has explicitly defined the Technical Lead as the sole final approval authority for LegacyMapper V4.

---

# Actor Identity

`decided_by` may identify the human operator.

It must be supplied explicitly.

Do not infer identity from:

```text
OS username
Git author
machine account
environment variables
repository path
previous proposal creator
```

The system records what the caller supplies.

Do not build authentication.

Authentication/RBAC are out of scope.

---

# Decision Preconditions

An approval decision may only be recorded against a Proposal whose current R8 status is:

```text
READY_FOR_REVIEW
```

Reject decisions against:

```text
DRAFT
WITHDRAWN
SUPERSEDED
```

unless a future explicitly approved contract says otherwise.

Required:

```text
ProposalStatus.READY_FOR_REVIEW
    is necessary
    but not sufficient
```

because an explicit Technical Lead decision is still required.

---

# Explicit Decision Only

R9 must never infer a decision from:

```text
proposal_method
proposal_kind
proposal content
source type
relation kind
confidence
evidence count
human origin
AI origin
dates
previous decisions
```

Forbidden examples:

```text
HUMAN_PROPOSED -> automatic APPROVED

AI_PROPOSED -> automatic REJECTED

DETERMINISTIC_RULE -> automatic APPROVED

high evidence count -> automatic APPROVED

CONFLICT resolution proposal -> automatic CORRECTION_REQUESTED
```

The caller must explicitly provide the decision.

---

# Decision Origin

All actual approval decisions in V4 must originate from the Technical Lead.

The system must not expose:

```text
AI_APPROVED
SYSTEM_APPROVED
AUTO_APPROVED
RULE_APPROVED
```

No automatic decision origin exists.

---

# Approval Does Not Mutate Proposal Semantics

R9 should preferably record decisions separately from the R8 Proposal.

Do NOT add:

```text
proposal.status = APPROVED
```

because `ProposalStatus` belongs to R8 and intentionally excludes approval outcomes.

Keep:

```text
Proposal lifecycle
```

and:

```text
Technical Lead approval decision
```

as separate concerns.

A proposal remains traceable as the proposal that was reviewed.

---

# Approval Record Identity

Use deterministic identity.

Suggested prefix:

```text
APR-
```

Reuse:

```text
stable_id
```

Identity should include immutable semantic decision fields such as:

```text
proposal_id
decision
authority
decided_by
rationale
correction instructions
previous decision id
```

Do not include:

```text
current time
random UUID
machine identity
memory address
```

unless an explicitly supplied business timestamp is part of the domain record and deterministically serialized.

Prefer not to require timestamps.

---

# Decision History

R9 must preserve decision history.

Do not overwrite previous decisions.

A proposal may have a sequence such as:

```text
READY_FOR_REVIEW
      ↓
CORRECTION_REQUESTED
      ↓
revised proposal
      ↓
READY_FOR_REVIEW
      ↓
APPROVED
```

Do not mutate the earlier decision into the later one.

Preserve both.

---

# Correction Workflow

Important distinction:

```text
CORRECTION_REQUESTED
```

must NOT mutate the existing Proposal text in-place.

The reviewed proposal is historical evidence of what was reviewed.

The correction should result in a NEW proposal if semantic content changes.

For example:

```text
Proposal A
    statement = original content

Decision 1
    CORRECTION_REQUESTED

Proposal B
    corrected content
    supersedes Proposal A

Decision 2
    APPROVED
```

R8 already supports proposal supersession.

R9 must integrate with that concept rather than rewriting historical proposal content.

---

# Re-Decision Policy

Define a clear deterministic rule.

Preferred:

A specific immutable proposal version may have at most one terminal Technical Lead decision.

After:

```text
APPROVED
```

or:

```text
REJECTED
```

do not allow another decision for the exact same Proposal version.

After:

```text
CORRECTION_REQUESTED
```

prefer requiring a new corrected Proposal version before another decision.

This preserves auditability.

Do not silently replace a decision.

---

# Approval Collection

Provide an in-memory deterministic collection/service if useful.

Suggested operations:

```text
record_decision
get
list
for_proposal
latest_for_proposal
by_decision
```

No database.

No external workflow engine.

---

# Duplicate Decision Policy

Exact duplicate decision:

```text
IDEMPOTENT_NO_OP
```

Same deterministic identity but incompatible content:

```text
REJECT
```

A different decision against a proposal that already has a terminal decision:

```text
REJECT
```

Do not overwrite.

---

# Approval vs Proposal Method

Required:

```text
HUMAN_PROPOSED != APPROVED
AI_PROPOSED != REJECTED
DETERMINISTIC_RULE != APPROVED
```

Proposal origin has no automatic influence on decision.

---

# Approval vs Authority

Required:

```text
authority = TECHNICAL_LEAD
```

does not mean the system itself acted as Technical Lead.

It means the recorded decision was explicitly supplied as a Technical Lead decision.

The agent must not fabricate this record during normal processing.

---

# Approval vs Canonical Knowledge

This is a critical boundary.

Even:

```text
Decision(
    decision = APPROVED
)
```

must NOT produce:

```text
KnowledgeStatement
canonical Knowledge Source
Plugin payload
canonical document
```

R10 owns composition.

R9 only makes the proposal eligible for R10.

Conceptually:

```text
APPROVED
    ↓
ELIGIBLE_FOR_CANONICAL_COMPOSITION
```

not:

```text
APPROVED
    ↓
CANONICALIZED
```

---

# Canonical Eligibility

R9 may expose deterministic query semantics such as:

```text
is_eligible_for_canonical_composition(proposal_id)
```

if useful.

Required behavior:

```text
APPROVED -> true
REJECTED -> false
CORRECTION_REQUESTED -> false
NO_DECISION -> false
```

But this helper must NOT compose knowledge.

It only represents eligibility.

---

# Relation Independence

Approval of a Proposal referencing a R7 relation must not mutate the relation.

For example:

```text
CONFLICT(A,B)
    ↓
Proposal P
    ↓
APPROVED
```

must NOT automatically produce:

```text
conflict.resolved = true
winner = A
winner = B
```

R10 or later explicit knowledge composition may represent the accepted resolution.

R7 relation remains historical/contextual evidence.

---

# Material Independence

Decision recording must not mutate:

```text
MaterialItem
KnowledgeRelation
ClassificationRecord
TemporalPlacement
ProvenanceGraph
KnowledgeStatus
```

---

# AI Boundary

R9 makes no AI calls.

Do not call:

```text
Claude
Copilot
Gemini
OpenAI
Ollama
any provider
```

Expected:

```text
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

AI must never determine approval.

---

# Security

Treat:

```text
decided_by
rationale
correction_instructions
metadata
```

as untrusted input.

Reuse sanitization.

Prompt-injection-shaped text must remain inert.

No:

```text
eval
exec
shell execution
dynamic import
template execution
```

Do not echo secrets through exception messages.

---

# No External I/O

The R9 module must not:

```text
read source files
fetch documents
scan directories
call providers
query databases
invoke Git
send notifications
```

It operates on explicit in-memory domain records.

---

# Suggested Package

Prefer:

```text
legacy_documenter/
└── knowledge/
    └── approval/
```

Possible files:

```text
approval/
├── __init__.py
├── enums.py
├── models.py
├── service.py
├── contract_report.py
└── example_report.py
```

Use fewer files if clearer.

Do not create pattern-heavy abstractions unnecessarily.

Follow:

```text
docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md
```

---

# Contract Artifact

Generate:

```text
output/v4_r9/V4_TECHNICAL_LEAD_APPROVAL_CONTRACT.json
```

Document at minimum:

```text
contract_kind
schema_version
module

decision_types
authority_types

decision_semantics
authority_semantics

proposal_status_precondition

explicit_decision_policy
automatic_decision_policy

approval_record_model
decision_identity_policy
duplicate_policy
decision_history_policy
redecision_policy

correction_policy
proposal_immutability_policy
relation_mutation_policy
material_mutation_policy
classification_mutation_policy
temporal_mutation_policy
provenance_mutation_policy
knowledge_status_mutation_policy

approval_vs_truth
approval_vs_authority
approval_vs_proposal_origin
approval_vs_canonical_knowledge

canonical_eligibility_policy

R10_boundary

AI_boundary
security_policy
external_io_policy
```

Include semantic statements equivalent to:

```text
ONLY_TECHNICAL_LEAD_MAY_AUTHORIZE_APPROVAL

READY_FOR_REVIEW_IS_NOT_APPROVED

APPROVED_IS_NOT_CANONICALIZED

REJECTED_IS_NOT_FALSE

CORRECTION_REQUESTED_IS_NOT_REJECTED

PROPOSAL_METHOD_DOES_NOT_DETERMINE_DECISION

AI_NEVER_APPROVES

SYSTEM_NEVER_APPROVES

R9_RECORDS_HUMAN_AUTHORITY
R9_DOES_NOT_CREATE_HUMAN_AUTHORITY

APPROVED_ONLY_MAKES_PROPOSAL_ELIGIBLE_FOR_R10

R10_OWNS_CANONICAL_KNOWLEDGE_COMPOSITION
```

---

# Example Artifact

Generate:

```text
output/v4_r9/V4_TECHNICAL_LEAD_APPROVAL_EXAMPLE.json
```

Synthetic data only.

Include:

## Example 1 — Approved proposal

```text
Proposal P
status = READY_FOR_REVIEW
```

Explicit Technical Lead decision:

```text
APPROVED
```

Show:

```text
proposal mutated = false
canonical knowledge created = false
eligible_for_R10 = true
```

---

## Example 2 — Rejected proposal

Explicit:

```text
REJECTED
```

Show:

```text
proposal false = NOT_DETERMINED
source false = NOT_DETERMINED
canonical knowledge created = false
eligible_for_R10 = false
```

---

## Example 3 — Correction requested

Explicit:

```text
CORRECTION_REQUESTED
```

Show:

```text
original proposal preserved = true
proposal content mutated = false
eligible_for_R10 = false
```

Then illustrate conceptually:

```text
Proposal B supersedes Proposal A
```

without automatically creating B if that belongs to the caller/R8.

---

## Example 4 — AI-originated proposal approved by human

Proposal:

```text
proposal_method = AI_PROPOSED
```

Decision:

```text
authority = TECHNICAL_LEAD
decision = APPROVED
```

Show:

```text
AI_APPROVAL = false
AI_ORIGIN_PRESERVED = true
HUMAN_DECISION_RECORDED = true
```

---

## Example 5 — Invalid proposal status

Proposal:

```text
status = DRAFT
```

Attempt decision:

```text
APPROVED
```

Expected:

```text
REJECTED_BY_VALIDATION
```

No approval record created.

---

## Example 6 — Duplicate/second terminal decision

Proposal already has:

```text
APPROVED
```

Attempt:

```text
REJECTED
```

Expected:

```text
REJECTED_BY_VALIDATION
```

Original decision preserved.

---

# Required Tests

Add deterministic tests covering at minimum:

### Taxonomy

Exact decision types:

```text
APPROVED
REJECTED
CORRECTION_REQUESTED
```

Exact authority types:

```text
TECHNICAL_LEAD
```

---

### Proposal status precondition

Only:

```text
READY_FOR_REVIEW
```

may receive a decision.

Reject:

```text
DRAFT
WITHDRAWN
SUPERSEDED
```

---

### Explicit decision

No decision is inferred.

No automatic approval.

No automatic rejection.

---

### Authority

Reject any authority not equal to:

```text
TECHNICAL_LEAD
```

No AI/system authority.

---

### Actor identity

`decided_by` required.

Never inferred from environment/Git/OS.

---

### Approval semantics

APPROVED does not create canonical knowledge.

APPROVED makes proposal eligible for R10 only.

---

### Rejection semantics

REJECTED does not mark statement/source/material false.

---

### Correction semantics

CORRECTION_REQUESTED preserves proposal.

Does not mutate proposal statement.

Does not create corrected proposal automatically.

---

### Decision history

Historical decisions preserved.

No overwrite.

---

### Re-decision policy

No second terminal decision against same immutable proposal version.

After CORRECTION_REQUESTED, prefer new proposal version for further review.

---

### Identity

Equivalent decision input produces identical deterministic `decision_id`.

No time/randomness.

---

### Duplicate policy

Exact duplicate idempotent.

Conflicting duplicate rejected.

---

### Proposal immutability

Proposal remains unchanged after decision.

---

### Relation immutability

Referenced relation remains unchanged.

---

### Material/classification/temporal/provenance/status immutability

No mutation.

---

### Proposal method independence

Verify:

```text
AI_PROPOSED
HUMAN_PROPOSED
DETERMINISTIC_RULE
```

do not determine approval outcome.

---

### AI boundary

Zero provider calls.

Zero LLM calls.

No approval inference.

---

### Canonical boundary

No `KnowledgeStatement` creation.

No canonical Knowledge Source creation.

---

### Security

Secret-like decision input sanitized.

Prompt-injection text inert.

Exception messages do not leak untrusted values.

---

### No I/O

No file/network/database/provider/Git I/O in approval model/service.

---

### Determinism

Contract byte-identical across repeated generation.

Example byte-identical across repeated generation.

---

### Regression

Run all tests.

Expected:

```text
>1022 PASS
```

Report exact count.

---

# Deterministic Serialization

Canonical deterministic serialization required.

Use stable field order / canonical JSON conventions already established in V4.

Do not depend on set/dict traversal ordering.

---

# Final Regression

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>1022 PASS
```

Then:

```text
python -m legacy_documenter.knowledge.readiness
```

Required:

```text
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

---

# Production Behavior

R9 must be additive.

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
V4_R8_BEHAVIOR_CHANGED=false
```

If an approved prior contract blocks R9:

STOP.

Do not silently alter it.

---

# PROJECT_STATE Update

After successful implementation:

```text
latest_completed_round = V4-R9
latest_approved_round = V4-R8

current_round_in_progress =
"V4-R9 (pending Technical Lead review)"

round_status =
V4-R9_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R9

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do NOT mark R9 approved.

---

# Required Result

Create:

```text
docs/V4/V4_R9_TECHNICAL_LEAD_APPROVAL_RESULT.md
```

Report at minimum:

```text
STATUS
ENTRY_GATE
BASELINE_TESTS
FINAL_TESTS

DECISION_MODEL
DECISION_TYPES
AUTHORITY_TYPES

PROPOSAL_STATUS_PRECONDITION
EXPLICIT_DECISION_POLICY
AUTOMATIC_DECISION_POLICY

APPROVAL_SEMANTICS
REJECTION_SEMANTICS
CORRECTION_SEMANTICS

DECISION_IDENTITY
DUPLICATE_POLICY
DECISION_HISTORY
REDECISION_POLICY

CORRECTION_POLICY

PROPOSAL_MUTATION
RELATION_MUTATION
MATERIAL_MUTATION
CLASSIFICATION_MUTATION
TEMPORAL_MUTATION
PROVENANCE_MUTATION
KNOWLEDGE_STATUS_MUTATION

APPROVAL_VS_TRUTH
APPROVAL_VS_AUTHORITY
APPROVAL_VS_PROPOSAL_ORIGIN
APPROVAL_VS_CANONICAL_KNOWLEDGE

CANONICAL_ELIGIBILITY

AI_APPROVAL
AI_CALLS

R10_BOUNDARY

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
V4_R8_REGRESSION

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

Include sections:

```text
## Reused Components
## New Components
## Approval Invariants
## Approval Semantics
## Rejection Semantics
## Correction Workflow
## Decision History
## Canonical Eligibility
## AI Boundary
## R10 Boundary
## Security Notes
## Out of Scope
```

---

# Expected Success State

```text
STATUS=V4_R9_TECHNICAL_LEAD_APPROVAL_COMPLETE
ENTRY_GATE=PASS

BASELINE_TESTS=1022_PASS
FINAL_TESTS=>1022_PASS

DECISION_TYPES=
APPROVED,
REJECTED,
CORRECTION_REQUESTED

AUTHORITY_TYPES=
TECHNICAL_LEAD

PROPOSAL_STATUS_PRECONDITION=
READY_FOR_REVIEW_ONLY

EXPLICIT_DECISION_POLICY=REQUIRED
AUTOMATIC_DECISION_POLICY=NONE

APPROVED_IS_NOT_CANONICALIZED=PASS
REJECTED_IS_NOT_FALSE=PASS
CORRECTION_REQUESTED_IS_NOT_REJECTED=PASS

DECISION_IDENTITY=DETERMINISTIC
DUPLICATE_POLICY=DETERMINISTIC
DECISION_HISTORY=PRESERVED

PROPOSAL_MUTATION=NONE
RELATION_MUTATION=NONE
MATERIAL_MUTATION=NONE
CLASSIFICATION_MUTATION=NONE
TEMPORAL_MUTATION=NONE
PROVENANCE_MUTATION=NONE
KNOWLEDGE_STATUS_MUTATION=NONE

APPROVAL_VS_TRUTH=PASS
APPROVAL_VS_AUTHORITY=PASS
APPROVAL_VS_PROPOSAL_ORIGIN=PASS
APPROVAL_VS_CANONICAL_KNOWLEDGE=PASS

CANONICAL_ELIGIBILITY=
APPROVED_ONLY

AI_APPROVAL=FORBIDDEN
AI_CALLS=0

R10_BOUNDARY=PASS

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
V4_R8_REGRESSION=PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW

PRODUCTION_BEHAVIOR_CHANGED=V4_ADDITIVE_ONLY

DECISION=V4_R9_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R9
```

---

# Critical R10 Boundary

R9 ends with:

```text
ApprovalDecision(
    decision=APPROVED
)
```

That means only:

```text
proposal eligible for canonical composition
```

It does NOT mean:

```text
KnowledgeStatement created
canonical Knowledge Source updated
human documentation generated
Plugin knowledge generated
```

Those belong to:

```text
V4-R10 — Canonical Knowledge Composition
```

---

# Out of Scope

Do NOT implement:

* authentication;
* RBAC;
* multiple approval roles;
* AI approval;
* system approval;
* automatic approval/rejection;
* canonical knowledge composition;
* KnowledgeStatement creation from approval;
* relation resolution;
* material mutation;
* proposal text mutation;
* automatic corrected proposal generation;
* notifications;
* persistence/database;
* workflow engine;
* R10–R14;
* V5.

---

# Stop Condition

STOP after:

1. implementing the Technical Lead decision model;
2. enforcing READY_FOR_REVIEW precondition;
3. implementing APPROVED / REJECTED / CORRECTION_REQUESTED;
4. preserving proposal immutability;
5. preserving decision history;
6. implementing deterministic decision identity;
7. implementing canonical eligibility without composition;
8. proving no automatic decision path exists;
9. proving AI/system cannot approve;
10. generating deterministic contract/example artifacts;
11. running full regression;
12. confirming readiness;
13. creating the R9 result;
14. updating PROJECT_STATE pending Technical Lead review.

Do NOT:

```text
approve R9
commit
push
begin R10
```

Wait for Technical Lead review.

Expected final state:

```text
V4_R9=READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R9
```
