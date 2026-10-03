# V5.3 R0.1 — Completar mediciones y continuidad

Estado final: **V5_3_R0_1_READY_FOR_CONTRACT**

Ronda de diagnóstico. No se modificó código de producción, tests, `PROJECT_STATE.json`, manifests, IDs ni Evidence Core. Sin IA, sin commit/push/tag. Instrumentación y scripts temporales solo en el scratchpad de la sesión (fuera del repo); nunca tocaron producción (se envolvieron funciones en tiempo de ejecución).

## 1. Correcciones de continuidad

- **A.** `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md` corregido (solo ese informe): D-8 pasa a **RESUELTO** (causa = `PermissionError` transitorio en `os.replace`; corrección `_replace_with_retry`; cobertura en V5.2 R4.2; estado ya en `PROJECT_STATE.json` desde R4.4). `PROJECT_STATE.json` no se tocó (no hay evidencia nueva).
- **B.** Prompts movidos a `prompts/V5/` (archivos aún sin versionar, movidos con `mv`): `V5_3_R0_EMPIRICAL_BASELINE.md` y `V5_3_R0_1_MEASUREMENT_COMPLETION.md`. Se actualizó la fila correspondiente y D-10 del informe R0. Prompts históricos no movidos.

## 2. Estado de prompts

| Archivo | Ubicación |
|---|---|
| R0 | `prompts/V5/V5_3_R0_EMPIRICAL_BASELINE.md` |
| R0.1 | `prompts/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md` |
| `prompts/V5_0/` | solo prompts históricos (≤ V5.2) |

## 3. Pendiente de Git (sin commit en esta ronda)

Rama `main`, HEAD `6c32c4c` (tag `v5.2`). `git diff --stat`: vacío (nada versionado modificado). Sin versionar, para decidir tras revisión humana:

1. `docs/V5/V5_2_GIT_CLOSURE_RESULT.md`
2. `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md` (modificado en R0.1)
3. `docs/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md` (este)
4. `prompts/V5/V5_3_R0_EMPIRICAL_BASELINE.md`
5. `prompts/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md`

## 4. Tiempos reales por etapa

Corrida controlada única válida: `python main.py full <IST oficial> --output <ruta corta> --verbose`, sin IA, mismo código que V5.2 (HEAD `6c32c4c`). Arnés temporal: envuelve las funciones de stage/sub-stage con `perf_counter` y contadores de E/S del proceso (`GetProcessIoCounters`) y memoria (`PeakWorkingSetSize`). Sin `psutil` (no se instaló nada).

**Incidencia de la medición (corrida 1, descartada):** la primera corrida terminó `PARTIAL` (exit 1): `documentation_v52` falló con `FileNotFoundError` en el `.tmp` de escritura atómica. La ruta del archivo medía **exactamente 260 caracteres** (salida en el scratchpad + `developer/modules/<módulo>/files/...`): límite MAX_PATH de Windows. No fue un fallo del pipeline en sí, sino de la longitud de la ruta de salida; se repitió con ruta corta. Ver D-13.

