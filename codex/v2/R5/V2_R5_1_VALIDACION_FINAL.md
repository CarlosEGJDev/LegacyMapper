TASK: Perform final full-real validation of LegacyMapper V2-R5.1.

VALIDATION ONLY.

DO NOT modify code.
DO NOT modify legacy source.
DO NOT repair defects during validation.
DO NOT introduce LLM processing.
DO NOT start any phase beyond V2-R5.1.

==================================================
BASELINE
========

Approved:

V1=CLOSED
V2-R1.1=APPROVED
V2-R2=APPROVED
V2-R3.1=APPROVED
V2-R4.1=APPROVED

R5 original validation:

`V2-R5_REQUIERE_CORRECCIONES`

R5 blocking defect:

nodes=108104
edges=438672
orphan_edge_sources=241935
orphan_edge_targets=255899

R5 also had excessive graph/detail duplication.

R5.1 implementation status:

`V2-R5_1_READY_FOR_FULL_REAL_VALIDATION`

R5.1 intended corrections:

* graph edges require materialized endpoints
* individual unresolved-call nodes/edges omitted from architecture graph
* DAO->Parameter edges omitted from architecture graph
* unresolved evidence preserved outside architecture graph
* parameter evidence preserved outside architecture graph
* functional paths globally stored instead of repeated per flow
* R4.1 flow/path identities preserved
* traceability remains ID/reference based

Implementation tests:

51 PASS

==================================================
INPUT
=====

Corrected output:

`output/v2_r5_1_full/`

Original R5 comparison baseline:

`output/v2_r5_full/`

Required corrected artifacts:

`output/v2_r5_1_full/ai_context/SYSTEM_CONTEXT.json`
`output/v2_r5_1_full/ai_context/SYSTEM_CONTEXT.md`
`output/v2_r5_1_full/ai_context/ARCHITECTURE_GRAPH.json`
`output/v2_r5_1_full/ai_context/FUNCTIONAL_FLOWS.json`
`output/v2_r5_1_full/ai_context/TRACEABILITY.json`

Use corrected upstream indexes from:

`output/v2_r5_1_full/index/`

Read:

`codex/V2/V2_R5_VALIDACION_REAL.md`
`codex/V2/V2_R5_1_RESULTADO.md`
`codex/V2/V2_R4_1_REPRODUCIBILIDAD_RESULTADO.md`

==================================================
SOURCE BASELINE
===============

Expected:

SOURCE_FILE_COUNT=4328

SOURCE_SNAPSHOT_SHA256=
6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

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
paths_to_stored_procedure=1121
paths_to_sql=1
paths_to_data_operation=4612
cross_project_flows=2187
dead_end_paths=1372
max_observed_depth=6

==================================================

1. ARTIFACTS
   ==================================================

Verify all five corrected R5 artifacts exist and parse.

Report for each:

* path
* bytes
* parse/read status

Required:
all present and valid.

==================================================
2. SOURCE SNAPSHOT
==================

Verify:

source_file_count=4328

source_snapshot_sha256=
6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

Verify source repository was not modified by R5.1.

Mismatch requires investigation.

==================================================
3. GRAPH INTEGRITY — BLOCKING CHECK
===================================

Load corrected:

`ARCHITECTURE_GRAPH.json`

Calculate independently:

node_count
edge_count
unique_node_ids
duplicate_node_ids
duplicate_logical_edges
orphan_edge_sources
orphan_edge_targets

Do NOT trust stored graph statistics alone.

For every edge:

source MUST exist in node IDs.
target MUST exist in node IDs.

REQUIRED:

duplicate_node_ids=0
duplicate_logical_edges=0
orphan_edge_sources=0
orphan_edge_targets=0

Any orphan endpoint = HIGH.

Any systematic duplicate-ID defect = HIGH.

==================================================
4. GRAPH CORRECTION COMPARISON
==============================

Compare R5 vs R5.1.

Original R5:

nodes=108104
edges=438672
orphan sources=241935
orphan targets=255899

Report corrected:

nodes
edges
orphan sources
orphan targets

Report:

node_reduction
edge_reduction
percentage_node_reduction
percentage_edge_reduction

Determine whether correction actually removed noise rather than merely hiding integrity errors.

==================================================
5. GRAPH NODE POLICY
====================

Count node types.

Verify architecture graph no longer blindly materializes:

* individual unresolved calls
* DAO parameters
* low-value evidence/member records

Verify high-value types remain where supported:

* Repository
* Solution
* Project
* DLL
* Namespace/Class/Interface where implemented
* WebForm
* Event
* Handler
* Method
* DataAccessOperation
* StoredProcedure
* SQL

Report intentionally omitted categories.

Check omission does NOT remove their detailed facts from overall R5 model.

==================================================
6. GRAPH EDGE POLICY
====================

Count relation types.

