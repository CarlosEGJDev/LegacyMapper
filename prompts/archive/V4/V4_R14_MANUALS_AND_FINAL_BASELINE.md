# LegacyMapper V4 — R14 Manuals and Final Baseline

TASK=V4_R14_MANUALS_AND_FINAL_BASELINE

MODE=DOCUMENTATION_CONSOLIDATION_AND_FINAL_BASELINE

IMPLEMENTATION_ALLOWED=true

SEMANTIC_REDESIGN_ALLOWED=false
COMPREHENSIVE_REFACTOR_ALLOWED=false

REAL_LLM_CALLS_ALLOWED=false
PROVIDER_CALLS_ALLOWED=false

GIT_COMMIT_ALLOWED=false
GIT_PUSH_ALLOWED=false

---

# Objective

Implement the final V4 implementation round:

```text id="6n56ks"
V4-R14 — Manuals and Final Baseline
```

R14 must consolidate LegacyMapper V4 into a repository-authoritative, agent-neutral, human-maintainable checkpoint.

The objective is NOT to add another knowledge capability.

The objective is to ensure that after V4:

1. a Technical Lead can understand how LegacyMapper is intended to be used;
2. a developer can understand the V4 architecture and its boundaries;
3. a fresh AI development agent can resume work from repository artifacts alone;
4. V4 contracts and approved decisions are discoverable;
5. operational/recovery procedures are documented;
6. the complete V4 test/security/regression state is captured deterministically;
7. a final V4 baseline exists;
8. the repository clearly distinguishes LegacyMapper from the future Plugin;
9. the planned post-V4 maintainability/readability refactor is explicitly recorded;
10. V4 can be submitted to the Technical Lead for final human review and formal closure.

Required principle:

```text id="acofz2"
DOCUMENT_AND_BASELINE_EXISTING_APPROVED_BEHAVIOR
DO_NOT_REDESIGN_IT
```

---

# Entry Gate

Before making changes, verify:

```text id="y2t6j0"
latest_completed_round = V4-R13
latest_approved_round = V4-R13

current_round_in_progress = null

round_status = V4-R13_APPROVED

next = V4-R14

tests = 1335

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Run:

```text id="cf36g4"
git status
```

Expected:

```text id="vk3dvl"
CLEAN
```

The new R14 prompt itself may be the only expected untracked file.

If unrelated work exists:

STOP.

If R13 is not formally closed:

STOP.

---

# Required Reading

Read repository authority before writing documentation.

At minimum:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/GENERATED_ARTIFACT_POLICY.md`
6. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`
7. `docs/V4/V4_CONTRACT_FOUNDATION.md`
8. `docs/V4/V4_AI_HANDOVER.md`
9. `docs/V4/V4_PROPOSED_ROADMAP.md`
10. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
11. all approved V4 result and closure records through R13;
12. R10 canonical contract/example;
13. R11 human-readable projection contract/example;
14. R12 Plugin-facing contract/example;
15. R13 regression/security artifacts.

Inspect the current V4 production packages.

Do not derive current behavior from conversation history.

Repository artifacts are authoritative.

---

# V4 Final Architecture

Documentation must preserve the approved architecture:

```text id="u02psg"
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
R11         R12
Human       Plugin-facing
projection  machine projection
```

Do not imply that every input necessarily passes through every conceptual stage if approved contracts allow otherwise.

Required:

```text id="v4canon"
ONE_CANONICAL_KNOWLEDGE_SOURCE
```

R11 and R12 are projections.

Neither is a second canonical source.

---

# Product Boundary

Documentation must clearly state:

```text id="lmpboundary"
LEGACYMAPPER_CONSTRUCTS_KNOWLEDGE
PLUGIN_CONSUMES_KNOWLEDGE
```

LegacyMapper V4 does NOT implement:

```text id="noruntime"
Plugin runtime
autonomous agents
orchestration
task planning
code generation
project modification
model routing
provider routing
autonomous execution
```

R12 only defines the machine-readable consumption contract.

---

# Technical Lead Authority

Document:

```text id="tlauth"
TECHNICAL_LEAD_IS_FINAL_APPROVAL_AUTHORITY
```

The Technical Lead is the controlled operator and sole final approval authority for incorporation into canonical knowledge.

Do not introduce enterprise RBAC.

Do not describe AI as an approval authority.

Preserve:

```text id="aiauth"
AI_NEVER_GRANTS_APPROVAL
SYSTEM_NEVER_GRANTS_APPROVAL
```

---

# Source Code Optionality

Documentation must explicitly explain that V4 supports:

```text id="v4modes"
CODE_ONLY
CODE_AND_HUMAN_INFORMATION
HUMAN_INFORMATION_ONLY
PARTIAL_INFORMATION
```

Source code is optional.

The common V4 knowledge model is not VB.NET-specific.

Existing V1/V2 legacy extraction remains valid for deterministic code facts.

True extraction-level language/framework/project-layout agnosticism remains outside V4 and belongs to future V5 planning.

Do not claim V5 has been implemented.

---

# Knowledge Semantics

Document the distinction between:

```text id="stages"
MATERIAL
EVIDENCE
INTERPRETATION
PROPOSAL
APPROVED_KNOWLEDGE
```

where applicable.

Explicitly preserve:

```text id="boundaries"
MATERIAL != APPROVED_KNOWLEDGE

