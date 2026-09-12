"""V4-R14 final baseline/manifest report builders.

This package does not implement any new knowledge capability. It only
consolidates already-approved V4-R1..R13 repository state into two
deterministic discovery artifacts:

* `output/v4_r14/V4_FINAL_BASELINE.json` — a deterministic snapshot of the
  final V4 checkpoint (test count, readiness, security/regression gates,
  approved artifact hashes, maintainability baseline).
* `output/v4_r14/V4_FINAL_MANIFEST.json` — a deterministic discovery index
  of the repository's important V4 artifacts (`FINAL_MANIFEST_IS_INDEX_NOT_AUTHORITY`).

Nothing here reads or writes canonical knowledge, performs classification,
composition, projection, or approval. It only inspects already-approved
repository files (round result documents, contract/example JSON artifacts)
and the local filesystem tree, following the same
plain-dict-builder + deterministic-JSON-renderer pattern used by every
R7-R13 `contract_report.py`.
"""
