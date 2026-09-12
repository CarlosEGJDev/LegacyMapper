# LegacyMapper V2-R4 — Functional Flow Resolver

TASK: Implement V2-R4.

BASELINE:

* V1 approved.
* V2-R1.1 approved.
* V2-R2 approved.
* V2-R3.1 approved for R4.
* V2-R5 NOT started.

SOURCE OF TRUTH:

* codex/V2/V2_R2_VALIDACION_REAL.md
* codex/V2/V2_R3_1_VALIDACION_REAL.md

DO NOT implement V2-R5.
DO NOT add LLM dependency.

## GOAL

Build deterministic functional flows by traversing already-approved structural indexes.

Target:

WebForm
-> Event/Lifecycle
-> Handler
-> Method
-> Call
-> Method
-> ...
-> DataAccessOperation
-> StoredProcedure | SQL

R4 must CONNECT existing facts.

R4 must NOT rediscover:

* WebForms
* calls
* methods
* stored procedures
* SQL
* data-access operations

Reuse approved V1/R1/R2/R3.1 outputs/models.

Current validated R3.1 readiness:

* Method -> DataAccessOperation edges: 9771
* operations_method_null: 0
* call_to_data_method_hits: 3805
* future R4 sample: 15 usable / 0 broken

R4 objective is graph traversal + flow normalization.

---

## R4-01 FLOW MODEL

Create deterministic FunctionalFlow model.

Minimum:

{
"id": "...",
"entry_point_id": "...",
"webform": "...",
"event": "...",
"handler": "...",
"start_method": "...",
"nodes": [],
"edges": [],
"terminal_operations": [],
"confidence": "...",
"status": "...",
"depth": 0,
"evidence": []
}

Stable deterministic IDs.

Do not duplicate complete source data already stored in other indexes.
Prefer references/IDs where possible.

---

## R4-02 NODE TYPES

Support at minimum:

* WebForm
* Event
* Handler
* Method
* Class
* Project
* DataAccessOperation
* StoredProcedure
* SQL
* ExternalCall
* UnresolvedCall

Do NOT invent architectural layers as facts.

Layer metadata may reuse previously resolved/inferred context but must preserve its confidence.

---

## R4-03 EDGE TYPES

Normalize flow relations including:

WebForm -> Event
Event -> Handler
Handler -> Method
Method -> Method
Method -> DataAccessOperation
DataAccessOperation -> StoredProcedure
DataAccessOperation -> SQL

Optional where useful:

Method -> ExternalCall
Method -> UnresolvedCall

Every edge must reference existing approved evidence.

Do not create new call relationships by name-only guessing.

---

## R4-04 ENTRY POINTS

Use V2-R2 confirmed entry points as roots.

Primary roots:

* web_event
* web_lifecycle

Include unresolved entry points only when explicitly flagged and useful for traceability.

Default flow generation should prioritize confirmed roots.

Each flow must preserve:

* WebForm
* control/event
* handler
* handler method
* source evidence

---

## R4-05 CALL GRAPH TRAVERSAL

Traverse existing V2-R1.1 call graph.

Rules:

1. Start at confirmed handler method.
2. Follow confirmed Method -> Method calls.
3. Continue until:

   * DataAccessOperation reached
   * external/unresolved call boundary reached
   * no outgoing confirmed calls
   * cycle detected
   * max depth reached

Do NOT re-resolve unresolved calls in R4.

Do NOT convert unresolved calls to confirmed.

---

## R4-06 RECURSION / CYCLES

Cycle-safe traversal mandatory.

Maintain visited path/state.

Detect:

* self recursion
* mutual recursion
* repeated method cycles

Represent cycle explicitly.

Never infinite-loop.

Cycle termination must preserve:

* cycle target
* source method
* evidence
* confidence

---

## R4-07 DEPTH

Configurable maximum traversal depth.

Suggested default:
12

Expose via config/CLI only if consistent with current architecture.

If max depth reached:

status = truncated_depth

Do not silently drop tail.

Report truncation metrics.

---

## R4-08 BRANCHING

A method may call multiple methods/data operations.

R4 must preserve branches.

Example:

Handler
-> MethodA
-> MethodB -> Proc1
-> MethodC -> Proc2
-> MethodD -> unresolved

Do not collapse distinct branches into one linear flow.

Represent as graph/path structure.

---

## R4-09 TERMINAL OPERATIONS

Terminal business-technical endpoints include:

* StoredProcedure
* SQL
* confirmed DataAccessOperation without resolved proc/SQL
* external boundary
* unresolved call boundary
* dead-end method

