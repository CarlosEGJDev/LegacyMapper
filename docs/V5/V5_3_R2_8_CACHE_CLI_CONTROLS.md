# LegacyMapper V5.3 — R2.8 Modos y Controles CLI de Cache

Estado final: **V5_3_R2_8_READY_FOR_REVIEW** (sin diferimientos: las cinco opciones quedan implementadas). Base: `dae2ba5`. Sin commit/tag/push.

## 1. Objetivo
Exponer en `main.py full` los controles de caché de R1 (ya soportados internamente por R2.4–R2.7) sin cambiar la semántica de corrección: toda variante produce la misma salida que full.

## 2. Contrato R1 recuperado

| Opción | Nombre R1 | Default R1 | Semántica R1 | Implementación previa | Acción R2.8 |
|---|---|---|---|---|---|
| cache mode | `--cache-mode {auto,off,refresh}` (§19) | "`auto` en R2 una vez validado; hasta R4 puede ser `off`" | `off`: no lee ni escribe caché, **no aplica write-skip**, camino V5.2; `refresh`: ignora caché, full, reescribe | biblioteca (`cache_mode`) | CLI + `off` desactiva también write-skip |
| cache dir | `--cache-dir` (§6) | `<output>/_cache_v53/` | cambia la ubicación | biblioteca (`cache_dir`) | CLI + validación de seguridad |
| verify cache | `--verify-cache=hash` / `fast` por defecto (§6.E.3, §13 `cache_verification`) | `fast` | `hash` = verificación estricta que relee y hashea | implícita (checksums al validar) | `--verify-cache[=fast\|hash]`, ver §8 |
| trust mtime | `--trust-mtime` (§5) | opt-in, nunca por defecto | `(size, mtime_ns)` como prefiltro del hash | no | implementado |
| changed ratio | `--incremental-max-changed-ratio` (§11) | **sin valor por defecto (desactivado)** | umbral de coste; mide R2 y fija default | no | implementado, default desactivado |

## 3. Diferencias R1 vs prompt (R1 manda)
1. **Default de `--cache-mode`**: R1 permite `off` hasta el cierre; el CLI ya se comportaba como `auto` (default de biblioteca desde R2.4). Se mantiene `auto` para no cambiar el comportamiento actual. **Decisión pendiente de revisión humana** (la fija el cierre, R2.9/R4).
2. **`off` y write-skip**: el prompt lo permitía; R1 dice que no se aplica. Se sigue R1: `off` reescribe todo (ambos mecanismos: `write_if_changed` y el de `documentation_v52/writer.py` leen un único interruptor).
3. **Ratio sin default**: el prompt pide "default contractual"; R1 lo define desactivado y delega el valor a R2.9 con medición. Se respeta R1. Mitigación: en IST solo se midió que el control funciona (§25), no el punto de equilibrio.
4. **`--verify-cache`**: R1 usa la forma `=hash`; se acepta también sin valor (equivale a `hash`).
5. `--long-paths` (listado por R1 en R2.8) ya existía desde R2.2.

## 4–5. Opciones implementadas y defaults (solo `full`; `analyze` no las acepta)
`--cache-mode {auto,off,refresh}` (auto) · `--cache-dir DIR` (`<output>/_cache_v53`) · `--verify-cache[={fast,hash}]` (fast; bare = hash) · `--trust-mtime` (apagado) · `--incremental-max-changed-ratio R` (desactivado, `0 ≤ R ≤ 1`, NaN/inf/fuera de rango rechazados por el parser).

## 6. Semántica de modos (matriz probada)
| Caso | auto | off | refresh |
|---|---|---|---|
| sin cache | cold/full | full sin cache, sin crear directorio | `refresh` + cache nueva |
| cache válida | `warm`/incremental | ignorada y no tocada (bytes idénticos) | full + reemplazo |
| corrupta | `fallback_full` con razón | ignorada | reemplazada |
| repo mismatch | `fallback_full` `REPOSITORY_MISMATCH` | ignorada | full + cache del repo actual |
| extraction schema mismatch | extracción completa + autocuración | sin reuse | full + nueva |
Mismo vocabulario de R2.7 (`mode` full/incremental/off/refresh; `session_mode`; `fallback_reason`). Una corrida fallida deja sin manifest válido (probado). Un modo desconocido en la biblioteca desactiva la caché con aviso (compatibilidad).

