# LegacyMapper — Post V4.1 User Manual, Technical Manual and Glossary

TASK=POST_V4_1_USER_TECHNICAL_MANUALS_AND_GLOSSARY

MODE=DOCUMENTATION_ONLY

V4_1_REOPEN_ALLOWED=false
PRODUCTION_CODE_CHANGE_ALLOWED=false
TEST_CHANGE_ALLOWED=false
CONTRACT_CHANGE_ALLOWED=false
BASELINE_CHANGE_ALLOWED=false
MANIFEST_CHANGE_ALLOWED=false
V5_IMPLEMENTATION_ALLOWED=false
PLUGIN_IMPLEMENTATION_ALLOWED=false

REAL_LLM_RUNTIME_CALLS_ALLOWED=false
PROVIDER_RUNTIME_CALLS_ALLOWED=false

COMMIT_ALLOWED=false
PUSH_ALLOWED=false

---

# Objective

Create three definitive, understandable documentation documents for the
formally closed LegacyMapper V4.1 system:

1. User Manual
2. Technical / Developer Manual
3. Shared Glossary

The documentation must describe the ACTUAL IMPLEMENTED V4.1 system.

Do not document planned V5 behavior as if it already existed.

Do not invent commands, APIs, interfaces, workflows, modules or
capabilities unsupported by repository evidence.

The documentation must be useful without requiring access to the
development conversation that created LegacyMapper.

---

# Authority

Repository artifacts are authoritative.

Read before writing:

1. CLAUDE.md
2. AGENTS.md
3. PROJECT_STATE.json
4. docs/PROJECT_RECOVERY.md
5. docs/GENERATED_ARTIFACT_POLICY.md
6. docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md

Then read:

7. docs/V4/V4_USER_MANUAL.md
8. docs/V4/V4_DEVELOPER_MANUAL.md
9. docs/V4/V4_OPERATIONS_AND_RECOVERY_MANUAL.md
10. docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md
11. docs/V4/V4_FINAL_CLOSURE_RESULT.md

Then read the V4.1 documentation and closure chain:

12. docs/V4_1/V4_1_R0_MAINTAINABILITY_INVENTORY_AND_REFACTOR_PLAN_RESULT.md
13. every V4.1 R1-R10 implementation result
14. every V4.1 R0-R10 closure/versioning result
15. docs/V4_1/V4_1_FINAL_CLOSURE_AND_VERSIONING_RESULT.md

Then inspect the current production source code directly.

Do not rely only on historical documentation when current V4.1 source
can verify a technical statement.

---

# Governing Principle

DOCUMENT_THE_IMPLEMENTED_SYSTEM

DO_NOT_REDESIGN_THE_SYSTEM

DO_NOT_INVENT_MISSING_FUNCTIONALITY

V4.1 is formally closed.

This task is a post-closure documentation supplement.

It must NOT reopen or mutate the V4.1 baseline.

---

# Audience

## User Manual

Audience:

- Technical Lead
- analyst
- controlled operator
- developer who only needs to operate LegacyMapper
- person receiving LegacyMapper for the first time

Assume:

- basic knowledge of repositories/files;
- no Python expertise required;
- no knowledge of LegacyMapper architecture required.

Use simple Spanish.

Explain technical terms only when necessary.

Use examples.

---

## Technical Manual

Audience:

- software developer;
- maintainer;
- future LegacyMapper developer;
- AI development agent receiving the repository.

Assume general software-development knowledge.

Do NOT assume previous knowledge of LegacyMapper.

The manual must be understandable by a C#/.NET developer with limited
Python experience.

Use Python terminology correctly, but explain important Python-specific
concepts when they differ significantly from a typical C# mental model.

---

## Glossary

Audience:

Both user and developer.

Definitions must be short, precise and LegacyMapper-specific.

Do not turn the glossary into another technical manual.

---

# DOCUMENT 1

Create:

docs/V4_1/LEGACYMAPPER_USER_MANUAL_V4_1.md

Title:

# LegacyMapper V4.1 — Manual de Usuario

