TASK=V3-R1_DOCUMENTATION_CONTRACT

MODE=DESIGN_AND_IMPLEMENT_CONTRACTS
NO_LLM
NO_NETWORK
NO_FULL_REAL_REPOSITORY_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_V3_R2_PLUS

==================================================
OBJECTIVE
=========

Define and implement the formal V3 documentation contract used to produce:

1. Functional application assessment:
   LEVANTAMIENTO_FUNCIONAL

2. Technical application assessment:
   LEVANTAMIENTO_TECNICO

These documents will later be generated from V2 deterministic evidence + AI interpretation, reviewed by humans, approved/rejected, and only then become authorized inputs for AI_KNOWLEDGE generation.

V3-R1 does NOT generate final human documentation.
V3-R1 defines schemas/contracts/rules/validation for future generation.

==================================================
ARCHITECTURAL PRINCIPLE
=======================

V2:
deterministic system facts.

V3:
deterministic evidence
-> AI interpretation
-> human documentation
-> validation
-> human approval
-> knowledge readiness
-> AI_KNOWLEDGE

Core rule:

PYTHON/DETERMINISTIC_MODEL = FACT DISCOVERY
AI = INTERPRETATION
HUMAN = APPROVAL AUTHORITY

LegacyMapper must never convert unsupported AI interpretation into deterministic fact.

==================================================
V3 SOURCE TYPES
===============

Define canonical source/evidence types:

DETERMINISTIC_CODE_FACT
APPROVED_FUNCTIONAL_DOCUMENT
APPROVED_TECHNICAL_DOCUMENT
APPROVED_EXTERNAL_INFORMATION
AI_INTERPRETATION
UNRESOLVED

Do not collapse these categories.

Each knowledge/document claim must be traceable to one or more source/evidence records.

==================================================
CONFIDENCE / EVIDENCE STATUS
============================

Define canonical factual status:

CONFIRMED
INTERPRETED
UNRESOLVED

Semantics:

CONFIRMED:
directly supported by deterministic V2 evidence or explicitly approved authoritative information.

INTERPRETED:
AI/human interpretation derived from evidence but not a direct structural fact.

UNRESOLVED:
insufficient evidence to make a reliable statement.

Forbidden:

* promoting INTERPRETED to CONFIRMED automatically
* promoting UNRESOLVED to INTERPRETED/CONFIRMED without new evidence
* inventing business rules
* guessing architecture pattern from names/folders only
* guessing module purpose solely from naming
* guessing external integrations
* guessing project responsibilities
* fabricating missing functional flows

==================================================
DOCUMENT 1
LEVANTAMIENTO_FUNCIONAL
=======================

Define formal document type:

FUNCTIONAL_ASSESSMENT

Required human output target:

`LEVANTAMIENTO_FUNCIONAL.md`

Contract must support at minimum:

1. Document metadata
2. Application purpose
3. Scope analyzed
4. Functional modules
5. Functions by module
6. Screens/interfaces involved
7. Main functional flows
8. Identifiable business/functional rules
9. Query/read processes
10. Update/write processes
11. Functional integrations
12. Data dependencies
13. Unresolved functional areas
14. Technical evidence traceability
15. Assumptions/interpretations
16. Known limitations
17. Review/approval information

Each functional module must support:

module_id
name
description
status
confidence
source_refs
functionalities[]
entry_points[]
flows[]
data_dependencies[]
unresolved_items[]

Each functionality must support:

functionality_id
name
description
status
confidence
source_refs
related_modules
entry_points
flow_ids
data_access_refs
stored_procedure_refs
unresolved_refs

Do not require that every application maps cleanly into modules.

Allow:

UNASSIGNED
CROSS_MODULE
UNKNOWN_MODULE

when evidence does not support confident grouping.

==================================================
FUNCTIONAL CLAIM RULES
======================

Examples of acceptable:

CONFIRMED:
"This WebForm participates in flow X."

INTERPRETED:
"This flow appears to support debt consultation."

UNRESOLVED:
"Business condition determining regularizability cannot be established from available evidence."

The contract must make these distinctions machine-readable.

