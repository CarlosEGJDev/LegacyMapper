# V4_2_R4_AI_INTERPRETATION_AND_PROPOSAL_INTEGRATION — Result

TASK=V4_2_R4_AI_INTERPRETATION_AND_PROPOSAL_INTEGRATION

MODE=CONTROLLED_IMPLEMENTATION

---

## STATUS

STATUS=V4_2_R4_AI_INTERPRETATION_AND_PROPOSAL_INTEGRATION_COMPLETE

---

## BASELINE

V4.2-R0 through R3 reviewed and approved by the Technical Lead, per task authority. Entering baseline: `1650_PASS_0_FAIL_0_SKIP`. V4.1 remains `FORMALLY_CLOSED`. `REAL_AI_RUNTIME_CALL_ALLOWED=false` was respected throughout: every test uses `legacy_documenter.llm.core.FakeLLMProvider` or a deliberately broken subclass — no `CopilotProvider`/`GeminiProvider` is imported anywhere in this round's code or tests, and no real network/provider call was ever attempted.

---

## FILES_CREATED

- `legacy_documenter/orchestration/__init__.py` — package marker, documents why AI integration is deliberately separate from `legacy_documenter/cli/`.
- `legacy_documenter/orchestration/ai_interpretation.py` — `run_ai_interpretation()`, builds a context package from the CURRENT run's own `ai_context/*.json`, calls a provider through the existing `ProviderRegistry` boundary, validates the response against a small closed schema.
- `legacy_documenter/orchestration/proposal_adapter.py` — `adapt_findings_to_proposals()`, converts validated findings into real `knowledge/proposals` `Proposal` records using the existing, unmodified `ProposalService`.
- `tests/test_v4_2_r4_ai_interpretation_and_proposal_integration.py` — 34 new focused tests.
- `docs/V4_2/V4_2_R4_AI_INTERPRETATION_AND_PROPOSAL_INTEGRATION_RESULT.md` (this file)

## FILES_MODIFIED

- `legacy_documenter/cli/parser.py` — added `--allow-ai-interpretation` to the `full` subparser only (not `analyze`); corrected `full`'s stale R1-era help text ("Not implemented in R1... placeholder") left over from before R2/R3 made it real.
- `legacy_documenter/cli/router.py` — `_route_full` now reads `args.allow_ai_interpretation` (defaulting to `False` via `getattr` since `analyze` never has this attribute) and threads it into `run_full_pipeline`. No AI logic added — only the flag is read and forwarded.
- `legacy_documenter/cli/full_pipeline.py` — added the AI_INTERPRETATION and PROPOSAL_GENERATION stages (opt-in only), `_run_ai_interpretation_stage`, `_write_proposal_output`, `_proposal_to_dict`, `_render_proposal_markdown`; `run_full_pipeline` gained `allow_ai_interpretation` and `ai_provider` parameters; `RunResult.ai_invoked` is now set from whether the provider was actually reached. Module docstring updated for the new 13-stage sequence. **No AI/proposal domain logic was added here** — every call is a single line into `orchestration.ai_interpretation`/`orchestration.proposal_adapter`, mirroring exactly how this file already calls into `pipeline_stages` for the deterministic stages (see AI_INTEGRATION_ARCHITECTURE below).
- `legacy_documenter/cli/stage_identity.py` — module docstring updated: all thirteen stages are now described accurately (nine deterministic + DOCUMENTATION always run; AI_INTERPRETATION/PROPOSAL_GENERATION run only on opt-in, otherwise `NOT_RUN`; FINAL_SUMMARY always last).
- `legacy_documenter/cli/execution_model.py` — unchanged in this round (its `ai_invoked` field, added in R2, is what this round finally sets meaningfully).
- `tests/test_v4_2_r1_cli_contract_and_execution_model.py`, `tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py` — both had a "forbidden capability" check that correctly forbade `full_pipeline.py` from referencing `llm`/`knowledge.proposals` in R1–R3 (when that was true). Updated to reflect R4's real, opt-in AI wiring: `pipeline_stages.py` remains fully forbidden from all AI/knowledge capability (unchanged, still enforced), and `full_pipeline.py` is now checked against the *still*-forbidden set only (`deep_interpretation`, `knowledge.approval`, `knowledge.canonical`, `knowledge.projection`, `knowledge.plugin_projection`, `knowledge.ingestion`) — `llm`/`knowledge.proposals` are no longer forbidden there because R4 legitimately, deliberately wires them in behind the opt-in flag. R2's stage-order test (`EXPECTED_STAGE_ORDER`) and its "every stage SUCCESS" assertion were extended for the two new stages, correctly asserting `NOT_RUN` for them since that test never opts in.
- `tests/test_v4_1_r0_maintainability_inventory.py` — extended for the new orchestration package and its knock-on effects (see MAINTAINABILITY_INVENTORY_UPDATE-equivalent detail folded into TESTS below). No V4.1 historical artifact was touched.

