# LegacyMapper V4 — R5 Human Approval, Closure and Versioning

TASK=V4_R5_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false

GIT_COMMIT_ALLOWED=true

GIT_PUSH_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false

PROVIDER_CALLS_ALLOWED=false

---

# Human Authorization

The Technical Lead has explicitly reviewed and APPROVED:

`V4-R5 — Knowledge Classification`

The development agent MUST NOT independently decide whether R5 deserves approval.

The development agent MUST only:

1. verify the reviewed R5 implementation;
2. verify deterministic artifacts;
3. record the Technical Lead approval;
4. update repository continuity state;
5. run regression/readiness validation;
6. create the formal Git checkpoint;
7. push using the existing repository configuration.

Do NOT modify the reviewed R5 implementation.

Do NOT begin V4-R6.

---

# Reviewed R5 Baseline

Primary reviewed artifacts:

```text
docs/V4/V4_R5_KNOWLEDGE_CLASSIFICATION_RESULT.md
output/v4_r5/V4_KNOWLEDGE_CLASSIFICATION_CONTRACT.json
output/v4_r5/V4_KNOWLEDGE_CLASSIFICATION_EXAMPLE.json
```

Reviewed implementation reported:

```text
STATUS=V4_R5_KNOWLEDGE_CLASSIFICATION_COMPLETE
ENTRY_GATE=PASS

BASELINE_TESTS=802_PASS
FINAL_TESTS=842_PASS

KNOWLEDGE_NATURES=17/17
CLASSIFICATION_TAXONOMY=REUSES_R1

CLASSIFICATION_STATUSES=CLASSIFIED,UNCLASSIFIED,AMBIGUOUS
CLASSIFICATION_METHODS=EXPLICIT,DETERMINISTIC_RULE,AI_PROPOSED,UNRESOLVED

SOURCE_TYPE_DISTINCTION=PASS
SOURCE_TYPE_AUTOMAPPING=NONE

TEMPORAL_DISTINCTION=PASS
PROVENANCE_DISTINCTION=PASS
APPROVAL_DISTINCTION=PASS
CANONICAL_KNOWLEDGE_DISTINCTION=PASS

EXPLICIT_CLASSIFICATION=PASS
UNCLASSIFIED=PASS
AMBIGUOUS=PASS

MATERIAL_SPLITTING=NOT_PERFORMED
KNOWLEDGE_STATEMENT_CREATION=NOT_PERFORMED

IDENTITY=DETERMINISTIC
ORDERING=CANONICAL
SERIALIZATION=DETERMINISTIC

BATCH_CLASSIFICATION=PASS
FAILURE_ISOLATION=PASS

SANITIZATION=PASS
PROMPT_INJECTION_BOUNDARY=PASS
SECURITY=PASS
NO_IO=PASS

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

DECISION=V4_R5_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R5
```

Reviewed deterministic hashes:

```text
V4_KNOWLEDGE_CLASSIFICATION_CONTRACT.json
SHA256=6fcdc5ec817d356df11b57326baec88e1c17fbd2e19fe21fde9a5084b65f63c7

V4_KNOWLEDGE_CLASSIFICATION_EXAMPLE.json
SHA256=4db376a95daa7722664040984e0b57f5e9c58a7c01a11ce5ba9b925443d1f17c
```

---

# Required Reading

Before changing repository state read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_PROPOSED_ROADMAP.md`
7. `docs/V4/V4_R4_CLOSURE_AND_VERSIONING_RESULT.md`
8. `docs/V4/V4_R5_KNOWLEDGE_CLASSIFICATION_RESULT.md`
9. `output/v4_r5/V4_KNOWLEDGE_CLASSIFICATION_CONTRACT.json`
10. `output/v4_r5/V4_KNOWLEDGE_CLASSIFICATION_EXAMPLE.json`
11. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
12. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Inspect:

```text
git status
git branch --show-current
git log --oneline -5
git remote -v
```

Do not modify remote configuration.

Do not rewrite history.

---

# Preconditions

Expected repository state:

```text
latest_completed_round = V4-R5
latest_approved_round = V4-R4

current_round_in_progress =
"V4-R5 (pending Technical Lead review)"

round_status =
V4-R5_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R5
```

Verify:

```text
V4_R5_IMPLEMENTATION=COMPLETE
V4_R5_DECISION=V4_R5_READY_FOR_HUMAN_REVIEW

TESTS>=842_PASS
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

