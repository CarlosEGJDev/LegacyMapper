# LegacyMapper V4 — R10 Canonical Knowledge Composition

TASK=V4_R10_CANONICAL_KNOWLEDGE_COMPOSITION

MODE=DETERMINISTIC_CANONICAL_COMPOSITION

IMPLEMENTATION_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

Implement the first V4 layer that composes approved proposals into the Canonical Knowledge Source.

R10 begins only after explicit Technical Lead approval exists in R9.

The pipeline is:

```text
Material / Evidence / Relations
            ↓
         Proposal
            ↓
Technical Lead Approval
            ↓
APPROVED + eligible_for_R10
            ↓
Canonical Knowledge Composition   <- R10
            ↓
Canonical Knowledge Source
```

R10 must remain deterministic.

No AI may decide what enters canonical knowledge.

---

# Fundamental Rule

R10 may compose only proposals that already have an explicit R9 decision:

```text
ApprovalDecisionType.APPROVED
```

Required:

```text
NO_APPROVAL -> NO_CANONICAL_COMPOSITION

REJECTED -> NOT_ELIGIBLE

CORRECTION_REQUESTED -> NOT_ELIGIBLE

APPROVED -> ELIGIBLE
```

Eligibility is necessary but composition must still validate all structural invariants.

---

# Core Distinctions

Required:

```text
INPUT MATERIAL != CANONICAL KNOWLEDGE

EVIDENCE != CANONICAL KNOWLEDGE

RELATION != CANONICAL KNOWLEDGE

PROPOSAL != CANONICAL KNOWLEDGE

APPROVAL != CANONICAL KNOWLEDGE

ELIGIBLE != COMPOSED

COMPOSED KNOWLEDGE != PROJECTION

CANONICAL SOURCE != HUMAN DOCUMENT

CANONICAL SOURCE != PLUGIN PAYLOAD
```

R10 owns canonical composition.

R11 and R12 only project it.

---

# One Canonical Knowledge Source

V4 must maintain one logical approved Canonical Knowledge Source.

Do NOT create separate truth stores such as:

```text
human_truth
plugin_truth
technical_truth
functional_truth
AI_truth
```

Instead:

```text
Canonical Knowledge Source
        ↓
   ┌────┴────┐
   ↓         ↓
R11 docs   R12 Plugin
```

R11 and R12 must later consume the same canonical source.

---

# Required Baseline

Before implementation require:

```text
latest_completed_round = V4-R9
latest_approved_round = V4-R9

current_round_in_progress = null

round_status = V4-R9_APPROVED

next = V4-R10

tests >= 1098
readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

If R9 is not formally closed:

STOP.

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
9. `docs/V4/V4_R9_TECHNICAL_LEAD_APPROVAL_RESULT.md`
10. `docs/V4/V4_R9_CLOSURE_AND_VERSIONING_RESULT.md`
11. `output/v4_r8/V4_PROPOSAL_LIFECYCLE_CONTRACT.json`
12. `output/v4_r9/V4_TECHNICAL_LEAD_APPROVAL_CONTRACT.json`
13. `docs/V4/V4_R3_PROVENANCE_RESULT.md`
14. `output/v4_r3/V4_PROVENANCE_CONTRACT.json`
15. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
16. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Inspect:

```text
legacy_documenter/knowledge/domain/
legacy_documenter/knowledge/proposals/
legacy_documenter/knowledge/approval/
legacy_documenter/knowledge/provenance/
```

Prefer composition over modification of already-approved modules.

---

# Entry Gate

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=1098 PASS
```

Run readiness.

Require:

```text
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

---

# Scope

Implement:

```text
canonical composition model
canonical entry model
eligibility validation
proposal + approval composition
canonical collection/source
duplicate/idempotency rules
lineage/provenance references
deterministic serialization
canonical contract artifact
canonical example artifact
```

Do NOT implement:

```text
R11 markdown/document rendering
R12 Plugin-facing payload
AI interpretation
automatic approval
automatic conflict resolution
source extraction redesign
V5 technology agnosticism
```

---

# Canonical Entry

Introduce a small source-neutral immutable canonical record.

Conceptually:

```text
CanonicalKnowledgeEntry
    knowledge_id
    statement
    source_type
    nature
    status
    temporal_state?
    evidence_refs
    provenance?
    related_statement_ids
    approval
    proposal_id
    approval_decision_id
    metadata
