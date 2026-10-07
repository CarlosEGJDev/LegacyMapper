"""Budget composition for a single attributed partial flow; no provider imports."""
from __future__ import annotations

from copy import deepcopy
from time import perf_counter

from legacy_documenter.context.ai_projection import AiProjectionBuilder
from legacy_documenter.context.composer import PROFILES
from legacy_documenter.context.flow_segmentation import FlowSegmenter, SegmentationPolicy, SegmentationError
from legacy_documenter.llm.payload import measure_request_payload


PARTIAL_INSTRUCTION = (
    " This request contains a PARTIAL FLOW SEGMENT, never the whole parent flow. "
    "Only describe the included paths. Omitted paths are identifiers for coverage "
    "bookkeeping, not supplied evidence and must not be cited or inferred. "
    "Do not claim completeness or merge this interpretation with other segments."
)


def segment_metadata(record):
    return {key: deepcopy(record[key]) for key in (
        "parent_flow_id", "segment_id", "partial", "ordinal", "included_paths", "omitted_paths",
        "completeness", "segmentation_policy_id", "segmentation_policy", "segment_reason", "overlap_paths",
    )}


def build_segmented_context(builder, indexes, scoped, snapshot, profile, limit, request_builder, schema, ordinal=1):
    """Choose one parent and one segment; do not invoke or semantically aggregate.

    Called after the inherited reduction ladder failed, or on explicit ordinal
    selection. Metadata outside the sent segment's refs never expands grounding.
    """
    if not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal < 1:
        raise SegmentationError("INVALID_SEGMENT")
    started = perf_counter()
    # Legacy profiles determine when the complete parent no longer fits. The
    # dedicated partial contract can use the neutral input window, including
    # mandatory omitted IDs; it still gates the entire rendered payload.
    segment_characters = min(PROFILES["LARGE"][1], limit * 4)
    policy = SegmentationPolicy(max_characters=segment_characters, input_token_limit=limit)

    def package(record):
        partial = record.get("partial") is True
        body = builder.package([record], source_snapshot=snapshot,
                               profile="LARGE" if partial else profile,
                               budget={"max_characters": segment_characters} if partial else None)
        if record.get("partial"):
            body.update(contract_name="AI_SEGMENT_PROJECTION", contract_version="1.0", package_type="AI_SEGMENT_PROJECTION")
            body["statistics"]["package_completeness"] = body["statistics"]["completeness"]
            body["statistics"]["completeness"] = "PARTIAL"
            body["truncation"].update(truncated=True, omitted_parent_path_count=len(record["omitted_paths"]), continuation_policy="OTHER_EXPLICIT_PARENT_SEGMENTS")
            body["segmentation"] = segment_metadata(record)
            # Body content changed: never reuse the historical package identity.
            from hashlib import sha256
            from legacy_documenter.context.flow_segmentation import canonical
            body.pop("package_id", None)
            body["package_id"] = "AIP-" + sha256(canonical(body).encode()).hexdigest()
        request = request_builder(body)
        if record.get("partial"):
            request.system_instruction += PARTIAL_INSTRUCTION
            request.metadata["flow_segment"] = segment_metadata(record)
            request.request_id = None
            request.__post_init__()
        return body, request, measure_request_payload(request, schema)

    def fits(record):
        body, request, metrics = package(record)
        return body["statistics"]["records_included"] == 1 and metrics["payload_estimated_tokens"] <= limit

    for flow_id in dict.fromkeys(scoped):
        parent = builder.hydrator.hydrate_flow(flow_id, indexes)
        if fits(parent):
            continue
        segments = FlowSegmenter().segment(parent, policy, fits)
        if ordinal > len(segments):
            raise SegmentationError("INVALID_SEGMENT")
        chosen = segments[ordinal - 1]
        body, request, metrics = package(chosen)
        if not fits(chosen):
            raise SegmentationError("BUDGET_IMPOSSIBLE_AFTER_SEGMENTATION")
        metrics["segmentation"] = {
            **segment_metadata(chosen), "segment_count": len(segments),
            "selected_segment_count": 1, "omitted_segment_count": len(segments) - 1,
            "other_selected_flows_omitted": len(set(scoped)) - 1,
            "seconds": round(perf_counter() - started, 6),
        }
        return body, request, metrics, None
    raise SegmentationError("SEGMENTATION_NOT_NEEDED")
