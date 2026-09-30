# PRE-V5.1 Rerun Intermittency Investigation — Result

## STATUS

`PRE_V5_1_RERUN_ISSUE_RESOLVED`

Investigación y corrección mínima de la causa raíz de la intermitencia confirmada en `docs/V5/PRE_V5_1_TEST_BASELINE_GATE_RESULT.md`. No se implementó V5.1, no se cambió la arquitectura V5.0, no se modificó `PROJECT_STATE.json` ni ningún baseline congelado. Se corrigió un único punto de producción compartido (`legacy_documenter/utils/atomic_write.py`) con un cambio mínimo (retry acotado), sin tocar ningún assert de test.

## REPRODUCTION

Siguiendo el protocolo del prompt (reproducir de forma controlada antes de modificar código):

1. **Tests afectados en aislamiento absoluto** (los 4 nombrados + el pequeño grupo de 4-6 tests): siempre `OK`. No reproduce.
2. **Módulo R6 completo (25 tests) en solitario:** reproduce de forma intermitente. Primera corrida completa: 3 fallos (`test_ai_enabled_run_then_deterministic_rerun_same_output`, `test_partial_run_then_rerun_recovers`, `test_successful_run_then_successful_rerun`). Segunda corrida completa (sin cambios): 3 fallos distintos (`test_ai_enabled_run_then_deterministic_rerun_same_output`, `test_deterministic_run_then_ai_enabled_rerun_same_output`, `test_partial_run_then_rerun_recovers`). El conjunto exacto de tests que falla varía entre corridas; siempre son tests de `RerunSameOutputTests` (la clase que ejecuta el pipeline dos veces sobre el mismo `--output`).
3. **Secuencia mínima que reproduce:** no se encontró una secuencia corta y determinista. Un script de reproducción que ejecuta las 6 clases de test que preceden a `RerunSameOutputTests` en el orden alfabético que usa `unittest.TestLoader` (`ApprovalAndCanonicalBoundaryTests`, `AtomicWriteTests`, `ExitCodeAndLegacyUnchangedTests`, `FilesystemFailureContainmentTests`, `PathSafetyTests`, `ProposalWriteFailureTests`) y luego repite el escenario de `test_ai_enabled_run_then_deterministic_rerun_same_output` en bucle reprodujo el fallo en el intento 3 de 15 (antes del fix). Esto confirma que la reproducción es **probabilística**, no ligada a un test concreto anterior ni a un orden exacto: cuantos más pipelines se ejecutan en el mismo proceso antes del rerun, mayor la probabilidad de que aparezca.
4. **Evidencia de interferencia capturada:** instrumentando el escenario reproducido se obtuvo el error real, nunca visible en el resumen de `unittest` (que solo reporta `RunStatus.FAILED != RunStatus.SUCCESS`):

   ```text
   StageId.CONTEXT StageStatus.FAILED StageError(
     stage=<StageId.CONTEXT: 'CONTEXT'>,
     category='PermissionError',
     message="[WinError 5] Acceso denegado: "
             "'...\\consumer_projection\\.CONSUMER_PROJECTION.json.j3cbhve5.tmp' -> "
             "'...\\consumer_projection\\CONSUMER_PROJECTION.json'",
     reference=None)
   ```

   El fallo ocurre siempre en el mismo punto lógico: el `os.replace()` de `atomic_write_text` al sobrescribir un archivo que **ya existía** de una corrida anterior dentro del mismo `--output` (es decir, específicamente en el escenario de rerun, nunca en una escritura a una ruta nueva).

## ROOT CAUSE

