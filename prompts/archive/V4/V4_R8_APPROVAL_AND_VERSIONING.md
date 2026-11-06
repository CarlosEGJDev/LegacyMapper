# LegacyMapper V4 — R8 Approval, Closure and Versioning

TASK=V4_R8_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false

R9_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false

PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true

GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

```text
V4-R8 — Proposal Lifecycle
```

The reviewed artifacts include:

```text
docs/V4/V4_R8_PROPOSAL_LIFECYCLE_RESULT.md

output/v4_r8/V4_PROPOSAL_LIFECYCLE_CONTRACT.json

output/v4_r8/V4_PROPOSAL_LIFECYCLE_EXAMPLE.json
```

This approval comes from the Technical Lead.

The development agent MUST NOT independently grant, reinterpret, expand, or replace that approval.

This task only:

```text
verifies
records
closes
versions
pushes
```

the already-reviewed R8 checkpoint.

Do NOT modify reviewed R8 semantics.

Do NOT begin R9.

---

# Required Reading

Before changing anything read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_PROPOSED_ROADMAP.md`
7. `docs/V4/V4_R7_CLOSURE_AND_VERSIONING_RESULT.md`
8. `docs/V4/V4_R8_PROPOSAL_LIFECYCLE_RESULT.md`
9. `output/v4_r8/V4_PROPOSAL_LIFECYCLE_CONTRACT.json`
10. `output/v4_r8/V4_PROPOSAL_LIFECYCLE_EXAMPLE.json`
11. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
12. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Do not reinterpret previous approvals.

---

# Expected Pre-Closure State

Verify:

```text
latest_completed_round = V4-R8
latest_approved_round = V4-R7

current_round_in_progress =
"V4-R8 (pending Technical Lead review)"

round_status =
V4-R8_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R8
```

Expected baseline:

```text
tests >= 1022
readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

If this does not match the reviewed R8 checkpoint:

STOP.

Do not silently reconcile discrepancies.

---

# Reviewed R8 Integrity Values

## Contract

Expected:

```text
R8_CONTRACT_SHA256=
56778b6c3cf92267fe4a501851668422bd646ef414f20d0c100216ecf699c91c
```

Artifact:

```text
output/v4_r8/V4_PROPOSAL_LIFECYCLE_CONTRACT.json
```

Required:

```text
R8_CONTRACT_INTEGRITY=PASS
```

---

## Example

Expected:

```text
R8_EXAMPLE_SHA256=
018f056bcd9e49a8c2adf260d78171de62beaae48567668ead7a3a6aa565cc32
```

Artifact:

```text
output/v4_r8/V4_PROPOSAL_LIFECYCLE_EXAMPLE.json
```

Required:

```text
R8_EXAMPLE_INTEGRITY=PASS
```

If either differs:

STOP.

Do not repair and approve in the same closure task.

---

# Reviewed R8 Semantics

Do not change the reviewed implementation.

Approved proposal kinds:

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

Approved proposal statuses:

```text
DRAFT
READY_FOR_REVIEW
WITHDRAWN
SUPERSEDED
```

Approved proposal methods:

```text
HUMAN_PROPOSED
DETERMINISTIC_RULE
AI_PROPOSED
```

Critical invariants:

```text
PROPOSAL != APPROVAL
PROPOSAL != DECISION
PROPOSAL != TRUTH
PROPOSAL != AUTHORITY
PROPOSAL != CANONICAL KNOWLEDGE
PROPOSAL != IMPLEMENTATION

READY_FOR_REVIEW != APPROVED

HUMAN_PROPOSED != APPROVED
DETERMINISTIC_RULE != APPROVED
AI_PROPOSED != APPROVED

CONFLICT != automatic RESOLUTION proposal
GAP != automatic MIGRATION proposal

PROPOSAL does not resolve RELATION
PROPOSAL does not mutate SOURCE MATERIAL
```

Approved boundary:

```text
R8 ends at READY_FOR_REVIEW
R9 owns Technical Lead approval
R10 owns Canonical Knowledge Composition
```

Do not alter any of these during closure.

---

# Regression Validation

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=1022 PASS
```

Report exact final count.

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

If validation fails:

STOP.

Do not close R8.

---

# Register Human Approval

Update:

```text
PROJECT_STATE.json
```

using its existing schema.

Required final state:

```text
latest_completed_round = V4-R8
latest_approved_round = V4-R8

