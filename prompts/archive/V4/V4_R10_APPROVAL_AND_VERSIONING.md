# LegacyMapper V4 — R10 Approval, Closure and Versioning

TASK=V4_R10_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
R10_SEMANTIC_CHANGE_ALLOWED=false
R11_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

```text
V4-R10 — Canonical Knowledge Composition
```

The Technical Lead also explicitly accepts the two documented R10 design decisions:

1. canonical identities use the `KNO-` prefix rather than reusing `KST-`;
2. `CanonicalKnowledgeEntry` is a separate frozen canonical record that reuses `KnowledgeStatement.validate()` rather than conflating R1 `ApprovalInfo` with the R9 `ApprovalDecision` model.

The development agent MUST NOT grant, reinterpret, broaden, or replace this human approval.

This task only verifies, records, closes, commits and pushes the already-reviewed R10 checkpoint.

Do NOT modify R10 semantics.

Do NOT begin R11.

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_PROPOSED_ROADMAP.md`
7. `docs/V4/V4_R9_CLOSURE_AND_VERSIONING_RESULT.md`
8. `docs/V4/V4_R10_CANONICAL_KNOWLEDGE_COMPOSITION_RESULT.md`
9. `output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_CONTRACT.json`
10. `output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_EXAMPLE.json`
11. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
12. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

---

# Expected Pre-Closure State

Verify:

```text
latest_completed_round = V4-R10
latest_approved_round = V4-R9

current_round_in_progress =
"V4-R10 (pending Technical Lead review)"

round_status =
V4-R10_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R10

tests = 1163
readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

If the semantic state differs:

STOP.

Do not reconcile silently.

---

# Reviewed Artifact Integrity

Expected contract:

```text
output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_CONTRACT.json

SHA256=
56d731d2df5d30a2f3fb57b5100d87a6211debb6c5438d7fe4d5da29dbca87f1
```

Expected example:

```text
output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_EXAMPLE.json

SHA256=
bd03870ef7e5fa7c92c93b2028ec49493e69bb5e7f20a6969395cce85a23b9f5
```

Required:

```text
R10_CONTRACT_INTEGRITY=PASS
R10_EXAMPLE_INTEGRITY=PASS
```

If either differs:

STOP.

Do not repair and approve in the same task.

---

# Approved R10 Architecture

Preserve:

```text
ONE_CANONICAL_KNOWLEDGE_SOURCE
```

Canonical composition remains:

```text
Proposal READY_FOR_REVIEW
        +
ApprovalDecision APPROVED
        +
ApprovalAuthority TECHNICAL_LEAD
        ↓
CanonicalKnowledgeEntry
```

Required distinctions:

```text
PROPOSAL != CANONICAL KNOWLEDGE
APPROVAL != CANONICAL KNOWLEDGE

ELIGIBLE != COMPOSED

APPROVED != CONFIRMED

APPROVAL STATUS != KNOWLEDGE STATUS

CANONICAL SOURCE != HUMAN DOCUMENT
CANONICAL SOURCE != PLUGIN PAYLOAD
```

---

# Approved Identity Decision

Preserve:

```text
KNO-
```

for canonical composition identity.

The Technical Lead accepts the documented rationale that canonical identity must retain proposal/approval composition identity and therefore must not simply reuse R1 `KST-` semantics.

Do not change this during closure.

---

# Approved Canonical Model Decision

Preserve:

```text
CanonicalKnowledgeEntry
```

as a separate frozen dataclass.

Continue reusing:

```text
KnowledgeStatement.validate()
```

internally for R1 structural/evidence invariants.

Do not replace the R9 `ApprovalDecision` semantics with the old R1 `ApprovalInfo`.

---

# Eligibility Invariant

Composition remains allowed only when:

```text
proposal.status == READY_FOR_REVIEW
AND
approval_decision.proposal_id == proposal.proposal_id
AND
approval_decision.decision == APPROVED
AND
approval_decision.authority == TECHNICAL_LEAD
```

Required:

```text
NO_APPROVAL -> NOT_ELIGIBLE
REJECTED -> NOT_ELIGIBLE
CORRECTION_REQUESTED -> NOT_ELIGIBLE
```

---

# Evidence Invariant

Preserve:

```text
KnowledgeStatus.CONFIRMED
```

requires authoritative evidence according to the existing R1 validation contract.

Technical Lead approval must never bypass this.

Required:

```text
APPROVED != CONFIRMED
```

---

# Traceability

Every canonical entry must continue to retain:

```text
proposal_id
approval_decision_id
```

Do not duplicate or erase upstream origin.

An AI-originated proposal approved by the Technical Lead must preserve:

```text
proposal_method = AI_PROPOSED
approval_authority = TECHNICAL_LEAD
```

as separate facts recoverable through their immutable upstream records.

---

# Temporal and Relation Semantics

Preserve:

```text
AS_IS + TO_BE
!= automatic conflict

HISTORICAL
!= automatic SUPERSEDED

CONFLICT
!= automatically resolved

GAP
!= automatically filled
```

No automatic supersession.

No automatic relation mutation.

---

# Projection Boundary

R10 ends at:

```text
Canonical Knowledge Source
```

R11 and R12 remain:

