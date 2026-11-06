# LegacyMapper V4.2-R8
# Documentation at Scale, Final Baseline and Closure Preparation

TASK=V4_2_R8_DOCUMENTATION_AT_SCALE_FINAL_BASELINE_AND_CLOSURE_PREPARATION

MODE=CONTROLLED_FINAL_IMPLEMENTATION_AND_VERIFICATION

PRODUCTION_CODE_CHANGE_ALLOWED=true
TEST_CHANGE_ALLOWED=true

REAL_AI_RUNTIME_CALL_ALLOWED=false
REAL_LEGACY_REPOSITORY_READ_ALLOWED=false
REAL_LEGACY_REPOSITORY_WRITE_ALLOWED=false

COMMIT_ALLOWED=false
PUSH_ALLOWED=false

V4_1_REOPEN_ALLOWED=false
V5_IMPLEMENTATION_ALLOWED=false
PLUGIN_RUNTIME_IMPLEMENTATION_ALLOWED=false

---

# 1. Authority

V4.2-R0 through R7.1 are reviewed, approved and versioned.

R7/R7.1 are formally closed.

Read:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/V4_2/V4_2_R7_REAL_IST_PILOT_AND_COMMITTABLE_FIXTURE_RESULT.md
docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md
docs/V4_2/V4_2_R7_SYNTHETIC_FIXTURE_VALIDATION.md
docs/V4_2/V4_2_R7_1_REAL_PILOT_FINDINGS_CORRECTION_RESULT.md
docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md
docs/V4_2/V4_2_R7_R7_1_CLOSURE_AND_VERSIONING_RESULT.md

Entering baseline:

1777_PASS_0_FAIL_0_SKIP

READINESS=READY

Authoritative exit codes:

SUCCESS = 0
PARTIAL = 1
CLI_USAGE_ERROR = 2
FAILED = 4

---

# 2. Objective

Prepare V4.2 for final Technical Lead acceptance.

R7 proved that LegacyMapper can analyze the real IST/Operacional repository
successfully and without fabricating relationships.

R7 also proved that several detailed human-facing documents become too large
to be practically consumed as single flat Markdown files.

R8 must solve that usability problem with the smallest deterministic design
that preserves detailed evidence.

R8 must then produce the final V4.2 verification/baseline and closure
preparation artifacts.

Do NOT formally close/version V4.2 in this task.

Technical Lead review is still required first.

---

# 3. Core Documentation Principle

Do NOT solve scale by deleting evidence.

Use two levels:

LEVEL 1 — NAVIGATION / SUMMARY
small human-readable documents that orient the developer and provide links
or deterministic references to detailed documentation.

LEVEL 2 — DETAIL
complete deterministic evidence, partitioned where necessary into
human-manageable documents.

The detailed machine-readable indexes remain authoritative evidence.

Human documentation is a projection of that evidence.

---

# 4. Characterize Current Documentation Architecture

Before changing production code inspect:

legacy_documenter/exporters/markdown_exporter.py
legacy_documenter/exporters/technical_documentation_renderer.py
legacy_documenter/documentation/
documentation stage orchestration
output ownership/recovery from R6

Characterize:

how fixed documentation filenames are generated;
whether downstream tests/contracts require exactly ten Markdown files;
how RUN_SUMMARY reports documentation locations;
whether links between Markdown files are currently supported;
whether deterministic ordering is guaranteed;
how stale generated documentation is cleaned on rerun.

Add characterization tests before changing behavior where required.

Do not infer a contract only from R7's output.

---

# 5. Scale Targets

Historical R7 real-pilot observations:

FUNCTIONAL_FLOWS.md ≈44MB / 396K lines
UNRESOLVED_FINDINGS.md ≈12.8MB / 163K lines
DATABASE_ACCESS.md ≈5.2MB / 32.5K lines

These historical values MUST NOT be claimed to have changed because R8 does
not rerun IST.

R8 should design deterministic partitioning based on semantic structure, not
on observed IST-specific names.

Primary scale targets:

FUNCTIONAL_FLOWS
DATABASE_ACCESS
UNRESOLVED_FINDINGS

WEB_ENTRY_POINTS and PROJECT_DEPENDENCIES may remain single documents unless
the architecture naturally supports safe partitioning and characterization
shows a clear benefit.

Do not broaden scope unnecessarily.

---

# 6. Documentation Navigation

Create a deterministic top-level navigation document, preferably:

documentation/README.md

or another clearly justified stable name.

It should tell a developer:

what LegacyMapper analyzed;
where to start;
where system/solution/project structure is documented;
where WebForms/entry points are documented;
where functional flows are documented;
where database access is documented;
where unresolved findings are documented;
where configuration/warnings are documented;
what "confirmed" and "unresolved" mean;
how to reach machine-readable evidence when more detail is needed.

Keep it concise.

Do not embed absolute analyst paths.

Do not expose credentials.

---

# 7. Functional Flow Partitioning

Replace the "one enormous flat human document" experience with a deterministic
summary/index plus partitioned detail.

Preferred conceptual structure:

documentation/
  FUNCTIONAL_FLOWS.md
  functional_flows/
      ...

FUNCTIONAL_FLOWS.md should become an index/summary suitable for human use.

Detailed flow documents should be partitioned by a stable semantic unit.

Choose the safest available unit after inspecting actual data, for example:

project
WebForm/source file
entry-point grouping

Do NOT partition using arbitrary byte/line chunks if a semantic grouping is
available.

Requirements:

stable deterministic filenames;
safe filenames;
no path traversal;
no AI-controlled filenames;
deterministic ordering;
repository-relative context;
links from summary/index to detail;
detail retains evidence;
F-01's additive fields remain visible.

If one semantic group is itself extremely large, a deterministic secondary
partition may be used only if needed and documented.

---

# 8. Database Access Partitioning

Apply the same principle.

Preferred conceptual structure:

documentation/
  DATABASE_ACCESS.md
  database_access/
      ...

Top-level document:

summary
counts
navigation
important classification explanation

Detail may be grouped deterministically by:

project
package
or another existing stable semantic unit

chosen from actual model structure.

Preserve:

operation kind
stored procedure where available
provider where available
source evidence
confidence/status where present

Do not invent architectural relationships.

---

# 9. Unresolved Findings Partitioning and Signal

Apply the same navigation/detail pattern.

Preferred:

documentation/
  UNRESOLVED_FINDINGS.md
  unresolved_findings/
      ...

The summary must distinguish categories of unresolved evidence where the
existing model already supports that distinction.

Do not hide unresolved findings.

F-06 remains:

PRESERVED_OBSERVATION

unless a purely PRESENTATIONAL grouping can separate obvious categories
without changing resolution semantics.

Do NOT suppress or discard InitializeComponent evidence in R8.

It may be grouped into an appropriate category if deterministically
classifiable from existing data.

Business-looking unresolved calls must remain visible.

No heuristic AI classification.

---

# 10. Backward Compatibility

Preserve the existing top-level filenames:

PROJECT_OVERVIEW.md
SOLUTION_STRUCTURE.md
PROJECT_DEPENDENCIES.md
WEBFORMS_MAP.md
CONFIGURATION_SUMMARY.md
ANALYSIS_WARNINGS.md
WEB_ENTRY_POINTS.md
FUNCTIONAL_FLOWS.md
DATABASE_ACCESS.md
UNRESOLVED_FINDINGS.md

Existing consumers must still find these names.

The three scale-target files may change from full-detail documents into
summary/index documents.

Document this explicitly as an authorized human-documentation behavior
change.

Machine indexes must not lose information.

---

# 11. Generated Artifact Ownership / Rerun

R6 established safe output ownership and stale-artifact handling.

Partitioned documentation introduces generated subdirectories.

Integrate them into the existing ownership model.

Requirements:

rerunning into the same output safely replaces LegacyMapper-owned detail;
stale partition files from a previous run cannot survive as if current;
unknown/user-created files are preserved;
cleanup never escapes output root;
source repository is untouched.

Add focused tests.

Do not implement a new generic artifact framework unless necessary.

---

# 12. Safe Deterministic Filenames

Partition filenames must be produced exclusively by deterministic trusted
code.

Handle:

duplicate names
characters invalid on Windows
case collisions
very long names
empty names

Prefer stable IDs already present in model data when they improve safety.

Human-readable label + stable ID is acceptable.

Do not use Python's randomized hash().

Do not use timestamp or UUID.

No AI/provider content controls filesystem paths.

Test path traversal inputs.

---

# 13. Relative Markdown Links

Links between documentation files must be:

relative;
portable;
deterministic;
correct on Windows-generated output;
not absolute filesystem URLs.

Prefer POSIX-style relative Markdown link separators where appropriate.

Test links against generated fixture output.

---

# 14. Synthetic Large-Scale Fixture/Test

Do NOT copy IST data.

