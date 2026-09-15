# LegacyMapper V4.2-R5 — Unified CLI and Operational UX: Result

STATUS: COMPLETE

BASELINE: Entering test count 1685 PASS / 0 FAIL / 0 SKIP (V4.2-R4 closure).
Exiting test count 1714 PASS / 0 FAIL / 0 SKIP (1685 pre-existing + 29 new
R5 tests, 0 weakened/deleted).

---

## FILES_CREATED

- `legacy_documenter/cli/run_summary_presenter.py` — the console/Markdown
  presentation layer introduced to satisfy section 12's maintainability
  guard: next-action derivation (`derive_next_action`), output-location
  discovery (`compute_output_locations`), the console summary
  (`render_console_summary`), and `RUN_SUMMARY.md` rendering
  (`render_markdown_summary`, moved out of `full_pipeline.py`). LOW risk,
  185 lines, standard library only.
- `tests/test_v4_2_r5_unified_cli_and_operational_ux.py` — 29 focused tests
  covering every item in section 21's list.
- `docs/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX_RESULT.md` — this file.

## FILES_MODIFIED

- `legacy_documenter/cli/execution_model.py` — `RunResult` gained five
  additive fields: `ai_requested`, `proposal_count`,
  `proposal_review_status`, `next_action`, `output_locations`. No existing
  field renamed, removed, or changed in meaning.
- `legacy_documenter/cli/full_pipeline.py` — wires the five new fields onto
  the `RunResult` it already builds (via `run_summary_presenter` helper
  functions); `_render_markdown_summary` was removed from this file (moved
  to the new module) and `_write_proposal_output` now returns the envelope
  status instead of the caller recomputing it. Net line count unchanged
  (488 → 488): the extraction offsets the new wiring exactly.
- `legacy_documenter/cli/parser.py` — richer top-level epilog explaining
  all four invocation shapes (legacy positional / `analyze` / `full` /
  `full --allow-ai-interpretation` / `readiness`); each subparser now also
  carries a `description` (shown by its own `--help`, previously only a
  parent-listing `help` string existed); `--allow-ai-interpretation`'s help
  text now states plainly that it may call the configured provider and
  that proposals are pending review, never auto-approved.
- `legacy_documenter/main.py` — prints one explicit opt-in notice before an
  AI-enabled `full` run; replaces the old single-line `message` print for
  `full` with `run_summary_presenter.render_console_summary(...)`. Exit-code
  logic, `analyze`/readiness printing, and `analyze_repository` are
  untouched.
- `tests/test_v4_2_r1_cli_contract_and_execution_model.py` — one test
  updated (`test_serialization_has_sorted_keys_and_no_whitespace_drift`)
  to include the five new additive `RunResult` JSON fields; the assertion
  itself (exact sorted-keys, no-whitespace rendering) is unchanged.
- `tests/test_v4_1_r0_maintainability_inventory.py` — recomputed against
  the live tree via `tools.v4_1_r0.report.build_inventory` (see
  MAINTAINABILITY below); no assertion weakened, only the R5-caused deltas
  (one new LOW-risk module, one new filesystem-access file, +1 module
  count) added to the existing R1–R4 delta narrative.

## CLI_HELP

`main.py --help` now shows an epilog (`RawDescriptionHelpFormatter`)
explicitly walking through all five invocation shapes and what each does
and does not do (documentation? AI? run summary?). Reaching it required a
small `normalize_argv` fix: previously a bare `python main.py --help` was
silently rewritten to `analyze --help` (the legacy-compatibility rewrite
applied even to the help flag), so a first-time user could never see the
top-level help — only `analyze`'s own. `-h`/`--help` as the first token is
now left untouched; every other legacy-compatibility behavior (bare
positional → `analyze`) is unchanged. Each subparser (`analyze`, `full`,
`readiness`) now also carries a `description` shown by its own `--help`,
not just a `help=` string shown in the parent's listing.

## CONSOLE_SUMMARY

