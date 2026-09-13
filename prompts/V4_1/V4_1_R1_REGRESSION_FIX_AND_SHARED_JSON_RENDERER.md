# LegacyMapper V4.1 — R1 Regression Fix and Shared JSON Renderer

TASK=V4_1_R1_REGRESSION_FIX_AND_SHARED_JSON_RENDERER

MODE=CONTROLLED_LOW_RISK_REFACTOR

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

V4.1-R1 has exactly two sequential objectives:

```text
A. Fix REG-002-CANDIDATE with the smallest correct test-only change.

B. Consolidate DUP-001 / DEBT-001:
   the byte-identical contract JSON rendering pattern.
```

These objectives MUST occur in that order.

Required invariant:

```text
R1_REFACTOR_MAY_BEGIN_ONLY_AFTER_FULL_SUITE_GREEN=true
```

Do not begin DUP-001 cleanup until REG-002 is fixed and the complete suite passes.

---

# Entry State

Expected repository state:

```text
V4 = FORMALLY CLOSED

V4.1-R0 = APPROVED

V4.1-R1 = NEXT

REG-002-CANDIDATE = OPEN
REG-002_R1_PRIORITY = FIRST_ACTION

REFRACTOR_GOAL = READABILITY_AND_MAINTAINABILITY
BEHAVIOR_CHANGE = FORBIDDEN
```

Expected tests:

```text
TOTAL=1402
PASS=1401
KNOWN_FAIL=1
KNOWN_FAIL_ID=REG-002-CANDIDATE
UNEXPECTED_FAIL=0
```

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/V4/V4_FINAL_CLOSURE_RESULT.md`
5. `docs/V4_1/V4_1_R0_MAINTAINABILITY_INVENTORY_AND_REFACTOR_PLAN_RESULT.md`
6. `docs/V4_1/V4_1_R0_CLOSURE_AND_VERSIONING_RESULT.md`
7. `output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json`
8. `output/v4_1_r0/V4_1_REFACTOR_PLAN.json`
9. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Repository artifacts are authoritative.

---

# Entry Gate

Run:

```text
git status
```

Expected:

```text
CLEAN
```

The R1 prompt itself may be the only untracked file.

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
TOTAL=1402
PASS=1401
FAIL=1

FAIL=
tests/test_v4_r14_manuals_and_final_baseline.py
DeterminismTests.test_baseline_matches_on_disk_artifact
```

If any unexpected failure exists:

STOP.

Run readiness:

```text
python -m legacy_documenter.knowledge.readiness
```

Require:

```text
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

---

# Global V4.1 Invariants

Preserve:

```text
REFRACTOR_GOAL=READABILITY_AND_MAINTAINABILITY

BEHAVIOR_CHANGE=FORBIDDEN

V4_CONTRACT_CHANGE=FORBIDDEN

PLUGIN_RUNTIME_IMPLEMENTATION=FORBIDDEN

