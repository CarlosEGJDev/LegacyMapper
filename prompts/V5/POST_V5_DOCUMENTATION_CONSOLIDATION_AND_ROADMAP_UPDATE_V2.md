# LegacyMapper — Documentation Consolidation & Post‑V5 Roadmap Update
## Claude execution prompt — documentation/state only, no product implementation

## 1. Objective

Update the repository documentation so that LegacyMapper can be resumed later without reconstructing the entire project history.

This task must consolidate:

1. what LegacyMapper was originally intended to solve;
2. what V1–V5 actually delivered;
3. the final V5 closure/tag state;
4. the clean-room user acceptance findings;
5. current real CLI/use model;
6. architecture/principles that must not regress;
7. lessons learned and best practices;
8. known limitations/debt;
9. the short post-V5 roadmap for **human experience + AI documentation**;
10. the new requirement for **AI-only interpretation from an existing deterministic baseline**.

This is a **documentation/governance round only**.

Do NOT implement product code.
Do NOT start V6.
Do NOT change schemas/contracts/runtime behavior.
Do NOT create new tags.

---

# 2. Ground truth / current state to preserve

Formal V5 closure:

```text
V5_CLOSED
V5_FINAL_CLOSURE_R3_COMPLETED
V5_FINAL_CLOSURE_PUSHED_TO_ORIGIN_MAIN
POST_V5_PLANNING
```

Formal V5 release commit:

```text
e831a2f84d2749b4452e06860521b3171093c7b9
```

Final tag:

```text
tag = v5
type = annotated
message = LegacyMapper V5 final release baseline
target = e831a2f84d2749b4452e06860521b3171093c7b9
published to origin = yes
```

Analyzer baseline:

```text
ANALYZER_VERSION = 3
ANALYZER_CODE_FINGERPRINT =
f05b2de43b726e75e03b97e1d35fef8b3407d54247e0a4e4537ab24d282fa26b
```

IST baseline:

```text
source:
  C:\Users\cgalianj\source\IST_40\Operacional

source files = 15138
source sha256 =
77965c64c7e204d39dc06a9451076df07a4b400e2bd41372fff2bab7fcd792e5

output files = 47523
output bytes = 2828066791
added = 0
removed = 0
changed = 0
```

Python pilot baseline:

```text
pilot_kind = SELF_HOSTED_CIRCULAR
external_independence_claim = false
independent_external_product = false
adapter = python-generic 1.0
source id = SELF_HOSTED_LEGACYMAPPER_V4_2_R8_E9E3D60
tree hash =
a190898bd89683a8ae443fd9d0640e37fc454327ceea34cacdd818c2862ce39e
cross-tech shared ids = 0 (with declared repository_id)
```

Final V5 tests:

```text
directed = 970
full suite = 3100
failures = 0
errors = 0
skips = 132
```

Final debt snapshot:

```text
BLOCKING = 0
FUTURE_PHASE = 14
OBSERVATION = 15
HISTORICAL_COMPATIBILITY = 5
```

Do not alter these historical baselines unless the repository contains stronger, later evidence.

---

# 3. Clean-room user acceptance facts to capture

A clean-room environment was created at:

```text
C:\PruebasLegacyMapper\V5_USER_ACCEPTANCE
```

The V5 release was extracted from tag `v5` via `git archive` into:

```text
...\V5_USER_ACCEPTANCE\app
```

and run outside the development repository.

Observed facts:

```text
runtime does not import from C:\dev\LegacyMapper
only a historical document mentions that path
own .venv used
Python version used in validation = 3.14.7
execution model = source checkout, python main.py
no pyproject.toml
no third-party runtime dependency installed
consumer CLI = not implemented
```

Clean-room status:

```text
V5_CLEANROOM_READY_FOR_USER_ACCEPTANCE
```

User acceptance notes created outside the repository:

```text
notes\START_HERE.md
notes\V5_USER_COMMANDS.md
notes\WHERE_TO_READ_HUMAN_DOCS.md
notes\WHERE_TO_READ_AI_CONTEXT.md
notes\V5_CLEANROOM_VALIDATION.md
samples\consumer_read_example.py
samples\fake_provider_demo.py
```

Read these files if present.

Important clean-room observations:

