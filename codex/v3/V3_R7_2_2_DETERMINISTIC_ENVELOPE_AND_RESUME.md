TASK=V3-R7_2_2_DETERMINISTIC_ENVELOPE_AND_RESUME

MODE=IMPLEMENT_AND_EXECUTE

PARENT=V3-R7_2_1
R7_2_1_STATUS=V3-R7_2_1_MODEL_CONTRACT_FAILURE

NO_R8
NO_AI_KNOWLEDGE
NO_HUMAN_APPROVAL
NO_MODEL_CHANGE
NO_VALIDATOR_WEAKENING
NO_V1_V2_REGENERATION
NO_RAW_REPOSITORY_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_DIRECT_LLM_MARKDOWN_GENERATION
NO_SEMANTIC_RESPONSE_REPAIR

OBJECTIVE

Resume V3-R7.2.1 from persisted checkpoints and eliminate avoidable model responsibility for deterministic identity metadata.

Observed R7.2.1 failure:

* 7 local functional assessments validated and persisted;
* 8th functional response rejected;
* request preflight PASS;
* only failing field: exact source_snapshot mismatch;
* no budget failure;
* no implementation-mapping failure;
* this counts as one comparable model-contract failure.

The persisted valid checkpoints MUST be reused if their exact identities remain valid.

Primary goals:

1. move deterministic identity fields outside model semantic responsibility;
2. preserve strict semantic validation;
3. reuse the existing seven valid functional assessments;
4. execute only missing/invalid work;
5. continue technical -> intermediate -> global synthesis;
6. generate R7.2 DRAFT documents if all validations pass.

==================================================
DESIGN PRINCIPLE
================

Python owns identity.

LLM owns interpretation.

Deterministic envelope:

PYTHON CONTROLLED

* profile_id
* context_package_id
* context_package_ids where structurally determined
* source_snapshot / source_snapshots
* schema_version
* prompt_contract_version
* request_hash
* provider metadata
* model metadata after execution
* assessment stage
* validation marker
* persisted content hash

MODEL CONTROLLED

* summary
* claims
* claim statement
* claim status within allowed contract
* claim source_type within allowed contract
* evidence selection only from supplied allowed evidence
* MissingInformation semantic content

Do not require the model to echo deterministic request identity when Python already possesses authoritative values.

==================================================
IMPORTANT DISTINCTION
=====================

This is NOT post-response semantic repair.

Do NOT:

* receive an invalid source_snapshot from the model;
* overwrite it afterward;
* then pretend the raw response was valid.

Instead:

change the response contract so deterministic envelope fields are not model-generated semantic fields.

The model produces only the semantic payload it is responsible for.

Python constructs the final Assessment envelope BEFORE validation using authoritative request metadata plus the raw semantic payload.

The semantic payload must remain unmodified.

==================================================
CANONICAL STRUCTURE
===================

Preferred architecture:

AssessmentEnvelope
{
deterministic_identity,
semantic_assessment
}

Where:

deterministic_identity:

* profile_id
* context_package_id(s)
* source_snapshot(s)
* schema_version
* prompt_contract_version
* request_hash
* stage

semantic_assessment:

* assessment_id if semantically required
* status
* summary
* claims
* missing_information

AssessmentValidator should validate the composed authoritative Assessment representation.

Do not weaken existing claim/evidence/status rules.

==================================================
CONTRACT COMPATIBILITY
======================

R5/R7.1 canonical rules remain authoritative.

If current schema requires identity fields inside the model payload:

refactor serialization/adapter boundary so those fields are deterministically injected before canonical object validation.

Do not create a competing second semantic contract.

The canonical validated Assessment must still expose required identity fields.

==================================================
RAW RESPONSE PRESERVATION
=========================

Do not persist raw model response by default.

For testability, it is sufficient to prove:

semantic model payload
+
deterministic envelope
======================

canonical validated Assessment

Do not silently normalize semantic values.

Allowed deterministic composition is limited to metadata already known before provider execution.

==================================================
FIELDS THAT MUST REMAIN MODEL-VALIDATED
=======================================

The following MUST NOT be deterministically corrected:

claim statement
claim status
source_type
evidence_refs selected by model
related_claim_ids
MissingInformation question/reason
blocking_level
section semantics
assessment status
summary

If any violates the canonical contract:

reject response.

==================================================
EVIDENCE CLOSURE
================

Model evidence_refs must still satisfy exact allowed evidence closure.

Python must NOT replace invented/unknown evidence IDs with valid ones.

Unknown evidence:

FAIL

Status promotion:

FAIL

Forbidden source type:

FAIL

Malformed MissingInformation:

FAIL

==================================================
REUSE EXISTING CHECKPOINTS
==========================

Input cache:

output/v3_r7_2/LOCAL_ASSESSMENTS.json

Expected existing valid local functional assessments:

7

Before reuse, revalidate each cached record.

Exact match required:

profile_id
context_package_id
source_snapshot
prompt_contract_version
schema_version
request_hash
content_hash
validation_status=VALID

Additionally rerun canonical AssessmentValidator against persisted assessment payload.

If PASS:

REUSE

If FAIL:

INVALIDATE

Do not assume the seven are valid merely because the prior report says so.

==================================================
CACHE MIGRATION
===============

The cached R7.2.1 assessments were stored under the previous envelope representation.

If the new deterministic-envelope representation changes persisted structure:

perform deterministic cache migration only if semantic assessment data and authoritative identity can be preserved exactly.

Migration rules:

* no LLM call;
* no semantic field modification;
* no status change;
* no evidence change;
* deterministic metadata transformation only;
* validate migrated object;
* generate new content hash;
* retain original source/request identity.

If safe migration is impossible:

invalidate only affected entries.

Do NOT invalidate all seven unnecessarily.

==================================================
RESUME PLAN
===========

Expected execution path:

LOAD CACHE
-> validate/migrate existing 7 functional checkpoints
-> reuse valid checkpoints
-> execute missing functional batch #8
-> validate
-> persist
-> execute/reuse all technical local assessments
-> persist each PASS immediately
-> hierarchical intermediate synthesis
-> persist each PASS
-> global functional synthesis
-> global technical synthesis
-> render documents

Do not rerun already valid work.

==================================================
FUNCTIONAL BATCH #8
===================

The previously rejected batch must be executed under the new deterministic-envelope contract.

Its request must still pass:

profile validation
context identity
source snapshot identity
schema
budget <=5000
allowed evidence closure
strict structured semantic payload

The model must no longer be responsible for copying source_snapshot.

==================================================
TECHNICAL LOCAL ASSESSMENTS
===========================

R7.2.1 did not execute technical local assessments.

Run all required technical local batches unless valid reusable checkpoints already exist.

Persist immediately after each PASS.

Expected count from R7.2:

8 technical local assessments

Do not assume exact count if deterministic planner now produces a justified equivalent partition.

Report actual count.

==================================================
PERSISTENCE
===========

Continue using:

output/v3_r7_2/LOCAL_ASSESSMENTS.json

and when reached:

output/v3_r7_2/INTERMEDIATE_ASSESSMENTS.json

Persistence requirements remain:

deterministic serialization
temporary file
flush/close
atomic replace
content hash
validation status
complete identity
resume safe

==================================================
SYNTHESIS
=========

Reuse R7.2.1 synthesis planner.

Do not redesign unless required by deterministic-envelope integration.

Every request:

<=5000 estimated input tokens

Preferred:

<=4200

If oversized:

add deterministic synthesis layer.

Maximum:

3 synthesis levels above local assessments.

==================================================
INTERMEDIATE ENVELOPE
=====================

Apply deterministic envelope to intermediate and global assessments too.

Python controls:

profile
package identity
source snapshots
schema
contract version
request identity
stage

LLM controls semantic interpretation only.

==================================================
HIERARCHICAL TRACEABILITY
=========================

Required:

GLOBAL CLAIM
-> INTERMEDIATE CLAIM
-> LOCAL CLAIM
-> CONTEXT PACKAGE
-> V2 EVIDENCE

Python-controlled envelope must improve traceability, not obscure it.

No dangling:

child_claim_ids
evidence_refs
package refs
snapshots

==================================================
CLAIM IDS
=========

If claim IDs are model-generated under the canonical contract, validate uniqueness and syntax.

Do not arbitrarily rewrite semantic claim IDs after generation.

If deterministic claim IDs are already defined by existing architecture, preserve that behavior.

Do not introduce a new ID policy unless necessary.

==================================================
ASSESSMENT ID
=============

Review whether assessment_id is semantic or infrastructure identity.

Preferred:

assessment_id deterministically generated by Python from:

stage
profile
context package identity
request hash

If changed to deterministic ownership:

document the decision and preserve canonical compatibility.

Do not modify claim semantics.

==================================================
MODEL FAILURE ACCOUNTING
========================

Current comparable post-R7.1 model-contract failures:

1

R7.2 budget failure does NOT count.

