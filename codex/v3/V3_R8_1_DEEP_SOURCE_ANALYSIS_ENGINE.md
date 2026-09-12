TASK=V3-R8_1_DEEP_SOURCE_ANALYSIS_ENGINE

MODE=DESIGN_IMPLEMENT_TEST_EXECUTE

PARENT=V3-R8_HUMAN_REVIEW_RECORDED_NEEDS_ANALYSIS

TARGET:
Resolve or materially reduce the 20 HUMAN_NEEDS_ANALYSIS items using deeper repository evidence.

CORE PRINCIPLE:

PYTHON DISCOVERS.
LLM INTERPRETS.

Codex is developing the LegacyMapper runtime.
Codex itself must not become part of the final runtime workflow.

==================================================
HUMAN REVIEW INPUT
==================

Human-confirmed:

C04=HUMAN_CONFIRMED

Functional dispositions:

FMI-001=NEEDS_ANALYSIS
FMI-002=NEEDS_ANALYSIS
FMI-003=NEEDS_ANALYSIS
FMI-004=NEEDS_ANALYSIS
FMI-005=NEEDS_ANALYSIS
FMI-006=NEEDS_ANALYSIS
FMI-007=NEEDS_ANALYSIS
FMI-008=NEEDS_ANALYSIS

Technical dispositions:

TMI-001=NEEDS_ANALYSIS
TMI-002=NEEDS_ANALYSIS
TMI-003=NEEDS_ANALYSIS
TMI-004=NEEDS_ANALYSIS
TMI-005=NEEDS_ANALYSIS
TMI-006=NEEDS_ANALYSIS
TMI-007=NEEDS_ANALYSIS
TMI-008=NEEDS_ANALYSIS
TMI-009=NEEDS_ANALYSIS
TMI-010=NEEDS_ANALYSIS
TMI-011=NEEDS_ANALYSIS
TMI-012=NEEDS_ANALYSIS

Architecture human knowledge:

NOT_PROVIDED

Do not assume MVC.
Do not assume any architectural pattern.

==================================================
OBJECTIVE
=========

Implement a reusable Deep Source Analysis capability inside LegacyMapper.

This must NOT be a one-off Codex script.

It must become part of the autonomous LegacyMapper runtime so that future repositories can automatically:

1. detect MissingInformation;
2. determine whether repository evidence can be searched more deeply;
3. execute deterministic deeper analysis;
4. enrich evidence;
5. request LLM interpretation only when deterministic facts need semantic interpretation;
6. re-evaluate unresolved claims;
7. escalate to human review only when repository evidence remains insufficient.

==================================================
ANALYSIS STRATEGY
=================

For each NEEDS_ANALYSIS item classify first:

DETERMINISTIC_DISCOVERY
LLM_INTERPRETATION
EXTERNAL_INFORMATION_REQUIRED
HUMAN_KNOWLEDGE_REQUIRED
NOT_APPLICABLE

Default must NOT be LLM.

Prefer deterministic discovery whenever evidence can be derived from source/project/configuration structure.

==================================================
DETERMINISTIC DISCOVERY AREAS
=============================

Implement or extend analyzers for evidence relevant to the 20 items.

At minimum evaluate:

---

## A. WEBFORM ENTRY-POINT ANALYSIS

Analyze:

.aspx
.ascx
CodeBehind
Inherits
page/control lifecycle
event handlers
button/link/grid events
server controls
code-behind method relationships

Attempt to derive:

WebForm/control
-> event
-> code-behind method
-> called method/class

Do not infer calls from names alone.

---

## B. CALL-GRAPH DEEPENING

Analyze VB.NET source relationships beyond existing shallow boundaries.

Attempt to resolve:

method -> method
method -> class
class -> class
project -> project

Include where deterministically supported:

instance calls
shared/static calls
constructor usage
interface implementation
inheritance
property-backed services
fully-qualified references
imports where resolution is unambiguous

Preserve ambiguity explicitly.

Never nearest-match unresolved symbols.

---

## C. PROJECT DEPENDENCY ANALYSIS

Parse deterministically:

.sln
.vbproj
ProjectReference
Reference
HintPath
assembly references
framework references
COM references if present
configuration-specific references where relevant

Produce:

project -> project
project -> assembly
assembly/version/path metadata when available

Do not treat backup copies as authoritative without provenance.

---

## D. COMPONENT RESPONSIBILITY EVIDENCE

Discover structural evidence for likely component responsibilities from:

project types
namespaces
inheritance
interfaces
implemented methods
call direction
WebForms usage
data-access usage
Oracle usage

Python may classify structural roles only when deterministic rules support them.

Examples of structural roles may include:

WEB_PRESENTATION
BUSINESS_LOGIC_CANDIDATE
DATA_ACCESS_CANDIDATE
SERVICE_CANDIDATE
SHARED_LIBRARY
INTEGRATION_CANDIDATE
UNKNOWN

These are structural classifications, NOT business semantic facts.

Do not convert naming conventions alone into CONFIRMED semantic responsibility.

---

## E. END-TO-END FLOW ANALYSIS

Attempt to expand chains:

WebForm / ASCX
-> code-behind
-> event/method
-> called class/method
-> BL/service candidate
-> SYS/DAL/data access candidate
-> Oracle operation
-> stored procedure / SQL when available

Each hop must contain evidence.

Represent:

COMPLETE
PARTIAL
AMBIGUOUS
UNRESOLVED

Do not fabricate missing hops.

---

## F. DATA-ACCESS SEMANTICS

Analyze deterministically where possible:

OracleCommand
CommandType
CommandText
stored procedure names
parameters
parameter direction
transaction boundaries
ExecuteReader
ExecuteNonQuery
ExecuteScalar
DataSet/DataTable adapters
repository/wrapper methods
connection usage

Link operations back to calling methods where resolvable.

---

## G. STORED PROCEDURE LINKAGE

Improve linkage between:

calling method
data-access operation
package
stored procedure
parameters

Use exact evidence.

Do not infer stored procedure semantics from procedure names as fact.

---

## H. INTEGRATION DISCOVERY

Search repository evidence for external integrations including but not limited to:

SAP
web services
SOAP
WCF
HTTP endpoints
file transfer
filesystem interfaces
email
queues
COM
external assemblies
configured endpoints

Discovery must be deterministic.

Secrets must never be emitted.

Configuration values that may contain credentials/tokens/passwords must be redacted.

---

## I. ARCHITECTURE EVIDENCE ANALYSIS

Do NOT classify architecture from directory names alone.

Collect architecture indicators such as:

project dependency direction
project types
WebForms usage
controller classes if any
System.Web.Mvc references if any
routing configuration if any
shared UI/view organization
business/data access project relationships
interfaces
dependency inversion evidence
service boundaries
shared libraries
framework references
code-behind patterns

Produce an evidence matrix.

Potential pattern labels may only be INTERPRETED by the LLM after deterministic evidence collection.

LLM must be allowed to return:

NO_PATTERN_CONFIRMED
HYBRID_PATTERN
INSUFFICIENT_EVIDENCE

Do not force MVC, layered architecture, Clean Architecture or any other known pattern.

==================================================
DEEP ANALYSIS MODEL
===================

Create a reusable runtime model.

Suggested semantic entities:

DeepAnalysisRequest
DeepAnalysisTarget
DeepEvidence
DeepRelationship
DeepFlow
DependencyEvidence
IntegrationEvidence
ArchitectureIndicator
DeepAnalysisResult

Do not use these exact names if existing architecture provides better canonical naming.

Each result must preserve:

target_missing_information_id
evidence_ids
source_file
source_project when known
symbol/method when known
relationship type
resolution status
confidence/status
provenance
source_snapshot

==================================================
NO FREE-TEXT CONFIDENCE
=======================

Prefer explicit statuses instead of arbitrary percentages.

Examples:

CONFIRMED
PARTIAL
AMBIGUOUS
UNRESOLVED

For architecture interpretation:

SUPPORTED
CONTRADICTED
INSUFFICIENT_EVIDENCE

==================================================
MISSING INFORMATION RE-EVALUATION
=================================

After deterministic discovery, re-evaluate all 20 items.

For each item produce one:

RESOLVED_BY_DETERMINISTIC_EVIDENCE
PARTIALLY_RESOLVED
REQUIRES_LLM_INTERPRETATION
REQUIRES_EXTERNAL_INFORMATION
REQUIRES_HUMAN_KNOWLEDGE
STILL_UNRESOLVED

Do not automatically mark the original human review decision as resolved.

Human review remains authoritative.

==================================================
LLM USE
=======

LLM may be used only after deterministic discovery.

Provider:

existing configured LLM provider abstraction.

Current runtime provider/model must remain configuration-driven.

Do not hardcode:

COPILOT
gpt-5.6-luna
Gemini
or any provider/model.

Use LLM only for semantic interpretation tasks such as:

* describing business meaning of deterministic call chains;
* interpreting architecture evidence;
* summarizing integration responsibility;
* interpreting end-to-end functionality.

Do NOT ask the LLM to discover source-code facts already available to Python.

==================================================
EVIDENCE CONSTRAINT
===================

Reuse the successful R7.2.3 principle.

LLM must receive request-local allowed evidence keys.

Example:

E01
E02
E03

LLM may cite only supplied keys.

