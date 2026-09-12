# LegacyMapper V4 — R14 Approval and V4 Final Closure

TASK=V4_R14_APPROVAL_AND_V4_FINAL_CLOSURE

MODE=HUMAN_APPROVAL_REGISTRATION_FINAL_CLOSURE_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
SEMANTIC_CHANGE_ALLOWED=false
R14_REDESIGN_ALLOWED=false

V5_IMPLEMENTATION_ALLOWED=false
POST_V4_REFACTOR_ALLOWED=false
PLUGIN_RUNTIME_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

```text
V4-R14 — Manuals and Final Baseline
```

The Technical Lead explicitly accepts:

1. the four final V4 manuals;
2. the deterministic V4 final baseline;
3. the deterministic V4 final manifest;
4. the minimal anti-staleness corrections to repository continuity documentation;
5. the additive `legacy_documenter/knowledge/closure/` reporting/helper package;
6. `PRODUCTION_BEHAVIOR_CHANGED=false`;
7. the captured pre-refactor maintainability baseline;
8. the carried-forward technical debt;
9. `POST_V4_MAINTAINABILITY_REFACTOR=PLANNED`;
10. no R14.1 corrective round is required.

This task records already-granted Technical Lead approval.

The development agent must NOT grant approval itself.

This task also performs the formal closure and versioning of LegacyMapper V4.

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/GENERATED_ARTIFACT_POLICY.md`
6. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`
7. `docs/V4/V4_CONTRACT_FOUNDATION.md`
8. `docs/V4/V4_AI_HANDOVER.md`
9. `docs/V4/V4_PROPOSED_ROADMAP.md`
10. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
11. `docs/V4/V4_R13_CLOSURE_AND_VERSIONING_RESULT.md`
12. `docs/V4/V4_R14_MANUALS_AND_FINAL_BASELINE_RESULT.md`
13. `docs/V4/V4_USER_MANUAL.md`
14. `docs/V4/V4_DEVELOPER_MANUAL.md`
15. `docs/V4/V4_OPERATIONS_AND_RECOVERY_MANUAL.md`
16. `docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md`
17. `output/v4_r14/V4_FINAL_BASELINE.json`
18. `output/v4_r14/V4_FINAL_MANIFEST.json`

Repository artifacts are authoritative.

Do not use conversation history to reconstruct missing repository state.

---

# Expected Pre-Closure State

Verify:

```text
latest_completed_round = V4-R14
latest_approved_round = V4-R13

current_round_in_progress =
"V4-R14 (pending Technical Lead review)"

round_status =
V4-R14_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R14

tests = 1380

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

# Reviewed R14 Artifacts

Expected final baseline:

```text
output/v4_r14/V4_FINAL_BASELINE.json

SHA256=
d13e3807a12187b226ea55752ae0e9dccd2ad20c9dbe044360ffa48bca526d1e
```

Expected final manifest:

```text
output/v4_r14/V4_FINAL_MANIFEST.json

SHA256=
be398240a31137e7dea25fcaa7b3cfe6580d2557f990f7da884d5775f5c40551
```

Require:

```text
V4_FINAL_BASELINE_INTEGRITY=PASS
V4_FINAL_MANIFEST_INTEGRITY=PASS
```

If either reviewed artifact differs:

STOP.

Do not regenerate, repair, replace, or approve changed artifacts in the same task.

---

# Approved R14 State

Preserve:

```text
FINAL_TESTS=1380_PASS

FINAL_BASELINE_DETERMINISM=PASS
FINAL_MANIFEST_DETERMINISM=PASS

APPROVED_ARTIFACT_INTEGRITY=PASS
BROKEN_INTERNAL_REFERENCES=0

ONE_CANONICAL_KNOWLEDGE_SOURCE=PASS
TECHNICAL_LEAD_FINAL_APPROVAL_AUTHORITY=PASS
SOURCE_CODE_OPTIONAL=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS
R11_R12_SIBLING_PROJECTIONS=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0
PLUGIN_RUNTIME=NOT_IMPLEMENTED