| Stage | Duración (s) | % del total | Nota |
|---|---:|---:|---|
| SCAN | 1,00 | 0,1 | |
| EXTRACTION | 61,50 | 3,5 | 42 495 lecturas, 324 MB |
| CALL_RESOLUTION | 1,12 | 0,1 | |
| WEB_ENTRY_RESOLUTION | 1,61 | 0,1 | |
| DATABASE_RESOLUTION | 1,70 | 0,1 | |
| FLOW_RESOLUTION | 9,33 | 0,5 | |
| DEPENDENCY_RESOLUTION | 0,30 | <0,1 | |
| **EXPORT** | **63,41** | 3,6 | |
| ↳ `index/` JSON (JSONExporter) | 29,26 | 1,7 | 996 MB |
| ↳ Markdown legado (MarkdownExporter) | 0,33 | <0,1 | |
| ↳ **Evidence Core** | 33,82 | 1,9 | log: build 22,2 / validate 0,8 / persist 10,7; relee 15 138 archivos (45 984 lecturas, 332 MB); 1 057 MB |
| **CONTEXT** | **580,02** | 33,0 | |
| ↳ `context/projects.json` | 0,75 | <0,1 | |
| ↳ `ai_context` (SystemContextBuilder) | 13,73 | 0,8 | 279 MB |
| ↳ `consumer_projection` | 565,36 | 32,2 | hidrata 12 642 flows; 199 MB |
| **DOCUMENTATION** (total) | **1 034,93** | 59,0 | |
| ↳ DOCUMENTATION legacy (renderers particionados) | ≈ 0,7 | <0,1 | suma de `sync_generated_partition_directory` ×4 |
| ↳ **HUMAN_DOCUMENTATION** | ≈ 547,6 | 31,2 | por diferencia (total − v52 − legacy); hidrata 12 642 flows otra vez. Fuera de hidratación: índice 0,03 + partitions 0,99 + sync 0,74 |
| ↳ **documentation_v52** | 486,63 | 27,7 | 46 567 md + manifest; 67 114 operaciones de escritura, 89 MB |
| **FINAL_SUMMARY** | 0,01 | <0,1 | |
| **Suma de stages** | 1 754,93 | | |

- Hidratación de flows: `EvidenceHydrator.hydrate_flow` = **25 284 llamadas (2 × 12 642), 1 099,0 s acumulados**, ≈ 98,7 % de `consumer_projection` + `HUMAN_DOCUMENTATION` (≈ 1 113 s) y **62,6 % del total**. Es la mayor oportunidad medida (D-5 de R0 confirmada con dato).
- Desglose por bloques: proyecciones derivadas (CONTEXT + DOCUMENTATION) = 1 615 s = **92 %**; análisis puro (SCAN…DEPENDENCY) = 75,9 s = **4,3 %**; EXPORT = 63,4 s = 3,6 %.
- Nota: el tiempo `SCAN…DEPENDENCY` (75,9 s) es inferior al 184 s de `repository.json` de la corrida previa. **Varianza observada entre mis dos corridas** (EXTRACTION 129,8 s → 61,5 s; Evidence Core 108,8 s → 33,8 s): los mismos archivos fuente, con caché de disco del SO frío vs. caliente. La corrida 1 (incompleta) se conserva solo como evidencia de varianza. Con dos muestras no se puede fijar un baseline con desviación; cualquier meta de R1 debe medirse en frío y en caliente.
- `hydrate_flow` se llamó exactamente 2 × 12 642 veces (dos pasadas completas); no se verificó qué stage hace cada pasada más allá de `consumer_projection` y `HUMAN_DOCUMENTATION`, que el código muestra que hidratan todos los flows.

## 5. Duración total

**1 755,37 s = 29 min 15 s** (desde antes del primer stage hasta el retorno de `main()`); wall del lanzador 1 758,40 s. Corrida 1 (fallida por MAX_PATH): 1 366 s, solo indicativa.

Volumen (todo el proceso): lecturas 88 535 operaciones / 659,5 MB; escrituras 73 085 operaciones / 2 852,7 MB. **Memoria pico (working set) 2,62 GB**, pagefile pico 2,85 GB (alcanzada durante EXPORT, no crece después). No se midió "archivos leídos/escritos" exactos, solo operaciones de E/S del proceso (la API no da conteo de archivos distintos).

## 6. Estado de process exit

| Dato | Valor |
|---|---|
| Exit code | **0** (corrida 2; corrida 1: 1 = `PARTIAL` por MAX_PATH) |
| `FINAL_SUMMARY` → retorno de `main()` | 0,37 s |
| Retorno de `main()` → proceso terminado | 2,48 s (incluye volcado de la medición y liberar ≈ 2,6 GB) |
| Hilos vivos al final | solo `MainThread` |
| `multiprocessing.active_children()` | `[]` |
| Procesos hijos (CIM, consultado con el proceso vivo tras `main()`) | ninguno |

Resultado: **no se reproduce** el antecedente "FINAL_SUMMARY=SUCCESS y proceso vivo" a escala IST (una corrida). Sigue sin ser prueba de que no ocurra con terminal/proceso externo; es un dato adicional, no un cierre definitivo (un punto de medición, no una garantía).

