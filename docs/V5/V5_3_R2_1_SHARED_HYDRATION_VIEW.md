# V5.3 R2.1 — HydrationView compartida

Estado final: **V5_3_R2_1_READY_FOR_REVIEW**

Se implementó únicamente lo definido en R1 §6.D (nivel 1): índices construidos una vez, memoización por `flow_id` y una única vista compartida por corrida. No hay caché persistida, ni write-skip, ni MAX_PATH, ni fingerprints, ni opciones CLI nuevas, ni cambios de IDs, Evidence Core, manifests o `CallResolver`. Sin IA. Sin commit, tag ni push. No se inició R2.2.

## 1. Resumen de implementación

- **Causa corregida (R1 M1):** `EvidenceHydrator.hydrate_flow` reconstruía 5 diccionarios y recorría los 170 020 paths y los 74 633 parámetros en cada llamada. Ahora los lookups (`flow_id→flow`, `id→entry_point`, `id→data_access`, `id→stored_procedure`, `id→sql_operation`, `flow_id→[paths]`, `caller→nombres de parámetro`) se construyen **una vez**.
- **Algoritmo de hidratación sin cambios**: mismos helpers (`select_and_deduplicate_paths`, `_hydrate_path_group`, `_terminals`, …), mismos campos, orden, `provenance` y `model_version`. `EvidenceHydrator.MODEL_VERSION` sigue `V4.3-R3`.
- **`HydrationView`** (nuevo): vista por corrida, perezosa, ligada a un `ix`, con memoización y contadores. El pipeline crea una sola y la comparte entre `consumer_projection` (CONTEXT) y `HUMAN_DOCUMENTATION` (DOCUMENTATION).
- **Resultado medido:** la hidratación de los 12 642 flows pasó de ≈ 1 050–1 100 s (2 pasadas) a ≈ 1–2 s. Corrida IST completa: **1 620–1 779 s → 632–642 s**.

## 2. Archivos modificados

| Archivo | Cambio |
|---|---|
| `legacy_documenter/context/hydration.py` (314 → 372 líneas) | `hydrate_flow` usa lookups indexados con un slot por instancia (clave: identidad + longitud de las 7 listas fuente); nuevo `_hydrate_indexed`; `_parameters_indexed`; clase interna `_HydrationLookups`; sin memoización ni estado global |
| `legacy_documenter/context/hydration_view.py` (**nuevo**, 80 líneas) | `HydrationView` |
| `legacy_documenter/cli/pipeline_stages.py` | `create_run_flow_source`, `log_run_flow_source_stats`; parámetro opcional `hydration_view` en `build_context_artifacts`, `_write_consumer_projection`, `render_documentation` |
| `legacy_documenter/cli/full_pipeline.py` | crea la fuente una vez y la pasa a CONTEXT y DOCUMENTATION como identificador opaco |
| `tests/test_v5_3_r2_1_shared_hydration_view.py` (**nuevo**, 23 tests) | ver §7 |
| `tests/test_v4_1_r0_maintainability_inventory.py` (**modificado**) | registra el módulo nuevo en el inventario histórico congelado (ver §12, D-2) |
| `prompts/V5/V5_3_R2_1_SHARED_HYDRATION_VIEW.md` | movido desde `prompts/V5_0/` (convención V5.3) |
| `docs/V5/V5_3_R2_1_SHARED_HYDRATION_VIEW.md` | este informe |

`main.py` y `PROJECT_STATE.json` no se tocaron.

## 3. Diseño final de `HydrationView`

```text
HydrationView(ix, hydrator=None, memoize=True)
  hydrate_flow(flow_id, ix=None) -> dict   # duck-type de EvidenceHydrator.hydrate_flow(flow_id, ix)
  stats -> {requests, hydrations, memo_hits, distinct_flows_hydrated, build_seconds, hydrate_seconds}
```

- **Perezosa:** nada se indexa hasta la primera solicitud, dentro del stage consumidor (un fallo de indexación queda dentro de su frontera de fallo, como antes).
- **Ligada a su `ix`:** pedir con otro `ix` lanza `ValueError` (no mezcla evidencia).
- **Memoización con copia defensiva:** guarda el registro *pristino* y entrega a cada solicitud su propia copia profunda. Medido en IST: copiar los 12 642 registros cuesta ≈ 1 s (0,06 s por 500), frente a ≈ 550 s de la hidratación anterior; por eso se mantiene la copia (cumple "sin objetos mutables compartidos") en vez de asumir que ningún consumidor muta. Además se auditó que los consumidores no mutan registros (`ConsumerProjectionBuilder.package`, `AiProjectionBuilder.package` y los renderers humanos solo leen).
- **Sin disco, sin estado global, sin IA;** solo biblioteca estándar (`collections`, `copy`, `time`).
- `EvidenceHydrator.hydrate_flow(flow_id, ix)` conserva su API: devuelve un registro nuevo en cada llamada (sin memo) pero ya indexa una vez por objeto `ix` dentro de la misma instancia, de modo que los llamadores existentes (p. ej. un `ConsumerProjectionBuilder()` por defecto, `AiProjectionBuilder`) también dejan de ser cuadráticos sin cambiar su código.