R7.2.1 source_snapshot mismatch DOES count.

Under R7.2.2 deterministic-envelope contract:

an identity mismatch in a field no longer model-owned must not occur because it is not requested from the model.

Comparable future model failure means:

* request preflight PASS;
* <=5000 budget;
* canonical semantic schema supplied;
* model violates a field it still owns.

Examples:

invalid evidence
status promotion
forbidden source_type
invalid MissingInformation
malformed semantic schema

If cumulative comparable failures reach 3:

MODEL_CHANGE_RECOMMENDED=true

Otherwise false.

==================================================
NO HIDDEN REPAIR
================

Add tests proving that deterministic envelope composition is not semantic repair.

Example:

raw semantic payload:
claim.status="CONFIRMED"
source_type="AI_INTERPRETATION"

Expected:

FAIL

Python must not downgrade it automatically.

Another:

evidence_refs=["UNKNOWN-EVIDENCE"]

Expected:

FAIL

Another:

semantic payload valid but model omits source_snapshot because envelope owns it.

Expected:

PASS after deterministic composition.

==================================================
REQUEST PROMPT
==============

Update model instructions so they clearly state:

Return semantic assessment JSON only.

Do not emit deterministic request metadata.

Do not emit:

source_snapshot
source_snapshots
profile_id
context_package_id
schema_version
prompt_contract_version
request_hash

unless some field remains semantically required by the canonical payload after refactor.

Avoid asking the model to repeat constants.

==================================================
BUDGET
======

Removing deterministic repeated metadata should not be used as justification to increase batch size.

Retain current limits.

Local requests:

<=5000 estimated tokens

Preferred:

<=4200 where feasible

==================================================
OFFLINE TESTS
=============

Create/update:

tests/test_v3_r7_2_2.py

Minimum tests:

1 deterministic envelope owns source snapshot
2 model payload may omit source snapshot
3 composed canonical assessment contains exact snapshot
4 profile controlled by envelope
5 context package controlled by envelope
6 schema version controlled by envelope
7 prompt contract version controlled by envelope
8 request hash controlled by envelope
9 semantic payload remains byte/structure equivalent where applicable
10 no semantic status repair
11 no source_type repair
12 no evidence repair
13 unknown evidence rejected
14 status promotion rejected
15 malformed MissingInformation rejected
16 cached R7.2.1 checkpoint revalidation
17 valid old checkpoint migrates safely
18 semantic cache content unchanged by migration
19 invalid cache entry rejected
20 cache content hash regenerated deterministically after migration
21 7 existing checkpoints reusable in fixture scenario
22 resume skips reusable calls
23 missing functional batch executes
24 new valid local result persisted
25 failed result not persisted
26 technical stage resumes after functional completion
27 per-call atomic checkpointing
28 intermediate envelope composition
29 global envelope composition
30 hierarchical evidence closure
31 source snapshots preserved through hierarchy
32 child claim traceability preserved
33 synthesis planner <=5000
34 preferred <=4200 where feasible
35 adaptive hierarchy preserved
36 deterministic rerun reuses cache
37 no direct LLM Markdown
38 renderer only receives validated global assessments
39 DRAFT gate retained
40 AI_KNOWLEDGE blocked
41 source immutability
42 provider-neutral semantic layer
43 model identity not hardcoded
44 comparable model-failure counter correct
45 R7.2 budget failure excluded from model failure counter

All offline.

Run:

python -m unittest discover -s tests

Baseline:

201 PASS

Expected:

> 201 PASS

==================================================
REAL EXECUTION
==============

After tests PASS:

execute R7.2.2 real recovery.

Use:

existing V2 outputs
existing R7.2 coverage planner
existing R7.2.1 synthesis planner
persisted R7.2.1 local cache
CopilotProvider
auto/configured model

No raw legacy scan.

No V2 regeneration.

==================================================
REAL CALL EXPECTATION
=====================

If seven functional cached assessments validate:

DO NOT repeat them.

Expected minimum new local calls:

1 functional
+
8 technical

Then only required intermediate/global synthesis calls.

Expected total new calls:

approximately 15-18

depending on deterministic synthesis partitioning.

Hard max for this execution:

24 NEW primary calls

Do not count reused assessments as real calls.

If reaching hard max:

stop safely with checkpoints persisted.

==================================================
VALIDATION ORDER
================

For each stage:

1 construct request identity deterministically
2 preflight
3 provider call
4 parse semantic JSON
5 compose deterministic envelope
6 canonical AssessmentValidator
7 persist PASS
8 continue

