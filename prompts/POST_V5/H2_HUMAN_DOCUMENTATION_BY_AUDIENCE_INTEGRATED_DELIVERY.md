# LegacyMapper Post-V5 — H2 Integrated Delivery
## Human Documentation by Audience

### Execution model
Complete this milestone in one integrated round whenever reasonably possible.

Normal correction budget:

```text
R1 = Integrated Delivery
R2 = Targeted Corrections only if real evidence requires them
R3 = Final Verification & Closure
```

If R1 is clean, skip R2 and go directly to closure.
Do not create micro-rounds.

---

## 1. Objective

Implement and validate the second Post-V5 milestone:

> Generate human-centered documentation at the right abstraction level for different audiences, while preserving deterministic truth, provenance, unresolved information and explicit separation between facts and AI interpretation.

H2 must provide three audience profiles:

```text
executive
functional
technical-overview
```

Primary goal:

> A person should be able to understand what a system/module does, how it is organized, and how its main flows connect without opening source code.

Permanent principles:

```text
Python discovers and validates; AI interprets.
Correct is not enough; documentation must be understandable.
Proposal != canonical.
Unresolved stays unresolved.
Analyze once, project many.
```

H2 is NOT about deeper class/method documentation.

---

## 2. Read first

Read actual current repository state before modifying anything.

At minimum:

```text
AGENTS.md
CLAUDE.md
PROJECT_STATE.json
README.md

docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
docs/POST_V5/LEGACYMAPPER_PRODUCT_PRINCIPLES.md
docs/POST_V5/H1_AI_ONLY_INTEGRATED_DELIVERY_RESULT.md
docs/POST_V5/H1_AI_ONLY_INVENTORY.json

docs/V5/V5_OPERATIONS_GUIDE.md

docs/continuity/LEGACYMAPPER_V5_ROADMAP.md
docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md
docs/continuity/LEGACYMAPPER_LESSONS_LEARNED.md
```

Also inspect actual implementation of:

```text
legacy_documenter/documentation_v52/
AudienceTransformer
profiles/config/templates/renderers
general/
developer/
consumer_projection
Evidence persistence
canonical knowledge
AI proposal/review output
```

Do not trust old summaries over current code.

---

## 3. Empirical baseline first

Before redesigning documentation, inspect real current outputs.

Use, if available:

```text
C:\PruebasLegacyMapper\V5_USER_ACCEPTANCE\outputs\IST_REAL
```

and at least one smaller output.

Measure and document:

```text
current human docs structure
current general/developer profiles
document counts
average/large document sizes
navigation depth
where technical detail overwhelms meaning
where module/system summaries are missing
where functional language is weak
where project/layer ownership is already reliable
where provenance is exposed or hidden
where unresolved information appears
```

Select a representative human-review sample containing, where possible:

```text
system overview
one large module/project
one web/view-heavy area
one data-heavy area
one external-integration area
one unresolved/ambiguous area
```

Do not redesign from synthetic fixtures alone.

---

## 4. Audience contract

### 4.1 executive

Audience:

```text
manager
product owner
business stakeholder
non-technical reviewer
```

Primary questions:

```text
What is this system for?
What are its major areas/modules?
What are the main business capabilities?
What external systems/databases does it depend on?
What important uncertainties remain?
```

Avoid by default:

```text
method names
class inventories
raw call graphs
source paths
large ID lists
```

Technical facts may exist behind links/details, but must not dominate the narrative.

### 4.2 functional

Audience:

```text
business analyst
functional analyst
support analyst
domain expert
QA
```

Primary questions:

```text
What functional areas exist?
What use cases/processes are observable?
What screens/views participate?
What are the important business flows?
What data is read/changed?
What external integrations participate?
Where are unresolved boundaries?
```

Prefer language such as:

```text
user starts...
system validates...
system reads...
system updates...
system sends...
process ends...
```

Do not invent business intent when evidence only proves technical behavior.

### 4.3 technical-overview

Audience:

```text
architect
developer new to the system
technical lead
maintainer
```

Primary questions:

```text
How is the system organized?
Which projects/modules/layers exist?
Which views/screens belong where?
What are the main dependencies?
Where does data access happen?
Which external integrations exist?
How do major flows cross project/layer boundaries?
```

Surface-level technical view only.
Detailed classes/methods remain supporting evidence, not the default story.

