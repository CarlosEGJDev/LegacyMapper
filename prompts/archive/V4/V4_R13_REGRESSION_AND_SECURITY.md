# LegacyMapper V4 — R13 Regression and Security

TASK=V4_R13_REGRESSION_AND_SECURITY

MODE=TRANSVERSAL_VALIDATION_AND_HARDENING

IMPLEMENTATION_ALLOWED=true

SEMANTIC_REDESIGN_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

Implement V4-R13:

```text
Regression and Security
```

This round validates the complete LegacyMapper V4 implementation after formal approval of V4-R1 through V4-R12.

R13 is a transversal validation/hardening round.

Its purpose is to prove that:

* V3 remains valid;
* V4-R1 through V4-R12 remain contractually consistent;
* no approved behavior has regressed;
* security boundaries remain intact;
* deterministic behavior remains reproducible;
* canonical knowledge remains protected from mutation;
* human approval authority remains explicit;
* AI/provider boundaries remain preserved;
* R11 and R12 remain sibling projections from R10;
* no hidden source-code requirement was introduced;
* no Plugin runtime was accidentally implemented;
* no secret-bearing or executable content is exposed through unsafe paths;
* repository continuity remains sufficient for a fresh AI agent;
* the project is safe to proceed to V4-R14 final manuals and baseline.

R13 must NOT redesign V4.

Required principle:

```text
VALIDATE_AND_HARDEN_EXISTING_CONTRACTS
DO_NOT_REDEFINE_THEM
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
8. every approved V4 result/closure document from R1 through R12
9. every V4 contract/example artifact from R1 through R12
10. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
11. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Inspect the current production packages under:

```text
legacy_documenter/knowledge/
```

including at minimum:

```text
domain/
input/
provenance/
ingestion/
classification/
temporal/
relations/
proposals/
approval/
canonical/
projection/
plugin_projection/
```

Also inspect existing security/sanitization/determinism utilities already used by V3/V4.

Do not duplicate existing validation mechanisms unless required to validate a new cross-round invariant.

---

# Entry Gate

Before implementation verify:

```text
latest_completed_round = V4-R12
latest_approved_round = V4-R12

current_round_in_progress = null

round_status = V4-R12_APPROVED

next = V4-R13

tests = 1288

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

If R12 is not formally closed:

STOP.

If unrelated user work exists:

STOP and report.

Do not silently reconcile repository state.

---

# R13 Scope

R13 must validate the full V4 architecture.

It may add:

* regression tests;
* security tests;
* deterministic invariant tests;
* contract-consistency tests;
* static checks;
* narrowly-scoped defensive guards;
* deterministic validation/report tooling.

R13 may fix a clearly demonstrated defect only when:

1. the defect violates an already-approved V4 contract;
2. the expected behavior is unambiguous from approved artifacts;
3. the fix is minimal;
4. no contract redesign is required;
5. tests prove the defect and the fix.

If a discovered problem requires a design decision or semantic change:

STOP.

Do not silently redesign approved behavior.

Report it for Technical Lead review.

---

# Core Architectural Invariants

Validate all of the following.

## LegacyMapper Role

```text
LEGACYMAPPER_CONSTRUCTS_KNOWLEDGE
PLUGIN_CONSUMES_KNOWLEDGE
```

LegacyMapper must not contain Plugin autonomous-runtime behavior.

---

## One Canonical Knowledge Source

Required:

```text
ONE_CANONICAL_KNOWLEDGE_SOURCE
```

R10 remains the canonical approved Knowledge Source.

R11 and R12 are projections.

Required topology:

```text
                  R10
        Canonical Knowledge Source
                  │
          ┌───────┴────────┐
          ↓                ↓
         R11              R12
  Human-readable      Machine-readable
```

Forbidden:

```text
R10 → R11 → R12
R10 → R12 → R11
R11 = canonical source
R12 = canonical source
```

---

# Source Code Optionality

Validate end-to-end that V4 supports:

```text
CODE_ONLY
CODE_AND_HUMAN_INFORMATION
HUMAN_INFORMATION_ONLY
PARTIAL_INFORMATION
```

No common V4 knowledge object may require:

```text
repository path
project path
symbol
method
language
framework
assembly
database
source-code location
```

