# LegacyMapper — Owner Acceptance Remediation R2
## Human Projection Normalization, Coverage Drift Diagnosis, and Zero-Provider Reprojection

## Context

The standalone real-AI acceptance completed the full interpretation successfully, but the final human product did not pass.

Authoritative real-AI result:
```text
planned requests = 597
successful requests = 597
failed attempts = 2 transient DNS failures
retries = 2
quota interruptions = 0
second run provider calls = 0
replayed responses = 597
projection provider calls = 0
scanner = 0
analyzer = 0
source reads = 0
```

Coverage:
```text
solutions = 91
projects = 228
HUMAN_AND_MACHINE_DOCUMENTED = 183
MACHINE_ONLY_DOCUMENTED = 10
UNRESOLVED_NO_SOLUTION = 35
CONTROLLED_ERROR = 0
PENDING_INTERPRETATION = 0
```

Blocking defect:
```text
BD-1
```

Real AI claim text contains literal prefixes:
```text
CONFIRMED:
INFERRED:
UNRESOLVED:
```

Those prefixes are rendered into 191 human pages. The human presentation contract only allows:
```text
Confirmado
Inferido
No resuelto
```

Current acceptance:
```text
FULL_SYSTEM_AI_INTERPRETATION = PASS
HUMAN_KNOWLEDGE_PRODUCT = FAIL
OWNER_STANDALONE_ACCEPTANCE = NOT_PASS_REMEDIATION_REQUIRED
```

## 1. Round classification

This is:
```text
OWNER_ACCEPTANCE_REMEDIATION_R2
```

It is NOT H5 reopening, POST_V5 reopening, V6, new AI interpretation, or new IST analysis.

Preserve:
```text
H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
```

## 2. Primary objective

Fix the product boundary:
```text
provider response
→ structured semantic normalization/validation
→ persisted semantic model
→ deterministic human renderer
```

Human renderers must not depend on raw provider textual prefixes.

Do not edit generated HTML after projection.
Do not patch the standalone output manually.
Fix the product in the repository.

## 3. Normalize truth-state prefixes

Implement deterministic normalization for leading markers:
```text
CONFIRMED:
INFERRED:
UNRESOLVED:
```

Normalization must:
```text
preserve structured truth state
remove redundant textual prefix from prose
not alter unrelated mid-sentence occurrences
not alter provenance/evidence semantics
not promote/demote state
```

Example:
```text
state = CONFIRMED
text = "CONFIRMED: The project calls X."
```
becomes:
```text
state = CONFIRMED
text = "The project calls X."
```

Human output may show:
```text
Confirmado — The project calls X.
```

It must never show:
```text
Confirmado — CONFIRMED: The project calls X.
```

## 4. Choose normalization boundary deliberately

Preferred order:
```text
A. normalize immediately after parse
B. normalize before semantic persistence
C. renderer normalization only if A/B would invalidate persisted request identity
```

The 597 accepted real responses already exist and must remain reusable.

Do not invalidate provider request identity merely because presentation normalization changed.

If persisted semantic artifacts require deterministic migration/re-normalization from stored accepted responses, do it with 0 provider calls.

Document the chosen boundary.

## 5. Preserve real AI responses

Use:
```text
C:\LegacyMapperAcceptance\work\real_ai_state
```

Required:
```text
real provider calls during remediation verification = 0
```

The 597 persisted real responses are authoritative for this acceptance attempt unless one is proven semantically invalid for an unrelated reason.

## 6. Regression tests for BD-1

Add tests using realistic provider output containing the three prefixes across:
```text
SYSTEM
SOLUTION
PROJECT
VIEW
FLOW
DATA
UNRESOLVED
```

Verify:
```text
structured state preserved
prefix removed from human prose
only Confirmado / Inferido / No resuelto visible
no English prefix leaks
no double state label
machine provenance intact
```

Also test that occurrences of those words later in legitimate prose are not stripped blindly.

Do not use an unsafe global regex.

## 7. Diagnose coverage drift 184/9 → 183/10

STUB:
```text
184 HUMAN_AND_MACHINE
9 MACHINE_ONLY
35 UNRESOLVED
```

REAL:
```text
183 HUMAN_AND_MACHINE
10 MACHINE_ONLY
35 UNRESOLVED
```

Identify the exact project that changed and report:
```text
stable id
project name
solution identity
STUB category
REAL category
reason
```

Determine whether it was driven by:
```text
deterministic applicability
AI semantic result
validation
empty subject
another rule
```

Required:
```text
CATEGORY_DRIFT_EXPLAINED = YES
```

Do not force equality merely to match STUB.

If it is a product bug, fix it and add a regression test.

## 8. Empty subject fields

Inspect persisted real semantic claims with empty `subject`.

Report:
```text
count
kinds affected
human impact
machine-reference impact
```

Classify:
```text
VALID_OPTIONAL
NORMALIZABLE_FROM_ENTITY_CONTEXT
PRODUCT_DEFECT
```

Do not invent business meaning.

If required, derive only from deterministic entity context or reject structurally.

## 9. Token usage = None

Treat as telemetry observation unless contractually required:
```text
TOKEN_USAGE_TELEMETRY = NOT_AVAILABLE_FROM_ADAPTER
```

Do not invent counts.
Do not block acceptance solely for missing provider token telemetry.

## 10. Targeted tests first

