# LegacyMapper — Owner Acceptance Remediation R1
## Full-System Hierarchical AI Interpretation + Resume

## Context

The independent standalone owner acceptance failed correctly.

Already proven:
```text
STANDALONE_INSTALL = PASS
FRESH_IST_ANALYSIS = PASS
```

Fresh acceptance corpus:
```text
SOURCE_ROOT = C:\inetpub\wwwroot\2010\IST\Operacional
source files = 16175
solutions = 91
projects = 228
flows = 10273
cross-project calls = 26206
Evidence errors = 0
fresh baseline = C:\LegacyMapperAcceptance\output\baseline
baseline files = 45874
baseline size ≈ 2.9 GB
analysis duration = 410 s
Evidence schema = 1.0
UI schema = 1.1
cross-project schema = 1.0
```

Blocking acceptance defect:
```text
ACC-01
FULL_SYSTEM_AI_INTERPRETATION = FAIL / NOT_AVAILABLE
```

The installed product currently supports project-level behavioral AI and bounded `interpret`, but not full hierarchical system interpretation with persistence/resume across the complete corpus.

No provider quota was consumed:
```text
provider requests = 0
```

---

## 1. Round classification

This is:
```text
OWNER_ACCEPTANCE_REMEDIATION_R1
```

It is NOT:
```text
H5 reopening
POST_V5 implementation continuation
V6
acceptance-environment patching
```

Preserve:
```text
H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
```

This is a release-candidate remediation discovered by independent owner acceptance.

---

## 2. Product objective

Implement first-class full-system AI orchestration over persisted deterministic Evidence:

```text
analyze once
→ interpret system hierarchically
→ persist every AI result
→ resume safely
→ project human/machine knowledge deterministically
```

Required downstream invariant:
```text
scanner = 0
analyzer = 0
source reads = 0
```

---

## 3. Full-system CLI

Add a clear CLI entry point, preferably:

```text
legacymapper interpret-system <baseline>
```

or an equally clear extension if existing architecture strongly favors it.

Support:
```text
baseline path
work/state path
provider
model/default model
resume
knowledge output path
```

No machine-specific required paths.

---

## 4. Hierarchical interpretation model

Implement explicit hierarchy:

```text
SYSTEM
  ↓
SOLUTION
  ↓
PROJECT / COMPONENT
  ↓
VIEW / BEHAVIOR (where applicable)
  ↓
CROSS-PROJECT FLOW
  ↓
DATA INTERACTION
```

Do not send the whole corpus in one request.
Do not call the provider per source file.
Use bounded structured context selection.

---

## 5. Coverage contract

Enumerate the complete baseline inventory.

Every project must end in exactly one state:

```text
HUMAN_AND_MACHINE_DOCUMENTED
MACHINE_ONLY_DOCUMENTED
UNRESOLVED_NO_SOLUTION
CONTROLLED_ERROR
```

No silent omission.

Create deterministic coverage metadata with:
```text
solution id
project id
stable project identity
interpretation state
human-doc applicability
provider request ids
semantic artifact ids
unresolved/error reason
```

Duplicate project names must remain distinguishable.

---

## 6. Non-UI projects

Projects without UI must still be interpreted where Evidence supports it.

May include:
```text
observable purpose
responsibilities
callers/consumers
dependencies
business/data flow
database interactions
stored procedures / SQL where supported
cross-project relations
unresolved behavior
```

Do not invent UI.
Do not infer business area only from project/folder names.

---

## 7. Stable provider request identity

Every AI request needs deterministic identity derived from semantic inputs, never timestamps or machine-local paths.

Include, as appropriate:
```text
schema version
interpretation type
entity identity
selected Evidence hashes
dependency semantic hashes
prompt/template version
provider/model policy
```

Persist:
```text
request identity
input hash
response body
response hash
validation result
accepted/rejected claims
provider metadata
```

---

## 8. Resume without replay

Blocking requirement.

If an accepted persisted response exists for the same request identity:

```text
provider call = 0
replay persisted response = YES
```

Required tests:
```text
first run -> calls > 0
interrupt
second run -> completed requests call provider 0 times
remaining work continues
```

