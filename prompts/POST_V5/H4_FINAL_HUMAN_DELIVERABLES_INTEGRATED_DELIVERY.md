# LegacyMapper Post-V5 — H4 Integrated Delivery
## Final Human Deliverables

### Execution model

Complete H4 in **one integrated round whenever reasonably possible**.

Default round model:

```text
R1 = Integrated Delivery
R2 = Targeted Corrections only if real evidence requires them
R3 = Final Verification & Closure
```

If R1 is clean, skip R2 and go directly to closure.

Do not create micro-rounds.

---

# 1. Objective

Implement the fourth Post-V5 milestone:

> **Package the human-facing knowledge produced by H2 and the structured visuals produced by H3 into final, navigable human deliverables.**

Primary output:

```text
interactive/navigable HTML
```

Secondary output:

```text
PDF
```

Supporting visual assets:

```text
SVG
PNG only if genuinely needed
```

H4 is about **presentation and packaging**, not new semantic inference.

Permanent rule:

> H2 supplies the human narrative.
> H3 supplies the structured visual projections.
> H4 composes them into usable final deliverables without changing their truth.

Do not invent new business meaning.

---

# 2. Read first

Read actual current repository state before implementation.

At minimum:

```text
AGENTS.md
CLAUDE.md
PROJECT_STATE.json
README.md

docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
docs/POST_V5/LEGACYMAPPER_PRODUCT_PRINCIPLES.md
docs/POST_V5/H2_HUMAN_DOCUMENTATION_BY_AUDIENCE_RESULT.md
docs/POST_V5/H3_STRUCTURED_VISUAL_PROJECTIONS_RESULT.md

docs/V5/V5_OPERATIONS_GUIDE.md
```

Inspect current H2/H3 outputs and contracts:

```text
documentation_v52/executive
documentation_v52/functional
documentation_v52/technical_overview

visuals/
VISUALS_MANIFEST.json
visual model JSON
SVG assets
```

Use current code as authority over roadmap prose.

Before H4 implementation, synchronize obvious H3 closure state if needed:

```text
H3 = CLOSED
H3 human review = APPROVED
NEXT = H4_FINAL_HUMAN_DELIVERABLES
```

This synchronization is documentation/state hygiene only; do not reopen H3.

---

# 3. Required final deliverables

H4 must produce, at minimum, these human deliverables:

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

Important:

Some of these names are **delivery surfaces**, not promises that all semantics already exist.

Where the underlying evidence does not support a rich business artifact, the deliverable must explicitly say so.

Examples:

```text
USE_CASES
→ may contain "No confirmed business use cases can be derived from current evidence"
→ may link to observable flows instead
→ must not manufacture actors/goals

EXTERNAL_INTEGRATIONS
→ distinguish confirmed, inferred, unclassified, and unresolved dependencies
→ do not call an unclassified library an external integration
```

Never fill semantic gaps with guesses just to satisfy a filename.

---

# 4. Audience experience

The final package must support three human reading paths:

```text
Executive
Functional
Technical overview
```

Each should start from a landing page appropriate to that audience.

## Executive

Should answer quickly:

```text
What system is this?
How large/complex is it?
How is it organized at a high level?
What are the main areas/modules?
What data/integration characteristics are visible?
What remains unknown?
```

Avoid method/class/raw IDs by default.

## Functional

Should emphasize:

```text
areas/solutions
observable interactions
screens
data operations
business-purpose uncertainty
unresolved behavior
```

Do not revert to a raw screen/event/SP table as the primary experience.

## Technical overview

Should emphasize:

```text
projects
layers
dependencies
screens
data interactions
major flows
unresolved boundaries
```

Deep method/class detail stays reachable but is not the main H4 narrative.

---

# 5. Information architecture

Create one deterministic site/package structure.

Suggested:

```text
index.html
executive/
functional/
technical/
deliverables/
visuals/
assets/
manifest.json
```

Prefer clear navigation over clever UI.

At minimum provide:

```text
Home
Executive
Functional
Technical
Deliverables
Unresolved
About evidence / labels
```

Cross-links should let the reader move:

```text
system → area → project → flow → data → unresolved
```

without opening source code.

---

# 6. HTML requirements

HTML is the primary deliverable.

Requirements:

```text
static
portable
works from local filesystem
no server required
no CDN
no external JavaScript dependency required for core use
relative links
deterministic filenames
UTF-8
print-friendly
accessible enough for keyboard/semantic reading
```

A small local JavaScript bundle is allowed only if it materially improves navigation and remains fully offline.

Preferred capabilities:

```text
collapsible sections
table of contents
search/filter if simple and local
SVG zoom/open-in-new-tab
breadcrumbs
audience switch
status legend
```

Do not build a frontend framework unless one already exists and is clearly justified.

Avoid SPA complexity.

---

# 7. Visual integration

Embed or link H3 SVGs deterministically.

For dense visuals:

```text
show summary diagram first
link to detail diagrams
offer open-full-size action
preserve title/legend
```

Do not rasterize SVG unless PDF tooling forces it.

Keep H3 status semantics visible:

```text
CONFIRMED
INFERRED
UNRESOLVED
AI_INTERPRETATION
CANONICAL
```

Do not restyle in a way that makes statuses harder to distinguish.

---

# 8. PDF requirements

PDF is secondary but must be usable.

Create at least:

```text
LegacyMapper_System_Overview.pdf
```

and, if architecture supports it cleanly, optionally audience-specific PDFs:

```text
LegacyMapper_Executive.pdf
LegacyMapper_Functional.pdf
LegacyMapper_Technical_Overview.pdf
```

The PDF must:

```text
render locally/offline
preserve headings
preserve visible status labels
include diagrams legibly
avoid clipped tables
avoid unreadably tiny full-system graphs
use summaries when diagrams are too dense
include page numbers / basic navigation if renderer supports it
```

If the repository already has a PDF generation path, reuse it.

If not, choose the smallest deterministic approach that works in the actual environment.

Do not make H4 depend on an internet browser service.

---

# 9. Deliverable semantics

## SYSTEM_OVERVIEW

Compose from H2 executive output + H3 system map.

## MODULE_MAP

Use only supported grouping:

```text
solution/area
project
inferred layer
```

Do not invent business modules.

If "module" is only safely represented by solution/project grouping, say so explicitly.

## FUNCTIONAL_AREAS

Use H2 area pages.

State clearly:

```text
area = solution
not confirmed business function
```

## USE_CASES

Do not manufacture them.

Allowed outcome:

```text
No confirmed use cases derivable from static evidence.
Observable flows are provided as the nearest evidence-backed representation.
```

If canonical human knowledge supports a use case, it may be shown as CANONICAL.

If an unapproved AI proposal suggests one, it must stay AI_INTERPRETATION.

## BUSINESS_FLOWS

Use H2 observable flows and H3 observable-flow diagrams.

Call them business flows only where actual evidence/canonical knowledge supports that name.

Otherwise use:

```text
observable flows
```

## ARCHITECTURE_OVERVIEW

Use project/layer/dependency views.

## PROJECT_LAYER_MAP

Use H3 project-layer-map and H2 technical overview.

## DATA_INTERACTIONS

Use H2 action categories + H3 data-interaction summary/detail maps.

## EXTERNAL_INTEGRATIONS

Distinguish:

```text
confirmed external
platform
unclassified
unresolved
```

Do not upgrade unknown libraries/services to confirmed integrations.

## KNOWN_UNRESOLVED_AREAS

Use H2 unresolved narrative and H3 unresolved visual cues.

This must remain prominent, not hidden at the end.

---

# 10. Epistemic status

Every final surface must preserve the project status model:

```text
CONFIRMED
INFERRED
UNRESOLVED
AI_INTERPRETATION
CANONICAL
```

Use one shared legend.

Critical rule:

> Presentation may simplify wording, but it may not strengthen certainty.

Do not convert:

```text
INFERRED → CONFIRMED
AI_INTERPRETATION → CONFIRMED
UNRESOLVED → absence
```

---

# 11. AI/canonical overlay

H4 must work with no AI run.

Optional AI/canonical content may be rendered only through the existing H2/H3 contracts.

Rules:

```text
unapproved AI remains visibly separate
canonical remains explicitly approved
rejected proposals are not rendered
no provider call during H4 generation
```

No new AI inference is needed for packaging.

---

# 12. CLI / UX

Inspect current CLI conventions before deciding.

Preferred public UX:

```text
python main.py deliver <existing-output>
```

or another single clear command if current conventions strongly favor it.

The command should:

```text
take persisted output as input
optionally consume audience docs and visuals already generated
or generate projections deterministically from persisted output if those are absent
never require source re-analysis
never call provider
support --output
support audience selection if low-cost
```

Avoid forcing the user to manually run many internal commands unless required by architecture.

If H4 orchestrates H2 + H3 generation internally, it must still use persisted baseline only.

---

# 13. Packaging manifest

Produce a deterministic final package manifest.

Suggested:

```text
DELIVERABLES_MANIFEST.json
```

Include at least:

```text
contract/version
baseline identity
baseline analyzer version/fingerprint
generated profiles
generated deliverables
visual package references
file hashes
relative paths
epistemic legend version
provider calls
source scan/analyzer invocation count
partial/aggregated visual count
```

No timestamps if they break determinism unless existing contract requires them.

---

# 14. Determinism

Same input/options must produce the same package bytes wherever reasonably expected.

Test:

```text
same baseline
same audience selections
same visuals
same options
→ byte-identical HTML/manifest/assets
```

If PDF bytes cannot be stable because of unavoidable renderer metadata, require at least:

```text
stable content hash after normalized metadata
or
semantic equivalence with deterministic HTML source
```

