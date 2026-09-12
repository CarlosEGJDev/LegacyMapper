TASK=V3-R7_2_1_HIERARCHICAL_SYNTHESIS

MODE=IMPLEMENT_AND_EXECUTE

PARENT=V3-R7_2
R7_2_STATUS=V3-R7_2_BUDGET_INSUFFICIENT

NO_R8
NO_AI_KNOWLEDGE
NO_HUMAN_APPROVAL
NO_MODEL_CHANGE
NO_VALIDATOR_WEAKENING
NO_V1_V2_REGENERATION
NO_RAW_REPOSITORY_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_DIRECT_LLM_MARKDOWN_GENERATION

OBJECTIVE

Close V3-R7.2 by fixing only the global synthesis budget failure.

R7.2 already proved:

* deterministic full V2 coverage planning works;
* all 259 projects are classified;
* structural inventories are represented;
* 8 functional local assessments passed;
* 8 technical local assessments passed;
* canonical R7.1 contract remains compliant;
* model failure did NOT occur.

Observed failure:

FUNCTIONAL global synthesis package
= 40 validated local claims
= 6598 estimated tokens

> 5000 configured maximum

Global synthesis was correctly blocked.

Goal:

1. persist validated local assessments;
2. reuse persisted assessments safely;
3. compact deterministically;
4. introduce bounded hierarchical synthesis;
5. keep every LLM request <=5000 estimated input tokens;
6. generate the two R7.2 DRAFT documents;
7. preserve full hierarchical traceability.

==================================================
NON-NEGOTIABLE PRINCIPLE
========================

Do NOT fix this by increasing the 5000-token limit.

Do NOT send all local claims directly to a single global call.

Required architecture:

V2 deterministic evidence
-> coverage planner
-> bounded local assessments
-> validation
-> PERSIST VALID LOCAL ASSESSMENTS
-> deterministic compaction
-> bounded intermediate synthesis
-> validation
-> deterministic compaction
-> bounded global synthesis
-> validation
-> deterministic aggregation
-> deterministic Markdown renderer

Python controls size, persistence, grouping and provenance.

LLM only interprets bounded structured packages.

==================================================
PRECONDITIONS
=============

Required:

V2-R5.1 complete
R7.1 contract enforcement available
R7.2 coverage planner available
CopilotProvider available
local Copilot authentication available

Baseline:

161 tests PASS

R7.2 facts:

TOTAL_COVERAGE_UNITS=87
PROJECTS=259
SOLUTIONS=113
WEBFORMS=3346
FLOWS=12642
DATA_OPERATIONS=20082
STORED_PROCEDURES=5389
UNRESOLVED_RELATIONSHIPS=162914

LOCAL_FUNCTIONAL_ASSESSMENTS=8/8 PASS
LOCAL_TECHNICAL_ASSESSMENTS=8/8 PASS

==================================================
PERSISTENCE REQUIREMENT
=======================

Validated local assessments MUST be persisted immediately after validation.

Preferred artifact:

output/v3_r7_2/LOCAL_ASSESSMENTS.json

The persisted structure must be machine-oriented and deterministic.

Each persisted assessment must include at minimum:

assessment_id
profile_id
assessment_status
context_package_id
source_snapshot
claims
missing_information
provider
model_id if available
prompt_contract_version
schema_version
validation_status
content_hash

Persist only after AssessmentValidator PASS.

Invalid assessments MUST NOT be persisted as reusable validated assessments.

==================================================
ATOMIC PERSISTENCE
==================

Persistence must be safe.

Preferred flow:

serialize deterministically
-> write temporary file
-> fsync/close if practical
-> atomic replace target

Avoid leaving partially written reusable state.

If the process stops after some valid assessments:

preserve the already-valid persisted results.

==================================================
RESUME / REUSE
==============

Before executing a local LLM call:

check whether a reusable validated assessment already exists.

Reuse only if ALL match exactly:

profile_id
context_package_id
source_snapshot
prompt_contract_version
schema_version
content_hash / request identity

If any required identity differs:

do not reuse.

Create a new assessment.

Never reuse solely by list position or batch number.

==================================================
R7.2 PREVIOUS EXECUTION
=======================

The previous 16 real local assessments were not persisted.

Therefore they cannot be trusted/reconstructed as validated reusable outputs from disk.

It is acceptable to repeat those calls once if necessary.

R7.2.1 MUST ensure future executions can resume without repeating successful calls.

