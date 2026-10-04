# V5.3 R2.7 — Scope Analysis + Persisted Run Metrics

Estado final: **V5_3_R2_7_READY_FOR_REVIEW** · `ARTIFACT_STATE_DEFERRED_BY_CONTRACT`

## 1. Objetivo

Persistir la observabilidad de la corrida (`RUN_METRICS.json`) y calcular de forma determinista el *scope* de los cambios del File State, sin saltar ningún stage ni reducir la corrección: resolvers, normalización, proyecciones, Evidence Core y documentación siguen recomputándose siempre.

## 2. Contrato R1 recuperado

| Tema | Qué dice R1 | Estado actual | Acción R2.7 |
|---|---|---|---|
| scope analysis | §10: `changed` = modo incremental con salida **completa**, solo informa; `project/component/folder` posteriores y solo filtran salidas; §8: `archivo → proyecto` obligatorio en R2, «alimenta métricas y scope»; `proyecto → dependientes` **pospuesto** | R2.4 dejó `project_path` fuera (requería extracción) | Se implementa `archivo → proyecto` desde `compile_items`/`content_items` de la extracción y el cierre de dependientes por referencias `Project -> Project` (ya resueltas por `DependencyResolver`, sin duplicar el mapeo); solo informa |
| persisted artifact state | §6.E/§21: `artifacts.json` (path,size,sha256,mtime_ns) para salidas sin manifest propio; asignado a **R2.6** (write-skip) | R2.6 resolvió el write-skip por comparación de bytes (equivalencia §6.E.5) | **No se crea** → `ARTIFACT_STATE_DEFERRED_BY_CONTRACT` (§9) |
| run metrics | §13: `<cache_dir>/RUN_METRICS.json`, no determinista, fuera de `RUN_SUMMARY`, `index/`, `evidence/`, `documentation_v52/` y de los checksums del manifest; envoltorio de stages; `peak_memory_bytes` por `ctypes` | no existía | Implementado exactamente en esa ruta |
| stage skipping | §6.C/§11: ninguno; sin invalidación parcial (FUTURE_PHASE) | ninguno | Ninguno |
| resolver invalidation | §6.C: no hay estado de resolvers; se recalculan siempre | ídem | Sin cambios |
| projection invalidation | §6.E: regenerar siempre + write-skip por contenido | R2.6 | Sin cambios |
| complete output invariant | §10/§12: toda corrida produce la salida completa, equivalente a full | verificado en R2.5/R2.6 | Verificado otra vez (§16) |

## 3. Diferencias entre R1 y los supuestos del prompt

- **`mode`:** R1 usa `full / incremental / off / refresh`; el prompt, `cold / warm / fallback_full`. **R1 manda:** `mode` usa el vocabulario de R1 y el valor interno de R2.4 va en `session_mode` (cold→full, fallback_full→full, warm→incremental, `REFRESH_REQUESTED`→refresh).
- **Métricas de R1 no incluidas:** `bytes_read` (no hay contador fiable en el proceso) y el desglose de sub-stages (EXPORT{json,markdown,evidence}, CONTEXT{…}, DOCUMENTATION{…}) — el prompt pide «nombres reales del pipeline» (los 10 `StageId` medidos); el desglose queda como NEXT_ROUND. `flows_hydrated/reused` se cubre con el bloque `hydration` de `HydrationView`. R1 permite «últimas N»; se conserva solo la última corrida.
- **Normalización:** su tiempo no se mide por separado (`extract_repository` forma parte del fingerprint del analizador; tocarlo exigiría subir `ANALYZER_VERSION`); se registra `extraction_postprocess_seconds` (ensamblado + normalización), derivado como EXTRACTION menos el bucle de la caché.
- **Corrida fallida:** R1 no dice nada; se escribe un `RUN_METRICS.json` con `final_status` FAILED/PARTIAL (no deja caché válida, como siempre).

## 4. Archivos modificados

