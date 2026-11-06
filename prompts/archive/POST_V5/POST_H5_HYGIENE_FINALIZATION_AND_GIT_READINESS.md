# LegacyMapper — Post-H5 Hygiene Finalization and Git Readiness

## Objective
Finish the remaining hygiene decisions and leave the repository ready for the final Post-V5 Git checkpoint.

Current state:
```text
H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
```

Do not start V6. Do not rerun real IST. Do not call the provider. Git actions are NOT authorized here.

## 1. Verify external cleanup
Confirm deletion of the previously authorized obsolete `_OFF_*` directories and create/update:
```text
C:\PruebasLegacyMapper\STORAGE_CLEANUP_POST_H5_RESULT.md
```
with:
```text
before_bytes
after_bytes
recovered_bytes
deleted_paths
retained_paths
retained_baseline_bytes
retained_ai_bytes
```

## 2. Decision A — Archive\LegacyMapper_old_clone
Inspect:
```text
C:\PruebasLegacyMapper\Archive\LegacyMapper_old_clone\
```
Focus on the 3 unversioned scripts, unpublished commits, and unique files not present in the current repo.

Classify each:
```text
MIGRATE_TO_CURRENT_REPO
ARCHIVE_AS_HISTORY
DELETE
MANUAL_REVIEW
```

Rules:
- useful current logic -> migrate to current repo
- diagnostic/tooling value -> move to `tools/`
- historical-only -> archive explicitly
- duplicate/obsolete -> delete

Required invariant:
> No useful current code may remain stranded in a historical clone.

If nothing unique/useful remains, the old clone may be deleted.

## 3. Decision B — root probe_*.py scripts
Inspect every versioned `probe_*.py`.

Classify:
```text
CURRENT_DIAGNOSTIC_TOOL
DUPLICATED_CAPABILITY
HISTORICAL_EXPERIMENT
OBSOLETE
```

If retained, move them out of repository root to:
```text
tools/provider_probes/
```
or an equivalent clear tooling path.

Retained probes must document:
```text
purpose
usage
required environment variables
real-provider/quota warning
```

Delete obsolete or duplicate probes.

Required invariant:
> Repository root contains no ad-hoc provider experiment scripts.

## 4. Decision C — final Git tree classification
Run:
```bash
git status --short
git diff --stat
git diff
git ls-files --others --exclude-standard
```

Classify every changed/untracked path:
```text
KEEP_AND_COMMIT
DELETE_BEFORE_COMMIT
ARCHIVE
UNRELATED
GENERATED_DO_NOT_COMMIT
```

Do not stage anything yet.

Create a path/reason table.

## 5. Documentation authority
Verify consistency among:
```text
PROJECT_STATE.json
README.md
CLAUDE.md
docs/ARCHITECTURE/CURRENT_ARCHITECTURE.md
docs/OPERATIONS/RESUME_LEGACYMAPPER.md
docs/OPERATIONS/WORKSPACE_CONTRACT.md
docs/OPERATIONS/TESTING_GUIDE.md
docs/POST_V5/POST_H5_FULL_WORKSPACE_AND_REPOSITORY_HYGIENE_RESULT.md
```

Required:
```text
H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
```

## 6. Prompt hygiene
Confirm `prompts/CURRENT/README.md` says:
```text
POST_V5 CLOSED
H1-H5 CLOSED
V6 NOT_STARTED
no active implementation prompt
```

## 7. Targeted tests only
If old-clone/probe cleanup changes repo files, run only relevant profiles, e.g.:
```text
python -X utf8 -m legacy_documenter.devtest fast
python -X utf8 -m legacy_documenter.devtest provider
python -X utf8 -m legacy_documenter.devtest distribution
```

No full IST. No provider.

## 8. Final hygiene gate
Update/create:
```text
docs/POST_V5/POST_H5_FULL_WORKSPACE_AND_REPOSITORY_HYGIENE_RESULT.md
```

Required:
```text
POST_H5_FULL_WORKSPACE_AND_REPOSITORY_HYGIENE = PASS
EXTERNAL_HISTORICAL_FIXTURE_DEPENDENCIES = 0
ACTIVE_ABSOLUTE_WORKSPACE_DEPENDENCIES = 0
BLOCKING_HYGIENE_DEBT = 0
OLD_CLONE_UNIQUE_CURRENT_CODE = 0
ROOT_AD_HOC_PROBES = 0
H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
```

## 9. Git readiness report
Create:
```text
docs/POST_V5/POST_V5_FINAL_GIT_READINESS.md
```

Include:
```text
working tree summary
files to commit
files intentionally excluded
external workspace cleanup result
test result
current state
recommended commit message
recommended branch/upstream
```

Recommended commit message:
```text
Finalize Post-V5 and repository hygiene
```

Do not commit yet.

## Git authority
```text
repository edits = YES
test cleanup = YES
tool cleanup = YES
documentation updates = YES
provider = NO
real IST analysis = NO
commit = NO
push = NO
tag = NO
```

> No useful code in historical clones. No ad-hoc scripts in root. No unexplained Git changes before the final checkpoint.
