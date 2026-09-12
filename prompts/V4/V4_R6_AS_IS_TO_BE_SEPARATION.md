# LegacyMapper V4 — R6 AS_IS / TO_BE Separation

TASK=V4_R6_AS_IS_TO_BE_SEPARATION

MODE=DETERMINISTIC_TEMPORAL_SEPARATION_CONTRACT

IMPLEMENTATION_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false

PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false

GIT_PUSH_ALLOWED=false

---

# Objective

Implement the V4 temporal-state separation layer.

R6 must allow already-ingested and optionally classified material to be organized according to an **explicitly supplied temporal state**:

```text
AS_IS
TO_BE
HISTORICAL
UNSPECIFIED
```

where `UNSPECIFIED` means the existing `MaterialItem.temporal_state is None`.

R6 does NOT introduce a new fourth `TemporalState` enum value.

The approved R1 taxonomy remains:

```text
TemporalState.AS_IS
TemporalState.TO_BE
TemporalState.HISTORICAL
```

`None` remains the representation of unspecified temporal state.

The purpose of R6 is to preserve and separate these states deterministically without inferring them.

---

# Fundamental Boundary

The central invariants are:

```text
TEMPORAL STATE != TRUTH
TEMPORAL STATE != KNOWLEDGE NATURE
TEMPORAL STATE != SOURCE TYPE
TEMPORAL STATE != APPROVAL
TEMPORAL STATE != AUTHORITY
TEMPORAL STATE != CONFLICT
TEMPORAL STATE != GAP
TEMPORAL STATE != CANONICAL STATUS
```

and:

```text
AS_IS != "confirmed current truth"
TO_BE != "approved future design"
HISTORICAL != "obsolete"
None != "invalid"
```

R6 organizes temporal context.

It does not establish semantic truth or authority.

---

# Current Authorized Baseline

The Technical Lead has explicitly approved and formally closed:

```text
V4-R1
V4-R1.1
V4-R2
V4-R3
V4-R4
V4-R5
```

Expected repository state:

```text
latest_completed_round = V4-R5
latest_approved_round = V4-R5
current_round_in_progress = null
round_status = V4-R5_APPROVED
next = V4-R6

tests >= 842
readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do not reinterpret previous approvals.

---

# Required Reading

Before modifying anything read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_CONTRACT_FOUNDATION.md`
6. `docs/V4/V4_AI_HANDOVER.md`
7. `docs/V4/V4_PROPOSED_ROADMAP.md`
8. `docs/V4/V4_R1_KNOWLEDGE_DOMAIN_MODEL_RESULT.md`
9. `output/v4_r1/V4_KNOWLEDGE_DOMAIN_MODEL_CONTRACT.json`
10. `docs/V4/V4_R2_INPUT_SOURCE_CONTRACTS_RESULT.md`
11. `output/v4_r2/V4_INPUT_SOURCE_CONTRACTS.json`
12. `docs/V4/V4_R3_PROVENANCE_RESULT.md`
13. `output/v4_r3/V4_PROVENANCE_CONTRACT.json`
14. `docs/V4/V4_R4_HUMAN_SUPPLIED_MATERIAL_INGESTION_RESULT.md`
15. `output/v4_r4/V4_HUMAN_MATERIAL_INGESTION_CONTRACT.json`
16. `docs/V4/V4_R5_KNOWLEDGE_CLASSIFICATION_RESULT.md`
17. `output/v4_r5/V4_KNOWLEDGE_CLASSIFICATION_CONTRACT.json`
18. `docs/V4/V4_R5_CLOSURE_AND_VERSIONING_RESULT.md`
19. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
20. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Inspect:

```text
legacy_documenter/knowledge/domain/
legacy_documenter/knowledge/input/
legacy_documenter/knowledge/provenance/
legacy_documenter/knowledge/ingestion/
legacy_documenter/knowledge/classification/
```

Reuse approved domain types.

Do not create competing temporal concepts.