## 4. Cómo se comparte entre consumidores

`run_full_pipeline` llama `stages.create_run_flow_source(indexes)` una vez tras ensamblar los índices y pasa el mismo identificador a `build_context_artifacts` (→ `ConsumerProjectionBuilder(hydrator=vista)`) y a `render_documentation` (→ `HUMAN_DOCUMENTATION`). La creación y el registro de contadores viven en `pipeline_stages`, no en el orquestador: el test existente `test_hydration_wiring_is_confined_to_pipeline_stages` (V4.3-R2) exige que `full_pipeline.py` no nombre la hidratación y se respetó sin modificarlo.

**Fuera de la vista compartida:** la etapa opt-in de IA (`orchestration/ai_interpretation.py`) recarga los índices desde disco (otro objeto `ix`), por lo que no puede compartir la vista de la corrida; no cambia, pero su `AiProjectionBuilder()` por defecto ya se beneficia de la indexación por instancia (ver D-3). El camino `analyze` (solo CONTEXT) usa el builder por defecto, también indexado.

## 5. Cómo se evita la doble hidratación

`consumer_projection` hidrata los 12 642 flows (miss); `HUMAN_DOCUMENTATION` los pide otra vez y se sirven de la memo (hit). Contadores reales de la corrida IST (log `Hydration:` y `meta`): `requests 25 284` (2 × 12 642), **`hydrations 12 642`**, `memo_hits 12 642`, `distinct_flows_hydrated 12 642`. Verificado además por test sobre un pipeline completo (fixture): `hydrations == flows`, `requests == 2 × flows`, `memo_hits == flows`.

## 6. Compatibilidad de salida

- **12 642 flows de IST:** JSON canónico (SHA-256, claves ordenadas) de la implementación anterior (extraída de `git HEAD`) frente a la nueva: **12 642 idénticos, 0 diferentes** (ejecutado sobre el código final). También idénticos entre `HydrationView` y `EvidenceHydrator.hydrate_flow`.
- **Árbol de salida completo de una corrida IST:** código nuevo vs código anterior (`git archive HEAD`), 47 526 archivos cada uno: **47 525 byte-idénticos**; el único distinto es `index/repository.json` y solo por `duration_seconds` (no determinista, excluido desde V5.0 D-01); igual ignorando ese campo. Áreas comparadas sin diferencias: `documentation_v52` (46 568), `documentation` (876, incluye `flujos_humanos`), `consumer_projection` (27), `evidence` (25), `ai_context` (5), `context` (1), `RUN_SUMMARY.*`, `index` (22, 21 idénticos).
- Sin cambios en IDs, Evidence Core, manifests, `RUN_SUMMARY` ni `MODEL_VERSION`.

## 7. Tests dirigidos (23, en `test_v5_3_r2_1_shared_hydration_view.py`)

Cubren los 12 puntos del prompt: equivalencia contra un oráculo con la implementación anterior (fixture sintético con dedup, unresolved, flow sin paths/sin entry point, SQL, transacción, parámetros con nombres vacíos/duplicados) y sobre un fixture real del pipeline; campos y orden de claves; mismo flow dos veces (memo, una hidratación, copias distintas); dos consumidores con la misma vista; ausencia de contaminación por mutación (incluye un consumidor que altera su copia); parámetros por `caller`; flow sin paths; flow con unresolved; flow con data access / stored procedure / SQL; determinismo e independencia del orden de entrada; construcción de lookups una sola vez (vista perezosa y `EvidenceHydrator`); detección de lista reemplazada o ampliada; vista ligada a su `ix`; `MODEL_VERSION` sin cambio; cableado real (`run_full_pipeline`: una vista, 1× hidratación, 2× solicitudes); **salida byte-idéntica de un pipeline completo con hidratación nueva vs hidratación anterior** sobre fixture; independencia de runtime (AST: solo biblioteca estándar y los dos módulos hermanos, sin E/S).

## 8. Comparación completa de los 12 642 flows

