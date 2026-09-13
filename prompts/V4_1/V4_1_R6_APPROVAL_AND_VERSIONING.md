# LegacyMapper V4.1 — R6 Approval and Versioning

TASK=V4_1_R6_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
REFACTOR_ALLOWED=false
R7_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

V4.1-R6 — Gap Closure and Controlled Extraction

The Technical Lead explicitly accepts:

- Gate A completed before any production modification;
- all 8 R5 characterization gaps closed;
- 25 new gap-closure tests;
- DatabaseExtractor reclassified to READY_FOR_LIMITED_EXTRACTION;
- FunctionalFlowResolver reclassified to READY_FOR_LIMITED_EXTRACTION;
- R6_EXTRACTION_GATE=OPEN;
- six narrow extractions;
- nine deferred responsibility groups;
- discovery and deferral of FunctionalFlowResolver indexing because of `_call_ref` coupling;
- preservation of DatabaseExtractor's order-sensitive core;
- preservation of FunctionalFlowResolver traversal and path-identity core;
- preservation of the `_path_id` / `_path_identities` patch point;
- public imports and signatures preserved;
- result/order/identifier/exception/state equivalence;
- approved historical artifacts unchanged;
- R0 frozen inventory untouched;
- PRODUCTION_BEHAVIOR_CHANGED=false;
- no R6.1 corrective round is required.

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
10. docs/V4_1/V4_1_R5_CLOSURE_AND_VERSIONING_RESULT.md
11. docs/V4_1/V4_1_R6_GAP_CLOSURE_AND_CONTROLLED_EXTRACTION_RESULT.md
12. output/v4_1_r6/V4_1_R6_EXTRACTION_EQUIVALENCE.json
13. output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json

Repository artifacts are authoritative.

---

# Expected Reviewed State

Require:

latest_completed_round = V4.1-R6
latest_approved_round = V4.1-R5

current_round_in_progress =
"V4.1-R6 (pending Technical Lead review)"

round_status =
V4_1_R6_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R6

tests = 1561
readiness = READY

provider_calls = 0
real_llm_calls = 0

If materially different:

STOP.

---

# Reviewed R6 Artifact

Expected:

output/v4_1_r6/V4_1_R6_EXTRACTION_EQUIVALENCE.json

SHA256=
bb60f1bd1b527003b2cbfdfcd98f13d77ca3cff246dc9b23c820da5378861ab1

Recompute.

Require:

R6_EQUIVALENCE_ARTIFACT_INTEGRITY=PASS

If different:

STOP.

Do not regenerate or repair it.

---

# Gate A Approval

Record:

GATE_A_DECISION=APPROVED

DATABASE_GAPS_CLOSED=4
FLOW_GAPS_CLOSED=4
TOTAL_GAPS_CLOSED=8

All eight gap-closure results are approved.

Do not reinterpret or reopen them during closure.

---

# Readiness Decisions

Record:

DATABASE_EXTRACTOR_R6_READINESS=READY_FOR_LIMITED_EXTRACTION
FLOW_RESOLVER_R6_READINESS=READY_FOR_LIMITED_EXTRACTION

These statuses mean limited, evidence-backed extraction only.

They do not authorize future extraction of deferred groups.

---

# Gate B Approval

Record:

GATE_B_DECISION=APPROVED

AUTHORIZED_EXTRACTIONS=6
DEFERRED_EXTRACTIONS=9
EXTRACTIONS_PERFORMED=6

Approved DatabaseExtractor extractions:

1. logical-line reassembly
2. string/token parsing
3. classification/normalization

Approved FunctionalFlowResolver extractions:

4. graph construction
5. key/label derivation
6. report composition

No additional extraction is authorized during closure.

---

# Approved Production Structure

Require these new internal modules to remain:

legacy_documenter/extractors/_database_line_scanner.py
legacy_documenter/extractors/_database_token_parsing.py
legacy_documenter/extractors/_database_classification.py

legacy_documenter/analysis/_flow_graph_construction.py
legacy_documenter/analysis/_flow_key_labels.py
legacy_documenter/analysis/_flow_report_composition.py

Existing facades remain:

legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py

---

# Deferred Responsibility Groups

Record and preserve as deferred:

DatabaseExtractor:

- variable/type-state tracking
- operation-detection-and-emission
- parameter-extraction-and-normalization
- extract() orchestration

FunctionalFlowResolver:

- indexing
- path-identity-and-construction
- confidence/status derivation
- _walk graph traversal
- resolve() orchestration

Do not modify these during closure.

---

# Path Identity Compatibility

Require:

FLOW_RESOLVER_PATH_ID_PATCH_POINT_PRESERVED=PASS

Preserve untouched:

