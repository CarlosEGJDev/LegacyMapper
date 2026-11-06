# LegacyMapper V4 — R1.1 Repository Versioning and Recovery

TASK=V4_R1_1_REPOSITORY_VERSIONING_AND_RECOVERY

MODE=REPOSITORY_OPTIMIZATION_AND_VALIDATION

IMPLEMENTATION_ALLOWED=true

FUNCTIONAL_BEHAVIOR_CHANGES_ALLOWED=false

---

# Objective

Prepare LegacyMapper to be safely versioned in Git/GitHub while preserving full development continuity across:

* different computers;
* different Claude sessions;
* Codex;
* future development agents;
* loss of conversational history.

The repository must contain the authoritative project state required to understand:

* what LegacyMapper is;
* what V1, V2 and V3 accomplished;
* what V4 currently implements;
* which decisions are approved;
* what the current baseline is;
* which tests must pass;
* what the next development step is;
* which large artifacts are intentionally excluded;
* how excluded artifacts can be restored or regenerated when needed.

The repository MUST NOT depend on AI conversation history for continuity.

This round is repository/infrastructure organization only.

Do not implement V4-R2.

---

# Required Reading

Read before changing anything:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `docs/V4/V4_AI_HANDOVER.md`
4. `docs/V4/V4_CONTRACT_FOUNDATION.md`
5. `docs/V4/V4_PROPOSED_ROADMAP.md`
6. `docs/V4/V4_00_BOOTSTRAP_RESULT.md`
7. `docs/V4/V4_00_1_ROADMAP_APPROVAL_RESULT.md`
8. `docs/V4/V4_R1_KNOWLEDGE_DOMAIN_MODEL_RESULT.md`
9. `output/v3_final/V3_FINAL_BASELINE.json`
10. `codex/V3/V3_CIERRE_FINAL.md`
11. `docs/LEGACYMAPPER_PYTHON_DEVELOPMENT_STANDARD.md`

Also inspect:

* repository root structure;
* current `.gitignore`, if present;
* all `output/` directories;
* all `codex/` historical directories;
* generated reports;
* logs;
* temporary/staging directories;
* Python caches;
* test artifacts;
* large JSON files;
* ZIP files;
* generated graph/flow/traceability artifacts;
* any local configuration or secret-bearing files.

Do not assume conversation history.

The repository is authoritative.

---

# Entry Gate

Before modifications verify:

V3_BASELINE=VALID

TESTS>=676_PASS

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true

AI_KNOWLEDGE_GENERATED=false

V4_R1=COMPLETE

No real LLM/provider calls are allowed.

If the entry gate fails, stop and report.

---

# Core Principle

Git must contain the MINIMUM COMPLETE CONTINUITY SET.

That means:

```text
VERSIONED REPOSITORY
=
SOURCE CODE
+ TESTS
+ CONTRACTS
+ APPROVED DECISIONS
+ ACTIVE ROADMAP
+ PROMPTS
+ HANDOVERS
+ MANUALS
+ SMALL BASELINES
+ RECOVERY INSTRUCTIONS
+ REQUIRED CONFIGURATION TEMPLATES
```

It must NOT automatically contain:

```text
GENERATED HEAVY DATA
+ REGENERABLE INTERMEDIATE OUTPUTS
+ FAILED ATTEMPT ARTIFACTS
+ TEMPORARY DATA
+ CACHES
+ LOGS
+ LOCAL MACHINE STATE
```

---

# Critical Continuity Requirement

A fresh capable development agent with:

* no prior conversation;
* no prior Claude session;
* no prior Codex session;
* no access to the previous PC;

must be able to clone the repository and determine:

1. what the project does;
2. project architecture and principles;
3. historical V1/V2/V3 status;
4. current V4 status;
5. current test baseline;
6. approved decisions;
7. which artifacts are intentionally absent;
8. how missing heavy artifacts are obtained/regenerated;
9. next development task.

This must be validated explicitly.

---

# Phase 1 — Repository Inventory

Before deleting, moving or ignoring anything, produce a deterministic repository inventory.

Create:

`output/v4_r1_1/V4_REPOSITORY_INVENTORY.json`

For each relevant file or directory record where practical:

* path;
* type;
* size;
* category;
* generated/not generated when determinable;
* required_for_runtime;
* required_for_tests;
* required_for_historical_continuity;
* required_for_current_development;
* regenerable;
* regeneration source/command when known;
* contains_possible_secrets;
* recommended disposition.

Recommended dispositions:

* KEEP_IN_GIT
* KEEP_SMALL_BASELINE
* IGNORE_REGENERABLE
* IGNORE_LOCAL_ONLY
* ARCHIVE_EXTERNAL
* GIT_LFS_CANDIDATE
* MANUAL_REVIEW_REQUIRED

Do not modify anything until this inventory exists.

---

# Phase 2 — Large Artifact Analysis

Identify:

* files > 1 MiB;
* files > 10 MiB;
* files > 50 MiB;
* files >= 100 MiB;
* large directories;
* duplicated outputs;
* ZIP archives;
* intermediate V1/V2/V3 run outputs;
* failed-attempt artifacts;
* graph/flow/traceability dumps;
* generated knowledge/context packages.

Create:

`output/v4_r1_1/V4_LARGE_ARTIFACT_ANALYSIS.json`

For each significant large artifact determine whether it is:

1. canonical and irreplaceable;
2. canonical but reproducible;
3. historical evidence only;
4. generated intermediate state;
5. failed-attempt residue;
6. local/cache/temp state.

Do not decide purely by file size.

Meaning and recoverability are more important than size.

---

# Phase 3 — Define the Continuity Set

Create:

`docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`

This document defines exactly what MUST remain versioned.

At minimum retain:

## Production

* `legacy_documenter/`
* dependency/project configuration required to run it.

## Tests

* `tests/`

## Agent-independent governance

* `AGENTS.md`
* `CLAUDE.md`
* applicable development standards.

## V4

* `docs/V4/`
* `prompts/V4/`
* approved V4 result reports;
* active roadmap;
* handovers;
* contracts.

## V3 closure

Preserve the minimum authoritative V3 closure set required to prove and understand:

* V3 formally closed;
* final readiness;
* approved human review;
* baseline hashes/state;
* AI knowledge not generated.

At minimum consider:

* `output/v3_final/V3_FINAL_BASELINE.json`
* `codex/V3/V3_CIERRE_FINAL.md`
* final V3 manuals;
* final approved V3 result/closure reports;
* active/canonical V3 governance information required by V4.

Do not automatically retain every historical attempt.

## V1/V2 historical continuity

Keep enough documentation to know:

* what each phase accomplished;
* final approved status;
* canonical output definitions;
* how large canonical outputs can be regenerated if necessary.

Historical execution noise is not authoritative continuity.

---

# Historical `codex/` Directories

Do NOT blindly delete or rename:

* `codex/V1`
* `codex/V2`
* `codex/V3`

They are historical records.

However, determine which contained files are:

* canonical final records;
* prompts worth preserving;
* approved decisions;
* failed attempts;
* duplicated bulky outputs;
* generated artifacts.

If heavy generated data exists inside historical directories, recommend/exclude it only when continuity is preserved through retained documentation and recovery instructions.

Do not rewrite history unnecessarily.

---

# Phase 4 — Generated Data Policy

Create:

`docs/GENERATED_ARTIFACT_POLICY.md`

Define categories such as:

## Canonical small artifacts

Versioned.

Examples:

* baselines;
* manifests;
* hashes;
* final status JSON;
* compact indexes.

## Heavy regenerable artifacts

Not versioned in normal Git.

Examples may include:

* architecture graph dumps;
* functional flow dumps;
* traceability dumps;
* temporary system-context dumps;
* repeated generated runs.

They must have:

* documented origin;
* regeneration procedure or source dependency;
* expected identity/hash when important.

## Heavy non-regenerable artifacts

Do not discard.

Classify for:

* external archive;
* GitHub Release;
* Git LFS;
* secure storage;

depending on semantics and security.

This round may recommend an external mechanism but must not upload data externally automatically.

---

# Phase 5 — `.gitignore`

Create or update root:

`.gitignore`

It should cover appropriate local/generated data such as:

* Python caches;
* test caches;
* coverage artifacts;
* IDE local data where appropriate;
* temporary files;
* logs;
* staging;
* generated heavy outputs;
* local runtime files;
* secrets/local environment files;
* backup files.

Do not ignore:

* source;
* tests;
* approved contracts;
* prompts;
* handovers;
* baselines needed for continuity;
* documentation required for recovery.

Use explicit path-based rules where broad wildcard rules could accidentally hide authoritative files.

Prefer safe and understandable rules.

---

# Phase 6 — Preserve Empty/Expected Directories

If runtime expects generated directories that will now be ignored, use a safe mechanism where necessary, e.g.:

`.gitkeep`

or create directories during runtime/tests.

Do not retain large generated content merely to keep directories present.

---