Never persist before canonical PASS.

==================================================
DOCUMENT GENERATION
===================

Generate only if:

all required local assessments valid
all intermediate assessments valid
global functional PASS
global technical PASS
traceability closure PASS

Then regenerate:

output/LEVANTAMIENTO_FUNCIONAL.md
output/LEVANTAMIENTO_TECNICO.md

Both remain DRAFT.

==================================================
DOCUMENT QUALITY
================

R7.2.2 must preserve the R7.2 coverage objective.

Do not fall back to R7.1 sample-only documents.

Compare against R7.1 at document level.

Required metrics:

projects represented before/after
WebForms represented before/after
flows represented before/after
linked data operations before/after
linked stored procedures before/after
CONFIRMED claims before/after
INTERPRETED claims before/after
UNRESOLVED claims before/after
MissingInformation before/after

==================================================
SUCCESS CRITERIA
================

PASS requires:

* deterministic envelope implemented;
* no semantic repair introduced;
* existing cache revalidated;
* valid previous checkpoints reused;
* missing local functional work completed;
* technical local assessments completed;
* local results persisted;
* intermediate synthesis completed;
* global synthesis completed;
* every request within budget;
* both DRAFT documents generated;
* coverage improved over R7.1;
* hierarchical traceability closed;
* tests PASS;
* source immutable;
* AI_KNOWLEDGE blocked.

==================================================
FAILURE STATES
==============

If existing cache cannot be safely migrated:

do not fail entire round automatically.

Report invalidated count and regenerate only invalidated assessments.

If semantic model contract fails:

STATUS=V3-R7_2_2_MODEL_CONTRACT_FAILURE

If provider/quota blocks execution:

STATUS=V3-R7_2_2_BLOCKED_PROVIDER

If request exceeds budget and hierarchy cannot split:

STATUS=V3-R7_2_2_BUDGET_STRATEGY_FAILURE

If deterministic envelope introduces semantic mutation:

STATUS=V3-R7_2_2_ENVELOPE_INTEGRITY_FAILURE

If traceability fails:

STATUS=V3-R7_2_2_TRACEABILITY_FAILURE

If hard new-call maximum reached:

STATUS=V3-R7_2_2_CALL_BUDGET_EXHAUSTED

Do not start R8.

==================================================
SUCCESS STATE
=============

STATUS=V3-R7_2_2_READY_FOR_HUMAN_REVIEW

DECISION=DETERMINISTIC_ENVELOPE_AND_RESUME_VALIDATED

NEXT=V3-R8_HUMAN_REVIEW_NOT_STARTED

==================================================
REPORT
======

Create ONLY:

codex/V3/V3_R7_2_2_RESULTADO.md

FORMAT:

STATUS
FILES_CHANGED
PRECONDITIONS
ROOT_CAUSE
DETERMINISTIC_ENVELOPE
MODEL_OWNED_FIELDS
PYTHON_OWNED_FIELDS
NO_SEMANTIC_REPAIR_VALIDATION
CACHE_FILE
CACHE_FOUND
CACHE_REVALIDATED
CACHE_MIGRATED
CACHE_REUSED
CACHE_INVALIDATED
FUNCTIONAL_LOCAL_REUSED
FUNCTIONAL_LOCAL_NEW
TECHNICAL_LOCAL_REUSED
TECHNICAL_LOCAL_NEW
CHECKPOINTING
SYNTHESIS_PLANNER
HIERARCHY_DEPTH
INTERMEDIATE_FUNCTIONAL
INTERMEDIATE_TECHNICAL
GLOBAL_FUNCTIONAL
GLOBAL_TECHNICAL
MAX_REQUEST_ESTIMATED_TOKENS
SELECTED_PROVIDER
MODEL_ID
NEW_REAL_CALLS_EXECUTED
REUSED_ASSESSMENTS
RETRIES
ASSESSMENT_VALIDATION
STATUS_PROPAGATION
EVIDENCE_CLOSURE
MISSING_INFORMATION_DEDUPLICATION
FUNCTIONAL_DOCUMENT
TECHNICAL_DOCUMENT
COVERAGE_R7_1_VS_R7_2_2
TRACEABILITY
UNIT_TESTS
TOTAL_TESTS
REGRESSION
SOURCE_IMMUTABILITY
SECURITY
COMPARABLE_MODEL_FAILURE_COUNT
MODEL_CHANGE_RECOMMENDED
KNOWN_LIMITATIONS
FAILURES
DECISION
NEXT

Stop.