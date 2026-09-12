# LegacyMapper V4-R14 — Manuals and Final Baseline — Result

## Governing Principle

```text
DOCUMENT_AND_BASELINE_EXISTING_APPROVED_BEHAVIOR
DO_NOT_REDESIGN_IT
```

This round is a documentation-consolidation round. No production behavior was redesigned. The only
new production code is a small, deterministic report-builder helper package
(`legacy_documenter/knowledge/closure/`), in the same spirit as every R7-R13 `contract_report.py`.

## Required Reading Performed

Read in full, in order, before writing anything: `CLAUDE.md`, `AGENTS.md`, `PROJECT_STATE.json`,
`docs/PROJECT_RECOVERY.md`, `docs/GENERATED_ARTIFACT_POLICY.md`,
`docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`, `docs/V4/V4_CONTRACT_FOUNDATION.md`,
`docs/V4/V4_AI_HANDOVER.md`, `docs/V4/V4_PROPOSED_ROADMAP.md`,
`docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`, and all fourteen approved V4 round result/closure
documents (`V4_R1_KNOWLEDGE_DOMAIN_MODEL_RESULT.md` through `V4_R13_REGRESSION_AND_SECURITY_RESULT.md`
and every `V4_R*_CLOSURE_AND_VERSIONING_RESULT.md`). Inspected the R10/R11/R12 contract+example JSON
artifacts and the R13 regression/security JSON artifacts under `output/v4_r10/` … `output/v4_r13/`.
Inspected the actual production packages under `legacy_documenter/knowledge/` directly (`domain`,
`input`, `provenance`, `ingestion`, `classification`, `temporal`, `relations`, `proposals`,
`approval`, `canonical`, `projection`, `plugin_projection`) — including reading `models.py` for
every round to verify enum members, field names, and identity-prefix helpers by source, not by
memory. `main.py`/`legacy_documenter/main.py` were inspected to confirm the actual, currently
supported CLI surface before writing the User Manual's operational section.

## Result

```text
STATUS=V4_R14_MANUALS_AND_FINAL_BASELINE_COMPLETE

ENTRY_GATE=PASS

BASELINE_TESTS=1335_PASS
FINAL_TESTS=1380_PASS

MANUALS_CREATED=docs/V4/V4_USER_MANUAL.md;docs/V4/V4_DEVELOPER_MANUAL.md;docs/V4/V4_OPERATIONS_AND_RECOVERY_MANUAL.md;docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md
MANUALS_UPDATED=AGENTS.md(minimal,phase-control-staleness-fix);docs/V4/V4_AI_HANDOVER.md(minimal,current-state-pointer-fix);docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md(minimal,additive-output-dir-list-fix)

FINAL_BASELINE=output/v4_r14/V4_FINAL_BASELINE.json
FINAL_BASELINE_SHA256=d13e3807a12187b226ea55752ae0e9dccd2ad20c9dbe044360ffa48bca526d1e

FINAL_MANIFEST=output/v4_r14/V4_FINAL_MANIFEST.json
FINAL_MANIFEST_SHA256=be398240a31137e7dea25fcaa7b3cfe6580d2557f990f7da884d5775f5c40551

FINAL_BASELINE_DETERMINISM=PASS
FINAL_MANIFEST_DETERMINISM=PASS

APPROVED_ARTIFACT_INTEGRITY=PASS
BROKEN_INTERNAL_REFERENCES=0

ONE_CANONICAL_KNOWLEDGE_SOURCE=PASS
TECHNICAL_LEAD_FINAL_APPROVAL_AUTHORITY=PASS
SOURCE_CODE_OPTIONAL=PASS

R11_BOUNDARY=PASS
R12_BOUNDARY=PASS
R11_R12_SIBLING_PROJECTIONS=PASS

PLUGIN_CONTRACT_NAME=LegacyMapperPluginKnowledge
PLUGIN_CONTRACT_VERSION=1.0
PLUGIN_RUNTIME=NOT_IMPLEMENTED

SECURITY_GATE=PASS
REGRESSION_GATE=PASS
CRITICAL_OPEN=0
HIGH_OPEN=0
MEDIUM_OPEN=0
LOW_OPEN=0

V5_IMPLEMENTED=false

POST_V4_MAINTAINABILITY_REFACTOR=PLANNED

MAINTAINABILITY_BASELINE=CAPTURED(output/v4_r14/V4_FINAL_BASELINE.json -> maintainability_baseline)
DEFERRED_DEBT=TD-001;TD-002;TD-003;TD-004;TD-005;DEBT-001;DEBT-002;DEBT-003

REPOSITORY_CONTINUITY=PASS
AGENT_NEUTRAL_CONTINUITY=PASS

PRODUCTION_CODE_CHANGED=false
PRODUCTION_BEHAVIOR_CHANGED=false

READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0

PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW

DECISION=V4_R14_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R14
```

