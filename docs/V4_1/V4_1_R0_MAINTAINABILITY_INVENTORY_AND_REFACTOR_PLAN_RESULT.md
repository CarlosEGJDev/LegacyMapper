# LegacyMapper V4.1-R0 — Maintainability Inventory and Refactor Plan — Result

```text
STATUS=V4_1_R0_MAINTAINABILITY_INVENTORY_COMPLETE

ENTRY_GATE=PASS_WITH_ONE_PRE_EXISTING_TEST_FAILURE

BASELINE_TESTS=1380 (expected, per PROJECT_STATE.json/V4-R14 closure)
FINAL_TESTS=1402 (1401 PASS, 1 pre-existing FAIL; 1380 baseline + 22 new V4.1-R0 tooling tests)

PRODUCTION_FILES_ANALYZED=143
TEST_FILES_ANALYZED=41 (existing) + 1 (new, this round) = 42

KNOWN_DEBT_ITEMS=9 (TD-001..TD-005, DEBT-001..DEBT-003, plus 1 newly discovered: REG-002-CANDIDATE)

NEW_MAINTAINABILITY_FINDINGS=see "Top Findings" below

HIGH_RISK_CANDIDATES=16 files (risk_summary.files_by_risk_category.HIGH)
VERY_HIGH_RISK_CANDIDATES=6 files (risk_summary.very_high_risk_files)

DUPLICATION_CANDIDATES=4 (DUP-001..DUP-004)
SAFE_CONSOLIDATION_CANDIDATES=1 (DUP-001 / DEBT-001, the shared contract JSON renderer)

TYPE_SAFETY_FINDINGS=15 lowest-annotation-coverage files recorded (type_safety_candidates)
DOCUMENTATION_FINDINGS=15 lowest-docstring-coverage files recorded (documentation_candidates)
NAMING_FINDINGS=4 curated rename candidates (naming_candidates)
EXCEPTION_BOUNDARY_FINDINGS=8 files with a broad `except Exception`/bare `except` (exception_candidates)
SIDE_EFFECT_FINDINGS=39 files touch the filesystem; 11 files touch network/provider surfaces
DEPENDENCY_FINDINGS=1 reported "cycle", diagnosed as a package-facade self-loop, not a true circular import; knowledge-domain projection/plugin_projection non-import direction re-verified PASS

CHARACTERIZATION_REQUIRED=5 modules (characterization_needs)

PROPOSED_ROUNDS=10 (V4.1-R1..V4.1-R10)
ROADMAP_CHANGED_FROM_INITIAL_PROPOSAL=true
ROADMAP_CHANGE_JUSTIFICATION=see "Roadmap Changes" below

MAINTAINABILITY_INVENTORY=output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json
MAINTAINABILITY_INVENTORY_SHA256=b3308ba13e5fbc8cf9f9d381f3cd9d83a53f9b2ad3fad94e9b361c64ae2f398f

REFACTOR_PLAN=output/v4_1_r0/V4_1_REFACTOR_PLAN.json
REFACTOR_PLAN_SHA256=205b933293291c15394f667ffef6ee450d5aef43b0453cdda94865c6036b3954

MAINTAINABILITY_INVENTORY_DETERMINISM=PASS
REFACTOR_PLAN_DETERMINISM=PASS

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW

DECISION=V4_1_R0_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_1_R0
```

---

## Required Reading Performed

Read, in full and in order, before any analysis: `CLAUDE.md`, `AGENTS.md`, `PROJECT_STATE.json`,
`docs/PROJECT_RECOVERY.md`, `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`,
`docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md`, `output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json`
(the V3 technical-debt artifact — TD-001..TD-005 verbatim source),
`output/v4_bootstrap/V4_TECHNICAL_DEBT_CLASSIFICATION.json`,
`output/v4_r14/V4_FINAL_BASELINE.json` (production/test module counts, maintainability_baseline
section, known_maintainability_debt list), `prompts/V4_1/V4_1_R0_MAINTAINABILITY_INVENTORY_AND_REFACTOR_PLAN.md`
(the full authoritative spec, read in full). `legacy_documenter/quality/maintainability_audit.py`
and `legacy_documenter/knowledge/closure/maintainability.py` (the two existing V3/V4 precedents
for this kind of AST-based diagnostic, read to avoid reinventing an incompatible shape and to
confirm the 143-production-file / 74-knowledge-file counts independently). The four V4 manuals
under `docs/V4/` were consulted for contract boundaries referenced throughout the inventory
(canonical/projection/plugin_projection semantics, Technical-Lead-only approval, provenance
separation) rather than re-read line-by-line, since V4.1-R0 does not modify any of those contracts.

