# LegacyMapper — Glossary (V4.2)

Definitions reflect actual LegacyMapper semantics as implemented in the current source
(`legacy_documenter/`), not generic dictionary definitions. Cross-reference: User Manual, Technical Manual.

**LegacyMapper** — This project: a tool that deterministically analyzes a legacy .NET Framework/VB.NET/
ASP.NET Web Forms/Oracle repository and produces technical documentation, with an optional, explicit,
restricted AI interpretation pass. See User Manual §4.1.

**Deterministic discovery** — Analysis performed entirely by Python code (scanning, parsing, resolving)
that never calls an AI/LLM provider and always produces the same output for the same input. Everything
under `legacy_documenter/scanner/`, `extractors/`, `analysis/` is deterministic discovery.

**AI interpretation** — The opt-in (`--allow-ai-interpretation`) pass in which a provider is asked to
restate or explain deterministic evidence the current run already discovered. Never allowed to invent a
relationship or fact; every finding must cite evidence-ref ids already present in the current run's own
context package (`legacy_documenter/orchestration/ai_interpretation.py`).

**Evidence** — A discrete, traceable fact discovered deterministically (a symbol, a call, a data-access
record, a resolved entry point). Modeled by `legacy_documenter/models/evidence.py` and referenced by id
(`EvidenceRef`, `legacy_documenter/knowledge/domain/models.py`) throughout the knowledge layer.

**Context** — A composed, budget-limited package of evidence records built for a specific purpose
(`legacy_documenter/context/resolver.py::ContextResolver`, `composer.py::ContextComposer`). Distinct from
the top-level runtime directory `context/`, which is where `ContextBuilder` writes its output at runtime —
same name, two different things (see Technical Manual §6).

**Source** — In the V4 knowledge model, a `SourceType` value (`legacy_documenter/knowledge/domain/
enums.py`) classifying where a piece of material originated (e.g. code, human-authored document). In CLI
usage, "source repository"/"repository" refers to the target codebase being analyzed.

**Provenance** — An explicit, acyclic record of where a piece of material/evidence/statement came from
(`legacy_documenter/knowledge/provenance/`: `ProvenanceGraph`, `ProvenanceNode`). Answers "where did this
come from," never "is this true."

