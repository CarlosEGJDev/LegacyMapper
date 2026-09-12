TASK=V3-R7_2_3_EVIDENCE_CONSTRAINED_RESUME

MODE=IMPLEMENT_AND_EXECUTE

PARENT=V3-R7_2_2
R7_2_2_STATUS=V3-R7_2_2_MODEL_CONTRACT_FAILURE

NO_R8
NO_AI_KNOWLEDGE
NO_HUMAN_APPROVAL
NO_MODEL_CHANGE_AUTOMATIC
NO_VALIDATOR_WEAKENING
NO_V1_V2_REGENERATION
NO_RAW_REPOSITORY_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_DIRECT_LLM_MARKDOWN_GENERATION
NO_SEMANTIC_RESPONSE_REPAIR

OBJECTIVE

Resume V3-R7.2 from the existing validated checkpoints and eliminate free-form generation of evidence identifiers.

Current validated state:

FUNCTIONAL_LOCAL=8/8 PASS
TECHNICAL_LOCAL=1 PASS
PERSISTED_VALID_ASSESSMENTS=9

R7.2.2 failure:

* request identity valid;
* deterministic envelope valid;
* request budget valid;
* model generated unknown evidence IDs;
* unknown IDs appeared in claims and MissingInformation;
* validator correctly rejected the response;
* invalid response was not persisted.

Primary correction:

The model may SELECT evidence identifiers.

The model must NOT GENERATE evidence identifiers.

==================================================
LEGACYMAPPER MODEL RULE
=======================

Do NOT apply the Codex "third failure -> change model" rule.

That rule applies to Codex as programming agent only.

For LegacyMapper:

MODEL_CHANGE_RECOMMENDED=true only when analysis shows the remaining failure is reasonably attributable to model capability after excluding:

1. Python/deterministic implementation defects;
2. request construction defects;
3. schema/contract ambiguity;
4. prompt ambiguity;
5. evidence-catalog design;
6. context/budget problems;
7. provider/serialization problems.

No fixed failure-count threshold exists for LegacyMapper.

Record failures for diagnosis, but do not automatically recommend another model based on count.

==================================================
DESIGN PRINCIPLE
================

Python discovers and constrains.

LLM interprets and selects.

Python validates.

Required evidence flow:

V2 evidence
↓
Python ContextPackage
↓
Python AllowedEvidenceCatalog
↓
LLM semantic interpretation
↓
LLM selects ONLY catalog evidence keys
↓
Python deterministic resolution
↓
canonical evidence IDs
↓
AssessmentValidator

The LLM must not construct canonical evidence IDs character by character.

==================================================
ROOT CAUSE TO CORRECT
=====================

R7.2.2 proved that deterministic identity ownership solved the previous source_snapshot problem.

The remaining failure is semantic evidence selection:

MODEL OUTPUT
-> evidence_refs containing unknown IDs
-> evidence closure FAIL

Do not weaken evidence closure.

Do not accept approximately matching IDs.

Do not silently drop unknown IDs.

Do not replace invented IDs after generation.

Instead prevent free-form canonical evidence-ID generation.

==================================================
ALLOWED EVIDENCE CATALOG
========================

For every model request, Python must construct an explicit bounded evidence catalog from the exact ContextPackage supplied to that request.

Preferred representation:

allowed_evidence = [
{
"key": "E01",
"type": "...",
"description": "...",
"canonical_id": "..."
},
{
"key": "E02",
...
}
]

However:

DO NOT expose canonical_id to the model if it is unnecessary.

Preferred model-visible representation:

E01 = concise evidence description
E02 = concise evidence description
E03 = concise evidence description

Python-owned mapping:

E01 -> canonical V2 evidence ID
E02 -> canonical V2 evidence ID
E03 -> canonical V2 evidence ID

The model outputs evidence KEYS, not canonical IDs.

==================================================
EVIDENCE KEY FORMAT
===================

Keys must be deterministic, compact and request-local.

Preferred:

E01
E02
...
E99

If more than 99 records are somehow required, use deterministic zero-padding appropriate to count.

But existing request limits should normally keep catalogs much smaller.

Keys must be generated deterministically from ordered ContextPackage evidence.

