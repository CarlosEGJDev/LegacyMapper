# V5.3 R2.4 — Cache Manifest + File State

Estado final: **V5_3_R2_4_READY_FOR_REVIEW**

## 1. Objetivo

Persistir la infraestructura mínima de V5.3 para comparar una corrida con la siguiente: `CACHE_MANIFEST.json`, `file_state.json`, identidad del repositorio, validación de integridad, clasificación determinista de archivos (unchanged/modified/added/deleted + renamed_candidate), modos cold/warm/fallback_full y fallback seguro a full. **No** hay caché de extracción: la ronda solo *registra* el modo y el diff; no se salta ni reutiliza nada.

## 2. Archivos modificados

| Archivo | Cambio |
|---|---|
| `legacy_documenter/cache/` (**nuevo**, 8 módulos) | `identity`, `file_state`, `diff`, `context`, `manifest`, `store`, `session`, `__init__` |
| `legacy_documenter/cli/full_pipeline.py` | `run_full_pipeline(..., cache_mode="auto", cache_dir=None)`: abre la sesión de caché tras SCAN y persiste solo si la corrida termina en SUCCESS (~12 líneas) |
| `legacy_documenter/cli/output_manifest.py` | `build_output_manifest` excluye `_cache_v53/` de nivel superior (cambio declarado en R1 §6/§21) |
| `legacy_documenter/utils/atomic_write.py` | añade `atomic_write_bytes` (aditivo; mismo mecanismo que `atomic_write_text`, sin traducción de saltos de línea) |
| `tests/test_v5_3_r2_4_cache_manifest_and_file_state.py` (**nuevo**, 52 tests) | ver §12 |
| `tests/test_v4_1_r0_maintainability_inventory.py` | inventario congelado: +8 módulos (211), categorías LOW +4/MEDIUM +4, `module_count` +68, archivos con acceso a disco, `session.py` en excepciones |
| `tests/test_v5_3_r2_2_…py` | el test e2e de R2.2 ignora `_cache_v53/CACHE_MANIFEST` (lleva `generated_at`) |
| `tests/test_v5_3_r2_3_…py` | "nada consume los módulos nuevos" ahora admite el paquete `cache/` como único consumidor |

No se tocó Evidence Core, IDs, `EVIDENCE_MANIFEST`, `documentation_v52/MANIFEST.json`, `RUN_SUMMARY`, el parser de CLI ni `PROJECT_STATE.json`. `main.py analyze` tampoco usa la caché (solo `full`).

## 3. Arquitectura de caché creada

```text
<output>/_cache_v53/
  file_state.json        (4,2 MB en IST)
  CACHE_MANIFEST.json    (≈ 2 KB, escrito ÚLTIMO)
```

Sin `extraction/`, shards, `artifacts.json` ni `RUN_METRICS.json`. Un módulo por responsabilidad (ninguno HIGH; `file_state`, `manifest`, `store`, `session` MEDIUM, 58–166 líneas; sin ciclos). Los temporales `.<nombre>.<8>.tmp` huérfanos de `_cache_v53/` se barren al inicio de cada corrida.

## 4. `CACHE_MANIFEST.json`

JSON de claves ordenadas: `contract` (`LegacyMapperCacheManifest`), `cache_schema_version` ("1"), `state` (`COMPLETE`), `versions` (analyzer_version, analyzer_code_fingerprint, evidence_schema_version, renderer_versions, template_profile_fingerprint), `config_fingerprint` (combinado), `config` (excludes, flow_max_depth, `analysis_config_fingerprint`, `projection_config_fingerprint`), `repository_identity`, `informative` (git_head, git_branch, generated_at), `file_state` (path, sha256, file_count) y `validity.complete = true`. Sin variables de entorno ni contenido.

**Orden de escritura** (probado): (1) se borra el manifest previo (al abrir la sesión, antes de ejecutar el resto de la corrida), (2) `file_state.json` atómico, (3) se relee y se verifica su SHA-256, (4) se construye el manifest, (5) `CACHE_MANIFEST.json` se escribe al final. Una interrupción antes del paso 5 deja `INCOMPLETE_CACHE` ⇒ full.

## 5. Repository Identity

`root_normalized`: ruta absoluta resuelta, separadores `/`, sin barra final, en minúsculas en Windows; `root_fingerprint`: SHA-256 de esa cadena. Misma ruta con otro contenido = mismo repositorio (lo detecta el File State); ruta distinta ⇒ `REPOSITORY_MISMATCH` ⇒ full. Git HEAD/branch se leen de `.git/HEAD` (archivos, sin subproceso) solo como metadata informativa.