The manual must answer, in understandable language:

## 1. ¿Qué es LegacyMapper?

Explain the purpose of the system.

Explain that LegacyMapper helps discover, organize, interpret,
validate and document knowledge about legacy systems.

Explain the fundamental separation:

Python discovers/resolves deterministic facts.
AI interprets when interpretation is required.
Technical Lead approves.

Do not imply AI authority.

---

## 2. ¿Qué problema resuelve?

Explain examples such as:

- poorly documented legacy applications;
- large repositories;
- unknown dependencies;
- functional flows difficult to follow;
- database access distributed through code;
- business knowledge outside source code;
- need to generate structured documentation;
- need to preserve uncertainty and provenance.

---

## 3. What LegacyMapper V4.1 can currently do

Describe only implemented capabilities.

Include the current .NET/VB.NET legacy-analysis capability.

Explain current code-oriented discovery including, where supported:

- solutions;
- projects;
- WebForms;
- classes;
- methods;
- dependencies;
- calls;
- database access;
- functional flows;
- unresolved relationships;
- evidence and confidence.

Also describe V4 capabilities:

- human-supplied information;
- provenance;
- classification;
- AS_IS / TO_BE / HISTORICAL;
- gap/conflict representation;
- proposals;
- Technical Lead approval;
- canonical knowledge;
- human-readable projection;
- machine-readable Plugin projection contract.

Clearly distinguish implemented capability from exposed end-user CLI
or automation.

---

## 4. What LegacyMapper does NOT currently do

Explicitly document at least:

- Plugin runtime is NOT implemented;
- V5 is NOT implemented;
- it is not yet fully language/framework/database agnostic;
- AI cannot approve knowledge;
- it does not modify the analyzed legacy source;
- it does not autonomously develop the target project;
- do not claim a unified V4 knowledge CLI if none exists.

---

## 5. Supported information modes

Explain clearly:

CODE_ONLY

CODE_AND_HUMAN_INFORMATION

HUMAN_INFORMATION_ONLY

PARTIAL_INFORMATION

For each mode provide:

- what information is available;
- what LegacyMapper can do with it;
- expected limitations;
- simple example.

---

## 6. Main conceptual workflow

Explain visually and in prose:

INPUT MATERIAL
      ↓
INGESTION / NORMALIZATION
      ↓
EVIDENCE / CONTEXT
      ↓
ANALYSIS / CLASSIFICATION / RELATIONSHIP
      ↓
PROPOSALS
      ↓
TECHNICAL LEAD APPROVAL
      ↓
CANONICAL KNOWLEDGE SOURCE
      ↓
 ┌────┴─────┐
 ↓          ↓
Human       Machine
documents   projection

Explain each step in non-technical language.

---

## 7. Source code analysis workflow

Explain how a user provides a legacy repository.

Verify the actual CLI implementation before documenting commands.

If the current supported command remains:

python main.py "<repository>" --output "<output>" [--verbose]

document it exactly.

If the source shows another authoritative invocation, document the
actual one instead.

Never invent a command.

Provide a Windows example using neutral paths such as:

C:\Legacy\Sistema
C:\LegacyMapperResults

Do not use machine-specific paths from the development environment.

---

## 8. Understanding generated results

Explain:

- deterministic facts;
- inferred information;
- unresolved information;
- confidence;
- evidence;
- provenance;
- proposals;
- approved knowledge;
- generated documents.

Explain that unresolved does not mean failure.

Explain why LegacyMapper preserves uncertainty rather than guessing.

---

## 9. Human approval

Explain:

Technical Lead is the final approval authority.

AI may propose or interpret.

System may validate structure.

Neither AI nor system grants final approval.

Explain approve / reject / correct conceptually.

---

## 10. Canonical Knowledge Source

Explain in simple language why there is ONE canonical knowledge source.

Explain:

Canonical Knowledge
        ↓
   ┌────┴────┐
   ↓         ↓
Human docs   Plugin projection

Explain that generated Markdown documents are views of canonical
knowledge, not independent truth stores.

---

## 11. Generated documentation

