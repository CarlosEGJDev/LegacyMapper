# LegacyMapper — User Manual (V4.2)

Status: V4.2 is formally closed (`PROJECT_STATE.json`: `current_version_status = V4_2_FORMALLY_CLOSED`).
This manual describes exactly what the current source code (`legacy_documenter/`, `main.py`) does — not
what a future version is designed to do. Where V4.2 stops short of a capability, that boundary is stated
explicitly rather than implied.

---

## 4.1 Purpose

LegacyMapper analyzes a legacy .NET Framework / VB.NET / ASP.NET Web Forms / Oracle repository and produces
deterministic technical documentation about it, with an optional, explicit AI interpretation pass over that
same evidence.

The guiding principle, stated in `AGENTS.md` and enforced throughout the codebase, is:

> **Python discovers and resolves facts. AI interprets later.**

Concretely:

- All facts about the analyzed repository — its projects, symbols, calls, WebForms, database access,
  functional flows, dependencies — are discovered by deterministic Python code (parsers, extractors,
  resolvers) that never calls an AI/LLM provider.
- An AI provider, when explicitly enabled, may only *restate or explain* evidence Python already
  discovered in the current run. It is never allowed to invent a relationship, fact, or business meaning,
  and its output is never treated as an approved fact — see §4.7 and §4.12.

V4.2 remains scoped to the ecosystem it has always targeted: **.NET Framework / VB.NET / ASP.NET Web Forms /
Oracle**, exactly as V4.1 was (see `docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md`,
`NOT_IMPLEMENTED_BOUNDARIES`). Language-, framework-, database-, project-layout-, and AI-provider/model-
agnosticism are explicitly **V5 work** (`PROJECT_STATE.json: next = "V5_DESIGN_PENDING"`); nothing in the
current source implements them. Do not assume LegacyMapper can be pointed at, e.g., a Java or Node.js
repository, or at a different database engine, and receive equivalent treatment.

## 4.2 Installation / Prerequisites

LegacyMapper is a plain Python package with no declared third-party runtime dependency (no
`requirements.txt`, `pyproject.toml`, or `setup.py` exists in this repository) and no packaging/deployment
tooling. The only prerequisites evidenced by the repository are:

- A Python interpreter compatible with the syntax used throughout `legacy_documenter/` (modern type-hint
  syntax such as `str | None`, `from __future__ import annotations`; the standard library only —
  `argparse`, `dataclasses`, `pathlib`, `hashlib`, `json`, `ast`, `asyncio`, `unittest`). The development
  environment used for this repository runs CPython 3.14 (see `__pycache__/*.cpython-314.pyc`); any
  reasonably current CPython 3.x that supports this syntax is expected to work, but no specific minimum
  version is declared anywhere in the repository.
- No database, web server, container runtime, or external service is required to run `analyze` or `full`
  without `--allow-ai-interpretation`.
- `--allow-ai-interpretation` additionally requires a resolvable AI provider (see §4.7) and, for the
  `COPILOT` provider, whatever local GitHub Copilot client the provider integration expects
  (`legacy_documenter/llm/providers/copilot.py`); no credentials or endpoints are hardcoded or documented
  here because none are evidenced as required for normal operation.

Do not assume a `pip install`/virtualenv step, a Docker image, or an environment-variable file is needed —
none is present in this repository. If your environment does not already have a suitable Python
interpreter, install one through your platform's normal means; LegacyMapper prescribes nothing beyond that.

## 4.3 CLI

LegacyMapper is invoked as `python main.py <command> ...`. The parser (`legacy_documenter/cli/parser.py`)
defines three explicit subcommands plus one backward-compatible legacy form:

| Invocation | Meaning |
|---|---|
| `python main.py analyze <repository> [options]` | Deterministic analysis only (pre-V4.2 behavior). |
| `python main.py full <repository> [options]` | Deterministic analysis + technical documentation + run summary. |
| `python main.py readiness` | Checks LegacyMapper's own knowledge-readiness gate; does not analyze a repository. |
| `python main.py <repository> [options]` | Legacy shorthand, silently rewritten to `analyze <repository> [options]`. |
| `python main.py -h` / `--help` | Shows the top-level help (all four forms), left untouched by the legacy rewrite. |