Ver §6. Método: mismas estructuras `indexes` (SCAN→FLOW sobre IST oficial `C:\Users\cgalianj\source\IST_40\Operacional`), hidratación anterior (558 s) vs nueva, hash canónico por flow. Resultado: **0 diferencias**.

## 9. Suite completa

`python -m unittest discover -s tests`: **2 472 pruebas, 0 fallas, 0 errores, 132 skips** (los esperados de clon limpio), 255,7 s. Son las 2 449 previas + 23 nuevas. Además los tests de hydration/context/documentation relacionados (`test_v4_3_r2_evidence_hydration`, `test_v4_1_r0_maintainability_inventory`) pasan.

Durante la ronda la primera ejecución completa falló una prueba (`test_on_disk_inventory_matches_fresh_build_if_present`): el inventario histórico de mantenibilidad marcó `hydration.py` como archivo de alto riesgo al crecer de 314 a 443 líneas. Se resolvió separando `HydrationView` en su propio módulo (y, tras detectar que un import diferido creaba un ciclo de dependencias que el mismo inventario prohíbe, invirtiendo la dependencia para que sea de una sola dirección). Ver D-2.

## 10. Métricas IST antes/después

Corridas `full` sin IA sobre IST oficial, sin IA, una tras otra en la misma sesión (código anterior = `git HEAD` vía `git archive`). Se hicieron dos pares de corridas; se muestran ambos porque los tiempos de I/O varían (R0.1 midió ×2–3 frío/caliente) y no se pudo aislar frío de caliente.

| Medida | Antes (par 1 / par 2) | Después (par 1 / par 2) |
|---|---:|---:|
| Tiempo total de la corrida | 1 779 s / 1 620 s | **642 s / 632 s** |
| Hidratación acumulada (`hydrate_flow`) | 1 097 s / 1 053 s (25 284 llamadas) | **0,9 s** (12 642 hidrataciones) + 0,07 s construcción de índices |
| `consumer_projection` | 574,2 s / 527,8 s | **13,5 s / 12,8 s** |
| CONTEXT (stage) | 590,5 s / 541,3 s | **30,2 s / 26,1 s** |
| `HUMAN_DOCUMENTATION` (por diferencia: DOCUMENTATION − v52 − legado) | ≈ 538 s / ≈ 538 s | **≈ 8,7 s / ≈ 8,0 s** |
| `documentation_v52` | 485,8 s / 408,1 s | 469,0 s / 406,8 s (sin cambios; es disco) |
| DOCUMENTATION (stage) | 1 025,4 s / 947,2 s | 478,4 s / 415,5 s |
| EXTRACTION / Evidence Core | 68,7 s, 46,3 s / 58,5 s, 30,9 s | 47,5 s, 41,4 s / 89,8 s, 58,7 s (**ruido de I/O**, sin relación con el cambio) |
| Flows hidratados (vista) | 25 284 llamadas | **12 642** hidrataciones, 12 642 hits |

Microbenchmark sobre IST (un solo proceso, mismas estructuras): antes 548–558 s para los 12 642 flows; ahora ≈ 1–2 s de hidratación + ≈ 1 s de copias defensivas (paso 1 completo 3–5 s incluyendo el hash de comparación).

**Criterios de R1:** hidratación total ≤ 200 s → cumplido con margen (≈ 1–2 s). La estimación de R1 (prototipo de ≈ 90 s por pasada) resultó pesimista porque el prototipo aún recorría `data_parameters` en cada flow; aquí ese recorrido también está indexado.

## 11. Memoria pico

Working set pico **2,62 GB** en ambas versiones (corrida nueva y anterior, iguales hasta la centésima): se alcanza durante EXPORT, antes de cualquier hidratación, y la memo de 12 642 registros no lo supera. El identificador de la fuente compartida se mantiene referenciado hasta que termina `run_full_pipeline` (incluye la etapa de IA opt-in); se podría liberar tras DOCUMENTATION (D-4, sin impacto medido).

Proceso: exit code 0; al final solo `MainThread`, sin hijos, `FINAL_SUMMARY` → retorno de `main()` 0,04–0,41 s.

## 12. Deuda técnica

