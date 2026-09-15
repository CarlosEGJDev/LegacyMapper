# LegacyMapper V4.2-R6 — Robustness, Recovery, Security and Approval-Surface Design: Result

STATUS: COMPLETE

BASELINE: Entering test count 1723 PASS / 0 FAIL / 0 SKIP (V4.2-R5.1
closure). Exiting test count 1748 PASS / 0 FAIL / 0 SKIP (1723 pre-existing
+ 25 new R6 tests, 0 weakened/deleted).

---

## FILES_CREATED

- `legacy_documenter/utils/atomic_write.py` — `atomic_write_text(path,
  content)`: temp-sibling-file + `os.replace` crash-safe write helper
  (section 7). 44 lines, MEDIUM risk.
- `legacy_documenter/cli/artifact_lifecycle.py` —
  `reset_stale_proposal_artifacts(output)`: the narrowly-scoped stale-
  proposal cleanup used for rerun safety (sections 4/5). 60 lines, LOW
  risk.
- `docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md` — the design-only approval
  surface artifact (section 13/14). `IMPLEMENTATION_STATUS=NOT_IMPLEMENTED`.
- `tests/test_v4_2_r6_robustness_recovery_security_and_approval_surface.py`
  — 25 tests covering section 19's full list.
- `docs/V4_2/V4_2_R6_ROBUSTNESS_RECOVERY_SECURITY_AND_APPROVAL_SURFACE_RESULT.md`
  — this file.

## FILES_MODIFIED

- `legacy_documenter/cli/full_pipeline.py` (488 -> 490 lines, VERY_HIGH
  risk unchanged) — calls `reset_stale_proposal_artifacts(output)` once at
  the top of `run_full_pipeline`, before any stage runs; delegates
  RUN_SUMMARY finalization to the new
  `run_summary_presenter.finalize_and_write_run_summary` (the old private
  `_write_run_summary` was removed, offsetting the new call sites); wraps
  `_write_proposal_output` in try/except so a proposal-write failure
  becomes a structured `PROPOSAL_GENERATION` `FAILED` stage instead of an
  uncaught exception; `_write_proposal_output` itself now writes both
  files via `atomic_write_text`.
- `legacy_documenter/cli/run_summary_presenter.py` (185 -> 234 lines, LOW
  -> HIGH risk) — `compute_output_locations` changed from a filesystem-
  existence check to a stage-outcome check (section 6's fix, see
  SUMMARY_INTEGRITY); new `finalize_and_write_run_summary` builds the true
  final-state `RunResult` (including a hypothetical `FINAL_SUMMARY` row)
  in memory and only persists it atomically once, closing the R5-
  documented self-reference gap.
