# LegacyMapper V4.2 — Manual Técnico para Desarrolladores

> Describe el sistema **tal como está implementado en V4.2** (candidata a cierre; pendiente de aprobación final del Technical Lead). Complementa, sin reemplazar, el [Manual Técnico V4.1](../V4_1/LEGACYMAPPER_TECHNICAL_MANUAL_V4_1.md), que sigue siendo la referencia para el sistema de conocimiento (`legacy_documenter/knowledge/`), los principios de diseño generales, y la arquitectura previa a V4.2. Este documento cubre lo que V4.2 agregó o cambió operativamente: el modelo de CLI/ejecución, el orquestador `full`, la propiedad y recuperación de artefactos generados, la partición de documentación (V4.2-R8), el límite AI/propuesta/aprobación, y la deuda/limitaciones conocidas al cierre de V4.2.

---

## 1. Enrutamiento de CLI

`legacy_documenter/cli/` implementa tres subcomandos explícitos sobre `main.py`:

```
python main.py analyze <repositorio> [opciones]     # análisis determinístico únicamente (compatibilidad V4.1)
python main.py full <repositorio> --output <salida> [opciones]   # análisis + documentación + RUN_SUMMARY
python main.py readiness                             # valida prerrequisitos internos, no analiza repositorio
python main.py <repositorio> [opciones]               # atajo heredado, delega a `analyze`
```

`legacy_documenter/cli/parser.py` define el contrato de argumentos; `legacy_documenter/cli/router.py` despacha al handler correspondiente; `legacy_documenter/cli/execution_model.py` define `RunResult`/`StageResult`/`RunStatus`/`StageStatus`, el modelo de datos común que ambos comandos usan para reportar qué pasó.

`analyze` es la orquestación de compatibilidad: llama a las mismas funciones de etapa que `full`, pero sin el manejo de fallas por etapa de `full` — una excepción no capturada aborta la ejecución completa, exactamente el comportamiento pre-V4.2.

---

## 2. El orquestador `full` (resiliente)

`legacy_documenter/cli/full_pipeline.run_full_pipeline` ejecuta diez etapas deterministas en orden (`SCAN` → `EXTRACTION` → `CALL_RESOLUTION` → `WEB_ENTRY_RESOLUTION` → `DATABASE_RESOLUTION` → `FLOW_RESOLUTION` → `DEPENDENCY_RESOLUTION` → `EXPORT` → `CONTEXT` → `DOCUMENTATION`), más dos etapas opcionales (`AI_INTERPRETATION`, `PROPOSAL_GENERATION`, ambas `NOT_RUN` salvo `--allow-ai-interpretation`) y un cierre (`FINAL_SUMMARY`).

Cada etapa se ejecuta envuelta en su propio `try/except`: una falla en una etapa se registra como `StageResult(status=FAILED, error=...)` y las etapas dependientes que no puedan continuar quedan `SKIPPED_DUE_TO_UPSTREAM_FAILURE` — nunca una excepción cruda hacia el usuario. El `RunStatus` global (`SUCCESS`/`PARTIAL`/`FAILED`) se deriva de qué combinación de etapas tuvo éxito, nunca de la existencia de archivos en disco.

`legacy_documenter/cli/pipeline_stages.py` contiene las funciones de etapa puras (compartidas por `analyze` y `full`); `full_pipeline.py` contiene únicamente la política de resiliencia/orquestación sobre esas funciones.

---

## 3. `RUN_SUMMARY` y contrato de determinismo

`legacy_documenter/cli/run_summary_presenter.py` construye `RUN_SUMMARY.json`/`.md` a partir del `RunResult` final. Campos clave: `status`, `stages[]`, `ai_requested`/`ai_invoked`, `proposal_count`/`proposal_review_status`, `canonical_knowledge_produced` (siempre `false` en V4.2), `technical_lead_approval` (siempre `false` en V4.2), `output_locations[]`, `next_action`.

**Contrato de determinismo (V4.2-R2, vigente sin cambios en V4.2-R8):** `RUN_SUMMARY.json` debe ser byte-idéntico entre dos ejecuciones equivalentes de la misma entrada (`tests/test_v4_2_r2_deterministic_full_pipeline_orchestrator.py::DeterminismTests`). Por esta razón, `RUN_SUMMARY.json` **no** lleva un campo de duración de pared completa (F-05, ver sección 9) ni ningún UUID/timestamp — cualquier valor de reloj real rompería ese contrato en la primera ejecución repetida.

---

## 4. Propiedad y recuperación de artefactos generados (rerun safety)

