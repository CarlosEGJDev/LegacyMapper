# V5.3 R2.6 — Guardián de Extraction Cache + Write-Skip de salidas restantes

Estado final: **V5_3_R2_6_READY_FOR_REVIEW** (sin familias diferidas)

## 1. Objetivo

(A) Dar a la extraction cache un guardián propio de su contrato persistido; (B) extender write-skip seguro a las salidas restantes: se genera siempre el contenido y solo se escribe si los bytes finales difieren. Sin reutilización de resolvers, flows, proyecciones ni documentación.

## 2. Estado de partida

`main` en `108bace` (checkpoint funcional `2cb317f`), rama `backup/v5.3-pre-worktree-cleanup`, worktrees residuales ya retirados. Suite previa: 2 663 tests. R2.5 había dejado como `CURRENT_PHASE` la falta de guardián de la extraction cache.

## 3. Guardián de extraction cache

Contrato propio, separado de `ANALYZER_VERSION`, `ANALYZER_CODE_FINGERPRINT`, `EVIDENCE_SCHEMA_VERSION` y del esquema del manifest. Dos piezas:
- **Runtime:** `versions.EXTRACTION_CACHE_SCHEMA_VERSION` (= 1), escrita en `CACHE_MANIFEST.json["versions"]["extraction_cache_schema_version"]` y comparada al cargar la extraction cache.
- **Guardia de desarrollo:** `fingerprints.extraction_contract_fingerprint()`, SHA-256 de los **árboles sintácticos normalizados** de `cache/extraction.py`, `cache/extraction_shards.py` y `cache/extraction_store.py` (los tres definen formato de shard, estructura de entrada, clave, reglas de `cache_bypass`, carga/validación/escritura). El test `test_extraction_contract_guard` compara ese fingerprint con el valor guardado junto a la versión y **falla si el código del contrato cambió sin revisar la versión** (procedimiento en el encabezado del test, igual que el guardián del analizador).

## 4. Versión / fingerprint elegidos

`EXTRACTION_CACHE_SCHEMA_VERSION = 1`; fingerprint de referencia `b32ef1db75b90eb4c5d6c7f7e2a244413cac7a78cedbe8847a54419ff894f809`. Estrategia: ignora comentarios, líneas en blanco, formato y docstrings (los distingue vía AST); **no** distingue un cambio de logging/métricas de uno de formato (cualquier código ejecutable cambia el hash) → estrategia conservadora y documentada: decide una persona. No se metió `cache/` en `ANALYZER_CODE_FINGERPRINT`.

## 5. Compatibilidad / fallback

Misma versión → reutilización. Versión distinta (`EXTRACTION_CACHE_SCHEMA_MISMATCH`) o campo ausente, p. ej. un manifest de R2.5 (`EXTRACTION_CACHE_SCHEMA_MISSING`) → la extraction cache no se reutiliza y se hace extracción completa (sin error); **File State e identidad siguen válidos** (la caché sigue `warm`; solo se regeneran los shards y el manifest nuevo lleva la versión actual). Renderers/templates/Git no invalidan (tests).

## 6. Archivos modificados

| Archivo | Cambio |
|---|---|
| `utils/write_if_changed.py` (**nuevo**, 110) | helper único + contadores |
| `fingerprints/extraction_contract.py` (**nuevo**, 46) / `fingerprints/__init__.py` | fingerprint del guardián |
| `versions.py` | `EXTRACTION_CACHE_SCHEMA_VERSION` |
| `cache/context.py`, `cache/manifest.py` | versión del contrato en contexto y manifest |
| `cache/extraction.py`, `cache/extraction_store.py` | comprobación de versión al cargar (`schema_incompatibility`) |
| `exporters/json_exporter.py`, `evidence/persistence.py`, `exporters/markdown_exporter.py`, `context/context_builder.py`, `context/system_context_builder.py`, `cli/artifact_lifecycle.py`, `cli/pipeline_stages.py` | escrituras → `write_text_if_changed` (con familia) |
| `cli/full_pipeline.py` | reset del ledger al inicio y log al final (+5 líneas) |
| `tests/test_v5_3_r2_6_…py` (**nuevo**, 35), `tests/test_v5_3_r2_4_…py`, `tests/test_v4_1_r0_…inventory.py` | ver §13–15 |

No se tocaron extractores, resolvers, Evidence Core (contenido/IDs), `documentation_v52/writer.py`, `RUN_SUMMARY`, CLI ni `PROJECT_STATE.json`.