PROVENANCE != APPROVAL
PROVENANCE != AUTHORITY
PROVENANCE != STATUS

APPROVED != CONFIRMED

AI_INTERPRETATION != FACT
```

Explain that Technical Lead approval authorizes incorporation but does not automatically change a knowledge status to `CONFIRMED`.

---

# Temporal Semantics

Document:

```text id="temporal"
AS_IS
TO_BE
HISTORICAL
UNSPECIFIED
```

No automatic inference.

Do not document:

```text id="badtemporal"
HISTORICAL => SUPERSEDED
None => AS_IS
TO_BE => CURRENT
AS_IS + TO_BE => CONFLICT
```

as automatic behavior.

---

# Relations

Document approved relation vocabulary:

```text id="relations"
DIFFERENCE
GAP
CONFLICT
TEMPORAL_EVOLUTION
```

Relations are explicit.

LegacyMapper does not automatically infer semantic conflicts merely because AS_IS and TO_BE differ.

---

# Proposal and Approval Lifecycle

Document R8 proposal states:

```text id="proposalstates"
DRAFT
READY_FOR_REVIEW
WITHDRAWN
SUPERSEDED
```

Preserve:

```text id="proposalrules"
READY_FOR_REVIEW != APPROVED
WITHDRAWN != REJECTED
```

Document R9 decisions:

```text id="approvaldecisions"
APPROVED
REJECTED
CORRECTION_REQUESTED
```

Preserve:

```text id="approvalrules"
CORRECTION_REQUESTED != REJECTED
REJECTED != FALSE
APPROVED != CONFIRMED
```

---

# Canonical Knowledge

Document R10 as the canonical composition boundary.

Explain:

```text id="knoprefix"
CanonicalKnowledgeEntry
KNO-
```

A canonical entry must remain traceable to its proposal and approval decision according to the approved R10 contract.

Do not describe R11 Markdown or R12 JSON as canonical knowledge stores.

---

# Human-Readable Projection

Document R11.

Required:

```text id="r11docs"
R11_SOURCE=R10_CANONICAL_KNOWLEDGE
R11_IS_PROJECTION=true
```

Explain:

* deterministic document routing;
* structured rules;
* no statement-text semantic routing;
* unmapped knowledge remains reported;
* one canonical item may project to multiple documents;
* `KNO-` traceability is preserved;
* statement is rendered verbatim;
* empty-document behavior is deterministic.

Document the approved 00–09 document families sufficiently for future maintenance.

Do not create a second truth hierarchy.

---

# Plugin-Facing Projection

Document R12.

Required:

```text id="r12docs"
CONTRACT_NAME=LegacyMapperPluginKnowledge
CONTRACT_VERSION=1.0

R12_SOURCE=R10_CANONICAL_KNOWLEDGE
R11_DEPENDENCY=NONE

