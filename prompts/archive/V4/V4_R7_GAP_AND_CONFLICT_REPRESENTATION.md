# LegacyMapper V4 — R7 Gap and Conflict Representation

TASK=V4_R7_GAP_AND_CONFLICT_REPRESENTATION

MODE=DETERMINISTIC_KNOWLEDGE_RELATION_REPRESENTATION

IMPLEMENTATION_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false

PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false

GIT_PUSH_ALLOWED=false

---

# Objective

Implement the V4 relation layer required to represent explicit differences, gaps, conflicts, and temporal evolution between already-ingested knowledge materials.

R7 is about **representation**, not autonomous semantic detection.

The system must be able to express that two or more existing materials have an explicitly established relationship without:

* deciding which statement is true;
* deciding which statement is authoritative;
* deciding which statement is approved;
* modifying their classification;
* modifying their temporal state;
* promoting anything to canonical knowledge;
* creating an R8 proposal;
* using an LLM to infer relationships from prose.

The required conceptual distinctions are:

```text
DIFFERENCE
GAP
CONFLICT
TEMPORAL_EVOLUTION
```

These relationships must remain independent from:

```text
SourceType
KnowledgeNature
TemporalState
KnowledgeStatus
Approval
Authority
Provenance
Canonical Knowledge
```

---

# Fundamental Invariants

The central R7 rules are:

```text
DIFFERENCE != GAP
DIFFERENCE != CONFLICT

GAP != CONFLICT
CONFLICT != GAP

AS_IS + TO_BE != GAP automatically
AS_IS + TO_BE != CONFLICT automatically
AS_IS + TO_BE != TEMPORAL_EVOLUTION automatically

HISTORICAL + AS_IS != SUPERSESSION automatically
HISTORICAL + TO_BE != MIGRATION automatically

CONFLICT != FALSE
CONFLICT != REJECTED

GAP != MISSING
GAP != UNRESOLVED

RELATION != KNOWLEDGE STATUS
RELATION != APPROVAL
RELATION != AUTHORITY
RELATION != PROPOSAL
RELATION != CANONICAL KNOWLEDGE
```

Most importantly:

```text
R7 REPRESENTS EXPLICIT RELATIONSHIPS.

R7 DOES NOT DISCOVER THEM FROM NATURAL-LANGUAGE CONTENT.
```

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
V4-R6
```

Expected repository state:

```text
latest_completed_round = V4-R6
latest_approved_round = V4-R6

current_round_in_progress = null

round_status = V4-R6_APPROVED
next = V4-R7

tests >= 875
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
18. `docs/V4/V4_R6_AS_IS_TO_BE_SEPARATION_RESULT.md`
19. `output/v4_r6/V4_TEMPORAL_SEPARATION_CONTRACT.json`
20. `docs/V4/V4_R6_CLOSURE_AND_VERSIONING_RESULT.md`
21. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
22. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Inspect:

```text
legacy_documenter/knowledge/domain/
legacy_documenter/knowledge/input/
legacy_documenter/knowledge/provenance/
legacy_documenter/knowledge/ingestion/
legacy_documenter/knowledge/classification/
legacy_documenter/knowledge/temporal/
```

Reuse existing identity, domain, validation, and deterministic serialization conventions.

Do not modify existing V3 or approved V4 contracts merely to simplify R7.

---

# Entry Gate

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=875 PASS
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

Verify:

```text
V4_R6=APPROVED
PROJECT_STATE.next=V4-R7
```

If any entry gate fails:

STOP.

Do not implement R7.

---

# Scope

R7 introduces a source-neutral, deterministic representation for explicit relations between knowledge materials.

The minimum supported relationship kinds are:

```text
DIFFERENCE
GAP
CONFLICT
TEMPORAL_EVOLUTION
```

Exact class names may differ if repository conventions justify a clearer name.

The semantics must remain equivalent.

Do not add unrelated relationship families without a demonstrated R7 requirement.

---

# Relationship Semantics

## DIFFERENCE

Means:

```text
Two or more related materials express different values,
descriptions, states, constraints, or perspectives.
```

