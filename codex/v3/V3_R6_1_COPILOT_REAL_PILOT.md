TASK=V3-R6_1_COPILOT_REAL_PILOT

MODE=IMPLEMENT_AND_EXECUTE_PILOT

ALLOW_REAL_COPILOT_CALLS
NO_GEMINI_REQUIRED
NO_GEMINI_API_KEY
NO_SECOND_REAL_PROVIDER
NO_FULL_LEGACY_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_FINAL_DOCUMENT_GENERATION
NO_V3_R7

OBJECTIVE

Replace the blocked Gemini pilot path with a GitHub Copilot SDK pilot using the locally authenticated GitHub/Copilot user.

Current baseline:

* V3-R6 GeminiProvider exists.
* 78 tests PASS.
* Gemini pilot was blocked only by missing GEMINI_API_KEY.
* Do NOT remove GeminiProvider.
* Add Copilot as an additional provider adapter for pilot validation.

Target:

ContextPackage
-> DocumentationProfile
-> DocumentationPrompt
-> LLMRequest
-> CopilotProvider
-> GitHub Copilot SDK
-> Structured Assessment
-> AssessmentValidator

==================================================
AUTHENTICATION
==============

Preferred authentication:

locally signed-in GitHub/Copilot user.

Do NOT require:

GEMINI_API_KEY
OPENAI_API_KEY
ANTHROPIC_API_KEY
manual token in source code

Use GitHub Copilot SDK authentication discovery.

Preferred behavior:

CopilotClient()
-> stored local GitHub/Copilot credentials

Do not print, serialize or persist credentials.

If local Copilot authentication is unavailable:

STATUS=V3-R6_1_BLOCKED_COPILOT_AUTH

Report only the missing authentication condition.

Do not request or expose the user's token.

==================================================
SDK / RUNTIME PRECONDITION
==========================

Check whether GitHub Copilot SDK is already available in the active Python environment.

Do NOT install packages automatically.

If SDK missing:

STATUS=V3-R6_1_BLOCKED_DEPENDENCY
REQUIRED_DEPENDENCY=GitHub Copilot SDK for Python

Stop.

If Python Copilot runtime is missing and SDK requires:

python -m copilot download-runtime

Do NOT execute download automatically unless current Codex authorization explicitly permits dependency/runtime download.

Instead report:

STATUS=V3-R6_1_BLOCKED_RUNTIME
REQUIRED_ACTION=python -m copilot download-runtime

Stop.

==================================================
PROVIDER
========

Implement:

CopilotProvider

behind existing V3-R4:

LLMProvider

Do not modify documentation core based on Copilot.

Preferred conceptual location:

legacy_documenter/llm/providers/copilot.py

Register provider through existing registry/factory.

Do not remove or rewrite GeminiProvider.

==================================================
PROVIDER CONFIG
===============

Reuse existing ProviderConfig.

Provider type:

COPILOT

If provider enum/type currently cannot represent it, add COPILOT using the smallest compatible change.

Configuration supports:

provider_id
model_id
capabilities
options

Do not add credential values.

==================================================
MODEL
=====

Do NOT hardcode a commercial model catalog.

Use a model ID available to the locally authenticated Copilot account.

If Copilot SDK provides model discovery/capability inspection, use it.

If not, accept model_id through pilot configuration.

If configured model is unavailable:

report explicit MODEL_UNAVAILABLE.

Do not silently substitute another model unless the SDK itself performs documented default selection.

Record the actual selected model in the result.

==================================================
COPILOT SESSION
===============

Create an ephemeral pilot session.

No persistent production conversation required.

Do not allow:

filesystem modifications
shell execution
tool execution
repository edits

through model-generated actions.

LegacyMapper needs text/structured interpretation only.

If SDK exposes permission/tool handlers:

deny unnecessary tool execution.

Do not use approve-all permissions.

==================================================
PROMPT BOUNDARY
===============

Preserve R5 semantic separation:

system_instruction
task_instruction
evidence_policy
claim_policy
context

Copilot serialization may combine fields as required by SDK transport, but core objects remain separate.

Do not rewrite R5 prompt semantics specifically for Copilot.

==================================================
STRUCTURED OUTPUT
=================

Use existing R5 assessment contracts.

Preferred result:

structured JSON matching requested assessment schema.

If Copilot SDK does not provide native schema mode:

request strict JSON using existing provider-neutral R5 output contract.

Then:

parse
-> validate schema
-> AssessmentValidator

Do not silently repair invalid claims or evidence references.

==================================================
PILOT FIXTURE
=============

Use SMALL controlled fixture only.

Do not scan real legacy repository.

Fixture must include:

one deterministic confirmed fact
one interpretation-capable relationship
one unresolved relationship
multiple evidence refs
context_package_id
source_snapshot
provenance

Keep token usage small.

==================================================
FUNCTIONAL PILOT
================

Execute ONE real Copilot call.

Flow:

fixture ContextPackage
-> FUNCTIONAL_ASSESSMENT
-> DocumentationPrompt
-> LLMRequest
-> CopilotProvider
-> structured response
-> FunctionalAssessmentResult
-> AssessmentValidator

