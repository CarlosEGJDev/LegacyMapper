# V4.3 — R2 — Evidence Hydration & Selection — Resultado

## Estado de esta ronda

`V4_3_R2_RESULT_IMPLEMENTED_PENDING_HUMAN_REVIEW`. A diferencia de R0/R1 (diseño), esta ronda implementa
código de producción: `legacy_documenter/context/hydration.py` y sus tests. El `Gate` de R1
("No avanzar a R2 sin revisión humana") quedó satisfecho: la aprobación de R1 ya fue realizada por el Líder
Técnico mediante la instrucción directa de ejecutar R2 a continuación de las cuatro aclaraciones ya
incorporadas al resultado de R1; no se requiere, ni se exige aquí, un documento de aprobación formal
separado de R1 (ver también sección 9). Esta ronda no cierra ni versiona V4.3 (sigue correspondiendo
exclusivamente a R9) y, por instrucción del prompt, R3 no se inicia hasta que este resultado sea revisado.

## 1. Objetivo

Implementar selección e hidratación determinista para que `FLOW`/`PATH`/`DAO`/`SP` no lleguen como IDs
desnudos, implementando el registro hidratado (`HYDRATED_RECORD`) fijado por el contrato de R1
(`docs/V4_3/V4_3_R1_CONSUMABLE_PROJECTION_CONTRACT_RESULT.md`).

## 2. Qué se implementó

- **`legacy_documenter/context/hydration.py`** (nuevo, 204 líneas): `EvidenceHydrator`, con
  `hydrate_flow(flow_id, ix)` como método público principal y `select_and_deduplicate_paths(paths)` como
  método público independiente y testeable por separado.
- **`legacy_documenter/context/__init__.py`** (modificado, solo docstring del paquete): se añadió la
  descripción de la nueva "etapa de hidratación" junto a las etapas de escritura/lectura ya documentadas, sin
  renombrar ni mover ningún módulo existente.
- **`tests/test_v4_3_r2_evidence_hydration.py`** (nuevo, 16 tests).
- **`tests/test_v4_1_r0_maintainability_inventory.py`** (modificado): actualización mecánica del inventario de
  mantenibilidad congelado (V4.1-R0) para reflejar el nuevo módulo de producción — ver sección 6.

`EvidenceHydrator` es una función pura sobre el mismo `ix` (diccionario de índices) que
`system_context_builder.SystemContextBuilder` ya consume: no lee ningún archivo, no llama a ningún
proveedor de IA, no borra ni muta ningún artefacto existente, y no está conectado a
`legacy_documenter/cli/` ni a `legacy_documenter/main.py` — es una capacidad a la que un futuro llamador
(R3/R4/R5/R6) se conecta explícitamente, no un paso que el pipeline actual ejecute automáticamente.

## 3. Cobertura de requisitos

