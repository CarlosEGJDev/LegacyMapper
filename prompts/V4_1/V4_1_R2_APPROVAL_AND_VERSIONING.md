# LegacyMapper V4.1 — R2 Approval and Versioning

TASK=V4_1_R2_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false
REFACTOR_ALLOWED=false
R3_IMPLEMENTATION_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=true
GIT_PUSH_ALLOWED=true

---

# Human Authorization

The Technical Lead has explicitly reviewed and approved:

```text
V4.1-R2 — Models, Types and Public Contracts Readability
```

The Technical Lead explicitly accepts:

1. the evidence-driven scope derived from R0;
2. the 11 modified production files;
3. the 33 annotated public/significant symbols;
4. the deliberate absence of new TypedDicts where stable shapes could not be proven;
5. `EvidenceKeyMap = dict[str, str]` as the single new semantic type alias;
6. preservation of ambiguous/historically-open JSON boundaries;
7. preservation of heterogeneous-return orchestrators for later characterization;
8. preservation of all R0 high-risk modules;
9. public calling compatibility;
10. model field/default equivalence;
11. serialized-output equivalence;
12. approved-artifact integrity;
13. `TD-005=PARTIALLY_RESOLVED`;
14. `PRODUCTION_BEHAVIOR_CHANGED=false`;
15. no R2.1 corrective round is required.

The development agent does not grant this approval.

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/V4/V4_FINAL_CLOSURE_RESULT.md`
5. `docs/V4_1/V4_1_R0_CLOSURE_AND_VERSIONING_RESULT.md`
6. `docs/V4_1/V4_1_R1_CLOSURE_AND_VERSIONING_RESULT.md`
7. `docs/V4_1/V4_1_R2_MODELS_TYPES_AND_PUBLIC_CONTRACTS_READABILITY_RESULT.md`
8. `output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json`
9. `output/v4_1_r0/V4_1_REFACTOR_PLAN.json`
10. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Repository artifacts are authoritative.

---

# Expected Reviewed State

Require:

```text
latest_completed_round = V4.1-R2
latest_approved_round = V4.1-R1

current_round_in_progress =
"V4.1-R2 (pending Technical Lead review)"

round_status =
V4_1_R2_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R2

tests = 1442
readiness = READY

provider_calls = 0
real_llm_calls = 0
```

If materially different:

STOP.

---

# Reviewed Equivalence Artifact

Expected:

```text
output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json

SHA256=
bd3daf04be868ef6465298c5e372aacc1f33bf234417f2bb914b79b22ab5a6f4
```

Recompute.

Require:

```text
TYPE_AND_CONTRACT_EQUIVALENCE_ARTIFACT_INTEGRITY=PASS
```

If different:

STOP.

Do not regenerate or repair it.

---

# Approved TD-005 Disposition

Record:

```text
TD_005_STATUS=PARTIALLY_RESOLVED
```

Do NOT mark TD-005 resolved.

The remaining work includes historically ambiguous nested JSON boundaries and heterogeneous-return orchestration boundaries that require characterization before safe narrowing.

Preserve this debt for later V4.1 rounds.

---

# Approved R2 Scope

Preserve:

```text
CANDIDATES_CONSIDERED=16
CANDIDATES_CHANGED=11
CANDIDATES_DEFERRED=5

AFFECTED_PUBLIC_SYMBOLS=33

NEW_TYPEDDICTS=0
NEW_TYPE_ALIASES=1
```

Approved alias:

```text
legacy_documenter.documentation.evidence_catalog.EvidenceKeyMap
```

Do not add additional typing during closure.

---

# Dynamic Boundaries

Require:

```text
DYNAMIC_BOUNDARIES_PRESERVED=PASS
```

Ambiguous/historically-open nested JSON parameters remain deliberately dynamic until characterized.

Do not replace them with speculative:

```text
dict[str, Any]
TypedDict
dataclass
object
```

merely for apparent type completeness.

---

# High-Risk Modules

Require unchanged:

```text
legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py
legacy_documenter/knowledge/readiness.py
legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py
```

Record:

```text
HIGH_RISK_MODULES_PRESERVED=PASS
```

Do not modify them during closure.

---

# Public Compatibility

Require:

```text
PUBLIC_RUNTIME_CONTRACT_CHANGED=false
PUBLIC_CALL_COMPATIBILITY=PASS

