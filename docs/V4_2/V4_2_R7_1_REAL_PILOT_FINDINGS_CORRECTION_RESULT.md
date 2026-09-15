# LegacyMapper V4.2-R7.1 — Real Pilot Findings Correction: Result

## STATUS

COMPLETE — F-01 through F-04 corrected; F-05 deferred by an existing
determinism contract; F-06/F-07 preserved as observations, unchanged.

## BASELINE

Entering test count 1763 PASS / 0 FAIL / 0 SKIP (V4.2-R7 closure). Exiting
test count 1777 PASS / 0 FAIL / 0 SKIP (1763 pre-existing + 14 new: 13 in
the new `tests/test_v4_2_r7_1_real_pilot_findings_correction.py`, plus 1 new
test method and additive assertions on 2 existing test methods in
`tests/test_v4_2_r7_synthetic_full_fixture.py`). 0 previously-passing test
was weakened or deleted.

## FILES_CREATED

- `tests/test_v4_2_r7_1_real_pilot_findings_correction.py` — 13 new tests:
  section 3 characterization (scenarios A–E) directly against
  `FunctionalFlowResolver`, F-01 machine/human-representation tests, and
  focused F-02/F-03/F-04 tests.
- `docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md`
- `docs/V4_2/V4_2_R7_1_REAL_PILOT_FINDINGS_CORRECTION_RESULT.md` (this file)

## FILES_MODIFIED

- `legacy_documenter/analysis/flow_resolver.py` — F-01: added two additive,
  independently-computed per-flow fields (`has_confirmed_terminal`,
  `has_unresolved_boundary`); the pre-existing `status`/`confidence`
  aggregation logic is completely unchanged.
- `legacy_documenter/analysis/_flow_report_composition.py` — F-01: added
  three additive aggregate counters to the flow-resolution summary
  (`flows_with_confirmed_terminal`, `flows_with_unresolved_boundary`,
  `flows_with_both`).
- `legacy_documenter/exporters/technical_documentation_renderer.py` — F-01:
  `FUNCTIONAL_FLOWS.md` now renders the two new per-flow facts alongside
  `Status`/`Confidence`, plus a short explanatory paragraph.
