# V4_2_R0_FULL_PIPELINE_ARCHITECTURE_AND_INVENTORY — Result

TASK=V4_2_R0_FULL_PIPELINE_ARCHITECTURE_AND_INVENTORY

MODE=ARCHITECTURE_AND_INVENTORY_ONLY

---

## STATUS

STATUS=V4_2_R0_ARCHITECTURE_AND_INVENTORY_COMPLETE

---

## BASELINE

V4_1_STATUS=FORMALLY_CLOSED (confirmed: `PROJECT_STATE.json` — `latest_completed_round=V4.1-R10`, `round_status=V4_1_FORMALLY_CLOSED`, `next=V5_DESIGN_PENDING`)

PLUGIN_RUNTIME=NOT_IMPLEMENTED

V5_IMPLEMENTED=false

No V4.1 historical artifact was read for modification purposes — only for reference. Nothing under `docs/V4/`, `docs/V4_1/`, `output/v4_1_r10/`, or `output/v3_final/` was modified.

---

## TESTS

Command executed: `python -m unittest discover -s tests`

```
Ran 1566 tests in 33.351s
OK
```

TESTS=1566_PASS_0_FAIL_0_SKIP

---

## READINESS

Command executed: `python -m legacy_documenter.knowledge.readiness`

```json
{
  "ai_knowledge_allowed": true,
  "ai_knowledge_generated": false,
  "readiness": "READY",
  "provider_calls": 0,
  "real_llm_calls": 0,
  "records": 47,
  "ineligible_records": 4,
  "status": "V3-R9_KNOWLEDGE_READINESS_GATE_COMPLETE"
}
```

READINESS=READY

---

## CURRENT_CLI

Verified directly from `legacy_documenter/main.py` argparse definition:

```
python main.py <repository> [--output OUTPUT] [--exclude FOLDER (repeatable)] [--verbose] [--flow-max-depth N]
```

Defaults: `--output="output"`, `--flow-max-depth=12`. No subcommands exist today. This is the **only** entry point; there is no `--full`, no `analyze`/`readiness` subcommand, and `main.py` never touches `legacy_documenter/knowledge/`.

---

## CURRENT_PIPELINE

`legacy_documenter/main.py::analyze_repository()` executes, **in order**, on every default run:

1. `RepositoryScanner(excludes).scan(root)` → `list[SourceFile]` (classification is embedded in the scan).
2. Extraction loop 1 (per file, `solution`/`vb_project`/`vb_source`/`aspx`/`ascx`/`master`/`web_config`) → `SolutionExtractor`, `VBProjExtractor`, `VBNetExtractor`, `WebFormsExtractor`, `WebConfigExtractor`. Each call wrapped in its own `try/except`; a failure is appended to an `errors` list and does **not** abort the run.
3. Extraction loop 2 (per `vb_source` file) → `CallExtractor`, `WebEventExtractor`, `DatabaseExtractor`, same per-file non-aborting pattern.
4. `apply_project_namespaces(...)`, `consolidate_partial_symbols(...)` — deterministic, in-memory.
5. `CallResolver`, `WebEntryResolver`, `DatabaseResolver`, `FunctionalFlowResolver(flow_max_depth)`, `DependencyResolver` — resolve calls, web entry points, database access, functional flows and cross-project dependencies. **None of steps 5–9 (resolvers) or 10–11 (exporters/context) are wrapped in try/except** — a failure here aborts the whole run uncaught, unlike the per-file-tolerant extraction stage.
6. `JSONExporter().export(output, indexes)`, `ContextBuilder().build_project_contexts(...)`, `SystemContextBuilder().build(...)`, `MarkdownExporter().export(...)`.

**Zero AI/LLM invocation occurs in the default CLI path.** `main.py` never imports `legacy_documenter.llm` or `legacy_documenter.documentation`, and never imports `legacy_documenter.knowledge`.

**Capabilities NOT reached by this CLI:** `analysis/deep_interpretation.py` (AI interpretation), `analysis/deep_source.py`, `analysis/targeted_exhaustion.py`, all of `legacy_documenter/documentation/` (18 modules — generation, synthesis, consistency, human review), `context/resolver.py` + `context/composer.py` (a second, LLM-prompt-oriented context-packaging layer on top of `ai_context/*.json`), and the entire `legacy_documenter/knowledge/` package (13 subpackages plus `readiness.py`).

**Components requiring explicit inputs the current CLI does not create:** `documentation/generator.py` hardcodes a read from `output/v2_r5_1_full/ai_context/*.json` (a historical snapshot path, not the path `SystemContextBuilder` writes for a fresh run) and instantiates `CopilotProvider` directly. `knowledge/readiness.py` reads `output/LEVANTAMIENTO_FUNCIONAL.md`, `output/LEVANTAMIENTO_TECNICO.md` and `codex/V3/V3_R8_4_REVISION_HUMANA_APROBADA.md` — none of which `main.py` produces.