MODEL_FIELD_EQUIVALENCE=PASS
MODEL_DEFAULT_EQUIVALENCE=PASS

SERIALIZED_OUTPUT_EQUIVALENCE=PASS
```

No signature/calling-convention redesign is authorized.

---

# Approved Artifact Integrity

Reconfirm relevant approved artifacts.

At minimum preserve the reviewed checks for:

```text
output/v4_r14/V4_FINAL_BASELINE.json

SHA256=
d13e3807a12187b226ea55752ae0e9dccd2ad20c9dbe044360ffa48bca526d1e
```

```text
output/v4_r14/V4_FINAL_MANIFEST.json

SHA256=
be398240a31137e7dea25fcaa7b3cfe6580d2557f990f7da884d5775f5c40551
```

```text
output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json

SHA256=
55c99c3b68ac159585c6a0ec7e05f74e8dd64dd871308d067ab27bdda1a1c33b
```

Require:

```text
APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
```

Do not regenerate historical artifacts.

---

# R0 Historical Inventory

Preserve the frozen historical artifact:

```text
output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
```

Its live reconstruction may legitimately differ because R2 changed typing diagnostics.

Required:

```text
R0_FROZEN_INVENTORY_MODIFIED=false
```

The existing durable comparison logic may account only for the explicitly authorized R1/R2 changes.

Do not weaken it into a generic permissive comparison.

---

# Global Invariants

Preserve:

```text
REFRACTOR_GOAL=READABILITY_AND_MAINTAINABILITY

BEHAVIOR_CHANGE=FORBIDDEN

V4_CONTRACT_CHANGE=FORBIDDEN

SERIALIZED_CONTRACT_CHANGE=FORBIDDEN

PUBLIC_API_BREAK=FORBIDDEN

PLUGIN_RUNTIME_IMPLEMENTATION=FORBIDDEN

V5_IMPLEMENTATION=FORBIDDEN
```

---

# Regression

Run:

```text
python -m unittest discover -s tests
```

Require:

```text
>=1442 PASS
FAIL=0
SKIP=0
```

No test may be removed, skipped or weakened.

---

# Readiness

Run:

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

# V4 Preservation

Require:

```text
V4_CONTRACTS_UNCHANGED=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0

PLUGIN_RUNTIME=NOT_IMPLEMENTED

V5_IMPLEMENTED=false
```

---

# Production Classification

Preserve:

```text
PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false
```

Closure itself must not introduce additional production changes.

---

# PROJECT_STATE

Register Technical Lead approval.

Required semantic state:

```text
latest_completed_round = V4.1-R2
latest_approved_round = V4.1-R2

current_round_in_progress = null

round_status = V4_1_R2_APPROVED

next = V4.1-R3

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

V4 remains formally closed.

---

# R2 Result Closure Section

Append only a closure section to:

```text
docs/V4_1/V4_1_R2_MODELS_TYPES_AND_PUBLIC_CONTRACTS_READABILITY_RESULT.md
```

Record:

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

TD_005_DECISION=PARTIALLY_RESOLVED_APPROVED

TYPE_SAFETY_SCOPE_DECISION=APPROVED
DYNAMIC_BOUNDARY_DECISION=APPROVED
HIGH_RISK_DEFERRAL_DECISION=APPROVED

TYPE_AND_CONTRACT_EQUIVALENCE_DECISION=APPROVED

R2_1_REQUIRED=false

ROUND_STATUS=APPROVED

DECISION=V4_1_R2_FORMALLY_APPROVED

NEXT=V4.1-R3
```

Do not rewrite the reviewed result.

---

# Closure Result

Create:

```text
docs/V4_1/V4_1_R2_CLOSURE_AND_VERSIONING_RESULT.md
```

Report at minimum:

```text
STATUS

HUMAN_REVIEW
APPROVAL_AUTHORITY

TD_005_DECISION

TYPE_SAFETY_SCOPE_DECISION
DYNAMIC_BOUNDARY_DECISION
HIGH_RISK_DEFERRAL_DECISION