```text
1. Python pilot may require --long-paths on Windows.
2. `full` against a nonexistent repository currently returns SUCCESS with an empty analysis.
   This is a post-V5 UX/input-validation defect candidate.
3. tools.manual_verify_full_pipeline with a generic Fake provider can end INVALID_OUTPUT
   because the Evidence guard rejects ungrounded output; this is expected safety behavior.
4. PowerShell-specific helper commands (Activate.ps1, Copy-Item, Remove-Item) were not
   validated in that session because PowerShell tooling was blocked by group policy.
   Core LegacyMapper CLI arguments were validated in Git Bash.
5. Correct PowerShell path from `app` to the clean-room venv is:
   ..\.venv\Scripts\python.exe
   not:
   \.venv\Scripts\python.exe
```

Do not misrepresent the PowerShell validation status.

---

# 4. Product vision — rewrite clearly and preserve permanently

LegacyMapper's product vision must be documented in plain language.

The intended product is NOT merely a code documentation generator.

The core vision is:

> **LegacyMapper reconstructs the most reliable practical understanding possible of how a legacy system works, using deterministic evidence first and AI interpretation second, without silently inventing facts.**

Permanent principle:

> **Python discovers, structures, selects and validates; AI interprets.**

Human experience objective:

```text
non-technical user
→ what the system does and how it behaves

functional/analyst user
→ modules, processes, use cases, business flows, data/integrations

technical user
→ projects, layers, views/screens, main components, dependencies, data interactions

AI consumer
→ structured evidence, context, provenance and unresolved information
```

Important constraint:

```text
Method/class-level detail is NOT the primary human-experience target for the next phase.
```

For now, documentation should remain mostly **system/module/project/layer/flow/use-case level**.

Do not remove deep technical evidence; just do not make it the primary human-facing story.

---

# 5. New post-V5 capability requirement: AI-only over existing deterministic output

Document this as an explicit planned capability.

Current modes:

```text
A. deterministic:
   repo → deterministic analysis → Evidence + docs + AI context

B. full with AI:
   repo → deterministic analysis → AI interpretation → proposals
```

New desired mode:

```text
C. AI-only / interpret-existing:
   existing deterministic output
   → validate deterministic baseline
   → reuse Evidence / AI context / manifests
   → AI interpretation
   → proposals / human-centered docs
```

The essential purpose is:

```text
analyze once
→ interpret many times
```

especially for large systems such as IST.

The AI-only mode MUST refuse to call a provider unless the deterministic baseline is valid.

Expected validation gate before provider invocation:

```text
deterministic output exists
Evidence manifest exists and validates
schema supported
analyzer fingerprint known
AI context exists
provenance valid
source/repository identity available
no corrupt/stale baseline detected
```

If invalid, expected conceptual state:

```text
AI_ONLY_INPUT_INVALID
```

Do NOT implement this command in this task.
Do NOT lock the final CLI name yet.

Possible names may be documented as design candidates only:

```text
interpret
ai-only
interpret-existing
```

The contract matters more than the command name.

---

# 6. Human-centered documentation roadmap — concise H1–H5

Create/update a short official post-V5 roadmap with exactly this direction.

## H1 — AI-only from persisted deterministic knowledge

Goal:

```text
existing valid deterministic output
→ AI interpretation
```

without rescanning the source repository.

Must preserve:

```text
no provider call on invalid baseline
provenance
schema/fingerprint validation
proposal != canonical
human review authority
```

## H2 — Human documentation by audience level

Define three high-level profiles:

```text
executive
functional
technical-overview
```

Primary content:

```text
system
modules / functional areas
projects
layers
views/screens
main dependencies
business flows
data interactions
external integrations
unresolved/unknown areas
```

Avoid making method/class detail the default narrative.

## H3 — Structured visual projections

AI must not freely invent diagrams.

Preferred pipeline:

```text
Evidence
→ AI structured interpretation
→ validated structured diagram model
→ deterministic renderer
→ SVG / PNG / HTML / PDF
```

Visual types may include:

```text
system map
module map
project/layer map
dependency map
business flow
use-case diagram
data interaction map
external integration map
```

Every important visual relation should retain traceability to source evidence or be explicitly marked as AI interpretation/inference.

## H4 — Final human deliverables

Target deliverables:

```text
SYSTEM_OVERVIEW
MODULE_MAP
FUNCTIONAL_AREAS
USE_CASES
BUSINESS_FLOWS
ARCHITECTURE_OVERVIEW
PROJECT_LAYER_MAP
DATA_INTERACTIONS
EXTERNAL_INTEGRATIONS
KNOWN_UNRESOLVED_AREAS
```