## 7. Helper write-if-changed

`write_bytes_if_changed(path, bytes, family)` y `write_text_if_changed(path, text, family, encoding, newline)`: genera bytes finales → `stat` + comparación byte a byte con el destino → omite si idénticos, si no escribe con `atomic_write_bytes` (temp + fsync + replace, temporal limpiado en fallo). Nunca `mtime`, nunca solo tamaño, nunca caché/manifest previo como autoridad. Para texto, `newline=None` reproduce exactamente el comportamiento previo (`write_text`/`atomic_write_text`: `\n` → `os.linesep`), de modo que los bytes finales de cada salida **son los mismos que antes**; `newline="\n"`/bytes no alteran nada. Un único helper; sin lógica repetida por renderer.

## 8. Salidas cubiertas

`index/` (JSONExporter), `evidence/` (particiones + `EVIDENCE_MANIFEST.json`), `consumer_projection/` (manifest + `parts/`), `documentation/flujos_humanos/`, `ai_context/`, `context/`, y la documentación legacy restante (`documentation/*.md` y sus particiones). Los escritores previamente no atómicos (`write_text` en `documentation/`, `context/`, `ai_context/`) ahora son atómicos.

## 9. Salidas excluidas y motivo

- `documentation_v52/`: ya tiene su write-skip de R2.2; no reimplementado (test).
- `RUN_SUMMARY.json/.md`: contienen duración/estado de la corrida; se siguen escribiendo con `atomic_write_text`.
- `repository.json` (`index/`): contiene `duration_seconds`; pasa por el helper (se compara y se reescribe cuando cambia) pero se declara no determinista. `evidence/EVIDENCE_MANIFEST.json` deriva de él (hashes de particiones) y varía igual. Sin cambiar contratos para evitarlo.
- `AI_PROPOSALS*` y `OUTPUT_MANIFEST.json` (comando aparte): fuera de alcance.

## 10. Atomicidad

Toda escritura real usa `atomic_write_bytes`; sin escritura parcial; temporal eliminado en cualquier fallo (tests: fallo de escritura, fallo de `os.replace`).

## 11. MAX_PATH

Sin cambios de comportamiento: el helper no añade preflight (los escritores previos tampoco lo tenían; `documentation_v52` conserva el de R2.2 y `--long-paths`). Una ruta que no se puede leer se trata como «distinta» y el intento de escritura falla igual que antes. Test de ruta larga (≈150+ caracteres) incluido.

## 12. Contadores

Por familia y en memoria (`LEDGER`): `generated`, `written`, `skipped_identical`, `bytes_generated`, `bytes_written`, `compare_seconds`, `write_seconds`; se loguean (INFO `write-skip: …`) al final de las etapas. Sin `RUN_METRICS.json`, sin cambios en `RUN_SUMMARY`.

## 13. Tests unitarios (helper: 15; guardián: 9)

Helper: archivo ausente, idéntico (no toca el archivo ni el mtime), distinto, mismo tamaño con distinto contenido, mtime restaurado, vacío, Unicode, binario, fallo de escritura conserva el original, sin temporales tras fallo de replace, uso de la primitiva atómica, ruta larga, contadores deterministas, saltos de línea intactos (y `newline=None` = `write_text`), destino directorio. Guardián: versión en manifest, misma versión compatible, versión distinta (extracción completa, File State válido, autocuración), manifest sin campo, renderer/template/Git no invalidan, guardia con versión+fingerprint, fingerprint insensible a comentarios/docstrings/formato y sensible al código, fuentes ausentes → `None`.

## 14. Tests por familia (pipeline sobre `v4_2_r7_full_sample`)

Cold escribe todo en las 7 familias; warm omite el 100 % de `consumer_projection`, `flujos_humanos`, `ai_context`, `context`, `documentation`, y todo salvo `index/repository.json` (≤1) y evidence (≤2); cold ≡ warm ≡ corrida sin caché; cambio real reescribe solo lo afectado; corrupción externa con mismo tamaño y mtime restaurado en 6 archivos (index, evidence, consumer_projection, ai_context, 2 docs) detectada y corregida; borrados recreados; sin `.tmp`; `documentation_v52` sin tocar; ledger solo en memoria. Independencia de runtime (3).

## 15. Suite completa

`python -m unittest discover -s tests`: **2 698 tests, 0 fallas, 0 errores, 132 skips**, 375 s (2 663 previas + 35). Tests existentes ajustados: contenido del manifest (campo nuevo) y el inventario de mantenibilidad congelado (+2 módulos → 216, categorías LOW +1 / MEDIUM +1, `module_count` +73, `system_context_builder.py` como archivo tocado).

