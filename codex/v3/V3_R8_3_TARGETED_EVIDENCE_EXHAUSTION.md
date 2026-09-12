# LegacyMapper — V3-R8.3 Targeted Evidence Exhaustion

TASK=V3-R8_3_TARGETED_EVIDENCE_EXHAUSTION

MODE=IMPLEMENT_TEST_EXECUTE

PARENT=V3-R8_2_CONTRACT_CORRECTION_COMPLETE

## 1. Objective

Perform one final bounded evidence analysis for exactly:

* FMI-007
* TMI-001
* TMI-011

These targets were classified by R8.2 as:

REQUIRES_EXTERNAL_INFORMATION

Do NOT assume that external information is actually required yet.

R8.2 showed that the interpretation context did not sufficiently expose the target-specific meaning and/or relevant relationships.

The objective is to distinguish:

1. information already discoverable from repository evidence;
2. information that exists but was omitted from the R8.2 context;
3. information that can only be partially inferred;
4. information genuinely absent from repository evidence.

CORE PRINCIPLE:

PYTHON DISCOVERS.
LLM INTERPRETS.
HUMAN APPROVES.

---

## 2. Scope

Analyze ONLY:

FMI-007
TMI-001
TMI-011

Do not reopen the other 17 MissingInformation items.

Preserve their current candidate states.

Do not start a new global repository analysis.

---

## 3. First Mandatory Step — Recover Original Meaning

Before inspecting additional evidence, Python must recover the complete original definition of:

FMI-007
TMI-001
TMI-011

from the canonical R7/R8 documentation/assessment artifacts.

For each target recover, where available:

* original ID
* original description/question
* document/profile
* original claim/context
* reason it was missing
* blocking status
* original evidence references
* human disposition
* previous analysis status

Produce:

TARGET_DEFINITIONS.json

The exact original target meaning must become part of the analysis contract.

Do not ask an LLM to interpret an identifier whose original semantic definition is missing.

If the canonical definition cannot be recovered:

classify:

TARGET_DEFINITION_MISSING

and report the contract/data defect.

Do NOT classify it as EXTERNAL_INFORMATION_REQUIRED.

---

## 4. Existing Evidence First

Before reading additional source files, search/reconcile existing deterministic artifacts from:

V1
V2
R7
R8
R8.1
R8.2

especially:

output/v3_r8_1/DEEP_ANALYSIS_SUMMARY.json
output/v3_r8_1/DEEP_ANALYSIS_EVIDENCE.json
output/v3_r8_1/DEEP_ANALYSIS_FLOWS.json
output/v3_r8_1/PROJECT_DEPENDENCIES.json
output/v3_r8_1/EXTERNAL_DEPENDENCIES.json
output/v3_r8_1/ARCHITECTURE_EVIDENCE.json
output/v3_r8_1/MISSING_INFORMATION_REEVALUATION.json

output/v3_r8_2/INTERPRETATION_REQUESTS.json
output/v3_r8_2/INTERPRETATION_RESULTS.json
output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json
output/v3_r8_2/DEEP_ANALYSIS_MERGED_SUMMARY.json

Prefer existing indexed evidence.

Do not regenerate R8.1 globally.

---

## 5. Targeted Source Lookup

Only if existing evidence cannot answer a specific part of a target:

allow bounded READ-ONLY source lookup.

The lookup must be derived from the recovered target definition and existing evidence.

Allowed examples:

* exact project reference resolution;
* exact config sections;
* exact assembly references;
* exact WebService references;
* exact SOAP endpoints/configuration;
* exact WebRequest usage;
* exact SMTP/MailMessage configuration or usage;
* exact COM references;
* exact SAP-related references;
* exact dependency declarations;
* exact project ownership/dependency relationships.

Do NOT perform:

* full repository rescan;
* unrestricted semantic scan;
* broad rediscovery of WebForms;
* regeneration of V1/V2;
* source modifications.

Every targeted lookup must record:

target_id
lookup_reason
lookup_scope
files_examined
evidence_found
evidence_not_found

---

## 6. FMI-007 Analysis

Recover the exact original definition first.

Then determine what functional information FMI-007 actually requests.

Do not infer its meaning from the identifier.

Use existing integration/dependency evidence and, if necessary, bounded source lookup.

Determine whether the requested functional information is:

RESOLVED_BY_EXISTING_EVIDENCE
RESOLVED_BY_TARGETED_DISCOVERY
PARTIALLY_RESOLVED
EVIDENCE_EXHAUSTED
TARGET_DEFINITION_MISSING

