TASK=V3-R7_HUMAN_DOCUMENT_GENERATION

MODE=IMPLEMENT_AND_EXECUTE

NO_AI_KNOWLEDGE
NO_V3_R8
NO_LEGACY_SOURCE_MODIFICATION
NO_FULL_REPOSITORY_RESCAN_UNLESS_REQUIRED_BY_EXISTING_V2_CONTEXT
NO_EXTERNAL_INFORMATION
NO_HUMAN_APPROVAL_AUTOMATION

OBJECTIVE

Generate the first real human-reviewable documentation artifacts from the deterministic V1/V2 evidence and the validated V3 interpretation pipeline.

Produce exactly:

output/LEVANTAMIENTO_FUNCIONAL.md
output/LEVANTAMIENTO_TECNICO.md

These documents are DRAFTS.

They MUST NOT be treated as approved knowledge.

Pipeline:

V1/V2 deterministic facts
-> Context Resolver
-> DocumentationProfile
-> DocumentationPrompt
-> CopilotProvider
-> Structured Assessment
-> AssessmentValidator
-> Markdown Renderer
-> Human DRAFT documents

==================================================
PRECONDITIONS
=============

Required:

V3-R1 APPROVED
V3-R2 APPROVED
V3-R3.2 APPROVED
V3-R4 APPROVED
V3-R5 APPROVED
V3-R6.1 APPROVED

CopilotProvider available.

Local GitHub Copilot authentication available.

Existing full V2 outputs available.

Do not regenerate V1/V2.

If required V2 evidence is missing:

STATUS=V3-R7_BLOCKED_MISSING_V2_EVIDENCE

Stop.

If Copilot authentication/provider unavailable:

STATUS=V3-R7_BLOCKED_PROVIDER

Stop.

==================================================
SOURCE AUTHORITY
================

Permitted source types:

DETERMINISTIC_CODE_FACT
AI_INTERPRETATION
UNRESOLVED

Do NOT introduce:

APPROVED_FUNCTIONAL_DOCUMENT
APPROVED_TECHNICAL_DOCUMENT
APPROVED_EXTERNAL_INFORMATION

because human approval has not occurred yet.

No claim may be promoted to APPROVED.

==================================================
DOCUMENT STATUS
===============

Both generated documents MUST contain machine-readable metadata indicating:

document_status=DRAFT
human_review_required=true
approved=false
knowledge_source_eligible=false

The documents MUST NOT become AI_KNOWLEDGE sources yet.

==================================================
REAL SYSTEM CONTEXT
===================

Use real LegacyMapper V2 evidence.

Do not use the small R6 fixture.

Use the existing V2 system model and V3 Context Resolver.

Do not perform a new raw repository analysis.

Select and compose bounded ContextPackages from existing deterministic V2 artifacts.

==================================================
CONTEXT STRATEGY
================

Do NOT send the entire V2 dataset to the model.

Use deterministic composition.

Required hierarchy:

SYSTEM
PROJECT
MODULE/AREA candidate
UI / WEBFORM
ENTRY POINT
METHOD
CALL RELATIONSHIP
DATA ACCESS
STORED PROCEDURE / SQL
UNRESOLVED

Compose multiple bounded ContextPackages.

Respect existing R3 limits.

Preserve:

context_package_id
source_snapshot
evidence IDs
project references
flow references
path references
data-access references

==================================================
FUNCTIONAL DOCUMENT
===================

Generate:

output/LEVANTAMIENTO_FUNCIONAL.md

Purpose:

Describe what the application appears to do from the available evidence.

Required sections:

1. Metadata
2. Alcance del levantamiento
3. Resumen funcional del aplicativo
4. Módulos o áreas funcionales identificadas
5. Funcionalidades por módulo/área
6. Pantallas, WebForms o puntos de entrada relevantes
7. Flujos funcionales identificados
8. Integraciones funcionales detectadas
9. Operaciones de datos relacionadas con funcionalidades
10. Dependencias funcionales relevantes
11. Información no determinada
12. Solicitudes de información adicional
13. Trazabilidad
14. Estado de revisión

==================================================
FUNCTIONAL MODULE RULES
=======================

A module/functional area may be emitted only when supported by evidence.

Do not invent module boundaries.

Possible evidence:

project relationships
WebForms grouping
namespace grouping
functional flow relationships
shared service relationships
data-access relationships
explicit naming evidence

If grouping is inferred rather than deterministic:

claim_status=INTERPRETED

If evidence does not support a stable module boundary:

state that module grouping is uncertain.