## 7. Experimentos de impacto incremental

Método: copia del baseline IST en el scratchpad (15 138 archivos, 668 MB; baseline oficial intacto). Por variante: se aplica el cambio, se ejecuta SCAN→DEPENDENCY (análisis puro, sin export), se calcula un *digest* y se compara con el digest de la copia sin cambios (que reproduce los conteos del baseline: 12 642 flows, 170 020 paths, 12 662 entry points, 259 proyectos), luego se revierte. Son **mediciones de diferencias reales en los índices**, no estimaciones, salvo "documentos potencialmente afectados" (calculado).

| # | Cambio | Archivos cambiados | Símbolos | Llamadas (entradas cambiadas) | Flows cambiados | Proyectos | Otros |
|---|---|---:|---|---|---:|---|---|
| 1 | Cuerpo: +1 línea en `Page_Load` de `ucValMo005.ascx.vb` | 1 | sin cambio | 48 (24 desaparecen, 24 aparecen: solo cambia el **número de línea**; 0 cambian de resolución) | **3** (y 3 entry points) | 1 (en flows) | dependencias sin cambio |
| 2 | Renombre de método: `blIndemnizacion.txtraerrpa` → `…Renombrado` | 1 | 1 archivo (clave del resolver cambia) | 23 (13 cambian de resolución, 8 archivos llamantes en 3 proyectos) | **8** | 3 | `functional_dependencies` cambia; `flow_unresolved` −31 |
| 2b | Firma: se añade un parámetro a `txtraerrpa` (mismo nombre) | 1 | **sin cambio** | **0** | **0** | 0 | **ningún índice cambia** |
| 3 | `.ascx`: texto de una etiqueta | 1 | — | 0 | 0 | 0 | ningún índice cambia |
| 3b | `.ascx`: `Inherits=` apunta a clase inexistente | 1 | — | 0 | 0 | 0 | `webforms` (1) y `dependencies` cambian |
| 4 | `.vbproj`: `RootNamespace` | 1 | 57 archivos con símbolos distintos (`effective_namespace`) | 0 | 0 (251 flows atraviesan el proyecto; ninguno cambió) | 1 | `dependencies` cambia |
| 5a | Archivo nuevo con clase única, añadido al `.vbproj` | 1 nuevo + `.vbproj` | +1 archivo | 0 | 0 | 1 (`.vbproj`) | `dependencies` cambia |
| 5b | Archivo nuevo con clase duplicada (`blIndemnizacion`) en el mismo proyecto | 1 nuevo + `.vbproj` | +1 archivo | 13 cambian de resolución (8 archivos, 3 proyectos) | **8** | 3 | `flow_unresolved` −31 |
| 5c | Archivo `.vb` eliminado (queda referenciado en `.vbproj`) | 1 eliminado | −1 archivo | 30 desaparecen | **4 removidos** (+4 entry points) | 1 | `flow_unresolved` −30 |

Lecturas relevantes:

- Un cambio de cuerpo **sin** modificar símbolos ni llamadas ya cambia evidencia: el ID de llamada (`CAL-…`) incluye la línea (`evidence/builder.py`), y los flows incluyen esa evidencia. Insertar una línea al inicio de un archivo desplaza **todas** las llamadas posteriores de ese archivo. La invalidación "solo cuerpo = solo ese archivo" es cierta para la **resolución**, pero la **evidencia/flows del archivo deben regenerarse**.
- El alcance real medido es pequeño y acotado en 1, 2, 5b, 5c (3–8 flows de 12 642 = 0,02–0,06 %) y cero flows en 2b/3/3b/4/5a. El peor caso medido, renombrar un método compartido, afectó 8 archivos en **3 proyectos distintos** (cruzan proyectos): el alcance `project` no es suficiente para cambios de nombre; sí lo es para cuerpo/`.ascx`/`.vbproj` en estos casos.
- La heurística "flows que tocan las clases del archivo cambiado" (prefijos de nodos de paths) **no es fiable como predictor** de los flows que realmente cambian (subestima 1, 2, 5b; en 4 sobreestima 251 vs 0). No se debe usar para invalidación; en R1 hace falta un índice inverso real (D-7).
- Documentos potencialmente afectados (calculado, no medido): v52 tiene 46 567 documentos; los que mencionan el componente del caso 1 (`ucvalmo005`) son 4, los del proyecto del caso 4 (`webmedvalorizacion`) 235 y los del caso 2 (`blindemnizacion`) 271 (coincidencia por ruta en `MANIFEST.json`). Por flow cambiado se regenera además su documento humano (`flujos_humanos`) y su partición de `consumer_projection`/`ai_context`. No se regeneró documentación para las variantes.
- Escalado: los experimentos cambian 1 archivo. Un cambio de rama (muchos archivos) no se midió; se mantiene el umbral/fallback a `repository` (R0).
- Tiempo del análisis puro sobre la copia: 68–97 s por variante (caché caliente), para contexto.

