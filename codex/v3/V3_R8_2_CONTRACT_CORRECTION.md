TASK=V3-R8_2_CONTRACT_CORRECTION

MODE=DIAGNOSE_CORRECT_TEST_RERUN

PARENT=V3-R8_2_NEEDS_CORRECTION

ROOT_CAUSE:
PROMPT_CONTRACT/SCHEMA

MODEL_CHANGE_ALLOWED=false

Do NOT change provider/model.

==================================================
OBJECTIVE
=========

Correct the evidence-authority contract defect found during R8.2 and rerun the evidence-constrained interpretation.

Observed failure:

GROUP_B emitted a CONFIRMED semantic claim citing evidence that was not authoritative enough for CONFIRMED.

Deterministic validator correctly rejected:

CONFIRMED_WITHOUT_AUTHORITY

This is a contract/schema defect, not established model incapability.

==================================================
PRIMARY CORRECTION
==================

Python must determine which claim statuses are legally available BEFORE the request is sent to the LLM.

Do not rely only on post-validation.

For semantic interpretation requests, default allowed claim statuses must be:

INTERPRETED
UNRESOLVED

CONFIRMED must only be exposed when Python determines that the specific claim/evidence relationship satisfies the existing authoritative-evidence contract.

If the request cannot deterministically establish authority:

CONFIRMED must not appear in the request-local schema enum.

==================================================
ARCHITECTURE RULE
=================

For architecture semantic interpretation requests:

LLM-generated architecture conclusions MUST NOT use CONFIRMED.

Allowed semantic claim statuses:

INTERPRETED
UNRESOLVED

Architecture pattern status remains independently:

PATTERN_SUPPORTED
HYBRID_PATTERN
NO_PATTERN_CONFIRMED
INSUFFICIENT_EVIDENCE

PATTERN_SUPPORTED does NOT mean claim status CONFIRMED.

Do not conflate:

pattern interpretation status

with:

evidence authority status.

==================================================
AUTHORITATIVE FACT REPRODUCTION
===============================

If deterministic authoritative facts need to appear in an LLM result, Python owns them.

Example:

WebForms count
ProjectReference count
System.Web.Mvc reference count
data-access counts

The model may reference these facts through allowed evidence aliases.

The model must not reclassify them as newly CONFIRMED semantic claims.

Separate:

deterministic_facts
semantic_interpretations

==================================================
REQUEST-LOCAL SCHEMA
====================

Generate request-local schema constraints based on request purpose.

Example:

SEMANTIC_INTERPRETATION:
claim_status enum =
INTERPRETED
UNRESOLVED

FACT_REPRODUCTION, only if genuinely required and authorized:
claim_status may include CONFIRMED under deterministic authority rules.

Prefer not to ask the model to reproduce facts unnecessarily.

==================================================
PROMPT CONTRACT
===============

Explicitly state:

You are interpreting supplied evidence.

You are not confirming new facts.

Use INTERPRETED when evidence supports a semantic conclusion.

Use UNRESOLVED when evidence is insufficient.

Never upgrade an interpretation to CONFIRMED.

Do not invent evidence.

==================================================
POST-VALIDATION
===============

Keep the existing deterministic validator.

Do NOT weaken:

CONFIRMED_WITHOUT_AUTHORITY

Do NOT silently downgrade:

CONFIRMED -> INTERPRETED

Invalid responses must still be rejected.

The correction must prevent invalid status generation rather than repair it afterward.

==================================================
MODEL ID DIAGNOSTIC DEFECT
==========================

R8.2 also revealed:

EFFECTIVE_MODEL=NOT_RECORDED_DUE_TO_FAILURE

Correct telemetry so provider/model identity is retained independently of semantic validation success/failure when the provider supplies it.

Do not guess model identity.

Failure reporting must preserve:

effective_provider
effective_model when available
request_id
target_group
validation_failure

==================================================
TRANSACTION/PERSISTENCE
=======================

Preserve atomic canonical publication.

Partial valid groups must not become canonical if the complete required transaction fails.

However, diagnostics may safely record non-semantic execution metadata.

Do not persist rejected semantic output as canonical evidence.

==================================================
RERUN
=====

After correction and offline tests PASS:

rerun the complete R8.2 interpretation from the beginning.

Do not reuse GROUP_A's previous in-memory semantic response as canonical.

Execute:

GROUP_A
GROUP_B
GROUP_C

through the corrected contract.

No new raw repository scan.

Reuse immutable R8.1 deterministic evidence.

The user's previous authorization applies to this R8.2 continuation only for the same three compact, sanitized evidence contexts and the same configured runtime provider.