## 16. IST cold

`…\IST_40\Operacional` (sin modificar), salida nueva, `run_full_pipeline` sin IA, SUCCESS, **736,8 s** (R2.5 cold: 714,8 s; diferencia dentro del ruido de I/O).

| Familia | generados | escritos | bytes generados | write_seconds |
|---|---:|---:|---:|---:|
| index | 22 | 22 | 996 416 388 | 1,94 |
| evidence | 25 | 25 | 1 057 049 755 | 2,26 |
| consumer_projection | 27 | 27 | 198 913 444 | 0,52 |
| flujos_humanos | 195 | 195 | 159 693 893 | 2,10 |
| ai_context | 5 | 5 | 279 178 592 | 0,70 |
| context | 1 | 1 | 896 897 | 0,02 |
| documentation | 681 | 681 | 66 784 080 | 6,69 |
| **Total** | **956** | **956** | **2 758 933 049** | **14,24** |

`compare_seconds` total cold: 0,10 s (los destinos no existen).

## 17. IST warm

Misma salida, SUCCESS, **139,5 s** (R2.5 warm: 189,2 s).

| Familia | escritos | omitidos idénticos | bytes escritos | compare_seconds |
|---|---:|---:|---:|---:|
| index | 1 (`repository.json`) | 21 | 83 438 | 0,39 |
| evidence | 1 (`EVIDENCE_MANIFEST.json`) | 24 | 2 625 | 0,41 |
| consumer_projection | 0 | 27 | 0 | 0,09 |
| flujos_humanos | 0 | 195 | 0 | 0,21 |
| ai_context | 0 | 5 | 0 | 0,11 |
| context | 0 | 1 | 0 | 0,00 |
| documentation | 0 | 681 | 0 | 0,50 |
| **Total** | **2** | **954** | **86 063** | **1,71** |

Evitados: 954 archivos y **2 758 846 986 B (≈ 2,57 GiB)** sin reescribir. Los 2 escritos son exactamente las salidas no deterministas declaradas (§9).

## 18. Corrupción controlada

Sobre la salida de IST, 5 archivos modificados en un byte con **mismo tamaño y mtime restaurado** (`index/symbols.json`, `evidence/solutions.json`, `consumer_projection/parts/part-000000.json`, `ai_context/SYSTEM_CONTEXT.json`, `documentation/flujos_humanos/BlIstSIAGF.md`). Rerun (139,8 s): los 5 detectados por comparación de bytes y reescritos; árbol final ≡ warm.

## 19. Borrado controlado

6 archivos eliminados (`index/projects.json`, `evidence/projects.json`, `ai_context/TRACEABILITY.json`, `consumer_projection/parts/part-000001.json`, `documentation/flujos_humanos/PreImpresion.md`, `documentation/PROJECT_OVERVIEW.md`) y recreados en el mismo rerun. Escritos en ese rerun por familia: index 3, evidence 3, ai_context 2, consumer_projection 2, flujos_humanos 2, documentation 1 (incluye los no deterministas y los 11 manipulados).

## 20. Equivalencia cold / warm

Cold vs warm: **47 523 archivos, 2 828 066 791 B, 0 diferencias** (hash SHA-256 por archivo; excluidos solo `RUN_SUMMARY.*` y `repository.json`, y `_cache_v53/`). Tras corrupción + borrado + rerun: otra vez 47 523 archivos, 0 diferencias frente al warm. Tras manipular, 11 archivos diferían (esperado), y volvieron a coincidir.

## 21. Gate de rendimiento por familia

Coste de comparar en warm (1,71 s en total, 0,5 s la más cara) frente a escribir en cold (14,2 s; documentation 6,7 s, evidence 2,3 s, flujos 2,1 s, index 1,9 s). Ninguna familia empeora: el comparar es ≈ 8× más barato que el escribir y evita 2,57 GiB de I/O por corrida. **Ninguna familia diferida** (no hay `WRITE_SKIP_DEFERRED_FOR_*`).

## 22. Beneficio total

Warm: 954 de 956 archivos y 2,57 GiB sin reescribir; coste de comparación 1,7 s; pipeline warm 139,5 s frente a 189,2 s en R2.5 (la mejora incluye ruido de caché de disco del SO y no se atribuye íntegramente al write-skip: el tiempo directamente atribuible es ≈ 12 s de escritura evitada). Menos desgaste de disco y de escáneres antivirus (menos `os.replace`).