---

## CAPABILITY_INVENTORY

| CAPABILITY | IMPLEMENTATION_LOCATION | INPUT | OUTPUT | DETERMINISTIC_OR_AI | CURRENTLY_REACHED_BY_CLI | REUSABLE_FOR_V4_2 | MISSING_INTEGRATION | RISKS |
|---|---|---|---|---|---|---|---|---|
| scanner | `scanner/repository_scanner.py`, `scanner/file_classifier.py` | repo root, excludes | `list[SourceFile]` | Deterministic | Yes | Yes, as-is | None | LOW |
| extractors | `extractors/*.py` (Solution, VBProj, VBNet, WebForms, WebConfig, Call, WebEvent, Database) | per-file path | per-file model | Deterministic | Yes | Yes, as-is | None | LOW |
| analysis.call_resolver | `analysis/call_resolver.py` | calls, symbols | resolved calls, functional deps | Deterministic | Yes | Yes, as-is | None | LOW |
| analysis.database_resolver | `analysis/database_resolver.py` (+ `_database_*` helpers) | data_access_indexes, projects | data_access, procs, sql_ops, params, deps | Deterministic | Yes | Yes, as-is | None | LOW |
| analysis.dependency_resolver | `analysis/dependency_resolver.py` | solutions, projects, symbols, webforms | dependencies | Deterministic | Yes | Yes, as-is | None | LOW |
| analysis.web_entry_resolver | `analysis/web_entry_resolver.py` | webforms, symbols, web_events, calls | entry_points, event_bindings, web deps | Deterministic | Yes | Yes, as-is | None | LOW |
| analysis.flow_resolver | `analysis/flow_resolver.py` (+ `_flow_*` helpers) | entry_points, calls, data_access, procs, sql_ops, functional_deps, errors | functional_flows, functional_paths, flow_summary, flow_unresolved | Deterministic | Yes | Yes, as-is | None | MEDIUM (deferred-refactor area per V4.1 debt ledger; touch carefully) |
| analysis.deep_source | `analysis/deep_source.py` | not confirmed in this pass | not confirmed | Not fully traced | No | Needs a dedicated read pass before reuse | Contract not verified | MEDIUM (unknown) |
| analysis.deep_interpretation | `analysis/deep_interpretation.py` | context + `ProviderConfig` (env-driven) | AI interpretation output | AI (provider-agnostic call site via `ProviderRegistry`) | No | Yes, with an explicit opt-in seam | Not wired to any orchestrator; no proposal/approval hook after it | MEDIUM |
| analysis.targeted_exhaustion | `analysis/targeted_exhaustion.py` | not confirmed in this pass | not confirmed | Not fully traced | No | Needs a dedicated read pass before reuse | Contract not verified | MEDIUM (unknown) |
| context | `context/context_builder.py`, `context/system_context_builder.py` | `indexes` dict | `output/context/projects.json`, `output/ai_context/{SYSTEM_CONTEXT.json,ARCHITECTURE_GRAPH.json,FUNCTIONAL_FLOWS.json,TRACEABILITY.json,SYSTEM_CONTEXT.md}` | Deterministic | Yes | Yes, as-is | None | LOW |
| context.resolver/composer | `context/resolver.py`, `context/composer.py` | reads `ai_context/*.json` from a workspace dir | LLM-prompt-ready context package | Deterministic (packaging) | No | Reusable but needs its input-path assumption verified against fresh output, not only the historical `v2_r5_1_full` snapshot | Path/schema compatibility with a fresh run unverified | MEDIUM |
| documentation (18 modules) | `documentation/*.py` | varies; `generator.py` hardcodes `output/v2_r5_1_full/ai_context/*.json` and a direct `CopilotProvider` instantiation | generated docs, consistency/coverage reports | Mostly AI-oriented / human-review workflow | No | Partially — logic is reusable, but path-hardcoding and direct-provider coupling must be removed before orchestration | Not wired to `main.py` output at all; hardcoded historical path | HIGH (hardcoded paths + provider bypass are real defects to fix before reuse, not just wiring gaps) |
| exporters | `exporters/json_exporter.py`, `exporters/markdown_exporter.py` | `indexes` dict | `output/index/*.json` (23 files), `output/documentation/*.md` (6 files) | Deterministic | Yes | Yes, as-is | None | LOW |
| llm | `llm/core.py` (`LLMProvider` ABC, `ProviderConfig`, `ProviderRegistry`), `llm/providers/copilot.py`, `llm/providers/gemini.py`, `llm/copilot_pilot.py` | — | — | AI infrastructure | No (unless `deep_interpretation`/`generator.py` run) | Yes for the registry pattern; Gemini provider file exists but is **not registered** in `ProviderRegistry.create()` (only `"FAKE"`/`"COPILOT"` recognized) | Gemini not wired into registry | LOW (registry itself is clean; the unregistered provider is a small, known gap) |
| knowledge/input | `knowledge/input/{contracts,catalog,normalization,validator}.py` | `SourceInput` | validated/normalized input | Deterministic | No | Yes, fully self-contained | No caller outside `knowledge/ingestion` + tests | LOW (isolated) |
| knowledge/ingestion | `knowledge/ingestion/service.py` | `SourceInput` | `IngestedMaterial`/`IngestionBatchResult` | Deterministic | No | Yes | No production caller | LOW (isolated) |
| knowledge/provenance | `knowledge/provenance/{graph,models,enums}.py` | material/nodes | `ProvenanceGraph` | Deterministic | No | Yes | No production caller | LOW (isolated) |
| knowledge/classification | `knowledge/classification/{service,catalog,enums,models}.py` | provenance nodes | classification decisions | Deterministic | No | Yes | No production caller | LOW (isolated) |
| knowledge/temporal | `knowledge/temporal/{service,models,enums}.py` | — | temporal-state records | Deterministic | No | Yes | No production caller | LOW (isolated) |
| knowledge/relations | `knowledge/relations/service.py` | — | relation records (gap/conflict/etc.) | Deterministic | No | Yes | No production caller | LOW (isolated) |
| knowledge/proposals | `knowledge/proposals/service.py` | — | proposal records | Deterministic | No | Yes | No production caller; no live producer of AI-sourced proposals feeds it today | MEDIUM (the proposal-generation side, e.g. from `deep_interpretation`, does not exist yet) |
| knowledge/approval | `knowledge/approval/service.py` | proposal | approval decision | Deterministic | No | Yes | No CLI/UX surface for a Technical Lead to actually record a decision | HIGH (this is the human-authority boundary; a real approval interface does not exist outside tests) |
| knowledge/canonical | `knowledge/canonical/service.py` | approved items | canonical records | Deterministic | No | Yes | No production producer feeds it | MEDIUM |
| knowledge/projection | `knowledge/projection/{service,rules,disk_io,markdown_renderer}.py` | canonical records | R11 Markdown projection | Deterministic | No | Yes | `disk_io.py` exists but its write path is not triggered by any CLI-reachable flow | MEDIUM |
| knowledge/plugin_projection | `knowledge/plugin_projection/{service,serializer,validator}.py` | canonical records | R12 plugin contract payload | Deterministic | No | Yes | No production caller; correctly matches `PLUGIN_RUNTIME=NOT_IMPLEMENTED` | LOW (intentionally dormant) |
| knowledge/readiness | `knowledge/readiness.py` + `_readiness_{io,parsing,evidence}.py` | pre-existing Markdown review docs (via `documentation.human_review`/`second_review`) + hashed artifacts | `output/v3_r9/*.json` | Deterministic | No (standalone `python -m` gate) | Yes, as a standalone gate | Reads `documentation/` outputs and historical `codex/V3/` files, not `main.py`/`knowledge/` pipeline outputs | LOW (works today as a closed, self-consistent gate; would need rework only if its input contract changes) |