---

# Entry Gate

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=842 PASS
```

Run:

```text
python -m legacy_documenter.knowledge.readiness
```

Expected:

```text
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

Verify:

```text
V4_R5=APPROVED
PROJECT_STATE.next=V4-R6
```

If any entry gate fails:

STOP.

Do not implement R6.

---

# Reuse TemporalState

R1 already defines:

```text
TemporalState.AS_IS
TemporalState.TO_BE
TemporalState.HISTORICAL
```

Reuse this enum unchanged.

Do NOT create:

```text
CURRENT
FUTURE
OLD
LEGACY
ACTIVE
OBSOLETE
UNKNOWN
UNSPECIFIED
```

as competing `TemporalState` values.

For R6:

```text
temporal_state=None
```

means:

```text
UNSPECIFIED
```

only at the separation/projection level.

Do not mutate R1 merely to give `None` a name.

---

# Temporal Semantics

## AS_IS

Means:

```text
the material explicitly describes or belongs to the current/existing-state perspective
```

It does NOT mean:

```text
the statement is true
the implementation was verified
the evidence is authoritative
the material is approved
```

Example:

```text
A human supplied document may be explicitly marked AS_IS
while still being incomplete, disputed, or unapproved.
```

---

## TO_BE

Means:

```text
the material explicitly describes or belongs to an intended/target/future-state perspective
```

It does NOT mean:

```text
the target has been approved
the target will definitely be implemented
the target is canonical
```

---

## HISTORICAL

Means:

```text
the material explicitly belongs to a historical context
```

It does NOT automatically mean:

```text
obsolete
superseded
incorrect
irrelevant
```

Supersession belongs to later semantic relationships.

---

## UNSPECIFIED

Represented by:

```text
MaterialItem.temporal_state is None
```

Means:

```text
no temporal state has been explicitly established
```

It is a valid state.

Do not treat it as an error.

Do not guess a temporal state merely to eliminate it.

---

# No Temporal Inference

R6 must never infer temporal state from arbitrary content.

Forbidden:

```text
keyword matching
regex semantic inference
filename inference
folder inference
SourceType mapping
KnowledgeNature mapping
provenance-origin mapping
classifier mapping
LLM interpretation
```

Examples:

```text
DETERMINISTIC_CODE_FACT
    != automatically AS_IS

EXISTING_IMPLEMENTATION
    != automatically AS_IS

REQUIREMENT
    != automatically TO_BE

NEED
    != automatically TO_BE

HISTORICAL document folder
    != automatically HISTORICAL

APPROVED_DECISION
    != automatically TO_BE
```

unless the temporal state was explicitly supplied by an upstream authorized contract.

---

# Important EXISTING_IMPLEMENTATION Rule

R5 may classify a material as:

```text
KnowledgeNature.EXISTING_IMPLEMENTATION
```

R6 must NOT automatically assign:

```text
TemporalState.AS_IS
```

The nature and temporal state remain independent.

For example:

```text
nature = EXISTING_IMPLEMENTATION
temporal_state = HISTORICAL
```

may describe a previous implementation.

Likewise:

```text
nature = EXISTING_IMPLEMENTATION
temporal_state = None
```

is valid when temporal context was not explicitly established.

---

# Important REQUIREMENT Rule

A material classified:

```text
KnowledgeNature.REQUIREMENT
```

must NOT automatically become:

```text
TemporalState.TO_BE
```

A requirement may be:

```text
AS_IS
```

when documenting an existing/current requirement,

```text
TO_BE
```

when explicitly describing a target requirement,

```text
HISTORICAL
```

when recording an old requirement,

or:

```text
None
```

when temporal context is unspecified.

---

# SourceType Independence

Temporal state is independent of `SourceType`.

Explicit tests must prove no automatic mapping such as:

```text
DETERMINISTIC_CODE_FACT -> AS_IS
HUMAN_REQUIREMENT -> TO_BE
USER_STORY -> TO_BE
APPROVED_DECISION -> TO_BE
EXTERNAL_DOCUMENT -> HISTORICAL
```