`legacy_documenter/cli/artifact_lifecycle.py` concentra la política de "qué le pertenece a LegacyMapper dentro de `--output`, y qué se limpia en cada corrida":

- `index/`, `documentation/*.md` (nombres fijos), `context/`, `ai_context/` se sobrescriben por completo cada vez que su etapa dueña corre — no requieren limpieza activa porque el conjunto de nombres de archivo nunca cambia entre corridas.
- `proposals/` (`reset_stale_proposal_artifacts`) se limpia incondicionalmente al inicio de cada `full`, antes de que corra cualquier etapa, para que una propuesta de IA de una corrida anterior nunca sobreviva pareciendo vigente en una corrida que no pidió IA.
- `documentation/functional_flows/`, `documentation/database_access/`, `documentation/unresolved_findings/` (V4.2-R8, ver sección 6) usan `sync_generated_partition_directory`: solo se eliminan archivos `.md` que ya no forman parte del conjunto de particiones de la corrida actual; cualquier archivo con otra extensión (por ejemplo, una nota que alguien haya dejado ahí) se preserva sin condición. El directorio se crea solo si hay al menos una partición que escribir, y se elimina de nuevo si queda vacío.

En ningún caso se toca el repositorio legado analizado (siempre de solo lectura), ni se sale de la carpeta `--output` seleccionada.

---

## 5. Modelo de documentación técnica (V4.2-R3, extendido en V4.2-R8)

`legacy_documenter/exporters/markdown_exporter.py` (los seis documentos pre-R3: `PROJECT_OVERVIEW.md`, `SOLUTION_STRUCTURE.md`, `PROJECT_DEPENDENCIES.md`, `WEBFORMS_MAP.md`, `CONFIGURATION_SUMMARY.md`, `ANALYSIS_WARNINGS.md`) y `legacy_documenter/exporters/technical_documentation_renderer.py` (`WEB_ENTRY_POINTS.md`, y los tres documentos con índice/detalle de R8) son funciones puras sobre el diccionario `indexes` que ya construyó el análisis determinístico — ningún renderer vuelve a leer un archivo de disco, ni llama a un LLM, ni infiere una relación que el análisis no haya descubierto ya.

`legacy_documenter/cli/pipeline_stages.render_documentation` orquesta la escritura: cada documento (incluido `documentation/README.md`) se calcula y escribe dentro de su propio `try/except`, de modo que la falla de un renderer nunca impide que los demás produzcan su documento (`DocumentationOutcome.written`/`.failures`).

---

## 6. Partición de documentación a escala (V4.2-R8)

### 6.1 Motivación

El pilotaje real de V4.2-R7 encontró que `FUNCTIONAL_FLOWS.md` (~44MB), `UNRESOLVED_FINDINGS.md` (~12.8MB) y `DATABASE_ACCESS.md` (~5.2MB) dejaban de ser consumibles como documentos planos únicos a la escala de un repositorio real grande (ver `docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md` FINDINGS `NOISE_OR_SCALE_ISSUES`). V4.2-R8 no vuelve a ejecutar ese repositorio real (`REAL_LEGACY_REPOSITORY_READ_ALLOWED=false` en R8); el rediseño se valida enteramente con datos sintéticos generados programáticamente en pruebas.

### 6.2 Diseño: Nivel 1 (navegación) + Nivel 2 (detalle)

Para cada uno de los tres documentos objetivo, `TechnicalDocumentationRenderer` expone tres métodos:

- `*()` (sin sufijo): el documento plano completo, sin cambios de comportamiento — se mantiene por compatibilidad y para consumidores que quieran todo en un solo documento (usado directamente por `tests/test_v4_2_r3_deterministic_technical_documentation.py`).
- `*_navigation()`: el documento de nivel superior (el que sigue viviendo en el nombre de archivo histórico, por ejemplo `documentation/FUNCTIONAL_FLOWS.md`) — resumen, conteos, y un enlace relativo por grupo hacia su documento de detalle.
- `*_partitions()`: un `dict[str, str]` de `{nombre_de_archivo: contenido}`, uno por grupo semántico, escrito bajo `documentation/<doc>/`.

Ambas rutas (la plana y la particionada) comparten las mismas funciones auxiliares de renderizado por ítem (`_render_flow_entry_lines`, `_data_access_table_lines`, `_render_unresolved_category_body`, etc.), de modo que no pueden divergir entre sí en el contenido de un ítem individual.