---

## AI_INTEGRATION_ARCHITECTURE

**Key architecture decision, made only after characterizing the existing code (per section 5's explicit instruction) — documented here in full because it deviates from a literal reading of "execute the existing interpretation capability":**

`legacy_documenter/analysis/deep_interpretation.py::run_deep_interpretation` was **not** reused as the AI_INTERPRETATION stage's implementation. Characterization showed it is a V3-R8-specific tool: it reads evidence exclusively from a hardcoded `output/v3_r8_1` directory shape (`DEEP_ANALYSIS_SUMMARY.json`, `ARCHITECTURE_EVIDENCE.json`, etc.) and interprets against eight hardcoded target ids (`FMI-001`, ...). Calling it here would mean the AI_INTERPRETATION stage reads a **historical, unrelated snapshot** as its input — exactly what section 7's context-boundary requirement explicitly forbids ("must not silently read... another historical snapshot as its interpretation input").

Instead, `orchestration/ai_interpretation.py` builds its own small context package from **the current run's own** `<output_dir>/ai_context/*.json` — the same files the CONTEXT stage (R2) writes moments earlier in the same `full` invocation — via the existing, path-agnostic `ContextResolver`/`ContextComposer` (`legacy_documenter/context/`), which were confirmed by characterization to take an explicit `root` parameter and hardcode nothing themselves. It reuses `deep_interpretation.py`'s **provider-selection pattern** (`ProviderConfig` + `ProviderRegistry().create()`, no hardcoded provider class) and its **validation discipline** (reject malformed/unauthorized-evidence output rather than silently accepting it), without reusing its V3-specific evidence-gathering code. This is a deliberate, narrower reuse: the *pattern*, not the *function*.

`documentation/generator.py` was **not** touched or imported anywhere (see DOCUMENTATION_GENERATOR_DECISION below) — it solves a different problem (AI-driven full documentation generation from a historical V2 snapshot) than R4's actual need (opt-in interpretation of the current run's own evidence, adapted into a proposal).

Responsibility separation, per section 19's explicit instruction:
- **`legacy_documenter/orchestration/ai_interpretation.py`** — builds the context package, calls the provider, validates the response. No file writing, no `Proposal` construction.
- **`legacy_documenter/orchestration/proposal_adapter.py`** — converts validated findings into `Proposal` records via the existing, unmodified `ProposalService`. No provider calls, no file writing.
- **`legacy_documenter/cli/full_pipeline.py`** — orchestrates *calling* the above two modules (one line each, wrapped in a `_run_stage`-style helper) and writes the small proposal envelope, mirroring exactly how it already writes `RUN_SUMMARY.json` (`_write_run_summary`) for FINAL_SUMMARY. It contains zero AI/proposal domain logic — every actual AI/proposal decision lives in `orchestration/`.
- **`legacy_documenter/cli/pipeline_stages.py`** — untouched. Per section 19's explicit exclusion, no AI logic was added here; it remains the deterministic-only module `analyze` also depends on.