`atomic_write_text` (`legacy_documenter/utils/atomic_write.py`) escribe un archivo temporal hermano y luego llama `os.replace(tmp_name, path)` una sola vez, sin reintento. En Windows, `os.replace` sobre un destino que **ya existe y fue reescrito recientemente por una corrida anterior del mismo proceso** puede fallar de forma transitoria con `PermissionError` (`[WinError 5] Access is denied`) cuando otro proceso del sistema operativo (el ejemplo más común: el escáner en tiempo real de un antivirus, o el indexador de búsqueda de Windows) mantiene abierto momentáneamente un handle de lectura sobre el archivo justo después de que la corrida anterior lo modificó. Es una condición de carrera externa al proceso Python, no una corrupción de datos: el intento fallido nunca deja el destino en un estado intermedio (el `os.replace` atómico o tiene éxito completo o no se ejecuta), pero sin reintento, un solo intento denegado se propaga como fallo de stage.

Esto explica exactamente los síntomas observados:
- Solo aparece en tests de `RerunSameOutputTests`/`test_rerun_into_the_same_output_remains_safe`, porque son los únicos que escriben dos veces sobre el mismo `--output` (todos los demás tests usan un `--output` nuevo por test vía `tempfile.TemporaryDirectory()`, y la primera escritura a una ruta nueva nunca compite con nada).
- Pasa siempre en aislamiento (una sola corrida por proceso reduce la ventana de exposición al escáner) y falla de forma intermitente cuando se ejecutan muchos pipelines seguidos en el mismo proceso (más escrituras a disco en rápida sucesión → más probabilidad de que el escáner esté todavía procesando un archivo justo modificado en el instante del siguiente `os.replace`).
- El test histórico afectado (`test_deterministic_run_then_ai_enabled_rerun_same_output`) y sus "vecinos" (`test_successful_run_then_successful_rerun`, `test_ai_enabled_run_then_deterministic_rerun_same_output`, `test_partial_run_then_rerun_recovers`, `test_rerun_into_the_same_output_remains_safe`) son exactamente el conjunto de tests con esta forma (rerun sobre el mismo directorio); no hay ningún factor compartido de test (fixture, mock, monkeypatch, variable de entorno, `cwd`, registry global) entre ellos más allá de ejercer ese mismo camino de producción.

`atomic_write_text` es el único punto de escritura atómica compartido por `RUN_SUMMARY.json`/`.md`, `AI_PROPOSALS.json`/`.md`, `index/*.json`, `consumer_projection/CONSUMER_PROJECTION.json` y las particiones sincronizadas (`sync_generated_json_partition_directory`), de modo que la misma causa raíz explica por qué la corrida específica que falla varía (cualquiera de esos archivos puede ser el que golpea la ventana de carrera en un momento dado), no solo `CONSUMER_PROJECTION.json`.

## CLASSIFICATION

`PRODUCTION_RERUN_BUG`

No hay estado global mutable, singleton, registry de provider, caché de módulo, monkeypatch filtrado entre tests, ni problema de `asyncio`/hilos/recursos abiertos: se buscó explícitamente evidencia de cada uno (ver DESIGN) y no se encontró ninguno. La causa es un defecto real, aunque de bajo impacto y externo en su disparador, en la ruta de producción de escritura atómica: no tolera una denegación de acceso transitoria de Windows al reescribir un archivo existente en un rerun.

## DESIGN

Antes de modificar código se buscó evidencia de cada categoría de interferencia listada en el prompt, usando el mismo script de reproducción instrumentado:

- **Directorios temporales / output dirs reutilizados:** cada test de `RerunSameOutputTests` crea su propio `tempfile.TemporaryDirectory()` fresco; no hay reutilización entre tests. Descartado como causa entre tests distintos (aunque sí es la condición necesaria para que un mismo test dispare la carrera consigo mismo, al escribir dos veces).
- **Variables de entorno / cwd:** sin cambios entre corridas exitosas y fallidas del mismo script.
- **Registry/config globals, caché/estado de módulo:** se inspeccionó `ProviderRegistry`, `FakeLLMProvider` (sin atributos de clase mutables, solo de instancia) y no se encontró ningún `lru_cache`/diccionario a nivel de módulo en el camino de `full_pipeline`/`pipeline_stages`/`atomic_write`.
- **Provider registry state / fake provider state / monkeypatches:** cada test construye su propio `FakeLLMProvider` nuevo; `unittest.mock.patch` usado en otros tests de la clase se deshace automáticamente al salir del `with`.
- **Asyncio state / recursos abiertos:** `FakeLLMProvider` no usa `asyncio`; no hay hilos ni sockets involucrados en el camino que falla.
- **Contenido previo del mismo output / orden de stages:** **sí** es relevante, pero como condición necesaria del escenario (reescribir un archivo existente), no como causa en sí — la causa es que `os.replace` no tolera la denegación transitoria al hacerlo.
- **Cleanup/finalizers:** `tempfile.TemporaryDirectory()` limpia correctamente al salir del `with`; no se observó ningún error de limpieza en los logs capturados.