Explain the R11 human-readable projection.

Explain the 00-09 document-family concept without overwhelming the user.

Explain traceability via knowledge_id.

Explain UNMAPPED entries.

---

## 12. AS_IS, TO_BE and HISTORICAL

Provide simple practical examples.

Explain that:

AS_IS != TO_BE

does not automatically mean contradiction.

It may represent a GAP.

---

## 13. GAP versus CONFLICT

Provide simple examples.

Example GAP:

AS_IS:
Application authenticates locally.

TO_BE:
Application must use corporate SSO.

Example CONFLICT:

Source A:
Database X is authoritative.

Source B:
Database Y is authoritative.

Do not claim these examples are actual project facts.

Mark them explicitly as examples.

---

## 14. Safety

Explain:

- legacy source is read-only;
- uncertainty is preserved;
- no hidden approval;
- provenance is retained;
- secrets should not be placed in documentation;
- generated artifacts must follow repository policy.

---

## 15. Common problems

Create a troubleshooting table.

Include at least:

READINESS not READY

missing repository

invalid output path

partial analysis

unresolved relationships

missing evidence

proposal pending approval

UNMAPPED canonical entry

tests failing

dirty repository during controlled maintenance

Do not invent error codes.

---

## 16. Practical usage example

Create a complete fictional example from:

legacy repository
→ analysis
→ evidence
→ interpretation
→ proposal
→ approval
→ canonical knowledge
→ human-readable documentation.

Clearly label it:

EJEMPLO ILUSTRATIVO — NO REPRESENTA DATOS REALES.

---

## 17. Current version status

Record:

V4 = FORMALLY CLOSED
V4.1 = FORMALLY CLOSED

Use the actual final test count from PROJECT_STATE.

Expected current baseline:

1566 PASS
0 FAIL
0 SKIP

READINESS=READY

PLUGIN_RUNTIME=NOT_IMPLEMENTED

V5_IMPLEMENTED=false

Verify before writing.

---

# DOCUMENT 2

Create:

docs/V4_1/LEGACYMAPPER_TECHNICAL_MANUAL_V4_1.md

Title:

# LegacyMapper V4.1 — Manual Técnico para Desarrolladores

This must be a comprehensive developer manual.

---

## 1. Purpose

Explain what LegacyMapper is architecturally.

Explain:

deterministic discovery
→ evidence
→ interpretation
→ controlled approval
→ canonical knowledge
→ projections.

---

## 2. Design principles

Document:

Python discovers/resolves.
AI interprets.
Technical Lead approves.

Evidence before inference.

No invented relationships.

Preserve uncertainty.

Preserve provenance.

One canonical knowledge source.

Source code optional.

Agent-neutral repository continuity.

Determinism where possible.

---

## 3. Current technology scope

Clearly distinguish V4.1 from V5.

Describe actual current supported legacy technology discovered from
the source.

Expected current principal scenario:

.NET Framework
VB.NET
ASP.NET Web Forms
Oracle

Do not claim general language/framework agnosticism.

---

## 4. Repository structure

Describe the actual current repository.

At minimum inspect and explain:

legacy_documenter/
tests/
docs/
prompts/
output/
tools/
PROJECT_STATE.json
AGENTS.md
CLAUDE.md

Explain historical codex/V1-V3 if still present.

Use an ASCII tree.

Do not fabricate directories.

---

## 5. Python architecture

Inspect the actual production tree.

Explain major areas such as:

scanner/
extractors/
analysis/
context/
documentation/
llm/
knowledge/
utils/

Only include directories that actually exist.

For each:

Purpose
Inputs
Outputs
Important classes/modules
Dependencies
Whether deterministic or AI-related.

---

## 6. V4 knowledge architecture

Explain the actual packages under:

legacy_documenter/knowledge/

Expected packages must be verified from source:

domain
input
provenance
ingestion
classification
temporal
relations
proposals
approval
canonical
projection
plugin_projection

Also describe closure/readiness support where appropriate.

Explain dependency direction.

Explain immutable/read-only boundaries.

---