If the execution environment requires explicit authorization again due to security policy, stop and request it rather than bypassing the policy.

==================================================
RETRY POLICY
============

No semantic retries.

One retry only for malformed transport/JSON according to existing R8.2 contract.

Record retries.

==================================================
MODEL FAILURE POLICY
====================

If another failure occurs, classify it:

PROMPT_CONTRACT
SCHEMA
DETERMINISTIC_ENVELOPE
EVIDENCE_SELECTION
CONTEXT_COMPOSITION
MODEL_CAPABILITY

Do not recommend model change unless evidence now demonstrates genuine MODEL_CAPABILITY limitation.

==================================================
TESTS
=====

Add tests covering at minimum:

1 semantic schema excludes CONFIRMED by default
2 architecture semantic schema excludes CONFIRMED
3 PATTERN_SUPPORTED does not imply CONFIRMED
4 deterministic facts separated from semantic interpretations
5 authoritative deterministic facts remain unchanged
6 LLM cannot promote deterministic fact
7 post-validator still rejects CONFIRMED_WITHOUT_AUTHORITY
8 no silent CONFIRMED->INTERPRETED downgrade
9 request-local schema deterministic
10 request-local status enum matches purpose
11 GROUP_B regression fixture
12 provider telemetry retained on validation failure
13 model telemetry retained when provider supplies model
14 model identity never guessed
15 atomic canonical publication preserved
16 rejected responses not persisted
17 R8.1 evidence immutable
18 no raw repository rescan
19 no automatic human approval
20 AI_KNOWLEDGE remains blocked

Run full regression:

python -m unittest discover -s tests

Baseline:

496 PASS

Expected:

> 496 PASS

==================================================
SUCCESSFUL REAL EXECUTION
=========================

Process exactly:

FMI-001
FMI-007
FMI-008
TMI-001
TMI-002
TMI-006
TMI-009
TMI-011

Then deterministically re-evaluate all 20 R8 targets.

==================================================
OUTPUT
======

On successful transaction create/update canonical R8.2 outputs under:

output/v3_r8_2/

including:

INTERPRETATION_REQUESTS.json
INTERPRETATION_RESULTS.json
ARCHITECTURE_INTERPRETATION.json
MISSING_INFORMATION_REEVALUATION.json
DEEP_ANALYSIS_MERGED_SUMMARY.json

Do not overwrite R8.1 evidence.

Do not overwrite reviewed levantamientos.

==================================================
RESULT REPORT
=============

Create:

codex/V3/V3_R8_2_CONTRACT_CORRECTION_RESULTADO.md

FORMAT:

STATUS
ROOT_CAUSE
FILES_CHANGED
CONTRACT_CORRECTION
SCHEMA_CORRECTION
ARCHITECTURE_STATUS_RULE
TELEMETRY_CORRECTION
BASELINE_TESTS
NEW_TESTS
TOTAL_TESTS
REQUEST_GROUPS
REQUEST_TOKEN_ESTIMATES
REAL_LLM_CALLS
RETRIES
EFFECTIVE_PROVIDER
EFFECTIVE_MODEL
GROUP_A_RESULT
GROUP_B_RESULT
GROUP_C_RESULT
EVIDENCE_CLOSURE
FUNCTIONAL_REEVALUATION
TECHNICAL_REEVALUATION
RESOLVED_ITEMS
PARTIALLY_RESOLVED_ITEMS
STILL_UNRESOLVED_ITEMS
HUMAN_KNOWLEDGE_REQUIRED_ITEMS
EXTERNAL_INFORMATION_REQUIRED_ITEMS
SOURCE_IMMUTABILITY
V2_IMMUTABILITY
R8_1_EVIDENCE_IMMUTABILITY
R7_R8_DOCUMENT_IMMUTABILITY
SECURITY
REGRESSION
MODEL_FAILURE_CLASSIFICATION
MODEL_CHANGE_RECOMMENDED
MODEL_CHANGE_REASON
AI_KNOWLEDGE_ALLOWED
DECISION
NEXT

==================================================
EXPECTED SUCCESS
================

STATUS=
V3-R8_2_CONTRACT_CORRECTION_COMPLETE

AI_KNOWLEDGE_ALLOWED=false

DECISION=
EVIDENCE_CONSTRAINED_INTERPRETATION_READY_FOR_HUMAN_REVIEW

NEXT=
SECOND_HUMAN_REVIEW

If another defect occurs:

do not conceal it.

Stop safely and report the exact failure classification.

Stop after report generation.