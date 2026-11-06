# LegacyMapper — Post-V4.2 GitHub Repository Cleanup and Versioning

## MODE

POST_V4_2_APPROVED_REPOSITORY_CLEANUP

## MODEL

Claude Opus 4.6

## AUTHORITY

The Technical Lead has reviewed and approved the repository inventory:

docs/V4_2/POST_V4_2_GITHUB_REPOSITORY_INVENTORY_AND_CLEANUP_PLAN_RESULT.md

and:

docs/V4_2/POST_V4_2_GITHUB_REPOSITORY_FILE_INVENTORY.csv

The inventory decision was:

READY_FOR_TECHNICAL_LEAD_CLEANUP_REVIEW

The Technical Lead now explicitly authorizes the controlled cleanup described below.

V4.2 remains formally closed.

DO NOT reopen V4.2.
DO NOT implement V5.
DO NOT modify production behavior.

---

# 1. APPROVED TECHNICAL LEAD DECISIONS

The Technical Lead approves:

1. Delete local generated-analysis artifacts classified EXCLUDE by the approved inventory.
2. Preserve every tracked/KEEP file.
3. Preserve:
   output/LEVANTAMIENTO_FUNCIONAL.md
   output/LEVANTAMIENTO_TECNICO.md
   as historical evidence (KEEP).
4. Add explicit .gitignore protection for:
   /output/v4_2_r7_ist_operacional/
5. Preserve Git history unchanged.
6. Do NOT use git filter-repo.
7. Do NOT use BFG.
8. Do NOT rewrite commits/history.
9. Document a safe convention for future real-system operational outputs.
10. Commit and push only the approved repository-policy/documentation changes after successful validation.

---

# 2. APPROVED CLEANUP SCOPE

The audit measured approximately:

CURRENT_WORKING_TREE_SIZE ~= 9.31 GiB
CURRENT_TRACKED_CONTENT_SIZE ~= 6.79 MB
CURRENT_GIT_DIRECTORY_SIZE ~= 4 MB

Approximately 9.30 GiB consists of generated operational analysis output.

Delete ONLY directories/files already classified EXCLUDE by the approved inventory.

This includes the large generated analysis directories identified by the audit, including:

output/v1_r1_full/
output/v2_r4_full/
output/v2_r4_1_full/
output/v2_r4_1_repro_a/
output/v2_r4_1_repro_b/
output/v2_r5_full/
output/v2_r5_1_full/
output/v2_r5_1_repro/
output/v3_r8_1/
output/v4_2_r7_ist_operacional/

and leftover generated/smoke-test output classified EXCLUDE by the inventory, including where present:

output/context/
output/documentation/
output/index/
output/v1_r1_internal/
output/v2_r4_1_internal/

Python cache directories/files classified EXCLUDE may also be removed:

__pycache__/
*.pyc

ONLY when they are untracked/ignored generated cache.

The approved CSV is authoritative for classification.

Before deleting each candidate:

- confirm it is classified EXCLUDE;
- confirm it is not currently tracked by Git;
- confirm it is not a KEEP artifact;
- confirm it is not one of the two LEVANTAMIENTO files.

If any candidate is tracked unexpectedly:

STOP.

Do not delete it.

---

# 3. ABSOLUTE KEEP RULE

DO NOT delete or modify any file classified KEEP.

In particular preserve:

main.py

