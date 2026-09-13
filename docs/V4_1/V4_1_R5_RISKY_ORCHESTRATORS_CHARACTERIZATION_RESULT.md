# LegacyMapper V4.1-R5 -- Risky Orchestrators Characterization -- Result

```text
STATUS=V4_1_R5_CHARACTERIZATION_COMPLETE
```

---

## ENTRY_GATE

```text
ENTRY_GATE=PASS
```

- `git status`: clean except `prompts/V4_1/V4_1_R5_RISKY_ORCHESTRATORS_CHARACTERIZATION.md` (expected untracked prompt file). Confirmed before any edit.
- `python -m unittest discover -s tests`: 1486 PASS, FAIL=0, SKIP=0.
- `python -m legacy_documenter.knowledge.readiness`: READINESS=READY, ai_knowledge_allowed=true, ai_knowledge_generated=false, provider_calls=0, real_llm_calls=0.
- `PROJECT_STATE.json` confirmed: latest_approved_round=V4.1-R4, next=V4.1-R5, V4 formally closed.

## BASELINE_TESTS

```text
BASELINE_TESTS=1486_PASS_0_FAIL_0_SKIP
```

## FINAL_TESTS

```text
FINAL_TESTS=1536_PASS_0_FAIL_0_SKIP
```

(1486 baseline + 24 new DatabaseExtractor characterization tests + 26 new FunctionalFlowResolver characterization tests. No test was removed, skipped, or weakened. No production file was modified -- confirmed by `git status --short` after all edits.)

## R5_MODE

```text
R5_MODE=CHARACTERIZATION_ONLY
```

## TARGETS

```text
TARGETS=legacy_documenter/extractors/database_extractor.py, legacy_documenter/analysis/flow_resolver.py
```

