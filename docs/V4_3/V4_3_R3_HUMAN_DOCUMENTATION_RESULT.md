# V4.3 — R3 — Documentación humana prioritaria — Resultado

## Estado de esta ronda

`V4_3_R3_RESULT_IMPLEMENTED_PENDING_HUMAN_REVIEW`. Como R2 (y a diferencia de R0/R1, de diseño), esta ronda
implementa código de producción: `legacy_documenter/documentation/human_flow_documentation.py` y sus tests.
El `Gate` de R2 ("Pendiente de aprobación por el Líder Técnico antes de iniciar R3") queda satisfecho por la
misma vía que R1→R2: la instrucción directa de ejecutar R3 (`ejecuta V4_3_R3_HUMAN_DOCUMENTATION.md`). Esta
ronda no cierra ni versiona V4.3 (sigue correspondiendo exclusivamente a R9) y no modifica `PROJECT_STATE.json`.

**Correcciones aplicadas a esta misma ronda** (instrucciones directas del Líder Técnico, sin iniciar R4, cada
una sobre el estado dejado por la anterior):

1. La versión original de este resultado (secciones 1–9 abajo) dejó explícitamente sin resolver el caso C de
   aceptación de R0 (evidencia de escritura/transacción). La **sección 10** documenta esa corrección: extiende
   R2 de forma mínima y aditiva para exponer evidencia transaccional/de tipo de operación de datos ya presente
   en los índices, sin introducir ninguna inferencia narrativa en el renderer.
2. Tras revisión humana de las tres muestras generadas por la corrección 1, se identificaron dos defectos de
   presentación: (a) un `PATH` deduplicado solo mostraba el puntero de origen del primer `path_id` fusionado,
   perdiendo silenciosamente la procedencia de los demás; (b) los elementos `technical_noise_candidate` se
   mezclaban sin distinción en la lista principal de "Servicios/capas". La **sección 12** documenta esa segunda
   corrección.

Las secciones 1–9 originales se conservan sin reescribir salvo donde una corrección las vuelve inexactas
(marcado explícitamente donde ocurre); las secciones 10 y 12 son la referencia autoritativa sobre el estado
final de cada defecto que corrigen.

## 1. Objetivo

Generar documentación humana útil, en español por defecto, a partir de la proyección hidratada que R2 ya
produce (`EvidenceHydrator.hydrate_flow`), implementando la superficie `human_documentation` que R1 §5.1
reservó para evidencia de código ("nueva, a implementar en R3/R4"), bajo el nombre de contrato
`HUMAN_DOCUMENTATION_PROJECTION 1.0` que R1 §5.1 ya fijó.

## 2. Qué se implementó

- **`legacy_documenter/documentation/human_flow_documentation.py`** (nuevo, 288 líneas):
  `render_flow_document(record, interpretations=None) -> str`, función pura que renderiza un registro
  `FLOW` hidratado (la forma exacta que devuelve `EvidenceHydrator.hydrate_flow`) como un documento Markdown
  en español, con las siete secciones exigidas por el prompt y la sección adicional de límites.
- **`tests/test_v4_3_r3_human_documentation.py`** (nuevo, 19 tests).
- **`tests/test_v4_1_r0_maintainability_inventory.py`** (modificado): actualización mecánica del inventario de
  mantenibilidad congelado (V4.1-R0) para reflejar el nuevo módulo de producción — ver sección 6.

`render_flow_document` es una función pura sobre el `dict` que `EvidenceHydrator.hydrate_flow` ya produce: no
lee ningún archivo, no llama a ningún proveedor de IA, no escribe a disco, y no está conectado a
`legacy_documenter/cli/` ni a `legacy_documenter/main.py` — misma postura de independencia de runtime que R2
(`legacy_documenter/context/hydration.py`).

## 3. Cobertura de requisitos

### 3.1 Las siete secciones del prompt

