# V4.3 — R8 — Correcciones posteriores al piloto real — Resultado

## Estado de esta ronda

`V4_3_READY_FOR_CLOSURE`. Esta ronda corrige los tres hallazgos reportados por el piloto externo real
(P-01, P-02, P-03) contra una distribución limpia de V4.3-R7 sobre un repositorio legacy real de gran escala
(`full` exit 0, `AI requested/invoked: False`, 905 archivos de salida, `consumer_projection` completo con
`flow_count=12642`/`path_count=170020`/`partition_count=26`). Como en R2–R7, esta ronda implementa código de
producción (correcciones reales, secciones 2–4) más su cobertura de test sintética; no accede al repositorio
IST real ni a `C:\PruebasLegacyMapper` (`AGENTS.md` "Legacy Source Repository"; el prompt de esta ronda:
"No asumir acceso directo a `C:\PruebasLegacyMapper`"). Ningún output/código/documento real del piloto se
incorpora a este repositorio -- únicamente los hallazgos, anonimizados y generalizados, reproducidos con
fixtures sintéticos (`tests/test_v4_3_r8_external_pilot_corrections.py`).

`REAL_AI_RUNTIME_CALL_ALLOWED=false` sigue vigente: esta ronda no toca `legacy_documenter.llm`ni
`legacy_documenter.orchestration` en absoluto -- los tres hallazgos son puramente deterministas
(agrupación/particionado y presentación de documentación humana).

## 1. Objetivo

`prompts/V4_3/V4_3_R8_EXTERNAL_PILOT_CORRECTIONS.md`: corregir los problemas reales que el piloto externo
encontró contra V4.3-R7, clasificarlos según la matriz obligatoria, y dejar V4.3 lista para cierre (R9), sin
expandir su alcance hacia agnosticismo tecnológico/provider, Plugin Runtime, o V5.

## 2. Hallazgo P-01 — Escalado de partición humana

**Síntoma real**: `documentation/HUMAN_DOCUMENTATION.md` agrupó 12642 flujos en 162 grupos; uno de ellos
(`proyectos`) concentró 2983 flujos porque la regla de agrupación (V4.3-R4, `webform_owner_group_key`) toma el
primer segmento de carpeta del WebForm, y para paths como
`proyectos\WebApplication1\WebApplication1\WebWPF\...` o
`proyectos\slnInformesSubsidios\Backup\WebInformesSubsidios\...` ese primer segmento es siempre la carpeta
contenedora genérica `proyectos`, nunca la unidad funcional/proyecto real. La partición resultante
(`documentation/flujos_humanos/proyectos.md`) alcanzó ~45 MB/340000 líneas.

**Clasificación**: `PROJECTION_GAP` (la proyección de agrupación determinista carecía de la señal estructural
correcta -- el proyecto `.vbproj` real ya estaba disponible en el índice determinista, pero
`human_documentation_scaling` nunca la leía) + `DOCUMENTATION_USABILITY` (el archivo resultante, aunque
correcto, dejó de ser consumible por su tamaño).

**Corrección, en dos partes**:

1. **Agrupación por proyecto propietario real, no por carpeta contenedora.** `EvidenceHydrator.hydrate_flow`
   (`legacy_documenter/context/hydration.py`) ahora hidrata un campo adicional, aditivo, en `entry_point`:
   `project` -- leído verbatim de `entry_points.json`, que ya lo resuelve estructuralmente
   (`WebEntryResolver`, vía el símbolo de código-behind del WebForm que matchea exactamente un `.vbproj` por
   sus `compile_items`; nunca una heurística basada en nombres). `owning_project_group_key`
   (`legacy_documenter/exporters/_documentation_partitioning.py`, nueva función) deriva la clave de grupo del
   stem de ese `.vbproj` cuando existe, y solo cae de vuelta al `webform_owner_group_key` de tres niveles
   (V4.3-R4, sin modificar) cuando no hay evidencia de proyecto. `flow_group_key`
   (`legacy_documenter/documentation/human_documentation_scaling.py`) delega en la nueva función. Resultado:
   dos WebForms bajo el mismo contenedor `proyectos\...\` pero de proyectos `.vbproj` distintos ya no colapsan
   en una única clave `"proyectos"`.
2. **Segunda capa de particionado determinista dentro de un mismo owner/proyecto.** Incluso con agrupación
   correcta, un solo proyecto real puede seguir concentrando miles de flujos. `render_human_documentation_partitions`
   ahora aplica un segundo umbral, `MAX_FLOWS_PER_GROUP_FILE = 500` (mismo valor que
   `context.consumer_projection.DEFAULT_PARTITION_SIZE`, elegido por consistencia, no por acoplamiento entre
   ambos módulos): un grupo con más de 500 flujos deja de producir `<owner>.md` con el detalle completo;
   `<owner>.md` se convierte en un pequeño sub-índice (conteo, número de particiones, enlaces) y el detalle
   completo se reparte en `<owner>-part-000001.md`, `<owner>-part-000002.md`, ... -- slices ordinales,
   deterministas, del mismo orden estable ya usado (`_sort_key`), nunca una sub-agrupación narrativa. Un
   grupo de 500 flujos o menos es completamente inafectado: sigue produciendo `<owner>.md` con el detalle
   completo, igual que en V4.3-R4/R7.

**No se tocó** `EvidenceHydrator`'s selección/deduplicación de paths, ni ningún otro campo de la evidencia
exhaustiva -- solo se añadió un campo (`project`) y se cambió la política de agrupación/particionado de la capa
de presentación de documentación humana.

**Tests**: `OwningProjectGroupKeyTests` (7), `SecondLayerSubPartitioningTests` (7) --
`tests/test_v4_3_r8_external_pilot_corrections.py` -- cubren: colapso de contenedor genérico corregido, dos
proyectos distintos bajo el mismo contenedor ya no comparten clave, fallback intacto cuando no hay evidencia de
proyecto, grupo en el umbral exacto sigue siendo un solo archivo, grupo por encima del umbral produce sub-índice
+ partes numeradas, ninguna pérdida/truncamiento, ninguna duplicación entre partes, unión completa y exacta,
determinismo ante reordenamiento de entrada, y enlace de vuelta al índice superior desde cada parte.

## 3. Hallazgo P-02 — Verbosidad de flujo humano

**Síntoma real**: `FLOW-0343552547` (`webCobMorosidad\CobLiquidacionDeudaPrev.ascx` → `Load` → `Page_Load`,
exactamente el caso A de la matriz de aceptación de R0) tiene 94 paths. La documentación generada mostraba
primero los 94 paths casi completos -- incluyendo decenas de elementos de bajo valor humano
(`DesplegarError`, `Left`, `values()`, `BeginTrans`/`Commit`/`Rollback`/`Close`, `SetCheckBox`,
`SetVisibleColumns`, `LimpiaNullDataset`, `parametrosURL`, etc.) -- antes de volver a listar incertidumbres y
finalmente repetir la trazabilidad PATH por PATH. La evidencia era correcta; la proyección dejó de ser
consumible como documentación humana.

**Clasificación**: `DOCUMENTATION_USABILITY` (orden de presentación, no un defecto de evidencia).

**Corrección**: `legacy_documenter/documentation/human_flow_documentation.py::render_flow_document` es ahora
summary-first. Nuevo orden de secciones (renumeradas 1–8, ninguna eliminada):

| # | Sección | Contenido |
|---|---|---|
| 1 | Qué es y dónde está | Sin cambios (V4.3-R3) |
| 2 | Evento/entrada inicial | Sin cambios (V4.3-R3) |
| 3 | **Resumen funcional determinista** (nueva) | Conteos: total de caminos, confirmados principales, con límite no resuelto, técnicos/infraestructura -- ningún nombre resuelto se vuelca aquí, solo números |
| 4 | **Rutas confirmadas principales** (nueva) | Solo caminos `confirmed`, con terminal resuelto (SP/SQL), no técnicos -- la vista principal que un humano lee primero |
| 5 | Servicios/capas | Antes sección 4 (V4.3-R3), sin cambio de contenido/lógica, solo renumerada |
| 6 | Datos/SP/SQL | Antes sección 5 (V4.3-R3), sin cambio de contenido/lógica, solo renumerada |
| 7 | Qué queda no resuelto | Antes sección 6; ahora también separa infraestructura de lo funcionalmente relevante (ver P-03) |
| 8 | **Evidencia técnica detallada / trazabilidad** (fusión) | Todo lo que antes era la sección 3 (todos los caminos, sin filtrar) + toda la antigua sección 7 (trazabilidad `PATH`/`evidence_refs`/`provenance`) -- el detalle exhaustivo único, nunca duplicado en las secciones 3/4 de arriba |

Nada se elimina ni se trunca: cada camino (incluidos los técnicos/de infraestructura) sigue descrito por
completo en la sección 8, exactamente como antes lo estaba en la antigua sección 3; solo cambia el orden en
que un lector los encuentra. `Límites de esta documentación` conserva su posición al final (antes de
`INTERPRETED`).

**Tests**: `SummaryFirstOrderingTests` (5) -- verifica el orden de aparición de los ocho encabezados, que el
resumen (sección 3) no vuelca nombres resueltos, que la sección 4 solo muestra caminos de negocio confirmados,
que la sección 8 conserva cada camino (incluido el ruido técnico), y que ningún marcador de contenido
desaparece del documento completo. Los tests preexistentes de V4.3-R3/R4 se actualizaron para la renumeración
(nunca debilitados -- ver sección 6).

## 4. Hallazgo P-03 — Ruido técnico vs. incertidumbre

**Síntoma real**: en el mismo flujo, `dbc.BeginTrans()`/`dbc.Commit()`/`dbc.Rollback()`/`dbc.Close()` aparecen
correctamente como evidencia transaccional confirmada (sección 6/Datos-SP-SQL) pero **también** aparecen,
simultáneamente, como límites no resueltos (su propio path individual termina en `unresolved_boundary` porque
la cadena no continúa más allá de la llamada de infraestructura) -- mezclados, sin distinción, con límites
genuinamente inciertos desde el punto de vista funcional (p. ej. `UnknownHelper.Execute`).

**Clasificación**: `DOCUMENTATION_USABILITY` (presentación, no evidencia). Explícitamente **no** es
`BUG_V4_3`: el `terminal_type == unresolved_boundary` es correcto (la cadena real no continúa más allá de esa
llamada), y `EvidenceHydrator` nunca debe inferir heurísticamente qué hay "después" de una llamada de
infraestructura sin evidencia -- degradarlo a "resuelto" sería exactamente la promoción de `unresolved` a
`confirmed` sin respaldo determinista que `AGENTS.md` prohíbe.

**Corrección, estrictamente presentation-only**: `human_flow_documentation.py` añade una lista de nombres de
método, local a este renderer (`PRESENTATION_TECHNICAL_METHOD_NAMES`), deliberadamente **separada** de
`EvidenceHydrator.TECHNICAL_NOISE_METHOD_NAMES` (V4.3-R3, sin modificar) -- más amplia
(`BeginTrans`/`BeginTransaction`/`Commit`/`Rollback`/`Close`/`Open`/`DesplegarError`/`Left`/`values`/
`SetCheckBox`/`SetVisibleColumns`/`LimpiaNullDataset`/`parametrosURL`, además de las tres ya conocidas). La
sección 7 (`Qué queda no resuelto`) ahora separa cada límite no resuelto en dos subsecciones según si su
nombre resuelto coincide con esa lista:

- **Principal**: límites no resueltos funcionalmente relevantes (sin cambios de comportamiento salvo que ahora
  muestra el nombre resuelto cuando existe, en vez de solo el id bruto).
- **`### Límites técnicos/infraestructura (no resueltos, de naturaleza conocida)`**: los reconocidos por nombre
  como infraestructura/ciclo de vida -- se conservan, con su trazabilidad intacta, pero relegados a esta
  subsección secundaria claramente etiquetada.

