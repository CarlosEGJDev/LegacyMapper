# LegacyMapper V4 — R4 Human Approval, Closure and Versioning

TASK=V4_R4_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false

GIT_COMMIT_ALLOWED=true

GIT_PUSH_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false

PROVIDER_CALLS_ALLOWED=false

---

# Human Authorization

The Technical Lead has explicitly reviewed and APPROVED:

`V4-R4 — Human Supplied Material Ingestion`

The reviewed implementation includes the documented minimal backward-compatible R1 extension:

```text
MaterialItem.temporal_state: TemporalState | None = None
```

The Technical Lead explicitly accepts this extension as part of the approved R4 implementation.

This approval was issued outside the development agent.

The development agent MUST NOT:

* reinterpret the approval;
* independently decide whether R4 deserves approval;
* modify the reviewed R4 implementation;
* redesign the R1 extension;
* perform cleanup/refactoring;
* begin V4-R5.

Its responsibility is only to:

1. verify the reviewed R4 state;
2. verify deterministic artifacts;
3. record the Technical Lead approval;
4. update repository continuity state;
5. run regression/readiness validation;
6. create the formal Git checkpoint;
7. push that checkpoint using the existing repository configuration.

---

# Reviewed R4 Baseline

Primary reviewed artifacts:

```text
docs/V4/V4_R4_HUMAN_SUPPLIED_MATERIAL_INGESTION_RESULT.md
output/v4_r4/V4_HUMAN_MATERIAL_INGESTION_CONTRACT.json
```

The reviewed implementation reported:

```text
STATUS=V4_R4_HUMAN_SUPPLIED_MATERIAL_INGESTION_COMPLETE
ENTRY_GATE=PASS

BASELINE_TESTS=766_PASS
FINAL_TESTS=802_PASS

STRUCTURED_INPUT=PASS
FREE_FORM_TEXT=PASS
SOURCE_TYPE_PRESERVATION=PASS
SOURCE_INFERENCE=NONE

R2_VALIDATION_REUSE=PASS
R1_MATERIAL_REUSE=PASS
R3_PROVENANCE_REUSE=PASS

MATERIAL_IDENTITY=DETERMINISTIC
NORMALIZATION=DETERMINISTIC_NON_SEMANTIC
ORIGINAL_CONTENT_PRESERVATION=PASS

TEMPORAL_PRESERVATION=PASS
TEMPORAL_INFERENCE=NONE

ORIGIN_PRESERVATION=PASS
PROVENANCE_COMPLETENESS=PASS

BATCH_INGESTION=PASS
FAILURE_ISOLATION=PASS
DUPLICATE_POLICY=DETERMINISTIC_EXACT_ONLY

KNOWLEDGE_CLASSIFICATION=NOT_PERFORMED
APPROVAL=NOT_PERFORMED
CANONICAL_KNOWLEDGE=NOT_GENERATED
LATER_STAGE_NODES=NOT_CREATED

SANITIZATION=PASS
PROMPT_INJECTION_BOUNDARY=PASS
SECURITY=PASS
NO_IO=PASS

CONTRACT_DETERMINISM=PASS
EXAMPLE_DETERMINISM=PASS

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

DECISION=V4_R4_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R4
```

Reviewed hashes:

```text
V4_HUMAN_MATERIAL_INGESTION_CONTRACT.json
SHA256=a9d478058a2e87560e14fcb66324e02a2691a17401243ef18a1ad0a451094542

V4_HUMAN_MATERIAL_INGESTION_EXAMPLE.json
SHA256=67a7383d57b33ad420eab45cbf2b22526b8cd02dedfae85fcc3b092aa295c49a
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
7. `docs/V4/V4_R3_CLOSURE_AND_VERSIONING_RESULT.md`
8. `docs/V4/V4_R4_HUMAN_SUPPLIED_MATERIAL_INGESTION_RESULT.md`
9. `output/v4_r4/V4_HUMAN_MATERIAL_INGESTION_CONTRACT.json`
10. `output/v4_r4/V4_HUMAN_MATERIAL_INGESTION_EXAMPLE.json`
11. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
12. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Inspect Git state:

```text
git status
git branch --show-current
git log --oneline -5
git remote -v
```

Do not modify the configured remote.

Do not rewrite history.

---

# Preconditions

Expected repository state before closure:

```text
latest_completed_round = V4-R4
latest_approved_round = V4-R3
current_round_in_progress = V4-R4 (pending Technical Lead review)
round_status = V4-R4_READY_FOR_HUMAN_REVIEW
next = HUMAN_REVIEW_V4_R4
```

Verify:

```text
V4_R4_IMPLEMENTATION=COMPLETE
V4_R4_DECISION=V4_R4_READY_FOR_HUMAN_REVIEW

