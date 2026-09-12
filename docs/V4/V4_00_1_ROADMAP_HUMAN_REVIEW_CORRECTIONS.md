# LegacyMapper V4 — Roadmap Human Review Corrections

TASK=V4_00_1_ROADMAP_HUMAN_REVIEW_CORRECTIONS

MODE=ROADMAP_CORRECTION_ONLY

IMPLEMENTATION_ALLOWED=false

## Context

`V4_00_BOOTSTRAP_AND_BASELINE` has completed successfully.

Human review approves the bootstrap and approves the proposed V4 roadmap subject to the corrections defined in this prompt.

Do not redesign V4.

Do not implement V4-R1.

Do not modify production code.

Do not modify V3 canonical artifacts.

The purpose of this task is only to incorporate the approved conceptual corrections into the V4 roadmap and persist the human approval decision.

---

## Required Reading

Read:

1. `AGENTS.md`
2. `docs/V4/V4_CONTRACT_FOUNDATION.md`
3. `docs/V4/V4_AI_HANDOVER.md`
4. `docs/V4/V4_PROPOSED_ROADMAP.md`
5. `docs/V4/V4_00_BOOTSTRAP_RESULT.md`
6. `output/v4_bootstrap/V4_GAP_ANALYSIS.json`
7. `output/v4_bootstrap/V4_REUSE_INVENTORY.json`
8. `output/v4_bootstrap/V4_TECHNICAL_DEBT_CLASSIFICATION.json`

Use repository state as authority.

---

# Human Review Decision

The Technical Lead approves:

V4_00_BOOTSTRAP=APPROVED

The proposed roadmap is approved subject to the two corrections below.

---

# Correction 1 — Knowledge Model Must Support the Target Knowledge Structure

V4-R1 must not model knowledge only around the current V3 functional and technical documents.

The V4 Knowledge Domain Model must be source-neutral and projection-neutral.

It must be capable of representing approved knowledge that can later be projected into the target Knowledge Source structure.

The currently known target families include:

* 00 El Área / onboarding
* 01 Gobernanza / norma
* 02 Flujos / flujo
* 03 Desarrollo de Software / norma
* 04 Arquitecturas de Referencia / norma
* 05 Plantillas / plantilla
* 06 Catálogo / levantamiento
* 07 Proyectos / proyecto
* 08 Historial / historial
* 09 Capacitación / formación

These families are NOT implementation classes that must mechanically become one Python class per section.

They are target knowledge/document families that the domain model must be capable of expressing without hardcoding itself to the current V3 documents.

V4-R1 must therefore explicitly validate that its model can represent heterogeneous knowledge natures and future projections without redesigning the core model.

The model must continue supporting the knowledge natures already established by `V4_CONTRACT_FOUNDATION`.

Do not implement document generation during V4-R1.

Do not hardcode the final document tree into the core domain model unless technically justified by a later contract.

The objective is compatibility, not premature coupling.

---

# Correction 2 — One Approved Knowledge Source, Multiple Projections

Clarify V4-R10, V4-R11 and V4-R12.

There must be ONE canonical approved Knowledge Source.

Human-readable and machine-readable outputs must derive from that same approved knowledge.

Conceptually:

```text
APPROVED KNOWLEDGE
        |
        v
CANONICAL KNOWLEDGE SOURCE
        |
        +----------------------+
        |                      |
        v                      v
HUMAN-READABLE          MACHINE-READABLE
PROJECTION              PROJECTION
        |                      |
        v                      v
Markdown / documents     Plugin contract
```

The human-readable documentation and the Plugin-facing representation must not become independent sources of truth.

They are projections of the same canonical approved knowledge.

## V4-R10

Canonical Knowledge Composition must establish the structured, versionable and traceable canonical Knowledge Source from approved knowledge.

It must preserve provenance, nature, lifecycle, temporal state, uncertainty and relevant human approval information.

## V4-R11

Document Projection must generate human-readable views from the canonical Knowledge Source.

It must support the target knowledge/document families without restricting the core model to one fixed document set.

Markdown is expected to be an important human-readable projection format.

Do not make Markdown the canonical internal knowledge representation unless a later explicit technical decision justifies it.

## V4-R12

Plugin-Facing Output Contract must define a structured, versioned, machine-readable projection of the same canonical Knowledge Source.

The future Plugin must not be required to reconstruct canonical semantics by parsing human-oriented Markdown when structured knowledge is available.

The Plugin-facing contract must preserve sufficient identity and traceability to correlate machine-readable knowledge with human-readable projections.

Do not implement Plugin behavior.

LegacyMapper constructs and projects knowledge.

The Plugin consumes that knowledge.

---

# Preserve Existing Roadmap

