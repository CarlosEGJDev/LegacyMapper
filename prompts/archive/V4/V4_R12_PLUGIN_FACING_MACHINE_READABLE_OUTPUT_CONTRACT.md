# LegacyMapper V4 — R12 Plugin-Facing Machine-Readable Output Contract

TASK=V4_R12_PLUGIN_FACING_MACHINE_READABLE_OUTPUT_CONTRACT

MODE=DETERMINISTIC_MACHINE_READABLE_PROJECTION

IMPLEMENTATION_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

Implement V4-R12:

```text
Plugin-Facing Machine-Readable Output Contract
```

LegacyMapper constructs and governs knowledge.

Plugin consumes knowledge and performs future autonomous project work.

The architectural boundary is:

```text
INPUT MATERIAL
      ↓
LegacyMapper
      ↓
Canonical Knowledge Source (R10)
      │
      ├──────────────→ R11 Human-Readable Projection
      │
      └──────────────→ R12 Plugin-Facing Projection
```

R12 must project the SAME canonical approved Knowledge Source established by R10 into a deterministic machine-readable contract suitable for future Plugin consumption.

Fundamental invariant:

```text
R12_SOURCE=CANONICAL_KNOWLEDGE_SOURCE
R12_SOURCE!=R11_MARKDOWN
```

R12 is a projection.

It is NOT:

* another canonical knowledge store;
* another truth source;
* an approval mechanism;
* an AI interpretation stage;
* a replacement for R10;
* a parser of R11 Markdown;
* Plugin itself;
* an agent runtime;
* an orchestration engine.

Required:

```text
PLUGIN_PAYLOAD_IS_PROJECTION=true
PLUGIN_PAYLOAD_IS_CANONICAL_SOURCE=false
```

---

# Required Reading

Read in this order:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_PROPOSED_ROADMAP.md`
7. `docs/V4/V4_CONTRACT_FOUNDATION.md`
8. `docs/V4/V4_R10_CANONICAL_KNOWLEDGE_COMPOSITION_RESULT.md`
9. `docs/V4/V4_R10_CLOSURE_AND_VERSIONING_RESULT.md`
10. `output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_CONTRACT.json`
11. `output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_EXAMPLE.json`
12. `legacy_documenter/knowledge/canonical/models.py`
13. `legacy_documenter/knowledge/canonical/service.py`
14. `docs/V4/V4_R11_HUMAN_READABLE_DOCUMENT_PROJECTION_RESULT.md`
15. `docs/V4/V4_R11_CLOSURE_AND_VERSIONING_RESULT.md`
16. `output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_CONTRACT.json`
17. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
18. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Inspect existing V3/R1-R11 serialization and deterministic contract/report patterns before implementing.

Reuse existing stable serialization and validation approaches where appropriate.

Do not duplicate capabilities merely because R12 introduces a new projection.

---

# Entry Gate

Before implementation verify:

```text
latest_completed_round = V4-R11
latest_approved_round = V4-R11

current_round_in_progress = null

round_status = V4-R11_APPROVED
next = V4-R12

tests >= 1213

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Verify:

```text
git status
```

Expected:

```text
CLEAN
```

If R11 is not formally approved and closed:

STOP.

If unrelated user work is present:

STOP and report it.

Do not silently reconcile repository state.

---

# Core Architectural Boundary

Preserve:

```text
ONE_CANONICAL_KNOWLEDGE_SOURCE
```

R12 reads:

```text
CanonicalKnowledgeCollection
```

from R10.

R12 must NOT read its knowledge from:

```text
output/v4_r11/example_docs/
Markdown files
R11 DocumentProjection
R11 ProjectionManifest
human-rendered documents
```

R11 and R12 are sibling projections.

Required:

```text
                 R10
       Canonical Knowledge Source
                 │
          ┌──────┴──────┐
          ↓             ↓
         R11           R12
       Markdown    Plugin payload
```

Forbidden:

```text
R10 → R11 Markdown → R12
```

---

# Canonical Input Is Read-Only

R12 must never:

* add canonical entries;
* remove canonical entries;
* mutate canonical entries;
* change status;
* change temporal state;
* change source type;
* change nature;
* change evidence;
* change provenance;
* modify proposals;
* modify approvals;
* resolve gaps;
* resolve conflicts;
* infer new knowledge.

Required:

```text
CANONICAL_INPUT_READ_ONLY=true
CANONICAL_INPUT_MUTATION=NONE
```

---

# Plugin Boundary

