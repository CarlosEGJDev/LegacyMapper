# LegacyMapper — Final Post-V5 Cleanup, Commit and Push

## Owner authorization

The owner explicitly authorizes the following actions:

```text
delete C:\PruebasLegacyMapper\Archive\LegacyMapper_old_clone = YES
review final git status = YES
commit = YES
push = YES
tag = NO
```

Do not create or push any tag.

Do not delete any other directory under:

```text
C:\PruebasLegacyMapper\Archive\
```

Do not touch the real IST source tree.

Do not run real IST analysis.
Do not call the provider.

---

# 1. Delete the explicitly authorized old clone

Delete exactly:

```text
C:\PruebasLegacyMapper\Archive\LegacyMapper_old_clone
```

This deletion is authorized because the previous review established:

```text
unpublished commits = 0
unique useful current code remaining = 0
list_copilot_models.py already migrated
other unversioned scripts were obsolete
```

If normal recursive deletion is blocked by path-length or filesystem issues, use a safe Windows-compatible deletion strategy only for this exact directory.

Do not broaden the deletion scope.

After deletion, verify:

```text
path no longer exists
Archive\ still exists
other Archive\ contents remain untouched
```

---

# 2. Confirm external workspace hygiene remains valid

Verify the current external workspace still satisfies:

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

Update the hygiene result only if necessary to record the old-clone deletion.

Do not alter H5 closure semantics.

---

# 3. Do NOT rerun the full suite unless a real code change appears

Current accepted validation evidence:

```text
full suite:
3575 tests
0 failures
0 errors
135 skipped
```

Subsequent targeted verification:

```text
fast = 152 tests OK
provider = 75 tests OK
distribution = 173 tests OK
state/hygiene modules = 637 tests OK
```

Since the remaining actions are:

```text
external clone deletion
documentation receipt update
Git checkpoint
```

do not rerun the full suite unless an unexpected runtime/code change is discovered.

If only docs/state/tool-location receipts change, targeted verification is sufficient.

---

# 4. Final Git inspection

Run:

```bash
git status --short
git diff --stat
git diff
git ls-files --others --exclude-standard
```

Confirm every changed/untracked repository path is classified as:

```text
KEEP_AND_COMMIT
```

except generated/ignored files that are intentionally not tracked.

Specifically verify:

```text
tools/provider_probes/
docs/POST_V5/
docs/OPERATIONS/
docs/ARCHITECTURE/
prompts/CURRENT/
prompts/archive/
PROJECT_STATE.json
README.md
CLAUDE.md
test/devtest changes
```

Also verify deleted obsolete root probes are intentional.

Do not stage unrelated changes.

If an unexplained unrelated file appears:

```text
STOP
report the path
do not commit
```

---

# 5. Verify current state before staging

The repository must tell one coherent current-state story:

```text
H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
POST_H5_FULL_WORKSPACE_AND_REPOSITORY_HYGIENE = PASS
```

No active document may say:

```text
H5 = NOT_STARTED
POST_V5 = IN_PROGRESS
```

unless clearly historical.

Confirm:

```text
prompts/CURRENT/README.md
```

states there is no active implementation prompt.

---

# 6. Stage final Post-V5 closure tree

Stage all legitimate Post-V5 finalization/hygiene changes.

Expected categories include:

```text
H5 closure state/docs
post-H5 hygiene implementation
test profile runner
path-independence changes
fixture-independence changes
prompt archive reorganization
canonical operations/architecture docs
provider probe cleanup/migration
PROJECT_STATE.json
README.md
CLAUDE.md
final hygiene/readiness reports
```

Do not stage:

```text
generated external workspace
C:\PruebasLegacyMapper\...
temporary logs
venvs
runtime caches
acceptance outputs
ignored build artifacts
```

---

# 7. Review staged diff

Run:

```bash
git diff --cached --stat
git diff --cached
```

Verify:

```text
no secrets
no tokens
no machine-local generated output
no accidental source corpus paths as runtime dependencies
no tag changes
no V6 start
```

Historical reports may retain historical machine paths where appropriate.

---

# 8. Commit

Create one final Post-V5 checkpoint commit.

Use commit subject:

```text
Finalize Post-V5 and repository hygiene
```

Recommended body:

```text
- close Post-V5 after H5 real IST validation
- remove active historical fixture/workspace dependencies
- add capability-oriented test profiles
- archive historical prompts and define current operational entry point
- add canonical architecture, workspace and testing documentation
- clean provider probe tooling
- finalize project state for standalone owner acceptance
```

Do not amend old commits.

---

# 9. Push

Before push record:

```bash
git branch --show-current
git log -1 --oneline
git remote -v
git status --short
```

Push the current branch to its configured upstream.

Rules:

```text
normal push only
no force push
no new remote
no tag push
```

---

# 10. Post-push verification

After push, report:

```text
branch
upstream
commit SHA
commit subject
push result
git status --short
```

Expected:

```text
working tree clean
```

If intentionally untracked/ignored files remain, list them clearly.

---

# 11. Do NOT start standalone acceptance yet

After successful push:

```text
POST_V5 = CLOSED
V6 = NOT_STARTED
OWNER_STANDALONE_ACCEPTANCE = NOT_STARTED
```

Do not run the full IST acceptance in this prompt.

The next owner-controlled step is:

```text
LEGACYMAPPER_OWNER_FULL_IST_STANDALONE_ACCEPTANCE.md
```

That run must use a wheel built from the exact pushed commit SHA.

---

# 12. Final result report

Create/update:

```text
docs/POST_V5/POST_V5_FINAL_GIT_CHECKPOINT_RESULT.md
```

Include:

```text
old clone deletion = PASS
final git classification = PASS
commit SHA
branch
upstream
push result
tag = NOT_CREATED
working tree status
H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
owner standalone acceptance = NOT_STARTED
```

If creating this report before commit is necessary, include all known data and fill the final SHA after commit only if repository workflow allows a follow-up receipt commit.

Prefer one coherent final commit where practical.

---

# Final authority

```text
delete LegacyMapper_old_clone = YES
repository edits = YES
staging = YES
commit = YES
push = YES

tag = NO
provider = NO
real IST analysis = NO
V6 start = NO
owner acceptance run = NO
```

> **This is the final Post-V5 Git checkpoint before the owner's independent standalone IST acceptance test.**
