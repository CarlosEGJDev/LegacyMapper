# V5.2 R0 — Documentation & Output Profiles Baseline

## 1. Estado

V5_2_R0_BASELINE_READY

Esta ronda es exclusivamente de estudio. No se modificó ningún archivo de `legacy_documenter/`, no se ejecutó ningún análisis nuevo de IST y no se creó ningún commit. V5.1 (Normalized Evidence Core) permanece cerrada y sin tocar. La evidencia de esta ronda proviene de leer el código real de generación de documentación y de inspeccionar una salida real reciente ya en disco.

## 2. Cómo funciona hoy la documentación

Hoy existen **cuatro salidas distintas**, todas generadas en la misma corrida (`EXPORT`/`CONTEXT`), sin relación de dependencia entre ellas — ninguna deriva de otra, cada una lee directamente el mismo diccionario `indexes` en memoria:

| Carpeta | Para quién | Generada por |
|---|---|---|
| `index/` | Compatibilidad máquina-a-máquina con V4.3 | `JSONExporter` |
| `documentation/` | Lo más cercano a "para humanos" que existe hoy | `MarkdownExporter` + `TechnicalDocumentationRenderer` + `human_flow_documentation.py`/`human_documentation_scaling.py` |
| `ai_context/` | Para un futuro consumidor de IA (V5.5), no para lectura humana | `legacy_documenter/context/*` |
| `consumer_projection/` | Para un plugin/consumidor externo, tampoco para lectura humana | `legacy_documenter/context/consumer_projection.py` |

`documentation/` es un conjunto de **generadores de texto Markdown escritos a mano en Python**: no existe ningún motor de templates, ningún archivo `.md`/`.jinja`/`.html` de plantilla, ni ninguna capa que separe "qué información mostrar" de "cómo se ve el texto". Cada documento tiene su propia función Python que concatena strings con formato Markdown embebido directamente en el código (título, tabla, separadores, todo hardcodeado). Confirmado leyendo `legacy_documenter/exporters/technical_documentation_renderer.py` (1222 líneas), `legacy_documenter/exporters/markdown_exporter.py`, `legacy_documenter/documentation/human_flow_documentation.py` (626 líneas) y `legacy_documenter/documentation/human_documentation_scaling.py` (404 líneas).

Dentro de `documentation/` conviven dos estilos de contenido, con un límite claro por historia del proyecto (no por diseño de V5.2):

- **Documentos "técnicos" (V4.2/V4.3-R3 en adelante):** `PROJECT_OVERVIEW.md`, `SOLUTION_STRUCTURE.md`, `WEBFORMS_MAP.md`, `PROJECT_DEPENDENCIES.md`, `DATABASE_ACCESS.md`, `WEB_ENTRY_POINTS.md`, `FUNCTIONAL_FLOWS.md`, `UNRESOLVED_FINDINGS.md`, `CONFIGURATION_SUMMARY.md`, `ANALYSIS_WARNINGS.md`. Cada uno tiene un documento "índice" de tamaño acotado a nivel raíz y, cuando la evidencia es grande, una carpeta con un archivo por proyecto/grupo (`database_access/`, `project_dependencies/`, `web_entry_points/`, `functional_flows/`, `unresolved_findings/`).
- **"Documentación humana de flujos" (V4.3-R3/R4/R8), en `flujos_humanos/`:** un documento en español por cada flujo funcional real (12 642 en IST), agrupado por WebForm/carpeta propietaria, con una estructura fija de 8 secciones repetida para cada flujo dentro del archivo de su grupo.

`RUN_SUMMARY.json`/`RUN_SUMMARY.md` (un quinto artefacto, fuera de `documentation/`) es el resumen operacional de la corrida (qué stage tuvo éxito, cuánto tardó) — no es documentación del sistema analizado.

## 3. Qué problema tiene para lectores humanos

Se inspeccionó una corrida real reciente sobre IST (`C:\PruebasLegacyMapper\Resultados\v5_1_r3_2_run_a`, generada por `main.py full` durante V5.1 R3.2, sin necesidad de repetir el análisis — ver sección 16). Problemas reales, medidos, no supuestos:

1. **Tamaño inmanejable en `flujos_humanos/`.** Esa única carpeta pesa **152.3 MB de 216.0 MB** que ocupa toda `documentation/` (70.5%), en solo 195 archivos. El archivo más grande, `WebSUBSubsidioNew-part-000001.md`, pesa **9.9 MB** — imposible de abrir cómodamente en un editor de texto normal, y completamente inviable para un lector humano que busque entender un flujo. La causa es doble: (a) el particionado (`MAX_FLOWS_PER_GROUP_FILE = 500`, en `human_documentation_scaling.py`) limita por **cantidad de flujos**, no por tamaño de archivo, así que un grupo de 500 flujos "pequeños" puede seguir pesando varios megabytes; y (b) cada flujo repite un bloque fijo de ~15 líneas ("Límites de esta documentación") **idéntico en cada uno de los 12 642 flujos**, además de las 8 secciones completas por flujo incluso cuando el flujo es trivial (ver ejemplo `BlIstSIAGF.md`, sección 16).
2. **Predomina lo no resuelto sobre lo útil.** De 12 642 flujos, solo 672 (5.3%) tienen un terminal confirmado; 11 368 (89.9%) tienen al menos un límite no resuelto (cifras del propio `HUMAN_DOCUMENTATION.md`). Un lector que abra un documento de flujo al azar tiene una probabilidad muy alta de encontrar una lista larga de "no se pudo confirmar su destino real" (`Chr(10)`, `Chr(13)`, `dbc.Close()`, `MsgBox(...)`) antes de llegar a algo funcionalmente relevante — visto directamente en `WebFiscalizacionRemota.md`, donde 15 de 16 límites no resueltos listados son llamadas de infraestructura (manejo de excepciones, transacciones, mensajes), no lógica de negocio.
3. **IDs internos como explicación principal en la práctica.** Aunque el propio documento declara la regla "los IDs técnicos no son la explicación principal", la sección 8 ("Evidencia técnica detallada") de cada flujo repite en texto plano `FLOW-`, `PATH-`, `CALL-`, `UNRES-`, `DAO-` para cada camino — y esa sección 8 suele ser la más larga del documento. Un lector sin contexto del motor no puede distinguir un `PATH-<hash-de-64-caracteres>` de información útil.
4. **No existe una "vista general" real.** No hay ningún documento que responda en lenguaje llano "¿qué hace este sistema?". `PROJECT_OVERVIEW.md` es una lista de conteos de archivos por extensión (`vb_source: 4328`, `ascx: 3165`, ...); `SOLUTION_STRUCTURE.md` es una lista de nombres de `.sln`/`.vbproj` sin ninguna descripción de propósito; `SYSTEM_CONTEXT.md` (en `ai_context/`, la aproximación más cercana a un resumen ejecutivo) está en **inglés** (el resto de `documentation/` está en español por decisión V4.3-R7) y es también una lista de conteos ("Confirmed: 12775; unresolved: 217581") sin ninguna narrativa.
5. **`CONFIGURATION_SUMMARY.md` mezcla producción y copias de respaldo sin distinguirlas.** Lista 60 `Web.config` sin indicar cuáles corresponden a carpetas `Backup`/`_back`/copias de Crystal Reports — un lector no puede saber cuál es la configuración real sin conocer ya la estructura de carpetas del repositorio.
6. **Mezcla de niveles de detalle dentro del mismo documento.** El propio esquema de flujo mezcla en un solo archivo: qué es (nivel 1), resumen funcional (nivel 2), y evidencia técnica exhaustiva con IDs (nivel 4) — sin ninguna forma de navegar del nivel 1 al 4 progresivamente; todo está siempre presente, en el mismo archivo, en el mismo scroll.

## 4. Qué funciona bien y debe conservarse

