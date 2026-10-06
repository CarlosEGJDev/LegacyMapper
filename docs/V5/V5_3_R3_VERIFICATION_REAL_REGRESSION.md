# V5.3 R3 — Verificación y regresión real

Fecha: 2026-10-06. Estado: `V5_3_R3_READY_FOR_HUMAN_REVIEW`.

## 1. Objetivo

Verificar equivalencia, determinismo, recuperación, seguridad y regresión de V5.3 sin rediseño ni inicio de R4.

## 2. Estado inicial

main; HEAD `aa7db0db6c77d7ec8a1b15f50e33bf176d948bcd`; 6 commits ahead de origin/main local. Backup `backup/v5.3-pre-worktree-cleanup` = `2cb317fe5ae3dd2cbad1f865b1faee4a50a99569`. Pendientes iniciales: informe R2.9.1 y prompt R3. Sin cambios runtime inesperados. Fuentes obligatorias leídas; R1 gobierna. Aprobación humana de R2.9/R2.9.1 regularizada antes de ejecutar, conforme al prompt activo.

## 3. Evidencia R2 reutilizada

R2.9: 33 corridas, 21 equivalencias, suite 2834/0/0/132; ratio None diferido y defaults aprobados. No se repitió rejilla ni calibración. Reutilizados la copia controlada de IST y los productos H (151 archivos VB modificados de forma independiente); fuente congelada durante R3. Referencia refresh previa confrontada byte a byte con una nueva corrida off/full. El input tiene 15138 archivos, 8106 analizados; no se presenta como fuente oficial sin mutaciones. Cache externa cold/borrado/regeneración e identidad entre repos se revalidan con fixtures; warm externa también en IST.

## 4. Archivos modificados

Nuevo: `tests/test_v5_3_r3_verification.py` y este informe. Modificados: PROJECT_STATE y los dos documentos de continuidad. Scripts, huellas y telemetría locales en `output/_local_r3/` (ignorado); productos/cache reutilizados en `output/v53r29/` (ignorado). Sin cambios runtime/cache, contratos o defaults.

## 5. Matriz de regresión canónica

| Corrida | Wall s | Stage EXTRACTION s | Session | Hits/misses | Equivalencia |
| --- | --- | --- | --- | --- | --- |
| off_reference | 673.798 | 103.370 | off | NA/NA | PASS |
| auto_cold | 341.469 | 71.548 | cold | 0/8106 | PASS |
| warm_1 | 193.590 | 0.238 | warm | 8064/42 | PASS |
| warm_2 | 202.520 | 0.265 | warm | 8064/42 | PASS |
| refresh | 324.835 | 75.306 | refresh | 0/8106 | PASS |
| verify_hash | 219.643 | 0.914 | warm | 8064/42 | PASS |
| external_warm | 227.175 | 0.243 | warm | 8064/42 | PASS |

Verify fast cubierto por cold/warm/refresh; verify hash por corrida propia. Todas las variantes confrontadas con el mismo snapshot full/off; sin nuevas exclusiones.

## 6. Determinismo

warm_1 y warm_2 son procesos independientes, mismo input congelado, ambos iguales al snapshot off por SHA-256/tamaño/conteo de cada archivo. Igualdad transitiva byte a byte entre ambas; IDs, estados y manifests canónicos incluidos. Cache validada y deep hash sano tras cada corrida cacheada.

## 7. Matriz de cache inválida

Fixture `v4_2_r7_full_sample`; cada caso parte de la misma cache sana. Corrida de recuperación + warm/hash posterior y comparación canónica completa en ambas.

