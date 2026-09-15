# LegacyMapper V4.2-R7 — Real IST Pilot and Committable Fixture: Result

STATUS: COMPLETE (evaluation round; a defect was found and preserved, not repaired)

## BASELINE

Entering test count 1748 PASS / 0 FAIL / 0 SKIP (V4.2-R6 closure).
Exiting test count 1763 PASS / 0 FAIL / 0 SKIP (1748 pre-existing + 15 new
R7 fixture tests, 0 weakened/deleted). No production module changed
(`PRODUCTION_CODE_CHANGE_ALLOWED=false` throughout).

## SELECTED_REAL_SOURCE

`C:\Users\cgalianj\source\IST_40\operacional`

## SOURCE_SELECTION

Both historically-mentioned paths exist on this machine
(`C:\Users\cgalianj\source\IST_40\operacional` and
`C:\inetpub\wwwroot\2010\IST\operacional`). Per section 3's instruction to
compare only enough read-only metadata to identify the intended source
according to current repository configuration, `AGENTS.md`'s "Legacy
Source Repository" section was checked: it names exactly one path as
"Current legacy repository" —
`C:\Users\cgalianj\source\IST_40\operacional` — with no second path
mentioned anywhere in that document, `CLAUDE.md`, or `PROJECT_STATE.json`.
This is not a case of two candidate documents disagreeing (which would
have required `DECISION=V4_2_R7_BLOCKED_SOURCE_SELECTION`); it is one
authoritative configuration document naming one path unambiguously, so
the pilot proceeded against it. Both locations were left completely
untouched — only the selected path was ever read.

## PRE_PILOT_TESTS

`python -m unittest discover -s tests`, run once, before the pilot:
1748 PASS / 0 FAIL / 0 SKIP.

## INTERMITTENT_R6_TEST_RECURRENCE

false — the disclosed non-reproducible R6 observation
(`test_deterministic_run_then_ai_enabled_rerun_same_output`) did not
recur in the pre-pilot run, and no other unexplained regression occurred.
The real pilot proceeded per section 7's decision rule.

## REAL_PILOT_COMMAND

```
python main.py full "C:\Users\cgalianj\source\IST_40\operacional" --output "output/v4_2_r7_ist_operacional" --verbose
```

`--allow-ai-interpretation` was never passed.

## REAL_PILOT_EXECUTIONS

1 (one primary, authoritative execution; no second run against the real
repository was performed — R6 rerun/recovery semantics against IST were
not separately re-tested here, since section 6 only permits a second run
"if explicitly required," and nothing about this pilot required it; R6's
own rerun/recovery guarantees are already covered by dedicated fixture
tests).

## REAL_PILOT_EXIT_CODE

0

## REAL_PILOT_STATUS

SUCCESS — all ten deterministic stages succeeded;
`AI_INTERPRETATION`/`PROPOSAL_GENERATION` correctly `NOT_RUN`.

## REAL_PILOT_DURATION

~9 minutes wall-clock (12:09:53 → 12:19:02, CLI invocation start to
finish). `index/repository.json`'s own `duration_seconds: 474.044`
(≈7.9 minutes) covers only the SCAN-through-EXTRACTION portion timed
internally by the pipeline — no single field in `RUN_SUMMARY.json`
reports the full run's duration; see
`docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md` FINDINGS F-05.

## SOURCE_IMMUTABILITY

Verified both before and after the pilot: `git status --short` inside
the (git-tracked) legacy repository produced byte-identical output;
representative file hashes (`Web.config`, three `.vbproj` files) were
identical; file count (18,455) and directory count (2,502) were
unchanged; `HEAD` (`4ba871924cf1fd04b510be35d1d3c3f4d4d9d472`) was
unchanged. No LegacyMapper write of any kind reached the source tree.

## REAL_DOCUMENTATION_ASSESSMENT

The deterministic pipeline is factually trustworthy at the level of
individual claims (six representative samples, all SUPPORTED or
PARTIALLY_SUPPORTED, none UNSUPPORTED), but three of eleven human-facing
documents (`FUNCTIONAL_FLOWS.md` 44MB/396K lines,
`UNRESOLVED_FINDINGS.md` 12.8MB/163K lines, `DATABASE_ACCESS.md`
5.2MB/32.5K lines) are not practically usable by a human as delivered,
and one HIGH-severity defect (a flow's own top-level `status`/
`confidence` can read "unresolved" even when it demonstrably reached a
real, confirmed database terminal — affecting 18.7% of all 12,642 real
flows) materially understates the tool's actual capability. Full
detail, all findings, and the six representative samples are in the
dedicated review document.

## REAL_DOCUMENTATION_REVIEW_PATH

`docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md`

## SYNTHETIC_FIXTURE

`tests/fixtures/v4_2_r7_full_sample/` — entirely synthetic (`SampleLegacy`/
`CustomerPage`/`CustomerService`/`CustomerRepository`), one solution,
three projects, one WebForm, a resolved UI→BL→repository→Oracle
stored-procedure chain, and one deliberately unresolvable external call.
Validated by 15 focused semantic-assertion tests
(`tests/test_v4_2_r7_synthetic_full_fixture.py`), all passing. The fixture
also deterministically reproduces two of the pilot's own findings in
miniature (F-01 and F-07 — see FINDINGS_SUMMARY), giving the Technical
Lead a minimal, committable, always-reproducible example of each without
any IST-derived data.

## SYNTHETIC_FIXTURE_VALIDATION_PATH

`docs/V4_2/V4_2_R7_SYNTHETIC_FIXTURE_VALIDATION.md`

