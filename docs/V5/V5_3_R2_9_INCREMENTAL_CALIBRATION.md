# V5.3 R2.9 — Calibración incremental final

Fecha: 2026-10-06. Evidencia machine-readable: [resultado JSON](V5_3_R2_9_INCREMENTAL_CALIBRATION.json).

## 1. Objetivo

Calibrar R2 sin redefinir R1. Resultado: `V5_3_R2_9_READY_FOR_REVIEW` + `CHANGED_RATIO_DEFAULT_DEFERRED`. Revisión humana pendiente; R3 no iniciada.

## 2. Estado de partida

Checkpoint funcional `c5f70143193b55713e3ca3d67bffaa7d997c9227`; main, 5 commits ahead de origin/main local. R2.8/R2.8.1 implementados; checkpoint R2.8.2 pendiente de versionar. PROJECT_STATE atrasado en R2.5.1 al inicio; actualizado a la evidencia actual. Se leyeron AGENTS, CLAUDE, R1, R2.7, R2.8, R2.8.1, R2.8.2 y continuidad.

## 3. Contrato R1

Cache opcional; salida canónica independiente de su presencia. SHA-256 de entrada seguro por defecto; compatibilidad/versiones/repo/esquema y corrupción fuerzan fallback/reextracción. Resolver global completo; scope observacional. Preservados confirmed/inferred/unresolved, reglas de IDs, Evidence Core y fingerprints. Ratio exacto: `(modified + added + deleted) / previous_file_count`; rename = added + deleted. No se redefine el denominador.

## 4. Comparador reproducible

`tools/v5_3_compare_full_incremental.py`: conteos, bytes totales y SHA-256 de cada archivo; streaming 1 MiB, 8 lectores, orden estable. Exit 0 equivalente, 1 divergencia, 2 error; JSON opcional fuera de ambos árboles. Error de lectura nunca equivale a igualdad; no timestamps ni contenido de archivos en el resumen. Exclusiones exactas: `_cache_v53/`, `RUN_SUMMARY.json`, `RUN_SUMMARY.md`, `index/repository.json`. Ninguna ampliación.

```text
python -m tools.v5_3_compare_full_incremental output/v53r29/f output/v53r29/i --json docs/V5/comparison.json
```

## 5. Archivos modificados/nuevos

Nuevos: comparador, `tools/v5_3_r2_9_calibrate.py`, `tests/test_v5_3_r2_9_incremental_calibration.py`, este resultado y su [JSON compacto](V5_3_R2_9_INCREMENTAL_CALIBRATION.json). Modificados: `.gitignore` (solo `/output/v53r29/`), PROJECT_STATE y dos documentos de continuidad. Sin cambios en módulos runtime/contratos/templates. Copia, productos y telemetría locales ignorados en Git; todos los nuevos reportes en docs/V5 por instrucción del usuario.

## 6. Tests del comparador y defaults

19 tests nuevos PASS: 13 comparador (igual, cambiado, añadido, eliminado, exclusiones exactas/directorios homónimos, grande, mismo tamaño/distintos bytes, orden, lectura fallida, directorio ausente, CLI/exit, JSON externo, no contenido secreto); 3 defaults (auto, None explícito en CLI/CacheOptions/API, fast/mtime false); 3 seguridad de mutación (fuente intacta/restauración, límites de ruta, BOM UTF-16). Dirigidos: 19, 0 fallas, 0 errores, 0 skips, 0.814 s; incluidos en suite completa.

## 7. Diseño experimental

Copia de IST oficial en `output/v53r29/r`: 15138 archivos, 8106 analizados. VB primero; después otros analizados; inventario al final. Round-robin por directorio de proyecto más próximo, desempate lexical; proxy geográfico de muestreo, sin afirmar ownership. Lista fija/huellas originales en PLAN.json local. Comentario válido al inicio de VB (preserva BOM UTF-8/UTF-16 y desplaza líneas), comentarios válidos para markup/config/proyectos/soluciones. Cambios independientes desde bytes originales, sin acumulación; originales solo lectura. 100 % incluye estrés de inventario no extraído: máximo solo analizados = 53.55 % del denominador.

Cada auto sin threshold restaura la misma cache original (previous_file_count=15138); refresh extrae todo sobre el otro árbol. Ambos productos parten del mismo estado del nivel anterior; no ejecutar refresh sobre la salida recién actualizada de auto. Preparación/copia/mutación/comparación fuera de wall de pipeline. Primera tanda 28.12 min; diez niveles proyectados 93.73 min sin preparación. Adaptación autorizada por §7, para reservar repeticiones de zona alta. No pipeline simultáneos; no trust-mtime. 33 corridas manuales.