La sección 3 (resumen) y la sección 4 (rutas principales) usan la misma clasificación local para decidir qué
caminos son "principales" (sección 4) frente a "técnicos/infraestructura" (deferidos a la sección 8) --
respuesta unificada tanto para P-02 como para P-03, sin dos mecanismos de clasificación paralelos.

**Invariantes verificados, no solo asumidos**: ningún test de esta ronda cambia `confidence`,
`technical_noise_candidate`, o `terminal_type` en el registro hidratado -- `TechnicalNoiseVsUncertaintyTests
.test_infrastructure_boundaries_are_still_declared_unresolved_never_promoted_to_confirmed` verifica
directamente el registro hidratado (no solo la prosa renderizada) para impedir que un cambio futuro promueva
silenciosamente estos límites a confirmados.

**Tests**: `TechnicalNoiseVsUncertaintyTests` (5) -- límite funcionalmente relevante permanece en la lista
principal; límites de infraestructura conocida en su propia subsección; nunca mezclados; nunca promovidos a
confirmado (verificado sobre el registro hidratado); trazabilidad completa preservada.

### 4.1 Corrección de seguimiento (revisión humana de las muestras R8) — clasificación por nombre de terminal era insuficiente cuando el terminal es opaco

**Síntoma real, encontrado al revisar `docs/V4_3/samples/R8/flujo_sintetico_verboso_summary_first.md`**: la
corrección de la sección 4 clasifica un límite no resuelto como "técnico/infraestructura" mirando únicamente
`terminal.resolved_name`. Pero `PATH-NOISE-1`/`PATH-NOISE-2` (los dos caminos cuyo único nodo es
`Formulario.DesplegarError`/`Formulario.LimpiaNullDataset`) terminan en un `terminal_target` opaco
(`unknown_noise_1`/`unknown_noise_2`) que no resuelve a ningún registro conocido -- `resolved_name` es `None`.
Como resultado, antes de esta corrección de seguimiento:

- **Sección 5 (Servicios/capas)** mostraba `Formulario.DesplegarError`/`Formulario.LimpiaNullDataset` en la
  lista principal de servicios de negocio -- porque esa sección seguía usando exclusivamente el flag
  `technical_noise_candidate` de `EvidenceHydrator` (V4.3-R3, deliberadamente estrecho:
  `InitializeComponent`/`Dispose`/`InitializeCulture` solamente), nunca la lista presentation-only más amplia
  que la sección 4/7 ya usaban.
- **Sección 7 (Qué queda no resuelto)** mostraba `unknown_noise_1`/`unknown_noise_2` en la lista principal de
  incertidumbre funcional -- porque la clasificación de un límite dependía solo de `terminal.resolved_name`
  (`None` en ambos casos), nunca de los nodos del propio camino que llega a ese límite.

