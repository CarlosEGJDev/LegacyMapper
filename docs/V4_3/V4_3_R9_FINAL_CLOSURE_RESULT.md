# V4.3 — R9 — Cierre Final, Versionado y Revisión del Piloto Real — Resultado

## Estado de esta ronda

`V4_3_CLOSED`. Todas las gates obligatorias del prompt de esta ronda
(`prompts/V4_3/V4_3_R9_FINAL_CLOSURE_AND_VERSIONING_PROMPT.md`) pasan con evidencia real, verificada en esta
tarea (no solo citada de rondas previas): piloto real exitoso post-R3A-R1, cuatro propuestas revisadas una por
una con `evidence_refs` verificados contra el índice real del propio piloto, suite completa en verde, Runtime
Independence PASS, sin secretos persistidos, y ningún defecto funcional real encontrado durante esta
verificación final. V4.3 se declara cerrada funcional y documentalmente.

## 1. Scope final de V4.3

V4.3 entrega, verificado en esta ronda:

- hydration determinista (`EvidenceHydrator.hydrate_flow`, V4.3-R2, no tocada desde entonces salvo el campo
  aditivo `entry_point.project` de R8);
- selección determinista (`select_flow_ids`, `_bucketed_order`, `_richness_bucket`, no tocados desde R3A-R1
  salvo el reordenamiento de aceptación dentro de `AiProjectionBuilder.package` documentado en
  `V4_3_R3A_R1_SELECTION_PACKING_QUALITY_CORRECTION_RESULT.md`);
- documentación humana en español por defecto, summary-first, con particionado a escala (R3/R4/R7/R8);
- scaling/partitioning (R4, corregido en R8 con agrupación por `.vbproj` real + segunda capa de subpartición);
- AI budgeting sobre el payload final (`measure_request_payload`, R5, no tocado);
- consumer projection (R6, no tocado en esta ronda ni en R3A-R1);
- AI projection (`AiProjectionBuilder`, R5/R6, con la corrección de empaquetado de R3A-R1);
- provider real validado end-to-end contra Copilot real (`copilot-local` / `gpt-5.6-luna`) en el piloto de
  esta ronda;
- propuestas de IA siempre pendientes de revisión humana (`proposal_review_status=PENDING_TECHNICAL_LEAD_REVIEW`,
  `technical_lead_approval=false` en el piloto real, verificado sección 3);
- ninguna canonicalización automática (`canonical_knowledge_produced=false`, verificado);
- ninguna aprobación automática (ninguna propuesta se aprueba en esta ronda, sección 4);
- outputs plugin-ready/consumer-ready (`consumer_projection/`) sin implementar Plugin Runtime;
- separación estricta "Python descubre/selecciona/presupuesta; IA interpreta" (`ai_projection.py` no importa
  `legacy_documenter.llm` ni ningún provider, verificado sección 8).

Queda explícitamente **fuera** de V4.3, confirmado sin cambios en esta ronda: adapters de tecnología genéricos,
detección/capacidades normalizadas multi-tecnología, rediseño de abstracción de provider genérica, Plugin
Runtime, rediseño V5, Approval Surface completa (`approval_surface_implementation: NOT_IMPLEMENTED` en
`PROJECT_STATE.json`, sin cambios), y cualquier cambio de contrato no requerido por esta ronda. Esta ronda no
introdujo ninguna funcionalidad nueva — únicamente revisión, verificación y documentación de cierre.

## 2. Resumen R0-R8

- **R0**: alcance y baseline empírico; cuatro casos reales de aceptación (A-D) fijados contra
  `C:\inetpub\wwwroot\2010\IST\Operacional`.
- **R1-R6**: hydration, documentación humana en español, scaling/partitioning, AI context budgeting, AI/consumer
  projection — cada ronda con su propio código de producción + tests, sin tocar rondas previas salvo campos
  aditivos.
- **R7**: aceptación interna real (no solo documental); dos hallazgos reales encontrados y corregidos dentro de
  la misma ronda (`consumer_projection` ausente de `output_locations`; documentación humana nunca conectada a
  `full`/`analyze`), más tres bloqueos de aceptación adicionales corregidos tras revisión del Líder Técnico
  (`output-manifest` como subcomando runtime, documentación técnica de producto en español, `RUN_SUMMARY.md` en
  español). Empaquetado de distribución limpia (`tools/v4_3_r7_build_pilot_distribution.py`) y manifest de
  outputs (`legacy_documenter/cli/output_manifest.py`) verificados de extremo a extremo vía subproceso real.
  `2057 tests, 0 fallos, 0 errores, 132 skips`.
