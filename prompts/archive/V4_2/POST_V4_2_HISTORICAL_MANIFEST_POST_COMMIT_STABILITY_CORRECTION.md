# LegacyMapper — Post-V4.2 Historical Manifest Post-Commit Stability Correction

## MODE

POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_CORRECTION

## MODEL

Claude Opus 4.6

## AUTHORITY

LegacyMapper V4.2 remains formally closed.

The Technical Lead reviewed the previous reconciliation round and found one
remaining logical defect in the historical-manifest integrity verification.

No commit/push has been authorized yet.

This is a narrow Post-V4.2 correction.

It does NOT reopen V4.2.

It does NOT implement V5.

It does NOT authorize broad refactoring.

---

# 1. CONFIRMED PROBLEM

The previous reconciliation changed:

tests/test_v4_2_r8_documentation_at_scale.py

so that historical authoritative artifacts are verified like this:

- if the working-tree file differs from HEAD:
  hash HEAD content;
- otherwise:
  hash current disk bytes.

This passes today only because the Post-V4.2 manuals are still uncommitted.

However, after the pending documentation is committed:

HEAD will contain the new Post-V4.2 manual content.

Then:

git diff HEAD -- <manual>

will report no difference.

The test will hash current disk/HEAD-equivalent content.

That content is intentionally different from the historical V4.2 closure
snapshot recorded in:

output/v4_2_r8/V4_2_FINAL_MANIFEST.json

Therefore the test would fail again immediately after the final commit.

This means the current solution is not post-commit stable.

---

# 2. PRIMARY OBJECTIVE

Make historical V4.2 manifest integrity verification stable across future
commits.

Required property:

A file may legitimately evolve after V4.2 closure.

The V4.2 historical manifest must still remain verifiable as evidence of the
V4.2 closure state.

Verification must NOT depend on whether the current working tree is dirty or
clean.

Verification must NOT depend on current HEAD containing the historical file
content.

The final semantics must survive:

V4.2 closure
→ later legitimate edits
→ later commit
→ fresh clone
→ historical V4.2 integrity verification

without false failure.

---

# 3. NON-NEGOTIABLE HISTORICAL RULE

Do NOT modify:

output/v4_2_r8/V4_2_FINAL_MANIFEST.json

output/v4_2_r8/V4_2_FINAL_BASELINE.json

or any recorded V4.2 historical hash.

Do NOT rewrite V4.2 closure documents.

Do NOT reinterpret the historical hashes as current-state hashes.

The historical manifest is immutable evidence.

---

# 4. DIAGNOSIS FIRST

Inspect:

tests/test_v4_2_r8_documentation_at_scale.py

tools/v4_2_r8_build_final_artifacts.py

output/v4_2_r8/V4_2_FINAL_MANIFEST.json

output/v4_2_r8/V4_2_FINAL_BASELINE.json

the Git history around the V4.2 closure commit

docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md

and the previous reconciliation result:

docs/V4_2/POST_V4_2_DOCUMENTATION_AND_HISTORICAL_MANIFEST_RECONCILIATION_RESULT.md

Determine exactly:

- what artifact state the historical hashes represent;
- which Git commit corresponds to the V4.2 closure state;
- whether that closure commit is deterministically identifiable from tracked
  repository evidence;
- whether historical artifact bytes can be retrieved from Git history;
- whether line-ending normalization/autocrlf affects comparisons;
- whether verification should use Git blob bytes, working-tree bytes, or a
  normalized representation;
- how to avoid depending on current HEAD.

Do not modify the test until the historical reference point is proven.

---

# 5. REQUIRED SEMANTIC MODEL

The verification must explicitly distinguish:

HISTORICAL_ARTIFACT_CONTENT

from:

CURRENT_REPOSITORY_CONTENT

Historical integrity means:

"The content recorded at the historical V4.2 closure reference still matches
the hashes stored in the V4.2 manifest."

It does NOT mean:

"The current repository file must forever equal the V4.2 version."

---

# 6. HISTORICAL REFERENCE

Determine the safest stable historical reference.

Preferred evidence order:

1. explicit V4.2 closure commit recorded in tracked closure documentation;
2. explicit commit recorded in PROJECT_STATE/history artifact;
3. deterministic Git-history resolution tied to the V4.2 closure artifact;
4. another already-existing immutable repository contract.

Do NOT:

- assume current HEAD;
- assume HEAD~1;
- hardcode an arbitrary commit discovered only from the local environment
  unless it is already evidenced in repository history/contracts;
- use branch-relative offsets;
- depend on working-tree state.

If no deterministic historical reference exists:

STOP and report.

Do not invent one silently.