**Clasificación**: `DOCUMENTATION_USABILITY` (mismo tipo que P-03; sigue sin ser `BUG_V4_3` -- ningún dato
determinista es incorrecto, solo la superficie de presentación no consultaba toda la evidencia ya disponible).

**Corrección, sigue siendo estrictamente presentation-only**:

- `_section_5_services_and_layers` ahora también marca como ruido un caller cuyo nombre coincide con
  `PRESENTATION_TECHNICAL_METHOD_NAMES` (la misma lista de la sección 4/7), no solo `technical_noise_candidate`
  -- unifica la clasificación en todo el documento en vez de mantener dos criterios distintos según la
  sección.
- `_section_7_unresolved` gana `_unresolved_boundary_node_callers`: para cada `path` cuyo
  `terminal_type == "unresolved_boundary"`, si su propio `terminal.resolved_name` es opaco (`None`) pero
  alguno de sus `nodes` es una llamada `data_access` cuyo nombre coincide con
  `PRESENTATION_TECHNICAL_METHOD_NAMES`, ese límite se relega a la subsección técnica/infraestructura -- **el
  id real del terminal se conserva sin cambios** (`unknown_noise_1`/`unknown_noise_2`, nunca inventado), y se
  añade una anotación de transparencia ("ruido técnico detectado en el camino vía `Formulario.DesplegarError`")
  explicando por qué, sin editar ni sustituir el id.
- `UnknownHelper.ProcesarAlgo` (terminal opaco, camino sin nodos) permanece en la lista principal: no hay
  evidencia de nodo que lo reclasifique, exactamente el comportamiento requerido (requisito 3).
- `dbc.BeginTrans`/`dbc.Commit` siguen clasificándose exactamente igual que en la sección 4 original (su propio
  `terminal.resolved_name` ya coincide directamente; no dependen del nuevo mecanismo de nodos) -- requisito 4.
- Sección 8 no se tocó: sigue mostrando el 100% de los caminos, sin excepción -- requisito 5.
- Ningún `confidence`/`terminal_type`/`technical_noise_candidate` cambia, y ningún `unresolved` se promueve a
  `confirmed` -- requisito 6, verificado explícitamente por
  `TechnicalNoiseVsUncertaintyTests.test_infrastructure_boundaries_are_still_declared_unresolved_never_promoted_to_confirmed`
  (sin cambios) y por el nuevo `OpaqueTerminalNodeEvidenceTests`.

**Tests nuevos** (`OpaqueTerminalNodeEvidenceTests`, 5, en `tests/test_v4_3_r8_external_pilot_corrections.py`):
terminal opaco + nodo `DesplegarError` clasifica infraestructura; terminal opaco + nodo `LimpiaNullDataset`
clasifica infraestructura; terminal opaco + nodo funcional genuinamente desconocido
(`Planilla.CalcularSaldoPendiente`, fixture nueva `_opaque_terminal_with_unknown_functional_node_ix`) **no**
se reclasifica como técnico, ni en la sección 5 ni en la 7; la lista principal de servicios (sección 5) excluye
todo elemento `PRESENTATION_TECHNICAL_METHOD_NAMES`; la sección 8 conserva el 100% de los caminos reclasificados
tras la corrección.

## 5. Matriz de clasificación (obligatoria, `prompts/V4_3/V4_3_R8_EXTERNAL_PILOT_CORRECTIONS.md`)

| Caso | Flujo | Hallazgo(s) aplicable(s) | Clasificación |
|---|---|---|---|
| A | `webCobMorosidad\CobLiquidacionDeudaPrev.ascx` → `Load` → `Page_Load` | P-02 (verbosidad, 94 paths), P-03 (ruido técnico vs. incertidumbre, mismo flujo real) | `DOCUMENTATION_USABILITY` (ambos) |
| B | `webCobMorosidad\cobCargaArcIntRea.ascx` → `Click` → `btnCargar_Click` | Ninguno de los tres hallazgos reportados afecta a este caso -- sus terminales confirmados (SP/DAO) ya se presentan correctamente en la sección 4 (rutas confirmadas principales) tras la corrección de P-02 | `EXPECTED_LIMITATION` (sin cambio necesario; cubierto por la regresión existente de V4.3-R0/R2/R3) |
| C | `webCobMorosidad\cobChqInsRen.ascx` → `Click` → `HypGuardar_Click` | Ninguno de los tres directamente; su evidencia transaccional (`BeginTrans`/`Commit` vía DAO) ya se muestra en la sección 6 (Datos/SP/SQL) como evidencia confirmada -- si esa misma llamada apareciera también como límite no resuelto en un caso real, P-03 la separaría igual que en el caso A | `EXPECTED_LIMITATION` |
| D | `webCobMorosidad\CobConsultaTransferencia.ascx` → `Load` → `Page_Load` (sin terminal confirmado) | P-01 indirectamente (si su WebForm cae bajo un contenedor genérico de muchos flujos, ahora agrupa por proyecto real en vez de por el contenedor) | `PROJECTION_GAP` (P-01) cuando aplica; de lo contrario `EXPECTED_LIMITATION` -- la ausencia de terminal confirmado sigue siendo una declaración explícita de incertidumbre, no oculta (V4.3-R0 criterio de aceptación, sin cambios) |

