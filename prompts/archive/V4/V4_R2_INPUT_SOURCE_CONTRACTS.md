# LegacyMapper V4 — R2 Input / Source Contracts

TASK=V4_R2_INPUT_SOURCE_CONTRACTS

MODE=DETERMINISTIC_CONTRACT_IMPLEMENTATION

IMPLEMENTATION_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false

PROVIDER_CALLS_ALLOWED=false

---

# Objective

Implement the deterministic V4 input/source contract layer.

This round defines how LegacyMapper represents, validates, normalizes, and safely accepts material coming from every approved V4 `SourceType`.

It establishes the boundary:

```text
EXTERNAL / RAW MATERIAL
        ↓
INPUT SOURCE CONTRACT
        ↓
VALIDATED MATERIAL
        ↓
future V4 ingestion / provenance / classification
```

This round DOES NOT perform the future ingestion workflow itself.

It defines the contracts that later rounds will consume.

The implementation must support all V4 operating scenarios:

* CODE_ONLY
* CODE_AND_HUMAN_INFORMATION
* HUMAN_INFORMATION_ONLY
* PARTIAL_INFORMATION

Source code is OPTIONAL.

No common V4 input contract may require:

* repository path;
* source-code file;
* symbol;
* project;
* programming language;
* framework;
* technology;
* scanner metadata.

Code-specific metadata may be required only when the selected source contract semantically represents `DETERMINISTIC_CODE_FACT`.

---

# Required Reading

Read before changing anything:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_CONTRACT_FOUNDATION.md`
7. `docs/V4/V4_PROPOSED_ROADMAP.md`
8. `docs/V4/V4_R1_KNOWLEDGE_DOMAIN_MODEL_RESULT.md`
9. `output/v4_r1/V4_KNOWLEDGE_DOMAIN_MODEL_CONTRACT.json`
10. `docs/V4/V4_R1_1_REPOSITORY_VERSIONING_RESULT.md`
11. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
12. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Inspect relevant existing implementation before designing anything new:

* `legacy_documenter/knowledge/domain/`
* `legacy_documenter/models/evidence.py`
* `legacy_documenter/documentation/evidence_catalog.py`
* `legacy_documenter/documentation/contracts.py`
* `legacy_documenter/utils/sanitizer.py`
* related tests.

Reuse existing deterministic helpers where semantics match.

Do not duplicate an existing capability merely because it belongs to an earlier V3 namespace.

---

# Entry Gate

Before implementation verify:

```text
V3_BASELINE=VALID
V4_R1=APPROVED
V4_R1_1=APPROVED
TESTS>=676_PASS
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REPOSITORY_RECOVERY=VALID
```

Also verify:

* production repository state is coherent with `PROJECT_STATE.json`;
* V3 canonical artifacts remain unchanged;
* no ignored heavy output is required for this round.

If the entry gate fails:

STOP.

Do not implement R2.

---

# Authority

The Technical Lead remains the sole final approval authority for incorporation into the canonical Knowledge Source.

Input validation is NOT approval.

A valid source contract means only:

> LegacyMapper can safely and deterministically understand the supplied material as an input of the declared source type.

It does NOT mean:

* the statement is true;
* the material is approved;
* the current system implements it;
* the material belongs in canonical knowledge;
* an AI interpretation becomes authoritative.

Those decisions belong to later V4 lifecycle stages.

---

# Core Distinction

Preserve the V4 lifecycle:

```text
MATERIAL
    ↓
EVIDENCE
    ↓
INTERPRETATION
    ↓
PROPOSAL
    ↓
APPROVED_KNOWLEDGE
```

Not every source necessarily passes through every stage in exactly the same way, but R2 must not collapse these concepts.

In particular:

```text
VALID_INPUT != APPROVED_KNOWLEDGE
```

and:

```text
AUTHORITATIVE_SOURCE != UNIVERSAL_TRUTH
```

---

# Scope

Implement deterministic contracts for the complete R1 `SourceType` catalog:

1. `DETERMINISTIC_CODE_FACT`
2. `HUMAN_REQUIREMENT`
3. `USER_STORY`
4. `BUSINESS_REQUIREMENT`
5. `BUSINESS_CONTEXT`
6. `TECHNICAL_CONSTRAINT`
7. `CORPORATE_STANDARD`
8. `APPROVED_DECISION`
9. `EXTERNAL_DOCUMENT`
10. `PROJECT_DOCUMENT`
11. `AI_INTERPRETATION`
12. `UNRESOLVED`

The catalog must be CLOSED.

Unknown source types must fail deterministically.

Do not silently coerce unknown strings into known types.

---

# Design Requirement — Prefer Policy Over Class Explosion

Do NOT automatically create one Python class for every source type.

Prefer a simple design such as:

```text
SourceInput
    +