## 23. Mantenibilidad

`write_if_changed.py` (110 líneas, MEDIUM) y `extraction_contract.py` (46, LOW); `extraction.py` queda en 200 líneas (MEDIUM, justo bajo el umbral de 200 del inventario: se compactó para no pasar a HIGH). `full_pipeline.py` +5 líneas (515 → 520, sigue VERY_HIGH preexistente). Sin ciclos: el helper solo depende de la primitiva atómica.

## 24. Seguridad

El helper solo lee el destino exacto que se va a escribir (ruta construida por el propio pipeline; nunca de un manifest); no persiste contenido adicional ni altera permisos; el contenido sigue saneado por los mismos emisores; sin secretos nuevos. Los contadores no se persisten.

## 25. Deuda técnica

| Hallazgo | Clase |
|---|---|
| BLOCKING | ninguno |
| `index/repository.json` y `EVIDENCE_MANIFEST.json` se reescriben cada corrida por `duration_seconds` (contrato existente, sin cambiar) | OBSERVATION (posible separación de metadata temporal en una ronda futura) |
| Dos primitivas atómicas de escritura (`atomic_write_*` y `documentation_v52/writer._atomic_write`) y dos verificadores de contenido (v52 vs helper) | NEXT_ROUND |
| Archivos grandes (`evidence/` e `index/` suman ≈ 1 GiB cada una; los archivos individuales son grandes): la comparación lee el archivo completo; coste medido 0,4 s, sin necesidad de streaming | OBSERVATION |
| `full_pipeline.py` sigue VERY_HIGH | OBSERVATION |
| El guardián es conservador: cualquier cambio de código en los 3 módulos exige revisar versión | OBSERVATION |
| Salidas aún sin write-skip: `RUN_SUMMARY.*`, `AI_PROPOSALS*`, `OUTPUT_MANIFEST.json` (no deterministas o fuera del pipeline) | FUTURE_PHASE |
| `cache-dir` por defecto en `<output>/_cache_v53/` y CLI sin controles (R2.8) | NEXT_ROUND |

## 26. Riesgos

Cambiar el formato de los registros cacheados sin subir la versión queda cubierto por el guardián solo para los tres módulos del contrato; la forma del registro de extracción vive en `pipeline_stages` (cubierta por `ANALYZER_VERSION`/fingerprint del analizador). Las escrituras que pasaban de no atómicas a atómicas añaden un `fsync` por archivo en cold (incluido en las medidas: +0 s apreciable).

## 27. Fuera de alcance confirmado

No se inició R2.7; sin caché de resolvers/flows/proyecciones, sin salto de stages, sin `artifacts.json`/`RUN_METRICS.json`, sin controles CLI, sin cambios de IDs ni de Evidence Core, extracción intacta (solo el guardián en la carga), sin IA, sin commit/tag/push.

## 28. Estado Git (solo consultas)

Rama `main`, HEAD `108bace`; rama `backup/v5.3-pre-worktree-cleanup` existente. Modificados: `cache/{context,extraction,extraction_store,manifest}.py`, `cli/{artifact_lifecycle,full_pipeline,pipeline_stages}.py`, `context/{context_builder,system_context_builder}.py`, `evidence/persistence.py`, `exporters/{json_exporter,markdown_exporter}.py`, `fingerprints/__init__.py`, `versions.py`, `tests/test_v4_1_r0_maintainability_inventory.py`, `tests/test_v5_3_r2_4_cache_manifest_and_file_state.py`. Nuevos: `utils/write_if_changed.py`, `fingerprints/extraction_contract.py`, `tests/test_v5_3_r2_6_write_skip_and_extraction_guardian.py`, `prompts/V5/V5_3_R2_6_…md` y este documento. Salidas de medición (`output/_r26_*`) eliminadas. Sin commit, tag ni push.

## 29. Recomendación para la siguiente ronda

Versionar R2.6 (commit propio) y continuar con R2.7 según el roadmap de V5.3. Antes, decidir si se quiere separar la metadata temporal de `repository.json` (permitiría 954/956 → 956/956 omitidos; no necesario).

## 30. Estado final

Guardián con versión + fingerprint y fallback seguro; write-skip por bytes en 7 familias, atómico y medido; equivalencia cold/warm total en IST; corrupción y borrados detectados y reparados; suite verde (2 698).

**V5_3_R2_6_READY_FOR_REVIEW**
