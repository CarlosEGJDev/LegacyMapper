# LegacyMapper V4 — Proposed Roadmap

## Status

`APPROVED` by the Technical Lead, subject to the two corrections recorded below. Approval is conceptual/architectural; no implementation has started as a result of this document.

## Human Review Decision

The Technical Lead approved `V4_00_BOOTSTRAP` and approved this roadmap subject to two corrections, recorded in `docs/V4/V4_00_1_ROADMAP_HUMAN_REVIEW_CORRECTIONS.md` and applied below:

1. **Knowledge Model Must Support the Target Knowledge Structure** — the V4-R1 domain model must be source-neutral and projection-neutral, not modeled only around the current V3 functional/technical documents.
2. **One Approved Knowledge Source, Multiple Projections** — there is exactly one canonical approved Knowledge Source; human-readable and machine-readable outputs are both projections derived from it, never independent sources of truth.

Full disposition is recorded in `docs/V4/V4_00_1_ROADMAP_APPROVAL_RESULT.md`.

## Principle

Contracts before implementation. Each round below is independently testable and preserves the V3 baseline (662 tests, `READY`, `AI_KNOWLEDGE_GENERATED=false`) throughout.

## V4-R1 Entry Criteria

Before V4-R1 implementation begins, the following must hold:

* `V3_BASELINE=VALID`
* `TESTS>=662_PASS`
* `READINESS=READY`
* `AI_KNOWLEDGE_ALLOWED=true`
* `AI_KNOWLEDGE_GENERATED=false`
* V3 canonical artifacts unchanged.
* V5 full technology/language/framework agnosticism remains out of scope.
* `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md` remains mandatory for all new V4 contracts and public/significant boundaries.
* The active development agent is replaceable; the repository, contracts, tests, decisions and handovers are authoritative, independent of any agent's memory.

## Rounds

### V4-R1 — Knowledge Domain Model
Define the source-neutral, projection-neutral data model: `MaterialItem`, `EvidenceRef`, `KnowledgeStatement`, source type enum (`DETERMINISTIC_CODE_FACT`, `HUMAN_REQUIREMENT`, `USER_STORY`, `BUSINESS_REQUIREMENT`, `BUSINESS_CONTEXT`, `TECHNICAL_CONSTRAINT`, `CORPORATE_STANDARD`, `APPROVED_DECISION`, `EXTERNAL_DOCUMENT`, `PROJECT_DOCUMENT`, `AI_INTERPRETATION`, `UNRESOLVED`), and the `nature` taxonomy from `V4_CONTRACT_FOUNDATION` section 5. Builds on `legacy_documenter/models/evidence.py` and `documentation/contracts.py` (EXTEND).

Per Correction 1, the model must be validated (by construction and by test, not by implementing document generation) against its ability to represent knowledge belonging to the currently known target knowledge/document families — `00 El Área`, `01 Gobernanza`, `02 Flujos`, `03 Desarrollo de Software`, `04 Arquitecturas de Referencia`, `05 Plantillas`, `06 Catálogo`, `07 Proyectos`, `08 Historial`, `09 Capacitación` — without hardcoding a one-class-per-family structure and without coupling the core model to the current V3 document tree. These families are target knowledge/document families the model must be able to express, not implementation classes to build now.

### V4-R2 — Input/Source Contracts
Define validated intake contracts per source type (schema, required fields, sanitization via `utils/sanitizer.py`). No LLM involvement; purely deterministic validation, following the `AllowedEvidenceCatalog` closed-catalog pattern.

### V4-R3 — Provenance
Extend evidence/lineage tracking (`documentation/evidence_resume.py`, `evidence_catalog.py`) to cover all V4 source types, recording origin and, when applicable, the Technical Lead's authorization of incorporation.

### V4-R4 — Human Supplied Material Ingestion
Implement the general-purpose intake mechanism for Technical-Lead-provided MATERIAL, generalizing `documentation/human_review.py` parsing beyond the fixed FMI/TMI vocabulary.

### V4-R5 — Classification
Implement `nature` classification and the `MATERIAL -> EVIDENCE -> INTERPRETATION -> PROPOSAL -> APPROVED_KNOWLEDGE` stage model (section 3.2).

