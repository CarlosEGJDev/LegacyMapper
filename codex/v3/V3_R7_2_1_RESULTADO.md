STATUS
V3-R7_2_1_MODEL_CONTRACT_FAILURE

FILES_CHANGED
legacy_documenter/documentation/synthesis.py
legacy_documenter/documentation/hierarchical.py
tests/test_v3_r7_2_1.py
output/v3_r7_2/LOCAL_ASSESSMENTS.json
codex/V3/V3_R7_2_1_RESULTADO.md

PRECONDITIONS
PASS: V2-R5.1, R7.1 canonical contract, R7.2 planner, CopilotProvider, authentication and existing R7.1 drafts available.

ROOT_CAUSE
The eighth functional local response copied a source snapshot value that did not exactly match the schema/request constant. Request preflight passed; this is a comparable model-contract failure, not a budget or implementation-mapping failure.

PERSISTENCE_IMPLEMENTATION
IMPLEMENTED: canonical deterministic serialization, temporary file, flush+fsync, atomic os.replace, content hash, validation marker and complete request identity.

LOCAL_CACHE
7 validated LOCAL_FUNCTIONAL assessments persisted in output/v3_r7_2/LOCAL_ASSESSMENTS.json. The rejected eighth assessment was not persisted.

CACHE_REUSE
0 reused in this first corrected execution.

CACHE_INVALIDATIONS
0

CHECKPOINTING
PASS: seven successful checkpoints survived the subsequent semantic failure and remain reusable by exact identity.

SYNTHESIS_PLANNER
IMPLEMENTED and offline validated: exact deduplication, compact claims, deterministic token-based partitioning, provenance retention and maximum depth enforcement.

HIERARCHY_DEPTH
0 synthesis levels executed; failure occurred during local functional assessment completion.

LOCAL_FUNCTIONAL_ASSESSMENTS
7 valid persisted; eighth response rejected for snapshot mismatch.

LOCAL_TECHNICAL_ASSESSMENTS
NOT EXECUTED

INTERMEDIATE_FUNCTIONAL_ASSESSMENTS
NOT EXECUTED; no intermediate cache created.

INTERMEDIATE_TECHNICAL_ASSESSMENTS
NOT EXECUTED

GLOBAL_FUNCTIONAL_SYNTHESIS
NOT EXECUTED

GLOBAL_TECHNICAL_SYNTHESIS
NOT EXECUTED

MAX_REQUEST_ESTIMATED_TOKENS
4759 across planned local requests; all <=5000.

SELECTED_PROVIDER
COPILOT

MODEL_ID
gpt-5.6-luna (effective SDK response model; selection remained auto/configured, not hardcoded).

REAL_CALLS_EXECUTED
8 primary calls

RETRIES
0; semantic snapshot mismatch was not retried.

ASSESSMENT_VALIDATION
7 PASS; 1 FAIL. AssessmentValidator and exact snapshot enforcement remained authoritative.

STATUS_PROPAGATION
No promotion observed in persisted assessments; hierarchy not reached.

MISSING_INFORMATION_DEDUPLICATION
Implemented and offline-tested; real hierarchical merge not reached.

FUNCTIONAL_DOCUMENT
Existing R7.1 DRAFT retained; not overwritten from incomplete/unvalidated hierarchy. Size remains 9041 bytes.

TECHNICAL_DOCUMENT
Existing R7.1 DRAFT retained; not overwritten. Size remains 11132 bytes.

COVERAGE_R7_1_VS_R7_2_1
Not available because global synthesis and R7.2.1 document generation did not complete.

TRACEABILITY
Persisted local assessments retain exact package, snapshot, claims and evidence identity. End-to-end global traceability not produced.

UNIT_TESTS
PASS: 40 new offline tests.

TOTAL_TESTS
201 PASS

REGRESSION
PASS: python -m unittest discover -s tests

SOURCE_IMMUTABILITY
PASS by execution design: existing V2 outputs only; no raw scan or write path to the legacy repository.

SECURITY
PASS: no credentials, environment dump, raw auth payload, model tools, shell, Git, MCP actions or legacy writes; invalid raw response not persisted.

MODEL_OBSERVATIONS
Seven consecutive bounded functional assessments complied. The eighth violated only the exact source_snapshot constraint despite canonical const/schema instructions.

MODEL_CHANGE_RECOMMENDED
false; this is the first comparable post-R7.1 model-contract failure and does not meet the established three-failure threshold.

KNOWN_LIMITATIONS
Execution can resume using seven exact validated checkpoints, but the rejected semantic response cannot be retried under this round's policy without a new explicit execution instruction.

FAILURES
MODEL_CONTRACT: snapshot, snapshot exact.

DECISION
MODEL_OUTPUT_REJECTED_CHECKPOINTS_PRESERVED

NEXT
V3-R7_2_1_NOT_CLOSED; V3-R8_HUMAN_REVIEW_NOT_STARTED
