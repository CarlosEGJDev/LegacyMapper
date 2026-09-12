TASK: Validate LegacyMapper V2-R4 against full real repository.

DO NOT modify code.
DO NOT start V2-R5.
DO NOT change approved V1/R1.1/R2/R3.1 semantics.

BASELINE:
- V1 approved.
- V2-R1.1 approved.
- V2-R2 approved.
- V2-R3.1 approved.
- V2-R4 implemented; 49 tests PASS.

INPUT:
- output/v2_r4_full/
- output/v2_r3_1_full/
- output/v2_r2_full/
- codex/V2/V2_R3_1_VALIDACION_REAL.md
- codex/V2/V2_R4_RESULTADO.md

PRIMARY:
- output/v2_r4_full/index/functional_flows.json
- output/v2_r4_full/index/functional_paths.json
- output/v2_r4_full/index/flow_summary.json
- output/v2_r4_full/index/flow_unresolved.json
- output/v2_r4_full/index/calls.json
- output/v2_r4_full/index/entry_points.json
- output/v2_r4_full/index/event_bindings.json
- output/v2_r4_full/index/data_access.json
- output/v2_r4_full/index/stored_procedures.json
- output/v2_r4_full/index/sql_operations.json
- output/v2_r4_full/index/errors.json

GOAL:
Determine whether R4 reliably converts approved entry points + call graph + persistence endpoints into deterministic functional flows suitable for V2-R5.

==================================================
1. METRICS
==================================================

Report:

- total_entry_points_considered
- entry_points_with_flows
- total_flows
- total_paths
- paths_to_stored_procedure
- paths_to_sql
- paths_to_data_operation
- unresolved_boundaries
- external_boundaries
- dead_end_paths
- cycle_paths
- truncated_paths
- unique_terminal_stored_procedures
- unique_terminal_sql_operations
- cross_project_flows
- max_observed_depth
- average_path_depth
- duplicate_flow_ids
- duplicate_path_ids
- duplicate_logical_paths
- errors

Also calculate:

entry_point_flow_coverage =
entry_points_with_flows / confirmed R2 entry points

db_terminal_ratio =
(paths_to_stored_procedure + paths_to_sql + paths_to_data_operation)
/
total_paths

Do not treat high counts alone as success.

==================================================
2. FLOW ROOT VALIDATION
==================================================

Sample >=25 flows across different WebForms/projects.

For each verify:

WebForm
-> Event/Lifecycle
-> Handler
-> start Method

against:
- entry_points.json
- event_bindings.json
- source evidence

Classify:
CORRECT
SUSPICIOUS
INCORRECT

Check:
- no unrelated WebForm merged
- no wrong handler ownership
- no fabricated start method
- multiple entry points sharing handler remain distinct roots

Report precision estimate.

==================================================
3. CALL GRAPH TRAVERSAL
==================================================

Sample >=30 traversed Method -> Method edges from functional paths.

Verify every edge exists as CONFIRMED in calls.json.

CRITICAL RULE:

R4 must never traverse an unresolved call as a confirmed Method -> Method edge.

Report:

- sampled confirmed traversal edges
- missing upstream edges
- unresolved calls incorrectly traversed
- inferred/name-only relationships
- wrong caller/callee ownership

Any fabricated confirmed traversal = CRITICAL.

==================================================
4. KNOWN REAL CHAINS
==================================================

Search for the previously validated anchors where available:

ucADHCartasVisualPDF2.Imprime_NOM
-> blADHds67.txobtenerdatosnom
-> PADH_D67.OBTENER_DATOS_NOM

ucADHCartasVisualPDF2.Imprime_DEU
-> blADHds67.txobtenerdatosdeu
-> PADH_D67.OBTENER_DATOS_DEU

ucADHImpCalAlzCAD.Page_Load
-> blADHds67.txobtenerdatoscarta
-> PADH_D67.OBTENER_DATOS_CARTA

ucADHMO831.CargaGrillaReq
-> blADHds67Bit.txbuscadetreqd67
-> PADH_D67_BIT.BUSCADETREQD67

ucADHMO831.HypGuardar_Click
-> blADHds67Bit.txinsertareqd67
-> PADH_D67_BIT.INSERTAREQD67

ucADHMO831.HypEliminar_Click
-> blADHds67Bit.txeliminareqd67
-> PADH_D67_BIT.ELIMINAREQD67

