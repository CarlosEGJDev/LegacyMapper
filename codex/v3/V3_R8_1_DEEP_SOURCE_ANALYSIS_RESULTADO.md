STATUS
V3-R8_1_DEEP_SOURCE_ANALYSIS_COMPLETE

FILES_CHANGED
legacy_documenter/analysis/deep_source.py
tests/test_v3_r8_1.py
output/v3_r8_1/DEEP_ANALYSIS_SUMMARY.json
output/v3_r8_1/DEEP_ANALYSIS_EVIDENCE.json
output/v3_r8_1/DEEP_ANALYSIS_FLOWS.json
output/v3_r8_1/PROJECT_DEPENDENCIES.json
output/v3_r8_1/EXTERNAL_DEPENDENCIES.json
output/v3_r8_1/ARCHITECTURE_EVIDENCE.json
output/v3_r8_1/MISSING_INFORMATION_REEVALUATION.json
codex/V3/V3_R8_1_DEEP_SOURCE_ANALYSIS_RESULTADO.md

RUNTIME_ENTRY_POINT
legacy_documenter.analysis.deep_source.run(source_root, output_dir); CLI: python -m legacy_documenter.analysis.deep_source SOURCE_ROOT --output OUTPUT_DIR. No Codex/manual-prompt dependency.

BASELINE_TESTS
422 PASS

NEW_TESTS
42 PASS: planning, target classification, WebForms/events/code-behind, project/assembly dependencies, integrations, redaction, Oracle/data access, flow statuses, architecture safety, reevaluation, deterministic identity and runtime autonomy.

TOTAL_TESTS
464 PASS

SOURCE_ROOT
C:\Users\cgalianj\source\IST_40\operacional; scan bounded to this configured root.

SOURCE_IMMUTABILITY
PASS: 18,455 source files before/after; metadata tree hash c65b0a03ae7895d885c8d9b28705acc9cce1913904c3e42fc0bd342a0ac5871e unchanged.

V2_IMMUTABILITY
PASS: 34-file aggregate SHA-256 bc73783aafc53e2029f656edd502291501aac8e0da3a7a76167095d824bd556f unchanged.

R7_R8_DOCUMENT_IMMUTABILITY
PASS: LEVANTAMIENTO_FUNCIONAL.md=e31a35fac44259bde1e362bfa03d3854bce9e3f157a3163ab6c17096f7ab9fc7; LEVANTAMIENTO_TECNICO.md=ccaf7af9ad2892af11457911557ab9cbaa4ee54b51031c8d52f3c1a5eb6e5e0f; unchanged and not approved.

ASSESSMENT_IMMUTABILITY
PASS: LOCAL_ASSESSMENTS.json=fbac45f95913d56f138cb89eef3b811b522c348135ac05cd10f02ea608e0bc6d; INTERMEDIATE_ASSESSMENTS.json=f6e6bc37ca6d470900b0b26e63a0ff31b198695957df8769ae643214960dc293; unchanged.

ANALYSIS_TARGETS
20/20 NEEDS_ANALYSIS items planned and reevaluated. Default strategy is deterministic discovery; semantic-only targets are explicitly classified LLM_INTERPRETATION after evidence discovery.

DETERMINISTIC_DISCOVERY
15,138 classified files; 3,346 WebForms/controls; 12,662 entry points; 4,328 call-index records; 20,082 data-access operations; 5,389 stored procedures; 12,642 flows; 170,020 evidence-bearing paths; zero extraction errors.

WEBFORM_ENTRY_MAPPING
12,662 entry-point records link WebForm/control metadata, CodeBehind/CodeFile, Inherits, event, handler and resolved start method when available. Missing start methods remain UNRESOLVED.

METHOD_CALL_RESOLUTION
Existing indexed symbol/call resolution reused and deep flow depth increased to 20. Calls are resolved only by deterministic resolver rules; ambiguous or unresolved boundaries are preserved and no nearest matching is used.

