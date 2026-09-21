# V4.3 — R7 — Aceptación interna y paquete para piloto real — Resultado

## Estado de esta ronda

`V4_3_READY_FOR_EXTERNAL_REAL_PILOT`. Como R1–R6, esta ronda implementa código de producción (dos hallazgos
reales, sección 3) además de herramientas/documentación de empaquetado. El `Gate` de rondas previas sigue
quedando satisfecho por la misma vía que R2→…→R7: la instrucción directa del Líder Técnico de ejecutar la
ronda (`ejecuta V4_3_R7_INTERNAL_ACCEPTANCE.md`). Esta ronda **no cierra ni versiona V4.3** (sigue
correspondiendo exclusivamente a R9), **no modifica `PROJECT_STATE.json`**, y **no accede al repositorio
IST real** (`AGENTS.md` "Legacy Source Repository") ni a `C:\PruebasLegacyMapper` (que, per el prompt de esta
ronda, "no existen en el repo de desarrollo y no son dependencia").

**Corrección posterior a la redacción inicial de esta ronda** (misma ronda R7, antes de autorizar el piloto):
la revisión del Líder Técnico encontró dos bloqueos de aceptación reales en el estado inicial de R7, y una
revisión adicional sobre esa misma corrección encontró un tercer punto de consistencia de producto
(`RUN_SUMMARY.md`, sección 10.3) — ver sección 10 para el detalle completo de los tres y de su corrección.
Solo después de esa corrección `PRODUCT/RUNTIME` puede declararse `READY` (sección 4.1); el estado de esta
ronda arriba ya refleja el estado corregido.

`REAL_AI_RUNTIME_CALL_ALLOWED=false` sigue vigente: ningún test de esta ronda alcanza un proveedor real; todos
inyectan `FakeLLMProvider` explícitamente.

## 1. Objetivo

`prompts/V4_3/V4_3_R7_INTERNAL_ACCEPTANCE.md`: validar internamente LegacyMapper V4.3 (R0–R6) y preparar su
empaquetado para un piloto externo real, sin incorporar datos reales al repositorio de desarrollo.

## 2. Método: aceptación interna real, no solo documental

Antes de escribir cualquier documento de aceptación, se ejecutó la suite completa y se corrió `full` de
extremo a extremo contra el fixture comprometido `tests/fixtures/v4_2_r3_sample` — dos veces: una vez dentro
de este repositorio de desarrollo, y una segunda vez **desde una copia de distribución limpia recién
construida**, para que "aceptación interna" describa un comportamiento verificado, no una lista de
afirmaciones. Esa segunda ejecución encontró dos defectos reales (sección 3), que se corrigieron antes de
declarar la ronda lista, en vez de documentarlos como pendientes.

## 3. Hallazgos reales encontrados y corregidos durante esta verificación

### 3.1 `compute_output_locations` nunca listaba `consumer_projection`

V4.3-R6 conectó `consumer_projection` al stage `CONTEXT` (`build_context_artifacts`), que escribe
`consumer_projection/CONSUMER_PROJECTION.json` + `parts/*.json` siempre que `CONTEXT` tiene éxito — exactamente
la misma condición bajo la que `ai_context/` se reporta. `legacy_documenter/cli/run_summary_presenter
.compute_output_locations` (V4.2-R5/R6) no se actualizó en ese momento: `RUN_SUMMARY.json`, `RUN_SUMMARY.md` y
el resumen de consola de **todo run `full`** desde R6 reportaban `ai_context` pero nunca `consumer_projection`,
aunque el directorio existiera físicamente en disco. Un operador de piloto externo leyendo únicamente el
resumen (la superficie que V4.2-R5 diseñó exactamente para ese propósito) nunca se habría enterado de que esa
superficie existe.

**Corrección** (`legacy_documenter/cli/run_summary_presenter.py`, una línea): `compute_output_locations` ahora
añade `"consumer_projection"` junto a `"ai_context"` bajo la misma condición (`CONTEXT` exitoso). Ninguna otra
lógica de la función cambia. Test:
`OutputLocationsIncludeConsumerProjectionTests.test_output_locations_lists_consumer_projection_when_context_succeeds`,
`.test_console_summary_mentions_consumer_projection_location`.

### 3.2 La documentación humana en español (V4.3-R3/R4) nunca estaba conectada a `full`/`analyze`

