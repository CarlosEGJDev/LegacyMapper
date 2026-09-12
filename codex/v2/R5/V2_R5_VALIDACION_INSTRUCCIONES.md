TASK: Validate LegacyMapper V2-R5 against the full real repository.

VALIDATION ONLY.

DO NOT modify code.
DO NOT modify legacy source.
DO NOT regenerate outputs unless required only for deterministic comparison.
DO NOT introduce LLM processing.
DO NOT start any phase beyond V2-R5.

==================================================
BASELINE
========

APPROVED:

V1 = CLOSED
V2-R1.1 = APPROVED
V2-R2 = APPROVED
V2-R3.1 = APPROVED
V2-R4.1 = APPROVED

R5 implementation status:

`V2-R5_READY_FOR_FULL_REAL_VALIDATION`

Implementation tests:

* 51 PASS

Current source snapshot:

SOURCE_FILE_COUNT=4328

SOURCE_SNAPSHOT_SHA256=
`6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a`

Current approved call baseline:

* calls_total=230356
* confirmed=12775
* inferred=0
* unresolved=217581

R2:

* entry_points=12662
* event_bindings=12662

R3.1:

* data_access=20082
* confirmed_data_access=20073
* Method->DataAccessOperation=9771
* operations_method_null=0
* stored_procedures=5389
* sql_operations=3
* parameters=74633

R4.1:

* flows=12642
* paths=170020
* duplicate_path_ids=0
* duplicate_logical_paths=0
* paths_to_stored_procedure=1121
* paths_to_sql=1
* paths_to_data_operation=4612
* unresolved_boundaries=162914
* dead_end_paths=1372
* cross_project_flows=2187
* max_observed_depth=6
* errors=0

==================================================
INPUT
=====

Primary output:

`output/v2_r5_full/`

Required R5 artifacts:

* `output/v2_r5_full/ai_context/SYSTEM_CONTEXT.json`
* `output/v2_r5_full/ai_context/SYSTEM_CONTEXT.md`
* `output/v2_r5_full/ai_context/ARCHITECTURE_GRAPH.json`
* `output/v2_r5_full/ai_context/FUNCTIONAL_FLOWS.json`
* `output/v2_r5_full/ai_context/TRACEABILITY.json`

Upstream indexes under:

`output/v2_r5_full/index/`

Use them as factual source for validation.

Also read:

* `codex/V2/V2_R5_RESULTADO.md`
* `codex/V2/V2_R4_1_REPRODUCIBILIDAD_RESULTADO.md`
* `codex/V2/V2_R4_1_VALIDACION_REAL.md`

==================================================
GOAL
====

Determine whether the R5 intermediate system model is:

* factually consistent with approved indexes
* deterministic
* internally coherent
* traceable
* portable
* secure
* compact enough for downstream use
* suitable for humans and future AI interpretation
* free from semantic invention

R5 must be validated as an integration layer, NOT as a new extractor.

==================================================

1. ARTIFACT AVAILABILITY
   ==================================================

Confirm all 5 artifacts exist.

Report:

* file path
* size bytes
* valid JSON/Markdown
* parse status

REQUIRED:
all 5 present and readable.

Missing primary artifact = HIGH.

==================================================
2. SOURCE SNAPSHOT METADATA
===========================

Verify SYSTEM_CONTEXT metadata contains current source identity.

Expected:

SOURCE_FILE_COUNT=4328

SOURCE_SNAPSHOT_SHA256=
6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

Verify:

* source repository metadata
* model/version metadata
* upstream phase references
* confidence model
* source indexes

Report mismatches.

Wrong source fingerprint = HIGH.

==================================================
3. SYSTEM_CONTEXT STRUCTURE
===========================

Validate SYSTEM_CONTEXT.json top-level model.

Check presence/usefulness of:

* metadata
* repository
* solutions
* projects
* web
* symbols
* configuration
* dependencies
* calls
* data_access
* functional
* statistics
* warnings

Exact naming may differ only if implementation convention is coherent.

Check that it is an integrated summary/reference model rather than a blind full duplication of upstream indexes.

Report:

* total size
* major sections
* embedded full-index duplication detected
* compact-reference behavior

Classify:
PASS
TOO_VERBOSE
INCOMPLETE

==================================================
4. REPOSITORY / PROJECT MODEL
=============================

Cross-check repository/project facts against V1 indexes.

Verify sample >=25 projects/solutions where available:

* solution -> project
* project path
* target framework
* RootNamespace
* AssemblyName
* project references
* DLL references
* source references

Check:

* no invented project roles
* no folder-name architecture inference
* relative path portability

Classify sampled records:
CORRECT
SUSPICIOUS
INCORRECT

Report precision.

==================================================
5. WEB MODEL
============

Sample >=30 WebForms across ASPX/ASCX/Master where available.