Extend testing with synthetic generated data large enough to prove that the
partitioning architecture behaves correctly beyond a trivial single-flow
fixture.

This does NOT require thousands of committed source files.

Prefer programmatically generated synthetic model objects in tests where
possible.

Test:

multiple projects/groups
duplicate labels
unsafe filename characters
large number of flows/operations/findings
deterministic partition ordering
stable filenames
links resolve
rerun removes stale owned partitions
unknown user files preserved

Keep tests fast and deterministic.

---

# 15. Existing R7 Synthetic Fixture

Preserve:

tests/fixtures/v4_2_r7_full_sample/

It must still execute through `full`.

Its expected documentation package must be updated only for authorized R8
additive/index/partition behavior.

Preserve F-01 correction.

Preserve F-07 observation.

No real IST data.

---

# 16. F-05 / F-06 / F-07

F-05:

DEFERRED_BY_DETERMINISM_CONTRACT

Do not add nondeterministic wall-clock data to RUN_SUMMARY.json.

F-06:

PRESERVED_OBSERVATION

Do not remove evidence.

Presentational categorization is allowed if deterministic and lossless.

F-07:

PRESERVED_OBSERVATION

Do not modify WebEntryResolver behavior in R8.

These items must remain visible in final V4.2 debt/known limitations.

---

# 17. Final User Documentation

Update/create V4.2 operational documentation explaining the user-facing
workflow.

At minimum produce:

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md
docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md

User manual should explain:

analyze
full
readiness
default no-AI behavior
optional AI interpretation flag
output structure
documentation/README.md
how to navigate partitioned documentation
exit codes
partial/failure behavior
rerun behavior
proposal review boundary
that approval/canonical promotion is not implemented
that Plugin runtime is not implemented

Technical manual should explain:

CLI routing
full pipeline orchestration
stage/result model
output ownership/recovery
documentation partitioning
AI interpretation/proposal boundary
Technical Lead approval boundary
canonical/R11/R12 status
security/provider guard
known limitations/debt
V5 boundary

Do not rewrite historical V4/V4.1 manuals.

---

# 18. Approval Surface Status

Preserve:

docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md

APPROVED_DESIGN_ONLY
IMPLEMENTATION_STATUS=NOT_IMPLEMENTED

Do not implement:

run_id
approve
reject
request correction
ApprovalDecision persistence
canonical promotion
R11/R12 orchestration

These remain future work.

---

# 19. V5 Boundary

V5 remains:

NOT_IMPLEMENTED

Explicitly preserve for V5:

language agnosticism
framework agnosticism
database agnosticism
project-layout agnosticism
AI/provider/model agnosticism

V4.2 must not redesign these.

---

# 20. Real AI / Real IST

Do NOT run real AI.

Do NOT run real IST.

REAL_PROVIDER_CALLS=0
REAL_IST_ACCESSED=false

R7 remains the authoritative real pilot.

R8 verification uses committed/synthetic fixtures.

---

# 21. Final Regression

Run:

python -m unittest discover -s tests

Entering baseline:

1777_PASS_0_FAIL_0_SKIP

Require all previous tests plus R8 tests.

If the historical R6 intermittent symptom recurs:

STOP.

Do not rerun repeatedly until green.

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY
provider_calls=0
real_llm_calls=0

Verify:

python main.py --help
python main.py full --help
python main.py readiness

No real provider.

No real IST.

---

# 22. Final V4.2 Baseline

Create:

output/v4_2_r8/V4_2_FINAL_BASELINE.json
output/v4_2_r8/V4_2_FINAL_MANIFEST.json

These are V4.2 final-candidate artifacts, not formal closure until Technical
Lead approval.

Use deterministic content only.

Do NOT include:

wall-clock timestamp
UUID
nondeterministic duration
absolute analyst path
environment secrets

Baseline should capture at minimum:

V4.2 implementation state
latest completed implementation round candidate
test count
readiness
exit-code contract
CLI commands
full deterministic pipeline availability
AI interpretation opt-in availability
approval/canonical boundary
Plugin runtime status
V5 status
R7 real-pilot historical status
R7 findings final state
documentation navigation/partitioning state
known limitations/debt

Manifest should provide deterministic hashes of authoritative V4.2
source/test/docs/contracts needed to verify the candidate state.

Do not include local real-IST generated output.

---

# 23. Baseline Integrity

After writing baseline/manifest:

verify deterministic regeneration where current tooling supports it;
verify referenced files exist;
verify no real IST output included;
verify no secrets;
verify no absolute local paths;
verify manifest hashes.