**Proposal** — A pre-approval record stating "given this material/evidence/relation/context, this is a
proposed action or conclusion" (`legacy_documenter/knowledge/proposals/models.py::Proposal`). Every proposal
LegacyMapper produces is `status = READY_FOR_REVIEW` (written as `PENDING_TECHNICAL_LEAD_REVIEW` in the
`full` pipeline's output envelope) — never approved automatically, never canonical.

**Technical Lead** — The human role with sole authority to approve, reject, or request correction of a
proposal (`legacy_documenter/knowledge/approval/models.py::ApprovalDecision`). No CLI command exists in
V4.2 through which a Technical Lead exercises this role — the design exists
(`docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md`), the implementation does not
(`IMPLEMENTATION_STATUS=NOT_IMPLEMENTED`).

**Approval** — An explicit `ApprovalDecision` (`APPROVED` / `REJECTED` / `CORRECTION_REQUESTED`) that a
Technical Lead makes about one specific `Proposal`. Not implemented as a runnable CLI command in V4.2.

**Canonical knowledge** — The single, immutable, source-neutral collection of approved knowledge entries
(the "Canonical Knowledge Source"). Composed only from an approved `Proposal` + `ApprovalDecision(APPROVED)`
pair (`legacy_documenter/knowledge/canonical/service.py`). `RunResult.canonical_knowledge_produced` is
`false` in every V4.2 run, without exception — no run ever produces canonical knowledge today.

**CanonicalKnowledgeEntry** — The immutable dataclass representing one canonical knowledge entry
(`legacy_documenter/knowledge/canonical/models.py`). Requires a permanent `proposal_id` and
`approval_decision_id`; reuses `KnowledgeStatement.validate()`'s structural/evidence rules rather than
re-implementing them.

**KNO / `knowledge_id`** — The deterministic identifier of a `CanonicalKnowledgeEntry`
(`knowledge_id` field). Derived only from immutable semantic content — never from wall-clock time,
randomness, a UUID, or object identity. "KNO identifier" in project shorthand refers to this same field;
there is no separate "KNO-" prefixed identity scheme in the current source.

**R11** — The V4-R10-onward round that produced the human-readable projection layer
(`legacy_documenter/knowledge/projection/`): renders a `CanonicalKnowledgeCollection` into deterministic
Markdown (`DocumentProjection`, `ProjectionManifest`). Projection-layer only; never mutates canonical data.

**R12 / `LegacyMapperPluginKnowledge`** — The versioned, machine-readable projection contract for an
external Plugin consumer (`legacy_documenter/knowledge/plugin_projection/models.py`):
`CONTRACT_NAME = "LegacyMapperPluginKnowledge"`, `CONTRACT_VERSION = "1.0"`. A `PluginKnowledgeEntry`'s
`knowledge_id` always equals its source `CanonicalKnowledgeEntry.knowledge_id` — no second identity is
minted.

**Plugin runtime** — A hypothetical external system that would consume a `LegacyMapperPluginKnowledge`
payload at runtime. Does **not exist** in V4.2 (`PROJECT_STATE.json: plugin_runtime = NOT_IMPLEMENTED`).
The R12 package produces the payload *shape* only; nothing consumes it.

**RunResult** — The outcome of one CLI command invocation (`legacy_documenter/cli/execution_model.py`):
command name, overall `RunStatus`, an ordered tuple of `StageResult`s, and the approval-boundary/UX fields
(`ai_invoked`, `canonical_knowledge_produced`, `technical_lead_approval`, `ai_requested`, `proposal_count`,
`proposal_review_status`, `next_action`, `output_locations`).

**StageResult** — The outcome of one named stage within a run: a `StageId`, a `StageStatus`, and an
optional `StageError` (`legacy_documenter/cli/execution_model.py`).

**RunStatus** — Overall run outcome: `SUCCESS`, `PARTIAL`, or `FAILED`. Computed non-subjectively by
`legacy_documenter/cli/full_pipeline.py::_compute_status` — see **SUCCESS**/**PARTIAL**/**FAILED** below.

**StageStatus** — Per-stage outcome: `SUCCESS`, `FAILED`, `SKIPPED_DUE_TO_UPSTREAM_FAILURE`, or `NOT_RUN`
(the last reserved for a stage that was never requested, e.g. `AI_INTERPRETATION` without
`--allow-ai-interpretation`).

**SUCCESS** (exit code `0`) — `analyze` always exits `0`. For `full`/`readiness`, every applicable stage
succeeded with no per-file extraction error.

**PARTIAL** (exit code `1`) — `full`/`readiness` completed with at least a minimally useful result
(`EXTRACTION` and `EXPORT` both succeeded, for `full`) but some stage failed, was skipped due to an
upstream failure, or a per-file extraction error was recorded.

**FAILED** (exit code `4`) — `full` did not produce even a minimally useful deterministic analysis package
(`EXTRACTION` or `EXPORT` did not succeed).

**USAGE** (exit code `2`) — An argparse-level usage error (unknown command, missing required argument),
never assigned by application code.

**READY** — The outcome of `python main.py readiness` (or `readiness.py::run()`) when every one of its
eight internal checks (`preconditions`, `claim_integrity`, `evidence_closure`, `quantitative_integrity`,
`architecture_integrity`, `knowledge_projection`, `knowledge_boundary`, `security`) passes. The opposite is
`BLOCKED`. This is a self-check of LegacyMapper's own V3-era approved documentation/evidence, not a
per-target-repository readiness signal.

**`ARCHITECTURE_EVIDENCE.json`** (`output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`) — A small (~1.8 KiB), narrowly
tracked `.gitignore` exception consumed by `readiness.py::architecture_valid()` as part of the
`architecture_integrity` check. Holds only four aggregate `DETERMINISTIC_INDICATORS` structural counts (no
source code, source paths, credentials, or PII), sourced verbatim from the already-tracked, human-approved
`codex/v3/V3_R8_1_DEEP_SOURCE_ANALYSIS_RESULTADO.md`. It is **contract evidence**, not a restored raw scan
dump — the rest of `output/v3_r8_1/` remains excluded — and it cannot be regenerated from the repository
alone, since its original values depended on a real legacy-repository scan.

**Historical closure artifact vs. mutable current-state document** — A distinction the V4.2 manifest
(`output/v4_2_r8/V4_2_FINAL_MANIFEST.json`) makes explicitly via two separate collections:
`authoritative_artifacts` (already-produced, already-reviewed evidence for the V4.2 candidate/closure state;
its recorded hashes are integrity requirements, verified against each file's last-*committed* content) and
`mutable_current_state_documents` (documents the manifest's own note says "intentionally change as the
project advances"; their recorded hashes are a point-in-time snapshot only, not an integrity requirement). A
file referenced as an authoritative artifact may still receive legitimate new edits after closure — the
historical manifest hash describes what was true at closure time, not a promise that the live path can never
be touched again.

**CODE_ONLY / CODE_AND_HUMAN_INFORMATION / HUMAN_INFORMATION_ONLY / PARTIAL_INFORMATION** — Source-type/
information-composition categories used in the V3-era knowledge-readiness and documentation layers
(`legacy_documenter/documentation/`, `knowledge/readiness.py`) to describe whether a claim rests on
deterministic code evidence alone, on human-supplied information alone, on a combination, or on an
incomplete mixture. Distinct from, and predating, the V4 `SourceType`/`KnowledgeNature` enums.

**AS_IS / TO_BE / HISTORICAL / GAP** — The four temporal buckets of `legacy_documenter/knowledge/temporal/`
(V4-R6): `AS_IS` (current confirmed state), `TO_BE` (a stated future/target state), `HISTORICAL` (a past
state no longer current), `GAP` (an identified difference/absence between buckets). Assigned to already-
ingested material; never inferred beyond what the material states.

**Unresolved boundary** — A point in analysis where deterministic evidence does not close to a confirmed
conclusion (e.g. a call that cannot be resolved to a declared symbol, a flow that cannot reach a confirmed
terminal). Always preserved explicitly, never silently dropped or upgraded to `confirmed`
(`UNRESOLVED_FINDINGS.md`; `flow_unresolved` records; `AGENTS.md` "Project Rules").

**Confirmed terminal** — In functional-flow resolution (`legacy_documenter/analysis/flow_resolver.py`), a
traced execution path that reaches a database/stored-procedure operation with `confirmed` evidence. A flow
can have a confirmed terminal on one path while its overall `Status` still reads `unresolved_boundary`
because of a different, unrelated unresolved path — both facts are recorded independently (User Manual
§4.8).

**Operational output** — The generated result of running LegacyMapper against a concrete, real legacy
system (a pilot, a client engagement). Must remain local, never committed, regardless of size
(`docs/GENERATED_ARTIFACT_POLICY.md`, "Real-System Operational Output").

**Tracked artifact** — A small, meaningful, generated file that a baseline/closure/round-result document
references by path or hash, and which therefore stays versioned in Git despite being generated (e.g.
`output/v4_2_r8/V4_2_FINAL_BASELINE.json`).

**Synthetic fixture** — A committable, hand-constructed (or pilot-derived-but-anonymized) sample repository
or dataset used by tests to reproduce a real-world finding deterministically without any real/sensitive
data (`tests/fixtures/v4_2_r7_full_sample/`, reproducing V4.2-R7 pilot findings F-01/F-07).

**Baseline** — A frozen, point-in-time snapshot of repository state (test counts, hashes, capability list)
recorded at a closure milestone (e.g. `output/v4_2_r8/V4_2_FINAL_BASELINE.json`). Not expected to match a
later live run byte-for-byte once the repository has legitimately moved on — see the Technical Manual §16
for a concrete case where a fresh-clone run and the recorded baseline diverge.

**Manifest** — A companion file to a baseline recording file paths and content hashes, used to verify the
baseline's referenced artifacts are byte-identical to what closure recorded
(`output/v4_2_r8/V4_2_FINAL_MANIFEST.json`).

**Agent-neutral continuity** — The property that `AGENTS.md`/`CLAUDE.md`/`PROJECT_STATE.json` are written
so that any capable AI development agent (not only one specific product) can pick up the project correctly
by reading the repository itself, never a specific agent's session memory (`AGENTS.md`: "the active
development agent," "any capable development agent").

**Provider (LLM provider)** — A concrete implementation of `legacy_documenter/llm/core.py::LLMProvider`
(e.g. `FakeLLMProvider`, `CopilotProvider`). `ProviderRegistry.create` currently wires only `"FAKE"` and
`"COPILOT"` — see Technical Manual §13, discrepancy AI-01.

**FakeLLMProvider** — A deterministic, in-memory, capability-aware `LLMProvider` implementation used
throughout the test suite and by `tools/manual_verify_full_pipeline.py` so no test or manual verification
ever reaches a real network/provider call.

**Findings** — The list of statements an AI interpretation pass returns, each with a `confidence`
(`CONFIRMED`/`UNCERTAIN`) and `evidence_refs`. Untrusted, unapproved, non-canonical until (and unless) a
Technical Lead later approves a `Proposal` built from them.
