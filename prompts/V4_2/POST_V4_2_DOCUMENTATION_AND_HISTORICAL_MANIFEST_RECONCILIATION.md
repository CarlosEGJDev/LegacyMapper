# LegacyMapper — Post-V4.2 Documentation and Historical Manifest Reconciliation

## MODE

POST_V4_2_DOCUMENTATION_AND_HISTORICAL_MANIFEST_RECONCILIATION

## MODEL

Claude Opus 4.6

## AUTHORITY

LegacyMapper V4.2 remains formally closed.

The Technical Lead has technically approved the fresh-clone reproducibility
correction for integration, but it has NOT yet been committed/versioned.

Current pending work includes:

1. Post-V4.2 updated User Manual.
2. Post-V4.2 updated Technical Manual.
3. New Post-V4.2 Glossary.
4. Documentation-update result.
5. Fresh-clone reproducibility correction.
6. Fresh-clone reproducibility result/verification.
7. The correction prompt and documentation prompt.

No commit/push has yet been authorized for this combined pending work.

This round must reconcile those changes before final versioning.

This is NOT V4.2-R9.

This does NOT reopen V4.2.

This does NOT implement V5.

---

# 1. AUTHORITATIVE INPUTS

Read before modifying anything:

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md

docs/V4_2/POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY_RESULT.md

docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION_RESULT.md

docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_VERIFICATION.md

output/v4_2_r8/V4_2_FINAL_BASELINE.json

output/v4_2_r8/V4_2_FINAL_MANIFEST.json

output/v3_r8_1/ARCHITECTURE_EVIDENCE.json

PROJECT_STATE.json

.gitignore

docs/GENERATED_ARTIFACT_POLICY.md

docs/PROJECT_RECOVERY.md

and the exact current implementation/tests involved in manifest verification
and readiness.

Current source and current tests take precedence for current behavior.

Historical V4.2 closure artifacts remain authoritative for what happened at
V4.2 closure time.

Do not conflate those two scopes.

---

# 2. CONFIRMED CORRECTION FACTS

The previous correction established:

HISTORICAL_TEST_COUNT=1809

CURRENT_DISCOVERED_TEST_COUNT=1809

TEST_COUNT_DIFFERENCE_EXPLAINED=true

READINESS=READY

READINESS_EXIT_CODE=0

READINESS_UNCAUGHT_EXCEPTION=false

REAL_PROVIDER_CALLS=0

REAL_IST_ACCESSED=false

FRESH_CLONE_REPRODUCIBILITY=PASS

The final correction-round full-suite run was:

1809 tests
1 failure
132 skipped
0 errors

The 132 skips are intentional fresh-clone behavior for four historical test
classes whose original tests require complete real-repository-derived dumps
that cannot honestly be reconstructed from tracked repository data.

The assertions were not removed or weakened.

Those tests execute normally when their required historical real-repository
fixtures exist locally.

The single remaining failure was:

FinalBaselineAndManifestIntegrityTests.test_manifest_hashes_match_referenced_files

Its cause was independently verified:

the V4.2 final manifest pins the V4.2-closure version of:

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md

while that same path currently contains a legitimate pending Post-V4.2
documentation revision.

The committed HEAD version of that manual matched the historical manifest
hash exactly.

Therefore:

THE HISTORICAL V4.2 MANIFEST IS NOT CORRUPT.

THE CURRENT DOCUMENTATION EDIT IS NOT CORRUPT.

THE VERIFICATION SCOPE IS TOO BROAD FOR A POST-CLOSURE MUTABLE DOCUMENT.

---

# 3. PRIMARY OBJECTIVES

This round has two objectives.

## OBJECTIVE A — DOCUMENTATION RECONCILIATION

Update the pending Post-V4.2 manuals/result so they describe the approved
fresh-clone correction accurately.

## OBJECTIVE B — HISTORICAL MANIFEST VERIFICATION SEMANTICS

Correct the current test/verification semantics so that:

- immutable authoritative V4.2 closure artifacts remain hash-verified;
- historical manifest contents remain untouched;
- legitimate Post-V4.2 evolution of mutable documentation does not falsely
  fail historical integrity verification;
- no historical evidence is rewritten;
- no hash is changed merely to make a test pass.

---

# 4. HISTORICAL VS CURRENT SEMANTICS

Establish and document this distinction:

HISTORICAL CLOSURE ARTIFACT

A file/hash describing exactly the state at a closed milestone.

CURRENT LIVE REPOSITORY ARTIFACT

A file that may legitimately evolve after that milestone.

A historical manifest can remain immutable even if a mutable live document
at the same repository path later changes.

The verifier must not confuse:

"current file differs from historical snapshot"

with:

"historical manifest is corrupted."

If the repository already provides a field such as:

authoritative_artifacts

mutable_artifacts

or equivalent semantics in the V4.2 manifest/baseline/contracts, use the
existing contract.

Do NOT invent a parallel contract unnecessarily.

---

# 5. MANIFEST TEST INVESTIGATION

Inspect exactly:

tests/test_v4_2_r8_documentation_at_scale.py

and specifically:

FinalBaselineAndManifestIntegrityTests.test_manifest_hashes_match_referenced_files

Determine:

- what manifest collections/fields it iterates;
- which files are intended immutable;
- which files are mutable/current-state references;
- whether the test currently loops over more than the manifest's
  authoritative immutable set;
- whether an existing `authoritative_artifacts` field already defines the
  correct scope.

Also inspect the code/tool that produced:

output/v4_2_r8/V4_2_FINAL_MANIFEST.json

to confirm intended semantics.

Do not modify anything until this is established.

---

# 6. EXPECTED NARROW TEST CORRECTION

If source inspection confirms that the existing manifest already distinguishes
authoritative immutable artifacts from mutable/reference artifacts, make the
smallest possible correction:

The historical hash-integrity test must validate ONLY the manifest collection
that the manifest contract itself defines as immutable/authoritative.

For example, if the contract is:

manifest["authoritative_artifacts"]

then the test should iterate exactly that collection.

Do not hardcode:

"ignore the user manual"

or any individual filename.

Do not special-case Post-V4.2 filenames.

Do not remove hash verification.

Do not change expected hashes.

Do not modify the V4.2 final manifest.

Do not modify the V4.2 final baseline.

The fix must be semantic/contract-driven.

If the manifest does NOT already provide enough information to distinguish
these scopes:

STOP and report.

Do not invent a new historical contract in this round without Technical Lead
review.

---

# 7. ARCHITECTURE_EVIDENCE DOCUMENTATION

Update the documentation to reflect:

output/v3_r8_1/ARCHITECTURE_EVIDENCE.json

is now a deliberately tracked narrow exception.

Document its role accurately:

- small contract/readiness evidence;
- approximately 1.8 KiB;
- aggregate structural indicators only;
- no source code;
- no source paths;
- no credentials;
- no PII;
- historically authentic values sourced from already tracked historical
  evidence;
- not a restored raw IST dump;
- full `output/v3_r8_1/` remains excluded except for this explicit file.

Do not claim it can be regenerated from the repository alone.

Its original generation depended on a real legacy scan.

---

# 8. READINESS DOCUMENTATION

Update the User Manual and Technical Manual.

Remove/replace the previous fresh-clone warning that stated:

python main.py readiness

fails with FileNotFoundError because ARCHITECTURE_EVIDENCE.json is absent.

Current behavior after the correction is:

python main.py readiness

EXIT_CODE=0
READINESS=READY
all eight checks=true
provider_calls=0
real_llm_calls=0

Explain why this is now reproducible.

Also document residual hardening debt:

`readiness.py` still assumes the tracked contract artifact exists.

If a user manually deletes/corrupts that tracked artifact, the current
implementation may still expose insufficient missing-input handling.

Do NOT implement this hardening in this round unless an existing test change
requires it directly.

Record it as future hardening/debt.

---