SourceContractPolicy
    +
SourceContractCatalog
    +
deterministic validator / normalizer
```

or another similarly maintainable design if repository inspection shows a better fit.

The important requirement is semantic separation, not a specific class count.

Use source-specific policy/configuration for differences between source types when that is simpler than subclass proliferation.

Follow:

`docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Classes:

`PascalCase`

Modules:

`snake_case`

Use type hints on public/significant boundaries.

Every significant public class/function/method must have a concise explanatory docstring.

Avoid unnecessary Python magic.

Avoid unnecessary C#-style abstraction.

---

# Required Input Model

Define a source-neutral validated input representation.

The exact names may be adjusted to fit R1 conventions, but conceptually it must support:

```text
source_type
content
reference
origin
contributor
title
temporal_state
authority
metadata
```

Not every field must be mandatory.

The contract must enforce only what is semantically necessary.

At least one meaningful payload mechanism must exist.

For example:

```text
content OR reference
```

must normally be present.

Empty material must fail.

Whitespace-only content/reference must not count as meaningful material.

Do not force human material to mimic source-code structure.

---

# Source-Specific Contract Policies

Implement deterministic policy rules for every `SourceType`.

The exact minimal requirements must be documented in the generated contract artifact.

Use the following semantics as the design baseline.

## DETERMINISTIC_CODE_FACT

Represents a fact extracted deterministically from source code or another deterministic code-analysis artifact.

May require code-specific reference information sufficient to trace the fact back to code evidence.

Examples:

* source file;
* symbol;
* project;
* deterministic evidence identifier;
* scanner/extractor reference.

Do not require ALL possible code metadata.

Require only enough traceability to prevent an untraceable item from claiming to be a deterministic code fact.

This requirement applies ONLY to this source type.

---

## HUMAN_REQUIREMENT

Represents a requirement explicitly supplied by a human.

Must support human-only operation.

Require meaningful content or a traceable reference to the supplied requirement.

Contributor/origin should be represented when supplied.

Do not require code.

Do not automatically treat the requirement as implemented AS_IS behavior.

---

## USER_STORY

Represents a user story supplied as project/business material.

Support either:

* free-form story content;

or structured information such as:

* actor;
* goal;
* benefit.

Do not require all three structured fields if meaningful free-form content exists.

Do not require code.

---

## BUSINESS_REQUIREMENT

Represents required business behavior or business outcome.

Require meaningful material.

Do not infer implementation.

Do not require code.

---

## BUSINESS_CONTEXT

Represents contextual business information that helps interpretation.

Require meaningful material.

Context is not automatically a requirement or norm.

Do not require code.

---

## TECHNICAL_CONSTRAINT

Represents a technical restriction or mandatory technical condition.

Require meaningful material.

Examples may include:

* platform limitation;
* compatibility restriction;
* infrastructure constraint;
* mandatory technology condition.

Do not confuse constraint with implementation evidence.

---

## CORPORATE_STANDARD

Represents an organizational/corporate standard.

Require meaningful material and enough source reference/origin to establish where the standard came from.

A corporate standard may be authoritative for the required standard while still not proving the current system complies with it.

---

## APPROVED_DECISION

Represents a decision already approved outside the V4 proposal lifecycle.

Require enough information to identify:

* the decision;
* its approval/source authority.

Do not automatically convert this input directly into canonical V4 approved knowledge.

The input still passes through V4 provenance/composition rules.

Do not fabricate approver identity when absent.

If the contract cannot establish that the supplied material actually represents an approved decision, validation must fail or classify the required field as missing according to the deterministic contract.

---

## EXTERNAL_DOCUMENT

Represents material originating outside the project repository/system.

Require:

* meaningful content or reference;
* traceable origin/reference.

Do not assume external documents are authoritative.

---

## PROJECT_DOCUMENT

Represents an existing project document.

Require:

* meaningful content or reference;
* enough project/document origin to trace the material.

Do not assume project documents are current or approved.

---

## AI_INTERPRETATION

Represents material explicitly produced through AI interpretation.

