# LegacyMapper V4.1 — R10 Final Baseline and Formal Closure

TASK=V4_1_R10_FINAL_BASELINE_AND_FORMAL_CLOSURE

MODE=FINAL_BASELINE_PREPARATION_AND_CLOSURE_REVIEW

PRODUCTION_IMPLEMENTATION_ALLOWED=false
REFACTOR_ALLOWED=false
BEHAVIOR_CHANGE=FORBIDDEN

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

R10 prepares the final V4.1 baseline and formal closure package.

V4.1-R0 through V4.1-R9 are already approved.

R10 must:

1. verify the complete approved V4.1 state;
2. construct a deterministic final V4.1 baseline;
3. construct a deterministic final V4.1 manifest;
4. record the final debt/deferred-work ledger;
5. record the V5 boundary;
6. verify repository continuity;
7. prepare V4.1 for Technical Lead final approval.

R10 must NOT:

- modify production code;
- refactor;
- resolve remaining debt;
- implement V5;
- introduce provider abstractions;
- implement Plugin runtime.

---

# Governing Invariant

REFRACTOR_GOAL=READABILITY_AND_MAINTAINABILITY
BEHAVIOR_CHANGE=FORBIDDEN

Require throughout:

PRODUCTION_BEHAVIOR_CHANGED=false

---

# Repository Authority

Read in full:

1. CLAUDE.md
2. AGENTS.md
3. PROJECT_STATE.json
4. docs/V4/V4_FINAL_CLOSURE_RESULT.md
5. docs/V4_1/V4_1_R0_CLOSURE_AND_VERSIONING_RESULT.md
6. docs/V4_1/V4_1_R1_CLOSURE_AND_VERSIONING_RESULT.md
7. docs/V4_1/V4_1_R2_CLOSURE_AND_VERSIONING_RESULT.md
8. docs/V4_1/V4_1_R3_CLOSURE_AND_VERSIONING_RESULT.md
9. docs/V4_1/V4_1_R4_CLOSURE_AND_VERSIONING_RESULT.md
10. docs/V4_1/V4_1_R5_CLOSURE_AND_VERSIONING_RESULT.md
11. docs/V4_1/V4_1_R6_CLOSURE_AND_VERSIONING_RESULT.md
12. docs/V4_1/V4_1_R7_CLOSURE_AND_VERSIONING_RESULT.md
13. docs/V4_1/V4_1_R8_CLOSURE_AND_VERSIONING_RESULT.md
14. docs/V4_1/V4_1_R9_CLOSURE_AND_VERSIONING_RESULT.md
15. output/v4_1_r9/V4_1_R9_COMPREHENSIVE_EQUIVALENCE.json

Repository artifacts are authoritative.

Do not depend on conversation memory.

---

# Entry Gate

Require:

V4 = FORMALLY CLOSED

V4.1-R0 through V4.1-R9 = APPROVED

latest_completed_round = V4.1-R9
latest_approved_round = V4.1-R9

current_round_in_progress = null
next = V4.1-R10

tests >= 1566
readiness = READY

provider_calls = 0
real_llm_calls = 0

Run:

git status

Expected clean except this R10 prompt.

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

# R9 Approval Verification

Require:

R9_VERIFICATION_DECISION=APPROVED

R9_COMPREHENSIVE_EQUIVALENCE_DECISION=APPROVED

R9 comprehensive artifact:

output/v4_1_r9/V4_1_R9_COMPREHENSIVE_EQUIVALENCE.json

Expected SHA256:

87f49a41712ac83f948378da4e56c0df54b8c3f1a02741013b1f4d1b87568f04

Recompute.

Require:

R9_COMPREHENSIVE_ARTIFACT_INTEGRITY=PASS

Do not regenerate R9.

---

# V4 Baseline Preservation

Verify:

output/v4_r14/V4_FINAL_BASELINE.json

SHA256=
d13e3807a12187b226ea55752ae0e9dccd2ad20c9dbe044360ffa48bca526d1e

output/v4_r14/V4_FINAL_MANIFEST.json

SHA256=
be398240a31137e7dea25fcaa7b3cfe6580d2557f990f7da884d5775f5c40551

Require:

V4_BASELINE_INTEGRITY=PASS
V4_MANIFEST_INTEGRITY=PASS

Do not modify or regenerate them.

---

# Historical V4.1 Artifact Preservation

Verify all approved V4.1 evidence artifacts R1-R9.

Require:

HISTORICAL_V4_1_ARTIFACT_INTEGRITY=PASS

R0_FROZEN_INVENTORY_MODIFIED=false

No historical approved artifact may be regenerated.

---

# Final V4.1 Baseline

Create:

output/v4_1_r10/V4_1_FINAL_BASELINE.json

This is the canonical final baseline for V4.1.

Include at minimum:

version = "V4.1"

status = "READY_FOR_TECHNICAL_LEAD_FINAL_APPROVAL"

v4_status

approved_rounds:
  r0
  r1
  r2
  r3
  r4
  r5
  r6
  r7
  r8
  r9

tests

readiness

behavior:
  refactor_goal
  behavior_change_forbidden
  production_behavior_changed