## 7. `--cache-dir`
Ruta relativa al cwd o absoluta, resuelta (symlinks/junctions seguidos). Se **rechaza** (caché desactivada con aviso, la corrida sigue válida) si: apunta a un archivo, está dentro del repositorio o lo contiene, es el output o un ancestro suyo. Dentro del output es válido y se informa relativo. `off` nunca la crea. El housekeeping solo toca temporales propios (`.*.tmp`), manifest y shards (probado: un `notes.txt` ajeno sobrevive). La identidad del repositorio (ruta raíz normalizada) impide mezclar repositorios.

## 8. `--verify-cache`
- Corrección R2.8.1: flag ausente → `fast`; bare `--verify-cache` → `hash` en cualquier posición, sin consumir el argumento siguiente; `=fast` / `=hash` explícitos conservados; `=foo` rechazado. La CLI normaliza únicamente el token exacto antes de `argparse`, respetando `--`. Ver [resultado R2.8.1](V5_3_R2_8_1_VERIFY_CACHE_BARE_FIX.md).
- `fast` (default): validación normal (manifest, checksum de `file_state`, versiones, identidad, config); **tolera un shard dañado** (se re-extrae).
- `hash`: relee y hashea **todos** los shards listados, aunque no se usen; exige conteo de entradas = `entry_count`, ausencia de shards no listados, rutas del file state únicas y relativas. Cualquier inconsistencia → `fallback_full` con `fallback_reason = VERIFY_CACHE_FAILED` y detalle en `cache_controls.verify_failure`; la corrida es full válida y reescribe la caché sana. No repara. No aplica en cold/refresh ni enmascara la razón real (p. ej. `MANIFEST_CORRUPT`).
- No es una opción vacía: cambia el resultado ante un shard dañado (F1 vs F2, §23).

## 9. `--trust-mtime`
Implementado (R1 lo autoriza opt-in). Solo con caché warm válida y compatible: si path, `file_type`, tamaño y `mtime_ns` coinciden se reutiliza el registro previo sin leer el archivo; cualquier otra cosa se hashea. **Riesgo documentado (aceptado por quien lo activa)**: bytes cambiados con tamaño y mtime restaurados **no se detectan** (probado; `--trust-mtime` ausente → se detectan). Nunca con cold/refresh/caché inválida. Nota: Evidence Core sigue leyendo cada archivo para `source_artifacts`, por lo que el ahorro es solo el de File State (§27).

## 10. `--incremental-max-changed-ratio`
`ratio = (modified+added+deleted) / archivos del File State previo`; se dispara solo si `ratio > umbral` (igual no dispara; previo = 0 → indefinido, no dispara; un rename cuenta 2). Efecto: `fallback_full` con `CHANGED_RATIO_EXCEEDED`, sin reuso de extracción, caché reescrita tras SUCCESS, scope reportado `full`. No salta stages ni resolvers. Los cambios observados siguen reportándose.

## 11. Clasificación CLI / fingerprints
`cache_mode`, `verify_cache`, `trust_mtime`, `incremental_max_changed_ratio` → `RUNTIME_ONLY`; `cache_dir` → `OUTPUT_LOCATION_ONLY`. Ninguna entra a `ANALYSIS_CONFIG_FINGERPRINT`/`CONFIG_FINGERPRINT` (probado: manifest `config`/`versions` idénticos con y sin controles). El guardián de R2.3 sigue verde.

## 12. API de biblioteca
`run_full_pipeline(..., cache_mode="auto", cache_dir=None, extraction_cache=None, verify_cache="fast", trust_mtime=False, incremental_max_changed_ratio=None)`. El router mapea 1:1 (test); una sola implementación (`cache/options.py`: `CacheOptions`, `resolve_cache_dir`, `describe_location`; `cache/verify.py`). Un decorador restaura la política de escritura al terminar la corrida (también ante excepción).

## 13. `RUN_METRICS.json`
Nuevo bloque aditivo `cache_controls`: `requested_mode`, `location` (`internal`/`external`), `relative_dir` (solo interno; **nunca ruta absoluta**; `null` si externo), `verify_cache`, `verify_result`/`verify_failure`/`verify_seconds` (solo si se verificó), `trust_mtime {enabled, files_trusted, files_hashed}`, `incremental_max_changed_ratio`, `observed_changed_ratio`. `schema_version` sigue `"1"` (cambio aditivo). `off`: no hay métricas (no se crea el directorio). Las métricas no son entrada de configuración.

