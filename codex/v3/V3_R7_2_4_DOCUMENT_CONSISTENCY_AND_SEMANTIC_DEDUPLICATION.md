TASK=V3-R7_2_4_DOCUMENT_CONSISTENCY_AND_SEMANTIC_DEDUPLICATION

MODE=IMPLEMENT_AND_EXECUTE

PARENT=V3-R7_2_3
R7_2_3_STATUS=V3-R7_2_3_READY_FOR_HUMAN_REVIEW

NO_R8
NO_AI_KNOWLEDGE
NO_HUMAN_APPROVAL
NO_MODEL_CHANGE
NO_V1_V2_REGENERATION
NO_RAW_REPOSITORY_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_ASSESSMENT_REGENERATION
NO_UNNECESSARY_LLM_CALLS
NO_DIRECT_LLM_MARKDOWN_GENERATION
NO_SEMANTIC_RESPONSE_REPAIR
NO_VALIDATOR_WEAKENING

==================================================
OBJECTIVE
=========

Correct the final documentation quality problems discovered during external review of V3-R7.2.3.

R7.2.3 pipeline architecture is accepted.

Do NOT redesign:

* deterministic envelope;
* evidence catalog;
* evidence-key resolution;
* ContextPackage generation;
* local assessment generation;
* hierarchical synthesis;
* canonical AssessmentValidator.

The problem to solve is the deterministic final-document composition layer.

Primary objectives:

1. validate consistency of quantitative claims;
2. distinguish totals from subsets and differently scoped metrics;
3. prevent ambiguous presentation of non-equivalent counts;
4. semantically consolidate redundant MissingInformation;
5. preserve complete provenance and traceability;
6. regenerate cleaner DRAFT documents;
7. use no new LLM inference unless deterministic processing proves insufficient.

==================================================
ACCEPTED INPUT STATE
====================

Treat these R7.2.3 results as validated inputs:

LOCAL_ASSESSMENTS=16 VALID
INTERMEDIATE_ASSESSMENTS=4 VALID
GLOBAL_ASSESSMENTS=2 VALID

GLOBAL_FUNCTIONAL=PASS
GLOBAL_TECHNICAL=PASS

EVIDENCE_CLOSURE=PASS
TRACEABILITY=PASS

TESTS=299 PASS

Existing documents:

output/LEVANTAMIENTO_FUNCIONAL.md
output/LEVANTAMIENTO_TECNICO.md

Existing persistence:

output/v3_r7_2/LOCAL_ASSESSMENTS.json
output/v3_r7_2/INTERMEDIATE_ASSESSMENTS.json
output/v3_r7_2/COVERAGE_INDEX.json

Use existing validated artifacts.

Do not repeat completed inference.

==================================================
KNOWN DOCUMENT QUALITY ISSUE 1
QUANTITATIVE CONSISTENCY
========================

External review identified apparently conflicting metrics in the technical document.

Example A:

Rendered technical narrative:

"2.009 operaciones de acceso a datos enlazadas"

Coverage metadata:

linked_data_operations=19159

Example B:

Rendered technical narrative:

"674 procedimientos almacenados Oracle identificados"

Coverage metadata:

linked_stored_procedures=5389
total_stored_procedures=5389

Do NOT assume either number is wrong.

Investigate deterministic provenance.

Determine whether the values represent:

* different evidence partitions;
* representative subset counts;
* distinct entity types;
* local/intermediate aggregation counts;
* unique values vs occurrences;
* linked vs identified records;
* filtered categories;
* duplicate-normalized values;
* another deterministic distinction.

The system must explain the distinction if it exists.

If the distinction cannot be established from existing validated artifacts:

mark the narrower statement as scope-ambiguous or UNRESOLVED.

Do not silently replace one value with another.

==================================================
METRIC PROVENANCE MODEL
=======================

Introduce a deterministic metric provenance representation if one does not already exist.

Suggested concept:

MetricFact
{
metric_name,
value,
scope,
population,
aggregation,
source_refs,
source_snapshot,
confidence/status
}

Exact implementation may follow existing project conventions.

Every quantitative statement rendered into final documents must be resolvable to:

VALUE
SCOPE
POPULATION
AGGREGATION
SOURCE

Example:

linked_data_operations
value=19159
scope=SYSTEM
population=DATA_ACCESS
aggregation=linked_records
source=COVERAGE_INDEX

A narrower claim must explicitly identify its narrower scope.

==================================================
METRIC SCOPE
============

Support deterministic scope distinctions such as:

SYSTEM_TOTAL
SYSTEM_LINKED
COVERAGE_PARTITION
REPRESENTATIVE_SUBSET
LOCAL_ASSESSMENT
INTERMEDIATE_ASSESSMENT
GLOBAL_ASSESSMENT
UNRESOLVED_SCOPE

