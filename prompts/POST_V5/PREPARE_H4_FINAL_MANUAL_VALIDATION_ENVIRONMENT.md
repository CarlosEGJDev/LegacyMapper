# LegacyMapper Post-V5 — Prepare Final Manual Validation Environment for H4

## Objective

Prepare a **fresh standalone LegacyMapper manual validation environment** for the owner to execute without Claude.

This environment is for the **final H4 manual validation** after the latest human catalog/wireframe polish.

Do not close H4.
Do not start H5.
Do not start V6.

The goal is:

> The owner can close Claude, open a normal Windows terminal, run LegacyMapper by himself, and inspect the final generated `human / ai / internal` knowledge package.

---

# 1. Target directory

Create the environment under exactly:

```text
C:\PruebasLegacyMapper\FinalValidation\
```

Recommended layout:

```text
C:\PruebasLegacyMapper\FinalValidation\
    runtime\
    venv\
    scripts\
    runs\
    README_RUN_ME.md
    RUN_LEGACYMAPPER.cmd
```

The runtime must not depend on:

```text
C:\dev\LegacyMapper
PYTHONPATH to development checkout
Claude temp folders
current working directory
developer-only assets
```

---

# 2. Install the current final product build

Use the current repository state after:

```text
H4_FINAL_HUMAN_CATALOG_AND_WIREFRAME_MICRO_POLISH
```

Build the current wheel.

Create an isolated virtual environment inside:

```text
C:\PruebasLegacyMapper\FinalValidation\venv
```

Install the wheel there.

Verify the installed package is the one being executed, not the source checkout.

Test from an unrelated current working directory.

---

# 3. Validation target

This final H4 manual run continues to use the representative target:

```text
LEGACY_SOURCE=C:\Users\cgalianj\source\IST\Operacional
LEGACY_PROJECT=WebPREPrevencion
LEGACY_SOLUTION=slnPREPrevencion_2010
```

Do not convert this into a product limitation.

This is only the final H4 representative manual validation.

H5 will later validate the complete IST solution/project set separately.

---

# 4. Final output contract

The final public package must use the current productized structure:

```text
package\
    KNOWLEDGE_PACKAGE.json
    human\
    ai\
    internal\
```

The owner should primarily inspect:

```text
human\index.html
human\LegacyMapper.pdf
human\executive.pdf
ai\knowledge.json
KNOWLEDGE_PACKAGE.json
```

Internal artifacts may exist under:

```text
internal\
```

but should not be the main user-facing experience.

---

# 5. Path configuration

Create:

```text
scripts\SET_PATHS.cmd
```

with clearly editable values:

```bat
@echo off

set "LEGACY_SOURCE=C:\Users\cgalianj\source\IST\Operacional"
set "LEGACY_PROJECT=WebPREPrevencion"
set "LEGACY_SOLUTION=slnPREPrevencion_2010"

set "LEGACY_RUN_ROOT=C:\PruebasLegacyMapper\FinalValidation\runs\manual_final"
```

Use a short enough output path to avoid the Windows path-length issue already observed previously.

Do not hardcode paths into production code.

---

# 6. AI provider

Use the existing LegacyMapper provider:

```text
provider_id = copilot-local
model_id = gpt-6-luna
```

unless the current repository contract requires the exact model identifier to be resolved differently.

LegacyMapper must invoke Copilot directly.

Claude must not be required during the run.

Do not hardcode a developer-specific Copilot executable path.

Use existing discovery behavior:

```text
1. explicit configured executable if supported
2. PATH discovery
3. controlled provider unavailable error
```

---

# 7. Environment preflight

Create:

```text
scripts\00_CHECK_ENVIRONMENT.cmd
```

It must verify:

```text
venv Python exists
LegacyMapper executable/module launches
installed package resolves outside source checkout
Copilot executable/provider is available
configured model is usable according to current provider contract
output root is writable
source path exists
project/solution values are present
```

Do not make a real provider request just for preflight unless current provider architecture makes it unavoidable.

The script must fail clearly on any missing prerequisite.

