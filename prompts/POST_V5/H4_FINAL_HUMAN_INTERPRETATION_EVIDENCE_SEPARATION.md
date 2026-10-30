# LegacyMapper Post-V5 — H4 Final Human Interpretation / Evidence Separation Polish

## Objective

Perform one final **human-documentation separation polish** based on the owner’s manual review of the real final-validation output.

This is not a new architecture round.
This is not H5.
Do not rerun scanner/analyzer.
Do not rebuild Evidence.
Do not call the AI provider again unless a hard blocker is found and reported first.
Do not change the AI knowledge truth model.

The problem to solve is presentation and audience separation:

> **Human documentation should contain the interpreted explanation of the system. Evidence, source references, deterministic support IDs, validation diagnostics and provenance belong to AI/internal artifacts, not in the main human narrative.**

The current documentation is much improved, but still mixes:

```text
human explanation
evidence/provenance
confirmation state
source references
AI labels
repeated claims
```

These must be separated more cleanly.

---

# 1. Current final-validation context

The final manual validation environment already exists and is operational:

```text
C:\PruebasLegacyMapper\FinalValidation\
```

Current real run output:

```text
C:\PruebasLegacyMapper\FinalValidation\runs\manual_final\package\
```

The owner reviewed:

```text
human\index.html
```

and confirms:

```text
the documentation is much better
the interpreted content is useful
the remaining issue is unnecessary evidence/provenance noise in the human document
```

Do not invalidate the current run.

Use the existing:

```text
baseline
persisted AI interpretation
package inputs
```

for this presentation-only correction.

---

# 2. Product rule

Apply this rule strictly:

> **Humans receive interpretation. AI/internal receives evidence and provenance.**

The human reader wants to know:

```text
what the solution is
what projects exist
what each project does
what views/screens exist
what each view does
what actions are available
what calls what
what data/procedures are reached
what is confirmed / inferred / unresolved
```

The human reader does NOT need to see, inline:

```text
Evidence IDs
EP-...
FLOW-...
source file paths
source line numbers
deterministic support references
validation candidate IDs
hashes
raw provenance strings
request IDs
provider diagnostics
```

These remain available in:

```text
ai\
internal\
```

---

# 3. Remove evidence references from primary human narrative

Remove from the main human HTML/PDF content strings such as:

```text
Referencias: EP-0363902331, EP-0398476657, FLOW-0150206897, ...
src:proyectos\...\archivo.ascx.vb:52
src:webFicha\...\archivo.ascx.vb:172
```

and equivalent deterministic provenance blocks.

Do not delete that information from the product.

Move/preserve it in:

```text
ai\provenance.json
ai\knowledge.json
internal\evidence\
internal\validation\
internal\traceability\
```

or the existing equivalent locations.

Human documentation may contain a single statement near the beginning:

> **La documentación se construyó a partir del análisis de IST y de una interpretación de IA validada contra la evidencia disponible.**

That is sufficient.

Do not expose individual source references in normal human reading flow.

---

# 4. Remove duplicated “Base de las afirmaciones” sections

The owner explicitly considers sections like:

```text
Base de las afirmaciones
Afirmación
Estado
Base
```

to be redundant in the human document when they repeat the same claim already shown immediately above.

Do not repeat the same statement once as:

```text
Afirmación
```

and then again as:

```text
Base de las afirmaciones
```

Remove these repeated evidence/base tables from the primary human experience.

If traceability must remain available in HTML:

```text
move it behind a clearly secondary collapsible technical traceability section
```

but preferably keep it outside `human/` entirely if the existing product contract supports that cleanly.

The PDF should not contain those repeated base/evidence tables.

---

# 5. Human state presentation — color is useful

Keep the semantic distinction:

```text
CONFIRMED
INFERRED
UNRESOLVED
```

but present it visually and simply.

At the beginning of the human documentation, explain the colors once.

Recommended visual contract:

```text
Blue / Confirmado
Orange / Inferido
Red / No resuelto
```

Exact colors may follow the existing template palette.

Use visually distinct bordered boxes/cards/badges.

Do not repeat the explanatory definition of each state throughout the document.

---

# 6. Avoid separate “Estado” columns when a colored block is clearer

Where practical, prefer:

```text
colored statement card
```

over a repetitive table:

```text
Afirmación | Estado
```

Especially for short sections such as:

```text
La solución
El proyecto
Estructura
Capacidades
```

The state should be visually encoded in the card/border/badge.

Tables are still valid where they communicate structured lists.

---

# 7. IA label — show once, not everywhere

The owner does not want the purple `IA` block repeated for every explanation.

Reason:

> The reader already understands from the beginning that the document is an AI-generated interpretation.

New rule:

At the beginning of the human document, show one clear note:

> **Interpretación asistida por IA**
>
> Este documento presenta una interpretación generada por IA a partir del análisis de IST. Las afirmaciones conservan su estado de confianza: Confirmado, Inferido o No resuelto.

After that:

```text
do not add a purple IA badge/card before every paragraph or section
```

Only show an explicit IA label again if a specific statement has a materially different semantic status such as:

```text
AI proposal not validated
```

---

# 8. Human narrative must read naturally

The human document should feel like documentation, not like an evidence-review UI.

Preferred:

```text
1. La solución

[Confirmado]
slnPREPrevencion_2010 contiene los proyectos blPrePrevencion,
sysPREPrevencion y WebPREPrevencion.

[Inferido]
WebPREPrevencion actúa como capa de presentación y utiliza los
proyectos de apoyo para lógica y acceso a datos.

[No resuelto]
El propósito de negocio global de la solución no puede determinarse
con certeza solo desde el código.
```

Avoid:

```text
Afirmación | Estado
Base de las afirmaciones
Referencias
Evidence IDs
source paths
IA
Afirmación repetida
```