Document exact behavior honestly.

Do not fake PDF byte determinism if the toolchain cannot provide it.

---

# 15. Tests

Add focused tests for at least:

```text
package contract
HTML generation
relative links
no broken navigation
audience landing pages
all required deliverable surfaces exist
USE_CASES does not invent content
EXTERNAL_INTEGRATIONS does not upgrade unclassified dependencies
statuses preserved
AI never promoted to confirmed
canonical labeled distinctly
unresolved remains visible
visual assets resolve
summary → detail links resolve
offline/local-file behavior
HTML escaping
long labels
empty/missing optional sections
same input → byte-identical HTML/package manifest
PDF generation smoke test
no provider calls
no source scanner/analyzer
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

# 16. Real IST validation

Use the persisted IST baseline.

Do not rerun deterministic analysis.

Recommended source:

```text
C:\PruebasLegacyMapper\V5_USER_ACCEPTANCE\outputs\IST_REAL_AI
```

Generate a full H4 package.

Validate:

```text
HTML file count
PDF file count
SVG/assets count
package size
generation time
broken links
missing referenced visuals
largest HTML page
largest PDF
partial/aggregated visual count
provider calls
scanner/analyzer invocations
baseline delta
```

Expected:

```text
provider calls = 0
scanner/analyzer = 0
baseline delta = 0
broken links = 0
```

---

# 17. Human review sample

Create:

```text
C:\PruebasLegacyMapper\Resultados\post_v5_h4_final_deliverables_review\
```

Include:

```text
full HTML package
PDF(s)
REVIEW_GUIDE.md
```

Use the same representative IST area where useful:

```text
slnPREPrevencion_2010
```

Review guide questions:

```text
1. Can a non-technical person understand the system without opening code?
2. Can a functional analyst find observable flows, screens, data and unresolved behavior?
3. Can a technical reader understand projects, layers, dependencies and data interactions?
4. Are inferred / unresolved / AI / canonical states obvious?
5. Are the main diagrams readable and easy to navigate?
6. Are unsupported use cases/business meanings avoided?
7. Can the package be opened offline from disk?
8. Is the PDF readable without clipped or microscopic diagrams?
```

Do not self-declare final user acceptance; H5 owns final validation/closure.

---

# 18. Documentation/state updates

Update:

```text
README.md
docs/V5/V5_OPERATIONS_GUIDE.md or current operations guide
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
PROJECT_STATE.json
```

After successful H4:

```text
H1 = CLOSED
H2 = CLOSED
H3 = CLOSED
H4_FINAL_HUMAN_DELIVERABLES = IMPLEMENTED_AND_VALIDATED
NEXT = H5_REAL_IST_VALIDATION_AND_CLOSURE
```

Do not start H5.

Roadmap hygiene:

```text
HX-01 = resolved by H2+H3+H4, pending H5 acceptance
HX-02 = resolved by H4 if HTML/PDF delivered
HX-03 = resolved by H3
```

---

# 19. Result document

Create:

```text
docs/POST_V5/H4_FINAL_HUMAN_DELIVERABLES_RESULT.md
```

Include:

```text
architecture
CLI
final package structure
deliverables implemented
HTML behavior
PDF behavior
epistemic-status handling
visual integration
tests
IST validation
determinism behavior
human review sample path
known limitations
debt introduced
Git status
recommendation
```

Final state exactly one of:

```text
H4_READY_FOR_HUMAN_REVIEW
H4_TARGETED_CORRECTION_REQUIRED
H4_BLOCKED
H4_OPEN_DECISION
```

---

# 20. Non-goals

Do not implement:

```text
H5 final acceptance/closure
new semantic inference
new business grouping
free-form AI documentation
new provider
Evidence redesign
adapter expansion
Plugin Runtime
consumer writes
third technology
V6
```

---

# 21. Git authority

For H4 Integrated Delivery:

```text
edit production code = YES
edit tests = YES
edit docs/state = YES

commit = NO
push = NO
tag = NO
```

Leave all accumulated Post-V5 changes in the working tree for human review.

---

# 22. Stop conditions

Stop as `H4_OPEN_DECISION` if:

```text
PDF generation requires a non-portable or unavailable dependency with no acceptable deterministic alternative
required deliverable semantics would require inventing unsupported business meaning
H4 would require redesigning Evidence/H2/H3 contracts
offline HTML cannot be produced without a major frontend stack
```

Report the smallest concrete decision needed.

---

# 23. Acceptance criterion

H4 succeeds when LegacyMapper can take a valid persisted baseline and generate a portable, offline human package in which:

```text
HTML is the primary navigable experience
PDF is a usable secondary artifact
H2 narrative and H3 visuals are integrated
required deliverable surfaces exist
unsupported semantics remain explicitly unresolved
all important claims retain traceability/status
no source code re-analysis is required
no provider call is required
```

and the package is ready for H5 real-world validation and final closure.
