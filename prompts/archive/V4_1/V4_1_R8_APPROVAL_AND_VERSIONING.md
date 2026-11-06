# LegacyMapper V4.1 — R8 Approval and Versioning

TASK=V4_1_R8_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
REFACTOR_ALLOWED=false
R9_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

V4.1-R8 — Naming and Documentation C#-friendly Part 2

The Technical Lead explicitly accepts:

- R8_MODE=POST_CHARACTERIZATION_READABILITY_PASS;
- 13 recovered candidates;
- SAFE_PRIVATE_RENAMES=0;
- SAFE_LOCAL_RENAMES=0;
- DOCUMENTATION_ONLY_CHANGES=3;
- SAFE_TYPE_HINT_CHANGES=1;
- `copilot_pilot.py` rename deferred;
- `context/` limited to documentation-only improvements;
- no module moves;
- no package restructuring;
- no import-topology change;
- one safe type annotation on `matched_type`;
- no forced typing of ambiguous historical JSON structures;
- TD-005 remains PARTIALLY_RESOLVED;
- R6 deferred groups preserved;
- R7 exception boundaries preserved;
- approved historical artifacts unchanged;
- R0 frozen inventory untouched;
- PRODUCTION_BEHAVIOR_CHANGED=false;
- no R8.1 corrective round is required.

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
12. docs/V4_1/V4_1_R7_CLOSURE_AND_VERSIONING_RESULT.md
13. docs/V4_1/V4_1_R8_NAMING_AND_DOCUMENTATION_PART_2_RESULT.md
14. output/v4_1_r8/V4_1_R8_NAMING_DOCUMENTATION_EQUIVALENCE.json
15. output/v4_1_r0/V4_1_REFACTOR_PLAN.json

Repository artifacts are authoritative.

---

# Expected Reviewed State

Require:

latest_completed_round = V4.1-R8
latest_approved_round = V4.1-R7

current_round_in_progress =
"V4.1-R8 (pending Technical Lead review)"

round_status =
V4_1_R8_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R8

tests = 1566
readiness = READY

provider_calls = 0
real_llm_calls = 0

If materially different:

STOP.

---

# Reviewed R8 Artifact

Expected:

output/v4_1_r8/V4_1_R8_NAMING_DOCUMENTATION_EQUIVALENCE.json

SHA256=
1d1ffccbaf037b39442cc19dcd16ff4e00fd16cfb23d88e34ffccb98b9a51023

Recompute.

Require:

R8_EQUIVALENCE_ARTIFACT_INTEGRITY=PASS

If different:

STOP.

Do not regenerate or repair it.

---

# R8 Decision

Record:

R8_MODE_DECISION=POST_CHARACTERIZATION_READABILITY_PASS_APPROVED

CANDIDATES_TOTAL=13

SAFE_PRIVATE_RENAMES=0
SAFE_LOCAL_RENAMES=0

DOCUMENTATION_ONLY_CHANGES=3
SAFE_TYPE_HINT_CHANGES=1

DEFERRED_CANDIDATES=1
DO_NOT_CHANGE_CANDIDATES=9

No additional naming, documentation, typing or structural change is authorized
during closure.

---

# Approved Documentation Changes

Approve exactly:

legacy_documenter/context/__init__.py
legacy_documenter/context/composer.py
legacy_documenter/context/context_builder.py

These changes are documentation-only.

Require:

CONTEXT_PACKAGE_DECISION=DOCUMENTATION_ONLY

Do not move or rename context modules.

Do not restructure the package.

Do not change import topology.

---

# Approved Type-Hint Change

Approve exactly:

legacy_documenter/extractors/_database_classification.py::matched_type

Approved annotation:

match: re.Match[str]

Do not add further annotations during closure.

Do not claim TD-005 fully resolved.

Require:

TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

---

# copilot_pilot Decision

Record:

COPILOT_PILOT_DECISION=DEFER

Do not rename:

legacy_documenter/llm/copilot_pilot.py

The rename remains deferred because it would require several production import
changes and compatibility support disproportionate to the readability benefit.

No compatibility wrapper is to be introduced during closure.

---

# Compatibility

Require:

PUBLIC_IMPORT_COMPATIBILITY=PASS
PUBLIC_SIGNATURE_COMPATIBILITY=PASS

POSITIONAL_CALL_COMPATIBILITY=NOT_APPLICABLE
KEYWORD_CALL_COMPATIBILITY=NOT_APPLICABLE

RETURN_VALUE_EQUIVALENCE=NOT_APPLICABLE
EXCEPTION_EQUIVALENCE=NOT_APPLICABLE

SERIALIZED_OUTPUT_EQUIVALENCE=PASS

No runtime behavior was modified.

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

Do not remove R6 compatibility delegates.

---

# R7 Preservation

Require:

R7_EXCEPTION_BOUNDARIES_PRESERVED=PASS

Do not modify:

legacy_documenter/main.py::_extract_into

Do not reopen provider exception boundaries.

Do not change exception handling.

---

# High-Risk Preservation

Do not structurally modify:

legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py

No high-risk refactor is authorized.

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
output/v4_1_r7/V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json

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

The already-authorized live reconstruction adjustments for the context docstring
changes are accepted.

Do not weaken assertions further.

---

# Debt Decisions

Preserve:

DEBT_002_DECISION=RESOLVED_UNCHANGED
DEBT_003_DECISION=RESOLVED_UNCHANGED
TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

R8 does not fully resolve TD-005.

---

# Regression

Run:

python -m unittest discover -s tests

Require:

>=1566 PASS
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

Closure itself must make no additional production changes.

