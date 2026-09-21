"""Opt-in AI interpretation over the CURRENT `full` run's own evidence (V4.2-R4, V4.3-R5).

Architecture decision (documented per V4.2-R4 section 5/8): this module does
**not** call `legacy_documenter.analysis.deep_interpretation.run_deep_interpretation`.
That function is a V3-R8-specific tool hardcoded to `output/v3_r8_1` evidence
files and eight fixed target ids (`FMI-001`, ...) -- calling it here would
violate the R4 context-boundary requirement that AI must consume evidence
from the current run, never a historical/unrelated snapshot.

V4.3-R5 changed *what* this module sends, not where it reads from. Until R5 it
built its package with `ContextComposer(resolver).compose("SYSTEM",
profile="SMALL")` -- the pre-R2 mechanism, whose `records` are bare reference
ids (`{"ref", "priority", "category"}`) for an unbounded `SYSTEM` sweep. That
is the V4.3-R0 defect pair `D-01` (no mandatory ceiling; a real repository
produced a ~13.8 MB / ~3.6 M token prompt, `EEE-02`) and `D-02`/`EEE-03`
(references carry no meaning). This module now builds a flow-scoped,
budget-bounded `AI_HYDRATED_PROJECTION 1.0` package of **hydrated** records
(`legacy_documenter.context.ai_projection`, over
`legacy_documenter.context.hydration`), and -- separately, because R1 section
5.2 is explicit that a package's own budget never authorizes a call -- measures
the **final serialized request payload** (`legacy_documenter.llm.core
.measure_request_payload`, the exact string a provider adapter's own prompt
builder now delegates to) against an applicable limit before reaching the
provider at all. This module still names no concrete provider class.

This module produces INTERPRETATION FINDINGS only: untrusted, unapproved,
non-canonical, always traceable to evidence ids the current run actually
discovered. It never writes anything to disk and never creates a `Proposal`
-- that is `orchestration.proposal_adapter`'s job.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from ._run_evidence_io import load_indexes as _load_indexes, load_source_snapshot as _load_source_snapshot
from legacy_documenter.context.ai_projection import (
    PROFILE_REDUCTION,
    AiProjectionBuilder,
    package_reference_ids,
    select_flow_ids,
)
from legacy_documenter.context.composer import PROFILES
from legacy_documenter.llm.core import (
    LLMProvider,
    LLMRequest,
    ProviderConfig,
    ProviderRegistry,
    measure_request_payload,
)

FINDING_SCHEMA = {"required": ["findings"]}

#: The budget profile used when a caller does not choose one. `SMALL`
#: (80 records / 16,000 characters, reused verbatim from
#: `legacy_documenter.context.composer.PROFILES`) is the same profile this
#: module already used before V4.3-R5 -- the change is that it is now applied
#: to a flow-scoped hydrated projection instead of an unbounded `SYSTEM`
#: reference sweep, and that `FULL` is not reachable from here at all.
DEFAULT_PROFILE = "SMALL"

#: LegacyMapper's own ceiling on the FINAL serialized request payload, in
#: estimated tokens, applied when the resolved provider declares no
#: `context_window`. That is the normal case in production today:
#: `_resolve_provider` builds a `ProviderConfig` without `context_window`, so
#: `FakeLLMProvider._status`'s existing check never even fires, and nothing
#: else measured the wrapped payload (V4.3-R0 `D-01`).
#:
#: Why 16,000: external finding `EEE-04` recorded that a hydrated FLOW
#: projection of ~5,600 tokens was enough for a useful, traceable
#: interpretation. 16,000 is ~2.9x that, which leaves real margin for the
#: system/user instructions, the policy blocks and the output schema that wrap
#: the package (all of which `measure_request_payload` counts, and none of
#: which the package's own `statistics.estimated_tokens` does), while still
#: being ~225x below the ~3.6 M token payload `EEE-02` observed. At the
#: shared 4-characters-per-token estimate this is ~64,000 characters.
DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS = 16000

SYSTEM_INSTRUCTION = (
    "You interpret already-discovered, deterministic evidence about a legacy system. "
    "You may only restate or explain what the evidence already shows. Never invent a "
    "relationship, business purpose, or fact the evidence does not contain. Cite only "
    "the evidence reference ids you were given. "
    "Tool use is prohibited: do not call, request, or simulate any tool, function, "
    "plugin, agent, or command. Do not inspect, open, read, list, or search any file, "
    "directory, repository, or URL. Do not execute shell commands or code. The attached "
    "evidence package is your only permitted source of information. Return only the "
    "requested structure: one strict JSON object, with no Markdown fences, comments, "
    "explanation, prefix, suffix, or chain-of-thought."
)

USER_INSTRUCTION = (
    'Given the attached deterministic, hydrated evidence package, list any findings that '
    'restate or explain what the evidence already shows. Return JSON exactly shaped as '
    '{"findings": [{"statement": str, "confidence": "CONFIRMED"|"UNCERTAIN", '
    '"evidence_refs": [ref, ...]}]}. Every evidence_refs entry must be one of the '
    "deterministic ids already present in the attached package's hydrated records "
    "(its flow_id, entry point id, path_ids, node/terminal ids, or evidence_refs)."
)


@dataclass
class AiInterpretationResult:
    """Outcome of one AI interpretation attempt.

    `provider_called` is the field `full_pipeline` reads to set
    `RunResult.ai_invoked` -- it is only ever `True` once a request actually
    reached `provider.structured_generate(...)`, never merely because
    interpretation was requested (see V4.2-R4 section 13). A
    `CONTEXT_TOO_LARGE` result therefore always carries
    `provider_called=False`: that gate fires *before* any call.
    """

    status: str  # "SUCCESS" | "CONTEXT_UNAVAILABLE" | "CONTEXT_TOO_LARGE" | "PROVIDER_ERROR" | "INVALID_OUTPUT"
    provider_called: bool
    provider_id: str | None = None
    model_id: str | None = None
    findings: list[dict] = field(default_factory=list)
    context_package_id: str | None = None
    error_message: str | None = None


def run_ai_interpretation(
    output_dir: str | Path, provider: LLMProvider | None = None,
    flow_ids: list[str] | None = None, profile: str = DEFAULT_PROFILE,
) -> AiInterpretationResult:
    """Runs one opt-in AI interpretation pass over the current run's own evidence.

    `output_dir` must be THIS run's `--output` directory: the hydrated
    projection is built exclusively from `<output_dir>/index/*.json` and its
    `source_snapshot` read from `<output_dir>/ai_context/SYSTEM_CONTEXT.json`
    -- never from `output/v2_r5_1_full/`, `output/v3_*`, or `codex/V3/`.

    `flow_ids`, when given, scopes the projection to exactly those flows.
    When omitted, a bounded set is selected deterministically by
    `select_flow_ids` (confirmed evidence first, capped by the profile's own
    record ceiling) -- never an unbounded `SYSTEM` sweep (V4.3-R0 `D-01`).

    `provider`, when supplied, replaces provider resolution via
    `ProviderRegistry` entirely -- this is the seam tests use so no real
    network/provider call ever occurs (REAL_AI_RUNTIME_CALL_ALLOWED=false).
    """
    try:
        indexes = _load_indexes(output_dir)
        source_snapshot = _load_source_snapshot(output_dir)
    except (FileNotFoundError, ValueError, KeyError, OSError) as exc:
        return AiInterpretationResult(status="CONTEXT_UNAVAILABLE", provider_called=False, error_message=str(exc))

    if provider is None:
        provider = _resolve_provider()
    limit = _payload_token_limit(provider)
    if limit <= 0:
        # The provider's own declared output reservation consumes its whole
        # `context_window` (or exceeds it): no input payload, however small,
        # could ever fit alongside it. Fail closed before building anything --
        # not just before the call -- since there is nothing left to budget for.
        return AiInterpretationResult(
            status="CONTEXT_TOO_LARGE", provider_called=False,
            error_message=f"reserved_output_tokens_exhaust_context_window:limit={limit}",
        )

    try:
        package, request, metrics, rejection = _build_within_budget(indexes, source_snapshot, flow_ids, profile, limit)
    except ValueError as exc:
        return AiInterpretationResult(status="CONTEXT_UNAVAILABLE", provider_called=False, error_message=str(exc))
    if rejection is not None:
        # Reduce-and-retry already happened and still did not fit (or the
        # package itself came back BUDGET_INSUFFICIENT). The R5 prompt is
        # explicit that BUDGET_INSUFFICIENT must not continue blindly: no
        # provider call is made and the pre-existing `CONTEXT_TOO_LARGE`
        # status (`legacy_documenter.llm.core.STATUSES`) is reported instead.
        return AiInterpretationResult(
            status="CONTEXT_TOO_LARGE", provider_called=False,
            context_package_id=package["package_id"], error_message=rejection,
        )

    known_refs = package_reference_ids(package)

    try:
        response = provider.structured_generate(request, FINDING_SCHEMA)
    except Exception as exc:
        # A raw provider/network exception is never the machine contract -- reduce
        # it to a short, credential-free message (see `_sanitize_provider_error`).
        return AiInterpretationResult(status="PROVIDER_ERROR", provider_called=True, error_message=_sanitize_provider_error(exc))

    provider_id = getattr(response, "provider_id", None)
    model_id = getattr(response, "model_id", None)

    response_status = getattr(response, "status", None)
    if response_status == "INVALID_STRUCTURED_OUTPUT":
        # The provider's own schema check already rejected the shape (e.g. a
        # missing top-level key) -- this is a malformed-output problem, not a
        # provider/network failure, so it is categorized accordingly. This is
        # a *post-call* safe failure and is deliberately independent of the
        # pre-call CONTEXT_TOO_LARGE gate above; both can occur, never the
        # same one masking the other.
        errors = ", ".join(getattr(response, "validation_errors", None) or [])
        return AiInterpretationResult(
            status="INVALID_OUTPUT", provider_called=True, provider_id=provider_id, model_id=model_id,
            error_message=errors or "invalid_structured_output",
        )
    if response_status != "SUCCESS":
        return AiInterpretationResult(
            status="PROVIDER_ERROR", provider_called=True, provider_id=provider_id, model_id=model_id,
            error_message=_sanitize_provider_error(getattr(response, "error", None) or response_status),
        )

    findings, error = _validate_findings(response.parsed_output, known_refs)
    if error:
        return AiInterpretationResult(
            status="INVALID_OUTPUT", provider_called=True, provider_id=provider_id, model_id=model_id,
            context_package_id=package["package_id"], error_message=error,
        )

    return AiInterpretationResult(
        status="SUCCESS", provider_called=True, provider_id=provider_id, model_id=model_id,
        findings=findings, context_package_id=package["package_id"],
    )


def _build_request(package: dict) -> LLMRequest:
    """Builds the `LLMRequest` for one `ai_projection` package.

    `metadata` is left empty on purpose. The provider's payload wrapper
    (`legacy_documenter.llm.core.render_request_payload`) emits
    `evidence_policy`/`claim_policy`/`missing_information_policy` blocks from
    it; an empty dict keeps each of those at `{}` rather than shipping
    audit/bookkeeping structures the interpretation task does not need ("no
    enviar metadata/continuations masivas innecesarias", R5 prompt). The
    package itself likewise carries only counts in `truncation`, never a
    `continuation_refs` list (see `ai_projection`).
    """
    return LLMRequest(
        purpose="ARCHITECTURE_INTERPRETATION",
        system_instruction=SYSTEM_INSTRUCTION,
        user_instruction=USER_INSTRUCTION,
        context=package,
        context_package_id=package["package_id"],
        context_schema_version=package["schema_version"],
        source_snapshot=str(package.get("source_snapshot") or ""),
        structured_output=True,
    )


def _build_within_budget(
    indexes: dict, source_snapshot: str, flow_ids: list[str] | None, profile: str, limit: int,
) -> tuple[dict, LLMRequest, dict, str | None]:
    """Builds the projection and its request, reducing the profile once if the payload does not fit.

    Policy (explicit, per the R5 prompt's requirement that it not be left
    ambiguous): **reduce once, then fail closed.** The first attempt uses the
    requested profile; if the package comes back `BUDGET_INSUFFICIENT`, or the
    measured final payload exceeds `limit`, exactly one retry is made at the
    next smaller profile (`PROFILE_REDUCTION`, e.g. `SMALL` -> `TINY`). If that
    still does not fit -- or the requested profile is already the smallest --
    no provider call is made and the caller reports `CONTEXT_TOO_LARGE`.
    A single retry is preferred over an open-ended shrink loop because each
    reduction drops real evidence: silently grinding a package down until
    something fits would be the "continue blindly" behavior this round exists
    to remove.

    Returns `(package, request, metrics, rejection)`; `rejection` is `None`
    when the request may be sent, otherwise a `; `-joined reason string naming
    every attempt that was refused and why (so a rejection is diagnosable
    without re-running).
    """
    builder = AiProjectionBuilder()
    attempts = [profile] + ([PROFILE_REDUCTION[profile]] if profile in PROFILE_REDUCTION else [])
    package = request = metrics = None
    reasons: list[str] = []
    for attempt_profile in attempts:
        scoped = flow_ids if flow_ids is not None else select_flow_ids(indexes, PROFILES[attempt_profile][0])
        package = builder.build(scoped, indexes, source_snapshot=source_snapshot, profile=attempt_profile)
        request = _build_request(package)
        metrics = measure_request_payload(request, FINDING_SCHEMA)
        if package["statistics"]["completeness"] == "BUDGET_INSUFFICIENT":
            reasons.append(f"budget_insufficient:profile={attempt_profile}")
            continue
        if metrics["payload_estimated_tokens"] > limit:
            reasons.append(
                f"payload_estimated_tokens={metrics['payload_estimated_tokens']}"
                f">limit={limit}:profile={attempt_profile}"
            )
            continue
        return package, request, metrics, None
    return package, request, metrics, "; ".join(reasons) or "context_budget_not_satisfied"


def _payload_token_limit(provider: object, request_max_output_tokens: int | None = None) -> int:
    """The applicable ceiling for the final INPUT payload, in estimated tokens.

    Policy (V4.3-R5, this correction):

    - A provider that declares no valid `context_window` (not an `int > 0`)
      gets LegacyMapper's own `DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS` ceiling on
      the input payload, unchanged from before this correction. That ceiling
      is never widened by anything below.
    - A provider that DOES declare a valid `context_window` shares that same
      window between the input payload and whatever output the provider may
      still need to produce afterwards. Authorizing an input payload up to
      the full `context_window` -- the pre-correction behavior -- could
      therefore authorize `input_tokens + max_output_tokens > context_window`
      once the provider actually generates. This function instead reserves
      output capacity first and returns the remainder:

          effective_input_limit = context_window - reserved_output_tokens

      `reserved_output_tokens` is chosen deterministically: prefer the
      provider's own declared `capabilities().max_output_tokens` when it is a
      valid `int > 0`; if the caller additionally knows the specific
      request's `max_output_tokens` and it is a smaller valid positive int,
      that smaller value is the reservation instead, since it is what that
      particular request could actually still produce. A provider that
      declares neither reserves nothing extra (`reserved_output_tokens = 0`)
      -- there is no further explicit, deterministic figure to reserve
      against, and LegacyMapper does not guess one.
    - The effective limit returned here can be zero or negative when the
      reservation consumes the whole window or more; callers MUST fail
      closed (`CONTEXT_TOO_LARGE`) on that rather than passing a
      non-positive limit through to a size comparison, since no input
      payload, however small, could ever fit alongside that reservation.
      This function itself never raises for that case -- it reports the
      number so the caller can gate on it before doing any other work.
    """
    try:
        capabilities = provider.capabilities()
        window = getattr(capabilities, "context_window", None)
    except Exception:
        capabilities = None
        window = None
    if not (isinstance(window, int) and window > 0):
        return DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS

    declared_output = getattr(capabilities, "max_output_tokens", None) if capabilities is not None else None
    reserved = declared_output if isinstance(declared_output, int) and declared_output > 0 else 0
    if (
        isinstance(request_max_output_tokens, int)
        and request_max_output_tokens > 0
        and request_max_output_tokens < reserved
    ):
        reserved = request_max_output_tokens

    return window - reserved


def _resolve_provider() -> LLMProvider:
    """Resolves a real provider through the existing registry (production path only;
    every test injects `provider` explicitly instead of calling this)."""
    provider_type = os.environ.get("LEGACYMAPPER_LLM_PROVIDER", "COPILOT")
    provider_id = os.environ.get("LEGACYMAPPER_LLM_PROVIDER_ID", f"{provider_type.lower()}-local")
    model_id = os.environ.get("LEGACYMAPPER_LLM_MODEL", "")
    config = ProviderConfig(provider_type, provider_id, model_id, max_output_tokens=2000, options={"timeout": 120})
    return ProviderRegistry().create(config)


def _validate_findings(parsed_output: object, known_refs: set[str]) -> tuple[list[dict], str | None]:
    """Validates AI output against a small closed schema.

    Never repairs meaning-changing malformed output (V4.2-R4 section 16): any
    structural problem -- wrong shape, missing statement, an evidence ref the
    current run never discovered -- is reported as an error, not silently
    dropped or guessed at. Since V4.3-R5 `known_refs` is the closed set of
    deterministic ids the *hydrated* records actually carry
    (`ai_projection.package_reference_ids`: flow id, entry point id, path ids,
    node/terminal ids, recorded `evidence_refs`), not the `"ref"` field of the
    pre-R2 reference records.
    """
    if not isinstance(parsed_output, dict):
        return [], "expected_object"
    findings = parsed_output.get("findings")
    if not isinstance(findings, list):
        return [], "findings_must_be_a_list"
    validated: list[dict] = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            return [], f"finding_{index}_not_an_object"
        statement = finding.get("statement")
        if not isinstance(statement, str) or not statement.strip():
            return [], f"finding_{index}_missing_statement"
        evidence_refs = finding.get("evidence_refs")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            return [], f"finding_{index}_missing_evidence_refs"
        unknown = [ref for ref in evidence_refs if ref not in known_refs]
        if unknown:
            return [], f"finding_{index}_unknown_evidence_refs:{','.join(sorted(unknown))}"
        confidence = finding.get("confidence") or "UNCERTAIN"
        if confidence not in {"CONFIRMED", "UNCERTAIN"}:
            return [], f"finding_{index}_invalid_confidence"
        validated.append({"statement": statement.strip(), "confidence": confidence, "evidence_refs": list(evidence_refs)})
    return validated, None


def _sanitize_provider_error(error: object) -> str:
    """Reduces a provider error to a short, credential-free message.

    Never serializes a raw traceback, environment dump, or credential/token
    value (V4.2-R4 section 15) -- only the first line of the provider's own
    message, truncated.
    """
    text = getattr(error, "message", None) or str(error)
    return text.splitlines()[0][:300] if text else "provider_error"
