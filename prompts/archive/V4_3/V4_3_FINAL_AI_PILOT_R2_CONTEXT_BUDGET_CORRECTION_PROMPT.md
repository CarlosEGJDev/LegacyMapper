# PROMPT — V4.3 FINAL AI PILOT R2 CONTEXT BUDGET REGRESSION CORRECTION

## 0. Contexto y estado

Repositorio: `E:\IAProyectos\LegacyMapper`

Estado vigente:
- V4.3 R0–R8 aprobados.
- CopilotProvider real validado.
- Distribución limpia validada.
- Primer piloto real IA: SUCCESS, pero con 8 propuestas demasiado homogéneas/triviales.
- Se aplicó una corrección determinista de diversidad en `legacy_documenter/context/ai_projection.py`.
- Suite posterior: 2121 tests, 1989 passed, 0 failed, 0 errors, 132 skipped.
- Se ejecutó el rerun real R2.
- R9 NO debe ejecutarse.
- V4.3 NO debe declararse cerrada.

## 1. Evidencia del rerun real R2

Resultado:

```text
status: PARTIAL
ai_requested: true
ai_invoked: false
proposal_count: 0
proposal_review_status: NO_PROPOSALS_GENERATED
canonical_knowledge_produced: false
technical_lead_approval: false
```

Stages:

```text
SCAN: SUCCESS
EXTRACTION: SUCCESS
CALL_RESOLUTION: SUCCESS
WEB_ENTRY_RESOLUTION: SUCCESS
DATABASE_RESOLUTION: SUCCESS
FLOW_RESOLUTION: SUCCESS
DEPENDENCY_RESOLUTION: SUCCESS
EXPORT: SUCCESS
CONTEXT: SUCCESS
DOCUMENTATION: SUCCESS
AI_INTERPRETATION: FAILED
PROPOSAL_GENERATION: SKIPPED_DUE_TO_UPSTREAM_FAILURE
FINAL_SUMMARY: SUCCESS
```

Error exacto:

```text
CONTEXT_TOO_LARGE:
budget_insufficient:profile=SMALL;
budget_insufficient:profile=TINY
```

El provider NO fue invocado:

```text
ai_invoked: false
provider_id: null
model_id: null
```

Por tanto, el fallo ocurre ANTES de CopilotProvider. No tocar provider, autenticación, SDK ni modelo.

## 2. Relación con la corrección anterior

La corrección anterior introdujo diversidad determinista mediante buckets de riqueza y round-robin estable, tanto en `select_flow_ids(...)` como en `AiProjectionBuilder.package(...)`.

El rerun demuestra una regresión de integración entre:

```text
diversidad determinista
+
budgeting determinista
```

La selección de flows más ricos puede producir un paquete que no cabe ni en SMALL ni TINY.

## 3. Objetivo exacto

Corregir únicamente la interacción entre selección por diversidad y budget enforcement para que:

1. la selección siga siendo determinista y diversa;
2. nunca se invoque el provider con un request fuera de presupuesto;
3. si existen candidatos que individualmente sí caben, el sistema construya un paquete válido dentro de SMALL o TINY;
4. no se vuelva al comportamiento anterior donde flows triviales monopolizan la muestra;
5. no se trunque evidencia de un flow de forma que rompa trazabilidad;
6. se mantenga `CONTEXT_TOO_LARGE` fail-closed cuando realmente no exista ninguna combinación válida.

No ampliar alcance.

## 4. Inspección obligatoria antes de modificar

Localizar y documentar exactamente:

1. dónde se calcula el budget de SMALL;
2. dónde se calcula TINY;
3. dónde se llama `measure_request_payload`;
4. orden exacto: `select_flow_ids -> hydration -> package -> request serialization -> budget validation`;
5. qué candidato(s) o combinación hacen fallar SMALL;
6. por qué TINY también falla;
7. si el recorte actual usa records, chars, request serializado real o una estimación previa;
8. si un solo flow rico supera el presupuesto;
9. si existen flows ricos posteriores que sí caben;
10. si el round-robin actual deja que un candidato muy grande bloquee el greedy packing.

