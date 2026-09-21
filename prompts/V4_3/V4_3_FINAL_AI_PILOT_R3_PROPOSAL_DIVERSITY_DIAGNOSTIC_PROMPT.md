# PROMPT — V4.3 FINAL AI PILOT R3 PROPOSAL DIVERSITY ROOT-CAUSE DIAGNOSTIC

## Rutas vigentes

Repositorio LegacyMapper:
`C:\dev\LegacyMapper`

Repositorio legacy real:
`C:\inetpub\wwwroot\2010\IST\Operacional`

Estas rutas reemplazan las anteriores para todos los pasos futuros.

## Estado

- V4.3 R0–R8 aprobados.
- CopilotProvider y distribución limpia validados.
- Corrección de diversidad determinista aplicada.
- Corrección budget-aware aplicada.
- R3 real: SUCCESS.
- `AI_INTERPRETATION`: SUCCESS.
- `PROPOSAL_GENERATION`: SUCCESS.
- Provider: `copilot-local`.
- Modelo: `gpt-5.6-luna`.
- 6 propuestas.
- `canonical knowledge produced`: False.
- `Technical Lead approval`: False.
- R9 NO debe ejecutarse.

## Problema pendiente

Las 6 propuestas del R3 siguen concentradas en dead ends, unresolved paths y ausencia de data operations.

Aún no sabemos si:

### A — Selection / Packing
Los flows ricos nunca llegaron al request final del modelo.

### B — LLM Finding Bias
Los flows ricos sí llegaron al request final, pero el LLM generó findings solo sobre unresolved/dead ends.

Esta tarea debe distinguir A de B sin cambiar comportamiento funcional.

## Objetivo

Diagnosticar de forma determinista:

1. qué flows fueron seleccionados;
2. bucket/richness de cada flow;
3. cuáles se hidrataron;
4. cuáles sobrevivieron al budget packing;
5. cuáles fueron excluidos por budget;
6. qué records llegaron al `LLMRequest`;
7. qué evidencia rica contenían;
8. si había SPs, transacciones, writes o data operations confirmadas;
9. cuáles produjeron findings;
10. cuáles llegaron al request pero fueron ignorados por el modelo.

NO modificar selector, prompts, budget, provider ni confidence.

## Cadena a inspeccionar

```text
select_flow_ids
-> hydration
-> AiProjectionBuilder.package
-> _build_request
-> measure_request_payload
-> provider.send
-> findings
-> proposals
```

Documentar funciones, módulos, límites SMALL/TINY y puntos de descarte.

## Diagnóstico mínimo por flow

Obtener al menos:

```text
flow_id
entry_point_id
richness_bucket
flow_confidence
hydrated
selected_for_package
excluded_by_budget
final_request_included
serialized_record_chars
path_count
evidence_ref_count
has_data_operations
data_operation_count
has_stored_procedures
stored_procedure_count
has_transactions
transaction_count
has_confirmed_write
participating_component_count
mixed_confirmed_unresolved
```

## Implementación recomendada

Preferir una herramienta separada, por ejemplo:

`tools/v4_3_ai_selection_diagnostic.py`

Debe reutilizar funciones productivas reales y NO duplicar aproximaciones del selector.

Debe:

- ejecutar la misma selección;
- usar la misma hidratación;
- usar el mismo package/budget logic;
- NO invocar Copilot;
- emitir qué records habrían llegado al request.

Puede generar un artefacto diagnóstico como:

`ai_context/AI_SELECTION_DIAGNOSTIC.json`

si encaja con la arquitectura existente.

No convertirlo en contrato público estable salvo que ya exista una convención para ello.

## Caso histórico

Verificar si existe:

`FLOW-0343552547`

y registrar si:

- fue seleccionado;
- hidratado;
- incluido/excluido;
- llegó al request final.

Si el ID ya no existe en esta copia del repo, no hardcodear ni fallar. Buscar flows ricos equivalentes por propiedades.

## Clasificación final obligatoria

Usar UNA:

### DIAGNOSIS_A_SELECTION_PACKING
Los records ricos no llegan al request final.

### DIAGNOSIS_B_LLM_FINDING_BIAS
Records ricos sí llegan completos al request, pero los findings se concentran en trivial/unresolved.