```text
Canonical Knowledge Source
        ↓
   ┌────┴────┐
   ↓         ↓
R11         R12
Human       Plugin
Projection  Projection
```

Do not implement either projection during this closure.

---

# Regression Validation

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=1163 PASS
```

Then run readiness.

Require:

```text
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

If any validation fails:

STOP.

---

# Register Technical Lead Approval

Update `PROJECT_STATE.json` using the existing schema.

Required final state:

```text
latest_completed_round = V4-R10
latest_approved_round = V4-R10

current_round_in_progress = null

round_status = V4-R10_APPROVED

next = V4-R11

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do not redesign the state schema.

---

# Append Closure to R10 Result

Append only a closure section to:

```text
docs/V4/V4_R10_CANONICAL_KNOWLEDGE_COMPOSITION_RESULT.md
```

Equivalent to:

```text
## Closure — Human Approval Recorded

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

IDENTITY_DECISION=KNO_PREFIX_APPROVED
CANONICAL_MODEL_DECISION=CANONICAL_KNOWLEDGE_ENTRY_APPROVED

ROUND_STATUS=APPROVED

DECISION=V4_R10_FORMALLY_APPROVED

NEXT=V4-R11
```

Do not rewrite the reviewed result.

---

# Do Not Modify Reviewed Implementation

Do not modify:

```text
legacy_documenter/knowledge/canonical/

tests/test_v4_r10_canonical_knowledge_composition.py

output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_CONTRACT.json

output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_EXAMPLE.json
```

If reviewed artifact integrity differs:

STOP.

---

# Git Safety

Inspect:

```text
git status
git diff
git diff --stat
```

Verify that the previous R9 documentation correction is already committed and pushed.

Do not use:

```text
git reset --hard
git clean
git checkout -- .
git restore .
git rebase
git amend
git squash
git push --force
```

---

# Security

Verify:

```text
SECRET_SCAN=PASS
```

No credentials, tokens, `.env`, private keys, or unrelated heavy artifacts may be committed.

---

# Closure Result

Create:

```text
docs/V4/V4_R10_CLOSURE_AND_VERSIONING_RESULT.md
```

Report at minimum:

```text
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

IDENTITY_DECISION
CANONICAL_MODEL_DECISION

R10_CONTRACT_SHA256
R10_CONTRACT_INTEGRITY

R10_EXAMPLE_SHA256
R10_EXAMPLE_INTEGRITY

TESTS
READINESS

AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE

GIT_STATUS_BEFORE
GIT_BRANCH
GIT_REMOTE

GIT_SAFETY
SECRET_SCAN

GIT_COMMIT
GIT_COMMIT_HASH
GIT_PUSH
GIT_STATUS_AFTER

REPOSITORY_CONTINUITY

ROUND_STATUS
DECISION
NEXT
```

---

# Expected R10 Checkpoint Files

Stage as applicable:

```text
legacy_documenter/knowledge/canonical/

tests/test_v4_r10_canonical_knowledge_composition.py

output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_CONTRACT.json
output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_EXAMPLE.json

docs/V4/V4_R10_CANONICAL_KNOWLEDGE_COMPOSITION_RESULT.md

prompts/V4/V4_R10_CANONICAL_KNOWLEDGE_COMPOSITION.md
prompts/V4/V4_R10_APPROVAL_AND_VERSIONING.md

PROJECT_STATE.json

docs/V4/V4_R10_CLOSURE_AND_VERSIONING_RESULT.md
```

Use explicit staging where practical.

Inspect staged diff before commit.

No R11 implementation file belongs in this commit.

---

# Commit

Preferred commit message:

```text
Approve and close LegacyMapper V4-R10
```

One normal commit.

No amend/squash.

---

# Push

Push current branch to `origin`.

No force push.

If explicit user authorization is required by the execution environment, STOP after commit and request it.

---

# Final Validation

After push:

```text
git status
```

Required:

```text
GIT_STATUS_AFTER=CLEAN
```

Repository must be up to date with `origin`.

---

# Repository Continuity

A fresh agent using repository artifacts alone must be able to determine:

```text
V3 = FORMALLY CLOSED

V4-R1    = APPROVED
V4-R1.1  = APPROVED
V4-R2    = APPROVED
V4-R3    = APPROVED
V4-R4    = APPROVED
V4-R5    = APPROVED
V4-R6    = APPROVED
V4-R7    = APPROVED
V4-R8    = APPROVED
V4-R9    = APPROVED
V4-R10   = APPROVED

readiness = READY
next = V4-R11
```

---

# Expected Success State

```text
STATUS=V4_R10_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

IDENTITY_DECISION=KNO_PREFIX_APPROVED
CANONICAL_MODEL_DECISION=CANONICAL_KNOWLEDGE_ENTRY_APPROVED

R10_CONTRACT_INTEGRITY=PASS
R10_EXAMPLE_INTEGRITY=PASS

TESTS=>=1163_PASS
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_R10_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_R10_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4-R11
```

---

# Stop Condition

STOP after closing and versioning R10.

Do NOT implement:

```text
V4-R11
```

Expected final state:

```text
V4_R9=FORMALLY_CLOSED_AND_CONSISTENT
V4_R10=FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4-R11
```