Do not infer business purpose solely from:

assembly names
class names
stored procedure names
service names
configuration keys

If structural evidence exists but business semantics cannot be established, preserve that distinction.

---

## 7. TMI-001 Analysis

Recover the exact original definition first.

Determine the exact dependency/technical relationship requested.

Use:

PROJECT_DEPENDENCIES.json
project ownership evidence
ProjectReference resolution
assembly references
solution/project mappings
existing architecture evidence

R8.1 recorded both resolved and unresolved ProjectReference relationships.

Attempt deterministic resolution only where exact evidence permits.

No nearest-name matching.

No filename similarity inference.

No project ownership inference without evidence.

If unresolved references remain after bounded deterministic analysis, record them explicitly.

Distinguish:

dependency inventory known

from:

complete dependency semantics known.

---

## 8. TMI-011 Analysis

Recover the exact original definition first.

Determine which external integrations/integration semantics it requests.

Use existing R8.1 evidence including indicators for:

COM
WebService
SOAP
MailMessage
WebRequest
SMTP
SAP
assembly references

Where necessary, perform bounded source/config lookup to determine:

integration type
declared endpoint if non-secret
referencing component/project
source location
protocol/technology
direction where deterministically supported

Do not expose:

credentials
passwords
tokens
connection-string secrets
private keys
authentication headers

Sanitize sensitive values.

Do not infer business purpose from integration names alone.

Distinguish:

INTEGRATION_PRESENT

from:

INTEGRATION_PURPOSE_KNOWN

and:

RUNTIME_BEHAVIOR_CONFIRMED.

---

## 9. Evidence Exhaustion Contract

For each target produce:

target_id
original_definition
analysis_steps
existing_evidence_used
targeted_lookups
new_deterministic_evidence
remaining_unknowns
evidence_exhausted
candidate_status
external_information_reason

Allowed candidate_status:

RESOLVED_BY_EXISTING_EVIDENCE
RESOLVED_BY_TARGETED_DISCOVERY
PARTIALLY_RESOLVED
EXTERNAL_INFORMATION_REQUIRED
TARGET_DEFINITION_MISSING

EXTERNAL_INFORMATION_REQUIRED may only be assigned when:

1. original target definition is known;
2. relevant existing evidence was checked;
3. bounded source lookup was performed when applicable;
4. repository evidence is insufficient for the requested information;
5. remaining information cannot be established without speculation.

Set:

evidence_exhausted=true

when these conditions are satisfied.

---

## 10. Optional LLM Interpretation

Use LLM only if deterministic evidence is found but semantic interpretation is required.

Do not invoke LLM merely to search.

Use existing LLMProvider abstraction.

Provider/model must remain configuration-driven.

Python owns:

target identity
original target definition
evidence catalog
source snapshots
allowed evidence aliases
candidate status envelope

LLM owns only semantic interpretation.

Use request-local:

AllowedEvidenceCatalog

with aliases:

E01
E02
E03
...

Unknown evidence alias:

REJECT

No nearest matching.
No silent repair.
No evidence invention.

Semantic claim statuses:

INTERPRETED
UNRESOLVED

Do not expose CONFIRMED to the LLM.

---

## 11. External Provider Safety

Do not send raw repository files to an external LLM provider.

Only compact sanitized evidence contexts may be transmitted.

Before any external inference record:

sanitized=true/false
secret_scan_pass=true/false
estimated_tokens
target_ids

If external transmission requires explicit authorization under current security policy:

STOP and request authorization.

Do not bypass the gate.

---

## 12. Human Decisions

Do not alter previous human decisions.

Preserve:

C04=HUMAN_CONFIRMED

Preserve the existing dispositions for the other R8 targets.

This round generates candidate evidence status only.

Do not automatically human-confirm anything.

---

## 13. Architecture

Do not reopen general architecture analysis.

Existing accepted interpretation remains:

WebForms-oriented evidence is supported.

MVC is not established.

Other architectural patterns may coexist.

Do not attempt to force a formal architecture classification in this round.

---

## 14. Outputs

Create:

output/v3_r8_3/

At minimum:

TARGET_DEFINITIONS.json
TARGETED_LOOKUPS.json
TARGETED_EVIDENCE.json
TARGET_REEVALUATION.json
EVIDENCE_EXHAUSTION_SUMMARY.json

