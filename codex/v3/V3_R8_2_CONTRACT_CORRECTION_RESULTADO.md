STATUS
V3-R8_2_CONTRACT_CORRECTION_COMPLETE

ROOT_CAUSE
PROMPT_CONTRACT/SCHEMA: semantic request schemas exposed CONFIRMED although Python could not establish claim-specific deterministic authority before inference. Post-validation correctly rejected GROUP_B with CONFIRMED_WITHOUT_AUTHORITY.

FILES_CHANGED
legacy_documenter/analysis/deep_interpretation.py
tests/test_v3_r8_2.py
tests/test_v3_r8_2_correction.py
output/v3_r8_2/INTERPRETATION_REQUESTS.json
output/v3_r8_2/INTERPRETATION_RESULTS.json
output/v3_r8_2/ARCHITECTURE_INTERPRETATION.json
output/v3_r8_2/MISSING_INFORMATION_REEVALUATION.json
output/v3_r8_2/DEEP_ANALYSIS_MERGED_SUMMARY.json
codex/V3/V3_R8_2_CONTRACT_CORRECTION_RESULTADO.md

CONTRACT_CORRECTION
Semantic prompts explicitly state: interpret supplied evidence; do not confirm new facts; use INTERPRETED or UNRESOLVED; never upgrade interpretation to CONFIRMED; deterministic facts remain Python-owned. Existing authority post-validator remains unchanged.

SCHEMA_CORRECTION
PASS: request-local SEMANTIC_INTERPRETATION claim status enum is exactly INTERPRETED,UNRESOLVED for GROUP_A, GROUP_B and GROUP_C. CONFIRMED is not model-selectable. Deterministic authoritative facts are published separately from semantic interpretations in INTERPRETATION_REQUESTS.json.

ARCHITECTURE_STATUS_RULE
PASS: architecture claims allow only INTERPRETED or UNRESOLVED. Pattern status remains independent. Final pattern_status=NO_PATTERN_CONFIRMED; this is not a CONFIRMED claim and does not prove another architecture from absence of System.Web.Mvc.

TELEMETRY_CORRECTION
Failure paths now retain effective_provider, effective_model when supplied, request_id, target_group and validation_failure independently of semantic acceptance. Model identity is never guessed. Atomic publication still excludes partial/rejected semantic results.

BASELINE_TESTS
496 PASS

NEW_TESTS
20 correction-specific tests PASS; 52 combined R8.2 tests PASS.

TOTAL_TESTS
516 PASS

REQUEST_GROUPS
GROUP_A=FMI-001,FMI-007; GROUP_B=FMI-008,TMI-001,TMI-006,TMI-011; GROUP_C=TMI-002,TMI-009. All three restarted from the beginning; no prior response reused.

REQUEST_TOKEN_ESTIMATES
GROUP_A=1289; GROUP_B=1257; GROUP_C=1751; all <=4200 preferred and <=5000 maximum.

REAL_LLM_CALLS
3

RETRIES
0

EFFECTIVE_PROVIDER
copilot-local

EFFECTIVE_MODEL
gpt-5.6-luna; provider-supplied actual response identity, not hardcoded selection.

GROUP_A_RESULT
VALID: FMI-001=PARTIALLY_RESOLVED_WITH_INTERPRETATION; FMI-007=REQUIRES_EXTERNAL_INFORMATION.

GROUP_B_RESULT
VALID: FMI-008=RESOLVED_WITH_INTERPRETATION; TMI-001=REQUIRES_EXTERNAL_INFORMATION; TMI-006=PARTIALLY_RESOLVED_WITH_INTERPRETATION; TMI-011=REQUIRES_EXTERNAL_INFORMATION. Regression CONFIRMED_WITHOUT_AUTHORITY prevented by schema; no CONFIRMED claim emitted.

GROUP_C_RESULT
VALID: TMI-002=RESOLVED_WITH_INTERPRETATION; TMI-009=PARTIALLY_RESOLVED_WITH_INTERPRETATION.