==================================================
PERSIST INTERMEDIATE SYNTHESIS
==============================

Validated intermediate synthesis assessments should also be persisted.

Preferred artifact:

output/v3_r7_2/INTERMEDIATE_ASSESSMENTS.json

Use the same identity and validation principles as local persistence.

This allows interrupted synthesis to resume safely.

==================================================
HIERARCHICAL SYNTHESIS
======================

Introduce an intermediate layer.

Target topology:

FUNCTIONAL:

8 local assessments
-> deterministic group A
-> deterministic group B
-> optionally group C only if necessary
-> functional global synthesis

TECHNICAL:

8 local assessments
-> deterministic group A
-> deterministic group B
-> optionally group C only if necessary
-> technical global synthesis

Do not require exactly two groups if budget requires another deterministic split.

Primary constraint:

EVERY synthesis request <=5000 estimated input tokens.

Recommended target:

<=4200 estimated input tokens

Reserve headroom for contract/schema instructions.

==================================================
DETERMINISTIC SYNTHESIS PLANNER
===============================

Implement deterministic synthesis planning.

Preferred location:

legacy_documenter/documentation/synthesis.py

Responsibilities:

* accept validated assessments;
* estimate synthesis input size;
* compact local outputs;
* partition them deterministically;
* guarantee request limits;
* preserve provenance;
* create intermediate synthesis packages;
* create final synthesis packages;
* expose planning metrics.

No AI-based batch planning.

==================================================
CLAIM COMPACTION
================

Do not blindly copy complete local assessment payloads into synthesis prompts.

Build compact machine representations.

For each claim retain only fields necessary for synthesis and traceability:

claim_id
status
concise claim text
source_type
evidence_ids
context_package_id
source_snapshot

Preserve other mandatory fields only if required by the canonical R5 validator.

Do not discard provenance.

==================================================
DETERMINISTIC DEDUPLICATION
===========================

Before intermediate synthesis:

deduplicate exact/redundant deterministic facts when safely possible.

Dedup keys may use:

normalized deterministic identity
same evidence set
same status
same source type
canonical stable representation

Do not semantically merge distinct claims using heuristics.

Do not promote status.

==================================================
AGGREGATE COUNTS OUTSIDE LLM
============================

System-wide counts and coverage metrics remain deterministic.

Do NOT spend LLM tokens repeatedly restating:

259 projects
113 solutions
3346 WebForms
12642 flows
20082 data operations
5389 stored procedures
162914 unresolved relationships

Carry these as structured deterministic metrics.

Inject once where needed in the final synthesis.

==================================================
INTERMEDIATE SYNTHESIS CONTRACT
===============================

Intermediate LLM calls use the SAME R7.1 canonical contract principles.

They produce structured assessments, not prose summaries.

Input authority:

validated lower-level claims
plus deterministic coverage metrics when relevant

Output claims may:

* consolidate compatible lower-level claims;
* identify supported broader interpretations;
* preserve unresolved areas;
* generate MissingInformation.

They MUST preserve child claim references.

==================================================
HIERARCHICAL PROVENANCE
=======================

Each intermediate/global claim must preserve:

parent_claim_id
child_claim_ids
underlying evidence_ids
source context_package_ids
source snapshots

Preferred traceability:

GLOBAL CLAIM
-> INTERMEDIATE CLAIMS
-> LOCAL CLAIMS
-> CONTEXT PACKAGES
-> V2 EVIDENCE

No provenance collapse.

==================================================
STATUS PROPAGATION
==================

No automatic promotion.

Rules:

CONFIRMED global/intermediate claim
requires underlying authoritative deterministic evidence satisfying existing R5 rules.

INTERPRETED remains INTERPRETED unless the authoritative rule permits CONFIRMED.

UNRESOLVED remains unresolved unless actual underlying evidence resolves it.

Do not mark a claim CONFIRMED merely because multiple AI interpretations agree.

==================================================
MISSING INFORMATION
===================

Merge MissingInformation deterministically before global synthesis where possible.

Deduplication key should be based on stable structured fields, not freeform semantic similarity.

Preserve:

request_id
document
section
question
reason
blocking_level
related_claim_ids
related_evidence_ids

If intermediate synthesis generates a new request:

validate it normally.

==================================================
GLOBAL SYNTHESIS
================

Final functional and technical synthesis must operate only on:

validated intermediate assessments
+
deterministic coverage metrics
+
required provenance metadata