`DIFFERENCE` is deliberately neutral.

It does NOT mean:

```text
one is incorrect
one supersedes another
there is a gap
there is a conflict
there is an error
there is a required migration
```

Examples:

```text
Material A:
"The system uses architecture A."

Material B:
"The target architecture is B."
```

may be represented as:

```text
DIFFERENCE
```

if that relation is explicitly supplied.

It must not automatically become GAP or CONFLICT.

---

# GAP

A `GAP` represents an explicitly established separation between two states, capabilities, requirements, conditions, or expectations.

Conceptually:

```text
observed/provided condition
        versus
required/desired/expected condition
```

Examples may include:

```text
current capability vs required capability
current process vs expected process
available documentation vs required documentation
existing implementation vs required implementation
```

But R7 must NOT infer these semantics merely because the materials are:

```text
AS_IS
TO_BE
```

or because their textual contents differ.

A GAP must be explicitly declared by its caller/input.

`GAP` does NOT mean:

```text
KnowledgeStatus.MISSING
KnowledgeStatus.UNRESOLVED
error
failure
non-compliance
rejection
```

Those concepts remain separate.

---

# CONFLICT

A `CONFLICT` represents an explicitly established incompatibility between two or more applicable materials.

Examples may conceptually include:

```text
two simultaneously applicable standards requiring incompatible values
two requirements that cannot both be satisfied
two current descriptions claiming mutually incompatible system states
```

However:

R7 must NOT derive conflict by comparing prose.

A relationship must be explicitly supplied as `CONFLICT`.

`CONFLICT` does NOT determine:

```text
which participant is correct
which participant has greater authority
which participant should be rejected
which participant should become canonical
whether either statement is false
```

Resolution belongs to later workflow stages and Technical Lead authority.

---

# TEMPORAL_EVOLUTION

A `TEMPORAL_EVOLUTION` represents an explicitly declared evolution/change between knowledge states over time or between temporal perspectives.

For example:

```text
AS_IS architecture A
        ->
TO_BE architecture B
```

may be explicitly represented as temporal evolution.

But R6 temporal placement alone MUST NOT create this relation.

Likewise:

```text
HISTORICAL A
AS_IS B
```

does not automatically mean:

```text
A was superseded by B
```

unless a later explicit relationship or approved knowledge establishes that.

TEMPORAL_EVOLUTION does NOT automatically mean:

```text
migration required
supersession
approval
implementation completed
implementation planned
```

---

# Explicit Relation Creation

Provide a deterministic service that creates relationship records only from an explicit relation request.

Conceptually:

```text
create_relation(request) -> KnowledgeRelation
```

The request should provide at minimum:

```text
relation_kind
participant material ids
```

and optionally justified metadata such as:

```text
basis/reference
notes
evidence references
direction
```

only where consistent with existing V4 contracts.

Do not inspect material prose to decide `relation_kind`.

---

# Source Material

R7 relationships should reference existing materials by stable identity.

Preferred primary linkage:

```text
MaterialItem.material_id
```

Do not duplicate complete material payloads inside relation records.

Do not create a second material identity system.

If future layers need relationships over approved knowledge rather than materials, that can be added when the canonical Knowledge Source exists.

R7 operates at the current pre-canonical stage.

---

# Relationship Record

Introduce a small source-neutral record conceptually similar to:

```text
KnowledgeRelation
    relation_id
    relation_kind
    participant_ids
    direction?
    basis?
    evidence_refs?
    metadata?
```

Exact shape may differ if repository conventions justify it.

Required properties:

* deterministic identity;
* no approval fields;
* no canonical fields;
* no truth field;
* no winner/loser fields;
* no resolution field requiring R8/R9 behavior;
* no mutation of participants;
* source-neutral;
* code-optional;
* classification-optional;
* temporal-placement-optional.

---

# Directionality

Relationship direction must be explicit and deterministic.

Do not infer direction from:

```text
TemporalState
SourceType
KnowledgeNature
dates
participant ordering
content
```

Recommended semantics:

### Symmetric relations

```text
DIFFERENCE
CONFLICT
```

