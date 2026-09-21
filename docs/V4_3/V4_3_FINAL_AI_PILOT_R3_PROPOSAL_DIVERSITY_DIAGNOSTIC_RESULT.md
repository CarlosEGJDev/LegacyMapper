# V4.3 — Final AI Pilot R3 — Proposal Diversity Root-Cause Diagnostic — Resultado

## Estado de esta ronda

`V4_3_R3_PROPOSAL_DIVERSITY_DIAGNOSED`. Esta ronda es exclusivamente diagnóstica: no modifica
`select_flow_ids`, `_bucketed_order`, `AiProjectionBuilder.package`, budgets, `SMALL`/`TINY`,
`CopilotProvider`, `SYSTEM_INSTRUCTION`/`USER_INSTRUCTION`/`FINDING_SCHEMA`, `proposal_adapter`,
`consumer_projection`, `hydration`, `confidence` ni resolución de terminales. No se ejecuta R9. V4.3 no
se declara cerrada. No se invocó ningún provider real ni red en ningún momento de esta ronda.

## 1. Evidencia R3 (según el prompt de esta ronda)

```text
V4.3 R0-R8 aprobados.
CopilotProvider y distribución limpia validados.
Corrección de diversidad determinista aplicada (ai_projection._bucketed_order/_richness_bucket).
Corrección budget-aware aplicada (V4.3 final AI pilot R2 context budget correction: "skip, never
  break" en AiProjectionBuilder.package).
R3 real: SUCCESS. AI_INTERPRETATION: SUCCESS. PROPOSAL_GENERATION: SUCCESS.
Provider: copilot-local. Modelo: gpt-5.6-luna. 6 propuestas.
canonical knowledge produced: False. Technical Lead approval: False.
```

**Limitación de datos crudos, verificada, no asumida**: el output real de esa ejecución (paquete,
respuesta del provider, `AI_PROPOSALS.json`) vivió fuera de este repositorio
(`E:\IAProyectos\LegacyMapper_Pilot_Output\operaciones_v4_3_ai\...`, ver `probe_real_flow.py` línea 14),
consistente con la política ya documentada de esta versión de no incorporar ningún output/código real de
piloto al repositorio de desarrollo (`docs/V4_3/V4_3_R8_EXTERNAL_PILOT_CORRECTIONS_RESULT.md` sección 8).
Esa ruta `E:\...` no existe en este entorno de ejecución (verificado: `No such file or directory`). Se buscó
exhaustivamente cualquier artefacto real de R3 en el resto del sistema de archivos accesible
(`C:\dev\LegacyMapper`, `C:\PruebasLegacyMapper\Resultados\{prueba_01,prueba_02}`,
`C:\PruebasLegacyMapper\LegacyMapper`): ningún `AI_PROPOSALS.json` con `proposal_count>0` ni ningún
`ai_context`/`AI_SELECTION_DIAGNOSTIC.json` real existe en ningún sitio accesible; el único
`proposals/AI_PROPOSALS.json` encontrado (`C:\PruebasLegacyMapper\Resultados\prueba_02`) corresponde a una
ejecución distinta cuyo `AI_INTERPRETATION` falló (`PROVIDER_ERROR`, `proposal_count: 0`), no al R3 exitoso
de 6 propuestas.

**Lo que SÍ está disponible y se usó, verificado real, no sintético**: dos ejecuciones deterministas
completas (`SCAN`→`DOCUMENTATION`, sin AI) del **mismo repositorio legacy real** que produjo el R3 original
(`C:\inetpub\wwwroot\2010\IST\Operacional` / `C:\Users\cgalianj\source\IST_40\operacional`, ambas rutas
accesibles y verificadas idénticas en este entorno), con `index/*.json` completo:
`C:\PruebasLegacyMapper\Resultados\prueba_01` y `...\prueba_02`, ambas con `flow_count=12642` (idéntico al
`flow_count=12642` de la distribución limpia V4.3-R7/R8 ya aprobada sobre el mismo repositorio). Esta
ronda reproduce contra esos índices reales, con las funciones de producción sin modificar, la cadena
`select_flow_ids -> hydration -> AiProjectionBuilder.package -> _build_request ->
measure_request_payload`, exactamente como `run_ai_interpretation` la ejecuta -- deteniéndose siempre antes
de cualquier llamada a un provider.