Do NOT re-inject full raw local packages.

Each global request:

<=5000 estimated tokens

Recommended:

<=4200 estimated tokens

If still over limit:

add another deterministic synthesis layer.

Do NOT increase budget.

==================================================
ADAPTIVE HIERARCHY
==================

Hierarchy depth must be deterministic and budget-driven.

Pseudo-behavior:

while synthesis_package_estimate > target_limit:
partition deterministically
synthesize partitions
validate
persist
compact validated outputs

Then produce final bounded package.

Maximum hierarchy depth:

3 synthesis levels above local assessments

If still impossible within limits:

STATUS=V3-R7_2_1_BUDGET_STRATEGY_FAILURE

Do not bypass the gate.

==================================================
REAL CALL BUDGET
================

Previous run used 16 calls but results were not persisted.

For this corrected execution:

local calls may need to be repeated once.

Target:

16 local calls
+
4-6 intermediate calls
+
2 global calls

Expected:

22-24 real primary calls

Hard maximum:

30 real primary calls

No semantic retries.

Maximum one retry only for retryable transport or malformed JSON under existing policy.

If persisted reusable assessments exist during rerun:

reuse them and reduce calls.

==================================================
CHECKPOINTING
=============

Persist after each successful validated call.

Execution checkpoints:

LOCAL_FUNCTIONAL
LOCAL_TECHNICAL
INTERMEDIATE_FUNCTIONAL
INTERMEDIATE_TECHNICAL
GLOBAL_FUNCTIONAL
GLOBAL_TECHNICAL

If execution stops:

resume from latest valid checkpoint.

Do not restart completed valid work.

==================================================
CACHE INVALIDATION
==================

Reusable assessment cache becomes invalid if any of these change:

source_snapshot
context package
profile
canonical contract version
schema version
request content hash

Do not use stale assessments silently.

Report reuse/invalidation counts.

==================================================
DOCUMENT GENERATION
===================

Only after BOTH global assessments PASS:

regenerate:

output/LEVANTAMIENTO_FUNCIONAL.md
output/LEVANTAMIENTO_TECNICO.md

Use deterministic renderer only.

LLM must not write Markdown directly.

==================================================
FUNCTIONAL DOCUMENT
===================

Preserve required R7.2 sections including:

Cobertura del levantamiento

Use global validated functional synthesis plus deterministic coverage metrics.

Do not revert to six-project sample semantics.

==================================================
TECHNICAL DOCUMENT
==================

Preserve required R7.2 sections including:

Cobertura técnica

Architecture result remains evidence-controlled.

Do not force:

layered architecture
3-tier
n-tier
MVC
Clean Architecture
or any other pattern.

==================================================
DOCUMENT STATUS
===============

Both documents:

document_status=DRAFT
human_review_required=true
approved=false
knowledge_source_eligible=false

Footer:

STATUS=DRAFT
HUMAN_REVIEW_REQUIRED=true
APPROVED=false
AI_KNOWLEDGE_ALLOWED=false

==================================================
R7.1 COMPARISON
===============

After successful generation compare document-level coverage with R7.1.

Report at minimum:

PROJECTS_REPRESENTED
WEBFORMS_REPRESENTED
FLOWS_REPRESENTED
DATA_OPERATIONS_LINKED
STORED_PROCEDURES_LINKED
CONFIRMED_CLAIMS
INTERPRETED_CLAIMS
UNRESOLVED_CLAIMS
MISSING_INFORMATION_COUNT

Do not treat R7.1 text as factual authority.

==================================================
OFFLINE TESTS
=============

Create/update:

tests/test_v3_r7_2_1.py

Minimum tests:

1 validated local assessment persisted
2 invalid assessment not persisted as reusable
3 deterministic persisted serialization
4 persisted content hash stable
5 cache reuse exact identity
6 cache rejected when source snapshot changes
7 cache rejected when profile changes
8 cache rejected when schema changes
9 cache rejected when contract version changes
10 cache rejected when request hash changes
11 atomic persistence behavior
12 partial checkpoint survives simulated stop
13 execution resumes without duplicate valid call
14 synthesis planner deterministic
15 synthesis planner respects <=5000
16 synthesis target <=4200 where feasible
17 deterministic claim compaction
18 provenance preserved during compaction
19 exact dedup deterministic
20 no semantic heuristic dedup
21 aggregate metrics kept outside repeated prompts
22 intermediate assessment validator required
23 invalid intermediate assessment excluded
24 intermediate assessment persistence
25 child claim refs preserved
26 evidence closure through hierarchy
27 status not promoted
28 AI interpretation agreement does not confirm
29 MissingInformation deterministic merge
30 global functional package <=5000
31 global technical package <=5000
32 adaptive extra level on oversized input
33 max hierarchy depth enforced
34 global validator required
35 no unvalidated output reaches renderer
36 DRAFT status retained
37 AI_KNOWLEDGE blocked
38 deterministic rerun using cache
39 source immutability
40 provider-neutral core architecture