R6 may only use the already-supplied `MaterialItem.temporal_state`.

---

# Classification Independence

R5 classification and R6 temporal state are orthogonal dimensions.

Conceptually:

```text
Material
├── SourceType
├── TemporalState
├── Provenance
└── Classification
    └── KnowledgeNature
```

Valid examples:

```text
ARCHITECTURE + AS_IS
ARCHITECTURE + TO_BE
ARCHITECTURE + HISTORICAL
ARCHITECTURE + None
```

and:

```text
NORM + AS_IS
NORM + TO_BE
NORM + HISTORICAL
NORM + None
```

R6 must not alter R5 `ClassificationRecord`.

---

# Temporal Separation Record

Introduce a small source-neutral record representing temporal placement/separation.

Conceptually:

```text
TemporalPlacement
    material_id
    temporal_state?
    bucket
```

Exact naming may differ if a clearer repository convention exists.

Preferred separation bucket model:

```text
AS_IS
TO_BE
HISTORICAL
UNSPECIFIED
```

The bucket is a deterministic projection of:

```text
MaterialItem.temporal_state
```

only.

Mapping:

```text
TemporalState.AS_IS       -> AS_IS
TemporalState.TO_BE       -> TO_BE
TemporalState.HISTORICAL  -> HISTORICAL
None                      -> UNSPECIFIED
```

This mapping is structural, not semantic inference.

---

# Do Not Duplicate Temporal Truth

Do not persist two independently editable temporal states.

If `TemporalPlacement` contains both:

```text
temporal_state
bucket
```

they must be mechanically consistent.

Prefer one canonical source plus deterministic projection.

Do not allow:

```text
temporal_state = AS_IS
bucket = TO_BE
```

---

# Temporal Separation Service

Provide a deterministic public capability conceptually equivalent to:

```text
separate(material) -> TemporalPlacement
```

and:

```text
separate_batch(materials) -> TemporalSeparationResult
```

It must read only:

```text
material.material_id
material.temporal_state
```

except for any harmless correlation fields explicitly justified by the contract.

It must not inspect material prose to determine temporal state.

---

# Batch Separation

Support deterministic separation of multiple materials.

The result should make it easy to obtain:

```text
AS_IS materials
TO_BE materials
HISTORICAL materials
UNSPECIFIED materials
```

Required:

* preserve deterministic ordering;
* no semantic grouping;
* no fuzzy deduplication;
* no content inspection;
* no material mutation;
* no loss of unspecified items.

If duplicate material IDs are accepted, define exact deterministic behavior.

Prefer rejecting conflicting duplicate identities rather than silently overwriting.

Exact duplicates may be idempotent if consistent with existing repository conventions.

Document the policy.

---

# Optional Classification Correlation

R6 may support correlation with R5 classifications by `material_id`.

For example:

```text
material_id = MAT-...
temporal_state = TO_BE

classification:
material_id = MAT-...
nature = ARCHITECTURE
```

This can allow later consumers to see:

```text
TO_BE ARCHITECTURE
```

without merging or mutating either record.

If implemented, correlation must be deterministic and optional.

Do not require a classification for temporal separation.

R6 must work for unclassified R4 materials.

---

# AS_IS vs TO_BE Is Not Conflict

This is a critical R6 invariant.

Given:

```text
Material A
temporal_state = AS_IS

Material B
temporal_state = TO_BE
```

R6 must NOT conclude:

```text
CONFLICT
CONTRADICTION
GAP
SUPERSEDED
```

even if their content differs.

R6 does not compare semantic content.

The difference may later represent:

```text
current state → target state
```

and R7 may determine whether a gap/conflict relationship is explicitly supported.

R6 only separates.

---

# HISTORICAL Is Not SUPERSEDED

Given:

```text
temporal_state = HISTORICAL
```

