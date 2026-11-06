# LegacyMapper V4 — R7 Approval, Closure and Versioning

TASK=V4_R7_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false

R8_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false

PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true

GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

```text
V4-R7 — Gap and Conflict Representation
```

The reviewed artifacts include:

```text
docs/V4/V4_R7_GAP_AND_CONFLICT_REPRESENTATION_RESULT.md

output/v4_r7/V4_GAP_CONFLICT_RELATION_CONTRACT.json

output/v4_r7/V4_GAP_CONFLICT_RELATION_EXAMPLE.json
```

This approval comes from the Technical Lead.

The development agent MUST NOT independently grant, reinterpret, expand, or replace that approval.

The purpose of this task is only to:

```text
verify
record
close
version
push
```

the already-reviewed R7 checkpoint.

Do NOT modify the reviewed R7 implementation.

Do NOT begin R8.

---

# Required Reading

Before making any change read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_PROPOSED_ROADMAP.md`
7. `docs/V4/V4_R6_CLOSURE_AND_VERSIONING_RESULT.md`
8. `docs/V4/V4_R7_GAP_AND_CONFLICT_REPRESENTATION_RESULT.md`
9. `output/v4_r7/V4_GAP_CONFLICT_RELATION_CONTRACT.json`
10. `output/v4_r7/V4_GAP_CONFLICT_RELATION_EXAMPLE.json`
11. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
12. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Do not reinterpret previous approvals.

---

# Expected Pre-Closure State

Verify:

```text
latest_completed_round = V4-R7
latest_approved_round = V4-R6

current_round_in_progress =
"V4-R7 (pending Technical Lead review)"

round_status =
V4-R7_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R7
```

Expected baseline:

```text
tests >= 928
readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

If the repository does not match the reviewed R7 state:

STOP.

Do not silently reconcile discrepancies.

---

# Reviewed R7 Integrity Values

Verify the deterministic artifacts against the reviewed values.

## Contract

Expected:

```text
R7_CONTRACT_SHA256=
a209f766b3ef1e225512ba4e26d5fd18d81cc18d34a0c52567d557778ddcc772
```

Artifact:

```text
output/v4_r7/V4_GAP_CONFLICT_RELATION_CONTRACT.json
```

Required:

```text
R7_CONTRACT_INTEGRITY=PASS
```

---

## Example

Expected:

```text
R7_EXAMPLE_SHA256=
308a2a342e1efac3e49c9d94c6965aabc3b795aeb9511f3ecbe05b25e6dd268f
```

Artifact:

```text
output/v4_r7/V4_GAP_CONFLICT_RELATION_EXAMPLE.json
```

Required:

```text
R7_EXAMPLE_INTEGRITY=PASS
```

If either deterministic artifact differs:

STOP.

Do not close R7.

---

# R7 Reviewed Semantics

Do not change the implementation or semantics already reviewed.

The approved R7 contract includes:

```text
RELATION_KINDS=
DIFFERENCE
GAP
CONFLICT
TEMPORAL_EVOLUTION
```

Core invariants:

```text
DIFFERENCE != GAP
DIFFERENCE != CONFLICT
GAP != CONFLICT

AS_IS + TO_BE
    != automatic GAP
    != automatic CONFLICT
    != automatic TEMPORAL_EVOLUTION

CONFLICT != FALSE
CONFLICT != REJECTED

GAP != MISSING
GAP != UNRESOLVED

RELATION != APPROVAL
RELATION != AUTHORITY
RELATION != PROPOSAL
RELATION != CANONICAL KNOWLEDGE
```

Approved directionality:

```text
SYMMETRIC:
DIFFERENCE
CONFLICT

DIRECTIONAL:
GAP
TEMPORAL_EVOLUTION
```

R7 semantic detection remains:

```text
NOT_PERFORMED
```

Do not alter these rules during closure.

---

# Regression Validation

Before recording approval run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=928 PASS
```

Report exact count.

Then run:

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

If regression/readiness fails:

STOP.

Do not close R7.

---

# Register Human Approval

Update:

```text
PROJECT_STATE.json
```

using its existing schema and conventions.

Required final state:

```text
latest_completed_round = V4-R7
latest_approved_round = V4-R7

current_round_in_progress = null

round_status = V4-R7_APPROVED

next = V4-R8

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do not redesign the state schema.

---

# Append Closure to R7 Result

Append a closure section to:

```text
docs/V4/V4_R7_GAP_AND_CONFLICT_REPRESENTATION_RESULT.md
```

Do not rewrite the reviewed result.

Append only something equivalent to:

```text
## Closure — Human Approval Recorded

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

ROUND_STATUS=APPROVED

DECISION=V4_R7_FORMALLY_APPROVED

NEXT=V4-R8
```

The development agent must not claim that it granted the approval.

---

# Do Not Modify Reviewed Implementation

