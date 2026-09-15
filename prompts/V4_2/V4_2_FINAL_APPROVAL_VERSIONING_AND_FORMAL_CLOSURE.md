# LegacyMapper V4.2
# Final Approval, Versioning and Formal Closure

TASK=V4_2_FINAL_APPROVAL_VERSIONING_AND_FORMAL_CLOSURE

MODE=CONTROLLED_FINAL_CLOSURE

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

The Technical Lead has completed final human review of V4.2-R8.

V4.2-R8 is APPROVED.

All V4.2 implementation rounds are now approved:

R0
R1
R2
R3
R4
R5
R5.1
R6
R7
R7.1
R8

The Technical Lead authorizes formal closure and versioning of V4.2.

Read:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/V4_2/V4_2_R8_DOCUMENTATION_AT_SCALE_FINAL_BASELINE_AND_CLOSURE_PREPARATION_RESULT.md
docs/V4_2/V4_2_R8_FINAL_DOCUMENTATION_REVIEW.md

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md
docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md

docs/V4_2/V4_2_R7_R7_1_CLOSURE_AND_VERSIONING_RESULT.md

output/v4_2_r8/V4_2_FINAL_BASELINE.json
output/v4_2_r8/V4_2_FINAL_MANIFEST.json

Do not implement anything new.

---

# 2. Purpose

Perform final verification, record Technical Lead approval, version the exact
approved V4.2 state, and formally close V4.2.

This is closure only.

No production implementation.
No test implementation.
No debt cleanup.
No V5 implementation.

---

# 3. Final Approved Baseline

Expected entering approved candidate:

TESTS=1809_PASS_0_FAIL_0_SKIP

READINESS=READY

FINAL_BASELINE=
output/v4_2_r8/V4_2_FINAL_BASELINE.json

FINAL_BASELINE_SHA256=
4e80b2ac757227204178d46c3eddb0fdebd166ee40c6453bbbae2c45e184d5ed

FINAL_MANIFEST=
output/v4_2_r8/V4_2_FINAL_MANIFEST.json

FINAL_MANIFEST_SHA256=
1ed09ad06daaa698ed3bf0b7d119fffdea41a610b6cc230d79bfedebb8cef7e0

Do not silently regenerate different approved hashes.

If verification produces different bytes/hashes:

STOP and report BLOCKED.

Do not overwrite the approved candidate and continue.

---

# 4. Final Verification

Run exactly once:

python -m unittest discover -s tests

Require:

1809_PASS_0_FAIL_0_SKIP

If any unexplained regression occurs, including recurrence of the historical
R6 intermittent symptom:

STOP.

Do not repeatedly rerun until green.

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY
provider_calls=0
real_llm_calls=0

Verify:

python main.py --help
python main.py full --help
python main.py readiness

Require authoritative exit-code contract remains:

SUCCESS=0
PARTIAL=1
CLI_USAGE_ERROR=2
FAILED=4

Do not run real AI.

Do not run real IST.

Expected:

REAL_PROVIDER_CALLS=0
REAL_IST_ACCESSED=false

---

# 5. Final Baseline / Manifest Integrity

Verify without changing approved content:

SHA256(
output/v4_2_r8/V4_2_FINAL_BASELINE.json
)
=
4e80b2ac757227204178d46c3eddb0fdebd166ee40c6453bbbae2c45e184d5ed

SHA256(
output/v4_2_r8/V4_2_FINAL_MANIFEST.json
)
=
1ed09ad06daaa698ed3bf0b7d119fffdea41a610b6cc230d79bfedebb8cef7e0

Verify every manifest entry against current repository bytes.

Verify:

no real IST generated output
no secrets
no absolute analyst paths
no wall-clock timestamp
no UUID/nondeterministic identifier

If any manifest entry differs:

STOP.

Do not repair production code in this closure.

---

# 6. Formal V4.2 State

Update active continuity/state artifacts according to repository conventions.

Record at minimum:

STATUS=V4_2_FORMALLY_CLOSED

V4_2_CLOSED=true

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