do not assign:

```text
KnowledgeStatus.SUPERSEDED
```

Historical context and supersession are different concepts.

R7/later lifecycle stages own explicit relationships.

---

# UNSPECIFIED Is Not MISSING Knowledge

Given:

```text
temporal_state = None
```

do not automatically assign:

```text
KnowledgeStatus.MISSING
KnowledgeStatus.UNRESOLVED
```

R6 may report:

```text
bucket = UNSPECIFIED
```

but does not change knowledge status.

---

# Temporal Comparison

R6 may provide deterministic structural comparison only.

Allowed:

```text
same temporal bucket?
different temporal bucket?
```

Not allowed:

```text
which one is correct?
which one supersedes the other?
which is newer?
which is authoritative?
which should become canonical?
```

Do not infer chronology from AS_IS / TO_BE / HISTORICAL.

---

# No Date Inference

R6 must not infer temporal state from:

```text
captured_at
approved_at
file timestamps
Git history
document dates
metadata dates
```

A 2020 document is not automatically HISTORICAL.

A document created today is not automatically AS_IS.

Dates and temporal semantic state are separate.

---

# Stable Identity

If temporal placement records receive IDs, use deterministic identity.

Suggested:

```text
TMP-
```

only if repository conventions support it.

Identity should depend only on semantically relevant fields, preferably:

```text
material_id
temporal bucket/state
```

Do not depend on:

```text
time
random UUID
memory address
machine path
dictionary order
```

Reuse `stable_id`.

---

# Deterministic Serialization

Canonical serialization must be deterministic.

For equivalent input:

```text
same material_id
same explicit temporal_state
```

produce byte-identical output.

Batch serialization must have documented canonical ordering.

---

# Security

Temporal processing treats all associated material as untrusted data.

R6 should not need to inspect prose.

Do not execute:

```text
content
metadata
references
rationale
classifier identity
```

No:

```text
eval
exec
dynamic import
shell command
document execution
```

If any descriptive metadata is copied into R6 output, reuse existing sanitizer.

Prefer not copying unnecessary material content at all.

---

# No External I/O

R6 must not:

```text
open source files
open document references
fetch URLs
scan directories
call APIs
query databases
call providers
```

It operates only on already-ingested in-memory/domain records.

---

# No AI Calls

Do not call:

```text
GitHub Copilot
Gemini
Claude
OpenAI
Ollama
any LLM/provider
```

Expected:

```text
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

---

# Suggested Implementation Location

Prefer:

```text
legacy_documenter/
└── knowledge/
    ├── domain/
    ├── input/
    ├── provenance/
    ├── ingestion/
    ├── classification/
    └── temporal/
```

Possible modules:

```text
temporal/
├── __init__.py
├── enums.py
├── models.py
├── service.py
└── contract_report.py
```

Use fewer modules if clearer.

Do not create architecture ceremony without value.

Follow established Python standard:

* PascalCase classes.
* snake_case modules/functions.
* type hints at significant boundaries.
* concise explanatory docstrings.
* simple Python.
* no unnecessary C# imitation.
* no unnecessary DI/frameworks.

---

# Contract Artifact

Generate:

`output/v4_r6/V4_TEMPORAL_SEPARATION_CONTRACT.json`

It must describe at minimum:

```text
contract_kind
schema_version

temporal_states
unspecified_representation
temporal_buckets

material_linkage
classification_independence
source_type_independence
provenance_independence

temporal_mapping
inference_policy

as_is_semantics
to_be_semantics
historical_semantics
unspecified_semantics

conflict_distinction
gap_distinction
supersession_distinction
approval_distinction
canonical_knowledge_distinction

identity_policy
ordering_policy
serialization_policy
batch_policy
duplicate_policy

