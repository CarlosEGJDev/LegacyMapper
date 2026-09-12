TASK=V3-R6_REAL_PROVIDER_PILOT

MODE=IMPLEMENT_AND_VALIDATE

ALLOW_REAL_LLM_PILOT
ALLOW_NETWORK_ONLY_FOR_SELECTED_PROVIDER
NO_FULL_LEGACY_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_FINAL_DOCUMENT_GENERATION
NO_HUMAN_APPROVAL_WORKFLOW
NO_AI_KNOWLEDGE
NO_V3_R7_PLUS

OBJECTIVE

Implement ONE real LLM provider adapter and validate the complete V3 interpretation pipeline using a small controlled ContextPackage.

This is a pilot.

R6 must prove:

ContextPackage
-> DocumentationProfile
-> DocumentationPrompt
-> LLMRequest
-> Real LLMProvider
-> Structured Assessment
-> deterministic AssessmentValidator

Do NOT generate full application documentation.

==================================================
PROVIDER SELECTION
==================

Implement exactly ONE real provider.

Preferred order:

1. GEMINI
2. OLLAMA
3. OPENAI_COMPATIBLE

Choose the provider that can be integrated with the least repository/environment disruption.

Do not implement multiple real providers in R6.

Document selected provider in result.

If required SDK is not already available:

DO NOT install automatically.

Report:

STATUS=V3-R6_BLOCKED_PROVIDER_DEPENDENCY

and specify required dependency.

If HTTP implementation can safely use existing standard/project dependencies without adding an SDK, that is acceptable.

==================================================
PROVIDER ARCHITECTURE
=====================

Real provider must implement the existing V3-R4 LLMProvider abstraction.

Core documentation code MUST remain unchanged with respect to provider selection.

Allowed conceptual structure:

legacy_documenter/
└── llm/
└── providers/
└── <selected_provider>.py

Adjust to repository conventions.

Provider-specific behavior belongs only inside provider adapter/configuration.

==================================================
NO MODEL-SPECIFIC CORE LOGIC
============================

Forbidden outside provider adapter:

if model == ...
if provider == "gemini"
if provider == "qwen"
if provider == "ollama"

Documentation profiles, prompts and validators must remain provider-neutral.

==================================================
CREDENTIALS
===========

Credentials must come only from safe external configuration.

Allowed examples:

environment variable
credential reference

Never:

hardcode API keys
store key in source
store key in tests
store key in result report
serialize key into LLMRequest
serialize key into LLMResponse
log key

If credential missing:

return/report explicit configuration error.

Do not fabricate credentials.

==================================================
CONFIGURATION
=============

Use existing generic R4 provider configuration.

Provider adapter may interpret:

provider_type
provider_id
model_id
endpoint
credential_source
capabilities
options

Avoid creating competing configuration model.

==================================================
CAPABILITIES
============

Real provider must expose:

context_window
max_output_tokens
structured_output
json_mode
system_instruction
temperature_control

Other R4 capabilities may be populated where known.

Unknown capability:

use null/false according to existing contract.

Do not fabricate unsupported capabilities.

==================================================
STRUCTURED OUTPUT
=================

Pilot must use structured assessment output.

Preferred:

provider-native structured JSON/schema mode

If unavailable:

request JSON output through provider-neutral prompt contract
then validate deterministically.

In either case:

provider response is NOT trusted until AssessmentValidator passes.

Do not silently repair semantic contract violations.

==================================================
REAL PILOT FIXTURE
==================

Use a SMALL synthetic or already-existing controlled ContextPackage fixture.

Do NOT run the full real legacy repository.

Fixture must contain enough evidence for:

* one functional interpretation;
* one technical interpretation;
* at least one CONFIRMED deterministic fact;
* at least one INTERPRETED semantic statement;
* at least one UNRESOLVED item;
* multiple evidence refs;
* source_snapshot;
* provenance.

Keep context small to control token cost.

==================================================
FUNCTIONAL PILOT
================

Run:

ContextPackage
-> FUNCTIONAL_ASSESSMENT profile
-> prompt
-> real provider
-> FunctionalAssessmentResult
-> AssessmentValidator

Validate:

structured response obtained
assessment profile correct
evidence IDs valid
no unknown evidence refs
no evidence-less CONFIRMED claim
INTERPRETED claims remain interpreted
UNRESOLVED preserved
source snapshot valid
traceability valid

==================================================
TECHNICAL PILOT
===============

Run:

ContextPackage
-> TECHNICAL_ASSESSMENT profile
-> prompt
-> real provider
-> TechnicalAssessmentResult
-> AssessmentValidator

Validate:

components/dependencies only from supplied evidence
architecture pattern not forced
supporting evidence referenced
unknown pattern allowed
technical unknowns preserved
no fabricated evidence IDs

==================================================
INSUFFICIENT EVIDENCE PILOT
===========================

Provide deliberately insufficient fixture/context.

Expected acceptable behavior:

PARTIAL

or

NEEDS_MORE_INFORMATION

with structured missing_information.

Not acceptable:

invented business rule
invented architecture
invented dependency
invented database object
invented module ownership

==================================================
MODEL RESPONSE CAPTURE
======================

For test/review artifact, store only sanitized pilot evidence necessary for debugging.

Do NOT store:

credentials
environment secrets
complete raw production repository content

If raw provider response is persisted for pilot debugging:

place under generated/test output location
sanitize it
mark it non-authoritative

Do not add large model dumps to result report.

==================================================
VALIDATION BOUNDARY
===================

Important:

LLMProvider SUCCESS

does NOT imply:

Assessment VALID

Flow:

provider response
|
v
structured parsing
|
v
AssessmentValidator
|
+-> VALID
|
+-> INVALID

Invalid assessment must remain invalid.

Do not auto-promote/rewrite invalid claims.

==================================================
FAILURE CLASSIFICATION
======================

Differentiate at minimum:

PROVIDER_CONFIGURATION_ERROR
PROVIDER_CONNECTION_ERROR
PROVIDER_ERROR
CONTEXT_TOO_LARGE
INVALID_STRUCTURED_OUTPUT
ASSESSMENT_VALIDATION_ERROR

Do not collapse all failures into generic exception.

==================================================
TOKEN / USAGE REPORTING
=======================

Capture provider usage if available.

Otherwise retain estimate.

Report:

input_tokens
output_tokens
total_tokens
estimated flag
token_count_method

Do not invent exact token numbers.

==================================================
RETRY
=====

No uncontrolled retries.

Maximum pilot policy:

1 initial request
optionally 1 retry only for clearly retryable transport/provider failure

No retry for:

invalid semantic assessment
unknown evidence refs
invented claims
schema contract violation unless provider's native response was malformed for transient reason

Avoid hidden token consumption.

==================================================
TEST STRATEGY
=============

Unit tests must NOT depend on external provider/network.

Existing FakeLLMProvider remains unit-test foundation.

Add provider adapter unit tests using mocked transport/client where possible.

Real provider test must be separate/integration/pilot command.

Default:

python -m unittest discover -s tests

must remain offline and deterministic.

==================================================
UNIT TESTS
==========

Add directed tests for selected provider:

1 provider implements LLMProvider
2 config mapping valid
3 credentials not serialized
4 missing credential handled
5 capability mapping
6 request mapping
7 system/user/context separation preserved
8 structured request mapping
9 text response mapping
10 structured response mapping
11 usage mapping
12 provider error mapping
13 timeout mapping where applicable
14 sanitized error
15 no model-specific documentation-core branch

All existing 75 tests remain PASS.

Expected total > 75.

==================================================
REAL PILOT COMMAND
==================

Create an explicit pilot execution mechanism consistent with repository conventions.

It must NOT execute as part of normal unit tests.

Example concept:

python -m legacy_documenter... --pilot

or dedicated test/integration script.

Do not introduce a complex CLI framework if unnecessary.

==================================================
REAL PILOT SAFETY
=================

Before real call validate:

provider configured
credential reference available
fixture only
context budget small
requested output budget bounded

Do not send full V2 artifacts.

Do not send raw legacy source tree.

==================================================
PILOT ACCEPTANCE
================

R6 READY only if:

* one real provider adapter implemented;
* all unit tests PASS;
* full existing regression PASS;
* real provider successfully called;
* functional structured assessment returned and validated;
* technical structured assessment returned and validated;
* insufficient-evidence scenario does not invent unsupported facts;
* traceability survives;
* no credential leakage;
* token/usage information reported.

If adapter implemented but real provider cannot be called due environment/credentials:

STATUS=V3-R6_IMPLEMENTED_NOT_EXECUTED

Do NOT claim successful integration.

If model repeatedly violates structured/evidence contract after reasonable pilot attempts:

STATUS=V3-R6_MODEL_UNSUITABLE_FOR_CONTRACT

Report exact failures.

Do not loosen the evidence policy to make model pass.

==================================================
MODEL QUALITY OBSERVATION
=========================

R6 may report factual pilot observations such as:

structured-output compliance
evidence-reference correctness
invalid claims
missing-information behavior

Do NOT create generalized quality ranking from one pilot.

==================================================
NO PROMPT TUNING LOOP
=====================

Do not repeatedly rewrite prompts to accommodate one model.

R5 contract is authoritative.

Minor serialization/provider adaptation is allowed.

Material semantic prompt changes require separate review.

==================================================
SECURITY
========

Verify:

no credentials committed
no credentials in report
no credentials in response fixture
no environment dump
no arbitrary file reads
no generated command execution
legacy source unchanged

==================================================
REGRESSION
==========

Run:

python -m unittest discover -s tests

All PASS.

Report:

PREVIOUS_TESTS=75
NEW_TOTAL_TESTS
R6_PROVIDER_TESTS
REGRESSION

==================================================
NON_GOALS
=========

Do NOT implement:

second real provider
provider benchmarking
automatic provider selection
fallback provider
full repository interpretation
full levantamiento generation
Markdown rendering
human approval workflow
questionnaire
external information ingestion
Knowledge Readiness
AI_KNOWLEDGE
embeddings
vector DB
V4

==================================================
RESULT
======

Create ONLY:

codex/V3/V3_R6_RESULTADO.md

Machine-oriented.
Compact.

FORMAT:

STATUS
FILES_CHANGED
SELECTED_PROVIDER
PROVIDER_ADAPTER
MODEL_ID
CONFIGURATION
CAPABILITIES
CREDENTIAL_POLICY
UNIT_TESTS
TOTAL_TESTS
REGRESSION
REAL_PILOT_EXECUTED
FUNCTIONAL_PILOT
TECHNICAL_PILOT
INSUFFICIENT_EVIDENCE_PILOT
STRUCTURED_OUTPUT
ASSESSMENT_VALIDATION
TRACEABILITY
USAGE
FAILURES
SECURITY
MODEL_OBSERVATIONS
KNOWN_LIMITATIONS
DECISION
NEXT

Successful expected:

STATUS=V3-R6_READY_FOR_REVIEW
DECISION=REAL_PROVIDER_PILOT_VALIDATED
NEXT=V3-R7_NOT_STARTED

Stop.
