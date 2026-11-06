# LegacyMapper V4.1 — R5 Risky Orchestrators Characterization

TASK=V4_1_R5_RISKY_ORCHESTRATORS_CHARACTERIZATION

MODE=CHARACTERIZATION_ONLY

PRODUCTION_REFACTOR_ALLOWED=false
PRODUCTION_BEHAVIOR_CHANGE_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

Characterize the behavior and internal responsibility boundaries of the two
high-risk orchestrators identified by the approved V4.1-R0 maintainability plan:

legacy_documenter/extractors/database_extractor.py

legacy_documenter/analysis/flow_resolver.py

R5 MUST NOT refactor or structurally modify either production module.

The purpose of R5 is to create sufficient behavioral evidence for a later
V4.1-R6 extraction decision.

Primary rule:

CHARACTERIZE_FIRST
REFACTOR_LATER

Required invariant:

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
10. docs/V4_1/V4_1_R4_CLOSURE_AND_VERSIONING_RESULT.md
11. output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
12. output/v4_1_r0/V4_1_REFACTOR_PLAN.json
13. legacy_documenter/extractors/database_extractor.py
14. legacy_documenter/analysis/flow_resolver.py
15. all tests, fixtures and callers related to those modules.

Repository artifacts are authoritative.

Resolve the exact R0 characterization requirements and risk classifications
from the repository.

Do not reconstruct them from conversation memory.

---

# Entry Gate

Require semantically:

V4 = FORMALLY CLOSED

V4.1-R0 = APPROVED
V4.1-R1 = APPROVED
V4.1-R2 = APPROVED
V4.1-R3 = APPROVED
V4.1-R4 = APPROVED

latest_approved_round = V4.1-R4
next = V4.1-R5

tests >= 1486
readiness = READY

provider_calls = 0
real_llm_calls = 0

Run:

git status

Expected clean except this R5 prompt.

Run:

python -m unittest discover -s tests

Require:

>=1486 PASS
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

# R5 Is Characterization Only

Production modification of either target is forbidden.

Do NOT:

- rename functions;
- move functions;
- extract helpers;
- split classes;
- add adapters;
- change signatures;
- add production aliases;
- add production type hints solely for readability;
- change exception handling;
- change ordering;
- change output shapes;
- change parsing semantics;
- change graph/path semantics;
- change Oracle/database extraction semantics.

Allowed changes are limited to:

- tests;
- fixtures;
- deterministic characterization tooling;
- R5 documentation;
- R5 output artifact;
- PROJECT_STATE pending-review update.

If production code must change to make a test possible:

STOP and report the limitation.

---

# Target A — DatabaseExtractor

Target:

legacy_documenter/extractors/database_extractor.py

R0 classified this module as requiring design review before extraction.

Characterize the live implementation before making any architectural proposal.

Record at minimum:

- class/function inventory;
- public methods;
- private methods;
- constructor inputs/state;
- callers;
- call graph;
- responsibility groups;
- input file/source types;
- SQL/Oracle-related parsing behavior;
- string/token/regex parsing rules;
- normalization rules;
- object/model creation;
- ordering;
- deduplication;
- identifier generation;
- unresolved/unknown handling;
- malformed-input handling;
- exception behavior;
- filesystem access;
- global/module state;
- mutation of instance state;
- cross-method coupling;
- hidden temporal ordering assumptions;
- side effects;
- deterministic behavior;
- external dependency boundaries.

Do not infer database semantics not proven by code/tests.

---

# DatabaseExtractor Responsibility Map

Create a map with:

symbol
responsibility
inputs
outputs
reads_state
writes_state
side_effects
callers
callee_dependencies
ordering_dependency
shared_internal_state
compatibility_risk
possible_future_destination
safe_extraction_confidence

`possible_future_destination` is advisory only.

No production module may be created in R5.

---

# Target B — FunctionalFlowResolver

Target:

legacy_documenter/analysis/flow_resolver.py

Characterize at minimum:

- class/function inventory;
- public/private methods;
- constructor/state;
- graph inputs;
- graph outputs;
- path resolution behavior;
- traversal direction;
- traversal order;
- cycle handling;
- visited-state behavior;
- recursion/iteration behavior;
- depth/boundary rules;
- unresolved boundaries;
- duplicate handling;
- deterministic ordering;
- node/edge assumptions;
- mutation;
- filtering;
- flow/path construction;
- identifiers;
- exception behavior;
- empty graph/input behavior;
- malformed/incomplete graph behavior;
- cross-method state coupling;
- callers and downstream consumers.

Do not change graph semantics.

---

# FunctionalFlowResolver Responsibility Map

Create the same map:

symbol
responsibility
inputs
outputs
reads_state
writes_state
side_effects
callers
callee_dependencies
ordering_dependency
shared_internal_state
compatibility_risk
possible_future_destination
safe_extraction_confidence

Again, future destinations are proposals only.

No R6 extraction is authorized.

---

# Characterization Strategy

Prefer tests against public/significant behavior.

Use private-method characterization only where necessary to freeze a critical
behavioral rule that cannot otherwise be observed.

Do not write tests that merely mirror implementation line-by-line.

Tests should capture observable contracts and high-risk invariants.

---

# DatabaseExtractor Characterization Tests

Preferred file:

tests/test_v4_1_r5_database_extractor_characterization.py

Cover representative existing behaviors supported by repository evidence.

At minimum evaluate and test where applicable:

1. public construction/import;
2. public signatures;
3. representative extraction input;
4. empty input;
5. malformed/incomplete input;
6. database-object classification;
7. normalization;
8. deduplication;
9. deterministic ordering;
10. deterministic identifiers;
11. repeated-run equivalence;
12. exception behavior;
13. unresolved/unknown constructs;
14. instance-state behavior;
15. no network/provider calls.

If a category does not exist in current behavior:

record NOT_APPLICABLE with evidence.

Do not invent behavior for test completeness.

---

# FunctionalFlowResolver Characterization Tests

Preferred file:

tests/test_v4_1_r5_flow_resolver_characterization.py

Cover where supported:

1. public construction/import;
2. public signatures;
3. simple linear flow;
4. branching flow;
5. convergence;
6. duplicate edges/nodes;
7. cycles;
8. unresolved targets;
9. unresolved sources;
10. empty graph;
11. isolated node;
12. repeated traversal;
13. deterministic path ordering;
14. deterministic flow ordering;
15. depth/boundary behavior;
16. state reset/reuse behavior;
17. malformed or incomplete data;
18. representative exception behavior.

Again:

NOT_APPLICABLE is preferable to invented behavior.

---

# Golden Fixtures

Where existing fixtures are sufficient, reuse them.

Create new fixtures only when they represent a minimal deterministic behavioral
case that cannot be expressed clearly inline.

Do not copy large legacy repositories into tests.

Prefer minimal synthetic examples grounded in actual accepted input structures.

No timestamps.
No random identifiers.
No machine-specific paths.

---

# State-Reuse Characterization

Both targets are large stateful-looking modules.

Explicitly determine whether instances may safely be reused.

For each target classify:

STATE_MODEL=
STATELESS
STATEFUL_RESET_PER_OPERATION
STATEFUL_REUSABLE
STATEFUL_SINGLE_USE
UNCLEAR

Test repeated calls where repository behavior permits.

Do not alter state-reset logic.

---

# Ordering Characterization

Determine whether ordering is:

SEMANTIC
DETERMINISTIC_BUT_NOT_SEMANTIC
INCIDENTAL
UNCLEAR

for major outputs.

If current tests rely on ordering, freeze it.

Do not sort outputs merely to make tests deterministic unless production
already guarantees that ordering.

---

# Exception Characterization

Create an exception map:

operation
input_condition
exception_type
message_or_pattern
source
currently_tested
newly_characterized

Do not normalize exceptions.

Do not wrap broad exceptions.

That belongs to later design review.

---

# Side Effect Characterization

Record:

filesystem_reads
filesystem_writes
network_access
provider_access
environment_access
global_state
mutable_instance_state

Require:

NEW_SIDE_EFFECTS_INTRODUCED=false

---

# Callers and Compatibility

Repository-wide identify every caller/importer of both targets.

Record:

caller_path
symbol_used
positional_or_keyword
public_or_internal
test_or_production
reflection_or_dynamic_access
patching_or_monkeypatching

This evidence will control R6 compatibility strategy.

Do not move symbols in R5.

---

# Extraction Candidate Classification

After characterization, classify logical responsibility groups only.

For each group:

responsibility
symbols
coupling
state_dependency
side_effect_dependency
public_contract_dependency
characterization_coverage
future_extraction_risk

Classification:

LOW
MEDIUM
HIGH
DO_NOT_EXTRACT_YET

This is analysis only.

---

# R6 Readiness Decision

For each target classify:

DATABASE_EXTRACTOR_R6_READINESS=
READY_FOR_CONTROLLED_EXTRACTION
PARTIALLY_READY
NOT_READY

FLOW_RESOLVER_R6_READINESS=
READY_FOR_CONTROLLED_EXTRACTION
PARTIALLY_READY
NOT_READY

This does NOT authorize R6.

If either is PARTIALLY_READY or NOT_READY, identify exactly what additional
characterization is missing.

Do not manipulate the decision to force R6 work.

---

# Remaining High-Risk Modules

Do not structurally modify:

legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py

R4 already handled readiness.py.

Require:

NON_TARGET_HIGH_RISK_MODULES_PRESERVED=PASS

---

# Debt Preservation

Preserve:

DEBT_002=RESOLVED
DEBT_003=RESOLVED
TD_005=PARTIALLY_RESOLVED

R5 does not resolve them further.

Do not begin TD-005 typing work.

---

# Approved Artifact Integrity

Verify at minimum:

output/v4_r14/V4_FINAL_BASELINE.json
output/v4_r14/V4_FINAL_MANIFEST.json
output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json
output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json
output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json
output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json

Require:

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

Do not regenerate frozen historical artifacts.

---

# R0 Frozen Inventory

No production code is authorized to change in R5.

Therefore require:

R0_FROZEN_INVENTORY_MODIFIED=false

and a live maintainability reconstruction must not change because of R5
production structure.

Do not alter frozen R0 artifacts.

---

# Characterization Artifact

Create:

output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json

Include at minimum:

round

targets

database_extractor:
  inventory
  callers
  responsibility_map
  state_model
  ordering_model
  exceptions
  side_effects
  behavior_cases
  extraction_candidates
  r6_readiness

flow_resolver:
  inventory
  callers
  responsibility_map
  state_model
  ordering_model
  exceptions
  side_effects
  behavior_cases
  extraction_candidates
  r6_readiness

coverage_summary

approved_artifact_integrity
non_target_high_risk_modules_preserved

tests
readiness

production_code_changed
production_behavior_changed

No timestamps.
No absolute machine-specific paths.

Generate twice independently.

Require:

ORCHESTRATOR_CHARACTERIZATION_ARTIFACT_DETERMINISM=PASS

---

# Production Classification

Required:

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

If production code changes:

STOP.

R5 must not be submitted for approval until production modifications are reverted
without destructive Git operations.

---

# Full Regression

Run:

python -m unittest discover -s tests

Require:

>1486 PASS
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

# PROJECT_STATE

After successful R5 characterization:

latest_completed_round = V4.1-R5
latest_approved_round = V4.1-R4

current_round_in_progress =
"V4.1-R5 (pending Technical Lead review)"

round_status =
V4_1_R5_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R5

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0

V4 remains formally closed.

Do not approve R5.

---

# Required Result

Create:

docs/V4_1/V4_1_R5_RISKY_ORCHESTRATORS_CHARACTERIZATION_RESULT.md

Report at minimum:

STATUS
ENTRY_GATE

BASELINE_TESTS
FINAL_TESTS

R5_MODE

TARGETS