## 6. `file_state.json`

Por archivo: `path` (relativa, `/`), `size`, `sha256_raw` (bytes reales; coincide con `evidence.builder._hash_file`, probado), `sha256_semantic` (helper de R2.3, solo tipos analizados, si no `null`), `file_type`, `mtime_ns` (solo metadata), `readable`. Ordenado por ruta, JSON canónico compacto; el contenido de las claves está cerrado (test: sin contenido ni secretos). Una sola lectura por archivo produce ambos hashes (analizados en memoria, el resto en streaming; pool acotado de 8 hilos). Un archivo ilegible se registra con `readable=false` y hashes `null`, y nunca cuenta como unchanged. `project_path` **no** se implementa: requiere el mapeo vbproj→compile (extracción), fuera de alcance.

## 7. Algoritmo de comparación

Por ruta: `unchanged` si el `file_type` coincide y la **clave de comparación** coincide (hash semántico en tipos analizados; crudo en el resto); `modified` si no; `added`/`deleted` por diferencia de conjuntos. Un cambio solo de saltos de línea en un tipo analizado es `unchanged` (también se lista en `line_ending_only`, diagnóstico); un cambio de BOM es `modified`. `mtime` no interviene.

## 8. renamed candidates

Un `deleted` y un `added` del mismo `file_type` y misma clave de comparación (semántica o cruda) se registran como `{"from","to","basis"}`, emparejados de forma determinista (ambos lados ordenados). Solo diagnóstico: **rename = deleted + added** (las rutas permanecen en ambas listas); no hay reutilización por rename. Los archivos vacíos se excluyen (comparten un único hash y no informan nada).

## 9. Compatibilidad/fallback

Obliga full (`fallback_full`, nunca error): `INCOMPLETE_CACHE` (file_state sin manifest), `MANIFEST_CORRUPT`, `STATE_NOT_COMPLETE`, `UNKNOWN_CACHE_SCHEMA`, `REPOSITORY_MISMATCH`, `FILE_STATE_MISSING`/`CHECKSUM_MISMATCH`/`CORRUPT`, `ANALYZER_SOURCES_UNAVAILABLE`, `ANALYZER_VERSION_MISMATCH`, `ANALYZER_CODE_FINGERPRINT_MISMATCH`, `EVIDENCE_SCHEMA_MISMATCH`, `ANALYSIS_CONFIG_MISMATCH`, `REFRESH_REQUESTED`. Sin caché: `cold` (`NO_CACHE`).

**No obliga full** (decisión según R1 §11: afectan proyecciones, no extracción): renderer versions, template/profile fingerprint, projection config fingerprint, Git HEAD y branch; se reportan en `informational_differences`. Detalle: el manifest compara el fingerprint de configuración **de análisis**; el `config_fingerprint` combinado se guarda pero no decide. El manifest no puede redirigir la lectura a otra ruta (`file_state.path` debe ser exactamente `file_state.json`).

## 10. Integración con pipeline

Tras SCAN exitoso: `begin_cache_session` valida, construye el File State actual, compara si es warm, borra el manifest previo y loguea (INFO) `cache: {mode, reason, files, diff, informational_differences, validate_seconds, file_state_build_seconds, diff_seconds}`. Al final, solo si `final_status == SUCCESS`, `persist()` escribe la caché nueva y loguea el tiempo. PARTIAL/FAILED/interrumpida ⇒ no queda manifest válido. Cualquier fallo de la caché (hash, lectura, escritura) se captura, se registra como warning y la corrida sigue igual que sin caché. Nada se salta ni se reutiliza; `RunResult`/`RUN_SUMMARY` intactos.

**CLI (decisión):** no se añadió `--cache-dir` ni `--cache-mode` (R1 los asigna a R2.8). La caché se lee/escribe automáticamente en `<output>/_cache_v53/`; los parámetros de biblioteca `cache_mode` (`auto|off|refresh`) y `cache_dir` existen en `run_full_pipeline` para pruebas y rollback, sin exposición en el parser (el guardián de clasificación de opciones sigue verde). Consecuencia a destacar: **el comportamiento por defecto de `full` ahora añade `_cache_v53/` a la salida** (R1 §21 sugería `off` por defecto hasta el cierre; el prompt de R2.4 pide lectura/escritura automática). El resto de la salida es idéntica (§12).

## 11. Seguridad

Solo rutas, tamaños, hashes, tipos y mtimes; sin contenido ni símbolos. Escritura atómica (`atomic_write_bytes`), checksum releído, manifest último, caché corrupta/de otro repo/incompleta ⇒ full sin romper la corrida, temporales huérfanos barridos. Probado: `Password=TopSecret123` en un fuente no aparece en `file_state.json`.