EVIDENCE_CLOSURE
PASS: all eight target results contain canonical evidence IDs resolved from request-local aliases; unknown aliases remain rejected. Six claim candidates are INTERPRETED and one is UNRESOLVED; zero CONFIRMED semantic claims.

FUNCTIONAL_REEVALUATION
FMI-001=PARTIALLY_RESOLVED_WITH_INTERPRETATION; FMI-002,FMI-003,FMI-004,FMI-005,FMI-006=PARTIALLY_RESOLVED; FMI-007=REQUIRES_EXTERNAL_INFORMATION; FMI-008=RESOLVED_WITH_INTERPRETATION. Human disposition remains NEEDS_ANALYSIS for all.

TECHNICAL_REEVALUATION
TMI-001=REQUIRES_EXTERNAL_INFORMATION; TMI-002=RESOLVED_WITH_INTERPRETATION; TMI-003,TMI-004,TMI-007,TMI-008,TMI-010,TMI-012=PARTIALLY_RESOLVED; TMI-005=RESOLVED_BY_DETERMINISTIC_EVIDENCE; TMI-006,TMI-009=PARTIALLY_RESOLVED_WITH_INTERPRETATION; TMI-011=REQUIRES_EXTERNAL_INFORMATION. Human disposition remains NEEDS_ANALYSIS for all.

RESOLVED_ITEMS
TMI-005=RESOLVED_BY_DETERMINISTIC_EVIDENCE; FMI-008,TMI-002=RESOLVED_WITH_INTERPRETATION. These are candidates for human review, not automatic human-resolution decisions.

PARTIALLY_RESOLVED_ITEMS
FMI-001,FMI-002,FMI-003,FMI-004,FMI-005,FMI-006,TMI-003,TMI-004,TMI-006,TMI-007,TMI-008,TMI-009,TMI-010,TMI-012.

STILL_UNRESOLVED_ITEMS
None assigned exactly STILL_UNRESOLVED. Partial and external-information states retain explicit unresolved aspects.

HUMAN_KNOWLEDGE_REQUIRED_ITEMS
None newly classified.

EXTERNAL_INFORMATION_REQUIRED_ITEMS
FMI-007,TMI-001,TMI-011.

SOURCE_IMMUTABILITY
PASS: no raw source scan or legacy-source access occurred during correction/rerun.

V2_IMMUTABILITY
PASS: 34-file aggregate SHA-256=bc73783aafc53e2029f656edd502291501aac8e0da3a7a76167095d824bd556f unchanged.

R8_1_EVIDENCE_IMMUTABILITY
PASS: aggregate SHA-256=7a423f2d847a143dd9c564ad055ef38a6a75da60facdf5a7aa31c43131f177e3 before and after.

R7_R8_DOCUMENT_IMMUTABILITY
PASS: LEVANTAMIENTO_FUNCIONAL.md=e31a35fac44259bde1e362bfa03d3854bce9e3f157a3163ab6c17096f7ab9fc7; LEVANTAMIENTO_TECNICO.md=ccaf7af9ad2892af11457911557ab9cbaa4ee54b51031c8d52f3c1a5eb6e5e0f; R8 review record=6a11cc0abb1d898159e0c00580afe5a1b2c3f2b54c331533ecb2c31292ff39c4; unchanged.

SECURITY
PASS: exactly three previously authorized compact sanitized contexts sent; provider tools/skills/MCP/file changes/Git disabled. Audit found zero unredacted sensitive assignments in canonical R8.2 outputs.

REGRESSION
PASS: python -m unittest discover -s tests; 516 tests.

MODEL_FAILURE_CLASSIFICATION
NONE after correction. All three groups validated.

MODEL_CHANGE_RECOMMENDED
false

MODEL_CHANGE_REASON
The observed failure was corrected at contract/schema level. The configured model completed all corrected groups without retry; no model-capability limitation established.

AI_KNOWLEDGE_ALLOWED
false

DECISION
EVIDENCE_CONSTRAINED_INTERPRETATION_READY_FOR_HUMAN_REVIEW

NEXT
SECOND_HUMAN_REVIEW