Ningún caso de la matriz se clasificó como `BUG_V4_3` (no hay evidencia determinista incorrecta),
`AI_CONTEXT_GAP` (ningún hallazgo involucra `ai_projection`/`consumer_projection`/AI), `UPSTREAM_ANALYSIS_GAP`
(ninguna extracción/resolución previa a la documentación humana resultó incorrecta), o `DEFER_V5` (los tres
hallazgos son correcciones deterministas dentro del alcance ya aprobado de V4.3, no requieren Plugin
Runtime/agnosticismo de provider).

## 6. Tests

`tests/test_v4_3_r8_external_pilot_corrections.py` (**30 tests, todos en verde**):

| Clase | Tests | Cubre |
|---|---|---|
| `OwningProjectGroupKeyTests` | 7 | Agrupación por `.vbproj` real en vez del contenedor genérico; dos proyectos distintos bajo el mismo contenedor ya no colisionan; fallback intacto sin evidencia de proyecto; `flow_group_key`/`EvidenceHydrator.hydrate_flow` exponen y usan el nuevo campo `project` |
| `SecondLayerSubPartitioningTests` | 7 | Umbral exacto sigue siendo un archivo; por encima del umbral produce sub-índice + partes; sin pérdida/truncamiento; sin duplicación; unión completa; determinismo; enlace de vuelta al índice |
| `SummaryFirstOrderingTests` | 5 | Orden de las ocho secciones; resumen sin nombres resueltos; sección 4 solo negocio confirmado; sección 8 conserva todo, incluido el ruido; nada desaparece del documento completo |
| `TechnicalNoiseVsUncertaintyTests` | 5 | Límite funcional en la lista principal; infraestructura en subsección separada; nunca mezclados; nunca promovidos a confirmado (registro hidratado); trazabilidad completa |
| `OpaqueTerminalNodeEvidenceTests` | 5 | **Nueva (sección 4.1)**: terminal opaco + nodo `DesplegarError`/`LimpiaNullDataset` clasifica infraestructura; terminal opaco + nodo funcional desconocido NO se reclasifica como técnico; sección 5 (servicios/capas) excluye todo elemento `PRESENTATION_TECHNICAL_METHOD_NAMES` de la lista principal; sección 8 conserva el 100% de los caminos reclasificados |
| `EvidencePreservationTests` | 1 | `path_id`/`evidence_ref` sobreviven hidratación y render sin pérdida ni reescritura |

Tests preexistentes actualizados para la renumeración de secciones (nunca debilitados, solo los límites de
`split()` movidos a los nuevos números de sección):
`tests/test_v4_3_r3_human_documentation.py` (encabezados esperados, límites de sección para las aserciones de
"sección 3"/"sección 4"/"sección 5"/"sección 7" ya existentes), `tests/test_v4_3_r4_scaling_and_partitioning.py`
(dos aserciones de encabezado en `NavigationIndexTests`/`PartitionDocumentTests`). Un campo aditivo
(`entry_point.project`) requirió actualizar una única aserción de igualdad exacta de diccionario en
`tests/test_v4_3_r2_evidence_hydration.py`.

**Conteos**: antes de esta ronda, `2057 tests, 0 fallos, 0 errores, 132 skips`
(`docs/V4_3/V4_3_R7_INTERNAL_ACCEPTANCE_RESULT.md` sección 6). Tras la redacción inicial de esta ronda: `2082
tests`. Tras la corrección de seguimiento de sección 4.1 (revisión humana de las muestras R8): **`2087 tests, 0
fallos, 0 errores, 132 skips`** (2082 + 5 nuevos) -- `python -m unittest discover -s tests` → `OK (skipped=132)`.
`python -m unittest tests.test_v4_3_r8_external_pilot_corrections` → **30/30 `OK`**.

## 7. Actualización mecánica del inventario de mantenibilidad (V4.1-R0)

Mismo patrón que cada ronda previa. Ninguna aserción existente se debilitó; solo se ajustaron los valores
esperados a los cambios reales de esta ronda:

| Sección del inventario | Ajuste |
|---|---|
| `risk_summary.high_risk_files` / `very_high_risk_files` | `legacy_documenter/documentation/human_flow_documentation.py` cruza de `HIGH` a `VERY_HIGH` (549 líneas tras las nuevas secciones 3/4/8 y la clasificación de nombres técnicos; cuatro `responsibility_signals` -- el mismo falso positivo por palabras de docstring ya aceptado en rondas previas para otros módulos, este módulo sigue sin tocar filesystem/red/un serializador real) |
| `risk_summary.files_by_risk_category` | `HIGH` -1, `VERY_HIGH` +1 (el mismo movimiento) |