Complete replay test:
```text
all persisted
→ provider calls = 0
→ same logical semantic output
```

---

## 9. Quota/provider interruption

On quota exhaustion or provider unavailability:

```text
stop cleanly
preserve completed state
preserve valid manifest
report completed/pending coverage
resume later without replay
```

Never silently skip pending interpretation.

---

## 10. AI truth contract

Respect:
```text
existence != reachable
reachable != observably used
absence of observable usage != obsolescence
AI interpretation != canonical
business meaning not inferred only from names
unresolved remains unresolved
```

Human truth states:
```text
CONFIRMED
INFERRED
UNRESOLVED
```

---

## 11. Structured semantic models

Add schemas/contracts for at least:
```text
SystemInterpretation
SolutionInterpretation
ProjectInterpretation
ViewInterpretation
CrossProjectFlowInterpretation
DataInteractionInterpretation
FullSystemCoverageManifest
```

AI produces structured semantics.
Deterministic renderers produce final documents.

---

## 12. System-level aggregation

System and solution summaries must explain behavior, not counts/files.

Cover:
```text
what the system appears to do
major solutions/subsystems
main responsibilities
important interaction paths
major data interactions
cross-project relations
unresolved areas
```

Principle:
> La IA explica comportamiento; no resume archivos.

---

## 13. Human knowledge product

Project the semantic model into an integrated human product:

```text
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
```

The navigable HTML is primary.

If one monolithic PDF is operationally unreasonable, a deterministic indexed PDF set is acceptable.

Include:
```text
executive overview
system map
solution catalog
project catalog
UI/view behavior
non-UI components
cross-project flows
data/procedure interactions
unresolved areas
technical drill-down
```

Macro first, micro second.

---

## 14. Human presentation contract

Normal human docs show only:
```text
Confirmado
Inferido
No resuelto
```

Do not expose:
```text
EP-*
FLOW-*
CALL-*
DAO-*
raw source paths
line numbers
provider/model diagnostics
internal Evidence ids
```

Those belong in `ai\` or `internal\`.

Preserve existing H4 visual principles.
Do not redesign diagrams unnecessarily.

---

## 15. Machine knowledge product

Produce structured full-system machine knowledge, for example:

```text
ai\
    knowledge.json
    system.json
    solutions.json
    projects.json
    views.json
    flows.json
    data.json
    unresolved.json
    provenance.json
    coverage.json
