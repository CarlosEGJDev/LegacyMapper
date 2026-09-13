# LegacyMapper V4.1-R2 — Models, Types and Public Contracts Readability — Result

## STATUS
`V4_1_R2_IMPLEMENTATION_COMPLETE`

## ENTRY_GATE
`PASS`. `git status` showed only the R2 prompt file untracked (as expected) before any edit. `python -m unittest discover -s tests` produced 1424 PASS / 0 FAIL. `python -m legacy_documenter.knowledge.readiness` reported `READY`, `ai_knowledge_allowed=true`, `ai_knowledge_generated=false`, `provider_calls=0`, `real_llm_calls=0`.

## BASELINE_TESTS
`1424_PASS` (0 FAIL)

## FINAL_TESTS
`1442_PASS` (0 FAIL, 0 SKIP) — 1424 pre-existing + 18 new R2 tests.

## TD_005_ORIGINAL_DESCRIPTION
Resolved verbatim from `output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json`'s `known_debt` array (sourced from `output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json`):

> "Ambiguous nested historical JSON shapes were not annotated with misleading object/Any types."

Affected files listed there: `legacy_documenter/documentation/*.py`, `legacy_documenter/analysis/*.py`, `legacy_documenter/extractors/*.py`. Recommended action: "Introduce narrow TypedDict/dataclass models only at boundaries a round is already modifying for another reason; do not retrofit typing repository-wide in one pass." Recommended round: "V4.1-R2 / V4.1-R4 (incremental, per touched boundary)".

## TD_005_STATUS
`PARTIALLY_RESOLVED`

## TD_005_REMAINING_WORK
R2 added narrow, safe return-type annotations (and one small type alias, `EvidenceKeyMap`) to functions in 11 of the 16 files R0's `type_safety_candidates` section identified, wherever a function's return shape was unambiguous and stable. It deliberately did **not**:
- Annotate function parameters carrying ambiguous, heterogeneous, historically-open nested JSON dict/list shapes (`document`, `assessment`, `package`, `payload`, `catalog`, `pool`, `plan`, etc.) across `legacy_documenter/documentation/*.py` and `legacy_documenter/analysis/*.py` — no stable, non-misleading TypedDict/dataclass shape could be proven for them without a structural characterization pass, which is exactly the risk TD-005's original description warns against.
- Touch `legacy_documenter/analysis/deep_source.py` (R0 characterization-sensitive, Step 5 — deferred).
- Annotate `legacy_documenter/documentation/generator.py`, `consistency_run.py`, `hierarchical.py`, or other `run()`/`execute()` orchestration functions, because their return shape differs per branch (an early-return failure path returns a different key set than the success path); a single return annotation would misrepresent the contract.
- Touch `legacy_documenter/extractors/*.py` — none of those files appeared in R0's `type_safety_candidates` list (their `typed_functions_percent` was already at/above the repository average), so there was no R0 evidence to act on.

Full resolution would require a dedicated characterization round that first proves a stable per-boundary shape (via fixture-based characterization tests) before introducing any TypedDict/dataclass at that boundary — exactly R0's own `recommended_action`.

