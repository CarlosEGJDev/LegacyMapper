# LegacyMapper — Owner Full IST Standalone Acceptance

## Purpose
Independent owner acceptance test outside the AI-assisted development environment.

Prove LegacyMapper can be installed and operated as a standalone product against the complete real IST corpus.

This is NOT development, NOT H5, and NOT V6.

## 1. Entry conditions
Run only after:
```text
POST_V5 = CLOSED
POST_H5_FULL_WORKSPACE_AND_REPOSITORY_HYGIENE = PASS
final Post-V5 repository checkpoint committed and pushed
```

Build/obtain a wheel from that exact commit and record:
```text
git_commit_sha
wheel_sha256
LegacyMapper version
Python version
```

Do not run from the development checkout.

## 2. Clean environment
Create a new root, e.g.:
```text
C:\LegacyMapperAcceptance\
    runtime\
    work\
    output\
    logs\
```

Requirements:
```text
new venv
no PYTHONPATH
no dependency on C:\dev\LegacyMapper
no dependency on old C:\PruebasLegacyMapper state
no copied historical baseline
no copied historical AI responses
working directory unrelated to repository
```

Install only from the release-candidate wheel.

## 3. Real source
Use the complete real IST source tree as the only pre-existing product input:
```text
<SOURCE_ROOT> = C:\Users\cgalianj\source\IST\Operacional
```

Everything else must be generated fresh.

## 4. Provider/account verification
Before the run, verify the intended GitHub Copilot account:
```text
/user
/user list
/usage
```

Also verify token overrides:
```powershell
$env:COPILOT_GITHUB_TOKEN
$env:GH_TOKEN
$env:GITHUB_TOKEN
```

Do not put secrets in reports.

## 5. Fresh deterministic analysis
Run a complete deterministic IST analysis from scratch.

No reuse of H5 baseline.

Record:
```text
source root
source file count
solutions
projects
duration
analyzer version
analyzer fingerprint
Evidence schema versions
baseline fingerprint/hash
```

## 6. Full-system AI interpretation
Interpret the complete system, not only representative cohorts.

Coverage must include every resolvable solution/project with sufficient Evidence.

Do NOT call the provider per source file.

Use hierarchical structured interpretation:
```text
system
→ solution
→ project/component
→ view/behavior where applicable
→ cross-project flow
→ data interaction
```

Persist every successful request/response immediately.

## 7. Coverage contract
Every discovered project must end in exactly one state:
```text
HUMAN_AND_MACHINE_DOCUMENTED
MACHINE_ONLY_DOCUMENTED
UNRESOLVED_NO_SOLUTION
CONTROLLED_ERROR
```

No project may silently disappear.

For each resolvable project:
```text
machine knowledge = required
human documentation = required where meaningful
```

Projects without UI still receive human-readable documentation describing, where evidence supports it:
```text
observable purpose
responsibilities
consumers/callers
dependencies
business/data flow
database interactions
cross-project relations
unresolved behavior
```

Do not invent screens.

## 8. Human knowledge product
Generate a system-level product:
```text
<OUTPUT_ROOT>\
    human\
        index.html
        IST_Complete.pdf
        executive\
        system\
        solutions\
        projects\
        views\
        flows\
        data\
        diagrams\
    ai\
    internal\
    ACCEPTANCE_MANIFEST.json
```

`human/index.html` must be the main navigation entry point for the complete system.

## 9. Human documentation levels
Include:
```text
1. Executive overview
2. System map
3. Solution catalog
4. Project catalog
5. UI/view behavior
6. Non-UI services/business/data projects
7. Cross-project flows
8. Data/procedure interactions
9. Unresolved areas
10. Technical drill-down
```

Macro first, micro second.

Avoid source-code dumps.

## 10. Human truth contract
Human states:
```text
Confirmado
Inferido
No resuelto
```

Forbidden in normal human narrative:
```text
EP-*
FLOW-*
CALL-*
DAO-*
raw source paths
line-number references
provider/model diagnostics
internal Evidence identifiers
```

Those belong in `ai/` or `internal/`.

## 11. AI truth contract
AI must not:
```text
invent unsupported business purpose
promote inference to confirmed
declare code obsolete because usage was not observed
auto-canonicalize business terminology
hide unresolved evidence
```

## 12. Full-system AI coverage metrics
Report:
```text
solutions discovered
projects discovered
projects interpreted
projects human-documented
projects machine-only
views interpreted
flows interpreted
data interactions interpreted
cross-project relations interpreted
unresolved items
provider requests
provider successes
provider retries
provider replays
provider failures
```

## 13. Quota/resume safety
Complete IST interpretation may consume substantial quota.

Required:
```text
persist each request/response immediately
stable request identity
resume without repeating successful requests
bounded retry policy
checkpoint after each solution/project group
```

If quota is exhausted:
```text
stop cleanly
preserve completed work
report exact remaining coverage
resume later without replaying completed provider calls
```

Do not silently skip interpretation.

## 14. Deterministic projection after AI
Once interpretation exists, regenerating:
```text
HTML
PDF
SVG
wireframes
indexes
catalogs
```
must not call the provider again.

## 15. Standalone runtime proof
PASS requires:
```text
wheel installation succeeds
CLI works outside repo
no PYTHONPATH
no old H5 state
no historical fixture tree
templates/resources load from installed package
Unicode/space paths work
provider account works
fresh analysis works
fresh interpretation works
full human package builds
machine package builds
```

## 16. Validation
Require:
```text
broken links = 0
missing assets = 0
invalid JSON = 0
dangling IDs = 0
human provenance leaks = 0
invalid human states = 0
silent project omissions = 0
```

Manual review:
```text
system index
executive overview
at least 5 solutions
large UI project
small UI project
cross-project flow
non-UI business/data project
sparse/unresolved project
```

## 17. Acceptance report
Create outside the repo:
```text
<OUTPUT_ROOT>\OWNER_ACCEPTANCE_RESULT.md
<OUTPUT_ROOT>\OWNER_ACCEPTANCE_EVIDENCE.json
```

Include:
```text
environment
wheel SHA
commit SHA
source scope
deterministic analysis result
AI full-system coverage
provider/account/model
quota usage summary
resume/replay behavior
human product result
machine product result
validation metrics
manual review notes
final verdict
```

No secrets/tokens.

## 18. Verdict
PASS requires:
```text
STANDALONE_INSTALL = PASS
FRESH_IST_ANALYSIS = PASS
FULL_SYSTEM_AI_INTERPRETATION = PASS
HUMAN_KNOWLEDGE_PRODUCT = PASS
MACHINE_KNOWLEDGE_PRODUCT = PASS
RESUME_WITHOUT_REPLAY = PASS
SILENT_OMISSIONS = 0
BLOCKING_ACCEPTANCE_DEFECTS = 0
```

If a blocking defect appears:
```text
OWNER_ACCEPTANCE = FAIL
```

Do not patch the installed acceptance environment manually.

Instead:
```text
record defect
return to repository
fix with targeted tests
build a new wheel
restart only the affected acceptance step where safe
```

## 19. Git policy
This acceptance run occurs outside the repository:
```text
repo edits = NO
commit = NO
push = NO
tag = NO
```

If acceptance passes, the owner may separately authorize a release/tag.

> This run proves LegacyMapper is a real standalone product, not something that only works inside the development environment where it was built.
