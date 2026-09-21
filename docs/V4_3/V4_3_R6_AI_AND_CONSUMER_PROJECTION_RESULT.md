# V4.3 — R6 — Integración IA y consumer projection — Resultado

## Estado de esta ronda

`V4_3_R6_RESULT_IMPLEMENTED_PENDING_HUMAN_REVIEW`. Como R1–R5, esta ronda implementa código de producción.
El `Gate` de R1 ("no avanzar a R2 sin revisión humana", `docs/V4_3/V4_3_R1_CONSUMABLE_PROJECTION_CONTRACT_RESULT.md`
sección 10) sigue quedando satisfecho por la misma vía que R2→R3→R4→R5→R6: la instrucción directa del Líder
Técnico de ejecutar cada ronda (`ejecuta V4_3_R6_AI_AND_CONSUMER_PROJECTION.md`). Esta ronda no cierra ni
versiona V4.3 (sigue correspondiendo exclusivamente a R9), no modifica `PROJECT_STATE.json` y **no inicia R7**.

`REAL_AI_RUNTIME_CALL_ALLOWED=false` sigue vigente: ningún test de esta ronda alcanza un proveedor real; todos
inyectan `FakeLLMProvider` explícitamente. No se ejecutó ninguna verificación manual del camino
`--allow-ai-interpretation` (`AGENTS.md` §"Manual AI-Path Verification").

## 1. Objetivo

`prompts/V4_3/V4_3_R6_AI_AND_CONSUMER_PROJECTION.md`: conectar `evidence projection` con `AI
interpretation`/`proposals`, y materializar `consumer_projection` como JSON estable, sin implementar Plugin
Runtime.

## 2. Diagnóstico previo: qué del objetivo ya estaba implementado

Antes de escribir código nuevo, se verificó contra qué ya existe en el repositorio, punto por punto contra los
seis requisitos de la sección "IA" del prompt:

| Requisito del prompt | Ya implementado | Dónde |
|---|---|---|
| findings citan evidencia incluida | Sí (V4.2-R4, ampliado V4.3-R5) | `ai_interpretation._validate_findings` contra `ai_projection.package_reference_ids` |
| hechos deterministas pueden ser `CONFIRMED` | Sí (V4.3-R2) | `hydration.EvidenceHydrator`: `confidence` se copia tal cual del índice, nunca inventado |
| síntesis AI = `INTERPRETED` (nunca sustituye evidencia determinista) | Sí (V4.2-R4, contrato fijado V4.3-R1 §5.2) | `AssessmentValidator`/`ai_projection.InterpretedContentError`; un finding de IA nunca se escribe como si fuera un hecho `confirmed` de `index/*.json` |
| unresolved preservado | Sí (V4.3-R2) | `EvidenceHydrator.hydrate_flow`: `unresolved` nunca se descarta ni se recategoriza |
| propuestas = `READY_FOR_REVIEW` | Sí (V4.2-R4) | `proposal_adapter.adapt_findings_to_proposals`: `ProposalMethod.AI_PROPOSED` + `transition_proposal(..., READY_FOR_REVIEW)`, nunca `APPROVED` |
| fallo AI no invalida documentación determinista | Sí, estructuralmente (V4.2-R2/R3/R4) | `full_pipeline.run_full_pipeline`: `DOCUMENTATION` corre y se resuelve **antes** de que `AI_INTERPRETATION` siquiera se intente, con su propio `StageResult` independiente |

Los seis eran ya verdaderos en el código antes de esta ronda. **Ninguno de los seis requería una corrección**;
lo que faltaba, y es la única causa de fallo/carencia real encontrada, era la sexta pieza del objetivo:
**`consumer_projection` no existía como JSON real** — R1 §9 lo dejó explícitamente diferido a esta ronda
("No se implementa `consumer_projection` como JSON real (`R6`)"). Esta ronda por tanto:

1. **No modifica** ninguna de las cinco piezas de integración IA/propuestas ya correctas (sección 2 arriba) —
   tocarlas sin una razón concreta violaría "corrige la causa, no el síntoma" y el principio de no introducir
   cambios no solicitados.
2. **Sí añade** una nueva clase de test (`AiIntegrationInvariantTests`,
   `tests/test_v4_3_r6_ai_and_consumer_projection.py`) que **re-verifica end-to-end**, en una única ejecución
   real de `run_full_pipeline`, que las cinco piezas siguen sosteniéndose juntas — no solo individualmente
   como cada ronda anterior ya las probaba por separado.
3. **Sí implementa** `consumer_projection` como JSON real, la pieza que realmente faltaba (sección 3).

## 3. `legacy_documenter/context/consumer_projection.py` (283 líneas)

Ubicación elegida: el mismo paquete `legacy_documenter/context/` donde ya viven `hydration.py` (R2, la fuente
de los registros) y `ai_projection.py` (R5, la otra superficie derivada de los mismos registros) — la capa a
la que pertenece por responsabilidad, exactamente igual que R5 razonó para `ai_projection.py`.

