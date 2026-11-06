# LegacyMapper V4.1 — R5 Approval and Versioning

TASK=V4_1_R5_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
REFACTOR_ALLOWED=false
R6_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

V4.1-R5 — Risky Orchestrators Characterization

The Technical Lead explicitly accepts:

- R5_MODE=CHARACTERIZATION_ONLY;
- zero production-code modification;
- 24 DatabaseExtractor characterization tests;
- 26 FunctionalFlowResolver characterization tests;
- 1536 total passing tests;
- DatabaseExtractor STATELESS classification;
- FunctionalFlowResolver STATEFUL_RESET_PER_OPERATION classification;
- the identified responsibility maps;
- the identified ordering/state/exception/side-effect contracts;
- the caller and compatibility inventories;
- the existing `_path_id` monkeypatch dependency;
- DATABASE_EXTRACTOR_R6_READINESS=PARTIALLY_READY;
- FLOW_RESOLVER_R6_READINESS=PARTIALLY_READY;
- the eight remaining characterization gaps;
- approved-artifact integrity;
- R0 frozen inventory untouched;
- PRODUCTION_CODE_CHANGED=false;
- PRODUCTION_BEHAVIOR_CHANGED=false;
- no R5.1 corrective round is required.

Important:

Approval of R5 does NOT authorize immediate production extraction in R6.

R6 must first close the eight explicitly recorded missing-characterization items
before any affected responsibility group may be extracted.

The development agent does not grant this approval.

---

# Required Reading

Read:

1. CLAUDE.md
2. AGENTS.md
3. PROJECT_STATE.json
4. docs/V4/V4_FINAL_CLOSURE_RESULT.md
5. docs/V4_1/V4_1_R0_CLOSURE_AND_VERSIONING_RESULT.md
6. docs/V4_1/V4_1_R1_CLOSURE_AND_VERSIONING_RESULT.md
7. docs/V4_1/V4_1_R2_CLOSURE_AND_VERSIONING_RESULT.md
8. docs/V4_1/V4_1_R3_CLOSURE_AND_VERSIONING_RESULT.md
9. docs/V4_1/V4_1_R4_CLOSURE_AND_VERSIONING_RESULT.md
10. docs/V4_1/V4_1_R5_RISKY_ORCHESTRATORS_CHARACTERIZATION_RESULT.md
11. output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json
12. output/v4_1_r0/V4_1_REFACTOR_PLAN.json

Repository artifacts are authoritative.

---

# Expected Reviewed State

Require:

latest_completed_round = V4.1-R5
latest_approved_round = V4.1-R4

current_round_in_progress =
"V4.1-R5 (pending Technical Lead review)"

round_status =
V4_1_R5_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R5

tests = 1536
readiness = READY

provider_calls = 0
real_llm_calls = 0

If materially different:

STOP.

---

# Reviewed Characterization Artifact

Expected:

output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json

SHA256=
04c82d51b17664630adcafe26dd343d5f0740932904c77dd7a458029d547be32

Recompute.

Require:

ORCHESTRATOR_CHARACTERIZATION_ARTIFACT_INTEGRITY=PASS

If different:

STOP.

Do not regenerate or repair it.

---

# R5 Scope Decision

Record:

R5_MODE_DECISION=CHARACTERIZATION_ONLY_APPROVED

TARGETS_APPROVED=
legacy_documenter/extractors/database_extractor.py,
legacy_documenter/analysis/flow_resolver.py

The narrower R5 scope is approved.

Do not add the five broader R0 files during closure.

---

# DatabaseExtractor Decision

Record:

DATABASE_EXTRACTOR_CHARACTERIZATION_DECISION=APPROVED

DATABASE_EXTRACTOR_STATE_MODEL=STATELESS

DATABASE_EXTRACTOR_R6_READINESS=PARTIALLY_READY

Preserve the four missing characterization items exactly as recorded by R5:

1. branch-order interaction between operation-detection regexes on the same physical line;
2. `_split_args` edge cases including nested parentheses and quoted commas;
3. isolated variable/type-state tracking behavior;
4. multiple classes with repeated variable names and class scoping.

Do not mark:

DATABASE_EXTRACTOR_R6_READINESS=READY_FOR_CONTROLLED_EXTRACTION

during closure.

---

# FunctionalFlowResolver Decision

Record:

FLOW_RESOLVER_CHARACTERIZATION_DECISION=APPROVED

FLOW_RESOLVER_STATE_MODEL=STATEFUL_RESET_PER_OPERATION

FLOW_RESOLVER_R6_READINESS=PARTIALLY_READY

Preserve the four missing characterization items exactly as recorded by R5:

1. pin `_stable_id` to exact known deterministic values;
2. characterize two entry points sharing an overlapping graph in one resolve call;
3. characterize `_flow_status` precedence when cycle and truncated depth coexist;
4. characterize a method containing both direct data-access operations and outgoing calls.

Do not mark:

FLOW_RESOLVER_R6_READINESS=READY_FOR_CONTROLLED_EXTRACTION

during closure.

---

# R6 Safety Boundary

Record explicitly:

R6_INITIAL_PHASE_REQUIRED=CHARACTERIZATION_GAP_CLOSURE

R6_PRODUCTION_EXTRACTION_PREAUTHORIZED=false

R6_EXTRACTION_REQUIRES_NEW_GATE=true

R6 may later extract only responsibility groups whose characterization is
sufficient after those gaps are closed.

PARTIALLY_READY is not equivalent to extraction approval.

---

# Existing Compatibility Constraint

Preserve as explicit architectural evidence:

FLOW_RESOLVER_PATH_ID_PATCH_POINT_PRESENT=true

A pre-existing test modifies:

resolver._path_id
resolver._path_identities

Any future R6 work affecting path identity must explicitly preserve or redesign
this compatibility under Technical Lead review.

No such redesign is authorized during R5 closure.

---

# Approved Artifact Integrity

Recompute and preserve:

output/v4_r14/V4_FINAL_BASELINE.json

output/v4_r14/V4_FINAL_MANIFEST.json

output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json

output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json

output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json

output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json

Require:

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

Do not regenerate historical artifacts.

---

# R0 Frozen Inventory

Require:

R0_FROZEN_INVENTORY_MODIFIED=false

No production code changed in R5.

Do not alter:

output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
output/v4_1_r0/V4_1_REFACTOR_PLAN.json

---

# Debt Decisions

Record:

DEBT_002_DECISION=RESOLVED_UNCHANGED
DEBT_003_DECISION=RESOLVED_UNCHANGED
TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

R5 resolves none of these further.

---

# Scope Fence

Do not modify production code.

In particular do not modify:

legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py
legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py

Do not:

- extract helpers;
- rename functions;
- move classes;
- modify signatures;
- add production wrappers;
- add production aliases;
- rename copilot_pilot.py;
- restructure context/;
- continue TD-005 typing work;
- begin R6;
- begin V5;
- implement Plugin runtime.

Require:

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

---

# Regression

Run:

python -m unittest discover -s tests

Require:

>=1536 PASS
FAIL=0
SKIP=0

No test may be removed, skipped or weakened.

---

# Readiness

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

---

# V4 Preservation

Require:

V4_CONTRACTS_UNCHANGED=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0

PLUGIN_RUNTIME=NOT_IMPLEMENTED
V5_IMPLEMENTED=false

---

# PROJECT_STATE

Register Technical Lead approval:

latest_completed_round = V4.1-R5
latest_approved_round = V4.1-R5

current_round_in_progress = null

round_status = V4_1_R5_APPROVED

next = V4.1-R6

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0

V4 remains formally closed.

---

# R5 Result Closure Section

Append only a closure section to:

docs/V4_1/V4_1_R5_RISKY_ORCHESTRATORS_CHARACTERIZATION_RESULT.md

Record:

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R5_MODE_DECISION=CHARACTERIZATION_ONLY_APPROVED

DATABASE_EXTRACTOR_CHARACTERIZATION_DECISION=APPROVED
DATABASE_EXTRACTOR_R6_READINESS=PARTIALLY_READY

FLOW_RESOLVER_CHARACTERIZATION_DECISION=APPROVED
FLOW_RESOLVER_R6_READINESS=PARTIALLY_READY

CHARACTERIZATION_GAPS=8

R6_INITIAL_PHASE_REQUIRED=CHARACTERIZATION_GAP_CLOSURE
R6_PRODUCTION_EXTRACTION_PREAUTHORIZED=false

R5_1_REQUIRED=false

ROUND_STATUS=APPROVED
DECISION=V4_1_R5_FORMALLY_APPROVED
NEXT=V4.1-R6

Do not rewrite the reviewed body.

---

# Closure Result

Create:

docs/V4_1/V4_1_R5_CLOSURE_AND_VERSIONING_RESULT.md

Report at minimum:

STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

R5_MODE_DECISION

DATABASE_EXTRACTOR_CHARACTERIZATION_DECISION
DATABASE_EXTRACTOR_STATE_MODEL
DATABASE_EXTRACTOR_R6_READINESS

FLOW_RESOLVER_CHARACTERIZATION_DECISION
FLOW_RESOLVER_STATE_MODEL
FLOW_RESOLVER_R6_READINESS

CHARACTERIZATION_GAPS