unless that information is explicitly part of the source material itself.

Required:

```text
SOURCE_CODE_OPTIONAL=true
```

---

# Authority Boundary

Validate:

```text
TECHNICAL_LEAD_IS_FINAL_APPROVAL_AUTHORITY
```

No code path may:

* auto-approve;
* AI-approve;
* provider-approve;
* system-approve;
* infer approval from status;
* infer approval from provenance;
* infer approval from canonical inclusion.

Required:

```text
AI_NEVER_GRANTS_APPROVAL
SYSTEM_NEVER_GRANTS_APPROVAL
```

R9 remains the approval boundary.

---

# Provenance Boundary

Validate:

```text
PROVENANCE != APPROVAL
PROVENANCE != AUTHORITY
PROVENANCE != STATUS
PROVENANCE != TRUTH
```

An AI-originated interpretation later approved by Technical Lead must still retain AI-origin provenance.

Approval must not rewrite origin.

---

# Status Boundary

Validate:

```text
APPROVED != CONFIRMED
```

Approval eligibility and knowledge status remain separate concepts.

Ensure no path silently promotes:

```text
PARTIAL
INTERPRETED
UNRESOLVED
CONFLICTING
MISSING
SUPERSEDED
```

to `CONFIRMED`.

---

# Temporal Boundary

Validate exact preservation of:

```text
AS_IS
TO_BE
HISTORICAL
UNSPECIFIED / None
```

Forbidden automatic semantics:

```text
HISTORICAL => SUPERSEDED
TO_BE => CURRENT
None => AS_IS
AS_IS + TO_BE => CONFLICT
```

unless already explicitly represented by approved data.

---

# Relation Boundary

Validate R7 semantics.

Required relation taxonomy remains explicit:

```text
DIFFERENCE
GAP
CONFLICT
TEMPORAL_EVOLUTION
```

No semantic auto-detection may have appeared after R7.

No later stage may silently convert a relation into approved truth.

---

# Proposal Boundary

Validate R8.

Proposal lifecycle remains:

```text
DRAFT
READY_FOR_REVIEW
WITHDRAWN
SUPERSEDED
```

Validate:

```text
READY_FOR_REVIEW != APPROVED
WITHDRAWN != REJECTED
SUPERSEDED requires explicit transition
```

No later package may mutate proposal status implicitly.

---

# Approval Boundary

Validate R9:

```text
APPROVED
REJECTED
CORRECTION_REQUESTED
```

Only:

```text
authority = TECHNICAL_LEAD
```

may produce an approval decision.

Validate:

```text
CORRECTION_REQUESTED != REJECTED
REJECTED != FALSE
APPROVED != CONFIRMED
```

---

# Canonical Composition Boundary

Validate R10.

Only eligible proposal + matching Technical Lead approval may enter canonical composition.

Canonical entries must preserve:

```text
proposal_id
approval_decision_id
source_type
nature
status
temporal_state
evidence_refs
provenance
related_statement_ids
```

No canonical identity recomputation instability.

Required prefix:

```text
KNO-
```

No duplicate canonical identity.

No automatic:

```text
supersession
gap resolution
conflict resolution
status promotion
temporal inference
```

---

# R11 Human Projection Boundary

Validate R11.

R11 remains projection-only.

Required:

```text
R11_SOURCE=R10_CANONICAL_KNOWLEDGE
CANONICAL_INPUT_MUTATION=NONE
```

Mapping must remain structured.

Forbidden:

```text
statement-text semantic routing
AI document routing
free-text inference
```

Validate:

```text
unmapped canonical knowledge preserved/reported
multi-projection allowed
statement rendered verbatim
KNO traceability present
empty document policy deterministic
```

---

# R12 Plugin Projection Boundary

Validate R12.

Required:

```text
R12_SOURCE=R10_CANONICAL_KNOWLEDGE
R11_DEPENDENCY=NONE
ALL_CANONICAL_ENTRIES_PROJECTED
SILENT_ENTRY_OMISSION=FORBIDDEN
PLUGIN_ENTRY_ID=CANONICAL_KNOWLEDGE_ID
```

Validate:

```text
LegacyMapperPluginKnowledge
contract_version=1.0
```