Business semantics inferred from identifiers must remain INTERPRETED unless independently supported.

==================================================
DOCUMENT 2
LEVANTAMIENTO_TECNICO
=====================

Define formal document type:

TECHNICAL_ASSESSMENT

Required human output target:

`LEVANTAMIENTO_TECNICO.md`

Contract must support at minimum:

1. Document metadata
2. Technical overview
3. Analyzed scope
4. Solutions/projects
5. Component organization
6. Architecture/design patterns
7. Project dependencies
8. Web/UI components
9. Business/application logic
10. Data access
11. Database/SP/SQL usage
12. Configuration
13. External integrations
14. Representative technical flows
15. Security mechanisms identified
16. Error handling
17. Deployment/runtime observations
18. Technical debt/risks observable from evidence
19. Unknown/non-determinable technical areas
20. Traceability
21. Review/approval information

==================================================
ARCHITECTURE / DESIGN PATTERN CONTRACT
======================================

Pattern identification requires explicit evidence.

Define structure:

pattern_id
pattern_name
classification
status
confidence
evidence_refs
supporting_observations
contradicting_observations
scope
notes

classification examples:

ARCHITECTURAL_PATTERN
DESIGN_PATTERN
LAYERING_STYLE
INTEGRATION_PATTERN
UNKNOWN

Pattern status:

CONFIRMED
INTERPRETED
UNRESOLVED

Never declare patterns solely because:

* folder names resemble layers
* project names contain BL/DAL/Web
* framework normally uses a pattern
* naming convention suggests MVC/MVP/etc.

Pattern evidence may include:

* project dependencies
* component relationships
* inheritance/interface structure
* call directions
* UI->logic->data flow
* configuration evidence
* repeated structural relationships

Allow multiple patterns.

Allow:

NO_PATTERN_CONFIRMED
INSUFFICIENT_EVIDENCE

==================================================
TECHNICAL CLAIM RULES
=====================

Structural facts from V2 remain deterministic.

Example:

CONFIRMED:
Project A references Project B.

INTERPRETED:
Observed dependency direction is consistent with a layered architecture.

UNRESOLVED:
Evidence is insufficient to identify a formal design pattern.

Do not automatically convert architecture interpretation into fact.

==================================================
COMMON DOCUMENT METADATA
========================

Both document types must define metadata containing at least:

document_id
document_type
schema_version
source_snapshot
generated_at
generator
provider
model
generation_mode
status
revision
scope
source_refs
validation_status
approval_status
approved_by
approved_at

Notes:

generated_at is metadata only and MUST NOT participate in deterministic semantic identity.

provider/model may be null before AI generation.

approved_by/approved_at may be null before approval.

==================================================
DOCUMENT LIFECYCLE
==================

Define lifecycle:

DRAFT
GENERATED
VALIDATED
NEEDS_CHANGES
APPROVED
REJECTED
SUPERSEDED

Allowed progression should be explicit.

Recommended:

DRAFT
-> GENERATED
-> VALIDATED
-> APPROVED

Alternative:

GENERATED
-> NEEDS_CHANGES
-> GENERATED

or:

VALIDATED
-> REJECTED

Approved content must not be silently overwritten.

New generation after APPROVED must create a new revision/version.

==================================================
APPROVAL GATE
=============

AI_KNOWLEDGE generation MUST be blocked unless:

functional_assessment.approval_status=APPROVED

AND

technical_assessment.approval_status=APPROVED

Future rounds may add additional readiness conditions.

V3-R1 only defines this contract.

Do not implement AI_KNOWLEDGE generator yet.

==================================================
TRACEABILITY CONTRACT
=====================

Every material claim must support:

claim_id
document_id
section_id
claim_type
text_or_structured_value
status
confidence
source_refs
evidence_refs
related_entities
validation_state

Source references must be stable IDs/references to V2 artifacts whenever possible.

Do not embed full V2 evidence repeatedly.

Prefer references such as:

project_id
symbol_id
webform_id
entry_point_id
flow_id
path_id
call_id
data_operation_id
stored_procedure_id
sql_operation_id

The contract must permit one claim -> many evidence refs.

==================================================
CLAIM TYPES
===========