_path_id
_path_identities
_add_path
_call_ref
_stable_id

No redesign is authorized.

---

# Compatibility

Require:

DATABASE_EXTRACTOR_PUBLIC_IMPORTS_PRESERVED=PASS
DATABASE_EXTRACTOR_PUBLIC_SIGNATURES_PRESERVED=PASS

FLOW_RESOLVER_PUBLIC_IMPORTS_PRESERVED=PASS
FLOW_RESOLVER_PUBLIC_SIGNATURES_PRESERVED=PASS

Existing extracted helper methods that remain callable through the original
classes must continue resolving.

No cleanup/removal of compatibility delegates during closure.

---

# Behavioral Equivalence

Require:

DATABASE_RESULT_EQUIVALENCE=PASS
DATABASE_ORDERING_EQUIVALENCE=PASS
DATABASE_IDENTIFIER_EQUIVALENCE=NOT_APPLICABLE
DATABASE_EXCEPTION_EQUIVALENCE=PASS

FLOW_RESULT_EQUIVALENCE=PASS
FLOW_ORDERING_EQUIVALENCE=PASS
FLOW_IDENTIFIER_EQUIVALENCE=PASS
FLOW_EXCEPTION_EQUIVALENCE=PASS
FLOW_STATE_REUSE_EQUIVALENCE=PASS

Do not change implementation to simplify these contracts.

---

# Approved Artifact Integrity

Recompute and preserve:

output/v4_r14/V4_FINAL_BASELINE.json

output/v4_r14/V4_FINAL_MANIFEST.json

output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json

output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json

output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json

output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json

output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json

Require:

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

Do not regenerate historical artifacts.

---

# R0 Frozen Inventory

Require:

R0_FROZEN_INVENTORY_MODIFIED=false

Authorized live-structure changes from R6 are accepted.

Do not modify:

output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
output/v4_1_r0/V4_1_REFACTOR_PLAN.json

Do not weaken comparison logic.

---

# Debt Decisions

Preserve:

DEBT_002_DECISION=RESOLVED_UNCHANGED
DEBT_003_DECISION=RESOLVED_UNCHANGED
TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

R6 resolves none of these further.

---

# Scope Fence

Do not modify structurally:

legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py

Do not:

- extract deferred DatabaseExtractor groups;
- extract deferred FunctionalFlowResolver groups;
- touch `_walk`;
- redesign `_path_id`;
- continue broad TD-005 typing work;
- rename copilot_pilot.py;
- restructure legacy_documenter/context/;
- perform R7 exception cleanup;
- begin V5;
- implement Plugin runtime.

---

# Regression

Run:

python -m unittest discover -s tests

Require:

>=1561 PASS
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

# Production Classification

Preserve:

PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false

Closure itself must make no further production change.

---

# PROJECT_STATE

Register Technical Lead approval:

latest_completed_round = V4.1-R6
latest_approved_round = V4.1-R6

current_round_in_progress = null

round_status = V4_1_R6_APPROVED

next = V4.1-R7

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0

V4 remains formally closed.

---

# R6 Result Closure Section

Append only a closure section to:

docs/V4_1/V4_1_R6_GAP_CLOSURE_AND_CONTROLLED_EXTRACTION_RESULT.md

Record:

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

GATE_A_DECISION=APPROVED
GATE_B_DECISION=APPROVED

TOTAL_GAPS_CLOSED=8

DATABASE_EXTRACTOR_R6_READINESS=READY_FOR_LIMITED_EXTRACTION
FLOW_RESOLVER_R6_READINESS=READY_FOR_LIMITED_EXTRACTION

AUTHORIZED_EXTRACTIONS=6
DEFERRED_EXTRACTIONS=9

R6_EQUIVALENCE_DECISION=APPROVED

R6_1_REQUIRED=false

ROUND_STATUS=APPROVED
DECISION=V4_1_R6_FORMALLY_APPROVED
NEXT=V4.1-R7

Do not rewrite the reviewed body.

---

# Closure Result

Create:

docs/V4_1/V4_1_R6_CLOSURE_AND_VERSIONING_RESULT.md

Report at minimum:

STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

GATE_A_DECISION
GATE_B_DECISION

DATABASE_GAPS_CLOSED
FLOW_GAPS_CLOSED
TOTAL_GAPS_CLOSED

DATABASE_EXTRACTOR_R6_READINESS
FLOW_RESOLVER_R6_READINESS

AUTHORIZED_EXTRACTIONS
DEFERRED_EXTRACTIONS
EXTRACTIONS_PERFORMED

R6_EQUIVALENCE_ARTIFACT_SHA256
R6_EQUIVALENCE_ARTIFACT_INTEGRITY
R6_EQUIVALENCE_DECISION

