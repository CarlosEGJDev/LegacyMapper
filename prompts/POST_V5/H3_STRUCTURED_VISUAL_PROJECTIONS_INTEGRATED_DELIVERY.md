# LegacyMapper Post-V5 — H3 Integrated Delivery
## Structured Visual Projections

### Execution model
Complete this milestone in **one integrated round whenever reasonably possible**.

Normal correction budget:

```text
R1 = Integrated Delivery
R2 = Targeted Corrections only if real evidence requires them
R3 = Final Verification & Closure
```

If R1 is clean, skip R2 and go directly to closure.
Do not create micro-rounds.

---

# 1. Objective

Implement and validate the third Post-V5 milestone:

> **Generate structured visual projections from persisted deterministic knowledge, with traceability, explicit epistemic status, and deterministic rendering.**

Target architecture:

```text
Persisted Evidence
    ↓
Structured visual model
    ↓
Validation
    ↓
Deterministic renderer
    ↓
SVG / PNG / embeddable HTML assets
```

Optional AI contribution may enrich the **structured model**, but AI must never draw free-form diagrams that bypass validation.

Permanent rule:

> AI may propose structure; deterministic code validates and renders.

H3 must NOT invent business relationships that are not supported.

---

# 2. Read first

Read actual current repository state before changing code.

At minimum:

```text
AGENTS.md
CLAUDE.md
PROJECT_STATE.json
README.md

docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
docs/POST_V5/LEGACYMAPPER_PRODUCT_PRINCIPLES.md
docs/POST_V5/H1_AI_ONLY_INTEGRATED_DELIVERY_RESULT.md
docs/POST_V5/H2_HUMAN_DOCUMENTATION_BY_AUDIENCE_RESULT.md

docs/V5/V5_OPERATIONS_GUIDE.md
```

Also inspect:

```text
documentation_v52
H2 audience projections
Evidence relationships
functional flows
projects / solutions
dependencies
data interactions
external dependencies
unresolved boundaries
AI proposals / canonical knowledge
consumer read API
```

Do not trust roadmap prose over current code.

---

# 3. First step: empirical inventory

Before designing diagram contracts, inspect real IST outputs and current H2 projections.

Use the persisted IST baseline and H2 sample if available:

```text
C:\PruebasLegacyMapper\V5_USER_ACCEPTANCE\outputs\IST_REAL_AI
C:\PruebasLegacyMapper\Resultados\post_v5_h2_human_review\
```

Measure which relationships are already reliable enough to visualize:

```text
solution → project
project → inferred layer
project → dependency
screen → project
flow → screen/entry point
flow → data operation
project → data object/operation
project → unresolved boundaries
external dependency classification
```

For each candidate relationship classify:

```text
SAFE_FOR_VISUALIZATION
SAFE_IF_LABELED_INFERRED
AI_ONLY_IF_LABELED
NOT_SAFE_YET
```

Do not implement a diagram type whose core relationships are not supported.

---

# 4. Structured visual model

Create one explicit machine-readable visual model contract.

Do not encode diagrams directly as SVG in business logic.

Suggested conceptual shape:

```text
VisualProjection
  id
  kind
  title
  audience
  scope
  nodes[]
  edges[]
  groups[]
  legend
  provenance[]
  unresolved[]
  metadata
```

Node fields should include at least:

```text
id
label
type
status
source_refs
metadata
```

Edge fields should include at least:

```text
source
target
relation
status
source_refs
label
```

Statuses must preserve project semantics:

```text
CONFIRMED
INFERRED
UNRESOLVED
AI_INTERPRETATION
CANONICAL
```

Every important edge must be traceable or explicitly marked as interpretation/inference.

---

# 5. Required diagram types for H3

Implement a minimal but useful set.

Mandatory:

```text
1. system-map
2. project-layer-map
3. dependency-map
4. observable-flow
5. data-interaction-map
```

Optional only if evidence supports them cleanly:

```text
use-case-map
external-integration-map
```

Do not implement dozens of diagram families.
Quality over breadth.

---

# 6. Diagram semantics

## 6.1 system-map

Shows high-level composition:

```text
System
→ Solutions/Areas
→ Projects
→ Main layers
```