Classify terminal type.

Primary R4 documentation value comes from paths reaching DB endpoints.

---

## R4-10 PATHS

Generate normalized path records in addition to graph flows.

Example:

{
"flow_id": "...",
"path_id": "...",
"entry_point_id": "...",
"nodes": [...],
"terminal_type": "stored_procedure",
"terminal_target": "PADH_D67_BIT.INSERTAREQD67",
"confidence": "confirmed"
}

Use paths to simplify R5/documentation/diagram generation.

Prevent duplicate logical paths.

---

## R4-11 CONFIDENCE

Flow confidence must derive from weakest material edge.

Recommended:

confirmed:
all required traversed edges confirmed.

unresolved:
one or more unresolved boundary edges exist.

Do not use inferred unless existing approved indexes explicitly contain inferred relationships.

Do not upgrade confidence.

---

## R4-12 EVIDENCE

Each flow/path must preserve traceability sufficient to reach source evidence.

Prefer references to source IDs/index records rather than copying huge evidence blocks.

Minimum traceability:

* entry point ID
* call IDs
* data-access operation IDs
* stored-procedure/SQL IDs

Optional compact evidence samples.

Avoid output explosion.

---

## R4-13 CROSS-PROJECT FLOW

Support traversal across project boundaries using existing confirmed call graph.

Target examples include chains such as:

Web
-> BL
-> SYS
-> DataAccess

Do not assume folder names prove layer transitions.

Record project changes when existing project ownership is available.

Useful metadata:

project_sequence:
[
"WebProject",
"BLProject",
"SYSProject"
]

Do not require project ownership for flow validity if method IDs are deterministic.

---

## R4-14 BUSINESS FLOW GROUPING

Group paths sharing same entry point into one functional flow.

Example:

EntryPoint:
btnGuardar.Click

Possible endpoints:

* PROC_A
* PROC_B
* SQL_SELECT
* unresolved external call

FunctionalFlow = one root graph.

FunctionalPath = each terminal path.

Do NOT infer business descriptions yet.

That belongs to R5/AI interpretation.

---

## R4-15 DEAD ENDS

Classify methods that terminate without persistence.

Possible terminal status:

* data_endpoint
* external_boundary
* unresolved_boundary
* dead_end
* cycle
* truncated_depth

Dead-end != error.

Do not force every UI event to reach DB.

---

## R4-16 UNRESOLVED CALLS

Preserve unresolved calls as boundaries when they appear in traversed methods.

Do not recursively guess target.

Store:

* caller
* expression
* receiver
* method name
* evidence
* reason unresolved if available

This helps R5 explain incomplete flows.

---

## R4-17 PERFORMANCE

Repository scale:

* ~230k calls
* ~12.6k entry points
* ~20k data-access operations

Avoid per-entry-point full graph scans.

Build indexes before traversal:

* method_id -> confirmed outgoing calls
* method_id -> unresolved outgoing calls
* method_id -> data-access operations
* operation_id -> procedures
* operation_id -> SQL
* entry_point -> handler method

Target complexity approximately proportional to traversed reachable graph.

Memoization/caching allowed.

Do not use O(entry_points × all_calls).

---

## R4-18 FLOW DEDUP

Deduplicate:

* identical flow edges
* identical paths
* identical terminal endpoints per identical path

Do not remove legitimate branching where same procedure is reached through different method paths.

Stable path identity should reflect ordered method/operation chain.

---

## R4-19 OUTPUTS

Add:

output/index/functional_flows.json
output/index/functional_paths.json
output/index/flow_summary.json

Optional:
output/index/flow_unresolved.json

Only if useful and non-redundant.

Do NOT remove/rename previous indexes.

---

## R4-20 FLOW SUMMARY

`flow_summary.json` should provide compact metrics:

* total_entry_points_considered
* entry_points_with_flows
* total_flows
* total_paths
* paths_to_stored_procedure
* paths_to_sql
* paths_to_data_operation
* unresolved_boundaries
* external_boundaries
* dead_end_paths
* cycle_paths
* truncated_paths
* unique_terminal_stored_procedures
* unique_terminal_sql_operations
* cross_project_flows
* max_observed_depth
* average_path_depth
* errors

No prose required.

---

## R4-21 EXISTING KNOWN REAL CHAINS

R3.1 validation already demonstrated usable endpoints such as:

* ucADHCartasVisualPDF2.Imprime_NOM
  -> blADHds67.txobtenerdatosnom
  -> PADH_D67.OBTENER_DATOS_NOM

