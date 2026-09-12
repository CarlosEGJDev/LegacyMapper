TASK=V3-R4_LLM_PROVIDER_ABSTRACTION

MODE=IMPLEMENT_AND_VALIDATE

NO_REAL_LLM
NO_NETWORK
NO_EXTERNAL_PROVIDER_SDK
NO_LEGACY_SOURCE_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_DOCUMENTATION_GENERATION
NO_V3_R5_PLUS

OBJECTIVE

Implement a provider-neutral LLM abstraction for future LegacyMapper AI interpretation.

R4 establishes:

* provider contract;
* request/response models;
* capability model;
* model metadata;
* structured-output contract;
* error model;
* usage metadata;
* deterministic FakeLLMProvider;
* compatibility with V3 ContextPackage.

R4 MUST NOT call Gemini, Copilot, Qwen, Claude, OpenAI or any external model.

==================================================
ARCHITECTURE
============

V2 deterministic facts
|
v
V3 ContextResolver
|
v
V3 ContextComposer
|
v
ContextPackage
|
v
LLMRequest
|
v
LLMProvider
|
+-> FakeLLMProvider [R4]
|
+-> real providers [future]
|
v
LLMResponse

CORE PRINCIPLE

LegacyMapper core depends on LLMProvider.

LegacyMapper core MUST NOT depend on:

* model names;
* provider SDKs;
* HTTP APIs;
* Ollama;
* Gemini;
* OpenAI;
* Anthropic;
* Copilot.

==================================================
PROVIDER CONTRACT
=================

Define abstract provider contract.

Conceptually:

LLMProvider

generate(request) -> LLMResponse

structured_generate(
request,
output_schema
) -> StructuredLLMResponse

capabilities() -> LLMCapabilities

model_info() -> LLMModelInfo

Exact Python API may follow repository conventions.

Provider implementations must be replaceable without changing ContextResolver, ContextComposer or future documentation logic.

==================================================
REQUEST MODEL
=============

Define LLMRequest.

Support at minimum:

request_id
purpose
system_instruction
user_instruction
context
context_package_id
context_schema_version
source_snapshot
temperature
max_output_tokens
structured_output
metadata

request_id must support deterministic identity where appropriate.

Do not include provider/model in semantic request content unless explicitly required by execution metadata.

==================================================
PURPOSE
=======

Define machine-readable purpose.

At minimum prepare:

FUNCTIONAL_DOCUMENTATION
TECHNICAL_DOCUMENTATION
ARCHITECTURE_INTERPRETATION
FUNCTIONAL_INTERPRETATION
MISSING_INFORMATION_ANALYSIS
KNOWLEDGE_GENERATION
TEST

R4 does not execute these real workflows.

Purpose is routing/metadata only.

==================================================
CONTEXT INPUT
=============

LLMRequest must accept composed V3 context.

Preserve:

context_package_id
budget_profile
estimated_tokens
completeness
provenance
traceability
source_snapshot

Do not copy full V2 artifacts into request.

Do not bypass ContextComposer.

Future documentation generation should consume approved ContextPackages, not arbitrary repository source dumps.

==================================================
CAPABILITIES
============

Define LLMCapabilities.

At minimum:

context_window
max_output_tokens
structured_output
json_mode
streaming
tool_use
reasoning
system_instruction
temperature_control

Use booleans/nullable numeric capabilities as appropriate.

Capabilities describe runtime/provider ability.

They are NOT model quality scores.

Do not encode assumptions such as:

Gemini is better at X
Qwen is worse at Y
Claude should be used for Z

==================================================
MODEL INFO
==========

Define LLMModelInfo.

At minimum:

provider_id
model_id
display_name
provider_type
capabilities
metadata

Do not hardcode known commercial model catalogs.

Configuration supplies model IDs later.

==================================================
PROVIDER TYPES
==============

Prepare extensible provider identifiers/types.

Examples future-compatible:

FAKE
OLLAMA
OPENAI
ANTHROPIC
GEMINI
AZURE_OPENAI
OPENAI_COMPATIBLE
CUSTOM

Do not implement real providers in R4.

Do not require every future provider to fit a fixed commercial list.

==================================================
STRUCTURED OUTPUT
=================

Future LegacyMapper documentation should prefer structured AI responses before Markdown rendering.

R4 must therefore support:

structured_generate(request, output_schema)

Output schema may be:

* Pydantic model;
* JSON Schema;
* existing project-compatible schema abstraction.

Avoid adding unnecessary dependencies.

Structured response must distinguish:

RAW_TEXT
VALID_STRUCTURED_OUTPUT
INVALID_STRUCTURED_OUTPUT

Do not silently repair invalid structured output in R4.

==================================================
RESPONSE MODEL
==============

Define LLMResponse.

At minimum:

request_id
response_id
provider_id
model_id
status
content
finish_reason
usage
warnings
metadata

Structured response additionally supports:

parsed_output
schema_validation_status
validation_errors

==================================================
RESPONSE STATUS
===============

Canonical statuses:

SUCCESS
INVALID_REQUEST
CONTEXT_TOO_LARGE
UNSUPPORTED_CAPABILITY
INVALID_STRUCTURED_OUTPUT
PROVIDER_ERROR
TIMEOUT
RATE_LIMITED
CANCELLED

Fake provider need only exercise applicable states.

==================================================
USAGE MODEL
===========

Define provider-neutral usage metadata:

input_tokens
output_tokens
total_tokens
token_count_method
estimated
latency_ms

Values may be null when provider does not supply them.

Do not fabricate exact token counts.

If ContextComposer estimate is used:

estimated=true

and retain estimation method.

==================================================
CAPABILITY VALIDATION
=====================

Before provider execution, validate request against capabilities.

Examples:

requested structured output but unsupported
-> UNSUPPORTED_CAPABILITY

context estimated above context_window
-> CONTEXT_TOO_LARGE

requested max_output_tokens above provider capability
-> INVALID_REQUEST or explicit compatible status

requested temperature when provider does not support control
-> explicit policy; do not silently pretend support

==================================================
CONTEXT WINDOW
==============

ContextComposer budget and provider context window are separate concepts.

R3:
creates a package under a selected budget.

R4:
checks whether package/request fits selected provider capability.

Do not make R3 model-specific.

Future flow:

Provider capabilities
|
v
Budget selection
|
v
ContextComposer
|
v
LLMRequest

R4 only prepares the compatibility contract.

==================================================
FAKE LLM PROVIDER
=================

Implement deterministic FakeLLMProvider.

Purpose:

test complete provider abstraction without:

* internet;
* credentials;
* SDK;
* real AI;
* nondeterminism.

Fake provider must support configurable:

provider_id
model_id
capabilities
fixed responses
structured responses
forced error/status

Given same configuration + request:
same response.

No randomness.

==================================================
FAKE STRUCTURED OUTPUT
======================

Fake provider must demonstrate:

valid structured response
invalid structured response
schema validation success
schema validation failure

Do not simulate AI reasoning.

Use deterministic fixtures.

==================================================
ERROR MODEL
===========

Define structured provider error.

At minimum:

error_code
message
provider_id
model_id
retryable
details

Do not expose credentials/secrets in errors.

Do not require exception parsing by future core logic.

==================================================
RETRY POLICY
============

Do NOT implement automatic retries yet.

Only define whether error is retryable.

Future provider/runtime layer may implement retry/backoff.

Reason:
automatic retries can create unexpected cost/token consumption.

==================================================
CONFIGURATION CONTRACT
======================

Prepare generic provider configuration.

At minimum:

provider_type
provider_id
model_id
endpoint
context_window
max_output_tokens
capabilities
options

Credentials MUST NOT be stored directly in normal configuration artifacts.

Support future credential references/environment configuration.

Example concept:

credential_source=ENVIRONMENT

Do not define actual secrets.

==================================================
PROVIDER REGISTRY
=================

Implement lightweight provider registry/factory if consistent with architecture.

Goal:

provider_type/config
|
v
registered provider implementation

R4 registry only needs FAKE provider.

Unknown provider:
explicit error.

Do not add external plugin framework.

==================================================
PROMPT BOUNDARY
===============

R4 must NOT implement final prompts.

But define request boundary:

system_instruction
user_instruction
context

These must remain separate.

Do not concatenate everything prematurely into one uncontrolled string.

This prepares future provider-specific serialization while keeping prompt semantics provider-neutral.

==================================================
TRACEABILITY
============

Every request/response must preserve:

context_package_id
source_snapshot

Future generated claim must be traceable:

AI claim
-> LLMResponse
-> LLMRequest
-> ContextPackage
-> V2 reference
-> source snapshot

R4 need only establish request/response side of this chain.

==================================================
DETERMINISTIC IDENTITY
======================

Stable semantic identity where applicable.

No:

* random UUID
* Python hash()
* current timestamp in semantic identity

request_id may derive from canonical:

purpose
context_package_id
instructions
structured-output schema identity
generation parameters

response_id for Fake provider may derive from:

request_id
provider_id
model_id
configured fake response

Real provider response IDs may later preserve provider-issued IDs.

==================================================
SECURITY
========

Never serialize credentials into:

LLMRequest
LLMResponse
errors
logs
test snapshots
provider metadata

Configuration may reference credential source but not credential value.

Fake provider must require no credential.

No network.

==================================================
PROVIDER INDEPENDENCE
=====================

Add explicit tests demonstrating that core request/response behavior does not require knowledge of a specific provider/model.