| Archivo | Cambio |
|---|---|
| `cache/scope.py` (**nuevo**, 202) | `analyze_scope` / `ScopeAnalysisResult` |
| `cache/run_metrics.py` (**nuevo**, 140) | esquema, `build_run_metrics`, escritura atómica, lectura diagnóstica, memoria pico |
| `cache/run_report.py` (**nuevo**, 73) | fin de corrida: calcula scope y escribe métricas (nunca lanza) |
| `utils/stage_timings.py` (**nuevo**, 36) | tiempos por stage en memoria (`TIMINGS`) |
| `cache/session.py`, `cache/__init__.py` | `CacheSession.finish` (persiste tras SUCCESS y siempre escribe métricas), timings y `started_at` |
| `cli/full_pipeline.py` | `TIMINGS.reset()`, cronometraje en `_run_stage`/documentación, llamada a `finish` (+8 líneas: 520 → 528) |
| `cli/pipeline_stages.py` | `log_run_flow_source_stats` guarda los contadores de hidratación (observabilidad) |
| `tests/test_v5_3_r2_7_scope_and_run_metrics.py` (**nuevo**, 46 tests) | §11–12 |
| `tests/test_v4_1_r0_…inventory.py`, `test_v5_3_r2_2_…`, `test_v5_3_r2_4_…`, `test_v5_3_r2_6_…` | ajustes por los módulos nuevos y por la presencia de `RUN_METRICS.json` en `_cache_v53/` |

Sin cambios en extractores, resolvers, Evidence Core/IDs, `documentation_v52`, `RUN_SUMMARY`, CLI, ni en los módulos del contrato de la extraction cache (el guardián de R2.6 sigue verde, sin subir su versión).

## 5. `RUN_METRICS.json` — schema

`contract` `LegacyMapperRunMetrics`, `schema_version` `"1"`; claves de primer nivel (estables, testeadas): `mode`, `session_mode`, `fallback_reason`, `started_at`, `completed_at`, `total_seconds`, `final_status`, `file_state` (`files_total`, `unchanged`, `modified`, `added`, `deleted`, `renamed_candidates`, `line_ending_only`, `validate_seconds`, `file_state_build_seconds`, `diff_seconds`), `extraction_cache` (hits, misses, bypass, reused, extracted, shards cargados/inválidos/reescritos, `load/parse/validate/assemble/extraction/persist_seconds`, `cache_size_bytes`, `reuse_disabled_reason`), `stage_seconds` (`SCAN`, `EXTRACTION`, `CALL_RESOLUTION`, `WEB_ENTRY_RESOLUTION`, `DATABASE_RESOLUTION`, `FLOW_RESOLUTION`, `DEPENDENCY_RESOLUTION`, `EXPORT`, `CONTEXT`, `DOCUMENTATION`), `extraction_postprocess_seconds`, `write_skip` (por familia: generated, written, skipped_identical, bytes_generated, bytes_written, compare/write_seconds), `hydration`, `scope`, `versions` (analyzer, fingerprint, extraction-cache schema, evidence schema, renderers, template, config), `cache_verification` (`byte_compare`), `peak_memory_bytes`, `overhead_seconds`. Contiene contadores, tiempos, rutas relativas y códigos de razón; pasa por `sanitize_data`. ≈ 5 KB en IST.

## 6. Persistencia / atomicidad

`<output>/_cache_v53/RUN_METRICS.json`, `atomic_write_bytes` (temp + fsync + replace; sin `.tmp` tras fallo, test). Se escribe al final de la corrida, también si es FAILED/PARTIAL. **No** figura en `CACHE_MANIFEST.json` ni en ningún checksum; ninguna decisión runtime lo lee (test: `read_run_metrics` no se usa fuera de su módulo): un archivo corrupto, ausente o antiguo no cambia nada y la siguiente corrida lo reemplaza (tests). Un fallo al escribirlo se registra como warning y no afecta a la corrida ni a la caché (test). Fuera de `OUTPUT_MANIFEST` (que excluye `_cache_v53/`), de `RUN_SUMMARY` y de cualquier salida de producto.

## 7. Scope model

