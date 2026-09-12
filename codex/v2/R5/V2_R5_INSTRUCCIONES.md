TASK: Implement LegacyMapper V2-R5 — System Intermediate Model.

DO NOT modify legacy source.
DO NOT introduce LLM processing.
DO NOT redesign approved V1/R1.1/R2/R3.1/R4.1 semantics.
DO NOT start any phase beyond V2-R5.

==================================================
BASELINE
========

APPROVED:

V1:
Structural repository model.

V2-R1.1:
Call graph foundation.

V2-R2:
Web functional entry points.

V2-R3.1:
Data-access mapping.

V2-R4.1:
Functional flow resolver.

R4.1 FINAL DECISION:

`V2-R4_1_APROBADA_PARA_R5`

Current reproducible call baseline:

* calls_total=230356
* confirmed=12775
* unresolved=217581
* inferred=0

Current legacy source fingerprint:

SOURCE_FILE_COUNT=4328

SOURCE_SNAPSHOT_SHA256=
`6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a`

Current R4.1:

* flows=12642
* paths=170020
* duplicate_path_ids=0
* duplicate_logical_paths=0
* cross_project_flows=2187
* paths_to_stored_procedure=1121
* paths_to_sql=1
* paths_to_data_operation=4612
* unresolved_boundaries=162914
* dead_end_paths=1372
* max_observed_depth=6
* errors=0

R4.1 repeated call graphs are byte-identical and deterministic.

==================================================
GOAL
====

Build a reusable deterministic intermediate representation of the legacy system.

LegacyMapper must transform approved indexes into a coherent system model suitable for:

* human inspection
* AI context
* architecture analysis
* functional analysis
* traceability
* Mermaid generation
* PlantUML generation
* Graphviz generation
* C4 interpretation
* sequence-diagram generation
* future documentation

Core principle:

`Python discovers/resolves/traces facts. AI interprets later.`

R5 must INTEGRATE approved evidence.

R5 must NOT rediscover source semantics.

==================================================
OUTPUT
======

Create:

`output/ai_context/`

with exactly these primary artifacts:

1. `SYSTEM_CONTEXT.json`
2. `SYSTEM_CONTEXT.md`
3. `ARCHITECTURE_GRAPH.json`
4. `FUNCTIONAL_FLOWS.json`
5. `TRACEABILITY.json`

Additional internal helper JSON files are NOT required.

Do not remove or rename existing `output/index/` artifacts.

==================================================
R5-01 SYSTEM_CONTEXT.JSON
=========================

Create the canonical machine-readable integrated model.

Suggested top-level structure:

{
"metadata": {},
"repository": {},
"solutions": [],
"projects": [],
"web": {},
"symbols": {},
"configuration": {},
"dependencies": {},
"calls": {},
"data_access": {},
"functional": {},
"statistics": {},
"warnings": []
}

Do NOT blindly duplicate full upstream indexes.

Prefer:

* summaries
* stable references
* normalized entities
* compact relationships
* IDs pointing to source indexes

Avoid creating a multi-hundred-megabyte duplicate of all R1-R4 JSON.

==================================================
R5-02 METADATA
==============

Include at least:

* model_version
* generated_by
* source_repository
* source_file_count
* source_snapshot_sha256
* generation_timestamp if project convention permits
* deterministic_model_version
* upstream_phase_versions
* confidence_model
* source_indexes

The system model must identify which source snapshot produced it.

If timestamp is included:
it must NOT participate in deterministic IDs.

==================================================
R5-03 REPOSITORY SUMMARY
========================

Integrate factual repository information:

* total files
* classified file counts
* solutions
* projects
* VB source count
* ASPX
* ASCX
* Master
* web.config count
* relevant configuration categories

Use existing V1 indexes.

No rescanning.

==================================================
R5-04 SOLUTIONS / PROJECTS
==========================

Represent:

Solution
-> Project

Project:

* path
* name
* root namespace
* assembly name
* target framework
* project references
* DLL references
* source-file references

Use stable existing identities where available.

Do not infer project layers from names.

Optional semantic labels such as "web", "BL", "SYS", "DAL" must NOT be facts unless already deterministically supported.

==================================================
R5-05 WEB MODEL
===============

Represent Web Forms entities compactly:

WebForm:

* identity/path
* type: aspx/ascx/master
* inherits
* codebehind
* resolved class/method links where available
* registered namespaces/controls
* entry_point IDs

Do not duplicate entire markup.

==================================================
R5-06 SYMBOL MODEL
==================

Represent normalized logical code symbols:

* namespace
* class
* interface
* module
* enum
* structure

Include where available:

* declared_namespace
* root_namespace
* effective_namespace
* namespace_confidence
* project
* physical declarations
* inheritance
* implemented interfaces
* member references

Use logical symbols to avoid unnecessary duplicate partial-class representation.

Preserve physical traceability.

==================================================
R5-07 CALL MODEL
================

Do NOT copy all 230356 call records into SYSTEM_CONTEXT.json unless required.

Instead expose compact call graph summary and references.

At minimum:

* total
* confirmed
* unresolved
* inferred
* cross-project confirmed count
* confirmed adjacency reference
* unresolved boundary reference
* source index path

Confirmed calls remain facts.

Unresolved calls remain explicit unresolved relationships.

Never promote unresolved.

==================================================
R5-08 DATA ACCESS MODEL
=======================

Integrate R3.1 facts:

* data-access operations
* stored procedures
* SQL operations
* parameters
* transactions
* providers
* repository wrappers
* direct provider usage

Expose useful summaries:

* operation counts
* unique procedures
* SQL counts
* operations per project/class/method where practical
* procedure references
* SQL references

No credentials or unsanitized connection data.

==================================================
R5-09 FUNCTIONAL MODEL
======================

Integrate approved R4.1 flow/path information.

SYSTEM_CONTEXT.json should expose:

functional:
{
"summary": {},
"flows": [...compact references...],
"paths_index": "...",
"unresolved_boundaries": {},
"terminal_summary": {}
}

Do NOT embed every full path if it causes unnecessary duplication.

Full normalized flows belong primarily in:

`FUNCTIONAL_FLOWS.json`

==================================================
R5-10 FUNCTIONAL_FLOWS.JSON
===========================

Create AI-consumable normalized functional flows.

Each flow should make it easy to answer:

"What happens when this WebForm event executes?"

Minimum conceptual structure:

{
"flow_id": "...",
"entry_point": {
"id": "...",
"webform": "...",
"event": "...",
"handler": "...",
"start_method": "..."
},
"paths": [...],
"projects": [...],
"terminal_operations": [...],
"stored_procedures": [...],
"sql_operations": [...],
"unresolved_boundaries": [...],
"confidence": "...",
"status": "..."
}

Paths must reference R4.1 path IDs.

Preserve:

* branch ordering
* method ordering
* DB endpoints
* unresolved boundaries
* confidence
* evidence references

Do not generate business descriptions.

Do not infer intent.

==================================================
R5-11 ARCHITECTURE_GRAPH.JSON
=============================

Build normalized graph representation.

Schema concept:

{
"nodes": [],
"edges": [],
"metadata": {},
"statistics": {}
}

Node types may include:

* Repository
* Solution
* Project
* Namespace
* Class
* Interface
* WebForm
* Event
* Handler
* Method
* DLL
* DataAccessOperation
* StoredProcedure
* SQL
* ExternalBoundary
* UnresolvedBoundary

Use only supported types from existing evidence.

Do NOT invent architectural components.

==================================================
R5-12 ARCHITECTURE GRAPH EDGES
==============================

Support normalized relations such as:

Repository -> Solution
Solution -> Project
Project -> Project
Project -> DLL
Project -> SourceFile
Namespace -> Class
Class -> BaseClass
WebForm -> CodeBehind
WebForm -> Class
WebForm -> Event
Event -> Handler
Handler -> Method
Method -> Method
Method -> DataAccessOperation
DataAccessOperation -> StoredProcedure
DataAccessOperation -> SQL

Optional:
Method -> UnresolvedBoundary

Every edge must have:

* source
* target
* relation
* confidence
* evidence/reference where applicable

Deduplicate identical logical edges.

==================================================
R5-13 GRAPH SCALE
=================

Architecture graph must be usable.

Do NOT blindly add every possible source-file/member relationship if this creates unusable noise.

Prefer architectural/functional relationships useful for downstream interpretation.

