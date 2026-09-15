# LegacyMapper V4.2-R5.1 — Exit-Code Contract and Real-Provider Guard: Result

STATUS: COMPLETE

BASELINE: Entering test count 1714 PASS / 0 FAIL / 0 SKIP (V4.2-R5 closure).
Exiting test count 1723 PASS / 0 FAIL / 0 SKIP (1714 pre-existing + 9 new
R5.1 tests, 0 weakened/deleted).

---

## FILES_CREATED

- `tests/__init__.py` — the test-suite-wide real-provider guard: replaces
  `legacy_documenter.orchestration.ai_interpretation._resolve_provider`
  (the one seam that resolves a real provider through `ProviderRegistry`)
  with a stub that raises `RuntimeError` immediately, for the duration of
  any `python -m unittest ...` run under `tests/`. Installed once, at
  package import time, so no individual test file has to opt in.
- `tools/manual_verify_full_pipeline.py` — the documented safe
  manual-verification command (section 5/6): runs `run_full_pipeline`
  (optionally with `--allow-ai-interpretation`) always injecting
  `FakeLLMProvider`, so it can never reach a real provider regardless of
  flags passed. Usable as `python -m tools.manual_verify_full_pipeline
  <repository> --output <dir> [--allow-ai-interpretation] [--forced-status
  ...]`.
- `tests/test_v4_2_r5_1_exit_code_contract_and_real_provider_guard.py` — 9
  tests covering the consolidated exit-code contract, the guard itself,
  the fail-safe (not silent) behavior of an unguarded AI-enabled run, and
  the manual-verification tool.
- `docs/V4_2/V4_2_R5_1_EXIT_CODE_CONTRACT_AND_REAL_PROVIDER_GUARD_RESULT.md`
  — this file.

## FILES_MODIFIED

- `legacy_documenter/cli/router.py` — comment-only change: the exit-code
  contract header comment now states explicitly that the Technical Lead
  reaffirmed `0/1/2/4` as authoritative at R5.1, and that the R5 prompt's
  `0/4/5/2` was incorrect. `EXIT_SUCCESS`/`EXIT_PARTIAL`/`EXIT_FAILED`
  constants and `_EXIT_CODE_BY_STATUS` are byte-for-byte unchanged.
- `AGENTS.md` — new "Manual AI-Path Verification" subsection under
  "Safety", stating the rule from section 6: when
  `REAL_AI_RUNTIME_CALL_ALLOWED=false`, manual AI-path verification must
  use `tools/manual_verify_full_pipeline` (or an equivalent explicit
  `FakeLLMProvider` injection), never
  `python main.py full ... --allow-ai-interpretation` directly.
- `tests/test_v4_1_r0_maintainability_inventory.py` — not touched by this
  round (see MAINTAINABILITY note below): confirmed unaffected, no edit
  needed.

## AUTHORITATIVE_EXIT_CODE_CONTRACT

SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4

Confirmed by direct inspection of `legacy_documenter/cli/router.py`
(`EXIT_SUCCESS = 0`, `EXIT_PARTIAL = 1`, `EXIT_FAILED = 4`, argparse itself
owns `2`) and by `tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py`,
which has asserted this exact mapping since R2. No runtime code changed.

## ACTIVE_REFERENCES_FOUND

Searched `docs/**/*.md`, `legacy_documenter/**/*.py`, `AGENTS.md`,
`CLAUDE.md`, `PROJECT_STATE.json` for exit-code contract statements. Result:
**no active reference contradicted the authoritative contract.**

| Location | Contract stated | Classification |
|---|---|---|
| `legacy_documenter/cli/router.py` (header comment + constants) | `0/1/2/4` | CURRENT_ACTIVE_CONTRACT (matches runtime) |
| `docs/V4_2/V4_2_R0_FULL_PIPELINE_ARCHITECTURE_AND_INVENTORY_RESULT.md` | generic ("exit codes stay uniform"), no specific numbers | CURRENT_ACTIVE_CONTRACT (no numbers to be wrong) |
| `docs/V4_2/V4_2_R1_CLI_CONTRACT_AND_EXECUTION_MODEL_RESULT.md` | `SUCCESS=0`, `PARTIAL=1`, retired placeholder `3` | CURRENT_ACTIVE_CONTRACT (correct, historical placeholder correctly marked retired) |
| `docs/V4_2/V4_2_R2_DETERMINISTIC_FULL_PIPELINE_ORCHESTRATOR_RESULT.md` | `0/1/2/4`, explicit `EXIT_CODE_CONTRACT` section | CURRENT_ACTIVE_CONTRACT (correct, this is where the contract was established) |
| `docs/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX_RESULT.md` | `0/1/2/4`, with an explicit RISKS note flagging the R5 prompt's stale `0/4/5/2` | CURRENT_ACTIVE_CONTRACT (correct; the discrepancy was already disclosed here, not hidden) |
| `prompts/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX.md` section 16 | `0/4/5/2` | HISTORICAL_RECORD (the literal instruction as given for that round — a point-in-time task specification, not living documentation) |

