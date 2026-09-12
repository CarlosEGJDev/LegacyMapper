TASK=V3-R7_1_ASSESSMENT_CONTRACT_ENFORCEMENT

MODE=CORRECT_AND_EXECUTE

PARENT=V3-R7
R7_STATUS=V3-R7_ASSESSMENT_VALIDATION_FAILURE

NO_R8
NO_AI_KNOWLEDGE
NO_FINAL_APPROVAL
NO_LEGACY_SOURCE_MODIFICATION
NO_V1_V2_REGENERATION
NO_FULL_REPOSITORY_SCAN
NO_VALIDATOR_WEAKENING
NO_SEMANTIC_REPAIR

OBJECTIVE

Correct V3-R7 real-assessment contract compliance without weakening R5.

Observed R7 failures:

FUNCTIONAL:

* profile mismatch
* unsupported source type
* invalid status promotion

TECHNICAL:

* profile mismatch
* unsupported source type
* invalid status promotion
* incomplete Claim schema
* incomplete MissingInformation schema

R7 correctly rejected both responses.

Goal:

make the model produce R5-compliant structured assessments by strengthening deterministic prompt/schema enforcement.

Do NOT modify validation rules merely to accept previous responses.

==================================================
NON-NEGOTIABLE INVARIANT
========================

AssessmentValidator remains authoritative.

Required flow:

ContextPackage
-> DocumentationProfile
-> Contract-Enforced DocumentationPrompt
-> LLMRequest
-> CopilotProvider
-> Structured Assessment
-> AssessmentValidator

Only VALID assessments may continue to:

aggregation
-> deterministic Markdown renderer

Invalid assessment:

REJECT
NO AGGREGATION
NO DOCUMENT
NO SILENT REPAIR

==================================================
ROOT CAUSE INSPECTION
=====================

Before modifying implementation:

inspect the exact R5 contracts and current R7 prompt serialization.

Determine whether each R7 failure originated from:

A) model non-compliance
B) prompt/schema omission
C) serialization mismatch
D) profile identifier mismatch
E) ambiguous contract instruction
F) implementation mapping error

Do not assume the model alone caused every failure.

Do not persist raw model responses containing unnecessary content.

Record root causes compactly in final report.

==================================================
CANONICAL CONTRACT
==================

The prompt MUST derive its output contract from the existing R5 structures.

Do not create an independent competing schema.

The model must receive an explicit canonical contract containing:

* exact profile identifier
* exact allowed assessment statuses
* exact allowed claim statuses
* exact allowed source types
* exact required Claim fields
* exact required MissingInformation fields
* exact evidence-reference rules
* exact context_package_id
* exact source_snapshot requirements

Prefer deterministic schema generation from existing Python types/constants.

Avoid manually duplicating enums when existing authoritative definitions can be reused.

==================================================
PROFILE ENFORCEMENT
===================

The requested profile ID must be inserted deterministically.

FUNCTIONAL call:

profile_id must equal the canonical FUNCTIONAL_ASSESSMENT profile identifier.

TECHNICAL call:

profile_id must equal the canonical TECHNICAL_ASSESSMENT profile identifier.

Explicit instruction:

RETURN profile_id EXACTLY as supplied.
DO NOT rename it.
DO NOT translate it.
DO NOT infer another profile.

Validator still verifies equality.

==================================================
SOURCE TYPE ENFORCEMENT
=======================

For R7 draft generation, model-emittable source types are limited to the types permitted by the current R5/R7 contract.

Explicitly provide the exact enum.

At this stage, do NOT permit the model to claim:

APPROVED_FUNCTIONAL_DOCUMENT
APPROVED_TECHNICAL_DOCUMENT
APPROVED_EXTERNAL_INFORMATION

No human approval exists.

AI interpretation must remain distinguishable from deterministic evidence.

Unknown source type:

INVALID.

Do not normalize an unknown source type after generation.

==================================================
CLAIM STATUS ENFORCEMENT
========================

Explicitly provide:

CONFIRMED
INTERPRETED
UNRESOLVED

Rules:

CONFIRMED
= only authoritative deterministic supporting evidence permits it.

INTERPRETED
= AI-derived interpretation grounded in supplied evidence.

UNRESOLVED
= evidence insufficient to establish the claim.

The model MUST NOT promote:

AI_INTERPRETATION -> CONFIRMED
UNRESOLVED -> CONFIRMED

If uncertain:

prefer INTERPRETED or UNRESOLVED.

Validator remains responsible for enforcement.

==================================================
CLAIM SCHEMA
============

Provide the exact required Claim structure to the model.

Every claim MUST contain every required field.

No omitted required fields.

No invented field names.

No aliases.

No prose outside the structured response.

Where contract fields are optional, preserve actual R5 semantics.

Do not change required fields merely because Luna omitted them in R7.

==================================================
MISSING INFORMATION SCHEMA
==========================

Provide exact MissingInformation structure.

