# LegacyMapper V4.2-R6
# Robustness, Recovery, Security and Approval-Surface Design

TASK=V4_2_R6_ROBUSTNESS_RECOVERY_SECURITY_AND_APPROVAL_SURFACE

MODE=CONTROLLED_IMPLEMENTATION

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

V4.2-R0 through R5.1 are reviewed, approved and versioned.

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
docs/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX_RESULT.md
docs/V4_2/V4_2_R5_1_EXIT_CODE_CONTRACT_AND_REAL_PROVIDER_GUARD_RESULT.md
docs/V4_2/V4_2_R5_R5_1_CLOSURE_AND_VERSIONING_RESULT.md

Current authoritative exit-code contract:

SUCCESS = 0
PARTIAL = 1
CLI_USAGE_ERROR = 2
FAILED = 4

Entering baseline:

1723_PASS_0_FAIL_0_SKIP

---

# 2. Objective

Harden the V4.2 full workflow before the real IST/Operacional pilot.

R6 focuses on:

- robustness;
- failure containment;
- recovery/re-run behavior;
- output integrity;
- security;
- clear approval-surface design;
- maintainability of the orchestrator.

R6 does NOT perform the real IST pilot.

R6 does NOT implement approval.

---

# 3. Characterize Before Changing

Before modifying production behavior, characterize the current full pipeline
with focused tests.

Inspect especially:

legacy_documenter/cli/full_pipeline.py
legacy_documenter/cli/pipeline_stages.py
legacy_documenter/cli/run_summary_presenter.py
legacy_documenter/cli/execution_model.py
legacy_documenter/orchestration/
legacy_documenter/knowledge/proposals/
legacy_documenter/knowledge/approval/
legacy_documenter/knowledge/canonical/

Identify:

stage dependencies
failure propagation
files written by each stage
behavior when output already exists
behavior after an interrupted/partial previous run
proposal artifact behavior
summary-writing behavior

Do not infer contracts solely from previous result documents.

---

# 4. Recovery / Re-run Semantics

A user must be able to safely run LegacyMapper again against the same output
directory.

Characterize and harden:

successful run → successful rerun
partial run → rerun
failed run → rerun
AI-enabled run → deterministic run in same output directory
deterministic run → AI-enabled run in same output directory

Do not recursively delete the output directory.

Do not delete unrelated user files.

Prevent stale LegacyMapper-owned artifacts from making a new run appear to
have produced results it did not actually produce.

Define ownership of generated artifacts explicitly.

If selective cleanup of LegacyMapper-owned stale artifacts is necessary,
make it deterministic and narrowly scoped.

Never clean arbitrary/unrecognized files.

---

# 5. Stale Proposal Safety

This boundary is especially important.

Example:

Run A:
full --allow-ai-interpretation
→ proposals generated

Run B:
full without AI
→ same output directory

Run B must NOT appear to have generated or currently require review of Run
A's stale proposals.

Likewise:

AI failure after a previous successful AI run must not leave stale proposals
that look current.

Design the smallest safe behavior.

Possible solutions include deterministic ownership/cleanup or run-scoped
metadata.

Do not introduce a large artifact-management framework.

---

# 6. Summary Integrity

RUN_SUMMARY.json and RUN_SUMMARY.md must describe the CURRENT run.

They must not infer current success from stale files left by an earlier run.

Review the pre-existing R5 documented discrepancy where the persisted summary
is created before FINAL_SUMMARY is appended.

Decide whether this should be corrected in R6.

Preferred invariant:

persisted RUN_SUMMARY represents the final completed run state as closely as
possible without recursive self-reference.

If fixing this requires a small clean design, do so.

If there is a genuine reason to preserve the preliminary/final distinction,
document it and prove it safe.

---

# 7. Interrupted Writes

Review how important machine artifacts are written.

At minimum inspect:

RUN_SUMMARY.json
proposal JSON
core index JSON

For authoritative machine-readable artifacts, avoid leaving a partially
written/corrupted file if the process is interrupted during replacement.

Prefer a small standard-library atomic-write helper where justified:

write temporary sibling
flush/close
os.replace

Do not introduce transactional infrastructure.

