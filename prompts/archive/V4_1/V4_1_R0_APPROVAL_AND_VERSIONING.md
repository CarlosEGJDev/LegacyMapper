# LegacyMapper V4.1 — R0 Approval and Versioning

TASK=V4_1_R0_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
REFACTOR_ALLOWED=false
R1_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

```text
V4.1-R0 — Maintainability Inventory and Refactor Plan
```

The Technical Lead explicitly accepts:

1. the maintainability inventory;
2. the revised ten-round V4.1 roadmap;
3. the deterministic analysis tooling under `tools/v4_1_r0/`;
4. the finding `REG-002-CANDIDATE`;
5. the diagnosis that `REG-002-CANDIDATE` is a pre-existing stale-snapshot test defect;
6. that R0 correctly did not modify the failing test because R0 was analysis-only;
7. that fixing REG-002 is the mandatory first action of V4.1-R1;
8. that no production behavior changed;
9. that no R0.1 corrective round is required.

The development agent must not grant approval itself.

---

# Important Baseline Exception

R0's entry gate discovered:

```text
BASELINE_TESTS=1380
PASS=1379
FAIL=1
```

The single failure is:

```text
REG-002-CANDIDATE
```

Affected test:

```text
tests/test_v4_r14_manuals_and_final_baseline.py
DeterminismTests.test_baseline_matches_on_disk_artifact
```

Accepted diagnosis:

The test compares the frozen R14 final baseline artifact, which correctly records the repository state at the time that artifact was generated, against the later live `PROJECT_STATE.json` state after R14 itself was approved.

This is a stale-snapshot assertion defect.

It is analogous in shape to REG-001.

R0 was not authorized to modify it.

This closure must NOT fix it.

---

# Required R1 Entry Rule

Record explicitly:

```text
R1_FIRST_ACTION=FIX_REG_002

R1_REFACTOR_MAY_BEGIN_ONLY_AFTER_FULL_SUITE_GREEN=true
```

Required R1 order:

```text
1. Reproduce REG-002.
2. Apply minimal test-only correction.
3. Run full regression.
4. Require all tests PASS.
5. Only then begin DUP-001 / DEBT-001 cleanup.
```

No other refactor may precede this.

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/V4/V4_FINAL_CLOSURE_RESULT.md`
5. `docs/V4_1/V4_1_R0_MAINTAINABILITY_INVENTORY_AND_REFACTOR_PLAN_RESULT.md`
6. `output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json`
7. `output/v4_1_r0/V4_1_REFACTOR_PLAN.json`
8. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Repository artifacts are authoritative.

---

# Reviewed R0 Artifacts

Expected:

```text
output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json

SHA256=
b3308ba13e5fbc8cf9f9d381f3cd9d83a53f9b2ad3fad94e9b361c64ae2f398f
```

Expected:

```text
output/v4_1_r0/V4_1_REFACTOR_PLAN.json

SHA256=
205b933293291c15394f667ffef6ee450d5aef43b0453cdda94865c6036b3954
```

Require:

```text
MAINTAINABILITY_INVENTORY_INTEGRITY=PASS
REFACTOR_PLAN_INTEGRITY=PASS
```

If either differs:

STOP.

Do not regenerate or repair them in the same task.

---

# Approved Inventory State

Preserve:

```text
PRODUCTION_FILES_ANALYZED=143

HIGH_RISK_CANDIDATES=16
VERY_HIGH_RISK_CANDIDATES=6

DUPLICATION_CANDIDATES=4
SAFE_CONSOLIDATION_CANDIDATES=1

CHARACTERIZATION_REQUIRED=5

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false
```

---

# Approved Duplication Decisions

Preserve:

```text
DUP-001=SAFE_TO_CONSOLIDATE
DUP-002=SIMILAR_BUT_SEMANTICALLY_DISTINCT
DUP-003=NEEDS_CHARACTERIZATION
DUP-004=DO_NOT_CONSOLIDATE
```

Do not broaden these classifications during closure.

---

# Approved Characterization Decisions

Preserve:

```text
TOO_RISKY_WITHOUT_DESIGN_REVIEW:
legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py
```

Preserve:

```text
ADDITIONAL_CHARACTERIZATION_REQUIRED:
legacy_documenter/knowledge/readiness.py
legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py
```

Do not refactor any of them during closure.

---

# Approved Debt

Carry forward:

```text
TD-001
TD-002
TD-003
TD-004
TD-005

DEBT-001
DEBT-002
DEBT-003

REG-002-CANDIDATE
```

REG-002 remains open until R1.

---

# Approved V4.1 Roadmap

The R0 evidence-based ten-round roadmap is approved.

Preserve the exact round definitions from:

```text
output/v4_1_r0/V4_1_REFACTOR_PLAN.json
```

Do not reconstruct or paraphrase the round definitions from memory.

At minimum continuity must show:

```text
V4.1-R1 through V4.1-R10 = PLANNED
```

with R1 first.

---

# Global V4.1 Invariants

Preserve:

```text
REFRACTOR_GOAL=READABILITY_AND_MAINTAINABILITY
BEHAVIOR_CHANGE=FORBIDDEN

