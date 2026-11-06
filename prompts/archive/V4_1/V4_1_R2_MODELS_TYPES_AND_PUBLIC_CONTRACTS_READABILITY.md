# LegacyMapper V4.1 — R2 Models, Types and Public Contracts Readability

TASK=V4_1_R2_MODELS_TYPES_AND_PUBLIC_CONTRACTS_READABILITY

MODE=CONTROLLED_TYPE_SAFETY_AND_READABILITY_REFACTOR

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

Improve maintainability at selected model, typing, and public/service boundaries without changing runtime behavior or approved contracts.

Primary debt:

```text
TD-005
```

R2 is NOT a repository-wide typing migration.

Required principle:

```text
TYPE_WHERE_IT_CLARIFIES
DO_NOT_TYPE_FOR_METRICS
```

And:

```text
BEHAVIOR_CHANGE=FORBIDDEN
```

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/V4/V4_FINAL_CLOSURE_RESULT.md`
5. `docs/V4_1/V4_1_R0_MAINTAINABILITY_INVENTORY_AND_REFACTOR_PLAN_RESULT.md`
6. `docs/V4_1/V4_1_R0_CLOSURE_AND_VERSIONING_RESULT.md`
7. `docs/V4_1/V4_1_R1_CLOSURE_AND_VERSIONING_RESULT.md`
8. `output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json`
9. `output/v4_1_r0/V4_1_REFACTOR_PLAN.json`
10. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Resolve the exact original definition and affected files of `TD-005` from repository artifacts.

Do not reconstruct TD-005 from conversation memory.

Repository artifacts are authoritative.

---

# Entry Gate

Require:

```text
V4 = FORMALLY CLOSED

V4.1-R0 = APPROVED
V4.1-R1 = APPROVED

latest_approved_round = V4.1-R1

next = V4.1-R2

tests >= 1424
readiness = READY

provider_calls = 0
real_llm_calls = 0
```

Run:

```text
git status
```

Expected clean except this R2 prompt.

Run:

```text
python -m unittest discover -s tests
```

Require:

```text
>=1424 PASS
FAIL=0
```

Run readiness.

Require:

```text
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

If any gate fails:

STOP.

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

# Scope Must Come From R0 Evidence

Use:

```text
output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
```

to identify the exact R2 candidates.

Do not perform a broad "add type hints everywhere" pass.

Build an explicit candidate table before editing:

```text
path
symbol
current_typing_issue
maintainability_value
public_boundary
runtime_risk
serialization_risk
proposed_change
```

Only implement candidates with:

```text
maintainability_value = meaningful
runtime_risk = low
serialization_risk = none_or_proven_equivalent
```

For any uncertain candidate:

DEFER.

---

# R2 Allowed Work

R2 may perform small changes such as:

* add missing return annotations;
* add useful parameter annotations;
* replace unnecessarily broad internal mapping annotations with narrow types;
* introduce small `TypedDict` definitions for stable internal JSON/mapping structures;
* introduce type aliases where they materially explain a contract;
* improve model/service-boundary annotations;
* add concise docstrings where typing alone does not explain intent;
* clarify Optional/Union boundaries;
* replace ambiguous local type declarations;
* improve names of private/local type concepts when compatibility is irrelevant.

Only where supported by R0 evidence.

---

# R2 Forbidden Work

Do NOT:

* convert the entire repository to TypedDict;
* replace runtime dataclasses with TypedDict merely for style;
* introduce Pydantic;
* introduce mypy/pyright as a mandatory dependency;
* add third-party typing dependencies;
* change JSON keys;
* change JSON ordering;
* change enum values;
* change dataclass field order;
* change constructor signatures incompatibly;
* change validation semantics;
* change default values;
* change optionality at runtime;
* change exception behavior;
* change deterministic IDs;
* change artifact paths;
* change public import paths;
* restructure packages;
* move classes between modules;
* begin responsibility decomposition;
* touch high-risk orchestrators merely to improve typing.

---

# Python Runtime Safety

Remember that Python annotations can affect runtime behavior.

Before introducing a type:

* check supported Python version;
* inspect whether annotations are introspected;
* inspect dataclass behavior;
* inspect serialization;
* inspect `typing.get_type_hints`;
* inspect equality/hash/repr dependencies;
* inspect tests that compare signatures or model fields.

Prefer annotations that do not alter runtime semantics.

Do not assume typing is behavior-free.

---

# TypedDict Policy

`TypedDict` is allowed only for mapping-shaped structures that already have a stable deterministic shape.

Good candidate:

```text
internal structured mapping passed between known services
```

Bad candidate:

```text
open metadata bag
external arbitrary JSON
intentionally extensible mapping
historical schema with heterogeneous values
```

Do not narrow extension points that are intentionally open.

---

# `Any` Policy