Verify:

* path/type
* inherits
* codebehind
* class linkage
* entry-point references
* registered control/namespace references where represented

Cross-check against:

* webforms.json
* entry_points.json
* event_bindings.json

No fabricated relationship allowed.

Report:

* broken webform references
* missing entry-point references
* incorrect ownership

==================================================
6. SYMBOL MODEL
===============

Sample >=30 logical symbols.

Verify where available:

* effective_namespace
* declared_namespace
* root_namespace
* project_path
* namespace_confidence
* physical declarations
* inheritance/interfaces

Cross-check against symbols/logical_symbols indexes.

Ensure partial declarations are not incorrectly collapsed without traceability.

Report:

* orphan symbols
* broken physical declarations
* namespace confidence promotions

No unresolved namespace may become confirmed silently.

==================================================
7. CALL MODEL
=============

Validate R5 call summary against current approved baseline:

total=230356
confirmed=12775
unresolved=217581
inferred=0

Check:

* no complete calls.json duplicated into SYSTEM_CONTEXT unless justified
* confirmed/unresolved distinction preserved
* no unresolved call promoted
* source index/reference exposed
* compact adjacency/reference model usable

Any confidence promotion = HIGH.

==================================================
8. DATA ACCESS MODEL
====================

Validate R5 data-access summaries/references against R3.1.

Expected upstream:

* operations=20082
* confirmed=20073
* Method->DataAccessOperation=9771
* operations_method_null=0
* stored_procedures=5389
* sql_operations=3
* parameters=74633

Sample >=30 DAO/SP/SQL references.

Verify:

Method
-> DataAccessOperation
-> StoredProcedure/SQL

Check:

* ID validity
* provider/reference integrity
* no fabricated stored procedure
* no wrong DAO association
* no credentials included

Report broken references.

==================================================
9. FUNCTIONAL_FLOWS MODEL
=========================

Validate:

`FUNCTIONAL_FLOWS.json`

Expected R4.1:

flows=12642
paths=170020

Verify all R4.1 flow IDs and path IDs are preserved exactly.

Calculate:

* total flows
* total paths/references
* unique flow IDs
* unique path IDs
* duplicate flow IDs
* duplicate path IDs
* duplicate logical paths

REQUIRED:

duplicate_flow_ids=0
duplicate_path_ids=0
duplicate_logical_paths=0

R5 must NOT generate new semantic path identities.

==================================================
10. FUNCTIONAL FLOW PRECISION
=============================

Sample >=30 flows.

Verify:

WebForm
-> Event/Lifecycle
-> Handler
-> Method
-> confirmed calls
-> DAO
-> StoredProcedure/SQL

Where unresolved boundaries occur:
they must remain explicit.

Classify each sampled flow:

CORRECT
SUSPICIOUS
INCORRECT

Report precision estimate.

Any systematic semantic alteration from R4.1 = HIGH.

==================================================
11. BRANCH PRESERVATION
=======================

Sample >=15 multi-path flows.

Verify:

* branch ordering preserved
* distinct method paths preserved
* same terminal via different legitimate chains preserved
* unresolved branch retained
* confirmed DB branch retained
* no R5 path collapse

Compare against R4.1 functional_paths.json.

Report lost/added logical branches.

Required:
no unexplained branch loss/addition.

==================================================
12. UNRESOLVED BOUNDARIES
=========================

Validate aggregate count against R4.1:

expected unresolved_boundaries=162914

If R5 representation aggregates them, verify complete referential coverage rather than requiring one fully duplicated object per boundary.

Sample >=30 boundaries.

Check:

* no target guessing
* unresolved confidence preserved
* caller/reference available
* traceability back to upstream call evidence

Any systematic promotion = HIGH/CRITICAL.

==================================================
13. ARCHITECTURE GRAPH
======================

Validate:

`ARCHITECTURE_GRAPH.json`

Report:

* node count
* edge count
* node types
* relation types
* duplicate nodes
* duplicate edges
* orphan edge sources
* orphan edge targets

REQUIRED:

duplicate logical edges=0
orphan edge sources=0
orphan edge targets=0

==================================================
14. ARCHITECTURE GRAPH FACTUALITY
=================================

Sample >=50 edges across different relation types.

Prioritize:

* Repository -> Solution
* Solution -> Project
* Project -> Project
* Project -> DLL
* Namespace -> Class
* Class -> BaseClass
* WebForm -> CodeBehind/Class
* WebForm -> Event
* Event -> Handler
* Handler -> Method
* Method -> Method
* Method -> DataAccessOperation
* DataAccessOperation -> StoredProcedure
* DataAccessOperation -> SQL

Cross-check every sampled edge against upstream indexes.

Classify:
CORRECT
SUSPICIOUS
INCORRECT

