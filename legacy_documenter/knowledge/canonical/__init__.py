"""V4-R10 Canonical Knowledge Composition boundary.

This package composes an already-approved R8 `Proposal` + R9
`ApprovalDecision(APPROVED, TECHNICAL_LEAD)` pair into one immutable
`CanonicalKnowledgeEntry`, stored in the single logical Canonical Knowledge
Source (`CanonicalKnowledgeCollection`).

R10 boundary:

* `ELIGIBLE != COMPOSED`. R9 eligibility (`is_eligible_for_canonical_composition`)
  is necessary but not sufficient; composition still validates every
  structural invariant explicitly.
* Composing a canonical entry never mutates the source `Proposal`,
  `ApprovalDecision`, `KnowledgeRelation`, `MaterialItem`,
  `ClassificationRecord`, `TemporalPlacement`, or `ProvenanceGraph`.
* `KnowledgeStatus` is never replaced or upgraded by an approval decision;
  the caller supplies it explicitly, and this module still enforces R1's own
  evidence invariants for that status (for example `CONFIRMED` requiring at
  least one authoritative `EvidenceRef`).
* No automatic supersession, conflict resolution, or gap resolution occurs
  anywhere in this package.
* This package produces the Canonical Knowledge Source only. It never
  generates R11 human-readable documentation or R12 Plugin-facing payloads.
* Zero LLM/provider calls occur anywhere in this package.
"""