LATEST_COMPLETED_ROUND=V4.2-R8
LATEST_APPROVED_ROUND=V4.2-R8

TESTS=1809

READINESS=READY

FINAL_BASELINE=
output/v4_2_r8/V4_2_FINAL_BASELINE.json

FINAL_BASELINE_SHA256=
4e80b2ac757227204178d46c3eddb0fdebd166ee40c6453bbbae2c45e184d5ed

FINAL_MANIFEST=
output/v4_2_r8/V4_2_FINAL_MANIFEST.json

FINAL_MANIFEST_SHA256=
1ed09ad06daaa698ed3bf0b7d119fffdea41a610b6cc230d79bfedebb8cef7e0

AUTHORITATIVE_EXIT_CODE_CONTRACT=
SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4

REAL_IST_PILOT=COMPLETED

DOCUMENTATION_AT_SCALE=IMPLEMENTED

APPROVAL_SURFACE_DESIGN=APPROVED_DESIGN_ONLY
APPROVAL_SURFACE_IMPLEMENTATION=NOT_IMPLEMENTED

PLUGIN_RUNTIME=NOT_IMPLEMENTED

V5_IMPLEMENTED=false

NEXT=V5_DESIGN_PENDING

Do not mark approval/canonical promotion as implemented.

---

# 7. Final Capability Statement

Record accurately that V4.2 provides:

unified CLI routing;
legacy-compatible analyze command;
full deterministic pipeline;
stage-level execution/result model;
partial/failure containment;
safe rerun/recovery behavior;
human technical documentation;
documentation navigation/partitioning at scale;
optional explicit AI interpretation;
proposal generation pending human review;
real IST/Operacional pilot completed;
synthetic committable full-pipeline regression fixture;
deterministic final baseline/manifest.

Record accurately that V4.2 does NOT provide:

implemented Technical Lead approval command;
run_id-bound approval;
automatic canonical promotion;
R11/R12 full-workflow orchestration after approval;
Plugin runtime;
V5 agnosticism.

Do not blur these boundaries.

---

# 8. Known Deferred Items

Preserve explicitly:

F-05 =
DEFERRED_BY_DETERMINISM_CONTRACT

Reason:
RUN_SUMMARY.json has byte-for-byte deterministic rerun contract; real
wall-clock duration is not stored there.

F-06 =
PRESERVED_OBSERVATION

InitializeComponent() evidence remains unresolved, but R8 groups it
presentationally.

F-07 =
PRESERVED_OBSERVATION

Markup-bound WebEntryResolver outgoing_calls gap remains.

Also preserve:

WEB_ENTRY_POINTS.md partitioning = OPEN_IF_FUTURE_SCALE_REQUIRES

PROJECT_DEPENDENCIES.md partitioning =
OPEN_IF_FUTURE_SCALE_REQUIRES

technical_documentation_renderer.py maintainability =
HIGH_RISK_FUTURE_EXTRACTION_CANDIDATE

These items do not block V4.2 closure.

---

# 9. V5 Boundary

Set:

NEXT=V5_DESIGN_PENDING

Do not create V5 production code.

Do not modify V4.2 to anticipate an unapproved V5 architecture.

V5 design must explicitly address:

language agnosticism;
framework agnosticism;
database agnosticism;
project-layout agnosticism;
AI/provider/model agnosticism.

Preserve:

Python discovers; AI interprets.

The core must eventually depend on abstract AI capabilities/contracts rather
than a specific Claude/OpenAI/Copilot/Ollama provider.

This is a V5 requirement, NOT V4.2 implementation.

---

# 10. Historical Integrity

Preserve:

V4 formal closure
V4.1 formal closure
R7 real pilot historical metrics
R7.1 correction distinction

Do not rewrite historical result documents.

Do not claim R8 reran IST.

Do not modify frozen V4/V4.1 baselines.

---

# 11. Generated Real IST Evidence

The local:

output/v4_2_r7_ist_operacional/

must NOT be staged or committed.

It remains local generated pilot evidence governed by generated-artifact
policy.