Do not derive keys from model output.

==================================================
MODEL CONTRACT
==============

The semantic model schema must use:

evidence_keys

instead of free-form:

evidence_refs

for model-owned semantic output.

Example claim semantic payload:

{
"claim_id": "TC-01",
"section": "...",
"statement": "...",
"status": "CONFIRMED",
"source_type": "DETERMINISTIC_CODE_FACT",
"evidence_keys": ["E01", "E04"]
}

MissingInformation:

{
...
"related_evidence_keys": ["E03", "E07"]
}

The model must not output canonical evidence IDs.

==================================================
DETERMINISTIC RESOLUTION
========================

After semantic JSON parsing:

Python resolves:

evidence_keys
-> canonical evidence_refs

and:

related_evidence_keys
-> related_evidence_ids

This is deterministic metadata resolution, NOT semantic repair.

Allowed:

E03 -> exact catalog canonical ID

Forbidden:

UNKNOWN_ID -> guessed nearest canonical ID

Forbidden:

E99 absent from catalog -> ignore

Unknown evidence key:

FAIL

No partial repair.

==================================================
WHY THIS IS NOT SEMANTIC REPAIR
===============================

The model explicitly selects an allowed symbolic evidence item.

Python merely resolves that symbol to the canonical V2 identifier already associated with it before inference.

Equivalent conceptually to:

enum selection
-> canonical value

Python does not alter the selected evidence meaning.

==================================================
CATALOG VALIDATION
==================

Before every provider call validate:

* every key unique;
* every canonical evidence ID unique where expected;
* every canonical evidence ID exists in supplied ContextPackage;
* every catalog entry belongs to current request;
* no evidence from another package leaks into catalog;
* ordering deterministic;
* descriptions derived from existing evidence only;
* no invented descriptions;
* catalog size bounded.

If catalog invalid:

DO NOT call provider.

==================================================
DESCRIPTION GENERATION
======================

Evidence descriptions must be deterministic.

Use existing V2/context fields.

Do not ask an LLM to summarize evidence for the catalog.

Keep descriptions concise enough to preserve request budget.

Examples of useful deterministic fields:

evidence type
project
symbol/method
WebForm
operation
stored procedure
relationship type
status
short deterministic identifier

Do not include unnecessary raw payloads.

==================================================
CLAIM SOURCE TYPE
=================

The model still owns:

status
source_type
statement

Therefore existing semantic validation remains authoritative.

Examples:

AI_INTERPRETATION + CONFIRMED when forbidden
-> FAIL

UNRESOLVED promoted without evidence
-> FAIL

Evidence catalog does not weaken source/status validation.

==================================================
MISSING INFORMATION
===================

MissingInformation must use:

related_evidence_keys

The same deterministic resolver maps these to canonical related_evidence_ids.

Unknown key:

FAIL entire assessment.

Do not remove only the invalid MissingInformation record.

==================================================
CLAIM RELATIONSHIPS
===================

related_claim_ids remain semantic model-owned fields if required.

Validate normally.

Do not deterministically invent claim relationships.

==================================================
DETERMINISTIC ENVELOPE
======================

Preserve R7.2.2 envelope design.

Python owns:

assessment_id
profile_id
context_package_ids
source_snapshots
schema_version
prompt_contract_version
request_hash
provider/model metadata
stage
validation marker
persisted content hash

LLM does NOT echo those fields.

==================================================
CACHE
=====

Existing cache:

output/v3_r7_2/LOCAL_ASSESSMENTS.json

Expected:

8 valid functional
1 valid technical

Revalidate before reuse.

Do not require migration solely because the model-facing evidence schema changes if persisted canonical assessments remain valid under AssessmentValidator.

Important distinction:

model request schema version may change;

canonical persisted Assessment schema does not need to change unnecessarily.

Reuse old validated assessments when:

canonical assessment remains valid
AND
original package/snapshot/request identity remains valid for its completed work.

Do not invalidate previous assessments merely because new requests use evidence_keys.

==================================================
RESUME
======

Expected:

LOAD CACHE
-> revalidate 9 assessments
-> reuse 8 functional
-> reuse 1 technical
-> resume missing technical assessments
-> persist each PASS
-> intermediate functional
-> intermediate technical
-> global functional
-> global technical
-> deterministic renderer
-> DRAFT documents

