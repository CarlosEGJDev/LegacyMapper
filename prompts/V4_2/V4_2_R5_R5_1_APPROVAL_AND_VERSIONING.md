# LegacyMapper V4.2 — R5 / R5.1 Approval and Versioning

TASK=V4_2_R5_R5_1_APPROVAL_AND_VERSIONING

MODE=CONTROLLED_CLOSURE_AND_VERSIONING

PRODUCTION_CODE_CHANGE_ALLOWED=false
TEST_CHANGE_ALLOWED=false

REAL_AI_RUNTIME_CALL_ALLOWED=false

COMMIT_ALLOWED=true
PUSH_ALLOWED=true

V4_1_REOPEN_ALLOWED=false
V5_IMPLEMENTATION_ALLOWED=false
PLUGIN_RUNTIME_IMPLEMENTATION_ALLOWED=false

---

# 1. Authority

The Technical Lead has formally approved:

V4.2-R5
V4.2-R5.1

R5.1 resolves the two review conditions raised against R5.

Authoritative exit-code contract:

0 = SUCCESS
1 = PARTIAL
2 = CLI_USAGE_ERROR
4 = FAILED

Read:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX_RESULT.md
docs/V4_2/V4_2_R5_1_EXIT_CODE_CONTRACT_AND_REAL_PROVIDER_GUARD_RESULT.md

Do not implement R6.

---

# 2. Purpose

Formally record Technical Lead approval of R5 and R5.1 and version the
approved repository state.

This is a closure/versioning task only.

Do not modify production code or tests.

Do not reinterpret or expand R5/R5.1.

---

# 3. State

Update the active project continuity/state artifacts only where required by
the repository's established V4.2 conventions.

Record at minimum:

V4_2_R5=APPROVED
V4_2_R5_1=APPROVED

LATEST_COMPLETED_ROUND=V4.2-R5.1
LATEST_APPROVED_ROUND=V4.2-R5.1

AUTHORITATIVE_EXIT_CODE_CONTRACT=SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4

NEXT=V4.2-R6

Do not mark V4.2 itself closed.

Do not mark R6 started.

Preserve:

V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED

---

# 4. Historical Integrity

Do not rewrite historical prompts/results to make them appear as if the R5
exit-code discrepancy never happened.

In particular preserve:

prompts/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX.md

and its historical 0/4/5/2 instruction.

R5.1 is the authoritative resolution of that discrepancy.

---

# 5. Verification

Before versioning run:

python -m unittest discover -s tests

Expected baseline:

1723_PASS_0_FAIL_0_SKIP

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY
provider_calls=0
real_llm_calls=0

REAL_PROVIDER_CALLS=0

Do not manually execute the normal real-provider AI path.

If AI-path verification unexpectedly becomes necessary, use only:

python -m tools.manual_verify_full_pipeline ...

with FakeLLMProvider.

---

# 6. Git Safety

Before commit:

- inspect git status;
- verify no secrets/credentials/tokens are staged;
- verify no temporary output or local-only artifacts are accidentally staged;
- verify no unrelated files are included;
- verify source legacy repository remains untouched.

Commit only the approved R5/R5.1 changes and required closure/state artifacts.

Push to the configured remote only after successful verification.

After push verify:

working tree clean
local commit exists on expected branch
remote synchronized

Do not amend/rewrite unrelated historical commits.

---

# 7. Commit

Use a clear closure/versioning commit message consistent with repository
history.

Conceptually:

V4.2 R5/R5.1 approved: unified CLI UX and provider guard

Adapt wording only if repository conventions require it.

---

# 8. Result

Create:

docs/V4_2/V4_2_R5_R5_1_CLOSURE_AND_VERSIONING_RESULT.md

Include:

STATUS
APPROVED_ROUNDS
AUTHORITATIVE_EXIT_CODE_CONTRACT
FILES_CHANGED_FOR_CLOSURE
TESTS
READINESS
REAL_PROVIDER_CALLS
SECURITY_CHECK
GIT_BRANCH
GIT_COMMIT
GIT_PUSH
GIT_STATUS
PROJECT_STATE
V4_1_REOPENED
V5_IMPLEMENTED
PLUGIN_RUNTIME
DECISION
NEXT

Expected:

APPROVED_ROUNDS=V4.2-R5,V4.2-R5.1

AUTHORITATIVE_EXIT_CODE_CONTRACT=SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4

TESTS=1723_PASS_0_FAIL_0_SKIP
READINESS=READY
REAL_PROVIDER_CALLS=0

V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED

PROJECT_STATE=V4_2_R5_1_APPROVED

DECISION=V4_2_R5_R5_1_CLOSED_AND_VERSIONED
NEXT=V4.2-R6

---

# 9. Stop

STOP after successful commit/push verification and result creation.

Do not implement R6.
Do not begin V5.
Do not call a real provider.