```

Exact shape may reuse or compose R1 `KnowledgeStatement`.

Do NOT duplicate domain concepts unnecessarily.

Preferred direction:

```text
R8 Proposal
+ R9 ApprovalDecision(APPROVED)
+ referenced contextual domain data
        ↓
R1-compatible KnowledgeStatement
        ↓
CanonicalKnowledgeEntry / canonical collection
```

If `KnowledgeStatement` already cleanly represents the final knowledge object, reuse it rather than inventing a parallel domain truth object.

But canonical membership itself must remain explicit.

---

# Critical Identity Rule

Canonical identity must be deterministic.

Suggested prefix:

```text
KNO-
```

or reuse existing `KST-` if the existing R1 contract already defines the canonical statement identity semantics cleanly.

Do NOT create a competing identity system without justification.

Identity must derive from immutable semantic content.

Never use:

```text
random UUID
current time
memory address
machine identity
filesystem path
```

---

# Proposal Traceability

Every canonical entry created from R10 must retain direct traceability to:

```text
proposal_id
approval_decision_id
```

and indirectly preserve:

```text
material basis
relation basis
evidence basis
proposal method
proposal origin
```

where available.

Approval must never erase proposal origin.

Example:

```text
AI_PROPOSED
    ↓
TECHNICAL_LEAD APPROVED
    ↓
Canonical Entry
```

must retain both facts:

```text
origin = AI_PROPOSED
approval = TECHNICAL_LEAD
```

They are orthogonal.

---

# Eligibility Validation

R10 must consume R9 eligibility semantics.

Composition allowed only when:

```text
proposal.status = READY_FOR_REVIEW
AND
approval.proposal_id = proposal.proposal_id
AND
approval.decision = APPROVED
AND
approval.authority = TECHNICAL_LEAD
```

Rejected:

```text
no approval
REJECTED
CORRECTION_REQUESTED
approval for different proposal
non-READY proposal
```

No automatic repair.

---

# Canonical Status

Do not reuse approval status as knowledge status.

Required:

```text
APPROVED decision
!=
KnowledgeStatus
```

Knowledge status must continue to represent the semantic state of the knowledge claim.

For example:

```text
CONFIRMED
INTERPRETED
PARTIAL
UNRESOLVED
MISSING
CONFLICTING
SUPERSEDED
```

Approval records who accepted incorporation.

KnowledgeStatus describes the knowledge itself.

Do not collapse these.

---

# Source Type and Nature

R10 must preserve:

```text
SourceType
KnowledgeNature
```

from explicit proposal/composition input.

Do not infer these from free text.

Do not silently assign:

```text
DETERMINISTIC_CODE_FACT
```

merely because code exists.

Code remains optional.

---

# Temporal State

Preserve explicit temporal state:

```text
AS_IS
TO_BE
HISTORICAL
```

If absent:

do not infer.

Do not convert AS_IS/TO_BE difference into conflict automatically.

Do not mark HISTORICAL as SUPERSEDED automatically.

---

# Evidence Rule

Canonical knowledge must preserve evidence references.

Do not invent evidence.

Where the target knowledge status requires authoritative evidence under the R1 contract, maintain that invariant.

In particular:

```text
CONFIRMED
```

must continue to satisfy its existing authoritative-evidence rule.

R10 must not weaken R1 invariants merely because a proposal was approved.

Technical Lead approval and evidence authority are separate dimensions.

---

# Provenance

R10 must preserve traceability rather than erase intermediate stages.

Conceptually:

```text
SOURCE
 ↓
MATERIAL
 ↓
EVIDENCE
 ↓
INTERPRETATION / RELATION
 ↓
PROPOSAL
 ↓
APPROVAL
 ↓