- `legacy_documenter/exporters/json_exporter.py` (17 -> 22 lines, risk
  unchanged LOW) — `index/*.json` now written via `atomic_write_text`
  (section 7's "core index JSON").
- `tests/test_v4_2_r5_unified_cli_and_operational_ux.py` — one test
  (`OutputLocationDiscoveryTests`) updated for `compute_output_locations`'s
  new signature/semantics; no assertion weakened, the replacement pins the
  new stage-outcome-based behavior and points at the fuller R6 test module.
- `tests/test_v4_1_r0_maintainability_inventory.py` — recomputed against
  the live tree via `tools.v4_1_r0.report.build_inventory` (see
  ORCHESTRATOR_MAINTAINABILITY); no assertion weakened, only the R6-caused
  deltas added to the existing R1–R5.1 delta narrative.

No other file was touched. `knowledge/approval`, `knowledge/proposals`,
`knowledge/canonical` were read for characterization only — none was
modified, per section 13's "design only."

## CHARACTERIZATION

Read (not inferred from prior result docs) before any change:

- **`pipeline_stages.py`**: the seven resolver/extraction functions write
  nothing to disk (pure in-memory transforms); `export_artifacts` /
  `build_context_artifacts` / `render_documentation` each write a fixed,
  hard-coded set of filenames, unconditionally overwritten in full every
  time they run — never additive, never dependent on a prior run's files.
- **`full_pipeline.py`** (pre-R6): no existence check, no cleanup, ever,
  before this round. A run into an already-used `--output` simply
  overwrote the same fixed filenames. `proposals/` was the one exception:
  it is written only when `--allow-ai-interpretation` is opted in AND AI
  interpretation returns a result, so a later run that never reaches that
  branch left an earlier run's `proposals/AI_PROPOSALS.json`/
  `AI_PROPOSALS_PENDING_REVIEW.md` completely untouched on disk.
- **`run_summary_presenter.py`** (pre-R6): `compute_output_locations` was
  `Path.exists()` on six fixed names — confirmed it could not distinguish
  "this run produced it" from "a stale artifact is still sitting there,"
  which is exactly what made a post-AI rerun's own `RUN_SUMMARY` list
  `proposals` as if current.
- **`knowledge/approval`/`knowledge/canonical`/`knowledge/proposals`**: all
  three fully implemented and unit-tested in isolation, all three
  completely unreachable from `cli/`/`orchestration/` today (confirmed via
  import search — no hit), none persists anything to disk. `ProposalStatus`
  has no `APPROVED`/`REJECTED` value; approving a proposal only ever
  creates a separate `ApprovalDecision` referencing `proposal_id` — the
  `Proposal` itself is never mutated by approval. Full detail in
  `docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md` section 1.
- **Exporters/filenames**: every filename `export_artifacts`,
  `build_context_artifacts`, `render_documentation`, and
  `_write_proposal_output` ever write is a fixed string literal or a
  code-controlled dict key from `_assemble_indexes`'s hard-coded key set —
  never derived from analyzed-repository content or AI/provider output.
  `proposal_id` is a deterministic hash (`stable_id`), never raw AI text,
  and is used only as JSON/Markdown *value* content, never as or within a
  path. Confirmed via full read of `json_exporter.py`,
  `markdown_exporter.py`, `context_builder.py`, `system_context_builder.py`,
  `technical_documentation_renderer.py`, and `full_pipeline.py`'s own
  proposal-writing code.
- **Writes were universally non-atomic**: every write in the pre-R6
  pipeline (`RUN_SUMMARY.json`/`.md`, proposal JSON/Markdown,
  `index/*.json`, documentation/context/ai_context files) used plain
  `Path.write_text(...)` directly on the final destination — confirmed by
  grep across `cli/*.py`, `context/*.py`, `exporters/*.py`; no
  `os.replace`/`tempfile` occurrence anywhere before this round.

## OUTPUT_OWNERSHIP

Narrowest safe model chosen per file/directory, evaluated per section 16:

| Location | Ownership model | Rationale |
|---|---|---|
| `index/` | Known files within directory (one `.json` per fixed `indexes` key) | `JSONExporter` only ever writes its own known key set; an unrelated file a user places there is never touched. |
| `documentation/` | Known files within directory (ten fixed `.md` names across `MarkdownExporter` + the four DOCUMENTATION-stage renderers) | Same reasoning; no wildcard/glob write. |
| `context/` | Known file (`projects.json`) | Single fixed file. |
| `ai_context/` | Known files within directory (four fixed names) | Same reasoning. |
| `proposals/` | Known files within directory (`AI_PROPOSALS.json`, `AI_PROPOSALS_PENDING_REVIEW.md` — `artifact_lifecycle.KNOWN_PROPOSAL_FILENAMES`) | The one directory this round actively resets; ownership had to be made explicit and machine-checkable (a literal tuple), not just "whatever we happen to write," precisely because it is also the one directory this round deletes from. |
| `RUN_SUMMARY.json`/`.md` | Known files (repository root of `--output`) | Two fixed files, always rewritten together by `finalize_and_write_run_summary`. |

No location is "whole directory" ownership (i.e. nothing deletes an entire
directory tree blindly) — every LegacyMapper-owned location is a known,
fixed filename set, which is what let `reset_stale_proposal_artifacts`
remove only its own two files and never risk an unrelated user file, and
is the ownership contract a future R7 real-pilot recovery path should
keep relying on rather than re-deriving.

## RERUN_SEMANTICS

Characterized and hardened (section 4), verified by
`RerunSameOutputTests`:

- **successful -> successful rerun**: unchanged, both `SUCCESS`.
- **partial -> rerun**: a forced upstream failure (`CONTEXT`) on run 1
  yields `PARTIAL`; an unforced rerun into the same `--output` recovers to
  `SUCCESS`.
- **failed -> rerun**: a forced `EXPORT` failure on run 1 yields `FAILED`;
  rerun recovers to `SUCCESS`, `index/repository.json` present.
- **AI-enabled -> deterministic rerun, same output**: the second run's own
  `RunResult` correctly reports `ai_requested=False`, `proposal_count=0`
  (see STALE_PROPOSAL_SAFETY for what happens to run 1's artifacts).
- **deterministic -> AI-enabled rerun, same output**: the second run
  correctly reports `ai_requested=True` and a positive `proposal_count`.

No run ever performs a recursive directory delete; every writer still
only overwrites its own known files in place (or, for `proposals/`, is
explicitly reset first — see below).

## STALE_PROPOSAL_SAFETY

The scenario section 5 calls "especially important," fixed with the
narrowest change that closes it (no general artifact-management
framework):

`legacy_documenter.cli.artifact_lifecycle.reset_stale_proposal_artifacts`
is called unconditionally at the very start of every `full` run, before
any stage executes. It removes only `AI_PROPOSALS.json`/
`AI_PROPOSALS_PENDING_REVIEW.md` if present, and removes the `proposals/`
directory itself only once empty (an unrelated file a user placed there
is always preserved — `proposals_dir.rmdir()` only succeeds when empty,
and the failure is swallowed).

Verified by `StaleProposalSafetyTests`:

- `full --allow-ai-interpretation` (proposals generated) followed by plain
  `full` into the same `--output`: the second run's `proposal_count` is
  `0`, `proposal_review_status` is `None`, `"proposals"` is absent from
  `output_locations`, the next action never mentions pending review, and
  — the physical files themselves are gone, not merely unreferenced, so a
  human browsing the output tree directly cannot find run A's proposals
  looking untouched.
- AI failure after a prior successful AI run: run B's own AI stage
  genuinely executes (a forced provider status is a structured failure,
  not an exception) and its proposal-write step still runs, **overwriting**
  run A's `PENDING_TECHNICAL_LEAD_REVIEW` envelope with a fresh, accurate
  `NO_PROPOSALS_GENERATED` one — the old "pending review" content is never
  left sitting there looking current.
- An unrelated user-created file under `proposals/` survives the reset
  untouched, and the directory is not removed while it is there.
- `reset_stale_proposal_artifacts` is a no-op (does not raise) when
  `proposals/` does not exist at all (the common case: a first run, or a
  run that never used AI).

## SUMMARY_INTEGRITY

Section 6's decision: **fixed**, not merely documented, via a genuinely
non-self-referential design (no engineered-around edge case):

`run_summary_presenter.finalize_and_write_run_summary` builds the
complete, true final `RunResult` **in memory first** — the run's real
stages plus one hypothetical `FINAL_SUMMARY: SUCCESS` entry, with
`next_action`/`output_locations` recomputed against that complete stage
list — and renders exactly that to `RUN_SUMMARY.json`/`.md`. This is sound
specifically because nothing is persisted unless the atomic write actually
succeeds: if it raises, the function returns a `FAILED` `FINAL_SUMMARY`
stage result instead, and the "SUCCESS" content that only ever existed in
memory is never written — the previous run's last complete summary (if
any) is left exactly as it was. `RUN_SUMMARY.json` now always contains its
own `FINAL_SUMMARY` row when the write succeeds (verified by
`SummaryIntegrityTests.test_persisted_summary_includes_its_own_final_summary_stage`),
closing the exact gap R5 documented and disclosed.

This same fix is what let `compute_output_locations` stop being a
filesystem-existence check (see STALE_PROPOSAL_SAFETY/CHARACTERIZATION):
it now derives every location from which stage(s) succeeded in the
`RunResult` being rendered, so the persisted file, the returned value, and
the console summary all describe the same true current-run state, never a
filesystem artifact left over from a different run.

## ATOMIC_WRITE_DECISION

Applied `atomic_write_text` (temp sibling + `os.replace`, standard library
only, `legacy_documenter/utils/atomic_write.py`) to exactly the three
categories section 7 named as the minimum: `RUN_SUMMARY.json`/`.md`,
`proposals/AI_PROPOSALS.json`/`AI_PROPOSALS_PENDING_REVIEW.md`, and
`index/*.json`. Deliberately **not** applied to `documentation/`,
`context/`, or `ai_context/` writes — those are not "authoritative
machine-readable artifacts" in the same sense (documentation is human-
oriented Markdown; the DOCUMENTATION stage already has its own per-
renderer failure containment), and section 7 explicitly says "apply only
where it materially improves recovery/integrity... do not introduce
transactional infrastructure." No general transactional-write framework
was introduced — one ~40-line function, three call sites.

