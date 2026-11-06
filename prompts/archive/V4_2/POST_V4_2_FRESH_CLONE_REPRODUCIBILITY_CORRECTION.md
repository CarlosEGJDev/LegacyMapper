# LegacyMapper — Post-V4.2 Fresh-Clone Reproducibility Correction

## MODE

POST_V4_2_CONTROLLED_REPRODUCIBILITY_CORRECTION

## MODEL

Claude Opus 4.6

## AUTHORITY

LegacyMapper V4.2 remains formally closed.

The Technical Lead reviewed the Post-V4.2 documentation-update round and
did NOT approve it for versioning yet because that round discovered a real
fresh-clone reproducibility problem.

This is a Post-V4.2 corrective maintenance round.

It does NOT reopen V4.2.

It does NOT implement V5.

It does NOT authorize broad refactoring.

---

# 1. CONFIRMED STARTING FINDING

During:

POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY

the repository was inspected from its cleaned state and the full test suite
was executed once.

Observed live result:

Ran 1625 tests
failures=2
errors=19

Historical V4.2 closure baseline:

1809_PASS_0_FAIL_0_SKIP

Investigation identified a common dependency:

output/v3_r8_1/ARCHITECTURE_EVIDENCE.json

Current facts reported by the documentation round:

- legacy_documenter/knowledge/readiness.py requires this artifact;
- the file is absent from the cleaned repository;
- git log --all found no tracked history for it;
- /output/v3_r8_1/ is excluded as heavy/regenerable output;
- a fresh clone can therefore fail readiness with FileNotFoundError;
- a V4.2 final manifest/integrity verification is also affected by the
  missing artifact;
- the previous 1809-pass closure environment apparently contained local
  artifacts not available from a clean clone.

These findings must be independently verified before modifying anything.

Do not assume the proposed root cause is complete merely because the
documentation round reported it.

---

# 2. PRIMARY OBJECTIVE

Make the current LegacyMapper repository self-contained enough that:

A NEW PROGRAMMER OR DEVELOPMENT AGENT CAN:

git clone
→ inspect repository
→ run the supported repository verification/test workflow
→ run readiness
→ continue toward V5

without requiring undocumented local historical files.

Required property:

FRESH_CLONE_REPRODUCIBILITY=PASS

No real legacy repository may be required.

No real AI provider may be required.

No deleted multi-GB operational analysis output may be restored.

---

# 3. IMPORTANT DISTINCTION

Do NOT confuse:

HISTORICAL BASELINE

with:

CURRENT LIVE REPOSITORY STATE

The historical V4.2 closure:

1809_PASS_0_FAIL_0_SKIP

must remain historical evidence.

Do NOT rewrite historical closure documents to pretend the fresh-clone
problem never existed.

Do NOT silently modify historical hashes.

Do NOT silently regenerate historical artifacts under different content and
present them as the originals.

If a current corrective baseline is needed, it must be explicitly identified
as POST-V4.2.

---

# 4. PHASE A — DIAGNOSIS BEFORE CORRECTION

Before changing production or tests, investigate the 21 non-passing tests.

Create an explicit mapping:

TEST
FAILURE/ERROR
DIRECT_CAUSE
ROOT_CAUSE
MISSING_INPUT_IF_ANY
RELATED_PRODUCTION_CODE
RELATED_HISTORICAL_ARTIFACT

Determine whether all 21 truly share one root cause.

Do not assume they do.

Inspect at minimum:

legacy_documenter/knowledge/readiness.py

legacy_documenter/knowledge/_readiness_*.py

relevant readiness tests

V4.2 baseline/manifest integrity tests

output/v4_2_r8/V4_2_FINAL_BASELINE.json

output/v4_2_r8/V4_2_FINAL_MANIFEST.json

.gitignore

docs/GENERATED_ARTIFACT_POLICY.md

PROJECT_STATE.json

historical V3 readiness evidence/contracts

