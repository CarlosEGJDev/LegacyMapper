"""Closed catalog of deterministic intake policies, one per V4 `SourceType`.

Mirrors the closed-catalog discipline of
`legacy_documenter.documentation.evidence_catalog` (canonical closure between a
key set and a known set): here the closure is between `SourceType` and its
registered `SourceContractPolicy`. An unknown `SourceType` or a `SourceType`
missing its policy both fail deterministically instead of falling back to a
default policy.
"""
from dataclasses import dataclass

from legacy_documenter.knowledge.domain.enums import SourceType


class UnknownSourceTypeError(ValueError):
    """Raised when a `SourceType` has no registered `SourceContractPolicy`."""


@dataclass(frozen=True)
class SourceContractPolicy:
    """Declares the deterministic intake rules for one `SourceType`.

    Each boolean gate below is checked by
    `legacy_documenter.knowledge.input.validator`; a policy composes gates
    instead of requiring a dedicated subclass per source type. `authority_scope`
    is the fixed, source-appropriate statement of what `authoritative=True`
    is allowed to claim for this type (see `V4_R2_INPUT_SOURCE_CONTRACTS.md`,
    "Authority Semantics"); `authority_allowed` is False only where claiming
    authority would contradict the source type's own meaning.
    """

    source_type: SourceType
    description: str
    requires_code_traceability: bool = False
    requires_origin_traceability: bool = False
    requires_story_structure: bool = False
    requires_decision_identity: bool = False
    requires_model_traceability: bool = False
    requires_explicit_content: bool = False
    authority_allowed: bool = True
    authority_scope: str = ""
    human_only_supported: bool = True