---

# 9. Human document hierarchy

Target reading structure:

```text
Cover / title
How to read status colors
Short note: AI-assisted interpretation based on IST

1. Solution
2. Projects
3. Modules / functional areas if safe
4. Views / screens
5. View behavior
6. View-to-view relations
7. Technical routes
8. Data / procedures
9. Known limitations
10. Optional appendix
```

The appendix may include:

```text
catalog of views
technical glossary
```

but not raw evidence diagnostics.

---

# 10. Evidence/provenance destination

Preserve full technical traceability for AI and engineering use.

Expected homes:

```text
ai\knowledge.json
ai\provenance.json
ai\unresolved.json
internal\
```

Make sure another AI can still answer:

```text
where did this fact come from?
which source artifact supports it?
which Evidence IDs support it?
which claims were rejected?
what validation status exists?
```

Human simplification must not destroy machine traceability.

---

# 11. Human vs AI contract

Enforce this separation:

```text
HUMAN
- explanation
- names
- relations
- behavior
- routes
- data
- diagrams
- status colors
- concise limitations

AI / INTERNAL
- Evidence IDs
- source paths
- line references
- hashes
- provenance
- validation details
- rejected claims
- diagnostics
- coverage metrics
```

This is a product principle, not a one-off formatting trick.

---

# 12. HTML behavior

For `human\index.html`:

Do not show raw source references in the normal visible flow.

If traceability is retained in the HTML at all:

```text
place it behind an advanced/technical expandable block
disabled/closed by default
clearly labeled as traceability
```

But preferred default:

```text
human HTML = interpretation only
```

with machine traceability outside `human/`.

---

# 13. PDF behavior

For:

```text
human\LegacyMapper.pdf
human\executive.pdf
```

Do not include:

```text
Evidence IDs
source file paths
line numbers
Base de las afirmaciones
raw provenance
repeated IA blocks
```

Keep:

```text
state color legend
interpreted explanation
technical route names
view names
class/method/procedure names where useful
diagrams/wireframes
known limitations
```

---

# 14. Do not remove technical usefulness

This polish must not oversimplify the technical sections.

Technical readers still need routes such as:

```text
ucPreMantJerarquia2
→ hypAsignar.Click
→ hypAsignar_Click
→ PreGesJerarquia.txcrear
→ sysPreGesJerarquia.crear
→ PPRE_GES_JERARQUIA.CREAR
```

That is useful human documentation.

What should disappear is the supporting provenance noise, not the technical route itself.

---

# 15. Tests

Add targeted tests for:

```text
no EP-* IDs in human HTML/PDF
no FLOW-* IDs in human HTML/PDF
no src: source-path references in primary human content
no "Base de las afirmaciones" repetition in PDF
no duplicate statement/base rendering
single AI interpretation notice at document start
no repeated purple IA badges for normal sections
status legend appears once near beginning
confirmed/inferred/unresolved remain visually distinct
technical routes remain present
ai/provenance and internal traceability remain intact
```

Also test:

```text
human simplification does not alter ai/knowledge.json semantics
human simplification does not alter Evidence
provider calls = 0
scanner/analyzer = 0
source reads = 0
```

During development:

```text
targeted tests only
```

At the end:

```text
python -X utf8 -m unittest discover -s tests
```

Run the full suite once after the changes are stable.

Required:

```text
0 failures
0 errors
```

---

# 16. Regeneration strategy

Because the final manual validation environment already has persisted baseline and AI responses:

Do not rerun:

```text
01_ANALYZE_ONCE
02_INTERPRET_WITH_AI
```

After product changes are installed/rebuilt into the validation runtime, regenerate only presentation/package steps equivalent to:

```text
03_GENERATE_HUMAN_KNOWLEDGE
04_GENERATE_AI_KNOWLEDGE
05_PACKAGE_FINAL_OUTPUT
06_COLLECT_REVIEW_FILES
```

or the current actual product-package command that produces the same result.

No provider call is required for this correction.

---

# 17. New review output

Do not overwrite the owner’s current manual run.

Generate a new review package, for example:

```text
C:\PruebasLegacyMapper\FinalValidation\runs\manual_final_clean_human\
```

or another short equivalent path.

The owner should inspect:

```text
package\human\index.html
package\human\LegacyMapper.pdf
package\human\executive.pdf
```

---

# 18. Result report

Create:

```text
docs/POST_V5/H4_FINAL_HUMAN_INTERPRETATION_EVIDENCE_SEPARATION_RESULT.md
```

Include:

```text
what evidence/provenance was removed from human output
where that information now remains available
how status colors are presented
how the AI notice was simplified
proof that technical routes remain
proof that ai/internal traceability remains
provider call count
scanner/analyzer/source-read count
targeted test result
full suite result
new review path
```

---

# 19. Final state

If successful:

```text
H4_FINAL_HUMAN_INTERPRETATION_EVIDENCE_SEPARATION = READY_FOR_HUMAN_APPROVAL
H4 = HUMAN_APPROVAL_PENDING
H5 = NOT_STARTED
```

Do not close H4 automatically.

The owner will inspect the clean human package.

---

# 20. Git authority

For this task:

```text
production presentation edits = YES
tests = YES
docs/state draft updates = YES
new AI calls = NO
scanner/analyzer rerun = NO
commit = NO
push = NO
tag = NO
```

Do not commit, push or tag without explicit human authorization.

---

# Final principles

> **The source of truth is IST, but the human reader does not need to see the Evidence machinery.**

> **Humans should read the interpretation. AI and internal artifacts should preserve the proof.**

> **Explain status once with color, then let the document read naturally.**

> **Do not repeat that the document is AI-generated on every section.**