`ScopeAnalysisResult`: `mode` (`full | partial_candidate`), `changed_files` (modified/added/deleted), `impacted_projects`, `transitive_projects`, `reasons` (conteos), `fallback_reason`, `unknowns`, `unassertable`, `inventory_only`, `symbols_in_changed_files` (solo conteos por archivo) y `external_project_references`; forma persistida con listas limitadas a 200 y conteos exactos, más `reach` (`bounded` | `global_resolution`). Sin contenido fuente ni payloads de símbolos. Orden y deduplicación deterministas (test de permutaciones/duplicados). Entradas: `FileStateDiff` (renames siguen siendo deleted+added; `renamed_candidates` nunca reduce el scope), tipos de archivo actuales y previos, proyectos/símbolos de la extracción y las dependencias resueltas.

## 8. Reglas conservadoras

- Sin estado previo válido (cold, `fallback_full`, `refresh`, config/versión/fingerprint incompatible): `full` con el motivo de la caché (`NO_CACHE`, `ANALYSIS_CONFIG_MISMATCH`, …).
- Archivo analizado que ningún proyecto lista, `.sln`, tipo desconocido: `full` con el desconocido nombrado.
- `.vbproj`: proyecto completo, más sus dependientes transitivos (referencias resueltas por ruta o, si la ruta relativa no acierta —los includes antiguos van relativos a la solución—, por nombre de archivo: **ensanche deliberado**, nunca recorta).
- **Hallazgo clave (medido en IST, §15):** un cambio en código (`.vb/.aspx/.ascx/.master`), `.vbproj` o `.sln` puede cambiar la resolución global de nombres y alcanzar proyectos que **no** son dependientes por referencia (un `RootNamespace` tocó 5 proyectos mientras las referencias solo alcanzaban 2). Por eso esos cambios son `mode = full` con `unassertable = GLOBAL_RESOLUTION_EFFECTS_NOT_BOUNDED`; `impacted_projects`/`transitive_projects` se informan como **suelo conocido**, nunca como cota.
- Solo son `partial_candidate` (alcance acotado): sin cambios, `web.config` listado por un proyecto, y archivos que ningún extractor lee (`INVENTORY_ONLY`: la igualdad `ANALYZED_FILE_TYPES` = mapa de extractores está guardada por test desde R2.3).

## 9. Persisted artifact state

**`ARTIFACT_STATE_DEFERRED_BY_CONTRACT`** — `artifacts.json` no se crea. R1 §21 lo asocia al write-skip de R2.6; R2.6 lo resolvió comparando bytes (equivalencia exacta por construcción, §6.E.5), de modo que su propósito (evitar leer salidas) ya no existe; implementarlo ahora implicaría hashear ≈ 2,6 GiB por corrida sin consumidor, y el prompt prohíbe usarlo como autoridad. Si una fase futura necesita huellas de salidas (proyección selectiva), se define entonces.

## 10. Integración con el pipeline

`_run_stage` y la etapa de documentación cronometran cada stage (`TIMINGS`); `log_run_flow_source_stats` guarda la hidratación; al final `cache_session.finish(status, total, extraction_outcome, dependency_outcome)` persiste la caché solo tras SUCCESS (como antes) y luego escribe las métricas, con scope calculado sobre datos que el pipeline ya tiene (sin índices nuevos ni copias). `cache_mode=off` no produce métricas. Ningún stage consulta el scope (test: `full_pipeline` no importa `analyze_scope`/`compute_scope`).

## 11. Tests unitarios (35)

Scope (18): sin cambios; modificado (suelo + dependientes transitivos); añadido/borrado; rename = deleted+added sin reducción; mapeo archivo→proyecto (mayúsculas/separadores); mapeo desconocido → full; tipo desconocido → full; `.vbproj`; `.sln`; `web.config` mapeado/no mapeado; archivos no analizados; solo cambios acotados son `partial_candidate`; cierre transitivo con cadenas y ciclos; referencias por nombre de archivo y externas; orden determinista + duplicados; símbolos sin payload; caché incompatible → full; listas limitadas con conteos exactos. Métricas (17): schema estable; cold; warm; fallback/refresh; contadores del File State; métricas de la extraction cache; write-skip por familia; stages con nombres reales; no afectan salidas/hashes/caché; corrupto ignorado y reemplazado; borrado inocuo; escritura atómica; fallo de escritura no falla la corrida; corrida fallida; `off` sin métricas; sin contenido/secretos/rutas absolutas; memoria pico.