No se encontró ningún propietario de estado global mutable que documentar (owner/setter/reader/reset), porque no existe: la interferencia es externa al proceso Python (un proceso del sistema operativo reteniendo el handle), no un dato compartido entre tests.

## FILES MODIFIED

- `legacy_documenter/utils/atomic_write.py`: se añadió `_replace_with_retry`, un reintento acotado (5 intentos, backoff exponencial desde 50 ms, ~1.55 s de espera total en el peor caso) específicamente alrededor de `os.replace`, capturando únicamente `PermissionError`. `atomic_write_text` ahora llama a `_replace_with_retry` en vez de `os.replace` directamente; el resto de su contrato (escritura a temporal hermano, `fsync`, limpieza del temporal en cualquier fallo final, propagación de la excepción si los reintentos se agotan) no cambia. No se tocó ningún otro archivo de producción. No se tocó ningún test en esta ronda (los cambios de `tests/test_v4_r13_regression_and_security.py` y `tests/test_v4_r14_manuals_and_final_baseline.py` que aparecen en el árbol de trabajo son de la ronda anterior — Opción A —, no de esta).

## TARGETED TESTS

Tras aplicar el fix, los 6 tests directamente relacionados con el síntoma, ejecutados juntos en un único comando:

```text
Ran 6 tests in 6.945s

OK
```

(`test_deterministic_run_then_ai_enabled_rerun_same_output`, `test_successful_run_then_successful_rerun`, `test_ai_enabled_run_then_deterministic_rerun_same_output`, `test_partial_run_then_rerun_recovers`, `test_ai_failure_after_prior_successful_ai_run_produces_a_fresh_no_proposals_envelope`, `test_rerun_into_the_same_output_remains_safe`.)

Adicionalmente, el script de reproducción en bucle (misma secuencia de 6 clases previas + escenario de rerun con IA, repetido) se corrió **30 veces** tras el fix: **0 fallos en 30 intentos**, frente a la reproducción en el intento 3 de 15 antes del fix.

## R6/R7 STABILITY TESTS

| Corrida | Resultado |
|---|---|
| R6 completo (25 tests), en solitario | `Ran 25 tests` — `OK` |
| R7 completo (16 tests), en solitario | `Ran 16 tests` — `OK` |
| R6+R7 juntos, corrida 1 | `Ran 41 tests` — `OK` |
| R6+R7 juntos, corrida 2 | `Ran 41 tests` — `OK` |
| R6+R7 juntos, corrida 3 | `Ran 41 tests` — `OK` |

Las 3 corridas consecutivas de R6+R7 exigidas como mínimo quedaron todas verdes, sin ningún fallo intermitente.

## FULL SUITE RESULTS

`python -m unittest discover -s tests`, tres corridas consecutivas (se ejecutó una tercera además del mínimo de dos, dada la severidad previa de la intermitencia):

| Corrida | Tests | Failures | Errors | Skips |
|---|---|---|---|---|
| 1 | 2169 | 0 | 0 | 132 |
| 2 | 2169 | 0 | 0 | 132 |
| 3 | 2169 | 0 | 0 | 132 |

Conteo total sin cambios respecto al baseline esperado por R3/el gate anterior (`2169 tests / 132 skips`); no se añadió ni eliminó ningún test en esta ronda.

