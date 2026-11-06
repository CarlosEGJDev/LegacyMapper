# LegacyMapper — Post-H5 Full Workspace and Repository Hygiene

## Objective

H5 has already completed successfully.

Authoritative state:

```text
H5 = CLOSED
POST_V5 = CLOSED
BLOCKING_DEBT = 0
V6 = NOT_STARTED
```

H5 validated:

```text
113 solutions
260 projects
1 authoritative deterministic IST analysis
15 real provider requests, all successful
3562 tests
0 failures
0 errors
132 skipped
```

This task is therefore NOT a Pre-H5 gate.

It is the **final post-H5 hygiene and productization cleanup** before the owner authorizes the final Git checkpoint.

The objective is to leave LegacyMapper:

```text
self-contained
fixture-independent
workspace-independent
folder-layout-independent
easy to resume
easy to test selectively
easy to understand
with historical clutter separated from current operational truth
```

Do NOT reopen H5.
Do NOT rerun H5.
Do NOT start V6.

---

# 1. Non-negotiable final invariants

At completion:

```text
H5 = CLOSED
POST_V5 = CLOSED
BLOCKING_DEBT = 0
V6 = NOT_STARTED

EXTERNAL_HISTORICAL_FIXTURE_DEPENDENCIES = 0
ACTIVE_ABSOLUTE_WORKSPACE_DEPENDENCIES = 0
BLOCKING_HYGIENE_DEBT = 0
```

No hygiene task may weaken or invalidate H5 closure evidence.

---

# 2. Preserve H5 evidence

Preserve repository evidence:

```text
docs/POST_V5/H5_REAL_IST_VALIDATION_AND_CLOSURE_RESULT.md
docs/POST_V5/H5_REAL_IST_VALIDATION_EVIDENCE.json
```

Preserve the H5 facts:

```text
one deterministic IST analysis
scanner after baseline = 0
analyzer after baseline = 0
downstream source opens = 0
BLOCKING = 0
```

Do not regenerate these results simply to clean the workspace.

---

# PHASE A — STORAGE INVENTORY AND CLEANUP

## 3. Inventory all generated workspace

Inspect recursively:

```text
C:\PruebasLegacyMapper\
```

Create:

```text
C:\PruebasLegacyMapper\STORAGE_INVENTORY_POST_H5.md
C:\PruebasLegacyMapper\STORAGE_INVENTORY_POST_H5.json
```

For every significant directory record:

```text
path
size_bytes
file_count
purpose
created_by
current_or_historical
referenced_by_repo
referenced_by_tests
referenced_by_scripts
contains_unique_state
duplicate_of
decision
reason
```

Allowed decisions:

```text
KEEP
MIGRATE_THEN_DELETE
DELETE
OPTIONAL_ARCHIVE
MANUAL_REVIEW
```

---

# 4. Special treatment of H5_Validation

H5 generated:

```text
C:\PruebasLegacyMapper\H5_Validation\
```

and a clean-room location such as:

```text
C:\PruebasLegacyMapper\H5 Validación ñ\
```

Do not automatically retain every H5 artifact just because H5 produced it.

Classify H5 output into:

```text
A. authoritative evidence already captured in repository reports
B. reusable deterministic baseline
C. persisted AI responses
D. final representative human packages
E. sweep-generated disposable packages
F. clean-room install/runtime copies
G. logs/temp/raster/build artifacts
```

Expected treatment:

```text
A -> KEEP in repository
B -> keep one canonical copy only if useful for future replay
C -> keep one canonical copy only if useful for future replay
D -> keep only a minimal approved sample if operationally useful
E -> DELETE after report verification
F -> DELETE after runtime validation is documented
G -> DELETE
```

H5 has already proven runtime independence, so duplicated clean-room installations are not permanent product state.

---

# 5. Canonical external workspace

Converge toward a small operational structure such as:

```text
C:\PruebasLegacyMapper\
    Current\
        state\
            baseline\
            ai\
        reference\
            final_human_sample\
        README.md

    Archive\
        [optional, only intentionally retained artifacts]
```

The exact folder name is not important.

The contract is:

> **The repository must not depend on the physical location of this workspace.**

Generated workspace can be moved or deleted.

---

# 6. Baseline retention policy

H5 created an authoritative baseline of approximately 3.70 GB.

Do not keep multiple copies.

