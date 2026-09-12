STATUS
VALIDATED_WITH_BLOCKING_DEFECTS

METRICS
total_entry_points_considered=12642
entry_points_with_flows=12642
total_flows=12642
total_paths=170020
paths_to_stored_procedure=1121
paths_to_sql=1
paths_to_data_operation=4612
unresolved_boundaries=162914
external_boundaries=0
dead_end_paths=1372
cycle_paths=0
truncated_paths=0
unique_terminal_stored_procedures=338
unique_terminal_sql_operations=1
cross_project_flows=2187
max_observed_depth=6
average_path_depth=1.3
duplicate_flow_ids=0
duplicate_path_ids=12
duplicate_logical_paths=0
errors=0
entry_point_flow_coverage=1.000000
db_terminal_ratio=0.033725

FLOW_ROOTS
AUTOMATED_STRUCTURAL_CHECK=12642/12642 flow roots match confirmed entry_point_id and handler_method.
RESULT=CORRECT for sampled/root-index structure; no merged roots detected.

CALL_TRAVERSAL
VERIFIED=11018 distinct flow Method -> Method edges against confirmed calls.json relations.
missing_upstream_edges=0
unresolved_calls_incorrectly_traversed=0
inferred_or_name_only_relationships=0
RESULT=CORRECT

KNOWN_CHAINS
PADH_D67_BIT.INSERTAREQD67=FOUND_CORRECT, 2 paths, sample EP-0310457658.
PADH_D67_BIT.ELIMINAREQD67=FOUND_CORRECT, 2 paths, sample EP-0121396352.
PADH_D67.OBTENER_DATOS_NOM=NOT_REACHABLE in R4 output.
PADH_D67.OBTENER_DATOS_DEU=NOT_REACHABLE in R4 output.
PADH_D67.OBTENER_DATOS_CARTA=NOT_REACHABLE in R4 output.
PADH_D67_BIT.BUSCADETREQD67=NOT_REACHABLE in R4 output.

DB_TERMINALS
VERIFIED=1122 stored-procedure/SQL terminal node IDs against R3.1-derived indexes.
broken_terminal_ids=0
broken_data_operation_ids=0
RESULT=CORRECT

BRANCHING
Flows retain 170020 terminal paths; maximum paths per flow=399. Distinct logical chains=170020. Confirmed DB branches coexist with unresolved branches.
RESULT=CORRECT

CYCLES
cycle_paths=0
RESULT=NO_CYCLES_OBSERVED

DEPTH_TRUNCATION
truncated_paths=0
max_observed_depth=6
configured_default_depth=12
RESULT=SUFFICIENT_FOR_OBSERVED_OUTPUT

UNRESOLVED_BOUNDARIES
unresolved_boundaries=162914
flow_unresolved_records=162914
Unresolved branches were not promoted to Method -> Method edges.
RESULT=CORRECT_BUT_HIGH_VOLUME

DEAD_ENDS
dead_end_paths=1372
No broken DAO references found in path nodes. No R4 false dead-end evidence found by index consistency checks.
RESULT=PLAUSIBLE

CROSS_PROJECT
cross_project_flows=2187
Project sequences are derived from resolved project ownership in paths; no naming-layer inference detected.
RESULT=CORRECT

DEDUP
duplicate_flow_ids=0
duplicate_logical_paths=0
duplicate_path_ids=12
DEFECT=Stable PATH hash collision: 12 IDs each identify two distinct paths. Requirement duplicate IDs=0 is violated.

CONFIDENCE
confirmed_paths=7103
unresolved_paths=162917
Confirmed Method -> Method edges all cross-check to confirmed upstream calls. Unresolved boundaries produce unresolved paths.
RESULT=CORRECT

TRACEABILITY
entry roots=12642/12642 structurally resolvable.
DB endpoint node IDs=1122/1122 resolvable.
DAO node IDs=all checked resolvable.
Call evidence references are compact deterministic references; no missing confirmed traversal relation found.
RESULT=USABLE_WITH_PATH_ID_COLLISION_LIMITATION

PERFORMANCE
max_paths_per_flow=399
No cycles, truncation, or duplicate logical-path explosion observed. Output is practical for R5 after identifier correction.
RESULT=PLAUSIBLE

SECURITY
R4 JSON scan: password/pwd/user id/uid/username/token unredacted assignment patterns=0.
RESULT=PASS

REGRESSION
R2: entry_points=12662; event_bindings=12662; preserved.
R3.1: data_access=20082; confirmed=20073; Method->DataAccessOperation=9771; operations_method_null=0; stored_procedures=5389; sql_operations=3; preserved.
R1.1 historical calls metric=230355; R4 calls=230356 (confirmed=12775, unresolved=217581). Snapshot directories output/v2_r3_1_full and output/v2_r2_full were unavailable; +1 unresolved call is unexplained and requires comparison before approval.

R5_READINESS
FAIL_PENDING_CORRECTIONS: unique path IDs are mandatory for traceability and R5 artifacts.

REQUIRED_FIXES
HIGH: Replace collision-prone PATH stable-ID generation; regenerate R4 output; prove duplicate_path_ids=0.
MEDIUM: Explain/reconcile the +1 unresolved call against approved R1.1/R3.1 snapshot.

DECISION
V2-R4_REQUIERE_CORRECCIONES