| # | Sección del prompt | Implementación |
|---|---|---|
| 1 | Qué es / dónde está | `_section_1_what_and_where`: formulario web, proyectos/capas involucrados, confianza general del flujo |
| 2 | Evento/entrada inicial | `_section_2_entry_event`: evento, manejador y método de inicio; declara explícitamente cuando no pudieron determinarse |
| 3 | Qué hace según evidencia | `_section_3_what_it_does`/`_describe_path`: una oración por cada grupo de camino hidratado (confianza + cadena de nodos + terminal resuelto) |
| 4 | Servicios/capas | `_section_4_services_and_layers`: invocadores de acceso a datos (`class.method`) distintos alcanzados por el flujo |
| 5 | Datos/SP/SQL | `_section_5_data_sp_sql`: procedimientos almacenados y operaciones SQL resueltos, con parámetros disponibles por invocador alcanzado |
| 6 | Qué queda no resuelto | `_section_6_unresolved`: límites no resueltos y caminos con incertidumbre, nunca ocultos |
| 7 | Evidencia/trazabilidad | `_section_7_evidence_and_traceability`: `path_id`s, `evidence_refs` y punteros de procedencia (`source_index_pointer`, `flow_source_index_pointer`) por camino |

### 3.2 Las seis reglas del prompt

| Regla | Cómo se satisface |
|---|---|
| No traducir JSON mecánicamente | Cada sección compone oraciones/listas en prosa a partir de campos del registro hidratado; ninguna sección serializa el `dict` de entrada. `test_document_is_not_a_mechanical_json_dump` verifica la ausencia de patrones de volcado JSON (`{'`, `": "`) en la salida. |
| IDs técnicos no son explicación principal | `_describe_node`/`_describe_terminal` usan `resolved_name` cuando existe; el `id` crudo (`SP-1`, `DAO-1`) solo aparece en la sección 7 (evidencia/trazabilidad) y en el mensaje explícito de "no resuelto". `test_resolved_names_are_the_primary_explanation_not_bare_ids` verifica que `SP-1` no aparece en la sección 3, mientras que `spActualizarSaldo` sí. |
| Nombres técnicos intactos | Ningún nombre de clase/método/procedimiento/paquete se transforma o traduce; `test_technical_names_are_preserved_intact` verifica `CobDAO.Actualizar`, `spActualizarSaldo`, `PKG_COB`, `PR_SALDO` verbatim. |
| IA solo aporta `INTERPRETED` | El parámetro opcional `interpretations` solo puede añadir contenido a una sección final separada y explícitamente etiquetada `## Interpretación de IA (\`INTERPRETED\`)`; `InvalidInterpretationError` rechaza cualquier ítem que declare un `status` distinto de `INTERPRETED` (nunca puede reclamar `CONFIRMED`) o que referencie `evidence_refs` ausentes/desconocidas — ver `_section_interpreted` y los tests de `InterpretedSectionTests`. Esta ronda no genera ninguna interpretación de IA por sí misma (eso es R5/R6); solo define el contrato de cómo un llamador futuro la adjuntaría sin violar la regla. |
| Sin IA debe existir documentación determinista útil | `render_flow_document(record)` sin `interpretations` produce un documento completo y útil por sí solo (las siete secciones + límites); `interpretations` es puramente opcional y aditivo. `test_deterministic_document_is_useful_without_any_ai` y `test_no_interpretation_means_no_interpreted_section` verifican que, sin él, no aparece ninguna sección `INTERPRETED`. |
| Declarar límites | `_section_limits` declara explícitamente: que el documento es 100% determinista (sin IA); que los IDs son trazabilidad, no explicación; cuántos caminos deterministas originales se fusionaron por deduplicación (reutilizando `record["selection"]` de R2) y cuántos se describen; que ningún elemento de `technical_noise_candidate` fue eliminado; y que solo la sección final, si existe, contiene interpretación de IA. |

## 4. Tests obligatorios — mapeo

| Categoría | Test(s) |
|---|---|
| Secciones requeridas / español | `test_document_is_in_spanish_with_required_sections` |
| IDs no son la explicación principal | `test_resolved_names_are_the_primary_explanation_not_bare_ids` |
| Nombres técnicos intactos | `test_technical_names_are_preserved_intact` |
| No traducción mecánica de JSON | `test_document_is_not_a_mechanical_json_dump` |
| Unresolved preservado (caso D de R0) | `test_flow_without_confirmed_terminal_declares_uncertainty_without_inventing_a_terminal`, `test_unresolved_path_is_declared_not_hidden` |
| Ruido técnico señalado, nunca eliminado | `test_technical_noise_candidate_is_flagged_but_never_removed` |
| Trazabilidad | `test_traceability_section_lists_path_ids_evidence_refs_and_provenance` |
| Útil sin IA | `test_deterministic_document_is_useful_without_any_ai`, `test_no_interpretation_means_no_interpreted_section` |
| Límites declarados | `test_limits_are_declared_explicitly` |
| Determinismo | `test_deterministic_across_repeated_calls` |
| `INTERPRETED` solo de IA, con evidencia y sin `CONFIRMED` | `InterpretedSectionTests` (4 tests) |
| Independencia de runtime | `RuntimeIndependenceTests` (3 tests, mismo patrón que R2) |