Ensure:

```text
R12_DOES_NOT_IMPLEMENT_PLUGIN_RUNTIME
```

No agents, orchestration, execution, project modification, prompt execution, provider/model routing.

---

# Metadata Boundary

Validate R12 approved policy:

```text
CANONICAL_METADATA_DEFAULT=NOT_PROJECTED
```

Ensure arbitrary metadata cannot silently become Plugin API.

Ensure R11-specific metadata does not affect R12.

---

# Determinism

Perform cross-round determinism review.

Validate no V4 deterministic artifact depends on:

```text
current time
random UUID
runtime object identity
machine-specific absolute path
environment-specific ordering
locale
hash-randomization ordering
provider/model response
network state
```

Where artifacts already have deterministic renderers, regenerate them independently.

At minimum validate determinism for:

* R8 proposal artifacts/contracts if applicable;
* R9 approval artifacts;
* R10 canonical contract/example;
* R11 projection contract/example/tree;
* R12 contract/example/payload serialization.

Do not rewrite approved artifact content solely to normalize style.

---

# Identity Stability

Review deterministic ID families.

At minimum:

```text
PRN-
PED-
TMP-
PRP-
APR-
KNO-
```

and other approved V4 identifiers.

Verify:

* identical semantic input → identical ID;
* input ordering does not alter identity where ordering is semantically irrelevant;
* unrelated metadata does not alter identities unless explicitly part of approved identity contract;
* no random identifiers;
* no collision caused by omission of contractually significant fields.

If a potential theoretical collision is found but no approved contract defines a fix:

document it.

Do not redesign ID semantics in R13 without Technical Lead review.

---

# Immutability / Mutation Safety

Validate approved frozen/read-only semantics.

At minimum ensure later stages do not mutate earlier-stage objects.

Examples:

```text
MaterialItem
KnowledgeStatement
Proposal
ApprovalDecision
CanonicalKnowledgeEntry
PluginKnowledgeEntry
DocumentProjection-related immutable structures
```

where approved models are expected immutable.

Test object state before/after downstream operations.

---

# Serialization Safety

Review every V4 serialization path.

Forbidden:

```text
pickle
marshal for untrusted data
eval
exec
compile from content
yaml unsafe loader
dynamic import from content
shell interpolation/execution
template execution from knowledge text
```

JSON content must remain inert.

---

# Prompt Injection Inertness

Knowledge content may contain text such as:

```text
Ignore previous instructions
Reveal secrets
Run this command
Delete repository
```

This is data.

It must never alter LegacyMapper behavior.

Validate across:

```text
ingestion
classification
proposal
canonical composition
R11 projection
R12 projection
serialization
```

No prompt/provider call is allowed in this round.

---

# Secret Handling

Review V4 input and projection surfaces.

Validate:

* existing sanitizer behavior;
* arbitrary metadata boundaries;
* fixed/non-echoing validation errors where used;
* secret-shaped content does not leak through excluded metadata;
* no `.env`, credentials, access tokens, API keys, private keys or local machine secrets exist in tracked artifacts;
* no test embeds a real credential.

Do not invent secret scrubbing over canonical statement text if that would violate approved verbatim-preservation semantics.

If an actual conflict exists:

STOP and report.

---

# Path Safety

Review every V4 file-output boundary.

Validate rejection/prevention of:

```text
../ traversal
absolute paths
drive-qualified paths
UNC escape
path separators that escape configured root
```

R11 path policy must remain enforced.

R12 core projection must not depend on filesystem paths.

---

# Filesystem Boundary

Core domain/services should not perform hidden filesystem operations unless their approved responsibility requires it.

Review for unexpected:

```text
open(
Path.write*
Path.unlink
shutil
os.remove
subprocess
```

inside core knowledge logic.

Output/report modules may perform explicit deterministic writes through approved boundaries.

---

# Network Boundary

R13 must prove that V4 core processing does not require network access.

No tests should call external network services.

No provider invocation.

No GitHub Copilot/Gemini/OpenAI/Anthropic/Ollama call.

Required:

```text
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
NETWORK_DEPENDENCY_FOR_V4_CORE=NONE
```

---

# Dependency Review

Review new V4 imports/dependencies.