## 8. Tabla completa de ratios

Segundos; NA = no capturado/no medido. Pipeline = RUN_METRICS.total_seconds; wall incluye arranque/imports y finalización. El JSON conserva también duración CLI instrumentada cuando disponible. Full = refresh equivalente; off inicial sin telemetría de etapas no se usa como proxy inventado.

| Nominal % | Real %/estado | Modified | Auto wall | Full wall | Auto pipeline | Full pipeline | Ahorro s | Ahorro % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.0 | 0.0000 | 0 | 195.434 | 264.809 | 193.843 | 257.877 | 69.375 | 26.198 |
| 0.1 | 0.0991 | 15 | 186.367 | 270.276 | 183.533 | 263.653 | 83.909 | 31.046 |
| 0.5 | 0.5020 | 76 | 209.973 | 276.475 | 206.288 | 267.989 | 66.502 | 24.054 |
| 1.0 | NO_MEDIDO_ADAPTACION | NA | NA | NA | NA | NA | NA | NA |
| 2.0 | NO_MEDIDO_ADAPTACION | NA | NA | NA | NA | NA | NA | NA |
| 5.0 | NO_MEDIDO_ADAPTACION | NA | NA | NA | NA | NA | NA | NA |
| 10.0 | 10.0013 | 1514 | 343.140 | 404.355 | 337.341 | 398.080 | 61.215 | 15.139 |
| 25.0 | NO_MEDIDO_ADAPTACION | NA | NA | NA | NA | NA | NA | NA |
| 50.0 | 50.0000 | 7569 | 337.721 | 405.163 | 330.969 | 397.985 | 67.442 | 16.646 |
| 100.0 | 100.0000 | 15138 | 330.149 | 353.966 | 323.003 | 347.635 | 23.817 | 6.729 |

Added=deleted=0 en todos los niveles medidos.

| Nominal % | Extr auto | Extr full | Hits | Misses | Shards reescritos auto | File State auto | File State full | Auto escritos/skip | Full escritos/skip |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.0 | 0.264 | 63.308 | 8064 | 42 | 0 | 15.620 | 11.363 | 2/954 | 2/954 |
| 0.1 | 0.375 | 64.111 | 8049 | 57 | 15 | 15.671 | 10.734 | 11/945 | 11/945 |
| 0.5 | 0.812 | 63.528 | 7988 | 118 | 68 | 17.446 | 10.632 | 11/945 | 11/945 |
| 10.0 | 22.740 | 63.320 | 6553 | 1553 | 256 | 11.508 | 13.961 | 439/524 | 439/524 |
| 50.0 | 71.834 | 79.127 | 535 | 7571 | 256 | 13.955 | 14.431 | 396/564 | 396/564 |
| 100.0 | 86.491 | 73.090 | 0 | 8106 | 256 | 9.317 | 15.690 | 4/956 | 4/956 |

Full: hits=0, misses=8106, shards reescritos=256. Write-skip = ledger observable; no se presenta como censo de todos los archivos V5.2 (writer con manifest propio). Byte counters completos por corrida en JSON.

| Nominal % | Extra wall s/miss | Extra extracción s/miss |
| --- | --- | --- |
| 0.0 | NA | NA |
| 0.1 | -0.604467 | 0.007400 |
| 0.5 | 0.191303 | 0.007211 |
| 10.0 | 0.097754 | 0.014875 |
| 50.0 | 0.018899 | 0.009506 |
| 100.0 | 0.016706 | 0.010693 |

Derivados contra auto 0 %, dividido por misses adicionales (bypass basal=42). Pendiente descriptiva, no coste causal por archivo: mezcla tamaño/tipo, reescritura de productos y ruido; valores negativos por ruido no significan extracción gratuita.

## 9. Punto de equilibrio

No se observó full igual/más barato en los seis pares medidos ni en las dos repeticiones adicionales de 100 %. No interpolar un punto de cruce inexistente. 50 % de inventario dejó 535 hits; 100 % dejó 0. Extracción en 100 % inicial: auto 86.491 vs full 73.090 s; ahorro de pared dependió de otras etapas. La composición de archivos y el I/O impiden convertir conteo en umbral universal.

| Muestra 100 % | Orden | Auto wall | Full wall | Ahorro s | Extr auto | Extr full | Equiv |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | auto→refresh | 330.149 | 353.966 | 23.817 | 86.491 | 73.090 | PASS |
| 1 | auto→refresh | 275.888 | 307.459 | 31.571 | 65.886 | 63.638 | PASS |
| 2 | refresh→auto | 314.578 | 349.045 | 34.467 | 64.556 | 91.449 | PASS |

