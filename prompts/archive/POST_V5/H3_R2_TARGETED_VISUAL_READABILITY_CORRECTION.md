# LegacyMapper Post-V5 — H3-R2 Targeted Correction
## Visual Readability: Layout + Decomposition Only

### Purpose

H3 architecture is accepted.

Human review of the real SVG sample found:

```text
system-map             = PASS
project-layer-map      = PASS
observable-flow        = PASS_WITH_READABILITY_OBSERVATION
dependency-map         = PARTIAL
data-interaction-map   = PARTIAL
```

This round corrects **visual readability only**.

Do NOT redesign H3.
Do NOT change Evidence.
Do NOT add new diagram kinds.
Do NOT start H4.

---

# 1. Read first

Read current repository state and H3 artifacts:

```text
AGENTS.md
CLAUDE.md
PROJECT_STATE.json

docs/POST_V5/H3_STRUCTURED_VISUAL_PROJECTIONS_RESULT.md
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md

C:\PruebasLegacyMapper\Resultados\post_v5_h3_visual_review\REVIEW_GUIDE.md
```

Inspect the actual reviewed SVGs:

```text
system-map.svg
project-layer-map.svg
dependency-map.svg
observable-flow.svg
data-interaction-map.svg
```

Preserve:

```text
system-map             = accepted
project-layer-map      = accepted
observable-flow        = semantically accepted
dependency-map         = readability correction required
data-interaction-map   = readability correction required
```

---

# 2. Scope

Allowed:

```text
layout.py
svg renderer only where required for readability
diagram decomposition / deterministic splitting
manifest/package metadata required by decomposition
tests
docs/state
```

Not allowed:

```text
Evidence schema changes
analyzer changes
adapter changes
AI/provider changes
new diagram families
business inference
H4 HTML/PDF packaging
large refactor
V6
```

---

# 3. Main objective

Improve readability for dense diagrams while preserving:

```text
same semantic relationships
same source_refs
same epistemic statuses
same deterministic behavior
same model validation guarantees
no silent omission
```

The solution should prefer **decomposition over clever line routing**.

Do not spend the round building a general graph-layout engine.

---

# 4. Dependency map correction

Current problem:

> Dense dependency diagrams become visually tangled because many edges cross and many nodes converge.

Target behavior:

```text
summary dependency map
→ deterministic project-focused submaps when density exceeds threshold
```

Preferred strategy:

```text
1. keep one high-level summary map
2. for dense areas/projects, generate deterministic submaps
3. one focal project or small project group per submap
4. show direct dependencies and optionally one-hop reverse dependencies
5. preserve dependency category:
   - internal repository
   - platform
   - unclassified / unresolved nature
6. link/map metadata between summary and detail diagrams
```

Do not repeat dozens of visually overlapping `uses` labels if relation meaning is already explained in the legend.

If edge labels are identical, prefer legend + minimal edge labeling.

---

# 5. Data interaction map correction

Current problem:

> The semantic grouping is useful, but many screen → data-operation edges create heavy visual crossing.

Target behavior:

```text
summary-map
→ category/project/screen-group detail maps
```

Preferred deterministic decomposition:

```text
summary:
  project/screen groups
  → read/create/update/delete/mixed/unknown groups
  → counts

details:
  one action category or bounded screen subset
  → concrete operations
```

Requirements:

```text
same underlying relations
technical operations remain traceable
action category remains INFERRED where applicable
no business meaning introduced
no relation silently removed
```

If the summary aggregates many relations, metadata/JSON must retain exact included/omitted members.

---

# 6. Observable flow correction

Semantics are accepted.

Problem:

> Long flows can become excessively horizontal.

Apply only a bounded layout improvement.

Preferred options:

```text
row/band wrapping after a deterministic depth threshold
or
sectioned continuation blocks
```

Requirements:

```text
logical execution order remains obvious
edge direction remains unambiguous
source_refs/statuses unchanged
same flow does not become visually reordered in a misleading way
```

Do not turn flow layout into a general free-positioning problem.

---

# 7. Deterministic decomposition contract

When a diagram is split:

```text
parent diagram
child diagrams
stable filenames
stable ordering
explicit parent/child metadata
```

Recommended metadata:

```text
projection_id
parent_projection_id
part_index
part_count
scope
included_count
omitted_count
aggregation_reason
```

If current model already has equivalent fields, reuse them.

Do not create duplicate contracts unnecessarily.

---

# 8. Partial vs decomposed

Do not misuse `partial`.

Use:

```text
partial = true
```

only when a single rendered projection intentionally aggregates/omits concrete nodes from that specific view.

For deterministic decomposition into child diagrams where full detail exists across the package, record that separately from “information not represented anywhere”.