If LLM interpretation is executed:

INTERPRETATION_REQUESTS.json
INTERPRETATION_RESULTS.json

Do not overwrite:

output/v3_r8_1/
output/v3_r8_2/

---

## 15. Tests

Add tests for at least:

1. exactly three targets selected;
2. original definitions recovered;
3. missing target definition is not classified external;
4. existing evidence checked before source lookup;
5. source lookup bounded by target;
6. no full repository rescan;
7. exact project-reference resolution only;
8. no nearest-name dependency matching;
9. integration presence separated from purpose;
10. runtime behavior not inferred from declaration;
11. secrets sanitized;
12. credentials never emitted;
13. evidence exhaustion requirements enforced;
14. external information cannot be selected prematurely;
15. LLM optional;
16. LLM does not perform discovery;
17. semantic schema excludes CONFIRMED;
18. unknown evidence aliases rejected;
19. provider/model configuration-driven;
20. previous human decisions immutable;
21. R8.1 immutable;
22. R8.2 immutable;
23. V2 immutable;
24. legacy source read-only;
25. AI_KNOWLEDGE blocked;
26. regression.

Run:

python -m unittest discover -s tests

Current baseline:

516 PASS

Expected:

> 516 PASS

---

## 16. Real Execution

After offline tests PASS:

execute the targeted analysis against the configured legacy source.

Do not perform global rediscovery.

Only bounded reads required by:

FMI-007
TMI-001
TMI-011

are authorized.

If compact sanitized evidence subsequently requires LLM semantic interpretation, use the existing provider abstraction subject to the external-transmission security gate.

---

## 17. Immutability

Verify:

SOURCE_IMMUTABILITY
V2_IMMUTABILITY
R7_R8_DOCUMENT_IMMUTABILITY
R8_1_IMMUTABILITY
R8_2_IMMUTABILITY

Legacy source is READ-ONLY.

---

## 18. AI Knowledge Gate

AI_KNOWLEDGE_ALLOWED=false

Do not generate AI_KNOWLEDGE.

Do not approve levantamientos.

This round precedes final second human review.

---

## 19. Result Report

Create:

codex/V3/V3_R8_3_TARGETED_EVIDENCE_EXHAUSTION_RESULTADO.md

Required format:

STATUS
FILES_CHANGED
RUNTIME_ENTRY_POINT
BASELINE_TESTS
NEW_TESTS
TOTAL_TESTS
TARGETS
TARGET_DEFINITIONS
EXISTING_EVIDENCE_ANALYSIS
TARGETED_SOURCE_LOOKUPS
FMI_007_RESULT
TMI_001_RESULT
TMI_011_RESULT
RESOLVED_BY_EXISTING_EVIDENCE
RESOLVED_BY_TARGETED_DISCOVERY
PARTIALLY_RESOLVED
EXTERNAL_INFORMATION_REQUIRED
TARGET_DEFINITION_MISSING
EVIDENCE_EXHAUSTED
REAL_LLM_CALLS
RETRIES
EFFECTIVE_PROVIDER
EFFECTIVE_MODEL
MODEL_FAILURE_CLASSIFICATION
MODEL_CHANGE_RECOMMENDED
MODEL_CHANGE_REASON
SOURCE_IMMUTABILITY
V2_IMMUTABILITY
R7_R8_DOCUMENT_IMMUTABILITY
R8_1_IMMUTABILITY
R8_2_IMMUTABILITY
SECURITY
REGRESSION
AI_KNOWLEDGE_ALLOWED
DECISION
NEXT

---

## 20. Success

Preferred successful status:

V3-R8_3_TARGETED_EVIDENCE_EXHAUSTION_COMPLETE

Success does NOT require resolving all three targets.

Success means LegacyMapper can demonstrate whether repository evidence for each target has genuinely been exhausted.

If repository evidence resolves a target:

preserve the evidence and candidate result.

If evidence is genuinely exhausted:

EXTERNAL_INFORMATION_REQUIRED is valid.

If target definition was missing from the interpretation context but exists canonically:

correct the context and continue.

If canonical target definition itself cannot be recovered:

report TARGET_DEFINITION_MISSING.

Expected:

AI_KNOWLEDGE_ALLOWED=false

DECISION=
TARGETED_EVIDENCE_READY_FOR_SECOND_HUMAN_REVIEW

NEXT=
V3-R8_4_SECOND_HUMAN_REVIEW

Stop after report generation.