### V4-R6 — AS_IS / TO_BE Separation
Add the temporal dimension (`AS_IS`, `TO_BE`, `HISTORICAL`) to `KnowledgeStatement`, allowing coexistence without automatic contradiction.

### V4-R7 — Gap and Conflict Representation
Implement `GAP` detection (AS_IS vs TO_BE difference) and `CONFLICT` representation (implicated sources/statements/nature/state/evidence/possible cause/human resolution), extending `documentation/consistency.py`'s deterministic comparison approach.

### V4-R8 — Proposal Lifecycle
Implement the `PROPOSAL` entity and its lifecycle states, sitting between `AI_INTERPRETATION` and `APPROVED_KNOWLEDGE`.

### V4-R9 — Technical Lead Approval
Generalize `documentation/human_review.py` / `second_review.py`'s document-level approval into a repeatable, per-proposal approve/reject/correct workflow tied to the Technical Lead as controlled operator (no RBAC beyond this single authority role, per `V4_CONTRACT_FOUNDATION` section 2).

### V4-R10 — Canonical Knowledge Composition
Establish the ONE structured, versionable, traceable canonical Knowledge Source from approved knowledge (section 8), building on `ContextComposer`'s priority/budget mechanism (EXTEND). It must preserve provenance, nature, lifecycle, temporal state (AS_IS/TO_BE/HISTORICAL), uncertainty and relevant human approval information. Per Correction 2, this is the single source of truth; V4-R11 and V4-R12 only derive projections from it.

### V4-R11 — Human-Readable Document Projection
Generalize `documentation/generator.py`/`renderer.py` projection beyond the two fixed V3 documents into a projection layer that derives human-readable views (Markdown expected to be an important format, but not the canonical internal representation unless a later explicit technical decision justifies it) from the single canonical Knowledge Source established in V4-R10. Must support the target knowledge/document families named in the V4-R1 entry above without restricting the core model to one fixed document set.

### V4-R12 — Plugin-Facing Machine-Readable Output Contract
Define a structured, versioned, machine-readable projection of the same canonical Knowledge Source from V4-R10 — not an independent source of truth. The contract must preserve sufficient identity and traceability to correlate machine-readable knowledge with the human-readable projection from V4-R11, and must not require the future Plugin to reconstruct canonical semantics by parsing human-oriented Markdown when structured knowledge is available. Explicitly excludes any Plugin responsibility (documenting/designing/developing/validating target projects) from LegacyMapper itself; LegacyMapper constructs and projects knowledge, the Plugin consumes it.

### V4-R13 — Regression and Security
Full regression suite extension covering all new contracts; sanitizer coverage extended to all new source types; no new provider calls beyond what each round's tests explicitly authorize.

### V4-R14 — Manuals and Final Baseline
Update `docs/V4/MANUAL_TECNICO_LEGACYMAPPER_V4.md` and `docs/V4/MANUAL_USUARIO_LEGACYMAPPER_V4.md`; publish `output/v4_final/V4_FINAL_BASELINE.json` following the same closure pattern as V3.

## Constraints Carried Into Every Round

* Preserve all 662 V3 tests and the V3 readiness gate unchanged.
* Do not modify canonical V3 artifacts, approved human review decisions, or R9 semantics.
* No real LLM/provider calls except where a round's own tests explicitly authorize and validate them.
* Every new capability must fit the `Python discovers/resolves, LLM interprets, human approves` boundary.
* Full technology/language/framework agnosticism remains deferred to V5.

## Canonical Knowledge Source and Projections (Correction 2 Summary)

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

There is exactly one canonical Knowledge Source, established in V4-R10. Human-readable documentation (V4-R11) and the Plugin-facing contract (V4-R12) are both projections of it and must never become independent sources of truth.

## Agent Neutrality

This roadmap refers to "the active development agent" generically. Claude is currently executing this work but is not an architectural dependency; any capable agent must be able to resume from this roadmap and the repository alone. Historical `codex/V1`, `codex/V2`, and `codex/V3` directories remain unchanged and are not renamed.

## Next Step

`V4_R1_KNOWLEDGE_DOMAIN_MODEL` — the Technical Lead has approved this roadmap; V4-R1 implementation may begin under a future, separately scoped prompt.
