# LegacyMapper V5.3 — R2.2.1 Saneamiento de mantenibilidad y validación final

## 1. Objetivo

Cerrar técnicamente R2.2 sin arrastrar deuda nueva de mantenibilidad.

Esta ronda debe hacer únicamente dos cosas:

1. extraer de `documentation_v52/engine.py` la lógica de escritura introducida en R2.2 hacia un módulo dedicado;
2. validar el código final exacto con tests y una corrida IST completa.

No añadir funcionalidad nueva.

## 2. Fuentes obligatorias

Leer antes de modificar:

- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `docs/V5/V5_3_R2_1_SHARED_HYDRATION_VIEW.md`
- `docs/V5/V5_3_R2_2_WRITE_SKIP_AND_MAX_PATH.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

## 3. Estado de partida

R2.2 terminó en:

`V5_3_R2_2_READY_FOR_REVIEW`

Hechos confirmados:

- `documentation_v52` en repetición sin cambios: 32,2 s;
- 0 documentos reescritos;
- 46.567 documentos omitidos;
- verificación estricta por contenido;
- salida byte-idéntica;
- `MAX_PATH` resuelto con preflight;
- `--long-paths` implementado;
- suite completa: 2.506 tests, 0 fallas, 0 errores;
- `documentation_v52/engine.py` quedó clasificado como riesgo `VERY_HIGH`;
- el último refactor mecánico del motor no fue validado con una corrida completa del pipeline.

## 4. Alcance permitido

Modificar únicamente lo necesario para:

### A. Extraer responsabilidad de escritura

Mover desde:

`legacy_documenter/documentation_v52/engine.py`

hacia un módulo dedicado, por ejemplo:

`legacy_documenter/documentation_v52/writer.py`

o nombre equivalente claramente justificado.

La extracción debe incluir únicamente responsabilidades de escritura, por ejemplo:

- verificación de documentos existentes;
- write-skip;
- escritura atómica de documentos;
- manifest final;
- limpieza de huérfanos;
- limpieza de directorios vacíos;
- contadores de escritura;
- coordinación de la fase de persistencia.

No mover lógica de render, selección de templates ni configuración salvo que sea estrictamente necesario para desacoplar la escritura.

### B. Mantener comportamiento idéntico

No cambiar:

- algoritmos;
- orden de efectos;
- nombres;
- rutas;
- encoding;
- line endings;
- manifest;
- contadores;
- mensajes;
- comportamiento MAX_PATH;
- comportamiento `--long-paths`;
- contratos públicos.

## 5. Restricción principal

Este trabajo es un refactor estructural.

La salida antes y después debe ser equivalente.

Si para extraer el módulo hay que cambiar comportamiento observable, detenerse y reportar.

## 6. Fuera de alcance

NO:

- iniciar R2.3;
- añadir fingerprints;
- añadir versiones;
- crear File State;
- crear `_cache_v53/`;
- implementar extraction cache;
- ampliar write-skip a otras salidas;
- cambiar MAX_PATH;
- cambiar `--long-paths`;
- cambiar IDs;
- cambiar Evidence Core;
- cambiar manifests;
- cambiar CLI salvo imports internos inevitables;
- ejecutar IA;
- modificar `PROJECT_STATE.json`;
- commit/push.

## 7. Mantenibilidad

Objetivo:

- reducir `engine.py`;
- separar render/orquestación de persistencia;
- evitar duplicación;
- mantener una sola dirección de dependencias;
- no introducir ciclos;
- no mover deuda de un módulo grande a otro módulo igualmente descontrolado.

Revisar el inventario histórico de mantenibilidad.

Si el nuevo módulo aparece como `HIGH` o superior:

- justificar;
- dividir solo si existe una separación natural de responsabilidad;
- no fragmentar artificialmente.

## 8. Tests dirigidos

Ejecutar al menos:

- `tests/test_v5_3_r2_2_write_skip_and_max_path.py`
- tests de `documentation_v52`
- tests de escritura atómica
- tests de CLI relacionados
- test histórico de mantenibilidad

Añadir tests nuevos solo si la extracción crea una superficie que no estaba cubierta.

No duplicar tests existentes sin necesidad.

## 9. Equivalencia antes/después

Comparar el comportamiento del código R2.2 previo al refactor contra el código final.

Debe coincidir:

- documentos generados;
- contenido byte a byte;
- `MANIFEST.json`;
- contadores;
- write-skip;
- huérfanos eliminados;
- errores MAX_PATH;
- comportamiento `--long-paths`.

Usar fixtures primero.

## 10. Suite completa

Ejecutar:

`python -m unittest discover -s tests`

Registrar:

- total;
- fallas;
- errores;
- skips;
- duración.

Debe quedar verde.

## 11. Corrida IST final obligatoria

Ejecutar una corrida completa sobre:

`C:\Users\cgalianj\source\IST_40\Operacional`

Sin IA.

Usar el código final exacto tras el refactor.

Después ejecutar una segunda corrida sobre la misma salida para validar write-skip.

Medir:

### Corrida A

- tiempo total;
- tiempo DOCUMENTATION;
- tiempo `documentation_v52`;
- documentos escritos;
- documentos omitidos;
- memoria pico.

### Corrida B

- tiempo total;
- tiempo DOCUMENTATION;
- tiempo `documentation_v52`;
- render;
- verificación;
- escritura;
- limpieza;
- manifest;
- documentos escritos;
- documentos omitidos;
- memoria pico.

## 12. Criterios de aceptación

Cerrar la ronda solo si:

1. `engine.py` baja de riesgo respecto a R2.2 o queda razonablemente reducido;
2. no aparece deuda equivalente injustificada en el módulo nuevo;
3. suite completa verde;
4. salida byte-idéntica;
5. write-skip sigue seguro;
6. repetición sin cambios mantiene `documentation_v52 <= 49 s`, salvo degradación externa claramente demostrada;
7. 0 documentos reescritos en repetición sin cambios;
8. `MAX_PATH` y `--long-paths` siguen funcionando;
9. no se amplió el alcance;
10. no se inició R2.3.

Si el tiempo supera 49 s por variación de antivirus/I/O:

- reportar valor;
- comparar con desglose;
- no falsear resultado;
- decidir estado según evidencia.

## 13. Deuda técnica

Clasificar cualquier hallazgo como:

- BLOCKING;
- CURRENT_PHASE;
- NEXT_ROUND;
- FUTURE_PHASE;
- OBSERVATION.

Prestar atención a:

- tamaño final de `engine.py`;
- tamaño del nuevo módulo;
- ciclos;
- duplicación;
- API pública innecesaria;
- dependencias cruzadas;
- tests congelados de mantenibilidad.

## 14. Git

Solo consultas.

No commit, tag ni push.

Registrar:

- archivos modificados;
- archivos nuevos;
- pendientes administrativos anteriores.

## 15. Entregable

Crear:

`docs/V5/V5_3_R2_2_1_MAINTAINABILITY_AND_FINAL_VALIDATION.md`

Debe incluir:

1. Objetivo.
2. Refactor realizado.
3. Archivos modificados.
4. Responsabilidades antes/después.
5. Tamaño y clasificación de mantenibilidad.
6. Dependencias/ciclos.
7. Tests dirigidos.
8. Suite completa.
9. Equivalencia.
10. Corrida IST A.
11. Corrida IST B.
12. Write-skip final.
13. MAX_PATH / long paths.
14. Deuda técnica.
15. Riesgos.
16. Fuera de alcance confirmado.
17. Estado Git.
18. Estado final.

## 16. Estados finales permitidos

Si todo cumple:

`V5_3_R2_2_1_READY_FOR_REVIEW`

Si hay regresión, deuda equivalente no razonable, tests fallidos o diferencia de salida:

`V5_3_R2_2_1_BLOCKED`

No usar otro estado.

## 17. Restricciones finales

No:

- iniciar R2.3;
- hacer commit;
- hacer push;
- tocar Evidence Core;
- cambiar IDs;
- ampliar write-skip;
- añadir caché persistida;
- añadir fingerprints;
- ejecutar IA.

Detenerse para revisión humana.
