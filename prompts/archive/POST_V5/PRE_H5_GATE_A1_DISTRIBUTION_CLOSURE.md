# LegacyMapper Post-V5 — Gate A.1
## Distribution, Generic Runtime Defaults, and Controlled CLI Failure Closure

### Status

Pre-H5 Gate A is already `PASS`.

This Gate A.1 is a **narrow closure hardening round** before Gate B.

Do not reopen Gate A concepts.
Do not start Gate B yet.
Do not start H5.
Do not start V6.

The purpose is to close the remaining runtime/productization gaps found after Gate A.

---

# 1. Scope

Resolve exactly these items:

```text
A1-01  Real distribution/installability validation
A1-02  Remove IST-specific defaults from behavior prototype
A1-03  Controlled error for output-manifest on nonexistent input
```

Additionally:

```text
record but do not redesign physical source-path provenance
```

The `scan_summary.root` / `source_repository` path-provenance topic belongs to Gate B because it may affect Evidence format/projection.

---

# 2. Product principle

The target product behavior is:

> LegacyMapper is generic, distributable, path-driven, and fails through explicit domain/CLI contracts instead of leaking Python exceptions.

A user should not need to know:

```text
repository layout
development checkout
developer project names
internal package structure
Python source-tree assumptions
```

---

# 3. A1-01 — Distribution / installability

Gate A proved runtime-copy portability.

Gate A.1 must prove an actual supported distribution/install workflow.

## Preferred implementation

Add standard Python packaging metadata if compatible with the current repository:

```text
pyproject.toml
```

Use modern standard packaging.

Do not add packaging complexity beyond what the product needs.

The package must include runtime resources such as:

```text
legacy_documenter/templates/human/default/**
legacy_documenter/templates/ai/**
schemas/assets that runtime commands require
```

Do not accidentally include:

```text
tests
historical outputs
large generated artifacts
Claude temp files
developer-only tools
IST source
```

unless packaging conventions explicitly require something small and harmless.

---

# 4. Installed execution

Validate from a clean isolated environment.

Preferred validation:

```text
create temporary venv
pip install <LegacyMapper package / wheel>
change cwd to unrelated directory
run installed LegacyMapper
```

If a console script is appropriate, define one, e.g.:

```text
legacymapper
```

If preserving:

```text
python -m legacy_documenter
```

is safer, that is also acceptable.

Do not break the existing:

```text
python main.py ...
```

workflow unless there is a compelling compatibility reason and it is documented.

---

# 5. Distribution test matrix

From the isolated environment verify:

```text
--help
full small fixture
docs persisted output
visuals persisted output
deliver persisted output
built-in human template discovery
custom --template-dir
AI-disabled deterministic commands
interpret with provider unavailable -> controlled failure
```

Requirements:

```text
cwd unrelated to installation
source path with spaces
Unicode path
output elsewhere
no developer checkout in PYTHONPATH
no COPILOT_CLI_PATH
no provider installed
```

The installed product must not read resources from the source checkout.

---

# 6. Wheel / package resource integrity

Build the distribution artifact and inspect it.

Verify that required built-in resources are present.

At minimum confirm:

```text
human/default/template.yaml
human/default/document.html
human/default/styles.css
human/default/pdf.css
```

and any renderer/static resource required by production commands.

Add an automated test that fails if packaged resource discovery breaks.

---

# 7. A1-02 — Remove IST-specific behavior defaults

Current debt:

```text
behavior/prototype.py
--project WebPREPrevencion
--solution slnPREPrevencion_2010
```

These defaults must not exist in the generic product.

A generic invocation must either:

```text
derive solution/project deterministically when unambiguous
```

or:

```text
require explicit --solution / --project
```

Do not silently choose the historical IST names.

Preferred decision rule:

```text
0 candidates -> controlled error
1 candidate -> select deterministically and record selection
>1 candidates -> require explicit user selection
```

Apply equivalent logic only if supported safely by existing Evidence.

Do not invent a business module/project.

---

# 8. Generic behavior CLI contract

The behavioral documentation entry point must be usable against an arbitrary supported repository/output.

No production defaults may contain:

```text
WebPREPrevencion
slnPREPrevencion_2010
IST_40
PREPrevencion
```

except in:

```text
tests
fixtures
historical docs/results
```

Add a production-code literal audit test.

---

# 9. A1-03 — output-manifest controlled failure

