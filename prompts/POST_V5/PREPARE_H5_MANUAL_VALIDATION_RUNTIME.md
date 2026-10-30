# LegacyMapper — Prepare Standalone Human Validation Runtime Before H4/H5 Closure

## Objective

Prepare a standalone LegacyMapper runtime for the human owner to execute manually, without Claude, from:

```text
C:\PruebasLegacyMapper\Resultados\h5_real_ist_validation\
```

This is **NOT H5 closure yet**.

Do not mark H4 closed.
Do not mark H5 closed.
Do not change product architecture.
Do not start V6.

The purpose is only to leave a ready-to-run LegacyMapper installation plus simple launch scripts so the human owner can execute the real IST validation himself and inspect the AI-interpreted outputs.

---

# 1. Target directory

Use exactly:

```text
C:\PruebasLegacyMapper\Resultados\h5_real_ist_validation\
```

Recommended layout:

```text
h5_real_ist_validation\
    runtime\
    venv\
    runs\
    scripts\
    README_RUN_ME.md
```

If a different internal layout is technically safer, keep the same top-level directory and document it clearly.

Do not depend on:

```text
C:\dev\LegacyMapper
Claude temp folders
current working directory
PYTHONPATH pointing to the development checkout
developer-only files
```

---

# 2. Install the current product build

Use the packaging support already validated in Gate A.1.

Preferred:

```text
build current wheel from the repository
create isolated venv inside the target directory
install the wheel into that venv
```

After installation, prove the runtime resolves from the installed package, not from the source checkout.

Test from an unrelated cwd.

The human owner must be able to run the prepared installation after Claude stops.

---

# 3. Do not perform the final human validation on behalf of the owner

Claude may perform only the minimal smoke checks needed to prove the prepared runtime launches.

Do not perform or approve the final H4/H5 validation.

The actual IST execution and human acceptance will be done manually by the owner afterward.

---

# 4. AI provider

The current intended provider for this validation is the existing Copilot-based provider already supported by LegacyMapper.

Inspect the **current repository implementation and CLI contract** and determine the exact provider identifier, configuration flags, executable discovery mechanism, and model selection currently supported.

Do not invent new provider flags.

Do not hardcode a developer-specific Copilot executable path.

Use this precedence:

```text
1. explicitly configured executable path if the existing product supports it
2. provider executable available through PATH
3. clear controlled error with instructions
```

If the product currently calls the provider `copilot-local`, preserve that exact existing identifier.

Do not require Claude to remain running.

The runtime must call Copilot directly through LegacyMapper.

---

# 5. Provider preflight script

Create:

```text
scripts\00_CHECK_ENVIRONMENT.cmd
```

It must verify, using the product's real contracts:

```text
Python/venv runtime exists
LegacyMapper launches
Copilot executable is discoverable/configured
required Copilot authentication/session prerequisite is available if the provider exposes a safe check
output directory is writable
```

Do not make an AI request just to test environment readiness unless the existing provider has no cheaper readiness mechanism.

The script must stop with a clear message if Copilot is unavailable.

---

# 6. Source path must be explicit

Do not bake an assumed IST path into production code.

Create:

```text
scripts\SET_PATHS.cmd
```

with one clearly editable line:

```bat
set "LEGACY_SOURCE=<PUT_REAL_IST_SOURCE_PATH_HERE>"
```

and:

```bat
set "LEGACY_RUN_ROOT=C:\PruebasLegacyMapper\Resultados\h5_real_ist_validation\runs\manual_validation"
```

If Claude knows the authoritative IST source path from existing repository/test documentation, it may prefill it, but it must still remain visibly configurable.

---

# 7. Manual execution scripts

Create simple Windows CMD scripts using the **actual current LegacyMapper CLI syntax** discovered from the repository.

Required scripts:

```text
scripts\01_ANALYZE_ONCE.cmd
scripts\02_INTERPRET_WITH_AI.cmd
scripts\03_GENERATE_DOCS.cmd
scripts\04_GENERATE_VISUALS.cmd
scripts\05_GENERATE_HUMAN_DELIVERABLES.cmd
scripts\06_GENERATE_EXECUTIVE_TEMPLATE.cmd
scripts\RUN_ALL.cmd
```

Important:

```text
01_ANALYZE_ONCE
```

must perform the fresh analyzer-v4 deterministic run required by the current product state.

After it succeeds:

```text
02–06
```

must reuse persisted output and must not rescan/reanalyze source.

`RUN_ALL.cmd` must simply orchestrate the same commands in order and stop immediately if any step fails.

---

# 8. Run folders

Use distinct locations:

```text
runs\manual_validation\baseline\
runs\manual_validation\ai\
runs\manual_validation\human_default\
runs\manual_validation\human_executive\
```

or the current product's required equivalent.