## 5. Casos reales de aceptación externa (R0 §5) frente a esta implementación

| Caso | Cobertura por este render |
|---|---|
| A. Consulta compleja, múltiples terminales | La sección 3 describe un camino por grupo hidratado (uno por terminal distinto tras deduplicación de R2), cada uno con su propia confianza — nunca colapsados en un solo enunciado |
| B. Procesamiento/carga, terminales confirmados | La sección 5 expone el/los procedimiento(s) almacenado(s) confirmado(s) con nombre/paquete/procedimiento resueltos; la sección 7 traza cada uno a `path_id`/`evidence_refs` |
| C. Escritura/transacción | **Resuelto por la corrección de la sección 10**: la sección 5 del render ahora presenta evidencia transaccional (`BeginTrans`/`Commit`/`Rollback`) y el tipo de operación de datos (`INSERT`/`UPDATE`/`DELETE`/`SELECT`/`MERGE`) cuando el índice determinista ya los registró explícitamente — nunca inferidos del nombre de un procedimiento almacenado. Ver sección 10 |
| D. Sin terminal confirmado | La sección 5 declara explícitamente "No se confirmó acceso a procedimientos almacenados ni operaciones SQL para este flujo"; la sección 6 declara la incertidumbre; ningún terminal se inventa — verificado por `test_flow_without_confirmed_terminal_declares_uncertainty_without_inventing_a_terminal` |

## 6. Archivos runtime modificados

| Archivo | Tipo de cambio |
|---|---|
| `legacy_documenter/documentation/human_flow_documentation.py` | Nuevo módulo de producción (luego extendido por la corrección de la sección 10) |
| `tests/test_v4_3_r3_human_documentation.py` | Nuevo archivo de tests (19 tests; +5 en la corrección de la sección 10) |
| `tests/test_v4_1_r0_maintainability_inventory.py` | Actualización mecánica del inventario congelado V4.1-R0: `production_python_module_count` 170→171, `human_flow_documentation.py` añadido al conjunto de rutas nuevas esperadas, `risk_summary["HIGH"]` +1 (el módulo cae en `HIGH`, no `MEDIUM`, por su recuento de responsabilidades y por estar bajo `legacy_documenter/documentation/`, tratado como histórico por la heurística de la herramienta), entra en `largest_modules` desplazando `legacy_documenter/knowledge/provenance/graph.py` del top-20, y `dependency_findings.module_count` +27→+28. Ninguna aserción se debilitó ni se eliminó; mismo patrón incremental que cada ronda previa. Actualizado una segunda vez por la corrección de la sección 10 (ver 10.3). |

También modificados por la corrección de la sección 10 (no en la versión original de esta ronda):
`legacy_documenter/context/hydration.py` (extendido, no nuevo — ver 10.1) y
`tests/test_v4_3_r2_evidence_hydration.py` (+6 tests — ver 10.3). Nuevos, no runtime:
`docs/V4_3/samples/R3/*.md` (tres muestras, sección 10.4).

Ningún archivo bajo `legacy_documenter/cli/`, `legacy_documenter/main.py`, `legacy_documenter/llm/`, ni
`PROJECT_STATE.json` fue modificado.

## 7. Conteos de tests

- Antes de esta ronda (tras R2): 1826 tests, 0 fallos, 132 skips esperados.
- Después de esta ronda: **1845 tests** (1826 + 19 nuevos de `test_v4_3_r3_human_documentation.py`),
  **0 fallos**, **132 skips** (sin cambio).
- `python -m unittest discover -s tests` → `OK (skipped=132)`.
- El módulo dedicado (`python -m unittest tests.test_v4_3_r3_human_documentation`) → 19/19 `OK`.
- El módulo de inventario de mantenibilidad actualizado
  (`python -m unittest tests.test_v4_1_r0_maintainability_inventory`) → 22/22 `OK`.

`PROJECT_STATE.json` no se modificó; sus campos `tests`/`test_failures`/`test_errors`/`expected_fresh_clone_skips`
siguen describiendo el baseline de V4.2, no este conteo post-R3. Actualizar esos campos, si corresponde, queda
para R9.

## 8. Fuera de alcance de esta ronda