### DIAGNOSIS_MIXED
Ambas cosas ocurren.

### DIAGNOSIS_INCONCLUSIVE
No puede demostrarse con datos.

No corregir A/B en esta tarea.

## Mapping proposals → flows

Mapear las 6 propuestas R3 mediante `evidence_refs`:

```text
proposal_id
flow_id
```

y comparar con todos los records incluidos en el request.

Determinar:

- flows incluidos que sí produjeron proposal;
- flows incluidos que NO produjeron proposal;
- riqueza de cada uno.

## Sin nuevas llamadas reales

NO ejecutar Copilot real.

Usar:

- outputs R3 existentes si son suficientes;
- reproducción determinista local;
- fixtures sintéticas.

## Tests mínimos

1. diagnóstico replica `select_flow_ids`;
2. diagnóstico replica `AiProjectionBuilder.package`;
3. oversized candidate queda `excluded_by_budget=true`;
4. rich candidate incluido refleja correctamente SP/write/transaction;
5. proposal→flow mapping correcto;
6. salida determinista estable;
7. sin provider call;
8. sin secret leakage;
9. regresiones R5/R6/R7/R8 + diversity + budget pasan.

Baseline:

```text
2136 tests
2004 passed
0 failed
0 errors
132 skipped
```

Criterio final:

```text
0 failed
0 errors
```

## Resultado

Crear:

`docs/V4_3/V4_3_FINAL_AI_PILOT_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_RESULT.md`

Debe incluir:

1. evidencia R3;
2. cadena selection→request;
3. diagnóstico por flow;
4. resultado de `FLOW-0343552547`;
5. records ricos seleccionados;
6. records ricos excluidos;
7. records finales enviados;
8. mapping proposals→flows;
9. clasificación A/B/MIXED/INCONCLUSIVE;
10. archivos modificados;
11. tests/resultados;
12. Runtime Independence;
13. restricciones;
14. próxima acción.

## Crear solo el siguiente prompt correspondiente

Si A:
`prompts/V4_3/V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION.md`

Si B:
`prompts/V4_3/V4_3_R3B_LLM_FINDING_DIVERSITY_CORRECTION.md`

Si MIXED:
`prompts/V4_3/V4_3_R3M_MIXED_PROPOSAL_QUALITY_CORRECTION.md`

Si INCONCLUSIVE:
no crear corrección.

NO ejecutar ese siguiente prompt.

## Restricciones

NO modificar comportamiento de:

```text
select_flow_ids
_bucketed_order
AiProjectionBuilder.package
budget limits
SMALL/TINY
CopilotProvider
SYSTEM_INSTRUCTION
USER_INSTRUCTION
FINDING_SCHEMA
proposal_adapter
consumer_projection
hydration
confidence
terminal resolution
PROJECT_STATE.json
V5
Plugin Runtime
```

Solo diagnóstico/tooling/tests/docs.

## Estado final permitido

Concluyente:
`V4_3_R3_PROPOSAL_DIVERSITY_DIAGNOSED`

No concluyente:
`V4_3_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_INCONCLUSIVE`

NO ejecutar R9.
NO declarar V4.3 cerrada.

## Formato final obligatorio

```text
STATUS:
<estado>

DIAGNOSIS:
DIAGNOSIS_A_SELECTION_PACKING |
DIAGNOSIS_B_LLM_FINDING_BIAS |
DIAGNOSIS_MIXED |
DIAGNOSIS_INCONCLUSIVE

ROOT CAUSE EVIDENCE:
<resumen>

FILES MODIFIED:
<lista>

R3 FLOWS SELECTED:
<resumen>

RICH FLOWS IN FINAL REQUEST:
<resumen>

RICH FLOWS EXCLUDED:
<resumen>

PROPOSAL -> FLOW MAPPING:
<resumen>

HISTORICAL FLOW-0343552547:
<resultado>

TESTS:
<resultado>

RUNTIME INDEPENDENCE:
PASS/FAIL

RESTRICTIONS:
PASS/FAIL

RESULT DOCUMENT:
<ruta>

NEXT PROMPT:
<ruta o NONE>

NEXT STEP:
<una sola acción>
```