Every emitted MissingInformation item MUST include all required fields defined by R5/R7.

R7 required semantics include:

request_id
document
section
question
reason
blocking_level
related_claim_ids
related_evidence_ids

Allowed blocking levels:

INFORMATIONAL
IMPORTANT
BLOCKING_FOR_APPROVAL

If there is no missing-information item:

return the canonical empty representation required by the schema.

Do not omit required container fields.

==================================================
EVIDENCE CLOSURE
================

Prompt must explicitly enumerate valid evidence IDs available to the assessment.

Instruction:

USE ONLY evidence IDs supplied in this ContextPackage.

DO NOT invent evidence IDs.
DO NOT modify evidence IDs.
DO NOT infer missing evidence IDs.

context_package_id and source_snapshot must also be copied exactly.

AssessmentValidator performs final closure validation.

==================================================
STRUCTURED OUTPUT
=================

Prefer SDK-native structured/schema-constrained output if Copilot SDK supports it without provider-specific contamination of core architecture.

If unavailable:

use strict JSON contract prompting.

The response must contain only the assessment payload expected by the parser.

No:

Markdown fences
explanation before JSON
explanation after JSON
comments
chain-of-thought

==================================================
CONTRACT EXEMPLAR
=================

Add ONE minimal deterministic exemplar for each profile only if necessary.

The exemplar must:

* use synthetic IDs;
* contain no legacy-system facts;
* demonstrate exact schema;
* demonstrate CONFIRMED vs INTERPRETED vs UNRESOLVED;
* demonstrate valid evidence references;
* demonstrate complete MissingInformation structure.

Do not use examples that bias the model toward a particular business module or architecture pattern.

Keep exemplars compact.

==================================================
CONTEXT SIZE
============

R6.1 succeeded with small controlled contexts.

R7 used two packages capped at 70 records.

For R7.1, reduce ambiguity before increasing model capability.

Use bounded real ContextPackages.

Initial target:

<= 40 evidence/context records per assessment

Preserve high-priority evidence first according to existing R3 P0-P4 policy.

Do NOT drop mandatory P0 evidence.

Do NOT truncate evidence required by emitted CONFIRMED claims.

If context cannot fit safely:

return BUDGET_INSUFFICIENT / appropriate existing status.

Do not fabricate completeness.

==================================================
R7 GENERATION ARCHITECTURE
==========================

Preserve existing R7 implementation:

aggregation.py
renderer.py
generator.py

Modify only what is necessary for contract compliance.

Do not rewrite working aggregation/rendering components unnecessarily.

==================================================
OFFLINE PREVALIDATION
=====================

Before making real calls, construct the exact request that would be sent.

Deterministically verify:

profile_id present and exact
schema present
allowed enums present
required Claim fields represented
required MissingInformation fields represented
context_package_id present
source_snapshot present
valid evidence IDs represented
forbidden approved source types excluded
output format explicitly constrained

If prevalidation fails:

do not call Copilot.

STATUS=V3-R7_1_REQUEST_CONTRACT_FAILURE

==================================================
TESTS
=====

Add/adjust deterministic offline tests for:

1 exact functional profile serialization
2 exact technical profile serialization
3 canonical status enum serialization
4 canonical source-type serialization
5 forbidden approved source types absent
6 complete Claim schema supplied
7 complete MissingInformation schema supplied
8 evidence IDs supplied exactly
9 context_package_id supplied exactly
10 source_snapshot supplied exactly
11 no status-promotion instruction ambiguity
12 strict JSON-only output instruction
13 malformed model response rejected
14 profile mismatch rejected
15 unknown source type rejected
16 incomplete Claim rejected
17 incomplete MissingInformation rejected
18 invented evidence rejected
19 AI_INTERPRETATION cannot become CONFIRMED
20 UNRESOLVED cannot become CONFIRMED
21 valid functional response accepted
22 valid technical response accepted
23 aggregation still excludes invalid assessments
24 renderer unchanged for valid assessment
25 request serialization deterministic

All unit tests offline.

Run:

python -m unittest discover -s tests

Baseline:

106 PASS

Expected:

> =106 PASS

==================================================
REAL PILOT
==========

After all tests PASS:

execute exactly TWO primary real calls.

CALL 1:
real bounded FUNCTIONAL assessment.

CALL 2:
real bounded TECHNICAL assessment.

Provider:

COPILOT

Model selection:

auto/configured.

Do NOT hardcode gpt-5.6-luna.

Record actual model returned.

==================================================
RETRY POLICY
============

Maximum primary real calls:

2

Maximum retry:

1 only for transport failure or syntactically malformed JSON if existing provider policy permits.

NO retry for:

semantic evidence violation
profile mismatch
status promotion
unsupported source type
missing required semantic fields

Such failures must be reported.

Do not repeatedly consume quota attempting to force compliance.

==================================================
SUCCESSFUL FUNCTIONAL ASSESSMENT
================================