# 9. TEST ARCHITECTURE DOCUMENTATION

Update the Technical Manual to describe the current fresh-clone test behavior.

Historical V4.2 closure:

1809 PASS
0 FAIL
0 SKIP

Current Post-V4.2 fresh-clone expectation after this correction:

1809 discovered tests.

Four historical test classes conditionally require untracked real-repository
dumps.

On a fresh clone their methods are reported as explicit SKIP rather than
uncontrolled setUpClass ERROR.

Current conditional skips total:

132

when those real-repository fixtures are absent.

Explain that:

- no test method was deleted;
- no assertion was weakened;
- the tests run normally when the original local fixture exists;
- this is deliberate separation between repository-reproducible verification
  and historical real-repository-dependent verification.

Do not present:

1809 PASS / 0 SKIP

as the current expected fresh-clone result.

---

# 10. TEST COUNT EXPLANATION

Document the 1625 → 1809 investigation where appropriate in the Technical
Manual/result, but do not overburden the User Manual.

The reason was:

when unittest setUpClass raises, unittest reports one synthetic class error and
does not count each test method.

Six affected classes caused 184 test methods to collapse into six counted
error entries.

After controlled handling:

1809 methods are discovered/countable again.

This was not test deletion.

---

# 11. REAL-REPOSITORY FIXTURE POLICY

Update:

docs/GENERATED_ARTIFACT_POLICY.md

and/or:

docs/PROJECT_RECOVERY.md

only if necessary to make the current policy explicit.

At minimum document the narrow exception:

output/v3_r8_1/ARCHITECTURE_EVIDENCE.json

is tracked contract evidence.

The rest of:

output/v3_r8_1/

remains operational/heavy output and must remain excluded.

Likewise, full historical dumps such as:

output/v2_r5_1_full/

remain untracked.

Do NOT make the policy suggest that all historical scan output should be
tracked.

Do NOT restore any deleted dump.

---

# 12. AI-01

Keep documented:

AI-01

Current state:

GeminiProvider exists.

ProviderRegistry currently exposes only FAKE/COPILOT.

Do NOT fix it here.

It remains candidate work for V5 runtime AI/provider/model agnosticism.

---

# 13. DOCUMENTS TO UPDATE

Update:

docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md

docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md

docs/V4_2/POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY_RESULT.md

If justified by §11, narrowly update:

docs/GENERATED_ARTIFACT_POLICY.md

docs/PROJECT_RECOVERY.md

Do not rewrite unrelated sections.

Preserve the detailed module/file/audit structure already produced.

---

# 14. NEW RESULT DOCUMENT

Create:

docs/V4_2/POST_V4_2_DOCUMENTATION_AND_HISTORICAL_MANIFEST_RECONCILIATION_RESULT.md

Required sections:

## STATUS

## INPUT_STATE

## HISTORICAL_VS_CURRENT_SEMANTICS

## MANIFEST_CONTRACT_INSPECTION

## MANIFEST_TEST_ROOT_CAUSE

## TEST_CORRECTION

## FILES_CHANGED

## DOCUMENTATION_RECONCILIATION

## ARCHITECTURE_EVIDENCE_DOCUMENTATION

## READINESS_DOCUMENTATION

## TEST_ARCHITECTURE_DOCUMENTATION

## GENERATED_ARTIFACT_POLICY

## AI_01_STATUS

## TARGETED_TESTS

## FINAL_AUTHORITATIVE_FULL_SUITE

## READINESS_VERIFICATION

## HISTORICAL_BASELINE_INTEGRITY

## HISTORICAL_MANIFEST_INTEGRITY

## CURRENT_REPOSITORY_VERIFICATION

## REAL_PROVIDER_CALLS

## REAL_IST_ACCESSED

## PRODUCTION_CODE_CHANGED

## TESTS_CHANGED

## V4_2_STATUS

## V5_STATUS

## GIT_STATUS

## DECISION

## NEXT

---

# 15. TESTING

Targeted tests may be used during development.