| ID | Hallazgo | Clase |
|---|---|---|
| D-1 | **La hidratación ya no es un cuello** (≈ 1 s vs ≈ 1 100 s). Por tanto la "caché persistida de flows hidratados" (R1 §6.D nivel 2) queda **sin justificación** con el criterio del propio R1 (solo se haría si leerla fuera más rápido que recomputarla: recomputar cuesta ≈ 1 s). El cuello dominante pasa a ser `documentation_v52` (≈ 407–469 s de ≈ 632–642 s, ≈ 65–73 %), escritura a disco (R1 M2) | **NEXT_ROUND** (R2.2) |
| D-2 | Se modificó el test histórico congelado `test_v4_1_r0_maintainability_inventory.py` para registrar el módulo nuevo: recuento de archivos 193 → 194, `module_count` +51, una ruta nueva en el conjunto de altas y `MEDIUM` +1 (todos con comentario de ronda, como en rondas previas). No se debilitó ninguna aserción; el módulo se creó justamente para no volver `hydration.py` de alto riesgo | **OBSERVATION** |
| D-3 | La etapa opt-in de IA recarga índices desde disco y no puede compartir la vista de la corrida sin cambiar su contrato; se beneficia de la indexación por instancia pero no de la memo compartida (su volumen, acotado por presupuesto, es pequeño) | **OBSERVATION** |
| D-4 | La fuente compartida queda referenciada hasta el final de `run_full_pipeline`; liberarla tras DOCUMENTATION reduciría memoria retenida, sin efecto medido en el pico | **OBSERVATION** |
| D-5 | `_ix_signature` detecta una lista reemplazada o de otro tamaño, no una edición en sitio de un elemento; riesgo solo para llamadores que muten `ix` entre llamadas a la misma instancia de `EvidenceHydrator` (ningún código de producción lo hace; cubierto por test) | **OBSERVATION** |
| D-6 | El ahorro en `analyze` (solo CONTEXT) y en el `ConsumerProjectionBuilder()` por defecto es esperable pero **no se midió** | **OBSERVATION** |
| — | BLOCKING | ninguno |

## 13. Riesgos

| Riesgo | Estado |
|---|---|
| Diferencia de salida | descartado: 12 642/12 642 flows idénticos y 47 525/47 526 archivos idénticos (el restante, solo `duration_seconds`) |
| Contaminación entre consumidores | mitigado con copia defensiva (≈ 1 s) y test de mutación |
| Mezcla de evidencia entre `ix` | la vista lanza `ValueError` si se le pasa otro `ix` |
| Mediciones con varianza de I/O | dos pares de corridas; el efecto de hidratación (≈ 1 000 s) excede con mucho la varianza observada (≈ 100–150 s) |
| Memoria | sin aumento del pico medido |
| Generalización | verificado en IST y fixtures; repositorios con muchos más flows escalan linealmente en flows (índices O(1)), pero no se midieron |

## 14. Confirmación de fuera de alcance

No se implementó: caché persistida, `_cache_v53/`, `CACHE_MANIFEST.json`, `file_state.json`, extraction cache, fingerprints, versiones nuevas del analizador, write-skip, MAX_PATH, opciones CLI, cambios de IDs, de Evidence Core, de manifests ni de `CallResolver`, análisis incremental, scopes ni IA. No se inició R2.2. `PROJECT_STATE.json` no se modificó.

## 15. Estado Git (solo consultas)

Rama `main`, HEAD `6c32c4c` (tag `v5.2`).

Modificados: `legacy_documenter/cli/full_pipeline.py`, `legacy_documenter/cli/pipeline_stages.py`, `legacy_documenter/context/hydration.py`, `tests/test_v4_1_r0_maintainability_inventory.py`.

Sin versionar: `legacy_documenter/context/hydration_view.py`, `tests/test_v5_3_r2_1_shared_hydration_view.py`, `docs/V5/V5_2_GIT_CLOSURE_RESULT.md`, `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md`, `docs/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md`, `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`, `docs/V5/V5_3_R2_1_SHARED_HYDRATION_VIEW.md`, `prompts/V5/` (R0, R0.1, R1, R2.1).

Las salidas generadas de las corridas IST (≈ 5,6 GB en `output/_r21_*`) y la copia de código `git archive` se eliminaron; los scripts temporales de medición quedaron en el scratchpad fuera del repo. No se tocaron los pendientes administrativos.

## 16. Estado final

Todos los criterios de §11 del prompt se cumplen: tests dirigidos y suite completa en verde; 12 642 flows equivalentes; `flows_hydrated = 12 642`; sin doble hidratación; hidratación total ≈ 1–2 s (≤ 200 s); `consumer_projection` y `HUMAN_DOCUMENTATION` mejoran de ≈ 530–575 s a ≈ 8–13 s; salida de consumidores byte-idéntica; sin cambios en manifests, IDs ni Evidence Core; sin caché persistida.

**V5_3_R2_1_READY_FOR_REVIEW**
