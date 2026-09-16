# Post-V4.2 User/Technical Manuals and Glossary — Result

## AMENDMENT (Post-V4.2 documentation and historical manifest reconciliation round)

This document's `TEST_ARCHITECTURE_VERIFICATION` and `SOURCE_VS_DOCUMENTATION_DISCREPANCIES` sections below
report exactly what this round observed and is preserved unchanged as the historical record of that
observation: `Ran 1625 tests ... FAILED (failures=2, errors=19)` on this round's own fresh-checkout run, with
root cause traced to an untracked `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`. A subsequent Post-V4.2
fresh-clone reproducibility correction round diagnosed and resolved that gap (see
`docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION_RESULT.md`), and a further Post-V4.2
documentation-and-manifest reconciliation round corrected the one remaining manifest-hash-verification test
failure it left behind, without touching any historical hash, the V4.2 final manifest/baseline, or
production code (see
`docs/V4_2/POST_V4_2_DOCUMENTATION_AND_HISTORICAL_MANIFEST_RECONCILIATION_RESULT.md`). The User Manual
(§4.6, §4.13) and Technical Manual (§16, §19, §20) were updated by that later round to describe the
corrected, current fresh-clone behavior (1809 discovered, 0 failures, 0 errors, 132 explained skips;
`readiness` READY, exit 0). This document's own body is left as originally written, as the accurate record
of what this round found at the time.

## STATUS

COMPLETE

## FILES_CREATED

- `docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md`

## FILES_UPDATED

- `docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md` (pre-existing tracked file, 173 lines; replaced with a
  current-source-verified version, 469 lines net diff)
- `docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md` (pre-existing tracked file, 158 lines; replaced with a
  current-source-verified version, 797 lines net diff)
- This result document (`docs/V4_2/POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY_RESULT.md`)

No other file was created, updated, or deleted. `PROJECT_STATE.json`, `AGENTS.md`, `CLAUDE.md`, all
production source under `legacy_documenter/`, all files under `tests/`, and all baseline/manifest files
under `output/` were read but not modified.

## USER_MANUAL_SUMMARY

`docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md`, 13 numbered sections (§4.1–§4.13) plus a header, covering:
purpose and the "Python discovers, AI interprets" principle with the V5-scope boundary stated explicitly;
evidence-based installation/prerequisites (no invented package manager/env vars); the CLI grammar including
the legacy bare-positional compatibility rewrite; `analyze` and `full` documented separately with their
real behavioral divergence; `readiness` documented as a self-check of LegacyMapper's own knowledge state,
including the fresh-checkout `ARCHITECTURE_EVIDENCE.json` gap found this round; AI interpretation's actual
current behavior (provider resolution, safety guard, the `ProviderRegistry` FAKE/COPILOT-only reality);
output-tree navigation including the V4.2-R8 navigation/partition split; the authoritative exit-code table;
rerun/recovery guarantees; the real-system operational-output policy; the approval boundary stated as
implemented-vs-not; and an evidence-based troubleshooting table (no invented error messages).

## TECHNICAL_MANUAL_SUMMARY

`docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md`, 18 numbered sections (§6–§23) following the plan's
mandatory outline: repository map; module inventory; file map; execution architecture; full pipeline;
extraction/analysis; documentation system; AI architecture; knowledge architecture; contracts/data models;
test architecture; tooling; continuity/agent handover; generated-artifact policy; known technical debt;
code audit map; maintainability inventory; V5 handover. Approximately 800 lines of net addition over the
prior draft, built entirely from files actually read this round (main.py, the full `legacy_documenter/`
tree, `PROJECT_STATE.json`, `.gitignore`, `docs/GENERATED_ARTIFACT_POLICY.md`, the V4.2 final closure/
baseline/manifest, and a live test-suite run).

## MODULE_INVENTORY_SUMMARY

§7 covers 15 top-level packages under `legacy_documenter/` (cli, scanner, extractors, analysis, exporters,
context, documentation, knowledge, llm, orchestration, models, quality, utils, config.py, package-level
main.py) plus a dedicated 14-row sub-table for `knowledge/`'s 14 sub-packages, explicitly marking which are
reachable from the CLI (only `proposals/` and `readiness.py`) versus implemented-but-unorchestrated
(`approval/`, `canonical/`, `projection/`, `plugin_projection/`, and the upstream `input/`/`ingestion/`/
`provenance/`/`classification/`/`temporal/`/`relations/` chain).