No hubo ningún módulo nuevo esta ronda (`_documentation_partitioning.py`, `hydration.py`,
`human_documentation_scaling.py` ya existían; solo se les añadieron funciones/campos) y ningún otro archivo
cruzó de categoría de riesgo. `production_inventory`, `dependency_findings`, `documentation_candidates`,
`duplication_candidates`, `known_debt`, `naming_candidates`, `exception_candidates` no cambian: esta ronda no
añade módulos, no introduce nuevas dependencias internas, y no cambia el manejo de excepciones de ningún
archivo. `python -m unittest tests.test_v4_1_r0_maintainability_inventory` → **22/22 `OK`**.

## 8. Restricciones R8 -- cumplimiento verificado

- `PROJECT_STATE.json`: no modificado.
- Plugin Runtime: no implementado.
- Provider/model abstraction: no rediseñada -- esta ronda no toca `legacy_documenter.llm`.
- V5: no iniciado.
- `consumer_projection`: no tocado (ninguna regresión de test lo exigió).
- Repositorio de desarrollo: no se incorporó ningún output real del piloto, código legacy real,
  `OUTPUT_MANIFEST`/`RUN_SUMMARY` reales, ni documento real generado -- únicamente los hallazgos
  anonimizados/generalizados (P-01/P-02/P-03) reproducidos con los fixtures sintéticos de
  `tests/test_v4_3_r8_external_pilot_corrections.py`, y las cuatro identidades de flujo de la matriz mínima,
  que ya eran públicas en `docs/V4_3/V4_3_R0_SCOPE_AND_EMPIRICAL_BASELINE_RESULT.md` sección 5 desde V4.3-R0.
- Runtime independence: sin cambios -- ninguno de los tres módulos tocados
  (`human_flow_documentation.py`, `human_documentation_scaling.py`, `hydration.py`,
  `_documentation_partitioning.py`) importa `legacy_documenter.llm` ni escribe a disco (verificado por las
  suites `RuntimeIndependenceTests` preexistentes de R2/R3/R4, sin modificar).
- Los siete puntos de test sintético exigidos por el prompt de corrección están cubiertos: (1) carpeta
  contenedora genérica `proyectos\...` (`OwningProjectGroupKeyTests`); (2) owner con miles de flujos /
  necesidad de subpartición (`SecondLayerSubPartitioningTests`); (3) flujo con muchos paths confirmados + mucho
  ruido técnico (`SummaryFirstOrderingTests`, `TechnicalNoiseVsUncertaintyTests`, fixture
  `_verbose_noisy_flow_ix`); (4) conservación exacta de `path_ids`/`evidence_refs`
  (`EvidencePreservationTests`); (5) unión completa y sin duplicados de particiones humanas
  (`SecondLayerSubPartitioningTests`); (6) summary-first (`SummaryFirstOrderingTests`); (7) evidencia
  exhaustiva todavía accesible (`SummaryFirstOrderingTests.test_exhaustive_detail_section_still_contains_every_path_including_noise`).

## 9. Archivos runtime modificados/creados

| Archivo | Tipo de cambio |
|---|---|
| `legacy_documenter/context/hydration.py` | `hydrate_flow` añade el campo aditivo `entry_point.project` (P-01) |
| `legacy_documenter/exporters/_documentation_partitioning.py` | Nueva función `owning_project_group_key` (P-01) |
| `legacy_documenter/documentation/human_documentation_scaling.py` | `flow_group_key` delega en `owning_project_group_key` (P-01); `render_human_documentation_partitions` gana sub-particionado de segunda capa (`MAX_FLOWS_PER_GROUP_FILE`, `_render_group_document`, `_render_group_sub_index`) (P-01); prosa del índice corregida para describir la política real de agrupación (proyecto `.vbproj` → fallback WebForm), corrección de sección 4.1's hermana de coherencia (**corrección 1** de esta sesión de revisión) |
| `legacy_documenter/documentation/human_flow_documentation.py` | `render_flow_document` reestructurado summary-first (secciones 3/4 nuevas, 5–8 renumeradas/fusionadas); nueva clasificación local `PRESENTATION_TECHNICAL_METHOD_NAMES`/`_path_is_presentation_technical`/`_path_is_confirmed_main` (P-02); sección 7 separa límites técnicos/infraestructura (P-03); **corrección 4.1** (**corrección 2** de esta sesión de revisión): `_section_5_services_and_layers` también excluye nombres `PRESENTATION_TECHNICAL_METHOD_NAMES`; nuevas `_path_presentation_technical_node_caller`/`_unresolved_boundary_node_callers`, usadas por `_section_7_unresolved` para reclasificar un límite con terminal opaco pero nodo técnico reconocido |
| `tests/test_v4_3_r8_external_pilot_corrections.py` | **Nuevo**, 30 tests (25 de la redacción inicial + 5 de la corrección de sección 4.1) |
| `tests/test_v4_3_r2_evidence_hydration.py` | Una aserción de igualdad exacta actualizada para el nuevo campo `entry_point.project` |
| `tests/test_v4_3_r3_human_documentation.py` | Encabezados/límites de sección actualizados a la renumeración (nunca debilitados) |
| `tests/test_v4_3_r4_scaling_and_partitioning.py` | Dos aserciones de encabezado actualizadas a la renumeración; un nombre de test corregido (`seven_section` → `eight_section`) |
| `tests/test_v4_1_r0_maintainability_inventory.py` | Actualización mecánica del inventario congelado (sección 7) |