Apply only where it materially improves recovery/integrity.

---

# 8. Failure Containment

Characterize failures at:

SCAN
EXTRACTION
resolvers
EXPORT
CONTEXT
DOCUMENTATION
AI_INTERPRETATION
PROPOSAL_GENERATION
FINAL_SUMMARY

Verify independent stages continue where appropriate.

Verify dependent stages become:

SKIPPED_DUE_TO_UPSTREAM_FAILURE

rather than crashing.

Verify FINAL_SUMMARY is attempted whenever enough execution state exists to
report the failure.

Do not hide failures.

Do not convert serious deterministic failure into SUCCESS.

---

# 9. Filesystem Errors

Add controlled tests for representative filesystem problems where practical:

output directory unavailable/unwritable
artifact replacement failure
documentation write failure
summary write failure

Do not depend on OS-specific permission behavior when a mock/fake can
characterize it more reliably.

Errors must be structured and understandable.

No raw traceback as the normal CLI contract.

---

# 10. Source Immutability

Re-verify the analyzed repository remains read-only from LegacyMapper's
perspective.

No recovery/cleanup operation may ever target the source repository.

All cleanup/replacement logic must be scoped exclusively beneath the selected
output directory and only to LegacyMapper-owned paths.

Add a regression test if current coverage does not prove this strongly
enough.

---

# 11. Path Safety

Review all R2-R5 output paths.

Ensure generated paths cannot escape the selected output root through:

absolute paths
`..`
unexpected proposal/document names
provider-controlled names

AI/provider output must never control filesystem paths.

Artifact filenames must come from deterministic trusted code.

Use resolved-path validation if current architecture makes traversal possible.

Do not over-engineer if paths are already closed constants; characterize and
document that fact.

---

# 12. Security

Re-verify:

no secrets/tokens/API keys in summaries
no environment dumps
provider errors sanitized
no raw traceback
no source modification
no AI-controlled output paths
no automatic approval
no canonical promotion

The R5.1 test-suite-wide provider guard must remain effective.

REAL_AI_RUNTIME_CALL_ALLOWED=false

All AI tests/manual verification must use:

FakeLLMProvider
stub
mock
or tools/manual_verify_full_pipeline

Never invoke the normal real-provider path during R6.

---

# 13. Approval Surface — DESIGN ONLY

R6 must inspect the existing:

knowledge/approval

contract and the proposal artifacts generated by R4/R5.

Design the future human approval surface needed after R6/R7.

Do NOT implement an approve command.

Document at minimum:

what the Technical Lead must review
proposal identity
evidence references
AI interpretation
proposal status
possible future decisions
how an approval decision would bind to an exact proposal
how corrected/rejected proposals should behave
how stale proposals from a previous run must be distinguished
what data is required before canonical promotion

The design must preserve:

Technical Lead = sole final approval authority

AI cannot approve.

Approval provenance remains separate from source provenance.

Do not add enterprise RBAC.

---

# 14. Approval-Surface Artifact

Create a design document:

docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md

This is a design artifact only.

It must clearly label:

IMPLEMENTATION_STATUS=NOT_IMPLEMENTED

Do not expose a fake/nonfunctional CLI command.

---

# 15. Orchestrator Maintainability

`legacy_documenter/cli/full_pipeline.py` enters R6 at approximately 488 lines
and VERY_HIGH risk.

R6 touches failure/recovery/summary orchestration, so this is now a justified
opportunity for a narrow extraction if characterization supports it.

Do NOT refactor merely to satisfy a metric.

Prefer extracting responsibilities directly touched by R6, for example:

artifact lifecycle/recovery
proposal output lifecycle
summary finalization

Keep `run_full_pipeline` readable as orchestration.

Do not move domain logic into CLI modules.

Do not change behavior unrelated to R6.

Report:

line count before/after
risk before/after
responsibilities extracted

---

# 16. Output Ownership

Document LegacyMapper-owned V4.2 paths.

At minimum evaluate:

index/
context/
ai_context/
documentation/
proposals/
RUN_SUMMARY.json
RUN_SUMMARY.md

Define whether ownership is:

whole directory
known files within directory

Choose the narrowest safe ownership model.

