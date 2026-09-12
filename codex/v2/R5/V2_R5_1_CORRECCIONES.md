TASK: Apply minimal corrective revision V2-R5.1.

DO NOT modify legacy source.
DO NOT modify approved V1/R1.1/R2/R3.1/R4.1 semantics.
DO NOT redesign functional flow resolution.
DO NOT introduce LLM processing.
DO NOT start any phase beyond V2-R5.1.

SOURCE:

`codex/V2/V2_R5_VALIDACION_REAL.md`

CURRENT DECISION:

`V2-R5_REQUIERE_CORRECCIONES`

==================================================
VALIDATED DEFECTS
=================

HIGH:

ARCHITECTURE_GRAPH integrity failure.

Current real output:

nodes=108104
edges=438672
duplicate_nodes=0
duplicate_edges=0
orphan_edge_sources=241935
orphan_edge_targets=255899

Cause identified by validation:

Functional/dependency edges are exported although corresponding graph source/target nodes are not always materialized.

R5 cannot be approved while graph edges reference missing nodes.

MEDIUM:

Graph representation is excessively noisy/duplicated.

Current examples:

UnresolvedCall nodes=70751
Method nodes=14181
Event nodes=12638
WebForm nodes=3346

Large relation categories include:

Method->UnresolvedCall=130943
Method->Method=108280
DataAccessOperation->Parameter=74633

Current files:

ARCHITECTURE_GRAPH.json ≈139 MB
FUNCTIONAL_FLOWS.json ≈144 MB
TRACEABILITY.json ≈59 MB

Goal is not merely smaller files.

Goal is a coherent reusable architectural/functional model with detailed evidence available through upstream indexes and traceability.

==================================================
R5.1-01 GRAPH INTEGRITY RULE
============================

Every exported architecture edge MUST reference existing graph nodes.

Required after generation:

orphan_edge_sources=0
orphan_edge_targets=0
duplicate_nodes=0
duplicate_logical_edges=0

Never export an edge whose source or target node is absent.

Implement explicit graph integrity validation before export.

If an invalid edge is detected:

* skip/aggregate it only according to deterministic graph policy; or
* fail generation if the edge is expected to have materialized endpoints.

Do not silently export broken references.

==================================================
R5.1-02 DO NOT FIX BY BLIND NODE MATERIALIZATION
================================================

Do NOT solve orphan edges by materializing every low-value source/target object.

Specifically do not automatically add hundreds of thousands of:

* unresolved call expression nodes
* parameter nodes
* source-file member nodes
* duplicated functional-path nodes
* transient evidence nodes

ARCHITECTURE_GRAPH is an architectural/functional navigation graph, not a copy of every index.

Detailed records remain accessible through:

* TRACEABILITY.json
* FUNCTIONAL_FLOWS.json
* output/index/*

==================================================
R5.1-03 ARCHITECTURE GRAPH PURPOSE
==================================

The graph should support high-value navigation such as:

Repository
-> Solution
-> Project

Project
-> Project
Project
-> DLL

Namespace
-> Class

Class
-> BaseClass

WebForm
-> Class
WebForm
-> Event
Event
-> Handler
Handler
-> Method

Method
-> Method

Method
-> DataAccessOperation

DataAccessOperation
-> StoredProcedure
DataAccessOperation
-> SQL

Optional unresolved representation should be compact.

Do not represent every unresolved call as its own graph node unless required for architecture navigation.

==================================================
R5.1-04 UNRESOLVED CALL COMPACTION
==================================

Current graph has excessive unresolved-call noise.

Do NOT discard unresolved facts.

Instead separate architecture representation from detailed traceability.

Preferred approach:

Architecture graph:

Method
-> UnresolvedBoundary

where UnresolvedBoundary may be deterministic aggregate by caller/method/project or another compact stable grouping.

Detailed unresolved call evidence remains in:

* functional flows
* traceability
* upstream calls index

Alternative acceptable approach:

omit Method->UnresolvedCall edges entirely from ARCHITECTURE_GRAPH if unresolved calls remain fully navigable via traceability.

Whichever policy is chosen:

* document it
* apply deterministically
* preserve factual unresolved status
* never promote unresolved to confirmed
* do not lose detailed source evidence from the overall R5 model

==================================================
R5.1-05 PARAMETER EDGE COMPACTION
=================================

Do not require every DataAccessOperation->Parameter relationship inside architecture graph.

Parameters are detailed data-access evidence.

Prefer keeping parameter detail in:

* R3.1 index
* SYSTEM_CONTEXT data-access summaries/references
* TRACEABILITY

Architecture graph may represent:

Method
-> DataAccessOperation
-> StoredProcedure/SQL

without individual parameter nodes.

If parameter nodes are retained, they must provide clear architectural value and all endpoints must exist.

==================================================
R5.1-06 FUNCTIONAL FLOW REPRESENTATION
======================================

Do NOT alter R4.1 semantic flows.

Required preservation:

flows=12642
paths=170020
duplicate_path_ids=0
duplicate_logical_paths=0

FUNCTIONAL_FLOWS.json may be compacted only if:

* all R4.1 flow IDs preserved
* all path IDs preserved
* ordered path semantics preserved
* terminal associations preserved
* unresolved boundaries preserved
* confidence preserved
* traceability allows reconstruction/navigation

Prefer references over repeated full node/evidence structures.

Do NOT regenerate path identity.

==================================================
R5.1-07 FUNCTIONAL_FLOWS SIZE REDUCTION
=======================================

Inspect current duplication.

Reduce repeated structures where practical.

Possible compact representation:

{
"flows": [
{
"flow_id": "...",
"entry_point_id": "...",
"path_ids": [...]
}
],
"paths": [
{
"path_id": "...",
"ordered_node_refs": [...],
"relation_types": [...],
"terminal": {...},
"confidence": "...",
"evidence_refs": [...]
}
]
}

Do not duplicate identical node metadata inside every path.

Central dictionaries/indexes may be used where useful.

Semantic equivalence with R4.1 is mandatory.

==================================================
R5.1-08 TRACEABILITY COMPACTION
===============================

TRACEABILITY must remain navigable but should not duplicate complete R5 structures.

Prefer mappings:

ID -> IDs/references

instead of:

ID -> copied full object

Example:

flow_id -> path_ids
path_id -> call_refs / dao_ids / sp_ids / sql_ids
entry_point_id -> flow_id
webform -> entry_point_ids

Do not duplicate full evidence bodies already available upstream.

==================================================
R5.1-09 SYSTEM_CONTEXT
======================

SYSTEM_CONTEXT.json already passed validation.

Do not expand it.

Preserve compact summaries/reference model.

Any changes should only reflect updated R5 artifact statistics/references.

SYSTEM_CONTEXT.md already passed.

Do not turn it into a large report.

==================================================
R5.1-10 GRAPH NODE POLICY
=========================

Define explicit deterministic node policy.

Each node type must have:

* stable ID
* type
* compact label/name
* confidence where relevant
* upstream reference

Suggested high-value node types:

Repository
Solution
Project
Namespace
Class
Interface
WebForm
Event
Handler
Method
DLL
DataAccessOperation
StoredProcedure
SQL
UnresolvedBoundary

Only add SourceFile/Parameter/etc. if justified.

Document included and intentionally excluded node categories.

==================================================
R5.1-11 GRAPH EDGE POLICY
=========================

Define allowed edge relations explicitly.

Before exporting:

if source node does not exist:
do not export edge

if target node does not exist:
do not export edge

Every retained edge must be useful and backed by upstream evidence/reference.

Deduplicate using canonical identity:

source_id
+
relation
+
target_id
+
confidence where materially necessary

==================================================
R5.1-12 GRAPH INTEGRITY VALIDATOR
=================================

Implement validator/check producing metrics:

node_count
edge_count
duplicate_node_ids
duplicate_logical_edges
orphan_edge_sources
orphan_edge_targets
node_types
relation_types

Generation/internal validation must fail if:

orphan_edge_sources > 0
orphan_edge_targets > 0
duplicate_node_ids > 0

==================================================
R5.1-13 TRACEABILITY ROUND TRIP
===============================

Preserve/strengthen round-trip navigation:

WebForm
-> EntryPoint
-> Flow
-> Path
-> Method
-> DataAccessOperation
-> StoredProcedure/SQL

Reverse where indexes allow:

StoredProcedure
-> paths
-> flows
-> entry points
-> WebForms

Graph compaction must not destroy this capability.

TRACEABILITY is the detailed navigation layer.

ARCHITECTURE_GRAPH is the compact structural/functional graph.

==================================================
R5.1-14 OUTPUT SIZE TARGET
==========================

No arbitrary hard size threshold is mandatory.

However, corrected representation should materially reduce unnecessary duplication/noise.

Report before/after sizes for:

SYSTEM_CONTEXT.json
ARCHITECTURE_GRAPH.json
FUNCTIONAL_FLOWS.json
TRACEABILITY.json
SYSTEM_CONTEXT.md

Expected:

ARCHITECTURE_GRAPH materially smaller than current ~139 MB.

FUNCTIONAL_FLOWS/TRACEABILITY should also reduce if duplication is found.

Do not sacrifice semantic completeness solely to meet a file-size target.

==================================================
R5.1-15 DETERMINISM
===================

Preserve deterministic behavior.

No:

* random UUID
* Python hash()
* timestamps in IDs
* unstable collection ordering

All collections with semantic comparison significance must be sorted canonically.

R4.1 flow/path IDs remain unchanged.

==================================================
R5.1-16 SECURITY
================

Continue centralized sanitizer usage.

After compaction, ensure no code path bypasses sanitizer.

No:

* passwords
* pwd values
* credentials
* tokens
* secret connection strings
* authentication secret values

Do not reproduce secret values in reports/tests.

==================================================
R5.1-17 REGRESSION
==================

Must preserve upstream baselines.

Calls:

total=230356
confirmed=12775
unresolved=217581
inferred=0

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

R4.1:

flows=12642
paths=170020
duplicate_path_ids=0
duplicate_logical_paths=0
unresolved_boundaries=162914

R5.1 must not change upstream extraction/resolution.

==================================================
R5.1-18 TESTS
=============

Preserve all existing tests.

Add tests covering at minimum:

T01 graph edge source always exists
T02 graph edge target always exists
T03 orphan_edge_sources=0
T04 orphan_edge_targets=0
T05 duplicate graph nodes=0
T06 duplicate graph edges=0
T07 unresolved compaction preserves unresolved state
T08 unresolved detail remains traceable
T09 parameter detail remains traceable when omitted from graph
T10 graph does not blindly materialize all unresolved calls
T11 graph does not require all parameter nodes
T12 flow IDs preserved
T13 path IDs preserved
T14 path count preserved
T15 branch semantics preserved
T16 DB endpoints preserved
T17 unresolved boundaries preserved
T18 confidence preserved
T19 flow/path compact references valid
T20 traceability flow->path
T21 traceability path->DAO
T22 traceability path->SP
T23 traceability path->SQL
T24 reverse SP->path/flow where supported
T25 no traceability orphan IDs
T26 SYSTEM_CONTEXT remains valid
T27 Markdown remains factual/compact
T28 deterministic graph generation
T29 deterministic compact flows
T30 deterministic traceability
T31 sanitizer applied
T32 no secret leakage
T33 upstream calls unchanged
T34 R2 unchanged
T35 R3.1 unchanged
T36 R4.1 unchanged
T37 no LLM/network dependency
T38 no legacy source modification
T39 graph scale sanity
T40 compact representation avoids repeated full evidence

Run:

`python -m unittest discover -s tests`

All tests must PASS.

==================================================
R5.1-19 INTERNAL VALIDATION
===========================

Run fixture/internal validation only after implementation.

Required:

all 5 R5 artifacts generated

graph:

orphan_edge_sources=0
orphan_edge_targets=0
duplicate_nodes=0
duplicate_edges=0

traceability:

broken references=0

functional:

flow IDs preserved
path IDs preserved
branch semantics preserved
confidence preserved

security:

PASS

determinism:

PASS on repeated internal fixture generation

Do NOT automatically run full real repository.

==================================================
R5.1-20 FILES
=============

Modify only R5 implementation/tests required by this correction.

Prefer changes within existing R5 components.

Do not alter R1-R4 resolvers unless a blocking upstream defect is discovered.

If such defect is discovered:

STOP.
Report it.
Do not silently patch an approved phase.

==================================================
R5.1-21 REAL VALIDATION COMMAND
===============================

Do NOT execute automatically.

Use:

`python main.py "C:\Users\cgalianj\source\IST_40\operacional" --output "output\v2_r5_1_full" --verbose`

==================================================
R5.1-22 ACCEPTANCE
==================

R5.1 is ready for full real validation only if:

* all tests PASS
* all five R5 artifacts generated
* orphan graph sources=0
* orphan graph targets=0
* duplicate graph nodes=0
* duplicate logical graph edges=0
* graph representation materially less noisy
* architecture graph remains useful
* R4.1 flows/path IDs preserved
* functional semantic completeness preserved
* traceability round trip preserved
* confidence separation preserved
* deterministic behavior PASS
* centralized sanitization PASS
* no upstream regression
* no LLM dependency
* no legacy source modification

==================================================
REPORT
======

Create ONLY:

`codex/V2/V2_R5_1_RESULTADO.md`

FORMAT:

STATUS
FILES_CHANGED
TESTS
GRAPH_ROOT_CAUSE
GRAPH_NODE_POLICY
GRAPH_EDGE_POLICY
GRAPH_INTEGRITY
UNRESOLVED_COMPACTION
PARAMETER_COMPACTION
FUNCTIONAL_FLOW_COMPACTION
TRACEABILITY_COMPACTION
OUTPUT_SIZE
DETERMINISM
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

Expected final status:

`V2-R5_1_READY_FOR_FULL_REAL_VALIDATION`

STOP after implementation/tests/internal validation.