AI_boundary
security_policy
external_io_policy
```

Explicitly include semantic statements equivalent to:

```text
TEMPORAL_STATE_IS_NOT_TRUTH
TEMPORAL_STATE_IS_NOT_APPROVAL
TEMPORAL_STATE_IS_NOT_KNOWLEDGE_NATURE
AS_IS_TO_BE_DIFFERENCE_IS_NOT_AUTOMATICALLY_CONFLICT
HISTORICAL_IS_NOT_AUTOMATICALLY_SUPERSEDED
UNSPECIFIED_IS_VALID
```

---

# Example Artifact

Generate:

`output/v4_r6/V4_TEMPORAL_SEPARATION_EXAMPLE.json`

Use only synthetic data.

Include at least four materials:

```text
Material A -> AS_IS
Material B -> TO_BE
Material C -> HISTORICAL
Material D -> None / UNSPECIFIED
```

Include classification correlation examples demonstrating the same nature in different temporal states:

```text
ARCHITECTURE + AS_IS
ARCHITECTURE + TO_BE
```

or equivalent.

Explicitly demonstrate:

```text
conflict = NOT_DETERMINED
gap = NOT_DETERMINED
superseded = NOT_DETERMINED
approval = NOT_PERFORMED
canonical_knowledge = NOT_GENERATED
```

Do not use real secrets or sensitive data.

---

# Required Tests

Add focused deterministic R6 tests.

At minimum:

## Temporal taxonomy

Reuse exactly the three existing R1 `TemporalState` values.

No competing temporal-state taxonomy.

`None` represented as `UNSPECIFIED` bucket.

---

## Mapping

Verify exact mapping:

```text
AS_IS -> AS_IS
TO_BE -> TO_BE
HISTORICAL -> HISTORICAL
None -> UNSPECIFIED
```

---

## No SourceType inference

Prove no automatic mapping from:

```text
DETERMINISTIC_CODE_FACT
HUMAN_REQUIREMENT
USER_STORY
APPROVED_DECISION
EXTERNAL_DOCUMENT
```

---

## No KnowledgeNature inference

Prove:

```text
EXISTING_IMPLEMENTATION != automatically AS_IS
REQUIREMENT != automatically TO_BE
NEED != automatically TO_BE
ARCHITECTURE != any automatic temporal state
```

---

## Classification independence

Same classification nature can correlate with:

```text
AS_IS
TO_BE
HISTORICAL
None
```

without changing classification.

---

## R4 independence

Unclassified R4 material can be temporally separated.

R5 classification is not required.

---

## No content inference

Use content containing phrases such as:

```text
"current implementation"
"future architecture"
"old historical system"
"target requirement"
```

with `temporal_state=None`.

All must remain:

```text
UNSPECIFIED
```

---

## No date inference

Provide different timestamps/dates in metadata/origin if available.

Temporal placement must remain based only on explicit `temporal_state`.

---

## AS_IS / TO_BE distinction

AS_IS and TO_BE are separated into different buckets.

No conflict object/status is created.

No semantic comparison occurs.

---

## Historical distinction

HISTORICAL does not create `SUPERSEDED`.

---

## Unspecified distinction

UNSPECIFIED does not create `MISSING` or `UNRESOLVED` knowledge status.

---

## Material immutability

Temporal separation does not mutate `MaterialItem`.

---

## Classification immutability

If correlation exists, R5 `ClassificationRecord` remains unchanged.

---

## Stable identity

Equivalent placements have identical deterministic IDs.

Different temporal states for the same synthetic material identity, if contractually representable, must not collide.

---

## Batch

All four buckets represented.

Deterministic ordering.

No item loss.

Duplicate policy tested.

---

## Security

Prompt-like or fake-secret material content is never interpreted/executed.

Prefer proving R6 does not copy or inspect content.

No raw secret appears in R6 artifact if content is not required.

---

## No I/O

No file/network/provider activity.

---

## Determinism

Generate contract twice independently.

Generate example twice independently.

Byte-identical outputs.

---

## Regression

All existing V3 and V4 tests remain PASS.

Expected:

```text
>842 PASS
```

Report actual count.

---

# Determinism Verification

Generate contract artifact twice independently.

Canonical bytes must match.

Generate example artifact twice independently.

Canonical bytes must match.

Compute SHA-256 values.

Required:

```text
CONTRACT_DETERMINISM=PASS
EXAMPLE_DETERMINISM=PASS
```

---

# Final Regression

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>842 PASS
```

