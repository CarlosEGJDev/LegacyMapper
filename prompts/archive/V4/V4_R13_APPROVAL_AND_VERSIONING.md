# LegacyMapper V4 — R13 Approval, Closure and Versioning

TASK=V4_R13_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
R13_SEMANTIC_CHANGE_ALLOWED=false
R14_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

```text id="e26x66"
V4-R13 — Regression and Security
```

The Technical Lead explicitly accepts:

1. `REG-001` as a valid LOW-severity regression defect.
2. The minimal test-only correction applied to the stale V4-R12 entry-gate assertion.
3. `DEBT-001`, `DEBT-002`, and `DEBT-003` as deferred post-V4 maintainability/documentation debt.
4. `POST_V4_MAINTAINABILITY_REFACTOR=PLANNED`.
5. No R13.1 corrective round is required.

This task records already-granted Technical Lead approval and versions the reviewed R13 checkpoint.

The development agent must NOT grant approval itself.

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_PROPOSED_ROADMAP.md`
7. `docs/V4/V4_R12_CLOSURE_AND_VERSIONING_RESULT.md`
8. `docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md`
9. `output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json`
10. `output/v4_r13/V4_SECURITY_INVARIANTS.json`
11. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
12. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

---

# Expected Pre-Closure State

Verify:

```text id="8o5ogp"
latest_completed_round = V4-R13
latest_approved_round = V4-R12

current_round_in_progress =
"V4-R13 (pending Technical Lead review)"

round_status =
V4-R13_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R13

tests = 1335

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

If semantic state differs:

STOP.

Do not reconcile silently.

---

# Reviewed R13 Artifacts

Expected:

```text id="5kjjz3"
output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json

SHA256=
86c7b3f984b7418b1d7fcb28295fb1376b6a81f42fbc361583007460dfab3782
```

Expected:

```text id="pjrtlr"
output/v4_r13/V4_SECURITY_INVARIANTS.json

SHA256=
ef09123b523421f2243bb15c6d9e52da9791400611cb5979521e32d99f156722
```

Require:

```text id="7l9jtm"
REGRESSION_SECURITY_REPORT_INTEGRITY=PASS
SECURITY_INVARIANTS_INTEGRITY=PASS
```

If either reviewed artifact differs:

STOP.

Do not repair and approve in the same task.

---

# Approved R13 Validation State

Preserve:

```text id="crbh3v"
SECURITY_GATE=PASS
REGRESSION_GATE=PASS

CRITICAL_OPEN=0
HIGH_OPEN=0
MEDIUM_OPEN=0
LOW_OPEN=0

APPROVED_ARTIFACT_INTEGRITY=PASS
```

---

# Approved Defect Resolution

Record:

```text id="a6vm7f"
REG-001
classification=REGRESSION_DEFECT
severity=LOW
affected_round=V4-R12
status=FIXED_IN_R13
```

The accepted fix is limited to:

```text id="2tcnzl"
tests/test_v4_r12_plugin_facing_machine_readable_output_contract.py
```

The stale literal:

```text id="bhxf04"
latest_approved_round == "V4-R11"
```

was replaced with a forward-compatible assertion that verifies R11 or a later round is approved.

Required:

```text id="y1n7kc"
REG_001_RESOLUTION=APPROVED
PRODUCTION_BEHAVIOR_CHANGED=false
```

Do not make further semantic or production changes during closure.

---

# Approved Technical Debt

Record and preserve:

```text id="5fvdpn"
DEBT-001=DEFERRED_TO_POST_V4_REFACTOR
DEBT-002=DEFERRED_TO_POST_V4_REFACTOR
DEBT-003=DEFERRED_TO_POST_V4_REFACTOR

POST_V4_MAINTAINABILITY_REFACTOR=PLANNED
```

Do not perform that refactor in this task.

The future refactor must prioritize:

```text id="fb1h9g"
readability
maintainability
clear responsibilities
C#-developer-friendly Python structure where idiomatic
type hints
docstrings
reduction of safe duplication
simplification of large/mixed-responsibility modules
```

while preserving behavior and approved contracts.

---

# Architectural Invariants

Preserve all R13 PASS results:

```text id="f0w9c2"
ONE_CANONICAL_KNOWLEDGE_SOURCE=PASS
TECHNICAL_LEAD_ONLY_APPROVAL=PASS
SOURCE_CODE_OPTIONAL=PASS

PROVENANCE_APPROVAL_SEPARATION=PASS
APPROVED_NOT_CONFIRMED=PASS
TEMPORAL_SEMANTICS=PASS
RELATION_SEMANTICS=PASS

PROPOSAL_BOUNDARY=PASS
APPROVAL_BOUNDARY=PASS
CANONICAL_BOUNDARY=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS
R11_R12_SIBLING_PROJECTIONS=PASS
```

No redesign is authorized.

---

# Security Invariants

Preserve:

```text id="8kk05p"
PROMPT_INJECTION_INERTNESS=PASS
DYNAMIC_EXECUTION=PASS
UNSAFE_DESERIALIZATION=PASS
PATH_SAFETY=PASS
SECRET_HANDLING=PASS

NETWORK_DEPENDENCY=NONE
PLUGIN_RUNTIME=NOT_IMPLEMENTED
PROVIDER_BOUNDARY=PASS
```

---

# Determinism / Identity

Preserve:

```text id="sn0w61"
DETERMINISM=PASS
IDENTITY_STABILITY=PASS
JSON_COMPATIBILITY=PASS
UNICODE=PASS
```

---

# End-to-End Scenarios

Preserve:

```text id="46f50q"
HUMAN_ONLY_FLOW=PASS
MIXED_SOURCE_FLOW=PASS
TRACEABILITY=PASS

IMPORT_HEALTH=PASS
DEPENDENCY_DIRECTION=PASS
```

---

# Regression Matrix

Require:

```text id="tjd0fr"
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
V4_R10_REGRESSION=PASS
V4_R11_REGRESSION=PASS
V4_R12_REGRESSION=PASS
```

---

# Full Regression

Run:

```text id="kn4a22"
python -m unittest discover -s tests
```

Require:

```text id="ez8mk0"
>=1335 PASS
```

No test may be removed, skipped, weakened, or modified during this closure task.

Run:

```text id="3v6dmw"
python -m legacy_documenter.knowledge.readiness
```

Require:

```text id="szfr6f"
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

If validation fails:

STOP.

---

# Register Technical Lead Approval

Update `PROJECT_STATE.json` using the existing schema.

Required final semantic state:

```text id="2r48nk"
latest_completed_round = V4-R13
latest_approved_round = V4-R13

current_round_in_progress = null

round_status = V4-R13_APPROVED

next = V4-R14

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do not redesign the state schema.

---

# Append Closure to R13 Result

Append only a closure section to:

```text id="gh2ygs"
docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md
```

Record at minimum:

```text id="5yq6pl"
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

REG_001_RESOLUTION=APPROVED

DEBT_001_DISPOSITION=DEFERRED_TO_POST_V4_REFACTOR
DEBT_002_DISPOSITION=DEFERRED_TO_POST_V4_REFACTOR
DEBT_003_DISPOSITION=DEFERRED_TO_POST_V4_REFACTOR

POST_V4_MAINTAINABILITY_REFACTOR=PLANNED

ROUND_STATUS=APPROVED

DECISION=V4_R13_FORMALLY_APPROVED

NEXT=V4-R14
```

Do not rewrite the reviewed R13 result.

---

# Do Not Modify Reviewed Implementation

Do not modify:

```text id="68tv0e"
tests/test_v4_r13_regression_and_security.py

tests/test_v4_r12_plugin_facing_machine_readable_output_contract.py

output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json

output/v4_r13/V4_SECURITY_INVARIANTS.json
```