| Caso | Session | Fallback reason | Reuse disabled | Hits/misses | SUCCESS/equiv/autocura |
| --- | --- | --- | --- | --- | --- |
| manifest_missing | fallback_full | INCOMPLETE_CACHE | — | 0/8 | PASS/PASS/PASS |
| manifest_json | fallback_full | MANIFEST_CORRUPT | — | 0/8 | PASS/PASS/PASS |
| file_state_checksum | fallback_full | FILE_STATE_CHECKSUM_MISMATCH | — | 0/8 | PASS/PASS/PASS |
| file_state_json | fallback_full | FILE_STATE_CORRUPT | — | 0/8 | PASS/PASS/PASS |
| shard_fast | warm | — | — | 7/1 | PASS/PASS/PASS |
| shard_hash | fallback_full | VERIFY_CACHE_FAILED | — | 0/8 | PASS/PASS/PASS |
| multiple_shards | warm | — | MULTIPLE_SHARDS_INVALID | 0/8 | PASS/PASS/PASS |
| extraction_schema | warm | — | EXTRACTION_CACHE_SCHEMA_MISMATCH | 0/8 | PASS/PASS/PASS |
| analyzer_version | fallback_full | ANALYZER_VERSION_MISMATCH | — | 0/8 | PASS/PASS/PASS |
| analyzer_fingerprint | fallback_full | ANALYZER_CODE_FINGERPRINT_MISMATCH | — | 0/8 | PASS/PASS/PASS |
| repository_identity | fallback_full | REPOSITORY_MISMATCH | — | 0/8 | PASS/PASS/PASS |
| analysis_config | fallback_full | ANALYSIS_CONFIG_MISMATCH | — | 0/8 | PASS/PASS/PASS |
| directory_deleted | cold | NO_CACHE | — | 0/8 | PASS/PASS/PASS |

Múltiples shards y schema de extracción pueden conservar session=warm porque File State sigue compatible; extracción se deshabilita completa y hits=0. No confundir esa observabilidad con reutilización de evidencia inválida. Fast tolera un shard con miss parcial; hash exige fallback full.

## 8. Interrupción / manifest-last

KeyboardInterrupt inyectado en la escritura final CACHE_MANIFEST, después de File State/shards. Sin manifest final; siguiente corrida INCOMPLETE_CACHE/fallback_full con hits=0, SUCCESS, equivalencia y cache sana. Tests previos de orden de escritura y FAILED/PARTIAL también ejecutados por suite completa.

## 9. Cache externa

Fixtures revalidan cold→warm→borrado→cold regenerado, no dependencia del producto, identidad de otro repo, métricas sin raíz absoluta y housekeeping que preserva contenido ajeno. IST external_warm usa copia íntegra de la cache sana interna con misma identidad del input; resultado equivalente a off. No se declara cold externa nueva en IST.

## 10. Junction / reparse

PASS real en Windows: cuatro junctions mediante `mklink /J`, sin elevación. Path.resolve entrega destino real; destinos repo, ancestro común que contiene repo/output y output rechazados; destino externo seguro aceptado. Sentinel intacto y sin manifest en repo. Limpieza solo os.rmdir sobre entrada junction, nunca eliminación recursiva del destino. No aplica WINDOWS_REPARSE_REAL_TEST_NOT_AVAILABLE.

## 11. Seguridad / sanitización

IST oficial: auditoría SHA-256 e inventario antes y después; 15138 archivos intactos. Copia controlada sin nuevas mutaciones en R3. Corridas manuales sin IA solicitada/invocada; provider/LLM real=0. Suite con proveedores fake y guard de resolución real. Telemetría/exportes saneados centralmente; stdout/stderr crudos de procesos no persistidos. Tests existentes de bypass ante sanitize_data, secretos ausentes en shards, paths externos omitidos y errores saneados revalidados.

## 12. Invariantes

Evidence Core, IDs y confirmed/inferred/unresolved idénticos dentro de la comparación de todos los productos; manifests incluidos. Resolvers globales recomputan (stages medidos en todas las corridas); scope observacional, sin stage skipping, recomputación parcial, flow cache ni projection cache. artifacts.json diferido por contrato. Defaults auto / fast / trust-mtime=false / ratio=None confirmados por tests. Sin cambios en legacy_documenter/.

## 13. Performance regression check

Warm wall 193.590/202.520 s; refresh 324.835 s; off 673.798 s; verify hash directo 2.63 s.

La tabla de regresión mide el stage EXTRACTION completo; los valores siguientes corresponden a extraction_cache.extraction_seconds.

