# LegacyMapper V4.1 — R6 Gap Closure and Controlled Extraction

TASK=V4_1_R6_GAP_CLOSURE_AND_CONTROLLED_EXTRACTION

MODE=TWO_GATE_CHARACTERIZATION_AND_EXTRACTION

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

BEHAVIOR_CHANGE=FORBIDDEN

---

# Objective

R6 has two mandatory sequential gates.

GATE_A=CHARACTERIZATION_GAP_CLOSURE
GATE_B=CONTROLLED_EXTRACTION_IF_AUTHORIZED

Gate B is forbidden until Gate A is fully complete.

Targets:

legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py

R5 closed with:

DATABASE_EXTRACTOR_R6_READINESS=PARTIALLY_READY
FLOW_RESOLVER_R6_READINESS=PARTIALLY_READY

R6 production extraction was explicitly NOT preauthorized.

---

# Repository Authority

Read in full:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/V4/V4_FINAL_CLOSURE_RESULT.md

docs/V4_1/V4_1_R0_CLOSURE_AND_VERSIONING_RESULT.md
docs/V4_1/V4_1_R1_CLOSURE_AND_VERSIONING_RESULT.md
docs/V4_1/V4_1_R2_CLOSURE_AND_VERSIONING_RESULT.md
docs/V4_1/V4_1_R3_CLOSURE_AND_VERSIONING_RESULT.md
docs/V4_1/V4_1_R4_CLOSURE_AND_VERSIONING_RESULT.md
docs/V4_1/V4_1_R5_CLOSURE_AND_VERSIONING_RESULT.md

docs/V4_1/V4_1_R5_RISKY_ORCHESTRATORS_CHARACTERIZATION_RESULT.md

output/v4_1_r0/V4_1_REFACTOR_PLAN.json
output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json

legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py

all tests and fixtures relevant to both targets.

Repository artifacts are authoritative.

Do not reconstruct R5 gaps from conversation memory.

---

# Entry Gate

Require:

V4 = FORMALLY CLOSED

V4.1-R0 through V4.1-R5 = APPROVED

latest_approved_round = V4.1-R5
next = V4.1-R6

tests >= 1536
readiness = READY

provider_calls = 0
real_llm_calls = 0

Run:

git status

Expected clean except this R6 prompt.

Run:

python -m unittest discover -s tests

Require:

>=1536 PASS
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
SERIALIZED_CONTRACT_CHANGE=FORBIDDEN
PUBLIC_API_BREAK=FORBIDDEN

DATABASE_EXTRACTION_SEMANTICS_CHANGE=FORBIDDEN
FLOW_TRAVERSAL_SEMANTICS_CHANGE=FORBIDDEN

PLUGIN_RUNTIME_IMPLEMENTATION=FORBIDDEN
V5_IMPLEMENTATION=FORBIDDEN

Do not modify production code during Gate A.

---

# GATE A — Mandatory Characterization Gap Closure

R5 recorded exactly 8 gaps.

All 8 must be addressed before Gate B may be evaluated.

Production-code edits are forbidden during Gate A.

Only tests, fixtures, deterministic analysis artifact updates and documentation
are allowed.

---

# DatabaseExtractor Gap 1

Characterize:

branch-order interaction between operation-detection regexes on the same physical/logical line.

Determine and test:

- whether multiple operation patterns may match the same line;
- which branch wins;
- whether `continue` statements suppress later matches;
- whether ordering is semantic;
- whether one physical line becoming multiple logical statements changes precedence;
- whether reordering branches would change output.

Create minimal deterministic tests.

Record:

DATABASE_GAP_1_STATUS=CLOSED or OPEN

---

# DatabaseExtractor Gap 2

Characterize `_split_args`.

Cover at minimum where current implementation supports them:

- nested parentheses;
- quoted commas;
- empty arguments;
- whitespace;
- escaped/doubled quotes if applicable;
- nested function expressions;
- parentheses inside quoted strings.

Do not improve parser behavior.

Freeze existing behavior exactly.

Record:

DATABASE_GAP_2_STATUS=CLOSED or OPEN

---

