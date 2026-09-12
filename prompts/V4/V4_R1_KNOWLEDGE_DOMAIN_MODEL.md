# LegacyMapper V4 — R1 Knowledge Domain Model

TASK=V4_R1_KNOWLEDGE_DOMAIN_MODEL

MODE=IMPLEMENT_AND_VALIDATE

IMPLEMENTATION_ALLOWED=true

## Objective

Implement the foundational V4 knowledge domain model.

This round creates the core source-neutral and projection-neutral structures that future V4 rounds will use for:

* multi-source knowledge;
* human-supplied information;
* provenance;
* classification;
* AS_IS / TO_BE separation;
* gap/conflict representation;
* proposal lifecycle;
* Technical Lead approval;
* canonical Knowledge Source composition;
* human-readable projection;
* Plugin-facing machine-readable projection.

Do not implement those later capabilities yet unless a minimal supporting type is strictly necessary for the R1 contract.

The objective of R1 is the DOMAIN MODEL, not the complete V4 workflow.

---

# Required Reading

Read before modifying code:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `docs/V4/V4_CONTRACT_FOUNDATION.md`
4. `docs/V4/V4_AI_HANDOVER.md`
5. `docs/V4/V4_PROPOSED_ROADMAP.md`
6. `docs/V4/V4_00_BOOTSTRAP_RESULT.md`
7. `docs/V4/V4_00_1_ROADMAP_APPROVAL_RESULT.md`
8. `output/v4_bootstrap/V4_REUSE_INVENTORY.json`
9. `output/v4_bootstrap/V4_GAP_ANALYSIS.json`
10. `output/v4_bootstrap/V4_TECHNICAL_DEBT_CLASSIFICATION.json`
11. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Also inspect the existing relevant implementation:

* `legacy_documenter/models/evidence.py`
* `legacy_documenter/documentation/contracts.py`
* `legacy_documenter/documentation/evidence_catalog.py`
* `legacy_documenter/documentation/human_review.py`
* related tests covering these contracts.

Do not assume previous conversation context.

Repository artifacts are authoritative.

---

# Entry Gate

Before implementation, verify:

V3_BASELINE=VALID

TESTS>=662_PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true

AI_KNOWLEDGE_GENERATED=false

No canonical V3 artifact may be modified.

V5 language/framework/technology/layout agnosticism remains out of scope.

No real LLM/provider call is allowed in this round.

If the entry gate fails, stop and report the failure.

---

# Critical V4 Clarification — Source Code Is Optional

V4 MUST NOT require source code to exist.

The core domain model must support all of these scenarios as first-class valid states:

## CODE_ONLY

Knowledge originates only from source-code-derived evidence.

This corresponds closely to the historical LegacyMapper use case.

## CODE_AND_HUMAN_INFORMATION

Knowledge originates from both source code and human/documentary material.

Both must coexist with independent provenance.

Neither silently overwrites the other.

Differences may later become GAP or CONFLICT records.

## HUMAN_INFORMATION_ONLY

No source code exists.

LegacyMapper receives only information such as:

* existing documentation;
* requirements;
* user stories;
* business needs;
* business context;
* technical constraints;
* corporate standards;
* architectural decisions;
* project documents;
* information supplied by the Technical Lead.

This is a VALID V4 operating mode.

Absence of `DETERMINISTIC_CODE_FACT` must not invalidate:

* MaterialItem;
* EvidenceRef;
* KnowledgeStatement;
* future Knowledge Source composition.

No model property may require a code file, code symbol, project file, repository scan, language, framework or technology merely to instantiate valid knowledge.

## PARTIAL_INFORMATION

Only partial material is available.

The model must allow knowledge to remain partial, unresolved or incomplete without inventing missing information.

---

# Architectural Rule

The model must satisfy:

```text
ZERO_OR_MORE_CODE_SOURCES
+
ZERO_OR_MORE_HUMAN_OR_DOCUMENT_SOURCES
+
AT_LEAST_ONE_VALID_MATERIAL_SOURCE
        |
        v
KNOWLEDGE DOMAIN MODEL
```

Code is one source type.

It is not the root of the V4 domain model.