Current known behavior:

```text
output-manifest <nonexistent-directory>
→ raw FileNotFoundError
```

Replace this with a controlled CLI/domain failure.

Requirements:

```text
human-readable message
machine-detectable code/status
non-zero exit code using existing exit-code contract
no Python traceback for expected invalid input
no partial output mutation
```

Reuse the Gate A path contract where appropriate.

Do not create a separate inconsistent validation system.

---

# 10. CLI consistency

Expected-input failures across public commands should follow one recognizable pattern.

Examples:

```text
SOURCE_PATH_NOT_FOUND
OUTPUT_PATH_NOT_DIRECTORY
PROVIDER_UNAVAILABLE
OUTPUT_MANIFEST_INPUT_NOT_FOUND
```

Exact naming may follow existing conventions.

Do not renumber the authoritative exit-code contract.

Expected user-input errors must not surface as uncaught exceptions.

---

# 11. No new scope

Do not fix in this round:

```text
UI/navigation/styles → Evidence Core
cross-project BL resolution
source physical-path projection redesign
second human template
consumer CLI
large renderer refactors
typing cleanup
broad exception cleanup
V6 features
```

These belong to later gates/debt work.

---

# 12. Tests — directed first

Create focused tests, for example:

```text
tests/test_post_v5_gate_a1_distribution.py
```

Cover:

```text
package build succeeds
required template resources included
installed runtime works outside checkout
installed runtime works from unrelated cwd
installed runtime deterministic commands require no provider
built-in template works after install
custom template override works after install
no IST-specific production defaults
single solution/project deterministic selection
multiple candidates require explicit selection
zero candidates controlled failure
output-manifest nonexistent path controlled failure
no traceback for expected path error
existing python main.py compatibility remains
```

No real AI provider calls.

---

# 13. Full suite policy

During implementation:

```text
directed tests only
```

When stable:

```text
relevant existing Gate A/H4/H1 tests
```

Then exactly one final full suite on the final tree:

```text
python -X utf8 -m unittest discover -s tests
```

Require:

```text
0 failures
0 errors
```

Record totals and duration.

---

# 14. Clean distribution proof

Produce a reproducible proof, including:

```text
distribution artifact type
installation command
temporary environment path class (not developer-specific literal)
runtime command used
cwd deliberately outside checkout
provider unavailable
commands/results
resource discovery result
```

Do not rely only on unit tests.

---

# 15. Historical compatibility

Preserve:

```text
Evidence semantics
stable IDs
existing baseline
H1 interpret behavior
H2 docs
H3 visuals
H4 deliver/template behavior
Gate A path contract
```

Do not rescan IST merely for this closure.

Use a small fixture for installed `full`.

Use persisted IST output only for relevant projection regression if needed.

---

# 16. Documentation and state

Create:

```text
docs/POST_V5/PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE_RESULT.md
```

Optionally:

```text
docs/POST_V5/PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE_EVIDENCE.json
```

Update:

```text
PROJECT_STATE.json
README.md
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
```

Expected successful state:

```text
PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE = PASS
```

And retain:

```text
PRE_H5_GATE_A_PORTABILITY = PASS
H5 = NOT_STARTED
```

---

# 17. Remaining debt after A.1

If successful, the pre-H5 plan becomes:

```text
Gate B
DT-03 UI/navigation/styles → Evidence Core
+ evaluate physical-path vs logical provenance projection

Gate C
DT-04 cross-project BL resolution
DT-07 second human template validation
DT-08 selected remaining product debt
UX-03 decision
```

Do not mark these resolved.

---

# 18. Git authority

For Gate A.1:

```text
edit production code = YES
edit tests = YES
edit docs/state = YES

commit = NO
push = NO
tag = NO
```

No Git versioning without explicit human authorization.

---

# 19. Success criteria

Gate A.1 passes only if:

```text
LegacyMapper can be installed/distributed into an isolated environment
built-in templates/resources work from the installed distribution
no source-checkout dependency exists
behavior prototype has no IST-specific production defaults
ambiguous project/solution selection is handled explicitly
output-manifest invalid input fails cleanly without raw traceback
deterministic commands still work without AI provider
existing Gate A guarantees remain green
one final full suite passes
H5 remains NOT_STARTED
```

Final principle:

> **A generic product cannot rely on a developer checkout, a developer project name, or an uncaught Python exception as part of its user contract.**