# DatabaseExtractor Gap 3

Characterize variable/type-state tracking independently from the entire extraction pipeline.

Determine:

- when a variable becomes known;
- how provider/command/adapter type information is stored;
- how later lines depend on prior declarations;
- whether reassignment alters classification;
- behavior for use-before-declaration;
- behavior for unknown type;
- scope lifetime.

Prefer focused tests around existing helpers/state transitions where possible.

Do not extract code yet.

Record:

DATABASE_GAP_3_STATUS=CLOSED or OPEN

---

# DatabaseExtractor Gap 4

Characterize multiple classes with repeated variable names.

At minimum establish behavior for:

ClassA:
  cmd

ClassB:
  cmd

Determine whether state is:

- class-scoped;
- file-scoped;
- overwritten;
- merged;
- accidentally shared.

Test repeated names with differing declared types when possible.

Do not fix surprising behavior.

Record it.

DATABASE_GAP_4_STATUS=CLOSED or OPEN

---

# FunctionalFlowResolver Gap 1

Pin `_stable_id` to exact deterministic known values.

Use minimal deterministic input strings already compatible with existing behavior.

Record exact expected values.

Require:

- same input -> exact same id;
- different canonical identity -> expected different id;
- cross-run stability.

Do not change hashing algorithm.

Record:

FLOW_GAP_1_STATUS=CLOSED or OPEN

---

# FunctionalFlowResolver Gap 2

Characterize two entry points sharing an overlapping call graph within one resolve() call.

Determine:

- graph/path cross-contamination;
- path identity separation;
- shared node reuse;
- flow ordering;
- per-entry-point isolation;
- global aggregation behavior.

Use a minimal synthetic graph.

Record:

FLOW_GAP_2_STATUS=CLOSED or OPEN

---

# FunctionalFlowResolver Gap 3

Characterize `_flow_status` precedence where cycle and truncated-depth conditions coexist.

R5 recorded the current precedence order as semantically significant.

Build a case in which the same flow can expose both properties, if current
architecture permits.

Pin the current result.

Do not alter precedence.

Record:

FLOW_GAP_3_STATUS=CLOSED or OPEN

If this combination is structurally impossible under current behavior:

record NOT_APPLICABLE with evidence sufficient to close the gap.

---

# FunctionalFlowResolver Gap 4

Characterize a method containing both:

- direct data-access operations;
- outgoing method calls

within the same `_walk` invocation.

Determine:

- emitted path(s);
- terminal/non-terminal behavior;
- ordering;
- whether both branches survive;
- flow status;
- data endpoint handling.

Do not change traversal.

Record:

FLOW_GAP_4_STATUS=CLOSED or OPEN

---

# Gate A Tests

Preferred files:

tests/test_v4_1_r6_database_extractor_gap_closure.py
tests/test_v4_1_r6_flow_resolver_gap_closure.py

Do not remove or weaken R5 characterization tests.

After completing the gap tests run:

python -m unittest discover -s tests

Require:

>1536 PASS
FAIL=0
SKIP=0

---

# Gate A Decision

Compute:

DATABASE_GAPS_CLOSED=<0..4>
FLOW_GAPS_CLOSED=<0..4>
TOTAL_GAPS_CLOSED=<0..8>

Gate B may be evaluated only if:

DATABASE_GAPS_CLOSED=4
FLOW_GAPS_CLOSED=4
TOTAL_GAPS_CLOSED=8

Otherwise:

R6_EXTRACTION_GATE=BLOCKED

Do not modify production code.

Create result/artifact and stop for Technical Lead review.

A characterization-only R6 is valid.

---

# Re-evaluate R6 Readiness

After closing all eight gaps, reclassify each target:

DATABASE_EXTRACTOR_R6_READINESS=
READY_FOR_LIMITED_EXTRACTION
PARTIALLY_READY
NOT_READY

FLOW_RESOLVER_R6_READINESS=
READY_FOR_LIMITED_EXTRACTION
PARTIALLY_READY
NOT_READY

Do not use READY merely because all gaps were closed.

Re-evaluate actual coupling and risk.

---

# GATE B — Controlled Extraction Authorization

