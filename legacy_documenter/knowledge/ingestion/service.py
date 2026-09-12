"""Deterministic human-supplied material ingestion service (V4-R4).

Pipeline: `SourceInput` -> R2 validation/normalization -> R1 `MaterialItem`
-> R3 `MATERIAL` `ProvenanceNode`. No step interprets, classifies, or
approves content; no step performs file, network, or provider I/O.

Explicit source-type scope: `DETERMINISTIC_CODE_FACT` belongs to the
deterministic code pipeline and `AI_INTERPRETATION` is not human-supplied
material, even though both would otherwise satisfy R2's structural contract.
The public human-ingestion boundary rejects both before R2 validation runs,
so the rejection reason is "not human-supplied," not an incidental R2
traceability failure.
"""
from dataclasses import replace

from legacy_documenter.knowledge.domain.enums import SourceType
from legacy_documenter.knowledge.domain.models import DomainValidationError, MaterialItem, Origin, new_material_id
from legacy_documenter.knowledge.ingestion.models import (
    IngestedMaterial,
    IngestionBatchResult,
    IngestionRejectedError,
    IngestionRejection,
)
from legacy_documenter.knowledge.input.contracts import SourceInput, SourceInputValidationError
from legacy_documenter.knowledge.input.catalog import UnknownSourceTypeError
from legacy_documenter.knowledge.input.validator import validate_source_input
from legacy_documenter.knowledge.provenance.enums import LineageCompleteness
from legacy_documenter.knowledge.provenance.graph import ProvenanceGraph, material_node_from_source_input
from legacy_documenter.knowledge.provenance.models import ProvenanceValidationError, normalize_node
from legacy_documenter.utils.sanitizer import sanitize_text

HUMAN_SUPPLIED_SOURCE_TYPES: frozenset[SourceType] = frozenset({
    SourceType.HUMAN_REQUIREMENT,
    SourceType.USER_STORY,
    SourceType.BUSINESS_REQUIREMENT,
    SourceType.BUSINESS_CONTEXT,
    SourceType.TECHNICAL_CONSTRAINT,
    SourceType.CORPORATE_STANDARD,
    SourceType.APPROVED_DECISION,
    SourceType.EXTERNAL_DOCUMENT,
    SourceType.PROJECT_DOCUMENT,
    SourceType.UNRESOLVED,
})
"""The closed set of `SourceType`s the public human-ingestion boundary accepts.

Deliberately excludes `DETERMINISTIC_CODE_FACT` (the deterministic code
pipeline's source type) and `AI_INTERPRETATION` (never human-supplied,
regardless of how its payload reads).
"""


def _sanitize_origin(origin: Origin | None) -> Origin | None:
    """Returns a sanitized copy of `origin`; R1's `Origin` itself is never modified."""
    if origin is None:
        return None
    return replace(
        origin,
        kind=sanitize_text(origin.kind),
        reference=sanitize_text(origin.reference) if origin.reference else origin.reference,
        contributor=sanitize_text(origin.contributor) if origin.contributor else origin.contributor,
    )


def _completeness_for(validated: SourceInput) -> LineageCompleteness:
    """Determines ingestion-lineage completeness from explicitly available provenance only.

    An identified origin (one carrying a `reference` or a `contributor`, not
    merely a bare `kind`) makes the material's own lineage `COMPLETE` for what
    this ingestion step represents. A bare origin or a standalone `reference`
    is `PARTIAL`: something is known, but not enough to fully identify where
    the material came from. Nothing supplied at all is `UNRESOLVED`. This
    never claims the *content* is complete, true, or approved — only that its
    declared origin is (or is not) resolvable.
    """
    origin = validated.origin
    if origin is not None and (origin.reference or origin.contributor):
        return LineageCompleteness.COMPLETE
    if origin is not None or validated.reference:
        return LineageCompleteness.PARTIAL
    return LineageCompleteness.UNRESOLVED


class HumanMaterialIngestionService:
    """Deterministic boundary that turns human-supplied `SourceInput` into traceable material.

    Stateless except for `ingest_batch`'s shared `ProvenanceGraph`, which
    exists only to demonstrate deterministic exact-duplicate handling across
    one batch (R3's `add_node` already treats an identical duplicate as an
    idempotent no-op); it is not a persistence layer.
    """

    def ingest(self, source_input: SourceInput) -> IngestedMaterial:
        """Ingests one `SourceInput`, returning its `MaterialItem` and `MATERIAL` provenance node.

        Raises `IngestionRejectedError` if `source_input.source_type` is
        outside `HUMAN_SUPPLIED_SOURCE_TYPES`, or if R2 validation rejects the
        input. R2's own rules are never weakened or bypassed.
        """
        self._assert_human_supplied_scope(source_input)
        validated = self._validate(source_input)

        material_id = new_material_id(
            validated.source_type.value, validated.content, validated.reference, validated.title
        )
        sanitized_origin = _sanitize_origin(validated.origin)
        material = MaterialItem(
            material_id=material_id,
            source_type=validated.source_type,
            title=validated.title,
            content=validated.content,
            reference=validated.reference,
            origin=sanitized_origin,
            metadata=validated.metadata,
            temporal_state=validated.temporal_state,
        )
        try:
            material.validate()
        except DomainValidationError as exc:
            raise IngestionRejectedError(str(exc)) from exc

        raw_node = material_node_from_source_input(replace(validated, origin=sanitized_origin), node_id=material_id)
        raw_node = replace(raw_node, provenance_status=_completeness_for(validated))
        try:
            node = normalize_node(raw_node)
        except ProvenanceValidationError as exc:
            raise IngestionRejectedError(str(exc)) from exc

        return IngestedMaterial(material=material, provenance_node=node)

    def ingest_batch(self, source_inputs: list[SourceInput]) -> IngestionBatchResult:
        """Ingests each item independently, isolating failures.

        One invalid item never removes a valid item from `accepted`; both
        lists preserve the original input order. All accepted items share one
        `ProvenanceGraph` so that an exact normalized duplicate across the
        batch is handled by R3's documented idempotent-duplicate-node policy
        rather than a second, R4-specific deduplication mechanism.
        """
        result = IngestionBatchResult()
        graph = ProvenanceGraph()
        for index, source_input in enumerate(source_inputs):
            try:
                ingested = self.ingest(source_input)
            except (IngestionRejectedError, SourceInputValidationError, UnknownSourceTypeError) as exc:
                result.rejected.append(IngestionRejection(index=index, reason=sanitize_text(str(exc))))
                continue
            graph.add_node(ingested.provenance_node)
            result.accepted.append(ingested)
        return result

    def _assert_human_supplied_scope(self, source_input: SourceInput) -> None:
        source_type = source_input.source_type
        if not isinstance(source_type, SourceType):
            raise IngestionRejectedError(f"invalid_source_type:{source_type!r}")
        if source_type not in HUMAN_SUPPLIED_SOURCE_TYPES:
            raise IngestionRejectedError(f"source_type_not_human_supplied:{source_type.value}")

    def _validate(self, source_input: SourceInput) -> SourceInput:
        try:
            return validate_source_input(source_input)
        except (SourceInputValidationError, UnknownSourceTypeError) as exc:
            raise IngestionRejectedError(sanitize_text(str(exc))) from exc
