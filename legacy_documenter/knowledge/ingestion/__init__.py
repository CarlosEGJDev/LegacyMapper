"""V4 deterministic ingestion boundary for human-supplied material.

Converts a human-authored `SourceInput` (R2) into a traceable
`MaterialItem` (R1) plus a `MATERIAL` `ProvenanceNode` (R3), without
interpreting, classifying, or approving the content. All ingested content is
treated as inert data: it is stored and sanitized, never executed, and never
obeyed as an instruction to LegacyMapper or to any development agent, even
when it reads like one.

`INGESTED_MATERIAL_IS_NOT_APPROVED_KNOWLEDGE`: submission and Technical Lead
approval are distinct lifecycle events, and this module only performs the
former.
"""