`render_documentation` (sección 2) invoca `*_navigation()` + `*_partitions()` para los tres documentos objetivo, y `sync_generated_partition_directory` (sección 4) para escribir/limpiar el subdirectorio correspondiente.

### 6.3 Criterio de agrupación por documento

| Documento | Unidad de agrupación | Justificación |
|---|---|---|
| `FUNCTIONAL_FLOWS.md` | Primer proyecto de `project_sequence` del flujo (`"unassigned"` si está vacío) | Ya presente en el modelo de flujo; agrupar por proyecto es la unidad semántica más natural para un desarrollador que busca "los flujos de mi módulo". |
| `DATABASE_ACCESS.md` | `project` del punto de acceso; para procedimientos/SQL sin `project` propio, el `project` de su primera evidencia | Preserva `operation_kind`, procedimiento almacenado, proveedor y evidencia sin inventar una relación nueva. |
| `UNRESOLVED_FINDINGS.md` | Categoría preexistente (`extraction_errors`, `unresolved_flow_boundaries`, `unresolved_entry_points`, `unresolved_database_access`) | Es la agrupación que el documento plano ya usaba como secciones `##`; convertirla en partición es el cambio más pequeño posible. |

`## Parameters` (dentro de `DATABASE_ACCESS.md`) se mantiene en el documento de navegación, sin particionar: ya está agrupado por invocador y es pequeño en la práctica; no es uno de los tres objetivos de escala primarios de la sección 5 del prompt de R8.

### 6.4 F-06: agrupación presentacional, no resolución

Dentro de la partición `unresolved_flow_boundaries.md`, las filas cuyo `terminal_target` es exactamente `InitializeComponent()` (ruido de diseñador de WebForms) se muestran bajo su propia subsección (`### Framework/Designer-Generated Boilerplate`), separadas de `### Other Unresolved Boundaries`. Esto es puramente presentacional: **ninguna fila se descarta ni se reclasifica como resuelta** — el conteo de la categoría en el documento de navegación es idéntico al de antes de la separación. F-06 sigue siendo `PRESERVED_OBSERVATION`; esta separación no es una corrección de esa observación, solo una mejora de legibilidad autorizada explícitamente por la sección 9 del prompt de R8.

### 6.5 Nombres de archivo seguros y deterministas (`legacy_documenter/exporters/_documentation_partitioning.py`)

