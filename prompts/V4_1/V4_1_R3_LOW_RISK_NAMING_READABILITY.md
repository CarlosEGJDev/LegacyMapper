# LegacyMapper V4.1 — R3 Low-Risk Naming Readability

TASK=V4_1_R3_LOW_RISK_NAMING_READABILITY

MODE=CONTROLLED_LOW_RISK_NAMING_REFACTOR

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

Improve readability through the small, evidence-backed naming changes approved by the V4.1-R0 roadmap.

R3 is intentionally narrow.

Primary targets:

```text
DEBT-003
LOW_RISK_NAMING_CANDIDATES_FROM_R0
```

This round must not become a repository-wide naming cleanup.

Required invariant:

```text
BEHAVIOR_CHANGE=FORBIDDEN
```

---

# Repository Authority

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/V4/V4_FINAL_CLOSURE_RESULT.md`
5. `docs/V4_1/V4_1_R0_MAINTAINABILITY_INVENTORY_AND_REFACTOR_PLAN_RESULT.md`
6. `docs/V4_1/V4_1_R0_CLOSURE_AND_VERSIONING_RESULT.md`
7. `docs/V4_1/V4_1_R1_CLOSURE_AND_VERSIONING_RESULT.md`
8. `docs/V4_1/V4_1_R2_CLOSURE_AND_VERSIONING_RESULT.md`
9. `output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json`
10. `output/v4_1_r0/V4_1_REFACTOR_PLAN.json`
11. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Repository artifacts are authoritative.

Do not reconstruct R3 scope from conversation memory.

Use the exact naming candidates recorded by R0.

---

# Entry Gate

Require:

```text
V4 = FORMALLY CLOSED

V4.1-R0 = APPROVED
V4.1-R1 = APPROVED
V4.1-R2 = APPROVED

latest_approved_round = V4.1-R2
next = V4.1-R3

tests >= 1442
readiness = READY

provider_calls = 0
real_llm_calls = 0
```

Run:

```text
git status
```

Expected clean except this R3 prompt.

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

Run readiness and require:

```text
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

If any entry gate fails:

STOP.

---

# Global V4.1 Invariants

Preserve:

```text
REFRACTOR_GOAL=READABILITY_AND_MAINTAINABILITY

BEHAVIOR_CHANGE=FORBIDDEN

V4_CONTRACT_CHANGE=FORBIDDEN

PUBLIC_API_BREAK=FORBIDDEN

SERIALIZED_CONTRACT_CHANGE=FORBIDDEN

PLUGIN_RUNTIME_IMPLEMENTATION=FORBIDDEN

V5_IMPLEMENTATION=FORBIDDEN
```

---

# R3 Scope

R0 replaced the original broad "Service Responsibility Separation" concept with:

```text
V4.1-R3 — Naming Pass Part 1 (Low-Risk Renames)
```

This decision is authoritative.

Use R0 artifacts to recover the exact candidates.

At minimum inspect:

```text
DEBT-003
maintainability_audit.audit
```

and the three verified batch-service parameter names identified by R0:

```text
classify_batch
create_proposal_batch
create_relation_batch
```

Do not assume these are the only targets until the R0 artifact is read.

---

# Candidate Table Before Editing

For every proposed rename record:

```text
path
symbol
current_name
proposed_name
scope
public_or_private
callers_found
keyword_callers_found
reflection_or_signature_usage
serialization_impact
compatibility_strategy
risk
```

Only implement:

```text
risk = LOW
```

Anything MEDIUM or above:

DEFER.

---

# Naming Principle

Rename only when the new name materially explains intent.

Good examples:

```text
requests -> classification_requests
requests -> proposal_requests
requests -> relation_requests
```

depending on actual function semantics.

Do NOT use those exact names unless repository evidence confirms them.

Avoid generic replacements such as:

```text
items
data
values
things
payloads
```

unless they are genuinely more accurate.

---

# DEBT-003

R0 identified generic `requests` naming in three batch-service methods.

The objective is readability only.

Before changing any parameter:

1. inspect every caller repository-wide;
2. identify positional calls;
3. identify keyword calls;
4. inspect tests;
5. inspect signature/introspection usage.

