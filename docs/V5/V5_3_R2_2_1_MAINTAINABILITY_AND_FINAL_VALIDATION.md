# V5.3 R2.2.1 — Saneamiento de mantenibilidad y validación final

Estado final: **V5_3_R2_2_1_READY_FOR_REVIEW**

## 1. Objetivo

Extraer de `documentation_v52/engine.py` la fase de escritura introducida en R2.2 a un módulo dedicado, sin cambiar comportamiento, y validar el código final exacto con tests y dos corridas IST completas (sin IA).

## 2. Refactor realizado

Movimiento literal (sin cambios de lógica) de `_atomic_write`, `_load_previous_manifest`, `_verify_existing`, `_prune_orphans`, `_prune_empty_directories`, `_write_documents`, `_write_manifest`, `_write_counters` y `_write_tree` (ahora `write_tree`), más las constantes `MANIFEST_FILENAME`, `MANIFEST_CONTRACT`, `VERIFICATION_MODE`, `VERIFY_WORKERS`, a `legacy_documenter/documentation_v52/writer.py`. `engine.py` conserva render/orquestación y llama a `write_tree(...)`. `result` se tipa como `Any` en `writer.py` (ver §6).

## 3. Archivos modificados

| Archivo | Cambio |
|---|---|
| `legacy_documenter/documentation_v52/writer.py` | **nuevo**, 252 líneas |
| `legacy_documenter/documentation_v52/engine.py` | 456 → 222 líneas; sin imports de E/S |
| `tests/test_v5_3_r2_2_write_skip_and_max_path.py` | solo apuntan a `writer` (imports, parches `writer.tempfile/os/_replace_with_retry`, `writer.write_tree`); `writer` añadido al test de independencia de runtime. Sin tests nuevos ni aserciones debilitadas |
| `tests/test_v4_1_r0_maintainability_inventory.py` | inventario congelado actualizado (ver §5) |

## 4. Responsabilidades antes/después

| | Antes (R2.2) | Después |
|---|---|---|
| `engine.py` | render + selección de templates + escritura/verificación/manifest/limpieza | render y orquestación; delega persistencia |
| `writer.py` | — | verificación estricta, write-skip, escritura atómica, huérfanos, directorios vacíos, manifest, contadores, coordinación |

`DocumentationV52Result`, `generate_documentation_v52`, `OUTPUT_DIRNAME` y firmas públicas siguen en `engine.py`.

## 5. Tamaño y clasificación de mantenibilidad

| Módulo | Líneas | Riesgo |
|---|---:|---|
| `engine.py` | 222 | **MEDIUM** (R2.2: VERY_HIGH; pre-R2.2: HIGH) |
| `writer.py` | 252 | **HIGH** |

`writer.py` es HIGH pero con una única responsabilidad cohesiva (persistencia); no hay costura natural para dividirlo sin fragmentar artificialmente (la verificación, la escritura y el manifest comparten `root`, `statuses` y contadores). Queda por debajo del corte top-20 de módulos grandes. Inventario congelado: recuento 196, `module_count` +53, `writer.py` en HIGH, `engine.py` fuera de HIGH/VERY_HIGH, categorías `MEDIUM +1`/`LOW +1`, `writer.py` en exception/side-effect files. Sin debilitar aserciones.

## 6. Dependencias/ciclos

Dirección única `engine → writer → utils`. Una primera versión usaba `TYPE_CHECKING` para importar `DocumentationV52Result` en `writer.py`; la herramienta de dependencias del inventario la reportó como ciclo, así que se eliminó (tipo `Any`). Resultado: sin ciclos nuevos (el test de dependencias pasa).

## 7. Tests dirigidos

`test_v5_3_r2_2_write_skip_and_max_path` (34) + `test_v4_1_r0_maintainability_inventory` (22): 56 OK. Cubren write-skip, escritura atómica (1 mkstemp/fsync/replace en repetición), MAX_PATH, `--long-paths` real en Windows y CLI. Tests de `documentation_v52` y CLI relacionados incluidos en la suite completa.

## 8. Suite completa

`python -m unittest discover -s tests`: **2 506 tests, 0 fallas, 0 errores, 132 skips**, 228 s.

## 9. Equivalencia

Fixture `v4_2_r7_full_sample`; `engine.py` R2.2 previo al refactor (copia en scratchpad) vs código final, en tres escenarios cada uno (primera corrida, repetición, árbol sucio con huérfano + directorio vacío + documento alterado): **árbol de 32 archivos byte-idéntico (incl. `MANIFEST.json`), contadores idénticos (salvo tiempos), listas de archivos idénticas**, huérfano eliminado, documento alterado reescrito (1 escrito / 30 omitidos). A escala IST la equivalencia se apoya además en la repetición B: 46 567 documentos verificados byte a byte contra lo renderizado, 0 reescritos. No se repitió la comparación del árbol IST completo contra el motor anterior (hecha en R2.2 para la misma lógica).

