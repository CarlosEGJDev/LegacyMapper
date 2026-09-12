# LegacyMapper V4 — Architecture and Contract Reference

## Purpose and Scope

This is a concise **technical reference**, not a narrative manual. It exists so a developer or AI
agent can look up an enum value, an ID prefix, a package boundary, or a security invariant without
re-reading all fourteen V4 round result documents. Every value below was verified against the
actual repository (production code under `legacy_documenter/knowledge/`, the R10/R11/R12/R13
contract and example JSON artifacts, and the fourteen round result documents under `docs/V4/`) as
part of V4-R14. If this document ever disagrees with the actual code or an approved contract JSON
artifact, **the repository wins** — report the discrepancy rather than trusting this file.

This document records `DOCUMENT_AND_BASELINE_EXISTING_APPROVED_BEHAVIOR`; it introduces no new
capability and changes no production behavior.

## 1. Architecture

```text
MATERIAL (any source)
   |  legacy_documenter/knowledge/input/ (R2 contracts) + ingestion/ (R4 intake)
   v
EVIDENCE / PROVENANCE
   |  legacy_documenter/knowledge/provenance/ (R3 lineage graph)
   v
CLASSIFICATION (nature) + TEMPORAL SEPARATION (AS_IS/TO_BE/HISTORICAL) + RELATIONS (DIFFERENCE/GAP/CONFLICT/TEMPORAL_EVOLUTION)
   |  legacy_documenter/knowledge/classification/, temporal/, relations/  (R5, R6, R7)
   v
PROPOSAL
   |  legacy_documenter/knowledge/proposals/ (R8)
   v
TECHNICAL LEAD APPROVAL
   |  legacy_documenter/knowledge/approval/ (R9)
   v
CANONICAL KNOWLEDGE SOURCE  (ONE_CANONICAL_KNOWLEDGE_SOURCE)
   |  legacy_documenter/knowledge/canonical/ (R10)
   |
   +---------------------------+
   |                           |
   v                           v
HUMAN-READABLE PROJECTION   PLUGIN-FACING PROJECTION
legacy_documenter/knowledge/  legacy_documenter/knowledge/
projection/ (R11)             plugin_projection/ (R12)
Markdown, 00-09 families      LegacyMapperPluginKnowledge 1.0, JSON
```