TYPE_AND_CONTRACT_EQUIVALENCE_ARTIFACT_SHA256
TYPE_AND_CONTRACT_EQUIVALENCE_ARTIFACT_INTEGRITY
TYPE_AND_CONTRACT_EQUIVALENCE_DECISION

PUBLIC_RUNTIME_CONTRACT_CHANGED
PUBLIC_CALL_COMPATIBILITY

MODEL_FIELD_EQUIVALENCE
MODEL_DEFAULT_EQUIVALENCE
SERIALIZED_OUTPUT_EQUIVALENCE

DYNAMIC_BOUNDARIES_PRESERVED
HIGH_RISK_MODULES_PRESERVED

APPROVED_ARTIFACT_HASHES_UNCHANGED
R0_FROZEN_INVENTORY_MODIFIED

TESTS
READINESS

V4_CONTRACTS_UNCHANGED
R11_BOUNDARY
R12_BOUNDARY

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
```

---

# Expected Success State

```text
STATUS=V4_1_R2_CLOSURE_AND_VERSIONING_COMPLETE

HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

TD_005_DECISION=PARTIALLY_RESOLVED_APPROVED

TYPE_SAFETY_SCOPE_DECISION=APPROVED
DYNAMIC_BOUNDARY_DECISION=APPROVED
HIGH_RISK_DEFERRAL_DECISION=APPROVED

TYPE_AND_CONTRACT_EQUIVALENCE_ARTIFACT_INTEGRITY=PASS
TYPE_AND_CONTRACT_EQUIVALENCE_DECISION=APPROVED

PUBLIC_RUNTIME_CONTRACT_CHANGED=false
PUBLIC_CALL_COMPATIBILITY=PASS

MODEL_FIELD_EQUIVALENCE=PASS
MODEL_DEFAULT_EQUIVALENCE=PASS
SERIALIZED_OUTPUT_EQUIVALENCE=PASS

DYNAMIC_BOUNDARIES_PRESERVED=PASS
HIGH_RISK_MODULES_PRESERVED=PASS

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
R0_FROZEN_INVENTORY_MODIFIED=false

TESTS=>=1442_PASS
READINESS=READY

V4_CONTRACTS_UNCHANGED=PASS
R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R2_APPROVED

GIT_SAFETY=PASS
SECRET_SCAN=PASS

GIT_COMMIT=PASS
GIT_PUSH=PASS
GIT_STATUS_AFTER=CLEAN

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

ROUND_STATUS=APPROVED

DECISION=V4_1_R2_FORMALLY_CLOSED_AND_VERSIONED

NEXT=V4.1-R3
```

---

# Git Safety

Inspect:

```text
git status
git diff
git diff --stat
```

No destructive Git operations.

Forbidden:

```text
git reset --hard
git clean
git restore .
git checkout -- .
git rebase
git amend
git squash
git push --force
```

---

# Secret Scan

Require:

```text
SECRET_SCAN=PASS
```

Do not expose secret values.

---

# Commit

Preferred message:

```text
Approve LegacyMapper V4.1-R2 type readability refactor
```

Use one normal commit.

No amend.

No squash.

---

# Push

Push normally to `origin`.

No force push.

---

# Repository Continuity

After closure a fresh human or AI agent must determine:

```text
V4 = FORMALLY CLOSED

V4.1-R0 = APPROVED
V4.1-R1 = APPROVED
V4.1-R2 = APPROVED

TD-005 = PARTIALLY_RESOLVED

DUP-001 = RESOLVED
DEBT-001 = RESOLVED

TESTS >= 1442 PASS

BEHAVIOR_CHANGE = FORBIDDEN

V4.1-R3 = NEXT
```

No conversation memory may be required.

---

# Stop Condition

STOP after:

1. R2 approval registration;
2. closure result creation;
3. full green regression;
4. readiness verification;
5. commit;
6. push;
7. clean Git status.

Do NOT:

* continue typing cleanup;
* mark TD-005 fully resolved;
* begin R3;
* restructure packages;
* decompose high-risk modules;
* change V4 contracts;
* begin V5;
* implement Plugin runtime.