Define at least:

APPLICATION_PURPOSE
MODULE
FUNCTIONALITY
FUNCTIONAL_FLOW
BUSINESS_RULE
INTEGRATION
DATA_DEPENDENCY

TECHNOLOGY
PROJECT_STRUCTURE
COMPONENT_RESPONSIBILITY
DEPENDENCY
ARCHITECTURE_PATTERN
DESIGN_PATTERN
DATA_ACCESS
SECURITY
ERROR_HANDLING
DEPLOYMENT
TECHNICAL_RISK

UNKNOWN
LIMITATION

Extensible contract required.

==================================================
UNRESOLVED / MISSING INFORMATION
================================

Both documents must explicitly retain information gaps.

Define MissingInformation record:

missing_id
document_type
scope
category
description
reason
impact
required_information
source_refs
status

status:

OPEN
PROVIDED
RESOLVED
NOT_AVAILABLE
NOT_REQUIRED

Categories may include:

BUSINESS_RULE
MODULE_PURPOSE
FUNCTIONALITY
EXTERNAL_INTEGRATION
SECURITY
DEPLOYMENT
ARCHITECTURE
DATA_SEMANTICS
OTHER

This structure will feed future V3 Knowledge Readiness / Information Request rounds.

==================================================
EXTERNAL INFORMATION PREPARATION
================================

Define future-compatible contract for human/external information.

Do NOT implement ingestion workflow yet.

Required future source type:

APPROVED_EXTERNAL_INFORMATION

Metadata should support:

external_info_id
title
description
provided_by
provided_at
scope
approval_status
source_reference
claims_supported

No external information becomes authoritative without explicit approval.

==================================================
STRUCTURED CONTRACTS
====================

Implement machine-readable models/schemas for at least:

DocumentMetadata
EvidenceReference
DocumentClaim
MissingInformation
FunctionalAssessment
FunctionalModule
Functionality
TechnicalAssessment
ArchitecturePatternAssessment
DocumentReview
DocumentApproval

Use existing project conventions.

Prefer Pydantic/dataclasses only if consistent with current LegacyMapper architecture.

Do not add unnecessary dependencies.

==================================================
SCHEMA VERSIONING
=================

Introduce explicit V3 documentation schema version.

Example:

`3.0.0`

Schema version must be present in top-level assessment artifacts.

Future schema changes must be distinguishable.

==================================================
IDENTITY
========

Stable IDs required for structured records.

No:

random UUID
Python hash()
timestamps as identity

Use deterministic identity derived from canonical stable fields where appropriate.

Human-generated/approval records may use externally supplied IDs if explicitly defined.

==================================================
VALIDATION
==========

Implement deterministic validation rules.

At minimum validate:

* required metadata
* valid document type
* valid status
* valid confidence/state enums
* source snapshot presence
* claim IDs unique
* module IDs unique
* functionality IDs unique
* architecture pattern IDs unique
* references syntactically valid
* APPROVED requires validation status
* AI_KNOWLEDGE gate requires both assessments APPROVED
* CONFIRMED claim requires supporting authoritative evidence reference
* UNRESOLVED cannot masquerade as CONFIRMED
* missing information IDs unique
* deterministic serialization/order where applicable

==================================================
MARKDOWN CONTRACT
=================

Define deterministic section contract/templates for:

LEVANTAMIENTO_FUNCIONAL.md
LEVANTAMIENTO_TECNICO.md

Do NOT generate final application documentation.

Templates should define headings/order/placeholders only.

Machine data remains authoritative for structure.

Future AI generation fills narrative sections.

==================================================
OUTPUT CONTRACT
===============

Prepare future directory contract:

output/
└── documentation/
├── functional/
│   ├── LEVANTAMIENTO_FUNCIONAL.json
│   └── LEVANTAMIENTO_FUNCIONAL.md
│
├── technical/
│   ├── LEVANTAMIENTO_TECNICO.json
│   └── LEVANTAMIENTO_TECNICO.md
│
├── reviews/
└── evidence/

Do not generate real repository documents in R1.

Fixture/test outputs may use temporary paths only.

==================================================
V4 COMPATIBILITY
================

