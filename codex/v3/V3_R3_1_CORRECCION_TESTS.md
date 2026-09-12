TASK=V3-R3_1_CORRECCION_TESTS

MODE=TEST_CORRECTION_ONLY

NO_NEW_FEATURES
NO_ARCHITECTURE_REDESIGN
NO_LLM
NO_NETWORK
NO_FULL_REAL_REPOSITORY_SCAN
NO_LEGACY_SOURCE_MODIFICATION
NO_V3_R4

OBJECTIVE

Close the explicit test-coverage debt left by V3-R2 and V3-R3.

Current blocking condition:

* V3-R2 dedicated expanded fixture coverage missing.
* V3-R3 synthetic budget fixture coverage missing.
* Current total test count remained 55.
* V3-R4 is BLOCKED until this correction passes.

Do not add new functional scope.

==================================================
ALLOWED CHANGES
===============

Primary target:

tests/

Production-code changes are allowed ONLY if a new test exposes a real defect in already-approved R2/R3 behavior.

If production code changes:

* keep them minimal;
* document exact defect;
* add regression test;
* do not introduce new features.

Expected production files, only if required:

legacy_documenter/context/resolver.py
legacy_documenter/context/composer.py

Do not modify unrelated V1/V2/V3-R1 code.

==================================================
R2 REQUIRED TEST COVERAGE
=========================

Add dedicated tests for ContextResolver.

Minimum explicit cases:

1. SYSTEM package creation

2. FUNCTIONAL package creation

3. TECHNICAL package creation

4. ENTITY package creation

5. FLOW package creation

6. DATA_ACCESS package creation

7. source_snapshot preserved

8. deterministic package_id

9. deterministic serialization

10. exact lookup -> FOUND

11. unknown lookup -> NOT_FOUND

12. duplicate normalized lookup -> AMBIGUOUS

13. ambiguity preserves candidate list

14. no silent selection

15. bounded expansion

16. expansion_depth=0

17. expansion_depth>0

18. deterministic expansion order

19. confirmed status preserved

20. unresolved status preserved

21. no confidence promotion

22. no R2-created semantic INTERPRETED claim

23. unresolved boundary retained

24. unresolved target not guessed

25. provenance artifact retained

26. provenance upstream ID retained

27. evidence refs retained

28. internal reference closure

29. external V2 refs explicit

30. functional package contains flow/data refs

31. functional package does not create business/module semantics

32. technical package contains project/dependency refs

33. technical package does not declare architectural pattern/layer

34. truncation explicit when resolver limits reached

35. no silent truncation

36. stack-neutral package schema

37. WebForms not mandatory

38. Oracle not mandatory

39. no network required

40. no LLM required

These must be actual test cases or clearly parametrized equivalents.

==================================================
R3 REQUIRED TEST COVERAGE
=========================

Add dedicated ContextComposer tests.

ENTITY COMPOSITION

41. PROJECT entity composition
42. UI/component entity composition
43. METHOD entity composition
44. FLOW entity composition
45. DATA_OPERATION entity composition
46. STORED_PROCEDURE entity composition

Verify:

* identity retained
* relationships retained
* provenance retained
* no semantic invention

DATA_ACCESS

47. DAO operation is P0
48. caller refs preserved
49. flow refs preserved
50. SP refs preserved
51. SQL refs preserved
52. compact parameter refs
53. no full parameter/evidence duplication

FLOW

54. ordered path refs preserved
55. DAO terminals retained
56. SP terminal retained
57. SQL terminal retained
58. unresolved path retained as P3
59. cross-project refs retained when fixture contains them

DEDUPLICATION

60. duplicate references removed
61. deduplication count correct
62. deduplication preserves all relationships
63. provenance not lost by deduplication

==================================================
SYNTHETIC BUDGET FIXTURE
========================

Create a deterministic synthetic fixture large enough to produce real budget pressure.

The SAME fixture/request must demonstrate:

FULL > LARGE > MEDIUM > SMALL > TINY

in included records and/or serialized context size.

Do not fake expected values directly.

The fixture must contain enough:

* P0 records
* P1 records
* P2 records
* P3 unresolved records
* P4 records
* multiple flows
* multiple paths
* multiple entities
* multiple evidence refs

to exercise selection/truncation.

==================================================
BUDGET PROFILE TESTS
====================

64. TINY applies limit

65. SMALL applies limit

66. MEDIUM applies limit

67. LARGE applies limit

68. FULL contains complete deduplicated fixture

69. FULL > LARGE

70. LARGE > MEDIUM

71. MEDIUM > SMALL

72. SMALL > TINY

Comparison must use at least one deterministic metric:

records_included
character_count
package_bytes

Prefer verifying more than one where stable.

==================================================
BUDGET LIMIT TESTS
==================

73. max_records enforced
74. max_characters enforced
75. max_estimated_tokens enforced
76. max_flows enforced
77. max_paths enforced
78. max_entities enforced
79. max_unresolved enforced
80. max_evidence_refs enforced

No silent omission.

==================================================
PRIORITY TESTS
==============

81. P0 selected before P1
82. P1 before P2
83. P2 before P3/P4 according to defined policy
84. P4 selected last
85. stable ordering within same priority

Priority must never mutate confidence.

==================================================
UNRESOLVED RESERVATION
======================

86. unresolved evidence present in fixture
87. constrained budget still reserves configured unresolved capacity
88. unresolved evidence cannot be completely displaced by large confirmed collection when reservation applies
89. unresolved retained with UNRESOLVED status

