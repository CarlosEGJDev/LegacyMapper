# LegacyMapper V4 — Developer Manual

## Audience

A future human developer, or an AI development agent (Claude, Codex, or any other capable agent),
resuming LegacyMapper V4 development with no prior conversation history. The repository is
authoritative; this manual only points at where its knowledge actually lives.

## 1. Repository Authority Hierarchy

Read, in this order, before writing any code:

1. `CLAUDE.md` — minimal bootstrap pointer, not a substitute for the rest of this list.
2. `AGENTS.md` — autonomy/permission boundary, phase control, safety rules.
3. `PROJECT_STATE.json` — machine-readable pointer to the latest completed/approved round and the
   declared `next` action.
4. `docs/PROJECT_RECOVERY.md` — how to become productive on a fresh checkout.
5. `docs/V4/V4_AI_HANDOVER.md` — narrative continuity requirements for V4.
6. `docs/V4/V4_CONTRACT_FOUNDATION.md` — the founding V4 principles (mechanism != content, material
   != approved knowledge, AS_IS != TO_BE, AI != authority, provenance mandatory, uncertainty
   explicit).
7. `docs/V4/V4_PROPOSED_ROADMAP.md` — the full R1–R14 round list and each round's original scope.
8. `docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md` — the technical index of enums, IDs, package
   boundaries, and security invariants (verified against actual code as of R14).
9. The result document of the latest **approved** round under `docs/V4/` (its `NEXT=` line names
   the next round) — see `PROJECT_STATE.json.latest_result_path`.
10. The active prompt under `prompts/V4/`, if one exists for that next round.

Do not begin implementing a round whose prompt does not yet exist. Do not treat agent memory —
yours or a predecessor's — as authoritative over any of the above.

## 2. Package Architecture

```text
legacy_documenter/
├── knowledge/
│   ├── domain/            R1  MaterialItem, EvidenceRef, KnowledgeStatement, closed enums
│   ├── input/              R2  Per-SourceType intake validation contracts
│   ├── provenance/         R3  Deterministic node/edge lineage graph
│   ├── ingestion/          R4  Human-supplied MaterialItem intake boundary
│   ├── classification/     R5  KnowledgeNature classification of a MaterialItem
│   ├── temporal/           R6  AS_IS/TO_BE/HISTORICAL/UNSPECIFIED structural bucketing
│   ├── relations/          R7  Explicit DIFFERENCE/GAP/CONFLICT/TEMPORAL_EVOLUTION relations
│   ├── proposals/          R8  Proposal lifecycle up to READY_FOR_REVIEW
│   ├── approval/           R9  Technical Lead ApprovalDecision
│   ├── canonical/          R10 CanonicalKnowledgeEntry — the one canonical Knowledge Source
│   ├── projection/         R11 Human-readable Markdown projection
│   ├── plugin_projection/  R12 LegacyMapperPluginKnowledge 1.0 machine-readable projection
│   ├── closure/            R14 Deterministic final baseline/manifest report builders
│   └── readiness.py        V3  Historical knowledge-readiness gate (unmodified by V4)
├── documentation/          V1–V3 functional/technical document generation (renderer, contracts, …)
├── models/                 V1–V3 code-specific evidence model
├── utils/sanitizer.py      Shared secret-redaction/JSON-sanitization used by every V4 round
└── main.py                 V1–V3 CLI entry point (legacy repository scanning)
```

Every V4 package under `knowledge/` follows the same internal shape, established by R7 and reused
through R13: `enums.py` (closed vocabularies), `models.py` (frozen dataclasses + `validate()` +
`new_*_id()`), `service.py` (a `*Service`/`*Collection` boundary with explicit rejection types), and
`contract_report.py`/`example_report.py` (deterministic JSON artifact builders, `sort_keys=True,
separators=(",", ":")`). Follow this shape for any new package rather than inventing a new one.

## 3. Allowed Dependency Direction

```text
domain
  ← input, provenance, ingestion, classification, temporal, relations
    ← proposals
      ← approval
        ← canonical
          ← projection, plugin_projection   (siblings — neither imports the other)
```

R13 verified this acyclically via `pkgutil.walk_packages` (zero import errors) and an explicit AST
scan confirming `plugin_projection` never imports `projection` and vice versa. A new round must not
introduce a reverse or cross dependency (e.g. `canonical` must never import `projection`).

