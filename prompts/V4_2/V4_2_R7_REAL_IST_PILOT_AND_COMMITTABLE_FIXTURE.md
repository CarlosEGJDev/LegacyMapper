# LegacyMapper V4.2-R7
# Real IST/Operacional Pilot and Committable Full Fixture

TASK=V4_2_R7_REAL_IST_PILOT_AND_COMMITTABLE_FIXTURE

MODE=CONTROLLED_REAL_PILOT

PRODUCTION_CODE_CHANGE_ALLOWED=false
TEST_CHANGE_ALLOWED=true

REAL_AI_RUNTIME_CALL_ALLOWED=false

REAL_LEGACY_REPOSITORY_READ_ALLOWED=true
REAL_LEGACY_REPOSITORY_WRITE_ALLOWED=false

COMMIT_ALLOWED=false
PUSH_ALLOWED=false

V4_1_REOPEN_ALLOWED=false
V5_IMPLEMENTATION_ALLOWED=false
PLUGIN_RUNTIME_IMPLEMENTATION_ALLOWED=false

---

# 1. Authority

V4.2-R0 through R6 are reviewed, approved and versioned.

R6 is formally closed.

Read:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/PROJECT_RECOVERY.md
docs/GENERATED_ARTIFACT_POLICY.md

docs/V4_2/V4_2_R6_ROBUSTNESS_RECOVERY_SECURITY_AND_APPROVAL_SURFACE_RESULT.md
docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md
docs/V4_2/V4_2_R6_CLOSURE_AND_VERSIONING_RESULT.md

Entering baseline:

1748_PASS_0_FAIL_0_SKIP

READINESS=READY

Authoritative exit codes:

SUCCESS = 0
PARTIAL = 1
CLI_USAGE_ERROR = 2
FAILED = 4

---

# 2. Objective

Perform the first controlled V4.2 `full` execution against the real
IST/Operacional legacy system.

Primary question:

Can a developer point LegacyMapper at this real legacy system and receive a
useful, internally consistent technical documentation package without
knowing LegacyMapper's internal V1-V4 pipeline?

This is primarily an EVALUATION round.

Do not repair product behavior during the real pilot.

If a defect is found:

record it,
classify it,
preserve evidence,
and continue where safe.

Do not silently fix the code and rerun until the output looks good.

---

# 3. Real Repository Selection

Two IST/Operacional paths have appeared historically:

C:\Users\cgalianj\source\IST_40\operacional

C:\inetpub\wwwroot\2010\IST\operacional

Before running the pilot:

1. Determine which path currently exists and represents the intended real
   system available in this environment.
2. If both exist, do NOT guess which is authoritative.
3. Compare only enough read-only metadata to identify the intended source
   according to current repository configuration/AGENTS/project state.
4. If authority remains ambiguous, STOP the real pilot and report BLOCKED
   rather than analyzing the wrong repository.

Never modify either location.

Record the exact selected path in the result.

---

# 4. Source Immutability Snapshot

Before the real pilot, establish a practical read-only integrity snapshot.

Do not hash every byte of a huge repository unless reasonably practical.

At minimum record deterministic metadata sufficient to detect obvious
LegacyMapper writes, such as:

file count
directory count
representative/high-value file hashes
latest modification timestamps or equivalent safe metadata

Choose a practical approach for this repository size.

After the pilot, repeat the same snapshot and verify LegacyMapper caused no
source modification.

Do not write snapshot files inside the legacy repository.

---

# 5. Pilot Output

Use a dedicated local generated-output directory.

Recommended:

output/v4_2_r7_ist_operacional/

This output is local/generated pilot evidence.

Do not stage/commit the real IST output unless repository policy explicitly
says otherwise.

Do not place generated files inside the legacy source repository.

---

# 6. Real Pilot Command

Run the deterministic full workflow only:

python main.py full "<selected IST/Operacional path>" \
    --output "output/v4_2_r7_ist_operacional"

Do NOT use:

--allow-ai-interpretation