## PROJECT_STATE CHECK

`PROJECT_STATE.json` no fue editado en ningún momento de esta ronda (`git diff --stat -- PROJECT_STATE.json` vacío antes y después del fix).

## RUNTIME IMPACT

El cambio es aditivo y de alcance mínimo: solo se activa cuando `os.replace` falla con `PermissionError`, algo que en el camino feliz (la gran mayoría de escrituras, incluida toda escritura a una ruta que no existía previamente) nunca ocurre, por lo que no añade latencia medible al caso normal. En el caso de una denegación transitoria real, añade como máximo ~1.55 s de reintentos acotados antes de, si la denegación persiste, propagar exactamente la misma excepción que antes (ningún comportamiento de error se oculta ni se convierte en éxito silencioso). No cambia la atomicidad de la escritura (el `os.replace` en sí sigue siendo la única operación que muta el destino), no cambia qué se escribe, no introduce nuevas dependencias, y aplica igual en todas las plataformas (en POSIX, donde este `PermissionError` transitorio no ocurre en la práctica, el bucle de reintento simplemente nunca se activa).

## RISKS

1. El mecanismo de reintento mitiga la ventana de carrera observada empíricamente (30/30 sin fallos), pero no puede garantizar matemáticamente que una denegación de acceso más larga (p. ej. un escaneo de antivirus inusualmente lento en una máquina cargada) no agote los 5 intentos; en ese caso el comportamiento es idéntico al anterior al fix: la excepción se propaga y el stage se reporta como `FAILED` de forma estructurada, nunca como un traceback crudo ni como un éxito falso.
2. No se identificó ni se intentó identificar el proceso externo exacto (antivirus, indexador, u otro) que retiene el handle; no es necesario para la corrección (el retry es agnóstico a la causa exacta de la denegación transitoria de Windows), pero significa que la frecuencia futura de esta condición en otras máquinas puede variar.
3. El mismo patrón de reintento no se aplicó a las operaciones `os.unlink` de limpieza en `legacy_documenter/cli/artifact_lifecycle.py` (borrado de particiones obsoletas), que en teoría podrían sufrir una denegación transitoria análoga; no se observó evidencia de que esto ocurra (ningún fallo reproducido apuntó a esa ruta) y el prompt exige el arreglo mínimo sustentado por evidencia, así que se dejó fuera de alcance deliberadamente.
4. El riesgo intermitente `test_deterministic_run_then_ai_enabled_rerun_same_output`, registrado en `PROJECT_STATE.json.known_risks.r6_intermittent_test` desde V4.2-R6, ahora tiene una causa raíz identificada y corregida (`PermissionError` transitorio de Windows en `atomic_write_text`); si el síntoma reapareciera pese a esta corrección, ya no debería asumirse la misma causa sin nueva evidencia, dado que el mecanismo de reintento ya cubre el modo de fallo aquí demostrado.

## PRE-V5.1 GATE RECOMMENDATION

Con la causa raíz corregida y validada (30/30 en el script de reproducción dirigido, 3/3 corridas R6+R7 verdes, 3/3 corridas de suite completa verdes con el conteo exacto esperado), se recomienda que una ronda de aprobación humana declare:

```text
PRE_V5_1_GATE_PASSED
```

Esta ronda no lo declara por sí misma (no está entre los estados permitidos de esta ronda ni de la anterior sin aprobación humana explícita), pero dado que los 4 gates de R3 quedan ahora satisfechos con evidencia (Opción A aplicada y estable; suite completa verde de forma reproducible; `PROJECT_STATE.json` sin ediciones retroactivas; arquitectura consolidada sin nuevos conflictos), no queda ningún hallazgo técnico pendiente que bloquee esa declaración.

## NEXT STEP

No se crea el prompt de V5.1. Queda a la espera de aprobación humana para declarar `PRE_V5_1_GATE_PASSED` y autorizar el inicio de V5.1.