- No se genera documentación humana para `SYSTEM`/`TECHNICAL`/otros niveles agregados, solo para un `FLOW`
  hidratado individual (R4 — "Scaling and Partitioning" — es el que aborda agregación/escalado a nivel de
  sistema completo).
- No se traduce ni modifica `legacy_documenter/exporters/technical_documentation_renderer.py` (el renderizador
  inglés existente de `WEB_ENTRY_POINTS.md`/`FUNCTIONAL_FLOWS.md`/`DATABASE_ACCESS.md`/`UNRESOLVED_FINDINGS.md`,
  D-05 de R0). R1 §7 ya deja explícito que V4.3 "puede, e intencionalmente va a" cambiar ese contenido a
  español, pero no fija en qué ronda; esta ronda entrega la superficie nueva y estable
  (`HUMAN_DOCUMENTATION_PROJECTION 1.0` sobre evidencia hidratada) que R1 §5.1 asignó explícitamente a R3/R4,
  sin tocar el renderizador de 802 líneas ya marcado `HIGH_RISK_FUTURE_EXTRACTION_CANDIDATE` — una reescritura
  de ese módulo es un cambio separado, de mayor riesgo, que no estaba required por el prompt de esta ronda
  ("basada en la proyección hidratada").
- ~~No se implementa una clasificación explícita de "naturaleza transaccional/de escritura" (caso C de R0)~~
  — **superado por la corrección de la sección 10**: sí se implementa, exclusivamente a partir de evidencia
  ya presente en los índices (`operation_kind == "transaction"` + verbo literal de la evidencia;
  `sql_operation`), nunca inferida del nombre de un procedimiento almacenado.
- No se implementa el contrato de presupuesto de `ai_projection`/`consumer_projection` (R5/R6).
- No se conecta `render_flow_document` a `legacy_documenter/cli/`/`main.py` ni a ningún flujo de ejecución
  automático — deliberado, misma postura que R2.
- No se modifica `PROJECT_STATE.json`.
- No se cierra ni versiona V4.3 (sigue correspondiendo exclusivamente a R9).

## 10. Corrección: evidencia transaccional/de escritura sin inferencia narrativa (caso C de R0)

Instrucción directa del Líder Técnico, aplicada sobre esta misma ronda R3, sin iniciar R4: "Corrige V4.3 R3
para resolver el gap del caso C de aceptación sin introducir inferencia narrativa en el renderer."

### 10.1 Extensión mínima de R2 (`legacy_documenter/context/hydration.py`)

`legacy_documenter.extractors.database_extractor.DatabaseExtractor` ya escribía, de forma determinista, dos
campos en cada registro de `index/data_access.json` que R2 no hidrataba todavía: `operation_kind ==
"transaction"` (para llamadas `BeginTrans(action)`/`Commit`/`Rollback`, con el verbo exacto solo recuperable
del texto de la expresión de evidencia ya extraída, no como campo estructurado propio) y `sql_operation`
(el verbo SQL crudo -- `INSERT`/`UPDATE`/`DELETE`/`SELECT`/`MERGE` -- ya presente en el propio registro de
operación, independiente del catálogo separado `sql_operations`). Esta corrección hidrata ambos, sin inventar
ningún campo nuevo que no existiera ya en `ix`:

- `EvidenceHydrator._transaction_evidence(d)`: dado un registro de `data_access`, devuelve `None` salvo que
  `operation_kind == "transaction"`; cuando aplica, `verb` es una coincidencia literal de palabra clave
  (`TRANSACTION_VERB_KEYWORDS = ("BeginTransaction", "BeginTrans", "Commit", "Rollback")`, mismo orden y mismos
  nombres que `DatabaseExtractor.TRANSACTION_RE`) contra el texto ya extraído en `evidence[0]["expression"]`
  -- nunca contra `class`/`method`/nombre resuelto. Si no hay coincidencia, `verb` es `None`, nunca adivinado.
- `_hydrate_node`/`_resolve_terminal` ahora incluyen, cuando aplica, `data_operation_kind` (= `d.get("sql_operation")`
  verbatim) y `transaction_evidence` en cada nodo/terminal de tipo `data_access`.
- Dos nuevos campos de nivel `FLOW`, construidos por los nuevos métodos `_transactions`/`_data_operations`:
  `record["transactions"]` (lista deduplicada y ordenada por id de evidencia transaccional alcanzada por los
  caminos del flujo) y `record["data_operations"]` (lista deduplicada y ordenada por id de operaciones de
  datos confirmadas), cada entrada con `id`, `verb`/`operation`, `confidence`, `path_ids` y
  `source_index_pointer` (`index/data_access.json#<id>`) para trazabilidad completa.