## 10. Default ratio

`None`, `CHANGED_RATIO_DEFAULT_DEFERRED`. No ventaja empírica estable de forzar full según esta rejilla; ruido y composición impiden fijar margen reproducible. Evita falsos positivos que fuerzan 8106 extracciones pese a cambios pequeños. Candidato funcional 0.005 probado G/H, descartado como default; no nace de un cruce medido. Control opt-in existente preservado.

## 11. Default cache-mode

`auto`: técnicamente validado como default V5.3, sujeto a revisión humana de R2.9. No cambio silencioso del código (ya era auto). Evidencia actual: cold/warm/off/refresh/verify/cache externa/G-H equivalentes; suite completa cubre corrupción, mismatch de versión/repo/esquema, regeneración y fallback seguro. Corrupción/mismatches se cubren con tests y evidencia previa R2.8, no se presentan como nuevos ensayos corruptos IST. Defaults restantes: verify=fast, trust-mtime=false.

## 12. Verify directo fast/hash

Misma copia controlada congelada en 76 modificaciones respecto al original; warm sin cambios entre repeticiones, hits=8064/misses=42, sin fallback. `cache_controls.verify_seconds` ausente en fast por contrato (no deep pass); NA, nunca cero medido.

| Verify | Rep | Verify directo s | Wall s | Pipeline s | Cache bytes | Shards | Equiv |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fast | 1 | NA | 188.447 | 187.047 | 267362776 | 256 | PASS |
| fast | 2 | NA | 177.062 | 174.581 | 267362776 | 256 | PASS |
| fast | 3 | NA | 168.515 | 166.226 | 267362778 | 256 | PASS |
| hash | 1 | 5.448 | 302.874 | 294.060 | 267362837 | 256 | PASS |
| hash | 2 | 3.065 | 181.383 | 179.018 | 267362835 | 256 | PASS |
| hash | 3 | 2.421 | 171.355 | 169.202 | 267362836 | 256 | PASS |

Hash directo: media 3.645, mediana 3.065, rango 2.421–5.448, desviación poblacional 1.302 s. Wall fast: media 178.008, mediana 177.062, rango 168.515–188.447, sd 8.165 s; hash: media 218.537, mediana 181.383, rango 171.355–302.874, sd 59.775 s. Primer hash: DOCUMENTATION 133.670 vs fast 53.232 s; File State 36.671 vs 16.675 s. No atribuir diferencia total a los 5.448 s directos de hash. Cache≈267.36 MB, 256 shards; bytes exactos/rango en tabla/JSON.

## 13. Matriz final IST

| Caso | Run | Session | Wall s | Extr s | Hits/misses | Equiv |
| --- | --- | --- | --- | --- | --- | --- |
| A inicial (timing) | A_auto_cold | cold | 799.007 | 72.170 | 0/8106 | SIN_SNAPSHOT |
| A proof | A_cold_proof | cold | 273.196 | 62.974 | 0/8106 | PASS |
| B | B_auto_warm | warm | 191.389 | 0.239 | 8064/42 | PASS |
| C | C_off | off | 668.418 | NA | NA | PASS |
| D | D_refresh | refresh | 279.444 | 63.168 | 0/8106 | PASS |
| E ×3 | verify_fast_1 | warm | 188.447 | 0.355 | 8064/42 | PASS |
| F ×3 | verify_hash_1 | warm | 302.874 | 0.777 | 8064/42 | PASS |
| G | G_below_candidate | warm | 501.958 | 0.437 | 8049/57 | PASS |
| H | H_above_candidate | fallback_full | 364.734 | 91.153 | 0/8106 | PASS |
| I cold | I_external_cold | cold | 223.993 | 62.678 | 0/8106 | PASS |
| I warm | I_external_warm | warm | 169.979 | 0.290 | 8064/42 | PASS |

A prueba cold independiente: cache interna eliminada de forma acotada, productos existentes; no se relabeló B como cold. Esta prueba cumple la fila A de equivalencia. A inicial aporta timing de creación de productos; sus bytes no se preservaron antes de B y no se declaran comparados. C off: etapas no capturadas; todas las referencias por nivel usan refresh medido. E/F tabla §12 contiene las tres repeticiones. G: ratio 15/15138=0.000991 <0.005, warm. H: 151/15138=0.009975 >0.005, fallback_full/CHANGED_RATIO_EXCEEDED. I external usa WORK/external_cache fuera de ambos árboles; cold y warm comparados separadamente.

## 14. Equivalencia