- **El principio "nunca inventar, siempre declarar lo no resuelto explícitamente"** está implementado de forma consistente y es, según la lectura del código y de la salida real, el activo más valioso del sistema actual — debe sobrevivir intacto a V5.2.
- **La separación índice/detalle particionado** (`DATABASE_ACCESS.md` + `database_access/<proyecto>.md`, etc.) ya resuelve el problema de escala para los documentos "técnicos" (no para `flujos_humanos/`, ver sección 3.1) — es el patrón correcto, solo aplicado de forma incompleta.
- **`database_access/<proyecto>.md`** es, de todo lo inspeccionado, el documento más cercano a "técnico pero legible": una tabla `Clase.Método | Proyecto | Tipo | Objetivo | Confianza | Origen`, sin relleno, sin repetición.
- **`README.md`** (el índice raíz de `documentation/`) es un buen punto de entrada: explica qué cubre cada documento y qué significa "confirmado" vs "no resuelto" en una frase clara.
- **Nunca se genera contenido con IA por defecto.** `human_flow_documentation.py`/`technical_documentation_renderer.py`/`markdown_exporter.py` no importan `legacy_documenter.llm` ni ningún provider (confirmado por lectura); toda `documentation/` de hoy ya cumple el principio "la documentación base debe poder generarse sin IA" que V5.2 exige mantener.

## 5. Vista general necesaria

Debe ser un documento nuevo y corto, no una reorganización de `PROJECT_OVERVIEW.md`/`SYSTEM_CONTEXT.md`. Debe responder, en un párrafo cada una, sin IDs internos ni JSON:

- ¿Qué hace este sistema? (a nivel de negocio: hoy no hay ninguna fuente determinista de esto más allá de nombres de proyecto/WebForm — es una limitación real, ver sección 14).
- ¿Qué módulos principales tiene? (agrupación por solución/carpeta propietaria, ya calculable desde `SOLUTION_STRUCTURE.md`/`PROJECT_DEPENDENCIES.md`, pero mostrado como lista corta con una frase por módulo, no una tabla exhaustiva de 258 proyectos).
- ¿Cómo se relacionan? (un resumen de las aristas de `PROJECT_DEPENDENCIES.md`, no las 9 422 aristas completas).
- ¿Qué procesos principales existen? (los flujos con terminal confirmado, priorizados sobre los 11 368 no resueltos — hoy estos ya existen como dato, solo no se presentan primero).
- ¿Con qué sistemas externos se comunica? (ya existe como dato: `ExternalDependency`/`XDP-` del Evidence Core, hoy no proyectado a ningún documento humano en absoluto).
- ¿Qué datos utiliza a grandes rasgos? (nombres de esquemas/paquetes Oracle agregados, no la lista de 5 392 `DataObject` individuales).

## 6. Vista desarrollador necesaria

Ya está parcialmente cubierta hoy por los documentos "técnicos" (sección 4), pero con exceso de detalle mezclado. Necesidades reales no cubiertas hoy:

- Un punto de entrada por módulo/proyecto que enlace a: sus dependencias, su acceso a datos, sus flujos con terminal confirmado — hoy cada uno vive en una carpeta paralela distinta (`database_access/`, `project_dependencies/`, `flujos_humanos/`) sin ningún documento que los una por proyecto.
- Progresión real: resumen del flujo (nivel 2) → detalle técnico (nivel 3/4) como un salto explícito (enlace), no todo en el mismo archivo.
- "¿Dónde está el código relacionado?" ya está cubierto (`archivo:línea` aparece consistentemente), pero enterrado dentro de secciones largas.

## 7. Clasificación KEEP_SIMPLE / KEEP_TECHNICAL / DETAIL_ON_DEMAND / INTERNAL_ONLY

Sobre el contenido real inspeccionado (no exhaustivo campo por campo — clasificación por tipo de contenido):