Primary format:

```text
HTML navigable/interactively browsable
```

Secondary format:

```text
PDF for sharing/reading
```

Additional render artifacts:

```text
SVG / PNG
```

Do not promise rich browser interactivity until implemented and validated.

## H5 — Real IST validation and closure

Validate on a representative IST slice first.

Success criterion:

```text
a non-technical person can understand what the system/module does
a functional person can understand main flows/use cases
a technical person can understand projects/layers/dependencies
without opening source code
```

Also verify:

```text
important statements trace to evidence
AI interpretation is visibly separated from confirmed facts
unresolved remains unresolved
no automatic canonicalization
```

Only after H1–H5 are complete should the project return to broader technical expansion.

---

# 7. Explicitly defer unrelated expansion

The next short phase must NOT expand into:

```text
third technology
Plugin Runtime
richer Python type inference
Python DB adapter expansion
large refactors
consumer write capabilities
provider proliferation
deep method/class documentation
V6 redesign
```

Preserve these as future debt/backlog.

Human experience must be settled first.

---

# 8. Documents to inspect before editing

Read actual repository files first.

At minimum inspect, if present:

```text
AGENTS.md
CLAUDE.md
PROJECT_STATE.json
README.md
docs/PROJECT_RECOVERY.md

LEGACYMAPPER_V5_ROADMAP.md
LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md
LEGACYMAPPER_LESSONS_LEARNED.md
ASSISTANT_WORKING_RULES_AND_PREFERENCES.md
CLAUDE_CODE_CLI_BEST_PRACTICES.md

docs/V5/V5_FINAL_AUDIT_AND_RELEASE_BASELINE.md
docs/V5/V5_FINAL_BASELINE.json
docs/V5/V5_FINAL_CLOSURE.md
docs/V5/V5_FINAL_CLOSURE.json
docs/V5/V5_FINAL_DEBT_LEDGER.json
docs/V5/V5_OPERATIONS_GUIDE.md
```

Also inspect any duplicate `(1)` roadmap/history files and determine whether they are canonical duplicates, archived copies, or accidental divergence.

Do not silently update one duplicate while leaving another contradictory copy.

If canonical ownership is ambiguous, report it explicitly and update the clearly authoritative one plus any intentionally mirrored copy.

Read clean-room notes from:

```text
C:\PruebasLegacyMapper\V5_USER_ACCEPTANCE\notes\
```

if available.

---

# 9. Documentation updates required

## A. PROJECT_STATE.json

Update to reflect:

```text
V5 closed
v5 tag published
clean-room acceptance completed
current phase = POST_V5_PLANNING
next focused initiative = Human Experience + AI Documentation
V6 not started
```

Do NOT claim H1–H5 implemented.

Suggested semantic state:

```text
current_version = POST_V5
status = POST_V5_PLANNING
v5_closed = true
v5_tag = v5
v6_started = false
active_initiative = HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION
initiative_status = PLANNED
```

Use the repository's actual schema/field conventions instead of inventing incompatible fields.

## B. LEGACYMAPPER_V5_ROADMAP.md

Convert stale historical headers/state into a current roadmap.

Must show:

```text
V5.0 CLOSED
V5.1 CLOSED
...
V5.9 CLOSED
V5 Closure CLOSED
tag v5 published
clean-room acceptance completed
```

Preserve historical round details, but clearly label old "READY_TO_START" snapshots as historical.

Append a concise:

```text
Post-V5 — Human Experience & AI Documentation
H1 ... H5
```

Do NOT call this V6.

## C. LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md

This should become the best long-term continuity document.

Update:

- project vision;
- V5 final architecture/results;
- final closure/tag;
- clean-room validation;
- actual IST source path used by final V5 baseline;
- Python circular pilot limitation;
- user-facing runtime model;
- current CLI model;
- AI proposal/review/canonical distinction;
- AI-only desired capability;
- H1–H5 short roadmap;
- current debt/future boundaries.

Correct stale history carefully; do not erase old paths or facts—mark them historical.

## D. LEGACYMAPPER_LESSONS_LEARNED.md

If present, update it substantially.
If absent, create it.

Capture concise, reusable lessons, including:

### Product lessons

```text
documentation correctness is not enough; comprehension matters
human audiences need different abstraction levels
method/class detail is often too low-level for first understanding
large systems need maps/modules/flows/use cases before code detail
AI value is strongest after deterministic evidence exists
```