Determine whether a retained H5 baseline is useful for:

```text
future reproducibility
AI replay
future V6 experiments
manual inspection
```

If yes:

```text
keep exactly one canonical copy
document its hash
document its schema versions
document how to relocate it
```

If no active product/test/runtime dependency exists:

```text
baseline may be treated as optional external archival state
```

LegacyMapper itself must remain functional without that specific baseline.

A fresh source analysis must be able to regenerate it.

---

# 7. AI response retention policy

Keep only unique persisted provider responses needed for:

```text
replay
audit
comparison
future deterministic projection
```

Deduplicate by:

```text
input identity
response identity
SHA-256
```

Delete duplicated copies across old H4/H5 run directories.

Provider responses must not be required for deterministic-only operation.

---

# 8. Remove obsolete historical workspace

After references and uniqueness are verified, delete:

```text
old H1/H2/H3/H4 generated outputs
superseded manual validation runs
old clean-room installations
duplicate wheels
duplicate venvs
duplicate deterministic baselines
duplicate AI-response trees
temporary render/raster output
test scratch output
obsolete logs
obsolete package sweeps
intermediate HTML/PDF/SVG trees
```

Never touch the real IST source corpus.

---

# 9. Storage result

Create:

```text
C:\PruebasLegacyMapper\STORAGE_CLEANUP_POST_H5_RESULT.md
```

Include:

```text
before_bytes
after_bytes
recovered_bytes
retained_baseline_bytes
retained_ai_bytes
deleted_paths
retained_paths
migrated_paths
```

---

# PHASE B — ZERO EXTERNAL FIXTURE DEPENDENCY

## 10. Hard rule

No active test may depend on:

```text
C:\PruebasLegacyMapper\...
C:\Users\<developer>\...
historical output folders
manual H4/H5 result packages
external generated snapshots
```

unless the test is explicitly classified as:

```text
REAL_IST
EXTERNAL_INTEGRATION
```

and receives its location via configuration.

---

# 11. Test fixture inventory

Inventory every active test fixture.

Classify:

```text
SYNTHETIC_UNIT
SMALL_CONTRACT
REPOSITORY_LOCAL_INTEGRATION
GENERATED_IN_TEST
HISTORICAL_SNAPSHOT
REAL_IST_EXTERNAL
PROVIDER_EXTERNAL
```

Required:

```text
HISTORICAL_SNAPSHOT required by active tests = 0
```

Historical snapshots can remain only as archival documentation, not active dependencies.

---

# 12. Replace historical fixtures

For each historical dependency:

```text
A. create minimal synthetic fixture
B. create small repository-local contract fixture
C. generate input dynamically
D. convert test into explicitly configured REAL_IST integration
E. remove redundant historical test
```

Do not copy multi-GB historical baselines into Git.

---

# PHASE C — TEST SUITE PRODUCTIZATION

## 13. Capability-oriented test profiles

Historical round tests may remain for audit value, but day-to-day verification must not require knowing round names.

Create stable profiles:

```text
FAST
CORE
ANALYSIS
BEHAVIOR
HUMAN_DOCS
AI_KNOWLEDGE
VISUALS
PACKAGING
DISTRIBUTION
PROVIDER
REAL_IST
FULL
```

Each profile must document:

```text
purpose
included modules/patterns
external dependencies
typical usage
expected duration class
```

---

# 14. Fast development workflow

Implement a simple runner such as:

```text
python -m legacy_documenter.devtest fast
python -m legacy_documenter.devtest behavior
python -m legacy_documenter.devtest packaging
python -m legacy_documenter.devtest full
```

or an equivalent repository-consistent mechanism.

Do not add a major testing framework solely for this cleanup.

The runner should select existing unittest modules.

---

# 15. Changed-area mapping

Create a maintained mapping:

```text
changed path -> recommended test profile
```

Examples:

```text
legacy_documenter/behavior/**        -> BEHAVIOR
legacy_documenter/visuals/**         -> VISUALS
legacy_documenter/deliver/**         -> PACKAGING
templates/human/**                   -> HUMAN_DOCS + PACKAGING
legacy_documenter/llm/**             -> PROVIDER + AI_KNOWLEDGE
legacy_documenter/utils/path_*       -> CORE + DISTRIBUTION
adapters/**                          -> ANALYSIS
```

Full suite is required for:

```text
milestone closure
release checkpoint
cross-cutting architecture change
shared contract/schema change
```

Not every local change.

---

# 16. Historical test cleanup

Inventory historical test modules such as:

```text
test_v4_*
test_v5_*
test_post_v5_*
```

Classify:

```text
AUTHORITATIVE_REGRESSION
DUPLICATED_COVERAGE
HISTORICAL_ONLY
OBSOLETE
```

Do NOT mass-delete tests for aesthetics.

Consolidate only where equivalent coverage is proven.

Goal:

> Active testing should be understandable by capability even if historical regression modules remain.

---

# PHASE D — PROMPT HYGIENE

## 17. Prompt inventory

Inventory all:

```text
prompts\
```

Classify:

```text
CURRENT
HISTORICAL_CLOSED
SUPERSEDED
DUPLICATE
EXPERIMENTAL
```

Current state:

```text
H1-H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
```

Therefore there should be no active H1-H5 execution prompt.

---

# 18. Archive historical prompts

Preferred conceptual layout:

```text
prompts\
    CURRENT\
        README.md
    archive\
        V4\
        V5\
        POST_V5\
```

Archive H1-H5 prompts.

Do not delete useful history unless exact duplicate/superseded and repository policy allows it.

Do not require prompt history to understand current architecture.

---

# 19. CURRENT prompt entry point

Create/update:

```text
prompts\CURRENT\README.md
```

It must say:

```text
Current state: POST_V5 CLOSED
H1-H5 CLOSED
V6 NOT_STARTED

There is currently no active implementation prompt.

To begin a new capability/version, create an explicit new owner-approved prompt.
```

This prevents accidental rerun of closed milestones.

---

# PHASE E — CANONICAL DOCUMENTATION

## 20. Resume guide

Create:

```text
docs/OPERATIONS/RESUME_LEGACYMAPPER.md
```

It must be sufficient to resume work from a fresh clone in an arbitrary directory.

Use placeholders:

```text
<REPO_ROOT>
<WORK_ROOT>
<SOURCE_ROOT>
<OUTPUT_ROOT>
```

Include:

```text
what LegacyMapper is
current state
architecture
installation
repository layout
workspace layout
source configuration
provider configuration
deterministic analysis
persisted Evidence reuse
AI interpretation
human docs
AI package
final packaging
test profiles
real IST testing
release/checkpoint procedure
how to regenerate disposable workspace
```

---

# 21. Workspace contract

Create:

```text
docs/OPERATIONS/WORKSPACE_CONTRACT.md
```

Define:

```text
repository = authoritative source/config/tests/docs
workspace = generated/disposable state
source corpus = external user input
```

The three may exist anywhere.

No relative placement between them is required.

---

# 22. Testing guide

Create:

```text
docs/OPERATIONS/TESTING_GUIDE.md
```

Include:

```text
profiles
when to run each
fixture policy
external integration policy
real IST configuration
provider configuration
full-suite gates
how to add tests
how to avoid historical output dependence
```

---

# 23. Current architecture

Create/update:

```text
docs/ARCHITECTURE/CURRENT_ARCHITECTURE.md
```

Canonical flow:

```text
Source
→ deterministic extraction/analysis
→ persisted Evidence
→ optional AI interpretation
→ structured knowledge
→ human / ai / internal projections
```

Core principles:

```text
analyze once / project many
human final authority
no auto-canonicalization
preserve unresolved
existence != usage
absence of usage evidence != obsolescence
```

---

# 24. Documentation authority

Recommended authoritative current documents:

```text
PROJECT_STATE.json
README.md
docs/ARCHITECTURE/CURRENT_ARCHITECTURE.md
docs/OPERATIONS/RESUME_LEGACYMAPPER.md
docs/OPERATIONS/WORKSPACE_CONTRACT.md
docs/OPERATIONS/TESTING_GUIDE.md
```

Historical roadmap/report docs must identify themselves as historical/version-specific.

Avoid multiple competing "current state" documents.

---

# PHASE F — PATH / MACHINE INDEPENDENCE

## 25. Audit absolute paths

Search active:

```text
legacy_documenter\
tests\
scripts\
pyproject.toml
README.md
docs/OPERATIONS\
```

for:

```text
C:\
Users\
PruebasLegacyMapper
dev\LegacyMapper
source\IST
```

Classify:

```text
ACTIVE_DEPENDENCY
TEST_EXAMPLE
DOC_EXAMPLE
HISTORICAL_RECORD
```

Required:

```text
ACTIVE_DEPENDENCY = 0
```

Historical reports may preserve historical paths.

Operational docs should use placeholders.

---

# 26. Relocation proof

Prove the product works when:

```text
repository path changes
workspace path changes
working directory is unrelated
paths contain spaces
paths contain Unicode
```

Do this with small synthetic inputs.

Do not rerun the full real IST analysis.

---

# PHASE G — CODE / SCRIPT / DOC HYGIENE

## 27. Inventory dead or confusing operational surfaces

Identify:

```text
obsolete scripts
superseded CLI wrappers
unused helper scripts
duplicate README instructions
old current-state files
dead test utilities
obsolete template copies
```

Before deletion require:

```text
reference search
contract check
targeted tests
```

Do not perform broad speculative refactoring.

H5 is already closed; this phase is hygiene, not architecture redesign.

---

# 28. Preserve H5 fixes

H5 fixed five real defects.

Ensure hygiene does not regress:

```text
exact solution membership matching
machine-only package for projects without UI/actions
knowledge.json data IDs
wireframes within frame
no business-purpose inference from solution name
```

The H5 regression tests must remain active.

---

# PHASE H — VALIDATION

## 29. No new real provider / IST analysis

During hygiene:

```text
real provider calls = 0
full IST deterministic analysis = 0
```

Use:

```text
synthetic fixtures
small contract fixtures
persisted state only where needed
```

---

# 30. Independence tests

Prove:

```text
tests pass without old C:\PruebasLegacyMapper\Resultados
tests pass without H4 historical run folders
tests pass without H5 sweep packages
tests pass after workspace relocation
FAST profile works
BEHAVIOR profile works
PACKAGING profile works
DISTRIBUTION profile works
```

Temporarily rename external historical directories during verification if necessary.

---

# 31. Final suite

After hygiene stabilizes, run once:

```text
python -X utf8 -m unittest discover -s tests
```

Required:

```text
0 failures
0 errors
```

This full suite must not run the real IST corpus or real provider unless current test contracts explicitly mark and skip those external integrations.

Expected external integration tests should be skipped with explicit reasons.

---

# PHASE I — FINAL REPORT

## 32. Create

```text
docs/POST_V5/POST_H5_FULL_WORKSPACE_AND_REPOSITORY_HYGIENE_RESULT.md
```

Include:

```text
storage before/after
GB recovered
baseline copies before/after
AI-response copies before/after
fixture dependencies removed
absolute path dependencies removed
test profiles
historical tests retained/removed
prompt archive result
canonical docs created
relocation proof
full suite result
provider calls = 0
IST analyses = 0
remaining hygiene debt
```

---

# 33. Hygiene completion gate

Required:

```text
POST_H5_FULL_WORKSPACE_AND_REPOSITORY_HYGIENE = PASS

EXTERNAL_HISTORICAL_FIXTURE_DEPENDENCIES = 0
ACTIVE_ABSOLUTE_WORKSPACE_DEPENDENCIES = 0
BLOCKING_HYGIENE_DEBT = 0

H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
```

If an active test still requires a historical external output tree:

```text
FAIL
```

Do not authorize final Git checkpoint until fixed.

---

# 34. Git authority

For this task:

```text
delete obsolete external generated outputs = YES
migrate/deduplicate retained external state = YES
repository hygiene edits = YES
test cleanup = YES
prompt archive/cleanup = YES
documentation cleanup = YES
state consistency updates = YES

provider calls = NO
real IST analysis = NO

commit = NO
push = NO
tag = NO
```

After owner review of this hygiene report, perform a separate final Git checkpoint.

---

# 35. Final sequence after hygiene

If hygiene passes:

```text
H5 CLOSED
POST_V5 CLOSED
→ review hygiene report
→ owner authorizes final Git checkpoint
→ commit
→ push
→ optional release/tag decision
→ V6 remains NOT_STARTED
```

---

# Final principles

> **The H5 run proves the product. The hygiene pass makes the repository maintainable.**

> **Tests validate contracts, not historical folders.**

> **Generated workspace is disposable.**

> **The repository must be resumable from any path on any machine.**

> **Closed prompts are history, not operational instructions.**

> **A full suite is a release/milestone gate, not the default test for every small change.**