V5_IMPLEMENTATION=FORBIDDEN
```

No semantic redesign is authorized.

---

# BLOCK A — REG-002

## Accepted Diagnosis

`REG-002-CANDIDATE` is a stale-snapshot test defect.

The affected test compares:

```text
frozen historical V4_FINAL_BASELINE.json
```

against:

```text
live PROJECT_STATE.json
```

after R14 itself became approved.

The baseline artifact is historical and immutable.

The live project state is allowed to advance.

Therefore:

```text
FROZEN_HISTORICAL_ARTIFACT != MOVING_LIVE_PROJECT_STATE
```

must not be asserted as byte-identical after closure.

---

# REG-002 Allowed Change

Allowed:

```text
tests/test_v4_r14_manuals_and_final_baseline.py
```

Apply the smallest test-only correction that preserves the original intent:

```text
verify deterministic baseline generation
WITHOUT requiring a historical frozen snapshot
to equal future live repository state
```

Preferred strategy:

* compare deterministic builder output against the appropriate frozen inputs/state;
* or validate determinism independently of the advancing approval pointer;
* or explicitly normalize/exclude the expected moving state field if that is consistent with the test's original intent.

Do NOT modify the frozen R14 artifact to make the test pass.

Do NOT modify production behavior to satisfy the stale test.

Do NOT weaken the test into a meaningless existence check.

---

# REG-002 Required Proof

After the minimal test correction run:

```text
python -m unittest discover -s tests
```

Require:

```text
TOTAL>=1402
FAIL=0
```

Record:

```text
REG_002=FIXED
REG_002_CHANGE_TYPE=TEST_ONLY
REG_002_PRODUCTION_CHANGE=false
REG_002_FULL_SUITE_GREEN=true
```

If the suite is not fully green:

STOP.

Do NOT proceed to Block B.

---

# BLOCK B — DUP-001 / DEBT-001

Only after Block A passes.

R0 established with hard evidence:

```text
DUP-001=SAFE_TO_CONSOLIDATE
```

Pattern:

all eleven V4 knowledge `contract_report.py` modules use the same effective renderer:

```python
json.dumps(
    build_X(),
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
)
```

The goal is to remove duplicated deterministic JSON rendering while preserving every serialized byte.

---

# Scope Discovery

Use the approved R0 inventory to identify the exact eleven affected files.

Do not invent a list from memory.

Verify each current renderer body directly before editing.

If any renderer differs semantically from the R0 inventory:

STOP and report.

---

# Shared Helper Design

Create one small explicit helper in an appropriate shared package.

Requirements:

```text
single responsibility
standard library only
explicit type hints
clear docstring
no global state
no I/O
no domain semantics
no knowledge-status logic
no round-specific behavior
```

It should perform only canonical deterministic JSON serialization.

Conceptually:

```python
def render_deterministic_json(payload: Mapping[str, object]) -> str: ...
```

The exact name/type signature may be adjusted to fit repository conventions.

Do not create a generic utility dumping ground.

Do not create an abstraction framework.

Do not introduce dependency injection.

---

# Dependency Direction

The helper must live at a dependency level safely reusable by R7-R12 contract reporters.

It must not introduce:

```text
round package -> later round package
projection -> plugin_projection
plugin_projection -> projection
domain -> reporting
canonical -> projection
```

Prefer a neutral utility/reporting location already compatible with repository architecture.

Document the chosen location and why.

---

# Compatibility

Preserve all existing public functions:

```text
build_*_contract()
render_*_contract_json()
```

Do NOT remove them.

Do NOT rename them.

Do NOT change their import paths.

Each existing `render_*_contract_json()` should become a thin wrapper/delegator if appropriate.

Public compatibility required:

```text
IMPORT_PATHS_UNCHANGED=true
PUBLIC_FUNCTION_NAMES_UNCHANGED=true
```

---

# Byte Equivalence

This is the central invariant.

Before changing each renderer, capture its output.

After refactor compare:

```text
BEFORE_BYTES == AFTER_BYTES
```

for every affected contract reporter.

Require:

```text
CONTRACT_JSON_BYTE_EQUIVALENCE=PASS
```

All previously approved artifact hashes affected by these renderers must remain unchanged.

At minimum verify the approved R7-R12 contract/example artifacts relevant to these renderers.

Do not regenerate historical reviewed artifacts merely to prove equality.

Compare against existing hashes where possible.

---

# DUP-002 Boundary

Do NOT consolidate:

```text
build_*_contract()
```

R0 classified:

```text
DUP-002=SIMILAR_BUT_SEMANTICALLY_DISTINCT
```

That decision remains authoritative.

Only the serialization operation is shared.

---

# DUP-003 / DUP-004 Boundary

Do not touch:

```text
DUP-003
DUP-004
```

in R1.

No batch-parameter renames.

No package restructuring.

---

# Python Style

Follow:

```text
docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md
```

For new helper:

* clear snake_case module;
* concise explanatory module/class/function docstring;
* type hints;
* no unnecessary Python magic;
* no clever dynamic dispatch;
* no unnecessary class if a pure function is sufficient.

Prefer the simplest correct design.

---

# Tests

Add focused R1 tests.

Preferred file:

```text
tests/test_v4_1_r1_regression_and_json_renderer.py
```

Cover at minimum:

1. REG-002 no longer fails;
2. historical R14 baseline remains untouched;
3. deterministic helper produces exact expected separators;
4. UTF-8/non-ASCII behavior remains `ensure_ascii=False`;
5. keys remain sorted;
6. all eleven contract renderers use equivalent output;
7. before/after approved artifact hashes remain unchanged;
8. public renderer import paths remain valid;
9. `build_*_contract()` functions remain independent;
10. no R11/R12 dependency-direction regression;
11. no provider/LLM calls;
12. readiness remains READY.

Do not weaken existing tests.

---

# Behavioral Equivalence Artifact

Create:

```text
output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json
```

Include at minimum:

```text
round
reg_002

