# LegacyMapper V4.2-R8 — Final Documentation Review

All evidence in this document comes from the committed synthetic fixture
(`tests/fixtures/v4_2_r7_full_sample/`) and from direct, unit-level
characterization of `TechnicalDocumentationRenderer`/
`MarkdownExporter`/`sync_generated_partition_directory` — never from a
rerun of the real IST/Operacional repository
(`REAL_LEGACY_REPOSITORY_READ_ALLOWED=false` for this round). Where a
number below reflects the historical V4.2-R7 real pilot, it is explicitly
labeled `HISTORICAL (R7)`; a number labeled `R8 SYNTHETIC` is a fresh
observation from this round's own synthetic evidence and must never be
read as a new real-repository measurement.

## TOP_LEVEL_NAVIGATION

`documentation/README.md` (new in R8) links all ten fixed-filename
documents plus itself, states what "confirmed"/"unresolved" mean, and
points to `index/*.json`/`ai_context/*.json` as the authoritative
machine-readable evidence for anything not shown in the human projection.
It never embeds the analyst's absolute repository path — `PROJECT_OVERVIEW.md`'s
existing F-04 correction (V4.2-R7.1) already established the safe-label
pattern (`_repository_display_label`), and `documentation_readme` reuses
that same helper. **R8 SYNTHETIC**: verified directly against the R7
fixture's own generated output (`v4_2_r7_full_sample` → label
`v4_2_r7_full_sample`) and against `DocumentationReadmeTests` with a
synthetic absolute Windows path.

## FUNCTIONAL_FLOW_NAVIGATION

`FUNCTIONAL_FLOWS.md` is now an index: the unchanged F-01 explanatory
paragraph, the unchanged `## Summary` table (now additionally reporting
`flows_with_confirmed_terminal`/`flows_with_unresolved_boundary`/
`flows_with_both`, all deterministically derived from existing per-flow
data), and a `## Flow Groups` table linking one row per project into
`functional_flows/<safe-name>.md`. **R8 SYNTHETIC**: confirmed against the
R7 fixture (one group, `Web\Web.vbproj`, three flows) and against
`FunctionalFlowsPartitioningTests` with a synthetically generated 60-flow/
5-project fixture (12 flows per project), which produces exactly five
partition files with deterministic, repeatable content
(`test_partition_ordering_is_deterministic`).

## DATABASE_NAVIGATION

`DATABASE_ACCESS.md` is now an index: summary sentence, a `## Classification`
section explaining `stored_procedure`/`sql_operation`/`transaction`/
`confidence` (previously implicit, now explicit per R8 section 8), a
`## Access Groups` table linking one row per project into
`database_access/<safe-name>.md`, and `## Parameters` retained at the top
level (small, already grouped by caller — not one of R8's three primary
scale targets). **R8 SYNTHETIC**: confirmed against the R7 fixture (one
group) and against a synthetic 9-access-point/3-project fixture
(`DatabaseAccessPartitioningTests`), preserving operation kind, stored
procedure name, and exact file:line evidence in the partition.

## UNRESOLVED_NAVIGATION

`UNRESOLVED_FINDINGS.md` is now an index over the same four categories the
flat document already used as `##` sections (extraction errors,
unresolved flow boundaries, unresolved entry points, unresolved database
access); each nonempty category links to
`unresolved_findings/<category>.md`. Within the flow-boundaries category,
F-06's `InitializeComponent()` boilerplate is separated into its own
`### Framework/Designer-Generated Boilerplate` subsection, distinct from
`### Other Unresolved Boundaries` — purely presentational, per section 9's
explicit allowance: every row from the flat document is still present
under one heading or the other, and the category's own top-level count is
unaffected (`test_category_count_unaffected_by_the_presentational_split`).
F-06 remains `PRESERVED_OBSERVATION`, not resolved.

## RELATIVE_LINKS

Every link from a navigation document into its partitioned detail uses a
repository-relative, POSIX-style path (`functional_flows/Web_Web_vbproj.md`,
never an absolute filesystem URL or a backslash separator).
`RelativeLinkResolutionTests.test_functional_flows_navigation_links_resolve_on_disk`
parses every such link out of a generated `FUNCTIONAL_FLOWS.md` and
confirms the referenced file actually exists at that path relative to
`documentation/`, on Windows-generated output.

## DETERMINISM

`FunctionalFlowsPartitioningTests.test_partition_ordering_is_deterministic`
and the safe-filename tests (`SafeFilenameTests`) confirm: the same input
always produces the same partition filenames and the same partition
content, never a random hash, timestamp, or UUID. `sanitize_label` makes
path traversal (`../../evil`), invalid Windows characters
(`< > : " / \ | ? *`), empty/`None` labels, over-length labels, and
Windows-reserved device names (`CON`, `PRN`, ...) all resolve to a safe,
deterministic filename; `build_partition_filenames` disambiguates two
labels that collide after sanitization (including a case-only collision,
a real Windows filesystem hazard) with a stable, order-derived numeric
suffix.

## RERUN_SAFETY

