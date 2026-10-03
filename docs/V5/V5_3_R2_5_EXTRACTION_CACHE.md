# V5.3 R2.5 — Extraction Cache

Estado final: **V5_3_R2_5_READY_FOR_REVIEW** · Decisión de rendimiento: **EXTRACTION_CACHE_ADOPTED**

## 1. Objetivo

Persistir y reutilizar, por archivo, la salida cruda de los extractores (solo EXTRACTION), demostrando (a) equivalencia exacta con una corrida full y (b) beneficio real medido frente a re-extraer. Ambas condiciones se cumplen en IST.

## 2. Archivos modificados

| Archivo | Cambio |
|---|---|
| `legacy_documenter/cache/extraction_shards.py` (**nuevo**, 53 líneas) | Formato puro: `shard_index` (SHA-256 de la ruta normalizada mod 256), `render_shard`/`parse_shard` (JSON canónico), nombres `ex-NNN.json` |
| `legacy_documenter/cache/extraction_store.py` (**nuevo**, 128) | Lado disco: carga validada (checksum, parseo) y escritura solo de shards cambiados, borrado de huérfanos |
| `legacy_documenter/cache/extraction.py` (**nuevo**, 198) | `ExtractionCache`: clave de entrada, plan de hits, `lookup`/`store`, política de `cache_bypass`, métricas |
| `legacy_documenter/cache/manifest.py` | `build_manifest(..., extraction=None)`: sección opcional `extraction` (nº de shards, SHA-256 por shard, `entry_count`) |
| `legacy_documenter/cache/store.py` | `write_cache(..., extraction)`: escribe shards → `file_state.json` → manifest (último); barre temporales de `extraction/` |
| `legacy_documenter/cache/session.py` / `__init__.py` | `extraction_cache` en `begin_cache_session`; carga shards si el modo es warm; `EXTRACTION_CACHE_DEFAULT_ENABLED = True`; métricas al log |
| `legacy_documenter/cli/pipeline_stages.py` | `extract_repository(files, root, extraction_cache=None)` refactorizada en registros por archivo (`_extractors`, `_primary_value`, `_extract_file`); reemplaza `_extract_into` |
| `legacy_documenter/cli/full_pipeline.py` | Parámetro de biblioteca `extraction_cache: bool \| None`; pasa `cache_session.extraction` a EXTRACTION |
| `legacy_documenter/fingerprints/code.py` | La lista de funciones fingerprinteadas sustituye `_extract_into` por las tres funciones nuevas |
| `legacy_documenter/versions.py` | **`ANALYZER_VERSION` 1 → 2** (refactor del código de extracción; salida sin cambios) |
| `tests/test_v5_3_r2_5_extraction_cache.py` (**nuevo**, 50 tests) | ver §12–13 |
| `tests/test_v5_3_r2_3_…py` | guard de versión/fingerprint actualizado (v2); el test "tipos analizados = mapa de extractores" lee `_extractors()` |
| `tests/test_v5_3_r2_4_…py` | el listado de la caché cold incluye `extraction/` |
| `tests/test_v4_1_r0_maintainability_inventory.py` | inventario congelado: +3 módulos (214), LOW +2 / MEDIUM +1, `module_count` +71, acceso a disco, excepciones, ranking de clases |

Sin cambios en Evidence Core, IDs, manifests existentes, parser de CLI, `RUN_SUMMARY`, `PROJECT_STATE.json`. `analyze` no usa la caché.

## 3. Arquitectura de extraction cache

```text
<output>/_cache_v53/
  extraction/ex-000.json … ex-255.json   (solo los shards con entradas)
  file_state.json
  CACHE_MANIFEST.json                    (escrito ÚLTIMO)
```

Flujo (solo EXTRACTION): para cada archivo con extractor, `lookup` → hit (registro independiente parseado del disco) o miss → se extrae y `store` serializa **de inmediato**. Los registros se ensamblan en las dos pasadas originales (primarios + errores en orden de escaneo; luego calls/web_events/data_access por `.vb`), por lo que el orden de salida es idéntico con o sin caché. Después siempre corren normalización global y todos los resolvers. Un módulo por responsabilidad: la caché no importa extractores, resolvers ni `cli` (test).

