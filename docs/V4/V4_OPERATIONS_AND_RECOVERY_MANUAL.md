# LegacyMapper V4 — Operations and Recovery Manual

This manual explains how to operate LegacyMapper safely day-to-day and how to recover project
state from the repository alone. It reuses and aligns with `docs/PROJECT_RECOVERY.md` rather than
contradicting it — where the two overlap, `docs/PROJECT_RECOVERY.md` remains the canonical
step-by-step clone/verify procedure and this manual adds the broader operational context around it.

## 1. Startup / Recovery Reading Order

On a fresh checkout, with no prior session memory, read in this order:

1. `CLAUDE.md` — minimal bootstrap; points at everything below.
2. `AGENTS.md` — permission boundary and phase control.
3. `PROJECT_STATE.json` — the authoritative, machine-readable pointer to current state.
4. `docs/PROJECT_RECOVERY.md` — clone/verify procedure and current-state pointers.
5. `docs/V4/V4_AI_HANDOVER.md` — narrative continuity requirements.
6. `output/v3_final/V3_FINAL_BASELINE.json` — the closed V3 baseline V4 builds on.
7. The active prompt under `prompts/V4/`, if the next round is already scoped.

Never substitute a remembered summary of these documents for actually reading them on a new
session — the whole point of this ordering is that it works with zero prior memory.

## 2. `PROJECT_STATE.json`'s Role

This file is the single machine-readable source of truth for "what round are we on and is it
approved." Key fields:

* `latest_completed_round` — the highest round whose **implementation** finished (may not yet be
  approved).
* `latest_approved_round` — the highest round the Technical Lead has **formally approved**. This is
  the round whose contracts/artifacts are safe to build on without re-litigating them.
* `round_status` / `current_round_in_progress` / `next` — where things stand right now and what
  action is expected next (e.g. `HUMAN_REVIEW_V4_R14`).
* `tests`, `readiness`, `ai_knowledge_allowed`, `ai_knowledge_generated`, `provider_calls`,
  `real_llm_calls` — the last-verified regression/readiness snapshot.

A round in progress always keeps `latest_approved_round` at the **previous** approved round until
the Technical Lead formally closes it — never advance this field yourself as the implementing agent.

## 3. Readiness Checks

```text
python -m unittest discover -s tests
python -m legacy_documenter.knowledge.readiness
```

Expected at any healthy checkpoint: the exact test count recorded in `PROJECT_STATE.json.tests`
(all `PASS`, zero failures/errors/skips), and `readiness=READY`, `ai_knowledge_allowed=true`,
`ai_knowledge_generated=false`, `provider_calls=0`, `real_llm_calls=0`. If either check fails on a
clean, unmodified checkout: **stop and report**, per `AGENTS.md` phase control — do not proceed with
new development.

## 4. Full Regression Command

`python -m unittest discover -s tests` is the full regression suite. It must be run before starting
any round (entry gate) and again before declaring a round done (final regression). Never skip,
remove, or weaken an existing test to make this pass — a shrinking or weakening test count is itself
a regression.

## 5. Repository Cleanliness Expectations

Before starting a new round, `git status` should show a clean tree except for the new round's own
prompt file under `prompts/V4/` (the round has not started yet, so only its instructions exist as
new). If unrelated uncommitted work is present, stop and ask rather than building on top of it or
silently discarding it.

## 6. Generated Artifact Policy

See `docs/GENERATED_ARTIFACT_POLICY.md` for the full rules. In short: a generated artifact is
versioned in Git only if some other approved document (a baseline, a closure record, a round result)
references it by path or hash — otherwise it is a regenerable, excluded-from-Git byproduct (Python
caches, heavy full-repository scan dumps, leftover smoke-test runs). Excluding a path from Git never
means deleting it from disk.

## 7. Reviewed Artifact Integrity

Every approved round's contract/example JSON artifact under `output/v4_r*/` has its SHA-256 recorded
in that round's own result document (`docs/V4/V4_R*_RESULT.md`). A later round (R13, and now R14)
must **recompute** the hash from disk and compare it against that recorded value — never trust that
the file "probably" still matches, and never regenerate/overwrite a reviewed artifact to make a
mismatch go away. If a mismatch is ever found: **stop immediately** and report it as a repository
integrity issue for the Technical Lead, rather than silently reconciling it. `output/v4_r14/`'s own
`V4_FINAL_BASELINE.json` records the R10–R13 hashes it recomputed for this exact purpose.

## 8. Git Safety Rules

* Never run a destructive Git command (`reset --hard`, `push --force`, `checkout .`, `clean -f`,
  `branch -D`) unless explicitly instructed.