```

Exact partitioning may follow current architecture.

Require:
```text
stable ids
valid cross references
no dangling ids
traceable semantic provenance
resume support
future AI consumption
```

---

## 16. Deterministic projection

Once semantic responses are persisted:

```text
HTML/PDF/SVG regeneration must call provider 0 times
```

Presentation/template changes must not trigger new interpretation.

---

## 17. No source parsing downstream

Add regression tests proving:
```text
source opens = 0
scanner = 0
analyzer = 0
```

during:
```text
interpret-system
resume
human projection
machine projection
```

---

## 18. Development tests

Do NOT use real IST for routine development tests.

Create compact synthetic fixtures covering:
```text
multiple solutions/projects
duplicate project names
UI project
non-UI project
cross-project calls
data interactions
unresolved project
controlled error
provider interruption
quota unavailable
resume
full persisted replay
```

Automated test provider:
```text
fake/stub only
real provider calls = 0
```

---

## 19. Required targeted tests

Cover at least:
```text
full inventory enumeration
hierarchical request planning
stable request identity
machine-path independence
response persistence
resume without replay
complete replay with zero provider calls
controlled provider failure
quota exhaustion state
coverage manifest completeness
duplicate project identity
non-UI interpretation
no name-only business inference
human state vocabulary
no human provenance leakage
machine cross references
no dangling ids
deterministic rendering without provider
zero source reads downstream
CLI behavior/exit codes
```

Use current `legacy_documenter.devtest` profiles.

---

## 20. Full suite

After targeted tests pass and implementation stabilizes, run once:

```text
python -X utf8 -m unittest discover -s tests
```

Required:
```text
0 failures
0 errors
```

---

## 21. Real provider verification

Default development:
```text
real provider calls = NO
```

One minimal real-provider smoke check is allowed only if needed for adapter compatibility.

Do NOT run a full IST provider sweep from the development repo.

---

## 22. Copilot account preflight

The failed acceptance showed:
```text
SDK account = CarlosEGJDevSecond
gh active account = CarlosEGJDev
```

The owner has verified the intended acceptance account is:
```text
CarlosEGJDev
```

Do not hardcode usernames.

Before the next real provider run, require explicit provider/account preflight and report authenticated identity when available, without secrets.

Do not silently switch account.

---

## 23. New wheel

After implementation/tests pass:
```text
build wheel from exact clean Git commit
record commit SHA
record wheel SHA-256
```

Do not overwrite previous acceptance evidence.

---

## 24. Reuse the fresh acceptance baseline

Do NOT rerun the successful 410-second deterministic analysis merely because ACC-01 occurred afterward.

Reuse:
```text
C:\LegacyMapperAcceptance\output\baseline
```

provided:
```text
integrity unchanged
schema supported
new wheel can consume it
```

This is NOT H5/historical reuse. It is the baseline created by the same independent owner acceptance attempt.

If schema incompatibility requires a re-analysis, report that explicitly before doing it.

---

## 25. Acceptance retry scope

After a new wheel is installed in a clean acceptance runtime, resume at:

```text
Step 6 — FULL_SYSTEM_AI_INTERPRETATION
```

Then perform:
```text
full hierarchical interpretation
resume/replay proof
human system product
machine system product
validation
manual owner review
```

Do not declare acceptance PASS until all remaining gates pass.

---

## 26. Acceptance outputs

Eventually require:
```text
OWNER_ACCEPTANCE_RESULT.md
OWNER_ACCEPTANCE_EVIDENCE.json
```

with:
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

---

## 27. Repository reporting

Create:
```text
docs/ACCEPTANCE/OWNER_ACCEPTANCE_REMEDIATION_R1_RESULT.md
```

Record:
```text
ACC-01 root cause
implemented capability
CLI contract
semantic schemas
resume contract
test evidence
full suite result
new wheel candidate details
remaining acceptance steps
```

Do not rewrite H5/Post-V5 history.

Suggested state while implementing:
```text
H5 = CLOSED
POST_V5 = CLOSED
V6 = NOT_STARTED
OWNER_STANDALONE_ACCEPTANCE = FAILED_ACC_01_REMEDIATION_IN_PROGRESS
```

When ready:
```text
OWNER_STANDALONE_ACCEPTANCE = READY_FOR_RETRY
```

---

## 28. Git authority

Authorized:
```text
repository code changes = YES
tests = YES
schemas/contracts = YES
CLI changes = YES
docs = YES
build new wheel = YES
targeted tests = YES
full suite once = YES
synthetic fake-provider tests = YES
```

Not authorized:
```text
full real IST re-analysis from development repo = NO
full real provider sweep from development repo = NO
commit = NO
push = NO
tag = NO
```

Owner must review before Git checkpoint.

---

## 29. Completion gate

Ready for owner review only if:

```text
FULL_SYSTEM_ORCHESTRATOR_IMPLEMENTED = PASS
HIERARCHICAL_AI_MODEL = PASS
COMPLETE_PROJECT_COVERAGE_CONTRACT = PASS
PERSISTED_REQUEST_IDENTITY = PASS
RESUME_WITHOUT_REPLAY_TEST = PASS
FULL_REPLAY_PROVIDER_CALLS = 0
NON_UI_PROJECT_SUPPORT = PASS
HUMAN_SYSTEM_PROJECTION = PASS
MACHINE_SYSTEM_PROJECTION = PASS
DOWNSTREAM_SOURCE_READS = 0
TARGETED_TESTS = PASS
FULL_SUITE = PASS
BLOCKING_REMEDIATION_DEBT = 0
OWNER_STANDALONE_ACCEPTANCE = READY_FOR_RETRY
```

> Do not patch the acceptance environment. Fix the product.

> Analyze once, interpret many, resume without replay.

> One semantic truth, projected for human and machine consumers.

> No project disappears silently.
