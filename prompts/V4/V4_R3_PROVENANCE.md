# LegacyMapper V4 — R3 Provenance

TASK=V4_R3_PROVENANCE

MODE=DETERMINISTIC_PROVENANCE_IMPLEMENTATION

IMPLEMENTATION_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false

PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false

GIT_PUSH_ALLOWED=false

---

# Objective

Implement the deterministic V4 provenance and lineage layer.

V4-R3 must allow LegacyMapper to answer, deterministically:

```text
Where did this material/evidence/statement come from?

Which earlier artifacts contributed to it?

What transformations occurred between the original source
and the current representation?

Can the lineage be traced back to identifiable source material?

Is the lineage complete, partial, unresolved, or invalid?

Was any interpretation introduced along the way?
```

The conceptual flow is:

```text
SOURCE / ORIGIN
      ↓
MATERIAL
      ↓
EVIDENCE
      ↓
INTERPRETATION / PROPOSAL
      ↓
APPROVED KNOWLEDGE
```

Not every object exists yet in V4.

R3 must therefore implement a provenance model capable of representing this lifecycle incrementally without implementing later rounds prematurely.

R3 defines provenance infrastructure.

It does NOT perform actual human-document ingestion.

---

# Human Authorization / Current State

The Technical Lead has explicitly approved and formally closed:

`V4-R2 — Input / Source Contracts`

The repository is authoritative.

Expected current state:

```text
latest_completed_round = V4-R2
latest_approved_round = V4-R2
round_status = V4-R2_APPROVED
next = V4-R3
tests >= 726
readiness = READY
ai_knowledge_generated = false
```

Do not reinterpret previous approvals.

---

# Required Reading

Read before modifying anything:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_CONTRACT_FOUNDATION.md`
7. `docs/V4/V4_PROPOSED_ROADMAP.md`
8. `docs/V4/V4_R1_KNOWLEDGE_DOMAIN_MODEL_RESULT.md`
9. `output/v4_r1/V4_KNOWLEDGE_DOMAIN_MODEL_CONTRACT.json`
10. `docs/V4/V4_R2_INPUT_SOURCE_CONTRACTS_RESULT.md`
11. `docs/V4/V4_R2_CLOSURE_AND_VERSIONING_RESULT.md`
12. `output/v4_r2/V4_INPUT_SOURCE_CONTRACTS.json`
13. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
14. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Inspect existing implementation before designing anything:

* `legacy_documenter/knowledge/domain/`
* `legacy_documenter/knowledge/input/`
* `legacy_documenter/models/evidence.py`
* `legacy_documenter/documentation/evidence_catalog.py`
* `legacy_documenter/documentation/evidence_resume.py`
* `legacy_documenter/documentation/contracts.py`
* `legacy_documenter/documentation/human_review.py`
* existing traceability/readiness helpers;
* relevant V3/V4 tests.

Reuse existing deterministic concepts where semantics match.

Do not duplicate V3 traceability logic merely because it exists in an older namespace.

---

# Entry Gate

Before implementation run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=726 PASS
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
V3_BASELINE=VALID
V4_R1=APPROVED
V4_R1_1=APPROVED
V4_R2=APPROVED
PROJECT_STATE.next=V4-R3
```

If any entry condition fails:

STOP.

Do not implement R3.

---

# Core Principle

Provenance answers:

```text
WHERE DID THIS COME FROM?
```

It does NOT answer:

```text
IS THIS TRUE?
IS THIS APPROVED?
IS THIS CURRENT?
IS THIS CANONICAL?
```

Therefore:

```text
TRACEABLE != TRUE
TRACEABLE != APPROVED
TRACEABLE != AUTHORITATIVE
TRACEABLE != CANONICAL
```

A perfectly traceable incorrect statement remains incorrect.

A perfectly traceable AI interpretation remains an AI interpretation.

A perfectly traceable requirement does not prove implementation.

A perfectly traceable corporate standard does not prove compliance.

Do not collapse provenance with authority, approval, confidence, temporal state, or knowledge status.

---

# Provenance Must Be Source-Neutral