legacy_documenter/**

tests/**

tests/fixtures/**

tools/**

docs/**

prompts/**

codex/**

result_codex/**

AGENTS.md

CLAUDE.md

PROJECT_STATE.json

all tracked configuration files

all tracked contract/example artifacts

all tracked baselines/manifests

all historical closure/result documents

all historical prompts

output/LEVANTAMIENTO_FUNCIONAL.md

output/LEVANTAMIENTO_TECNICO.md

and all small tracked output/** artifacts classified KEEP.

DO NOT apply a blanket deletion to output/.

DO NOT apply a blanket .gitignore rule to output/.

The output directory intentionally contains both:

A. operational generated output -> EXCLUDE

B. small development/contract/history artifacts -> KEEP

This distinction is mandatory.

---

# 4. PRE-DELETION SAFETY GATE

Before deleting anything:

1. Run git status.
2. Record HEAD.
3. Record origin/main after git fetch.
4. Confirm no unexpected tracked modifications exist.
5. Confirm each approved EXCLUDE path is untracked or ignored.
6. Confirm KEEP artifacts exist.
7. Confirm:
   output/LEVANTAMIENTO_FUNCIONAL.md
   output/LEVANTAMIENTO_TECNICO.md
   are tracked and will remain untouched.
8. Measure working-tree size before cleanup.
9. Measure tracked-content size.
10. Measure .git size.

If unexpected tracked changes exist:

STOP and report.

Do not attempt to repair, reset, stash, checkout, or discard them automatically.

---

# 5. CLEANUP EXECUTION

After the safety gate passes:

Delete the approved EXCLUDE operational/generated artifacts.

Deletion must operate on explicit approved paths or classifications.

Do NOT use broad destructive patterns such as:

rm -rf output/*
del output\*
git clean -fdx

Do NOT run commands capable of deleting unknown user files outside the approved EXCLUDE set.

Do NOT access the real IST source repository.

Deleting the local generated directory:

output/v4_2_r7_ist_operacional/

is explicitly authorized.

This deletes only LegacyMapper-generated pilot output, NOT the source IST repository.

---

# 6. .GITIGNORE

Modify .gitignore narrowly.

Add:

# Real-system operational pilot output.
# Generated analysis of a concrete legacy system must remain local and must
# never be committed. Distilled findings belong in tracked docs/fixtures.
/output/v4_2_r7_ist_operacional/

Do NOT ignore output/ globally.

Preserve all existing path-specific rules.

Also review whether the existing local-output convention:

/output/_local_*/

or equivalent already exists.

If it exists, preserve it.

If the exact syntax differs, do not unnecessarily rewrite it.

---

# 7. FUTURE REAL-SYSTEM OUTPUT POLICY

Update:

docs/GENERATED_ARTIFACT_POLICY.md

with a concise rule for future analyses.

The policy must establish:

- results generated from a real legacy system are operational output;
- operational output is local and must not be committed;
- prefer a predictable local-output naming convention for ad-hoc/future runs;
- use output/_local_<descriptive-name>/ where practical;
- if a formally named real pilot output directory is required, add an explicit .gitignore rule at the same time the pilot is created;
- findings needed for project history must be distilled into small tracked documentation/tests/synthetic fixtures;
- never solve this by globally ignoring output/ because output/ also contains tracked contracts/baselines/manifests.

Do not rewrite unrelated portions of the policy.

---

# 8. POST-CLEANUP VALIDATION

After deletion:

Verify:

1. Every approved EXCLUDE directory targeted for cleanup is gone.
2. No KEEP file was deleted.
3. No tracked source file was deleted.
4. No tracked test was deleted.
5. No tracked documentation/history was deleted.
6. No tracked prompt was deleted.
7. No tracked contract/baseline/manifest was deleted.
8. Both LEVANTAMIENTO files remain.
9. git diff does not show unexpected deletions.
10. git status contains only the intentionally modified/new repository-policy artifacts.
11. output/v4_2_r7_ist_operacional/ no longer exists locally.
12. .gitignore now protects that path.
13. No real-system operational output is staged.

Measure:

WORKING_TREE_SIZE_BEFORE
WORKING_TREE_SIZE_AFTER
SPACE_RECLAIMED
TRACKED_CONTENT_SIZE_AFTER
GIT_DIRECTORY_SIZE_AFTER

Report human-readable MiB/GiB and bytes when practical.

Expected result:

Working tree should drop from approximately 9.31 GiB to a very small repository-sized working tree.

Do not fail solely because filesystem metadata causes small differences from the audit estimate.

---

# 9. CONTINUITY VALIDATION

Explicitly verify:

"Can a new programmer or agent clone the resulting Git repository and continue with V5 without any deleted local operational output?"

Expected:

YES

Verify availability of:

- agent bootstrap;
- PROJECT_STATE;
- source;
- tests;
- fixtures;
- tools;
- contracts;
- baselines;
- manifests;
- manuals/documentation;
- prompts;
- historical evidence;
- V4.2 final closure;
- known technical debt.

---

# 10. TESTS

Because production code is not being changed, do not modify tests.

A complete 1809-test execution is not required solely for deleting ignored/untracked operational output.