SECURITY_GATE=PASS
REGRESSION_GATE=PASS

CRITICAL_OPEN=0
HIGH_OPEN=0
MEDIUM_OPEN=0
LOW_OPEN=0

V5_IMPLEMENTED=false

POST_V4_MAINTAINABILITY_REFACTOR=PLANNED

PRODUCTION_BEHAVIOR_CHANGED=false
```

No redesign is authorized.

---

# Final V4 Architecture

Preserve:

```text
INPUT MATERIAL
      ↓
INGESTION / NORMALIZATION
      ↓
EVIDENCE / CONTEXT
      ↓
ANALYSIS / CLASSIFICATION / RELATIONSHIP
      ↓
PROPOSALS
      ↓
TECHNICAL LEAD APPROVAL
      ↓
CANONICAL KNOWLEDGE SOURCE
      ↓
 ┌────┴─────┐
 ↓          ↓
R11         R12
Human       Plugin-facing
projection  machine projection
```

Required:

```text
ONE_CANONICAL_KNOWLEDGE_SOURCE
```

R11 and R12 remain projections only.

---

# Product Boundary

Preserve:

```text
LEGACYMAPPER_CONSTRUCTS_KNOWLEDGE
PLUGIN_CONSUMES_KNOWLEDGE
```

V4 does not implement Plugin runtime.

Do not implement Plugin agents, orchestration, planning, code generation, project modification, provider routing, model routing, or autonomous execution.

---

# Approval Authority

Preserve:

```text
TECHNICAL_LEAD_IS_FINAL_APPROVAL_AUTHORITY
AI_NEVER_GRANTS_APPROVAL
SYSTEM_NEVER_GRANTS_APPROVAL
```

Do not introduce RBAC.

---

# Knowledge Semantics

Preserve:

```text
MATERIAL != APPROVED_KNOWLEDGE

PROVENANCE != APPROVAL
PROVENANCE != AUTHORITY
PROVENANCE != STATUS

APPROVED != CONFIRMED

AI_INTERPRETATION != FACT
```

No semantic redesign is authorized.

---

# Source Code Optionality

Preserve support for:

```text
CODE_ONLY
CODE_AND_HUMAN_INFORMATION
HUMAN_INFORMATION_ONLY
PARTIAL_INFORMATION
```

Required:

```text
SOURCE_CODE_OPTIONAL=true
```

V4 remains source/projection-neutral at the knowledge layer.

Do not claim extraction-level technology agnosticism.

---

# R11 / R12 Boundary

Preserve:

```text
R11_SOURCE=R10_CANONICAL_KNOWLEDGE

R12_SOURCE=R10_CANONICAL_KNOWLEDGE
R11_DEPENDENCY=NONE

R11_R12_SIBLING_PROJECTIONS=true
```

R12 contract remains:

```text
LegacyMapperPluginKnowledge
1.0
```

---

# V5 Boundary

Record:

```text
V5_IMPLEMENTED=false
```

V5 remains future work.

Do not create a V5 roadmap or implementation in this task.

---

# Post-V4 Maintainability Refactor

The next planned development activity after formal V4 closure is:

```text
POST_V4_MAINTAINABILITY_REFACTOR=PLANNED
```

Suggested phase identity:

```text
V4.1 — Comprehensive Maintainability Refactor
```

Its governing invariants will be:

```text
REFRACTOR_GOAL=READABILITY_AND_MAINTAINABILITY
BEHAVIOR_CHANGE=FORBIDDEN
```

The refactor must be performed in later controlled rounds with Technical Lead review.

Do NOT begin it in this task.

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
```

and the R14 maintainability baseline.

---

# Final Regression

Run:

```text
python -m unittest discover -s tests
```

Require:

```text
>=1380 PASS
```

No test may be removed, skipped, weakened, or semantically altered during closure.

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

If validation fails:

STOP.

---

# Register R14 Approval