## 14. Scope invariants
Sin cambios en `scope.py`; `.vb/.aspx/.ascx/.master/.vbproj/.sln` siguen conservadores/full; cierre transitivo solo como observabilidad; ningún stage saltado (test: en ratio excedido se ejecutan SCAN…DOCUMENTATION; `session.py` no importa `analyze_scope`); `artifacts.json` no existe; `ARTIFACT_STATE_DEFERRED_BY_CONTRACT` sigue vigente. Cuando la caché warm es rechazada por un control, el scope se informa `full`.

## 15–16. Tests
`tests/test_v5_3_r2_8_cache_cli_controls.py`: **56 tests** — parser (defaults, modos, inválido, ruta con espacios, verify, trust, ratio válido/fuera de rango/NaN, `analyze` no acepta, clasificación, mapeo router→biblioteca), opciones/rutas inseguras, matriz de modos (cold/warm/corrupta/incompatible/schema/off sin lectura-escritura/refresh/fallo/repo mismatch), cache externa (cold/warm/borrar/regenerar, no en output, sin rutas absolutas, housekeeping), verify (sano, fast tolera 1 shard, hash rechaza, shard sobrante/faltante, razón real no enmascarada), trust (default detecta, opt-in no detecta, size/mtime distintos se hashean, nunca en cold/refresh/inválida), ratio (debajo/igual/encima, 0, rename, previo 0, sin gating), equivalencia de 6 variantes × interna/externa contra referencia `off`, invariantes de scope y de estructura.

## 17. Suite completa
`python -m unittest discover -s tests`: **2 800 tests, 0 fallas, 0 errores, 132 skips, 564 s**. Ajustes a tests existentes: `test_v4_1_r0_maintainability_inventory.py` (+3 módulos: 223, categorías de riesgo, accesos a archivo, `module_count`). Tras la última suite solo se añadió `verify_seconds` a `cache_controls`; se re-ejecutaron R2.7 y verify (52 tests OK).

## 18–25. Validación IST (`…\IST_40\Operacional`, sin modificar; salidas fuera del repo)
Una sola instancia del arnés (una primera tanda quedó invalidada por dos arneses concurrentes y se descartó). Referencia de equivalencia: salida del modo `off`, 47 523 archivos, hash por archivo, excluidos `RUN_SUMMARY.*`, `repository.json`, `_cache_v53/`.

| Paso | Resultado |
|---|---|
| **A auto cold** | `full`/`cold` `NO_CACHE`, 557,1 s, 0 hits / 8 106 misses (+42 bypass), cache creada, métricas correctas |
| **B auto warm** | `incremental`/`warm`, 150,7 s, 8 064 hits / 42 misses, 15 138 unchanged, scope `partial_candidate`, write-skip activo |
| **C off** | 532 s (sin cache); **0 diferencias** vs A (47 523 archivos); `_cache_v53` no creado; sin métricas |
| **D refresh** | `refresh`, 229,9 s, 0 hits, caché regenerada; **0 diferencias** vs `off` |
| **E externo** | cold 641 s → warm 225 s (8 064 hits) → caché borrada, salida intacta (0 dif.) → regenerada `cold`/`NO_CACHE` 280 s; nada de caché en output; 0 dif. en cada comparación |
| **F corrupta (copia de la caché)** | `fast`: warm, 1 shard inválido, 8 032 hits / 74 misses, 0 dif.; `hash`: `fallback_full` `VERIFY_CACHE_FAILED` (`SHARD_INVALID:003`), 272,8 s, status SUCCESS, 0 dif. vs `off`. Sin error fatal |
| **G changed ratio (copia de IST, umbral 0,005)** | 15 `.vb` modificados → ratio 0,000991 → warm incremental (8 049 hits); +98 más (113 en total) → ratio 0,007465 → `fallback_full` `CHANGED_RATIO_EXCEEDED`, 0 hits, 273,6 s, SUCCESS |
| **H trust-mtime (copia)** | alterado un identificador de `blADHD67Esp.vb` con mismo tamaño y mtime restaurado. Default: `modified=1` (detectado, 8 063 hits). `--trust-mtime`: `modified=0`, 15 138 archivos confiados, **no detectado**; salida 73 archivos distinta de la del default (extracción obsoleta) — comportamiento exacto y documentado del opt-in |