REAL_AI_RUNTIME_CALL_ALLOWED=false

This pilot must establish deterministic V4.2 behavior first.

Capture:

exit code
overall run status
stage statuses
structured errors/warnings
duration if naturally available
generated artifact locations

Do not repeatedly rerun the real pilot to obtain a better result.

One primary real pilot execution is authoritative.

If it exposes a defect, preserve that result.

A second run is allowed only if explicitly required to test R6 rerun/recovery
semantics, and it must be labeled separately rather than replacing the first
result.

---

# 7. Intermittent R6 Trigger

R6 disclosed one non-reproducible occurrence involving:

test_deterministic_run_then_ai_enabled_rerun_same_output

Before the real pilot run:

python -m unittest discover -s tests

Run the suite once.

If that symptom or any unexplained regression occurs:

STOP.

Do not repeatedly rerun until green.

Set:

DECISION=V4_2_R7_BLOCKED_REGRESSION_INVESTIGATION

Do not run the real IST pilot.

---

# 8. Documentation Package Evaluation

After the pilot, inspect the generated human-facing documentation.

At minimum evaluate:

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
RUN_SUMMARY.md

Do not merely verify that the files exist.

Evaluate whether they are useful to a developer unfamiliar with IST.

For each document classify:

USEFUL
PARTIALLY_USEFUL
NOT_USEFUL
NOT_GENERATED

and explain why.

---

# 9. Documentation Quality Questions

Evaluate empirically:

Can the reader identify the system/project structure?

Can the reader identify solutions/projects/modules?

Can the reader identify WebForms entry points?

Can the reader follow representative UI -> code -> BL/service -> database
flows where evidence supports them?

Can the reader identify Oracle/database interactions?

Are unresolved relationships clearly distinguished from resolved facts?

Are warnings understandable?

Is deterministic evidence traceable?

Does any document imply unsupported semantics?

Is important information present only in JSON but missing from the
human-readable documentation?

Are documents too large/noisy to be useful?

Are duplicate or low-value sections dominating the result?

Does the documentation expose absolute local paths or other unnecessary
environment-specific information?

Record concrete examples.

Do not invent expected relationships from your own knowledge of IST.

Judge only against source-derived evidence.

---

# 10. Quantitative Pilot Metrics

Record useful deterministic metrics from the real run.

Where available:

repository file count
solutions
projects
VB source files
WebForms/pages/controls
symbols
dependencies
call relationships
web entries/events
database relationships
functional flows
unresolved findings
errors/warnings

Also record generated documentation file count and relevant machine artifact
counts.

Do not alter product code just to manufacture a metric.

If a metric is unavailable, say UNAVAILABLE.

---

# 11. Representative Evidence Sampling

Select a small deterministic/explicit sample of real artifacts to inspect in
depth.

Prefer examples covering:

one WebForm/page
one code-behind path
one BL/service path
one database/Oracle path
one functional flow
one unresolved relationship

The sample must come from LegacyMapper output, not prior conversational
knowledge.

For each sample:

identify the output evidence
identify what the documentation claims
verify the claim is supported by deterministic evidence
classify as:

SUPPORTED
PARTIALLY_SUPPORTED
UNSUPPORTED

Any UNSUPPORTED human-facing statement is a serious pilot finding.

Do not modify production code during R7 to fix it.

---

# 12. Real Source Confidentiality

Do not copy large portions of corporate source into committed documentation.

The R7 result/review may include:

filenames
project names
symbol names
aggregate metrics
short evidence identifiers
short diagnostic examples necessary to explain a defect

Avoid embedding:

credentials
connection-string secrets
personal data
large source excerpts
full configuration files
large generated JSON payloads

Sanitize any sensitive values.

The local generated output may contain source-derived analysis as already
designed, but it must remain governed by GENERATED_ARTIFACT_POLICY and must
not be committed accidentally.

---

# 13. Synthetic Committable Full Fixture

In addition to the real pilot, create or extend a small synthetic fixture
that exercises the complete deterministic V4.2 workflow.

Purpose:

preserve a committable regression example representing the capabilities
validated against IST without committing IST-derived data.

The fixture must be synthetic.

Do NOT copy:

real IST source
real class names
real project names
real connection strings
real business names/data

It should contain enough synthetic .NET/VB.NET/WebForms/Oracle structure to
exercise, where reasonably possible:

solution/project discovery
VB source extraction
WebForm/code-behind
call relationship
BL/service relationship
database access
functional flow
unresolved finding
technical documentation generation

Use generic names such as:

SampleLegacy
CustomerPage
CustomerService
CustomerRepository

or equivalent.

Do not attempt V5 language/framework agnosticism.

This remains a V4.2 .NET/VB/WebForms-oriented fixture.

---

# 14. Fixture Location

Follow current tests/fixtures conventions.

Prefer a clearly named location such as:

tests/fixtures/v4_2_r7_full_sample/

unless current repository conventions indicate a better path.

Do not place generated output inside the fixture itself.

---

# 15. Fixture Validation

Add focused tests proving the synthetic fixture can run through `full`
deterministically and produce the expected documentation package.

At minimum verify:

full exits SUCCESS or the explicitly justified expected status
required deterministic stages succeed
documentation files exist
representative WebForm evidence appears
representative database evidence appears
representative functional-flow evidence appears
unresolved evidence remains explicit
no AI invoked
no proposals
no canonical knowledge
no approval
source fixture unchanged
rerun same output remains safe

Do not assert huge full-file snapshots if focused semantic assertions are
more maintainable.

---

# 16. No Production Fixes During Pilot

PRODUCTION_CODE_CHANGE_ALLOWED=false

This is important.

If the real pilot reveals:

missing extraction
incorrect relationships
bad rendering
performance issue
crash
path issue
unsupported claim
documentation usability problem

do NOT edit production code in R7.

Classify findings:

BLOCKER
HIGH
MEDIUM
LOW
OBSERVATION

For each finding record:

ID
severity
evidence
affected artifact/stage
expected behavior
observed behavior
recommended future action

A blocker/high issue may require R7.1 before closure.

---

# 17. Allowed Test/Fixture Changes

TEST_CHANGE_ALLOWED=true only for:

synthetic fixture
R7 fixture tests
test helpers directly necessary for that fixture

Do not alter tests merely to accommodate a real-pilot defect.

Do not weaken existing assertions.

Do not change production modules.

---

# 18. Real AI Guard

REAL_AI_RUNTIME_CALL_ALLOWED=false

No real AI provider may be invoked.

Do not run:

full --allow-ai-interpretation

against IST.

Do not run normal provider resolution manually.

If an AI path must be exercised for the synthetic fixture, use only
FakeLLMProvider — but AI is not required for this R7 fixture objective.

Expected:

REAL_PROVIDER_CALLS=0

---

# 19. Approval / Canonical Boundary

R7 does NOT implement or execute approval.

Expected:

TECHNICAL_LEAD_APPROVAL=false
CANONICAL_KNOWLEDGE_PRODUCED=false

Do not implement `run_id`.

Do not implement approve/reject/correction commands.

Do not invoke canonical composition.

The approval-surface design remains design-only.

---

# 20. Regression

Before real pilot:

python -m unittest discover -s tests

Run once.

Require:

1748_PASS_0_FAIL_0_SKIP

before adding R7 tests/fixture.

After fixture/test additions:

python -m unittest discover -s tests

Require all previous tests plus R7 tests.

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY
provider_calls=0
real_llm_calls=0

Record both pre-pilot and final counts.

---

# 21. Maintainability

No production code should change.

If production code differs after R7:

STOP and explain why.

Fixture/test additions do not justify modifying frozen V4.1 production
baselines.

Do not update production maintainability expectations unless production
source actually changed — which is forbidden in R7.

---

# 22. Human Review Artifact

Create:

docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md

Include:

SELECTED_SOURCE
PILOT_COMMAND
PILOT_EXIT_CODE
PILOT_STATUS