R11 and R12 are **siblings**, both reading only `legacy_documenter.knowledge.canonical.service.CanonicalKnowledgeCollection.list()`.
Neither reads the other's output; `plugin_projection` never imports `projection` and vice versa
(verified by R13's AST import-node scan in both directions). `R11_DEPENDENCY=NONE` on R12's side is
an explicit, tested contract property.

Not every input necessarily passes through every stage above — e.g. `MaterialItem` ingestion (R4)
does not require R5 classification before R6 temporal separation, and R7 relations are optional,
explicit-only annotations. The stages describe the available pipeline, not a mandatory linear path
every piece of material must traverse.

## 2. Round Responsibility Summary (R1–R14)

| Round | Package | Responsibility |
|---|---|---|
| R1 | `knowledge/domain/` | Source-neutral domain model: `MaterialItem`, `EvidenceRef`, `KnowledgeStatement`, `SourceType`, `KnowledgeNature`, `KnowledgeStatus`, `TemporalState` |
| R1.1 | (repository) | Repository versioning/recovery inventory, `V4_REPOSITORY_CONTINUITY_CONTRACT.md` |
| R2 | `knowledge/input/` | Per-`SourceType` intake validation contracts (`SourceInput`, `SourceContractCatalog`) |
| R3 | `knowledge/provenance/` | Deterministic node/edge lineage graph (`ProvenanceNode`, `ProvenanceEdge`, `ProvenanceGraph`) |
| R4 | `knowledge/ingestion/` | Human-supplied `MaterialItem` intake boundary (`HumanMaterialIngestionService`) |
| R5 | `knowledge/classification/` | `KnowledgeNature` classification of a `MaterialItem` (`ClassificationRecord`) |
| R6 | `knowledge/temporal/` | AS_IS/TO_BE/HISTORICAL/UNSPECIFIED structural bucketing (`TemporalPlacement`) |
| R7 | `knowledge/relations/` | Explicit DIFFERENCE/GAP/CONFLICT/TEMPORAL_EVOLUTION relations (`KnowledgeRelation`) |
| R8 | `knowledge/proposals/` | `Proposal` lifecycle up to `READY_FOR_REVIEW` |
| R9 | `knowledge/approval/` | Technical Lead `ApprovalDecision` (APPROVED/REJECTED/CORRECTION_REQUESTED) |
| R10 | `knowledge/canonical/` | `CanonicalKnowledgeEntry` composition — the one canonical Knowledge Source |
| R11 | `knowledge/projection/` | Human-readable Markdown projection (00–09 document families) |
| R12 | `knowledge/plugin_projection/` | `LegacyMapperPluginKnowledge` 1.0 machine-readable projection |
| R13 | (tests + `output/v4_r13/`) | Full regression/security validation of R1–R12 |
| R14 | `docs/V4/`, `output/v4_r14/` | Manuals, final baseline/manifest — this document's own round |

## 3. Source Types (`SourceType`, R1) — 12 values

`DETERMINISTIC_CODE_FACT`, `HUMAN_REQUIREMENT`, `USER_STORY`, `BUSINESS_REQUIREMENT`,
`BUSINESS_CONTEXT`, `TECHNICAL_CONSTRAINT`, `CORPORATE_STANDARD`, `APPROVED_DECISION`,
`EXTERNAL_DOCUMENT`, `PROJECT_DOCUMENT`, `AI_INTERPRETATION`, `UNRESOLVED`.

R4 human-supplied ingestion accepts 10 of these (everything except `DETERMINISTIC_CODE_FACT` and
`AI_INTERPRETATION`, which have their own, non-human-ingestion paths).

## 4. Knowledge Natures (`KnowledgeNature`, R1) — 17 values

`NORM`, `LEVANTAMIENTO`, `REQUIREMENT`, `NEED`, `BUSINESS_RULE`, `DECISION`, `ARCHITECTURE`,
`PROCESS`, `FLOW`, `CATALOG`, `PROJECT`, `RESOLUTION`, `LESSON`, `TRAINING`, `GLOSSARY`,
`CONSTRAINT`, `EXISTING_IMPLEMENTATION`.

`SourceType != KnowledgeNature`: R5's classification service never derives `nature` from
`source_type`; both are always supplied independently by the caller.

## 5. Knowledge Statuses (`KnowledgeStatus`, R1) — 7 values

`CONFIRMED`, `INTERPRETED`, `PARTIAL`, `UNRESOLVED`, `MISSING`, `CONFLICTING`, `SUPERSEDED`.
`CONFIRMED` requires at least one authoritative `EvidenceRef` (enforced by
`KnowledgeStatement.validate()` and reused unmodified inside
`CanonicalKnowledgeEntry.validate()`). Technical Lead approval (`APPROVED`, R9) never forces
`CONFIRMED` or any other status — `APPROVED != CONFIRMED`.

## 6. Temporal States and Buckets

* `TemporalState` (R1, attached to `MaterialItem`/`KnowledgeStatement`/`CanonicalKnowledgeEntry`):
  `AS_IS`, `TO_BE`, `HISTORICAL` (optional; may be `None`/absent).
* `TemporalBucket` (R6, a projection-level concept only, never a `TemporalState` extension):
  `AS_IS`, `TO_BE`, `HISTORICAL`, `UNSPECIFIED`. Mapping is a fixed dict:
  `AS_IS→AS_IS`, `TO_BE→TO_BE`, `HISTORICAL→HISTORICAL`, `None→UNSPECIFIED`. Never inferred from
  content, dates, source type, or nature.
* R12's `PluginKnowledgeManifest.temporal_state_counts` uses the explicit label `"UNSPECIFIED"` for
  an absent temporal state — never `null`/`"None"`/`"AS_IS"`.

## 7. Relation Types (`RelationKind`, R7) — 4 values

`DIFFERENCE` (symmetric), `GAP` (directional, FROM→TO), `CONFLICT` (symmetric),
`TEMPORAL_EVOLUTION` (directional). All four are created only via an explicit `RelationRequest`;
none is ever auto-derived merely because an `AS_IS` and a `TO_BE` statement differ.

## 8. Proposal Lifecycle (R8)

* `ProposalKind` (8): `INTERPRETATION`, `RESOLUTION`, `CORRECTION`, `RECONCILIATION`, `SELECTION`,
  `ADDITIONAL_INFORMATION`, `MIGRATION`, `KNOWLEDGE_ADDITION`.
* `ProposalStatus` (4): `DRAFT`, `READY_FOR_REVIEW`, `WITHDRAWN`, `SUPERSEDED`.
  Valid transitions: `DRAFT→READY_FOR_REVIEW`, `DRAFT→WITHDRAWN`, `DRAFT→SUPERSEDED`,
  `READY_FOR_REVIEW→SUPERSEDED`, `READY_FOR_REVIEW→WITHDRAWN`. `READY_FOR_REVIEW != APPROVED`;
  `WITHDRAWN != REJECTED`.
* `ProposalMethod` (3): `HUMAN_PROPOSED`, `DETERMINISTIC_RULE`, `AI_PROPOSED`.

## 9. Approval (R9)

* `ApprovalDecisionType` (3): `APPROVED`, `REJECTED`, `CORRECTION_REQUESTED`.
  `CORRECTION_REQUESTED != REJECTED`; `REJECTED != FALSE`; `APPROVED != CONFIRMED`.
* `ApprovalAuthority`: exactly one member, `TECHNICAL_LEAD`. No RBAC, no AI or system authority
  value exists anywhere in the enum.
* Precondition: a decision may only be recorded against a `Proposal` whose status is
  `READY_FOR_REVIEW`.
* `is_eligible_for_canonical_composition()` returns `True` only for `APPROVED` decisions by
  `TECHNICAL_LEAD` — a pure query, never a write.

## 10. Canonical Entry Structure (R10)

```text
CanonicalKnowledgeEntry(
  knowledge_id,            # KNO- prefix, deterministic
  statement,
  source_type, nature, status,
  proposal_id,             # required, permanent traceability to R8
  approval_decision_id,    # required, permanent traceability to R9
  temporal_state=None,
  evidence_refs=(),
  provenance=None,
  related_statement_ids=(),
  metadata={},
)
```

Eligibility to compose: `proposal.status == READY_FOR_REVIEW AND approval_decision.proposal_id ==
proposal.proposal_id AND approval_decision.decision == APPROVED AND approval_decision.authority ==
TECHNICAL_LEAD`. `CanonicalKnowledgeCollection` is the **only** collection type in the package — no
parallel `human_truth`/`plugin_truth`/`technical_truth` store exists anywhere in the repository.

## 11. R11 Projection Boundary

* `R11_SOURCE=R10_CANONICAL_KNOWLEDGE`, projection-only; `DocumentProjection` is a read-only,
  in-memory view — it never stores a mutated copy of an entry and never invents one.
* Mapping is via structured `ProjectionRule` conditions only (`source_type`, `nature`, `status`,
  `temporal_state`, closed `metadata["projection_categories"]` tags) — never by parsing
  `statement` text.
* Document tree: one flat, closed tuple of 41 `ProjectionTarget` values under
  `00-el-area/` … `09-capacitacion/` (declared in `legacy_documenter/knowledge/projection/rules.py`).
  `00`, `01`, `02`, `04` use prompt-specified filenames; `03-desarrollo-de-software` (16 documents)
  and the general `05`/`06`/`07`/`08`/`09` documents (`plantillas.md`, `catalogo.md`,
  `proyectos.md`, `historial.md`, `capacitacion.md`) were a Technical-Lead-approved discretionary
  choice recorded in the R11 result document.
* Unmapped entries are preserved and reported in `ProjectionManifest.unmapped_knowledge_ids`, never
  hidden or errored.
* One canonical entry may render into more than one document, always under the identical
  `knowledge_id`.
* Traceability marker: `<!-- knowledge_id: KNO-... -->` after every rendered item; the
  `knowledge_id` is also the item's Markdown heading.
* Empty documents are still generated, with the fixed marker "No approved canonical knowledge is
  currently projected to this document."
* `proposal_id`, `approval_decision_id`, and `evidence_refs` are never rendered into the human
  document — only `knowledge_id` is exposed there.

## 12. R12 Contract Boundary

```text
CONTRACT_NAME    = LegacyMapperPluginKnowledge
CONTRACT_VERSION = 1.0
R12_SOURCE       = R10_CANONICAL_KNOWLEDGE
R11_DEPENDENCY   = NONE
```

* `PluginKnowledgePayload(contract_name, contract_version, canonical_source, entries, manifest)`.
* `PluginKnowledgeEntry.knowledge_id` is always the canonical `KNO-` id — no second Plugin identity
  field exists.
* `ALL_CANONICAL_ENTRIES_PROJECTED`; `SILENT_ENTRY_OMISSION=FORBIDDEN`.
* `CANONICAL_METADATA_DEFAULT=NOT_PROJECTED`: `PluginKnowledgeEntry` has no `metadata` field at
  all — arbitrary `CanonicalKnowledgeEntry.metadata` is never copied into the Plugin payload.
* `PLUGIN_PAYLOAD_IS_PROJECTION`, never canonical knowledge itself.
* Package: `legacy_documenter/knowledge/plugin_projection/` (`models.py`, `service.py`,
  `serializer.py`, `validator.py`, `contract_report.py`, `example_report.py`).

## 13. Deterministic ID Prefixes

| Prefix | Type | Round |
|---|---|---|
| `KST-` | `KnowledgeStatement` | R1 |
| `MAT-` | `MaterialItem` | R1 |
| `EVR-` | `EvidenceRef` | R1 |
| `SRC-` | `SourceInput` | R2 |
| `PRN-` | `ProvenanceNode` | R3 |
| `PED-` | `ProvenanceEdge` | R3 |
| `CLS-` | `ClassificationRecord` | R5 |
| `TMP-` | `TemporalPlacement` | R6 |
| `REL-` | `KnowledgeRelation` | R7 |
| `PRP-` | `Proposal` | R8 |
| `APR-` | `ApprovalDecision` | R9 |
| `KNO-` | `CanonicalKnowledgeEntry` | R10 |

All are derived via the shared `legacy_documenter.documentation.contracts.stable_id` SHA-256-based
helper (a V3 utility, reused unmodified by every V4 round) over semantically load-bearing fields
only — never over `metadata`, current time, randomness, or object identity.
`PluginKnowledgeEntry.knowledge_id` (R12) reuses the `KNO-` id verbatim; it introduces no second
identity scheme.

## 14. Security Invariants (validated by R13)

`TECHNICAL_LEAD_ONLY_APPROVAL`, `AI_CANNOT_APPROVE`, `NO_PROVIDER_CALLS_IN_DETERMINISTIC_V4_CORE`,
`NO_AUTO_STATUS_PROMOTION`, `NO_CANONICAL_MUTATION_FROM_PROJECTIONS`,
`R11_PATH_TRAVERSAL_FORBIDDEN`, `R12_ARBITRARY_METADATA_NOT_PROJECTED`,
`PROMPT_INJECTION_IS_INERT_DATA`, `NO_DYNAMIC_EXECUTION`, `NO_UNSAFE_DESERIALIZATION`,
`SOURCE_CODE_OPTIONAL`, `PLUGIN_RUNTIME_NOT_IMPLEMENTED`. Full detail and evidence:
`output/v4_r13/V4_SECURITY_INVARIANTS.json` and `output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json`.
`CRITICAL_OPEN=0`, `HIGH_OPEN=0` as of R13's closure.

## 15. V5 Boundary

`V5_NOT_IMPLEMENTED`. Full language/framework/technology/project-layout agnosticism at the
source-extraction level is explicitly deferred to a future V5. V4's common knowledge model is
already source-neutral at the *knowledge* level (`SourceType` includes 11 non-code types and
`SOURCE_CODE_OPTIONAL=true`), but the V1–V3 extraction engine that produces
`DETERMINISTIC_CODE_FACT` evidence remains VB.NET/legacy-repository-specific. Do not treat V4 as
having solved extraction-level agnosticism.

## 16. Post-V4 Maintainability Refactor

`POST_V4_MAINTAINABILITY_REFACTOR=PLANNED`, goal `READABILITY_AND_MAINTAINABILITY`,
`BEHAVIOR_CHANGE=FORBIDDEN` unless a later explicit Technical Lead decision authorizes otherwise.
Deferred debt carried forward: V3's `TD-001`..`TD-005` (`output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json`)
plus R13's `DEBT-001`..`DEBT-003` (`output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json` →
`technical_debt`). See `docs/V4/V4_DEVELOPER_MANUAL.md` for what this means for a developer today.