---

## CURRENT_OUTPUT_INVENTORY

Verified from exporter/builder source (a representative live run was not executed against a real repository in this pass; the only available fixture, `tests/fixtures/v2_r1_sample/`, has no `.sln`/`.aspx`/`web.config`, so it would only degenerate-exercise the `vb_project`/`vb_source` extractors and is not representative of a full-pipeline smoke test — flagged as a gap in TEST_FIXTURES for a future round, not fabricated as if it were run):

**PUBLIC_USER_OUTPUT candidates (already produced today):**
- `output/documentation/{PROJECT_OVERVIEW.md, SOLUTION_STRUCTURE.md, PROJECT_DEPENDENCIES.md, WEBFORMS_MAP.md, CONFIGURATION_SUMMARY.md, ANALYSIS_WARNINGS.md}` — human-readable Markdown, generated deterministically by `MarkdownExporter`.
- `output/ai_context/SYSTEM_CONTEXT.md` — human-readable summary.

**MACHINE_OUTPUT (already produced today):**
- `output/index/*.json` — 23 files, one per top-level key of `indexes` (`repository, files, solutions, projects, symbols, logical_symbols, calls, entry_points, event_bindings, data_access, stored_procedures, sql_operations, data_parameters, functional_dependencies, functional_flows, functional_paths, flow_summary, flow_unresolved, webforms, configuration, dependencies, errors`).
- `output/context/projects.json`.
- `output/ai_context/{SYSTEM_CONTEXT.json, ARCHITECTURE_GRAPH.json, FUNCTIONAL_FLOWS.json, TRACEABILITY.json}`.

