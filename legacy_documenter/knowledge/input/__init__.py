"""V4 deterministic input/source contract layer.

Validates, normalizes and sanitizes raw material for every V4 `SourceType`
before it becomes a `legacy_documenter.knowledge.domain.models.MaterialItem`.
A valid `SourceInput` means only that LegacyMapper can safely and
deterministically understand the supplied material as an input of its
declared source type — it is not approval, and it is not proof that the
material is true, implemented, or belongs in canonical knowledge. Those
decisions belong to later V4 lifecycle stages (provenance, classification,
proposal, Technical Lead approval).
"""