Do not imply functional business grouping beyond known solution/project containment.

## 6.2 project-layer-map

Shows:

```text
Project
→ inferred/known layer
→ major neighboring projects
```

Layer inference must be visibly labeled as inferred.

## 6.3 dependency-map

Shows only supported project/library dependencies.

Differentiate:

```text
internal repository dependency
platform dependency
unclassified/external dependency
```

Do not treat unclassified as confirmed third-party.

## 6.4 observable-flow

Shows an evidence-backed observable flow:

```text
screen / entry point
→ event
→ project/component boundary
→ data operation
→ unresolved boundary if encountered
```

Do not turn technical flow into unsupported business intent.

## 6.5 data-interaction-map

Shows:

```text
project/screen
→ operation category
→ data object/procedure
```

May reuse H2 action categories:

```text
read
create
update
delete
mixed
unknown
```

---

# 7. Layout strategy

Use deterministic layout.

Preferred order:

```text
simple DAG/layered layout first
stable sorting by canonical IDs/labels
bounded node count
deterministic grouping
```

Do not rely on nondeterministic external layout engines unless seed/stability is proven.

If a layout library is already available, verify:

```text
same model → byte-identical or semantically identical output
```

If not, implement a simple internal deterministic layout sufficient for H3.
Avoid over-engineering.

---

# 8. Rendering

Required output:

```text
SVG
```

Optional if low-cost and architecture-consistent:

```text
PNG
small standalone HTML preview
```

SVG is primary because it is deterministic, portable, embeddable, vector, and suitable for H4 HTML/PDF.

Renderer must:

```text
escape labels safely
handle long names
wrap text
include legend
encode status visually
preserve readable ordering
avoid overlapping labels where practical
```

Do not use AI image generation for product diagrams.

---

# 9. Visual status language

Use a deterministic style system for epistemic status.

Example semantics:

```text
CONFIRMED         solid
INFERRED          dashed
UNRESOLVED        dotted / warning marker
AI_INTERPRETATION clearly distinct
CANONICAL         explicitly marked approved
```

Do not rely only on color.
Include labels/legend so diagrams remain understandable in grayscale/PDF/accessibility contexts.

---

# 10. Scope and size control

Large systems cannot be rendered as one giant graph.

Add deterministic limits and decomposition.

For example:

```text
system summary
→ one diagram per area/solution
→ one diagram per project
→ one diagram per selected flow
```

If node/edge count exceeds a threshold:

```text
split deterministically
or aggregate conservatively
```

Never silently drop relationships.

If something is omitted, record:

```text
partial = true
included_count
omitted_count
reason
```

---

# 11. CLI / UX

Prefer extending the H2 `docs` path or add one clear command consistent with current CLI.

Before choosing, inspect current CLI conventions.

Preferred possibilities:

```text
python main.py visuals <existing-output>
```

or:

```text
python main.py docs <existing-output> --visuals
```

Choose the smallest coherent public UX and document rationale.

The command must operate on **persisted output**, not require source re-analysis.
It must not invoke an AI provider by default.

---

# 12. AI relationship

H3 must work fully without AI.

If AI proposals or canonical knowledge exist:

```text
confirmed evidence remains primary
canonical knowledge may enrich labels/grouping if contract allows
unapproved AI interpretation may appear only when explicitly requested
```

Any AI-derived node/edge must remain `AI_INTERPRETATION` unless human-approved canonical knowledge already exists.

No auto-approval.
No auto-canonicalization.

---

# 13. Tests

Add focused tests covering at least:

```text
visual model schema/contract
stable node IDs
stable edge IDs
traceability refs
status propagation
system-map generation
project-layer-map generation
dependency-map generation
observable-flow generation
data-interaction-map generation
unresolved edge/node rendering
inferred layer visibly marked
AI interpretation never rendered as confirmed
large graph deterministic split/aggregation
SVG escaping
long labels
empty graph behavior
same input → byte-identical SVG
no source scan/analyzer
no provider calls
baseline unchanged
```

Run directed tests first.

Then:

```text
python -X utf8 -m unittest discover -s tests
```

Require:

```text
0 failures
0 errors
```

Record exact totals.

---