Verify retained edges have materialized endpoints.

Sample >=50 graph edges across major relation types.

Cross-check against upstream indexes.

Prioritize:

Solution -> Project
Project -> Project
Project -> DLL
Namespace -> Class
Class -> BaseClass
WebForm -> Class
WebForm -> Event
Event -> Handler
Handler -> Method
Method -> Method
Method -> DataAccessOperation
DataAccessOperation -> StoredProcedure
DataAccessOperation -> SQL

Classify sample:

CORRECT
SUSPICIOUS
INCORRECT

Report precision.

No relation may be created only from naming assumptions.

==================================================
7. UNRESOLVED COMPACTION
========================

Verify individual unresolved-call graph noise is removed/compacted.

Original graph:

UnresolvedCall nodes=70751
Method->UnresolvedCall edges=130943

Report corrected counts.

REQUIRED:

Architecture graph must not reproduce the original individual unresolved-call explosion.

Then verify unresolved facts remain available through:

FUNCTIONAL_FLOWS
TRACEABILITY
upstream indexes

Expected R4.1 unresolved boundaries:

162914

Sample >=30 unresolved paths/boundaries.

Verify:

* unresolved remains unresolved
* evidence/reference retained
* no target guessing
* no confidence promotion

==================================================
8. PARAMETER COMPACTION
=======================

Original graph contained:

DataAccessOperation->Parameter=74633

Verify corrected architecture graph does not require individual parameter nodes/edges.

Expected upstream parameters remain:

74633

Verify parameter detail remains accessible through upstream/R5 references.

Sample >=20 data operations with parameters.

No parameter information may be semantically lost from overall model.

==================================================
9. FUNCTIONAL FLOWS INTEGRITY
=============================

Load:

`FUNCTIONAL_FLOWS.json`

Verify:

flows=12642
paths=170020

Calculate:

unique_flow_ids
unique_path_ids
duplicate_flow_ids
duplicate_path_ids
duplicate_logical_paths

REQUIRED:

unique_flow_ids=12642
unique_path_ids=170020
duplicate_flow_ids=0
duplicate_path_ids=0
duplicate_logical_paths=0

Compare R5.1 path ID set with approved R4.1 path ID set.

Required:

lost_path_ids=0
added_path_ids=0

Do same for flow IDs.

==================================================
10. FUNCTIONAL FLOW SEMANTICS
=============================

Verify compact representation did not alter semantics.

Sample >=40 paths.

Cross-check against R4.1:

* ordered nodes
* relation_types
* terminal_type
* terminal_target
* confidence
* evidence references

Required:

same path ID must represent same logical path.

Any ID reused for altered semantics = CRITICAL.

==================================================
11. BRANCH PRESERVATION
=======================

Sample >=20 multi-path flows.

Verify:

* all legitimate branches retained
* ordering retained
* DB terminal branches retained
* unresolved branches retained
* same endpoint through distinct chains remains distinct
* no path collapse due to compaction

Report:

lost_branches
added_branches
changed_branches

Required:
0 unexplained semantic differences.

==================================================
12. DB TERMINALS
================

Validate R4.1 terminal baseline:

paths_to_stored_procedure=1121
paths_to_sql=1
paths_to_data_operation=4612

Verify associations survive compaction.

Sample >=30 DB-reaching paths.

Check:

Method
-> DataAccessOperation
-> StoredProcedure/SQL

Broken terminal reference = HIGH.

==================================================
13. TRACEABILITY INTEGRITY
==========================

Load:

`TRACEABILITY.json`

Calculate independently:

broken references
orphan IDs
missing flow IDs
missing path IDs
missing DAO IDs
missing SP IDs
missing SQL IDs

Validate:

WebForm -> EntryPoint
EntryPoint -> Flow
Flow -> Path
Path -> Call references
Path -> DAO
Path -> StoredProcedure
Path -> SQL
Symbol -> physical declarations
Project -> source files

Required:
no systematic broken references.

==================================================
14. TRACEABILITY ROUND TRIP
===========================

Perform >=30 round trips.

Forward:

WebForm
-> EntryPoint
-> Flow
-> Path
-> Method
-> DataAccessOperation
-> StoredProcedure/SQL

Reverse where supported:

StoredProcedure
-> Path
-> Flow
-> EntryPoint
-> WebForm

Also test:

Project
-> Symbol/Source
-> graph representation/reference

Report:

PASS
PARTIAL
FAIL

Approval requires functional/database round trip PASS.

==================================================
15. GRAPH VS TRACEABILITY SEPARATION
====================================

Verify intended responsibility separation:

ARCHITECTURE_GRAPH:
compact structural/functional navigation.

TRACEABILITY:
detailed ID/reference navigation.

FUNCTIONAL_FLOWS:
ordered functional execution paths.

SYSTEM_CONTEXT:
integrated summary/index.