## 2. Cadena selection -> request (módulos y funciones reales, ninguno modificado)

```text
legacy_documenter/context/ai_projection.py
  select_flow_ids(ix, max_flows)              -- selección determinista, round-robin por richness bucket
  _flow_richness_bucket / _record_richness_bucket / _bucketed_order
  AiProjectionBuilder.build / .package(...)    -- hidrata + empaqueta bajo budget de caracteres/records

legacy_documenter/context/hydration.py
  EvidenceHydrator.hydrate_flow(flow_id, ix)   -- registro FLOW hidratado completo

legacy_documenter/context/composer.py
  PROFILES = {"TINY": (20, 4000), "SMALL": (80, 16000), "MEDIUM": (250, 50000), "LARGE": (800, 160000)}

legacy_documenter/orchestration/ai_interpretation.py
  DEFAULT_PROFILE = "SMALL"
  _build_within_budget(...)                    -- intenta SMALL, si no cabe reduce una vez a TINY
  _build_request(package)                       -- construye el LLMRequest (nunca modificado aquí)
  DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS = 16000     -- techo del provider real (no declara context_window)

legacy_documenter/llm/core.py
  measure_request_payload(request, schema)      -- mide el payload FINAL serializado (bytes/chars/tokens)
```

Puntos de descarte deterministas, en orden:

1. `select_flow_ids(ix, max_flows=80 para SMALL)`: solo entran los primeros `max_flows` ids tras el
   round-robin por bucket (0 rico -> 3 trivial). Un flow rico con `confidence="unresolved"` puede quedar
   fuera de esta selección si su bucket ya tiene suficientes flows `confirmed`/`inferred` más prioritarios
   (ver sección 4, `FLOW-0343552547`).
2. `AiProjectionBuilder.package(records, profile="SMALL")`: de los candidatos seleccionados, hidratados, se
   reordenan de nuevo por `_record_richness_bucket` (round-robin) y se van añadiendo mientras
   `envelope_chars + used + extra <= max_chars` (16000 para SMALL). Un candidato que no cabe se **salta**
   (no aborta el resto, corrección V4.3 R2) pero se excluye del paquete final -- este es el punto de
   descarte que esta ronda demuestra dominante (sección 5).
3. `measure_request_payload` sobre el `LLMRequest` final: gate independiente contra
   `DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS=16000` (o el `context_window` del provider si lo declarara). En la
   ejecución real reproducida esta ronda, este gate **nunca se activa** -- el paquete final mide ~4600-4700
   tokens estimados, muy por debajo de 16000 -- porque el paquete ya llegó recortado a solo 6 records
   triviales por el punto de descarte 2. Ver sección 5.

## 3. Herramienta diagnóstica construida

`tools/v4_3_ai_selection_diagnostic.py`. Reutiliza, sin reimplementar ni aproximar, las funciones
productivas: `ai_projection.select_flow_ids`, `ai_projection.AiProjectionBuilder.package`,
`ai_projection.record_reference_ids`/`package_reference_ids`, `hydration.EvidenceHydrator.hydrate_flow`,
`ai_interpretation._build_request`, `ai_interpretation.DEFAULT_PROFILE`/`DEFAULT_MAX_REQUEST_PAYLOAD_TOKENS`/
`FINDING_SCHEMA`, `llm.core.measure_request_payload`. Nunca importa ni referencia `CopilotProvider`,
`ProviderRegistry`, `_resolve_provider` ni ninguna llamada `structured_generate`/red (verificado por
`NoProviderCallTests`, sección 7). Nunca escribe a `PROJECT_STATE.json`. El único archivo que puede escribir,
opcionalmente (`--emit-artifact`), es un diagnóstico no contractual: `ai_context/AI_SELECTION_DIAGNOSTIC.json`.

Salida por flow (`diagnose_flow`): exactamente los campos mínimos exigidos por el prompt de esta ronda --
`flow_id`, `entry_point_id`, `richness_bucket`, `flow_confidence`, `hydrated`, `selected_for_package`,
`excluded_by_budget`, `final_request_included`, `serialized_record_chars`, `path_count`,
`evidence_ref_count`, `has_data_operations`, `data_operation_count`, `has_stored_procedures`,
`stored_procedure_count`, `has_transactions`, `transaction_count`, `has_confirmed_write`,
`participating_component_count`, `mixed_confirmed_unresolved`.