Verified by `AtomicWriteTests`: a successful write leaves no temp file
behind; a write whose `os.replace` step fails removes its own temp file
and leaves the original destination completely untouched (never raises
past that point without cleaning up, and never partially writes).

## FAILURE_CONTAINMENT

Re-characterized and one real gap closed:

- SCAN/EXTRACTION/resolver/EXPORT/CONTEXT/DOCUMENTATION/AI_INTERPRETATION
  failure containment was already correct (R2–R4) and remains so —
  verified again by `FilesystemFailureContainmentTests
  .test_dependent_stages_skip_rather_than_crash_on_upstream_failure`
  (a `CALL_RESOLUTION` failure correctly cascades `SKIPPED_DUE_TO_
  UPSTREAM_FAILURE` to `WEB_ENTRY_RESOLUTION`/`FLOW_RESOLUTION` while
  `DATABASE_RESOLUTION`/`DEPENDENCY_RESOLUTION` continue independently, and
  `FINAL_SUMMARY` still runs).
- **New gap closed**: `_write_proposal_output`'s call site was not wrapped
  in any failure boundary before this round — a filesystem error there
  (already possible pre-R6, just never exercised by a test) would have
  propagated all the way out of `run_full_pipeline` as a raw, uncaught
  exception, violating "no raw traceback as the normal CLI contract"
  (section 9) and "do not hide failures" (section 8) by crashing instead
  of reporting. It is now wrapped: a write failure downgrades the
  already-appended `PROPOSAL_GENERATION` stage result in place to
  `FAILED` with a structured `StageError`, resets `proposals` to empty
  (so `proposal_count`/`proposal_review_status` never claim something was
  written when it was not), and the run continues to `FINAL_SUMMARY`
  normally — overall status becomes `PARTIAL`, never a crash, never a
  silently-swallowed `SUCCESS`. Verified by
  `ProposalWriteFailureTests.test_proposal_write_failure_is_structured_not_a_crash`.