## 12. Tests dirigidos (52 nuevos)

File State (16): unchanged/modified/added/deleted, rename (diagnóstico y sigue siendo added+deleted, hash crudo en no analizados, vacíos y emparejado determinista), CRLF↔LF (raw cambia, semántico igual), BOM, no analizados, hash crudo = `SourceArtifact`, mtime, cambio de tipo, ilegible, orden y JSON deterministas, rutas normalizadas, sin secretos, file_state malformado, sin `project_path`. Cache Manifest (18): cold, válido, contenido, sin manifest, corrupto (6 variantes), `state != COMPLETE`, schema desconocido, checksum/ausente/corrupto, no redirigible, repo distinto, cada incompatibilidad de extracción (5), cambio real de config, renderer/template/projection/Git no invalidan, manifest al final, interrupción, releer file_state, fuentes no disponibles, temporales. Identidad (3), independencia de runtime (2) e integración (13, ver §13).

Integración (`run_full_pipeline` sobre `v4_2_r7_full_sample`): primera corrida crea `_cache_v53/` cold; segunda warm con todo unchanged; **salida lógica idéntica con y sin caché** (y en rerun warm); caché corrupta ⇒ full correcto y caché reescrita; corrida fallida ⇒ sin manifest y la siguiente regenera; borrar `_cache_v53/` no cambia resultados; no se saltan stages y `extract_repository` se llama igual (no hay reutilización); diff real tras modificar/añadir un archivo; fallo al escribir o al construir el estado no falla la corrida; `off`/`refresh`/`cache_dir`; `build_output_manifest` excluye la caché.

## 13. Suite completa

`python -m unittest discover -s tests`: **2 613 tests, 0 fallas, 0 errores, 132 skips**, 268 s (2 561 previas + 52 nuevas).

## 14. Validación IST — Corrida A (cold)

`main.py full` sobre `C:\Users\cgalianj\source\IST_40\Operacional`, sin IA, salida nueva, exit 0, SUCCESS. 15 138 archivos.

| Medida | Valor |
|---|---:|
| Tiempo total de la corrida | 662,9 s (escritura de v52 495 s: variación habitual de I/O) |
| Construir File State (hashes raw + semántico) | **3,7 s** |
| Validar manifest | 0,09 s |
| Persistir caché | 0,05 s |
| Aportado por R2.4 en total | **≈ 3,8 s** |
| `file_state.json` / `CACHE_MANIFEST.json` | 4 238 038 B / 1 976 B |
| Memoria pico (working set) | 2,53 GB (sin cambio frente a R2.2.1) |

## 15. Validación IST — Corrida B (warm, sin cambios)

Misma salida, segunda corrida, exit 0, SUCCESS.

| Medida | Valor |
|---|---:|
| Validar manifest | 0,15 s |
| Construir File State | 6,3 s |
| Comparar estados | 0,02 s |
| Persistir | 0,05 s |
| Aportado por R2.4 | **≈ 6,5 s** |
| unchanged / modified / added / deleted / renamed | **15 138 / 0 / 0 / 0 / 0** |
| Tiempo total | 199,8 s (R2.2.1: 220,8 s; sin degradación apreciable) |
| Memoria pico | 2,57 GB |

Nota de medición: los tiempos de hashing (3,7 s y 6,3 s) se tomaron con los archivos de IST ya en la caché de disco del SO por corridas previas; una lectura realmente fría será mayor (R2.3 midió 15 s en frío solo para los 8 106 archivos analizados).

## 16. Cambio controlado (copia de IST)

Copia de IST (sin `.git`) en `output/_r24_c` (copia: 141,6 s; eliminada al terminar). Se construyó una caché sobre la copia (cold → persistida → warm sin cambios: 15 138 unchanged, 0 cambios) y luego se aplicó: 1 `.vb` modificado, 1 `.vb` nuevo, 1 `.vb` eliminado, 1 rename, 1 cambio solo de CRLF→LF y 1 cambio de BOM. Resultado (IST oficial intacto):

| Clase | Resultado |
|---|---|
| modified (2) | el archivo editado y el de BOM cambiado ✔ |
| added (2) / deleted (2) | el nuevo + el renombrado / el eliminado + el original del rename ✔ |
| renamed_candidates (1) | `AssemblyInfo.vb` → `Renamed_AssemblyInfo.vb`, base semántica ✔ (sigue en added+deleted) |
| line_ending_only (1) | el CRLF↔LF, clasificado unchanged ✔ |
| unchanged | 15 134 |

