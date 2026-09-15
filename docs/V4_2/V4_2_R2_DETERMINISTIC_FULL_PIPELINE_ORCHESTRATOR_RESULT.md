# V4_2_R2_DETERMINISTIC_FULL_PIPELINE_ORCHESTRATOR — Result

TASK=V4_2_R2_DETERMINISTIC_FULL_PIPELINE_ORCHESTRATOR

MODE=CONTROLLED_IMPLEMENTATION

---

## STATUS

STATUS=V4_2_R2_DETERMINISTIC_FULL_PIPELINE_ORCHESTRATOR_COMPLETE

---

## BASELINE

V4.2-R0 and V4.2-R1 reviewed and approved by the Technical Lead, per task authority. Entering baseline: `1601_PASS_0_FAIL_0_SKIP`. V4.1 remains `FORMALLY_CLOSED`; nothing under `docs/V4/`, `docs/V4_1/`, or the V4.1 final baseline/manifest was modified. `AI_RUNTIME_CALL_ALLOWED=false` was respected: no LLM/provider call is made anywhere in this round's code or tests.

---

## FILES_CREATED

- `legacy_documenter/cli/pipeline_stages.py` — deterministic stage functions (SCAN through CONTEXT), extracted from the pre-R2 `analyze_repository` without changing any stage's internal logic. Shared by both `analyze` and `full`.
- `legacy_documenter/cli/full_pipeline.py` — the resilient orchestrator (`run_full_pipeline`) implementing the R2 partial-failure policy and writing the run summary.
- `tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py` — 17 new focused tests.
- `docs/V4_2/V4_2_R2_DETERMINISTIC_FULL_PIPELINE_ORCHESTRATOR_RESULT.md` (this file)

## FILES_MODIFIED

- `legacy_documenter/main.py` — `analyze_repository()` now calls the shared stage functions in `legacy_documenter.cli.pipeline_stages` instead of inlining scanner/extractor/resolver/exporter code directly; it adds **no** stage-level exception handling of its own, so its observable behavior is unchanged (verified, see ANALYZE_EQUIVALENCE). `main()`'s handling of `full`'s result was updated to reflect the real (no longer placeholder) `RunResult` shape.
- `legacy_documenter/cli/router.py` — `_route_full` now calls `full_pipeline.run_full_pipeline(...)` instead of returning the R1 `NOT_IMPLEMENTED_FOR_R1` placeholder; the exit-code contract was extended (see EXIT_CODE_CONTRACT). No pipeline logic lives in the router itself.
- `legacy_documenter/cli/execution_model.py` — `RunResult` gained three always-rendered fields: `ai_invoked`, `canonical_knowledge_produced`, `technical_lead_approval` (all default `False`), per the R2 run-summary requirement that these invariants be stated explicitly, not by omission.
- `tests/test_v4_2_r1_cli_contract_and_execution_model.py` — the two tests that pinned R1's now-retired `NOT_IMPLEMENTED_FOR_R1` placeholder behavior for `full` were replaced with routing-only checks (the orchestrator's real behavior is covered in the new R2 test module); the `EXIT_NOT_IMPLEMENTED` import was removed; the deterministic-serialization literal test was updated for the three new `RunResult` fields. No test coverage was removed net of these changes — the retired assertions tested behavior that no longer exists (the placeholder itself), and equivalent-or-greater coverage of the real `full` behavior was added in the new R2 module.
- `tests/test_v4_1_r0_maintainability_inventory.py` — extended for the two new production modules and their knock-on effects on `legacy_documenter/main.py`'s own metrics (see MAINTAINABILITY_INVENTORY_UPDATE below). No V4.1 historical artifact was touched — only the test that compares live source against the frozen `output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json` snapshot.

---

## ORCHESTRATOR_ARCHITECTURE

Per section 16's guidance, a small dedicated component was added rather than growing `router.py`:

- **`legacy_documenter/cli/pipeline_stages.py`** — one function per deterministic stage (`scan_repository`, `extract_repository`, `resolve_calls`, `resolve_web_entries`, `resolve_database`, `resolve_flows`, `resolve_dependencies`, `export_artifacts`, `build_context_artifacts`), each a thin, faithful extraction of the exact pre-R2 inline code — no behavior was rewritten, only relocated and given a name and a return type (small `@dataclass` outcome objects instead of bare tuples, for readability at call sites). This module has **no** knowledge of `RunResult`, exit codes, or failure policy — it only knows how to run one stage and return its result or raise.
- **`legacy_documenter/cli/full_pipeline.py`** — the one place that knows about stage ordering, dependency rules, and the partial-failure policy. It calls the exact same `pipeline_stages` functions `analyze_repository` calls, wrapping each in `_run_stage` (catch-and-record) and skipping dependents via `_skipped` when a prerequisite did not succeed.
- **`legacy_documenter/main.py::analyze_repository`** — now a thin sequential caller of the same stage functions, with **no** added exception handling, preserving the pre-R2 abort-on-first-unexpected-error behavior exactly.

Responsibilities stayed separated as required: CLI parsing (`parser.py`) ≠ command routing (`router.py`, now just an exit-code mapping for `full`) ≠ orchestration (`full_pipeline.py`) ≠ stage implementation (`pipeline_stages.py`, itself calling the pre-existing `scanner`/`extractors`/`analysis`/`context`/`exporters` domain packages, which were not modified). No new interfaces, no dependency-injection framework, no DAG engine — `full_pipeline.py` is a straight-line sequence with explicit `if <upstream>_ok:` gates.

---

## ANALYZE_EQUIVALENCE

