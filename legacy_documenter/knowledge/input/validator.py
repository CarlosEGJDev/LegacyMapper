"""Deterministic validation entry point for the V4 input/source contract layer.

`validate_source_input` is the single boundary a caller uses: it normalizes
the raw `SourceInput`, applies the universal empty-material rule, applies the
`SourceType`-specific policy gates from `catalog.py`, validates any embedded
`Origin`/`TemporalState`, and resolves the scoped authority statement. No
network access, no file access, and no provider call happens here — R2
validates contracts; ingestion (ownership of actually reading a supplied
reference) belongs to a later round.
"""
from legacy_documenter.knowledge.domain.enums import SourceType, TemporalState
from legacy_documenter.knowledge.input.catalog import SourceContractCatalog, SourceContractPolicy
from legacy_documenter.knowledge.input.contracts import SourceInput, SourceInputValidationError
from legacy_documenter.knowledge.input.normalization import normalize_source_input


def validate_source_input(raw: SourceInput) -> SourceInput:
    """Validates and normalizes `raw`, returning a new, safe-to-use `SourceInput`.

    Raises `SourceInputValidationError` (or `UnknownSourceTypeError`, a
    subclass of `ValueError`, from the catalog lookup) on any contract
    violation. Never repairs, promotes, or silently drops an invalid field.
    """
    if not isinstance(raw.source_type, SourceType):
        raise SourceInputValidationError(f"invalid_source_type:{raw.source_type!r}")
    policy = SourceContractCatalog.get(raw.source_type)

    normalized = normalize_source_input(raw)

    _check_meaningful_payload(normalized, policy)
    if normalized.origin is not None:
        normalized.origin.validate()
    _check_temporal_state(normalized)
    _check_policy_specific(normalized, policy)
    _check_authority(normalized, policy)

    return _resolve_authority_scope(normalized, policy)


def _check_meaningful_payload(value: SourceInput, policy: SourceContractPolicy) -> None:
    """Rejects material with no non-blank `content` and no non-blank `reference`.

    This is the universal floor every `SourceType` shares, except
    `USER_STORY`, whose structured actor/goal/benefit form is a valid
    alternative payload entirely handled by `_check_story_structure`.
    """
    if policy.requires_story_structure:
        return
    if value.content is None and value.reference is None:
        raise SourceInputValidationError("empty_material:content_and_reference_both_absent")


def _check_temporal_state(value: SourceInput) -> None:
    """Rejects a `temporal_state` outside the closed R1 enum; absence is always allowed."""
    if value.temporal_state is not None and not isinstance(value.temporal_state, TemporalState):
        raise SourceInputValidationError(f"invalid_temporal_state:{value.temporal_state!r}")


def _check_authority(value: SourceInput, policy: SourceContractPolicy) -> None:
    """Rejects `authoritative=True` for a source type whose policy forbids claiming authority."""
    if value.authoritative and not policy.authority_allowed:
        raise SourceInputValidationError(
            f"authority_not_allowed_for_source_type:{value.source_type.value}"
        )


def _resolve_authority_scope(value: SourceInput, policy: SourceContractPolicy) -> SourceInput:
    """Fills the canonical, source-type-scoped authority statement when authority is claimed.

    Only ever copies the fixed, policy-declared `authority_scope` text — it
    never fabricates a new claim. A caller-supplied `authority_scope` is left
    untouched (trusted as already deterministic, unaugmented text).
    """
    if value.authoritative and not value.authority_scope and policy.authority_scope:
        value.authority_scope = policy.authority_scope
    return value


def _check_policy_specific(value: SourceInput, policy: SourceContractPolicy) -> None:
    """Dispatches to each policy gate that applies to `value.source_type`.

    One function per gate, composed by boolean flags on the policy, instead of
    one validator subclass per `SourceType`.
    """
    if policy.requires_code_traceability:
        _check_code_traceability(value)
    if policy.requires_origin_traceability:
        _check_origin_traceability(value)
    if policy.requires_story_structure:
        _check_story_structure(value)
    if policy.requires_decision_identity:
        _check_decision_identity(value)
    if policy.requires_model_traceability:
        _check_model_traceability(value)
    if policy.requires_explicit_content:
        _check_explicit_content(value)


def _check_code_traceability(value: SourceInput) -> None:
    """Requires a code locator and an origin, without demanding every code metadata field."""
    if not value.reference:
        raise SourceInputValidationError("deterministic_code_fact_requires_reference")
    if value.origin is None or not value.origin.kind:
        raise SourceInputValidationError("deterministic_code_fact_requires_origin")


def _check_origin_traceability(value: SourceInput) -> None:
    """Requires a locator beyond bare content: a `reference`, or an origin with one."""
    has_origin_reference = value.origin is not None and bool(value.origin.reference)
    if not value.reference and not has_origin_reference:
        raise SourceInputValidationError(
            f"{value.source_type.value.lower()}_requires_traceable_origin_or_reference"
        )


def _check_story_structure(value: SourceInput) -> None:
    """Accepts free-form content, or structured actor/goal/benefit metadata; never requires both forms."""
    structured = any(value.metadata.get(key) for key in ("actor", "goal", "benefit"))
    if not value.content and not structured:
        raise SourceInputValidationError(
            "user_story_requires_free_form_content_or_structured_actor_goal_benefit"
        )


def _check_decision_identity(value: SourceInput) -> None:
    """Requires both a decision identifier and an approval/source authority reference."""
    has_decision_identifier = bool(value.reference) or bool(value.metadata.get("decision_id"))
    has_authority_reference = (
        bool(value.metadata.get("approver"))
        or (value.origin is not None and (bool(value.origin.contributor) or bool(value.origin.reference)))
    )
    if not has_decision_identifier or not has_authority_reference:
        raise SourceInputValidationError(
            "approved_decision_requires_decision_identity_and_approval_authority"
        )


def _check_model_traceability(value: SourceInput) -> None:
    """Requires enough origin/model/process reference to keep AI-origin material identifiable as such."""
    if not value.content:
        raise SourceInputValidationError("ai_interpretation_requires_content")
    traceable = (
        (value.origin is not None and bool(value.origin.reference))
        or bool(value.metadata.get("model"))
        or bool(value.metadata.get("process"))
    )
    if not traceable:
        raise SourceInputValidationError("ai_interpretation_requires_model_or_process_traceability")


def _check_explicit_content(value: SourceInput) -> None:
    """Requires explicit content (a reference alone cannot explain what is unresolved)."""
    if not value.content:
        raise SourceInputValidationError("unresolved_requires_explicit_content")