---

# 8. Manual execution scripts

Create:

```text
scripts\01_ANALYZE_ONCE.cmd
scripts\02_INTERPRET_WITH_AI.cmd
scripts\03_GENERATE_HUMAN_KNOWLEDGE.cmd
scripts\04_GENERATE_AI_KNOWLEDGE.cmd
scripts\05_PACKAGE_FINAL_OUTPUT.cmd
scripts\06_COLLECT_REVIEW_FILES.cmd
scripts\RUN_ALL.cmd
```

Use the **actual current CLI syntax from the repository**.

Do not invent flags.

---

# 9. Step 01 — Analyze once

`01_ANALYZE_ONCE.cmd` must:

```text
analyze the real IST source deterministically
create a fresh persisted baseline
perform scanner/analyzer exactly once
use no AI
```

This is the only step allowed to read the source tree for deterministic analysis.

If the current CLI's `full` command also runs documentation stages, use the safest current supported command sequence that guarantees a valid persisted baseline.

Do not silently accept PARTIAL if deterministic Evidence is incomplete.

Log:

```text
scanner count
analyzer count
file count
result state
output path
```

---

# 10. Step 02 — Interpret with real AI

`02_INTERPRET_WITH_AI.cmd` must:

```text
consume the persisted baseline
use copilot-local
use gpt-6-luna
perform the current final AI interpretation
use the final concise explanatory prompt style
not rerun scanner/analyzer
not reread source
```

It must fail if the provider is unavailable.

No fake provider fallback.

Persist the AI interpretation for downstream reuse.

---

# 11. Step 03 — Generate human knowledge

`03_GENERATE_HUMAN_KNOWLEDGE.cmd` must:

```text
reuse persisted Evidence
reuse persisted AI interpretation
generate the final human documentation
generate HTML
generate LegacyMapper.pdf
generate executive.pdf
generate diagrams/wireframes
not call AI again
not read source again
```

The final human content must include the latest polish:

```text
simple explanatory AI prose
known behavior first
uncertainty grouped
4-column descriptive catalog
no low-value coverage metrics in PDF
horizontal readable wireframe labels
```

---

# 12. Step 04 — Generate AI knowledge

`04_GENERATE_AI_KNOWLEDGE.cmd` must generate/reuse:

```text
ai\knowledge.json
```

and the current supported AI projections, preserving:

```text
architecture
projects
views
flows
dependencies
data
unresolved
provenance
human-confirmed knowledge capability
```

No new provider call just because the machine projection is generated.

---

# 13. Step 05 — Package final output

`05_PACKAGE_FINAL_OUTPUT.cmd` must assemble:

```text
package\
    KNOWLEDGE_PACKAGE.json
    human\
    ai\
    internal\
```

The public contract must not expose the old pipeline-oriented folder structure as the main user experience.

Legacy folders may remain under `internal` or as compatibility artifacts if required, but the final documented output is:

```text
human
ai
internal
```

---

# 14. Step 06 — Collect review files

Create:

```text
scripts\06_COLLECT_REVIEW_FILES.cmd
```

It must create:

```text
runs\manual_final\REVIEW_FILES.txt
```

listing the actual generated paths for:

```text
package\KNOWLEDGE_PACKAGE.json
package\human\index.html
package\human\LegacyMapper.pdf
package\human\executive.pdf
package\ai\knowledge.json
package\ai\unresolved.json
AI_INTERPRETATION_MANIFEST.json
validation_report.json
relevant run logs
```

Use only files that actually exist.

---

# 15. RUN_ALL

Create:

```text
scripts\RUN_ALL.cmd
```

It must show:

```text
[1/6] Analyze once
[2/6] Interpret with Copilot
[3/6] Generate human knowledge
[4/6] Generate AI knowledge
[5/6] Package final output
[6/6] Collect review files
```

Stop immediately on first non-zero exit code.

Do not continue after a failed step.

---

# 16. Top-level launcher

Create:

```text
C:\PruebasLegacyMapper\FinalValidation\RUN_LEGACYMAPPER.cmd
```

