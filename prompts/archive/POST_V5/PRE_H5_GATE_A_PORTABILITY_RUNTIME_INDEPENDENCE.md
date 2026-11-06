# LegacyMapper Post-V5 — Gate A
## Portability, Runtime Independence, Strict Input Validation, Optional AI, and Path/Resource Contract

### Status

H4 human documentation is ready for final human approval.

H5 must **not** start yet.

This Gate A is the first pre-H5 hardening gate.

The goal is to prove that the current LegacyMapper product can run from a clean environment and from arbitrary valid paths without depending on the development machine, repository checkout location, Claude/Copilot temp folders, current working directory, or an installed AI provider.

This is product hardening, not a new capability phase.

---

# 1. Product requirement

LegacyMapper must satisfy this operational principle:

> **A user gives LegacyMapper a valid source path and an output path, and it works from any supported environment without depending on where LegacyMapper was developed.**

The deterministic core must be self-contained.

AI is optional.

No absolute developer paths may be required.

---

# 2. Gate A scope

Resolve together:

```text
DT-01  Portability / runtime independence
DT-02  UX-01 strict invalid-path handling
DT-05  AI provider is optional
DT-06  Global path/resource contract
```

Do not work on:

```text
DT-03 UI/navigation/styles → Evidence Core
DT-04 cross-project BL resolution
DT-07 second human template
DT-08 consumer CLI / renderer maintainability
H5
V6
```

---

# 3. Required execution model

The supported execution model must be path-driven.

Equivalent CLI shapes are acceptable if they follow current conventions, but all commands must resolve resources independently of cwd.

Examples:

```text
python main.py full <source-path> --output <output-path>
python main.py interpret <existing-output>
python main.py docs <existing-output>
python main.py visuals <existing-output>
python main.py deliver <existing-output>
```

For human behavioral documentation/template flow, equivalent supported commands must also work from a non-repository cwd.

The implementation must not assume:

```text
cwd == C:\dev\LegacyMapper
repository lives on C:
developer username
specific temp directory
specific Claude/Copilot runtime location
editable source checkout
```

---

# 4. Runtime resource contract

Define one explicit resource-resolution policy.

Recommended precedence:

```text
1. explicit CLI argument
2. explicit environment/config override where already supported
3. packaged/built-in runtime resource
4. fail clearly
```

Resources include:

```text
templates
schemas
static assets
default configuration
prompt-independent renderer resources
adapter metadata
package data
```

Do not silently search arbitrary developer directories.

No production code may contain hardcoded paths such as:

```text
C:\dev\LegacyMapper
C:\Users\<developer>
AppData\Local\Temp\claude
scratchpad paths
IST-specific absolute paths
```

Test fixtures may use temporary paths, but runtime code must not.

---

# 5. Built-in templates must travel with the product

`templates/human/default` must work when LegacyMapper is:

```text
copied to another directory
executed from another cwd
installed as a package
used from a read-only installation directory where output is elsewhere
```

The default template must not depend on the source checkout being the working directory.

User overrides must remain supported:

```text
--template human/default
--template-dir <external-template-dir>
```

or equivalent current syntax.

External template overrides must never mutate the built-in template.

---

# 6. UX-01 — strict source-path validation

The current known debt:

```text
full on a nonexistent repository can return empty SUCCESS
```

must be resolved.

Before scanning/analyzing:

```text
source path must exist
source path must be readable
source path must have the expected kind (directory/file according to command)
output path must be creatable/writable when needed
source and output must not resolve to an unsafe contradictory layout
```

If invalid:

```text
no scanner
no analyzer
no provider
no partial fake output
no SUCCESS
```

Use the authoritative exit-code contract already present in the project.

Do not invent a new exit-code scheme if an existing one applies.

The error must be human-readable and machine-detectable.

Examples to cover:

```text
nonexistent source
source points to file when directory required
permission denied
output parent nonexistent but creatable
output parent not writable
source path with spaces
source path with Unicode
relative source path
relative output path
different drive
trailing separator
"." cwd source
```

