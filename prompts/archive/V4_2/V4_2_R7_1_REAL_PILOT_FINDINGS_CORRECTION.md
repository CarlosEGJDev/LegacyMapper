# LegacyMapper V4.2-R7.1
# Real Pilot Findings Correction

TASK=V4_2_R7_1_REAL_PILOT_FINDINGS_CORRECTION

MODE=CONTROLLED_CORRECTION

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

V4.2-R7 real IST pilot was reviewed by the Technical Lead.

The R7 execution and diagnosis are accepted.

R7 is NOT formally closed because the Technical Lead accepts:

F-01 = HIGH / MUST_FIX_BEFORE_R7_CLOSURE
F-02 = MEDIUM / FIX_IN_R7_1
F-03 = MEDIUM / FIX_IN_R7_1
F-04 = LOW / FIX_IN_R7_1
F-05 = LOW / FIX_IN_R7_1
F-06 = OBSERVATION / DEFER
F-07 = OBSERVATION / DEFER

Read:

CLAUDE.md
AGENTS.md
PROJECT_STATE.json

docs/V4_2/V4_2_R7_REAL_IST_PILOT_AND_COMMITTABLE_FIXTURE_RESULT.md
docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md
docs/V4_2/V4_2_R7_SYNTHETIC_FIXTURE_VALIDATION.md

Entering baseline:

1763_PASS_0_FAIL_0_SKIP

Do not run the real IST repository in this correction round.

Use the synthetic fixture and existing deterministic evidence.

---

# 2. Primary Objective

Correct the product defects discovered empirically by the real R7 pilot
without redesigning V4.2.

Priority order:

1. F-01 flow outcome semantics
2. F-02 duplicate solution rendering
3. F-03 WebForms register rendering
4. F-04 human-facing absolute-path exposure
5. F-05 full-run duration reporting

F-06 and F-07 remain deferred observations.

Do not broaden scope automatically.

---

# 3. F-01 — Characterize Before Fixing

This is the critical correction.

R7 observed:

2370 / 12642 real functional flows had:

terminal_operations != []

with a confirmed path reaching a real database/data-access terminal,

while the flow's top-level fields still reported:

status = unresolved_boundary
confidence = unresolved

The synthetic R7 fixture deterministically reproduces this behavior.

Before changing production code:

inspect FunctionalFlowResolver;
inspect current status/confidence aggregation;
inspect path-level status/confidence;
inspect terminal_operations semantics;
inspect existing V2/V3/V4 regression contracts.

Add focused characterization tests that distinguish at least:

A. flow resolves a confirmed terminal and has no unresolved side boundary;
B. flow resolves a confirmed terminal but also contains an unrelated
   unresolved side call;
C. flow has no confirmed terminal and ends unresolved;
D. multiple paths where some reach confirmed terminals and some do not;
E. flow reaches only non-database resolved nodes but still has unresolved
   boundaries.

Do not assume the Technical Lead's diagnosis implies a particular enum
change.

First establish the actual existing domain semantics.

---

# 4. F-01 — Required Semantic Invariant

The human-facing and machine-readable flow result must distinguish:

"this flow successfully reached confirmed terminal evidence"

from:

"this flow resolved nothing useful."

An unrelated unresolved side call must not erase the fact that a confirmed
path reached a terminal operation.

However:

Do NOT hide unresolved boundaries.

Do NOT simply force every flow with terminal_operations to SUCCESS if that
would falsely imply complete resolution.

If the existing status model supports a mixed/partial state, use it.

If it does not, prefer the smallest explicit representation that preserves
both facts, for example conceptually:

confirmed terminal reached = true
unresolved boundaries remain = true

rather than destroying either side of the evidence.

Do not invent a new status casually.

If changing the status enum/schema is required, STOP and explain the
compatibility impact before doing it.

Prefer an additive/derived representation when sufficient.

Machine output and human documentation must agree.

---

# 5. F-01 — Documentation

FUNCTIONAL_FLOWS.md must make it immediately understandable when:

a confirmed terminal was reached;
unresolved boundaries also remain.

The summary must not imply that every unresolved boundary means no useful
flow was resolved.

Include useful aggregate metrics such as:

flows with confirmed terminal operations
flows with unresolved boundaries
flows containing both

only if these metrics can be deterministically derived from existing data.

Do not fabricate percentages or classifications.

---

# 6. F-02 — Duplicate Solutions

R7 found 24/113 duplicate solution names in the real pilot.

Correct SOLUTION_STRUCTURE.md rendering so duplicate-named solutions are
distinguishable.

Prefer deterministic path/context disambiguation.

Do not alter solution identity merely for presentation.

Do not expose unnecessary absolute local prefixes.

