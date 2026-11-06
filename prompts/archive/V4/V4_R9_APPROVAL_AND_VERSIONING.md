# LegacyMapper V4 — R9 Approval, Closure and Versioning

TASK=V4_R9_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
R10_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

```text
V4-R9 — Technical Lead Approval
```

The development agent MUST NOT grant or reinterpret this approval.

This task only verifies, records, closes, commits and pushes the already-reviewed R9 checkpoint.

Do NOT modify R9 semantics.

Do NOT begin R10.

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_PROPOSED_ROADMAP.md`
7. `docs/V4/V4_R8_CLOSURE_AND_VERSIONING_RESULT.md`
8. `docs/V4/V4_R9_TECHNICAL_LEAD_APPROVAL_RESULT.md`
9. `output/v4_r9/V4_TECHNICAL_LEAD_APPROVAL_CONTRACT.json`
10. `output/v4_r9/V4_TECHNICAL_LEAD_APPROVAL_EXAMPLE.json`
11. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
12. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

---

# Expected Pre-Closure State

Verify:

```text
latest_completed_round = V4-R9
latest_approved_round = V4-R8

current_round_in_progress =
"V4-R9 (pending Technical Lead review)"

round_status =
V4-R9_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R9

tests = 1098
readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

If this does not match:

STOP.

Do not reconcile discrepancies silently.

---

# Reviewed Artifact Integrity

Expected contract:

```text
output/v4_r9/V4_TECHNICAL_LEAD_APPROVAL_CONTRACT.json
SHA256=f222d6f6440297c8f9838b1e2227059b72441f4f9a50b9fae5f8a23331563ef9
```

Expected example:

```text
output/v4_r9/V4_TECHNICAL_LEAD_APPROVAL_EXAMPLE.json
SHA256=b5cc1c3152c3db97712643fd946c45a63b22197e51c1593d5a37a086b59c6fa3
```

Required:

```text
R9_CONTRACT_INTEGRITY=PASS
R9_EXAMPLE_INTEGRITY=PASS
```

If either differs:

STOP.

Do not repair and approve in the same task.

---

# Reviewed R9 Semantics

Do not change:

```text
DECISION_TYPES =
APPROVED
REJECTED
CORRECTION_REQUESTED
```

Authority:

```text
TECHNICAL_LEAD
```

Precondition:

```text
READY_FOR_REVIEW_ONLY
```

Approved re-decision policy:

```text
ONE_DECISION_PER_PROPOSAL_ID
```

This policy is intentionally accepted by the Technical Lead.

After `CORRECTION_REQUESTED`, further review must use a new distinct R8 proposal version.

Critical invariants:

```text
PROPOSAL != DECISION
READY_FOR_REVIEW != APPROVED

APPROVED != CANONICALIZED
REJECTED != FALSE
CORRECTION_REQUESTED != REJECTED

AI_PROPOSED != AI_APPROVED
HUMAN_PROPOSED != HUMAN_APPROVED

R9_RECORDS_HUMAN_AUTHORITY
R9_DOES_NOT_CREATE_HUMAN_AUTHORITY

APPROVED_ONLY_MAKES_PROPOSAL_ELIGIBLE_FOR_R10
R10_OWNS_CANONICAL_KNOWLEDGE_COMPOSITION
```

Do not alter these.

---

# Regression Validation

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=1098 PASS
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

If validation fails:

STOP.

---

# Register Technical Lead Approval

Update `PROJECT_STATE.json` using the existing schema.

Required final state:

```text
latest_completed_round = V4-R9
latest_approved_round = V4-R9

current_round_in_progress = null

round_status = V4-R9_APPROVED

next = V4-R10

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do not redesign the state schema.

---

# Append Closure to R9 Result

Append only a closure section to:

```text
docs/V4/V4_R9_TECHNICAL_LEAD_APPROVAL_RESULT.md
```

Equivalent to:

```text
## Closure — Human Approval Recorded

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

ROUND_STATUS=APPROVED

DECISION=V4_R9_FORMALLY_APPROVED

NEXT=V4-R10
```

Do not rewrite the reviewed result.

---

# Do Not Modify Reviewed Implementation

Do not modify:

```text
legacy_documenter/knowledge/approval/

tests/test_v4_r9_technical_lead_approval.py

output/v4_r9/V4_TECHNICAL_LEAD_APPROVAL_CONTRACT.json

output/v4_r9/V4_TECHNICAL_LEAD_APPROVAL_EXAMPLE.json
```

If integrity differs:

STOP.

---

# Git Safety

Inspect:

```text
git status
git diff
git diff --stat
```

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

No history rewrite.

---

# Security

Verify:

```text
SECRET_SCAN=PASS
```

No real credentials, tokens, `.env`, private keys, or unrelated heavy artifacts may be committed.

---

# Closure Result

Create:

```text
docs/V4/V4_R9_CLOSURE_AND_VERSIONING_RESULT.md
```

Report at minimum:

```text
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

R9_CONTRACT_SHA256
R9_CONTRACT_INTEGRITY

R9_EXAMPLE_SHA256
R9_EXAMPLE_INTEGRITY

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

# Expected R9 Checkpoint Files

Stage as applicable:

```text
legacy_documenter/knowledge/approval/

tests/test_v4_r9_technical_lead_approval.py

output/v4_r9/V4_TECHNICAL_LEAD_APPROVAL_CONTRACT.json
output/v4_r9/V4_TECHNICAL_LEAD_APPROVAL_EXAMPLE.json

docs/V4/V4_R9_TECHNICAL_LEAD_APPROVAL_RESULT.md

prompts/V4/V4_R9_TECHNICAL_LEAD_APPROVAL.md
prompts/V4/V4_R9_APPROVAL_AND_VERSIONING.md

PROJECT_STATE.json

docs/V4/V4_R9_CLOSURE_AND_VERSIONING_RESULT.md
```

Inspect staged diff before commit.

No R10 files belong in this commit.

---

# Commit

Preferred:

```text
Approve and close LegacyMapper V4-R9
```

One normal commit.

---

# Push

Push current branch to `origin`.

No force push.

If the execution environment requires explicit user authorization for the push, STOP after commit and request that explicit authorization rather than bypassing the control.

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

Repository continuity must show:

```text
V3 = FORMALLY CLOSED

V4-R1   = APPROVED
V4-R1.1 = APPROVED
V4-R2   = APPROVED
V4-R3   = APPROVED
V4-R4   = APPROVED
V4-R5   = APPROVED
V4-R6   = APPROVED
V4-R7   = APPROVED
V4-R8   = APPROVED
V4-R9   = APPROVED

readiness = READY
next = V4-R10
```

---

# Expected Success State

```text
STATUS=V4_R9_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R9_CONTRACT_INTEGRITY=PASS
R9_EXAMPLE_INTEGRITY=PASS

TESTS=>=1098_PASS
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_R9_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_R9_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4-R10
```

---

# Stop Condition

STOP after closing and versioning R9.

Do NOT implement:

```text
V4-R10
```

Expected final state:

```text
V4_R9=FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4-R10
```