- `legacy_documenter/exporters/markdown_exporter.py` — F-02
  (`solution_structure` now shows each solution's own path, disambiguating
  duplicate names), F-03 (`webforms_map` renders `register` metadata as
  sorted Markdown sub-bullets instead of raw Python `dict` repr, excluding
  the internal `_normalized` field), F-04 (`project_overview` shows a safe
  repository display label via the new `_repository_display_label` helper
  instead of the analyst's absolute local path).
- `tests/test_v4_2_r7_synthetic_full_fixture.py` — added
  `test_bl_to_database_flow_status_still_downgrades_but_now_says_so_explicitly`
  (the F-01 correction, exercised against the real pipeline output) and
  additive `has_confirmed_terminal`/`has_unresolved_boundary` assertions on
  `test_unresolved_finding_remains_explicit_not_guessed` (`btnNotify_Click`,
  which correctly reports `has_confirmed_terminal: false`, distinguishing it
  from the corrected `btnSave_Click` case). No existing assertion's expected
  value was changed; only new assertions were added, per section 12 ("update
  only the F-01 assertion whose expected behavior is intentionally
  corrected") — the F-01-relevant assertion did not previously check
  `status`/`confidence` at all, so nothing pre-existing needed to change,
  and F-07's own dedicated test in this file is untouched.
- `tests/test_v4_1_r0_maintainability_inventory.py` — reconciled the
  V4.1-R0 frozen historical AST-scan comparison test with this round's
  legitimate line-count growth in `markdown_exporter.py`,
  `flow_resolver.py`, and `technical_documentation_renderer.py`
  (`FunctionalFlowResolver.resolve` re-enters the `largest_functions`/
  `largest_classes` top-N lists it had dropped out of at R3;
  `TechnicalDocumentationRenderer.functional_flows` newly enters the
  `largest_functions` top-N list, displacing two untouched functions below
  the cutoff — the same ranking-membership mechanism already documented for
  R3's renderer additions). No test assertion was weakened: every
  comparison still requires exact equality once the known, explained
  line-count deltas are normalized, exactly as the R3/R6 precedents in this
  same file already do for other files this round did not touch.

## F01_STATUS

FIXED

## F01_ROOT_CAUSE

`FunctionalFlowResolver.resolve()`'s `flow_confidence`/`_flow_status`
aggregate **every** path discovered from a flow's entry point to a single
worst-case value: `flow_confidence` is `"unresolved"` if any path is not
`"confirmed"`, and `status` picks the first matching terminal type in a
fixed precedence order where `unresolved_boundary` outranks
`data_endpoint`. A method reached along the flow's confirmed
database-terminal path can itself make an unrelated call that is
unresolved (in the synthetic fixture: `CustomerRepository.Save`'s
`cmd.ExecuteNonQuery()`), producing a second, independent
`unresolved_boundary` path in the same flow that then outranks the
confirmed `data_endpoint` path in `_flow_status`'s precedence order — even
though the confirmed database terminal was, in fact, fully reached.

## F01_OLD_SEMANTICS

See `docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md` F-01 DETAIL ->
OLD_SEMANTICS.

## F01_NEW_SEMANTICS

See `docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md` F-01 DETAIL ->
NEW_SEMANTICS.

## F01_COMPATIBILITY

100% additive. No status/confidence enum value was added, removed, or
reinterpreted; no schema/enum change was made or required, so no STOP was
raised per section 4. Every existing consumer reading only the pre-existing
fields observes byte-identical behavior to before this round.

## F02_STATUS

FIXED

## F03_STATUS

FIXED

## F04_STATUS

FIXED

## F05_STATUS

DEFERRED_BY_DETERMINISM_CONTRACT — see
`docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md` SECTION 9 — F-05 REASONING
for the exact existing test/contract this would have broken.

## F06_STATUS

PRESERVED_OBSERVATION

## F07_STATUS

PRESERVED_OBSERVATION

## DOCUMENTATION_SCALE_STATUS

Unresolved, out of scope for this round per section 10 (no pagination,
HTML site, search engine, database, or web UI was implemented); recorded
for a future documentation-navigation round. F-01's own required
documentation correction added a fixed, short explanatory paragraph plus
two short per-flow fields — a negligible size increase relative to
`FUNCTIONAL_FLOWS.md`'s total scale, and directly required by F-01 itself
rather than an unrelated addition.

## SYNTHETIC_FIXTURE

`tests/fixtures/v4_2_r7_full_sample/` — unchanged (byte-identical; no
IST-derived name or data was added, per section 12/13). Only the assertions
in its dedicated test file were extended.

## SYNTHETIC_FIXTURE_RESULT

See `docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md` F-01 DETAIL ->
SYNTHETIC_FIXTURE_RESULT.

## TESTS

1777_PASS_0_FAIL_0_SKIP (`python -m unittest discover -s tests`).

## READINESS

READY (`provider_calls: 0`, `real_llm_calls: 0`) — confirmed via
`python -m legacy_documenter.knowledge.readiness` after this round's
changes.

## REAL_PROVIDER_CALLS

0

## REAL_IST_ACCESSED

false — no test or manual command in this round reads
`C:\Users\cgalianj\source\IST_40\operacional`; all evidence is the
committed synthetic fixture and direct unit-level characterization.

## EXIT_CODE_CONTRACT

SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4 (unchanged; not touched by this round).

## TECHNICAL_LEAD_APPROVAL

false

## CANONICAL_KNOWLEDGE_PRODUCED

false

## PRODUCTION_BEHAVIOR_CHANGED

true — `index/functional_flows.json` and `index/flow_summary.json` gain
additive fields (see FILES_MODIFIED); `documentation/FUNCTIONAL_FLOWS.md`,
`documentation/SOLUTION_STRUCTURE.md`, `documentation/WEBFORMS_MAP.md`, and
`documentation/PROJECT_OVERVIEW.md` render differently (additively, or with
a corrected/safer display value). No pre-existing field, file, or behavior
was removed; no exit code, stage outcome, or CLI contract changed.

## LEGACY_ANALYZE_BEHAVIOR_CHANGED

false — `analyze`/legacy paths are unaffected beyond the same additive
`documentation`/`index` rendering changes described above (`analyze` calls
the same underlying resolver/exporters as `full`); no test asserting
`analyze`'s own exit-code/error/index-shape contract was changed, and all
such pre-existing tests still pass unmodified.

## V4_1_REOPENED

false

## V5_IMPLEMENTED

false

## PLUGIN_RUNTIME

NOT_IMPLEMENTED

## DEFERRED

F-05 (`DEFERRED_BY_DETERMINISM_CONTRACT`); the documentation-scale problem
(section 10, unchanged from R7); F-06/F-07 (`PRESERVED_OBSERVATION`, as
instructed).

## RISKS

None newly introduced. The additive fields/counters slightly grow
`index/functional_flows.json`, `index/flow_summary.json`, and
`documentation/FUNCTIONAL_FLOWS.md`; this is bounded (two short fields per
flow, three counters total) and was required by F-01 itself.

## DECISION

V4_2_R7_1_READY_FOR_TECHNICAL_LEAD_REVIEW

## NEXT

HUMAN_REVIEW_V4_2_R7_1