---

## CLI_AI_OPT_IN

```
python main.py full <repository> --output <directory> [--allow-ai-interpretation]
```

`--allow-ai-interpretation` (`store_true`, default `False`) is added **only** to the `full` subparser — `analyze` never gained this option, since `analyze` remains deterministic-only by definition. Without the flag, `full` behaves exactly as R2/R3 left it: `AI_INTERPRETATION`/`PROPOSAL_GENERATION` are `NOT_RUN` and no environment variable alone can enable AI (`LEGACYMAPPER_LLM_PROVIDER` etc. are only ever read *inside* `orchestration.ai_interpretation._resolve_provider()`, which is only called once `allow_ai_interpretation=True` and `provider=None`) — verified with a test that patches `_resolve_provider` to raise if called, confirming it is never invoked without the flag. `python main.py full --help` documents the flag; verified manually and via a subprocess test.

---

## CONTEXT_BOUNDARY

AI interpretation consumes **only** `<output_dir>/ai_context/*.json` — `output_dir` being the exact `--output` directory this same `full` invocation is writing to. Verified concretely: `ContextResolver(output_dir)` requires those files to exist (raises `FileNotFoundError` otherwise, caught and reported as `CONTEXT_UNAVAILABLE`); a run against a *different*, empty output directory fails closed even when a fully-populated run exists elsewhere, proving no path-guessing or fallback to another location occurs. `AI_INTERPRETATION`'s real prerequisite in the stage graph is `CONTEXT` succeeding (not just `EXTRACTION`), since it literally cannot run without CONTEXT's output — derived from source, not assumed. `output/v2_r5_1_full/`, `output/v3_*`, and `codex/V3/` are never referenced anywhere in `orchestration/ai_interpretation.py`'s code (only named in its docstrings, explaining what it must *not* do).

---

## AI_INTERPRETATION_STAGE

`StageId.AI_INTERPRETATION` (declared in R1) now executes only when `allow_ai_interpretation=True` **and** `CONTEXT` succeeded. Per section 8's explicit choice point ("absent from the scheduled stage list or NOT_RUN — document the choice"): **`NOT_RUN` was chosen**, not omission. `RUN_SUMMARY.json` always lists all thirteen stages; when AI wasn't requested, `AI_INTERPRETATION`/`PROPOSAL_GENERATION` show `"status":"NOT_RUN"` rather than being absent — this is more informative for a script or human reading the summary (it can always distinguish "this capability exists and wasn't used" from "this LegacyMapper version doesn't have this capability yet"), and it is the first real use of the `StageStatus.NOT_RUN` value R1 defined but never exercised. `_compute_status` already excluded `NOT_RUN` from its "trouble" check by construction (it only checks `{FAILED, SKIPPED_DUE_TO_UPSTREAM_FAILURE}`), so no change to that function was needed — a default `full` run's status is unaffected by the two new always-present `NOT_RUN` entries.

---

## PROPOSAL_ADAPTER

`orchestration/proposal_adapter.py::adapt_findings_to_proposals` uses the **existing, completely unmodified** `knowledge/proposals` domain: `ProposalRequest` → `ProposalService.create_proposal()` → `transition_proposal(..., ProposalStatus.READY_FOR_REVIEW)`. No second proposal model was invented. Preserved per finding, exactly as required:

- **AI origin / method**: `proposal_method=ProposalMethod.AI_PROPOSED` (verified by test).
- **Proposal kind**: `ProposalKind.INTERPRETATION` (an AI interpretation is exactly that kind, not a resolution/correction/etc.).
- **Evidence references**: `evidence_refs` carries the finding's own validated evidence ref ids (verified traceable back to the context package's `records`).
- **Status/uncertainty**: created at `DRAFT`, then transitioned to `READY_FOR_REVIEW` using the *existing* `transition_proposal` lifecycle function (not a new concept) — a purely structural "complete enough to show the Technical Lead" transition, confirmed by reading `knowledge/proposals/models.py`'s own documentation of that function: never an approval. `ProposalStatus` has no `APPROVED`/`REJECTED`/`CORRECTED` member at all (verified) — those genuinely cannot be produced by this code.

