# LegacyMapper V4.1 — R0 Maintainability Inventory and Refactor Plan

TASK=V4_1_R0_MAINTAINABILITY_INVENTORY_AND_REFACTOR_PLAN

MODE=ANALYSIS_AND_PLANNING_ONLY

PRODUCTION_CODE_MODIFICATION_ALLOWED=false
TEST_SEMANTIC_MODIFICATION_ALLOWED=false
CONTRACT_MODIFICATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Context

LegacyMapper V4 is formally closed.

Required repository state:

```text
V4_CLOSED=true

LATEST_COMPLETED_ROUND=V4-R14
LATEST_APPROVED_ROUND=V4-R14

TESTS=1380_PASS
READINESS=READY

SECURITY_GATE=PASS
REGRESSION_GATE=PASS

PROJECT_STATE=V4_FORMALLY_CLOSED

POST_V4_MAINTAINABILITY_REFACTOR=PLANNED
```

This new phase is:

```text
V4.1 — Comprehensive Maintainability Refactor
```

Governing invariants:

```text
REFRACTOR_GOAL=READABILITY_AND_MAINTAINABILITY
BEHAVIOR_CHANGE=FORBIDDEN
```

V4.1 must preserve all approved V1-V4 behavior and contracts.

---

# Objective

Produce a complete, evidence-based maintainability inventory and a safe refactor roadmap.

Do NOT refactor production code in this round.

R0 must answer:

1. Which parts of LegacyMapper are hardest for a human developer to understand?
2. Which modules/classes/functions have excessive responsibility?
3. Which code is duplicated?
4. Which duplicated code is actually semantically equivalent and safe to consolidate?
5. Which modules have weak typing?
6. Which modules have confusing names?
7. Which modules use broad exception boundaries?
8. Which modules mix pure/domain logic with filesystem/reporting/provider concerns?
9. Which historical modules should be left alone unless characterization tests are added first?
10. In what exact order should the project be refactored to minimize behavioral risk?
11. Which changes can be isolated into small reviewable rounds?
12. Which existing public APIs/contracts require compatibility wrappers?

R0 is a planning round.

Required principle:

```text
UNDERSTAND_FIRST
REFACTOR_SECOND
```

---

# Repository Authority

Read first:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`
6. `docs/V4/V4_FINAL_CLOSURE_RESULT.md`
7. `docs/V4/V4_USER_MANUAL.md`
8. `docs/V4/V4_DEVELOPER_MANUAL.md`
9. `docs/V4/V4_OPERATIONS_AND_RECOVERY_MANUAL.md`
10. `docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md`
11. `output/v4_r14/V4_FINAL_BASELINE.json`
12. `output/v4_r14/V4_FINAL_MANIFEST.json`
13. V3 technical-debt artifact
14. V4-R13 regression/security report

Repository artifacts are authoritative.

Do not rely on conversation history.

---

# Entry Gate

Verify:

```text
latest_completed_round = V4-R14
latest_approved_round = V4-R14

round_status = V4_FORMALLY_CLOSED

next = POST_V4_MAINTAINABILITY_REFACTOR

tests = 1380

readiness = READY

provider_calls = 0
real_llm_calls = 0
```

Run:

```text
git status
```

Expected:

```text
CLEAN
```

The R0 prompt itself may be the only untracked file.

Run:

```text
python -m unittest discover -s tests
```

Require:

```text
>=1380 PASS
```

Run readiness.

Require:

```text
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

If repository state differs materially:

STOP and report.

---

# Preserve V4

V4 is a closed baseline.

R0 must not alter:

```text
V4 contracts
V4 approved artifacts
R10 canonical semantics
R11 document projection semantics
R12 Plugin contract
Technical Lead approval semantics
provenance semantics
temporal semantics
relation semantics
proposal lifecycle
approval lifecycle
deterministic ID semantics
security boundaries
source-code optionality
Plugin boundary
```

---

# Known Deferred Debt

Carry forward and resolve exact definitions from repository artifacts:

```text
TD-001
TD-002
TD-003
TD-004
TD-005

DEBT-001
DEBT-002
DEBT-003
```

For each debt item record:

```text
id
source
original_description
current_relevance
affected_files
risk
recommended_round
recommended_action
```

Do not reinterpret vague debt without checking its original artifact.

