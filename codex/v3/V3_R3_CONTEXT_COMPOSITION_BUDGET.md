TASK=V3-R3_CONTEXT_COMPOSITION_BUDGET

MODE=IMPLEMENT_AND_VALIDATE
NO_LLM
NO_NETWORK
NO_FULL_REAL_REPOSITORY_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_V3_R4_PLUS

OBJECTIVE
Complete V3 context composition and implement deterministic context budgeting over V3-R2 ContextResolver.

Primary goals:

1. close V3-R2 test-coverage debt;
2. complete useful ENTITY and DATA_ACCESS package composition;
3. compose packages from reusable evidence without duplication;
4. introduce deterministic context budgets;
5. prioritize evidence when packages exceed configured limits;
6. expose measurable package size/cost statistics;
7. prepare packages for future LLMProvider consumption.

R3 MUST NOT perform AI interpretation.

ARCHITECTURE

V2 deterministic artifacts
|
v
V3-R2 ContextResolver
|
v
V3-R3 ContextComposer
|
+-> evidence selection
+-> reference expansion
+-> deduplication
+-> priority ordering
+-> budget enforcement
+-> compact ContextPackage
|
v
Future V3-R4 LLMProvider

PRINCIPLE

Context budget controls HOW MUCH evidence is supplied.

It must never change WHAT THE EVIDENCE MEANS.

No confidence promotion.
No semantic inference.
No business interpretation.

==================================================
R2 FOLLOW-UP
============

Explicitly verify and complete V3-R2 behavior.

Add dedicated tests for:

SYSTEM
FUNCTIONAL
TECHNICAL
ENTITY
FLOW
DATA_ACCESS

Do not consider existing V3-R1 tests sufficient evidence for R2.

R3 final report must separately state:

R1_TESTS
R2_TESTS
R3_TESTS
TOTAL_TESTS

==================================================
CONTEXT COMPOSER
================

Implement deterministic ContextComposer.

Responsibilities:

* consume ContextResolver results;
* compose related evidence;
* deduplicate references/entities;
* apply package policy;
* apply budget;
* retain unresolved evidence;
* retain provenance;
* retain traceability;
* produce deterministic output.

Preferred conceptual location:

legacy_documenter/context/composer.py

Adjust only if repository conventions justify another location.

Do not restructure unrelated V1/V2/V3-R1 code.

==================================================
ENTITY PACKAGE COMPOSITION
==========================

ENTITY package must become useful for future AI retrieval.

Support generic entity scopes where V2 data permits:

PROJECT
COMPONENT
UI
SYMBOL
METHOD
ENTRY_POINT
FLOW
DATA_OPERATION
STORED_PROCEDURE
SQL_OPERATION

Do not make these stack-specific requirements.

Given an entity, include compact relevant context such as:

entity identity
entity type
source snapshot
direct relationships
parent/owner refs where available
entry point refs
flow refs
path refs
dependency refs
data-access refs
evidence refs
unresolved refs
provenance

Do not invent missing relationships.

Ambiguous entity resolution remains AMBIGUOUS.

==================================================
DATA_ACCESS PACKAGE COMPOSITION
===============================

DATA_ACCESS package must support targeted technical/functional documentation.

Given a data operation / SP / SQL reference, include where available:

operation identity
operation type
calling method refs
flow refs
path refs
parameter metadata refs
stored procedure refs
SQL refs
project/component refs
evidence refs
unresolved refs
provenance

Parameters should remain compact.

Do not duplicate complete parameter/evidence bodies unless necessary.

Do not infer business meaning from stored procedure names.

==================================================
FLOW PACKAGE COMPOSITION
========================

FLOW package should provide a future AI enough context to explain a flow without loading global V2.

Include:

flow identity
entry point
UI/component refs
ordered path refs
selected ordered path nodes where required
confirmed calls
cross-project boundaries
DAO/data operations
SP/SQL terminals
unresolved boundaries
confidence/status
evidence refs
provenance

