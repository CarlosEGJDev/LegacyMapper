"""Opt-in AI interpretation over the CURRENT `full` run's own evidence (V4.2-R4).

Architecture decision (documented per V4.2-R4 section 5/8): this module does
**not** call `legacy_documenter.analysis.deep_interpretation.run_deep_interpretation`.
That function is a V3-R8-specific tool hardcoded to `output/v3_r8_1` evidence
files and eight fixed target ids (`FMI-001`, ...) -- calling it here would
violate the R4 context-boundary requirement that AI must consume evidence
from the current run, never a historical/unrelated snapshot. Instead, this
module builds its own small context package from THIS run's own
`<output_dir>/ai_context/*.json` (written moments earlier by the same run's
CONTEXT stage) via the existing, path-agnostic `ContextResolver`/
`ContextComposer`, and calls a provider through the existing
`ProviderConfig`/`ProviderRegistry` boundary -- the same pattern
`deep_interpretation.py` already uses for provider selection, reused here,
just not its V3-specific evidence-gathering.

This module produces INTERPRETATION FINDINGS only: untrusted, unapproved,
non-canonical, always traceable to evidence ids the current run actually
discovered. It never writes anything to disk and never creates a `Proposal`
-- that is `orchestration.proposal_adapter`'s job.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from legacy_documenter.context.composer import ContextComposer
from legacy_documenter.context.resolver import ContextResolver
from legacy_documenter.llm.core import LLMProvider, LLMRequest, ProviderConfig, ProviderRegistry

FINDING_SCHEMA = {"required": ["findings"]}

SYSTEM_INSTRUCTION = (
    "You interpret already-discovered, deterministic evidence about a legacy system. "
    "You may only restate or explain what the evidence already shows. Never invent a "
    "relationship, business purpose, or fact the evidence does not contain. Cite only "
    "the evidence reference ids you were given."
)

USER_INSTRUCTION = (
    'Given the attached deterministic evidence package, list any findings that restate '
    'or explain what the evidence already shows. Return JSON exactly shaped as '
    '{"findings": [{"statement": str, "confidence": "CONFIRMED"|"UNCERTAIN", '
    '"evidence_refs": [ref, ...]}]}. Every evidence_refs entry must be one of the ref '
    "values already present in the attached context package's records."
)


@dataclass
class AiInterpretationResult:
    """Outcome of one AI interpretation attempt.

    `provider_called` is the field `full_pipeline` reads to set
    `RunResult.ai_invoked` -- it is only ever `True` once a request actually
    reached `provider.structured_generate(...)`, never merely because
    interpretation was requested (see V4.2-R4 section 13).
    """

    status: str  # "SUCCESS" | "CONTEXT_UNAVAILABLE" | "PROVIDER_ERROR" | "INVALID_OUTPUT"
    provider_called: bool
    provider_id: str | None = None
    model_id: str | None = None
    findings: list[dict] = field(default_factory=list)
    context_package_id: str | None = None
    error_message: str | None = None


def run_ai_interpretation(output_dir: str | Path, provider: LLMProvider | None = None) -> AiInterpretationResult:
    """Runs one opt-in AI interpretation pass over the current run's own context.

    `output_dir` must be THIS run's `--output` directory. The context package
    is built exclusively from `<output_dir>/ai_context/*.json` -- never from
    `output/v2_r5_1_full/`, `output/v3_*`, or `codex/V3/`. `provider`, when
    supplied, replaces provider resolution via `ProviderRegistry` entirely --
    this is the seam tests use so no real network/provider call ever occurs
    (V4.2-R4 REAL_AI_RUNTIME_CALL_ALLOWED=false).
    """
    try:
        resolver = ContextResolver(output_dir)
        package = ContextComposer(resolver).compose("SYSTEM", profile="SMALL")
    except (FileNotFoundError, ValueError, KeyError) as exc:
        return AiInterpretationResult(status="CONTEXT_UNAVAILABLE", provider_called=False, error_message=str(exc))

    known_refs = {record["ref"] for record in package.get("records", [])}
    if provider is None:
        provider = _resolve_provider()

    request = LLMRequest(
        purpose="ARCHITECTURE_INTERPRETATION",
        system_instruction=SYSTEM_INSTRUCTION,
        user_instruction=USER_INSTRUCTION,
        context=package,
        context_package_id=package["package_id"],
        context_schema_version=package["schema_version"],
        source_snapshot=str(package.get("source_snapshot") or ""),
        structured_output=True,
    )

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
        # provider/network failure, so it is categorized accordingly.
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
    dropped or guessed at.
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