`normalize_argv` (`legacy_documenter/cli/parser.py`) performs the legacy rewrite: any argument list whose
first token is **not** `analyze`, `full`, `readiness`, `-h`, or `--help` is treated as the pre-V4.2 bare
form and has `analyze` prepended before argparse ever sees it. This is a hard backward-compatibility
guarantee, not a second parsing path — both spellings reach the exact same `analyze` subparser.

Shared options for `analyze` and `full`:

| Option | Default | Meaning |
|---|---|---|
| `repository` (positional) | — | Repository path to analyze. |
| `--output` | `output` | Output directory. |
| `--exclude` | (none, repeatable) | Additional folder name(s) to exclude from scanning. |
| `--verbose` | off | Enables info-level logging. |
| `--flow-max-depth` | `12` | Maximum confirmed method-call depth for functional-flow resolution. |

`full` adds one more option:

| Option | Default | Meaning |
|---|---|---|
| `--allow-ai-interpretation` | off | Opts in to one AI interpretation pass over this run's own evidence (see §4.7). |

`readiness` takes no arguments — it validates LegacyMapper's own prerequisites, not a target repository
(see §4.6).

## 4.4 `analyze`

`analyze` (`legacy_documenter.main.analyze_repository`, routed via
`legacy_documenter/cli/router.py::_route_analyze`) is the pre-V4.2 deterministic pipeline, preserved
byte-for-byte for existing scripts. It:

- scans the repository (`legacy_documenter/scanner/`),
- extracts solutions/projects/symbols/WebForms/database access (`legacy_documenter/extractors/`),
- resolves calls, web entry points, database access, functional flows, and dependencies
  (`legacy_documenter/analysis/`),
- writes JSON/Markdown index artifacts (`legacy_documenter/exporters/json_exporter.py`,
  `markdown_exporter.py`) and context artifacts (`legacy_documenter/context/`) under `--output`.

`analyze` does **not** render the ten fixed technical-documentation files, does **not** write a
`RUN_SUMMARY`, and never contacts an AI provider — there is no `--allow-ai-interpretation` option on
`analyze` at all. Its exit code is always `0` (`EXIT_SUCCESS`); an unexpected exception propagates and
terminates the process rather than being converted into a structured `PARTIAL`/`FAILED` result — `analyze`
does not use the stage/`RunResult` model at all (`RunResult(command="analyze", status=RunStatus.SUCCESS)` is
reported unconditionally on return). `analyze` never modifies the analyzed repository.

Use `analyze` when you specifically need the pre-V4.2 output shape and none of `full`'s additional
documentation/resilience/summary behavior.

## 4.5 `full`

`full` (`legacy_documenter/cli/full_pipeline.py::run_full_pipeline`, routed via
`legacy_documenter/cli/router.py::_route_full`) is the recommended default. It runs the same deterministic
stages as `analyze`, plus:

- **Resilient, stage-level orchestration.** Each stage — `SCAN, EXTRACTION, CALL_RESOLUTION,
  WEB_ENTRY_RESOLUTION, DATABASE_RESOLUTION, FLOW_RESOLUTION, DEPENDENCY_RESOLUTION, EXPORT, CONTEXT,
  DOCUMENTATION` — is wrapped so one stage's failure does not abort stages that do not depend on it. A
  stage whose required upstream stage failed is reported `SKIPPED_DUE_TO_UPSTREAM_FAILURE`, never silently
  omitted (`legacy_documenter/cli/stage_identity.py`).
- **Technical documentation** (`DOCUMENTATION` stage): renders ten fixed Markdown documents plus a
  `documentation/README.md` navigation page — see §4.8.
- **A run summary**: `RUN_SUMMARY.json` and `RUN_SUMMARY.md` under `--output`, always written, recording
  every stage's outcome plus the approval-boundary fields (`ai_invoked`, `canonical_knowledge_produced`,
  `technical_lead_approval`, `ai_requested`, `proposal_count`, `proposal_review_status`, `next_action`,
  `output_locations`).
