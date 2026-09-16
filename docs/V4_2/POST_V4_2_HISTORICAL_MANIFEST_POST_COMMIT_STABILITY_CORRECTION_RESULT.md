# Post-V4.2 — Historical Manifest Post-Commit Stability Correction — Result

## STATUS

COMPLETE.

## STARTING_PROBLEM

The previous reconciliation round's fix to
`FinalBaselineAndManifestIntegrityTests.test_manifest_hashes_match_referenced_files`
compared `authoritative_artifacts` content to **current HEAD** whenever the
working tree had an uncommitted diff for that path, and to current disk
bytes otherwise. This only passed because the pending Post-V4.2 manual
edits were still uncommitted (`git diff HEAD` reported dirty, so the test
fell back to hashing `HEAD`, which still held the old, historically
correct content). The moment those edits are committed, HEAD would hold
the *new* manual content, `git diff HEAD` would report clean, and the test
would hash current-disk-equals-HEAD content — which legitimately differs
from the V4.2 closure snapshot recorded in the manifest — causing an
immediate false failure on the very next commit. The fix implicitly used
"current HEAD" as a stand-in for "historical truth," which is wrong on
both counts: it depends on dirty/clean working-tree state, and it depends
on HEAD's *current* content rather than a fixed historical point.

## HISTORICAL_REFERENCE_INVESTIGATION

Investigated, in order:

1. `tests/test_v4_2_r8_documentation_at_scale.py` — confirmed the prior
   HEAD-diff-based logic (quoted above) and its `_has_uncommitted_change`/
   `_git_head_bytes` helpers.
2. `tools/v4_2_r8_build_final_artifacts.py` — `sha256_of()` computes
   `hashlib.sha256((REPO_ROOT / rel_path).read_bytes()).hexdigest()`, i.e.
   the manifest's `authoritative_artifacts` hashes are **working-tree disk
   bytes at build time**, not a git-blob hash and not a normalized text
   hash.
3. `docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md` — section
   `FILES_CHANGED_FOR_CLOSURE` states the manifest/baseline (built in the
   preceding task) were staged and committed together with the closure
   task's own two files, "as one commit on `main`." Section `## GIT_COMMIT`
   explicitly records that commit: `` `af7e2099039e791c5a14ff94bf5ad348e8dbb4db` ``
   — "V4.2 formally closed: final approval, versioning, and closure".
   Section `## GIT_STATUS` independently confirms, via
   `git rev-parse HEAD` / `git rev-parse origin/main` immediately after
   push, that this commit is exactly what was pushed to `origin/main`.
4. `git log --oneline --all` confirms `af7e2099...` is a real, reachable
   ancestor commit of the current `main` history.
5. `docs/V4_2/POST_V4_2_DOCUMENTATION_AND_HISTORICAL_MANIFEST_RECONCILIATION_RESULT.md`
   (previous round) — confirms the two-collection manifest contract
   (`authoritative_artifacts` vs. `mutable_current_state_documents`) and
   that the latter is explicitly "not an integrity requirement."

This satisfies evidence order (1) from the plan: an explicit V4.2 closure
commit recorded in tracked, already-reviewed closure documentation. No
invented commit, no `HEAD~N` offset, no locally-guessed hash was used.

## V4_2_CLOSURE_REFERENCE

`af7e2099039e791c5a14ff94bf5ad348e8dbb4db`, read at test time from
`docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md`'s `## GIT_COMMIT`
section via a small regex (not hardcoded as a literal in the test), with a
defensive `git cat-file -e <commit>^{commit}` check that the commit is
actually reachable in local history (guards against a shallow clone
silently producing a false pass or a confusing error).

## ORIGINAL_MANIFEST_HASH_SEMANTICS

Confirmed empirically: for every `authoritative_artifacts` entry, hashing
`git show af7e2099...:<path>` reproduces the manifest's recorded
`sha256` **except** for four `legacy_documenter/**` `.py` sources
(`flow_resolver.py`, `markdown_exporter.py`, `pipeline_stages.py`,
`full_pipeline.py`). For those four, the manifest hash matches the same
git-blob content with `\n` → `\r\n` applied (i.e. the CRLF-smudged form
`core.autocrlf=true` would produce on checkout). All `.md`/`.json`
authoritative artifacts matched the raw (LF) blob directly. This confirms
the manifest hashed *whatever line-ending representation actually sat on
disk* at build time, which was heterogeneous across files (some files
apparently arrived on disk as LF regardless of autocrlf, e.g.
freshly-authored docs; the four `.py` sources had gone through a normal
git checkout smudge to CRLF).