* ucADHCartasVisualPDF2.Imprime_DEU
  -> blADHds67.txobtenerdatosdeu
  -> PADH_D67.OBTENER_DATOS_DEU

* ucADHImpCalAlzCAD.Page_Load
  -> blADHds67.txobtenerdatoscarta
  -> PADH_D67.OBTENER_DATOS_CARTA

* ucADHMO831.CargaGrillaReq
  -> blADHds67Bit.txbuscadetreqd67
  -> PADH_D67_BIT.BUSCADETREQD67

* ucADHMO831.HypGuardar_Click
  -> blADHds67Bit.txinsertareqd67
  -> PADH_D67_BIT.INSERTAREQD67

* ucADHMO831.HypEliminar_Click
  -> blADHds67Bit.txeliminareqd67
  -> PADH_D67_BIT.ELIMINAREQD67

These are validation anchors, not hardcoded mappings.

Do NOT special-case them.

---

## R4-22 FALSE POSITIVE GUARDS

Do NOT:

* infer Method -> Method by same method name
* traverse unresolved calls as confirmed
* treat all methods in same class as connected
* infer flow from folder proximity
* infer project layer from name alone
* invent database endpoints
* merge unrelated entry points
* collapse different branches
* follow comments/string code
* interpret JavaScript as server call graph
* fabricate missing methods

---

## R4-23 TESTS

Preserve ALL existing tests.

Add targeted R4 tests at minimum:

T01 simple EntryPoint -> Method -> Proc
T02 EntryPoint -> Method -> Method -> Proc
T03 multi-hop 4+ methods
T04 branching to two procedures
T05 branch to SQL + procedure
T06 unresolved call boundary
T07 dead-end method
T08 self recursion
T09 mutual recursion
T10 cycle termination
T11 max-depth truncation
T12 cross-project path
T13 multiple entry points same handler
T14 multiple procedures same method
T15 same procedure via different valid paths
T16 duplicate logical path removal
T17 preserve different valid branches
T18 path confidence confirmed
T19 unresolved boundary confidence
T20 terminal DataAccessOperation without proc/SQL
T21 project_sequence
T22 evidence/ID traceability
T23 stable flow IDs
T24 stable path IDs
T25 no unresolved call promotion
T26 R1.1 call graph unchanged
T27 R2 entry points unchanged
T28 R3.1 data-access indexes unchanged
T29 no secret reintroduced in flow evidence
T30 performance/indexed traversal sanity

Add more if required.

---

## R4-24 SECURITY

R3.1 security guarantees remain mandatory.

Do not copy unsanitized evidence from source indexes into flow outputs.

All exported R4 evidence must use centralized sanitizer.

No credentials/secrets.

Regression test required.

---

## R4-25 REGRESSION

Must preserve approved metrics/content for:

* calls
* entry_points
* event_bindings
* data_access
* stored_procedures
* sql_operations
* data_parameters

R4 is additive.

Do NOT modify their semantic resolution unless required to fix an explicit bug.

If an upstream bug is discovered:
STOP and report it.
Do not silently redesign upstream phase.

---

## R4-26 ACCEPTANCE

PASS only if:

* all existing tests PASS
* R4 tests PASS
* functional flows generated deterministically
* confirmed calls only used for confirmed traversal
* unresolved boundaries preserved
* cycles safe
* depth bounded
* branching preserved
* paths deduplicated
* DB endpoints linked
* cross-project flows supported
* source traceability preserved
* no secrets exposed
* upstream indexes unchanged materially
* no V2-R5 implementation

---

## VALIDATION

Run:

python -m unittest discover -s tests

Then:

* fixture validation
* internal validation

DO NOT automatically run full real 14k-file repository.

No LLM dependency.

---

## REPORT

Create only:

codex/V2/V2_R4_RESULTADO.md

FORMAT:

STATUS
FILES_CHANGED
TESTS
OUTPUTS
FLOW_MODEL
TRAVERSAL_RULES
CYCLE_HANDLING
BRANCHING
TERMINALS
PERFORMANCE
SECURITY
REGRESSION
INTERNAL_METRICS
KNOWN_LIMITATIONS
REAL_VALIDATION_COMMAND
NEXT

Machine-oriented.
Compact.
No ZIP.
No additional reports.

---

## REAL VALIDATION COMMAND

Recommend:

python main.py "E:\IAProyectos\revision\revision-main" --output "output\v2_r4_full" --verbose

Do not execute automatically.

---

## STOP

After implementation + tests:

STOP.

Expected:

V2-R4 ready for full real validation.
V2-R5 NOT STARTED.
