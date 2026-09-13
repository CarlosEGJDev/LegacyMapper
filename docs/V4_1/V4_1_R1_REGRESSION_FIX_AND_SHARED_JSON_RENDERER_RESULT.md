# LegacyMapper V4.1-R1 — Regression Fix and Shared JSON Renderer — Result

```text
STATUS=V4_1_R1_IMPLEMENTATION_COMPLETE

ENTRY_GATE=PASS_WITH_ACCEPTED_REG_002_AND_AUTHORIZED_SCOPE_EXPANSION

BASELINE_TESTS_TOTAL=1402
BASELINE_TESTS_PASS=1398
BASELINE_KNOWN_FAIL=4 (REG-002-CANDIDATE + 3 round-ordinal-parsing defects; see Scope Expansion section)

REG_002_REPRODUCED=PASS
REG_002_FIXED=PASS
REG_002_CHANGE_TYPE=TEST_ONLY
REG_002_FULL_SUITE_GREEN_BEFORE_REFACTOR=PASS

SHARED_RENDERER_PATH=legacy_documenter/utils/json_rendering.py
SHARED_RENDERER_DESIGN=single pure function render_deterministic_json(payload), standard-library json only, explicit type hints, no I/O, no global state, no domain semantics, no round-specific behavior

AFFECTED_RENDERERS=11 (legacy_documenter/knowledge/{approval,canonical,classification,ingestion,input,plugin_projection,projection,proposals,provenance,relations,temporal}/contract_report.py)

DUP_001=RESOLVED
DEBT_001=RESOLVED

DUP_002_PRESERVED_DISTINCT=PASS
DUP_003_UNTOUCHED=PASS
DUP_004_UNTOUCHED=PASS

PUBLIC_IMPORT_PATHS_PRESERVED=PASS
PUBLIC_FUNCTION_NAMES_PRESERVED=PASS

CONTRACT_JSON_BYTE_EQUIVALENCE=PASS

APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS

BEHAVIORAL_EQUIVALENCE_ARTIFACT=output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json
BEHAVIORAL_EQUIVALENCE_ARTIFACT_SHA256=55c99c3b68ac159585c6a0ec7e05f74e8dd64dd871308d067ab27bdda1a1c33b
BEHAVIORAL_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS

FINAL_TESTS=1424_PASS (1402 pre-existing + 22 new V4.1-R1 tests), FAIL=0

V4_CONTRACTS_UNCHANGED=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS

PRODUCTION_CODE_CHANGED=true
PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=V4_1_R1_READY_FOR_HUMAN_REVIEW

DECISION=V4_1_R1_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_1_R1
```

---

## Entry Gate

`git status` showed only `prompts/V4_1/V4_1_R1_REGRESSION_FIX_AND_SHARED_JSON_RENDERER.md` as untracked, as expected.

`python -m unittest discover -s tests` produced exactly the 4 expected failures and no others:

1. `tests/test_v4_r14_manuals_and_final_baseline.py::DeterminismTests::test_baseline_matches_on_disk_artifact` (REG-002-CANDIDATE)
2. `tests/test_v4_r12_plugin_facing_machine_readable_output_contract.py::EntryGateTests::test_project_state_records_r11_approved`
3. `tests/test_v4_r13_regression_and_security.py::RepositoryContinuityStateTests::test_project_state_round_is_at_least_r12`
4. `tests/test_v4_r14_manuals_and_final_baseline.py::EntryGateAndContinuityTests::test_project_state_at_least_r13_approved`

TOTAL=1402, PASS=1398, FAIL=4 — matching the expanded entry-gate expectation exactly. No other failure was found.

`python -m legacy_documenter.knowledge.readiness` returned `READY`, `ai_knowledge_allowed=true`, `ai_knowledge_generated=false`, `provider_calls=0`, `real_llm_calls=0`.

---

## Block A — REG-002 and the 3 Round-Ordinal-Parsing Fixes

### REG-002-CANDIDATE