---

## PROPOSAL_GENERATION_STAGE

`StageId.PROPOSAL_GENERATION` executes only when `AI_INTERPRETATION` reported `SUCCESS`. If AI interpretation failed (any reason), `PROPOSAL_GENERATION` is `SKIPPED_DUE_TO_UPSTREAM_FAILURE` naming `AI_INTERPRETATION` as the blocking stage — verified with tests for both a provider failure and a malformed-output failure. If AI was never requested, `PROPOSAL_GENERATION` is `NOT_RUN`, matching `AI_INTERPRETATION`. No fallback/invented proposal is ever generated on failure — verified: a `run_full_pipeline` call with a malformed-output provider produces zero proposals and no `proposals/` directory content beyond the envelope recording the failure.

---

## PROPOSAL_OUTPUT

Persisted under `<output_dir>/proposals/` — deliberately separate from `output/index/` (deterministic-only), per section 12's explicit instruction:

- **`proposals/AI_PROPOSALS.json`** — authoritative, deterministic envelope (`render_deterministic_json`, the same sorted-keys/compact-separators helper the rest of V4.2 already shares). Top-level `status` field is exactly `"PENDING_TECHNICAL_LEAD_REVIEW"` when proposals exist, `"NO_PROPOSALS_GENERATED"` otherwise — stated explicitly, never implied.
- **`proposals/AI_PROPOSALS_PENDING_REVIEW.md`** — small human-readable listing (pure formatting over the same envelope, no separate logic), ending with an explicit non-approval disclaimer.

Both files are written **only** when `--allow-ai-interpretation` was passed (`_write_proposal_output` is a no-op when `ai_result is None`) — `analyze` never calls this function at all, so its output tree is completely unaffected, verified explicitly.

