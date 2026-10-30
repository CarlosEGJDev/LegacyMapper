# LegacyMapper Post-V5 — Human Template Productization
## Generic Human Template + Readable PDF/HTML + Template Directories

### Status / rationale

H4-R5 validated the behavioral documentation concept and the AI interpretation contract on real IST, but human review identified productization work that must be completed before H4 can be considered ready for final acceptance.

This is **not H4-R6**. The five-round H4 correction limit remains respected.

Treat this as a **productization workstream for the approved behavioral documentation direction**, not another exploratory correction round.

Do not start H5.

---

# 1. Primary objective

Productize the human documentation pipeline so that:

```text
Evidence / behavioral context
→ AI structured interpretation
→ deterministic validation
→ human template
→ readable HTML / PDF
```

The human output must be easy to read and visually structured.

The AI must fill structured fields.
The AI must not freely design the final document.

Permanent principle:

> **The AI interprets and fills a validated template model. The renderer owns layout and presentation.**

---

# 2. Current technical debt to address

Treat the following as the active debt for this workstream.

## P0 — Human documentation productization

1. The current PDF/HTML repeats `Interpretación de IA — no aprobada` excessively.
2. Typography hierarchy is too weak:
   - title
   - section title
   - subsection title
   - body paragraph
   - technical note
   - evidence note
   must be visually distinct.
3. PDF/HTML needs a clearer table of contents and navigation.
4. Behavioral explanation must remain primary; raw inventory must remain appendix/navigation.
5. Each important view needs a simple box-flow diagram:
   - view
   - event/handler
   - class/business/service
   - DAO/repository
   - stored procedure / SQL
   - database/external boundary
6. UI reconstruction currently uses structure but not enough real styling.
7. Human documentation is not yet driven by a reusable template contract.
8. UI/navigation evidence is still read from source as read-only enrichment instead of persisted Evidence.
9. Cross-project BL calls remain unresolved for many views.
10. H4 roadmap/state wording must remain synchronized with human review.

## P1 — Existing Post-V5 debt still open

Preserve and do not accidentally conflate with this workstream:

```text
UX-01 full on nonexistent repository can return empty SUCCESS
UX-03 no consumer CLI
```

These are not blockers for this template work unless implementation touches them.

---

# 3. Template directories

Add an explicit template root to LegacyMapper.

Recommended repository structure:

```text
templates/
├── human/
│   ├── default/
│   │   ├── template.yaml
│   │   ├── document.html
│   │   ├── styles.css
│   │   ├── pdf.css
│   │   └── assets/
│   └── README.md
└── ai/
    └── README.md
```

For now:

```text
human = implemented
ai = reserved/documented only
```

Do not implement a generic AI prompt-template runtime yet unless already trivial and clearly required.

Template discovery should support at least:

```text
built-in repository templates
optional user template directory override
```

Recommended CLI shape if compatible with existing conventions:

```text
python main.py deliver <existing-output> --template human/default
```

and optionally:

```text
--template-dir <path>
```

Do not invent CLI syntax if current parser conventions strongly suggest a different equivalent.

---

# 4. Human template contract

Create a deterministic, versioned template contract.

Suggested:

```text
LegacyMapperHumanTemplate 1.0
```

The template should declare:

```text
template_id
template_version
audience
language
sections
styles
assets
required_fields
optional_fields
```

The renderer should fill fields from validated `BehavioralDocument` / `ViewExplanation`.

The template must never invoke AI directly.

---

# 5. Generic default human template

Create a first built-in generic template for behavioral documentation.

Reading order:

```text
Cover
AI interpretation notice
Table of contents
Solution
Project
Module decision / module summary if supported
Important views
Detailed view chapters
Cross-view behavior
Data/persistence
Observable usage / legacy uncertainty
Known unresolved areas
Appendix
```

The full view catalog belongs in the appendix or HTML navigation.

---

# 6. AI notice — once, not everywhere

Remove the long repeated label:

```text
Interpretación de IA — no aprobada
```

from every heading/subheading.

Instead:

## At the beginning

Show one prominent notice:

```text
This document contains AI-generated interpretations.
AI interpretation is not automatically approved or canonical.
Confirmed, inferred, unresolved and AI-generated content are distinguished visually.
```

## In the body

Use only a compact marker:

```text
IA
```

or a subtle visual style.

The underlying structured status remains:

```text
AI_INTERPRETATION
```

Do not weaken epistemic traceability.

---

# 7. Typography hierarchy

The default template must define a strong hierarchy.

At minimum:

```text
Document title
H1
H2
H3
Body
Caption
Technical detail
Evidence/source reference
Status badge
```

For PDF and HTML:

```text
Document title = largest
H1 = clearly smaller than title
H2 = clearly smaller than H1
H3 = clearly smaller than H2
Body = comfortable reading size
Evidence/source refs = smaller and visually secondary
```

Avoid having all text appear at nearly the same size/weight.

Do not hardcode presentation inside behavioral model objects.

Presentation belongs in template CSS/style rules.

---

# 8. Table of contents

Generate a deterministic TOC.

PDF:

```text
Solution
Project
Module structure
Views
each selected/detailed view
Cross-view behavior
Data/persistence
Unresolved
Appendix
```

HTML:

```text
sticky or clear TOC
anchor links
view-level navigation
```

Use stable anchors.

---

# 9. View chapter template

Each important view should render in this order:

```text
View title
One-line explanation
What it does / how it is used
Observable usage status
Approximate UI reconstruction
Simple technical flow diagram
Main actions
Data and persistence
Related classes
Incoming/outgoing views/popups
Messages
Known / inferred / unresolved
Technical evidence
```