CANONICAL KNOWLEDGE
```

Do not rewrite R3's approved provenance model unnecessarily.

If R3 does not model approval as a graph node, do not silently modify the R3 taxonomy merely to force it.

Instead ensure canonical entries carry enough stable references to reconstruct the chain.

Any provenance extension that requires changing an approved R3 enum must be explicitly justified in the result and preferably deferred unless strictly required.

---

# Canonical Collection

Provide a deterministic in-memory canonical source/collection.

Suggested capabilities:

```text
compose
add
get
list
contains
by_source_type
by_nature
by_status
by_temporal_state
by_proposal_id
```

Keep the API small.

No database.

---

# Idempotency

Composing the exact same approved proposal more than once:

```text
IDEMPOTENT_NO_OP
```

It must not create duplicate canonical entries.

A conflicting attempt to use the same canonical identity with incompatible semantics:

```text
REJECT
```

No silent overwrite.

---

# One Approved Proposal, One Canonical Entry

Default V4 rule:

```text
one approved immutable proposal version
→ at most one canonical entry
```

Do not split one proposal into multiple canonical facts automatically.

If a proposal is too broad, correction/splitting should happen before approval.

R10 must not reinterpret proposal content.

---

# Supersession

Do not automatically supersede existing canonical knowledge merely because:

```text
new proposal approved
newer date exists
TO_BE exists
similar statement exists
```

Supersession must be explicit.

If supported in R10, it must use explicit identifiers and preserve history.

No physical deletion.

---

# Conflict Handling

R10 must not resolve R7 conflicts automatically.

If an approved proposal represents a resolution, canonical composition may incorporate the approved resolution statement.

But do not mutate historical `KnowledgeRelation`.

Required:

```text
CONFLICT HISTORY PRESERVED
```

---

# Gap Handling

Likewise:

```text
GAP != automatically filled
```

An approved knowledge-addition/migration proposal can produce canonical knowledge, but the R7 GAP relation remains historical evidence.

---

# Canonical Source Mutability

Prefer immutable entries and append-oriented deterministic collection behavior.

No hidden rewrite.

No silent merge.

No fuzzy deduplication.

---

# Composition Request

Prefer an explicit request object, conceptually:

```text
CanonicalCompositionRequest
    proposal
    approval_decision
    source_type
    nature
    knowledge_status
    temporal_state?
    evidence_refs?
    provenance?
    related_statement_ids?
    metadata?
```

Exact design may differ.

Important:

All semantic values required to construct canonical knowledge must be explicit or already present in immutable upstream records.

Do not derive missing semantic values from free text.

---

# AI Boundary

R10 makes no AI/provider calls.

Expected:

```text
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

No AI may:

```text
decide canonical inclusion
infer approval
select a winning conflict side
invent evidence
infer source type
infer nature
infer temporal state
upgrade status
```

---

# Security

Treat:

```text
statement
metadata
evidence descriptions
human-originated fields
```

as untrusted data.

Reuse existing sanitizer.

Prompt-injection-shaped content remains inert.

No:

```text
eval
exec
dynamic import
shell execution
template execution
```

---

# No External I/O

R10 domain/service layer must not:

```text
read source files
scan directories
query database
call provider
call network
invoke Git
write external systems
```

It operates on explicit in-memory domain records.

Artifact generators may deterministically render contract/example JSON under the established project pattern.

---

# Suggested Package

Prefer:

```text
legacy_documenter/
└── knowledge/
    └── canonical/
```

Possible files:

```text
canonical/
├── __init__.py
├── models.py
├── service.py
├── contract_report.py
└── example_report.py
```

Add enums only if genuinely required.

Do not create excessive abstractions.

Follow the Python development standard.

---

# Contract Artifact

Generate:

```text
output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_CONTRACT.json
```

Document at minimum:

```text
contract_kind
schema_version
module

canonical_model
canonical_identity_policy

eligibility_policy
approval_requirements

proposal_traceability_policy
approval_traceability_policy
evidence_policy
provenance_policy

source_type_policy
knowledge_nature_policy
knowledge_status_policy
temporal_state_policy

duplicate_policy
idempotency_policy

supersession_policy
conflict_policy
gap_policy

proposal_mutation_policy
approval_mutation_policy
relation_mutation_policy
material_mutation_policy

canonical_source_policy

R11_boundary
R12_boundary

AI_boundary
security_policy
external_io_policy
```

Include explicit semantic statements equivalent to:

```text
NO_APPROVAL_NO_CANONICAL_COMPOSITION

REJECTED_NOT_ELIGIBLE
CORRECTION_REQUESTED_NOT_ELIGIBLE

APPROVED_IS_ELIGIBLE_NOT_AUTOMATICALLY_COMPOSED

ONE_CANONICAL_KNOWLEDGE_SOURCE

CANONICAL_ENTRY_RETAINS_PROPOSAL_ID
CANONICAL_ENTRY_RETAINS_APPROVAL_DECISION_ID

APPROVAL_DOES_NOT_ERASE_ORIGIN

APPROVAL_STATUS_DOES_NOT_REPLACE_KNOWLEDGE_STATUS

R10_DOES_NOT_RESOLVE_RELATIONS_AUTOMATICALLY

R11_AND_R12_ARE_PROJECTIONS_OF_THE_SAME_CANONICAL_SOURCE

AI_NEVER_DECIDES_CANONICAL_INCLUSION
```