compatibility:
  public_imports
  public_signatures
  positional_calls
  keyword_calls
  deterministic_identifiers
  deterministic_ordering
  serialized_outputs
  exception_behavior
  partial_results
  state_reuse

canonical_knowledge:
  one_canonical_source
  technical_lead_authority
  source_code_optional
  provenance
  uncertainty
  temporal_semantics
  ai_interpretation_self_approval

r11
r12

plugin_contract:
  name
  version
  runtime_implemented

security

debt

v5_boundary

provider_calls
real_llm_calls

Do not include timestamps.
Do not include absolute machine paths.

---

# Final V4.1 Manifest

Create:

output/v4_1_r10/V4_1_FINAL_MANIFEST.json

The manifest must enumerate the approved V4.1 closure/evidence chain required
to reconstruct and verify V4.1 without conversation memory.

Include at minimum:

- R0 frozen inventory;
- R0 refactor plan;
- every R1-R9 approved evidence artifact;
- every R0-R9 closure result;
- final V4 baseline and manifest references;
- R9 comprehensive artifact;
- R10 final baseline;
- relevant authoritative project-state/recovery documents.

For each immutable artifact include:

path
sha256
role

Use repository-relative paths only.

The manifest must not claim mutable state documents are immutable unless their
role is explicitly identified as mutable/current-state metadata.

---

# Baseline/Manifest Determinism

Generate:

V4_1_FINAL_BASELINE.json

twice independently.

Require identical bytes/hash.

Generate:

V4_1_FINAL_MANIFEST.json

twice independently.

Require identical bytes/hash.

Record:

V4_1_FINAL_BASELINE_DETERMINISM=PASS
V4_1_FINAL_MANIFEST_DETERMINISM=PASS

---

# Final Behavioral State

Require:

CONTRACT_VERIFICATION_MATRIX=PASS

DETERMINISTIC_BEHAVIOR=PASS

PRODUCTION_BEHAVIOR_CHANGED=false

DATABASE_EXTRACTOR_BEHAVIOR_EQUIVALENCE=PASS

FLOW_RESOLVER_BEHAVIOR_EQUIVALENCE=PASS

R7_EXCEPTION_BOUNDARIES_PRESERVED=PASS

PROVIDER_BOUNDARY_PRODUCTION_CHANGES=0

No new equivalence redesign is required in R10.

R9 is the comprehensive proof.

R10 records that proof into the final baseline.

---

# Canonical Knowledge Final State

Require:

ONE_CANONICAL_KNOWLEDGE_SOURCE=PASS

TECHNICAL_LEAD_FINAL_APPROVAL_AUTHORITY=PASS

SOURCE_CODE_OPTIONAL=PASS

PROVENANCE_PRESERVED=PASS

UNCERTAINTY_PRESERVED=PASS

AS_IS_TO_BE_HISTORICAL_SEMANTICS_PRESERVED=PASS

AI_INTERPRETATION_NOT_SELF_APPROVING=PASS

---

# R11 / R12 Final State

Require:

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0

PLUGIN_RUNTIME=NOT_IMPLEMENTED

R11 remains human-readable projection.

R12 remains Plugin-facing machine projection.

Neither is the canonical source.

---

# Final Debt Ledger

Preserve exactly unless repository evidence proves a later approved decision:

DUP_001=RESOLVED
DUP_002=PRESERVED_DISTINCT
DUP_003=UNTOUCHED
DUP_004=UNTOUCHED

DEBT_001=RESOLVED
DEBT_002=RESOLVED
DEBT_003=RESOLVED

REG_002_CANDIDATE=RESOLVED

TD_001=OPEN
TD_002=DEFERRED
TD_003=PRESERVED_DISTINCT
TD_004=PARTIALLY_RESOLVED
TD_005=PARTIALLY_RESOLVED

Require:

FINAL_DEBT_LEDGER_CONSISTENT=PASS

R10 must not resolve debt.

Remaining debt is allowed in final V4.1 closure because it is explicitly
documented, risk-classified, and intentionally deferred.

---

# V5 Boundary

Record explicitly:

V5_IMPLEMENTED=false

V5 must address true agnosticism across at least:

- programming language;
- framework;
- project layout;
- architecture pattern;
- database/persistence technology;
- AI provider;
- AI model.

Require:

V5_AGNOSTICISM_BOUNDARY_DOCUMENTED=PASS

Important:

V4.1 does not implement any of these transformations.

Do not create provider abstractions.

Do not redesign extractors.

Do not rename Copilot-specific modules.

---

# Security

Require:

SECURITY_GATE=PASS

Perform closure-level verification for:

- secret introduction;
- unsafe paths;
- source-tree mutation;
- provider calls;
- real LLM calls;
- external runtime dependencies unexpectedly introduced by V4.1.

No secret value may be printed.

---

# Full Regression

Run:

python -m unittest discover -s tests

Require:

>=1566 PASS
FAIL=0
SKIP=0

No tests may be:

- removed;
- skipped;
- weakened;
- modified merely to make R10 pass.

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

# R10 Production Classification

Require:

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

If any production code changes:

STOP.

---