It MUST remain identifiable as AI-origin material.

Require sufficient origin/model/process reference to prevent it from being indistinguishable from human or deterministic evidence.

Do NOT require a real provider call in this round.

Tests must use fixtures.

AI interpretation must never become authoritative merely because it is structurally valid.

---

## UNRESOLVED

Represents material deliberately retained because its meaning/source/status cannot yet be resolved.

Require enough information to explain what is unresolved.

Do not force false classification into another source type.

Do not automatically reject uncertainty when preserving uncertainty is the correct behavior.

---

# Authority Semantics

R1 currently contains:

`EvidenceRef.authoritative: bool`

R2 must formally define what authority means at the source/input boundary.

The following rule is mandatory:

> Authority is scoped to what the source is qualified or authorized to establish.

Examples:

A human requirement may be authoritative evidence that:

> “This requirement was supplied/approved as a requirement.”

It is NOT automatically authoritative evidence that:

> “The current system implements this requirement.”

A corporate standard may be authoritative evidence of:

> “The organization requires this standard.”

It is NOT automatically evidence that:

> “Every existing application complies with the standard.”

A deterministic code fact may be authoritative evidence of:

> “The analyzed code contains this observed structure/behavior.”

It is NOT automatically authoritative evidence of:

> “This is the intended business behavior.”

Therefore:

```text
authoritative=true
```

must never be interpreted independently from:

* SourceType;
* claim/statement semantics;
* provenance;
* TemporalState;
* later Technical Lead approval.

R2 must document and enforce this semantic boundary where deterministic validation can reasonably do so.

If a minimal new concept such as:

`authority_scope`

is necessary, it may be introduced.

However:

* do not mutate R1 contracts unnecessarily;
* do not implement R3 provenance early;
* do not create an elaborate authorization system;
* do not implement RBAC.

If no domain-model change is required, document the scoped-authority rule explicitly in the R2 contract and tests.

---

# Temporal State

R1 provides:

* AS_IS
* TO_BE
* HISTORICAL

R2 inputs may optionally declare temporal state.

Do not force every input to declare one if the material genuinely does not establish it yet.

If supplied, it must use the closed R1 enum.

Never infer:

AS_IS

from:

DETERMINISTIC_CODE_FACT

without explicit deterministic semantics supporting that classification.

Never infer:

TO_BE

merely because something is a requirement.

Later rounds handle richer classification.

---

# Normalization

Implement deterministic normalization only where meaning is preserved.

Examples:

* trim meaningless outer whitespace;
* normalize empty optional strings to the repository's chosen canonical representation;
* validate enum values;
* validate metadata structure;
* normalize safe identifiers if existing conventions require it.

Do NOT:

* rewrite user meaning;
* summarize;
* translate;
* infer missing requirements;
* infer authority;
* infer temporal state;
* infer knowledge nature;
* use an LLM.

Normalization must be deterministic and idempotent where practical:

```text
normalize(normalize(x)) == normalize(x)
```

Add a test for this property.

---

# Sanitization and Security

Inspect and reuse:

`legacy_documenter/utils/sanitizer.py`

Do not create a second unrelated sanitizer if existing semantics are suitable.

Determine and document exactly how source intake handles:

* obvious secrets;
* unsafe/local credentials;
* untrusted text;
* file/reference strings;
* metadata;
* control characters where relevant.

Important:

Sanitization must not silently destroy evidence semantics.

If existing sanitizer behavior redacts a sensitive value:

* preserve enough information to know redaction occurred when appropriate;
* never leak the original secret into logs/errors/generated reports.

If rejection is safer than redaction for a specific field, document and test that deterministic rule.

Do not broaden security behavior beyond what is justified by existing project semantics.

---

# References and Paths

Source references are evidence identifiers, not automatically filesystem operations.

A human-supplied reference such as:

```text
SharePoint document reference
Bitbucket URL
document identifier
business ticket
decision ID
```

must not be rejected merely because it is not a local path.

Conversely, a raw input reference must not automatically be opened/read by R2.

R2 validates contracts.

R4 will handle ingestion.

No network calls.

No file fetching.

No external connectors.

No provider calls.

---

# Metadata

Metadata must remain extensible but safe.

Use a deterministic JSON-compatible structure.

Do not allow arbitrary Python executable objects.

Validate enough to guarantee future serialization.

If nested structures are accepted, ensure values are composed only from supported JSON-compatible primitives/containers.

