# LegacyMapper — Post-V4.2 Final Approval and Versioning

## MODE

POST_V4_2_FINAL_APPROVAL_AND_VERSIONING

## MODEL

Claude Opus 4.6

## AUTHORITY

The Technical Lead has reviewed and APPROVED the complete Post-V4.2
maintenance/documentation block for final integration and versioning.

LegacyMapper V4.2 remains formally closed.

This task does NOT reopen V4.2.

This task does NOT implement V5.

Its purpose is to:

1. perform final consistency verification;
2. correct one verified editorial arithmetic inconsistency if confirmed;
3. update repository continuity state;
4. commit all approved Post-V4.2 work as one controlled integration;
5. push it;
6. verify the repository AFTER the real commit;
7. leave the repository clean and ready for V5 design.

---

# 1. APPROVED POST-V4.2 BLOCK

The approved block includes the repository cleanup already completed and
versioned previously, plus the currently uncommitted work from these rounds:

## Documentation update

prompts/V4_2/POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY.md

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md

docs/V4_2/POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY_RESULT.md

## Fresh-clone reproducibility correction

prompts/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION.md

docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION_RESULT.md

docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_VERIFICATION.md

output/v3_r8_1/ARCHITECTURE_EVIDENCE.json

.gitignore

tests/test_v3_r7_2.py
tests/test_v3_r7_2_4.py
tests/test_v3_r8_2.py
tests/test_v3_r8_2_correction.py

## Documentation / historical manifest reconciliation

prompts/V4_2/POST_V4_2_DOCUMENTATION_AND_HISTORICAL_MANIFEST_RECONCILIATION.md

docs/V4_2/POST_V4_2_DOCUMENTATION_AND_HISTORICAL_MANIFEST_RECONCILIATION_RESULT.md

tests/test_v4_2_r8_documentation_at_scale.py

docs/GENERATED_ARTIFACT_POLICY.md

docs/PROJECT_RECOVERY.md

## Historical manifest post-commit stability correction

prompts/V4_2/POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_CORRECTION.md

docs/V4_2/POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_CORRECTION_RESULT.md

docs/V4_2/POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_VERIFICATION.md

The actual git diff/status is authoritative.

Do not invent a missing change merely because it appears in this inventory.

---

# 2. APPROVAL STATE

Technical Lead decision:

POST_V4_2_BLOCK=APPROVED_FOR_VERSIONING

Approved technical state:

POST_COMMIT_STABILITY=PASS

HISTORICAL_MANIFEST_INTEGRITY=PASS

READINESS=READY

CURRENT_TEST_DISCOVERY=1810

CURRENT_TEST_FAILURES=0

CURRENT_TEST_ERRORS=0

CURRENT_TEST_SKIPS=132

ALL_SKIPS_EXPLAINED=true

REAL_PROVIDER_CALLS=0

REAL_IST_ACCESSED=false

PRODUCTION_CODE_CHANGED=false

V4_2_REOPENED=false

V5_IMPLEMENTED=false

---

# 3. IMPORTANT HISTORICAL INVARIANTS

Do NOT modify:

output/v4_2_r8/V4_2_FINAL_BASELINE.json

output/v4_2_r8/V4_2_FINAL_MANIFEST.json

historical V4.2 closure hashes

historical V4.2 closure decisions.

The historical V4.2 closure commit remains:

af7e2099039e791c5a14ff94bf5ad348e8dbb4db

The current repository is moving forward from that historical state.

---

# 4. SMALL EDITORIAL CORRECTION TO VERIFY

The Technical Lead identified one possible arithmetic inconsistency in:

docs/V4_2/POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_VERIFICATION.md

The document currently states approximately:

"All 28 authoritative_artifacts entries verified OK"

and also:

"26 against raw historical blob, 4 against CRLF-converted form"

26 + 4 = 30.

Before editing, inspect the actual manifest and verification result.

Determine the correct counts.

If this is only an editorial counting typo:

correct ONLY the incorrect count(s).

Do not change the technical conclusion.

Do not change manifest content.

Do not rerun architecture work.

Record the correction in the final result.

If the apparent arithmetic mismatch reflects an actual verification defect
rather than a typo:

STOP before commit and report.

---

# 5. PROJECT_STATE UPDATE

Update:

PROJECT_STATE.json

to describe the CURRENT repository after this approved Post-V4.2 block.

Preserve:

V4_CLOSED=true
V4_1_CLOSED=true
V4_2_CLOSED=true

current_version_status must continue to communicate that V4.2 is formally
closed.

Do NOT invent V4.3.

Do NOT mark V5 implemented.

Set/record, using the existing PROJECT_STATE structure rather than inventing
unnecessary parallel fields, the equivalent of:

POST_V4_2_MAINTENANCE_STATUS=COMPLETE

POST_V4_2_DOCUMENTATION=APPROVED

POST_V4_2_FRESH_CLONE_REPRODUCIBILITY=PASS

POST_V4_2_HISTORICAL_MANIFEST_STABILITY=PASS

TESTS=1810

TEST_FAILURES=0

TEST_ERRORS=0

EXPECTED_FRESH_CLONE_SKIPS=132

READINESS=READY

PLUGIN_RUNTIME=NOT_IMPLEMENTED

V5_IMPLEMENTED=false

NEXT=V5_DESIGN_PENDING

Preserve known unresolved debt, including at minimum where still applicable:

- F05 deferred-by-determinism-contract;
- F06 preserved observation;
- F07 preserved observation;
- WEB_ENTRY_POINTS scale debt;
- PROJECT_DEPENDENCIES scale debt;
- technical_documentation_renderer.py maintainability debt;
- readiness missing/corrupt ARCHITECTURE_EVIDENCE defensive handling;
- AI-01: GeminiProvider exists but is not reachable via ProviderRegistry;
- approval surface implementation NOT_IMPLEMENTED;
- Plugin runtime NOT_IMPLEMENTED;
- any older V4.1 debt still explicitly applicable.

Do not mark unrelated debt resolved.

---

# 6. CONTINUITY REVIEW

Review for consistency:

AGENTS.md
CLAUDE.md
PROJECT_STATE.json
docs/PROJECT_RECOVERY.md
docs/GENERATED_ARTIFACT_POLICY.md

Only modify AGENTS.md or CLAUDE.md if the current information is now factually
wrong or insufficient for a new development agent to start V5.

Avoid unnecessary edits.

Required continuity property:

fresh development agent
→ reads CLAUDE.md / AGENTS.md
→ reads PROJECT_STATE.json
→ understands V4/V4.1/V4.2 are closed
→ understands Post-V4.2 maintenance is complete
→ understands current test/readiness semantics
→ starts at V5_DESIGN_PENDING

No conversation memory may be required.

---

# 7. PRE-COMMIT VERIFICATION

Before staging/commit, run targeted checks sufficient to verify:

- the historical-manifest stability test;
- manifest/baseline files remain untouched;
- PROJECT_STATE consistency;
- ARCHITECTURE_EVIDENCE tracked exception;
- no accidental real-system output included;
- no secrets.

Then execute one authoritative PRE-COMMIT full suite:

python -m unittest discover -s tests

Expected:

DISCOVERED=1810
FAILURES=0
ERRORS=0

SKIPS may be 132 when the historical real-repository dumps remain absent.

Require:

ALL_SKIPS_EXPLAINED=true

Then:

python main.py readiness

Expected:

EXIT_CODE=0
READINESS=READY
provider_calls=0
real_llm_calls=0

If anything fails:

STOP.
DO NOT COMMIT.

---

# 8. STAGING SAFETY

Before commit inspect:

git status --short

and:

git diff --stat
git diff
git diff --cached

Stage only approved Post-V4.2 files plus the final continuity/result changes
from this task.

Explicitly ensure no real operational output is staged.

The only allowed file under:

output/v3_r8_1/

is:

output/v3_r8_1/ARCHITECTURE_EVIDENCE.json

Do not stage any other historical dump.

Do not stage:

output/v2_r5_1_full/

or real IST/pilot output.

Report the final staged file inventory.

---

# 9. FINAL RESULT DOCUMENT

Create:

docs/V4_2/POST_V4_2_FINAL_APPROVAL_AND_VERSIONING_RESULT.md

It must include:

## STATUS

## TECHNICAL_LEAD_APPROVAL

## APPROVED_BLOCK

## EDITORIAL_CORRECTION

## FINAL_FILES_INCLUDED

## PROJECT_STATE_UPDATE

## CONTINUITY_STATUS

## PRE_COMMIT_TARGETED_VERIFICATION

## PRE_COMMIT_FULL_SUITE

## PRE_COMMIT_READINESS

## HISTORICAL_BASELINE_INTEGRITY

## HISTORICAL_MANIFEST_INTEGRITY

## POST_COMMIT_STABILITY

## SECURITY

## REAL_PROVIDER_CALLS

## REAL_IST_ACCESSED

## PRODUCTION_CODE_CHANGED

## V4_2_STATUS

## V5_STATUS

## STAGED_FILE_INVENTORY

## GIT_COMMIT

## GIT_PUSH

## POST_COMMIT_FULL_SUITE

## POST_COMMIT_READINESS

## POST_COMMIT_HISTORICAL_MANIFEST_VERIFICATION

## GIT_STATUS_FINAL

## DECISION

## NEXT

---

# 10. COMMIT