## Entry Gate

`PROJECT_STATE.json` confirmed before any change: `latest_completed_round=V4-R13`,
`latest_approved_round=V4-R13`, `current_round_in_progress=null`, `round_status=V4-R13_APPROVED`,
`next=V4-R14`, `tests=1335`, `readiness=READY`, `provider_calls=0`, `real_llm_calls=0`.
`python -m unittest discover -s tests` → **1335 tests, OK**.
`python -m legacy_documenter.knowledge.readiness` → `READINESS=READY`,
`AI_KNOWLEDGE_ALLOWED=true`, `AI_KNOWLEDGE_GENERATED=false`, `PROVIDER_CALLS=0`,
`REAL_LLM_CALLS=0`. `git status` showed only the new
`prompts/V4/V4_R14_MANUALS_AND_FINAL_BASELINE.md` untracked, exactly as expected. Entry gate:
**PASS**.

## Manuals — Created

All four suggested filenames were used exactly as named in the prompt; no deviation, so no
justification is required for a filename change. No existing document already fulfilled any of
these four responsibilities (the closest candidates, `docs/V3/MANUAL_TECNICO_LEGACYMAPPER_V3.md`
and `docs/V3/MANUAL_USUARIO_LEGACYMAPPER_V3.md`, are V3-era and describe the closed V3 baseline, not
the V4 multi-source knowledge pipeline; they were left untouched, per the immutability of closed V3
documents).

1. `docs/V4/V4_USER_MANUAL.md` — Technical Lead / controlled operator audience. Covers: what
   LegacyMapper does/does not do; the four supported input modes (`CODE_ONLY`,
   `CODE_AND_HUMAN_INFORMATION`, `HUMAN_INFORMATION_ONLY`, `PARTIAL_INFORMATION`); how human
   material fits; the material→proposal→review→approval pipeline; Technical Lead sole approval
   authority (`AI_NEVER_GRANTS_APPROVAL`/`SYSTEM_NEVER_GRANTS_APPROVAL`); the one canonical
   Knowledge Source and its two sibling projections; handling of partial/unresolved information;
   provenance; AS_IS/TO_BE/HISTORICAL; and safe operational expectations. Verified against
   `legacy_documenter/main.py`'s actual `argparse` definition before writing §9 — no V4
   knowledge-pipeline CLI subcommand exists; only the original V1-V3 `main.py "<repo>" --output
   "<dir>" [--verbose]` scanning CLI does, and the manual states this explicitly rather than
   inventing a command.

2. `docs/V4/V4_DEVELOPER_MANUAL.md` — future developer/AI agent audience. Covers: the repository
   authority reading order; the twelve-package `knowledge/` architecture and each package's single
   responsibility; the acyclic dependency direction (verified against R13's own
   `pkgutil.walk_packages` finding); immutable/read-only boundaries (frozen dataclasses, R9's
   read-only `Proposal` access, R10's read-only `Proposal`/`ApprovalDecision` access, R11/R12's
   read-only `CanonicalKnowledgeCollection.list()` access); the deterministic ID-prefix table;
   source-code optionality; the approval and canonical-composition boundaries; R11/R12 sibling
   independence; carried-forward security constraints; a pointer to the Python development
   standard; testing expectations (including the explicit `REG-001` lesson about not hardcoding a
   `PROJECT_STATE.json` literal); how to add a feature without bypassing contracts; and when a
   change requires a Technical Lead decision instead of an implementation attempt.

3. `docs/V4/V4_OPERATIONS_AND_RECOVERY_MANUAL.md` — explicitly aligned with, not duplicating or
   contradicting, `docs/PROJECT_RECOVERY.md` (read first, as instructed). Covers: startup/recovery
   reading order; `PROJECT_STATE.json`'s role and field semantics; readiness checks; the full
   regression command; repository cleanliness expectations; the generated-artifact policy summary;
   reviewed-artifact integrity verification procedure (the same recompute-and-compare discipline
   this very round performed for R10-R13); Git safety rules; secret safety; how to resume after
   interrupted AI work; how to identify the latest approved round (via its closure record); what
   must never be reconstructed from memory when repository evidence exists; and how to distinguish
   a pending implementation from an approved checkpoint (using V4-R14's own current state as the
   worked example).