PLUGIN_PAYLOAD_IS_PROJECTION
PLUGIN_PAYLOAD_IS_NOT_CANONICAL_KNOWLEDGE

ALL_CANONICAL_ENTRIES_PROJECTED
SILENT_ENTRY_OMISSION=FORBIDDEN

PLUGIN_ENTRY_ID=CANONICAL_KNOWLEDGE_ID
```

Explain compatibility policy.

Document:

```text id="metapolicy"
CANONICAL_METADATA_DEFAULT=NOT_PROJECTED
```

Do not document arbitrary metadata as part of the Plugin API.

---

# Security Model

Document the V4 security model established and validated by R13.

At minimum:

```text id="secmodel"
TECHNICAL_LEAD_ONLY_APPROVAL
AI_CANNOT_APPROVE
NO_PROVIDER_CALLS_IN_DETERMINISTIC_V4_CORE
NO_AUTO_STATUS_PROMOTION
NO_CANONICAL_MUTATION_FROM_PROJECTIONS
R11_PATH_TRAVERSAL_FORBIDDEN
R12_ARBITRARY_METADATA_NOT_PROJECTED
PROMPT_INJECTION_IS_INERT_DATA
NO_DYNAMIC_EXECUTION
NO_UNSAFE_DESERIALIZATION
SOURCE_CODE_OPTIONAL
PLUGIN_RUNTIME_NOT_IMPLEMENTED
```

Do not overstate security guarantees beyond what R13 validated.

---

# Determinism

Document deterministic behavior and identity families.

At minimum cover:

```text id="ids"
PRN-
PED-
TMP-
PRP-
APR-
KNO-
```

and other relevant approved IDs.

Explain that deterministic artifacts avoid runtime timestamps/random UUIDs/machine identity/environment-dependent ordering where the approved contracts require determinism.

---

# Manuals

Create a small, purposeful set of final V4 manuals.

Do NOT create dozens of tiny documents.

Preferred files:

```text id="manualpaths"
docs/V4/V4_USER_MANUAL.md
docs/V4/V4_DEVELOPER_MANUAL.md
docs/V4/V4_OPERATIONS_AND_RECOVERY_MANUAL.md
docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md
```

If existing repository documentation already fulfills one of these responsibilities, update/reuse it rather than duplicating it.

Any deviation from these filenames must be justified in the R14 result.

---

# V4_USER_MANUAL.md

Audience:

```text id="useraud"
Technical Lead / controlled LegacyMapper operator
```

Explain practically:

* what LegacyMapper does;
* what it does not do;
* supported input modes;
* how human information fits;
* role of deterministic code facts;
* proposal/review/approval concept;
* Technical Lead responsibility;
* canonical Knowledge Source;
* human-readable outputs;
* Plugin-facing output;
* handling partial/unresolved information;
* provenance;
* AS_IS/TO_BE/HISTORICAL;
* safe operational expectations.

Do not invent a CLI if one does not exist.

Do not describe commands that the repository does not actually support.

---

# V4_DEVELOPER_MANUAL.md

Audience:

```text id="devaud"
future human developer or AI development agent
```

Explain:

* repository authority hierarchy;
* package architecture;
* responsibilities of V4 packages;
* allowed dependency direction;
* immutable/read-only boundaries;
* deterministic IDs;
* source code optionality;
* approval boundary;
* canonical composition;
* R11/R12 sibling projections;
* security constraints;
* Python development standard;
* testing expectations;
* how to add a new feature without bypassing contracts;
* how to recognize when a change requires Technical Lead decision.

Include concrete repository paths.

Do not depend on chat history.

---

# V4_OPERATIONS_AND_RECOVERY_MANUAL.md

Explain:

* startup/recovery reading order;
* `PROJECT_STATE.json`;
* readiness;
* full regression command;
* repository cleanliness;
* generated artifact policy;
* reviewed artifact integrity;
* Git safety;
* secret safety;
* how to resume after interrupted AI work;
* how to identify latest approved round;
* what must never be reconstructed from memory when repository evidence exists;
* how to distinguish pending implementation from approved checkpoint.

Reuse `docs/PROJECT_RECOVERY.md` rather than contradicting it.

---

# V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md

This is a concise technical reference, not another narrative manual.

Include:

* architecture diagram;
* R1–R14 responsibility summary;
* source types;
* knowledge natures;
* knowledge statuses;
* temporal states;
* relation types;
* proposal states/methods/kinds;
* approval decisions/authority;
* canonical entry structure;
* R11 projection boundary;
* R12 contract boundary;
* Plugin contract name/version;
* important deterministic ID prefixes;
* key security invariants;
* V5 boundary.

All values must come from actual approved repository contracts.

If the repository differs from remembered/conversational values:

repository wins.

Report the discrepancy rather than silently choosing conversation memory.

---

# Repository Authority / AI Handover

Review and, where necessary, update:

```text id="handoverdocs"
CLAUDE.md
AGENTS.md
PROJECT_STATE.json
docs/V4/V4_AI_HANDOVER.md
docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md
```

Goal:

a fresh Claude, Codex, or future AI agent can resume from the repository alone.

`CLAUDE.md` must remain a minimal bootstrap.

Do not turn it into the entire manual.

`AGENTS.md` remains agent-neutral.

Do not make repository continuity Claude-specific.

---

# Historical Records

Do NOT rename/move/delete historical:

```text id="history"
codex/
codex/V1/
codex/V2/
codex/V3/
```

These are historical execution records.

The fact that their folder is named `codex` does not make current V4 continuity Codex-specific.

---

# V5 Boundary

Document clearly:

```text id="v5boundary"
V5_NOT_IMPLEMENTED
```

Potential V5 concern:

true source-extraction language/framework/technology/project-layout agnosticism.

Do not design V5 in detail.

Do not implement V5.

---

# Planned Post-V4 Maintainability Refactor

The Technical Lead has explicitly requested a comprehensive readability and maintainability refactor after V4 closes.

Record:

```text id="postv4"
POST_V4_MAINTAINABILITY_REFACTOR=PLANNED
```

This is a separate future phase.

Its goal will be:

```text id="refactorgoal"
READABILITY_AND_MAINTAINABILITY
```

with:

```text id="refactorbehavior"
BEHAVIOR_CHANGE=FORBIDDEN
```

unless a later explicit Technical Lead decision authorizes otherwise.

Carry forward at minimum R13:

```text id="debts"
DEBT-001
DEBT-002
DEBT-003
```

Also carry forward relevant unresolved V3 maintainability debt.

Do not perform the refactor in R14.

---

# Maintainability Baseline

Because a dedicated refactor follows V4, capture a deterministic pre-refactor baseline.

At minimum record:

```text id="maintbaseline"
production Python module/file count
test count
important package inventory
largest relevant modules where deterministically measurable
known maintainability debt
docstring observations
type-hint observations
duplicated report/serialization patterns
mixed-responsibility modules already identified
```

Do not add a large analysis dependency.

This baseline is diagnostic and will help prove the future refactor preserves behavior.

---

# Final V4 Baseline

Create:

```text id="baselinefile"
output/v4_r14/V4_FINAL_BASELINE.json
```

It must deterministically describe the final V4 implementation checkpoint.

Include at minimum:

```text id="baselinefields"
version = V4

