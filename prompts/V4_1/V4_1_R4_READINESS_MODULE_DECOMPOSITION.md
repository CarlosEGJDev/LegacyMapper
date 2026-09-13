# LegacyMapper V4.1 — R4 Readiness Module Decomposition

TASK=V4_1_R4_READINESS_MODULE_DECOMPOSITION

MODE=CHARACTERIZE_THEN_CONTROLLED_DECOMPOSITION

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

Improve readability and responsibility separation of:

legacy_documenter/knowledge/readiness.py

Primary debt:

DEBT-002

R0 classified this module as requiring additional characterization before safe extraction.

Therefore R4 has two mandatory sequential gates:

PHASE_A=CHARACTERIZATION
PHASE_B=CONTROLLED_DECOMPOSITION_IF_PROVEN_SAFE

Phase B is forbidden until Phase A passes.

Global invariant:

REFRACTOR_GOAL=READABILITY_AND_MAINTAINABILITY
BEHAVIOR_CHANGE=FORBIDDEN

---

# Repository Authority

Read in full:

1. CLAUDE.md
2. AGENTS.md
3. PROJECT_STATE.json
4. docs/V4/V4_FINAL_CLOSURE_RESULT.md
5. docs/V4_1/V4_1_R0_MAINTAINABILITY_INVENTORY_AND_REFACTOR_PLAN_RESULT.md
6. docs/V4_1/V4_1_R0_CLOSURE_AND_VERSIONING_RESULT.md
7. docs/V4_1/V4_1_R1_CLOSURE_AND_VERSIONING_RESULT.md
8. docs/V4_1/V4_1_R2_CLOSURE_AND_VERSIONING_RESULT.md
9. docs/V4_1/V4_1_R3_CLOSURE_AND_VERSIONING_RESULT.md
10. output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
11. output/v4_1_r0/V4_1_REFACTOR_PLAN.json
12. docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md
13. legacy_documenter/knowledge/readiness.py
14. all tests directly or indirectly covering readiness behavior.

Repository artifacts are authoritative.

Resolve the exact R0 definition of DEBT-002 from repository artifacts.

Do not reconstruct it from conversation memory.

---

# Entry Gate

Require semantically:

V4 = FORMALLY CLOSED

V4.1-R0 = APPROVED
V4.1-R1 = APPROVED
V4.1-R2 = APPROVED
V4.1-R3 = APPROVED

latest_approved_round = V4.1-R3
next = V4.1-R4

tests >= 1468
readiness = READY

provider_calls = 0
real_llm_calls = 0

Run:

git status

Expected clean except this R4 prompt.

Run:

python -m unittest discover -s tests

Require:

>=1468 PASS
FAIL=0
SKIP=0

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
PROVIDER_CALLS=0
REAL_LLM_CALLS=0

If any entry gate fails:

STOP.

---

# Global Invariants

Preserve:

BEHAVIOR_CHANGE=FORBIDDEN

V4_CONTRACT_CHANGE=FORBIDDEN
READINESS_SEMANTICS_CHANGE=FORBIDDEN
READINESS_OUTPUT_CHANGE=FORBIDDEN
PUBLIC_API_BREAK=FORBIDDEN
SERIALIZED_CONTRACT_CHANGE=FORBIDDEN

PLUGIN_RUNTIME_IMPLEMENTATION=FORBIDDEN
V5_IMPLEMENTATION=FORBIDDEN

No provider or real LLM call is authorized.

---

# Phase A — Mandatory Characterization

Before modifying production code, characterize readiness.py.

Record at minimum:

- public functions/classes/constants;
- private functions;
- importers/callers;
- CLI/module-entry behavior;
- filesystem reads;
- filesystem writes;
- environment dependencies;
- PROJECT_STATE dependencies;
- approved-artifact dependencies;
- ordering dependencies;
- hash/integrity checks;
- exception behavior;
- exit behavior;
- stdout/stderr behavior;
- deterministic output shape;
- global/module state;
- monkeypatch-sensitive symbols;
- tests patching names directly from readiness.py;
- tests depending on import location;
- functions with multiple responsibilities;
- candidate responsibility groups.

Create an explicit responsibility map:

symbol
responsibility
inputs
outputs
side_effects
callers
compatibility_risk
candidate_destination
safe_to_extract

Do not edit production code before this map exists.

---

# Characterization Tests

Add focused characterization tests before decomposition.

Preferred file:

tests/test_v4_1_r4_readiness_characterization.py

Capture existing behavior, not desired behavior.

Cover at minimum:

1. public imports;
2. public signatures;
3. representative READY result;
4. representative non-ready result if supported by current tests/fixtures;
5. ai_knowledge_allowed semantics;
6. ai_knowledge_generated semantics;
7. provider_calls and real_llm_calls reporting;
8. deterministic ordering;
9. output/serialization shape;
10. exception behavior;
11. CLI/module invocation behavior where applicable;
12. filesystem interactions;
13. monkeypatch-sensitive module symbols;
14. PROJECT_STATE interaction;
15. no real provider/LLM calls.

Do not modify readiness behavior to make characterization tests easier.

After adding characterization tests run the full suite.

Require:

CHARACTERIZATION_TESTS=PASS
FULL_SUITE_AFTER_CHARACTERIZATION=>1468_PASS
FAIL=0
SKIP=0

Only then evaluate Phase B.

---

# Phase A Decision Gate

Classify:

READINESS_DECOMPOSITION_DECISION=
SAFE_FOR_CONTROLLED_EXTRACTION
CHARACTERIZED_BUT_DEFER
BLOCKED

Phase B is allowed only for:

SAFE_FOR_CONTROLLED_EXTRACTION

If CHARACTERIZED_BUT_DEFER or BLOCKED:

- do not modify readiness.py structurally;
- preserve characterization tests;
- create the result/equivalence artifact;
- classify DEBT-002 honestly;
- stop for Technical Lead review.

A characterization-only R4 is an acceptable outcome.

Do not force decomposition merely because the round is named "decomposition".

---

# Phase B — Controlled Decomposition

Only execute if Phase A proves extraction safe.

The goal is not to make readiness.py artificially tiny.

The goal is to make responsibilities understandable.

Prefer small cohesive helpers/modules with explicit names.

Potential responsibility groups must come from Phase A evidence, not from this prompt.

Examples of categories that MAY exist:

- state loading;
- artifact/integrity verification;
- readiness evaluation;
- report/result composition;
- CLI rendering.

These are examples only.

Do not create them unless actual code supports those boundaries.

---

# Compatibility Facade

The existing public module:

legacy_documenter.knowledge.readiness

must remain the compatibility facade.

Existing public imports must continue resolving.

Existing external callers must not need changes.

Require:

READINESS_PUBLIC_IMPORTS_PRESERVED=PASS
READINESS_PUBLIC_SIGNATURES_PRESERVED=PASS

If a function is moved internally, re-export/wrap only where required for compatibility.

Avoid wrappers when no compatibility need exists.

---

# Monkeypatch Compatibility

This is especially important.

Before moving any imported dependency or function, search tests for patterns such as:

patch("legacy_documenter.knowledge.readiness...")
monkeypatch.setattr(readiness, ...)
direct assignment to readiness module symbols

Moving a dependency behind another module can silently break these tests and downstream users even when runtime output looks identical.

For each affected patchable symbol classify:

PATCH_LOCATION_PRESERVED
COMPATIBILITY_FORWARDING_REQUIRED
SAFE_TO_MOVE
DEFER

Require:

MONKEYPATCH_COMPATIBILITY=PASS

Do not solve this with broad dynamic __getattr__ magic.

Prefer explicit compatibility.

---

# Side-Effect Boundaries

Do not hide filesystem/provider/global-state behavior behind generic utility modules.

Any extracted helper with side effects must have an explicit responsibility.

Pure deterministic logic should be separated from I/O only when Phase A demonstrates that the separation is behaviorally equivalent.

No new global mutable state.

No caching unless already present.

---

# Naming and Structure

Follow:

docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md

Use:

- PascalCase for classes;
- snake_case modules/functions;
- one primary significant class per file where useful;
- explicit type hints at public/service boundaries;
- concise docstrings for significant functions/classes;
- comments for non-obvious deterministic/security/evidence rules.