After all documentation and narrow test corrections are complete, execute
exactly one final authoritative full-suite run:

python -m unittest discover -s tests

Expected current clean-repository semantics:

DISCOVERED=1809
FAILURES=0
ERRORS=0
SKIPPED=132

provided the four real-repository-dependent fixture families are absent.

If those real fixtures happen to exist locally, skip count may be lower.

Therefore the strict requirements are:

DISCOVERED=1809
FAILURES=0
ERRORS=0

and:

ALL_SKIPS_EXPLAINED=true

Do not force the skip count.

Also execute:

python main.py readiness

Expected:

EXIT_CODE=0
READINESS=READY
provider_calls=0
real_llm_calls=0

---

# 16. IMPORTANT MANIFEST TEST DETAIL

The final full-suite run occurs while the Post-V4.2 manuals are modified.

Therefore:

if the manifest-integrity test has been corrected according to the manifest's
existing immutable/authoritative contract, legitimate pending documentation
changes must no longer cause a false historical-integrity failure.

This is the principal acceptance test for the manifest reconciliation.

If the only way to make it pass is to modify:

output/v4_2_r8/V4_2_FINAL_MANIFEST.json

or:

output/v4_2_r8/V4_2_FINAL_BASELINE.json

STOP.

Do not modify them.

---

# 17. PRODUCTION BOUNDARY

Expected:

PRODUCTION_CODE_CHANGED=false

Only test semantics, documentation, policy, and the already-pending
fresh-clone correction should be involved.

Do NOT modify:

legacy_documenter/**

unless investigation discovers that the manifest contract cannot be respected
without a production correction.

If production modification appears necessary:

STOP for Technical Lead review before making it.

---

# 18. HISTORICAL INTEGRITY

Must remain:

V4_2_FINAL_BASELINE_MODIFIED=false

V4_2_FINAL_MANIFEST_MODIFIED=false

V4_2_CLOSURE_DOCUMENTS_REWRITTEN=false

GIT_HISTORY_REWRITTEN=false

The historical closure remains historical evidence.

Post-V4.2 documentation may evolve.

---

# 19. PROJECT STATE

Do NOT modify:

PROJECT_STATE.json

yet.

The combined Post-V4.2 work has not been versioned.

PROJECT_STATE will be updated only in the final approval/versioning round
after Technical Lead review.

---

# 20. GIT

Do NOT commit.

Do NOT push.

Do not stage files merely for convenience.

The Technical Lead will review the reconciled state first.

Preserve all currently pending correction/documentation files.

---

# 21. SECURITY

REAL_PROVIDER_CALLS=0

REAL_IST_ACCESSED=false

No heavy real-system output restored.

No secrets introduced.

No source-derived operational content added beyond the already-approved
1803-byte architecture contract evidence.

---

# 22. STOP CONDITIONS

STOP if:

- the manifest does not already distinguish authoritative/immutable artifacts
  sufficiently to make a contract-driven test correction;
- correcting the test requires changing historical hashes;
- correcting the test requires modifying the V4.2 final baseline/manifest;
- a production-code modification becomes necessary;
- final suite has any failure or error;
- test discovery is not 1809 and the difference is unexplained;
- a skip is unexplained;
- readiness is not READY/exit 0;
- readiness makes a real provider call;
- real IST access would be required;
- any heavy historical output would need restoration;
- historical closure evidence would need rewriting.

Do not bypass a STOP by weakening assertions.

---

# 23. EXPECTED SUCCESS STATE

STATUS=COMPLETE

DECISION=POST_V4_2_DOCUMENTATION_AND_MANIFEST_RECONCILIATION_READY_FOR_TECHNICAL_LEAD_REVIEW

CURRENT_TEST_DISCOVERY=1809

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

V4_2_FINAL_BASELINE_MODIFIED=false

V4_2_FINAL_MANIFEST_MODIFIED=false

NEXT=HUMAN_FINAL_POST_V4_2_REVIEW

Stop.

Do NOT commit.
Do NOT push.
Do NOT start V5.