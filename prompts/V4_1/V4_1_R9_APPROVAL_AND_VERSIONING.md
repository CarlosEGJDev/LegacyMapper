# LegacyMapper V4.1 — R9 Approval and Versioning

TASK=V4_1_R9_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
REFACTOR_ALLOWED=false
R10_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

V4.1-R9 — Comprehensive Regression and Behavioral Equivalence

The Technical Lead explicitly accepts:

- R9 is verification-only;
- baseline tests = 1566 pass, 0 fail, 0 skip;
- final tests = 1566 pass, 0 fail, 0 skip;
- V4 baseline integrity PASS;
- V4 manifest integrity PASS;
- R1-R8 historical artifact integrity PASS;
- R0 frozen inventory unchanged;
- R1-R8 approval chain complete;
- cumulative change inventory verified;
- all 17 contract-verification items PASS;
- deterministic behavior PASS;
- DatabaseExtractor equivalence PASS;
- FunctionalFlowResolver equivalence PASS;
- R6 deferred groups preserved;
- R7 exception boundaries preserved;
- provider boundary production changes = 0;
- canonical knowledge contracts preserved;
- R11 boundary preserved;
- R12 boundary preserved;
- security gate PASS;
- debt state consistent;
- V5 agnosticism boundary documented but not implemented;
- production code changed = false;
- production behavior changed = false;
- no R9.1 corrective round is required.

The development agent does not grant this approval.

---

# Required Reading

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
14. docs/V4_1/V4_1_R9_COMPREHENSIVE_REGRESSION_AND_BEHAVIORAL_EQUIVALENCE_RESULT.md
15. output/v4_1_r9/V4_1_R9_COMPREHENSIVE_EQUIVALENCE.json

Repository artifacts are authoritative.

---

# Expected Reviewed State

Require:

latest_completed_round = V4.1-R9
latest_approved_round = V4.1-R8

current_round_in_progress =
"V4.1-R9 (pending Technical Lead review)"

round_status =
V4_1_R9_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R9

tests = 1566
readiness = READY

provider_calls = 0
real_llm_calls = 0

If materially different:

STOP.

---

# Reviewed R9 Artifact

Expected:

output/v4_1_r9/V4_1_R9_COMPREHENSIVE_EQUIVALENCE.json

SHA256=
87f49a41712ac83f948378da4e56c0df54b8c3f1a02741013b1f4d1b87568f04

Recompute.

Require:

R9_COMPREHENSIVE_ARTIFACT_INTEGRITY=PASS

If different:

STOP.

Do not regenerate or repair the artifact.

---

# V4 Baseline

Require:

V4_BASELINE_INTEGRITY=PASS
V4_MANIFEST_INTEGRITY=PASS

Expected:

V4_FINAL_BASELINE_SHA256=
d13e3807a12187b226ea55752ae0e9dccd2ad20c9dbe044360ffa48bca526d1e

V4_FINAL_MANIFEST_SHA256=
be398240a31137e7dea25fcaa7b3cfe6580d2557f990f7da884d5775f5c40551

Do not regenerate them.

---

# Historical V4.1 Evidence

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

R0_FROZEN_INVENTORY_MODIFIED=false

Do not regenerate historical artifacts.

---

# Approval Chain

Require:

R1_R8_APPROVAL_CHAIN_COMPLETE=PASS

Register:

R9_VERIFICATION_DECISION=APPROVED

No previous approval may be rewritten.

---

# Contract Matrix

Require:

CONTRACT_VERIFICATION_MATRIX=PASS

The following remain PASS:

- public import paths;
- public callable signatures;
- positional call compatibility;
- keyword call compatibility;
- deterministic identifiers;
- deterministic ordering;
- serialized output structures;
- exception behavior;
- partial-result behavior;
- state reuse/reset semantics;
- readiness behavior;
- canonical knowledge behavior;
- R11 human projection boundary;
- R12 Plugin projection boundary;
- security invariants;
- source-code optionality;
- Technical Lead approval authority.

Closure must not modify production code to re-prove any contract.

---

# High-Risk Preservation

Require:

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

Do not modify:

legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py

Do not touch:

_path_id
_path_identities
_add_path
_call_ref
_stable_id

---

# R7 Preservation

Require:

R7_EXCEPTION_BOUNDARIES_PRESERVED=PASS
PROVIDER_BOUNDARY_PRODUCTION_CHANGES=0

Do not modify:

legacy_documenter/main.py::_extract_into

Do not modify provider exception boundaries.

---

# Canonical Knowledge Contracts

Require:

ONE_CANONICAL_KNOWLEDGE_SOURCE=PASS
TECHNICAL_LEAD_FINAL_APPROVAL_AUTHORITY=PASS
SOURCE_CODE_OPTIONAL=PASS
PROVENANCE_PRESERVED=PASS
UNCERTAINTY_PRESERVED=PASS
AS_IS_TO_BE_HISTORICAL_SEMANTICS_PRESERVED=PASS
AI_INTERPRETATION_NOT_SELF_APPROVING=PASS

No canonical knowledge redesign is authorized.

---

# Projection Boundaries

Require:

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0
PLUGIN_RUNTIME=NOT_IMPLEMENTED

---

# Security

Require:

SECURITY_GATE=PASS

No source-tree mutation.

No secret introduction.

No provider calls.

No real LLM calls.

No hidden network dependency.

---

# Debt State

Preserve exactly:

DUP_001=RESOLVED
DEBT_001=RESOLVED
DEBT_002=RESOLVED
DEBT_003=RESOLVED