---

## 5. Common information architecture

All three profiles must project from the same underlying truth.

Preferred semantic hierarchy:

```text
System
  ↓
Functional Areas / Modules
  ↓
Projects / Layers
  ↓
Views / Screens / Entry Points
  ↓
Use Cases / Business Flows
  ↓
Data Interactions
  ↓
External Integrations
  ↓
Known Unresolved Areas
```

Do not force entities into a hierarchy unless Evidence supports that relationship.

If module/functional-area identity is not deterministic, represent it as:

```text
INFERRED
AI_INTERPRETATION
UNRESOLVED
```

according to the real source of the conclusion.

---

## 6. Fact / interpretation labeling

Human-facing docs must make epistemic status visible but not noisy.

Supported statuses should map to current project semantics:

```text
CONFIRMED
INFERRED
UNRESOLVED
AI_INTERPRETATION
CANONICAL
```

Rules:

```text
deterministic Evidence → CONFIRMED
deterministic heuristic explicitly marked by current contracts → INFERRED
missing/ambiguous relation → UNRESOLVED
unapproved AI proposal → AI_INTERPRETATION
human-approved canonical knowledge → CANONICAL
```

Do not promote AI text to CONFIRMED.
Do not hide unresolved information merely to make documentation cleaner.

---

## 7. Relationship with H1 AI-only

H2 must work with the persisted baseline created by deterministic analysis.

It may consume:

```text
deterministic Evidence
existing AI context
AI-only proposals from H1
reviewed/canonical knowledge
```

with strict precedence:

```text
deterministic Evidence
> human-approved canonical knowledge
> explicitly labeled AI interpretation
```

If no AI run exists, H2 must still produce useful deterministic human documentation.

If AI proposals exist but are not approved, they may appear only in a clearly separated interpretation section or equivalent.

No automatic AI provider call should occur merely because human docs are generated.

---

## 8. Reuse existing documentation engine

Prefer extending the existing V5.2 architecture:

```text
Evidence
→ Audience Transformation
→ Profile
→ Template
→ Renderer
```

Do not build a parallel documentation engine unless current architecture makes extension impossible.

Minimize changes to:

```text
Evidence Core
analyzer
adapters
review
AI provider
```

H2 should primarily change projection/transformation/profile/template behavior.

---

## 9. Required human deliverables for H2

H2 does NOT yet implement final H4 packaging.

Each audience profile should expose, where Evidence supports them:

```text
System Overview
Functional Areas / Modules
Main Projects / Layers
Main Views / Screens
Main Business Flows / Use Cases
Data Interactions
External Integrations
Known Unresolved Areas
```

Do not create empty decorative sections when no evidence exists.

H3 handles structured visual diagrams.
H4 handles final HTML/PDF productization.

---

## 10. Navigation and readability

Documentation must be summary-first.

Preferred pattern:

```text
short overview
→ key facts
→ main relationships
→ unresolved/interpretation
→ links to deeper technical evidence
```

Avoid giant flat documents.

Where content is large:

```text
system index
→ module/area page
→ project/layer page
→ deeper evidence link
```

Navigation labels must be human-readable.

Stable IDs may remain in metadata/links, but should not dominate headings.

---

## 11. Language quality

The human documentation must avoid raw internal jargon when a clearer phrase exists.

Examples:

```text
EntryPoint → Punto de entrada
DataOperation → Interacción con datos
ExternalDependency → Integración / dependencia externa
UnresolvedBoundary → Área no resuelta
```

Do not change canonical schema names merely for presentation.
This is a projection concern.

Use Spanish as the default human-facing language unless current profile configuration explicitly says otherwise.

---

## 12. Tests

Add focused tests covering at least:

```text
three profiles exist
same Evidence produces three different abstraction levels
executive hides method/class detail by default
functional surfaces flows/screens/data/integrations
technical-overview surfaces projects/layers/dependencies
confirmed/inferred/unresolved statuses remain correct
AI proposal is never rendered as confirmed
canonical knowledge is distinguishable from raw AI proposal
docs work without any AI run
docs can optionally include H1 interpretation without provider invocation
navigation links resolve
no project/module ownership is invented
deterministic rerun is byte-identical where timestamps are excluded by existing conventions
```

Run directed tests first.

Then:

```text
python -m unittest discover -s tests
```