The future Plugin is a separate consumer system.

LegacyMapper R12 only produces a contract/payload.

R12 must NOT implement:

* Plugin runtime;
* Plugin agents;
* agent orchestration;
* task planning;
* code generation;
* project development;
* project modification;
* autonomous execution;
* model selection;
* provider routing;
* prompt execution;
* external-system actions.

Required:

```text
LEGACYMAPPER_CONSTRUCTS_KNOWLEDGE
PLUGIN_CONSUMES_KNOWLEDGE
```

---

# Versioned Machine Contract

The Plugin-facing payload must have an explicit contract version.

Prefer a closed constant such as:

```text
contract_name = "LegacyMapperPluginKnowledge"
contract_version = "1.0"
```

or an equivalently explicit stable representation.

Do not derive version from:

* current date;
* Git hash;
* test count;
* runtime environment;
* package version;
* machine state.

Version changes must be intentional future contract decisions.

Required:

```text
EXPLICIT_CONTRACT_VERSION=true
```

---

# Payload Envelope

Define a deterministic top-level machine-readable envelope.

A preferred conceptual structure is:

```text
PluginKnowledgePayload
    contract_name
    contract_version
    canonical_source
    entries
    manifest
```

The exact Python representation may differ if a cleaner design is justified.

Do not introduce unnecessary abstractions.

The payload must clearly state that its entries originate from the canonical Knowledge Source.

Suggested canonical source metadata:

```text
source_kind = "CANONICAL_KNOWLEDGE_SOURCE"
projection_kind = "PLUGIN_MACHINE_READABLE"
```

Do not call the payload:

```text
truth
source_of_truth
plugin_truth
```

---

# Entry Projection

Every eligible canonical entry in the machine-readable projection must preserve enough information for Plugin to consume the knowledge without consulting R11 Markdown.

At minimum project:

```text
knowledge_id
statement
source_type
nature
status
temporal_state
evidence_refs
related_statement_ids
```

Also preserve canonical traceability to:

```text
proposal_id
approval_decision_id
```

where these fields exist in R10 canonical entries.

Provenance should be projected in a structured machine-readable representation when present.

Do not invent provenance when absent.

Do not replace canonical identifiers with new Plugin-specific knowledge identifiers.

Required:

```text
PLUGIN_ENTRY_ID=CANONICAL_KNOWLEDGE_ID
```

---

# Approval Semantics

The payload comes from R10 canonical approved knowledge.

Do not create a second Plugin approval state.

The payload may expose traceability to the approval decision, but must not reinterpret approval.

Required:

```text
PLUGIN_PROJECTION_DOES_NOT_APPROVE
PLUGIN_PROJECTION_DOES_NOT_REJECT
PLUGIN_PROJECTION_DOES_NOT_CHANGE_KNOWLEDGE_STATUS
```

Remember:

```text
APPROVED != CONFIRMED
```

An approved canonical entry may retain a status other than CONFIRMED.

---

# Evidence

Preserve canonical evidence references exactly and deterministically.

Do not:

* invent evidence;
* drop evidence silently;
* convert evidence IDs into claims;
* mark evidence authoritative differently;
* fetch external evidence;
* resolve evidence at projection time.

The Plugin contract should allow the future consumer to understand which evidence references support an entry.

If only IDs/references are available in the canonical model, preserve those IDs/references.

Do not expand them by inference.

---

# Provenance

When canonical provenance is present, preserve it structurally.

Required:

```text
PROVENANCE_PRESERVED=true
```

Do not conflate:

```text
provenance
approval
authority
status
source_type
```

These remain distinct concepts.

AI-originated material that was later approved by the Technical Lead must remain traceable as AI-originated plus separately human-approved.

Approval must not rewrite provenance.

---

# Relationships

Preserve:

```text
related_statement_ids
```

deterministically.

Do not infer additional graph relationships.

Do not convert R7 relations into resolved truth.

If the R10 canonical entry only carries relation references, preserve those references as defined.

R12 must not perform graph reasoning.

---

# Temporal Semantics

Preserve:

```text
AS_IS
TO_BE
HISTORICAL
None / unspecified
```

exactly according to canonical data.

Do not infer temporal state.

Do not automatically:

* supersede HISTORICAL;
* conflict AS_IS with TO_BE;
* promote TO_BE to current;
* treat unspecified as AS_IS.

---

# Knowledge Status Semantics

Preserve canonical KnowledgeStatus exactly.

Do not promote:

```text
PARTIAL
INTERPRETED
UNRESOLVED
CONFLICTING
MISSING
SUPERSEDED
```

or any other valid canonical status into CONFIRMED.

Machine-readable output must make uncertainty visible rather than hide it.

---

# Human-Information-Only Support

R12 must work when canonical knowledge contains no source-code evidence.

Required scenario:

```text
HUMAN_INFORMATION_ONLY
```

The payload must not require:

* source file;
* repository path;
* project path;
* symbol;
* method;
* language;
* framework;
* assembly;
* database;
* source-code location.

Code remains optional.

Required:

```text
SOURCE_CODE_OPTIONAL=true
```

---

# Technology Neutrality Within V4 Scope

Do not redesign the V1/V2 extraction pipeline.

V5 remains the round/version for true source-extraction technology/language/framework agnosticism.

However, the R12 Plugin-facing contract must not unnecessarily require VB.NET-specific fields.

Required:

```text
PLUGIN_CONTRACT_NOT_VBNET_SPECIFIC=true
```

The machine-readable knowledge contract should be usable for canonical knowledge produced from:

* code;
* human information;
* mixed sources;
* partial information.

---

# Deterministic Serialization

Provide a deterministic JSON serialization.

Requirements:

```text
UTF-8
stable key ordering
stable entry ordering
stable nested collection ordering where semantically unordered
no timestamps
no UUIDs
no runtime object identity
no machine-specific paths
no locale-dependent output
```

Preferred entry ordering:

```text
knowledge_id
```

unless a better deterministic ordering is justified.

Preserve meaningful sequence only where sequence is part of the canonical contract.

---

# Manifest

Include deterministic payload metadata sufficient for a consumer to validate basic completeness.

Suggested:

```text
PluginKnowledgeManifest
    canonical_entry_count
    projected_entry_count
    knowledge_ids
    status_counts
    source_type_counts
    nature_counts
    temporal_state_counts
```

Counts must be derived deterministically.

The manifest is projection metadata.

It is NOT canonical knowledge.

Do not introduce metrics requiring semantic interpretation.

Required:

```text
MANIFEST_IS_PROJECTION_METADATA=true
```

---

# Completeness Policy

Preferred default:

```text
ALL_CANONICAL_ENTRIES_PROJECTED
```

R12 should normally project every canonical entry because Plugin needs the complete canonical Knowledge Source.

Do not reuse R11 document mapping rules to filter machine knowledge.

Required:

```text
R12_DOES_NOT_USE_R11_MAPPING_RULES=true
```

If a canonical entry cannot be serialized under the contract:

FAIL explicitly.

Do not silently omit it.

Required:

```text
SILENT_ENTRY_OMISSION=FORBIDDEN
```

---

# Schema / Validation

The machine-readable output must have an explicit deterministic validation contract.

Use a simple maintainable mechanism consistent with the existing repository.

Do not add a large new dependency solely for schema validation unless already justified by the repository architecture.

Validate at minimum:

```text
contract name/version
canonical source kind
projection kind
entry identity
required fields
closed enum values
collection uniqueness
canonical count == projected count
manifest consistency
traceability fields
JSON compatibility
```

Duplicate `knowledge_id` in one payload must be rejected.

---

# Compatibility Policy

Document compatibility expectations.

For contract version `1.0`:

* consumers may rely on required fields;
* new optional fields in a future compatible revision must not silently alter existing field semantics;
* removal/renaming/semantic reinterpretation of required fields requires an intentional contract-version decision;
* enum expansion must be treated explicitly because consumers may use closed vocabularies.

Do not build a migration framework in R12.

Only define the contract policy.

---

# Projection Identity

Do NOT create a second identity for each knowledge entry.

Required:

```text
machine_entry.knowledge_id == canonical_entry.knowledge_id
```

The top-level payload itself may have a deterministic fingerprint/hash if useful, but it must be derived entirely from serialized content.

If implemented:

```text
payload_fingerprint = SHA256(canonical serialized payload content)
```

Do not include the fingerprint recursively inside the bytes from which it is calculated unless a clearly separated canonical hashing representation is defined.

A fingerprint is optional.

Do not create complexity solely to have one.

---

# Security

Treat canonical statement, metadata, provenance, evidence identifiers, and relation identifiers as untrusted data.

Serialization must never execute them.

Forbidden:

```text
eval
exec
dynamic import from content
shell execution
template-code execution
deserialization into executable objects
filesystem path execution
provider invocation
```

Prompt-injection-shaped content must remain inert JSON string data.

