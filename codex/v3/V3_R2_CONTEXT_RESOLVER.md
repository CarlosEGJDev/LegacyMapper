TASK=V3-R2_CONTEXT_RESOLVER

MODE=IMPLEMENT_AND_VALIDATE
NO_LLM
NO_NETWORK
NO_FULL_REAL_REPOSITORY_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_V3_R3_PLUS

OBJECTIVE
Implement deterministic ContextResolver over approved V2 artifacts.

Purpose:
select, relate, prioritize and compact V2 evidence required by future AI generation of:

* LEVANTAMIENTO_FUNCIONAL
* LEVANTAMIENTO_TECNICO

R2 MUST NOT interpret business meaning.
R2 MUST NOT generate final human documentation.
R2 MUST NOT infer modules/patterns/responsibilities from names.

PRINCIPLE
V2 facts -> ContextResolver -> compact evidence packages -> future AI interpretation.

Python selects evidence.
AI interprets later.
Human approves later.

INPUT CONTRACT
Consume existing V2-R5.1 artifacts/indexes by reference.

Primary:

* SYSTEM_CONTEXT.json
* ARCHITECTURE_GRAPH.json
* FUNCTIONAL_FLOWS.json
* TRACEABILITY.json

Use upstream indexes only when required for evidence detail.

Do not duplicate/reimplement V1/V2 extraction or resolution.

Do not assume fixed absolute output path.

CONTEXT PACKAGE TYPES
Implement at least:

SYSTEM
FUNCTIONAL
TECHNICAL
ENTITY
FLOW
DATA_ACCESS

R2 primary documentation packages:
FUNCTIONAL
TECHNICAL

SYSTEM package:
high-level deterministic bootstrap/context.

ENTITY/FLOW/DATA_ACCESS:
future targeted retrieval and package composition.

COMMON PACKAGE MODEL
Define machine-readable ContextPackage containing at least:

package_id
package_type
schema_version
source_snapshot
scope
selection_policy
statistics
entities
relationships
flow_refs
path_refs
data_access_refs
evidence_refs
unresolved_refs
warnings
truncation
provenance

package_id must be deterministic.

No full evidence bodies unless explicitly required.

Prefer stable V2 IDs/references.

SCHEMA_VERSION
Introduce explicit context-package schema version.

Suggested:
3.1.0

Do not change V3 documentation contract version 3.0.0 unnecessarily.

SOURCE SNAPSHOT
Every package must retain V2 source snapshot identity.

Package generation must fail or warn according to explicit policy if required snapshot metadata is absent.

Never combine evidence from different source snapshots silently.

FUNCTIONAL PACKAGE
Goal:
provide sufficient factual evidence for future LEVANTAMIENTO_FUNCIONAL generation.

Include/select:

* application/system summary facts
* WebForms/UI surfaces
* entry points
* event/lifecycle bindings
* functional flows
* path references
* confirmed method relationships relevant to flows
* data-access endpoints reached by flows
* stored procedures / SQL refs
* cross-project flow evidence
* unresolved functional boundaries
* source/evidence refs
* confidence/status from upstream

Do NOT:

* invent module names
* infer business purpose
* infer business rules
* label a flow with business meaning solely from identifiers
* convert unresolved into interpreted/confirmed
* generate prose documentation

Candidate grouping may be structural only and must be explicitly labeled non-semantic.

TECHNICAL PACKAGE
Goal:
provide sufficient factual evidence for future LEVANTAMIENTO_TECNICO generation.

Include/select:

* repository/system metadata
* solutions
* projects
* project dependencies
* DLL/external dependencies
* namespaces/types/components where useful
* Web/UI technical structure
* confirmed call relationships
* architecture graph summaries/references
* representative technical flows
* data-access structure
* stored procedure / SQL usage
* configuration evidence available from V2
* security-related deterministic evidence available from V2
* deployment/runtime deterministic evidence available from V2
* unresolved technical areas
* source/evidence refs

Do NOT:

* declare architectural/design pattern
* invent layers
* assign project responsibilities from names
* invent deployment architecture
* invent security mechanisms
* infer framework behavior not represented by evidence

Pattern interpretation belongs to later AI generation and V3-R1 claim rules.

SYSTEM PACKAGE
Provide compact bootstrap facts:

* source snapshot
* repository statistics
* solution/project overview
* Web surface summary
* symbol/call summary
* data-access summary
* flow summary
* unresolved summary
* references to deeper packages/evidence

SYSTEM must remain compact.

TARGETED PACKAGE RESOLUTION
Support deterministic package requests by stable entity/reference where possible.

Examples:

* project
* WebForm/UI entity
* symbol/class
* method
* entry point
* flow
* path
* data operation
* stored procedure
* SQL operation

Resolver must navigate existing V2 traceability/graph/flow references.

Do not search by AI semantic similarity.

Name lookup may be supported only as deterministic exact/normalized lookup with ambiguity preserved.