Both deterministic R5 artifacts must exist.

---

# Deterministic Artifact Integrity

Recompute both R5 artifacts using the same canonical repository mechanisms used during R5.

Expected contract SHA-256:

```text
6fcdc5ec817d356df11b57326baec88e1c17fbd2e19fe21fde9a5084b65f63c7
```

Expected example SHA-256:

```text
4db376a95daa7722664040984e0b57f5e9c58a7c01a11ce5ba9b925443d1f17c
```

Required:

```text
CONTRACT_INTEGRITY=PASS
EXAMPLE_INTEGRITY=PASS
```

If either differs unexpectedly:

STOP.

Do not register approval.

Do not commit.

Do not push.

Report the discrepancy.

---

# Preserve Reviewed R5 Implementation

No R5 implementation change is authorized during closure.

Do NOT modify:

```text
legacy_documenter/knowledge/classification/
tests/test_v4_r5_knowledge_classification.py
output/v4_r5/V4_KNOWLEDGE_CLASSIFICATION_CONTRACT.json
output/v4_r5/V4_KNOWLEDGE_CLASSIFICATION_EXAMPLE.json
```

Do not perform:

* cleanup;
* refactoring;
* renaming;
* API redesign;
* taxonomy changes;
* technical-debt work;
* semantic improvements.

The implementation being committed must remain the implementation reviewed by the Technical Lead.

---

# Register Human Approval

Update:

`PROJECT_STATE.json`

using its existing schema.

Required resulting state:

```text
latest_completed_round = V4-R5
latest_approved_round = V4-R5
current_round_in_progress = null

round_status = V4-R5_APPROVED
next = V4-R6

tests = <actual validated count>
readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do not redesign `PROJECT_STATE.json`.

Do not rename fields.

---

# R5 Result Closure

Append a small closure section to:

`docs/V4/V4_R5_KNOWLEDGE_CLASSIFICATION_RESULT.md`

Do not rewrite the implementation report.

Append information equivalent to:

```text
## Closure — Human Approval Recorded

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD
ROUND_STATUS=APPROVED
DECISION=V4_R5_FORMALLY_APPROVED
NEXT=V4-R6
```

Do not invent Technical Lead personal identity.

Do not invent an approval timestamp unless an existing repository convention requires one.

---

# Regression Validation

After recording approval run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=842 PASS
```

Report actual count.

Then run:

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

If regression or readiness fails:

STOP.

Do not modify production code during closure to make it pass.

Do not commit or push.

---

# Git Safety Check

Before staging run:

```text
git status
```

Verify the working tree contains only:

* reviewed R5 implementation;
* R5 tests;
* R5 deterministic artifacts;
* R5 implementation prompt;
* R5 result;
* this approval/versioning prompt;
* `PROJECT_STATE.json`;
* R5 closure result.

No unrelated user change may be discarded.

No ignored heavy generated directory may be staged.

No machine-specific file may be staged.

---

# Secret / Repository Safety

Inspect intended staged content using existing repository security practices.

Do not commit:

* `.env`;
* API keys;
* access tokens;
* OAuth credentials;
* passwords;
* private keys;
* machine-specific secrets;
* ignored heavy generated artifacts.

Synthetic test credentials already covered by sanitizer/security tests are acceptable.

Required:

```text
GIT_SAFETY=PASS
SECRET_SCAN=PASS
```

---

# Required Closure Result

Create:

`docs/V4/V4_R5_CLOSURE_AND_VERSIONING_RESULT.md`

Report at minimum:

```text
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

R5_CONTRACT_SHA256
R5_CONTRACT_INTEGRITY

R5_EXAMPLE_SHA256
R5_EXAMPLE_INTEGRITY

TESTS
READINESS

AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE

R5_IMPLEMENTATION_INCLUDED
R5_TESTS_INCLUDED
R5_ARTIFACTS_INCLUDED
R5_PROMPTS_INCLUDED

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

Expected semantic result:

```text
STATUS=V4_R5_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R5_CONTRACT_SHA256=6fcdc5ec817d356df11b57326baec88e1c17fbd2e19fe21fde9a5084b65f63c7
R5_CONTRACT_INTEGRITY=PASS

R5_EXAMPLE_SHA256=4db376a95daa7722664040984e0b57f5e9c58a7c01a11ce5ba9b925443d1f17c
R5_EXAMPLE_INTEGRITY=PASS

TESTS>=842_PASS
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_R5_APPROVED