Do not expose secrets merely because they exist in arbitrary metadata.

Inspect existing sanitization policy and reuse it appropriately.

Do not silently alter canonical statement text.

If arbitrary metadata creates a conflict between exact canonical preservation and secret-safe Plugin projection, STOP and document the boundary rather than inventing a policy.

---

# Metadata Policy

R10 contains metadata.

Do NOT automatically dump arbitrary metadata into the Plugin payload unless its safety and contract semantics are explicitly justified.

Preferred conservative policy:

```text
CANONICAL_METADATA_DEFAULT=NOT_PROJECTED
```

Project only explicitly contracted fields.

This avoids turning arbitrary metadata into an unstable Plugin API or leaking incidental internal information.

If some metadata is required, define an explicit allowlist.

Do not use free-form metadata as hidden semantic behavior in Plugin.

---

# R11 Independence

Tests must demonstrate that changing R11 projection configuration or Markdown formatting does not change the R12 machine payload for identical R10 canonical input.

Required:

```text
R11_INDEPENDENCE=PASS
```

R12 package must not import:

```text
legacy_documenter.knowledge.projection
```

unless there is a purely generic utility whose reuse cannot create semantic coupling.

Prefer no R11 package dependency.

---

# Suggested Package

Prefer:

```text
legacy_documenter/knowledge/plugin_projection/
```

Possible files:

```text
__init__.py
models.py
service.py
serializer.py
validator.py
contract_report.py
example_report.py
```

Use only the structure needed for clear responsibilities.

Follow:

```text
docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md
```

Classes PascalCase.

Modules snake_case.

Type hints at public/service boundaries.

Concise docstrings for significant public classes/functions.

Avoid unnecessary magic and pattern proliferation.

---

# In-Memory Boundary

Core flow should preferably be:

```text
CanonicalKnowledgeCollection
          ↓
PluginProjectionService
          ↓
PluginKnowledgePayload
          ↓
deterministic serializer
          ↓
JSON string/bytes
```

Core projection must not require filesystem state.

Contract/example report generation may write deterministic artifacts through isolated existing output mechanisms.

---

# Required Synthetic Example

Create a deterministic synthetic Plugin-facing example demonstrating at least:

1. code-origin canonical knowledge;
2. human-information-only canonical knowledge;
3. AI-originated interpretation later approved by Technical Lead while provenance remains AI-originated;
4. CONFIRMED entry;
5. PARTIAL or equivalent non-confirmed entry;
6. UNRESOLVED entry;
7. AS_IS entry;
8. TO_BE entry;
9. HISTORICAL entry;
10. unspecified temporal state;
11. evidence references;
12. proposal/approval traceability;
13. related statement IDs;
14. provenance present;
15. provenance absent;
16. no source-code-specific fields required for human-only entry;
17. prompt-injection-shaped statement serialized inertly.

Use synthetic data only.

Do not present it as actual organizational knowledge.

---

# Contract Artifact

Generate:

```text
output/v4_r12/V4_PLUGIN_FACING_OUTPUT_CONTRACT.json
```

It must document at minimum:

```text
contract_name
contract_version

payload_model
entry_model
manifest_model

canonical_source_policy
projection_policy
canonical_mutation_policy

identity_policy
completeness_policy
silent_omission_policy

source_code_policy
technology_specificity_policy

statement_policy
status_policy
temporal_policy
evidence_policy
provenance_policy
relationship_policy
approval_traceability_policy
metadata_policy

serialization_policy
ordering_policy
validation_policy
compatibility_policy

R11_independence
Plugin_boundary

AI_policy
provider_policy
security_policy
```

It must explicitly state:

```text
ONE_CANONICAL_KNOWLEDGE_SOURCE
PLUGIN_PAYLOAD_IS_PROJECTION
PLUGIN_PAYLOAD_IS_NOT_CANONICAL_KNOWLEDGE
R12_SOURCE_IS_R10_CANONICAL_KNOWLEDGE
R12_SOURCE_IS_NOT_R11_MARKDOWN
CANONICAL_INPUT_READ_ONLY
ALL_CANONICAL_ENTRIES_PROJECTED
SILENT_ENTRY_OMISSION_FORBIDDEN
PLUGIN_ENTRY_ID_IS_CANONICAL_KNOWLEDGE_ID
APPROVAL_DOES_NOT_CHANGE_KNOWLEDGE_STATUS
PROVENANCE_REMAINS_DISTINCT_FROM_APPROVAL
SOURCE_CODE_IS_OPTIONAL
PLUGIN_CONTRACT_IS_NOT_VBNET_SPECIFIC
R12_DOES_NOT_USE_R11_MAPPING_RULES
R12_DOES_NOT_IMPLEMENT_PLUGIN_RUNTIME
AI_NEVER_DECIDES_PLUGIN_PROJECTION
```

