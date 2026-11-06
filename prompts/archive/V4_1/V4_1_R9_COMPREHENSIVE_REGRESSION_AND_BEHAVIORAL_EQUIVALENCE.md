# LegacyMapper V4.1 — R9 Comprehensive Regression and Behavioral Equivalence

TASK=V4_1_R9_COMPREHENSIVE_REGRESSION_AND_BEHAVIORAL_EQUIVALENCE

MODE=VERIFICATION_ONLY

BEHAVIOR_CHANGE=FORBIDDEN
PRODUCTION_IMPLEMENTATION_ALLOWED=false
REFACTOR_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

R9 is the comprehensive verification round for the complete V4.1
maintainability refactor.

R9 must demonstrate that the cumulative changes from V4.1-R1 through V4.1-R8
preserved the approved V4 behavior and contracts.

R9 is NOT a cleanup round.

R9 is NOT an opportunity to fix stylistic issues.

R9 is NOT V5.

No production refactor or redesign is authorized.

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
13. docs/V4_1/V4_1_R7_CLOSURE_AND_VERSIONING_RESULT.md
14. docs/V4_1/V4_1_R8_CLOSURE_AND_VERSIONING_RESULT.md

Also inspect all V4.1 equivalence/characterization artifacts.

Repository artifacts are authoritative.

Do not reconstruct historical decisions from conversation memory.

---

# Entry Gate

Require:

V4 = FORMALLY CLOSED

V4.1-R0 through V4.1-R8 = APPROVED

latest_completed_round = V4.1-R8
latest_approved_round = V4.1-R8
current_round_in_progress = null
next = V4.1-R9

tests >= 1566
readiness = READY

provider_calls = 0
real_llm_calls = 0

Run:

git status

Expected clean except this R9 prompt.

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

# Verification-Only Fence

Do not modify production code.

Do not:

- refactor;
- rename;
- move modules;
- extract helpers;
- add type hints to production code;
- add production docstrings;
- alter exception handling;
- change provider behavior;
- change deterministic algorithms;
- change output schemas;
- change identifiers;
- change ordering;
- change persistence behavior.

If R9 discovers a defect:

record it.

Do not silently repair it.

If the defect invalidates behavioral equivalence:

R9 must fail or become BLOCKED and recommend a corrective round.

---

# V4 Baseline Integrity

Verify the approved V4 baseline and manifest.

Expected SHA-256:

V4_FINAL_BASELINE =
d13e3807a12187b226ea55752ae0e9dccd2ad20c9dbe044360ffa48bca526d1e

V4_FINAL_MANIFEST =
be398240a31137e7dea25fcaa7b3cfe6580d2557f990f7da884d5775f5c40551

Require:

V4_BASELINE_INTEGRITY=PASS
V4_MANIFEST_INTEGRITY=PASS

Do not regenerate either artifact.

---

# Historical V4.1 Artifact Integrity

Verify every approved V4.1 evidence artifact.

R1:
output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json

SHA256=
55c99c3b68ac159585c6a0ec7e05f74e8dd64dd871308d067ab27bdda1a1c33b

R2:
output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json

SHA256=
bd3daf04be868ef6465298c5e372aacc1f33bf234417f2bb914b79b22ab5a6f4

R3:
output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json

SHA256=
9e922d288b4f07812482baef1a5383276cd71f729e27cc67b47e54c30c5afecf

R4:
output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json

SHA256=
eb07e0f35540e0607b90f8ff707c7cac8e1f113419d338e3cc8579fa12f1e617

R5:
output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json

SHA256=
04c82d51b17664630adcafe26dd343d5f0740932904c77dd7a458029d547be32

R6:
output/v4_1_r6/V4_1_R6_EXTRACTION_EQUIVALENCE.json

SHA256=
bb60f1bd1b527003b2cbfdfcd98f13d77ca3cff246dc9b23c820da5378861ab1

R7:
output/v4_1_r7/V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json

SHA256=
ccb21db6b051b15b19c617dc387f28d7910386e634036f777b2a7eff374a5d4d