## 10. Corrida IST A (sin reutilización, salida nueva)

Código final, `main.py full ... --verbose`, sin IA, exit 0, `RUN_SUMMARY` SUCCESS.

| Medida | Valor |
|---|---:|
| Tiempo total | 875,1 s |
| `documentation_v52` (render + fase de escritura) | 540,8 s (render 10,9 + escritura 529,9) |
| ↳ escritura de documentos | 526,0 s |
| Documentos escritos / omitidos | 46 567 / 0 |
| Memoria pico (working set) | 2,53 GB |
| Tiempo stage DOCUMENTATION | no emitido por `RUN_SUMMARY`; aprox. por mtimes ≈ 145 s (documentación legada) + v52 ≈ 541 s |

## 11. Corrida IST B (repetición sobre la misma salida)

| Medida | Valor |
|---|---:|
| Tiempo total | **220,8 s** |
| `documentation_v52` (render + escritura) | **39,3 s** (≤ 49 s ✔) |
| ↳ render | 8,7 s |
| ↳ verificación | 27,7 s |
| ↳ escritura de documentos | 0,02 s |
| ↳ limpieza | 2,7 s |
| ↳ manifest | 0,07 s |
| Documentos escritos / omitidos | **0 / 46 567** |
| Memoria pico | 2,55 GB |
| Tiempo stage DOCUMENTATION | no medido (misma limitación que A); la parte v52 es 39,3 s |

La verificación (27,7 s) es más lenta que en R2.2 (19,9 s) por variación de I/O/antivirus de la máquina (A: 2,9 s de verificación sin archivos; el margen contra 49 s se mantiene: 39,3 s). No se atribuye a la extracción: el código movido es idéntico.

## 12. Write-skip final

`strict_content` intacto: omisión solo con tamaño y bytes idénticos; manifest previo `valid` solo clasifica contadores; 0 reescrituras en B; `MANIFEST.json` es el único archivo escrito.

## 13. MAX_PATH / long paths

Sin cambios; tests de preflight (bordes, temporal, error `OUTPUT_PATH_TOO_LONG`) y la prueba real de rutas > 259 caracteres en Windows con `--long-paths` pasan tras la extracción. La corrida IST usó `--output` corto (sin `--long-paths`).

## 14. Deuda técnica

| Hallazgo | Clase |
|---|---|
| `writer.py` HIGH (252 líneas, `write_tree` ~60 líneas) | OBSERVATION |
| `RUN_SUMMARY` no emite duración por stage; DOCUMENTATION no medible directamente | OBSERVATION |
| Verificación 20–28 s sin File State (sin cambio respecto a R2.2) | NEXT_ROUND (R2.4, opcional) |
| `fsync` por archivo, preflight solo en v52, demás stages reescriben todo | NEXT_ROUND (heredado de R2.2: D-2, D-4, D-10) |
| BLOCKING / CURRENT_PHASE | ninguno |

## 15. Riesgos

Tiempos dependientes de I/O y antivirus (B varió 32,2 → 39,3 s entre rondas, dentro del objetivo). `result: Any` en `writer.py` pierde tipado estático a cambio de evitar el ciclo. Equivalencia IST completa contra el motor anterior no repetida (ver §9).

## 16. Fuera de alcance confirmado

No se inició R2.3; sin fingerprints, versiones, File State, `_cache_v53/`, extraction cache ni ampliación de write-skip; sin cambios en MAX_PATH, `--long-paths`, IDs, Evidence Core, manifests ni CLI; sin IA; `PROJECT_STATE.json` intacto; sin commit/tag/push. Las salidas de medición (`output/_r221_a`) se eliminaron.

## 17. Estado Git (solo consultas)

Rama `main`, HEAD `6c32c4c`. Modificados: `cli/full_pipeline.py`, `cli/parser.py`, `cli/pipeline_stages.py`, `cli/router.py`, `context/hydration.py`, `documentation_v52/engine.py`, `tests/test_v4_1_r0_maintainability_inventory.py`. Nuevos: `documentation_v52/writer.py`, `context/hydration_view.py`, `utils/path_limits.py`, `tests/test_v5_3_r2_1_*.py`, `tests/test_v5_3_r2_2_*.py`, `docs/V5/` (R0…R2.2.1, V5_2_GIT_CLOSURE_RESULT), `prompts/V5/`. Pendiente administrativo previo: los cambios sin commit de R2.1/R2.2 (el cierre Git de V5.2 ya está hecho: commit, tag `v5.2` y publicación en `origin/main`).

## 18. Estado final

Criterios: `engine.py` MEDIUM (reducido); `writer.py` justificado; suite verde; salida byte-idéntica (fixtures + verificación IST); write-skip seguro; v52 repetición 39,3 s ≤ 49 s; 0 reescritos; MAX_PATH y `--long-paths` operativos; alcance respetado.

**V5_3_R2_2_1_READY_FOR_REVIEW**
