STATUS
V3-R7_2_2_MODEL_CONTRACT_FAILURE

FILES_CHANGED
legacy_documenter/documentation/envelope.py
legacy_documenter/documentation/resume.py
legacy_documenter/documentation/synthesis.py
tests/test_v3_r7_2_2.py
output/v3_r7_2/LOCAL_ASSESSMENTS.json
codex/V3/V3_R7_2_2_RESULTADO.md

PRECONDITIONS
PASS: existing V2 outputs, R7.2 planner, R7.2.1 synthesis planner, seven local checkpoints, CopilotProvider and local authentication available.

ROOT_CAUSE
The deterministic identity mismatch from R7.2.1 was eliminated. During resumed technical coverage, a model-controlled semantic payload selected unknown evidence IDs in claims and MissingInformation. Request identity and budget were valid; this is a semantic model-contract failure.

DETERMINISTIC_ENVELOPE
IMPLEMENTED. The model returns only status, summary, claims and MissingInformation semantics. Python composes the canonical Assessment identity before AssessmentValidator execution.

MODEL_OWNED_FIELDS
summary; assessment status; claim_id; statement; claim status; source_type; evidence_refs; section; MissingInformation request/question/reason/blocking level/related IDs.

PYTHON_OWNED_FIELDS
assessment_id; profile_id; context package IDs; source snapshots; schema and prompt-contract versions; request hash; provider/model metadata; stage; validation marker; persisted content hash.

NO_SEMANTIC_REPAIR_VALIDATION
PASS offline and real: unknown claim/MissingInformation evidence was rejected, not replaced or removed. Status/source/evidence semantics remain byte-structurally unchanged through envelope composition.

CACHE_FILE
output/v3_r7_2/LOCAL_ASSESSMENTS.json

CACHE_FOUND
7 prior functional checkpoints.

CACHE_REVALIDATED
7/7 PASS: identity, original content hash, validation marker, package/snapshot/profile and canonical Assessment validation.

CACHE_MIGRATED
7 safely migrated to deterministic-envelope identity; semantic claims and MissingInformation unchanged; original identity/hash retained in migration metadata.

CACHE_REUSED
7

CACHE_INVALIDATED
0

FUNCTIONAL_LOCAL_REUSED
7

FUNCTIONAL_LOCAL_NEW
1 PASS and persisted. Functional local coverage is now 8/8.

TECHNICAL_LOCAL_REUSED
0

TECHNICAL_LOCAL_NEW
1 PASS and persisted; next technical response failed and was not persisted.

CHECKPOINTING
PASS: cache contains 9 validated entries (8 functional, 1 technical). Failed semantic output is absent.

SYNTHESIS_PLANNER
Preserved and offline validated; not reached in real execution after technical rejection.

HIERARCHY_DEPTH
0 synthesis levels executed.

INTERMEDIATE_FUNCTIONAL
NOT EXECUTED

INTERMEDIATE_TECHNICAL
NOT EXECUTED

GLOBAL_FUNCTIONAL
NOT EXECUTED

GLOBAL_TECHNICAL
NOT EXECUTED

MAX_REQUEST_ESTIMATED_TOKENS
4759 planned local maximum; every executed request <=5000.

SELECTED_PROVIDER
COPILOT

MODEL_ID
gpt-5.6-luna effective response model; selected through SDK auto/configuration, not hardcoded.

NEW_REAL_CALLS_EXECUTED
3

REUSED_ASSESSMENTS
7

RETRIES
0

ASSESSMENT_VALIDATION
2 new PASS and persisted; 1 new FAIL rejected for unknown evidence and claim/MissingInformation evidence closure.

STATUS_PROPAGATION
No deterministic status correction or promotion occurred.

EVIDENCE_CLOSURE
PASS for all 9 persisted assessments; FAIL for rejected technical payload.

MISSING_INFORMATION_DEDUPLICATION
Implemented and offline-tested; real hierarchy not reached.

FUNCTIONAL_DOCUMENT
Existing R7.1 DRAFT retained; not overwritten.

TECHNICAL_DOCUMENT
Existing R7.1 DRAFT retained; not overwritten.

COVERAGE_R7_1_VS_R7_2_2
Not produced because intermediate/global synthesis did not complete.

TRACEABILITY
Checkpoint traceability is closed through package/snapshot/evidence. Global hierarchical traceability not produced.

UNIT_TESTS
PASS: 45 new offline tests.

TOTAL_TESTS
246 PASS

REGRESSION
PASS: python -m unittest discover -s tests

SOURCE_IMMUTABILITY
PASS by execution design: existing V2 outputs only; no raw scan or legacy-source write.

SECURITY
PASS: no credentials, environment dump, raw authentication data, model filesystem/shell/Git/MCP tools or unrestricted permissions.

COMPARABLE_MODEL_FAILURE_COUNT
2: R7.2.1 snapshot mismatch + R7.2.2 unknown semantic evidence. R7.2 budget failure excluded.

MODEL_CHANGE_RECOMMENDED
false; threshold of three comparable failures has not been reached.

KNOWN_LIMITATIONS
Execution can resume from 8 functional and 1 technical valid checkpoints. Remaining technical, intermediate and global work is pending explicit continuation.

FAILURES
MODEL_CONTRACT: unknown evidence; evidence closure; missing evidence closure.

DECISION
MODEL_SEMANTIC_OUTPUT_REJECTED_CHECKPOINTS_PRESERVED

NEXT
V3-R7_2_2_NOT_CLOSED; V3-R8_HUMAN_REVIEW_NOT_STARTED
