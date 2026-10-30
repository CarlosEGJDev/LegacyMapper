# LegacyMapper Post-V5 — H4 Final Human Catalog and Wireframe Micro-Polish

## Objective

Perform one final **micro-polish** before the last manual H4 validation.

This is not a new H4 round.
This is not H5.
Do not reopen architecture, Evidence, AI knowledge contracts, packaging, cross-project resolution, or analyzer behavior.

The product already has the correct target structure:

```text
output\
    human\
    ai\
    internal\
```

This task changes only two presentation details:

```text
1. Remove low-value numeric/coverage information from the human PDF catalog.
2. Fix remaining unreadable vertical text in wireframe controls.
```

Everything else should remain stable.

---

# 1. Current state

Treat as PASS:

```text
PRE_H5_GATE_A_PORTABILITY = PASS
PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE = PASS
PRE_H5_GATE_B_EVIDENCE_CORE = PASS
PRE_H5_GATE_B1_EVIDENCE_CORE_CLOSURE = PASS
PRE_H5_GATE_C_FINAL_HARDENING = PASS
PRE_H5_BLOCKING_DEBT = 0
H4_FINAL_KNOWLEDGE_PRODUCTIZATION = READY_FOR_HUMAN_APPROVAL
H4_FINAL_HUMAN_NOISE_AND_PDF_POLISH = READY_FOR_MANUAL_VALIDATION
```

Current H4 state:

```text
H4 = HUMAN_APPROVAL_PENDING
H5 = NOT_STARTED
```

Do not close H4 automatically.

---

# 2. Main product rule

Human documentation must prioritize:

```text
names
purpose
behavior
relationships
technical routes
data/procedures
visual explanations
```

Do not use numbers merely because they are available.

> **If a count does not help a human understand the system, it does not belong in the primary human PDF.**

---

# 3. Remove low-value catalog metrics

The current human PDF catalog still includes columns such as:

```text
Acciones
¿Lee?
¿Escribe?
¿Abre otra?
Cómo se llega
```

and values such as:

```text
26 vistas la abren
4 acciones
sí/no
0
1
3
```

These should not dominate the human catalog.

For the PDF, simplify the catalog to useful descriptive columns such as:

```text
Vista
Título visible
Qué parece hacer
Uso observable
```

Optionally:

```text
Relación principal
```

only if it can be expressed with names rather than counts.

Do not replace names with numeric summaries.

---

# 4. Remove coverage metrics from human PDF

The section:

```text
Mediciones de cobertura (para decisiones de diseño)
```

must not appear in the main human PDF.

Examples of data to remove from the human PDF:

```text
vistas del proyecto = 121
con code behind = 107
con eventos o acciones = 107
alcanzan clase de negocio o dao = 39
alcanzan procedimiento o sql = 39
con invocaciones entrantes = 8
con invocaciones salientes = 32
soportan wireframe documental = 117
estructuralmente no resueltas = 100
```

These numbers may remain in:

```text
ai/
internal/
diagnostics
coverage reports
machine-readable manifests
```

but not in the primary human guide.

If useful in HTML, place them only in a collapsed/internal diagnostic section clearly labeled as analysis metadata.

---

# 5. Keep useful scope counts only when human-relevant

Counts are still allowed when they communicate obvious scope and are paired with names.

Good:

```text
La solución contiene 3 proyectos:
- blPrePrevencion
- sysPREPrevencion
- WebPREPrevencion
```

Good:

```text
El proyecto tiene 121 vistas
```

only if the document immediately provides or links to the view catalog.

Bad:

```text
39 routes reach data
100 unresolved actions
32 outgoing invocations
```

unless specifically requested by the user.

---

# 6. Keep the human catalog descriptive

Preferred PDF catalog:

| Vista | Título visible | Qué parece hacer | Uso observable |
|---|---|---|---|
| ucBusSuc | Buscar Centro de Trabajo | Búsqueda / selección de centros de trabajo | Uso observable activo |
| ucPreMantJerarquia2 | Mantención de Jerarquías | Mantención de relaciones jerárquicas | Uso no resuelto |

The HTML may provide richer drill-down through links.

Do not repeat technical counts in the PDF catalog.

---

# 7. Wireframe control-label defect

Known remaining defect:

```text
ucPreMantJerarquia2
```

The wireframe now fits on one page, but controls such as:

```text
iconoAsignar
iconoDesasociar
```

