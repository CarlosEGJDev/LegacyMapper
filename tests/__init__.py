"""LegacyMapper test suite package.

V4.2-R5.1 real-provider guard: R5 disclosed that a manual, non-test CLI
invocation of `full --allow-ai-interpretation` (run without injecting a
fake provider) accidentally reached this development environment's real,
locally logged-in Copilot client. That specific incident happened outside
`tests/`, so it could not have been caught here -- but the same silent
failure mode (a test author forgetting to inject `ai_provider=`/patch
`_resolve_provider`, then unknowingly reaching a real provider instead of
merely getting a wrong result) is exactly what this guard closes for the
automated suite itself: every round under `REAL_AI_RUNTIME_CALL_ALLOWED=false`
must fail loudly, not silently succeed against a real provider.

This module is imported once, automatically, as soon as any test under
`tests/` is imported (`python -m unittest discover -s tests`, or any
`python -m unittest tests.test_x`) -- so the guard is installed for every
regression run without each test file having to opt in. It replaces
`legacy_documenter.orchestration.ai_interpretation._resolve_provider` (the
one seam that resolves a REAL provider through `ProviderRegistry`, reached
only when a caller passes no `ai_provider` at all) with a stub that raises
immediately, naming the offending call. It does not touch
`CopilotProvider`/`GeminiProvider` construction itself -- several existing
tests (`test_v3_r6.py`, `test_v3_r6_1.py`) legitimately instantiate those
classes directly with an injected fake client/transport, and must keep
working unchanged.

A test that needs to exercise `_resolve_provider`'s own env-var-driven
config-building logic (as V4.2-R4's `ExplicitOptInEnablesInterpretationTests`
already does) still can: `unittest.mock.patch(...)` on the same target
saves and restores whatever is currently installed, so it layers cleanly on
top of this module-level guard with no special-casing required.

Production code (`python main.py full ... --allow-ai-interpretation`, run
directly, not through this package) is completely unaffected -- this file
is only ever imported as part of the `tests` package, never by `main.py` or
any `legacy_documenter` module.
"""
from __future__ import annotations

from legacy_documenter.orchestration import ai_interpretation

_REAL_PROVIDER_GUARD_MESSAGE = (
    "A test attempted to resolve a REAL AI provider via "
    "legacy_documenter.orchestration.ai_interpretation._resolve_provider(). "
    "REAL_AI_RUNTIME_CALL_ALLOWED=false for the automated test suite: inject "
    "a FakeLLMProvider (ai_provider=... / provider=...) or patch "
    "_resolve_provider explicitly instead of relying on real provider "
    "resolution. See docs/V4_2/V4_2_R5_1_EXIT_CODE_CONTRACT_AND_REAL_PROVIDER_GUARD_RESULT.md."
)


def _blocked_resolve_provider():
    raise RuntimeError(_REAL_PROVIDER_GUARD_MESSAGE)


ai_interpretation._resolve_provider = _blocked_resolve_provider
