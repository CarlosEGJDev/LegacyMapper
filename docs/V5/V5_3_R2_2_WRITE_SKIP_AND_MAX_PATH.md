# V5.3 R2.2 — Write-skip de `documentation_v52` y MAX_PATH

Estado final: **V5_3_R2_2_READY_FOR_REVIEW**

Se implementaron únicamente las dos decisiones de R1 asignadas a R2.2: (1) no reescribir documentos de `documentation_v52` ya idénticos en disco, con verificación **estricta por contenido**; (2) preflight de longitud de rutas en Windows antes de escribir, con `--long-paths` opt-in. No hay caché persistida general, ni `_cache_v53/`, ni File State, ni fingerprints, ni write-skip de otras salidas. Sin IA. Sin commit, tag ni push. No se inició R2.3.

Resultado clave en IST: repetición sin cambios, `documentation_v52` **561 s → 32,2 s** (objetivo R1 ≤ 49 s, cumplido con margen estrecho), 0 documentos reescritos, salida **byte-idéntica**.

## 1. Resumen

- **Write-skip:** el contenido se genera igual que antes; cada documento existente se compara byte a byte con los bytes que se escribirían; si coincide no se crea temporal, ni `fsync`, ni `os.replace`. Lo que falta o difiere se escribe con la escritura atómica existente. El `MANIFEST.json` se construye solo desde la salida actual y se escribe al final: es el que produciría una corrida completa.
- **Preflight MAX_PATH:** función pura y reutilizable (`utils/path_limits.py`); antes de crear carpetas, escribir o borrar nada mide todas las rutas del stage (más el nombre temporal atómico) y aborta con `OUTPUT_PATH_TOO_LONG`.
- **`--long-paths`:** implementado (solo `full`), Windows, opt-in; inocuo en otras plataformas.
- **Optimización adicional necesaria para el objetivo:** la limpieza de directorios vacíos intentaba `rmdir` en cada directorio (siempre fallaba en los que tienen documentos) y costaba 17–21 s; ahora solo se intenta en directorios fuera del conjunto esperado (misma semántica).

## 2. Archivos modificados

| Archivo | Cambio |
|---|---|
| `legacy_documenter/documentation_v52/engine.py` (+238 líneas) | write-skip estricto, `_load_previous_manifest`, `_verify_existing`, `_prune_orphans`, `_prune_empty_directories`, `_write_documents`, `_write_manifest`, `_write_counters`; parámetro `long_paths`; `DocumentationV52Result.write_stats` (solo en memoria). `_atomic_write` y el esquema del manifest **sin cambios** |
| `legacy_documenter/utils/path_limits.py` (**nuevo**, 143 líneas) | `check_output_paths`, `OutputPathTooLongError` (`OUTPUT_PATH_TOO_LONG`), `applicable_path_limit`, `to_extended_path`, `windows_long_paths_enabled` (lectura del registro, solo lectura), `suggested_max_output_length` |
| `legacy_documenter/cli/pipeline_stages.py` | `render_documentation(..., long_paths)` → `generate_documentation_v52`; log INFO `documentation_v52 write: {…}` |
| `legacy_documenter/cli/full_pipeline.py`, `router.py`, `parser.py` | `--long-paths` (solo `full`) → `run_full_pipeline(long_paths=…)` |
| `tests/test_v5_3_r2_2_write_skip_and_max_path.py` (**nuevo**, 34 tests) | ver §10 |
| `tests/test_v4_1_r0_maintainability_inventory.py` (**modificado**) | registra el módulo nuevo y el crecimiento de `engine.py` en el inventario histórico congelado (ver D-5) |
| `prompts/V5/V5_3_R2_2_WRITE_SKIP_AND_MAX_PATH.md` | movido desde `prompts/V5_0/` |
| `docs/V5/V5_3_R2_2_WRITE_SKIP_AND_MAX_PATH.md` | este informe |

`MANIFEST.json`, IDs, Evidence Core, `PROJECT_STATE.json` y `main.py` no se tocaron.

## 3. Diseño final del write-skip