R5_IMPLEMENTATION_INCLUDED=true
R5_TESTS_INCLUDED=true
R5_ARTIFACTS_INCLUDED=true
R5_PROMPTS_INCLUDED=true

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS

ROUND_STATUS=APPROVED
DECISION=V4_R5_FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4-R6
```

---

# Closure Result and Self-Referential Commit

The closure result itself must be included in the formal R5 closure commit:

```text
docs/V4/V4_R5_CLOSURE_AND_VERSIONING_RESULT.md
```

Preferred:

```text
GIT_COMMIT_HASH=SELF
```

because the result is contained by the same commit it describes.

Do not amend afterward merely to insert the hash.

---

# Staging

Stage only the intended R5 checkpoint.

Expected categories:

```text
V4-R5 implementation
V4-R5 tests
V4-R5 deterministic artifacts
V4-R5 documentation
V4-R5 prompts
PROJECT_STATE approval transition
V4-R5 closure result
```

Inspect:

```text
git diff --cached --stat
git diff --cached
```

If unrelated changes are present:

STOP.

Do not discard user work.

---

# Commit

Create one normal commit.

Preferred message:

```text
Approve and close LegacyMapper V4-R5
```

Do NOT use:

```text
git commit --amend
git rebase
git reset --hard
git clean -fd
```

Do not rewrite previous history.

---

# Push

Determine the actual current branch first.

Push using the existing configured remote/upstream.

Normally:

```text
git push origin <current-branch>
```

Do not assume the branch before checking it.

Do NOT use:

```text
git push --force
```

Do not modify remote configuration.

If authentication requires human action:

STOP and report it.

---

# Post-Push Verification

After successful push:

```text
git status
git log --oneline -5
```

Verify:

```text
working tree = clean

R5 closure commit = present

local branch = synchronized with upstream

PROJECT_STATE.latest_completed_round = V4-R5
PROJECT_STATE.latest_approved_round = V4-R5
PROJECT_STATE.round_status = V4-R5_APPROVED
PROJECT_STATE.next = V4-R6
```

---

# Repository Continuity Verification

A fresh future agent with no conversation history must be able to determine:

```text
V3 = FORMALLY CLOSED

V4-R1 = APPROVED
V4-R1.1 = APPROVED
V4-R2 = APPROVED
V4-R3 = APPROVED
V4-R4 = APPROVED
V4-R5 = APPROVED

CURRENT BASELINE >=842 tests
READINESS = READY

NEXT = V4-R6
```

Conversation memory must not be required.

---

# Established Versioning Lifecycle

Continue enforcing:

```text
IMPLEMENT ROUND
      ↓
VALIDATE
      ↓
READY_FOR_HUMAN_REVIEW
      ↓
STOP
      ↓
TECHNICAL LEAD REVIEW
      ↓
APPROVED
      ↓
CLOSURE + PROJECT_STATE
      ↓
TESTS / READINESS
      ↓
COMMIT
      ↓
PUSH
      ↓
NEXT ROUND
```

No development agent may turn:

```text
READY_FOR_HUMAN_REVIEW
```

into:

```text
APPROVED
```

without explicit Technical Lead authorization.

---

# Out of Scope

Do NOT implement:

* V4-R6 AS_IS / TO_BE Separation;
* V4-R7 Gap and Conflict Representation;
* V4-R8 Proposal Lifecycle;
* V4-R9 Technical Lead Approval workflow;
* V4-R10 Canonical Knowledge Composition;
* V4-R11 Human-Readable Document Projection;
* V4-R12 Plugin-Facing Machine-Readable Output;
* V4-R13 Regression and Security;
* V4-R14 Manuals and Final Baseline.

Do not:

* infer temporal state;
* reconcile temporal states;
* detect semantic gaps/conflicts;
* create proposals;
* approve knowledge;
* create canonical Knowledge Source;
* generate Plugin output;
* call any LLM/provider.

---

# Stop Condition

STOP after:

1. R5 artifact integrity is verified;
2. Technical Lead approval is recorded;
3. `PROJECT_STATE.json` identifies V4-R5 as approved;
4. R5 result contains the human-approval closure;
5. tests pass;
6. readiness remains READY;
7. closure result is created;
8. intended files are staged;
9. Git commit succeeds;
10. Git push succeeds;
11. post-push continuity is verified.

Do NOT begin V4-R6.

Expected final state:

```text
V4_R5=FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4-R6
```

Wait for Technical Lead authorization.
