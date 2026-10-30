# LegacyMapper Post-V5 — H4 Final Human Template Polish and Approval
## Final Presentation, Layout, and Rendering Corrections

### Context

H4 behavioral documentation and the human template system are already technically validated.

The remaining work is **final presentation polish** so this milestone can be left ready for human approval.

This is **not a new conceptual round**.
Do **not** redesign the model.
Do **not** reopen the behavioral interpretation concept.
Do **not** start H5.

This is a **final closure-polish round** for the human documentation template and its renderers.

---

# 1. Objective

Leave the H4 human documentation milestone ready for approval by correcting the remaining presentation, rendering, and documentation issues in a **global** way.

The result must look:

```text
ordered
professional
readable
consistent
macro-to-micro
```

and the improvements must apply to:

```text
HTML
PDF
SVG diagrams
```

globally, not only to one pilot view.

---

# 2. Preserve what is already accepted

Do not regress these accepted achievements:

```text
behavioral documentation model
macro → micro structure
AI interpretation contract
usage-status model
template system
template directories
default human template
style-aware reconstruction
simple box-flow diagrams
appendix/catalog separation
baseline integrity
test stability
```

The concept is accepted.
This round is about **finishing quality**.

---

# 3. Primary corrections required

## A. Box-diagram text overflow

Current issue:

```text
text escapes boxes
text is cut or visually cramped
some labels are truncated or leave the box boundaries
```

Required correction:

```text
all text inside diagram boxes must stay contained
```

Implement globally for all relevant SVG diagrams.

Requirements:

```text
automatic line wrapping
internal padding
sufficient minimum box height
adaptive box height when text wraps
reasonable box width
no text overflowing box borders
no cropped labels
stable deterministic layout
```

If a label is too long, the box must grow or wrap.
Do not let text escape the box.

Apply this to all simple flow diagrams and any similar generated SVGs.

---

## B. Centered document title

The main document title must be:

```text
centered
visually prominent
clearly separated from the following content
```

Add consistent spacing below the title.

---

## C. Justified explanatory paragraphs

Human explanation paragraphs should be:

```text
justified
comfortable to read
visually separated from titles/subtitles
```

Apply to the main body text in HTML and PDF where appropriate.

Do not justify tiny labels, badges, or diagram captions where it harms readability.

---

## D. Centered view subtitle

When a specific view/screen begins, the view title should behave as a subtitle:

```text
centered
clearly styled as a subtitle
with top and bottom spacing
```

This should visually separate:

```text
preceding explanation
view subsection start
following diagram/image
```

---

## E. Centered image / diagram block

The view reconstruction image and the flow diagram block should be:

```text
centered
visually separated from the subtitle
visually separated from surrounding paragraphs
```

Add consistent margin above and below.

---

## F. Professional vertical rhythm / spacing

The whole document needs better rhythm:

```text
title
→ spacing
intro paragraph
→ spacing
view subtitle
→ spacing
image / diagram
→ spacing
body sections
```

Do not leave elements visually crowded together.

The template must feel deliberate and professional.

---

# 4. Apply globally, not locally

These fixes must not be made only for:

```text
ucPreMantEmpadronamiento
ucBusSuc
ucPreMantDepPrevencion
```

They must be implemented at the renderer/template level so that all future human documents inherit them automatically.

This includes:

```text
HTML template
PDF CSS / PDF rendering
SVG diagram generator
```

The rule is:

> **Fix the system, not the single sample.**

---

# 5. AI notice cleanup

Keep the earlier correction and finish it cleanly.

## Required behavior

Show the AI disclaimer clearly **once near the beginning** of the document.

It should explain:

```text
this document contains AI-generated interpretations
AI interpretation is not automatically approved/canonical
confirmed / inferred / unresolved / AI interpretation remain visually distinguishable
```

## In the body

Do not repeat long phrases like:

```text
Interpretación de IA — no aprobada
```

throughout the document.

Use only a light-weight marker strategy, for example:

```text
one marker per major block or chapter
small IA badge
subtle styling
```

Do not place an `IA` marker on every small paragraph if it creates visual noise.

The status in the structured model must remain unchanged:

```text
AI_INTERPRETATION
```

This is a presentation correction only.

---

# 6. Correct obsolete cover wording

The cover/front page must not incorrectly state that the documentation was generated without AI provider calls if the narrative actually comes from a real AI run that was replayed/revalidated later.

Replace any obsolete wording like:

```text
generated without calling an AI provider
```

with accurate wording such as:

```text
This document includes interpretations obtained from a real AI run and later revalidated deterministically.
The final rendering did not require new provider calls or a fresh source-code analysis.
```

Use equivalent wording if needed, but it must be accurate.

---

# 7. Typography and style polish

Preserve the current typography hierarchy, but finish its presentation quality.

Required visual distinction:

```text
Document title
H1
H2
H3
Body paragraph
Caption
Technical note
Evidence/source note
Status badge
```

Additionally ensure:

```text
consistent margins
consistent line spacing
consistent section spacing
clean alignment
no visually accidental misalignment
```

