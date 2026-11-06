# LegacyMapper V4.1 — R7 Approval and Versioning

TASK=V4_1_R7_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
REFACTOR_ALLOWED=false
R8_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

V4.1-R7 — Exception Boundaries and Adapter Cleanup

The Technical Lead explicitly accepts:

- R7_MODE=CHARACTERIZE_THEN_NARROW_CLEANUP;
- baseline 1561 passing tests;
- final 1566 passing tests;
- 5 new characterization tests;
- live exception-boundary inventory;
- six provider-boundary files kept out of production cleanup;
- resume.py characterized but deferred;
- exactly one SAFE_LOCAL_CLEANUP;
- exactly one cleanup performed;
- consolidation of the three semantically-identical extractor handlers in
  legacy_documenter/main.py::analyze_repository;
- new private `_extract_into(...)` helper;
- same broad caught exception type;
- same structured error result;
- same call ordering;
- same partial-result behavior;
- same public imports/signatures;
- provider production changes = 0;
- R6 deferred groups preserved;
- approved artifact integrity;
- R0 frozen inventory untouched;
- PRODUCTION_BEHAVIOR_CHANGED=false;
- no R7.1 corrective round is required.

The development agent does not grant this approval.

---

# Required Reading

Read in full:

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
11. docs/V4_1/V4_1_R6_CLOSURE_AND_VERSIONING_RESULT.md
12. docs/V4_1/V4_1_R7_EXCEPTION_BOUNDARIES_AND_ADAPTER_CLEANUP_RESULT.md
13. output/v4_1_r7/V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json
14. output/v4_1_r0/V4_1_REFACTOR_PLAN.json

Repository artifacts are authoritative.

---

# Expected Reviewed State

Require:

latest_completed_round = V4.1-R7
latest_approved_round = V4.1-R6

current_round_in_progress =
"V4.1-R7 (pending Technical Lead review)"

round_status =
V4_1_R7_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R7

tests = 1566
readiness = READY

provider_calls = 0
real_llm_calls = 0

If materially different:

STOP.

---

# Reviewed R7 Artifact

Expected:

output/v4_1_r7/V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json

SHA256=
ccb21db6b051b15b19c617dc387f28d7910386e634036f777b2a7eff374a5d4d

Recompute.

Require:

R7_EQUIVALENCE_ARTIFACT_INTEGRITY=PASS

If different:

STOP.

Do not regenerate or repair it.

---

# R7 Scope Decision

Record:

R7_MODE_DECISION=CHARACTERIZE_THEN_NARROW_CLEANUP_APPROVED

EXCEPTION_BOUNDARY_INVENTORY_DECISION=APPROVED

IN_SCOPE_CANDIDATES=1
SAFE_LOCAL_CLEANUPS=1
AUTHORIZED_CLEANUPS=1
CLEANUPS_PERFORMED=1

No additional cleanup is authorized during closure.

---

# Approved Cleanup

Approved production modification:

legacy_documenter/main.py

Approved change:

three duplicated extraction try/except blocks consolidated behind the private
helper:

_extract_into(...)

The following behavior is approved as preserved:

- caught exception type remains Exception;
- error dictionary shape remains identical;
- error message remains str(exc);
- extractor label remains identical;
- source file value remains identical;
- sink append behavior remains identical;
- per-file ordering remains identical;
- extractor failures remain isolated;
- partial successful results remain preserved;
- subsequent extractors continue executing after one failure.

Do not further simplify this helper during closure.

---

# Provider Boundary Decision

Require:

OUT_OF_SCOPE_PROVIDER_BOUNDARIES=6
PROVIDER_BOUNDARY_PRODUCTION_CHANGES=0

Preserve unchanged:

legacy_documenter/documentation/generator.py
legacy_documenter/documentation/hierarchical.py
legacy_documenter/documentation/systematic.py
legacy_documenter/llm/copilot_pilot.py
legacy_documenter/llm/providers/copilot.py
legacy_documenter/llm/providers/gemini.py

No provider taxonomy redesign is authorized.

Do not:

- narrow broad provider exceptions;
- broaden existing specific exceptions;
- add retries;
- introduce ProviderException;
- introduce LLMException;
- normalize provider errors;
- introduce global middleware.