No file was found that both (a) currently describes itself as documenting
the *active* contract and (b) states a number other than `0/1/2/4`. The
only `0/4/5/2` occurrence in the repository is the R5 prompt file itself,
which this round classifies as a historical instruction artifact, not
active documentation — see HISTORICAL_REFERENCES_PRESERVED.

## HISTORICAL_REFERENCES_PRESERVED

`prompts/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX.md` was **not**
edited. It is the literal task specification that was actually issued and
actually executed for R5 (CLAUDE.md: "the repository is the authoritative
source of state," but a prompt file is a record of an instruction given,
not a statement of current behavior). Rewriting its stated `0/4/5/2` after
the fact would erase evidence of exactly the discrepancy this round exists
to resolve. `docs/V4_2/V4_2_R5_UNIFIED_CLI_AND_OPERATIONAL_UX_RESULT.md`'s
own RISKS entry describing this discrepancy was also left unedited — it
already correctly described both the stale prompt number and the real
contract, and remains the historical record of when/how this was first
noticed.

## RUNTIME_EXIT_CODE_BEHAVIOR

Unchanged, as instructed (section 4: "do not change router exit-code
behavior if inspection confirms it already implements SUCCESS→0,
PARTIAL→1, FAILED→4, argparse→2"). Inspection confirmed exactly this, so
`legacy_documenter/cli/router.py`'s `EXIT_SUCCESS`/`EXIT_PARTIAL`/
`EXIT_FAILED`/`_EXIT_CODE_BY_STATUS` were not touched — only the header
comment was strengthened to record the Technical Lead's explicit
reaffirmation.

## EXIT_CODE_TESTS

One new consolidated test class,
`ExitCodeContractTests` (in `tests/test_v4_2_r5_1_exit_code_contract_and_real_provider_guard.py`),
asserting all four externally observable cases in one place:

- `test_router_constants_match_the_authoritative_contract` — the raw
  constants.
- `test_all_four_externally_observable_exit_codes` — `full` SUCCESS→0
  (real run), `full` PARTIAL→1 (forced `CONTEXT` stage failure), `full`
  FAILED→4 (forced `EXPORT` stage failure), `analyze` usage error→2
  (missing required positional, via subprocess so argparse's own
  `SystemExit(2)` is observed end-to-end); `readiness` SUCCESS→0 is
  exercised too.
- `test_no_stale_r1_placeholder_code_reused` — exit code `3` (R1's retired
  placeholder) can never reappear as a mapped `RunStatus` value.

This supplements, not replaces, the pre-existing per-scenario exit-code
assertions already in `tests/test_v4_2_r1_cli_contract_and_execution_model.py`
and `tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py` (none
weakened or removed).

## REAL_PROVIDER_GUARD

**Chosen solution (two parts, per section 5's explicit guidance to prefer
this over an invasive production change):**

1. **Automated-test guard** — `tests/__init__.py` replaces
   `legacy_documenter.orchestration.ai_interpretation._resolve_provider`
   (the exact, single seam that resolves a real provider via
   `ProviderRegistry`, reached only when a caller passes no `provider`/
   `ai_provider` at all) with a stub that raises `RuntimeError` naming the
   violation, installed once at package-import time so every
   `python -m unittest discover -s tests` run is protected without any
   test file having to opt in. This targets *resolution*, not provider
   *construction* — existing tests that legitimately build
   `CopilotProvider`/`GeminiProvider` directly with an injected fake
   client/transport (`test_v3_r6.py`, `test_v3_r6_1.py`) are completely
   unaffected (verified by
   `test_guard_does_not_block_direct_copilot_or_gemini_class_construction`).
   `unittest.mock.patch(...)` on the same target (used by two pre-existing
   R4 tests) still layers cleanly on top, since `patch` saves/restores
   whatever is currently installed.
2. **Documented safe manual-verification path** —
   `tools/manual_verify_full_pipeline.py`, always injecting
   `FakeLLMProvider` regardless of CLI flags, plus a new "Manual AI-Path
   Verification" rule in `AGENTS.md` stating that
   `python main.py full ... --allow-ai-interpretation` must never be
   invoked directly for manual verification when real AI calls are
   forbidden.

**Why not a deeper/production-level guard:** an env-var or code-level gate
inside `_resolve_provider()` itself that blocks real resolution by default
would either (a) require a normal, authorized production user to pass an
extra unexplained flag/env-var to get real AI behavior (violates section
5's "must remain capable of using the configured real provider during
normal authorized use... do not globally disable Copilot or external
providers"), or (b) require detecting "are we in a controlled/test
round" at runtime, which is exactly the invasive, environment-specific
complexity section 5 says not to over-engineer. The chosen two-part
solution protects both failure modes that actually occurred/could occur
(a forgetful automated test, and a human's unguarded manual command)
without touching production semantics at all.

## SAFE_MANUAL_VERIFICATION

`python -m tools.manual_verify_full_pipeline <repository> --output <dir>
[--allow-ai-interpretation] [--forced-status PROVIDER_ERROR]` — always
builds and injects a `FakeLLMProvider`; prints the same
`render_console_summary` output `main.py` would, in verbose mode (full
stage table), so a human can inspect the AI-enabled console/UX path
end-to-end without ever touching real-provider resolution. Verified by
`SafeManualVerificationTests`: one test proves it never calls
`_resolve_provider` (patched to raise `AssertionError` if it were), another
exercises both a demonstrated success and a demonstrated failure path
(`--forced-status PROVIDER_ERROR`) through it.

## REAL_PROVIDER_CALLS

**0.** Every test in this round (and the full suite) uses `FakeLLMProvider`
or the newly-installed raising stub; `tools/manual_verify_full_pipeline.py`
was used for its own two verification runs during this round, both with
`FakeLLMProvider` only. No `CopilotProvider`/`GeminiProvider` real-network
path was exercised at any point during R5.1's implementation or
verification.

## TESTS

9 new tests in
`tests/test_v4_2_r5_1_exit_code_contract_and_real_provider_guard.py`
(4 exit-code-contract tests, 4 real-provider-guard tests, covering both the
guard's positive effect and that it does not over-block legitimate direct
provider-class construction, 2 safe-manual-verification tests — one class
holds 2, see file for exact grouping). Full suite: 1723/1723 passing
(1714 pre-existing + 9 new), 0 weakened, 0 deleted.

## READINESS

`python -m legacy_documenter.knowledge.readiness` → `READINESS=READY`,
`provider_calls: 0`, `real_llm_calls: 0`.

## PRODUCTION_BEHAVIOR_CHANGED

No runtime behavior changed. `router.py`'s exit-code mapping is
byte-for-byte identical; only its comment was strengthened. The
`tests/__init__.py` guard only affects code imported and run under the
`tests` package — `legacy_documenter`/`main.py`/production execution never
imports `tests`, so `python main.py full ... --allow-ai-interpretation` in
normal use is completely unaffected and still capable of reaching a real,
configured provider.

## LEGACY_ANALYZE_BEHAVIOR_CHANGED

false — `analyze`/legacy invocation paths were not touched by this round;
the pre-existing R2 byte-identical legacy-vs-analyze test still passes
unmodified.

## V4_1_REOPENED

false

## V5_IMPLEMENTED

false

## PLUGIN_RUNTIME

NOT_IMPLEMENTED

## RISKS

1. The `tests/__init__.py` guard protects only code paths reached through
   the `tests` package. It does not and cannot protect an ad hoc manual
   shell command (the exact failure mode that caused the original R5
   incident) — that protection is documentation/process-based
   (`AGENTS.md`'s new rule + `tools/manual_verify_full_pipeline.py`), which
   depends on the rule actually being followed in future sessions rather
   than being mechanically enforced. This is the deliberate trade-off
   section 5 asked for ("do not over-engineer... strengthen test
   helpers/fixtures... make future round instructions unambiguous")
   rather than a gap left unaddressed.
2. If a future round adds a second real-provider-resolution seam elsewhere
   in the codebase (e.g. a different orchestration module calling
   `ProviderRegistry` directly rather than through
   `ai_interpretation._resolve_provider`), this guard would not cover it
   automatically. Recommend any future AI-integration round re-verify this
   guard still covers every production resolution seam.

## DECISION

V4_2_R5_1_READY_FOR_TECHNICAL_LEAD_REVIEW

## NEXT

HUMAN_REVIEW_V4_2_R5_1