==================================================
TRUNCATION / COMPLETENESS
=========================

90. FULL fixture -> COMPLETE
91. constrained package -> TRUNCATED
92. truncation report contains excluded counts
93. truncation report contains excluded_by_priority
94. continuation refs emitted where supported
95. package never claims COMPLETE after truncation

==================================================
BUDGET_INSUFFICIENT
===================

Create case where mandatory P0 + identity/provenance exceed budget.

96. status=BUDGET_INSUFFICIENT
97. mandatory P0 is not silently removed
98. minimum required size estimate reported
99. factual confidence remains unchanged

==================================================
TOKEN ESTIMATION
================

100. estimated_tokens = ceil(character_count / chars_per_token)
101. default chars_per_token=4
102. configurable chars_per_token works
103. estimate deterministic
104. estimate explicitly remains approximation metadata

==================================================
SIZE / QUALITY METRICS
======================

105. package_bytes deterministic

106. character_count deterministic

107. records_selected correct

108. records_included correct

109. records_excluded correct

110. deduplicated_records correct

111. counts_by_priority correct

112. counts_by_category correct

113. confirmed_reference_count correct

114. unresolved_reference_count correct

115. traceability_reference_count correct

116. flow_count correct

117. data_access_count correct

118. entity_count correct

119. coverage_by_priority emitted

No semantic quality score.

==================================================
PROGRESSIVE DISCLOSURE
======================

Validate retrieval/composition level contract:

120. L0 SYSTEM
121. L1 STRUCTURE
122. L2 ENTITY
123. L3 FLOW
124. L4 DATA_ACCESS
125. L5 EVIDENCE

These are retrieval levels only.

Do not introduce AI-driven retrieval.

==================================================
PACKAGE INDEX / CACHE IDENTITY
==============================

126. package index contract valid
127. package_id stable for same snapshot/request/policy/budget
128. changing budget changes semantic package identity when output selection changes
129. changing source snapshot changes package identity
130. no UUID/random/hash()/timestamp identity

==================================================
TRACEABILITY
============

Validate complete chain:

DocumentClaim-compatible reference
-> ContextPackage
-> package evidence/ref
-> V2 upstream reference
-> source_snapshot

131. traceability chain valid
132. compaction does not break upstream ref
133. no evidence body required for traceability
134. one-to-many evidence refs preserved

==================================================
SECURITY / ISOLATION
====================

135. no network
136. no LLM
137. no credentials introduced
138. raw sanitized configuration values are not rehydrated
139. no real legacy repository scan
140. legacy source remains untouched

==================================================
REGRESSION
==========

Run complete suite:

python -m unittest discover -s tests

Requirements:

ALL PASS.

Explicitly report:

V1_V2_TESTS
V3_R1_TESTS
V3_R2_TESTS
V3_R3_TESTS
TOTAL_TESTS

Do not claim R2/R3 coverage if tests are only inherited from earlier suites.

==================================================
REPEATED DETERMINISM CHECK
==========================

For the synthetic fixture:

Generate the same representative composed package twice.

Verify:

canonical serialization identical
package_id identical
statistics identical
selection order identical
truncation report identical

If possible verify byte identity for canonical serialized output.

==================================================
ACCEPTANCE CRITERIA
===================

PASS only if:

* dedicated R2 tests exist;
* dedicated R3 tests exist;
* synthetic budget fixture exists;
* FULL > LARGE > MEDIUM > SMALL > TINY demonstrated;
* priority policy tested;
* unresolved reservation tested;
* COMPLETE/TRUNCATED/BUDGET_INSUFFICIENT tested;
* token estimation tested;
* traceability tested;
* determinism tested;
* all repository tests PASS.

If any mandatory area is missing:

STATUS=V3-R3_1_REQUIRES_CORRECTION

Do NOT report READY_FOR_REVIEW.

==================================================
NON_GOALS
=========

Do NOT implement:

LLMProvider
Gemini
Copilot
Qwen/Ollama
Claude
OpenAI
AI prompts
AI interpretation
documentation generation
LEVANTAMIENTO_FUNCIONAL
LEVANTAMIENTO_TECNICO
Knowledge Readiness
AI_KNOWLEDGE
semantic search
embeddings
vector DB
V4

==================================================
REPORT
======

Create ONLY:

codex/V3/V3_R3_1_RESULTADO.md

Machine-oriented.
Compact.

FORMAT:

STATUS
FILES_CHANGED
PRODUCTION_FIXES
R2_DEDICATED_TESTS
R3_DEDICATED_TESTS
SYNTHETIC_FIXTURE
BUDGET_ORDER
PRIORITY_TESTS
UNRESOLVED_RESERVATION
TRUNCATION_TESTS
BUDGET_INSUFFICIENT_TESTS
TOKEN_ESTIMATION_TESTS
METRICS_TESTS
PROGRESSIVE_DISCLOSURE_TESTS
TRACEABILITY_TESTS
DETERMINISM_TESTS
SECURITY_TESTS
V1_V2_TESTS
V3_R1_TESTS
V3_R2_TESTS
V3_R3_TESTS
TOTAL_TESTS
REGRESSION
KNOWN_LIMITATIONS
DECISION
NEXT

Expected successful result:

STATUS=V3-R3_1_READY_FOR_REVIEW
DECISION=R2_R3_TEST_DEBT_CLOSED
NEXT=V3-R4_NOT_STARTED

Stop.