The package must make clear:

```text
summary is aggregated
details contain expanded relationships
nothing silently discarded
```

---

# 9. Layout rules

Preserve deterministic ordering.

Prefer:

```text
stable node ordering
bounded width
bounded column count
group-local routing
orthogonal/simple routing where practical
shared relation labels in legend
```

Avoid:

```text
force-directed nondeterminism
random seeds
layout depending on filesystem enumeration order
external web/runtime dependencies
```

Same model/package input must reproduce byte-identical SVGs where current conventions require it.

---

# 10. Visual readability rules

Improve:

```text
edge crossing count
label collisions
long horizontal canvases
visual density
```

without sacrificing traceability.

Where useful:

```text
increase vertical spacing
bundle visually equivalent edges only when exact member metadata remains available
move repeated relation wording into legend
use grouped boxes
show counts in summary nodes
```

Do not rely only on color.

Keep existing status patterns/text.

---

# 11. Tests

Add focused tests covering at least:

```text
dense dependency graph decomposes deterministically
dependency summary + detail preserve all original relationships
dense data-interaction graph decomposes deterministically
summary counts equal detailed relationship totals
no relationship disappears across decomposition
parent/child metadata stable
stable filenames/order
observable-flow wrapping preserves logical order
same input → byte-identical outputs
system-map unchanged
project-layer-map unchanged
status semantics unchanged
source_refs unchanged
AI interpretation never strengthened
unresolved remains unresolved
no provider calls
no source scan/analyzer
baseline unchanged
```

Run directed H3/H3-R2 tests first.

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

# 12. Real IST validation

Reuse the existing persisted IST baseline.

Do not rerun deterministic analysis.

Regenerate the same human-review sample:

```text
C:\PruebasLegacyMapper\Resultados\post_v5_h3_visual_review\
```

At minimum regenerate:

```text
dependency-map.svg
data-interaction-map.svg
observable-flow.svg
```

plus any new deterministic child SVGs/details.

Also verify:

```text
system-map.svg byte-identical or semantically unchanged
project-layer-map.svg byte-identical or semantically unchanged
```

Measure before/after:

```text
canvas width/height
node count
edge count
diagram count
number of child diagrams
largest SVG size
partial/aggregated diagrams
broken refs
baseline delta
provider calls
scanner/analyzer invocations
```

If practical, record a simple visual-density metric such as:

```text
edges per visible node
maximum outgoing edges per rendered panel
```

Do not invent a fake crossing metric if one is not actually measured.

---

# 13. Human review sample

Refresh `REVIEW_GUIDE.md`.

Ask specifically:

```text
1. Can a reviewer follow a dependency from a project to its targets without tracing through a dense tangle?
2. Can a functional reviewer understand the data-interaction summary before opening detail maps?
3. Does the observable flow fit a normal browser viewport better?
4. Are confirmed/inferred/unresolved states still obvious?
5. Is any relationship missing or represented more strongly than Evidence supports?
```

Do not self-declare human acceptance.

---

# 14. Documentation/state

Update:

```text
docs/POST_V5/H3_STRUCTURED_VISUAL_PROJECTIONS_RESULT.md
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
PROJECT_STATE.json
```

Fix current roadmap hygiene while here:

```text
HX-03 = RESOLVED_BY_H3
HX-01 = partially resolved by H2 + H3, final packaging pending H4
```

Do not reopen H1/H2.

---

# 15. Result section

Append to the existing H3 result:

```text
H3-R2 Targeted Visual Readability Correction
```

Include:

```text
human-review finding
exact layout/decomposition changes
before/after measurements
diagrams generated
relationship preservation checks
IST validation
tests
baseline delta
provider calls
known limitations
sample path
Git status
recommendation
```

Final state must be exactly one of:

```text
H3_READY_FOR_FINAL_HUMAN_REVIEW
H3_TARGETED_CORRECTION_REQUIRED
H3_BLOCKED
H3_OPEN_DECISION
```

---

# 16. Git authority

For H3-R2:

```text
edit production code = YES, layout/decomposition scope only
edit tests = YES
edit docs/state = YES

commit = NO
push = NO
tag = NO
```

Leave all accumulated H1–H3 changes in the working tree.

---

# 17. Success criterion

H3-R2 succeeds when:

```text
dependency-map is understandable without tracing a dense tangle
data-interaction-map provides a readable summary with bounded detail maps
observable-flow is less excessively horizontal
all relationships remain traceable
no relationship is silently lost
statuses remain correct
same input remains deterministic
baseline remains unchanged
provider calls = 0
source re-analysis = 0
```

At that point H3 can move to final human confirmation and then H4.