are still rendered as narrow vertical character stacks.

This must be fixed.

> **Control labels must remain horizontally legible in wireframes.**

Preferred behavior:

```text
[Asignar]
[Desasociar]
```

instead of vertical character stacking.

---

# 8. Wireframe label simplification

When a control is an icon/button and the literal internal identifier is too long for the available box:

Use a human-readable short label derived from visible/semantic action data.

Examples:

```text
iconoAsignar      -> Asignar
iconoDesasociar   -> Desasociar
icono buscar      -> Buscar
icono guardar     -> Guardar
icono Eliminar    -> Eliminar
icono cerrar      -> Cerrar
```

Preserve the raw/internal identifier in the HTML detail/model if needed.

Do not fabricate a semantic label if no visible/action meaning exists.

Fallback order:

```text
1. visible text
2. known associated action/event name normalized for humans
3. shortened identifier
4. icon placeholder
```

Never rotate text vertically just to make it fit.

---

# 9. Wireframe layout rules

For small vertical control areas:

```text
minimum readable width
horizontal text only
allow slightly wider center action column
reduce surrounding whitespace if needed
use compact labels
```

If necessary, rebalance columns rather than shrinking text below readability.

The wireframe should favor human understanding over literal reproduction of control proportions.

It is a documentary reconstruction, not a pixel-perfect screenshot.

---

# 10. Representative visual checks

At minimum inspect:

```text
ucPreMantJerarquia2
ucBusSuc
ucPreMantEmpadronamiento
ucPreEstadisticasAccidentes
ucPreConActxProd
```

Explicitly verify:

```text
no vertical character stacks
no clipped button labels
no text escaping controls
no control overlap
no unreadably tiny labels
```

---

# 11. Do not alter semantic truth

Do not change:

```text
AI interpretation content
Evidence status
confirmed/inferred/unresolved state
technical routes
view relationships
data procedures
AI knowledge model
internal manifests
```

This is presentation-only.

---

# 12. No AI / no analysis

For this task:

```text
provider calls = 0
scanner = 0
analyzer = 0
source reads = 0
Evidence rebuild = 0
```

Reuse the existing persisted baseline and AI interpretation.

---

# 13. Output

Generate a new review package, for example:

```text
C:\PruebasLegacyMapper\Resultados\h4_final_catalog_wireframe_polish\
```

Keep the public structure:

```text
package\
    KNOWLEDGE_PACKAGE.json
    human\
    ai\
    internal\
```

The owner should only need to inspect:

```text
human\index.html
human\LegacyMapper.pdf
human\executive.pdf
```

The AI/internal package should remain unchanged.

---

# 14. Tests

Add targeted tests for:

```text
human PDF catalog has no low-value numeric metric columns
coverage metrics section absent from human PDF
useful scope counts still allowed
catalog keeps view names and titles
wireframe labels are horizontal
icon/button labels are human-readable when safely known
no vertical character stacks
AI package byte-identical
provider calls = 0
scanner/analyzer/source reads = 0
PDF deterministic
```

During development:

```text
targeted tests only
```

At the end, once stable:

```text
python -X utf8 -m unittest discover -s tests
```

Run the full suite exactly once.

Required:

```text
0 failures
0 errors
```

---

# 15. Result report

Create:

```text
docs/POST_V5/H4_FINAL_HUMAN_CATALOG_AND_WIREFRAME_MICRO_POLISH_RESULT.md
```

Include:

```text
catalog changes
coverage metrics removed from human PDF
what remains in ai/internal
wireframe label strategy
representative visual checks
provider/scanner/analyzer/source-read proof
targeted tests
full suite result
review path
```

---

# 16. Final state

If technically successful:

```text
H4_FINAL_HUMAN_CATALOG_AND_WIREFRAME_MICRO_POLISH = READY_FOR_FINAL_MANUAL_RUN
H4 = HUMAN_APPROVAL_PENDING
H5 = NOT_STARTED
```

Do not close H4.

The next step is the **final manual end-user run of LegacyMapper**.

If the owner approves that run, then prepare the formal H4 closure prompt.

---

# 17. Git authority

For this round:

```text
production edits = YES
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

> **Human documentation explains the system; it does not expose analyzer statistics.**

> **Names and relationships are more useful than counts.**

> **Wireframes are documentary explanations, so readability beats literal control proportions.**

> **No semantic truth changes in this round.**