| Clasificación | Contenido real observado |
|---|---|
| **KEEP_SIMPLE** | Nombre del sistema/módulo, propósito cuando exista evidencia (hoy no existe determinista, ver sección 14), lista corta de módulos principales, conteo de flujos confirmados vs no resueltos como proporción (no la lista completa), lista de sistemas externos (`ExternalDependency.name`), nombres de paquetes/esquemas de datos agregados. |
| **KEEP_TECHNICAL** | Tabla `Clase.Método → Objetivo (SP/SQL) → archivo:línea` (ya existe en `database_access/*.md`), punto de entrada + evento + destino confirmado de un flujo, dependencias proyecto→proyecto agrupadas, estructura de soluciones/proyectos. |
| **DETAIL_ON_DEMAND** | El listado exhaustivo de *todos* los caminos de un flujo (sección 8 de hoy, incluidos los técnicos/infraestructura), los parámetros de cada `DataOperation` (`DataParameter`, 74 633 registros), la lista completa de límites no resueltos por flujo, `CONFIGURATION_SUMMARY.md` completo (60 `Web.config`). |
| **INTERNAL_ONLY** | `FLOW-*`/`PATH-*`/`CAL-*`/`UNRES-*`/`DAO-*`/`SRC-*`/todo el resto de ids `sha256` del Evidence Core, punteros `index/*.json#ID`, `schema_version`/`HUMAN_DOCUMENTATION_PROJECTION 1.0`/nombre de modelo (`V4.3-R3`), el bloque repetido "Límites de esta documentación", cualquier mención a `technical_noise_candidate`/mecánica interna del resolver. |

No se elimina ningún dato del Evidence Core: esta clasificación es puramente de presentación, tal como exige el prompt.

## 8. Perfiles de salida que parecen necesarios

Evidencia real respalda exactamente los dos que el prompt pide estudiar como mínimo, y ninguno adicional:

- **General Overview** — cubre la sección 5. No existe hoy ni un borrador; es una necesidad nueva confirmada por la ausencia total encontrada en la sección 3.4.
- **Developer Technical** — es, en esencia, lo que `documentation/` ya intenta ser hoy (menos `flujos_humanos/` en su forma actual), reorganizado con navegación progresiva y sin el exceso de detalle de la sección 8 de cada flujo en el cuerpo principal.

No se encontró evidencia real de una necesidad de un tercer perfil (p. ej. "auditoría de seguridad" o "migración") — no se propone ninguno, conforme a "no crear docenas de perfiles especulativos".

## 9. Qué debería controlar un template

- Título y encabezados de cada sección.
- Orden de las secciones.
- Inclusión/exclusión de una sección quando no aplica (hoy, p. ej., "No se identificaron servicios/clases..." se imprime siempre, incluso vacío — un template debería poder omitir la sección entera).
- Formato de tabla (columnas, orden) para cada tipo de listado (dependencias, accesos a datos, flujos).
- El bloque de "límites/disclaimers" — hoy repetido por flujo; con templates puede convertirse en una sección única al nivel del documento contenedor, no un template en sí, pero solo el template decide dónde/cuántas veces aparece.

## 10. Qué debería controlar un profile

- Qué nivel de detalle mostrar (1–4, sección 3 de este documento) para una audiencia dada.
- Qué categorías de contenido incluir según la clasificación de la sección 7 (p. ej. General Overview = solo KEEP_SIMPLE + un resumen de KEEP_TECHNICAL; Developer Technical = KEEP_SIMPLE + KEEP_TECHNICAL + enlaces a DETAIL_ON_DEMAND).
- Umbrales de "qué es ruido técnico/infraestructura" (hoy `PRESENTATION_TECHNICAL_METHOD_NAMES` está hardcodeado en `human_flow_documentation.py`; un profile debería poder decidir si mostrarlo o no, sin que el renderer decida por él).
- Idioma (hoy está hardcodeado a español en cada función `_es`, con una segunda familia de funciones en inglés que ningún camino productivo invoca).

## 11. Qué debería controlar un renderer

- La conversión a Markdown/HTML/otro formato de salida — puramente mecánica, sin decisiones de contenido.
- El particionado físico por tamaño de archivo (hoy limitado a "cantidad de flujos", el defecto BLOCKING de la sección 15) debería ser responsabilidad del renderer, no del profile ni del template.
- Escapado, sanitización de nombres de archivo (ya existe como utilidad reutilizable: `legacy_documenter/exporters/_documentation_partitioning.py::sanitize_label`/`build_partition_filenames`) — correcto conservarlo tal cual.

## 12. Defaults necesarios