**EVIDENCE_OUTPUT:** `errors` (within `output/index/errors.json`) is the closest existing analogue today — a flat list of extraction/analysis failures. There is currently **no dedicated evidence/provenance artifact** produced by the default CLI run; the `knowledge/provenance` model exists but is disconnected (see KNOWLEDGE_PIPELINE_BOUNDARY).

**INTERNAL_OUTPUT (historical, not regenerated by current `main.py`):** `output/v3_final/V3_FINAL_BASELINE.json`, `output/v3_r9/{KNOWLEDGE_READINESS.json, KNOWLEDGE_PROJECTION.json, KNOWLEDGE_BOUNDARY.json, READINESS_TRACEABILITY.json}` — these are readiness-gate artifacts from a prior round, produced by `knowledge/readiness.py` reading hand-placed historical inputs (`output/LEVANTAMIENTO_FUNCIONAL.md`, `output/LEVANTAMIENTO_TECNICO.md`, `codex/V3/...`), not artifacts a fresh `main.py` run creates.

**Not yet established (do not assume for V4.2 design):** a "temporary/intermediate artifacts" area distinct from final output does not exist today — `main.py` writes directly to its final locations under `--output`; there is no separate staging/scratch directory convention to preserve or extend.

---

## DOCUMENTATION_CAPABILITY_MATRIX

| Candidate document | Classification | Basis |
|---|---|---|
| SYSTEM OVERVIEW | GENERATABLE_WITH_EXISTING_COMPONENTS | `output/documentation/PROJECT_OVERVIEW.md` + `output/ai_context/SYSTEM_CONTEXT.md` already cover this; only orchestration/renaming needed |
| TECHNICAL ARCHITECTURE | GENERATABLE_WITH_EXISTING_COMPONENTS | `output/ai_context/ARCHITECTURE_GRAPH.json` + `SOLUTION_STRUCTURE.md` + `PROJECT_DEPENDENCIES.md` cover most of this deterministically |
| PROJECTS / MODULES | ALREADY_GENERATED | `output/documentation/PROJECT_OVERVIEW.md`, `output/context/projects.json` |
| DEPENDENCIES | ALREADY_GENERATED | `output/documentation/PROJECT_DEPENDENCIES.md`, `output/index/dependencies.json` |
| WEB ENTRY POINTS | GENERATABLE_WITH_EXISTING_COMPONENTS | `output/index/entry_points.json` and `event_bindings.json` exist; no dedicated Markdown rendering of entry points exists yet — `WEBFORMS_MAP.md` covers Web Forms structure but not entry-point/flow-start semantics specifically; needs a small renderer |
| FUNCTIONAL FLOWS | GENERATABLE_WITH_EXISTING_COMPONENTS | `output/ai_context/FUNCTIONAL_FLOWS.json` and `output/index/functional_flows.json`/`functional_paths.json`/`flow_summary.json` exist as data; no Markdown rendering exists — needs REQUIRES_SMALL_NEW_RENDERER, listed here as the primary path since the data is fully present |
| DATABASE ACCESS | GENERATABLE_WITH_EXISTING_COMPONENTS | `output/index/data_access.json`, `stored_procedures.json`, `sql_operations.json` exist; no dedicated Markdown rendering exists today — needs a small renderer |
| UNRESOLVED FINDINGS | GENERATABLE_WITH_EXISTING_COMPONENTS | `output/index/errors.json`, `flow_unresolved.json` exist as data; `ANALYSIS_WARNINGS.md` already renders warnings but coverage of unresolved-flow-specific detail should be confirmed/extended |
| EVIDENCE / TRACEABILITY | REQUIRES_ORCHESTRATION | `output/ai_context/TRACEABILITY.json` exists at the code-analysis level, but true evidence/provenance in the V4-knowledge sense (`knowledge/provenance`) is fully disconnected from the code pipeline today (see KNOWLEDGE_PIPELINE_BOUNDARY) — producing a genuinely traceable, knowledge-grade evidence document requires wiring, not just a renderer |

No document above is classified `REQUIRES_NEW_DOMAIN_CAPABILITY` or `NOT_SUPPORTED_BY_CURRENT_EVIDENCE`: every candidate in the prompt's list has either existing output or existing structured data that a renderer/orchestrator can consume. The one genuinely open item is EVIDENCE/TRACEABILITY at knowledge-grade fidelity, which is an orchestration/wiring problem, not a missing-capability problem — the `knowledge/provenance` package already implements the model; it simply has no producer today.

---

## FULL_PIPELINE_PROPOSAL

Proposed V4.2 full-pipeline boundary, built strictly from what exists:

```
legacy source (read-only)
      │
      ▼
scan (scanner/)                                    — existing, unchanged
      │
      ▼
extraction (extractors/)                            — existing, unchanged, per-file tolerant
      │
      ▼
deterministic analysis (analysis/*_resolver.py)      — existing, unchanged
      │
      ▼
indexes + context (exporters/, context/)             — existing, unchanged
      │
      ├──────────────────────────────┐
      ▼                               ▼
human-readable documentation     [OPTIONAL] AI interpretation
(deterministic renderers over          (analysis/deep_interpretation.py,
 existing JSON — new small              provider-agnostic via
 renderers for flows/DB/                ProviderRegistry; OFF by default,
 entry points)                          explicit opt-in flag required)
      │                               │
      │                               ▼
      │                         Proposal (knowledge/proposals)
      │                               │
      │                               ▼
      │                    Technical Lead Approval (knowledge/approval)
      │                               │
      │                               ▼
      │                    Canonical Knowledge (knowledge/canonical)
      │                               │
      │                    ┌──────────┴──────────┐
      │                    ▼                      ▼
      │            R11 human projection    R12 plugin projection
      │            (knowledge/projection)  (knowledge/plugin_projection,
      │                                     still PLUGIN_RUNTIME=NOT_IMPLEMENTED)
      ▼
final run summary (new: a single top-level status/manifest artifact)
```

**Key architectural decision:** the deterministic code-analysis half (scan → extraction → analysis → indexes/context → deterministic documentation) can run fully automatically end-to-end today, reusing 100% existing, tested, deterministic components — this is the safe, always-on backbone of the "full pipeline."

The **knowledge/V4 half is a genuinely separate, currently disconnected subsystem** that must **not** be silently folded into an automatic run. A fully automatic run **cannot legitimately reach canonical knowledge**, because canonical knowledge requires a real `ApprovalDecisionType.APPROVED` from a human `Technical Lead` — there is no way to manufacture that automatically without violating the core V4/V4.1 principle ("AI output must never silently become approved canonical knowledge"). This boundary is stated explicitly, per instruction: **an automatic `full` run may produce AI-assisted *proposals* (if AI interpretation is explicitly enabled), but it must stop at `Proposal`, never auto-invoking `Approval`.** Canonical knowledge, R11 projection, and R12 projection remain human-gated, out of scope for what an unattended CLI run can produce end-to-end in V4.2.

---

## KNOWLEDGE_PIPELINE_BOUNDARY

Verified fact (not an assumption): **`legacy_documenter/knowledge/` and the code-analysis pipeline driven by `main.py` are two fully disconnected subsystems today.** No file under `legacy_documenter/` outside `knowledge/` imports anything from `knowledge/`, except one unrelated standalone audit script (`quality/maintainability_audit.py`) that is not part of `main.py`'s call graph. The only callers of `knowledge/*` services are `tests/` and each package's own self-documenting `contract_report.py`/`example_report.py` fixtures. `knowledge/readiness.py` reads historical, hand-placed Markdown review documents and `codex/V3/` files — not fresh output from `main.py` or from `knowledge/` itself.

**Implication for V4.2:** wiring `knowledge/` into an orchestrated pipeline is new integration work, not a refactor of an existing connection. The correct join points, in order of how little new logic they require:

1. **`knowledge/input` / `knowledge/ingestion`** can consume `main.py`'s `indexes` (particularly `errors`, `functional_flows`, `data_access`) as `SourceInput` material with `SourceType.DETERMINISTIC_CODE_FACT` — this is a straight adapter, no new domain logic.
2. **`knowledge/proposals`** needs an actual producer. Today nothing creates a `Proposal` from `analysis/deep_interpretation.py`'s output. This is the first real integration gap: an adapter from an LLM interpretation result to `ProposalKind.INTERPRETATION` / `ProposalMethod.AI_PROPOSED` does not exist.
3. **`knowledge/approval`** needs an actual human-facing surface. Today it is only exercised by tests calling the service directly. A V4.2 CLI cannot invent Technical Lead approval; at most it can produce a clearly-labeled "pending approval" artifact and let a human apply approval through a still-to-be-designed mechanism (this is explicitly out of scope to design in R0; flagged for R2–R4).
4. **`knowledge/canonical`**, **`knowledge/projection`**, **`knowledge/plugin_projection`** only become reachable once (2) and (3) exist; they are otherwise correctly dormant.

---

## AI_BOUNDARY

`analysis/deep_interpretation.py` uses a clean, provider-agnostic call site: it reads `LEGACYMAPPER_LLM_PROVIDER` (default `"COPILOT"`), `LEGACYMAPPER_LLM_MODEL`, `LEGACYMAPPER_LLM_PROVIDER_ID` from the environment, builds a `ProviderConfig`, and obtains a concrete provider through `llm/core.py::ProviderRegistry.create()`. This is the boundary V4.2 should reuse unchanged.