Root cause confirmed: `test_baseline_matches_on_disk_artifact` compared the frozen `output/v4_r14/V4_FINAL_BASELINE.json` (recorded when `latest_approved_round="V4-R13"`, `test_count=1380`, `production_python_module_count=143`) against a freshly rebuilt baseline from the *current* live `PROJECT_STATE.json` and repository tree — three fields differed for legitimate reasons: `latest_approved_round` (now `V4.1-R0`), `test_count` (now higher), and `maintainability_baseline.test_python_module_count` (now higher).

Fix applied (test-only, `tests/test_v4_r14_manuals_and_final_baseline.py`): `test_baseline_matches_on_disk_artifact` now asserts byte-for-byte equality on every field except the three fields known to legitimately advance, and separately asserts each of those three fields only ever moved forward (never backward) relative to the frozen snapshot. `production_python_module_count` was added to this same excluded/forward-only set later in this round (see Block B side effects below), for the identical reason.

The frozen artifact itself was never modified. `output/v4_r14/V4_FINAL_BASELINE.json` SHA-256 remained `d13e3807a12187b226ea55752ae0e9dccd2ad20c9dbe044360ffa48bca526d1e` throughout the entire round.

After this fix and the 3 ordinal fixes below, `python -m unittest discover -s tests` produced 1402/1402 PASS, FAIL=0.

---

## Scope Expansion — Round-Ordinal-Parsing Fix (User-Authorized)

**What the 3 additional failures were:**

1. `tests/test_v4_r12_plugin_facing_machine_readable_output_contract.py::EntryGateTests::test_project_state_records_r11_approved`
2. `tests/test_v4_r13_regression_and_security.py::RepositoryContinuityStateTests::test_project_state_round_is_at_least_r12`
3. `tests/test_v4_r14_manuals_and_final_baseline.py::EntryGateAndContinuityTests::test_project_state_at_least_r13_approved`

**Root cause (verified independently in each file):** each test parsed `PROJECT_STATE.json`'s `latest_approved_round` with a regex hardcoded to the literal shape `V4-R(\d+)`. None of the three files shared a common helper module (R12 used an inline `re.search` in the test method; R13 defined its own `_round_ordinal` instance method; R14 defined its own module-level `_round_ordinal` function) — each was fixed independently in place, in the same style it already used, rather than introducing a new shared test-helper module for only 3 call sites. Once `latest_approved_round` legitimately advanced to `"V4.1-R0"` (the new V4.1-phase naming scheme, correctly recorded by V4.1-R0's approved closure), the `V4-R(\d+)`-only regex stopped matching and every dependent "N or later approved" assertion failed.

**Exactly what was changed in each of the 3 files:**

- `tests/test_v4_r12_plugin_facing_machine_readable_output_contract.py` (`EntryGateTests.test_project_state_records_r11_approved`, ~line 74): the inline regex changed from `r"V4-R(\d+)"` to `r"V4(?:\.(\d+))?-R(\d+)"`; the ordinal is now computed as `phase * 1000 + round_number` (phase defaults to 0 for plain `V4-R<N>` labels), so a `V4.1-R<N>` label sorts after every `V4-R<N>` label.
- `tests/test_v4_r13_regression_and_security.py` (`RepositoryContinuityStateTests._round_ordinal`, ~line 716): same regex and `phase * 1000 + round_number` ordinal change; still returns `-1` when no match is found, preserving its original fallback behavior.
- `tests/test_v4_r14_manuals_and_final_baseline.py` (module-level `_round_ordinal`, ~line 51): same regex and ordinal change; still raises `AssertionError(f"no_round_ordinal_found:{round_label}")` when no match is found, preserving its original fail-closed behavior. This function is also reused by the fixed `test_baseline_matches_on_disk_artifact` (REG-002 fix, above).