After all pre-commit gates pass, commit the entire approved block as one
controlled integration commit.

Suggested commit message:

Post-V4.2 maintenance: documentation and reproducibility hardening

Do not amend the historical V4.2 closure commit.

Do not squash or rewrite history.

Record the exact new commit SHA.

---

# 11. PUSH

Push to the existing configured upstream/main.

Require:

PUSH=PASS

Then verify:

git rev-parse HEAD

and:

git rev-parse origin/main

must be identical.

If push fails:

report it honestly.

Do not claim completion.

---

# 12. CRITICAL POST-COMMIT VERIFICATION

This section is mandatory because the defect fixed in the previous round was
specifically a post-commit stability defect.

After the REAL commit is created, while HEAD now contains the new Post-V4.2
manuals and test logic, execute:

python -m unittest discover -s tests

This is a separate POST-COMMIT authoritative verification.

Expected:

DISCOVERED=1810
FAILURES=0
ERRORS=0

ALL_SKIPS_EXPLAINED=true

Then execute:

python main.py readiness

Expected:

EXIT_CODE=0
READINESS=READY
provider_calls=0
real_llm_calls=0

Also execute the historical manifest integrity test specifically after commit.

It must still pass while:

HEAD != V4.2 closure commit

and the Post-V4.2 manuals are now committed.

This is the real-world confirmation of:

POST_COMMIT_STABILITY=PASS.

If any post-commit verification fails:

DO NOT hide it.

Record:

POST_COMMIT_VERIFICATION=FAILED

and do not mark the maintenance block formally complete.

Do not rewrite the commit unless explicitly authorized later.

---

# 13. FINAL GIT STATE

After successful push and post-commit verification:

git status --short

must be clean.

HEAD == origin/main.

No staging leftovers.

No untracked prompt/result files from this block.

If test/readiness execution creates ignored local runtime artifacts, they are
acceptable only if ignored and do not appear in git status.

---

# 14. SECURITY

Require:

REAL_PROVIDER_CALLS=0

REAL_IST_ACCESSED=false

NO_REAL_OPERATIONAL_OUTPUT_STAGED=true

NO_SECRET_SHAPED_VALUES_INTRODUCED=true

GIT_HISTORY_REWRITTEN=false

---

# 15. PRODUCTION BOUNDARY

Expected:

PRODUCTION_CODE_CHANGED=false

This Post-V4.2 block changed tests, documentation, repository policy/state,
and the small tracked architecture evidence artifact.

No `legacy_documenter/**` production behavior should change.

If production code is unexpectedly in the diff:

STOP before commit unless it is proven to be a pre-approved pending change
from the reviewed block.

---

# 16. SUCCESS STATE

Only if every gate passes:

STATUS=COMPLETE

TECHNICAL_LEAD_APPROVAL=APPROVED

POST_V4_2_MAINTENANCE=FORMALLY_VERSIONED

POST_V4_2_DOCUMENTATION=APPROVED_AND_VERSIONED

FRESH_CLONE_REPRODUCIBILITY=PASS

HISTORICAL_MANIFEST_INTEGRITY=PASS

POST_COMMIT_STABILITY=PASS

CURRENT_TEST_DISCOVERY=1810

CURRENT_TEST_FAILURES=0

CURRENT_TEST_ERRORS=0

ALL_SKIPS_EXPLAINED=true

READINESS=READY

READINESS_EXIT_CODE=0

REAL_PROVIDER_CALLS=0

REAL_IST_ACCESSED=false

PRODUCTION_CODE_CHANGED=false

V4_2_CLOSED=true

V4_2_REOPENED=false

V5_IMPLEMENTED=false

GIT_PUSH=PASS

HEAD_EQUALS_ORIGIN_MAIN=true

GIT_STATUS=CLEAN

DECISION=POST_V4_2_MAINTENANCE_AND_DOCUMENTATION_FORMALLY_CLOSED

NEXT=V5_DESIGN_PENDING

---

# 17. STOP CONDITIONS

STOP before commit if:

- editorial count mismatch reflects a real verification defect;
- pre-commit suite has any failure/error;
- test discovery differs from 1810 without explanation;
- any skip is unexplained;
- readiness is not READY/exit 0;
- historical manifest/baseline has been modified;
- real operational output is staged;
- real provider was called;
- real IST was accessed unexpectedly;
- production code changed unexpectedly;
- security concern appears.

After commit, report FAILED rather than rewriting history if:

- post-commit suite fails;
- historical manifest verification fails;
- readiness fails;
- push fails.

Do not silently amend/rewrite the commit.

---

# 18. END

After successful commit/push/post-commit verification:

stop.

Do NOT start V5 in this same task.

The next independent phase is:

V5_DESIGN_PENDING