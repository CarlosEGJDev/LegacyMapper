"""Deterministic partial projections of hydrated flows; never new Evidence.

Whole deduplicated path groups are atomic: their original path IDs and refs
stay together. No overlap or intra-path fragmentation. Budget-specific
serialization belongs to the caller's neutral fit predicate.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
import hashlib
import json

from .ai_projection import record_reference_ids, _reject_interpreted_content
from .hydration import EvidenceHydrator


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class SegmentationError(ValueError):
    """Closed error codes only, without source/request/exception text."""

    def __init__(self, code):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class SegmentationPolicy:
    version: str = "flow-segmentation-v1"
    max_characters: int = 16000
    input_token_limit: int = 16000
    ordering: str = "PATH_ID_ASCENDING"
    overlap: str = "NONE"
    oversized_path: str = "FAIL_EXPLICITLY_NO_FRAGMENTATION"

    def __post_init__(self):
        if not self.version or any(not isinstance(n, int) or isinstance(n, bool) or n <= 0 for n in (self.max_characters, self.input_token_limit)):
            raise SegmentationError("INVALID_SEGMENTATION_POLICY")
        if self.ordering != "PATH_ID_ASCENDING" or self.overlap != "NONE" or self.oversized_path != "FAIL_EXPLICITLY_NO_FRAGMENTATION":
            raise SegmentationError("INVALID_SEGMENTATION_POLICY")

    @property
    def identity(self):
        return "SEGPOL-" + hashlib.sha256(canonical(asdict(self)).encode()).hexdigest()


def _paths(parent):
    if not isinstance(parent.get("flow_id"), str) or not parent["flow_id"] or parent.get("partial") or parent.get("segment_id"):
        raise SegmentationError("INVALID_PARENT_FLOW")
    paths = parent.get("paths")
    if not isinstance(paths, list) or not paths or not isinstance(parent.get("provenance"), dict):
        raise SegmentationError("INCOMPLETE_PROVENANCE")
    if any(not isinstance(p, dict) or not isinstance(p.get("path_ids"), list) for p in paths):
        raise SegmentationError("INCOMPLETE_PROVENANCE")
    ids = [pid for p in paths for pid in p.get("path_ids", [])]
    if any(not p.get("path_ids") for p in paths) or any(not isinstance(pid, str) or not pid for pid in ids) or len(set(ids)) != len(ids):
        raise SegmentationError("INCOMPLETE_PROVENANCE")
    _reject_interpreted_content(parent)
    if any(not isinstance(p.get("path_provenance"), list)
           or any(not isinstance(v, dict) for v in p["path_provenance"])
           or {v.get("path_id") for v in p["path_provenance"]} != set(p["path_ids"]) for p in paths):
        raise SegmentationError("INCOMPLETE_PROVENANCE")
    return sorted(paths, key=lambda p: tuple(sorted(p["path_ids"])))


def _segment_id(parent_id, policy_id, included, ordinal):
    return "SEG-" + hashlib.sha256(canonical([parent_id, policy_id, included, ordinal]).encode()).hexdigest()


def _project(parent, paths, all_ids, policy, ordinal):
    included = sorted(pid for path in paths for pid in path["path_ids"])
    selected = set(included)
    omitted = [pid for pid in all_ids if pid not in selected]
    if not included or not omitted:
        raise SegmentationError("INVALID_SEGMENT")
    # Copy only selected paths; avoid copying the full parent for each candidate.
    record = {key: deepcopy(value) for key, value in parent.items() if key not in {
        "paths", "terminals", "transactions", "data_operations", "parameters", "unresolved", "selection"
    }}
    record["paths"] = deepcopy(paths)
    hydrator = EvidenceHydrator()
    record["terminals"] = hydrator._terminals(record["paths"])
    record["transactions"] = hydrator._transactions(record["paths"])
    record["data_operations"] = hydrator._data_operations(record["paths"])
    callers = {node.get("caller") for path in paths for node in path.get("nodes", [])}
    record["parameters"] = deepcopy([p for p in parent.get("parameters", []) if p.get("caller") in callers])
    record["unresolved"] = [pid for pid in parent.get("unresolved", []) if pid in selected]
    record["selection"] = {
        "input_path_count": len(all_ids), "output_path_count": len(paths),
        "included_original_path_count": len(included), "omitted_original_path_count": len(omitted),
        "priority_policy": policy.ordering,
    }
    record.update(
        parent_flow_id=parent["flow_id"], partial=True,
        segment_id=_segment_id(parent["flow_id"], policy.identity, included, ordinal), ordinal=ordinal,
        included_paths=included, omitted_paths=omitted, completeness="PARTIAL",
        segmentation_policy=asdict(policy), segmentation_policy_id=policy.identity,
        segment_reason="PARENT_EXCEEDS_CONSUMER_BUDGET", overlap_paths=[],
    )
    record["evidence_refs"] = sorted(record_reference_ids(record))
    record["provenance"]["parent_flow_id"] = parent["flow_id"]
    record["provenance"]["included_path_provenance"] = [
        deepcopy(p) for path in paths for p in path.get("path_provenance", [])
    ]
    return record


def validate_segment(segment, parent, policy):
    """Validate exact projection content, not only a subset of identifiers."""
    paths = _paths(parent)
    if segment.get("partial") is not True:
        raise SegmentationError("INVALID_SEGMENT")
    all_ids = sorted(pid for path in paths for pid in path["path_ids"])
    included = segment.get("included_paths")
    if not isinstance(included, list) or not included or len(set(included)) != len(included):
        raise SegmentationError("INVALID_SEGMENT")
    ordinal = segment.get("ordinal")
    if not isinstance(ordinal, int) or isinstance(ordinal, bool) or not 1 <= ordinal <= len(paths):
        raise SegmentationError("INVALID_SEGMENT")
    chosen = [path for path in paths if set(path["path_ids"]) <= set(included)]
    if sorted(pid for path in chosen for pid in path["path_ids"]) != sorted(included):
        raise SegmentationError("INCOMPLETE_PROVENANCE")
    expected = _project(parent, chosen, all_ids, policy, ordinal)
    if segment != expected:
        raise SegmentationError("INVALID_SEGMENT")


class FlowSegmenter:
    """Greedy ordered partitions with binary search, no per-path prefix rescans.

    Emitting omitted IDs costs O(paths * segments) by the required contract.
    Fit trials use binary search rather than reserializing every growing prefix.
    A failed atomic path aborts the entire plan; nothing is silently dropped.
    """

    def segment(self, parent, policy=None, fits=None):
        policy = policy or SegmentationPolicy()
        fits = fits or (lambda record: len(canonical(record)) <= policy.max_characters)
        paths = _paths(parent)
        if fits(parent):
            return []
        if len(paths) < 2:
            raise SegmentationError("SINGLE_PATH_OVERSIZED")
        all_ids = sorted(pid for path in paths for pid in path["path_ids"])
        result = []
        cursor = 0
        while cursor < len(paths):
            ordinal = len(result) + 1
            # A partial segment must omit at least one parent path (V5.0 R3).
            upper = len(paths) if cursor else len(paths) - 1
            smallest = _project(parent, paths[cursor:cursor + 1], all_ids, policy, ordinal)
            if not fits(smallest):
                code = "SINGLE_PATH_OVERSIZED" if len(canonical(paths[cursor])) > policy.max_characters else "BUDGET_IMPOSSIBLE_AFTER_SEGMENTATION"
                raise SegmentationError(code)
            low, high = cursor + 1, upper
            while low < high:
                middle = (low + high + 1) // 2
                candidate = _project(parent, paths[cursor:middle], all_ids, policy, ordinal)
                if fits(candidate):
                    low = middle
                else:
                    high = middle - 1
            result.append(_project(parent, paths[cursor:low], all_ids, policy, ordinal))
            cursor = low
        return result