PASS requires:

provider response received
structured response valid
known evidence refs only
no evidence-less CONFIRMED claim
AI semantic claims remain INTERPRETED
UNRESOLVED preserved
traceability valid

==================================================
TECHNICAL PILOT
===============

Execute ONE real Copilot call.

PASS requires:

TechnicalAssessmentResult valid
component/dependency statements grounded
architecture pattern not mandatory
unknown/insufficient pattern accepted
supporting evidence valid
no fabricated evidence IDs
traceability valid

==================================================
INSUFFICIENT EVIDENCE PILOT
===========================

Execute ONE deliberately insufficient-context call.

Expected:

PARTIAL

or

NEEDS_MORE_INFORMATION

with structured MissingInformation when appropriate.

FAIL if model invents unsupported:

business rules
architecture
dependencies
DB objects
module ownership
external systems

==================================================
CALL LIMIT
==========

Maximum real calls:

3 primary calls.

Optional retry:

maximum 1 retry per pilot only for retryable SDK/transport failure.

No retries for semantic validation failure.

Do not consume Copilot quota repeatedly trying to force compliance.

==================================================
ASSESSMENT VALIDATION
=====================

Provider success != assessment success.

Existing AssessmentValidator remains authoritative.

Do not weaken:

evidence closure
CONFIRMED authority
source snapshot validation
context package validation
claim status policy

If model violates contract:

report failure.

==================================================
USAGE
=====

Capture usage/token metadata if Copilot SDK exposes it.

If unavailable:

use existing estimate
estimated=true

Never fabricate exact usage.

==================================================
UNIT TESTS
==========

Normal test suite must remain fully offline.

Mock/inject Copilot client/session transport for unit tests.

Add tests for:

1 CopilotProvider implements LLMProvider
2 registry resolves COPILOT
3 local-auth configuration requires no secret field
4 request mapping
5 system/task/context preserved
6 session/model mapping
7 text response mapping
8 structured response mapping
9 invalid structured response
10 SDK/provider error mapping
11 model unavailable mapping
12 usage mapping when supplied
13 missing usage accepted
14 credentials never serialized
15 tool/permission execution disabled
16 no Copilot-specific branch in documentation core

All existing 78 tests must PASS.

Expected total > 78.

==================================================
REAL PILOT EXECUTION
====================

Real Copilot calls MUST NOT run in:

python -m unittest discover -s tests

Provide separate explicit pilot execution.

Use repository conventions.

Pilot must verify before calling:

SDK available
runtime available
local auth available
model available/configured
fixture small
output bound configured

==================================================
SECURITY
========

Mandatory:

no tokens written
no credentials logged
no keychain content exposed
no environment dump
no raw auth response stored
no repository scan
no source modification
no model tool execution
no shell execution from model
no filesystem writes from model

==================================================
GEMINI PROVIDER
===============

Keep existing GeminiProvider intact.

Do NOT attempt Gemini pilot.

Do NOT require GEMINI_API_KEY.

R6.1 validates Copilot only.

==================================================
ACCEPTANCE
==========

READY only if:

* CopilotProvider implemented;
* offline tests PASS;
* full regression PASS;
* locally authenticated Copilot call succeeds;
* functional pilot validates;
* technical pilot validates;
* insufficient-evidence pilot validates;
* traceability preserved;
* no credential leakage.

Successful:

STATUS=V3-R6_1_READY_FOR_REVIEW
DECISION=REAL_COPILOT_PROVIDER_PILOT_VALIDATED
NEXT=V3-R7_NOT_STARTED

If SDK missing:

STATUS=V3-R6_1_BLOCKED_DEPENDENCY

If runtime missing:

STATUS=V3-R6_1_BLOCKED_RUNTIME

If local authentication missing:

STATUS=V3-R6_1_BLOCKED_COPILOT_AUTH

If Free plan/quota/model access prevents calls:

STATUS=V3-R6_1_BLOCKED_COPILOT_ACCESS

If responses execute but violate R5 evidence contract:

STATUS=V3-R6_1_MODEL_CONTRACT_FAILURE

Do NOT weaken R5 to make pilot pass.

==================================================
REGRESSION
==========

Run:

python -m unittest discover -s tests

Expected baseline:

78 existing tests PASS

* new Copilot provider tests

==================================================
REPORT
======

Create ONLY:

codex/V3/V3_R6_1_RESULTADO.md

FORMAT:

STATUS
FILES_CHANGED
SELECTED_PROVIDER
COPILOT_SDK
COPILOT_RUNTIME
LOCAL_AUTH
PLAN_ACCESS
MODEL_ID
PROVIDER_ADAPTER
UNIT_TESTS
TOTAL_TESTS
REGRESSION
REAL_CALLS_EXECUTED
FUNCTIONAL_PILOT
TECHNICAL_PILOT
INSUFFICIENT_EVIDENCE_PILOT
STRUCTURED_OUTPUT
ASSESSMENT_VALIDATION
TRACEABILITY
USAGE
TOOL_EXECUTION
SECURITY
MODEL_OBSERVATIONS
FAILURES
KNOWN_LIMITATIONS
DECISION
NEXT

Stop.