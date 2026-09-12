# LegacyMapper — Repository Continuity Contract

## Purpose

This document defines exactly what MUST remain versioned in Git so that a fresh development agent — with no conversation history, no prior Claude/Codex session, and no access to any previous machine — can clone this repository and continue LegacyMapper development.

It is produced by `V4_R1_1_REPOSITORY_VERSIONING_AND_RECOVERY`. It does not replace `AGENTS.md`, `CLAUDE.md`, `docs/V4/V4_AI_HANDOVER.md`, or any approved contract; it only states which files carry that knowledge and must therefore be tracked.

## Core Principle

```text
VERSIONED REPOSITORY
=
SOURCE CODE
+ TESTS
+ CONTRACTS
+ APPROVED DECISIONS
+ ACTIVE ROADMAP
+ PROMPTS
+ HANDOVERS
+ MANUALS
+ SMALL BASELINES
+ RECOVERY INSTRUCTIONS
+ REQUIRED CONFIGURATION TEMPLATES
```

It must NOT automatically contain generated heavy data, regenerable intermediate outputs, failed-attempt artifacts, temporary data, caches, logs, or local machine state. The full disposition of every current file/directory is recorded in `output/v4_r1_1/V4_REPOSITORY_INVENTORY.json`.

## Production

* `legacy_documenter/` (all Python source, excluding `__pycache__/`)
* `main.py`
* No third-party dependency file exists or is required — LegacyMapper V1–V4 use only the Python standard library. If a future round introduces a dependency, a `requirements.txt` (or equivalent) becomes part of this contract at that time.

## Tests

* `tests/` (all test modules and `tests/fixtures/`, excluding `__pycache__/`)
* Baseline: 676 tests must pass (`python -m unittest discover -s tests`).

## Agent-Independent Governance

* `AGENTS.md`
* `CLAUDE.md`
* `.gitignore`
* `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`
* `PROJECT_STATE.json`
* `docs/PROJECT_RECOVERY.md`
* `docs/GENERATED_ARTIFACT_POLICY.md`
* this file

## V4

* `docs/V4/` (contract foundation, roadmap, handover, all round results, this continuity contract)
* `prompts/V4/` (every prompt that has driven a round, including this one)

## V3 Closure

Minimum authoritative V3 closure set, proving and explaining V3 is formally closed, ready, and did not generate AI knowledge:

* `output/v3_final/V3_FINAL_BASELINE.json` — canonical baseline.
* `codex/v3/V3_CIERRE_FINAL.md` — formal closure record.
* `docs/V3/MANUAL_TECNICO_LEGACYMAPPER_V3.md`, `docs/V3/MANUAL_USUARIO_LEGACYMAPPER_V3.md` — final manuals.
* `output/LEVANTAMIENTO_FUNCIONAL.md`, `output/LEVANTAMIENTO_TECNICO.md` — APPROVED documentation referenced by hash in the baseline.
* `output/v3_r9/*` — the four `KNOWLEDGE_*`/`READINESS_TRACEABILITY.json` files listed by hash in the baseline's `canonical_artifacts`.
* `output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json` — referenced by hash in the baseline's `technical_debt`.
* `output/v3_r10/`, `output/v3_r10_1/`, `output/v3_r7_2/`, `output/v3_r8_2/`, `output/v3_r8_3/` — small (well under 1 MiB combined) evidence artifacts backing the closure narrative in `codex/v3/V3_CIERRE_FINAL.md`.

These are retained in full; none is a full/reproducibility legacy-repository scan dump.

## V1/V2 Historical Continuity

* `codex/v1/`, `codex/v2/` — kept in full. All files are small Markdown instructions/results/validations; none is generated heavy data.
* `result_codex/V1_ANALYSIS_REPORT.md`.

These directories are historical records, not authoritative for current development, but required to answer "what did V1/V2 accomplish."

Historical execution noise that is NOT retained: the full/reproducibility legacy-repository scan output directories (`output/v1_r1_full/`, `output/v2_r4_full/`, `output/v2_r4_1_full/`, `output/v2_r4_1_repro_a/`, `output/v2_r4_1_repro_b/`, `output/v2_r5_full/`, `output/v2_r5_1_full/`, `output/v2_r5_1_repro/`) and the V3-R8.1 raw deep-analysis dump (`output/v3_r8_1/`). Each is deterministically regenerable by rerunning the tool against the legacy source; see `docs/PROJECT_RECOVERY.md`.

## V4 Round Results

* `output/v4_bootstrap/` (V4-00 reuse inventory, gap analysis, technical debt classification)
* `output/v4_r1/` (V4-R1 domain model contract)
* `output/v4_r1_1/` (this round's inventory, large-artifact analysis, GitHub suitability report)

## Historical `codex/` Directories — Explicit Statement

`codex/v1`, `codex/v2`, `codex/v3` are NOT renamed, reorganized, or pruned by this round. Every file inside them is small Markdown and is retained. No heavy generated data exists inside them.

## Not Retained (Excluded From Git, Not Deleted From Disk)

See `docs/GENERATED_ARTIFACT_POLICY.md` for the full category definitions and `.gitignore` for the exact paths. In summary: Python caches, the empty `context/` runtime directory's contents, the nine full/reproducibility legacy-scan dumps under `output/`, and small leftover smoke-test run outputs (`output/context/`, `output/documentation/`, `output/index/`, `output/v1_r1_internal/`, `output/v2_r4_1_internal/`) that are not referenced by any canonical V3/V4 result.

Excluding a path from Git never means deleting it from the local machine. See "Do Not Delete Valuable Data" in the active prompt and the `OPTIONAL_LOCAL_CLEANUP` section of `docs/V4/V4_R1_1_REPOSITORY_VERSIONING_RESULT.md`.