should normally be treated as symmetric.

Thus:

```text
A CONFLICT B
```

and:

```text
B CONFLICT A
```

must not accidentally become distinct semantic relationships merely because input order changed.

Canonicalize participant identity deterministically.

---

### Directional relations

```text
GAP
TEMPORAL_EVOLUTION
```

may be directional when explicitly declared.

For example:

```text
FROM = AS_IS material
TO   = TO_BE material
```

but only because the caller supplied that direction.

Do not infer:

```text
AS_IS -> TO_BE
```

from temporal state automatically.

If the contract allows directionless GAP, document it explicitly.

Prefer a simple unambiguous contract.

---

# Participant Cardinality

At minimum support relationships between two materials.

If support for more than two participants is simple and clean, it may be implemented.

Do not introduce unnecessary graph complexity.

Regardless of cardinality:

```text
a relation cannot reference zero or one unique participant
```

unless a specific relation type can justify it.

For the four R7 kinds, prefer:

```text
>=2 unique participants
```

---

# Self Relationship

Reject:

```text
A CONFLICT A
A DIFFERENCE A
A GAP A
A TEMPORAL_EVOLUTION A
```

unless there is an exceptionally strong domain reason.

For R7, there is no such requirement.

Expected:

```text
SELF_RELATION=REJECTED
```

---

# Duplicate Relationships

Define deterministic duplicate behavior.

Recommended:

For symmetric relationships:

```text
CONFLICT(A,B)
CONFLICT(B,A)
```

represent the same relation.

Likewise:

```text
DIFFERENCE(A,B)
DIFFERENCE(B,A)
```

For directional relationships:

```text
GAP(A->B)
```

is distinct from:

```text
GAP(B->A)
```

and:

```text
TEMPORAL_EVOLUTION(A->B)
```

is distinct from:

```text
TEMPORAL_EVOLUTION(B->A)
```

Exact duplicate relations may be idempotent.

Conflicting duplicate identity/semantics must be rejected rather than silently overwritten.

Document and test the policy.

---

# Stable Identity

Use deterministic IDs.

Suggested prefix:

```text
REL-
```

if compatible with repository conventions.

Reuse:

```text
stable_id
```

Identity should depend only on semantically relevant canonical fields.

For symmetric relations:

```text
relation_kind
canonical sorted participant ids
```

For directional relations:

```text
relation_kind
from participant ids
to participant ids
```

Do not include:

```text
current time
random UUID
memory address
machine path
input dictionary ordering
non-semantic descriptive notes
```

unless a field truly changes the semantic identity of the relation.

---

# Relation Basis

If useful, allow a small explicit basis/method field.

For example:

```text
EXPLICIT
DETERMINISTIC_RULE
AI_PROPOSED
UNRESOLVED
```

But do NOT let this accidentally implement R8.

If added:

* R7 itself should only produce deterministic/explicit relationships during this round;
* `AI_PROPOSED` is representable for future compatibility but no AI calls occur;
* relation method does not imply approval;
* relation method does not imply truth.

If this adds unnecessary complexity, omit it and document the source of relation creation through existing metadata/provenance structures instead.

Prefer simplicity.

---

# Evidence and Provenance

R7 must not invent evidence.

If a relationship has explicit evidence references:

* preserve them;
* validate identity;
* do not claim evidence proves more than its declared relation;
* do not change R3 provenance.

A relation may exist with:

```text
explicit caller declaration
```

without manufacturing fake provenance.

If integration with `ProvenanceGraph` is implemented, it must be additive and explicit.

Do not mutate historical provenance automatically.

Do not create artificial provenance chains merely to make the relation look complete.

---

# R5 Classification Independence

Relationship type must not be inferred from `KnowledgeNature`.

Forbidden examples:

```text
REQUIREMENT + REQUIREMENT -> CONFLICT
EXISTING_IMPLEMENTATION + REQUIREMENT -> GAP
ARCHITECTURE + ARCHITECTURE -> DIFFERENCE
NORM + NORM -> CONFLICT
```

All could potentially have those relationships, but only if explicitly established.

