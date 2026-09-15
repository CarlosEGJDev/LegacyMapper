# LegacyMapper V4.2-R7.1 — Real Pilot Findings Verification

Verifies the correction of the seven findings the V4.2-R7 real IST pilot
recorded (`docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md` FINDINGS).
This round does not rerun the real IST repository
(`REAL_LEGACY_REPOSITORY_READ_ALLOWED=false`) — all evidence below comes
from the synthetic fixture (`tests/fixtures/v4_2_r7_full_sample/`) and
targeted unit-level characterization of `FunctionalFlowResolver`/
`MarkdownExporter`. No real IST percentage is claimed to have changed.

## SUMMARY TABLE

| ID | R7_SEVERITY | R7_1_STATUS | PRODUCTION_CHANGE | TEST_EVIDENCE | RESULT |
|---|---|---|---|---|---|
| F-01 | HIGH | FIXED | Yes — `legacy_documenter/analysis/flow_resolver.py`, `legacy_documenter/analysis/_flow_report_composition.py`, `legacy_documenter/exporters/technical_documentation_renderer.py` | `tests/test_v4_2_r7_1_real_pilot_findings_correction.py` (`CharacterizationTests` A–E, `F01MachineRepresentationTests`, `F01HumanDocumentationTests`); `tests/test_v4_2_r7_synthetic_full_fixture.py::FunctionalFlowTests::test_bl_to_database_flow_status_still_downgrades_but_now_says_so_explicitly` | Both facts ("reached a confirmed terminal" / "an unresolved boundary remains") are now independently visible, machine- and human-readable, without changing or hiding the pre-existing `status`/`confidence` aggregation. |
| F-02 | MEDIUM | FIXED | Yes — `legacy_documenter/exporters/markdown_exporter.py` (`solution_structure`) | `tests/test_v4_2_r7_1_real_pilot_findings_correction.py::F02DuplicateSolutionNameTests` | Duplicate-named solutions are now disambiguated by their own repository-relative `.sln` path in the rendered header; solution identity (the bare `name` field) is unchanged. |
| F-03 | MEDIUM | FIXED | Yes — `legacy_documenter/exporters/markdown_exporter.py` (`webforms_map`) | `tests/test_v4_2_r7_1_real_pilot_findings_correction.py::F03WebFormsRegisterRenderingTests` | `register` entries render as sorted Markdown sub-bullets of their own source-derived attributes; the internal `_normalized` lookup copy and raw Python `dict` repr text are never emitted. |
| F-04 | LOW | FIXED | Yes — `legacy_documenter/exporters/markdown_exporter.py` (`project_overview`, new `_repository_display_label` helper) | `tests/test_v4_2_r7_1_real_pilot_findings_correction.py::F04AbsolutePathExposureTests` | `PROJECT_OVERVIEW.md` now shows only the repository's trailing folder name, never the analyst's absolute path or local username. `index/repository.json`'s own `root` field (an established machine contract per `legacy_documenter/analysis/deep_source.py`'s rerun-snapshot use of it) is untouched — this correction is scoped to human-facing output only. |
| F-05 | LOW | DEFERRED_BY_DETERMINISM_CONTRACT | No | `tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py::DeterminismTests::test_run_summary_json_is_identical_across_two_runs` (pre-existing, unmodified) | Adding a real wall-clock full-run duration to `RUN_SUMMARY.json` would make that byte-for-byte-identical-across-two-runs contract fail (wall-clock time legitimately differs run to run even against the identical fixture). No existing R1–R6 contract designates `RUN_SUMMARY.json` as runtime telemetry exempt from this determinism requirement, so the exact reasoning above is why F-05 is deferred rather than forced. See section 9 discussion below. |
| F-06 | OBSERVATION | PRESERVED_OBSERVATION | No | `tests/test_v4_2_r7_synthetic_full_fixture.py::GeneratedDocumentationTests` (unmodified) | `InitializeComponent()` boilerplate noise in `UNRESOLVED_FINDINGS.md` remains current, unfixed, unhidden behavior, exactly as R7 recorded it. |
| F-07 | OBSERVATION | PRESERVED_OBSERVATION | No | `tests/test_v4_2_r7_synthetic_full_fixture.py::FunctionalFlowTests::test_markup_bound_handler_reproduces_the_known_outgoing_calls_gap` (unmodified) | `WebEntryResolver` still never attaches `outgoing_calls` to a markup-bound entry point; this assertion is untouched and still passes. |

## F-01 DETAIL

### OLD_SEMANTICS

A functional flow's own top-level `status`/`confidence` fields were a
**worst-case aggregation across every execution path traced from that
flow's entry point**: `flow_confidence` was `"unresolved"` if *any* path in
the flow was not `"confirmed"`, and `status` (`_flow_status`) picked the
first matching terminal type in a fixed precedence order
(`truncated_depth` > `cycle` > `unresolved_boundary` > `data_endpoint` >
`dead_end`). Consequently, a single unrelated unresolved call anywhere in
the traced method sequence (e.g. `cmd.ExecuteNonQuery()` in the synthetic
fixture's `CustomerRepository.Save`, itself downstream of the confirmed
BL→repository→Oracle chain) silently outranked a real, `confirmed`
database/stored-procedure terminal reached by a *different* path in the
same flow — the flow's own headline fields reported `unresolved_boundary`/
`unresolved` with no way to tell that case apart from a flow that resolved
nothing whatsoever. This affected 2,370 of 12,642 real flows (18.7%) in the
V4.2-R7 pilot and is reproduced deterministically by the synthetic
fixture's `btnSave_Click` flow.