Verificación directa: `legacy_documenter/documentation/human_flow_documentation.py`/`human_documentation_scaling.py`
(diseñados e implementados en R3/R4, con muestras en `docs/V4_3/samples/R3/`, `R4/`) nunca aparecían
referenciados desde `legacy_documenter/cli/`. Al correr `full` contra el fixture comprometido, `documentation/`
no contenía ningún documento en español — solo los documentos técnicos preexistentes de V4.2, en inglés. Esto
no era un descuido silencioso: R4 lo documentó explícitamente como una decisión deliberada, diferida a una
ronda posterior ("esa decisión de wiring... corresponde a una ronda posterior", `V4_3_R4_..._RESULT.md`
sección 9) — pero el prompt de esta ronda (`V4_3_R7_INTERNAL_ACCEPTANCE.md`, obligatorio 5: "documentación
humana y consumer projection en fixtures") exige que ambas superficies existan juntas en un fixture real antes
de declarar el paquete listo para piloto, lo cual hizo que esta fuera exactamente la ronda posterior a la que
R4 se refería.

**Corrección, siguiendo los tres puntos que R4 dejó explícitamente pendientes de decidir**:

| Punto pendiente (R4 sección 9) | Decisión de esta ronda |
|---|---|
| Nombre de archivo final bajo `documentation/` | `HUMAN_DOCUMENTATION.md` — el nombre que `render_human_documentation_partitions` ya codificaba como enlace relativo (`../HUMAN_DOCUMENTATION.md`) desde R4, nunca cambiado |
| Orden de ejecución respecto de `render_documentation` | Dentro del mismo `render_documentation` (stage `DOCUMENTATION`), después de los cuatro renderizadores existentes — mismo límite de fallo, mismo stage, sin nuevo `StageId` |
| Política de fallo parcial | Idéntica a los otros cuatro: `try`/`except` propio; un fallo aquí se registra en `outcome.failures` y no impide que `WEB_ENTRY_POINTS.md`/`FUNCTIONAL_FLOWS.md`/etc. se escriban |

Implementación (`legacy_documenter/cli/pipeline_stages.py::render_documentation`): hidrata cada flujo de
`indexes["functional_flows"]` con `EvidenceHydrator` (V4.3-R2, sin reimplementar), llama a
`render_human_documentation_index`/`render_human_documentation_partitions` (V4.3-R3/R4, sin modificar), y
escribe `documentation/HUMAN_DOCUMENTATION.md` + `documentation/flujos_humanos/*.md` vía
`sync_generated_partition_directory` (V4.2-R8, el mismo mecanismo de particiones Markdown ya usado por los
otros cuatro documentos). `interpretations_by_flow` se omite deliberadamente: este stage sigue siendo
puramente determinista, igual que los otros cuatro — no se genera ni se requiere ningún contenido de IA aquí.
`analyze` sigue sin llamar a `render_documentation` en absoluto (sin cambios desde V4.2-R3), así que no gana
esta salida.

Tests: `HumanDocumentationWiringTests` (5), incluyendo
`test_full_command_produces_human_documentation_and_consumer_projection_together` (la verificación literal del
obligatorio 5) y `test_human_documentation_failure_does_not_prevent_other_documents` (la política de fallo
parcial, verificada inyectando un fallo real).

### 3.3 Por qué estos dos hallazgos no invalidan R3–R6

Ninguno de los dos es un defecto en la lógica ya implementada y probada de R2–R6: `hydration.py`,
`human_flow_documentation.py`, `human_documentation_scaling.py`, `ai_projection.py`, `consumer_projection.py`
y `ai_interpretation.py` no cambiaron su comportamiento interno en esta ronda (salvo la extensión aditiva de
`compute_output_locations`, que no toca ninguno de esos módulos). Ambos son huecos de **integración/reporting**
exactamente del tipo que una ronda de "aceptación interna" existe para encontrar antes de un piloto externo,
no defectos de diseño de las rondas que los dejaron pendientes deliberadamente.

## 4. Readiness: DEV/GOVERNANCE vs. PRODUCT/RUNTIME

El prompt exige separar explícitamente estos dos ejes — no son el mismo tipo de "listo".

### 4.1 PRODUCT/RUNTIME — `READY`

Lo que importa para un operador de piloto externo: ¿la herramienta funciona, de forma standalone, contra un
repositorio real?

| Criterio | Estado | Evidencia |
|---|---|---|
| Suite completa | `2057 tests, 0 fallos, 0 errores, 132 skips` | sección 6 |
| `full` funcional dentro del repo de desarrollo | Verificado | `PilotDistributionTests`, `HumanDocumentationWiringTests` |
| `full` funcional **fuera** del repo de desarrollo (distribución limpia) | Verificado, de extremo a extremo, vía subproceso real (`python main.py full ... `) | `test_clean_distribution_runs_full_standalone_against_a_fixture` |
| `analyze`/`full` sin dependencias de terceros | Verificado (AST de todo `legacy_documenter/**/*.py`): solo librería estándar + `copilot` opcional, importado perezosamente solo dentro de `CopilotProvider._generate` | sección 5 |
| Salida determinista completa: `index/`, `documentation/` (técnica, **en español por defecto** desde la corrección BLOQUEO 2 — sección 10.2 — + `HUMAN_DOCUMENTATION.md` en español), `ai_context/`, `consumer_projection/` (particionado) | Verificada junta en un mismo run real | `test_full_command_produces_human_documentation_and_consumer_projection_together`, `SpanishByDefaultProductDocumentationTests` |
| `RUN_SUMMARY.md` **en español por defecto**, `RUN_SUMMARY.json` sin cambios | Corregido y verificado (BLOQUEO 2, parte 2 — sección 10.3) | `RunSummaryMarkdownSpanishByDefaultTests` |
| `output-manifest` generable **desde la distribución limpia**, sin volver al repo de desarrollo | Corregido y verificado (BLOQUEO 1 — sección 10.1) | `test_clean_distribution_builds_output_manifest_via_its_own_cli_subcommand` |
| `--allow-ai-interpretation` opt-in, nunca por defecto | Sin cambios desde V4.2-R4; re-verificado | `tests/test_v4_2_r4_...` (34, sin cambios) |
| Fallo de IA no invalida salida determinista (documentación técnica, humana, `consumer_projection`) | Verificado con un `FakeLLMProvider(forced_status="PROVIDER_ERROR")` real | `AiFailureStillDoesNotAffectHumanDocumentationTests`, `V4_3_R6_..._RESULT.md` sección 5 |
| Seguridad de reejecución (particiones/propuestas obsoletas no sobreviven) | Sin cambios desde V4.2-R6/V4.3-R6; re-verificado | suite existente, sin cambios |
| Contrato de exit code (`SUCCESS_0_PARTIAL_1_USAGE_2_FAILED_4`) | Sin cambios desde V4.2-R5.1 | — |
| Manifest de outputs para auditoría de reproducibilidad | Nuevo, verificado, y ahora disponible desde runtime (sección 10.1) | sección 5.2, sección 10.1 |
| Distribución limpia ejecutable de forma standalone | Nueva, verificada | sección 5.1 |

No hay ningún elemento `PRODUCT/RUNTIME` bloqueante **tras la corrección de sección 10**. El único límite
conocido y explícito: **ningún run de V4.3 se ha ejecutado todavía contra el repositorio legacy real**
(`IST_40/operacional`) — deliberadamente, porque esta ronda es "aceptación interna", no el piloto en sí; el
piloto externo es precisamente el paso siguiente que valida esto contra escala/forma reales
(`docs/V4_3/V4_3_REAL_PILOT_INSTRUCTIONS.md`).

### 4.2 DEV/GOVERNANCE — `READY_FOR_PILOT_PENDING_FORMAL_CLOSURE`

Lo que importa para el proceso/gobernanza del proyecto, distinto de si la herramienta funciona:

| Criterio | Estado |
|---|---|
| Revisión humana de cada ronda R0–R7 | Satisfecha por instrucción directa del Líder Técnico en cada ronda (mismo patrón que V4.1/V4.2); revisión humana *formal* de esta ronda sigue pendiente (sección 9, checklist) |
| `PROJECT_STATE.json` | **No actualizado por ninguna ronda de V4.3** (R1–R7 lo declaran explícitamente fuera de alcance) — sigue reportando `current_version: "V4.2"`. Esto es deliberado, no un olvido: la actualización de estado formal corresponde a R9 (cierre/versionado), no a rondas intermedias |
| Documento de resultado por ronda | R0–R7 lo tienen, incluyendo correcciones posteriores documentadas explícitamente cuando ocurrieron (R5 §8.1, R6 particionado) |
| Punto abierto heredado | `legacy_documenter/documentation/interpretation.py` (el camino de IA V3-era, distinto de `ai_interpretation.py`) sigue sin wiring decidido — registrado en R5 §10 y R6 §10, todavía no requerido explícitamente por ningún prompt; permanece abierto para una ronda futura |
| Cierre/versionado de V4.3 | No corresponde a esta ronda (R9 exclusivamente) |

Ninguno de estos puntos bloquea el piloto externo: el piloto no requiere que V4.3 esté formalmente cerrado ni
que `PROJECT_STATE.json` refleje V4.3 todavía — solo requiere que la herramienta funcione (`PRODUCT/RUNTIME`,
ya `READY`) y que existan instrucciones seguras para ejecutarlo (sección 7).

## 5. Empaquetado para piloto externo

### 5.1 Distribución limpia: `tools/v4_3_r7_build_pilot_distribution.py`

Copia únicamente `main.py` + `legacy_documenter/` (excluyendo `__pycache__`/`*.pyc`) a un destino — nunca
`docs/`, `prompts/`, `tests/`, `codex/`, `output/`, `result_codex/`, `tools/`, `README.md`, `AGENTS.md`,
`CLAUDE.md`, `PROJECT_STATE.json`, ni nada bajo `.git`. Verificación de que esto es seguro, no solo una
suposición: un escaneo AST de cada import de todo `legacy_documenter/**/*.py` (sección 4.1) confirma que el
paquete es autocontenido — únicamente librería estándar más `copilot`, importado perezosamente solo dentro de
`CopilotProvider._generate` (nunca durante el análisis determinista). La lista de entradas a copiar es una
**allowlist** fija (`RUNTIME_ROOT_ENTRIES`), no un blocklist: un archivo nuevo, no-runtime, añadido a la raíz
del repositorio en una ronda futura nunca se filtra a una distribución de piloto sin una decisión explícita de
añadirlo aquí.

Verificación real, no solo por inspección de rutas:

```
python -m tools.v4_3_r7_build_pilot_distribution <destino>
cd <destino>
python main.py full <repositorio_legacy> --output <output>
```

ejecutado exactamente así (vía `subprocess`, working directory = la distribución copiada, ningún archivo del
repositorio de desarrollo en el `PYTHONPATH` ni en el directorio de trabajo) produjo `exit code 0`,
`RUN_SUMMARY.json` con `"status": "SUCCESS"`, y tanto `documentation/HUMAN_DOCUMENTATION.md` como
`consumer_projection/CONSUMER_PROJECTION.json` presentes. Test:
`PilotDistributionTests.test_clean_distribution_runs_full_standalone_against_a_fixture`.

Rechaza copiar a un destino no vacío (`FileExistsError`) — nunca mezcla una distribución nueva con contenido
de una anterior o de otro origen.

### 5.2 Manifest de outputs: `legacy_documenter/cli/output_manifest.py` + `tools/v4_3_r7_build_output_manifest.py`

`build_output_manifest(output_dir)` enumera, de forma determinista (ordenado por ruta relativa, nunca por
orden de enumeración del sistema de archivos), cada archivo bajo un `--output` ya producido: ruta, tamaño en
bytes, y SHA-256. Deliberadamente **no** se conectó automáticamente dentro de `run_full_pipeline`: el
contrato de stages (`StageId`, `RunResult`) ya es estable y está ampliamente probado desde V4.2-R1; en su
lugar es un paso posterior explícito y opcional (`python -m tools.v4_3_r7_build_output_manifest <dir>`), para
que un operador de piloto (o el Líder Técnico) pueda verificar exactamente qué produjo una ejecución y
detectar cualquier modificación posterior, sin tener que re-ejecutar LegacyMapper ni comparar directorios a
mano. Tests: `OutputManifestTests` (6), incluyendo determinismo y cobertura de `HUMAN_DOCUMENTATION.md` +
`CONSUMER_PROJECTION.json` juntos sobre un run real.

## 6. Tests

`tests/test_v4_3_r7_internal_acceptance.py` (**33 tests**, todos en verde — 20 de la redacción inicial de esta
ronda, 7 de la corrección de sección 10.1/10.2, y 6 de la corrección de sección 10.3):

| Clase de test | Tests | Cubre |
|---|---|---|
| `HumanDocumentationWiringTests` | 5 | escritura de índice/particiones, enlace índice↔partición, `full` produce ambas superficies juntas, `analyze` no las gana, política de fallo parcial |
| `OutputLocationsIncludeConsumerProjectionTests` | 2 | `consumer_projection` en `output_locations` y en el resumen de consola (hallazgo 3.1) |
| `OutputManifestTests` | 6 | fallo cerrado ante directorio ausente, tamaño/hash por archivo, orden/rutas deterministas, exclusión del propio manifest, determinismo, cobertura sobre un run real |
| `PilotDistributionTests` | 7 | solo `main.py`+`legacy_documenter`, exclusión de directorios de desarrollo, exclusión de `__pycache__`, rechazo de destino no vacío, lista de archivos copiados, ejecución `full` standalone real, **+1: `output-manifest` generado vía subproceso real desde la distribución limpia (BLOQUEO 1, sección 10.1)** |
| `OutputManifestCliSubcommandTests` | 3 | **BLOQUEO 1**: el parser acepta `output-manifest`, el router lo enruta y escribe el manifest, `FileNotFoundError` se propaga para un directorio ausente |
| `SpanishByDefaultProductDocumentationTests` | 3 | **BLOQUEO 2 (parte 1)**: los once documentos obligatorios son español por defecto sobre un run `full` real; identificadores/status nunca se traducen; los renderers planos en inglés siguen sin ser parte de la salida de `full` |
| `RunSummaryMarkdownSpanishByDefaultTests` | 6 | **Nueva (BLOQUEO 2, parte 2 — sección 10.3)**: `RUN_SUMMARY.md` es español por defecto sobre un run `full` real; `StageId`/status/error nunca se traducen; `RUN_SUMMARY.json` estructuralmente sin cambios; `SUCCESS`/`FAILED` correctos en ambas superficies; `consumer_projection` presente en `output_locations` en ambas superficies |
| `AiFailureStillDoesNotAffectHumanDocumentationTests` | 1 | fallo real de IA no invalida `HUMAN_DOCUMENTATION.md` |
| **Total** | **33** | |

Además, varios tests preexistentes se actualizaron para reflejar el nuevo estado real, no debilitados:
`test_v4_2_r3_deterministic_technical_documentation.py::test_render_documentation_never_raises_for_a_single_renderer_failure`
(`outcome.written` pasa de 4 a 5 documentos: `HUMAN_DOCUMENTATION.md` se suma), las dos pruebas de
independencia de runtime que verificaban que `hydration`/`human_documentation_scaling` **no** estaban
conectadas al CLI (`test_v4_3_r2_evidence_hydration.py`, `test_v4_3_r4_scaling_and_partitioning.py`) — ahora
verifican que la conexión está **confinada** a `pipeline_stages.py` (nunca a `full_pipeline.py`/`main.py`
directamente) —, las aserciones de texto en inglés sobre los renderers de navegación/partición ahora
traducidos (corrección de sección 10.2, `tests/test_v4_2_r8_documentation_at_scale.py`,
`tests/test_v4_2_r7_synthetic_full_fixture.py`), y (corrección de sección 10.3)
`RunSummaryMarkdownReadabilityTests.test_run_summary_md_is_human_readable_and_does_not_duplicate_documentation`
(`tests/test_v4_2_r5_unified_cli_and_operational_ux.py`) — todas actualizadas a las cadenas en español
equivalentes, nunca debilitadas ni eliminadas, solo traducidas junto con el renderer que verifican.

**Conteos**: antes de esta ronda, `2024 tests, 0 fallos, 0 errores, 132 skips`
(`docs/V4_3/V4_3_R6_AI_AND_CONSUMER_PROJECTION_RESULT.md` §11). Tras la redacción inicial de esta ronda: `2044
tests`. Tras la corrección de sección 10.1/10.2 (BLOQUEO 1 y 2, parte 1): `2051 tests`. Tras la corrección de
sección 10.3 (BLOQUEO 2, parte 2 — `RUN_SUMMARY.md`): **`2057 tests, 0 fallos, 0 errores, 132 skips`**
(2051 + 6 nuevos) — `python -m unittest discover -s tests` → `OK (skipped=132)`.
`python -m unittest tests.test_v4_3_r7_internal_acceptance` → **33/33 `OK`**.
`python -m unittest tests.test_v4_1_r0_maintainability_inventory` → **22/22 `OK`** (inventario congelado, sin
más ajustes necesarios por esta corrección — `run_summary_presenter.py` ya estaba en `touched_paths` desde
V4.2-R5/R6).

## 7. Actualización mecánica del inventario de mantenibilidad (V4.1-R0)

Mismo patrón exacto que cada ronda previa. Ninguna aserción existente se debilitó; solo se ajustaron los
valores esperados a los cambios reales de esta ronda:

| Sección del inventario | Ajuste |
|---|---|
| `production_python_module_count` | 175 → **176** (`cli/output_manifest.py`, nuevo, LOW) |
| `risk_summary.files_by_risk_category` | `LOW` +1 (`output_manifest.py`); tras la corrección de sección 10.1, `router.py` cruza de `MEDIUM` a `HIGH` (el nuevo subcomando `output-manifest` añade una cuarta rama de despacho más su propia función auxiliar de escritura de manifest) |
| `dependency_findings.module_count` | +32 → **+33** |
| Fórmula de `dependency_findings` | `output_manifest.py` no importa nada interno; `pipeline_stages.py` gana `context.hydration` (dirección `cli -> context` ya establecida) y, por primera vez, `documentation.human_documentation_scaling` (nueva dirección `cli -> documentation`, acíclica: `documentation` nunca importa nada de `cli`) |
| `side_effect_candidates.filesystem_access` | + `cli/output_manifest.py` (+10 → +11); tras la corrección de sección 10.1, + `cli/router.py` (+11 → +12: `_route_output_manifest` importa `Path` y llama a `atomic_write_text` directamente) |
| `documentation_candidates` (docstring por debajo del promedio) | Tras la corrección de sección 10.2, `llm/providers/copilot.py` sale de esta lista (su propio `_prompt` ahora documenta su delegación a `render_request_payload`, V4.3-R5) y `exporters/technical_documentation_renderer.py` entra (su cobertura de docstrings se diluye por las nuevas funciones auxiliares `*_es` de renderizado en español, cada una ya documentada, pero el conteo de funciones del archivo creció más rápido que su conteo de docstrings) |

Cruce de categoría de riesgo en la redacción inicial de esta ronda: ninguno (`consumer_projection.py`
permanece `HIGH`, `pipeline_stages.py` permanece `VERY_HIGH`, ambos ya cruzados en R6). La corrección de
sección 10.1 sí produce un cruce nuevo: `router.py` de `MEDIUM` a `HIGH` (ver arriba).

## 8. Fuera de alcance de esta ronda

- No se accede al repositorio legacy real (`IST_40/operacional`) ni a `C:\PruebasLegacyMapper`.
- No se implementa Plugin Runtime.
- No se cambia nada de `AI_INTERPRETATION`/`PROPOSAL_GENERATION` (`ai_interpretation.py`,
  `proposal_adapter.py`): ambos permanecen exactamente como R4/R5/R6 los dejaron.
- No se modifica `legacy_documenter/documentation/interpretation.py` (punto abierto heredado, sección 4.2).
- No se conecta `build_output_manifest` automáticamente dentro de `run_full_pipeline` (sección 5.2) —
  deliberadamente un paso posterior opcional, no un nuevo stage.
- No se modifica `PROJECT_STATE.json`.
- No se inicia V4.3-R8.
- No se cierra ni versiona V4.3 (sigue correspondiendo exclusivamente a R9).

## 9. Archivos runtime modificados/creados

| Archivo | Tipo de cambio |
|---|---|
| `legacy_documenter/cli/run_summary_presenter.py` | `compute_output_locations` añade `"consumer_projection"` (hallazgo 3.1) |
| `legacy_documenter/cli/pipeline_stages.py` | `render_documentation` ahora también escribe `HUMAN_DOCUMENTATION.md` + `flujos_humanos/` (hallazgo 3.2) |
| `legacy_documenter/cli/output_manifest.py` | **Nuevo** (62 líneas). Manifest determinista de un árbol de salida |
| `tools/v4_3_r7_build_pilot_distribution.py` | **Nuevo**. Constructor de distribución limpia |
| `tools/v4_3_r7_build_output_manifest.py` | **Nuevo**. Envoltorio de CLI sobre `output_manifest.py` (conveniencia de repo de desarrollo; ver sección 10.1 para la vía runtime) |
| `legacy_documenter/cli/parser.py` | **Corrección sección 10.1**: nuevo subcomando `output-manifest` (`COMMANDS`, subparser, ayuda) |
| `legacy_documenter/cli/router.py` | **Corrección sección 10.1**: nueva ruta `_route_output_manifest` |
| `legacy_documenter/main.py` | **Corrección sección 10.1**: imprime el mensaje de resultado de `output-manifest`, igual que `readiness` |
| `legacy_documenter/exporters/markdown_exporter.py` | **Corrección sección 10.2**: `project_overview`/`solution_structure`/`webforms_map`/`configuration_summary`/`analysis_warnings` renderizan en español |
| `legacy_documenter/exporters/technical_documentation_renderer.py` | **Corrección sección 10.2**: `functional_flows_navigation`/`_partitions`, `database_access_navigation`/`_partitions`, `unresolved_findings_navigation`/`_partitions`, `documentation_readme` renderizan en español (nuevas funciones/constantes auxiliares `*_es`, sin tocar los renderers planos en inglés) |
| `legacy_documenter/cli/run_summary_presenter.py` | **Corrección sección 10.3**: `render_markdown_summary` renderiza `RUN_SUMMARY.md` en español; nueva función `_derive_next_action_es`. `RUN_SUMMARY.json`/`render_run_result`/`derive_next_action`/`render_console_summary` sin cambios |
| `tests/test_v4_3_r7_internal_acceptance.py` | **33 tests** (20 de la redacción inicial + 7 de la corrección de sección 10.1/10.2 + 6 de la corrección de sección 10.3) |
| `tests/test_v4_2_r3_deterministic_technical_documentation.py` | Conteo de `outcome.written` actualizado (4 → 5) |
| `tests/test_v4_3_r2_evidence_hydration.py`, `tests/test_v4_3_r4_scaling_and_partitioning.py` | Tests de independencia de runtime actualizados para reflejar el wiring confinado a `pipeline_stages.py` |
| `tests/test_v4_2_r8_documentation_at_scale.py`, `tests/test_v4_2_r7_synthetic_full_fixture.py` | **Corrección sección 10.2**: aserciones de texto en inglés sobre los renderers ahora traducidos, actualizadas a español |
| `tests/test_v4_2_r5_unified_cli_and_operational_ux.py` | **Corrección sección 10.3**: `RunSummaryMarkdownReadabilityTests` actualizado a los encabezados/oración de próxima acción en español |
| `tests/test_v4_1_r0_maintainability_inventory.py` | Actualización mecánica del inventario congelado (sección 7); sin ajustes adicionales por la corrección de sección 10.3 (`run_summary_presenter.py` ya estaba en `touched_paths` desde V4.2-R5/R6) |
| `docs/V4_3/V4_3_REAL_PILOT_INSTRUCTIONS.md` | **Corrección sección 10.1/10.2/10.3**: `output-manifest` documentado como subcomando runtime; documentación técnica y `RUN_SUMMARY.md` documentados como español por defecto |

No se tocó `legacy_documenter/cli/full_pipeline.py`, `legacy_documenter/cli/stage_identity.py`,
`legacy_documenter/cli/serialization.py` (`render_run_result`/`RUN_SUMMARY.json`), `legacy_documenter/orchestration/`,
`legacy_documenter/context/hydration.py`, `legacy_documenter/context/ai_projection.py`,
`legacy_documenter/context/consumer_projection.py`, `legacy_documenter/documentation/human_flow_documentation.py`,
`legacy_documenter/documentation/human_documentation_scaling.py`, ni `PROJECT_STATE.json`.

## 10. Corrección de bloqueos de aceptación (Líder Técnico, misma ronda R7)

La revisión del Líder Técnico sobre el estado inicial de esta ronda encontró dos bloqueos de aceptación reales
antes de autorizar el piloto externo. Ambos se corrigen aquí, dentro de la misma ronda R7 (no se abre R7.1 ni
se avanza a R8): el patrón ya establecido por V4.2-R7.1/R4.3-R4/R5/R6 de corregir hallazgos reales de
verificación dentro de la ronda que los encuentra.

### 10.1 BLOQUEO 1 — `output-manifest` no estaba disponible dentro de la distribución limpia

**Defecto**: `V4_3_REAL_PILOT_INSTRUCTIONS.md` (redacción inicial de esta ronda) instruía al operador del
piloto a generar la distribución limpia (solo `main.py` + `legacy_documenter/`, sección 5.1 — `tools/`
explícitamente excluido) y luego, dentro de esa misma distribución, ejecutar
`python -m tools.v4_3_r7_build_output_manifest`. Ese script vive bajo `tools/`, que la distribución limpia
nunca copia — el comando instruido simplemente no habría funcionado dentro del entorno que las mismas
instrucciones acababan de construir.

**Corrección**: `build_output_manifest` (`legacy_documenter/cli/output_manifest.py`, sin cambios) ahora se
expone también como un subcomando runtime de `legacy_documenter.cli`:

```
python main.py output-manifest <directorio de salida>
```

- `legacy_documenter/cli/parser.py`: `COMMANDS` gana `"output-manifest"`; nuevo subparser con un único
  argumento posicional (`output_dir`).
- `legacy_documenter/cli/router.py`: nueva ruta `_route_output_manifest`, que llama a
  `build_output_manifest` y escribe `OUTPUT_MANIFEST.json` de forma atómica (`atomic_write_text` +
  `render_deterministic_json`), exactamente como ya lo hacía `tools/v4_3_r7_build_output_manifest.py`. Un
  `FileNotFoundError` (directorio ausente/no válido) se propaga sin capturar — territorio de uso incorrecto
  de la CLI, no un fallo de pipeline, igual que otros errores de uso de `analyze`/`full`.
- `legacy_documenter/main.py`: imprime el mensaje de resultado para `output-manifest`, igual que ya hacía
  para `readiness`.

Como esta ruta vive dentro de `legacy_documenter/`, viaja con la distribución limpia sin ningún cambio a
`tools/v4_3_r7_build_pilot_distribution.py` ni a su `RUNTIME_ROOT_ENTRIES`. `tools/v4_3_r7_build_output_manifest.py`
se mantiene, sin cambios, como una conveniencia equivalente para quien trabaja directamente dentro del
repositorio de desarrollo — ambas vías llaman exactamente a la misma función determinista, nunca duplicada.

**Verificación real, no solo por inspección**: `PilotDistributionTests
.test_clean_distribution_builds_output_manifest_via_its_own_cli_subcommand` construye la distribución limpia,
ejecuta `python main.py full ...` y luego `python main.py output-manifest ...` — ambos vía `subprocess` real,
directorio de trabajo = la distribución copiada, ningún archivo del repositorio de desarrollo en el
`PYTHONPATH` ni en el directorio de trabajo — y confirma `OUTPUT_MANIFEST.json` producido, cubriendo
`documentation/HUMAN_DOCUMENTATION.md` y `consumer_projection/CONSUMER_PROJECTION.json`. Adicionalmente,
`OutputManifestCliSubcommandTests` (3 tests) verifica el parser/router a nivel de unidad. `docs/V4_3/
V4_3_REAL_PILOT_INSTRUCTIONS.md` sección 4.1 se corrigió para instruir `python main.py output-manifest` en
lugar del comando `tools/` original.

### 10.2 BLOQUEO 2 (parte 1: documentación técnica) — la documentación técnica de producto seguía en inglés heredado de V4.2

**Defecto**: R7 declaraba `PRODUCT/RUNTIME: READY` pero, de los once documentos human-readable/product-facing
que `full` genera activamente, solo `HUMAN_DOCUMENTATION.md` (V4.3-R3/R4/R7) y `PROJECT_DEPENDENCIES.md`/
`WEB_ENTRY_POINTS.md` (corrección V4.3-R4 sección 12/13, ya aplicada antes de esta corrección) eran español
por defecto. `PROJECT_OVERVIEW.md`, `SOLUTION_STRUCTURE.md`, `WEBFORMS_MAP.md`, `CONFIGURATION_SUMMARY.md`,
`FUNCTIONAL_FLOWS.md`, `DATABASE_ACCESS.md`, `UNRESOLVED_FINDINGS.md`, `ANALYSIS_WARNINGS.md`, y el
`README.md` de `documentation/` seguían en inglés, heredado sin revisar de V4.2.

**Clasificación** (obligatoria por el prompt de corrección):

| Documento | Clasificación | Disposición |
|---|---|---|
| `PROJECT_OVERVIEW.md`, `SOLUTION_STRUCTURE.md`, `PROJECT_DEPENDENCIES.md`, `WEBFORMS_MAP.md`, `WEB_ENTRY_POINTS.md`, `FUNCTIONAL_FLOWS.md`, `DATABASE_ACCESS.md`, `UNRESOLVED_FINDINGS.md`, `CONFIGURATION_SUMMARY.md`, `ANALYSIS_WARNINGS.md`, `README.md` de `documentation/` | human-readable / product-facing | **Corregidos a español por defecto en esta sección** |
| `HUMAN_DOCUMENTATION.md` + `flujos_humanos/*.md` | human-readable / product-facing | Ya español desde V4.3-R3/R4/R7 — sin cambios aquí |
| `index/*.json`, `ai_context/*.json`, `consumer_projection/*.json`, `RUN_SUMMARY.json`, `OUTPUT_MANIFEST.json` | machine-readable | No requieren traducción — contratos JSON con claves/valores estables, nunca prosa |
| `RUN_SUMMARY.md` | human-readable / product-facing | **Corregido a español por defecto — ver sección 10.3 (seguimiento de esta misma corrección, tras revisión adicional del Líder Técnico)** |

Dentro de cada documento corregido: identificadores (nombres de clase/método/proyecto/WebForm), paths,
comandos, nombres de tipos (`Project*`, `stored_procedure`, etc.), campos JSON (`appSettings`,
`codebehind`, `total_files`, etc.) y valores de status (`confirmed`/`unresolved`) se preservan exactos,
nunca traducidos — solo la prosa/encabezados/etiquetas circundantes.

**Corrección**:

- `legacy_documenter/exporters/markdown_exporter.py`: `project_overview`, `solution_structure`,
  `webforms_map`, `configuration_summary`, `analysis_warnings` (los cinco métodos que `MarkdownExporter.export`
  escribe directamente) ahora renderizan en español. Ninguno de los cinco estaba particionado ni R4 lo
  reabrió para partición (documentos pequeños a escala real); se tradujeron en el lugar, sin cambiar su
  estructura.
- `legacy_documenter/exporters/technical_documentation_renderer.py`: `functional_flows_navigation`/
  `_partitions`, `database_access_navigation`/`_partitions`, `unresolved_findings_navigation`/`_partitions`
  y `documentation_readme` (los únicos métodos de este renderer que `render_documentation`/`full` realmente
  escriben a disco — ver `_PARTITIONED_DOCUMENTATION_RENDERERS` en `pipeline_stages.py`) ahora renderizan en
  español, siguiendo exactamente el mismo patrón que `web_entry_points_navigation`/`_partitions` ya
  establecieron en la redacción inicial de esta ronda. Los renderers planos correspondientes
  (`functional_flows`, `database_access`, `unresolved_findings`, `web_entry_points`, y
  `MarkdownExporter.project_dependencies`) permanecen sin cambios, en inglés: ninguno es parte de la salida
  de `full`/`analyze` (confirmado por `SpanishByDefaultProductDocumentationTests
  .test_flat_english_renderers_are_not_part_of_full_output`); se conservan únicamente para llamadores
  directos de test/API en inglés preexistentes que quieren un documento completo sin particionar.

**Verificación real, no solo sobre renderers aislados**: `SpanishByDefaultProductDocumentationTests` corre
`run_full_pipeline` sobre el fixture comprometido y lee los once documentos generados directamente desde
disco (`test_full_run_writes_every_mandatory_document_in_spanish`), confirma que identificadores/valores de
status sobreviven intactos (`test_technical_identifiers_are_never_translated`), y confirma que los renderers
planos en inglés no son alcanzados por `full` (`test_flat_english_renderers_are_not_part_of_full_output`).

### 10.3 BLOQUEO 2 (parte 2, seguimiento) — `RUN_SUMMARY.md` seguía en inglés

**Defecto**: la corrección de sección 10.2 clasificó `RUN_SUMMARY.md` como "mixto" (navegación humana mínima
sobre un contrato en gran parte enumerado/estructural) y lo dejó explícitamente fuera de alcance, en inglés.
Revisión adicional del Líder Técnico sobre esa misma decisión encontró que esa clasificación era incorrecta:
`RUN_SUMMARY.md` lo genera el producto, está diseñado para lectura humana (headers/etiquetas de prosa, no solo
una tabla de valores), y `V4_3_REAL_PILOT_INSTRUCTIONS.md` sección 5 instruye explícitamente al operador del
piloto a consultarlo para diagnosticar un run `PARTIAL`/`FAILED` — exactamente el tipo de documento
human-readable/product-facing que la regla V4.3 (español por defecto, identificadores técnicos preservados)
ya cubre. La exclusión de sección 10.2 no era una decisión de alcance sostenible; era el mismo defecto de
herencia-sin-revisar-de-V4.2 que sección 10.2 ya corrigió para los otros once documentos, simplemente no
detectado en esa primera pasada porque el documento parecía "mixto" en lugar de puramente de prosa.

**Corrección**: `legacy_documenter/cli/run_summary_presenter.py::render_markdown_summary` ahora renderiza
`RUN_SUMMARY.md` en español: título, etiquetas de la lista de estado (`Comando`/`Estado`/`IA solicitada`/etc.),
encabezados de sección (`## Etapas`, `## Ubicaciones de salida`, `## Próxima acción`) y una nueva función
`_derive_next_action_es` (que refleja exactamente la misma lógica de decisión que `derive_next_action`, nunca
una segunda regla mantenida por separado — solo el idioma de la oración renderizada difiere) para la oración
de próxima acción. Se preservan exactos, nunca traducidos: los valores de `StageId` (`stage.stage.value`, p.
ej. `SCAN`/`EXPORT`/`FINAL_SUMMARY`), los valores de `RunStatus`/`StageStatus` (p. ej. `SUCCESS`/`PARTIAL`/
`FAILED`), `stage.error.category`/`stage.error.message` (nombre de clase de excepción/mensaje real, siempre
técnico), cada path/nombre de archivo en `output_locations`, y `result.command`.

**`RUN_SUMMARY.json` permanece completamente sin cambios**: `render_run_result`/el contrato de campos de
`RUN_SUMMARY.json` no se tocan. En particular, `result.next_action` — el campo que `RUN_SUMMARY.json` y el
resumen de consola (`render_console_summary`) leen — sigue siendo exactamente el que `derive_next_action`
(sin cambios) produce, en inglés; `_derive_next_action_es` es una función nueva, separada, que
`render_markdown_summary` llama únicamente para su propia sección `## Próxima acción` en el archivo `.md` —
nunca sustituye ni recalcula `result.next_action` en sí. El resumen de consola (`render_console_summary`) no
se modificó en esta corrección: no se le añadió prosa humana nueva, por lo que el punto 4 de la instrucción de
corrección ("cualquier prosa humana nueva o equivalente debe ser español por defecto si corresponde") no
aplica retroactivamente a texto de consola preexistente y sin cambios.

**Verificación real, no solo sobre el renderer en aislamiento**: `RunSummaryMarkdownSpanishByDefaultTests`
(6 tests, nueva) corre `run_full_pipeline` sobre el fixture comprometido y lee `RUN_SUMMARY.md`/
`RUN_SUMMARY.json` directamente desde disco: prosa/encabezados en español
(`test_run_summary_md_has_spanish_prose_and_headers`), `StageId`/status nunca traducidos
(`test_stage_ids_and_statuses_are_never_translated`), `category`/`message` de error preservados verbatim vía
un fallo real inyectado (`test_error_category_and_message_are_preserved_verbatim`), el contrato de
`RUN_SUMMARY.json` estructuralmente igual y con `next_action` en inglés (`test_run_summary_json_is_structurally_unchanged`),
`SUCCESS`/`FAILED` representados correctamente en ambas superficies con un fallo real inyectado
(`test_success_partial_failed_still_render_correctly_in_markdown_and_json`), y `consumer_projection` presente
en `output_locations` tanto en `RUN_SUMMARY.md` como en `RUN_SUMMARY.json`
(`test_output_locations_still_include_consumer_projection_in_both_surfaces`). Además, el test preexistente
`RunSummaryMarkdownReadabilityTests.test_run_summary_md_is_human_readable_and_does_not_duplicate_documentation`
(`tests/test_v4_2_r5_unified_cli_and_operational_ux.py`) se actualizó para verificar los encabezados en
español y la oración de próxima acción en español, nunca debilitado.

## 11. Revisión humana obligatoria (pendiente) — Gate para R8 (si aplica) / piloto externo

Pendiente de aprobación por el Líder Técnico antes de considerar el piloto externo formalmente autorizado:

- [ ] este resultado R7 (`docs/V4_3/V4_3_R7_INTERNAL_ACCEPTANCE_RESULT.md`);
- [ ] los dos hallazgos reales encontrados y corregidos durante la verificación (sección 3): `consumer_projection`
      ausente de `output_locations`, y la documentación humana en español nunca conectada a `full`/`analyze`;
- [ ] la decisión de wiring de `HUMAN_DOCUMENTATION.md` (nombre de archivo, orden de ejecución, política de
      fallo parcial) que R4 dejó explícitamente pendiente (sección 3.2);
- [ ] la separación de readiness `PRODUCT/RUNTIME` (`READY`) vs. `DEV/GOVERNANCE`
      (`READY_FOR_PILOT_PENDING_FORMAL_CLOSURE`), y que ninguno de los puntos de gobernanza abiertos bloquea
      el piloto (sección 4);
- [ ] la distribución limpia y su verificación de ejecución `full` standalone real (sección 5.1);
- [ ] el manifest de outputs y la decisión de mantenerlo como paso posterior opcional, no un nuevo stage
      (sección 5.2);
- [ ] `docs/V4_3/V4_3_REAL_PILOT_INSTRUCTIONS.md` (entregable obligatorio, documento separado);
- [ ] los conteos de tests: **2057 tests, 0 fallos, 0 errores, 132 skips** (sección 6);
- [ ] el punto abierto heredado sobre `documentation/interpretation.py`, aún sin abordar (sección 4.2);
- [ ] la corrección de los dos bloqueos de aceptación encontrados en la revisión del Líder Técnico sobre el
      estado inicial de esta ronda (sección 10): `output-manifest` expuesto como subcomando runtime
      (BLOQUEO 1, sección 10.1), y documentación técnica de producto en español por defecto (BLOQUEO 2,
      sección 10.2), incluyendo la clasificación human-readable/product-facing vs. machine-readable de la
      tabla en 10.2;
- [ ] la corrección de seguimiento de sección 10.3: `RUN_SUMMARY.md` reclasificado como human-readable/
      product-facing (ya no "mixto") y corregido a español por defecto, preservando `StageId`/status/error/
      paths exactos y sin alterar en absoluto el contrato de `RUN_SUMMARY.json`.

`PRODUCT/RUNTIME` solo puede quedar `READY` (sección 4.1) una vez resueltos los tres puntos de la corrección
de sección 10 (BLOQUEO 1, BLOQUEO 2 parte 1, BLOQUEO 2 parte 2/sección 10.3) — ya lo están, y esta sección de
revisión humana cubre esa corrección explícitamente en sus dos últimos puntos.