PROJECT_DEPENDENCIES
167 ProjectReference relationships: 124 CONFIRMED exact targets and 43 UNRESOLVED. Project, GUID/name and source snapshot provenance retained.

EXTERNAL_DEPENDENCIES
4,838 assembly references with version and sanitized HintPath metadata where present. 3,871 source integration indicators: COM=3511, WebService=259, SOAP=69, MailMessage=23, WebRequest=6, SMTP=2, SAP=1.

DATA_ACCESS_LINKAGE
20,082 indexed operations retain source file/project, class/method, provider, command type/text, execution mode, transactions and canonical evidence when deterministically available.

STORED_PROCEDURE_LINKAGE
5,389 canonical stored procedures linked through exact data-access evidence; associated parameter index preserved. No procedure-name business semantics inferred.

END_TO_END_FLOWS
12,642 flows and 170,020 paths generated through entry -> handler/method -> calls -> data operation -> stored procedure/SQL/unresolved boundary. COMPLETE/PARTIAL/AMBIGUOUS/UNRESOLVED semantics remain evidence-driven.

ARCHITECTURE_EVIDENCE
WebForms usage=3,346 SUPPORTED; project-reference direction=167 SUPPORTED; data-access operations=20,082 SUPPORTED; System.Web.Mvc references=0 INSUFFICIENT_EVIDENCE. pattern_confirmed=false; LLM interpretation NOT_EXECUTED; formal architecture remains unconfirmed.

FUNCTIONAL_REEVALUATION
FMI-002,FMI-003,FMI-004,FMI-005,FMI-006=PARTIALLY_RESOLVED. FMI-001,FMI-007,FMI-008=REQUIRES_LLM_INTERPRETATION with deterministic evidence supplied.

TECHNICAL_REEVALUATION
TMI-005=RESOLVED_BY_DETERMINISTIC_EVIDENCE. TMI-003,TMI-004,TMI-007,TMI-008,TMI-010,TMI-012=PARTIALLY_RESOLVED. TMI-001,TMI-002,TMI-006,TMI-009,TMI-011=REQUIRES_LLM_INTERPRETATION.

RESOLVED_ITEMS
TMI-005

PARTIALLY_RESOLVED_ITEMS
FMI-002,FMI-003,FMI-004,FMI-005,FMI-006,TMI-003,TMI-004,TMI-007,TMI-008,TMI-010,TMI-012

LLM_INTERPRETATION_ITEMS
FMI-001,FMI-007,FMI-008,TMI-001,TMI-002,TMI-006,TMI-009,TMI-011

STILL_UNRESOLVED_ITEMS
None at this reevaluation category; partial and interpretation-required items retain unresolved portions and are not considered resolved.

HUMAN_KNOWLEDGE_REQUIRED_ITEMS
None classified at this stage. Human review remains authoritative after deeper evidence assessment.

EXTERNAL_INFORMATION_REQUIRED_ITEMS
None classified at this stage.

REAL_LLM_CALLS
0

EFFECTIVE_PROVIDER
NOT_EXECUTED

EFFECTIVE_MODEL
NOT_EXECUTED

MODEL_CHANGE_RECOMMENDED
false

MODEL_CHANGE_REASON
No model execution or model-capability failure occurred. Provider/model selection remains configuration-driven.

SECURITY
PASS: centralized recursive sanitization applied; source excerpts bounded; audit found 0 unredacted password/pwd/token/secret/user-id assignments in final JSON. No credential output, source write, external service or unrestricted filesystem scan.

REGRESSION
PASS: python -m unittest discover -s tests; 464 tests.

AI_KNOWLEDGE_ALLOWED
false

DECISION
DEEP_SOURCE_EVIDENCE_READY_FOR_HUMAN_REVIEW

NEXT
HUMAN_REVIEW_OF_DEEP_ANALYSIS
