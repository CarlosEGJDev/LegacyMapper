# LegacyMapper Post-V5 — H4-R5 Final Behavioral Documentation Correction
## AI Interpretation + Observable Usage Classification

### Round policy

This is an **exceptional fifth H4 round**, justified by human review of the H4-R4 real IST prototype.

Reason:

```text
H4-R4 proved the macro→micro structure, view discovery,
wireframe reconstruction, invocation tracing and technical paths,
but did not yet perform real AI behavioral interpretation.
```

This round must remain targeted.

Do not create further H4 micro-rounds after this one.

If this round cannot produce the expected human result, stop and re-diagnose instead of adding H4-R6.

---

# 1. Objective

Transform the H4-R4 behavioral prototype from:

```text
technical evidence + deterministic templates
```

into:

```text
technical evidence
→ behavioral context
→ AI interpretation
→ structured explanation
→ deterministic validation
→ human documentation
```

The final documentation must explain the software from macro to micro:

```text
Solution
→ Project
→ Module only if supported
→ View
→ What the view does
→ How it is reached
→ What the user can do
→ What happens for each important action
→ Which classes participate
→ What data/persistence is reached
→ What other views/popups/messages are involved
→ Whether the component is observably used
→ What remains unresolved
```

Permanent product principle:

> **The AI explains behavior; it does not merely summarize files.**

Secondary principles:

> **Macro first, micro later.**

> **The view/screen is the main unit of behavioral explanation.**

> **Existence in source code does not imply active production use.**

---

# 2. Pilot target

Continue using:

```text
Solution:
slnPREPrevencion_2010

Project:
WebPREPrevencion
```

Preserve the H4-R4 selected views unless current evidence justifies replacing one:

```text
ucPreMantEmpadronamiento
ucBusSuc
ucPreMantDepPrevencion
ucPreEstadisticasAccidentes
ucPreMantMetas
```

Do not expand to all IST yet.

---

# 3. Preserve accepted H4-R4 findings

Do not regress these results:

```text
Solution → Project → Views is correct for WebPREPrevencion
NO_SAFE_MODULE_STRUCTURE is the current result
prefixes are naming conventions, not modules
wireframe reconstruction is useful
incoming/outgoing view invocation tracing is useful
technical action paths are useful
data/persistence tracing is useful where evidence reaches it
epistemic labels are useful
```

Do not invent module boundaries.

---

# 4. Real AI interpretation is now required

H4-R4 explicitly used no provider.

H4-R5 must exercise the existing AI-only interpretation capability over **structured behavioral context**.

Do not send the raw repository indiscriminately.

For each selected view, construct a bounded behavioral context containing only relevant evidence:

```text
solution/project identity
view identity/type/title
UI controls
visible labels where known
parameters
session inputs
events
handlers
methods
related classes
incoming invocations
outgoing invocations
popup/modal relationships
confirmed technical paths
data operations
stored procedures/SQL boundaries
messages/errors
unresolved calls
usage evidence
source_refs
epistemic statuses
```

Then ask AI to produce a structured behavioral explanation.

---

# 5. AI interpretation contract

The AI should answer the human questions:

```text
What is this view for, based on observable evidence?
What can the user do here?
What happens when the view opens?
What happens for the main actions?
What information comes in?
What information is displayed/selected/changed?
Where does the request/data go?
Which classes participate?
What other views/popups are involved?
What evidence suggests this view is actually used?
What remains uncertain?
```

The AI may synthesize meaning from multiple technical facts.

The AI may **not**:

```text
invent business actors
invent requirements
invent use cases
invent module structure
invent external systems
invent database semantics beyond evidence
invent production usage
claim dead/obsolete code without proof
promote an inferred claim to confirmed
```

---

# 6. Structured AI output

Use/extend a structured schema rather than free-form-only text.

At minimum, each `ViewExplanation` should contain:

```text
view_id
simple_summary
observable_purpose
usage_status
usage_reasoning
inputs
main_actions[]
incoming_invocations[]
outgoing_invocations[]
behavior_paths[]
data_behavior
related_classes[]
messages_popups[]
ui_reconstruction_ref
known
inferred
unresolved
source_refs
```

Each important narrative field should carry:

```text
status
source_refs
reasoning_basis
```

Allowed statuses remain:

```text
CONFIRMED
INFERRED
UNRESOLVED
AI_INTERPRETATION
CANONICAL
```

AI-generated narrative stays:

```text
AI_INTERPRETATION
```

unless explicitly approved by a human.

---

# 7. New concept: observable usage

Legacy systems may contain obsolete or uncertain artifacts.

LegacyMapper must distinguish:

```text
EXISTS_IN_SOURCE
REACHABLE_FROM_OBSERVED_FLOW
OBSERVABLY_USED
```

These are not equivalent.

Add an evidence-backed usage classification for views/classes/components.

Recommended states:

```text
ACTIVE_OBSERVABLE
POSSIBLY_ACTIVE
ISOLATED
LEGACY_CANDIDATE
UNRESOLVED_USAGE
```