Keep the simple explanation before technical details.

---

# 10. Simple box-flow diagram

Add a deterministic box diagram per important action/view where evidence exists.

Target:

```text
[View]
   ↓
[Event / Handler]
   ↓
[Business / Service Class]
   ↓
[DAO / Repository]
   ↓
[Stored Procedure / SQL]
   ↓
[Database / External Boundary]
```

Rules:

```text
only include nodes supported by evidence
skip missing architectural layers
show UNRESOLVED explicitly
preserve source_refs
no force layout
no complex routing
stable deterministic ordering
```

A view may have multiple important actions.

Prefer one overview diagram plus action-specific details if needed.

---

# 11. Style-aware UI reconstruction investigation

Before claiming visual fidelity, inspect what real styling assets exist for the IST project.

Measure:

```text
.aspx/.ascx markup
master pages
CSS files
inline styles
class attributes
themes/skins
images/icons
layout tables/divs
shared controls
JavaScript that changes visibility/layout
```

For selected pilot views, determine:

```text
how much of the original presentation can be reconstructed
which styles resolve
which assets resolve
which style dependencies are dynamic/unavailable
```

Classify reconstruction capability:

```text
STRUCTURE_ONLY
STYLE_PARTIAL
STYLE_HIGH_CONFIDENCE
```

Do not promise “90% fidelity” unless evidence supports it.

---

# 12. Improved UI reconstruction

If real CSS/master/theme evidence is available, enhance the documentary reconstruction.

Allowed:

```text
layout
spacing
font emphasis
borders
backgrounds
control dimensions
icons/images when local and evidenced
grouping/panels/tabs
```

Do not execute arbitrary legacy JavaScript.

Do not require running the legacy application.

Always label:

```text
DOCUMENTARY RECONSTRUCTION
NOT A PRODUCTION SCREENSHOT
```

If style fidelity is partial, say so.

---

# 13. AI filling rules

The AI fills structured behavioral fields only.

Do not let the AI emit arbitrary HTML/CSS/PDF layout.

Required flow:

```text
behavioral context
→ structured AI output
→ validation
→ sanitized behavioral model
→ template renderer
```

The validator remains responsible for:

```text
symbol existence
source_refs
usage classification
status preservation
no obsolete/dead claims without evidence
no fabricated procedures/classes/controls
```

---

# 14. Template safety

A user-provided human template may control layout, but not truth.

Template rendering must not be able to:

```text
promote AI_INTERPRETATION to CONFIRMED
hide UNRESOLVED in the data model
change source_refs
mutate baseline
invoke provider
execute arbitrary code
```

If template supports expressions, keep them declarative and bounded.

Prefer simple placeholders / loops / conditional sections.

---

# 15. Tests

Add focused tests for:

```text
template discovery
default human template loads
custom template directory loads
invalid template rejected
required fields validated
AI notice rendered once
AI status preserved in structured model
typography classes present
TOC anchors resolve
view chapter order
catalog in appendix
box-flow only uses evidenced nodes
unresolved layer shown explicitly
style-aware reconstruction never invents CSS/assets
no arbitrary template execution
deterministic rendering
```

If production code changes, run full suite:

```text
python -X utf8 -m unittest discover -s tests
```

Require:

```text
0 failures
0 errors
```

---

# 16. Real IST pilot

Use:

```text
slnPREPrevencion_2010
WebPREPrevencion
```

Render with:

```text
templates/human/default
```

Pilot views:

```text
ucPreMantEmpadronamiento
ucBusSuc
ucPreMantDepPrevencion
```

For each, produce:

```text
human explanation
usage status
improved UI reconstruction
simple box-flow diagram
data/persistence
unresolved
```

---

# 17. Human review package

Create:

```text
C:\PruebasLegacyMapper\Resultados\post_v5_human_template_productization\
```

Include:

```text
HTML package
PDF
template used
template manifest
structured behavioral explanation
style reconstruction report
REVIEW_GUIDE.md
```

Review questions:

```text
1. ¿Se entiende claramente la jerarquía de título/subtítulo/párrafo?
2. ¿El aviso de IA aparece una sola vez y no molesta durante la lectura?
3. ¿El índice permite encontrar rápidamente proyecto/vistas/secciones?
4. ¿El texto humano sigue siendo la narrativa principal?
5. ¿Los diagramas de cajas ayudan a entender vista → clases → BD?
6. ¿La reconstrucción visual se parece más a la vista real cuando existen estilos?
7. ¿Se declara honestamente cuando la fidelidad visual es parcial?
8. ¿El template puede cambiarse sin tocar Evidence ni la interpretación IA?
9. ¿Las afirmaciones de IA siguen validadas y trazables?
10. ¿Este formato ya es adecuado como template humano genérico?
```

---

# 18. Documentation / state

Update:

```text
docs/POST_V5/H4_BEHAVIORAL_DOCUMENTATION_PROTOTYPE_RESULT.md
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
PROJECT_STATE.json
README.md
```

Record the template system explicitly.

Do not mark H5 started.

---

# 19. Git authority

For this productization workstream:

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

# 20. Success criterion

Success means LegacyMapper can render the validated behavioral model through a reusable human template, producing an HTML/PDF document that:

```text
has clear title/subtitle/body hierarchy
has a useful index
shows the AI disclaimer once
keeps AI status in the underlying model
explains behavior before technical detail
includes simple evidence-backed box flows
uses real UI styles when safely available
keeps unresolved/legacy uncertainty explicit
allows future human templates without changing analysis/AI logic
```

H5 remains NOT_STARTED until human review approves this productized human template direction.
