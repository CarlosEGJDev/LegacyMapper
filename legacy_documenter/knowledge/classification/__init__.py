"""V4 deterministic knowledge-classification layer (V4-R5).

Records what `KnowledgeNature` (R1's existing, unmodified 17-value taxonomy)
an already-ingested `MaterialItem` (R4) represents, without inferring
meaning from prose, without auto-mapping `SourceType` to `KnowledgeNature`,
and without promoting material into approved or canonical knowledge.

`SOURCE_TYPE_IS_NOT_KNOWLEDGE_NATURE`: where material came from and what
semantic category it represents are independent dimensions.
`CLASSIFIED_IS_NOT_APPROVED_KNOWLEDGE`: classification is pre-approval, a
distinct lifecycle event from Technical Lead approval (R9).
"""