R7 may correlate classification by `material_id`.

It must not require classification.

It must not mutate `ClassificationRecord`.

---

# R6 Temporal Independence

Relationship kind must not be inferred from `TemporalState` or `TemporalBucket`.

Forbidden:

```text
AS_IS + TO_BE -> GAP
AS_IS + TO_BE -> TEMPORAL_EVOLUTION
HISTORICAL + AS_IS -> SUPERSEDED
TO_BE + TO_BE with different values -> CONFLICT
```

Temporal state may be included in a read-only correlated view if useful.

But it is not an inference rule.

---

# Important Difference vs Gap Example

Given:

```text
A:
temporal_state = AS_IS
value = 1,000,000

B:
temporal_state = TO_BE
value = 1,200,000
```

R7 must NOT automatically conclude:

```text
GAP
```

Possible explicit relationships could be:

```text
DIFFERENCE
TEMPORAL_EVOLUTION
GAP
```

depending on externally supplied meaning.

Without an explicit relation request:

```text
NO_RELATION
```

is correct.

---

# Important Difference vs Conflict Example

Given:

```text
Requirement A:
"Use authentication mechanism X."

Requirement B:
"Use authentication mechanism Y."
```

R7 must not automatically conclude:

```text
CONFLICT
```

They might:

* apply to different contexts;
* coexist;
* be alternatives;
* represent evolution;
* actually conflict.

Only explicit relation input determines the R7 relationship.

---

# Important Conflict Semantics

If:

```text
CONFLICT(A,B)
```

is explicitly supplied, R7 records:

```text
A and B are represented as conflicting according to the supplied relation.
```

It does NOT record:

```text
A is wrong
B is wrong
A wins
B wins
A is obsolete
B is authoritative
A must be rejected
B becomes canonical
```

Conflict resolution is outside R7.

---

# Important Gap Semantics

If:

```text
GAP(A -> B)
```

is explicitly supplied, R7 records the gap relationship.

It does NOT automatically create:

```text
task
requirement
proposal
migration plan
implementation action
approval request
```

R8 and later workflow stages own proposals/actions.

---

# KnowledgeStatus Independence

R1 includes statuses such as:

```text
CONFLICTING
MISSING
UNRESOLVED
SUPERSEDED
```

R7 relationships MUST NOT automatically mutate a participant `KnowledgeStatement` or assign those statuses.

Examples:

```text
CONFLICT relation
    != automatic KnowledgeStatus.CONFLICTING

GAP relation
    != automatic KnowledgeStatus.MISSING

TEMPORAL_EVOLUTION
    != automatic KnowledgeStatus.SUPERSEDED
```

These concepts may later become related through explicit lifecycle rules.

R7 itself only represents relations.

---

# Approval Independence

A relation record does not mean that the Technical Lead approved:

```text
the relation
the participating materials
the semantic conclusion
a resolution
canonical incorporation
```

Do not add:

```text
approved=true
canonical=true
accepted=true
```

to the relation merely because it exists.

R9 owns Technical Lead approval.

---

# R8 Boundary

Do not create Proposal objects.

A relation may later be used by R8 to generate/propose:

```text
resolution
correction
selection
reconciliation
migration
additional-information request
```

but R7 does not do this.

R7 output is relational evidence/context for later stages.

---

# Relation Collection / Repository

If helpful, provide a deterministic in-memory collection/service supporting:

```text
add
get
list
by_kind
relations_for(material_id)
```

Avoid creating a database or persistence layer.

No external storage is required.

Canonical serialization to JSON-compatible structures is sufficient.

Do not over-engineer a graph database.

---

# No Semantic Detection

R7 must never determine relation type through:

```text
keyword matching
regex
text similarity
embeddings
LLM
classifier
filename
directory
SourceType
KnowledgeNature
TemporalState
dates
participant ordering
```

R7 must not compare natural-language text to discover:

```text
conflict
gap
difference
evolution
```

The relation kind must come from explicit structured input.

---

# No AI Calls

Do not call:

```text
Claude
GitHub Copilot
Gemini
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

# No External I/O

The R7 relation module must not:

```text
read source files
read referenced documents
fetch URLs
scan directories
query databases
invoke Git
call providers
```

It operates only on already-existing in-memory/domain records and explicit relation requests.

Contract/example generation may write the required deterministic artifacts through established repository mechanisms.

---

# Security

All relation input must be treated as untrusted data.

Prefer relation records containing only:

```text
stable ids
enum values
small sanitized notes/metadata when genuinely useful
```

If notes/metadata are supported:

reuse existing sanitization and JSON-compatible metadata validation.

Do not execute or interpret text.

No:

```text
eval
exec
dynamic imports
shell execution
template execution
```

Prompt-injection text inside notes must remain inert.

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
    ├── temporal/
    └── relations/
```

Possible modules:

```text
relations/
├── __init__.py
├── enums.py
├── models.py
├── service.py
└── contract_report.py
```

Use fewer files if clearer.

Follow:

`docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

In particular:

* classes `PascalCase`;
* modules/functions `snake_case`;
* type hints at significant/public boundaries;
* concise explanatory docstrings;
* one significant responsibility per class/module where useful;
* no unnecessary C# imitation;
* no unnecessary framework/DI ceremony;
* deterministic rules in straightforward Python.

---

# Contract Artifact

Generate:

`output/v4_r7/V4_GAP_CONFLICT_RELATION_CONTRACT.json`

It must document at minimum:

```text
contract_kind
schema_version
module

relation_kinds

difference_semantics
gap_semantics
conflict_semantics
temporal_evolution_semantics

explicit_relation_policy
semantic_detection_policy

participant_model
participant_cardinality
self_relation_policy

directionality_policy
symmetric_relation_policy
directional_relation_policy

duplicate_policy
identity_policy
ordering_policy
serialization_policy

source_type_independence
classification_independence
temporal_independence
provenance_independence

knowledge_status_distinction
approval_distinction
authority_distinction
proposal_distinction
canonical_knowledge_distinction

AI_boundary
security_policy
external_io_policy
```

Include semantic statements equivalent to:

```text
DIFFERENCE_IS_NOT_GAP
DIFFERENCE_IS_NOT_CONFLICT
GAP_IS_NOT_CONFLICT
AS_IS_TO_BE_IS_NOT_AUTOMATICALLY_GAP
AS_IS_TO_BE_IS_NOT_AUTOMATICALLY_CONFLICT
AS_IS_TO_BE_IS_NOT_AUTOMATICALLY_TEMPORAL_EVOLUTION
CONFLICT_DOES_NOT_SELECT_A_WINNER
GAP_DOES_NOT_CREATE_A_PROPOSAL
RELATION_DOES_NOT_IMPLY_APPROVAL
RELATION_DOES_NOT_MUTATE_KNOWLEDGE_STATUS
```

---

# Example Artifact

Generate:

`output/v4_r7/V4_GAP_CONFLICT_RELATION_EXAMPLE.json`

Use synthetic data only.

Include at minimum:

## Example 1 — neutral difference

```text
Material A
Material B

relation = DIFFERENCE
```

Show:

```text
gap = NOT_INFERRED
conflict = NOT_INFERRED
approval = NOT_PERFORMED
```

---

## Example 2 — explicit gap

```text
AS_IS material
TO_BE material