R3 provenance must work for:

```text
CODE_ONLY
CODE_AND_HUMAN_INFORMATION
HUMAN_INFORMATION_ONLY
PARTIAL_INFORMATION
```

No common provenance contract may require:

* source-code path;
* symbol;
* project;
* programming language;
* framework;
* repository scanner;
* code-analysis metadata.

Those may appear only when the originating source actually provides them.

The following must all be representable:

```text
VB.NET code
human requirement
user story
corporate standard
business context
technical constraint
project document
external document
approved decision
AI interpretation
unresolved information
future source types
```

without redesigning the provenance model.

---

# Preserve Existing V4 Semantics

Reuse R1/R2 concepts rather than creating competing equivalents:

From R1:

* `MaterialItem`
* `EvidenceRef`
* `Origin`
* `Provenance`
* `KnowledgeStatement`
* `SourceType`
* `TemporalState`

From R2:

* `SourceInput`
* `SourceContractPolicy`
* validated/normalized input semantics;
* scoped authority semantics;
* source contract catalog.

R3 may extend provenance capability where R1's initial `Provenance` model is insufficient.

Prefer backward-compatible extension/composition.

Do NOT redesign R1 merely for aesthetic reasons.

If a genuine R1 defect is found:

1. document it;
2. prove why R3 cannot satisfy its contract without correcting it;
3. make the smallest backward-compatible change;
4. preserve all existing R1/R2 tests.

---

# Provenance Levels

R3 must distinguish at least these concepts.

## Origin

The identifiable place/person/system/process from which material originated.

Examples:

```text
source repository
document
business ticket
Technical Lead
project documentation
corporate policy repository
external document
AI model/process
legacy scanner
```

Origin is not necessarily authority.

---

## Material Provenance

Links validated material to its source/origin.

Conceptually:

```text
SOURCE INPUT
    ↓
MATERIAL
```

R3 must support a material existing with:

* complete provenance;
* partial provenance;
* unresolved provenance.

Do not fabricate missing provenance merely to make lineage complete.

---

## Evidence Provenance

Links evidence back to material and/or another identifiable evidence source.

Conceptually:

```text
MATERIAL
    ↓
EVIDENCE
```

Evidence must be able to identify what material contributed to it.

---

## Derived Provenance

Represents an artifact derived from one or more previous artifacts.

Conceptually:

```text
A + B + C
    ↓
DERIVATION / TRANSFORMATION
    ↓
D
```

Examples:

```text
multiple requirements → summarized requirement set
code facts + project document → interpretation
business requirement + corporate standard → proposal
several evidence records → knowledge statement
```

R3 must represent multi-parent derivation.

Do not assume one source → one result.

---

# Provenance Graph

Implement a deterministic provenance graph or semantically equivalent lineage structure.

The exact internal representation is an implementation decision.

It must support:

```text
NODE
EDGE
```

A node represents an identifiable provenance participant.

An edge represents a lineage relationship/transformation.

Possible node kinds conceptually include:

```text
SOURCE
MATERIAL
EVIDENCE
STATEMENT
INTERPRETATION
PROPOSAL
KNOWLEDGE
```

Do not implement future lifecycle behavior merely because these node labels exist.

They are lineage categories, not workflow implementations.

If a smaller closed catalog is sufficient for R3, use it.

---

# Provenance Node Contract

A provenance node should minimally support concepts equivalent to:

```text
node_id
node_kind
source_type
reference
origin
metadata
```

Not every field must be required.

Node identity must be deterministic when derived from deterministic inputs.

Do not use random UUIDs for canonical deterministic lineage.

Do not use timestamps as identity.

---

# Provenance Edge Contract

A provenance edge must represent:

```text
parent/source node
child/derived node
relationship/transformation
```

It should support concepts equivalent to:

```text
edge_id
from_node_id
to_node_id
relationship
transformation
metadata
```

Possible relationships may include:

```text
ORIGINATES_FROM
MATERIALIZED_FROM
EVIDENCE_FROM
DERIVED_FROM
INTERPRETED_FROM
REFERENCES
```

Use a small closed catalog.

