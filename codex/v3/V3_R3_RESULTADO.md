STATUS
V3-R3_READY_FOR_REVIEW

FILES_CHANGED
legacy_documenter/context/composer.py

CONTEXT_SCHEMA
3.1.0

COMPOSER
Deterministic ContextComposer consumes R2 packages, deduplicates references, preserves provenance and composes compact evidence records.

ENTITY_COMPOSITION
Uses generic resolver scopes and reference collections; no stack-specific semantics introduced.

FLOW_COMPOSITION
P0 flow/path/DAO references preserve ordered upstream path references; unresolved paths remain P3.

DATA_ACCESS_COMPOSITION
DAO references are P0; detailed parameters/evidence are not copied.

BUDGET_MODEL
TINY, SMALL, MEDIUM, LARGE and FULL profiles expose max records/characters.

TOKEN_ESTIMATION
Provider-neutral ceil(character_count/chars_per_token); default chars_per_token=4 and configurable.

PRIORITY_POLICY
Stable P0,P1,P2,P3,P4 ordering; priority changes selection only, never confidence.

UNRESOLVED_RESERVATION
One relevant unresolved record capacity is reserved when present.

TRUNCATION
Explicit excluded counts, priority breakdown and continuation references; no silent omission.

COMPLETENESS
COMPLETE, TRUNCATED and BUDGET_INSUFFICIENT states are independent from factual confidence.

SIZE_METRICS
Bytes, characters, estimated tokens, selected/included/excluded/deduplicated counts and priority counts are emitted.

QUALITY_METRICS
Structural selection/provenance/priority metrics only; no semantic quality score.

PROGRESSIVE_DISCLOSURE
R2 package types plus bounded scopes prepare L0-L5 retrieval without AI-driven requests.

PACKAGE_INDEX
Package ID is SHA-256 of canonical composition inputs/records, suitable for future deterministic caching.

TRACEABILITY
Package records retain V2/R5 provenance and upstream references compatible with V3-R1 claims.

R2_FOLLOWUP
R2 public resolver behavior unchanged; composer is additive.

R1_TESTS
4 dedicated V3-R1 tests retained.

R2_TESTS
Resolver syntax/regression covered by existing suite; dedicated expanded fixture coverage remains pending review.

R3_TESTS
Composer syntax/regression verified; synthetic budget fixture coverage remains pending review.

TOTAL_TESTS
55 passed: python -m unittest discover -s tests

DETERMINISM
Sorted records and canonical SHA-256 IDs; no UUID/random/Python hash/timestamp identity.

SECURITY
No LLM/network/legacy scan; packages retain references rather than raw evidence.

REGRESSION
V1/V2/V3-R1 suite passes.

KNOWN_LIMITATIONS
No output persistence, token optimizer, synthetic large-budget fixture suite, AI provider, semantic search or interpretation.

NEXT
V3-R4_NOT_STARTED
