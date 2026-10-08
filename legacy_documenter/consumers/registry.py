"""Immutable, deterministic registry of consumer descriptors (V5.8).

Descriptors are plain data: nothing is imported, loaded, discovered on disk or executed, and there is no network
or side effect. Adding descriptors returns a new registry; the original never changes.
"""
from __future__ import annotations

from types import MappingProxyType

from .contracts import CAPABILITY_SPECS, CONTRACT_VERSION, ConsumerCapability, ConsumerDescriptor, ConsumerError, ConsumerErrorCode

#: Consumers that exist today, expressed through the contract (V5.8 section 33: WRAP, never replace).
_BUILTIN = (
    ("builtin.evidence-reader", (ConsumerCapability.READ_EVIDENCE,)),
    ("builtin.flow-reader", (ConsumerCapability.READ_FLOW, ConsumerCapability.READ_PARTIAL_FLOW)),
    ("builtin.ai-context", (ConsumerCapability.READ_AI_CONTEXT,)),
    ("builtin.canonical-reader", (ConsumerCapability.READ_CANONICAL,)),
    ("builtin.review-history-reader", (ConsumerCapability.READ_REVIEW_HISTORY,)),
    ("builtin.human-docs", (ConsumerCapability.RENDER_HUMAN_DOC,)),
    ("builtin.json-export", (ConsumerCapability.EXPORT_JSON,)),
)


class ConsumerRegistry:
    """Maps `consumer_id` to its validated `ConsumerDescriptor`; duplicates are rejected."""

    def __init__(self, descriptors: tuple[ConsumerDescriptor, ...] = ()) -> None:
        ordered = tuple(sorted(descriptors, key=lambda d: d.consumer_id))
        by_id = {d.consumer_id: d for d in ordered}
        if len(by_id) != len(ordered):
            raise ConsumerError(ConsumerErrorCode.INVALID_DESCRIPTOR, "duplicate_consumer_id")
        self._descriptors = ordered
        self._by_id = MappingProxyType(by_id)

    def get(self, consumer_id: str) -> ConsumerDescriptor:
        """The descriptor, or UNKNOWN_CONSUMER."""
        try:
            return self._by_id[consumer_id]
        except KeyError:
            raise ConsumerError(ConsumerErrorCode.UNKNOWN_CONSUMER, "consumer_not_registered") from None

    def with_descriptors(self, *descriptors: ConsumerDescriptor) -> "ConsumerRegistry":
        """A new registry that also holds `descriptors`."""
        return ConsumerRegistry(self._descriptors + tuple(descriptors))

    def ids(self) -> tuple[str, ...]:
        """Sorted consumer ids."""
        return tuple(self._by_id)

    def to_dict(self) -> dict:
        """Stable JSON shape, sorted by consumer id."""
        return {"contract_version": CONTRACT_VERSION, "consumers": [d.to_dict() for d in self._descriptors]}

    def __len__(self) -> int:
        return len(self._descriptors)


def builtin_registry() -> ConsumerRegistry:
    """Descriptors for the wrapped consumers; kinds come from `CAPABILITY_SPECS`, so they cannot drift."""
    descriptors = []
    for consumer_id, capabilities in _BUILTIN:
        specs = [CAPABILITY_SPECS[c] for c in capabilities]
        descriptors.append(ConsumerDescriptor(
            consumer_id=consumer_id, consumer_version="1.0", contract_version=CONTRACT_VERSION,
            capabilities_required=tuple(sorted(capabilities)),
            input_kinds=tuple(sorted({k for s in specs for k in s.input_kinds})),
            output_kinds=tuple(sorted({k for s in specs for k in s.output_kinds})), read_only=True,
        ))
    return ConsumerRegistry(tuple(descriptors))