explicit relation = GAP
direction explicitly supplied
```

Show:

```text
gap = REPRESENTED
conflict = NOT_INFERRED
proposal = NOT_CREATED
```

---

## Example 3 — explicit conflict

Two synthetic applicable requirements:

```text
explicit relation = CONFLICT
```

Show:

```text
winner = NOT_SELECTED
truth = NOT_DETERMINED
approval = NOT_PERFORMED
```

---

## Example 4 — temporal evolution

```text
historical/current or current/target synthetic materials
explicit relation = TEMPORAL_EVOLUTION
```

Show:

```text
supersession = NOT_INFERRED
migration = NOT_INFERRED
```

---

## Example 5 — no relation from temporal separation alone

```text
A = AS_IS
B = TO_BE
```

No explicit relationship request.

Show:

```text
relation = NONE
gap = NOT_INFERRED
conflict = NOT_INFERRED
temporal_evolution = NOT_INFERRED
```

---

# Required Tests

Add focused deterministic R7 tests.

At minimum:

## Relation taxonomy

Verify exactly the intended R7 relation kinds:

```text
DIFFERENCE
GAP
CONFLICT
TEMPORAL_EVOLUTION
```

No accidental mapping to `KnowledgeStatus`.

---

## Explicit creation only

Creating an explicit relation produces the requested kind.

No relation is created merely because two materials exist.

---

## No content inference

Materials with contradictory-looking phrases must not create relationships automatically.

Examples:

```text
"Use architecture A"
"Do not use architecture A"
```

and:

```text
"Minimum income = 1,000,000"
"Minimum income = 1,200,000"
```

Without an explicit request:

```text
NO_RELATION
```

---

## No SourceType inference

Test representative combinations such as:

```text
HUMAN_REQUIREMENT + HUMAN_REQUIREMENT
CORPORATE_STANDARD + PROJECT_DOCUMENT
DETERMINISTIC_CODE_FACT + HUMAN_REQUIREMENT
APPROVED_DECISION + BUSINESS_REQUIREMENT
```

No automatic GAP/CONFLICT/DIFFERENCE/EVOLUTION.

---

## No KnowledgeNature inference

Prove no automatic relations from:

```text
REQUIREMENT + REQUIREMENT
ARCHITECTURE + ARCHITECTURE
EXISTING_IMPLEMENTATION + REQUIREMENT
NORM + CONSTRAINT
```

---

## No TemporalState inference

Prove:

```text
AS_IS + TO_BE
HISTORICAL + AS_IS
HISTORICAL + TO_BE
TO_BE + TO_BE
```

do not automatically create any R7 relationship.

---

## Difference semantics

An explicitly requested DIFFERENCE creates DIFFERENCE only.

It must not mutate participants or generate GAP/CONFLICT.

---

## Gap semantics

An explicit GAP creates GAP.

It must not create:

```text
MISSING
UNRESOLVED
proposal
task
migration
```

---

## Conflict semantics

An explicit CONFLICT creates CONFLICT.

It must not:

```text
select winner
select loser
assign truth
assign authority
reject participant
approve participant
```

---

## Temporal evolution semantics

Explicit TEMPORAL_EVOLUTION is representable.

It must not infer:

```text
SUPERSEDED
migration
approval
implementation completion
```

---

## Symmetry

Verify:

```text
CONFLICT(A,B) == CONFLICT(B,A)
```

semantically/identically according to the contract.

Likewise:

```text
DIFFERENCE(A,B) == DIFFERENCE(B,A)
```

---

## Directionality

If GAP is directional:

```text
GAP(A->B) != GAP(B->A)
```

If TEMPORAL_EVOLUTION is directional:

```text
EVOLUTION(A->B) != EVOLUTION(B->A)
```

Direction must be explicit.

---

## Self relation

Reject all four relation kinds when only one unique participant exists.

---

## Duplicate policy

Test exact duplicate idempotency.

Test symmetric reversed duplicate behavior.

Test directional reversed relation distinction.

Reject conflicting duplicate semantics rather than silently overwriting.

---

## Stable identity

Equivalent semantic relations must receive identical deterministic IDs.

Participant input ordering must not alter symmetric relation identity.

Directional orientation must alter directional relation identity.

---

## Material immutability

Creating/querying relations does not mutate `MaterialItem`.

---

## Classification immutability

Correlation does not mutate R5 `ClassificationRecord`.

---

## Temporal immutability

Correlation does not mutate R6 `TemporalPlacement`.

---

## Knowledge status independence

No R7 operation automatically sets:

```text
CONFLICTING
MISSING
UNRESOLVED
SUPERSEDED
```

---

## Approval independence

Relation records contain no implicit approval/canonical promotion.

---

## Batch behavior

If batch creation is implemented:

* deterministic ordering;
* failure isolation;
* exact duplicate policy;
* no item loss;
* deterministic accepted/rejected results.

---

## Security

Prompt injection and fake secret inside optional notes/metadata remain inert and sanitized.

No untrusted payload is executed.

---

## No I/O

No file/network/database/provider I/O.

---

## Determinism

Generate contract twice independently.

Generate example twice independently.

Byte-identical canonical outputs.

---

## Regression

All prior tests remain PASS.

Expected:

```text
>875 PASS
```

Report actual count.

---

# Deterministic Serialization

Canonical relation serialization must be stable.

For symmetric relation participants:

```text
canonicalize participant ordering
```

before identity/serialization.

For directional relations:

```text
preserve explicit direction
```

while keeping deterministic ordering inside each side if collections are supported.

Never depend on Python set/dict iteration order for semantic output.

---

# Determinism Verification

Generate:

`V4_GAP_CONFLICT_RELATION_CONTRACT.json`

twice independently.

Required:

```text
CONTRACT_DETERMINISM=PASS
```

Generate:

`V4_GAP_CONFLICT_RELATION_EXAMPLE.json`

twice independently.

Required:

```text
EXAMPLE_DETERMINISM=PASS
```

Compute SHA-256 values for both.

---

# Final Regression

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>875 PASS
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

R7 must be additive.

Expected:

```text
V3_BEHAVIOR_CHANGED=false
V4_R1_BEHAVIOR_CHANGED=false
V4_R2_BEHAVIOR_CHANGED=false
V4_R3_BEHAVIOR_CHANGED=false
V4_R4_BEHAVIOR_CHANGED=false
V4_R5_BEHAVIOR_CHANGED=false
V4_R6_BEHAVIOR_CHANGED=false
```

Do not modify earlier contracts solely for convenience.

If an actual defect blocks R7:

STOP and document it.

---

# PROJECT_STATE Update

After successful implementation and validation update:

`PROJECT_STATE.json`

to:

```text
latest_completed_round = V4-R7
latest_approved_round = V4-R6