---

# 7. EXPECTED TEST DESIGN

If the historical V4.2 closure commit can be deterministically identified,
historical authoritative-artifact verification should conceptually be:

historical_commit
+
artifact_path
→ retrieve historical content
→ compute equivalent historical hash
→ compare to manifest hash

The implementation may differ if line-ending normalization requires a safer
approach.

The verifier must be stable when:

- the current working tree is dirty;
- the current working tree is clean;
- the current HEAD has a newer version of the same path;
- a fresh clone checks out the current repository.

Current HEAD must not be used as the historical authority.

---

# 8. LINE ENDING / AUTOCRLF REQUIREMENT

The previous round found:

core.autocrlf=true

and observed that:

git show <commit>:<path>

may return LF blob bytes while working-tree content may contain CRLF.

Do not reintroduce false failures caused solely by representation differences.

Investigate how the original V4.2 manifest hashes were generated:

- from working-tree bytes;
- from Git blob bytes;
- or from normalized content.

The correction must reproduce the SAME representation semantics used when the
manifest was created.

Do not simply normalize everything unless the original manifest contract did
so.

If exact historical working-tree byte reproduction is impossible from Git
history alone because the manifest hashed post-checkout transformed bytes,
determine whether a deterministic equivalent can be reconstructed from the
historical blob + repository attributes/config.

If not safely solvable:

STOP and report.

Do not weaken integrity.

---

# 9. REQUIRED POST-COMMIT STABILITY TEST

Add or update tests so this exact scenario is explicitly protected:

V4.2 historical manifest exists.

An authoritative artifact path later contains new legitimate content.

That new content is considered committed/current state.

Historical verification still validates the historical V4.2 snapshot rather
than the newer current content.

The test must NOT require performing a real Git commit in the user's
repository.

Use a deterministic isolated fixture/mock/temp Git repository only if needed.

The test must prove:

POST_COMMIT_STABILITY=PASS

It is not sufficient to test only a dirty working tree.

---

# 10. CURRENT-STATE VERIFICATION

Do not remove useful current-repository checks.

If appropriate, keep separate semantics:

HISTORICAL_MANIFEST_INTEGRITY

and:

CURRENT_REPOSITORY_VALIDITY

But do not mix them.

For historical authoritative artifacts:

historical content/hash belongs to historical verification.

For mutable current-state documents:

follow the manifest contract already present.

For current repository health:

use current tests/readiness/current contracts, not a historical hash snapshot.

---

# 11. PROHIBITED SOLUTIONS

Do NOT:

- compare against current HEAD as historical authority;
- compare only if git diff says dirty;
- hardcode manual filenames;
- update manifest hashes;
- replace historical hashes with current hashes;
- skip historical hash checking;
- mark authoritative files mutable merely to make tests pass;
- ignore line-ending differences without understanding them;
- disable the test;
- delete assertions;
- rewrite historical Git commits;
- change production code;
- access real IST;
- call a real AI provider;
- start V5.

---

# 12. IMPLEMENTATION BOUNDARY

Expected changed area:

tests/test_v4_2_r8_documentation_at_scale.py

Possibly:

small test helper code local to tests

Only if strictly necessary.

Expected:

PRODUCTION_CODE_CHANGED=false

Do NOT modify:

legacy_documenter/**

If production changes appear necessary:

STOP for Technical Lead review.

---

# 13. DOCUMENTATION

Do NOT modify the three manuals unless the final technical semantics differ
materially from what they currently state.

If documentation must change:

report exact required sections first.

Do not broadly rewrite them.

The preferred outcome is:

MANUALS_CHANGED=false

because this round should primarily stabilize test semantics.

---

# 14. TARGETED TESTING

During development, run targeted tests covering:

- historical manifest integrity;
- mutable current-state document handling;
- dirty working-tree case;
- clean working-tree case;
- later-committed/current-content case;
- line-ending/autocrlf behavior if applicable.

Report each targeted test run.

---

# 15. FINAL AUTHORITATIVE FULL SUITE

After the final correction, execute exactly one final full suite:

python -m unittest discover -s tests

Expected:

DISCOVERED=1809
FAILURES=0
ERRORS=0

Skips may remain:

132

if the four real-repository-dependent fixture groups remain absent.

Requirements:

ALL_SKIPS_EXPLAINED=true

No real provider.

No real IST.

---

# 16. READINESS

Execute:

python main.py readiness

Expected:

EXIT_CODE=0
READINESS=READY
provider_calls=0
real_llm_calls=0

No uncaught exception.

---

# 17. POST-COMMIT STABILITY VERIFICATION

Without committing the real repository, explicitly demonstrate that the new
historical verifier does not depend on current HEAD containing historical
content.

Provide evidence for:

POST_COMMIT_STABILITY=PASS

The verification must demonstrate a state equivalent to:

historical V4.2 content at path X
→ later committed content at same path X
→ historical V4.2 manifest still validates historical content.

---

# 18. RESULT DOCUMENTS

Create exactly:

docs/V4_2/POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_CORRECTION_RESULT.md

and:

docs/V4_2/POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_VERIFICATION.md

---

# 19. CORRECTION RESULT REQUIRED SECTIONS

## STATUS

## STARTING_PROBLEM

## HISTORICAL_REFERENCE_INVESTIGATION

## V4_2_CLOSURE_REFERENCE

## ORIGINAL_MANIFEST_HASH_SEMANTICS

## AUTOCRLF_AND_LINE_ENDING_ANALYSIS

## SELECTED_SOLUTION

## WHY_CURRENT_HEAD_IS_NOT_USED

## IMPLEMENTATION

## FILES_CHANGED

## TESTS_ADDED_OR_CHANGED

## DIRTY_WORKTREE_CASE

## CLEAN_WORKTREE_CASE

## POST_COMMIT_SIMULATION_CASE

## TARGETED_TESTS

## FINAL_AUTHORITATIVE_FULL_SUITE

## READINESS_VERIFICATION

## HISTORICAL_MANIFEST_INTEGRITY

## HISTORICAL_BASELINE_INTEGRITY

## POST_COMMIT_STABILITY

## CURRENT_REPOSITORY_VALIDITY

## MANUALS_CHANGED

## PRODUCTION_CODE_CHANGED

## REAL_PROVIDER_CALLS

## REAL_IST_ACCESSED

## V4_2_STATUS

## V5_STATUS

## GIT_STATUS

## DECISION

## NEXT

---

# 20. VERIFICATION DOCUMENT

The verification document must be compact and auditable.

Include:

- historical V4.2 reference used;
- how it was resolved;
- representative historical artifact hash verification;
- dirty-working-tree test;
- clean-working-tree test;
- simulated later-commit test;
- line-ending behavior;
- final full-suite result;
- readiness result;
- Git status;
- no real provider;
- no IST access;
- no historical artifact modification.

---

# 21. REQUIRED SAFETY VALUES

PRODUCTION_CODE_CHANGED=false

REAL_PROVIDER_CALLS=0

REAL_IST_ACCESSED=false

V4_2_REOPENED=false

V5_IMPLEMENTED=false

V4_2_FINAL_BASELINE_MODIFIED=false

V4_2_FINAL_MANIFEST_MODIFIED=false

GIT_HISTORY_REWRITTEN=false

PROJECT_STATE_MODIFIED=false

---

# 22. PROJECT STATE

Do NOT modify:

PROJECT_STATE.json

The final combined Post-V4.2 block is not yet approved/versioned.

---

# 23. GIT

Do NOT commit.

Do NOT push.

Do NOT rewrite Git history.

Do not stage files merely for convenience.

The Technical Lead must review this correction first.

---

# 24. STOP CONDITIONS

STOP if:

- the V4.2 closure historical reference cannot be deterministically identified;
- historical hash representation cannot be reproduced safely;
- solving the issue requires changing historical hashes;
- solving the issue requires modifying the historical manifest/baseline;
- the solution still depends on current HEAD;
- the solution still depends on dirty/clean working-tree state;
- line-ending behavior remains ambiguous;
- production code must change;
- final full suite has any failure/error;
- test count differs from 1809 without explanation;
- readiness is not READY/exit 0;
- real IST access would be required;
- real AI provider would be required.

Do not bypass a STOP by weakening assertions.

---

# 25. EXPECTED SUCCESS STATE

STATUS=COMPLETE

DECISION=POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_READY_FOR_TECHNICAL_LEAD_REVIEW

POST_COMMIT_STABILITY=PASS

HISTORICAL_MANIFEST_INTEGRITY=PASS

CURRENT_TEST_DISCOVERY=1809

CURRENT_TEST_FAILURES=0

CURRENT_TEST_ERRORS=0

ALL_SKIPS_EXPLAINED=true

READINESS=READY

READINESS_EXIT_CODE=0

PRODUCTION_CODE_CHANGED=false

REAL_PROVIDER_CALLS=0

REAL_IST_ACCESSED=false

V4_2_CLOSED=true

V4_2_REOPENED=false

V5_IMPLEMENTED=false

NEXT=HUMAN_POST_COMMIT_STABILITY_REVIEW

Stop.

Do NOT commit.
Do NOT push.
Do NOT start V5.