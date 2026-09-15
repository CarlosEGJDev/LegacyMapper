# LegacyMapper V4.2-R5
# Unified CLI and Operational UX

TASK=V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX

MODE=CONTROLLED_IMPLEMENTATION

PRODUCTION_CODE_CHANGE_ALLOWED=true
TEST_CHANGE_ALLOWED=true

V4_1_REOPEN_ALLOWED=false
V5_IMPLEMENTATION_ALLOWED=false
PLUGIN_RUNTIME_IMPLEMENTATION_ALLOWED=false

REAL_AI_RUNTIME_CALL_ALLOWED=false

COMMIT_ALLOWED=false
PUSH_ALLOWED=false

---

# 1. Authority

V4.2-R0 through R4 have been reviewed and approved by the Technical Lead.

Read:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/PROJECT_RECOVERY.md
docs/GENERATED_ARTIFACT_POLICY.md

docs/V4_2/V4_2_R0_FULL_PIPELINE_ARCHITECTURE_AND_INVENTORY_RESULT.md
docs/V4_2/V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL_RESULT.md
docs/V4_2/V4_2_R2_DETERMINISTIC_FULL_PIPELINE_ORCHESTRATOR_RESULT.md
docs/V4_2/V4_2_R3_DETERMINISTIC_TECHNICAL_DOCUMENTATION_RESULT.md
docs/V4_2/V4_2_R4_AI_INTERPRETATION_AND_PROPOSAL_INTEGRATION_RESULT.md

docs/V4_1/LEGACYMAPPER_USER_MANUAL_V4_1.md
docs/V4_1/LEGACYMAPPER_TECHNICAL_MANUAL_V4_1.md

Inspect current production source before implementation.

---

# 2. Objective

Make the V4.2 CLI understandable and practical for a developer who should
not need to know LegacyMapper's internal V1-V4 pipeline.

Primary user workflow:

python main.py full <repository> --output <directory>

Optional AI interpretation:

python main.py full <repository> --output <directory> \
    --allow-ai-interpretation

After execution, the user should immediately understand:

- whether the run succeeded;
- whether it was partial or failed;
- where the documentation is;
- where deterministic evidence is;
- whether AI was used;
- whether proposals require review;
- what LegacyMapper did NOT do;
- what the next action is.

R5 is primarily operational UX and CLI composition.

Do not expand the domain scope.

---

# 3. Preserve Existing Commands

These remain valid:

python main.py <repository> ...
python main.py analyze <repository> ...
python main.py full <repository> ...
python main.py readiness

Do not break existing flags.

Do not change legacy/analyze output behavior.

Do not silently enable AI.

---

# 4. CLI Help

Improve CLI help so a developer can understand the difference between:

legacy positional invocation
analyze
full
readiness

Clearly communicate:

analyze = deterministic legacy-compatible analysis

full = deterministic analysis + technical documentation + execution summary

full --allow-ai-interpretation =
full + optional AI interpretation + proposals pending Technical Lead review

readiness =
validates LegacyMapper's knowledge/readiness prerequisites

Do not describe canonical knowledge as automatically produced by `full`.

Do not describe proposals as approved.

---

# 5. Human Console Summary

After `full`, print a concise human-readable execution summary.

It should include at minimum:

LegacyMapper run status
repository
output directory

deterministic analysis status
documentation status

AI requested
AI actually invoked

proposal status/count where applicable

canonical knowledge produced
Technical Lead approval

important output locations

recommended next action

Do not dump every StageResult unless verbose mode explicitly warrants it.

The default output should be useful but concise.

---

# 6. Recommended Next Action

Derive the next action deterministically from run state.

Examples conceptually:

SUCCESS, no AI:
"Technical documentation generated successfully."

SUCCESS/PARTIAL with proposals:
"AI proposals are pending Technical Lead review."

PARTIAL because AI failed:
"Deterministic documentation is available; AI interpretation failed."

FAILED:
"Analysis did not produce the minimum useful output. Inspect RUN_SUMMARY.json."

Do not imply that the user has approved anything.

Do not auto-run another command.

---

# 7. Output Discovery

A user should not have to inspect the repository source to know where results
went.

The console summary should identify relevant existing locations such as:

documentation/
index/
ai_context/
proposals/ when present
RUN_SUMMARY.json
RUN_SUMMARY.md

Only show locations that actually exist or are relevant to the run.

Use paths relative to the selected output directory where practical.

Avoid noisy absolute-path repetition.

---

# 8. Run Summary Human Readability

Review the existing:

RUN_SUMMARY.md

from R2-R4.

Improve it if needed so it is useful as the durable human-readable record of
the run.

It should communicate:

overall status
stage results
structured failures
AI status
proposal status
approval/canonical status
important generated artifacts
next action

Do not duplicate all technical documentation into RUN_SUMMARY.md.

RUN_SUMMARY.json remains the authoritative machine execution record.

---

# 9. Machine Contract Stability

Do not casually change the R2-R4 JSON contract.

If RUN_SUMMARY.json requires additive fields for:

proposal count
proposal review status
next action
important output locations

prefer additive, backward-compatible fields.

Do not rename/remove existing fields without explicit justification.

Document every contract delta.

---

# 10. AI UX

`--allow-ai-interpretation` must remain explicit opt-in.

Before or during an AI-enabled run, make it clear that:

AI interpretation may call the configured provider.

Do not print credentials/provider secrets.

If no provider is available/configured:

the deterministic pipeline remains useful;
AI stage becomes a structured partial failure;
the user receives a clear explanation.

Do not silently fall back to another provider.

---

# 11. Approval UX Boundary

R5 does NOT implement approval.

However, when proposals exist, the UX must clearly say:

PENDING_TECHNICAL_LEAD_REVIEW

and identify:

proposals/AI_PROPOSALS_PENDING_REVIEW.md

as the human review artifact.

Do not provide an `approve` command in R5.

Do not manufacture approval.

---

# 12. Full Pipeline Maintainability Guard

`legacy_documenter/cli/full_pipeline.py` entered R5 at approximately
488 lines and VERY_HIGH risk.

Do NOT keep adding operational presentation logic directly to it.

Before adding substantial new behavior, extract presentation/result-writing
responsibilities into focused modules.

Potential responsibilities suitable for extraction include:

run-summary composition
console-summary composition
proposal-output serialization

This list is illustrative.

Do not perform a broad refactor of full_pipeline.py merely to reduce a metric.

Extract only responsibilities directly touched by R5 or clearly separable
with existing characterization coverage.

Goal:

full_pipeline.py should become easier to understand or at minimum must not
grow materially.

Behavior change outside R5 UX is forbidden.

---

# 13. Renderer Maintainability Guard

Do not add R5 UX logic to:

technical_documentation_renderer.py
pipeline_stages.py

R5 concerns CLI/result presentation, not technical-document rendering.

---

# 14. Structured Presentation

Prefer a small presentation/service layer rather than scattered `print()`
calls.

Possible conceptual component:

RunSummaryPresenter

or equivalent.

Exact design should follow existing source.

Responsibilities may include:

human console output
next-action derivation
artifact-location derivation

Do not create a UI framework.

Do not add third-party CLI dependencies merely for colors/tables.

Standard library is sufficient.

---

# 15. Verbose Mode

Preserve current `--verbose`.

If useful, `full --verbose` may show stage-level detail.

Default mode should remain concise.

Do not change legacy/analyze verbose semantics unnecessarily.

---

# 16. Exit Codes

Preserve the R2 contract:

0 = SUCCESS
4 = PARTIAL
5 = FAILED
2 = argparse/usage error

Do not change exit codes for UX reasons.

AI optional failure remains PARTIAL.

---

# 17. Security

Console output and summaries must never expose:

credentials
tokens
authorization headers
environment dumps

Structured provider errors must remain sanitized.

Do not print raw tracebacks as normal user output.

Verbose mode does not waive this rule.

---

# 18. Output Directory Behavior

Document clearly whether:

existing files are overwritten
new files are added
directories are reused

Do not introduce destructive recursive cleanup.

Do not delete unrelated user files.

Do not modify source.

---

# 19. Real AI Guard

REAL_AI_RUNTIME_CALL_ALLOWED=false

Use FakeLLMProvider/mocks for R5 tests.

Do not call Copilot/Gemini/network providers.

