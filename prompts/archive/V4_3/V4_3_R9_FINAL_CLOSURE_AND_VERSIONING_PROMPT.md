# PROMPT — V4.3 R9 — FINAL CLOSURE, VERSIONING & REAL PILOT REVIEW

## 0. Contexto vigente

Repositorio LegacyMapper:

`C:\dev\LegacyMapper`

Repositorio legacy real:

`C:\inetpub\wwwroot\2010\IST\Operacional`

Estado previo aprobado:

- V4.3 R0-R8 aprobados.
- Workstation rebaseline reconstruido y validado.
- R3A-R1 Selection/Packing Quality Correction aplicada y verificada.
- Suite completa después de R3A-R1: 2169 tests, 0 failed, 0 errors, 132 skipped.
- Piloto real posterior a R3A-R1 ejecutado con Copilot real.
- Provider real: `copilot-local`
- Modelo real: `gpt-5.6-luna`
- Resultado del piloto: `SUCCESS`
- `AI_INTERPRETATION`: `SUCCESS`
- `PROPOSAL_GENERATION`: `SUCCESS`
- 4 propuestas generadas.
- `canonical_knowledge_produced=false`
- `technical_lead_approval=false`
- No hay aprobación automática ni conocimiento canónico automático.

Resultado clave del piloto:

La corrección R3A-R1 consiguió que `FLOW-0004993422` sobreviviera al packing y llegara al request real.

El modelo produjo findings sobre evidencia rica de ese flow, incluyendo:

- entry point `hypAnular_Click`;
- operación transaccional confirmada;
- `PreAdhClasuc.txeliminar`;
- `BeginTrans`;
- paths unresolved relacionados con `PreAdhClasuc.eliminar(...)`, `dbc.BeginTrans()`, `dbc.Close()`,
  `dbc.Rollback()`, `dbc.Commit()` y `DesplegarError(ex)`.

Por tanto, quedó validada de punta a punta la cadena:

```text
legacy real
-> análisis determinista
-> selección/hydration
-> packing con evidencia rica
-> request dentro de budget
-> Copilot real
-> gpt-5.6-luna
-> findings grounded
-> propuestas pendientes de revisión
```

Esta ronda es la revisión final de V4.3 y, solo si toda la evidencia es suficiente, su cierre/versionado.

## 1. Objetivo

Realizar la revisión final de V4.3 sobre:

1. integridad del estado del repositorio;
2. resultados de tests;
3. correcciones R3A-R1;
4. piloto real exitoso;
5. calidad y trazabilidad de las 4 propuestas;
6. Runtime Independence;
7. restricciones de V4.3;
8. documentación final;
9. versionado/cierre de V4.3.

NO introducir nuevas funcionalidades.

Si aparece un defecto funcional real, detener el cierre y documentarlo.

## 2. Evidencia obligatoria a revisar

Revisar como mínimo:

```text
docs/V4_3/V4_3_EXECUTION_PLAN.md
docs/V4_3/V4_3_R7_INTERNAL_ACCEPTANCE_RESULT.md
docs/V4_3/V4_3_R8_EXTERNAL_PILOT_CORRECTIONS_RESULT.md
docs/V4_3/V4_3_FINAL_AI_PILOT_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_RESULT.md
docs/V4_3/V4_3_WORKSTATION_REBASELINE_RESULT.md
docs/V4_3/V4_3_R3A_R1_SELECTION_PACKING_QUALITY_CORRECTION_RESULT.md
```

y los artefactos reales del último piloto exitoso bajo:

`C:\PruebasLegacyMapper\Resultados\v4_3_ai_rerun_r3a_r1_retry1`

en particular:

```text
RUN_SUMMARY.json
RUN_SUMMARY.md
proposals\AI_PROPOSALS.json
proposals\AI_PROPOSALS_PENDING_REVIEW.md
OUTPUT_MANIFEST.json
```

No copiar outputs reales completos al repositorio.

## 3. Validación del piloto real

Confirmar explícitamente:

```text
status = SUCCESS
ai_requested = true
ai_invoked = true
AI_INTERPRETATION = SUCCESS
PROPOSAL_GENERATION = SUCCESS
proposal_count = 4
proposal_review_status = PENDING_TECHNICAL_LEAD_REVIEW
canonical_knowledge_produced = false
technical_lead_approval = false
provider_id = copilot-local
model_id = gpt-5.6-luna
```

Verificar que no exista:

```text
CONTEXT_TOO_LARGE
PROVIDER_ERROR
BUDGET_INSUFFICIENT
```

en el piloto exitoso.

## 4. Revisión de calidad de propuestas

Revisar las 4 propuestas una por una.

Para cada una registrar:

```text
proposal_id
flow_id
entry_point_id
confidence
statement
evidence_refs
clasificación:
  - RICH_GROUNDED
  - TRIVIAL_GROUNDED
  - UNRESOLVED_GROUNDED
  - INVALID_OR_UNSUPPORTED
```

No aprobar automáticamente ninguna propuesta.

La revisión debe verificar:

- que `evidence_refs` existan;
- que las statements estén soportadas por evidencia determinista;
- que no inventen semántica;
- que no conviertan uncertainty en certeza;
- que transacciones/data access estén correctamente representadas;
- que referencias unresolved sigan explícitamente unresolved.

Confirmar específicamente que las propuestas sobre `FLOW-0004993422` están grounded y prueban la utilidad de la corrección R3A-R1.

## 5. Criterio de aceptación de diversidad

Para cerrar V4.3 NO se exige que todas las propuestas sean ricas.

Sí se exige que el piloto real demuestre:

1. al menos una propuesta grounded basada en evidencia rica;
2. que la evidencia rica llegó al modelo;
3. que el modelo utilizó esa evidencia;
4. que siguen coexistiendo findings trivial/unresolved cuando corresponden;
5. que no existe monopolio de findings triviales por defecto.

Si estos puntos se cumplen, la validación de diversidad se considera PASS.

## 6. Tests finales

Ejecutar:

```bat
cd /d C:\dev\LegacyMapper
python -m unittest discover -s tests
```

Esperado mínimo:

```text
0 failed
0 errors
```

Registrar:

```text
total
passed
failed
errors
skipped
```

Los skips deben seguir explicados.

No modificar tests/baselines cerrados para forzar un verde.

## 7. Git / working tree

Registrar:

```bat
git status
git branch --show-current
git rev-parse HEAD
```

Clasificar cambios actuales en:

```text
V4.3 funcionales
V4.3 tests
V4.3 docs/prompts
preexistentes/no relacionados
```

No mezclar cambios ajenos en el cierre.

## 8. Runtime Independence

Revalidar:

- runtime de producto no depende de:
  - docs/
  - prompts/
  - tests/
  - PROJECT_STATE.json
  - governance/result files
- provider Copilot sigue siendo opcional;
- ejecución determinista sigue funcionando sin `github-copilot-sdk`;
- `requirements-copilot.txt` sigue siendo dependencia opcional;
- no existen secretos persistidos en repo/output/manifiestos.

Resultado obligatorio:

```text
PASS
```

o bloquear cierre.

## 9. Estado del contrato V4.3

Confirmar que V4.3 entrega:

- hydration determinista;
- selección determinista;
- human documentation;
- scaling/partitioning;
- AI budgeting sobre payload final;
- consumer projection;
- AI projection;
- provider real validado;
- propuestas AI siempre pendientes de revisión humana;
- no canonicalización automática;
- no aprobación automática;
- outputs plugin-ready/consumer-ready sin implementar Plugin Runtime;
- separación Python descubre / IA interpreta.

Confirmar también que siguen FUERA de V4.3:

- generic technology adapters;
- multi-tech normalized detection/capabilities;
- generic provider abstraction redesign;
- Plugin Runtime;
- V5 redesign;
- Approval Surface completa si no fue implementada;
- cambios de contratos no requeridos.