Semantics:

## ACTIVE_OBSERVABLE

Use only when there is positive evidence such as:

```text
confirmed incoming invocation
confirmed navigation
participation in a confirmed flow
confirmed event/action path
confirmed data path combined with observable entry relationship
```

## POSSIBLY_ACTIVE

Use when:

```text
component has meaningful code/behavior
but entry/invocation cannot be fully confirmed
```

## ISOLATED

Use when:

```text
artifact exists
and no observable incoming relationship is found
and it is not part of a resolved flow
```

This does NOT mean obsolete.

## LEGACY_CANDIDATE

Use only as a cautious candidate label when multiple indicators align, e.g.:

```text
no incoming references found
no confirmed flow participation
no recent/active navigation evidence in available static scope
duplicated/replaced-looking structure if supported
```

Never state:

```text
"unused"
"dead"
"obsolete"
```

as fact unless evidence truly proves it.

## UNRESOLVED_USAGE

Use when:

```text
dynamic loading
reflection
shell/menu indirection
configuration-driven navigation
external invocation
or incomplete analysis prevents a safe conclusion
```

Permanent rule:

> **Absence of observable usage evidence is not evidence of obsolescence.**

---

# 8. Human wording for usage

Prefer:

```text
"No se encontró evidencia observable de uso en el alcance analizado."
```

over:

```text
"Esta vista no se usa."
```

Prefer:

```text
"Su uso permanece no resuelto porque la aplicación puede cargarla dinámicamente desde el shell."
```

when applicable.

For `ACTIVE_OBSERVABLE`, explain why:

```text
"Esta vista tiene 26 invocaciones entrantes confirmadas desde otras pantallas."
```

Do not lead with the count if a simpler explanation works.

---

# 9. Human narrative format

The first section of each detailed view must now read like an explanation, not a status table.

Preferred structure:

```text
Qué hace esta vista

Esta pantalla ...
Cuando se abre ...
El usuario puede ...
Al guardar ...
La información pasa por ...
Finalmente ...
```

Then place epistemic labels and evidence underneath or inline.

Example target style:

```text
Departamento de Prevención

Esta pantalla permite mantener información relacionada con el
Departamento de Prevención y el profesional asociado.

Al abrirse, carga parámetros de apoyo. El usuario puede buscar una
persona, crear/modificar información y guardar los cambios.

La acción Guardar pasa por PrePrvDeptoPrv.txGrabar y termina en
PPRE_PRV_DEPTO_PRV.GRABAR.

También puede abrir una ventana de búsqueda de personas.

Estado de la explicación: AI_INTERPRETATION
Basada en: [source_refs...]
```

Do not overstate business meaning.

---

# 10. Progressive explanation

For each selected view, order the chapter as:

```text
A. En una frase
B. Qué hace y cómo se usa
C. Evidencia de uso
D. Cómo se llega
E. Reconstrucción visual
F. Acciones principales
G. Flujo técnico
H. Datos y persistencia
I. Clases relacionadas
J. Vistas/popups/mensajes relacionados
K. Qué sabemos / qué inferimos / qué no sabemos
L. Evidencia técnica
```

The reader should encounter technical names only after the simple behavioral explanation.

---

# 11. Move inventory out of the main story

The full catalog of 121 views must no longer occupy many early PDF pages.

Change the main reading flow to:

```text
Solution
→ Project
→ module decision
→ representative/important views
→ detailed behavioral explanations
→ cross-view behavior
→ data/persistence
→ unresolved usage/components
→ appendix/catalog
```

The full view catalog remains available:

```text
HTML navigation
appendix
search/filter
```

but it is not the primary narrative.

---

# 12. UI reconstruction

Preserve H4-R4 wireframes.

They are accepted as:

```text
DOCUMENTARY RECONSTRUCTION
NOT A SCREENSHOT
```

Do not add controls unsupported by evidence.

If AI describes the screen, validate that referenced controls/labels exist in the wireframe/evidence.

---

# 13. Deterministic validation of AI narrative

Python must validate the structured AI response.

At minimum verify:

```text
view exists
referenced controls exist where claimed
referenced events/handlers/methods exist
referenced classes exist
referenced procedures/data targets exist
incoming/outgoing invocation refs resolve or remain unresolved
usage evidence exists for ACTIVE_OBSERVABLE
CONFIRMED claims have deterministic support
AI-generated synthesis is labeled AI_INTERPRETATION
source_refs resolve
```

If AI references a nonexistent symbol:

```text
reject that claim
preserve the rest if safe
record validation issue
```

Do not silently rewrite unsupported AI output into confirmed truth.

---

# 14. Invocation target anomalies

Preserve and explicitly handle current known unresolved invocation targets:

```text
WebPrePrevencion\ucPreDirecContactosMant
webPrevencion\ucBusEmp
```

They must remain unresolved unless current evidence actually resolves them.

Do not generate broken links to them.

---

# 15. Provider strategy

Use the existing AI provider architecture.

Do not add a new provider.