shared_renderer

affected_modules

public_api_preservation

byte_equivalence

approved_artifact_hashes

tests

readiness

production_behavior_changed
```

No timestamps.

No machine-specific absolute paths.

Generate deterministically.

Require:

```text
BEHAVIORAL_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS
```

---

# Full Regression

After all R1 changes run:

```text
python -m unittest discover -s tests
```

Require:

```text
FAIL=0
```

Expected total:

```text
>1402 PASS
```

No skip/removal/weakening.

Run readiness again.

Require:

```text
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

---

# Security / Contract Preservation

Require:

```text
V4_CONTRACTS_UNCHANGED=PASS

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0

PLUGIN_RUNTIME=NOT_IMPLEMENTED

V5_IMPLEMENTED=false
```

---

# Production Behavior

R1 may change implementation structure in the deterministic rendering layer.

Required:

```text
PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false
```

The REG-002 correction itself must remain:

```text
REG_002_PRODUCTION_CHANGE=false
```

---

# PROJECT_STATE

After successful implementation:

```text
latest_completed_round = V4.1-R1
latest_approved_round = V4.1-R0

current_round_in_progress =
"V4.1-R1 (pending Technical Lead review)"

round_status =
V4_1_R1_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R1

tests = <actual passing test count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

V4 remains formally closed.

Do not approve R1.

---

# Required Result

Create:

```text
docs/V4_1/V4_1_R1_REGRESSION_FIX_AND_SHARED_JSON_RENDERER_RESULT.md
```

Report at minimum:

```text
STATUS
ENTRY_GATE

BASELINE_TESTS_TOTAL
BASELINE_TESTS_PASS
BASELINE_KNOWN_FAIL

REG_002_REPRODUCED
REG_002_FIXED
REG_002_CHANGE_TYPE
REG_002_FULL_SUITE_GREEN_BEFORE_REFACTOR

SHARED_RENDERER_PATH
SHARED_RENDERER_DESIGN

AFFECTED_RENDERERS

DUP_001
DEBT_001

DUP_002_PRESERVED_DISTINCT
DUP_003_UNTOUCHED
DUP_004_UNTOUCHED

PUBLIC_IMPORT_PATHS_PRESERVED
PUBLIC_FUNCTION_NAMES_PRESERVED

CONTRACT_JSON_BYTE_EQUIVALENCE

APPROVED_ARTIFACT_HASHES_UNCHANGED

BEHAVIORAL_EQUIVALENCE_ARTIFACT
BEHAVIORAL_EQUIVALENCE_ARTIFACT_SHA256
BEHAVIORAL_EQUIVALENCE_ARTIFACT_DETERMINISM

FINAL_TESTS

V4_CONTRACTS_UNCHANGED

R11_BOUNDARY
R12_BOUNDARY

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
STATUS=V4_1_R1_IMPLEMENTATION_COMPLETE

ENTRY_GATE=PASS_WITH_ACCEPTED_REG_002

REG_002_REPRODUCED=PASS
REG_002_FIXED=PASS
REG_002_CHANGE_TYPE=TEST_ONLY
REG_002_FULL_SUITE_GREEN_BEFORE_REFACTOR=PASS

DUP_001=RESOLVED
DEBT_001=RESOLVED

DUP_002_PRESERVED_DISTINCT=PASS
DUP_003_UNTOUCHED=PASS
DUP_004_UNTOUCHED=PASS

PUBLIC_IMPORT_PATHS_PRESERVED=PASS
PUBLIC_FUNCTION_NAMES_PRESERVED=PASS

CONTRACT_JSON_BYTE_EQUIVALENCE=PASS

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

BEHAVIORAL_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS

FINAL_TESTS=>1402_PASS

V4_CONTRACTS_UNCHANGED=PASS

PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R1_READY_FOR_HUMAN_REVIEW

DECISION=V4_1_R1_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_1_R1
```

---

# Stop Condition

STOP after R1 implementation, tests, deterministic equivalence artifact, result document and PROJECT_STATE update.

Do NOT:

* approve R1;
* commit;
* push;
* start R2;
* modify DUP-002;
* modify DUP-003;
* modify DUP-004;
* begin high-risk module decomposition;
* change V4 contracts;
* begin V5;
* implement Plugin runtime.
