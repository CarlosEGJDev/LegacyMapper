# POST-V4.2 Fresh-Clone Reproducibility — Verification Evidence

Compact, auditable evidence log for the correction described in
`docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION_RESULT.md`.
All commands executed from repository root (`C:\dev\LegacyMapper`) using
`C:\Users\cgalianj\AppData\Local\Programs\Python\Python314\python`.

## Test discovery / count

| When | Command | Result |
|---|---|---|
| Before correction | `python -m unittest discover -s tests` | `Ran 1625 tests in 75.472s` / `FAILED (failures=2, errors=19)` |
| After correction | `python -m unittest discover -s tests` | `Ran 1809 tests in 74.789s` / `FAILED (failures=1, skipped=132)` |
| Historical closure baseline (`PROJECT_STATE.json.tests`) | n/a | `1809` |

1809 (post-correction) == 1809 (historical). Difference explained: `unittest` counts one
synthetic `setUpClass` error per class (not per method) when `setUpClass` raises; six
classes hit this before correction, undercounting `testsRun` by 184. See
CORRECTION_RESULT.md § TEST_COUNT_INVESTIGATION for the full method-count reconciliation.

## Final authoritative full-suite result (run exactly once, post-correction)

```
Ran 1809 tests in 74.789s

FAILED (failures=1, skipped=132)
```

- 0 errors.
- 1 failure: `test_v4_2_r8_documentation_at_scale.FinalBaselineAndManifestIntegrityTests.test_manifest_hashes_match_referenced_files`.
- 132 skips, all carrying an explicit reason string naming the missing untracked real-repository fixture (`output/v2_r5_1_full/` or `output/v3_r8_1/` full dump) and pointing at `docs/PROJECT_RECOVERY.md`.

## Readiness result

Command: `python main.py readiness`

```json
{
  "ai_knowledge_allowed": true,
  "ai_knowledge_generated": false,
  "checks": {
    "architecture_integrity": true,
    "claim_integrity": true,
    "evidence_closure": true,
    "knowledge_boundary": true,
    "knowledge_projection": true,
    "preconditions": true,
    "quantitative_integrity": true,
    "security": true
  },
  "ineligible_records": 4,
  "output": "output\\v3_r9",
  "provider_calls": 0,
  "readiness": "READY",
  "real_llm_calls": 0,
  "records": 47,
  "status": "V3-R9_KNOWLEDGE_READINESS_GATE_COMPLETE"
}
```

`EXIT_CODE=0`. No traceback, no uncaught exception.

## Missing-file behavior (pre-correction, for the record)

```
FileNotFoundError: [Errno 2] No such file or directory:
'C:\\dev\\LegacyMapper\\output\\v3_r8_1\\ARCHITECTURE_EVIDENCE.json'
```
raised from `legacy_documenter/knowledge/readiness.py:145` via `_readiness_io._read`,
propagating uncaught through `readiness.run()`, the `python -m
legacy_documenter.knowledge.readiness` CLI (exit 1), and `python main.py readiness`
(exit 1, tripping `test_all_four_externally_observable_exit_codes`).

## Tracked-file availability

- `git log --all --oneline -- output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` (pre-correction): empty — never tracked.
- Post-correction: `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` exists on disk, 1803 bytes.
- `git check-ignore`/`git add -n output/v3_r8_1/` (post-correction): stages exactly `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`; no other file under that directory is un-ignored.
- `git ls-files output/ | grep v4_2_r8`: confirms `output/v4_2_r8/V4_2_FINAL_BASELINE.json` and `output/v4_2_r8/V4_2_FINAL_MANIFEST.json` remain tracked and untouched by this round (no diff against HEAD).
- `git show HEAD:docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md | sha256sum` == `4c11209f6fac40617b6a16c6ad796e1c384bb444b0dcf691d3216e2dafd70e71` == the hash pinned in `output/v4_2_r8/V4_2_FINAL_MANIFEST.json` — confirms the one remaining test failure is caused solely by the *pending, uncommitted* working-tree edit to that manual, not by any defect in the manifest or in this correction.

## Git status

Working tree at the end of this round (no commit made):

```
 M .gitignore
 M docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md        (pre-existing pending, untouched by this round)
 M docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md              (pre-existing pending, untouched by this round)
 M tests/test_v3_r7_2.py
 M tests/test_v3_r7_2_4.py
 M tests/test_v3_r8_2.py
 M tests/test_v3_r8_2_correction.py
?? docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md                 (pre-existing pending, untouched)
?? docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION_RESULT.md
?? docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_VERIFICATION.md
?? docs/V4_2/POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY_RESULT.md   (pre-existing pending, untouched)
?? output/v3_r8_1/                                         (new: exactly one trackable file inside)
?? prompts/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION.md
?? prompts/V4_2/POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY.md       (pre-existing pending, untouched)
```

`PROJECT_STATE.json`: unmodified (verified byte-identical before/after). No `git commit`,
no `git push` executed.

## Repository size

- Tracked content before this round's changes (HEAD, 652 files): 1,499,292 bytes (~1.43 MiB).
- Tracked content after (if staged, 653 files): +1,803 bytes (~1.43 MiB total).
- No restoration of the ~9.3 GiB previously cleaned-up heavy output. No new directory larger than 2 KiB was added.

## No real provider / no real IST access

- `grep`/manual read of `legacy_documenter/llm/core.py::ProviderRegistry.create`: only `FAKE` and `COPILOT` are constructible; `gemini.py` is not imported by any changed file.
- Full-suite run output includes, per fixture-based full-pipeline test: `(FakeLLMProvider only -- no real AI provider was ever reachable from this script.)`.
- `readiness` output: `provider_calls: 0`, `real_llm_calls: 0`.
- `C:\Users\cgalianj\source\IST_40\operacional` was not referenced by any command run in this round; `legacy_documenter/analysis/deep_source.py::run()` (the only real-scan entry point) was never invoked.

## No historical rewrite

- `output/v4_2_r8/V4_2_FINAL_BASELINE.json`, `output/v4_2_r8/V4_2_FINAL_MANIFEST.json`: no diff against HEAD (not opened for writing at any point).
- `PROJECT_STATE.json`: no diff against HEAD.
- `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` is a **new** tracked file (previously absent/untracked), not a rewrite of any existing historical artifact.
