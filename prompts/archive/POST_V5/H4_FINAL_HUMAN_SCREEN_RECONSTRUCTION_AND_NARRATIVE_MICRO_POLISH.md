# LegacyMapper Post-V5 — H4 Final Human Screen Reconstruction and Narrative Micro-Polish

## Objective

Perform the **last H4 human-presentation micro-polish**.

If this round is technically successful and the owner approves the resulting human files, H4 can be formally closed.

This is NOT:
- a new architecture round
- H5
- an Evidence change
- an AI re-interpretation
- a scanner/analyzer change
- a diagram redesign

The owner explicitly considers the following already good:

```text
RUN_ALL.cmd experience = APPROVED
human / ai / internal structure = APPROVED
flow diagrams = APPROVED
behavior diagrams = APPROVED
general human-documentation direction = APPROVED
```

The only remaining work is:

```text
1. polish documentary screen reconstructions
2. remove the last source/provenance noise from human prose
3. simplify human state presentation
4. make the narrative sound like documentation, not an evidence audit
```

---

# 1. Hard scope boundary

Do NOT redesign the diagrams.

The owner explicitly says:

> **Los diagramas ya están perfectos.**

Do not change their conceptual layout, semantics or information density unless required only by an existing renderer invariant.

This round focuses on:

```text
wireframe / screen reconstruction
human wording
human-only presentation
```

---

# 2. Known screen-reconstruction defects from real manual review

## 2.1 `ucPreMantJerarquia2`

The current reconstruction is understandable but the center action column is visually poor.

Observed problems:

```text
Asignar / Desasociar area too narrow
arrow symbols appear detached from the buttons
arrow symbols appear vertically stacked
lblMensaje1 / lblMensaje2 occupy awkward structural cells
button and arrow layout does not resemble a clean action control area
excessive structural grid lines in the central column
```

Preferred documentary layout:

```text
Empleados Dependientes          Acciones          Empleados NO dependientes

[lstDepend]                      [Asignar →]       [lstNoDepend]
                                 [← Desasociar]

                                 lblMensaje1
                                 lblMensaje2
```

or an equivalent readable deterministic arrangement.

Requirements:

```text
no vertically stacked arrow characters
no detached arrow symbols
no narrow cells containing only < or >
no overlap
no button text clipping
center action region has sufficient width
```

If the actual markup contains separate icon controls, preserve their semantic existence internally, but the human reconstruction may combine them visually into a documentary action button when this improves comprehension.

If direction cannot be safely established, use `[Asignar]` / `[Desasociar]` without arrows rather than inventing direction.

---

# 3. Internal control IDs are secondary in reconstructions

The reconstruction should prioritize what a human would perceive.

Preferred display order:

```text
1. visible label/text
2. semantic action name
3. humanized control identifier
4. raw identifier only when no better label exists
```

Examples:

```text
hypBuscar       -> Buscar
hypAsignar      -> Asignar
HypDesasociar   -> Desasociar
```

The raw identifier remains in the machine model.

Do not remove it from `ai/` or `internal/`.

---

# 4. `ucPreConActxProd` date-range defect

Current reconstruction renders `Hasta` vertically between `[fec_ini]` and `[fec_fin]`.

This is not acceptable.

Target:

```text
[fec_ini]   Hasta   [fec_fin]
```

or, only if safely supported by surrounding semantics:

```text
Desde [fec_ini]   Hasta [fec_fin]
```

Hard rule:

> **Human labels such as “Hasta”, “Criterio”, “Fecha”, “Acción”, etc. must never be rendered one character per line.**

If the available layout cannot fit the word:

```text
widen the cell
rebalance sibling columns
reduce empty space
move the label above/beside controls
```

Never solve it with character stacking.

---

# 5. General screen-reconstruction layout engine

Improve deterministic reconstruction rules so this is not fixed only for two specific views.

Add layout behavior for:

```text
label + control
control + separator + control
two-list transfer controls
button/action columns
date ranges
small intermediary labels
```

The renderer should recognize that a short semantic text element between two controls often needs a minimum human-readable width.

Examples:

```text
[date] Hasta [date]

[list] [Asignar →] [list]
       [← Desasociar]

[label] [input]
```

---

# 6. Minimum width rule for human words

Introduce a deterministic minimum width rule based on rendered word width.

For any non-symbolic human text:

```text
minimum cell width >= longest unbreakable word + padding
```

Examples:

```text
Hasta
Criterio
Buscar
Asignar
Desasociar
Clasificación
Profesional
```

Do not wrap these character-by-character.

If the word still cannot fit:

```text
move it to its own row
or rebalance columns
```

---

# 7. Symbols and directional controls

Single-character symbols are allowed only when they truly represent the control.

Examples:

```text
<
>
v
```

But they must not appear as accidental detached layout artifacts.

For transfer controls between lists, prefer a coherent human representation only if direction is supported:

```text
[Asignar →]
[← Desasociar]
```

Otherwise:

```text
[Asignar]
[Desasociar]
```

is preferable.

---

# 8. Documentary reconstruction, not literal DOM layout

Keep this product principle:

> **The wireframe is a documentary reconstruction, not a pixel-perfect reproduction of the legacy markup.**

Therefore it is valid to:

```text
rebalance columns
group related controls
normalize icon/button labels
move small helper labels
use consistent spacing
simplify purely structural table cells
```

as long as the reconstruction preserves:

```text
visible controls
functional grouping
relative relationships
meaning
known actions
```

Do not preserve broken legacy table geometry when it harms comprehension.

---

# 9. Remove source line numbers from human documentation

Remove provenance suffixes such as:

```text
(línea 68)
(línea 81)
(línea 149)
(línea 251)
(línea 334)
(línea 684)
```

from human HTML/PDF.

Remove them from:

```text
messages
actions
popup descriptions
behavior prose
technical narrative
```

Example:

Current:

```text
Puede mostrar el mensaje «Debe Ingresar Fecha de Inicio» (línea 146).
```

Target:

```text
Puede mostrar el mensaje «Debe Ingresar Fecha de Inicio».
```

Keep exact source locations in:

```text
ai/provenance.json
internal/
Evidence
```

Do not destroy traceability.

---

# 10. Replace audit language in human prose

The human document still uses phrases such as:

```text
La evidencia muestra...
La evidencia confirma...
La evidencia no precisa...
La evidencia permite seguir...
según la evidencia...
Evidencia de uso
```

These should generally become direct documentary language.

Preferred:

```text
La vista muestra...
El análisis confirma...
No se pudo determinar...
La ruta observable llega hasta...
Uso observable
Qué se conoce
Qué no pudo determinarse
```

Use context-sensitive wording.

Do not mechanically replace every occurrence if it changes meaning.

Principle:

> **The human document explains the system; it does not narrate the Evidence engine.**

---

# 11. Rename “Evidencia de uso”

In human documents rename:

```text
Evidencia de uso
```

to:

```text
Uso observable
```

or equivalent natural human wording.

---

# 12. Human state legend: only three states

For the normal human document, show only:

```text
Confirmado
Inferido
No resuelto
```

Recommended visual mapping:

```text
AZUL     Confirmado
NARANJA  Inferido
ROJO     No resuelto
```

Use both color and text/border.

Keep governance states such as:

```text
AI_INTERPRETATION
CANONICAL
```

in machine/governance models (`ai/`, `internal/`), not in the primary human legend.

---

# 13. Single AI notice

Keep exactly one introductory explanation similar to:

```text
Interpretación asistida por IA

Este documento presenta una interpretación generada por IA
a partir del análisis de IST. Las afirmaciones se presentan como
Confirmadas, Inferidas o No resueltas según el respaldo disponible.
```

Do not repeat IA badges/cards throughout normal human sections.

---

# 14. Preserve useful technical detail

Do NOT remove useful technical routes.

Keep:

```text
view names
events
handlers
methods
classes
stored procedures
view-to-view relationships
messages visible to users
QueryString/session inputs when useful
```

Example to preserve:

```text
ucPreMantJerarquia2
→ hypAsignar.Click
→ hypAsignar_Click
→ PreGesJerarquia.txcrear
→ sysPreGesJerarquia.crear
→ PPRE_GES_JERARQUIA.CREAR
```

The objective is to remove provenance noise, not technical information.

---

# 15. Diagrams are frozen for this round

Do not redesign:

```text
flow simple diagrams
dependency diagrams
view invocation diagrams
data diagrams
system/project maps
```

They are considered approved by the owner.

Only fix them if a regression test proves the current presentation change accidentally breaks them.

---

# 16. Representative screen validation

