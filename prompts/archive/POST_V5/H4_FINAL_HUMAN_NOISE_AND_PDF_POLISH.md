# LegacyMapper Post-V5 — H4 Final Human Noise and PDF Polish

## Objective

Perform one final, very small H4 presentation/content polish before the final manual validation.

This is **not H4-R6**.
This is **not H5**.
Do not reopen architecture, Evidence Core, Gate A/B/C, cross-project resolution, AI knowledge contracts, or packaging.

The productization introduced in the previous round remains the target:

```text
output\
    human\
    ai\
    internal\
```

This round changes only the **human-facing presentation**.

Primary goals:

```text
1. Reduce remaining human-documentation noise.
2. Stop giving uncertainty more prominence than known behavior.
3. Fix PDF/wireframe pagination defects.
4. Preserve the AI knowledge package and all internal truth unchanged.
```

---

# 1. Current state

Treat as already PASS:

```text
PRE_H5_GATE_A_PORTABILITY = PASS
PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE = PASS
PRE_H5_GATE_B_EVIDENCE_CORE = PASS
PRE_H5_GATE_B1_EVIDENCE_CORE_CLOSURE = PASS
PRE_H5_GATE_C_FINAL_HARDENING = PASS
PRE_H5_BLOCKING_DEBT = 0
H4_FINAL_KNOWLEDGE_PRODUCTIZATION = READY_FOR_HUMAN_APPROVAL
```

Current productization:

```text
human\
ai\
internal\
```

Current H4 state:

```text
H4 = HUMAN_APPROVAL_PENDING
H5 = NOT_STARTED
```

Do not close H4 automatically.

---

# 2. Main product rule

Use this rule throughout the human output:

> **Known and useful behavior is the main story. Uncertainty is supporting information.**

And:

> **Human documentation should explain the system, not explain LegacyMapper's limitations.**

The human reader should come away understanding:

```text
what the project contains
what each relevant view does
what actions exist
what other views/components are related
what technical path is followed
what data/procedures are reached
```

Not:

```text
how much LegacyMapper failed to resolve
how many unresolved calls exist
why a specific call was not resolved
internal analyzer limitations
```

---

# 3. Executive output — reduce uncertainty aggressively

Current executive output still gives too much space to uncertainty.

Change the executive document so that sections equivalent to:

```text
Lo que no se puede afirmar
Acciones cuyo destino posterior es indeterminado
```

do **not** occupy major sections or full pages.

Instead, use a short final section:

```text
Limitaciones conocidas
```

Maximum intent:

```text
2–4 concise bullets or short paragraphs
```

Example:

```text
Limitaciones conocidas
- Algunas pantallas se cargan dinámicamente y su uso no puede confirmarse solo con análisis estático.
- Algunas rutas terminan en componentes externos o llamadas cuyo destino no está disponible.
- El propósito funcional exacto de ciertas vistas requiere conocimiento del negocio.
```

That is enough for executive readers.

Do not include tables of unresolved calls in executive output.

Do not include technical call names in executive limitations unless absolutely necessary.

---

# 4. Default human guide — uncertainty only where it matters

In the main human guide:

Keep uncertainty only when it materially changes the meaning of an action.

Good:

```text
Buscar
→ btnBuscar_Click
→ destino posterior indeterminado
```

Bad:

```text
The analysis did not resolve X.
The analysis could not determine Y.
The analysis did not find Z.
The destination is unresolved.
The implementation is unknown.
```

repeated in multiple paragraphs.

For each view:

```text
describe known behavior first
describe technical route second
mention one concise uncertainty only if needed
```

Do not repeat the same unknown in:

```text
summary
usage
actions
data
technical section
known/unknown section
```

Pick the most useful place once.

---

# 5. Remove low-value human sections

Review the human guide for sections that mostly restate uncertainty or analyzer mechanics.

Potential candidates to remove, collapse, or move to internal/AI output:

```text
Qué sabemos, qué inferimos y qué no sabemos
long lists of unresolved calls
repeated "Evidencia de uso" explanations
verbose explanations of missing destination
analysis implementation notes
```

Do not remove semantic truth.

If useful for traceability:

```text
move to collapsible HTML detail
or technical appendix
or internal/
or ai/unresolved.json
```

The main PDF should not be dominated by those details.

---

# 6. Keep valuable human content

Do not remove these strengths:

```text
project names
view names
visible titles
simple AI explanation
main actions
Action → Route tables
related views
data/procedures
technical execution paths
wireframes
flow diagrams
tables that explain behavior
```

The previous productization direction remains approved.

---

# 7. AI package must not change

Do not change the meaning or structure of:

```text
ai/knowledge.json
ai/architecture.json
ai/views.json
ai/flows.json
ai/data.json
ai/unresolved.json
ai/provenance.json
```

unless a purely presentation-independent bug is discovered.

No semantic rewriting of AI knowledge is requested.

The detailed unresolved information belongs there and in `internal/`, not in the primary human narrative.

---

