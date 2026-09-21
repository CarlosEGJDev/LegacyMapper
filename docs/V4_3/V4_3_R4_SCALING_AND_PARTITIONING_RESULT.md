# V4.3 — R4 — Escalabilidad y particionado documental — Resultado

## Estado de esta ronda

`V4_3_R4_RESULT_IMPLEMENTED_PENDING_HUMAN_REVIEW`. Como R2/R3, esta ronda implementa código de producción:
`legacy_documenter/documentation/human_documentation_scaling.py` y sus tests. El `Gate` de R3 ("Pendiente de
aprobación por el Líder Técnico antes de iniciar R4") queda satisfecho por la misma vía que R0→R1→R2→R3: la
instrucción directa de ejecutar R4 (`ejecuta V4.3-R4 tal como la define
prompts/V4_3/V4_3_R4_SCALING_AND_PARTITIONING.md`). Esta ronda no cierra ni versiona V4.3 (sigue
correspondiendo exclusivamente a R9) y no modifica `PROJECT_STATE.json`.

**Corrección posterior 1 (instrucción directa del Líder Técnico, aplicada sobre esta misma ronda, ver sección
12)**: la clave de agrupación de `flow_group_key` (defecto: usaba `projects`/`project_sequence`, el orden de
traversal del grafo, en vez de evidencia real de propiedad del WebForm) fue corregida, y `WEB_ENTRY_POINTS.md`/
`PROJECT_DEPENDENCIES.md` fueron reabiertos para el mismo particionado navegación/detalle que R4 introdujo para
`human_documentation`. `WEBFORMS_MAP.md` permanece sin particionar. La sección 12 es autoritativa sobre el
estado final donde difiera de las secciones 1-11.

**Corrección posterior 2 (instrucción directa del Líder Técnico, aplicada sobre esta misma ronda, ver sección
13)**: los documentos de navegación/partición de `WEB_ENTRY_POINTS.md`/`web_entry_points/*.md` y
`PROJECT_DEPENDENCIES.md`/`project_dependencies/*.md` introducidos por la corrección 1 (en inglés en esa
versión) fueron traducidos al español por defecto -- el mismo requisito global que `human_documentation` ya
cumplía desde R3 -- preservando intactos nombres de WebForms/handlers/controles/IDs/rutas/proyectos y sin
tocar la estructura de particionado (mismos grupos, rutas, nombres de archivo, conteos, evidencia y enlaces).
La sección 13 es autoritativa sobre el estado final donde difiera de las secciones 1-12.

## 1. Objetivo

Evitar documentos humanos monolíticos manteniendo evidencia exhaustiva (`prompts/V4_3/V4_3_R4_SCALING_AND_PARTITIONING.md`),
reutilizando el patrón navegación/detalle ya validado por V4.2-R8
(`legacy_documenter/exporters/technical_documentation_renderer.py`: `functional_flows_navigation`/
`functional_flows_partitions`, `database_access_navigation`/`database_access_partitions`) para la superficie
que R3 dejó explícitamente fuera de alcance: documentación humana a escala de sistema completo (muchos flujos),
no solo un `FLOW` hidratado individual
(`docs/V4_3/V4_3_R3_HUMAN_DOCUMENTATION_RESULT.md` sección 8: "R4 — 'Scaling and Partitioning' — es el que
aborda agregación/escalado a nivel de sistema completo").

## 2. Qué se implementó

- **`legacy_documenter/documentation/human_documentation_scaling.py`** (nuevo, 239 líneas): capa de agregación
  pura sobre una lista de registros `FLOW` hidratados (la forma exacta que produce
  `EvidenceHydrator.hydrate_flow`, V4.3-R2). Expone:
  - `render_human_documentation_index(hydrated_flows) -> str`: documento de navegación/resumen top-level, en
    español, con una tabla por grupo (proyecto) y sus contadores.
  - `render_human_documentation_partitions(hydrated_flows, interpretations_by_flow=None) -> dict[str, str]`:
    un documento de detalle por grupo, cada uno la concatenación completa de `render_flow_document` (R3, sin
    modificar) para cada flujo del grupo.
  - `flow_group_key(record) -> str`: la clave de agrupación (primer proyecto conocido del flujo, o
    `"unassigned"`), expuesta para que un futuro llamador pueda reutilizarla sin reimplementarla.
- **`tests/test_v4_3_r4_scaling_and_partitioning.py`** (nuevo, 27 tests).
- **`tests/test_v4_1_r0_maintainability_inventory.py`** (modificado): actualización mecánica del inventario de
  mantenibilidad congelado (V4.1-R0) para reflejar el nuevo módulo de producción — ver sección 6.

`human_documentation_scaling.py` no reescribe `render_flow_document` (R3): lo importa y lo llama una vez por
flujo, exactamente como el prompt indica ("R4 no la reescribe, la usa/agrega"). No lee ni escribe ningún
archivo, no llama a ningún proveedor de IA, y no está conectado a `legacy_documenter/cli/` ni a
`legacy_documenter/main.py` — misma postura de independencia de runtime que R2/R3 (ver sección 8 para la
justificación explícita de esta decisión).

## 3. Cobertura de requisitos (uno a uno contra el prompt literal)

| Requisito del prompt | Implementación |
|---|---|
| Índice/resumen top-level | `render_human_documentation_index`: título, conteos totales (flujos, con terminal confirmado, con límite no resuelto), tabla "Grupos de flujos" con un enlace por grupo. Nunca repite las siete secciones de detalle de un flujo (`test_index_never_repeats_full_flow_detail`) |
| Detalle particionado | `render_human_documentation_partitions`: un documento por grupo (proyecto), cada uno con el `render_flow_document` completo (siete secciones + límites) de cada flujo del grupo, sin resumir ni recortar contenido |
| Enlaces relativos | El índice enlaza `flujos_humanos/<safe-name>.md` (relativo, `PARTITIONS_SUBDIR` = `"flujos_humanos"`); cada partición enlaza de vuelta `../HUMAN_DOCUMENTATION.md`. `test_index_links_point_at_the_partitions_subdir_and_match_actual_filenames` verifica que cada enlace del índice corresponde exactamente a un nombre de archivo realmente producido |
| Nombres estables | Reutiliza sin modificar `legacy_documenter.exporters._documentation_partitioning.sanitize_label`/`build_partition_filenames` (V4.2-R8) — nunca un sanitizador reinventado; `test_partition_filenames_are_produced_via_the_shared_partitioning_helper_not_reinvented` |
| Política de tamaño | Declarada explícitamente, no implementada como lógica condicional nueva: navegación + particiones se generan de forma incondicional para cualquier lista no vacía de flujos hidratados, sin umbral de cantidad — la misma política ya vigente para `FUNCTIONAL_FLOWS.md`/`DATABASE_ACCESS.md`/`UNRESOLVED_FINDINGS.md` desde V4.2-R8 (`legacy_documenter/cli/pipeline_stages.py` línea ~361, `_PARTITIONED_DOCUMENTATION_RENDERERS`, invocación sin umbral). El texto de la política aparece literalmente en el propio documento de índice generado (sección "Política de tamaño") y se verifica en `test_index_declares_an_explicit_unconditional_size_policy` |
| Machine projection intacta | Ninguna función muta el/los registro(s) hidratado(s) que recibe; `MachineProjectionIntactTests` (2 tests) verifica igualdad profunda antes/después de cada función. Ningún campo de `AI_HYDRATED_PROJECTION 1.0` se renombra, elimina ni reinterpreta — este módulo solo arregla documentos ya renderizados en grupos |
| Conteos y trazabilidad preservados | `test_every_input_flow_is_preserved_exactly_once_across_all_partitions` verifica que cada flujo de entrada aparece exactamente una vez en el conjunto de particiones (ni perdido ni duplicado); el índice muestra el total exacto de flujos de entrada (`test_index_counts_match_input_totals`); cada partición conserva íntegra la sección 7 de trazabilidad de R3 (`path_id`, `evidence_refs`, `source_index_pointer`, `flow_source_index_pointer`) para cada flujo, sin modificarla |

## 4. Tests obligatorios — mapeo

| Categoría | Test(s) |
|---|---|
| Clave de agrupación (proyecto / `unassigned`) | `FlowGroupKeyTests` (3 tests) |
| Índice: idioma, secciones, no repetición de detalle | `test_index_is_in_spanish_and_lists_every_group`, `test_index_never_repeats_full_flow_detail` |
| Política de tamaño declarada explícitamente | `test_index_declares_an_explicit_unconditional_size_policy` |
| Conteos del índice | `test_index_counts_match_input_totals` |
| Enlaces relativos válidos | `test_index_links_point_at_the_partitions_subdir_and_match_actual_filenames`, `test_partition_links_back_to_the_top_level_index_with_a_relative_link` |
| Lista vacía sin error | `test_index_over_empty_flow_list_declares_no_flows_without_error`, `test_empty_flow_list_produces_no_partitions` |
| Determinismo (incluida independencia del orden de entrada) | `test_index_is_deterministic_regardless_of_input_order`, `test_partition_flow_order_within_a_group_is_stable_and_sorted`, `DeterminismTests` (2 tests) |
| Agrupación por proyecto / grupo `unassigned` | `test_partitions_group_flows_by_project_and_unassigned_flows_get_their_own_partition` |
| Nombres estables vía helper compartido | `test_partition_filenames_are_produced_via_the_shared_partitioning_helper_not_reinvented`, `SanitizeLabelReuseTests` (2 tests) |
| Detalle particionado completo | `test_partition_contains_full_seven_section_detail_for_each_flow_in_its_group` |
| Conteos/trazabilidad preservados sin pérdida ni duplicación | `test_every_input_flow_is_preserved_exactly_once_across_all_partitions` |
| `interpretations_by_flow` pasa a través por flujo, sin fabricar contenido | `test_interpretations_are_passed_through_per_flow_only`, `test_no_interpretations_argument_means_no_interpreted_section_anywhere` |
| Machine projection intacta (sin mutación) | `MachineProjectionIntactTests` (2 tests) |
| Independencia de runtime (mismo patrón que R2/R3) | `RuntimeIndependenceTests` (3 tests) |

## 5. Casos reales de aceptación externa (R0 §5) frente a las muestras generadas

Las tres muestras bajo `docs/V4_3/samples/R4/` (sección 7) reutilizan tres de los cuatro flujos de ejemplo de
R0/R3, ahora agregados en un solo sistema de tres flujos y dos grupos, para mostrar el particionado en
funcionamiento:

| Caso | Flujo | Grupo | Partición |
|---|---|---|---|
| B (procesamiento/carga, terminal confirmado) | `cobCargaArcIntRea.ascx` → `Click` → `btnCargar_Click` | `DAL` | `flujos_humanos/DAL.md` |
| C (escritura/transacción) | `cobChqInsRen.ascx` → `Click` → `HypGuardar_Click` | `DAL` | `flujos_humanos/DAL.md` (mismo grupo que B, dos flujos en un documento) |
| D (sin terminal confirmado) | `CobConsultaTransferencia.ascx` → `Load` → `Page_Load` | `webCobMorosidad` | `flujos_humanos/webCobMorosidad.md` |

El caso A (múltiples terminales) ya está cubierto por la cobertura de R3 dentro de `render_flow_document`
(sección 3 de cada documento de detalle describe un camino por grupo hidratado); esta ronda no cambia esa
lógica, solo agrega los documentos resultantes.

## 6. Archivos runtime modificados

| Archivo | Tipo de cambio |
|---|---|
| `legacy_documenter/documentation/human_documentation_scaling.py` | Nuevo módulo de producción |
| `tests/test_v4_3_r4_scaling_and_partitioning.py` | Nuevo archivo de tests (27 tests) |
| `tests/test_v4_1_r0_maintainability_inventory.py` | Actualización mecánica del inventario congelado V4.1-R0: `production_python_module_count` 172 (171+1); el nuevo módulo entra en `HIGH` (239 líneas, bajo `legacy_documenter/documentation/`, mismo patrón heurístico que ya clasifica `human_flow_documentation.py` como `HIGH`); entra en `largest_modules`, desplazando `legacy_documenter/knowledge/plugin_projection/models.py` del top-20; `dependency_findings.module_count` +29 (antes +28); `risk_summary["HIGH"]` +1. Ninguna aserción se debilitó ni se eliminó; mismo patrón incremental que cada ronda previa |

Ningún archivo bajo `legacy_documenter/cli/`, `legacy_documenter/main.py`, `legacy_documenter/llm/`, ni
`PROJECT_STATE.json` fue modificado. `legacy_documenter/exporters/technical_documentation_renderer.py`
tampoco fue modificado (ver sección 8).

## 7. Muestras Markdown generadas

Tres documentos generados con `render_human_documentation_index`/`render_human_documentation_partitions`, a
partir de un fixture equivalente al de los tests (tres flujos, dos grupos), guardados bajo
`docs/V4_3/samples/R4/` (no son artefactos de producto; ilustran el resultado de esta ronda para revisión
humana):

| Archivo | Contenido ilustrado |
|---|---|
| `documentacion_humana_indice.md` | Índice top-level: 3 flujos hidratados, 2 grupos (`DAL`, `webCobMorosidad`), tabla de conteos, enlaces relativos, y la declaración explícita de política de tamaño |
| `flujos_humanos/DAL.md` | Partición del grupo `DAL`: dos flujos completos (casos B y C de R0), cada uno con sus siete secciones íntegras, enlace de vuelta al índice |
| `flujos_humanos/webCobMorosidad.md` | Partición del grupo `webCobMorosidad`: un flujo sin terminal confirmado (caso D de R0), incertidumbre declarada explícitamente |

## 8. Decisión sobre WEB_ENTRY_POINTS/PROJECT_DEPENDENCIES/WEBFORMS_MAP ("Revisar")

El prompt de esta ronda pide **revisar** estos tres documentos como candidatos a particionado, no
necesariamente reescribirlos. Evidencia empírica real ya registrada (no fabricada en esta ronda), de
`docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md` (piloto real IST):

| Documento | Escala real observada (V4.2-R7) | Clasificación V4.2-R7 |
|---|---|---|
| `WEB_ENTRY_POINTS.md` | 25.595 líneas / 1,2MB, ~2.580 secciones | `PARTIALLY_USEFUL` — "correct, well-formatted per-WebForm tables ... but no index/navigation/filtering" |
| `PROJECT_DEPENDENCIES.md` | 9.424 líneas / 978KB | `PARTIALLY_USEFUL` — "useful as a grep-able reference, not something a human reads start to finish" |
| `WEBFORMS_MAP.md` | 13.944 líneas / 1,37MB | `PARTIALLY_USEFUL` — defecto de presentación distinto (repr crudo de Python en `register`, F-03, ya corregido en V4.2-R7.1), no ausencia de navegación |

Contraste directo: `FUNCTIONAL_FLOWS.md` (396.178 líneas / 44MB) fue clasificado `NOT_USEFUL` a la misma
escala real y sí recibió partición navegación/detalle en V4.2-R8. Los tres documentos de esta sección son
sustancialmente más pequeños y quedaron clasificados `PARTIALLY_USEFUL`, no `NOT_USEFUL` — un grado de
severidad distinto, ya evaluado y ya decidido por el Líder Técnico: `PROJECT_STATE.json` (`documentation_remaining_scale_debt`)
marca explícitamente `WEB_ENTRY_POINTS.md` y `PROJECT_DEPENDENCIES.md` como `OPEN_IF_FUTURE_SCALE_REQUIRES`
(no `REQUIRED`); `WEBFORMS_MAP.md` no está en esa lista en absoluto, porque su defecto identificado (F-03) era
de presentación, no de escala/navegación, y ya se corrigió por separado.

**Decisión de esta ronda**: no se reescribe ni particiona ninguno de los tres. Razones:

1. No existe evidencia empírica nueva en V4.3 (R0 §2, hallazgos EEE-01..EEE-08) que reclasifique estos tres
   documentos por encima de su clasificación V4.2-R7 ya vigente; introducir partición para ellos ahora sería
   fabricar una necesidad de escala no evidenciada, prohibido explícitamente por `AGENTS.md` ("Do not fabricate
   relationships") y por la instrucción de esta ronda.
2. La superficie que R0/R1/R3 sí identificaron con evidencia empírica directa (EEE-04, EEE-06, EEE-08) y que
   R3 explícitamente diseñó para R4 es `human_documentation` a escala de sistema — esa es la entrega central de
   esta ronda (secciones 1-7).
3. Los tres documentos son generados por
   `legacy_documenter/exporters/technical_documentation_renderer.py` (802 líneas, marcado
   `HIGH_RISK_FUTURE_EXTRACTION_CANDIDATE` en `PROJECT_STATE.json.maintainability_debt`), que R3 §8 ya dejó
   explícitamente sin tocar por ser un cambio de mayor riesgo no requerido por el prompt de esa ronda; el mismo
   razonamiento aplica aquí, con más fuerza porque la propia clasificación V4.2-R7 (`PARTIALLY_USEFUL`, no
   `NOT_USEFUL`) no exige el cambio.
4. `PROJECT_STATE.json` no se modifica en esta ronda (regla dura del prompt de ejecución); el marcador
   `OPEN_IF_FUTURE_SCALE_REQUIRES` para `WEB_ENTRY_POINTS.md`/`PROJECT_DEPENDENCIES.md` sigue siendo la
   decisión vigente y correcta tras esta revisión — "future scale" no ha llegado dentro del alcance de V4.3.

Esta decisión queda documentada explícitamente aquí, como exige la instrucción de esta ronda, en vez de forzar
un cambio no requerido. Si una ronda futura (post-V4.3, o V5) encuentra evidencia empírica que sí cruce el
umbral `NOT_USEFUL`/impráctico para alguno de los tres, el mecanismo a reutilizar sería idéntico al de esta
sección: `sanitize_label`/`build_partition_filenames` más un `*_navigation()`/`*_partitions()` por documento,
exactamente como ya lo hizo V4.2-R8 y como lo hace esta ronda para `human_documentation`.

## 9. Fuera de alcance de esta ronda

- No se modifica `render_flow_document` (R3) — se reutiliza sin cambios.
- No se modifica `exporters/technical_documentation_renderer.py` ni ninguno de sus documentos existentes
  (`WEB_ENTRY_POINTS.md`, `FUNCTIONAL_FLOWS.md`, `DATABASE_ACCESS.md`, `UNRESOLVED_FINDINGS.md`,
  `PROJECT_DEPENDENCIES.md`, `WEBFORMS_MAP.md`) — ver sección 8 para la decisión explícita sobre los tres
  últimos.
- No se conecta `render_human_documentation_index`/`render_human_documentation_partitions` a
  `legacy_documenter/cli/`/`main.py` ni a ningún flujo de ejecución automático. Decisión deliberada, misma
  postura que R2/R3: el prompt de esta ronda pide diseñar/implementar el mecanismo de escalado y particionado,
  no decidir en qué punto del pipeline `full`/`analyze` se invoca (esa decisión de wiring, junto con la ruta de
  archivo top-level real bajo `documentation/`, corresponde a una ronda posterior que además tendría que
  decidir el nombre final de archivo, el orden de ejecución respecto de `render_documentation`, y la política
  de fallo parcial — ninguna de las cuales está definida ni pedida por el prompt de R4). Las rutas usadas en
  este resultado (`HUMAN_DOCUMENTATION.md` a nivel de `documentation/`, subdirectorio `flujos_humanos/`) son
  conceptuales/ilustrativas para las muestras y los enlaces relativos generados, no una ruta de escritura a
  disco implementada en esta ronda.
- No se implementa ningún mecanismo nuevo de interpretación de IA: `interpretations_by_flow` es un simple paso
  directo (pass-through) por flujo hacia el parámetro `interpretations` que R3 ya definió y validó
  (`InvalidInterpretationError`); esta ronda no genera ninguna interpretación por sí misma.
- No se modifica `PROJECT_STATE.json`.
- No se cierra ni versiona V4.3 (sigue correspondiendo exclusivamente a R9).
- No se inicia R5.

## 10. Conteos de tests

- Antes de esta ronda (tras R3, incluidas sus dos correcciones): 1862 tests, 0 fallos, 132 skips.
- Después de esta ronda: **1889 tests** (1862 + 27 nuevos de `test_v4_3_r4_scaling_and_partitioning.py`),
  **0 fallos**, **132 skips** (sin cambio).
- `python -m unittest discover -s tests` → `OK (skipped=132)`.
- El módulo dedicado (`python -m unittest tests.test_v4_3_r4_scaling_and_partitioning`) → 27/27 `OK`.
- El módulo de inventario de mantenibilidad actualizado
  (`python -m unittest tests.test_v4_1_r0_maintainability_inventory`) → 22/22 `OK`.

`PROJECT_STATE.json` no se modificó; sus campos `tests`/`test_failures`/`test_errors`/`expected_fresh_clone_skips`
siguen describiendo el baseline de V4.2, no este conteo post-R4. Actualizar esos campos, si corresponde, queda
para R9.

## 11. Revisión humana obligatoria (pendiente) — Gate para R5

Pendiente de aprobación por el Líder Técnico antes de iniciar R5:

- [ ] este resultado R4 (`docs/V4_3/V4_3_R4_SCALING_AND_PARTITIONING_RESULT.md`);
- [ ] `legacy_documenter/documentation/human_documentation_scaling.py` y su reutilización sin modificación de
      `render_flow_document` (R3) y de `sanitize_label`/`build_partition_filenames` (V4.2-R8) (secciones 2-3);
- [ ] la política de tamaño declarada explícitamente (generación incondicional, sin umbral nuevo), en vez de
      lógica condicional inventada (sección 3, fila "Política de tamaño");
- [ ] la decisión original, con evidencia empírica citada, de no particionar `WEB_ENTRY_POINTS.md`/
      `PROJECT_DEPENDENCIES.md`/`WEBFORMS_MAP.md` en esta ronda (sección 8) — **superada por la corrección de la
      sección 12** para `WEB_ENTRY_POINTS.md`/`PROJECT_DEPENDENCIES.md`; la decisión sobre `WEBFORMS_MAP.md` se
      mantiene y queda reafirmada en la sección 12;
- [ ] la decisión de no conectar el nuevo módulo (`human_documentation_scaling.py`) a
      `legacy_documenter/cli/`/`main.py` (sección 9) — no afectada por la corrección;
- [ ] las tres muestras Markdown generadas bajo `docs/V4_3/samples/R4/` (sección 7) — **regeneradas con la
      agrupación corregida, ver sección 12**;
- [ ] los archivos runtime modificados (sección 6), en particular la actualización mecánica del inventario de
      mantenibilidad V4.1-R0 — **ampliada por la corrección de la sección 12**;
- [ ] los conteos de tests finales (sección 10: 1889 tests) — **superados por el conteo final post-corrección de
      la sección 12: 1912 tests, 0 fallos, 132 skips**.

## 12. Corrección: clave de agrupación real y particionado de WEB_ENTRY_POINTS/PROJECT_DEPENDENCIES

Instrucción directa del Líder Técnico, aplicada como corrección puntual y acotada sobre esta misma ronda R4
(no inicia V4.3-R5, no modifica `PROJECT_STATE.json`, no implementa AI budgeting). Mismo estilo que
`docs/V4_3/V4_3_R3_HUMAN_DOCUMENTATION_RESULT.md` secciones 10/12: las secciones 1-11 anteriores se conservan
como registro histórico de la implementación original; esta sección es **autoritativa sobre el estado final**
donde entra en conflicto con ellas.

### 12.1 Defecto 1 — clave de agrupación de HUMAN_DOCUMENTATION

`flow_group_key(record)` usaba `record["projects"][0]` (equivalente a `project_sequence[0]`): el primer
proyecto/capa que el *traversal* del grafo de resolución alcanzó, no una propiedad del WebForm que origina el
flujo. Para un flujo cuyo WebForm invoca directamente una clase de acceso a datos, `project_sequence[0]` es a
menudo la capa `DAL`, no la carpeta real del WebForm.

Evidencia concreta observada en la sección 5 original (tabla de casos B/C/D): `cobCargaArcIntRea.ascx` y
`cobChqInsRen.ascx`, ambos bajo `webCobMorosidad\`, quedaban agrupados como `DAL` (porque sus cadenas de
resolución alcanzaban primero la capa `DAL`), mientras que `CobConsultaTransferencia.ascx` — bajo la misma
carpeta real — quedaba en un grupo `webCobMorosidad` separado. Los tres deberían estar en el mismo grupo.

**Corrección**: `flow_group_key` deriva la clave exclusivamente de `record["entry_point"]["webform"]` (evidencia
directa ya presente en el registro hidratado), nunca de `projects`/`project_sequence`, vía la función
compartida `webform_owner_group_key` (nueva, `legacy_documenter/exporters/_documentation_partitioning.py`):

1. **Regla principal**: `webform` no vacío con separador de ruta (`\` o `/`, normalizado) → su primer segmento de
   ruta (la carpeta que contiene el `.ascx`/`.aspx`).
2. **Fallback (tier 2)**: `webform` no vacío sin separador de ruta (archivo en la raíz) → su nombre de archivo sin
   extensión — sigue siendo evidencia directa del punto de entrada, solo con granularidad distinta.
3. **`"unassigned"` (tier 3)**: `webform` ausente/`None`/vacío tras `strip()` — únicamente cuando no hay
   evidencia real, nunca como sustituto de `projects`.

Ejemplo verificado por test (`FlowGroupKeyTests`,
`tests/test_v4_3_r4_scaling_and_partitioning.py`): con `entry_point.webform =
"webCobMorosidad\\cobCargaArcIntRea.ascx"` y `projects = ["DAL"]`, `flow_group_key` devuelve `"webCobMorosidad"`,
no `"DAL"`; lo mismo para `"webCobMorosidad\\cobChqInsRen.ascx"`; ambos flujos, pasados juntos a
`render_human_documentation_partitions`, terminan en la misma partición `webCobMorosidad.md`
(`test_two_flows_under_the_same_webform_folder_land_in_the_same_partition`). Las muestras regeneradas bajo
`docs/V4_3/samples/R4/` (ver 12.3) muestran los tres flujos B/C/D en un único grupo `webCobMorosidad`.

No se usa ninguna heurística de nombres de proyecto (p. ej. una lista "DAL"/"BL"/"Infrastructure" a excluir): la
regla es puramente estructural sobre `entry_point.webform`. `PARTITIONS_SUBDIR`, `sanitize_label`/
`build_partition_filenames` y el resto del particionado no cambian — solo el origen de la clave.

### 12.2 Reapertura de WEB_ENTRY_POINTS.md y PROJECT_DEPENDENCIES.md; WEBFORMS_MAP.md sin cambios

La sección 8 original documentó, con evidencia empírica de V4.2-R7, que estos tres documentos eran
`PARTIALLY_USEFUL` (no `NOT_USEFUL`) y decidió no particionarlos en la implementación original de esta ronda. El
Líder Técnico reabre esa decisión, acotadamente, solo para dos de los tres, reutilizando la misma evidencia ya
citada (nunca fabricada de nuevo, conforme a `AGENTS.md`):

| Documento | Escala real observada (V4.2-R7) | Decisión final (esta corrección) |
|---|---|---|
| `WEB_ENTRY_POINTS.md` | 25.595 líneas / 1,2MB, ~2.580 secciones | **Reabierto**: navegación + particiones por carpeta propietaria del WebForm |
| `PROJECT_DEPENDENCIES.md` | 9.424 líneas / 978KB | **Reabierto**: navegación + particiones por proyecto de origen (`source`) |
| `WEBFORMS_MAP.md` | 13.944 líneas / 1,37MB | **Sin cambios**: se mantiene sin particionar |

`WEBFORMS_MAP.md` se deja explícitamente fuera de esta corrección: su hallazgo original (F-03, repr crudo de
Python en `register`) ya fue corregido por separado en V4.2-R7.1 y era un defecto de *presentación*, no de
ausencia de navegación/escala; la instrucción del Líder Técnico para esta corrección lo nombra explícitamente
como fuera de alcance ("`WEBFORMS_MAP.md` NO se toca en esta corrección"). Esta es una decisión independiente de
la de los otros dos documentos, no una consecuencia automática de ella.

**WEB_ENTRY_POINTS.md** (`legacy_documenter/exporters/technical_documentation_renderer.py`): nuevos métodos
`web_entry_points_navigation(indexes)`/`web_entry_points_partitions(indexes)`, mismo patrón exacto que
`functional_flows_navigation`/`functional_flows_partitions` (V4.2-R8): navegación con tabla de grupos + enlaces
relativos a `web_entry_points/<safe-name>.md`; particiones con las mismas tablas "Control/Event/Type/Handler/
Confidence" y sección "Unresolved Entry Points" que ya produce `web_entry_points()`, por grupo. El método plano
`web_entry_points()` no se modifica. Agrupación: `_web_entry_point_group_key`, que delega en
`webform_owner_group_key` (la misma función que usa `flow_group_key`, sección 12.1 — factorizada una sola vez en
`_documentation_partitioning.py` para no duplicarla entre los dos módulos). Wiring en
`legacy_documenter/cli/pipeline_stages.py`: `("WEB_ENTRY_POINTS.md", "web_entry_points")` se elimina de
`_DOCUMENTATION_RENDERERS` (que queda vacía) y se añade
`("WEB_ENTRY_POINTS.md", "web_entry_points", "web_entry_points_navigation", "web_entry_points_partitions")` a
`_PARTITIONED_DOCUMENTATION_RENDERERS` — exactamente la misma transición que V4.2-R8 ya aplicó a los otros tres
documentos.

**PROJECT_DEPENDENCIES.md** (`legacy_documenter/exporters/markdown_exporter.py`, una clase/ruta de escritura
distinta de `TechnicalDocumentationRenderer`): nuevos métodos `project_dependencies_navigation(indexes)`/
`project_dependencies_partitions(indexes)`, agrupando por `dep["source"]` (el proyecto de origen de cada arista
de dependencia, ya presente en `indexes["dependencies"]`, sin inventar ningún campo nuevo). `MarkdownExporter.
export()` ahora escribe `PROJECT_DEPENDENCIES.md` como documento de navegación y sincroniza
`documentation/project_dependencies/` con `sync_generated_partition_directory`
(`legacy_documenter.cli.artifact_lifecycle`, reutilizada sin reimplementar la lógica de sync/limpieza de
particiones obsoletas). Se verificó que `legacy_documenter/cli/artifact_lifecycle.py` no importa nada de
`legacy_documenter/exporters/` ni de `legacy_documenter/cli/pipeline_stages.py` (solo `pathlib`), y que
`legacy_documenter/cli/__init__.py` está vacío (solo docstring) — por lo que importar
`legacy_documenter.cli.artifact_lifecycle` desde `markdown_exporter.py` no crea un ciclo de importación,
confirmado empíricamente (`python -c "import legacy_documenter.exporters.markdown_exporter"` funciona). El
método plano `project_dependencies()` no se modifica.

Requisitos comunes verificados por test para ambos documentos: toda la evidencia se conserva (la unión de las
particiones reproduce el mismo contenido que el renderer plano, sin duplicar filas entre particiones —
`test_union_of_partitions_reproduces_the_flat_document_content_without_duplication` en ambos casos); ningún
schema de `index/*.json` cambia; el documento top-level nunca se elimina, se convierte en índice; el detalle
completo vive solo en las particiones; enlaces relativos verificados contra los nombres de archivo realmente
producidos; nombres vía `sanitize_label`/`build_partition_filenames` sin reinventar; determinismo independiente
del orden de entrada; cobertura exhaustiva (cada WebForm/cada dependencia en exactamente una partición);
`render_documentation` funciona end-to-end tras el cambio de wiring de WEB_ENTRY_POINTS
(`RenderDocumentationWebEntryPointsWiringTests`, incluida limpieza de particiones obsoletas en un rerun); y
`MarkdownExporter.export()` escribe correctamente índice + directorio de particiones de PROJECT_DEPENDENCIES y
limpia particiones obsoletas de una corrida anterior
(`MarkdownExporterExportWritesProjectDependenciesPartitionsTests`).

### 12.3 Muestras regeneradas y nuevas (Tareas 3 y 4)

Las tres muestras bajo `docs/V4_3/samples/R4/` originales (sección 7) se regeneraron con la agrupación
corregida: `documentacion_humana_indice.md` ahora muestra un único grupo `webCobMorosidad` con los tres flujos
B/C/D (2 con terminal confirmado, 1 con límite no resuelto), y `flujos_humanos/webCobMorosidad.md` contiene el
detalle completo de los tres. El antiguo `flujos_humanos/DAL.md` ya no existe (no hay grupo `DAL`).

Nuevas muestras pequeñas añadidas (Tarea 4), generadas a partir de fixtures reducidos reutilizando los mismos
tres WebForms bajo `webCobMorosidad\`/dos proyectos de ejemplo:

| Archivo | Contenido |
|---|---|
| `docs/V4_3/samples/R4/documentacion_humana_indice.md` | Índice regenerado: 3 flujos, 1 grupo (`webCobMorosidad`) |
| `docs/V4_3/samples/R4/flujos_humanos/webCobMorosidad.md` | Partición única regenerada: los tres flujos B/C/D completos |
| `docs/V4_3/samples/R4/web_entry_points_indice.md` | Índice de WEB_ENTRY_POINTS de ejemplo (3 entry points, 1 grupo) |
| `docs/V4_3/samples/R4/web_entry_points/webCobMorosidad.md` | Partición de ejemplo de WEB_ENTRY_POINTS |
| `docs/V4_3/samples/R4/project_dependencies_indice.md` | Índice de PROJECT_DEPENDENCIES de ejemplo (3 aristas, 2 proyectos origen) |
| `docs/V4_3/samples/R4/project_dependencies/WebCobranzas.md` | Partición de ejemplo de PROJECT_DEPENDENCIES (origen `WebCobranzas`) |
| `docs/V4_3/samples/R4/project_dependencies/CobranzasBL.md` | Partición de ejemplo de PROJECT_DEPENDENCIES (origen `CobranzasBL`) |

### 12.4 Archivos runtime modificados por esta corrección

| Archivo | Tipo de cambio |
|---|---|
| `legacy_documenter/exporters/_documentation_partitioning.py` | Nueva función compartida `webform_owner_group_key` |
| `legacy_documenter/documentation/human_documentation_scaling.py` | `flow_group_key` corregido para usar `entry_point.webform` vía la función compartida; docstrings/prosa española actualizados |
| `legacy_documenter/exporters/technical_documentation_renderer.py` | Nuevos métodos `web_entry_points_navigation`/`web_entry_points_partitions` + `_web_entry_point_group_key`; `web_entry_points()` sin cambios |
| `legacy_documenter/exporters/markdown_exporter.py` | Nuevos métodos `project_dependencies_navigation`/`project_dependencies_partitions` + `_group_dependencies_by_source`; `export()` ahora escribe navegación + sincroniza particiones de PROJECT_DEPENDENCIES; `project_dependencies()` sin cambios |
| `legacy_documenter/cli/pipeline_stages.py` | `WEB_ENTRY_POINTS.md` movido de `_DOCUMENTATION_RENDERERS` a `_PARTITIONED_DOCUMENTATION_RENDERERS` |
| `tests/test_v4_3_r4_scaling_and_partitioning.py` | `FlowGroupKeyTests` corregido/ampliado; fixture compartida ajustada; nuevas clases de test para WEB_ENTRY_POINTS/PROJECT_DEPENDENCIES/wiring de pipeline/`MarkdownExporter.export()` |
| `tests/test_v4_1_r0_maintainability_inventory.py` | Actualización mecánica: `MarkdownExporter` (8→10 métodos) cruza el umbral de clasificación de esta herramienta (`OK`→`REVIEW`) en `largest_classes`; ninguna otra sección del inventario congelado se vio afectada (verificado por comparación directa contra una reconstrucción fresca) |

Ningún archivo bajo `legacy_documenter/llm/` ni el repositorio legacy fuente fue tocado. `PROJECT_STATE.json` no
se modificó. No se inició V4.3-R5. No se implementó presupuesto de IA (`ai_projection`/AI budgeting).

### 12.5 Conteos de tests

- Antes de esta corrección (tras la implementación original de R4, sección 10): 1889 tests, 0 fallos, 132 skips.
- Después de esta corrección: **1912 tests**, **0 fallos**, **132 skips** (sin cambio) —
  `python -m unittest discover -s tests` → `OK (skipped=132)`.
- `python -m unittest tests.test_v4_3_r4_scaling_and_partitioning` (ejecutado en verbose, `-v`, para esta
  verificación) → **50/50 `OK`**, desglosado por clase de test (la suma exacta de las 12 clases del módulo,
  no una lista parcial):

  | Clase de test | Tests |
  |---|---|
  | `PartitionDocumentTests` | 9 |
  | `WebEntryPointsPartitioningTests` | 7 |
  | `NavigationIndexTests` | 7 |
  | `FlowGroupKeyTests` | 7 |
  | `ProjectDependenciesPartitioningTests` | 6 |
  | `WebformOwnerGroupKeySharedHelperTests` | 3 |
  | `RuntimeIndependenceTests` | 3 |
  | `MarkdownExporterExportWritesProjectDependenciesPartitionsTests` | 2 |
  | `MachineProjectionIntactTests` | 2 |
  | `DeterminismTests` | 2 |
  | `SanitizeLabelReuseTests` | 1 |
  | `RenderDocumentationWebEntryPointsWiringTests` | 1 |
  | **Total** | **50** |

  (La cifra "31 antes de la corrección" de un borrador previo de esta sección describía número de tests
  antes de la corrección, no una suma que debiera cuadrar con las clases nuevas listadas junto a ella; esa
  frase se elimina aquí porque mezclaba dos conteos distintos y no sumaba 50. El desglose de arriba es el
  conteo real, verificado por clase, de la suite tal como quedó tras la corrección.)
- `python -m unittest tests.test_v4_1_r0_maintainability_inventory` → `OK` (inventario congelado V4.1-R0
  actualizado mecánicamente, sección 12.4).

### 12.6 Revisión humana obligatoria (corrección) — Gate para R5

Pendiente de aprobación por el Líder Técnico antes de iniciar R5 (sustituye a la sección 11 para los puntos que
esta corrección modifica):

- [ ] la corrección de `flow_group_key` (12.1), verificada contra el caso real `webCobMorosidad`;
- [ ] la reapertura de `WEB_ENTRY_POINTS.md`/`PROJECT_DEPENDENCIES.md` y la decisión de no tocar
      `WEBFORMS_MAP.md` (12.2);
- [ ] las muestras regeneradas y nuevas bajo `docs/V4_3/samples/R4/` (12.3);
- [ ] los archivos runtime modificados por esta corrección (12.4);
- [ ] los conteos de tests finales: 1912 tests, 0 fallos, 132 skips (12.5).

## 13. Corrección 2: español por defecto para WEB_ENTRY_POINTS/PROJECT_DEPENDENCIES

Instrucción directa del Líder Técnico, aplicada como corrección puntual y acotada sobre esta misma ronda R4 (no
inicia V4.3-R5, no modifica `PROJECT_STATE.json`). Mismo estilo que la sección 12: las secciones 1-12 anteriores
se conservan como registro histórico; esta sección es **autoritativa sobre el estado final** donde entra en
conflicto con ellas.

### 13.1 Defecto

La corrección 1 (sección 12) reabrió `WEB_ENTRY_POINTS.md`/`web_entry_points/*.md` y
`PROJECT_DEPENDENCIES.md`/`project_dependencies/*.md` para particionado, pero sus nuevos métodos
(`web_entry_points_navigation`/`web_entry_points_partitions`, `project_dependencies_navigation`/
`project_dependencies_partitions`) renderizaban en inglés -- el mismo idioma que sus renderers planos
preexistentes (`web_entry_points()`/`project_dependencies()`, no autorados por R4, ver sección 8). Esto
incumplía el requisito global del proyecto de documentación humana en español por defecto
(`PROJECT_STATE.json.human_documentation_language = "ES"`, ya cumplido por `human_documentation_scaling.py`
desde la implementación original de esta ronda) para la documentación humana específicamente creada/modificada
por R4.

### 13.2 Corrección

Se tradujo únicamente la prosa/encabezados humanos de los cuatro métodos R4-autorados; los renderers planos
preexistentes (`web_entry_points()`, `project_dependencies()`) **no se tocan** -- siguen en inglés, decisión de
alcance ya establecida y no reabierta por esta corrección (sección 8: "R1 §7 ya deja explícito que V4.3 ...
puede ... cambiar ese contenido a español, pero no fija en qué ronda").

**`legacy_documenter/exporters/technical_documentation_renderer.py`** (`web_entry_points_navigation`/
`web_entry_points_partitions`):

| Inglés (antes) | Español (ahora) |
|---|---|
| `# Web Entry Points` | `# Puntos de entrada web` |
| `## Entry Point Groups` | `## Grupos de puntos de entrada` |
| `## By WebForm` | `## Por WebForm` |
| `## Unresolved Entry Points` | `## Puntos de entrada no resueltos` |
| `\| Group \| WebForms \| Entry Points \| Confirmed \| Unresolved \| Detail \|` | `\| Grupo \| WebForms \| Puntos de entrada \| Confirmados \| No resueltos \| Detalle \|` |
| `\| Control \| Event \| Type \| Handler \| Confidence \|` | `\| Control \| Evento \| Tipo \| Manejador \| Confianza \|` |
| `\| WebForm \| Control \| Event \| Handler \|` | `\| WebForm \| Control \| Evento \| Manejador \|` |
| `Discovered N entry point(s) across...` | `Se descubrieron N punto(s) de entrada en...` |
| `_(page)_` (placeholder de control ausente) | `_(página)_` |
| `(unknown WebForm)` (placeholder) | `(WebForm desconocido)` |
| frase explicativa de "Full per-WebForm detail is partitioned..." | traducida íntegra |
| frase explicativa de "These entry points could not be resolved..." | traducida íntegra |

**`legacy_documenter/exporters/markdown_exporter.py`** (`project_dependencies_navigation`/
`project_dependencies_partitions`):

| Inglés (antes) | Español (ahora) |
|---|---|
| `# Project Dependencies` | `# Dependencias de proyectos` |
| `\| Source Project \| Dependencies \| Detail \|` | `\| Proyecto origen \| Dependencias \| Detalle \|` |
| `N project dependency edge(s) across M source project(s).` | `N arista(s) de dependencia de proyecto en M proyecto(s) origen.` |
| frase explicativa de "Full detail is partitioned by source project..." | traducida íntegra |
| `No project dependencies were discovered.` | `No se descubrieron dependencias de proyectos.` |

**Preservado intacto en ambos documentos, verificado por test** (sección 13.4): nombres de WebForms (rutas
completas, p. ej. `webCobMorosidad\cobCargaArcIntRea.ascx`), handlers (`btnCargar_Click`), controles
(`btnCargar`), IDs, valores de `confidence`/`dependency_type` (`unresolved`, `ProjectReference`), y nombres de
proyecto (`WebApp`, `CobranzasBL`) -- ninguno se traduce ni se modifica.

### 13.3 Estructura de particionado sin cambios

Ningún cambio a grupos, rutas de partición, nombres de archivo, conteos o enlaces relativos -- solo texto. Esto
se sigue directamente de que la traducción tocó exclusivamente literales de cadena de prosa/encabezados dentro
de los mismos cuatro métodos, sin tocar `_group_by`/`_web_entry_point_group_key`/`webform_owner_group_key`/
`_group_dependencies_by_source`/`sanitize_label`/`build_partition_filenames` ni la lógica de agrupación/
sorting/nombrado de ninguno de los dos módulos. Verificado por los tests de agrupación/deduplicación/enlaces ya
existentes de las secciones 3/12 (sin modificar), que siguen en verde tras esta corrección sin haber sido
tocados.

### 13.4 Tests añadidos

Dos clases nuevas en `tests/test_v4_3_r4_scaling_and_partitioning.py` (3 tests cada una), más 3 aserciones de
texto corregidas en tests preexistentes (`test_unresolved_entry_stays_visible_within_its_own_group`,
`test_no_entry_points_produces_no_partitions`, `test_no_dependencies_produces_no_partitions` -- estas tres
esperaban literales en inglés que la traducción reemplazó; se actualizaron al texto español real, ninguna
aserción se debilitó):

| Clase | Tests | Verifica |
|---|---|---|
| `WebEntryPointsSpanishByDefaultTests` | `test_navigation_is_in_spanish`, `test_partitions_are_in_spanish`, `test_technical_names_are_preserved_intact` | Encabezados/prosa en español, ausencia de literales en inglés, WebForm/handler/control/confidence intactos |
| `ProjectDependenciesSpanishByDefaultTests` | `test_navigation_is_in_spanish`, `test_partitions_are_in_spanish`, `test_technical_names_are_preserved_intact` | Encabezados/prosa en español, ausencia de literales en inglés, nombre de proyecto/`dependency_type` intactos |

Los tests de conteos, cobertura, determinismo, ausencia de pérdida de evidencia y estructura de particionado ya
existentes (secciones 3-4 y 12.2, `WebEntryPointsPartitioningTests`/`ProjectDependenciesPartitioningTests`/
`RenderDocumentationWebEntryPointsWiringTests`/`MarkdownExporterExportWritesProjectDependenciesPartitionsTests`)
no requirieron cambio de lógica -- solo las tres correcciones de literal de texto ya listadas -- y siguen
verificando exactamente las mismas garantías (13.3).

### 13.5 Muestras regeneradas

Regeneradas ejecutando directamente los renderers reales (no escritas a mano) para garantizar que coinciden
byte a byte con el código:

| Archivo | Contenido |
|---|---|
| `docs/V4_3/samples/R4/web_entry_points_indice.md` | Índice de WEB_ENTRY_POINTS regenerado en español (mismo fixture de 3 entry points/1 grupo que la sección 12.3) |
| `docs/V4_3/samples/R4/web_entry_points/webCobMorosidad.md` | Partición regenerada en español |
| `docs/V4_3/samples/R4/project_dependencies_indice.md` | Índice de PROJECT_DEPENDENCIES regenerado en español (mismo fixture de 3 aristas/2 proyectos origen) |
| `docs/V4_3/samples/R4/project_dependencies/WebCobranzas.md` | Partición regenerada en español |

Los grupos (`webCobMorosidad`; `WebCobranzas`/`CobranzasBL`), nombres de archivo, y conteos (3 entry points, 3
aristas) son idénticos a las muestras anteriores a esta corrección -- solo el texto humano cambió.

### 13.6 Archivos modificados por esta corrección

| Archivo | Tipo de cambio |
|---|---|
| `legacy_documenter/exporters/technical_documentation_renderer.py` | `web_entry_points_navigation`/`web_entry_points_partitions` traducidos al español; `web_entry_points()` sin cambios |
| `legacy_documenter/exporters/markdown_exporter.py` | `project_dependencies_navigation`/`project_dependencies_partitions` traducidos al español; `project_dependencies()` sin cambios; su crecimiento a 204 líneas cruza el umbral de 200 líneas de este proyecto (LOW → MEDIUM, ver 13.7) |
| `tests/test_v4_3_r4_scaling_and_partitioning.py` | 2 clases nuevas (6 tests) + 3 aserciones de texto corregidas en tests existentes |
| `tests/test_v4_1_r0_maintainability_inventory.py` | Actualización mecánica: `markdown_exporter.py` cruza de `LOW` a `MEDIUM` en `risk_summary["files_by_risk_category"]` (112 → 204 líneas); `technical_documentation_renderer.py` permanece en `MEDIUM` (ya muy por encima de cualquier umbral de línea desde antes de esta corrección, sin cruce de categoría) |
| `docs/V4_3/samples/R4/web_entry_points_indice.md`, `.../web_entry_points/webCobMorosidad.md`, `.../project_dependencies_indice.md`, `.../project_dependencies/WebCobranzas.md` | Regenerados en español |

Ningún archivo bajo `legacy_documenter/llm/` ni el repositorio legacy fuente fue tocado. `PROJECT_STATE.json` no
se modificó. No se inició V4.3-R5. `WEBFORMS_MAP.md` no se tocó (fuera de alcance explícito de esta corrección).

### 13.7 Conteos de tests

- Antes de esta corrección (tras la corrección 1, sección 12.5): 1912 tests, 0 fallos, 132 skips.
- Después de esta corrección: **1918 tests** (1912 + 6 nuevos de `WebEntryPointsSpanishByDefaultTests`/
  `ProjectDependenciesSpanishByDefaultTests`), **0 fallos**, **132 skips** (sin cambio) --
  `python -m unittest discover -s tests` → `OK (skipped=132)`, ejecutado antes y después de esta corrección.
- `python -m unittest tests.test_v4_3_r4_scaling_and_partitioning` → **56/56 `OK`**, desglosado por clase
  (la suma exacta de las 14 clases del módulo):

  | Clase de test | Tests |
  |---|---|
  | `PartitionDocumentTests` | 9 |
  | `FlowGroupKeyTests` | 7 |
  | `NavigationIndexTests` | 7 |
  | `WebEntryPointsPartitioningTests` | 7 |
  | `ProjectDependenciesPartitioningTests` | 6 |
  | `ProjectDependenciesSpanishByDefaultTests` | 3 |
  | `RuntimeIndependenceTests` | 3 |
  | `WebEntryPointsSpanishByDefaultTests` | 3 |
  | `WebformOwnerGroupKeySharedHelperTests` | 3 |
  | `DeterminismTests` | 2 |
  | `MachineProjectionIntactTests` | 2 |
  | `MarkdownExporterExportWritesProjectDependenciesPartitionsTests` | 2 |
  | `RenderDocumentationWebEntryPointsWiringTests` | 1 |
  | `SanitizeLabelReuseTests` | 1 |
  | **Total** | **56** |

- `python -m unittest tests.test_v4_1_r0_maintainability_inventory` → 22/22 `OK` (inventario congelado
  actualizado mecánicamente para el cruce de categoría de `markdown_exporter.py`, sección 13.6; ninguna otra
  sección se vio afectada).

### 13.8 Fuera de alcance, incluso tras esta corrección

- `web_entry_points()`/`project_dependencies()` (renderers planos preexistentes, no autorados por R4)
  permanecen en inglés -- no reabiertos por esta corrección.
- `WEBFORMS_MAP.md` no se toca (excluido explícitamente de la instrucción de esta corrección, y ya fuera de
  alcance desde la sección 12.2).
- No se modifica `PROJECT_STATE.json`.
- No se inicia V4.3-R5.
- No se cambia la estructura de particionado (grupos, rutas, nombres de archivo, conteos, evidencia, enlaces) --
  ver 13.3.

### 13.9 Revisión humana obligatoria (corrección 2) — Gate para R5

Pendiente de aprobación por el Líder Técnico antes de iniciar R5 (complementa la sección 12.6 para los puntos
que esta corrección modifica):

- [ ] la traducción al español de `web_entry_points_navigation`/`web_entry_points_partitions` y
      `project_dependencies_navigation`/`project_dependencies_partitions`, con nombres técnicos intactos (13.1-13.2);
- [ ] la confirmación de que la estructura de particionado no cambió (13.3);
- [ ] los tests nuevos/corregidos (13.4);
- [ ] las cuatro muestras regeneradas bajo `docs/V4_3/samples/R4/` (13.5);
- [ ] los archivos runtime modificados, en particular el cruce de categoría de `markdown_exporter.py` en el
      inventario de mantenibilidad (13.6);
- [ ] los conteos de tests finales: 1918 tests, 0 fallos, 132 skips (13.7).
