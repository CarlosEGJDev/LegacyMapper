# LegacyMapper V4.2-R2
# Deterministic Full Pipeline Orchestrator

TASK=V4_2_R2_DETERMINISTIC_FULL_PIPELINE_ORCHESTRATOR

MODE=CONTROLLED_IMPLEMENTATION

PRODUCTION_CODE_CHANGE_ALLOWED=true
TEST_CHANGE_ALLOWED=true

V4_1_REOPEN_ALLOWED=false
V5_IMPLEMENTATION_ALLOWED=false
PLUGIN_RUNTIME_IMPLEMENTATION_ALLOWED=false

AI_RUNTIME_CALL_ALLOWED=false

COMMIT_ALLOWED=false
PUSH_ALLOWED=false

---

# 1. Authority

V4.2-R0 and V4.2-R1 have been reviewed and approved by the Technical Lead.

Read:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/PROJECT_RECOVERY.md
docs/GENERATED_ARTIFACT_POLICY.md

docs/V4_2/V4_2_R0_FULL_PIPELINE_ARCHITECTURE_AND_INVENTORY_RESULT.md
docs/V4_2/V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL_RESULT.md

Inspect current production source before implementation.

---

# 2. Objective

Implement the deterministic backbone of:

python main.py full <repository> --output <directory>

using the execution model established in R1.

R2 must make `full` genuinely useful.

The deterministic full pipeline is:

SCAN
→ EXTRACTION
→ deterministic normalization/consolidation
→ CALL_RESOLUTION
→ WEB_ENTRY_RESOLUTION
→ DATABASE_RESOLUTION
→ FLOW_RESOLUTION
→ DEPENDENCY_RESOLUTION
→ EXPORT
→ CONTEXT
→ FINAL_SUMMARY

R2 does NOT include:

new documentation renderers
AI interpretation
knowledge proposal generation
human approval
canonical knowledge
R11/R12 orchestration
Plugin runtime
V5

---

# 3. Fundamental Rule

Do not duplicate the existing analysis implementation.

The existing `analyze_repository()` behavior is authoritative.

Refactor only as much as necessary to expose reusable deterministic stages.

The CLI is an orchestration boundary.

CLI parsing != orchestration
orchestration != extraction
orchestration != analysis
orchestration != documentation

Do not copy existing scanner/extractor/resolver/exporter logic into a second
pipeline.

If reusable stage extraction is required, extract existing behavior into
clearly named functions/services and make BOTH:

legacy/analyze
and
full

reuse those functions.

---

# 4. Backward Compatibility — HARD REQUIREMENT

These must remain supported:

python main.py <repository> ...
python main.py analyze <repository> ...

Their observable deterministic analysis output must remain equivalent to
the pre-R2 behavior.

Do not make legacy/analyze use the new partial-failure policy if doing so
would alter its established behavior.

If necessary:

analyze = compatibility orchestration
full = resilient orchestration

while sharing the underlying deterministic stage implementations.

No duplicated domain logic.

---

# 5. Full Command

Replace R1's NOT_IMPLEMENTED_FOR_R1 placeholder.

`full` must now execute the deterministic pipeline.

Expected conceptual behavior:

python main.py full <repository> --output <directory>

→ execute deterministic stages
→ preserve useful partial results
→ generate existing machine/context/documentation artifacts
→ generate a deterministic run summary
→ return an exit code representing overall run status

Do not invoke AI.

Do not invoke Technical Lead approval.

Do not invoke canonical knowledge.

---

# 6. Stage Execution

Use the R1 model:

RunResult
StageResult
StageError
StageId
RunStatus
StageStatus

Populate real stage results.

Every stage that actually runs must be represented.

Do not create fake SUCCESS stages.

A stage result must correspond to real execution.

---

# 7. Partial-Failure Policy

Implement the R0 policy.

Extraction remains per-file tolerant as today.

For resolver/output stages:

a stage failure must be captured as StageError rather than automatically
terminating the complete `full` process.

Continue independent downstream stages where safe.

If a downstream stage requires a failed upstream result, mark it:

SKIPPED_DUE_TO_UPSTREAM_FAILURE

Do not execute it with invalid/missing prerequisites.

Do not invent replacement data.

Examples:

WEB_ENTRY_RESOLUTION failure
may require FLOW_RESOLUTION to be skipped.