Do not change:

```text
legacy_documenter/knowledge/relations/
tests/test_v4_r7_gap_and_conflict_representation.py
output/v4_r7/V4_GAP_CONFLICT_RELATION_CONTRACT.json
output/v4_r7/V4_GAP_CONFLICT_RELATION_EXAMPLE.json
```

unless required solely to correct a proven integrity failure.

If such a failure exists:

STOP instead.

Do not repair and approve in the same closure task.

---

# Git Safety

Before staging inspect:

```text
git status
git diff
git diff --stat
```

Confirm there is no unrelated user work.

Do not discard or overwrite user changes.

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

unless explicitly authorized by the Technical Lead.

No force push.

No history rewrite.

---

# Secret and Artifact Safety

Before committing verify:

```text
SECRET_SCAN=PASS
```

Ensure:

* no credentials;
* no `.env`;
* no access tokens;
* no API keys;
* no accidental heavy generated output;
* `.gitignore` policy respected;
* repository continuity contract respected.

Do not commit excluded historical heavy artifacts.

---

# Closure Result

Create:

```text
docs/V4/V4_R7_CLOSURE_AND_VERSIONING_RESULT.md
```

Report at minimum:

```text
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

R7_CONTRACT_SHA256
R7_CONTRACT_INTEGRITY

R7_EXAMPLE_SHA256
R7_EXAMPLE_INTEGRITY

TESTS
READINESS

AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE

R7_IMPLEMENTATION_INCLUDED
R7_TESTS_INCLUDED
R7_ARTIFACTS_INCLUDED
R7_PROMPTS_INCLUDED

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

# Files Expected in the R7 Checkpoint

Stage the reviewed R7 checkpoint and closure artifacts.

Expected files include as applicable:

```text
legacy_documenter/knowledge/relations/

tests/test_v4_r7_gap_and_conflict_representation.py

output/v4_r7/V4_GAP_CONFLICT_RELATION_CONTRACT.json

output/v4_r7/V4_GAP_CONFLICT_RELATION_EXAMPLE.json

docs/V4/V4_R7_GAP_AND_CONFLICT_REPRESENTATION_RESULT.md

prompts/V4/V4_R7_GAP_AND_CONFLICT_REPRESENTATION.md

prompts/V4/V4_R7_APPROVAL_AND_VERSIONING.md

PROJECT_STATE.json

docs/V4/V4_R7_CLOSURE_AND_VERSIONING_RESULT.md
```

Inspect staged content before committing:

```text
git diff --cached
git diff --cached --stat
```

No unrelated file may be included.

---

# Commit

Create one normal commit.

Preferred commit message:

```text
Approve and close LegacyMapper V4-R7
```

No amend.

No squash.

No history rewrite.

The closure result may report:

```text
GIT_COMMIT_HASH=SELF
```

if it is contained inside the same commit it describes.

Do not amend afterward merely to insert its own hash.

---

# Push

Push the current checked-out branch to the existing configured remote.

Expected:

```text
origin
```

Do not change remote configuration.

Do not force push.

---

# Final Git Validation

After push:

```text
git status
```

Required:

```text
GIT_STATUS_AFTER=CLEAN
```

Verify repository continuity.

A fresh development agent must be able to determine only from repository artifacts that:

```text
V3 = FORMALLY CLOSED

V4-R1 = APPROVED
V4-R1.1 = APPROVED
V4-R2 = APPROVED
V4-R3 = APPROVED
V4-R4 = APPROVED
V4-R5 = APPROVED
V4-R6 = APPROVED
V4-R7 = APPROVED

readiness = READY

next = V4-R8
```

No prior conversation memory may be required.

---

# Expected Success State

```text
STATUS=V4_R7_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R7_CONTRACT_SHA256=
a209f766b3ef1e225512ba4e26d5fd18d81cc18d34a0c52567d557778ddcc772

R7_CONTRACT_INTEGRITY=PASS

R7_EXAMPLE_SHA256=
308a2a342e1efac3e49c9d94c6965aabc3b795aeb9511f3ecbe05b25e6dd268f

R7_EXAMPLE_INTEGRITY=PASS

TESTS=>=928_PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_R7_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_R7_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4-R8
```

---

# Stop Condition

STOP after:

1. verifying reviewed R7 integrity;
2. running regression/readiness;
3. recording Technical Lead approval;
4. updating `PROJECT_STATE.json`;
5. appending the closure section to the R7 result;
6. creating the closure/versioning result;
7. staging only R7/closure artifacts;
8. committing;
9. pushing;
10. confirming clean Git state;
11. confirming repository continuity.

Do NOT implement:

```text
V4-R8
```

Do NOT create proposals.

Do NOT modify R7 semantics.

Wait for the Technical Lead to authorize the next round.

Expected final state:

```text
V4_R7=FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4-R8
```
