# LegacyMapper V4.2 — R7 / R7.1
# Approval and Versioning

TASK=V4_2_R7_R7_1_APPROVAL_AND_VERSIONING

MODE=CONTROLLED_CLOSURE_AND_VERSIONING

PRODUCTION_CODE_CHANGE_ALLOWED=false
TEST_CHANGE_ALLOWED=false
REAL_AI_RUNTIME_CALL_ALLOWED=false
REAL_LEGACY_REPOSITORY_READ_ALLOWED=false

COMMIT_ALLOWED=true
PUSH_ALLOWED=true

V4_1_REOPEN_ALLOWED=false
V5_IMPLEMENTATION_ALLOWED=false
PLUGIN_RUNTIME_IMPLEMENTATION_ALLOWED=false

---

# 1. Authority

The Technical Lead has formally approved:

V4.2-R7
V4.2-R7.1

R7's real pilot diagnosis is accepted.

R7.1 resolves the HIGH finding that blocked R7 closure.

Approved finding state:

F-01=FIXED
F-02=FIXED
F-03=FIXED
F-04=FIXED
F-05=DEFERRED_BY_DETERMINISM_CONTRACT
F-06=PRESERVED_OBSERVATION
F-07=PRESERVED_OBSERVATION

Read:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/V4_2/V4_2_R7_REAL_IST_PILOT_AND_COMMITTABLE_FIXTURE_RESULT.md
docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md
docs/V4_2/V4_2_R7_SYNTHETIC_FIXTURE_VALIDATION.md

docs/V4_2/V4_2_R7_1_REAL_PILOT_FINDINGS_CORRECTION_RESULT.md
docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md

Do not implement R8.

---

# 2. Purpose

Formally record Technical Lead approval of R7 and R7.1 and version the exact
approved cumulative state.

This is closure/versioning only.

Do not modify production code or tests.

Do not rerun IST.

---

# 3. State

Update active continuity/state artifacts according to repository conventions.

Record at minimum:

V4_2_R7=APPROVED
V4_2_R7_1=APPROVED

LATEST_COMPLETED_ROUND=V4.2-R7.1
LATEST_APPROVED_ROUND=V4.2-R7.1

TESTS=1777

READINESS=READY

AUTHORITATIVE_EXIT_CODE_CONTRACT=
SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4

REAL_IST_PILOT=COMPLETED

R7_FINDINGS:
F-01=FIXED
F-02=FIXED
F-03=FIXED
F-04=FIXED
F-05=DEFERRED_BY_DETERMINISM_CONTRACT
F-06=PRESERVED_OBSERVATION
F-07=PRESERVED_OBSERVATION

DOCUMENTATION_SCALE_PROBLEM=OPEN

NEXT=V4.2-R8

Do not mark V4.2 closed yet.
Do not mark R8 started.

Preserve:

V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED

APPROVAL_SURFACE_IMPLEMENTATION=NOT_IMPLEMENTED

---

# 4. Historical Integrity

Preserve R7 as the authoritative historical real-pilot result.

Do not rewrite R7's original metrics to pretend R7.1 had already existed.

In particular:

R7's 18.7% finding remains historical pilot evidence.

R7.1 did NOT rerun IST and therefore must not claim a corrected real-IST
percentage.

Preserve the distinction:

R7 = real pilot / defect discovery
R7.1 = synthetic deterministic correction and regression verification

---

# 5. Deferred Items

Record explicitly for R8/future work:

F-05:
full-run duration deferred because RUN_SUMMARY.json currently has a
byte-for-byte determinism contract.

F-06:
InitializeComponent() unresolved-documentation noise.

F-07:
markup-bound WebEntryResolver outgoing_calls gap.

Documentation scale/usability:

FUNCTIONAL_FLOWS.md ≈44MB
UNRESOLVED_FINDINGS.md ≈12.8MB
DATABASE_ACCESS.md ≈5.2MB

These values are historical R7 pilot observations.

Do not claim they have changed without another real pilot.

---

# 6. Verification

Run:

python -m unittest discover -s tests

Expected:

1777_PASS_0_FAIL_0_SKIP

Run the suite once.

If the historical intermittent R6 symptom or any unexplained regression
occurs:

STOP.