PASS only if:

provider SUCCESS
strict structured response parses
profile exact
schema complete
source types valid
claim statuses valid
evidence closure PASS
context package PASS
source snapshot PASS
AssessmentValidator PASS

==================================================
SUCCESSFUL TECHNICAL ASSESSMENT
===============================

PASS requires the same validation plus:

architecture pattern is not forced.

Valid outcomes include:

CONFIRMED
INTERPRETED
NO_PATTERN_CONFIRMED
INSUFFICIENT_EVIDENCE

according to existing R5/R7 representation.

MissingInformation must be complete when emitted.

==================================================
DOCUMENT GENERATION
===================

If BOTH real assessments PASS:

run existing deterministic aggregation/rendering.

Generate:

output/LEVANTAMIENTO_FUNCIONAL.md
output/LEVANTAMIENTO_TECNICO.md

Both remain:

STATUS=DRAFT
HUMAN_REVIEW_REQUIRED=true
APPROVED=false
AI_KNOWLEDGE_ALLOWED=false

Do not mark them approved.

If either assessment fails:

do NOT generate or overwrite the corresponding document from invalid data.

If no previously valid R7 documents exist, leave it absent.

==================================================
DOCUMENT VALIDATION
===================

For generated documents verify:

non-empty
DRAFT
traceability present
no dangling evidence refs
no unsupported CONFIRMED claims
MissingInformation preserved
no forced architecture
no AI_KNOWLEDGE
no approval

==================================================
MODEL FAILURE TRACKING
======================

This is correction attempt:

R7.1 = MODEL/CONTRACT ATTEMPT 2 for real document-generation compliance.

If the real model still violates the semantic contract after the request itself passes deterministic prevalidation:

record:

MODEL_CONTRACT_ATTEMPT=2
MODEL_CHANGE_RECOMMENDED=false

Do not change model yet.

If a future R7.2 produces the third comparable model-contract failure:

MODEL_CONTRACT_ATTEMPT=3
MODEL_CHANGE_RECOMMENDED=true

This implements the standing three-failure rule.

==================================================
SECURITY
========

Maintain R7 security constraints:

no credentials persisted
no environment dump
no model filesystem tools
no model shell
no model Git
no MCP model actions
no legacy source modification
no raw authentication data

==================================================
SOURCE IMMUTABILITY
===================

Do not modify:

C:\Users\cgalianj\source\IST_40\operacional

Use existing V2 artifacts only.

==================================================
ACCEPTANCE
==========

SUCCESS:

both real assessments valid
both documents generated
all tests PASS
traceability closed
draft gate preserved

Then:

STATUS=V3-R7_1_READY_FOR_HUMAN_REVIEW
DECISION=ASSESSMENT_CONTRACT_ENFORCEMENT_VALIDATED
MODEL_CONTRACT_ATTEMPT=2
NEXT=V3-R8_HUMAN_REVIEW_NOT_STARTED

If request construction itself is invalid:

STATUS=V3-R7_1_REQUEST_CONTRACT_FAILURE
DECISION=IMPLEMENTATION_CORRECTION_REQUIRED
NEXT=V3-R7_1_NOT_CLOSED

If model returns structurally/semantically invalid assessments despite valid request:

STATUS=V3-R7_1_MODEL_CONTRACT_FAILURE
DECISION=MODEL_OUTPUT_REJECTED
MODEL_CONTRACT_ATTEMPT=2
MODEL_CHANGE_RECOMMENDED=false
NEXT=V3-R7_2_NOT_STARTED

If provider unavailable:

STATUS=V3-R7_1_BLOCKED_PROVIDER

Do not start R8.

==================================================
REPORT
======

Create ONLY:

codex/V3/V3_R7_1_RESULTADO.md

FORMAT:

STATUS
FILES_CHANGED
ROOT_CAUSE
CONTRACT_SOURCE
REQUEST_PREVALIDATION
CONTEXT_PACKAGE_LIMITS
SELECTED_PROVIDER
MODEL_ID
MODEL_CONTRACT_ATTEMPT
REAL_CALLS_EXECUTED
FUNCTIONAL_ASSESSMENT
TECHNICAL_ASSESSMENT
PROFILE_VALIDATION
SOURCE_TYPE_VALIDATION
CLAIM_SCHEMA_VALIDATION
MISSING_INFORMATION_VALIDATION
STATUS_PROMOTION_VALIDATION
EVIDENCE_CLOSURE
ASSESSMENT_VALIDATION
AGGREGATION
FUNCTIONAL_DOCUMENT
TECHNICAL_DOCUMENT
TRACEABILITY
UNIT_TESTS
TOTAL_TESTS
REGRESSION
SOURCE_IMMUTABILITY
SECURITY
MODEL_OBSERVATIONS
MODEL_CHANGE_RECOMMENDED
KNOWN_LIMITATIONS
FAILURES
DECISION
NEXT

Stop.