Do not copy its contents into closure artifacts.

---

# 12. Git Safety

Before staging inspect:

git status
git diff
git diff --cached

Verify no:

credential
token
API key
connection-string value
private key
real IST source
real IST generated output
temporary/local-only artifact
unrelated change

is staged.

Commit only:

approved R8 implementation/tests/docs/manuals
approved final baseline/manifest/tool
R8 prompt/result/review
final closure prompt/result
required state/continuity updates

Preserve all already-versioned history.

Do not amend/squash/rewrite historical commits.

Push only after all verification passes.

After push verify:

branch is expected branch
HEAD == origin/main
working tree has no tracked modifications

The intentionally untracked real-IST output may remain and must be reported
separately rather than called a dirty tracked tree.

---

# 13. Final Closure Result

Create:

docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md

Include:

STATUS
CLOSED_VERSION
APPROVED_ROUNDS
HUMAN_REVIEW
APPROVAL_AUTHORITY

CAPABILITIES
NOT_IMPLEMENTED_BOUNDARIES

FILES_CHANGED_FOR_CLOSURE

TESTS
INTERMITTENT_R6_TEST_RECURRENCE
READINESS
REAL_PROVIDER_CALLS
REAL_IST_ACCESSED

FINAL_BASELINE
FINAL_BASELINE_SHA256
FINAL_MANIFEST
FINAL_MANIFEST_SHA256
MANIFEST_INTEGRITY

R7_REAL_PILOT_STATUS

F01_STATUS
F02_STATUS
F03_STATUS
F04_STATUS
F05_STATUS
F06_STATUS
F07_STATUS

DOCUMENTATION_AT_SCALE
DOCUMENTATION_REMAINING_SCALE_DEBT
MAINTAINABILITY_DEBT

SECURITY_CHECK

GIT_BRANCH
GIT_COMMIT
GIT_PUSH
GIT_STATUS

PROJECT_STATE
V4_2_CLOSED

AUTHORITATIVE_EXIT_CODE_CONTRACT

V4_CLOSED
V4_1_CLOSED
V5_IMPLEMENTED
PLUGIN_RUNTIME
APPROVAL_SURFACE_IMPLEMENTATION

DECISION
NEXT

Expected:

STATUS=COMPLETE

CLOSED_VERSION=V4.2

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

TESTS=1809_PASS_0_FAIL_0_SKIP
INTERMITTENT_R6_TEST_RECURRENCE=false

READINESS=READY
REAL_PROVIDER_CALLS=0
REAL_IST_ACCESSED=false

FINAL_BASELINE_SHA256=
4e80b2ac757227204178d46c3eddb0fdebd166ee40c6453bbbae2c45e184d5ed

FINAL_MANIFEST_SHA256=
1ed09ad06daaa698ed3bf0b7d119fffdea41a610b6cc230d79bfedebb8cef7e0

MANIFEST_INTEGRITY=PASS

R7_REAL_PILOT_STATUS=COMPLETED

F01_STATUS=FIXED
F02_STATUS=FIXED
F03_STATUS=FIXED
F04_STATUS=FIXED
F05_STATUS=DEFERRED_BY_DETERMINISM_CONTRACT
F06_STATUS=PRESERVED_OBSERVATION
F07_STATUS=PRESERVED_OBSERVATION

DOCUMENTATION_AT_SCALE=IMPLEMENTED

PROJECT_STATE=V4_2_FORMALLY_CLOSED
V4_2_CLOSED=true

AUTHORITATIVE_EXIT_CODE_CONTRACT=
SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4

V4_CLOSED=true
V4_1_CLOSED=true

V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED
APPROVAL_SURFACE_IMPLEMENTATION=NOT_IMPLEMENTED

DECISION=LEGACYMAPPER_V4_2_FORMALLY_CLOSED

NEXT=V5_DESIGN_PENDING

---

# 14. Stop

STOP after:

final verification
state update
closure result
commit
push
remote synchronization verification

Do not implement V5.
Do not run IST.
Do not call a real provider.
Do not implement approval.