R0's own broader `V4.1-R5` plan entry ("Large Historical Orchestrators -- Characterization Only") originally scoped seven files (`database_extractor.py`, `flow_resolver.py`, `deep_source.py`, `documentation/{generator,hierarchical,resume,systematic}.py`). This R5 prompt's own narrower, authoritative scope covers only the two HIGH-risk, oversized-class modules named as Target A/B; the other five remain deferred (`resume.py` and `deep_source.py` explicitly re-fenced by this round, the other three simply out of this round's scope). This narrowing is consistent with the repository's established pattern of each round's own prompt narrowing R0's broader plan entry to a specific, reviewable scope (as R3 did for DEBT-003 and R4 did for DEBT-002).

---

## DATABASE_EXTRACTOR_CHARACTERIZATION

```text
DATABASE_EXTRACTOR_CHARACTERIZATION=COMPLETE
```

Full detail recorded in `output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json` -> `database_extractor`.

## DATABASE_EXTRACTOR_PUBLIC_SURFACE

```text
DATABASE_EXTRACTOR_PUBLIC_SURFACE=1 public method (extract), 25 private helper methods, 26 module-level regex constants.
```

Signature pinned: `extract(self, path: str | Path, root: str | Path | None = None) -> dict`.

## DATABASE_EXTRACTOR_CALLERS

```text
DATABASE_EXTRACTOR_CALLERS=6 (1 production: legacy_documenter/main.py; 3 test modules calling extract() directly or via analyze_repository; 2 tooling/path-string-only references)
```

Full caller table (caller_path, symbol_used, positional_or_keyword, public_or_internal, test_or_production, reflection_or_dynamic_access, patching_or_monkeypatching) in the JSON artifact -> `database_extractor.callers`. No monkeypatching of `DatabaseExtractor` found anywhere.

## DATABASE_EXTRACTOR_RESPONSIBILITY_MAP

7 responsibility groups identified: logical-line reassembly, string/token parsing, variable-and-type state tracking, operation detection and emission, parameter extraction and normalization, classification/normalization, and the `extract()` orchestration itself. Full map (symbol/responsibility/inputs/outputs/reads_state/writes_state/side_effects/callers/callee_dependencies/ordering_dependency/shared_internal_state/compatibility_risk/possible_future_destination/safe_extraction_confidence) is in the JSON artifact -> `database_extractor.responsibility_map`.

## DATABASE_EXTRACTOR_STATE_MODEL

```text
DATABASE_EXTRACTOR_STATE_MODEL=STATELESS
```

No `__init__` is defined and no `self.` attribute is assigned anywhere in the class body. `vars(DatabaseExtractor())` is `{}` both before and after calling `extract()`. A single shared instance reused across multiple files in a loop (exactly as `main.py` does) produces byte-identical results to fresh instances per file.

## DATABASE_EXTRACTOR_ORDERING_MODEL

```text
SEMANTIC for the single-pass line scan (a variable's declared type must be recognized before later Command/Adapter/OraConn checks reference that name) and for parameter list order (source order, relied on for evidence fidelity). INCIDENTAL for per-line regex-match dict iteration order.
```

## DATABASE_EXTRACTOR_EXCEPTION_MAP

3 entries recorded (operation/input_condition/exception_type/message_or_pattern/source/currently_tested/newly_characterized) in the JSON artifact -> `database_extractor.exceptions`. Key finding: `extract()` itself has no assertion/raise path of its own for malformed VB text -- it is a lenient scanner; the only exception it can propagate is `FileNotFoundError` from the underlying file read.

## DATABASE_EXTRACTOR_SIDE_EFFECTS

```text
filesystem_reads=1 (the single .vb file passed to extract())
filesystem_writes=0
network_access=false
provider_access=false
environment_access=false
global_state=false
mutable_instance_state=false
```

## DATABASE_EXTRACTOR_BEHAVIOR_CASES

11 representative behavior cases characterized (direct OracleCommand + CommandType + Execute; adapter Fill; OraConn ExecProc/ExecProcDS with parameter CSV; transactions; dynamic-SQL detection; ambiguous unresolved stored procedures; comment/string-literal stripping; class-field-scoped variables; multiline continuation; empty input; missing `End Class`). Full list in the JSON artifact -> `database_extractor.behavior_cases`.

## DATABASE_EXTRACTOR_EXTRACTION_CANDIDATES

7 candidate groups classified (LOW/MEDIUM/HIGH/DO_NOT_EXTRACT_YET future_extraction_risk). Logical-line reassembly, string/token parsing, and classification/normalization are LOW risk (pure, already independently testable). Variable-and-type state tracking and operation-detection-and-emission are HIGH risk (tightly coupled, order-dependent, mixed inline into `extract()`). Full table in the JSON artifact -> `database_extractor.extraction_candidates`.

## DATABASE_EXTRACTOR_R6_READINESS

```text
DATABASE_EXTRACTOR_R6_READINESS=PARTIALLY_READY
```

Missing characterization (see JSON artifact -> `database_extractor.r6_readiness_missing_characterization` for the full list): branch-order interaction between operation-detection regexes on the same physical line; `_split_args` edge cases (nested parens, quoted commas); an isolated unit test for variable/type-state tracking independent of full `extract()` runs; multi-class-with-repeated-variable-name scoping.

---

## FLOW_RESOLVER_CHARACTERIZATION

```text
FLOW_RESOLVER_CHARACTERIZATION=COMPLETE
```

Full detail recorded in `output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json` -> `flow_resolver`.

## FLOW_RESOLVER_PUBLIC_SURFACE

```text
FLOW_RESOLVER_PUBLIC_SURFACE=__init__(max_depth: int = 12) + 1 public method (resolve), 20 private helper methods.
```

Signature pinned: `resolve(self, entry_points, calls, data_access, stored_procedures, sql_operations, dependencies, errors=None) -> tuple[list[dict], list[dict], dict, list[dict]]`.

## FLOW_RESOLVER_CALLERS

```text
FLOW_RESOLVER_CALLERS=6 (1 production: legacy_documenter/main.py; 3 test modules calling resolve() via the full pipeline or directly patching internals; 2 tooling/path-string-only references)
```

Full caller table in the JSON artifact -> `flow_resolver.callers`. **Monkeypatch found**: `tests/test_v1_unittest.py::test_v2_r4_1_path_ids_use_complete_canonical_identity_and_guard_collisions` directly reassigns `resolver._path_id` (an instance-level function attribute) and `resolver._path_identities` on a live instance to force a deterministic collision. Any future R6 extraction of `_path_id`/`_add_path` must preserve this exact patch point or deliberately update that pre-existing test.

## FLOW_RESOLVER_RESPONSIBILITY_MAP

8 responsibility groups identified: indexing, graph traversal (`_walk`), graph construction, path-identity-and-construction, key/label derivation, confidence/status derivation, report composition, and `resolve()` orchestration. Full map in the JSON artifact -> `flow_resolver.responsibility_map`.

## FLOW_RESOLVER_STATE_MODEL

```text
FLOW_RESOLVER_STATE_MODEL=STATEFUL_RESET_PER_OPERATION
```

`self._path_identities`, `self.method_calls`, `self.unresolved_calls`, `self.data_by_method`, `self.proc_by_operation`, and `self.sql_by_operation` are all reassigned at the very top of `resolve()`, before any use. Calling `resolve()` twice on the same instance with the same inputs is byte-identical to a fresh instance. `main.py` never actually reuses one instance across multiple `resolve()` calls, but the reset guarantees it would be safe if it did.

## FLOW_RESOLVER_ORDERING_MODEL

```text
SEMANTIC for _flow_status's fixed precedence order (truncated_depth > cycle > unresolved_boundary > data_endpoint > dead_end) and for path/node identity (which encodes the traversal path itself). DETERMINISTIC_BUT_NOT_SEMANTIC for the final flows/paths list ordering (explicitly re-sorted by id) and project_sequence (first-seen order). INCIDENTAL for graph_nodes/graph_edges dict insertion order during traversal.
```

## FLOW_RESOLVER_EXCEPTION_MAP

3 entries recorded in the JSON artifact -> `flow_resolver.exceptions`. Key finding: `_add_path` raises `ValueError("Functional path ID collision: {path_id}")` when the same path id is computed with a different canonical identity than previously recorded -- this is the module's only explicit raise path, and it is directly characterized. A `resolve()` exception is not caught around this specific call in `main.py` (unlike the per-file `DatabaseExtractor` loop), so it would propagate uncaught -- recorded as evidence, not newly characterized (caller-side behavior, out of this module's scope).

