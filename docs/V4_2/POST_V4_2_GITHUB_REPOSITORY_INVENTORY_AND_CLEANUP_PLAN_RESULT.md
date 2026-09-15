# POST_V4_2_GITHUB_REPOSITORY_INVENTORY_AND_CLEANUP_PLAN_RESULT

Mode: POST_V4_2_REPOSITORY_AUDIT_ONLY. Read-only inspection. No production/test/doc/prompt/governance file modified. No file deleted, moved, or renamed. No `.gitignore` change applied. No commit/push. No real IST access. No real AI provider calls. No V5 work started.

## STATUS

AUDIT_COMPLETE. Decision: **READY_FOR_TECHNICAL_LEAD_CLEANUP_REVIEW**.

Repository is already close to the target state: nothing large is currently tracked by Git. The only concrete action item is a `.gitignore` gap (see GITIGNORE_RECOMMENDATIONS) plus two REVIEW-classified small tracked files. No blocking condition from Section 17 was found (no secret in tracked content, no real IST content tracked, no oversized single tracked file, no history-rewrite requirement).

## EXECUTIVE_SUMMARY

- Working tree total: **9,996,610,622 bytes (~9.31 GiB)**, across 1,754 files (includes `.git`).
- Of that, **9,985,777,928 bytes (~9.30 GiB, 57 aggregated/expanded rows in the CSV)** is generated legacy-analysis output that is either already `.gitignore`-excluded (V1-V3 full/repro scan dumps, leftover smoke-test output, `__pycache__`) or untracked-and-not-yet-ignored (`output/v4_2_r7_ist_operacional/`, the real IST pilot — 1.3 GiB / 40 files).
- **Currently tracked content is only ~6.79 MB (647 files)**; virtually all of it is source, tests, docs, prompts, codex history, tooling, config, and small contracts/baselines/examples under `output/`. This already matches the KEEP doctrine in Section 5.
- `.git` directory is **~4.03 MB** (3 packs, 945 objects; loose 1.06 MiB + pack 2.63 MiB). No history bloat.
- Net effect: **no tracked file needs to be removed**. The one real risk is that `output/v4_2_r7_ist_operacional/` is untracked but NOT yet covered by `.gitignore` — it could be accidentally `git add`ed. This is the main actionable finding.
- Two tracked files (`output/LEVANTAMIENTO_FUNCIONAL.md`, `output/LEVANTAMIENTO_TECNICO.md`) have ambiguous current role and are classified REVIEW rather than KEEP or EXCLUDE.
- V5 continuity from a clean clone using only current tracked (KEEP) files: **YES** (see V5_CONTINUITY_CHECK).

## REPOSITORY_SIZE

| Metric | Value |
|---|---|
| CURRENT_WORKING_TREE_SIZE | 9,996,610,622 bytes (~9.31 GiB), 1,754 files |
| CURRENT_TRACKED_CONTENT_SIZE | 6,793,577 bytes (~6.48 MiB), 647 files (`git ls-files` + `stat`) |
| CURRENT_GIT_DIRECTORY_SIZE | 4,025,642 bytes (~3.84 MiB) on disk; `git count-objects -vH`: count=471 loose (1.06 MiB), in-pack=945, packs=3, size-pack=2.63 MiB, garbage=0 |
| TARGET_UNDER_100_MB | **YES** (tracked content ~6.8 MB) |
| TARGET_UNDER_200_MB | **YES** |

Working tree vs tracked vs `.git` are three very different numbers here: the working tree is dominated (>99.9%) by untracked/ignored generated output that never entered Git history in its current form (except one large historical blob, see GIT_HISTORY_SIZE).

## DIRECTORY_SIZE_BREAKDOWN

Top-level, full working tree (files + bytes, descending):

| Dir | Files | Size |
|---|---|---|
| output | 473 | 9,984,237,069 (~9.30 GiB) |
| .git | 512 | 4,025,642 (~3.84 MiB) |
| tests | 138 | 2,498,314 (~2.38 MiB) |
| legacy_documenter | 338 | 2,385,417 (~2.27 MiB) |
| docs | 93 | 1,172,472 (~1.12 MiB) |
| prompts | 70 | 1,088,318 (~1.04 MiB) |
| codex | 105 | 936,091 (~0.89 MiB) |
| tools | 18 | 252,201 |
| result_codex | 1 | 2,076 |
| context | 1 | 0 |