Update `PROJECT_STATE.json` using the existing schema.

Required semantic state:

```text
latest_completed_round = V4-R14
latest_approved_round = V4-R14

current_round_in_progress = null

round_status = V4_FORMALLY_CLOSED

next = POST_V4_MAINTAINABILITY_REFACTOR

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

If the existing schema has an explicit version/phase closure field, update it consistently.

Do not redesign the schema solely to add one.

---

# R14 Result Closure Section

Append only a closure section to:

```text
docs/V4/V4_R14_MANUALS_AND_FINAL_BASELINE_RESULT.md
```

Record at minimum:

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

MANUALS_DECISION=APPROVED
FINAL_BASELINE_DECISION=APPROVED
FINAL_MANIFEST_DECISION=APPROVED
CONTINUITY_CORRECTIONS_DECISION=APPROVED
CLOSURE_HELPER_PACKAGE_DECISION=APPROVED
MAINTAINABILITY_BASELINE_DECISION=APPROVED

R14_1_REQUIRED=false

ROUND_STATUS=APPROVED

DECISION=V4_R14_FORMALLY_APPROVED

NEXT=V4_FINAL_CLOSURE
```

Do not rewrite the reviewed R14 result.

---

# Final V4 Closure Record

Create:

```text
docs/V4/V4_FINAL_CLOSURE_RESULT.md
```

This is the authoritative final V4 closure record.

Report at minimum:

```text
STATUS

V4_CLOSED
HUMAN_REVIEW
APPROVAL_AUTHORITY

LATEST_COMPLETED_ROUND
LATEST_APPROVED_ROUND

R14_1_REQUIRED

MANUALS_DECISION
FINAL_BASELINE_DECISION
FINAL_MANIFEST_DECISION
CONTINUITY_CORRECTIONS_DECISION
CLOSURE_HELPER_PACKAGE_DECISION
MAINTAINABILITY_BASELINE_DECISION

FINAL_BASELINE_SHA256
FINAL_BASELINE_INTEGRITY

FINAL_MANIFEST_SHA256
FINAL_MANIFEST_INTEGRITY

APPROVED_ARTIFACT_INTEGRITY

TESTS
READINESS

SECURITY_GATE
REGRESSION_GATE

CRITICAL_OPEN
HIGH_OPEN
MEDIUM_OPEN
LOW_OPEN

ONE_CANONICAL_KNOWLEDGE_SOURCE
TECHNICAL_LEAD_FINAL_APPROVAL_AUTHORITY
SOURCE_CODE_OPTIONAL

R11_BOUNDARY
R12_BOUNDARY
R11_R12_SIBLING_PROJECTIONS

PLUGIN_CONTRACT_NAME
PLUGIN_CONTRACT_VERSION
PLUGIN_RUNTIME

V5_IMPLEMENTED

POST_V4_MAINTAINABILITY_REFACTOR
REFRACTOR_GOAL
REFRACTOR_BEHAVIOR_CHANGE

DEFERRED_DEBT

AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PRODUCTION_BEHAVIOR_CHANGED

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

DECISION
NEXT
```

---

# Expected Final Closure State