## 7. Data lifecycle

Document:

Material
Evidence
Interpretation
Proposal
Approval
CanonicalKnowledgeEntry
Projection

Include IDs and their actual deterministic prefixes.

Verify prefixes from source.

Expected examples include:

KST-
MAT-
EVR-
SRC-
PRN-
PED-
CLS-
TMP-
REL-
PRP-
APR-
KNO-

Do not document a prefix unless verified.

---

## 8. Domain models

Explain the important models.

Include:

SourceType
KnowledgeNature
KnowledgeStatus
TemporalState
TemporalBucket
RelationKind
ProposalKind
ProposalStatus
ProposalMethod
ApprovalDecisionType
ApprovalAuthority
CanonicalKnowledgeEntry

List actual enum members only after verifying source.

---

## 9. Legacy code discovery

Explain how LegacyMapper discovers facts from the current .NET/VB.NET
repository.

Cover where implemented:

solutions/projects
VB source
WebForms
symbols
dependencies
method calls
database access
functional flows
architecture graph
traceability.

Explain the confidence/evidence model.

Explain why project naming conventions alone cannot be treated as
architectural truth.

---

## 10. Database analysis

Explain the current database extractor.

Describe Oracle-related extraction only to the extent supported by
the source.

Explain deterministic scanning/classification.

Explain limitations and unresolved cases.

Mention V4.1-R6 decomposition where useful for maintainers.

Do not expose implementation detail irrelevant to maintenance.

---

## 11. Flow resolver

Explain its responsibility.

Explain graph construction, traversal, path identity, state/reset
behavior and unresolved boundaries at an understandable level.

Document the V4.1 characterization/extraction constraints.

Explain which high-risk areas remain intentionally deferred.

---

## 12. AI boundary

Inspect current implementation.

Explain:

what is deterministic;
what may invoke an LLM;
provider boundary;
what AI is allowed to interpret;
what AI cannot authorize.

Do not describe V5 provider/model agnosticism as implemented.

Clearly state:

V5 will address broader AI provider/model agnosticism.

---

## 13. Canonical Knowledge

Explain CanonicalKnowledgeCollection and CanonicalKnowledgeEntry.

Explain eligibility.

Explain immutability/read-only behavior.

Explain why projections cannot create canonical knowledge.

---

## 14. Human-readable projection

Explain R11 architecture.

Include:

ProjectionTarget
ProjectionRule
ProjectionService
ProjectionManifest

Explain:

41-document closed target architecture if still current.

Explain explicit structured rules.

Explain that free-text semantic routing is forbidden.

Explain knowledge_id traceability.

---

## 15. Plugin-facing projection

Explain R12.

Contract:

LegacyMapperPluginKnowledge
version 1.0

Explain what is projected.

Explain what is intentionally not projected.

Explain:

PLUGIN_RUNTIME=NOT_IMPLEMENTED.

LegacyMapper constructs knowledge.

Plugin consumes knowledge.

---

## 16. Security model

Document actual security invariants.

Include:

read-only legacy source;
safe paths;
no path traversal;
secret handling;
sanitization;
no hidden external dependency;
provider call accounting;
provenance;
approval boundary.

Only claim what repository evidence supports.

---

## 17. Configuration

Document actual configuration mechanisms.

Do not invent environment variables.

Separate:

required
optional
provider-specific
development/test-only.

---

## 18. Running LegacyMapper

Verify all actual commands from source/docs.

Document:

environment preparation;
analysis command;
readiness command;
test command.

Known expected commands include:

python -m unittest discover -s tests

python -m legacy_documenter.knowledge.readiness

Verify before publishing.

---

## 19. Tests

Explain the testing strategy.

Record current baseline only after verifying:

1566 PASS
0 FAIL
0 SKIP

Explain regression/equivalence tests.

Explain deterministic artifact tests.

Explain security tests.

Explain the REG-001 lesson:

tests should not unnecessarily hardcode an exact transient
PROJECT_STATE round literal.

---

## 20. V4.1 maintainability refactor

Provide a concise history of R0-R10.