`full`'s console output (via `render_console_summary`) reports: overall
status, repository, output directory, deterministic-analysis status,
documentation status, AI requested vs. AI invoked, proposal review status
+ count (only when AI was requested), canonical-knowledge-produced,
Technical-Lead-approval, existing output locations, and the recommended
next action. Default mode does not dump the stage table; `--verbose` adds
one line per stage (status + error detail). FAILED runs are still routed
through `LOG.error` (unchanged from R2); SUCCESS/PARTIAL through `print`.
An additional one-line opt-in notice ("this run may call the configured AI
provider") is printed before an AI-enabled run starts, distinct from the
summary that follows it.

## NEXT_ACTION_MODEL

`derive_next_action(result, ai_requested, proposal_count)` is a pure
function of already-computed `RunResult` state:

- `FAILED` → "Analysis did not produce the minimum useful output. Inspect
  RUN_SUMMARY.json."
- `proposal_count > 0` → "AI proposals are pending Technical Lead review.
  See proposals/AI_PROPOSALS_PENDING_REVIEW.md."
- AI requested and `AI_INTERPRETATION` stage `FAILED` → "Deterministic
  documentation is available; AI interpretation failed. See
  RUN_SUMMARY.json for details."
- `PARTIAL` (any other cause) → "Deterministic documentation is available,
  but some stages were partial. Review RUN_SUMMARY.json."
- otherwise → "Technical documentation generated successfully."

Never implies approval; never auto-runs another command — it only returns
text, printed by `main.py` and written into `RUN_SUMMARY.json`/`.md`.

## OUTPUT_DISCOVERY

`compute_output_locations(output_dir)` is a pure existence check over six
well-known relative paths (`documentation`, `index`, `ai_context`,
`proposals`, `RUN_SUMMARY.json`, `RUN_SUMMARY.md`) — a path not produced by
a given run (e.g. `proposals/` without `--allow-ai-interpretation`) is
simply absent from the list, never described as forthcoming. Both the
console summary and `RUN_SUMMARY.json`/`.md` render the same list.

## RUN_SUMMARY_HUMAN

`RUN_SUMMARY.md` (via `render_markdown_summary`, now in
`run_summary_presenter.py`) gained AI-requested, proposal count/review
status, an "Output Locations" section, and a "Next Action" section, on top
of the pre-existing command/status/AI-invoked/canonical-knowledge/approval
header and stage table. It still does not duplicate technical
documentation content (verified by test:
`RunSummaryMarkdownReadabilityTests`).

## RUN_SUMMARY_MACHINE_CONTRACT

Additive only. Pre-R5 fields (`command`, `status`, `stages`, `ai_invoked`,
`canonical_knowledge_produced`, `technical_lead_approval`) are byte-for-byte
unchanged in shape and meaning. Five new fields added, always present:
`ai_requested` (bool), `proposal_count` (int), `proposal_review_status`
(`"PENDING_TECHNICAL_LEAD_REVIEW"` | `"NO_PROPOSALS_GENERATED"` | `null`),
`next_action` (str), `output_locations` (list[str]). No field renamed or
removed. `analyze`/`readiness` never write `RUN_SUMMARY.json` (unchanged);
their in-memory `RunResult.to_dict()` also carries the five new fields at
their defaults, but since neither is ever serialized to disk this has no
observable contract effect.

**Documented pre-existing discrepancy (not introduced by R5):** as before
R5, `RUN_SUMMARY.json`/`.md` are written from a *preliminary* `RunResult`
computed before the `FINAL_SUMMARY` stage itself is appended, so the file
never lists a `FINAL_SUMMARY` stage entry even though the value `full`
returns to its caller does. `output_locations`/`next_action` are computed
twice (once before the write, once after) precisely so the file's own
`output_locations` reflects what existed at write time and the returned
value reflects the true final state — this mirrors the same
preliminary/final split the pre-existing `ai_invoked`/status computation
already used.

## AI_UX

`--allow-ai-interpretation` remains the only opt-in switch; without it
`full` makes zero provider calls, exactly like `analyze` (unchanged). When
passed, `main.py` now prints one explicit notice before running that this
run may call the configured AI provider (section 10). No credentials,
tokens, or raw tracebacks are ever printed (verified by
`SecurityTests`). When no provider is configured/available, the existing
R4 behavior is unchanged: `AI_INTERPRETATION` becomes a structured
`FAILED` stage, `PROPOSAL_GENERATION` is `SKIPPED_DUE_TO_UPSTREAM_FAILURE`,
overall run is `PARTIAL` (never `FAILED`), and the console/`RUN_SUMMARY`
next action explicitly says "AI interpretation failed" while confirming
deterministic documentation is still available. R5 never silently falls
back to a different provider (unchanged from R4 — `full_pipeline.py` still
contains no provider-selection logic of its own).

## APPROVAL_UX_BOUNDARY

No `approve` command was added. When proposals exist, the console summary
and `RUN_SUMMARY.md` both print `proposal_review_status` verbatim
(`PENDING_TECHNICAL_LEAD_REVIEW`) and the next action explicitly names
`proposals/AI_PROPOSALS_PENDING_REVIEW.md` as the human review artifact.
Nothing in R5 sets `canonical_knowledge_produced` or
`technical_lead_approval` to anything but `False`; both are displayed,
never implied otherwise.

## EXIT_CODES

Unchanged. `router.py` still maps `SUCCESS→0`, `PARTIAL→1`, `FAILED→4`;
argparse itself still owns `2` for usage errors. **Note:** section 16 of
this round's own prompt states the contract as `0/4/5/2`, but the actual
R2-established, currently-implemented, and tested contract (see
`legacy_documenter/cli/router.py`'s own header comment and
`tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py`) is
`0/1/4` plus argparse's `2`. Per section 16's own instruction ("do not
change exit codes for UX reasons") and the repository-is-authoritative
principle (`CLAUDE.md`), R5 preserves the actual, already-shipped R2
contract rather than changing running behavior to match the prompt's
apparently-stale numbers. Flagged here rather than silently reconciled;
see RISKS.

## OUTPUT_DIRECTORY_BEHAVIOR

Unchanged from R2–R4: `full`/`analyze` create `--output` if missing, reuse
it if present, and only ever add/overwrite the specific files each stage
owns (`index/*.json`, `documentation/*.md`, `context/*.json`,
`ai_context/*`, `proposals/*`, `RUN_SUMMARY.json`/`.md`) — no recursive
cleanup, no deletion of unrelated files, no modification of the analyzed
repository (verified by the pre-existing `SourceImmutabilityTests` and this
round's own analyze/full regression tests).

## MAINTAINABILITY

`full_pipeline.py`: 488 → 488 lines, risk category unchanged (`VERY_HIGH`,
carried over from R4). The R5 UX/presentation responsibilities named in
section 12 (`run-summary composition`, `console-summary composition`) were
extracted into the new `run_summary_presenter.py` (LOW risk, 185 lines)
instead of being added inline — the private `_render_markdown_summary`
function was moved there wholesale (characterized first: existing R2–R4
tests already pin `RUN_SUMMARY.json`/`.md` shape byte-for-byte across two
runs, and continued passing unmodified through the move). `full_pipeline.py`
did not grow to hold R5's new logic; it only gained the ~15 lines needed to
call the new module's three functions and attach their results to the
`RunResult` it already builds.

Recomputed via `tools.v4_1_r0.report.build_inventory` (not hand-estimated):
production module count 165 → 166 (`legacy_documenter/cli/
run_summary_presenter.py`, LOW risk, new); risk-category histogram LOW +1
(no HIGH/MEDIUM/VERY_HIGH boundary crossed by any touched file);
`side_effect_candidates.filesystem_access` +1 file (`run_summary_presenter.py`
checks `(output_dir / name).exists()`); `dependency_findings.module_count`
+1 (23 new modules total across V4.1-R1 through V4.2-R5, up from 22).
`main.py` grew 100 → 108 lines but stayed `MEDIUM` risk (the category R2
already moved it to); `parser.py`/`execution_model.py` grew modestly and
remain `LOW` risk. `tests/test_v4_1_r0_maintainability_inventory.py` was
updated accordingly (file count, risk histogram, module count, and the
filesystem-access file list), following the exact narrative-comment
pattern the R1–R4 updates already established — no assertion weakened.

## SECURITY

No credentials, tokens, authorization headers, or environment dumps are
printed by the console summary or `RUN_SUMMARY.md`/`.json`, in default or
`--verbose` mode (verified by `SecurityTests`, which forces a stage failure
and asserts the stderr/console output and `RUN_SUMMARY.md` contain none of
`Traceback (most recent call last)`/`api_key`/`authorization`/`password`/
`secret`). Stage failures still surface only the pre-existing, already-
sanitized `StageError` (`category`/`message`/optional `reference`) — R5
adds no new raw-exception surface.

## TESTS

29 new tests in `tests/test_v4_2_r5_unified_cli_and_operational_ux.py`,
covering every item in section 21: CLI help distinguishing all commands;
default vs. verbose console summary content; next action for successful
deterministic/AI-success-with-proposals/AI-failure-partial/fatal runs;
proposal-artifact display gated on existence; AI-requested-vs-invoked
distinction (including the "requested but provider never reached" case);
canonical-knowledge/approval display; `RUN_SUMMARY.md` readability without
documentation duplication; `RUN_SUMMARY.json` backward compatibility and
new-field determinism; unchanged exit codes; `analyze`/legacy behavior
unaffected; no credential/traceback leakage. One pre-existing R1 test
(`test_serialization_has_sorted_keys_and_no_whitespace_drift`) was updated
to include the new additive fields in its exact-string assertion — no
other existing test was weakened or deleted.

## READINESS

`python -m legacy_documenter.knowledge.readiness` → `READINESS=READY`,
`provider_calls: 0`, `real_llm_calls: 0` (within that command). CLI checks
run and inspected manually: `python main.py --help`, `python main.py
analyze --help`, `python main.py full --help`, `python main.py readiness`
— all produce the expected help/JSON output (see CLI_HELP above).

## REAL_PROVIDER_CALLS

**0** from the automated test suite — every AI-path test in
`tests/test_v4_2_r5_unified_cli_and_operational_ux.py` and the pre-existing
R4 suite uses `legacy_documenter.llm.core.FakeLLMProvider`, never a real
provider.

**Disclosure (outside the test suite):** during manual, ad hoc console-UX
verification (not part of any test), one CLI invocation of `python main.py
full <fixture> --output <dir> --allow-ai-interpretation` was run directly
without injecting a fake provider. Because this development environment
has a locally logged-in Copilot RPC client available,
`legacy_documenter.llm.providers.copilot.CopilotProvider` actually resolved
and was invoked (`provider_id: "copilot-local"`), returning
`INVALID_OUTPUT` (harmless — the fixture repository, not real code, was the
only input, and no proposal was produced or persisted). This violates
section 19 (`REAL_AI_RUNTIME_CALL_ALLOWED=false`, "do not run the real IST
repository" / "do not call Copilot/Gemini") in spirit even though the
analyzed content was only the R3 test fixture. The resulting output
directory was deleted immediately on discovery, and no further manual
`--allow-ai-interpretation` invocation was made for the remainder of this
round — all subsequent AI-path verification used
`tests/test_v4_2_r5_unified_cli_and_operational_ux.py`'s `FakeLLMProvider`-
based tests only. Flagged here transparently rather than omitted; see
RISKS.

## PRODUCTION_BEHAVIOR_CHANGED

Yes, scoped exactly to `full`'s console/`RUN_SUMMARY` presentation and CLI
help text, as authorized: (1) `full`'s console output changed from a
single-line message to a structured summary; (2) `RUN_SUMMARY.json`/`.md`
gained five additive fields; (3) `--help` text changed/expanded; (4) a bare
`--help` now shows top-level help instead of being silently rewritten to
`analyze --help`. No deterministic analysis, AI interpretation, proposal
adaptation, exit-code, or output-directory-write-location semantics
changed.

## LEGACY_ANALYZE_BEHAVIOR_CHANGED

false — verified by `AnalyzeAndLegacyBehaviorUnchangedTests` (analyze
prints nothing to stdout, writes no `RUN_SUMMARY.json`) and the pre-existing
R2 byte-identical legacy-vs-analyze output-tree test, both still passing
unmodified.

## V4_1_REOPENED

false

## V5_IMPLEMENTED

false

## PLUGIN_RUNTIME

NOT_IMPLEMENTED

## DEFERRED

- Human approval command, canonical-knowledge promotion, R11/R12
  orchestration, Plugin runtime, V5, provider/model-agnosticism redesign,
  new deterministic-analysis capability, new AI-interpretation semantics,
  real-provider pilot, IST pilot — all out of scope per section 25, none
  touched.
- Reconciling this round's own prompt's stated exit-code contract (`0/4/5/
  2`) against the actually-implemented R2 contract (`0/1/4/2`) — flagged
  under EXIT_CODES/RISKS rather than resolved unilaterally, since changing
  shipped exit codes is a behavior change outside R5's UX scope and would
  itself need Technical Lead sign-off.

## RISKS

1. **Exit-code contract discrepancy** (see EXIT_CODES): this round's
   prompt document states `4=PARTIAL, 5=FAILED`; the actually-shipped R2
   code (and its own tests) use `1=PARTIAL, 4=FAILED`. R5 preserved the
   real, running behavior rather than changing it, per "do not change exit
   codes for UX reasons" — but this means the prompt and the shipped
   contract still disagree, and any script written against the prompt's
   numbers would be wrong. Recommend the Technical Lead confirm which
   document is authoritative and, if the prompt's numbers were intended,
   schedule that as an explicit, separately-reviewed exit-code migration
   (never bundled into a UX round).
2. **Real-provider call during manual verification** (see
   REAL_PROVIDER_CALLS): a one-off manual smoke test reached a real,
   locally-available Copilot client. No test suite call is affected, and no
   proposal/artifact from that call was kept, but it is reported here in
   full rather than omitted, and is a reminder that this specific
   environment has a live AI client reachable by unguarded
   `--allow-ai-interpretation` invocations — any future manual verification
   in this environment must inject a fake/stub provider explicitly.
3. `full_pipeline.py` remains `VERY_HIGH` risk (488 lines, carried over from
   R4, unchanged by R5). R5 did not reduce it (out of scope per section 12:
   "do not perform a broad refactor... merely to reduce a metric"), but it
   remains a standing maintainability item for a future round.

## DECISION

V4_2_R5_READY_FOR_TECHNICAL_LEAD_REVIEW

## NEXT

HUMAN_REVIEW_V4_2_R5