Do not create dozens of speculative relationship types.

R3 must define only relationships required for provenance semantics currently known.

---

# Direction

Choose and document ONE canonical edge direction.

Recommended:

```text
earlier/source
      ↓
later/derived
```

For example:

```text
Material → Evidence
Evidence → Statement
Evidence A ─┐
Evidence B ─┼→ Derived Statement
Evidence C ─┘
```

All traversal, cycle detection, root discovery, and serialization must use the same direction.

Do not mix directions between APIs.

---

# Transformation

Provenance must distinguish:

```text
LINK
```

from:

```text
TRANSFORMATION
```

A simple reference is not necessarily a semantic transformation.

Where transformation information is supplied, represent it explicitly.

Examples:

```text
DETERMINISTIC_EXTRACTION
NORMALIZATION
HUMAN_SUPPLIED
AI_INTERPRETATION
AGGREGATION
MANUAL_CORRECTION
```

Keep this catalog minimal and closed.

Do not claim a transformation occurred unless it is explicitly known.

Unknown transformation must remain unknown/unresolved rather than guessed.

---

# AI Interpretation Boundary

AI-derived content must remain visibly AI-derived throughout lineage.

Example:

```text
Material A
Material B
    ↓
AI_INTERPRETATION
    ↓
Statement X
```

A downstream node must not erase the fact that AI interpretation exists in its ancestry.

R3 must provide a deterministic way to answer:

```text
Does this node have AI-derived ancestry?
```

No real LLM call is required or allowed.

Use fixtures.

AI ancestry does not automatically invalidate knowledge.

It simply must remain traceable.

---

# Human Contribution Boundary

Human-originated material must remain identifiable as human-originated where provenance supplies that fact.

R3 must not replace a human contributor/origin with:

```text
LegacyMapper
```

merely because LegacyMapper normalized or linked the material.

Transformation processor and original origin are different concepts.

Preserve both where appropriate.

---

# Lineage Completeness

Define deterministic lineage completeness semantics.

At minimum support conceptually:

```text
COMPLETE
PARTIAL
UNRESOLVED
```

Optionally:

```text
INVALID
```

if useful for structurally broken lineage.

Suggested semantics:

## COMPLETE

Every required provenance relationship for the represented object is traceable to an accepted root/source.

## PARTIAL

Some provenance is known but at least one expected lineage element is absent.

## UNRESOLVED

The system explicitly knows provenance cannot currently be resolved.

## INVALID

The graph violates deterministic structural invariants.

Do not classify partial provenance as complete merely because one parent is known.

Do not reject legitimate uncertainty when PARTIAL/UNRESOLVED is the truthful state.

---

# Root Sources

The graph must provide deterministic root discovery.

A root is a provenance node that has no earlier lineage parent within the graph.

Root does NOT mean:

```text
authoritative
approved
true
canonical
```

It only means the lineage represented by the graph begins there.

Tests must enforce this distinction.

---

# Multi-Source Lineage

A derived artifact may depend on multiple parents.

Example:

```text
Requirement A ───────┐
Corporate Standard B ├──→ Proposed Statement X
Code Fact C ─────────┘
```

R3 must preserve all three parents.

No parent may be silently discarded.

Traversal must return the complete deterministic ancestry.

---

# Cycle Prevention

Provenance lineage must be acyclic.

Reject:

```text
A → B
B → A
```

and longer cycles:

```text
A → B → C → A
```

Cycle detection must be deterministic.

Self-reference:

```text
A → A
```

must fail.

Do not silently repair cycles.

---

# Dangling References

A provenance edge must not point to a nonexistent node.

Reject dangling:

```text
from_node
to_node
```

references.

If partial provenance is needed, represent it explicitly through status/completeness semantics rather than inventing nonexistent node IDs.

---

# Duplicate Handling

Reject or deterministically deduplicate duplicate nodes/edges according to a documented rule.

Preferred:

* duplicate node ID with different content → FAIL;
* exact duplicate edge → deterministically deduplicate or FAIL consistently;
* same semantic edge with incompatible metadata → FAIL.