### Architecture lessons

```text
analyze once / project many
persist normalized evidence
separate logical repository identity from physical paths
never let AI mutate deterministic truth
proposal != canonical
preserve unresolved explicitly
runtime independence must be tested outside dev repo
```

### AI lessons

```text
AI should interpret evidence, not discover truth by guessing
provider calls must be explicit
fake provider must still be grounded
AI outputs require provenance/baseline identity
visual diagrams should come from structured models, not free-form drawing
AI-only reuse is essential for large repos
```

### Process lessons

```text
measure before design
real corpus before declaring architecture complete
one coherent objective per round
tests in same round
group corrections instead of micro-rounds
full regression before closure
clean-room acceptance before considering distribution complete
human review gates matter
```

### Windows/runtime lessons

```text
long path behavior matters
PowerShell relative paths differ from root-relative paths
clean-room venv must not resolve to dev environment
output location and repository_id have different identities
```

### UX lessons from clean-room

```text
full on nonexistent repo returning SUCCESS empty is confusing
consumer API exists but no consumer CLI
user START_HERE/command cheat sheet is valuable
AI-only mode missing from public CLI is a practical gap
```

Distinguish:

```text
lesson
accepted limitation
future defect candidate
future capability
```

## E. CLAUDE_CODE_CLI_BEST_PRACTICES.md

If present, update only reusable engineering/agent practices.

Include:

- always read actual `--help` before documenting CLI;
- never invent commands/options;
- distinguish Git Bash vs PowerShell syntax;
- validate runtime from clean-room;
- use explicit paths;
- do not assume `.venv` location;
- large real target outputs go outside dev repo;
- prefer deterministic baseline reuse;
- provider must not be invoked accidentally;
- never auto-approve/canonicalize;
- diagrams/AI docs must retain evidence grounding;
- do not treat a green suite alone as product acceptance.

Do not turn it into LegacyMapper product history.

## F. ASSISTANT_WORKING_RULES_AND_PREFERENCES.md

If present, preserve user collaboration preferences:

```text
Spanish concise communication
physical .md prompts
explicit repo paths
human checkpoints
max ~3 rounds/version/initiative where practical
one coherent objective per round
Claude executes repo prompts
Git authority must be explicit
commit/push/tag never assumed
```

Add:

```text
for product UX work, test as a real user outside dev repo
prefer runnable copy/paste commands
distinguish facts from interpretation
```

Do not include sensitive or machine-specific personal data unless already intentionally part of project docs.

## G. docs/V5/V5_OPERATIONS_GUIDE.md

Update only if current content is stale.

Add/confirm:

```text
clean-room execution model
correct PowerShell relative venv example
full / analyze / readiness / output-manifest
AI-enabled full
review flow
no consumer CLI
--long-paths note for large Windows outputs
```

Explicitly document current gap:

```text
No public AI-only command exists yet to reuse an already generated deterministic output.
```

Do NOT document a future command as if implemented.

## H. README.md / docs/PROJECT_RECOVERY.md / CLAUDE.md

Make minimal continuity updates only if needed.

They should point readers toward:

```text
PROJECT_STATE.json
final V5 baseline/closure
operations guide
project history
lessons learned
post-V5 human-experience roadmap
```

Do not duplicate all content.

---

# 10. New long-term planning document

Create:

```text
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
```

Keep it concise.

Required sections:

1. Purpose
2. Why this phase exists
3. What V5 already provides
4. Main human-experience gap
5. AI-only reuse requirement
6. H1–H5 roadmap
7. Non-goals
8. Success criteria
9. Permanent invariants
10. Deferred backlog
11. Recommended first round

Recommended first implementation round:

```text
H1-R1 — AI-only contract, baseline validation and UX design
```

No implementation in this documentation task.

---

# 11. Optional knowledge-transfer document

Create, only if it adds value and avoids duplication:

```text
docs/POST_V5/LEGACYMAPPER_PRODUCT_PRINCIPLES.md
```

Purpose: a short stable principles document independent of version history.

Suggested permanent principles:

```text
1. Deterministic facts before interpretation.
2. Never silently invent missing relationships.
3. Preserve confirmed / inferred / unresolved.
4. Provenance is part of the product.
5. Analyze once, project many.
6. Human comprehension is a first-class output.
7. AI output is a proposal until humans approve it.
8. Canonical knowledge requires explicit human authority.
9. Runtime must be independent from development/governance files.
10. Real-system validation is mandatory before architectural claims.
```