No asumir la causa: demostrarla con fixtures/mediciones deterministas.

## 5. Principio obligatorio

Preservar:

> Python selecciona y presupuesta; IA interpreta.

100% determinista. Sin LLM, red, random ni ranking IA para budgeting/selección.

## 6. Comportamiento esperado

Diseño conceptual aceptable:

```text
1. ordenar candidatos con la política determinista de diversidad;
2. medir el costo real/serializable de incorporar cada candidato;
3. incorporar candidatos mientras el request final permanezca dentro del presupuesto;
4. si un candidato no cabe, no abortar automáticamente: probar determinísticamente candidatos posteriores que sí puedan caber;
5. no truncar evidencia contractual de un candidato incluido;
6. si ningún candidato válido cabe, CONTEXT_TOO_LARGE.
```

No usar `take first N` ni `stop on first oversized` si existen candidatos posteriores que caben.

## 7. Atomicidad de evidencia

No romper un flow para hacerlo caber salvo que ya exista un contrato explícito de partición parcial para AI context.

No inventar truncado nuevo de:
- paths;
- terminals;
- data operations;
- evidence_refs.

Preferir otro flow completo que sí entre.

## 8. Budget real

Preservar R5: el budget se aplica al request final serializado, no solo a aproximaciones intermedias.

No cambiar límites, `chars_per_token`, `measure_request_payload`, output reservation, schema reservation ni context window para “hacer pasar” el piloto.

## 9. SMALL / TINY

Preservar:

```text
SMALL
-> si no cabe, TINY
-> si tampoco cabe, CONTEXT_TOO_LARGE
```

La corrección debe permitir que cada perfil construya su propia selección compatible con su budget. No eliminar fail-closed.

## 10. Diversidad bajo presupuesto

Conservar representación de buckets ricos cuando sea posible, pero el budget manda.

Si un candidato bucket 0 es individualmente demasiado grande, no debe bloquear todos los demás. Puede saltarse determinísticamente y continuar con candidatos posteriores que sí caben.

No alterar `confidence`.

## 11. Caso real conocido

`FLOW-0343552547` funcionó manualmente con ~27969 tokens estimados usando el provider real.

No hardcodear ese flow. Solo sirve como evidencia de que un flow rico puede caber individualmente.

## 12. Tests obligatorios

### T1 — Rich oversized first candidate
A: bucket 0 demasiado grande; B: bucket 0 cabe; C: bucket 1 cabe; D: bucket 3 cabe.
Esperado: A se excluye por budget; B/C y, si cabe, D se seleccionan.

### T2 — No candidate fits
Todos exceden individualmente el budget. Esperado: `CONTEXT_TOO_LARGE`, sin provider call.

### T3 — SMALL fails, TINY succeeds
Verificar fallback real existente con fixture sintética.

### T4 — SMALL succeeds
Dataset mixto rico dentro de budget. No llega a TINY.

### T5 — Final serialized payload
Medir con la misma serialización/medición contractual del request final.

### T6 — Stable output
Misma entrada => mismos IDs, orden, profile y medición.

### T7 — Diversity survives budget pruning
No seleccionar solo bucket 3 si existen candidatos ricos que sí caben.

### T8 — Atomic evidence
Candidato incluido conserva campos/evidence refs contractuales íntegros.

### T9 — No confidence mutation
Confidence original intacta.

### T10 — No LLM dependency
Sin red, Copilot ni provider.

### T11 — Regressions
Preservar R5/R6/R7/R8 y la corrección de proposal quality.

## 13. Diagnóstico interno recomendado

Si existe una superficie adecuada, exponer solo para tests/log interno datos deterministas como:

```text
profile
candidate_flow_id
candidate_bucket
candidate_size
selected / skipped_budget
final_payload_bytes
final_payload_estimated_tokens
```

