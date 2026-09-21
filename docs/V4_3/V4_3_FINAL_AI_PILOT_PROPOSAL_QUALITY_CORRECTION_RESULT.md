# V4.3 — Corrección de calidad de propuestas del piloto final de IA (resultado)

Ejecuta `prompts/V4_3/V4_3_FINAL_AI_PILOT_PROPOSAL_QUALITY_CORRECTION_PROMPT.md`.

Estado de entrada: V4.3-R0–R8 aprobados, corrección pre-cierre de Copilot y de
distribución completadas, piloto final real ejecutado (`AI_INTERPRETATION`:
SUCCESS, `PROPOSAL_GENERATION`: SUCCESS, modelo `gpt-5.6-luna`, 8 propuestas,
sin conocimiento canónico, sin aprobación del Technical Lead). R9 no se ejecuta
en esta tarea.

---

## 1. Hallazgo del piloto real

Las 8 propuestas del piloto final seguían casi todas el mismo patrón:

```text
<entry point> has no recorded data operations and ends at an unresolved node.
```

Ejemplo:

```text
The dgrVariables_DataBinding DataBinding entry point in
webIndemnizacion\ucINDProcesosIndividualesFIN.ascx
has no recorded data operations and ends at an unresolved node.
```

`CopilotProvider`, el runtime de IA, el structured output y el runtime de
generación de propuestas funcionaron correctamente. El problema estaba,
exclusivamente, en qué flows llegan a consumir los slots limitados que ve la
IA.

---

## 2. Causa raíz

La selección determinista de candidatos vive en
[`legacy_documenter/context/ai_projection.py`](../../legacy_documenter/context/ai_projection.py),
en dos puntos:

1. **`select_flow_ids(ix, max_flows)`** (pre-hidratación): filtra
   `ix["functional_flows"]` y ordena por `(CONFIDENCE_ORDER[flow.confidence],
   flow_id)`, truncando a `max_flows` (80 para el perfil `SMALL`, el que usa
   `run_ai_interpretation` por defecto).
2. **`AiProjectionBuilder.package(records, ...)`** (post-hidratación): vuelve a
   ordenar los registros ya hidratados con la misma clave
   `(CONFIDENCE_ORDER[record.confidence], flow_id)` y trunca por
   `max_records` y por un recorte greedy de caracteres hasta el presupuesto.

Ninguno de los dos puntos miraba nunca `data_operations`, `transactions`,
`terminals.stored_procedures`/`sql_operations`, ni la mezcla de confidence por
path — solo la etiqueta agregada `confidence` del flow (que mide si la
*extracción de evidencia* fue confiable, no si el *terminal alcanzado* está
resuelto) y el `flow_id` como desempate. Un flow puede tener
`confidence="confirmed"` y aun así terminar en un `unresolved_boundary` sin
ninguna operación de datos registrada — exactamente el patrón que dominó el
piloto. Al ordenar solo por esa etiqueta agregada, un repositorio con muchos
flows de ese tipo terminaba llenando los 80 slots del perfil `SMALL` (y, tras
el recorte por presupuesto de caracteres en `package()`, los slots finales que
la IA efectivamente vio) casi enteramente con ese patrón, sin importar que
existieran flows con SPs, transacciones o escrituras confirmadas en el mismo
repositorio.

`adapt_findings_to_proposals` (`legacy_documenter/orchestration/proposal_adapter.py`)
y `_validate_findings` (`legacy_documenter/orchestration/ai_interpretation.py`)
no imponen ningún límite ni orden propio: pasan 1:1 los `findings` que el LLM
devuelve. Las "8 propuestas" del piloto no son un tope determinista — son,
simplemente, cuántos `findings` decidió devolver el modelo dado el conjunto de
flows (mayoritariamente triviales) que se le mostró.

---

## 3. Algoritmo anterior

```text
ordered = sorted(flows_o_records, key=(CONFIDENCE_ORDER[confidence], flow_id))
selected = ordered[:max_flows_o_max_records]
```