* Never skip commit hooks (`--no-verify`) or bypass signing unless explicitly instructed.
* Prefer new commits over amending existing ones.
* Stage specific files by name; never `git add -A`/`git add .` blindly, to avoid accidentally
  including secrets or large binaries.
* Never push, publish, or deploy without explicit instruction — this is called out separately in
  `AGENTS.md`'s permission boundary.
* An implementing round never approves itself, never marks V4 formally closed, and never commits or
  pushes on its own initiative unless its own prompt explicitly authorizes it (compare: R1–R14's
  implementation rounds all end `NEXT=HUMAN_REVIEW_V4_R<N>`; a separate `_CLOSURE_AND_VERSIONING_`
  step records the Technical Lead's actual approval).

## 9. Secret Safety

* Never place credentials, tokens, connection strings, or `.env` content in any committed file —
  `.gitignore` excludes `.env*` as a safety net, but none should exist in the first place.
* Every free-form string/dict field flowing into a V4 knowledge record is sanitized via
  `legacy_documenter.utils.sanitizer` before storage; exception messages use fixed, non-echoing
  codes that never interpolate untrusted content.
* Before publishing or committing anything, double-check new files for anything secret-shaped —
  even in an innocuous-looking filename — per the standing Git safety protocol.

## 10. Resuming After Interrupted AI Work

1. Run `git status`. If there is uncommitted work from an interrupted session, read it before
   deciding whether to keep, finish, or discard it — never blindly reset.
2. Read `PROJECT_STATE.json`. Compare `latest_completed_round` against `latest_approved_round`: a
   gap between them means the higher round's implementation exists but has not yet been reviewed —
   treat it as **pending human review**, not as approved, regardless of how complete it looks.
3. Read that pending round's own result document (`docs/V4/V4_R<N>_..._RESULT.md`) in full — it
   records exactly what was implemented, what was deliberately left out of scope, and what its
   `DECISION`/`NEXT` fields say.
4. Re-run the full regression suite and readiness check yourself; do not trust a stale summary.
5. Do not silently continue into the next round while a prior round sits unapproved — respect
   `AGENTS.md`'s phase control ("do not automatically start the next round").

## 11. Identifying the Latest Approved Round

`PROJECT_STATE.json.latest_approved_round` is authoritative. Corroborate it, if in doubt, by finding
that round's `docs/V4/V4_R<N>_CLOSURE_AND_VERSIONING_RESULT.md` (or, for R13, the
`## Closure — Human Approval Recorded` section appended to its own result document) — every formally
approved round has one of these two forms, each stating `HUMAN_REVIEW=APPROVED`,
`APPROVAL_AUTHORITY=TECHNICAL_LEAD`, and `ROUND_STATUS=APPROVED`. A round with no such record,
however complete its implementation looks, is not approved.

## 12. What Must Never Be Reconstructed From Memory

When repository evidence exists, always defer to it over any agent's memory or summary, including
this manual's own prose if it ever appears to disagree with:

* the actual enum members, field names, and validation logic in `legacy_documenter/knowledge/*`;
* the SHA-256 values and JSON content of `output/v4_r*/*.json` contract/example artifacts;
* the literal text of an approved round's result/closure document;
* `PROJECT_STATE.json`'s current field values.

`docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md` was itself built this way for R14 — verified
against the actual code and artifacts, not reconstructed from a prior conversation — and should be
treated as a starting index, not a replacement for checking the underlying source when precision
matters (e.g. before changing a contract).

## 13. Pending Implementation vs. Approved Checkpoint

* **Pending implementation**: a round's code, tests, and result document exist and the entry
  gate/regression/readiness checks all pass, but no `_CLOSURE_AND_VERSIONING_RESULT.md` (or
  equivalent embedded closure section) exists yet, and `PROJECT_STATE.json.round_status` reads
  `..._READY_FOR_HUMAN_REVIEW`. Treat its contracts as a proposal to review, not as a foundation to
  build the next round on.
* **Approved checkpoint**: the round has an explicit closure record with
  `HUMAN_REVIEW=APPROVED`/`ROUND_STATUS=APPROVED`, and `PROJECT_STATE.json.latest_approved_round`
  names it (or a later round). Only an approved checkpoint's contracts are safe to treat as a stable
  foundation for new work.

As of V4-R14's own implementation, `PROJECT_STATE.json.latest_approved_round` remains `V4-R13` —
R14 itself is `V4-R14_READY_FOR_HUMAN_REVIEW`, pending exactly this distinction.