4. `docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md` — concise technical reference, not a
   narrative manual. Contains an architecture diagram; an R1-R14 responsibility table; the full
   `SourceType` (12), `KnowledgeNature` (17), `KnowledgeStatus` (7), `TemporalState`/`TemporalBucket`,
   `RelationKind` (4), `ProposalKind` (8)/`ProposalStatus` (4)/`ProposalMethod` (3),
   `ApprovalDecisionType` (3)/`ApprovalAuthority` (1) vocabularies; the `CanonicalKnowledgeEntry`
   structure and eligibility rule; the R11 projection boundary (41-document 00-09 family, rule
   model, traceability marker format); the R12 contract boundary (`LegacyMapperPluginKnowledge`
   `1.0`, metadata-not-projected policy); the full deterministic ID-prefix table (`KST-`, `MAT-`,
   `EVR-`, `SRC-`, `PRN-`, `PED-`, `CLS-`, `TMP-`, `REL-`, `PRP-`, `APR-`, `KNO-` — each verified
   directly against its `new_*_id`/`stable_id(...)` call site in the actual source, not assumed);
   the R13 security invariant list; and the V5 boundary. Every enum member and prefix listed was
   grep-verified against the actual `enums.py`/`models.py` source in this round, not carried over
   from memory of the round result documents alone.

## Manuals — Updated (Minimal, Justified)

Per the prompt's "Repository Authority / AI Handover" section, three existing continuity documents
were reviewed and given small, additive, non-redesigning corrections — each is a genuine staleness
fix that would otherwise mislead a fresh agent, not a new capability:

* **`AGENTS.md`** — its "Phase Control" section still listed a hardcoded `V2-R1.1 → APPROVED … V2-R4
  → CURRENT` progression from the V2 era, directly contradicting the actual V4-R13 state. Replaced
  the hardcoded list with an explicit pointer to `PROJECT_STATE.json` as the single authoritative
  phase/round pointer, so this section can never go stale again for any future version. No rule,
  permission boundary, or safety constraint was changed.
* **`docs/V4/V4_AI_HANDOVER.md`** — its "Current Project State" section still read
  `V4: FOUNDATION / DEFINITION` / "V4 implementation has not started," written before V4-R1 began.
  Updated to `V4: IMPLEMENTATION_IN_PROGRESS` with an explicit note that R1-R13 are implemented and
  approved, R14 is the final planned round, and that a fresh agent must always defer to
  `PROJECT_STATE.json` over this document's own historical language. No principle/philosophy
  section was altered.
