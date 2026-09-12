TASK=V3-R8_HUMAN_REVIEW

MODE=PREPARE_HUMAN_REVIEW

PARENT=V3-R7_2_4
PARENT_STATUS=V3-R7_2_4_READY_FOR_HUMAN_REVIEW

NO_AUTOMATIC_APPROVAL
NO_AI_KNOWLEDGE
NO_NEW_LLM_INTERPRETATION
NO_PROVIDER_CALLS
NO_V1_V2_REGENERATION
NO_ASSESSMENT_REGENERATION
NO_RAW_REPOSITORY_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_DOCUMENT_SEMANTIC_REWRITE
NO_CLAIM_PROMOTION
NO_MISSING_INFORMATION_RESOLUTION
NO_HUMAN_DECISION_INFERENCE

==================================================
OBJECTIVE
=========

Prepare the LegacyMapper V3 documentation for explicit human review.

The human reviewer must be able to understand:

1. what LegacyMapper CONFIRMED;
2. what LegacyMapper INTERPRETED;
3. what remains UNRESOLVED;
4. what additional information is requested;
5. what structural coverage was achieved;
6. what semantic limitations remain;
7. what the reviewer must explicitly approve, reject or request changes for.

Codex must prepare the review package.

Codex must NOT make the human approval decision.

==================================================
AUTHORITATIVE REVIEW INPUTS
===========================

Primary documents:

output/LEVANTAMIENTO_FUNCIONAL.md
output/LEVANTAMIENTO_TECNICO.md

Supporting validated artifacts:

output/v3_r7_2/LOCAL_ASSESSMENTS.json
output/v3_r7_2/INTERMEDIATE_ASSESSMENTS.json
output/v3_r7_2/COVERAGE_INDEX.json

Parent report:

codex/V3/V3_R7_2_4_RESULTADO.md

Use these existing artifacts.

Do not regenerate semantic assessments.

==================================================
PRECONDITIONS
=============

Verify before preparing review:

FUNCTIONAL_DOCUMENT_STATUS=DRAFT
TECHNICAL_DOCUMENT_STATUS=DRAFT

FUNCTIONAL_HUMAN_REVIEW_REQUIRED=true
TECHNICAL_HUMAN_REVIEW_REQUIRED=true

FUNCTIONAL_APPROVED=false
TECHNICAL_APPROVED=false

FUNCTIONAL_KNOWLEDGE_SOURCE_ELIGIBLE=false
TECHNICAL_KNOWLEDGE_SOURCE_ELIGIBLE=false

R7_2_4_STATUS=READY_FOR_HUMAN_REVIEW

If any precondition fails:

STOP.

STATUS=V3-R8_PRECONDITION_FAILURE

==================================================
REVIEW PRINCIPLE
================

R8 is a HUMAN GATE.

The system may:

* organize information;
* summarize existing validated claims deterministically;
* group claims by status;
* present evidence references;
* present MissingInformation;
* provide review checklists;
* record an explicit future human decision.

The system may NOT:

* approve its own output;
* reinterpret evidence;
* resolve UNRESOLVED claims;
* promote INTERPRETED claims;
* invent missing information;
* infer approval from silence;
* infer approval from tests passing.

==================================================
HUMAN REVIEW PACKAGE
====================

Create:

codex/V3/V3_R8_PAQUETE_REVISION_HUMANA.md

This is the primary artifact that the user will review.

It must be concise enough for practical human review.

Do not copy the complete traceability payload into the main review sections.

Provide references to the original documents for detailed provenance.

==================================================
PACKAGE STRUCTURE
=================

The review package must contain:

# LegacyMapper V3 — Revisión Humana

## 1. Estado

Display:

FUNCTIONAL_DOCUMENT=DRAFT
TECHNICAL_DOCUMENT=DRAFT
HUMAN_REVIEW_REQUIRED=true
AI_KNOWLEDGE_ALLOWED=false

Explain briefly:

This package does not approve the documentation.
The human reviewer must provide the final decision.

==================================================
2. SYSTEM COVERAGE SUMMARY
==========================

Present deterministic structural coverage separately from semantic understanding.

Include:

PROJECTS_CLASSIFIED=259
SOLUTIONS_REPRESENTED=113
WEBFORMS_REPRESENTED=3346
FUNCTIONAL_FLOWS_REPRESENTED=12642
LINKED_DATA_OPERATIONS=19159
LINKED_STORED_PROCEDURES=5389
UNRESOLVED_RELATIONSHIPS=162914

Explicitly state:

STRUCTURAL_COVERAGE != COMPLETE_SEMANTIC_UNDERSTANDING

Do not imply that all 259 projects are semantically understood.

==================================================
3. FUNCTIONAL REVIEW
====================

Use:

output/LEVANTAMIENTO_FUNCIONAL.md

Present claims grouped into:

### 3.1 Confirmed

For each:

ID
short statement
evidence reference summary

### 3.2 Interpreted

For each:

ID
short statement
evidence reference summary
review warning:

REQUIRES_HUMAN_CONFIRMATION

### 3.3 Unresolved

For each:

ID
short statement
why unresolved if existing document states it

Do not reinterpret.

==================================================
4. FUNCTIONAL MISSING INFORMATION
=================================

Present canonical:

FMI-001..FMI-008

For each:

ID
family
blocking level
question
reason

Do not include enormous evidence lists in the primary review view.

Instead include:

TRACEABILITY_AVAILABLE=true

and reference the corresponding section in:

output/LEVANTAMIENTO_FUNCIONAL.md

==================================================
5. FUNCTIONAL HUMAN CHECKLIST
=============================

Ask reviewer to evaluate:

[ ] Are the identified functional areas correct?
[ ] Are important functional areas missing?
[ ] Are the described WebForms/entry points representative?
[ ] Are interpreted functional conclusions reasonable?
[ ] Are any CONFIRMED claims actually incorrect?
[ ] Can I answer any FMI requests?
[ ] Are any FMI requests unnecessary?
[ ] Does the document adequately describe the application functionally?

Do not pre-check boxes.

==================================================
6. TECHNICAL REVIEW
===================

Use:

output/LEVANTAMIENTO_TECNICO.md

Present claims grouped into:

### 6.1 Confirmed

ID
short statement
evidence reference summary

### 6.2 Interpreted

ID
short statement
evidence reference summary
REQUIRES_HUMAN_CONFIRMATION

### 6.3 Unresolved

ID
short statement
reason when available

==================================================
7. QUANTITATIVE TECHNICAL REVIEW
================================

Explicitly present scope distinctions discovered in R7.2.4.

SYSTEM STRUCTURAL:

linked_data_operations=19159
linked_stored_procedures=5389

COVERAGE PARTITION EXAMPLES:

data_access_partition_count=2009
stored_procedures_partition_count=674

Explain:

These values have different deterministic scopes and are not directly contradictory.

The reviewer should verify whether the terminology accurately communicates the legacy system.

Do not change the numbers.

==================================================
8. TECHNICAL MISSING INFORMATION
================================

Present canonical:

TMI-001..TMI-012

For each:

ID
family
blocking level
question
reason

Highlight especially:

TECHNICAL_ARCHITECTURE_PATTERN
TECHNICAL_PROJECT_DEPENDENCIES
TECHNICAL_EXTERNAL_DEPENDENCIES
TECHNICAL_COMPONENT_RESPONSIBILITY
TECHNICAL_END_TO_END_FLOW

Do not resolve them.

==================================================
9. TECHNICAL HUMAN CHECKLIST
============================

Ask reviewer:

[ ] Are the identified technical components correct?
[ ] Is the WebForms presentation description correct?
[ ] Is the Oracle/data-access description correct?
[ ] Are project/component responsibilities correctly represented?
[ ] Do I know the architecture/pattern used by the system?
[ ] Can I provide missing project dependency information?
[ ] Can I provide external assembly/dependency information?
[ ] Can I clarify end-to-end WebForm -> BL -> DAL/SYS -> Oracle flows?
[ ] Are any CONFIRMED technical claims incorrect?
[ ] Are INTERPRETED technical claims reasonable?
[ ] Can I answer any TMI requests?
[ ] Does the technical document adequately represent the system?

Do not pre-check.

==================================================
10. CRITICAL ITEMS FOR APPROVAL
===============================

Produce deterministic lists:

FUNCTIONAL_BLOCKING_ITEMS

TECHNICAL_BLOCKING_ITEMS

Include canonical MissingInformation with:

blocking_level=BLOCKING_FOR_APPROVAL

Do not decide whether the reviewer must actually provide every item.

Present them as system-declared blockers requiring explicit human disposition.

Human disposition may be:

ANSWERED
ACCEPTED_AS_UNRESOLVED
NEEDS_ANALYSIS
NOT_APPLICABLE

Only human may choose disposition.

==================================================
11. REVIEWER RESPONSE TEMPLATE
==============================

Create an empty response template.

FUNCTIONAL_DECISION=
TECHNICAL_DECISION=

Allowed:

APPROVED
NEEDS_CHANGES
NEEDS_MORE_INFORMATION
REJECTED

Then:

FUNCTIONAL_COMMENTS=

TECHNICAL_COMMENTS=

FUNCTIONAL_MISSING_INFORMATION_RESPONSES=

TECHNICAL_MISSING_INFORMATION_RESPONSES=

GENERAL_COMMENTS=

Do not populate any decision.

==================================================
12. APPROVAL RULES
==================

AI_KNOWLEDGE remains blocked unless:

FUNCTIONAL_DECISION=APPROVED
AND
TECHNICAL_DECISION=APPROVED

A test PASS does not count as approval.

A Codex status does not count as approval.

Generation of this review package does not count as approval.

Only explicit human reviewer decision counts.

==================================================
REVIEW RESPONSE FILE
====================

Also create:

codex/V3/V3_R8_RESPUESTA_REVISION.md