**Why this was authorized as an in-scope expansion of Block A rather than a separate round:** all 4 failures (REG-002 plus these 3) are the exact same defect class — a test hardcoding an exact literal shape/value of a field (`PROJECT_STATE.json`'s `latest_approved_round`, or a frozen snapshot of it) instead of the durable invariant the test is actually meant to protect ("round N or later is approved"). Fixing REG-002 alone while leaving the other 3 broken would have left the round in a state that could never reach `R1_REFACTOR_MAY_BEGIN_ONLY_AFTER_FULL_SUITE_GREEN=true`, and splitting a single root-cause defect class across two separate rounds would have been artificial process overhead for a mechanically identical, low-risk, test-only fix. The user (acting as Technical Lead) explicitly authorized this expansion before any repository change was made.

**Confirmation this was purely test-only:** all 4 changes touched only test files (`tests/test_v4_r12_plugin_facing_machine_readable_output_contract.py`, `tests/test_v4_r13_regression_and_security.py`, `tests/test_v4_r14_manuals_and_final_baseline.py`). No production module, no `PROJECT_STATE.json` field, and no V4 contract was modified to achieve this fix. `ROUND_ORDINAL_PARSING_DEFECT_FIXED=true`.

```text
REG_002=FIXED
REG_002_CHANGE_TYPE=TEST_ONLY
REG_002_PRODUCTION_CHANGE=false
REG_002_FULL_SUITE_GREEN=true

ROUND_ORDINAL_PARSING_DEFECT_FIXED=true
ROUND_ORDINAL_PARSING_CHANGE_TYPE=TEST_ONLY
ROUND_ORDINAL_PARSING_PRODUCTION_CHANGE=false
ROUND_ORDINAL_PARSING_USER_AUTHORIZED_SCOPE_EXPANSION=true
```

---

## Block B — DUP-001 / DEBT-001 Consolidation

### Scope discovery

The exact eleven files were read directly from `output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json`'s `DUP-001` finding (not reconstructed from memory):

```text
legacy_documenter/knowledge/approval/contract_report.py
legacy_documenter/knowledge/canonical/contract_report.py
legacy_documenter/knowledge/classification/contract_report.py
legacy_documenter/knowledge/ingestion/contract_report.py
legacy_documenter/knowledge/input/contract_report.py
legacy_documenter/knowledge/plugin_projection/contract_report.py
legacy_documenter/knowledge/projection/contract_report.py
legacy_documenter/knowledge/proposals/contract_report.py
legacy_documenter/knowledge/provenance/contract_report.py
legacy_documenter/knowledge/relations/contract_report.py
legacy_documenter/knowledge/temporal/contract_report.py
```

Each file's current source was read directly and verified to match the R0 inventory's recorded pattern exactly:
`json.dumps(build_X(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))`, differing only in which `build_*` function is called. No renderer differed semantically from what R0's inventory predicted.

### Shared helper

Created `legacy_documenter/utils/json_rendering.py`:

```python
def render_deterministic_json(payload: Mapping[str, object]) -> str:
    """Serializes `payload` as canonical, deterministic JSON text..."""
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
```

Standard library only (`json`), explicit type hints, no I/O, no global state, no domain semantics, no round-specific behavior. Exported from `legacy_documenter/utils/__init__.py` alongside the existing `sanitize_text`/`sanitize_data`.

**Placement rationale:** `legacy_documenter/utils/` is already the established neutral, dependency-safe location shared by multiple R7-R12 knowledge packages (`sanitizer.py` is imported by `approval`, `canonical`, `classification`, `ingestion`, `input`, `proposals`, `provenance`, and `relations` service modules). Placing the new helper there introduces no new package, no round-package dependency, and no `projection` <-> `plugin_projection` edge — `legacy_documenter.utils` depends on nothing under `legacy_documenter.knowledge`, and nothing under `legacy_documenter.knowledge` depends on another round's contract_report module.

### Compatibility

Every `build_*_contract()` / `build_source_contract_report()` function (DUP-002) was left completely untouched — confirmed by direct source inspection (`inspect.getsource`) showing no reference to `render_deterministic_json` inside any builder. Every `render_*_contract_json()` / `render_source_contract_report_json()` function keeps its exact original name and module path; each is now a one-line delegator: `return render_deterministic_json(build_X())`. A repository-wide grep (including `tests/`) for every `render_*_contract_json` caller found no breakage; the new `tests/test_v4_1_r1_regression_and_json_renderer.py` exercises every one of the eleven import paths directly.

### Byte equivalence

Before editing any renderer, this round captured each renderer's output SHA-256 and length. After refactoring, every one of the eleven renderers was re-invoked and compared byte-for-byte against its captured "before" value:

```text
approval            PASS  sha256=f222d6f6440297c8f9838b1e2227059b72441f4f9a50b9fae5f8a23331563ef9
canonical           PASS  sha256=56d731d2df5d30a2f3fb57b5100d87a6211debb6c5438d7fe4d5da29dbca87f1
classification      PASS  sha256=6fcdc5ec817d356df11b57326baec88e1c17fbd2e19fe21fde9a5084b65f63c7
ingestion           PASS  sha256=a9d478058a2e87560e14fcb66324e02a2691a17401243ef18a1ad0a451094542
input               PASS  sha256=60144e2c67e96c66f708157885607fd07bbeb4087cac81f9049d7019612a0ef7
plugin_projection   PASS  sha256=7ad986ee285108f80c30eec5db962501b6fb073d66c017c5d87b9a52cf2a5fa3
projection          PASS  sha256=5802e0e78dabd8e44de030ee15c56db747444147a462d050ad2971ffc39206fd
proposals           PASS  sha256=56778b6c3cf92267fe4a501851668422bd646ef414f20d0c100216ecf699c91c
provenance          PASS  sha256=734d6985783cb7a171aec9952dd9534077fef0ca09fef084179800cd98b1eb2d
relations           PASS  sha256=4e202fd6d458eeaec568c4c0bb419d40faeb434727b6ac2587874f3b40a256ee
temporal            PASS  sha256=e46b858742d409b273cbc929e8a6c137dd7d58a698f7fc49fe1bcfca85de9531
```

`CONTRACT_JSON_BYTE_EQUIVALENCE=PASS` for all eleven. The full detail (including `before_len`/`after_len`) is recorded in `output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json`.

The 54 files under `output/v4_r7/` through `output/v4_r12/` (existing approved artifacts) were hashed before and after Block B; every hash is unchanged (`APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS`). No historical approved artifact was regenerated to "prove" equality — comparisons used the already-recorded hashes.

### Boundaries respected

- DUP-002 (`build_*_contract()` bodies): completely untouched.
- DUP-003 (`requests`/`request` batch-parameter naming): not touched.
- DUP-004 (per-package `models.py`/`service.py` layout): not touched.
- No batch-parameter renames; no package restructuring beyond the one new `legacy_documenter/utils/json_rendering.py` module.

### An unavoidable, explained side effect

Adding one new production module (`legacy_documenter/utils/json_rendering.py`) and touching the import lines of the eleven renderers plus `legacy_documenter/utils/__init__.py` legitimately changed two structural counts that two *pre-existing* tests hardcoded as exact literals:

- `tests/test_v4_1_r0_maintainability_inventory.py::ProductionFileDiscoveryTests::test_file_count_matches_r14_baseline_observation` hardcoded `143` production modules; it is now `144` (one new file). Updated to `144` with an explanatory comment.
- `tests/test_v4_1_r0_maintainability_inventory.py::GeneratedArtifactOnDiskTests::test_on_disk_inventory_matches_fresh_build_if_present` compared the frozen, approved V4.1-R0 inventory artifact byte-for-byte against a fresh AST rescan of the live tree. This is the same "frozen historical snapshot vs moving live state" defect class as REG-002. It was fixed the same way: byte-equality is still asserted on every section except `production_inventory`, `risk_summary`, and `dependency_findings`, and those three sections are now checked narrowly (no path removed; the only new path is `legacy_documenter/utils/json_rendering.py`; `module_count` increased by exactly 1; the `LOW` risk bucket increased by exactly 1; every other risk/dependency finding is unchanged; and every touched `contract_report.py`/`utils/__init__.py` inventory entry is explicitly allow-listed as an expected diff, while any *unexpected* diff anywhere else still fails the test).

Both changes are test-only, fully explained, and do not weaken either test's ability to catch an unrelated regression.

---

## Tests

`tests/test_v4_1_r1_regression_and_json_renderer.py` (22 tests) covers: REG-002 fixed and frozen-baseline hash pinned; all 3 round-ordinal fixes pass and still correctly reject an out-of-range round (`V4-R5` returns an ordinal below the required threshold for all three, proving the fix is a real ordering and not vacuously true); the shared JSON helper's exact separator/sorted-key contract; `ensure_ascii=False` preserved with a Spanish-accented string (`"Configuración de línea, año, sueño"`); all eleven renderers routing through the shared helper; the 12 relevant R7-R12 approved artifacts still present, non-empty, and valid JSON; every public renderer import path resolving and returning a string; every `build_*_contract` function's source containing no reference to `render_deterministic_json`; no `projection` <-> `plugin_projection` import in either direction; the shared helper importing only `json`/`typing`/`__future__`; and readiness remaining READY with zero provider/LLM calls.

No existing test was removed, skipped, or weakened; the 5 tests that needed a code change (2 Block A files beyond REG-002's own, REG-002's own test, plus the 2 downstream V4.1-R0 inventory tests) each had their *durable invariant preserved* while removing a hardcoded literal that this round's own authorized changes made stale.

---

## Behavioral Equivalence Artifact

`output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json` was generated twice independently (fresh Python process re-imports and re-renders every module both times) and produced byte-identical output both times.

```text
BEHAVIORAL_EQUIVALENCE_ARTIFACT_SHA256=55c99c3b68ac159585c6a0ec7e05f74e8dd64dd871308d067ab27bdda1a1c33b
BEHAVIORAL_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS
```

---

## Final Regression

```text
python -m unittest discover -s tests
Ran 1424 tests
OK (FAIL=0)
```

1424 = 1402 pre-existing (all now passing) + 22 new V4.1-R1 tests.

```text
python -m legacy_documenter.knowledge.readiness
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

---

## Security / Contract Preservation

```text
V4_CONTRACTS_UNCHANGED=PASS
APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
R11_BOUNDARY=PASS (no import of legacy_documenter.knowledge.plugin_projection from projection)
R12_BOUNDARY=PASS (no import of legacy_documenter.knowledge.projection from plugin_projection)
PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0
PLUGIN_RUNTIME=NOT_IMPLEMENTED
V5_IMPLEMENTED=false
```

---

## Production Behavior Classification

```text
PRODUCTION_CODE_CHANGED=true (new legacy_documenter/utils/json_rendering.py + 11 renderer call sites + utils/__init__.py export)
PRODUCTION_BEHAVIOR_CHANGED=false (every one of the eleven renderers proven byte-identical before/after)
REG_002_PRODUCTION_CHANGE=false (test-only)
ROUND_ORDINAL_PARSING_PRODUCTION_CHANGE=false (test-only, all 3 fixes)
```

---

## PROJECT_STATE

Updated per the round's required end state: `latest_completed_round="V4.1-R1"`, `latest_approved_round` unchanged at `"V4.1-R0"`, `current_round_in_progress="V4.1-R1 (pending Technical Lead review)"`, `round_status="V4_1_R1_READY_FOR_HUMAN_REVIEW"`, `next="HUMAN_REVIEW_V4_1_R1"`, `tests=1424`, `readiness="READY"`, `ai_knowledge_allowed=true`, `ai_knowledge_generated=false`, `provider_calls=0`, `real_llm_calls=0`. V4 closure fields were not touched. V4.1-R1 was not approved.

---

## Decision

```text
DECISION=V4_1_R1_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_1_R1
```

No commit, no push, no approval, no R2 work, no DUP-002/003/004 modification, no high-risk module decomposition, no V4 contract change, no V5 work, and no Plugin runtime implementation occurred in this round.

## Closure — Human Approval Recorded

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

REG_002_DECISION=APPROVED
ROUND_ORDINAL_PARSING_FIX_DECISION=APPROVED
R0_TEST_ADJUSTMENTS_DECISION=APPROVED

DUP_001_DECISION=APPROVED
DEBT_001_DECISION=APPROVED

BEHAVIORAL_EQUIVALENCE_DECISION=APPROVED

R1_1_REQUIRED=false

ROUND_STATUS=APPROVED

DECISION=V4_1_R1_FORMALLY_APPROVED

NEXT=V4.1-R2
```