V4_CONTRACT_CHANGE=FORBIDDEN
PLUGIN_RUNTIME_IMPLEMENTATION=FORBIDDEN
V5_IMPLEMENTATION=FORBIDDEN
```

---

# Regression During Closure

Because REG-002 is intentionally still open, the full suite is expected to retain exactly that known failure.

Run:

```text
python -m unittest discover -s tests
```

Expected pre-R1 state:

```text
TOTAL=1402
KNOWN_FAIL=1
KNOWN_FAIL_ID=REG-002-CANDIDATE
UNEXPECTED_FAIL=0
```

Do not attempt to make the suite green in this closure.

If:

```text
UNEXPECTED_FAIL > 0
```

STOP.

If REG-002 disappears without an authorized change:

STOP and investigate.

No test may be removed, skipped, weakened, or changed.

---

# Readiness

Run:

```text
python -m legacy_documenter.knowledge.readiness
```

Require:

```text
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

---

# PROJECT_STATE

Register R0 approval.

Use the existing schema.

Required semantic state:

```text
latest_completed_round = V4.1-R0
latest_approved_round = V4.1-R0

current_round_in_progress = null

round_status = V4_1_R0_APPROVED

next = V4.1-R1

tests = 1402
```

If the schema tracks failing tests or known defects, record REG-002 there using the existing structure.

Do NOT redesign the schema solely to add a defect field.

V4 remains formally closed.

Do not alter V4 closure status.

---

# R0 Result Closure Section

Append only a closure section to:

```text
docs/V4_1/V4_1_R0_MAINTAINABILITY_INVENTORY_AND_REFACTOR_PLAN_RESULT.md
```

Record:

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

REG_002_CANDIDATE=ACCEPTED
REG_002_STATUS=OPEN_FOR_R1
REG_002_R1_PRIORITY=FIRST_ACTION

ROADMAP_DECISION=APPROVED

R0_1_REQUIRED=false

ROUND_STATUS=APPROVED

DECISION=V4_1_R0_FORMALLY_APPROVED

NEXT=V4.1-R1
```

Do not rewrite the reviewed result.

---

# Closure Result

Create:

```text
docs/V4_1/V4_1_R0_CLOSURE_AND_VERSIONING_RESULT.md
```

Report at minimum:

```text
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

MAINTAINABILITY_INVENTORY_SHA256
MAINTAINABILITY_INVENTORY_INTEGRITY

REFACTOR_PLAN_SHA256
REFACTOR_PLAN_INTEGRITY

ROADMAP_DECISION

REG_002_CANDIDATE
REG_002_STATUS
REG_002_R1_PRIORITY

TESTS_TOTAL
TESTS_PASS
KNOWN_FAIL
UNEXPECTED_FAIL

PRODUCTION_CODE_CHANGED
PRODUCTION_BEHAVIOR_CHANGED

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
AGENT_NEUTRAL_CONTINUITY

ROUND_STATUS
DECISION
NEXT
```

---

# Expected Success State

```text
STATUS=V4_1_R0_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

MAINTAINABILITY_INVENTORY_INTEGRITY=PASS
REFACTOR_PLAN_INTEGRITY=PASS

ROADMAP_DECISION=APPROVED

REG_002_CANDIDATE=ACCEPTED
REG_002_STATUS=OPEN_FOR_R1
REG_002_R1_PRIORITY=FIRST_ACTION

TESTS_TOTAL=1402
TESTS_PASS=1401
KNOWN_FAIL=1
UNEXPECTED_FAIL=0

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R0_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_1_R0_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4.1-R1
```

---

# Git Safety

Inspect:

```text
git status
git diff
git diff --stat
```

Forbidden:

```text
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

```text
SECRET_SCAN=PASS
```

Do not expose real secret values.

---

# Commit

Preferred message:

```text
Approve LegacyMapper V4.1-R0 maintainability plan
```

Use one normal commit.

No amend.

No squash.

---

# Push

Push normally to `origin`.

No force push.

---

# Repository Continuity

After closure a fresh human or AI agent must be able to determine:

```text
V4 = FORMALLY CLOSED

V4.1-R0 = APPROVED

V4.1-R1 = NEXT

REG-002-CANDIDATE = OPEN
REG-002_R1_PRIORITY = FIRST_ACTION

REFRACTOR_GOAL = READABILITY_AND_MAINTAINABILITY
BEHAVIOR_CHANGE = FORBIDDEN
```

No conversation memory may be required.

---

# Stop Condition

STOP after:

1. R0 approval registration;
2. closure result creation;
3. regression verification;
4. readiness verification;
5. commit;
6. push;
7. clean Git status.

Do NOT:

* fix REG-002;
* begin DUP-001 cleanup;
* begin R1;
* modify production code;
* modify V4 contracts;
* begin V5;
* implement Plugin runtime.