Gate B may execute only if:

TOTAL_GAPS_CLOSED=8

and at least one responsibility group is independently classified:

LOW_RISK_AND_CHARACTERIZED

Do not authorize extraction for a whole class/module.

Authorization is per responsibility group.

For every candidate record:

target
responsibility
symbols
characterization_coverage
state_dependency
ordering_dependency
side_effect_dependency
public_contract_dependency
monkeypatch_dependency
extraction_risk
authorization

Allowed authorization:

AUTHORIZED
DEFERRED

---

# DatabaseExtractor Extraction Boundary

R5 identified likely LOW candidates:

- logical-line reassembly;
- string/token parsing;
- classification/normalization.

Re-evaluate each after Gate A.

Do not assume all three remain LOW.

The following remain forbidden unless Gate A evidence explicitly proves otherwise:

- variable/type-state core;
- operation-detection-and-emission core;
- extract() orchestration.

Prefer leaving the high-risk sequential scan intact.

---

# FunctionalFlowResolver Extraction Boundary

R5 identified likely LOW candidates:

- indexing;
- graph construction;
- key/label derivation;
- report composition.

Re-evaluate each after Gate A.

Do not assume all are authorized.

Do NOT extract `_walk` in R6 unless evidence unexpectedly proves it LOW risk,
which must be justified explicitly.

Path identity requires special protection because an existing test directly
patches:

resolver._path_id
resolver._path_identities

Any extraction involving path-identity symbols must preserve those patch points
exactly or be deferred.

Prefer deferral.

---

# Extraction Design Rules

For authorized groups only:

- use small cohesive internal modules;
- keep existing public classes/modules as compatibility facades;
- preserve existing public import paths;
- preserve method signatures;
- preserve return values;
- preserve exceptions;
- preserve ordering;
- preserve identifiers;
- preserve deterministic behavior;
- preserve monkeypatch locations where they are established behavior.

No dynamic `__getattr__`.
No broad `**kwargs` compatibility hacks.
No generic service/factory/manager abstractions without concrete need.
No dependency-injection framework.
No unnecessary C# ceremony.

Follow the approved LegacyMapper Python development style.

---

# DatabaseExtractor Compatibility

Existing production caller:

legacy_documenter/main.py

must require zero changes unless strictly internal import wiring requires one
and public behavior remains identical.

Prefer:

DatabaseExtractor.extract(...)

remaining unchanged.

Require:

DATABASE_EXTRACTOR_PUBLIC_IMPORTS_PRESERVED=PASS
DATABASE_EXTRACTOR_PUBLIC_SIGNATURES_PRESERVED=PASS

---

# FunctionalFlowResolver Compatibility

Preserve:

FunctionalFlowResolver(...)
FunctionalFlowResolver.resolve(...)

and all existing import paths.

Require:

FLOW_RESOLVER_PUBLIC_IMPORTS_PRESERVED=PASS
FLOW_RESOLVER_PUBLIC_SIGNATURES_PRESERVED=PASS

Require:

FLOW_RESOLVER_PATH_ID_PATCH_POINT_PRESERVED=PASS

if path-identity code is touched.

If it cannot be preserved simply:

DEFER that extraction.

---

# Behavioral Equivalence

Capture pre-extraction representative outputs after Gate A and before Gate B.

After each authorized extraction compare.

Require where applicable:

DATABASE_RESULT_EQUIVALENCE=PASS
DATABASE_ORDERING_EQUIVALENCE=PASS
DATABASE_IDENTIFIER_EQUIVALENCE=PASS
DATABASE_EXCEPTION_EQUIVALENCE=PASS

FLOW_RESULT_EQUIVALENCE=PASS
FLOW_ORDERING_EQUIVALENCE=PASS
FLOW_IDENTIFIER_EQUIVALENCE=PASS
FLOW_EXCEPTION_EQUIVALENCE=PASS
FLOW_STATE_REUSE_EQUIVALENCE=PASS

No "close enough" comparisons.

Use exact equality wherever existing deterministic structures permit it.

---

# Extraction Incrementality

Do not extract all authorized groups at once.