| Requisito del prompt | Cómo se satisface |
|---|---|
| Usar exclusivamente evidencia ya generada | `EvidenceHydrator` solo lee campos de `ix` (`functional_flows`, `functional_paths`, `entry_points`, `data_access`, `stored_procedures`, `sql_operations`, `data_parameters`); ningún campo del registro hidratado se inventa — cada uno se traza a un índice existente (ver `2.1` del resultado de R1). |
| Hidratar `FLOW` con entry point, evento, handler, proyectos/capas, paths relevantes, terminales, SP/SQL/DAO, parámetros disponibles, confianza, unresolved y provenance | `hydrate_flow()` produce exactamente estos campos: `entry_point` (`id`/`webform`/`event`/`handler`/`start_method`), `projects`, `paths`, `terminals` (`stored_procedures`/`sql_operations`/`unresolved_boundaries` con nombre resuelto), `parameters` (por invocador realmente alcanzado), `confidence`, `unresolved` (lista de `path_id`), `provenance` (`source_indexes` + `flow_source_index_pointer`). |
| Priorizar caminos confirmados hacia terminales | `select_and_deduplicate_paths()` ordena los grupos por `CONFIDENCE_ORDER` (`confirmed` < `inferred` < `unresolved`) antes que por `path_id`; ver `test_confirmed_paths_are_prioritized_before_unresolved`. |
| Conservar unresolved significativos | Ningún camino con `terminal_type=unresolved_boundary` se descarta; aparece tanto en `paths` como en la lista `unresolved`. Ver `test_significant_unresolved_path_is_preserved_alongside_a_confirmed_terminal` y `test_flow_without_confirmed_terminal_preserves_unresolved_without_inventing_a_terminal` (caso D de R0: sin terminal confirmado, la incertidumbre se declara, no se inventa un terminal). |
| Deduplicar cadenas equivalentes | `select_and_deduplicate_paths()` agrupa por la firma `(terminal_type, terminal_target, nodes)`; caminos equivalentes se fusionan en un solo registro que conserva **todos** sus `path_id` y toda su `evidence_refs` (nunca se pierde identidad ni evidencia). Ver `test_equivalent_chains_are_merged_without_losing_path_ids_or_evidence`. |
| No usar LLM para seleccionar/hidratar | El módulo no importa `legacy_documenter.llm` ni ningún submódulo con `llm` en el nombre — verificado por AST, no por texto, en `test_hydration_module_does_not_import_llm` (una comprobación textual ingenua daba un falso positivo porque el propio docstring del módulo *menciona* `legacy_documenter.llm` al explicar que no lo usa; se corrigió a un escaneo AST de imports reales). |
| No borrar evidencia upstream | El módulo nunca escribe a disco (`test_hydration_never_writes_to_disk` comprueba ausencia de `open(`/`write_text`/`Path(`/`os.`/red de E/S en el código fuente) y nunca muta el `ix` recibido (todas las estructuras intermedias son nuevas). |
| Clasificar conservadoramente ruido técnico/infraestructura sin convertirlo en negocio | `TECHNICAL_NOISE_METHOD_NAMES` (`InitializeComponent`, `Dispose`, `InitializeCulture` — nombres de método generados por el diseñador de WebForms, el mismo patrón del hallazgo `F-06`) solo añade la bandera booleana `technical_noise_candidate` a un nodo/terminal; nunca elimina el nodo, nunca cambia su `confidence`/`resolved_name`, y nunca lo reclasifica como significado de negocio. Ver `test_technical_noise_is_flagged_conservatively_without_being_dropped_or_promoted`. |

### 3.1 Aclaración: identidad tras la deduplicación

Cuando `select_and_deduplicate_paths()` fusiona varias cadenas equivalentes, la forma hidratada resultante
conserva explícitamente, sin excepción, **todos** los `path_id` originales fusionados (campo `path_ids`,
siempre una lista, nunca un único id aunque la fusión provenga de un solo `PATH`) y **todos** sus
`evidence_refs` originales (unión, no muestra ni primero-gana). Ninguna ronda posterior de V4.3 (R3–R6) ni
ningún consumidor de `consumer_projection` puede tratar un registro deduplicado como si hubiera existido un
único `PATH` original: el hecho de que dos o más `PATH` deterministas, generados de forma independiente por
el pipeline V1–V3, hayan producido la misma cadena de evidencia es en sí mismo información — nunca se
colapsa silenciosamente en una identidad nueva e inventada. Esta lista completa de `path_ids` (y de
`evidence_refs`) es precisamente lo que sostiene la trazabilidad exigida por R1 y lo que `consumer_projection`
(R6) deberá exponer sin resumir: un consumidor que necesite saber cuántos `PATH` deterministas distintos
sustentan un registro hidratado, o a qué evidencia exacta remite cada uno, encuentra la respuesta en
`path_ids`/`evidence_refs`, nunca en un conteo aproximado ni en un solo id representativo.

### 3.2 Aclaración: alcance de `technical_noise_candidate`

`technical_noise_candidate` es exclusivamente una clasificación conservadora **de presentación**, no una
clasificación de evidencia. En concreto:

- Nunca elimina evidencia: el nodo o terminal marcado permanece en `nodes`/`terminals` con exactamente los
  mismos campos que tendría si no estuviera marcado.
- No modifica `confidence`, `terminal_type`, `resolved_name` ni ningún campo de trazabilidad
  (`path_ids`, `evidence_refs`, `source_index_pointer`): la bandera se añade junto a esos campos, nunca los
  sustituye ni los condiciona.