## 4. Sharding

256 shards; shard = `SHA-256(ruta normalizada con "/")[:4] mod 256` → estable y determinista; mismo contenido ⇒ mismos bytes (test). JSON canónico: entradas ordenadas por ruta, separadores compactos, ASCII, LF final. Solo se reescriben los shards cuyo SHA-256 cambió (medido: 1 archivo modificado ⇒ 1 shard reescrito de 256; rename ⇒ 2; sin cambios ⇒ 0). Checksum de cada shard en `CACHE_MANIFEST.json["extraction"]`. Se mantienen 256 shards: shard medio ≈ 1,0 MB, máximo 3,75 MB; no hay evidencia para cambiarlo.

## 5. Clave de unidad

Por archivo, guardada en cada entrada y exigida por igualdad: `file_type`, base y hash de comparación (semántico en tipos analizados, el mismo criterio que el File State), `analyzer_version`, `analyzer_code_fingerprint`, fingerprint de configuración de análisis. Sin `mtime`. La ruta es la clave de la entrada. Una entrada con cualquier campo distinto es miss (test).

## 6. Registros persistidos

Solo salida de extractor por archivo, antes de normalización y resolvers: `vb_source` → symbols, calls, web_events, data_access_indexes, errores; `aspx/ascx/master` → webform; `vb_project` → project; `solution`; `web_config` → configuration; cada uno con sus errores. No se persisten resolvers, flows, paths, dependencias resueltas, documentación ni Evidence Core. El orden de claves de cada registro se preserva a propósito (forma parte de la salida del extractor).

## 7. Sanitización / cache_bypass

Antes de persistir un registro se exige: (a) que sobreviva un round-trip JSON sin cambios y (b) que `sanitize_data(registro) == registro` (se reutiliza el sanitizador central, sin duplicarlo). Si no: `cache_bypass` — no se persiste y el archivo se re-extrae siempre. Un error cuya causa es el SO (`OSError`) tampoco se cachea (no depende solo de los bytes). IST: **42 de 8 106 archivos (0,5 %)** son bypass; los 8 064 restantes se cachean. Un error de extracción determinista (p. ej. `.vbproj` mal formado) se cachea y se reutiliza (test); uno que el sanitizador altera va a bypass (test).

## 8. Mutabilidad

Persistir ocurre en `store`, antes de la normalización, que muta en sitio. Los hits son objetos recién parseados (independientes); los shards no tocados nunca se reserializan, y los hits de un shard que sí se reescribirá se serializan en el `lookup`, antes de entregarse. Al terminar se libera todo (`release`). Tests: mutar símbolos/calls/etc. tras una corrida no altera los bytes de los shards ni corridas posteriores; ídem en un shard reescrito.

## 9. Normalización global

`apply_project_namespaces` y `consolidate_partial_symbols` corren siempre sobre las listas ensambladas. Verificado en IST (RootNamespace cambiado ⇒ solo se re-extrae el `.vbproj` y la salida es ≡ full) y con partial classes (§17).

## 10. Resolvers

CALL, WEB_ENTRY, DATABASE, FLOW y DEPENDENCY se recomputan siempre (test: cada uno se invoca en la corrida warm). Sin invalidación parcial.

## 11. Corrupción / fallback

- 1 shard corrupto, ausente o con checksum/estructura inválida ⇒ solo sus archivos son miss, se re-extraen y el shard se regenera (IST: 68 misses = 42 bypass + 26; salida ≡ full; autocuración en la corrida siguiente).
- >1 shard inválido ⇒ sin reutilización (`MULTIPLE_SHARDS_INVALID`), extracción completa y caché regenerada (IST ≡ full).
- Manifest inválido/incompatible, caché borrada, versión/fingerprint/config de análisis distintos ⇒ `fallback_full`/cold de R2.4, sin reutilización.
- Sección `extraction` ilegible ⇒ extracción completa. `lookup`/`store`/`load` nunca lanzan hacia el pipeline; fallo de escritura de shards ⇒ warning, corrida válida, sin manifest (test).