A reader should be able to distinguish, for example, two solutions with the
same filename located in different repository-relative directories.

Add focused tests.

---

# 7. F-03 — WebForms Register Rendering

WEBFORMS_MAP.md currently renders register metadata through Python dict repr.

Replace that with deterministic human-readable Markdown.

Do not expose internal normalization fields merely because they exist in the
dictionary.

Render only useful public/source-derived fields.

Preserve deterministic ordering.

Add focused tests proving raw:

{'TagPrefix': ...

style output is not emitted.

---

# 8. F-04 — Human-Facing Absolute Path

The real pilot exposed:

C:\Users\<username>\...

in PROJECT_OVERVIEW.md.

Human-facing documentation should use a safe repository display label or
repository-relative representation.

Do not remove information required internally for deterministic analysis.

Do not blindly alter machine artifacts if the absolute root is part of an
existing machine contract.

Scope this correction primarily to HUMAN-FACING documentation.

If `index/repository.json.root` is an established machine contract, preserve
it and explicitly document that F-04 is corrected for human-facing output
only.

Never expose the username in newly rendered shared documentation when it is
not necessary.

Add a test using a synthetic absolute source root.

---

# 9. F-05 — Full Run Duration

Add a whole-run duration to the V4.2 run result/summary if this can be done
without compromising deterministic versioned artifacts.

Important distinction:

runtime operational telemetry may naturally vary between executions.

Do not introduce wall-clock duration into artifacts whose byte-for-byte
determinism is an established contract unless that contract explicitly
allows runtime telemetry.

Inspect R1-R6 tests/contracts first.

Preferred solution:

record duration in the operational RUN_SUMMARY only if RUN_SUMMARY is already
defined as execution telemetry rather than a deterministic versioned
baseline.

If adding duration would break a determinism invariant, do not force it.

In that case document:

F-05=DEFERRED_BY_DETERMINISM_CONTRACT

with exact reasoning.

Do not add timestamps/UUIDs to canonical/versioned knowledge.

---

# 10. Scale Problem

The real pilot showed:

FUNCTIONAL_FLOWS.md ~44MB
DATABASE_ACCESS.md ~5.2MB
UNRESOLVED_FINDINGS.md ~12.8MB

R7 classified these as not practically human-usable.

R7.1 is primarily a correctness/presentation correction round, not a full
documentation-navigation redesign.

However, F-01's FUNCTIONAL_FLOWS rendering correction must not make the
44MB document larger without improving usability.

Inspect whether a SMALL deterministic improvement is safe, such as a concise
summary at the beginning.

Do NOT implement:

pagination framework
HTML site
search engine
database
web UI
large documentation architecture

Record the remaining scale problem explicitly for R8/future work.

---

# 11. F-06 / F-07

Do NOT fix automatically.

F-06:
InitializeComponent() noise in unresolved findings.

F-07:
markup-bound WebEntryResolver outgoing_calls lookup gap.

Preserve the R7 synthetic fixture tests that reproduce current behavior.

Do not change those assertions to hide the observations.

Record both as deferred.

---

# 12. Existing R7 Fixture

The synthetic fixture is now authoritative regression evidence for R7
findings.

Preserve:

tests/fixtures/v4_2_r7_full_sample/

Do not replace it with a simpler fixture that stops reproducing F-01/F-07.

Update only the F-01 assertion whose expected behavior is intentionally
corrected.

F-07 must continue to reproduce its known current behavior.

No IST-derived names/data may enter the fixture.

---

# 13. Security

REAL_AI_RUNTIME_CALL_ALLOWED=false

REAL_LEGACY_REPOSITORY_READ_ALLOWED=false

Do not access either real IST path.

Use only committed/synthetic fixtures.

No credentials
no environment dumps
no raw traceback
no AI-controlled paths
no automatic approval
no canonical promotion

R5.1 provider guard remains mandatory.

REAL_PROVIDER_CALLS=0

---

# 14. Approval Boundary

Do not implement:

run_id
approve
reject
request-correction
ApprovalDecision persistence
canonical promotion
R11/R12 orchestration
Plugin runtime

Technical Lead remains sole approval authority.

The approved R6 approval-surface document remains DESIGN ONLY.

---

# 15. V5 Boundary

Do not implement:

language agnosticism
framework agnosticism
database agnosticism
project-layout agnosticism
AI/provider/model agnosticism architecture

These remain V5.

---

# 16. Maintainability

Use established Python practices:

idiomatic Python first;
PascalCase classes;
snake_case modules;
clear responsibilities;
type hints at public/service boundaries;
concise docstrings;
comments for non-obvious evidence/determinism rules;
no unnecessary Python magic;
no unnecessary C# ceremony.

Characterize before modifying FunctionalFlowResolver.

Do not grow already-high-risk modules unnecessarily.

If F-01 logic can be extracted into a small deterministic helper with a clear
responsibility, prefer that over adding another large conditional block.

Do not refactor unrelated code.

---

# 17. Tests

Add focused tests for F-01 through F-04 and F-05 if implemented.

At minimum prove:

confirmed terminal only
confirmed terminal + unresolved side boundary
unresolved only
mixed multi-path flow

machine output preserves both resolved and unresolved facts
human flow documentation preserves both facts

duplicate solution names disambiguated
solution identity unchanged

WebForms register rendered as Markdown
internal dict repr absent
internal normalization metadata absent

human-facing overview does not expose synthetic local username

duration contract preserved or explicitly deferred

F-07 remains reproduced and deferred

no AI
no proposals
no approval
no canonical knowledge
source fixture unchanged

legacy analyze unchanged
exit codes unchanged

Do not weaken/delete previous tests.

---

# 18. Regression

Run:

python -m unittest discover -s tests

Entering baseline:

1763_PASS_0_FAIL_0_SKIP

Require all previous tests plus R7.1 tests.

Run:

python -m legacy_documenter.knowledge.readiness

Require:

READINESS=READY
provider_calls=0
real_llm_calls=0

REAL_PROVIDER_CALLS=0

Do not run real IST.

---

# 19. Verification Artifact

Create:

docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md

For F-01 through F-07 provide a table:

ID
R7_SEVERITY
R7_1_STATUS
PRODUCTION_CHANGE
TEST_EVIDENCE
RESULT

Allowed statuses:

FIXED
DEFERRED
PRESERVED_OBSERVATION
BLOCKED

For F-01 additionally explain:

OLD_SEMANTICS
NEW_SEMANTICS
COMPATIBILITY
MACHINE_REPRESENTATION
HUMAN_REPRESENTATION
SYNTHETIC_FIXTURE_RESULT

Do not claim the real IST percentages changed because R7.1 does not rerun
IST.

---

# 20. Result

Create:

docs/V4_2/V4_2_R7_1_REAL_PILOT_FINDINGS_CORRECTION_RESULT.md

Include:

STATUS
BASELINE

FILES_CREATED
FILES_MODIFIED

F01_STATUS
F01_ROOT_CAUSE
F01_OLD_SEMANTICS
F01_NEW_SEMANTICS
F01_COMPATIBILITY

F02_STATUS
F03_STATUS
F04_STATUS
F05_STATUS
F06_STATUS
F07_STATUS

DOCUMENTATION_SCALE_STATUS

SYNTHETIC_FIXTURE
SYNTHETIC_FIXTURE_RESULT

TESTS
READINESS
REAL_PROVIDER_CALLS
REAL_IST_ACCESSED

EXIT_CODE_CONTRACT

TECHNICAL_LEAD_APPROVAL
CANONICAL_KNOWLEDGE_PRODUCED

PRODUCTION_BEHAVIOR_CHANGED
LEGACY_ANALYZE_BEHAVIOR_CHANGED

V4_1_REOPENED
V5_IMPLEMENTED
PLUGIN_RUNTIME

DEFERRED
RISKS
DECISION
NEXT

Expected:

F01_STATUS=FIXED
F02_STATUS=FIXED
F03_STATUS=FIXED
F04_STATUS=FIXED

F05_STATUS=FIXED or DEFERRED_BY_DETERMINISM_CONTRACT

F06_STATUS=PRESERVED_OBSERVATION
F07_STATUS=PRESERVED_OBSERVATION

REAL_PROVIDER_CALLS=0
REAL_IST_ACCESSED=false

EXIT_CODE_CONTRACT=SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4

TECHNICAL_LEAD_APPROVAL=false
CANONICAL_KNOWLEDGE_PRODUCED=false

LEGACY_ANALYZE_BEHAVIOR_CHANGED=false

V4_1_REOPENED=false
V5_IMPLEMENTED=false
PLUGIN_RUNTIME=NOT_IMPLEMENTED

If successful:

DECISION=V4_2_R7_1_READY_FOR_TECHNICAL_LEAD_REVIEW
NEXT=HUMAN_REVIEW_V4_2_R7_1

If F-01 cannot be corrected without a breaking domain/schema change:

DECISION=V4_2_R7_1_BLOCKED
NEXT=TECHNICAL_LEAD_DECISION_REQUIRED

---

# 21. Stop

STOP after R7.1 implementation, regression, readiness and both required
documents.

Do not run IST.
Do not implement R8.
Do not commit.
Do not push.
Do not call a real provider.
Do not implement approval.
Do not begin V5.