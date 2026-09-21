# PROMPT — V4.3 FINAL AI PILOT PROPOSAL QUALITY CORRECTION

## 0. Contexto y autoridad

Repositorio:

`E:\IAProyectos\LegacyMapper`

Estado actual de V4.3:

- R0–R8 ejecutados y aprobados.
- Corrección pre-cierre del provider COPILOT completada.
- Corrección de distribución limpia completada.
- Piloto final real con IA ejecutado correctamente.
- `AI_INTERPRETATION`: SUCCESS.
- `PROPOSAL_GENERATION`: SUCCESS.
- Modelo real registrado: `gpt-5.6-luna`.
- Se generaron 8 propuestas.
- No se produjo conocimiento canónico.
- No hubo aprobación del Technical Lead.
- R9 todavía NO debe ejecutarse.

El problema ya NO está en:

- GitHub Copilot SDK;
- autenticación;
- runtime del SDK;
- `CopilotProvider`;
- structured output;
- distribución;
- `consumer_projection`;
- hidratación;
- ejecución del pipeline.

Esta tarea existe únicamente para revisar y corregir la CALIDAD DE SELECCIÓN de candidatos usados para generar propuestas de IA.

---

# 1. Evidencia del piloto final real

El piloto final terminó:

```text
LegacyMapper full run: SUCCESS

Deterministic analysis: SUCCESS
Documentation: SUCCESS

AI requested: True
AI invoked: True

AI_INTERPRETATION: SUCCESS
PROPOSAL_GENERATION: SUCCESS
FINAL_SUMMARY: SUCCESS

Proposals: PENDING_TECHNICAL_LEAD_REVIEW (8 pending)

Canonical knowledge produced: False
Technical Lead approval: False
```

Modelo real:

```text
gpt-5.6-luna
```

Por lo tanto, la infraestructura de IA está validada y NO debe tocarse en esta tarea.

---

# 2. Hallazgo de calidad

Las 8 propuestas producidas en el piloto final presentan prácticamente el mismo patrón:

```text
<entry point> has no recorded data operations and ends at an unresolved node.
```

Ejemplos reales:

```text
The dgrVariables_DataBinding DataBinding entry point in
webIndemnizacion\ucINDProcesosIndividualesFIN.ascx
has no recorded data operations and ends at an unresolved node.
```

```text
The Page_Load Load entry point in
webPRESaludOcupacional\ucPreConsultaControles.ascx
has no recorded data operations and ends at an unresolved node.
```

```text
The hylGuardar_Click Click entry point in ucUPOMo034.ascx
has no recorded data operations and ends at an unresolved node.
```

```text
The btnAgregar_Click Click entry point in WebSubsidio\ucSUBManPorcCajas.ascx
has no recorded data operations and ends at an unresolved node.
```

Las otras propuestas siguen el mismo patrón general.

Esto demuestra:

```text
CopilotProvider                         PASS
AI runtime                              PASS
Structured output                       PASS
Proposal generation runtime             PASS

Candidate selection quality             WEAK
Proposal diversity                      WEAK
Technical Lead usefulness               WEAK
```

El problema parece estar en qué flows/unidades se seleccionan para consumir los slots limitados de propuestas.

---

# 3. Evidencia de que la IA sí puede producir una interpretación rica

Antes del piloto final se probó manualmente el flow real:

```text
FLOW-0343552547
```

con aproximadamente:

```text
payload_estimated_tokens: 27969
```

El mismo provider real y `gpt-5.6-luna` produjeron structured output válido y una interpretación útil.

La interpretación identificó correctamente:

```text
Load -> Page_Load
CobLiquidacionDeudaPrev.ascx
EP-0494012737
FLOW-0343552547
```

y operaciones confirmadas como:

```text
PCOB_DEUDAS_ENCABEZADO.OBTENERGASTOSCOBEJ
PCOB_DEUDAS_ENCABEZADO.OBTENERLIQDEUDAPREV
PCOB_DEUDAS_ENCABEZADO.OBTENERLIQDEUDAPREV2
PCOB_FACTORES.OBTENERVALORES
```

También preservó correctamente incertidumbres:

- no afirmó orden exacto de todas las rutas;
- no inventó retorno de stored procedures;
- no convirtió `BeginTrans` en escritura confirmada;
- mantuvo el flow global como `unresolved`.

Conclusión:

> La IA puede producir interpretaciones útiles cuando recibe una unidad de evidencia suficientemente rica.

Por tanto, esta tarea NO debe intentar “mejorar el modelo”, cambiar prompts globales ni ampliar contexto indiscriminadamente.

---

# 4. Objetivo exacto

Revisar la lógica determinista actual que selecciona candidatos para `PROPOSAL_GENERATION` y corregirla mínimamente para que los slots disponibles no se consuman exclusivamente con flows triviales/unresolved sin operaciones de datos.

El resultado deseado es una muestra determinista y más informativa que pueda incluir, cuando existan candidatos:

- flows con data operations confirmadas;
- stored procedures confirmados;
- transacciones confirmadas;
- write evidence confirmada;
- múltiples componentes participantes;
- mezcla de evidencia confirmed + unresolved;
- flows unresolved útiles;
- flows sin data operations solo cuando aporten diversidad o evidencia relevante.

NO se busca eliminar flows unresolved.

NO se busca forzar artificialmente flows “interesantes”.

NO se debe alterar `confidence`.

NO se debe inventar evidencia.

---

# 5. Principio obligatorio

La selección debe seguir siendo:

```text
DETERMINISTA
```

La IA NO decide qué flows analizar.

Debe mantenerse el principio:

> Python descubre/selecciona; IA interpreta.

No introducir una llamada LLM para ranking, filtering, scoring o candidate selection.

---

# 6. Inspección obligatoria antes de modificar

Primero localizar y documentar:

1. dónde se seleccionan los candidatos para AI interpretation/proposal generation;
2. cuántos candidatos máximos se seleccionan;
3. cuál es el orden actual;
4. qué atributos/evidencia están disponibles durante la selección;
5. por qué los primeros 8 candidatos del piloto final terminaron siendo casi homogéneos;
6. si existe ranking, orden por ID, entrada, confidence, path count u otro criterio;
7. si la selección ocurre antes o después de hydration/projection.

NO modificar código antes de entender esa cadena.

---

# 7. Restricciones de arquitectura

NO modificar:

```text
CopilotProvider
requirements-copilot.txt
distribution builder
consumer_projection
hydration semantics
flow confidence
terminal resolution
R8 presentation logic
ProviderRegistry
V5
Plugin Runtime
technology detection
PROJECT_STATE.json
```

salvo documentación específica de esta corrección.

NO ejecutar R9.

NO declarar V4.3 cerrada.

NO cambiar el modelo configurado.

NO llamar Copilot real desde tests.

NO incorporar outputs reales del piloto como fixtures.

---

# 8. Diseño esperado de selección

No imponer una implementación concreta sin inspeccionar el código actual.

Pero la solución debe ser equivalente a una selección determinista con diversidad semántica.

Ejemplo conceptual permitido:

```text
bucket A: flows con confirmed data operations
bucket B: flows con stored procedures / transaction / write evidence
bucket C: flows mixtos confirmed + unresolved
bucket D: unresolved sin data operations
```

Luego seleccionar de forma determinista desde varios buckets para evitar que los primeros N slots sean todos iguales.

También es aceptable un sistema de score determinista si:

- usa solo evidencia ya calculada;
- el score es documentable;
- no cambia confidence;
- no oculta candidatos;
- produce orden estable;
- mantiene trazabilidad.

Ejemplo conceptual de criterios útiles:

```text
+ confirmed data operation
+ confirmed stored procedure
+ confirmed write
+ confirmed transaction
+ multiple participating components
+ mixed confirmed/unresolved evidence
+ multiple evidence references
```

No usar criterios basados en interpretación LLM.

No usar aleatoriedad.

---

# 9. Requisito de estabilidad

La misma entrada debe producir siempre la misma selección.

Si existen empates:

- usar un tie-break determinista estable;
- por ejemplo IDs ya existentes;
- no depender de orden de diccionarios no contractual;
- no usar random.