Initial content must contain the empty reviewer response template.

It must NOT contain:

APPROVED

as a selected decision.

Allowed initial values:

FUNCTIONAL_DECISION=PENDING
TECHNICAL_DECISION=PENDING

==================================================
FUTURE HUMAN INPUT
==================

R8 execution ends after package preparation.

Do NOT wait interactively inside Codex.

The expected workflow is:

Codex prepares package
↓
User receives package
↓
User reviews documents
↓
User fills/provides review decision
↓
new explicit Codex instruction
↓
record human decision
↓
evaluate knowledge readiness

The current execution must stop before recording a human decision.

==================================================
NO AUTOMATIC DOCUMENT MODIFICATION
==================================

If Codex notices a possible documentation problem during package generation:

do not modify the source documents.

Record it under:

REVIEW_OBSERVATIONS

in the review package.

Human decides whether another correction round is required.

==================================================
TRACEABILITY
============

The review package may compact traceability for readability.

It must never destroy original traceability.

Detailed provenance remains authoritative in:

LEVANTAMIENTO_FUNCIONAL.md
LEVANTAMIENTO_TECNICO.md
validated assessments

==================================================
TESTS
=====

Create/update:

tests/test_v3_r8.py

Minimum offline tests:

1 functional DRAFT required
2 technical DRAFT required
3 functional human_review_required
4 technical human_review_required
5 approved false precondition
6 knowledge eligibility false
7 package generation deterministic
8 package contains coverage summary
9 structural vs semantic warning present
10 confirmed functional claims represented
11 interpreted functional claims represented
12 unresolved functional claims represented
13 FMI canonical requests represented
14 functional checklist unselected
15 confirmed technical claims represented
16 interpreted technical claims represented
17 unresolved technical claims represented
18 TMI canonical requests represented
19 technical checklist unselected
20 quantitative scope distinction represented
21 2009 partition retained
22 19159 system metric retained
23 674 partition retained
24 5389 system metric retained
25 blocking functional items represented
26 blocking technical items represented
27 response template generated
28 functional decision PENDING
29 technical decision PENDING
30 no automatic APPROVED decision
31 no knowledge eligibility promotion
32 no source document semantic modification
33 no assessment modification
34 no V2 modification
35 no provider execution
36 no LLM execution
37 no raw repository scan
38 no legacy source modification
39 traceability references preserved
40 explicit human approval required
41 both documents required for knowledge readiness
42 one approved + one pending remains blocked
43 tests cannot trigger approval
44 Codex status cannot trigger approval
45 package creation cannot trigger approval

Run:

python -m unittest discover -s tests

Baseline:

359 PASS

Expected:

> 359 PASS

==================================================
IMMUTABILITY
============

Record pre/post hashes for:

output/LEVANTAMIENTO_FUNCIONAL.md
output/LEVANTAMIENTO_TECNICO.md
output/v3_r7_2/LOCAL_ASSESSMENTS.json
output/v3_r7_2/INTERMEDIATE_ASSESSMENTS.json
V2 artifacts

All must remain unchanged.

R8 creates review artifacts only.

==================================================
REAL EXECUTION
==============

After offline tests PASS:

generate:

codex/V3/V3_R8_PAQUETE_REVISION_HUMANA.md
codex/V3/V3_R8_RESPUESTA_REVISION.md
codex/V3/V3_R8_RESULTADO.md

No provider calls.

No LLM calls.

No semantic regeneration.

==================================================
SUCCESS
=======

STATUS=V3-R8_WAITING_FOR_HUMAN_REVIEW

This is the expected successful state.

Do NOT use:

V3-R8_APPROVED

because no human decision has yet been supplied.

==================================================
RESULT REPORT
=============

Create:

codex/V3/V3_R8_RESULTADO.md

FORMAT:

STATUS
FILES_CHANGED
PRECONDITIONS
REVIEW_INPUTS
FUNCTIONAL_DOCUMENT
TECHNICAL_DOCUMENT
STRUCTURAL_COVERAGE
FUNCTIONAL_CLAIMS
FUNCTIONAL_MISSING_INFORMATION
TECHNICAL_CLAIMS
TECHNICAL_MISSING_INFORMATION
BLOCKING_ITEMS
REVIEW_PACKAGE
REVIEW_RESPONSE_TEMPLATE
REVIEW_OBSERVATIONS
NEW_REAL_LLM_CALLS
PROVIDER_CALLS
SOURCE_DOCUMENTS_UNCHANGED
ASSESSMENTS_UNCHANGED
V2_IMMUTABILITY
SOURCE_IMMUTABILITY
UNIT_TESTS
TOTAL_TESTS
REGRESSION
AI_KNOWLEDGE_ALLOWED
HUMAN_DECISION
DECISION
NEXT

Expected:

AI_KNOWLEDGE_ALLOWED=false
HUMAN_DECISION=PENDING
DECISION=WAITING_FOR_EXPLICIT_HUMAN_REVIEW
NEXT=USER_REVIEW

Stop.