By contrast, `documentation/generator.py` (V3-R7 era) directly imports and instantiates `CopilotProvider`, bypassing `ProviderRegistry` entirely, and also hardcodes a read path to a historical output snapshot (`output/v2_r5_1_full/ai_context/*.json`). This is a real defect relative to the registry pattern already established elsewhere in the codebase, not merely a wiring gap — it must be corrected (route through `ProviderRegistry`, remove the hardcoded path) before this module can be reused inside an orchestrated V4.2 pipeline.

`llm/providers/gemini.py` exists as a file implementing the `LLMProvider` interface but is **not registered** in `ProviderRegistry.create()` (only `"FAKE"` and `"COPILOT"` are recognized) — a small, known gap, not a structural problem.

**V5 design input (recorded, not acted on in V4.2):** the coexistence of a clean registry-based call site (`deep_interpretation.py`) and a hardcoded direct-instantiation call site (`generator.py`) shows the current codebase is not uniformly provider-agnostic even today; V5's provider/model-agnosticism redesign should standardize all call sites on the `ProviderRegistry` pattern and formally register all provider implementations (including Gemini) rather than leaving some recognized-but-unregistered. V4.2 will fix the `generator.py` hardcoding as a correctness fix for reuse, but will **not** redesign the registry/provider abstraction itself.

---

## CLI_OPTIONS_EVALUATED