- `FINAL_SUMMARY` itself was already contained (R2); still is, now via
  `finalize_and_write_run_summary`'s own try/except, verified by
  `SummaryIntegrityTests.test_summary_write_failure_is_structured_not_a_crash`.

## FILESYSTEM_FAILURES

Representative controlled tests added (section 9), all via mocks rather
than depending on real OS permission behavior:

- `test_unwritable_output_directory_is_a_structured_failure_not_a_traceback`
  — `JSONExporter.export` raising `PermissionError` surfaces as a
  structured `EXPORT` `FAILED` stage; overall run correctly `FAILED`
  (EXPORT is required for minimal usefulness).
- `test_summary_write_failure_is_structured_not_a_crash` /
  `test_summary_write_failure_never_leaves_a_lying_success_file` —
  `atomic_write_text` raising during summary finalization: structured
  `FINAL_SUMMARY` `FAILED`, overall `PARTIAL`, and a prior good
  `RUN_SUMMARY.json` is never overwritten with fabricated success content.
- `test_proposal_write_failure_is_structured_not_a_crash` — see
  FAILURE_CONTAINMENT above.
- `test_atomic_write_failure_cleans_up_temp_file_and_preserves_original` —
  `os.replace` raising: no temp file left behind, original file byte-for-
  byte unchanged.

