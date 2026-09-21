# PROMPT — V4.3 R3A (R1) — SELECTION/PACKING QUALITY CORRECTION — CORREGIDO

## 0. Contexto y estado

Repositorio LegacyMapper: `C:\dev\LegacyMapper`

Repositorio legacy real: `C:\inetpub\wwwroot\2010\IST\Operacional`

Este prompt **reemplaza** a `prompts/V4_3/V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION.md` (versión
original). La versión original queda congelada/no ejecutada; este R1 corrige una premisa numérica
internamente inconsistente de esa versión, documentada en
`docs/V4_3/V4_3_WORKSTATION_REBASELINE_RESULT.md` sección 12/18. **No ejecutar ninguna de las dos versiones
en la misma tarea que las revisa** -- este archivo se crea para una ronda FUTURA separada.

Estado vigente:
- V4.3 R0-R8 aprobados.
- R3 real (piloto): SUCCESS, 6 propuestas, pero concentradas en dead ends/unresolved/sin data operations.
- `docs/V4_3/V4_3_FINAL_AI_PILOT_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_RESULT.md`: diagnóstico determinista
  original, clasificación `DIAGNOSIS_A_SELECTION_PACKING` (0 records ricos llegan al request final) --
  **esta parte del diagnóstico se reprodujo y se confirma vigente** en un equipo nuevo
  (`docs/V4_3/V4_3_WORKSTATION_REBASELINE_RESULT.md` sección 11).
- `docs/V4_3/V4_3_WORKSTATION_REBASELINE_RESULT.md` sección 12: corrige una afirmación numérica del
  diagnóstico original ("100% de los candidatos ricos individualmente exceden el presupuesto completo") que
  es **falsa** -- 5 de 40 candidatos ricos (12.5%) individualmente caben bajo el presupuesto de 16000
  caracteres de `SMALL` y aun así quedan excluidos del paquete final.
- R9 NO debe ejecutarse. V4.3 NO debe declararse cerrada.

## 1. Causa raíz corregida (no volver a diagnosticar desde cero; sí incorporar esta corrección)

`tools/v4_3_ai_selection_diagnostic.py` + la instrumentación de solo lectura de
`V4_3_WORKSTATION_REBASELINE_RESULT.md` sección 12 demostraron, con datos reales del repositorio legacy
real, **dos capas de causa raíz, ninguna sustituye a la otra**:

```text
candidatos seleccionados (select_flow_ids, SMALL, max_flows=80): 80
  de ellos, richness bucket 0/1 ("ricos"): 40
records incluidos en el paquete final: 6
  de ellos, richness bucket 0/1: 0        <- CERO records ricos llegan al request
records ricos EXCLUIDOS por budget: 40    <- el 100% de los candidatos OFRECIDOS quedan fuera del paquete
                                              final (esto SÍ es correcto y se mantiene)

Capa 1 -- outliers reales de tamaño: 35 de 40 candidatos ricos (87.5%) exceden, cada uno por sí solo, el
  presupuesto completo de SMALL (16000 caracteres): 84948-161040 caracteres, 75-149 paths cada uno. Para
  estos, ningún reordenamiento los habría incluido enteros bajo este presupuesto.

Capa 2 -- orden de evaluación + first-fit greedy sin look-ahead (la parte que la versión original de este
  prompt no reportó): 5 de 40 candidatos ricos (12.5%) SÍ caben individualmente bajo el presupuesto completo
  (9680, 11778, 15352, 15659, 15795 caracteres) y aun así ninguno entra al paquete final. Causa exacta,
  reconstruida evaluando `AiProjectionBuilder.package` en su orden real: `_bucketed_order` itera round-robin
  entre buckets 0/1/2/3, y dentro de cada bucket ordena por `confidence` y luego `flow_id` ascendente --
  NUNCA por tamaño. Los primeros candidatos del bucket 0 en ese orden son outliers enormes (capa 1) que se
  descartan sin consumir presupuesto, pero en cada vuelta del round-robin los candidatos triviales de los
  buckets 2/3 que les toca sí se aceptan de inmediato (first-fit greedy). El presupuesto de 16000 caracteres
  queda consumido casi en su totalidad (13669 de 15311 caracteres disponibles tras descontar el envelope) por
  solo 6 records triviales (1633-5100 caracteres cada uno) aceptados en las primeras ~10 posiciones de la
  secuencia de evaluación, antes de que el packer llegue siquiera a examinar el primer candidato rico de
  tamaño razonable (posición 24 de 80). Los candidatos ricos bajo-budget nunca se comparan contra "¿cabe
  mejor que lo ya aceptado?" -- el algoritmo es estrictamente incremental e irrevocable.

payload_estimated_tokens del request final: 4648-4700 de un límite de 16000 (mucho margen sin usar --
  confirma que el problema NO es el gate final `measure_request_payload`, es el presupuesto INTERNO de
  `package()`, igual que en el diagnóstico original)
```