AMBIGUITY
Never silently select one entity when multiple candidates match.

Return structured ambiguity:

status=AMBIGUOUS
candidates=[...]

Similarly:

NOT_FOUND
FOUND

Do not guess.

RELATION EXPANSION
Implement bounded deterministic relation expansion.

Package selection may traverse:

WebForm
-> EntryPoint
-> Flow
-> Path
-> Method
-> DataAccessOperation
-> StoredProcedure/SQL

and technical relations such as:

Solution
-> Project
-> Project/DLL

Use existing V2 relationships.

Do not discover new call relations.

Expansion depth must be explicit/configurable and deterministic.

No unbounded graph traversal.

EVIDENCE PRIORITY
Define deterministic priority tiers.

P0:
direct confirmed V2 facts required for requested scope.

P1:
direct traceability/flow relationships.

P2:
supporting structural context.

P3:
unresolved boundaries relevant to scope.

P4:
optional evidence/detail references.

Priority is selection priority only.
It MUST NOT change factual confidence.

CONFIDENCE PRESERVATION
Preserve upstream state.

confirmed -> confirmed
inferred -> inferred if present
unresolved -> unresolved

Never promote confidence.

R2 packages may expose V3-R1-compatible:
CONFIRMED
INTERPRETED
UNRESOLVED

But R2 itself must not create INTERPRETED semantic claims.

If translation is required:
upstream confirmed -> CONFIRMED
upstream unresolved -> UNRESOLVED
upstream inferred -> preserve explicit inferred provenance; do not promote.

COMPACTION
Critical requirement.

Do not create another ~280 MB copy of V2.

Use:

* IDs
* references
* normalized summaries
* counts
* selected records only

Avoid:

* copying full calls index
* copying all path evidence
* copying full architecture graph
* repeating same entity in every flow
* repeating same evidence body
* duplicating parameters unnecessarily

Packages should contain shared entity/reference collections where useful.

REFERENCE CLOSURE
Every internal reference included in a package must be either:

A) resolvable inside package
OR
B) explicitly external and point to a stable V2 artifact/entity reference.

No accidental broken references.

PROVENANCE
Every selected record must retain enough provenance to determine:

* originating V2 artifact/index
* stable upstream ID where available
* source snapshot
* upstream confidence/status where applicable

Do not embed absolute source paths unless existing approved metadata requires them.

UNRESOLVED
Unresolved evidence is required context, not noise.

Functional package must retain relevant unresolved boundaries.

Technical package must retain relevant unresolved structural/technical boundaries.

Support compact unresolved records:

unresolved_id
scope_ref
kind
upstream_ref
evidence_refs
confidence/status

Do not guess missing target.

SELECTION POLICY
Make package selection policy machine-readable.

At minimum:

package_type
requested_scope
expansion_depth
priority_policy
included_categories
excluded_categories
limits
truncated
truncation_reasons

This prepares V3-R3 token/context budgeting.

R2 does NOT implement token counting/budget optimization yet.

LIMITS
Allow deterministic record-count limits for defensive operation.

If a limit is reached:

* never silently drop data
* set truncated=true
* report category/reason/count
* preserve continuation/resolution references where practical

Default fixture tests should avoid truncation.

DOCUMENTATION CONTRACT INTEGRATION
ContextPackage must be compatible with V3-R1.

Future FUNCTIONAL_ASSESSMENT claims must be able to cite package/V2 evidence.

Future TECHNICAL_ASSESSMENT claims must be able to cite package/V2 evidence.

Do not generate assessments in R2.

OUTPUT CONTRACT
Prepare future structure:

output/
└── context_packages/
├── system/
├── functional/
├── technical/
├── entity/
├── flow/
└── data_access/

R2 real repository output is NOT generated automatically.

Fixtures/tests may write temporary packages.

SERIALIZATION
Deterministic canonical serialization.

No:

* random UUID
* Python hash()
* timestamps in semantic identity
* unstable set/dict ordering

Same V2 input + same resolver request + same policy
=> semantically identical package.

SECURITY
Do not bypass existing sanitization.

Context packages must not reintroduce secrets from configuration/evidence.

Prefer sanitized V2 facts.

If raw upstream evidence is ever referenced:
reference it; do not copy sensitive raw values.

V4 COMPATIBILITY
ContextResolver must depend on generic V2/system-model references rather than requiring:

* VB.NET
* WebForms
* Oracle
* .sln
* .vbproj

Current V2 data may contain these technologies.

They must not be mandatory concepts in ContextPackage schema.

This ensures future V4 adapters can feed equivalent system-model facts.

IMPLEMENTATION STRUCTURE
Follow existing project conventions.

Preferred conceptual location:

legacy_documenter/
└── context/
├── resolver.py
├── models.py
├── policies.py
└── loaders.py

Adjust if current structure provides a cleaner compatible placement.

