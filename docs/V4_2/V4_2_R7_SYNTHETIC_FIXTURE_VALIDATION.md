# LegacyMapper V4.2-R7 — Synthetic Full-Fixture Validation

## FIXTURE_PATH

`tests/fixtures/v4_2_r7_full_sample/`

## FIXTURE_CONTENTS

Entirely synthetic — no real IST source, class names, project names,
connection strings, or business data. Generic names throughout
(`SampleLegacy`, `CustomerPage`, `CustomerService`, `CustomerRepository`),
following section 13's naming guidance exactly.

```
tests/fixtures/v4_2_r7_full_sample/
├── SampleLegacy.sln                       (1 solution, 3 Project() entries)
├── Web/
│   ├── Web.vbproj
│   ├── CustomerPage.aspx                  (WebForm markup, 2 buttons)
│   └── CustomerPage.aspx.vb               (code-behind: Page_Load, btnSave_Click, btnNotify_Click)
├── Bl/
│   ├── CustomerService.vbproj
│   └── CustomerService.vb                 (BL/service layer: Save() -> CustomerRepository.Save())
└── Sys/
    ├── CustomerRepository.vbproj
    └── CustomerRepository.vb              (data-access layer: Oracle stored-procedure call)
```

Three projects, one solution, three WebForm event/lifecycle handlers, one
resolved cross-project BL call chain, one resolved Oracle stored-procedure
call, and one deliberately-unresolvable external call
(`ExternalMailer.Send(...)`, a type never defined in the fixture).

## COVERED_CAPABILITIES

Per section 13's checklist:

| Capability | Exercised by |
|---|---|
| Solution/project discovery | `SampleLegacy.sln` → 3 projects (`Web`, `CustomerService`, `CustomerRepository`) |
| VB source extraction | All three `.vb` files |
| WebForm/code-behind | `CustomerPage.aspx` + `CustomerPage.aspx.vb` (markup `OnClick` bindings + a code-behind `Handles Me.Load`) |
| Call relationship | `CustomerPage.btnSave_Click` → `CustomerService.Save` (cross-project, resolved) |
| BL/service relationship | `CustomerService.Save` → `CustomerRepository.Save` (cross-project, resolved) |
| Database access | `CustomerRepository.Save`'s `OracleCommand("PKG_CUSTOMER.SAVE_CUSTOMER", ...)` + `CommandType.StoredProcedure` |
| Functional flow | One flow per entry point (`Page_Load`, `btnSave_Click`, `btnNotify_Click`); `btnSave_Click`'s flow reaches the real stored procedure as its `terminal_operations` |
| Unresolved finding | `ExternalMailer.Send(...)` (undefined type) stays explicitly `confidence: "unresolved"`, never guessed |
| Technical documentation generation | All ten `documentation/*.md` files generated and asserted to exist, with `DATABASE_ACCESS.md` asserted to contain the real procedure name |

Not attempted (out of scope for V4.2, per section 13): any non-.NET
language/framework.

## EXPECTED_FULL_STATUS

SUCCESS — all deterministic stages (`SCAN` through `DOCUMENTATION`,
`FINAL_SUMMARY`) succeed; `AI_INTERPRETATION`/`PROPOSAL_GENERATION`
correctly `NOT_RUN` (never opted into).

## GENERATED_DOCUMENTATION

All ten fixed `documentation/*.md` filenames are produced
(`PROJECT_OVERVIEW.md`, `SOLUTION_STRUCTURE.md`, `PROJECT_DEPENDENCIES.md`,
`WEBFORMS_MAP.md`, `CONFIGURATION_SUMMARY.md`, `ANALYSIS_WARNINGS.md`,
`WEB_ENTRY_POINTS.md`, `FUNCTIONAL_FLOWS.md`, `DATABASE_ACCESS.md`,
`UNRESOLVED_FINDINGS.md`), plus `RUN_SUMMARY.json`/`.md`. Given the
fixture's tiny size, none of the real pilot's scale/noise findings
(F-01's underlying data still applies structurally, but nothing here is
large enough to be "too big to read") apply to this fixture's own output
— `DATABASE_ACCESS.md` is 624 bytes and `UNRESOLVED_FINDINGS.md` 789
bytes, both fully readable in one glance.

