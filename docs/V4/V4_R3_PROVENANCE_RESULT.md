# V4-R3 Provenance — Result

## Human Authorization / Current State

`V4-R2 — Input / Source Contracts` was explicitly approved and formally closed by the Technical Lead (`docs/V4/V4_R2_CLOSURE_AND_VERSIONING_RESULT.md`, `docs/V4/V4_R2_INPUT_SOURCE_CONTRACTS_RESULT.md`). This approval was not reinterpreted or re-evaluated by this round.

## Required Reading

All fourteen required documents were read: `CLAUDE.md`, `AGENTS.md`, `PROJECT_STATE.json`, `docs/PROJECT_RECOVERY.md`, `docs/V4/V4_AI_HANDOVER.md`, `docs/V4/V4_CONTRACT_FOUNDATION.md`, `docs/V4/V4_PROPOSED_ROADMAP.md`, `docs/V4/V4_R1_KNOWLEDGE_DOMAIN_MODEL_RESULT.md`, `output/v4_r1/V4_KNOWLEDGE_DOMAIN_MODEL_CONTRACT.json`, `docs/V4/V4_R2_INPUT_SOURCE_CONTRACTS_RESULT.md`, `docs/V4/V4_R2_CLOSURE_AND_VERSIONING_RESULT.md`, `output/v4_r2/V4_INPUT_SOURCE_CONTRACTS.json`, `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`, `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`. Existing implementation inspected: `legacy_documenter/knowledge/domain/`, `legacy_documenter/knowledge/input/`, `legacy_documenter/models/evidence.py`, `legacy_documenter/documentation/evidence_catalog.py`, `legacy_documenter/documentation/evidence_resume.py`, `legacy_documenter/documentation/contracts.py`, `legacy_documenter/documentation/human_review.py`. No existing generic graph/DAG implementation was found anywhere in the codebase (`evidence_resume.py` is a one-line CLI wrapper around V3's document-resume workflow; `human_review.py` is V3 text-parsing specific) — R3's `ProvenanceGraph` is genuinely new capability, not a duplicate of something already present.

## Entry Gate

* `python -m unittest discover -s tests` → **726 tests, OK** (pre-R3 baseline).
* `python -m legacy_documenter.knowledge.readiness` → `readiness=READY`, `ai_knowledge_allowed=true`, `ai_knowledge_generated=false`, `provider_calls=0`, `real_llm_calls=0`.
* `V3_BASELINE=VALID`, `V4_R1=APPROVED`, `V4_R1_1=APPROVED`, `V4_R2=APPROVED` (per `PROJECT_STATE.json.round_status=V4-R2_APPROVED`), `PROJECT_STATE.next=V4-R3` — all confirmed from repository state without reinterpreting the prior approval.

`ENTRY_GATE=PASS`

## Reused Components

* `legacy_documenter.knowledge.domain.enums.SourceType` — reused as the node/edge source-type discriminator; not duplicated.
* `legacy_documenter.knowledge.domain.models.Origin` — reused unchanged as `ProvenanceNode.origin`.
* `legacy_documenter.knowledge.domain.models.Provenance` — left untouched; see "R1 Provenance Compatibility" below for its documented relationship to the new graph.
* `legacy_documenter.knowledge.input.contracts.SourceInput` — reused as the input type for `material_node_from_source_input`.
* `legacy_documenter.knowledge.input.normalization.validate_metadata` — reused as-is for both `ProvenanceNode.metadata` and `ProvenanceEdge.metadata`; no second, subtly different metadata validator was created (`models._validate_metadata` only re-wraps its exception type for a single error surface).
* `legacy_documenter.utils.sanitizer.sanitize_text` — reused for `ProvenanceNode.reference`.
* `legacy_documenter.documentation.contracts.stable_id` — reused by `new_node_id`/`new_edge_id` (`PRN-`/`PED-` prefixes) instead of inventing a second hashing scheme.

## New Components

New package `legacy_documenter/knowledge/provenance/`:

* `enums.py` — `NodeKind` (7 values), `EdgeRelationship` (6 values), `TransformationType` (6 values, always optional/never guessed), `LineageCompleteness` (4 values).
* `models.py` — `ProvenanceNode`, `ProvenanceEdge`, `ProvenanceValidationError`, `normalize_node`/`normalize_edge`, `new_node_id`/`new_edge_id`.
* `graph.py` — `ProvenanceGraph` (`add_node`, `add_edge`, `get_node`, `parents_of`, `children_of`, `ancestors_of`, `descendants_of`, `roots_of`, `has_ai_ancestry`, `lineage_completeness`, `validate_graph`, `to_canonical_dict`, `render_canonical_json`) and `material_node_from_source_input` (R2 interop helper).
* `contract_report.py` — `build_provenance_contract` / `render_provenance_contract_json`.

Tests: `tests/test_v4_r3_provenance.py` (40 new test methods).

## Provenance Invariants

* **Edge direction**: canonical direction is EARLIER/SOURCE → LATER/DERIVED (a parent points at its child), used consistently by every traversal method and by serialization. Documented once in `graph.py`'s module docstring; no API mixes directions.
* **Cycle prevention**: `add_edge` rejects a self-loop immediately with a dedicated message, and rejects any edge that would close a longer cycle by checking, before insertion, whether the new edge's destination can already reach its source through existing child edges.
* **Dangling references**: `add_edge` requires both `from_node_id` and `to_node_id` to already exist in the graph; a partial-provenance situation is represented through `LineageCompleteness`, never through an edge pointing at a nonexistent node.
* **Duplicates**: an identical node/edge re-added under the same id is an idempotent no-op; a different node/edge under the same id fails deterministically (`duplicate_*_conflicting_semantics`). Nothing is ever silently merged.
* **Completeness is declared, not inferred**: `ProvenanceNode.provenance_status` defaults to `UNRESOLVED` and is otherwise set explicitly by the caller. `ProvenanceGraph` never promotes a node to `COMPLETE` merely because it has one or more parents, and never demotes an explicit declaration on its own initiative — Python cannot know what lineage a given business object *should* have, so it only stores and returns that declaration. `INVALID` is reserved for `validate_graph()` detecting an actual structural violation; a graph built solely through the public API can never reach that state, so `validate_graph()` exists as an explicit, independent re-check (for example after deserializing a graph assembled elsewhere).
* **AI ancestry never erased**: `has_ai_ancestry` walks the full transitive ancestry, so AI-derived material remains detectable no matter how many `DERIVED_FROM`/`INTERPRETED_FROM` hops separate a downstream node from it.
* **No authority/approval field anywhere**: neither `ProvenanceNode` nor `ProvenanceEdge` has an `authoritative`, `approved`, or `approval_status` field. This is structural, not a runtime check — the graph is incapable of expressing authority or approval, by design.

## R1 Provenance Compatibility

`legacy_documenter.knowledge.domain.models.Provenance` (`origin`, `material_ids`, `evidence_ids`, `contributor`, `notes`) is preserved unchanged and remains **the compact, per-`KnowledgeStatement` provenance summary** — the answer to "what backs this one statement," attached directly to it. `ProvenanceGraph` is **the full deterministic multi-node/multi-edge lineage structure** — the answer to "what is the complete traceable history across many statements/materials/evidence." Neither replaces the other: `Provenance.material_ids`/`evidence_ids` and `ProvenanceGraph.parents_of(...)` can describe the same underlying facts from two authoritative angles (a test demonstrates `provenance.material_ids == graph.parents_of(evidence_node_id)` for the same lineage). No R1 file was modified.

## R2 SourceInput Compatibility

`graph.material_node_from_source_input(source_input)` maps a validated `SourceInput` onto a `MATERIAL`-kind `ProvenanceNode` (`source_type`, `reference`, `origin`, and `title` via `metadata`), with a deterministic id derived from the input's normalized fields when none is supplied. This demonstrates the required `SourceInput -> Material provenance node` linkage without implementing R4 ingestion: no document is parsed, no filesystem is scanned, no network call occurs. A human-only `SourceInput` (`HUMAN_REQUIREMENT`, no code fields) round-trips into a valid node with `reference=None`, confirmed by test.

## Security Notes

* `ProvenanceNode.reference` and every string inside `ProvenanceNode.metadata` / `ProvenanceEdge.metadata` are sanitized (via the existing `sanitize_text`/R2 metadata validator) inside `normalize_node`/`normalize_edge`, before validation runs — so a rejected node/edge's exception message is already built from sanitized data.
* A fake secret (`Password=clave123`) was tested in a node's `reference` and in `metadata`; it is redacted to `Password=********` and does not appear in the node, in `render_canonical_json()`, or in the contract/example artifacts.
* No file, network, or provider I/O occurs anywhere in `legacy_documenter/knowledge/provenance/`. A `reference` is stored and sanitized as a string only; nothing in R3 opens, fetches, or dereferences it.

## Technical Debt

No unrelated refactoring was performed. `TD-005` (explicit type hints) was followed for every new public class/function in the `provenance` package. No provider code was touched (`TD-002` not applicable here). R2's metadata validator was reused rather than re-implemented, directly avoiding a new instance of `TD-003` (cross-round helper duplication) in this round.

## Result

```text
STATUS=V4_R3_PROVENANCE_COMPLETE
ENTRY_GATE=PASS
BASELINE_TESTS=726_PASS
FINAL_TESTS=766_PASS

PROVENANCE_MODEL=NODE_EDGE_GRAPH(ProvenanceNode+ProvenanceEdge+ProvenanceGraph)
NODE_KINDS=SOURCE,MATERIAL,EVIDENCE,STATEMENT,INTERPRETATION,PROPOSAL,KNOWLEDGE
EDGE_RELATIONSHIPS=ORIGINATES_FROM,MATERIALIZED_FROM,EVIDENCE_FROM,DERIVED_FROM,INTERPRETED_FROM,REFERENCES
TRANSFORMATION_TYPES=DETERMINISTIC_EXTRACTION,NORMALIZATION,HUMAN_SUPPLIED,AI_INTERPRETATION,AGGREGATION,MANUAL_CORRECTION(optional;never_guessed)
COMPLETENESS_STATES=COMPLETE,PARTIAL,UNRESOLVED,INVALID
EDGE_DIRECTION=EARLIER_SOURCE_TO_LATER_DERIVED

SOURCE_NEUTRAL=PASS
CODE_ONLY=PASS
HUMAN_INFORMATION_ONLY=PASS
CODE_AND_HUMAN_INFORMATION=PASS
PARTIAL_INFORMATION=PASS

MULTI_PARENT_LINEAGE=PASS
ROOT_DISCOVERY=PASS
CYCLE_DETECTION=PASS(self_two_node_and_longer_cycles_rejected)
DANGLING_REFERENCE_VALIDATION=PASS
DUPLICATE_HANDLING=PASS(same_content_idempotent;conflicting_content_rejected)

STABLE_IDENTITY=PASS(PRN-/PED-_prefixes_via_stable_id)
DETERMINISTIC_ORDERING=PASS(all_traversal_results_sorted)
DETERMINISTIC_SERIALIZATION=PASS(insertion_order_independent)

AI_ANCESTRY=PASS(direct_and_multi-level_indirect_detected)
HUMAN_ORIGIN_PRESERVATION=PASS
AUTHORITY_SEPARATION=PASS(no_authority_field_exists_on_node_or_edge)
APPROVAL_SEPARATION=PASS(no_approval_field_exists_on_node_or_edge)

R1_PROVENANCE_RELATIONSHIP=DEFINED(R1_Provenance=compact_per-statement_summary;ProvenanceGraph=full_lineage_structure;both_coexist)
R2_INPUT_RELATIONSHIP=DEFINED(material_node_from_source_input)

METADATA_VALIDATION=PASS(reused_R2_validator)
SANITIZATION=PASS(reused_existing_sanitizer)
SECURITY=PASS
NO_IO=PASS

CONTRACT_ARTIFACT=output/v4_r3/V4_PROVENANCE_CONTRACT.json
CONTRACT_SHA256=734d6985783cb7a171aec9952dd9534077fef0ca09fef084179800cd98b1eb2d
EXAMPLE_ARTIFACT=output/v4_r3/V4_PROVENANCE_EXAMPLE.json
DETERMINISM=PASS

V3_REGRESSION=PASS(676_of_676_pre-existing_still_pass)
V4_R1_REGRESSION=PASS(14_of_14_R1_tests_still_pass)
V4_R2_REGRESSION=PASS(50_of_50_R2_tests_still_pass)

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=UPDATED(latest_completed_round=V4-R3;latest_approved_round=V4-R2;round_status=V4-R3_READY_FOR_HUMAN_REVIEW;next=HUMAN_REVIEW_V4_R3)
PRODUCTION_BEHAVIOR_CHANGED=V4_ADDITIVE_ONLY
TECHNICAL_DEBT=TD-005_ADDRESSED_FOR_NEW_CODE;TD-002_NOT_APPLICABLE;TD-003_AVOIDED_VIA_REUSE

DECISION=V4_R3_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R3
```

## Out of Scope — Confirmed Not Implemented

No human-document ingestion occurred (R4). No knowledge classification (R5). No AS_IS/TO_BE separation logic beyond the closed enum already in R1 (R6). No gap/conflict detection (R7). No proposal lifecycle (R8). No Technical Lead approval workflow (R9). No canonical Knowledge Source composition or human-readable/Plugin-facing projections (R10/R11/R12). No V5 agnosticism work. No real LLM/provider call was made; `AI_INTERPRETATION` and its transformation type are exercised only through fixtures.

Stop. `V4-R4` has not been implemented. `V4-R3` is not marked human-approved; no commit or push was performed during this round.

## Closure — Human Approval Recorded

This section was added by `V4_R3_APPROVAL_AND_VERSIONING`; nothing above it was altered.

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD
ROUND_STATUS=APPROVED
DECISION=V4_R3_FORMALLY_APPROVED
NEXT=V4-R4
```

The Technical Lead's approval was issued outside the development agent and is recorded here as authoritative; it was not re-evaluated or independently granted by the agent. See `docs/V4/V4_R3_CLOSURE_AND_VERSIONING_RESULT.md` for the full closure/versioning record.