## Entry Gate

`PROJECT_STATE.json` matched the expected checkpoint exactly: `latest_completed_round=V4-R14`,
`latest_approved_round=V4-R14`, `round_status=V4_FORMALLY_CLOSED`, `next=POST_V4_MAINTAINABILITY_REFACTOR`,
`tests=1380`, `readiness=READY`, `provider_calls=0`, `real_llm_calls=0`. `git status` showed only
`prompts/V4_1/` untracked, as expected.

`python -m unittest discover -s tests` reported **1379 PASS / 1 FAIL out of 1380** — not the clean
1380 PASS the entry gate calls for. The single failure,
`DeterminismTests.test_baseline_matches_on_disk_artifact` in
`tests/test_v4_r14_manuals_and_final_baseline.py`, rebuilds `V4_FINAL_BASELINE.json` live from the
*current* `PROJECT_STATE.json` (`latest_approved_round=V4-R14`, now that R14 itself has been
approved) and compares it byte-for-byte against the frozen on-disk artifact, which was generated
and hashed **before** R14's own approval (`latest_approved_round=V4-R13` at generation time). This
is the identical defect shape to `REG-001` found and fixed in R13 (a generated snapshot compared
against a moving-target live value that is expected to advance once the round that produced the
snapshot is itself approved) — except this time nobody could fix it inside R14, because R14 was
the round being closed. This is recorded as **`REG-002-CANDIDATE`** in `known_debt` rather than
fixed, because V4.1-R0 is analysis-only: `TEST_SEMANTIC_MODIFICATION_ALLOWED=false` and
`PRODUCTION_CODE_MODIFICATION_ALLOWED=false` for this round. Per the spec's own escalation rule
("If repository state differs materially: STOP and report"), this is reported prominently here and
in the inventory rather than silently worked around; it does not block the analysis/planning
objective of R0, so R0 proceeded rather than halting, and recommends a test-only fix as the very
first item of `V4.1-R1` (see the roadmap).

`python -m legacy_documenter.knowledge.readiness` reported `READINESS=READY`,
`AI_KNOWLEDGE_ALLOWED=true`, `AI_KNOWLEDGE_GENERATED=false`, `PROVIDER_CALLS=0`,
`REAL_LLM_CALLS=0` — unaffected by the test-suite finding above.

## Tooling Placement

Analysis/report-generation code for this round lives under a new top-level `tools/` directory
(`tools/v4_1_r0/inventory.py`, `report.py`, `generate.py`), **not** under
`legacy_documenter/knowledge/` or any other production package. Rationale: `legacy_documenter/`
is production code subject to `PRODUCTION_CODE_MODIFICATION_ALLOWED=false` and to the "one
knowledge-domain capability per package" convention every V4 round package follows; a
maintainability-inventory generator is planning tooling for this round, not a new knowledge-domain
capability, and placing it inside `legacy_documenter/knowledge/` would blur that boundary and
imply it is part of the shipped product surface. `tools/` is imported by nothing under
`legacy_documenter/` or `main.py` — confirmed by grep — so this addition changes no import graph,
no runtime behavior, and no production module. It is new tooling, not a modification of existing
production behavior: `PRODUCTION_CODE_CHANGED=false` and `PRODUCTION_BEHAVIOR_CHANGED=false` both
hold because no file under `legacy_documenter/` was edited (confirmed by `git status --porcelain`
showing only new, untracked paths: `tools/`, `output/v4_1_r0/`,
`tests/test_v4_1_r0_maintainability_inventory.py`, `prompts/V4_1/`, and this document plus
`PROJECT_STATE.json`).

The tooling is intentionally standard-library only (`ast`, `pathlib`, `json`, `hashlib`) and
read-only over the repository tree; it imports no `legacy_documenter` module and calls no
LLM/provider.

## Top Findings

1. **DEBT-001/DUP-001 confirmed with hard evidence.** All 11 `render_*_contract_json` functions
   across every `legacy_documenter/knowledge/*/contract_report.py` module have the byte-identical
   one-line body `json.dumps(build_X(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))`.
   This is the clearest `SAFE_TO_CONSOLIDATE` candidate in the repository — a shared helper changes
   zero output bytes.
2. **DEBT-003 confirmed with hard evidence.** Exactly three service methods
   (`classify_batch`, `create_proposal_batch`, `create_relation_batch`) use a generic `requests`
   parameter name; renaming the parameter (not the type) is a low-risk, contract-invisible change.