EXPORT failure
must not automatically imply that analysis stages failed.

AI is not present in R2.

---

# 8. Dependency Rules

Define explicit, minimal dependencies between deterministic stages.

Do NOT implement a generic DAG/workflow engine.

A simple orchestration sequence with explicit dependency checks is preferred.

Document dependencies in code where non-obvious.

At minimum validate dependencies around:

SCAN → EXTRACTION

EXTRACTION → resolution stages

CALL_RESOLUTION → WEB_ENTRY_RESOLUTION / FLOW_RESOLUTION as actually required

WEB_ENTRY_RESOLUTION → FLOW_RESOLUTION

DATABASE_RESOLUTION → FLOW_RESOLUTION

analysis results → EXPORT

analysis results → CONTEXT

Derive exact dependencies from source signatures.

Do not assume them from this prompt if source contradicts them.

---

# 9. Extraction Semantics

Preserve the current two extraction loops and their per-file error tolerance.

Existing extraction errors must remain visible in generated analysis output.

A run with extraction errors may legitimately become:

PARTIAL

rather than FAILED,

provided useful analysis/output can still be produced.

Define and test this explicitly.

---

# 10. Run Status

Derive RunStatus deterministically.

Expected semantics:

SUCCESS:
all required deterministic stages completed successfully and no condition
classified as partial occurred.

PARTIAL:
useful output exists but one or more recoverable failures/unresolved
conditions occurred.

FAILED:
the run could not produce a minimally useful deterministic analysis package.

Define "minimally useful" concretely in code/tests/result documentation.

Do not make this subjective.

---

# 11. Exit Codes

Preserve:

0 = SUCCESS

Define stable exit codes for:

PARTIAL
FAILED

Do not collide with argparse usage error 2 unless unavoidable.

R1 used 3 for NOT_IMPLEMENTED; that placeholder disappears in R2.

Document the final V4.2-R2 exit-code contract.

Scripts must be able to distinguish:

SUCCESS
PARTIAL
FAILED
CLI_USAGE_ERROR

---

# 12. Final Run Summary

Generate a deterministic summary artifact for `full`.

It must allow a human or script to understand:

command
overall status
stage statuses
structured errors
whether useful outputs were produced
whether AI was invoked
whether canonical knowledge was produced
whether Technical Lead approval occurred

For R2 these invariants must always be:

AI_INVOKED=false
CANONICAL_KNOWLEDGE_PRODUCED=false
TECHNICAL_LEAD_APPROVAL=false

Use a clear location under the selected run output directory.

Choose the exact filename based on repository conventions and document it in
the result.

Prefer both:

machine-readable JSON as authoritative execution record

and, only if trivial without duplicating logic, a small human-readable
summary.

Do not implement R3 technical documentation here.

---

# 13. Determinism

The run summary must be deterministic for equivalent execution results.

No random UUID.

No current timestamp in identity-critical payload.

No machine/environment dump.

No raw traceback as primary machine error representation.

Ordering must be stable.

Reuse existing deterministic JSON utilities.

---

# 14. Source Safety

The analyzed repository is READ-ONLY.

R2 must never:

write into source
rename source files
delete source files
create temporary files inside source
modify project/solution/config files

All generated artifacts go under `--output`.

Add/retain tests proving source immutability where practical.

---

# 15. Output Safety

Do not delete a user's existing output directory blindly.

Inspect current exporter behavior.

If overwrite behavior already exists, preserve compatibility for `analyze`.

For `full`, document the exact behavior.

Do not introduce destructive cleanup such as recursive directory deletion
unless explicitly required and safely scoped.

---

# 16. Execution Architecture

Prefer a small dedicated orchestration component rather than placing the
full pipeline in `router.py`.

Illustrative only:

legacy_documenter/cli/full_pipeline.py

or:

legacy_documenter/orchestration/full_pipeline.py

Choose based on existing architecture.

The router should route.

The orchestrator should orchestrate.

Domain components should perform domain work.

Do not create unnecessary interfaces or dependency-injection infrastructure.

---

# 17. Python Development Style

Use idiomatic Python first.

Keep organization understandable for a C# developer where compatible.

PascalCase classes.
snake_case modules.

Clear responsibilities.

Type hints on public/service boundaries.

Concise explanatory docstrings on significant public classes/functions.

