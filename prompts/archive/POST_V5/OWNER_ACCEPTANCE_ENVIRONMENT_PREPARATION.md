# LegacyMapper — Owner Standalone Acceptance Environment Preparation

## Objective

Prepare a completely independent acceptance environment for the owner's full standalone IST validation.

This task prepares the environment only.

Do NOT start the full IST deterministic analysis.
Do NOT start full-system AI interpretation.
Do NOT modify production code.
Do NOT create a tag.

The next step, only after this preparation reports READY, will be:

```text
LEGACYMAPPER_OWNER_FULL_IST_STANDALONE_ACCEPTANCE.md
```

---

# 1. Authoritative release candidate

The exact repository commit to validate is:

```text
d509f45f9de5498038dc727a045218d04c2aca54
```

Expected commit subject:

```text
Finalize Post-V5 and repository hygiene
```

Expected branch/upstream:

```text
main
origin/main
```

Verify:

```bash
git status --short
git branch --show-current
git rev-parse HEAD
git log -1 --oneline
git status -sb
```

Required:

```text
HEAD = d509f45f9de5498038dc727a045218d04c2aca54
branch = main
working tree = clean
main synchronized with origin/main
```

If HEAD is different:

```text
STOP
do not build acceptance wheel
report mismatch
```

Do not checkout another commit silently.

---

# 2. Do not use historical workspace state

The owner acceptance must not reuse:

```text
C:\PruebasLegacyMapper\Current\state\baseline
C:\PruebasLegacyMapper\Current\state\ai
C:\PruebasLegacyMapper\H5_Validation
historical H4/H5 run outputs
old provider-response caches
```

Do not copy them into the acceptance environment.

They may remain on disk, but acceptance must be independent of them.

---

# 3. Acceptance root

Prepare a new clean root:

```text
C:\LegacyMapperAcceptance\
```

If it already exists from an earlier attempt, do NOT reuse it blindly.

Either:

```text
rename/archive previous attempt
```

or:

```text
delete only after verifying it is an old acceptance workspace
```

Target structure:

```text
C:\LegacyMapperAcceptance\
    runtime\
        wheel\
    venv\
    work\
    output\
    logs\
    scripts\
    ACCEPTANCE_ENVIRONMENT.md
```

Do not place the repository inside this directory.

---

# 4. Build wheel from exact Git commit

Build the wheel from the exact current repository tree at:

```text
d509f45f9de5498038dc727a045218d04c2aca54
```

Use the repository's normal build mechanism.

Expected artifact location:

```text
C:\LegacyMapperAcceptance\runtime\wheel\
```

There must be exactly one wheel selected as the acceptance candidate.

Record:

```text
wheel filename
wheel size
wheel SHA-256
build command
build timestamp
source commit SHA
```

Do not use an older wheel from:

```text
C:\PruebasLegacyMapper\
dist\
previous FinalValidation\
```

---

# 5. Create clean virtual environment

Create:

```text
C:\LegacyMapperAcceptance\venv\
```

Use the supported/current Python interpreter.

Record:

```text
python --version
python executable path
pip version
```

Install only what is required for standalone operation.

Install LegacyMapper from the newly built wheel, not editable mode.

Forbidden:

```text
pip install -e .
PYTHONPATH pointing to repository
import from C:\dev\LegacyMapper
```

---

# 6. Prove import isolation

From an unrelated working directory, for example:

```text
C:\Windows
```

or another neutral directory, verify:

```powershell
C:\LegacyMapperAcceptance\venv\Scripts\python.exe -c "import legacy_documenter, pathlib; print(pathlib.Path(legacy_documenter.__file__).resolve())"
```

Required import path:

```text
C:\LegacyMapperAcceptance\venv\Lib\site-packages\...
```

Forbidden import path:

```text
C:\dev\LegacyMapper\...
```

Also verify:

```powershell
$env:PYTHONPATH
```

Expected:

```text
empty / unset
```

If not empty, clear it for the acceptance environment and document the original state.

---

# 7. Verify CLI installation

From an unrelated working directory, verify the installed CLI and module entry point.

Examples:

```powershell
C:\LegacyMapperAcceptance\venv\Scripts\legacymapper.exe --help
C:\LegacyMapperAcceptance\venv\Scripts\python.exe -m legacy_documenter --help
```

Required:

```text
both entry points execute successfully
templates/package resources load
no repository checkout required
```

Do not run full analysis yet.

---

# 8. Provider dependencies

Install/verify the provider dependency required by the configured `copilot-local` provider.

Record versions such as:

```text
github-copilot-sdk
Copilot CLI
```

Do not install unrelated development dependencies unless required by the standalone runtime.

---

# 9. Verify Copilot account manually

Before any acceptance provider call, verify the intended GitHub Copilot account.

Use Copilot CLI:

```text
/user
/user list
/usage
```

Record only:

```text
GitHub username/account identity
quota/usage status at high level
```

Do not record secrets.

If the intended account is not active, switch/login before proceeding.

---

# 10. Check environment token overrides

Inspect:

```powershell
$env:COPILOT_GITHUB_TOKEN
$env:GH_TOKEN
$env:GITHUB_TOKEN
```

Do NOT print token values into reports.

Record only:

```text
SET / NOT_SET
```

If one is set unexpectedly and could override the intended Copilot account:

```text
STOP
report the condition
do not start acceptance
```

Do not delete user-level credentials permanently without owner instruction.

For the acceptance shell/session, ensure authentication resolves to the intended account.

---

# 11. Verify model/provider discovery

Perform only a lightweight provider discovery check.

Allowed:

```text
provider availability
model listing
authentication check
```

Do NOT send a full interpretation request.

Record:

```text
provider id
available model(s)
selected/default model behavior
```

If LegacyMapper uses an empty model setting to select the provider's current default, document that behavior.

Do not hardcode an old historical model if the provider no longer offers it.

---

# 12. Clean acceptance configuration

Create a dedicated acceptance configuration/script set under:

```text
C:\LegacyMapperAcceptance\scripts\
```

Use placeholders/variables for:

```text
SOURCE_ROOT
WORK_ROOT
OUTPUT_ROOT
PROVIDER
MODEL
```

For this owner run, expected source is:

```text
C:\Users\cgalianj\source\IST\Operacional
```

Expected generated roots:

```text
WORK_ROOT   = C:\LegacyMapperAcceptance\work
OUTPUT_ROOT = C:\LegacyMapperAcceptance\output
```

Do not reference:

```text
C:\PruebasLegacyMapper
C:\dev\LegacyMapper
```

from operational acceptance scripts.

---

# 13. Prepare owner-friendly launcher

Create:

```text
C:\LegacyMapperAcceptance\RUN_ACCEPTANCE.cmd
```

and, if helpful:

```text
C:\LegacyMapperAcceptance\CHECK_ENVIRONMENT.cmd
C:\LegacyMapperAcceptance\SET_PATHS.cmd
```

The launcher must be understandable to the owner.

It should NOT start automatically during this preparation task.

It should be prepared to invoke the later full acceptance workflow.

Use UTF-8-safe Python invocation where appropriate.

---

# 14. No historical baseline or AI cache reuse

Before declaring READY, verify acceptance directories do not contain copied data from:

```text
C:\PruebasLegacyMapper\Current\
C:\PruebasLegacyMapper\H5_Validation\
```

Required:

```text
old baseline reused = NO
old AI responses reused = NO
```

Acceptance `work\` and `output\` should initially be empty except for configuration/readme files.

---

# 15. Minimal smoke test only

Run a lightweight smoke test that does NOT analyze real IST.

Allowed:

```text
--help
version
small synthetic fixture
template/resource loading
provider availability without full interpretation
```

Do not execute:

```text
full IST scan
full deterministic analysis
project sweep
real AI interpretation
documentation generation over IST
```

---

# 16. Create acceptance environment receipt

Create:

```text
C:\LegacyMapperAcceptance\ACCEPTANCE_ENVIRONMENT.md
```

Include:

```text
READY_FOR_OWNER_ACCEPTANCE = YES/NO

commit SHA
commit subject
branch
upstream status

wheel path
wheel filename
wheel SHA-256

Python version
Python executable
venv path
LegacyMapper import path

PYTHONPATH set = YES/NO
repository import dependency = YES/NO

provider id
Copilot CLI version
provider SDK version
Copilot account verified = YES/NO
token overrides = SET/NOT_SET (names only, never values)
model discovery result

SOURCE_ROOT
WORK_ROOT
OUTPUT_ROOT

old H5 baseline reused = NO
old AI responses reused = NO

smoke test result
blocking preparation issues
```

---

# 17. READY gate

Only declare:

```text
READY_FOR_OWNER_ACCEPTANCE = YES
```

if all are true:

```text
COMMIT_MATCH = PASS
WORKING_TREE_CLEAN = PASS
WHEEL_BUILT_FROM_EXACT_SHA = PASS
WHEEL_SHA256_RECORDED = PASS
CLEAN_VENV = PASS
NO_PYTHONPATH = PASS
IMPORT_FROM_SITE_PACKAGES = PASS
CLI_FROM_UNRELATED_CWD = PASS
NO_HISTORICAL_BASELINE_REUSE = PASS
NO_HISTORICAL_AI_REUSE = PASS
COPILOT_ACCOUNT_VERIFIED = PASS
NO_UNEXPECTED_TOKEN_OVERRIDE = PASS
PROVIDER_DISCOVERY = PASS
SMOKE_TEST = PASS
```

If any fail:

```text
READY_FOR_OWNER_ACCEPTANCE = NO
```

Report the blocker and stop.

---

# 18. Do not start full acceptance

Even if preparation passes, do NOT run the full IST analysis in this prompt.

Final state must be:

```text
POST_V5 = CLOSED
V6 = NOT_STARTED
OWNER_STANDALONE_ACCEPTANCE = NOT_STARTED
READY_FOR_OWNER_ACCEPTANCE = YES
```

The owner will then execute:

```text
LEGACYMAPPER_OWNER_FULL_IST_STANDALONE_ACCEPTANCE.md
```

---

# Git authority

```text
repository edits = NO
commit = NO
push = NO
tag = NO

external acceptance workspace creation = YES
wheel build = YES
venv creation = YES
runtime dependency installation = YES
acceptance scripts = YES
provider/account discovery = YES

real IST analysis = NO
real full AI interpretation = NO
```

---

# Final principle

> **Preparation proves the acceptance environment is independent. The next prompt proves the product itself.**