Preserve ordering.

Do not generate flow narrative.

==================================================
COMPOSITION DEDUPLICATION
=========================

Within a package:

same entity/reference must not be repeated unnecessarily.

Use normalized collections/maps or canonical unique lists.

Track:

raw_selected_records
unique_records
deduplicated_records

Deduplication must preserve all relationships and provenance.

==================================================
CONTEXT BUDGET MODEL
====================

Implement explicit ContextBudget.

Support named profiles:

TINY
SMALL
MEDIUM
LARGE
FULL

Profiles must be configuration/policy, not model-specific.

Do NOT hardcode:

Qwen
Gemini
Copilot
Claude
OpenAI
or any model name.

Each budget should support at minimum:

max_records
max_characters
max_estimated_tokens
max_flows
max_paths
max_entities
max_unresolved
max_evidence_refs

FULL may use no practical content limit but must still remain deterministic and deduplicated.

==================================================
TOKEN ESTIMATION
================

Implement provider-neutral deterministic token estimation.

Do NOT add tokenizer dependency yet.

Use documented conservative approximation.

Example acceptable policy:

estimated_tokens = ceil(character_count / configurable_chars_per_token)

Default ratio must be explicit/configurable.

Token estimate is planning metadata only.

It must NOT claim exact provider token count.

Expose:

character_count
estimated_tokens
estimation_method
chars_per_token

Future providers may replace/augment estimation with exact tokenizer capability.

==================================================
BUDGET APPLICATION
==================

Apply budget deterministically.

Selection order:

P0
P1
P2
P3
P4

Within same priority:
use stable canonical ordering.

Never use randomness.

When budget is insufficient:

1. retain required identity/scope metadata;
2. retain P0 evidence;
3. retain direct traceability required to understand P0;
4. retain P1 as capacity permits;
5. then P2;
6. retain relevant unresolved P3 according to reserved policy;
7. P4 last.

Do NOT silently discard unresolved information entirely.

==================================================
UNRESOLVED RESERVATION
======================

Budget policy must reserve configurable capacity for relevant unresolved evidence.

Reason:
future AI must know what LegacyMapper does NOT know.

Implement policy such as:

reserved_unresolved_records
or
reserved_unresolved_ratio

Exact implementation may follow project conventions.

Do not allow large confirmed collections to erase all unresolved context.

==================================================
TRUNCATION
==========

If budget prevents full composition:

truncated=true

Include structured truncation report:

budget_profile
limit_type
included_counts
excluded_counts
excluded_by_priority
excluded_categories
continuation_refs where practical
warnings

Never represent truncated package as complete.

==================================================
BUDGET OVERFLOW
===============

If mandatory P0 + identity/provenance alone exceed selected budget:

do NOT silently remove required P0.

Return explicit state:

BUDGET_INSUFFICIENT

Package/report must identify minimum required size estimate.

==================================================
PACKAGE COMPLETENESS
====================

Define:

COMPLETE
TRUNCATED
BUDGET_INSUFFICIENT

This state is independent from factual confidence.

Example:

package completeness=TRUNCATED
fact status=CONFIRMED

These must never be conflated.

==================================================
SIZE STATISTICS
===============

Every composed package should expose:

package_bytes
character_count
estimated_tokens
records_selected
records_included
records_excluded
deduplicated_records
counts_by_priority
counts_by_category
budget_profile
completeness

Statistics must be deterministic for identical input.

==================================================
CONTEXT QUALITY METRICS
=======================

Add deterministic structural metrics only.

At minimum:

confirmed_reference_count
unresolved_reference_count
traceability_reference_count
flow_count
data_access_count
entity_count
coverage_by_priority

Do NOT create semantic quality scores.

Do NOT claim:
"documentation quality = 95%"

R3 cannot know that.

==================================================
FUNCTIONAL COMPOSITION
======================

For FUNCTIONAL packages prioritize:

P0:
entry points
flows
ordered paths
reached data operations
SP/SQL terminals