## CANDIDATES_CONSIDERED
16 (all entries in `output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json`'s `type_safety_candidates` array).

## CANDIDATES_CHANGED
11 files: `legacy_documenter/documentation/{contracts,interpretation,renderer,aggregation,consistency,evidence_catalog,envelope,coverage,human_review}.py`, `legacy_documenter/analysis/{deep_interpretation,targeted_exhaustion}.py`. Within these files, only individual functions/methods/properties with an unambiguous, stable return type (and, in a few cases, parameters that were already fully-typed dataclasses) received annotations — never the ambiguous nested-JSON parameters. See `output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json`'s `public_symbols` array for the exact per-symbol list (33 symbols).

## CANDIDATES_DEFERRED
5 files/groups, each with a recorded reason (full detail in the equivalence artifact's `candidates_deferred`):
1. `legacy_documenter/analysis/deep_source.py` — R0 Step-5 characterization-sensitive module.
2. `legacy_documenter/documentation/generator.py` — heterogeneous per-branch `run()`/`_request()`/`_strict()` returns.
3. `legacy_documenter/documentation/consistency_run.py` — same heterogeneous-return-shape reasoning.
4. `legacy_documenter/documentation/hierarchical.py` — same heterogeneous-return-shape reasoning.
5. Every ambiguous-nested-JSON *parameter* across the 11 changed files (e.g. `document`, `assessment`, `package`, `payload`, `pool`, `plan`, `catalog`) — classified `UNKNOWN`/`SIMILAR_SHAPE_DIFFERENT_SEMANTICS` per Step 7's no-premature-abstraction rule, left as implicit `Any` (`NECESSARY_DYNAMIC_BOUNDARY`).

## AFFECTED_PRODUCTION_FILES
```
legacy_documenter/analysis/deep_interpretation.py
legacy_documenter/analysis/targeted_exhaustion.py
legacy_documenter/documentation/aggregation.py
legacy_documenter/documentation/consistency.py
legacy_documenter/documentation/contracts.py
legacy_documenter/documentation/coverage.py
legacy_documenter/documentation/envelope.py
legacy_documenter/documentation/evidence_catalog.py
legacy_documenter/documentation/human_review.py
legacy_documenter/documentation/interpretation.py
legacy_documenter/documentation/renderer.py
```
(Plus `tests/test_v4_1_r0_maintainability_inventory.py`, extended — not weakened — to authorize this round's expected, mechanical `typed_functions_percent`/`type_safety_candidates` shift in its live-vs-frozen R0 inventory comparison, following the exact precedent the test's own docstring already establishes for R1's DUP-001 change.)

## AFFECTED_PUBLIC_SYMBOLS
33 symbols (functions, methods, one property group, one new type alias). Full table with `current_signature`/`proposed_signature`/`import_path`/`callers_found`/`runtime_contract_changed` is in `output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json` under `public_symbols`. Every entry has `runtime_contract_changed: false`.

## NEW_TYPEDDICTS
None. No mapping shape in the touched files was proven stable/deterministic enough to justify a `TypedDict` under this round's policy (every candidate mapping was either historically heterogeneous or an intentionally open extension point).

## NEW_TYPE_ALIASES
One: `legacy_documenter.documentation.evidence_catalog.EvidenceKeyMap = dict[str, str]` — maps a request-local evidence key (e.g. `"E01"`) to its canonical evidence id. Documented inline; used as a local-variable annotation inside `resolve_payload`. Carries real domain meaning (distinguishes the closed, fixed-shape key-resolution mapping from the open evidence records it resolves), unlike a rejected `StringList`-style alias.

## ANNOTATIONS_ADDED
33 return-type annotations/parameter clarifications across 11 files (see `public_symbols` in the equivalence artifact for the itemized list). No parameter annotation was added to any function whose parameter carries an ambiguous/open nested-JSON shape.

## ANY_CLASSIFICATION
All `Any`-shaped (implicit, unannotated) parameters encountered in the 11 touched files were classified `NECESSARY_DYNAMIC_BOUNDARY` (open/historically-evolved JSON dict/list shapes with no single stable contract) or `DEFER` (orchestration return values whose shape differs per branch). No `SAFE_TO_NARROW` classification was applied in this round — no candidate was found where a narrower type could be proven accurate without a characterization pass. Full list with justifications is under `dynamic_boundaries_preserved` in the equivalence artifact.

## DYNAMIC_BOUNDARIES_PRESERVED
`PASS` — every boundary classified `NECESSARY_DYNAMIC_BOUNDARY` remains unannotated/dynamic; confirmed by `tests/test_v4_1_r2_models_types_and_public_contracts.py::DynamicBoundariesPreservedTests`, which calls `aggregate()` and `build_catalog()` with deliberately extra-keyed/heterogeneous fixtures and confirms they are still accepted.

## HIGH_RISK_MODULES_TOUCHED
None.

## HIGH_RISK_MODULES_DEFERRED
```
legacy_documenter/extractors/database_extractor.py
legacy_documenter/analysis/flow_resolver.py
legacy_documenter/knowledge/readiness.py
legacy_documenter/documentation/resume.py
legacy_documenter/analysis/deep_source.py
```
Confirmed byte-identical (SHA-256 spot-check) and AST-top-level-shape-identical to their pre-R2 state via `tests/test_v4_1_r2_models_types_and_public_contracts.py::HighRiskModulesUntouchedTests`.

## PUBLIC_RUNTIME_CONTRACT_CHANGED
`false`

## PUBLIC_CALL_COMPATIBILITY
`PASS`

## MODEL_FIELD_EQUIVALENCE
`PASS` — no dataclass field was added, removed, reordered, or renamed. Verified for `MetricFact`, `EvidenceReference`, `DocumentClaim`, `MissingInformation`, `DocumentMetadata`, `FunctionalModule`, `ArchitecturePatternAssessment`, `DocumentationContract`, `DocumentationProfile`, `DocumentationPrompt` via `dataclasses.fields()` introspection in the new test module.

## MODEL_DEFAULT_EQUIVALENCE
`PASS` — defaults/default factories/frozen state unchanged (e.g. `MetricFact.status` default `"CONFIRMED"` and `frozen=True`; `EvidenceReference.authoritative` default `False`; `DocumentationContract`'s list fields' `default_factory` still produce lists) — verified by the same tests.

## SERIALIZED_OUTPUT_EQUIVALENCE
`PASS` — `MetricFact.to_dict()`, `render()`, `stable_hash()`, `stable_id()`, and `hid()` were exercised for repeatability (same input -> byte-identical/structurally-identical output across repeated calls); none of these functions' bodies were modified, only their signatures gained a return annotation.

## APPROVED_ARTIFACT_HASHES_UNCHANGED
`PASS` (spot-check). None of the R2-touched files are imported by `legacy_documenter/knowledge/*` or by any V4 R7-R14 artifact generator (confirmed by grep — R2 touched only `legacy_documenter/analysis/*.py` and `legacy_documenter/documentation/*.py`). Spot-checked hashes, unchanged:
- `output/v4_r14/V4_FINAL_BASELINE.json` = `d13e3807a12187b226ea55752ae0e9dccd2ad20c9dbe044360ffa48bca526d1e`
- `output/v4_r14/V4_FINAL_MANIFEST.json` = `be398240a31137e7dea25fcaa7b3cfe6580d2557f990f7da884d5775f5c40551`
- `output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json` = `55c99c3b68ac159585c6a0ec7e05f74e8dd64dd871308d067ab27bdda1a1c33b`

The only historical artifact whose *live rebuild* diverges from its frozen on-disk form is `output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json` — expected, because R2 legitimately raised `typed_functions_percent` for 5 of its own `type_safety_candidates` files. The frozen file itself was **not** modified or regenerated (no hash change to the file); only `tests/test_v4_1_r0_maintainability_inventory.py`'s live-vs-frozen comparison test was extended to authorize this exact, explained diff — the same pattern that test already used for R1's DUP-001 change.

## TYPE_AND_CONTRACT_EQUIVALENCE_ARTIFACT
`output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json`

## TYPE_AND_CONTRACT_EQUIVALENCE_ARTIFACT_SHA256
`bd3daf04be868ef6465298c5e372aacc1f33bf234417f2bb914b79b22ab5a6f4`

## TYPE_AND_CONTRACT_EQUIVALENCE_ARTIFACT_DETERMINISM
`PASS` — generated twice independently from the same generator script; both outputs were byte-identical (`diff` empty, same SHA-256).

## TYPING_DIAGNOSTICS_BEFORE
`typed_functions_percent` (AST diagnostic, `tools/v4_1_r0/inventory.py`; a function counts as "typed" only when every non-`self` parameter and its return are annotated), before R2:
```
contracts.py=0.0  interpretation.py=0.0  consistency.py=0.0  coverage.py=0.0
human_review.py=0.0  evidence_catalog.py=0.0  aggregation.py=0.0  envelope.py=0.0
renderer.py=0.0  deep_interpretation.py=0.0  targeted_exhaustion.py=0.0
```

## TYPING_DIAGNOSTICS_AFTER
```
contracts.py=83.33  interpretation.py=50.0  consistency.py=7.14  coverage.py=11.11
human_review.py=22.22  evidence_catalog.py=0.0  aggregation.py=0.0  envelope.py=0.0
renderer.py=0.0  deep_interpretation.py=0.0  targeted_exhaustion.py=0.0
```
Six files show `0.0` before and after despite gaining return-type annotations: the diagnostic only credits a function once *every* parameter is also typed, and this round deliberately left the ambiguous nested-JSON parameters on those functions untyped. This is expected under `DO_NOT_TYPE_FOR_METRICS` — these numbers are supporting evidence, not an optimization target. Side effect: 5 files (`contracts.py`, `interpretation.py`, `consistency.py`, `coverage.py`, `human_review.py`) moved off R0's relative below-average `type_safety_candidates` list; 5 previously-just-above-average files became newly below-average as the repository mean shifted (`synthesis.py`, `llm/copilot_pilot.py`, `systematic.py`, `resume.py`, `second_review.py`) — a mechanical consequence of a relative-threshold diagnostic, not a behavior change.

## V4_CONTRACTS_UNCHANGED
`PASS`

## R11_BOUNDARY
`PASS` — no R2-touched file lies under `legacy_documenter/knowledge/`; `legacy_documenter/knowledge/projection` and `legacy_documenter/knowledge/plugin_projection` still do not cross-import (verified by `tests/test_v4_1_r2_models_types_and_public_contracts.py::BoundaryDirectionTests` and the full existing suite).

## R12_BOUNDARY
`PASS`. `PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge`, `PLUGIN_CONTRACT_VERSION=1.0` unchanged (untouched code). `PLUGIN_RUNTIME=NOT_IMPLEMENTED` (unchanged).

## PRODUCTION_CODE_CHANGED
`true`

## PRODUCTION_BEHAVIOR_CHANGED
`false`

## READINESS
`READY`

## AI_KNOWLEDGE_ALLOWED
`true`

## AI_KNOWLEDGE_GENERATED
`false`

## REAL_LLM_CALLS
`0`

## PROVIDER_CALLS
`0`

## PROJECT_STATE
Updated: `latest_completed_round="V4.1-R2"`, `latest_approved_round="V4.1-R1"` (unchanged — V4.1-R2 is not approved by this round), `current_round_in_progress="V4.1-R2 (pending Technical Lead review)"`, `round_status="V4_1_R2_READY_FOR_HUMAN_REVIEW"`, `next="HUMAN_REVIEW_V4_1_R2"`, `tests=1442`, `readiness="READY"`, `ai_knowledge_allowed=true`, `ai_knowledge_generated=false`, `provider_calls=0`, `real_llm_calls=0`. V4 closure fields untouched.

## DECISION
`V4_1_R2_READY_FOR_HUMAN_REVIEW`

## NEXT
`HUMAN_REVIEW_V4_1_R2`

---

## Narrative Summary

R2 scoped its work strictly to R0's own `type_safety_candidates` evidence (16 files, all with `typed_functions_percent=0.0`). After reading every one of those files in full, the code turned out to be dense, single-line-per-function V1/V3-era code that assembles and forwards heterogeneous, historically-evolved JSON dict/list shapes via `{**x, ...}` merges and dict comprehensions — precisely the "ambiguous nested historical JSON shapes" TD-005 itself warns were deliberately left untyped rather than mistyped. Given the round's governing principle (`TYPE_WHERE_IT_CLARIFIES`, `DO_NOT_TYPE_FOR_METRICS`, `BEHAVIOR_CHANGE=FORBIDDEN`) and the explicit instruction to defer any uncertain candidate, the safe and honest scope was: add return-type annotations only where a function's return shape was provably stable and unambiguous (booleans, strings, ints, `Path`, small tuples, or dataclasses whose shape was already fully typed), and introduce exactly one small type alias (`EvidenceKeyMap`) where a genuinely stable, narrow mapping shape existed. Parameters carrying open/heterogeneous JSON, and orchestration functions whose return shape differs by branch, were left untyped and documented as `NECESSARY_DYNAMIC_BOUNDARY` or `DEFER`.

This produced 33 annotated public symbols across 11 files with zero parameter-shape guesses, zero TypedDicts (none of the inspected mapping shapes met the "stable, deterministic" bar), and zero calling-convention changes. The one existing test that needed updating (`test_v4_1_r0_maintainability_inventory.py`'s live-vs-frozen R0 inventory comparison) was extended — following the exact precedent it already established for R1's DUP-001 extraction — to authorize the expected, explained `typed_functions_percent`/`type_safety_candidates` shift, rather than weakened or skipped. A new focused test module (18 tests) covers import resolution, calling-convention preservation, dataclass/model equivalence, serialization determinism, approved-artifact-hash spot-checks, the new type alias's behavior, dynamic-boundary preservation, high-risk-module non-modification, R11/R12 boundary integrity, readiness, and absence of new network/provider imports.

TD-005 is therefore classified `PARTIALLY_RESOLVED`: the safe, high-value portion (annotating unambiguous return shapes at 11 files) is done; the harder, genuinely valuable portion (proving stable per-boundary shapes for the ambiguous nested JSON that flows through `documentation/*.py` and `analysis/*.py`, and for the four heterogeneous-return orchestrators) remains and requires a dedicated characterization round, exactly as R0's own `recommended_action` anticipated.

No approved V4/V4.1 artifact hash changed. No dataclass/model shape changed. No public calling convention changed. The full regression suite grew from 1424 to 1442 passing tests with zero failures and zero skips. Readiness remains `READY` with zero provider/LLM calls throughout. This round is submitted for human review; it does not approve itself, commit, push, or begin R3.

## Closure — Human Approval Recorded

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

TD_005_DECISION=PARTIALLY_RESOLVED_APPROVED

TYPE_SAFETY_SCOPE_DECISION=APPROVED
DYNAMIC_BOUNDARY_DECISION=APPROVED
HIGH_RISK_DEFERRAL_DECISION=APPROVED

TYPE_AND_CONTRACT_EQUIVALENCE_DECISION=APPROVED

R2_1_REQUIRED=false

ROUND_STATUS=APPROVED

DECISION=V4_1_R2_FORMALLY_APPROVED

NEXT=V4.1-R3
```