- **Optional AI interpretation and proposal generation** — see §4.7.

Without `--allow-ai-interpretation`, `full` makes **zero** AI/provider calls — exactly like `analyze`.

Failure containment example: if `WEB_ENTRY_RESOLUTION` fails, `DATABASE_RESOLUTION` (which does not depend
on it) still runs; `FLOW_RESOLUTION` (which depends on both) is skipped and reported as such; `EXPORT` and
`DOCUMENTATION` still run over whatever the successful stages produced — a partial but honest output tree,
never a crash and never fabricated data for the missing piece
(`legacy_documenter/cli/full_pipeline.py::_assemble_indexes`: "A field whose producing stage failed/was
skipped is an empty container — an honest 'nothing produced', never invented data").

## 4.6 `readiness`

`python main.py readiness` does **not** analyze any user-supplied repository. It validates LegacyMapper's
own internal knowledge-readiness prerequisites — a fixed, self-referential gate defined in
`legacy_documenter/knowledge/readiness.py` (originally V3-R9) that checks LegacyMapper's own approved
V3-era functional/technical documentation (`output/LEVANTAMIENTO_FUNCIONAL.md`,
`output/LEVANTAMIENTO_TECNICO.md`), its own human-review record
(`codex/V3/V3_R8_4_REVISION_HUMANA_APROBADA.md`), and its own architecture evidence
(`output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`) for internal consistency, evidence closure, and the absence
of secret-shaped values. `READY` means all of `preconditions`, `claim_integrity`, `evidence_closure`,
`quantitative_integrity`, `architecture_integrity`, `knowledge_projection`, `knowledge_boundary`, and
`security` passed. This is a project-continuity self-check, not a per-run readiness signal about the
repository you point `analyze`/`full` at.

**Fresh-clone behavior**: `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` is a small (~1.8 KiB), deliberately
tracked exception to the otherwise-excluded `/output/v3_r8_1/` directory — a narrow `.gitignore` carve-out,
not a restored operational dump. It contains only the four aggregate `DETERMINISTIC_INDICATORS` structural
counts and the architecture conclusion, sourced from the already-tracked, human-approved
`codex/v3/V3_R8_1_DEEP_SOURCE_ANALYSIS_RESULTADO.md`; it carries no source code, no source file paths, no
credentials, and no personally identifiable data. On a fresh clone, `python main.py readiness` now succeeds:
`exit code 0`, `readiness: READY`, all eight checks `true`, `provider_calls: 0`, `real_llm_calls: 0`. Note
this file cannot be *regenerated* from the repository alone — its original values depended on a real legacy
scan; it is tracked precisely because that scan is not repeatable from tracked inputs. Residual hardening
debt (not implemented): `legacy_documenter/knowledge/readiness.py` still assumes this tracked file exists;
if it is manually deleted or corrupted, current behavior may still raise an uncontrolled exception rather
than a controlled `BLOCKED` result. See the Technical Manual §20 for detail.

## 4.7 AI interpretation

AI interpretation is **off by default** and only reachable from `full` via `--allow-ai-interpretation`.
`analyze` can never trigger it — the option does not exist on that subcommand.

What actually happens when enabled (`legacy_documenter/orchestration/ai_interpretation.py`):

- One `AI_INTERPRETATION` stage runs only if the `CONTEXT` stage already succeeded in *this* run — it reads
  exclusively from `<output>/ai_context/*.json` written moments earlier by the same run, never a historical
  snapshot or a different run's output.
- The provider is asked to restate/explain the attached evidence only, under a system instruction that
  forbids inventing relationships or business meaning and requires every finding to cite evidence
  reference ids that are actually present in the current run's own context package.
  (`legacy_documenter/orchestration/ai_interpretation.py::SYSTEM_INSTRUCTION`, `_validate_findings`).
- If `PROPOSAL_GENERATION` also succeeds, findings become `Proposal` records written to
  `output/proposals/AI_PROPOSALS.json` (authoritative) and
  `output/proposals/AI_PROPOSALS_PENDING_REVIEW.md` (human-readable), every one carrying
  `status = PENDING_TECHNICAL_LEAD_REVIEW` — **never** approved automatically.
- Provider resolution (`_resolve_provider`) reads `LEGACYMAPPER_LLM_PROVIDER` (default `COPILOT`),
  `LEGACYMAPPER_LLM_PROVIDER_ID`, and `LEGACYMAPPER_LLM_MODEL` from the environment and constructs a real
  provider through `ProviderRegistry`. **`ProviderRegistry.create` currently only recognizes `"FAKE"` and
  `"COPILOT"`** (`legacy_documenter/llm/core.py::ProviderRegistry.create`) — a `GeminiProvider` class exists
  (`legacy_documenter/llm/providers/gemini.py`) but is not registered/reachable through this path; see the
  Technical Manual §13 and the discrepancy note in the result document.
- Any real production invocation of `--allow-ai-interpretation` resolves and may call a real provider.
  **Do not** run `full ... --allow-ai-interpretation` for manual verification — use
  `python -m tools.manual_verify_full_pipeline <repository> --output <dir> --allow-ai-interpretation`
  (always injects `FakeLLMProvider`), or the automated test suite, which additionally fails loudly if any
  test path unexpectedly reaches real provider resolution (`AGENTS.md`, "Manual AI-Path Verification").

## 4.8 Output navigation

Under `--output` (only for `full`; `analyze` writes only `index/` and `context/`):

```
<output>/
  index/                     deterministic JSON indexes (both commands)
  context/                   ai_context/-adjacent context artifacts (both commands)
  ai_context/                current-run evidence package for AI_INTERPRETATION (full only)
  documentation/
    README.md                V4.2-R8 top-level navigation document
    PROJECT_OVERVIEW.md
    SOLUTION_STRUCTURE.md
    PROJECT_DEPENDENCIES.md
    WEBFORMS_MAP.md
    CONFIGURATION_SUMMARY.md
    ANALYSIS_WARNINGS.md
    WEB_ENTRY_POINTS.md
    FUNCTIONAL_FLOWS.md            navigation/summary document
    DATABASE_ACCESS.md             navigation/summary document
    UNRESOLVED_FINDINGS.md         navigation/summary document
    functional_flows/<safe-name>.md    detail partitions, one per semantic group
    database_access/<safe-name>.md     detail partitions
    unresolved_findings/<safe-name>.md detail partitions
  proposals/                 only if --allow-ai-interpretation was passed
    AI_PROPOSALS.json
    AI_PROPOSALS_PENDING_REVIEW.md
  RUN_SUMMARY.json            full only
  RUN_SUMMARY.md              full only
```

The ten fixed-filename documents are historical: six from `MarkdownExporter`
(`legacy_documenter/exporters/markdown_exporter.py` — `PROJECT_OVERVIEW.md`, `SOLUTION_STRUCTURE.md`,
`PROJECT_DEPENDENCIES.md`, `WEBFORMS_MAP.md`, `CONFIGURATION_SUMMARY.md`, `ANALYSIS_WARNINGS.md`) and four
from `TechnicalDocumentationRenderer`
(`legacy_documenter/exporters/technical_documentation_renderer.py` — `WEB_ENTRY_POINTS.md`,
`FUNCTIONAL_FLOWS.md`, `DATABASE_ACCESS.md`, `UNRESOLVED_FINDINGS.md`).

V4.2-R8 added a navigation/detail split for the three documents that grew unusably large at real-repository
scale during the V4.2-R7 real pilot (`FUNCTIONAL_FLOWS.md`, `DATABASE_ACCESS.md`, `UNRESOLVED_FINDINGS.md`):
the fixed-filename document is now a small summary/index, and the full detail is split by semantic group
(typically per project) into `documentation/<doc-stem-lowercase>/<safe-name>.md` files with deterministic,
filesystem-safe names (`legacy_documenter/exporters/_documentation_partitioning.py::sanitize_label`) —
never derived from AI content, a timestamp, or Python's randomized `hash()`. `documentation/README.md` is
the single entry point that links to every fixed document and lists whether it was partitioned.

`WEB_ENTRY_POINTS.md`, `PROJECT_DEPENDENCIES.md` remain single flat documents; scale-driven partitioning
for them was evaluated and deliberately left open
(`PROJECT_STATE.json: documentation_remaining_scale_debt`, `"OPEN_IF_FUTURE_SCALE_REQUIRES"` for both) —
see Technical Manual §20.

## 4.9 Exit codes

Authoritative contract (`legacy_documenter/cli/router.py`, reaffirmed at V4.2-R5.1 over an earlier,
incorrect draft in the V4.2-R5 prompt document):

| Code | Meaning | Applies to |
|---|---|---|
| `0` | `SUCCESS` | `analyze` (always), `full`, `readiness` |
| `1` | `PARTIAL` | `full`, `readiness` |
| `2` | `USAGE` | argparse's own usage error (unknown command, missing argument) — not assigned by application code, produced by `argparse` itself |
| `4` | `FAILED` | `full` |

`3` (an R1-era `NOT_IMPLEMENTED_FOR_R1` placeholder) is retired and deliberately never reused.

`full`'s status is computed non-subjectively
(`legacy_documenter/cli/full_pipeline.py::_compute_status`): `FAILED` unless both `EXTRACTION` and `EXPORT`
succeeded; otherwise `PARTIAL` if any per-file extraction error, any `FAILED` stage, or any
`SKIPPED_DUE_TO_UPSTREAM_FAILURE` stage exists; otherwise `SUCCESS`.

## 4.10 Rerun / recovery

Rerunning `full` (or `analyze`) into the same `--output` directory is safe:

- `index/`, `documentation/` (including its R8 partition subdirectories), `context/`, and `ai_context/` are
  unconditionally overwritten in full by the stage that owns them, every time that stage runs.
- A stale `proposals/` pair from an earlier run into the same directory is removed unconditionally *before*
  any stage of the new run executes (`legacy_documenter/cli/artifact_lifecycle.py::reset_stale_proposal_artifacts`)
  — this run's own `AI_INTERPRETATION`/`PROPOSAL_GENERATION` stages then rewrite it fresh only if they
  actually produce output, so a rerun without `--allow-ai-interpretation` never leaves a previous run's
  proposals looking current.
- A stale partition file left over from a previous run whose semantic groups have since changed is removed
  as part of the partitioned rendering (deterministic partitioning always reflects only the current run's
  groups).
- A user-created file placed inside a generated directory (e.g. a note dropped into `documentation/`) is
  preserved — only the fixed, generated filenames/partition files are touched.
- The analyzed source repository is never modified, renamed, or written into, by any command
  (`AGENTS.md`, "Legacy Source Repository").

## 4.11 Real-system output

Per `docs/GENERATED_ARTIFACT_POLICY.md`'s "Real-System Operational Output" section: results from running
LegacyMapper against a concrete, real legacy system (a pilot, an ad-hoc engagement analysis) are
operational output, not project source, and **must remain local and must never be committed**, regardless
of size. The convention for a new such run is `output/_local_<descriptive-name>/`, already covered by a
generic `.gitignore` rule (`/output/_local_*/`) with no `.gitignore` edit required. If a formally named
directory is used instead, the matching explicit `.gitignore` path rule must be added in the same change
that creates it (as was done for `output/v4_2_r7_ist_operacional/`, the V4.2-R7 real IST pilot). Whatever
from a real-system run matters for project history must be distilled into small tracked documentation,
tests, or synthetic fixtures (e.g. `tests/test_v4_2_r7_synthetic_full_fixture.py`) before the raw
operational output is discarded — never solved by globally ignoring `output/`, which also holds tracked
contracts, baselines, and manifests.

## 4.12 Approval boundary

**Implemented today:**

- Deterministic analysis, technical documentation, and (opt-in) AI interpretation producing proposals for
  human review, as described above.
- Proposals are always written as `PENDING_TECHNICAL_LEAD_REVIEW`; `RunResult.canonical_knowledge_produced`
  and `RunResult.technical_lead_approval` are `false` in every V4.2 run, without exception.
- A documented (not implemented) approval-surface design:
  `docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md`, `IMPLEMENTATION_STATUS=NOT_IMPLEMENTED`.

**Not implemented in V4.2** (`PROJECT_STATE.json`: `approval_surface_implementation = NOT_IMPLEMENTED`,
`plugin_runtime = NOT_IMPLEMENTED`):

- No `approve` / `reject` / `request-correction` CLI command exists.
- No `run_id`-bound approval mechanism exists.
- No automatic promotion of a proposal to canonical knowledge exists.
- The knowledge sub-packages that model canonical composition, approval, and Plugin-facing projection
  (`legacy_documenter/knowledge/canonical/`, `approval/`, `plugin_projection/`, `projection/`) exist as
  tested, reusable *domain/contract* code, but `full`/`analyze`/`readiness` never call into them — there is
  no orchestrated end-to-end "R11/R12" workflow reachable from the CLI after a proposal is generated.
- No Plugin runtime exists that consumes `LegacyMapperPluginKnowledge` payloads at runtime.

Every proposal LegacyMapper produces requires a human Technical Lead decision, made outside this tool,
before it can inform anything downstream.

## 4.13 Troubleshooting

| Symptom | Likely cause | Evidence |
|---|---|---|
| `python main.py readiness` raises `FileNotFoundError` for `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` (should not occur on a normal clone; this file is now tracked) | The file was manually deleted, or `/output/v3_r8_1/` was fully re-excluded locally. `readiness.py` still assumes the tracked file exists and does not yet degrade to a controlled `BLOCKED` result if it is missing — recorded as residual hardening debt, not implemented this round. | `legacy_documenter/knowledge/readiness.py::_execute`; see §4.6 and the Technical Manual §20. |
| `full --allow-ai-interpretation` unexpectedly reaches a real AI client during manual testing | `_resolve_provider()` always resolves a real provider (`COPILOT` by default) unless one is injected. | `legacy_documenter/orchestration/ai_interpretation.py::_resolve_provider`; `AGENTS.md`, "Manual AI-Path Verification". Use `tools/manual_verify_full_pipeline.py` instead. |
| `full` reports `PARTIAL` with a `SKIPPED_DUE_TO_UPSTREAM_FAILURE` stage | An upstream dependency stage failed; the skipped stage's `StageError.message` names it explicitly. | `legacy_documenter/cli/full_pipeline.py::_skipped`; inspect `RUN_SUMMARY.json`. |
| `full` reports `FAILED` | `EXTRACTION` or `EXPORT` did not succeed — no minimally useful analysis package exists. | `legacy_documenter/cli/full_pipeline.py::_compute_status`. |
| Exit code `2` with no `RunResult` printed | This is argparse's own usage error (bad/missing arguments), not an application-level outcome. | `legacy_documenter/cli/router.py` comment on `EXIT_*` constants. |
| `documentation/FUNCTIONAL_FLOWS.md` (etc.) looks short/empty compared to expectations | V4.2-R8 made it a navigation summary; the detail is under `documentation/functional_flows/<safe-name>.md`. | §4.8; `docs/V4_2/V4_2_R8_DOCUMENTATION_AT_SCALE_FINAL_BASELINE_AND_CLOSURE_PREPARATION_RESULT.md`. |
| `UNRESOLVED_FINDINGS.md` contains `InitializeComponent()` boilerplate noise | Known, preserved observation (F-06), not a bug — WebForms designer-generated code is not specially filtered. | `docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md`. |
| A `WebEntryResolver`-derived flow lacks `outgoing_calls` for a markup-bound handler | Known, preserved observation (F-07) — `WebEntryResolver` does not attach `outgoing_calls` to markup-bound entry points. | Same document; `tests/test_v4_2_r7_synthetic_full_fixture.py::FunctionalFlowTests`. |