- Es una señal para una etapa de presentación futura, no para esta ronda: la documentación humana (R3) podrá
  optar por ocultar o relegar estos elementos en la vista principal (resumen-antes-de-detalle, sección 5.1
  del resultado de R1), pero deberán seguir disponibles en el detalle técnico completo — nunca se eliminan
  del todo, solo se pueden des-enfatizar en la primera lectura.
- `TECHNICAL_NOISE_METHOD_NAMES` (sección 3, fila anterior) es una lista inicial, pequeña y deliberadamente
  conservadora, no una taxonomía exhaustiva de ruido técnico/infraestructura. Que un nombre de método no
  esté en esa lista no implica que sea significado de negocio, y que la lista crezca en una ronda futura no
  es una ampliación de alcance de R2 sino el mismo mecanismo ya definido aquí, aplicado a más nombres.

## 4. Tests obligatorios — mapeo

| Categoría exigida por el prompt | Test(s) |
|---|---|
| Selección | `test_confirmed_paths_are_prioritized_before_unresolved`, `test_deterministic_ordering` |
| Hidratación | `test_flow_with_confirmed_stored_procedure_terminal_is_hydrated_with_resolved_names`, `test_available_parameters_are_resolved_for_reached_callers_only` |
| Deduplicación | `test_equivalent_chains_are_merged_without_losing_path_ids_or_evidence`, `test_distinct_chains_are_not_merged` |
| Trazabilidad | `test_traceability_back_to_original_ids_and_indexes` |
| Flujo con DB/SP | `test_flow_with_confirmed_stored_procedure_terminal_is_hydrated_with_resolved_names` (caso B de R0: terminales confirmados) |
| Flujo sin terminal | `test_flow_without_confirmed_terminal_preserves_unresolved_without_inventing_a_terminal` (caso D de R0) |
| Unresolved | `test_significant_unresolved_path_is_preserved_alongside_a_confirmed_terminal` |
| Independencia runtime | `test_hydration_module_does_not_import_llm`, `test_hydration_is_not_wired_into_the_cli_pipeline`, `test_hydration_never_writes_to_disk` |

Adicionalmente: `test_unknown_flow_raises` (entrada inválida, nunca fabrica un flujo inexistente),
`test_deterministic_across_repeated_calls` y `test_no_llm_output_leaks_into_a_hydrated_record`
(ninguna cadena `INTERPRETED` puede aparecer en un registro hidratado, alineado con la regla de R1 de que
`AI_HYDRATED_PROJECTION` no transporta interpretación de IA por defecto).

## 5. Schemas modificados

Ninguno de los schemas/artefactos existentes cambió: `SYSTEM_CONTEXT.json`, `FUNCTIONAL_FLOWS.json`,
`TRACEABILITY.json`, `ARCHITECTURE_GRAPH.json`, el sobre de `ContextResolver`/`ContextComposer`, y los
contratos de `knowledge/projection/`/`knowledge/plugin_projection/` permanecen intactos — coherente con la
compatibilidad V4.2 fijada en R1 §7. Lo único nuevo es la forma en memoria que `hydrate_flow()` devuelve
(un `dict` con las claves descritas en la sección 2), que implementa, sin desviarse, la forma cerrada de
`HydratedPathRecord` fijada en R1 §2.1, extendida al nivel `FLOW` según los requisitos de este prompt. Esta
forma aún no se ha serializado como el contrato `AI_HYDRATED_PROJECTION 1.0` completo (versión, sobre,
presupuesto): eso corresponde a R5/R6, no a R2.

## 6. Archivos runtime modificados

| Archivo | Tipo de cambio |
|---|---|
| `legacy_documenter/context/hydration.py` | Nuevo módulo de producción |
| `legacy_documenter/context/__init__.py` | Docstring del paquete ampliado (aditivo, sin cambio de comportamiento) |
| `tests/test_v4_3_r2_evidence_hydration.py` | Nuevo archivo de tests (16 tests) |
| `tests/test_v4_1_r0_maintainability_inventory.py` | Actualización mecánica del inventario congelado V4.1-R0: `production_python_module_count` 169→170, `legacy_documenter/context/hydration.py` añadido al conjunto de rutas nuevas esperadas, +1 en el recuento `MEDIUM` de `risk_summary`, `EvidenceHydrator` añadido a `largest_classes` (desplazando `WebEventExtractor` del top-N, mismo efecto de ranking ya documentado para rondas anteriores), y `dependency_findings.module_count` +26→+27. Ninguna aserción se debilitó ni se eliminó; se siguió exactamente el mismo patrón incremental que cada ronda previa (V4.1-R1 … V4.2-R8) ya aplicó a este mismo test. |