---

# Example Artifact

Generate:

```text
output/v4_r12/V4_PLUGIN_FACING_OUTPUT_EXAMPLE.json
```

This should be an actual valid example of the versioned machine-readable Plugin payload or a deterministic wrapper containing that exact payload.

Prefer making it directly consumable as the contract example rather than a prose report.

---

# Determinism

Generate contract and example independently at least twice.

Require byte-identical output.

Also serialize the same payload in separate Python processes and compare bytes.

Required:

```text
CONTRACT_DETERMINISM=PASS
EXAMPLE_DETERMINISM=PASS
PAYLOAD_SERIALIZATION_DETERMINISM=PASS
```

---

# Tests

Add deterministic tests covering at minimum:

## Entry Gate

* R11 formally approved;
* repository continuity;
* baseline >=1213.

## Canonical Boundary

* R10 collection read-only;
* no canonical entry creation by R12;
* no canonical mutation;
* no proposal mutation;
* no approval mutation;
* no status mutation;
* no temporal mutation.

## Source Boundary

* R12 consumes R10 canonical collection;
* no R11 Markdown input;
* no R11 projection-rule dependency;
* no R11 package semantic dependency.

## Payload

* explicit contract name;
* explicit contract version;
* canonical source kind;
* projection kind;
* required entry fields;
* every canonical entry projected;
* canonical/projected counts equal;
* no silent omission;
* duplicate IDs rejected.

## Identity

* Plugin entry retains KNO- id;
* no second knowledge identity.

## Status

* CONFIRMED preserved;
* PARTIAL preserved;
* INTERPRETED/UNRESOLVED/etc. preserved as supported by canonical enum;
* approval never forces CONFIRMED.

## Temporal

* AS_IS preserved;
* TO_BE preserved;
* HISTORICAL preserved;
* unspecified remains unspecified.

## Evidence

* evidence references preserved;
* no invented evidence;
* no evidence resolution.

## Provenance

* provenance preserved when present;
* absent remains absent;
* AI origin remains AI origin after TL approval;
* approval remains separate.

## Relationships

* related_statement_ids preserved;
* no relationship inference.

## Human-Only Knowledge

* payload works without source-code fields;
* no repository/symbol/language/framework requirement.

## Metadata

* arbitrary canonical metadata is not projected by default;
* no hidden mapping behavior from metadata.

## Serialization

* valid JSON;
* deterministic ordering;
* JSON-compatible values;
* deterministic bytes;
* no timestamps/random UUIDs/machine paths.

## Validation

* invalid contract version rejected;
* invalid source/projection kind rejected;
* invalid enum rejected;
* duplicate knowledge IDs rejected;
* manifest mismatch rejected;
* missing required traceability rejected.

## Security

* prompt injection inert;
* HTML/Markdown-shaped strings inert;
* shell-shaped content inert;
* no eval/exec/dynamic content execution;
* no provider call;
* no secret leakage through arbitrary metadata;
* fixed/non-echoing validation errors where appropriate.

## R11 Independence

* R11 rendering/configuration changes do not affect R12 payload;
* R12 does not parse Markdown.

## Plugin Boundary

* no Plugin runtime;
* no agents;
* no orchestration;
* no task execution;
* no model/provider routing.

## AI Boundary

* REAL_LLM_CALLS=0;
* PROVIDER_CALLS=0.

## Determinism

* contract deterministic;
* example deterministic;
* payload deterministic across processes.

## Regression

Run full suite.

Expected:

```text
>1213 PASS
```

Do not reduce existing coverage.

---

# PROJECT_STATE After Successful Implementation

Update using the existing schema:

```text
latest_completed_round = V4-R12
latest_approved_round = V4-R11

current_round_in_progress =
"V4-R12 (pending Technical Lead review)"

round_status =
V4-R12_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R12

tests = <actual final count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do NOT mark R12 approved.

---

# Required Result Document

Create:

```text
docs/V4/V4_R12_PLUGIN_FACING_MACHINE_READABLE_OUTPUT_CONTRACT_RESULT.md
```

Report at minimum:

```text
STATUS
ENTRY_GATE