## 8. Line endings

**Censo IST (solo tipos analizados: `.vb .aspx .ascx .master .vbproj .sln .config`, 8 542 archivos):** 8 538 CRLF, 3 mixtos, 1 sin saltos de línea, 0 LF puro; 1 449 con BOM UTF-8; 3 con `\r` suelto. El repositorio IST es esencialmente CRLF homogéneo. (Censo de todos los archivos, 18 455: 14 443 CRLF, 251 LF, 3 115 "mixtos" — casi todos binarios `.gif/.png/.cache`, que no deben normalizarse.)

**Experimento reproducible** (67 archivos muestreados, semilla fija, `.vb/.aspx/.ascx/.vbproj`; extracción real):

| Variante | Hash crudo cambia | Hash normalizado (CRLF/CR→LF) cambia | Extracción (symbols/calls/web_events/db/webforms/projects) |
|---|---|---|---|
| CRLF→LF | sí (todos) | **no** | idéntica (byte a byte) |
| a CRLF (ya lo están) | no | no | idéntica |
| añadir/quitar BOM | sí | **sí** (la normalización no lo oculta) | **cambia** (symbols, calls, web_events) |
| espacios al final de línea | sí | sí | idéntica en la muestra |

Conclusiones:

- **Falsos positivos con hash crudo:** cambios solo de line endings (LF↔CRLF, p. ej. `autocrlf`, checkout en otra plataforma): hash distinto, extracción idéntica → recomputación inútil pero correcta. En IST hoy casi no ocurren (CRLF homogéneo), pero un checkout en Linux los produciría en ~100 % de los archivos.
- **Falsos negativos potenciales con hash normalizado:** ninguno por LF/CRLF en la extracción (los extractores leen con `read_text` + `splitlines`, que ya normalizan). El BOM y el espacio final **sí** deben seguir cambiando el hash (el BOM altera la extracción; el espacio no, pero es más seguro no ocultarlo). Riesgo: normalizar a ciegas binarios (`.gif/.png`) daría falsos negativos → normalizar solo tipos de texto analizados.
- **Recomendación R1:** mantener `SourceArtifact.sha256` crudo como hash de integridad/compatibilidad; añadir un segundo hash **de contenido semántico** (solo para tipos de texto de la lista de scan: CRLF/CR→LF, **sin** tocar BOM ni espacios) como clave de invalidación de extracción, con fallback al crudo. Decisión final en contrato R1. No se cambió el contrato de hash.

## 9. Propuesta de versionado del analizador (sin implementar)

Hoy no existe constante de versión (R0). No usar solo el commit de Git (un commit que no cambia el analizador invalidaría todo; un cambio sin commit no invalidaría nada; un árbol sucio no tiene identidad estable). Propuesta: **cuatro versiones independientes, enteras y declaradas en código**, más un fingerprint de configuración:

| Componente | Qué cubre | Dónde | Cuándo se incrementa |
|---|---|---|---|
| `ANALYZER_VERSION` | extractores, `CallResolver`, resolvers de entry/DB/flow/dependencias, normalización de namespaces/partial | constante única en un módulo de versiones (p. ej. `legacy_documenter/versions.py`) | todo cambio que altere `index/` o evidencia |
| `EVIDENCE_SCHEMA_VERSION` | contrato y esquema de `evidence/` (ya existe schema/contrato V5.1 en `EVIDENCE_MANIFEST`; reutilizar ese valor) | el existente | cambio de esquema/IDs |
| `RENDERER_VERSION` | renderers legados, `consumer_projection`, `ai_context`, `HUMAN_DOCUMENTATION`, `documentation_v52` (uno por familia si conviene) | constantes por renderer | cambio de salida de un renderer |
| `TEMPLATE_PROFILE_VERSION` | plantillas/perfiles/idioma de v52 | derivar un hash determinista del contenido de `documentation_v52/defaults/*` + perfil + idioma | automático (hash del contenido) |
| `config_fingerprint` | `DEFAULT_EXCLUDES`, `--exclude` ordenado, `--flow-max-depth` | hash del JSON canónico | automático |

Clave de caché de una unidad = hash(contenido semántico de entrada, los componentes aplicables de arriba, `config_fingerprint`). Un test (en R1/R2) debería fallar si cambia el código de extracción sin cambiar `ANALYZER_VERSION` (p. ej. hash de los archivos de `extractors/` y `analysis/` fijado en el test). El commit Git se registra como metadato informativo, no como clave.

## 10. Alcance real de `CallResolver`

Del código (`legacy_documenter/analysis/call_resolver.py`, sin modificar) y confirmado con los experimentos 2/2b/4/5:

**Entradas de `symbols` que usa el resolver:** `kind` (solo `class`/`module` para el índice de tipos; `members[].kind ∈ {sub, function}` para métodos), `name`, `effective_namespace`/`namespace` (nombre completo), `members[].name` y `project_path` (solo copiado a `resolved_project`). **No usa** cuerpos, parámetros, tipos de retorno, accesibilidad, modificadores, `inherits`/`implements` ni líneas. De `calls` usa `receiver`, `receiver_path`, `method_name`, `containing_class/method`, `candidates`, y las instanciaciones del mismo archivo (`variable_types`).

| Cambio | ¿Obliga a recalcular la resolución global? | Evidencia |
|---|---|---|
| Solo cuerpo (sin tocar nombres) | **No** para resolución de otros archivos. Sí re-resolver las llamadas del propio archivo y regenerar su evidencia | exp. 1: 0 cambios de resolución |
| Cambio de firma sin cambiar nombre/tipo de miembro | **No**; el modelo no contiene parámetros → salida idéntica | exp. 2b: 0 diferencias |
| Renombre de método/miembro | **Sí**, para toda llamada cuyo receptor resuelva a esa clase (8 archivos / 3 proyectos medido); acotable buscando llamadas con ese `method_name` | exp. 2 |
| Símbolo (clase) nuevo | **Sí** si su nombre simple o completo coincide con algún `type_name`/receptor existente (ambigüedad → `unresolved`); si es nombre único, no cambia nada | exp. 5a (0) vs 5b (13) |
| Símbolo eliminado | **Sí** para llamadas que lo apuntaban (y flows que lo atraviesan); las del resto, no | exp. 5c (30 llamadas, 4 flows) |
| Cambio de namespace / `RootNamespace` | **Sí en teoría** (cambia `full_name`, que es el target); en el caso medido ninguna llamada cambió, pero 57 archivos de símbolos sí → recomputar por proyecto como mínimo | exp. 4 |
| Clase `Partial` | Resolver agrupa por nombre; cambiar miembros de una parte altera el conjunto `members` de ese símbolo → tratar como renombre/alta de miembro. No medido | — |
| Llamadas nuevas/eliminadas | solo afectan al archivo emisor y a los flows que las recorren | exp. 1 |

**Criterio seguro propuesto:** guardar por archivo una *clave del resolver* = `(kind, name, namespace efectivo, project_path, {(kind,nombre) de miembros sub/function})`. Si esa clave no cambia, la resolución global no cambia (probado con 1, 2b, 3). Si cambia, recalcular todas las llamadas con `method_name`/tipo afectado (índice inverso nombre→llamadas) o, por defecto conservador, todo el `CALL_RESOLUTION` (1,1 s: **el stage completo cuesta ~1 s; recalcularlo siempre es barato**). El coste real está aguas abajo (flows → proyecciones), no en el resolver. `FLOW_RESOLUTION` (9,3 s) también es barato. Por tanto en R1 conviene recalcular SCAN-resolvers completos a partir de extracción cacheada por archivo y limitar la caché inteligente a **proyecciones**.

