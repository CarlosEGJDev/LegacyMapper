# LegacyMapper V4 — R2 Human Approval, Closure and Versioning

TASK=V4_R2_APPROVAL_AND_VERSIONING

MODE=HUMAN_APPROVAL_REGISTRATION_AND_VERSIONING

IMPLEMENTATION_ALLOWED=false

GIT_COMMIT_ALLOWED=true

GIT_PUSH_ALLOWED=true

REAL_LLM_CALLS_ALLOWED=false

PROVIDER_CALLS_ALLOWED=false

---

# Human Authorization

The Technical Lead has explicitly reviewed and APPROVED:

`V4-R2 — Input / Source Contracts`

This approval was issued outside the development agent and is authoritative for this closure task.

The development agent MUST NOT reinterpret, re-evaluate, or independently grant this approval.

Its responsibility is only to:

1. record the Technical Lead's approval;
2. verify the approved state remains valid;
3. update repository continuity state;
4. create the Git checkpoint;
5. push the checkpoint to the already configured repository.

---

# Important Existing Git State

The Technical Lead has already manually created a Git commit after the V4-R2 implementation.

Do NOT treat that as an error.

Do NOT rewrite, squash, amend, reset, rebase, or delete that commit.

This task must create a NEW closure/versioning commit containing any remaining approval/state/versioning changes required by this prompt.

If there are no repository changes after recording the approval state, do not create an artificial empty commit unless required to represent the explicit approval checkpoint.

In that case, an empty commit MAY be created specifically as the formal V4-R2 approval checkpoint.

---

# Required Reading

Read:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `PROJECT_STATE.json`
4. `docs/PROJECT_RECOVERY.md`
5. `docs/V4/V4_AI_HANDOVER.md`
6. `docs/V4/V4_PROPOSED_ROADMAP.md`
7. `docs/V4/V4_R2_INPUT_SOURCE_CONTRACTS_RESULT.md`
8. `output/v4_r2/V4_INPUT_SOURCE_CONTRACTS.json`
9. `docs/V4/V4_REPOSITORY_CONTINUITY_CONTRACT.md`

Inspect:

```text
git status
git log --oneline -5
git remote -v
```

Do not modify the configured remote.

---

# Preconditions

Verify:

```text
V4_R2_IMPLEMENTATION=COMPLETE
V4_R2_DECISION=V4_R2_READY_FOR_HUMAN_REVIEW
TESTS>=726_PASS
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
```

Also verify the R2 contract artifact exists:

`output/v4_r2/V4_INPUT_SOURCE_CONTRACTS.json`

Expected SHA-256 from the reviewed R2 result:

```text
60144e2c67e96c66f708157885607fd07bbeb4087cac81f9049d7019612a0ef7
```

If the artifact hash differs unexpectedly:

STOP.

Do not approve, commit, or push until the discrepancy is explained.

---

# Register Human Approval

Update the repository's authoritative state so that:

```text
latest_completed_round = V4-R2
latest_approved_round = V4-R2
next = V4-R3
```

Preserve the existing `PROJECT_STATE.json` schema and conventions.

Do not redesign it.

If the state model contains an appropriate field for approval status, update it consistently.

The repository must clearly communicate:

```text
V4_R2=APPROVED
NEXT=V4-R3
```

A new development agent with no conversation history must be able to determine this solely from repository artifacts.

---

# R2 Result Closure

Update:

`docs/V4/V4_R2_INPUT_SOURCE_CONTRACTS_RESULT.md`

only if necessary to record the externally supplied Technical Lead approval.

Do NOT rewrite the implementation result.

Do NOT alter historical test numbers, hashes, decisions, or implementation findings.

Prefer a small explicit closure section such as:

```text
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD
ROUND_STATUS=APPROVED
NEXT=V4-R3
```

Do not invent the Technical Lead's personal name or approval timestamp unless the repository already has a deterministic convention for it.

---

# Regression Validation

Run:

```text
python -m unittest discover -s tests
```

Expected:

```text
>=726 PASS
```

Then:

```text
python -m legacy_documenter.knowledge.readiness
```

Expected:

```text
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
PROVIDER_CALLS=0
REAL_LLM_CALLS=0
```

No R2 implementation change is authorized during this task.

If tests or readiness fail:

STOP.

Do not commit or push a broken closure state.

---

# Git Safety Check

Before staging:

```text
git status
```

Verify that:

* no ignored heavy generated directories are being introduced;
* no credentials/secrets are present;
* no unexpected local-machine files are present;
* no unrelated destructive change is included.