Do not convert directory names into business modules without corroborating evidence.

==================================================
FUNCTIONAL CLAIM RULES
======================

CONFIRMED:

requires deterministic supporting evidence.

INTERPRETED:

allowed only when clearly labeled.

UNRESOLVED:

preserve when evidence is insufficient.

Do NOT invent:

business rules
actor permissions
process ownership
SLA
manual procedures
regulatory meaning
business justification
external integrations
screen purpose
module purpose

unless supported by evidence.

==================================================
TECHNICAL DOCUMENT
==================

Generate:

output/LEVANTAMIENTO_TECNICO.md

Purpose:

Describe the technical design and architecture supported by LegacyMapper evidence.

Required sections:

1. Metadata
2. Alcance técnico
3. Resumen tecnológico
4. Organización de soluciones y proyectos
5. Componentes técnicos identificados
6. Dependencias entre componentes
7. WebForms y capa de presentación
8. Lógica de aplicación / negocio
9. Acceso a datos
10. Oracle / procedimientos almacenados / SQL
11. Flujos técnicos representativos
12. Dependencias entre proyectos
13. Dependencias externas y ensamblados
14. Patrón de diseño / arquitectura
15. Evidencia a favor del patrón
16. Evidencia contradictoria o ambigua
17. Riesgos técnicos observables
18. Información técnica no determinada
19. Solicitudes de información adicional
20. Trazabilidad
21. Estado de revisión

==================================================
ARCHITECTURE PATTERN
====================

Do NOT force a known architecture pattern.

Allowed pattern assessment statuses:

CONFIRMED
INTERPRETED
NO_PATTERN_CONFIRMED
INSUFFICIENT_EVIDENCE

If identifying a pattern such as layered architecture:

include:

supporting evidence
contradicting evidence
confidence/status

Do not infer architecture only from project or folder names.

==================================================
TECHNICAL RISK RULES
====================

Only emit observable risks.

Examples of acceptable evidence-backed risk categories:

high coupling
cross-project dependencies
large unresolved call boundaries
direct provider access
shared components
legacy framework usage
high dependency concentration
mixed data-access styles
ambiguous project ownership

Do NOT assign severity based only on intuition.

Use:

OBSERVED
INTERPRETED
UNRESOLVED

No speculative security vulnerabilities.

==================================================
MISSING INFORMATION
===================

Use structured MissingInformation from R5.

Generate requests when evidence is insufficient.

Each request must include:

request_id
document
section
question
reason
blocking_level
related_claim_ids
related_evidence_ids

blocking_level:

INFORMATIONAL
IMPORTANT
BLOCKING_FOR_APPROVAL

Do not invent answers.

==================================================
LLM EXECUTION STRATEGY
======================

Use CopilotProvider validated in R6.1.

Model selection:

auto/configured through provider.

Record effective model if returned.

Do not hardcode gpt-5.6-luna.

Keep provider-neutral core.

==================================================
CALL BUDGET
===========

Avoid excessive model usage.

Use deterministic preprocessing and aggregation before LLM calls.

Prefer:

one system-level assessment
bounded functional package assessments
bounded technical package assessments

Do not perform one LLM call per method, class, WebForm, or flow.

Maximum real inference calls:

20

Target:

<= 12 calls

If context can be deterministically consolidated, prefer fewer calls.

==================================================
STRUCTURED FIRST
================

LLM MUST NOT directly write Markdown.

Required pipeline:

ContextPackages
-> structured AssessmentResult
-> AssessmentValidator
-> deterministic aggregation
-> deterministic Markdown renderer

Markdown must be generated only from validated structured assessments.

==================================================
ASSESSMENT VALIDATION
=====================

Every real response must pass existing R5 AssessmentValidator.

Invalid assessment:

must not enter final document.

Do not silently repair semantic violations.

If invalid:

record failure
optionally retry once only for malformed transport/JSON response

Do not retry semantic evidence violations repeatedly.

==================================================
AGGREGATION
===========

Implement deterministic aggregation of validated assessments.

Required:

deduplicate claims
preserve all evidence refs
preserve strongest valid status without promoting interpretations
merge MissingInformation deterministically
sort output deterministically
preserve source snapshots
preserve package provenance

Do not let the LLM perform final global deduplication.

==================================================
MARKDOWN RENDERING
==================

Renderer must be deterministic.

No provider/model-specific formatting.

Each major claim should expose its status.

Recommended compact notation:

[CONFIRMED]
[INTERPRETED]
[UNRESOLVED]

Do not include raw prompt text.