**A. Preserve existing command and add `--full`**
`python main.py <repository> --output <dir> --full` — Pros: zero breaking change, minimal argparse delta, trivially backward compatible. Cons: overloads a single command with two very different execution modes (today's deterministic-only run vs. a broader pipeline that may include AI proposals); makes future scriptable composition (e.g. "just run readiness", "just run analysis") awkward as more modes accumulate; conflates "what to run" with "how much to run" in one boolean flag.

**B. Introduce subcommands (`analyze` / `full` / `readiness`)**
`python main.py analyze <repository> --output <dir>`, `python main.py full <repository> --output <dir> [--allow-ai-interpretation]`, `python main.py readiness` — Pros: scriptable, each subcommand has a clear single responsibility, matches the way `knowledge/readiness` is already invoked as its own `python -m` entry point conceptually, leaves room for future subcommands (e.g. a future `approve` surface) without overloading flags, and each subcommand can evolve its own flag set independently (important for V5 extensibility). Cons: is a breaking change to the current invocation shape (`python main.py <repository>` no longer works verbatim) unless the legacy positional form is preserved as an implicit-default subcommand.

**C. Minimal alternative — keep single command, no `--full`, only add opt-in AI/knowledge flags directly**
`python main.py <repository> --output <dir> --with-interpretation --with-knowledge-ingestion` — Pros: avoids subcommand complexity entirely. Cons: does not scale — as V4.2 adds more optional stages (interpretation, proposal, projection preview), flag count grows unmanageably, and it still conflates "one command, many unrelated concerns" the same way Option A does, only worse as more flags are added.

---

## CLI_RECOMMENDATION

**Recommend Option B (subcommands), implemented so that Option A's backward-compatibility concern is fully neutralized:** keep `python main.py <repository> [--output ...] [--exclude ...] [--verbose] [--flow-max-depth N]` working exactly as today by treating a bare positional repository argument (no subcommand) as an implicit alias for the new `analyze` subcommand — i.e., existing scripts and CI invocations do not break. Add `full` as a new subcommand that runs the deterministic backbone described in FULL_PIPELINE_PROPOSAL plus, only when explicitly requested via a flag such as `--allow-ai-interpretation`, the optional AI-interpretation-to-proposal stage (never auto-approval). Add `readiness` as a thin subcommand wrapper around the existing `python -m legacy_documenter.knowledge.readiness` entry point, purely for discoverability — the existing `python -m` invocation remains valid and undocumented removal of it is not proposed.

This best satisfies the prompt's priorities: **clarity** (each subcommand does one clearly named thing), **backward compatibility** (bare positional form preserved as an alias), **scriptability** (subcommands compose cleanly in CI/scripts, exit codes and `--output` stay uniform), **future V5 extensibility** (new subcommands or per-subcommand flags can be added without touching unrelated ones), **simple implementation** (argparse subparsers are a standard, low-risk pattern), and **low duplication** (the `full` subcommand orchestrates existing components rather than reimplementing them, per the "CLI must be an orchestration boundary, not a second domain layer" principle).

---

## OUTPUT_EXPERIENCE_PROPOSAL

Derived from CURRENT_OUTPUT_INVENTORY, not invented from scratch:

- **PUBLIC_USER_OUTPUT:** the existing `output/documentation/*.md` family, extended with the two small new renderers identified in DOCUMENTATION_CAPABILITY_MATRIX (functional flows, database access), plus a new top-level **run summary** document (human-readable status: what ran, what was partial/unresolved, whether AI interpretation ran, whether any proposals are pending approval).
- **MACHINE_OUTPUT:** the existing `output/index/*.json` and `output/ai_context/*.json` families, unchanged in shape; a `full` run adds, only when AI interpretation was requested, the resulting `Proposal` records serialized under a clearly separate location (not mixed into `output/index/`, which is deterministic-only today) — exact filenames are deferred to R1/R2 design, not fixed here.
- **EVIDENCE_OUTPUT:** today's closest analogue (`errors.json`, `flow_unresolved.json`, `TRACEABILITY.json`) remains as-is for the deterministic backbone; a knowledge-grade evidence/provenance artifact (from `knowledge/provenance`) only appears once the ingestion adapter described in KNOWLEDGE_PIPELINE_BOUNDARY exists — this is future-round work, explicitly not promised as part of R0.
- **INTERNAL_OUTPUT:** no change proposed to how `main.py` writes directly to final locations; introducing a separate staging/scratch area is a candidate simplification for a later round (would help make partial/aborted runs less confusing) but is not required for R0 and is not decided here.

Filenames above are illustrative of category, not finalized, per instruction.

---

## PARTIAL_FAILURE_POLICY

Today's actual behavior, verified from `main.py`, is **inconsistent** and should be corrected in V4.2, not merely preserved:

- Extraction (steps 2–3) is already correctly partial-tolerant: a per-file exception is caught, recorded in `errors`, and the run continues.
- Resolvers and exporters (steps 5–11) have **no** exception handling: any single unexpected error aborts the entire run, discarding all partial results already computed (including everything the tolerant extraction stage produced).

**Proposed policy for the `full` pipeline (design only, not implemented in R0):**
- Preserve the existing per-file-tolerant behavior for extraction, unchanged.
- Wrap each resolver stage (call/database/dependency/web-entry/flow resolution) and each output stage (exporters/context/documentation) in a stage-level boundary that records a structured failure (stage name, exception summary, affected inputs where knowable) into the run summary and **continues to the next independent stage** where the next stage does not strictly require the failed stage's output; where it does (e.g. flow resolution needs entry points), that dependent stage is itself marked `SKIPPED_DUE_TO_UPSTREAM_FAILURE` rather than crashing.
- AI unavailability or AI interpretation failure must degrade to "no proposals generated," never to invented interpretation — this matches the existing principle and requires no new behavior, only ensuring the optional interpretation stage is wrapped the same way.
- Absent human information, partial source code, or `readiness != READY` are all valid, expected states for a `full` run to complete "successfully" while explicitly reporting reduced coverage in the run summary — never silently upgraded to `UNRESOLVED → assumed value`.
- **Never** convert `UNRESOLVED`/`MISSING`/partial states into invented facts at any stage — this is a hard invariant carried over unchanged from V4/V4.1.

---

## V5_BOUNDARY

Explicitly preserved as V5, not V4.2, scope: language agnosticism, framework agnosticism, architecture/project-layout agnosticism, database/persistence agnosticism, AI provider/model agnosticism. V4.2's only justified seam relevant to V5 is the CLI subcommand structure recommended above (CLI_RECOMMENDATION) — subcommands make it straightforward for V5 to later add agnostic variants without redesigning the CLI surface — and the correction of `documentation/generator.py`'s hardcoded provider instantiation to use the existing `ProviderRegistry`, which is a V4.2 correctness fix (making existing code consistent with the existing abstraction) rather than the V5 redesign of that abstraction itself.

---

## RISKS

| Risk | Classification | Mitigation |
|---|---|---|
| Orchestration duplication (CLI reimplementing analysis/knowledge logic instead of calling it) | MEDIUM | Enforce the "CLI is an orchestration boundary" principle in code review; the `full` subcommand must only call existing services/classes, never re-derive their logic |
| Coupling between current `main.py` and analysis components | LOW | `main.py`'s sequence is already a simple, readable orchestration of independent classes; extending it into subcommands is additive, not a rewrite |
| Generated artifact dependencies (e.g. `generator.py`'s hardcoded `v2_r5_1_full` path) | HIGH | Must be fixed as part of reuse, not worked around; fix the path to read from the run's actual `--output` directory before `documentation/generator.py` is wired into any orchestrated flow |
| Historical output dependencies (`knowledge/readiness.py` reading `codex/V3/` and hand-placed Markdown) | MEDIUM | Leave `readiness.py`'s existing contract untouched for now (it is a closed, working gate); do not assume a `full` run's fresh output can silently replace its inputs without a dedicated compatibility pass |
| AI availability/provider dependencies | LOW | Already isolated behind `ProviderRegistry`; `full` pipeline must treat AI interpretation as strictly optional and degrade gracefully per PARTIAL_FAILURE_POLICY |
| Output size/performance (23 JSON index files + context + docs, potentially on large real repositories) | MEDIUM | No evidence gathered in this pass on real-repository scale performance; recommend a dedicated performance check against a realistic-size repository before R7 pilot, not assumed safe by default |
| Deterministic reproducibility | LOW | The deterministic backbone (scan→extract→analyze→export) has no identified sources of non-determinism in this pass; the only new risk is if AI-interpretation-derived proposals are serialized with non-deterministic ordering — must be addressed when that adapter is built |
| Source immutability (legacy source must remain read-only) | LOW | No write path to the analyzed repository was found anywhere in the inspected code; principle holds today and should be asserted with a test if not already covered |
| Approval-boundary risk (a `full` run silently reaching canonical knowledge) | HIGH | Explicitly designed out in FULL_PIPELINE_PROPOSAL: automatic runs stop at `Proposal`; no code path from `deep_interpretation` to `canonical`/`approval` exists today, and none should be added without a real human-facing approval surface, which is out of scope until a future round explicitly designs it |
| Regression risk to V4.1 | LOW | V4.2 is additive (new subcommands, new adapters); the existing bare-positional-argument `analyze` behavior is preserved verbatim, and no V4.1 knowledge-package internals are proposed to change |
| Future V5 migration risk | LOW | The recommended subcommand structure and the `generator.py` provider-registry fix both reduce, rather than increase, future V5 migration cost; no V5-shaped abstraction is being introduced prematurely |

---

## PROPOSED_V4_2_ROADMAP

The preliminary roadmap in the task prompt is **validated with two adjustments**, based on evidence gathered in this round:

- **V4.2-R0** — Baseline + inventory + architecture. *(this document)*
- **V4.2-R1** — CLI contract + execution/result model. Introduce the `analyze`/`full`/`readiness` subcommand structure (CLI_RECOMMENDATION) and a formal run-result/summary model (status, per-stage outcome, errors) — this is prerequisite plumbing for everything after it.
- **V4.2-R2** — Full-pipeline orchestrator for the deterministic backbone only (scan→extract→analyze→export→context), applying the corrected PARTIAL_FAILURE_POLICY (stage-level tolerance) to the currently-fragile resolver/exporter stages. **Adjustment:** explicitly scope R2 to the deterministic backbone only; do not bundle AI interpretation into R2, to keep the approval-boundary risk isolated to a later, dedicated round.
- **V4.2-R3** — Integration of existing technical analysis into the new renderers identified in DOCUMENTATION_CAPABILITY_MATRIX (functional flows, database access, entry points) — small, additive, low-risk.
- **V4.2-R4** — Interpretation/context/documentation integration. **Adjustment:** this round must explicitly include (a) fixing `documentation/generator.py`'s hardcoded path and direct `CopilotProvider` instantiation (flagged HIGH risk above) as a precondition to reusing it, and (b) building the `knowledge/proposals` adapter from `deep_interpretation` output — this is new integration code, not existing-capability wiring, and should be estimated accordingly.
- **V4.2-R5** — Unified full CLI and user-facing output experience (OUTPUT_EXPERIENCE_PROPOSAL), including the run summary artifact.
- **V4.2-R6** — Robustness, partial results, recovery, security — formalizing PARTIAL_FAILURE_POLICY across all stages, plus a first design pass (not implementation) on the human-facing approval surface identified as a gap in KNOWLEDGE_PIPELINE_BOUNDARY.
- **V4.2-R7** — Real pilot against the IST/Operacional legacy system. **Note:** `tests/fixtures/` currently contains no repository-scale fixture (only `v2_r1_sample/`, three files, no `.sln`/`.aspx`/`web.config`) — R7 should also produce a smaller, committable synthetic fixture exercising the full extractor set (solution + web forms + config + VB), both for CI smoke-testing and to avoid every full-pipeline validation depending on access to the real, non-public IST/Operacional repository.
- **V4.2-R8** — Documentation, comprehensive regression, baseline and formal closure — unchanged from the preliminary roadmap.

No round is implemented in this R0 pass.

---

## PRODUCTION_CODE_CHANGED

PRODUCTION_CODE_CHANGED=false

## TESTS_CHANGED

TESTS_CHANGED=false

## V4_1_REOPENED

V4_1_REOPENED=false

## V5_IMPLEMENTED

V5_IMPLEMENTED=false

## PLUGIN_RUNTIME

PLUGIN_RUNTIME=NOT_IMPLEMENTED

---

## DECISION

DECISION=V4_2_R0_READY_FOR_TECHNICAL_LEAD_REVIEW

## NEXT

NEXT=HUMAN_REVIEW_V4_2_R0