Verified with `tests/fixtures/v2_r1_sample` (the only committable fixture available; see V4.2-R0's TEST_FIXTURES note):

- `python main.py <fixture> --output <A>` (legacy) vs. `python main.py analyze <fixture> --output <B>` (explicit) via two separate subprocesses: identical file sets, and byte-identical content for every file **except** `index/repository.json`'s `duration_seconds` (wall-clock, legitimately non-deterministic between two separate process runs) — every other field of that file, including `stats`/`ignored`/`root`, is asserted byte-identical after masking only that one field.
- `analyze_repository()` called directly against the fixture reproduces the same `indexes` shape (`errors == []`, `len(symbols) == 2`, `len(projects) == 1`) and writes the same artifact set (`index/repository.json`, `documentation/PROJECT_OVERVIEW.md`, `context/projects.json`, `ai_context/SYSTEM_CONTEXT.json`) as before the refactor.
- `analyze` never writes `RUN_SUMMARY.json`/`.md` — confirmed explicitly, since that artifact is `full`-only.
- The existing V4.1-R7 characterization suite (`tests/test_v4_1_r7_exception_boundaries_characterization.py`, which patches `CallExtractor`/`WebEventExtractor`/`DatabaseExtractor` at the class level and calls `analyze_repository` directly) passes unchanged — proof that per-file error recording, call order, and the `indexes["errors"]` shape are untouched by moving the code into `pipeline_stages.py`.

No pre-R2 characterized behavior of `analyze`/legacy was found to differ.

---

## FULL_PIPELINE

`python main.py full <repository> --output <directory>` now executes the real deterministic pipeline (replacing R1's placeholder):

1. Runs SCAN → EXTRACTION → CALL_RESOLUTION → WEB_ENTRY_RESOLUTION → DATABASE_RESOLUTION → FLOW_RESOLUTION → DEPENDENCY_RESOLUTION → EXPORT → CONTEXT, each wrapped so a failure is recorded rather than aborting the process.
2. Assembles the same `indexes` shape `analyze` produces (using best-available data — see PARTIAL_FAILURE_POLICY) and writes the same `index/*.json`, `documentation/*.md`, `context/*.json`, `ai_context/*` artifacts via the shared `export_artifacts`/`build_context_artifacts` stage functions.
3. Writes `RUN_SUMMARY.json`/`.md` (FINAL_SUMMARY) under `--output`.
4. Returns an exit code representing overall run status (see EXIT_CODE_CONTRACT).

No AI interpretation, knowledge ingestion, proposal generation, approval, canonical knowledge, or R11/R12 projection is invoked anywhere in `full_pipeline.py` or `pipeline_stages.py` — verified by asserting none of those module names appear anywhere in either file's source (both in the R1 test module, extended, and in the new R2 module).

---

## STAGE_ORDER

Verified (a clean run against the fixture) to produce, in order: `SCAN, EXTRACTION, CALL_RESOLUTION, WEB_ENTRY_RESOLUTION, DATABASE_RESOLUTION, FLOW_RESOLUTION, DEPENDENCY_RESOLUTION, EXPORT, CONTEXT, FINAL_SUMMARY` — exactly the sequence in section 2 of the task. `DOCUMENTATION`, `AI_INTERPRETATION`, and `PROPOSAL_GENERATION` (three of the thirteen `StageId` members R1 established) are **not** part of the R2 stage list at all — they are out of scope for this round (no new renderers, no AI) and are simply never scheduled, not represented as `NOT_RUN` placeholders. `EXPORT` still covers both `JSONExporter` and `MarkdownExporter` together, per the R1 decision that they share one failure boundary; `CONTEXT` likewise covers both `ContextBuilder` and `SystemContextBuilder`.

---

## STAGE_DEPENDENCIES

Derived from the actual pre-R2 `analyze_repository` data flow (not assumed from the prompt), and confirmed via source inspection before implementation:

| Stage | Depends on | Why |
|---|---|---|
| SCAN | — | first stage |
| EXTRACTION | SCAN | needs `files`/`root` |
| CALL_RESOLUTION | EXTRACTION | needs `calls`, `symbols` |
| WEB_ENTRY_RESOLUTION | CALL_RESOLUTION | needs **resolved** calls, not raw extracted calls (the pre-R2 code reassigns `calls` to `CallResolver`'s output before calling `WebEntryResolver`) |
| DATABASE_RESOLUTION | EXTRACTION | needs `data_access_indexes`, `projects` — independent of CALL_RESOLUTION/WEB_ENTRY_RESOLUTION |
| FLOW_RESOLUTION | CALL_RESOLUTION, WEB_ENTRY_RESOLUTION, DATABASE_RESOLUTION (all three) | needs resolved calls, entry points, and resolved database access together |
| DEPENDENCY_RESOLUTION | EXTRACTION | needs `solutions`, `projects`, `symbols`, `webforms` — independent of every resolver above |
| EXPORT | EXTRACTION | needs the assembled `indexes`; runs with whatever resolver data is available, never hard-blocked on a specific resolver |
| CONTEXT | EXTRACTION | same as EXPORT |
| FINAL_SUMMARY | — | always attempted, even after a SCAN/EXTRACTION failure, so a failed run still produces a record of what happened |

One correction to the prompt's illustrative dependency list: DEPENDENCY_RESOLUTION does **not** depend on CALL_RESOLUTION/WEB_ENTRY_RESOLUTION/DATABASE_RESOLUTION — `DependencyResolver.resolve(solutions, projects, symbols, webforms)`'s actual signature only consumes EXTRACTION's output. Verified by test: `CallResolver.resolve` patched to raise still leaves `DEPENDENCY_RESOLUTION` (and `DATABASE_RESOLUTION`) `SUCCESS`.

---

## PARTIAL_FAILURE_POLICY

Implemented exactly as specified:

- Extraction stays **per-file tolerant**, unchanged (a bad file → an entry in `errors`, extraction continues).
- Every resolver/output stage is wrapped in `_run_stage`, which converts any exception into a `StageResult(status=FAILED, error=StageError(...))` instead of propagating it.
- A stage whose required upstream stage(s) did not succeed is marked `SKIPPED_DUE_TO_UPSTREAM_FAILURE` (via `_skipped`, which names the blocking stage(s) in the error message) and is **never executed** with invalid/missing prerequisites — no replacement/invented data is ever substituted for a resolver's output; a field whose stage failed or was skipped is an honest empty container (`[]` or `{}`), except `calls`, which falls back to the *raw extracted* (unresolved) call list when `CALL_RESOLUTION` itself did not succeed — a deliberate, documented exception, because extraction genuinely produced that data even though resolution could not use it.
- Verified: patching `CallResolver.resolve` to raise → `CALL_RESOLUTION=FAILED`, `WEB_ENTRY_RESOLUTION=SKIPPED_DUE_TO_UPSTREAM_FAILURE`, `FLOW_RESOLUTION=SKIPPED_DUE_TO_UPSTREAM_FAILURE`, while `DATABASE_RESOLUTION` and `DEPENDENCY_RESOLUTION` (independent) still run and `EXPORT`/`CONTEXT` still succeed with partial data → overall `PARTIAL`.
- Verified: patching `stages.export_artifacts` to raise → `EXPORT=FAILED` → overall `FAILED` (no minimally useful package, per RUN_STATUS_CONTRACT).
- Verified: patching `stages.scan_repository` to raise → `SCAN=FAILED`, `EXTRACTION`/`EXPORT`/etc. all `SKIPPED_DUE_TO_UPSTREAM_FAILURE` → overall `FAILED` — and `FINAL_SUMMARY` still runs, successfully writing a summary that records the failure (a failed run is never silent).

---

## RUN_STATUS_CONTRACT

Defined non-subjectively in `full_pipeline._compute_status` and stated here exactly as implemented:

**"Minimally useful deterministic analysis package"** = **EXTRACTION completed AND EXPORT completed** — i.e., real analysis artifacts (`index/*.json`, `documentation/*.md`) exist under `--output`. This is the one concrete, testable definition the whole status derivation hangs on:

- **FAILED**: `EXTRACTION` is not `SUCCESS`, or `EXPORT` is not `SUCCESS`. (Nothing useful was produced, regardless of what else happened.)
- **PARTIAL**: `EXTRACTION` and `EXPORT` both `SUCCESS`, but at least one of: any recorded per-file extraction error (`indexes["errors"]` non-empty), any stage `FAILED`, or any stage `SKIPPED_DUE_TO_UPSTREAM_FAILURE`.
- **SUCCESS**: `EXTRACTION` and `EXPORT` both `SUCCESS`, no extraction errors, and every stage `SUCCESS`.

One documented nuance: `RUN_SUMMARY.json`'s **written content** reflects status computed from stages SCAN..CONTEXT (before `FINAL_SUMMARY` itself is known to have succeeded, since the file can't describe its own write outcome); the **returned** `RunResult` (used for the exit code) recomputes status including `FINAL_SUMMARY`, so a `FINAL_SUMMARY` write failure still downgrades the exit code to at least `PARTIAL` even though the already-written file shows the pre-downgrade status. This is a deliberate, minor, documented limitation rather than an engineered-around edge case — a file cannot authoritatively report on its own write's success.

---

## EXIT_CODE_CONTRACT

```
0 = SUCCESS            (analyze, full, readiness)
1 = PARTIAL             (full, readiness)
2 = CLI_USAGE_ERROR     (argparse itself -- unknown command, missing argument; not assigned by this code, produced automatically)
4 = FAILED               (full)
```

`3` (`NOT_IMPLEMENTED_FOR_R1`, `full`'s R1 placeholder code) is **retired**, not reused — deliberately, so an R1-era script that happened to check for exit code 3 fails loudly instead of silently misreading a real R2 `FAILED`/`PARTIAL`/`SUCCESS` outcome as "not implemented." `readiness`'s existing `SUCCESS`/`PARTIAL` mapping (established in R1) is unchanged.

---

## RUN_SUMMARY

Two files, written under `--output` (not inside the analyzed repository) only by `full`, never by `analyze`:

- **`RUN_SUMMARY.json`** — authoritative, machine-readable. Exactly `render_run_result(result)` (the R1 deterministic serializer, reused rather than duplicated) — sorted keys, fixed separators, no timestamp/UUID/environment dump. Contains `command`, `status`, `stages` (each with `stage`, `status`, and `error` when present — `stage`/`category`/`message`/optional `reference`, never a raw traceback), `ai_invoked`, `canonical_knowledge_produced`, `technical_lead_approval`.
- **`RUN_SUMMARY.md`** — small, human-readable, pure formatting derived from the same `RunResult` (no separate logic, no duplicated data source): status, the three approval-boundary invariants, and a stage/status/error table.

Filename choice: `RUN_SUMMARY.{json,md}` at the top of `--output`, matching the existing SCREAMING_SNAKE_CASE convention already used for top-level generated documents in this repository (e.g. `PROJECT_OVERVIEW.md`, `KNOWLEDGE_READINESS.json`).

---

## SOURCE_IMMUTABILITY

No stage function, in either `pipeline_stages.py` or `full_pipeline.py`, writes, renames, deletes, or creates anything inside the analyzed repository — every write goes through `JSONExporter`/`MarkdownExporter`/`ContextBuilder`/`SystemContextBuilder` (unmodified, pre-existing, `--output`-scoped) or `full_pipeline._write_run_summary` (also `--output`-scoped). Verified with a dedicated test: SHA-256 hashes of every file in `tests/fixtures/v2_r1_sample` are identical before and after a full `run_full_pipeline` call against it.

---

## OUTPUT_BEHAVIOR

Every exporter/builder stage function uses `Path(...).mkdir(parents=True, exist_ok=True)` before writing (pre-existing behavior, unchanged) — an existing `--output` directory is never deleted or blindly overwritten wholesale; individual files within it are overwritten in place (also pre-existing behavior, unchanged for `analyze`). `full` follows the exact same convention: no new destructive cleanup, no recursive directory deletion, was introduced anywhere in this round.

---

## TESTS

New: `tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py` — 17 tests covering stage ordering, SUCCESS/PARTIAL/FAILED derivation, SKIPPED_DUE_TO_UPSTREAM_FAILURE + independent-stage-continues, extraction-error preservation, structured-error contract, run-summary determinism, the three approval-boundary invariants, source immutability, `analyze`/legacy/`readiness` compatibility, and the no-AI/no-knowledge-import guarantee.

Modified: `tests/test_v4_2_r1_cli_contract_and_execution_model.py` (2 tests replaced with routing-only equivalents reflecting the retired placeholder; 1 net test removed, superseded by broader R2 coverage — see FILES_MODIFIED) and `tests/test_v4_1_r0_maintainability_inventory.py` (extended, not weakened — see MAINTAINABILITY_INVENTORY_UPDATE).

```
python -m unittest discover -s tests
Ran 1617 tests in 34.881s
OK
```

TESTS=1617_PASS_0_FAIL_0_SKIP (1601 entering baseline − 1 retired R1 placeholder test + 17 new R2 tests = 1617; 0 tests removed without replacement, 0 weakened)

### MAINTAINABILITY_INVENTORY_UPDATE

`tests/test_v4_1_r0_maintainability_inventory.py` needed an update because two legitimate new production modules were added. Every number below was **recomputed using the same deterministic inventory builder the test itself uses** (`tools.v4_1_r0.report.build_inventory`), never hand-estimated:

| Metric | Previous value (post-R1) | New value (post-R2) | Reason | New modules responsible |
|---|---|---|---|---|
| Production file count | 159 | 161 | Two new modules added | `legacy_documenter/cli/pipeline_stages.py`, `legacy_documenter/cli/full_pipeline.py` |
| `dependency_findings.module_count` delta vs. frozen V4.1-R0 baseline | +16 | +18 | Same two new modules | same |
| `risk_summary.files_by_risk_category["LOW"]` | 86 | 86 (unchanged) | Neither new file is LOW risk | — |
| `risk_summary.files_by_risk_category["MEDIUM"]` | 52 | 54 | `full_pipeline.py` is MEDIUM risk (+1); `main.py`'s own risk_category also dropped HIGH→MEDIUM as a side effect of shrinking (+1) | `full_pipeline.py`; `main.py` (existing file, category shift, not a new module) |
| `risk_summary.files_by_risk_category["HIGH"]` | 16 | 16 (unchanged net) | `pipeline_stages.py` enters HIGH (+1) exactly offsetting `main.py` leaving HIGH (−1) | `pipeline_stages.py` entering; `main.py` leaving |
| `risk_summary.high_risk_files` membership | included `main.py` | includes `pipeline_stages.py` instead | same category shift | same |
| `largest_modules` (top-20) membership | included `main.py` | includes `pipeline_stages.py` and `full_pipeline.py`; `main.py` **and** `readiness.py` both drop out | Two new, larger entries (340/287 lines) displaced two existing members from the top-20 ranking — `readiness.py`'s own size (188 lines) is unchanged by R2; it was already near the cutoff and got pushed out by ranking, not by regressing itself | `pipeline_stages.py`, `full_pipeline.py` (entering); `main.py`, `readiness.py` (displaced) |
| `largest_functions` (top-N) membership | included `(main.py, analyze_repository)` | includes `(full_pipeline.py, run_full_pipeline)` instead | `analyze_repository` is now far shorter (delegates to `pipeline_stages`); the new orchestrator's ten explicit stage calls make it a new top-N entry | same two files |
| `exception_candidates` membership | included `main.py` | includes `pipeline_stages.py` and `full_pipeline.py` instead | All of `main.py`'s exception handling (the `_extract_into` helper and its try/except blocks) moved to `pipeline_stages.py`; `full_pipeline.py` adds its own per-stage try/except handling | `pipeline_stages.py`, `full_pipeline.py` (entering); `main.py` (leaving, now has zero exception handling) |
| `side_effect_candidates["filesystem_access"]` | 42 files | 44 files | `full_pipeline.py` writes `RUN_SUMMARY.*` directly; `pipeline_stages.py` inherits the signal from the exporter/context-builder calls it makes | `full_pipeline.py`, `pipeline_stages.py` |

The frozen `output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json` artifact itself was **not** modified — only the test comparing live source against it. No assertion was weakened: every changed assertion moved from an exact-equality or fixed-set check to an explicit, narrower set-difference/inequality check that still pins the exact expected delta, with the reasoning documented inline in the test (mirroring the pattern every prior V4.1 round already used for this same test).

---

## READINESS

```
python -m legacy_documenter.knowledge.readiness
readiness=READY, provider_calls=0, real_llm_calls=0
```

READINESS=READY

Also verified: `python main.py --help`, `python main.py analyze --help`, `python main.py full --help` all exit `0`; `python main.py readiness` exits `0` and prints the same JSON shape as `python -m legacy_documenter.knowledge.readiness`.

---

## AI_INVOKED

AI_INVOKED=false

## CANONICAL_KNOWLEDGE_PRODUCED

CANONICAL_KNOWLEDGE_PRODUCED=false

## TECHNICAL_LEAD_APPROVAL

TECHNICAL_LEAD_APPROVAL=false

All three are hard-coded `False` defaults on `RunResult`, always rendered explicitly (never omitted) in `RUN_SUMMARY.json`, and verified both on the in-memory `RunResult` and on the written JSON file's contents.

---

## PRODUCTION_BEHAVIOR_CHANGED

PRODUCTION_BEHAVIOR_CHANGED=true

This is expected and intentional: `full` went from an R1 placeholder (always `NOT_IMPLEMENTED_FOR_R1`, exit `3`) to a real, working deterministic pipeline. `analyze`'s and the legacy invocation's behavior did **not** change (see LEGACY_ANALYZE_BEHAVIOR_CHANGED).

## LEGACY_ANALYZE_BEHAVIOR_CHANGED

LEGACY_ANALYZE_BEHAVIOR_CHANGED=false

Verified byte-for-byte (modulo the pre-existing, legitimately non-deterministic `duration_seconds` field) via ANALYZE_EQUIVALENCE above.

## V4_1_REOPENED

V4_1_REOPENED=false

## V5_IMPLEMENTED

V5_IMPLEMENTED=false

## PLUGIN_RUNTIME

PLUGIN_RUNTIME=NOT_IMPLEMENTED

---

## DEFERRED_TO_R3

- New technical-document renderers for functional flows, database access, and web entry points (the data already exists in `indexes`; only rendering is missing — see V4.2-R0's documentation capability matrix).

## DEFERRED_TO_R4

- AI interpretation integration (wiring `analysis/deep_interpretation.py` into `full`).
- The `knowledge/proposals` adapter from AI interpretation output.
- Fixing `documentation/generator.py`'s hardcoded `output/v2_r5_1_full/` path and direct `CopilotProvider` instantiation (flagged HIGH risk in V4.2-R0), a precondition for reusing that module.
- A human-facing approval surface (`knowledge/approval` has no production caller yet).

---

## RISKS

| Risk | Classification | Mitigation |
|---|---|---|
| `_assemble_indexes`'s `calls` fallback-to-raw-extracted-data rule being mistaken for "resolved" data by a downstream consumer of `full`'s output | LOW | Documented explicitly in the function's own docstring and in this result document; the field's actual provenance (resolved vs. raw) is always inferable from whether `CALL_RESOLUTION`'s `StageResult` is `SUCCESS` in the same `RUN_SUMMARY.json` |
| The `RUN_SUMMARY.json`-content-vs-returned-exit-code nuance (pre-`FINAL_SUMMARY` status written to disk vs. post-`FINAL_SUMMARY` status returned) causing confusion in a rare `FINAL_SUMMARY`-write-failure case | LOW | Documented explicitly in RUN_STATUS_CONTRACT above and in `run_full_pipeline`'s docstring; the case only arises when the summary write itself fails, which is already a `PARTIAL`-or-worse condition being surfaced, not hidden |
| Two new large modules (`pipeline_stages.py` 340 lines HIGH-risk, `full_pipeline.py` 287 lines MEDIUM-risk) becoming touch-with-care refactor targets for later rounds | MEDIUM | Both are already covered by dedicated test suites (17 new R2 tests plus the reused R1/R7 characterization tests via shared stage functions); any future round touching them should add characterization tests first, per the established V4.1 methodology |
| `tests/test_v4_1_r0_maintainability_inventory.py` needing another manual, empirically-recomputed update in R3+ as more `cli/`-adjacent code is added | MEDIUM | The empirical-recomputation method (diff `tools.v4_1_r0.report.build_inventory` output against the frozen baseline, never hand-estimate) is now demonstrated twice (R1, R2) and documented inline in the test itself for the next round's author |
| Exit code `4` for `FAILED` not being a widely-recognized convention | LOW | Documented explicitly in EXIT_CODE_CONTRACT above; `0`/`1`/`2` follow common convention, `4` was chosen specifically to avoid colliding with argparse's own `2` per the task's explicit instruction |

---

## DECISION

DECISION=V4_2_R2_READY_FOR_TECHNICAL_LEAD_REVIEW

## NEXT

NEXT=HUMAN_REVIEW_V4_2_R2