SOURCE_CONTRACT_POLICIES: dict[SourceType, SourceContractPolicy] = {
    SourceType.DETERMINISTIC_CODE_FACT: SourceContractPolicy(
        source_type=SourceType.DETERMINISTIC_CODE_FACT,
        description="Requires a code locator (reference) and an origin identifying the code repository/scanner, "
                    "sufficient to trace the fact back to code evidence. Does not require every possible code metadata field.",
        requires_code_traceability=True,
        human_only_supported=False,
        authority_scope="The analyzed code contains this observed structure/behavior; "
                         "it is not automatically evidence of the intended business behavior.",
    ),
    SourceType.HUMAN_REQUIREMENT: SourceContractPolicy(
        source_type=SourceType.HUMAN_REQUIREMENT,
        description="Requires meaningful content or a traceable reference to the supplied requirement. No code required.",
        authority_scope="This requirement was supplied/approved as a requirement; "
                         "it is not automatically evidence that the current system implements it.",
    ),
    SourceType.USER_STORY: SourceContractPolicy(
        source_type=SourceType.USER_STORY,
        description="Requires free-form story content, or structured actor/goal information in metadata "
                    "when no free-form content is supplied. No code required.",
        requires_story_structure=True,
        authority_scope="This user story was supplied as project/business material; "
                         "it is not automatically approved scope or evidence of implementation.",
    ),
    SourceType.BUSINESS_REQUIREMENT: SourceContractPolicy(
        source_type=SourceType.BUSINESS_REQUIREMENT,
        description="Requires meaningful content or reference describing the required business behavior/outcome. "
                    "No code required; implementation is never inferred.",
        authority_scope="This is the required business behavior/outcome as stated; "
                         "it is not automatically evidence that it is currently implemented.",
    ),
    SourceType.BUSINESS_CONTEXT: SourceContractPolicy(
        source_type=SourceType.BUSINESS_CONTEXT,
        description="Requires meaningful content or reference. Context is never automatically a requirement or norm.",
        authority_scope="This is supplied contextual business information; "
                         "it is not automatically a requirement or a norm by itself.",
    ),
    SourceType.TECHNICAL_CONSTRAINT: SourceContractPolicy(
        source_type=SourceType.TECHNICAL_CONSTRAINT,
        description="Requires meaningful content or reference describing the restriction/mandatory condition. "
                    "Never conflated with implementation evidence.",
        authority_scope="This is a stated technical restriction/condition; "
                         "it is not automatically evidence that the current system already satisfies or violates it.",
    ),
    SourceType.CORPORATE_STANDARD: SourceContractPolicy(
        source_type=SourceType.CORPORATE_STANDARD,
        description="Requires meaningful content or reference plus a traceable origin/reference establishing where "
                    "the standard came from.",
        requires_origin_traceability=True,
        authority_scope="The organization requires this standard; "
                         "it is not automatically evidence that every existing application complies with it.",
    ),
    SourceType.APPROVED_DECISION: SourceContractPolicy(
        source_type=SourceType.APPROVED_DECISION,
        description="Requires enough information to identify the decision (reference or metadata['decision_id']) "
                    "and its approval/source authority (origin.contributor, origin.reference, or metadata['approver']). "
                    "Never auto-promoted to canonical V4 approved knowledge; still passes through provenance/composition.",
        requires_decision_identity=True,
        authority_scope="A decision was approved by the identified authority outside the V4 proposal lifecycle; "
                         "this does not by itself make the material canonical V4 approved knowledge.",
    ),
    SourceType.EXTERNAL_DOCUMENT: SourceContractPolicy(
        source_type=SourceType.EXTERNAL_DOCUMENT,
        description="Requires meaningful content or reference plus a traceable origin/reference. "
                    "External origin never implies authoritativeness by itself.",
        requires_origin_traceability=True,
        authority_scope="This material originates from the identified external source; "
                         "external origin does not imply authoritativeness of its content.",
    ),
    SourceType.PROJECT_DOCUMENT: SourceContractPolicy(
        source_type=SourceType.PROJECT_DOCUMENT,
        description="Requires meaningful content or reference plus enough project/document origin to trace the "
                    "material. Never assumed current or approved.",
        requires_origin_traceability=True,
        authority_scope="This is an existing project document from the identified origin; "
                         "it is not automatically current or approved.",
    ),
    SourceType.AI_INTERPRETATION: SourceContractPolicy(
        source_type=SourceType.AI_INTERPRETATION,
        description="Requires meaningful content plus sufficient origin/model/process reference "
                    "(origin.reference, metadata['model'], or metadata['process']) so it remains identifiable as "
                    "AI-origin material. Never becomes authoritative merely by being structurally valid.",
        requires_model_traceability=True,
        authority_scope="This content was produced through AI interpretation from the identified model/process; "
                         "it never becomes authoritative merely by being structurally valid.",
    ),
    SourceType.UNRESOLVED: SourceContractPolicy(
        source_type=SourceType.UNRESOLVED,
        description="Requires explicit content explaining what is unresolved. Never coerced into another source "
                    "type merely to avoid uncertainty, and never accepted as authoritative.",
        requires_explicit_content=True,
        authority_allowed=False,
        authority_scope="",
    ),
}


class SourceContractCatalog:
    """Closed, deterministic lookup from `SourceType` to `SourceContractPolicy`."""

    @staticmethod
    def supported_types() -> frozenset[SourceType]:
        """Returns the closed set of `SourceType`s this catalog has a policy for."""
        return frozenset(SOURCE_CONTRACT_POLICIES.keys())

    @staticmethod
    def get(source_type: SourceType) -> SourceContractPolicy:
        """Returns the policy for `source_type`, failing deterministically if unregistered."""
        if not isinstance(source_type, SourceType):
            raise UnknownSourceTypeError(f"unknown_source_type:{source_type!r}")
        policy = SOURCE_CONTRACT_POLICIES.get(source_type)
        if policy is None:
            raise UnknownSourceTypeError(f"no_policy_for_source_type:{source_type}")
        return policy

    @staticmethod
    def assert_complete() -> bool:
        """Verifies every `SourceType` enum member has exactly one registered policy.

        Prevents a future `SourceType` addition from silently having no intake
        contract at all.
        """
        if set(SourceType) != SourceContractCatalog.supported_types():
            missing = set(SourceType) - SourceContractCatalog.supported_types()
            extra = SourceContractCatalog.supported_types() - set(SourceType)
            raise UnknownSourceTypeError(f"catalog_incomplete:missing={missing}:extra={extra}")
        return True