```text
STATUS=V4_FINAL_CLOSURE_COMPLETE

V4_CLOSED=true

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

LATEST_COMPLETED_ROUND=V4-R14
LATEST_APPROVED_ROUND=V4-R14

R14_1_REQUIRED=false

MANUALS_DECISION=APPROVED
FINAL_BASELINE_DECISION=APPROVED
FINAL_MANIFEST_DECISION=APPROVED
CONTINUITY_CORRECTIONS_DECISION=APPROVED
CLOSURE_HELPER_PACKAGE_DECISION=APPROVED
MAINTAINABILITY_BASELINE_DECISION=APPROVED

FINAL_BASELINE_INTEGRITY=PASS
FINAL_MANIFEST_INTEGRITY=PASS

APPROVED_ARTIFACT_INTEGRITY=PASS

TESTS=>=1380_PASS
READINESS=READY

SECURITY_GATE=PASS
REGRESSION_GATE=PASS

CRITICAL_OPEN=0
HIGH_OPEN=0
MEDIUM_OPEN=0
LOW_OPEN=0

ONE_CANONICAL_KNOWLEDGE_SOURCE=PASS
TECHNICAL_LEAD_FINAL_APPROVAL_AUTHORITY=PASS
SOURCE_CODE_OPTIONAL=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS
R11_R12_SIBLING_PROJECTIONS=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0
PLUGIN_RUNTIME=NOT_IMPLEMENTED

V5_IMPLEMENTED=false

POST_V4_MAINTAINABILITY_REFACTOR=PLANNED
REFRACTOR_GOAL=READABILITY_AND_MAINTAINABILITY
REFRACTOR_BEHAVIOR_CHANGE=FORBIDDEN

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PRODUCTION_BEHAVIOR_CHANGED=false

PROJECT_STATE=V4_FORMALLY_CLOSED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

DECISION=LEGACYMAPPER_V4_FORMALLY_CLOSED

NEXT=POST_V4_MAINTAINABILITY_REFACTOR
```

---

# Git Safety

Before staging inspect:

```text
git status
git diff
git diff --stat
```

No destructive Git operations.

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

Do not expose secret values.

Do not commit credentials, `.env`, tokens, private keys, caches, virtual environments, machine-local files, or unrelated heavy artifacts.

---

# Expected Checkpoint

Stage only relevant R14/V4 closure changes.

Expected files include:

```text
docs/V4/V4_USER_MANUAL.md
docs/V4/V4_DEVELOPER_MANUAL.md
docs/V4/V4_OPERATIONS_AND_RECOVERY_MANUAL.md
docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md

docs/V4/V4_R14_MANUALS_AND_FINAL_BASELINE_RESULT.md
docs/V4/V4_FINAL_CLOSURE_RESULT.md

AGENTS.md
docs/V4/V4_AI_HANDOVER.md
docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md

legacy_documenter/knowledge/closure/

tests/test_v4_r14_manuals_and_final_baseline.py

output/v4_r14/V4_FINAL_BASELINE.json
output/v4_r14/V4_FINAL_MANIFEST.json

prompts/V4/V4_R14_MANUALS_AND_FINAL_BASELINE.md
prompts/V4/V4_R14_APPROVAL_AND_V4_FINAL_CLOSURE.md

PROJECT_STATE.json
```

Do not include V5 implementation.

Do not include post-V4 refactor implementation.

Inspect staged diff before commit.

---

# Commit

Preferred commit message:

```text
Approve R14 and formally close LegacyMapper V4
```

Use one normal commit.

No amend.

No squash.

---

# Push

Push current branch normally to `origin`.

No force push.

If explicit user authorization is required:

STOP after commit and request it.

---

# Final Repository Continuity

After push, a fresh human or AI agent must be able to determine solely from repository artifacts:

```text
V1 = CLOSED
V2 = CLOSED
V3 = FORMALLY CLOSED
V4 = FORMALLY CLOSED

V4-R1 through V4-R14 = APPROVED

READINESS=READY

ONE_CANONICAL_KNOWLEDGE_SOURCE=true

PLUGIN_CONTRACT=LegacyMapperPluginKnowledge/1.0
PLUGIN_RUNTIME=NOT_IMPLEMENTED

V5_IMPLEMENTED=false

POST_V4_MAINTAINABILITY_REFACTOR=PLANNED

NEXT=POST_V4_MAINTAINABILITY_REFACTOR
```

No conversation memory may be required.

---

# Stop Condition

STOP after:

1. R14 approval registration;
2. V4 final closure record;
3. final regression/readiness;
4. repository continuity validation;
5. commit;
6. push;
7. clean Git status.

Do NOT begin:

```text
V5
POST_V4_MAINTAINABILITY_REFACTOR
PLUGIN_RUNTIME
```

The next action belongs to a new controlled phase.
