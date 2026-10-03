# V5.3 R0 — Baseline empírico para motor incremental y caché

Estado final: **V5_3_R0_READY_FOR_CONTRACT**

Ronda de diagnóstico. No se modificó código de producción, tests, manifests, IDs ni Evidence Core. No hubo commit, push, tag ni IA. No se repitió la extracción IST.

## 1. Estado Git

| Dato | Valor |
|---|---|
| Rama | `main` |
| HEAD | `6c32c4c9c6fe2642e56e9f33739a95d43d6ae411` (`chore(v5.2): close documentation profiles phase`) |
| Tag `v5.2` | existe y apunta a `6c32c4c9…` (`git rev-list -n1 v5.2`) → V5.2 = tag publicado |
| Árbol | limpio salvo 2 archivos sin versionar |
| Sin versionar | `docs/V5/V5_2_GIT_CLOSURE_RESULT.md` (creado tras el cierre; **no resuelto**, solo registrado); `prompts/V5/V5_3_R0_EMPIRICAL_BASELINE.md` (este prompt; movido desde `prompts/V5_0/` en R0.1 para cumplir la convención `prompts/V5/` de V5.3) |

Este documento será un tercer archivo sin versionar al terminar la ronda.

## 2. Baseline utilizado

- Repositorio IST oficial: `C:\Users\cgalianj\source\IST_40\Operacional` (`main`). Lectura solo.
- Última corrida IST válida completa: `C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_1_validation\ist_full_run\` (29-09-2026; `RUN_SUMMARY.json` `status=SUCCESS`, 13 stages, IA `NOT_RUN`). Producida por el código de V5.2 (R3.4.1), anterior a los cambios de R4.2 (solo `atomic_write`/i18n) y R4.3 (solo estado/tests). No se regeneró.
- Fuera del repo hay otras corridas (`v5_1_r3_2_run_a/b`, `v5_2_r2_real_run*`, `v5_2_r4_2_regen` = solo regeneración de `documentation_v52`). No se usaron salvo `v5_2_r3_1_validation/run.log` (único log con tiempos, ver §5).
- IST en esa corrida: 15 138 archivos escaneados, 1 409 directorios ignorados, 259 `.vbproj`, 113 `.sln`, 4 328 `.vb`, 3 165 `.ascx`, 177 `.aspx`.

## 3. Pipeline actual

Orquestación: `cli/full_pipeline.py::run_full_pipeline` (resiliente) y `main.analyze_repository` (compatibilidad); ambas llaman las mismas funciones de `cli/pipeline_stages.py`. `analyze` = SCAN…EXPORT + CONTEXT (según `pipeline_stages`, sin DOCUMENTATION; no se verificó `main.analyze_repository` línea a línea); `full` = todo + IA opt-in.

| Stage | Input | Output | Depende de | ¿Se recalcula siempre? | ¿Reutilizable? | Qué la invalida |
|---|---|---|---|---|---|---|
| SCAN | árbol de archivos (`rglob`), `DEFAULT_EXCLUDES`, `--exclude` | `files` (ruta, ext, tamaño, tipo) | FS, config de excludes, `FileClassifier` | sí, completo, sin hash | sí (lista de archivos ya persistida en `index/files.json`) | alta/baja/renombre de archivo; cambio de excludes/clasificador |
| EXTRACTION | cada archivo (`solution`, `vb_project`, `vb_source`, `aspx/ascx/master`, `web_config`) + 3ª pasada por `.vb` (calls, web events, database) | symbols, projects, solutions, webforms, configuration, calls crudas, web_events, data_access_indexes; luego namespaces y partial classes (globales) | contenido del archivo (extracción por archivo, tolerante a error); `apply_project_namespaces` y `consolidate_partial_symbols` cruzan proyecto↔símbolo | sí, lee 100 % | por archivo (fase 1) sí; normalización global no | cambio de contenido del archivo; de los `.vbproj` que lo incluyen; versión de extractores |
| CALL_RESOLUTION | calls, symbols | calls resueltas, functional_dependencies | **todos** los symbols (resolución global) | sí | no localmente | cualquier símbolo agregado/quitado/renombrado; cambio de una llamada |
| WEB_ENTRY_RESOLUTION | webforms, symbols, web_events, calls resueltas | entry_points, event_bindings, functional_dependencies | CALL_RESOLUTION | sí | por entry point, con dependencias | cambio del `.aspx/.ascx`, su code-behind o las llamadas alcanzables |
| DATABASE_RESOLUTION | data_access_indexes, projects | data_access, stored_procedures, sql_operations, data_parameters, functional_dependencies | EXTRACTION (independiente de calls) | sí | por archivo/proyecto | cambio del archivo fuente o de la conexión en `web.config`/proyecto |
| FLOW_RESOLUTION | entry_points, calls, data_access, SPs, sql, functional_dependencies, `flow_max_depth` | functional_flows, functional_paths, flow_summary, flow_unresolved | CALL + WEB_ENTRY + DATABASE (las tres) | sí | por flow, con grafo de alcance | cualquier archivo alcanzable desde el entry point; `--flow-max-depth` |
| DEPENDENCY_RESOLUTION | solutions, projects, symbols, webforms | dependencies (26 960) | EXTRACTION | sí | por proyecto | `.sln`, `.vbproj`, referencias |
| EXPORT | `indexes` en memoria | `index/*.json` (22), `documentation/*.md` (MarkdownExporter), `evidence/` (25 archivos + manifest) | todos los anteriores | sí; **reescribe todo** | ver §4 y §8 | cualquier cambio aguas arriba |
| ↳ Evidence Core | `indexes` + **sha256 real de cada archivo fuente** (relee los 15 138) | 24 particiones + `EVIDENCE_MANIFEST.json` (`partition_sha256`) | `indexes`, `repo_root` | sí; borra manifest previo y escribe al final | la partición como unidad; IDs son deterministas (`sha256_id`) | idem EXPORT |
| CONTEXT | `indexes` | `context/projects.json`, `ai_context/*` (4 JSON + md), `consumer_projection/` (manifest + 26 partes) | `indexes` completos; hidrata **todos** los flows | sí | por flow | cualquier cambio de flow |
| DOCUMENTATION | `indexes` (+ `evidence/external_dependencies.json`) | `documentation/` particionada (legacy) + `HUMAN_DOCUMENTATION` (hidrata todos los flows) + `documentation_v52/` (46 567 md + `MANIFEST.json`) | `indexes`, plantillas/perfiles v52 | sí; los subdirectorios se sincronizan (borran huérfanos) | por documento (v52 ya tiene sha256 por archivo) | evidencia del componente; plantilla/perfil; idioma |
| AI_INTERPRETATION / PROPOSAL_GENERATION | `output/ai_context/*` | `proposals/` | CONTEXT + `--allow-ai-interpretation` | **NOT_RUN** salvo opt-in | fuera de alcance de V5.3 | — |
| FINAL_SUMMARY | resultados de stages | `RUN_SUMMARY.json/.md` | todos | sí | no | — |

**Cachés/índices persistidos hoy:** ninguno usado como caché. No existe ningún mecanismo de cache/incremental en `legacy_documenter/` (grep `cache|fingerprint|incremental|memoiz`: solo un contador informativo en `documentation/hierarchical.py` de V3 y la nota de diseño en `evidence/persistence.py`). El único uso de hash de contenido hacia adelante es `SourceArtifact.sha256` (Evidence Core) y `partition_sha256`/manifest v52.

## 4. Artefactos persistidos existentes (corrida `ist_full_run`)

| Directorio | Archivos | Bytes | Comentario |
|---|---:|---:|---|
| `index/` | 22 | 996 416 389 | JSON legado (identidad byte a byte con V4.3, D-01) |
| `evidence/` | 25 | 1 057 049 755 | Evidence Core V5.1: 24 particiones + `EVIDENCE_MANIFEST.json` |
| `documentation/` (legado) | 876 | 226 477 973 | incluye `flujos_humanos/` 195 archivos, 159 693 893 B |
| `documentation_v52/` | 46 568 | 69 162 272 | 46 567 `.md` (59 097 181 B) + `MANIFEST.json` (10 065 091 B) |
| `consumer_projection/` | 27 | 198 913 444 | manifest + 26 partes |
| `ai_context/` | 5 | 279 178 592 | ARCHITECTURE_GRAPH, FUNCTIONAL_FLOWS, TRACEABILITY, SYSTEM_CONTEXT |
| `context/` | 1 | 896 897 | |
| `RUN_SUMMARY.*` | 2 | ~2 012 | |
| **Total** | **47 526** | **2 828 097 334 (≈ 2,63 GiB)** | |

- **Archivos de evidencia:** 25 (1 057 049 755 B). Mayores: `functional_dependencies` 200,5 MB, `calls` 147,9 MB, `call_identities` 141,1 MB, `functional_paths` 97,5 MB, `flow_unresolved` 92,8 MB, `functional_flows` 86,3 MB, `unresolved_boundaries` 79,8 MB, `data_parameters` 75,4 MB.
- **Documentos V5.2:** 46 567 `.md`, 59 097 181 B (`developer/` 46 561, `general/` 5, `README.md`).
- **Manifests existentes:** `evidence/EVIDENCE_MANIFEST.json` (conteos por entidad + `partition_sha256` de las 24 particiones; 2 625 B), `documentation_v52/MANIFEST.json` (sha256 y tamaño de cada uno de los 46 567 archivos + `profiles`, `gaps`, `warnings`), `RUN_SUMMARY.json` (solo estados por stage, sin tiempos). `output_manifest.py` (V4.2) existe para otro uso.
- **Índices existentes:** `index/*.json` (22) y `evidence/*.json`; ninguno es un índice de consulta (todos son listas completas; sin lookup por clave). `files.json` (3,8 MB) lista los 15 138 archivos con ruta/tamaño/tipo, **sin hash**.
- **Archivos con hashes:** `evidence/source_artifacts.json` (15 138 registros con `sha256` de contenido, tamaño, tipo, ID `SRC-…`), `evidence/EVIDENCE_MANIFEST.json`, `documentation_v52/MANIFEST.json`. Todos los IDs de evidencia son `sha256_id` (hash de la identidad canónica, no del contenido).
- **Candidatos a caché natural:** (1) `evidence/source_artifacts.json` — es de facto un *content fingerprint index* del repo en la corrida previa; (2) `index/files.json` + `evidence/scan_summary.json`; (3) `EVIDENCE_MANIFEST.partition_sha256` — permite detectar si una partición cambió; (4) `documentation_v52/MANIFEST.json` — permite detectar documentos idénticos; (5) `index/symbols.json`, `webforms.json`, `projects.json` como resultado de EXTRACTION por archivo.
- **Tiempo de lectura medido (sin re-analizar; lectura de bytes, misma máquina):**

| Conjunto | Archivos | Bytes | Lectura |
|---|---:|---:|---:|
| `index/` | 22 | 996 MB | 1,2 s (parseo JSON: 7,0 s) |
| `evidence/` | 25 | 1 057 MB | 1,65 s (parseo JSON: 7,2 s) |
| `consumer_projection/` | 27 | 199 MB | 0,68 s |
| `ai_context/` | 5 | 279 MB | 0,40 s |
| `documentation/` | 876 | 226 MB | 11,4 s |
| `documentation_v52/` | 46 568 | 69 MB | **272 s** |

Lectura clave: el coste de I/O lo domina el **número de archivos**, no los bytes (69 MB en 46 568 archivos tarda ~165× más que 1 GB en 22). La caché (y el manifest v52) deben leer/escribir por partición o por manifest, no abrir 46 k archivos para decidir. La causa exacta (antivirus/NTFS/cache de disco) no se investigó; la lectura pudo ser en frío. Es medición única, no promedio.

## 5. Costos medidos

**No hay tiempos por stage persistidos** en `RUN_SUMMARY.json` (V5.0 R0 ya lo reportó; sigue siendo verdad). Lo que sí hay:

| Fuente | Dato |
|---|---|
| `index/repository.json.duration_seconds` | **184,085 s** = SCAN→DEPENDENCY_RESOLUTION (hasta ensamblar `indexes`), corrida `ist_full_run`. Otras corridas del mismo IST: 112,7 s (V5.1 R3.1) y 370,1 s (V5.1 R0): varianza ×3,3 en la misma fase. |
| `v5_2_r3_1_validation/run.log` | wall total **33 m 11 s** (`time`); log `Evidence Core: build 132,7 s, validate 1,5 s, persist 14,4 s`. La construcción ≈ hashing de 15 138 archivos. |
| `LOG.info` de `build_evidence_artifacts` | único timing por sub-etapa emitido a log; no persistido. |

**Ventanas por mtime de archivos de `ist_full_run` (estimación; no es cronometraje).** Inicio no registrado: se estima 13:24:20 = primera escritura de `index/` (13:27:24) − 184 s. Fin: `RUN_SUMMARY.json` 13:56:41.

| Tramo | Ventana | Duración aprox. |
|---|---|---:|
| SCAN…DEPENDENCY (analítica) | ~13:24:20 → 13:27:24 | ~3 m 04 s (medido: 184 s) |
| EXPORT: `index/` + md legado | 13:27:24 → 13:27:57 | ~33 s |
| EXPORT: Evidence Core | 13:27:57 → 13:29:59 | ~2 m 02 s |
| CONTEXT (`context`, `ai_context`, `consumer_projection`) | 13:29:59 → 13:39:12 | ~9 m 13 s (`ai_context` ~13 s; el resto ≈ `consumer_projection`, hidrata todos los flows) |
| DOCUMENTATION: renderers particionados legados | 13:39:13 → 13:39:17 | ~5 s |
| DOCUMENTATION: `HUMAN_DOCUMENTATION`/`flujos_humanos` | 13:39:17 → 13:48:27 | ~9 m 10 s (hidrata otra vez todos los flows) |
| DOCUMENTATION: `documentation_v52` | 13:48:27 → 13:56:26 | ~7 m 59 s (46 567 archivos + manifest) |
| Cierre (`RUN_SUMMARY`) | 13:56:26 → 13:56:41 | ~15 s (sin explicar) |
| **Total** | 13:24:20 → 13:56:41 | **~32 m 21 s** (coherente con 33 m 11 s de otra corrida) |

- **Etapas más costosas (aprox.):** DOCUMENTATION (~17 m 30 s, 54 %), CONTEXT (~9 m, 29 %), analítica+EXPORT (~5 m 40 s, 17 %). La parte "analizar" pura es solo ~17 %; **~83 % del tiempo es proyección/documentación derivada de evidencia**. Esto reorienta V5.3: la caché por etapa de proyecciones tiene más retorno que la de extracción.
- **Volumen escrito por corrida:** ≈ 2,63 GiB en 47 526 archivos. **Leído:** todo el repo (15 138 archivos, dos veces: extracción y `hashlib.file_digest` del Evidence Core; los `.vb` tres veces por las tres pasadas de extractores).
- **Outputs regenerados aunque el input no cambie:** todos. Ninguna etapa comprueba si su resultado previo sigue válido; incluso `documentation_v52` reescribe 46 567 archivos, y `flujos_humanos`/`consumer_projection`/`ai_context` hidratan los 12 642 flows sin memoización entre ellos. Evidencia de estabilidad: dos corridas independientes dan 25 archivos de `evidence/` byte-idénticos y `index/` 21/22 idéntico (solo `duration_seconds`) (V5.1 R3), lo que confirma que una caché por hash sería válida.
- **Gaps de medición:** tiempos por stage; memoria pico; CPU vs I/O; tiempo real del stage CONTEXT vs DOCUMENTATION por wall-clock (solo mtimes); duración exacta de inicio.

## 6. Candidatos de fingerprint

| Entidad | Datos mínimos | Estabilidad | Falso positivo (cambio detectado sin cambio real) | Falso negativo (cambio real no detectado) | ¿Hash reutilizable hoy? |
|---|---|---|---|---|---|
| Archivo fuente | bytes del archivo (sha256) | alta | line endings/BOM/espacios cambian el hash sin cambio semántico (LF↔CRLF ya visto en el repo) | ninguno si se hashea el contenido; alto si se usa solo mtime/tamaño | **Sí:** `SourceArtifact.sha256` |
| Proyecto (`.vbproj`) | hash del `.vbproj` + hashes de sus `compile_items` + referencias | media | cambios en orden de items | omitir un archivo incluido por *wildcard* o referencia no listada | parcial (hash de `.vbproj` sí; conjunto de items no) |
| Solución | hash del `.sln` + proyectos listados | alta | poco | omitir proyectos dinámicos | parcial |
| Evidencia normalizada | `partition_sha256` por partición; por entidad, hash del JSON canónico | alta (D-01) | reordenamiento de listas si cambia el orden de emisión | — | **Sí** por partición (`EVIDENCE_MANIFEST`); no por entidad |
| Flow / path | hash del entry point + cierre transitivo de archivos/símbolos alcanzados + `flow_max_depth` | media | mayor recomputación por cierre amplio | subestimar el cierre (llamadas por reflexión/dinámicas no resueltas) | no; los IDs son de identidad, no de contenido |
| Documentación proyectada | hash de (evidencia del componente + plantilla + perfil + idioma + versión del renderer) | alta | — | omitir la plantilla/perfil del hash | **Sí** como *salida* (`MANIFEST.json` sha256); no como *clave de entrada* |
| Configuración | `DEFAULT_EXCLUDES`, `--exclude`, `--flow-max-depth`, `web.config` | alta | — | olvidar un parámetro de CLI | no |
| Templates / profiles | contenido de `documentation_v52/defaults/*` y config | alta | — | — | no (viven en el paquete) |
| Versión del analizador | **no existe** constante de versión (grep `__version__|ANALYZER_VERSION`: sin resultados) | — | — | **crítico:** cambio de extractor sin invalidar caché | no |

No se implementó ningún fingerprint.

## 7. Mapa conceptual de invalidación

```text
archivo .vb cambiado
→ EXTRACTION: symbols/calls/web_events/data_access_indexes de ESE archivo
→ (global) apply_project_namespaces + consolidate_partial_symbols
→ CALL_RESOLUTION: resuelve contra TODOS los símbolos → llamadas de otros archivos pueden resolver distinto
→ WEB_ENTRY_RESOLUTION / DATABASE_RESOLUTION / FLOW_RESOLUTION: flows que alcanzan ese archivo (y flows con `unresolved` que ahora podrían resolver)
→ Evidence: source_artifacts (su sha256), calls, call_identities, unresolved_boundaries, functional_*  de esos flows
→ proyecciones: documentación del componente, del proyecto y de los flows; consumer_projection/ai_context de esos flows
```

| Cambio | Invalida (basado en el sistema actual) |
|---|---|
| Cuerpo de un método sin tocar firma ni llamadas | solo ese archivo y los flows que lo atraviesan; sus docs. Confianza alta solo si la firma/símbolos son iguales. |
| Cambio de firma, nombre, `Partial`, namespace o clase agregada/quitada | **proyecto** + toda resolución global de llamadas (`CallResolver` es global), potencialmente **cualquier proyecto** que llame ese nombre. |
| `.aspx/.ascx` | su entry point/eventos, su code-behind, flows del entry point; docs del componente. |
| `.vbproj` | proyecto, namespaces de sus símbolos (`root_namespace`), `dependencies`, y por arrastre resolución de llamadas. |
| `.sln` | `solutions`, `dependencies`; solo relaciones, no extracción de código. |
| `web.config`/conexiones | `configuration`, `external_dependencies`, `data_access`/stored procedures asociados; docs de configuración. |
| Archivo nuevo o eliminado o renombrado | SCAN (lista), su proyecto, resolución global de llamadas; los `unresolved` previos pueden resolverse. |
| `--exclude`, `--flow-max-depth`, `DEFAULT_EXCLUDES`, extractor/renderer/plantilla/perfil/idioma | **todo el repositorio** (o todas las proyecciones afectadas) |

Casos que **no** permiten asumir invalidación local: cualquier símbolo público (resolución global), `Partial` classes multi-archivo, wildcard de compilación en `.vbproj`, cambio de rama, y `flow_unresolved`/`unresolved_boundaries` (162 914 registros): un archivo nuevo puede convertir un `unresolved` en resuelto en un flow que no lo referencia.

## 8. Evaluación de scopes

| Scope | Ya existe | Falta | Riesgo | Precisión razonable |
|---|---|---|---|---|
| `repository` | pipeline actual completo | nada | ninguno | exacta (es el estado actual) |
| `project` | `projects.json`, `compile_items`, `dependencies`, `project_path` en symbols, `documentation/project_dependencies/` | cierre de proyectos dependientes; llamadas cruzadas entre proyectos (resolución global) | medio: referencias cruzadas y `unresolved` | buena para extracción; parcial para flows |
| `folder` | `files.json` (carpeta por archivo) | mapeo carpeta→proyecto/flow; una carpeta no es unidad de compilación | alto: una carpeta cruza proyectos y viceversa | solo listado/extracción por archivo; resolución no es local |
| `component` | `components.json` (9 859), entry points, docs por componente en v52 | límites del componente vs. flows que lo cruzan; dependencias por método (limitación conocida) | medio-alto | documentación sí; resolución de llamadas no |
| `changed` | `SourceArtifact.sha256` de la corrida previa | fingerprint del corrida actual, comparación, versión del analizador, detección de renombres/borrados; base persistida confiable | alto si se cree en localidad | exacta en *qué archivos cambiaron*; el alcance del impacto depende del cierre de dependencias (§7) |

## 9. Estado de persisted indexes

- **Existen:** `index/*.json`, `evidence/*.json` con `EVIDENCE_MANIFEST` (particiones + hash), `documentation_v52/MANIFEST.json`, `consumer_projection/CONSUMER_PROJECTION.json`.
- **Consultas hoy respondibles sin re-analizar** (cargando JSON, ~7 s por conjunto): qué archivos tiene el repo y su hash; qué proyectos/soluciones existen; qué flows hay; qué documentos generó v52 y su hash; conteos por entidad. Todas requieren leer la lista completa (no hay lookup por clave ni índice inverso).
- **Consultas no respondibles:** "qué flows alcanzan el archivo X" (falta índice inverso archivo→símbolos→flows; solo hay referencias en `functional_paths`/`provenance` a recorrer), "qué proyectos dependen de Y" (hay `dependencies` a nivel proyecto, no cierre transitivo), "qué documentos salen de qué evidencia" (v52 lista archivos, no su evidencia de origen).
- **Falta para recomputación parcial:** fingerprint de entrada por unidad; grafo de dependencias archivo→símbolo→llamada→flow→documento; versión del analizador/plantilla/perfil/config en el estado persistido; escritura atómica coordinada con un manifest de caché; política ante particiones parciales.
- **Datos canónicos:** `evidence/` (contrato V5.1, byte-estable, IDs deterministas, con provenance) y, como fuente de verdad de contenido, `SourceArtifact.sha256`. **Derivados/presentación:** `index/` (proyección legada, identidad byte a byte exigida), `documentation/`, `documentation_v52/`, `consumer_projection/`, `ai_context/`, `context/`, `RUN_SUMMARY` (con `duration_seconds` no determinista).
- `evidence/persistence.py` deja documentado que JSON compacto fue elegido para V5.1 y que JSONL se difiere a V5.3 si aparece un consumidor en streaming. Con 1 GiB de evidencia y 7 s de parseo, esa decisión debe reevaluarse en R1 con datos, no asumirse.

## 10. Estado de process exit

- Antecedente: V4.3, run determinista con `FINAL_SUMMARY=SUCCESS` y proceso Python vivo. V5.0 R0 lo dejó `NOT_REPRODUCED`; V5.2 R4 lo conservó como trabajo de medición.
- **Evidencia de código:** `grep` sobre `legacy_documenter/` de `thread|ProcessPool|ThreadPool|multiprocessing|subprocess|atexit|os._exit|daemon|concurrent.futures|Popen` → **0 coincidencias**. El camino determinista no crea hilos ni procesos. `logging.basicConfig` aparece una sola vez en `main.py` (handler estándar). Las únicas superficies externas son el proveedor IA (`CopilotClient`, solo opt-in) y `main()` retorna vía `raise SystemExit(main())`.
- **Medición realizada (fixture `tests/fixtures/v2_r1_sample`, `python main.py full`, sin IA, salida en scratchpad fuera del repo):** exit code 0, wall 1,18 s, proceso termina solo. En proceso: `threading.enumerate()` = solo `MainThread`, `multiprocessing.active_children()` = `[]` tras `main()`.
- **Límite:** es fixture, no IST (~32 min). Un run de esa duración no se repitió. No prueba que el antecedente no ocurra (el terminal, un proceso Copilot residual u otro factor externo siguen posibles). Queda como punto de medición de una futura corrida controlada: registrar `threading.enumerate()`, `psutil` de procesos hijos y handles al final de una corrida IST real, y tiempo entre `FINAL_SUMMARY` y salida del proceso (con timeout).

## 11. Riesgos

| Riesgo | Nota específica |
|---|---|
| Invalidación incompleta | La resolución global de llamadas hace que una invalidación por archivo sea insegura; default seguro = ampliar el alcance. |
| Cache stale | Sin constante de versión del analizador; un cambio de extractor/renderer no invalida nada. |
| Cambio de configuración | `--exclude`, `--flow-max-depth`, `DEFAULT_EXCLUDES` cambian el resultado; deben entrar al fingerprint. |
| Cambio de template/perfil | v52 tiene plantillas/perfiles en el paquete; deben entrar al fingerprint de documentación. |
| Versión del analizador | No existe; R1 debe definirla sin alterar IDs ni manifests existentes. |
| Cambio de branch | Cambia muchos archivos a la vez: puede ser más caro que un full run. Se necesita umbral y *fallback* a repository. |
| Line endings | LF↔CRLF cambia el sha256 sin cambio semántico (falso positivo seguro); el hash normalizado sería falso negativo potencial. Decidir explícitamente. |
| Renombrados/eliminados | El `SRC-` id es hash de la **ruta**: un renombre = eliminar + agregar; hay que purgar entidades huérfanas (hoy `sync_generated_partition_directory` sí borra documentos huérfanos). |
| Dependencias cruzadas | Ver §7: llamadas globales, partial classes, `.vbproj` con items. |
| Outputs parciales | `EVIDENCE_MANIFEST` se escribe al final y se borra antes (buen patrón); `documentation_v52` y `consumer_projection` no tienen equivalente de manifest de finalización coordinado. |
| Corrupción de caché | Sin checksum de la propia caché; usar `partition_sha256`/`MANIFEST.json` para validar antes de reutilizar. |
| Compatibilidad con full | La ejecución completa debe seguir produciendo salida byte-idéntica (D-01); la incremental debe poder compararse contra full. |
| I/O por número de archivos | 46 567 archivos tardan 272 s en leerse: una caché basada en archivo por documento puede ser tan lenta como regenerar. |
| Varianza de tiempos | `duration_seconds` 112 s–370 s en el mismo IST: sin métricas por stage no se puede afirmar mejora. |

## 12. Deuda técnica clasificada

| ID | Hallazgo | Clase |
|---|---|---|
| D-1 | No hay tiempos por stage persistidos (`RUN_SUMMARY` solo tiene estado) | **NEXT_ROUND** (R1 debe definir métricas; añadirlas hoy chocaría con el test de igualdad exacta de `RUN_SUMMARY`, ver V5.0 R2 D-12) |
| D-2 | No existe versión del analizador/renderer usable como clave de caché | **NEXT_ROUND** (contrato R1) |
| D-3 | `duration_seconds` no determinista en `repository.json`; decidir si migra a métricas | **NEXT_ROUND** |
| D-4 | `CallResolver` global: impide invalidación por archivo | **CURRENT_PHASE** (restricción de diseño de V5.3, no defecto) |
| D-5 | Hidratación repetida de los 12 642 flows por `consumer_projection`, `flujos_humanos` y `ai_context`, sin memoización entre stages | **NEXT_ROUND** (candidato de mayor retorno, ≈ 18 min) |
| D-6 | `documentation_v52` escribe 46 567 archivos siempre; sin caché por documento | **CURRENT_PHASE** |
| D-7 | Sin índice inverso archivo→flows / proyecto→dependientes | **NEXT_ROUND** |
| D-8 | Intermitencia de escritura (`known_risks.r6_intermittent_test`): **resuelta**. Causa identificada (`PermissionError` transitorio de Windows en `os.replace` de `atomic_write_text`), corrección aplicada (`_replace_with_retry`), cobertura de tests añadida en V5.2 R4.2 y `PROJECT_STATE.json` ya refleja `ROOT_CAUSE_IDENTIFIED_AND_FIXED` (V5.2 R4.4). Ya no está pendiente. *(Corregido en R0.1; la redacción original de R0 la daba por desactualizada.)* | **RESUELTO** (sin acción) |
| D-9 | Process exit sin medición a escala IST | **NEXT_ROUND** (corrida controlada) |
| D-10 | Prompt de R0 en `prompts/V5_0/` en vez de `prompts/V5/` (**movido a `prompts/V5/` en R0.1**) y `V5_2_GIT_CLOSURE_RESULT.md` sin versionar (sigue pendiente de revisión humana) | **OBSERVATION** |
| D-11 | Decisión JSON vs JSONL de `persistence.py` pendiente de reevaluación | **FUTURE_PHASE**/R1 |
| D-12 | `technical_documentation_renderer.py` alto riesgo de mantenibilidad (`PROJECT_STATE`) | **FUTURE_PHASE** |
| — | BLOCKING | ninguno |

