# LegacyMapper V4.1 — R8 Naming and Documentation C#-friendly Part 2

TASK=V4_1_R8_NAMING_AND_DOCUMENTATION_PART_2

MODE=POST_CHARACTERIZATION_READABILITY_PASS

BEHAVIOR_CHANGE=FORBIDDEN

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

R8 performs a second controlled naming/documentation readability pass after
the characterization and structural work of R4-R7.

The goal is to make LegacyMapper easier to understand and maintain for a
C#-experienced developer without making the Python code non-idiomatic.

R8 may improve:

- ambiguous internal names;
- local variable names;
- internal helper names;
- module-level explanatory docstrings;
- function/class docstrings;
- comments around non-obvious deterministic/evidence/security behavior;
- safe type-hint gaps where semantics are already proven;
- readability of already-characterized low-risk code.

R8 must NOT become another structural-refactor round.

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
13. docs/V4_1/V4_1_R7_CLOSURE_AND_VERSIONING_RESULT.md
14. output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
15. output/v4_1_r0/V4_1_REFACTOR_PLAN.json

Repository artifacts are authoritative.

Recover the exact R0/R3 deferred naming/documentation candidates from the
repository.

Do not reconstruct candidate lists from conversation memory.

---

# Entry Gate

Require:

V4 = FORMALLY CLOSED

V4.1-R0 through V4.1-R7 = APPROVED

latest_approved_round = V4.1-R7
next = V4.1-R8

tests >= 1566
readiness = READY

provider_calls = 0
real_llm_calls = 0

Run:

git status

Expected clean except this R8 prompt.

Run:

python -m unittest discover -s tests

Require:

>=1566 PASS
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

# Candidate Recovery

Build a live candidate inventory covering:

- R0 naming candidates;
- R3 deferred candidates;
- R2 remaining safe documentation/type-readability candidates;
- modules changed during R4-R7 whose new internal structure may now need
  explanatory docstrings/comments;
- ambiguous internal names discovered by characterization.

For each candidate record:

path
symbol
current_name
candidate_name
public_or_private
runtime_imported
keyword_callers
reflection_or_dynamic_access
test_references
monkeypatch_dependency
serialized_name_dependency
compatibility_risk
documentation_gap
type_hint_gap
r8_classification

Allowed r8_classification:

SAFE_PRIVATE_RENAME
SAFE_LOCAL_RENAME
DOCUMENTATION_ONLY
SAFE_TYPE_HINT
CHARACTERIZED_BUT_DEFER
DO_NOT_CHANGE

Do not edit production code before the inventory is complete.

---

# Naming Rules

Prefer names that communicate responsibility explicitly.

Good:

classification_requests
proposal_requests
relation_requests
build_maintainability_inventory
extractor
source_path
target_records
error_records
entry_point_id
canonical_identity

Avoid vague names where context is non-obvious:

data
item
obj
thing
tmp
x
result
info
manager
handler

unless the scope makes the meaning already obvious.

Do not rename merely for stylistic preference.

A rename must improve comprehension materially.

---

# Public Compatibility

Public/imported symbols are protected by default.

Do not rename a public symbol unless:

- the new name is additive;
- the existing symbol remains available;
- call compatibility is preserved;
- import compatibility is preserved;
- no serialization contract depends on the name.

Prefer aliases/delegation only when the readability gain is meaningful.

Do not proliferate aliases.

If the old public name is already understandable:

leave it unchanged.

---

# Private Rename Safety

A private rename may occur only if all of the following are true:

- no dynamic access;
- no reflection dependency;
- no monkeypatch dependency;
- no string-based reference;
- no serialized contract dependency;
- all callers are statically discoverable;
- characterization is sufficient;
- full regression remains green.

If any is uncertain:

DEFER.

---

# R6/R7 Preservation Fence

Do not reopen structural decisions from R6/R7.

Do not structurally refactor:

legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py
legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py

Do not touch R6 deferred groups.

Do not touch:

_path_id
_path_identities
_add_path
_call_ref
_stable_id

Do not remove R6 compatibility delegates.

Do not alter `_extract_into` behavior from R7.

Require:

R6_DEFERRED_GROUPS_PRESERVED=PASS
R7_EXCEPTION_BOUNDARIES_PRESERVED=PASS

---

# copilot_pilot.py

R3 explicitly deferred renaming `copilot_pilot.py`.

R8 may re-evaluate it.

Do not rename it automatically.

Determine:

- import references;
- package exports;
- tests;
- documentation references;
- string/path references;
- provider bootstrap dependencies;
- external compatibility risk.

Classify:

SAFE_TO_RENAME
NOT_WORTH_RENAMING
DEFER