---

# PROJECT_STATE

Register Technical Lead approval:

latest_completed_round = V4.1-R8
latest_approved_round = V4.1-R8

current_round_in_progress = null

round_status = V4_1_R8_APPROVED

next = V4.1-R9

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0

V4 remains formally closed.

---

# R8 Result Closure Section

Append only a closure section to:

docs/V4_1/V4_1_R8_NAMING_AND_DOCUMENTATION_PART_2_RESULT.md

Record:

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R8_MODE_DECISION=POST_CHARACTERIZATION_READABILITY_PASS_APPROVED

CANDIDATES_TOTAL=13

SAFE_PRIVATE_RENAMES=0
SAFE_LOCAL_RENAMES=0
DOCUMENTATION_ONLY_CHANGES=3
SAFE_TYPE_HINT_CHANGES=1

COPILOT_PILOT_DECISION=DEFER
CONTEXT_PACKAGE_DECISION=DOCUMENTATION_ONLY

R6_DEFERRED_GROUPS_PRESERVED=PASS
R7_EXCEPTION_BOUNDARIES_PRESERVED=PASS

TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

R8_EQUIVALENCE_DECISION=APPROVED

R8_1_REQUIRED=false

ROUND_STATUS=APPROVED
DECISION=V4_1_R8_FORMALLY_APPROVED
NEXT=V4.1-R9

Do not rewrite the reviewed body.

---

# Closure Result

Create:

docs/V4_1/V4_1_R8_CLOSURE_AND_VERSIONING_RESULT.md

Report at minimum:

STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

R8_MODE_DECISION

CANDIDATES_TOTAL

SAFE_PRIVATE_RENAMES
SAFE_LOCAL_RENAMES
DOCUMENTATION_ONLY_CHANGES
SAFE_TYPE_HINT_CHANGES

DEFERRED_CANDIDATES
DO_NOT_CHANGE_CANDIDATES

COPILOT_PILOT_DECISION
CONTEXT_PACKAGE_DECISION

R8_EQUIVALENCE_ARTIFACT_SHA256
R8_EQUIVALENCE_ARTIFACT_INTEGRITY
R8_EQUIVALENCE_DECISION

PUBLIC_IMPORT_COMPATIBILITY
PUBLIC_SIGNATURE_COMPATIBILITY
POSITIONAL_CALL_COMPATIBILITY
KEYWORD_CALL_COMPATIBILITY
RETURN_VALUE_EQUIVALENCE
EXCEPTION_EQUIVALENCE
SERIALIZED_OUTPUT_EQUIVALENCE

R6_DEFERRED_GROUPS_PRESERVED
R7_EXCEPTION_BOUNDARIES_PRESERVED

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

STATUS=V4_1_R8_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R8_MODE_DECISION=POST_CHARACTERIZATION_READABILITY_PASS_APPROVED

CANDIDATES_TOTAL=13

SAFE_PRIVATE_RENAMES=0
SAFE_LOCAL_RENAMES=0
DOCUMENTATION_ONLY_CHANGES=3
SAFE_TYPE_HINT_CHANGES=1

DEFERRED_CANDIDATES=1
DO_NOT_CHANGE_CANDIDATES=9

COPILOT_PILOT_DECISION=DEFER
CONTEXT_PACKAGE_DECISION=DOCUMENTATION_ONLY

R8_EQUIVALENCE_ARTIFACT_INTEGRITY=PASS
R8_EQUIVALENCE_DECISION=APPROVED

PUBLIC_IMPORT_COMPATIBILITY=PASS
PUBLIC_SIGNATURE_COMPATIBILITY=PASS
POSITIONAL_CALL_COMPATIBILITY=NOT_APPLICABLE
KEYWORD_CALL_COMPATIBILITY=NOT_APPLICABLE
RETURN_VALUE_EQUIVALENCE=NOT_APPLICABLE
EXCEPTION_EQUIVALENCE=NOT_APPLICABLE
SERIALIZED_OUTPUT_EQUIVALENCE=PASS

R6_DEFERRED_GROUPS_PRESERVED=PASS
R7_EXCEPTION_BOUNDARIES_PRESERVED=PASS

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

PROJECT_STATE=V4_1_R8_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_COMMIT_HASH=<ACTUAL_COMMIT_HASH>
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_1_R8_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4.1-R9

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

Approve LegacyMapper V4.1-R8 naming and documentation readability

Use one normal commit.

No amend.
No squash.

After commit:

git rev-parse HEAD

Record the actual hash in the closure document.

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

V4.1-R0 through V4.1-R8 = APPROVED

DUP-001 = RESOLVED
DEBT-001 = RESOLVED
DEBT-002 = RESOLVED
DEBT-003 = RESOLVED

TD-005 = PARTIALLY_RESOLVED

R6 deferred groups remain preserved
R7 exception boundaries remain preserved

copilot_pilot rename = DEFERRED
context package = DOCUMENTATION_ONLY

TESTS >= 1566 PASS

BEHAVIOR_CHANGE = FORBIDDEN

V4.1-R9 = NEXT

No conversation memory may be required.

---

# Stop Condition

STOP after:

1. R8 approval registration;
2. closure result creation;
3. full regression;
4. readiness verification;
5. normal commit;
6. actual commit hash recording;
7. push;
8. clean Git status.

Do NOT:

- begin R9;
- perform additional renames;
- add extra type hints;
- restructure context/;
- rename copilot_pilot.py;
- reopen R6 deferred groups;
- alter R7 exception behavior;
- modify high-risk modules;
- begin V5;
- implement Plugin runtime.