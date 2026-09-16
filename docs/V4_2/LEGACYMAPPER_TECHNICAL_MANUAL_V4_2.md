# LegacyMapper — Technical Manual (V4.2)

This is the primary developer-handover, maintenance, and code-audit map for LegacyMapper. It is derived
from reading the current source tree (`legacy_documenter/`, `main.py`, `tests/`, `tools/`), current
contracts (`PROJECT_STATE.json`, `.gitignore`, `docs/GENERATED_ARTIFACT_POLICY.md`), and current V4.2
closure documents — not from memory of historical documentation. Where current code disagrees with
historical claims, this manual documents the current implementation and flags the discrepancy explicitly
(see also the round result document's `SOURCE_VS_DOCUMENTATION_DISCREPANCIES` section).

V4.2 is formally closed. V5 is not implemented. Nothing in this manual should be read as V5 already
existing.

---

## §6 Repository Map

| Path | Kind | Responsibility |
|---|---|---|
| `main.py` | Entry point | Two lines: imports `legacy_documenter.main.main` and calls it as the process exit code. |
| `legacy_documenter/` | Production source | The entire LegacyMapper implementation (169 `.py` files as of this round — see §22). |
| `tests/` | Tests | 62 test modules, `unittest`-based, organized chronologically by round (V1→V4.2-R8). See §16. |
| `tools/` | Developer tooling | One-off/manual scripts: baseline/manifest builders, a safe manual AI-path verifier, historical V4.1 round generators. Not imported by production code. See §17. |
| `docs/` | Governance/history | Round result documents, closure records, the generated-artifact policy, the recovery document, this manual set. Organized by version (`V3/`, `V4/`, `V4_1/`, `V4_2/`). |
| `prompts/` | Governance/history | The active/historical instruction documents each round was executed against, organized the same way as `docs/`. |
| `codex/` | Development-agent history | Machine-oriented, compact reports/instructions produced by the development agent, historically Codex-led (V1–V3); name preserved for continuity, not a Codex-only requirement (`AGENTS.md`). |
| `result_codex/` | Historical evidence | Early (V1-era) analysis report(s) predating the `codex/`/`docs/` split. |
| `output/` | Mixed: tracked contracts + local generated output | Small canonical artifacts (baselines, manifests, approved documentation) are tracked; heavy/regenerable scan dumps and real-system pilot output are `.gitignore`-excluded. See §19. |
| `context/` | Runtime working directory | Created and populated at runtime by `legacy_documenter/context/context_builder.py`; empty in a clean checkout except `.gitkeep`. **Naming collision**: this top-level `context/` is unrelated to the production package `legacy_documenter/context/` (see §8). |
| `AGENTS.md` | Governance | Development-agent operating instructions: autonomy, permission boundary, project rules, phase control. |
| `CLAUDE.md` | Governance | Points any Claude-based agent at `AGENTS.md`/`PROJECT_STATE.json`/handover docs; deliberately does not duplicate rules. |
| `PROJECT_STATE.json` | Governance | The single authoritative, machine-readable pointer to current version/round/status/known risks/debt. |
| `.gitignore` | Governance/mechanical | Enforces the generated-artifact policy by explicit path, never a broad wildcard. |

## §7 Module Inventory

All packages are under `legacy_documenter/`. "Called by" is CLI-command-oriented; most knowledge
sub-packages are reachable only from their own tests and from `readiness.py`/`main.py`'s legacy path, not
from `full`'s orchestration.

| Package | Purpose | Key files | Primary classes/functions | Inputs | Outputs | Depends on | Called by | Tests |
|---|---|---|---|---|---|---|---|---|
| `cli/` | CLI parsing, routing, execution/result model, resilient `full` orchestration, UX presentation | `parser.py`, `router.py`, `execution_model.py`, `stage_identity.py`, `pipeline_stages.py`, `full_pipeline.py`, `run_summary_presenter.py`, `artifact_lifecycle.py`, `serialization.py` | `build_parser`, `route`, `RunResult`/`StageResult`/`RunStatus`/`StageStatus`, `StageId`, `run_full_pipeline` | `sys.argv`, filesystem repo path | Exit code, `RunResult`, `RUN_SUMMARY.{json,md}` | `orchestration/`, `knowledge/readiness.py`, `scanner/`, `extractors/`, `analysis/`, `exporters/`, `context/`, `documentation/` | `main.py` | `test_v4_2_r1_*`, `_r2_*`, `_r5*`, `_r6*` |
| `scanner/` | Deterministic repository walk and per-file classification | `repository_scanner.py`, `file_classifier.py` | `RepositoryScanner`, `FileClassifier` | Repo root path, exclude list | List of `SourceFile`, classification stats | `models/`, `config.py` | `cli/pipeline_stages.py` | `test_v1*`, `test_v4_2_r2*` |
| `extractors/` | Parses source/config/project files into domain models | `solution_extractor.py`, `vbproj_extractor.py`, `vbnet_extractor.py`, `webforms_extractor.py`, `webconfig_extractor.py`, `web_event_extractor.py`, `call_extractor.py`, `database_extractor.py` + private `_database_*.py` helpers | `SolutionExtractor`, `VBProjExtractor`, `VBNetExtractor`, `WebFormsExtractor`, `WebConfigExtractor`, `WebEventExtractor`, `CallExtractor`, `DatabaseExtractor` | Classified `SourceFile`s | Solutions, projects, symbols, WebForms, calls, data-access records, SQL operations, config | `models/`, `scanner/` | `cli/pipeline_stages.py::extract_repository` | `test_v1*`, `test_v3_r*`, `test_v4_1_r5/r6_*extractor*` |
| `analysis/` | Deterministic resolution/interpretation over extracted data | `call_resolver.py`, `web_entry_resolver.py`, `database_resolver.py`, `flow_resolver.py` (+ `_flow_graph_construction.py`, `_flow_key_labels.py`, `_flow_report_composition.py`), `dependency_resolver.py`, `deep_source.py`, `deep_interpretation.py`, `targeted_exhaustion.py` | `CallResolver`, `WebEntryResolver`, `DatabaseResolver`, `FlowResolver`, `DependencyResolver` | Extracted symbols/calls/webforms/data-access | Resolved calls, entry points, functional flows/paths, dependency graph | `models/`, `extractors/` | `cli/pipeline_stages.py` | `test_v4_1_r5/r6_flow_resolver*`, `test_v4_2_r7_1*`, `test_v4_2_r7_synthetic*` |
| `exporters/` | Deterministic JSON/Markdown rendering of analysis results | `json_exporter.py`, `markdown_exporter.py`, `technical_documentation_renderer.py`, `_documentation_partitioning.py` | `JSONExporter`, `MarkdownExporter`, `TechnicalDocumentationRenderer` | `indexes` dict assembled by `pipeline_stages`/`full_pipeline` | `index/*.json`, `documentation/*.md`, `documentation/<doc>/<safe-name>.md` | `utils/atomic_write.py`, `utils/sanitizer.py` | `cli/pipeline_stages.py::render_documentation` | `test_v4_2_r3*`, `test_v4_2_r7_1*`, `test_v4_2_r8*` |
| `context/` | Builds compact runtime context artifacts and a read/compose boundary for AI | `context_builder.py`, `system_context_builder.py`, `resolver.py`, `composer.py` | `ContextBuilder`, `SystemContextBuilder`, `ContextResolver`, `ContextComposer` | `indexes`, `output/ai_context/*.json` | `output/context/projects.json`, composed context packages | none beyond `utils/` | `cli/pipeline_stages.py`, `orchestration/ai_interpretation.py` | `test_v3_r2_r3*`, `test_v4_2_r4*` |
| `documentation/` | V3-era LLM-assisted functional/technical document generation, aggregation, consistency, human-review parsing | `generator.py`, `renderer.py`, `aggregation.py`, `interpretation.py`, `consistency.py`, `consistency_run.py`, `coverage.py`, `evidence_catalog.py`, `evidence_resume.py`, `envelope.py`, `hierarchical.py`, `human_review.py`, `second_review.py`, `synthesis.py`, `systematic.py`, `resume.py`, `contracts.py` | `render`, `aggregate`, `parse_document`, `AssessmentValidator` | Context packages, LLM responses (V3 path only) | `output/LEVANTAMIENTO_FUNCIONAL.md`/`_TECNICO.md` and related evidence JSON | `context/`, `llm/` | `knowledge/readiness.py` (reads outputs only); not called by `full`/`analyze` | `test_v3_r6*`, `test_v3_r7*`, `test_v3_r8*` |
| `knowledge/` | V4 knowledge-domain model: ingestion → provenance → classification → temporal → relations → proposals → approval → canonical → projection/plugin_projection; plus the V3-R9 readiness gate and V4.1-R0/V4-R14 closure reports | See sub-package table below | — | — | — | `documentation/`, `context/` (readiness only) | `readiness()` only reachable from CLI; sub-packages otherwise self-contained and test-only | `test_v3_r9*`, `test_v4_r1..r14*` |
| `llm/` | Provider-neutral request/response contracts and concrete provider adapters | `core.py`, `providers/copilot.py`, `providers/gemini.py`, `copilot_pilot.py` | `LLMProvider`, `FakeLLMProvider`, `ProviderRegistry`, `CopilotProvider`, `GeminiProvider` | `LLMRequest` | `LLMResponse` | none | `orchestration/ai_interpretation.py`, `documentation/generator.py` (V3 path) | `test_v4_2_r4*`, `test_v4_2_r5_1*` |
| `orchestration/` | V4.2-R4 seam between `full` and AI/proposal logic | `ai_interpretation.py`, `proposal_adapter.py` | `run_ai_interpretation`, `adapt_findings_to_proposals` | `output/ai_context/*.json`, injected/resolved `LLMProvider` | `AiInterpretationResult`, `list[Proposal]` | `context/`, `llm/`, `knowledge/proposals/models.py` | `cli/full_pipeline.py` | `test_v4_2_r4*` |
| `models/` | Plain domain dataclasses shared across extraction/analysis/export | `call.py`, `dependency.py`, `entry_point.py`, `evidence.py`, `project.py`, `source_file.py`, `symbol.py`, `webform.py` | `Call`, `Dependency`, `EntryPoint`, `Evidence`, `Project`, `SourceFile`, `Symbol`, `WebForm` | — | — | none | Nearly every other package | Covered indirectly by extractor/scanner/analysis tests |
| `quality/` | Deterministic AST-based maintainability inventory tooling | `maintainability_audit.py` | `audit`/`build_maintainability_inventory`/`write_audit` | Production `.py` tree | Maintainability JSON (module sizes, typing/docstring coverage) | none (stdlib `ast` only) | `tools/`, historical V3-R10/V4.1-R0 rounds | `test_v4_1_r0_maintainability_inventory*` |
| `utils/` | Small deterministic infrastructure helpers | `atomic_write.py`, `json_rendering.py`, `sanitizer.py` | `atomic_write_text`, `render_deterministic_json`, `sanitize_data` | — | — | none | Nearly every writer in the codebase | Covered indirectly across suite |
| `config.py` | Shared constants | — | `DEFAULT_EXCLUDES`, `VTI_PREFIX` | — | — | none | `scanner/` | — |
| `main.py` (package-level, distinct from top-level `main.py`) | Legacy `analyze_repository` compatibility orchestration + CLI `main()` | — | `analyze_repository`, `main` | CLI args | Same as `analyze` (§4.4) | `cli/parser.py`, `cli/router.py`, `cli/pipeline_stages.py` | top-level `main.py` | `test_v1*`, `test_v4_2_r1*` |

### `knowledge/` sub-packages (detail)

| Sub-package | Round origin | Purpose | Reachable from CLI? |
|---|---|---|---|
| `domain/` | V4-R1 | Source-neutral domain model: `KnowledgeStatement`, `EvidenceRef`, `Provenance`, enums (`KnowledgeNature`, `KnowledgeStatus`, `SourceType`, `TemporalState`) | No — foundational types only |
| `input/` | V4-R2 | Validates/normalizes/sanitizes raw material into `MaterialItem` per `SourceType` | No |
| `ingestion/` | V4-R4 | Converts a human-authored `SourceInput` into a traceable `MaterialItem` + `MATERIAL` `ProvenanceNode` | No |
| `provenance/` | V4-R3 | Acyclic `ProvenanceGraph`/`ProvenanceNode` lineage answering "where did this come from" | No |
| `classification/` | V4-R5 | Records `KnowledgeNature` for an ingested `MaterialItem` without inferring new facts | No |
| `temporal/` | V4-R6 | AS_IS/TO_BE/HISTORICAL/GAP temporal-bucket separation | No |
| `relations/` | V4-R7 | Gap/conflict/difference/evolution relation representation | No |
| `proposals/` | V4-R8 | `Proposal` pre-approval lifecycle model (`ProposalStatus`, `ProposalKind`, `ProposalMethod`) | **Yes** — `orchestration/proposal_adapter.py` constructs `Proposal` records that `full_pipeline.py` writes |
| `approval/` | V4-R9 | `ApprovalDecision` model for Technical Lead APPROVED/REJECTED/CORRECTION_REQUESTED | No — design-only surface, `IMPLEMENTATION_STATUS=NOT_IMPLEMENTED` |
| `canonical/` | V4-R10 | Composes an approved `Proposal` + `ApprovalDecision` into an immutable `CanonicalKnowledgeEntry` | No |
| `projection/` | V4-R11 | Projects a `CanonicalKnowledgeCollection` into human-readable Markdown (`DocumentProjection`) | No |
| `plugin_projection/` | V4-R12 | Projects a `CanonicalKnowledgeCollection` into `LegacyMapperPluginKnowledge` (versioned machine-readable payload) | No |
| `closure/` | V4.1-R10/V4-R14/V4.2-R8 | Builds final baseline/manifest reports from repository state (used by `tools/*_build_*artifacts.py`) | No (tooling only) |
| `readiness.py` + `_readiness_*.py` | V3-R9, extracted V4.1-R4 | LegacyMapper's own knowledge-readiness gate | **Yes** — `python main.py readiness` |

Everything from `proposals/` through `plugin_projection/` (except `proposals/`, which `full` does use) is
implemented and unit-tested, but **not orchestrated together** by any command. A developer extending the
approval/canonical/projection workflow into an actual CLI surface is building new orchestration on top of
already-solid domain code, not writing that domain code from scratch.

## §8 File Map (selected significant files)

| File | Kind | Responsibility | Key class/function | Collaborators | Tests |
|---|---|---|---|---|---|
| `legacy_documenter/cli/parser.py` | Orchestration/CLI | Argument grammar + legacy bare-positional rewrite | `build_parser`, `normalize_argv` | `router.py` | `test_v4_2_r1*`, `test_v4_2_r5*` |
| `legacy_documenter/cli/router.py` | Orchestration/CLI | Dispatch + exit-code mapping (authoritative `EXIT_*` constants) | `route` | `full_pipeline.py`, `knowledge/readiness.py` | `test_v4_2_r1*`, `test_v4_2_r5_1*` |
| `legacy_documenter/cli/execution_model.py` | Domain model/contract | `RunResult`/`StageResult`/`RunStatus`/`StageStatus`/`StageError` | — | Everything under `cli/` | `test_v4_2_r1*`, `test_v4_2_r5*` |
| `legacy_documenter/cli/stage_identity.py` | Contract | `StageId` enum, the 13-stage vocabulary | — | `full_pipeline.py` | `test_v4_2_r1*` |
| `legacy_documenter/cli/pipeline_stages.py` (421 lines) | Orchestration (shared) | The actual stage functions `analyze`/`full` both call; also `render_documentation`/`DocumentationOutcome` | `scan_repository`, `extract_repository`, `resolve_calls`, `resolve_web_entries`, `resolve_database`, `resolve_flows`, `resolve_dependencies`, `export_artifacts`, `build_context_artifacts`, `render_documentation` | `scanner/`, `extractors/`, `analysis/`, `exporters/`, `context/` | `test_v3_r2_r3*`, `test_v4_2_r2/r3*` |
| `legacy_documenter/cli/full_pipeline.py` (490 lines) | Orchestration (resilient) | `run_full_pipeline`: 13-stage resilient orchestrator, `RunResult` finalization, proposal persistence | `run_full_pipeline`, `_compute_status`, `_assemble_indexes`, `_write_proposal_output` | `pipeline_stages`, `artifact_lifecycle`, `run_summary_presenter`, `orchestration/*` | `test_v4_2_r2*`, `_r4*`, `_r6*` |
| `legacy_documenter/cli/run_summary_presenter.py` (234 lines) | Renderer/UX | Console + `RUN_SUMMARY.md` rendering; derives `next_action`/`output_locations` | `render_console_summary`, `render_markdown_summary`, `derive_next_action`, `compute_output_locations` | `full_pipeline.py` | `test_v4_2_r5*` |
| `legacy_documenter/cli/artifact_lifecycle.py` | Utility (rerun safety) | Removes stale `proposals/` before a new `full` run starts | `reset_stale_proposal_artifacts` | `full_pipeline.py` | `test_v4_2_r6*` |
| `legacy_documenter/cli/serialization.py` | Utility | `RunResult` → deterministic JSON | — | `full_pipeline.py`/tests | `test_v4_2_r1*` |
| `legacy_documenter/scanner/repository_scanner.py` | Infrastructure | Recursive walk with exclude handling | `RepositoryScanner` | `file_classifier.py`, `models/source_file.py` | `test_v1*` |
| `legacy_documenter/scanner/file_classifier.py` | Extractor-adjacent | Per-file type classification by extension/name | `FileClassifier` | — | `test_v1*` |
| `legacy_documenter/extractors/database_extractor.py` (358 lines) | Extractor | Extracts SQL/data-access evidence from VB.NET source, delegating token/line/classification detail to its `_database_*` helpers | `DatabaseExtractor` | `_database_classification.py`, `_database_line_scanner.py`, `_database_token_parsing.py` | `test_v4_1_r5/r6_database_extractor*` |
| `legacy_documenter/extractors/call_extractor.py` (245 lines) | Extractor | Extracts method-call sites from VB.NET source | `CallExtractor` | `models/call.py` | `test_v1*`, `test_v3_r4*` |
| `legacy_documenter/extractors/vbnet_extractor.py` | Extractor | Parses VB.NET class/method/symbol declarations | `VBNetExtractor` | `models/symbol.py` | `test_v1*` |
| `legacy_documenter/extractors/webforms_extractor.py` | Extractor | Parses `.aspx`/`.ascx` markup for controls | `WebFormsExtractor` | `models/webform.py` | `test_v1*` |
| `legacy_documenter/extractors/web_event_extractor.py` | Extractor | Parses markup-declared UI event bindings | `WebEventExtractor` | `analysis/web_entry_resolver.py` | `test_v1*` |
| `legacy_documenter/extractors/webconfig_extractor.py` | Extractor | Parses `web.config` for configuration facts | `WebConfigExtractor` | — | `test_v1*` |
| `legacy_documenter/extractors/solution_extractor.py` / `vbproj_extractor.py` | Extractor | Parses `.sln`/`.vbproj` project structure | `SolutionExtractor`, `VBProjExtractor` | `models/project.py` | `test_v1*` |
| `legacy_documenter/analysis/flow_resolver.py` (312 lines) + `_flow_graph_construction.py`, `_flow_key_labels.py`, `_flow_report_composition.py` | Resolver (largest analysis component) | Builds and reports functional-flow graphs up to `--flow-max-depth`; worst-case status aggregation across traced paths | `FlowResolver` | `call_resolver.py`, `web_entry_resolver.py`, `database_resolver.py` | `test_v4_1_r5/r6_flow_resolver*`, `test_v4_2_r7_1*`, `test_v4_2_r7_synthetic*` |
| `legacy_documenter/analysis/call_resolver.py` | Resolver | Resolves extracted call sites to declared symbols | `CallResolver` | `models/symbol.py`, `models/call.py` | `test_v1*` |
| `legacy_documenter/analysis/web_entry_resolver.py` | Resolver | Resolves UI event bindings to confirmed/unresolved entry points; known gap: never attaches `outgoing_calls` to markup-bound entries (F-07) | `WebEntryResolver` | `extractors/web_event_extractor.py` | `test_v4_2_r7_synthetic*::FunctionalFlowTests` |
| `legacy_documenter/analysis/database_resolver.py` | Resolver | Resolves data-access records to stored procedures/SQL operations | `DatabaseResolver` | `extractors/database_extractor.py` | `test_v1*` |
| `legacy_documenter/analysis/dependency_resolver.py` | Resolver | Builds inter-project/inter-symbol dependency graph | `DependencyResolver` | `models/dependency.py` | `test_v1*` |
| `legacy_documenter/analysis/deep_source.py`, `deep_interpretation.py`, `targeted_exhaustion.py` | V3-era analysis tools | Historical V3-R7/R8 evidence-exhaustion and interpretation tooling, hardcoded to `output/v3_r8_1` fixed evidence files/target ids; **not called by `full`'s `AI_INTERPRETATION` stage** (see §13) | `run_deep_interpretation` (among others) | `context/` | `test_v3_r7*`, `test_v3_r8*` |
| `legacy_documenter/exporters/markdown_exporter.py` | Renderer | The six original fixed-filename documents | `MarkdownExporter` | `utils/atomic_write.py` | `test_v4_2_r3*` |
| `legacy_documenter/exporters/technical_documentation_renderer.py` (802 lines, `TechnicalDocumentationRenderer` class ~462 of them per V4.2 closure baseline — see §12 for the current measurement) | Renderer (flagged maintainability debt) | Four documents plus their V4.2-R8 navigation/partition variants | `TechnicalDocumentationRenderer` | `_documentation_partitioning.py`, `markdown_exporter._repository_display_label` | `test_v4_2_r3*`, `_r7_1*`, `_r8*` |
| `legacy_documenter/exporters/_documentation_partitioning.py` | Utility | Deterministic, path-traversal-safe filename derivation for partitions | `sanitize_label`, `build_partition_filenames` | `technical_documentation_renderer.py` | `test_v4_2_r8*` |
| `legacy_documenter/exporters/json_exporter.py` | Renderer/adapter | Writes sanitized `index/*.json` | `JSONExporter` | `utils/sanitizer.py`, `utils/atomic_write.py` | `test_v1*` |
| `legacy_documenter/context/context_builder.py` | Write-stage adapter | Writes `output/context/projects.json` per-project summary | `ContextBuilder` | — | `test_v3_r2_r3*` |
| `legacy_documenter/context/system_context_builder.py` | Write-stage adapter | Builds the compact `SYSTEM_CONTEXT.json` intermediate model (V2-R5 origin) | `SystemContextBuilder` | `utils/sanitizer.py` | `test_v3_r2_r3*` |
| `legacy_documenter/context/resolver.py` | Read-stage adapter | Read-only resolution of `ai_context/*.json`/`index/*.json` into typed packages (`SYSTEM`/`FUNCTIONAL`/`TECHNICAL`/`ENTITY`/`FLOW`/`DATA_ACCESS`) | `ContextResolver` | — | `test_v3_r2_r3*`, `test_v4_2_r4*` |
| `legacy_documenter/context/composer.py` | Read-stage adapter | Applies a token/record budget (`TINY`..`FULL` profiles) to a resolved package | `ContextComposer` | `context/resolver.py` | `test_v3_r2_r3*`, `test_v4_2_r4*` |
| `legacy_documenter/orchestration/ai_interpretation.py` | Orchestration seam | Builds current-run-only context, calls provider, validates output shape/evidence-ref closure | `run_ai_interpretation`, `_resolve_provider`, `_validate_findings` | `context/`, `llm/core.py` | `test_v4_2_r4*` |
| `legacy_documenter/orchestration/proposal_adapter.py` | Orchestration seam | Converts AI findings into `knowledge.proposals.models.Proposal` records | `adapt_findings_to_proposals` | `knowledge/proposals/models.py` | `test_v4_2_r4*` |
| `legacy_documenter/llm/core.py` | Contract/domain model | Provider-neutral request/response/capability contracts; `FakeLLMProvider`; `ProviderRegistry` (currently only wires `FAKE`/`COPILOT`) | `LLMProvider`, `LLMRequest`, `LLMResponse`, `FakeLLMProvider`, `ProviderRegistry` | — | `test_v4_2_r4*`, `_r5_1*` |
| `legacy_documenter/llm/providers/copilot.py` | Adapter | Concrete provider over a local GitHub Copilot client | `CopilotProvider` | `llm/core.py` | `test_v4_2_r4*` (via fakes), guarded from real calls in tests |
| `legacy_documenter/llm/providers/gemini.py` | Adapter (present but unregistered) | Concrete provider over Gemini's HTTP API; reads `GEMINI_API_KEY` | `GeminiProvider` | `llm/core.py` | Not exercised by `tests/__init__.py`'s registry-path tests; see §13 discrepancy |
| `legacy_documenter/knowledge/readiness.py` + `_readiness_evidence.py`, `_readiness_io.py`, `_readiness_parsing.py` | Domain gate / compatibility facade | LegacyMapper's own knowledge-readiness gate (§4.6); `readiness.py` is the sole public/compatibility entry point after V4.1-R4's extraction | `KnowledgeReadinessService`, `run` | `documentation/human_review.py`, `documentation/second_review.py` | `test_v3_r9*`, `test_v4_1_r4*` |
| `legacy_documenter/knowledge/proposals/models.py` / `service.py` (254 lines) | Domain model / service | `Proposal`, `ProposalStatus`, `ProposalKind`, `ProposalMethod`; lifecycle service | — | `orchestration/proposal_adapter.py` | `test_v4_r8*` |
| `legacy_documenter/knowledge/canonical/models.py` / `service.py` (287 lines) | Domain model / service | `CanonicalKnowledgeEntry` (reuses `KnowledgeStatement.validate()`), composition service | — | Not called by `full` | `test_v4_r10*` |
| `legacy_documenter/knowledge/plugin_projection/models.py` / `serializer.py` / `service.py` | Domain model / service | `LegacyMapperPluginKnowledge` contract (`CONTRACT_NAME`/`CONTRACT_VERSION = "1.0"`), `PluginKnowledgeEntry`/`Manifest`/`Payload` | — | Not called by `full` | `test_v4_r12*` |
| `legacy_documenter/quality/maintainability_audit.py` | Tooling/utility | AST-only static maintainability inventory (no import of runtime code) | `audit`, `write_audit` | stdlib `ast` only | `test_v4_1_r0*` |
| `legacy_documenter/utils/atomic_write.py` | Infrastructure | Write-then-rename atomic text writes | `atomic_write_text` | — | Indirect, via every writer |
| `legacy_documenter/utils/json_rendering.py` | Infrastructure | Sorted-key, fixed-separator deterministic JSON rendering | `render_deterministic_json` | — | Indirect |
| `legacy_documenter/utils/sanitizer.py` | Infrastructure/security | Strips secret-shaped values from exported evidence | `sanitize_data` | — | Indirect, via `json_exporter.py`, `system_context_builder.py` |

Grouped, not individually tabulated above (small, cohesive, low-risk): `legacy_documenter/models/*.py` (eight
one-purpose dataclass files, 16–60 lines each); `legacy_documenter/knowledge/*/enums.py` and
`*/contract_report.py`/`*/example_report.py` files across the knowledge sub-packages (contract
documentation/example generators, not runtime logic); `legacy_documenter/documentation/*.py` V3-era
generation/aggregation/consistency helpers beyond `generator.py`/`renderer.py` (self-contained, exercised
only by V3-era tests and not reachable from `full`/`analyze`).

## §9 Execution Architecture

```
sys.argv
  -> legacy_documenter/cli/parser.py: normalize_argv (legacy-form rewrite) -> build_parser (argparse)
  -> legacy_documenter/main.py: main() parses args, calls legacy_documenter/cli/router.py: route(args, analyze_repository)
       command == "analyze" -> _route_analyze -> legacy_documenter.main.analyze_repository
           -> cli/pipeline_stages.py: scan_repository -> extract_repository -> resolve_calls ->
              resolve_web_entries -> resolve_database -> resolve_flows -> resolve_dependencies ->
              export_artifacts -> build_context_artifacts
           -> exits 0 unconditionally (no stage-level result tracking)
       command == "full" -> _route_full -> cli/full_pipeline.py: run_full_pipeline
           -> same stage functions, each wrapped for partial-failure containment (see §10)
           -> cli/pipeline_stages.py: render_documentation (DOCUMENTATION stage)
           -> [opt-in] orchestration/ai_interpretation.py: run_ai_interpretation (AI_INTERPRETATION)
           -> [opt-in] orchestration/proposal_adapter.py: adapt_findings_to_proposals (PROPOSAL_GENERATION)
           -> cli/run_summary_presenter.py: finalize_and_write_run_summary (FINAL_SUMMARY)
           -> exit code from router.py's EXIT_* map, keyed by RunResult.status
       command == "readiness" -> _route_readiness -> knowledge/readiness.py: run()
           -> exit 0/1 keyed by "READY"/"BLOCKED"
```

`analyze` and `full` diverge in exactly one architectural respect: `analyze` calls the shared stage
functions directly with no exception handling of its own (an unexpected failure propagates and aborts the
process — the pre-V4.2 behavior, preserved intentionally); `full` wraps every stage independently
(`cli/full_pipeline.py::_run_stage`/`_skipped`) so a failure is captured as a `StageError` instead of
crashing sibling stages. Both ultimately call the exact same stage implementations in
`cli/pipeline_stages.py` — there is no second, divergent analysis implementation for `full`.

## §10 Full Pipeline

| Stage | Responsibility | Implementation | Input | Output | Failure behavior | Depends on | Tests |
|---|---|---|---|---|---|---|---|
| `SCAN` | Walk repository, classify files | `pipeline_stages.scan_repository` → `scanner/` | Repo root, excludes | `SourceFile` list, stats | `FAILED`; everything downstream skipped | — | `test_v4_2_r2*` |
| `EXTRACTION` | Parse solutions/projects/symbols/webforms/config/calls/data-access | `pipeline_stages.extract_repository` → `extractors/` | Classified files | Solutions/projects/symbols/webforms/calls/data-access/errors | `FAILED`; `CALL_RESOLUTION`/`DATABASE_RESOLUTION`/`DEPENDENCY_RESOLUTION`/`EXPORT`/`CONTEXT`/`DOCUMENTATION` all skipped | `SCAN` | `test_v4_2_r2*` |
| `CALL_RESOLUTION` | Resolve call sites to symbols | `pipeline_stages.resolve_calls` → `analysis/call_resolver.py` | Calls, symbols | Resolved calls, functional dependencies | `FAILED`; `WEB_ENTRY_RESOLUTION`/`FLOW_RESOLUTION` skipped | `EXTRACTION` | `test_v4_2_r2*` |
| `WEB_ENTRY_RESOLUTION` | Resolve UI events to entry points | `pipeline_stages.resolve_web_entries` → `analysis/web_entry_resolver.py` | Webforms, symbols, web events, resolved calls | Entry points, event bindings | `FAILED`; `FLOW_RESOLUTION` skipped | `CALL_RESOLUTION` | `test_v4_2_r2*` |
| `DATABASE_RESOLUTION` | Resolve data-access to stored procs/SQL ops | `pipeline_stages.resolve_database` → `analysis/database_resolver.py` | Data-access indexes, projects | Data access, stored procedures, SQL ops | `FAILED`; `FLOW_RESOLUTION` skipped | `EXTRACTION` | `test_v4_2_r2*` |
| `FLOW_RESOLUTION` | Build functional-flow graphs | `pipeline_stages.resolve_flows` → `analysis/flow_resolver.py` | Entry points, calls, data access, functional deps, `--flow-max-depth` | Functional flows/paths/summary/unresolved | `SKIPPED_DUE_TO_UPSTREAM_FAILURE` if any of the three above failed; otherwise `FAILED` on its own error | `CALL_RESOLUTION`, `WEB_ENTRY_RESOLUTION`, `DATABASE_RESOLUTION` | `test_v4_2_r2*`, `_r7_1*` |
| `DEPENDENCY_RESOLUTION` | Build inter-project dependency graph | `pipeline_stages.resolve_dependencies` → `analysis/dependency_resolver.py` | Solutions, projects, symbols, webforms | Dependency list | `FAILED`; no downstream stage depends on it exclusively | `EXTRACTION` | `test_v4_2_r2*` |
| `EXPORT` | Write `index/*.json` + Markdown | `pipeline_stages.export_artifacts` → `exporters/json_exporter.py`, `markdown_exporter.py` | Assembled `indexes` dict | `output/index/*`, six fixed docs | `FAILED`; run downgraded to `FAILED` overall (§9's status rule) | `EXTRACTION` | `test_v4_2_r2*` |
| `CONTEXT` | Write context artifacts | `pipeline_stages.build_context_artifacts` → `context/` | `indexes` | `output/context/*`, `output/ai_context/*` | `FAILED`; `AI_INTERPRETATION` skipped | `EXTRACTION` | `test_v4_2_r2*` |
| `DOCUMENTATION` | Render four more fixed docs + navigation/partitions | `_run_documentation_stage` → `exporters/technical_documentation_renderer.py` | `indexes` | `documentation/*.md`, `documentation/<doc>/*` | One renderer's failure recorded in `DocumentationOutcome.failures`, others still run; wrapper still reports the stage `FAILED` if any renderer failed | `EXTRACTION` | `test_v4_2_r3*`, `_r8*` |
| `AI_INTERPRETATION` | Opt-in interpretation over current-run evidence | `_run_ai_interpretation_stage` → `orchestration/ai_interpretation.py` | `output/ai_context/*.json` | `AiInterpretationResult` | `NOT_RUN` unless opted in; `SKIPPED_DUE_TO_UPSTREAM_FAILURE` if `CONTEXT` failed; `FAILED` on provider/validation error | `CONTEXT` (only when opted in) | `test_v4_2_r4*` |
| `PROPOSAL_GENERATION` | Convert findings to `Proposal`s | `orchestration/proposal_adapter.py` | `AiInterpretationResult.findings` | `list[Proposal]` | `NOT_RUN` unless opted in; `SKIPPED_DUE_TO_UPSTREAM_FAILURE` if `AI_INTERPRETATION` failed | `AI_INTERPRETATION` (only when opted in) | `test_v4_2_r4*` |
| `FINAL_SUMMARY` | Write `RUN_SUMMARY.{json,md}` | `run_summary_presenter.finalize_and_write_run_summary` | Full stage list + `RunResult` | `RUN_SUMMARY.json`/`.md` | Appended to the stage list; its own outcome factors into the final `RunStatus` | All prior stages | `test_v4_2_r6*` |

`RunResult`/`StageResult`/`RunStatus`/`StageStatus` (`cli/execution_model.py`) are the shared contract: a
`RunResult` carries the command name, overall `RunStatus`, an ordered tuple of `StageResult`s (each a
`StageId` + `StageStatus` + optional `StageError`), and the approval-boundary fields listed in §4.5/§4.12.
Partial/failure containment is implemented entirely in `cli/full_pipeline.py` via `_run_stage` (catches any
exception, converts to `StageError`) and `_skipped` (records which upstream stage(s) blocked this one) —
there is no separate workflow-engine abstraction; it is plain, explicit Python control flow.

## §11 Extraction / Analysis

Deterministic discovery, in dependency order:

1. **Repository scanning** (`scanner/repository_scanner.py`, `file_classifier.py`) — walks the tree,
   classifies each file (`solution`, `project`, `vbnet_source`, `webform_markup`, `webform_codebehind`,
   `webconfig`, etc.) using extension/name heuristics only.
2. **Project/solution discovery** (`extractors/solution_extractor.py`, `vbproj_extractor.py`) — parses
   `.sln`/`.vbproj` structure into `models/project.py` records.
3. **VB.NET symbols** (`extractors/vbnet_extractor.py`) — parses class/method declarations into
   `models/symbol.py`.
4. **WebForms and code-behind** (`extractors/webforms_extractor.py`, `web_event_extractor.py`) — parses
   `.aspx`/`.ascx` markup and UI event bindings.
5. **Calls** (`extractors/call_extractor.py`) — extracts raw call sites; `analysis/call_resolver.py`
   resolves them to declared symbols.
6. **WebForms entry points** (`analysis/web_entry_resolver.py`) — resolves UI events into `confirmed`/
   unresolved entry points. Known gap (F-07): never attaches `outgoing_calls` to a markup-bound entry
   point — an intentionally preserved observation, not silently patched (see §20).
7. **Database access** (`extractors/database_extractor.py` + `_database_classification.py`,
   `_database_line_scanner.py`, `_database_token_parsing.py`; resolved by `analysis/database_resolver.py`)
   — extracts and classifies SQL/data-access evidence, stored procedures, and SQL operations from VB.NET
   source.
8. **Functional-flow resolution** (`analysis/flow_resolver.py` + its three `_flow_*` helpers) — traces
   confirmed method-call paths from entry points through to database/stored-procedure terminals, up to
   `--flow-max-depth`. Status/confidence are worst-case aggregations across every traced path for a flow
   (see the User Manual §4.8 quoted intro text) — a flow can be `unresolved_boundary` overall while still
   having reached a confirmed terminal on one path; both facts are preserved independently.
9. **Dependency resolution** (`analysis/dependency_resolver.py`) — builds the inter-project/inter-symbol
   dependency graph from solutions/projects/symbols/webforms.
10. **Unresolved boundaries and traceability** — every resolver preserves `confirmed` / `inferred` /
    `unresolved` distinctions explicitly (never silently promoted; `AGENTS.md`, "Project Rules"); the
    `UNRESOLVED_FINDINGS.md` document and `flow_unresolved` records are the human-facing surface of this.

What Python establishes deterministically: every fact listed above, plus their confidence/status
(`confirmed`/`inferred`/`unresolved`). What AI may interpret (only when `--allow-ai-interpretation` is
passed): restating/explaining that already-established evidence, citing only evidence-ref ids the current
run itself produced — never adding a new relationship or fact (§4.7, §13).

## §12 Documentation System

`legacy_documenter/exporters/markdown_exporter.py` (`MarkdownExporter`) renders the six original fixed
documents (`PROJECT_OVERVIEW.md`, `SOLUTION_STRUCTURE.md`, `PROJECT_DEPENDENCIES.md`, `WEBFORMS_MAP.md`,
`CONFIGURATION_SUMMARY.md`, `ANALYSIS_WARNINGS.md`).

`legacy_documenter/exporters/technical_documentation_renderer.py` (`TechnicalDocumentationRenderer`)
renders the four V4.2-added documents (`WEB_ENTRY_POINTS.md`, `FUNCTIONAL_FLOWS.md`, `DATABASE_ACCESS.md`,
`UNRESOLVED_FINDINGS.md`). V4.2-R8 added, for the latter three, a `*_navigation()` method (renders the
small fixed-filename summary) and a `*_partitions()` method (renders the same evidence split by semantic
group into `documentation/<doc>/<safe-name>.md`, using `_documentation_partitioning.py::sanitize_label` for
filesystem-safe, path-traversal-proof names, with deterministic numeric-suffix disambiguation for
colliding labels). The original flat `*()` methods are unchanged and still directly tested. Stale partition
files from a previous run's now-obsolete groups are not carried forward: partitioned rendering always
reflects only the current run's groups.

`cli/pipeline_stages.py::render_documentation` writes `documentation/README.md` (a fixed navigation index
linking every document) and applies the "one bad renderer must not destroy the others" policy: each
renderer's failure is recorded in `DocumentationOutcome.failures`, not raised, so one broken document never
prevents the rest from being written; `cli/full_pipeline.py::_run_documentation_stage` inspects that
outcome rather than relying on exception propagation.

Unknown/user-created files inside `documentation/` are preserved across reruns — only the fixed filenames
and partition files the renderer owns are overwritten (§4.10).

**Maintainability measurement (this round).** `PROJECT_STATE.json`'s `maintainability_debt` flags
`technical_documentation_renderer.py` as a `HIGH_RISK_FUTURE_EXTRACTION_CANDIDATE`, citing a historical
V4.2-R8 closure baseline of ~802 lines with the `TechnicalDocumentationRenderer` class itself ~462 lines.
This round measured the file directly: **it is currently 802 lines** (`wc -l`), matching the historical
figure exactly — no drift since V4.2-R8 closure. It remains the single largest production module in the
repository (see §22) and the debt classification stands unchanged; see §20 for the full debt record.

## §13 AI Architecture

**What exists today:**

- A provider-neutral contract (`legacy_documenter/llm/core.py`): `LLMRequest`/`LLMResponse`/
  `LLMCapabilities`/`ProviderConfig`/`Usage`/`ProviderError`, and an abstract `LLMProvider` base
  (`generate`, `capabilities`, `model_info`).
- `FakeLLMProvider` — a deterministic, capability-aware in-memory provider used throughout the test suite
  and by `tools/manual_verify_full_pipeline.py`; it never performs I/O.
- `ProviderRegistry.create(config)` — **currently only recognizes `provider_type in {"FAKE", "COPILOT"}`**;
  passing any other `provider_type` raises `ValueError("unknown provider")`.
- `CopilotProvider` (`llm/providers/copilot.py`) — the one concrete real-provider integration actually
  reachable through the registry, over a local GitHub Copilot client, async under the hood
  (`asyncio.run`).
- `GeminiProvider` (`llm/providers/gemini.py`) — a second concrete provider implementation exists in the
  source tree (reads `GEMINI_API_KEY` via `credential_source`, posts to an HTTP transport) but
  **`ProviderRegistry.create` does not route `"GEMINI"` to it** — it is unreachable from
  `_resolve_provider()`'s production path and not exercised by the test suite's registry-path tests. This
  is a source-vs-completeness discrepancy worth flagging to the Technical Lead (see the result document).
- Context construction: `context/resolver.py` (`ContextResolver`, read-only) +
  `context/composer.py` (`ContextComposer`, applies a `TINY`/`SMALL`/`MEDIUM`/`LARGE`/`FULL` token/record
  budget) — the same read-side machinery both the V3-era `documentation/generator.py` path and the V4.2
  `orchestration/ai_interpretation.py` path use.
- Interpretation: `orchestration/ai_interpretation.py::run_ai_interpretation` — the only AI entry point
  `full` actually calls. Builds a context package exclusively from the current run's own
  `output/ai_context/*.json`, sends a structured-output request under a restrictive system instruction, and
  validates the response shape/evidence-ref closure before ever returning a "SUCCESS" result.
- Proposal generation: `orchestration/proposal_adapter.py::adapt_findings_to_proposals` converts validated
  findings into `knowledge/proposals/models.py::Proposal` records.
- Real-provider safety: production code (`_resolve_provider`) is only ever reached when no `provider` is
  injected; every test and the dedicated `tools/manual_verify_full_pipeline.py` script injects
  `FakeLLMProvider` explicitly. `tests/__init__.py` additionally guards against any test path
  accidentally reaching real provider resolution (`AGENTS.md`).

**Current coupling/limitations:**

- `ai_interpretation.py` does not accept a caller-supplied `ProviderConfig` — provider/model selection in
  production is entirely environment-variable-driven (`LEGACYMAPPER_LLM_PROVIDER`,
  `LEGACYMAPPER_LLM_PROVIDER_ID`, `LEGACYMAPPER_LLM_MODEL`), with `COPILOT` as the hardcoded default.
- There is exactly one AI *purpose* wired end-to-end (`ARCHITECTURE_INTERPRETATION`, hardcoded in
  `run_ai_interpretation`), even though `llm/core.py::PURPOSES` defines seven.
- `documentation/generator.py` (the V3-era path) constructs a `CopilotProvider` directly rather than going
  through `ai_interpretation.py`'s seam — two independent call sites reach a real provider under different
  conditions; a developer must check both when reasoning about "can this ever call a real AI provider".

**V5 requirement (not implemented today):** true AI/provider/model agnosticism — a stable core contract/
port through which any runtime AI backend is swappable, with provider-specific transport/auth/model/retry
detail kept entirely outside core domain logic. `llm/core.py`'s `LLMProvider` ABC is a reasonable seed for
this, but `ProviderRegistry`'s two-provider hardcoded `if`/`elif` and `ai_interpretation.py`'s
single-purpose, environment-variable-only configuration are not yet that. "Python discovers; AI interprets"
must be preserved unchanged by any V5 provider-agnosticism work.

## §14 Knowledge Architecture

Full conceptual pipeline as modeled by `legacy_documenter/knowledge/`:

```
input material (knowledge/input/) -> ingestion (knowledge/ingestion/) -> provenance (knowledge/provenance/)
  -> classification (knowledge/classification/) + temporal separation (knowledge/temporal/)
  -> relations (knowledge/relations/) -> proposals (knowledge/proposals/)
  -> Technical Lead approval (knowledge/approval/) -> canonical knowledge (knowledge/canonical/)
  -> projections: human-readable (knowledge/projection/, R11) / Plugin-facing (knowledge/plugin_projection/, R12)
```

Every stage above domain-models a real, tested contract. What is **not** true today: no CLI command
orchestrates this pipeline end-to-end. The only stage actually wired into `full` is `proposals/` (via
`orchestration/proposal_adapter.py`) — everything from `approval/` onward exists as implemented,
unit-tested library code with no caller in production orchestration.

Key contracts:

- **`CanonicalKnowledgeEntry`** (`knowledge/canonical/models.py`) — immutable, source-neutral entry;
  `knowledge_id` is deterministic (never time/UUID/object-identity derived); requires a non-empty
  `proposal_id` and `approval_decision_id` (both permanent, never erased); reuses
  `KnowledgeStatement.validate()` (R1) rather than re-implementing its evidence-authority rules.
- **KNO identifiers** — `CanonicalKnowledgeEntry.knowledge_id` is the closest concept to a "KNO" identifier
  in the current source; it is produced by a deterministic id-derivation function (`new_knowledge_id`,
  referenced from `canonical/service.py`), not a separate "KNO-" prefixed scheme distinct from
  `knowledge_id` — treat "KNO identifier" and "`knowledge_id`" as the same thing in this codebase.
- **"One canonical source"** — the R10 Canonical Knowledge Source is explicitly modeled as the single
  source of truth for approved knowledge; `plugin_projection`'s `PluginCanonicalSourceDescriptor` declares,
  structurally, that its payload is a *projection of* that source, never a second source of truth
  (`SOURCE_KIND = "CANONICAL_KNOWLEDGE_SOURCE"`, never named `truth`/`source_of_truth`).
- **R11 human projection** (`knowledge/projection/`) — `DocumentProjection`/`ProjectionManifest`, rendered
  to Markdown by `projection/markdown_renderer.py`; projection-layer only, never mutates canonical data.
- **R12 `LegacyMapperPluginKnowledge`** (`knowledge/plugin_projection/models.py`) — `CONTRACT_NAME =
  "LegacyMapperPluginKnowledge"`, `CONTRACT_VERSION = "1.0"`; `PluginKnowledgeEntry.knowledge_id` always
  equals the source `CanonicalKnowledgeEntry.knowledge_id` — no second identity is minted.
- **Plugin runtime** — does **not exist**. `plugin_projection/` produces a payload *shape*; nothing in the
  repository consumes it at runtime. `PROJECT_STATE.json: plugin_runtime = "NOT_IMPLEMENTED"`.

## §15 Contracts and Data Models

| Name | Module | Purpose | Key fields | Producer | Consumer | Stability notes |
|---|---|---|---|---|---|---|
| `RunResult` / `StageResult` / `RunStatus` / `StageStatus` | `cli/execution_model.py` | CLI run/stage outcome | `command`, `status`, `stages`, `ai_invoked`, `canonical_knowledge_produced`, `technical_lead_approval`, `ai_requested`, `proposal_count`, `proposal_review_status`, `next_action`, `output_locations` | `cli/full_pipeline.py`, `cli/router.py` | `run_summary_presenter.py`, tests, CLI console output | Stable, additive-only since V4.2-R2; every V4.2-R5 field defaults safely so older callers see no behavior change |
| `StageId` | `cli/stage_identity.py` | Named pipeline stage vocabulary | 13 enum values | — | `full_pipeline.py`, `RUN_SUMMARY.json` readers | Stable; a full vocabulary is always emitted (`NOT_RUN` rather than omission) |
| `LLMRequest` / `LLMResponse` / `LLMCapabilities` / `ProviderConfig` / `Usage` / `ProviderError` | `llm/core.py` | Provider-neutral AI contract | See §13 | `orchestration/ai_interpretation.py`, `documentation/generator.py` | `llm/providers/*` | Internal/pre-V5; not yet the stable public "port" V5 must design |
| `Proposal` / `ProposalStatus` / `ProposalKind` / `ProposalMethod` | `knowledge/proposals/models.py` | Pre-approval proposal lifecycle | `proposal_id`, `statement`, `rationale`, `evidence_refs`, `status` | `orchestration/proposal_adapter.py` | `full_pipeline.py::_write_proposal_output` | Stable; every V4.2 proposal is `READY_FOR_REVIEW` |
| `CanonicalKnowledgeEntry` | `knowledge/canonical/models.py` | Immutable approved-knowledge entry | `knowledge_id`, `statement`, `source_type`, `nature`, `status`, `proposal_id`, `approval_decision_id`, `evidence_refs`, `provenance` | `knowledge/canonical/service.py` | `knowledge/projection/`, `knowledge/plugin_projection/` | Stable contract, not yet reachable from any orchestrated workflow |
| `KnowledgeStatement` / `EvidenceRef` / `Provenance` | `knowledge/domain/models.py` | Foundational R1 domain model | — | Everywhere in `knowledge/` | `canonical/models.py` (reused, not re-implemented) | Foundational; changing it is a cross-package-breaking change |
| `LegacyMapperPluginKnowledge` payload (`PluginKnowledgeEntry`/`PluginKnowledgeManifest`/`PluginCanonicalSourceDescriptor`/`PluginKnowledgePayload`) | `knowledge/plugin_projection/models.py` | Versioned machine-readable projection for an external Plugin | `CONTRACT_NAME="LegacyMapperPluginKnowledge"`, `CONTRACT_VERSION="1.0"` | `knowledge/plugin_projection/service.py` | No current consumer (no Plugin runtime) | Explicit contract-version constant; a breaking change requires bumping `CONTRACT_VERSION` |
| `SourceFile` / `Project` / `Symbol` / `Call` / `WebForm` / `EntryPoint` / `Dependency` / `Evidence` | `models/*.py` | Cross-module domain records | Small, per-file dataclasses | `extractors/`, `scanner/` | `analysis/`, `exporters/`, `context/` | Stable; widely depended upon, low churn risk |

## §16 Test Architecture

62 test modules under `tests/`, `unittest`-based, discoverable via `python -m unittest discover -s tests`.
Organized chronologically by the round that introduced them, which also groups them by responsibility:

| Group | Files (prefix) | Covers |
|---|---|---|
| V1 baseline | `test_v1*` | Original scanner/extractor/exporter behavior, preserved as regression protection |
| V3 rounds | `test_v3_r1` .. `test_v3_r10_1` | Context/composer, documentation generation/aggregation/consistency, human-review parsing, the R9 readiness gate, R10 maintainability inventory |
| V4 knowledge rounds | `test_v4_r1_knowledge_domain_model` .. `test_v4_r14_manuals_and_final_baseline` | One test module per knowledge sub-package round (R1 domain model through R14 final baseline), plus `test_v4_r13_regression_and_security` |
| V4.1 rounds | `test_v4_1_r0_maintainability_inventory` .. `test_v4_1_r7_exception_boundaries_characterization` | Maintainability inventory, JSON renderer regression, model/type/public-contract characterization, readiness/database-extractor/flow-resolver characterization and gap-closure, exception-boundary characterization |
| V4.2 rounds | `test_v4_2_r1_cli_contract_and_execution_model` .. `test_v4_2_r8_documentation_at_scale` | CLI contract, full-pipeline orchestrator, technical documentation, AI interpretation/proposals, exit codes/real-provider guard, unified CLI/UX, robustness/recovery/security/approval-surface design, real-pilot findings correction, synthetic full-pipeline fixture, documentation-at-scale/final baseline |
| Shared harness | `tests/__init__.py`, `tests/conftest.py`, `tests/fixtures/` | Real-provider-call guard (fails loudly if any test path reaches real provider resolution), shared fixtures, synthetic sample repositories |

Notable groups by kind: **characterization tests** (`*_characterization.py`) pin existing behavior before
refactors, rather than asserting a spec from scratch; **compatibility tests** assert the legacy bare-
positional form and `readiness`'s module entry point remain unchanged; **security/provider-call guard**
tests assert zero real network/provider calls and no secret leakage; **synthetic fixtures**
(`tests/fixtures/v4_2_r7_full_sample/`, exercised by `test_v4_2_r7_synthetic_full_fixture.py`) reproduce the
real V4.2-R7 IST pilot's key findings (F-01, F-07) deterministically without any real IST data; **baseline/
manifest integrity tests** (`test_v4_2_r8_documentation_at_scale.py::FinalBaselineAndManifestIntegrityTests`)
verify `output/v4_2_r8/V4_2_FINAL_BASELINE.json`/`V4_2_FINAL_MANIFEST.json` hash-match the files they claim
to describe.

**Historical account (V4.2 closure)**: the V4.2 closure baseline recorded `"tests": "1809_PASS_0_FAIL_0_SKIP"`
in `PROJECT_STATE.json` and `output/v4_2_r8/V4_2_FINAL_BASELINE.json` — 1809 tests, 0 failures, 0 skips, in
whatever local environment produced that closure result.

**First fresh-checkout run this documentation round observed** (`python -m unittest discover -s tests`, no
test modified before this run):

```
Ran 1625 tests in 66.575s
FAILED (failures=2, errors=19)
```

This was materially different from the historical 1809 figure. A subsequent Post-V4.2 correction round
(`docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION_RESULT.md`) diagnosed and resolved both the
count gap and 20 of the 21 non-passing tests, and a further reconciliation round corrected the last one. The
diagnosis, preserved here for the historical record:

- 19 of the 21 non-passing tests, plus `readiness.py` itself, depended on
  `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`, which `git log --all` showed was **never a tracked file** at
  that point — excluded by `.gitignore` (`/output/v3_r8_1/`, classified as a "heavy regenerable artifact")
  and present only in whatever local environment last produced the 1809-pass baseline. On a fresh clone,
  `readiness()` raised `FileNotFoundError` for that path, and every test calling `readiness()` (directly, via
  the CLI module entry point, or via a "readiness remains green" regression assertion) errored identically.
- `test_v4_2_r5_1_exit_code_contract_and_real_provider_guard.py::test_all_four_externally_observable_exit_codes`
  also called the `readiness` CLI path and failed for the same root cause.
- `test_v4_2_r8_documentation_at_scale.py::FinalBaselineAndManifestIntegrityTests::test_manifest_hashes_match_referenced_files`
  failed because `V4_2_FINAL_MANIFEST.json` recorded a hash for a file under `output/v3_r8_1/` that was
  absent for the same reason.
- The 1625-vs-1809 count gap itself had a separate, structural cause, unrelated to any missing file: when a
  `setUpClass` raises, `unittest` reports exactly **one synthetic `ERROR: setUpClass (...)` entry for the
  whole class** and never counts its individual test methods in `testsRun`. Six classes hit this
  (`test_v3_r7_2.CoveragePlannerTests` (20 methods), `test_v3_r7_2_4.TestV3R724`, `test_v3_r8_2.R82Tests`
  (18), `test_v3_r8_2_correction.CorrectionTests` (20), `test_v3_r9.KnowledgeReadinessTests` (45), and
  `test_v4_1_r4_readiness_characterization.RepresentativeResultTests` (6)), collapsing 184 real test methods
  into 6 counted entries. **No test was deleted and no assertion was weakened** — this was purely
  `unittest`'s own `setUpClass`-failure accounting.

**Correction applied**: (1) `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` (~1.8 KiB) is now a deliberately
tracked, narrow `.gitignore` exception — small aggregate structural-indicator evidence sourced from the
already-tracked `codex/v3/V3_R8_1_DEEP_SOURCE_ANALYSIS_RESULTADO.md`, not a restored raw dump; the rest of
`output/v3_r8_1/` remains excluded. (2) Four historical test classes whose original tests require the full,
un-reconstructable real-repository dumps (`output/v2_r5_1_full/`, the rest of `output/v3_r8_1/`) now carry
`@unittest.skipUnless(...)` guards, so a fresh clone reports an explicit, reasoned `SKIP` per method instead
of one uncontrolled `setUpClass` `ERROR` — this is what lets `unittest` count all 184 individual methods
again. (3) The one remaining manifest-hash failure was root-caused to the verification test comparing the
*live working tree* against a frozen historical snapshot even while a legitimate, still-uncommitted
Post-V4.2 documentation edit was in progress on the same path; the manifest's own two-collection contract
(`authoritative_artifacts` vs. `mutable_current_state_documents`) was already correct, so the test itself was
narrowed to compare `authoritative_artifacts` against their last-*committed* (`git show HEAD:<path>`) content
whenever the working tree currently differs from HEAD, and against disk otherwise — no manifest hash, no
production code, and no historical baseline/manifest file was changed. See
`docs/V4_2/POST_V4_2_DOCUMENTATION_AND_HISTORICAL_MANIFEST_RECONCILIATION_RESULT.md` for the full record.

**Current, corrected fresh-clone expectation**: 1809 tests discovered (matching the historical figure
exactly); 0 failures; 0 errors; 132 skips when the four real-repository-dependent fixture families are
absent (the normal fresh-clone case) — each skip carries an explicit, human-readable reason naming the
missing fixture. **This is not the same thing as the historical "1809 PASS / 0 SKIP"** — it is a deliberate,
documented split between what a bare fresh clone can verify from tracked data alone and what additionally
runs, unchanged and fully assertive, whenever the original local real-repository fixture happens to be
present. No test method was removed and no assertion was weakened to reach this state.

## §17 Tooling

| Tool | Purpose | Mutates state? | Output | Relationship to closure |
|---|---|---|---|---|
| `tools/manual_verify_full_pipeline.py` | Safe manual verification of `full`, including `--allow-ai-interpretation`, always injecting `FakeLLMProvider` | Writes to the `--output` directory the caller supplies | Same shape as a real `full` run | The mandated safe alternative to invoking `python main.py full ... --allow-ai-interpretation` directly (`AGENTS.md`) |
| `tools/v4_2_r8_build_final_artifacts.py` | Builds `output/v4_2_r8/V4_2_FINAL_BASELINE.json`/`V4_2_FINAL_MANIFEST.json` deterministically from current repo-relative paths/hashes | Writes those two files only; reads, never modifies, production code | Candidate baseline/manifest (Technical Lead review still required before formal closure) | Directly produced the artifacts this round measured in §12/§16 |
| `tools/v4_1_r10_build_artifacts.py`, `v4_1_r7_build_artifact.py`, `v4_1_r8_build_artifact.py`, `v4_1_r9_build_artifact.py` | Historical V4.1 round-result artifact builders | Write to their own round's `output/v4_1_r*/` directory | Round-specific JSON | Historical; not re-run in a normal development loop |
| `tools/v4_1_r0/generate.py`, `inventory.py`, `report.py` | Historical V4.1-R0 maintainability inventory tooling | Writes `output/v4_1_r0/*` | Maintainability audit JSON | Predecessor to `legacy_documenter/quality/maintainability_audit.py`, which this manual's §22 uses directly |

None of these tools is imported by `legacy_documenter/`; they are standalone scripts run directly with
`python -m tools.<name>` or `python tools/<name>.py`.

## §18 Continuity / Agent Handover

Bootstrap sequence a new developer or AI development agent actually follows (per `CLAUDE.md`):

1. `AGENTS.md` — autonomy, permission boundary, project rules, phase control.
2. `PROJECT_STATE.json` — the single authoritative pointer to current version/round/status/known
   risks/debt; supersedes any stale round list in `AGENTS.md`'s own memory.
3. `docs/V4/V4_AI_HANDOVER.md` — active handover narrative.
4. `output/v3_final/V3_FINAL_BASELINE.json` — the V3 canonical baseline.
5. The active prompt under `prompts/V4*/` for whatever `next` in `PROJECT_STATE.json` names.

If the repository "does not compile mentally" (a fresh checkout with no session memory), `CLAUDE.md` names
`docs/PROJECT_RECOVERY.md` as the recovery path. A development agent's own conversation memory is never
authoritative — the repository, specifically `PROJECT_STATE.json`, is (`AGENTS.md`: "Current progression is
not duplicated here, to avoid it going stale").

**Starting development from a fresh clone**, concretely:

1. Read `PROJECT_STATE.json` to determine `current_version_status`/`next`.
2. Read this Technical Manual's §6–§9 for the repository/module/execution shape.
3. Run `python -m unittest discover -s tests` and compare the result against §16 — expect 1809 discovered,
   0 failures, 0 errors, 132 skips (all explained), since the fresh-checkout `ARCHITECTURE_EVIDENCE.json` gap
   was corrected; a full-repository fixture placed locally lowers the skip count, never the discovered total.
4. Read the active document named by `PROJECT_STATE.json`'s `next` field before starting any new round —
   never infer the next round from this manual or from memory.

## §19 Generated Artifact Policy

Full authoritative text: `docs/GENERATED_ARTIFACT_POLICY.md`. Summary, verified against the current
`.gitignore`:

- **Canonical small artifacts — versioned.** Anything referenced by path/hash from a baseline, closure
  record, or round result (e.g. `output/v3_final/V3_FINAL_BASELINE.json`, `output/v4_2_r8/*`,
  `output/LEVANTAMIENTO_FUNCIONAL.md`) stays tracked regardless of being generated.
- **Heavy regenerable artifacts — not versioned.** Full-repository scan dumps
  (`output/v1_r1_full/`, `output/v2_r4_full/`, ..., `output/v2_r5_1_full/`, `output/v3_r8_1/`) are
  `.gitignore`-excluded by explicit path; regenerable via `python main.py "<legacy_repo>" --output "<target>"
  --verbose` against a real legacy repository. **Narrow, deliberate exception**:
  `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` (~1.8 KiB) is tracked despite living under an otherwise-excluded
  directory, via a `.gitignore` carve-out (`/output/v3_r8_1/*` plus `!/output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`).
  It holds only small aggregate structural-indicator evidence (four `DETERMINISTIC_INDICATORS` counts and an
  architecture conclusion), sourced verbatim from the already-tracked, human-approved
  `codex/v3/V3_R8_1_DEEP_SOURCE_ANALYSIS_RESULTADO.md` — not a restored raw scan and not independently
  regenerable from the repository alone, since its original values depended on a real legacy scan. The rest
  of `output/v3_r8_1/` (and all of `output/v2_r5_1_full/`) remains fully excluded; no other historical full
  scan dump should be tracked on this precedent (§16, §20).
- **Real-system operational output** — output from analyzing a concrete real legacy system must remain
  local, never committed, regardless of size (`output/v4_2_r7_ist_operacional/`, explicitly excluded).
  Convention for new runs: `output/_local_<name>/` (already covered by a generic `.gitignore` rule) or, if a
  formally named directory is needed, add the matching explicit `.gitignore` rule in the same change.
- **Heavy non-regenerable artifacts** — none currently exist; if one appears, it must be classified and a
  storage mechanism (external archive / GitHub Release / Git LFS / secure storage) chosen before
  `output/` can be considered safe to leave as-is.
- **Why `output/` cannot be globally ignored**: it holds tracked contracts/baselines/manifests alongside
  local generated noise; a blanket ignore would silently drop authoritative history.
- **Safe to delete locally**: anything under the "heavy regenerable" and "smoke-test leftover" lists in
  `.gitignore`/the policy document. **Must remain tracked**: everything else under `output/`, all of
  `docs/`, `prompts/`, `codex/`, `result_codex/`, and obviously all of `legacy_documenter/`/`tests/`.

## §20 Known Technical Debt

| ID | Area | Current status | Affected file(s) | Impact | Why it remains | Suggested future version | Risk if modified | Related tests/evidence |
|---|---|---|---|---|---|---|---|---|
| F-05 | `RUN_SUMMARY.json` lacks a run-duration/timestamp field | `DEFERRED_BY_DETERMINISM_CONTRACT` | `cli/run_summary_presenter.py` | Cannot tell two runs' wall-clock duration apart from the summary alone | Adding wall-clock/UUID content would break the existing determinism invariant (`test_run_summary_json_is_identical_across_two_runs`); no R1–R6 document exempts `RUN_SUMMARY.json` from it | A version that explicitly redefines determinism to exclude a declared "runtime telemetry" field | Silently breaks an existing regression test if added without a contract change | `docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md` §"SECTION 9"; `test_v4_2_r2_deterministic_full_pipeline_orchestrator.py::DeterminismTests` |
| F-06 | `InitializeComponent()` designer boilerplate noise in `UNRESOLVED_FINDINGS.md` | `PRESERVED_OBSERVATION` (not a defect) | `exporters/technical_documentation_renderer.py`, `analysis/flow_resolver.py` | Cosmetic noise for a human reader of unresolved findings | Deliberately not filtered — filtering designer boilerplate risks silently hiding a genuine unresolved case that happens to look similar | Could add an explicit, evidenced "designer-generated" classification rather than filtering by name pattern | Any heuristic filter risks a false negative (hiding a real unresolved boundary) | `tests/test_v4_2_r7_synthetic_full_fixture.py::GeneratedDocumentationTests` |
| F-07 | `WebEntryResolver` never attaches `outgoing_calls` to a markup-bound entry point | `PRESERVED_OBSERVATION` (not a defect) | `analysis/web_entry_resolver.py` | Functional flows starting from a markup-bound handler under-report their own outgoing calls | Fixing requires a resolver-behavior change carrying its own regression risk, deliberately out of scope for a findings-correction round | A round that extends `WebEntryResolver` to resolve markup-bound outgoing calls, with new characterization tests first | Could change flow `status`/`confirmed terminal` results for real repositories | `tests/test_v4_2_r7_synthetic_full_fixture.py::FunctionalFlowTests::test_markup_bound_handler_reproduces_the_known_outgoing_calls_gap` |
| DEBT-DOC-01 | `WEB_ENTRY_POINTS.md` remains a single flat document (no V4.2-R8 partitioning) | `OPEN_IF_FUTURE_SCALE_REQUIRES` | `exporters/technical_documentation_renderer.py::web_entry_points` | Could become unwieldy at a scale similar to what triggered R8's flow/database/unresolved-findings split | Not evidenced as a problem at V4.2-R7 pilot scale; partitioning it preemptively was judged unnecessary work | Apply the same navigation/partition pattern if a future real run shows it necessary | Low if left alone; moderate refactor if added without reusing `_documentation_partitioning.py` | `PROJECT_STATE.json: documentation_remaining_scale_debt` |
| DEBT-DOC-02 | `PROJECT_DEPENDENCIES.md` remains a single flat document | `OPEN_IF_FUTURE_SCALE_REQUIRES` | `exporters/markdown_exporter.py::project_dependencies` | Same as above | Same as above | Same as above | Same as above | `PROJECT_STATE.json: documentation_remaining_scale_debt` |
| MAINT-01 | `technical_documentation_renderer.py` maintainability | `HIGH_RISK_FUTURE_EXTRACTION_CANDIDATE` | `exporters/technical_documentation_renderer.py` (802 lines; `TechnicalDocumentationRenderer` ~462 lines) | Largest production module; mixes four distinct document renderers plus their navigation/partition variants in one class | Extracting per-document renderers now risks breaking the flat/partitioned rendering symmetry (§12) without characterization tests scoped to the split | A dedicated extraction round with characterization tests locking flat-vs-partitioned output equality first | High — the four renderers currently guarantee identical evidence rendering between flat and partitioned output via shared private helpers; a careless split could silently diverge them | `PROJECT_STATE.json: maintainability_debt`; §12 above (line count re-measured this round, unchanged at 802) |
| TESTINFRA-01 | `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` fresh-checkout gap | `RESOLVED` (Post-V4.2 fresh-clone reproducibility correction) | `knowledge/readiness.py::_execute`, `.gitignore`, `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` (now tracked), `test_v3_r9`, `test_v3_r10*`, `test_v4_1_r1..r4`, `test_v4_2_r1/r2/r5_1` | Was: `python main.py readiness` and ~1.2% of the test suite failed on a fresh clone. Now: readiness is `READY`, exit 0, on a fresh clone. | The small, non-sensitive, historically-authentic evidence file is now a deliberate tracked `.gitignore` exception (§19); `readiness.py` itself was not modified | Residual hardening (not implemented): `readiness.py` still assumes the tracked file exists; manual deletion/corruption may still raise uncontrolled rather than a controlled `BLOCKED` | `docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION_RESULT.md`; full suite: 1809 discovered, 0 errors post-correction |
| BASELINE-01 | `V4_2_FINAL_MANIFEST.json` referenced a hash for a file absent on a fresh clone / verification test compared the live working tree against frozen historical evidence | `RESOLVED` (Post-V4.2 documentation and historical manifest reconciliation) | `tests/test_v4_2_r8_documentation_at_scale.py::FinalBaselineAndManifestIntegrityTests::test_manifest_hashes_match_referenced_files` | Was: failed on a fresh clone (ARCHITECTURE_EVIDENCE.json gap), then failed again once a legitimate pending Post-V4.2 manual edit diverged from the frozen closure-time hash on the same path. Now: passes. | Root cause 1 resolved by TESTINFRA-01. Root cause 2: the manifest's own `authoritative_artifacts` vs. `mutable_current_state_documents` contract was already correct and was not modified; the test was narrowed to compare `authoritative_artifacts` against their last-*committed* content (`git show HEAD:<path>`) only when the working tree currently diverges from HEAD, and against disk otherwise, so a legitimate in-progress edit to a manifest-referenced document no longer falsely reads as historical-evidence corruption | No manifest hash, no manifest/baseline file, and no production code was changed | `docs/V4_2/POST_V4_2_DOCUMENTATION_AND_HISTORICAL_MANIFEST_RECONCILIATION_RESULT.md`; `tests/test_v4_2_r8_documentation_at_scale.py` |
| AI-01 | `GeminiProvider` implemented but unreachable via `ProviderRegistry` | **Newly documented this round** — `OPEN` | `llm/providers/gemini.py`, `llm/core.py::ProviderRegistry.create` | A second concrete provider exists in the source tree with no way to select it in production | Not evidenced as intentionally deferred anywhere found in `docs/`/`PROJECT_STATE.json`; appears to be incomplete wiring rather than a deliberate exclusion | Either wire `"GEMINI"` into `ProviderRegistry.create` with test coverage, or explicitly document it as scaffolding for a future round | Low to add (additive `elif` branch); should not be done without provider-specific tests and the "no real provider call" test guard extended to cover it | `llm/core.py::ProviderRegistry.create`; absence from `tests/__init__.py`'s guard-related fixtures |
| R6-01 | `test_deterministic_run_then_ai_enabled_rerun_same_output` intermittency | `NON_REPRODUCIBLE_AS_OF_V4.2_FORMAL_CLOSURE` | Test observed under `test_v4_2_r6_robustness_recovery_security_and_approval_surface.py` | Did not recur through R7, R7.1, R8, or final closure regression runs | Root cause not identified; closure treats non-recurrence as acceptable but not as proof of absence | V5 must treat any recurrence as an investigation trigger, not dismiss it | Ignoring a recurrence would erode confidence in the determinism contract broadly | `PROJECT_STATE.json: known_risks.r6_intermittent_test` |
| APPR-01 | Approval-surface implementation | `NOT_IMPLEMENTED` (design only, `docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md`) | No implementation files — design document only | No CLI path from a proposal to an approval decision exists | Explicitly out of V4.2 scope; approved as `APPROVED_DESIGN_ONLY` | A round scoped to implementing the approval CLI surface against the existing `knowledge/approval/` domain model | Implementing a real approval command is a significant new capability requiring its own security/audit review | `PROJECT_STATE.json: approval_surface_implementation` |
| PLUGIN-01 | Plugin runtime | `NOT_IMPLEMENTED` | No implementation files | No external system can currently consume `LegacyMapperPluginKnowledge` payloads at runtime | Explicitly out of V4.2 scope | A dedicated Plugin-runtime round/version, consuming the already-versioned R12 contract | New attack surface (an external consumer); needs its own security review | `PROJECT_STATE.json: plugin_runtime` |

## §21 Code Audit Map

Suggested audit order, grouped by architectural layer:

1. **CLI/orchestration boundary** — `cli/parser.py`, `router.py`, `execution_model.py`, `stage_identity.py`,
   `pipeline_stages.py`, `full_pipeline.py`, `run_summary_presenter.py`, `artifact_lifecycle.py`.
   Complexity concern: `full_pipeline.py` (490 lines) is the second-largest module in the repository and
   the most structurally central — it wires ten deterministic stages plus two opt-in AI stages plus
   summary finalization. Audit questions: Is `run_full_pipeline` doing orchestration only, or has domain
   logic (e.g. `_assemble_indexes`) crept in alongside pure sequencing? Is the per-stage try/except pattern
   (`_run_stage`) applied uniformly, or does any stage silently bypass it? Known debt: none beyond size.
2. **Deterministic extraction** — `scanner/`, `extractors/`. Complexity concern: `database_extractor.py`
   (358 lines) plus three private `_database_*` helpers is the most decomposed extractor, suggesting the
   others (`call_extractor.py`, 245 lines; monolithic, not yet split into private helpers) could benefit
   from the same treatment. Audit questions: Does `call_extractor.py` mix line-scanning, token-parsing, and
   classification responsibilities the way `database_extractor.py` used to before its `_database_*` split?
   Is deterministic parsing adequately isolated from any analysis-layer inference?
3. **Deterministic analysis/resolution** — `analysis/`. Complexity concern: `flow_resolver.py` (312 lines)
   plus three `_flow_*` helpers is the largest, most graph-algorithmic component; `web_entry_resolver.py`
   carries the known F-07 gap. Audit questions: Is flow-status worst-case aggregation (§11) documented
   clearly enough at the code level, not just in the User Manual? Could `web_entry_resolver.py`'s
   markup-bound `outgoing_calls` gap (F-07) be closed with a bounded, well-tested extension, or does it
   require a broader resolver redesign?
4. **Documentation rendering** — `exporters/`. Complexity concern: `technical_documentation_renderer.py`
   (802 lines, flagged `HIGH_RISK_FUTURE_EXTRACTION_CANDIDATE`, §20 MAINT-01). Audit questions: Could each
   of the four documents' flat+navigation+partition trio be extracted into its own module without breaking
   the shared-helper guarantee that flat and partitioned renderings never drift apart? Is the 802-line size
   itself evidence of "too broad a responsibility," or is it four cohesive, individually-small renderers
   that merely live in one file?
5. **Context/AI seam** — `context/`, `llm/`, `orchestration/`. Complexity concern: two independent
   real-provider call sites (`documentation/generator.py` and `orchestration/ai_interpretation.py`), and an
   unreachable `GeminiProvider` (AI-01). Audit questions: Does provider-specific logic (Copilot's async
   client, Gemini's HTTP transport) leak into `llm/core.py`'s supposedly neutral contract at all? Should
   `ProviderRegistry` be the single production entry point for *every* real-provider call site, retiring
   `documentation/generator.py`'s direct `CopilotProvider` construction?
6. **Knowledge domain** — `knowledge/domain/`, `input/`, `ingestion/`, `provenance/`, `classification/`,
   `temporal/`, `relations/`, `proposals/`, `approval/`, `canonical/`, `projection/`, `plugin_projection/`.
   Complexity concern: not size (most files are well under 300 lines) but *orchestration gap* — many
   well-tested contracts with no production caller. Audit questions: Is each sub-package's test suite a
   genuine characterization of its contract, or does it merely exercise the happy path? Would wiring these
   into an actual approval-surface CLI (APPR-01) surface any latent contract mismatch between adjacent
   sub-packages (e.g. `proposals/` → `approval/` → `canonical/`) that unit tests in isolation would miss?
7. **Readiness/closure tooling** — `knowledge/readiness.py` + `_readiness_*.py`, `knowledge/closure/`,
   `quality/maintainability_audit.py`, `tools/`. Complexity concern: TESTINFRA-01/BASELINE-01 (§20) — a
   hardcoded, untracked-file dependency. Audit questions: Should `readiness.py`'s architecture-evidence
   check be made explicit about its non-reproducibility, or restructured to not require a file with no
   recorded provenance? Is `_execute`'s single large function (readable but doing eight distinct checks
   inline) a case for further decomposition given the `_readiness_*` split already happened once
   (V4.1-R4)?
8. **Governance/continuity** — `AGENTS.md`, `CLAUDE.md`, `PROJECT_STATE.json`, `.gitignore`,
   `docs/GENERATED_ARTIFACT_POLICY.md`. Audit questions: Does every debt item currently `OPEN`/`DEFERRED`
   in `PROJECT_STATE.json` have a corresponding entry in §20 of this manual (cross-check both directions)?
   Is `PROJECT_STATE.json` itself internally consistent with the artifacts it points to (this round found
   one place it is not — TESTINFRA-01/BASELINE-01)?

## §22 Maintainability Inventory

Computed this round via `legacy_documenter.quality.maintainability_audit.audit('.')` (deterministic,
AST-only, imports no runtime code):

- **Production `.py` files**: 169 (under `legacy_documenter/`, excluding `__pycache__`).
- **Classes**: 181. **Functions/methods**: 705. **Symbols total**: 886; **significant symbols** (public, or
  private-but->20-line): 636.
- **Typing coverage** (fully annotated parameters + return): 80.14% of all functions/methods; 77.8% of
  significant functions/methods.
- **Docstring coverage**: 76.52% of all symbols; 93.87% of significant symbols.
- **Large-module candidates** (>250 lines): 10 modules.
- **Multiple-responsibility candidates** (≥4 of `json`/`write_text`/`read_text`/`validate`/`render`/
  `provider`/`security` lexical signals present): 28 modules.

**Largest production modules by line count** (top 15, this round's measurement):

| Lines | Module |
|---|---|
| 802 | `legacy_documenter/exporters/technical_documentation_renderer.py` |
| 490 | `legacy_documenter/cli/full_pipeline.py` |
| 421 | `legacy_documenter/cli/pipeline_stages.py` |
| 358 | `legacy_documenter/extractors/database_extractor.py` |
| 344 | `legacy_documenter/knowledge/canonical/example_report.py` |
| 312 | `legacy_documenter/analysis/flow_resolver.py` |
| 287 | `legacy_documenter/knowledge/canonical/service.py` |
| 263 | `legacy_documenter/documentation/consistency.py` |
| 260 | `legacy_documenter/knowledge/approval/example_report.py` |
| 254 | `legacy_documenter/knowledge/proposals/service.py` |
| 250 | `legacy_documenter/knowledge/plugin_projection/example_report.py` |
| 245 | `legacy_documenter/extractors/call_extractor.py` |
| 239 | `legacy_documenter/knowledge/domain/models.py` |
| 234 | `legacy_documenter/cli/run_summary_presenter.py` |
| 233 | `legacy_documenter/knowledge/relations/service.py` |

Note that three of the ten "large-module candidates" are `*_example_report.py` files (contract-example
generators, not runtime logic) — a reader auditing for genuine complexity should weight the top of this
list (`technical_documentation_renderer.py`, `full_pipeline.py`, `pipeline_stages.py`,
`database_extractor.py`, `flow_resolver.py`) more heavily than the `example_report.py`/`contract_report.py`
files, which are verbose by design (they exist to document a contract with worked examples).

Files already identified by prior rounds as risky/deferred (cross-referenced against §20): only
`technical_documentation_renderer.py` carries an explicit `PROJECT_STATE.json` maintainability-debt flag;
the other large modules above (`full_pipeline.py`, `pipeline_stages.py`, `database_extractor.py`,
`flow_resolver.py`) are large but not currently flagged as debt by any tracked document — a Technical Lead
auditing for the *next* extraction candidate after `technical_documentation_renderer.py` would start there.

No arbitrary quality score is introduced here; the tool itself documents its own limitation: "Line count is
an inventory signal, not a quality verdict" and "Responsibility candidates are lexical prompts for human
review" (`legacy_documenter/quality/maintainability_audit.py::audit`, `limitations` field).

## §23 V5 Handover

**What V4.2 already provides:**

- A working, tested, deterministic analysis pipeline for .NET Framework/VB.NET/ASP.NET Web Forms/Oracle,
  with explicit `confirmed`/`inferred`/`unresolved` evidence tracking throughout.
- A resilient, stage-modeled orchestrator (`RunResult`/`StageResult`/`StageId`) that already generalizes
  well beyond this specific technology stack's stage *names* — the partial-failure containment pattern
  itself is technology-neutral.
- A provider-neutral AI request/response contract (`llm/core.py`) and one production seam
  (`orchestration/ai_interpretation.py`) that already enforces "AI restates, never invents" — a real
  starting point for, not yet an instance of, provider agnosticism.
- A fully modeled (if not yet orchestrated) knowledge pipeline from ingestion through canonical composition
  through both human-readable and machine-readable (Plugin-facing) projection.
- A deterministic maintainability-inventory tool (`quality/maintainability_audit.py`) reusable for any
  future Python-based version of this tool, unmodified.

**What V5 must design:**

- **Language agnosticism** — `extractors/`/`analysis/` are entirely VB.NET/WebForms-specific today; V5
  needs a discovery abstraction that is not simply "the same modules with more `if language ==` branches."
- **Framework agnosticism** — ASP.NET Web Forms concepts (`WebForm`, code-behind, UI event bindings) are
  baked into `models/webform.py`, `extractors/webforms_extractor.py`, `analysis/web_entry_resolver.py`.
- **Database agnosticism** — `extractors/database_extractor.py`'s SQL/stored-procedure classification is
  Oracle-flavored; a generalized data-access model is V5 work.
- **Project-layout agnosticism** — `.sln`/`.vbproj` discovery (`extractors/solution_extractor.py`,
  `vbproj_extractor.py`) assumes a Visual Studio solution/project layout.
- **Runtime AI/provider/model agnosticism** — promote `llm/core.py`'s `LLMProvider` ABC into an actually
  stable, versioned core port; retire the two independent real-provider call sites (`documentation/
  generator.py`'s direct `CopilotProvider` construction and `orchestration/ai_interpretation.py`'s
  `_resolve_provider`) into one; decide `GeminiProvider`'s fate (wire it in or remove it) rather than
  leaving it unreachable (AI-01).
- Preserve "Python discovers; AI interprets" as an invariant through all of the above — agnosticism must
  not become "AI infers what Python used to discover deterministically."
- Runtime AI agnosticism and development-agent neutrality are **related but distinct**: the former is about
  what AI backend `orchestration/ai_interpretation.py` (or its V5 successor) can call at runtime for a
  user's analysis; the latter (already partially addressed — `CLAUDE.md`/`AGENTS.md` are written to be
  agent-neutral) is about which AI coding assistant can develop LegacyMapper itself. Do not conflate a V5
  design decision about one with the other.

**Debt that may be resolved in V5:**

- MAINT-01 (`technical_documentation_renderer.py` extraction) — a language/framework-agnostic rendering
  layer likely requires this split anyway.
- AI-01 (`GeminiProvider` wiring) — naturally resolved by a real provider-agnostic port.
- DEBT-DOC-01/02 (remaining flat documents) — likely revisited alongside any rendering-layer redesign.

**What may be deferred to V5.1/V5.2:**

- APPR-01 (approval-surface implementation) and PLUGIN-01 (Plugin runtime) do not require agnosticism to be
  solved first; either could be implemented against the *current* V4.2 knowledge contracts as a V5.x
  increment, or folded into V5 itself — this manual does not decide that scheduling question.
- TESTINFRA-01/BASELINE-01 (untracked `ARCHITECTURE_EVIDENCE.json` dependency) is not a V5-scale design
  problem; it can and arguably should be fixed independently of any V5 work, once a Technical Lead decides
  whether to commit a synthetic replacement or restructure `readiness.py`'s check.

This manual does not design V5's architecture — it hands off exactly the boundary V5 must cross, grounded
in the current source, for the Technical Lead and the next development agent to plan from.
