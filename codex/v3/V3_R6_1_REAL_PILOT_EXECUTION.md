TASK=V3-R6_1_REAL_GEMINI_PILOT_EXECUTION

MODE=EXECUTE_AND_VALIDATE_ONLY

NO_ARCHITECTURE_CHANGES
NO_NEW_PROVIDER
NO_PROMPT_REDESIGN
NO_FULL_LEGACY_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_FINAL_DOCUMENT_GENERATION
NO_V3_R7

OBJECTIVE

Complete the real Gemini pilot already implemented in V3-R6.

Current state:

* GeminiProvider implemented.
* Offline provider tests PASS.
* Full suite = 78 PASS.
* Real pilot was NOT executed only because GEMINI_API_KEY was unavailable.

Do not redesign R6.

==================================================
PRECONDITION
============

Read Gemini credential only from environment:

GEMINI_API_KEY

Never:

* print the key;
* serialize the key;
* write the key into result files;
* write the key into source/tests;
* dump environment variables.

If GEMINI_API_KEY is absent:

STATUS=V3-R6_1_BLOCKED_CREDENTIAL_MISSING

Stop.

==================================================
MODEL CONFIGURATION
===================

Use a Gemini model ID supplied through existing provider configuration.

Do not hardcode commercial model catalogs into core.

If current pilot configuration already defines model_id, reuse it.

Do not install SDK.

Use existing GeminiProvider implementation.

==================================================
PILOT INPUT
===========

Use SMALL controlled fixture ContextPackages only.

Do not scan:

C:\Users\cgalianj\source\IST_40\operacional

Do not load giant V2 artifacts.

Pilot fixture must retain:

* context_package_id
* source_snapshot
* provenance
* evidence refs
* CONFIRMED deterministic evidence
* INTERPRETED-capable evidence
* UNRESOLVED evidence

==================================================
PILOT 1 — FUNCTIONAL
====================

Execute exactly one functional assessment call.

Flow:

ContextPackage
-> FUNCTIONAL_ASSESSMENT
-> DocumentationPrompt
-> LLMRequest
-> GeminiProvider
-> structured result
-> AssessmentValidator

PASS requires:

* provider SUCCESS
* structured response parseable
* FunctionalAssessmentResult valid
* no fabricated evidence IDs
* no evidence-less CONFIRMED claims
* AI interpretation remains INTERPRETED
* unresolved evidence preserved
* source_snapshot valid
* traceability valid

==================================================
PILOT 2 — TECHNICAL
===================

Execute exactly one technical assessment call.

PASS requires:

* provider SUCCESS
* TechnicalAssessmentResult valid
* component/dependency claims grounded
* no forced architecture pattern
* supporting/contradicting evidence preserved where applicable
* unknown/insufficient pattern acceptable
* no fabricated refs
* traceability valid

==================================================
PILOT 3 — INSUFFICIENT EVIDENCE
===============================

Execute exactly one deliberately insufficient-context call.

Expected valid result:

PARTIAL

or

NEEDS_MORE_INFORMATION

Must include structured missing-information output when appropriate.

FAIL if Gemini invents unsupported:

* business rule
* architecture
* dependency
* DB object
* module ownership
* external integration

==================================================
CALL LIMIT
==========

Maximum:

3 primary real calls total.

Optional:
1 retry per call ONLY for clearly retryable transport/provider failure.

No retries for:

* semantic validation failure
* fabricated evidence
* invalid claim status
* unsupported conclusions

Do not burn tokens trying to force the model to pass.

==================================================
ASSESSMENT VALIDATION
=====================

Provider SUCCESS does not equal assessment success.

Each response must pass existing AssessmentValidator.

Do not silently repair:

* evidence refs
* claim statuses
* missing information
* source snapshots
* package IDs

If validation fails:

record failure accurately.

==================================================
USAGE
=====

Capture provider usage when available:

input_tokens
output_tokens
total_tokens

If unavailable:

retain estimator and mark estimated=true.

Never fabricate exact values.

==================================================
MODEL OBSERVATION
=================

Report only pilot-specific observations:

* structured output compliance
* evidence reference compliance
* claim-status compliance
* missing-information behavior

Do not create generalized model ranking.

==================================================
SECURITY
========

Assert:

* credential absent from outputs
* credential absent from logs
* credential absent from report
* no environment dump
* no legacy scan
* no source modification
* no arbitrary command execution

==================================================
REGRESSION
==========

After pilot run:

python -m unittest discover -s tests

All existing tests must still PASS.

Expected baseline:

78 PASS

If no code changes are required, total may remain 78.

==================================================
SUCCESS
=======

Successful result only if all three real calls execute and validate.

Expected:

STATUS=V3-R6_1_READY_FOR_REVIEW
DECISION=REAL_PROVIDER_PILOT_VALIDATED
NEXT=V3-R7_NOT_STARTED

If one or more model responses violate the contract:

STATUS=V3-R6_1_MODEL_CONTRACT_FAILURE

Do not weaken validator/policies.

If credential missing:

STATUS=V3-R6_1_BLOCKED_CREDENTIAL_MISSING

==================================================
REPORT
======

Create ONLY:

codex/V3/V3_R6_1_RESULTADO.md

FORMAT:

STATUS
FILES_CHANGED
MODEL_ID
CREDENTIAL_AVAILABLE
REAL_CALLS_EXECUTED
FUNCTIONAL_PILOT
TECHNICAL_PILOT
INSUFFICIENT_EVIDENCE_PILOT
STRUCTURED_OUTPUT
ASSESSMENT_VALIDATION
TRACEABILITY
USAGE
MODEL_OBSERVATIONS
SECURITY
TOTAL_TESTS
REGRESSION
FAILURES
DECISION
NEXT

Stop.