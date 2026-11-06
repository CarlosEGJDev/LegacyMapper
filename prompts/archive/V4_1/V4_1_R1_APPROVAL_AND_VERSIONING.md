# LegacyMapper V4.1 — R1 Approval and Versioning

TASK=V4_1_R1_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
REFACTOR_ALLOWED=false
R2_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

```text id="kyfzhx"
V4.1-R1 — Regression Fix and Shared JSON Renderer
```

The Technical Lead explicitly accepts:

1. REG-002 as fixed;
2. the user-authorized expansion that fixed the three V4/V4.1 round-ordinal parsing regressions;
3. the two downstream R0 test updates required by the legitimate production-module-count change;
4. the requirement that all test changes preserve durable invariants rather than weaken tests;
5. the shared deterministic JSON renderer;
6. the resolution of DUP-001 / DEBT-001;
7. preservation of DUP-002, DUP-003 and DUP-004;
8. byte-equivalence of all eleven affected renderers;
9. preservation of public function names and import paths;
10. preservation of approved historical artifacts and hashes;
11. `PRODUCTION_BEHAVIOR_CHANGED=false`;
12. no R1.1 corrective round is required.

The development agent does not grant this approval.

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/V4/V4_FINAL_CLOSURE_RESULT.md`
5. `docs/V4_1/V4_1_R0_CLOSURE_AND_VERSIONING_RESULT.md`
6. `docs/V4_1/V4_1_R1_REGRESSION_FIX_AND_SHARED_JSON_RENDERER_RESULT.md`
7. `output/v4_1_r0/V4_1_REFACTOR_PLAN.json`
8. `output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json`
9. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Repository artifacts are authoritative.

---

# Expected Pre-Closure State

Require semantically:

```text id="zn2krb"
latest_completed_round = V4.1-R1
latest_approved_round = V4.1-R0

current_round_in_progress =
"V4.1-R1 (pending Technical Lead review)"

round_status =
V4_1_R1_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R1

tests = 1424

readiness = READY

provider_calls = 0
real_llm_calls = 0
```

If materially different:

STOP.

---

# Reviewed Behavioral Equivalence Artifact

Expected:

```text id="62e76x"
output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json

SHA256=
55c99c3b68ac159585c6a0ec7e05f74e8dd64dd871308d067ab27bdda1a1c33b
```

Recompute.

Require:

```text id="50hdfv"
BEHAVIORAL_EQUIVALENCE_ARTIFACT_INTEGRITY=PASS
```

If different:

STOP.

Do not regenerate it.

---

# Approved Regression Fixes

Preserve:

```text id="94iz8v"
REG_002=FIXED
REG_002_CHANGE_TYPE=TEST_ONLY
REG_002_PRODUCTION_CHANGE=false

ROUND_ORDINAL_PARSING_DEFECT_FIXED=true
ROUND_ORDINAL_PARSING_CHANGE_TYPE=TEST_ONLY
ROUND_ORDINAL_PARSING_PRODUCTION_CHANGE=false
ROUND_ORDINAL_PARSING_USER_AUTHORIZED_SCOPE_EXPANSION=true
```

The affected tests must retain their durable invariant.

Do not reintroduce exact historical-state assumptions.

---

# Approved R0 Test Adjustments

The Technical Lead accepts the two R0 test adjustments caused by the legitimate addition of:

```text id="fzyh7r"
legacy_documenter/utils/json_rendering.py
```

Preserve:

```text id="o8bl5g"
PRODUCTION_MODULE_COUNT_CHANGE=143_TO_144
EXPECTED_NEW_PRODUCTION_MODULES=1
```

The tests must continue detecting unrelated changes.

Do not convert them into permissive snapshot checks.

---

# Approved Shared Renderer

Preserve:

```text id="mynkzm"
SHARED_RENDERER_PATH=
legacy_documenter/utils/json_rendering.py
```

Conceptual responsibility:

```text id="iglxz7"
deterministic JSON serialization only
```

No domain semantics.

No filesystem.

No provider access.

No global state.

No round-specific behavior.

---

# DUP-001 / DEBT-001

Record:

```text id="vwyqbm"
DUP_001=RESOLVED
DEBT_001=RESOLVED
```

Preserve:

```text id="4a1nzc"
DUP_002=SIMILAR_BUT_SEMANTICALLY_DISTINCT
DUP_003=UNTOUCHED
DUP_004=UNTOUCHED
```

Do not broaden the shared abstraction during closure.

---

# Public Compatibility

Require:

```text id="4fd9pz"
PUBLIC_IMPORT_PATHS_PRESERVED=PASS
PUBLIC_FUNCTION_NAMES_PRESERVED=PASS
```

Existing:

```text id="o04zq7"
build_*_contract()
render_*_contract_json()
```

must remain available at their existing paths.

---

# Byte Equivalence

Require:

```text id="hxnhrk"
AFFECTED_RENDERERS=11

CONTRACT_JSON_BYTE_EQUIVALENCE=PASS
APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
```

Do not regenerate historical artifacts.

---

# Global V4.1 Invariants

Preserve:

```text id="ouh1bp"
REFRACTOR_GOAL=READABILITY_AND_MAINTAINABILITY
BEHAVIOR_CHANGE=FORBIDDEN

V4_CONTRACT_CHANGE=FORBIDDEN
PLUGIN_RUNTIME_IMPLEMENTATION=FORBIDDEN
V5_IMPLEMENTATION=FORBIDDEN
```

---

# Regression

Run:

```text id="n2i1br"
python -m unittest discover -s tests
```

Require:

```text id="ek1u5s"
>=1424 PASS
FAIL=0
```

No test may be removed, skipped or weakened.

Run:

```text id="x7omlh"
python -m legacy_documenter.knowledge.readiness
```

Require:

```text id="xbpbua"
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