Do not rerun completed valid assessments.

==================================================
TECHNICAL RESUME
================

R7.2.2 stopped on the next technical local response after one technical PASS.

Resume from first missing technical package.

All new technical calls must use evidence-key catalogs.

Persist immediately after canonical PASS.

==================================================
INTERMEDIATE SYNTHESIS
======================

Evidence-constrained selection also applies to intermediate synthesis.

For intermediate requests, construct a bounded catalog of allowed lower-level evidence references.

The model may select:

local claim keys
and/or compact evidence keys

depending on existing synthesis architecture.

Preferred approach:

C01 -> local claim identity
E01 -> underlying evidence identity

Python resolves both deterministically.

Do not require the model to reproduce long hashes/IDs.

==================================================
GLOBAL SYNTHESIS
================

Apply the same principle globally.

The global model should select compact deterministic keys representing validated intermediate claims/evidence.

Do not ask it to reproduce:

long ContextPackage IDs
snapshot hashes
canonical evidence hashes

Python owns those mappings.

==================================================
TRACEABILITY
============

Final traceability must still resolve fully:

GLOBAL CLAIM
-> INTERMEDIATE CLAIM
-> LOCAL CLAIM
-> CONTEXT PACKAGE
-> V2 EVIDENCE
-> SOURCE SNAPSHOT

Compact keys are request-local transport identifiers only.

They must never replace canonical IDs in persisted final assessments.

==================================================
PERSISTENCE
===========

Persist only canonical resolved assessments after:

1. semantic parse PASS
2. evidence-key resolution PASS
3. deterministic envelope composition PASS
4. canonical AssessmentValidator PASS

Persisted assessments should contain canonical evidence_refs, not temporary E01/E02 keys.

Do not persist raw model responses.

==================================================
REQUEST BUDGET
==============

Every request remains:

<=5000 estimated input tokens

Preferred:

<=4200 where feasible

Evidence descriptions must be compact.

Do not increase ContextPackage size because IDs are shorter.

==================================================
PREFLIGHT
=========

Before each real provider call:

PROFILE_PASS
ENVELOPE_PASS
CONTEXT_PACKAGE_PASS
SOURCE_SNAPSHOT_PASS
EVIDENCE_CATALOG_PASS
EVIDENCE_CLOSURE_PASS
PROMPT_SCHEMA_PASS
TOKEN_ESTIMATE<=5000

If any FAIL:

no provider call.

==================================================
MODEL PROMPT REQUIREMENTS
=========================

Tell the model explicitly:

* evidence keys are an enum-like closed set;
* use only keys shown in AllowedEvidenceCatalog;
* never invent evidence keys;
* never output canonical evidence IDs;
* if no evidence supports a claim, mark it appropriately rather than inventing evidence;
* if required information is absent, use MissingInformation;
* strict JSON only.

Do not rely solely on prose.

Where supported by current structured schema, constrain evidence_keys against the actual request-local allowed key set.

==================================================
STRUCTURED SCHEMA
=================

Preferred:

generate request-local JSON Schema enum:

"evidence_keys": {
"type": "array",
"items": {
"enum": ["E01","E02",...]
}
}

and equivalent enum for:

related_evidence_keys

If provider/SDK cannot enforce dynamic enum directly:

retain explicit catalog + deterministic post-validation.

Document actual enforcement level.

Do not pretend provider-side enforcement exists if it does not.

==================================================
NO EVIDENCE AVAILABLE
=====================

If a semantic statement has no authoritative evidence:

do not force evidence selection.

Use canonical R5 rules for INTERPRETED/UNRESOLVED.

The catalog is a constraint, not a reason to fabricate support.

==================================================
TESTS
=====

Create/update:

tests/test_v3_r7_2_3.py

Minimum tests:

1 deterministic evidence catalog generation
2 stable evidence ordering
3 stable E-key assignment
4 catalog only contains current package evidence
5 duplicate key rejected
6 unknown canonical source rejected preflight
7 model-visible catalog excludes canonical IDs where configured
8 valid E01 resolves canonical evidence
9 multiple keys resolve deterministically
10 unknown key rejected
11 unknown key not silently removed
12 unknown key not nearest-matched
13 claim evidence resolution
14 MissingInformation evidence resolution
15 unknown MissingInformation key rejects assessment
16 canonical persisted assessment contains evidence_refs
17 temporary evidence_keys absent from persisted canonical assessment
18 semantic statement unchanged by resolution
19 semantic status unchanged
20 semantic source_type unchanged
21 invalid status promotion still rejected
22 invalid source_type still rejected
23 no-evidence INTERPRETED handling
24 no-evidence UNRESOLVED handling
25 dynamic enum generated from catalog
26 enum excludes foreign-package evidence
27 request preflight validates catalog
28 invalid catalog prevents provider call
29 catalog descriptions deterministic
30 catalog descriptions use no LLM
31 evidence catalog respects token budget
32 deterministic envelope retained
33 9 existing cache assessments revalidate in fixture scenario
34 valid previous cache reused despite new transport evidence schema
35 completed functional calls skipped
36 completed technical call skipped
37 missing technical resumes
38 successful technical persisted
39 failed evidence selection not persisted
40 intermediate claim-key catalog deterministic
41 intermediate evidence-key resolution
42 global key catalog deterministic
43 hierarchical canonical traceability preserved
44 no long model-generated canonical IDs required
45 canonical AssessmentValidator unchanged
46 no semantic repair
47 renderer receives canonical IDs only
48 DRAFT gate retained
49 AI_KNOWLEDGE blocked
50 source immutability
51 provider-neutral core behavior
52 model not hardcoded
53 LegacyMapper model-change policy has no fixed failure count

All tests offline.

Run:

python -m unittest discover -s tests

Baseline:

246 PASS

Expected:

> 246 PASS

==================================================
REAL EXECUTION
==============

After tests PASS:

execute real resume using:

existing V2 outputs
R7.2 coverage planner
R7.2.1 synthesis planner
R7.2.2 deterministic envelope
existing LOCAL_ASSESSMENTS cache
CopilotProvider
auto/configured model

No raw legacy scan.
No V1/V2 regeneration.

==================================================
CALL CONSERVATION
=================

Expected reusable:

8 functional
1 technical

Do not count reused assessments as real calls.

Expected remaining local technical calls:

approximately 7

Then execute only required intermediate/global calls.

Target new real calls:

<=16

Hard max:

22 NEW primary calls

No semantic retries.

Transport retry only if already permitted by existing provider policy.

==================================================
CHECKPOINTING
=============

Persist after every new canonical PASS.

If execution stops:

next run must resume from all valid persisted checkpoints.

Never discard previous valid assessments because a later stage fails.

==================================================
DOCUMENT GENERATION
===================

Only after:

LOCAL_FUNCTIONAL complete
LOCAL_TECHNICAL complete
INTERMEDIATE_FUNCTIONAL valid
INTERMEDIATE_TECHNICAL valid
GLOBAL_FUNCTIONAL valid
GLOBAL_TECHNICAL valid
TRACEABILITY closure PASS

regenerate:

output/LEVANTAMIENTO_FUNCIONAL.md
output/LEVANTAMIENTO_TECNICO.md

LLM never writes Markdown directly.

==================================================
DOCUMENT STATUS
===============

Both:

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
DOCUMENT QUALITY GATE
=====================

Do not mark READY_FOR_HUMAN_REVIEW merely because files were generated.

Verify material improvement over R7.1.

Required evaluation:

STRUCTURAL_COVERAGE
INTERPRETATION_COVERAGE
PROJECTS_REPRESENTED
WEBFORMS_REPRESENTED
FLOWS_REPRESENTED
DATA_OPERATIONS_LINKED
STORED_PROCEDURES_LINKED
CONFIRMED_CLAIMS
INTERPRETED_CLAIMS
UNRESOLVED_CLAIMS
MISSING_INFORMATION_COUNT

Critical sections must either:

A. contain materially broader supported conclusions;

or

B. contain bounded UNRESOLVED conclusions backed by systematic V2 coverage.

==================================================
ARCHITECTURE
============

Do not force architecture pattern.

Allowed:

CONFIRMED
INTERPRETED
NO_PATTERN_CONFIRMED
INSUFFICIENT_EVIDENCE

Architecture conclusions require supporting and contradicting evidence according to existing contract.

==================================================
LEGACYMAPPER MODEL CAPABILITY DIAGNOSIS
=======================================

If another model semantic failure occurs:

DO NOT recommend model change automatically.

Diagnose:

CONTRACT_ISSUE
PYTHON_ISSUE
EVIDENCE_CATALOG_ISSUE
CONTEXT_ISSUE
BUDGET_ISSUE
PROVIDER_ISSUE
MODEL_CAPABILITY_CANDIDATE

Only use:

MODEL_CAPABILITY_CANDIDATE

after the other relevant categories have been reasonably excluded.

MODEL_CHANGE_RECOMMENDED=true only if evidence indicates a practical model capability limitation.

No numeric failure threshold.

==================================================
FAILURE STATES
==============

If evidence catalog construction invalid:

STATUS=V3-R7_2_3_EVIDENCE_CATALOG_FAILURE

If model emits unknown key despite closed catalog:

STATUS=V3-R7_2_3_MODEL_SEMANTIC_FAILURE

If deterministic resolver changes semantics:

STATUS=V3-R7_2_3_EVIDENCE_RESOLUTION_INTEGRITY_FAILURE

If provider blocked:

STATUS=V3-R7_2_3_BLOCKED_PROVIDER

If synthesis cannot fit budget:

STATUS=V3-R7_2_3_BUDGET_STRATEGY_FAILURE

If traceability fails:

STATUS=V3-R7_2_3_TRACEABILITY_FAILURE

If call hard max reached:

STATUS=V3-R7_2_3_CALL_BUDGET_EXHAUSTED

Do not start R8.

==================================================
SUCCESS
=======

STATUS=V3-R7_2_3_READY_FOR_HUMAN_REVIEW

DECISION=EVIDENCE_CONSTRAINED_HIERARCHICAL_SYNTHESIS_VALIDATED

NEXT=V3-R8_HUMAN_REVIEW_NOT_STARTED

==================================================
REPORT
======

Create ONLY:

codex/V3/V3_R7_2_3_RESULTADO.md

FORMAT:

STATUS
FILES_CHANGED
PRECONDITIONS
ROOT_CAUSE
EVIDENCE_CATALOG
EVIDENCE_KEY_FORMAT
MODEL_VISIBLE_EVIDENCE
CANONICAL_EVIDENCE_MAPPING
DYNAMIC_SCHEMA_ENFORCEMENT
UNKNOWN_EVIDENCE_POLICY
NO_SEMANTIC_REPAIR_VALIDATION
DETERMINISTIC_ENVELOPE
CACHE_FOUND
CACHE_REVALIDATED
CACHE_REUSED
CACHE_INVALIDATED
FUNCTIONAL_LOCAL_REUSED
FUNCTIONAL_LOCAL_NEW
TECHNICAL_LOCAL_REUSED
TECHNICAL_LOCAL_NEW
CHECKPOINTING
INTERMEDIATE_FUNCTIONAL
INTERMEDIATE_TECHNICAL
GLOBAL_FUNCTIONAL
GLOBAL_TECHNICAL
HIERARCHY_DEPTH
MAX_REQUEST_ESTIMATED_TOKENS
SELECTED_PROVIDER
MODEL_ID
NEW_REAL_CALLS_EXECUTED
REUSED_ASSESSMENTS
RETRIES
ASSESSMENT_VALIDATION
EVIDENCE_CLOSURE
STATUS_PROPAGATION
MISSING_INFORMATION_DEDUPLICATION
FUNCTIONAL_DOCUMENT
TECHNICAL_DOCUMENT
COVERAGE_R7_1_VS_R7_2_3
TRACEABILITY
UNIT_TESTS
TOTAL_TESTS
REGRESSION
SOURCE_IMMUTABILITY
SECURITY
LEGACYMAPPER_FAILURE_DIAGNOSIS
MODEL_CAPABILITY_ASSESSMENT
MODEL_CHANGE_RECOMMENDED
KNOWN_LIMITATIONS
FAILURES
DECISION
NEXT

Stop.