Do not introduce C#-style ceremony into Python.

Do not create interfaces, factories, DI containers, managers, or abstractions without a concrete need.

---

# Scope Fence

R4 may modify only what is necessary for readiness decomposition and its tests/artifacts.

Do not structurally refactor:

legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py
legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py

Do not perform the deferred:

copilot_pilot.py rename
legacy_documenter/context/ rename/restructure

Do not continue broad TD-005 typing work.

Preserve:

TD_005=PARTIALLY_RESOLVED
DEBT_003=RESOLVED

---

# Behavioral Equivalence

Capture representative readiness results before Phase B.

After Phase B compare them.

Require:

READINESS_RESULT_EQUIVALENCE=PASS
READINESS_SERIALIZATION_EQUIVALENCE=PASS
READINESS_ORDERING_EQUIVALENCE=PASS
READINESS_EXCEPTION_EQUIVALENCE=PASS
READINESS_CLI_EQUIVALENCE=PASS

where each category is applicable to existing behavior.

Do not manufacture an equivalence category for behavior that does not exist; report NOT_APPLICABLE with evidence.

---

# Approved Artifact Integrity

Recompute relevant frozen hashes.

At minimum verify:

output/v4_r14/V4_FINAL_BASELINE.json
output/v4_r14/V4_FINAL_MANIFEST.json
output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json
output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json
output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json

Require:

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

Do not regenerate historical artifacts.

---

# R0 Maintainability Snapshot

If legitimate module/file/function counts change because of authorized R4 extraction, update only the durable R0 comparison logic needed to account for those explicitly authorized changes.

Do not modify the frozen R0 inventory.

Require:

R0_FROZEN_INVENTORY_MODIFIED=false

Do not weaken the comparison into a generic permissive check.

---

# Readiness Equivalence Artifact

Create:

output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json

Include at minimum:

round
debt_002

phase_a
characterization

responsibility_map

decomposition_decision

production_files_before
production_files_after

public_symbols
public_signatures

monkeypatch_compatibility

side_effect_boundaries

behavior_equivalence

serialization_equivalence
ordering_equivalence
exception_equivalence
cli_equivalence

approved_artifact_integrity

r0_frozen_inventory_modified

tests
readiness

production_code_changed
production_behavior_changed

No timestamps.
No absolute machine-specific paths.

Generate twice independently.

Require:

READINESS_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS

---

# DEBT-002 Disposition

At the end classify honestly:

DEBT_002_STATUS=
RESOLVED
PARTIALLY_RESOLVED
DEFERRED
BLOCKED

RESOLVED is allowed only if the exact R0-defined debt has actually been eliminated while preserving compatibility and behavior.

If only safe portions are extracted:

PARTIALLY_RESOLVED

If characterization shows extraction should wait:

DEFERRED

Do not force RESOLVED.

---

# Full Regression

Run:

python -m unittest discover -s tests

Require:

>1468 PASS
FAIL=0
SKIP=0

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

---

# V4 Preservation

Require:

V4_CONTRACTS_UNCHANGED=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0

PLUGIN_RUNTIME=NOT_IMPLEMENTED

V5_IMPLEMENTED=false

---

# Production Classification

If Phase B executes successfully, expected:

PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false

If R4 stops after characterization:

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

Tests/docs/artifacts do not count as production behavior changes.

---

# PROJECT_STATE

After successful R4 execution:

latest_completed_round = V4.1-R4
latest_approved_round = V4.1-R3

current_round_in_progress =
"V4.1-R4 (pending Technical Lead review)"

round_status =
V4_1_R4_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R4

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0

V4 remains formally closed.

Do not approve R4.

---

# Required Result

Create:

docs/V4_1/V4_1_R4_READINESS_MODULE_DECOMPOSITION_RESULT.md

Report at minimum:

STATUS
ENTRY_GATE

BASELINE_TESTS
CHARACTERIZATION_TESTS
TESTS_AFTER_CHARACTERIZATION
FINAL_TESTS

DEBT_002_ORIGINAL_DESCRIPTION
DEBT_002_STATUS

