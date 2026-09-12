STATUS
V2-R4_1_READY_FOR_FULL_REAL_VALIDATION

FILES_CHANGED
legacy_documenter/analysis/flow_resolver.py
tests/test_v1_unittest.py

TESTS
python -m unittest discover -s tests
50 passed

PATH_ID_ROOT_CAUSE
R4 used a polynomial hash reduced modulo 1000000007 and formatted as 10 decimal digits. The finite reduced space produced 12 collisions for distinct complete path identities in the real output.

PATH_ID_FIX
PATH IDs now use complete canonical JSON identity: entry_point_id, ordered node IDs, ordered relation_types, terminal_type and terminal_target. SHA-256 full hex digest is deterministic and independent of runtime ordering.

COLLISION_GUARD
Resolver records path_id -> canonical identity. Identical canonical identity deduplicates; differing canonical identity with the same ID raises ValueError and cannot overwrite or merge a path.

CALL_COUNT_INVESTIGATION
R4 output has 230356 calls: confirmed=12775, unresolved=217581. Approved historical baseline is 230355: confirmed=12775, unresolved=217580. R4/R4.1 do not modify CallExtractor or CallResolver; flow resolution consumes the already-built calls index after call resolution. Available output/v1_r1_full lacks calls.json and output/v2_r2_full/output/v2_r3_1_full snapshots are unavailable, so the exact historical-extra call ID cannot be established deterministically without fabricating a comparison.

CALL_COUNT_CAUSE
ENVIRONMENT_OR_SOURCE_SNAPSHOT_DIFFERENCE_SUSPECTED. The delta is exactly one unresolved call and no confirmed-call delta exists. It is not caused by R4.1 path identity code, which runs after calls extraction. Full R4.1 validation must retain calls.json and compare it to the approved snapshot to identify the exact record.

REGRESSION
Traversal logic unchanged. R2/R3.1 resolver code unchanged. Tests preserve confirmed-call behavior, unresolved boundaries, entry points, data access and sanitizer behavior.

INTERNAL_METRICS
Fixture validation: duplicate_flow_ids=0; duplicate_path_ids=0; duplicate_logical_paths=0; errors=0. The fixture has no confirmed WebForms entry point, therefore flows=0; end-to-end R4 branching/determinism coverage remains in the unit suite.

SECURITY
Centralized JSON sanitizer unchanged. R4.1 identity contains only IDs/relation labels/terminal metadata and copies no source evidence.

KNOWN_LIMITATIONS
No full real repository run was performed. The exact +1 unresolved-call identity cannot be recovered because the required approved call-index snapshot is absent locally.

REAL_VALIDATION_COMMAND
python main.py "C:\Users\cgalianj\source\IST_40\operacional" --output "output\v2_r4_1_full" --verbose

NEXT
Run full R4.1 validation; require duplicate_path_ids=0 and snapshot comparison of the one unresolved-call delta. V2-R5 NOT STARTED.