All tests offline.

Run:

python -m unittest discover -s tests

Baseline:

161 PASS

Expected:

> 161 PASS

==================================================
REAL EXECUTION
==============

After offline tests PASS:

run R7.2.1 real pipeline.

Use:

existing V2 outputs only
R7.2 deterministic coverage planner
R7.1 canonical contract
CopilotProvider
auto/configured model selection

Do not hardcode Luna.

Capture effective model where provider exposes it.

==================================================
REQUEST PREFLIGHT
=================

Every real request must pass before execution:

canonical profile exact
contract exact
package identity exact
source snapshot exact
valid evidence closure
estimated tokens <=5000
preferred target <=4200
no approved-document source types
strict structured output

If request fails preflight:

do not call provider.

==================================================
SUCCESS CRITERIA
================

PASS requires:

* local valid assessments persisted;
* safe reuse implemented;
* deterministic synthesis planner implemented;
* hierarchical synthesis used;
* every real request <=5000 estimated tokens;
* intermediate assessments validated;
* global functional assessment PASS;
* global technical assessment PASS;
* both R7.2 documents generated;
* coverage materially exceeds R7.1;
* hierarchical traceability closed;
* no status promotion;
* source immutable;
* AI_KNOWLEDGE blocked;
* tests PASS.

==================================================
MODEL FAILURE RULE
==================

Do NOT count the R7.2 budget failure as a model failure.

If a valid <=5000 request using the canonical contract is rejected due semantic model non-compliance:

record that model-contract failure separately.

MODEL_CHANGE_RECOMMENDED remains false unless the established three-comparable-failures rule is reached.

==================================================
FAILURE STATES
==============

If local/intermediate persistence fails:

STATUS=V3-R7_2_1_PERSISTENCE_FAILURE

If deterministic hierarchy cannot fit within budget:

STATUS=V3-R7_2_1_BUDGET_STRATEGY_FAILURE

If provider unavailable/quota exhausted:

STATUS=V3-R7_2_1_BLOCKED_PROVIDER

If model violates contract:

STATUS=V3-R7_2_1_MODEL_CONTRACT_FAILURE

If global synthesis passes but document traceability fails:

STATUS=V3-R7_2_1_TRACEABILITY_FAILURE

Do not start R8.

==================================================
SUCCESS STATE
=============

STATUS=V3-R7_2_1_READY_FOR_HUMAN_REVIEW

DECISION=HIERARCHICAL_SYNTHESIS_VALIDATED

NEXT=V3-R8_HUMAN_REVIEW_NOT_STARTED

==================================================
REPORT
======

Create ONLY:

codex/V3/V3_R7_2_1_RESULTADO.md

FORMAT:

STATUS
FILES_CHANGED
PRECONDITIONS
ROOT_CAUSE
PERSISTENCE_IMPLEMENTATION
LOCAL_CACHE
CACHE_REUSE
CACHE_INVALIDATIONS
CHECKPOINTING
SYNTHESIS_PLANNER
HIERARCHY_DEPTH
LOCAL_FUNCTIONAL_ASSESSMENTS
LOCAL_TECHNICAL_ASSESSMENTS
INTERMEDIATE_FUNCTIONAL_ASSESSMENTS
INTERMEDIATE_TECHNICAL_ASSESSMENTS
GLOBAL_FUNCTIONAL_SYNTHESIS
GLOBAL_TECHNICAL_SYNTHESIS
MAX_REQUEST_ESTIMATED_TOKENS
SELECTED_PROVIDER
MODEL_ID
REAL_CALLS_EXECUTED
RETRIES
ASSESSMENT_VALIDATION
STATUS_PROPAGATION
MISSING_INFORMATION_DEDUPLICATION
FUNCTIONAL_DOCUMENT
TECHNICAL_DOCUMENT
COVERAGE_R7_1_VS_R7_2_1
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