DATABASE_EXTRACTOR_CHARACTERIZATION
DATABASE_EXTRACTOR_PUBLIC_SURFACE
DATABASE_EXTRACTOR_CALLERS
DATABASE_EXTRACTOR_RESPONSIBILITY_MAP
DATABASE_EXTRACTOR_STATE_MODEL
DATABASE_EXTRACTOR_ORDERING_MODEL
DATABASE_EXTRACTOR_EXCEPTION_MAP
DATABASE_EXTRACTOR_SIDE_EFFECTS
DATABASE_EXTRACTOR_BEHAVIOR_CASES
DATABASE_EXTRACTOR_EXTRACTION_CANDIDATES
DATABASE_EXTRACTOR_R6_READINESS

FLOW_RESOLVER_CHARACTERIZATION
FLOW_RESOLVER_PUBLIC_SURFACE
FLOW_RESOLVER_CALLERS
FLOW_RESOLVER_RESPONSIBILITY_MAP
FLOW_RESOLVER_STATE_MODEL
FLOW_RESOLVER_ORDERING_MODEL
FLOW_RESOLVER_EXCEPTION_MAP
FLOW_RESOLVER_SIDE_EFFECTS
FLOW_RESOLVER_BEHAVIOR_CASES
FLOW_RESOLVER_EXTRACTION_CANDIDATES
FLOW_RESOLVER_R6_READINESS

CHARACTERIZATION_GAPS

NON_TARGET_HIGH_RISK_MODULES_PRESERVED

DEBT_002_STATUS
DEBT_003_STATUS
TD_005_STATUS

APPROVED_ARTIFACT_HASHES_UNCHANGED
R0_FROZEN_INVENTORY_MODIFIED

ORCHESTRATOR_CHARACTERIZATION_ARTIFACT
ORCHESTRATOR_CHARACTERIZATION_ARTIFACT_SHA256
ORCHESTRATOR_CHARACTERIZATION_ARTIFACT_DETERMINISM

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

# Expected Success State

STATUS=V4_1_R5_CHARACTERIZATION_COMPLETE

ENTRY_GATE=PASS

R5_MODE=CHARACTERIZATION_ONLY

FINAL_TESTS=>1486_PASS
FAIL=0
SKIP=0

NON_TARGET_HIGH_RISK_MODULES_PRESERVED=PASS

DEBT_002_STATUS=RESOLVED
DEBT_003_STATUS=RESOLVED
TD_005_STATUS=PARTIALLY_RESOLVED

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
R0_FROZEN_INVENTORY_MODIFIED=false

ORCHESTRATOR_CHARACTERIZATION_ARTIFACT_DETERMINISM=PASS

V4_CONTRACTS_UNCHANGED=PASS
R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R5_READY_FOR_HUMAN_REVIEW

DECISION=V4_1_R5_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_1_R5

---

# Important Outcome Rule

These are all valid outcomes:

DATABASE_EXTRACTOR_R6_READINESS=READY_FOR_CONTROLLED_EXTRACTION
DATABASE_EXTRACTOR_R6_READINESS=PARTIALLY_READY
DATABASE_EXTRACTOR_R6_READINESS=NOT_READY

FLOW_RESOLVER_R6_READINESS=READY_FOR_CONTROLLED_EXTRACTION
FLOW_RESOLVER_R6_READINESS=PARTIALLY_READY
FLOW_RESOLVER_R6_READINESS=NOT_READY

R5 success is determined by quality of characterization, not by whether R6 is
authorized.

Do not force a READY result.

---

# Git Safety

Do not commit or push.

Do not use:

git reset --hard
git clean
git restore .
git checkout -- .
git rebase
git amend
git squash
git push --force

---

# Final Stop

STOP after:

1. characterization tests;
2. full regression;
3. deterministic characterization artifact;
4. result document;
5. PROJECT_STATE pending Technical Lead review.

Do NOT:

- approve R5;
- commit;
- push;
- begin R6;
- refactor DatabaseExtractor;
- refactor FunctionalFlowResolver;
- modify resume.py;
- modify deep_source.py;
- continue TD-005 typing work;
- rename copilot_pilot.py;
- restructure context/;
- change V4 contracts;
- begin V5;
- implement Plugin runtime.