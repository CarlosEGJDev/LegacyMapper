"""V4-R9 deterministic Technical Lead approval layer.

An `ApprovalDecision` records that the Technical Lead explicitly decided
`APPROVED`, `REJECTED`, or `CORRECTION_REQUESTED` for one R8 `Proposal` that
was `READY_FOR_REVIEW` at decision time. Recording a decision never mutates
the R8 `Proposal` it references, never resolves the `KnowledgeRelation`/
`MaterialItem`/`ClassificationRecord`/`TemporalPlacement`/`ProvenanceGraph`/
`KnowledgeStatus` it may reference, and never creates a `KnowledgeStatement`
or any canonical Knowledge Source content. `APPROVED` only makes a proposal
eligible for R10 Canonical Knowledge Composition; it does not perform that
composition. R9 records human authority — it never creates it.
"""
