# LegacyMapper Post-V5 — H2-R2 Targeted Correction
## Functional projection readability correction

Complete this as one targeted correction round. H2 architecture is accepted. `executive` and `technical_overview` are accepted. Correct only the real human-review finding:

> The `functional` profile is still too close to a technical trace inventory (`screen → event → stored procedure`) and does not yet provide enough functional reading value for analysts.

Do not reopen H1. Do not redesign H2. Do not start H3.

## Read first

Read current repo state plus:

```text
AGENTS.md
CLAUDE.md
PROJECT_STATE.json
docs/POST_V5/H2_HUMAN_DOCUMENTATION_BY_AUDIENCE_RESULT.md
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
C:\PruebasLegacyMapper\Resultados\post_v5_h2_human_review\REVIEW_GUIDE.md
```

Inspect the current generated sample:

```text
executive/README.md
functional/areas/slnPREPrevencion_2010.md
functional/processes-part-000001.md
functional/unresolved.md
technical_overview/modules/WebPrePrevencion.md
technical_overview/dependencies.md
```

Preserve this review result:

```text
Executive          = PASS
Technical-overview = PASS
Functional         = PARTIAL
```

## Objective

Make the functional profile useful to a functional/business analyst **without inventing business meaning**.

Current weak pattern:

```text
technical screen
→ technical event
→ stored procedure
```

Target:

```text
observable interaction
→ cautious human-readable action category
→ technical evidence as traceability
→ unsupported business intent remains unresolved
```

Example source evidence:

```text
ucPreContactosDir2.ascx
→ Click
→ PPRE_CONTACTOS.GRABA_DIRECCIONES
```

Allowed wording:

```text
Acción observable: interacción de escritura detectada.
Operación técnica: PPRE_CONTACTOS.GRABA_DIRECCIONES.
Propósito de negocio: no determinado por evidencia.
```

Not allowed without independent evidence:

```text
El usuario actualiza la dirección de una empresa.
Esta pantalla gestiona contactos comerciales.
```

## Deterministic action classification

Use existing Evidence operation kind if available. Only if needed, add a conservative presentation-only classifier such as:

```text
READ / SELECT / GET / TRAER / LEER / BUSCAR / CONSULTAR
→ Consulta / lectura

INSERT / CREATE / CREAR / GRABAR / REGISTRAR
→ Registro / creación

UPDATE / MOD / MODIFICAR / ACTUALIZAR
→ Modificación

DELETE / ELIMINAR / BORRAR
→ Eliminación

unknown / mixed
→ Operación de datos observada / Mixta
```

Rules:

```text
presentation-only
deterministic
tested
never business intent
mixed operations are not falsely collapsed
no Evidence/schema/analyzer changes
```

## Functional information architecture

Make the primary reading order:

```text
Área
→ resumen funcional observable
→ pantallas con actividad
→ tipo de interacción observable
→ dato/operación involucrada
→ no resuelto
→ trazabilidad técnica
```

Prefer sections like:

```text
Resumen funcional observable
Pantallas con actividad identificada
Interacciones de consulta
Interacciones de registro/creación
Interacciones de modificación
Interacciones de eliminación
Operaciones mixtas/no clasificadas
Procesos cuya finalidad de negocio no puede determinarse
Trazabilidad técnica
```

Omit empty sections.

The raw `processes-part-*` table may remain, but as drill-down/traceability rather than the primary functional experience.

## Area page

Improve pages like:

```text
functional/areas/slnPREPrevencion_2010.md
```

Prefer a human-readable table such as:

```text
Pantalla
Acción observable
Tipo de interacción
Dato/operación involucrada
Estado
```

Keep original identifiers visible for traceability, but do not let them dominate the explanation.

## Global processes

Before raw process rows, add a functional summary with at least:

```text
count by action category
count by area/project
top screens with observable interactions
count unresolved
```

Then link to detailed rows.

A functional reader must not need to scan hundreds of technical rows to understand what was observed.

## Unresolved

Improve `functional/unresolved.md` with a human-readable summary before technical calls.

Explain:

```text
what "unresolved" means
how much behavior is affected
which projects/areas are most affected
why the analyzer stops there
what must not be inferred
```

Then retain technical details such as `dbc.Rollback()` or `InitializeComponent()` as drill-down evidence.

Do not hide or reduce unresolved counts.

## AI/provider behavior

This correction must not require AI.

```text
provider calls = 0
source re-analysis = 0
```

Preserve existing H2 precedence and labeling for proposals/canonical knowledge.

## Tests

Add/adjust focused tests proving:

```text
functional primary view is no longer raw screen/event/SP inventory
action categories are deterministic and conservative
read/write/update/delete/unknown/mixed are handled correctly
business intent is never invented
technical identifiers remain traceable
raw technical detail remains reachable
unresolved summary precedes technical unresolved detail
empty action categories are omitted
executive is unchanged except unavoidable shared metadata
technical_overview is unchanged except unavoidable shared metadata
rerun is byte-identical
no provider calls
no source analysis stages
```

Run directed tests, then:

```text
python -X utf8 -m unittest discover -s tests
```

Require:

```text
0 failures
0 errors
```

Record exact totals.

## IST validation

Reuse the existing persisted IST baseline. Do not rerun deterministic analysis.

Regenerate the functional projection and refresh:

```text
C:\PruebasLegacyMapper\Resultados\post_v5_h2_human_review\
```

for the same area `slnPREPrevencion_2010`.

At minimum refresh:

```text
functional/areas/slnPREPrevencion_2010.md
functional/processes-part-000001.md
functional/unresolved.md
```

Verify:

```text
baseline deterministic delta = 0
provider calls = 0
broken links = 0
functional rerun byte-identical
```

Do not self-declare human acceptance.

## Documentation/state

Update:

```text
docs/POST_V5/H2_HUMAN_DOCUMENTATION_BY_AUDIENCE_RESULT.md
docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md
PROJECT_STATE.json
```

Remove stale roadmap text that still recommends H1-R1 as next.

If clean:

```text
H2_HUMAN_DOCUMENTATION_BY_AUDIENCE = IMPLEMENTED_AND_VALIDATED
H2_HUMAN_REVIEW = READY_FOR_FINAL_HUMAN_CONFIRMATION
NEXT = H3_STRUCTURED_VISUAL_PROJECTIONS
```

Add a section to the existing H2 result:

```text
H2-R2 Targeted Functional Readability Correction
```

Include before/after examples, tests, IST regeneration, baseline delta, provider calls, limitations, sample path, Git status and recommendation.

Final state must be one of:

```text
H2_READY_FOR_FINAL_HUMAN_REVIEW
H2_TARGETED_CORRECTION_REQUIRED
H2_BLOCKED
H2_OPEN_DECISION
```

## Git authority

```text
edit production code = YES, only functional projection/readability scope
edit tests = YES
edit docs/state = YES
commit = NO
push = NO
tag = NO
```

Leave H1 + H2 accumulated changes in the working tree.

## Non-goals

Do not implement:

```text
H3 diagrams
H4 HTML/PDF packaging
business-domain inference from prefixes
AI-generated business summaries
new provider
Evidence/schema changes
analyzer changes
adapter changes
large refactor
V6
```

## Success criterion

A functional analyst can understand:

```text
where interaction occurs
what kind of technical action is observable
what data operation is involved
what remains unknown
```

without opening source code and without LegacyMapper inventing business meaning.
