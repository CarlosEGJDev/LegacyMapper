STATUS
CURRENT_CALL_GRAPH_REPRODUCIBLE

FILES_AVAILABLE
v2_r4_full=present
v2_r4_1_full=present
v2_r4_1_repro_a=present
v2_r4_1_repro_b=present

CALL_METRICS
All four calls.json files:
total=230356
confirmed=12775
inferred=0
unresolved=217581
explicit_call_ids=0 (upstream call records have no id field)
canonical_unique_calls=228973
duplicate_logical_record_occurrences=1383; multiplicity is byte-identical in all four outputs.

FILE_HASHES
v2_r4_full/calls.json size=211588538 sha256=e3def02b037ff89194572af085ec1a04449f0c9ff8892421b614137c36f61187 BYTE_IDENTICAL
v2_r4_1_full/calls.json size=211588538 sha256=e3def02b037ff89194572af085ec1a04449f0c9ff8892421b614137c36f61187 BYTE_IDENTICAL
v2_r4_1_repro_a/calls.json size=211588538 sha256=e3def02b037ff89194572af085ec1a04449f0c9ff8892421b614137c36f61187 BYTE_IDENTICAL
v2_r4_1_repro_b/calls.json size=211588538 sha256=e3def02b037ff89194572af085ec1a04449f0c9ff8892421b614137c36f61187 BYTE_IDENTICAL

SEMANTIC_COMPARISON
repro_a_vs_repro_b only_left=0 only_right=0 changed_logical_records=0
r4_1_full_vs_repro_a only_left=0 only_right=0 changed_logical_records=0
r4_full_vs_repro_a only_left=0 only_right=0 changed_logical_records=0

ID_STABILITY
calls.json has no explicit call ID field. Full canonical call records, including source/evidence fields, are byte-identical across executions; R4 evidence references are deterministically derived from file, line, expression and resolved target. same_logical_different_representation=0; explicit_id_collisions=N/A.

CONFIDENCE_STABILITY
repro_a_vs_repro_b confirmed_delta=0 unresolved_delta=0 inferred_delta=0. PASS.

PIPELINE_ORDER
main.py: CallExtractor.extract for each VB source -> CallResolver.resolve(calls, symbols) -> WebEntryResolver.resolve(..., calls) -> DatabaseResolver.resolve -> FunctionalFlowResolver.resolve(entry_points, calls, ...).
FunctionalFlowResolver only indexes/reads existing calls; R4.1 _path_id only builds SHA-256 IDs from path metadata. Neither path can add, delete, re-extract, or alter calls/call confidence/caller/target. RESULT=UPSTREAM_IMMUTABLE_FOR_R4.

R4_VS_R4_1
R4, R4.1 and both repro outputs calls.json are byte-identical. The +1 unresolved call existed before the R4.1 correction. R4_1_REGRESSION=NO; R4_REGRESSION=NO_EVIDENCE.

SOURCE_SNAPSHOT
SOURCE_FILE_COUNT=4328
SOURCE_SNAPSHOT_SHA256=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a
Fingerprint input: sorted relative_path, file_size, file-content SHA-256 tuples for scanned VB source files; no source content stored.

REPRODUCIBILITY
DETERMINISTIC

HISTORICAL_DELTA
CURRENT_GRAPH_DETERMINISTIC_HISTORICAL_SNAPSHOT_UNAVAILABLE
Historical 230355 index cannot be reconstructed. Current baseline is 230356 with the source snapshot fingerprint above; confirmed count remains 12775 and delta is one unresolved call only.

R5_RISK
LOW. The delta is unresolved only, the confirmed graph is unchanged, R4 never traverses unresolved calls as confirmed, and unresolved calls remain explicit boundaries.

SECURITY
PASS. Report contains only counts, hashes and pipeline metadata; no source bodies or secret values.

R4_1_READINESS
PASS. R4.1 has unique deterministic path IDs, preserved functional behavior, byte-identical repeated call graphs, stable confidence, immutable upstream call processing, current source fingerprint, and low risk.

REQUIRED_FIXES
NONE

DECISION
V2-R4_1_APROBADA_PARA_R5