---

# Example Artifact

Generate:

```text
output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_EXAMPLE.json
```

Synthetic examples only.

Include:

## Example 1 — Approved human proposal

Show:

```text
Proposal READY_FOR_REVIEW
Approval APPROVED / TECHNICAL_LEAD
Composition succeeds
canonical entry created
proposal id retained
approval decision id retained
```

---

## Example 2 — Approved AI-origin proposal

Show:

```text
proposal_method = AI_PROPOSED
approval = TECHNICAL_LEAD APPROVED
canonical entry created

AI_ORIGIN_PRESERVED = true
HUMAN_APPROVAL_PRESERVED = true
AI_APPROVAL = false
```

---

## Example 3 — Rejected proposal

Expected:

```text
composition rejected
canonical entry created = false
```

---

## Example 4 — Correction requested

Expected:

```text
composition rejected
canonical entry created = false
```

---

## Example 5 — No approval

Expected:

```text
composition rejected
canonical entry created = false
```

---

## Example 6 — Duplicate approved proposal

Compose twice.

Expected:

```text
canonical_count = 1
IDEMPOTENT_NO_OP
```

---

## Example 7 — CONFIRMED without required authoritative evidence

Expected:

```text
REJECTED_BY_VALIDATION
```

Approval must not bypass R1 evidence rules.

---

## Example 8 — AS_IS / TO_BE coexistence

Show two explicitly approved entries with different temporal states can coexist without automatic conflict/supersession.

---

# Required Tests

Add deterministic tests covering at minimum:

### Entry Gate

R9 approved and closed.

---

### Eligibility

APPROVED succeeds.

REJECTED fails.

CORRECTION_REQUESTED fails.

No decision fails.

Approval for another proposal fails.

---

### Technical Lead authority

Only valid R9-approved authority accepted.

No AI/system fabricated approval.

---

### Proposal state

Only expected reviewed proposal version may compose.

---

### Canonical identity

Stable deterministic id.

No time/randomness.

---

### Traceability

Canonical entry retains:

```text
proposal_id
approval_decision_id
```

---

### Origin preservation

AI_PROPOSED remains AI_PROPOSED after human approval/composition.

Human approval remains separately visible.

---

### Knowledge status separation

Approval does not force:

```text
CONFIRMED
```

or any other KnowledgeStatus.

---

### Evidence invariants

CONFIRMED authoritative evidence rule remains enforced.

No invented evidence.

---

### Source-neutral behavior

No source-code fields required.

Test a human-information-only canonical entry.

---

### Temporal behavior

None is not inferred.

AS_IS/TO_BE do not auto-conflict.

HISTORICAL does not auto-SUPERSEDE.

---

### Relations

No mutation of GAP/CONFLICT/DIFFERENCE/TEMPORAL_EVOLUTION.

---

### Proposal immutability

No mutation.

---

### Approval immutability

No mutation.

---

### Duplicate/idempotency

Exact recomposition is idempotent.

Conflicting duplicate rejected.

---

### One proposal → one canonical entry

No automatic splitting.

---

### Security

Sanitization.

Prompt injection inert.

No secret leakage through exceptions.

---

### No I/O

No file/network/database/provider/Git I/O from composition service.

---

### AI Boundary

Zero LLM/provider calls.

---

### R11/R12 Boundary

No markdown documentation generation.

No Plugin-facing contract generation.

Only canonical domain/composition artifacts.

---

### Determinism

Contract byte-identical across repeated generation.

Example byte-identical across repeated generation.

---

### Regression

Run full suite.

Expected:

```text
>1098 PASS
```

Report exact count.

---

# Final Regression

Run:

```text
python -m unittest discover -s tests
```

Then readiness.

Require:

```text
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

Important:

R10 creates V4 canonical composition infrastructure, but this round must NOT generate the future project-wide AI knowledge artifact that V3 intentionally left blocked.

Therefore:

```text
AI_KNOWLEDGE_GENERATED=false
```

must remain true unless an already-approved repository contract explicitly defines that flag differently.

Do not reinterpret the flag silently.

---

# PROJECT_STATE Update

After successful implementation:

```text
latest_completed_round = V4-R10
latest_approved_round = V4-R9

current_round_in_progress =
"V4-R10 (pending Technical Lead review)"

round_status =
V4-R10_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R10

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do NOT approve R10.

---

# Required Result

Create:

```text
docs/V4/V4_R10_CANONICAL_KNOWLEDGE_COMPOSITION_RESULT.md
```