- **R8**: tres hallazgos reales del piloto externo (P-01 escalado de partición humana, P-02 verbosidad de
  documento de flujo, P-03 ruido técnico vs. incertidumbre) corregidos con código de producción real,
  estrictamente presentation-only/proyección donde correspondía — ningún caso clasificado como `BUG_V4_3`.
  `2087 tests, 0 fallos, 0 errores, 132 skips`.

## 3. Historial de problemas reales encontrados

Ver `docs/V4_3/V4_3_FINAL_AI_PILOT_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_RESULT.md` y
`docs/V4_3/V4_3_R3A_R1_SELECTION_PACKING_QUALITY_CORRECTION_RESULT.md`: el hallazgo central post-R8 fue que,
pese a la diversidad round-robin ya corregida en `select_flow_ids`, el 100% de los candidatos ricos (0/40)
llegaban al `LLMRequest` final bajo el perfil `SMALL` en el repositorio real a escala completa
(`flow_count=12642`), diagnosticado en dos capas: (1) 35/40 candidatos ricos exceden por sí solos el
presupuesto completo de `SMALL` (outliers reales de tamaño, no corregibles por reordenamiento); (2) 5/40 caben
individualmente pero `AiProjectionBuilder.package`, con un único orden de evaluación fijo y first-fit greedy
sin look-ahead, los deja sin presupuesto porque records triviales pequeños se aceptan antes en el mismo
recorrido. Ninguna de las dos capas fue reportada correctamente en el diagnóstico R3 original (que afirmó,
incorrectamente, que el 100% de los ricos excedía el presupuesto individual) — el rebaseline (sección 6) lo
corrigió con datos reales reproducidos dos veces.

## 4. Corrección proposal diversity

Heredada de V4.3 (rondas previas a esta, `_bucketed_order`/`_richness_bucket` en `ai_projection.py`): garantiza
que `select_flow_ids` ofrezca candidatos de los cuatro buckets de riqueza en round-robin, no solo los más
triviales. Esta corrección **no** se tocó en R9; se preserva sin cambios (confirmado, sección 7 de este
documento).

## 5. Corrección context budget

Heredada (V4.3 final AI pilot R2, "skip, never break" en `AiProjectionBuilder.package"`): un candidato que no
cabe se salta, nunca aborta el resto del empaquetado. Preservada sin cambios en R9.

## 6. Diagnóstico selection/packing

`docs/V4_3/V4_3_FINAL_AI_PILOT_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_RESULT.md` +
`docs/V4_3/V4_3_WORKSTATION_REBASELINE_RESULT.md`: diagnóstico de dos capas descrito en la sección 3 de este
documento, reproducido dos veces contra el repositorio legacy real (`prueba_01`/`prueba_02`, luego
`v4_3_rebaseline`), con la herramienta de solo lectura `tools/v4_3_ai_selection_diagnostic.py` (nunca reimplementa
las funciones productivas, las reutiliza).

## 7. Workstation rebaseline