El presupuesto de caracteres por perfil (`composer.PROFILES["SMALL"] = (80, 16000)`,
`["TINY"] = (20, 4000)`), reutilizado sin cambios por `ai_projection.ALLOWED_PROFILES`, sigue siendo
estructuralmente incompatible con el 87.5% de los flows ricos hidratados a esta escala (capa 1) -- eso no
cambia. Lo que este R1 corrige es que el otro 12.5% de los candidatos ricos **sí cabría** si el algoritmo de
empaquetado no los dejara sistemáticamente detrás de records triviales aceptados antes en un orden fijo que
no considera tamaño (capa 2).

## 2. Objetivo exacto

Corregir la calidad de selección/empaquetado para que un request `SMALL`/`TINY` real, sobre un repositorio a
esta escala, incluya al menos evidencia rica parcial (no cero) cuando existan candidatos ricos disponibles,
sin:

1. ampliar el presupuesto de caracteres/tokens del request final (eso ya tiene margen: ~4700/16000 -- el
   problema no es el gate de `measure_request_payload`, es el presupuesto INTERNO de `package()`, ver
   sección 1);
2. inventar/truncar evidencia de un record incluido de forma que rompa trazabilidad
   (`evidence_refs`/`path_ids`/`terminal` deben sobrevivir íntegros si el record se incluye);
3. cambiar `confidence`, `terminal_type`, ni ninguna clasificación de riqueza existente
   (`_richness_bucket`/`_flow_richness_bucket`/`_record_richness_bucket`);
4. volver al comportamiento anterior donde flows triviales monopolizan la muestra (preservar diversidad).

No ampliar alcance a V5, Plugin Runtime, ni a agnosticismo de provider/tecnología.

## 3. Direcciones de diseño a evaluar (no prescriptivas, decidir con evidencia; orden sugerido por relevancia
   según la causa raíz de dos capas de la sección 1)

Explorar, con mediciones deterministas reales (no asumir cuál funciona):

- **[Prioridad sugerida, ataca la capa 2] Empaquetado consciente de tamaño dentro de cada bucket / entre
  buckets**: en vez de (o además de) el orden `_bucketed_order` puro (round-robin por bucket, luego
  confidence, luego flow_id), evaluar una estrategia que dé una oportunidad real a los candidatos ricos que
  individualmente caben (9680-15795 caracteres en el caso demostrado) ANTES de que records triviales agoten
  el presupuesto -- por ejemplo, reservar una porción del presupuesto para el primer candidato rico que quepa
  por bucket antes de aceptar más triviales, o intentar un candidato rico "mediano" en cada ronda del
  round-robin antes de rellenar con triviales adicionales del mismo tamaño. Cualquier estrategia debe seguir
  siendo 100% determinista (mismo input, mismo output, mismo orden) y no requiere ordenar por tamaño de forma
  que rompa el criterio `confirmed antes que inferred antes que unresolved` ya vigente -- combinarlos, no
  reemplazar uno por otro.
- **[Ataca la capa 1] Partición de un record rico** en sub-unidades citables dentro del mismo presupuesto
  (p. ej. un subconjunto de paths/terminales por record en vez de el flow completo), si y solo si ya existe o
  se puede definir un contrato de partición parcial explícito para `ai_projection` sin inventar semántica
  nueva de "evidencia incompleta pero no marcada como tal" -- cualquier partición debe declararse
  explícitamente truncada, nunca presentarse como completa. Relevante solo para el 87.5% de candidatos ricos
  que son outliers de tamaño real (capa 1); no es necesaria para el 12.5% que ya caben individualmente
  (capa 2), donde ordenar mejor basta.
- **Presupuesto diferenciado entre perfiles usados para selección de candidatos vs. empaquetado real** (el
  gate final de `measure_request_payload` ya tiene ~11300 tokens de margen sin usar en el caso demostrado --
  investigar si ese margen puede trasladarse de forma determinista al presupuesto interno de `package()` sin
  violar el techo real del provider). Nota: esto ayudaría a ambas capas, pero no resuelve por sí solo la capa
  2 si el orden de evaluación sigue sin considerar tamaño -- un presupuesto mayor solo pospone el mismo
  problema de orden a una escala mayor.
- Cualquier otra dirección que preserve todos los invariantes de la sección 2 y se demuestre con
  fixtures/mediciones deterministas sobre el repositorio real, no solo sintéticas.

## 4. Principio obligatorio

Preservar: `Python selecciona y presupuesta; IA interpreta.` 100% determinista. Sin LLM, red, random ni
ranking IA para selección/budgeting.

## 5. No modificar