R8:
output/v4_1_r8/V4_1_R8_NAMING_DOCUMENTATION_EQUIVALENCE.json

SHA256=
1d1ffccbaf037b39442cc19dcd16ff4e00fd16cfb23d88e34ffccb98b9a51023

Require:

R1_ARTIFACT_INTEGRITY=PASS
R2_ARTIFACT_INTEGRITY=PASS
R3_ARTIFACT_INTEGRITY=PASS
R4_ARTIFACT_INTEGRITY=PASS
R5_ARTIFACT_INTEGRITY=PASS
R6_ARTIFACT_INTEGRITY=PASS
R7_ARTIFACT_INTEGRITY=PASS
R8_ARTIFACT_INTEGRITY=PASS

HISTORICAL_V4_1_ARTIFACT_INTEGRITY=PASS

Do not regenerate historical artifacts.

---

# R0 Frozen Evidence

Verify:

output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
output/v4_1_r0/V4_1_REFACTOR_PLAN.json

Require:

R0_FROZEN_INVENTORY_MODIFIED=false

R0 remains historical evidence.

Live code is expected to differ because of approved R1-R8 changes.

Do not rewrite R0.

---

# Cumulative Change Inventory

Build a deterministic cumulative inventory of all production changes made
during R1-R8.

For each round record:

round
production_files_added
production_files_modified
public_surface_changed
structural_change
documentation_only_change
typing_change
characterization_only
behavior_change_claim
equivalence_artifact
approved

This inventory must be derived from repository evidence.

Do not guess.

Require:

R1_R8_APPROVAL_CHAIN_COMPLETE=PASS

---

# Contract Verification Matrix

Verify cumulative preservation of:

1. public import paths;
2. public callable signatures;
3. positional-call compatibility;
4. keyword-call compatibility;
5. deterministic identifiers;
6. deterministic ordering;
7. serialized output structures;
8. exception behavior;
9. partial-result behavior;
10. state reuse/reset semantics;
11. readiness behavior;
12. canonical knowledge behavior;
13. R11 human projection boundary;
14. R12 Plugin projection boundary;
15. security invariants;
16. source-code optionality;
17. Technical Lead approval authority.

For each contract record:

contract
evidence
rounds_affecting
verification
status

Allowed status:

PASS
NOT_APPLICABLE

No UNKNOWN is acceptable for final READY.

---

# Determinism Verification

Re-run deterministic outputs where repository tooling supports safe local
generation without provider/LLM calls.

Verify at minimum:

- stable identifiers;
- ordering;
- readiness result;
- V4.1 evidence artifact generation where generation does not mutate historical
  approved artifacts;
- canonical knowledge deterministic behavior;
- R11 deterministic projection behavior;
- R12 deterministic Plugin projection behavior.

Never overwrite approved historical artifacts.

Use temporary paths when regeneration is required for comparison.

Require:

DETERMINISTIC_BEHAVIOR=PASS

---

# DatabaseExtractor Preservation

Verify R5/R6 characterization and R6 extraction boundaries remain intact.

Require:

DATABASE_EXTRACTOR_BEHAVIOR_EQUIVALENCE=PASS

DATABASE_EXTRACTOR_ORDERING_EQUIVALENCE=PASS

DATABASE_EXTRACTOR_EXCEPTION_EQUIVALENCE=PASS

DATABASE_EXTRACTOR_R6_DEFERRED_GROUPS_PRESERVED=PASS

Do not modify DatabaseExtractor.

---

# FunctionalFlowResolver Preservation

Require:

FLOW_RESOLVER_BEHAVIOR_EQUIVALENCE=PASS

FLOW_RESOLVER_ORDERING_EQUIVALENCE=PASS

FLOW_RESOLVER_IDENTIFIER_EQUIVALENCE=PASS

FLOW_RESOLVER_EXCEPTION_EQUIVALENCE=PASS

FLOW_RESOLVER_STATE_REUSE_EQUIVALENCE=PASS

FLOW_RESOLVER_R6_DEFERRED_GROUPS_PRESERVED=PASS

Verify that:

_path_id
_path_identities
_add_path
_call_ref
_stable_id