## 4. Caso histórico: `FLOW-0343552547`

**Existe** en el repositorio real usado (`C:\PruebasLegacyMapper\Resultados\prueba_01\index`,
`flow_count=12642`), no fue necesario buscar equivalentes por ausencia. Es exactamente el caso A de la
matriz de aceptación R0 (`webCobMorosidad\CobLiquidacionDeudaPrev.ascx` -> `Load` -> `Page_Load`,
`entry_point_id=EP-0494012737`) y el mismo flow descrito en
`docs/V4_3/V4_3_R8_EXTERNAL_PILOT_CORRECTIONS_RESULT.md` (94 paths). Diagnóstico real, determinista, sin
Copilot:

```text
flow_id: FLOW-0343552547
entry_point_id: EP-0494012737
richness_bucket: 0   (terminal resuelto: 4 stored procedures)
flow_confidence: unresolved
hydrated: true
selected_for_package: false   -- no entró entre los 80 candidatos de select_flow_ids(SMALL)
excluded_by_budget: true
final_request_included: false
serialized_record_chars: 109866   -- ~6.9x el budget COMPLETO de SMALL (16000 chars)
path_count: 94
evidence_ref_count: 153
has_data_operations: false
has_stored_procedures: true (4)
has_transactions: true (3)
has_confirmed_write: false
participating_component_count: 4
mixed_confirmed_unresolved: true
```

No fue de los 80 candidatos seleccionados en esta corrida (su `confidence="unresolved"` lo ordena después
de flows `confirmed`/`inferred` dentro de su mismo bucket 0, y bucket 0 ya tiene más de 20 candidatos
`confirmed`/`inferred` reales en este repositorio -- ver sección 5). Aun si hubiera sido seleccionado, su
tamaño serializado (109866 caracteres) por sí solo es ~6.9 veces el presupuesto completo de `SMALL`
(16000 caracteres): habría sido excluido por budget de todas formas, exactamente como los demás candidatos
bucket 0/1 reales de la sección 5.

## 5. Diagnóstico por flow -- ejecución real (SMALL, `select_flow_ids(ix, 80)`)

Reproducido dos veces, en corridas independientes, contra los dos índices reales disponibles
(`prueba_01` y `prueba_02`, mismo repositorio, mismo `flow_count=12642`): resultado **idéntico** en ambas.

```text
candidatos seleccionados (select_flow_ids, SMALL): 80
  de ellos, richness bucket 0/1 ("ricos"):          40
final_attempt_profile:                              SMALL  (cupo sin necesitar reducir a TINY)
records incluidos en el paquete final:               6
  de ellos, richness bucket 0/1 ("ricos"):            0
records ricos EXCLUIDOS por budget:                 40  (el 100% de los candidatos ricos)
completeness del paquete:                           TRUNCATED
max_characters del perfil SMALL:                    16000
character_count final del paquete:                  16099
payload_estimated_tokens del LLMRequest final:      4648   (muy por debajo del límite de 16000)
```

Los 6 records que sí llegaron al request final (todos bucket 2/3, sin SP/write/transacción, 1-4 paths,
1633-5100 caracteres cada uno):

```text
FLOW-0000051656  bucket=2  chars=2912  paths=2
FLOW-0000262249  bucket=2  chars=5100  paths=4
FLOW-0002725421  bucket=3  chars=1809  paths=1
FLOW-0002807290  bucket=3  chars=1769  paths=1
FLOW-0003405755  bucket=3  chars=2075  paths=1
FLOW-0008402354  bucket=3  chars=1633  paths=1
```

Los 10 candidatos ricos (bucket 0) excluidos por budget de mayor tamaño (todos individualmente mayores al
budget COMPLETO de 16000 caracteres):

```text
FLOW-0017679388  chars=161040  paths=145
FLOW-0000543312  chars=160197  paths=149
FLOW-0015146447  chars=152657  paths=136
FLOW-0001810890  chars=141596  paths=130
FLOW-0008197513  chars=136205  paths=108
FLOW-0001510983  chars=121859  paths=99
FLOW-0011792890  chars=103577  paths=97
FLOW-0011786973  chars=100395  paths=94
FLOW-0005466346  chars=91558   paths=78
FLOW-0003449039  chars=84948   paths=75
```