No:

if model == ...
if provider == "gemini" inside core interpretation logic
if provider == "qwen" ...
if provider == "copilot" ...

Provider-specific behavior belongs inside provider implementations later.

==================================================
FUTURE COPILOT NOTE
===================

Do NOT assume GitHub Copilot exposes a general-purpose API suitable for LegacyMapper.

Treat future Copilot integration as capability-dependent.

If later no supported API/provider interface is available, LegacyMapper must work unchanged with other providers.

No Copilot implementation in R4.

==================================================
FUTURE PROVIDER TARGETS
=======================

Architecture should permit later adapters such as:

OllamaProvider
GeminiProvider
OpenAIProvider
AnthropicProvider
AzureOpenAIProvider
OpenAICompatibleProvider

Do not implement them now.

==================================================
IMPLEMENTATION
==============

Preferred conceptual structure:

legacy_documenter/
└── llm/
├── models.py
├── provider.py
├── registry.py
└── fake_provider.py

Adjust to repository conventions if needed.

Keep provider-independent models separate from Fake provider.

==================================================
V3-R1/R2/R3 COMPATIBILITY
=========================

Do not modify approved contracts unnecessarily.

Must remain compatible with:

V3-R1 Documentation Contract
V3-R2 ContextResolver
V3-R3 ContextComposer

ContextPackage should be consumable without transformation that destroys provenance.

All existing 67 tests must remain passing.

==================================================
TESTS
=====

Add dedicated R4 tests.

Minimum:

1 LLMRequest valid
2 deterministic request ID
3 request preserves context_package_id
4 request preserves source_snapshot
5 request preserves purpose
6 system/user/context separated
7 LLMCapabilities valid
8 LLMModelInfo valid
9 generic provider config valid
10 credentials absent from serialized config/request

11 FakeLLMProvider registered
12 unknown provider rejected
13 Fake provider generate SUCCESS
14 deterministic fake response
15 deterministic fake response ID
16 provider/model metadata retained

17 structured_generate valid
18 structured output parsed
19 schema validation success
20 invalid structured output detected
21 schema validation errors retained
22 invalid structured output not silently repaired

23 unsupported structured output capability rejected
24 context too large rejected
25 max output tokens validation
26 unsupported temperature control handled explicitly

27 usage metadata exact/estimated distinction
28 null usage accepted
29 estimated context usage preserved

30 provider error structured
31 retryable flag preserved
32 provider error contains no credentials
33 forced Fake error deterministic

34 context package provenance retained
35 request/response traceability retained
36 source snapshot retained end-to-end

37 provider/model names do not alter core schema
38 arbitrary CUSTOM provider type/config representable
39 no commercial model catalog required
40 no model-specific core branch

41 no network
42 no external SDK required
43 no real LLM
44 no legacy repository scan
45 V1/V2 regression
46 V3-R1 regression
47 V3-R2/R3 regression

Run:

python -m unittest discover -s tests

All PASS.

Expected total > 67.

==================================================
VALIDATION
==========

Fixtures only.

Demonstrate:

ContextPackage fixture
-> LLMRequest
-> FakeLLMProvider
-> LLMResponse

and:

ContextPackage fixture
-> structured request
-> FakeLLMProvider
-> schema validation

Repeat execution and verify deterministic Fake results.

No real model.

==================================================
NON_GOALS
=========

Do NOT implement:

GeminiProvider
Copilot integration
OllamaProvider
OpenAIProvider
AnthropicProvider
Azure provider
HTTP calls
SDK installs
real credentials
real model tests
documentation prompts
AI interpretation
LEVANTAMIENTO_FUNCIONAL generation
LEVANTAMIENTO_TECNICO generation
human approval
Knowledge Readiness
AI_KNOWLEDGE
semantic search
vector DB
V4

==================================================
REPORT
======

Create ONLY:

codex/V3/V3_R4_RESULTADO.md

Machine-oriented.
Compact.

FORMAT:

STATUS
FILES_CHANGED
LLM_CONTRACT
REQUEST_MODEL
RESPONSE_MODEL
CAPABILITIES
MODEL_INFO
PROVIDER_CONFIG
PROVIDER_REGISTRY
FAKE_PROVIDER
STRUCTURED_OUTPUT
CAPABILITY_VALIDATION
USAGE
ERROR_MODEL
TRACEABILITY
DETERMINISM
SECURITY
PROVIDER_INDEPENDENCE
R4_TESTS
TOTAL_TESTS
REGRESSION
KNOWN_LIMITATIONS
DECISION
NEXT

Successful expected:

STATUS=V3-R4_READY_FOR_REVIEW
DECISION=LLM_PROVIDER_ABSTRACTION_READY
NEXT=V3-R5_NOT_STARTED

Stop.