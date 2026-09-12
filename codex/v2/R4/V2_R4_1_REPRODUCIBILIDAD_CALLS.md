TASK: Perform deterministic reproducibility validation of the V2-R4.1 call graph before approving R5.

VALIDATION ONLY.

DO NOT modify code.
DO NOT modify generated indexes.
DO NOT start V2-R5.
DO NOT attempt to force historical calls_total=230355.
DO NOT fabricate the unavailable historical calls.json.

BACKGROUND:

Historical approved metric:

* calls_total=230355
* confirmed=12775
* unresolved=217580

Current repository executions:

* calls_total=230356
* confirmed=12775
* unresolved=217581

Historical calls.json snapshot is unavailable because generated output indexes were not stored in Git.

Previous R4.1 validation classified the +1 unresolved call as UNEXPLAINED because exact historical record comparison was impossible.

GOAL:

Determine whether the CURRENT call graph is:

1. deterministic across repeated executions;
2. identical before/after R4.1 flow processing where current outputs permit comparison;
3. generated entirely upstream of R4/R4.1;
4. safe to accept as the reproducible baseline for V2-R5.

INPUTS:

* `output/v2_r4_full/index/calls.json`
* `output/v2_r4_1_full/index/calls.json`
* `output/v2_r4_1_repro_a/index/calls.json`
* `output/v2_r4_1_repro_b/index/calls.json`

Also inspect relevant implementation responsible for:

* call extraction
* call resolution
* main pipeline ordering
* R4 flow resolution
* R4.1 path-ID logic

==================================================

1. FILE AVAILABILITY
   ==================================================

Confirm which of these exist:

* v2_r4_full calls.json
* v2_r4_1_full calls.json
* repro_a calls.json
* repro_b calls.json

Do not silently skip missing files.

At minimum repro_a and repro_b are required.

==================================================
2. EXACT COUNTS
===============

For every available calls.json report:

* total calls
* confirmed
* inferred
* unresolved
* unique IDs
* duplicate IDs
* duplicate logical calls

Expected current reproducible candidate:

total=230356
confirmed=12775
unresolved=217581

Do not treat historical 230355 as mandatory because its exact source snapshot is unavailable.

==================================================
3. BYTE HASHES
==============

Calculate SHA-256 of each complete calls.json file.

Report:

filename
sha256
file size

If hashes are identical:
record BYTE_IDENTICAL.

If hashes differ:
continue with semantic comparison; JSON ordering alone must not automatically be treated as semantic change.

==================================================
4. SEMANTIC CANONICAL COMPARISON
================================

Canonicalize every call record deterministically.

Compare sets independent of JSON list ordering.

Canonical identity should use all stable semantically relevant call fields, including where present:

* call ID
* caller method/class/project
* source file
* target/resolved method
* receiver
* method/expression
* relation/call kind
* confidence
* resolution status
* evidence location

Do not include volatile runtime-only metadata if any.

Compare:

A) repro_a vs repro_b

REQUIRED:
semantic difference=0

Also compare when available:

B) v2_r4_1_full vs repro_a
C) v2_r4_full vs repro_a

Report:

* only_left
* only_right
* changed logical records

==================================================
5. ID STABILITY
===============

Verify calls representing the same canonical logical call have the same ID across repeated runs.

Report:

* same logical call / different ID count
* duplicate call IDs
* call ID collisions

REQUIRED for repro_a vs repro_b:

same_logical_different_id=0
duplicate_call_ids=0

Any systematic instability blocks R5.

==================================================
6. CONFIDENCE STABILITY
=======================

Compare repro_a vs repro_b:

* confirmed sets
* unresolved sets
* inferred sets

REQUIRED:

confirmed delta=0
unresolved delta=0
inferred delta=0

No call may change confidence between identical executions.

==================================================
7. PIPELINE ORDER PROOF
=======================

Inspect code.

Document exact pipeline order relevant to:

CallExtractor / call discovery
-> CallResolver
-> calls index
-> R2 entry points
-> R3 data access
-> R4 FlowResolver

Use actual implementation names/order.

Prove whether R4/R4.1:

* receives/reads existing call records; or
* can mutate/recompute call extraction.

Specifically inspect changes introduced by:

`legacy_documenter/analysis/flow_resolver.py`

and R4.1 path-ID correction.

Determine whether any R4/R4.1 code path can:

* add calls
* delete calls
* alter confidence
* modify caller/target
* trigger another call extraction pass with different semantics

RESULT:

UPSTREAM_IMMUTABLE_FOR_R4
or
R4_CAN_AFFECT_CALLS

Provide concrete code evidence, compactly.

==================================================
8. R4 VS R4.1 CALL GRAPH
========================

If `output/v2_r4_full/index/calls.json` exists, compare it semantically with current R4.1 outputs.