```text
render en memoria → check_output_paths (aborta antes de escribir) → bytes+SHA-256 por documento
→ leer manifest previo (solo para clasificar contadores) → mkdir root → borrar huérfanos .md
→ _verify_existing (match | missing | different, pool acotado de 8 hilos)
→ escribir solo missing/different (atomic existente) → escribir MANIFEST.json (último)
→ podar directorios vacíos
```

Orden de efectos inalterado respecto a V5.2: huérfanos primero, documentos, manifest al final, directorios vacíos al final.

## 4. Fuente de confianza usada

**Los bytes del archivo en disco**, comparados con los bytes que se van a escribir. El manifest previo **no** es fuente de confianza para omitir una escritura: se lee únicamente para clasificar los contadores (`documents_changed_vs_previous_manifest`, `documents_disk_mismatch_with_same_previous_manifest`) y una ausencia o corrupción del manifest no afecta a la corrección.

## 5. Modo de verificación implementado

Solo **`strict_content`**. Para cada documento: `stat` (si no existe → `missing`); si el tamaño difiere → `different` sin leer; si coincide, se lee y se compara `bytes ==` (equivale a comparar SHA-256, sin calcularlo). Cualquier error de lectura o tipo inesperado → `different` (se reescribe).

**Modo `fast` NO implementado (decisión según §7 del prompt).** Con solo el manifest existente y metadatos del archivo no puede demostrarse seguro: el manifest guarda `path/size/sha256` pero no `mtime`, y no puede añadirse sin cambiar su esquema (prohibido) ni sin crear un estado auxiliar persistente (una caché nueva, fuera de alcance). Comparar el `mtime` del archivo con el del manifest no es una prueba: un `mtime` restaurado (copia/restauración de backup, `os.utime`) acepta falsamente un archivo editado; `size` sola tampoco basta (mismo tamaño). Un modo rápido sin esas garantías sería una heurística insegura; solo sería sostenible con File State persistido (R2.4/R1 §6.A), y, como el modo estricto ya cumple el objetivo, podría no hacer falta.

**Cómo se hizo viable el modo estricto:** la verificación secuencial de los 46 567 archivos costó 28,7–50,8 s (microbenchmark); con un pool acotado de hilos (E/S, resultados independientes del orden): 4 hilos 9,9 s, **8 hilos 8,0 s**, 16 hilos 7,0 s. Se eligió 8 (el pool se cierra y se une antes de retornar; verificado: sin hilos residuales, exit 0). En el pipeline completo cuesta 15,6–23,9 s.

## 6. Por qué es seguro

1. Solo se omite una escritura si el archivo existe, tiene exactamente el tamaño esperado **y** su contenido es idéntico byte a byte.
2. Todo lo demás (falta, truncado, mismo tamaño con contenido distinto, ilegible, no regular) se reescribe: la prueba lo cubre con un bit alterado, mismo tamaño y `mtime` restaurado.
3. Como el contenido final es siempre el esperado, la salida es equivalente a una corrida completa **por construcción**; el manifest sale de la salida actual, no de lo que había en disco.
4. Manifest previo ausente o corrupto (6 variantes probadas) → mismo resultado correcto.
5. Sin cambios de encoding ni de saltos de línea (UTF-8, LF; no se pasa por `atomic_write_text`, que traduciría `\n`).
6. Huérfanos eliminados como antes; directorios vacíos podados con la misma semántica.

## 7. Contadores (en memoria; log INFO `documentation_v52 write: {…}`; no se persisten ni se tocó `RUN_SUMMARY`)

`documents_total`, `documents_written`, `documents_skipped_write`, `documents_missing`, `documents_changed`, `documents_verified`, `documents_changed_vs_previous_manifest`, `documents_disk_mismatch_with_same_previous_manifest`, `orphans_removed`, `previous_manifest` (`valid/absent/corrupt`), `verification_mode`, `verify_workers`, y tiempos `render_seconds`, `verify_seconds`, `write_seconds`, `cleanup_seconds` (huérfanos + directorios), `manifest_seconds`, `write_phase_seconds`.