remain compatible with the R5/R6 characterization.

Do not modify them.

---

# R7 Exception Boundary Preservation

Require:

R7_EXCEPTION_BOUNDARIES_PRESERVED=PASS

PROVIDER_BOUNDARY_PRODUCTION_CHANGES=0

Verify `_extract_into` still preserves:

- Exception catch behavior;
- error record shape;
- message;
- ordering;
- partial-result behavior;
- extractor isolation.

Do not modify it.

---

# R8 Readability Preservation

Verify:

COPILOT_PILOT_RENAME=DEFERRED

CONTEXT_PACKAGE_STRUCTURE_UNCHANGED=PASS

TD_005_STATUS=PARTIALLY_RESOLVED

No attempt may be made in R9 to finish these items.

---

# Canonical Knowledge Verification

Verify the V4 canonical knowledge contracts remain unchanged.

Require:

ONE_CANONICAL_KNOWLEDGE_SOURCE=PASS

TECHNICAL_LEAD_FINAL_APPROVAL_AUTHORITY=PASS

SOURCE_CODE_OPTIONAL=PASS

PROVENANCE_PRESERVED=PASS

UNCERTAINTY_PRESERVED=PASS

AS_IS_TO_BE_HISTORICAL_SEMANTICS_PRESERVED=PASS

AI_INTERPRETATION_NOT_SELF_APPROVING=PASS

No canonical knowledge redesign is allowed.

---

# R11 Human Projection Verification

Require:

R11_BOUNDARY=PASS

Verify:

- R11 remains a deterministic human-readable projection;
- canonical statements remain projected without semantic rewriting;
- R11 is not the canonical source;
- R11 does not become Plugin input authority.

---

# R12 Plugin Projection Verification

Require:

R12_BOUNDARY=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0

Verify:

- R12 remains machine-facing projection;
- canonical source remains authoritative;
- Plugin IDs remain canonical KNO identifiers;
- Plugin runtime remains NOT_IMPLEMENTED.

---

# Security Verification

Verify:

SECURITY_GATE=PASS

At minimum check:

- no secret values introduced;
- no source-tree mutation;
- no unsafe path traversal regression;
- no provider calls;
- no real LLM calls;
- no hidden external network requirement introduced by V4.1.

Do not expose secret values in reports.

---

# V5 Boundary / Deferred Agnosticism

R9 must document, but NOT implement, the remaining V5 boundary.

Record that V5 is responsible for true runtime/domain agnosticism, including
at least:

- programming language agnosticism;
- framework agnosticism;
- project-layout agnosticism;
- architecture-pattern agnosticism;
- database/persistence-technology agnosticism where applicable;
- AI provider agnosticism;
- AI model agnosticism.

Important:

Do not redesign these concerns in R9.

Do not create new provider abstractions.

Do not rename or replace Copilot-specific components.

Do not modify extraction architecture for language/framework agnosticism.

The purpose of this section is to ensure the repository records the future V5
boundary explicitly.

Require:

V5_IMPLEMENTED=false
V5_AGNOSTICISM_BOUNDARY_DOCUMENTED=PASS

---

# Debt Verification

Preserve existing decisions:

DUP_001=RESOLVED
DEBT_001=RESOLVED
DEBT_002=RESOLVED
DEBT_003=RESOLVED

TD_005=PARTIALLY_RESOLVED

Recover all remaining R0/R1-R8 deferred debt from repository evidence.

Do not silently mark deferred items resolved.

Require:

DEBT_STATE_CONSISTENT=PASS

---

# Full Regression

Run:

python -m unittest discover -s tests

Require:

>=1566 PASS
FAIL=0
SKIP=0

No test may be:

- removed;
- skipped;
- weakened;
- rewritten merely to make R9 pass.

Additional verification tests may be added only if required to prove a missing
cross-round invariant.

Production code must remain untouched.

---

# Readiness

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

---

# Comprehensive R9 Artifact

Create:

output/v4_1_r9/V4_1_R9_COMPREHENSIVE_EQUIVALENCE.json

Include at minimum:

round

entry_gate

v4_baseline_integrity
v4_manifest_integrity