## 12. Tests de integración (11)

Scope sigue cambios reales y **todos** los stages se ejecutan (resolvers, EXPORT, CONTEXT, DOCUMENTATION) con salida ≡ full; cambio de configuración → full contractual; extraction cache, guardián y write-skip siguen funcionando; métricas/scope fuera de `OUTPUT_MANIFEST`, de Evidence y de `RUN_SUMMARY`; `TIMINGS` se reinicia por corrida. Independencia de runtime (5, incluidos en el total): módulos sin imports de tests/prompts/docs/cli/analysis/extractors; métricas nunca leídas por el runtime; scope no compuerta stages; igualdad tipos analizados = extractores; exports.

## 13. Suite completa

`python -m unittest discover -s tests`: **2 744 tests, 0 fallas, 0 errores, 132 skips**, 468 s (2 698 previas + 46 nuevas). Ajustes a tests existentes: el e2e de R2.2 ignora `RUN_METRICS` (lleva tiempos), el listado de la caché de R2.4 incluye el archivo nuevo, el test del ledger de R2.6 distingue producto de `_cache_v53/`, e inventario congelado (+4 módulos → 220: LOW +1/MEDIUM +3, `module_count` +77, acceso a disco y excepciones por diseño en `run_metrics`/`run_report`, tipado de `run_report`, sin ciclos).

## 14. IST warm sin cambios

`…\IST_40\Operacional` (sin modificar). Cold 655,6 s (cache nueva) y warm 149,3 s (`total_seconds` 148,4). File State: **15 138 unchanged, 0 modified/added/deleted/renamed**. Scope: `partial_candidate`, `reach = bounded`, razón `NO_CHANGES`. Extraction cache warm: 8 064 hits, 42 misses (= los 42 bypass), 256 shards, load 0,57 s + parse 1,63 s + validate 0,07 s + assemble 0,17 s + extracción de bypass 0,24 s. Tiempos por stage (warm): SCAN 1,0 s, EXTRACTION 0,3, CALL_RESOLUTION 2,0, WEB_ENTRY 1,6, DATABASE 1,3, FLOW 10,7, DEPENDENCY 0,5, EXPORT 57,5, CONTEXT 30,4, DOCUMENTATION 36,2. Hidratación: 12 642 flows (una vez cada uno; 25 284 solicitudes, 12 642 `memo_hits`). Write-skip: 954 omitidos de 956; escritos solo `index/repository.json` y un archivo de evidence (duración). **Cold vs warm: 47 523 archivos, 2 828 066 791 B, 0 diferencias** (hash por archivo; excluidos `RUN_SUMMARY.*`, `repository.json`, `_cache_v53/`).

## 15. Escenarios controlados A–I (copia de IST)

Cada escenario: caché cold sobre la copia → cambio → sesión warm + extracción cacheada + scope; luego, estado `full` (sin caché) del mismo estado y comparación de registros contra el estado previo. En todos, **la extracción con caché ≡ full** (hash JSON incl. orden de claves).