## 4. Immutable / Read-Only Boundaries

* Every V1–V3 canonical artifact (`output/v3_final/V3_FINAL_BASELINE.json`, V3 evidence, V3
  approved human-review decisions) is a closed, immutable input to V4 — never modify it.
* Every approved V4 round's own contract/example JSON artifact under `output/v4_r*/` is immutable
  once its result document records a SHA-256 for it — regenerate only inside that round's own
  scope, and never silently; a later round may only **recompute and compare** the hash, per R13's
  and R14's own artifact-integrity checks.
* A round only ever reads an earlier round's data structures **read-only**. R9 reads `Proposal`
  read-only and never calls `ProposalCollection.transition`/`.supersede`. R10 reads `Proposal`/
  `ApprovalDecision` read-only and never mutates either. R11/R12 read
  `CanonicalKnowledgeCollection.list()` read-only and never call `.add()`/`.compose()`. This pattern
  is structural (frozen dataclasses raise `dataclasses.FrozenInstanceError` on mutation attempts),
  not just a convention — preserve it in any new code.

## 5. Deterministic IDs

Every V4 identity is derived via `legacy_documenter.documentation.contracts.stable_id` (a V3 SHA-256
helper, reused verbatim by every round) over **semantically load-bearing fields only** — never
`metadata`, current time, randomness, or object/machine identity. See
`docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md` §13 for the full prefix table
(`KST-`/`MAT-`/`EVR-`/`SRC-`/`PRN-`/`PED-`/`CLS-`/`TMP-`/`REL-`/`PRP-`/`APR-`/`KNO-`). When adding a
new identity, reuse `stable_id` — do not invent a second hashing scheme.

## 6. Source Code Optionality