```text
CopilotProvider
SYSTEM_INSTRUCTION / USER_INSTRUCTION / FINDING_SCHEMA
measure_request_payload (el gate del request final, no el problema demostrado)
hydration.py (EvidenceHydrator.hydrate_flow, selección/deduplicación de paths)
consumer_projection.py
proposal_adapter.py
PROJECT_STATE.json
V5 / Plugin Runtime
distribution builder / requirements-copilot.txt
```

Si la corrección mínima necesaria requiere tocar `composer.PROFILES` (compartido con paquetes no-AI),
evaluar primero si `ai_projection` puede definir su propio presupuesto interno sin modificar
`composer.PROFILES` para otros consumidores -- documentar la decisión explícitamente si se toca.

## 6. Tests obligatorios (mínimo)

1. Repetir, como regresión, el escenario real demostrado en el diagnóstico (fixture sintética equivalente a
   "N candidatos ricos individualmente sobredimensionados + M candidatos ricos que caben individualmente pero
   quedan detrás de candidatos triviales en el orden actual + K candidatos triviales, todos dentro de
   budget"): verificar que la corrección SÍ incluye al menos un record rico (parcial o completo, según diseño
   elegido) en el paquete final, sin exceder el presupuesto del request final. La fixture debe cubrir
   explícitamente el caso de la capa 2 (un candidato rico que individualmente cabe pero que el orden actual
   descarta por agotamiento de presupuesto), no solo el caso de outliers de la capa 1.
2. Ningún record incluido pierde `evidence_refs`/`path_ids`/`terminal` de forma no declarada.
3. Diversidad preservada: no volver a 100% trivial cuando existan candidatos ricos.
4. `measure_request_payload` del request final sigue dentro del límite real del provider.
5. Sin mutación de `confidence`/`terminal_type`/clasificación de riqueza existente.
6. Determinismo: misma entrada, misma salida, mismo orden.
7. Sin llamada a provider/red en ningún test.
8. Regresión completa V4.2/V4.3 (R2, R5, R6, R7, R8, diversidad, budget, y el diagnóstico R3/rebaseline) en
   verde.
9. Reproducir, contra el output determinista real ya reconstruido en
   `C:\PruebasLegacyMapper\Resultados\v4_3_rebaseline` (o uno equivalente regenerado), que al menos uno de
   los 5 candidatos ricos bajo-budget identificados (`FLOW-0004993422`, `FLOW-0005929194`,
   `FLOW-0011096966`, `FLOW-0006182693`, `FLOW-0020041332`) sobrevive hasta el paquete final bajo la
   corrección, cuando antes ninguno lo hacía.

## 7. Suite

Ejecutar `python -m unittest discover -s tests`. Criterio: `0 failed`, `0 errors` en todo lo perteneciente a
V4.2/V4.3 y a esta corrección. Si reaparecen fallos de hash de baseline V4/V4.1 por CRLF/worktree (no
reproducidos en el equipo del rebaseline, ver `V4_3_WORKSTATION_REBASELINE_RESULT.md` sección 6-7), deben
reportarse explícitamente, no ocultarse ni "arreglarse" tocando artefactos de baseline cerrados fuera de
alcance.

## 8. Documento de resultado

Crear: `docs/V4_3/V4_3_R3A_R1_SELECTION_PACKING_QUALITY_CORRECTION_RESULT.md`. Debe incluir: evidencia de
las dos capas de causa raíz (heredada de esta ronda de rebaseline), diseño evaluado y elegido, por qué se
descartaron las alternativas, algoritmo nuevo exacto, invariantes preservados (evidencia atómica, diversidad,
determinismo, sin mutación de confidence), tests (incluyendo el test 9 de la sección 6 de este prompt),
resultados de suite completa, Runtime Independence, restricciones, y estado final.

## 9. Estado final permitido

Si pasa: `V4_3_READY_FOR_R3_RERUN` (habilita, en una tarea FUTURA separada, un nuevo piloto real con la
corrección aplicada -- no ejecutar ese rerun en esta tarea).

Si no: `V4_3_SELECTION_PACKING_CORRECTION_BLOCKED`.

NO usar `V4_3_CLOSED`. NO ejecutar R9.

## 10. Formato final obligatorio

```text
STATUS:
<estado>

ROOT CAUSE (heredada del diagnóstico R3 + rebaseline, dos capas):
<resumen>

DESIGN EVALUATED:
<resumen>

DESIGN CHOSEN:
<resumen>

FILES MODIFIED:
<lista>

ATOMIC EVIDENCE:
<resultado>

DIVERSITY PRESERVED:
<resultado>

TESTS:
<resultado>

RUNTIME INDEPENDENCE:
PASS/FAIL

RESTRICTIONS:
PASS/FAIL

RESULT DOCUMENT:
<ruta>

NEXT STEP:
<una sola acción>
```

Realizar únicamente esta corrección. NO ejecutar piloto real. NO ejecutar R9.
