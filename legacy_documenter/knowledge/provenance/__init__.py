"""V4 deterministic provenance and lineage layer.

Answers "where did this material/evidence/statement come from" via an
explicit, acyclic `ProvenanceGraph` of `ProvenanceNode`s and
`ProvenanceEdge`s. Provenance is strictly about traceability: a traceable
node is never automatically true, approved, current, authoritative, or
canonical. Those judgments belong to later V4 lifecycle stages (knowledge
classification, proposal lifecycle, Technical Lead approval, canonical
composition).
"""