Add tests/tools only if needed for deterministic verification.

Do not modify V4 or V4.1 frozen baselines.

---

# 24. Maintainability Inventory

Because production code may change for partitioning:

recompute live maintainability inventory using:

tools.v4_1_r0.report.build_inventory

Do not hand-estimate.

Do not modify frozen V4.1 historical inventory.

If ranking/top-N changes occur because of legitimate R8 changes, reconcile
the live comparison exactly as prior approved rounds did.

Do not weaken assertions.

Report significant module/function sizes after R8.

Avoid creating another VERY_HIGH-risk monolith.

---

# 25. Final Documentation Review Artifact

Create:

docs/V4_2/V4_2_R8_FINAL_DOCUMENTATION_REVIEW.md

Using only synthetic/committed evidence, evaluate:

top-level navigation
functional-flow navigation
database navigation
unresolved navigation
relative links
determinism
rerun safety
unknown-file preservation
source immutability
F-01 representation
F-05 status
F-06 status
F-07 status
security
remaining scale risks

Do NOT claim new real-IST size/performance metrics.

Explicitly distinguish:

historical R7 evidence
R8 synthetic verification

---

# 26. Result

Create:

docs/V4_2/V4_2_R8_DOCUMENTATION_AT_SCALE_FINAL_BASELINE_AND_CLOSURE_PREPARATION_RESULT.md

Include:

STATUS
BASELINE

FILES_CREATED
FILES_MODIFIED

DOCUMENTATION_NAVIGATION
FUNCTIONAL_FLOW_PARTITIONING
DATABASE_ACCESS_PARTITIONING
UNRESOLVED_FINDINGS_PARTITIONING

BACKWARD_COMPATIBILITY
OUTPUT_OWNERSHIP
RERUN_SAFETY
FILENAME_SAFETY
RELATIVE_LINKS

USER_MANUAL
TECHNICAL_MANUAL

R7_HISTORICAL_PILOT
F01_STATUS
F02_STATUS
F03_STATUS
F04_STATUS
F05_STATUS
F06_STATUS
F07_STATUS

DOCUMENTATION_SCALE_STATUS

TESTS
INTERMITTENT_R6_TEST_RECURRENCE
READINESS
REAL_PROVIDER_CALLS
REAL_IST_ACCESSED

FINAL_BASELINE
FINAL_BASELINE_SHA256
FINAL_MANIFEST
FINAL_MANIFEST_SHA256
MANIFEST_INTEGRITY

MAINTAINABILITY

TECHNICAL_LEAD_APPROVAL
CANONICAL_KNOWLEDGE_PRODUCED
APPROVAL_SURFACE_IMPLEMENTATION

PRODUCTION_BEHAVIOR_CHANGED
LEGACY_ANALYZE_BEHAVIOR_CHANGED

AUTHORITATIVE_EXIT_CODE_CONTRACT

V4_1_REOPENED
V5_IMPLEMENTED
PLUGIN_RUNTIME

DEFERRED
RISKS
DECISION
NEXT

Expected invariants:

R7_HISTORICAL_PILOT=COMPLETED

F01_STATUS=FIXED
F02_STATUS=FIXED
F03_STATUS=FIXED
F04_STATUS=FIXED
F05_STATUS=DEFERRED_BY_DETERMINISM_CONTRACT
F06_STATUS=PRESERVED_OBSERVATION
F07_STATUS=PRESERVED_OBSERVATION

REAL_PROVIDER_CALLS=0
REAL_IST_ACCESSED=false

READINESS=READY

TECHNICAL_LEAD_APPROVAL=false
CANONICAL_KNOWLEDGE_PRODUCED=false
APPROVAL_SURFACE_IMPLEMENTATION=NOT_IMPLEMENTED

AUTHORITATIVE_EXIT_CODE_CONTRACT=
SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4

V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED

If successful:

DECISION=V4_2_R8_READY_FOR_FINAL_TECHNICAL_LEAD_REVIEW
NEXT=HUMAN_FINAL_REVIEW_V4_2

Otherwise:

DECISION=V4_2_R8_BLOCKED
NEXT=<explicit reason>

---

# 27. Stop

STOP after:

documentation-at-scale implementation
manuals
final regression
readiness
final candidate baseline/manifest
final documentation review
R8 result

Do not formally close V4.2.
Do not commit.
Do not push.
Do not run IST.
Do not call a real provider.
Do not implement approval.
Do not begin V5.