`output/` internal breakdown (directories, descending by size) — the dominant cost centers:

| Subdir | Files | Size | Git status |
|---|---|---|---|
| v2_r5_full | 34 | 1,347,864,019 | ignored |
| v4_2_r7_ist_operacional | 40 | 1,341,333,709 | **untracked, NOT ignored** |
| v2_r5_1_full | 34 | 1,277,912,605 | ignored |
| v2_r5_1_repro | 34 | 1,277,912,605 | ignored |
| v2_r4_1_repro_b | 29 | 998,734,139 | ignored |
| v2_r4_1_full | 29 | 998,734,139 | ignored |
| v2_r4_1_repro_a | 29 | 998,734,137 | ignored |
| v2_r4_full | 29 | 955,832,146 | ignored |
| v3_r8_1 | 7 | 755,252,732 | ignored |
| v1_r1_full | 17 | 30,292,015 | ignored |
| (all other output/v3_*, v4_*, v4_1_*, v4_2_r8) | ~90 combined | ~1.0 MB combined | tracked (KEEP: contracts/examples/baselines) |
| v1_r1_internal, v2_r4_1_internal, context, documentation, index | ~70 combined | ~30 KB combined | ignored (leftover smoke-test) |

`legacy_documenter/`, `tests/`, `tools/` sizes above include ignored `__pycache__/` content mixed with tracked source — tracked-only size is captured precisely per-file in the CSV.

## FILE_TYPE_BREAKDOWN

Whole working tree, by extension (descending size):

| Ext | Count | Size |
|---|---|---|
| .json | 349 | 9,899,313,862 |
| .md | 396 | 88,131,894 |
| .pyc | 237 | 3,147,249 (ignored cache) |
| .pack | 3 | 2,723,099 (`.git`) |
| .py | 243 | 1,985,111 |
| (no ext) | 489 | 1,242,143 (mostly `.git` internals + a few extensionless docs) |
| .idx | 3 | 29,676 (`.git`) |
| .sample | 14 | 26,788 (`.git/hooks` samples) |
| .rev | 3 | 3,936 (`.git`) |
| .gitignore | 1 | 3,189 |
| .vb/.vbproj/.sln/.aspx | 15 | 3,675 (synthetic legacy-app test fixtures under `tests/`) |
| .gitkeep | 1 | 0 |