Reject unsupported runtime objects deterministically.

Do not prematurely encode all future knowledge semantics into metadata.

Important semantics should have explicit fields/contracts when already known.

---

# Stable Identity

Inspect R1 ID helpers and existing `stable_id()`.

If validated input requires a stable identity, reuse the existing deterministic convention rather than inventing another incompatible hash scheme.

Identity must not depend on:

* current time;
* random values;
* machine path when semantically irrelevant;
* object memory address;
* provider response.

Equivalent normalized inputs should produce equivalent deterministic identity when identity generation is part of R2.

Do not change R1 IDs unless a proven defect requires it.

---

# Closed Source Contract Catalog

Implement a deterministic catalog similar in spirit to the existing closed-catalog approach used by `AllowedEvidenceCatalog`.

The catalog must allow LegacyMapper to answer:

```text
What SourceTypes are accepted?
What fields are required for this SourceType?
What validation policy applies?
What authority semantics apply?
What traceability requirements apply?
```

Unknown SourceType:

FAIL.

Missing catalog policy for an existing R1 SourceType:

FAIL.

At test time verify:

```text
set(SourceType) == set(SourceContractCatalog.supported_types)
```

or semantically equivalent logic.

This prevents adding a future SourceType without explicitly defining its intake contract.

---

# Contract Artifact

Generate:

`output/v4_r2/V4_INPUT_SOURCE_CONTRACTS.json`

This file must be deterministic and machine-readable.

It must describe, for each SourceType:

* source type;
* minimal required information;
* optional information;
* traceability requirement;
* authority semantics;
* temporal-state behavior;
* code dependency;
* validation behavior;
* sanitization behavior;
* whether human-only operation is supported.

The artifact is a CONTRACT PROJECTION.

It is not canonical Knowledge Source content.

---

# Required Implementation Location

Prefer extending the V4 knowledge package, for example:

```text
legacy_documenter/
└── knowledge/
    ├── domain/
    └── input/
```

Possible modules:

```text
input/
├── __init__.py
├── contracts.py
├── catalog.py
├── validator.py
└── normalization.py
```

This is guidance, not a mandatory file count.

Do not create unnecessary files/classes.

Choose the smallest maintainable structure consistent with the Python development standard.

---

# Backward Compatibility

V3 behavior must remain unchanged.

Do not modify V3 canonical artifacts.

Do not change:

* V3 evidence semantics;
* V3 readiness result;
* approved human review;
* V3 hashes;
* V3 document outputs;
* provider behavior.

If reuse requires adapting an existing V3 helper, preserve its public behavior and existing tests.

Prefer composition over invasive mutation.

---

# V4-R1 Compatibility

R2 must consume the R1 domain model rather than creating a competing model.

Reuse:

* `SourceType`
* `TemporalState`
* `MaterialItem`
* `Origin`

and other R1 types when semantically appropriate.

Do not duplicate those enums/classes in the input package.

If R2 reveals a genuine R1 defect, document it before changing the R1 contract.

Any R1-compatible extension must preserve all R1 tests.

---

# Out of Scope

Do NOT implement:

## V4-R3

Full provenance lineage.

## V4-R4

Human-material ingestion pipeline.

## V4-R5

Knowledge classification.

## V4-R6

AS_IS / TO_BE separation logic.

## V4-R7

Gap/conflict detection.

## V4-R8

Proposal lifecycle.

## V4-R9

Technical Lead approval workflow.

## V4-R10

Canonical Knowledge Source composition.

## V4-R11

Human-readable projection.

## V4-R12

Plugin-facing projection.

## V5

Language/framework/project-layout agnosticism redesign.

Do not modify VB.NET extraction/scanning architecture for V5 concerns.

---

# Tests

Add focused deterministic R2 tests.

Do not modify existing tests merely to make new implementation pass.

At minimum test:

## Catalog completeness

All 12 R1 SourceTypes have exactly one deterministic intake policy.

Unknown source type rejected.

---

## CODE_ONLY

Valid deterministic code fact accepted with sufficient code traceability.

Code fact without required traceability rejected.

---

## HUMAN_INFORMATION_ONLY

Valid human requirement accepted with zero code fields.

Valid user story accepted with zero code fields.

Valid business requirement accepted with zero code fields.

Valid business context accepted with zero code fields.

Valid technical constraint accepted with zero code fields.

Valid corporate standard accepted without code.