## AUTOCRLF_AND_LINE_ENDING_ANALYSIS

`core.autocrlf=true` and no `.gitattributes` are configured. `git show
<commit>:<path>` always returns the raw, LF-normalized blob as stored in
git, never the smudged working-tree form. Since the original manifest
hashed real disk bytes (see above) and those disk bytes were, for some
files, CRLF-smudged, a correct historical-equivalence check must accept
**both** representations of the historical blob (raw LF-as-stored, and
LF→CRLF converted) rather than assuming one universally. This was verified
directly (see ORIGINAL_MANIFEST_HASH_SEMANTICS) rather than assumed, and
is implemented as `_historical_hash_candidates()` — a pure function of the
historical blob's own bytes, independent of the current working tree or
HEAD.

## SELECTED_SOLUTION

Replaced the HEAD-diff-gated comparison with a comparison pinned to the
V4.2 closure commit:

- `authoritative_artifacts`: for each entry, fetch
  `git show <closure_commit>:<path>` and accept a match if either that
  blob, or its CRLF/LF counterpart, hashes to the manifest's recorded
  `sha256`. Current working-tree/HEAD content is never read for the hash
  comparison. A lightweight `path.is_file()` existence check against the
  current working tree is kept (unchanged from all prior rounds) as a
  basic current-repository sanity check, clearly separated from the
  content-hash comparison.
- `mutable_current_state_documents`: unchanged — existence-only, per the
  manifest's own documented contract.
- Added a new, isolated post-commit-stability regression test (see
  TESTS_ADDED_OR_CHANGED) that proves the same verification logic is
  stable across a simulated later commit, in a throwaway temp git repo.

## WHY_CURRENT_HEAD_IS_NOT_USED

HEAD is not historical evidence — it is "whatever the repository currently
contains," which by design is allowed to diverge from the V4.2 closure
snapshot for `authoritative_artifacts` paths that continue to evolve
(e.g. the manuals under `docs/V4_2/`). Using HEAD (directly, or
conditionally via a dirty/clean check) makes the test's pass/fail outcome
a function of unrelated, later, legitimate commits — exactly the bug this
round fixes. The V4.2 closure commit is a fixed point in git history that
never changes regardless of what happens to `main` afterwards, which is
what "historical integrity" requires.

## IMPLEMENTATION

File: `tests/test_v4_2_r8_documentation_at_scale.py`.

Added module-level helpers (used by both the real test and the isolated
post-commit-stability test):

- `_git_show_bytes(repo_root, commit, rel_path)` — raw bytes of a path at
  a given commit, via `git show <commit>:<path>`.
- `_historical_hash_candidates(blob)` — the blob bytes plus its CRLF/LF
  counterpart.
- `_matches_historical_hash(repo_root, commit, rel_path, expected_sha256)`
  — true if any candidate hashes to `expected_sha256`.

Added `FinalBaselineAndManifestIntegrityTests._v4_2_closure_commit()`,
which reads and validates the closure commit hash from
`docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md`.

Rewrote `test_manifest_hashes_match_referenced_files` to use these helpers
instead of `_has_uncommitted_change`/`_git_head_bytes` (both removed).

## FILES_CHANGED

- `tests/test_v4_2_r8_documentation_at_scale.py` (test logic only).

No other file was modified by this round. `output/v4_2_r8/V4_2_FINAL_MANIFEST.json`
and `output/v4_2_r8/V4_2_FINAL_BASELINE.json` were read-only inputs,
untouched. `PROJECT_STATE.json` untouched. `legacy_documenter/**` untouched.

## TESTS_ADDED_OR_CHANGED

- Changed: `test_manifest_hashes_match_referenced_files` (historical-commit
  based, see above).
- Added: `test_historical_manifest_integrity_survives_a_later_commit` —
  builds an isolated temp git repo (`tempfile.TemporaryDirectory`, never
  the real LegacyMapper repository), commits "historical" content,
  records its hash, then makes a second, later commit with different
  "Post-V4.2" content at the same path (so HEAD now differs from the
  historical snapshot), and asserts that `_matches_historical_hash`
  pinned to the first commit still validates the historical content —
  both with a clean tree and with an additional uncommitted dirty edit on
  top. Also asserts HEAD's own content does NOT match the historical hash
  (proving the test is not accidentally vacuous).

## DIRTY_WORKTREE_CASE

Covered by the real suite run itself: at the time of this round, the
pending Post-V4.2 manual edits are uncommitted (dirty tree for those
paths), and `test_manifest_hashes_match_referenced_files` passes because
verification never reads working-tree state for `authoritative_artifacts`
— it only reads `git show <closure_commit>:<path>`. Also explicitly
exercised by the new isolated test's final assertion (dirty tree on top of
the later commit still resolves against the pinned historical commit).