If SAFE_TO_RENAME still requires compatibility shims or broad changes:

prefer DEFER.

A file rename is not required for R8 success.

---

# context/ Package

R3 also deferred `legacy_documenter/context/`.

Inspect it for naming/documentation readability only.

Do NOT restructure the package in R8.

Allowed:

- docstrings;
- comments;
- private/local names;
- clear type hints.

Forbidden:

- moving modules;
- flattening package structure;
- changing import topology.

---

# Documentation Standard

Every significant public class/function/method should have a concise docstring
that explains:

- what it does;
- what key inputs mean;
- what it returns;
- important behavior constraints where non-obvious.

Do not write large tutorial-style docstrings.

For internal helpers, add a docstring only where responsibility or invariant
is non-obvious.

Comments should explain:

- deterministic ordering;
- compatibility reasons;
- evidence/provenance rules;
- security boundaries;
- intentionally preserved historical behavior;
- why a surprising branch/order cannot be changed.

Do not comment obvious syntax.

---

# C#-Friendly Readability

Use organization familiar to a C# developer where it remains idiomatic Python:

- explicit responsibility names;
- clear class boundaries;
- explicit return types where stable;
- limited hidden mutation;
- concise module/class/function documentation;
- predictable naming.

Do not introduce C# anti-patterns into Python:

- trivial property wrappers;
- interfaces without need;
- factory/service abstractions for every class;
- dependency injection frameworks;
- unnecessary DTO duplication;
- unnecessary `IWhatever` concepts.

Python remains Python.

---

# Type Hint Safety

R8 may close only safe, already-understood type-hint gaps.

Do not force annotations onto ambiguous nested historical JSON structures.

Preserve TD-005's unresolved semantic uncertainty.

Allowed:

- obvious scalar returns;
- stable list/dict container shapes already characterized;
- parameters whose runtime types are already constrained by callers/tests;
- internal helpers newly created in R4-R7 whose contracts are clear.

If a type requires `Any` merely to make the checker quiet:

prefer no new annotation unless the current design already uses that shape.

Do not claim TD-005 fully resolved unless every original gap is genuinely closed.

Expected default:

TD_005_STATUS=PARTIALLY_RESOLVED

---

# R4-R7 New Internal Modules

Inspect the internal modules introduced during R4-R7 for readability:

R4:
legacy_documenter/knowledge/_readiness_io.py
legacy_documenter/knowledge/_readiness_parsing.py
legacy_documenter/knowledge/_readiness_evidence.py

R6:
legacy_documenter/extractors/_database_line_scanner.py
legacy_documenter/extractors/_database_token_parsing.py
legacy_documenter/extractors/_database_classification.py
legacy_documenter/analysis/_flow_graph_construction.py
legacy_documenter/analysis/_flow_key_labels.py
legacy_documenter/analysis/_flow_report_composition.py

R7:
legacy_documenter/main.py::_extract_into

These are candidates for:

DOCUMENTATION_ONLY
SAFE_TYPE_HINT
SAFE_PRIVATE_RENAME

Do not restructure them.

---

# Rename Characterization

Before any rename, pin:

- import resolution;
- callable behavior;
- keyword-call behavior if relevant;
- exception behavior;
- result equality;
- test references;
- reflection/monkeypatch absence.

Add focused tests only when existing tests do not sufficiently protect the
rename.

Do not create noisy tests for trivial local-variable renames.

---

# Cleanup Authorization

After inventory classify candidates into:

SAFE_PRIVATE_RENAME
SAFE_LOCAL_RENAME
DOCUMENTATION_ONLY
SAFE_TYPE_HINT
CHARACTERIZED_BUT_DEFER
DO_NOT_CHANGE

Only the first four may be changed.

No quota.

Zero renames is acceptable if documentation/type improvements are the safer
choice.

Do not force change merely to make R8 look substantial.

---

# Compatibility Requirements

For changed callable symbols require as applicable:

PUBLIC_IMPORT_COMPATIBILITY=PASS
PUBLIC_SIGNATURE_COMPATIBILITY=PASS
POSITIONAL_CALL_COMPATIBILITY=PASS
KEYWORD_CALL_COMPATIBILITY=PASS
RETURN_VALUE_EQUIVALENCE=PASS
EXCEPTION_EQUIVALENCE=PASS
SERIALIZED_OUTPUT_EQUIVALENCE=PASS

For private/local-only changes use:

NOT_APPLICABLE

where appropriate.

---

# Forbidden Changes

Do not:

- structurally split more modules;
- move responsibilities;
- alter provider boundaries;
- rename serialized keys;
- rename JSON fields;
- rename Plugin contract fields;
- change public API contracts;
- change deterministic ordering;
- change exception behavior;
- change evidence/provenance semantics;
- begin R9 regression work early;
- begin V5;
- implement Plugin runtime.

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
output/v4_1_r7/V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json

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

