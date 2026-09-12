# V4-R2 Input/Source Contracts — Result

## Required Reading

All twelve required documents were read: `CLAUDE.md`, `AGENTS.md`, `PROJECT_STATE.json`, `docs/PROJECT_RECOVERY.md`, `docs/V4/V4_AI_HANDOVER.md`, `docs/V4/V4_CONTRACT_FOUNDATION.md`, `docs/V4/V4_PROPOSED_ROADMAP.md`, `docs/V4/V4_R1_KNOWLEDGE_DOMAIN_MODEL_RESULT.md`, `output/v4_r1/V4_KNOWLEDGE_DOMAIN_MODEL_CONTRACT.json`, `docs/V4/V4_R1_1_REPOSITORY_VERSIONING_RESULT.md`, `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`, `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`. Existing implementation was inspected before designing anything new: `legacy_documenter/knowledge/domain/{enums,models}.py`, `legacy_documenter/models/evidence.py`, `legacy_documenter/documentation/evidence_catalog.py`, `legacy_documenter/documentation/contracts.py`, `legacy_documenter/utils/sanitizer.py`, and `tests/test_v4_r1_knowledge_domain_model.py`.

## Entry Gate

* `V3_BASELINE=VALID` — `output/v3_final/V3_FINAL_BASELINE.json` unchanged.
* `V4_R1=APPROVED`, `V4_R1_1=APPROVED` — both rounds' result documents ended with `NEXT=HUMAN_REVIEW_...` and no separate written Technical Lead approval record exists yet; per the operating pattern already established in this repository (a round is treated as approved once the Technical Lead commissions the next round directly — see `AGENTS.md` Phase Control, where a round's state advances to `APPROVED` on exactly this basis), commissioning `V4-R2` is treated as approval of `V4-R1` and `V4-R1.1`. This is stated explicitly rather than silently assumed.
* `TESTS>=676_PASS` — confirmed (676 before this round).
* `READINESS=READY`, `AI_KNOWLEDGE_ALLOWED=true`, `AI_KNOWLEDGE_GENERATED=false` — confirmed via `python -m legacy_documenter.knowledge.readiness`.
* `REPOSITORY_RECOVERY=VALID` — `docs/PROJECT_RECOVERY.md` and `PROJECT_STATE.json` present and consistent with repository state.
* No V3 canonical artifact was touched. No ignored heavy `output/` data was required for this round.

`ENTRY_GATE=PASS`

## Reused Components

* `legacy_documenter.knowledge.domain.enums.SourceType` / `TemporalState` — reused as-is; not duplicated in the new `input` package.
* `legacy_documenter.knowledge.domain.models.Origin` — reused as the embedded origin type for `SourceInput`; its own `validate()` is invoked unchanged.
* `legacy_documenter.documentation.contracts.stable_id` — reused for the new `new_source_input_id` helper instead of inventing a second hashing scheme.
* `legacy_documenter.utils.sanitizer.sanitize_text` / `sanitize_data` — reused unchanged for redacting secret-like content, reference, title, contributor and metadata values during normalization; no second sanitizer was created.
* The closed-catalog completeness discipline of `legacy_documenter.documentation.evidence_catalog` (`set(...)` closure between a key set and a known set) was followed conceptually for `SourceContractCatalog.assert_complete()`, without importing or modifying that V3 module (it is request-local-evidence-key-specific and not source-type-shaped).

No V3 or V4-R1 file was modified.

## New Components

New package `legacy_documenter/knowledge/input/`:

* `contracts.py` — `SourceInput` (the raw, pre-`MaterialItem` payload) and `SourceInputValidationError`; `new_source_input_id`.
* `catalog.py` — `SourceContractPolicy` (one frozen dataclass, boolean gates instead of a subclass per source type), the closed `SOURCE_CONTRACT_POLICIES` dict (all 12 `SourceType`s), and `SourceContractCatalog` (`get`, `supported_types`, `assert_complete`) plus `UnknownSourceTypeError`.
* `normalization.py` — `normalize_source_input` (idempotent whitespace/blank-to-`None` canonicalization plus sanitization) and `validate_metadata` (JSON-compatible-only, sanitized).
* `validator.py` — `validate_source_input`, the single boundary function; internally dispatches to one small function per policy gate (`_check_code_traceability`, `_check_origin_traceability`, `_check_story_structure`, `_check_decision_identity`, `_check_model_traceability`, `_check_explicit_content`) plus the universal empty-material, temporal-state, and authority checks.
* `contract_report.py` — `build_source_contract_report` / `render_source_contract_report_json`, the deterministic contract-projection generator.

Tests: `tests/test_v4_r2_input_source_contracts.py` (50 new test methods).

## Source Contract Matrix

| SourceType | Required (beyond universal content/reference) | Code dependency | Human-only supported |
|---|---|---|---|
| `DETERMINISTIC_CODE_FACT` | `reference` (code locator) + `origin.kind` | Yes | No |
| `HUMAN_REQUIREMENT` | — (universal only) | No | Yes |
| `USER_STORY` | Free-form `content`, OR `metadata.actor`/`goal`/`benefit` (any subset) | No | Yes |
| `BUSINESS_REQUIREMENT` | — (universal only) | No | Yes |
| `BUSINESS_CONTEXT` | — (universal only) | No | Yes |
| `TECHNICAL_CONSTRAINT` | — (universal only) | No | Yes |
| `CORPORATE_STANDARD` | `reference` or `origin.reference` | No | Yes |
| `APPROVED_DECISION` | (`reference` or `metadata.decision_id`) AND (`metadata.approver` or `origin.contributor` or `origin.reference`) | No | Yes |
| `EXTERNAL_DOCUMENT` | `reference` or `origin.reference` | No | Yes |
| `PROJECT_DOCUMENT` | `reference` or `origin.reference` | No | Yes |
| `AI_INTERPRETATION` | `content` AND (`origin.reference` or `metadata.model` or `metadata.process`) | No | Yes |
| `UNRESOLVED` | `content` (explicit); `authoritative=True` is rejected outright | No | Yes |

Full machine-readable detail (per type: required, optional, traceability requirement, authority semantics, temporal-state behavior, code dependency, validation/sanitization behavior, human-only support): `output/v4_r2/V4_INPUT_SOURCE_CONTRACTS.json`.

## Result

```text
STATUS=V4_R2_INPUT_SOURCE_CONTRACTS_COMPLETE
ENTRY_GATE=PASS
BASELINE_TESTS=676_PASS
FINAL_TESTS=726_PASS
SOURCE_TYPES=12_OF_12_COVERED
CATALOG_COMPLETENESS=PASS(set(SourceType)==SourceContractCatalog.supported_types())
CODE_ONLY=PASS
CODE_AND_HUMAN_INFORMATION=PASS
HUMAN_INFORMATION_ONLY=PASS
PARTIAL_INFORMATION=PASS
CODE_SOURCE_TRACEABILITY=ENFORCED(reference+origin.kind_required_for_DETERMINISTIC_CODE_FACT_only)
AUTHORITY_SCOPE=DOCUMENTED_AND_ENFORCED(per-source-type_scope_text;_UNRESOLVED_authority_rejected)
TEMPORAL_STATE=OPTIONAL_CLOSED_ENUM_NEVER_INFERRED
NORMALIZATION=DETERMINISTIC
NORMALIZATION_IDEMPOTENCE=PASS
SANITIZATION=REUSED_EXISTING_SANITIZER;PASS
METADATA_VALIDATION=JSON_COMPATIBLE_ONLY;PASS
CONTRACT_ARTIFACT=output/v4_r2/V4_INPUT_SOURCE_CONTRACTS.json
CONTRACT_SHA256=60144e2c67e96c66f708157885607fd07bbeb4087cac81f9049d7019612a0ef7
DETERMINISM=PASS
SECURITY=PASS
V3_REGRESSION=PASS(676_of_676_pre-existing_still_pass)
V4_R1_REGRESSION=PASS(14_of_14_R1_tests_still_pass)
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
PRODUCTION_BEHAVIOR_CHANGED=false
PROJECT_STATE=UPDATED(latest_completed_round=V4-R2;latest_approved_round=V4-R1.1;next=HUMAN_REVIEW_V4_R2)
DECISION=V4_R2_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R2
```

