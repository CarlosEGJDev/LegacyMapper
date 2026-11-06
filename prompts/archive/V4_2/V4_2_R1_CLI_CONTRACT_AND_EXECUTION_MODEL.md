# LegacyMapper V4.2-R1
# CLI Contract and Execution Model

TASK=V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL

MODE=CONTROLLED_IMPLEMENTATION

PRODUCTION_CODE_CHANGE_ALLOWED=true
TEST_CHANGE_ALLOWED=true

V4_1_REOPEN_ALLOWED=false
V5_IMPLEMENTATION_ALLOWED=false
PLUGIN_RUNTIME_IMPLEMENTATION_ALLOWED=false

COMMIT_ALLOWED=false
PUSH_ALLOWED=false

---

# 1. Authority

V4.2-R0 has been reviewed and approved by the Technical Lead.

Read before implementation:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/PROJECT_RECOVERY.md
docs/GENERATED_ARTIFACT_POLICY.md

docs/V4_2/V4_2_R0_FULL_PIPELINE_ARCHITECTURE_AND_INVENTORY_RESULT.md

docs/V4_1/LEGACYMAPPER_TECHNICAL_MANUAL_V4_1.md
docs/V4_1/LEGACYMAPPER_GLOSSARY_V4_1.md

Inspect current production source directly before modifying it.

---

# 2. Objective

Implement only the foundational execution contracts required by V4.2:

1. introduce a clear CLI command model;
2. preserve the complete existing CLI behavior;
3. introduce an execution/result model suitable for the future full pipeline;
4. establish clean orchestration boundaries for R2+.

Do NOT implement the full pipeline in R1.

---

# 3. Backward Compatibility — HARD REQUIREMENT

The existing invocation MUST continue to work:

python main.py <repository> \
    [--output OUTPUT] \
    [--exclude FOLDER] \
    [--verbose] \
    [--flow-max-depth N]

Its observable analysis behavior and generated artifacts must remain equivalent
to V4.1.

Do not require existing users/scripts to add the `analyze` word.

---

# 4. New CLI Contract

Introduce explicit subcommand support.

Target user-facing contract:

python main.py analyze <repository> [existing analysis options]

python main.py full <repository> [existing analysis options]

python main.py readiness

AND preserve:

python main.py <repository> [existing analysis options]

as an alias for:

python main.py analyze <repository> [existing analysis options]

Important:

R1 establishes parsing/routing contracts.

R1 MUST NOT implement the future full pipeline.

The `full` command may exist only as a clearly controlled placeholder/router
for the future V4.2 pipeline.

It MUST NOT silently behave as if the full pipeline already exists.

Choose a safe behavior such as a clear NOT_IMPLEMENTED_FOR_R1 result and
non-success exit code if appropriate.

Document and test the exact behavior.

Do not fake successful full-pipeline execution.

---

# 5. Readiness Command

Add:

python main.py readiness

as a thin user-facing route to the existing readiness capability.

Do not duplicate readiness logic.

Reuse:

legacy_documenter.knowledge.readiness

The existing command:

python -m legacy_documenter.knowledge.readiness

must continue to work unchanged.

---

# 6. Execution Model

Introduce a small, explicit execution model suitable for R2+.

At minimum evaluate and implement the minimal useful equivalents of:

RunStatus
StageStatus
StageResult
RunResult

Exact names may differ if source architecture justifies better names.

The model must support future representation of:

SUCCESS
PARTIAL
FAILED

and stage states equivalent to:

SUCCESS
FAILED
SKIPPED_DUE_TO_UPSTREAM_FAILURE
NOT_RUN

Do not over-engineer.

Do not create a workflow framework.

Do not introduce a generic DAG engine.

Do not introduce dependency injection infrastructure.

The model exists only to make orchestration state explicit and testable.

---

# 7. Stage Identity

Define a stable, explicit way to identify future full-pipeline stages.

Candidate stages include:

SCAN
EXTRACTION
CALL_RESOLUTION
WEB_ENTRY_RESOLUTION
DATABASE_RESOLUTION
FLOW_RESOLUTION
DEPENDENCY_RESOLUTION
EXPORT
CONTEXT
DOCUMENTATION
AI_INTERPRETATION
PROPOSAL_GENERATION
FINAL_SUMMARY

Do not execute these stages through a new orchestrator in R1.

Only establish the representation required for future rounds.

If some candidate stage names do not match actual architecture, correct them
and document why.

---

# 8. Error Representation

Stage failures must eventually be representable without serializing raw
Python tracebacks as the primary machine contract.

Create a minimal structured error representation capable of carrying:

stage
error type/category
human-readable message

Optionally:

affected input/reference

Do not expose secrets.

Do not store arbitrary environment contents.

Do not implement R2 stage-level exception handling yet.

R1 defines the contract only.

---

# 9. Result Serialization

