# LegacyMapper V4.1 — R3 Approval and Versioning

TASK=V4_1_R3_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
REFACTOR_ALLOWED=false
R4_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

```text
V4.1-R3 — Naming Pass Part 1 (Low-Risk Renames)
```

The Technical Lead explicitly accepts:

1. the exact R0-derived R3 scope;
2. the three safe batch-parameter renames;
3. the additive `build_maintainability_inventory` alias;
4. preservation of `audit` and `write_audit`;
5. zero keyword-call compatibility breakage;
6. zero compatibility shims;
7. deferral of `copilot_pilot.py`;
8. deferral of the `legacy_documenter/context/` package;
9. `DEBT-003=RESOLVED`;
10. `TD-005=PARTIALLY_RESOLVED`;
11. preservation of all high-risk modules;
12. naming behavior equivalence;
13. approved-artifact integrity;
14. `PRODUCTION_BEHAVIOR_CHANGED=false`;
15. no R3.1 corrective round is required.

The development agent does not grant this approval.

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/V4/V4_FINAL_CLOSURE_RESULT.md`
5. `docs/V4_1/V4_1_R0_CLOSURE_AND_VERSIONING_RESULT.md`
6. `docs/V4_1/V4_1_R1_CLOSURE_AND_VERSIONING_RESULT.md`
7. `docs/V4_1/V4_1_R2_CLOSURE_AND_VERSIONING_RESULT.md`
8. `docs/V4_1/V4_1_R3_LOW_RISK_NAMING_READABILITY_RESULT.md`
9. `output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json`
10. `output/v4_1_r0/V4_1_REFACTOR_PLAN.json`

Repository artifacts are authoritative.

---

# Expected Reviewed State

Require:

```text
latest_completed_round = V4.1-R3
latest_approved_round = V4.1-R2

current_round_in_progress =
"V4.1-R3 (pending Technical Lead review)"

round_status =
V4_1_R3_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R3

tests = 1468
readiness = READY

provider_calls = 0
real_llm_calls = 0
```

If materially different:

STOP.

---

# Reviewed Artifact

Expected:

```text
output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json

SHA256=
9e922d288b4f07812482baef1a5383276cd71f729e27cc67b47e54c30c5afecf
```

Recompute.

Require:

```text
NAMING_COMPATIBILITY_ARTIFACT_INTEGRITY=PASS
```

If different:

STOP.

Do not regenerate or repair it.

---

# Approved Naming Changes

Preserve exactly:

```text
classify_batch:
requests -> classification_requests

create_proposal_batch:
requests -> proposal_requests

create_relation_batch:
requests -> relation_requests
```

And:

```text
legacy_documenter.quality.maintainability_audit
```

preserves:

```text
audit
write_audit
```

and adds:

```text
build_maintainability_inventory
```

Do not perform additional renames during closure.

---

# Compatibility

Require:

```text
PUBLIC_IMPORT_PATHS_PRESERVED=PASS
POSITIONAL_CALL_COMPATIBILITY=PASS
KEYWORD_CALL_COMPATIBILITY=PASS

RETURN_VALUE_EQUIVALENCE=PASS
EXCEPTION_BEHAVIOR_EQUIVALENCE=PASS
NAMING_BEHAVIOR_EQUIVALENCE=PASS
```

No compatibility shim is required or authorized.

---

# Debt Disposition

Record:

```text
DEBT_003_STATUS=RESOLVED
TD_005_STATUS=PARTIALLY_RESOLVED
```

Do not reopen DEBT-003.

Do not mark TD-005 resolved.

---

# Deferred Naming Candidates

Preserve deferred:

```text
legacy_documenter/llm/copilot_pilot.py
legacy_documenter/context/
```

Required:

```text
COPILOT_PILOT_RENAME=DEFERRED
CONTEXT_PACKAGE_RENAME=DEFERRED
```

Do not rename or move them during closure.

---

# High-Risk Modules

Require unchanged:

```text
legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py
legacy_documenter/knowledge/readiness.py
legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py
```

Require:

```text
HIGH_RISK_MODULES_PRESERVED=PASS
```

---

# Approved Artifact Integrity

Reconfirm:

```text
output/v4_r14/V4_FINAL_BASELINE.json
output/v4_r14/V4_FINAL_MANIFEST.json
output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json
output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json
```

Require:

```text
APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
```

Do not regenerate historical artifacts.

---

# Global Invariants

Preserve:

```text
REFRACTOR_GOAL=READABILITY_AND_MAINTAINABILITY
BEHAVIOR_CHANGE=FORBIDDEN

V4_CONTRACT_CHANGE=FORBIDDEN
SERIALIZED_CONTRACT_CHANGE=FORBIDDEN
PUBLIC_API_BREAK=FORBIDDEN