Confirm compaction did not simply delete information required downstream.

Classify:

CLEAN_SEPARATION
PARTIAL_SEPARATION
INFORMATION_LOSS

INFORMATION_LOSS = blocking.

==================================================
16. AI USABILITY
================

Using corrected R5 artifacts and their upstream references, verify support for:

Q1 Which WebForms reach stored procedure X?
Q2 Which procedures are reachable from WebForm Y?
Q3 Which projects participate in functional flow Z?
Q4 Which handlers reach data access?
Q5 Which unresolved boundaries exist in flow Z?
Q6 What is the ordered path from event X to DB endpoint Y?
Q7 Which project/class owns method X?
Q8 Which flows cross projects?

Classify each:

SUPPORTED
PARTIALLY_SUPPORTED
NOT_SUPPORTED

Core Q1-Q6 must be SUPPORTED for approval.

No AI execution required.

==================================================
17. SYSTEM_CONTEXT
==================

Verify SYSTEM_CONTEXT.json remains compact/integrated.

Check:

* source metadata
* repository
* solutions/projects
* web
* symbols
* calls summary
* data-access summary
* functional summary/references
* statistics
* warnings

Ensure full calls/path/evidence indexes were not newly duplicated into SYSTEM_CONTEXT.

Classification:

PASS
TOO_VERBOSE
INCOMPLETE

==================================================
18. SYSTEM_CONTEXT.MD
=====================

Verify Markdown remains:

* factual
* compact
* portable
* free of unsupported business narrative
* useful as AI bootstrap context
* free of secrets

Report bytes.

==================================================
19. FILE SIZE COMPARISON
========================

Report exact R5 and R5.1 sizes.

Original R5:

SYSTEM_CONTEXT.json=6070127
ARCHITECTURE_GRAPH.json=139390147
FUNCTIONAL_FLOWS.json=144309946
TRACEABILITY.json=59358789
SYSTEM_CONTEXT.md=871

Report R5.1 values.

Calculate per artifact:

byte_difference
percentage_change

Also calculate:

TOTAL_R5_BYTES
TOTAL_R5_1_BYTES
TOTAL_REDUCTION_BYTES
TOTAL_REDUCTION_PERCENT

Do not require arbitrary size target.

Classify:

MATERIALLY_IMPROVED
MINOR_IMPROVEMENT
NO_IMPROVEMENT
REGRESSION

==================================================
20. DUPLICATION / NOISE
=======================

Inspect whether R5.1 still unnecessarily repeats:

* full call records
* full evidence bodies
* path metadata inside every flow
* parameter records
* unresolved call records
* complete upstream objects

Report major duplication sources.

Classify:

COMPACT
ACCEPTABLE
EXCESSIVE

Approval requires COMPACT or ACCEPTABLE.

==================================================
21. PERFORMANCE
===============

Assess corrected real-scale artifacts.

Report:

* parse success
* largest artifact
* node/edge scale
* flow/path scale
* obvious memory/output explosion
* pathological representation symptoms

Classify:

PRACTICAL
BORDERLINE
UNSUITABLE

Approval requires PRACTICAL or justified BORDERLINE with no downstream blocker.

==================================================
22. CONFIDENCE SEPARATION
=========================

Verify:

confirmed -> confirmed
inferred -> inferred
unresolved -> unresolved

Search for:

* confidence promotion
* guessed target
* guessed project role
* guessed architecture layer
* invented business meaning

Any systematic invention = CRITICAL.

==================================================
23. PORTABILITY
===============

Check all five artifacts for absolute Windows paths.

Allowed:

source repository root only in snapshot metadata.

Report:

absolute_internal_references
metadata_root_references

Internal artifact navigation should use relative/stable references.

Classify:

PASS
MINOR
BLOCKING

==================================================
24. SECURITY — EXHAUSTIVE
=========================

Perform exhaustive scan of all five R5.1 artifacts.

Check for actual unsanitized:

password
pwd
credential
token
secret
connection-string credentials
authentication secrets
database login values

Also inspect evidence/reference structures for sanitizer bypass.

Do NOT reproduce secret values in report.

Report only:

matches_checked
confirmed_secret_leaks
false_positive_categories

Required:

confirmed_secret_leaks=0

Any actual secret exposure = CRITICAL.

==================================================
25. DETERMINISM — FULL REAL
===========================

Full real determinism proof is required before V2 closure.

Generate second corrected run:

`output/v2_r5_1_repro/`

Allowed command:

`python main.py "C:\Users\cgalianj\source\IST_40\operacional" --output "output\v2_r5_1_repro" --verbose`

Do not modify source/code between runs.

Compare all five R5 artifacts.

For JSON:

canonical semantic comparison/hash.

For Markdown:

compare content after excluding ONLY explicitly allowed nondeterministic metadata, if any.