`RerunStalePartitionCleanupTests` and
`RenderDocumentationRerunSafetyTests.test_rerun_with_fewer_projects_removes_the_stale_partition_file`
confirm: `sync_generated_partition_directory` (the R8 extension of R6's
output-ownership model, `legacy_documenter/cli/artifact_lifecycle.py`)
removes only `.md` files that are no longer part of the current run's
partition set, writes the current run's files, and creates/removes the
subdirectory itself only as needed. A full `render_documentation` rerun
into the same output with fewer projects shrinks
`documentation/functional_flows/` from three files to one, with no stale
file left behind.

## UNKNOWN_FILE_PRESERVATION

`RerunStalePartitionCleanupTests.test_unknown_user_file_is_preserved_and_directory_is_kept`
confirms a non-`.md` file placed inside a partition directory (e.g. a
person's own note) survives an arbitrary number of reruns, including one
that removes every `.md` partition — the directory itself is never removed
while any file remains in it.

## SOURCE_IMMUTABILITY

No test in this round, nor any production change, reads or writes the
real IST/Operacional repository. The R7 synthetic fixture's own
byte-identity test
(`tests/test_v4_2_r7_synthetic_full_fixture.py::SourceImmutabilityAndRerunTests::test_fixture_files_are_byte_identical_before_and_after`)
still passes unmodified, confirming the fixture itself is untouched by the
new partitioned-documentation code path.

## F01_REPRESENTATION

`FunctionalFlowsPartitioningTests.test_partition_preserves_f01_additive_fields`
confirms every partitioned flow entry still carries `Confirmed terminal
reached:`/`Unresolved boundary remains:` alongside `Status`/`Confidence` —
the F-01 correction (V4.2-R7.1) is fully preserved through the R8
navigation/partition rewrite, not just in the flat fallback renderer.

## F05_STATUS

`DEFERRED_BY_DETERMINISM_CONTRACT` (unchanged from V4.2-R7.1). No wall-clock
duration field was added to `RUN_SUMMARY.json` in R8; the existing
`tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py::DeterminismTests::test_run_summary_json_is_identical_across_two_runs`
still passes unmodified.

## F06_STATUS

`PRESERVED_OBSERVATION`. See UNRESOLVED_NAVIGATION above: R8 groups the
boilerplate presentationally, per section 9's explicit allowance, but does
not filter, hide, or resolve it.

## F07_STATUS

`PRESERVED_OBSERVATION`, unchanged.
`tests/test_v4_2_r7_synthetic_full_fixture.py::FunctionalFlowTests::test_markup_bound_handler_reproduces_the_known_outgoing_calls_gap`
still passes unmodified — `WebEntryResolver` was not touched in R8, per
section 16's explicit instruction not to modify its behavior.

## SECURITY

- No credential, connection-string value, API key, or private-key marker
  appears in any generated document, partition, or new production file
  (checked directly across `docs/V4_2/*.md`, the R8 production modules,
  and the R8 test module).
- `PROJECT_OVERVIEW.md`/`documentation/README.md` never expose the
  analyst's absolute local path or Windows username — verified with a
  synthetic absolute path (`C:\Users\testuser\...`) in both
  `DocumentationReadmeTests` (this round) and the existing F-04 tests
  (V4.2-R7.1).
- Every partition filename is produced exclusively by deterministic
  trusted code (`_documentation_partitioning.py`); no AI/provider content
  ever reaches a filesystem path.
- `output/v4_2_r7_ist_operacional/` (the real pilot's local generated
  evidence) is not read, copied, or referenced by any R8 code or test.

## REMAINING_SCALE_RISKS

The V4.2-R7 real pilot's `WEB_ENTRY_POINTS.md` (1.2MB / 25,595 lines,
`HISTORICAL (R7)`) and `PROJECT_DEPENDENCIES.md` (978KB / 9,424 lines,
`HISTORICAL (R7)`) were both classified `PARTIALLY_USEFUL` rather than
`NOT_USEFUL` — large but structurally organized (per-WebForm sections; one
edge per line) and usable with external search tooling (`grep`, an
editor's find). Per section 5's explicit scope ("may remain single
documents unless the architecture naturally supports safe partitioning and
characterization shows a clear benefit"), R8 did not partition either
document; both remain single flat files. If a future real pilot against a
larger repository finds either genuinely unusable, a future round could
apply the same navigation/partition pattern established here (project for
`PROJECT_DEPENDENCIES.md`, WebForm for `WEB_ENTRY_POINTS.md`) — this is
recorded as open, not attempted.

`legacy_documenter/exporters/technical_documentation_renderer.py` itself
grew to 802 lines (`TechnicalDocumentationRenderer` class: 462 lines) to
hold both the flat and the new navigation/partition rendering paths,
sharing per-item helper functions. The live maintainability inventory
(section 24; see the R8 result document's MAINTAINABILITY section)
classifies it `HIGH` risk, not `VERY_HIGH` — no new `VERY_HIGH`-risk module
was introduced by this round — but it is now the single largest module in
the repository and a candidate for a future extraction round (splitting
the navigation/partition renderers into their own module, following the
precedent already set for `FunctionalFlowResolver`/`DatabaseExtractor` in
V4.1-R6) if it continues to grow.