**A real bug was found and fixed while building this**: `dataclasses.asdict(proposal)` alone left `proposal_kind`/`proposal_method`/`status` as live `(str, Enum)` instances. `json.dumps` happens to render those correctly (str subclasses take JSON's string fast path), but the Markdown f-string renderer did not — Python's `Enum.__str__` prints `"ProposalKind.INTERPRETATION"`, not the plain value. Fixed with a small `_proposal_to_dict` helper that normalizes to `.value` once, shared by both the JSON and Markdown writers — caught by manual verification before it reached the test suite, and now covered by `test_proposal_envelope_uses_plain_string_enum_values_not_repr`.

---

## APPROVAL_BOUNDARY

R4's hard requirement is met unconditionally, opt-in or not: no code path anywhere in `orchestration/` or the R4 additions to `full_pipeline.py` imports or calls `knowledge/approval`, `knowledge/canonical`, `knowledge/projection`, `knowledge/plugin_projection`, `knowledge/ingestion`, `ApprovalDecisionType`, or `ApprovalAuthority` — verified by three separate source-scanning tests (on the orchestration package, on `full_pipeline.py`, and on `pipeline_stages.py`, the last of which additionally forbids `llm`/`knowledge.proposals` entirely since it must remain deterministic-only forever). No Technical Lead identity is ever manufactured. `TECHNICAL_LEAD_APPROVAL` and `CANONICAL_KNOWLEDGE_PRODUCED` remain hard-coded `False` on `RunResult` (unchanged defaults from R2) and are asserted `False` even in a fully successful AI-enabled run.

---

## RUN_RESULT_BEHAVIOR

`ai_invoked` is computed from `AiInterpretationResult.provider_called`, **not** from whether `--allow-ai-interpretation` was passed:

- Default `full` (no flag): `ai_invoked=False` (verified).
- `--allow-ai-interpretation` passed, but `CONTEXT` failed first: AI_INTERPRETATION is `SKIPPED_DUE_TO_UPSTREAM_FAILURE`, the provider is never resolved or called, `ai_invoked=False`.
- `--allow-ai-interpretation` passed, `CONTEXT` succeeded, provider actually called (success or failure): `ai_invoked=True` in both cases — including a provider exception (verified with `test_provider_exception_is_caught_not_propagated`, which still asserts `ai_invoked` reflects the attempt correctly via the stage status, since `provider_called=True` is set the moment a request reaches `structured_generate`).

`canonical_knowledge_produced`/`technical_lead_approval` remain `False` in every scenario tested, including a fully successful AI-enabled run with real proposals generated.

---

## AI_FAILURE_POLICY

Implemented and verified exactly as specified: deterministic pipeline `SUCCESS` + AI interpretation `FAILED` → overall `RunStatus.PARTIAL`, never `FAILED` (verified explicitly, with an assertion that status is *not* `FAILED`). All deterministic documents and `index/*.json` remain available after an AI failure (verified: `index/repository.json`, `documentation/PROJECT_OVERVIEW.md`, `documentation/WEB_ENTRY_POINTS.md` all still present). A raw provider exception (e.g. a simulated `ConnectionError`) is caught inside `orchestration.ai_interpretation.run_ai_interpretation` itself and converted to a structured `AiInterpretationResult(status="PROVIDER_ERROR", ...)` — it never propagates as a Python exception out of the stage, and `FINAL_SUMMARY` still runs and writes a complete record of what happened.

---

## SECURITY

No credential, token, or authorization header is ever written to `RunResult`, `StageError`, the proposal artifacts, or logs. `_sanitize_provider_error` reduces any provider exception/error to its first line, truncated to 300 characters — verified with a test injecting a provider error containing both a fake token string and a multi-line simulated traceback, asserting the resulting message contains no `"Traceback"` text and stays within the length bound. No `os.environ` dump appears anywhere in the proposal output (verified). Malformed AI output is never silently repaired — every validation failure in `_validate_findings` is a hard rejection (empty findings list, no proposal) with a structured, specific error code (`missing_statement`, `unknown_evidence_refs:...`, etc.), never a best-effort guess at what the AI "probably meant."

---

## DETERMINISM_BOUNDARY

Documented explicitly, as required: AI text content itself is **not** claimed to be deterministic (a real provider's output varies call to call) — R4 makes no such claim anywhere. What **is** deterministic, and verified by test:

- The nine deterministic analysis stages and DOCUMENTATION (unchanged from R2/R3).
- `proposals/AI_PROPOSALS.json`'s serialization, given the *same* validated AI result: two separate `run_full_pipeline` calls with two independently-constructed `FakeLLMProvider` instances returning the identical structured response produce byte-identical `AI_PROPOSALS.json` content (verified) — because `Proposal.proposal_id` is itself content-hash-derived (`stable_id`, no timestamp/UUID) and `render_deterministic_json` sorts keys with fixed separators.
- A default (non-AI) `full` run's `RUN_SUMMARY.json` remains byte-identical across repeated runs (verified) — R4 introduces no new non-determinism into the deterministic path.

---

## DOCUMENTATION_GENERATOR_DECISION

**Decision: B. NOT_REQUIRED_FOR_R4.** `documentation/generator.py` was not modified, reused, or imported anywhere in this round. Reasoning: R4's actual need — opt-in interpretation of the *current* run's own evidence, adapted into a `Proposal` — is structurally different from what `generator.py` does (AI-driven generation of full documentation text from a hardcoded historical `output/v2_r5_1_full/` snapshot, using a directly-instantiated `CopilotProvider`). Characterization confirmed both of its R0-identified defects (the hardcoded path and the direct-provider coupling) are entangled inside its single `run()` function with no parameter to override either independently — reusing it would require fixing both defects regardless of R4's actual scope, which is exactly the "do not refactor unrelated V3 documentation infrastructure" the task warns against. Its cleanup remains deferred to a future, explicitly-scoped round, as it was after R0.

---

## TESTS

New: `tests/test_v4_2_r4_ai_interpretation_and_proposal_integration.py` — 34 tests covering: zero provider calls by default; provider called only after explicit opt-in; current-run-only context (including a real fail-closed proof against an empty second output directory); successful fake interpretation → Proposal with AI origin/method preserved and status never beyond `READY_FOR_REVIEW`; deterministic proposal-envelope serialization; malformed output (missing key, non-list findings, unknown/hallucinated evidence ref) → structured failure, never a proposal; provider failure (forced status and raised exception) → `AI_INTERPRETATION FAILED` → `PROPOSAL_GENERATION SKIPPED_DUE_TO_UPSTREAM_FAILURE` → overall `PARTIAL` with deterministic artifacts intact; no canonical knowledge/approval/R11/R12/Plugin runtime ever, opt-in or not; no credentials/env dumps in output; source immutability; `analyze`/legacy compatibility; `full` without the flag remains deterministic; CLI help documents the flag.

One test-design mistake was caught and fixed, not hidden: an initial textual "forbidden path string" scan flagged the module's own docstring, which legitimately *names* `output/v2_r5_1_full`/`output/v3_r8`/`codex/V3` in prose while explaining the constraint it satisfies (exactly the "document this boundary" requirement) — a textual grep cannot distinguish "documents the prohibition" from "violates it." Replaced with a stronger *behavioral* proof instead (a second, freshly-empty output directory must still fail closed even though a fully-populated run exists elsewhere), which is what actually demonstrates the property.

Modified: `tests/test_v4_2_r1_cli_contract_and_execution_model.py`, `tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py` (both had forbidden-capability checks correctly loosened for `full_pipeline.py` only, per AI_INTEGRATION_ARCHITECTURE above — `pipeline_stages.py`'s check is unchanged and still fully enforced), and `tests/test_v4_1_r0_maintainability_inventory.py` (extended, not weakened — every number recomputed empirically via `tools.v4_1_r0.report.build_inventory`, including two more knock-on ranking/heuristic effects: `full_pipeline.py` grew enough in R4 to cross from HIGH into VERY_HIGH — exactly offsetting V4.1-R4's earlier `readiness.py` VERY_HIGH→HIGH move, a coincidence documented as such, not glossed over — and `ai_interpretation.py`'s legitimate `os.environ` usage triggers the scanner's `filesystem_access`/exception-handling heuristics, documented as correct and deliberate rather than a stray import to remove, unlike R3's genuine unused-import bug).

```
python -m unittest discover -s tests
Ran 1685 tests in 54.114s
OK
```

TESTS=1685_PASS_0_FAIL_0_SKIP (1650 entering baseline + 34 new R4 tests + 1 net from splitting one R2 test into two more precisely-scoped tests = 1685; 0 tests removed or weakened)

---

## READINESS

```
python -m legacy_documenter.knowledge.readiness
readiness=READY, provider_calls=0, real_llm_calls=0
```

READINESS=READY

Also verified: `python main.py full --help` lists `--allow-ai-interpretation` with its explanatory help text.

---

## REAL_PROVIDER_CALLS

REAL_PROVIDER_CALLS=0

No test in this round imports or constructs `CopilotProvider`/`GeminiProvider` (verified by a dedicated source-scanning test); every provider used is `legacy_documenter.llm.core.FakeLLMProvider` or a local subclass overriding `structured_generate` to simulate a failure — never a real network/process call.

## AI_INVOKED_TEST_BEHAVIOR

Verified across every relevant scenario: `False` by default; `False` when opted in but `CONTEXT` failed (provider never resolved); `True` once a request actually reaches `structured_generate`, whether that call succeeds, returns a provider-error status, returns malformed structured output, or raises an exception.

## CANONICAL_KNOWLEDGE_PRODUCED

CANONICAL_KNOWLEDGE_PRODUCED=false

## TECHNICAL_LEAD_APPROVAL

TECHNICAL_LEAD_APPROVAL=false

Both verified `False` in every scenario, including a fully successful AI-enabled run with generated proposals.

---

## PRODUCTION_BEHAVIOR_CHANGED

PRODUCTION_BEHAVIOR_CHANGED=true

Expected and intentional: `full --allow-ai-interpretation` is new, opt-in behavior. Default `full` (no flag) and `analyze` are unaffected (see below).

## LEGACY_ANALYZE_BEHAVIOR_CHANGED

LEGACY_ANALYZE_BEHAVIOR_CHANGED=false

Verified: `analyze` never creates a `proposals/` directory; the legacy bare-positional invocation and explicit `analyze` still produce byte-for-byte identical output trees (subprocess-verified, as in every prior round).

## V4_1_REOPENED

V4_1_REOPENED=false

## V5_IMPLEMENTED

V5_IMPLEMENTED=false

## PLUGIN_RUNTIME

PLUGIN_RUNTIME=NOT_IMPLEMENTED

---

## DEFERRED

- Human approval UX for reviewing/acting on `PENDING_TECHNICAL_LEAD_REVIEW` proposals (a future round — `knowledge/approval` has no production caller yet, by design).
- Canonical knowledge promotion (R10-equivalent integration).
- R11/R12 projection wiring into `full`.
- Plugin runtime.
- `documentation/generator.py`'s hardcoded-path/direct-provider cleanup (still not required; deferred again per DOCUMENTATION_GENERATOR_DECISION).
- Gemini provider registration in `ProviderRegistry` (a pre-existing, independent gap noted since V4.2-R0; not touched here since R4 does not require it).
- A real-provider pilot and the IST/Operacional pilot (both explicitly out of R4's scope guard; reserved for a later round).
- V5 provider/model-agnosticism redesign.

---

## RISKS

| Risk | Classification | Mitigation |
|---|---|---|
| `orchestration.ai_interpretation` deliberately not reusing `deep_interpretation.py` could be read as ignoring the task's "execute the existing interpretation capability" instruction | LOW | Documented explicitly and in detail (AI_INTEGRATION_ARCHITECTURE) with the concrete characterization evidence (hardcoded V3 paths/targets) that makes literal reuse a context-boundary violation; the *pattern* (provider boundary, validation discipline) is reused, the *V3-specific function* is not |
| A real provider's structured output not matching the small `FINDING_SCHEMA`/finding shape this module expects (real providers may not honor structured-output instructions as reliably as `FakeLLMProvider`) | MEDIUM | Already the exact scenario `_validate_findings` exists to handle -- any shape mismatch is a structured `INVALID_OUTPUT` failure, never a crash or an invented proposal; a future real-provider pilot round should specifically stress-test this |
| `full_pipeline.py` is now VERY_HIGH risk by the maintainability inventory's own heuristic (488 lines, many branches) | MEDIUM | Already covered by 34 new R4 tests plus all reused R2/R3 stage-orchestration tests; any future round touching it should add characterization tests first, per the established methodology; a future round could consider extracting the AI/proposal stage-wiring block into a small dedicated function if it grows further |
| `tests/test_v4_1_r0_maintainability_inventory.py` needing another empirically-recomputed update in R5+ | MEDIUM | The method is now demonstrated four times (R1-R4) and documented inline in the test for the next round's author |
| Gemini remaining unregistered in `ProviderRegistry` means `LEGACYMAPPER_LLM_PROVIDER=GEMINI` would fail at `_resolve_provider()` time with `ValueError("unknown provider")` | LOW | Pre-existing gap, unrelated to R4's scope; `_resolve_provider()` failing closed (rather than silently falling back to a different provider) is itself the correct, safe behavior until a future round registers it |

---

## DECISION

DECISION=V4_2_R4_READY_FOR_TECHNICAL_LEAD_REVIEW

## NEXT

NEXT=HUMAN_REVIEW_V4_2_R4