latest_completed_round
latest_approved_round

test_count

readiness
ai_knowledge_allowed
ai_knowledge_generated
provider_calls
real_llm_calls

canonical_knowledge_model
human_projection
plugin_projection

plugin_contract_name
plugin_contract_version

security_gate
regression_gate

critical_open
high_open
medium_open
low_open

source_code_optional
technical_lead_final_approval_authority

v5_implemented

post_v4_maintainability_refactor

approved_artifact_hashes

manuals

maintainability_baseline
```

No timestamps.

No machine-specific absolute paths.

No random values.

---

# Final Manifest

Create:

```text id="manifestfile"
output/v4_r14/V4_FINAL_MANIFEST.json
```

Purpose:

provide deterministic discovery of the important V4 repository artifacts.

Include structured categories such as:

```text id="manifestcategories"
authority_files
manuals
round_results
round_closures
contracts
examples
security_artifacts
baseline
continuity_files
```

Use repository-relative paths only.

Do not include every test/cache/generated file.

The manifest is a discovery index, not another truth source.

Required:

```text id="manifestpolicy"
FINAL_MANIFEST_IS_INDEX_NOT_AUTHORITY
```

---

# Artifact Hashes

The final baseline should capture SHA-256 for important approved deterministic artifacts.

At minimum include reviewed R10, R11, R12 and R13 artifacts.

Do not overwrite approved artifacts.

Recompute and compare against their closure records.

If any mismatch exists:

STOP.

Required:

```text id="hashpass"
APPROVED_ARTIFACT_INTEGRITY=PASS
```

---

# Baseline Determinism

Generate independently twice:

```text id="baselineartifacts"
output/v4_r14/V4_FINAL_BASELINE.json
output/v4_r14/V4_FINAL_MANIFEST.json
```

Require:

```text id="baselinepass"
FINAL_BASELINE_DETERMINISM=PASS
FINAL_MANIFEST_DETERMINISM=PASS
```

---

# Documentation Accuracy Validation

Add deterministic tests/checks where useful to ensure final manuals do not contradict machine-readable contracts.

Do not attempt general natural-language semantic verification.

Use explicit markers/contract values for important invariants.

Examples:

```text id="docchecks"
LegacyMapperPluginKnowledge
contract_version 1.0
ONE_CANONICAL_KNOWLEDGE_SOURCE
TECHNICAL_LEAD
SOURCE_CODE_OPTIONAL
R11/R12 sibling projection boundary
V5_NOT_IMPLEMENTED
POST_V4_MAINTAINABILITY_REFACTOR=PLANNED
```

Prefer simple deterministic checks.

---

# Broken Internal References

Check repository-relative paths referenced by the new manuals and final manifest.

Required:

```text id="refcheck"
BROKEN_INTERNAL_REFERENCES=0
```

Only validate references that are intended as repository file references.

Do not treat conceptual examples as paths.

---

# Security

R14 documentation and baseline generation must not weaken R13.

Require:

```text id="r14security"
SECURITY_GATE=PASS
REGRESSION_GATE=PASS