SOURCE_IMMUTABILITY

QUANTITATIVE_METRICS

DOCUMENT_EVALUATION

QUALITY_QUESTIONS

REPRESENTATIVE_SAMPLES

UNSUPPORTED_CLAIMS

MISSING_HUMAN_DOCUMENTATION

NOISE_OR_SCALE_ISSUES

SECURITY_AND_CONFIDENTIALITY

FINDINGS

OVERALL_DOCUMENTATION_ASSESSMENT

RECOMMENDATION

This document must allow the Technical Lead to judge the real output without
requiring the entire generated IST output tree.

---

# 23. Synthetic Fixture Validation Artifact

Create:

docs/V4_2/V4_2_R7_SYNTHETIC_FIXTURE_VALIDATION.md

Include:

FIXTURE_PATH
FIXTURE_CONTENTS
COVERED_CAPABILITIES
EXPECTED_FULL_STATUS
GENERATED_DOCUMENTATION
SEMANTIC_ASSERTIONS
RERUN_RESULT
SOURCE_IMMUTABILITY
AI_INVOKED
PROPOSALS
CANONICAL
APPROVAL
TESTS
DECISION

---

# 24. Result

Create:

docs/V4_2/V4_2_R7_REAL_IST_PILOT_AND_COMMITTABLE_FIXTURE_RESULT.md

Include:

STATUS
BASELINE
SELECTED_REAL_SOURCE
SOURCE_SELECTION
PRE_PILOT_TESTS
INTERMITTENT_R6_TEST_RECURRENCE

REAL_PILOT_COMMAND
REAL_PILOT_EXECUTIONS
REAL_PILOT_EXIT_CODE
REAL_PILOT_STATUS
REAL_PILOT_DURATION

SOURCE_IMMUTABILITY

REAL_DOCUMENTATION_ASSESSMENT
REAL_DOCUMENTATION_REVIEW_PATH

SYNTHETIC_FIXTURE
SYNTHETIC_FIXTURE_VALIDATION_PATH

FILES_CREATED
FILES_MODIFIED

FINDINGS_SUMMARY
BLOCKERS
HIGH_FINDINGS
MEDIUM_FINDINGS
LOW_FINDINGS
OBSERVATIONS

FINAL_TESTS
READINESS
REAL_PROVIDER_CALLS

TECHNICAL_LEAD_APPROVAL
CANONICAL_KNOWLEDGE_PRODUCED

PRODUCTION_CODE_CHANGED
LEGACY_ANALYZE_BEHAVIOR_CHANGED

V4_1_REOPENED
V5_IMPLEMENTED
PLUGIN_RUNTIME

DECISION
NEXT

Expected invariants:

INTERMITTENT_R6_TEST_RECURRENCE=false
REAL_PROVIDER_CALLS=0

TECHNICAL_LEAD_APPROVAL=false
CANONICAL_KNOWLEDGE_PRODUCED=false

PRODUCTION_CODE_CHANGED=false
LEGACY_ANALYZE_BEHAVIOR_CHANGED=false

V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED

Decision rules:

If pre-pilot regression fails:

DECISION=V4_2_R7_BLOCKED_REGRESSION_INVESTIGATION

If source authority is ambiguous:

DECISION=V4_2_R7_BLOCKED_SOURCE_SELECTION

If pilot exposes BLOCKER/HIGH product defects:

DECISION=V4_2_R7_REQUIRES_CORRECTION
NEXT=V4.2-R7.1

If pilot is operationally successful with only acceptable MEDIUM/LOW/
OBSERVATION findings:

DECISION=V4_2_R7_READY_FOR_TECHNICAL_LEAD_REVIEW
NEXT=HUMAN_REVIEW_V4_2_R7

---

# 25. Stop

STOP after:

real pilot
documentation evaluation
synthetic fixture/tests
final regression
readiness
three required R7 documents

Do not implement R7.1 automatically.
Do not implement R8.
Do not commit.
Do not push.
Do not call a real AI provider.
Do not implement approval.
Do not begin V5.