Do NOT require exact path presence if the corresponding method is not reachable from an R2 root.

For each reachable anchor:
- locate flow
- verify ordered method chain
- verify terminal DB endpoint
- verify evidence references

Classify:
FOUND_CORRECT
FOUND_INCORRECT
NOT_REACHABLE
EXPECTED_BUT_MISSING

==================================================
5. DATABASE TERMINALS
==================================================

Sample >=30 DB terminal paths:
- >=20 StoredProcedure if available
- all SQL paths if <10, otherwise >=10
- DataAccessOperation-only terminals where available

Verify:

EntryPoint
-> Handler
-> Method chain
-> DataAccessOperation
-> StoredProcedure/SQL

Cross-check terminal IDs against R3.1 indexes.

Check:
- no fabricated procedure
- no wrong operation/procedure association
- SQL terminal references real SQL operation
- operation-only terminal genuinely lacks resolved proc/SQL

Classify:
CORRECT
SUSPICIOUS
INCORRECT

Report DB terminal precision.

==================================================
6. BRANCHING
==================================================

Find >=10 flows with multiple terminal paths.

Verify R4 preserves legitimate branches.

Example:

Handler
 -> MethodA
    -> MethodB -> Proc1
    -> MethodC -> Proc2

Check:
- branches not collapsed
- distinct method paths preserved
- same procedure via different legitimate paths preserved
- exact duplicate logical paths removed
- unresolved branch does not eliminate confirmed DB branch

Classify branching behavior.

==================================================
7. CYCLES
==================================================

Inspect all cycle paths if <=20, otherwise sample >=20.

Verify:
- actual repeated method exists in path
- cycle terminates traversal
- no infinite expansion
- cycle target correctly identified
- cycle does not suppress unrelated valid branches

False cycle detection = HIGH.

Infinite/repeated path explosion = CRITICAL.

==================================================
8. DEPTH TRUNCATION
==================================================

Inspect all truncated paths if <=20, otherwise sample >=20.

Verify:
- path reached configured max depth
- terminal status indicates truncation
- tail was not silently classified as dead-end
- max observed depth consistent with --flow-max-depth

Default expected max depth:
12

Report whether depth=12 appears sufficient.

If material legitimate DB chains are truncated:
classify HIGH/MEDIUM based on impact.

Do NOT change depth during validation.

==================================================
9. UNRESOLVED BOUNDARIES
==================================================

Sample >=25 unresolved boundaries.

Verify:
- upstream call is unresolved in calls.json
- R4 did NOT guess a target
- caller/expression/receiver/method/evidence retained when available
- boundary terminates only that branch

Classify:
CORRECT
SUSPICIOUS
INCORRECT

Report whether unresolved volume materially prevents useful R5 interpretation.

==================================================
10. DEAD ENDS
==================================================

Sample >=20 dead-end paths.

Verify:
- terminal method has no confirmed outgoing call/data operation in approved indexes
- unresolved call was not incorrectly discarded
- DB operation was not missed by R4 indexing

Classify:
TRUE_DEAD_END
UPSTREAM_UNRESOLVED
R4_FALSE_DEAD_END

Material R4 false dead ends = HIGH.

==================================================
11. CROSS-PROJECT FLOWS
==================================================

Sample >=20 cross-project flows if available.

Verify project ownership against existing project metadata.

Prioritize chains resembling:

Web
-> BL
-> SYS
-> DB

Do NOT validate architecture based only on folder/project names.

Check:
- ordered project_sequence
- actual confirmed calls cross project
- no project inserted by naming heuristic
- missing project context allowed where upstream unresolved

Report precision.

==================================================
12. PATH DEDUP
==================================================

Check globally:

- duplicate flow IDs
- duplicate path IDs
- identical ordered node chains
- identical logical terminal paths
- duplicate edges inside same flow

Distinguish legitimate same endpoint reached through different paths.

Requirements:
duplicate IDs = 0
duplicate logical paths = 0

Do NOT mark distinct method chains to same procedure as duplicates.

==================================================
13. CONFIDENCE
==================================================

Sample >=30 paths.

Verify:

confirmed:
all material traversed relationships confirmed.

unresolved:
contains unresolved boundary.

No confidence upgrade allowed.