## 8. Diseño MAX_PATH

- **Límite:** 259 caracteres utilizables (MAX_PATH = 260 incluye el NUL). **Temporal atómico:** `.{nombre}.{8 aleatorios}.tmp` = nombre + 14; la condición es `len(ruta_final) + 14 ≤ 259`.
- **Preflight** (`check_output_paths`): función pura sobre longitudes, ejecutada tras generar en memoria y **antes** de `mkdir`, escrituras o borrados; mide todas las rutas del stage + `MANIFEST.json`. En no-Windows no hace nada (`limit=None`).
- **Detección de rutas largas del SO:** lee `LongPathsEnabled` (solo lectura, no modifica el SO); si está activo, usa el límite extendido. En esta máquina vale 0.
- **Error:** `OutputPathTooLongError` con `code = "OUTPUT_PATH_TOO_LONG"`; el mensaje (español) incluye: nº de rutas que exceden, la peor ruta, su longitud (con y sin temporal), el límite, `--output` actual y su longitud, la **longitud máxima sugerida de `--output`** (`límite − 14 − 1 − longitud relativa más larga desde --output`), "No se escribió nada de esta etapa" y la opción `--long-paths`. En el pipeline se refleja como fallo del stage DOCUMENTATION (`RENDERER_FAILURE`) con ese mensaje, no como `FileNotFoundError` ambiguo.
- **Caso IST:** ruta relativa más larga de v52 = 165 caracteres (con `documentation_v52/`, medido en R1) ⇒ `--output` ≤ 79 caracteres.
- **No se mapean nombres a hash** (rompería enlaces, slugs y rutas del manifest).

## 9. Estado de `--long-paths`

