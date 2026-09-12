TASK=V3-R8_2_EVIDENCE_CONSTRAINED_DEEP_INTERPRETATION

MODE=IMPLEMENT_TEST_EXECUTE

PARENT=V3-R8_1_DEEP_SOURCE_ANALYSIS_COMPLETE

CORE PRINCIPLE:

PYTHON DISCOVERS.
LLM INTERPRETS.

Do not perform another broad repository discovery pass.

Reuse the deterministic evidence already produced by R8.1.

==================================================
INPUT STATE
===========

R8.1 classification:

RESOLVED_BY_DETERMINISTIC_EVIDENCE:
TMI-005

PARTIALLY_RESOLVED:
FMI-002
FMI-003
FMI-004
FMI-005
FMI-006
TMI-003
TMI-004
TMI-007
TMI-008
TMI-010
TMI-012

REQUIRES_LLM_INTERPRETATION:
FMI-001
FMI-007
FMI-008
TMI-001
TMI-002
TMI-006
TMI-009
TMI-011

Use as authoritative R8.1 inputs:

output/v3_r8_1/DEEP_ANALYSIS_SUMMARY.json
output/v3_r8_1/DEEP_ANALYSIS_EVIDENCE.json
output/v3_r8_1/DEEP_ANALYSIS_FLOWS.json
output/v3_r8_1/PROJECT_DEPENDENCIES.json
output/v3_r8_1/EXTERNAL_DEPENDENCIES.json
output/v3_r8_1/ARCHITECTURE_EVIDENCE.json
output/v3_r8_1/MISSING_INFORMATION_REEVALUATION.json

Do not overwrite them.

==================================================
OBJECTIVE
=========

Interpret only the 8 semantic targets that R8.1 determined require LLM interpretation.

The LLM must not discover new source facts.

The LLM may only interpret deterministic evidence already collected by Python.

The execution must produce:

* constrained semantic interpretations;
* validated evidence links;
* updated candidate resolution status for each of the 8 targets;
* architecture interpretation without forcing a pattern;
* functional/data semantics interpretation;
* component responsibility interpretation;
* no automatic human approval.

==================================================
TARGETS
=======

FUNCTIONAL:

FMI-001
FMI-007
FMI-008

TECHNICAL:

TMI-001
TMI-002
TMI-006
TMI-009
TMI-011

Do not send the other 12 targets to the LLM unless strictly required as contextual evidence.

They remain governed by their deterministic R8.1 status.

==================================================
INTERPRETATION PLANNER
======================

Implement or extend a Python planner that creates one or more compact InterpretationRequest objects.

Each request must include:

target_ids
purpose
allowed_evidence_catalog
context_package_ids
source_snapshot_ids
output_schema
token_budget
provider-neutral metadata

Python owns all deterministic envelope fields.

The model owns only semantic interpretation payload.

==================================================
EVIDENCE-CONSTRAINED CONTRACT
=============================

Reuse the successful V3-R7.2.3 principle.

For every request:

Python generates request-local evidence aliases:

E01
E02
E03
...

The LLM may cite only those aliases.

After parsing:

Python maps aliases back to canonical DeepEvidence IDs.

Unknown alias:

REJECT RESPONSE

No nearest matching.
No silent repair.
No evidence dropping.
No invented canonical IDs.

==================================================
NO FACT DISCOVERY BY LLM
========================

Prompt must explicitly prohibit the model from asserting:

new classes
new methods
new projects
new stored procedures
new dependencies
new integrations
new flow edges
new WebForms
new architecture evidence

unless already present in allowed evidence.

LLM output must distinguish:

EVIDENCE_FACT
INTERPRETATION
UNRESOLVED

The LLM must not emit EVIDENCE_FACT claims that are not directly backed by supplied deterministic evidence.

==================================================
FUNCTIONAL INTERPRETATION
=========================

For FMI-001 and FMI-007:

Interpret the business/functional meaning of deterministic evidence relating to:

WebForms
entry points
events
methods
call chains
data-access operations
transactions
Oracle command types
stored procedures
parameters
execution modes

The LLM may describe likely functional meaning only as INTERPRETED unless authoritative evidence supports CONFIRMED.

Do not infer business rules solely from method, class, table or procedure names.

For FMI-008:

Interpret the functional relevance of structural architecture evidence.

Do not force a formal architecture label.

==================================================
TECHNICAL INTERPRETATION
========================

For TMI-001, TMI-006 and TMI-011:

Interpret architecture evidence.

Allowed conclusions:

PATTERN_SUPPORTED
HYBRID_PATTERN
NO_PATTERN_CONFIRMED
INSUFFICIENT_EVIDENCE

A formal architecture must not be CONFIRMED unless deterministic evidence is strong enough under the existing claim contract.

