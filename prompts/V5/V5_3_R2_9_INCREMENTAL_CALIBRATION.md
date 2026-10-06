# LegacyMapper V5.3 — R2.9 Calibración Final del Motor Incremental

## 1. Objetivo

Cerrar la implementación R2 de V5.3 con evidencia empírica suficiente para fijar decisiones operativas finales antes de entrar a R3.

Esta ronda debe:
1. construir/usar un comparador reproducible `full vs incremental`;
2. medir el punto de equilibrio de `--incremental-max-changed-ratio`;
3. decidir el default recomendado del ratio;
4. decidir el default final de `--cache-mode`;
5. medir directamente `verify_seconds`;
6. confirmar equivalencia de outputs;
7. actualizar continuidad (`PROJECT_STATE.json` y documentos equivalentes necesarios) al estado real de V5.3;
8. dejar preparado el paso a R3 de verificación/regresión.

NO iniciar R3.

## 2. Fuente de autoridad

Leer antes de modificar:
- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `docs/V5/V5_3_R2_7_SCOPE_ANALYSIS_AND_RUN_METRICS.md`
- `docs/V5/V5_3_R2_8_CACHE_CLI_CONTROLS.md`
- `docs/V5/V5_3_R2_8_1_VERIFY_CACHE_BARE_FIX.md`
- `docs/V5/V5_3_R2_8_2_GIT_CHECKPOINT.md`
- `PROJECT_STATE.json`
- documentos de continuidad/roadmap vigentes
- `AGENTS.md`
- `CLAUDE.md`

Regla: **R1 manda.** R2.9 mide y fija defaults; no redefine el contrato.

## 3. Estado de partida

Checkpoint funcional actual:

`c5f70143193b55713e3ca3d67bffaa7d997c9227`

R2.8/R2.8.1 ya aportan:
- `--cache-mode {auto,off,refresh}`;
- `--cache-dir`;
- `--verify-cache[=fast|hash]`;
- `--trust-mtime`;
- `--incremental-max-changed-ratio`;
- métricas persistidas;
- scope conservador;
- extraction cache;
- write-skip;
- fallback seguro.

Datos relevantes:
- warm IST ~150 s;
- off/full ~532 s;
- auto cold ~557 s;
- refresh ~230 s;
- changed ratio probado funcionalmente;
- `trust-mtime` ahorra ~4.8 s en File State pero es opt-in inseguro;
- ratio aún sin default;
- default `cache-mode=auto` aún pendiente de decisión final;
- `verify_seconds` existe en métricas pero faltó medición IST directa;
- `PROJECT_STATE.json` sigue atrasado.

Pendiente sin versionar esperado:
`docs/V5/V5_3_R2_8_2_GIT_CHECKPOINT.md`

## 4. Comparador full vs incremental

Crear o consolidar una herramienta reproducible para comparar:
- referencia full/off;
- incremental/auto;
- refresh;
- variantes con cambio controlado.

Debe verificar:
- conteo de archivos;
- tamaño total;
- SHA-256 por archivo;
- diferencias añadidas/eliminadas/modificadas;
- exclusiones explícitas de no deterministas.

No usar timestamps como criterio de equivalencia.

Preferir:
`tools/v5_3_compare_full_incremental.py`
o equivalente coherente con el repo.

No convertirlo en dependencia runtime.

## 5. Exclusiones

Documentar explícitamente cualquier exclusión necesaria.

Esperadas:
- `_cache_v53/`;
- `RUN_SUMMARY.*`;
- `index/repository.json`;
- cualquier otra ya declarada no determinista en R2.6/R2.7/R2.8.

No ampliar exclusiones para ocultar diferencias.

Toda nueva diferencia no justificada:
`V5_3_R2_9_BLOCKED`

## 6. Salida del comparador

Debe producir resumen legible y machine-readable, por ejemplo:
- exit 0 = equivalente;
- exit no-cero = divergencia;
- JSON pequeño opcional fuera de outputs canónicos.

Debe incluir:
- files_compared;
- equal;
- added;
- removed;
- changed;
- excluded;
- total_bytes;
- duration.

No persistir contenido completo de archivos.

## 7. Punto de equilibrio del changed ratio

Usar copia controlada de IST. No modificar IST oficial.