Prefer a bounded prototype run with the available configured provider.

Record:

```text
provider id
model id
request count
input context size
output size
validation outcome
rejected claims
```

If no real provider is available in the execution environment:

```text
H4_BEHAVIORAL_AI_BLOCKED_PROVIDER_UNAVAILABLE
```

Do not replace real AI interpretation with templates and claim success.

A fake provider may be used only for tests.

---

# 16. Prototype output

Regenerate:

```text
C:\PruebasLegacyMapper\Resultados\post_v5_h4_behavioral_doc_prototype\
```

Include:

```text
prototype\index.html
Entendiendo_WebPREPrevencion.pdf
structured_explanation\explanations.json
structured_explanation\validation_report.json
AI_INTERPRETATION_MANIFEST.json
wireframes\
REVIEW_GUIDE.md
```

The HTML/PDF should make it obvious which text came from AI interpretation.

---

# 17. Human review focus

Update `REVIEW_GUIDE.md`.

Questions:

```text
1. ¿Ahora puedo explicar qué hace WebPREPrevencion sin abrir código?
2. ¿La lectura va realmente de macro a micro?
3. ¿La explicación de cada vista es humana y no una lista de artefactos?
4. ¿Entiendo qué ocurre cuando realizo una acción importante?
5. ¿Puedo seguir la acción hasta clases/datos cuando existe evidencia?
6. ¿Los popups y ventanas explican quién los invoca y qué hacen?
7. ¿El wireframe ayuda a reconocer la pantalla?
8. ¿La documentación distingue existencia, uso observable y uso no resuelto?
9. ¿Evita llamar obsoleto/no usado a algo sin evidencia suficiente?
10. ¿Las interpretaciones de IA están claramente separadas de hechos confirmados?
11. ¿El catálogo completo quedó relegado a navegación/apéndice?
12. ¿Esto es sustancialmente más útil que el PDF H4 original y que H4-R4?
```

---

# 18. Tests

Add targeted tests for:

```text
AI behavioral schema
AI narrative validation
fabricated symbol rejection
fabricated procedure rejection
AI status remains AI_INTERPRETATION
usage classification rules
ACTIVE_OBSERVABLE requires positive evidence
ISOLATED does not become OBSOLETE
LEGACY_CANDIDATE wording remains cautious
dynamic/shell entry becomes UNRESOLVED_USAGE when appropriate
wireframe references remain valid
catalog moved to appendix
deterministic rendering from validated explanation
```

Run directed tests.

If production code changes, run:

```text
python -X utf8 -m unittest discover -s tests
```

Require:

```text
0 failures
0 errors
```

---

# 19. Baseline integrity

Do not rerun the entire IST deterministic analysis.

Reuse the persisted baseline.

Additional source reads are allowed only where H4-R4 already required them for:

```text
UI markup
code-behind invocation literals
```

Document any such read as:

```text
read-only enrichment
```

Do not mutate source or baseline.

Require:

```text
baseline delta = 0
scanner/analyzer full rerun = 0
```

---

# 20. Result document

Update/create:

```text
docs/POST_V5/H4_BEHAVIORAL_DOCUMENTATION_PROTOTYPE_RESULT.md
```

Append:

```text
H4-R5 Final Behavioral Documentation Correction
```

Include:

```text
AI provider/model
behavioral context contract
structured AI schema
usage classification model
selected views
before/after examples
validation results
rejected AI claims
HTML/PDF changes
tests
baseline integrity
known limitations
human review path
Git status
recommendation
```

Final state exactly one of:

```text
H4_BEHAVIORAL_AI_READY_FOR_HUMAN_REVIEW
H4_BEHAVIORAL_AI_CORRECTION_FAILED
H4_BEHAVIORAL_AI_BLOCKED_PROVIDER_UNAVAILABLE
H4_BEHAVIORAL_AI_BLOCKED_BY_EVIDENCE
```

Do not mark global H4 CLOSED automatically.

---

# 21. PROJECT_STATE

Record truthfully:

```text
H4 packaging = technically validated
H4 behavioral documentation = human-review correction in progress/result
H5 = NOT_STARTED
```

If this round succeeds technically:

```text
h4_behavioral_ai = READY_FOR_HUMAN_REVIEW
```

Do not set H4 CLOSED until the human explicitly approves the resulting artifact.

---

# 22. Git authority

For H4-R5:

```text
edit production code = YES, targeted
edit tests = YES
edit docs/state = YES

commit = NO
push = NO
tag = NO
```

No versioning without explicit human authorization.

---

# 23. Success criterion

This round succeeds only if the prototype lets a human read:

```text
Solution
→ Project
→ View
→ what the view does
→ how it is used
→ what happens for important actions
→ what classes participate
→ where data goes
→ what other views/popups participate
→ what evidence exists that the component is active
→ what remains unresolved
```

and the human can reasonably say:

> **"Ahora entiendo cómo funciona el proyecto, no solo qué archivos contiene."**

If that does not happen, stop H4 and re-diagnose the product model instead of adding another implementation round.