3. **A newly discovered pre-existing test defect (REG-002-CANDIDATE)**, same shape as R13's
   REG-001: `V4_FINAL_BASELINE.json`'s determinism test compares a frozen historical snapshot
   against the live, advancing `PROJECT_STATE.json.latest_approved_round`. Recommended as the very
   first V4.1-R1 action (test-only fix).
4. **Two oversized "God classes" by direct reading, not just line count**:
   `DatabaseExtractor` (27 methods, 395 lines, `legacy_documenter/extractors/database_extractor.py`)
   and `FunctionalFlowResolver` (24 methods, 316 lines, `legacy_documenter/analysis/flow_resolver.py`)
   mix low-level text scanning with higher-level interpretation/report-formatting decisions. Both
   score only HIGH (not VERY_HIGH) on the mechanical per-file heuristic, which is a genuine
   limitation of file-level metrics — cohesion problems inside one very large class need direct
   reading, not just line/keyword counts, to surface.
5. **The mechanical VERY_HIGH-risk set is dominated by historical V1 orchestration**
   (`documentation/generator.py`, `hierarchical.py`, `resume.py`, `systematic.py`) plus
   `analysis/deep_source.py` (7 distinct responsibility signals in only 163 lines) and
   `knowledge/readiness.py` (DEBT-002). None of these have a dedicated characterization test module
   targeting their internal seams by name.
6. **The one reported "circular import" is a false alarm** — a package-facade self-loop
   (`legacy_documenter/llm/__init__.py` does `from .core import *`, and `providers/copilot.py`
   imports from the `legacy_documenter.llm` facade instead of `.core` directly). No true
   import-time cycle exists; recorded as a naming/import-clarity finding, not a defect.
7. **The R13-established knowledge-domain dependency direction still holds.**
   `plugin_projection.service` imports only `canonical`/`domain`; `projection.service` imports only
   `canonical`/`domain`/its own `projection.models`; neither imports the other — reverified by an
   independent AST-based edge scan in this round, not assumed from memory.
8. **DUP-002 (per-round contract/example builder bodies) is correctly `SIMILAR_BUT_SEMANTICALLY_DISTINCT`**,
   confirming TD-003's own original caution: R7's relation contract and R10's canonical contract
   share a textual shape but encode different field semantics and must not be merged by pattern
   similarity.
9. **Type-hint and docstring gaps concentrate in the historical `documentation/`, `analysis/`, and
   `extractors/` packages** (see `type_safety_candidates`/`documentation_candidates` in the
   inventory), consistent with TD-005's original scope and with V4-R14's own diagnostic baseline.
10. **39 of 143 files touch the filesystem and 11 touch network/provider surfaces**, but side
    effects remain concentrated at recognizable boundaries (extractors/scanner reading the
    read-only legacy repository; `documentation`/`exporters` writing generated output;
    `projection/disk_io.py` and `readiness.py` as the only two knowledge-package writers; all
    provider access confined to `legacy_documenter/llm/`) — no stray filesystem/network call was
    found inside a knowledge-domain business-logic module.

## Roadmap Changes

The initial 10-round proposal from the spec is **kept at 10 rounds but re-scoped**, since the
evidence gathered in this round changes what several rounds should actually do:

- **R1** ("Shared Reporting / Serialization Cleanup") is expanded to *also* fix
  `REG-002-CANDIDATE` first (test-only), since fixing a known-stale test before doing any other
  V4.1 work keeps every later round's entry gate clean. The serialization cleanup itself
  (DUP-001/DEBT-001) is unchanged from the proposal.
- **R3** ("Service Responsibility Separation" in the original proposal) is **replaced** with a
  narrower "Naming Pass Part 1 (Low-Risk Renames)" round. Evidence did not support a
  repository-wide service-responsibility-separation round this early: the only concrete, verified,
  low-risk renames available at this point are DEBT-003 and the `maintainability_audit.audit`
  alias; the genuinely risky responsibility separations (readiness.py, database_extractor.py,
  flow_resolver.py) each need their own characterization work first, which the original R3 slot
  would have collided with R4/R5's own scope.
- **R5** ("Large Orchestrators & Complex Flows") is **split into two rounds**: a
  characterization-only R5 (add tests, change nothing) and a design-reviewed extraction-only R6
  ("Extraction Behind Characterization"), replacing the original single R5 slot. Evidence
  (`characterization_needs` classifying `database_extractor.py`/`flow_resolver.py` as
  `TOO_RISKY_WITHOUT_DESIGN_REVIEW`) does not support extracting from these modules in the same
  round that first characterizes them — the spec itself asks for exactly this kind of split
  ("add a characterization round").