relevant V3/V4/V4.1/V4.2 closure/result documents

Git history for the missing path where useful.

---

# 5. ARCHITECTURE_EVIDENCE INVESTIGATION

Determine exactly what:

output/v3_r8_1/ARCHITECTURE_EVIDENCE.json

represented.

Answer:

- who produced it;
- from what inputs;
- whether its generation was deterministic;
- whether a generator still exists;
- whether it contained source-derived operational data;
- whether it contained sensitive information;
- whether it was intended as contract evidence or temporary execution output;
- why readiness depends on it;
- why the final manifest references it;
- whether its absence should cause BLOCKED rather than an exception;
- whether the correct solution is to preserve a small fixture/contract,
  regenerate it, remove the dependency, or redesign the check.

Do NOT restore an artifact merely because a test expects it.

First determine its semantic role.

---

# 6. SOLUTION SELECTION

Evaluate at least these approaches:

A. TRACK A SMALL REQUIRED CONTRACT/EVIDENCE ARTIFACT

B. REGENERATE THE REQUIRED EVIDENCE DETERMINISTICALLY FROM TRACKED INPUTS

C. CHANGE READINESS SO THE HISTORICAL LOCAL ARTIFACT IS NO LONGER A
   RUNTIME REQUIREMENT

D. MAKE MISSING OPTIONAL/HISTORICAL EVIDENCE RETURN AN HONEST BLOCKED
   RESULT INSTEAD OF RAISING FileNotFoundError

E. A NARROW COMBINATION OF THE ABOVE

Choose the smallest architecturally correct solution.

Selection criteria, in priority order:

1. semantic correctness;
2. fresh-clone reproducibility;
3. deterministic behavior;
4. no real legacy-data dependency;
5. no real AI dependency;
6. historical integrity;
7. security/privacy;
8. minimal behavioral change;
9. maintainability;
10. repository size.

Do NOT optimize merely for making tests green.

---

# 7. PROHIBITED SHORTCUTS

Do NOT:

- recreate a fake ARCHITECTURE_EVIDENCE.json just to satisfy hashes;
- copy real IST/pilot data into Git;
- weaken tests without semantic justification;
- skip readiness checks to obtain READY;
- hardcode READY;
- delete failing tests;
- alter expected hashes merely to make integrity tests pass;
- rewrite V4.2 closure history;
- reintroduce heavy V1/V2/V3/V4 operational output;
- globally unignore output/;
- call a real LLM provider;
- access IST/Operacional;
- start V5;
- fix unrelated technical debt.

---

# 8. HISTORICAL MANIFEST PROBLEM

Treat the V4.2 final manifest carefully.

If:

output/v4_2_r8/V4_2_FINAL_MANIFEST.json

references a file that was never tracked and therefore cannot exist in a
fresh clone, document that as a historical closure reproducibility defect.

Do NOT silently change the historical V4.2 manifest.

Prefer preserving it as historical evidence.

If current verification needs to distinguish:

HISTORICAL_MANIFEST_VERIFICATION

from:

CURRENT_REPOSITORY_VERIFICATION

implement/document that distinction explicitly and minimally.

A historical manifest is allowed to describe the historical closure
environment.

It must not falsely imply that every referenced local artifact is part of
the current Git snapshot.

---

# 9. READINESS SEMANTICS

Inspect the intended contract of:

python main.py readiness

A missing expected evidence file must never cause an uncontrolled
FileNotFoundError if the command can instead report an honest structured
state.

Determine whether the correct result is:

READY

or:

BLOCKED

based on available tracked evidence and the actual readiness contract.

Never manufacture READY.

If the required readiness evidence can be made reproducibly available from
tracked/deterministic inputs, READY may be correct.

If genuinely required evidence remains unavailable, readiness must report
BLOCKED cleanly and explain why.

The goal is not "force READY".

The goal is:

DETERMINISTIC + HONEST + FRESH-CLONE-SAFE.

---

# 10. TEST COUNT INVESTIGATION

The documentation round ran:

1625 tests

while the historical closure recorded:

1809 tests.

Investigate this difference independently of the 21 failures/errors.

Determine:

- whether 1809 represented unittest test cases while the current discovery
  really contains only 1625;
- whether test modules/cases were accidentally removed;
- whether historical generated tests/fixtures affected discovery;
- whether counting methodology changed;
- whether cleanup removed something tests depended on;
- whether the historical count was environment-dependent;
- whether current test discovery is incomplete.

Do NOT assume that fixing the 21 failures will restore the count to 1809.

Report:

HISTORICAL_TEST_COUNT=1809

CURRENT_DISCOVERED_TEST_COUNT=<verified>

TEST_COUNT_DIFFERENCE_EXPLAINED=true/false

If unexplained:

STOP before versioning.

A clean passing suite with unexplained missing test coverage is not
sufficient.

---

# 11. GEMINI PROVIDER

The documentation round also discovered:

legacy_documenter/llm/providers/gemini.py

exists, while:

ProviderRegistry.create

only exposes FAKE and COPILOT.

Do NOT fix this in this round unless it is directly responsible for
fresh-clone reproducibility.

Record it as existing debt:

AI-01

and leave it for V5/provider-agnostic architecture work.

---

# 12. IMPLEMENTATION BOUNDARY

Production/test changes ARE allowed in this round only when necessary to
correct fresh-clone reproducibility.

Allowed areas include, if justified:

- readiness handling;
- deterministic evidence reconstruction;
- narrow test corrections/additions;
- current verification tooling;
- generated-artifact policy;
- .gitignore if a small required tracked artifact needs a narrowly scoped
  exception.

Avoid touching:

- scanners;
- extractors;
- flow resolution;
- database resolution;
- documentation rendering;
- AI interpretation;
- proposals;
- approval;
- canonical knowledge;
- R11/R12;
- Plugin contracts;

unless diagnosis proves direct involvement.

---

# 13. REGRESSION REQUIREMENT

After correction, execute:

python -m unittest discover -s tests

exactly once for the final authoritative verification.

Do not repeatedly modify/rerun until green without documenting intermediate
failures.

Before the authoritative final run, targeted tests may be used during
development.

The final report must distinguish:

TARGETED_DEVELOPMENT_TESTS

from:

FINAL_AUTHORITATIVE_FULL_SUITE

If the final full suite fails:

STOP.

Do not commit.

Report exact failures.

---

# 14. READINESS VERIFICATION

After correction execute:

python main.py readiness

Record:

EXIT_CODE
STATUS
CHECKS
ERRORS

Expected:

no uncaught exception.

READY is preferred only if supported by actual reproducible evidence.

BLOCKED is acceptable if semantically correct and fully explained, but in
that case:

FRESH_CLONE_REPRODUCIBILITY

may still PASS if the command behaves correctly and the missing evidence is
an intentional/documented condition.

However, assess whether BLOCKED would prevent V5 continuity.

---

# 15. REPOSITORY SIZE / DATA SAFETY

Verify correction does not materially undo the cleanup.

Report:

TRACKED_CONTENT_SIZE_BEFORE
TRACKED_CONTENT_SIZE_AFTER

No new large operational artifacts.

Any newly tracked evidence artifact must be:

- small;
- non-sensitive;
- justified;
- deterministic or historically authentic;
- necessary.

If >1 MiB:

STOP for Technical Lead review before staging it.

---

# 16. DOCUMENTATION IMPACT

The following documentation-update files are currently awaiting approval:

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md

docs/V4_2/POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY_RESULT.md

Do NOT rewrite these files in this correction round.

Instead create a section in the correction result:

DOCUMENTATION_CHANGES_REQUIRED_AFTER_CORRECTION

List exact sections/claims that will need updating after the correction is
approved.