No test depends on actually setting real OS file permissions (Windows
permission semantics differ from POSIX and are not reliably testable
across environments) — every failure is characterized via a mock/fake,
per section 9's explicit suggestion.

## SOURCE_IMMUTABILITY

Re-verified, not merely assumed:
`SourceImmutabilityTests.test_fixture_untouched_across_rerun_partial_and_stale_proposal_cleanup`
hashes every fixture file's bytes before and after a sequence that
includes an AI-enabled run, a forced `CONTEXT` failure, and a plain
rerun — byte-identical. A second, more targeted test,
`test_reset_stale_proposal_artifacts_never_touches_the_source_repository`,
proves the new cleanup function specifically cannot reach the analyzed
repository even if misused (passing the fixture root itself finds no
`proposals/` directory there to touch, by construction — the function
only ever descends into `<output>/proposals`, never anywhere derived from
`repo_root`). No recovery/cleanup logic added this round accepts or
derives a path from `repo_root` at all.

## PATH_SAFETY

Reviewed all R2–R5 output paths (section 11); conclusion: **already
closed constants, not something requiring new validation code** — a
narrower fix (or no fix) was correct here rather than adding path-
resolution guards nothing currently threatens. Every filename any writer
produces is either a Python string literal or a dict key from a fixed,
code-controlled key set (`_assemble_indexes`); the one AI-influenced value
in the whole pipeline, `Proposal.statement` (raw AI text) and
`evidence_refs`, is used only as JSON/Markdown *value* content, never as
or within a path — the two proposal filenames themselves
(`AI_PROPOSALS.json`, `AI_PROPOSALS_PENDING_REVIEW.md`) are literal string
constants unconditionally, regardless of what the AI returned.

Verified directly (not just characterized) by
`PathSafetyTests.test_proposal_filenames_are_fixed_regardless_of_ai_statement_content`:
an AI response whose `statement` contains a `../../escape/attempt/../../etc/passwd`-shaped
string still produces exactly the two fixed proposal filenames, with the
traversal-shaped text present only as JSON value content, never
interpreted as a path segment. `test_output_never_written_outside_the_
selected_output_directory` additionally confirms every file an AI-enabled
run writes lands under the caller's own `--output` path and nowhere else.

## SECURITY

Re-verified every item in section 12:

- No secrets/tokens/API keys in `RUN_SUMMARY`/proposal output (existing
  R5 `SecurityTests` still pass unmodified; this round adds no new secret
  surface).
- No environment dumps: `atomic_write_text`/`reset_stale_proposal_
  artifacts` touch no environment state.
- Provider errors sanitized: unchanged (`_sanitize_provider_error`, R4).
- No raw traceback as normal CLI contract: reconfirmed for the two new
  failure paths this round added containment for (proposal write,
  summary write) via `FilesystemFailureContainmentTests`/
  `ProposalWriteFailureTests`/`SummaryIntegrityTests` — every induced
  failure surfaces as a structured `StageError`, never a bare exception
  reaching the caller.
- No source modification: SOURCE_IMMUTABILITY above.
- No AI-controlled output paths: PATH_SAFETY above.
- No automatic approval, no canonical promotion: verified by
  `ApprovalAndCanonicalBoundaryTests` — `technical_lead_approval`/
  `canonical_knowledge_produced` stay `False`, and no `approvals/`/
  `canonical/` directory is ever created by `full`.
- **The R5.1 test-suite-wide provider guard remains effective**: this
  round's own `RealProviderGuardTests` (R5.1) still pass unmodified in
  the full regression run; every new AI-path test in this round's own
  module uses `FakeLLMProvider` exclusively, and `tests/__init__.py`'s
  guard was not touched.

## APPROVAL_SURFACE_DESIGN

`docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md`,
`IMPLEMENTATION_STATUS=NOT_IMPLEMENTED`. Grounded in the actual existing
`knowledge/approval`/`knowledge/canonical`/`knowledge/proposals` domain
model (not invented from scratch): documents what the Technical Lead must
review per proposal, the three possible decisions
(`APPROVED`/`REJECTED`/`CORRECTION_REQUESTED` — the existing, closed
`ApprovalDecisionType`), how a decision binds to an exact `proposal_id`,
how corrected/rejected proposals should behave
(`supersedes_proposal_id`, never an in-place edit), what data
`CanonicalCompositionService.compose` already requires before promotion,
and preserves every explicit constraint from section 13 (Technical Lead =
sole authority, AI cannot approve, approval provenance separate from
source provenance — already true structurally today, no enterprise RBAC).
It names one concrete, currently-missing prerequisite for a future round
(a deterministic `run_id` so an approval surface can refuse to act on a
proposal from a superseded run) rather than glossing over it. No CLI
command was added; no fake/nonfunctional command is exposed anywhere.

## ORCHESTRATOR_MAINTAINABILITY

Recomputed via `tools.v4_1_r0.report.build_inventory` (not hand-
estimated):

- `full_pipeline.py`: **488 -> 490 lines, VERY_HIGH risk unchanged.**
  Despite touching failure/recovery/summary orchestration throughout this
  round (stale-proposal reset call, proposal-write failure containment,
  delegating summary finalization), net growth is 2 lines — the
  `_write_run_summary` function (17 lines) was removed entirely in favor
  of one call to the new `finalize_and_write_run_summary`.
- **Responsibilities extracted** (section 15's suggested list, both
  taken): "summary finalization" moved to
  `run_summary_presenter.finalize_and_write_run_summary` (which absorbed
  the growth: 185 -> 234 lines, crossing LOW -> HIGH risk — the deliberate
  trade-off that kept `full_pipeline.py` flat); "artifact lifecycle" moved
  to the new `legacy_documenter/cli/artifact_lifecycle.py` (60 lines, LOW
  risk) rather than being inlined. "Proposal output lifecycle" (the third
  suggested candidate) was *not* separately extracted — `_write_proposal_
  output`/`_proposal_to_dict`/`_render_proposal_markdown` remain in
  `full_pipeline.py` unchanged in structure (only their write calls now go
  through `atomic_write_text`); extracting them was not required by
  anything this round actually touched (the round's proposal-lifecycle
  work was the *reset*, already its own module, and the *failure
  containment*, a two-line try/except at the existing call site) --
  extracting further would have been refactoring for a metric, which
  section 15 explicitly forbids.
- No refactor was made to any code path this round did not otherwise
  touch; `run_full_pipeline` remains a straight-line orchestration
  sequence, not a framework.

## TESTS

25 new tests in
`tests/test_v4_2_r6_robustness_recovery_security_and_approval_surface.py`,
covering every item in section 19: successful/partial/failed rerun
recovery; AI<->non-AI rerun in both directions; stale-proposal safety
(both scenarios named in section 5) plus unknown-user-file preservation;
source immutability (fixture hash + a targeted cleanup-scope test);
summary integrity (both the new `FINAL_SUMMARY` self-reference fix and
write-failure containment); proposal-write-failure containment; a
representative filesystem failure (unwritable output via mock); path
traversal impossibility through AI-controlled statement content;
approval/canonical boundary (still `False`/absent); exit codes (0/1/2/4)
and legacy/analyze unchanged. One pre-existing R5 test
(`OutputLocationDiscoveryTests`) was updated for the new
`compute_output_locations` signature — not weakened, its replacement pins
the new, stricter stage-outcome-based behavior. No other existing test was
weakened or deleted. Full suite: 1748/1748 passing.

## READINESS

`python -m legacy_documenter.knowledge.readiness` → `READINESS=READY`,
`provider_calls: 0`, `real_llm_calls: 0`. CLI checks run and confirmed:
`python main.py --help`, `python main.py full --help`,
`python main.py readiness` — all exit `0`.

## REAL_PROVIDER_CALLS

0. Every AI-path test in this round's new module, and every pre-existing
AI-path test in the full suite, uses `FakeLLMProvider` exclusively. No
manual verification outside the automated test suite was performed this
round (unlike R5, no ad hoc CLI invocation of
`full --allow-ai-interpretation` was run) — the lesson from R5's
disclosure and R5.1's new `AGENTS.md` rule was followed throughout.

## EXIT_CODE_CONTRACT

SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4