---

# 7. Clean-room portability validation

Create a real clean-room validation.

The test must not run from the LegacyMapper repo cwd.

Use a temporary or isolated directory such as:

```text
<temp>\legacymapper-cleanroom\
```

Requirements:

```text
copy/install only runtime-required files
change cwd to unrelated directory
invoke LegacyMapper with absolute source/output paths
verify deterministic analysis works
verify docs/visuals/deliver work from persisted output
verify built-in human template resolves
verify generated HTML/PDF/SVG assets resolve
```

The clean-room run must prove there is no hidden dependency on the development checkout.

If package installation is already supported, prefer installing into an isolated venv.

If not, use the smallest honest runtime-copy test possible and document the gap.

Do not claim packaging/install portability that was not actually tested.

---

# 8. AI provider must be optional

Deterministic LegacyMapper must work with:

```text
no Claude
no Copilot
no OpenAI client
no provider CLI
no provider credentials
no network access
```

For AI-disabled operations:

```text
full deterministic mode
docs
visuals
deliver
template rendering
existing deterministic projections
```

must not touch a provider.

For AI-required commands such as `interpret`:

```text
provider missing/unconfigured
→ explicit controlled error
→ no corruption of existing output
→ no fallback to invented content
```

The absence of a provider must never break deterministic commands.

---

# 9. Remove provider-location coupling

Audit provider bootstrapping for path coupling.

The H4-R5 pilot used a process-local `COPILOT_CLI_PATH` workaround.

That historical workaround must not become a hidden product requirement.

Allowed:

```text
explicit configured provider executable path
provider discovered through supported OS/PATH mechanism
provider-specific documented configuration
```

Not allowed:

```text
hardcoded developer CLI location
Claude temp directory dependency
silent search in developer profile
provider required for non-AI commands
```

---

# 10. Path normalization

Centralize or consistently reuse path handling.

Cover:

```text
Path.resolve / absolute normalization where safe
Windows drive letters
UNC paths if already supported
spaces
Unicode
case differences
relative paths
symlink/junction behavior without unsafe assumptions
```

Do not normalize in a way that mutates user intent or breaks reproducibility.

Persist provenance using the existing project conventions.

Avoid storing machine-specific absolute paths in portable artifacts unless the contract explicitly requires them.

When absolute paths are unavoidable for provenance, distinguish:

```text
source identity / logical path
runtime physical path
```

---

# 11. Portable generated artifacts

Generated human deliverables must remain portable after generation.

For HTML packages:

```text
no absolute local filesystem links
no C:\dev paths
no temp paths
no developer profile paths
relative asset links only where appropriate
offline open from disk
```

For PDF:

```text
no runtime dependency on source assets after file generation
```

For SVG:

```text
embedded/local relative resources only
no developer absolute references
```

Audit manifests and review guides for accidental absolute development paths.

Review guides may state the output folder used for validation, but portable package internals must not depend on it.

---

# 12. Read-only installation scenario

Validate:

```text
LegacyMapper runtime/package directory = read-only
source repository = read-only
output directory = writable
```

Expected:

```text
analysis/render succeeds
all caches/output/temp state goes to allowed output/temp location
no attempt to write into installation/templates/package directories
```

If some cache contract intentionally writes elsewhere, document and configure it explicitly.

---

# 13. Determinism

Portability changes must not change deterministic meaning.

For the same source and same effective configuration:

```text
Evidence semantic content equivalent
stable IDs unchanged unless path identity contract explicitly requires otherwise
same deterministic projections
same template output modulo explicitly machine-specific provenance fields
```

If machine-specific paths currently contaminate hashes/IDs, treat that as a defect and correct it conservatively.

Do not silently rewrite historical compatibility contracts without documenting impact.

---

# 14. Targeted tests first

During development, use directed tests only.

Create a focused Gate A test module, for example:

```text
tests/test_post_v5_gate_a_portability.py
```