We will update the manuals in a separate controlled pass.

---

# 17. RESULT DOCUMENTS

Create exactly:

docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION_RESULT.md

and:

docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_VERIFICATION.md

The RESULT document must include:

## STATUS
## STARTING_STATE
## FAILURE_MAP
## ROOT_CAUSE
## ARCHITECTURE_EVIDENCE_ROLE
## TEST_COUNT_INVESTIGATION
## SOLUTIONS_EVALUATED
## SELECTED_SOLUTION
## IMPLEMENTATION
## FILES_CHANGED
## FILES_ADDED
## FILES_DELETED
## TARGETED_DEVELOPMENT_TESTS
## FINAL_AUTHORITATIVE_FULL_SUITE
## READINESS_VERIFICATION
## HISTORICAL_MANIFEST_HANDLING
## FRESH_CLONE_REPRODUCIBILITY
## REPOSITORY_SIZE_IMPACT
## SECURITY
## REAL_PROVIDER_CALLS
## REAL_IST_ACCESSED
## GEMINI_AI_01_STATUS
## DOCUMENTATION_CHANGES_REQUIRED_AFTER_CORRECTION
## V4_2_STATUS
## V5_STATUS
## GIT_STATUS
## DECISION
## NEXT

The VERIFICATION document must provide compact, auditable evidence for:

- test discovery/count;
- final test result;
- readiness result;
- missing-file behavior;
- tracked-file availability;
- Git status;
- repository size;
- no real provider;
- no real IST access;
- no historical rewrite.

---

# 18. EXPECTED SAFETY VALUES

REAL_PROVIDER_CALLS=0

REAL_IST_ACCESSED=false

V4_2_REOPENED=false

V5_IMPLEMENTED=false

PLUGIN_RUNTIME=NOT_IMPLEMENTED

GIT_HISTORY_REWRITTEN=false

HISTORICAL_V4_2_BASELINE_MODIFIED=false

HISTORICAL_V4_2_MANIFEST_MODIFIED=false

---

# 19. GIT

Do NOT commit.

Do NOT push.

The Technical Lead must review the correction first.

Do not modify PROJECT_STATE.json yet.

Do not version the pending manual/glossary changes yet.

At end, git status may contain:

- the pre-existing pending documentation files/prompt;
- this correction prompt;
- the two correction result documents;
- narrowly justified production/test/policy changes from this correction.

Explicitly distinguish pre-existing pending documentation changes from new
correction changes.

---

# 20. STOP CONDITIONS

STOP WITHOUT COMMIT if:

- the 1809 → current test-count difference cannot be explained;
- any failing test has a different unexplained root cause;
- correction requires real IST data;
- correction requires a real AI provider;
- correction requires restoring large deleted operational output;
- correction requires falsifying historical evidence;
- correction requires modifying the historical V4.2 baseline/manifest;
- correction requires >1 MiB of new tracked evidence;
- a security/privacy concern is discovered;
- the final authoritative full suite fails;
- readiness still throws an uncaught exception;
- V5 continuity cannot be established.

Do not hide a STOP condition by weakening tests.

---

# 21. EXPECTED DECISION

On successful correction:

STATUS=COMPLETE

DECISION=POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_READY_FOR_TECHNICAL_LEAD_REVIEW

FRESH_CLONE_REPRODUCIBILITY=PASS

TEST_COUNT_DIFFERENCE_EXPLAINED=true

FINAL_TEST_SUITE=PASS

READINESS_UNCAUGHT_EXCEPTION=false

V4_2_CLOSED=true

V4_2_REOPENED=false

V5_IMPLEMENTED=false

REAL_PROVIDER_CALLS=0

REAL_IST_ACCESSED=false

NEXT=HUMAN_REPRODUCIBILITY_REVIEW

Stop.

Do NOT commit.
Do NOT push.
Do NOT update manuals.
Do NOT start V5.