**Corrección posterior a la implementación inicial de esta ronda (aún R6, antes de iniciar R7)**: la primera
versión de este módulo devolvía un único paquete sin acotar, con todos los flujos hidratados dentro de
`records`. R1 §5.3 exige que la superficie sea "razonablemente pequeña"; un repositorio real con miles de
flujos y decenas/cientos de miles de `PATH`s habría convertido ese único archivo en un monolito. Esto **no**
se corrige truncando ni omitiendo evidencia — `SILENT_ENTRY_OMISSION` sigue prohibido — se corrige con
**particionado determinista y completo**: `build` ahora devuelve un *manifest* pequeño más un conjunto
determinista de *particiones*, cada una autocontenida. El resto de esta sección describe la arquitectura ya
corregida.

### 3.1 Arquitectura final: manifest + particiones

```
consumer_projection/
├── CONSUMER_PROJECTION.json   ← manifest: pequeño, siempre, sin importar cuántos flujos existan
└── parts/
    ├── part-000000.json       ← partición: hidratación COMPLETA de sus flujos, autocontenida
    ├── part-000001.json
    └── ...
```

| Símbolo | Responsabilidad |
|---|---|
| `ConsumerProjectionBuilder.build(ix, flow_ids=None, source_snapshot=None) -> (manifest, partitions)` | Hidrata `flow_ids` (o **todos** los flujos de `ix` si se omite) llamando a `EvidenceHydrator.hydrate_flow` — nunca reimplementa la hidratación — y los reparte en particiones deterministas de tamaño acotado |
| `ConsumerProjectionBuilder.package(records, ...) -> (manifest, partitions)` | El mismo particionado sobre registros ya hidratados |
| `build_consumer_projection(...)` | Envoltorio a nivel de módulo sobre `build` |
| `ConsumerProjectionError` | Fallo cerrado explícito ante omisión o duplicación de un flujo entre particiones |
| `partition_filename(index)` / `partition_relative_path(index)` | Derivación determinista del nombre/ruta de una partición |
| `CONTRACT_NAME`, `CONTRACT_VERSION`, `PACKAGE_ID_PREFIX`, `PARTITION_ID_PREFIX`, `DEFAULT_PARTITION_SIZE` | `"LegacyMapperConsumerProjection"`, `"1.0"`, `"CPJ-"`, `"CPJ-PART-"`, `500` |

`manifest` sigue transportando `LegacyMapperConsumerProjection 1.0`, `source_snapshot`, un `package_id`
estable (`CPJ-<sha256>`) y `statistics.completeness = "COMPLETE"` (R1 §5.3, exactamente igual que antes de
esta corrección) — lo que cambió es que `manifest` **ya no contiene `records`**: contiene, en su lugar, el
mínimo necesario para descubrir y localizar cada partición (sección 3.3).

### 3.2 Estrategia de particionado: por cantidad fija de flujos, nunca por etiqueta narrativa

