TASK: Validate LegacyMapper V2-R4.1 corrective revision against the full real repository.

VALIDATION ONLY.

DO NOT modify code.
DO NOT start V2-R5.
DO NOT regenerate outputs unless required only to verify determinism.
DO NOT change approved V1/R1.1/R2/R3.1/R4 semantics.

SOURCE REPORTS:

* `codex/V2/V2_R4_VALIDACION_REAL.md`
* `codex/V2/V2_R4_1_RESULTADO.md`

PRIMARY INPUT:

* `output/v2_r4_1_full/`

PREVIOUS R4 DEFECTS:

HIGH:

* duplicate_path_ids=12
* distinct logical paths shared stable path IDs.

MEDIUM:

* approved R1.1 calls_total=230355
* R4 calls_total=230356
* unexplained +1 unresolved call.

GOAL:

Determine whether R4.1 fixes the path-ID defect, explains/reconciles the call-count difference, preserves R4 functional behavior and is reliable enough to authorize V2-R5.

==================================================

1. TEST / IMPLEMENTATION STATUS
   ==================================================

Read:

`codex/V2/V2_R4_1_RESULTADO.md`

Confirm:

* all tests PASS
* collision fix implemented
* collision guard implemented
* no R5 implementation
* full real output exists

Report exact test count.

==================================================
2. PATH ID GLOBAL VALIDATION
============================

Analyze all:

`output/v2_r4_1_full/index/functional_paths.json`

Calculate:

* total_paths
* unique_path_ids
* duplicate_path_ids
* duplicate_logical_paths

REQUIRED:

duplicate_path_ids=0
duplicate_logical_paths=0

For every path_id verify that exactly one canonical logical path is represented.

FAIL HIGH if any distinct logical paths still share an ID.

==================================================
3. PATH ID DETERMINISM
======================

Verify implementation uses canonical deterministic path identity.

Identity must materially distinguish:

* entry_point_id
* ordered node sequence
* ordered relation/edge sequence where applicable
* terminal_type
* terminal_target

Confirm:

* no random UUID
* no timestamp
* no Python `hash()`
* no ordering-dependent unstable input
* cryptographic/stable digest used
* sufficient digest length

If possible using existing outputs/tests, verify identical logical input reproduces identical ID.

RESULT:
PASS
FAIL

==================================================
4. COLLISION GUARD
==================

Inspect implementation/tests.

Verify:

same canonical path + same ID
-> legitimate dedup

different canonical path + same ID
-> cannot silently overwrite/merge

Report collision handling.

Silent collision merging = HIGH.

==================================================
5. PATH PRESERVATION
====================

Compare R4.1 against previous R4 validation where possible.

Previous R4:

total_flows=12642
total_paths=170020
paths_to_stored_procedure=1121
paths_to_sql=1
paths_to_data_operation=4612
unresolved_boundaries=162914
dead_end_paths=1372
cross_project_flows=2187
max_observed_depth=6
average_path_depth=1.3
duplicate_logical_paths=0

R4.1 should preserve functional semantics.

Path IDs may change.

Investigate material differences.

Do NOT require exact counts if the reconciled +1 upstream call legitimately changes a derived count.

Classify differences:
EXPECTED
EXPLAINED
SUSPICIOUS
REGRESSION

==================================================
6. FLOW ROOTS
=============

Verify:

* total confirmed R2 roots represented
* entry_point_id resolution
* handler/start method resolution
* no root merging caused by ID changes

Expected prior R4:
entry_points_with_flows=12642
total_flows=12642

Report deviations.

==================================================
7. CALL TRAVERSAL REGRESSION
============================

Verify all R4.1 confirmed Method -> Method traversal edges exist as confirmed upstream calls.

Calculate:

* confirmed traversed edges
* missing upstream edges
* unresolved calls traversed as confirmed
* inferred/name-only traversal

REQUIRED:

missing_upstream_edges=0
unresolved_calls_traversed_as_confirmed=0
inferred/name_only=0

Any systematic violation = HIGH/CRITICAL.

==================================================
8. CALL COUNT RECONCILIATION
============================

Previous approved historical baseline:

calls_total=230355
confirmed=12775
unresolved=217580

Previous R4 real output:

calls_total=230356
confirmed=12775
unresolved=217581

Validate R4.1 investigation.

Identify/explain the additional unresolved call where deterministically possible.

Report:

* current calls_total
* current confirmed
* current unresolved
* additional call identity/evidence if available
* root cause

Classify root cause:

SOURCE_SNAPSHOT_DIFFERENCE
ENVIRONMENT_DIFFERENCE
OUTPUT_CONTAMINATION
UPSTREAM_CODE_REGRESSION
DEDUP_DIFFERENCE
OTHER_EXPLAINED
UNEXPLAINED

IMPORTANT:

Do NOT modify upstream extraction to force historical count.

If source snapshot changed between machines/runs and evidence supports this, accept the count difference as environmental/source variation.

If R4/R4.1 altered upstream extraction semantics, classify HIGH regression.

==================================================
9. DB TERMINALS
===============

Verify R4.1 preserves terminal resolution.

Calculate:

* paths_to_stored_procedure
* paths_to_sql
* paths_to_data_operation
* unique_terminal_stored_procedures
* unique_terminal_sql_operations
* broken_terminal_ids
* broken_data_operation_ids

