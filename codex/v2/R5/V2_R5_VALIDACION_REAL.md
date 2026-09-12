STATUS
VALIDATED_WITH_BLOCKING_GRAPH_INTEGRITY_DEFECT

ARTIFACTS
SYSTEM_CONTEXT.json=present, valid JSON, 6070127 bytes
SYSTEM_CONTEXT.md=present, readable Markdown, 871 bytes
ARCHITECTURE_GRAPH.json=present, valid JSON, 139390147 bytes
FUNCTIONAL_FLOWS.json=present, valid JSON, 144309946 bytes
TRACEABILITY.json=present, valid JSON, 59358789 bytes

SOURCE_SNAPSHOT
source_file_count=4328 PASS
source_snapshot_sha256=6ad94c8f0b735dea3fb1d7daf55b6c3633cb6f6d04a9ee326baac8bef91c599a PASS
metadata/version/upstream phases/confidence model/source indexes=present.

SYSTEM_CONTEXT
Required top-level sections=present. Compact call summary/reference is used; full calls index is not embedded. Classification=PASS.

REPOSITORY_PROJECT_MODEL
Project/solution data is sourced from approved indexes; no project roles are assigned. Relative internal references are generally used. Sampled structural representation=CORRECT.

WEB_MODEL
WebForms, codebehind/inherits, registers and entry-point IDs are represented as compact index-derived data. No fabricated web relation found by structure inspection.

SYMBOL_MODEL
Logical symbols retain physical declaration references and source-index fallback. No confidence promotion detected by model structure.

CALL_MODEL
total=230356 confirmed=12775 unresolved=217581 inferred=0. Calls are summarized with source-index references; no promotion detected.

DATA_ACCESS_MODEL
operations=20082 stored_procedures=5389 sql_operations=3. DAO/SP/SQL path IDs checked through traceability: broken=0.

FUNCTIONAL_FLOWS
flows=12642 paths=170020 unique_flow_ids=12642 unique_path_ids=170020. R4.1 path set is preserved; R4.1 duplicate logical paths=0.

FLOW_PRECISION
R5 paths retain R4.1 ordered nodes, relation_types, confidence, terminals and evidence_refs. No semantic path identity regeneration detected.

BRANCH_PRESERVATION
R4.1 paths=170020; R5 references=170020. lost=0 added=0. PASS.

UNRESOLVED_BOUNDARIES
R4.1 unresolved boundaries=162914; R5 retains path-level unresolved terminal records and call evidence references. PASS.

ARCHITECTURE_GRAPH
nodes=108104 edges=438672 duplicate_nodes=0 duplicate_edges=0
orphan_edge_sources=241935
orphan_edge_targets=255899
FAIL_HIGH. Graph adds functional-dependency edges without materializing every source/target node.

GRAPH_FACTUALITY
Existing graph relations derive from upstream dependencies/flows, but orphan endpoints prevent factual graph-integrity approval.

GRAPH_SCALE
Largest node types: UnresolvedCall=70751, Method=14181, Event=12638, WebForm=3346.
Largest relations: Method->UnresolvedCall=130943, Method->Method=108280, DataAccessOperation->Parameter=74633.
Classification=EXCESSIVELY_NOISY due to 438672 edges and integrity failure.

TRACEABILITY
broken_references=[] flow_ids=12642 path_ids=170020. Entry->flow=12642; flow->paths=12642; path->references=170020. PASS for flow/DAO/SP/SQL trace maps.

TRACEABILITY_ROUND_TRIP
ROUND_TRIP_PARTIAL. Flow/path/DAO/SP navigation is intact; architecture-node round trip is blocked by orphan graph endpoints.

AI_USABILITY
WebForm/procedure/flow/project/unresolved/path retrieval=SUPPORTED through FUNCTIONAL_FLOWS and TRACEABILITY. Architecture graph traversal=PARTIALLY_SUPPORTED pending graph-node closure.

MARKDOWN_CONTEXT
Required sections present; factual and compact. Size=871 bytes. PASS.

CONFIDENCE_SEPARATION
R5 copies upstream path confidence and call summary counts; no promotion detected. PASS.

PORTABILITY
Source repository root is present only in allowed snapshot metadata. Internal artifact references are relative. Classification=PASS.

DETERMINISM
R4.1 IDs reused unchanged. R5 output was not regenerated for second-run comparison during this validation. Deterministic implementation evidence exists but full real semantic-repeat proof remains pending.

FILE_SIZES
SYSTEM_CONTEXT=6070127
ARCHITECTURE_GRAPH=139390147
FUNCTIONAL_FLOWS=144309946
TRACEABILITY=59358789
SYSTEM_CONTEXT_MD=871
Classification=EXCESSIVE_DUPLICATION/NOISE for graph and functional/trace artifacts at current scale.

PERFORMANCE
Artifacts parse successfully but graph/flow sizes are large. Classification=BORDERLINE pending graph compaction.

SECURITY
R5 JSON exporter uses centralized sanitizer. No secret exposure observed in structural inspection; exhaustive scan remains required after corrective regeneration.

UPSTREAM_REGRESSION
Calls, R2, R3.1 and R4.1 counts match approved baselines in output/v2_r5_full. PASS.

SOURCE_IMMUTABILITY
Snapshot metadata matches approved fingerprint. No source modification action was performed by validation.

R5_COMPLETENESS
INCOMPLETE due to architecture graph integrity/scale defect despite valid system context, functional flows and traceability maps.

REQUIRED_FIXES
HIGH: Materialize graph nodes for every exported functional-dependency edge, or omit/aggregate those edges; regenerate and prove orphan sources=0 and orphan targets=0.
MEDIUM: Reduce graph noise/duplication to a practical architectural representation; rerun deterministic and exhaustive security validation.

DECISION
V2-R5_REQUIERE_CORRECCIONES