---

# Python Development Philosophy

V4.1 must make the code easier for a C# developer to understand while remaining idiomatic Python.

Prefer:

```text
clear modules
clear class responsibilities
PascalCase classes
snake_case modules/functions
type hints
small explicit services
explicit data flow
predictable control flow
useful docstrings
useful comments for non-obvious rules
one significant class per file when it improves clarity
```

Avoid:

```text
unnecessary Python magic
metaprogramming
clever dynamic dispatch
trivial getters/setters
empty interfaces
pattern proliferation
unnecessary dependency injection
one-class-per-file dogma for tiny cohesive types
deep inheritance
hidden global state
```

The goal is not to make Python look like C#.

The goal is to make it understandable to a developer whose primary background is C#.

---

# Inventory Scope

Analyze all production Python under:

```text
legacy_documenter/
```

Do not restrict analysis to V4 packages.

Include historical V1-V3 production code because the future maintainability refactor concerns the whole project.

Exclude:

```text
__pycache__
virtual environments
generated output
tests
historical codex execution records
```

except when tests are needed to evaluate safety.

---

# File Inventory

For every production `.py` file collect where practical:

```text
path
line_count
class_count
function_count
public_symbol_count
docstring_coverage
type_hint_observations
imports
internal_dependencies
filesystem_access
network/provider_access
exception_boundary_observations
responsibility_count
risk_category
```

Do not create complex fake precision.

Metrics are diagnostic.

---

# Largest Modules

Identify at minimum:

* top 20 production files by line count;
* top 20 functions/methods by line count where deterministically measurable;
* top 20 classes by method count / approximate size where practical.

For each, classify:

```text
OK
REVIEW
REFACTOR_CANDIDATE
CHARACTERIZATION_REQUIRED
DO_NOT_TOUCH_WITHOUT_DESIGN_DECISION
```

---

# Responsibility Analysis

Find modules/classes that mix concerns such as:

```text
parsing + domain decisions
domain logic + filesystem
domain logic + serialization
validation + mutation
provider access + business logic
orchestration + formatting
state calculation + report writing
configuration + execution
```

For every candidate identify the actual responsibilities.

Do not classify a module as problematic only because it is long.

Cohesion matters more than raw line count.

---

# Duplication Analysis

Identify duplicated or near-duplicated patterns.

At minimum inspect:

```text
contract_report.py patterns
example_report.py patterns
JSON renderers
stable sorting helpers
validation helpers
artifact hashing
report builders
service batch operations
cross-round helpers
```

For each duplication candidate classify:

```text
SAFE_TO_CONSOLIDATE
SIMILAR_BUT_SEMANTICALLY_DISTINCT
NEEDS_CHARACTERIZATION
DO_NOT_CONSOLIDATE
```

This distinction is critical.

Do not recommend abstraction merely because code looks similar.

---

# Type Safety Analysis

Identify:

```text
missing return annotations
missing parameter annotations
Any usage
dict[str, Any] boundaries
nested untyped JSON
optional/union ambiguity
unchecked mapping access
```

Prioritize public/service boundaries.

Do not require full static typing everywhere.

Identify where stronger typing materially improves maintainability.

---

# Documentation Analysis

Review:

```text
module docstrings
class docstrings
public function/method docstrings
comments explaining non-obvious invariants
comments that merely restate syntax
stale comments
```

Classify documentation debt by usefulness, not percentage alone.

---

# Naming Analysis

Identify confusing names.

Examples:

```text
request
requests
data
result
manager
helper
util
processor
handler
```

Do not rename automatically.

For each suggested rename state:

```text
current_name
reason
suggested_name
public_api_impact
compatibility_strategy
```

---

# Exception Boundary Analysis

Identify:

```text
except Exception
bare except
exception swallowing
exception translation
provider-adapter boundaries
filesystem boundaries
JSON parsing boundaries
```

Classify each broad exception as:

```text
JUSTIFIED_BOUNDARY
REFACTOR_CANDIDATE
HISTORICAL_COMPATIBILITY
RISKY
```

Do not mechanically remove broad exception handling.

---

# Filesystem / Side-Effect Analysis

Identify modules that perform:

```text
filesystem writes
filesystem reads
subprocess
environment access
network/provider access
global state mutation
```