`docs/V4_3/V4_3_WORKSTATION_REBASELINE_RESULT.md`: reconstrucción completa del entorno en un equipo distinto
tras la pérdida de los outputs externos originales (`E:\IAProyectos\...`, nunca versionados en el repo por
política). Reprodujo `flow_count=12642` idéntico, `2148 tests, 0 fallos, 0 errores, 132 skips` como baseline
previo a R3A-R1, y corrigió una contradicción numérica del diagnóstico R3 original (9680 vs. "100% de los
ricos exceden 16000" — falso, verificado: 5/40 caben individualmente).

## 8. R3A-R1

`docs/V4_3/V4_3_R3A_R1_SELECTION_PACKING_QUALITY_CORRECTION_RESULT.md`: corrección real de código en
`AiProjectionBuilder.package` (empaquetado en dos pasadas: reserva de como máximo un candidato rico por bucket
0/1 que quepa individualmente, luego backfill idéntico a la lógica preexistente). Verificada matemáticamente
segura (el costo total no depende del orden de agregación, solo del conjunto elegido), y verificada contra el
output real reconstruido: `FLOW-0004993422` (9680 caracteres, el más pequeño de los 5 candidatos capa-2) pasó
de excluido a incluido en el paquete final (`rich_in_final_request_count` 0 → 1).
`select_flow_ids`/`_bucketed_order`/`_richness_bucket`/`EvidenceHydrator`/`composer.PROFILES`/
`measure_request_payload`/`CopilotProvider`/`SYSTEM_INSTRUCTION`/`USER_INSTRUCTION`/`FINDING_SCHEMA`/
`proposal_adapter`/`consumer_projection` no fueron tocados por R3A-R1 (confirmado en su propio documento de
resultado, sección 6). 21 tests nuevos, suite completa `2169 tests, 0 fallos, 0 errores, 132 skips`.

## 9. Piloto real final

Ejecutado tras R3A-R1 contra `C:\PruebasLegacyMapper\Resultados\v4_3_ai_rerun_r3a_r1_retry1`. Verificado
directamente en esta ronda (no solo citado):

```text
status: SUCCESS
ai_requested: true
ai_invoked: true
AI_INTERPRETATION: SUCCESS
PROPOSAL_GENERATION: SUCCESS
proposal_count: 4
proposal_review_status: PENDING_TECHNICAL_LEAD_REVIEW
canonical_knowledge_produced: false
technical_lead_approval: false
provider_id: copilot-local
model_id: gpt-5.6-luna
```

Todas las etapas del pipeline (`SCAN`..`FINAL_SUMMARY`, incluidas `AI_INTERPRETATION`/`PROPOSAL_GENERATION`)
`SUCCESS`. Búsqueda explícita de `CONTEXT_TOO_LARGE`/`PROVIDER_ERROR`/`BUDGET_INSUFFICIENT` en todo el árbol de
salida del piloto (`RUN_SUMMARY.json`, `RUN_SUMMARY.md`, `proposals/`, `OUTPUT_MANIFEST.json`): **ninguna
coincidencia**. Verificación adicional de ausencia de secretos: grep de patrones de credencial/API
key/token/bearer sobre `OUTPUT_MANIFEST.json`, `RUN_SUMMARY.json`, `proposals/AI_PROPOSALS.json`: **sin
coincidencias**.

No se copió ningún output real completo al repositorio — solo esta revisión y sus hallazgos, en este
documento.

## 10. Revisión de las 4 propuestas

Revisadas una por una en esta ronda, con `evidence_refs` verificados contra `index/*.json` del propio piloto
(`entry_points.json`, `functional_flows.json`, `functional_paths.json`, `data_access.json`) — **las 17
referencias de evidencia de las 4 propuestas existen realmente** en el índice determinista producido por el
mismo run (verificado programáticamente, no por inspección).

### PRP-3b4be84a5598d9ea0ad74aa6fc7ecd05b64aec2ba2e801a860978819ab5c7da4

```text
flow_id: FLOW-0002725421
entry_point_id: EP-0888451805
confidence: CONFIRMED
statement: "The DataBinding entry point dgrVariables_DataBinding is classified as confirmed and has one path
  ending at a dead end; no data operations, stored procedures, or SQL operations are recorded."
evidence_refs: EP-0888451805, FLOW-0002725421, PATH-0fbb8cc8c634fc1274e95bc8c38e4009e9471f16d8a8eac0828b111b1ad18b4e
clasificación: TRIVIAL_GROUNDED
```

Soportada por evidencia determinista: el statement describe correctamente un dead-end sin operaciones de
datos, no inventa semántica, no convierte incertidumbre en certeza (usa "confirmed" solo para la clasificación
del entry point, no para inventar un terminal resuelto que no existe). Grounded pero trivial — exactamente el
tipo de hallazgo que las rondas previas documentaron como dominante antes de R3A-R1.

### PRP-3a3c78c55ebd4db029b9833f96324552b04e4cea7c5ab563776f6210c97c5507

```text
flow_id: FLOW-0004993422
entry_point_id: EP-0931393924
confidence: CONFIRMED
statement: "The hypAnular_Click flow includes a confirmed transaction data-access operation,
  PreAdhClasuc.txeliminar, with the transaction verb BeginTrans."
evidence_refs: DAO-0932211932, EP-0931393924, FLOW-0004993422, PATH-cb5c81d96ce75e2a437ee633a962efa6ba2d1431fb3326799423cab252269051
clasificación: RICH_GROUNDED
```

Este es exactamente el flow que R3A-R1 rescató del budget (9680 caracteres, antes excluido en el 100% de las
corridas previas). El statement representa correctamente una operación transaccional confirmada citando el DAO
real (`PreAdhClasuc.txeliminar`) y el verbo de transacción (`BeginTrans`), sin inventar ningún detalle no
presente en la evidencia hidratada. **Prueba directa del valor de la corrección R3A-R1**: sin ella, ningún
candidato de este flow habría llegado nunca al modelo.

### PRP-78d9a81744078c4b6627890df7d3e63efb43abaa24d0a74ec2e023cd67d07561

```text
flow_id: FLOW-0004993422
confidence: UNCERTAIN
statement: "The hypAnular_Click flow also contains unresolved paths whose boundaries include
  PreAdhClasuc.eliminar(...), dbc.BeginTrans(), dbc.Close(), dbc.Rollback(), dbc.Commit(), and DesplegarError(ex)."
evidence_refs: FLOW-0004993422, PATH-35c23886..., PATH-3af54d8a..., PATH-74e660c9..., PATH-7603bdba...,
  PATH-ae7b8da7..., PATH-dc37e974... (6 paths)
clasificación: UNRESOLVED_GROUNDED
```

Del mismo flow rescatado. El statement mantiene explícitamente la incertidumbre ("unresolved paths",
confidence `UNCERTAIN`) sin promoverla a certeza, y enumera límites de infraestructura conocidos
(`BeginTrans`/`Close`/`Rollback`/`Commit`/`DesplegarError`) tal como el índice real los registra — no inventa
qué hay después de esos límites. Segunda prueba de que el modelo usó la evidencia rica de `FLOW-0004993422`
cuando llegó, distinguiendo correctamente entre el camino confirmado (propuesta anterior) y los caminos
todavía no resueltos del mismo flow.

### PRP-998320af1e798a68bda9b07422bad15af2c05c8c63980c9246c8085abf145320

```text
flow_id: FLOW-0000051656
entry_point_id: EP-0568583646
confidence: UNCERTAIN
statement: "The Page_Init entry point ucADHManAntGenSI has unresolved confidence, with two unresolved paths
  that both terminate at InitializeComponent()."
evidence_refs: EP-0568583646, FLOW-0000051656, InitializeComponent(), PATH-1de02b10..., PATH-5fe64c55...
clasificación: UNRESOLVED_GROUNDED (ruido técnico conocido, deuda F06 — ver sección 13)
```

Terminal `InitializeComponent()` es ruido técnico ya documentado como deuda conocida (F06); el statement lo
declara explícitamente como `unresolved`/`UNCERTAIN`, no lo disfraza de hallazgo funcional. No inválido: la
propuesta no inventa nada, solo reporta correctamente un terminal de bajo valor.

Ninguna propuesta se clasifica `INVALID_OR_UNSUPPORTED`. Ninguna propuesta fue aprobada automáticamente en esta
ronda — las 4 permanecen `PENDING_TECHNICAL_LEAD_REVIEW`/`READY_FOR_REVIEW`, sin cambio de estado.

## 11. Tests finales

```text
cd C:\dev\LegacyMapper
python -m unittest discover -s tests

Ran 2169 tests in 117.776s
OK (skipped=132)
```

`0 failed`, `0 errors`, `132 skipped` — ejecutado directamente en esta ronda (no solo citado de R3A-R1), mismo
conteo exacto que `V4_3_R3A_R1_SELECTION_PACKING_QUALITY_CORRECTION_RESULT.md` sección 8. Los 132 skips
corresponden a los mismos dumps externos no versionados ya documentados (`output/v2_r5_1_full/`,
`output/v3_r8_1/`), consistentes con `PROJECT_STATE.json.all_skips_explained=true`. No se modificó ningún
test ni baseline para forzar verde en esta ronda.

## 12. Runtime Independence

**PASS.**

- Ningún módulo bajo `legacy_documenter/` lee ni depende de `docs/`, `prompts/`, `tests/`,
  `PROJECT_STATE.json`, ni de ningún documento de gobernanza/resultado de ronda (verificado: ningún
  `open()`/import bajo `legacy_documenter/` referencia esas rutas).
- El provider Copilot sigue siendo opcional: `legacy_documenter/llm/providers/copilot.py` solo importa
  `asyncio`/`inspect`/`json`/`re`/`time`/módulos internos a nivel de módulo; `from copilot import
  CopilotClient` y `from copilot.generated.rpc import ...` están dentro de `async def _generate`/`async def
  deny`, nunca a nivel de módulo — confirmado leyendo el archivo directamente en esta ronda.
- Ejecución determinista sigue funcionando sin `github-copilot-sdk`: la suite completa (2169 tests) no invoca
  ningún provider real (`FakeLLMProvider` en todos los tests de IA), y la importación de
  `legacy_documenter.cli.full_pipeline`/`legacy_documenter.orchestration` no requiere el SDK de Copilot a nivel
  de módulo.
- `requirements-copilot.txt` sigue siendo dependencia opcional: su propio contenido lo declara explícitamente
  ("Optional runtime dependency for the COPILOT provider only... not required to run deterministic analysis,
  the FAKE provider, or the test suite").
- No existen secretos persistidos: grep de patrones de credencial/API key/token/bearer sobre el repositorio
  completo (`*.py`, `*.json`, `*.md`) y sobre el manifiesto/propuestas del piloto real: **sin coincidencias**
  en ningún caso (secciones 9 y esta sección).

## 13. Restricciones preservadas

Verificado en esta ronda: ninguno de los símbolos protegidos por la sección 14 del prompt fue tocado durante
R9 — `select_flow_ids`, `_bucketed_order`, `AiProjectionBuilder.package`, `EvidenceHydrator`,
`composer.PROFILES`, `measure_request_payload`, `CopilotProvider`, `SYSTEM_INSTRUCTION`, `USER_INSTRUCTION`,
`FINDING_SCHEMA`, `proposal_adapter`, `consumer_projection`. Esta ronda es exclusivamente de revisión y
documentación de cierre; no se ejecutó ninguna optimización adicional, no se inició V5, no se implementó
Plugin Runtime, no se introdujo funcionalidad nueva.

## 14. Deudas que pasan a V5/post-V5

Documentadas, no corregidas en esta ronda:

- **F05**: duration pendiente por compatibilidad byte-identical previa (`PROJECT_STATE.json.r7_findings.F-05:
  DEFERRED_BY_DETERMINISM_CONTRACT`, sin cambios).
- **F06**: ruido `InitializeComponent` — visible de nuevo en esta misma ronda en
  `PRP-998320af1e798a68bda9b07422bad15af2c05c8c63980c9246c8085abf145320` (sección 10), confirmando que sigue
  siendo una fuente de propuestas de bajo valor, correctamente marcada como `UNCERTAIN`/no confirmada, no un
  defecto.
- **F07**: gaps de `outgoing_calls` en markup WebForms (`PROJECT_STATE.json.r7_findings.F-07:
  PRESERVED_OBSERVATION`, sin cambios).
- Flows ricos gigantes que siguen sin caber completos bajo `SMALL`: 35/40 candidatos ricos de este
  repositorio real exceden individualmente el presupuesto completo de `SMALL` (16000 caracteres); R3A-R1
  resolvió la capa de orden de evaluación (5/40), no la de tamaño real (35/40) — partición de un record rico
  en sub-unidades citables evaluada y rechazada explícitamente en R3A-R1 por requerir un contrato nuevo fuera
  de alcance.
- Contrato eventual de partición parcial de evidence records (evaluado y rechazado para V4.3, ver
  `V4_3_R3A_R1_SELECTION_PACKING_QUALITY_CORRECTION_RESULT.md` sección 2, punto 2).
- Approval Surface (`approval_surface_implementation: NOT_IMPLEMENTED`, sin cambios).
- Plugin Runtime (no implementado, fuera de alcance de V4.3).
- Abstracción de provider genérica.
- Abstracción genérica de tecnología/base de datos/layout.
- Normalización multi-tecnología.
- Deuda de UX de nombres (p. ej. `confidence`) si sigue vigente — no se encontró documentación V4.3 abierta
  específicamente sobre este punto; se registra como posible debt residual heredado del prompt de esta ronda,
  sin evidencia adicional que lo precise en esta revisión.

Ninguna de estas deudas se convirtió en cambio funcional durante R9.

## 15. Estado final

`V4_3_CLOSED`.

- V4.3 queda cerrada funcional y documentalmente.
- El piloto real (`copilot-local` / `gpt-5.6-luna`, post-R3A-R1) validó la cadena completa: legacy real →
  análisis determinista → selección/hydration → packing con evidencia rica → request dentro de budget →
  Copilot real → findings grounded → propuestas pendientes de revisión.
- Las 4 propuestas del piloto siguen requiriendo revisión humana explícita (`PENDING_TECHNICAL_LEAD_REVIEW`);
  ninguna fue aprobada, canonicalizada, ni modificada por esta ronda.
- V5 queda habilitada como siguiente línea de trabajo (desacoplamiento core↔tecnología, core↔provider, Plugin
  Runtime, según decisión de alcance futura) — no iniciada en esta ronda.