# 8. No new AI call

For this polish:

```text
provider calls = 0
```

Do not call Copilot.

Reuse the already persisted interpretation from the final knowledge productization round.

This task is deterministic human presentation polish only.

---

# 9. No source / analyzer work

Do not:

```text
run scanner
run analyzer
rebuild Evidence
read source tree
rerun IST analysis
modify Evidence semantics
```

Use the existing persisted baseline and existing AI interpretation.

---

# 10. PDF / wireframe pagination defect

Fix the current wireframe pagination problem.

Known example:

```text
ucPreMantJerarquia2
```

The current PDF splits the reconstruction across multiple pages in a way that leaves narrow/vertical text fragments such as:

```text
iconoAsignar
iconoDesasociar
```

on an isolated middle page.

This is not acceptable.

Required rule:

> **Never split a wireframe so that controls, labels, buttons or icons become isolated vertical fragments or unreadable partial elements.**

Preferred strategies, in order:

```text
1. Scale the full wireframe to fit one page when still readable.
2. If too tall, split only at logical section boundaries.
3. Keep each control row/group intact.
4. Do not split inside a button/icon/label.
5. If needed, use landscape orientation for that wireframe page.
6. If still too large, use a full-page reduced overview + detailed continuation sections.
```

Do not produce arbitrary vertical slicing.

---

# 11. PDF pagination rules

Apply general PDF layout rules:

```text
avoid orphan headings
avoid splitting action tables after header with one row
avoid splitting a single route across pages if it can fit together
avoid isolated one-line continuation pages
avoid control labels detached from their wireframe region
prefer page break before a large diagram rather than splitting badly
```

Preserve deterministic output.

---

# 12. Human HTML vs PDF

HTML may retain richer detail through:

```text
collapsible sections
full relation lists
full diagrams
technical traceability
```

PDF should be more curated.

Rule:

> **HTML can be complete; PDF should be readable.**

Do not force every HTML detail into PDF.

---

# 13. Executive vs default

Executive:

```text
short
business/system oriented
projects
main capabilities
major dependencies
important data impact
small limitation note
```

Default human guide:

```text
functional + technical
view-by-view explanations
actual action routes
relations
data
wireframes
diagrams
```

Do not duplicate the same large unresolved sections in both.

---

# 14. Visual regression targets

At minimum review these existing H4 representative views:

```text
ucPreMantJerarquia2
ucBusSuc
ucPreMantEmpadronamiento
ucPreEstadisticasAccidentes
ucPreConActxProd
```

Explicitly inspect PDF pages for:

```text
wireframe clipping
vertical text fragments
bad table splits
orphan headings
diagram overflow
unreadable scaling
```

---

# 15. Human content regression targets

Verify:

```text
executive does not contain unresolved-call tables
executive limitation section is short
default does not repeat the same uncertainty multiple times
known behavior appears before uncertainty
actual names/routes remain visible
technical usefulness is preserved
```

---

# 16. Output

Generate a review package under a new directory, e.g.:

```text
C:\PruebasLegacyMapper\Resultados\h4_final_human_noise_pdf_polish\
```

Public package must still be:

```text
package\
    KNOWLEDGE_PACKAGE.json
    human\
    ai\
    internal\
```

The owner should need to inspect only:

```text
human\index.html
human\LegacyMapper.pdf
human\executive.pdf
```

The AI package should be copied/reused unchanged.

---

# 17. Tests

Add targeted tests for:

```text
executive has no unresolved-call table
executive has concise limitations
default does not repeat identical unresolved statements
known behavior appears before uncertainty
AI package unchanged
provider calls = 0
scanner/analyzer = 0
source reads = 0
wireframe pagination avoids isolated control fragments
no arbitrary vertical split of controls
PDF generated successfully
```

During implementation:

```text
targeted tests only
```

After all changes are stable:

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

# 18. Result report

Create:

```text
docs/POST_V5/H4_FINAL_HUMAN_NOISE_AND_PDF_POLISH_RESULT.md
```

Include:

```text
what human sections changed
what uncertainty was removed/collapsed
what remains in ai/internal
PDF pagination changes
wireframe split strategy
provider calls
scanner/analyzer/source-read proof
targeted tests
full suite result
review output path
```

---

# 19. Final state

If technically successful:

```text
H4_FINAL_HUMAN_NOISE_AND_PDF_POLISH = READY_FOR_MANUAL_VALIDATION
H4 = HUMAN_APPROVAL_PENDING
H5 = NOT_STARTED
```

Do not close H4.

The next step is a **manual LegacyMapper run as an end user** using the final package contract.

If that run is accepted by the owner, then prepare a separate formal H4 closure action.

---

# 20. Git authority

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

> **Known behavior first.**

> **Uncertainty remains available, but it does not dominate human documentation.**

> **HTML may be complete; PDF must be readable.**

> **Do not split diagrams or wireframes in ways that make controls unreadable.**

> **AI and internal knowledge stay complete; human output stays useful.**
