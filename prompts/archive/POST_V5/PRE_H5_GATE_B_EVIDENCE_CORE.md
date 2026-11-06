# LegacyMapper Post-V5 — Gate B
## Persist UI / Navigation / Styles into Evidence Core and Complete Analyze-Once Semantics

### Status

Pre-H5 Gate A = PASS.
Pre-H5 Gate A.1 = PASS.
H5 = NOT_STARTED.

This Gate B addresses the main remaining architectural debt that prevents the strongest form of:

> **Analyze once, interpret and project many times.**

Do not start Gate C.
Do not start H5.
Do not start V6.

---

# 1. Objective

Move the UI / navigation / style information currently read from source during behavioral documentation into persisted, versioned, deterministic Evidence.

Target architecture:

```text
Source repository
    ↓
deterministic analysis ONCE
    ↓
Evidence Core
    ├── source/code facts
    ├── UI structure
    ├── navigation/invocations
    ├── messages
    ├── parameters
    ├── style references
    └── source provenance
    ↓
source repository can be unavailable
    ↓
AI interpretation / docs / visuals / deliver / templates
```

After Gate B, behavioral documentation must not need to reopen source files merely to recover UI/navigation/style facts already known at analysis time.

---

# 2. Scope

Resolve:

```text
DT-03 UI/navigation/styles → Evidence Core
```

Also evaluate and, if safe, improve:

```text
physical source path vs logical source provenance projection
```

Do not resolve here:

```text
DT-04 cross-project BL resolution
DT-07 second human template
DT-08 remaining lower-priority debt
UX-03 consumers CLI
large renderer refactors
V6 features
```

---

# 3. Current known gap

The current behavioral prototype enriches from source after the deterministic baseline exists.

Known post-V5 facts include UI/navigation/style details such as:

```text
.aspx / .ascx control structure
labels/text
buttons
grids
panels
validators
navigation targets
popup/invocation relationships
messages
parameters
CSS classes
inline styles
master/style/theme references
icons/images
```

Some of these are currently persisted in a behavioral sidecar rather than in Evidence Core.

This Gate must remove that architectural split.

---

# 4. Evidence design principle

Evidence Core must persist facts, not presentation.

Persist:

```text
what exists
where it came from
relationships
resolved references
unresolved references
status/provenance
```

Do not persist:

```text
HTML layout
PDF layout
human prose
AI interpretation
visual design decisions
```

The renderer/template remains downstream.

---

# 5. Evidence schema extension

Design a versioned Evidence extension for UI/navigation/styles.

Prefer additive evolution over destructive schema changes.

Suggested conceptual entities:

```text
UiDocument
UiControl
UiProperty
UiEventBinding
UiNavigationEdge
UiMessage
UiParameter
UiStyleReference
UiAssetReference
UiContainerRelationship
```

Exact names may follow current conventions.

Every persisted record should preserve enough information for downstream behavioral reconstruction without rereading source.

At minimum include:

```text
stable_id
entity_kind
logical_source_path
source_refs
status
properties
relationships
```

---

# 6. UI structure evidence

Persist deterministic facts for supported markup.

For WebForms:

```text
.aspx
.ascx
.master
```

Capture where available:

```text
control type
control id
visible label/text
container/parent relation
order
server-side event binding
data-bound control type
validator relationship
panel/group/tab/container
popup/modal markers if evidenced
content placeholder/master relation
```

Do not invent missing controls.

Do not infer runtime visibility as fact unless statically supported.

---

# 7. Navigation / invocation evidence

Persist relationships such as:

```text
view/control → target view
view/control → popup
button/event → target view
control → user control
host page → contained user control
menu/config → view
```

Each relation must distinguish:

```text
CONFIRMED
INFERRED
UNRESOLVED
```

Preserve missing targets explicitly.

Do not convert absence of a resolved destination into absence of behavior.

---

# 8. Messages and parameters

Persist observable UI messages where statically supported.

Examples:

```text
literal confirmation text
literal validation/error message
resource key reference
dynamic/non-static message marker
```

Do not store invented paraphrases as deterministic Evidence.

Persist parameters where evidenced:

```text
querystring names
route-like values
control parameters
popup input/output
session/context keys where already deterministically discovered
```