DATABASE_EXTRACTOR_PUBLIC_IMPORTS_PRESERVED
DATABASE_EXTRACTOR_PUBLIC_SIGNATURES_PRESERVED

FLOW_RESOLVER_PUBLIC_IMPORTS_PRESERVED
FLOW_RESOLVER_PUBLIC_SIGNATURES_PRESERVED
FLOW_RESOLVER_PATH_ID_PATCH_POINT_PRESERVED

DATABASE_RESULT_EQUIVALENCE
DATABASE_ORDERING_EQUIVALENCE
DATABASE_IDENTIFIER_EQUIVALENCE
DATABASE_EXCEPTION_EQUIVALENCE

FLOW_RESULT_EQUIVALENCE
FLOW_ORDERING_EQUIVALENCE
FLOW_IDENTIFIER_EQUIVALENCE
FLOW_EXCEPTION_EQUIVALENCE
FLOW_STATE_REUSE_EQUIVALENCE

APPROVED_ARTIFACT_HASHES_UNCHANGED
R0_FROZEN_INVENTORY_MODIFIED

DEBT_002_DECISION
DEBT_003_DECISION
TD_005_DECISION

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

STATUS=V4_1_R6_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

GATE_A_DECISION=APPROVED
GATE_B_DECISION=APPROVED

DATABASE_GAPS_CLOSED=4
FLOW_GAPS_CLOSED=4
TOTAL_GAPS_CLOSED=8

DATABASE_EXTRACTOR_R6_READINESS=READY_FOR_LIMITED_EXTRACTION
FLOW_RESOLVER_R6_READINESS=READY_FOR_LIMITED_EXTRACTION

AUTHORIZED_EXTRACTIONS=6
DEFERRED_EXTRACTIONS=9
EXTRACTIONS_PERFORMED=6

R6_EQUIVALENCE_ARTIFACT_INTEGRITY=PASS
R6_EQUIVALENCE_DECISION=APPROVED

DATABASE_EXTRACTOR_PUBLIC_IMPORTS_PRESERVED=PASS
DATABASE_EXTRACTOR_PUBLIC_SIGNATURES_PRESERVED=PASS

FLOW_RESOLVER_PUBLIC_IMPORTS_PRESERVED=PASS
FLOW_RESOLVER_PUBLIC_SIGNATURES_PRESERVED=PASS
FLOW_RESOLVER_PATH_ID_PATCH_POINT_PRESERVED=PASS

DATABASE_RESULT_EQUIVALENCE=PASS
DATABASE_ORDERING_EQUIVALENCE=PASS
DATABASE_IDENTIFIER_EQUIVALENCE=NOT_APPLICABLE
DATABASE_EXCEPTION_EQUIVALENCE=PASS

FLOW_RESULT_EQUIVALENCE=PASS
FLOW_ORDERING_EQUIVALENCE=PASS
FLOW_IDENTIFIER_EQUIVALENCE=PASS
FLOW_EXCEPTION_EQUIVALENCE=PASS
FLOW_STATE_REUSE_EQUIVALENCE=PASS

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
R0_FROZEN_INVENTORY_MODIFIED=false

DEBT_002_DECISION=RESOLVED_UNCHANGED
DEBT_003_DECISION=RESOLVED_UNCHANGED
TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

TESTS=>=1561_PASS
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

PROJECT_STATE=V4_1_R6_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_COMMIT_HASH=<ACTUAL_COMMIT_HASH>
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_1_R6_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4.1-R7

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

Approve LegacyMapper V4.1-R6 controlled orchestrator extraction

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

V4.1-R0 through V4.1-R6 = APPROVED

DUP-001 = RESOLVED
DEBT-001 = RESOLVED
DEBT-002 = RESOLVED
DEBT-003 = RESOLVED

TD-005 = PARTIALLY_RESOLVED

DatabaseExtractor = READY_FOR_LIMITED_EXTRACTION
FunctionalFlowResolver = READY_FOR_LIMITED_EXTRACTION

R6 authorized extractions = 6
R6 deferred extractions = 9

TESTS >= 1561 PASS

BEHAVIOR_CHANGE = FORBIDDEN

V4.1-R7 = NEXT

No conversation memory may be required.

---

# Stop Condition

STOP after:

1. R6 approval registration;
2. closure result creation;
3. full regression;
4. readiness verification;
5. normal commit;
6. real commit hash recording;
7. push;
8. clean Git status.

Do NOT:

- begin R7;
- perform additional extraction;
- touch deferred groups;
- modify resume.py;
- modify deep_source.py;
- continue TD-005 typing work;
- rename copilot_pilot.py;
- restructure context/;
- begin V5;
- implement Plugin runtime.