---

# V4 Preservation

Require:

```text id="smkqeo"
V4_CONTRACTS_UNCHANGED=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0

PLUGIN_RUNTIME=NOT_IMPLEMENTED

V5_IMPLEMENTED=false
```

---

# Production Classification

Preserve:

```text id="d7cbs8"
PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false

REG_002_PRODUCTION_CHANGE=false
ROUND_ORDINAL_PARSING_PRODUCTION_CHANGE=false
```

---

# PROJECT_STATE

Register Technical Lead approval.

Required semantic state:

```text id="7rjqgn"
latest_completed_round = V4.1-R1
latest_approved_round = V4.1-R1

current_round_in_progress = null

round_status = V4_1_R1_APPROVED

next = V4.1-R2

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

V4 remains formally closed.

Do not modify V4 closure semantics.

---

# R1 Result Closure Section

Append only a closure section to:

```text id="3i0l6a"
docs/V4_1/V4_1_R1_REGRESSION_FIX_AND_SHARED_JSON_RENDERER_RESULT.md
```

Record:

```text id="vy8j4s"
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

REG_002_DECISION=APPROVED
ROUND_ORDINAL_PARSING_FIX_DECISION=APPROVED
R0_TEST_ADJUSTMENTS_DECISION=APPROVED

DUP_001_DECISION=APPROVED
DEBT_001_DECISION=APPROVED

BEHAVIORAL_EQUIVALENCE_DECISION=APPROVED

R1_1_REQUIRED=false

ROUND_STATUS=APPROVED

DECISION=V4_1_R1_FORMALLY_APPROVED

NEXT=V4.1-R2
```

Do not rewrite the reviewed implementation result.

---

# Closure Result

Create:

```text id="02dj6p"
docs/V4_1/V4_1_R1_CLOSURE_AND_VERSIONING_RESULT.md
```

Report at minimum:

```text id="f8mgzm"
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

REG_002_DECISION
ROUND_ORDINAL_PARSING_FIX_DECISION
R0_TEST_ADJUSTMENTS_DECISION

DUP_001_DECISION
DEBT_001_DECISION

BEHAVIORAL_EQUIVALENCE_ARTIFACT_SHA256
BEHAVIORAL_EQUIVALENCE_ARTIFACT_INTEGRITY
BEHAVIORAL_EQUIVALENCE_DECISION

CONTRACT_JSON_BYTE_EQUIVALENCE
APPROVED_ARTIFACT_HASHES_UNCHANGED

PUBLIC_IMPORT_PATHS_PRESERVED
PUBLIC_FUNCTION_NAMES_PRESERVED

TESTS
READINESS

V4_CONTRACTS_UNCHANGED
R11_BOUNDARY
R12_BOUNDARY

PRODUCTION_CODE_CHANGED
PRODUCTION_BEHAVIOR_CHANGED

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
AGENT_NEUTRAL_CONTINUITY

ROUND_STATUS
DECISION
NEXT
```

---

# Expected Success State

```text id="wwtm9i"
STATUS=V4_1_R1_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

REG_002_DECISION=APPROVED
ROUND_ORDINAL_PARSING_FIX_DECISION=APPROVED
R0_TEST_ADJUSTMENTS_DECISION=APPROVED

DUP_001_DECISION=APPROVED
DEBT_001_DECISION=APPROVED

BEHAVIORAL_EQUIVALENCE_ARTIFACT_INTEGRITY=PASS
BEHAVIORAL_EQUIVALENCE_DECISION=APPROVED

CONTRACT_JSON_BYTE_EQUIVALENCE=PASS
APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

PUBLIC_IMPORT_PATHS_PRESERVED=PASS
PUBLIC_FUNCTION_NAMES_PRESERVED=PASS

TESTS=>=1424_PASS
READINESS=READY

V4_CONTRACTS_UNCHANGED=PASS
R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R1_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_1_R1_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4.1-R2
```

---

# Git Safety

Inspect before staging:

```text id="4i4y4z"
git status
git diff
git diff --stat
```

No destructive Git operations.

Forbidden:

```text id="bvrj8j"
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

```text id="kchb3a"
SECRET_SCAN=PASS
```

Do not expose secret values.

---

# Commit

Preferred message:

```text id="tupufm"
Approve LegacyMapper V4.1-R1 safe renderer refactor
```

One normal commit.

No amend.

No squash.

---

# Push

Push current branch normally to `origin`.

No force push.

---

# Repository Continuity

After closure a fresh human or AI agent must determine:

```text id="lkwcvz"
V4 = FORMALLY CLOSED

V4.1-R0 = APPROVED
V4.1-R1 = APPROVED

REG-002 = RESOLVED
ROUND_ORDINAL_PARSING_DEFECT = RESOLVED

DUP-001 = RESOLVED
DEBT-001 = RESOLVED

DUP-002 = PRESERVED_DISTINCT
DUP-003 = UNTOUCHED
DUP-004 = UNTOUCHED

TESTS >= 1424 PASS

BEHAVIOR_CHANGE = FORBIDDEN

V4.1-R2 = NEXT
```

No conversation memory may be required.

---

# Stop Condition

STOP after:

1. R1 approval registration;
2. closure result creation;
3. full green regression;
4. readiness verification;
5. commit;
6. push;
7. clean Git status.

Do NOT begin R2.

Do NOT modify DUP-002/003/004.

Do NOT begin high-risk decomposition.

Do NOT modify V4 contracts.

Do NOT begin V5.

Do NOT implement Plugin runtime.