Dynamic values may remain unresolved.

---

# 9. Style evidence

Persist style references, not rendered appearance.

Capture:

```text
CSS file references
class attributes
inline style declarations
master/theme/skin references
local image/icon references
resolved asset path
unresolved asset path
```

Where possible, preserve resolved declaration facts needed for documentary reconstruction, but do not turn Evidence into a browser/CSS engine.

Recommended separation:

```text
StyleReference = deterministic reference
StyleResolution = deterministic static resolution, if available
VisualReconstruction = downstream projection
```

---

# 10. Master/theme/host chain

A `.ascx` often receives layout/styles from its host/master rather than declaring them directly.

Persist enough graph structure to reconstruct:

```text
user control
→ host page
→ master page
→ stylesheet/theme/skin
→ local assets
```

If host resolution is ambiguous, preserve the ambiguity.

Do not choose one host without evidence.

---

# 11. Source reader removal from downstream behavioral flow

After the new Evidence exists, review:

```text
behavior/evidence.py
behavior/source.py
behavior/styles.py
behavior/prototype.py
```

Goal:

```text
docs/behavior/template rendering from persisted output
= zero source repository reads
```

Allowed source reads:

```text
only during deterministic analysis/extraction
```

Downstream commands must consume persisted Evidence.

If transitional compatibility wrappers are required, they must be explicit and temporary.

---

# 12. Analyze-once hard gate

Add a test where:

```text
1. analyze fixture
2. persist output
3. physically remove/rename source repository
4. run behavioral documentation
5. run docs
6. run visuals
7. run deliver
```

Expected:

```text
success from persisted output
scanner = 0
analyzer = 0
source_reads = 0
provider = 0 unless explicitly running interpretation
```

For AI interpretation, use persisted Behavioral Context / Evidence.

No source fallback.

---

# 13. Behavioral Context Package

Update the bounded AI context builder to consume the new persisted Evidence.

The AI context should include, when relevant:

```text
view identity
UI controls
observable actions
navigation
incoming/outgoing relationships
messages
parameters
styles/assets metadata
classes/data routes already persisted
unresolved facts
```

Do not send raw repository files as a substitute.

Keep AI context bounded and structured.

---

# 14. Sidecar migration

Current behavioral sidecars such as UI/navigation evidence should be reviewed.

Preferred end state:

```text
authoritative UI/navigation/style facts = Evidence Core
```

A sidecar may remain only as:

```text
derived projection
compatibility artifact
debug/report
```

It must no longer be the authoritative source of deterministic facts.

Document compatibility behavior.

---

# 15. Evidence versioning

If Evidence schema/fingerprint changes:

```text
increment the appropriate schema/version/fingerprint
document compatibility impact
preserve old-baseline validation behavior
do not silently accept incompatible baselines
```

Old persisted baselines should either remain readable through a compatibility path or fail clearly with an explicit unsupported/migration requirement.

Do not silently reinterpret old data as new Evidence.

---

# 16. Physical path vs logical provenance

Gate A/A.1 recorded that fields such as:

```text
scan_summary.root
source_repository
```

may persist physical machine paths.

Evaluate whether downstream portable projections can use:

```text
logical_source_id
logical_source_path
```

while retaining physical path only as optional provenance metadata.

Goals:

```text
stable identity independent of installation path
portable artifacts
clear distinction between logical source and runtime physical path
```

Do not change stable IDs or historical contracts casually.

If changing persisted Evidence format is risky, implement a safe derived logical projection and document physical provenance as compatibility metadata.

---

# 17. Deterministic IDs

UI/navigation/style evidence must use deterministic IDs.

IDs must not depend on:

```text
absolute developer path
current working directory
temporary folder
machine username
```

Prefer inputs such as:

```text
logical repository identity
relative source path
entity kind
control id/name
stable ordinal only where semantically necessary
```

---

# 18. Extraction location

UI/navigation/style extraction belongs in the deterministic adapter/analyzer layer.

For VB.NET WebForms/Oracle, place implementation under the existing adapter architecture.

Do not put source parsing into:

```text
behavior renderer
AI layer
template layer
deliver layer
```

Python discovers and persists.
AI interprets later.

---

