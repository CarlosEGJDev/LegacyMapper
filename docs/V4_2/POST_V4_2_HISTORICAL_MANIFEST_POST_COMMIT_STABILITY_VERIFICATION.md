# Post-V4.2 — Historical Manifest Post-Commit Stability — Verification

Compact, auditable evidence for the correction recorded in
`POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_CORRECTION_RESULT.md`.

## HISTORICAL_V4.2_REFERENCE_USED

Commit `af7e2099039e791c5a14ff94bf5ad348e8dbb4db` ("V4.2 formally closed:
final approval, versioning, and closure").

## HOW_IT_WAS_RESOLVED

Read at test time from `docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md`,
section `## GIT_COMMIT` (tracked, already-reviewed closure documentation),
via `FinalBaselineAndManifestIntegrityTests._v4_2_closure_commit()`, then
confirmed reachable with:

```
git cat-file -e af7e2099039e791c5a14ff94bf5ad348e8dbb4db^{commit}
```

Not hardcoded as a bare literal in the test; not HEAD; not `HEAD~N`.

## REPRESENTATIVE_HISTORICAL_ARTIFACT_HASH_VERIFICATION

Manual spot check (independent of the test suite), comparing manifest
hashes to `git show af7e2099...:<path>` (accepting the CRLF/LF
counterpart per the autocrlf analysis):

| Path | Result |
|---|---|
| `docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md` | OK (raw blob, LF) |
| `docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md` | OK (raw blob, LF) |
| `legacy_documenter/analysis/flow_resolver.py` | OK (CRLF-converted blob) |
| `legacy_documenter/exporters/markdown_exporter.py` | OK (CRLF-converted blob) |
| `legacy_documenter/cli/pipeline_stages.py` | OK (CRLF-converted blob) |
| `legacy_documenter/cli/full_pipeline.py` | OK (CRLF-converted blob) |
| `output/v4_2_r8/V4_2_FINAL_BASELINE.json` | OK (raw blob, LF) |

All 31 `authoritative_artifacts` entries verified OK by this method (27
against the raw historical blob, 4 against its CRLF-converted form).

## DIRTY_WORKING_TREE_TEST

Real repository, as-is: `docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md`,
`LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md` (both `authoritative_artifacts`
entries) have pending uncommitted edits from the earlier documentation
round. `test_manifest_hashes_match_referenced_files` PASSED — verification
never reads working-tree bytes for these entries; it reads
`git show af7e2099...:<path>` only.

## CLEAN_WORKING_TREE_TEST

Isolated temp-repo simulation
(`test_historical_manifest_integrity_survives_a_later_commit`): after the
second ("later Post-V4.2") commit and before any further edit, the tree is
clean and HEAD differs from the historical commit. `_matches_historical_hash`
pinned to the first commit PASSED; a direct comparison against HEAD's
content was asserted to FAIL (proving the check is not vacuously true).

## SIMULATED_LATER_COMMIT_TEST

Same isolated test. Commit 1 = historical content
(`V4.2 CLOSURE CONTENT\n`), recorded hash = its sha256. Commit 2 (later,
different content, `POST-V4.2 EDITED CONTENT\n`) makes HEAD diverge from
history at the same path. `_matches_historical_hash(repo, commit1, path,
historical_sha256)` PASSED both immediately after commit 2 (clean) and
after an additional uncommitted edit on top (dirty). Result:
POST_COMMIT_STABILITY=PASS.

## LINE_ENDING_BEHAVIOR

`core.autocrlf=true`, no `.gitattributes`. Empirically, the original
manifest hashes correspond to whichever line-ending representation
actually sat on disk per file at build time (heterogeneous: most
`docs/**`/`.json` artifacts as LF, four `legacy_documenter/**` `.py`
sources as CRLF). `_historical_hash_candidates()` accepts both the raw
historical git-blob bytes and their CRLF/LF counterpart, so this is
handled deterministically from the historical blob alone — no dependency
on the current working tree's autocrlf smudge state.

## FINAL_FULL_SUITE_RESULT

```
python -m unittest discover -s tests
```

`Ran 1810 tests in 69.923s` — `OK (skipped=132)`.
DISCOVERED=1810 (1809 + 1 new required post-commit-stability test).
FAILURES=0. ERRORS=0. SKIPS=132 (unchanged, all previously explained).
ALL_SKIPS_EXPLAINED=true.

## READINESS_RESULT

```
python main.py readiness
```

`readiness=READY`, exit code `0`, `provider_calls=0`, `real_llm_calls=0`.

## GIT_STATUS

No commit performed. No push performed. No staging performed. Only
`tests/test_v4_2_r8_documentation_at_scale.py` was modified by this round
(plus the two new result documents created by it); all previously pending
Post-V4.2 changes from earlier rounds remain uncommitted, untouched by
this round.

## NO_REAL_PROVIDER

Confirmed: `provider_calls=0`, `real_llm_calls=0` in the readiness output
above; no network/provider code paths were exercised by any test run in
this round.

## NO_IST_ACCESSED

Confirmed: no path under `C:\Users\cgalianj\source\IST_40\operacional` (or
any real legacy repository) was read or referenced by this round's changes
or test runs.

## NO_HISTORICAL_ARTIFACT_MODIFICATION

Confirmed: `output/v4_2_r8/V4_2_FINAL_MANIFEST.json` and
`output/v4_2_r8/V4_2_FINAL_BASELINE.json` are byte-identical to their
state before this round (read-only inputs to the corrected test; not
opened for writing by any change in this round).

## RESULT

POST_COMMIT_STABILITY=PASS, HISTORICAL_MANIFEST_INTEGRITY=PASS,
CURRENT_TEST_DISCOVERY=1810, CURRENT_TEST_FAILURES=0,
CURRENT_TEST_ERRORS=0, ALL_SKIPS_EXPLAINED=true, READINESS=READY,
READINESS_EXIT_CODE=0, PRODUCTION_CODE_CHANGED=false,
REAL_PROVIDER_CALLS=0, REAL_IST_ACCESSED=false, V4_2_CLOSED=true,
V4_2_REOPENED=false, V5_IMPLEMENTED=false.