## CLEAN_WORKTREE_CASE

Explicitly exercised by the new isolated test immediately after the
second ("later") commit, before any further edit — a clean tree whose
HEAD differs from history — and the historical check still passes while a
direct HEAD-content comparison is shown to fail (both asserted).

## POST_COMMIT_SIMULATION_CASE

Same isolated test: commit 1 = historical content (`V4.2 CLOSURE
CONTENT`), commit 2 = different content at the same path
(`POST-V4.2 EDITED CONTENT`), standing in for a real future commit of the
pending manuals. Historical verification pinned to commit 1 passes in
both the clean and dirty states after commit 2. Result: PASS.

## TARGETED_TESTS

Ran (PowerShell, this checkout):

```
python -m unittest tests.test_v4_2_r8_documentation_at_scale.FinalBaselineAndManifestIntegrityTests -v
```

Result: `Ran 6 tests in 9.952s` / `OK` — covering: artifacts exist,
builder byte-identical regeneration, the corrected historical-manifest
hash test, the new post-commit-stability simulation, the no-secret/no-
absolute-path check, and the baseline invariants check.

## FINAL_AUTHORITATIVE_FULL_SUITE

Executed exactly once, after the fix:

```
python -m unittest discover -s tests
```

Result: `Ran 1810 tests in 69.923s` / `OK (skipped=132)`.

DISCOVERED=1810 (1809 + 1 new post-commit-stability test required by this
round's own plan section 9 — a documented, plan-mandated increase, not an
unexplained drift). FAILURES=0. ERRORS=0. SKIPS=132, unchanged from the
prior round, all previously explained (four real-repository-dependent
fixture families still absent — no new skip reasons introduced).
ALL_SKIPS_EXPLAINED=true.

## READINESS_VERIFICATION

```
python main.py readiness
```

Result: `"readiness": "READY"`, `"provider_calls": 0`, `"real_llm_calls": 0`,
all `checks` true, process exit code `0`. No uncaught exception.

## HISTORICAL_MANIFEST_INTEGRITY

PASS. Every `authoritative_artifacts` entry's content at the V4.2 closure
commit (`af7e2099039e791c5a14ff94bf5ad348e8dbb4db`) matches its pinned
manifest hash, independent of current HEAD/working-tree state.

## HISTORICAL_BASELINE_INTEGRITY

Unaffected/unchanged by this round: `test_builder_regenerates_byte_identical_output`
(regenerates `V4_2_FINAL_BASELINE.json` from the current builder module
and compares to the on-disk baseline) continues to pass as before; this
round did not touch that test or the baseline file.

## POST_COMMIT_STABILITY

PASS — proven via the isolated temp-repo simulation described above,
without performing any commit in the real LegacyMapper repository.

## CURRENT_REPOSITORY_VALIDITY

Kept separate from historical integrity, as required: `path.is_file()`
existence checks against the current working tree remain for
`authoritative_artifacts` and `mutable_current_state_documents`; current
repository health continues to be exercised by the rest of the test suite
and by `python main.py readiness`, not by historical hash comparison.

## MANUALS_CHANGED

false. No technical semantics changed by this round; only test-internal
verification logic changed. The three manuals/glossary were not touched.

## PRODUCTION_CODE_CHANGED

false. `legacy_documenter/**` was not modified.

## REAL_PROVIDER_CALLS

0.

## REAL_IST_ACCESSED

false.

## V4_2_STATUS

V4.2 remains formally closed (`af7e2099039e791c5a14ff94bf5ad348e8dbb4db`
is used only as a read-only historical reference point; nothing about the
closure itself was reopened or altered).

## V5_STATUS

NOT_IMPLEMENTED. Out of scope for this round.

## GIT_STATUS

No commit, no push, no staging performed by this round. Working tree
still carries all previously pending, uncommitted Post-V4.2 changes from
the prior four rounds, plus this round's own change to
`tests/test_v4_2_r8_documentation_at_scale.py`. `output/v4_2_r8/V4_2_FINAL_MANIFEST.json`
and `V4_2_FINAL_BASELINE.json` are unmodified (still exactly as
committed at V4.2 closure). `PROJECT_STATE.json` is unmodified.

## DECISION

POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_READY_FOR_TECHNICAL_LEAD_REVIEW

## NEXT

HUMAN_POST_COMMIT_STABILITY_REVIEW. Do not commit, do not push, do not
start V5.