# 19. Real IST baseline strategy

Do not repeatedly reanalyze full IST while developing.

Development:

```text
small targeted fixtures
directed tests
```

Only after the extractor/schema is stable, perform the necessary real IST refresh once if the Evidence format requires it.

If the old IST baseline cannot contain the new fields, document that a new deterministic baseline generation is required exactly once.

Do not mix repeated full IST scans with presentation testing.

---

# 20. Required representative fixtures

Create fixtures covering at least:

```text
.aspx page with master
.ascx user control
button click handler
grid
validator
panel/container
literal message
dynamic message
navigation to another view
popup/user-control relation
CSS class
inline style
stylesheet reference
image/icon
unresolved target
ambiguous host
```

Expected Evidence must be byte/deterministically stable.

---

# 21. Downstream regression

Verify no regression in:

```text
H1 interpret
H2 docs
H3 visuals
H4 deliver
human/default template
wireframe reconstruction
flow boxes
usage classification
AI claim validator
```

The behavioral output may improve due to richer persisted Evidence, but truth/status rules must remain identical.

---

# 22. Tests — directed first

Create focused Gate B tests, for example:

```text
tests/test_post_v5_gate_b_ui_evidence_core.py
```

Cover:

```text
UI controls persisted
parent/container relations persisted
events persisted
navigation persisted
messages persisted
parameters persisted
CSS class/style refs persisted
master/theme/style chain persisted
asset refs persisted
unresolved refs preserved
IDs deterministic across physical locations
source removed after analysis → downstream still works
behavior layer performs zero source reads
old sidecar is derived/non-authoritative
invalid/old schema handled explicitly
logical provenance independent of physical path
```

No real provider calls.

---

# 23. Test execution policy

During development:

```text
directed Gate B tests only
```

Then relevant:

```text
Evidence
adapter
H1
H4 behavior/template
Gate A/A.1 portability
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

---

# 24. Real IST validation

After directed tests are green, validate on IST.

If Evidence schema changes require a deterministic refresh:

```text
perform ONE full deterministic analysis
```

Record:

```text
scanner count
analyzer count
new Evidence schema/fingerprint
file count
delta explanation
```

Then close/rename/remove source access for downstream validation and run:

```text
interpret as configured
docs
visuals
deliver
human behavioral/template rendering
```

Expected after baseline exists:

```text
scanner = 0
analyzer = 0
source repository reads = 0
```

This is the key Gate B acceptance test.

---

# 25. Required report

Create:

```text
docs/POST_V5/PRE_H5_GATE_B_EVIDENCE_CORE_RESULT.md
```

and preferably:

```text
docs/POST_V5/PRE_H5_GATE_B_EVIDENCE_CORE_EVIDENCE.json
```

Report:

```text
schema changes
new evidence entities
extractors
sidecar migration
logical/physical provenance decision
tests
real IST results
source-offline downstream proof
compatibility impact
remaining debt
```

---

# 26. State updates

Update:

```text
PROJECT_STATE.json
README.md
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
```

Successful state:

```text
PRE_H5_GATE_B_EVIDENCE_CORE = PASS
```

Keep:

```text
PRE_H5_GATE_A_PORTABILITY = PASS
PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE = PASS
H5 = NOT_STARTED
```

---

# 27. Remaining debt after Gate B

If Gate B passes, only Gate C remains before H5:

```text
DT-04 cross-project BL resolution
DT-07 second human template validation
DT-08 selected remaining product debt
UX-03 decision
```

Do not declare Gate C items resolved.

---

# 28. Git authority

For Gate B:

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

# 29. Success criteria

Gate B passes only if:

```text
UI/navigation/style facts are authoritative in persisted Evidence
behavioral documentation no longer rereads source
downstream projections work after source is unavailable
AI context is built from persisted structured Evidence
unresolved UI/navigation facts remain unresolved
style reconstruction consumes persisted style evidence
stable IDs do not depend on physical machine path
physical vs logical provenance has an explicit contract
sidecar is no longer authoritative
tests pass
one final full suite passes
H5 remains NOT_STARTED
```

Final principle:

> **The source repository is needed to discover facts once. It must not be needed again merely to explain, render, or reinterpret those facts.**