## FLOW_RESOLVER_SIDE_EFFECTS

```text
filesystem_reads=0
filesystem_writes=0
network_access=false
provider_access=false
environment_access=false
global_state=false
mutable_instance_state=self._path_identities, self.method_calls, self.unresolved_calls, self.data_by_method, self.proc_by_operation, self.sql_by_operation (all reset per resolve() call)
```

## FLOW_RESOLVER_BEHAVIOR_CASES

15 representative behavior cases characterized (linear flow to dead_end/data_operation; branching; convergence to a shared node; duplicate call expressions remaining distinct edges; direct and indirect cycles; unresolved call boundaries; entry-point eligibility gating; empty graph; isolated node; max-depth truncation; instance-reuse equivalence; flow/path sort order; malformed-input tolerance in indexing; path-id collision). Full list in the JSON artifact -> `flow_resolver.behavior_cases`.

## FLOW_RESOLVER_EXTRACTION_CANDIDATES

8 candidate groups classified. Indexing, graph construction, key/label derivation, and report composition are LOW risk (pure, already independently testable -- indexing helpers were directly unit-tested in isolation this round). Path-identity-and-construction and confidence/status derivation are MEDIUM risk. Graph traversal (`_walk`) is HIGH risk (recursive, shared mutable state, multiple untested interaction cases). Full table in the JSON artifact -> `flow_resolver.extraction_candidates`.

## FLOW_RESOLVER_R6_READINESS

```text
FLOW_RESOLVER_R6_READINESS=PARTIALLY_READY
```

Missing characterization (see JSON artifact -> `flow_resolver.r6_readiness_missing_characterization` for the full list): `_stable_id`'s exact hashing output is not pinned to a specific known value (only cross-run equality/inequality); no test exercises two entry points sharing an overlapping call graph within one `resolve()` call to confirm no cross-contamination; `_flow_status`'s full precedence order is not exercised with both a cycle and a truncated_depth path in the same flow; no test exercises a method with both direct data-access operations and outgoing calls in the same `_walk` invocation.

---

## CHARACTERIZATION_GAPS

```text
CHARACTERIZATION_GAPS=8 (4 per target, listed above and in the JSON artifact's r6_readiness_missing_characterization fields)
```

None of these gaps block R5 itself (characterization-only); they are exactly the additional evidence a future R6 design-review round would need before a specific extraction shape could be committed to.

---

## NON_TARGET_HIGH_RISK_MODULES_PRESERVED

```text
NON_TARGET_HIGH_RISK_MODULES_PRESERVED=PASS
```

`git diff --stat HEAD` against `legacy_documenter/documentation/resume.py` and `legacy_documenter/analysis/deep_source.py` shows zero changes. `readiness.py` was already handled in R4 and is not re-touched.

---

## DEBT_002_STATUS

```text
DEBT_002_STATUS=RESOLVED
```

Unchanged from V4.1-R4.

## DEBT_003_STATUS

```text
DEBT_003_STATUS=RESOLVED
```

Unchanged from V4.1-R3.

## TD_005_STATUS

```text
TD_005_STATUS=PARTIALLY_RESOLVED
```

Unchanged; R5 did not touch typing work.

---

## APPROVED_ARTIFACT_HASHES_UNCHANGED

```text
APPROVED_ARTIFACT_HASHES_UNCHANGED=PASS
```