At minimum visually inspect the actual rendered HTML/PDF reconstruction of:

```text
ucPreMantJerarquia2
ucBusSuc
ucPreMantEmpadronamiento
ucPreEstadisticasAccidentes
ucPreConActxProd
```

Mandatory visual assertions:

```text
no human word rendered vertically character-by-character
no detached transfer arrows
no overlapping controls
no clipped labels
no unusably narrow intermediary cells
date ranges read naturally
list-transfer controls read naturally
```

Specifically verify:

```text
ucPreMantJerarquia2:
    Asignar
    Desasociar
    transfer area

ucBusSuc:
    Criterio

ucPreConActxProd:
    Hasta
```

---

# 17. Raster/manual visual verification

This round must include rendered visual inspection.

Do not merely assert:

```text
SVG within viewBox = visual PASS
```

Both are required:

```text
structural PASS
visual human-readable PASS
```

Record representative pages/files checked in the result report.

---

# 18. Tests

Add targeted tests for:

```text
no line-number suffixes in human HTML/PDF
source line numbers remain in ai/internal provenance
human legend contains Confirmado/Inferido/No resuelto
human legend does not expose AI_INTERPRETATION/Canonical governance entries
single AI introductory notice
"Evidencia de uso" absent from primary human presentation
no human word vertically stacked character-by-character
date-range separator minimum width
transfer-action column minimum width
ucPreMantJerarquia2 action controls readable
ucBusSuc Criterio readable
ucPreConActxProd Hasta readable
diagrams unchanged semantically
ai/ unchanged semantically
```

During implementation:

```text
targeted tests only
```

At the end, once stable:

```text
python -X utf8 -m unittest discover -s tests
```

Run the full suite once.

Required:

```text
0 failures
0 errors
```

---

# 19. No AI / analysis rerun

For this round:

```text
provider calls = 0
scanner = 0
analyzer = 0
Evidence rebuild = 0
source reads = 0
```

Reuse the persisted:

```text
baseline
AI responses
knowledge model
```

---

# 20. Regeneration

Use the existing final-validation assets.

Do not rerun:

```text
01_ANALYZE_ONCE
02_INTERPRET_WITH_AI
```

Regenerate only presentation/package from persisted inputs.

Do not overwrite previous outputs.

Suggested review path:

```text
C:\PruebasLegacyMapper\FinalValidation\runs\manual_final_h4_candidate\
```

---

# 21. Files for owner review

The owner should inspect:

```text
package\human\index.html
package\human\LegacyMapper.pdf
package\human\executive.pdf
```

and specifically the representative screen reconstructions.

No need for the owner to inspect AI/internal unless traceability has accidentally been lost.

---

# 22. Result report

Create:

```text
docs/POST_V5/H4_FINAL_HUMAN_SCREEN_RECONSTRUCTION_AND_NARRATIVE_MICRO_POLISH_RESULT.md
```

Include:

```text
screen reconstruction changes
ucPreMantJerarquia2 before/after behavior
ucBusSuc label handling
ucPreConActxProd date-range handling
human provenance removed
line numbers removed
audit-language changes
human state legend changes
proof ai/internal provenance remains
visual pages inspected
provider/scanner/analyzer/source-read count
targeted tests
full suite
review path
```

---

# 23. Expected state

If technically successful:

```text
H4_FINAL_HUMAN_SCREEN_RECONSTRUCTION_AND_NARRATIVE_MICRO_POLISH
    = READY_FOR_FINAL_HUMAN_APPROVAL

H4 = HUMAN_APPROVAL_PENDING
H5 = NOT_STARTED
```

Do not close H4 automatically.

The owner has explicitly indicated that if these final corrections are satisfactory, H4 will be approved.

---

# 24. Git authority

For this task:

```text
presentation production edits = YES
tests = YES
docs/state draft updates = YES
AI provider calls = NO
scanner/analyzer = NO
commit = NO
push = NO
tag = NO
```

Do not commit, push or tag without explicit human authorization.

---

# Final principles

> **The diagrams are approved; do not redesign them.**

> **The remaining visual debt is in reconstructed screens.**

> **A documentary reconstruction may simplify legacy table geometry to improve human comprehension.**

> **No human word should be rendered as a vertical stack of characters.**

> **Humans receive interpretation; AI/internal retains provenance.**

> **If this candidate passes human review, H4 is ready to close.**