historical_artifact_integrity:
  r1
  r2
  r3
  r4
  r5
  r6
  r7
  r8

r0_frozen_inventory_modified

approval_chain

cumulative_change_inventory

contract_verification_matrix

determinism

database_extractor

flow_resolver

r7_exception_boundaries

r8_readability

canonical_knowledge

r11_boundary
r12_boundary

security

debt_state

v5_boundary:
  language_agnostic
  framework_agnostic
  project_layout_agnostic
  architecture_pattern_agnostic
  database_agnostic
  ai_provider_agnostic
  ai_model_agnostic
  implemented

tests
readiness

production_code_changed
production_behavior_changed

No timestamps.
No machine-specific absolute paths.

Generate twice independently.

Require:

R9_COMPREHENSIVE_ARTIFACT_DETERMINISM=PASS

---

# Production Classification

R9 itself must report:

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

If production code changes:

STOP.

R9 fails its scope.

---

# PROJECT_STATE

After successful R9 verification:

latest_completed_round = V4.1-R9
latest_approved_round = V4.1-R8

current_round_in_progress =
"V4.1-R9 (pending Technical Lead review)"

round_status =
V4_1_R9_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R9

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0

V4 remains formally closed.

Do not approve R9.

---

# Required Result

Create:

docs/V4_1/V4_1_R9_COMPREHENSIVE_REGRESSION_AND_BEHAVIORAL_EQUIVALENCE_RESULT.md

Report at minimum:

STATUS
ENTRY_GATE

BASELINE_TESTS
FINAL_TESTS

V4_BASELINE_INTEGRITY
V4_MANIFEST_INTEGRITY

R1_ARTIFACT_INTEGRITY
R2_ARTIFACT_INTEGRITY
R3_ARTIFACT_INTEGRITY
R4_ARTIFACT_INTEGRITY
R5_ARTIFACT_INTEGRITY
R6_ARTIFACT_INTEGRITY
R7_ARTIFACT_INTEGRITY
R8_ARTIFACT_INTEGRITY
HISTORICAL_V4_1_ARTIFACT_INTEGRITY

R0_FROZEN_INVENTORY_MODIFIED

R1_R8_APPROVAL_CHAIN_COMPLETE

CONTRACT_VERIFICATION_MATRIX

DETERMINISTIC_BEHAVIOR

DATABASE_EXTRACTOR_BEHAVIOR_EQUIVALENCE
DATABASE_EXTRACTOR_ORDERING_EQUIVALENCE
DATABASE_EXTRACTOR_EXCEPTION_EQUIVALENCE
DATABASE_EXTRACTOR_R6_DEFERRED_GROUPS_PRESERVED

FLOW_RESOLVER_BEHAVIOR_EQUIVALENCE
FLOW_RESOLVER_ORDERING_EQUIVALENCE
FLOW_RESOLVER_IDENTIFIER_EQUIVALENCE
FLOW_RESOLVER_EXCEPTION_EQUIVALENCE
FLOW_RESOLVER_STATE_REUSE_EQUIVALENCE
FLOW_RESOLVER_R6_DEFERRED_GROUPS_PRESERVED

R7_EXCEPTION_BOUNDARIES_PRESERVED
PROVIDER_BOUNDARY_PRODUCTION_CHANGES

COPILOT_PILOT_RENAME
CONTEXT_PACKAGE_STRUCTURE_UNCHANGED
TD_005_STATUS

ONE_CANONICAL_KNOWLEDGE_SOURCE
TECHNICAL_LEAD_FINAL_APPROVAL_AUTHORITY
SOURCE_CODE_OPTIONAL
PROVENANCE_PRESERVED
UNCERTAINTY_PRESERVED
AS_IS_TO_BE_HISTORICAL_SEMANTICS_PRESERVED
AI_INTERPRETATION_NOT_SELF_APPROVING

R11_BOUNDARY
R12_BOUNDARY

PLUGIN_CONTRACT_NAME
PLUGIN_CONTRACT_VERSION
PLUGIN_RUNTIME

SECURITY_GATE

