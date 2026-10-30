# LegacyMapper Post-V5 — H4 Final Human Layout and Overflow Polish

## Objective

Perform a final **layout/readability polish** on the human documentation.

This is presentation-only.

Do not change:
- Evidence semantics
- AI interpretation semantics
- project/view relationships
- technical routes
- AI knowledge contracts
- packaging structure
- scanner/analyzer behavior

Do not start H5.
Do not close H4 automatically.

The owner has explicitly approved the overall direction:

```text
RUN_ALL.cmd experience = good
human / ai / internal structure = good
diagrams = useful
wireframes = useful
human content direction = good
```

The remaining issue is visual containment:

> Some diagrams, tables and technical blocks still exceed margins or feel cramped.

The goal of this round is:

> **Everything must fit cleanly within its page/container while remaining readable.**

---

# 1. Current product principles

Preserve:

```text
human\
ai\
internal\
```

Preserve the latest human-documentation separation rules:

```text
human = interpretation
ai/internal = evidence/provenance
```

Preserve:

```text
Confirmado
Inferido
No resuelto
```

as visually distinct states.

Preserve the single introductory AI interpretation notice.

Do not reintroduce:

```text
EP-*
FLOW-*
src:file:line
Base de las afirmaciones
repeated IA badges
raw provenance
```

into human output.

---

# 2. Main visual rule

Apply this globally:

> **No diagram, wireframe, table, code/route block, badge, card or text container may exceed the usable width of the HTML container or PDF page.**

This applies to:

```text
HTML
LegacyMapper.pdf
executive.pdf
```

No horizontal clipping.
No elements outside page bounds.
No text hidden under page edges.
No overflow beyond visible container.

---

# 3. PDF containment strategy

For wide visual content, apply this priority order:

```text
1. Fit within usable page width at readable size.
2. Reflow labels/content.
3. Rebalance columns.
4. Use compact but readable typography.
5. Use landscape page for genuinely wide content.
6. Split only at logical boundaries.
```

Do not solve overflow by:

```text
arbitrary clipping
extremely small text
vertical character stacking
cutting a diagram mid-node
cutting a route mid-step
```

---

# 4. Diagram rules

For all generated diagrams:

```text
system map
project map
dependency map
observable flow
data interaction map
behavior flow diagrams
```

ensure:

```text
viewBox matches content
no node crosses SVG bounds
no label crosses node bounds
no text exceeds page/container
adequate padding around edge nodes
arrows remain visible
long labels wrap deterministically
```

When embedded into PDF:

```text
respect printable width
keep aspect ratio
center diagram
use landscape if readability would otherwise be lost
```

Do not stretch/distort SVGs.

---

# 5. Wireframe rules

Keep the current good wireframe behavior.

Ensure:

```text
all controls inside wireframe bounds
horizontal labels
no clipped labels
no control overlaps
no controls outside page
no screenshot-like pixel obsession
```

If a wireframe is wider than available width:

```text
rebalance regions
reduce empty spacing
shorten only presentation labels safely
scale proportionally
```

Do not modify raw semantic control identity.

---

# 6. Tables

Wide human tables must not overflow.

For PDF:

Prefer:

```text
fewer columns
shorter human labels
wrapped cell text
reasonable column weighting
landscape page when needed
```

Do not shrink all text just to keep too many columns.

If a table remains too wide:

```text
split it into two meaningful tables
```

Example:

Instead of:

```text
Vista | Título | Propósito | Estado | Relación | Entrada | Salida | Datos | Procedimiento
```

prefer:

```text
Vista | Título | Qué hace | Uso observable
```

plus a separate technical-detail table when needed.

---

# 7. Technical route blocks

Routes such as:

```text
View
→ Event
→ Handler
→ Business Method
→ Cross-project Method
→ DAO
→ Stored Procedure
```

must remain readable.

For narrow pages:

```text
wrap at route-step boundaries
one semantic step per line if needed
indent continuation consistently
```

Never break inside symbol names unless unavoidable.

Do not reduce font below normal readable technical size.

---

# 8. Long identifiers

For identifiers such as:

```text
ucPreMantEmpadronamiento
PPRE_GES_JERARQUIA.TRAER_SUPERVISORES
fully-qualified class/method names
```

Use deterministic wrapping rules.

Preferred:

```text
wrap at:
.
/
\
_
namespace boundaries
route separators
```

Avoid character-by-character wrapping.

---

# 9. Status cards

For:

```text
Confirmado
Inferido
No resuelto
```

ensure cards:

```text
fit page/container
wrap paragraph text naturally
keep badge aligned
do not create excessive empty space
do not force fixed heights
```

Color should communicate state without harming print readability.

Use border + label, not color alone.

---

# 10. HTML responsive behavior

`human\index.html` must remain usable at common desktop widths.

Ensure:

```text
max-width container
responsive SVG width
overflow-safe tables
wrapping technical content
no body-level horizontal scrollbar caused by document content
```

For tables too wide for small screens:

```text
local horizontal scroll inside the table container
```

is acceptable.

Do not make the entire page horizontally scroll.

---

# 11. PDF page layout

General PDF rules:

```text
consistent margins
no content in margin area
no orphan section headings
no one-line continuation pages
avoid table header alone at bottom of page
avoid diagram title separated from its diagram
avoid route title separated from route body
```

If a diagram needs a dedicated page:

```text
give it a dedicated page
```

rather than forcing it into remaining space.

---

# 12. Executive PDF

Do not over-engineer the executive PDF.

Keep it:

```text
short
clean
high-level
visually calm
```

No large technical diagrams unless they materially improve understanding.

Ensure every table/diagram fits without scaling to unreadable size.

---

# 13. Main human PDF

The main PDF may remain more detailed.

Prioritize:

```text
readability
clear hierarchy
useful diagrams
functional explanation
technical routes
```

Do not prioritize density.

Whitespace is acceptable if it improves comprehension.

---

# 14. Representative review targets

At minimum inspect these representative views:

```text
ucPreMantJerarquia2
ucBusSuc
ucPreMantEmpadronamiento
ucPreEstadisticasAccidentes
ucPreConActxProd
```

Also inspect:

```text
solution-level diagram
project-level diagram
one dependency map
one data-interaction map
one long technical route
one wide catalog table
```

---

# 15. Automated visual guards

Add deterministic tests where practical for:

```text
SVG content stays within viewBox
no known vertical character stacks
no page-width overflow from rendered tables
no human HTML body-level horizontal overflow from generated components
no PDF block wider than usable page width according to renderer measurements
long route wrapping
long identifier wrapping
```

Do not attempt fragile pixel-perfect tests.

Test structural/layout invariants.

---

# 16. No semantic changes

This round must not change:

```text
ai/knowledge.json semantics
ai/provenance.json semantics
Evidence
confirmed/inferred/unresolved classification
technical routes
view relationships
stored procedures
human-confirmed domain knowledge
```

Presentation-only changes are allowed.

---

# 17. No new AI / no new analysis

For this task:

```text
provider calls = 0
scanner = 0
analyzer = 0
source reads = 0
Evidence rebuild = 0
```

Reuse:

```text
existing baseline
existing persisted AI responses
existing knowledge model
```

---

# 18. Regeneration

Use the current final-validation environment:

```text
C:\PruebasLegacyMapper\FinalValidation\
```

Do not rerun:

```text
01_ANALYZE_ONCE
02_INTERPRET_WITH_AI
```

Regenerate only the current presentation/package stages equivalent to:

```text
03_GENERATE_HUMAN_KNOWLEDGE
04_GENERATE_AI_KNOWLEDGE
05_PACKAGE_FINAL_OUTPUT
06_COLLECT_REVIEW_FILES
```

Use a new run/output directory so the previous review remains available.

Suggested:

```text
C:\PruebasLegacyMapper\FinalValidation\runs\manual_final_layout_polish\
```

---

# 19. Human review output

The owner should inspect only:

```text
package\human\index.html
package\human\LegacyMapper.pdf
package\human\executive.pdf
```

Optional:

```text
one or two representative SVG files
```

No need to inspect internal diagnostics unless a defect is found.

---

# 20. Tests

During implementation:

```text
targeted tests only
```

Once stable:

```text
python -X utf8 -m unittest discover -s tests
```

Run full suite once.

Required:

```text
0 failures
0 errors
```

---

# 21. Result report

Create:

```text
docs/POST_V5/H4_FINAL_HUMAN_LAYOUT_AND_OVERFLOW_POLISH_RESULT.md
```

Include:

```text
layout rules changed
diagram scaling changes
table wrapping changes
technical route wrapping changes
HTML overflow handling
PDF overflow handling
representative views inspected
provider calls
scanner/analyzer/source-read proof
targeted tests
full suite result
review path
```

---

# 22. Final state

If successful:

```text
H4_FINAL_HUMAN_LAYOUT_AND_OVERFLOW_POLISH = READY_FOR_HUMAN_APPROVAL
H4 = HUMAN_APPROVAL_PENDING
H5 = NOT_STARTED
```

Do not close H4 automatically.

---

# 23. Git authority

For this task:

```text
presentation edits = YES
tests = YES
docs/state draft updates = YES
provider calls = NO
scanner/analyzer rerun = NO
commit = NO
push = NO
tag = NO
```

Do not commit, push or tag without explicit human authorization.

---

# Final principles

> **Readable beats dense.**

> **Nothing may escape the page or container.**

> **Scale, reflow or split at logical boundaries — never clip.**

> **Diagrams and wireframes are valuable and must remain.**

> **This is a presentation polish, not a semantic redesign.**