**Implementado.** Solo en `full` (`analyze` no escribe v52 y lo rechaza como opción desconocida). En Windows, `documentation_v52` se escribe a través de la ruta extendida `\\?\` (`to_extended_path`); `result.output_dir`, los nombres, los enlaces y las rutas relativas del manifest **no cambian** (verificado: `MANIFEST.json` byte-idéntico con y sin la opción). En otras plataformas es **inocuo** (se acepta y no hace nada; decisión: el diseño más simple, documentado en la ayuda). Prueba real en Windows: escritura de rutas > 300 caracteres, lectura, y write-skip sobre rutas extendidas. Advertencia en la ayuda: otras herramientas (Explorador, editores, antivirus) pueden no abrir esas rutas. Alcance: **solo `documentation_v52`** (D-4).

## 10. Tests dirigidos (34, `test_v5_3_r2_2_write_skip_and_max_path.py`)

- **Write-skip (14 del prompt):** primera corrida; segunda idéntica (solo el manifest pasa por `mkstemp`/`fsync`/`replace`: 1/1/1); cambio de un documento; documento ausente; corrupto (truncado y mismo tamaño con basura); edición externa de mismo tamaño con `mtime` restaurado; manifest ausente; manifest corrupto (6 variantes); huérfanos y directorios vacíos; manifest/árbol idénticos a una generación completa sobre un árbol sucio; encoding/saltos de línea; determinismo; pool: mismo resultado que secuencial y sin hilos residuales; end-to-end con `run_full_pipeline` dos veces (evidencia, `index/`, proyecciones y documentación legada sin cambios; `written == 0`, `skipped == total`); independencia de runtime (AST).
- **MAX_PATH:** dentro del límite; exactamente en el borde (cabe / +1 falla); falla solo por el temporal; varias rutas y peor reportada; contenido del error; longitud sugerida exacta (cabe / +1 falla); sin límite; por plataforma y opt-in; lectura de registro booleana; ruta extendida; nada se escribe ni borra al abortar; stage reporta `OUTPUT_PATH_TOO_LONG`; rutas relativas del manifest sin cambios con `--long-paths`; prueba real de rutas > 259 en Windows.
- **CLI:** `full` acepta `--long-paths`; `analyze` lo rechaza; el router lo pasa al pipeline.

## 11. Suite completa

`python -m unittest discover -s tests`: **2 506 pruebas, 0 fallas, 0 errores, 132 skips**, 506 s (2 472 previas + 34 nuevas). Incluye tests de `documentation_v52`, escritura atómica y CLI.

Nota de proceso: una ejecución intermedia (1 122 s, la máquina estaba muy lenta por el antivirus) falló un test por *timeout* de 60 s de `test_clean_distribution_runs_full_standalone_against_a_fixture` (ejecuta `main.py full` en un subproceso); pasa en aislamiento (9 tests del grupo en 25,7 s) y en la repetición completa. Ver D-9. Durante la ronda el inventario de mantenibilidad congelado exigió registrar el módulo nuevo y el crecimiento de `engine.py`; se hizo con comentarios de ronda (D-5).

## 12. Equivalencia byte a byte

- **Árbol completo de IST** (47 526 archivos): código actual vs. el mismo código con el `engine.py` original de `git HEAD` (la única diferencia es la fase de escritura): **`documentation_v52`: 46 568 archivos comparados, 0 diferentes** (mismos 46 567 documentos y mismo `MANIFEST.json`); `evidence` (25), `index` (22: 21 idénticos), `consumer_projection` (27), `ai_context` (5), `documentation` (876), `context` (1): 0 diferencias. Las únicas diferencias del árbol: `index/repository.json` (solo `duration_seconds`, no determinista) y `RUN_SUMMARY.json/.md`, **artefacto de mi referencia**: el `engine.py` original no tiene `write_stats`, así que esa corrida terminó PARTIAL justo después de escribir todo el árbol.
- **Código final, a escala IST:** los 46 567 documentos reales escritos y re-verificados dos veces coinciden **byte a byte** con el contenido esperado (46 567 ok, 0 mal); manifest con 46 567 archivos.

## 13. Métricas IST antes/después

Corridas `full` completas sin IA sobre IST oficial (`C:\Users\cgalianj\source\IST_40\Operacional`), salida en ruta corta, misma sesión.

| Medida | A (sin reutilización) | B (repetición sin cambios) |
|---|---:|---:|
| `documentation_v52` (stage) | 561,1 s | **32,2 s** |
| ↳ render en memoria | 18,4 s | 9,2 s |
| ↳ verificación | 4,4 s (nada que verificar) | 19,9 s |
| ↳ escritura de documentos | 537,0 s | 0,02 s |
| ↳ limpieza (huérfanos + directorios) | 0,9 s | 2,8 s |
| ↳ manifest | 0,06 s | 0,08 s |
| ↳ fase de escritura | 542,6 s | 22,9 s |
| DOCUMENTATION (stage) | 573,3 s | 41,4 s |
| Tiempo total de la corrida | 796,6 s | **206,2 s** |
| Memoria pico (working set) | 2,72 GB | 2,74 GB |

Referencia previa (R2.1, mismo código de escritura anterior): v52 ≈ 407–486 s por corrida.

**Corrida B intermedia (antes de optimizar la limpieza de directorios):** v52 = **58,9 s** (render 14,0; verificación 23,3; limpieza 20,9; manifest 0,1), por encima de los 49 s. La causa era el barrido `rmdir` por directorio (también 17,6 s en A); se corrigió en esta ronda (misma semántica, cubierta por test).

**Código final tras un último refactor mecánico del motor en helpers** (fase de escritura únicamente, con los 46 567 documentos reales de IST, sin render): A_clean 932 s (escritura 926,6 s), B 31,2 s (verificación 23,4; limpieza 7,3), C 20,7 s (verificación 15,6; limpieza 4,7). Sumando el render (9–14 s) la repetición queda en ≈ 30–45 s. No se repitió la corrida completa del pipeline tras ese refactor (cambio de estructura sin cambio de lógica, cubierto por los 34 tests y la suite completa).

## 14. Documentos escritos/omitidos

| | Escritos | Omitidos | Verificados | Faltantes |
|---|---:|---:|---:|---:|
| A (sin reutilización) | 46 567 | 0 | 0 | 46 567 |
| B (repetición) | **0** | **46 567** | 46 567 | 0 |

Comprobado también por fechas de modificación: en B solo cambió `documentation_v52/MANIFEST.json`; los 46 567 documentos conservan su `mtime` (el resto de stages sí reescriben todo, fuera de alcance). El contador de E/S del proceso de Windows mostró ~30 000 "operaciones de escritura"/39,6 MB en B pese a no escribirse documentos; no se investigó la causa (métrica de mi arnés, no del código) — D-8.

## 15. Tiempo de verificación

Pipeline completo: **15,6–23,9 s** (B: 19,9 s; B intermedio 23,3 s) para leer y comparar 46 567 archivos (≈ 69 MB) con 8 hilos. Microbenchmark: 28,7–50,8 s secuencial; 8,0 s con 8 hilos. Con File State persistido (R2.4) la verificación podría evitarse en los archivos intactos, pero el coste actual ya cumple el objetivo.

## 16. Tiempo de escritura

Escribir los 46 567 documentos con el mecanismo atómico existente: **537–575 s** en pipeline; 926,6 s en una medición posterior con el antivirus más lento (5,8 ms/archivo en microbenchmark de R1; hoy ≈ 11–20 ms/archivo). Esa cifra **no mejora** en la primera corrida o cuando casi todo cambia: R2.2 evita escrituras, no las acelera (D-2, D-3). Escritura en B: 0,02 s.

**Objetivo de R1 (`documentation_v52` ≤ 49 s en repetición sin cambios):** **cumplido** en el pipeline completo (32,2 s) con la verificación **estricta** (sin debilitarla). El margen es estrecho y depende del I/O/antivirus de la máquina (B intermedio: 58,9 s antes de optimizar la limpieza).

## 17. Deuda técnica

| ID | Hallazgo | Clase |
|---|---|---|
| D-1 | Coste de la verificación segura sin File State: 16–24 s por leer 46 567 archivos; un modo `fast` requeriría estado persistido (File State, R2.4) y hoy no hace falta para cumplir el objetivo | **NEXT_ROUND** (R2.4, opcional) |
| D-2 | `fsync` por archivo: sin cambios; las escrituras reales (primera corrida o cambios masivos) siguen costando 537–926 s. Candidato de R1 §6.E (escritura sin `fsync` solo en el árbol derivado v52) sigue abierto | **NEXT_ROUND** |
| D-3 | Antivirus/NTFS (McAfee `mcshield`: ~16 600 s de CPU acumulada) domina la creación de archivos pequeños; el tiempo de escritura inicial varió 537–926 s (y una corrida completa de referencia tardó 12 048 s); no es controlable desde el código salvo escribiendo menos | **OBSERVATION** |
| D-4 | El preflight y `--long-paths` cubren solo `documentation_v52`; `documentation/`, `evidence/`, `index/`, `consumer_projection/` y `ai_context/` no tienen preflight (rutas más cortas, sin medir) | **NEXT_ROUND** |
| D-5 | `engine.py` cruzó de HIGH a VERY_HIGH y entra en el top de módulos grandes del inventario; se registró en el test histórico congelado (recuento 195, `module_count` +52, `path_limits.py`, categorías, top-N, efectos laterales +1) sin debilitar aserciones. Extraer la fase de escritura a su propio módulo reduciría el riesgo | **FUTURE_PHASE** |
| D-6 | Render en memoria 9–18 s es ahora ≈ 30–55 % de la repetición sin cambios | **OBSERVATION** |
| D-7 | `MANIFEST.json` (10 MB) se reescribe siempre aunque sea idéntico (0,1 s) | **OBSERVATION** |
| D-8 | `GetProcessIoCounters` no sirve para contar escrituras reales en este entorno (marcó ~30 k operaciones sin escribir documentos); la evidencia válida son las fechas de modificación | **OBSERVATION** |
| D-9 | `test_clean_distribution_runs_full_standalone_against_a_fixture` usa un timeout fijo de 60 s: falla cuando la máquina está muy lenta (pasa aislado y en la repetición) | **OBSERVATION** |
| D-10 | Los demás stages siguen reescribiendo todo en cada corrida (`index/` ≈ 1 GB, evidencia ≈ 1 GB, particiones y proyecciones) | **NEXT_ROUND** (R2.6) |
| — | BLOCKING | ninguno |

## 18. Riesgos

| Riesgo | Mitigación / estado |
|---|---|
| Aceptar un archivo incorrecto | verificación por contenido; ningún `size`/`mtime`/manifest se usa como prueba; probado con edición de un bit y `mtime` restaurado |
| Carrera con edición externa durante la verificación | ventana de segundos; un archivo editado entre verificación y fin de corrida quedaría con la edición hasta la siguiente (misma exposición que cualquier archivo escrito y luego editado) |
| Hilos | pool acotado (8), unido antes de retornar; verificado: solo `MainThread` y exit 0 al terminar |
| Márgenes del objetivo de 49 s | 32,2 s medido (pipeline), 30–45 s estimado con el código final; depende de I/O y antivirus |
| Medición del código final | las corridas de pipeline son anteriores al refactor mecánico del motor; la fase de escritura del código final se midió con los documentos reales (§13) |
| `--long-paths` | puede producir rutas que otras herramientas no abren; documentado; no cambia nombres lógicos |
| Prueba de lectura de registro (`LongPathsEnabled`) | solo lectura; si falla se asume desactivado (conservador) |
| Comparación de referencia | la referencia usa el motor original sobre el código actual (no el commit completo); el pipeline completo del commit se comparó ya en R2.1 |

## 19. Fuera de alcance confirmado

No se implementó: `_cache_v53/`, `CACHE_MANIFEST.json`, `file_state.json`, extraction cache, fingerprints de analizador/config, `ANALYZER_VERSION`, `CONFIG_FINGERPRINT`, caché de flows hidratados, write-skip de `index/`, Evidence Core, `consumer_projection`, `ai_context` o documentación legada, scopes, invalidación, cambios de IDs, de Evidence Core o de `CallResolver`, SQLite/JSONL, IA, R2.3. No se añadieron campos al `MANIFEST.json` ni al `RUN_SUMMARY`.

## 20. Estado Git (solo consultas)

Rama `main`, HEAD `6c32c4c` (tag `v5.2`).

Modificados (incluye lo pendiente de R2.1): `legacy_documenter/cli/full_pipeline.py`, `cli/parser.py`, `cli/pipeline_stages.py`, `cli/router.py`, `legacy_documenter/context/hydration.py`, `legacy_documenter/documentation_v52/engine.py`, `tests/test_v4_1_r0_maintainability_inventory.py`.

Sin versionar: `legacy_documenter/context/hydration_view.py`, `legacy_documenter/utils/path_limits.py`, `tests/test_v5_3_r2_1_shared_hydration_view.py`, `tests/test_v5_3_r2_2_write_skip_and_max_path.py`, `docs/V5/V5_2_GIT_CLOSURE_RESULT.md`, `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md`, `docs/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md`, `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`, `docs/V5/V5_3_R2_1_SHARED_HYDRATION_VIEW.md`, `docs/V5/V5_3_R2_2_WRITE_SKIP_AND_MAX_PATH.md`, `prompts/V5/` (R0, R0.1, R1, R2.1, R2.2).

Las salidas generadas de las mediciones (≈ 8 GB en `output/_r22_*`, `_fc`) y las copias temporales de código se eliminaron; los scripts de medición quedaron en el scratchpad, fuera del repo.

## 21. Estado final

Cumplido: tests dirigidos (34) y suite completa en verde (2 506); `documentation_v52` byte-idéntico (46 568 archivos) frente a la escritura completa; 0 documentos reescritos en la repetición; verificación estricta sin debilitar; objetivo ≤ 49 s cumplido (32,2 s); preflight `OUTPUT_PATH_TOO_LONG` antes de escribir y `--long-paths` operativo; sin cambios en IDs, Evidence Core, manifests ni esquema del manifest; sin caché persistida.

**V5_3_R2_2_READY_FOR_REVIEW**