DEBT_STATE_CONSISTENT

V5_IMPLEMENTED
V5_AGNOSTICISM_BOUNDARY_DOCUMENTED

R9_COMPREHENSIVE_ARTIFACT
R9_COMPREHENSIVE_ARTIFACT_SHA256
R9_COMPREHENSIVE_ARTIFACT_DETERMINISM

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

FINAL_TESTS=>=1566_PASS
FAIL=0
SKIP=0

V4_BASELINE_INTEGRITY=PASS
V4_MANIFEST_INTEGRITY=PASS

HISTORICAL_V4_1_ARTIFACT_INTEGRITY=PASS
R0_FROZEN_INVENTORY_MODIFIED=false

R1_R8_APPROVAL_CHAIN_COMPLETE=PASS

CONTRACT_VERIFICATION_MATRIX=PASS
DETERMINISTIC_BEHAVIOR=PASS

DATABASE_EXTRACTOR_BEHAVIOR_EQUIVALENCE=PASS
DATABASE_EXTRACTOR_ORDERING_EQUIVALENCE=PASS
DATABASE_EXTRACTOR_EXCEPTION_EQUIVALENCE=PASS
DATABASE_EXTRACTOR_R6_DEFERRED_GROUPS_PRESERVED=PASS

FLOW_RESOLVER_BEHAVIOR_EQUIVALENCE=PASS
FLOW_RESOLVER_ORDERING_EQUIVALENCE=PASS
FLOW_RESOLVER_IDENTIFIER_EQUIVALENCE=PASS
FLOW_RESOLVER_EXCEPTION_EQUIVALENCE=PASS
FLOW_RESOLVER_STATE_REUSE_EQUIVALENCE=PASS
FLOW_RESOLVER_R6_DEFERRED_GROUPS_PRESERVED=PASS

R7_EXCEPTION_BOUNDARIES_PRESERVED=PASS
PROVIDER_BOUNDARY_PRODUCTION_CHANGES=0

COPILOT_PILOT_RENAME=DEFERRED
CONTEXT_PACKAGE_STRUCTURE_UNCHANGED=PASS
TD_005_STATUS=PARTIALLY_RESOLVED

ONE_CANONICAL_KNOWLEDGE_SOURCE=PASS
TECHNICAL_LEAD_FINAL_APPROVAL_AUTHORITY=PASS
SOURCE_CODE_OPTIONAL=PASS
PROVENANCE_PRESERVED=PASS
UNCERTAINTY_PRESERVED=PASS
AS_IS_TO_BE_HISTORICAL_SEMANTICS_PRESERVED=PASS
AI_INTERPRETATION_NOT_SELF_APPROVING=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0
PLUGIN_RUNTIME=NOT_IMPLEMENTED

SECURITY_GATE=PASS

DEBT_STATE_CONSISTENT=PASS

V5_IMPLEMENTED=false
V5_AGNOSTICISM_BOUNDARY_DOCUMENTED=PASS

R9_COMPREHENSIVE_ARTIFACT_DETERMINISM=PASS

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R9_READY_FOR_HUMAN_REVIEW

DECISION=V4_1_R9_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_1_R9

---

# Stop Conditions

STOP and report failure/blocker if:

- an approved historical artifact hash changes;
- V4 baseline/manifest integrity fails;
- production code must change;
- a V4 contract cannot be verified;
- deterministic identifiers differ;
- deterministic ordering differs;
- serialized outputs differ;
- exception semantics differ;
- R11 or R12 boundaries differ;
- provider/LLM calls occur;
- security verification fails;
- regression suite fails.

Do not repair the issue inside R9.

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

1. comprehensive verification;
2. cumulative R1-R8 change inventory;
3. contract verification matrix;
4. deterministic verification;
5. full regression;
6. security verification;
7. V5 agnosticism boundary documentation;
8. deterministic R9 artifact;
9. result document;
10. PROJECT_STATE pending Technical Lead review.

Do NOT:

- approve R9;
- commit;
- push;
- begin R10;
- modify production code;
- refactor;
- implement V5;
- introduce provider abstractions;
- implement Plugin runtime.