However, after cleanup run an appropriate lightweight repository validation sufficient to establish that:

- Python package imports remain available;
- repository bootstrap files remain available;
- no tracked test fixture was removed;
- V4.2 final baseline/manifest files remain available.

If any validation indicates a KEEP dependency was accidentally removed:

STOP.

Do not commit.

Report the problem.

---

# 11. RESULT DOCUMENT

Create:

docs/V4_2/POST_V4_2_GITHUB_REPOSITORY_CLEANUP_AND_VERSIONING_RESULT.md

It must contain at least:

## STATUS

## TECHNICAL_LEAD_DECISIONS_APPLIED

## PRE_CLEANUP_GIT_STATE

## DELETED_OPERATIONAL_OUTPUTS

## PRESERVED_KEEP_ARTIFACTS

## LEVANTAMIENTO_FILES

## GITIGNORE_CHANGE

## GENERATED_ARTIFACT_POLICY_CHANGE

## WORKING_TREE_SIZE_BEFORE

## WORKING_TREE_SIZE_AFTER

## SPACE_RECLAIMED

## TRACKED_CONTENT_SIZE_AFTER

## GIT_DIRECTORY_SIZE_AFTER

## V5_CONTINUITY_CHECK

## VALIDATION

## SECURITY_CHECK

## FILES_CHANGED

## FILES_DELETED_FROM_GIT

Expected:

NONE

## GIT_HISTORY_REWRITTEN

Expected:

false

## REAL_IST_SOURCE_ACCESSED

Expected:

false

## REAL_PROVIDER_CALLS

Expected:

0

## GIT_COMMIT

## GIT_PUSH

## GIT_STATUS

## DECISION

## NEXT

---

# 12. VERSIONING

Only after all validation passes:

Stage ONLY:

.gitignore

docs/GENERATED_ARTIFACT_POLICY.md

docs/V4_2/POST_V4_2_GITHUB_REPOSITORY_INVENTORY_AND_CLEANUP_PLAN_RESULT.md

docs/V4_2/POST_V4_2_GITHUB_REPOSITORY_FILE_INVENTORY.csv

prompts/V4_2/POST_V4_2_GITHUB_REPOSITORY_INVENTORY_AND_CLEANUP_PLAN.md

prompts/V4_2/POST_V4_2_GITHUB_REPOSITORY_CLEANUP_AND_VERSIONING.md

docs/V4_2/POST_V4_2_GITHUB_REPOSITORY_CLEANUP_AND_VERSIONING_RESULT.md

Some of these audit artifacts may already be tracked depending on how the previous round was executed.

Do not stage anything else.

Before commit:

git diff --cached

Inspect it.

Confirm no generated operational output appears.

Confirm no secret appears.

Confirm no real IST generated content appears.

Then commit with an appropriate Post-V4.2 repository-cleanup message.

Push to origin/main.

Verify:

HEAD == origin/main

and no tracked modifications remain.

Ignored/local caches that were not part of the approved cleanup do not by themselves invalidate the closure.

---

# 13. STOP CONDITIONS

STOP WITHOUT COMMIT if:

- any proposed deletion is tracked;
- any KEEP artifact would be removed;
- V5 continuity becomes NO;
- a required baseline/manifest disappears;
- a tracked test fixture disappears;
- real IST source would need to be accessed;
- a secret is discovered in content about to be committed;
- operational real-system output appears in staging;
- unexpected tracked modifications are present;
- push would require force;
- history rewrite would be required.

Do not automatically repair these conditions.

Report them for Technical Lead review.

---

# 14. EXPECTED DECISION

On success:

STATUS=COMPLETE

DECISION=POST_V4_2_REPOSITORY_CLEANUP_COMPLETE

V4_2_CLOSED=true

V5_IMPLEMENTED=false

V5_CONTINUITY=READY

GIT_HISTORY_REWRITTEN=false

REAL_IST_SOURCE_ACCESSED=false

REAL_PROVIDER_CALLS=0

TARGET_UNDER_100_MB=true

NEXT=POST_V4_2_DOCUMENTATION_UPDATE

Stop after cleanup, validation, result, commit, push and synchronization verification.

Do NOT start the manual/glossary update.

Do NOT start V5.