`sanitize_label` reemplaza todo carácter fuera de `[A-Za-z0-9_-]` por `_` — lo que vuelve estructuralmente imposible que un `..` o un separador de ruta (`/`, `\`) sobreviva al proceso, sea cual sea la etiqueta de entrada — y cae a `"unassigned"` para una etiqueta vacía, `None`, o que quede vacía tras el saneo; trunca a 80 caracteres; y añade un guion bajo de escape a un nombre reservado de Windows (`CON`, `PRN`, `NUL`, `COM1`..`COM9`, `LPT1`..`LPT9`). `build_partition_filenames` resuelve colisiones (dos etiquetas distintas que sanean al mismo nombre, incluida una colisión de mayúsculas/minúsculas insensible en el sistema de archivos de Windows) con un sufijo numérico derivado del orden de entrada — nunca un hash aleatorio, timestamp, o UUID. Ningún contenido controlado por IA/proveedor participa en la derivación de un nombre de archivo.

### 6.6 Enlaces Markdown

Todo enlace entre documentos generados usa una ruta relativa con separador `/` (estilo POSIX), nunca una ruta absoluta ni backslashes de Windows — válida tanto al abrirse en un visor de Markdown como al resolverse directamente en el árbol de archivos generado en Windows.

---

## 7. Límite AI / propuestas / aprobación

Sin cambios de fondo respecto a V4.1 (ver el Manual Técnico V4.1, sección sobre propuestas/aprobación); en V4.2 se reafirma:

- `--allow-ai-interpretation` es la única puerta de entrada a un proveedor de IA real; sin ese flag, `full` (y `analyze`) hacen cero llamadas a IA/proveedor.
- Toda ejecución de prueba automatizada usa `FakeLLMProvider` (nunca un proveedor real) — reforzado por un guard en `tests/__init__.py` que falla ruidosamente si algún test alcanza inesperadamente la resolución de un proveedor real (ver `docs/V4_2/V4_2_R5_1_EXIT_CODE_CONTRACT_AND_REAL_PROVIDER_GUARD_RESULT.md`).
- La superficie de aprobación (`approve`/`reject`/`request-correction`, persistencia de `ApprovalDecision`, promoción a conocimiento canónico) está **diseñada pero no implementada** (`docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md`, `APPROVED_DESIGN_ONLY` / `IMPLEMENTATION_STATUS=NOT_IMPLEMENTED`). Ningún comando de V4.2 implementa `run_id`, aprobación, ni orquestación R11/R12.
- `canonical_knowledge_produced` y `technical_lead_approval` permanecen `false` en toda ejecución de V4.2.

---

## 8. Estado de canónico / R11 / R12

Sin cambios respecto a V4.1: el sistema de conocimiento canónico (`legacy_documenter/knowledge/`), su proyección legible por humanos (R11) y su contrato legible por máquina para un futuro Plugin (R12) existen como capacidad interna del motor y están cubiertos por su propia suite de pruebas, pero **no se ejercitan a través de un CLI unificado de conocimiento** en V4.2 — el CLI de V4.2 (`analyze`/`full`/`readiness`) es exclusivamente la superficie de análisis de código, no la superficie de gestión de conocimiento. Ver la sección 3.3 del [Manual de Usuario V4.1](../V4_1/LEGACYMAPPER_USER_MANUAL_V4_1.md).

---

## 9. Seguridad y guardas de proveedor

- El repositorio legado analizado se accede en modo solo lectura; ninguna etapa de V4.2 escribe, renombra, o elimina un archivo dentro de él.
- El guard de proveedor real (R5.1) impide que una verificación manual de la ruta con IA habilitada alcance accidentalmente un proveedor real: usar `python -m tools.manual_verify_full_pipeline` (siempre inyecta `FakeLLMProvider`) en lugar de `python main.py full ... --allow-ai-interpretation` directamente para cualquier verificación manual, exactamente como ya documentaba `AGENTS.md` desde R5.1.
- Ningún documento generado (los diez de nombre fijo, sus particiones, ni `README.md`) incluye una ruta absoluta del analista ni un valor de credencial/cadena de conexión real; `PROJECT_OVERVIEW.md` (F-04, V4.2-R7.1) muestra solo el nombre de la carpeta final del repositorio, nunca la ruta completa.
- `RUN_SUMMARY.json` nunca lleva un UUID ni un timestamp (ver sección 3).

---

## 10. Limitaciones y deuda conocida al cierre de V4.2

| ID | Estado | Descripción |
|---|---|---|
| F-05 | `DEFERRED_BY_DETERMINISM_CONTRACT` | No existe un campo de duración de pared completa en `RUN_SUMMARY.json`; agregarlo rompería el contrato de determinismo byte-a-byte de la sección 3. |
| F-06 | `PRESERVED_OBSERVATION` | El ruido de `InitializeComponent()` en hallazgos no resueltos se agrupa presentacionalmente (sección 6.4) pero no se filtra ni resuelve. |
| F-07 | `PRESERVED_OBSERVATION` | `WebEntryResolver` no adjunta `outgoing_calls` a un punto de entrada vinculado por marcado ASPX (`OnClick="..."`) en lugar de por cláusula `Handles` de code-behind; impacto real acotado (0.3% de los puntos de entrada reales observados en R7). |
| Escala documental restante | `OPEN` | La partición de V4.2-R8 resuelve el problema de escala para los tres documentos objetivo; una futura ronda podría todavía necesitar paginación/búsqueda para `WEB_ENTRY_POINTS.md`/`PROJECT_DEPENDENCIES.md` si un repositorio real llegara a superar la escala observada en R7 para esos dos documentos. |

Ninguna de estas limitaciones representa una relación fabricada o un dato incorrecto — son, en cada caso, un problema de completitud/presentación/alcance explícitamente diferido, nunca uno de corrección.

---

## 11. Límite de V5

V5 permanece fuera de alcance y no implementado. Explícitamente preservado para V5, no para V4.2:

- Agnosticismo de lenguaje.
- Agnosticismo de framework.
- Agnosticismo de base de datos.
- Agnosticismo de layout de proyecto.
- Agnosticismo de proveedor/modelo de IA.

V4.2 no rediseña ni aproxima ninguno de estos puntos; el escenario tecnológico soportado sigue siendo exactamente el descrito en la sección 3 del [Manual Técnico V4.1](../V4_1/LEGACYMAPPER_TECHNICAL_MANUAL_V4_1.md).

---

Para una introducción no técnica, ver el [Manual de Usuario V4.2](LEGACYMAPPER_USER_MANUAL_V4_2.md).
Para definiciones de términos, ver el [Glosario V4.1](../V4_1/LEGACYMAPPER_GLOSSARY_V4_1.md) (sigue vigente).