| Esc. | Cambio | Diff | Scope informado | Resultado real (oráculo) |
|---|---|---|---|---|
| A | `.vb` modificado (`AssemblyInfo.vb`, vinculado a 47 proyectos) | 1 modified | `full` (código); suelo: 47 proyectos, 1 símbolo | 1 registro cambiado; 47 proyectos impactados = suelo; FN 0 |
| B | `.vb` nuevo sin proyecto | 1 added | `full` (`UNMAPPED_ANALYZED_FILE`) | 3 registros, todos del archivo nuevo; sin proyecto dueño |
| C | `.vb` eliminado (listado por proyectos) | 1 deleted | `full`; suelo 47 | 2 registros; 47 = suelo; FN 0 |
| D | rename | 1 added + 1 deleted (+1 candidato diagnóstico) | `full` (el nuevo no está listado) | 4 registros; 47 proyectos; el candidato no reduce nada |
| E1 | `RootNamespace` de un `.vbproj` | 1 modified | `full` + `GLOBAL_RESOLUTION…`; suelo: 1 proyecto + 1 dependiente | **686 registros cambiados; 5 proyectos impactados; 178 archivos fuera del archivo cambiado** |
| E2 | quitar un `Compile` del `.vbproj` | 1 modified | ídem; suelo: 1 proyecto | **1 376 registros; 5 proyectos** |
| F | `.sln` | 1 modified | `full` (`SOLUTION_CHANGED`) | 0 registros |
| G | `web.config` (clave nueva en `appSettings`) | 1 modified | `partial_candidate`, `bounded`; 62 proyectos (los que lo listan) | 2 registros cambiados (solo configuración); 62 = 62; FN 0, extras 0 |
| H | archivo no analizado (`.gitignore`) | 1 modified | `partial_candidate`, `INVENTORY_ONLY` | 0 registros; FN 0 |
| I | cambio de `excludes` | — | `full` con `ANALYSIS_CONFIG_MISMATCH` (la caché cae a `fallback_full`; el scope no se sobrepone) | — |

El escenario extra «renombrar una clase referenciada desde otros archivos» **no pudo ejecutarse**: la selección automática no halló una clase de archivo único con llamadas resueltas hacia ella; E1/E2 demuestran empíricamente el efecto global que ese escenario buscaba (la resolución global alcanza proyectos sin referencia).

## 16. Oracle full vs incremental

Extracción cacheada ≡ full en los 9 escenarios (hash JSON); salida completa del pipeline warm ≡ cold en IST (47 523 archivos, 0 diferencias, §14); R2.5/R2.6 ya comparaban salida cacheada vs `cache_mode=off`. El scope no altera ninguna salida (no se usa para decidir).

## 17. False negatives / conservative extras

- **Scopes `partial_candidate` (alcance acotado): 0 false negatives** (G: 62 proyectos informados = 62 reales, extras 0; H y «sin cambios»: 0 impacto real).
- **Scopes `full`: no declaran cota** (FN 0 por definición); extras conservadores = proyectos no impactados (p. ej. A/C/D: 212 de 259; B: 259; E: 254; F: 259).
- **Evidencia que justifica la regla:** con la primera versión del scope (que trataba código/`.vbproj` como `partial_candidate` con suelo + dependientes), el oráculo encontró **3 (E1) y 4 (E2) proyectos reales fuera del alcance informado** → *false negatives* de esa versión. Se corrigió en esta misma ronda: esos cambios pasan a `mode = full` con `unassertable` declarado, y el suelo se informa como suelo. Resultado final con el oráculo: 0 false negatives en todo escenario donde el scope declara una cota.
- Registros sin archivo propietario determinable (flows/paths): 0 en estos escenarios (`undeterminable_records` = 0).

## 18. Overhead

Warm IST: **scope 0,008 s + construcción de métricas 0,001 s + escritura 0,009 s ≈ 0,02 s** (cold ≈ 0,06 s) sobre 148 s; el cronometraje de stages es un `perf_counter` por stage. El warm total (149,3 s) frente a R2.6 (139,5 s) está dentro del ruido de I/O (el overhead medido directamente es ≈ 0,02 s).

## 19. Memoria

Pico del proceso al final de una corrida warm completa: **3 048 259 584 B (2,84 GiB)** (`peak_memory_bytes`, `ctypes`/`PeakWorkingSetSize`). El scope solo crea un diccionario `archivo → proyectos` (una entrada por ítem de compilación/contenido) y el cierre de dependientes, transitorios; no duplica modelos, evidencia ni extraction cache. No se re-baselineó contra R2.4 (2,57 GB): la diferencia es atribuible a R2.5 (+0,33 GB medidos entonces); R2.7 no aporta crecimiento apreciable.