Run focused tests for:
```text
truth-prefix normalization
semantic re-normalization
human vocabulary
coverage classification
empty-subject handling
machine package stability
```

Real provider calls:
```text
0
```

## 11. Full suite

If production code changes, after targeted tests pass run once:
```text
python -X utf8 -m unittest discover -s tests
```

Require:
```text
0 failures
0 errors
```

## 12. Build candidate wheel

After code/tests pass, build a new wheel candidate.

Do not use it for new AI interpretation.

It only needs to:
```text
consume existing baseline
replay existing real AI state
reproject human/machine products
```

Record wheel SHA-256.

Do not commit/push yet.

## 13. Zero-provider acceptance reprojection

Use:
```text
baseline = C:\LegacyMapperAcceptance\output\baseline
real AI state = C:\LegacyMapperAcceptance\work\real_ai_state
```

Perform:
```text
interpret-system replay
→ provider calls = 0
→ 597 responses replayed

project-system
→ provider calls = 0
→ scanner = 0
→ analyzer = 0
→ source reads = 0
```

Write to a NEW directory:
```text
C:\LegacyMapperAcceptance\output\real_ai_product_r2
```

Do not overwrite the defective original `real_ai_product`.

## 14. Human validation

Require:
```text
broken links = 0
missing assets = 0
invalid JSON = 0
dangling IDs = 0
duplicate IDs = 0
human provenance leaks = 0
invalid human states = 0
silent project omissions = 0

literal "CONFIRMED:" in normal human claim text = 0
literal "INFERRED:" in normal human claim text = 0
literal "UNRESOLVED:" in normal human claim text = 0
```

Internal machine enums are allowed where designed.

## 15. Preserve interpretation meaning

Compare before/after:
```text
request ids
input hashes
raw response hashes
structured truth states
coverage inventory
```

Expected:
```text
new provider calls = 0
real provider responses reused = 597
baseline unchanged
```

Any semantic change must be limited to justified normalization.

## 16. SYSTEM interpretation check

Because SYSTEM was not in the 15-request sample, explicitly inspect the persisted real SYSTEM interpretation.

Verify:
```text
structured response valid
grounded
no unsupported business invention
no obsolescence inference
unresolved preserved
human projection readable
```

No provider call.

## 17. Acceptance result files

Do NOT replace canonical acceptance files with PASS yet.

During remediation create:
```text
C:\LegacyMapperAcceptance\output\OWNER_ACCEPTANCE_REMEDIATION_R2_RESULT.md
C:\LegacyMapperAcceptance\output\OWNER_ACCEPTANCE_REMEDIATION_R2_EVIDENCE.json
```

Keep historical acceptance result files.

Only after owner manual review may the canonical:
```text
OWNER_ACCEPTANCE_RESULT.md
OWNER_ACCEPTANCE_EVIDENCE.json
```
be updated to final PASS.

## 18. Manual owner review remains required

After automated R2 validation passes, stop and report:
```text
READY_FOR_OWNER_MANUAL_REVIEW = YES
```

Suggested owner sample:
```text
system overview
executive overview
5 solutions
large UI project
small UI project
non-UI project
cross-project flow
data-heavy project
unresolved project
some views
```

Do not declare PASS on the owner's behalf.

## 19. Repository report

Create:
```text
docs/ACCEPTANCE/OWNER_ACCEPTANCE_REMEDIATION_R2_RESULT.md
```

Include:
```text
BD-1 root cause
normalization boundary
tests
coverage drift explanation
empty-subject findings
token telemetry observation
full suite
zero-provider replay
zero-provider reprojection
human validation
new wheel candidate
manual review pending
```

Suggested state:
```text
OWNER_STANDALONE_ACCEPTANCE = READY_FOR_OWNER_MANUAL_REVIEW
```

## 20. Git authority

Authorized:
```text
repository code changes = YES
tests = YES
docs = YES
schemas/normalization = YES
build wheel candidate = YES
targeted tests = YES
full suite once = YES
zero-provider acceptance replay = YES
zero-provider reprojection = YES
```

Not authorized:
```text
new real provider calls = NO
fresh IST analysis = NO
commit = NO
push = NO
tag = NO
V6 start = NO
```

## Completion gate

Ready for owner manual review only if:
```text
BD1_FIXED = PASS
REAL_PROVIDER_CALLS = 0
REAL_RESPONSES_REUSED = 597
COVERAGE_DRIFT_EXPLAINED = YES
EMPTY_SUBJECTS_CLASSIFIED = YES
TARGETED_TESTS = PASS
FULL_SUITE = PASS
REPLAY_PROVIDER_CALLS = 0
PROJECTION_PROVIDER_CALLS = 0
SCANNER = 0
ANALYZER = 0
SOURCE_READS = 0
BROKEN_LINKS = 0
INVALID_JSON = 0
DANGLING_IDS = 0
HUMAN_PROVENANCE_LEAKS = 0
INVALID_HUMAN_STATES = 0
ENGLISH_TRUTH_PREFIX_LEAKS = 0
SILENT_PROJECT_OMISSIONS = 0
BLOCKING_REMEDIATION_DEBT = 0
READY_FOR_OWNER_MANUAL_REVIEW = YES
```

> Do not spend provider quota to fix a deterministic presentation defect.

> Preserve the 597 accepted real interpretations and fix the product boundary.

> The human renderer consumes structured truth; it must not expose raw provider formatting.