# 14. Real IST validation

Use the existing persisted IST baseline.
Do not rerun deterministic analysis.

Generate a representative visual package for:

```text
system level
slnPREPrevencion_2010
WebPREPrevencion
one dependency-heavy project/area
one data-heavy flow
one unresolved-heavy example
```

Measure:

```text
number of diagrams
generation time
largest SVG size
node/edge counts
split/partial diagrams
broken references
baseline deterministic delta
provider calls
source scan/analyzer invocations
```

Expected:

```text
provider calls = 0
source scan/analyzer = 0
baseline deterministic delta = 0
```

---

# 15. Human review sample

Create/refresh:

```text
C:\PruebasLegacyMapper\Resultados\post_v5_h3_visual_review\
```

Include at least:

```text
system-map.svg
project-layer-map.svg
dependency-map.svg
observable-flow.svg
data-interaction-map.svg
REVIEW_GUIDE.md
```

Use a consistent IST area, preferably `slnPREPrevencion_2010`, where possible.

The guide should ask:

```text
Can a non-technical reader understand the high-level map?
Can a functional reader follow the observable flow?
Can a technical reader understand project/layer/dependency structure?
Are inferred and unresolved relationships visibly distinct?
Does any edge imply more than the evidence proves?
```

Do not self-declare acceptance.

---

# 16. H4 readiness

H3 must leave outputs suitable for H4 embedding.

At minimum provide:

```text
stable SVG files
machine-readable visual model JSON
deterministic filenames
relative links/metadata
title/legend
```

Do NOT implement final H4 HTML/PDF packaging yet.

---

# 17. Documentation updates

Update only canonical docs needed:

```text
README.md if public command changes
docs/V5/V5_OPERATIONS_GUIDE.md or current operations guide
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
PROJECT_STATE.json
```

If H1/H2 remain marked `CLOSED_PENDING_COMMIT`, synchronize state before final H3 closure if they have already been committed.

---

# 18. Result document

Create:

```text
docs/POST_V5/H3_STRUCTURED_VISUAL_PROJECTIONS_RESULT.md
```

Include:

```text
empirical relationship inventory
visual model contract
diagram types implemented
renderer design
layout strategy
status/legend semantics
files changed
small validation
IST validation
human-review sample path
directed tests
full suite totals
baseline delta
provider calls
known limitations
debt introduced
Git status
recommendation
```

Final state must be exactly one of:

```text
H3_READY_FOR_HUMAN_REVIEW
H3_TARGETED_CORRECTION_REQUIRED
H3_BLOCKED
H3_OPEN_DECISION
```

---

# 19. Product state after successful H3

If validation is clean:

```text
H1 = CLOSED
H2 = CLOSED
H3_STRUCTURED_VISUAL_PROJECTIONS = IMPLEMENTED_AND_VALIDATED
NEXT = H4_FINAL_HUMAN_DELIVERABLES
```

Do not start H4 in this round.
Do not call this V6.

---

# 20. Non-goals

Do not implement:

```text
H4 final HTML/PDF package
H5 final audience acceptance
AI free-form diagram generation
new provider
new Evidence schema unless strictly unavoidable
third technology
Plugin Runtime
consumer write API
large refactor
V6
```

---

# 21. Git authority

For H3 Integrated Delivery:

```text
edit production code = YES
edit tests = YES
edit documentation/state = YES

commit = NO
push = NO
tag = NO
```

Leave all H3 changes in working tree for human review.

---

# 22. Stop conditions

Stop and report `H3_OPEN_DECISION` if:

```text
required relationships are not available with reliable provenance
diagram rendering would require guessing missing relationships
deterministic layout cannot be achieved with current approach
H3 would require redesigning Evidence Core
H3 would require H4 packaging to be implemented first
```

Report the smallest concrete decision required.

---

# 23. Acceptance criterion

H3 is successful when LegacyMapper can take a valid persisted baseline and generate deterministic, traceable, human-readable visual projections that:

```text
show only supported relationships
distinguish confirmed/inferred/unresolved/AI/canonical states
do not require source re-analysis
do not require AI
remain suitable for later HTML/PDF embedding
```

and the same input reproduces the same structured model and SVG output.