Important:

A Python parameter rename can break callers using keyword arguments.

Therefore:

```text
PARAMETER_RENAME_IS_NOT_AUTOMATICALLY_BEHAVIOR_FREE
```

If any public/external-looking caller uses the old keyword name, preserve compatibility.

---

# Compatibility Strategies

For each parameter rename choose one:

```text
DIRECT_RENAME_SAFE
COMPATIBILITY_SHIM_REQUIRED
DEFER_RENAME
```

Prefer no shim if every known caller is positional/internal and the public contract is demonstrably not externally relied upon.

If compatibility cannot be proven:

DEFER.

Do not introduce complicated `**kwargs` compatibility machinery merely to obtain a prettier name.

---

# maintainability_audit.audit

Inspect the R0 naming finding directly.

If the approved plan calls for a clearer alias:

* preserve the existing `audit` symbol;
* add the clearer name if appropriate;
* retain compatibility;
* avoid changing behavior.

Expected strategy where applicable:

```text
NEW_CLEAR_NAME
+
LEGACY_COMPATIBILITY_ALIAS
```

Do not remove `audit()`.

Do not break `write_audit()` or existing imports.

If R0 evidence supports a different strategy, follow the repository artifact.

---

# Public API Preservation

For every changed public/significant symbol require:

```text
OLD_IMPORT_PATH_STILL_VALID=true
OLD_CALLING_STYLE_STILL_VALID=true
RETURN_VALUE_UNCHANGED=true
EXCEPTION_BEHAVIOR_UNCHANGED=true
```

Where a rename is internal/local only, record that explicitly.

---

# High-Risk Modules

Do NOT structurally modify:

```text
legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py
legacy_documenter/knowledge/readiness.py
legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py
```

R3 is not their round.

Require:

```text
HIGH_RISK_MODULES_PRESERVED=PASS
```

---

# TD-005 Boundary

Do not continue R2 typing work in R3.

Preserve:

```text
TD_005=PARTIALLY_RESOLVED
```

No additional speculative typing.

---

# DUP Boundaries

Preserve:

```text
DUP_001=RESOLVED
DUP_002=PRESERVED_DISTINCT
DUP_003=<evaluate only insofar as DEBT-003 naming applies>
DUP_004=UNTOUCHED
```

R3 does not reopen shared JSON rendering.

---

# Tests

Add focused tests.

Preferred:

```text
tests/test_v4_1_r3_low_risk_naming_readability.py
```

Cover at minimum:

1. old public imports remain valid;
2. new clearer alias/name resolves where introduced;
3. positional calling behavior unchanged;
4. keyword compatibility preserved where required;
5. return values unchanged;
6. exceptions unchanged for representative invalid input;
7. batch outputs unchanged;
8. deterministic IDs unchanged;
9. serialization unchanged;
10. high-risk modules untouched;
11. V4 contracts unchanged;
12. readiness READY;
13. no provider/LLM calls.

Do not weaken existing tests.

---

# Behavioral Comparison

For each changed function capture representative pre-change output.

Compare post-change output.

Require:

```text
NAMING_BEHAVIOR_EQUIVALENCE=PASS
```

Parameter/local names are allowed to change.

Runtime semantics are not.

---

# Naming Compatibility Artifact

Create:

```text
output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json
```

Include at minimum:

```text
round

candidates_considered
candidates_changed
candidates_deferred

debt_003

renames

compatibility

public_imports

keyword_call_compatibility

behavior_equivalence

high_risk_modules

approved_artifact_integrity

tests

readiness

production_behavior_changed
```

No timestamps.

No absolute machine paths.

Generate twice independently.

Require:

```text
NAMING_COMPATIBILITY_ARTIFACT_DETERMINISM=PASS
```

---

# Approved Artifact Integrity

Verify relevant approved artifacts remain unchanged.

Require:

```text
APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
```

At minimum include R14 baseline/manifest and R1/R2 equivalence artifacts.

Do not regenerate frozen historical artifacts.

---

# Full Regression

Run:

```text
python -m unittest discover -s tests
```

Require:

```text
>1442 PASS
FAIL=0
SKIP=0
```

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

# Debt Disposition

At end classify:

```text
DEBT_003_STATUS=
RESOLVED
PARTIALLY_RESOLVED
DEFERRED
```

Only mark RESOLVED if all R0-defined DEBT-003 naming issues were safely addressed.

Also record:

```text
TD_005_STATUS=PARTIALLY_RESOLVED
```

unchanged.

---

# Production Classification

Expected:

```text
PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false
```

If no safe rename can actually be implemented:

```text
PRODUCTION_CODE_CHANGED=false
```

is acceptable.

Do not force a production change merely to satisfy the round title.

---

# PROJECT_STATE

After successful R3 implementation:

```text
latest_completed_round = V4.1-R3
latest_approved_round = V4.1-R2

current_round_in_progress =
"V4.1-R3 (pending Technical Lead review)"

round_status =
V4_1_R3_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R3

tests = <actual passing count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

V4 remains formally closed.

Do not approve R3.

---

# Required Result

Create:

```text
docs/V4_1/V4_1_R3_LOW_RISK_NAMING_READABILITY_RESULT.md
```

Report at minimum:

```text
STATUS
ENTRY_GATE

BASELINE_TESTS
FINAL_TESTS

R3_SCOPE_CONFIRMED_FROM_R0

CANDIDATES_CONSIDERED
CANDIDATES_CHANGED
CANDIDATES_DEFERRED

DEBT_003_STATUS
TD_005_STATUS

RENAMES_PERFORMED
ALIASES_ADDED
COMPATIBILITY_SHIMS_ADDED

PUBLIC_IMPORT_PATHS_PRESERVED
POSITIONAL_CALL_COMPATIBILITY
KEYWORD_CALL_COMPATIBILITY

RETURN_VALUE_EQUIVALENCE
EXCEPTION_BEHAVIOR_EQUIVALENCE
NAMING_BEHAVIOR_EQUIVALENCE

HIGH_RISK_MODULES_PRESERVED

APPROVED_ARTIFACT_HASHES_UNCHANGED

NAMING_COMPATIBILITY_ARTIFACT
NAMING_COMPATIBILITY_ARTIFACT_SHA256
NAMING_COMPATIBILITY_ARTIFACT_DETERMINISM

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
STATUS=V4_1_R3_IMPLEMENTATION_COMPLETE

ENTRY_GATE=PASS

FINAL_TESTS=>1442_PASS
FAIL=0
SKIP=0

TD_005_STATUS=PARTIALLY_RESOLVED

PUBLIC_IMPORT_PATHS_PRESERVED=PASS
POSITIONAL_CALL_COMPATIBILITY=PASS
KEYWORD_CALL_COMPATIBILITY=PASS

RETURN_VALUE_EQUIVALENCE=PASS
EXCEPTION_BEHAVIOR_EQUIVALENCE=PASS
NAMING_BEHAVIOR_EQUIVALENCE=PASS

HIGH_RISK_MODULES_PRESERVED=PASS

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

NAMING_COMPATIBILITY_ARTIFACT_DETERMINISM=PASS

V4_CONTRACTS_UNCHANGED=PASS
R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R3_READY_FOR_HUMAN_REVIEW

DECISION=V4_1_R3_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_1_R3
```

---

# Stop Conditions

STOP if:

* a rename breaks keyword-call compatibility;
* a public import would disappear;
* behavior/output changes;
* an approved artifact hash changes;
* a high-risk module must be structurally modified;
* the candidate requires characterization;
* scope expands beyond the R0 naming findings.

Defer instead of forcing the change.

---

# Final Stop

STOP after:

1. low-risk naming implementation;
2. focused tests;
3. full regression;
4. compatibility artifact;
5. result document;
6. PROJECT_STATE pending Technical Lead review.

Do NOT:

* approve R3;
* commit;
* push;
* begin R4;
* decompose readiness;
* touch DatabaseExtractor or FunctionalFlowResolver;
* continue broad typing cleanup;
* begin V5;
* implement Plugin runtime.