Aplicado igual en `select_flow_ids` (sobre flows crudos) y en
`AiProjectionBuilder.package` (sobre registros ya hidratados, antes del
recorte por presupuesto de caracteres).

---

## 4. Algoritmo nuevo

Se añadió una clave de diversidad **ortogonal a `confidence`** (nunca la lee
ni la reordena) que clasifica cada candidato en uno de 4 buckets, de más rico
a más trivial, usando exclusivamente evidencia ya calculada:

```text
bucket 0: terminal resuelto (stored_procedure / sql) O escritura confirmada
          (INSERT/UPDATE/DELETE/MERGE) O transacción confirmada
bucket 1: cualquier otra operación de datos confirmada
bucket 2: diversidad secundaria — evidencia confirmed+unresolved mezclada,
          múltiples componentes participantes, o múltiples evidence_refs
bucket 3: sin operaciones de datos y terminal unresolved (el patrón
          homogéneo que produjo el piloto)
```

Dentro de cada bucket, el orden sigue siendo el mismo de siempre:
`(CONFIDENCE_ORDER[confidence], flow_id)` — el desempate nunca cambió.

Entre buckets, `_bucketed_order` (nueva función privada en `ai_projection.py`)
hace un *round-robin* determinista: toma un elemento del bucket 0, luego del
1, del 2, del 3, y repite, hasta agotar todos los candidatos. Esto evita que
el bucket trivial (3) agote el cupo antes de que buckets más ricos aporten
algo, sin necesidad de fijar cuotas exactas por categoría — si un bucket está
vacío, el round-robin simplemente lo salta (degradación seguro: "si no hay
candidatos ricos, usar los disponibles").

Dos versiones de la clasificación por bucket, ambas puras y sin mutar nada:

- `_flow_richness_bucket` (pre-hidratación, usada por `select_flow_ids`): lee
  directamente `ix["functional_paths"]` (campos `terminal_type`, `nodes`,
  `terminal_target`, `confidence`, `evidence_refs`, ya presentes sin
  hidratar) y `ix["data_access"]` (`sql_operation`, `operation_kind`,
  `confidence`) — los mismos campos crudos que `EvidenceHydrator` ya lee, sin
  invocar el hidratador ni reimplementar su lógica.
- `_record_richness_bucket` (post-hidratación, usada por
  `AiProjectionBuilder.package`): lee los campos que
  `EvidenceHydrator.hydrate_flow` ya calculó (`terminals`, `data_operations`,
  `transactions`, `paths`, `projects`).

`select_flow_ids` decide **qué flows entran en la hidratación** (evita que el
bucket trivial ya condicione la muestra antes de siquiera hidratar); `package`
decide, sobre los ya hidratados, **qué sobrevive al recorte por presupuesto de
caracteres** — sin este segundo ajuste, el recorte por presupuesto (que
también se hacía por `(confidence, flow_id)`) podía volver a deshacer la
diversidad que `select_flow_ids` ya había logrado.

No se modificó `hydration.py`, `consumer_projection.py`, ni ninguna semántica
de `confidence`/`terminal resolution`. No se introdujo ninguna llamada LLM,
ranking por IA, ni aleatoriedad.

---

## 5. Por qué sigue siendo determinista

- Sin `random`, sin llamadas a IA, sin heurísticas basadas en interpretación.
- Los buckets se calculan una sola vez a partir de campos ya presentes en `ix`
  o en el registro hidratado; el mismo `ix`/conjunto de registros produce
  siempre los mismos buckets.
- El desempate dentro de cada bucket (`CONFIDENCE_ORDER`, luego `flow_id`
  ascendente) es estable y ya existía.
- El recorrido round-robin entre buckets es un bucle `for` sobre claves fijas
  `(0, 1, 2, 3)` — nunca depende de orden de iteración de diccionarios no
  contractual.
- Cubierto por T3 (`test_select_flow_ids_is_stable_across_repeated_calls`,
  `test_select_flow_ids_is_stable_regardless_of_input_flow_order`,
  `test_package_ordering_is_stable_across_repeated_calls`) y T4
  (desempates).

---

## 6. Cómo se evita la homogeneidad de candidatos

Con un `max_flows`/`max_records` pequeño y un conjunto mixto disponible, el
round-robin garantiza que los primeros N slots recorran los buckets 0→3 antes
de repetir un bucket — el bucket trivial (3) nunca puede agotar el cupo por sí
solo mientras existan candidatos en 0, 1 o 2. Verificado sintéticamente en
`tests/test_v4_3_final_ai_pilot_proposal_quality_correction.py`
(`T2MixedCandidateSetTests`, `RichnessBucketDiversityTests`) con un fixture
equivalente al de la sección 14 del prompt (FLOW-A trivial, FLOW-B con
stored procedure, FLOW-C con transacción, FLOW-D con escritura, FLOW-E con
evidencia mixta, FLOW-F trivial): con límite 4, la selección nunca queda
reducida a `{FLOW-A, FLOW-F}`.

## 7. Degradación cuando no existen candidatos ricos

Cuando todos los candidatos caen en el bucket 3 (dataset homogéneo, T1), los
buckets 0-2 quedan vacíos, el round-robin los salta sin error y devuelve los
candidatos disponibles del bucket 3 en el mismo orden estable de siempre. No
hay ninguna condición que falle por ausencia de una categoría — cubierto por
`T1HomogeneousTrivialSetTests`.

---

## 8. Tratamiento de confidence / rationale

Se revisó la combinación observada en el piloto:

```text
Rationale: AI-proposed interpretation (confidence: CONFIRMED).
Statement: ... ends at an unresolved node.
```

`confidence: CONFIRMED` en el rationale **no es** la `confidence` determinista
del flow (`confirmed`/`inferred`/`unresolved`, calculada por el pipeline
determinista y usada por la selección). Es el valor `"CONFIRMED"|"UNCERTAIN"`
que el propio LLM reporta sobre **su propia observación**, definido en el
esquema de `USER_INSTRUCTION`
(`legacy_documenter/orchestration/ai_interpretation.py`) y consumido
literalmente por
`adapt_findings_to_proposals` (`rationale=f"AI-proposed interpretation
(confidence: {finding.get('confidence', 'UNCERTAIN')})."`,
`legacy_documenter/orchestration/proposal_adapter.py`). Es, por tanto, una
afirmación de confianza de la IA sobre su propia declaración ("estoy seguro de
que este flow no tiene operaciones registradas"), no una promoción ni una
reinterpretación de la confidence de evidencia del flow — ambos valores son
independientes y coexisten sin conflicto de contrato, aunque comparten
vocabulario (`CONFIRMED`/`unresolved`) que puede confundir a un lector humano.

Es una colisión de nomenclatura documentable, no un defecto funcional: no se
modificó `confidence` en ningún punto (verificado por T5), no se corrigió
código porque no hay una confidence de evidencia mal usada — el rationale
etiqueta correctamente lo que es (confianza del hallazgo de la IA). Se deja
documentado aquí para que un futuro round de UX de propuestas considere
renombrar ese campo (p.ej. `ai_confidence` vs. `flow_confidence`) para evitar
la ambigüedad visual.

---

## 9. Idioma de las propuestas — conclusión

`SYSTEM_INSTRUCTION`/`USER_INSTRUCTION`
(`legacy_documenter/orchestration/ai_interpretation.py:80-100`) están
escritas en inglés en código, y no existe ninguna plantilla externa bajo
`prompts/V4_3/` que el runtime cargue — esos archivos son documentos de
diseño/proceso, no plantillas de prompt. El texto de cada `statement` es la
salida verbatim del LLM (`proposal_adapter.py:33`,
`statement=finding["statement"]`), así que el inglés observado en el piloto
es una consecuencia directa de que el modelo respondió en el idioma de la
instrucción que recibió.

`PROJECT_STATE.json` define `human_documentation_language: "ES"`, pero ese
contrato es explícitamente para `HUMAN_DOCUMENTATION.md` (la documentación
narrativa para humanos, ya estandarizada en español en Post-V4.2). No existe
ningún contrato vigente que declare el idioma esperado de `AI_PROPOSALS.json`
— es un artefacto distinto (propuestas para revisión del Technical Lead, no
documentación humana final). Cambiar `SYSTEM_INSTRUCTION`/`USER_INSTRUCTION`
tocaría el runtime de IA ya validado por el piloto real (fuera del alcance de
esta corrección, que es exclusivamente de selección de candidatos) y no está
cubierto por ningún contrato explícito.

**Conclusión: se documenta como deuda, no se amplía el alcance de esta tarea.**
Deuda registrada en la sección 15.

---

## 10. Archivos modificados

- `legacy_documenter/context/ai_projection.py` — `select_flow_ids` y
  `AiProjectionBuilder.package` ahora usan `_bucketed_order` con
  `_flow_richness_bucket`/`_record_richness_bucket` en lugar de un `sorted`
  puro por `(confidence, flow_id)`. Se agregaron `_WRITE_OPERATIONS`,
  `_richness_bucket`, `_bucketed_order`, `_flow_richness_bucket`,
  `_record_richness_bucket` como funciones privadas del módulo.

Ningún otro archivo de producción fue modificado. No se tocó `hydration.py`,
`consumer_projection.py`, `CopilotProvider`, `requirements-copilot.txt`, el
distribution builder, `ProviderRegistry`, V5, Plugin Runtime, detección de
tecnología, ni `PROJECT_STATE.json`.

---

## 11. Tests agregados

`tests/test_v4_3_final_ai_pilot_proposal_quality_correction.py` (23 tests
nuevos), cubriendo T1–T9 del prompt más verificación explícita de diversidad
(sección 14):

- `T1HomogeneousTrivialSetTests` (3) — dataset 100% trivial: selección válida,
  determinista, sin fallo.
- `T2MixedCandidateSetTests` (3) — dataset mixto: la selección no queda
  reducida a la categoría trivial; el recorte de `package()` por presupuesto
  tampoco descarta toda la riqueza antes que lo trivial.
- `T3StableOrderingTests` (3) — misma entrada, misma salida, en
  `select_flow_ids` y en `package()`.
- `T4TieBreakTests` (2) — empates de bucket/confidence se resuelven por
  `flow_id` ascendente.
- `T5NoConfidenceMutationTests` (3) — confidence de flow/path/terminal
  inalterada tras seleccionar/empaquetar.
- `T6EvidencePreservationTests` (2) — ids de evidencia originales preservados.
- `T7CandidateLimitTests` (2) — `len(selected) <= límite` respetado.
- `T8NoLLMDependencyTests` (2) — sin imports de `legacy_documenter.llm` ni de
  Copilot; ejecuta sin proveedor.
- `T9ExistingRegressionTests` (1) — superficie pública de R5 preservada.
- `RichnessBucketDiversityTests` (2) — fixture equivalente a la sección 14
  del prompt (FLOW-A…F); verifica que la selección de 4-de-6 no colapsa a
  `{FLOW-A, FLOW-F}` y que el orden de buckets es el esperado.

---

## 12. Resultados

Tests específicos del selector/propuestas (`test_v4_3_final_ai_pilot_proposal_quality_correction`):

```text
Ran 23 tests
OK
```

Tests V4.3 relevantes (`test_v4_3_r2_evidence_hydration`,
`test_v4_3_r3_human_documentation`, `test_v4_3_r4_scaling_and_partitioning`,
`test_v4_3_r5_ai_context_budgeting`, `test_v4_3_r6_ai_and_consumer_projection`,
`test_v4_3_r7_internal_acceptance`, `test_v4_3_r8_external_pilot_corrections`,
`test_v4_3_pre_closure_copilot_provider_correction`,
`test_v4_2_r4_ai_interpretation_and_proposal_integration`, más la propia suite
de esta corrección):

```text
Ran 345 tests
OK
```

Suite completa (`python -m unittest discover -s tests`):

```text
total:    2121
passed:   1989
failed:   0
errors:   0
skipped:  132
```

(Baseline previo: 2098 tests, 1966 passed, 0 failed, 0 errors, 132 skipped —
la diferencia es exactamente los 23 tests agregados por esta corrección;
`0 failed`/`0 errors` se mantiene.)

---

## 13. Runtime Independence

- `ai_projection.py` sigue sin importar `legacy_documenter.llm` ni ningún
  proveedor (verificado por `T8NoLLMDependencyTests` vía AST, y por los tests
  preexistentes `RuntimeIndependenceTests` de
  `test_v4_3_r5_ai_context_budgeting.py`, que siguen pasando sin cambios).
- Ningún test nuevo llama a Copilot real, red, ni ningún `LLMProvider`.
- La corrección es puramente de reordenamiento/selección sobre estructuras en
  memoria ya calculadas.

**RUNTIME INDEPENDENCE: PASS**

---

## 14. Restricciones verificadas

| Restricción | Estado |
|---|---|
| No modificar `CopilotProvider` | Cumplido — no tocado |
| No modificar `requirements-copilot.txt` | Cumplido — no tocado |
| No modificar distribution builder | Cumplido — no tocado |
| No modificar `consumer_projection` | Cumplido — no tocado |
| No modificar semántica de `hydration` | Cumplido — `hydration.py` no tocado |
| No modificar `flow confidence` | Cumplido — nunca se lee ni escribe en la selección; T5 lo verifica |
| No modificar `terminal resolution` | Cumplido — `hydration.py` no tocado |
| No modificar R8 presentation logic | Cumplido — no tocado |
| No modificar `ProviderRegistry` | Cumplido — no tocado |
| No modificar V5 / Plugin Runtime / detección de tecnología | Cumplido — no tocados |
| No modificar `PROJECT_STATE.json` | Cumplido — no tocado |
| No ejecutar R9 | Cumplido |
| No declarar V4.3 cerrada | Cumplido |
| No cambiar el modelo configurado | Cumplido |
| No llamar Copilot real desde tests | Cumplido (T8) |
| No incorporar outputs reales del piloto como fixtures | Cumplido — fixtures 100% sintéticas |
| Selección determinista, sin LLM para ranking/filtering/scoring | Cumplido |
| No reducir evidence package / cambiar budget / truncar evidencia / cambiar `measure_request_payload` / cambiar schema de AI request | Cumplido — ningún cambio en `ai_interpretation.py`, `composer.py` ni en los perfiles/presupuestos |

**RESTRICTIONS: PASS**

---

## 15. Deuda residual

- **Idioma de `AI_PROPOSALS.json`**: sigue en inglés (`SYSTEM_INSTRUCTION`/
  `USER_INSTRUCTION` hardcodeadas). No hay contrato vigente que exija español
  para este artefacto específico; si un futuro round decide extender el
  estándar de español (`human_documentation_language: "ES"`) a las
  propuestas de IA, deberá tratarse como su propio cambio de alcance (afecta
  el runtime de IA validado por el piloto real, no solo la selección de
  candidatos).
- **Nomenclatura `confidence` en el rationale de propuestas**: el campo
  `confidence` de un finding es la confianza que el LLM declara sobre su
  propia observación, distinta de la `confidence` de evidencia del flow
  (`confirmed`/`inferred`/`unresolved`). Ambas conviven sin conflicto de
  contrato, pero comparten vocabulario. Documentado como candidato a
  renombrado en un futuro round de UX de propuestas (no se tocó código: no es
  un defecto, es una colisión de nombres).

---

## 16. Estado final

```text
V4_3_READY_FOR_FINAL_AI_PILOT_RERUN
```

No se ejecutó R9. No se declaró V4.3 cerrada. No se ejecutó el piloto real
(instrucciones para el rerun en
`docs/V4_3/V4_3_FINAL_AI_PILOT_RERUN_INSTRUCTIONS.md`).