## 13. Qué NO se midió

- Tiempos por stage con cronómetro (solo `duration_seconds` de la fase analítica, un `run.log` de otra corrida y ventanas por mtime).
- Memoria pico y CPU.
- Reproducibilidad de los tiempos (una sola muestra de lectura; corridas previas muestran varianza ×3,3).
- Efecto de caché de disco/antivirus en la lectura de 46 k archivos.
- Process exit a escala IST; handles abiertos.
- Distribución real del alcance de invalidación (cuántos flows/proyectos afecta un cambio típico): requiere un cambio controlado; no se hizo.
- Estabilidad de `SourceArtifact.sha256` frente a cambios de line endings.
- Suite completa de tests (no requerida en R0).

## 14. Datos que necesita R1

1. Cronometraje por stage y sub-stage de **una** corrida IST real controlada (con `threading.enumerate()` al final), para fijar un baseline numérico.
2. Cantidad de flows/proyectos/documentos afectados por 3–5 cambios sintéticos representativos (cuerpo de método, firma, `.aspx`, `.vbproj`, archivo nuevo) sobre una **copia** fuera del repo legado (el repo legado es de solo lectura).
3. Decisión de line endings y del alcance del hash de archivo.
4. Definición de versión del analizador/renderer/plantilla y su ubicación.
5. Mapa exacto de qué campos de `symbols`/`calls` pueden alterar `CallResolver` (para acotar el cierre en lugar de asumir "todo").
6. Confirmar si la salida incremental debe ser byte-idéntica a la completa (aquí se asume que sí, por D-01).