Do not mechanically eliminate `Any`.

Classify each relevant `Any` as:

```text
NECESSARY_DYNAMIC_BOUNDARY
SAFE_TO_NARROW
DEFER
```

Examples of legitimate `Any`:

* generic JSON values;
* external provider payload boundaries;
* intentionally open metadata;
* compatibility layers.

Replacing truthful `Any` with an inaccurate narrow type is worse than retaining `Any`.

---

# Public Contract Inventory

Before changes, identify every affected public symbol.

For each record:

```text
module
symbol
kind
current_signature
proposed_signature
import_path
callers_found
runtime_contract_changed
```

Require:

```text
PUBLIC_RUNTIME_CONTRACT_CHANGED=false
```

Adding an annotation is allowed only if it does not change calling semantics.

---

# Model Safety

For affected dataclasses/models capture before and after:

```text
field names
field order
defaults
default factories
frozen state
equality behavior
hash behavior where applicable
constructor calling behavior
serialized representation where applicable
```

Require equivalence.

Do not reorder fields for aesthetics.

---

# Serialization Safety

For every affected model or mapping participating in serialization:

capture representative deterministic output before modification.

Compare after modification.

Require:

```text
SERIALIZED_OUTPUT_EQUIVALENCE=PASS
```

Where approved artifacts directly depend on affected code, verify existing hashes remain unchanged.

Do not regenerate historical artifacts merely to make them match.

---

# Public Signature Compatibility

Preserve positional and keyword calling behavior.

Required:

```text
PUBLIC_CALL_COMPATIBILITY=PASS
```

Annotations may improve.

Calling semantics may not.

Do not make previously optional arguments mandatory.

Do not make positional arguments keyword-only or vice versa.

---

# TD-005

Resolve the original debt statement from repository artifacts.

At the end classify:

```text
TD_005_STATUS=
RESOLVED
PARTIALLY_RESOLVED
DEFERRED
```

Do not mark `RESOLVED` unless the original debt has actually been eliminated.

If R2 intentionally handles only the safe/high-value portion, prefer:

```text
TD_005_STATUS=PARTIALLY_RESOLVED
```

and record exact remaining work.

---

# High-Risk Boundaries

Do not refactor these merely for typing if R0 marked them characterization-sensitive:

```text
legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py
legacy_documenter/knowledge/readiness.py
legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py
```

If a trivial annotation is genuinely safe and useful, document why.

Default:

```text
DEFER_TO_CHARACTERIZATION_ROUND
```

---

# Historical Compatibility

V1-V3 code may have awkward structures that are externally relied upon.

Do not modernize historical code solely because newer V4 code uses stronger typing.

Compatibility wins.

---

# No Premature Abstraction

If the same mapping shape appears in two places, do not automatically create one shared type.

First determine whether they represent the same semantic contract.

Required classification:

```text
SAME_CONTRACT
SIMILAR_SHAPE_DIFFERENT_SEMANTICS
UNKNOWN
```

Only `SAME_CONTRACT` may share a type.

---

# Documentation

For every new public/significant type alias, TypedDict, class, or function:

add a concise explanatory docstring/comment.

Explain:

```text
what this type represents
why the boundary is intentionally narrow or broad
```

Do not comment obvious syntax.

---

# C#-Friendly Readability

Where compatible with idiomatic Python:

prefer explicit readable type names over deeply nested inline annotations.

For example, prefer:

```python
EvidenceIndex = dict[str, tuple[str, ...]]
```

when the alias carries real domain meaning.

Do not create aliases such as:

```python
StringList = list[str]
```

that add no semantic value.

---

# Static Diagnostic

Use standard-library AST inspection or existing R0 tooling to measure before/after relevant typing observations.

Do not add a mandatory static-type-checking dependency.

Record diagnostic changes, but do not optimize solely for counts.

Metrics are supporting evidence only.

---

# Tests

Add focused R2 tests.

Preferred:

```text
tests/test_v4_1_r2_models_types_and_public_contracts.py
```

Cover at minimum:

1. affected public imports still resolve;
2. calling conventions unchanged;
3. dataclass/model field order unchanged;
4. defaults/default factories unchanged;
5. serialization unchanged;
6. deterministic outputs unchanged;
7. approved artifact hashes unchanged where applicable;
8. type aliases/TypedDicts express the intended stable structures;
9. intentionally dynamic boundaries remain dynamic;
10. high-risk modules were not structurally refactored;
11. R11/R12 boundaries unchanged;
12. readiness READY;
13. no LLM/provider calls.

Do not remove or weaken existing tests.

---

# Type and Contract Equivalence Artifact

Create:

```text
output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json
```

Include:

```text
round

td_005

candidates_considered
candidates_changed
candidates_deferred

public_symbols

model_equivalence

serialization_equivalence

approved_artifact_integrity

dynamic_boundaries_preserved

high_risk_modules

typing_diagnostics_before
typing_diagnostics_after

tests

readiness

production_behavior_changed
```

No timestamps.

No absolute machine-specific paths.

Generate twice independently.

Require:

```text
TYPE_AND_CONTRACT_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS
```

---

# Full Regression

Run:

```text
python -m unittest discover -s tests
```

Require:

```text
>1424 PASS
FAIL=0
```

Run readiness again.

Require:

```text
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

---

# Approved Artifact Integrity

Verify relevant approved V4 artifacts remain unchanged.

At minimum require:

```text
V4_CONTRACTS_UNCHANGED=PASS
APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
```

If an approved hash changes:

STOP.

Do not repair/regenerate the artifact in the same round.

---

# R11 / R12

Require:

```text
R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0

PLUGIN_RUNTIME=NOT_IMPLEMENTED
```

---

# Production Classification

Expected:

```text
PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false
```

If evidence shows runtime behavior changed:

STOP.

Do not classify it as refactor.

---

# PROJECT_STATE

After successful R2 implementation:

```text
latest_completed_round = V4.1-R2
latest_approved_round = V4.1-R1

current_round_in_progress =
"V4.1-R2 (pending Technical Lead review)"

round_status =
V4_1_R2_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_1_R2

tests = <actual passing test count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

V4 remains formally closed.

Do not approve R2.

---

# Required Result

Create:

```text
docs/V4_1/V4_1_R2_MODELS_TYPES_AND_PUBLIC_CONTRACTS_READABILITY_RESULT.md
```

Report at minimum:

```text
STATUS
ENTRY_GATE

BASELINE_TESTS
FINAL_TESTS

TD_005_ORIGINAL_DESCRIPTION
TD_005_STATUS
TD_005_REMAINING_WORK

CANDIDATES_CONSIDERED
CANDIDATES_CHANGED
CANDIDATES_DEFERRED

AFFECTED_PRODUCTION_FILES
AFFECTED_PUBLIC_SYMBOLS

NEW_TYPEDDICTS
NEW_TYPE_ALIASES
ANNOTATIONS_ADDED

ANY_CLASSIFICATION
DYNAMIC_BOUNDARIES_PRESERVED

HIGH_RISK_MODULES_TOUCHED
HIGH_RISK_MODULES_DEFERRED

PUBLIC_RUNTIME_CONTRACT_CHANGED
PUBLIC_CALL_COMPATIBILITY

MODEL_FIELD_EQUIVALENCE
MODEL_DEFAULT_EQUIVALENCE
SERIALIZED_OUTPUT_EQUIVALENCE

APPROVED_ARTIFACT_HASHES_UNCHANGED

TYPE_AND_CONTRACT_EQUIVALENCE_ARTIFACT
TYPE_AND_CONTRACT_EQUIVALENCE_ARTIFACT_SHA256
TYPE_AND_CONTRACT_EQUIVALENCE_ARTIFACT_DETERMINISM

TYPING_DIAGNOSTICS_BEFORE
TYPING_DIAGNOSTICS_AFTER

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
STATUS=V4_1_R2_IMPLEMENTATION_COMPLETE

ENTRY_GATE=PASS

BASELINE_TESTS=1424_PASS
FINAL_TESTS=>1424_PASS

PUBLIC_RUNTIME_CONTRACT_CHANGED=false
PUBLIC_CALL_COMPATIBILITY=PASS

MODEL_FIELD_EQUIVALENCE=PASS
MODEL_DEFAULT_EQUIVALENCE=PASS
SERIALIZED_OUTPUT_EQUIVALENCE=PASS

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

TYPE_AND_CONTRACT_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS

DYNAMIC_BOUNDARIES_PRESERVED=PASS

V4_CONTRACTS_UNCHANGED=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R2_READY_FOR_HUMAN_REVIEW

DECISION=V4_1_R2_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_1_R2
```

---

# Stop Conditions

STOP immediately if:

* an approved artifact hash changes;
* a public calling convention changes;
* dataclass/model field order changes;
* a default/default factory changes;
* serialized output changes;
* runtime validation changes;
* deterministic IDs change;
* tests cannot remain fully green;
* a candidate requires structural decomposition;
* a supposedly safe type narrowing is actually ambiguous.

Such work belongs to another controlled round.

---

# Final Stop

STOP after:

1. R2 implementation;
2. focused tests;
3. full regression;
4. equivalence artifact;
5. result document;
6. PROJECT_STATE pending human review.

Do NOT:

* approve R2;
* commit;
* push;
* start R3;
* restructure packages;
* perform responsibility decomposition;
* refactor high-risk orchestrators;
* begin V5;
* implement Plugin runtime.