## FILE_MAP_SUMMARY

§8 individually documents ~40 significant files with responsibility/key class/collaborators/tests, grouping
only genuinely small, cohesive, low-risk files (the eight `models/*.py` dataclass files; the knowledge
sub-packages' `enums.py`/`contract_report.py`/`example_report.py` files; V3-era `documentation/*.py`
helpers beyond `generator.py`/`renderer.py`). No significant production `.py` file was omitted for being
"internal."

## EXECUTION_ARCHITECTURE_VERIFICATION

Verified directly from source (`legacy_documenter/cli/parser.py`, `router.py`, `main.py`,
`full_pipeline.py`, `pipeline_stages.py`): `analyze` and `full` call the identical shared stage functions in
`cli/pipeline_stages.py`; they diverge only in failure-handling strategy (`analyze`: unguarded, propagates
exceptions; `full`: per-stage try/except via `_run_stage`/`_skipped`). The 13-stage vocabulary
(`StageId`) and the `RunResult`/`StageResult`/`RunStatus`/`StageStatus` contract were read in full and are
documented in Technical Manual §9–§10 with the exact stage-dependency graph as implemented (not as
originally planned in older round documents).

## TEST_ARCHITECTURE_VERIFICATION

`python -m unittest discover -s tests` was executed in this session (no test file modified before, during,
or after). Result: `Ran 1625 tests in 66.575s / FAILED (failures=2, errors=19)`. This was investigated to
root cause rather than reported blindly: 19 of the 21 non-passing tests, plus the two remaining failures,
trace to `legacy_documenter/knowledge/readiness.py`'s hardcoded dependency on
`output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`, a file confirmed (via `git log --all`) to have **never been
tracked in this Git repository** and excluded by `.gitignore` as a "heavy regenerable artifact." This is
reported as historical-vs-live rather than as a claim that the suite currently passes 1809/1809; the
historical `1809_PASS_0_FAIL_0_SKIP` V4.2 closure figure is reported explicitly as historical in both the
User Manual (§4.6, §4.13) and Technical Manual (§16, §20).

## MAINTAINABILITY_INVENTORY

Computed this round via `legacy_documenter.quality.maintainability_audit.audit('.')` (AST-only, no runtime
import): 169 production `.py` files, 181 classes, 705 functions/methods, 80.14% typing coverage (77.8%
significant-boundary), 76.52% docstring coverage (93.87% significant), 10 large-module candidates (>250
lines), 28 multiple-responsibility candidates. Full top-15-by-lines table recorded in Technical Manual §22.
`legacy_documenter/exporters/technical_documentation_renderer.py` was directly measured at **802 lines**
(`wc -l`), exactly matching the historical V4.2-R8 closure baseline figure cited in
`PROJECT_STATE.json: maintainability_debt` — no drift found.

## CODE_AUDIT_MAP_SUMMARY