Unknown user-created files must be preserved.

This ownership contract should support R7 real-pilot recovery.

---

# 17. No Real IST Yet

Do NOT run:

C:\Users\cgalianj\source\IST_40\operacional
C:\inetpub\wwwroot\2010\IST\operacional

or any real corporate/legacy repository.

Use committed fixtures only.

R7 is the controlled real pilot.

---

# 18. Python Development Practices

Maintain established LegacyMapper practices:

idiomatic Python first;
PascalCase classes;
snake_case modules;
clear responsibilities;
type hints on public/service boundaries;
concise docstrings on significant public APIs;
comments for non-obvious security/evidence/recovery rules;
avoid Python magic;
avoid unnecessary C# ceremony;
avoid unnecessary DI/framework abstractions;
simple, secure, maintainable implementation.

Prefer deterministic helpers over AI for all recovery/security behavior.

---

# 19. Tests

Add focused tests covering at minimum:

successful rerun same output
partial → rerun
failed → rerun
AI → non-AI same output
non-AI → AI same output
stale proposals cannot appear current
AI failure removes/invalidates prior current proposals safely
unknown user files preserved
source repository untouched
summary represents current run
summary failure structured
proposal write failure structured
representative filesystem failure
path traversal impossible through proposal/provider content
real provider resolution blocked in tests
credentials never serialized
no approval produced
no canonical knowledge produced
exit codes remain 0/1/2/4
legacy/analyze unchanged

If atomic writes are introduced:

test replacement semantics and cleanup of temporary files on controlled
failure where practical.

Do not weaken/delete existing tests.

---

# 20. Regression

Run:

python -m unittest discover -s tests

Entering baseline:

1723_PASS_0_FAIL_0_SKIP

Require all previous tests plus R6 tests.

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY
provider_calls=0
real_llm_calls=0

REAL_PROVIDER_CALLS=0

Verify:

python main.py --help
python main.py full --help
python main.py readiness

Use no real provider.

Use no real IST repository.

---

# 21. Maintainability Inventory

If production modules change, recompute with:

tools.v4_1_r0.report.build_inventory

Do not hand-estimate.

Do not modify the frozen V4.1 inventory.

Update the live maintainability test only for empirically verified deltas.

Do not weaken assertions.

---

# 22. Scope Guard

R6 MUST NOT implement:

approve command
Technical Lead decision execution
canonical promotion
R11/R12 orchestration
Plugin runtime
V5 architecture
language/framework/database agnosticism
provider/model agnosticism redesign
real-provider pilot
IST pilot

If any becomes necessary:

STOP and report the dependency.

---

# 23. Result

Create:

docs/V4_2/V4_2_R6_ROBUSTNESS_RECOVERY_SECURITY_AND_APPROVAL_SURFACE_RESULT.md

Include:

STATUS
BASELINE
FILES_CREATED
FILES_MODIFIED
CHARACTERIZATION
OUTPUT_OWNERSHIP
RERUN_SEMANTICS
STALE_PROPOSAL_SAFETY
SUMMARY_INTEGRITY
ATOMIC_WRITE_DECISION
FAILURE_CONTAINMENT
FILESYSTEM_FAILURES
SOURCE_IMMUTABILITY
PATH_SAFETY
SECURITY
APPROVAL_SURFACE_DESIGN
ORCHESTRATOR_MAINTAINABILITY
TESTS
READINESS
REAL_PROVIDER_CALLS
EXIT_CODE_CONTRACT
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

EXIT_CODE_CONTRACT=SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4

LEGACY_ANALYZE_BEHAVIOR_CHANGED=false
V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED

Approval design artifact:

docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md

must exist with:

IMPLEMENTATION_STATUS=NOT_IMPLEMENTED

If successful:

DECISION=V4_2_R6_READY_FOR_TECHNICAL_LEAD_REVIEW
NEXT=HUMAN_REVIEW_V4_2_R6

Otherwise:

DECISION=V4_2_R6_BLOCKED
NEXT=<explicit reason>

---

# 24. Stop

STOP after R6 implementation, tests, readiness and result.

Do not implement R7.
Do not commit.
Do not push.
Do not run IST.
Do not call a real provider.