Do NOT reproduce every round report.

Explain what maintainability problems were addressed.

Explain:

behavior change was forbidden.

Summarize:

shared JSON rendering
typing/contracts
naming
readiness decomposition
orchestrator characterization
controlled extraction
exception-boundary cleanup
documentation/naming
comprehensive equivalence
final baseline.

---

## 21. Remaining technical debt

Use the final V4.1 ledger exactly.

Expected:

DUP-001 RESOLVED
DUP-002 PRESERVED_DISTINCT
DUP-003 UNTOUCHED
DUP-004 UNTOUCHED
DEBT-001 RESOLVED
DEBT-002 RESOLVED
DEBT-003 RESOLVED
REG-002-CANDIDATE RESOLVED
TD-001 OPEN
TD-002 DEFERRED
TD-003 PRESERVED_DISTINCT
TD-004 PARTIALLY_RESOLVED
TD-005 PARTIALLY_RESOLVED

Verify against final closure.

Explain what PRESERVED_DISTINCT means.

Do not silently treat deferred debt as defects requiring immediate
correction.

---

## 22. How to modify LegacyMapper safely

Create a developer procedure:

1. read repository authority;
2. check PROJECT_STATE;
3. understand affected contract;
4. characterize behavior;
5. add/modify tests;
6. implement smallest change;
7. run focused tests;
8. run full regression;
9. run readiness;
10. verify deterministic artifacts if affected;
11. human review;
12. commit/version.

Explain when NOT to refactor.

---

## 23. Python guide for a C# developer

Include a short practical mapping:

Python module       ↔ roughly C# source/namespace responsibility
dataclass           ↔ DTO/value-like model
Enum                ↔ C# enum
tuple/frozen model  ↔ immutable/read-only data
type hints          ↔ compile-time-like documentation/static analysis aid
__init__.py         ↔ package public surface
pytest/unittest     ↔ unit test framework concepts

Clarify that these are conceptual comparisons, not exact language
equivalences.

Explain why trivial C#-style getters/setters/interfaces should not be
introduced into Python.

---

## 24. Extension points

Describe current safe extension points supported by evidence.

Separate from V5 planned architecture.

Do not invent abstractions.

---

## 25. Troubleshooting for developers

Include:

import errors
test regression
readiness failure
artifact hash mismatch
non-deterministic output
unexpected provider call
unresolved extraction
dirty git state
historical artifact modification
canonical/projection boundary violation.

---

## 26. Recovery and continuity

Explain how another developer or AI agent resumes the project solely
from repository artifacts.

Reference:

PROJECT_STATE.json
PROJECT_RECOVERY.md
AGENTS.md
CLAUDE.md
final closure documents
final baseline
final manifest.

Conversation history must not be required.

---

## 27. V5 boundary

Clearly label:

NOT IMPLEMENTED IN V4.1.

Explain future scope only:

language agnosticism
framework agnosticism
project-layout agnosticism
architecture-pattern agnosticism
database/persistence agnosticism
AI-provider agnosticism
AI-model agnosticism.

Do not design V5 here.

---

# DOCUMENT 3

Create:

docs/V4_1/LEGACYMAPPER_GLOSSARY_V4_1.md

Title:

# LegacyMapper V4.1 — Glosario

Organize alphabetically.

Each entry:

TERM
Definition
Why it matters in LegacyMapper
Related terms

Keep definitions concise.

At minimum include, if supported by repository terminology:

AI Interpretation
AI Knowledge Allowed
AI Knowledge Generated
Approval
ApprovalAuthority
ApprovalDecision
AS_IS
Canonical Knowledge
CanonicalKnowledgeCollection
CanonicalKnowledgeEntry
Classification
Code Fact
Confidence
Conflict
Controlled Operator
DETERMINISTIC_CODE_FACT
Determinism
Evidence
Evidence Reference
Gap
HISTORICAL
Human Information
Human Requirement
Ingestion
Knowledge ID
Knowledge Nature
Knowledge Source
Knowledge Status
Legacy Source
LegacyMapper
Material
Machine-Readable Projection
Manifest
Plugin
Plugin Runtime
Projection
ProjectionRule
ProjectionTarget
Proposal
Provenance
Readiness
Relation
R11
R12
SourceType
Technical Lead
Temporal State
TO_BE
Traceability
UNMAPPED
Unresolved
V4
V4.1
V5

