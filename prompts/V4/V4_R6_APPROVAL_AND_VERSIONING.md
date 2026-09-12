# LegacyMapper V4 — R6 Human Approval, Closure and Versioning

TASK=V4_R6_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false

GIT_COMMIT_ALLOWED=true

GIT_PUSH_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false

PROVIDER_CALLS_ALLOWED=false

---

# Human Authorization

The Technical Lead has explicitly reviewed and APPROVED:

`V4-R6 — AS_IS / TO_BE Separation`

The development agent MUST NOT independently decide whether R6 deserves approval.

The development agent MUST only:

1. verify the reviewed R6 implementation;
2. verify deterministic artifacts;
3. record the Technical Lead approval;
4. update repository continuity state;
5. run regression/readiness validation;
6. create the formal Git checkpoint;
7. push using the existing repository configuration.

Do NOT modify the reviewed R6 implementation.

Do NOT begin V4-R7.

---

# Reviewed R6 Baseline

Primary reviewed artifacts:

```text
docs/V4/V4_R6_AS_IS_TO_BE_SEPARATION_RESULT.md
output/v4_r6/V4_TEMPORAL_SEPARATION_CONTRACT.json
output/v4_r6/V4_TEMPORAL_SEPARATION_EXAMPLE.json
```

Reviewed implementation reported:

```text
STATUS=V4_R6_AS_IS_TO_BE_SEPARATION_COMPLETE
ENTRY_GATE=PASS

BASELINE_TESTS=842_PASS
FINAL_TESTS=875_PASS

TEMPORAL_TAXONOMY=REUSES_R1
TEMPORAL_STATES=AS_IS,TO_BE,HISTORICAL
UNSPECIFIED_REPRESENTATION=None
TEMPORAL_BUCKETS=AS_IS,TO_BE,HISTORICAL,UNSPECIFIED

TEMPORAL_MAPPING=PASS

SOURCE_TYPE_INFERENCE=NONE
KNOWLEDGE_NATURE_INFERENCE=NONE
CONTENT_INFERENCE=NONE
DATE_INFERENCE=NONE

CLASSIFICATION_INDEPENDENCE=PASS
PROVENANCE_INDEPENDENCE=PASS
APPROVAL_DISTINCTION=PASS

AS_IS_TO_BE_SEPARATION=PASS
CONFLICT_DETECTION=NOT_PERFORMED
GAP_DETECTION=NOT_PERFORMED

HISTORICAL_HANDLING=PASS
SUPERSESSION=NOT_INFERRED

UNSPECIFIED_HANDLING=PASS
KNOWLEDGE_STATUS_MUTATION=NONE

MATERIAL_MUTATION=NONE
CLASSIFICATION_MUTATION=NONE

IDENTITY=DETERMINISTIC
ORDERING=DETERMINISTIC
SERIALIZATION=DETERMINISTIC

BATCH_SEPARATION=PASS
DUPLICATE_POLICY=DOCUMENTED_AND_TESTED

SECURITY=PASS
NO_IO=PASS

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

DECISION=V4_R6_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R6
```

Reviewed deterministic hashes:

```text
V4_TEMPORAL_SEPARATION_CONTRACT.json
SHA256=e46b858742d409b273cbc929e8a6c137dd7d58a698f7fc49fe1bcfca85de9531

V4_TEMPORAL_SEPARATION_EXAMPLE.json
SHA256=4793f3aece1d3682a14da03a4c9147af7748e991400eba5520e374c9f9c7d6ff
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
7. `docs/V4/V4_R5_CLOSURE_AND_VERSIONING_RESULT.md`
8. `docs/V4/V4_R6_AS_IS_TO_BE_SEPARATION_RESULT.md`
9. `output/v4_r6/V4_TEMPORAL_SEPARATION_CONTRACT.json`
10. `output/v4_r6/V4_TEMPORAL_SEPARATION_EXAMPLE.json`
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
latest_completed_round = V4-R6
latest_approved_round = V4-R5

current_round_in_progress =
"V4-R6 (pending Technical Lead review)"

round_status =
V4-R6_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R6
```

Verify:

```text
V4_R6_IMPLEMENTATION=COMPLETE
V4_R6_DECISION=V4_R6_READY_FOR_HUMAN_REVIEW

TESTS>=875_PASS
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

Both deterministic R6 artifacts must exist.

---

# Deterministic Artifact Integrity

Recompute both R6 artifacts using the same canonical repository mechanisms used during R6.

Expected contract SHA-256:

```text
e46b858742d409b273cbc929e8a6c137dd7d58a698f7fc49fe1bcfca85de9531
```

Expected example SHA-256:

```text
4793f3aece1d3682a14da03a4c9147af7748e991400eba5520e374c9f9c7d6ff
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

# Preserve Reviewed R6 Implementation

No R6 implementation change is authorized during closure.

Do NOT modify:

```text
legacy_documenter/knowledge/temporal/
tests/test_v4_r6_as_is_to_be_separation.py
output/v4_r6/V4_TEMPORAL_SEPARATION_CONTRACT.json
output/v4_r6/V4_TEMPORAL_SEPARATION_EXAMPLE.json
```

Do not perform:

* cleanup;
* refactoring;
* renaming;
* API redesign;
* temporal taxonomy changes;
* duplicate-policy changes;
* semantic improvements;
* technical-debt work.

The implementation being committed must remain the implementation reviewed by the Technical Lead.

---

# Register Human Approval

Update:

`PROJECT_STATE.json`

using its existing schema.

Required resulting state:

```text
latest_completed_round = V4-R6
latest_approved_round = V4-R6
current_round_in_progress = null

round_status = V4-R6_APPROVED
next = V4-R7

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

# R6 Result Closure

Append a small closure section to:

`docs/V4/V4_R6_AS_IS_TO_BE_SEPARATION_RESULT.md`

Do not rewrite the implementation report.

Append information equivalent to:

```text
## Closure — Human Approval Recorded

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD
ROUND_STATUS=APPROVED
DECISION=V4_R6_FORMALLY_APPROVED
NEXT=V4-R7
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
>=875 PASS
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

* reviewed R6 implementation;
* R6 tests;
* R6 deterministic artifacts;
* R6 implementation prompt;
* R6 result;
* this approval/versioning prompt;
* `PROJECT_STATE.json`;
* R6 closure result.

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

Synthetic credentials used in tests are acceptable only when intentionally sanitized/tested.

Required:

```text
GIT_SAFETY=PASS
SECRET_SCAN=PASS
```

---

# Required Closure Result

Create:

`docs/V4/V4_R6_CLOSURE_AND_VERSIONING_RESULT.md`

Report at minimum:

```text
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

R6_CONTRACT_SHA256
R6_CONTRACT_INTEGRITY

R6_EXAMPLE_SHA256
R6_EXAMPLE_INTEGRITY

TESTS
READINESS

AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE

R6_IMPLEMENTATION_INCLUDED
R6_TESTS_INCLUDED
R6_ARTIFACTS_INCLUDED
R6_PROMPTS_INCLUDED

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
STATUS=V4_R6_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R6_CONTRACT_SHA256=e46b858742d409b273cbc929e8a6c137dd7d58a698f7fc49fe1bcfca85de9531
R6_CONTRACT_INTEGRITY=PASS

R6_EXAMPLE_SHA256=4793f3aece1d3682a14da03a4c9147af7748e991400eba5520e374c9f9c7d6ff
R6_EXAMPLE_INTEGRITY=PASS

TESTS>=875_PASS
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_R6_APPROVED

R6_IMPLEMENTATION_INCLUDED=true
R6_TESTS_INCLUDED=true
R6_ARTIFACTS_INCLUDED=true
R6_PROMPTS_INCLUDED=true

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS

ROUND_STATUS=APPROVED
DECISION=V4_R6_FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4-R7
```

---

# Closure Result and Self-Referential Commit

The closure result itself must be included in the formal R6 closure commit:

```text
docs/V4/V4_R6_CLOSURE_AND_VERSIONING_RESULT.md
```

Preferred:

```text
GIT_COMMIT_HASH=SELF
```

because the result is contained by the same commit it describes.

Do not amend afterward merely to insert the hash.

---

# Staging

Stage only the intended R6 checkpoint.

Expected categories:

```text
V4-R6 implementation
V4-R6 tests
V4-R6 deterministic artifacts
V4-R6 documentation
V4-R6 prompts
PROJECT_STATE approval transition
V4-R6 closure result
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
Approve and close LegacyMapper V4-R6
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

R6 closure commit = present

local branch = synchronized with upstream

PROJECT_STATE.latest_completed_round = V4-R6
PROJECT_STATE.latest_approved_round = V4-R6
PROJECT_STATE.round_status = V4-R6_APPROVED
PROJECT_STATE.next = V4-R7
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
V4-R6 = APPROVED

CURRENT BASELINE >=875 tests
READINESS = READY

NEXT = V4-R7
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
* compare material prose semantically;
* detect gaps;
* detect conflicts;
* infer contradiction;
* infer supersession;
* infer migration;
* create proposals;
* approve knowledge;
* create canonical Knowledge Source;
* generate Plugin output;
* call any LLM/provider.

---

# Stop Condition

STOP after:

1. R6 artifact integrity is verified;
2. Technical Lead approval is recorded;
3. `PROJECT_STATE.json` identifies V4-R6 as approved;
4. R6 result contains the human-approval closure;
5. tests pass;
6. readiness remains READY;
7. closure result is created;
8. intended files are staged;
9. Git commit succeeds;
10. Git push succeeds;
11. post-push continuity is verified.

Do NOT begin V4-R7.

Expected final state:

```text
V4_R6=FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4-R7
```

Wait for Technical Lead authorization.