Do not create this file if the same purpose is already served cleanly by an existing canonical document.

---

# 12. Debt update

Do NOT rewrite the V5 closure debt history.

Add a post-V5 planning view that explicitly identifies:

```text
UX-01: full nonexistent repo returns SUCCESS empty
UX-02: no AI-only reuse command
UX-03: no consumer CLI
HX-01: human docs still too technical / insufficiently visual for broad audiences
HX-02: PDF/HTML visual documentation not yet productized
HX-03: structured use-case/module visual projection not implemented
```

These are NOT V5 closure blockers.

Classify them as:

```text
POST_V5
```

or equivalent repository convention.

Do not retroactively mark V5 incomplete.

---

# 13. Quality rules for documentation

Every statement must be one of:

```text
verified current fact
historical fact
accepted limitation
future capability
design candidate
```

Do not mix them.

Especially:

- do not write `ai-only` as an existing command;
- do not claim PowerShell wrappers were validated;
- do not claim external Python independence;
- do not imply Plugin Runtime exists;
- do not claim V6 has begun;
- do not imply AI-generated docs are canonical by default.

Avoid giant duplicated documents.
Prefer links between canonical docs.

---

# 14. Search for stale contradictions

Before finalizing, search repository documentation for stale phrases such as:

```text
V5_0_READY_TO_START
V5_2 not closed
V5 closure pending
TAG_NOT_CREATED_PENDING_HUMAN_DECISION
v5 tag pending
V5_CLOSURE_IN_PROGRESS
V5_CLOSURE_R1_READY_FOR_HUMAN_REVIEW
v5_closure_started=false
V6_READY_TO_START
```

Do not blindly replace historical reports.

Classify each occurrence:

```text
historical receipt → preserve
current orientation/state → update
duplicate canonical doc → reconcile
```

Also search stale IST target references:

```text
C:\inetpub\wwwroot\2010\IST\Operacional
```

Keep them when explicitly historical, but make the final V5 baseline path clearly:

```text
C:\Users\cgalianj\source\IST_40\Operacional
```

---

# 14A. Permanent milestone execution rule

Document this as a reusable lesson and operating rule in the canonical process/lessons documentation:

```text
Milestone execution discipline:
- complete each milestone in a single prompt/round whenever reasonably possible;
- if one prompt is not enough, use at most 3 review/correction rounds by default;
- only exceptional, explicitly justified cases may extend to 5 rounds;
- if 3 rounds are insufficient, stop and rediagnose before continuing;
- do not continue mechanically with micro-rounds;
- group related corrections into one coherent round.
```

This is a permanent lesson learned from the project and should appear in the canonical lessons/process documentation, not only in this execution prompt.

# 15. Git scope

This task authorizes documentation/state edits only.

Allowed categories:

```text
*.md
PROJECT_STATE.json
documentation-only roadmap/state JSON if already canonical
```

No production/test/tool code changes.

Do NOT:

```text
commit
push
tag
amend
rebase
reset
clean
```

Leave the working tree ready for human review.

---

# 16. Deliverable report

Create:

```text
docs/POST_V5/POST_V5_DOCUMENTATION_CONSOLIDATION_RESULT.md
```

Report:

1. files inspected;
2. files updated;
3. files created;
4. canonical roadmap selected;
5. duplicate/stale docs found;
6. V5 final state recorded;
7. clean-room facts incorporated;
8. H1–H5 roadmap recorded;
9. lessons learned added;
10. best practices added;
11. stale contradictions remaining intentionally historical;
12. any ambiguity/blocker;
13. Git status;
14. recommendation.

Final state if clean:

```text
POST_V5_DOCUMENTATION_CONSOLIDATION_READY_FOR_HUMAN_REVIEW
NEXT = H1_R1_AI_ONLY_CONTRACT_AND_UX_DESIGN
```

If canonical-document ambiguity prevents safe consolidation:

```text
POST_V5_DOCUMENTATION_CONSOLIDATION_OPEN_DECISION
```

Do not start H1 implementation automatically.

---

# 17. Final principle

The point of this task is not to produce more documentation volume.

It is to leave a **small set of trustworthy, current, non-contradictory canonical documents** that explain:

```text
what LegacyMapper is
why it exists
what V5 proved
how to use it
what was learned
what remains limited
what comes next
```

Prefer clarity over volume.