Check:
- unresolved path labeled confirmed
- inferred edge silently converted to confirmed
- mixed path incorrectly labeled

Any systematic confidence promotion = HIGH/CRITICAL.

==================================================
14. TRACEABILITY
==================================================

Sample >=20 paths.

Verify IDs/references resolve to upstream indexes:

- entry_point_id
- call IDs
- DataAccessOperation IDs
- StoredProcedure IDs
- SQL IDs

Report:
- complete traceability
- broken references
- orphan IDs

Broken DB endpoint references = HIGH.

Systematic broken references = CRITICAL.

==================================================
15. PERFORMANCE / EXPLOSION
==================================================

Analyze:

- paths per flow distribution
- max paths per flow
- top 20 largest flows
- path depth distribution
- repeated prefixes
- cycle counts
- unresolved branch counts

Detect combinatorial explosion.

Flag suspicious cases such as:
- thousands of near-identical paths from one entry point
- repeated recursive expansions
- duplicate branch multiplication
- path counts inconsistent with reachable graph

Classify:
PLAUSIBLE
SUSPICIOUS
EXPLOSION_DEFECT

Estimate whether current output is practical for R5.

==================================================
16. SECURITY
==================================================

CRITICAL validation.

Search all R4 generated JSON:

- functional_flows.json
- functional_paths.json
- flow_summary.json
- flow_unresolved.json

Check evidence/reference fields for exposed:
- password
- pwd
- user id
- uid
- username
- credentials
- tokens
- connection-string secret values

Do not reproduce secrets.

Any actual exposed secret = CRITICAL FAIL.

==================================================
17. REGRESSION
==================================================

Compare R4 output upstream indexes against approved R3.1/R2.

Must preserve materially:

R1.1:
- calls_total=230355
- confirmed=12775
- unresolved=217580

R2:
- entry_points=12662
- event_bindings=12662

R3.1:
- data_access=20082
- data_access_confirmed=20073
- Method -> DataAccessOperation=9771
- operations_method_null=0
- stored_procedures=5389
- SQL operations=3
- parameters=74633
- duplicate logical dependencies=0

Check errors behavior.

Any unexplained upstream semantic change = HIGH.

==================================================
18. R5 READINESS
==================================================

Determine whether R4 outputs are reliable enough for R5 to build:

SYSTEM_CONTEXT.json
SYSTEM_CONTEXT.md
ARCHITECTURE_GRAPH.json
FUNCTIONAL_FLOWS.json
TRACEABILITY.json

R5 requires:
- reliable roots
- reliable confirmed traversal
- usable DB terminals
- explicit unresolved boundaries
- cycle safety
- bounded traversal
- branching preservation
- dedup
- traceability
- manageable output size
- security PASS

Do NOT implement R5.

==================================================
19. REQUIRED_FIXES
==================================================

If defects exist classify:

CRITICAL
HIGH
MEDIUM
LOW

CRITICAL/HIGH block R5.

MEDIUM/LOW are non-blocking unless evidence shows material impact on system-model reliability.

==================================================
20. DECISION
==================================================

Return exactly one:

A) V2-R4_APROBADA_PARA_R5
B) V2-R4_REQUIERE_CORRECCIONES
C) V2-R4_NO_CONFIABLE

Approval requires:
- no CRITICAL
- no blocking HIGH
- traversal precision acceptable
- no unresolved-call promotion
- DB terminals reliable
- cycles/depth safe
- branching correct
- dedup correct
- traceability reliable
- no path explosion
- security PASS
- no upstream regression
- R5 readiness PASS

==================================================
OUTPUT
==================================================

Create only:

codex/V2/V2_R4_VALIDACION_REAL.md

FORMAT:

STATUS
METRICS
FLOW_ROOTS
CALL_TRAVERSAL
KNOWN_CHAINS
DB_TERMINALS
BRANCHING
CYCLES
DEPTH_TRUNCATION
UNRESOLVED_BOUNDARIES
DEAD_ENDS
CROSS_PROJECT
DEDUP
CONFIDENCE
TRACEABILITY
PERFORMANCE
SECURITY
REGRESSION
R5_READINESS
REQUIRED_FIXES
DECISION

Machine-oriented.
Compact.
No ZIP.
No additional reports.
No code changes.
V2-R5 NOT STARTED.