Report for every artifact:

semantic_equal
canonical_sha256 where practical
only_left
only_right
changed_records

REQUIRED:

all semantic_equal=true

Unexpected semantic difference = HIGH.

==================================================
26. SOURCE REPRODUCIBILITY
==========================

Calculate current VB source fingerprint using approved method:

sorted tuples:

relative_path
file_size
file-content SHA-256

Expected:

SOURCE_FILE_COUNT=4328

SOURCE_SNAPSHOT_SHA256=
6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

Second R5.1 run must use same fingerprint.

Mismatch = investigate before decision.

==================================================
27. UPSTREAM REGRESSION
=======================

Verify corrected full output AND reproducibility output preserve:

CALLS
230356
confirmed=12775
unresolved=217581
inferred=0

R2
entry_points=12662
event_bindings=12662

R3.1
data_access=20082
confirmed=20073
Method->DataAccessOperation=9771
operations_method_null=0
stored_procedures=5389
sql_operations=3
parameters=74633

R4.1
flows=12642
paths=170020
duplicate_path_ids=0
duplicate_logical_paths=0
unresolved_boundaries=162914

Any unexplained semantic delta = HIGH.

==================================================
28. SOURCE IMMUTABILITY
=======================

Confirm validation/R5.1 did not modify legacy source.

Use fingerprint evidence.

Do not assume mismatch was caused by LegacyMapper without evidence.

Required:
approved fingerprint preserved.

==================================================
29. R5.1 COMPLETENESS
=====================

Evaluate whether corrected R5 now provides a complete reusable intermediate system model.

Must support:

* repository structure
* solution/project structure
* WebForm surface
* symbol model
* call summary
* data-access model
* functional execution paths
* compact architecture graph
* detailed traceability
* confidence separation
* deterministic IDs
* source snapshot identity
* portable AI context

Classify:

COMPLETE
COMPLETE_WITH_NONBLOCKING_LIMITATIONS
INCOMPLETE

==================================================
30. DEFECT SEVERITY
===================

Classify all findings:

CRITICAL
HIGH
MEDIUM
LOW

CRITICAL/HIGH block V2 closure.

MEDIUM/LOW may remain only if they do not materially affect:

* factual reliability
* graph integrity
* functional semantics
* traceability
* determinism
* portability
* security
* downstream AI usability

==================================================
31. FINAL DECISION
==================

Return EXACTLY one:

A) V2-R5_1_APROBADA_V2_COMPLETA
B) V2-R5_1_REQUIERE_CORRECCIONES
C) V2-R5_1_NO_CONFIABLE

A requires:

* all 5 artifacts valid
* source fingerprint PASS
* orphan graph sources=0
* orphan graph targets=0
* duplicate graph nodes=0
* duplicate logical graph edges=0
* graph factuality PASS
* graph noise materially corrected
* flows=12642
* paths=170020
* R4.1 flow/path IDs preserved
* branch semantics preserved
* DB terminals preserved
* unresolved state preserved
* traceability integrity PASS
* functional/database round trip PASS
* AI core Q1-Q6 SUPPORTED
* confidence separation PASS
* portability acceptable
* file-size/noise acceptable
* exhaustive security PASS
* full-real deterministic reproduction PASS
* upstream regression PASS
* source immutability PASS
* no CRITICAL
* no blocking HIGH

If approved:

record exactly:

`V2 COMPLETE`

==================================================
OUTPUT
======

Create ONLY:

`codex/V2/V2_R5_1_VALIDACION_FINAL_RESULTADO.md`

FORMAT:

STATUS
ARTIFACTS
SOURCE_SNAPSHOT
GRAPH_INTEGRITY
GRAPH_COMPARISON
GRAPH_NODE_POLICY
GRAPH_EDGE_POLICY
GRAPH_FACTUALITY
UNRESOLVED_COMPACTION
PARAMETER_COMPACTION
FUNCTIONAL_FLOWS
FLOW_SEMANTICS
BRANCH_PRESERVATION
DB_TERMINALS
TRACEABILITY
TRACEABILITY_ROUND_TRIP
GRAPH_TRACEABILITY_SEPARATION
AI_USABILITY
SYSTEM_CONTEXT
MARKDOWN_CONTEXT
FILE_SIZE_COMPARISON
DUPLICATION_NOISE
PERFORMANCE
CONFIDENCE_SEPARATION
PORTABILITY
SECURITY
DETERMINISM
SOURCE_REPRODUCIBILITY
UPSTREAM_REGRESSION
SOURCE_IMMUTABILITY
R5_1_COMPLETENESS
REQUIRED_FIXES
DECISION

Machine-oriented.
Compact.
No ZIP.
No code changes.
No additional reports.
No phase beyond V2-R5.1.

If decision=A:
append:

`V2 COMPLETE`

and STOP.
