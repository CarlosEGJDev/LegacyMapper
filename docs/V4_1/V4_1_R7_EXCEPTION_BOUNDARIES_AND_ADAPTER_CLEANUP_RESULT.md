# LegacyMapper V4.1-R7 -- Exception Boundaries and Adapter Cleanup Result

```text
STATUS=V4_1_R7_IMPLEMENTATION_COMPLETE
```

---

## ENTRY_GATE

```text
ENTRY_GATE=PASS
```

`git status` clean except the untracked `prompts/V4_1/V4_1_R7_EXCEPTION_BOUNDARIES_AND_ADAPTER_CLEANUP.md`. `latest_approved_round=V4.1-R6`, `next=V4.1-R7`. Baseline `python -m unittest discover -s tests`: 1561 pass, 0 fail, 0 skip. Baseline `python -m legacy_documenter.knowledge.readiness`: `READINESS=READY`, `ai_knowledge_allowed=true`, `ai_knowledge_generated=false`, `provider_calls=0`, `real_llm_calls=0`.

## BASELINE_TESTS

```text
BASELINE_TESTS=1561_PASS_0_FAIL_0_SKIP
```

## FINAL_TESTS

```text
FINAL_TESTS=1566_PASS_0_FAIL_0_SKIP
```

## R7_MODE

```text
R7_MODE=CHARACTERIZE_THEN_NARROW_CLEANUP
```

---

## EXCEPTION_BOUNDARY_INVENTORY