## SEMANTIC_ASSERTIONS

Implemented in `tests/test_v4_2_r7_synthetic_full_fixture.py` (15 tests,
6 test classes) rather than a full-file snapshot, per section 15's
"focused semantic assertions... more maintainable" guidance:

- `FixtureFullRunTests` — `full` exits `SUCCESS`; every deterministic
  stage `SUCCESS`; AI/proposals correctly `NOT_RUN`/absent; canonical
  knowledge and Technical Lead approval both `False`.
- `SolutionProjectDiscoveryTests` — exactly 1 solution, 3 projects,
  matching names.
- `CallAndBlServiceRelationshipTests` — the UI→BL call and the BL→
  repository call are each individually resolved to the correct
  `resolved_target`; the external, undefined `ExternalMailer.Send` call
  stays explicitly unresolved with no candidates.
- `DatabaseAccessTests` — exactly one `data_access` operation, correctly
  classified `stored_procedure`, exact package/procedure name, with
  evidence.
- `FunctionalFlowTests` — exactly one flow per entry point; the
  `btnSave_Click` flow's `terminal_operations` names the real stored
  procedure with at least four `confirmed` edges (this also **reproduces
  V4.2-R7's F-01 finding deterministically**: the same flow's top-level
  `status` is still `unresolved_boundary` despite that real terminal —
  asserted honestly as current behavior, not hidden); the
  `btnNotify_Click` flow stays explicitly `unresolved_boundary`/
  `unresolved`; a dedicated test
  (`test_markup_bound_handler_reproduces_the_known_outgoing_calls_gap`)
  pins F-07 (markup-bound handlers never get `outgoing_calls` attached)
  as current, unfixed behavior, distinguishing it from the code-behind
  `Handles`-bound `Page_Load` entry point, which IS populated correctly.
- `GeneratedDocumentationTests` — all ten documentation files exist;
  `DATABASE_ACCESS.md` contains the real procedure name;
  `UNRESOLVED_FINDINGS.md` contains the expected section heading.
- `SourceImmutabilityAndRerunTests` — fixture files byte-identical
  before/after; a rerun into the same output directory stays `SUCCESS`;
  the legacy `analyze_repository` path also succeeds on this fixture.

Per section 17, `TEST_CHANGE_ALLOWED=true` was used only for this new
fixture and its own test file; no existing test was altered or weakened,
and no production module was touched.

## RERUN_RESULT

`test_rerun_into_the_same_output_remains_safe`: running `full` twice into
the same `--output` directory both times reports `RunStatus.SUCCESS` —
consistent with V4.2-R6's rerun-safety guarantees (this fixture never
uses `--allow-ai-interpretation`, so V4.2-R6's stale-proposal-cleanup path
is not separately exercised here; that path already has its own dedicated
coverage in `tests/test_v4_2_r6_robustness_recovery_security_and_approval_surface.py`).

## SOURCE_IMMUTABILITY

`test_fixture_files_are_byte_identical_before_and_after` hashes every
fixture file's bytes before and after a `full` run and asserts equality —
confirmed unchanged.

## AI_INVOKED

False (never requested; `--allow-ai-interpretation` is never passed
anywhere in this fixture's tests).

## PROPOSALS

None (`proposal_count: 0`, `proposal_review_status: None`).

## CANONICAL

Not produced (`canonical_knowledge_produced: False`); `knowledge.canonical`
is never imported or invoked by this fixture's tests.

## APPROVAL

Not produced (`technical_lead_approval: False`); `knowledge.approval` is
never imported or invoked by this fixture's tests.

## TESTS

15/15 passing in `tests/test_v4_2_r7_synthetic_full_fixture.py`; full
regression suite 1763/1763 passing (1748 pre-existing + 15 new), 0
weakened, 0 deleted.

## DECISION

FIXTURE_VALIDATED