DUP_002=PRESERVED_DISTINCT
DUP_003=UNTOUCHED
DUP_004=UNTOUCHED

TD_001=OPEN
TD_002=DEFERRED
TD_003=PRESERVED_DISTINCT
TD_004=PARTIALLY_RESOLVED
TD_005=PARTIALLY_RESOLVED

REG_002_CANDIDATE=RESOLVED

Require:

DEBT_STATE_CONSISTENT=PASS

Do not silently resolve any remaining item during closure.

---

# V5 Boundary

Preserve:

V5_IMPLEMENTED=false
V5_AGNOSTICISM_BOUNDARY_DOCUMENTED=PASS

V5 is responsible for future agnosticism across:

- programming language;
- framework;
- project layout;
- architecture pattern;
- database/persistence technology;
- AI provider;
- AI model.

Do not implement any V5 architecture during this closure.

Do not introduce provider abstractions.

---

# Regression

Run:

python -m unittest discover -s tests

Require:

>=1566 PASS
FAIL=0
SKIP=0

No test may be removed, skipped, weakened or rewritten merely for closure.

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

# Production Classification

R9 itself remains:

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

Closure itself must make no production-code changes.

---

# PROJECT_STATE

Register Technical Lead approval:

latest_completed_round = V4.1-R9
latest_approved_round = V4.1-R9

current_round_in_progress = null

round_status = V4_1_R9_APPROVED

next = V4.1-R10

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0

V4 remains formally closed.

---

# R9 Result Closure Section

Append only a closure section to:

docs/V4_1/V4_1_R9_COMPREHENSIVE_REGRESSION_AND_BEHAVIORAL_EQUIVALENCE_RESULT.md

Record:

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R9_VERIFICATION_DECISION=APPROVED

CONTRACT_VERIFICATION_MATRIX=PASS
DETERMINISTIC_BEHAVIOR=PASS

HISTORICAL_V4_1_ARTIFACT_INTEGRITY=PASS
R1_R8_APPROVAL_CHAIN_COMPLETE=PASS

R9_COMPREHENSIVE_EQUIVALENCE_DECISION=APPROVED

R9_1_REQUIRED=false

ROUND_STATUS=APPROVED
DECISION=V4_1_R9_FORMALLY_APPROVED
NEXT=V4.1-R10

Do not rewrite the reviewed body.

---

# Closure Result

Create:

docs/V4_1/V4_1_R9_CLOSURE_AND_VERSIONING_RESULT.md

Report at minimum:

STATUS
HUMAN_REVIEW
APPROVAL_AUTHORITY

R9_VERIFICATION_DECISION

V4_BASELINE_INTEGRITY
V4_MANIFEST_INTEGRITY

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

R9_COMPREHENSIVE_ARTIFACT_SHA256
R9_COMPREHENSIVE_ARTIFACT_INTEGRITY
R9_COMPREHENSIVE_EQUIVALENCE_DECISION

TESTS
READINESS

PRODUCTION_CODE_CHANGED
PRODUCTION_BEHAVIOR_CHANGED

AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE

GIT_STATUS_BEFORE
GIT_BRANCH
GIT_REMOTE
GIT_SAFETY
SECRET_SCAN

GIT_COMMIT
GIT_COMMIT_HASH
GIT_PUSH
GIT_STATUS_AFTER

REPOSITORY_CONTINUITY
AGENT_NEUTRAL_CONTINUITY

ROUND_STATUS
DECISION
NEXT

---

# Expected Success State

STATUS=V4_1_R9_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R9_VERIFICATION_DECISION=APPROVED

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

R9_COMPREHENSIVE_ARTIFACT_INTEGRITY=PASS
R9_COMPREHENSIVE_EQUIVALENCE_DECISION=APPROVED

TESTS=>=1566_PASS
READINESS=READY

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R9_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_COMMIT_HASH=<ACTUAL_COMMIT_HASH>
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_1_R9_FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4.1-R10

---

# Git Safety

Inspect:

git status
git diff
git diff --stat

Forbidden:

git reset --hard
git clean
git restore .
git checkout -- .
git rebase
git amend
git squash
git push --force

---

# Secret Scan

Require:

SECRET_SCAN=PASS

Do not expose secret values.

---

# Commit

Preferred message:

Approve LegacyMapper V4.1-R9 comprehensive equivalence verification

Use one normal commit.

No amend.
No squash.

Record the real commit hash with:

git rev-parse HEAD

---

# Push

Push normally to origin.

No force push.

After push require:

git status --short

to be empty.

---

# Repository Continuity

After closure a fresh human or AI agent must determine:

V4 = FORMALLY CLOSED

V4.1-R0 through V4.1-R9 = APPROVED

V4.1 comprehensive behavioral equivalence = PASS

TESTS >= 1566 PASS

PRODUCTION_BEHAVIOR_CHANGED = false

remaining debt preserved explicitly

V5 = NOT IMPLEMENTED

V5 future scope includes:
language/framework/layout/architecture/database/AI-provider/AI-model agnosticism

V4.1-R10 = NEXT

No conversation memory may be required.

---

# Stop Condition

STOP after:

1. R9 approval registration;
2. closure result creation;
3. full regression;
4. readiness verification;
5. normal commit;
6. actual commit hash recording;
7. push;
8. clean Git status.

Do NOT:

- begin R10;
- modify production code;
- fix remaining debt;
- refactor;
- implement V5;
- introduce AI-provider abstractions;
- implement Plugin runtime.