Recovered live from the repository (not from R0's per-file notes alone), matching R0's `exception_candidates` file set exactly (8 files):

| Path | Live handler count | R0 classification |
|---|---|---|
| `legacy_documenter/documentation/generator.py` | 1 | HISTORICAL_COMPATIBILITY |
| `legacy_documenter/documentation/hierarchical.py` | 3 (`except Exception`, `except ValueError`, `except RuntimeError`) | HISTORICAL_COMPATIBILITY |
| `legacy_documenter/documentation/resume.py` | 6 | REFACTOR_CANDIDATE |
| `legacy_documenter/documentation/systematic.py` | 1 | HISTORICAL_COMPATIBILITY |
| `legacy_documenter/llm/copilot_pilot.py` | 1 | JUSTIFIED_BOUNDARY |
| `legacy_documenter/llm/providers/copilot.py` | 4 | JUSTIFIED_BOUNDARY |
| `legacy_documenter/llm/providers/gemini.py` | 2 | JUSTIFIED_BOUNDARY |
| `legacy_documenter/main.py` | 4 | JUSTIFIED_BOUNDARY |

Live inspection corrected two R0 per-file notes: `generator.py`/`hierarchical.py`/`systematic.py`'s sole `except Exception` directly wraps `asyncio.run(discover_model())` (a provider-discovery call), so despite R0's file-level `HISTORICAL_COMPATIBILITY` label, that specific catch site is a provider boundary, not a documentation-handler cleanup candidate. Conversely, `main.py`'s R0 note ("Top-level CLI entry point translating internal stage failures into a safe exit path") does not match the live code: its 4 handlers are inside `analyze_repository`'s deterministic per-file extraction loop, three of them (`CallExtractor`, `WebEventExtractor`, `DatabaseExtractor`) sharing an identical shape unrelated to any provider call.

## ADAPTER_INVENTORY

One redundant-adapter finding: `legacy_documenter/main.py::analyze_repository` contained three near-identical `try: sink.append(extractor.extract(full_path, root)) except Exception as exc: errors.append({...})` blocks (CallExtractor, WebEventExtractor, DatabaseExtractor), differing only in the extractor object, target list, and label string -- classified `SEMANTICALLY_IDENTICAL`. A fourth, differently-shaped handler in the same function (branching over solution/vb_project/vb_source/webform/web_config file types) was left unchanged (`DIFFERENT`).

## PROVIDER_BOUNDARY_INVENTORY

```text
PROVIDER_BOUNDARY_PRODUCTION_CHANGES=0
```

| Path | Current catch | Provider | Existing taxonomy | Existing contract tests | Reason deferred |
|---|---|---|---|---|---|
| `legacy_documenter/documentation/generator.py` | `except Exception` around `discover_model()` | Copilot (local) | No | Yes (`V3-R7_BLOCKED_PROVIDER` fixtures) | Provider Boundary Fence; TD-002 explicitly deferred |
| `legacy_documenter/documentation/hierarchical.py` | `except Exception` around `discover_model()`; `except ValueError`/`except RuntimeError` around provider-response synthesis | Copilot (local) | No | Yes | Same |
| `legacy_documenter/documentation/systematic.py` | `except Exception` around `discover_model()` | Copilot (local) | No | Yes | Same |
| `legacy_documenter/llm/copilot_pilot.py` | `except Exception as exc` classifying auth/access failure | Copilot (local) | Partial (`BLOCKED_COPILOT_AUTH`/`BLOCKED_COPILOT_ACCESS`) | Yes | Scope Fence forbids touching `copilot_pilot.py` |
| `legacy_documenter/llm/providers/copilot.py` | 4 handlers converting subprocess/Chat failures to `ProviderError` | Copilot | Yes (domain `ProviderError`) | Yes | R0 JUSTIFIED_BOUNDARY; matches TD-002's stated plan |
| `legacy_documenter/llm/providers/gemini.py` | 2 handlers converting HTTP/urllib failures to `ProviderError` | Gemini | Yes (domain `ProviderError`) | Yes | R0 JUSTIFIED_BOUNDARY |

No generic `ProviderException`/`LLMException`/`AdapterException`, no retry framework, no cross-provider normalization introduced.

---

## IN_SCOPE_CANDIDATES

```text
IN_SCOPE_CANDIDATES=1
```

`legacy_documenter/main.py::analyze_repository` -- the three duplicated CallExtractor/WebEventExtractor/DatabaseExtractor blocks.

## OUT_OF_SCOPE_PROVIDER_BOUNDARIES

```text
OUT_OF_SCOPE_PROVIDER_BOUNDARIES=6
```

`generator.py`, `hierarchical.py`, `systematic.py`, `copilot_pilot.py`, `providers/copilot.py`, `providers/gemini.py`.

## OUT_OF_SCOPE_HIGH_RISK

```text
OUT_OF_SCOPE_HIGH_RISK=1
```

`legacy_documenter/documentation/resume.py` (named in this round's High-Risk Fence; live inspection found all 6 handlers entangled with `provider.structured_generate`/`store.persist`, so no tiny isolated handler qualified for narrowing even under the R0 plan's original R7 language). `database_extractor.py`, `flow_resolver.py`, `deep_source.py` inspected for classification evidence only (already covered by R5/R6 characterization); zero production edits.

## NEEDS_CHARACTERIZATION

```text
NEEDS_CHARACTERIZATION=0
```

---

## CHARACTERIZATION_TESTS

```text
CHARACTERIZATION_TESTS=5
```

`tests/test_v4_1_r7_exception_boundaries_characterization.py` -- pins `analyze_repository`'s error-record shape, ordering (CallExtractor before WebEventExtractor before DatabaseExtractor per file), and partial-result behavior for each of the three IN_SCOPE handlers, both individually and simultaneously, plus the no-failure baseline. All 5 tests were run and passed against the pre-cleanup code, then re-run unchanged and passed against the post-cleanup code.

## EXCEPTION_MAP

See `output/v4_1_r7/V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json` -> `characterization.exception_map` (7 entries: the 4 `main.py` handlers plus the 3 provider-discovery catches in `generator.py`/`hierarchical.py`/`systematic.py`).

---

## SAFE_LOCAL_CLEANUPS

```text
SAFE_LOCAL_CLEANUPS=1
```

`legacy_documenter/main.py::analyze_repository`'s three duplicated extractor blocks, consolidated into one internal `_extract_into` helper.

## CHARACTERIZED_BUT_DEFERRED

```text
CHARACTERIZED_BUT_DEFERRED=1
```

`legacy_documenter/documentation/resume.py`.

## DO_NOT_CHANGE

```text
DO_NOT_CHANGE=6
```

The 6 provider-boundary files listed above.

## R7_CLEANUP_GATE

```text
R7_CLEANUP_GATE=OPEN
```

---

## AUTHORIZED_CLEANUPS

```text
AUTHORIZED_CLEANUPS=1
```

## DEFERRED_CLEANUPS

```text
DEFERRED_CLEANUPS=1
```

## CLEANUPS_PERFORMED

```text
CLEANUPS_PERFORMED=1
```

`legacy_documenter/main.py`: replaced three duplicated `try/except Exception` blocks with calls to a new private helper `_extract_into(extractor, label, source, full_path, root, sink, errors)`. Same caught exception type (`Exception`), same error-record shape (`{"file", "extractor", "error"}`), same per-file call order, same partial-result behavior (a failing extractor does not stop the next one from running). No public symbol, signature, or behavior changed.

---

## PRODUCTION_FILES_ADDED

```text
PRODUCTION_FILES_ADDED=0
```

## PRODUCTION_FILES_MODIFIED

```text
PRODUCTION_FILES_MODIFIED=1
```

`legacy_documenter/main.py`

---

## PUBLIC_IMPORT_COMPATIBILITY

```text
PUBLIC_IMPORT_COMPATIBILITY=PASS
```

## PUBLIC_SIGNATURE_COMPATIBILITY

```text
PUBLIC_SIGNATURE_COMPATIBILITY=PASS
```

`analyze_repository`'s signature is unchanged; `_extract_into` is a new private helper, not part of the public surface.

## SUCCESS_RESULT_EQUIVALENCE

```text
SUCCESS_RESULT_EQUIVALENCE=PASS
```

## FAILURE_RESULT_EQUIVALENCE

```text
FAILURE_RESULT_EQUIVALENCE=PASS
```

## EXCEPTION_TYPE_EQUIVALENCE

```text
EXCEPTION_TYPE_EQUIVALENCE=PASS
```

## EXCEPTION_MESSAGE_EQUIVALENCE

```text
EXCEPTION_MESSAGE_EQUIVALENCE=PASS
```

## ORDERING_EQUIVALENCE

```text
ORDERING_EQUIVALENCE=PASS
```

## SIDE_EFFECT_EQUIVALENCE

```text
SIDE_EFFECT_EQUIVALENCE=PASS
```

## PARTIAL_RESULT_EQUIVALENCE

```text
PARTIAL_RESULT_EQUIVALENCE=PASS
```

All six equivalences verified by `tests/test_v4_1_r7_exception_boundaries_characterization.py`, unchanged before/after the cleanup, plus the full regression suite.

---

## PROVIDER_BOUNDARY_PRODUCTION_CHANGES

```text
PROVIDER_BOUNDARY_PRODUCTION_CHANGES=0
```

## R6_DEFERRED_GROUPS_PRESERVED

```text
R6_DEFERRED_GROUPS_PRESERVED=PASS
```

`git status` shows no changes to `legacy_documenter/extractors/database_extractor.py` or `legacy_documenter/analysis/flow_resolver.py`; `_path_id`, `_path_identities`, `_add_path`, `_call_ref`, `_stable_id` untouched.

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
| `output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json` | `eb07e0f35540e0607b90f8ff707c7cac8e1f113419d338e3cc8579fa12f1e617` |
| `output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json` | `04c82d51b17664630adcafe26dd343d5f0740932904c77dd7a458029d547be32` |
| `output/v4_1_r6/V4_1_R6_EXTRACTION_EQUIVALENCE.json` | `bb60f1bd1b527003b2cbfdfcd98f13d77ca3cff246dc9b23c820da5378861ab1` |

None regenerated; none touched.

## R0_FROZEN_INVENTORY_MODIFIED

```text
R0_FROZEN_INVENTORY_MODIFIED=false
```

`output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json` and `output/v4_1_r0/V4_1_REFACTOR_PLAN.json` untouched (`git diff --stat` empty). `legacy_documenter/main.py`'s live structural metrics legitimately moved (line/function count up, `except_exception_count` 4->2 as three redundant handlers collapsed into one shared helper); the live-reconstruction comparison test (`tests/test_v4_1_r0_maintainability_inventory.py`) was extended, not weakened, adding `legacy_documenter/main.py` to the acknowledged-diff set with explicit before/after assertions on `production_inventory`, `largest_modules`, `largest_functions`, and `exception_candidates`, following the same pattern R4/R6 used for `readiness.py`/`database_extractor.py`/`flow_resolver.py`.

---

## R7_EQUIVALENCE_ARTIFACT

```text
R7_EQUIVALENCE_ARTIFACT=output/v4_1_r7/V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json
```

## R7_EQUIVALENCE_ARTIFACT_SHA256

```text
R7_EQUIVALENCE_ARTIFACT_SHA256=ccb21db6b051b15b19c617dc387f28d7910386e634036f777b2a7eff374a5d4d
```

## R7_EQUIVALENCE_ARTIFACT_DETERMINISM

```text
R7_EQUIVALENCE_ARTIFACT_DETERMINISM=PASS
```

Generated twice independently (via `tools/v4_1_r7_build_artifact.py`); both runs produced the identical SHA-256 above.

---

## DEBT_002_STATUS

```text
DEBT_002_STATUS=RESOLVED
```

## DEBT_003_STATUS

```text
DEBT_003_STATUS=RESOLVED
```

## TD_005_STATUS

```text
TD_005_STATUS=PARTIALLY_RESOLVED
```

Unchanged from R6; R7 did not continue TD-005 broadly.

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

No file under `legacy_documenter/knowledge/` was touched this round.

---

## PRODUCTION_CODE_CHANGED

```text
PRODUCTION_CODE_CHANGED=true
```

## PRODUCTION_BEHAVIOR_CHANGED

```text
PRODUCTION_BEHAVIOR_CHANGED=false
```

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
latest_completed_round = "V4.1-R7"
latest_approved_round = "V4.1-R6"
current_round_in_progress = "V4.1-R7 (pending Technical Lead review)"
round_status = "V4_1_R7_READY_FOR_HUMAN_REVIEW"
next = "HUMAN_REVIEW_V4_1_R7"
tests = 1566
readiness = "READY"
ai_knowledge_allowed = true
ai_knowledge_generated = false
provider_calls = 0
real_llm_calls = 0
```

V4 remains formally closed. This round is not approved; no commit or push was performed.

---

## DECISION

```text
DECISION=V4_1_R7_READY_FOR_HUMAN_REVIEW
```

## NEXT

```text
NEXT=HUMAN_REVIEW_V4_1_R7
```

---

# Closure Addendum (V4.1-R7 Approval and Versioning)

## HUMAN_REVIEW

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD
```

Registered per `prompts/V4_1/V4_1_R7_APPROVAL_AND_VERSIONING.md`. The Technical Lead explicitly reviewed and approved `V4.1-R7 -- Exception Boundaries and Adapter Cleanup`: `R7_MODE=CHARACTERIZE_THEN_NARROW_CLEANUP`, baseline 1561 / final 1566 passing tests, the 5 new characterization tests, the live exception-boundary inventory, the six provider-boundary files kept out of production cleanup, `resume.py` characterized but deferred, exactly one `SAFE_LOCAL_CLEANUP` performed (the `_extract_into` consolidation in `legacy_documenter/main.py::analyze_repository`), preservation of caught exception type/error shape/message/label/ordering/partial-result behavior, public import/signature compatibility, zero provider production changes, R6 deferred-group preservation, approved-artifact integrity, R0 frozen inventory untouched, `PRODUCTION_BEHAVIOR_CHANGED=false`, and that no R7.1 corrective round is required.

## R7_MODE_DECISION

```text
R7_MODE_DECISION=CHARACTERIZE_THEN_NARROW_CLEANUP_APPROVED
```

## EXCEPTION_BOUNDARY_INVENTORY_DECISION

```text
EXCEPTION_BOUNDARY_INVENTORY_DECISION=APPROVED
```

## SAFE_LOCAL_CLEANUPS

```text
SAFE_LOCAL_CLEANUPS=1
```

## AUTHORIZED_CLEANUPS

```text
AUTHORIZED_CLEANUPS=1
```

## CLEANUPS_PERFORMED

```text
CLEANUPS_PERFORMED=1
```

## PROVIDER_BOUNDARY_PRODUCTION_CHANGES

```text
PROVIDER_BOUNDARY_PRODUCTION_CHANGES=0
```

## R6_DEFERRED_GROUPS_PRESERVED

```text
R6_DEFERRED_GROUPS_PRESERVED=PASS
```

## R7_EQUIVALENCE_DECISION

```text
R7_EQUIVALENCE_DECISION=APPROVED
```

Recomputed SHA-256 of `output/v4_1_r7/V4_1_R7_EXCEPTION_BOUNDARY_EQUIVALENCE.json`: `ccb21db6b051b15b19c617dc387f28d7910386e634036f777b2a7eff374a5d4d` -- matches exactly.

## R7_1_REQUIRED

```text
R7_1_REQUIRED=false
```

## ROUND_STATUS

```text
ROUND_STATUS=APPROVED
```

## DECISION

```text
DECISION=V4_1_R7_FORMALLY_APPROVED
```

## NEXT

```text
NEXT=V4.1-R8
```
