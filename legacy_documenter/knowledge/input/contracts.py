"""Source-neutral raw input representation for the V4 input/source contract layer.

`SourceInput` is the pre-`MaterialItem` payload a caller supplies: content or a
reference, optional origin/contributor/title/temporal-state/authority
declarations, and free-form JSON-compatible metadata. It never requires a
filesystem path, a code symbol, a project, a language, a framework, or a
technology to be constructed; code-specific traceability is enforced only for
`SourceType.DETERMINISTIC_CODE_FACT`, in `catalog.py`/`validator.py`.
"""
from dataclasses import dataclass, field

from legacy_documenter.documentation.contracts import stable_id
from legacy_documenter.knowledge.domain.enums import SourceType, TemporalState
from legacy_documenter.knowledge.domain.models import Origin


class SourceInputValidationError(ValueError):
    """Raised when a `SourceInput` violates its deterministic source contract.

    Never raised to repair, promote or downgrade a value silently: invalid
    input is rejected, not fixed.
    """


@dataclass
class SourceInput:
    """Represents one unit of raw material offered to LegacyMapper as an input.

    `content` and `reference` are both optional individually; at least one
    non-blank value between them must survive normalization for the input to
    be meaningful. `authoritative` and `authority_scope` follow the R2 scoped-
    authority rule: `authoritative=True` only ever claims what the declared
    `source_type` is qualified to establish (see `catalog.SOURCE_CONTRACT_POLICIES`
    for each type's `authority_scope` text), never a broader truth.
    """

    source_type: SourceType
    content: str | None = None
    reference: str | None = None
    origin: Origin | None = None
    contributor: str | None = None
    title: str | None = None
    temporal_state: TemporalState | None = None
    authoritative: bool = False
    authority_scope: str | None = None
    metadata: dict = field(default_factory=dict)


def new_source_input_id(source_input: SourceInput) -> str:
    """Derives a stable `SRC-` id from a validated/normalized `SourceInput`.

    Reuses the existing V3 `stable_id` hashing contract instead of inventing a
    second identity scheme. Two equivalently normalized inputs (same source
    type, content, reference and title) always produce the same id; the id
    never depends on current time, randomness, or object identity.
    """
    return stable_id(
        "SRC",
        source_input.source_type.value,
        source_input.content,
        source_input.reference,
        source_input.title,
    )
