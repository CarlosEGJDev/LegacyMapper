# LegacyMapper — Final Version Git Checkpoint and Release Wheel

## Purpose

Create the final Git checkpoint for the accepted LegacyMapper version and rebuild the release wheel from the exact committed SHA.

This step does NOT start V6 and does NOT create a tag.

Authoritative state before starting:

```text
OWNER_STANDALONE_ACCEPTANCE = PASS
OWNER_MANUAL_REVIEW = PASS
BLOCKING_ACCEPTANCE_DEBT = 0
READY_FOR_FINAL_GIT_CHECKPOINT = YES

H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
```

The owner has approved the final human product.

---

# 1. Pre-commit repository review

Before staging, inspect:

```text
git status --short
git diff --stat
git diff
```

Confirm every pending change belongs only to:

```text
R2 human projection remediation
R2 regression tests
R2 inventory fixture/update
final owner acceptance closure
PROJECT_STATE synchronization
acceptance documentation
archived prompts generated during these rounds
```

Expected R2 production changes include:

```text
models.py
product.py
```

Expected R2/closure support changes include:

```text
new regression test(s)
updated inventory JSON required by the repository test contract
docs/ACCEPTANCE/OWNER_ACCEPTANCE_REMEDIATION_R2_RESULT.md
docs/ACCEPTANCE/OWNER_STANDALONE_ACCEPTANCE_FINAL_RESULT.md
docs/ACCEPTANCE/OWNER_ACCEPTANCE_FINAL_CLOSURE_RESULT.md
PROJECT_STATE.json
relevant archived prompts
```

Do not stage unrelated files.

If any unrelated or unexplained modification exists:

```text
STOP
READY_FOR_FINAL_GIT_CHECKPOINT = NO
```

and report it.

---

# 2. State consistency gate

Before commit verify:

```text
OWNER_STANDALONE_ACCEPTANCE = PASS
OWNER_MANUAL_REVIEW = PASS
BLOCKING_ACCEPTANCE_DEBT = 0
H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
```

Historical fields may retain truthful historical values such as:

```text
v5_6_git_checkpoint = R1_NO_COMMIT_PUSH_TAG_BY_INSTRUCTION
```

Do not rewrite historical facts merely to make wording uniform.

No stale active acceptance state may remain such as:

```text
READY_FOR_RETRY
READY_FOR_OWNER_REVIEW
READY_FOR_OWNER_MANUAL_REVIEW
NOT_BUILT
```

unless clearly contained in historical narrative/evidence rather than current state.

---

# 3. Tests before commit

Do not call the provider.

Do not analyze IST.

Do not scan source.

The latest known validation is:

```text
full suite = 3626 tests
failures = 0
errors = 0
skipped = 135

post-closure targeted/state suites = 675
result = PASS
```

Because production R2 code was already covered by the clean 3626-test full suite and only state/docs changed afterward, do NOT repeat the full suite unless the pre-commit review finds a production-code change made after that suite.

Run the smallest authoritative state/acceptance validation required by the repository if needed.

Required:

```text
provider calls = 0
fresh IST analysis = 0
scanner = 0
analyzer = 0
```

---

# 4. Git authorization

The owner authorizes:

```text
stage = YES
commit = YES
push = YES
tag = NO
force push = NO
```

Use a normal commit on `main`.

Recommended commit subject:

```text
Finalize owner acceptance and human projection
```

The commit should contain the complete R2 remediation and final acceptance closure.

Do not split into unnecessary commits unless repository policy requires it.

---

# 5. Commit

Stage only approved files.

Create the commit:

```text
git add <approved files>
git commit -m "Finalize owner acceptance and human projection"
```

Record:

```text
commit SHA
commit subject
files committed
```

Verify after commit:

```text
git status --short
```

Expected:

```text
clean
```

If not clean, explain every remaining item before continuing.

---

# 6. Push

Verify branch:

```text
main
```

Verify remote relationship and that no force is required.

Push normally:

```text
git push origin main
```

Required:

```text
normal push = PASS
force push = NO
tag = NO
```

After push verify local `main` and `origin/main` resolve to the same SHA.