The output should look like a finished human document, not a raw prototype.

---

# 8. SVG / diagram rendering polish

For all SVG flow diagrams:

## Must improve

```text
text containment
box sizing
label legibility
overall centering
balanced whitespace
arrow readability
```

## Preserve

```text
deterministic ordering
epistemic color/status semantics
dotted/dashed unresolved styling
source-based node inclusion
no invented layers
```

## Optional layout improvements if low risk

```text
center diagram title
balance column spacing
improve lane alignment
wrap long procedure or class names gracefully
increase canvas height/width when needed
```

Do not introduce nondeterministic layout engines.

---

# 9. HTML and PDF alignment

Ensure the HTML and PDF present the same intended reading order and visual structure.

They do not need pixel-perfect identity, but they should agree on:

```text
title placement
AI notice placement
section order
view subtitle placement
diagram centering
paragraph justification
spacing rhythm
appendix separation
```

The PDF should feel like a polished export of the same template system.

---

# 10. Template-level implementation

These corrections must live in the template system.

Update as needed:

```text
templates/human/default/template.yaml
templates/human/default/document.html
templates/human/default/styles.css
templates/human/default/pdf.css
```

Update renderer code only where necessary to support:

```text
diagram centering
layout spacing
text wrapping in SVG boxes
chapter-level IA markers
accurate cover wording
```

Do not hardcode one-off fixes into the sample output.

---

# 11. Human structure to preserve

The reading order should remain:

```text
Cover
AI interpretation notice
Table of contents
Solution
Project
Module decision / no-safe-module note
Important views
Detailed view chapters
Cross-view behavior
Data/persistence
Observable usage / legacy uncertainty
Known unresolved areas
Appendix
```

Do not let the appendix or catalog dominate the narrative again.

---

# 12. Style-aware reconstruction

Do not regress the styling gains already achieved.

Preserve the current honest classification:

```text
STRUCTURE_ONLY
STYLE_PARTIAL
STYLE_HIGH_CONFIDENCE
```

Continue to label reconstructed views as:

```text
DOCUMENTARY RECONSTRUCTION
NOT A PRODUCTION SCREENSHOT
```

But ensure their placement in the document is clean and centered.

---

# 13. Tests

Add/adjust tests as needed for final polish.

At minimum verify:

```text
AI notice rendered once in the intended place
no repeated long AI disclaimer in body headings
template title alignment classes/hooks exist
view subtitle classes/hooks exist
image/diagram centering classes/hooks exist
paragraph justification classes/hooks exist
diagram SVG text wraps/box sizing remain deterministic
long labels remain inside boxes
HTML rendering stable
PDF rendering stable
same input → deterministic outputs
baseline unchanged
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

Record exact totals.

---

# 14. Real IST validation package

Regenerate the human template productization review package.

Path:

```text
C:\PruebasLegacyMapper\Resultados\post_v5_human_template_productization\
```

Include updated:

```text
PDF
HTML
template files
style reconstruction report
REVIEW_GUIDE.md
representative SVG diagrams
representative wireframes
```

Use at least the existing pilot views:

```text
ucPreMantEmpadronamiento
ucBusSuc
ucPreMantDepPrevencion
```

---

# 15. Human review questions

Update `REVIEW_GUIDE.md` to verify:

```text
1. Is the document title centered and visually clear?
2. Are explanatory paragraphs justified and easier to read?
3. Are view subtitles centered and well separated?
4. Are diagrams/images centered and visually well placed?
5. Do flow-diagram labels remain inside boxes?
6. Is the document more ordered and professional overall?
7. Does the AI notice appear once without excessive repetition?
8. Are the diagrams still semantically correct after the layout polish?
9. Does the same improvement apply globally, not only to one sample?
10. Is the milestone now ready for final human approval?
```

---

# 16. Documentation / state

Update as needed:

```text
docs/POST_V5/H4_BEHAVIORAL_DOCUMENTATION_PROTOTYPE_RESULT.md
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
PROJECT_STATE.json
README.md
```

Record that this round is final presentation/rendering polish for the human template system.

Do not start H5.

---

# 17. Git authority

For this final polish round:

```text
edit production code = YES
edit tests = YES
edit docs/state = YES

commit = NO
push = NO
tag = NO
```

No versioning without explicit human authorization.

---

# 18. Final expected state

If successful, the result should be:

```text
H4_HUMAN_TEMPLATE_READY_FOR_FINAL_HUMAN_APPROVAL
```

and the generated artifacts should show:

```text
clean centered title
single clear AI notice
justified explanatory text
centered view subtitles
centered diagrams/images
contained SVG box text
professional spacing
consistent global rendering
```

---

# 19. Success criterion

This round succeeds only if the human document now feels:

```text
ordered
professional
clean
readable
consistent
```

while preserving:

```text
behavioral explanation
epistemic honesty
deterministic validation
macro-to-micro clarity
template reuse
```

The key test is simple:

> **A human should be able to say: "Now this looks like a finished professional document, not a prototype with loose edges."**
