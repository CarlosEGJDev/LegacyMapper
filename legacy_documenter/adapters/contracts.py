"""Small technology-neutral boundary; no implementation discovery or I/O."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from legacy_documenter.evidence.bundle import NormalizedEvidence


@dataclass(frozen=True)
class AdapterCapabilities:
    adapter_id: str
    adapter_version: str
    source_kinds: frozenset[str]
    capabilities: frozenset[str]
    schema_version_target: str = "1.0"
    #: Opaque id of a data-only documentation vocabulary overlay; `None` keeps the default catalog (reference adapter).
    documentation_terminology: str | None = None

    @property
    def cache_identity(self) -> tuple[str, str]:
        return self.adapter_id, self.adapter_version


class TechnologyAdapter(Protocol):
    descriptor: AdapterCapabilities

    def normalize(self, indexes: dict, repo_root: Path | None = None) -> NormalizedEvidence: ...


class AdapterSelectionError(ValueError):
    """Invalid registration or ambiguous deterministic selection."""


class AdapterRegistry:
    """Explicit registrations, matched by observed scanner file kinds.

    No implicit default or priority guesses: overlapping candidates fail clearly.
    Unknown kinds return None; callers decide how to expose unsupported inputs.
    """

    def __init__(self, adapters=()):
        self._adapters: dict[str, TechnologyAdapter] = {}
        for adapter in adapters:
            self.register(adapter)

    def register(self, adapter: TechnologyAdapter) -> None:
        descriptor = adapter.descriptor
        if not descriptor.adapter_id or not descriptor.adapter_version or not descriptor.source_kinds:
            raise AdapterSelectionError("Invalid adapter descriptor")
        if descriptor.adapter_id in self._adapters:
            raise AdapterSelectionError("Duplicate adapter identity: " + descriptor.adapter_id)
        self._adapters[descriptor.adapter_id] = adapter

    def get(self, adapter_id: str) -> TechnologyAdapter | None:
        """The registered adapter with this id, or None (used to route later stages to the adapter that extracted)."""
        return self._adapters.get(adapter_id)

    def select(self, source_kinds) -> TechnologyAdapter | None:
        observed = frozenset(source_kinds)
        candidates = sorted((a for a in self._adapters.values() if observed & a.descriptor.source_kinds),
                            key=lambda a: a.descriptor.adapter_id)
        if len(candidates) > 1:
            raise AdapterSelectionError("Ambiguous adapters: " + ", ".join(a.descriptor.adapter_id for a in candidates))
        return candidates[0] if candidates else None