PHASE_A
READINESS_RESPONSIBILITY_MAP
READINESS_PUBLIC_SYMBOLS
READINESS_PUBLIC_SIGNATURES
READINESS_CALLERS
READINESS_SIDE_EFFECTS
READINESS_PATCH_POINTS

READINESS_DECOMPOSITION_DECISION
PHASE_B_EXECUTED

PRODUCTION_FILES_ADDED
PRODUCTION_FILES_MODIFIED

EXTRACTIONS_PERFORMED
RESPONSIBILITIES_REMAINING_IN_FACADE

READINESS_PUBLIC_IMPORTS_PRESERVED
READINESS_PUBLIC_SIGNATURES_PRESERVED
MONKEYPATCH_COMPATIBILITY

READINESS_RESULT_EQUIVALENCE
READINESS_SERIALIZATION_EQUIVALENCE
READINESS_ORDERING_EQUIVALENCE
READINESS_EXCEPTION_EQUIVALENCE
READINESS_CLI_EQUIVALENCE

APPROVED_ARTIFACT_HASHES_UNCHANGED
R0_FROZEN_INVENTORY_MODIFIED

READINESS_EQUIVALENCE_ARTIFACT
READINESS_EQUIVALENCE_ARTIFACT_SHA256
READINESS_EQUIVALENCE_ARTIFACT_DETERMINISM

TD_005_STATUS
DEBT_003_STATUS

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

---

# Expected Successful Decomposition State

If Phase B is proven safe and executed:

STATUS=V4_1_R4_IMPLEMENTATION_COMPLETE

ENTRY_GATE=PASS

READINESS_DECOMPOSITION_DECISION=SAFE_FOR_CONTROLLED_EXTRACTION
PHASE_B_EXECUTED=true

FINAL_TESTS=>1468_PASS
FAIL=0
SKIP=0

READINESS_PUBLIC_IMPORTS_PRESERVED=PASS
READINESS_PUBLIC_SIGNATURES_PRESERVED=PASS
MONKEYPATCH_COMPATIBILITY=PASS

READINESS_RESULT_EQUIVALENCE=PASS
READINESS_SERIALIZATION_EQUIVALENCE=PASS
READINESS_ORDERING_EQUIVALENCE=PASS
READINESS_EXCEPTION_EQUIVALENCE=PASS
READINESS_CLI_EQUIVALENCE=PASS

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
R0_FROZEN_INVENTORY_MODIFIED=false

V4_CONTRACTS_UNCHANGED=PASS
R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R4_READY_FOR_HUMAN_REVIEW

DECISION=V4_1_R4_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_1_R4

---

# Acceptable Characterization-Only State

If Phase A proves decomposition should be deferred:

STATUS=V4_1_R4_CHARACTERIZATION_COMPLETE

ENTRY_GATE=PASS

READINESS_DECOMPOSITION_DECISION=CHARACTERIZED_BUT_DEFER
PHASE_B_EXECUTED=false

DEBT_002_STATUS=DEFERRED

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

FINAL_TESTS=>1468_PASS
FAIL=0
SKIP=0

READINESS=READY

PROJECT_STATE=V4_1_R4_READY_FOR_HUMAN_REVIEW

DECISION=V4_1_R4_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_1_R4

This is not a failed round.

---

# Stop Conditions

STOP Phase B if:

- public readiness import compatibility cannot be preserved;
- monkeypatch compatibility is ambiguous;
- output/ordering/serialization changes;
- exception or CLI behavior changes;
- an approved artifact hash changes;
- extraction requires changing readiness semantics;
- another high-risk module must be structurally modified;
- tests cannot remain fully green.

Record the evidence and defer rather than forcing decomposition.

---

# Final Stop

STOP after:

1. Phase A characterization;
2. Phase B only if proven safe;
3. focused tests;
4. full regression;
5. deterministic equivalence artifact;
6. result document;
7. PROJECT_STATE pending Technical Lead review.

Do NOT:

- approve R4;
- commit;
- push;
- begin R5;
- refactor DatabaseExtractor;
- refactor FunctionalFlowResolver;
- refactor resume.py;
- refactor deep_source.py;
- rename copilot_pilot.py;
- restructure context/;
- continue broad typing cleanup;
- begin V5;
- implement Plugin runtime.