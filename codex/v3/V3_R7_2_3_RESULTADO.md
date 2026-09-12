STATUS
V3-R7_2_3_READY_FOR_HUMAN_REVIEW

FILES_CHANGED
legacy_documenter/documentation/evidence_catalog.py
legacy_documenter/documentation/evidence_resume.py
legacy_documenter/documentation/resume.py
tests/test_v3_r7_2_2.py
tests/test_v3_r7_2_3.py
output/v3_r7_2/LOCAL_ASSESSMENTS.json
output/v3_r7_2/INTERMEDIATE_ASSESSMENTS.json
output/v3_r7_2/COVERAGE_INDEX.json
output/LEVANTAMIENTO_FUNCIONAL.md
output/LEVANTAMIENTO_TECNICO.md
codex/V3/V3_R7_2_3_RESULTADO.md

PRECONDITIONS
PASS: V2-R5.1 artifacts, coverage/synthesis planners, deterministic envelope, nine initial canonical checkpoints, CopilotProvider and local authentication available.

ROOT_CAUSE
R7.2.2 asked the model to reproduce long canonical evidence IDs. R7.2.3 replaced free-form ID generation with selection from a request-local closed key catalog; evidence closure was not weakened.

EVIDENCE_CATALOG
PASS: deterministic catalog generated from each exact ContextPackage, unique keys/IDs, package-local closure, deterministic descriptions and bounded size.

EVIDENCE_KEY_FORMAT
E01, E02, ... with deterministic zero-padding based on catalog size.

MODEL_VISIBLE_EVIDENCE
Only key, evidence type and deterministic concise description. canonical_id is excluded from the model-visible catalog.

CANONICAL_EVIDENCE_MAPPING
Python resolves exact key-to-canonical mappings after semantic parse. Persisted assessments contain evidence_refs/related_evidence_ids only; no temporary evidence_keys persisted.

DYNAMIC_SCHEMA_ENFORCEMENT
Request-local JSON Schema enums constrain claim evidence_keys and MissingInformation related_evidence_keys. Copilot transport uses strict schema prompting plus deterministic post-parse validation; native SDK schema enforcement is not claimed.

UNKNOWN_EVIDENCE_POLICY
Reject entire assessment. No unknown key is dropped, approximated or nearest-matched.

NO_SEMANTIC_REPAIR_VALIDATION
PASS: statements, statuses, source types, sections, related claims and MissingInformation semantics remain unchanged. Key resolution changes only the predeclared transport symbol into its canonical evidence ID.

DETERMINISTIC_ENVELOPE
PRESERVED: Python owns assessment/profile/package/snapshot/version/hash/stage/provider metadata; model owns semantic payload.

CACHE_FOUND
9 initial valid local assessments: 8 functional, 1 technical.

CACHE_REVALIDATED
9/9 PASS before reuse; subsequent checkpoints also validated before reuse.

CACHE_REUSED
15 canonical local assessments in the successful resumed run.

CACHE_INVALIDATED
0

FUNCTIONAL_LOCAL_REUSED
8

FUNCTIONAL_LOCAL_NEW
0; already complete from R7.2.2.

TECHNICAL_LOCAL_REUSED
1 initially; six additional valid checkpoints were reused after the single malformed-response retry.

TECHNICAL_LOCAL_NEW
7 valid assessments completed. Eight technical call attempts occurred because one response was syntactically invalid JSON and retried once.

CHECKPOINTING
PASS: LOCAL_ASSESSMENTS.json contains 16/16 valid local assessments. INTERMEDIATE_ASSESSMENTS.json contains 4 intermediate and 2 global valid assessments. Atomic persistence used after every canonical PASS.

INTERMEDIATE_FUNCTIONAL
2 valid assessments.

INTERMEDIATE_TECHNICAL
2 valid assessments.

GLOBAL_FUNCTIONAL
PASS; validated global synthesis generated 13 rendered claims.

GLOBAL_TECHNICAL
PASS; validated global synthesis generated 14 rendered claims; no architecture pattern was forced.