## 12. Tests unitarios (50 en total, ver §13 para integración)

Sharding (6): determinista y en rango, valor congelado, dispersión, JSON canónico, rechazo de shards malformados, nombres. Seguridad/almacén (7): bypass por sanitización, error saneado → bypass y error limpio cacheado, error del SO → bypass, round-trip fallido → bypass, archivo desconocido, bypass re-extraído siempre, sin secretos ni rutas absolutas en shards. Reutilización (20): cold→warm ≡ full, modified miss (solo su shard), added miss, deleted purge, rename = delete+add, entrada con clave distinta, error cacheado, mutación no altera caché (2), normalización tras RootNamespace, partial class, cambio solo de CRLF reutiliza y es ≡ full, 1 shard corrupto (y autocuración), shard ausente, >1 corrupto, sección inválida, `lookup` sabotado no lanza, checksums en manifest, bytes reproducibles. Independencia de runtime (3).

## 13. Tests de integración (`run_full_pipeline` sobre `v4_2_r7_full_sample`)

cold persiste shards y salida ≡ sin caché; warm reutiliza y los 5 resolvers se ejecutan; 1 shard corrupto; >1 corrupto; manifest inválido; caché borrada; cambio de `ANALYZER_VERSION`; cambio de fingerprint de código; cambio de config de análisis (excludes); renderer/template **no** invalidan; HEAD/branch **no** invalidan; fallo de escritura no falla la corrida; `cache_mode="off"`; `extraction_cache=False`; cambio controlado ≡ full. Todo con comparación byte a byte del árbol de salida (salvo `RUN_SUMMARY*`, `repository.json` y `_cache_v53/`).

## 14. Suite completa

`python -m unittest discover -s tests`: **2 663 tests, 0 fallas, 0 errores, 132 skips**, 1 176 s (2 613 previas + 50 nuevas). Duración inflada: se ejecutó en paralelo con la validación IST.

## 15. IST cold

Referencia `main.py`-equivalente (`run_full_pipeline`, sin IA) sobre `…\IST_40\Operacional`, 15 138 archivos, 8 106 con extractor.

| Medida | Valor |
|---|---:|
| Extracción full sin caché (2 corridas, mismo proceso) | **49,25 s / 49,80 s** |
| Extracción con caché cold (incluye serializar + comprobar) | 58,7 s (+9,2 s) |
| Escritura de shards | 3,2 s |
| Entradas persistidas / bypass | 8 064 / 42 |
| Tamaño total de `extraction/` | **263 096 270 B (250,9 MiB)**; 256 shards, medio 1 027 719 B, mín. 158 999, máx. 3 752 496 |
| Pipeline completo cold | 714,8 s (referencia sin caché: 681,5 s) |

## 16. IST warm

Sin cambios (mismas condiciones, in-process):

| Medida | Valor |
|---|---:|
| Leer shards (`load`) | 0,22 s |
| Validar checksums | 0,07 s |
| Parsear JSON | 1,49 s |
| Ensamblar (lookups) | 0,14 s |
| **load + validate + parse + assemble** | **≈ 1,9 s** |
| Re-extraer los 42 bypass | 0,2 s |
| Etapa EXTRACTION total | 0,24 s |
| Hits / misses (42 = bypass) / reutilizados / re-extraídos | 8 064 / 42 / 8 064 / 42 |
| Shards cargados / inválidos / reescritos | 256 / 0 / 0 |
| Pipeline completo warm | 189,2 s (R2.4 warm: 199,8 s) |

Dos corridas warm consecutivas dieron el mismo resultado (hash idéntico a full).

## 17. Cambios controlados (copia de IST, IST oficial intacto)

Cache cold sobre la copia y, por escenario, restauración de la caché → cambio → extracción cacheada vs extracción full del mismo estado:

| Escenario | Diff File State | misses (de los cuales 42 bypass) | shards reescritos | ≡ full |
|---|---|---:|---:|:---:|
| C. 1 `.vb` modificado | 1 modified | 43 | 1 | ✔ |
| D. rename `.vb` | 1 added + 1 deleted (+1 candidato) | 43 | 2 | ✔ |
| E. RootNamespace de un `.vbproj` | 1 modified | 43 (solo ese `.vbproj` + bypass) | 1 | ✔ |
| F. partial class (archivo `Form1.Designer.vb`) | 1 modified | 43 | 1 | ✔ |
| G. 1 shard corrupto | — | 68 | 1 | ✔ |
| H. 2 shards corruptos | — | 8 106 (reuso desactivado) | 256 | ✔ |

Además, un cambio controlado de extremo a extremo (`run_full_pipeline` cold → 1 `.vb` modificado → warm, vs. corrida sin caché del mismo estado): 47 524 archivos de salida comparados, 0 diferencias. No se ejecutó en IST un cambio solo de saltos de línea (cubierto por test sobre fixture; el File State de R2.4 ya lo clasifica en IST).

## 18. Equivalencia full vs cache

- **Extracción** (símbolos, calls, web_events, webforms, projects, solutions, configuration, data_access_indexes, errors, logical_symbols tras normalización): comparada con `json.dumps(asdict(outcome))` (incluye el orden de claves) en cold, 2× warm y escenarios C–H: **idéntica** en todos.
- **Pipeline completo** IST oficial: warm con caché vs corrida con `cache_mode="off"`: **47 523 archivos, 0 diferencias** (resolvers, flows, paths, Evidence Core, documentation_v52, manifests, índices; excluidos solo `RUN_SUMMARY.*`, `repository.json` y `_cache_v53/`). Cambio controlado: 47 524 archivos, 0 diferencias.

## 19. Gate de rendimiento

`load + validate + parse + assemble` ≈ **1,9 s** < re-extraer ≈ **49,5 s** (mismos archivos, misma máquina, mismo proceso). Ahorro ≈ 47,6 s (≈ 96 %) por corrida warm, a un coste cold de ≈ 12 s.

## 20. Decisión final

**EXTRACTION_CACHE_ADOPTED.** `EXTRACTION_CACHE_DEFAULT_ENABLED = True` (kill-switch: `extraction_cache=False` o `cache_mode="off"` a nivel biblioteca). El ahorro real de una corrida completa es menor que 47 s en términos relativos porque, tal como mostró R0, el grueso del tiempo está en la escritura de documentación (≈ 500 s en una salida fría); esa parte no pertenece a esta ronda.

## 21. Tamaño de caché

`extraction/` 251 MiB en IST (más 4,2 MB de `file_state.json`). Crece con el código fuente; el costo en disco se paga en cada `--output` de `full`.

## 22. Costes

Cold: ≈ +9 s en EXTRACTION (serializar + round-trip + sanitización) + 3 s de escritura ≈ 12 s sobre ≈ 700 s (≈ 2 %). Warm: −47 s en EXTRACTION. Memoria (etapa EXTRACTION, in-process, pico de working set): sin caché 527 MB; cold 819 MB (+292); warm 854 MB (+327, los shards parseados). Las corridas completas de pipeline (≈ 2,5 GB de pico según R2.4) no se re-midieron; el incremento es ≤ 0,33 GB.

## 23. Seguridad

0 coincidencias de `SECRET_ASSIGN_RE` con valor distinto de `********` en los 256 shards de IST (mismo patrón que el sanitizador); sin rutas absolutas del repositorio en los shards (test + grep en IST); rutas relativas; sanitización/bypass verificados; escrituras atómicas; manifest último; corrupción no rompe la corrida (tests e IST); la identidad del repositorio (R2.4) impide mezclar repositorios.

## 24. Deuda técnica