`.json` dominates almost entirely because of the untracked/ignored generated-analysis dumps (index/*.json full-repository extraction files, 90–390 MB each). Tracked `.json` (contracts/baselines/examples) totals well under 1 MB.

## LARGEST_FILES

All files >1 MB in the working tree are inside `output/` and are either already-`.gitignore`-excluded historical full-scan dumps (V1–V3) or the untracked real-IST pilot (`v4_2_r7_ist_operacional`). **None are tracked by Git.** Selected largest (full list of >1MB in CSV/underlying data):

| Path | Size | Tracked | Classification |
|---|---|---|---|
| output/v3_r8_1/DEEP_ANALYSIS_FLOWS.json | 388.6 MB | no (ignored) | EXCLUDE |
| output/v3_r8_1/DEEP_ANALYSIS_EVIDENCE.json | 361.8 MB | no (ignored) | EXCLUDE |
| output/{v2_r5_full,v2_r5_1_full,v2_r5_1_repro,v2_r4_1_repro_a,v2_r4_1_repro_b,v2_r4_1_full,v2_r4_full}/index/functional_dependencies.json | 227.2 MB each (7 copies) | no (ignored) | EXCLUDE |
| output/v4_2_r7_ist_operacional/index/functional_dependencies.json | 227.2 MB | no (untracked, gap) | EXCLUDE |
| output/{v2_*}/index/calls.json (7 copies) + v4_2_r7_ist_operacional/index/calls.json | 211.6 MB each | no | EXCLUDE |
| ... (functional_flows.json, functional_paths.json, flow_unresolved.json, data_parameters.json, ARCHITECTURE_GRAPH.json, TRACEABILITY.json — each 55–145 MB, duplicated 5–8x across v2_* rounds and v4_2_r7_ist_operacional) | | no | EXCLUDE |

Buckets: >50 MB: ~45 files (all in the 9 ignored V1–V3 dump dirs + IST pilot). >25 MB: same set plus a few smaller index files. >10 MB / >5 MB / >1 MB: same 10 directories only — no tracked file anywhere in the repo exceeds 1 MB (largest tracked file is `docs/V4_1/...` class markdown / `output/v4_r1_1/V4_LARGE_ARTIFACT_ANALYSIS.json`, all well under 200 KB).

PURPOSE (all buckets): raw extraction indexes / deep-analysis evidence / AI context bundles produced by running `main.py` against a legacy repository (V1–V3 rounds) or the real IST pilot (V4.2 R7). CAN_REGENERATE: yes, via `python main.py "<legacy_repo>" --output "output/<name>" --verbose` per `docs/PROJECT_RECOVERY.md` and the `.gitignore` header comment — except the real IST run, which requires the actual IST repository (out of scope here, and per task constraints must not be accessed). NEEDED_FOR_V5: no (V5 begins from source/tests/contracts, not from a specific legacy-repo's extraction). NEEDED_FOR_HISTORY: no for raw dumps (the narrative findings are captured in tracked `docs/V4_2/V4_2_R7_*RESULT.md` and `V4_2_R7_1_FINDINGS_VERIFICATION.md`, and a synthetic committable fixture exists at `tests/fixtures` + `tests/test_v4_2_r7_synthetic_full_fixture.py`). RECOMMENDATION: keep excluded (8 of 9 dirs already are); close the `.gitignore` gap for `v4_2_r7_ist_operacional`.

## GIT_HISTORY_SIZE

`git count-objects -vH`: 945 objects in 3 packs (2.63 MiB) + 471 loose objects (1.06 MiB), 0 garbage. Total `.git` on-disk size 4.03 MB — small, no optimization needed.

Non-destructive `git rev-list --objects --all | git cat-file --batch-check` scan (largest historical blobs, descending):

| Size | Path (as recorded in history) |
|---|---|
| 8,693,162 | output/v1_r1_full/index/dependencies.json |
| 8,081,952 | output/v1_r1_full/index/symbols.json |
| 4,222,516 | output/v1_r1_full/index/webforms.json |
| 3,515,202 | output/v1_r1_full/index/files.json |
| 1,358,274 | output/v1_r1_full/documentation/WEBFORMS_MAP.md |
| 1,250,494 | output/v1_r1_full/index/projects.json |
| 965,676 | output/v1_r1_full/documentation/PROJECT_DEPENDENCIES.md |
| 881,709 | output/v1_r1_full/context/projects.json |
| (remaining) | all <270 KB — round result/report/test files |

Finding: `output/v1_r1_full/**` was committed at some point in V1 history (before the current `.gitignore` exclusion rule existed — `.gitignore` history shows 4 historical edits) and now lives only as historical blobs, compressed well inside the 2.63 MiB pack. It is NOT present in the current tracked snapshot (`git ls-files` confirms). **This explains a small amount of `.git` size but does not push it out of range** (.git is 4 MB total). CURRENT SNAPSHOT CLEANUP (this audit's scope) is unaffected. GIT HISTORY CLEANUP (rewriting history to purge these old blobs) is a separate Technical Lead decision — not required to hit the <100 MB / <200 MB targets, since `.git` is already ~4 MB.

## KEEP

645 tracked files (see CSV), covering: `main.py`, `legacy_documenter/**` (source), `tests/**` (test suite backing the 1809-test baseline), `tools/**` (build/report/inventory tooling), `docs/**` (V3/V4/V4_1/V4_2 technical+user manuals, glossary, round closure results), `prompts/**` (V4/V4_1/V4_2 round prompts incl. the plan prompt for this audit), `codex/**` (V1–V3 historical dev-agent instructions/results, names preserved), `result_codex/` (V1 analysis report), `context/.gitkeep` (runtime dir placeholder), `AGENTS.md`, `CLAUDE.md`, `PROJECT_STATE.json`, `.gitignore`, and small `output/**` contracts/examples/baselines/manifests (`output/v3_final/V3_FINAL_BASELINE.json`, `output/v4_1_r10/V4_1_FINAL_*`, `output/v4_2_r8/V4_2_FINAL_*`, `output/v4_r14/V4_FINAL_*`, `output/v4_r*/**` contract+example JSON pairs, `output/v4_r11/example_docs/**`, `output/v3_r*/**` small round-assessment JSON). Full per-file list with rationale: CSV column `reason`.

## EXCLUDE

57 rows in the CSV (40 individual files + 17 aggregated directory rows covering hundreds more files), all already either `.gitignore`-excluded or untracked, none currently tracked:
- `output/v4_2_r7_ist_operacional/**` (40 files, 1.34 GiB) — real IST pilot operational output. **Untracked but currently NOT matched by any `.gitignore` rule** (gap).
- `output/{v1_r1_full,v2_r4_full,v2_r4_1_full,v2_r4_1_repro_a,v2_r4_1_repro_b,v2_r5_full,v2_r5_1_full,v2_r5_1_repro,v3_r8_1}/` (9 dirs, ~8.64 GiB) — already excluded by explicit `.gitignore` path rules.
- `output/{context,documentation,index,v1_r1_internal,v2_r4_1_internal}/` — leftover smoke-test output, already excluded.
- `__pycache__/` under `legacy_documenter/**`, `tests/`, `tools/**` — Python bytecode cache, already excluded.

No currently-tracked file was classified EXCLUDE.

## REVIEW

2 tracked files:
- `output/LEVANTAMIENTO_FUNCIONAL.md` (25,969 bytes)
- `output/LEVANTAMIENTO_TECNICO.md` (34,114 bytes)

Both carry `document_status=APPROVED` / `provider=COPILOT` metadata headers suggesting they are generated documentation output (functional/technical elicitation) rather than authored project documentation, but sit at `output/` root (not under any versioned round directory) with no obvious cross-reference found from `docs/V3`/`docs/V4*` closure results during this audit. Small (60 KB combined) — size is not a concern. Per Section 5 ("ante duda: REVIEW > EXCLUDE"), not reclassified to EXCLUDE. **Technical Lead should confirm**: (a) which round produced them, (b) whether a corresponding `docs/V3` or `codex/v3` result references them, (c) KEEP (historical round evidence) vs relocate-in-place documentation vs candidate for future cleanup. No action taken.

## GENERATED_ANALYSIS_OUTPUT_POLICY

Confirmed split holds cleanly across the current repository:
- **(A) Operational output** (raw extraction/analysis of a concrete legacy system): all 9 V1–V3 full/repro dump directories + `v4_2_r7_ist_operacional` → EXCLUDE, none tracked, consistent with policy.
- **(B) Development/contract output** (small artifacts proving a contract/round/closure): all `output/v4_*`, `output/v3_r*`, `output/v3_final`, `output/v4_1_r10`, `output/v4_2_r8` content → tracked KEEP, sizes trivial (largest ~140 KB).

No blanket `output/`-ignoring rule exists or is recommended; the existing `.gitignore` already implements the path-based approach mandated by Section 8.

## HISTORICAL_EVIDENCE_POLICY

`codex/` (v1, v2 incl. R1–R5, v3) and `result_codex/` preserved verbatim, all tracked, all classified KEEP/history, no renames. `docs/V3`, `docs/V4`, `docs/V4_1`, `docs/V4_2` retain every round's `*_RESULT.md` and `*_CLOSURE_AND_VERSIONING_RESULT.md` — this is the audit trail a new agent needs to reconstruct decisions without replaying the actual work. `prompts/V4`, `prompts/V4_1`, `prompts/V4_2` retain every round prompt used to drive execution (agent-neutral reproducibility). No historical document, prompt, or codex file was found to be excludable; none removed or renamed.

## V5_CONTINUITY_CHECK

**Could a new agent/programmer clone this repo today (KEEP files only) and start V5 correctly? YES.**

Coverage check:
- Agent bootstrap: `CLAUDE.md` → `AGENTS.md` → `PROJECT_STATE.json` → `docs/V4/V4_AI_HANDOVER.md` → `output/v3_final/V3_FINAL_BASELINE.json` → active `prompts/V4_2/` prompt — full chain present and tracked.
- Current state: `PROJECT_STATE.json` (V4.2, V4_2_FORMALLY_CLOSED, R8, 1809 tests) tracked.
- Architecture/contracts: `docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md`, `V4_CONTRACT_FOUNDATION.md`, plus every `output/v4_r*` contract+example pair — tracked.
- Code + tests + fixtures: `legacy_documenter/**`, `tests/**` (incl. `tests/fixtures`, synthetic full-fixture test) — tracked.
- Tooling: `tools/**` — tracked.
- Documentation/manuals/glossary: `docs/V4/V4_DEVELOPER_MANUAL.md`, `V4_USER_MANUAL.md`, `docs/V4_1/LEGACYMAPPER_GLOSSARY_V4_1.md`, `docs/V4_2/LEGACYMAPPER_*_MANUAL_V4_2.md` — tracked.
- Decisions/known debt: round `*_RESULT.md` files across `docs/V4*`, `codex/v3` human-review records — tracked.
- V4.2 final state: `output/v4_2_r8/V4_2_FINAL_BASELINE.json` + `V4_2_FINAL_MANIFEST.json`, `docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md` — tracked.
- Real-pilot findings (without needing the raw 1.3 GiB dump): `docs/V4_2/V4_2_R7_REAL_IST_PILOT_AND_COMMITTABLE_FIXTURE_RESULT.md`, `V4_2_R7_1_REAL_PILOT_FINDINGS_CORRECTION_RESULT.md`, `V4_2_R7_1_FINDINGS_VERIFICATION.md`, plus `tests/test_v4_2_r7_synthetic_full_fixture.py` and `tests/test_v4_2_r7_1_real_pilot_findings_correction.py` with their fixtures — tracked, and this is exactly the "committable fixture" pattern the R7 round title describes.

No local/untracked file was identified whose loss would block V5 continuity. `output/v4_2_r7_ist_operacional/` is explicitly excluded by design (real client data), not a continuity gap — its findings were already distilled into the tracked result docs/fixtures above.

## GITIGNORE_RECOMMENDATIONS

Do not modify `.gitignore` in this task (read-only). Proposal for Technical Lead:

**ADD** (closes the confirmed gap):
```
# Real-system operational pilot output (contains findings from a real
# analyzed legacy system; must never enter Git). Distilled findings live
# in docs/V4_2/V4_2_R7_*_RESULT.md and tests/fixtures (synthetic, committable).
/output/v4_2_r7_ist_operacional/
```
General pattern suggestion: adopt the same opt-in convention already used for future ad-hoc runs (`/output/_local_*/`) for any future real-system pilot directory, e.g. document in `docs/GENERATED_ARTIFACT_POLICY.md` that real-system pilot output directories must be named so they either match an explicit new `.gitignore` line (as above) or the existing `_local_` prefix convention, added at pilot-creation time rather than discovered post-hoc.

**KEEP AS-IS**: all existing explicit path-based rules (`/output/v1_r1_full/`, the V2 full/repro set, `/output/v3_r8_1/`, the leftover-smoke-test set, `/context/*` with `.gitkeep` exception, `__pycache__/`, venv/build/cache patterns). These are correctly scoped and do not use broad wildcards over `output/`, `docs/`, or `prompts/` — consistent with the repo's stated principle.

**NO CHANGE NEEDED** to `docs/`, `prompts/`, `codex/`, `tests/`, `legacy_documenter/`, `tools/` — none are wildcard-ignored today and none should be.

## PROPOSED_CLEANUP

**SAFE_EXCLUSIONS** (already fully outside Git, add/keep `.gitignore` coverage only, no data loss risk):
- Add the one missing `.gitignore` line for `/output/v4_2_r7_ist_operacional/`. V5 continuity unaffected — see V5_CONTINUITY_CHECK (findings already distilled into tracked docs/fixtures).
- No tracked file needs removal.

**REQUIRES_TECHNICAL_LEAD_REVIEW**:
- `output/LEVANTAMIENTO_FUNCIONAL.md`, `output/LEVANTAMIENTO_TECNICO.md` — confirm role before any future action; no action taken here.
- Whether to formally document the real-pilot-output naming convention in `docs/GENERATED_ARTIFACT_POLICY.md` so this gap class doesn't recur (R7.2, R8, etc. would hit the same gap otherwise for any next real pilot).

**MUST_KEEP**: everything in the KEEP list (645 files) — bootstrap, source, tests, tooling, docs, prompts, codex history, contracts/baselines/manifests. Unconditional per Section 5/7.

**OPTIONAL_GIT_HISTORY_OPTIMIZATION**: historical `output/v1_r1_full/**` blobs (~30 MB total across ~9 files) sitting in old commits, compressed into the 2.63 MiB pack. Purging via `git filter-repo`/BFG would save negligible space (`.git` is already 4 MB) and is NOT recommended purely for size. Flagged only for completeness per Section 12; this is explicitly a separate Technical Lead decision and was not executed (no destructive git operation was run).

## EXPECTED_SIZE_AFTER_CLEANUP

Since no tracked content changes, and the only proposed cleanup is a `.gitignore` addition (which affects future `git add` safety, not current repository size):

- EXPECTED_REPOSITORY_SNAPSHOT_SIZE_AFTER_CLEANUP (tracked content in a fresh clone) = **unchanged, ~6.79 MB** (plus whatever `.git` overhead the remote already carries, currently ~4 MB locally).
- PROPOSED_KEEP_SIZE = 6,733,494 bytes (KEEP rows) + 60,083 bytes pending REVIEW decision = **~6.79 MB** total tracked-eligible content.
- PROPOSED_EXCLUDED_SIZE = 9,985,777,928 bytes (~9.30 GiB), already outside Git today except for the `.gitignore` gap.
- TARGET_UNDER_100_MB = YES. TARGET_UNDER_200_MB = YES. No category is pushing the repo over either threshold; the repository is already effectively at target size for its tracked content.

## RISKS

1. **`output/v4_2_r7_ist_operacional/` is not `.gitignore`-covered.** A routine `git add -A` or `git add output/` by any contributor would stage 1.3 GiB of real-system data, including a real legacy system's internal names/structure. This is the single most important finding of this audit. No file has been added to Git as part of this task; it remains untracked exactly as found.
2. Two REVIEW files (`output/LEVANTAMIENTO_*`) have unclear provenance; low size/risk but flagged for Technical Lead judgment rather than silently kept or excluded.
3. `git` history retains `output/v1_r1_full/**` blobs from before the exclusion rule existed. Low impact today (4 MB total `.git`), but if repository history is ever exported/audited externally, this real-history detail should be known (these are V1 fixture/legacy-repo-analysis artifacts, not confirmed to contain third-party sensitive data in this audit — not independently re-verified here beyond the file-type/path check).
4. No secret material was found in any tracked file; one prior self-documented false-positive note exists in `output/v4_r1_1/V4_GITHUB_SUITABILITY.json` (fake test credentials + env-var *names* only) — re-confirmed by an independent grep in this audit, no literal secret values found.

## TECHNICAL_LEAD_DECISIONS_REQUIRED

1. Approve adding the proposed `.gitignore` line for `/output/v4_2_r7_ist_operacional/` (and decide the general naming convention for future real-pilot output directories).
2. Resolve REVIEW classification of `output/LEVANTAMIENTO_FUNCIONAL.md` / `output/LEVANTAMIENTO_TECNICO.md`.
3. Decide whether the historical `output/v1_r1_full/**` blobs in git history warrant a history rewrite (OPTIONAL_GIT_HISTORY_OPTIMIZATION) — recommendation is NO, not worth the disruption for ~30 MB, but this is explicitly a Technical Lead call, not an audit finding requiring action.

## NEXT

**READY_FOR_TECHNICAL_LEAD_CLEANUP_REVIEW.** No cleanup was executed. No V5 work was started. No manuals were updated. Await Technical Lead decision on the 3 items above; once the `.gitignore` gap is closed, the repository requires no further size-related action to remain V5-ready from a clean clone.