21 comparaciones PASS, 0 añadidos/eliminados/modificados frente a full equivalente. Referencia baseline off: 47.523 archivos, 2.827.992.237 bytes. Counts/bytes por variante:

| Comparación | Archivos | Bytes ref | Bytes auto | Added/removed/changed | Comparar s |
| --- | --- | --- | --- | --- | --- |
| G_below_candidate | 47523 | 2827992844 | 2827992844 | 0/0/0 | 146.125 |
| H_above_candidate | 47524 | 2827997275 | 2827997275 | 0/0/0 | 109.934 |
| baseline_auto_off | 47523 | 2827992237 | 2827992237 | 0/0/0 | 656.954 |
| baseline_cold_off | 47523 | 2827992237 | 2827992237 | 0/0/0 | 110.442 |
| baseline_refresh_off | 47523 | 2827992237 | 2827992237 | 0/0/0 | 121.299 |
| external_cold_off | 47523 | 2827992848 | 2827992848 | 0/0/0 | 82.907 |
| external_off | 47523 | 2827992848 | 2827992848 | 0/0/0 | 81.486 |
| ratio_0_0 | 47523 | 2827992237 | 2827992237 | 0/0/0 | 91.285 |
| ratio_0_001 | 47523 | 2827992844 | 2827992844 | 0/0/0 | 95.298 |
| ratio_0_005 | 47523 | 2827992848 | 2827992848 | 0/0/0 | 97.301 |
| ratio_0_1 | 47585 | 2828452536 | 2828452536 | 0/0/0 | 108.892 |
| ratio_0_5 | 47855 | 2838753350 | 2838753350 | 0/0/0 | 123.951 |
| ratio_1_0 | 47855 | 2838753587 | 2838753587 | 0/0/0 | 139.974 |
| repeat_1.0_1 | 47855 | 2838753602 | 2838753602 | 0/0/0 | 101.195 |
| repeat_1.0_2 | 47855 | 2838753602 | 2838753602 | 0/0/0 | 192.369 |
| verify_fast_1 | 47523 | 2827992848 | 2827992848 | 0/0/0 | 115.352 |
| verify_fast_2 | 47523 | 2827992848 | 2827992848 | 0/0/0 | 84.952 |
| verify_fast_3 | 47523 | 2827992848 | 2827992848 | 0/0/0 | 81.213 |
| verify_hash_1 | 47523 | 2827992848 | 2827992848 | 0/0/0 | 157.107 |
| verify_hash_2 | 47523 | 2827992848 | 2827992848 | 0/0/0 | 82.509 |
| verify_hash_3 | 47523 | 2827992848 | 2827992848 | 0/0/0 | 81.635 |

## 15. Suite completa

`python -X utf8 -m unittest discover -s tests`: 2834 tests, 0 fallas, 0 errores, 132 skips; duración unittest 650.53 s, wall 659.841 s; exit 0. Skips: conteo coincide con los 132 esperados por artefactos/baselines pesados opcionales ausentes en clon limpio; no skips nuevos en los 19 tests R2.9. Guard de proveedor real de tests conservado; tests AI usan fakes.

## 16. Rendimiento

Warm inicial: extracción 0.239 s vs refresh 63.168 s; 8064 archivos con extracción reutilizada, 42 bypass de sanitización. Auto cold inicial 799.007 vs off nuevo 668.418 s: coste inicial de cache/productos; no usar como coste de threshold. Cold proof existente 273.196 s. El I/O/documentación/proyecciones/global resolvers dominan conforme sube el cambio; wall y etapas reportados sin causalidad inventada. Cache externa warm 169.979 s. No garantía de speedup universal ni umbral transferible a otras composiciones.

## 17. Seguridad

Fuente oficial readonly: SHA-256 de 15138 archivos escaneados sin cambios; inventario igual, comprobado después de validación. Mutaciones/eliminación de cache guardadas por resolve estrictamente dentro de WORK; nunca SOURCE. Copia raw de entrada local ignorada en Git, no exportada como evidencia. Sanitizador central para JSON; sin contenido/logs crudos ni credenciales en reportes. Manual: AI solicitado/invocado=false; provider/real LLM=0 en esta ronda. Historial de pilot AI previo en PROJECT_STATE se preserva.

## 18. Mantenibilidad

Herramientas dev independientes, stdlib; runtime no las importa. Comparador reusable, arnés reanudable por evidencia guardada. No ejecutar baseline de nuevo sobre productos ya mutados: reanudación documentada usa la fase correcta. Reproducir desde WORK ausente o conservar PLAN/runs/estado coherentes. Código runtime, cache schema y fingerprints sin cambios. full_pipeline.py continúa VERY_HIGH; sin refactor de contrato por conveniencia.