Determine whether side effects are isolated appropriately.

Recommend separation only when it improves responsibilities without changing behavior.

---

# Dependency Direction

Build a lightweight deterministic internal dependency view.

Look for:

```text
circular imports
upward dependencies
projection -> canonical violations
domain -> I/O violations
historical package coupling
cross-round dependencies
```

Do not introduce a graph dependency solely for this analysis.

Use standard library if practical.

---

# Characterization Test Needs

Before recommending extraction/splitting of risky modules, identify whether characterization tests are sufficient.

For each risky candidate classify:

```text
EXISTING_TESTS_SUFFICIENT
ADDITIONAL_CHARACTERIZATION_REQUIRED
TOO_RISKY_WITHOUT_DESIGN_REVIEW
```

List the specific behaviors that need to be frozen before refactoring.

---

# Public Compatibility

Identify public/imported symbols whose paths are likely relied upon by tests or callers.

For each refactor candidate state whether it needs:

```text
NO_WRAPPER
COMPATIBILITY_WRAPPER
REEXPORT
DEPRECATION_PATH
DO_NOT_MOVE
```

Do not assume internal-looking symbols are unused.

Use repository references to verify.

---

# Maintainability Risk Categories

Use:

```text
LOW
MEDIUM
HIGH
VERY_HIGH
```

This is refactor risk, not security severity.

Examples:

LOW:

* duplicated deterministic serializer.

MEDIUM:

* service extraction with strong tests.

HIGH:

* large orchestration flow.

VERY_HIGH:

* historical behavior with weak characterization or externally consumed import path.

---

# Proposed V4.1 Roadmap

Evaluate and refine this initial roadmap:

```text
V4.1-R1 — Shared Reporting / Serialization Cleanup

V4.1-R2 — Models, Types and Public Contracts Readability

V4.1-R3 — Service Responsibility Separation

V4.1-R4 — Readiness Module Decomposition

V4.1-R5 — Large Orchestrators & Complex Flows

V4.1-R6 — Duplication and Cross-Round Helper Consolidation

V4.1-R7 — Exception Boundaries & Adapter Cleanup

V4.1-R8 — Naming, Documentation and C#-Friendly Readability Pass

V4.1-R9 — Comprehensive Regression & Behavioral Equivalence

V4.1-R10 — Maintainability Final Baseline & Closure
```

This ordering is PROPOSED, not authoritative.

R0 must challenge it based on actual repository evidence.

It may:

```text
merge rounds
split rounds
reorder rounds
add a characterization round
defer unsafe work
```

but must justify every change.

---

# Round Design Requirements

Each proposed round must specify:

```text
round_id
title
objective
primary_files
debt_items_addressed
allowed_changes
forbidden_changes
characterization_required
expected_tests
risk
rollback_boundary
human_review_gate
```

Rounds should be small enough for independent Technical Lead review.

Avoid mega-rounds.

---

# Behavior Preservation Strategy

Define how V4.1 will prove:

```text
BEHAVIOR_CHANGE=FORBIDDEN
```

At minimum use:

```text
existing 1380-test baseline
characterization tests
approved artifact hashes
deterministic output comparison
public contract comparison
readiness comparison
security invariant comparison
```

Not every refactor may preserve every generated source file byte-for-byte.

Distinguish:

```text
behavioral equivalence
serialized-contract equivalence
artifact equivalence
implementation equivalence
```

Implementation equivalence is NOT required.

Behavioral/contract equivalence is.

---

# Deterministic Artifact Preservation

Identify which approved artifacts must remain byte-identical during V4.1.

At minimum inspect R10-R14 closure/baseline artifacts and determine:

```text
IMMUTABLE_HISTORICAL_ARTIFACT
REGENERATABLE_WITH_EQUAL_HASH_REQUIRED
CURRENT_STATE_ARTIFACT
NOT_APPLICABLE
```

Do not casually regenerate closed historical artifacts.

---

# Maintainability Success Criteria

R0 must propose measurable but non-gameable success criteria.

Examples:

```text
no behavior regressions
all tests pass
no contract/hash drift
reduced duplicated report logic
reduced mixed responsibilities
improved type coverage at service boundaries
zero undocumented public significant symbols
fewer oversized orchestrators
explicit compatibility wrappers where paths move
```