Do not use these exact names if existing project terminology provides better canonical values.

The important requirement is explicit scope.

==================================================
QUANTITATIVE CLAIM VALIDATION
=============================

Before rendering a quantitative global claim:

1. extract its numeric value;
2. resolve evidence;
3. determine metric provenance;
4. compare against deterministic coverage metrics;
5. determine whether values are equivalent or differently scoped.

If equivalent scope and different values:

FAIL document consistency validation.

If different scope:

allow both only if the rendered text explicitly communicates the difference.

If scope cannot be determined:

do not render as an unqualified system-wide fact.

Prefer:

[UNRESOLVED] Existing evidence contains differently scoped counts that cannot yet be deterministically reconciled.

Never guess.

==================================================
SYSTEM METRICS AUTHORITY
========================

COVERAGE_INDEX and deterministic system metrics are authoritative for structural coverage counts when their semantics exactly match the rendered metric.

Examples:

total_projects
represented_webforms
represented_flows
linked_data_operations
linked_stored_procedures

Do NOT use them to overwrite a semantically different assessment metric.

Authority applies only when metric meaning/scope is equivalent.

==================================================
DOCUMENT QUALITY ISSUE 2
MISSING INFORMATION REDUNDANCY
==============================

R7.2.3 reports deterministic MissingInformation merge PASS, but final documents still contain substantial semantic redundancy.

Examples include repeated questions concerning:

TECHNICAL:

* architecture/pattern identification;
* project dependencies;
* external assemblies/packages;
* WebForm -> flow -> data path;
* business-rule/component responsibility.

FUNCTIONAL:

* WebForm/ASCX -> entry_point -> flow;
* flow destination;
* WebForm -> data operation/SP;
* functional meaning of flows/data operations.

The current IDs differ, but the underlying information need is often equivalent.

Do not deduplicate by ID equality only.

==================================================
SEMANTIC DEDUPLICATION WITHOUT LLM
==================================

Implement deterministic semantic-family consolidation.

Preferred strategy:

1. normalize structured fields;
2. classify requests into deterministic information-need families;
3. merge requests within equivalent family when their requested missing fact is equivalent;
4. preserve all source requests/evidence/claims.

Initial families may include:

FUNCTIONAL_ENTRY_FLOW_MAPPING
FUNCTIONAL_FLOW_DESTINATION
FUNCTIONAL_DATA_SEMANTICS
FUNCTIONAL_INTEGRATION_MAPPING
TECHNICAL_ARCHITECTURE_PATTERN
TECHNICAL_PROJECT_DEPENDENCIES
TECHNICAL_EXTERNAL_DEPENDENCIES
TECHNICAL_COMPONENT_RESPONSIBILITY
TECHNICAL_END_TO_END_FLOW

Do not classify only from arbitrary free-text similarity.

Use deterministic signals such as:

profile
section
related claim types
evidence categories
structured request fields
known keywords/tokens
blocking level
relationship types

If deterministic classification is uncertain:

do not merge.

False negatives are preferable to false-positive merges.

==================================================
CANONICAL INFORMATION REQUEST
=============================

For merged requests construct a deterministic canonical representation.

Suggested:

CanonicalMissingInformation
{
canonical_id,
profile,
family,
blocking_level,
question,
reason,
source_request_ids,
related_claim_ids,
evidence_refs,
source_packages,
source_snapshots
}

Question/reason must be selected or composed deterministically.

Do not use an LLM to rewrite them.

Preferred deterministic rule:

* choose the most complete existing question;
* preserve original wording;
* combine provenance separately.

Do not generate new business meaning.

==================================================
BLOCKING LEVEL MERGE
====================

When equivalent requests have different blocking levels:

use the strongest existing level according to canonical severity order.

Example:

BLOCKING_FOR_APPROVAL

> IMPORTANT
> INFORMATIONAL

Do not lower severity.

Record all original severities in provenance if useful.

==================================================
TRACEABILITY
============

A merged MissingInformation item must preserve:

CANONICAL REQUEST
-> ORIGINAL REQUEST IDS
-> RELATED CLAIMS
-> EVIDENCE
-> CONTEXT PACKAGES
-> SOURCE SNAPSHOTS

No provenance may be discarded because of deduplication.

==================================================
IDENTIFIER COLLISIONS
=====================

Current documents contain repeated local IDs such as:

MI001
MI002
FA-R1
M1
REQ-TECHNICAL-ASSESSMENT

These IDs originate from independent assessments and are not globally unique.

Final rendered documents must not present them as globally unique identifiers.

Generate deterministic document-level canonical IDs.

Functional example:

FMI-001
FMI-002
...

Technical example:

TMI-001
TMI-002
...

Preserve original IDs in provenance.

==================================================
DOCUMENT RENDERING
==================

Regenerate:

output/LEVANTAMIENTO_FUNCIONAL.md
output/LEVANTAMIENTO_TECNICO.md

using deterministic rendering only.

The LLM must not write Markdown.

The final documents should contain:

* validated global claims;
* quantitative claims with unambiguous scope;
* canonical MissingInformation requests;
* complete traceability;
* structural coverage;
* explicit distinction between structural and semantic coverage.

==================================================
DOCUMENT STATUS
===============

Remain:

document_status=DRAFT
human_review_required=true
approved=false
knowledge_source_eligible=false

Footer:

STATUS=DRAFT
HUMAN_REVIEW_REQUIRED=true
APPROVED=false
AI_KNOWLEDGE_ALLOWED=false

Do not mark APPROVED.

==================================================
FUNCTIONAL DOCUMENT QUALITY
===========================

Preserve the systematic coverage achieved in R7.2.3:

projects=259 classified
solutions=113
WebForms=3346
flows=12642
linked_data_operations=19159
linked_stored_procedures=5389
unresolved relationships represented=162914

These are structural metrics, not proof of complete semantic understanding.

Do not convert structural coverage into semantic certainty.

==================================================
TECHNICAL DOCUMENT QUALITY
==========================

Specifically verify:

* access-data counts;
* stored-procedure counts;
* solution/project counts;
* WebForm/ASCX counts;
* flow counts;
* unresolved relationship counts.

Any narrower counts retained in narrative must have explicit scope.

Example concept:

"The deterministic system coverage contains 19,159 linked data operations. A narrower validated assessment identified 2,009 records within scope X."

Only use wording like this if scope X can actually be proven.

Otherwise mark distinction unresolved.

==================================================
NO CLAIM PROMOTION
==================

Do not change:

INTERPRETED -> CONFIRMED
UNRESOLVED -> INTERPRETED
UNRESOLVED -> CONFIRMED

solely because of document consistency processing.

R7.2.4 may clarify scope and presentation.

It may not increase semantic certainty.

==================================================
NO CLAIM DELETION
=================

Do not silently delete a validated global claim because it conflicts with another metric.

Instead:

* reconcile scope deterministically;
* or render the conflict explicitly;
* or mark its scope unresolved.

Preserve original claim provenance.

==================================================
LLM POLICY
==========

Target:

NEW_REAL_LLM_CALLS=0

Do not call Copilot/Luna for:

* deduplication;
* metric reconciliation;
* wording cleanup;
* identifier normalization;
* rendering.

If deterministic evidence proves insufficient to distinguish a metric:

leave it unresolved.

Do not call LLM merely to obtain a plausible explanation.

If implementation discovers a genuinely semantic operation impossible to perform safely and deterministically:

STOP.

Report:

LLM_REQUIRED_FOR_SEMANTIC_REVIEW=true

Do not execute the LLM automatically.

==================================================
TESTS
=====

Create/update:

tests/test_v3_r7_2_4.py

Minimum offline tests:

1 MetricFact deterministic serialization
2 metric scope preserved
3 metric provenance preserved
4 system metric resolves from coverage index
5 equivalent metric same value PASS
6 equivalent metric different value FAIL
7 differently scoped metric different value allowed
8 differently scoped metric requires explicit rendered scope
9 unresolved metric scope not rendered as system-wide fact
10 2009 vs 19159 fixture cannot be silently reconciled
11 674 vs 5389 fixture cannot be silently reconciled
12 system coverage metric not used to overwrite different semantic metric
13 quantitative claim retains evidence
14 quantitative claim retains snapshot
15 functional MissingInformation family classification
16 technical architecture family classification
17 project dependency family classification
18 external dependency family classification
19 end-to-end flow family classification
20 uncertain classification remains separate
21 same family equivalent requests merge
22 different families do not merge
23 merged request preserves all source IDs
24 merged request preserves all evidence
25 merged request preserves all claims
26 merged request preserves packages
27 merged request preserves snapshots
28 strongest blocking level retained
29 original blocking levels recoverable
30 canonical functional IDs deterministic
31 canonical technical IDs deterministic
32 duplicate local IDs do not collide globally
33 canonical ordering deterministic
34 no LLM used for deduplication
35 no LLM used for metric reconciliation
36 no LLM used for rendering
37 global claims not semantically rewritten
38 claim status not promoted
39 claim source_type preserved
40 original conflicting claim provenance preserved
41 functional structural coverage retained
42 technical structural coverage retained
43 structural coverage explicitly distinguished from semantic coverage
44 traceability closure after deduplication
45 no dangling original MissingInformation refs
46 regenerated functional document DRAFT
47 regenerated technical document DRAFT
48 human review required
49 knowledge source eligibility false
50 AI_KNOWLEDGE blocked
51 legacy source immutable
52 V2 artifacts unchanged
53 local assessments unchanged
54 intermediate/global assessments semantically unchanged
55 deterministic repeated render byte-identical where existing conventions allow
56 zero provider calls in successful deterministic execution
57 LegacyMapper model-change policy unaffected