Sin templates propios, V5.2 debería producir por defecto algo equivalente al perfil **Developer Technical** de hoy, pero corrigiendo los problemas BLOCKING (sección 15) — nunca el estado actual de `flujos_humanos/` tal cual (152 MB en un único subárbol es inaceptable como default). Prioridad de simplicidad significa: el documento raíz (equivalente a `README.md` de hoy) debe seguir siendo el punto de entrada, y cualquier detalle exhaustivo debe estar a un clic de distancia, nunca en el mismo archivo que el resumen.

## 13. Personalización futura

No se diseña CLI todavía (fuera de alcance de R0), pero la evidencia real sugiere que un usuario necesitará, como mínimo: elegir un profile por nombre (`--profile general|developer`), aportar un directorio de templates propio que sobrescriba el default por sección/tipo de documento (no todo o nada), y elegir formato de salida (Markdown ya cubierto; HTML no existe hoy en ningún renderer real, confirmado por lectura — sería trabajo nuevo, no una opción ya soportada).

## 14. Relación con IA

Confirmado: ningún renderer/exporter de `documentation/` de hoy importa `legacy_documenter.llm` ni ningún provider — la generación base ya es 100% determinista y sin IA, exactamente como V5.2 exige mantener. La limitación real es la inversa: **no hay ninguna fuente determinista de "qué hace el sistema de negocio"** (sección 5) — eso es evidencia que solo una interpretación (IA u otra) podría aportar; V5.2 debe dejar un hueco explícito para que una `INTERPRETED` (ya prevista y validada en `human_flow_documentation.py` desde V4.3-R3) llene esa sección sin que su ausencia rompa el documento determinista.

## 15. Problemas encontrados

**BLOCKING_FOR_V5_2**

1. **Tamaño de archivo individual sin límite real.** El particionado actual limita por cantidad de flujos (500), no por bytes; el resultado real (`WebSUBSubsidioNew-part-000001.md`, 9.9 MB) es inutilizable para un lector humano. V5.2 no puede heredar esta estrategia de particionado sin corregirla.
2. **No existe ninguna "vista general" para audiencias no técnicas.** Es el objetivo humano prioritario #1 del prompt de V5.2, y hoy no existe ni una aproximación — `PROJECT_OVERVIEW.md`/`SYSTEM_CONTEXT.md` son listas de conteos, no una narrativa.

**IMPORTANT**

3. Predominancia de contenido no resuelto/técnico sobre contenido funcionalmente relevante en los documentos de flujo (sección 3.2) — ya mitigado parcialmente por el orden "resumen primero" de V4.3-R8, pero el volumen bruto de detalle no resuelto sigue dominando el archivo.
4. `CONFIGURATION_SUMMARY.md` no distingue configuración de producción de copias de respaldo — puede inducir a error a un lector que no conozca ya la estructura de carpetas.
5. Mezcla de idioma: `SYSTEM_CONTEXT.md` en inglés dentro de un producto cuya documentación humana es en español por decisión explícita (V4.3-R7).

**MINOR**

6. Existen dos familias de funciones renderer (`_es` y sin sufijo) para el mismo contenido en `technical_documentation_renderer.py`; solo la familia `_es` se usa en producción — la otra es código muerto desde la perspectiva del producto actual, aunque sigue cubierta por tests.
7. IDs de 64 caracteres (`PATH-<sha256>`) se imprimen en texto plano dentro de prosa, dificultando la lectura visual aunque el lector sepa que puede ignorarlos.

## 16. Decisiones necesarias para R1

**Ya respaldadas por V5.0/V5.1 (no requieren nueva decisión):**

- Evidence Core sigue siendo la única fuente de verdad; documentación es una proyección — ya es el principio de V5.0/V5.1, V5.2 solo lo extiende a audiencias humanas.
- Nunca inventar/completar lo no resuelto — ya es una regla establecida (I-4/I-5 mismas del Evidence Core, y la regla textual "nunca se adivina" de `human_flow_documentation.py`).
- Independencia de IA para la generación base — ya validada en V5.1 y confirmada de nuevo aquí para `documentation/`.

**Nuevas, requieren decisión explícita del Technical Lead antes de R1:**