---

# 10. Diversidad mínima esperada

Si el conjunto completo de candidatos contiene evidencia suficiente, una selección de 8 NO debería estar compuesta exclusivamente por:

```text
no recorded data operations + unresolved node
```

La selección final debe intentar incluir diversidad de evidencia.

Esto NO significa exigir exactamente una cantidad fija por categoría si el dataset no contiene suficientes candidatos.

La lógica debe degradar de forma segura:

```text
si no hay candidatos ricos -> usar los disponibles
```

No fallar por ausencia de una categoría.

---

# 11. Calidad del statement

Revisar también por qué las propuestas finales quedaron en inglés.

NO cambiar todavía toda la arquitectura de internacionalización.

Si el idioma proviene de un prompt/config existente y V4.3 define español como default humano, corregir únicamente si forma parte directa del camino de proposal generation y puede hacerse sin ampliar alcance.

Si el idioma de propuestas NO está especificado por contrato actual, documentarlo como deuda y NO ampliar esta tarea.

No asumir.

---

# 12. Confidence / rationale

Revisar la combinación observada:

```text
Rationale:
AI-proposed interpretation (confidence: CONFIRMED).

Statement:
... ends at an unresolved node.
```

Determinar qué significa `confidence: CONFIRMED`.

Si representa confianza de la propuesta y no confidence del flow, documentarlo claramente.

Si está usando erróneamente una confidence distinta de la evidencia del flow, corregirlo.

NO cambiar confidence del flow.

NO degradar/elevar confidence artificialmente para mejorar propuestas.

---

# 13. Tests requeridos

Agregar tests deterministas usando fixtures sintéticas.

Como mínimo:

## T1 — Homogeneous trivial set

Dataset con solo flows unresolved sin data operations.

Esperado:

- selección válida;
- determinista;
- no falla;
- usa candidatos disponibles.

## T2 — Mixed candidate set

Dataset sintético con:

- unresolved sin data operations;
- confirmed data operation;
- stored procedure;
- transaction;
- write evidence;
- mixed confirmed/unresolved.

Esperado:

- selección limitada a N;
- incluye diversidad cuando existe;
- no consume todos los slots con la categoría trivial.

## T3 — Stable ordering

Misma entrada ejecutada múltiples veces.

Esperado:

```text
same selected IDs
same order
```

## T4 — Tie break

Candidatos con mismo score/prioridad.

Esperado:

- orden estable por criterio explícito.

## T5 — No confidence mutation

Verificar que selección/ranking NO modifica:

```text
flow confidence
path confidence
terminal confidence
```

## T6 — Evidence preservation

Los candidatos seleccionados conservan los IDs de evidencia originales.

## T7 — Candidate limit

Si el límite actual es N:

```text
len(selected) <= N
```

sin cambio accidental de contrato.

## T8 — No LLM dependency

El selector debe funcionar sin:

```text
copilot
network
LLM provider
```

## T9 — Existing regression

Preservar los tests actuales de proposal generation.

---

# 14. Validación específica recomendada

Agregar una fixture sintética equivalente conceptualmente a:

```text
FLOW-A:
  unresolved
  no data operations

FLOW-B:
  confirmed stored procedure

FLOW-C:
  confirmed transaction

FLOW-D:
  confirmed write

FLOW-E:
  mixed confirmed + unresolved

FLOW-F:
  unresolved
  no data operations
```

Con límite suficientemente pequeño, verificar que el selector no elija exclusivamente A/F si B/C/D/E están disponibles.

---

# 15. No tocar consumer_projection

Muy importante:

`consumer_projection` ya fue validado y NO debe modificarse.

La corrección debe ocurrir en la selección de candidatos para la IA/propuestas, no alterando la proyección exhaustiva de consumo.

---

# 16. No optimizar contexto todavía

El flow real `FLOW-0343552547` funcionó con ~28K tokens.

Por tanto:

- no reducir evidence package por esta tarea;
- no cambiar budget;
- no truncar evidence;
- no cambiar `measure_request_payload`;
- no cambiar schema de AI request.

Esta ronda es de candidate selection/quality, no de token optimization.