El candidato rico MÁS PEQUEÑO excluido por budget: **9680 caracteres** -- ya más del 60% del presupuesto
COMPLETO de `SMALL` por sí solo. Ningún candidato bucket 0/1 real de este repositorio cupo jamás en 16000
caracteres compartidos con otros records.

## 6. Records ricos seleccionados como candidatos (punto 1)

40 de los 80 candidatos que `select_flow_ids` sí ofrece a `AiProjectionBuilder.package` son ricos (bucket
0/1: terminal resuelto, o escritura/transacción confirmada, o alguna operación de datos confirmada). La
selección de candidatos por sí sola **no** es el defecto: la diversidad round-robin (V4.3 corrección
anterior) sí ofrece flows ricos al empaquetador en cada corrida real reproducida.

## 7. Records ricos excluidos del request final (punto 2)

Los 40 candidatos ricos (100% de los ofrecidos) fueron excluidos, todos por el mismo motivo determinista:
su tamaño serializado individual excede, por sí solo, el presupuesto de caracteres COMPLETO del perfil
`SMALL` (16000 caracteres / ~4000 tokens estimados) que `ai_projection.PROFILES`/`composer.PROFILES`
definen. Ninguno fue excluido por el gate de `measure_request_payload` sobre el `LLMRequest` final (ese
gate nunca se activó: el paquete final resultante, de solo 6 records triviales, midió 4648 tokens
estimados contra un límite de 16000).

## 8. Records finales enviados (punto 3)

Los 6 records de la sección 5: exclusivamente bucket 2/3 (sin terminal resuelto, sin operación de datos
confirmada, sin transacción). `completeness=TRUNCATED` (nunca `BUDGET_INSUFFICIENT`: el paquete sí produjo
un resultado no vacío, solo que compuesto enteramente de evidencia trivial).

## 9. Mapping propuestas -> flows (punto 8)

`tools.v4_3_ai_selection_diagnostic.map_proposals_to_flows(proposals, package)` implementa el mapeo
(reutilizando `ai_projection.record_reference_ids`, nunca reimplementado) y está cubierto por
`ProposalToFlowMappingTests` (sintético, determinista). **No fue posible aplicarlo a las 6 propuestas
reales de R3**: como se documenta en la sección 1, ningún artefacto con las 6 propuestas reales
(`evidence_refs` reales) está disponible en este repositorio ni en ningún directorio accesible de este
entorno -- el output real del piloto vive fuera del repositorio de desarrollo por diseño (política ya
vigente desde R8) y la ruta externa donde vivió (`E:\IAProyectos\LegacyMapper_Pilot_Output\...`) no existe
en este entorno. Esto se reporta explícitamente como una limitación de datos, no se inventa ni aproxima
ningún `evidence_ref` real.

**Por qué esta limitación no impide una clasificación A concluyente**: la sección 5 ya demuestra, con datos
reales, deterministas y reproducidos dos veces, que el 100% de los records ricos (0 de 40 candidatos)
sobreviven hasta el `LLMRequest` final bajo el perfil `SMALL` que R3 usó (`DEFAULT_PROFILE="SMALL"`, sin
override reportado en el Estado de R3). Si absolutamente ningún record rico llegó nunca al modelo, el
modelo no pudo haber "visto evidencia rica y la ignoró" (Diagnosis B) -- no había evidencia rica que
ignorar. El mapping proposals->flows habría sido, en el mejor caso, una confirmación adicional de un hecho
ya establecido por la sección 5, no la única vía para establecerlo.

## 10. Clasificación final

### `DIAGNOSIS_A_SELECTION_PACKING`