No se tocó `legacy_documenter/llm/`, `legacy_documenter/orchestration/`, `legacy_documenter/context/consumer_projection.py`,
`legacy_documenter/context/ai_projection.py`, `legacy_documenter/cli/`, ni `PROJECT_STATE.json`.

## 10. Muestras sintéticas materializadas para revisión humana (`docs/V4_3/samples/R8/`)

Añadidas después de la redacción inicial de esta ronda, a pedido explícito del Líder Técnico: el código y los
tests de R8 ya estaban en verde, pero faltaba una muestra tangible del comportamiento final -- exactamente lo
que `docs/V4_3/samples/R3/`, `R4/`, `R6/` ya hacen para sus propias rondas. Generadas con un script de un solo
uso (no forma parte del runtime ni se conserva en el repositorio) que:

- reutiliza, sin modificar, los fixtures sintéticos ya comprometidos en
  `tests/test_v4_3_r8_external_pilot_corrections.py` (`_synthetic_large_group_ix`, `_verbose_noisy_flow_ix`);
- llama, sin modificar, a las funciones de producción de R2/R3/R4/R8
  (`EvidenceHydrator.hydrate_flow`, `render_human_documentation_index`, `render_human_documentation_partitions`,
  `render_flow_document`) exactamente como `pipeline_stages.render_documentation` ya las invoca en producción;
- no cambia ningún comportamiento runtime -- ninguna de las funciones anteriores fue tocada para producir
  estas muestras, y ningún umbral (`MAX_FLOWS_PER_GROUP_FILE`) fue alterado.

Ningún dato/código del repositorio legacy real ni ningún output real del piloto se usó o incorporó -- todo el
contenido es sintético, generado localmente, con las mismas identidades de flujo/proyecto de ejemplo ya usadas
en `tests/test_v4_3_r8_external_pilot_corrections.py` y en esta misma sección 2 (`WebWPF`, `proyectos\WebWPF\...`).

**Regeneradas tras la corrección de sección 4.1**: la revisión humana de la primera versión de estas muestras
encontró las dos correcciones de presentación de sección 4.1/corrección 1 (agrupación) y corrección 2
(clasificación técnica con terminal opaco). Las seis muestras se regeneraron, con el mismo script y los mismos
fixtures sin cambios, después de aplicar ambas correcciones -- el contenido descrito abajo ya refleja el
comportamiento corregido, no el original.

### Archivos generados

| Ruta | Contenido | Demuestra |
|---|---|---|
| `docs/V4_3/samples/R8/HUMAN_DOCUMENTATION.md` | Índice de nivel superior sobre 513 flujos sintéticos, 2 grupos | Índice sin detalle completo, enlaces relativos correctos hacia `flujos_humanos/` |
| `docs/V4_3/samples/R8/flujos_humanos/WebWPF.md` | Sub-índice (512 flujos, por encima del umbral) | Agrupación por `.vbproj` real (`WebWPF`) en vez del contenedor genérico `proyectos` (P-01, parte 1); sub-índice sin detalle de flujo (P-01, parte 2) |
| `docs/V4_3/samples/R8/flujos_humanos/WebWPF-part-000001.md` | 500 flujos (el máximo por archivo) | Partición numerada determinista, parte 1/2 |
| `docs/V4_3/samples/R8/flujos_humanos/WebWPF-part-000002.md` | 12 flujos restantes | Partición numerada determinista, parte 2/2 -- unión de ambas partes = exactamente los 512 flujos del grupo, sin pérdida ni duplicación (verificado programáticamente, ver abajo) |
| `docs/V4_3/samples/R8/flujos_humanos/webCobMorosidad.md` | 1 flujo (grupo pequeño, sin evidencia de proyecto) | Un grupo ordinario, por debajo del umbral, sigue produciendo un único archivo con detalle completo -- sin cambio de comportamiento respecto a V4.3-R4/R7 |
| `docs/V4_3/samples/R8/flujo_sintetico_verboso_summary_first.md` | El documento de un único flujo sintético verboso (`FLOW-BIG`, reproducción del caso real `CobLiquidacionDeudaPrev.ascx`/`Page_Load`), aislado de su archivo de grupo | Los ocho puntos summary-first pedidos, en un único documento compacto (ver tabla siguiente) |

### Cobertura de los ocho puntos summary-first en `flujo_sintetico_verboso_summary_first.md`