- **¿El particionado por tamaño de archivo reemplaza o convive con el particionado por cantidad de flujos?** Afecta directamente si `MAX_FLOWS_PER_GROUP_FILE` sigue existiendo o se sustituye por un límite en bytes.
- **¿Quién resuelve el hueco de "qué hace el sistema de negocio"?** Si la respuesta es "una interpretación humana o de IA aportada externamente" (sección 14), V5.2 necesita definir el contrato exacto de esa sección `INTERPRETED` para el nivel de sistema completo (hoy solo existe a nivel de flujo individual).
- **¿Dónde vive la configuración de "qué es ruido técnico/infraestructura" (`PRESENTATION_TECHNICAL_METHOD_NAMES`)?** Hoy es una constante Python hardcodeada; si pasa a ser parte del profile (sección 10), hace falta decidir su formato y si es extensible por el usuario.
- **¿HTML es un renderer real de V5.2 o queda fuera de alcance hasta una versión posterior?** No existe ningún renderer HTML hoy; el prompt de R1 debe decidir si lo incluye en el alcance mínimo o lo excluye explícitamente.
- **¿Los defaults reemplazan `documentation/` tal cual existe hoy, o coexisten con ella durante una transición?** Afecta directamente si V5.2 es un reemplazo o una capa nueva sobre la salida V4.3 existente.

## 17. Evidencia real utilizada

- Corrida real reutilizada (no se repitió el análisis de IST): `C:\PruebasLegacyMapper\Resultados\v5_1_r3_2_run_a` (generada por V5.1 R3.2 sobre `C:\Users\cgalianj\source\IST_40\Operacional`).
- Muestra representativa seleccionada de `documentation/flujos_humanos/` y `documentation/database_access/`:
  - **Simple:** `BlIstSIAGF.md` (2 flujos, 8.4 KB) — caso mínimo, mayormente no resuelto.
  - **Mediano, con acceso a datos y dependencia externa no resuelta:** `WebFiscalizacionRemota.md` (8 flujos) — un flujo con evidencia transaccional confirmada y 15 límites no resueltos de infraestructura.
  - **Complejo/a escala:** `WebMEDDespacho.md` → `WebMEDDespacho-part-000001.md` (589 flujos, partición de 8.7 MB) y `WebSUBSubsidioNew-part-000001.md` (9.9 MB, el archivo más grande del árbol completo).
  - **Acceso a datos limpio:** `database_access/WebPREComite_vbproj.md` (14 puntos de acceso, tabla legible).
  - **Vista general existente:** `README.md`, `PROJECT_OVERVIEW.md`, `SOLUTION_STRUCTURE.md`, `WEBFORMS_MAP.md`, `CONFIGURATION_SUMMARY.md`, `UNRESOLVED_FINDINGS.md`, `ai_context/SYSTEM_CONTEXT.md`.
- Medición real: `documentation/` completo = 226 477 973 B (216.0 MB); `flujos_humanos/` = 159 693 893 B (152.3 MB, 70.5% del total), 195 archivos.
- Código real leído (no asumido): `legacy_documenter/exporters/markdown_exporter.py`, `legacy_documenter/exporters/technical_documentation_renderer.py`, `legacy_documenter/documentation/human_flow_documentation.py`, `legacy_documenter/documentation/human_documentation_scaling.py`, `legacy_documenter/exporters/_documentation_partitioning.py`, `legacy_documenter/context/system_context_builder.py` (origen de `ai_context/SYSTEM_CONTEXT.md`).

## 18. Conclusión

La documentación actual es técnicamente correcta y honesta (nunca inventa, siempre declara lo no resuelto), pero no cumple el objetivo humano de V5.2 tal como existe hoy: no hay vista general, el detalle técnico domina visualmente incluso en la vista para desarrolladores, y a escala real de IST una parte central (`flujos_humanos/`) es literalmente inmanejable en tamaño de archivo. Ninguno de estos problemas requiere descartar el Evidence Core ni la lógica de extracción/resolución existente — son, en su totalidad, problemas de presentación/generación, exactamente el espacio de problema que V5.2 (Template/Profile/Renderer) está diseñado para resolver. La baseline queda lista para que R1 tome las decisiones arquitectónicas listadas en la sección 16.

V5_2_R0_BASELINE_READY