No architectural edge may exist solely because of naming convention.

==================================================
15. GRAPH SCALE / USABILITY
===========================

Inspect graph size and density.

Report:

* total nodes
* total edges
* top node types
* top relation types
* largest fan-out
* largest fan-in

Determine whether graph is:

PRACTICAL
LARGE_BUT_USABLE
EXCESSIVELY_NOISY

Check that source/member noise has not overwhelmed functional/architectural relationships.

Do not fail solely for large size if representation remains indexed and useful.

==================================================
16. TRACEABILITY.JSON
=====================

Validate all major mappings:

* WebForm -> entry points
* entry point -> flow
* flow -> paths
* path -> call references
* path -> DAO
* path -> stored procedure
* path -> SQL
* symbol -> physical declarations
* project -> source files
* graph node -> upstream reference

Calculate:

* total mappings
* broken IDs
* orphan references
* missing expected mappings

REQUIRED:
no systematic broken traceability.

==================================================
17. TRACEABILITY ROUND TRIP
===========================

Perform >=25 round-trip validations.

Examples:

WebForm
-> entry point
-> flow
-> path
-> method call reference
-> DAO
-> stored procedure

and:

StoredProcedure
<- DAO
<- path
<- flow
<- entry point
<- WebForm

Also test:
Project -> source/symbol -> graph node.

Report:

ROUND_TRIP_PASS
ROUND_TRIP_PARTIAL
ROUND_TRIP_FAIL

Broken DB/flow round-trip = HIGH.

==================================================
18. AI QUESTION USABILITY
=========================

Using ONLY R5 artifacts plus traceability references, determine whether the model can support factual retrieval for questions such as:

1. Which WebForms reach stored procedure X?
2. Which procedures are reachable from WebForm Y?
3. What projects participate in flow Z?
4. Which handlers reach a data operation?
5. What unresolved calls exist in a flow?
6. What is the ordered path from event to DB endpoint?

Do NOT actually implement AI.

Evaluate whether deterministic structures contain enough references.

Classify each:
SUPPORTED
PARTIALLY_SUPPORTED
NOT_SUPPORTED

Material missing navigation needed for intended R5 purpose = HIGH/MEDIUM depending impact.

==================================================
19. SYSTEM_CONTEXT.MD
=====================

Inspect:

`SYSTEM_CONTEXT.md`

Verify required factual sections exist:

* Snapshot
* Repository
* Solutions and Projects
* Web Application Surface
* Code Structure
* Dependency Model
* Call Graph
* Data Access
* Functional Flows
* Unresolved Areas
* Confidence
* Traceability
* Statistics
* Usage Notes

Check:

* factual only
* compact
* no unsupported business narrative
* no invented architecture
* no secrets
* useful as portable context for a new AI session

Report size and approximate usefulness.

==================================================
20. FACT / CONFIDENCE SEPARATION
================================

Search all R5 artifacts for confidence handling.

Verify:

confirmed stays confirmed
inferred stays inferred
unresolved stays unresolved

Check for:

* unresolved -> confirmed promotion
* guessed project role
* guessed architecture layer
* guessed business purpose
* fabricated endpoint
* inferred relationship presented as fact

Any systematic semantic invention = CRITICAL.

==================================================
21. PORTABILITY
===============

Inspect all 5 artifacts for absolute Windows paths.

Allowed:

source repository root in snapshot metadata.

Prefer relative paths elsewhere.

Report:

* absolute internal reference count
* path categories
* portability-impacting references

Classify:

PASS
MINOR
BLOCKING

R5 copied to another PC should remain navigable.

==================================================
22. DETERMINISM
===============

Validate deterministic construction.

Inspect code and outputs for:

* random UUID
* Python hash()
* timestamp-based IDs
* unstable set ordering
* unstable dict iteration affecting semantic output

Confirm R4.1 IDs are reused unchanged.

If feasible without modifying source, run R5 generation a second time into:

`output/v2_r5_repro/`

using the same legacy repository and compare the five artifacts semantically.

Command allowed for THIS validation:

`python main.py "C:\Users\cgalianj\source\IST_40\operacional" --output "output\v2_r5_repro" --verbose`

This second run is optional if full deterministic equivalence can already be proven; strongly prefer it if practical.

For JSON:
compare canonical semantic hashes.

For Markdown:
normalize only explicitly nondeterministic metadata such as allowed generation timestamp before comparison.

Report:

* semantic hash equality
* structural differences
* unexpected deterministic differences

Unexpected semantic difference = HIGH.

==================================================
23. FILE SIZE / DUPLICATION
===========================

Report exact size for all five artifacts.

Check whether data is duplicated excessively between:

SYSTEM_CONTEXT.json
FUNCTIONAL_FLOWS.json
ARCHITECTURE_GRAPH.json
TRACEABILITY.json