Do not restructure unrelated V1/V2 code.

LOADER
Implement deterministic read-only loading of required V2 artifacts.

Responsibilities:

* validate artifact existence
* parse JSON
* expose source snapshot
* provide indexed lookup
* detect incompatible/mixed snapshots
* avoid loading unnecessary artifacts where practical

Do not mutate V2 artifacts.

INDEXING
Build in-memory deterministic lookup indexes where required.

Examples:

flow_id -> flow
path_id -> path
entry_point_id -> flow(s)
WebForm ref -> entry points
data_operation_id -> operation
stored_procedure_id -> SP
project_id -> project

Do not persist redundant full copies unless justified.

TESTS
Preserve all existing tests.

Add comprehensive V3-R2 coverage.

Minimum coverage points:

1 SYSTEM package valid
2 FUNCTIONAL package valid
3 TECHNICAL package valid
4 ENTITY package valid
5 FLOW package valid
6 DATA_ACCESS package valid
7 schema version present
8 source snapshot preserved
9 mixed snapshot rejected/detected
10 deterministic package ID
11 deterministic serialization
12 same request produces same package
13 exact entity lookup FOUND
14 missing entity NOT_FOUND
15 ambiguous lookup AMBIGUOUS
16 ambiguity candidates preserved
17 no semantic guessing
18 bounded expansion
19 expansion depth deterministic
20 WebForm->EntryPoint relation
21 EntryPoint->Flow relation
22 Flow->Path relation
23 Path->Method refs
24 Method->DAO relation
25 DAO->SP relation
26 DAO->SQL relation
27 project dependency relation
28 DLL dependency relation where fixture supports it
29 confirmed state preserved
30 unresolved state preserved
31 no confidence promotion
32 no R2-created INTERPRETED semantic claim
33 unresolved boundary retained
34 unresolved target not guessed
35 P0 priority represented
36 P1 priority represented
37 P2 priority represented
38 P3 priority represented
39 selection policy serialized
40 limits serialized
41 truncation explicit
42 no silent truncation
43 provenance artifact retained
44 provenance upstream ID retained
45 evidence refs retained
46 internal reference closure
47 external V2 reference explicit
48 no full calls duplication
49 no full graph duplication
50 no repeated evidence-body duplication
51 functional package contains UI/flows/data refs
52 functional package does not create module semantics
53 technical package contains project/dependency evidence
54 technical package does not declare architecture pattern
55 technical package retains data-access evidence
56 technical package retains configuration refs when available
57 SYSTEM remains summary-oriented
58 package output stack-neutral
59 WebForms not required by schema
60 Oracle not required by schema
61 future generic component accepted
62 V3-R1 EvidenceReference compatibility
63 V3-R1 claim can reference package evidence
64 read-only V2 artifacts
65 no legacy scan
66 no network
67 no LLM
68 sanitizer preserved
69 absolute internal paths not introduced
70 V1/V2 tests remain passing

Run:

python -m unittest discover -s tests

All PASS.

INTERNAL VALIDATION
Fixtures only.

Verify:

* all package types construct
* deterministic IDs
* deterministic serialization
* bounded traversal
* ambiguity handling
* unresolved preservation
* provenance
* reference closure
* compaction behavior
* truncation behavior
* V3-R1 compatibility
* no LLM/network
* no legacy source scan
* no V1/V2 regression

Do NOT execute full repository:

C:\Users\cgalianj\source\IST_40\operacional

NON_GOALS
Do NOT implement:

* token estimation/budget optimizer
* embeddings/vector database
* semantic search
* LLMProvider
* Copilot integration
* Gemini integration
* Ollama/Qwen integration
* OpenAI/Claude integration
* prompts for final documentation
* AI interpretation
* LEVANTAMIENTO_FUNCIONAL generation
* LEVANTAMIENTO_TECNICO generation
* human approval UI/workflow
* Knowledge Readiness
* Missing Information workflow
* AI_KNOWLEDGE
* V4 language adapters

REPORT
Create ONLY:

codex/V3/V3_R2_RESULTADO.md

Machine-oriented.
Compact.

FORMAT:

STATUS
FILES_CHANGED
CONTEXT_SCHEMA_VERSION
PACKAGE_TYPES
LOADER
RESOLUTION
EXPANSION
AMBIGUITY
PRIORITY_POLICY
FUNCTIONAL_PACKAGE
TECHNICAL_PACKAGE
SYSTEM_PACKAGE
UNRESOLVED
PROVENANCE
REFERENCE_CLOSURE
COMPACTION
TRUNCATION
V3_R1_COMPATIBILITY
V4_COMPATIBILITY
TESTS
DETERMINISM
SECURITY
REGRESSION
KNOWN_LIMITATIONS
NEXT

Expected:

STATUS=V3-R2_READY_FOR_REVIEW
NEXT=V3-R3_NOT_STARTED

Stop.
