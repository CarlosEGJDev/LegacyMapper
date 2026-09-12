TASK=V3-R5_DOCUMENTATION_PROFILES_PROMPT_CONTRACT

MODE=IMPLEMENT_AND_VALIDATE

NO_REAL_LLM
NO_NETWORK
NO_EXTERNAL_PROVIDER_SDK
NO_LEGACY_SOURCE_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_FINAL_DOCUMENT_GENERATION
NO_HUMAN_APPROVAL_WORKFLOW
NO_AI_KNOWLEDGE
NO_V3_R6_PLUS

OBJECTIVE

Implement the provider-neutral documentation interpretation contract used to transform approved V3 ContextPackages into structured draft assessments.

R5 establishes:

* documentation profiles;
* functional interpretation contract;
* technical interpretation contract;
* prompt specification;
* structured output schemas;
* evidence/claim constraints;
* missing-information output;
* provider-neutral prompt building;
* deterministic FakeLLMProvider validation.

R5 MUST NOT generate final Levantamiento Markdown documents yet.

==================================================
PIPELINE
========

V2 FACTS
|
v
ContextResolver
|
v
ContextComposer
|
v
ContextPackage
|
v
DocumentationProfile
|
v
DocumentationPrompt
|
v
LLMRequest
|
v
LLMProvider
|
v
Structured Interpretation
|
v
Future document generation

R5 ends at:

Structured Interpretation

==================================================
CORE PRINCIPLE
==============

AI interprets evidence.

AI does NOT establish deterministic structural facts.

All generated statements must remain traceable to evidence or explicitly marked as interpretation/unresolved.

Never allow:

AI interpretation -> automatic CONFIRMED fact

==================================================
DOCUMENTATION PROFILES
======================

Implement profiles for:

FUNCTIONAL_ASSESSMENT
TECHNICAL_ASSESSMENT

Profile must define at minimum:

profile_id
profile_version
purpose
required_context_types
preferred_context_types
required_sections
structured_output_schema
claim_policy
missing_information_policy
instructions
metadata

Profiles must remain provider/model neutral.

Do not encode:

Gemini-specific prompts
Qwen-specific prompts
OpenAI-specific prompts
Claude-specific prompts
Copilot-specific prompts

==================================================
FUNCTIONAL ASSESSMENT PROFILE
=============================

Purpose:

produce structured evidence-based interpretation for future:

LEVANTAMIENTO_FUNCIONAL

The structured output must be able to represent:

application/system summary
identified functional areas/modules
functionalities
entry points
UI interactions
functional flows
business operations
data dependencies
cross-module relationships
unresolved functional behavior
missing information
claims
evidence references
interpretation notes

IMPORTANT:

Do NOT assume a module exists solely because:

* folder name exists;
* namespace exists;
* project name exists;
* class name resembles business concept.

A module/functionality may be:

CONFIRMED
INTERPRETED
UNRESOLVED

according to evidence policy.

==================================================
TECHNICAL ASSESSMENT PROFILE
============================

Purpose:

produce structured evidence-based interpretation for future:

LEVANTAMIENTO_TECNICO

Structured output must support:

system technical summary
projects/components
technical responsibilities
dependencies
integration points
data-access behavior
runtime/configuration observations
cross-project relationships
architecture observations
architecture pattern assessments
supporting evidence
contradicting evidence
technical risks/unknowns
missing information
claims
evidence references
interpretation notes

Do NOT hardcode .NET-specific architecture assumptions.

Current V2 evidence may come from legacy .NET, but R5 schemas must remain compatible with future V4 language/framework adapters.

==================================================
ARCHITECTURE PATTERN ASSESSMENT
===============================

Technical interpretation may identify possible patterns.

Allowed result conceptually:

pattern_name
status
confidence_descriptor
supporting_evidence_refs
contradicting_evidence_refs
reasoning_summary

Allowed statuses:

CONFIRMED
INTERPRETED
UNRESOLVED
NO_PATTERN_CONFIRMED
INSUFFICIENT_EVIDENCE

Do not require a pattern.

Do not infer:

MVC
Clean Architecture
N-Tier
DDD
Repository
Service Layer
etc.

without supporting evidence.

==================================================
SOURCE TYPES
============

Preserve V3-R1 source taxonomy:

DETERMINISTIC_CODE_FACT
APPROVED_FUNCTIONAL_DOCUMENT
APPROVED_TECHNICAL_DOCUMENT
APPROVED_EXTERNAL_INFORMATION
AI_INTERPRETATION
UNRESOLVED

R5 current ContextPackages primarily derive from:

DETERMINISTIC_CODE_FACT

Do not fabricate approved documents/external information.