Unchanged (not touched by this round at all); reconfirmed passing via the
pre-existing R5.1 `ExitCodeContractTests` and this round's own
`ExitCodeAndLegacyUnchangedTests.test_exit_codes_remain_0_1_2_4` in the
full regression run.

## PRODUCTION_BEHAVIOR_CHANGED

Yes, scoped exactly to `full`'s recovery/integrity/summary behavior, as
authorized: (1) a stale `proposals/` pair from an earlier run is now
removed at the start of every `full` run; (2) `RUN_SUMMARY.json`/`.md`'s
`output_locations` now reflect this run's actual stage outcomes instead
of filesystem existence, and the persisted file now includes its own
`FINAL_SUMMARY` row; (3) `RUN_SUMMARY.json`/`.md`, the proposal JSON/
Markdown pair, and `index/*.json` are now written atomically; (4) a
proposal-write failure is now contained as a structured stage failure
instead of an uncaught exception. No deterministic analysis, AI
interpretation semantics, exit-code mapping, or CLI argument contract
changed.

## LEGACY_ANALYZE_BEHAVIOR_CHANGED

false — `analyze`/legacy invocation paths were not touched; reconfirmed by
this round's own `test_analyze_and_legacy_behavior_unchanged` and the
pre-existing R2 byte-identical legacy-vs-analyze test, both passing
unmodified. (`json_exporter.py`'s atomic-write change affects `analyze`
too, but only *how* `index/*.json` is written, never its content or
behavior on success — confirmed by the unchanged `indexes["errors"] == []`
assertion and the pre-existing byte-identical output-tree test still
passing.)

## V4_1_REOPENED

false

## V5_IMPLEMENTED

false

## PLUGIN_RUNTIME

NOT_IMPLEMENTED

## DEFERRED

- The actual approval CLI surface, any on-disk persistence for
  `ApprovalDecision`/`CanonicalKnowledgeEntry`, and the `run_id` field
  named as a prerequisite in `V4_2_APPROVAL_SURFACE_DESIGN.md` section 6 —
  all explicitly design-only this round (section 13/22).
- Extracting `_write_proposal_output`/`_proposal_to_dict`/
  `_render_proposal_markdown` into their own module — not required by
  anything this round touched; see ORCHESTRATOR_MAINTAINABILITY.
- Approval command, canonical promotion, R11/R12 orchestration, Plugin
  runtime, V5, language/framework/database/provider/model agnosticism
  redesign, real-provider pilot, IST pilot — all out of scope per section
  22, none touched.

## RISKS

1. One test run of the full new R6 module produced a single, non-
   reproducible failure (`test_deterministic_run_then_ai_enabled_rerun_
   same_output`, expecting `SUCCESS` but observing `PARTIAL`) that could
   not be reproduced across 5 subsequent full-module runs, the same test
   in isolation, or any bisected subset of classes run before it. No
   shared/global mutable state was found in the code path involved
   (`ProposalService`, `stable_id`, `ContextResolver` are all
   per-call-fresh). Most likely a one-off Windows temporary-directory
   cleanup timing artifact under this environment's load, not a
   deterministic logic defect — flagged here transparently rather than
   silently dismissed. If this recurs in a future round's regression run,
   it warrants a dedicated investigation before being dismissed again.
2. `run_summary_presenter.py` crossed from LOW to HIGH risk (185 -> 234
   lines) as the direct consequence of taking on the summary-finalization
   responsibility extracted out of `full_pipeline.py`. This is the
   intended trade-off (section 15 prioritizes keeping `run_full_pipeline`
   itself readable over minimizing every individual file's score), not an
   overlooked regression, but it is now the fourth-largest risk
   contributor in the `cli/` package and a candidate for its own review in
   a future maintainability-focused round.
3. The approval-surface design (section 13/14) is necessarily speculative
   where it touches a not-yet-built `run_id` mechanism (section 6 of the
   design doc) — a future round implementing it may find the exact
   mechanism needs adjustment once real persistence is designed.

## DECISION

V4_2_R6_READY_FOR_TECHNICAL_LEAD_REVIEW

## NEXT

HUMAN_REVIEW_V4_2_R6
