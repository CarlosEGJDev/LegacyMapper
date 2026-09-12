STATUS
VALIDATED_WITH_NONBLOCKING_FUNCTIONAL_RESULTS_AND_UNRECONCILED_CALL_DELTA

TESTS
50 passed, as recorded in V2_R4_1_RESULTADO.md.
Full real output exists: output/v2_r4_1_full.

METRICS
total_entry_points_considered=12642
entry_points_with_flows=12642
total_flows=12642
total_paths=170020
unique_path_ids=170020
duplicate_path_ids=0
duplicate_logical_paths=0
paths_to_stored_procedure=1121
paths_to_sql=1
paths_to_data_operation=4612
unresolved_boundaries=162914
dead_end_paths=1372
cycle_paths=0
truncated_paths=0
cross_project_flows=2187
max_observed_depth=6
average_path_depth=1.3
errors=0

PATH_ID_VALIDATION
PASS. Every path_id maps to exactly one canonical logical path; duplicate_path_ids=0.

PATH_ID_DETERMINISM
PASS. Identity canonically serializes entry_point_id, ordered nodes, ordered relation_types, terminal_type and terminal_target; uses full SHA-256 hex. No UUID, timestamp, Python hash(), or unstable collection ordering.

COLLISION_GUARD
PASS. path_id -> canonical identity registry accepts identical deduplication and raises ValueError for differing identities; silent merge is prevented.

PATH_PRESERVATION
R4 logical paths=170020; R4.1 logical paths=170020; lost=0; added=0. All 170020 path IDs changed as expected from the identity fix. RESULT=EXPECTED.

FLOW_ROOTS
12642/12642 flows resolve to an existing confirmed entry point and its handler_method. Root count unchanged. PASS.

CALL_TRAVERSAL
confirmed_traversed_edges=11018
missing_upstream_edges=0
unresolved_calls_traversed_as_confirmed=0
inferred_or_name_only_traversal=0
PASS.

CALL_COUNT_RECONCILIATION
current_calls_total=230356
current_confirmed=12775
current_unresolved=217581
historical_approved_total=230355
historical_approved_confirmed=12775
historical_approved_unresolved=217580
classification=UNEXPLAINED
R4/R4.1 do not alter CallExtractor/CallResolver; flow resolution runs after calls creation. Required approved calls snapshots are absent locally, so the exact additional unresolved call ID/evidence cannot be determined without fabricating a baseline comparison. No evidence of R4.1 upstream extraction regression.

DB_TERMINALS
terminal_nodes_checked=1122
broken_terminal_ids=0
broken_data_operation_ids=0
unique_terminal_stored_procedures=338
unique_terminal_sql_operations=1
PASS.

BRANCHING_DEDUP
duplicate_logical_paths=0
max_paths_per_flow=399
No lost logical branches from R4 to R4.1; confirmed DB and unresolved branches coexist. PASS.

UNRESOLVED_BOUNDARIES
unresolved_boundaries=162914
flow_unresolved_records=162914
No target guessing or confidence promotion detected. PASS.

CYCLE_DEPTH
cycle_paths=0
truncated_paths=0
max_observed_depth=6
No expansion defect observed. PASS.

CROSS_PROJECT
cross_project_flows=2187
Project sequence is derived from resolved project ownership; naming-only layer inference not detected. PASS.

TRACEABILITY
flow roots resolvable=12642/12642
DB terminal IDs resolvable=1122/1122
DAO path node IDs broken=0
Unique path IDs are safe traceability keys. PASS.

PERFORMANCE
total_paths=170020
max_paths_per_flow=399
No duplicate-path multiplication, cycles, or recursive explosion. PLAUSIBLE.

SECURITY
Unredacted password/pwd/user id/uid/username/token assignment patterns=0 across R4.1 JSON. PASS.

UPSTREAM_REGRESSION
R2 preserved: entry_points=12662; event_bindings=12662.
R3.1 preserved: data_access=20082; confirmed=20073; Method->DataAccessOperation=9771; operations_method_null=0; stored_procedures=5389; sql_operations=3.
Confirmed calls=12775 preserved. Historical total-call delta remains unproven, not changed by R4.1.

R5_READINESS
FAIL_PENDING_CALL_COUNT_RECONCILIATION. All R4.1 functional, traceability, security and path-ID requirements pass; approval condition requiring reconciliation/proven non-regression of the +1 unresolved call is not yet met.

REQUIRED_FIXES
MEDIUM: Obtain approved calls.json snapshot (or reproducible historical source snapshot), identify the exact +1 unresolved call, and classify it as source/environment difference or upstream regression. No R4.1 functional fix required.

DECISION
V2-R4_1_REQUIERE_CORRECCIONES