Respect the existing `.gitignore` and repository continuity contract.

Do NOT use:

```text
git reset --hard
git clean -fd
git rebase
git commit --amend
git push --force
```

Do not rewrite history.

---

# Commit

Stage only the files belonging to this approved closure/versioning checkpoint.

Expected files may include:

* `PROJECT_STATE.json`
* `docs/V4/V4_R2_INPUT_SOURCE_CONTRACTS_RESULT.md`
* this approval/versioning prompt
* other small continuity artifacts only if legitimately required by the repository contract.

Before committing, inspect:

```text
git diff --cached
```

Confirm the staged changes contain no unrelated modifications.

Create a new commit.

Preferred commit message:

```text
Approve and close LegacyMapper V4-R2
```

If the Technical Lead's previous manual commit already contains all R2 implementation files, preserve it unchanged.

This new commit represents the explicit human-approval checkpoint.

---

# Push

Use the existing configured branch and remote.

Do NOT create or modify remote configuration.

Push normally.

Expected conceptually:

```text
git push origin main
```

Use the actual current branch if it differs from `main`.

No force push.

If authentication requires explicit human interaction, STOP and report the exact action required instead of attempting to bypass authentication.

---

# Post-Push Verification

After push, verify:

```text
git status
git log --oneline -5
```

Expected:

* working tree clean, except explicitly documented local-only/ignored artifacts;
* R2 approval commit present;
* current local branch synchronized with the configured upstream;
* `PROJECT_STATE.json` identifies V4-R2 as approved;
* next round is V4-R3.

Do NOT start V4-R3.

---

# Required Closure Result

Create:

`docs/V4/V4_R2_CLOSURE_AND_VERSIONING_RESULT.md`

This result itself must be included in the closure commit.

Report:

```text
STATUS
HUMAN_REVIEW
APPROVAL_AUTHORITY
R2_CONTRACT_SHA256
TESTS
READINESS
AI_KNOWLEDGE_ALLOWED
AI_KNOWLEDGE_GENERATED
REAL_LLM_CALLS
PROVIDER_CALLS
PROJECT_STATE
PREVIOUS_MANUAL_COMMIT_PRESERVED
GIT_STATUS_BEFORE
GIT_COMMIT
GIT_PUSH
GIT_STATUS_AFTER
REPOSITORY_CONTINUITY
ROUND_STATUS
DECISION
NEXT
```

Expected success state:

```text
STATUS=V4_R2_CLOSURE_AND_VERSIONING_COMPLETE
HUMAN_REVIEW=APPROVED
APPROVAL_AUTHORITY=TECHNICAL_LEAD
R2_CONTRACT_SHA256=60144e2c67e96c66f708157885607fd07bbeb4087cac81f9049d7019612a0ef7
TESTS>=726_PASS
READINESS=READY
AI_KNOWLEDGE_ALLOWED=true
AI_KNOWLEDGE_GENERATED=false
REAL_LLM_CALLS=0
PROVIDER_CALLS=0
PROJECT_STATE=V4_R2_APPROVED
PREVIOUS_MANUAL_COMMIT_PRESERVED=true
GIT_COMMIT=PASS
GIT_PUSH=PASS
REPOSITORY_CONTINUITY=PASS
ROUND_STATUS=APPROVED
DECISION=V4_R2_FORMALLY_CLOSED_AND_VERSIONED
NEXT=V4-R3
```

---

# Future Versioning Rule

From this checkpoint onward, use the following lifecycle for every V4 round:

```text
IMPLEMENT ROUND
      ↓
VALIDATE
      ↓
READY_FOR_HUMAN_REVIEW
      ↓
STOP
      ↓
TECHNICAL LEAD REVIEW
      ↓
APPROVED
      ↓
CLOSURE + PROJECT_STATE UPDATE
      ↓
TESTS / READINESS
      ↓
GIT COMMIT
      ↓
GIT PUSH
      ↓
NEXT ROUND
```

The development agent MUST NEVER convert:

```text
READY_FOR_HUMAN_REVIEW
```

into:

```text
APPROVED
```

without explicit Technical Lead authorization.

The development agent may perform Git commit/push after that explicit authorization.

This rule applies to:

* Claude;
* Codex;
* any future development agent.

The repository remains the authoritative continuity mechanism.

---

# Stop Condition

STOP after successful V4-R2 closure, commit, push, and post-push verification.

Do NOT implement V4-R3.

Wait for the Technical Lead to authorize the next round.