CRITICAL_OPEN=0
HIGH_OPEN=0
```

No credentials, tokens, private keys or `.env` content in manuals/baselines.

Do not echo secret-shaped values from tests.

No provider/LLM calls.

---

# Regression

Run the complete test suite.

```text id="r14tests"
python -m unittest discover -s tests
```

Expected:

```text id="r14testexpected"
>1335 PASS
```

Do not remove/skip/weaken tests to satisfy R14.

Run readiness:

```text id="r14readiness"
python -m legacy_documenter.knowledge.readiness
```

Require:

```text id="r14ready"
READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

---

# Production Code

R14 should normally require:

```text id="prodchange"
PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false
```

Documentation helpers/tests/report builders may be added if needed.

If production-code modification becomes necessary to correct an actual approved-contract defect:

STOP and report before changing it.

R14 is not a defect-remediation or refactor round.

---

# Required Tests

Prefer one focused file:

```text id="r14testfile"
tests/test_v4_r14_manuals_and_final_baseline.py
```

Test at minimum:

1. entry gate/continuity;
2. manuals exist;
3. required contract markers are present;
4. Plugin contract name/version matches R12;
5. one canonical source marker;
6. source-code optionality marker;
7. Technical Lead authority marker;
8. V5 not implemented marker;
9. post-V4 maintainability refactor planned;
10. baseline JSON validity;
11. manifest JSON validity;
12. deterministic baseline;
13. deterministic manifest;
14. no machine-specific absolute paths;
15. important artifact hashes match;
16. manifest repository paths exist;
17. broken internal references = 0 for intended references;
18. security/regression state preserved;
19. no provider/LLM calls;
20. repository continuity remains agent-neutral.

Do not hardcode a state assertion that will become invalid merely because R14 later becomes formally approved.

Learn from `REG-001`.

---

# PROJECT_STATE After Successful R14 Implementation

R14 implementation is complete but NOT yet approved.

Update using existing schema:

```text id="r14state"
latest_completed_round = V4-R14
latest_approved_round = V4-R13

current_round_in_progress =
"V4-R14 (pending Technical Lead review)"

round_status =
V4-R14_READY_FOR_HUMAN_REVIEW

next =
HUMAN_REVIEW_V4_R14

tests = <actual count>

readiness = READY

ai_knowledge_allowed = true
ai_knowledge_generated = false

provider_calls = 0
real_llm_calls = 0
```

Do not mark V4 formally closed.

Do not set `latest_approved_round=V4-R14`.

---

# Required Result

Create:

```text id="r14resultpath"
docs/V4/V4_R14_MANUALS_AND_FINAL_BASELINE_RESULT.md
```

Report at minimum:

```text id="r14resultfields"
STATUS
ENTRY_GATE

BASELINE_TESTS
FINAL_TESTS

MANUALS_CREATED
MANUALS_UPDATED

FINAL_BASELINE
FINAL_BASELINE_SHA256

FINAL_MANIFEST
FINAL_MANIFEST_SHA256

FINAL_BASELINE_DETERMINISM
FINAL_MANIFEST_DETERMINISM

APPROVED_ARTIFACT_INTEGRITY
BROKEN_INTERNAL_REFERENCES

ONE_CANONICAL_KNOWLEDGE_SOURCE
TECHNICAL_LEAD_FINAL_APPROVAL_AUTHORITY
SOURCE_CODE_OPTIONAL

R11_BOUNDARY
R12_BOUNDARY
R11_R12_SIBLING_PROJECTIONS

PLUGIN_CONTRACT_NAME
PLUGIN_CONTRACT_VERSION
PLUGIN_RUNTIME

SECURITY_GATE
REGRESSION_GATE
CRITICAL_OPEN
HIGH_OPEN
MEDIUM_OPEN
LOW_OPEN

V5_IMPLEMENTED

POST_V4_MAINTAINABILITY_REFACTOR

MAINTAINABILITY_BASELINE
DEFERRED_DEBT

REPOSITORY_CONTINUITY
AGENT_NEUTRAL_CONTINUITY

PRODUCTION_CODE_CHANGED
PRODUCTION_BEHAVIOR_CHANGED

READINESS
AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS

PROJECT_STATE

DECISION
NEXT
```

---

# Expected Success State

```text id="r14success"
STATUS=V4_R14_MANUALS_AND_FINAL_BASELINE_COMPLETE

ENTRY_GATE=PASS

FINAL_TESTS=>1335_PASS

MANUALS=PASS

FINAL_BASELINE=output/v4_r14/V4_FINAL_BASELINE.json
FINAL_MANIFEST=output/v4_r14/V4_FINAL_MANIFEST.json

FINAL_BASELINE_DETERMINISM=PASS
FINAL_MANIFEST_DETERMINISM=PASS

APPROVED_ARTIFACT_INTEGRITY=PASS
BROKEN_INTERNAL_REFERENCES=0

ONE_CANONICAL_KNOWLEDGE_SOURCE=PASS
TECHNICAL_LEAD_FINAL_APPROVAL_AUTHORITY=PASS
SOURCE_CODE_OPTIONAL=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS
R11_R12_SIBLING_PROJECTIONS=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0
PLUGIN_RUNTIME=NOT_IMPLEMENTED

SECURITY_GATE=PASS
REGRESSION_GATE=PASS

CRITICAL_OPEN=0
HIGH_OPEN=0

V5_IMPLEMENTED=false

POST_V4_MAINTAINABILITY_REFACTOR=PLANNED

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false

REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW

DECISION=V4_R14_READY_FOR_HUMAN_REVIEW

NEXT=HUMAN_REVIEW_V4_R14
```

---

# Stop Condition

After creating/updating manuals, deterministic final baseline/manifest, tests, continuity documentation and the R14 result:

STOP.

Do NOT:

* approve R14;
* formally close V4;
* commit;
* push;
* begin V5;
* begin the post-V4 maintainability refactor;
* redesign approved V4 contracts;
* implement Plugin runtime;
* call any provider/LLM.

The next action is:

```text id="r14next"
HUMAN_REVIEW_V4_R14
```