The already-reviewed REG-001 test correction is part of the approved checkpoint.

No additional correction is authorized.

---

# Git Safety

Inspect:

```text id="0sm4g8"
git status
git diff
git diff --stat
```

No destructive Git operation.

Forbidden:

```text id="4bcavf"
git reset --hard
git clean
git restore .
git checkout -- .
git rebase
git amend
git squash
git push --force
```

---

# Secret Scan

Require:

```text id="ggkthn"
SECRET_SCAN=PASS
```

Do not report secret values.

No credentials, `.env`, tokens, private keys, local virtualenvs, caches or unrelated/heavy generated artifacts may be committed.

---

# Closure Result

Create:

```text id="9cw98m"
docs/V4/V4_R13_CLOSURE_AND_VERSIONING_RESULT.md
```

Report at minimum:

```text id="pr0y0h"
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

REG_001_RESOLUTION

DEBT_001_DISPOSITION
DEBT_002_DISPOSITION
DEBT_003_DISPOSITION

POST_V4_MAINTAINABILITY_REFACTOR

REGRESSION_SECURITY_REPORT_SHA256
REGRESSION_SECURITY_REPORT_INTEGRITY

SECURITY_INVARIANTS_SHA256
SECURITY_INVARIANTS_INTEGRITY

TESTS

SECURITY_GATE
REGRESSION_GATE

CRITICAL_OPEN
HIGH_OPEN
MEDIUM_OPEN
LOW_OPEN

APPROVED_ARTIFACT_INTEGRITY

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

# Expected Checkpoint Files

Stage as applicable:

```text id="j2s7e9"
tests/test_v4_r13_regression_and_security.py

tests/test_v4_r12_plugin_facing_machine_readable_output_contract.py

output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json
output/v4_r13/V4_SECURITY_INVARIANTS.json

docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md

prompts/V4/V4_R13_REGRESSION_AND_SECURITY.md
prompts/V4/V4_R13_APPROVAL_AND_VERSIONING.md

PROJECT_STATE.json

docs/V4/V4_R13_CLOSURE_AND_VERSIONING_RESULT.md
```

No R14 implementation file belongs in this commit.

Inspect staged diff before commit.

---

# Commit

Preferred commit message:

```text id="pob7fy"
Approve and close LegacyMapper V4-R13
```

One normal commit.

No amend.

No squash.

---

# Push

Push current branch normally to `origin`.

No force push.

If explicit authorization is required:

STOP after commit and request it.

---

# Repository Continuity

A fresh agent must be able to determine from repository artifacts alone:

```text id="7pjncc"
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
V4-R11   = APPROVED
V4-R12   = APPROVED
V4-R13   = APPROVED

readiness = READY
next = V4-R14

POST_V4_MAINTAINABILITY_REFACTOR = PLANNED
```

---

# Expected Success State

```text id="5w18i9"
STATUS=V4_R13_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

REG_001_RESOLUTION=APPROVED

DEBT_001_DISPOSITION=DEFERRED_TO_POST_V4_REFACTOR
DEBT_002_DISPOSITION=DEFERRED_TO_POST_V4_REFACTOR
DEBT_003_DISPOSITION=DEFERRED_TO_POST_V4_REFACTOR

POST_V4_MAINTAINABILITY_REFACTOR=PLANNED

REGRESSION_SECURITY_REPORT_INTEGRITY=PASS
SECURITY_INVARIANTS_INTEGRITY=PASS

TESTS=>=1335_PASS

SECURITY_GATE=PASS
REGRESSION_GATE=PASS

CRITICAL_OPEN=0
HIGH_OPEN=0
MEDIUM_OPEN=0
LOW_OPEN=0

APPROVED_ARTIFACT_INTEGRITY=PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_R13_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_R13_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4-R14
```

---

# Stop Condition

STOP after closing and versioning R13.

Do NOT begin V4-R14.

Do NOT perform the post-V4 maintainability/readability refactor.