Then:

```text
python -m legacy_documenter.knowledge.readiness
```

Expected:

```text
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

---

# Production Behavior

R6 must be additive.

Expected:

```text
V3_BEHAVIOR_CHANGED=false
V4_R1_BEHAVIOR_CHANGED=false
V4_R2_BEHAVIOR_CHANGED=false
V4_R3_BEHAVIOR_CHANGED=false
V4_R4_BEHAVIOR_CHANGED=false
V4_R5_BEHAVIOR_CHANGED=false
```

Do not modify earlier contracts simply to simplify R6.

If a genuine defect blocks implementation:

STOP and document it.

---

# PROJECT_STATE Update

After successful implementation and validation update:

`PROJECT_STATE.json`

to:

```text
latest_completed_round = V4-R6
latest_approved_round = V4-R5

current_round_in_progress =
"V4-R6 (pending Technical Lead review)"

round_status =
V4-R6_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R6

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do NOT mark R6 approved.

---

# Required Result

Create:

`docs/V4/V4_R6_AS_IS_TO_BE_SEPARATION_RESULT.md`

Report at minimum:

```text
STATUS
ENTRY_GATE
BASELINE_TESTS
FINAL_TESTS

TEMPORAL_TAXONOMY
TEMPORAL_STATES
UNSPECIFIED_REPRESENTATION
TEMPORAL_BUCKETS

TEMPORAL_PLACEMENT
MATERIAL_LINKAGE
TEMPORAL_MAPPING

SOURCE_TYPE_INFERENCE
KNOWLEDGE_NATURE_INFERENCE
CONTENT_INFERENCE
DATE_INFERENCE

CLASSIFICATION_INDEPENDENCE
PROVENANCE_INDEPENDENCE
APPROVAL_DISTINCTION

AS_IS_TO_BE_SEPARATION
CONFLICT_DETECTION
GAP_DETECTION

HISTORICAL_HANDLING
SUPERSESSION

UNSPECIFIED_HANDLING
KNOWLEDGE_STATUS_MUTATION

MATERIAL_MUTATION
CLASSIFICATION_MUTATION

IDENTITY
ORDERING
SERIALIZATION

BATCH_SEPARATION
DUPLICATE_POLICY

SANITIZATION
PROMPT_INJECTION_BOUNDARY
SECURITY
NO_IO

CONTRACT_ARTIFACT
CONTRACT_SHA256
EXAMPLE_ARTIFACT
EXAMPLE_SHA256

CONTRACT_DETERMINISM
EXAMPLE_DETERMINISM

V3_REGRESSION
V4_R1_REGRESSION
V4_R2_REGRESSION
V4_R3_REGRESSION
V4_R4_REGRESSION
V4_R5_REGRESSION

READINESS
AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE
PRODUCTION_BEHAVIOR_CHANGED
TECHNICAL_DEBT

DECISION
NEXT
```

Also include:

## Reused Components

## New Components

## Temporal Invariants

## AS_IS / TO_BE Semantics

## Historical Semantics

## Unspecified Semantics

## R4 / R5 Integration

## R7 Boundary

## Security Notes

## Out of Scope

---

# Expected Success State