Do not run the real IST repository.

---

# 20. Python Development Style

Maintain all established LegacyMapper practices:

- idiomatic Python first;
- PascalCase classes;
- snake_case modules;
- clear responsibilities;
- type hints on public/service boundaries;
- concise docstrings for significant public classes/functions/methods;
- comments for non-obvious deterministic/security/evidence rules;
- no unnecessary Python magic;
- no C# ceremony transplanted into Python;
- no unnecessary DI/framework abstractions;
- simple, secure, maintainable implementation.

Do not trade maintainability for a prettier CLI.

---

# 21. Tests

Add focused tests covering at minimum:

CLI help explains analyze/full/readiness

default full console summary

successful deterministic full next action

AI-enabled successful proposal next action

AI failure partial next action

fatal run next action

proposal review artifact displayed when proposals exist

no proposal path displayed when proposals do not exist

AI requested vs AI invoked are distinguished

canonical knowledge false displayed correctly

Technical Lead approval false displayed correctly

RUN_SUMMARY.md human readability

RUN_SUMMARY.json backward-compatible existing fields

any new JSON fields deterministic

exit codes unchanged

verbose behavior where changed

no credential leakage

legacy/analyze behavior unchanged

source immutability

real provider never called

Do not weaken/delete existing tests.

---

# 22. Characterization Before Extraction

If extracting responsibilities from full_pipeline.py:

first characterize the existing behavior being moved.

Tests must pin:

RUN_SUMMARY.json
RUN_SUMMARY.md
proposal JSON/Markdown output

as applicable before/while extracting.

The extraction must not alter existing semantics except for explicitly
approved additive R5 UX fields/presentation.

---

# 23. Regression

Entering baseline:

1685_PASS_0_FAIL_0_SKIP

Run:

python -m unittest discover -s tests

Require all existing tests plus R5 tests.

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY

Verify:

python main.py --help
python main.py analyze --help
python main.py full --help
python main.py readiness

Do not run real IST/Operacional.

---

# 24. Maintainability Inventory

If source changes affect:

tests/test_v4_1_r0_maintainability_inventory.py

recompute using:

tools.v4_1_r0.report.build_inventory

Do not hand-estimate.

Do not modify the frozen V4.1 baseline artifact.

Do not weaken assertions.

Report:

full_pipeline.py lines before/after
risk before/after

and any new production modules.

---

# 25. Scope Guard

R5 MUST NOT implement:

human approval command
canonical knowledge promotion
R11/R12 orchestration
Plugin runtime
V5
provider/model agnosticism redesign
new deterministic analysis capability
new AI interpretation semantics
real provider pilot
IST pilot

If UX requires any of these:

STOP and report dependency instead.

---

# 26. Result

Create:

docs/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX_RESULT.md

Include:

STATUS
BASELINE
FILES_CREATED
FILES_MODIFIED
CLI_HELP
CONSOLE_SUMMARY
NEXT_ACTION_MODEL
OUTPUT_DISCOVERY
RUN_SUMMARY_HUMAN
RUN_SUMMARY_MACHINE_CONTRACT
AI_UX
APPROVAL_UX_BOUNDARY
EXIT_CODES
OUTPUT_DIRECTORY_BEHAVIOR
MAINTAINABILITY
SECURITY
TESTS
READINESS
REAL_PROVIDER_CALLS
PRODUCTION_BEHAVIOR_CHANGED
LEGACY_ANALYZE_BEHAVIOR_CHANGED
V4_1_REOPENED
V5_IMPLEMENTED
PLUGIN_RUNTIME
DEFERRED
RISKS
DECISION
NEXT

Expected:

REAL_PROVIDER_CALLS=0
LEGACY_ANALYZE_BEHAVIOR_CHANGED=false

V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED

If successful:

DECISION=V4_2_R5_READY_FOR_TECHNICAL_LEAD_REVIEW
NEXT=HUMAN_REVIEW_V4_2_R5

Otherwise:

DECISION=V4_2_R5_BLOCKED
NEXT=<explicit reason>

---

# 27. Stop

STOP after R5 implementation, tests, readiness and result.

Do not implement R6.
Do not commit.
Do not push.
Do not reopen V4.1.
Do not begin V5.