Secuencia ejecutada (cada fase debe terminar exit 0 antes de la siguiente):

```text
python -m tools.v5_3_r2_9_calibrate baseline
python -m tools.v5_3_r2_9_calibrate cold-proof
python -m tools.v5_3_r2_9_calibrate grid --ratios 0,0.001,0.005
python -m tools.v5_3_r2_9_calibrate verify
python -m tools.v5_3_r2_9_calibrate grid --ratios 0.1,0.5,1
python -m tools.v5_3_r2_9_calibrate repeat-high --ratios 1
python -m tools.v5_3_r2_9_calibrate threshold
python -m unittest discover -s tests
python -m tools.v5_3_r2_9_calibrate audit
```

## 19. Deuda técnica

| Elemento | Clase | Decisión |
| --- | --- | --- |
| Divergencia/regresión | BLOCKING | Ninguna observada |
| Comparador/calibración/verify/defaults | CURRENT_PHASE | Entregados; ratio diferido explícitamente |
| Verificación R3 / junction-reparse real de cache externa | NEXT_ROUND | Pendiente; no probado realmente en Windows |
| full_pipeline.py VERY_HIGH | FUTURE_PHASE | Refactor en ronda propia; no bloquea esta calibración |
| artifacts.json | FUTURE_PHASE | ARTIFACT_STATE_DEFERRED_BY_CONTRACT; byte compare vigente |
| Scope código full/unassertable; sin partial resolver recomputation | FUTURE_PHASE | Conservador; sin autoridad para stage skipping |
| Projection/flow cache | FUTURE_PHASE | No implementada; fuera de alcance |
| Dos implementaciones atomic write | FUTURE_PHASE | Sin unificación que altere garantías aprobadas |
| trust-mtime | OBSERVATION | Opt-in inseguro, false por defecto; no usado para defaults |
| repository.json no determinista | OBSERVATION | Duración/ruta; exclusión previa explícita |
| Ratio default | OBSERVATION | None; diferido sin bloquear R2; futuras muestras si se reconsidera |
| Verify hash overhead / ruido | OBSERVATION | Mediana directa 3.065 s; total no equivale a coste de verify |

## 20. PROJECT_STATE

V5.3 IN_PROGRESS; latest_completed_round=V5.3-R2.9; latest_approved_round=V5.3-R2.8 (sin fabricar aprobación humana); round_status=READY_FOR_REVIEW; next=V5.3-R3 sujeto a revisión. Tests=2834, failures=errors=0, skips=132; extraction cache ADOPTED, CLI/scope/metrics IMPLEMENTED; R2 complete técnico=true; V5.3 closed=false; tag=null; revisión R2.9 PENDING. Defaults y evidencia enlazados.

## 21. Continuidad

Actualizados LEGACYMAPPER_V5_ROADMAP.md y LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md: cabecera vigente + ledger R2.6/R2.6.1, R2.7/R2.7.1, R2.8/R2.8.1/R2.8.2 y R2.9. Fotos históricas, fechas, cifras y secciones anteriores preservadas; no reescribir R2.8/R2.7 retroactivamente.

## 22. Git

Consultas locales exclusivamente: rama `main`, HEAD `c5f70143193b55713e3ca3d67bffaa7d997c9227`, ahead origin/main local=5; backup `backup/v5.3-pre-worktree-cleanup` → `2cb317fe5ae3dd2cbad1f865b1faee4a50a99569`. Sin fetch/commit/stage/push/tag/amend/rebase. `docs/V5/V5_3_R2_8_2_GIT_CHECKPOINT.md` sigue sin versionar; prompt actual también era untracked al inicio. Cambios R2.9 listados en §5; outputs pesados ignorados. `git diff --check`: PASS (solo avisos LF/CRLF preexistentes); archivos nuevos sin whitespace final.

## 23. Recomendación R3

Revisar humanamente este resultado y comenzar R3 solo por instrucción explícita. Baseline c5 + cambios dev actuales; defaults auto/None/fast/false. Priorizar regresión canónica, recuperación de cache inválida y límites de rutas reales; repetir en otra composición de cambios si se reconsidera ratio. No introducir partial resolvers/projection cache como parte implícita de R3.

## 24. Estado final

`V5_3_R2_9_READY_FOR_REVIEW`

`CHANGED_RATIO_DEFAULT_DEFERRED`

R2 completo técnicamente; revisión humana pendiente. V5.3 abierta; R3 no ejecutada. Sin bloqueo determinista observado.