If R8 changes only names/docstrings/type hints, structural metrics should remain
stable except for line counts/docstring metrics where expected.

Update durable comparison logic only when truly necessary and with explicit
before/after assertions.

Do not weaken unrelated checks.

---

# R8 Evidence Artifact

Create:

output/v4_1_r8/V4_1_R8_NAMING_DOCUMENTATION_EQUIVALENCE.json

Include at minimum:

round

entry_gate

candidate_inventory

changes:
  private_renames
  local_renames
  documentation_changes
  type_hint_changes
  deferred_candidates
  do_not_change

compatibility:
  public_imports
  public_signatures
  positional_calls
  keyword_calls
  return_values
  exceptions
  serialized_outputs

r6_deferred_groups_preserved
r7_exception_boundaries_preserved

copilot_pilot_decision
context_package_decision

td_005_status

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

Generate twice independently.

Require:

R8_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS

---

# Full Regression

Run:

python -m unittest discover -s tests

Require:

>1566 PASS
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

If documentation/type/name improvements touch production files:

PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false

If no production file requires change:

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

Behavior change is forbidden.

---

# PROJECT_STATE

After successful R8 execution:

latest_completed_round = V4.1-R8
latest_approved_round = V4.1-R7

current_round_in_progress =
"V4.1-R8 (pending Technical Lead review)"

round_status =
V4_1_R8_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R8

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0

V4 remains formally closed.

Do not approve R8.

---

# Required Result

Create:

docs/V4_1/V4_1_R8_NAMING_AND_DOCUMENTATION_PART_2_RESULT.md

Report at minimum:

STATUS
ENTRY_GATE

BASELINE_TESTS
FINAL_TESTS

R8_MODE

CANDIDATES_TOTAL

SAFE_PRIVATE_RENAMES
SAFE_LOCAL_RENAMES
DOCUMENTATION_ONLY_CHANGES
SAFE_TYPE_HINT_CHANGES

DEFERRED_CANDIDATES
DO_NOT_CHANGE_CANDIDATES

COPILOT_PILOT_DECISION
CONTEXT_PACKAGE_DECISION

PRODUCTION_FILES_ADDED
PRODUCTION_FILES_MODIFIED

PUBLIC_IMPORT_COMPATIBILITY
PUBLIC_SIGNATURE_COMPATIBILITY
POSITIONAL_CALL_COMPATIBILITY
KEYWORD_CALL_COMPATIBILITY
RETURN_VALUE_EQUIVALENCE
EXCEPTION_EQUIVALENCE
SERIALIZED_OUTPUT_EQUIVALENCE

R6_DEFERRED_GROUPS_PRESERVED
R7_EXCEPTION_BOUNDARIES_PRESERVED

TD_005_STATUS

APPROVED_ARTIFACT_HASHES_UNCHANGED
R0_FROZEN_INVENTORY_MODIFIED

R8_EQUIVALENCE_ARTIFACT
R8_EQUIVALENCE_ARTIFACT_SHA256
R8_EQUIVALENCE_ARTIFACT_DETERMINISM

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

# Expected Success Invariants

ENTRY_GATE=PASS

FINAL_TESTS=>1566_PASS
FAIL=0
SKIP=0

R6_DEFERRED_GROUPS_PRESERVED=PASS
R7_EXCEPTION_BOUNDARIES_PRESERVED=PASS

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
R0_FROZEN_INVENTORY_MODIFIED=false

R8_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS

V4_CONTRACTS_UNCHANGED=PASS
R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R8_READY_FOR_HUMAN_REVIEW

DECISION=V4_1_R8_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_1_R8

---

# Stop Conditions

STOP or DEFER a candidate if:

- public compatibility is uncertain;
- keyword callers exist and compatibility cannot be preserved;
- a monkeypatch or reflection dependency exists;
- a serialized name could change;
- the change crosses a provider boundary;
- an R6 deferred group must be touched;
- an R7 exception contract changes;
- exact result/exception equivalence fails;
- approved artifact hashes change;
- regression cannot remain green.

Prefer no rename over a risky rename.

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

1. candidate inventory;
2. safe naming/documentation/type changes;
3. compatibility verification;
4. full regression;
5. deterministic R8 artifact;
6. result document;
7. PROJECT_STATE pending Technical Lead review.

Do NOT:

- approve R8;
- commit;
- push;
- begin R9;
- structurally refactor modules;
- modify provider runtime behavior;
- reopen R6 deferred groups;
- alter R7 exception behavior;
- begin V5;
- implement Plugin runtime.