Valid approved decision accepted without code.

Valid external document accepted without code.

Valid project document accepted without code.

Valid unresolved material accepted without code.

---

## CODE_AND_HUMAN_INFORMATION

Code-derived and human-derived source inputs coexist without either contract contaminating the other.

---

## PARTIAL_INFORMATION

Valid unresolved/partial material can be preserved without inventing missing classification.

---

## User story flexibility

Free-form user story accepted.

Structured actor/goal/benefit form accepted if implemented.

Do not require redundant forms simultaneously.

---

## Authority scope

Verify that validation does not treat:

HUMAN_REQUIREMENT + authoritative

as proof of AS_IS implementation.

Verify that:

CORPORATE_STANDARD + authoritative

does not imply current compliance.

Verify that:

AI_INTERPRETATION

cannot become authoritative merely through input structure.

---

## Temporal state

Valid closed enum accepted.

Unknown temporal state rejected.

Missing temporal state accepted when policy permits it.

No inappropriate AS_IS/TO_BE inference.

---

## Sanitization

Secret-like fixture does not leak raw secret into:

* normalized output where redaction is expected;
* exception messages;
* generated contract output;
* logs/reports produced by the test.

Use only fake test credentials.

Never add a real credential.

---

## References

Non-filesystem references accepted where appropriate.

No file/network access occurs during contract validation.

---

## Metadata

JSON-compatible nested metadata accepted.

Unsupported Python object rejected.

---

## Normalization

Whitespace normalization behaves deterministically.

Normalization is idempotent.

Equivalent normalized input behaves consistently.

---

## Empty material

Reject:

* empty content;
* whitespace-only content;
* empty reference;

when no other meaningful payload exists.

---

## R1 regression

All R1 tests remain PASS.

---

## V3 regression

All historical tests remain PASS.

Expected full suite:

```text
> 676 PASS
```

Do not target an arbitrary exact new test count.

Report actual count.

---

# Determinism Verification

Run relevant R2 contract generation twice.

Compare resulting:

`V4_INPUT_SOURCE_CONTRACTS.json`

The serialized result must be byte-identical if inputs/code are unchanged.

Report SHA-256.

Expected:

```text
DETERMINISM=PASS
```

---

# Security Verification

Confirm:

* no real secrets introduced;
* no provider credentials required;
* no network access;
* no external file access during validation;
* sanitization deterministic;
* secret-like fixture values do not leak.

Expected:

```text
SECURITY=PASS
```

---

# Regression Verification

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=676 PASS
```

Then run:

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

# Repository Continuity Update

Because the repository is now the authoritative continuity mechanism, update:

`PROJECT_STATE.json`

only after R2 implementation and validation are complete.

It must reflect that:

```text
latest_completed_round = V4-R2
```

but R2 must NOT be marked human-approved unless this repository's state model explicitly distinguishes implementation completion from Technical Lead approval.

The next state should remain:

```text
NEXT=HUMAN_REVIEW_V4_R2
```

until Technical Lead review.

Do not claim R2 approval on behalf of the user.

Ensure all newly created small R2 source/contracts/tests/results are eligible for Git tracking under the current `.gitignore`.

Do not modify the repository continuity policy unless R2 introduces a genuinely new continuity requirement.

---

# Required Result

Create:

`docs/V4/V4_R2_INPUT_SOURCE_CONTRACTS_RESULT.md`

Report at minimum:

```text
STATUS
ENTRY_GATE
BASELINE_TESTS
FINAL_TESTS
SOURCE_TYPES
CATALOG_COMPLETENESS
CODE_ONLY
CODE_AND_HUMAN_INFORMATION
HUMAN_INFORMATION_ONLY
PARTIAL_INFORMATION
CODE_SOURCE_TRACEABILITY
AUTHORITY_SCOPE
TEMPORAL_STATE
NORMALIZATION
NORMALIZATION_IDEMPOTENCE
SANITIZATION
METADATA_VALIDATION
CONTRACT_ARTIFACT
CONTRACT_SHA256
DETERMINISM
SECURITY
V3_REGRESSION
V4_R1_REGRESSION
READINESS
AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS
PRODUCTION_BEHAVIOR_CHANGED
PROJECT_STATE
DECISION
NEXT
```

Also document:

## Reused Components

What existing V3/V4 components were reused and why.

## New Components

New modules/classes/functions and responsibilities.

## Source Contract Matrix

For every SourceType:

* required;