## 17. Costes medidos

Cold ≈ 3,8 s, warm ≈ 6,5 s sobre corridas de 200–660 s (≈ 1–3 %). La construcción del File State es secuencial respecto a la extracción (se ejecuta tras SCAN, antes de EXTRACTION); se podría solapar o fusionar con la lectura de Evidence Core en rondas posteriores. Duplicación de lectura medida/documentada: hoy cada archivo se lee en File State, en extracción (los `.vb`, tres veces) y en Evidence Core (`_hash_file`); R2.4 añade una lectura más y no altera Evidence Core.

## 18. Tamaños de archivos

`file_state.json` 4,24 MB (≈ 280 B por archivo, 15 138 registros) — aceptable; `CACHE_MANIFEST.json` 1,98 KB.

## 19. Deuda técnica

| Hallazgo | Clase |
|---|---|
| Lectura duplicada con Evidence Core y extracción (hash raw en File State + `_hash_file` + lecturas de extractores) | NEXT_ROUND (R2.5+/cuando se reutilice la lectura) |
| `--cache-dir`/`--cache-mode`/`--verify-cache`/`--trust-mtime`/`--incremental-max-changed-ratio` sin exponer; parámetros solo de biblioteca | NEXT_ROUND (R2.8) |
| `_cache_v53/` aparece por defecto en `full` aunque la salida lógica es idéntica; R1 sugería `off` por defecto hasta el cierre | CURRENT_PHASE (decisión a confirmar) |
| `project_path` no incluido en File State | NEXT_ROUND (con extracción) |
| `mtime_ns` se persiste solo como metadata; no se usa (sin `--trust-mtime`) | OBSERVATION |
| `file_state.json` (4,2 MB) se relee y reescribe entero cada corrida | OBSERVATION |
| `build_output_manifest` excluye `_cache_v53/` solo en el nivel superior de `--output`; un `--cache-dir` externo no se ve afectado (ya está fuera) | OBSERVATION |
| Identidad ligada a la ruta: mover el repositorio invalida la caché (comportamiento previsto) | OBSERVATION |
| `analyze` no usa la caché | OBSERVATION |
| `full_pipeline.py` sigue VERY_HIGH (515 líneas, +12 en esta ronda) | OBSERVATION (preexistente) |
| BLOCKING | ninguno |

## 20. Riesgos

Reutilización incorrecta: ninguna posible todavía (nada se reutiliza); la validación es estricta y falla hacia full. La caché solo se vuelve peligrosa cuando R2.5 la consuma; por eso `ANALYSIS_CONFIG_MISMATCH`, fingerprint de código e identidad ya están bloqueados con tests. Duplicación de `atomic_write_bytes` con `documentation_v52/writer._atomic_write` (mismo mecanismo, no unificados para no tocar R2.2). El hashing añade I/O en frío proporcional al repositorio.

## 21. Fuera de alcance confirmado

No se inició R2.5; sin extraction cache, shards, `artifacts.json`, `RUN_METRICS.json`; sin saltarse extracción, resolvers ni stages; sin cambios en Evidence Core, IDs, manifests existentes (solo la exclusión de `_cache_v53/` en el output manifest), CLI ni `RUN_SUMMARY`; sin ampliar write-skip; sin IA; sin commit/tag/push.

## 22. Estado Git (solo consultas)

Rama `main`, HEAD `6c32c4c` (tag `v5.2`). Modificados: `cli/full_pipeline.py`, `cli/output_manifest.py`, `cli/parser.py`, `cli/pipeline_stages.py`, `cli/router.py`, `context/hydration.py`, `documentation_v52/engine.py`, `utils/atomic_write.py`, `tests/test_v4_1_r0_maintainability_inventory.py`. Nuevos: `cache/`, `versions.py`, `fingerprints/`, `context/hydration_view.py`, `documentation_v52/writer.py`, `utils/path_limits.py`, tests de R2.1–R2.4, `docs/V5/` y `prompts/V5/`. Pendientes previos: cambios sin commit de R2.1–R2.3 y los documentos de V5.3. Salidas de medición (`output/_r24_a`, `output/_r24_c`) eliminadas.

## 23. Estado final

Manifest seguro y determinista, File State correcto, cold/warm/corrupt/incomplete cubiertos, repo distinto no reutiliza, diff validado a escala IST (incluido rename, CRLF y BOM), suite verde (2 613), salida lógica idéntica, sin reutilización de extracción, coste agregado medido (≈ 4–7 s).

**V5_3_R2_4_READY_FOR_REVIEW**