Important:

Previous validation already observed R4 calls_total=230356.

Determine:

R4 calls
vs
R4.1 calls
vs
repro_a
vs
repro_b

If all are semantically identical:

prove that the +1 existed before the R4.1 correction and therefore was not introduced by R4.1.

If R4 and R4.1 differ:
report exact records and investigate.

==================================================
9. CURRENT SOURCE SNAPSHOT FINGERPRINT
======================================

Generate a deterministic fingerprint of the legacy source inputs relevant to call extraction WITHOUT modifying source files.

At minimum calculate:

* total VB source files analyzed
* deterministic hash derived from sorted tuples:
  relative_path + file_size + file-content SHA-256

Do this for the current legacy repository:

`C:\Users\cgalianj\source\IST_40\operacional`

Store only aggregate fingerprint/report data.

Do not copy source contents.

Purpose:

Establish an immutable identity for the CURRENT source snapshot so future validation can state exactly which source produced 230356 calls.

Report:

SOURCE_FILE_COUNT
SOURCE_SNAPSHOT_SHA256

This fingerprint becomes evidence for the current approved baseline if R4.1 passes.

==================================================
10. REPRODUCIBILITY VERDICT
===========================

Classify:

DETERMINISTIC
NONDETERMINISTIC
INCONCLUSIVE

DETERMINISTIC requires:

* repro_a/repro_b semantic calls identical
* call IDs stable
* confidence stable
* no duplicate/collision defect
* current source fingerprint established

==================================================
11. HISTORICAL DELTA CLASSIFICATION
===================================

Historical exact calls.json cannot be reconstructed.

Classify the +1 historical difference using one:

CURRENT_GRAPH_DETERMINISTIC_HISTORICAL_SNAPSHOT_UNAVAILABLE
R4_REGRESSION
R4_1_REGRESSION
CURRENT_GRAPH_NONDETERMINISTIC
INCONCLUSIVE

The first classification is acceptable for R5 only when:

* repeated scans are identical;
* R4/R4.1 cannot alter call extraction;
* confirmed calls remain 12775;
* current graph is internally valid;
* no evidence of upstream regression exists.

Do NOT label the +1 as a specific source change unless deterministic evidence actually identifies one.

==================================================
12. R5 RISK ASSESSMENT
======================

Evaluate whether accepting 230356 as the new reproducible baseline could materially harm R5.

Check:

* +1 is unresolved only
* confirmed graph unchanged
* unresolved calls are never traversed as confirmed
* R4 preserves unresolved boundary
* no target is fabricated
* R5 will inherit explicit unresolved state rather than false confirmed relation

Classify risk:

NONE
LOW
MEDIUM
HIGH

Explain compactly.

If the delta is one unresolved boundary, deterministic, and never promoted, expected risk should be evaluated based on evidence, not assumed.

==================================================
13. SECURITY
============

Do not print source bodies or secrets.

Source fingerprint must contain only hashes/counts/paths as needed.

No connection-string secret values in report.

==================================================
14. R4.1 FINAL READINESS
========================

R4.1 may be approved for R5 if:

* R4.1 functional validation previously PASS except historical delta
* duplicate_path_ids=0
* duplicate_logical_paths=0
* repro_a and repro_b calls are semantically identical
* call IDs deterministic
* confidence deterministic
* R4/R4.1 proven not to mutate call extraction
* current source snapshot fingerprint established
* confirmed calls=12775 remains preserved
* historical +1 is unresolved only
* no evidence of current regression
* R5 risk <= LOW
* security PASS

==================================================
15. DECISION
============

Return EXACTLY one:

A) V2-R4_1_APROBADA_PARA_R5
B) V2-R4_1_REQUIERE_CORRECCIONES
C) V2-R4_1_NO_CONFIABLE

If A:
the current 230356-call graph becomes the reproducible baseline associated with SOURCE_SNAPSHOT_SHA256.

Record historical 230355 only as prior metric with unavailable source/index snapshot.

Do not claim both snapshots are identical.

==================================================
OUTPUT
======

Create ONLY:

`codex/V2/V2_R4_1_REPRODUCIBILIDAD_RESULTADO.md`

FORMAT:

STATUS
FILES_AVAILABLE
CALL_METRICS
FILE_HASHES
SEMANTIC_COMPARISON
ID_STABILITY
CONFIDENCE_STABILITY
PIPELINE_ORDER
R4_VS_R4_1
SOURCE_SNAPSHOT
REPRODUCIBILITY
HISTORICAL_DELTA
R5_RISK
SECURITY
R4_1_READINESS
REQUIRED_FIXES
DECISION

Machine-oriented.
Compact.
No ZIP.
No code modifications.
No additional reports.
V2-R5 NOT STARTED.