Behavior:

```bat
call scripts\00_CHECK_ENVIRONMENT.cmd
if errorlevel 1 exit /b %errorlevel%

call scripts\RUN_ALL.cmd
if errorlevel 1 exit /b %errorlevel%

pause
```

The owner should be able to use either:

```text
double-click RUN_LEGACYMAPPER.cmd
```

or:

```bat
cd /d C:\PruebasLegacyMapper\FinalValidation
RUN_LEGACYMAPPER.cmd
```

---

# 17. Logs

Write logs under:

```text
C:\PruebasLegacyMapper\FinalValidation\runs\manual_final\logs\
```

Suggested:

```text
00_environment.log
01_analyze.log
02_interpret.log
03_human.log
04_ai_knowledge.log
05_package.log
06_review_files.log
```

Do not hide stderr.

---

# 18. README for owner

Create:

```text
C:\PruebasLegacyMapper\FinalValidation\README_RUN_ME.md
```

Keep it short and operational.

Explain:

```text
1. where paths are configured
2. how to check environment
3. how to run everything
4. how to run steps individually
5. where human documentation is
6. where AI knowledge is
7. where logs are
8. what to do if Copilot/authentication fails
9. that 01_ANALYZE_ONCE should not be rerun just to regenerate presentation
10. that human presentation steps must reuse persisted Evidence/AI
```

---

# 19. Manual-run review objective

This environment exists so the owner can answer:

```text
Does LegacyMapper run without Claude?
Does it analyze IST successfully?
Does Copilot interpretation run successfully?
Is the human output understandable?
Are the PDFs useful?
Are the wireframes readable?
Is the AI package structured and useful?
Is the final folder structure understandable?
```

Do not answer those questions on behalf of the owner.

---

# 20. Preparation smoke checks only

Claude may perform only the minimum smoke checks required to prove:

```text
wheel builds
venv installs
entry point works
scripts invoke valid current CLI commands
preflight behaves correctly
package templates/resources are available
```

Do not perform the owner's final real run unless strictly required to detect a script/runtime blocker.

If a real run is required only for validating script correctness, stop and report before doing a full expensive IST run.

---

# 21. Testing policy

Do not rerun the entire test suite merely to prepare this environment if the current repository state already has the final green suite:

```text
3500 tests
0 failures
0 errors
132 skips
```

Use targeted packaging/runtime smoke tests only.

Do not rerun scanner/analyzer during environment preparation.

---

# 22. Preserve current state

Do not automatically:

```text
close H4
approve AI as canonical
start H5
close H5
commit
push
tag
```

Current state remains:

```text
H4_FINAL_HUMAN_CATALOG_AND_WIREFRAME_MICRO_POLISH = READY_FOR_FINAL_MANUAL_RUN
H4 = HUMAN_APPROVAL_PENDING
H5 = NOT_STARTED
```

---

# 23. Git authority

For this task:

```text
create external validation environment = YES
build wheel = YES
create isolated venv = YES
create helper scripts/docs = YES
production-code edits = NO unless a real standalone blocker is found
targeted smoke tests = YES
commit = NO
push = NO
tag = NO
```

If a product defect prevents standalone execution, stop and report before changing architecture.

---

# 24. Completion report

Create:

```text
C:\PruebasLegacyMapper\FinalValidation\FINAL_MANUAL_VALIDATION_ENVIRONMENT_REPORT.md
```

Include:

```text
wheel used
installed version
Python version
entry point
provider identifier
model
Copilot discovery method
source path
project
solution
run root
scripts created
exact command behind each script
whether any real AI call was made during preparation
whether any scanner/analyzer run was made during preparation
smoke-check results
known prerequisites
```

Final readiness state:

```text
H4_FINAL_MANUAL_VALIDATION_ENVIRONMENT_READY
```

This is not H4 closure.

---

# Final principle

> **The owner must be able to close Claude, execute `RUN_LEGACYMAPPER.cmd`, and have the current final LegacyMapper independently produce the `human / ai / internal` package for review.**