HIERARCHY_DEPTH
2 synthesis levels above local assessments for both profiles.

MAX_REQUEST_ESTIMATED_TOKENS
4759; every request <=5000.

SELECTED_PROVIDER
COPILOT

MODEL_ID
gpt-5.6-luna effective SDK response model; auto/configured selection, not hardcoded.

NEW_REAL_CALLS_EXECUTED
14 total attempts: 8 technical-local attempts, 4 intermediate calls and 2 global calls.

REUSED_ASSESSMENTS
15 at final successful resume checkpoint.

RETRIES
1, solely for syntactically malformed JSON. No semantic retry.

ASSESSMENT_VALIDATION
16 local, 4 intermediate and 2 global canonical assessments valid and persisted. One malformed JSON response was never composed or persisted.

EVIDENCE_CLOSURE
PASS across local, intermediate, global and rendered documents.

STATUS_PROPAGATION
PASS: no AI_INTERPRETATION or UNRESOLVED claim was deterministically promoted.

MISSING_INFORMATION_DEDUPLICATION
PASS deterministic structured merge. Functional document contains 19 requests; technical document contains 33 after systematic coverage.

FUNCTIONAL_DOCUMENT
PASS: output/LEVANTAMIENTO_FUNCIONAL.md, 21622 bytes, DRAFT, 13 global claims, 19 MissingInformation items, coverage and traceability sections present.

TECHNICAL_DOCUMENT
PASS: output/LEVANTAMIENTO_TECNICO.md, 28324 bytes, DRAFT, 14 global claims, 33 MissingInformation items, coverage and traceability sections present.

COVERAGE_R7_1_VS_R7_2_3
FUNCTIONAL projects 6->259; WebForms 6->3346; flows 4->12642; linked data operations unavailable->19159; linked procedures unavailable->5389; CONFIRMED 10->10; INTERPRETED 1->1; UNRESOLVED 4->2; MissingInformation 3->19.
TECHNICAL projects 6->259; WebForms 6->3346; flows 4->12642; linked data operations unavailable->19159; linked procedures unavailable->5389; CONFIRMED 16->10; INTERPRETED 1->2; UNRESOLVED 8->2; MissingInformation 4->33.

TRACEABILITY
PASS: global -> intermediate -> local -> ContextPackage -> canonical V2 evidence -> source snapshot. Temporary request-local keys do not appear in persisted canonical assessments.

UNIT_TESTS
PASS: 53 new evidence-constrained tests; prior historical checkpoint test made progress-compatible.

TOTAL_TESTS
299 PASS

REGRESSION
PASS: python -m unittest discover -s tests

SOURCE_IMMUTABILITY
PASS by design: existing V2 outputs only; no raw repository scan or legacy-source write.

SECURITY
PASS: no credentials, environment dump, raw authentication, model filesystem/shell/Git/MCP actions, unrestricted permissions or legacy writes. Raw responses were not persisted.

LEGACYMAPPER_FAILURE_DIAGNOSIS
EVIDENCE_CATALOG_ISSUE corrected. The only transient new failure was syntactically malformed JSON and succeeded under the single allowed retry. No remaining contract, Python, context, budget, provider or catalog failure observed.

MODEL_CAPABILITY_ASSESSMENT
No practical capability limitation established; the model complied after deterministic evidence selection constraints.

MODEL_CHANGE_RECOMMENDED
false; LegacyMapper uses diagnosis rather than a numeric failure threshold.

KNOWN_LIMITATIONS
Structural inclusion is not 100% semantic understanding. Detailed evidence is represented through deterministic partitions and validated hierarchical summaries; MissingInformation remains substantial and requires human review.

FAILURES
One transient malformed JSON response, resolved by the only permitted syntactic retry. No final failure.

DECISION
EVIDENCE_CONSTRAINED_HIERARCHICAL_SYNTHESIS_VALIDATED

NEXT
V3-R8_HUMAN_REVIEW_NOT_STARTED