---

# 17. Suite completa

Baseline vigente tras la corrección de distribución:

```text
2098 tests
1966 passed
0 failed
0 errors
132 skipped
```

Como se agregarán tests, el total puede aumentar.

Criterio obligatorio:

```text
0 failures
0 errors
```

Ejecutar:

1. tests específicos del selector/proposals;
2. tests de V4.3 relevantes;
3. suite completa.

Documentar:

```text
total
passed
failed
errors
skipped
```

---

# 18. Piloto sintético / local

Antes de cualquier nuevo piloto real:

- demostrar con fixtures sintéticas que la selección ahora incluye diversidad;
- mostrar los IDs seleccionados y la razón determinista de su selección;
- no llamar Copilot real.

Si existe una función interna de ranking/selection, documentar su salida.

---

# 19. Documentación de resultado

Crear:

`docs/V4_3/V4_3_FINAL_AI_PILOT_PROPOSAL_QUALITY_CORRECTION_RESULT.md`

Debe incluir:

1. hallazgo del piloto real;
2. causa raíz;
3. algoritmo/criterio anterior;
4. algoritmo/criterio nuevo;
5. por qué sigue siendo determinista;
6. cómo se evita homogeneidad de candidatos;
7. degradación cuando no existen candidatos ricos;
8. tratamiento de confidence;
9. idioma de proposals y conclusión;
10. archivos modificados;
11. tests agregados;
12. resultados;
13. Runtime Independence;
14. restricciones verificadas;
15. deuda residual;
16. estado final.

---

# 20. Estado final permitido

Si la corrección pasa:

```text
V4_3_READY_FOR_FINAL_AI_PILOT_RERUN
```

Si no:

```text
V4_3_PROPOSAL_QUALITY_CORRECTION_BLOCKED
```

NO usar:

```text
V4_3_CLOSED
```

NO ejecutar R9.

---

# 21. Instrucciones para rerun

Crear o actualizar:

`docs/V4_3/V4_3_FINAL_AI_PILOT_RERUN_INSTRUCTIONS.md`

Debe indicar cómo repetir el piloto real en una salida NUEVA, por ejemplo:

```text
E:\IAProyectos\LegacyMapper_Pilot_Output\operaciones_v4_3_ai_final_r2
```

No ejecutar el rerun como parte de esta tarea.

El rerun deberá revisar:

- `RUN_SUMMARY.json`;
- `RUN_SUMMARY.md`;
- `AI_PROPOSALS.json`;
- `AI_PROPOSALS_PENDING_REVIEW.md`;
- cantidad de propuestas;
- diversidad de evidencia;
- idioma;
- confidence/rationale;
- provider/model;
- ausencia de secretos;
- canonical knowledge sigue false;
- Technical Lead approval sigue false.

---

# 22. Orden obligatorio de ejecución

1. inspeccionar selector actual;
2. documentar causa raíz;
3. revisar confidence/rationale;
4. revisar idioma sin ampliar alcance;
5. diseñar cambio mínimo determinista;
6. implementar;
7. agregar tests;
8. ejecutar tests específicos;
9. ejecutar suite completa;
10. validar selección sintética;
11. comprobar restricciones;
12. crear resultado;
13. crear instrucciones de rerun.

NO ejecutar piloto real.
NO ejecutar R9.

---

# 23. Formato obligatorio de respuesta final

```text
STATUS:
<estado>

ROOT CAUSE:
<resumen>

FILES MODIFIED:
<lista>

OLD SELECTION:
<resumen>

NEW DETERMINISTIC SELECTION:
<resumen>

DIVERSITY:
<resultado>

CONFIDENCE:
<resultado>

PROPOSAL LANGUAGE:
<resultado>

TESTS:
<resultado>

RUNTIME INDEPENDENCE:
PASS/FAIL

RESTRICTIONS:
PASS/FAIL

RESULT DOCUMENT:
<ruta>

RERUN INSTRUCTIONS:
<ruta>

NEXT STEP:
<una sola acción>
```

Realizar únicamente esta corrección de calidad.

NO ejecutar R9.
NO ejecutar el piloto real.