Run:

python -m unittest discover -s tests

Baseline:

299 PASS

Expected:

> 299 PASS

==================================================
PRE-EXECUTION HASHES
====================

Before modification/execution record hashes for:

V2 source artifacts
LOCAL_ASSESSMENTS.json
INTERMEDIATE_ASSESSMENTS.json

After execution verify:

V2 hashes unchanged.

Assessment semantic payloads unchanged.

If persistence metadata must change for a deterministic reason, explain exactly why.

Preferred:

do not modify assessment persistence at all.

==================================================
EXECUTION
=========

After tests PASS:

1. load validated R7.2.3 artifacts;
2. build metric provenance index;
3. run quantitative consistency validation;
4. build canonical MissingInformation sets;
5. validate traceability closure;
6. deterministically regenerate both documents;
7. rerun consistency validation against rendered documents;
8. rerun full test suite;
9. verify hashes/immutability;
10. produce report.

No provider call should occur.

==================================================
SUCCESS CRITERIA
================

Success requires:

METRIC_PROVENANCE=PASS
QUANTITATIVE_CONSISTENCY=PASS
MISSING_INFORMATION_CANONICALIZATION=PASS
SEMANTIC_DEDUPLICATION=PASS
TRACEABILITY=PASS
FUNCTIONAL_DOCUMENT=PASS
TECHNICAL_DOCUMENT=PASS
NEW_REAL_LLM_CALLS=0
REGRESSION=PASS
SOURCE_IMMUTABILITY=PASS
ASSESSMENTS_UNCHANGED=PASS
AI_KNOWLEDGE_BLOCKED=PASS

==================================================
SUCCESS STATUS
==============

STATUS=V3-R7_2_4_READY_FOR_HUMAN_REVIEW

DECISION=DOCUMENT_CONSISTENCY_AND_SEMANTIC_DEDUPLICATION_VALIDATED

NEXT=V3-R8_HUMAN_REVIEW_NOT_STARTED

==================================================
FAILURE STATES
==============

If quantitative conflict cannot be safely represented:

STATUS=V3-R7_2_4_METRIC_CONSISTENCY_FAILURE

If deterministic deduplication cannot preserve meaning:

STATUS=V3-R7_2_4_DEDUPLICATION_FAILURE

If traceability breaks:

STATUS=V3-R7_2_4_TRACEABILITY_FAILURE

If existing assessment corruption is discovered:

STATUS=V3-R7_2_4_ASSESSMENT_INTEGRITY_FAILURE

If semantic LLM review is actually required:

STATUS=V3-R7_2_4_REQUIRES_SEMANTIC_REVIEW

Do not start R8.

==================================================
REPORT
======

Create ONLY:

codex/V3/V3_R7_2_4_RESULTADO.md

FORMAT:

STATUS
FILES_CHANGED
PRECONDITIONS
INPUT_ASSESSMENTS
PRE_EXECUTION_HASHES
METRIC_PROVENANCE
QUANTITATIVE_CONSISTENCY
DATA_OPERATION_METRIC_ANALYSIS
STORED_PROCEDURE_METRIC_ANALYSIS
METRIC_SCOPE_RULES
SYSTEM_METRIC_AUTHORITY
MISSING_INFORMATION_INPUT_COUNTS
MISSING_INFORMATION_FAMILIES
MISSING_INFORMATION_CANONICALIZATION
MISSING_INFORMATION_OUTPUT_COUNTS
FUNCTIONAL_DEDUPLICATION
TECHNICAL_DEDUPLICATION
BLOCKING_LEVEL_MERGE
IDENTIFIER_NORMALIZATION
TRACEABILITY
FUNCTIONAL_DOCUMENT
TECHNICAL_DOCUMENT
STRUCTURAL_VS_SEMANTIC_COVERAGE
NEW_REAL_LLM_CALLS
LLM_REQUIRED_FOR_SEMANTIC_REVIEW
ASSESSMENTS_UNCHANGED
V2_IMMUTABILITY
SOURCE_IMMUTABILITY
UNIT_TESTS
TOTAL_TESTS
REGRESSION
SECURITY
KNOWN_LIMITATIONS
FAILURES
DECISION
NEXT

Stop.