---

# High-Risk Decision

Record:

OUT_OF_SCOPE_HIGH_RISK=1

legacy_documenter/documentation/resume.py

Preserve it unchanged.

Its exception boundaries remain deferred because they are entangled with
provider.structured_generate and store.persist behavior.

Do not reinterpret this deferral during closure.

---

# R6 Preservation

Require:

R6_DEFERRED_GROUPS_PRESERVED=PASS

Do not modify:

legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py

Do not touch:

_path_id
_path_identities
_add_path
_call_ref
_stable_id

Do not alter the six R6 internal extraction modules.

---

# Compatibility and Equivalence

Require:

PUBLIC_IMPORT_COMPATIBILITY=PASS
PUBLIC_SIGNATURE_COMPATIBILITY=PASS

SUCCESS_RESULT_EQUIVALENCE=PASS
FAILURE_RESULT_EQUIVALENCE=PASS

EXCEPTION_TYPE_EQUIVALENCE=PASS
EXCEPTION_MESSAGE_EQUIVALENCE=PASS

ORDERING_EQUIVALENCE=PASS
SIDE_EFFECT_EQUIVALENCE=PASS
PARTIAL_RESULT_EQUIVALENCE=PASS

No implementation changes are authorized to "improve" these results.

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

output/v4_1_r6/V4_1_R6_EXTRACTION_EQUIVALENCE.json

Require:

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

Do not regenerate historical artifacts.

---

# R0 Frozen Inventory

Require:

R0_FROZEN_INVENTORY_MODIFIED=false

Do not modify:

output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
output/v4_1_r0/V4_1_REFACTOR_PLAN.json

The already-authorized live comparison update for main.py is accepted.

Do not weaken comparison assertions further.

---

# Debt Decisions

Preserve:

DEBT_002_DECISION=RESOLVED_UNCHANGED
DEBT_003_DECISION=RESOLVED_UNCHANGED
TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

R7 does not resolve these further.

---

# Scope Fence

Do not modify production code during closure.

In particular do not modify:

legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py
legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py

Do not:

- perform additional exception cleanup;
- modify providers;
- change exception taxonomies;
- change `_extract_into`;
- continue TD-005 broadly;
- rename copilot_pilot.py;
- restructure legacy_documenter/context/;
- begin R8;
- begin V5;
- implement Plugin runtime.

Closure itself must make no additional production changes.

---

# Regression

Run:

python -m unittest discover -s tests

Require:

>=1566 PASS
FAIL=0
SKIP=0

No test may be removed, skipped, or weakened.

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

Closure itself must not change production code.

---

# PROJECT_STATE

Register Technical Lead approval:

latest_completed_round = V4.1-R7
latest_approved_round = V4.1-R7

current_round_in_progress = null

round_status = V4_1_R7_APPROVED

next = V4.1-R8

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0

V4 remains formally closed.

---

# R7 Result Closure Section

Append only a closure section to:

docs/V4_1/V4_1_R7_EXCEPTION_BOUNDARIES_AND_ADAPTER_CLEANUP_RESULT.md

Record:

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R7_MODE_DECISION=CHARACTERIZE_THEN_NARROW_CLEANUP_APPROVED

EXCEPTION_BOUNDARY_INVENTORY_DECISION=APPROVED

SAFE_LOCAL_CLEANUPS=1
AUTHORIZED_CLEANUPS=1
CLEANUPS_PERFORMED=1

PROVIDER_BOUNDARY_PRODUCTION_CHANGES=0
R6_DEFERRED_GROUPS_PRESERVED=PASS

R7_EQUIVALENCE_DECISION=APPROVED

R7_1_REQUIRED=false

ROUND_STATUS=APPROVED
DECISION=V4_1_R7_FORMALLY_APPROVED
NEXT=V4.1-R8

Do not rewrite the reviewed body.

---

# Closure Result

Create:

docs/V4_1/V4_1_R7_CLOSURE_AND_VERSIONING_RESULT.md

Report at minimum:

STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

R7_MODE_DECISION
EXCEPTION_BOUNDARY_INVENTORY_DECISION