Cover at least:

```text
invalid source rejected before scanner
invalid source rejected before analyzer
invalid source causes zero provider calls
nonexistent source is not SUCCESS
source path with spaces
Unicode path
relative source/output paths
different cwd
built-in template discovery outside repo cwd
custom template-dir outside repo
read-only runtime directory
portable HTML has no absolute dev/temp links
deterministic commands work without provider installed
interpret fails cleanly when provider is required but unavailable
explicit provider path works when configured
no hardcoded development paths in production runtime modules
clean-room execution
```

Use test doubles for provider calls in the suite.

Do not call a real provider from tests.

---

# 15. Full suite policy

Do **not** repeatedly run the complete suite during implementation.

Required process:

```text
1. directed Gate A tests
2. fix until green
3. relevant existing portability/runtime tests
4. ONE full suite at the end
```

Final command:

```text
python -X utf8 -m unittest discover -s tests
```

Require:

```text
0 failures
0 errors
```

Record:

```text
total
failures
errors
skips
duration
exit code
```

---

# 16. Real validation

Use at least two validations.

## A. Small controlled fixture

From a clean room:

```text
arbitrary source path with spaces/Unicode
arbitrary output path
cwd unrelated to repo
provider unavailable
```

Verify deterministic operation.

## B. Existing IST persisted-output regression

Do not rescan IST merely to test docs/render portability.

Use the already persisted IST output for:

```text
interpret gate validation as appropriate
docs
visuals
deliver
human template rendering
```

Confirm:

```text
scanner = 0
analyzer = 0
baseline unchanged
no provider for deterministic projections
```

If a fresh-source portability analysis is needed, use a small fixture, not full IST.

---

# 17. Hardcoded-path audit

Perform an explicit production-code scan for path coupling.

Search for at least:

```text
C:\
Users\
AppData\
Temp\claude
scratchpad
PruebasLegacyMapper
dev\LegacyMapper
source\IST
```

Classify every occurrence:

```text
runtime defect
test fixture
documentation/example
historical record
```

Runtime defects must be removed.

Do not rewrite historical documentation solely because it records a real historical path.

---

# 18. Output/report

Create:

```text
docs/POST_V5/PRE_H5_GATE_A_PORTABILITY_RESULT.md
```

and, if useful:

```text
docs/POST_V5/PRE_H5_GATE_A_PORTABILITY_EVIDENCE.json
```

Report:

```text
scope
changes
path contract
UX-01 resolution
clean-room setup
read-only-runtime result
provider-absent result
hardcoded-path audit
directed tests
full suite
IST persisted-output regression
known remaining debt
```

---

# 19. State updates

Update:

```text
PROJECT_STATE.json
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
README.md
```

Expected successful state:

```text
PRE_H5_GATE_A_PORTABILITY = PASS
```

Do not mark H5 started.

Do not close the whole post-V5 initiative yet.

---

# 20. Remaining debt after Gate A

If Gate A passes, explicitly leave only the next pre-H5 work as pending:

```text
Gate B
DT-03 UI/navigation/styles → Evidence Core

Gate C
DT-04 cross-project BL resolution
DT-07 second human template validation
DT-08 selected lower-priority debt
```

Do not accidentally declare those resolved.

---

# 21. Git authority

For Gate A:

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

# 22. Success criteria

Gate A passes only if all are true:

```text
nonexistent/invalid source cannot return SUCCESS
runtime works from unrelated cwd
built-in templates resolve outside repository cwd
deterministic commands work without any AI provider
AI-required commands fail cleanly when provider is unavailable
no production runtime dependency on developer absolute paths
runtime/source may be read-only while output is writable
generated human package has no hidden dev/temp path dependency
clean-room validation passes
directed tests pass
one final full suite passes
IST persisted baseline remains unchanged
H5 remains NOT_STARTED
```

Final principle:

> **LegacyMapper must depend on explicit inputs and packaged runtime resources, never on the machine or folder where it was developed.**