# Phase 7 — Recovery Documentation

Create:

`docs/PROJECT_RECOVERY.md`

This is a critical artifact.

A developer or AI on a completely new machine must be able to follow it.

Include:

## Prerequisites

* supported Python setup;
* dependency installation;
* external tools when applicable.

## Clone

Repository checkout procedure.

## Local configuration

Which files must be created locally and must not be committed.

Use template/example files where appropriate.

Never place credentials in the repository.

## Legacy source

Explain clearly that legacy source code is optional for V4 as a domain concept.

Also explain that specific V1/V2/V3 regeneration operations may require access to the historical legacy source.

Do not imply V4 HUMAN_INFORMATION_ONLY mode needs legacy source.

## Heavy historical artifacts

Explain which are excluded and why.

For each relevant artifact/group:

* whether it is required for ordinary development;
* whether it is required only to regenerate older results;
* where it should come from;
* command/process to recreate it when known.

## Verification

Document exact commands for:

* tests;
* readiness;
* repository health/recovery verification.

## Current state

Include pointers, not duplicated project knowledge, to:

* current handover;
* roadmap;
* baseline;
* latest approved round.

## Next step discovery

Explain how a new development agent determines the next task from repository state.

---

# Phase 8 — Recovery Manifest

Create:

`PROJECT_STATE.json`

or, if repository conventions suggest a better location:

`docs/PROJECT_STATE.json`

This must be SMALL and versioned.

It must contain machine-readable continuity information such as:

* project name;
* schema version;
* current major version;
* latest completed round;
* latest approved round;
* current test baseline;
* readiness state;
* AI knowledge allowed/generated flags;
* canonical baseline path;
* active handover path;
* active roadmap path;
* next task;
* recovery document path;
* generated artifact policy path;
* heavy artifacts included/excluded status.

Example semantics:

```text
project = LegacyMapper
current_version = V4
latest_approved_round = V4-R1
tests = 676
readiness = READY
ai_knowledge_generated = false
next = V4-R2
```

Do not make this file a duplicate knowledge base.

It is an index/pointer for continuity.

---

# Phase 9 — Agent Bootstrap Verification

Review `CLAUDE.md` and `AGENTS.md`.

Do not duplicate project knowledge into `CLAUDE.md`.

Ensure the bootstrap chain enables a new agent to discover at least:

```text
CLAUDE.md
   ↓
AGENTS.md
   ↓
PROJECT_STATE.json
   ↓
V4_AI_HANDOVER.md
   ↓
V4_PROPOSED_ROADMAP.md
   ↓
latest approved round result
```

If `CLAUDE.md` needs a small update to reference `PROJECT_STATE.json` or `PROJECT_RECOVERY.md`, that is allowed.

Keep it minimal and agent-neutral.

If `AGENTS.md` still contains historical Codex-centric wording that can safely be made agent-neutral without changing semantics, update only the generic wording.

Do not rename historical `codex/` directories.

---

# Phase 10 — Git Safety Scan

Before recommending initial commit:

Verify that tracked candidates do not contain obvious:

* passwords;
* API tokens;
* OAuth tokens;
* private keys;
* `.env` secrets;
* connection strings with credentials;
* private certificates;
* local user-specific absolute paths where they are inappropriate;
* credential caches.

Reuse existing security/sanitizer capabilities where appropriate.

Do not display discovered secret values in reports.

Report only:

* path;
* category;
* sanitized description;
* disposition.

If a probable real secret is found:

STOP publication readiness.

Do not delete it automatically unless clearly generated/local and safe to remove.

---

# Phase 11 — GitHub Suitability

Assess repository suitability for ordinary GitHub Git tracking.

Create:

`output/v4_r1_1/V4_GITHUB_SUITABILITY.json`

Record:

* total retained candidate size;
* count of retained files;
* largest retained file;
* files >= 50 MiB;
* files >= 100 MiB;
* LFS candidates;
* excluded generated data size;
* secret scan status;
* continuity status.

Goal:

* no normal Git tracked file >= 100 MiB;
* preferably no ordinary tracked artifact near that size;
* generated heavy data excluded;
* source/docs/tests remain complete.

Do not install or configure Git LFS automatically unless explicitly necessary and already available.

Prefer exclusion/regeneration over LFS for programmatically generated artifacts.

---

# Phase 12 — Git Initialization Readiness

Check whether repository is already a Git repository.

If not:

Do NOT create a remote.

Local `git init` may be performed only if safe and useful.

Do NOT:

* push;
* publish;
* create GitHub repository;
* add credentials;
* configure authentication;
* rewrite an existing Git history;
* run destructive Git cleanup.

The objective is to make the directory READY for versioning.

User will decide when/where to publish.

---

# Important Git History Rule

If the project is already in Git and large files were previously committed, adding them to `.gitignore` is not sufficient.

Detect this condition.

If present:

* report it clearly;
* calculate impact;
* propose a safe history-cleanup procedure;
* DO NOT rewrite history automatically.

---

# Do Not Delete Valuable Data

This round must distinguish:

EXCLUDED_FROM_GIT

from:

DELETE_FROM_DISK

They are NOT the same.

Heavy files may remain on the user's local machine while being ignored by Git.

Do not permanently delete historical or generated artifacts merely because they should not be versioned.

If cleanup would reclaim significant disk space, provide it as a separate optional recommendation.

---

# Tests and Regression

After repository/documentation changes run:

`python -m unittest discover -s tests`

Expected:

> =676 PASS

Also run the existing readiness command.

Expected:

READINESS=READY

AI_KNOWLEDGE_ALLOWED=true

AI_KNOWLEDGE_GENERATED=false

No provider call.

No real LLM call.

Repository optimization must not alter functional behavior.

---

# Recovery Simulation

Perform a deterministic continuity simulation without requiring actual network cloning.

Create a temporary clean view or equivalent verification of the FILES THAT WOULD BE VERSIONED.

Using only retained/versioned candidate files, verify that a new agent can locate:

* `AGENTS.md`;
* `CLAUDE.md`;
* `PROJECT_STATE.json`;
* `PROJECT_RECOVERY.md`;
* V4 handover;
* V4 roadmap;
* latest R1 result;
* V3 final baseline;
* tests;
* production source;
* next task.

Do not copy heavy ignored data merely for this simulation.

Record:

RECOVERY_SIMULATION=PASS/FAIL

---

# Required Result

Create:

`docs/V4/V4_R1_1_REPOSITORY_VERSIONING_RESULT.md`

It must report:

STATUS

ENTRY_GATE

BASELINE_TESTS

FINAL_TESTS

READINESS

REPOSITORY_SIZE_BEFORE

GIT_CANDIDATE_SIZE_AFTER

HEAVY_DATA_EXCLUDED_SIZE

FILES_OVER_50_MIB

FILES_OVER_100_MIB

GIT_LFS_REQUIRED

SECRET_SCAN

CONTINUITY_CONTRACT

PROJECT_STATE

PROJECT_RECOVERY

GITIGNORE

AGENT_BOOTSTRAP

RECOVERY_SIMULATION

V3_CONTINUITY

V4_CONTINUITY

PRODUCTION_BEHAVIOR_CHANGED

REAL_LLM_CALLS

PROVIDER_CALLS

AI_KNOWLEDGE_GENERATED

DECISION

NEXT

Also include:

## KEEP_IN_GIT

High-level categories.

## EXCLUDED_FROM_GIT

High-level categories and reasons.

## EXTERNAL_ARCHIVE_REQUIRED

Any non-regenerable data that cannot safely be dropped from continuity.

## OPTIONAL_LOCAL_CLEANUP

Disk-only cleanup suggestions.

Do not execute optional destructive cleanup.

---

# Expected Success State

```text
STATUS=V4_R1_1_REPOSITORY_VERSIONING_COMPLETE
ENTRY_GATE=PASS
TESTS>=676_PASS
READINESS=READY
CONTINUITY_CONTRACT=VALID
PROJECT_STATE=VALID
PROJECT_RECOVERY=VALID
GITIGNORE=VALID
SECRET_SCAN=PASS
AGENT_BOOTSTRAP=PASS
RECOVERY_SIMULATION=PASS
V3_CONTINUITY=PRESERVED
V4_CONTINUITY=PRESERVED
PRODUCTION_BEHAVIOR_CHANGED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
AI_KNOWLEDGE_GENERATED=false
DECISION=REPOSITORY_READY_FOR_GIT_VERSIONING
NEXT=HUMAN_REVIEW_V4_R1_1
```

If essential non-regenerable heavy artifacts cannot be safely excluded:

```text
DECISION=REPOSITORY_VERSIONING_BLOCKED_PENDING_EXTERNAL_ARCHIVE_DECISION
```

Do not hide that problem.

---

# Stop Condition

Stop after repository/versioning preparation.

Do not implement V4-R2.

Do not push to GitHub.

Do not create a remote repository.

Do not delete heavy local artifacts.

Wait for Technical Lead review.