==================================================
CLAIM STATUS
============

Canonical:

CONFIRMED
INTERPRETED
UNRESOLVED

Policy:

CONFIRMED
requires authoritative deterministic or approved source evidence.

INTERPRETED
requires evidence but includes AI-derived semantic interpretation.

UNRESOLVED
used when evidence is incomplete/ambiguous/contradictory.

AI-generated semantic conclusions should normally be INTERPRETED unless deterministic evidence directly establishes the statement.

==================================================
CLAIM MODEL
===========

Reuse/extend V3-R1 DocumentClaim contract where compatible.

Every claim must retain:

claim_id
statement
status
source_type
evidence_refs
context_package_id
source_snapshot
metadata

Optional:

interpretation_basis
uncertainty_reason

One claim may reference multiple evidence items.

No evidence-less CONFIRMED claim.

==================================================
EVIDENCE POLICY
===============

Prompt must explicitly instruct AI:

* use only provided ContextPackage evidence;
* do not invent code relationships;
* do not invent business rules;
* do not invent module ownership;
* do not invent database objects;
* do not invent external systems;
* do not assume unresolved targets;
* preserve ambiguity;
* distinguish fact from interpretation;
* explicitly report insufficient evidence.

Every nontrivial conclusion must reference evidence IDs.

==================================================
MISSING INFORMATION
===================

R5 must support structured missing-information output.

Use existing V3-R1 MissingInformation contract where possible.

At minimum:

missing_information_id
topic
description
reason
impact
related_claim_refs
related_evidence_refs
priority
suggested_information_needed

Do NOT generate user-facing questionnaire yet.

R5 only produces structured missing-information records.

==================================================
PROMPT CONTRACT
===============

Implement provider-neutral prompt representation.

Do NOT create one huge unstructured string as the primary internal contract.

Conceptually:

DocumentationPrompt

profile
system_instruction
task_instruction
evidence_policy
claim_policy
output_contract
context
metadata

Serialization into LLMRequest may produce text as needed, but semantic pieces must remain separately testable.

==================================================
SYSTEM INSTRUCTION
==================

Create stable provider-neutral system instruction.

Must establish:

You are an evidence-grounded software-system analyst.

Use only supplied evidence.

Never promote interpretation into deterministic fact.

When evidence is insufficient:
mark unresolved or request missing information.

All claims require traceable evidence according to claim policy.

Do not infer unsupported architecture/business behavior.

Output only the requested structured format.

Exact wording may be improved but semantics must remain stable.

==================================================
FUNCTIONAL TASK INSTRUCTION
===========================

Functional profile instruction must ask AI to:

identify evidence-supported functional areas;
describe supported functionalities;
connect entry points to functional flows;
identify business/data interactions where supported;
preserve unresolved relationships;
identify missing functional information;
produce structured claims with evidence.

Do NOT ask AI to invent friendly module names without evidence.

If useful human-readable labels are interpreted:
status must remain INTERPRETED.

==================================================
TECHNICAL TASK INSTRUCTION
==========================

Technical profile must ask AI to:

describe system/components from evidence;
interpret responsibilities cautiously;
identify dependency/integration relationships;
describe data-access observations;
evaluate possible architectural patterns;
retain contradictory evidence;
report technical unknowns;
produce evidence-grounded structured claims.

No architecture pattern is mandatory.

==================================================
CONTEXT SELECTION
=================

Profiles declare desired ContextPackage categories.

FUNCTIONAL preferred context:

SYSTEM
FUNCTIONAL
FLOW
ENTITY
DATA_ACCESS where relevant

TECHNICAL preferred context:

SYSTEM
TECHNICAL
ENTITY
FLOW
DATA_ACCESS

R5 MUST NOT query raw repository directly.

R5 MUST NOT load V2 giant artifacts bypassing ContextResolver/Composer.

Input is ContextPackage.

==================================================
CONTEXT COMPLETENESS
====================

Prompt must expose package completeness:

COMPLETE
TRUNCATED
BUDGET_INSUFFICIENT

If TRUNCATED or BUDGET_INSUFFICIENT:

AI must not assume absent evidence means absence in application.

Structured output should preserve context limitation.

==================================================
UNRESOLVED EVIDENCE
===================

Unresolved evidence must be visible to interpretation.

Prompt must explicitly state:

unresolved references are evidence of uncertainty,
not permission to infer target relationships.

==================================================
STRUCTURED OUTPUT
=================

Implement provider-neutral schemas for:

FunctionalAssessmentResult
TechnicalAssessmentResult

Both must include at minimum:

assessment_id
profile_id
profile_version
context_package_ids
source_snapshots
status
summary
claims
missing_information
warnings
metadata