`DEFAULT_PARTITION_SIZE = 500` flujos por partición (configurable vía `ConsumerProjectionBuilder(partition_size=...)`).
Los flujos se ordenan de forma determinista (`flow_id` ascendente, el mismo orden que la versión anterior ya
usaba) y se dividen en cortes consecutivos de tamaño fijo — nunca por proyecto, WebForm, o cualquier otra
etiqueta humana. Esta es la preferencia explícita del prompt de corrección ("particionado por
cantidad/tamaño controlado de registros, no por nombres narrativos o heurísticas humanas"), y es
deliberadamente **distinta** del particionado ya existente en
`legacy_documenter/exporters/_documentation_partitioning.py` (`sanitize_label`/`build_partition_filenames`,
V4.2-R8): ese helper deriva un nombre de archivo a partir de una etiqueta de grupo narrativa (un proyecto, un
WebForm) para *documentación humana* — el prompt de esta corrección pide explícitamente lo opuesto para esta
superficie *machine-facing*, así que no se reutiliza (aunque sí se evaluó primero, siguiendo la instrucción de
no fijar una nomenclatura nueva si el repositorio ya tenía un helper mejor).

Nombres de partición: `parts/part-{index:06d}.json` (cero-rellenado, ascendente:
`parts/part-000000.json`, `parts/part-000001.json`, ...) — deterministas, y ordenan igual en el sistema de
archivos, en `ls`, y en la lista `manifest["partitions"]`, sin necesidad de parsear JSON primero.

### 3.3 El manifest: contenido mínimo obligatorio

| Campo | Contenido |
|---|---|
| `contract_name` / `contract_version` | `"LegacyMapperConsumerProjection"` / `"1.0"` |
| `source_snapshot` | Igual que `ai_context/SYSTEM_CONTEXT.json.metadata.source_snapshot_sha256` de esta misma ejecución |
| `package_id` | `CPJ-<sha256>`, canónico sobre el cuerpo del manifest (que a su vez incluye el `partition_id` de cada partición — ver sección 3.5: cambia si cambia cualquier partición) |
| `statistics` | Totales globales: `flow_count`, `path_count`, `confirmed_flow_count`/`inferred_flow_count`/`unresolved_flow_count`, `partition_count`, `completeness` |
| `statistics.completeness` | Siempre `"COMPLETE"` — no existe `TRUNCATED`/`BUDGET_INSUFFICIENT` en esta superficie |
| `partitioning` | `strategy: "FIXED_SIZE_BY_FLOW_COUNT"`, `partition_size`, `partition_count`, `directory`, `filename_pattern` |
| `partitions` | Lista determinista (orden ascendente por `index`), un elemento por partición: `index`, `relative_path`, `partition_id`, `flow_count`, `first_flow_id`, `last_flow_id` |
| `provenance` | Igual que antes (modelo de hidratación, índices fuente) |

Esto cubre exactamente los ocho puntos mínimos exigidos por la corrección: `contract_name`/`version`,
`source_snapshot`, un id de proyección estable, estadísticas globales, `completeness=COMPLETE`, el total de
flujos/paths, la estrategia de particionado, y la lista determinista de particiones con su id/hash, `flow_count`
y ruta relativa.

### 3.4 Cada partición es autocontenida

Una partición nunca necesita otra partición, ni el manifest, para interpretar sus propios `records` — lleva
su propio `contract_name`/`contract_version`/`source_snapshot`/`provenance` y los registros hidratados
completos, exactamente igual que la versión sin particionar los llevaba:

| Campo de una partición | Contenido |
|---|---|
| `contract_name` / `contract_version` | Igual que el manifest — la partición pertenece al mismo contrato, no a uno distinto |
| `source_snapshot` | Igual que el manifest (mismo valor, para poder correlacionar sin volver a leerlo) |
| `partition_index` | El mismo índice que su entrada en `manifest["partitions"]` |
| `partition_id` | `CPJ-PART-<sha256>` sobre el cuerpo de esta partición únicamente |
| `scope.flow_ids` | Los `flow_id` exactos que contiene, en el mismo orden que `records` |
| `records` | Los registros hidratados completos (`EvidenceHydrator.hydrate_flow`, sin cambios) |
| `statistics` / `provenance` | Igual forma que antes, ahora acotados a esta partición |

Un consumidor puede leer `CONSUMER_PROJECTION.json`, descubrir las particiones que le interesan, abrir
**solo esas** (nunca todas) y reconstruir flujo → punto de entrada → paths → terminales/evidencia/provenance
sin ninguna clase interna de LegacyMapper y sin abrir ninguna otra partición
(`PartitionSelfContainmentTests`).

### 3.5 Garantía matemática de no pérdida (`SILENT_ENTRY_OMISSION=FORBIDDEN` bajo particionado)

Sea `F` el conjunto de `flow_id` solicitados (todos los de `ix`, o los explícitos) y `P₀, P₁, ..., Pₙ₋₁` las
particiones que `package()` produce. El código impone, y los tests verifican, dos invariantes:

1. **Unión completa**: `P₀.flow_ids ∪ P₁.flow_ids ∪ ... ∪ Pₙ₋₁.flow_ids == F`. Cada `flow_id` de `F` aparece
   en exactamente una partición: el particionado es un corte consecutivo, sin solapamiento, de la lista ya
   ordenada y deduplicada (`sorted(set(flow_ids))` en `build`), así que la unión de los cortes reconstruye
   exactamente la lista original.
2. **Intersección vacía**: `Pᵢ.flow_ids ∩ Pⱼ.flow_ids == ∅` para todo `i ≠ j`, por la misma razón (cortes
   consecutivos de una lista sin solaparse).

Estas dos propiedades se cumplen por construcción (`chunks = [ordered[i:i+size] for i in range(0, len(ordered), size)]`
— una partición de listas de Python nunca solapa ni omite ningún elemento), pero el módulo **no confía
únicamente en la construcción**: `_verify_partitioning_is_lossless` recorre el resultado y falla cerrado
(`ConsumerProjectionError`) si la unión real no coincide exactamente con lo solicitado, o si aparece cualquier
duplicado — el mismo patrón de "guarda explícita para un caso que el código ya hace inalcanzable" que
`PluginProjectionService.project` (R12) ya usa para su propio `silent_entry_omission_detected`. Antes incluso
de llegar a esa guarda, `EvidenceHydrator.hydrate_flow` ya falla con `UnknownFlowError` si se solicita un
`flow_id` que no existe en `ix` (nunca lo omite en silencio), y `_reject_duplicate_flow_ids` falla si dos
registros ya hidratados comparten `flow_id` antes de repartirlos en particiones. Tests:
`test_every_flow_appears_in_the_partitions_union`, `test_no_flow_is_duplicated_across_partitions`,
`test_no_flow_is_silently_omitted`, `test_unknown_flow_id_fails_closed_rather_than_silently_omitting`,
`test_duplicate_records_passed_to_package_are_rejected`.

### 3.6 Independencia y JSON plano (sin cambios respecto de la versión inicial)

- **Independiente de `ai_projection.py`/`human_documentation`/`llm` en código, no solo en dato.**
  `consumer_projection.py` importa únicamente su hermano `.hydration` — verificado por AST
  (`RuntimeIndependenceTests.test_never_imports_ai_projection_human_documentation_or_llm`), exactamente lo que
  R1 §5.3 pide.
- **Registros son JSON plano**, exactamente lo que `EvidenceHydrator.hydrate_flow` devuelve, nunca una clase
  interna de LegacyMapper (`PartitionSelfContainmentTests.test_partition_body_is_plain_json_primitives`).
- Mismo método de cálculo de id que `CTX-`/`AIP-` (SHA-256 canónico sobre el cuerpo serializado), con `CPJ-`
  para el manifest y `CPJ-PART-` para cada partición.

## 4. Materialización: `output/consumer_projection/CONSUMER_PROJECTION.json` + `parts/*.json`

### 4.1 Decisión: extender el stage `CONTEXT` existente, no crear un nuevo `StageId`

`consumer_projection` es determinista y **nunca opt-in** (a diferencia de `AI_INTERPRETATION`/
`PROPOSAL_GENERATION`) — se evaluó seriamente crear un nuevo `StageId.CONSUMER_PROJECTION` propio, pero se
descartó: `legacy_documenter.cli.stage_identity.StageId` es un contrato de trece identidades ya estable
(V4.2-R1 en adelante) del que dependen `execution_model.RunResult`, `run_summary_presenter` y decenas de
aserciones existentes sobre la lista exacta de stages en `RUN_SUMMARY.json`/tests de `full`. Añadir una
identidad nueva para una escritura de archivo que comparte exactamente el mismo límite de fallo que `CONTEXT`
ya tiene (ver el propio docstring de `StageId.EXPORT`: "cubre dos escritores... sin límite de fallo
independiente entre ellos") habría propagado ese cambio de contrato a superficies que no lo necesitan, por
una razón puramente de nomenclatura, no de comportamiento. En su lugar:

`legacy_documenter/cli/pipeline_stages.py::build_context_artifacts` (llamada, sin cambios de firma, tanto por
`analyze` como por `full` — ambos comandos ya comparten esta función, ver el docstring del módulo) ahora
también escribe `output/consumer_projection/CONSUMER_PROJECTION.json`, bajo el mismo límite de fallo
`StageId.CONTEXT` que ya cubre `output/context/*.json` y `output/ai_context/*`:

```python
def build_context_artifacts(output, indexes):
    ContextBuilder().build_project_contexts(output, indexes)
    system_context_artifacts = SystemContextBuilder().build(output, indexes)
    source_snapshot = system_context_artifacts["SYSTEM_CONTEXT.json"]["metadata"]["source_snapshot_sha256"]
    _write_consumer_projection(output, indexes, source_snapshot)
```

`source_snapshot` se toma del mismo valor que `ai_context/SYSTEM_CONTEXT.json` ya expone
(`metadata.source_snapshot_sha256`), sin recalcularlo por separado — un consumidor puede correlacionar ambos
artefactos de la misma ejecución por ese valor compartido
(`PipelineMaterializationTests.test_consumer_projection_carries_the_run_source_snapshot`).

### 4.2 Escritura sanitizada y atómica, para el manifest y para cada partición

`_write_consumer_projection` pasa el manifest **y cada partición, por separado**, por
`legacy_documenter.utils.sanitize_data` antes de serializarlos con `render_deterministic_json` (misma
serialización canónica que el resto de artefactos V4-R7…R12), y escribe el manifest con `atomic_write_text`
(V4.2-R6, temp-sibling + `os.replace`) — el mismo patrón que `AGENTS.md` exige ("Use the centralized
sanitizer for exported evidence") y que V4.2-R6 ya estableció para los artefactos autoritativos de
LegacyMapper.

Las particiones se escriben con `legacy_documenter.cli.artifact_lifecycle
.sync_generated_json_partition_directory(target / "parts", serialized_partitions)` — una función nueva,
hermana de `sync_generated_partition_directory` (V4.2-R8, ya usada para particiones Markdown de
documentación humana), que aplica exactamente la misma política de limpieza segura de particiones obsoletas
("usa el mecanismo seguro existente del proyecto, si aplica") pero para archivos `.json`, escritos con
`atomic_write_text` en vez de `write_text` plano: no se generalizó la función existente porque eso habría
cambiado la primitiva de escritura para sus llamadores Markdown preexistentes y no relacionados
(`markdown_exporter.py`, `pipeline_stages.render_documentation`), que siguen intactos. Una re-ejecución sobre
el mismo `--output` con menos flujos (y por tanto menos particiones) elimina los archivos `part-NNNNNN.json`
que ya no corresponden — el mismo principio de seguridad ante reejecución de V4.2-R6 §5, aplicado aquí a esta
superficie nueva. Test: `RerunStalePartitionCleanupTests.test_rerun_with_fewer_flows_removes_stale_partitions`
(601 flujos → 1 flujo sobre el mismo `--output`, con el `DEFAULT_PARTITION_SIZE=500` real, sin parchear).

### 4.3 Consecuencia de la decisión de la sección 4.1

Ni `AI_INTERPRETATION`, ni `PROPOSAL_GENERATION`, ni ningún nuevo `StageId` está involucrado:
`consumer_projection` se produce siempre, tanto con `--allow-ai-interpretation` como sin él, y tanto en
`analyze` como en `full` (`PipelineMaterializationTests
.test_full_command_also_writes_consumer_projection_without_ai_opt_in`,
`.test_analyze_writes_consumer_projection_json`). Un fallo de `AI_INTERPRETATION` no puede afectarlo: en el
orden de ejecución de `run_full_pipeline`, `CONTEXT` (y por tanto `consumer_projection`) ya se ejecutó y se
resolvió antes de que `AI_INTERPRETATION` siquiera se intente (sección 5).

## 5. Verificación end-to-end de que el fallo de IA no invalida la salida determinista

`AiFailureDoesNotInvalidateDeterministicOutputTests
.test_ai_failure_leaves_documentation_and_consumer_projection_intact`: una corrida real de `run_full_pipeline`
con `--allow-ai-interpretation` y un `FakeLLMProvider(forced_status="PROVIDER_ERROR")` produce:

| Stage | Resultado |
|---|---|
| `DOCUMENTATION` | `SUCCESS` |
| `AI_INTERPRETATION` | `FAILED` |
| `output/documentation/` | existe, completo |
| `output/consumer_projection/CONSUMER_PROJECTION.json` | existe, completo |
| `RunResult.status` | `PARTIAL` (nunca `FAILED`: `EXTRACTION`/`EXPORT` sí tuvieron éxito, ver `_compute_status`) |

Esto es exactamente "fallo AI no invalida documentación determinista" (prompt, sección "IA"), demostrado
conductualmente contra el pipeline real, no solo inferido de la lectura del código en la sección 2.

## 6. Tests

`tests/test_v4_3_r6_ai_and_consumer_projection.py` (**40 tests**, todos en verde — reescrito íntegramente
para la arquitectura manifest+particiones de la corrección; los 23 tests de la implementación inicial fueron
reemplazados por estos 40, no simplemente ampliados, porque el contrato que verifican cambió de forma
(`build` devuelve `(manifest, partitions)`, no un único paquete)):

| Clase de test | Tests | Cubre |
|---|---|---|
| `ManifestContractTests` | 9 | prefijo `CPJ-`, `contract_name`/`version`, `source_snapshot`, completitud/totales, estrategia de particionado declarada, cada entrada con id/`flow_count`/ruta, sin campo `records`, determinismo, `package_id` sensible al contenido |
| `PartitioningLosslessnessTests` | 8 | 0 flujos, 1 flujo, más particiones que `partition_size`, unión completa, sin duplicados, sin omisión, id desconocido falla cerrado, registros duplicados rechazados |
| `DeterministicNamingAndHashingTests` | 4 | nombres cero-rellenados/ascendentes, orden por `flow_id`, `partition_id` estable entre builds, `partition_id` cambia si cambia esa partición |
| `ManifestPointsOnlyAtRealPartitionsTests` | 2 | toda entrada del manifest apunta a una partición real; ninguna partición existe sin entrada en el manifest |
| `PartitionSelfContainmentTests` | 4 | contrato/provenance propios, reconstrucción completa flujo→entry point→paths→terminales, JSON plano, ninguna partición depende de otra |
| `RuntimeIndependenceTests` | 3 | sin import de `ai_projection`/`documentation`/`llm` (AST), sin I/O de archivos, sin reimplementar hidratación |
| `PipelineMaterializationTests` | 3 | `analyze` escribe manifest + particiones, `source_snapshot` compartido manifest↔partición↔`SYSTEM_CONTEXT.json`, `full` también lo escribe sin opt-in de IA |
| `RerunStalePartitionCleanupTests` | 1 | rerun con menos flujos elimina particiones obsoletas (601 → 1 flujo, `DEFAULT_PARTITION_SIZE=500` real) |
| `ManifestStaysSmallAtScaleTests` | 2 | prueba de escala sintética: el manifest permanece pequeño (< 20 KB) y con crecimiento sub-proporcional al pasar de 50 a 2000 flujos; el detalle se distribuye en múltiples particiones, ninguna con más de `partition_size` registros |
| `AiFailureDoesNotInvalidateDeterministicOutputTests` | 1 | fallo real de IA no invalida `DOCUMENTATION` ni `consumer_projection` (sección 5) |
| `AiIntegrationInvariantTests` | 3 | propuestas `READY_FOR_REVIEW`/`AI_PROPOSED` nunca `APPROVED`, findings con referencia desconocida rechazados, `unresolved` preservado en una partición |
| **Total** | **40** | |

Ningún test existente fue debilitado ni modificado (salvo la actualización mecánica del inventario de
mantenibilidad congelado, sección 8). En particular, `tests/test_v4_2_r4_ai_interpretation_and_proposal_integration.py`
(34 tests) y `tests/test_v4_3_r5_ai_context_budgeting.py` (66 tests) siguen en verde **sin cambios**.

## 7. Cobertura de requisitos (uno a uno contra el prompt literal de R6)

| Requisito literal | Dónde | Test(s) |
|---|---|---|
| findings citan evidencia incluida | Ya implementado (V4.2-R4/V4.3-R5); re-verificado end-to-end | `AiIntegrationInvariantTests.test_findings_must_cite_evidence_actually_included_in_the_package` |
| hechos deterministas pueden ser `CONFIRMED` | Ya implementado (V4.3-R2) | `ConsumerProjectionContractTests.test_confidence_is_never_altered_or_invented` |
| síntesis AI = `INTERPRETED` | Ya implementado (V4.2-R4/V4.3-R1 §5.2), sin cambios | (sin test nuevo: cubierto por la suite de R4/R5 existente, no debilitada) |
| unresolved preservado | Ya implementado (V4.3-R2); re-verificado en la superficie nueva | `AiIntegrationInvariantTests.test_unresolved_evidence_is_preserved_in_the_consumer_projection` |
| propuestas = `READY_FOR_REVIEW` | Ya implementado (V4.2-R4); re-verificado end-to-end | `AiIntegrationInvariantTests.test_proposals_are_ready_for_review_and_ai_proposed` |
| fallo AI no invalida documentación determinista | Ya implementado estructuralmente (V4.2-R2/R3/R4); demostrado conductualmente por primera vez en esta ronda | `AiFailureDoesNotInvalidateDeterministicOutputTests.test_ai_failure_leaves_documentation_and_consumer_projection_intact` |
| `consumer_projection`: JSON versionado, autocontenido, razonablemente pequeño, IDs/provenance, sin Plugin Runtime | Sección 3 (particionado determinista y completo); `PLUGIN_RUNTIME_NOT_IMPLEMENTED` sin cambios | `ManifestContractTests` (9), `ManifestStaysSmallAtScaleTests` (2), `PipelineMaterializationTests` (3) |
| **No hacer**: no implementar Plugin Runtime | No se tocó `legacy_documenter/knowledge/plugin_projection/` ni ningún concepto de runtime de plugin | — |

Requisitos del contrato R1 §5.3 (además del prompt):

| Exigencia de R1 §5.3 | Test |
|---|---|
| `SILENT_ENTRY_OMISSION=FORBIDDEN` | `test_unknown_flow_id_fails_closed_rather_than_silently_omitting` |
| Independiente de `human_documentation`, no la importa | `test_never_imports_ai_projection_human_documentation_or_llm` |
| `schema/versión`: `LegacyMapperConsumerProjection 1.0` | `test_package_declares_the_contract_name_and_version` |
| Prefijo `CPJ-<sha256>` | `test_package_id_uses_the_cpj_prefix` |

## 8. Actualización mecánica del inventario de mantenibilidad (V4.1-R0)

Mismo patrón exacto que cada ronda previa (cf. `V4_3_R5_..._RESULT.md` §9.1). Ninguna aserción existente se
debilitó; solo se ajustaron los valores esperados al nuevo módulo y a los cruces de categoría reales causados
por esta ronda, incluyendo su propia corrección de particionado:

| Sección del inventario | Ajuste |
|---|---|
| `production_python_module_count` | 174 → **175** (un módulo nuevo) |
| Conjunto de rutas nuevas | + `context/consumer_projection.py` |
| `risk_summary.high_risk_files` | `cli/pipeline_stages.py` sale (cruce a `VERY_HIGH`, implementación inicial); + `context/consumer_projection.py` entra (cruce a `HIGH`, esta corrección) |
| `risk_summary.very_high_risk_files` | + `cli/pipeline_stages.py` (cruce `HIGH → VERY_HIGH`, sin cambios adicionales por la corrección: ya estaba en `VERY_HIGH` antes de ella) |
| `risk_summary.files_by_risk_category` | `HIGH` neto sin cambio (`pipeline_stages.py` sale, `consumer_projection.py` entra); `VERY_HIGH` +1 (`pipeline_stages.py`); `MEDIUM` sin término nuevo (`consumer_projection.py` nunca pasó por `MEDIUM`: ya entra directamente en `HIGH`) |
| `dependency_findings.module_count` | +31 → **+32** |
| `largest_modules` | + `context/consumer_projection.py` (283 líneas) entra al top-20, empujando además a `legacy_documenter/knowledge/relations/service.py` (no tocado por esta ronda) bajo el corte |
| Fórmula de `dependency_findings` | `consumer_projection.py` importa solo `.hydration` (dirección `context -> context` ya establecida); `pipeline_stages.py` importa además `context.consumer_projection`/`utils.atomic_write`/`utils.json_rendering`/`utils.sanitizer` (direcciones `cli -> context`/`cli -> utils` ya establecidas) — ninguna dirección nueva |

**Cruce de categoría, implementación inicial**: `legacy_documenter/cli/pipeline_stages.py` pasa de `HIGH` a
`VERY_HIGH` (421 → 454 líneas) al añadir la llamada a `_write_consumer_projection` y sus cuatro imports
nuevos. La cuarta señal de `responsibility_signals` que completa el cruce (`provider_or_network`) es un falso
positivo conocido de la heurística de nombres de este mismo módulo de inventario
(`NETWORK_PROVIDER_NAME_HINTS` incluye la subcadena `"llm"`, sin noción de negación): la dispara la propia
frase del docstring de `build_context_artifacts` explicando que, a diferencia de `AI_INTERPRETATION`, esta
escritura "reaches no AI/LLM service" — documentación honesta sobre la ausencia de acceso a IA, no acceso
real. Se documenta aquí como decisión consciente (igual que R5 documentó el cruce equivalente de
`ai_interpretation.py`) en vez de reescribir la documentación del código para evadir la heurística.

**Cruce de categoría, corrección de particionado**: `legacy_documenter/context/consumer_projection.py`
(142 → 283 líneas, el particionado determinista, las guardas de pérdida/duplicación y los helpers de nombre
de archivo) cruza de `MEDIUM` a `HIGH` (gana `filesystem` y `validation` junto a los ya presentes
`provider_or_network`/`serialization`). `filesystem` es el mismo tipo de falso positivo de nombre que el de
`pipeline_stages.py` arriba (el propio docstring del módulo menciona `write_text`/`read_text` al explicar que
el módulo *nunca* los llama); `validation` en cambio es real: el módulo ahora contiene guardas explícitas
`raise ValueError`/`ConsumerProjectionError` (sección 3.5). `pipeline_stages.py` crece de 454 a 473 líneas
(serializa y sincroniza un diccionario de particiones en vez de un único paquete) pero no cruza una segunda
vez de categoría: ya estaba en `VERY_HIGH` desde la implementación inicial.

## 9. Muestra regenerada: `docs/V4_3/samples/R6/`

Regenerada contra el fixture `tests/fixtures/v4_2_r3_sample` (`analyze_repository`, la misma fuente que ya
usan las muestras de R3/R4), reemplazando la muestra de la implementación inicial de esta ronda:

| Archivo | Tamaño | Contenido |
|---|---|---|
| `CONSUMER_PROJECTION.json` | **1309 bytes** | El manifest completo: `package_id`, `partitioning` (`partition_size=500`, `partition_count=1`), la única entrada de `partitions` (con su `partition_id`/`flow_count`/`relative_path`), `statistics` (`flow_count=1`, `path_count=2`, `completeness=COMPLETE`), `source_snapshot`, `provenance` |
| `parts/part-000000.json` | **4187 bytes** | La única partición de este fixture pequeño: un registro FLOW hidratado completo (punto de entrada, paths, terminales, evidencia, provenance) |

Con un único flujo en el fixture, el manifest y la partición son comparables en tamaño (1.3 KB vs. 4.2 KB) —
la ventaja del particionado no es visible a esta escala, es visible en `ManifestStaysSmallAtScaleTests`
(sección 6), que demuestra sintéticamente que el manifest crece muy por debajo de forma proporcional al
número de flujos (50 → 2000 flujos: 40 particiones, manifest todavía por debajo de 20 KB) mientras el detalle
hidratado completo se reparte en tantas particiones de ≤`partition_size` registros como haga falta.

## 10. Fuera de alcance de esta ronda

- No se implementa Plugin Runtime (`PLUGIN_RUNTIME_NOT_IMPLEMENTED` sin cambios).
- No se crea un nuevo `StageId`/identidad de stage (sección 4.1); `consumer_projection` se materializa dentro
  del stage `CONTEXT` existente.
- No se modifica ninguna de las cinco piezas de integración IA/propuestas ya correctas (sección 2): ni
  `ai_interpretation.py`, ni `proposal_adapter.py`, ni `hydration.py`, ni `ai_projection.py`, ni el orden de
  stages de `full_pipeline.py`.
- No se modifica `legacy_documenter/documentation/interpretation.py` — el punto abierto que R5 §10 dejó
  registrado explícitamente para "R6 si el Líder Técnico lo considera necesario" sigue sin instrucción
  explícita de tocarlo en el prompt de R6; se mantiene registrado como pendiente para una ronda futura que lo
  aborde con su propio diseño, no como una extensión implícita de esta.
- No se generaliza `sync_generated_partition_directory` (V4.2-R8): se añadió una función hermana
  (`sync_generated_json_partition_directory`) en vez de modificar la existente, para no cambiar la primitiva
  de escritura de sus llamadores Markdown preexistentes (sección 4.2).
- No se modifica `PROJECT_STATE.json`.
- No se inicia V4.3-R7.
- No se cierra ni versiona V4.3 (sigue correspondiendo exclusivamente a R9).

## 11. Conteos de tests

- **Antes** de esta ronda: **1984 tests, 0 fallos, 0 errores, 132 skips** (ver
  `docs/V4_3/V4_3_R5_AI_CONTEXT_BUDGETING_RESULT.md` §8.1).
- **Tras la implementación inicial de R6**: **2007 tests, 0 fallos, 0 errores, 132 skips** (1984 + 23).
- **Tras la corrección de escalabilidad (particionado)**: los 23 tests iniciales fueron reemplazados por
  **40 tests** que verifican el contrato manifest+particiones (sección 6) → **2024 tests, 0 fallos, 0
  errores, 132 skips** —
  `python -m unittest discover -s tests` → `OK (skipped=132)`.
- `python -m unittest tests.test_v4_3_r6_ai_and_consumer_projection` → **40/40 `OK`**.
- `python -m unittest tests.test_v4_1_r0_maintainability_inventory` → **22/22 `OK`**.
- `python -m unittest tests.test_v4_3_r5_ai_context_budgeting` → **66/66 `OK`** (sin cambios).
- `python -m unittest tests.test_v4_2_r4_ai_interpretation_and_proposal_integration` → **34/34 `OK`** (sin
  cambios).

## 12. Archivos runtime modificados/creados

| Archivo | Tipo de cambio |
|---|---|
| `legacy_documenter/context/consumer_projection.py` | Reescrito para partición determinista (142 → 283 líneas). `build`/`package` ahora devuelven `(manifest, partitions)`; añade `ConsumerProjectionError` por duplicación, `partition_filename`/`partition_relative_path`, y las guardas de la sección 3.5 |
| `legacy_documenter/cli/pipeline_stages.py` | `_write_consumer_projection` ahora escribe el manifest más un diccionario de particiones vía `sync_generated_json_partition_directory` (454 → 473 líneas) |
| `legacy_documenter/cli/artifact_lifecycle.py` | **Nueva función** `sync_generated_json_partition_directory` (hermana de `sync_generated_partition_directory`, V4.2-R8, para particiones `.json` escritas atómicamente) |
| `tests/test_v4_3_r6_ai_and_consumer_projection.py` | Reescrito íntegramente para el contrato manifest+particiones (23 → 40 tests) |
| `tests/test_v4_1_r0_maintainability_inventory.py` | Actualización mecánica del inventario congelado (sección 8) |
| `docs/V4_3/samples/R6/CONSUMER_PROJECTION.json`, `docs/V4_3/samples/R6/parts/part-000000.json` | Muestra regenerada (sección 9) |

No se tocó `legacy_documenter/cli/full_pipeline.py`, `legacy_documenter/cli/stage_identity.py`,
`legacy_documenter/orchestration/ai_interpretation.py`, `legacy_documenter/orchestration/proposal_adapter.py`,
`legacy_documenter/exporters/_documentation_partitioning.py`, ni `PROJECT_STATE.json`.

## 13. Revisión humana obligatoria (pendiente) — Gate para R7

Pendiente de aprobación por el Líder Técnico antes de iniciar R7:

- [ ] este resultado R6 (`docs/V4_3/V4_3_R6_AI_AND_CONSUMER_PROJECTION_RESULT.md`), incluida la corrección de
      escalabilidad;
- [ ] el diagnóstico de la sección 2: que las cinco piezas de integración IA/propuestas ya estaban
      implementadas correctamente antes de esta ronda, y que la única pieza real y faltante era
      `consumer_projection` como JSON real;
- [ ] la arquitectura final manifest + particiones, la estrategia `FIXED_SIZE_BY_FLOW_COUNT`, y la garantía
      matemática de no pérdida (secciones 3.1–3.5);
- [ ] la decisión de extender el stage `CONTEXT` existente en vez de crear un nuevo `StageId`, y su
      justificación frente al contrato de trece identidades ya estable (sección 4.1);
- [ ] la función nueva `sync_generated_json_partition_directory` y la decisión de no generalizar la existente
      (sección 4.2);
- [ ] la verificación end-to-end de que un fallo real de IA no invalida `DOCUMENTATION` ni
      `consumer_projection` (sección 5);
- [ ] los dos cruces de categoría de mantenibilidad (`pipeline_stages.py` HIGH→VERY_HIGH,
      `consumer_projection.py` MEDIUM→HIGH) y sus falsos positivos de heurística documentados (sección 8);
- [ ] la muestra regenerada bajo `docs/V4_3/samples/R6/` (sección 9);
- [ ] los conteos de tests: **2024 tests, 0 fallos, 0 errores, 132 skips** (sección 11);
- [ ] el punto abierto heredado de R5 sobre `documentation/interpretation.py`, aún sin abordar (sección 10).