REQUIRED:

broken_terminal_ids=0
broken_data_operation_ids=0

Sample >=20 DB paths and verify traceability where useful.

==================================================
10. BRANCHING / DEDUP
=====================

Verify:

* legitimate branches preserved
* same DB endpoint via different valid method chains preserved
* identical logical paths deduplicated
* unresolved branches coexist with valid confirmed branches
* ID fix did not collapse branches

Report:
duplicate logical paths
lost branch evidence
incorrectly merged paths

==================================================
11. UNRESOLVED BOUNDARIES
=========================

Verify unresolved calls remain boundaries.

Do not require reduction in unresolved count.

Check:

* no target guessing
* no confidence promotion
* unresolved branch termination preserved
* unresolved branch does not remove valid confirmed branches

RESULT:
PASS/FAIL

==================================================
12. CYCLE / DEPTH
=================

Report:

* cycle_paths
* truncated_paths
* max_observed_depth

Confirm:

* no infinite expansion
* depth guard intact
* cycle guard intact

Previous R4:
cycle_paths=0
truncated_paths=0
max_observed_depth=6

Material behavioral change requires explanation.

==================================================
13. CROSS-PROJECT
=================

Verify cross-project flow semantics remain based on resolved ownership.

Report:

* cross_project_flows
* project sequence integrity
* naming-based project/layer inference detected

Expected:
no naming-only inference.

==================================================
14. TRACEABILITY
================

CRITICAL FOR R5.

Validate references from functional paths to:

* entry_point IDs
* call evidence/references
* data-access operation IDs
* stored-procedure IDs
* SQL IDs

Calculate broken/orphan references.

REQUIRED:
no systematic broken references.

Path IDs must now be globally unique and safe for use as R5 traceability keys.

==================================================
15. PERFORMANCE / PATH EXPLOSION
================================

Calculate:

* total_paths
* max_paths_per_flow
* largest flows
* average_path_depth
* max depth
* duplicate logical paths

Check that path-ID correction did NOT cause:

* duplicated paths
* branch multiplication
* path explosion
* repeated recursive expansion

Classify:

PLAUSIBLE
SUSPICIOUS
EXPLOSION_DEFECT

==================================================
16. SECURITY
============

Scan R4.1 JSON outputs.

Check for actual exposed:

* password
* pwd
* user id
* uid
* username
* credentials
* token
* connection-string secrets

Do not reproduce secret values.

REQUIRED:
actual exposed secrets=0

Any exposed secret = CRITICAL.

==================================================
17. UPSTREAM REGRESSION
=======================

Verify materially:

R2:
entry_points=12662
event_bindings=12662

R3.1:
data_access=20082
confirmed=20073
Method->DataAccessOperation=9771
operations_method_null=0
stored_procedures=5389
sql_operations=3
parameters=74633

R1.1 confirmed-call semantics:
confirmed=12775

Historical total-call difference may be accepted ONLY if section 8 provides a deterministic non-regression explanation.

No unrelated semantic changes allowed.

==================================================
18. R5 READINESS
================

R5 requires R4.1 to provide reliable unique traceability keys.

PASS only if:

* duplicate_path_ids=0
* duplicate_logical_paths=0
* deterministic path IDs
* collision guard works
* functional paths preserved
* confirmed traversal reliable
* unresolved boundaries preserved
* DB terminals reliable
* branching preserved
* no path explosion
* traceability reliable
* security PASS
* no blocking upstream regression
* +1 call reconciled or proven non-regression

Do NOT implement R5.

==================================================
19. REQUIRED_FIXES
==================

Classify remaining issues:

CRITICAL
HIGH
MEDIUM
LOW

CRITICAL/HIGH block R5.

MEDIUM may block only if it materially compromises deterministic traceability or system-model reliability.

==================================================
20. DECISION
============

Return EXACTLY one:

A) V2-R4_1_APROBADA_PARA_R5
B) V2-R4_1_REQUIERE_CORRECCIONES
C) V2-R4_1_NO_CONFIABLE

Approval requires:

* no CRITICAL
* no blocking HIGH
* duplicate_path_ids=0
* duplicate_logical_paths=0
* path ID determinism PASS
* collision safety PASS
* traversal regression PASS
* DB terminal integrity PASS
* traceability PASS
* security PASS
* call-count discrepancy reconciled/non-regression
* R5_READINESS=PASS

==================================================
OUTPUT
======

Create ONLY:

`codex/V2/V2_R4_1_VALIDACION_REAL.md`

FORMAT:

STATUS
TESTS
METRICS
PATH_ID_VALIDATION
PATH_ID_DETERMINISM
COLLISION_GUARD
PATH_PRESERVATION
FLOW_ROOTS
CALL_TRAVERSAL
CALL_COUNT_RECONCILIATION
DB_TERMINALS
BRANCHING_DEDUP
UNRESOLVED_BOUNDARIES
CYCLE_DEPTH
CROSS_PROJECT
TRACEABILITY
PERFORMANCE
SECURITY
UPSTREAM_REGRESSION
R5_READINESS
REQUIRED_FIXES
DECISION

Machine-oriented.
Compact.
No ZIP.
No additional reports.
No code changes.
V2-R5 NOT STARTED.