Do not optimize for metrics alone.

---

# Required Artifact 1

Create:

```text
output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
```

Include at minimum:

```text
baseline

production_inventory

largest_modules
largest_classes
largest_functions

responsibility_candidates
duplication_candidates
type_safety_candidates
documentation_candidates
naming_candidates
exception_candidates
side_effect_candidates
dependency_findings

known_debt

characterization_needs

public_compatibility

risk_summary
```

No timestamps.

No machine-specific absolute paths.

---

# Required Artifact 2

Create:

```text
output/v4_1_r0/V4_1_REFACTOR_PLAN.json
```

Include:

```text
phase = V4.1

goal = READABILITY_AND_MAINTAINABILITY
behavior_change = FORBIDDEN

rounds

global_invariants

baseline_tests

required_final_validation

deferred_items
```

No timestamps.

---

# Determinism

Generate both artifacts twice independently.

Require:

```text
MAINTAINABILITY_INVENTORY_DETERMINISM=PASS
REFACTOR_PLAN_DETERMINISM=PASS
```

---

# Tests

R0 may add analysis/report tests.

Prefer:

```text
tests/test_v4_1_r0_maintainability_inventory.py
```

Tests must validate the analysis tooling, not production semantics.

Do not modify existing semantic tests.

Run full suite.

Require:

```text
>=1380 PASS
```

---

# Production Changes

Required:

```text
PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false
```

Analysis helpers may live outside production packages where practical.

If adding analysis code under production package would blur responsibilities, prefer a dedicated tooling/report location consistent with repository structure.

---

# PROJECT_STATE

After successful R0:

```text
latest_completed_round = V4.1-R0
latest_approved_round = V4-R14

current_round_in_progress =
"V4.1-R0 (pending Technical Lead review)"

round_status =
V4_1_R0_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R0

tests = <actual>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do not mark V4.1 approved.

Do not change V4 closure state.

---

# Required Result

Create:

```text
docs/V4_1/V4_1_R0_MAINTAINABILITY_INVENTORY_AND_REFACTOR_PLAN_RESULT.md
```

Report at minimum:

```text
STATUS
ENTRY_GATE

BASELINE_TESTS
FINAL_TESTS

PRODUCTION_FILES_ANALYZED
TEST_FILES_ANALYZED

KNOWN_DEBT_ITEMS
NEW_MAINTAINABILITY_FINDINGS

HIGH_RISK_CANDIDATES
VERY_HIGH_RISK_CANDIDATES

DUPLICATION_CANDIDATES
SAFE_CONSOLIDATION_CANDIDATES

TYPE_SAFETY_FINDINGS
DOCUMENTATION_FINDINGS
NAMING_FINDINGS
EXCEPTION_BOUNDARY_FINDINGS
SIDE_EFFECT_FINDINGS
DEPENDENCY_FINDINGS

CHARACTERIZATION_REQUIRED

PROPOSED_ROUNDS
ROADMAP_CHANGED_FROM_INITIAL_PROPOSAL
ROADMAP_CHANGE_JUSTIFICATION

MAINTAINABILITY_INVENTORY
MAINTAINABILITY_INVENTORY_SHA256

REFACTOR_PLAN
REFACTOR_PLAN_SHA256

MAINTAINABILITY_INVENTORY_DETERMINISM
REFACTOR_PLAN_DETERMINISM

PRODUCTION_CODE_CHANGED
PRODUCTION_BEHAVIOR_CHANGED

READINESS
AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE

DECISION
NEXT
```

---

# Expected Success State

```text
STATUS=V4_1_R0_MAINTAINABILITY_INVENTORY_COMPLETE

ENTRY_GATE=PASS

FINAL_TESTS=>=1380_PASS

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

MAINTAINABILITY_INVENTORY_DETERMINISM=PASS
REFACTOR_PLAN_DETERMINISM=PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

DECISION=V4_1_R0_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_1_R0
```

---

# Stop Condition

STOP after inventory, plan, tests, artifacts and result document.

Do NOT:

* refactor production code;
* approve R0;
* commit;
* push;
* start V4.1-R1;
* change V4 contracts;
* regenerate closed historical artifacts;
* start V5;
* implement Plugin runtime.

The next action is:

```text
HUMAN_REVIEW_V4_1_R0
```
