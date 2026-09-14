# LegacyMapper V4.1 — R7 Exception Boundaries and Adapter Cleanup

TASK=V4_1_R7_EXCEPTION_BOUNDARIES_AND_ADAPTER_CLEANUP

MODE=CHARACTERIZE_THEN_NARROW_CLEANUP

BEHAVIOR_CHANGE=FORBIDDEN

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

R7 improves readability and maintainability of historical exception/adaptation
boundaries without changing runtime behavior.

The round is intentionally narrow.

Primary scope:

- historical documentation handlers;
- local adapters around deterministic/documentation workflows;
- broad exception boundaries that are already local and well-characterized;
- redundant adapter/handler boilerplate where behavior is provably identical.

R7 is NOT a provider-wide exception redesign.

Do not introduce a new generic exception framework.

Do not normalize historical exceptions unless characterization proves exact
equivalence.

Required invariant:

PRODUCTION_BEHAVIOR_CHANGED=false

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
11. docs/V4_1/V4_1_R5_CLOSURE_AND_VERSIONING_RESULT.md
12. docs/V4_1/V4_1_R6_CLOSURE_AND_VERSIONING_RESULT.md
13. output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
14. output/v4_1_r0/V4_1_REFACTOR_PLAN.json

Also inspect all live production modules identified by R0 under documentation,
adapter, handler, provider, and exception-boundary categories.

Repository artifacts are authoritative.

Recover the exact R0 R7 scope and all exception/adapter candidates from the
repository.

Do not reconstruct candidate lists from conversation memory.

---

# Entry Gate

Require:

V4 = FORMALLY CLOSED

V4.1-R0 through V4.1-R6 = APPROVED

latest_approved_round = V4.1-R6
next = V4.1-R7

tests >= 1561
readiness = READY

provider_calls = 0
real_llm_calls = 0

Run:

git status

Expected clean except this R7 prompt.

Run:

python -m unittest discover -s tests

Require:

>=1561 PASS
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

# Scope Recovery

Before changing production code, build an exact live inventory of:

- try/except blocks;
- broad `except Exception`;
- exception-to-result adapters;
- file/document read fallbacks;
- parsing fallbacks;
- historical documentation wrappers;
- compatibility handlers;
- error-to-warning conversions;
- adapter classes/functions;
- repeated local exception handling patterns.

For every candidate record:

path
symbol
exception_types
caught_scope
result_on_success
result_on_failure
side_effects
logging_or_reporting
ordering_dependency
caller_dependency
public_contract_dependency
provider_dependency
existing_test_coverage
r0_classification
r7_scope_classification

Allowed `r7_scope_classification`:

IN_SCOPE
OUT_OF_SCOPE_PROVIDER_BOUNDARY
OUT_OF_SCOPE_HIGH_RISK
OUT_OF_SCOPE_DIFFERENT_ROUND
NEEDS_CHARACTERIZATION

Do not edit production code before this inventory is complete.

---

# Provider Boundary Fence

Broad provider/LLM boundaries remain excluded from cleanup unless the repository
already contains a provider-specific exception taxonomy with characterization
tests proving behavior.

Specifically:

Do not replace broad provider exceptions merely because they appear stylistically
undesirable.

Do not create:

- generic ProviderException;
- generic LLMException;
- generic AdapterException;
- global exception middleware;
- shared retry framework;
- cross-provider exception normalization.

Provider-specific exception behavior requires its own contract evidence.

If provider boundaries are found, record them as:

OUT_OF_SCOPE_PROVIDER_BOUNDARY

and preserve them unchanged.

---

# Historical Documentation Focus

Prioritize historical documentation modules and deterministic adapters.

Inspect especially the live documentation-related modules identified by R0,
but do not assume every module is safe.

For each candidate determine whether the current handler:

- catches expected I/O/parsing failure;
- suppresses malformed historical input intentionally;
- converts exceptions into structured errors;
- converts exceptions into empty/default results;
- preserves partial progress;
- affects deterministic ordering;
- is relied on by existing tests;
- is part of a public/imported API;
- hides provenance that later logic expects.

Characterize before cleanup.

---

# High-Risk Fence

Do not structurally refactor:

legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py
legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py

R7 may inspect their exception boundaries for classification evidence only.

No production edits to those files unless the approved R0 R7 scope explicitly
names a tiny isolated handler and characterization independently proves it safe.

Default action for these files:

DEFER.

---

# R6 Preservation Fence

Do not modify R6's deferred groups:

DatabaseExtractor:
- variable/type-state tracking;
- operation-detection-and-emission;
- parameter-extraction-and-normalization;
- extract() orchestration.

FunctionalFlowResolver:
- indexing;
- path identity/construction;
- confidence/status derivation;
- _walk;
- resolve() orchestration.

Do not touch:

_path_id
_path_identities
_add_path
_call_ref
_stable_id

Require:

R6_DEFERRED_GROUPS_PRESERVED=PASS

---

# Characterization Before Cleanup

For every IN_SCOPE production candidate, characterize:

1. exact exception type(s);
2. exact success output;
3. exact failure output;
4. whether exception propagates or is swallowed;
5. error/warning record shape;
6. message preservation;
7. ordering;
8. partial-result behavior;
9. filesystem side effects;
10. repeated-call determinism;
11. caller-visible behavior.

Add focused characterization tests before production edits.

Prefer observable public behavior.

Use private-function tests only where required to freeze an otherwise invisible
compatibility contract.

---

# Exception Map

Create an exception map with:

path
symbol
operation
input_condition
exception_type
message_or_pattern
propagates
converted_to
partial_result_preserved
side_effects
caller_visible
existing_test
new_characterization_test
cleanup_candidate

No speculative exception types.

Record only what live code/evidence supports.

---

# Cleanup Authorization

After characterization classify every IN_SCOPE candidate:

SAFE_LOCAL_CLEANUP
CHARACTERIZED_BUT_DEFER
DO_NOT_CHANGE

Only `SAFE_LOCAL_CLEANUP` may be modified.

Authorization is per candidate, not per file.

---

# Allowed Cleanup Shapes

Allowed only when behavior is byte/value equivalent:

- extract repeated local helper logic;
- name a previously inline deterministic handler;
- reduce duplicated exception-to-structured-result code;
- clarify adapter boundaries;
- replace duplicated tiny local patterns with one internal helper;
- improve local variable/function naming where compatibility permits;
- add concise type hints/docstrings around newly extracted helpers;
- remove dead local duplication proven unreachable/unused;
- simplify nesting without changing caught exception scope.

Prefer small internal helpers/modules.

Keep public module/class/function paths unchanged.

---

# Forbidden Cleanup Shapes

Do not:

- broaden or narrow caught exception types without explicit evidence;
- replace specific catches with `Exception`;
- replace broad catches with guessed specific exceptions;
- change exception messages;
- change return shapes;
- introduce new error codes;
- change logging/reporting semantics;
- add retries;
- add fallback behavior;
- remove intentionally swallowed errors;
- turn swallowed errors into raised errors;
- turn raised errors into swallowed errors;
- reorder deterministic error records;
- redesign provider boundaries;
- introduce global exception abstractions.

---

# Compatibility

For every modified production symbol require:

PUBLIC_IMPORT_COMPATIBILITY=PASS
PUBLIC_SIGNATURE_COMPATIBILITY=PASS
RETURN_VALUE_EQUIVALENCE=PASS
EXCEPTION_EQUIVALENCE=PASS
ORDERING_EQUIVALENCE=PASS

Where a symbol is private but tests/importers rely on its original location,
preserve the callable compatibility point.

No dynamic `__getattr__`.
No broad `**kwargs` compatibility shims.

---

# Adapter Cleanup

If duplicated adapter behavior is identified, determine whether instances are:

SEMANTICALLY_IDENTICAL
SIMILAR_BUT_DOMAIN_SPECIFIC
DIFFERENT

Only `SEMANTICALLY_IDENTICAL` may be consolidated.

Do not merge adapters merely because their code looks similar.

Preserve domain-specific naming when it carries meaning.

---

# New Internal Modules

Creating a small internal module is allowed only when:

- at least two in-scope handlers truly share identical semantics;
- extraction makes the exception boundary clearer;
- public compatibility remains unchanged;
- no provider boundary is crossed;
- tests characterize pre/post behavior.

Use descriptive `snake_case` filenames.

Avoid generic names such as:

helpers.py
utils.py
common.py
manager.py

unless repository conventions already justify them.

---

# Python Development Standard

Apply the approved LegacyMapper Python style:

- idiomatic Python first;
- classes PascalCase;
- modules snake_case;
- one significant responsibility per module where it improves clarity;
- explicit type hints at service/public boundaries;
- concise explanatory docstrings;
- comments for non-obvious compatibility/security/evidence rules;
- no unnecessary magic;
- no trivial getter/setter ceremony;
- no pattern proliferation;
- no unnecessary dependency injection.

A C# developer should be able to follow the code without the code becoming
non-idiomatic Python.

---

# Tests

Preferred files, adapting names to the actual candidate modules:

tests/test_v4_1_r7_exception_boundaries_characterization.py
tests/test_v4_1_r7_adapter_cleanup_equivalence.py

Do not create artificial tests for out-of-scope provider boundaries.

Characterize them in the artifact instead.

After characterization and before cleanup run the focused tests.

After every production cleanup run focused tests again.

---

# Behavioral Equivalence

Capture deterministic pre-change outputs for every modified candidate.

After cleanup require exact equivalence where possible.

Report:

EXCEPTION_TYPE_EQUIVALENCE
EXCEPTION_MESSAGE_EQUIVALENCE
FAILURE_RESULT_EQUIVALENCE
SUCCESS_RESULT_EQUIVALENCE
ORDERING_EQUIVALENCE
SIDE_EFFECT_EQUIVALENCE
PARTIAL_RESULT_EQUIVALENCE

Use:

PASS
NOT_APPLICABLE

Do not use approximate semantic equivalence where exact comparison is possible.

---

# Provider Boundary Report

Even though provider boundaries are out of scope, R7 must record them.

Create a table:

path
symbol
current_catch
provider
existing_taxonomy
existing_contract_tests
reason_deferred

Require:

PROVIDER_BOUNDARY_PRODUCTION_CHANGES=0

This evidence may inform a later dedicated round.

---

# Production Change Gate

Production cleanup may execute only if at least one candidate is:

SAFE_LOCAL_CLEANUP

If no candidate qualifies:

R7_CLEANUP_GATE=NO_SAFE_CANDIDATES

Do not force a refactor.

A characterization-only R7 remains valid.

If candidates qualify:

R7_CLEANUP_GATE=OPEN

Modify only authorized candidates.

---

# Scope Fence

Do not:

- continue TD-005 broadly;
- refactor resume.py;
- refactor deep_source.py;
- refactor DatabaseExtractor core;
- refactor FunctionalFlowResolver core;
- alter R6 compatibility delegates;
- modify provider runtime behavior;
- rename copilot_pilot.py;
- restructure legacy_documenter/context/;
- begin R8;
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
output/v4_1_r6/V4_1_R6_EXTRACTION_EQUIVALENCE.json

Require:

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

Do not regenerate historical artifacts.

---

# R0 Frozen Inventory

Do not modify:

output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
output/v4_1_r0/V4_1_REFACTOR_PLAN.json

Require:

R0_FROZEN_INVENTORY_MODIFIED=false

If authorized R7 cleanup legitimately changes live structural metrics, update
only durable comparison logic following the established R4/R6 precedent.

Do not weaken unrelated assertions.

---

# R7 Evidence Artifact

Create:

output/v4_1_r7/V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json

Include at minimum:

round

entry_gate

inventory:
  exception_boundaries
  adapters
  provider_boundaries
  high_risk_boundaries

candidates:
  in_scope
  out_of_scope_provider
  out_of_scope_high_risk
  needs_characterization

characterization:
  exception_map
  behavior_contracts
  tests_added

cleanup_gate

authorized_cleanups
deferred_cleanups
cleanups_performed

compatibility:
  public_imports
  public_signatures
  success_results
  failure_results
  exception_types
  exception_messages
  ordering
  side_effects
  partial_results

provider_boundary_changes

r6_deferred_groups_preserved

production_files_added
production_files_modified

approved_artifact_integrity
r0_frozen_inventory_modified

tests
readiness

production_code_changed
production_behavior_changed

No timestamps.
No machine-specific absolute paths.

Generate twice independently.

Require:

R7_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS

---

# Production Classification

If no cleanup is authorized:

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

If safe cleanup occurs:

PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false

Behavior change is forbidden in all cases.

---

# Full Regression

Run:

python -m unittest discover -s tests

Require:

>1561 PASS
FAIL=0
SKIP=0

No test may be removed, skipped, or weakened.

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

After successful R7 execution:

latest_completed_round = V4.1-R7
latest_approved_round = V4.1-R6