§21 groups production code into 8 audit areas (CLI/orchestration; deterministic extraction; deterministic
analysis/resolution; documentation rendering; context/AI seam; knowledge domain; readiness/closure tooling;
governance/continuity), each with concrete complexity concerns, relevant contracts/tests, known debt
cross-references, and specific audit questions (never framed as findings unless evidence already supports
one, per the plan's explicit instruction).

## KNOWN_DEBT_VERIFICATION

§20 documents 12 debt items: the three from `PROJECT_STATE.json.r7_findings` (F-05 deferred-by-determinism-
contract, F-06/F-07 preserved observations, verified against
`docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md`); the two `documentation_remaining_scale_debt` entries
(`WEB_ENTRY_POINTS.md`, `PROJECT_DEPENDENCIES.md`); the `maintainability_debt` entry
(`technical_documentation_renderer.py`, re-measured this round, unchanged); the `r6_intermittent_test` known
risk; `approval_surface_implementation=NOT_IMPLEMENTED` and `plugin_runtime=NOT_IMPLEMENTED`; and three
items newly documented this round from direct source/test inspection: the untracked
`ARCHITECTURE_EVIDENCE.json` fresh-checkout gap (and its manifest-hash-check consequence), and
`GeminiProvider` being implemented but unreachable through `ProviderRegistry`. No debt item was fixed;
every one is reported status-only per the plan's explicit instruction not to fix debt in this task.

## GLOSSARY_SUMMARY

`docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md`, ~40 terms, covering every term the plan's §24 lists as
"applicable" plus terms discovered in code (`GAP`, `confirmed terminal`, `FakeLLMProvider`, `findings`,
`agent-neutral continuity`). Each definition states the term's actual LegacyMapper semantics with a source
reference, not a generic definition; explicitly notes the `context` (package) vs `context/` (runtime
directory) naming collision and that "KNO identifier" and `knowledge_id` are the same field.

## CROSS_DOCUMENT_CONSISTENCY

Verified consistent across all three documents: CLI commands (`analyze`/`full`/`readiness` + legacy
bare-positional); exit codes (0/1/2/4, `USAGE` never assigned by application code); AI behavior (off by
default, `ProviderRegistry` currently FAKE/COPILOT only, `GeminiProvider` unreachable — stated identically
in the User Manual §4.7, Technical Manual §13, and flagged as debt AI-01 in §20); the approval boundary
(implemented: proposal generation; not implemented: approve/reject CLI, `run_id`-bound approval, automatic
canonical promotion, R11/R12 orchestration, Plugin runtime — stated identically in User Manual §4.12,
Technical Manual §14/§23, and the Glossary's Technical Lead/Approval/Plugin runtime entries); Plugin status
(`NOT_IMPLEMENTED` everywhere it is mentioned); V5 status (`next = V5_DESIGN_PENDING`, nothing implemented,
stated identically in User Manual §4.1 and Technical Manual §23); operational output policy (identical
wording basis from `docs/GENERATED_ARTIFACT_POLICY.md` in User Manual §4.11 and Technical Manual §19);
supported technologies (.NET Framework/VB.NET/ASP.NET Web Forms/Oracle, stated identically in User Manual
§4.1 and Technical Manual §23); terminology (Glossary is the single source for every term used across both
manuals — no manual defines a term differently from the Glossary).

## SOURCE_VS_DOCUMENTATION_DISCREPANCIES

1. **Test count / readiness on a fresh checkout.** `PROJECT_STATE.json` states `"tests": 1809` and
   `"readiness": "READY"`. A fresh-checkout run of `python -m unittest discover -s tests` in this session
   produced `Ran 1625 tests ... FAILED (failures=2, errors=19)`. Root cause: `output/v3_r8_1/
   ARCHITECTURE_EVIDENCE.json`, which `legacy_documenter/knowledge/readiness.py::_execute` hard-requires,
   was never a tracked file in this Git repository (`git log --all` shows no history for it) and is
   excluded by `.gitignore` as a "heavy regenerable artifact," even though no regeneration command for that
   specific file is documented anywhere. This is not a regression caused by this round (no test/production
   file was touched) — it is a pre-existing gap between what V4.2 closure recorded (from an environment that
   apparently had this local, untracked file) and what any fresh clone of this repository can currently
   reproduce. Documented as debt items TESTINFRA-01/BASELINE-01 in the Technical Manual §20, and reported
   accurately (not silently copied) in both manuals per the plan's explicit instruction.
2. **`V4_2_FINAL_MANIFEST.json` hash-integrity test failure**, same root cause as #1 — the manifest records
   a hash for a file under `output/v3_r8_1/` that is absent on this checkout.
3. **`GeminiProvider` implemented but unreachable.** `legacy_documenter/llm/providers/gemini.py` defines a
   concrete provider, but `legacy_documenter/llm/core.py::ProviderRegistry.create` only routes
   `"FAKE"`/`"COPILOT"`. No V4.2 document found describes this as an intentional exclusion; documented as
   debt item AI-01 rather than described anywhere as an implemented capability.
4. **No other contradiction was found** between the V4.2 closure documents' capability/boundary claims
   (`docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md`'s `CAPABILITIES`/`NOT_IMPLEMENTED_BOUNDARIES`)
   and the current source: the ten fixed documentation filenames, the V4.2-R8 navigation/partition split,
   the exit-code contract, the approval-surface/Plugin-runtime `NOT_IMPLEMENTED` status, and the
   `technical_documentation_renderer.py` 802-line maintainability figure were all independently verified
   against current source and matched exactly.

## REAL_PROVIDER_CALLS

0

## REAL_IST_ACCESSED

false

## PRODUCTION_CODE_CHANGED

false

## TESTS_CHANGED

false

## V4_2_REOPENED

false

## V5_IMPLEMENTED

false

## PLUGIN_RUNTIME

NOT_IMPLEMENTED

## APPROVAL_SURFACE_IMPLEMENTATION

NOT_IMPLEMENTED

## VALIDATION

Performed this round, all read-only against production/test code and existing tracked documents:

- Inspected the current CLI parser/router implementation in full (`legacy_documenter/cli/parser.py`,
  `router.py`, `execution_model.py`, `stage_identity.py`, `full_pipeline.py`, `pipeline_stages.py`).
- Inspected the current production package tree in full (`find legacy_documenter -name "*.py"`, 169
  files); read every file referenced in the Technical Manual's file map directly.
- Inspected the current test tree (62 modules listed via `find tests`) and executed the full suite once
  (see TEST_ARCHITECTURE_VERIFICATION above); no test was altered before, during, or after the run.
- Inspected `tools/` (all 5 non-historical entries plus the `v4_1_r0/` sub-package) for purpose/state
  mutation/output.
- Inspected `PROJECT_STATE.json` in full.
- Inspected `.gitignore` in full and cross-checked its rules against `git log --all` history for the
  specific file this round found missing.
- Inspected `docs/GENERATED_ARTIFACT_POLICY.md` in full.
- Inspected the V4.2 final closure (`docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md`) and final
  baseline/manifest (`output/v4_2_r8/V4_2_FINAL_BASELINE.json`, `V4_2_FINAL_MANIFEST.json`, existence and
  path only — full byte-level manifest verification was not re-run since that is the failing test's own
  job, already inspected and reported above).
- Inspected known-debt sources: `PROJECT_STATE.json`'s `r7_findings`, `documentation_remaining_scale_debt`,
  `maintainability_debt`, `known_risks`, `approval_surface_implementation`, `plugin_runtime`, plus
  `docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md` and `docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md`.
- Verified no real AI/LLM provider call occurred: no `--allow-ai-interpretation` invocation of `python
  main.py full` was made at any point in this round; the only pipeline invocation observed in tool output
  during investigation (visible in the Bash history) was a pre-existing test artifact from the suite run
  itself, using the suite's own `FakeLLMProvider`/deterministic fixtures, never a live run initiated by
  this round's own commands against a real repository.
- Verified no real IST/Operacional access occurred: `C:\Users\cgalianj\source\IST_40\operacional` was never
  referenced, read, or scanned by any command run in this round.
- Verified no production/test file was modified: `git status --porcelain` before finalizing this document
  shows changes limited to the three manuals plus this result document (and the pre-existing untracked
  prompt file for this round, `prompts/V4_2/POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY.md`, which this
  round did not create or modify).

## GIT_STATUS

Working tree changes at the end of this round (`git status --porcelain`):

```
 M docs/V4_2/LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md
 M docs/V4_2/LEGACYMAPPER_USER_MANUAL_V4_2.md
?? docs/V4_2/LEGACYMAPPER_GLOSSARY_V4_2.md
?? docs/V4_2/POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY_RESULT.md
?? prompts/V4_2/POST_V4_2_USER_TECHNICAL_MANUALS_AND_GLOSSARY.md
```

The two manual files (`LEGACYMAPPER_USER_MANUAL_V4_2.md`, `LEGACYMAPPER_TECHNICAL_MANUAL_V4_2.md`) were
already tracked, pre-existing files in this repository before this round (173 and 158 lines respectively);
this round replaced their content with a version freshly derived from the current source tree, per this
round's explicit authorization to update them. No commit was made and no push occurred.

## DECISION

POST_V4_2_DOCUMENTATION_READY_FOR_TECHNICAL_LEAD_REVIEW

## NEXT

HUMAN_DOCUMENTATION_REVIEW
