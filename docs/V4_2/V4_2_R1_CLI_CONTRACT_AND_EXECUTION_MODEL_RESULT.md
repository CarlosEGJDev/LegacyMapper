# V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL — Result

TASK=V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL

MODE=CONTROLLED_IMPLEMENTATION

---

## STATUS

STATUS=V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL_COMPLETE

---

## BASELINE

V4.2-R0 (`docs/V4_2/V4_2_R0_FULL_PIPELINE_ARCHITECTURE_AND_INVENTORY_RESULT.md`) reviewed and approved by the Technical Lead, per task authority. `PROJECT_STATE.json` unchanged by this task. V4.1 remains `FORMALLY_CLOSED`; nothing under `docs/V4/`, `docs/V4_1/`, or the V4.1 final baseline/manifest was modified.

---

## FILES_CREATED

- `legacy_documenter/cli/__init__.py`
- `legacy_documenter/cli/parser.py` — argument parsing, legacy-invocation normalization
- `legacy_documenter/cli/router.py` — command routing (`analyze`/`full`/`readiness`)
- `legacy_documenter/cli/execution_model.py` — `RunStatus`, `StageStatus`, `StageError`, `StageResult`, `RunResult`
- `legacy_documenter/cli/stage_identity.py` — `StageId`
- `legacy_documenter/cli/serialization.py` — deterministic `RunResult` rendering
- `tests/test_v4_2_r1_cli_contract_and_execution_model.py` — 35 new focused tests
- `docs/V4_2/V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL_RESULT.md` (this file)

## FILES_MODIFIED

- `legacy_documenter/main.py` — `main()` now builds the parser/router from `legacy_documenter.cli`; `analyze_repository()` and every other pre-existing function are **byte-identical**, only `main()` and the top-level imports changed. The stale `argparse.ArgumentParser(description="Legacy .NET Documentation Analyzer V1")` string (already flagged as a cosmetic defect in `docs/V4_1/LEGACYMAPPER_TECHNICAL_MANUAL_V4_1.md` section 18) was corrected to `"LegacyMapper Documentation Analyzer"` while this exact line was necessarily touched to add subcommands.
- `tests/test_v4_1_r0_maintainability_inventory.py` — this is a pre-existing V4.1-R0 characterization test that pins the exact live production-file count and diffs the live AST-scanned inventory against a frozen V4.1-R0 snapshot, extending its established per-round delta tracking to account for the six new `legacy_documenter/cli/` modules (file count 153→159; `risk_summary` LOW +5/MEDIUM +1; `dependency_findings.module_count` delta +10→+16). Every delta was computed empirically by running the same `tools.v4_1_r0.report.build_inventory` the test itself uses (not hand-estimated), and no existing assertion was weakened — only the already-established "new files legitimately appear here" pattern (used by every prior V4.1 round: R1, R4, R6) was extended one more time. No V4.1 historical *artifact* (the frozen `output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json` itself, or any closure document) was touched — only the test that compares against it.

---

## CLI_ARCHITECTURE

A small `legacy_documenter/cli/` package was introduced, per the prompt's illustrative shape, with responsibilities kept separate:

- **`parser.py`** — CLI parsing only: builds the `analyze`/`full`/`readiness` subparsers and rewrites a legacy invocation into an explicit `analyze` one (`normalize_argv`). Knows nothing about what a command *does*.
- **`router.py`** — command routing only: given parsed arguments, calls the one existing capability each command maps to (`analyze_repository` for `analyze`, `legacy_documenter.knowledge.readiness.run` for `readiness`) or reports the R1 placeholder for `full`. Contains no analysis logic of its own.
- **`execution_model.py`** / **`stage_identity.py`** / **`serialization.py`** — the execution/result model, kept as pure data types with no I/O and no orchestration behavior.