```text
STATUS=V4_R6_AS_IS_TO_BE_SEPARATION_COMPLETE
ENTRY_GATE=PASS

BASELINE_TESTS=842_PASS
FINAL_TESTS=>842_PASS

TEMPORAL_TAXONOMY=REUSES_R1
TEMPORAL_STATES=AS_IS,TO_BE,HISTORICAL
UNSPECIFIED_REPRESENTATION=None
TEMPORAL_BUCKETS=AS_IS,TO_BE,HISTORICAL,UNSPECIFIED

TEMPORAL_MAPPING=PASS

SOURCE_TYPE_INFERENCE=NONE
KNOWLEDGE_NATURE_INFERENCE=NONE
CONTENT_INFERENCE=NONE
DATE_INFERENCE=NONE

CLASSIFICATION_INDEPENDENCE=PASS
PROVENANCE_INDEPENDENCE=PASS

AS_IS_TO_BE_SEPARATION=PASS
CONFLICT_DETECTION=NOT_PERFORMED
GAP_DETECTION=NOT_PERFORMED

HISTORICAL_HANDLING=PASS
SUPERSESSION=NOT_INFERRED

UNSPECIFIED_HANDLING=PASS
KNOWLEDGE_STATUS_MUTATION=NONE

MATERIAL_MUTATION=NONE
CLASSIFICATION_MUTATION=NONE

IDENTITY=DETERMINISTIC
ORDERING=DETERMINISTIC
SERIALIZATION=DETERMINISTIC

BATCH_SEPARATION=PASS
DUPLICATE_POLICY=DOCUMENTED_AND_TESTED

PROMPT_INJECTION_BOUNDARY=PASS
SECURITY=PASS
NO_IO=PASS

CONTRACT_ARTIFACT=VALID
EXAMPLE_ARTIFACT=VALID
CONTRACT_DETERMINISM=PASS
EXAMPLE_DETERMINISM=PASS

V3_REGRESSION=PASS
V4_R1_REGRESSION=PASS
V4_R2_REGRESSION=PASS
V4_R3_REGRESSION=PASS
V4_R4_REGRESSION=PASS
V4_R5_REGRESSION=PASS

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW
PRODUCTION_BEHAVIOR_CHANGED=V4_ADDITIVE_ONLY

DECISION=V4_R6_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R6
```

---

# Critical R7 Boundary

Do not accidentally implement R7 while separating temporal states.

These examples must remain unresolved semantically:

```text
AS_IS:
"The application uses architecture A."

TO_BE:
"The application should use architecture B."
```

R6 may report:

```text
different temporal buckets
```

R6 may NOT report:

```text
GAP
CONFLICT
CONTRADICTION
MIGRATION_REQUIRED
A_SUPERSEDED_BY_B
```

Likewise:

```text
AS_IS:
"Minimum income is 1,000,000."

TO_BE:
"Minimum income is 1,200,000."
```

is not automatically a contradiction.

It may simply describe an intended change.

R7 will own explicit representation of gap/conflict relationships.

---

# Out of Scope

Do NOT implement:

* R7 Gap and Conflict Representation;
* R8 Proposal Lifecycle;
* R9 Technical Lead Approval;
* R10 Canonical Knowledge Composition;
* R11 Human-Readable Projection;
* R12 Plugin-Facing Projection;
* R13 Final Regression/Security;
* R14 Manuals/Final Baseline;
* V5 language/framework/technology agnosticism.

Do not:

```text
infer temporal state
compare prose semantically
detect conflicts
detect gaps
infer supersession
infer chronology
approve knowledge
create proposals
create canonical knowledge
create KnowledgeStatement automatically
call LLM/provider
perform external I/O
```

---

# Stop Condition

STOP after:

1. implementing deterministic temporal separation;
2. supporting AS_IS, TO_BE, HISTORICAL and unspecified placement;
3. proving no temporal inference occurs;
4. proving R4/R5 independence;
5. proving AS_IS/TO_BE separation does not create conflict/gap semantics;
6. generating deterministic contract/example artifacts;
7. running all tests;
8. confirming readiness;
9. creating the R6 result;
10. updating `PROJECT_STATE.json` to pending Technical Lead review.

Do NOT:

* approve R6;
* commit;
* push;
* begin R7.

Wait for Technical Lead review.

Expected final state:

```text
V4_R6=READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R6
```