For each group:

1. establish pre-extraction tests/evidence;
2. perform one cohesive extraction;
3. run focused tests;
4. run relevant R5/R6 characterization tests;
5. verify compatibility;
6. continue only if green.

If an extraction fails after reasonable correction:

revert only that local uncommitted extraction using non-destructive manual edits
and mark the group DEFERRED.

Do not use destructive Git commands.

---

# Scope Fence

Do not structurally modify:

legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py

Do not:

- rename copilot_pilot.py;
- restructure legacy_documenter/context/;
- continue broad TD-005 typing work;
- redesign provider boundaries;
- perform R7 exception cleanup;
- begin V5;
- implement Plugin runtime.

Preserve:

DEBT_002=RESOLVED
DEBT_003=RESOLVED
TD_005=PARTIALLY_RESOLVED

---

# Approved Artifact Integrity

Verify:

output/v4_r14/V4_FINAL_BASELINE.json
output/v4_r14/V4_FINAL_MANIFEST.json
output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json
output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json
output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json
output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json
output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json

Require:

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

Do not regenerate historical artifacts.

---

# R0 Frozen Inventory

If Gate B changes production structure, the live reconstruction may legitimately
change.

Do not modify the frozen R0 inventory or plan.

Require:

R0_FROZEN_INVENTORY_MODIFIED=false

Update durable comparison tests only for explicitly authorized structural
changes.

Do not weaken them generically.

---

# R6 Equivalence Artifact

Create:

output/v4_1_r6/V4_1_R6_EXTRACTION_EQUIVALENCE.json

Include at minimum:

round

entry_gate

gate_a:
  database_gaps
  flow_gaps
  total_closed
  tests
  readiness_reassessment

gate_b:
  allowed
  candidate_groups
  authorized_groups
  deferred_groups
  extractions_performed

database_extractor:
  compatibility
  behavior_equivalence
  ordering_equivalence
  identifier_equivalence
  exception_equivalence

flow_resolver:
  compatibility
  patch_point_preservation
  behavior_equivalence
  ordering_equivalence
  identifier_equivalence
  exception_equivalence
  state_reuse_equivalence

production_files_added
production_files_modified

approved_artifact_integrity
r0_frozen_inventory_modified

tests
readiness

production_code_changed
production_behavior_changed

No timestamps.
No absolute machine paths.

Generate twice.

Require:

R6_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS

---

# Production Classification

If Gate A completes but Gate B remains blocked:

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

If one or more authorized groups are extracted:

PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false

Behavior change is never allowed.

---

# Full Regression

Run:

python -m unittest discover -s tests

Require:

>1536 PASS
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

After successful R6 execution:

latest_completed_round = V4.1-R6
latest_approved_round = V4.1-R5

current_round_in_progress =
"V4.1-R6 (pending Technical Lead review)"

round_status =
V4_1_R6_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R6

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0

V4 remains formally closed.

Do not approve R6.

---

# Required Result

Create:

docs/V4_1/V4_1_R6_GAP_CLOSURE_AND_CONTROLLED_EXTRACTION_RESULT.md

Report at minimum:

STATUS
ENTRY_GATE

BASELINE_TESTS
FINAL_TESTS

GATE_A_STATUS

DATABASE_GAP_1_STATUS
DATABASE_GAP_2_STATUS
DATABASE_GAP_3_STATUS
DATABASE_GAP_4_STATUS

FLOW_GAP_1_STATUS
FLOW_GAP_2_STATUS
FLOW_GAP_3_STATUS
FLOW_GAP_4_STATUS

DATABASE_GAPS_CLOSED
FLOW_GAPS_CLOSED
TOTAL_GAPS_CLOSED

DATABASE_EXTRACTOR_R6_READINESS
FLOW_RESOLVER_R6_READINESS

R6_EXTRACTION_GATE

GATE_B_EXECUTED

EXTRACTION_CANDIDATES
AUTHORIZED_EXTRACTIONS
DEFERRED_EXTRACTIONS
EXTRACTIONS_PERFORMED

PRODUCTION_FILES_ADDED
PRODUCTION_FILES_MODIFIED