No production type under `legacy_documenter/knowledge/domain`, `canonical`, or `plugin_projection`
requires a filesystem path, code symbol, language, or framework field to be valid (verified by R13's
field-absence scan: no `repository_path`/`project_path`/`symbol`/`method`/`language`/`framework`/
`assembly`/`database` field exists on `MaterialItem`/`EvidenceRef`/`Provenance`/
`CanonicalKnowledgeEntry`/`PluginKnowledgeEntry`). Any new field on those types must preserve this —
a code-specific attribute belongs on a code-specific type (e.g. V3's `legacy_documenter.models.evidence.Evidence`),
never on the shared V4 domain/canonical types.

## 7. The Approval Boundary

Only `legacy_documenter.knowledge.approval` may construct an `ApprovalDecision`, and its only
`ApprovalAuthority` member is `TECHNICAL_LEAD`. No code anywhere in the repository may auto-approve,
auto-reject, or infer a decision from proposal content, origin, or confidence — R9's and R13's tests
assert no `auto_approve`/`ai_approve`/`system_approve`/`infer_approval` symbol exists anywhere under
`legacy_documenter/knowledge`. If a future feature seems to need an automatic approval path, **stop
and raise it as a Technical Lead decision** — do not implement it.

## 8. Canonical Composition

Only `legacy_documenter.knowledge.canonical.service.CanonicalCompositionService.compose()` may
construct a `CanonicalKnowledgeEntry`, and only when the R8/R9 eligibility rule holds (see the
Architecture Reference §10). `CanonicalKnowledgeCollection` is the **only** canonical store type;
never introduce a second one (`human_truth`/`plugin_truth`/similar), even under a different name.

## 9. R11 / R12 Sibling Projections

Both `knowledge/projection` (R11) and `knowledge/plugin_projection` (R12) read only
`CanonicalKnowledgeCollection.list()`. If you extend one, do not make it depend on the other's
output or internal types — a Plugin consumer must never need to parse R11's Markdown to recover
structured knowledge, and R11's document mapping must never depend on R12's JSON shape. Adding a
new projection target (R11) or a new contract field (R12, with an explicit `contract_version` bump)
is additive; do not restructure the shared canonical model to accommodate a projection-specific
need.

## 10. Security Constraints (carry forward from R13)

* Sanitize every free-form string/dict field via `legacy_documenter.utils.sanitizer.sanitize_text`/
  `sanitize_data` before storing it on any new record — this is already the pattern in every R2–R12
  package.
* Never introduce `eval`/`exec`/`compile`(as a call)/dynamic `__import__`/`subprocess`/`os.system`/
  `pickle`/`marshal`/`yaml.load` anywhere under `legacy_documenter/knowledge`. R13's static scan
  checks for exactly these.
* Any path-accepting surface must be validated through a single, closed-set choke point (see
  `legacy_documenter/knowledge/projection/models.py:validate_target_path` as the existing pattern)
  — never trust or concatenate an untrusted path.
* Exception messages must use fixed, non-echoing codes (e.g. `"proposal_not_ready_for_review:DRAFT"`)
  — never interpolate untrusted content into an error message.
* No new production dependency without updating `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`
  (LegacyMapper currently has zero third-party dependencies).

## 11. Python Development Standard

Follow `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md` (in Spanish) for every new module:
`PascalCase` classes, `snake_case` modules/functions, explicit type hints on public boundaries,
concise docstrings explaining purpose/result/non-obvious effects, no `except Exception` outside a
deliberate, documented external boundary, and no premature Repository/Factory/Strategy/DI patterns.
The permanent boundary: **Python discovers and resolves facts; the LLM interprets; the human
approves.**

## 12. Testing Expectations

* Before any change: `python -m unittest discover -s tests` must pass in full (1335 as of R13's
  closure; check `PROJECT_STATE.json.tests` for the current authoritative count).
* After any change: re-run the full suite — never remove, skip, or weaken an existing test to reach
  a PASS. `python -m legacy_documenter.knowledge.readiness` must report `READY`,
  `ai_knowledge_allowed=true`, `ai_knowledge_generated=false`, `provider_calls=0`,
  `real_llm_calls=0`.
* Every new package needs its own `tests/test_v4_r<N>_<name>.py`, following the existing structure:
  entry-gate/regression tests, invariant tests (structural, not just behavioral), a security section
  (secret redaction + prompt-injection inertness + no dynamic execution), and a determinism section
  (contract/example JSON regenerated twice, byte-identical).
* **Never hardcode a `PROJECT_STATE.json` field value that will change once the current round is
  itself approved** — this caused `REG-001` in R13 (a literal `latest_approved_round == "V4-R11"`
  assertion broke the moment R12 closed). Use a round-ordinal or "at least" comparison instead.

## 13. Adding a New Feature Without Bypassing Contracts

1. Read the relevant existing package(s) fully before writing anything — check whether the
   capability already exists, can be composed from an existing type, or requires a new,
   independently-testable package (EXTEND/ADAPT/COMPOSE/REUSE_AS_IS, in that preference order, per
   the pattern every round's result document already documents explicitly).
2. Never modify an earlier round's approved type to add unrelated fields; add a new type or a
   documented, backward-compatible field addition instead (see R4's `MaterialItem.temporal_state`
   addition for the precedent: additive, defaulted, all pre-existing tests re-run unchanged).
3. Preserve every invariant listed in `docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md` — do not
   silently reinterpret `APPROVED`, `CONFIRMED`, `READY_FOR_REVIEW`, or any temporal/relation
   semantics.
4. Write the tests first or alongside the implementation; include an explicit "out of scope"
   section in your round's result document naming what you deliberately did not build.
5. Run the full regression suite and readiness check before declaring the round done.

## 14. When a Change Needs a Technical Lead Decision

Stop and raise it explicitly — do not implement a workaround — when a change would:

* redesign any approved V4 contract's semantics (not just extend it additively);
* introduce any form of automatic approval, automatic status promotion, or automatic
  conflict/gap resolution;
* require a real LLM/provider call anywhere in the deterministic V4 core;
* touch a V3 canonical artifact, an approved V3 human-review decision, or V3 evidence;
* begin the post-V4 maintainability refactor (`POST_V4_MAINTAINABILITY_REFACTOR=PLANNED` — not yet
  authorized to start) or any V5 (`V5_NOT_IMPLEMENTED`) scope;
* would change `PRODUCTION_BEHAVIOR_CHANGED` from `false` to `true` in a round whose own prompt
  requires it to stay `false`.

In every such case: document the finding clearly in your round's result document, do not perform
the change, and continue with the rest of the round's in-scope work rather than blocking entirely.