- **R6** ("Duplication and Cross-Round Helper Consolidation" in the original proposal) is
  effectively **already absorbed into R1** (the only `SAFE_TO_CONSOLIDATE` duplication found,
  DUP-001, is small enough to fold into the serialization-cleanup round) — the renumbered R6 in
  this plan is the extraction round described above, not a second consolidation pass, because
  evidence did not surface a second wave of safe consolidations distinct from DUP-001.
- **R7** ("Exception Boundaries & Adapter Cleanup") is **narrowed** to explicitly exclude the
  provider boundary (`legacy_documenter/llm/providers/*`, `copilot_pilot.py`): TD-002's own
  original plan says retain these until provider-specific exception taxonomies are
  contract-tested, and evidence in this round reconfirmed they are the correct place for a broad
  `except Exception` (external SDK/HTTP/subprocess boundary). Only the `HISTORICAL_COMPATIBILITY`/
  `REFACTOR_CANDIDATE` handlers in `documentation/*.py` are in scope.
- **R8** ("Naming, Documentation and C#-Friendly Readability Pass") is **narrowed** to "Part 2":
  it now only covers the naming candidates that needed characterization first (the `context/`
  package) or a rename wrapper (`copilot_pilot.py`), since Part 1's low-risk renames moved to the
  new R3.
- **R9/R10** (Comprehensive Regression & Behavioral Equivalence; Maintainability Final Baseline &
  Closure) are **kept as proposed**, unchanged — evidence did not surface a reason to alter the
  closing verification/closure shape that worked well in V4-R13/R14.

Net effect: still 10 rounds, same total scope, but re-ordered so that (a) the newly discovered test
defect is fixed before anything else, (b) no round both characterizes and extracts the same
high-risk module, and (c) low-risk renames are pulled forward ahead of the higher-risk
responsibility-separation work instead of being bundled with it.

## Duplication Analysis Summary

| id | pattern | classification | tracked_as |
|---|---|---|---|
| DUP-001 | `render_*_contract_json` one-line JSON renderer (11 files) | SAFE_TO_CONSOLIDATE | DEBT-001 |
| DUP-002 | `build_*_contract()` plain-dict builders | SIMILAR_BUT_SEMANTICALLY_DISTINCT | TD-003 |
| DUP-003 | generic `requests` batch-parameter name (3 files) | NEEDS_CHARACTERIZATION | DEBT-003 |
| DUP-004 | per-round `models.py`/`service.py`/`enums.py` package layout | DO_NOT_CONSOLIDATE | — |

Full detail, including the exact evidence for each classification, is in
`output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json` → `duplication_candidates`.

## Known Debt — Resolution Table

| id | source | current_relevance | recommended_round |
|---|---|---|---|
| TD-001 | `output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json` | Still accurate | V4.1-R8 |
| TD-002 | `output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json` | Still accurate; boundary re-confirmed at exactly 3 provider files | V4.1-R7 (deliberately not addressed) |
| TD-003 | `output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json` | Still accurate; DUP-002 confirms distinctness | V4.1-R6 (partial; only DUP-001 tail consolidated) |
| TD-004 | `output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json` | Still accurate; VERY_HIGH-risk orchestrators unchanged | V4.1-R5 (characterization), V4.1-R6 (extraction) |
| TD-005 | `output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json` | Still accurate; lowest type-hint coverage remains in documentation/analysis/extractors | V4.1-R2 |
| DEBT-001 | `docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md` | Confirmed with hard evidence | V4.1-R1 |
| DEBT-002 | `docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md` | Still accurate; readiness.py is 292 lines, VERY_HIGH risk | V4.1-R4 |
| DEBT-003 | `docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md` | Confirmed with hard evidence | V4.1-R8 |
| REG-002-CANDIDATE | This round's entry gate | Newly discovered, same shape as REG-001 | V4.1-R1 (first action) |

Full `original_description` text (verbatim from each source artifact), `affected_files`, `risk`,
and `recommended_action` for every item is in
`output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json` → `known_debt`.

## Characterization Required

