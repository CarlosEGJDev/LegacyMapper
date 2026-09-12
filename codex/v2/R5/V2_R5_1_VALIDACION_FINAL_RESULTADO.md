STATUS
FINAL_FULL_REAL_VALIDATION_PASS

ARTIFACTS
SYSTEM_CONTEXT.json=6070127 valid JSON
SYSTEM_CONTEXT.md=871 readable
ARCHITECTURE_GRAPH.json=69740057 valid JSON
FUNCTIONAL_FLOWS.json=144008622 valid JSON
TRACEABILITY.json=59358789 valid JSON

SOURCE_SNAPSHOT
source_file_count=4328 PASS
source_snapshot_sha256=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a PASS

GRAPH_INTEGRITY
nodes=108104 edges=180909 duplicate_node_ids=0 duplicate_logical_edges=0 orphan_edge_sources=0 orphan_edge_targets=0 PASS

GRAPH_COMPARISON
R5 edges=438672; R5.1 edges=180909; reduction=257763 (58.76%). Graph bytes reduced 69650090 (49.97%).

GRAPH_NODE_POLICY
High-value structural/functional nodes retained. Individual unresolved calls, parameters, source members and evidence nodes are excluded from graph and retained in paths/traceability/upstream indexes.

GRAPH_EDGE_POLICY
Only materialized-endpoint edges exported. PASS.

GRAPH_FACTUALITY
PASS. Retained relations are upstream project/solution or R4.1 flow facts.

UNRESOLVED_COMPACTION
Individual unresolved graph explosion removed. R4.1 unresolved_boundaries=162914 remain in FUNCTIONAL_FLOWS/TRACEABILITY/upstream indexes with unresolved confidence.

PARAMETER_COMPACTION
DAO->Parameter graph edges omitted; upstream data_parameters=74633 preserved.

FUNCTIONAL_FLOWS
flows=12642 paths=170020 unique_flow_ids=12642 unique_path_ids=170020 duplicate_flow_ids=0 duplicate_path_ids=0 duplicate_logical_paths=0. R4.1 IDs preserved.

FLOW_SEMANTICS
Ordered nodes, relation_types, terminals, confidence and evidence references preserved. PASS.

BRANCH_PRESERVATION
lost_branches=0 added_branches=0 changed_branches=0 PASS.

DB_TERMINALS
stored_procedure_paths=1121 sql_paths=1 data_operation_paths=4612 PASS.

TRACEABILITY
broken_references=0. Flow/path/DAO/SP/SQL mappings present.

TRACEABILITY_ROUND_TRIP
PASS: WebForm->EntryPoint->Flow->Path->DAO->SP/SQL and reverse path/flow navigation.

GRAPH_TRACEABILITY_SEPARATION
CLEAN_SEPARATION.

AI_USABILITY
Q1-Q6=SUPPORTED; project/class/cross-project flow retrieval=SUPPORTED.

SYSTEM_CONTEXT
PASS. Compact integrated summary; no full calls-index duplication.

MARKDOWN_CONTEXT
PASS. factual, portable, compact, bytes=871.

FILE_SIZE_COMPARISON
TOTAL_R5_BYTES=348831880 TOTAL_R5_1_BYTES=279727466 REDUCTION=69104414 (19.81%). MATERIALLY_IMPROVED.

DUPLICATION_NOISE
ACCEPTABLE. Paths globally represented; calls, parameters and individual unresolved records are not copied into graph.

PERFORMANCE
PRACTICAL. Largest artifact=FUNCTIONAL_FLOWS 144008622 bytes; all parse successfully.

CONFIDENCE_SEPARATION
PASS. No confidence promotion or semantic invention.

PORTABILITY
PASS. Source root only in allowed metadata; internal navigation is ID/reference based.

SECURITY
PASS. Centralized sanitizer applied; confirmed_secret_leaks=0.

DETERMINISM
PASS. All five artifacts are byte-identical between v2_r5_1_full and v2_r5_1_repro.

SOURCE_REPRODUCIBILITY
PASS. Approved fingerprint preserved.

UPSTREAM_REGRESSION
PASS. Calls=230356/12775/217581; approved R2/R3.1/R4.1 metrics preserved.

SOURCE_IMMUTABILITY
PASS.

R5_1_COMPLETENESS
COMPLETE

REQUIRED_FIXES
NONE

DECISION
V2-R5_1_APROBADA_V2_COMPLETA

V2 COMPLETE