current_round_in_progress =
"V4.1-R7 (pending Technical Lead review)"

round_status =
V4_1_R7_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R7

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0

V4 remains formally closed.

Do not approve R7.

---

# Required Result

Create:

docs/V4_1/V4_1_R7_EXCEPTION_BOUNDARIES_AND_ADAPTER_CLEANUP_RESULT.md

Report at minimum:

STATUS
ENTRY_GATE

BASELINE_TESTS
FINAL_TESTS

R7_MODE

EXCEPTION_BOUNDARY_INVENTORY
ADAPTER_INVENTORY
PROVIDER_BOUNDARY_INVENTORY

IN_SCOPE_CANDIDATES
OUT_OF_SCOPE_PROVIDER_BOUNDARIES
OUT_OF_SCOPE_HIGH_RISK
NEEDS_CHARACTERIZATION

CHARACTERIZATION_TESTS

EXCEPTION_MAP

SAFE_LOCAL_CLEANUPS
CHARACTERIZED_BUT_DEFERRED
DO_NOT_CHANGE

R7_CLEANUP_GATE

AUTHORIZED_CLEANUPS
DEFERRED_CLEANUPS
CLEANUPS_PERFORMED

PRODUCTION_FILES_ADDED
PRODUCTION_FILES_MODIFIED

PUBLIC_IMPORT_COMPATIBILITY
PUBLIC_SIGNATURE_COMPATIBILITY

SUCCESS_RESULT_EQUIVALENCE
FAILURE_RESULT_EQUIVALENCE
EXCEPTION_TYPE_EQUIVALENCE
EXCEPTION_MESSAGE_EQUIVALENCE
ORDERING_EQUIVALENCE
SIDE_EFFECT_EQUIVALENCE
PARTIAL_RESULT_EQUIVALENCE

PROVIDER_BOUNDARY_PRODUCTION_CHANGES

R6_DEFERRED_GROUPS_PRESERVED

APPROVED_ARTIFACT_HASHES_UNCHANGED
R0_FROZEN_INVENTORY_MODIFIED

R7_EQUIVALENCE_ARTIFACT
R7_EQUIVALENCE_ARTIFACT_SHA256
R7_EQUIVALENCE_ARTIFACT_DETERMINISM

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

# Acceptable Outcomes

Both are valid:

1. Characterization plus safe local cleanup:

STATUS=V4_1_R7_IMPLEMENTATION_COMPLETE
R7_CLEANUP_GATE=OPEN
CLEANUPS_PERFORMED=>0

or

2. Characterization-only because no candidate is sufficiently safe:

STATUS=V4_1_R7_CHARACTERIZATION_COMPLETE
R7_CLEANUP_GATE=NO_SAFE_CANDIDATES
CLEANUPS_PERFORMED=0

Do not force cleanup merely to satisfy the round title.

---

# Expected Success Invariants

ENTRY_GATE=PASS

FINAL_TESTS=>1561_PASS
FAIL=0
SKIP=0

PROVIDER_BOUNDARY_PRODUCTION_CHANGES=0

R6_DEFERRED_GROUPS_PRESERVED=PASS

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
R0_FROZEN_INVENTORY_MODIFIED=false

R7_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS

V4_CONTRACTS_UNCHANGED=PASS
R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R7_READY_FOR_HUMAN_REVIEW

DECISION=V4_1_R7_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_1_R7

---

# Stop Conditions

STOP production cleanup immediately if:

- exact exception behavior cannot be pinned;
- a candidate crosses a provider boundary;
- exception type changes;
- exception message changes;
- failure result changes;
- partial-result behavior changes;
- ordering changes;
- side effects change;
- a high-risk module must be structurally modified;
- R6 deferred groups must be touched;
- approved artifact hashes change;
- full regression does not remain green.

Defer instead of forcing cleanup.

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

1. exception/adapter inventory;
2. characterization tests;
3. cleanup authorization decision;
4. only safe local cleanups, if any;
5. focused equivalence verification;
6. full regression;
7. deterministic R7 artifact;
8. result document;
9. PROJECT_STATE pending Technical Lead review.

Do NOT:

- approve R7;
- commit;
- push;
- begin R8;
- refactor provider-wide boundaries;
- refactor high-risk modules;
- touch R6 deferred groups;
- continue TD-005 broadly;
- rename copilot_pilot.py;
- restructure context/;
- begin V5;
- implement Plugin runtime.