Preparar varios niveles de cambio sobre archivos analizados, preferentemente `.vb` distribuidos entre proyectos.

Mínimo:
- 0 %
- ~0.1 %
- ~0.5 %
- ~1 %
- ~2 %
- ~5 %
- ~10 %
- ~25 %
- ~50 %
- ~100 %

Si el coste operativo lo hace excesivo, puede ajustarse la rejilla tras una primera tanda, pero debe cubrir:
- zona claramente incremental;
- transición;
- zona claramente full.

## 8. Qué medir por nivel

Para cada ratio real:

### Incremental sin threshold
- total pipeline seconds;
- extraction seconds;
- cache hits;
- cache misses;
- shards rewritten;
- File State seconds;
- write-skip;
- outputs equivalentes.

### Full/off o refresh equivalente
- total pipeline seconds;
- extraction seconds;
- outputs equivalentes.

### Derivados
- ahorro absoluto;
- ahorro porcentual;
- coste incremental extra por miss;
- punto donde full pasa a ser igual o más barato.

Registrar al menos 2 repeticiones cerca del punto de cruce si el ruido es alto.

## 9. Cambios representativos

No usar solo cambios triviales de un mismo archivo.

Preferir selección distribuida entre proyectos para evitar sesgo.

Mantener determinismo de selección:
- lista fija;
- seed fija si se usa selección pseudoaleatoria;
- documentar archivos elegidos o algoritmo.

No introducir cambios semánticos que rompan parsing intencionalmente.

## 10. Fórmula del ratio

Usar exactamente la fórmula vigente:

`(modified + added + deleted) / previous_file_count`

salvo que R1 defina otra.

Rename sigue contando como added + deleted si ese es el contrato vigente.

## 11. Decisión del default del ratio

No elegir exactamente el punto de cruce si hay mucho ruido.

Preferir margen conservador.

La decisión debe justificar:
- rendimiento;
- estabilidad;
- coste de falsos positivos;
- seguridad;
- facilidad de entender.

Si la evidencia no permite fijar un valor estable:
mantener `None` y declarar:

`CHANGED_RATIO_DEFAULT_DEFERRED`

Eso es preferible a inventar un threshold.

## 12. Default de cache mode

R1 permitía `off` hasta cierre y `auto` una vez validado.

Evaluar:
- fallback seguro;
- corrupción;
- version mismatch;
- repo mismatch;
- extraction schema mismatch;
- external cache-dir;
- refresh;
- verify;
- equivalencia full;
- estabilidad en IST.

Si todo sigue verde, documentar formalmente si:
`cache-mode=auto`
queda aprobado como default V5.3.

No cambiarlo silenciosamente.

## 13. verify_seconds

Usar el campo:
`cache_controls.verify_seconds`

Medir sobre IST warm:
- `verify=fast`;
- `verify=hash`.

Mínimo 3 repeticiones de cada una si el coste total es razonable.

Registrar:
- verify_seconds;
- total_seconds;
- variación;
- tamaño de cache;
- número de shards.

Separar tiempo directo de verify de variación total de la corrida.

## 14. Matriz mínima final IST

Validar:
- A. auto cold
- B. auto warm
- C. off
- D. refresh
- E. verify fast
- F. verify hash
- G. changed ratio debajo del default candidato
- H. changed ratio encima del default candidato
- I. cache externa

No repetir escenarios innecesarios si ya existe salida reciente reutilizable y verificable, pero toda decisión nueva debe tener evidencia actual.

## 15. Equivalencia

Usar el comparador de R2.9.

Para cada variante relevante:
- 0 diferencias deterministas vs referencia full/off.

La variante `trust-mtime` con mtime manipulado queda fuera de equivalencia obligatoria porque es opt-in inseguro ya documentado.

No usar `trust-mtime` para fijar defaults.

## 16. Tests del comparador

Cubrir:
1. árboles iguales;
2. archivo cambiado;
3. añadido;
4. eliminado;
5. exclusiones;
6. archivo grande;
7. mismo tamaño/diferentes bytes;
8. orden determinista;
9. error de lectura;
10. exit code.

## 17. Tests de defaults

Añadir/ajustar tests para la decisión final:
- `cache-mode` default;
- changed ratio default si se fija;
- verify default sigue `fast`;
- trust-mtime sigue false.

