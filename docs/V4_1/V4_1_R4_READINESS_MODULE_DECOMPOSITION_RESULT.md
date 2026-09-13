# LegacyMapper V4.1-R4 -- Readiness Module Decomposition -- Result

```text
STATUS=V4_1_R4_IMPLEMENTATION_COMPLETE
```

---

## ENTRY_GATE

```text
ENTRY_GATE=PASS
```

- `git status`: clean except `prompts/V4_1/V4_1_R4_READINESS_MODULE_DECOMPOSITION.md` (expected untracked prompt file). Confirmed before any edit.
- `python -m unittest discover -s tests`: 1468 PASS, FAIL=0, SKIP=0.
- `python -m legacy_documenter.knowledge.readiness`: READINESS=READY, ai_knowledge_allowed=true, ai_knowledge_generated=false, provider_calls=0, real_llm_calls=0.
- `PROJECT_STATE.json` confirmed: latest_approved_round=V4.1-R3, next=V4.1-R4, V4 formally closed.

## BASELINE_TESTS

```text
BASELINE_TESTS=1468_PASS_0_FAIL_0_SKIP
```

## CHARACTERIZATION_TESTS

```text
CHARACTERIZATION_TESTS=18_PASS
```

Added in `tests/test_v4_1_r4_readiness_characterization.py` before any production edit; pins the pre-decomposition public surface, representative READY result, output-file hashes, exception behavior, and CLI invocation of `legacy_documenter.knowledge.readiness`.

## TESTS_AFTER_CHARACTERIZATION

```text
TESTS_AFTER_CHARACTERIZATION=1486_PASS_0_FAIL_0_SKIP
```

(1468 baseline + 18 new characterization tests, run before touching production code.)

## FINAL_TESTS

```text
FINAL_TESTS=1486_PASS_0_FAIL_0_SKIP
```

(Same 1486; no test was added or removed during Phase B itself, only production code moved and four pre-existing frozen-comparison tests were updated to reflect the authorized structural change -- see `RESPONSIBILITIES_REMAINING_IN_FACADE` note below.)

---

## DEBT_002_ORIGINAL_DESCRIPTION

```text
DEBT_002_ORIGINAL_DESCRIPTION=
"legacy_documenter/knowledge/readiness.py (the historical V3-R9 gate) mixes
document parsing, evidence-closure computation, and file I/O in one large
module. Unmodified V3 code; left as-is."
(source: docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md, via
output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json known_debt)
```

R0's own `V4.1-R4` refactor-plan entry (`output/v4_1_r0/V4_1_REFACTOR_PLAN.json`) scoped the round to exactly this: "Split ... into parsing / evidence-closure computation / file-I/O modules behind a compatibility wrapper", with `characterization_required=true` and `forbidden_changes` covering the four output files' schema/content and the `checks`/`readiness` boolean logic.

## DEBT_002_STATUS

```text
DEBT_002_STATUS=RESOLVED
```