Nota sobre el coste de extracción con caché por archivo: extracción 61,5 s (3,5 %) — ahorro menor que hidratación/proyecciones (≈ 92 %).

## 11. Contrato propuesto: incremental vs full

**Invariante:** `mismo input + misma versión (analyzer/schema/renderer/template) + misma configuración` ⇒ salida incremental final **equivalente** a una corrida `full` del mismo estado.

"Equivalente" significa:

1. **IDs:** conjunto de IDs de evidencia, flows, paths, calls, documentos idéntico (ya deterministas `sha256_id`).
2. **Relaciones:** mismas aristas/dependencias (`functional_dependencies`, `dependencies`, paths), mismo orden canónico.
3. **Estados:** mismos `confirmed/inferred/unresolved`; `flow_unresolved`/`unresolved_boundaries` idénticos (un archivo nuevo debe poder resolver un `unresolved` previo, como en exp. 5a/5b/5c).
4. **Particiones lógicas:** mismas particiones de evidencia/consumer/documentos (incluidas las que quedan vacías y las huérfanas eliminadas).
5. **Documentación:** `documentation_v52` y `flujos_humanos`: mismo contenido y `sha256` por documento; `MANIFEST.json` idéntico.
6. **Manifests:** `EVIDENCE_MANIFEST.json`, `documentation_v52/MANIFEST.json`, `CONSUMER_PROJECTION.json`: idénticos salvo campos no deterministas declarados explícitamente (p. ej. `duration_seconds`, marcas de tiempo, métricas de ejecución, metadatos de caché), que deben vivir fuera de los artefactos byte-estables.
7. **Verificación:** test de equivalencia (full vs incremental sobre fixture y, por muestra, sobre IST), y fallback a `full` ante cualquier duda (cambio de versión/config, caché corrupta/parcial, cambio de rama masivo).

No se implementó la comparación.

## 12. Riesgos

| Riesgo | Nota |
|---|---|
| Línea en el ID de llamada | Insertar/quitar una línea cambia IDs `CAL-…` y evidencia de flows aunque no haya cambio semántico (exp. 1: 3 flows). El diseño de invalidación debe incluir la posición de línea en el archivo cambiado. |
| Heurística de alcance no fiable | La aproximación por nodos de paths falló (§7). Sin índice inverso real no se debe invalidar localmente. |
| MAX_PATH (Windows) | La salida de `documentation_v52` puede superar 260 caracteres y fallar de forma confusa (`FileNotFoundError` del `.tmp`); afecta también a cualquier caché basada en rutas por documento. |
| Hidratación repetida | Dos hidrataciones completas (1 099 s) dominan; una caché de proyecciones sin resolver esto no mejora el costo principal. |
| Varianza por caché del SO | Diferencias ×2–3 entre corridas idénticas; mediciones de R1 deben separar frío/caliente. |
| Un solo baseline | Una corrida válida de referencia; sin desviación estándar. |
| BOM | Altera la extracción; un hash normalizado ingenuo daría falsos negativos. |
| Cruce de proyectos | Un renombre afecta varios proyectos (3 medido) → el scope `project` no basta para nombres. |
| Proyecciones y escritura de 46 k archivos | 486 s; 67 k operaciones de escritura; caché por documento-archivo puede ser tan lenta como regenerar (R0). |
| Generalización | 9 cambios sobre 1–2 componentes; no se midieron cambios de rama masivos, `web.config`, ni `Partial`. |
| Process exit | Una medición; no reproduce el antecedente, sin garantía. |

## 13. Deuda técnica clasificada

