TASK: Validate LegacyMapper V2-R1.1 on real repository.
DO NOT modify code.
DO NOT start V2-R2.

INPUTS:
- output/v2_r1_full/
- output/v2_r1_1_full/
- codex/V2/V2_R1_VALIDACION_REAL.md

PRIMARY FILES:
- output/v2_r1_1_full/index/calls.json
- output/v2_r1_1_full/index/functional_dependencies.json
- output/v2_r1_1_full/index/errors.json

Use V2-R1 baseline files only for comparison.

GOAL:
Determine whether V2-R1.1 reduced false positives/noise without materially damaging valid call resolution, and whether V2-R2 can be authorized.

CHECKS:

1. GLOBAL METRICS
Compare R1 vs R1.1:
- total calls
- confirmed
- inferred
- unresolved
- % by confidence
- instantiations
- functional_dependencies total
- duplicate relations
- cross-project confirmed
- unique resolved targets
- multiple-candidate calls
- errors

2. REQUIRED REGRESSION CHECKS
Verify that R1.1 removed/reduced:
- VB built-ins/intrinsics as functional calls
- JavaScript/string literal calls
- indexed/default-property false calls:
  Tables(...)
  Rows(...)
  Item(...)
  Attributes(...)
  Session(...)
- artificial inferred targets such as:
  Class.isnothing
  Class.cstr
  Class.values
  Class.format
- duplicated Class -> UsesClass edges

3. CONFIRMED PRESERVATION
Sample at least 20 confirmed calls from R1.1, prioritizing:
- Web -> BL
- BL -> SYS
- cross-project
- local valid calls
- fully-qualified calls

Classify:
CORRECT
SUSPICIOUS
INCORRECT

Compare against R1 when useful.
Confirm receiver_path/full qualifier preservation where applicable.

4. INFERRED QUALITY
Sample at least 20 inferred R1.1 calls.
Classify:
REASONABLE
SHOULD_CONFIRM
SHOULD_UNRESOLVE
INCORRECT

Check specifically whether weak fabricated local targets are gone.

5. UNRESOLVED
Sample at least 20 unresolved.
Group main causes only.
Determine whether unresolved growth is healthy conservatism or regression.

6. CROSS-PROJECT
Validate at least 10 confirmed cross-project relations.
Check source project, target project and structural coherence.
Do not use Web/bl/sys naming alone as proof.

7. DEDUP
Report:
- duplicated logical dependency keys
- duplicated extra rows
Compare R1 vs R1.1.
Confirm evidence_count/evidence_samples preserve repeated evidence without repeated edges.

8. ERROR CHECK
errors.json must be summarized.
Any new parser/runtime errors = regression.

9. DECISION
Return exactly one:

A) V2-R1_1_APROBADA_PARA_R2
B) V2-R1_1_REQUIERE_CORRECCIONES
C) V2-R1_1_REGRESION

If B/C:
list only required fixes grouped:
CRITICAL
HIGH
MEDIUM
LOW

Do not implement them.

OUTPUT:
codex/V2/V2_R1_1_VALIDACION_REAL.md

FORMAT:
Machine-oriented and compact.
Include only:
STATUS
METRICS_COMPARISON
REGRESSION_CHECKS
CONFIRMED_SAMPLE
INFERRED_SAMPLE
UNRESOLVED_CAUSES
CROSS_PROJECT_CHECK
DEDUP_CHECK
ERRORS
REQUIRED_FIXES
DECISION

No ZIP.
No extra reports.
No code changes.
V2-R2 must remain NOT STARTED until decision A.