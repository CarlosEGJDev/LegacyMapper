# LegacyMapper — ACC-01 Remediation Checkpoint + STUB Rehearsal

## Owner approval

The owner approves the ACC-01 remediation result for checkpointing.

Current validated remediation state:

```text
OWNER_STANDALONE_ACCEPTANCE = READY_FOR_RETRY
H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
```

Validated:
```text
targeted remediation tests = 36 PASS
full suite = 3611 tests
failures = 0
errors = 0
skipped = 135
real provider calls during development = 0
```

Real acceptance baseline rehearsal planning:
```text
solutions = 91
projects = 228
documented = 184
machine-only = 9
unresolved/no-solution = 35
planned AI requests = 597
HTML pages = 602
validation defects = 0
```

## 1. Final remediation review

Run:
```bash
git status --short
git diff --stat
git diff
git ls-files --others --exclude-standard
```

Verify all changes belong to ACC-01 remediation:
```text
legacy_documenter/system/
CLI integration
schemas/contracts
resume/persistence logic
system projection
tests
docs/ACCEPTANCE/
PROJECT_STATE.json
resume/operations documentation
```

Reject unrelated changes.

## 2. Preserve historical state

Verify:
```text
H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
OWNER_STANDALONE_ACCEPTANCE = READY_FOR_RETRY
```

Do not rewrite H5/Post-V5 history.

## 3. Git checkpoint

Authorized:
```text
stage = YES
commit = YES
push = YES
tag = NO
```

Commit subject:
```text
Add full-system AI interpretation and resume support
```

Suggested body:
```text
- add hierarchical system/solution/project interpretation
- persist stable provider request identities
- resume without replaying completed AI calls
- add complete coverage manifest
- add integrated human and machine system projection
- add provider/account preflight safeguards
- add ACC-01 remediation tests and documentation
```

Do not amend the previous Post-V5 checkpoint.

Push normally:
```text
no force push
no new remote
no tag
```

Record:
```text
branch
commit SHA
commit subject
push result
git status --short
```

Expected working tree:
```text
clean
```

## 4. Build official remediation wheel

Do NOT use the pre-commit wheel:
```text
54180991…de98d
```

Build the official acceptance candidate from the exact committed remediation SHA.

Record:
```text
commit SHA
wheel filename
wheel size
wheel SHA-256
Python version
build command
```

Do not overwrite prior acceptance evidence.

## 5. Prepare retry runtime

Install the official wheel into a fresh acceptance venv/runtime.

Requirements:
```text
not editable
PYTHONPATH = empty
import path = site-packages
repository checkout not required
```

Reuse:
```text
C:\LegacyMapperAcceptance\output\baseline
```

Do NOT rerun IST analysis.

Confirm:
```text
baseline integrity unchanged
Evidence schema supported
UI schema supported
cross-project schema supported
new wheel can consume baseline
```

## 6. Copilot account preflight

The intended real acceptance account is:
```text
CarlosEGJDev
```

Do not hardcode it into product code.

Before any real provider call verify:
```text
/user
/usage
```

Required:
```text
provider account verified = YES
account = CarlosEGJDev
unexpected token override = NO
```

If account mismatches:
```text
STOP
real provider calls = 0
```

## 7. Full STUB rehearsal before spending quota

Run the complete acceptance interpretation/projection path against the real fresh baseline using:
```text
provider = STUB
```

Exercise:
```text
interpret-system
full hierarchy
complete inventory enumeration
coverage manifest
resume/persistence
project-system
human product generation
machine product generation
validation
```

Expected corpus:
```text
solutions = 91
projects = 228
```

No project may disappear silently.

## 8. Resume/replay proof

### Fresh STUB run
Expected:
```text
planned requests ≈ 597
all planned requests completed by STUB
coverage manifest complete
```

### Re-run with persisted state
Expected:
```text
new provider calls = 0
persisted replay = all previously completed requests
```

### Projection-only re-run
Expected:
```text
provider calls = 0
source reads = 0
scanner = 0
analyzer = 0
```

## 9. Validate product structure

Require:
```text
human/index.html exists
human system/solution/project navigation exists
IST complete PDF or documented indexed PDF set exists
ai system package exists
coverage manifest exists
internal provenance/state exists
```

Validation:
```text
broken links = 0
missing assets = 0
invalid JSON = 0
dangling IDs = 0
human provenance leaks = 0
invalid human states = 0
silent project omissions = 0
```

Normal human states only:
```text
Confirmado
Inferido
No resuelto
```

Do not expose normal-reader internals such as raw source paths, line numbers, internal Evidence ids, provider diagnostics, EP/FLOW/CALL/DAO ids.

## 10. Rehearsal report

Create:
```text
C:\LegacyMapperAcceptance\output\ACC01_STUB_REHEARSAL_RESULT.md
C:\LegacyMapperAcceptance\output\ACC01_STUB_REHEARSAL_EVIDENCE.json
```

Include:
```text
remediation commit SHA
official wheel SHA-256
baseline identity
solutions/projects
planned requests
completed requests
replayed requests
provider calls on second run
coverage states
HTML page count
PDF result
machine package result
validation metrics
source reads during interpretation/projection
scanner/analyzer counters
final STUB rehearsal verdict
```

## 11. READY_FOR_REAL_AI gate

Declare:
```text
READY_FOR_REAL_AI_ACCEPTANCE = YES
```

only if all pass:
```text
OFFICIAL_WHEEL_FROM_COMMIT = PASS
BASELINE_REUSE = PASS
FULL_SYSTEM_STUB_INTERPRETATION = PASS
COMPLETE_COVERAGE = PASS
RESUME_WITHOUT_REPLAY = PASS
SECOND_RUN_PROVIDER_CALLS = 0
HUMAN_PROJECTION = PASS
MACHINE_PROJECTION = PASS
BROKEN_LINKS = 0
INVALID_JSON = 0
DANGLING_IDS = 0
HUMAN_PROVENANCE_LEAKS = 0
SILENT_PROJECT_OMISSIONS = 0
DOWNSTREAM_SOURCE_READS = 0
BLOCKING_REHEARSAL_DEFECTS = 0
COPILOT_ACCOUNT_PREFLIGHT = PASS
```

If any fail:
```text
READY_FOR_REAL_AI_ACCEPTANCE = NO
```

Do not spend real provider quota.

## 12. Stop before real AI

Even if rehearsal passes:
```text
real provider full-system calls = NO
```

The owner will authorize the real acceptance separately.

## Final authority

```text
repository edits = only if needed to finalize documented remediation state
stage = YES
commit = YES
push = YES
tag = NO

build official wheel = YES
fresh acceptance runtime = YES
reuse fresh standalone baseline = YES
STUB full-system rehearsal = YES
STUB resume/replay verification = YES

real Copilot full-system interpretation = NO
fresh IST re-analysis = NO
V6 start = NO
```

> First prove orchestration, coverage, persistence and projection for free. Then spend real provider quota only once.