## 20. Seguridad

Métricas y scope: solo conteos, tiempos, rutas relativas, códigos de razón y hashes de versión; sin contenido fuente, SQL ni payloads de símbolos (test con `Password=TopSecret123`, texto de clases y ruta absoluta del repo ausentes); pasan por `sanitize_data`; escritura atómica; ningún consumidor runtime.

## 21. Mantenibilidad

Un módulo por responsabilidad (`scope` 202 líneas, `run_metrics` 140, `run_report` 73, `stage_timings` 36; ninguno HIGH; sin ciclos: `run_report` recibe la sesión tipada `Any` para no importar `session`). `full_pipeline.py` +8 líneas (528, sigue VERY_HIGH preexistente). Sin duplicar mapeo de proyectos/dependencias (usa los resultados de `DependencyResolver`). Métricas desacopladas de las salidas canónicas.

## 22. Deuda técnica

| Hallazgo | Clase |
|---|---|
| BLOCKING | ninguno |
| `scope.py` queda en 202 líneas (MEDIUM; en el umbral de 200) | OBSERVATION |
| `bytes_read` y desglose de sub-stages de R1 §13 no medidos; normalización solo derivada | NEXT_ROUND |
| Escenario «renombrar clase referenciada» sin ejecutar | NEXT_ROUND |
| Una cota segura para código requeriría comparar la superficie de declaraciones previa/nueva (registros previos de la extraction cache); hoy todo cambio de código es `full` | FUTURE_PHASE |
| `artifacts.json` no implementado (diferido) | FUTURE_PHASE |
| Solo se conserva la última corrida en `RUN_METRICS.json` | OBSERVATION |
| `full_pipeline.py` VERY_HIGH | OBSERVATION |

## 23. Riesgos

Un consumidor futuro que trate `impacted_projects` como cota de los efectos de un cambio de código se equivocaría (el oráculo lo demostró): por eso esos cambios se marcan `full`/`unassertable`. Las métricas son no deterministas por diseño; nadie debe compararlas ni usarlas como fuente de verdad.

## 24. Fuera de alcance

No se inició R2.8; sin controles CLI nuevos (`--cache-*`, `--verify-cache`, …), sin caché de resolvers/flows/proyecciones, sin salto de stages, sin recomputación parcial, sin IDs nuevos ni cambios en Evidence Core o documentación, sin IA, sin commit/tag/push.

## 25. Estado Git (solo consultas)

Rama `main`, HEAD `c49a8a4` (R2.6), 3 commits por delante de `origin/main`; rama `backup/v5.3-pre-worktree-cleanup` intacta. Modificados: `cache/__init__.py`, `cache/session.py`, `cli/full_pipeline.py`, `cli/pipeline_stages.py`, y los tests `test_v4_1_r0_…inventory`, `test_v5_3_r2_2_…`, `test_v5_3_r2_4_…`, `test_v5_3_r2_6_…`. Nuevos: `cache/{scope,run_metrics,run_report}.py`, `utils/stage_timings.py`, `tests/test_v5_3_r2_7_…py`, `prompts/V5/V5_3_R2_7_…md` y este documento. Pendiente de versionar: `docs/V5/V5_3_R2_6_1_GIT_CHECKPOINT.md`. Salidas de medición (`output/_r27*`) eliminadas.

## 26. Recomendación para R2.8

Versionar R2.7 junto con el documento pendiente de R2.6.1. R2.8 (modos y controles CLI) puede apoyarse en `session_mode`/`mode` y en `fallback_reason` ya registrados; antes de cualquier uso de scope para reducir trabajo, resolver la cota segura para código (comparación de superficie) como fase propia.

## 27. Estado final

Métricas persistidas fuera de todo checksum y de las salidas de producto; scope determinista, conservador y validado con oráculo en 9 escenarios sobre IST (0 false negatives en cotas declaradas; el oráculo corrigió la regla de código/`.vbproj`); ningún stage saltado; suite verde (2 744); overhead ≈ 0,02 s.

**V5_3_R2_7_READY_FOR_REVIEW**