P1:
direct UI/component relationships
confirmed calls required by paths
cross-project transitions

P2:
supporting structural context

P3:
relevant unresolved boundaries

P4:
additional evidence references

Do not create module/business semantics.

==================================================
TECHNICAL COMPOSITION
=====================

For TECHNICAL packages prioritize:

P0:
projects/components
direct dependencies
technical flow relationships
data-access structure

P1:
supporting call/project relationships
configuration/security/deployment facts where available

P2:
additional architecture evidence

P3:
technical unresolved boundaries

P4:
additional evidence references

Do not declare patterns/layers.

==================================================
SYSTEM COMPOSITION
==================

SYSTEM must remain bootstrap-oriented.

It should answer structurally:

* what system snapshot is this?
* what evidence categories exist?
* how large is analyzed system?
* what packages/scopes can be requested?
* what major structural counts exist?
* where should deeper evidence be requested?

SYSTEM should NOT attempt to contain all V2 facts.

==================================================
PROGRESSIVE DISCLOSURE
======================

Prepare deterministic progressive context levels:

L0 SYSTEM
L1 STRUCTURE
L2 ENTITY
L3 FLOW
L4 DATA_ACCESS
L5 EVIDENCE

These are retrieval/composition levels, not confidence levels.

A future AI should be able to begin with L0/L1 and request deeper evidence only when necessary.

Do not implement AI-driven requests yet.

==================================================
PACKAGE INDEX
=============

Define compact package index contract enabling future lookup:

package_id
package_type
scope
source_snapshot
budget_profile
completeness
size_statistics
related_package_refs

Do not generate a global huge duplicate index.

==================================================
CACHE PREPARATION
=================

Package IDs must allow deterministic caching later.

Same:

source snapshot

* package request
* composition policy
* budget profile

=> same semantic package_id.

Do NOT implement complex cache infrastructure unless trivially needed.

==================================================
V3-R1 COMPATIBILITY
===================

Future DocumentClaim must be able to cite:

ContextPackage
+
specific package evidence
+
original V2 reference

Preserve chain:

DocumentClaim
-> ContextPackage
-> V2 evidence/reference
-> source snapshot

No traceability loss through compaction.

==================================================
V3-R2 COMPATIBILITY
===================

Do not break ContextResolver public behavior without explicit reason.

If modifications are required:

* preserve backward compatibility where practical;
* document exact change;
* add regression test.

==================================================
FUTURE LLM PROVIDER CONTRACT
============================

Prepare ContextPackage output so V3-R4 can consume:

serialized_context
estimated_tokens
budget_profile
completeness
provenance
traceability

Do NOT implement LLMProvider.

Do NOT create model-specific package formats.

==================================================
MODEL INDEPENDENCE
==================

R3 must remain usable later with:

Gemini
Copilot-compatible services if API access is available
Qwen/Ollama
Claude
OpenAI
Azure OpenAI
other providers

No provider-specific branches.

Provider capabilities belong to R4+.

==================================================
SECURITY
========

Continue sanitized evidence policy.

Do not rehydrate secrets.

Do not copy raw configuration values when sanitized references suffice.

No credentials.

No external API calls.

==================================================
DETERMINISM
===========

Same input artifacts

* same request
* same policy
* same budget

must produce semantically identical output.

Stable ordering required.

No UUID.
No random.
No Python hash identity.
No current timestamp in semantic identity.

==================================================
TESTS
=====

Add explicit R2 and R3 tests.

Required R2 follow-up:

1 all six package types
2 source snapshot preservation
3 FOUND
4 NOT_FOUND
5 AMBIGUOUS
6 ambiguity candidates
7 bounded expansion
8 no semantic guessing
9 confidence preservation
10 unresolved preservation
11 truncation explicit
12 provenance
13 reference closure
14 functional semantics not invented
15 technical pattern not invented
16 deterministic IDs
17 deterministic serialization
18 no stack-specific schema requirement
19 no network
20 no LLM

