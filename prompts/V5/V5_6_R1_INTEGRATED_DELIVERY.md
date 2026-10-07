# LegacyMapper V5.6 — R1 Integrated Delivery
## Rich Flow Segmentation

## 1. Objetivo

Implementar V5.6 en una sola ronda integrada siguiendo el modelo vigente:

```text
R1 — Integrated Delivery
R2 — Targeted Corrections solo si son necesarias
R3 — Final Verification & Closure
```

Objetivo de V5.6:

> Resolver flows demasiado grandes sin truncación silenciosa y con provenance completa.

Contrato mínimo heredado del roadmap:

```text
parent_flow_id
partial = true
included_paths
omitted_paths
evidence_refs
```

Principio obligatorio:

```text
un segmento nunca se presenta como flow completo
```

y:

```text
si existe omisión
→ debe ser explícita, trazable y verificable
```

V5.6 NO cambia la verdad del Evidence Core.
V5.6 NO adelanta aprobación/canonicalización de V5.7.
V5.6 NO implementa plugin runtime ni multi-tech pilot.

---

## 2. Estado de partida

V5.5 está cerrada y publicada.

Commit efectivo V5.5:

`6b8a8138ab6aa90969067fc2b0b63c0671fb07df`

Estado esperado:

```text
V5_5_CLOSED
V5_5_R3_PUSHED_TO_ORIGIN_MAIN
V5_6_READY_TO_START
```

V5.6 no iniciada.

Puede existir como única modificación administrativa local posterior al push:

`docs/V5/V5_5_R3_FINAL_VERIFICATION_AND_CLOSURE.md`

con su recibo post-push.

Clasificarla, preservarla y no perderla.

---

## 3. Principios heredados

Preservar:

```text
Python descubre y valida.
La IA interpreta.
```

Además:

```text
Evidence ≠ Segment
Segment ≠ Flow completo
Segment ≠ Canonical Knowledge
```

Segmentación es una proyección/partición trazable de un flow existente.

Nunca debe:

- inventar paths;
- inventar evidence_refs;
- borrar omitted paths;
- cambiar IDs de evidencia;
- promover unresolved;
- alterar confirmed/inferred/unresolved;
- auto-aprobar contenido IA;
- convertir un segmento en flow canónico.

---

## 4. Fuentes obligatorias

Leer antes de diseñar:

- `AGENTS.md`
- `CLAUDE.md`
- `PROJECT_STATE.json`
- contratos/cierre V5.0
- contrato/cierre V5.1
- cierre V5.2
- cierre V5.3
- cierre V5.4
- cierre V5.5
- `docs/V5/V5_5_R1_INTEGRATED_DELIVERY.md`
- `docs/V5/V5_5_R3_FINAL_VERIFICATION_AND_CLOSURE.md`
- ambos roadmaps/continuidad
- contratos históricos de context budgeting y flow projection relevantes
- tests actuales sobre:
  - FunctionalFlow
  - FunctionalPath
  - ai_context
  - select_flow_ids
  - hydration
  - context budget
  - documentation human flow
  - consumer projection
  - proposal grounding

Regla:

```text
contrato aprobado
> evidencia del código actual
> este prompt
> conveniencia
```

---

## 5. Gate A — Baseline empírico real

Antes de diseñar segmentación, medir flows reales.

Inspeccionar:

```text
legacy_documenter/analysis/
legacy_documenter/context/
legacy_documenter/evidence/
legacy_documenter/exporters/
legacy_documenter/documentation/
legacy_documenter/documentation_v52/
legacy_documenter/orchestration/
```

Localizar exactamente dónde se representan:

- flow;
- path;
- node/step;
- evidence refs;
- unresolved;
- hydration;
- packing;
- context selection;
- human documentation;
- ai-context.

No asumir nombres.

---

## 6. Métricas de flows sobre IST

Usar una corrida/output V5.5 verificable si está disponible.

Si la evidencia ya existe localmente y corresponde al cierre V5.5:

- no repetir análisis completo solo para medir.

Calcular como mínimo distribución de:

- paths por flow;
- steps/nodes por flow;
- evidence refs por flow;
- tamaño serializado por flow;
- tokens estimados por flow o payload;
- flows que exceden budget actual;
- flows que activan reducción/overflow;
- máximo;
- p50;
- p90;
- p95;
- p99.

Identificar al menos:

- flow grande real representativo;
- flow mediano;
- flow pequeño/control.

No persistir source crudo en el informe.

---

## 7. Baseline del problema actual

Demostrar empíricamente qué ocurre hoy cuando un flow es demasiado grande.

Clasificar comportamiento actual:

```text
COMPLETE
REDUCED
OMITTED
CONTEXT_TOO_LARGE
TRUNCATED
OTHER
```

Verificar si hoy existe alguna truncación implícita en:

- ai_context;
- consumer projection;
- documentation;
- provider package;
- human flow rendering.

Si no existe truncación silenciosa hoy, documentarlo.
V5.6 igual debe formalizar segmentación para evitarla cuando el flow excede capacidad.

---

## 8. Gate B — Diseño mínimo

No construir un graph database ni un workflow engine.

Definir el contrato mínimo de segmento.

Conceptualmente:

```text
FlowSegment
    segment_id
    parent_flow_id
    partial = true
    ordinal
    included_paths
    omitted_paths
    evidence_refs
    completeness
    segmentation_reason
```

Los nombres pueden cambiar si el proyecto ya tiene convenciones mejores.

Obligatorio:

- parent_flow_id;
- partial=true;
- included paths explícitos;
- omitted paths explícitos;
- evidence refs;
- orden determinista;
- reason/policy identificable;
- identidad determinista.

---

## 9. Identidad del segmento

`segment_id` debe ser determinista.

Debe derivarse solo de datos estables, por ejemplo:

```text
parent_flow_id
+ policy/version
+ ordered included path ids
+ ordinal
```

No usar:

- timestamp;
- random UUID;
- Python hash no estable;
- provider/model;
- wall clock.

Mismo flow + misma policy:

```text
→ mismos segmentos
→ mismos IDs
→ mismo orden
```

---

## 10. Unidad de segmentación

Decidir con evidencia real cuál es la unidad correcta:

- path completo;
- grupo de paths;
- subgraph;
- entry/branch cluster.

Preferencia:

> no partir un path internamente si puede evitarse.

Si un único path excede el límite:

- debe existir estrategia explícita;
- no truncar silenciosamente;
- marcar fragmentación interna si se implementa;
- conservar provenance exacta.

No implementar fragmentación intra-path si no es necesaria según IST real.

---

## 11. Política determinista

Definir una policy/version explícita.

Ejemplo conceptual:

```text
segmentation_policy = flow-segmentation-v1
```

La policy debe fijar:

- orden de paths;
- tamaño objetivo;
- hard limit;
- overlap si existe;
- tratamiento de path oversized;
- cálculo de omitted paths;
- completeness.

No usar IA para decidir particiones.

---

## 12. Budget integration

V5.5 ya dejó un budget neutral.

V5.6 debe integrarse sin romperlo.

Secuencia objetivo:

```text
flow
→ deterministic segmentation if needed
→ segment selection/package
→ request budget
→ provider
```

No:

```text
provider decide cómo cortar el flow
```

Segmentation threshold debe basarse en:

- límites de contexto neutrales;
- tamaño medido;
- policy determinista.

No hardcodear Copilot.

---

## 13. Completeness contract

Cada segmento debe poder decir claramente:

```text
partial = true
```

y además distinguir:

- paths incluidos;
- paths omitidos respecto del parent;
- coverage/completeness.

Una representación de parent flow completo debe seguir siendo:

```text
partial = false
```

No reutilizar un tipo parcial como si fuera completo.

---

## 14. Provenance

Cada segment debe conservar:

- `parent_flow_id`;
- included path IDs;
- evidence refs de paths incluidos;
- mapping hacia evidencia original;
- unresolved correspondiente;
- adapter/extensions cuando el consumer lo requiera.

Nunca duplicar o sintetizar refs inexistentes.

Si un path aparece en más de un segmento por overlap:

- declararlo;
- provenance idéntica;
- no generar nueva evidencia.

---

## 15. Omitted paths

`omitted_paths` es obligatorio cuando `partial=true`.

Debe representar:

```text
parent paths - included paths
```

según el contrato elegido.

No permitir:

```text
partial=true
omitted_paths desconocido
```

salvo un estado explícito y justificado por contrato.

Agregar invariantes.

---

## 16. Overlap

No introducir overlap por defecto.

Si evidencia real muestra que se necesita continuidad entre segmentos:

- permitir overlap mínimo y determinista;
- distinguir `included_paths` de `overlap_paths` si hace falta;
- no contar overlap dos veces en completeness.

Si no es necesario:

```text
overlap = none
```

---

## 17. Segmentación y AI context

Integrar V5.6 con `ai-context`.

Para un flow grande:

- seleccionar uno o más segments;
- cada request sabe que recibe un partial;
- instrucciones/context metadata indican parent flow y partial;
- provider no puede confundir el segmento con flow completo;
- finding/proposal conserva parent + segment provenance.

Si múltiples segments producen findings sobre el mismo parent:

- no consolidar automáticamente con reglas IA ad hoc;
- preservar identidad/origen;
- deduplicación solo si ya existe contrato determinista seguro.

---

## 18. Segmentación y documentación humana

Auditar si documentation human-functional/technical necesita presentar segments.

Regla preferida:

- documentación determinista del flow completo sigue derivando del flow completo cuando cabe/ya existe;
- segmentation V5.6 sirve principalmente para consumidores limitados por budget.

No degradar documentación humana actual convirtiéndola automáticamente en trozos si no es necesario.

Si segments se muestran:

- label explícito `partial`;
- link/reference al parent;
- included/omitted visibles o accesibles.

---

## 19. Segmentación y consumer projection

No romper contrato existente.

Agregar segments solo si:

- existe espacio contractual;
- pueden ser sidecar/proyección;
- consumers viejos siguen funcionando.

No cambiar schema canónico de consumers innecesariamente.

Preferir extensión compatible o artifact dedicado.

---

## 20. Persistencia

Decidir si segmentación debe persistirse o generarse on-demand.

Criterio:

- si determinista y barata, on-demand puede ser suficiente;
- si costosa/reutilizada por múltiples consumers, persistencia puede ser útil.

No crear cache nueva sin necesidad.

Si se persiste:

- contrato/version;
- deterministic write;
- write-if-changed;
- provenance;
- no source crudo.

---

## 21. Cache/fingerprints

Evaluar impacto sobre V5.3.

Regla:

- segmentación NO debe invalidar extraction cache;
- si la segmentation policy cambia, artifacts de segments deben invalidarse;
- analysis/evidence fingerprint solo cambia si realmente cambia análisis determinista upstream.

Preferencia:

```text
segmentation policy/version
→ projection/context identity
```

no:

```text
→ extraction analyzer fingerprint
```

Probarlo.

---

## 22. AI identity

V5.5 introdujo AICFG.

Para requests basados en segments, identidad/reuse debe distinguir:

- parent flow;
- segment id;
- segmentation policy/version;
- provider config AICFG.

No mezclar resultados de:

- segment A;
- segment B;
- parent completo;
- policy v1/v2.

---

## 23. Error model

Agregar estados/códigos solo si hacen falta:

- segmentation impossible;
- single path oversized;
- invalid segment;
- incomplete provenance;
- budget impossible after segmentation.

No ocultar estas condiciones como provider error.

---

## 24. Invariantes

Agregar invariantes deterministas:

Para cada segment:

```text
segment.parent_flow_id existe
segment.partial == true
included_paths no vacío
included_paths ⊆ parent.paths
omitted_paths = parent.paths - included_paths
evidence_refs ⊆ refs válidas del parent
segment_id determinista
ordinal válido
```

Si overlap existe, adaptar formalmente.

---

## 25. Fake/synthetic proof

Crear fixtures sintéticas para:

- flow pequeño → no segmentar;
- flow justo bajo límite;
- flow justo sobre límite;
- flow grande → N segments;
- path único oversized;
- unresolved paths;
- evidence refs compartidas;
- deterministic repeat;
- policy change changes IDs/identity as expected.

No depender solo de IST.

---

## 26. Real flow proof

Usar al menos un flow grande real de IST identificado en Gate A.

Demostrar:

```text
parent flow
→ N segments
→ union(included_paths) cubre parent según policy
→ omitted explícitos por segmento
→ provenance válida
→ determinismo
```

No incluir contenido sensible del flow en docs; usar IDs y métricas.

---

## 27. Tests dirigidos obligatorios

Cubrir:

### Contract
- segment fields;
- partial invariant;
- parent identity;
- deterministic IDs.

### Policy
- deterministic ordering;
- boundary conditions;
- oversized path;
- overlap/no-overlap.

### Provenance
- refs subset parent;
- unresolved preserved;
- included/omitted exactos.