Do not silently merge contradictory provenance.

---

# Stable Identity

Reuse existing stable deterministic ID conventions where possible.

Inspect:

* `stable_id`
* R1 ID helpers;
* R2 `new_source_input_id`.

If new helpers are required, use clear prefixes such as conceptually:

```text
PRN-
PED-
```

but follow repository naming conventions discovered during implementation.

IDs must not depend on:

* current time;
* random UUID;
* memory address;
* traversal order where order is semantically irrelevant;
* machine-specific paths unless the path itself is the actual evidence reference.

Equivalent normalized lineage must produce equivalent IDs.

---

# Deterministic Ordering

Serialization and traversal outputs must use deterministic ordering.

For example:

* nodes sorted by stable ID;
* edges sorted by stable ID;
* ancestry results stable;
* root results stable.

Input insertion order must not change canonical serialized output when semantics are identical.

Add explicit tests.

---

# Metadata

Provenance metadata must remain JSON-compatible.

Reuse R2 metadata validation if semantics match.

Do not accept arbitrary executable Python objects.

Do not use metadata to hide core provenance semantics that deserve explicit fields.

---

# Security

Provenance may contain:

* document references;
* paths;
* contributor information;
* source identifiers;
* sanitized material references.

Reuse existing sanitization behavior where appropriate.

Do not leak secrets through:

* provenance nodes;
* edges;
* metadata;
* exception messages;
* generated artifacts;
* reports.

Do not automatically open:

* local paths;
* URLs;
* SharePoint references;
* Bitbucket references;
* document references.

R3 stores/validates lineage references only.

No external I/O.

---

# Required Provenance Operations

Provide deterministic operations equivalent to:

```text
add_node
add_edge
get_node
parents_of
children_of
ancestors_of
descendants_of
roots_of
has_ai_ancestry
lineage_completeness
validate_graph
```

Exact method names may differ if repository conventions justify it.

Do not build a generic graph framework.

Build only what LegacyMapper provenance needs.

---

# R1 Provenance Compatibility

R1 introduced:

```text
Provenance(
    origin,
    material_ids,
    evidence_ids,
    contributor,
    notes
)
```

R3 must explicitly decide and document how this object relates to the new lineage representation.

Preferred possibilities:

```text
R1 Provenance = compact provenance summary
R3 ProvenanceGraph = full deterministic lineage
```

or another equally clear backward-compatible relationship.

Do NOT leave two ambiguous competing provenance systems.

The result document must state which representation is authoritative for which purpose.

---

# R2 SourceInput Compatibility

Demonstrate deterministic linkage:

```text
SourceInput
    ↓
Material provenance node
```

without implementing R4 ingestion.

A fixture/helper may show how a validated R2 input can be represented in lineage.

Do not create the actual ingestion orchestration.

No document parsing.

No filesystem scan.

No network retrieval.

---

# Provenance Contract Artifact

Generate:

`output/v4_r3/V4_PROVENANCE_CONTRACT.json`

It must be deterministic and machine-readable.

Include at minimum:

```text
contract_kind
schema_version
node_kinds
edge_relationships
transformation_types
completeness_states
edge_direction
identity_rules
cycle_policy
dangling_reference_policy
duplicate_policy
authority_distinction
approval_distinction
AI_ancestry_semantics
R1_provenance_relationship
R2_input_relationship
```

This artifact is a CONTRACT PROJECTION.

It is NOT canonical Knowledge Source content.

---

# Optional Example Fixture Artifact

If useful for proving the contract, a small deterministic example may be generated:

`output/v4_r3/V4_PROVENANCE_EXAMPLE.json`

Example:

```text
human requirement
        ┐
code fact
        ├→ evidence/derived statement
corporate standard
        ┘
```

The example must use fake/synthetic data only.

It must not be mistaken for canonical knowledge.

---

# Implementation Location

Prefer:

```text
legacy_documenter/
└── knowledge/
    ├── domain/
    ├── input/
    └── provenance/
```

Possible modules:

```text
provenance/
├── __init__.py
├── enums.py
├── models.py
├── graph.py
└── contract_report.py
```