- **Un procedimiento almacenado resuelto solo por nombre nunca produce una entrada en `data_operations`**: la
  rama `stored_procedure` de `_resolve_terminal` no fue tocada y sigue sin exponer `data_operation_kind` —
  verificado por `test_write_is_never_inferred_from_a_stored_procedure_name_alone` (hidratación) usando un SP
  llamado deliberadamente `spInsertarRegistro` sin ninguna evidencia de escritura propia.

### 10.2 Presentación determinista en español (`legacy_documenter/documentation/human_flow_documentation.py`)

- `_evidence_suffix(item)`: añade, a la descripción de un nodo/terminal en la sección 3, `"evidencia
  transaccional confirmada (\`<verbo>\`)"` y/o `"operación de datos confirmada: \`<verbo>\`"` **solo** cuando
  el campo determinista correspondiente (`transaction_evidence`/`data_operation_kind`) ya está presente en el
  registro hidratado — nunca inspecciona `resolved_name`/`caller` para adivinar naturaleza.
- Nuevas subsecciones en la sección 5 (`_data_operations_and_transactions`): `### Evidencia transaccional` y
  `### Operaciones de datos confirmadas`, listando `record["transactions"]`/`record["data_operations"]`
  respectivamente; ausentes por completo (nunca una sección vacía) cuando el flujo no tiene esa evidencia.
- Nueva viñeta en `_section_limits`: declara explícitamente que la evidencia transaccional y el tipo de
  operación de datos solo se presentan cuando el índice ya los registró, y que un procedimiento almacenado
  nunca se clasifica como "escritura" por su nombre.

### 10.3 Tests añadidos

| Archivo | Tests nuevos | Cubre |
|---|---|---|
| `tests/test_v4_3_r2_evidence_hydration.py` (`TransactionAndDataOperationEvidenceTests`) | 6 | Transacción confirmada con verbo (`test_confirmed_transaction_evidence_is_hydrated_with_its_verb`, incluye un verbo no determinado por ausencia de evidencia); ausencia de evidencia transaccional (`test_absence_of_transaction_evidence_is_none_not_a_guess`); operación de escritura declarada por el índice (`test_confirmed_sql_write_operation_kind_is_hydrated_from_the_index`); no inferencia desde nombre de SP (`test_write_is_never_inferred_from_a_stored_procedure_name_alone`); trazabilidad completa (`test_transaction_and_data_operation_traceability`); determinismo (`test_deterministic_across_repeated_calls`) |
| `tests/test_v4_3_r3_human_documentation.py` (`TransactionAndDataOperationRenderingTests`) | 5 | Evidencia transaccional presentada en español (`test_confirmed_transaction_evidence_is_presented_in_spanish`); tipo de operación de datos presentado cuando existe (`test_confirmed_data_operation_kind_is_presented_when_available`); no inferencia desde nombre de SP en el render (`test_write_is_never_inferred_from_a_stored_procedure_name_alone`); ausencia produce secciones ausentes, no vacías (`test_absence_of_transaction_evidence_produces_no_transactional_section`); trazabilidad (`test_traceability_covers_transaction_and_data_operation_evidence`) |

`tests/test_v4_1_r0_maintainability_inventory.py` se actualizó una segunda vez (mecánicamente, mismo patrón
que las rondas anteriores) para reflejar el crecimiento de ambos módulos: `hydration.py` (204→290 líneas,
sigue `MEDIUM`) entra ahora también en `largest_modules`, desplazando
`legacy_documenter/knowledge/projection/example_report.py`; `human_flow_documentation.py` creció a 335 líneas
(sigue `HIGH`, sin cambio de categoría).

### 10.4 Muestras Markdown generadas

Tres documentos generados con `render_flow_document`, a partir de fixtures equivalentes a las de los tests,
guardados bajo `docs/V4_3/samples/R3/` (no son artefactos de producto; ilustran el resultado de esta ronda
para revisión humana):

