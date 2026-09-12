TASK=V3-R3_2_FINAL_COVERAGE_CORRECTION

MODE=TEST_AND_DEFECT_FIX_ONLY

NO_NEW_FEATURES
NO_ARCHITECTURE_REDESIGN
NO_LLM
NO_NETWORK
NO_LEGACY_SCAN
NO_V3_R4

OBJECTIVE

Close ONLY the mandatory gaps explicitly reported by V3-R3.1.

Current baseline:

* 63 tests PASS.
* R2/R3 implementation exists.
* Synthetic budget fixture exists.
* Budget ordering FULL > LARGE > MEDIUM > SMALL > TINY already demonstrated.

Do not redo already passing coverage.

PASS requires every gap below to be implemented and tested.

==================================================
GAP 1 — AMBIGUOUS NORMALIZED LOOKUP
===================================

Add explicit fixture/case where normalized lookup maps to multiple candidates.

Assert:

status == AMBIGUOUS
candidate count > 1
candidate ordering deterministic
no candidate silently selected

==================================================
GAP 2 — TARGETED ENTITY COMPOSITION
===================================

Add explicit targeted composition tests for:

PROJECT
UI / COMPONENT
METHOD
DATA_OPERATION / DAO
STORED_PROCEDURE

For each supported fixture assert:

identity retained
entity type retained
direct refs retained
provenance retained
source_snapshot retained
no semantic interpretation introduced

Where relationship exists, assert relevant:

flow refs
path refs
caller refs
data access refs
SP refs
project/component refs

Do not require unsupported evidence.

==================================================
GAP 3 — DATA ACCESS DETAIL
==========================

Explicitly test:

DAO -> caller
DAO -> flow
DAO -> path
DAO -> stored procedure
DAO -> SQL where fixture supports it

Add compact parameter-reference case.

Assert parameter metadata is referenced/compacted and complete raw evidence bodies are not duplicated.

==================================================
GAP 4 — INDEPENDENT LIMITS
==========================

Each limit MUST have its own directed test.

Test separately:

max_estimated_tokens
max_flows
max_paths
max_entities
max_unresolved
max_evidence_refs

Existing max_records/max_characters coverage may be reused if already explicit.

For every constrained case assert:

limit enforced
truncated/completeness state correct
excluded count reported
no silent omission

==================================================
GAP 5 — PRIORITY P1/P2
======================

Extend synthetic fixture with explicit:

P0
P1
P2
P3
P4

Under constrained budget assert selection order:

P0 before P1
P1 before P2
P2 according to policy before lower optional evidence
P4 last

Also assert:

priority does not alter factual confidence
stable ordering within same priority

==================================================
GAP 6 — BUDGET_INSUFFICIENT P0
==============================

Add explicit assertion that mandatory P0 records are NOT silently removed when mandatory context exceeds budget.

Assert:

completeness == BUDGET_INSUFFICIENT
mandatory P0 retained
minimum_required_characters present
minimum estimate >= actual mandatory requirement
confidence unchanged

==================================================
GAP 7 — CONFIGURABLE TOKEN FORMULA
==================================

Existing default formula already passes.

Add explicit test:

chars_per_token = configurable non-default value

Assert exactly:

estimated_tokens == ceil(character_count / chars_per_token)

Also verify deterministic repetition.

==================================================
GAP 8 — COMPLETE METRICS
========================

Add explicit assertions for every required metric:

package_bytes
character_count
estimated_tokens
records_selected
records_included
records_excluded
deduplicated_records
counts_by_priority
counts_by_category

confirmed_reference_count
unresolved_reference_count
traceability_reference_count
flow_count
data_access_count
entity_count
coverage_by_priority

Use deterministic fixture with known expected counts.

Do not introduce semantic quality score.

==================================================
GAP 9 — SECURITY
================

Add explicit fixture containing representative sensitive/raw-looking values.

Verify composer/resolver does NOT rehydrate or expose credentials/secrets.

Test at minimum patterns representing:

password
connection-string credential
token/API-key-like value

Assertions:

no secret appears in composed serialized output
sanitized/reference representation retained where applicable
no network
no external calls

Do not weaken existing sanitization.

==================================================
GAP 10 — COMPLETE TRACEABILITY
==============================

Add directed traceability round-trip fixture covering:

DocumentClaim-compatible reference
-> ContextPackage
-> ENTITY/FLOW reference
-> DAO/data operation
-> StoredProcedure OR SQL
-> V2 upstream reference
-> source_snapshot

Assert every hop is resolvable by ID/ref.

Also verify:

one-to-many evidence refs preserved
compaction does not break IDs
raw evidence body not required

==================================================
GAP 11 — REGRESSION
===================

Run full suite:

python -m unittest discover -s tests

All PASS.

The final test count MUST be greater than 63.

Do not report completion merely because inherited tests pass.

==================================================
PRODUCTION CODE
===============

Prefer test-only changes.

Modify production code ONLY when one of the directed tests exposes an actual defect.

Allowed only if necessary:

legacy_documenter/context/resolver.py
legacy_documenter/context/composer.py

For every production change report:

DEFECT
CAUSE
MINIMAL_FIX
REGRESSION_TEST

No unrelated refactor.

==================================================
ACCEPTANCE
==========

READY only if ALL are true:

* ambiguous normalized lookup tested
* PROJECT composition tested
* UI/component composition tested
* METHOD composition tested
* DAO/data operation composition tested
* SP composition tested
* compact parameter refs tested
* independent token/flow/path/entity/unresolved/evidence limits tested
* P1/P2 priority tested
* mandatory P0 BUDGET_INSUFFICIENT behavior tested
* configurable token formula tested explicitly
* all required metrics asserted
* sanitizer/credential tests pass
* full traceability chain passes
* total suite > 63
* all tests PASS

If ANY item missing:

STATUS=V3-R3_2_REQUIRES_CORRECTION

Do not proceed to R4.

==================================================
REPORT
======

Create ONLY:

codex/V3/V3_R3_2_RESULTADO.md

Compact machine-oriented format:

STATUS
FILES_CHANGED
PRODUCTION_FIXES
AMBIGUOUS_LOOKUP
ENTITY_PROJECT
ENTITY_UI_COMPONENT
ENTITY_METHOD
ENTITY_DATA_OPERATION
ENTITY_STORED_PROCEDURE
DATA_ACCESS_TRACE
PARAMETER_COMPACTION
INDEPENDENT_LIMITS
P1_P2_PRIORITY
BUDGET_INSUFFICIENT_P0
TOKEN_FORMULA
METRICS
SECURITY
FULL_TRACEABILITY
PREVIOUS_TEST_COUNT
NEW_TEST_COUNT
TOTAL_TESTS
REGRESSION
REMAINING_GAPS
DECISION
NEXT

Successful expected result:

STATUS=V3-R3_2_READY_FOR_REVIEW
REMAINING_GAPS=NONE
DECISION=R2_R3_TEST_DEBT_CLOSED
NEXT=V3-R4_NOT_STARTED

Stop.