V3 documentation contracts MUST NOT hardcode VB.NET/WebForms/Oracle as required concepts.

They may reference current V2 entity IDs generically.

Contract must allow future systems using:

.NET
Java
Python
JavaScript/TypeScript
Angular
React
other stacks

Do NOT implement V4 adapters.

V3 must be agnostic to knowledge origin even though current producer is V2 .NET analysis.

==================================================
FILES / STRUCTURE
=================

Follow current repository conventions.

Preferred conceptual location:

legacy_documenter/
└── documentation/
├── models/
├── validation/
├── templates/
└── contracts/

Adjust to existing architecture if a cleaner compatible location exists.

Avoid restructuring unrelated V1/V2 code.

==================================================
TESTS
=====

Add comprehensive unit tests.

Minimum coverage points:

1 functional assessment valid
2 technical assessment valid
3 schema version required
4 invalid document type rejected
5 invalid lifecycle state rejected
6 duplicate claim ID rejected
7 duplicate module ID rejected
8 duplicate functionality ID rejected
9 duplicate pattern ID rejected
10 CONFIRMED claim with evidence accepted
11 CONFIRMED claim without authoritative evidence rejected
12 INTERPRETED claim accepted with evidence
13 UNRESOLVED preserved
14 unresolved cannot be promoted implicitly
15 functional module UNKNOWN supported
16 CROSS_MODULE supported
17 multiple evidence refs supported
18 architecture pattern CONFIRMED
19 architecture pattern INTERPRETED
20 architecture pattern UNRESOLVED
21 insufficient architecture evidence representable
22 contradicting evidence representable
23 MissingInformation OPEN
24 MissingInformation PROVIDED
25 MissingInformation RESOLVED
26 external information contract representable
27 unapproved external info not authoritative
28 document validation lifecycle
29 approval lifecycle
30 APPROVED requires validation
31 approved document revision immutable semantics
32 functional approval gate false
33 technical approval gate false
34 both approved gate true
35 stable IDs deterministic
36 no Python hash identity
37 serialization deterministic
38 V2 refs represented without full evidence duplication
39 WebForms-specific fields not required
40 Oracle-specific fields not required
41 future language-neutral component refs accepted
42 functional Markdown section contract
43 technical Markdown section contract
44 source snapshot required
45 approval metadata nullable before approval
46 provider/model nullable before generation
47 generated metadata accepted
48 claim type extensibility
49 traceability one-to-many evidence
50 no network/LLM required

Run:

`python -m unittest discover -s tests`

All PASS.

==================================================
INTERNAL VALIDATION
===================

Use fixtures only.

Verify:

* contracts instantiate
* invalid states rejected
* deterministic serialization
* Markdown structure contract
* approval gate
* no dependency on LLM
* no network
* no legacy repository scan
* no V1/V2 regression

Do NOT execute:

`C:\Users\cgalianj\source\IST_40\operacional`

==================================================
NON-GOALS
=========

Do NOT implement:

ContextResolver
token budgeting
LLMProvider
Ollama/OpenAI/Claude providers
AI generation
final functional documentation
final technical documentation
human UI
knowledge readiness engine
information request generator
AI_KNOWLEDGE
language adapters
V4 Universal IR

==================================================
REPORT
======

Create ONLY:

`codex/V3/V3_R1_RESULTADO.md`

Machine-oriented.
Compact.

FORMAT:

STATUS
FILES_CHANGED
CONTRACT_VERSION
FUNCTIONAL_CONTRACT
TECHNICAL_CONTRACT
CLAIM_MODEL
EVIDENCE_MODEL
CONFIDENCE_MODEL
PATTERN_MODEL
MISSING_INFORMATION_MODEL
DOCUMENT_LIFECYCLE
APPROVAL_GATE
TRACEABILITY
MARKDOWN_CONTRACT
V4_COMPATIBILITY
TESTS
DETERMINISM
SECURITY
REGRESSION
KNOWN_LIMITATIONS
NEXT

Expected successful status:

`V3-R1_READY_FOR_REVIEW`

NEXT must state:

`V3-R2_NOT_STARTED`

Stop.