`TOO_RISKY_WITHOUT_DESIGN_REVIEW`: `legacy_documenter/extractors/database_extractor.py`,
`legacy_documenter/analysis/flow_resolver.py`.
`ADDITIONAL_CHARACTERIZATION_REQUIRED`: `legacy_documenter/knowledge/readiness.py`,
`legacy_documenter/documentation/resume.py`, `legacy_documenter/analysis/deep_source.py`.
`EXISTING_TESTS_SUFFICIENT`: the DUP-001 shared-renderer extraction (existing per-round
contract/example SHA-256 hash tests already pin the exact serialized bytes).

## Public Compatibility

Five compatibility decisions are recorded (`public_compatibility` in the inventory), verified by
repository-wide grep rather than assumed: `legacy_documenter.main.main`/`analyze_repository`
(`DO_NOT_MOVE`, imported by `main.py` and `tests/test_v1*.py`); `readiness.run`
(`COMPATIBILITY_WRAPPER`, documented CLI entry point); the 11 `contract_report.py`
render/build functions (`REEXPORT`, referenced by each package's own hash tests);
`maintainability_audit.audit`/`write_audit` (`COMPATIBILITY_WRAPPER`, no cross-package importer
found); the `legacy_documenter.llm` facade (`NO_WRAPPER`, already public, only an internal-only
import-clarity change is proposed).

## Determinism Verification

`tools/v4_1_r0/generate.py` builds each artifact payload twice in the same process and compares
the serialized text before writing; both comparisons passed
(`MAINTAINABILITY_INVENTORY_DETERMINISM=PASS`, `REFACTOR_PLAN_DETERMINISM=PASS`). Independently,
the generator was invoked twice as **separate process runs** and the resulting on-disk SHA-256
values were identical across both runs (`b3308ba1...398f` / `205b9332...b3954`), which is a
stronger determinism proof than an in-process comparison alone. (An initial run surfaced a
Windows-specific `Path.write_text` newline-translation issue — `\n` was rewritten to `\r\n` on
disk, changing the file's bytes away from what had just been hashed in memory — fixed by writing
with `newline=""`; this was a bug in the new R0 tooling itself, not in any production code, and is
noted here for transparency.)

## Files Added

```text
tools/__init__.py                                                    (new)
tools/v4_1_r0/__init__.py                                            (new)
tools/v4_1_r0/inventory.py                                           (new)
tools/v4_1_r0/report.py                                              (new)
tools/v4_1_r0/generate.py                                            (new)
tests/test_v4_1_r0_maintainability_inventory.py                      (new, 22 tests)
output/v4_1_r0/V4_1_MAINTAINABILITY_INVENTORY.json                   (new)
output/v4_1_r0/V4_1_REFACTOR_PLAN.json                               (new)
docs/V4_1/V4_1_R0_MAINTAINABILITY_INVENTORY_AND_REFACTOR_PLAN_RESULT.md (new, this file)
PROJECT_STATE.json                                                   (updated, pending review)
```

No file under `legacy_documenter/` was created, modified, or deleted. No existing test was
modified, weakened, or removed.

## Decision

`V4.1-R0 — Maintainability Inventory and Refactor Plan` is complete. The entry gate passed with
one newly discovered, pre-existing, LOW-risk test defect (`REG-002-CANDIDATE`) recorded rather than
fixed, per this round's analysis-only constraints. 143 production files were analyzed via
deterministic AST tooling placed under a new top-level `tools/` directory, outside every
production package. Both required artifacts were generated twice with byte-identical results
(`MAINTAINABILITY_INVENTORY_DETERMINISM=PASS`, `REFACTOR_PLAN_DETERMINISM=PASS`). The proposed
10-round V4.1 roadmap was evaluated against this round's actual evidence and re-scoped (same round
count, changed responsibilities per round — see "Roadmap Changes") rather than accepted or
rewritten arbitrarily. `PRODUCTION_CODE_CHANGED=false` and `PRODUCTION_BEHAVIOR_CHANGED=false` both
hold. `PROJECT_STATE.json` has been updated to `V4_1_R0_READY_FOR_HUMAN_REVIEW` (not approved);
`latest_approved_round` remains `V4-R14` and no V4 closure field was changed.

`NEXT=HUMAN_REVIEW_V4_1_R0`

## Closure — Human Approval Recorded

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

REG_002_CANDIDATE=ACCEPTED
REG_002_STATUS=OPEN_FOR_R1
REG_002_R1_PRIORITY=FIRST_ACTION

ROADMAP_DECISION=APPROVED

R0_1_REQUIRED=false

ROUND_STATUS=APPROVED

DECISION=V4_1_R0_FORMALLY_APPROVED

NEXT=V4.1-R1
```