Python maps keys back to canonical evidence IDs.

Unknown key:

REJECT RESPONSE

No nearest match.
No silent dropping.
No evidence repair.

==================================================
MODEL FAILURE POLICY
====================

LegacyMapper runtime has NO numeric automatic model-switch threshold.

If a real LLM response fails:

determine whether cause is:

PROMPT_CONTRACT
SCHEMA
DETERMINISTIC_ENVELOPE
EVIDENCE_SELECTION
CONTEXT_COMPOSITION
MODEL_CAPABILITY

Correct deterministic/contract/context problems first.

Only recommend another runtime model when evidence shows a genuine model-capability limitation.

Do not recommend a model change merely because one inference fails.

==================================================
AUTONOMOUS RUNTIME REQUIREMENT
==============================

The Deep Source Analysis capability must be callable from Python without Codex.

Design the execution path so future LegacyMapper runtime can perform approximately:

missing_information
-> analysis planner
-> deterministic discovery
-> evidence enrichment
-> optional LLM interpretation
-> deterministic validation
-> updated assessment candidate
-> human review gate when required

Codex must document the callable runtime entry point.

Do not create a manual-prompt dependency.

==================================================
CURRENT REAL REPOSITORY EXECUTION
=================================

After offline tests pass:

Execute the Deep Source Analysis against the configured legacy repository.

Legacy source remains READ-ONLY.

A deeper source scan is AUTHORIZED for this task.

Do not modify the legacy repository.

Do not scan unrelated filesystem locations.

==================================================
PERFORMANCE
===========

Avoid naïve O(N²) whole-repository comparisons.

Build deterministic indexes for:

symbols
methods
projects
references
WebForms
events
data-access calls
stored procedures
external dependencies

Reuse V1/V2 facts when possible.

Only inspect raw source where existing evidence is insufficient.

==================================================
OUTPUT DIRECTORY
================

Create:

output/v3_r8_1/

At minimum:

DEEP_ANALYSIS_SUMMARY.json
DEEP_ANALYSIS_EVIDENCE.json
DEEP_ANALYSIS_FLOWS.json
PROJECT_DEPENDENCIES.json
EXTERNAL_DEPENDENCIES.json
ARCHITECTURE_EVIDENCE.json
MISSING_INFORMATION_REEVALUATION.json

Do not overwrite V1/V2/R7 outputs.

==================================================
ARCHITECTURE OUTPUT
===================

ARCHITECTURE_EVIDENCE.json must distinguish:

DETERMINISTIC_INDICATORS
LLM_INTERPRETATION
CONTRADICTING_EVIDENCE
UNRESOLVED_EVIDENCE

If LLM interpretation is executed, produce candidate conclusion such as:

PATTERN_CONFIRMED
HYBRID_PATTERN
NO_PATTERN_CONFIRMED
INSUFFICIENT_EVIDENCE

A pattern may only be CONFIRMED if evidence contract permits it.

Otherwise remain INTERPRETED.

==================================================
FUNCTIONAL OUTPUT
=================

For functional NEEDS_ANALYSIS attempt specifically to improve:

FMI-001 functional semantics
FMI-002 entry -> flow -> data mapping
FMI-003 integrations
FMI-004 flow destinations
FMI-005 WebForm/control -> flow/destination
FMI-006 external integrations
FMI-007 data-operation functional context
FMI-008 architecture-related functional context

==================================================
TECHNICAL OUTPUT
================

For technical NEEDS_ANALYSIS attempt specifically to improve:

TMI-001 architecture
TMI-002 component responsibilities
TMI-003 end-to-end flows
TMI-004 external dependencies
TMI-005 project dependencies
TMI-006 architecture evidence
TMI-007 component/project/interface relationships
TMI-008 assemblies/packages/services
TMI-009 business/component responsibility context
TMI-010 external assemblies/versions
TMI-011 architecture/layer boundaries
TMI-012 dependencies/packages/assemblies

==================================================
HUMAN REVIEW SAFETY
===================

Do NOT modify:

FUNCTIONAL_DECISION
TECHNICAL_DECISION

Do NOT automatically approve:

LEVANTAMIENTO_FUNCIONAL.md
LEVANTAMIENTO_TECNICO.md

Do NOT set:

knowledge_source_eligible=true

Do NOT start AI_KNOWLEDGE.

This round produces new evidence for a second human review.

==================================================
DOCUMENT REGENERATION
=====================

Do NOT rewrite the final human documents in this round unless required solely to create a clearly separate candidate preview.

If candidate documents are useful, write only:

output/v3_r8_1/LEVANTAMIENTO_FUNCIONAL_CANDIDATE.md
output/v3_r8_1/LEVANTAMIENTO_TECNICO_CANDIDATE.md

