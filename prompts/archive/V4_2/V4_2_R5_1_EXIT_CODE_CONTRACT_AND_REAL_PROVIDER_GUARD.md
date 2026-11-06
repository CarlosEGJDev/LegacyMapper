# LegacyMapper V4.2-R5.1
# Exit-Code Contract and Real-Provider Guard

TASK=V4_2_R5_1_EXIT_CODE_CONTRACT_AND_REAL_PROVIDER_GUARD

MODE=CONTROLLED_CORRECTION

PRODUCTION_CODE_CHANGE_ALLOWED=true
TEST_CHANGE_ALLOWED=true

REAL_AI_RUNTIME_CALL_ALLOWED=false

COMMIT_ALLOWED=false
PUSH_ALLOWED=false

V4_1_REOPEN_ALLOWED=false
V5_IMPLEMENTATION_ALLOWED=false
PLUGIN_RUNTIME_IMPLEMENTATION_ALLOWED=false

---

# 1. Authority

V4.2-R5 was reviewed by the Technical Lead.

R5 implementation is technically accepted, but formal approval is pending
two small corrections/clarifications discovered during review.

Read:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX_RESULT.md

Inspect the actual R2-R5 implementation and tests.

---

# 2. Technical Lead Decision — Exit Codes

The Technical Lead explicitly resolves the R5 discrepancy.

The authoritative V4.2 CLI exit-code contract is:

0 = SUCCESS
1 = PARTIAL
2 = CLI_USAGE_ERROR / argparse usage error
4 = FAILED

This matches the behavior already implemented and tested since R2.

Do NOT migrate runtime behavior to 0/4/5/2.

The 0/4/5/2 values appearing in the R5 prompt were stale/incorrect
instructions.

Repository documentation created or modified for active V4.2 development
must consistently use the authoritative 0/1/2/4 contract.

Historical approved artifacts must not be silently rewritten.

---

# 3. Find Active Contradictions

Search active V4.2 documentation/source/tests for statements describing the
current exit-code contract.

Classify each occurrence as:

CURRENT_ACTIVE_CONTRACT
HISTORICAL_RECORD
STALE_ACTIVE_REFERENCE

Do not rewrite historical round-result evidence merely to hide the
discrepancy.

Correct only active references that are supposed to describe the current
contract.

Document what was found and what was intentionally preserved historically.

---

# 4. Runtime Behavior

Do not change router exit-code behavior if inspection confirms it already
implements:

SUCCESS -> 0
PARTIAL -> 1
FAILED -> 4

argparse -> 2

Add or strengthen focused contract tests if necessary so these values cannot
drift accidentally.

Prefer one explicit authoritative test of all four externally observable
cases.

---

# 5. Real Provider Guard

R5 disclosed that one manual verification accidentally reached the locally
available Copilot provider even though:

REAL_AI_RUNTIME_CALL_ALLOWED=false

The Technical Lead accepts that disclosure and does not require reverting
R5.

However, future controlled rounds with real AI forbidden must fail closed
against accidental provider use.

Inspect the existing test/provider injection architecture and implement the
smallest maintainable safeguard appropriate to DEVELOPMENT/TEST verification.

Do NOT disable legitimate production AI functionality:

python main.py full ... --allow-ai-interpretation

must remain capable of using the configured real provider during normal
authorized use.

Therefore do not globally disable Copilot or external providers.

The guard should protect controlled test/manual verification contexts, not
change product semantics.

If a reliable code-level guard would require invasive environment-specific
behavior, do not over-engineer it. In that case:

- strengthen test helpers/fixtures;
- add a documented safe manual-verification command/path using
  FakeLLMProvider or an explicit test harness;
- make future round instructions unambiguous.

Explain the chosen solution.

---

# 6. Manual Verification Rule

Establish explicitly:

When a round declares:

REAL_AI_RUNTIME_CALL_ALLOWED=false

manual verification MUST NOT invoke:

python main.py full ... --allow-ai-interpretation

through the normal provider-resolution path.

AI-path verification must instead use:

FakeLLMProvider
stub provider
mocked provider
or a dedicated test harness that injects one.

Automated tests must continue to fail if they unexpectedly reach a real
provider.

---

# 7. Scope

Do NOT implement:

R6
approval UX
canonical promotion
R11/R12 orchestration
Plugin runtime
V5
real provider pilot
IST pilot

Do not refactor full_pipeline.py merely for metrics.

---

# 8. Development Practices

Maintain established LegacyMapper practices:

idiomatic Python first;
PascalCase classes;
snake_case modules;
clear responsibilities;
type hints at public/service boundaries;
concise docstrings;
comments for non-obvious security/determinism rules;
no unnecessary Python magic;
no unnecessary C# ceremony;
simple and maintainable implementation.

---

# 9. Regression

Entering baseline:

1714_PASS_0_FAIL_0_SKIP

Run:

python -m unittest discover -s tests

Require all existing tests plus any R5.1 tests.

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY

REAL_PROVIDER_CALLS must remain:

0

Do not run real IST/Operacional.

Do not perform any real Copilot/Gemini/provider call, including manual
verification.

---

# 10. Result

Create:

docs/V4_2/V4_2_R5_1_EXIT_CODE_CONTRACT_AND_REAL_PROVIDER_GUARD_RESULT.md

Include:

STATUS
BASELINE
FILES_CREATED
FILES_MODIFIED
AUTHORITATIVE_EXIT_CODE_CONTRACT
ACTIVE_REFERENCES_FOUND
HISTORICAL_REFERENCES_PRESERVED
RUNTIME_EXIT_CODE_BEHAVIOR
EXIT_CODE_TESTS
REAL_PROVIDER_GUARD
SAFE_MANUAL_VERIFICATION
REAL_PROVIDER_CALLS
TESTS
READINESS
PRODUCTION_BEHAVIOR_CHANGED
LEGACY_ANALYZE_BEHAVIOR_CHANGED
V4_1_REOPENED
V5_IMPLEMENTED
PLUGIN_RUNTIME
RISKS
DECISION
NEXT

Expected:

AUTHORITATIVE_EXIT_CODE_CONTRACT=SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4
REAL_PROVIDER_CALLS=0
LEGACY_ANALYZE_BEHAVIOR_CHANGED=false
V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED

If successful:

DECISION=V4_2_R5_1_READY_FOR_TECHNICAL_LEAD_REVIEW
NEXT=HUMAN_REVIEW_V4_2_R5_1

---

# 11. Stop

STOP after R5.1.

Do not implement R6.
Do not commit.
Do not push.
Do not call a real provider.