IN_SCOPE_CANDIDATES
OUT_OF_SCOPE_PROVIDER_BOUNDARIES
OUT_OF_SCOPE_HIGH_RISK

SAFE_LOCAL_CLEANUPS
AUTHORIZED_CLEANUPS
DEFERRED_CLEANUPS
CLEANUPS_PERFORMED

R7_EQUIVALENCE_ARTIFACT_SHA256
R7_EQUIVALENCE_ARTIFACT_INTEGRITY
R7_EQUIVALENCE_DECISION

PUBLIC_IMPORT_COMPATIBILITY
PUBLIC_SIGNATURE_COMPATIBILITY

SUCCESS_RESULT_EQUIVALENCE
FAILURE_RESULT_EQUIVALENCE
EXCEPTION_TYPE_EQUIVALENCE
EXCEPTION_MESSAGE_EQUIVALENCE
ORDERING_EQUIVALENCE
SIDE_EFFECT_EQUIVALENCE
PARTIAL_RESULT_EQUIVALENCE

PROVIDER_BOUNDARY_PRODUCTION_CHANGES
R6_DEFERRED_GROUPS_PRESERVED

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

STATUS=V4_1_R7_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R7_MODE_DECISION=CHARACTERIZE_THEN_NARROW_CLEANUP_APPROVED

EXCEPTION_BOUNDARY_INVENTORY_DECISION=APPROVED

IN_SCOPE_CANDIDATES=1
OUT_OF_SCOPE_PROVIDER_BOUNDARIES=6
OUT_OF_SCOPE_HIGH_RISK=1

SAFE_LOCAL_CLEANUPS=1
AUTHORIZED_CLEANUPS=1
DEFERRED_CLEANUPS=1
CLEANUPS_PERFORMED=1

R7_EQUIVALENCE_ARTIFACT_INTEGRITY=PASS
R7_EQUIVALENCE_DECISION=APPROVED

PUBLIC_IMPORT_COMPATIBILITY=PASS
PUBLIC_SIGNATURE_COMPATIBILITY=PASS

SUCCESS_RESULT_EQUIVALENCE=PASS
FAILURE_RESULT_EQUIVALENCE=PASS
EXCEPTION_TYPE_EQUIVALENCE=PASS
EXCEPTION_MESSAGE_EQUIVALENCE=PASS
ORDERING_EQUIVALENCE=PASS
SIDE_EFFECT_EQUIVALENCE=PASS
PARTIAL_RESULT_EQUIVALENCE=PASS

PROVIDER_BOUNDARY_PRODUCTION_CHANGES=0
R6_DEFERRED_GROUPS_PRESERVED=PASS

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
R0_FROZEN_INVENTORY_MODIFIED=false

DEBT_002_DECISION=RESOLVED_UNCHANGED
DEBT_003_DECISION=RESOLVED_UNCHANGED
TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

TESTS=>=1566_PASS
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

PROJECT_STATE=V4_1_R7_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_COMMIT_HASH=<ACTUAL_COMMIT_HASH>
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_1_R7_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4.1-R8

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

Approve LegacyMapper V4.1-R7 exception boundary cleanup

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

V4.1-R0 through V4.1-R7 = APPROVED

DUP-001 = RESOLVED
DEBT-001 = RESOLVED
DEBT-002 = RESOLVED
DEBT-003 = RESOLVED

TD-005 = PARTIALLY_RESOLVED

R7 provider production changes = 0
R7 safe local cleanups = 1

R6 deferred groups remain preserved

TESTS >= 1566 PASS

BEHAVIOR_CHANGE = FORBIDDEN

V4.1-R8 = NEXT

No conversation memory may be required.

---

# Stop Condition

STOP after:

1. R7 approval registration;
2. closure result creation;
3. full regression;
4. readiness verification;
5. normal commit;
6. actual commit hash recording;
7. push;
8. clean Git status.

Do NOT:

- begin R8;
- perform additional cleanup;
- modify provider boundaries;
- modify resume.py;
- modify deep_source.py;
- touch R6 deferred groups;
- continue TD-005 broadly;
- rename copilot_pilot.py;
- restructure context/;
- begin V5;
- implement Plugin runtime.