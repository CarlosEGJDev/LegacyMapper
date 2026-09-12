STATUS
READY_FOR_FULL_REAL_VALIDATION

FILES_CHANGED
legacy_documenter/analysis/flow_resolver.py
legacy_documenter/main.py
tests/test_v1_unittest.py

TESTS
python -m unittest discover -s tests
49 passed

OUTPUTS
output/index/functional_flows.json
output/index/functional_paths.json
output/index/flow_summary.json
output/index/flow_unresolved.json

FLOW_MODEL
Deterministic flow/path IDs. One graph flow per confirmed R2 entry point; paths retain node IDs, terminal type/target, confidence, evidence references, depth and project sequence.

TRAVERSAL_RULES
Indexes confirmed calls, unresolved calls, data-access operations and operation terminals before traversal. Traverses only confirmed Method -> Method calls. Default max depth: 12; CLI: --flow-max-depth.

CYCLE_HANDLING
Path-local cycle detection emits a cycle terminal and does not recurse further.

BRANCHING
Every confirmed call, data operation and unresolved call branch is retained; identical logical paths are deduplicated.

TERMINALS
StoredProcedure, SQL, unresolved boundary, data operation without resolved DB terminal, dead end, cycle and depth truncation.

PERFORMANCE
Traversal uses method-keyed indexes; no per-entry full-call scan.

SECURITY
All R4 output is exported through the centralized recursive sanitizer; evidence is references/compact IDs rather than copied source bodies.

REGRESSION
R4 is additive. Existing approved indexes are not resolved or modified by the flow phase.

INTERNAL_METRICS
49 unit tests passed. End-to-end fixture verifies deterministic branch paths to stored procedure, SQL and unresolved boundary.

KNOWN_LIMITATIONS
External boundaries are emitted only when an existing upstream index distinguishes them; otherwise unresolved calls remain unresolved boundaries. No LLM or R5 interpretation was added.

REAL_VALIDATION_COMMAND
python main.py "E:\IAProyectos\revision\revision-main" --output "output\v2_r4_full" --verbose

NEXT
Run the real validation command. V2-R5 NOT STARTED.
