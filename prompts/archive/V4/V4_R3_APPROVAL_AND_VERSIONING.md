# LegacyMapper V4 — R3 Human Approval, Closure and Versioning

TASK=V4_R3_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false

GIT_COMMIT_ALLOWED=true

GIT_PUSH_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false

PROVIDER_CALLS_ALLOWED=false

---

# Human Authorization

The Technical Lead has explicitly reviewed and APPROVED:

`V4-R3 — Provenance`

This approval was issued outside the development agent and is authoritative for this closure task.

The development agent MUST NOT:

* reinterpret the approval;
* re-evaluate whether R3 deserves approval;
* independently grant approval;
* modify the R3 implementation;
* begin V4-R4.

Its responsibility is only to:

1. verify the reviewed R3 state;
2. record the Technical Lead's approval;
3. update repository continuity state;
4. run regression/readiness validation;
5. create the formal Git checkpoint;
6. push that checkpoint using the existing repository configuration.

---

# Reviewed R3 Baseline

The Technical Lead reviewed the following primary artifacts:

```text
docs/V4/V4_R3_PROVENANCE_RESULT.md
output/v4_r3/V4_PROVENANCE_CONTRACT.json
```

The reviewed implementation reported:

```text
STATUS=V4_R3_PROVENANCE_COMPLETE
ENTRY_GATE=PASS

BASELINE_TESTS=726_PASS
FINAL_TESTS=766_PASS

SOURCE_NEUTRAL=PASS
CODE_ONLY=PASS
HUMAN_INFORMATION_ONLY=PASS
CODE_AND_HUMAN_INFORMATION=PASS
PARTIAL_INFORMATION=PASS

MULTI_PARENT_LINEAGE=PASS
ROOT_DISCOVERY=PASS
CYCLE_DETECTION=PASS
DANGLING_REFERENCE_VALIDATION=PASS
DUPLICATE_HANDLING=PASS

STABLE_IDENTITY=PASS
DETERMINISTIC_ORDERING=PASS
DETERMINISTIC_SERIALIZATION=PASS

AI_ANCESTRY=PASS
HUMAN_ORIGIN_PRESERVATION=PASS
AUTHORITY_SEPARATION=PASS
APPROVAL_SEPARATION=PASS

SECURITY=PASS
NO_IO=PASS
DETERMINISM=PASS

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

DECISION=V4_R3_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R3
```

Reviewed R3 contract SHA-256:

```text
734d6985783cb7a171aec9952dd9534077fef0ca09fef084179800cd98b1eb2d
```

---

# Required Reading

Before changing repository state, read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_PROPOSED_ROADMAP.md`
7. `docs/V4/V4_R3_PROVENANCE_RESULT.md`
8. `output/v4_r3/V4_PROVENANCE_CONTRACT.json`
9. `docs/V4/V4_R2_CLOSURE_AND_VERSIONING_RESULT.md`
10. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`

Inspect Git state:

```text
git status
git branch --show-current
git log --oneline -5
git remote -v
```

Do not modify the configured remote.

Do not rewrite repository history.

---

# Preconditions

Verify the repository currently communicates:

```text
latest_completed_round = V4-R3
latest_approved_round = V4-R2
round_status = V4-R3_READY_FOR_HUMAN_REVIEW
next = HUMAN_REVIEW_V4_R3
```

Verify:

```text
V4_R3_IMPLEMENTATION=COMPLETE
V4_R3_DECISION=V4_R3_READY_FOR_HUMAN_REVIEW
TESTS>=766_PASS
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

Verify the contract artifact exists:

```text
output/v4_r3/V4_PROVENANCE_CONTRACT.json
```

Recompute its canonical deterministic SHA-256 using the same repository mechanism used to generate the contract.

Expected:

```text
734d6985783cb7a171aec9952dd9534077fef0ca09fef084179800cd98b1eb2d
```

Do not rely only on filesystem metadata.

If the canonical artifact differs unexpectedly:

STOP.

Do not register approval, commit, or push until the discrepancy is understood.

---

# Preserve Reviewed R3 Implementation

No R3 implementation change is authorized.

Do NOT modify:

```text
legacy_documenter/knowledge/provenance/
tests/test_v4_r3_provenance.py
output/v4_r3/V4_PROVENANCE_CONTRACT.json
output/v4_r3/V4_PROVENANCE_EXAMPLE.json
```

unless a deterministic validation process itself rewrites an artifact byte-identically.

Do not perform cleanup or refactoring.

Do not correct unrelated technical debt.

The implementation reviewed by the Technical Lead must remain the implementation being approved.

---

# Register Human Approval

Update:

`PROJECT_STATE.json`

using its existing schema and conventions.

Required resulting state:

```text
latest_completed_round = V4-R3
latest_approved_round = V4-R3
current_round_in_progress = null
round_status = V4-R3_APPROVED
next = V4-R4
tests = <actual validated final count>
readiness = READY
ai_knowledge_allowed = true
ai_knowledge_generated = false
provider_calls = 0
real_llm_calls = 0
```

Do not redesign `PROJECT_STATE.json`.

Do not rename existing fields.

The repository must allow a future agent with no conversation history to determine:

```text
V4_R3=APPROVED
NEXT=V4-R4
```

solely from repository artifacts.

---

# R3 Result Closure

Append a small explicit closure section to:

`docs/V4/V4_R3_PROVENANCE_RESULT.md`

Do not rewrite the implementation report.

Do not alter existing:

* test counts;
* hashes;
* implementation findings;
* design decisions;
* regression results;
* original R3 decision.

Append information equivalent to:

```text
## Closure — Human Approval Recorded

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD
ROUND_STATUS=APPROVED
DECISION=V4_R3_FORMALLY_APPROVED
NEXT=V4-R4
```

Do not invent:

* Technical Lead personal name;
* approval timestamp;

unless an existing deterministic repository convention explicitly requires them.

---

# Regression Validation

After recording approval state, run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=766 PASS
```

Report the actual count.

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

If tests fail or readiness changes unexpectedly:

STOP.

Do not commit or push a broken closure state.

Do not modify production code to make closure validation pass.

Report the failure instead.

---

# Git Safety Check

Before staging run:

```text
git status
```

Verify:

* R3 implementation files are the expected uncommitted implementation from the reviewed round;
* no unexpected unrelated modification exists;
* no ignored heavy generated directory will be staged;
* no credential or secret file will be staged;
* no local-machine-only file will be staged;
* `.gitignore` and repository continuity policy remain respected.

The R3 implementation has not yet been committed as part of the established workflow.

Therefore the closure checkpoint SHOULD include:

1. the reviewed R3 implementation;
2. R3 tests;
3. R3 deterministic contract/example artifacts;
4. R3 result;
5. R3 prompt;
6. R3 approval/versioning prompt;
7. updated `PROJECT_STATE.json`;
8. closure/versioning result.

Do not include unrelated files.

---

# Secret / Repository Safety

Before committing, inspect staged content for obvious credentials/secrets according to existing repository security practices.

Do not commit:

* `.env`;
* tokens;
* API keys;
* passwords;
* OAuth credentials;
* machine-specific secrets;
* ignored heavy generated artifacts.

Synthetic secret fixtures used by tests are allowed only where clearly fake and already expected by repository tests.

---

# Required Closure Result

Create:

`docs/V4/V4_R3_CLOSURE_AND_VERSIONING_RESULT.md`

It must report:

```text
STATUS
HUMAN_REVIEW
APPROVAL_AUTHORITY

R3_CONTRACT_SHA256
R3_CONTRACT_INTEGRITY

TESTS
READINESS
AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE

R3_IMPLEMENTATION_INCLUDED
R3_TESTS_INCLUDED
R3_ARTIFACTS_INCLUDED
R3_PROMPTS_INCLUDED

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

Expected semantic success:

```text
STATUS=V4_R3_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R3_CONTRACT_SHA256=734d6985783cb7a171aec9952dd9534077fef0ca09fef084179800cd98b1eb2d
R3_CONTRACT_INTEGRITY=PASS

TESTS>=766_PASS
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_R3_APPROVED

R3_IMPLEMENTATION_INCLUDED=true
R3_TESTS_INCLUDED=true
R3_ARTIFACTS_INCLUDED=true
R3_PROMPTS_INCLUDED=true

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
REPOSITORY_CONTINUITY=PASS

