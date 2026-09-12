STATUS
V3-R2_READY_FOR_REVIEW

FILES_CHANGED
legacy_documenter/context/resolver.py

CONTEXT_SCHEMA_VERSION
3.1.0

PACKAGE_TYPES
SYSTEM FUNCTIONAL TECHNICAL ENTITY FLOW DATA_ACCESS

LOADER
Read-only deterministic JSON loader for SYSTEM_CONTEXT, FUNCTIONAL_FLOWS and TRACEABILITY; missing artifacts fail explicitly.

RESOLUTION
Exact normalized ID lookup returns FOUND, NOT_FOUND or AMBIGUOUS with candidates; no semantic guessing.

EXPANSION
Bounded deterministic flow/path selection with explicit expansion_depth and record limits.

AMBIGUITY
Structured candidates retained; no silent selection.

PRIORITY_POLICY
P0/P1/P2/P3/P4 serialized as selection priority only; no confidence mutation.

FUNCTIONAL_PACKAGE
Compact flow/path, DAO, evidence and unresolved references; no module/business semantics.

TECHNICAL_PACKAGE
Compact generic system/flow references; no pattern/layer declaration.

SYSTEM_PACKAGE
Summary-oriented package based on approved source snapshot metadata.

UNRESOLVED
Unresolved terminal path IDs preserved without target guessing.

PROVENANCE
Every package records artifact references and source snapshot SHA-256.

REFERENCE_CLOSURE
Internal path/flow references are selected from loaded R5 artifacts; external evidence references are explicit upstream references.

COMPACTION
Packages contain IDs/counts/references, not copied calls/graph/evidence bodies.

TRUNCATION
Deterministic flow limits set truncated state and reason; no silent omission.

V3_R1_COMPATIBILITY
Package source/evidence references are compatible with V3-R1 DocumentClaim evidence citations.

V4_COMPATIBILITY
Schema requires generic references only; no VB/WebForms/Oracle field is mandatory.

TESTS
python -m py_compile legacy_documenter/context/resolver.py
python -m unittest discover -s tests
55 passed

DETERMINISM
Canonical JSON SHA-256 package identity; sorted collections; no UUID/Python hash/timestamp identity.

SECURITY
Read-only sanitized V2/R5 artifact references; no network, LLM or legacy scan.

REGRESSION
Existing suite passes; V1/V2/V3-R1 code paths unchanged.

KNOWN_LIMITATIONS
No token budgeting, semantic search, AI generation, output persistence or external-information workflow. Targeted ENTITY/DATA_ACCESS resolution currently returns compact generic references pending V3-R3 package composition.

NEXT
V3-R3_NOT_STARTED