Never overwrite the reviewed DRAFT documents.

==================================================
TESTS
=====

Create/update appropriate tests.

Minimum test families:

1 deterministic analysis planning
2 target classification
3 WebForm event extraction
4 CodeBehind linkage
5 method-call linkage
6 ambiguity preservation
7 project-reference extraction
8 assembly-reference extraction
9 external dependency extraction
10 redaction of secrets
11 data-access extraction
12 Oracle command extraction
13 stored-procedure linkage
14 parameter linkage
15 end-to-end path construction
16 partial-flow preservation
17 unresolved-flow preservation
18 architecture indicator extraction
19 architecture does not assume MVC
20 directory names alone cannot confirm architecture
21 no model/provider hardcoding
22 request-local evidence keys
23 unknown evidence key rejected
24 evidence canonicalization
25 MissingInformation reevaluation
26 resolved status requires evidence
27 partial resolution preserved
28 human knowledge required preserved
29 external information required preserved
30 runtime callable without Codex
31 deterministic repeated run
32 source immutability
33 V2 immutability
34 R7/R8 reviewed docs unchanged
35 assessments unchanged
36 security regression
37 no secret leakage
38 real repository execution bounded to configured root
39 no automatic approval
40 AI_KNOWLEDGE remains blocked

Run:

python -m unittest discover -s tests

Current baseline:

422 PASS

Expected:

> 422 PASS

==================================================
REAL LLM EXECUTION
==================

Real LLM calls are allowed only if deterministic discovery reaches a task that genuinely requires interpretation.

Before each real inference:

* compact context;
* use evidence-constrained contract;
* remain within existing token-budget policy;
* preserve provider/model neutrality.

Record:

REAL_LLM_CALLS
EFFECTIVE_PROVIDER
EFFECTIVE_MODEL
MODEL_CHANGE_RECOMMENDED
MODEL_CHANGE_REASON

Do not hardcode expected model.

==================================================
SUCCESS CRITERIA
================

Successful execution does NOT require resolving all 20 items.

Success requires:

* autonomous deep-analysis capability implemented;
* real repository analyzed safely;
* every NEEDS_ANALYSIS item re-evaluated;
* deterministic evidence increased where possible;
* unresolved items remain explicit;
* optional LLM interpretation evidence-constrained;
* no invented relationships;
* reviewed documents unchanged;
* AI knowledge still blocked pending human re-review.

==================================================
RESULT REPORT
=============

Create:

codex/V3/V3_R8_1_DEEP_SOURCE_ANALYSIS_RESULTADO.md

FORMAT:

STATUS
FILES_CHANGED
RUNTIME_ENTRY_POINT
BASELINE_TESTS
NEW_TESTS
TOTAL_TESTS
SOURCE_ROOT
SOURCE_IMMUTABILITY
V2_IMMUTABILITY
R7_R8_DOCUMENT_IMMUTABILITY
ASSESSMENT_IMMUTABILITY
ANALYSIS_TARGETS
DETERMINISTIC_DISCOVERY
WEBFORM_ENTRY_MAPPING
METHOD_CALL_RESOLUTION
PROJECT_DEPENDENCIES
EXTERNAL_DEPENDENCIES
DATA_ACCESS_LINKAGE
STORED_PROCEDURE_LINKAGE
END_TO_END_FLOWS
ARCHITECTURE_EVIDENCE
FUNCTIONAL_REEVALUATION
TECHNICAL_REEVALUATION
RESOLVED_ITEMS
PARTIALLY_RESOLVED_ITEMS
LLM_INTERPRETATION_ITEMS
STILL_UNRESOLVED_ITEMS
HUMAN_KNOWLEDGE_REQUIRED_ITEMS
EXTERNAL_INFORMATION_REQUIRED_ITEMS
REAL_LLM_CALLS
EFFECTIVE_PROVIDER
EFFECTIVE_MODEL
MODEL_CHANGE_RECOMMENDED
MODEL_CHANGE_REASON
SECURITY
REGRESSION
AI_KNOWLEDGE_ALLOWED
DECISION
NEXT

Expected gate:

AI_KNOWLEDGE_ALLOWED=false

Possible successful status:

V3-R8_1_DEEP_SOURCE_ANALYSIS_COMPLETE

NEXT:

HUMAN_REVIEW_OF_DEEP_ANALYSIS

If implementation or real execution reveals a deterministic design defect:

do not hide it.

Use:

STATUS=V3-R8_1_NEEDS_CORRECTION

and explain exact cause.

==================================================
FINAL RULE
==========

Do not optimize for making all MissingInformation disappear.

Optimize for discovering the maximum amount of verifiable repository evidence while preserving uncertainty honestly.

Stop after report generation.