Report at minimum:

```text
STATUS
ENTRY_GATE
BASELINE_TESTS
FINAL_TESTS

CANONICAL_MODEL
CANONICAL_IDENTITY

ELIGIBILITY_POLICY
APPROVAL_REQUIREMENTS

CANONICAL_SOURCE_POLICY

PROPOSAL_TRACEABILITY
APPROVAL_TRACEABILITY
ORIGIN_PRESERVATION

SOURCE_TYPE_POLICY
KNOWLEDGE_NATURE_POLICY
KNOWLEDGE_STATUS_POLICY
TEMPORAL_STATE_POLICY

EVIDENCE_POLICY
PROVENANCE_POLICY

DUPLICATE_POLICY
IDEMPOTENCY_POLICY

SUPERSESSION_POLICY
CONFLICT_POLICY
GAP_POLICY

PROPOSAL_MUTATION
APPROVAL_MUTATION
RELATION_MUTATION
MATERIAL_MUTATION

AI_CALLS
AI_CANONICAL_DECISION

R11_BOUNDARY
R12_BOUNDARY

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
V4_R9_REGRESSION

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

Include:

```text
## Reused Components
## New Components
## Canonical Composition Invariants
## Eligibility
## Traceability
## Evidence and Provenance
## Identity and Idempotency
## Origin Preservation
## Canonical Source Boundary
## R11 Boundary
## R12 Boundary
## AI Boundary
## Security Notes
## Out of Scope
```

---

# Expected Success State

```text
STATUS=V4_R10_CANONICAL_KNOWLEDGE_COMPOSITION_COMPLETE
ENTRY_GATE=PASS

BASELINE_TESTS=1098_PASS
FINAL_TESTS=>1098_PASS

ELIGIBILITY_POLICY=APPROVED_ONLY
APPROVAL_AUTHORITY=TECHNICAL_LEAD

ONE_CANONICAL_KNOWLEDGE_SOURCE=PASS

CANONICAL_IDENTITY=DETERMINISTIC

PROPOSAL_TRACEABILITY=PRESERVED
APPROVAL_TRACEABILITY=PRESERVED
ORIGIN_PRESERVATION=PASS

APPROVAL_DOES_NOT_REPLACE_KNOWLEDGE_STATUS=PASS

CONFIRMED_EVIDENCE_INVARIANT=PRESERVED

DUPLICATE_POLICY=DETERMINISTIC
IDEMPOTENCY=PASS

AUTOMATIC_SUPERSESSION=NONE
AUTOMATIC_CONFLICT_RESOLUTION=NONE
AUTOMATIC_GAP_RESOLUTION=NONE

PROPOSAL_MUTATION=NONE
APPROVAL_MUTATION=NONE
RELATION_MUTATION=NONE
MATERIAL_MUTATION=NONE

AI_CANONICAL_DECISION=FORBIDDEN
AI_CALLS=0

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

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
V4_R9_REGRESSION=PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW

PRODUCTION_BEHAVIOR_CHANGED=V4_ADDITIVE_ONLY

DECISION=V4_R10_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_R10
```

---

# Critical Boundary

R10 may produce:

```text
Canonical Knowledge Source
```

but must NOT yet produce either final projection:

```text
R11 Human-readable documents
R12 Plugin-facing machine-readable output
```

Those must remain projections over the same canonical source.

---

# Out of Scope

Do NOT implement:

* R11 document projection;
* R12 Plugin-facing projection;
* multiple canonical stores;
* RBAC;
* AI approval;
* AI canonical inclusion decisions;
* automatic classification;
* automatic status promotion;
* automatic conflict resolution;
* automatic gap resolution;
* fuzzy deduplication;
* database persistence;
* workflow engine;
* external notifications;
* source scanner redesign;
* V5.

---

# Stop Condition

STOP after:

1. implementing deterministic canonical composition;
2. enforcing R9 APPROVED eligibility;
3. preserving proposal and approval traceability;
4. preserving source origin;
5. preserving R1 evidence/status invariants;
6. implementing one canonical source;
7. implementing deterministic identity/idempotency;
8. proving no automatic conflict/gap/supersession behavior;
9. proving no AI/provider decision path;
10. generating deterministic contract/example artifacts;
11. running full regression;
12. confirming readiness;
13. creating the R10 result;
14. updating PROJECT_STATE pending Technical Lead review.

Do NOT:

```text
approve R10
commit
push
begin R11
```

Expected:

```text
V4_R10=READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R10
```
