"""V4 deterministic AS_IS/TO_BE temporal-separation layer (V4-R6).

Organizes already-ingested `MaterialItem`s (R4), optionally correlated with
R5 `ClassificationRecord`s, into one of four temporal buckets derived
structurally from the material's own, already-supplied
`TemporalState` — never inferred from prose, `SourceType`,
`KnowledgeNature`, provenance origin, or dates.

`TEMPORAL_STATE_IS_NOT_TRUTH`, `TEMPORAL_STATE_IS_NOT_APPROVAL`: `AS_IS` is
not "confirmed current truth," `TO_BE` is not "approved future design,"
`HISTORICAL` is not "obsolete," and an unspecified temporal state is not an
error. Separating `AS_IS` from `TO_BE` material is not conflict/gap
detection — that is R7's responsibility.
"""