Comments for non-obvious deterministic/security/evidence rules.

Avoid unnecessary Python magic.

Avoid C# ceremony transplanted into Python.

Keep code simple and maintainable.

---

# 18. Analyze Equivalence

Perform an equivalence check:

legacy invocation
vs
explicit analyze

using a representative committable fixture.

Require identical generated artifacts.

If refactoring existing analysis code was necessary, also compare against a
pre-R2 expected/characterized result where available.

Do not claim equivalence without evidence.

---

# 19. Full Pipeline Tests

Add focused tests covering at minimum:

full executes deterministic stages

stage ordering

successful run → SUCCESS

recoverable stage failure → PARTIAL

fatal/minimal-output failure → FAILED

upstream failure → dependent stage SKIPPED_DUE_TO_UPSTREAM_FAILURE

independent downstream stage can continue

extraction errors preserved

structured errors contain no raw traceback contract

run summary deterministic

AI_INVOKED=false

CANONICAL_KNOWLEDGE_PRODUCED=false

TECHNICAL_LEAD_APPROVAL=false

source repository remains unchanged

legacy CLI remains compatible

analyze remains compatible

readiness remains compatible

full does not import/call AI

full does not import/call approval/canonical/projection/plugin runtime

Do not weaken/delete existing tests.

---

# 20. Regression

Run:

python -m unittest discover -s tests

Baseline entering R2:

1601_PASS_0_FAIL_0_SKIP

Require:

all 1601 existing tests remain passing
plus new R2 tests.

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY

Also verify:

python main.py --help
python main.py analyze --help
python main.py full --help
python main.py readiness

Do not execute a multi-GB real IST analysis merely for this round.

Use fixtures.

---

# 21. Maintainability Inventory Test

If:

tests/test_v4_1_r0_maintainability_inventory.py

requires an update because legitimate new production modules were added:

do not blindly change expected numbers.

Recompute the actual inventory using the same deterministic inventory
builder used by the test.

Document:

previous value
new value
reason for delta
new production modules responsible

Do not modify the frozen V4.1-R0 artifact.

Do not weaken assertions.

---

# 22. Scope Guard

R2 MUST NOT implement:

new R3 Markdown renderers
AI interpretation
knowledge ingestion integration
proposal generation
human approval UX
canonical knowledge
R11/R12
Plugin runtime
V5

If any becomes required unexpectedly:

STOP and report why.

Do not silently expand scope.

---

# 23. Result

Create:

docs/V4_2/V4_2_R2_DETERMINISTIC_FULL_PIPELINE_ORCHESTRATOR_RESULT.md

Include:

STATUS
BASELINE
FILES_CREATED
FILES_MODIFIED
ORCHESTRATOR_ARCHITECTURE
ANALYZE_EQUIVALENCE
FULL_PIPELINE
STAGE_ORDER
STAGE_DEPENDENCIES
PARTIAL_FAILURE_POLICY
RUN_STATUS_CONTRACT
EXIT_CODE_CONTRACT
RUN_SUMMARY
SOURCE_IMMUTABILITY
OUTPUT_BEHAVIOR
TESTS
READINESS
AI_INVOKED
CANONICAL_KNOWLEDGE_PRODUCED
TECHNICAL_LEAD_APPROVAL
PRODUCTION_BEHAVIOR_CHANGED
LEGACY_ANALYZE_BEHAVIOR_CHANGED
V4_1_REOPENED
V5_IMPLEMENTED
PLUGIN_RUNTIME
DEFERRED_TO_R3
DEFERRED_TO_R4
RISKS
DECISION
NEXT

Expected invariants:

AI_INVOKED=false
CANONICAL_KNOWLEDGE_PRODUCED=false
TECHNICAL_LEAD_APPROVAL=false

LEGACY_ANALYZE_BEHAVIOR_CHANGED=false

V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED

If successful:

DECISION=V4_2_R2_READY_FOR_TECHNICAL_LEAD_REVIEW
NEXT=HUMAN_REVIEW_V4_2_R2

Otherwise:

DECISION=V4_2_R2_BLOCKED
NEXT=<explicit reason>

---

# 24. Stop

STOP after R2 implementation, tests, readiness and result.

Do not implement R3.
Do not commit.
Do not push.
Do not reopen V4.1.
Do not begin V5.