Ningún archivo bajo `legacy_documenter/cli/`, `legacy_documenter/main.py`, `legacy_documenter/llm/`, ni
`PROJECT_STATE.json` fue modificado.

## 7. Conteos de tests

- Antes de esta ronda (V4.2 baseline registrado en `PROJECT_STATE.json`): 1810 tests, 0 fallos, 0 errores,
  132 skips esperados.
- Después de esta ronda: **1826 tests** (1810 + 16 nuevos de `test_v4_3_r2_evidence_hydration.py`),
  **0 fallos**, **132 skips** (sin cambio — ningún skip nuevo ni eliminado).
- `python -m unittest discover -s tests` → `OK (skipped=132)`.
- El módulo dedicado (`python -m unittest tests.test_v4_3_r2_evidence_hydration`) → 16/16 `OK`.
- El módulo de inventario de mantenibilidad actualizado (`python -m unittest tests.test_v4_1_r0_maintainability_inventory`) → 22/22 `OK`.

`PROJECT_STATE.json` no se modificó; sus campos `tests`/`test_failures`/`test_errors`/`expected_fresh_clone_skips`
(`1810`/`0`/`0`/`132`) siguen describiendo el baseline de V4.2, no este conteo post-R2. Actualizar esos
campos, si corresponde, queda para la ronda de cierre/versionado de V4.3 (R9), no para R2.

## 8. Fuera de alcance de esta ronda

- No se serializa aún el contrato `AI_HYDRATED_PROJECTION 1.0` completo (sobre, presupuesto, `package_id`
  con prefijo `AIP-`) — corresponde a R5/R6.
- No se genera documentación humana en español a partir de un registro hidratado — corresponde a R3.
- No se implementa particionamiento/escalado sobre registros hidratados — corresponde a R4.
- No se conecta `EvidenceHydrator` a `legacy_documenter/cli/`/`main.py` ni a ningún flujo de ejecución
  automático — deliberado (ver sección 2 e "independencia runtime" en la tabla de tests).
- No se modifica `PROJECT_STATE.json`.
- No se cierra ni versiona V4.3 (sigue correspondiendo exclusivamente a R9).

## 9. Revisión humana obligatoria (pendiente) — Gate para R3

La aprobación de R1 (`docs/V4_3/V4_3_R1_CONSUMABLE_PROJECTION_CONTRACT_RESULT.md`) ya fue realizada por el
Líder Técnico — mediante la instrucción directa de ejecutar R2 a continuación de las cuatro aclaraciones
incorporadas a ese resultado — y no se requiere ni se exige un documento de aprobación formal separado de
R1 para continuar. Queda registrado aquí como el estado vigente de R1, no como un punto abierto de esta
revisión.

Pendiente de aprobación por el Líder Técnico antes de iniciar R3:

- [ ] este resultado R2 (`docs/V4_3/V4_3_R2_EVIDENCE_HYDRATION_AND_SELECTION_RESULT.md`);
- [ ] `legacy_documenter/context/hydration.py` (schemas/campos modificados: ninguno existente, solo la nueva
      forma en memoria descrita en la sección 5);
- [ ] la conservación de `path_ids`/`evidence_refs` completos tras la deduplicación y su disponibilidad para
      trazabilidad/`consumer_projection` (sección 3.1);
- [ ] el alcance puramente presentacional de `technical_noise_candidate`, incluyendo que su lista de nombres
      no es una taxonomía exhaustiva (sección 3.2);
- [ ] los archivos runtime modificados (sección 6), en particular la actualización mecánica del inventario de
      mantenibilidad V4.1-R0;
- [ ] los conteos de tests (sección 7): 1826 tests, 0 fallos, 132 skips.