## 15. Recomendaciones para el contrato de R1

- Medir antes de optimizar: primero métricas por stage/sub-stage no deterministas fuera de los manifests byte-estables; luego caché.
- Priorizar por retorno medido: (1) proyecciones/documentación (~83 % del tiempo) por memoización de hidratación de flows y caché por documento vía manifest; (2) reutilización del hash de archivo; (3) extracción por archivo; (4) resolución global, la última y con default de invalidación conservador.
- Política por defecto: ante duda, ampliar el alcance de invalidación hasta `repository`. Nunca reutilizar bajo evidencia insuficiente. Preservar `confirmed/inferred/unresolved`.
- Diseñar la caché con **manifest de finalización escrito al final y validado por hash** (patrón de `EVIDENCE_MANIFEST`), y unidades de lectura grandes (particiones), no un archivo por documento.
- Fingerprint compuesto e inspeccionable: contenido del archivo + versión del analizador + configuración + plantilla/perfil + idioma. Toda decisión determinista, sin IA.
- No cambiar IDs, `EVIDENCE_MANIFEST`, `index/` ni `RUN_SUMMARY` existentes sin decisión explícita; la salida incremental debe compararse contra una corrida full.
- Definir `changed` primero (es el único scope que aprovecha lo ya persistido); dejar `folder` para el final por ser el de peor precisión.
- Incluir en el contrato el fallback a corrida completa (cambio de branch, versión, config, cache corrupta).

## 16. Archivos modificados

| Archivo | Cambio |
|---|---|
| `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md` | Creado (este documento, único entregable). |

Sin cambios en código, tests, `PROJECT_STATE.json`, manifests ni docs previos. Se crearon archivos temporales de medición solo en el scratchpad de la sesión (fuera del repo): `measure.py`, `exitcheck.py`, salidas de fixture. No se escribió nada en el repositorio legado ni en `C:\PruebasLegacyMapper`. `PROJECT_STATE.json` no se actualizó (no lo pedía el prompt).

## 17. Confirmación

**No se implementó V5.3.** No hay caché, análisis incremental, invalidación, índice persistido nuevo, scopes, fingerprints ni refactors. No se ejecutó IA. No se hizo commit, push ni tag. `v5_3_started` permanece `false`.

**V5_3_R0_READY_FOR_CONTRACT**