This is guidance only.

Use fewer modules if simpler.

Do not create unnecessary abstractions.

Follow the established Python development standard.

---

# Required Tests

Add focused deterministic R3 tests.

Do not alter existing tests simply to make R3 pass.

At minimum cover:

## Basic lineage

```text
Source/Material → Evidence → Statement
```

Traversal works in both parent and child directions.

---

## Human-only provenance

A lineage consisting entirely of human-supplied information is valid.

No code fields required.

---

## Code-only provenance

A deterministic code-fact lineage is valid.

---

## Mixed provenance

Human requirement + code fact + corporate standard may all contribute to one derived node.

All parents remain visible.

---

## Partial provenance

Partial provenance remains PARTIAL.

No missing source is invented.

---

## Unresolved provenance

Explicit unresolved provenance remains UNRESOLVED.

---

## Roots

Root discovery is deterministic.

Roots are not automatically authoritative/approved.

---

## Multi-parent

All parents and full ancestry preserved.

---

## Cycle rejection

Self-cycle rejected.

Two-node cycle rejected.

Longer cycle rejected.

---

## Dangling edge rejection

Missing source node rejected.

Missing destination node rejected.

---

## Duplicate node

Same ID + same semantics handled deterministically.

Same ID + conflicting semantics rejected.

---

## Duplicate edge

Exact duplicate handled according to documented policy.

Conflicting duplicate rejected.

---

## Deterministic identity

Equivalent normalized lineage produces same IDs.

---

## Deterministic serialization

Equivalent graphs inserted in different orders serialize byte-identically.

---

## AI ancestry

Direct AI-derived node detected.

Indirect descendant of AI-derived node detected.

Non-AI lineage returns false.

AI ancestry remains detectable through multiple derivation levels.

---

## Human origin preservation

Normalization/transformation does not erase original human origin.

---

## Authority separation

Traceable source does not automatically become authoritative.

Root does not automatically become authoritative.

Complete lineage does not automatically become approved.

---

## R1 compatibility

Existing R1 `Provenance` semantics remain valid.

---

## R2 compatibility

Validated `SourceInput` can be represented in provenance without code when source type is human-only.

---

## Metadata validation

JSON-compatible metadata accepted.

Unsupported runtime objects rejected.

---

## Security

Fake secret fixture is sanitized/redacted according to existing rules.

Raw fake secret does not appear in:

* serialized graph;
* errors;
* contract artifact;
* example artifact.

---

## No I/O

No network/provider/file retrieval occurs.

---

## V3 regression

All existing V3 tests remain PASS.

---

## V4-R1 regression

All R1 tests remain PASS.

---

## V4-R2 regression

All R2 tests remain PASS.

Expected full suite:

```text
> 726 PASS
```

Report actual count.

---

# Determinism Verification

Generate:

`output/v4_r3/V4_PROVENANCE_CONTRACT.json`

twice independently.

Canonical bytes must match.

Compute SHA-256.

Expected:

```text
DETERMINISM=PASS
```

If an example artifact is generated, verify it too.

---

# Regression Verification

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=726 PASS
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

R3 is an additive V4 capability.

Expected:

```text
V3_BEHAVIOR_CHANGED=false
V4_R1_BEHAVIOR_CHANGED=false
V4_R2_BEHAVIOR_CHANGED=false
```

Do not change existing behavior unless a proven defect requires correction.

Any correction must be explicitly documented.

---

# Technical Debt

The V4 bootstrap identified relevant debt including:

* provider exception boundaries;
* cross-round helpers with distinct validated semantics;
* gradual narrow typing / nested JSON improvement.

Address debt only if directly touched by R3.

Do not perform unrelated refactoring.

Prefer reuse of R2 JSON-compatible metadata validation rather than creating another subtly different validator.

---

# PROJECT_STATE Update

After successful implementation and validation, update:

`PROJECT_STATE.json`

to represent:

```text
latest_completed_round = V4-R3
latest_approved_round = V4-R2
current_round_in_progress = V4-R3 (pending Technical Lead review)
round_status = V4-R3_READY_FOR_HUMAN_REVIEW
next = HUMAN_REVIEW_V4_R3
tests = <actual final count>
```