R2.9 referencia: warm inicial 191.389 s, warm verify fast 168.515–188.447 s, refresh 279.444 s, off nuevo 668.418 s; hash directo 2.421–5.448 s. R2.8 referencia aproximada: warm 150 s, refresh 230 s, off 532 s. Contexto distinto de I/O y creación/reuso de productos; sin atribuir causalidad ni exigir igualdad de wall. No recalibración ni cambio de ratio.

- warm_1: extracción 0.204 s; hits 8064; write-skip ledger 954; resolvers globales medidos.
- warm_2: extracción 0.227 s; hits 8064; write-skip ledger 954; resolvers globales medidos.
- refresh: extracción 75.275 s; hits 0; write-skip ledger 954; resolvers globales medidos.
- verify_hash: extracción 0.286 s; hits 8064; write-skip ledger 954; resolvers globales medidos.
- external_warm: extracción 0.209 s; hits 8064; write-skip ledger 954; resolvers globales medidos.

Warm medio 198.055 s: ahorro frente a refresh 39.0 %. Hits, extracción y write-skip mantienen la ventaja; sin alerta de regresión funcional/performance sustancial e inexplicada. Variación wall frente a rondas anteriores registrada sin causa aislada.

Seguridad empírica: 6 documentos de métricas sin rutas absolutas ni cambios al sanear; 512 shards internos/externos idempotentes bajo sanitizador central. Tests con secretos sintéticos verifican bypass y ausencia en persistencia/diagnósticos.

## 14. Tests dirigidos

```text
python -X utf8 -m unittest tests.test_v5_3_r3_verification tests.test_v5_3_r2_9_incremental_calibration tests.test_v5_3_r2_8_cache_cli_controls.ExternalCacheDirTests tests.test_v5_3_r2_8_cache_cli_controls.ModeMatrixTests.test_repository_mismatch_falls_back_to_full tests.test_v5_3_r2_5_extraction_cache.StoreAndSafetyTests tests.test_v5_3_r2_7_scope_and_run_metrics
```

Mismo conjunto ejecutado mediante runner local para conservar la matriz y un footer seguro; duración 85.611 s.

83 tests; failures=0, errors=0, skips=0; PASS. Cuatro tests nuevos para huecos: matriz recuperación+equivalencia+autocura, interrupción con recuperación, junction real y diagnóstico de corrupción sin dump de secreto sintético. Casos internos de matriz no inflan el conteo unittest. Error inicial del test nuevo: literal VERIFY_FAILED corregido al código contractual VERIFY_CACHE_FAILED; no defecto runtime.

## 15. Suite completa

`python -X utf8 -m unittest discover -s tests`: 2838 tests, 0 fallas, 0 errores, 132 skips; 728.365 s unittest, 735.653 s wall; exit 0. Skips comparados con baseline esperada 132; junction nuevo ejecutado, sin skip de entorno.

Primera suite: 2838 tests, 2 fallas, 0 errores, 132 skips, 657.855 s. Ambas fallas históricas V4 estaban causadas por el cambio local de readiness a IN_PROGRESS; sus tests y builder esperan READY como disponibilidad técnica global. R2.9 había dejado READY_FOR_REVIEW después de su suite. Se regularizó solo PROJECT_STATE: readiness=READY; avance/revisión de ronda se mantienen en round_status/human_review. Sin cambio runtime, baseline V4 ni tests históricos. Grupo V4 completo revalidado: 45 PASS (0.330 s); cuatro tests R3 revalidados: PASS (18.491 s). La segunda suite completa es el resultado final indicado arriba.

## 16. Corridas IST ejecutadas

Validación posterior a la metadata final: grupo histórico V4, 45 tests PASS en 0.455 s; auditoría final de fuente oficial/inventario, 15138 archivos sin cambios.

Siete procesos: off_reference, auto_cold, warm_1, warm_2, refresh, verify_hash y external_warm, en ese orden y sin pipelines concurrentes. --long-paths, sin --trust-mtime/--allow-ai-interpretation/threshold. Cold cache interna recreada de forma acotada; preparación, snapshot/comparación y copia de cache fuera del wall de pipeline. Fixtures cubren recuperación evitando corridas IST redundantes.