### NEW_SEMANTICS

`_flow_confidence`/`_flow_status`'s existing aggregation logic is
**completely unchanged** — no enum value, precedence rule, or worst-case
semantic was altered, consistent with section 4's instruction not to force
every flow with `terminal_operations` to a false success. Two new additive
fields are computed independently from the same already-discovered paths
and added to each flow:

- `has_confirmed_terminal` (bool): `true` if at least one path in the flow
  is `confidence: "confirmed"` and reaches a `stored_procedure`/`sql`/
  `data_operation` terminal.
- `has_unresolved_boundary` (bool): `true` if at least one path in the flow
  has terminal type `unresolved_boundary`/`cycle`/`truncated_depth`.

`index/flow_summary.json` gains three matching aggregate counters:
`flows_with_confirmed_terminal`, `flows_with_unresolved_boundary`,
`flows_with_both` (all deterministically derived from existing per-flow
data, per section 5 — no fabricated percentage or classification).
`FUNCTIONAL_FLOWS.md` renders `Confirmed terminal reached:`/`Unresolved
boundary remains:` alongside the existing `Status:`/`Confidence:` line for
every flow, plus a short explanatory paragraph at the top of the document,
so a human reader sees both facts together rather than only the
potentially-misleading `status` value.

### COMPATIBILITY

100% additive/backward-compatible. Every pre-existing field
(`status`, `confidence`, `terminal_operations`, `nodes`, `edges`, ...) is
byte-identical to before this correction for the same input — verified by
`F01MachineRepresentationTests::test_existing_status_confidence_fields_are_unchanged_backward_compatible`
and by `test_bl_to_database_flow_status_still_downgrades_but_now_says_so_explicitly`
still asserting the exact same `status: "unresolved_boundary"` /
`confidence: "unresolved"` values as before. No schema/enum change was
needed or made; per section 4, an enum change was never attempted and this
document does not raise a STOP for one.

### MACHINE_REPRESENTATION

`index/functional_flows.json`: each flow object gains
`has_confirmed_terminal`/`has_unresolved_boundary` (both booleans).
`index/flow_summary.json`: gains `flows_with_confirmed_terminal`/
`flows_with_unresolved_boundary`/`flows_with_both` (all integers).

### HUMAN_REPRESENTATION

`documentation/FUNCTIONAL_FLOWS.md`: a new introductory paragraph
explains the distinction once, at the top of the document; every
per-flow entry's summary line gains `Confirmed terminal reached: `yes`/`no``
and `Unresolved boundary remains: `yes`/`no`` alongside the pre-existing
`Status`/`Confidence`; the `## Summary` table (already a generic
sorted-key render of `flow_summary`) automatically picks up the three new
aggregate counters with no renderer change beyond what F-01 already
required.

### SYNTHETIC_FIXTURE_RESULT

`tests/test_v4_2_r7_synthetic_full_fixture.py::FunctionalFlowTests`:
`btnSave_Click`'s flow still reports `status: "unresolved_boundary"` /
`confidence: "unresolved"` (unchanged) and now additionally reports
`has_confirmed_terminal: true` / `has_unresolved_boundary: true`.
`btnNotify_Click`'s flow (which reaches no BL/DB evidence at all) reports
`has_confirmed_terminal: false` / `has_unresolved_boundary: true` —
correctly distinguishing the two cases the pilot could not previously tell
apart from the flow's own fields alone. 5/5 new `CharacterizationTests`
(scenarios A–E, section 3) and 4/4 new `F01MachineRepresentationTests`/
`F01HumanDocumentationTests` pass; both fixture assertions above pass.

## SECTION 9 — F-05 REASONING

Section 9 required inspecting the R1–R6 tests/contracts before adding a
full-run duration field. `tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py::DeterminismTests::test_run_summary_json_is_identical_across_two_runs`
is an existing, unmodified, currently-passing test asserting
`RUN_SUMMARY.json` is byte-for-byte identical across two `run_full_pipeline`
invocations against the same fixture. A real wall-clock duration value
cannot satisfy that invariant (it legitimately differs between two runs of
identical inputs), and no R1–R6 document declares `RUN_SUMMARY.json` an
exception to it as "runtime telemetry." Per section 9's explicit
instruction ("If adding duration would break a determinism invariant, do
not force it"), F-05 is recorded as
`F-05=DEFERRED_BY_DETERMINISM_CONTRACT` rather than implemented. No
timestamp/UUID field was added anywhere, consistent with section 9's final
sentence.

## SCALE PROBLEM (SECTION 10)

Not addressed by this round beyond F-01's own required correction (a fixed
introductory paragraph plus two short additive fields per flow — a
negligible fraction of `FUNCTIONAL_FLOWS.md`'s total size, and required by
F-01 itself). Pagination, an HTML site, a search engine, a database, a web
UI, or any large documentation-navigation architecture were explicitly out
of scope for R7.1 (section 10) and were not implemented. The 44MB/12.8MB/
5.2MB scale problem (`FUNCTIONAL_FLOWS.md`/`UNRESOLVED_FINDINGS.md`/
`DATABASE_ACCESS.md`) recorded by R7 remains open and is recommended for a
future documentation-navigation round (R8+).