Required R3:

21 ENTITY composition
22 PROJECT entity
23 UI/component entity
24 METHOD entity
25 FLOW entity
26 DATA_OPERATION entity
27 STORED_PROCEDURE entity
28 DATA_ACCESS composition
29 caller refs
30 flow refs
31 SP refs
32 SQL refs
33 parameter refs compact
34 FLOW composition ordered
35 flow unresolved retained
36 cross-project refs retained
37 deduplication
38 deduplication preserves relationships
39 TINY profile
40 SMALL profile
41 MEDIUM profile
42 LARGE profile
43 FULL profile
44 character limit
45 estimated-token limit
46 record limit
47 flow limit
48 path limit
49 entity limit
50 unresolved reservation
51 P0 before P1
52 P1 before P2
53 P3 unresolved preserved
54 P4 last
55 stable ordering inside priority
56 truncation report
57 excluded counts
58 excluded priority counts
59 COMPLETE
60 TRUNCATED
61 BUDGET_INSUFFICIENT
62 mandatory P0 retained
63 minimum required estimate
64 deterministic token estimate
65 configurable chars/token
66 deterministic size statistics
67 deterministic quality metrics
68 progressive L0
69 progressive L1
70 progressive L2
71 progressive L3
72 progressive L4
73 progressive L5
74 package index contract
75 deterministic cache identity
76 DocumentClaim->Package->V2 traceability
77 no evidence body duplication
78 no full graph duplication
79 no full calls duplication
80 functional prioritization
81 technical prioritization
82 SYSTEM remains compact
83 no module semantics
84 no architecture-pattern declaration
85 no confidence promotion
86 sanitized data maintained
87 no credentials introduced
88 no real legacy scan
89 no network
90 no LLM
91 V1/V2 regression
92 V3-R1 regression
93 V3-R2 regression

Run:

python -m unittest discover -s tests

All PASS.

==================================================
VALIDATION
==========

Fixtures only.

Additionally create deterministic synthetic fixture large enough to demonstrate:

FULL > LARGE > MEDIUM > SMALL > TINY

in included evidence where budget pressure exists.

Validate:

* package size decreases appropriately;
* P0 remains;
* unresolved reservation works;
* traceability remains valid;
* no semantic facts change;
* repeated execution byte/semantic deterministic.

Do NOT scan:

C:\Users\cgalianj\source\IST_40\operacional

==================================================
NON_GOALS
=========

Do NOT implement:

LLMProvider
Gemini
Copilot
Qwen/Ollama
Claude
OpenAI
Azure OpenAI
real AI calls
prompt engineering for documentation
functional interpretation
technical interpretation
architecture-pattern interpretation
LEVANTAMIENTO_FUNCIONAL
LEVANTAMIENTO_TECNICO
human approval
Knowledge Readiness
external information ingestion
AI_KNOWLEDGE
vector DB
embeddings
semantic search
V4 adapters

==================================================
REPORT
======

Create ONLY:

codex/V3/V3_R3_RESULTADO.md

Machine-oriented.
Compact.

FORMAT:

STATUS
FILES_CHANGED
CONTEXT_SCHEMA
COMPOSER
ENTITY_COMPOSITION
FLOW_COMPOSITION
DATA_ACCESS_COMPOSITION
BUDGET_MODEL
TOKEN_ESTIMATION
PRIORITY_POLICY
UNRESOLVED_RESERVATION
TRUNCATION
COMPLETENESS
SIZE_METRICS
QUALITY_METRICS
PROGRESSIVE_DISCLOSURE
PACKAGE_INDEX
TRACEABILITY
R2_FOLLOWUP
R1_TESTS
R2_TESTS
R3_TESTS
TOTAL_TESTS
DETERMINISM
SECURITY
REGRESSION
KNOWN_LIMITATIONS
NEXT

Expected:

STATUS=V3-R3_READY_FOR_REVIEW
NEXT=V3-R4_NOT_STARTED

Stop.