The exact R0-defined debt -- parsing, evidence-closure computation, and file I/O mixed into one module -- has been eliminated: those three responsibilities now live in dedicated internal modules, while `readiness.py` itself keeps only validation, projection, security, and orchestration (which R0's own description did not name as part of this debt). Public compatibility and behavior are fully preserved (see below).

---

## PHASE_A

```text
PHASE_A=COMPLETE
```

Characterization was performed against the live repository, not from conversation memory:

- **Public functions/classes/constants**: `run`, `KnowledgeReadinessService`, `parse_human_record`, `validate_preconditions`, `validate_claims`, `architecture_valid`, `quantitative_valid`, `build_projection`, `build_boundary`, `ALLOWED_STATUSES`, `ALLOWED_METRIC_SCOPES`, `PROHIBITED_ASSERTIONS`, `SECRET_RE`, `JsonObject`, plus re-exported `EXTERNAL`/`PARTIAL`/`RESOLVED`/`parse_document`.
- **Private functions used directly by tests**: `_hash`, `_safe` (imported by name in `tests/test_v3_r9.py`); `_read`, `_field`, `_details`, `_csv`, `_canonical_catalog`, `evidence_closed`, `evidence_closure_diagnostics`, `_execute` (used only internally, but part of the module's importable surface via `import *`).
- **Importers/callers** (confirmed by repository-wide grep): `tests/test_v3_r9.py` (`from ... import *` plus explicit `_hash`/`_safe`), `tests/test_v3_r10.py` (`KnowledgeReadinessService`, `run`), `tests/test_v3_r10_1.py` (`run`), `tests/test_v4_1_r1_regression_and_json_renderer.py` (`run as run_readiness`), `tests/test_v4_1_r2_models_types_and_public_contracts.py` (`from ... import readiness; readiness.run()`), `tests/test_v4_1_r3_low_risk_naming_readability.py` (`from ... import run`), `tests/test_v4_1_r0_maintainability_inventory.py` (path-based AST inventory of the file itself). No non-test production caller exists.
- **CLI/module-entry behavior**: `if __name__ == "__main__": print(json.dumps(run(), ...))`.
- **Filesystem reads**: `output/LEVANTAMIENTO_FUNCIONAL.md`, `output/LEVANTAMIENTO_TECNICO.md`, `codex/V3/V3_R8_4_REVISION_HUMANA_APROBADA.md`, `output/v3_r7_2/LOCAL_ASSESSMENTS.json`, `output/v3_r7_2/INTERMEDIATE_ASSESSMENTS.json`, `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`.
- **Filesystem writes**: four files under `output/v3_r9/` (`KNOWLEDGE_READINESS.json`, `KNOWLEDGE_PROJECTION.json`, `KNOWLEDGE_BOUNDARY.json`, `READINESS_TRACEABILITY.json`).
- **Environment dependencies**: none.
- **PROJECT_STATE dependencies**: none (confirmed by source scan; `"PROJECT_STATE"` does not appear anywhere in `readiness.py`).
- **Approved-artifact dependencies**: none of the four R9 output files are themselves frozen/approved artifacts from a later round.
- **Ordering dependencies**: `sorted(review["decisions"].items())` in `build_projection`; `sorted()` on diagnostic identifier lists in `evidence_closure_diagnostics`; deterministic dict/JSON key ordering (`sort_keys=True`) on write.
- **Hash/integrity checks**: `_hash()` used for document/human-review SHA-256 recorded in `READINESS_TRACEABILITY.json`, and by tests to assert output-file immutability/determinism.
- **Exception behavior**: `parse_human_record` raises `ValueError("DUPLICATE_HUMAN_DISPOSITION")` on a repeated disposition key; no other explicit exception raised by this module (upstream `parse_document`/`json.loads` may raise on malformed input, unchanged).
- **Exit behavior**: none (no `sys.exit`); CLI prints and returns normally.
- **stdout/stderr behavior**: CLI prints one JSON document to stdout via `print()`.
- **Deterministic output shape**: fixed top-level key sets for `run()`'s return value and each of the four written JSON files (pinned in the characterization tests).
- **Global/module state**: none (no module-level mutable state; all functions are pure or read-only against fixed paths).
- **Monkeypatch-sensitive symbols / patch points**: see `READINESS_PATCH_POINTS` below.
- **Tests patching names directly from readiness.py**: none found by repository-wide grep for `patch("legacy_documenter.knowledge.readiness`, `monkeypatch.setattr(readiness`, or direct assignment to a `readiness.<name>` attribute.
- **Tests depending on import location**: `tests/test_v3_r9.py`'s `from ... import *` and explicit `_hash`/`_safe` import depend on the exact module path `legacy_documenter.knowledge.readiness`, not on where symbols are *defined*.
- **Functions with multiple responsibilities**: `_execute` orchestrates all of parsing, evidence-closure, validation, projection, and I/O in one function body (kept as orchestration in the facade; not split further, since R0's own plan names three extraction categories, not a full flattening).
- **Candidate responsibility groups**: file I/O (`_read`, `_hash`); parsing (`parse_human_record`, `_field`, `_details`, `_csv`, plus the human-disposition constants `HUMAN_CONFIRMED`/`EXPECTED`); evidence-closure computation (`_canonical_catalog`, `evidence_closed`, `evidence_closure_diagnostics`). Validation, projection, security, and orchestration were evaluated and kept in the facade -- see `RESPONSIBILITIES_REMAINING_IN_FACADE`.

## READINESS_RESPONSIBILITY_MAP

Full map (symbol / responsibility / inputs / outputs / side_effects / callers / compatibility_risk / candidate_destination / safe_to_extract) is recorded verbatim in `output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json` -> `responsibility_map`. Summary:

| Symbol | Responsibility | Side effects | Safe to extract |
|---|---|---|---|
| `_read`, `_hash` | file_io | filesystem read | YES |
| `parse_human_record`, `_field`, `_details`, `_csv`, `HUMAN_CONFIRMED`, `EXPECTED` | parsing | none (pure) | YES |
| `_canonical_catalog`, `evidence_closed`, `evidence_closure_diagnostics` | evidence_closure_computation | `_canonical_catalog` reads files (via `_read`) | YES |
| `validate_preconditions`, `validate_claims`, `architecture_valid`, `quantitative_valid` | validation | none (pure) | NO (kept in facade; not named in R0's DEBT-002 extraction scope) |
| `build_projection`, `build_boundary` | projection | none (pure) | NO (kept in facade) |
| `_safe` | security | none (pure) | NO (kept in facade) |
| `_execute`, `KnowledgeReadinessService`, `run` | orchestration | writes 4 JSON files | NO (must remain the public entry point/CLI) |

## READINESS_PUBLIC_SYMBOLS

```text
READINESS_PUBLIC_SYMBOLS_PRESERVED=ALL (run, KnowledgeReadinessService, parse_human_record,
validate_preconditions, validate_claims, architecture_valid, quantitative_valid,
build_projection, build_boundary, ALLOWED_STATUSES, ALLOWED_METRIC_SCOPES,
PROHIBITED_ASSERTIONS, SECRET_RE, JsonObject, EXTERNAL, PARTIAL, RESOLVED,
parse_document, _hash, _safe, _read, _field, _details, _csv, _canonical_catalog,
evidence_closed, evidence_closure_diagnostics, _execute)
```

## READINESS_PUBLIC_SIGNATURES

Pinned pre-decomposition and re-verified identical post-decomposition for every documented public function (see `tests/test_v4_1_r4_readiness_characterization.py::PublicSignatureTests`); e.g. `run(workspace: str | pathlib.Path = '.') -> dict[str, object]` unchanged.

## READINESS_CALLERS

```text
READINESS_CALLERS=7 test modules (listed under PHASE_A above); zero non-test production callers.
```

## READINESS_SIDE_EFFECTS

```text
READINESS_SIDE_EFFECTS=6 fixed-path file reads + 4 fixed-path file writes under output/v3_r9/; no network, no provider calls, no global mutable state.
```

## READINESS_PATCH_POINTS

All 19 names in `PATCH_POINTS` (`tests/test_v4_1_r4_readiness_characterization.py`) were classified and verified to still resolve from `legacy_documenter.knowledge.readiness` after the split. Full classification is in `output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json` -> `monkeypatch_compatibility.patch_points_classified`:

- **PATCH_LOCATION_PRESERVED** (defined directly in `readiness.py`, unchanged): `run`, `KnowledgeReadinessService`, `_safe`, `validate_preconditions`, `validate_claims`, `architecture_valid`, `quantitative_valid`, `build_projection`, `build_boundary`, `_execute`.
- **COMPATIBILITY_FORWARDING_REQUIRED** (definition moved to an internal module, re-exported into `readiness.py` via an explicit named import): `parse_human_record`, `_hash`, `_read`, `_field`, `_details`, `_csv`, `_canonical_catalog`, `evidence_closed`, `evidence_closure_diagnostics`.

No `**kwargs`/`__getattr__` magic was used; every forwarded symbol is a plain, explicit `from legacy_documenter.knowledge._readiness_* import name` at the top of `readiness.py`.

---

## READINESS_DECOMPOSITION_DECISION

```text
READINESS_DECOMPOSITION_DECISION=SAFE_FOR_CONTROLLED_EXTRACTION
```

## PHASE_B_EXECUTED

```text
PHASE_B_EXECUTED=true
```

---

## PRODUCTION_FILES_ADDED

```text
PRODUCTION_FILES_ADDED=3
legacy_documenter/knowledge/_readiness_io.py
legacy_documenter/knowledge/_readiness_parsing.py
legacy_documenter/knowledge/_readiness_evidence.py
```

## PRODUCTION_FILES_MODIFIED

```text
PRODUCTION_FILES_MODIFIED=1
legacy_documenter/knowledge/readiness.py
```

## EXTRACTIONS_PERFORMED

```text
EXTRACTIONS_PERFORMED=3
```

1. File I/O (`_read`, `_hash`) -> `legacy_documenter/knowledge/_readiness_io.py`.
2. Parsing (`parse_human_record`, `_field`, `_details`, `_csv`, `HUMAN_CONFIRMED`, `EXPECTED`) -> `legacy_documenter/knowledge/_readiness_parsing.py`.
3. Evidence-closure computation (`_canonical_catalog`, `evidence_closed`, `evidence_closure_diagnostics`) -> `legacy_documenter/knowledge/_readiness_evidence.py`.

## RESPONSIBILITIES_REMAINING_IN_FACADE

```text
RESPONSIBILITIES_REMAINING_IN_FACADE=validation, projection, security, orchestration/CLI
```

`readiness.py` keeps `validate_preconditions`, `validate_claims`, `architecture_valid`, `quantitative_valid` (validation); `build_projection`, `build_boundary`, `PROHIBITED_ASSERTIONS` (projection); `_safe`, `SECRET_RE` (security); and `_execute`, `KnowledgeReadinessService`, `run`, the CLI `__main__` block (orchestration). This keeps the file path, `python -m legacy_documenter.knowledge.readiness` entry point, and every existing test's import statement working with zero changes, while still splitting out the three responsibilities R0's own plan named (parsing / evidence-closure computation / file I/O). readiness.py's own line count dropped from 292 to 188; four pre-existing frozen-comparison tests (`tests/test_v4_1_r0_maintainability_inventory.py`, `tests/test_v4_1_r2_models_types_and_public_contracts.py`, `tests/test_v4_1_r3_low_risk_naming_readability.py`, `tests/test_v4_r14_manuals_and_final_baseline.py`) were updated to account for this explicitly-authorized structural change (production file count, risk-category bucket, largest-modules ranking, side-effect-candidate file list) -- no semantic assertion was weakened; each updated assertion still fails if any *other* file changes unexpectedly.

---

## READINESS_PUBLIC_IMPORTS_PRESERVED

```text
READINESS_PUBLIC_IMPORTS_PRESERVED=PASS
```

## READINESS_PUBLIC_SIGNATURES_PRESERVED

```text
READINESS_PUBLIC_SIGNATURES_PRESERVED=PASS
```

## MONKEYPATCH_COMPATIBILITY

```text
MONKEYPATCH_COMPATIBILITY=PASS
```

---

## READINESS_RESULT_EQUIVALENCE

```text
READINESS_RESULT_EQUIVALENCE=PASS
```

## READINESS_SERIALIZATION_EQUIVALENCE

```text
READINESS_SERIALIZATION_EQUIVALENCE=PASS
```

All four `output/v3_r9/*.json` files are byte-identical (SHA-256 pinned in `tests/test_v4_1_r4_readiness_characterization.py::SerializationAndOrderingTests`) before and after the split.

## READINESS_ORDERING_EQUIVALENCE

```text
READINESS_ORDERING_EQUIVALENCE=PASS
```

## READINESS_EXCEPTION_EQUIVALENCE

```text
READINESS_EXCEPTION_EQUIVALENCE=PASS
```

`parse_human_record`'s `ValueError("DUPLICATE_HUMAN_DISPOSITION")` and `_field`'s `None`-on-no-match behavior verified unchanged.

## READINESS_CLI_EQUIVALENCE

```text
READINESS_CLI_EQUIVALENCE=PASS
```

`python -m legacy_documenter.knowledge.readiness` still prints the same JSON shape (verified via subprocess in the characterization tests); no `__main__.py`/package conversion was needed since `readiness.py` remains a plain module file.

---

## APPROVED_ARTIFACT_HASHES_UNCHANGED

```text
APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
```

| Artifact | SHA-256 |
|---|---|
| `output/v4_r14/V4_FINAL_BASELINE.json` | `d13e3807a12187b226ea55752ae0e9dccd2ad20c9dbe044360ffa48bca526d1e` |
| `output/v4_r14/V4_FINAL_MANIFEST.json` | `be398240a31137e7dea25fcaa7b3cfe6580d2557f990f7da884d5775f5c40551` |
| `output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json` | `55c99c3b68ac159585c6a0ec7e05f74e8dd64dd871308d067ab27bdda1a1c33b` |
| `output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json` | `bd3daf04be868ef6465298c5e372aacc1f33bf234417f2bb914b79b22ab5a6f4` |
| `output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json` | `9e922d288b4f07812482baef1a5383276cd71f729e27cc67b47e54c30c5afecf` |

None regenerated; none touched.

## R0_FROZEN_INVENTORY_MODIFIED

```text
R0_FROZEN_INVENTORY_MODIFIED=false
```

`output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json` and `output/v4_1_r0/V4_1_REFACTOR_PLAN.json` themselves were not touched. Only the *test comparison logic* in `tests/test_v4_1_r0_maintainability_inventory.py` was extended (following the exact precedent already established by V4.1-R1/R2/R3 in the same file) to account for the three new authorized files and readiness.py's now-lower risk category; every other field is still asserted byte-for-byte equal to the frozen R0 snapshot.

---

## READINESS_EQUIVALENCE_ARTIFACT

```text
READINESS_EQUIVALENCE_ARTIFACT=output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json
```

## READINESS_EQUIVALENCE_ARTIFACT_SHA256

```text
READINESS_EQUIVALENCE_ARTIFACT_SHA256=eb07e0f35540e0607b90f8ff707c7cac8e1f113419d338e3cc8579fa12f1e617
```

## READINESS_EQUIVALENCE_ARTIFACT_DETERMINISM

```text
READINESS_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS
```

Generated twice independently from the same deterministic builder (no timestamps, no machine-specific absolute paths); byte-for-byte identical both times.

---

## TD_005_STATUS

```text
TD_005_STATUS=PARTIALLY_RESOLVED
```

Unchanged from V4.1-R3; R4 did not touch typing work (out of scope).

## DEBT_003_STATUS

```text
DEBT_003_STATUS=RESOLVED
```

Unchanged from V4.1-R3; R4 did not touch the batch-parameter naming.

---

## V4_CONTRACTS_UNCHANGED

```text
V4_CONTRACTS_UNCHANGED=PASS
```

## R11_BOUNDARY

```text
R11_BOUNDARY=PASS
```

## R12_BOUNDARY

```text
R12_BOUNDARY=PASS
```

`PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge`, `PLUGIN_CONTRACT_VERSION=1.0`, `PLUGIN_RUNTIME=NOT_IMPLEMENTED`, `V5_IMPLEMENTED=false` -- none touched this round.

---

## PRODUCTION_CODE_CHANGED

```text
PRODUCTION_CODE_CHANGED=true
```

## PRODUCTION_BEHAVIOR_CHANGED

```text
PRODUCTION_BEHAVIOR_CHANGED=false
```

Four production files changed (one modified facade, three new internal modules); zero runtime behavior changed (full regression suite, characterization tests, and manual output-hash comparison all confirm equivalence).

---

## READINESS

```text
READINESS=READY
```

## AI_KNOWLEDGE_ALLOWED

```text
AI_KNOWLEDGE_ALLOWED=true
```

## AI_KNOWLEDGE_GENERATED

```text
AI_KNOWLEDGE_GENERATED=false
```

## REAL_LLM_CALLS

```text
REAL_LLM_CALLS=0
```

## PROVIDER_CALLS

```text
PROVIDER_CALLS=0
```

---

## PROJECT_STATE

`PROJECT_STATE.json` updated to:

```text
latest_completed_round = "V4.1-R4"
latest_approved_round = "V4.1-R3"   (unchanged)
current_round_in_progress = "V4.1-R4 (pending Technical Lead review)"
round_status = "V4_1_R4_READY_FOR_HUMAN_REVIEW"
next = "HUMAN_REVIEW_V4_1_R4"
tests = 1486
readiness = "READY"
ai_knowledge_allowed = true
ai_knowledge_generated = false
provider_calls = 0
real_llm_calls = 0
```

V4 closure fields untouched. R4 is **not** marked approved.

---

## DECISION

```text
DECISION=V4_1_R4_READY_FOR_HUMAN_REVIEW
```

## NEXT

```text
NEXT=HUMAN_REVIEW_V4_1_R4
```

---

## Narrative Summary

R4 executed DEBT-002 exactly as R0's own refactor plan scoped it: characterize `legacy_documenter/knowledge/readiness.py` first (Phase A), then only decompose if characterization proved it safe (Phase B). Phase A added 18 characterization tests pinning the module's pre-decomposition public surface (including the two "private" names, `_hash` and `_safe`, that `tests/test_v3_r9.py` imports directly, and the full `from ... import *` surface that same test relies on), representative READY output, exact output-file hashes, exception behavior, and CLI invocation -- and confirmed by repository-wide grep that no test monkeypatches or directly assigns to any `readiness` module attribute, which made the extraction's compatibility risk low and well-bounded.

Phase B extracted exactly the three responsibilities R0's plan named -- file I/O, parsing, and evidence-closure computation -- into three new internal `legacy_documenter/knowledge/_readiness_*.py` modules, while deliberately keeping validation, projection, security, and orchestration (including the CLI `__main__` block) inside `readiness.py` itself. This design choice kept `readiness.py` at its exact original file path with its exact original importable namespace (every extracted name is re-exported via an explicit named import, never a wildcard or `__getattr__`), so every one of the seven existing test modules that import from `legacy_documenter.knowledge.readiness` needed zero changes, and `python -m legacy_documenter.knowledge.readiness` did not require converting the module into a package with a separate `__main__.py`.

The extraction legitimately changed structural facts about the repository (production file count 144->147, `readiness.py`'s own risk_category VERY_HIGH->HIGH, its position in the largest-modules ranking, and the file list of the filesystem_access side-effect candidate) that four pre-existing frozen-comparison tests asserted. Each was updated following the exact same pattern V4.1-R1/R2/R3 already established in the same test files for their own authorized changes -- no semantic assertion was weakened, and every updated assertion still fails on any *other*, unauthorized change.

The full regression suite (1486 tests, up from the 1468 baseline plus 18 new characterization tests) is green, readiness stays `READY` with zero provider/LLM calls, all five required historical artifact hashes are verified unchanged, and none of the four remaining fenced high-risk modules (`database_extractor.py`, `flow_resolver.py`, `resume.py`, `deep_source.py`) were touched. `PROJECT_STATE.json` reflects the pending-review state without marking R4 approved and without touching any V4 closure field.

---

## Closure Section — Technical Lead Approval

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

CHARACTERIZATION_DECISION=APPROVED
DECOMPOSITION_DECISION=APPROVED

DEBT_002_DECISION=RESOLVED_APPROVED
DEBT_003_DECISION=RESOLVED_UNCHANGED
TD_005_DECISION=PARTIALLY_RESOLVED_UNCHANGED

READINESS_EQUIVALENCE_DECISION=APPROVED

R4_1_REQUIRED=false

ROUND_STATUS=APPROVED
DECISION=V4_1_R4_FORMALLY_APPROVED
NEXT=V4.1-R5
```

The Technical Lead reviewed and approved Phase A's characterization-before-modification approach (18 characterization tests), the `SAFE_FOR_CONTROLLED_EXTRACTION` decision, and Phase B's controlled decomposition: extraction of file I/O into `_readiness_io.py`, parsing into `_readiness_parsing.py`, and evidence-closure computation into `_readiness_evidence.py`, with validation, projection, security, and orchestration/CLI kept in `readiness.py`. Explicit compatibility forwarding (no wildcard/`__getattr__` magic), preserved public symbols/signatures, preserved monkeypatch/import compatibility, and byte-equivalent R9 serialized outputs are all accepted as recorded. `DEBT-002=RESOLVED`, `DEBT-003=RESOLVED` (unchanged), and `TD-005=PARTIALLY_RESOLVED` (unchanged) are all accepted. No R4.1 corrective round is required.