## FILES_CREATED

- `tests/fixtures/v4_2_r7_full_sample/` — `SampleLegacy.sln`,
  `Web/Web.vbproj`, `Web/CustomerPage.aspx`, `Web/CustomerPage.aspx.vb`,
  `Bl/CustomerService.vbproj`, `Bl/CustomerService.vb`,
  `Sys/CustomerRepository.vbproj`, `Sys/CustomerRepository.vb`.
- `tests/test_v4_2_r7_synthetic_full_fixture.py` — 15 new tests.
- `docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md`
- `docs/V4_2/V4_2_R7_SYNTHETIC_FIXTURE_VALIDATION.md`
- `docs/V4_2/V4_2_R7_REAL_IST_PILOT_AND_COMMITTABLE_FIXTURE_RESULT.md` (this file)
- `output/v4_2_r7_ist_operacional/` — the real pilot's generated output.
  **Local/generated evidence only, not staged/committed** (per section 5;
  this round does not commit at all — `COMMIT_ALLOWED=false`).

## FILES_MODIFIED

None. No production module (`legacy_documenter/**`) and no pre-existing
test file was changed — confirmed by `git status --short` showing only
new, untracked paths.

## FINDINGS_SUMMARY

7 findings: 0 BLOCKER, 1 HIGH, 2 MEDIUM, 2 LOW, 2 OBSERVATION. Full detail
(evidence, affected stage, expected vs. observed behavior, recommended
future action) in `docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md`
FINDINGS.

## BLOCKERS

None.

## HIGH_FINDINGS

- **F-01**: 2,370 of 12,642 real functional flows (18.7%) reach a real,
  `confidence: "confirmed"` database/stored-procedure terminal operation
  (visible in the flow's own `terminal_operations` field and a fully
  confirmed edge chain) yet the flow's own top-level `status`/
  `confidence` still reports `unresolved_boundary`/`unresolved` —
  apparently because any single unrelated unresolved call elsewhere in
  the same handler method downgrades the whole flow's reported outcome,
  even when the actual DB-reaching path resolved completely. This
  materially understates the tool's real capability behind
  `flow_summary.json`'s headline `unresolved_boundaries: 162914` metric,
  and is deterministically reproduced by the synthetic fixture's own
  `btnSave_Click` flow (see
  `tests/test_v4_2_r7_synthetic_full_fixture.py
  ::FunctionalFlowTests::test_bl_to_database_flow_reaches_the_real_stored_procedure`).

## MEDIUM_FINDINGS

- **F-02**: `SOLUTION_STRUCTURE.md` has 24 of 113 solution headers
  (21%) that are exact-name duplicates with no distinguishing path shown,
  making duplicate-named solutions (e.g. a `Backup/` copy) indistinguishable
  to a reader.
- **F-03**: `WEBFORMS_MAP.md` renders WebForm `register` metadata as raw
  Python `dict` repr text instead of Markdown, a presentation defect.

## LOW_FINDINGS

- **F-04**: `PROJECT_OVERVIEW.md`/`index/repository.json` embed the
  analyst's absolute local filesystem path (revealing the local Windows
  username) — unnecessary environment-specific information in
  human-facing output.
- **F-05**: no single field in `RUN_SUMMARY.json` reports the full run's
  wall-clock duration (only a partial, internally-timed
  `duration_seconds` covering SCAN-through-EXTRACTION).

## OBSERVATIONS

- **F-06**: `UNRESOLVED_FINDINGS.md`'s "Unresolved Flow Boundaries" table
  is diluted by repeated, low-value designer-boilerplate rows
  (`InitializeComponent()`).
- **F-07**: `WebEntryResolver` never attaches `outgoing_calls` to an
  ASPX-markup-bound (`OnClick="..."`) entry point (it looks the call
  graph up under the wrong file path) — real but narrow impact: only 40
  of 12,662 real entry points (0.3%) use markup binding; the dominant
  code-behind `Handles`-clause pattern is unaffected. Also deterministically
  reproduced by the synthetic fixture.

## FINAL_TESTS

1763_PASS_0_FAIL_0_SKIP (`python -m unittest discover -s tests`, run
after adding the R7 fixture/tests). No previously-passing test was
weakened or deleted; the intermittent R6 symptom did not recur in this
run either.

## READINESS

READY (`provider_calls: 0`, `real_llm_calls: 0`), recorded both
pre-pilot and post-fixture — unchanged throughout this round.

## REAL_PROVIDER_CALLS

0. `--allow-ai-interpretation` was never passed against the real IST
repository or anywhere in the synthetic fixture's tests; no manual
real-provider verification was performed.

## TECHNICAL_LEAD_APPROVAL

false

## CANONICAL_KNOWLEDGE_PRODUCED

false

## PRODUCTION_CODE_CHANGED

false — confirmed by `git status --short`: only new fixture/test/doc/
prompt files and the local-only pilot output directory appear; no file
under `legacy_documenter/` was touched. Per section 16, every defect
found (F-01 through F-07) was recorded, classified, and evidenced, never
repaired, during this round.

## LEGACY_ANALYZE_BEHAVIOR_CHANGED

false — `analyze`/legacy paths were not touched; the synthetic fixture's
own `test_legacy_analyze_path_also_succeeds_on_the_fixture` and the full
suite's pre-existing legacy-behavior tests all pass unmodified.

## V4_1_REOPENED

false

## V5_IMPLEMENTED

false

## PLUGIN_RUNTIME

NOT_IMPLEMENTED

## DECISION

V4_2_R7_REQUIRES_CORRECTION

## NEXT

V4.2-R7.1