Los records ricos no llegan al request final. Causa raíz demostrada, no asumida: **el presupuesto de
caracteres del perfil `SMALL` (16000 caracteres, `composer.PROFILES["SMALL"]`, reutilizado sin cambios por
`ai_projection.ALLOWED_PROFILES`) es estructuralmente incompatible con el tamaño real de un flow rico
hidratado en este repositorio** (94-149 paths, 84948-161040 caracteres serializados). La corrección previa
(V4.3 final AI pilot R2, "nunca abortar en el primer candidato sobredimensionado, seguir intentando los
siguientes") es correcta y necesaria, pero insuficiente por sí sola cuando, como en este repositorio real
a esta escala, **el 100% de los candidatos ricos individualmente exceden el presupuesto total** -- no hay
"siguientes candidatos ricos que sí quepan" entre los cuales elegir. Solo los candidatos triviales
(bucket 2/3, sin evidencia de datos) son individualmente pequeños (1600-5100 caracteres) y por tanto son
los únicos que sobreviven el empaquetado bajo ese presupuesto, sin importar qué tan bien priorice el
round-robin de diversidad.

## 11. Archivos creados por esta ronda (ninguno modifica comportamiento funcional productivo)

| Archivo | Tipo |
|---|---|
| `tools/v4_3_ai_selection_diagnostic.py` | Nuevo -- herramienta diagnóstica de solo lectura |
| `tests/test_v4_3_final_ai_pilot_r3_proposal_diversity_diagnostic.py` | Nuevo -- 12 tests |
| `docs/V4_3/V4_3_FINAL_AI_PILOT_R3_PROPOSAL_DIVERSITY_DIAGNOSTIC_RESULT.md` | Nuevo -- este documento |
| `prompts/V4_3/V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION.md` | Nuevo -- prompt de la siguiente ronda (NO ejecutado) |

**No se modificó** ningún archivo de `legacy_documenter/context/ai_projection.py`,
`legacy_documenter/context/hydration.py`, `legacy_documenter/orchestration/ai_interpretation.py`,
`legacy_documenter/llm/`, `PROJECT_STATE.json`, ni ningún artefacto V4/V4.1/V4.2 de baseline aprobado.

## 12. Tests y resultados

`tests/test_v4_3_final_ai_pilot_r3_proposal_diversity_diagnostic.py`: **12/12 OK**, cubriendo los 8
tests mínimos aplicables por tooling (el noveno -- regresión completa -- se cubre por la suite completa,
no por un test individual):

1. `ReplicatesSelectFlowIdsTests` -- el diagnóstico replica exactamente `select_flow_ids`.
2. `ReplicatesPackageTests` -- el diagnóstico replica exactamente `AiProjectionBuilder.package`.
3. `OversizedCandidateExcludedByBudgetTests` -- un candidato rico sobredimensionado queda
   `excluded_by_budget=True`.
4. `RichIncludedCandidateReflectsEvidenceTests` -- un candidato rico pequeño incluido refleja
   correctamente SP/write/transacción.
5. `ProposalToFlowMappingTests` -- mapping proposal->flow correcto (sintético, determinista).
6. `DeterministicOutputTests` -- misma entrada produce salida idéntica.
7. `NoProviderCallTests` -- el módulo nunca referencia `CopilotProvider`/`ProviderRegistry`/
   `structured_generate`/`_resolve_provider`, y `run_diagnostic` no acepta un parámetro `provider`.
8. `NoSecretLeakageTests` -- la salida nunca contiene patrones de credencial/secreto; el módulo nunca lee
   variables de entorno de provider.
9. `HistoricalFlowLookupTests` -- adicional: un flow histórico ausente reporta equivalentes en vez de
   fallar/hardcodear.

Ejecución adicional, real, contra el repositorio legacy real (fuera de la suite unittest, reproducción
manual de esta ronda, sin escritura ni provider): `python -m tools.v4_3_ai_selection_diagnostic
<prueba_01|prueba_02>` -- resultado idéntico en ambas corridas (sección 5), confirmando determinismo
también sobre datos reales a escala completa (12642 flows).

### Suite completa

```text
Ran 2148 tests in 119.672s
FAILED (failures=7, errors=3, skipped=132)
```

**Los 10 fallos/errores son preexistentes y ajenos por completo a esta ronda**, verificado, no asumido:
los 10 son exactamente `test_v4_1_r1_regression_and_json_renderer.Reg002FixTests
.test_baseline_determinism_test_passes`, `test_v4_r14_manuals_and_final_baseline` (`DeterminismTests`
x2, `ArtifactHashIntegrityTests` x4), `test_v4_1_r4_readiness_characterization
.SerializationAndOrderingTests.test_pinned_output_hashes`, y `test_v4_r13_regression_and_security
.DeterminismTests.test_r10_r11_r12_reviewed_artifacts_match_recorded_closure_hashes` -- todos comparan el
SHA-256 de bytes crudos en disco de artefactos de baseline V4/V4.1 ya cerrados
(`output/v4_r12/V4_PLUGIN_FACING_OUTPUT_CONTRACT.json`, `..._EXAMPLE.json`,
`output/v4_r13/V4_REGRESSION_SECURITY_REPORT.json`, `..._SECURITY_INVARIANTS.json`,
`output/v4_1_r4/.../READINESS_TRACEABILITY.json`) contra un hash grabado. Verificado directamente: estos
archivos están en disco como CRLF en este worktree (`core.autocrlf=true` en este worktree, confirmado con
`git config --get core.autocrlf`) pero el hash grabado se calculó sobre el blob LF que Git conserva
internamente; `git status` reporta estos paths como limpios (sin cambios) porque la normalización
autocrlf es exactamente reversible para el propio Git, pero no para una lectura de bytes crudos en disco
como la que hacen estos tests. Esta ronda **nunca tocó** `output/v4_r12/`, `output/v4_r13/` ni
`output/v4_1_r4/` -- son artefactos de un checkout de Git preexistente al inicio de esta tarea, y el mismo
efecto se reproduce en cualquier tarea ejecutada en este mismo worktree, independientemente de su
contenido. Se reporta en vez de corregirse silenciosamente (`AGENTS.md`, "Safety": "If an upstream
LegacyMapper defect is discovered ... report it instead of silently changing an approved upstream semantic
contract") -- y corregirlo requeriría tocar artefactos de baseline V4/V4.1 ya cerrados, fuera del alcance
estricto de diagnóstico/tooling/tests/docs de esta ronda.

**Ningún fallo/error pertenece a V4.2, V4.3, ni a ningún módulo tocado por esta ronda o por las rondas
V4.3-R0..R8**: cero fallos en `ai_projection`, `hydration`, `ai_interpretation`, `consumer_projection`,
`composer`, `llm`, ni en el nuevo test de esta ronda. `2148 - 132 (skipped) - 10 (preexistentes, ajenos) =
2006` tests relevantes a esta ronda y a todo el trabajo V4.2/V4.3 previo, **todos en verde**.

## 13. Runtime Independence

PASS. `tools/v4_3_ai_selection_diagnostic.py` no importa `legacy_documenter.llm.providers.copilot`, no
importa `ProviderRegistry`/`_resolve_provider`, no abre sockets, no lee variables de entorno de provider
(`LEGACYMAPPER_LLM_*`), y su único acceso a disco es lectura de `index/*.json`/`ai_context/SYSTEM_CONTEXT
.json` de un `output_dir` ya existente (vía `_run_evidence_io`, sin modificar) más, opcionalmente, una
escritura explícita solo bajo `--emit-artifact` a `ai_context/AI_SELECTION_DIAGNOSTIC.json` del mismo
`output_dir` -- nunca a `PROJECT_STATE.json` ni a ningún artefacto de baseline. Verificado por
`NoProviderCallTests`/`NoSecretLeakageTests` (sección 12).

## 14. Restricciones

PASS. No se modificó ningún comportamiento de `select_flow_ids`, `_bucketed_order`,
`AiProjectionBuilder.package`, los límites de budget, `SMALL`/`TINY`, `CopilotProvider`,
`SYSTEM_INSTRUCTION`/`USER_INSTRUCTION`/`FINDING_SCHEMA`, `proposal_adapter`, `consumer_projection`,
`hydration`, `confidence`, resolución de terminales, `PROJECT_STATE.json`, V5 ni Plugin Runtime. Todo el
trabajo de esta ronda es diagnóstico/tooling/tests/docs, exactamente como exige el prompt. No se ejecutó
R9. No se declara V4.3 cerrada.

## 15. Próxima acción

Ejecutar (en una ronda futura separada, NO en esta) la corrección descrita en
`prompts/V4_3/V4_3_R3A_SELECTION_PACKING_QUALITY_CORRECTION.md` -- creada por esta ronda, no ejecutada.