| # | Punto pedido | Sección del documento |
|---|---|---|
| 1 | Resumen funcional determinista primero | `## 3. Resumen funcional determinista` |
| 2 | Rutas confirmadas principales | `## 4. Rutas confirmadas principales` |
| 3 | Servicios/capas | `## 5. Servicios/capas` (lista principal: solo `Planilla.obtenerGastosCobEJ`/`Planilla.obtenerLiqDeudaPrev`; `Formulario.DesplegarError`/`Formulario.LimpiaNullDataset` en `### Elementos técnicos/auxiliares`, tras la corrección de sección 4.1) |
| 4 | Datos/SP/SQL | `## 6. Datos/SP/SQL` |
| 5 | Evidencia transaccional | `## 6. Datos/SP/SQL` → `### Evidencia transaccional` (`dbc.BeginTrans`/`dbc.Commit`, confirmadas) |
| 6 | Incertidumbres funcionales relevantes | `## 7. Qué queda no resuelto` (lista principal: solo `UnknownHelper.ProcesarAlgo` -- terminal opaco sin evidencia de nodo técnico) |
| 7 | Límites técnicos/infraestructura separados | `## 7. Qué queda no resuelto` → `### Límites técnicos/infraestructura (no resueltos, de naturaleza conocida)` (`dbc.BeginTrans`/`dbc.Commit` -- las mismas dos llamadas de la fila 5, aquí en su rol de límite no resuelto -- **más**, tras la corrección de sección 4.1, `unknown_noise_1`/`unknown_noise_2`: terminales opacos cuyo propio camino contiene `Formulario.DesplegarError`/`Formulario.LimpiaNullDataset`, reclasificados con anotación de transparencia y su id real preservado; nunca mezclados con la fila 6) |
| 8 | Evidencia técnica exhaustiva/trazabilidad al final | `## 8. Evidencia técnica detallada / trazabilidad` (los 7 caminos completos + trazabilidad `PATH`/`evidence_refs`/`provenance`) |

### Verificación de la muestra de particionado (no solo por inspección)

Sobre los archivos generados: `WebWPF-part-000001.md` contiene exactamente 500 documentos `# Flujo FLOW-*`,
`WebWPF-part-000002.md` exactamente 12, ningún `flow_id` de los 512 aparece en ambos archivos, y la unión de
ambos reproduce exactamente el conjunto `{FLOW-00000, ..., FLOW-00511}` -- verificado programáticamente contra
los archivos ya escritos en disco (no solo contra los tests unitarios que ya cubren la misma propiedad sobre
datos en memoria, sección 6).

**Tamaño**: `WebWPF-part-000001.md` pesa ~1.8 MB (500 documentos de flujo mínimos, cada uno con las ocho
secciones completas más la sección de límites -- el mismo costo por flujo que produce el archivo real de
45 MB/2983 flujos del piloto, a una escala sintética ~6 veces menor); el resto de los archivos generados pesan
entre 0.5 KB y 44 KB. Se mantiene deliberadamente por encima del umbral exacto (512 > 500) en vez de usar un
conteo mucho mayor, para que la muestra siga siendo la más pequeña posible que aún ejercita de forma real el
mecanismo de segunda capa con las funciones de producción sin modificar.

## 11. Revisión humana obligatoria (pendiente) — Gate para R9

Pendiente de aprobación por el Líder Técnico antes de considerar V4.3 lista para cierre/versionado (R9):

- [ ] este resultado R8 (`docs/V4_3/V4_3_R8_EXTERNAL_PILOT_CORRECTIONS_RESULT.md`);
- [ ] la corrección de P-01 (agrupación por proyecto `.vbproj` real + segunda capa de particionado,
      sección 2), incluyendo que `EvidenceHydrator` no fue modificado en su selección/deduplicación de
      evidencia;
- [ ] la corrección de P-02 (documento summary-first, secciones 3/4/8, sección 3);
- [ ] la corrección de P-03 (separación presentation-only de límites técnicos/infraestructura vs.
      funcionalmente relevantes, sección 4), incluyendo la verificación explícita de que ningún límite se
      promueve a confirmado;
- [ ] la corrección de seguimiento de sección 4.1 (clasificación por evidencia de nodo cuando el terminal es
      opaco, en servicios/capas y en qué queda no resuelto), incluyendo que un nodo funcional genuinamente
      desconocido nunca se reclasifica como técnico y que la sección 8 conserva el 100% de los caminos;
- [ ] la matriz de clasificación de los cuatro casos A–D (sección 5);
- [ ] los conteos de tests: **2087 tests, 0 fallos, 0 errores, 132 skips** (sección 6);
- [ ] el cumplimiento de las ocho restricciones R8 (sección 8);
- [ ] las muestras sintéticas materializadas bajo `docs/V4_3/samples/R8/` (sección 10, regeneradas tras la
      corrección de sección 4.1), incluyendo la verificación explícita de que la partición de 512 flujos
      sintéticos es completa y sin duplicados.