Do not rerun repeatedly until green.

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY
provider_calls=0
real_llm_calls=0

REAL_PROVIDER_CALLS=0
REAL_IST_ACCESSED=false

Do not execute the real IST repository.

Do not run a real AI path.

---

# 7. Approved Compatibility

Verify/document without changing code:

F-01 additive fields remain:

has_confirmed_terminal
has_unresolved_boundary

Flow summary additive counters remain:

flows_with_confirmed_terminal
flows_with_unresolved_boundary
flows_with_both

Existing:

status
confidence

semantics remain unchanged.

Verify:

F-02 duplicate solution rendering remains repository-relative.
F-03 register rendering remains human-readable Markdown.
F-04 human-facing project overview does not expose absolute user path.
F-07 remains intentionally unfixed.

No implementation work is authorized here.

---

# 8. Generated Real Pilot Output

The real IST pilot output:

output/v4_2_r7_ist_operacional/

is local/generated evidence.

Do NOT stage or commit it.

Do not delete it merely for closure unless existing generated-artifact policy
requires cleanup.

Do not copy its contents into repository documentation.

Synthetic fixture is committable:

tests/fixtures/v4_2_r7_full_sample/

and must be included as part of the approved R7 state.

---

# 9. Git Safety

Before staging inspect:

git status
git diff

Verify no:

credentials
tokens
API keys
connection-string values
real IST source
real IST generated output
temporary files
unrelated modifications

are staged.

Commit only:

approved R7 synthetic fixture/tests/docs/prompt
approved R7.1 production/tests/docs/prompt
required closure/state artifacts

No real IST generated output.

Push only after verification.

After push require:

expected branch
remote synchronized
working tree clean

Do not rewrite unrelated history.

---

# 10. Result

Create:

docs/V4_2/V4_2_R7_R7_1_CLOSURE_AND_VERSIONING_RESULT.md

Include:

STATUS
APPROVED_ROUNDS

R7_REAL_PILOT_STATUS
R7_1_CORRECTION_STATUS

F01_STATUS
F02_STATUS
F03_STATUS
F04_STATUS
F05_STATUS
F06_STATUS
F07_STATUS

DOCUMENTATION_SCALE_STATUS

FILES_CHANGED_FOR_CLOSURE

TESTS
INTERMITTENT_R6_TEST_RECURRENCE
READINESS
REAL_PROVIDER_CALLS
REAL_IST_ACCESSED

SECURITY_CHECK

GIT_BRANCH
GIT_COMMIT
GIT_PUSH
GIT_STATUS

PROJECT_STATE
AUTHORITATIVE_EXIT_CODE_CONTRACT

V4_1_REOPENED
V5_IMPLEMENTED
PLUGIN_RUNTIME
APPROVAL_SURFACE_IMPLEMENTATION

DECISION
NEXT

Expected:

STATUS=COMPLETE

APPROVED_ROUNDS=V4.2-R7,V4.2-R7.1

R7_REAL_PILOT_STATUS=COMPLETED
R7_1_CORRECTION_STATUS=APPROVED

F01_STATUS=FIXED
F02_STATUS=FIXED
F03_STATUS=FIXED
F04_STATUS=FIXED
F05_STATUS=DEFERRED_BY_DETERMINISM_CONTRACT
F06_STATUS=PRESERVED_OBSERVATION
F07_STATUS=PRESERVED_OBSERVATION

DOCUMENTATION_SCALE_STATUS=OPEN

TESTS=1777_PASS_0_FAIL_0_SKIP
INTERMITTENT_R6_TEST_RECURRENCE=false

READINESS=READY
REAL_PROVIDER_CALLS=0
REAL_IST_ACCESSED=false

PROJECT_STATE=V4_2_R7_1_APPROVED

AUTHORITATIVE_EXIT_CODE_CONTRACT=
SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4

V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED
APPROVAL_SURFACE_IMPLEMENTATION=NOT_IMPLEMENTED

DECISION=V4_2_R7_R7_1_CLOSED_AND_VERSIONED
NEXT=V4.2-R8

---

# 11. Stop

STOP after successful commit/push verification and result creation.

Do not implement R8.
Do not rerun IST.
Do not call a real provider.
Do not implement approval.
Do not begin V5.