## 17. Equivalencia

| Comparación | Archivos | Bytes ref/candidato | Added/removed/changed |
| --- | --- | --- | --- |
| auto_cold | 47524 | 2827997275/2827997275 | 0/0/0 |
| external_warm | 47524 | 2827997275/2827997275 | 0/0/0 |
| off_vs_previous_refresh | 47524 | 2827997275/2827997275 | 0/0/0 |
| refresh | 47524 | 2827997275/2827997275 | 0/0/0 |
| verify_hash | 47524 | 2827997275/2827997275 | 0/0/0 |
| warm_1 | 47524 | 2827997275/2827997275 | 0/0/0 |
| warm_2 | 47524 | 2827997275/2827997275 | 0/0/0 |

Exclusiones exactas aprobadas: `_cache_v53/`, root `RUN_SUMMARY.json`, root `RUN_SUMMARY.md`, `index/repository.json`. Ninguna ampliación. Comparador de R2.9 sin modificaciones; errores de lectura nunca equivalen a igualdad.

## 18. Deuda final

| Elemento | Clase | Estado |
| --- | --- | --- |
| Corrección/equivalencia/fallback | BLOCKING | Ninguna observada |
| Revisión humana R3 y cierre formal R4 | CLOSURE_REQUIRED | Pendientes |
| Junction/reparse real | OBSERVATION | PASS; entorno Windows actual |
| full_pipeline.py VERY_HIGH; dos atomic writers | FUTURE_PHASE | Refactor/unificación en ronda propia |
| artifacts.json; recomputación parcial; flow/projection cache | FUTURE_PHASE | Diferidos por contrato |
| Scope conservador | OBSERVATION | No reduce cómputo global |
| repository.json no determinista | OBSERVATION | Exclusión contractual |
| Ratio default None | OBSERVATION | CHANGED_RATIO_DEFAULT_DEFERRED |
| trust-mtime opt-in | OBSERVATION | Inseguro documentado; default false |

## 19. PROJECT_STATE

latest_completed_round=V5.3-R3; latest_approved_round=V5.3-R2.9.1; revisión R3 PENDING; round_status=V5_3_R3_READY_FOR_HUMAN_REVIEW; next=V5.3-R4; verification COMPLETED; readiness global técnico=READY (contrato histórico), sin conceder aprobación R3. Defaults y ratio diferido preservados; V5.3 closed=false/tag=null. Contadores históricos AI de fases anteriores conservados; contadores propios R3=0.

## 20. Continuidad

Actualizados solo estado vigente y ledger de los dos documentos de continuidad; aprobación R2.9/R2.9.1 regularizada y R3 registrada. Estados históricos e informes anteriores preservados. R4 no ejecutada ni aprobación R3 inferida.

## 21. Git

HEAD aa7db0db6c77d7ec8a1b15f50e33bf176d948bcd; rama main; ahead local origin/main=6; backup 2cb317fe5ae3dd2cbad1f865b1faee4a50a99569. Solo consultas; sin staging, commit, push, tag, amend, rebase, clean o reset. Pendiente previo R2.9.1 preservado.

Estado final de archivos:

```text
 M PROJECT_STATE.json
 M docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md
 M docs/continuity/LEGACYMAPPER_V5_ROADMAP.md
?? docs/V5/V5_3_R2_9_1_GIT_CHECKPOINT.md
?? docs/V5/V5_3_R3_VERIFICATION_REAL_REGRESSION.md
?? prompts/V5/V5_3_R3_VERIFICATION_REAL_REGRESSION.md
?? tests/test_v5_3_r3_verification.py
```

`git diff --check`: PASS; outputs locales ignorados; sin diff runtime ni modificación de informes históricos.

## 22. Recomendación R4

Revisar humanamente este resultado; autorizar R4 por instrucción explícita para cierre documental/contractual y posterior versionado según autorización propia. No convertir deuda FUTURE_PHASE en bloqueo sin evidencia.

## 23. Estado final

`V5_3_R3_READY_FOR_HUMAN_REVIEW`. Verificación completa; V5.3 abierta, R4 pendiente.