| Artifact | SHA-256 |
|---|---|
| `output/v4_r14/V4_FINAL_BASELINE.json` | `d13e3807a12187b226ea55752ae0e9dccd2ad20c9dbe044360ffa48bca526d1e` |
| `output/v4_r14/V4_FINAL_MANIFEST.json` | `be398240a31137e7dea25fcaa7b3cfe6580d2557f990f7da884d5775f5c40551` |
| `output/v4_1_r1/V4_1_R1_BEHAVIORAL_EQUIVALENCE.json` | `55c99c3b68ac159585c6a0ec7e05f74e8dd64dd871308d067ab27bdda1a1c33b` |
| `output/v4_1_r2/V4_1_R2_TYPE_AND_CONTRACT_EQUIVALENCE.json` | `bd3daf04be868ef6465298c5e372aacc1f33bf234417f2bb914b79b22ab5a6f4` |
| `output/v4_1_r3/V4_1_R3_NAMING_COMPATIBILITY.json` | `9e922d288b4f07812482baef1a5383276cd71f729e27cc67b47e54c30c5afecf` |
| `output/v4_1_r4/V4_1_R4_READINESS_EQUIVALENCE.json` | `eb07e0f35540e0607b90f8ff707c7cac8e1f113419d338e3cc8579fa12f1e617` |

None regenerated; none touched.

## R0_FROZEN_INVENTORY_MODIFIED

```text
R0_FROZEN_INVENTORY_MODIFIED=false
```

No production code changed this round; `tests/test_v4_1_r0_maintainability_inventory.py`'s full 22-test suite (including the live-reconstruction comparison against the frozen R0 snapshot) passes unmodified and unchanged.

---

## ORCHESTRATOR_CHARACTERIZATION_ARTIFACT

```text
ORCHESTRATOR_CHARACTERIZATION_ARTIFACT=output/v4_1_r5/V4_1_R5_ORCHESTRATOR_CHARACTERIZATION.json
```

## ORCHESTRATOR_CHARACTERIZATION_ARTIFACT_SHA256

```text
ORCHESTRATOR_CHARACTERIZATION_ARTIFACT_SHA256=04c82d51b17664630adcafe26dd343d5f0740932904c77dd7a458029d547be32
```

## ORCHESTRATOR_CHARACTERIZATION_ARTIFACT_DETERMINISM

```text
ORCHESTRATOR_CHARACTERIZATION_ARTIFACT_DETERMINISM=PASS
```

Generated twice independently from the same deterministic builder (no timestamps, no machine-specific absolute paths); byte-for-byte identical both times.

---

## V4_CONTRACTS_UNCHANGED

```text
V4_CONTRACTS_UNCHANGED=PASS
```

## R11_BOUNDARY

```text
R11_BOUNDARY=PASS
```

## R12_BOUNDARY

```text
R12_BOUNDARY=PASS
```

`PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge`, `PLUGIN_CONTRACT_VERSION=1.0`, `PLUGIN_RUNTIME=NOT_IMPLEMENTED`, `V5_IMPLEMENTED=false` -- none touched this round.

---

## PRODUCTION_CODE_CHANGED

```text
PRODUCTION_CODE_CHANGED=false
```

## PRODUCTION_BEHAVIOR_CHANGED

```text
PRODUCTION_BEHAVIOR_CHANGED=false
```

Only two new test files and one output artifact were added; `git status --short` confirms zero production files touched.

---

## READINESS

```text
READINESS=READY
```

## AI_KNOWLEDGE_ALLOWED

```text
AI_KNOWLEDGE_ALLOWED=true
```

## AI_KNOWLEDGE_GENERATED

```text
AI_KNOWLEDGE_GENERATED=false
```

## REAL_LLM_CALLS

```text
REAL_LLM_CALLS=0
```

## PROVIDER_CALLS

```text
PROVIDER_CALLS=0
```

---

## PROJECT_STATE

`PROJECT_STATE.json` updated to:

```text
latest_completed_round = "V4.1-R5"
latest_approved_round = "V4.1-R4"   (unchanged)
current_round_in_progress = "V4.1-R5 (pending Technical Lead review)"
round_status = "V4_1_R5_READY_FOR_HUMAN_REVIEW"
next = "HUMAN_REVIEW_V4_1_R5"
tests = 1536
readiness = "READY"
ai_knowledge_allowed = true
ai_knowledge_generated = false
provider_calls = 0
real_llm_calls = 0
```

V4 closure fields untouched. R5 is **not** marked approved, and does **not** authorize R6.

---

## DECISION

```text
DECISION=V4_1_R5_READY_FOR_HUMAN_REVIEW
```

## NEXT

```text
NEXT=HUMAN_REVIEW_V4_1_R5
```

---

## Narrative Summary