Do NOT mark R3 approved.

Only the Technical Lead may approve R3.

---

# Repository Continuity

Ensure all new R3:

* source;
* tests;
* prompt;
* result;
* contract artifact;
* small deterministic example artifact, if any;

are eligible for Git tracking.

Do NOT commit or push during this implementation round.

Versioning occurs only after Technical Lead approval using the established lifecycle.

---

# Required Result

Create:

`docs/V4/V4_R3_PROVENANCE_RESULT.md`

Report at minimum:

```text
STATUS
ENTRY_GATE
BASELINE_TESTS
FINAL_TESTS

PROVENANCE_MODEL
NODE_KINDS
EDGE_RELATIONSHIPS
TRANSFORMATION_TYPES
COMPLETENESS_STATES
EDGE_DIRECTION

SOURCE_NEUTRAL
CODE_ONLY
HUMAN_INFORMATION_ONLY
CODE_AND_HUMAN_INFORMATION
PARTIAL_INFORMATION

MULTI_PARENT_LINEAGE
ROOT_DISCOVERY
CYCLE_DETECTION
DANGLING_REFERENCE_VALIDATION
DUPLICATE_HANDLING

STABLE_IDENTITY
DETERMINISTIC_ORDERING
DETERMINISTIC_SERIALIZATION

AI_ANCESTRY
HUMAN_ORIGIN_PRESERVATION
AUTHORITY_SEPARATION
APPROVAL_SEPARATION

R1_PROVENANCE_RELATIONSHIP
R2_INPUT_RELATIONSHIP

METADATA_VALIDATION
SANITIZATION
SECURITY
NO_IO

CONTRACT_ARTIFACT
CONTRACT_SHA256
EXAMPLE_ARTIFACT
DETERMINISM

V3_REGRESSION
V4_R1_REGRESSION
V4_R2_REGRESSION

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

## Provenance Invariants

## R1 Provenance Compatibility

## R2 SourceInput Compatibility

## Security Notes

## Technical Debt

---

# Expected Success State

```text
STATUS=V4_R3_PROVENANCE_COMPLETE
ENTRY_GATE=PASS
SOURCE_NEUTRAL=PASS

CODE_ONLY=PASS
HUMAN_INFORMATION_ONLY=PASS
CODE_AND_HUMAN_INFORMATION=PASS
PARTIAL_INFORMATION=PASS

MULTI_PARENT_LINEAGE=PASS
ROOT_DISCOVERY=PASS
CYCLE_DETECTION=PASS
DANGLING_REFERENCE_VALIDATION=PASS
DUPLICATE_HANDLING=PASS

STABLE_IDENTITY=PASS
DETERMINISTIC_ORDERING=PASS
DETERMINISTIC_SERIALIZATION=PASS

AI_ANCESTRY=PASS
HUMAN_ORIGIN_PRESERVATION=PASS
AUTHORITY_SEPARATION=PASS
APPROVAL_SEPARATION=PASS

R1_PROVENANCE_RELATIONSHIP=DEFINED
R2_INPUT_RELATIONSHIP=DEFINED

METADATA_VALIDATION=PASS
SANITIZATION=PASS
SECURITY=PASS
NO_IO=PASS

CONTRACT_ARTIFACT=VALID
DETERMINISM=PASS

V3_REGRESSION=PASS
V4_R1_REGRESSION=PASS
V4_R2_REGRESSION=PASS

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW
PRODUCTION_BEHAVIOR_CHANGED=V4_ADDITIVE_ONLY

DECISION=V4_R3_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R3
```

---

# Stop Condition

STOP after:

1. R3 implementation;
2. tests;
3. deterministic contract generation;
4. result documentation;
5. `PROJECT_STATE.json` pending-review update.

Do NOT:

* approve R3;
* commit;
* push;
* start R4;
* ingest real human documents;
* call an LLM;
* generate canonical Knowledge Source;
* generate Plugin-facing knowledge.

Wait for Technical Lead review.