| Hallazgo | Clase |
|---|---|
| BLOCKING | ninguno |
| `_cache_v53/` (ahora ≈ 251 MiB) aparece por defecto en `full`; decisión de default/exposición CLI (`--cache-*`) pendiente | NEXT_ROUND (R2.8) |
| Sin `--cache-mode/--cache-dir` en CLI; solo parámetros de biblioteca | NEXT_ROUND (R2.8) |
| Coste JSON parse (1,5 s) y de escritura cold (≈ 12 s) aceptables; SQLite/JSONL no justificados por la medición | OBSERVATION |
| 256 shards: medio 1 MB, max 3,75 MB; sin evidencia para cambiar | OBSERVATION |
| 42 archivos IST (0,5 %) siempre bypass por sanitización (se re-extraen en 0,2 s) | OBSERVATION |
| Lectura duplicada: el File State y Evidence Core siguen leyendo cada archivo además de la extracción (la extracción de hits ya no lee los `.vb` 3 veces) | NEXT_ROUND |
| `project_path` no en File State (requiere vbproj→compile) | FUTURE_PHASE |
| `cache/extraction.py` rankea entre las clases más grandes (11 métodos) y empuja a `dependency_resolver.py` fuera del top-N del inventario | OBSERVATION |
| `full_pipeline.py` sigue VERY_HIGH (preexistente) | OBSERVATION |
| Las funciones de `cache/` no están en el fingerprint de código: un cambio de formato de registro requiere subir `CACHE_SCHEMA_VERSION`/`ANALYZER_VERSION` manualmente | CURRENT_PHASE (a confirmar) |
| El fingerprint de código del analizador cambió por el refactor ⇒ `ANALYZER_VERSION` se subió a 2 (cachés R2.4 existentes → `ANALYZER_VERSION_MISMATCH`, full) | OBSERVATION |

## 25. Riesgos

Reuso incorrecto: mitigado por clave estricta, round-trip y sanitización antes de persistir, checksums por shard, bypass y equivalencia verificada a escala IST. Dependencia en que los extractores no tengan estado entre archivos (hoy no lo tienen: verificado por equivalencia byte a byte). Un cambio solo de CRLF/LF reutiliza la extracción (criterio semántico de R2.3); validado por test y por R2.4, no re-ejecutado en IST. Las rondas siguientes no deben alterar el formato del registro sin subir versión.

## 26. Fuera de alcance confirmado

No se inició R2.6; no se cachearon resolvers, flows, proyecciones ni `artifacts.json`/`RUN_METRICS.json`; sin cambios en Evidence Core ni IDs; sin ampliar write-skip; sin IA (`allow_ai_interpretation` no usado); sin `--cache-*` en CLI; sin commit, tag ni push.

## 27. Estado Git (solo consultas)

Rama `main`, HEAD `6c32c4c`. Modificados (previos + esta ronda): `cli/full_pipeline.py`, `cli/output_manifest.py`, `cli/parser.py`, `cli/pipeline_stages.py`, `cli/router.py`, `context/hydration.py`, `documentation_v52/engine.py`, `utils/atomic_write.py`, `tests/test_v4_1_r0_maintainability_inventory.py`, y (esta ronda, ya sin commit, sobre archivos nuevos o ya modificados) `cache/*` (+3 módulos), `fingerprints/code.py`, `versions.py`, tests R2.3/R2.4. Nuevos de esta ronda: `legacy_documenter/cache/extraction*.py` (3), `tests/test_v5_3_r2_5_extraction_cache.py`, este documento. Pendientes previos: todo lo de R2.1–R2.4 y los documentos V5.3. Salidas de medición (`output/_r25_*`) eliminadas.

## 28. Estado final

Caché de extracción por archivo implementada, shards deterministas con checksum en manifest, bypass por sanitización, mutabilidad aislada, normalización y resolvers siempre recomputados, corrupción parcial/total cubierta, salida ≡ full a escala IST (47 523 y 47 524 archivos, 0 diferencias), suite verde (2 663), gate cumplido (1,9 s vs 49,5 s).

**V5_3_R2_5_READY_FOR_REVIEW** — **EXTRACTION_CACHE_ADOPTED**

Se detiene para revisión humana.