### Budget
- segment fits;
- impossible after segmentation;
- provider-independent;
- no silent truncation.

### AI
- request metadata partial;
- parent + segment grounding;
- AICFG + segment identity;
- Fake provider end-to-end.

### Compatibility
- small flows unchanged;
- existing ai-context unchanged when no segmentation;
- human docs unchanged unless intentionally extended;
- consumer projection compatibility.

### Cache
- extraction cache unaffected;
- policy identity invalidates only segment-dependent artifacts.

---

## 28. Architecture guard

Agregar guard para impedir que segmentation dependa de provider concreto.

Debe ser neutral.

Permitido:

```text
context/segmentation
projection/segmentation
```

o estructura equivalente.

Prohibido:

```text
segmentation → copilot
segmentation → oracle
segmentation → webforms
```

---

## 29. Suite completa

Ejecutar:

```text
python -X utf8 -m unittest discover -s tests
```

Baseline V5.5:

```text
2907 tests
0 failures
0 errors
132 skips
```

Criterio:

```text
0 failures
0 errors
```

Corregir defectos coherentes dentro de R1.

No crear micro-rondas.

---

## 30. IST regression — deterministic outputs

V5.6 no debe cambiar Evidence Core ni outputs deterministas existentes para flows que no usan la nueva proyección.

Ejecutar regresión mínima sobre IST.

Reutilizar baseline V5.5 si verificable.

Comparar outputs canónicos existentes.

Esperado para outputs existentes:

```text
added = 0
removed = 0
changed = 0
```

salvo artifact nuevo de segmentación explícitamente fuera del comparador legacy.

No ampliar exclusiones del comparador para esconder cambios.

Si se agrega artifact nuevo, compararlo por separado.

---

## 31. Segment artifact validation

Si existe artifact nuevo:

verificar:

- schema/version;
- determinismo;
- sorted/stable output;
- write-if-changed;
- no secretos/source crudo;
- parent refs válidas;
- no orphan segments.

Ejecutar dos generaciones sobre mismo input y comparar byte a byte.

---

## 32. AI OFF regression

IA OFF debe seguir comportándose igual para outputs existentes.

Esperado:

```text
AI requested = false
AI invoked = false
real provider calls = 0
```

La presencia de segmentation code no debe activar provider.

---

## 33. Fake AI segmented end-to-end

Ejecutar flow sintético o real controlado que fuerce segmentation:

```text
large flow
→ segments
→ selected segment
→ package
→ Fake AI
→ grounded finding/proposal
```

Verificar:

- request marca partial;
- parent_flow_id presente;
- segment_id presente;
- refs solo del segment/package;
- omitted paths conocidos;
- proposal no se presenta como conocimiento del parent completo;
- canonical=false.

Sin red.

---

## 34. No auto-merge semántico

No implementar en V5.6 un sistema que combine múltiples respuestas IA y declare una interpretación global completa automáticamente.

Eso requeriría contrato separado.

Puede existir aggregation determinista de metadata:

- segment count;
- coverage;
- completed segments;
- failed segments.

Pero contenido semántico de IA debe permanecer atribuible a cada segment/proposal.

---

## 35. Performance

Medir costo de segmentación:

- tiempo total segmentation;
- segments creados;
- flows segmentados;
- tamaño before/after;
- payload reduction.

No exigir acelerar pipeline global.

Sí evitar algoritmos O(N²) innecesarios sobre flows grandes.

Registrar máximo real.

---

## 36. Maintainability audit

Antes/después registrar:

- módulos nuevos;
- responsabilidades;
- imports;
- MIXED;
- complejidad/line count observacional;
- provider-specific coupling = 0;
- technology-specific coupling = 0.

No convertir flow resolver en un módulo aún más grande si puede evitarse.

---

## 37. Seguridad

Preservar:

- no source crudo en reportes;
- no secrets;
- no prompts completos;
- source IST read-only;
- Fake para AI tests;
- provider real calls = 0.

Segment metadata puede contener IDs/rutas lógicas ya contractualmente permitidas, pero no debe volcar snippets arbitrarios.

---

## 38. Deuda permitida

Clasificar:

```text
BLOCKING
FUTURE_PHASE
OBSERVATION
```

Puede quedar FUTURE_PHASE:

- semantic aggregation multi-segment;
- adaptive AI-driven segmentation;
- cross-flow segmentation;
- plugin-facing segment API V5.8;
- second-tech stress V5.9;
- optimization/caching avanzado.

No implementar por adelantado.

---

## 39. Definition of Done R1

R1 queda lista si:

- contrato de segment explícito;
- IDs deterministas;
- partial siempre explícito;
- included/omitted correctos;
- provenance completa;
- no silent truncation;
- integración con budget neutral;
- Fake AI segmented E2E pasa;
- small flows mantienen comportamiento;
- outputs existentes equivalentes;
- suite completa verde;
- real provider calls = 0;
- no deuda BLOCKING.

---

## 40. R2 solo si hace falta

Usar R2 únicamente si hay defecto real:

- omitted incorrectos;
- segment presentado como completo;
- IDs no deterministas;
- provenance perdida;
- budget aún trunca silenciosamente;
- provider-specific coupling;
- outputs legacy divergen;
- cache incorrecta;
- suite roja.

No usar R2 para:

- mejoras cosméticas;
- semantic merge;
- V5.7 approval;
- V5.8 plugin;
- V5.9 multi-tech.

Si R1 queda limpia:

```text
R1 → R3
```

---

## 41. PROJECT_STATE

Al finalizar R1:

```text
current_version = V5.6
status = V5_6_IN_PROGRESS
latest_completed_round = V5.6-R1
latest_approved_round = V5.5-R3
round_status = V5_6_R1_READY_FOR_HUMAN_REVIEW
human_review = PENDING
v5_6_closed = false
next = HUMAN_REVIEW
```

No marcar V5.6 cerrada.

---

## 42. Continuidad

Actualizar solo estado vigente/ledger.

Registrar:

- V5.5 CLOSED;
- V5.6 R1;
- modelo máximo3 rondas;
- R2 solo si targeted correction real.

No reescribir historia.

---

## 43. Git

En R1:

- consultas permitidas;
- NO commit;
- NO push;
- NO tag;
- NO amend;
- NO rebase;
- NO clean;
- NO reset destructivo.

Registrar:

- branch;
- HEAD;
- origin/main;
- ahead/behind;
- archivos modificados/nuevos;
- recibo post-push V5.5 pendiente si existe.

---

## 44. Entregables

Crear:

`docs/V5/V5_6_R1_INTEGRATED_DELIVERY.md`

Recomendado:

`docs/V5/V5_6_R1_INTEGRATED_DELIVERY.json`

Opcional:

`docs/V5/V5_6_R1_FLOW_SEGMENTATION_INVENTORY.json`

El Markdown debe incluir:

1. Objetivo.
2. Estado inicial.
3. Fuentes.
4. Baseline flows IST.
5. Distribución/percentiles.
6. Problema actual.
7. Diseño.
8. Segment contract.
9. Identity.
10. Policy/version.
11. Budget integration.
12. Completeness.
13. Provenance.
14. Included/omitted.
15. Oversized paths.
16. AI context.
17. Human docs.
18. Consumer compatibility.
19. Persistence.
20. Cache/fingerprints.
21. AI identity.
22. Error model.
23. Invariantes.
24. Synthetic proof.
25. Real IST flow proof.
26. Tests dirigidos.
27. Suite completa.
28. IST regression.
29. Segment artifact determinism.
30. Fake AI segmented E2E.
31. Performance.
32. Maintainability.
33. Security.
34. Debt.
35. PROJECT_STATE.
36. Continuidad.
37. Git.
38. Recomendación R2/R3.
39. Estado final.

---

## 45. Estados finales permitidos

Éxito:

```text
V5_6_R1_READY_FOR_HUMAN_REVIEW
```

y exactamente una recomendación:

```text
V5_6_NEXT_R2_TARGETED_CORRECTIONS
```

o:

```text
V5_6_NEXT_R3_FINAL_VERIFICATION
```

Bloqueo:

```text
V5_6_R1_BLOCKED
```

Solo por defecto contractual/técnico real.

---

## 46. Regla final

Esta es una ronda integrada.

Ejecutar:

```text
medir flows reales
→ diseñar policy
→ implementar segmentación
→ integrar budget/context
→ corregir
→ probar
→ validar IST
→ validar Fake AI segmentado
→ auditar
→ documentar
```

No detenerse después de cada subpaso.

No activar providers reales.

No iniciar V5.7.

Detenerse al final para revisión humana.