current_round_in_progress =
"V4-R7 (pending Technical Lead review)"

round_status =
V4-R7_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R7

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do NOT mark R7 approved.

---

# Required Result

Create:

`docs/V4/V4_R7_GAP_AND_CONFLICT_REPRESENTATION_RESULT.md`

Report at minimum:

```text
STATUS
ENTRY_GATE
BASELINE_TESTS
FINAL_TESTS

RELATION_TAXONOMY
RELATION_KINDS

RELATION_RECORD
PARTICIPANT_MODEL
PARTICIPANT_CARDINALITY

DIFFERENCE_SEMANTICS
GAP_SEMANTICS
CONFLICT_SEMANTICS
TEMPORAL_EVOLUTION_SEMANTICS

EXPLICIT_RELATION_POLICY
SEMANTIC_DETECTION

SOURCE_TYPE_INFERENCE
KNOWLEDGE_NATURE_INFERENCE
TEMPORAL_STATE_INFERENCE
CONTENT_INFERENCE
DATE_INFERENCE

SYMMETRIC_RELATIONS
DIRECTIONAL_RELATIONS
SELF_RELATION_POLICY
DUPLICATE_POLICY

IDENTITY
ORDERING
SERIALIZATION

MATERIAL_MUTATION
CLASSIFICATION_MUTATION
TEMPORAL_MUTATION

KNOWLEDGE_STATUS_MUTATION
APPROVAL_DISTINCTION
AUTHORITY_DISTINCTION
PROPOSAL_DISTINCTION
CANONICAL_KNOWLEDGE_DISTINCTION

PROVENANCE_INTEGRATION

BATCH_RELATIONS

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
V4_R6_REGRESSION

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

Also include sections:

## Reused Components

## New Components

## Relation Invariants

## Difference Semantics

## Gap Semantics

## Conflict Semantics

## Temporal Evolution Semantics

## R5 / R6 Integration

## R8 Boundary

## Security Notes

## Out of Scope

---

# Expected Success State

```text
STATUS=V4_R7_GAP_AND_CONFLICT_REPRESENTATION_COMPLETE
ENTRY_GATE=PASS

