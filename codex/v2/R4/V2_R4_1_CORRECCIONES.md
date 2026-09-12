TASK: Apply minimal corrective revision V2-R4.1.

DO NOT start V2-R5.
DO NOT redesign R4.
DO NOT modify approved V1/R1.1/R2/R3.1 semantics.
DO NOT change functional traversal unless strictly required by the defects below.

SOURCE:
`codex/V2/V2_R4_VALIDACION_REAL.md`

CURRENT VALIDATION RESULT:
`V2-R4_REQUIERE_CORRECCIONES`

BLOCKERS:

1. HIGH
   duplicate_path_ids=12

   12 stable PATH IDs each identify two distinct logical paths.

   Requirements:

   * every functional path must have a globally unique deterministic `path_id`
   * same logical ordered path must reproduce same ID across runs
   * different logical paths must never share an ID
   * duplicate_path_ids must become 0
   * duplicate_logical_paths must remain 0

2. MEDIUM
   Approved R1.1 baseline:
   calls_total=230355
   confirmed=12775
   unresolved=217580

   R4 real output:
   calls_total=230356
   confirmed=12775
   unresolved=217581

   Explain and reconcile the unexplained +1 unresolved call.

==================================================
R4.1-01 PATH ID FIX
===================

Inspect current path stable-ID generation.

Determine exactly why 12 collisions occurred.

Replace collision-prone path identity generation with a deterministic identity based on the complete logical ordered path.

The identity input must distinguish at minimum where applicable:

* entry_point_id
* ordered node IDs
* ordered edge/relation sequence
* terminal_type
* terminal_target

Do not use truncated/insufficient identity material that allows distinct paths to collide.

Recommended model:

canonical_path_identity =
entry_point_id
+
ordered node IDs
+
ordered relation types
+
terminal_type
+
terminal_target

Serialize canonically before hashing.

Requirements:

* deterministic
* stable across executions
* same path -> same ID
* distinct path -> distinct ID
* independent of runtime object ordering
* no random UUID
* no timestamp
* no Python `hash()`
* use stable cryptographic digest already compatible with project conventions

If current IDs use shortened digests, use sufficient digest length to eliminate practical collisions.

Do not alter logical path content to hide collisions.

==================================================
R4.1-02 COLLISION SAFETY
========================

Add explicit validation during path generation/export:

If generated `path_id` already exists:

* if canonical path identity is identical:
  treat as duplicate logical path and deduplicate normally

* if canonical path identity differs:
  this is an ID collision and must not silently overwrite/merge paths

Preferred behavior:
generate IDs from sufficiently complete canonical material so this condition never occurs.

Tests must prove collision detection/avoidance.

==================================================
R4.1-03 CALL COUNT RECONCILIATION
=================================

Investigate:

approved baseline:
total=230355
confirmed=12775
unresolved=217580

R4:
total=230356
confirmed=12775
unresolved=217581

Find the exact additional unresolved call.

Report:

* call ID
* source file
* caller method
* expression/receiver/method name
* why it exists in R4 output but not approved baseline
* whether caused by:

  * source repository difference
  * scanner/extractor change
  * execution environment
  * generated/output contamination
  * ordering/dedup issue
  * actual upstream regression
  * other deterministic cause

Do NOT change upstream call extraction merely to force the expected count.

If the +1 is caused by different source-repository contents between machines/runs:
document evidence and classify as environment/source snapshot difference.

If caused by R4 code changing upstream call extraction:
this is a regression and must be corrected.

If previous approved snapshot is unavailable:
use repository/code/history/current indexes to identify the additional call as far as deterministically possible and clearly state the evidence limitation.

==================================================
R4.1-04 REGRESSION
==================

R4.1 must preserve:

R1.1 semantics:

* confirmed calls remain deterministic
* unresolved calls are not promoted
* no name-only traversal

R2:

* entry_points=12662
* event_bindings=12662

R3.1:

* data_access=20082
* confirmed data_access=20073
* Method->DataAccessOperation=9771
* operations_method_null=0
* stored_procedures=5389
* sql_operations=3
* parameters=74633

R4 real functional behavior must remain materially unchanged:

* flow roots
* confirmed Method -> Method traversal
* branching
* DB terminals
* unresolved boundaries
* dead ends
* cross-project flows
* confidence
* traceability
* cycle/depth behavior

Only IDs may legitimately change because of corrected path identity.

==================================================
R4.1-05 TESTS
=============

Preserve all existing tests.

Add tests covering at least:

T01 same canonical path -> same path_id
T02 different entry point -> different path_id
T03 different ordered method chain -> different path_id
T04 different terminal -> different path_id
T05 different branch -> different path_id
T06 canonical serialization deterministic
T07 no Python runtime hash dependency
T08 duplicate identical logical path deduplicated
T09 distinct paths cannot overwrite each other
T10 collision detection guard
T11 functional flow IDs remain stable
T12 R4 traversal unchanged
T13 confirmed calls unchanged
T14 unresolved calls not promoted
T15 R2 baseline unchanged
T16 R3.1 baseline unchanged
T17 sanitizer still applies
T18 no R5 output generated

Run:

`python -m unittest discover -s tests`

All tests must PASS.

==================================================
R4.1-06 INTERNAL VALIDATION
===========================

After tests, run fixture/internal validation only.

Verify:

* duplicate_path_ids=0
* duplicate_flow_ids=0
* duplicate_logical_paths=0
* no logical path loss
* same branches preserved
* same DB terminal reachability preserved
* no security regression

Do NOT automatically run the full real legacy repository.

==================================================
R4.1-07 SECURITY
================

Continue using centralized sanitizer.

Do not expose connection secrets or credentials while investigating the +1 unresolved call.

Evidence in report must remain sanitized.

==================================================
R4.1-08 OUTPUT
==============

Create/update only the code/tests required for R4.1 and:

`codex/V2/V2_R4_1_RESULTADO.md`

Report format:

STATUS
FILES_CHANGED
TESTS
PATH_ID_ROOT_CAUSE
PATH_ID_FIX
COLLISION_GUARD
CALL_COUNT_INVESTIGATION
CALL_COUNT_CAUSE
REGRESSION
INTERNAL_METRICS
SECURITY
KNOWN_LIMITATIONS
REAL_VALIDATION_COMMAND
NEXT

Keep report machine-oriented and compact.

==================================================
REAL VALIDATION COMMAND
=======================

Do NOT execute automatically.

Current legacy repository:

`C:\Users\cgalianj\source\IST_40\operacional`

Command:

`python main.py "C:\Users\cgalianj\source\IST_40\operacional" --output "output\v2_r4_1_full" --verbose`

==================================================
ACCEPTANCE
==========

R4.1 implementation is ready for real validation when:

* all tests PASS
* duplicate_path_ids=0 internally
* duplicate_flow_ids=0
* duplicate_logical_paths=0
* deterministic stable path IDs demonstrated
* path collisions cannot silently merge distinct paths
* +1 unresolved call investigated and explained
* no upstream semantic regression
* R4 traversal behavior preserved
* security PASS
* V2-R5 NOT STARTED

STOP after implementation/tests/internal validation.

Expected final status:

`V2-R4_1_READY_FOR_FULL_REAL_VALIDATION`