Si changed ratio se mantiene desactivado:
test explícito.

## 18. Suite completa

Ejecutar:
`python -m unittest discover -s tests`

Registrar:
- total;
- fallas;
- errores;
- skips;
- duración.

Criterio:
0 fallas, 0 errores.

## 19. PROJECT_STATE.json

Actualizar al estado real de V5.3.

Mínimo esperado:
- current_version: V5.3;
- status: V5_3_IN_PROGRESS;
- latest_completed_round: R2.8.2 o R2.9 según convención;
- latest_approved_round: actualizar si existe campo apropiado;
- next_round: V5.3-R3;
- tests: total actualizado;
- extraction cache: ADOPTED;
- cache CLI controls: implemented;
- scope analysis: implemented/conservative;
- run metrics: implemented;
- R2 complete: true si R2.9 queda aprobado técnicamente;
- V5.3 closed: false.

No declarar V5.3 cerrada.

## 20. Continuity docs

Actualizar solo los documentos de continuidad que estén claramente obsoletos.

Preservar secciones históricas.

No reescribir historia.

Registrar:
- R2.6;
- R2.7;
- R2.8;
- R2.8.1;
- R2.8.2;
- R2.9.

## 21. Deuda técnica

Clasificar:
- BLOCKING;
- CURRENT_PHASE;
- NEXT_ROUND;
- FUTURE_PHASE;
- OBSERVATION.

Revisar especialmente:
- `full_pipeline.py` VERY_HIGH;
- `artifacts.json` diferido;
- scope para código sigue full/unassertable;
- no partial resolver recomputation;
- no projection cache;
- `trust-mtime` inseguro opt-in;
- cache external symlink/reparse no probado;
- two atomic write implementations;
- `repository.json` no determinista;
- ratio default;
- verify hash overhead.

## 22. Git

Solo consultas.

NO:
- commit;
- push;
- tag;
- amend;
- rebase.

Registrar:
- rama;
- HEAD;
- commits ahead;
- backup branch;
- archivos modificados/nuevos;
- `docs/V5/V5_3_R2_8_2_GIT_CHECKPOINT.md` pendiente.

## 23. Fuera de alcance

NO:
- iniciar R3;
- partial resolver recomputation;
- stage skipping;
- cache de flows;
- projection cache;
- `artifacts.json`;
- nuevos scope modes;
- cambios Evidence Core;
- cambios IDs;
- IA;
- push/tag.

R2.9 calibra y verifica; no abre una nueva arquitectura incremental.

## 24. Entregable

Crear:
`docs/V5/V5_3_R2_9_INCREMENTAL_CALIBRATION.md`

Debe incluir:
1. Objetivo.
2. Estado de partida.
3. Contrato R1 relevante.
4. Comparador full vs incremental.
5. Archivos modificados.
6. Tests del comparador.
7. Diseño experimental changed ratio.
8. Tabla completa de ratios.
9. Punto de equilibrio observado.
10. Decisión de default ratio.
11. Decisión de default cache-mode.
12. verify_seconds fast/hash.
13. Matriz final IST.
14. Equivalencia.
15. Suite completa.
16. Rendimiento.
17. Seguridad.
18. Mantenibilidad.
19. Deuda técnica.
20. PROJECT_STATE actualizado.
21. Continuidad actualizada.
22. Estado Git.
23. Recomendación para R3.
24. Estado final.

## 25. Estados finales permitidos

Si calibración y defaults quedan suficientemente sustentados:
`V5_3_R2_9_READY_FOR_REVIEW`

Si el ratio no permite fijar default estable pero todo lo demás pasa:
`V5_3_R2_9_READY_FOR_REVIEW`
+
`CHANGED_RATIO_DEFAULT_DEFERRED`

Si hay divergencias full/incremental, regresiones o tests fallidos:
`V5_3_R2_9_BLOCKED`

## 26. Criterio de cierre

R2.9 está lista si:
- comparador reproducible existe;
- full vs incremental equivalen;
- punto de equilibrio fue medido;
- ratio default fue fijado o diferido justificadamente;
- cache-mode default quedó decidido;
- verify_seconds fue medido directamente;
- suite completa verde;
- continuidad refleja el estado real;
- no se amplió alcance;
- R3 puede comenzar con una baseline estable.

Detenerse para revisión humana.