R6_INITIAL_PHASE_REQUIRED
R6_PRODUCTION_EXTRACTION_PREAUTHORIZED
R6_EXTRACTION_REQUIRES_NEW_GATE

FLOW_RESOLVER_PATH_ID_PATCH_POINT_PRESENT

ORCHESTRATOR_CHARACTERIZATION_ARTIFACT_SHA256
ORCHESTRATOR_CHARACTERIZATION_ARTIFACT_INTEGRITY
ORCHESTRATOR_CHARACTERIZATION_DECISION

NON_TARGET_HIGH_RISK_MODULES_PRESERVED

DEBT_002_DECISION
DEBT_003_DECISION
TD_005_DECISION

APPROVED_ARTIFACT_HASHES_UNCHANGED
R0_FROZEN_INVENTORY_MODIFIED

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

---

# Expected Success State

STATUS=V4_1_R5_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R5_MODE_DECISION=CHARACTERIZATION_ONLY_APPROVED

DATABASE_EXTRACTOR_CHARACTERIZATION_DECISION=APPROVED
DATABASE_EXTRACTOR_STATE_MODEL=STATELESS
DATABASE_EXTRACTOR_R6_READINESS=PARTIALLY_READY

FLOW_RESOLVER_CHARACTERIZATION_DECISION=APPROVED
FLOW_RESOLVER_STATE_MODEL=STATEFUL_RESET_PER_OPERATION
FLOW_RESOLVER_R6_READINESS=PARTIALLY_READY

CHARACTERIZATION_GAPS=8

R6_INITIAL_PHASE_REQUIRED=CHARACTERIZATION_GAP_CLOSURE
R6_PRODUCTION_EXTRACTION_PREAUTHORIZED=false
R6_EXTRACTION_REQUIRES_NEW_GATE=true

FLOW_RESOLVER_PATH_ID_PATCH_POINT_PRESENT=true

ORCHESTRATOR_CHARACTERIZATION_ARTIFACT_INTEGRITY=PASS
ORCHESTRATOR_CHARACTERIZATION_DECISION=APPROVED

NON_TARGET_HIGH_RISK_MODULES_PRESERVED=PASS

DEBT_002_DECISION=RESOLVED_UNCHANGED
DEBT_003_DECISION=RESOLVED_UNCHANGED
TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
R0_FROZEN_INVENTORY_MODIFIED=false

TESTS=>=1536_PASS
READINESS=READY

V4_CONTRACTS_UNCHANGED=PASS
R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R5_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_COMMIT_HASH=<ACTUAL_COMMIT_HASH>
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_1_R5_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4.1-R6

---

# Git Safety

Inspect:

git status
git diff
git diff --stat

Forbidden:

git reset --hard
git clean
git restore .
git checkout -- .
git rebase
git amend
git squash
git push --force

---

# Secret Scan

Require:

SECRET_SCAN=PASS

Do not expose secret values.

---

# Commit

Preferred message:

Approve LegacyMapper V4.1-R5 risky orchestrator characterization

Use one normal commit.

No amend.
No squash.

After commit record the real hash using:

git rev-parse HEAD

The closure document must contain the actual commit hash.

---

# Push

Push normally to origin.

No force push.

After push require:

git status --short

to be empty.

---

# Repository Continuity

After closure a fresh human or AI agent must determine:

V4 = FORMALLY CLOSED

V4.1-R0 = APPROVED
V4.1-R1 = APPROVED
V4.1-R2 = APPROVED
V4.1-R3 = APPROVED
V4.1-R4 = APPROVED
V4.1-R5 = APPROVED

DUP-001 = RESOLVED
DEBT-001 = RESOLVED
DEBT-002 = RESOLVED
DEBT-003 = RESOLVED

TD-005 = PARTIALLY_RESOLVED

DatabaseExtractor R6 readiness = PARTIALLY_READY
FunctionalFlowResolver R6 readiness = PARTIALLY_READY

R6 initial phase = characterization gap closure
R6 production extraction preauthorized = false

TESTS >= 1536 PASS

BEHAVIOR_CHANGE = FORBIDDEN

V4.1-R6 = NEXT

No conversation memory may be required.

---

# Stop Condition

STOP after:

1. R5 approval registration;
2. closure result creation;
3. full regression;
4. readiness verification;
5. normal commit;
6. real commit hash recording;
7. push;
8. clean Git status.

Do NOT:

- begin R6;
- modify either risky orchestrator;
- close any of the eight gaps;
- extract any helper;
- modify resume.py;
- modify deep_source.py;
- continue TD-005 typing work;
- rename copilot_pilot.py;
- restructure context/;
- begin V5;
- implement Plugin runtime.