Functional-specific fields:
functional_areas
functionalities
entry_points
flows
data_dependencies

Technical-specific fields:
components
dependencies
integrations
data_access
architecture_patterns
technical_unknowns

Use existing contracts where possible.

Avoid duplicate competing schemas.

==================================================
ASSESSMENT STATUS
=================

Suggested canonical result status:

GENERATED
PARTIAL
NEEDS_MORE_INFORMATION
INVALID

Meaning:

GENERATED
sufficient structured result produced.

PARTIAL
valid result but significant context truncation/unresolved evidence remains.

NEEDS_MORE_INFORMATION
required interpretation cannot responsibly proceed.

INVALID
structured response violates contract.

Do not map GENERATED to human APPROVED.

==================================================
FAKE PROVIDER VALIDATION
========================

Use FakeLLMProvider only.

Create deterministic fixtures demonstrating:

1 functional valid structured result
2 technical valid structured result
3 unresolved result
4 missing-information result
5 invalid claim without evidence
6 invalid CONFIRMED AI-only claim
7 invalid structured response
8 truncated-context interpretation
9 budget-insufficient interpretation

Fake responses must contain no actual AI reasoning.

They are validation fixtures only.

==================================================
POST-RESPONSE VALIDATION
========================

Do NOT trust provider structured output solely because JSON/schema is valid.

Implement deterministic assessment validator.

Validate at minimum:

profile matches request
context_package_ids known
source_snapshots known
claim IDs unique
claim evidence refs exist in supplied package(s)
CONFIRMED claim has authoritative evidence
AI_INTERPRETATION cannot independently justify CONFIRMED
UNRESOLVED remains unresolved
missing-info refs valid
no unknown fabricated evidence IDs

Invalid references:
assessment INVALID.

Do not silently drop invalid claims.

==================================================
CROSS-CONTEXT TRACEABILITY
==========================

If assessment consumes multiple ContextPackages:

all package IDs must be listed.

Each claim must reference evidence resolvable to at least one consumed package.

Trace:

Assessment
-> Claim
-> evidence_ref
-> ContextPackage
-> upstream V2 ref
-> source_snapshot

==================================================
DETERMINISTIC IDENTITY
======================

Use canonical deterministic IDs where appropriate:

DocumentationProfile ID/version stable.

Prompt semantic identity stable.

Assessment IDs for deterministic Fake responses stable.

No Python hash().
No random UUID.
No current timestamp in semantic hash.

==================================================
PROMPT VERSIONING
=================

Prompt contract must be versioned.

At minimum:

profile_version
prompt_contract_version

Future prompt changes must be identifiable for reproducibility.

Do not embed model name into prompt version.

==================================================
PROVIDER INDEPENDENCE
=====================

Same DocumentationPrompt must be consumable by any compatible LLMProvider.

No core branches such as:

if provider == GEMINI
if model == QWEN
if provider == OPENAI

Provider serialization differences belong to provider adapters.

==================================================
TOKEN/BUDGET AWARENESS
======================

R5 consumes existing R3 metrics.

Expose:

estimated_tokens
budget_profile
completeness

Do NOT implement a tokenizer.

Do NOT dynamically recompose context inside prompt builder.

If request exceeds selected provider capability:
R4 handles capability validation.

==================================================
SECURITY
========

Prompt builder must not:

rehydrate sanitized configuration values;
include credentials;
load environment secrets;
read arbitrary repository files;
follow paths from model output;
execute model-generated commands.

Fake provider no network.

==================================================
FILES / STRUCTURE
=================

Preferred conceptual structure:

legacy_documenter/
├── documentation/
│   ├── profiles.py
│   ├── prompts.py
│   ├── assessment_models.py
│   └── assessment_validator.py
└── llm/
└── existing R4 abstraction

Adjust to existing repository conventions.

Do not create unnecessary tiny modules if current project favors consolidation.

==================================================
TESTS
=====

Add dedicated R5 tests.

Minimum coverage:

PROFILES

1 functional profile exists
2 technical profile exists
3 profile IDs deterministic
4 profile versions present
5 profiles provider neutral
6 functional required/preferred contexts valid
7 technical required/preferred contexts valid

PROMPT CONTRACT

8 prompt system/task/context separated
9 prompt contract versioned
10 deterministic prompt identity
11 functional prompt generated
12 technical prompt generated
13 evidence policy included
14 claim policy included
15 missing-information policy included
16 completeness exposed
17 unresolved evidence exposed

FUNCTIONAL RESULT

18 valid FunctionalAssessmentResult
19 functional areas support evidence refs
20 functionalities support evidence refs
21 flow refs preserved
22 data dependency refs preserved
23 interpreted functional labels not CONFIRMED automatically

