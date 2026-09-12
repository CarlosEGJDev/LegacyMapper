# LegacyMapper — Project Recovery

## Purpose

This document lets a developer or AI agent on a completely new machine, with no prior conversation or session history, clone this repository and become fully productive. The repository is authoritative; this document does not duplicate project knowledge, it points to where that knowledge lives.

## Prerequisites

* Python 3.x, standard library only. LegacyMapper has **zero third-party dependencies** — there is no `requirements.txt`/`pyproject.toml` because none is needed. `pip install` is not required to run tests or the tool.
* No external tools, databases, or services are required.
* Windows or any OS with Python; the project has been developed on Windows but contains no OS-specific runtime assumptions in its own source.

## Clone

```text
git clone https://github.com/CarlosEGJDev/LegacyMapper.git
cd LegacyMapper
```

## Local Configuration

No local configuration file is required to run the test suite or the readiness command. Nothing in this repository requires a `.env` file or credentials for normal development.

The one path that is machine-specific is the legacy source repository location (see below); it is passed as a CLI argument, never stored in a committed file.

Never place credentials, tokens, or connection strings in any committed file. `.gitignore` excludes `.env*` files as a safety net, but none currently exist or are expected.

## Legacy Source

The legacy source repository (`C:\Users\cgalianj\source\IST_40\operacional` on the current operator's machine) is:

* **optional** for ordinary V4 development — V4's `HUMAN_INFORMATION_ONLY` knowledge-ingestion mode does not require it, and the full 676-test suite runs entirely against fixtures and does not touch it;
* **required** only to regenerate the specific historical V1/V2/V3 full-repository scan outputs listed below, or to run a fresh full-repository scan of that particular legacy application.

If you do not have access to that legacy repository, you can still: run all tests, read every V1–V4 decision and result, and continue V4 development from `PROJECT_STATE.json` onward.

## Heavy Historical Artifacts (Excluded From Git)

The following directories are intentionally not versioned (see `.gitignore` and `docs/GENERATED_ARTIFACT_POLICY.md`) because they are large (~8.2 GiB combined), deterministic, and reproducible:

| Artifact | Required for ordinary development? | Required to regenerate older results? | Source | Command |
|---|---|---|---|---|
| `output/v1_r1_full/` | No | Yes, to reproduce the V1-R1 full run | legacy source repo | `python main.py "<legacy_repo>" --output "output/v1_r1_full" --verbose` |
| `output/v2_r4_full/`, `v2_r4_1_full/`, `v2_r4_1_repro_a/`, `v2_r4_1_repro_b/` | No | Yes, to reproduce the V2-R4/R4.1 full and reproducibility runs | legacy source repo | same pattern, substitute `--output` |
| `output/v2_r5_full/`, `v2_r5_1_full/`, `v2_r5_1_repro/` | No | Yes, to reproduce the V2-R5/R5.1 full and reproducibility runs | legacy source repo | same pattern |
| `output/v3_r8_1/` | No | Yes, to reproduce the V3-R8.1 deep-analysis raw dump | legacy source repo | same pattern; see `codex/v3/V3_R8_1_DEEP_SOURCE_ANALYSIS_ENGINE.md` for the exact round instructions |
| `output/context/`, `output/documentation/`, `output/index/`, `output/v1_r1_internal/`, `output/v2_r4_1_internal/` | No | No — leftover smoke-test runs, not referenced by any canonical result | any sample source | `python main.py "<any_source>" --output "<dir>"` |

None of these directories were deleted from disk by this round; they are excluded from Git only. If you are recovering onto a machine that never had them, a clean checkout simply will not include them, and the repository remains fully functional without them.

If the legacy source repository itself is unavailable, these specific historical outputs cannot be regenerated, but nothing about current (V4) development depends on that.

## Verification

After cloning, run, in order:

```text
python -m unittest discover -s tests
```

Expected: **676 tests, OK** (see `PROJECT_STATE.json` for the current authoritative count).

```text
python -m legacy_documenter.knowledge.readiness
```

Expected: `readiness=READY`, `ai_knowledge_allowed=true`, `ai_knowledge_generated=false`, `provider_calls=0`, `real_llm_calls=0`.

If either check fails on a clean clone, stop and report — do not proceed with new development until both pass, per `AGENTS.md` phase-control rules.

## Current State

Do not re-derive project knowledge here; follow these pointers:

* Current handover: `docs/V4/V4_AI_HANDOVER.md`
* Current roadmap: `docs/V4/V4_PROPOSED_ROADMAP.md`
* Canonical V3 baseline: `output/v3_final/V3_FINAL_BASELINE.json`
* Latest approved round result: see `PROJECT_STATE.json` → `latest_approved_round` and `latest_result_path`
* Machine-readable state index: `PROJECT_STATE.json`

## Next Step Discovery

A new development agent determines the next task by reading, in order:

1. `CLAUDE.md` — entry point, points to `AGENTS.md`, the handover, the baseline, and the active prompt.
2. `AGENTS.md` — operating rules, permission boundary, phase control.
3. `PROJECT_STATE.json` — machine-readable pointer to the latest completed/approved round and the declared `next` task.
4. `docs/V4/V4_AI_HANDOVER.md` — narrative continuity requirements.
5. `docs/V4/V4_PROPOSED_ROADMAP.md` — the full ordered round list (V4-R1 … V4-R14) and each round's scope.
6. The result document of the latest approved round under `docs/V4/` (e.g. `V4_R1_KNOWLEDGE_DOMAIN_MODEL_RESULT.md`) — its `NEXT=` line names the next round.
7. The corresponding prompt under `prompts/V4/` for that next round, if one already exists; otherwise the next round is scoped by a new prompt before implementation begins, per `AGENTS.md` phase-control (`Do not automatically start the next round`).

Do not begin implementing a round whose prompt does not yet exist under `prompts/V4/`, and do not implement V4-R2 or later as a side effect of this recovery document.