## 26. Equivalencia
`auto`, `off`, `refresh`, cache interna, externa, verify=hash (corrupta → full): **0 diferencias** vs referencia en IST (C, D, E×3, F). En tests: 6 variantes × interna/externa == referencia, y cambio incremental == full para cada control. La única diferencia observada es la esperada y documentada de `--trust-mtime` ante bytes manipulados (H).

## 27. Rendimiento
- Parser/control: despreciable (opciones y validación de rutas; `ratio` es una división tras el diff ya calculado).
- `verify-cache=hash`: warm 167,4 s vs 150,7 s sin verify (+16,7 s de pared, dentro del ruido de I/O entre corridas: warm osciló entre 147 y 225 s). El coste directo esperado es una segunda lectura de los 256 shards (~2,3 s según R2.7: load 0,57 + parse 1,63 + validate 0,07). Se añadió `verify_seconds` a `cache_controls` para medirlo directamente; no se re-midió en IST.
- `trust-mtime`: File State build **5,2 s → 0,38 s** (≈ 4,8 s de ahorro sobre ≈ 150 s: ~3 %); no se adopta por defecto.
- `ratio`: sin coste medible. **No se midió el punto de equilibrio** (R1 lo asigna a R2.9).

## 28. Seguridad
Cache-dir: rutas inseguras rechazadas, sin borrar directorios ajenos, `file_state.path` cerrado (verify rechaza rutas absolutas/`..`/duplicadas), manifest no redirige rutas, corrupción → fallback, escritura atómica de R2.4 intacta, sin rutas absolutas ni secretos en métricas (test), `off` independiente (no lee, no escribe, no crea, no altera una caché existente). Symlinks/junctions: se resuelven antes de comparar; no se probó un reparse point real en Windows (límite).

## 29. Mantenibilidad
Lógica en módulos nuevos (`options`, `verify`, `write_policy`); `begin_cache_session` dividido en helpers; parser con `_add_cache_arguments`; `full_pipeline.py` solo +decorador y 3 parámetros. Sin refactor grande.

## 30. Deuda técnica
Punto de equilibrio del ratio y default de `--cache-mode` pendientes de R2.9/cierre; `cache_verification` en métricas sigue `byte_compare` (describe write-skip) y convive con `cache_controls.verify_cache`. Ambigüedad del bare corregida en R2.8.1; sin cambios a las mediciones IST ni al runtime/cache.

## 31. Riesgos
`--trust-mtime` es inseguro ante mtimes restaurados (opt-in, documentado). `off` es más lento (sin write-skip) por contrato. Un `--cache-dir` inseguro desactiva la caché con aviso en lugar de abortar.

## 32. Fuera de alcance (no hecho)
R2.9, stage skipping, recomputo parcial, caché de flows/proyecciones, `artifacts.json`, IDs/Evidence Core, scope modes `project/component/folder`, IA, push/tag.

## 33. Estado Git (solo consultas)
Rama `main`, HEAD `dae2ba5`, 4 commits por delante de `origin/main`, backup `backup/v5.3-pre-worktree-cleanup` en `2cb317f`. Modificados: `cache/{__init__,file_state,run_metrics,run_report,session}.py`, `cli/{full_pipeline,parser,router}.py`, `documentation_v52/writer.py`, `fingerprints/configuration.py`, `utils/write_if_changed.py`, `tests/test_v4_1_r0_maintainability_inventory.py`. Nuevos: `cache/options.py`, `cache/verify.py`, `utils/write_policy.py`, `tests/test_v5_3_r2_8_cache_cli_controls.py`, este documento, `prompts/V5/V5_3_R2_8_CACHE_CLI_CONTROLS.md`. Pendientes de R2.7.1: prompt y resultado (`prompts/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md`, `docs/V5/V5_3_R2_7_1_GIT_CHECKPOINT.md`). `PROJECT_STATE.json` no se actualiza (se mantiene hasta checkpoint/cierre).

## 34. Recomendación R2.9
Comparador full vs incremental con IST como regresión; medir el punto de equilibrio del ratio variando la fracción modificada y fijar su default; decidir el default de `--cache-mode`; medir `verify_seconds` directamente. Antes, un checkpoint Git de R2.8 (humano).

## 35. Estado final
**V5_3_R2_8_READY_FOR_REVIEW**