BASELINE_TESTS
FINAL_TESTS

CONTRACT_NAME
CONTRACT_VERSION

PAYLOAD_MODEL
ENTRY_MODEL
MANIFEST_MODEL

CANONICAL_SOURCE_POLICY
R12_SOURCE
R11_DEPENDENCY
CANONICAL_INPUT_MUTATION

IDENTITY_POLICY
COMPLETENESS_POLICY
SILENT_OMISSION_POLICY

SOURCE_CODE_POLICY
TECHNOLOGY_SPECIFICITY

STATEMENT_POLICY
STATUS_POLICY
TEMPORAL_POLICY
EVIDENCE_POLICY
PROVENANCE_POLICY
RELATIONSHIP_POLICY
APPROVAL_TRACEABILITY_POLICY
METADATA_POLICY

SERIALIZATION_POLICY
ORDERING_POLICY
VALIDATION_POLICY
COMPATIBILITY_POLICY

PLUGIN_BOUNDARY

SECURITY

AI_CALLS
PROVIDER_CALLS

CONTRACT_ARTIFACT
CONTRACT_SHA256

EXAMPLE_ARTIFACT
EXAMPLE_SHA256

CONTRACT_DETERMINISM
EXAMPLE_DETERMINISM
PAYLOAD_SERIALIZATION_DETERMINISM

R11_INDEPENDENCE

V3_REGRESSION
V4_R1_REGRESSION
V4_R2_REGRESSION
V4_R3_REGRESSION
V4_R4_REGRESSION
V4_R5_REGRESSION
V4_R6_REGRESSION
V4_R7_REGRESSION
V4_R8_REGRESSION
V4_R9_REGRESSION
V4_R10_REGRESSION
V4_R11_REGRESSION

READINESS

AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED

REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE

PRODUCTION_BEHAVIOR_CHANGED
TECHNICAL_DEBT

DESIGN_DECISIONS

DECISION
NEXT
```

---

# Expected Success State

```text
STATUS=V4_R12_PLUGIN_FACING_MACHINE_READABLE_OUTPUT_CONTRACT_COMPLETE

ENTRY_GATE=PASS

FINAL_TESTS=>1213_PASS

CONTRACT_NAME=LegacyMapperPluginKnowledge
CONTRACT_VERSION=1.0

CANONICAL_SOURCE_POLICY=ONE_CANONICAL_KNOWLEDGE_SOURCE

R12_SOURCE=R10_CANONICAL_KNOWLEDGE
R11_DEPENDENCY=NONE

CANONICAL_INPUT_MUTATION=NONE

IDENTITY_POLICY=CANONICAL_KNOWLEDGE_ID_PRESERVED

COMPLETENESS_POLICY=ALL_CANONICAL_ENTRIES_PROJECTED
SILENT_OMISSION_POLICY=FORBIDDEN

SOURCE_CODE_POLICY=OPTIONAL
TECHNOLOGY_SPECIFICITY=NOT_VBNET_SPECIFIC

STATEMENT_POLICY=VERBATIM
STATUS_POLICY=PRESERVE
TEMPORAL_POLICY=PRESERVE
EVIDENCE_POLICY=PRESERVE_REFERENCES
PROVENANCE_POLICY=PRESERVE_WHEN_PRESENT
RELATIONSHIP_POLICY=PRESERVE_REFERENCES
APPROVAL_TRACEABILITY_POLICY=PRESERVE
METADATA_POLICY=NOT_PROJECTED_BY_DEFAULT

SERIALIZATION_POLICY=DETERMINISTIC_JSON
VALIDATION_POLICY=STRICT_CONTRACT_VALIDATION

PLUGIN_BOUNDARY=CONTRACT_ONLY_NO_RUNTIME

SECURITY=PASS

AI_CALLS=0
PROVIDER_CALLS=0

CONTRACT_DETERMINISM=PASS
EXAMPLE_DETERMINISM=PASS
PAYLOAD_SERIALIZATION_DETERMINISM=PASS

R11_INDEPENDENCE=PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW

DECISION=V4_R12_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_R12
```

---

# Stop Condition

After implementation, tests, deterministic artifact generation and result documentation:

STOP.

Do NOT:

* approve R12;
* commit;
* push;
* implement R13;
* implement Plugin;
* create Plugin agents;
* create autonomous execution;
* call an AI/provider;
* use R11 Markdown as R12 input.

The next action is:

```text
HUMAN_REVIEW_V4_R12
```