| Archivo | Caso de R0 §5 | Contenido ilustrado |
|---|---|---|
| `flow_confirmed_terminal.md` | B (procesamiento/carga, terminal confirmado) | `cobCargaArcIntRea.ascx` → `Click` → `btnCargar_Click`; dos `PATH` deterministas deduplicados en un solo camino confirmado hacia un procedimiento almacenado con nombre/paquete resueltos |
| `flow_unresolved_no_terminal.md` | D (sin terminal confirmado) | `CobConsultaTransferencia.ascx` → `Load` → `Page_Load`; incertidumbre declarada explícitamente, sin inventar ningún terminal |
| `flow_technical_noise_and_transaction.md` | A + C combinados (múltiples terminales; escritura/transacción) | `cobChqInsRen.ascx` → `Click` → `HypGuardar_Click`; un camino confirmado con evidencia transaccional (`BeginTrans`) y operación de datos confirmada (`INSERT`) hacia un procedimiento almacenado llamado deliberadamente `spInsertarRenovacionCheque` (para demostrar que el nombre no se usa como evidencia), y un segundo camino no resuelto con ruido técnico (`InitializeComponent`) señalado pero no eliminado |

### 10.5 Conteos de tests tras la corrección

- Antes de la corrección (R3 original): 1845 tests, 0 fallos, 132 skips.
- Después de la corrección: **1856 tests** (1845 + 6 de `TransactionAndDataOperationEvidenceTests` + 5 de
  `TransactionAndDataOperationRenderingTests`), **0 fallos**, **132 skips** (sin cambio).
- `python -m unittest discover -s tests` → `OK (skipped=132)`.
- `python -m unittest tests.test_v4_3_r2_evidence_hydration` → 22/22 `OK`.
- `python -m unittest tests.test_v4_3_r3_human_documentation` → 24/24 `OK`.
- `python -m unittest tests.test_v4_1_r0_maintainability_inventory` → 22/22 `OK`.

### 10.6 Fuera de alcance, incluso tras esta corrección

- No se modifica `PROJECT_STATE.json`.
- No se conecta `EvidenceHydrator`/`render_flow_document` a `legacy_documenter/cli/`/`main.py`.
- No se inicia R4.
- Sigue sin tocarse `exporters/technical_documentation_renderer.py` (ver sección 8, sin cambios por esta
  corrección).
- El verbo transaccional exacto (`BeginTrans` vs. `Commit` vs. `Rollback`) solo es recuperable cuando la
  evidencia extraída conserva la expresión de código original; si una futura ronda de extracción cambiara
  ese formato de evidencia, `_transaction_verb` seguiría degradando a `verb: None` en vez de fallar o adivinar
  — comportamiento ya cubierto por `test_confirmed_transaction_evidence_is_hydrated_with_its_verb` (el caso
  `DAO-TX-UNKNOWN`).

## 12. Segunda corrección: provenance completo tras deduplicación, y separación del ruido técnico

Instrucción directa del Líder Técnico, basada en la revisión humana de las tres muestras generadas por la
corrección de la sección 10, aplicada sobre esta misma ronda R3, sin iniciar R4: "Realiza una corrección final
y acotada de V4.3 R3 basada en la revisión humana de las muestras generadas."

### 12.1 Defecto 1: provenance de `PATH` deduplicados

Cuando `select_and_deduplicate_paths` (R2) fusiona varios `path_id` equivalentes en un solo grupo hidratado,
el campo original `source_index_pointer` apuntaba **únicamente** al primer `path_id` fusionado
(`group["path_ids"][0]`). Con dos o más `PATH` fusionados (`PATH-A`, `PATH-B`), tanto el registro hidratado
como el documento humano mostraban solo el puntero de `PATH-A`, perdiendo silenciosamente el de `PATH-B` —
exactamente el defecto que la muestra `flow_confirmed_terminal.md` (dos `PATH` deduplicados en un procedimiento
almacenado confirmado) dejó visible en la revisión humana.

**Corrección en `legacy_documenter/context/hydration.py`** (`_hydrate_path_group`): cada grupo de camino
hidratado ahora incluye también `path_provenance`, una lista ordenada y completa de
`{"path_id": <id>, "source_index_pointer": "index/functional_paths.json#<id>"}`, una entrada por cada
`path_id` fusionado, sin excepción. `source_index_pointer` (singular, primer `path_id`) se conserva sin
cambios por compatibilidad con quien ya lo consuma; `path_provenance` es la fuente completa y autoritativa.

**Corrección en `legacy_documenter/documentation/human_flow_documentation.py`** (`_section_7_evidence_and_traceability`):
la sección 7 ahora enumera, para cada `PATH`, una línea de procedencia por cada `path_id` fusionado
(`` `PATH-A` → `index/functional_paths.json#PATH-A` ``, `` `PATH-B` → `index/functional_paths.json#PATH-B` ``),
en vez de un único origen compartido.