Expose statistics for omitted/aggregated categories.

Maintain traceability back to detailed indexes.

==================================================
R5-14 TRACEABILITY.JSON
=======================

Provide deterministic navigation between R5 and upstream indexes.

Minimum mappings:

* WebForm -> entry_points
* entry_point -> flow
* flow -> paths
* path -> call references
* path -> data-access operations
* path -> stored procedures
* path -> SQL
* symbol -> physical declarations
* project -> source files
* architecture node -> source index/reference

Traceability must allow downstream AI/tooling to reach factual source evidence without reparsing source code.

==================================================
R5-15 TRACEABILITY INTEGRITY
============================

No orphan references.

Validate:

* flow IDs
* path IDs
* entry-point IDs
* DataAccessOperation IDs
* StoredProcedure IDs
* SQL IDs
* symbol references
* project references

Broken references must be reported.

Never silently drop broken references.

==================================================
R5-16 SYSTEM_CONTEXT.MD
=======================

Generate compact human/AI-readable portable context.

This is NOT a huge documentation dump.

Target purpose:

A new AI session should understand the legacy system structure without reading the repository directly.

Suggested sections:

# LegacyMapper System Context

## Snapshot

## Repository

## Solutions and Projects

## Web Application Surface

## Code Structure

## Dependency Model

## Call Graph

## Data Access

## Functional Flows

## Unresolved Areas

## Confidence

## Traceability

## Statistics

## Usage Notes

Keep it factual.

Do not create unsupported business narratives.

Do not claim architectural patterns unless evidence supports them.

==================================================
R5-17 FACT / INFERENCE SEPARATION
=================================

Maintain strict distinction:

confirmed
inferred
unresolved

R5 aggregation must not upgrade confidence.

If a flow contains an unresolved boundary:
preserve it.

If a project role is not deterministically known:
do not assign one.

If a business purpose is unknown:
do not invent it.

==================================================
R5-18 PORTABILITY
=================

R5 outputs must not rely on absolute Windows paths when stable relative paths can be used.

Source repository metadata may contain the configured root separately.

References within the model should prefer normalized relative paths.

Goal:

R5 artifacts should remain useful when copied to another computer.

==================================================
R5-19 DETERMINISM
=================

All deterministic model IDs must:

* use canonical stable inputs
* be stable across identical executions
* avoid Python hash()
* avoid random UUID
* avoid timestamps
* avoid unordered-set/dict-dependent identity

Sort exported collections where required for reproducibility.

Running R5 twice against identical upstream indexes should produce semantically identical artifacts.

Timestamp metadata may differ if explicitly allowed, but must be excluded from semantic identity.

==================================================
R5-20 PERFORMANCE / SIZE
========================

Avoid loading unnecessary duplicated representations.

R5 should handle current scale:

* 14k+ files
* 230k+ calls
* 170k functional paths
* 20k+ data operations

Use indexed lookups.

Avoid O(N²) joins where dictionary/index lookup is possible.

Do not copy full call evidence/source bodies into every functional path.

Prefer references.

Report output file sizes in validation report.

If an output becomes excessively large because of duplicated structures:
refactor representation before declaring R5 complete.

==================================================
R5-21 SECURITY
==============

All exported values pass through centralized sanitizer where appropriate.

Never expose:

* passwords
* credentials
* tokens
* secret connection strings
* sensitive authentication values

Do not duplicate sanitized evidence into unsanitized R5 fields.

==================================================
R5-22 ERRORS / WARNINGS
=======================

SYSTEM_CONTEXT must surface:

* upstream errors count
* unresolved relationships
* unresolved functional boundaries
* namespace unresolved counts where useful
* traceability failures
* R5 generation warnings

Warnings are facts.

Do not describe unresolved relationships as system defects unless justified.

==================================================
R5-23 AI USABILITY
==================

R5 artifacts should make downstream questions practical, such as:

* Which WebForms call a given stored procedure?
* Which projects participate in a given functional flow?
* Which handlers reach Oracle?
* What procedures are reachable from a page/control?
* Which calls remain unresolved?
* What classes are shared across projects?
* What is the path from event X to database operation Y?

Do NOT implement natural-language Q&A.

Ensure the model contains enough deterministic references to support those questions later.