TESTS>=802_PASS
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

Verify both deterministic artifacts exist:

```text
output/v4_r4/V4_HUMAN_MATERIAL_INGESTION_CONTRACT.json
output/v4_r4/V4_HUMAN_MATERIAL_INGESTION_EXAMPLE.json
```

---

# Deterministic Artifact Integrity

Recompute both artifacts using the same canonical repository mechanisms used during R4.

Expected contract SHA-256:

```text
a9d478058a2e87560e14fcb66324e02a2691a17401243ef18a1ad0a451094542
```

Expected example SHA-256:

```text
67a7383d57b33ad420eab45cbf2b22526b8cd02dedfae85fcc3b092aa295c49a
```

Required:

```text
CONTRACT_INTEGRITY=PASS
EXAMPLE_INTEGRITY=PASS
```

If either artifact differs unexpectedly:

STOP.

Do not register approval.

Do not commit.

Do not push.

Report the discrepancy.

---

# Preserve Reviewed R4 Implementation

No R4 implementation change is authorized during closure.

Do NOT modify:

```text
legacy_documenter/knowledge/ingestion/
tests/test_v4_r4_human_material_ingestion.py
output/v4_r4/V4_HUMAN_MATERIAL_INGESTION_CONTRACT.json
output/v4_r4/V4_HUMAN_MATERIAL_INGESTION_EXAMPLE.json
```

Also do NOT alter the approved R1 extension:

```text
MaterialItem.temporal_state
```

unless a deterministic artifact-generation mechanism rewrites an artifact byte-identically.

Do not perform:

* cleanup;
* refactoring;
* renaming;
* API redesign;
* type-model redesign;
* technical-debt work.

The implementation being committed must remain the implementation reviewed by the Technical Lead.

---

# Register Human Approval

Update:

`PROJECT_STATE.json`

using its existing schema and conventions.

Required resulting state:

```text
latest_completed_round = V4-R4
latest_approved_round = V4-R4
current_round_in_progress = null
round_status = V4-R4_APPROVED
next = V4-R5

tests = <actual validated final count>
readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do not redesign `PROJECT_STATE.json`.

Do not rename fields.

Repository artifacts alone must allow a future agent to determine:

```text
V4_R4=APPROVED
NEXT=V4-R5
```

---

# R4 Result Closure

Append a small closure section to:

`docs/V4/V4_R4_HUMAN_SUPPLIED_MATERIAL_INGESTION_RESULT.md`

Do not rewrite the implementation report.

Do not alter existing:

* test counts;
* hashes;
* design decisions;
* security findings;
* regression findings;
* implementation findings;
* original decision.

Append information equivalent to:

```text
## Closure — Human Approval Recorded

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD
R1_TEMPORAL_STATE_EXTENSION=APPROVED_AS_PART_OF_R4
ROUND_STATUS=APPROVED
DECISION=V4_R4_FORMALLY_APPROVED
NEXT=V4-R5
```

Do not invent Technical Lead personal identity.

Do not invent an approval timestamp unless an existing deterministic repository convention requires one.

---

# Regression Validation

After recording approval run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=802 PASS
```

Report actual count.

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

If regression or readiness fails:

STOP.

Do not modify production code to make closure pass.

Do not commit or push a broken closure state.

Report the failure.

---

# Git Safety Check

Before staging run:

```text
git status
```

Verify that the working tree contains only:

* reviewed R4 implementation;
* approved R1 `MaterialItem.temporal_state` extension;
* R4 tests;
* R4 artifacts;
* R4 prompt;
* R4 result;
* this approval/versioning prompt;
* `PROJECT_STATE.json`;
* closure-result documentation.

No unrelated user modification may be discarded.

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

Clearly synthetic security-test fixtures are allowed where expected by the existing test suite.

Required:

```text
GIT_SAFETY=PASS
SECRET_SCAN=PASS
```

---

# Required Closure Result

Create:

`docs/V4/V4_R4_CLOSURE_AND_VERSIONING_RESULT.md`

It must report at minimum:

```text
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY
R1_TEMPORAL_STATE_EXTENSION

R4_CONTRACT_SHA256
R4_CONTRACT_INTEGRITY

R4_EXAMPLE_SHA256
R4_EXAMPLE_INTEGRITY

TESTS
READINESS

AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE

R4_IMPLEMENTATION_INCLUDED
R4_R1_EXTENSION_INCLUDED
R4_TESTS_INCLUDED
R4_ARTIFACTS_INCLUDED
R4_PROMPTS_INCLUDED

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
STATUS=V4_R4_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD
R1_TEMPORAL_STATE_EXTENSION=APPROVED_AS_PART_OF_R4

R4_CONTRACT_SHA256=a9d478058a2e87560e14fcb66324e02a2691a17401243ef18a1ad0a451094542
R4_CONTRACT_INTEGRITY=PASS

R4_EXAMPLE_SHA256=67a7383d57b33ad420eab45cbf2b22526b8cd02dedfae85fcc3b092aa295c49a
R4_EXAMPLE_INTEGRITY=PASS

TESTS>=802_PASS
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_R4_APPROVED

R4_IMPLEMENTATION_INCLUDED=true
R4_R1_EXTENSION_INCLUDED=true
R4_TESTS_INCLUDED=true
R4_ARTIFACTS_INCLUDED=true
R4_PROMPTS_INCLUDED=true

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS

ROUND_STATUS=APPROVED
DECISION=V4_R4_FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4-R5
```

---

# Closure Result and Self-Referential Commit

The closure result itself must be included in the formal R4 closure commit:

```text
docs/V4/V4_R4_CLOSURE_AND_VERSIONING_RESULT.md
```

Do not create a result claiming a commit hash that does not yet exist.

Preferred:

```text
GIT_COMMIT_HASH=SELF
```

with an explanation that the result is contained by the commit it describes.

Do not amend the commit afterward merely to insert its own hash.

---

# Staging

Stage only the intended R4 checkpoint.

Expected categories:

```text
V4-R4 implementation
approved R1 temporal_state extension
V4-R4 tests
V4-R4 artifacts
V4-R4 documentation
V4-R4 prompts
PROJECT_STATE approval transition
V4-R4 closure result
```

Inspect:

```text
git diff --cached --stat
git diff --cached
```

If unrelated changes are present:

STOP.

Isolate them without deleting or discarding user work.

---

# Commit

Create one normal commit.

Preferred message:

```text
Approve and close LegacyMapper V4-R4
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

Determine the current branch first.

Push using the existing configured remote/upstream.

Normally:

```text
git push origin <current-branch>
```

Do not assume the branch without checking it.

Do NOT use:

```text
git push --force
```

Do not modify remote configuration.

If authentication requires explicit human action:

STOP and report the required action.

Do not bypass authentication.

---

# Post-Push Verification

After successful push run:

```text
git status
git log --oneline -5
```

Verify:

```text
working tree = clean

R4 closure commit = present

local branch = synchronized with upstream

PROJECT_STATE.latest_completed_round = V4-R4
PROJECT_STATE.latest_approved_round = V4-R4
PROJECT_STATE.round_status = V4-R4_APPROVED
PROJECT_STATE.next = V4-R5
```

---

# Repository Continuity Verification

A future agent with no conversation history must be able to determine from the repository:

```text
V3 = FORMALLY CLOSED

V4-R1 = APPROVED
V4-R1.1 = APPROVED
V4-R2 = APPROVED
V4-R3 = APPROVED
V4-R4 = APPROVED

CURRENT BASELINE >= 802 tests
READINESS = READY

NEXT = V4-R5
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

No development agent may convert:

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

* V4-R5 Knowledge Classification;
* V4-R6 AS_IS / TO_BE Separation;
* V4-R7 Gap and Conflict Representation;
* V4-R8 Proposal Lifecycle;
* V4-R9 Technical Lead Approval workflow;
* V4-R10 Canonical Knowledge Composition;
* V4-R11 Human-Readable Document Projection;
* V4-R12 Plugin-Facing Machine-Readable Output;
* V4-R13 Regression and Security;
* V4-R14 Manuals and Final Baseline;
* V5 technology/language/framework agnosticism.

Do not:

* classify R4 material;
* infer temporal state;
* detect semantic conflicts;
* create proposals;
* create approved knowledge;
* generate canonical Knowledge Source;
* generate Plugin output;
* call LLM/provider;
* fetch external documents.

---

# Stop Condition

STOP after:

1. R4 artifact integrity is verified;
2. Technical Lead approval is recorded;
3. approved R1 extension is explicitly recorded;
4. `PROJECT_STATE.json` identifies V4-R4 as approved;
5. R4 result contains the human-approval closure;
6. tests pass;
7. readiness remains READY;
8. closure result is created;
9. intended files are staged;
10. Git commit succeeds;
11. Git push succeeds;
12. post-push continuity is verified.

Do NOT begin V4-R5.

Expected final state:

```text
V4_R4=FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4-R5
```

Wait for Technical Lead authorization.