Detect:

* full 230k calls duplicated
* full source bodies duplicated
* complete path structures repeated unnecessarily multiple times
* massive evidence duplication

Classify:

COMPACT
ACCEPTABLE
EXCESSIVE_DUPLICATION

If excessive duplication materially harms usability, classify HIGH/MEDIUM.

==================================================
24. PERFORMANCE
===============

Record where available:

* R5 generation behavior
* output sizes
* parsing feasibility
* largest collections
* pathological O(N²)-like symptoms
* memory/output explosion indicators

No need for microbenchmarks.

Classify:

PRACTICAL
BORDERLINE
UNSUITABLE

==================================================
25. SECURITY
============

CRITICAL.

Scan all five R5 artifacts.

Check for actual unredacted:

* password
* pwd
* user id
* uid
* username
* credential
* token
* secret
* connection-string credential values

Do not reproduce secrets.

Also ensure evidence fields do not bypass centralized sanitizer.

Any actual secret exposure = CRITICAL FAIL.

==================================================
26. UPSTREAM REGRESSION
=======================

Validate current real indexes still preserve approved baselines.

Calls:

* total=230356
* confirmed=12775
* unresolved=217581
* inferred=0

R2:

* entry_points=12662
* event_bindings=12662

R3.1:

* data_access=20082
* confirmed=20073
* Method->DataAccessOperation=9771
* operations_method_null=0
* stored_procedures=5389
* sql_operations=3
* parameters=74633

R4.1:

* flows=12642
* paths=170020
* duplicate_path_ids=0
* duplicate_logical_paths=0

Any unexplained semantic change = HIGH.

==================================================
27. SOURCE IMMUTABILITY
=======================

Confirm R5 did not modify:

`C:\Users\cgalianj\source\IST_40\operacional`

Where practical, compare current source fingerprint with approved fingerprint:

SOURCE_FILE_COUNT=4328

SOURCE_SNAPSHOT_SHA256=
6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a

Mismatch requires investigation.

Do not automatically assume R5 caused a mismatch.

==================================================
28. R5 COMPLETENESS
===================

Evaluate whether R5 meets its intended role as a reusable system intermediate model.

Must provide:

* structural model
* project/solution relationships
* WebForm surface
* symbol context
* call summary
* data-access context
* functional flows
* architecture graph
* traceability
* portable Markdown summary
* confidence separation
* source snapshot identity

Classify:

COMPLETE
COMPLETE_WITH_NONBLOCKING_LIMITATIONS
INCOMPLETE

==================================================
29. REQUIRED_FIXES
==================

Classify defects:

CRITICAL
HIGH
MEDIUM
LOW

CRITICAL/HIGH block V2 closure.

MEDIUM/LOW are non-blocking unless they materially affect:

* factual reliability
* traceability
* portability
* determinism
* security
* downstream usability

==================================================
30. FINAL DECISION
==================

Return EXACTLY one:

A) V2-R5_APROBADA_V2_COMPLETA
B) V2-R5_REQUIERE_CORRECCIONES
C) V2-R5_NO_CONFIABLE

Approval requires:

* all 5 artifacts valid
* source snapshot identity valid
* SYSTEM_CONTEXT coherent
* functional flow preservation PASS
* architecture graph factual/integrity PASS
* traceability PASS
* round-trip navigation PASS
* confidence separation PASS
* determinism PASS
* portability acceptable
* output size/performance acceptable
* security PASS
* no upstream regression
* source immutability PASS
* no CRITICAL
* no blocking HIGH

==================================================
OUTPUT
======

Create ONLY:

`codex/V2/V2_R5_VALIDACION_REAL.md`

FORMAT:

STATUS
ARTIFACTS
SOURCE_SNAPSHOT
SYSTEM_CONTEXT
REPOSITORY_PROJECT_MODEL
WEB_MODEL
SYMBOL_MODEL
CALL_MODEL
DATA_ACCESS_MODEL
FUNCTIONAL_FLOWS
FLOW_PRECISION
BRANCH_PRESERVATION
UNRESOLVED_BOUNDARIES
ARCHITECTURE_GRAPH
GRAPH_FACTUALITY
GRAPH_SCALE
TRACEABILITY
TRACEABILITY_ROUND_TRIP
AI_USABILITY
MARKDOWN_CONTEXT
CONFIDENCE_SEPARATION
PORTABILITY
DETERMINISM
FILE_SIZES
PERFORMANCE
SECURITY
UPSTREAM_REGRESSION
SOURCE_IMMUTABILITY
R5_COMPLETENESS
REQUIRED_FIXES
DECISION

Machine-oriented.
Compact.
No ZIP.
No code changes.
No additional reports.
No phase beyond V2-R5.

If approved, record:

`V2 COMPLETE`

and stop.