---

# 7. Build final release wheel from exact committed SHA

The previous R2 candidate wheel:

```text
SHA-256 = 5baee7d9…09ba
```

was built from an uncommitted tree and is NOT the final release artifact.

Build a fresh wheel from the exact final commit using the established clean `git archive` workflow.

Do not build from a dirty checkout.

Required provenance:

```text
source = exact committed SHA
working tree influence = none
editable install = no
```

Expected package version remains:

```text
LegacyMapper 5.9.0
```

unless the repository already contains a deliberate version change. Do not invent a new version number in this step.

Record:

```text
wheel filename
wheel bytes
wheel SHA-256
Python version
source commit SHA
build command/workflow
```

---

# 8. Minimal release-wheel verification

Install the newly built wheel into a fresh temporary venv.

Verify:

```text
PYTHONPATH = empty
import path = site-packages
legacymapper --help = PASS
python -m legacy_documenter --help = PASS
```

Do not execute real AI.

Do not re-run IST analysis.

If a cheap deterministic smoke/profile exists that requires no source corpus and no provider, it may be run.

Required:

```text
provider calls = 0
```

---

# 9. Release provenance receipt

Create an external release receipt outside the repository, for example:

```text
C:\LegacyMapperAcceptance\output\FINAL_RELEASE_CHECKPOINT_RESULT.md
C:\LegacyMapperAcceptance\output\FINAL_RELEASE_CHECKPOINT_EVIDENCE.json
```

Include:

```text
final commit SHA
branch
push result
origin/main SHA
working tree clean
wheel filename
wheel SHA-256
wheel source SHA
fresh venv verification
owner acceptance PASS
manual review PASS
H5 CLOSED
POST_V5 CLOSED
V6 NOT_STARTED
tag NOT_CREATED
```

Do not alter already accepted semantic/provider state.

---

# 10. Repository documentation after commit

Do NOT create a second repository commit merely to record the SHA of the commit that was just created unless an existing repository contract explicitly requires that SHA inside tracked files.

The external release receipt is the authoritative place for:

```text
final commit SHA
final release wheel SHA-256
```

If a tracked file absolutely requires post-commit release provenance, STOP and report the requirement instead of silently creating another commit.

---

# 11. Final gate

Required:

```text
FINAL_GIT_CHECKPOINT = PASS
MAIN_PUSHED = YES
LOCAL_MAIN_EQUALS_ORIGIN_MAIN = YES
WORKING_TREE_CLEAN = YES
FINAL_RELEASE_WHEEL_FROM_COMMITTED_SHA = YES
FINAL_RELEASE_WHEEL_SMOKE = PASS
OWNER_STANDALONE_ACCEPTANCE = PASS
BLOCKING_ACCEPTANCE_DEBT = 0
V6 = NOT_STARTED
TAG_CREATED = NO
```

Then report:

```text
READY_FOR_FINAL_VERSION_TAG_REVIEW = YES
```

---

# 12. Stop before tag

Do not create:

```text
git tag
release tag
GitHub release
V6 branch
V6 commit
```

The owner will review the final commit SHA and release-wheel SHA-256 first.

---

# Final report

Return:

```text
FINAL_GIT_CHECKPOINT
commit SHA
commit subject
push result
origin/main SHA
working tree status

release wheel filename
release wheel SHA-256
release wheel source SHA
fresh venv smoke result

OWNER_STANDALONE_ACCEPTANCE
BLOCKING_ACCEPTANCE_DEBT
H5
POST_V5
V6

TAG_CREATED
READY_FOR_FINAL_VERSION_TAG_REVIEW
```

Expected:

```text
FINAL_GIT_CHECKPOINT = PASS
OWNER_STANDALONE_ACCEPTANCE = PASS
BLOCKING_ACCEPTANCE_DEBT = 0
H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
TAG_CREATED = NO
READY_FOR_FINAL_VERSION_TAG_REVIEW = YES
```

> This checkpoint freezes the accepted implementation in Git.

> The release wheel must come from that exact commit.

> Do not tag until the owner reviews the checkpoint.
