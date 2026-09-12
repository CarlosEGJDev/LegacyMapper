STATUS
V3-R7_2_BUDGET_INSUFFICIENT

FILES_CHANGED
legacy_documenter/documentation/coverage.py
legacy_documenter/documentation/systematic.py
legacy_documenter/documentation/aggregation.py
legacy_documenter/documentation/renderer.py
legacy_documenter/documentation/__init__.py
tests/test_v3_r7_2.py
codex/V3/V3_R7_2_RESULTADO.md

PRECONDITIONS
PASS: V2-R5.1 artifacts, R7.1 drafts, CopilotProvider, local authentication and canonical R7.1 contract enforcement available.

COVERAGE_PLANNER
IMPLEMENTED and executed deterministically. Full inventories are classified in Python; no previous DRAFT was used as evidence.

V2_SOURCE_ARTIFACTS
Existing output/v2_r5_1_full ai_context and index JSON only. No V1/V2 regeneration and no raw-source scan.

TOTAL_COVERAGE_UNITS
87 unique units across PROJECTS, SOLUTIONS, WEBFORMS, FUNCTIONAL_FLOWS, DATA_ACCESS, STORED_PROCEDURES and UNRESOLVED_BOUNDARIES.

PROJECT_COVERAGE
total=259; covered=234; partially_covered=24; no_usable_evidence=1; unresolved_ownership=0. All projects classified.

SOLUTION_COVERAGE
total=113; structurally represented=113.

WEBFORM_COVERAGE
total=3346; structurally represented=3346 through deterministic grouped units.

FLOW_COVERAGE
total=12642; structurally represented=12642 through deterministic grouped units.

DATA_ACCESS_COVERAGE
total_operations=20082; deterministically linked to project+method=19159; representative detailed operations included in bounded units.

STORED_PROCEDURE_COVERAGE
total=5389; linked through recorded evidence=5389; representative procedures included by deterministic partitions.

UNRESOLVED_COVERAGE
total=162914; classified/represented structurally=162914 across LOCAL_CALL_UNRESOLVED, CROSS_PROJECT_UNRESOLVED, FRAMEWORK_CALL, UI_BINDING, DATA_BOUNDARY and UNKNOWN where applicable.

BATCH_COUNT
8 functional local batches + 8 technical local batches planned and executed. Global synthesis batches were not called because preflight budget validation failed.

BATCH_LIMITS
Local batches: 11-12 records including mandatory system metrics; 3675-4759 estimated tokens; all <=35 records and <=5000 tokens.

LOCAL_FUNCTIONAL_ASSESSMENTS
8/8 completed without contract rejection before the budget stop.

LOCAL_TECHNICAL_ASSESSMENTS
8/8 completed without contract rejection before the budget stop.

GLOBAL_FUNCTIONAL_SYNTHESIS
NOT EXECUTED. Deterministic package contained 40 validated local claims and was estimated at 6598 tokens, exceeding the 5000-token bound.

GLOBAL_TECHNICAL_SYNTHESIS
NOT EXECUTED because execution stopped at the prior global budget gate.

SELECTED_PROVIDER
COPILOT

MODEL_ID
Auto/configured through Copilot SDK; effective model was not emitted by the budget-failure result and is not inferred.

REAL_CALLS_EXECUTED
16 primary local calls; no retries; no global calls. Execution was not restarted because doing so could exceed the hard maximum of 30 calls.

ASSESSMENT_VALIDATION
Local assessments passed canonical parsing/validation gates. No global assessment exists and no invalid/unvalidated result entered rendering.

MISSING_INFORMATION_DEDUPLICATION
Implemented and offline-tested; real global deduplication not executed because synthesis was blocked by budget.

FUNCTIONAL_DOCUMENT
R7.1 DRAFT retained unchanged; R7.2 replacement not generated.

TECHNICAL_DOCUMENT
R7.1 DRAFT retained unchanged; R7.2 replacement not generated.

ARCHITECTURE_PATTERN_RESULT
No R7.2 result; no pattern was forced.

COVERAGE_R7_1_VS_R7_2
Structural planning improved from the R7.1 six-project sample to classification of 259 projects and complete grouped inventories, but no validated R7.2 global documents exist, so document-level before/after claims are unavailable.

TRACEABILITY
Hierarchical mapping and evidence closure are implemented/tested offline. Real global traceability was not produced; R7.1 document traceability remains intact.

UNIT_TESTS
PASS; 30 new R7.2 tests are offline.

TOTAL_TESTS
161 PASS (131 baseline + 30 R7.2 tests).

REGRESSION
PASS: python -m unittest discover -s tests

SOURCE_IMMUTABILITY
PASS by execution design: only existing V2 output artifacts were read; C:\Users\cgalianj\source\IST_40\operacional was not scanned or modified.

SECURITY
PASS: no credentials/environment dump/raw authentication; model tools, shell, Git, MCP and filesystem actions disabled; no raw model responses persisted.

MODEL_OBSERVATIONS
The bounded local contract remained compliant across 16 calls. The failure is deterministic global-package sizing, not a comparable model-contract failure.

MODEL_CHANGE_RECOMMENDED
false

KNOWN_LIMITATIONS
Validated local assessments were not persisted before the global budget gate, so they cannot be reused without new calls. The synthesis strategy requires deterministic compaction or a bounded hierarchical merge before re-execution.

FAILURES
Global functional synthesis input exceeded the configured token limit: 6598 > 5000.

DECISION
GLOBAL_SYNTHESIS_BUDGET_STRATEGY_REVIEW_REQUIRED

NEXT
V3-R7_2_NOT_CLOSED; V3-R8_HUMAN_REVIEW_NOT_STARTED