| ID | Hallazgo | Clase |
|---|---|---|
| D-13 (nuevo) | `documentation_v52` falla con `FileNotFoundError` si la ruta de salida + ruta del documento supera MAX_PATH (260) en Windows; el stage reporta `RENDERER_FAILURE` sin indicar la causa real. No se corrigió (ronda de medición). Workaround: `--output` corto. | **NEXT_ROUND** (validación/mitigación de ruta; decidir en contrato) |
| D-5 | Hidratación duplicada de flows: 1 099 s = 62,6 % del total | **NEXT_ROUND** (prioridad máxima medida) |
| D-1 | Sin tiempos por stage persistidos (ahora medidos externamente; el arnés es temporal) | **NEXT_ROUND** |
| D-2 | Sin versión de analizador/renderer/plantilla (propuesta en §9) | **NEXT_ROUND** |
| D-7 | Sin índice inverso archivo→flows/proyectos (heurística sustituta falló) | **NEXT_ROUND** |
| D-14 (nuevo) | IDs de llamada dependen de la línea: un cambio de una línea regenera evidencia de todo el archivo | **NEXT_ROUND** (decidir si se mantiene el contrato de ID o se aísla la invalidación) |
| D-6 | `documentation_v52` escribe siempre 46 567 archivos (486 s) | **CURRENT_PHASE** |
| D-4 | `CallResolver` global: no es el cuello (1,1 s); criterio de invalidación en §10 | **OBSERVATION** (la restricción de R0 queda relajada por medición) |
| D-3 | `duration_seconds` no determinista en `repository.json` | **NEXT_ROUND** |
| D-9 | Process exit: medido a escala IST, no reproducido | **OBSERVATION** |
| D-8 | Intermitencia de escritura | **RESUELTO** (corregido el informe R0) |
| D-11 | JSON vs JSONL (7 s de parseo por ~1 GB; lectura dominada por nº de archivos) | **FUTURE_PHASE** |
| D-12 | `technical_documentation_renderer.py` alto riesgo | **FUTURE_PHASE** |
| — | BLOCKING | ninguno |

## 14. ¿Datos suficientes para R1?

**Suficientes.** Cubiertos: cronometraje por stage/sub-stage (§4); process exit a escala IST (§6); impacto incremental real de 9 cambios (§7); decisión de line endings (§8); versión del analizador (§9); alcance del `CallResolver` (§10); contrato incremental vs full (§11). Limitaciones que R1 debe asumir (no bloquean): un solo baseline válido con varianza frío/caliente ×2–3; no se midieron cambios de rama masivos, `web.config`, `Partial` ni `.sln`; docs afectados solo calculados. Hallazgo que reorienta el diseño: el 92 % del tiempo es proyección derivada (con hidratación duplicada = 62,6 %), y `CALL_RESOLUTION` completo cuesta ~1 s; la mayor ganancia está en proyecciones/hidratación, no en invalidación fina de la resolución.

## 15. Archivos modificados

| Archivo | Cambio |
|---|---|
| `docs/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md` | Creado (entregable único) |
| `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md` | Corrección de continuidad (D-8, D-10, fila de archivos sin versionar) |
| `prompts/V5/V5_3_R0_EMPIRICAL_BASELINE.md` | Movido desde `prompts/V5_0/` |
| `prompts/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md` | Movido desde `prompts/V5_0/` (destino indicado por el prompt) |

Sin cambios en código, tests, `PROJECT_STATE.json`, manifests, IDs ni documentos previos. Temporales (scratchpad, fuera del repo): `harness.py`, `launch.py`, `digest.py`, `variants.py`, `compare.py`, `eol_*.py`, digests, copia de IST (borrada). Salida generada de la corrida (≈ 2,8 GB) creada en una carpeta del repo por un error de ruta mío y **eliminada** al terminar; `git status` solo muestra los archivos de §3. El repositorio legado no se modificó (solo lectura). No se escribió en `C:\PruebasLegacyMapper`.

## 16. Confirmación

**No se implementó caché, análisis incremental, invalidación, índices persistidos nuevos, scopes, fingerprints ni versionado.** No se modificó `CallResolver` ni Evidence Core. Sin IA. Sin commit, tag ni push. `v5_3_started` permanece `false`. Ronda detenida para revisión humana.

**V5_3_R0_1_READY_FOR_CONTRACT**