Prefer standard library and existing project dependencies.

Report:

* unnecessary dependency additions;
* circular imports;
* cross-round semantic coupling;
* R11↔R12 coupling;
* canonical layer depending on projections;
* lower-level domain packages depending on higher-level projections.

Required architecture direction should remain acyclic.

At minimum:

```text
domain
  ↑
input/provenance/ingestion/classification/temporal/relations
  ↑
proposals
  ↑
approval
  ↑
canonical
  ↑
projection / plugin_projection
```

Exact module dependencies may vary, but lower layers must not depend semantically on projections.

---

# Import Cycle Validation

Run/import all V4 modules independently.

Ensure no circular-import failure.

Optionally use a deterministic static import graph if simple to implement.

Do not introduce a large new dependency only for graph visualization.

---

# Exception Safety

Review public/service boundaries.

Validate that malformed external data fails:

```text
explicitly
deterministically
without partial mutation
without leaking secret-shaped input
```

Do not catch broad exceptions merely to hide programmer defects.

Do not rewrite all historical V3 exception handling in R13.

---

# JSON Compatibility

Validate all machine-readable V4 output contains JSON-compatible values only.

Reject or normalize according to already-approved contracts.

No silent `str(object)` fallback for arbitrary objects.

---

# Unicode

Test representative Unicode content.

At minimum:

```text
Spanish accents
ñ
symbols
non-ASCII text
```

Ensure deterministic UTF-8 JSON/Markdown behavior.

Do not ASCII-lossily normalize approved content.

---

# Large Input Defensive Tests

Add modest deterministic stress cases where useful.

Examples:

* many canonical entries;
* repeated evidence references;
* many related IDs;
* long inert statement text.

Purpose:

```text
detect accidental quadratic/explosive behavior
```

Do not conduct performance optimization unless an actual defect is demonstrated.

Do not create massive repository artifacts.

---

# Cross-Projection Consistency

For identical canonical input:

R11 and R12 may format differently but must point back to the same canonical IDs.

Validate:

```text
R11_KNOWLEDGE_IDS ⊆ R10_KNOWLEDGE_IDS
R12_KNOWLEDGE_IDS == R10_KNOWLEDGE_IDS
```

R11 may legitimately have unmapped items.

R12 may not.

No projection may invent a `KNO-` ID.

---

# Traceability

Validate end-to-end traceability for representative canonical items:

```text
Material / Evidence
       ↓
Proposal
       ↓
ApprovalDecision
       ↓
CanonicalKnowledgeEntry KNO-
       ↓
R11 and/or R12
```

Traceability must not imply that every stage necessarily exists for every source unless approved contracts require it.

No invented evidence.

---

# Human-Information-Only End-to-End Scenario

Create or reuse a deterministic test demonstrating:

```text
human material
→ ingestion
→ classification
→ proposal
→ Technical Lead approval fixture
→ canonical composition
→ R11/R12 projections
```

without any:

```text
source repository
VB.NET file
symbol
method
framework
database
project path
```

No AI calls.

Use explicit synthetic data.

---

# Mixed-Source Scenario

Validate a deterministic scenario combining:

```text
DETERMINISTIC_CODE_FACT
HUMAN_REQUIREMENT
BUSINESS_CONTEXT
TECHNICAL_CONSTRAINT
AI_INTERPRETATION
```

where provenance and approval remain distinct.

Do not use AI to generate the interpretation fixture.

Create it as explicit synthetic test data.

---

# Regression Matrix

Produce a formal matrix for V3 and every V4 round.

At minimum:

```text
V3
V4-R1
V4-R2
V4-R3
V4-R4
V4-R5
V4-R6
V4-R7
V4-R8
V4-R9
V4-R10
V4-R11
V4-R12
```

For each record:

```text
round
tests
contract_status
security_status
determinism_status
regression_status
notes
```

Historical rounds need not be re-generated if current tests prove their invariants.

---

# Security Invariant Registry

Create a deterministic registry of important security/authority invariants.

Examples:

```text
TECHNICAL_LEAD_ONLY_APPROVAL
AI_CANNOT_APPROVE
NO_PROVIDER_CALLS
NO_AUTO_STATUS_PROMOTION
NO_CANONICAL_MUTATION_FROM_PROJECTIONS
R11_PATH_TRAVERSAL_FORBIDDEN
R12_ARBITRARY_METADATA_NOT_PROJECTED
PROMPT_INJECTION_IS_INERT_DATA
NO_DYNAMIC_EXECUTION
NO_UNSAFE_DESERIALIZATION
NO_SECRET_FILES_IN_ARTIFACTS
SOURCE_CODE_OPTIONAL
PLUGIN_RUNTIME_NOT_IMPLEMENTED
```

Each invariant must report:

```text
PASS
FAIL
NOT_APPLICABLE
```

Use `NOT_APPLICABLE` only when genuinely justified.

Do not report `PASS` merely because a test is missing.

---

# Static Security Review

Inspect production Python files involved in V4 for risky primitives.

Search at minimum for:

```text
eval(
exec(
compile(
pickle
marshal
subprocess
os.system
Popen
shell=True
__import__(
importlib
yaml.load
requests
urllib
socket
```

Context matters.

Do not fail merely because a safe import exists elsewhere in the repository.

The R13 report should explain relevant findings.

---

# Artifact Integrity

Recompute hashes of approved V4 deterministic artifacts where stored/referenced by closure records.

At minimum verify R10, R11, R12 reviewed artifacts.

Do not change reviewed artifacts.

If hash mismatch is found:

STOP.

Do not regenerate over an approved artifact and continue.

Required:

```text
APPROVED_ARTIFACT_INTEGRITY=PASS
```

---

# Git / Repository Security Review

Do not commit in this implementation round.

Inspect:

```text
.gitignore
git status
tracked file list
```

Validate no obvious:

```text
.env
credential
token dump
local virtualenv
cache
large generated artifact
secret key
```

was accidentally introduced by V4.

Do not scan or report secret values themselves.

Use fixed/redacted descriptions.

---

# Technical Debt Review

R13 must produce an updated technical-debt list.

Include:

* unresolved debt carried from V3;
* new V4 maintainability debt;
* files/classes with high complexity;
* repeated serialization/validation logic;
* documentation/type-hint gaps;
* large orchestrators;
* safe future refactor candidates.

IMPORTANT:

Do not perform the comprehensive readability refactor now.

The Technical Lead has explicitly requested a dedicated maintainability/readability refactor after V4 closes.

Record that as a post-V4 planned activity.

Suggested label:

```text
POST_V4_MAINTAINABILITY_REFACTOR=PLANNED
```

R13 may fix security/regression defects.

It must NOT turn into the readability refactor.

---

# Python Maintainability Review

Without refactoring behavior, collect useful metrics/observations for the future maintainability phase.

Examples:

```text
production Python module count
largest production modules
largest classes/functions
docstring coverage estimate
public type-hint coverage estimate
duplicated serialization/report patterns
cross-package helper duplication
broad exception boundaries
files with mixed responsibilities
```

Keep metrics deterministic and reproducible where practical.

Do not install a large analysis framework solely for this.

This section is diagnostic only.

---

# Required New Tests

Add focused R13 tests.

Prefer:

```text
tests/test_v4_r13_regression_and_security.py
```

or a small clear test package if necessary.

Do not scatter dozens of tiny files without benefit.

Required coverage includes:

1. all authority invariants;
2. no AI/system auto-approval;
3. canonical immutability;
4. source code optionality;
5. human-only flow;
6. mixed-source flow;
7. status preservation;
8. temporal preservation;
9. provenance vs approval separation;
10. R11/R12 sibling relationship;
11. no R11→R12 dependency;
12. projection ID consistency;
13. path traversal rejection;
14. arbitrary metadata exclusion from R12;
15. prompt injection inertness;
16. no dynamic execution primitives in V4 core;
17. deterministic artifacts;
18. deterministic IDs;
19. JSON compatibility;
20. Unicode preservation;
21. approved artifact hash integrity;
22. import cycle/basic module import health;
23. no provider/model calls;
24. no Plugin runtime symbols;
25. repository continuity state.

---

# Defect Classification

Any discovered problem must be classified:

```text
SECURITY_DEFECT
REGRESSION_DEFECT
CONTRACT_VIOLATION
DETERMINISM_DEFECT
TRACEABILITY_DEFECT
MAINTAINABILITY_DEBT
DOCUMENTATION_DEBT
OUT_OF_SCOPE_DESIGN_QUESTION
```

For each defect record:

```text
id
classification
severity
affected_round
affected_file
description
evidence
resolution
status
```

Allowed statuses:

```text
FIXED_IN_R13
DEFERRED_TO_POST_V4_REFACTOR
REQUIRES_TECHNICAL_LEAD_DECISION
NOT_A_DEFECT
```

Security or contract defects requiring semantic redesign must not be silently fixed.

---

# Severity

Use:

```text
CRITICAL
HIGH
MEDIUM
LOW
INFORMATIONAL
```

Do not exaggerate severity.

A maintainability issue alone is not `CRITICAL`.

---

# Security Gate

R13 may only be marked ready for human review if:

```text
CRITICAL_OPEN=0
HIGH_OPEN=0
```

and any open MEDIUM/LOW items are clearly documented and do not violate approved contracts.

Prefer:

```text
SECURITY_GATE=PASS
```

---

# Regression Gate

Require:

```text
V3_REGRESSION=PASS
V4_R1_REGRESSION=PASS
V4_R2_REGRESSION=PASS
V4_R3_REGRESSION=PASS
V4_R4_REGRESSION=PASS
V4_R5_REGRESSION=PASS
V4_R6_REGRESSION=PASS
V4_R7_REGRESSION=PASS
V4_R8_REGRESSION=PASS
V4_R9_REGRESSION=PASS
V4_R10_REGRESSION=PASS
V4_R11_REGRESSION=PASS
V4_R12_REGRESSION=PASS
```

---

# Full Test Suite

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>1288 PASS
```

No pre-existing tests may be removed or skipped merely to satisfy R13.

Run readiness.

Require:

```text
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

---

# Required Artifacts

Create:

```text
output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json
```

and:

```text
output/v4_r13/V4_SECURITY_INVARIANTS.json
```

Both must be deterministic.

---

# V4_REGRESSION_SECURITY_REPORT.json

Include at minimum:

```text
round
status

baseline_tests
final_tests

regression_matrix

artifact_integrity
determinism

defects

open_defect_counts_by_severity

security_gate
regression_gate

readiness

provider_calls
real_llm_calls

post_v4_maintainability_refactor
```

Do not include timestamps.

---

# V4_SECURITY_INVARIANTS.json

Include structured invariant records:

```text
invariant_id
description
status
evidence
```

Avoid embedding full source files or secret-shaped test data.

---

# Determinism

Generate both R13 artifacts twice independently.

Require:

```text
REGRESSION_SECURITY_REPORT_DETERMINISM=PASS
SECURITY_INVARIANTS_DETERMINISM=PASS
```

---

# PROJECT_STATE After Successful R13 Implementation

Update using existing schema:

```text
latest_completed_round = V4-R13
latest_approved_round = V4-R12

current_round_in_progress =
"V4-R13 (pending Technical Lead review)"

round_status =
V4-R13_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R13

tests = <actual count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do NOT mark R13 approved.

---

# Required Result Document

Create:

```text
docs/V4/V4_R13_REGRESSION_AND_SECURITY_RESULT.md
```

Report at minimum:

```text
STATUS
ENTRY_GATE

BASELINE_TESTS
FINAL_TESTS

SECURITY_GATE
REGRESSION_GATE

CRITICAL_OPEN
HIGH_OPEN
MEDIUM_OPEN
LOW_OPEN

APPROVED_ARTIFACT_INTEGRITY

ONE_CANONICAL_KNOWLEDGE_SOURCE
TECHNICAL_LEAD_ONLY_APPROVAL
SOURCE_CODE_OPTIONAL
PROVENANCE_APPROVAL_SEPARATION
APPROVED_NOT_CONFIRMED
TEMPORAL_SEMANTICS
RELATION_SEMANTICS
PROPOSAL_BOUNDARY
APPROVAL_BOUNDARY
CANONICAL_BOUNDARY
R11_BOUNDARY
R12_BOUNDARY
R11_R12_SIBLING_PROJECTIONS