---

# Core Domain Types

Implement a minimal, cohesive V4 domain model including at least the concepts below.

Exact module boundaries may be adjusted if justified by current repository architecture.

Prefer a small number of clear modules rather than unnecessary fragmentation.

## MaterialItem

Represents material supplied to or discovered by LegacyMapper before it becomes approved knowledge.

It must be able to represent material from any supported V4 source type.

At minimum consider fields such as:

* stable id;
* source type;
* title/name when applicable;
* content or reference;
* origin;
* metadata;
* optional external/source reference.

Do not make filesystem path mandatory.

Do not make source code metadata mandatory.

Material may exist only as human-provided content.

---

## EvidenceRef

Represents traceable evidence supporting a knowledge statement.

Reuse or extend the existing evidence model where appropriate.

Preserve compatibility with V3 evidence semantics.

A V4 evidence reference must not assume it points to code.

It may point to:

* code-derived evidence;
* requirement;
* user story;
* document;
* standard;
* decision;
* business information;
* Technical Lead supplied material;
* unresolved source material.

Do not duplicate existing V3 evidence concepts unnecessarily.

---

## KnowledgeStatement

Represents one semantically meaningful knowledge statement.

It should be capable of carrying, directly or through strongly typed associated structures:

* stable id;
* statement/content;
* source type or source relationship;
* nature;
* status;
* evidence references;
* provenance/origin;
* optional temporal state;
* optional relationships to other knowledge records.

Do not prematurely implement R6, R7, R8 or R9 behavior.

R1 may define extensible enums/types that later rounds will use, but must not implement lifecycle engines or automated gap/conflict detection.

---

# Source Types

Support the V4 contract source types:

* `DETERMINISTIC_CODE_FACT`
* `HUMAN_REQUIREMENT`
* `USER_STORY`
* `BUSINESS_REQUIREMENT`
* `BUSINESS_CONTEXT`
* `TECHNICAL_CONSTRAINT`
* `CORPORATE_STANDARD`
* `APPROVED_DECISION`
* `EXTERNAL_DOCUMENT`
* `PROJECT_DOCUMENT`
* `AI_INTERPRETATION`
* `UNRESOLVED`

Use an explicit enum or equivalent constrained type.

Do not use free-form strings where a closed contract is appropriate.

---

# Knowledge Nature

Support the knowledge nature taxonomy from `V4_CONTRACT_FOUNDATION`.

At minimum:

* norm;
* levantamiento;
* requirement;
* need;
* business_rule;
* decision;
* architecture;
* process;
* flow;
* catalog;
* project;
* resolution;
* lesson;
* training;
* glossary;
* constraint;
* existing_implementation.

Normalize naming according to existing project style.

Use explicit constrained values.

Do not encode the target document sections directly as the nature enum unless technically justified.

---

# Knowledge Status

R1 must establish a vocabulary capable of representing at minimum:

* CONFIRMED
* INTERPRETED
* PARTIAL
* UNRESOLVED
* MISSING
* CONFLICTING
* SUPERSEDED

Preserve compatibility with existing V3 semantics where applicable.

Do not silently change V3 meanings.

---

# Temporal State

Prepare the model for:

* AS_IS
* TO_BE
* HISTORICAL

This temporal dimension may be represented in R1 because it is a fundamental domain property.

Do not implement GAP detection yet.

The model must allow AS_IS and TO_BE statements about the same subject to coexist.

---

# Provenance

R1 must establish enough structure for later provenance work without prematurely implementing R3.

A statement should be able to identify where its supporting material came from.

The design must allow provenance for:

* file-based sources;
* code-derived sources;
* direct human input;
* copied text;
* external documents;
* future structured imports.

Do not assume every origin has a filesystem path.

Do not assume every origin has a URL.

---

# Technical Lead Authority

The Technical Lead is the controlled operator and eventual approval authority.

Do not implement the full R9 approval workflow yet.

However, the model must not prevent future storage of:

* approval status;
* approver identity/role;
* approval timestamp;
* correction/rejection information.

Do not implement enterprise RBAC.

---

# Projection Neutrality

The core domain model MUST NOT depend on:

* Markdown;
* a particular document filename;
* V3 `LEVANTAMIENTO_FUNCIONAL`;
* V3 `LEVANTAMIENTO_TECNICO`;
* the future Plugin output format;
* SharePoint;
* Confluence.

Those are projections/destinations.

The Knowledge Domain Model is upstream of them.

---

# Target Knowledge Families Compatibility

Without implementing document generation, verify through tests that the model can represent knowledge intended for all currently known target families:

* `00 El Área`
* `01 Gobernanza`
* `02 Flujos`
* `03 Desarrollo de Software`
* `04 Arquitecturas de Referencia`
* `05 Plantillas`
* `06 Catálogo`
* `07 Proyectos`
* `08 Historial`
* `09 Capacitación`

Do not implement one Python class per family.

The same core model should represent them through appropriate nature, metadata and relationships.

---

# Canonical Knowledge Principle

R1 must align with the approved architecture:

```text
MATERIAL
    |
    v
EVIDENCE / INTERPRETATION / PROPOSAL
    |
    v
APPROVED KNOWLEDGE
    |
    v
CANONICAL KNOWLEDGE SOURCE
    |
    +--> HUMAN-READABLE PROJECTION
    |
    +--> MACHINE-READABLE PLUGIN PROJECTION
```

R1 does not implement the complete pipeline.

Its structures must make this future pipeline possible without a redesign.

---

# Relationship With Existing V3 Models

Prefer:

EXTEND

ADAPT

or COMPOSE

before introducing duplicate concepts.

Do not mutate historical V3 semantics solely to make V4 simpler.

If a new V4 model is safer than changing a V3 model, use a separate V4 type and provide explicit compatibility boundaries.

Document the decision.

---

# Python Development Standard

All newly introduced code must follow the established LegacyMapper Python standard from the first implementation.

Required:

* idiomatic Python;
* simple design;
* clear responsibility boundaries;
* PascalCase classes;
* snake_case modules;
* consistent public/significant type hints;
* concise explanatory docstrings;
* readable structure for a developer coming from C#;
* no unnecessary Python magic;
* no trivial Java/C#-style getter/setter boilerplate;
* no unnecessary abstract interfaces;
* no pattern proliferation;
* no premature dependency injection framework;
* deterministic validation where practical.

A significant public class or method without useful documentation should be treated as incomplete.

---

# Technical Debt

Relevant inherited debt:

TD-002=provider exception boundaries
TD-003=cross-round helpers
TD-005=type hints

For this round:

TD-005 is directly relevant.

New and modified V4 boundaries must use proper type hints.

TD-002 should not be modified because R1 must not call providers.

TD-003 should only be touched if R1 necessarily modifies a shared helper and contract equivalence is demonstrated.

Do not perform unrelated debt cleanup.

---

# Suggested Module Placement

Inspect the current architecture first.

A reasonable target could be:

`legacy_documenter/knowledge/models.py`

or a small cohesive package such as:

`legacy_documenter/knowledge/domain/`

Do not create unnecessary layers.

Choose the structure that best fits the current codebase and explain the decision in the result.

If multiple significant classes become large and independent, prefer clear separate modules.

Do not mechanically create one file per tiny enum/value object.

---

# Validation Rules

Add deterministic validation for the domain types where appropriate.

Examples:

* non-empty stable ids;
* valid enum values;
* no impossible null/empty combinations;
* duplicate evidence references rejected where appropriate;
* code-specific fields optional for non-code sources;
* human-only material valid without any code metadata.

Keep validation close to the domain contract.

Do not introduce an LLM for validation.

---

# Required Tests

Add focused tests for the new domain model.

At minimum verify:

## Scenario 1 — CODE_ONLY

A valid knowledge statement backed by `DETERMINISTIC_CODE_FACT`.

## Scenario 2 — CODE_AND_HUMAN_INFORMATION

One code fact and one human requirement coexist and retain independent provenance.

## Scenario 3 — HUMAN_INFORMATION_ONLY

Create valid material/evidence/knowledge from a human requirement or project document with:

* no source-code path;
* no language;
* no project file;
* no code symbol;
* no repository scan metadata.