Avoid overwriting evidence accidentally.

Document exactly which folder is passed to `interpret`, `docs`, `visuals`, and `deliver`.

---

# 9. AI interpretation

`02_INTERPRET_WITH_AI.cmd` must:

```text
consume the persisted analyzer-v4 output
use the configured Copilot provider
perform real AI interpretation
not rescan source
not rebuild deterministic Evidence
```

Use the actual current model/provider defaults or explicit supported flags.

If a model is required, document the exact model selected.

Do not silently fall back to fake AI.

Do not accept a missing provider as success.

---

# 10. Human deliverables

Generate both current human templates:

```text
human/default
human/executive
```

The human owner primarily wants to inspect:

```text
AI explanations
view behavior
cross-project technical routes
data/stored procedure routes
wireframes
SVG flows
HTML
PDF
UNRESOLVED areas
```

Do not auto-approve AI interpretations.

---

# 11. README for the owner

Create:

```text
C:\PruebasLegacyMapper\Resultados\h5_real_ist_validation\README_RUN_ME.md
```

It must be written for a non-developer operator and contain:

```text
1. where to edit the IST source path
2. how to run environment check
3. how to run everything automatically
4. how to run each step separately
5. where the final HTML/PDF are located
6. where AI explanations JSON is located
7. how to recognize a provider/authentication error
8. how to rerun presentation only without rescanning
9. warning that 01_ANALYZE_ONCE should not be rerun just to adjust documents
```

Keep it short and operational.

---

# 12. Generate a convenient launcher

Create at the top level:

```text
RUN_LEGACYMAPPER.cmd
```

Behavior:

```text
call scripts\00_CHECK_ENVIRONMENT.cmd
call scripts\RUN_ALL.cmd
pause at the end
```

It must show clear progress:

```text
[1/6] Analyze once
[2/6] AI interpretation
[3/6] Human docs
[4/6] Visuals
[5/6] Default human deliverable
[6/6] Executive human deliverable
```

Stop on first non-zero exit code.

---

# 13. Logs

Each step must preserve stdout/stderr under:

```text
runs\manual_validation\logs\
```

Suggested:

```text
01_analyze.log
02_interpret.log
03_docs.log
04_visuals.log
05_default.log
06_executive.log
```

Do not hide failures.

---

# 14. Expected review package

At the end of a successful manual run, make it easy for the owner to send these files for review:

```text
AI_INTERPRETATION_MANIFEST.json
explanations.json
validation_report.json
usage_summary.json
representative flow SVGs
default HTML
default PDF
executive HTML
executive PDF
run logs
PROJECT_STATE.json or copied validation-state snapshot
```

Create:

```text
runs\manual_validation\REVIEW_FILES.txt
```

containing the actual generated relative paths after the run.

---

# 15. Safety / state

Do not automatically:

```text
approve H4
close H4
start/close H5
canonicalize AI content
commit
push
tag
```

Current state remains:

```text
H4 = awaiting human final approval
H5 = NOT_STARTED
PRE_H5_GATE_A = PASS
PRE_H5_GATE_A1 = PASS
PRE_H5_GATE_B = PASS
PRE_H5_GATE_B1 = PASS
PRE_H5_GATE_C = PASS
PRE_H5_BLOCKING_DEBT = 0
```

---

# 16. Testing policy

Do not run the whole 3,454-test suite again merely to prepare this runtime.

Use only targeted packaging/runtime smoke tests required to prove:

```text
wheel installs
entry point works
templates are present
scripts use valid current CLI syntax
provider preflight is correct
```

No full IST analysis by Claude unless strictly necessary to validate the launcher syntax.

The human owner will perform the real run.

---

# 17. Git authority

For this preparation task:

```text
edit helper scripts/docs outside repo = YES
build wheel = YES
install local isolated runtime = YES
production-code changes = NO unless an actual blocker is discovered
tests = targeted only
commit = NO
push = NO
tag = NO
```

If an actual product defect prevents standalone execution, stop and report it before altering architecture.

---

# 18. Completion report

Create:

```text
C:\PruebasLegacyMapper\Resultados\h5_real_ist_validation\PREPARED_RUNTIME_REPORT.md
```

Report:

```text
wheel/build used
installed version
Python version
entry point
provider identifier
provider/model configuration
Copilot discovery method
target directory
smoke checks
exact scripts created
exact command behind each script
whether a real AI call was made during preparation
known prerequisites for the owner
```

Final state should be:

```text
H5_MANUAL_VALIDATION_RUNTIME_READY
```

This is an operational readiness state only, not H4/H5 closure.

Final principle:

> The owner must be able to close Claude, open a normal Windows terminal, run `RUN_LEGACYMAPPER.cmd`, and have LegacyMapper analyze once, invoke its configured Copilot AI provider, and generate the current human deliverables by itself.