PROMPT_INJECTION_INERTNESS
DYNAMIC_EXECUTION
UNSAFE_DESERIALIZATION
PATH_SAFETY
SECRET_HANDLING
NETWORK_DEPENDENCY
PLUGIN_RUNTIME
PROVIDER_BOUNDARY

DETERMINISM
IDENTITY_STABILITY
JSON_COMPATIBILITY
UNICODE

HUMAN_ONLY_FLOW
MIXED_SOURCE_FLOW
TRACEABILITY

IMPORT_HEALTH
DEPENDENCY_DIRECTION

REGRESSION_SECURITY_REPORT
REGRESSION_SECURITY_REPORT_SHA256

SECURITY_INVARIANTS
SECURITY_INVARIANTS_SHA256

REGRESSION_SECURITY_REPORT_DETERMINISM
SECURITY_INVARIANTS_DETERMINISM

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
V4_R12_REGRESSION

READINESS
AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PRODUCTION_BEHAVIOR_CHANGED

FIXED_DEFECTS
DEFERRED_DEBT
TECHNICAL_DEBT

POST_V4_MAINTAINABILITY_REFACTOR

PROJECT_STATE

DECISION
NEXT
```

---

# Expected Success State

```text
STATUS=V4_R13_REGRESSION_AND_SECURITY_COMPLETE

ENTRY_GATE=PASS

FINAL_TESTS=>1288_PASS

SECURITY_GATE=PASS
REGRESSION_GATE=PASS

CRITICAL_OPEN=0
HIGH_OPEN=0

APPROVED_ARTIFACT_INTEGRITY=PASS

ONE_CANONICAL_KNOWLEDGE_SOURCE=PASS
TECHNICAL_LEAD_ONLY_APPROVAL=PASS
SOURCE_CODE_OPTIONAL=PASS

PROVENANCE_APPROVAL_SEPARATION=PASS
APPROVED_NOT_CONFIRMED=PASS
TEMPORAL_SEMANTICS=PASS
RELATION_SEMANTICS=PASS

PROPOSAL_BOUNDARY=PASS
APPROVAL_BOUNDARY=PASS
CANONICAL_BOUNDARY=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS
R11_R12_SIBLING_PROJECTIONS=PASS

PROMPT_INJECTION_INERTNESS=PASS
DYNAMIC_EXECUTION=PASS
UNSAFE_DESERIALIZATION=PASS
PATH_SAFETY=PASS
SECRET_HANDLING=PASS

NETWORK_DEPENDENCY_FOR_V4_CORE=NONE
PLUGIN_RUNTIME=NOT_IMPLEMENTED

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

DETERMINISM=PASS
IDENTITY_STABILITY=PASS
JSON_COMPATIBILITY=PASS
UNICODE=PASS

HUMAN_ONLY_FLOW=PASS
MIXED_SOURCE_FLOW=PASS
TRACEABILITY=PASS

IMPORT_HEALTH=PASS
DEPENDENCY_DIRECTION=PASS

REGRESSION_SECURITY_REPORT_DETERMINISM=PASS
SECURITY_INVARIANTS_DETERMINISM=PASS

V3_REGRESSION=PASS
V4_R1_REGRESSION=PASS
V4_R2_REGRESSION=PASS
V4_R3_REGRESSION=PASS
V4_R4_REGRESSION=PASS
V4_R5_REGRESSION=PASS
V4_R6_REGRESSION=PASS
V4_R7_REGRESSION=PASS
V4_R8_REGRESSION=PASS
V4_R9_REGRESSION=PASS
V4_R10_REGRESSION=PASS
V4_R11_REGRESSION=PASS
V4_R12_REGRESSION=PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

POST_V4_MAINTAINABILITY_REFACTOR=PLANNED

PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW

DECISION=V4_R13_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_R13
```

---

# Stop Condition

After validation, any narrowly justified hardening fixes, tests, deterministic artifacts and result documentation:

STOP.

Do NOT:

* approve R13;
* commit;
* push;
* begin R14;
* perform the comprehensive readability/maintainability refactor;
* implement Plugin runtime;
* call any AI/provider;
* redesign approved V4 contracts.

The next action is:

```text
HUMAN_REVIEW_V4_R13
```