BASELINE_TESTS=875_PASS
FINAL_TESTS=>875_PASS

RELATION_KINDS=DIFFERENCE,GAP,CONFLICT,TEMPORAL_EVOLUTION

EXPLICIT_RELATION_POLICY=REQUIRED
SEMANTIC_DETECTION=NOT_PERFORMED

SOURCE_TYPE_INFERENCE=NONE
KNOWLEDGE_NATURE_INFERENCE=NONE
TEMPORAL_STATE_INFERENCE=NONE
CONTENT_INFERENCE=NONE
DATE_INFERENCE=NONE

DIFFERENCE_SEMANTICS=PASS
GAP_SEMANTICS=PASS
CONFLICT_SEMANTICS=PASS
TEMPORAL_EVOLUTION_SEMANTICS=PASS

SYMMETRIC_RELATIONS=DIFFERENCE,CONFLICT
DIRECTIONAL_RELATIONS=GAP,TEMPORAL_EVOLUTION
SELF_RELATION_POLICY=REJECTED

IDENTITY=DETERMINISTIC
ORDERING=DETERMINISTIC
SERIALIZATION=DETERMINISTIC

MATERIAL_MUTATION=NONE
CLASSIFICATION_MUTATION=NONE
TEMPORAL_MUTATION=NONE

KNOWLEDGE_STATUS_MUTATION=NONE
APPROVAL_DISTINCTION=PASS
AUTHORITY_DISTINCTION=PASS
PROPOSAL_DISTINCTION=PASS
CANONICAL_KNOWLEDGE_DISTINCTION=PASS

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
V4_R6_REGRESSION=PASS

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW
PRODUCTION_BEHAVIOR_CHANGED=V4_ADDITIVE_ONLY

DECISION=V4_R7_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R7
```

---

# Critical R8 Boundary

R7 must not resolve the relations it represents.

Example:

```text
CONFLICT:
A = "Authentication must use X"
B = "Authentication must use Y"
```

R7 ends at:

```text
CONFLICT(A,B)
```

It must not produce:

```text
SELECT_A
SELECT_B
REJECT_A
REJECT_B
CHANGE_REQUIREMENT
ASK_TECHNICAL_LEAD
CREATE_MIGRATION
CREATE_DECISION
```

Those are proposals/actions and belong to R8 or later.

Likewise:

```text
GAP(A->B)
```

must not automatically become:

```text
IMPLEMENT_B
CREATE_TASK
CREATE_PROJECT
REQUEST_BUDGET
MIGRATE_A_TO_B
```

R8 owns the proposal lifecycle.

---

# Out of Scope

Do NOT implement:

* autonomous semantic gap detection;
* autonomous semantic conflict detection;
* embeddings/similarity;
* LLM conflict analysis;
* relation resolution;
* winner/loser selection;
* Technical Lead decision workflow;
* proposal creation;
* corrective action generation;
* migration planning;
* task generation;
* canonical Knowledge Source composition;
* human-readable projection;
* Plugin projection;
* R8 Proposal Lifecycle;
* R9 Technical Lead Approval;
* R10 Canonical Knowledge Composition;
* R11 Human-Readable Projection;
* R12 Plugin-Facing Output;
* R13 Regression/Security closure;
* R14 Manuals/Final Baseline;
* V5 technology/language/framework agnosticism.

---

# Stop Condition

STOP after:

1. implementing deterministic explicit relationship representation;
2. supporting DIFFERENCE, GAP, CONFLICT, and TEMPORAL_EVOLUTION;
3. proving no semantic auto-detection occurs;
4. proving SourceType / KnowledgeNature / TemporalState independence;
5. proving participant records are not mutated;
6. proving conflict does not select a winner;
7. proving gap does not create a proposal;
8. generating deterministic contract/example artifacts;
9. running all tests;
10. confirming readiness;
11. creating the R7 result;
12. updating `PROJECT_STATE.json` to pending Technical Lead review.

Do NOT:

* approve R7;
* commit;
* push;
* begin R8.

Wait for Technical Lead review.

Expected final state:

```text
V4_R7=READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R7
```