# Repository Continuity

Verify a fresh human or agent can reconstruct:

- what V4 implemented;
- why V4.1 existed;
- what R0-R9 changed;
- what remained unchanged;
- final test state;
- final behavior-equivalence state;
- remaining debt;
- Plugin contract boundary;
- V5 future scope;
- current project status.

Require:

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

No conversation memory may be required.

---

# R10 Artifacts

Create:

output/v4_1_r10/V4_1_FINAL_BASELINE.json

output/v4_1_r10/V4_1_FINAL_MANIFEST.json

Compute and report SHA-256 for both.

Generate each twice independently.

---

# PROJECT_STATE

After successful R10 preparation:

latest_completed_round = V4.1-R10
latest_approved_round = V4.1-R9

current_round_in_progress =
"V4.1-R10 (pending Technical Lead final review)"

round_status =
V4_1_R10_READY_FOR_FINAL_REVIEW

next =
HUMAN_FINAL_REVIEW_V4_1

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0

V4 remains formally closed.

V4.1 must NOT yet be marked formally closed.

---

# Required Result

Create:

docs/V4_1/V4_1_R10_FINAL_BASELINE_AND_FORMAL_CLOSURE_RESULT.md

Report at minimum:

STATUS
ENTRY_GATE

BASELINE_TESTS
FINAL_TESTS

V4_BASELINE_INTEGRITY
V4_MANIFEST_INTEGRITY

HISTORICAL_V4_1_ARTIFACT_INTEGRITY
R0_FROZEN_INVENTORY_MODIFIED

R9_COMPREHENSIVE_ARTIFACT_INTEGRITY
R9_COMPREHENSIVE_EQUIVALENCE_DECISION

CONTRACT_VERIFICATION_MATRIX
DETERMINISTIC_BEHAVIOR

DATABASE_EXTRACTOR_BEHAVIOR_EQUIVALENCE
FLOW_RESOLVER_BEHAVIOR_EQUIVALENCE
R7_EXCEPTION_BOUNDARIES_PRESERVED
PROVIDER_BOUNDARY_PRODUCTION_CHANGES

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

FINAL_DEBT_LEDGER_CONSISTENT

V5_IMPLEMENTED
V5_AGNOSTICISM_BOUNDARY_DOCUMENTED

SECURITY_GATE

V4_1_FINAL_BASELINE
V4_1_FINAL_BASELINE_SHA256
V4_1_FINAL_BASELINE_DETERMINISM

V4_1_FINAL_MANIFEST
V4_1_FINAL_MANIFEST_SHA256
V4_1_FINAL_MANIFEST_DETERMINISM

PRODUCTION_CODE_CHANGED
PRODUCTION_BEHAVIOR_CHANGED

READINESS
AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

REPOSITORY_CONTINUITY
AGENT_NEUTRAL_CONTINUITY

PROJECT_STATE

DECISION
NEXT

---

# Expected Success State

STATUS=V4_1_R10_READY_FOR_FINAL_REVIEW

ENTRY_GATE=PASS

FINAL_TESTS=>=1566_PASS_0_FAIL_0_SKIP

V4_BASELINE_INTEGRITY=PASS
V4_MANIFEST_INTEGRITY=PASS

HISTORICAL_V4_1_ARTIFACT_INTEGRITY=PASS
R0_FROZEN_INVENTORY_MODIFIED=false

R9_COMPREHENSIVE_ARTIFACT_INTEGRITY=PASS
R9_COMPREHENSIVE_EQUIVALENCE_DECISION=APPROVED

CONTRACT_VERIFICATION_MATRIX=PASS
DETERMINISTIC_BEHAVIOR=PASS

DATABASE_EXTRACTOR_BEHAVIOR_EQUIVALENCE=PASS
FLOW_RESOLVER_BEHAVIOR_EQUIVALENCE=PASS

R7_EXCEPTION_BOUNDARIES_PRESERVED=PASS
PROVIDER_BOUNDARY_PRODUCTION_CHANGES=0

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

FINAL_DEBT_LEDGER_CONSISTENT=PASS

V5_IMPLEMENTED=false
V5_AGNOSTICISM_BOUNDARY_DOCUMENTED=PASS

SECURITY_GATE=PASS

V4_1_FINAL_BASELINE_DETERMINISM=PASS
V4_1_FINAL_MANIFEST_DETERMINISM=PASS

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

PROJECT_STATE=V4_1_R10_READY_FOR_FINAL_REVIEW

DECISION=V4_1_R10_READY_FOR_TECHNICAL_LEAD_FINAL_APPROVAL

NEXT=HUMAN_FINAL_REVIEW_V4_1

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

1. final V4.1 baseline generation;
2. final V4.1 manifest generation;
3. deterministic verification;
4. final debt ledger verification;
5. regression;
6. readiness verification;
7. security verification;
8. repository-continuity verification;
9. result document;
10. PROJECT_STATE pending final Technical Lead review.

Do NOT:

- formally close V4.1;
- approve R10;
- commit;
- push;
- begin V5;
- resolve remaining debt;
- modify production code;
- introduce provider abstractions;
- implement Plugin runtime.