No crear un artefacto público nuevo sin convención.

## 14. No modificar

NO modificar:

```text
CopilotProvider
requirements-copilot.txt
distribution builder
consumer_projection.py
hydration.py
ProviderRegistry
V5
Plugin Runtime
technology detection
PROJECT_STATE.json
human documentation renderers
R8 presentation logic
```

Si aparece un bug fuera de alcance estrictamente necesario, detenerse y documentar BLOCKED en vez de ampliar alcance silenciosamente.

## 15. Deudas fuera de esta ronda

NO abordar:
- idioma inglés de AI proposals;
- renombrado UX de `confidence`.

## 16. Suite

Baseline:

```text
2121 tests
1989 passed
0 failed
0 errors
132 skipped
```

Ejecutar tests específicos, R5, R6, R7/R8 relevantes, proposal quality correction y suite completa.

Criterio: `0 failed`, `0 errors`.

## 17. Validación sintética obligatoria

Documentar un ejemplo equivalente a:

ANTES:

```text
rich-large -> budget fail -> CONTEXT_TOO_LARGE
```

DESPUÉS:

```text
rich-large -> skipped_budget
rich-medium -> selected
mixed-small -> selected
trivial-small -> selected if remaining budget
final request -> within budget
```

Sin provider real.

## 18. Documento de resultado

Crear:

`docs/V4_3/V4_3_FINAL_AI_PILOT_R2_CONTEXT_BUDGET_CORRECTION_RESULT.md`

Debe incluir:
1. evidencia R2;
2. causa raíz demostrada;
3. cadena exacta selection/budget;
4. algoritmo anterior;
5. algoritmo nuevo;
6. atomicidad;
7. SMALL/TINY;
8. diversidad bajo budget;
9. tests;
10. resultados;
11. Runtime Independence;
12. restricciones;
13. deuda residual;
14. estado final.

## 19. Instrucciones R3

Crear:

`docs/V4_3/V4_3_FINAL_AI_PILOT_R3_INSTRUCTIONS.md`

Usar salida NUEVA, por ejemplo:

`E:\IAProyectos\LegacyMapper_Pilot_Output\operaciones_v4_3_ai_final_r3`

Usar repositorio real:

`E:\IAProyectos\revision\revision-main`

y subcomando correcto:

```text
python main.py full ...
```

Exigir reconstruir distribución limpia después de esta corrección.

NO ejecutar R3 dentro de esta tarea.

## 20. Estado final permitido

Si pasa:

`V4_3_READY_FOR_FINAL_AI_PILOT_R3`

Si no:

`V4_3_CONTEXT_BUDGET_CORRECTION_BLOCKED`

NO usar `V4_3_CLOSED`. NO ejecutar R9.

## 21. Orden obligatorio

1. inspeccionar cadena de budget;
2. reproducir fallo sintético;
3. demostrar causa raíz;
4. diseñar solución budget-aware mínima;
5. implementar;
6. agregar tests;
7. ejecutar suites específicas;
8. ejecutar suite completa;
9. validar ejemplo sintético;
10. comprobar restricciones;
11. crear resultado;
12. crear instrucciones R3.

## 22. Formato final obligatorio

```text
STATUS:
<estado>

ROOT CAUSE:
<resumen>

FILES MODIFIED:
<lista>

OLD BUDGET BEHAVIOR:
<resumen>

NEW BUDGET-AWARE SELECTION:
<resumen>

SMALL/TINY:
<resultado>

DIVERSITY UNDER BUDGET:
<resultado>

ATOMIC EVIDENCE:
<resultado>

TESTS:
<resultado>

RUNTIME INDEPENDENCE:
PASS/FAIL

RESTRICTIONS:
PASS/FAIL

RESULT DOCUMENT:
<ruta>

R3 INSTRUCTIONS:
<ruta>

NEXT STEP:
<una sola acción>
```

Realizar únicamente esta corrección.

NO ejecutar piloto real.
NO ejecutar R9.