This scenario MUST PASS.

## Scenario 4 — PARTIAL_INFORMATION

A valid partial/unresolved statement can exist without LegacyMapper inventing missing content.

## Scenario 5 — AS_IS / TO_BE COEXISTENCE

Two statements about the same conceptual subject may coexist when one is AS_IS and the other is TO_BE.

No automatic conflict should be produced in R1.

## Scenario 6 — TARGET FAMILY REPRESENTATION

Demonstrate that each of the ten target knowledge families can be represented using the common domain model without specialized family classes.

## Scenario 7 — INVALID CONTRACTS

Reject invalid enum values and structurally invalid records deterministically.

## Scenario 8 — V3 REGRESSION

All existing tests remain passing.

---

# Forbidden In This Round

Do NOT implement:

* general-purpose human ingestion pipeline;
* LLM classification;
* automated knowledge classification engine;
* GAP detection;
* CONFLICT detection engine;
* proposal lifecycle engine;
* Technical Lead approval workflow;
* canonical Knowledge Source composer;
* Markdown projection;
* Plugin output;
* V5 extractors;
* language/framework agnosticism refactor;
* real provider calls;
* AI_KNOWLEDGE generation.

Do not modify legacy source.

---

# Required Outputs

Create a compact result report:

`docs/V4/V4_R1_KNOWLEDGE_DOMAIN_MODEL_RESULT.md`

If useful for deterministic inspection, also create:

`output/v4_r1/V4_KNOWLEDGE_DOMAIN_MODEL_CONTRACT.json`

The JSON artifact should describe the implemented contract, not duplicate Python source code.

Do not create unnecessary ZIP files.

---

# Result Report

The result must include:

STATUS

ENTRY_GATE

V3_BASELINE

BASELINE_TESTS

FINAL_TESTS

DOMAIN_MODEL

MATERIAL_ITEM

EVIDENCE_REF

KNOWLEDGE_STATEMENT

SOURCE_TYPES

KNOWLEDGE_NATURES

KNOWLEDGE_STATUSES

TEMPORAL_STATES

PROVENANCE_SUPPORT

CODE_OPTIONAL

CODE_ONLY_SCENARIO

CODE_AND_HUMAN_SCENARIO

HUMAN_INFORMATION_ONLY_SCENARIO

PARTIAL_INFORMATION_SCENARIO

TARGET_FAMILIES_COMPATIBILITY

V3_COMPATIBILITY

TECHNICAL_DEBT

PRODUCTION_FILES_CHANGED

TEST_FILES_CHANGED

REAL_LLM_CALLS

PROVIDER_CALLS

AI_KNOWLEDGE_GENERATED

DECISION

NEXT

---

# Expected Success State

STATUS=V4_R1_KNOWLEDGE_DOMAIN_MODEL_COMPLETE

ENTRY_GATE=PASS

V3_BASELINE=VALID

BASELINE_TESTS>=662_PASS

FINAL_TESTS>BASELINE_TESTS

DOMAIN_MODEL=VALID

MATERIAL_ITEM=IMPLEMENTED

EVIDENCE_REF=IMPLEMENTED_OR_COMPATIBLY_EXTENDED

KNOWLEDGE_STATEMENT=IMPLEMENTED

SOURCE_TYPES=VALIDATED

KNOWLEDGE_NATURES=VALIDATED

KNOWLEDGE_STATUSES=VALIDATED

TEMPORAL_STATES=VALIDATED

PROVENANCE_SUPPORT=FOUNDATIONAL

CODE_OPTIONAL=true

CODE_ONLY_SCENARIO=PASS

CODE_AND_HUMAN_SCENARIO=PASS

HUMAN_INFORMATION_ONLY_SCENARIO=PASS

PARTIAL_INFORMATION_SCENARIO=PASS

TARGET_FAMILIES_COMPATIBILITY=PASS

V3_COMPATIBILITY=PASS

REAL_LLM_CALLS=0

PROVIDER_CALLS=0

AI_KNOWLEDGE_GENERATED=false

DECISION=V4_R1_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_R1

Stop after completion.

Do not begin V4-R2.