TECHNICAL RESULT

24 valid TechnicalAssessmentResult
25 component refs preserved
26 dependency refs preserved
27 data access refs preserved
28 architecture pattern supports evidence
29 contradictory evidence retained
30 NO_PATTERN_CONFIRMED valid
31 INSUFFICIENT_EVIDENCE valid

CLAIMS

32 confirmed deterministic claim valid
33 interpreted claim valid
34 unresolved claim valid
35 evidence-less confirmed claim rejected
36 AI-only confirmed claim rejected
37 unknown evidence ref rejected
38 duplicate claim ID rejected
39 source snapshot mismatch rejected
40 context package mismatch rejected

MISSING INFORMATION

41 valid missing information
42 missing info evidence refs validated
43 invalid refs rejected
44 insufficient evidence can yield NEEDS_MORE_INFORMATION

CONTEXT LIMITATION

45 COMPLETE handled
46 TRUNCATED preserved
47 BUDGET_INSUFFICIENT preserved
48 absence under truncation not treated as system absence

FAKE PROVIDER

49 functional fake structured response
50 technical fake structured response
51 invalid structured fake response rejected
52 deterministic fake assessment result

TRACEABILITY

53 Assessment -> Claim
54 Claim -> evidence
55 evidence -> ContextPackage
56 ContextPackage -> source_snapshot
57 multi-package assessment traceability

SECURITY / ISOLATION

58 no credential leakage
59 no network
60 no real LLM
61 no repository scan
62 no source modification

REGRESSION

63 V1/V2 tests pass
64 V3-R1 tests pass
65 V3-R2/R3 tests pass
66 V3-R4 tests pass

Run:

python -m unittest discover -s tests

All PASS.

Expected total > 71.

==================================================
VALIDATION SCENARIOS
====================

SCENARIO A — FUNCTIONAL

ContextPackage fixture
-> functional DocumentationProfile
-> DocumentationPrompt
-> LLMRequest
-> FakeLLMProvider
-> FunctionalAssessmentResult
-> assessment validation
-> PASS

SCENARIO B — TECHNICAL

ContextPackage fixture
-> technical DocumentationProfile
-> DocumentationPrompt
-> LLMRequest
-> FakeLLMProvider
-> TechnicalAssessmentResult
-> assessment validation
-> PASS

SCENARIO C — INSUFFICIENT EVIDENCE

Limited/unresolved ContextPackage
-> Fake response
-> NEEDS_MORE_INFORMATION
-> structured missing information
-> no invented claim

SCENARIO D — INVALID AI CLAIM

Fake provider returns:

CONFIRMED
source_type=AI_INTERPRETATION
without authoritative evidence

Expected:
INVALID

==================================================
NON_GOALS
=========

Do NOT implement:

real Gemini calls
real Copilot calls
Ollama calls
OpenAI calls
Claude calls
real API credentials
automatic retries
final Markdown document rendering
LEVANTAMIENTO_FUNCIONAL.md
LEVANTAMIENTO_TECNICO.md
human approval state machine
user questionnaire
external information ingestion
Knowledge Readiness
AI_KNOWLEDGE
semantic search
embeddings
vector DB
V4

==================================================
COMPATIBILITY
=============

Do not break:

V3-R1 contracts
V3-R2 ContextResolver
V3-R3 ContextComposer
V3-R4 LLMProvider

All existing 71 tests must remain passing.

==================================================
REPORT
======

Create ONLY:

codex/V3/V3_R5_RESULTADO.md

Machine-oriented.
Compact.

FORMAT:

STATUS
FILES_CHANGED
DOCUMENTATION_PROFILES
FUNCTIONAL_PROFILE
TECHNICAL_PROFILE
PROMPT_CONTRACT
PROMPT_VERSION
ASSESSMENT_MODELS
FUNCTIONAL_ASSESSMENT
TECHNICAL_ASSESSMENT
ARCHITECTURE_PATTERN_POLICY
CLAIM_POLICY
EVIDENCE_POLICY
MISSING_INFORMATION
CONTEXT_LIMITATION_POLICY
ASSESSMENT_VALIDATOR
FAKE_PROVIDER_VALIDATION
TRACEABILITY
DETERMINISM
SECURITY
PROVIDER_INDEPENDENCE
R5_TESTS
TOTAL_TESTS
REGRESSION
KNOWN_LIMITATIONS
DECISION
NEXT

Successful expected:

STATUS=V3-R5_READY_FOR_REVIEW
DECISION=DOCUMENTATION_INTERPRETATION_CONTRACT_READY
NEXT=V3-R6_NOT_STARTED

Stop.