Tests nuevos:
- `tests/test_v4_3_r2_evidence_hydration.py::HydrateFlowTests::test_deduplicated_path_group_preserves_a_source_index_pointer_for_every_merged_path_id`
  (dos `path_id` fusionados, dos punteros distintos, ninguno perdido) y
  `::test_undeduplicated_path_still_carries_its_own_path_provenance_entry` (un solo `path_id` no fusionado
  también produce su propia entrada de `path_provenance`, nunca una lista vacía).
- `tests/test_v4_3_r3_human_documentation.py::RenderFlowDocumentTests::test_deduplicated_path_shows_a_source_pointer_for_every_merged_path_id`
  y `::test_undeduplicated_path_also_shows_its_own_source_pointer`.

### 12.2 Defecto 2: `technical_noise_candidate` mezclado en "Servicios/capas"

La sección 4 original (`_section_4_services_and_layers`) listaba todos los invocadores de acceso a datos
(`class.method`) alcanzados por el flujo en una sola lista plana, sin distinguir los marcados
`technical_noise_candidate` (p. ej. `InitializeComponent`, `Dispose`, generados por el diseñador de WebForms,
V4.2 finding F-06) de los invocadores de negocio reales — exactamente el riesgo de lectura que la muestra
`flow_technical_noise_and_transaction.md` dejó visible: `CobDAO.InitializeComponent` aparecía junto a
`CobDAO.GuardarCheque`/`CobDAO.InsertarDetalleCheque` sin ninguna señal de que el primero no es lógica de
negocio.

**Corrección en `legacy_documenter/documentation/human_flow_documentation.py`** (`_section_4_services_and_layers`):
la sección 4 ahora separa los invocadores en dos grupos, calculados a partir del mismo `technical_noise_candidate`
que `EvidenceHydrator` ya computa (nunca re-derivado aquí por otro medio):

- la lista principal solo contiene invocadores de negocio (no marcados como ruido técnico);
- un invocador marcado como ruido técnico aparece en una subsección separada y explícitamente titulada
  `### Elementos técnicos/auxiliares (no lógica de negocio)`, con una nota que aclara que se conservan como
  evidencia (confianza y trazabilidad intactas) pero no deben interpretarse como servicios de negocio;
- ningún dato se elimina: el invocador de ruido técnico sigue apareciendo en la sección 3 (con su anotación
  ya existente), en la sección 6/7 si corresponde, y ahora también, por separado, en la sección 4 — nunca
  se retira de la evidencia técnica ni cambia su `confidence`.

Tests nuevos (`tests/test_v4_3_r3_human_documentation.py::RenderFlowDocumentTests`):
- `test_technical_noise_caller_is_separated_from_the_business_services_list`: `CobDAO.Actualizar` (negocio)
  aparece en la lista principal; `CobDAO.InitializeComponent` (ruido técnico) aparece únicamente en la
  subsección separada, nunca en la lista principal.
- `test_technical_noise_caller_still_fully_traceable_elsewhere`: el invocador de ruido técnico sigue siendo
  recuperable en el resto del documento (camino, `PATH`, `evidence_refs`, provenance).

### 12.3 Archivos modificados por esta segunda corrección

| Archivo | Tipo de cambio |
|---|---|
| `legacy_documenter/context/hydration.py` | Extendido: nuevo campo `path_provenance` por grupo de camino hidratado |
| `legacy_documenter/documentation/human_flow_documentation.py` | Extendido: sección 4 separa negocio/ruido técnico; sección 7 enumera provenance completo |
| `tests/test_v4_3_r2_evidence_hydration.py` | +2 tests |
| `tests/test_v4_3_r3_human_documentation.py` | +4 tests |
| `tests/test_v4_1_r0_maintainability_inventory.py` | Sin cambios: el crecimiento de línea de ambos módulos (`hydration.py` 290→304, `human_flow_documentation.py` 335→367) no cruzó ningún umbral de categoría de riesgo ni de pertenencia al top-20 de `largest_modules`/`largest_classes`/`documentation_candidates`; verificado ejecutando el módulo completo, 22/22 `OK` sin modificación |
| `docs/V4_3/samples/R3/flow_confirmed_terminal.md` | Regenerado: sección 7 ahora muestra `PATH-B01-1`/`PATH-B01-2` con su propio puntero cada uno |
| `docs/V4_3/samples/R3/flow_unresolved_no_terminal.md` | Regenerado (sin cambio de contenido sustantivo: un solo `PATH` no deduplicado, sin invocadores de ruido técnico) |
| `docs/V4_3/samples/R3/flow_technical_noise_and_transaction.md` | Regenerado: sección 4 separa `CobDAO.GuardarCheque`/`CobDAO.InsertarDetalleCheque` (negocio) de `CobDAO.InitializeComponent` (subsección de ruido técnico); sección 7 muestra el puntero propio de cada `PATH` |