ROUND_STATUS=APPROVED
DECISION=V4_R3_FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4-R4
```

---

# Important Closure-Result Commit Rule

The closure result itself:

`docs/V4/V4_R3_CLOSURE_AND_VERSIONING_RESULT.md`

MUST be included in the same formal R3 closure commit.

Therefore:

1. create the result before the final commit;
2. stage it together with the other R3 files;
3. inspect `git diff --cached`;
4. then commit.

Do not create a result that claims a commit hash before that commit exists.

If the result needs to record the final commit hash, use a deterministic two-step approach that does NOT rewrite history, or record the hash as:

```text
GIT_COMMIT_HASH=SELF
```

with an explanatory note that this result is contained by the commit being described.

Preferred: avoid unnecessary self-referential commit metadata.

---

# Staging Verification

Stage only the intended R3 checkpoint files.

Then inspect:

```text
git diff --cached --stat
git diff --cached
```

Confirm that staged content corresponds only to:

```text
V4-R3 implementation
V4-R3 tests
V4-R3 artifacts
V4-R3 documentation
V4-R3 prompts
PROJECT_STATE approval transition
V4-R3 closure result
```

If unrelated changes are present:

STOP and isolate them before committing.

Do not discard unrelated user work.

---

# Commit

Create one new normal commit.

Preferred message:

```text
Approve and close LegacyMapper V4-R3
```

Do NOT use:

```text
git commit --amend
git rebase
git reset --hard
git clean -fd
```

Do not squash prior commits.

Do not rewrite history.

---

# Push

Push using the existing current branch and configured upstream/remote.

Normally:

```text
git push origin <current-branch>
```

Do not assume `main` without checking the actual branch.

Do NOT:

```text
git push --force
```

Do not alter remote configuration.

If authentication requires explicit human interaction:

STOP and report exactly what the Technical Lead must authorize/do.

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
R3 closure commit = present
local branch = synchronized with upstream
PROJECT_STATE.latest_approved_round = V4-R3
PROJECT_STATE.round_status = V4-R3_APPROVED
PROJECT_STATE.next = V4-R4
```

Ignored/local-only artifacts may remain only if explicitly expected by repository policy.

---

# Repository Continuity Verification

Verify that a fresh future agent can determine from the repository alone:

```text
V3 = FORMALLY CLOSED
V4-R1 = APPROVED
V4-R1.1 = APPROVED
V4-R2 = APPROVED
V4-R3 = APPROVED

CURRENT BASELINE >= 766 tests
READINESS = READY

NEXT = V4-R4
```

The repository remains the authoritative continuity mechanism.

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
CLOSURE + PROJECT_STATE UPDATE
      ↓
TESTS / READINESS
      ↓
GIT COMMIT
      ↓
GIT PUSH
      ↓
NEXT ROUND
```

The development agent MUST NEVER convert:

```text
READY_FOR_HUMAN_REVIEW
```

to:

```text
APPROVED
```

without explicit Technical Lead authorization.

This applies equally to:

* Claude;
* Codex;
* any future development agent.

---

# Out of Scope

Do NOT implement:

* V4-R4 human-material ingestion;
* V4-R5 classification;
* V4-R6 AS_IS/TO_BE separation;
* V4-R7 gaps/conflicts;
* V4-R8 proposal lifecycle;
* V4-R9 approval workflow;
* V4-R10 canonical Knowledge Source;
* V4-R11 document projection;
* V4-R12 Plugin-facing output;
* V4-R13 final regression/security;
* V4-R14 final manuals/baseline;
* V5 agnosticism.

No LLM/provider calls.

No canonical Knowledge Source generation.

No Plugin output generation.

---

# Stop Condition

STOP after:

1. Technical Lead approval is recorded;
2. `PROJECT_STATE.json` identifies V4-R3 as approved;
3. R3 result contains the approval closure;
4. tests pass;
5. readiness remains READY;
6. contract integrity is confirmed;
7. closure result is created;
8. intended R3 files are staged;
9. Git commit succeeds;
10. Git push succeeds;
11. post-push repository continuity is verified.

Do NOT begin V4-R4.

Expected final state:

```text
V4_R3=FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4-R4
```

Wait for Technical Lead authorization for the next round.