==================================================
R5-24 TESTS
===========

Preserve all existing tests.

Add tests at minimum:

T01 SYSTEM_CONTEXT generated
T02 ARCHITECTURE_GRAPH generated
T03 FUNCTIONAL_FLOWS generated
T04 TRACEABILITY generated
T05 SYSTEM_CONTEXT.md generated
T06 deterministic model IDs
T07 deterministic repeated output
T08 no random/Python hash identity
T09 flow/path references valid
T10 entry point references valid
T11 DAO references valid
T12 stored procedure references valid
T13 SQL references valid
T14 symbol/project references valid
T15 no orphan architecture edges
T16 graph edge dedup
T17 confirmed confidence preserved
T18 unresolved confidence preserved
T19 no confidence promotion
T20 relative path normalization
T21 source snapshot metadata present
T22 R4.1 path IDs preserved
T23 R4.1 flow IDs preserved
T24 branching preserved
T25 unresolved boundaries preserved
T26 DB terminal associations preserved
T27 cross-project information preserved
T28 sanitizer applied
T29 no secret leakage
T30 large-index lookup sanity/performance
T31 upstream indexes unchanged
T32 R1.1 call baseline semantics unchanged
T33 R2 baseline unchanged
T34 R3.1 baseline unchanged
T35 R4.1 baseline unchanged
T36 no LLM invocation
T37 no legacy-source modification
T38 compact-reference behavior
T39 Markdown context required sections
T40 traceability round-trip test

Run:

`python -m unittest discover -s tests`

All tests must PASS.

==================================================
R5-25 INTERNAL VALIDATION
=========================

After implementation/tests, run fixture/internal validation only.

Verify:

* all 5 R5 artifacts generated
* no orphan IDs
* duplicate graph edges=0
* duplicate flow/path references=0
* confidence preserved
* sanitizer PASS
* deterministic repeated generation
* upstream indexes unchanged

Do NOT automatically run full legacy repository.

==================================================
R5-26 REGRESSION
================

R5 is additive.

Must preserve approved baselines.

Current reproducible calls:

* total=230356
* confirmed=12775
* unresolved=217581

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

No upstream semantic modification allowed.

If an upstream defect is discovered:
STOP and report it.
Do not silently fix previous approved phases inside R5.

==================================================
R5-27 IMPLEMENTATION LOCATION
=============================

Prefer isolated R5 components, for example:

`legacy_documenter/context/system_context_builder.py`
`legacy_documenter/exporters/ai_context_exporter.py`
`legacy_documenter/analysis/architecture_graph_builder.py`
`legacy_documenter/analysis/traceability_builder.py`

Exact naming may follow existing project conventions.

Avoid putting all R5 logic into main.py.

main.py should only orchestrate.

==================================================
R5-28 CLI
=========

R5 should run as part of normal LegacyMapper execution after R4.

Do not require an external AI service.

No interactive input.

No network dependency.

==================================================
R5-29 REAL VALIDATION COMMAND
=============================

Do NOT execute automatically.

Current legacy repository:

`C:\Users\cgalianj\source\IST_40\operacional`

Use:

`python main.py "C:\Users\cgalianj\source\IST_40\operacional" --output "output\v2_r5_full" --verbose`

==================================================
R5-30 ACCEPTANCE
================

Implementation ready for full real validation when:

* all existing/new tests PASS
* all 5 artifacts generated
* deterministic output PASS
* graph integrity PASS
* traceability PASS
* confidence preservation PASS
* R4.1 flow/path identities preserved
* DB terminal integrity PASS
* unresolved boundaries preserved
* sanitizer/security PASS
* output size practical
* no upstream regression
* no LLM dependency
* no legacy-source modification

==================================================
REPORT
======

Create ONLY:

`codex/V2/V2_R5_RESULTADO.md`

FORMAT:

STATUS
FILES_CHANGED
TESTS
OUTPUTS
SYSTEM_CONTEXT
ARCHITECTURE_GRAPH
FUNCTIONAL_FLOWS
TRACEABILITY
MARKDOWN_CONTEXT
DETERMINISM
PORTABILITY
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

Expected final status:

`V2-R5_READY_FOR_FULL_REAL_VALIDATION`

STOP after implementation/tests/internal validation.