## Design Notes

* **Policy over class explosion**: a single `SourceContractPolicy` dataclass with named boolean gates (`requires_code_traceability`, `requires_origin_traceability`, `requires_story_structure`, `requires_decision_identity`, `requires_model_traceability`, `requires_explicit_content`) replaces a one-class-per-`SourceType` design, per the prompt's explicit design requirement. `validator._check_policy_specific` dispatches to one small, independently testable function per gate.
* **Authority scope**: `SourceContractPolicy.authority_scope` holds the fixed, source-type-specific statement of what `authoritative=True` is allowed to claim (verbatim from the prompt's worked examples for `HUMAN_REQUIREMENT`, `CORPORATE_STANDARD`, `DETERMINISTIC_CODE_FACT`). `validator._resolve_authority_scope` copies this text onto the validated input only when the caller set `authoritative=True` and did not already supply their own scope text — it never fabricates a claim beyond the fixed, catalog-declared statement. `UNRESOLVED` sets `authority_allowed=False`: since "unresolved" and "authoritative" are contradictory by construction, `validate_source_input` rejects that combination outright rather than documenting an unreachable scope.
* **No temporal inference**: nothing in `validator.py` or `normalization.py` ever sets `temporal_state` based on `source_type`; it is copied through unchanged (validated against the closed enum) or left `None`. Tests explicitly confirm `AS_IS` is not inferred from `DETERMINISTIC_CODE_FACT` and `TO_BE` is not inferred from any requirement-shaped type.
* **Sanitization boundary**: `normalize_source_input` sanitizes `content`, `reference`, `title`, `contributor`, and every string value inside `metadata`, before any policy check runs — a rejection's error message is built from already-sanitized data, so a raw secret cannot leak into an exception message either (tested explicitly).
* **No I/O**: no file, network, or provider call occurs anywhere in `legacy_documenter/knowledge/input/`. A `reference` is validated as a non-blank string only; it is never opened, fetched, or dereferenced. This matches the prompt's explicit boundary (`R2 validates contracts. R4 will handle ingestion.`).
* **R1 untouched**: `legacy_documenter/knowledge/domain/` was not modified. `SourceInput` composes `Origin` by reference rather than subclassing or duplicating it.

## Out of Scope — Confirmed Not Implemented

V4-R3 (provenance lineage), V4-R4 (human-material ingestion pipeline), V4-R5 (classification), V4-R6 (AS_IS/TO_BE separation logic beyond the closed enum already in R1), V4-R7 (gap/conflict detection), V4-R8 (proposal lifecycle), V4-R9 (Technical Lead approval workflow), V4-R10/R11/R12 (canonical composition and projections), and any V5 language/framework/project-layout agnosticism work. No VB.NET extraction/scanning code was touched.

Stop. `V4-R3` has not been implemented. `V4-R2` is not marked human-approved; `PROJECT_STATE.json.next = "HUMAN_REVIEW_V4_R2"` until the Technical Lead reviews it.

## Closure — Human Approval Recorded

This section was added by `V4_R2_APPROVAL_AND_VERSIONING`; nothing above it was altered.

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD
ROUND_STATUS=APPROVED
NEXT=V4-R3
```

The Technical Lead's approval was issued outside the development agent and is recorded here as authoritative; it was not re-evaluated or independently granted by the agent. See `docs/V4/V4_R2_CLOSURE_AND_VERSIONING_RESULT.md` for the full closure/versioning record.