* **`docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`** — its "V4 Round Results" section only listed
  `output/v4_bootstrap/`, `output/v4_r1/`, `output/v4_r1_1/` (as written by R1.1) and its "Tests"
  section hardcoded "676 tests." Extended the round-results list additively to cover
  `output/v4_r2/` … `output/v4_r14/` (each already small and non-heavy, consistent with this
  document's own classification criteria) and replaced the hardcoded test count with a pointer to
  `PROJECT_STATE.json.tests`, for the same anti-staleness reason as the `AGENTS.md` fix.

`CLAUDE.md` was reviewed and left unchanged — it is already a minimal bootstrap pointing at
`AGENTS.md`, `PROJECT_STATE.json`, `V4_AI_HANDOVER.md`, the V3 baseline, and the active prompt, and
adding manual references to it would violate the prompt's own instruction that it "must remain a
minimal bootstrap."

## Final Baseline and Manifest

`legacy_documenter/knowledge/closure/` (`artifact_hashes.py`, `maintainability.py`,
`baseline_report.py`, `manifest_report.py`) builds both deterministically from live repository
state — `PROJECT_STATE.json`, the R13 regression/security report, recomputed R10-R13 artifact
hashes, and an `ast`/`os.walk`-based maintainability scan (no new dependency). Both were generated,
inspected, and then **regenerated one final time** after `PROJECT_STATE.json` was updated to its
R14 pending-review state (so the baseline's own `test_count`/`latest_completed_round` reflect the
final, post-test-authoring state) — see `FINAL_BASELINE_SHA256`/`FINAL_MANIFEST_SHA256` above for
the resulting values.

`APPROVED_ARTIFACT_INTEGRITY=PASS`: `artifact_hashes.verify_reviewed_artifacts()` recomputed SHA-256
for all eight reviewed R10-R13 artifacts from disk and compared each against the value recorded in
that round's own result document (never a second, independently hardcoded copy) — all eight
matched exactly:

```text
output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_CONTRACT.json  MATCH
output/v4_r10/V4_CANONICAL_KNOWLEDGE_COMPOSITION_EXAMPLE.json   MATCH
output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_CONTRACT.json  MATCH
output/v4_r11/V4_HUMAN_READABLE_DOCUMENT_PROJECTION_EXAMPLE.json   MATCH
output/v4_r12/V4_PLUGIN_FACING_OUTPUT_CONTRACT.json  MATCH
output/v4_r12/V4_PLUGIN_FACING_OUTPUT_EXAMPLE.json   MATCH
output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json     MATCH
output/v4_r13/V4_SECURITY_INVARIANTS.json            MATCH
```

No mismatch was found; the round did not need to invoke its STOP condition for this check.

`FINAL_BASELINE_DETERMINISM=PASS` / `FINAL_MANIFEST_DETERMINISM=PASS`: both builders were invoked
twice from independent `python -c` subprocess invocations after the final `PROJECT_STATE.json`
update; both produced byte-identical output matching each other and the on-disk artifact's SHA-256
exactly (see the two hash values quoted above, reproduced identically across three separate
invocations during this round).

`BROKEN_INTERNAL_REFERENCES=0`: every path listed in `output/v4_r14/V4_FINAL_MANIFEST.json` (all
nine categories) was verified to exist on disk by `manifest_report._existing()` before being
included (a missing candidate raises `ManifestPathError` rather than being silently included), and
`tests/test_v4_r14_manuals_and_final_baseline.py::ManifestPathsExistTests` independently re-checks
every manifest path plus every backtick-quoted repository-relative path reference found in the four
new manuals.

## Maintainability Baseline (Diagnostic)

Captured inside `V4_FINAL_BASELINE.json.maintainability_baseline`: 143 production `.py` modules
under `legacy_documenter/` (74 of them under `legacy_documenter/knowledge/`, across 13
sub-packages, `closure/` being the only one added by this round), 41 test modules under `tests/`,
296 public classes/functions scanned with 0 missing docstrings, 255 functions scanned with 3
missing return-type annotations (diagnostic only, not treated as a defect), the ten largest
`knowledge/` modules by line count, and the full carried-forward debt list (`TD-001`..`TD-005` from
V3's `output/v3_r10_1/TECHNICAL_DEBT_REMAINING.json`, plus R13's `DEBT-001`..`DEBT-003` from
`output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json`). This baseline is diagnostic only; no refactor
was performed.

## Discrepancy / STOP Items Found

None required a full STOP. One item worth flagging explicitly: while verifying the manifest's
self-referencing `baseline` category (`output/v4_r14/V4_FINAL_BASELINE.json` and
`.../V4_FINAL_MANIFEST.json` listing themselves), the manifest builder's existence check needed the
manifest file to already exist before it could describe itself — resolved by creating an empty
placeholder file before the first generation pass, then overwriting it with real content; this is
noted here for transparency, not as a defect, since the final on-disk file and its rebuilt-from-
scratch equivalent are byte-identical (see determinism above).

## Security / Regression Preserved

`SECURITY_GATE=PASS` and `REGRESSION_GATE=PASS` were **re-derived from R13's own artifacts**
(`output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json`), not re-run from scratch — nothing in R14
changed any code R13 validated. `CRITICAL_OPEN=0`, `HIGH_OPEN=0`, `MEDIUM_OPEN=0`, `LOW_OPEN=0`,
all consistent with R13's closure. No credential, token, private key, or `.env`-shaped content
appears anywhere in the four new manuals or the two new JSON artifacts (spot-checked manually and
covered by `tests/test_v4_r14_manuals_and_final_baseline.py::NoMachineSpecificPathTests`).

## Tests

`tests/test_v4_r14_manuals_and_final_baseline.py` — 45 new tests covering all 20 required items
from the prompt's "Required Tests" section: entry-gate/continuity, manual existence, required
contract markers, Plugin contract name/version match against R12's own artifact, one-canonical-
source/source-code-optionality/Technical-Lead-authority/V5-not-implemented/post-V4-refactor-planned
markers, baseline/manifest JSON validity, baseline/manifest determinism, absence of machine-specific
absolute paths and timestamp-shaped fields, artifact-hash integrity (recomputed independently of the
production `closure` package's own hashing call), manifest-path and manual-internal-reference
existence, security/regression-state preservation, absence of any provider/LLM import in the new
code, and agent-neutral repository continuity.

**No test hardcodes a `PROJECT_STATE.json`/round-state literal that would break once V4-R14 is
itself approved** — every such assertion (`test_project_state_at_least_r13_approved`,
`test_latest_completed_round_is_r14_or_later`, `test_latest_approved_round_is_at_least_r13`) uses
the `_round_ordinal()` helper for a "≥ N" comparison instead of an exact string match, directly
applying the `REG-001` lesson from R13. `test_project_state_not_marked_r14_approved` only asserts
the round is *not yet* marked approved — a check that expires cleanly (becomes moot, not false) the
moment R14 is formally approved and superseded by V4-R15 or a closure step, rather than breaking.

## Final Regression

```text
python -m unittest discover -s tests   -> 1380 tests, OK (1335 baseline + 45 new V4-R14 tests)
python -m legacy_documenter.knowledge.readiness
    -> READINESS=READY, AI_KNOWLEDGE_ALLOWED=true, AI_KNOWLEDGE_GENERATED=false,
       PROVIDER_CALLS=0, REAL_LLM_CALLS=0
```

No pre-existing test was removed, skipped, or weakened.

## Production Code / Behavior

`PRODUCTION_CODE_CHANGED=false` in the sense the prompt cares about (no existing V1-V13 production
module's *behavior* was modified): the only production code added is the new, additive
`legacy_documenter/knowledge/closure/` package (four small modules, ~330 lines total), which reads
already-approved repository state and writes only the two new R14 output artifacts — it does not
alter any existing package's public surface or behavior. `PRODUCTION_BEHAVIOR_CHANGED=false`. No
actual approved-contract defect was discovered in any R1-R13 package during this round's reading —
if one had been, per the prompt's instruction, it would have been reported here and left unfixed
rather than silently corrected.

## Files Added / Changed

```text
docs/V4/V4_USER_MANUAL.md                                          (new)
docs/V4/V4_DEVELOPER_MANUAL.md                                     (new)
docs/V4/V4_OPERATIONS_AND_RECOVERY_MANUAL.md                       (new)
docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md                  (new)
docs/V4/V4_R14_MANUALS_AND_FINAL_BASELINE_RESULT.md                (new, this file)
AGENTS.md                                                          (minimal edit: Phase Control staleness)
docs/V4/V4_AI_HANDOVER.md                                          (minimal edit: current-state pointer)
docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md                       (minimal edit: round-results list, test count pointer)
legacy_documenter/knowledge/closure/__init__.py                    (new)
legacy_documenter/knowledge/closure/artifact_hashes.py             (new)
legacy_documenter/knowledge/closure/maintainability.py             (new)
legacy_documenter/knowledge/closure/baseline_report.py             (new)
legacy_documenter/knowledge/closure/manifest_report.py             (new)
tests/test_v4_r14_manuals_and_final_baseline.py                    (new, 45 tests)
output/v4_r14/V4_FINAL_BASELINE.json                                (new)
output/v4_r14/V4_FINAL_MANIFEST.json                                (new)
PROJECT_STATE.json                                                 (updated, pending review)
```

## PROJECT_STATE

```text
PROJECT_STATE=UPDATED_PENDING_HUMAN_REVIEW
```

`PROJECT_STATE.json` updated: `latest_completed_round=V4-R14`, `latest_approved_round=V4-R13`
(**unchanged** — R14 is not yet approved), `current_round_in_progress="V4-R14 (pending Technical
Lead review)"`, `round_status="V4-R14_READY_FOR_HUMAN_REVIEW"`, `next="HUMAN_REVIEW_V4_R14"`,
`tests=1380`, `readiness=READY`, `ai_knowledge_allowed=true`, `ai_knowledge_generated=false`,
`provider_calls=0`, `real_llm_calls=0`, `latest_result_path` updated to point at this document. V4
is **not** marked formally closed.

## Decision / Next

```text
DECISION=V4_R14_READY_FOR_HUMAN_REVIEW
NEXT=HUMAN_REVIEW_V4_R14
```

R14 is implemented, tested, and documented. It has not been approved, committed, or pushed. No V5
work, Plugin runtime, or post-V4 maintainability refactor was started. This is the final planned V4
round; the next action is Technical Lead review of this round and, if approved, formal closure of
V4 as a whole — neither of which this round performs on its own initiative.

## Stop

Per the active prompt: no commit or push was performed; R14 was not self-approved; V4 was not
marked formally closed; no post-V4 refactor or V5 work was begun; no Plugin runtime was
implemented; no provider/LLM call was made anywhere in this round.

## Closure — Human Approval Recorded

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD

MANUALS_DECISION=APPROVED
FINAL_BASELINE_DECISION=APPROVED
FINAL_MANIFEST_DECISION=APPROVED
CONTINUITY_CORRECTIONS_DECISION=APPROVED
CLOSURE_HELPER_PACKAGE_DECISION=APPROVED
MAINTAINABILITY_BASELINE_DECISION=APPROVED

R14_1_REQUIRED=false

ROUND_STATUS=APPROVED

DECISION=V4_R14_FORMALLY_APPROVED

NEXT=V4_FINAL_CLOSURE
```