## 10. Documentos finales de cierre

Si todo pasa, crear:

`docs/V4_3/V4_3_R9_FINAL_CLOSURE_RESULT.md`

Debe incluir:

1. scope final de V4.3;
2. resumen R0-R8;
3. historial de problemas reales encontrados;
4. corrección proposal diversity;
5. corrección context budget;
6. diagnóstico selection/packing;
7. workstation rebaseline;
8. R3A-R1;
9. piloto real final;
10. revisión de las 4 propuestas;
11. tests finales;
12. Runtime Independence;
13. restricciones preservadas;
14. deudas que pasan a V5/post-V5;
15. estado final.

También actualizar, solo si corresponde al modelo de versionado vigente del repo:

`PROJECT_STATE.json`

para reflejar cierre V4.3.

No introducir campos arbitrarios: seguir exactamente el schema/estilo ya usado por versiones anteriores.

## 11. Deudas que NO bloquean V4.3

Documentar, sin corregir en esta ronda, las deudas ya conocidas que correspondan:

- F05 duration pendiente por compatibilidad byte-identical previa;
- F06 ruido `InitializeComponent`;
- F07 gaps WebForms markup outgoing_calls;
- flows ricos gigantes que siguen sin caber completos bajo SMALL;
- eventual contrato de partición parcial de evidence records;
- Approval Surface;
- Plugin Runtime;
- generic provider abstraction;
- generic technology/db/layout abstraction;
- normalización multi-tech;
- cualquier deuda de UX como nombres `confidence` si sigue vigente.

No convertir deuda post-V4.3 en cambio funcional durante R9.

## 12. Versionado / cierre

Solo si todas las gates pasan:

Estado final:

`V4_3_CLOSED`

y documentar que:

- V4.3 está cerrada funcional y documentalmente;
- el piloto real validó la cadena completa;
- las propuestas siguen requiriendo revisión humana;
- V5 queda habilitada como siguiente línea de trabajo.

Si alguna gate falla:

`V4_3_R9_BLOCKED`

y documentar exactamente qué falta.

## 13. Commit

Si el repositorio usa cierre por commit/versionado y el working tree está suficientemente limpio:

- preparar commit de cierre V4.3;
- NO hacer push automáticamente salvo que las instrucciones vigentes del repo lo autoricen explícitamente.

Commit sugerido:

`Close V4.3 evidence projection and real AI validation`

Si existen cambios ajenos no separables con seguridad, NO hacer commit y documentar bloqueo operativo sin alterar archivos ajenos.

## 14. No modificar

NO modificar comportamiento funcional salvo para corregir un defecto imprescindible encontrado durante la validación final.

Especialmente NO tocar:

```text
select_flow_ids
_bucketed_order
AiProjectionBuilder.package
EvidenceHydrator
composer.PROFILES
measure_request_payload
CopilotProvider
SYSTEM_INSTRUCTION
USER_INSTRUCTION
FINDING_SCHEMA
proposal_adapter
consumer_projection
```

si todas las gates ya pasan.

NO ejecutar otra optimización.
NO iniciar V5.
NO implementar Plugin Runtime.

## 15. Resultado final obligatorio

Formato:

```text
STATUS:
<V4_3_CLOSED | V4_3_R9_BLOCKED>

REAL PILOT:
<resultado>

PROPOSAL QUALITY:
<resultado>

RICH EVIDENCE VALIDATION:
PASS/FAIL

FINAL TEST SUITE:
<resultado>

RUNTIME INDEPENDENCE:
PASS/FAIL

V4.3 SCOPE:
PASS/FAIL

DEFERRED DEBT:
<resumen>

FILES CREATED:
<lista>

FILES MODIFIED:
<lista>

PROJECT_STATE:
<resultado>

GIT:
<resultado>

RESULT DOCUMENT:
<ruta>

NEXT STEP:
<una sola acción>
```

Realizar únicamente la revisión/cierre de V4.3.
No iniciar V5 en esta tarea.