Ningún archivo bajo `legacy_documenter/cli/`, `legacy_documenter/main.py`, `legacy_documenter/llm/`, ni
`PROJECT_STATE.json` fue modificado por esta corrección.

### 12.4 Conteos de tests tras la segunda corrección

- Antes de esta corrección: 1856 tests, 0 fallos, 132 skips.
- Después de esta corrección: **1862 tests** (1856 + 2 de `test_v4_3_r2_evidence_hydration.py` + 4 de
  `test_v4_3_r3_human_documentation.py`), **0 fallos**, **132 skips** (sin cambio).
- `python -m unittest discover -s tests` → `OK (skipped=132)`.
- `python -m unittest tests.test_v4_3_r2_evidence_hydration` → 24/24 `OK`.
- `python -m unittest tests.test_v4_3_r3_human_documentation` → 28/28 `OK`.
- `python -m unittest tests.test_v4_1_r0_maintainability_inventory` → 22/22 `OK` (sin modificación).

### 12.5 Fuera de alcance, incluso tras esta corrección

- No se modifica `PROJECT_STATE.json`.
- No se conecta `EvidenceHydrator`/`render_flow_document` a `legacy_documenter/cli/`/`main.py`.
- No se inicia R4.
- `source_index_pointer` (singular) no se elimina, por compatibilidad con cualquier consumidor existente de
  la forma hidratada de R2; queda documentado en el docstring del módulo como redundante frente a
  `path_provenance`, que es la fuente completa.
- La separación negocio/ruido técnico de la sección 4 es puramente de presentación (igual que
  `technical_noise_candidate` en general, ver R2 §3.2): no reclasifica evidencia, no cambia `confidence`, y
  no introduce un nuevo estado de confianza.

## 13. Revisión humana obligatoria (pendiente) — Gate para R4

Pendiente de aprobación por el Líder Técnico antes de iniciar R4:

- [ ] este resultado R3 (`docs/V4_3/V4_3_R3_HUMAN_DOCUMENTATION_RESULT.md`), incluidas las secciones 10 y 12
      de corrección;
- [ ] `legacy_documenter/documentation/human_flow_documentation.py` y su cobertura de las siete
      secciones/seis reglas del prompt (secciones 2–3);
- [ ] el diseño del parámetro opcional `interpretations`/`InvalidInterpretationError` como único punto de
      entrada de contenido `INTERPRETED`, sin implementar todavía ninguna llamada real de IA (sección 3.2,
      fila "IA solo aporta `INTERPRETED`");
- [ ] la decisión de alcance de no tocar `exporters/technical_documentation_renderer.py` en esta ronda
      (sección 8);
- [ ] la extensión de `EvidenceHydrator` (`legacy_documenter/context/hydration.py`) con evidencia
      transaccional/de tipo de operación de datos, y la garantía de que un procedimiento almacenado nunca se
      clasifica como escritura por su nombre (sección 10.1);
- [ ] la presentación determinista de esa evidencia en `human_flow_documentation.py`, sin inferencia narrativa
      (sección 10.2);
- [ ] `path_provenance` como fuente completa de procedencia tras deduplicación, y su presentación en la
      sección 7 (sección 12.1);
- [ ] la separación de `technical_noise_candidate` en una subsección propia de la sección 4, sin eliminar
      evidencia ni cambiar `confidence` (sección 12.2);
- [ ] las tres muestras Markdown regeneradas bajo `docs/V4_3/samples/R3/` (secciones 10.4 y 12.3);
- [ ] los archivos runtime modificados (secciones 6, 10.3 y 12.3), en particular la actualización mecánica
      (dos veces) del inventario de mantenibilidad V4.1-R0, y su ausencia de cambio tras la segunda corrección;
- [ ] los conteos de tests finales (sección 12.4): 1862 tests, 0 fallos, 132 skips.