Important current deterministic facts from R8.1 include:

WebForms usage > 0
project-reference direction available
data-access structure available
System.Web.Mvc references = 0

Do not transform absence of System.Web.Mvc into proof of a specific architecture.

For TMI-002 and TMI-009:

Interpret component responsibilities from structural evidence.

Possible semantic roles may be described, but must preserve uncertainty.

No component may be assigned a business responsibility solely from naming.

==================================================
REQUEST PARTITIONING
====================

Prefer small evidence-focused requests.

Do not place all repository evidence in a single prompt.

Partition by semantic target/family.

Recommended grouping:

GROUP A:
FMI-001
FMI-007

GROUP B:
FMI-008
TMI-001
TMI-006
TMI-011

GROUP C:
TMI-002
TMI-009

If evidence size exceeds budget, split further deterministically.

==================================================
TOKEN BUDGET
============

Use existing token estimation policy.

Maximum estimated tokens per request:

5000

Preferred:

<=4200

If request exceeds budget:

compact deterministic evidence
or split the request.

Do not truncate mandatory evidence silently.

==================================================
OUTPUT CONTRACT
===============

For each target produce:

target_id
interpretation_status
semantic_summary
claim_candidates
evidence_aliases
canonical_evidence_ids
unresolved_aspects
recommended_next_status
source_snapshots

interpretation_status allowed:

VALID
INVALID
INSUFFICIENT_EVIDENCE

recommended_next_status allowed:

RESOLVED_WITH_INTERPRETATION
PARTIALLY_RESOLVED_WITH_INTERPRETATION
STILL_UNRESOLVED
REQUIRES_HUMAN_KNOWLEDGE
REQUIRES_EXTERNAL_INFORMATION

Do not use APPROVED.

==================================================
CLAIM STATUS RULES
==================

Claim candidates may be:

CONFIRMED
INTERPRETED
UNRESOLVED

CONFIRMED requires authoritative deterministic evidence under the existing contract.

LLM interpretation alone cannot create CONFIRMED.

If uncertain:

INTERPRETED

If evidence does not support a semantic conclusion:

UNRESOLVED

==================================================
MISSING INFORMATION RE-EVALUATION
=================================

After LLM interpretation:

Python deterministically merges:

R8.1 deterministic evidence
+
validated LLM interpretation

Then re-evaluate all 20 items.

Do not change the recorded human disposition.

Human disposition remains:

NEEDS_ANALYSIS

This round only produces candidate resolution state for the next human review.

==================================================
PARTIALLY RESOLVED ITEMS
========================

Do not ignore R8.1 partially resolved items.

Re-evaluate them deterministically after the interpretation step using the enriched semantic context.

However:

Do not automatically send them to the LLM unless required.

If they can now be upgraded using existing evidence + validated interpretation context, record that.

Otherwise keep PARTIALLY_RESOLVED.

==================================================
ARCHITECTURE RESULT
===================

Create a dedicated architecture interpretation output.

It must include:

deterministic_indicators
contradicting_indicators
llm_interpretation
pattern_status
unresolved_points
evidence_ids

Allowed pattern_status:

PATTERN_SUPPORTED
HYBRID_PATTERN
NO_PATTERN_CONFIRMED
INSUFFICIENT_EVIDENCE

Never output:

MVC_CONFIRMED

unless the deterministic evidence actually supports that claim.

==================================================
MODEL / PROVIDER
================

Use existing configured provider abstraction.

Do not hardcode provider or model.

Record actual:

EFFECTIVE_PROVIDER
EFFECTIVE_MODEL

Current runtime may resolve to GitHub Copilot / gpt-5.6-luna, but this must remain configuration-driven.

==================================================
MODEL FAILURE POLICY
====================

LegacyMapper runtime has no fixed retry/model-switch threshold.

If an inference fails:

classify cause as:

PROMPT_CONTRACT
SCHEMA
DETERMINISTIC_ENVELOPE
EVIDENCE_SELECTION
CONTEXT_COMPOSITION
MODEL_CAPABILITY

Correct deterministic/contract/context issues where appropriate.

Only recommend changing runtime model if failure is genuinely attributable to model capability.

No automatic model change.

==================================================
RETRIES
=======

No semantic retries.

A single retry is allowed only for transport-level malformed JSON or equivalent serialization failure, using the same evidence and semantics contract.

Record every retry.

==================================================
AUTONOMOUS RUNTIME
==================

This capability must remain callable from Python without Codex.

Expose or document a runtime entry point such as:

run_deep_interpretation(...)

or equivalent canonical existing design.

Codex must not become an execution dependency.

==================================================
OUTPUT DIRECTORY
================

Create:

output/v3_r8_2/

At minimum:

INTERPRETATION_REQUESTS.json
INTERPRETATION_RESULTS.json
ARCHITECTURE_INTERPRETATION.json
MISSING_INFORMATION_REEVALUATION.json
DEEP_ANALYSIS_MERGED_SUMMARY.json

Optional candidate human documents:

LEVANTAMIENTO_FUNCIONAL_CANDIDATE.md
LEVANTAMIENTO_TECNICO_CANDIDATE.md

If candidate documents are generated:

do not overwrite the original reviewed DRAFT documents.

==================================================
HUMAN REVIEW GATE
=================

Do not modify:

FUNCTIONAL_DECISION
TECHNICAL_DECISION

Do not change recorded human dispositions.

Do not approve documents.

Do not set:

knowledge_source_eligible=true

Do not start AI_KNOWLEDGE.

Expected:

AI_KNOWLEDGE_ALLOWED=false

==================================================
SOURCE IMMUTABILITY
===================

Do not modify:

legacy repository
V1 artifacts
V2 artifacts
R7/R8 reviewed documents
R8 human decision record
R8.1 deterministic evidence
validated assessments

Record hashes/pre-post checks where appropriate.

==================================================
TESTS
=====

Create/update tests for at least:

1 interpretation planner deterministic
2 only 8 required targets selected
3 provider/model not hardcoded
4 deterministic envelope owned by Python
5 evidence aliases local to request
6 unknown alias rejected
7 canonical evidence mapping
8 no new source facts from LLM
9 CONFIRMED requires deterministic authority
10 interpretation alone cannot confirm
11 unresolved preserved
12 architecture no forced pattern
13 System.Web.Mvc absence not treated as positive architecture proof
14 component responsibility uncertainty preserved
15 token budget enforced
16 deterministic partitioning
17 retry only malformed transport/JSON
18 no semantic retry
19 model-failure classification
20 re-evaluation merges deterministic + semantic evidence
21 human dispositions unchanged
22 no automatic approval
23 AI knowledge blocked
24 runtime callable without Codex
25 source immutability
26 V2 immutability
27 reviewed-doc immutability
28 R8.1 evidence immutability
29 secret-safe prompts/results
30 regression

Run:

python -m unittest discover -s tests

Current baseline:

464 PASS

Expected:

> 464 PASS

==================================================
REAL EXECUTION
==============

After offline tests PASS:

execute real interpretation using configured runtime provider.

Only the 8 semantic targets may trigger real inference.

Use compact evidence-constrained requests.

Do not perform broad raw-repository rescans.

==================================================
RESULT REPORT
=============

Create:

codex/V3/V3_R8_2_EVIDENCE_CONSTRAINED_INTERPRETATION_RESULTADO.md

FORMAT:

STATUS
FILES_CHANGED
RUNTIME_ENTRY_POINT
BASELINE_TESTS
NEW_TESTS
TOTAL_TESTS
INTERPRETATION_TARGETS
REQUEST_GROUPS
REQUEST_TOKEN_ESTIMATES
REAL_LLM_CALLS
RETRIES
EFFECTIVE_PROVIDER
EFFECTIVE_MODEL
MODEL_FAILURE_CLASSIFICATION
MODEL_CHANGE_RECOMMENDED
MODEL_CHANGE_REASON
FUNCTIONAL_INTERPRETATION
TECHNICAL_INTERPRETATION
ARCHITECTURE_INTERPRETATION
RESOLVED_ITEMS
PARTIALLY_RESOLVED_ITEMS
STILL_UNRESOLVED_ITEMS
HUMAN_KNOWLEDGE_REQUIRED_ITEMS
EXTERNAL_INFORMATION_REQUIRED_ITEMS
EVIDENCE_CLOSURE
SOURCE_IMMUTABILITY
V2_IMMUTABILITY
R7_R8_DOCUMENT_IMMUTABILITY
R8_1_EVIDENCE_IMMUTABILITY
SECURITY
REGRESSION
AI_KNOWLEDGE_ALLOWED
DECISION
NEXT

==================================================
SUCCESS
=======

Preferred successful status:

V3-R8_2_INTERPRETATION_COMPLETE

Success does NOT require resolving every item.

Success requires:

* only evidence-backed interpretations;
* all 8 targets processed;
* no hallucinated evidence;
* architecture uncertainty preserved where necessary;
* deterministic reevaluation of all 20 items;
* reviewed documents unchanged;
* AI knowledge still blocked pending explicit human review.

Expected:

AI_KNOWLEDGE_ALLOWED=false

NEXT=SECOND_HUMAN_REVIEW

If execution reveals a contract/design defect:

STATUS=V3-R8_2_NEEDS_CORRECTION

Do not hide the defect.

Stop after report generation.