Do not include chain-of-thought.

Do not include credentials.

==================================================
TRACEABILITY
============

Each significant section must retain machine-resolvable traceability.

At minimum:

claim_id
claim_status
evidence_ids
context_package_ids

A final traceability section may summarize the mappings.

No dangling evidence reference permitted.

==================================================
DOCUMENT REVIEW GATE
====================

At end of each document include:

STATUS=DRAFT
HUMAN_REVIEW_REQUIRED=true
APPROVED=false
AI_KNOWLEDGE_ALLOWED=false

No automatic approval.

Do not generate knowledge readiness READY.

==================================================
FILES
=====

Preferred implementation locations:

legacy_documenter/documentation/generator.py
legacy_documenter/documentation/aggregation.py
legacy_documenter/documentation/renderer.py

Reuse existing modules when appropriate.

Do not duplicate functionality already present.

Tests:

tests/test_v3_r7.py

Generated outputs:

output/LEVANTAMIENTO_FUNCIONAL.md
output/LEVANTAMIENTO_TECNICO.md

Report:

codex/V3/V3_R7_RESULTADO.md

Do not create additional report files.

==================================================
TESTS
=====

Add offline deterministic tests for:

1 functional aggregation
2 technical aggregation
3 claim deduplication
4 no status promotion
5 missing information merging
6 evidence closure
7 deterministic ordering
8 functional Markdown renderer
9 technical Markdown renderer
10 DRAFT metadata
11 approval false
12 AI_KNOWLEDGE_ALLOWED false
13 architecture NO_PATTERN_CONFIRMED
14 architecture INSUFFICIENT_EVIDENCE
15 interpreted architecture pattern
16 unresolved sections preserved
17 provider response cannot bypass validator
18 invalid assessment excluded
19 source snapshots preserved
20 output deterministic across repeated runs

All model calls mocked in unit tests.

Run:

python -m unittest discover -s tests

Baseline:

85 tests PASS

Expected:

> 85 PASS

==================================================
REAL GENERATION VALIDATION
==========================

After tests PASS:

execute real V3-R7 generation.

Verify:

both documents exist
both non-empty
both DRAFT
both traceable
no dangling evidence
no unsupported CONFIRMED claims
no automatic approval
no AI_KNOWLEDGE
no raw secrets
no legacy source modifications

==================================================
SOURCE IMMUTABILITY
===================

Verify legacy source remains unchanged.

Do not write to:

C:\Users\cgalianj\source\IST_40\operacional

==================================================
SECURITY
========

No credential values.

No environment dump.

No model filesystem tools.

No model shell tools.

No model Git tools.

No MCP model actions.

No source modification.

==================================================
ACCEPTANCE
==========

Success requires:

* V3-R7 implementation complete;
* unit/regression tests PASS;
* functional DRAFT generated;
* technical DRAFT generated;
* all included LLM assessments validated;
* traceability closed;
* MissingInformation preserved;
* architecture pattern not forced;
* human approval required;
* AI_KNOWLEDGE blocked;
* no source mutation.

Success:

STATUS=V3-R7_READY_FOR_HUMAN_REVIEW
DECISION=HUMAN_DOCUMENT_DRAFTS_GENERATED
NEXT=V3-R8_HUMAN_REVIEW_NOT_STARTED

Failure examples:

V3-R7_BLOCKED_PROVIDER
V3-R7_BLOCKED_MISSING_V2_EVIDENCE
V3-R7_ASSESSMENT_VALIDATION_FAILURE
V3-R7_TRACEABILITY_FAILURE
V3-R7_GENERATION_FAILURE

Do not start R8.

==================================================
REPORT
======

Create ONLY:

codex/V3/V3_R7_RESULTADO.md

FORMAT:

STATUS
FILES_CHANGED
PRECONDITIONS
V2_SOURCE_ARTIFACTS
CONTEXT_PACKAGES
SELECTED_PROVIDER
MODEL_ID
REAL_CALLS_EXECUTED
FUNCTIONAL_ASSESSMENTS
TECHNICAL_ASSESSMENTS
ASSESSMENT_VALIDATION
AGGREGATION
FUNCTIONAL_DOCUMENT
TECHNICAL_DOCUMENT
ARCHITECTURE_PATTERN_RESULT
MISSING_INFORMATION
TRACEABILITY
UNIT_TESTS
TOTAL_TESTS
REGRESSION
SOURCE_IMMUTABILITY
SECURITY
KNOWN_LIMITATIONS
FAILURES
DECISION
NEXT

Stop.