Expected:

```text
0 failures
0 errors
```

Record exact totals.

---

## 13. Human acceptance sample

Create a compact review sample from real IST.

Recommended location outside repo:

```text
C:\PruebasLegacyMapper\Resultados\post_v5_h2_human_review\
```

or repository-approved equivalent.

The sample must include all three audience profiles for the same representative area so a reviewer can compare them directly.

For each profile, answer:

```text
Can a non-technical reader understand this?
Can a functional reader understand the process?
Can a technical reader understand organization/dependencies?
Is anything stated more strongly than the evidence supports?
Is unresolved information visible?
```

Do not claim human acceptance yourself.
Prepare the material for human review.

---

## 14. Real IST validation

Run H2 against IST real or reuse a valid current deterministic IST baseline where architecture permits.

Do not re-run deterministic analysis unnecessarily.

Record:

```text
documents generated by profile
largest document sizes
generation time
broken links
empty/low-value sections
number of unresolved items surfaced
number of AI interpretation sections if applicable
baseline deterministic artifacts changed? must be NO if projecting from existing output
```

If generating documentation requires a fresh projection only, reuse persisted Evidence.

---

## 15. Quality gates

H2 is successful only if all are true:

```text
1. three audiences receive materially different views
2. docs remain grounded in Evidence
3. no AI proposal is promoted to fact
4. unresolved is preserved
5. non-technical content is meaningfully less technical
6. functional content emphasizes observable processes
7. technical-overview emphasizes system organization, not methods
8. existing deep technical evidence remains reachable
9. no source re-analysis is required merely to regenerate audience docs
10. full suite remains green
```

---

## 16. Documentation updates

Update only canonical docs needed:

```text
README.md if user-facing commands/output changed
docs/V5/V5_OPERATIONS_GUIDE.md or current operations guide
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
PROJECT_STATE.json after successful validation
```

If H1 roadmap still contains stale wording such as:

```text
AI-only = future capability
UX-02 = unresolved
command name candidates
```

correct it as documentation hygiene before closing H2, without reopening H1 implementation.

---

## 17. Result document

Create:

```text
docs/POST_V5/H2_HUMAN_DOCUMENTATION_BY_AUDIENCE_RESULT.md
```

Include:

```text
empirical baseline
audience contracts
architecture/reuse decisions
files changed
profiles implemented
fact/inference/AI labeling behavior
small validation
IST validation
human-review sample path
directed tests
full suite totals
known limitations
debt introduced
Git status
recommendation
```

Final state must be exactly one of:

```text
H2_READY_FOR_HUMAN_REVIEW
H2_TARGETED_CORRECTION_REQUIRED
H2_BLOCKED
H2_OPEN_DECISION
```

---

## 18. Product state after successful H2

If validation is clean, update state to equivalent of:

```text
H1_AI_ONLY = CLOSED
H2_HUMAN_DOCUMENTATION_BY_AUDIENCE = IMPLEMENTED_AND_VALIDATED
NEXT = H3_STRUCTURED_VISUAL_PROJECTIONS
```

Do not start H3.
Do not call this V6.

---

## 19. Non-goals

Do not implement:

```text
H3 diagram model/rendering
H4 final HTML/PDF product packaging
H5 final acceptance
third technology
Plugin Runtime
consumer CLI
new provider
deep method/class docs
large refactor
V6
```

---

## 20. Git authority

For H2 Integrated Delivery:

```text
edit production code = YES
edit tests = YES
edit documentation/state = YES

commit = NO
push = NO
tag = NO
```

Leave the working tree ready for human review.

---

## 21. Stop conditions

Stop and report H2_OPEN_DECISION instead of inventing if:

```text
module/functional-area grouping requires unsupported business inference
existing V5.2 architecture cannot support three profiles without breaking closed contracts
current Evidence is insufficient to distinguish project/layer ownership reliably
AI proposal/canonical precedence is ambiguous in current contracts
H2 would require H3 visual architecture to be implemented first
```

Report the smallest concrete decision required.

---

## 22. Acceptance criterion

H2 is successful when the same LegacyMapper baseline can generate three useful human views:

```text
executive
functional
technical-overview
```

and each tells the same evidence-backed truth at a different level of abstraction, without inventing facts, without hiding unresolved areas, and without requiring the reader to open source code to understand the system at that level.