Verify actual terminology.

If a term is not part of the actual system, omit it or clearly label
it as explanatory terminology.

---

# Cross-document rules

The three documents must agree with each other.

The User Manual may link to the Glossary.

The Technical Manual may link to both.

The Glossary may link back to the relevant manual section.

Use relative repository links.

Do not duplicate entire technical explanations into the glossary.

---

# Readability Requirements

Write the three manuals in Spanish.

Use:

- clear headings;
- short paragraphs;
- diagrams where useful;
- tables only where they improve comprehension;
- practical examples;
- code blocks for commands;
- warnings where misuse could affect repository integrity.

Avoid excessive formal/governance language in the User Manual.

The Technical Manual may be more precise/formal.

Do not assume the reader participated in V1-V4.1 development.

---

# Accuracy Verification

Before completing:

Verify every documented command against actual repository source.

Verify every documented path exists.

Verify every important class/module mentioned exists.

Verify every enum member against source.

Verify every ID prefix against source.

Verify current test count.

Verify current readiness.

Verify Plugin contract name/version.

Verify Plugin runtime state.

Verify V5 state.

Verify final debt ledger.

Verify V4.1 remains formally closed.

---

# Regression

Run:

python -m unittest discover -s tests

Expected baseline:

1566 PASS
0 FAIL
0 SKIP

Do not modify tests.

Run:

python -m legacy_documenter.knowledge.readiness

Expected:

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
PROVIDER_CALLS=0
REAL_LLM_CALLS=0

---

# Repository Preservation

Require:

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false
TESTS_CHANGED=false
V4_BASELINE_CHANGED=false
V4_1_FINAL_BASELINE_CHANGED=false
V4_1_FINAL_MANIFEST_CHANGED=false

V4_1_FORMALLY_CLOSED=true

Do not update PROJECT_STATE to create a new V4.1 round.

This is documentation created after the closed V4.1 baseline.

---

# Result Report

Create:

docs/V4_1/POST_V4_1_USER_TECHNICAL_MANUALS_AND_GLOSSARY_RESULT.md

Include:

STATUS
FILES_CREATED
FILES_MODIFIED
SOURCE_VERIFICATION
COMMAND_VERIFICATION
PATH_VERIFICATION
MODEL_VERIFICATION
ENUM_VERIFICATION
ID_PREFIX_VERIFICATION
TESTS
READINESS
PLUGIN_CONTRACT
PLUGIN_RUNTIME
V5_IMPLEMENTED
FINAL_DEBT_LEDGER_CONSISTENT
PRODUCTION_CODE_CHANGED
PRODUCTION_BEHAVIOR_CHANGED
TESTS_CHANGED
V4_1_BASELINE_INTEGRITY
V4_1_MANIFEST_INTEGRITY
REPOSITORY_CONTINUITY
DOCUMENTATION_CONSISTENCY
DECISION
NEXT

Expected:

STATUS=POST_V4_1_DOCUMENTATION_READY_FOR_HUMAN_REVIEW

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false
TESTS_CHANGED=false

TESTS=1566_PASS_0_FAIL_0_SKIP
READINESS=READY

V4_1_BASELINE_INTEGRITY=PASS
V4_1_MANIFEST_INTEGRITY=PASS

DOCUMENTATION_CONSISTENCY=PASS

DECISION=POST_V4_1_DOCUMENTATION_READY_FOR_TECHNICAL_LEAD_REVIEW

NEXT=HUMAN_REVIEW_POST_V4_1_DOCUMENTATION

---

# Stop

Do not commit.

Do not push.

Do not begin V5.

Do not modify production code.

Do not modify tests.

Do not alter V4 or V4.1 historical closure documents.

Stop after generating the three manuals and the review result.