Do not replace the existing 14-round strategy merely because of these corrections.

Retain V4-R1 through V4-R14 unless an actual dependency contradiction makes a small ordering correction necessary.

The expected roadmap remains conceptually:

V4-R1 Knowledge Domain Model

V4-R2 Input/Source Contracts

V4-R3 Provenance

V4-R4 Human Supplied Material Ingestion

V4-R5 Classification

V4-R6 AS_IS / TO_BE Separation

V4-R7 Gap and Conflict Representation

V4-R8 Proposal Lifecycle

V4-R9 Technical Lead Approval

V4-R10 Canonical Knowledge Composition

V4-R11 Human-Readable Document Projection

V4-R12 Plugin-Facing Machine-Readable Output Contract

V4-R13 Regression and Security

V4-R14 Manuals and Final Baseline

---

# V4-R1 Entry Criteria

Add explicit entry criteria for V4-R1.

Before implementation begins, V4-R1 must preserve:

V3_BASELINE=VALID

TESTS>=662_PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true

AI_KNOWLEDGE_GENERATED=false

V3 canonical artifacts unchanged.

V5 concerns remain out of scope.

The Python development standard remains mandatory.

The active development agent is replaceable.

The repository, contracts, tests, decisions and handovers are authoritative.

---

# Technical Debt

Preserve the bootstrap classification:

TD-001=DEFER

TD-002=RELEVANT_TO_V4

TD-003=RELEVANT_TO_V4

TD-004=DEFER

TD-005=RELEVANT_TO_V4

Relevant technical debt must be addressed opportunistically only when the corresponding V4 boundary is modified.

Do not perform unrelated refactoring.

In particular, new V4 contracts and public/significant boundaries must follow the established Python development standard from their first implementation:

* idiomatic Python;
* clear responsibilities;
* PascalCase classes;
* snake_case modules;
* consistent type hints;
* concise explanatory docstrings;
* minimal unnecessary Python magic;
* no unnecessary C# pattern imitation;
* simple, secure and maintainable code.

---

# Agent Neutrality

The roadmap must refer to the active development agent generically where possible.

Claude is currently executing the work but must not become an architectural dependency.

Historical `codex/V1`, `codex/V2`, and `codex/V3` directories remain unchanged.

Do not rename historical artifacts.

---

# Required Changes

Update:

`docs/V4/V4_PROPOSED_ROADMAP.md`

After incorporating the approved corrections, change its status from:

PROPOSED

to:

APPROVED

Add the Technical Lead human review decision.

Do not remove useful information from the original roadmap.

Create:

`docs/V4/V4_00_1_ROADMAP_APPROVAL_RESULT.md`

The result must record at minimum:

STATUS

V4_00_BOOTSTRAP

ROADMAP_STATUS

HUMAN_REVIEW

CORRECTION_1_KNOWLEDGE_STRUCTURE

CORRECTION_2_PROJECTION_MODEL

CANONICAL_KNOWLEDGE_SOURCE

HUMAN_READABLE_PROJECTION

PLUGIN_MACHINE_READABLE_PROJECTION

PLUGIN_BOUNDARY

V3_BASELINE

PRODUCTION_CODE_CHANGED

TESTS

REAL_LLM_CALLS

PROVIDER_CALLS

DECISION

NEXT

---

# Verification

Run the existing test suite:

`python -m unittest discover -s tests`

No production code changes are expected.

No real LLM/provider calls are allowed.

Verify that canonical V3 artifacts remain unchanged.

---

# Expected Result

STATUS=V4_00_1_ROADMAP_CORRECTIONS_COMPLETE

V4_00_BOOTSTRAP=APPROVED

ROADMAP_STATUS=APPROVED

HUMAN_REVIEW=APPROVED_WITH_CORRECTIONS_APPLIED

CORRECTION_1_KNOWLEDGE_STRUCTURE=APPLIED

CORRECTION_2_PROJECTION_MODEL=APPLIED

CANONICAL_KNOWLEDGE_SOURCE=ONE

HUMAN_READABLE_PROJECTION=DERIVED_FROM_CANONICAL_KNOWLEDGE

PLUGIN_MACHINE_READABLE_PROJECTION=DERIVED_FROM_CANONICAL_KNOWLEDGE

PLUGIN_BOUNDARY=PRESERVED

V3_BASELINE=VALID

PRODUCTION_CODE_CHANGED=false

TESTS>=662_PASS

REAL_LLM_CALLS=0

PROVIDER_CALLS=0

DECISION=V4_ROADMAP_FORMALLY_APPROVED

NEXT=V4_R1_KNOWLEDGE_DOMAIN_MODEL

Stop.

Do not implement V4-R1.