R5 characterized the two HIGH-risk, oversized-class orchestrators R0 flagged as needing design review before any extraction: `DatabaseExtractor` (1 public method, 25 private helpers, 26 module-level VB.NET regex constants) and `FunctionalFlowResolver` (1 public method plus 20 private helpers). No production code was touched -- the entire round added 50 new characterization tests (24 + 26) across two new test files, plus one deterministic JSON evidence artifact.

`DatabaseExtractor` proved to be fully `STATELESS` (no `__init__`, no `self.` attributes anywhere), making instance reuse across many files -- exactly what `main.py` already does in its extraction loop -- provably safe. Its responsibility groups split cleanly into low-risk, already-independently-testable pieces (line reassembly, string/token parsing, provider/direction classification) versus a high-risk core: `extract()`'s single sequential pass threads mutable `variables`/`commands`/`adapters`/`parameters` dicts through roughly fifteen ordered regex branches with `continue` statements controlling which branch wins per line. That ordering is semantically load-bearing and only partially isolated by unit tests today.

`FunctionalFlowResolver` proved `STATEFUL_RESET_PER_OPERATION`: every instance attribute needed by a traversal is reassigned fresh at the top of `resolve()`, so repeated calls on one instance are safe even though `main.py` never actually does this. Its indexing helpers (`_index_calls`, `_index_data_access`, `_index_terminals`) are pure and were directly unit-tested in isolation this round, confirming they are low-risk extraction candidates on their own. The recursive `_walk` traversal, by contrast, is high-risk: it mutates shared node/edge/path dictionaries across recursive calls, and one pre-existing test (`tests/test_v1_unittest.py::test_v2_r4_1_...`) already monkeypatches `_path_id` directly on a live instance -- any future extraction touching path-identity construction must preserve that exact patch point.

Both targets are honestly classified `PARTIALLY_READY` for R6, not forced to `READY_FOR_CONTROLLED_EXTRACTION`: each has a specific, named list of missing characterization (branch-order interactions for `DatabaseExtractor`; multi-entry-point isolation and pinned hash-stability for `FunctionalFlowResolver`) that a future design-review round would need to close first. The full regression suite (1536 tests, up from the 1486 baseline) is green, readiness stays `READY` with zero provider/LLM calls, all six required historical artifact hashes are verified unchanged, the R0 frozen inventory reconstruction is unaffected (no production files changed), and neither `resume.py` nor `deep_source.py` was touched. `PROJECT_STATE.json` reflects the pending-review state without marking R5 approved and without authorizing R6.

---

## Closure Section — Technical Lead Approval

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

R5_MODE_DECISION=CHARACTERIZATION_ONLY_APPROVED

DATABASE_EXTRACTOR_CHARACTERIZATION_DECISION=APPROVED
DATABASE_EXTRACTOR_R6_READINESS=PARTIALLY_READY

FLOW_RESOLVER_CHARACTERIZATION_DECISION=APPROVED
FLOW_RESOLVER_R6_READINESS=PARTIALLY_READY

CHARACTERIZATION_GAPS=8

R6_INITIAL_PHASE_REQUIRED=CHARACTERIZATION_GAP_CLOSURE
R6_PRODUCTION_EXTRACTION_PREAUTHORIZED=false

R5_1_REQUIRED=false

ROUND_STATUS=APPROVED
DECISION=V4_1_R5_FORMALLY_APPROVED
NEXT=V4.1-R6
```

The Technical Lead reviewed and approved the narrower R5 scope (`database_extractor.py` and `flow_resolver.py` only; the other five files from R0's broader plan entry are not added during closure), zero production-code modification, the 24 + 26 characterization tests, the `STATELESS` / `STATEFUL_RESET_PER_OPERATION` classifications, the responsibility maps and ordering/state/exception/side-effect contracts, the caller and compatibility inventories, and the existing `_path_id`/`_path_identities` monkeypatch dependency (`FLOW_RESOLVER_PATH_ID_PATCH_POINT_PRESENT=true`) as explicit architectural evidence requiring preservation or Technical-Lead-reviewed redesign in any future round. Both `PARTIALLY_READY` verdicts and their eight named missing-characterization items are accepted exactly as recorded -- neither module is marked `READY_FOR_CONTROLLED_EXTRACTION`. Approval of R5 explicitly does **not** authorize immediate production extraction in R6: `R6_INITIAL_PHASE_REQUIRED=CHARACTERIZATION_GAP_CLOSURE`, `R6_PRODUCTION_EXTRACTION_PREAUTHORIZED=false`, and `R6_EXTRACTION_REQUIRES_NEW_GATE=true`. No R5.1 corrective round is required.