Provide deterministic serialization for the execution/result model.

Requirements:

same model → same serialized output
stable ordering
no timestamp required for identity
no UUID/random IDs
no machine-specific absolute paths unless they are explicit run inputs
no credentials/environment dumps

Prefer existing JSON rendering utilities where appropriate.

Do not duplicate deterministic JSON infrastructure already present in V4.1.

---

# 10. Python Development Style

Use idiomatic Python first.

Where compatible, keep organization comfortable for a C# developer.

Classes:
PascalCase

Modules:
snake_case

Prefer one significant class per file where it improves clarity.

Use type hints consistently at public/service boundaries.

Significant public classes/functions/methods require concise explanatory
docstrings.

Avoid unnecessary Python magic.

Avoid trivial getter/setter wrappers.

Avoid empty interfaces.

Avoid unnecessary dependency injection or pattern proliferation.

Comments should explain non-obvious orchestration, deterministic,
security, evidence, or compatibility rules.

Keep implementation simple.

---

# 11. CLI Architecture

Do not turn main.py into a larger monolith.

If parsing/routing begins to make main.py harder to understand, extract a
small dedicated CLI package/module.

Possible shape:

legacy_documenter/cli/
    parser.py
    router.py

This is illustrative, not mandatory.

Derive the actual structure from the current source.

Responsibilities should remain clear:

CLI parsing
≠
command routing
≠
analysis implementation
≠
execution result model

Do not move existing analysis logic merely for cosmetic reasons.

---

# 12. Full Command Boundary

For R1:

full != implemented full pipeline

The CLI must clearly communicate that the contract exists but execution will
be implemented in subsequent V4.2 rounds.

Do not call:

AI interpretation
knowledge ingestion
proposal generation
approval
canonical knowledge
R11
R12

from `full` in R1.

---

# 13. Approval Boundary

No CLI route may automatically create an approved canonical entry.

No CLI route may manufacture Technical Lead approval.

ApprovalAuthority.TECHNICAL_LEAD remains unchanged.

R1 must not add an `approve` command.

---

# 14. V5 Boundary

Do not implement:

language agnosticism
framework agnosticism
database agnosticism
project-layout agnosticism
AI provider/model redesign

Do not create speculative V5 abstractions.

V4.2 remains focused on the current .NET/VB.NET/WebForms/Oracle system.

---

# 15. Tests

Add focused tests for at minimum:

legacy positional CLI remains accepted

explicit `analyze` command accepted

existing analysis flags accepted through `analyze`

`full` command parsed/routed according to the R1 placeholder contract

`readiness` routes to existing readiness logic

existing `python -m legacy_documenter.knowledge.readiness` remains valid

execution status model

stage status model

structured error model

deterministic result serialization

no automatic approval/canonical behavior from R1 CLI routes

Do not weaken or delete existing tests.

---

# 16. Regression

Run the complete suite:

python -m unittest discover -s tests

Expected:

at least 1566 existing tests remain passing
plus new R1 tests.

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY

Verify existing CLI help/behavior.

Verify both:

python main.py --help

python main.py analyze --help

Do not run a destructive or multi-GB legacy analysis merely to validate
argument parsing.

---

# 17. Scope Guard

R1 MUST NOT implement:

full-pipeline orchestration
new technical-document renderers
AI interpretation integration
proposal adapter
human approval UX
canonical knowledge integration
R11/R12 orchestration
Plugin runtime
V5

If implementation discovers that one of these is required for the CLI
contract itself, STOP and report the dependency instead of expanding scope.

---

# 18. Result

Create:

docs/V4_2/V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL_RESULT.md

Include at minimum:

STATUS
BASELINE
FILES_CREATED
FILES_MODIFIED
CLI_ARCHITECTURE
LEGACY_CLI_COMPATIBILITY
ANALYZE_COMMAND
FULL_COMMAND
READINESS_COMMAND
EXECUTION_MODEL
STAGE_MODEL
ERROR_MODEL
SERIALIZATION
TESTS
READINESS
PRODUCTION_BEHAVIOR_CHANGED
V4_1_REOPENED
V5_IMPLEMENTED
PLUGIN_RUNTIME
DEFERRED_TO_R2
DEFERRED_TO_R3
DEFERRED_TO_R4
RISKS
DECISION
NEXT

Expected invariants:

V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED

The legacy analysis path must remain behaviorally compatible.

If successful:

DECISION=V4_2_R1_READY_FOR_TECHNICAL_LEAD_REVIEW
NEXT=HUMAN_REVIEW_V4_2_R1

Otherwise:

DECISION=V4_2_R1_BLOCKED
NEXT=<explicit reason>

---

# 19. Stop

STOP after R1 implementation, tests, readiness verification and result.

Do not implement R2.
Do not commit.
Do not push.
Do not reopen V4.1.
Do not begin V5.