`legacy_documenter/main.py` keeps 100% of the existing analysis implementation (`analyze_repository`, `apply_project_namespaces`, `consolidate_partial_symbols`, `_extract_into`, `_norm_path`) untouched; it was not turned into a larger monolith — the only change to `main()` is that it now delegates to `cli.parser`/`cli.router` instead of building its own `argparse.ArgumentParser` inline.

---

## LEGACY_CLI_COMPATIBILITY

Verified directly, not assumed:

```
python main.py tests/fixtures/v2_r1_sample --output <dir_a>
python main.py analyze tests/fixtures/v2_r1_sample --output <dir_b>
diff -rq <dir_a> <dir_b>   →   IDENTICAL OUTPUT
```

The legacy bare-positional form and the explicit `analyze` form produce byte-identical output trees. `normalize_argv` rewrites any argument list whose first token is not itself `analyze`/`full`/`readiness` (a repository path, a leading flag such as `--output`, `--help`, or no arguments at all) into an explicit `analyze` invocation before argparse parses it — verified with dedicated tests for all of: bare repository, bare repository with trailing flags, flags placed *before* the positional repository, and no arguments at all.

`python main.py --help` and `python main.py analyze --help` both exit `0` and print the same option set the pre-V4.2 parser printed (`repository`, `--output`, `--exclude`, `--verbose`, `--flow-max-depth`) — verified manually. `python main.py --help` resolves to `analyze --help` under the same normalization rule that makes bare invocations work, which is intentionally consistent: a legacy user asking for help gets the same reference they always got.

---

## ANALYZE_COMMAND

`python main.py analyze <repository> [--output OUTPUT] [--exclude FOLDER] [--verbose] [--flow-max-depth N]` — identical option set and defaults to the pre-V4.2 top-level parser. Routes straight to the existing, unmodified `analyze_repository()`; `router._route_analyze` passes through the four arguments unchanged and returns `RunResult(command="analyze", status=RunStatus.SUCCESS)` on completion (verified with a fake injected `analyze_repository` asserting the exact call signature).

---

## FULL_COMMAND

`python main.py full <repository> [same options as analyze]` — parses and routes, but is a **clearly controlled placeholder**, per the hard requirement:

- Never calls `analyze_repository` (or any other stage) — verified with a test where the injected fake raises `AssertionError` if called at all, and the test passes.
- Never imports or references `deep_interpretation`, `knowledge.proposals`, `knowledge.approval`, `knowledge.canonical`, `knowledge.projection`, `knowledge.plugin_projection`, or `knowledge.ingestion` — verified by asserting none of those tokens appear in `router.py`'s source.
- Returns `RunResult(command="full", status=RunStatus.FAILED, stages=(StageResult(stage=FINAL_SUMMARY, status=FAILED, error=StageError(category="NOT_IMPLEMENTED_FOR_R1", ...)),))`.
- Exits with `EXIT_NOT_IMPLEMENTED = 3` (distinct from `0`=success and argparse's own `2`=usage error, so a script can tell "full isn't implemented yet" apart from "you typed the command wrong").
- Prints its error message via `LOG.error(...)` (always visible, independent of `--verbose`) rather than pretending to succeed.

Manual verification: `python main.py full tests/fixtures/v2_r1_sample --output <dir>` printed `ERROR: full: The V4.2 full pipeline is not implemented yet...` and exited `3`; no `<dir>` was created.

---

## READINESS_COMMAND

`python main.py readiness` is a thin route: `router._route_readiness` calls `legacy_documenter.knowledge.readiness.run()` (the exact function `python -m legacy_documenter.knowledge.readiness` already used) and prints the same JSON shape (`json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)`). No readiness logic is duplicated — a dedicated test asserts the router source literally imports `run as run_readiness` from `legacy_documenter.knowledge.readiness` rather than reimplementing any check. `RunStatus` is `SUCCESS` (exit `0`) when `payload["readiness"] == "READY"`, otherwise `PARTIAL` (exit `1`) — verified with both a `READY` and a non-`READY` fake payload.

**`python -m legacy_documenter.knowledge.readiness` was not touched** and still works: verified via `subprocess.run([sys.executable, "-m", "legacy_documenter.knowledge.readiness"], ...)` in the new test suite, and manually — same output shape as before this round.

---

## EXECUTION_MODEL

Implemented in `legacy_documenter/cli/execution_model.py` as small, frozen dataclasses/enums — no workflow engine, no DAG, no dependency injection framework:

- `RunStatus(str, Enum)`: `SUCCESS`, `PARTIAL`, `FAILED`.
- `StageStatus(str, Enum)`: `SUCCESS`, `FAILED`, `SKIPPED_DUE_TO_UPSTREAM_FAILURE`, `NOT_RUN`.
- `StageResult` (frozen dataclass): `stage: StageId`, `status: StageStatus`, `error: StageError | None`.
- `RunResult` (frozen dataclass): `command: str`, `status: RunStatus`, `stages: tuple[StageResult, ...]`, `message: str | None`.

R1 uses this minimally — `analyze` produces a single-outcome `RunResult` with no populated `stages`, `full` produces one placeholder `StageResult`. The model exists so R2+ can populate `stages` with real per-stage outcomes without changing this type's shape; nothing in R1 executes multiple stages through it.

---

## STAGE_MODEL

`legacy_documenter/cli/stage_identity.py::StageId` defines 13 stable stage names: `SCAN`, `EXTRACTION`, `CALL_RESOLUTION`, `WEB_ENTRY_RESOLUTION`, `DATABASE_RESOLUTION`, `FLOW_RESOLUTION`, `DEPENDENCY_RESOLUTION`, `EXPORT`, `CONTEXT`, `DOCUMENTATION`, `AI_INTERPRETATION`, `PROPOSAL_GENERATION`, `FINAL_SUMMARY` — exactly the prompt's candidate list, with one documented clarification rather than a correction: `EXPORT` is kept singular (not split into a JSON-export/Markdown-export pair) because `analyze_repository()` always runs `JSONExporter` and `MarkdownExporter` back-to-back as one deterministic step today — there is no independent failure boundary between them to justify two stage identities. No orchestrator executes these identities in R1; `full`'s placeholder result references only `FINAL_SUMMARY`.

---

## ERROR_MODEL

`StageError` (frozen dataclass): `stage: StageId`, `category: str`, `message: str`, `reference: str | None = None`. `to_dict()` renders only these declared fields — never a raw traceback, never environment contents. Verified with tests asserting the rendered dict's keys are exactly `{stage, category, message}` (plus `reference` only when set), and that a sample message contains no traceback markers (`"Traceback"`, `'  File "'`). R1 defines the contract only — no stage-level exception handling is implemented yet (explicitly deferred, see DEFERRED_TO_R2).

---

## SERIALIZATION

`legacy_documenter/cli/serialization.py::render_run_result` reuses the existing `legacy_documenter.utils.json_rendering.render_deterministic_json` (the same sorted-keys/fixed-separators renderer already shared by the V4 knowledge sub-packages) instead of writing a second deterministic-JSON writer. Verified: two independently constructed but value-equal `RunResult` instances serialize to identical bytes; a plain `RunResult` renders to exactly `{"command":"analyze","stages":[],"status":"SUCCESS"}` (sorted keys, no whitespace); no field name in the rendered payload contains `id`/`time` (no UUID, no timestamp). No machine-specific absolute path is part of the model — commands only ever carry whatever the caller explicitly passed in.

---

## TESTS

New: `tests/test_v4_2_r1_cli_contract_and_execution_model.py` — 35 tests covering `normalize_argv`, subcommand parsing/defaults, `analyze`/`full`/`readiness` routing, the execution/stage/error models, deterministic serialization, and the approval boundary (no `approve` subcommand exists; `router.py` never references `ApprovalAuthority`/`CanonicalKnowledgeEntry`).

Modified: `tests/test_v4_1_r0_maintainability_inventory.py` — extended (not weakened) to account for the new `legacy_documenter/cli/` package, per FILES_MODIFIED above.

```
python -m unittest discover -s tests
Ran 1601 tests in 33.782s
OK
```

TESTS=1601_PASS_0_FAIL_0_SKIP (1566 pre-existing + 35 new; 0 tests removed or weakened)

---

## READINESS

```
python -m legacy_documenter.knowledge.readiness
readiness=READY, provider_calls=0, real_llm_calls=0
```

READINESS=READY

---

## PRODUCTION_BEHAVIOR_CHANGED

PRODUCTION_BEHAVIOR_CHANGED=false

The deterministic analysis pipeline's observable behavior and generated artifacts are unchanged — verified byte-for-byte identical between the legacy invocation and the new `analyze` subcommand against `tests/fixtures/v2_r1_sample`. The only user-visible additions are new commands (`full`, `readiness`) and a corrected (previously stale) argparse description string; no existing command's output changed.

## V4_1_REOPENED

V4_1_REOPENED=false

## V5_IMPLEMENTED

V5_IMPLEMENTED=false

## PLUGIN_RUNTIME

PLUGIN_RUNTIME=NOT_IMPLEMENTED

---

## DEFERRED_TO_R2

- Full-pipeline orchestration itself (actually running SCAN→EXTRACTION→...→FINAL_SUMMARY through the stage model).
- Stage-level exception handling / the corrected partial-failure policy described in V4.2-R0 (wrapping resolver/exporter stages so one failure doesn't abort the whole run).
- Any code that populates more than one `StageResult` per run.

## DEFERRED_TO_R3

- New technical-document renderers (functional flows, database access, entry points) identified as `GENERATABLE_WITH_EXISTING_COMPONENTS` in V4.2-R0's documentation capability matrix.

## DEFERRED_TO_R4

- AI interpretation integration (wiring `deep_interpretation.py` into `full`).
- The `knowledge/proposals` adapter from AI interpretation output.
- Fixing `documentation/generator.py`'s hardcoded `output/v2_r5_1_full/` path and direct `CopilotProvider` instantiation (flagged HIGH risk in V4.2-R0), a precondition for reusing that module.

---

## RISKS

| Risk | Classification | Mitigation |
|---|---|---|
| `full`'s placeholder being mistaken for a working pipeline by a script that doesn't check the exit code | LOW | Distinct exit code (`3`, not `0` or argparse's `2`) plus an explicit `ERROR:`-prefixed message naming `NOT_IMPLEMENTED_FOR_R1`; covered by a dedicated test |
| `normalize_argv`'s first-token heuristic misclassifying an edge-case invocation | LOW | Exhaustively tested (bare repo, bare repo + flags, flags-before-positional, no args, explicit `analyze`/`full`/`readiness`); the only path treated as "explicit subcommand" is an exact first-token match against the closed 3-name set, so no repository path can accidentally collide unless a real repository were literally named `analyze`, `full`, or `readiness` — this narrow edge case is a known limitation of positional/subcommand disambiguation via argparse and is accepted as extremely unlikely in practice for this system's actual repository-path inputs, not silently ignored |
| `tests/test_v4_1_r0_maintainability_inventory.py`'s frozen-artifact-comparison test needing another manual delta update in R2+ as more `cli/` code is added | MEDIUM | Documented inline in the test itself (this round's comment block) so the next round's author has the empirical-recomputation method already modeled, rather than needing to reverse-engineer it |
| Execution model drifting from what R2's real orchestrator actually needs, forcing a breaking change later | LOW | Model was deliberately kept minimal (four types, no engine); `RunResult.stages` is already a tuple built to be populated incrementally, so R2 extending it is additive, not a redesign |

---

## DECISION

DECISION=V4_2_R1_READY_FOR_TECHNICAL_LEAD_REVIEW

## NEXT

NEXT=HUMAN_REVIEW_V4_2_R1