current_round_in_progress = null

round_status = V4-R8_APPROVED

next = V4-R9

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do not redesign the state schema.

---

# Append Closure to R8 Result

Append only a closure section to:

```text
docs/V4/V4_R8_PROPOSAL_LIFECYCLE_RESULT.md
```

Equivalent to:

```text
## Closure — Human Approval Recorded

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

ROUND_STATUS=APPROVED

DECISION=V4_R8_FORMALLY_APPROVED

NEXT=V4-R9
```

Do not rewrite the reviewed result.

The development agent must not claim it granted approval.

---

# Do Not Modify Reviewed Implementation

Do not change:

```text
legacy_documenter/knowledge/proposals/

tests/test_v4_r8_proposal_lifecycle.py

output/v4_r8/V4_PROPOSAL_LIFECYCLE_CONTRACT.json

output/v4_r8/V4_PROPOSAL_LIFECYCLE_EXAMPLE.json
```

If an integrity failure exists:

STOP.

Do not repair and approve within the same task.

---

# Git Safety

Before staging inspect:

```text
git status
git diff
git diff --stat
```

Confirm no unrelated user work exists.

Do not:

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

No force push.

No history rewrite.

---

# Secret and Artifact Safety

Before commit verify:

```text
SECRET_SCAN=PASS
```

Ensure:

* no credentials;
* no `.env`;
* no API keys;
* no tokens;
* no accidental heavy output;
* `.gitignore` policy respected;
* repository continuity contract respected.

---

# Closure Result

Create:

```text
docs/V4/V4_R8_CLOSURE_AND_VERSIONING_RESULT.md
```

Report at minimum:

```text
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

R8_CONTRACT_SHA256
R8_CONTRACT_INTEGRITY

R8_EXAMPLE_SHA256
R8_EXAMPLE_INTEGRITY

TESTS
READINESS

AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE

R8_IMPLEMENTATION_INCLUDED
R8_TESTS_INCLUDED
R8_ARTIFACTS_INCLUDED
R8_PROMPTS_INCLUDED

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

# Expected R8 Checkpoint Files

Stage the reviewed checkpoint and closure artifacts, including as applicable:

```text
legacy_documenter/knowledge/proposals/

tests/test_v4_r8_proposal_lifecycle.py

output/v4_r8/V4_PROPOSAL_LIFECYCLE_CONTRACT.json

output/v4_r8/V4_PROPOSAL_LIFECYCLE_EXAMPLE.json

docs/V4/V4_R8_PROPOSAL_LIFECYCLE_RESULT.md

prompts/V4/V4_R8_PROPOSAL_LIFECYCLE.md

prompts/V4/V4_R8_APPROVAL_AND_VERSIONING.md

PROJECT_STATE.json

docs/V4/V4_R8_CLOSURE_AND_VERSIONING_RESULT.md
```

Inspect:

```text
git diff --cached
git diff --cached --stat
```

No unrelated files.

---

# Commit

Preferred commit:

```text
Approve and close LegacyMapper V4-R8
```

One normal commit.

No amend.

No squash.

No history rewrite.

---

# Push

Push current branch to configured remote:

```text
origin
```

No force push.

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

A fresh development agent must be able to determine:

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

readiness = READY

next = V4-R9
```

---

# Expected Success State

```text
STATUS=V4_R8_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R8_CONTRACT_SHA256=
56778b6c3cf92267fe4a501851668422bd646ef414f20d0c100216ecf699c91c

R8_CONTRACT_INTEGRITY=PASS

R8_EXAMPLE_SHA256=
018f056bcd9e49a8c2adf260d78171de62beaae48567668ead7a3a6aa565cc32

R8_EXAMPLE_INTEGRITY=PASS

TESTS=>=1022_PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_R8_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_R8_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4-R9
```

---

# Stop Condition

STOP after:

1. verifying reviewed R8 artifact integrity;
2. running regression/readiness;
3. recording Technical Lead approval;
4. updating `PROJECT_STATE.json`;
5. appending closure to the R8 result;
6. creating the closure/versioning result;
7. staging only R8/closure artifacts;
8. committing;
9. pushing;
10. confirming clean Git state;
11. confirming repository continuity.

Do NOT implement:

```text
V4-R9
```

Expected final state:

```text
V4_R8=FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4-R9
```