PLUGIN_RUNTIME_IMPLEMENTATION=FORBIDDEN
V5_IMPLEMENTATION=FORBIDDEN
```

---

# Regression

Run:

```text
python -m unittest discover -s tests
```

Require:

```text
>=1468 PASS
FAIL=0
SKIP=0
```

No test may be removed, skipped or weakened.

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

REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

---

# V4 Preservation

Require:

```text
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

```text
PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false
```

Closure itself must not introduce additional production changes.

---

# PROJECT_STATE

Register Technical Lead approval.

Required semantic state:

```text
latest_completed_round = V4.1-R3
latest_approved_round = V4.1-R3

current_round_in_progress = null

round_status = V4_1_R3_APPROVED

next = V4.1-R4

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

V4 remains formally closed.

---

# R3 Result Closure Section

Append only a closure section to:

```text
docs/V4_1/V4_1_R3_LOW_RISK_NAMING_READABILITY_RESULT.md
```

Record:

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

NAMING_SCOPE_DECISION=APPROVED
DEBT_003_DECISION=RESOLVED_APPROVED
TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

COMPATIBILITY_DECISION=APPROVED
DEFERRED_NAMING_DECISION=APPROVED

NAMING_COMPATIBILITY_DECISION=APPROVED

R3_1_REQUIRED=false

ROUND_STATUS=APPROVED

DECISION=V4_1_R3_FORMALLY_APPROVED

NEXT=V4.1-R4
```

Do not rewrite the reviewed result.

---

# Closure Result

Create:

```text
docs/V4_1/V4_1_R3_CLOSURE_AND_VERSIONING_RESULT.md
```

Report at minimum:

```text
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

NAMING_SCOPE_DECISION

DEBT_003_DECISION
TD_005_DECISION

NAMING_COMPATIBILITY_ARTIFACT_SHA256
NAMING_COMPATIBILITY_ARTIFACT_INTEGRITY
NAMING_COMPATIBILITY_DECISION

PUBLIC_IMPORT_PATHS_PRESERVED
POSITIONAL_CALL_COMPATIBILITY
KEYWORD_CALL_COMPATIBILITY

RETURN_VALUE_EQUIVALENCE
EXCEPTION_BEHAVIOR_EQUIVALENCE
NAMING_BEHAVIOR_EQUIVALENCE

HIGH_RISK_MODULES_PRESERVED

COPILOT_PILOT_RENAME
CONTEXT_PACKAGE_RENAME

APPROVED_ARTIFACT_HASHES_UNCHANGED

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

```text
STATUS=V4_1_R3_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

NAMING_SCOPE_DECISION=APPROVED

DEBT_003_DECISION=RESOLVED_APPROVED
TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

NAMING_COMPATIBILITY_ARTIFACT_INTEGRITY=PASS
NAMING_COMPATIBILITY_DECISION=APPROVED

PUBLIC_IMPORT_PATHS_PRESERVED=PASS
POSITIONAL_CALL_COMPATIBILITY=PASS
KEYWORD_CALL_COMPATIBILITY=PASS

RETURN_VALUE_EQUIVALENCE=PASS
EXCEPTION_BEHAVIOR_EQUIVALENCE=PASS
NAMING_BEHAVIOR_EQUIVALENCE=PASS

HIGH_RISK_MODULES_PRESERVED=PASS

COPILOT_PILOT_RENAME=DEFERRED
CONTEXT_PACKAGE_RENAME=DEFERRED

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

TESTS=>=1468_PASS
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

PROJECT_STATE=V4_1_R3_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_1_R3_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4.1-R4
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

---

# Commit

Preferred message:

```text
Approve LegacyMapper V4.1-R3 low-risk naming refactor
```

One normal commit.

No amend.

No squash.

---

# Push

Push normally to `origin`.

No force push.

---

# Repository Continuity

After closure a fresh human or AI agent must determine:

```text
V4 = FORMALLY CLOSED

V4.1-R0 = APPROVED
V4.1-R1 = APPROVED
V4.1-R2 = APPROVED
V4.1-R3 = APPROVED

DUP-001 = RESOLVED
DEBT-001 = RESOLVED
DEBT-003 = RESOLVED

TD-005 = PARTIALLY_RESOLVED

TESTS >= 1468 PASS

BEHAVIOR_CHANGE = FORBIDDEN

V4.1-R4 = NEXT
```

No conversation memory may be required.

---

# Stop Condition

STOP after:

1. R3 approval registration;
2. closure result creation;
3. full green regression;
4. readiness verification;
5. commit;
6. push;
7. clean Git status.

Do NOT:

* begin R4;
* rename `copilot_pilot.py`;
* restructure `context/`;
* continue typing cleanup;
* modify high-risk modules;
* change V4 contracts;
* begin V5;
* implement Plugin runtime.