DATABASE_EXTRACTOR_PUBLIC_IMPORTS_PRESERVED
DATABASE_EXTRACTOR_PUBLIC_SIGNATURES_PRESERVED

FLOW_RESOLVER_PUBLIC_IMPORTS_PRESERVED
FLOW_RESOLVER_PUBLIC_SIGNATURES_PRESERVED
FLOW_RESOLVER_PATH_ID_PATCH_POINT_PRESERVED

DATABASE_RESULT_EQUIVALENCE
DATABASE_ORDERING_EQUIVALENCE
DATABASE_IDENTIFIER_EQUIVALENCE
DATABASE_EXCEPTION_EQUIVALENCE

FLOW_RESULT_EQUIVALENCE
FLOW_ORDERING_EQUIVALENCE
FLOW_IDENTIFIER_EQUIVALENCE
FLOW_EXCEPTION_EQUIVALENCE
FLOW_STATE_REUSE_EQUIVALENCE

APPROVED_ARTIFACT_HASHES_UNCHANGED
R0_FROZEN_INVENTORY_MODIFIED

R6_EQUIVALENCE_ARTIFACT
R6_EQUIVALENCE_ARTIFACT_SHA256
R6_EQUIVALENCE_ARTIFACT_DETERMINISM

DEBT_002_STATUS
DEBT_003_STATUS
TD_005_STATUS

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

# Expected Gate-A Success

Require:

DATABASE_GAP_1_STATUS=CLOSED
DATABASE_GAP_2_STATUS=CLOSED
DATABASE_GAP_3_STATUS=CLOSED
DATABASE_GAP_4_STATUS=CLOSED

FLOW_GAP_1_STATUS=CLOSED
FLOW_GAP_2_STATUS=CLOSED
FLOW_GAP_3_STATUS=CLOSED
FLOW_GAP_4_STATUS=CLOSED

DATABASE_GAPS_CLOSED=4
FLOW_GAPS_CLOSED=4
TOTAL_GAPS_CLOSED=8

Only then may:

R6_EXTRACTION_GATE=OPEN

---

# Acceptable Gate-B Outcomes

Valid:

GATE_B_EXECUTED=true
with one or more narrow extractions

or:

GATE_B_EXECUTED=false
because no group remains sufficiently safe

Both are acceptable.

Do not force production refactoring.

---

# Expected Final State

STATUS=V4_1_R6_IMPLEMENTATION_COMPLETE

ENTRY_GATE=PASS

TOTAL_GAPS_CLOSED=8

PRODUCTION_BEHAVIOR_CHANGED=false

FINAL_TESTS=>1536_PASS
FAIL=0
SKIP=0

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
R0_FROZEN_INVENTORY_MODIFIED=false

R6_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS

V4_CONTRACTS_UNCHANGED=PASS
R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R6_READY_FOR_HUMAN_REVIEW

DECISION=V4_1_R6_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_1_R6

---

# Stop Conditions

STOP Gate B immediately if:

- any of the 8 gaps remains open;
- an extraction changes ordering;
- deterministic IDs change;
- exception behavior changes;
- DatabaseExtractor extraction alters sequential branch semantics;
- FunctionalFlowResolver extraction alters traversal semantics;
- `_path_id` compatibility is lost;
- public imports/signatures change;
- an approved artifact hash changes;
- another high-risk module must be touched;
- full regression cannot remain green.

Defer instead of forcing the extraction.

---

# Final Stop

STOP after:

1. all eight characterization gaps are evaluated;
2. Gate B is evaluated only if all eight close;
3. only authorized low-risk extractions are performed;
4. focused equivalence tests;
5. full regression;
6. deterministic R6 artifact;
7. result document;
8. PROJECT_STATE pending Technical Lead review.

Do NOT:

- approve R6;
- commit;
- push;
- begin R7;
- refactor resume.py;
- refactor deep_source.py;
- extract `_walk` without explicit evidence;
- redesign `_path_id`;
- continue TD-005 typing;
- rename copilot_pilot.py;
- restructure context/;
- begin V5;
- implement Plugin runtime.