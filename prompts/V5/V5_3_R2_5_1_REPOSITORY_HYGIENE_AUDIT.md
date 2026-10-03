# LegacyMapper V5.3 — R2.5.1 Higiene, coherencia y obsolescencia del repositorio

## 1. Objetivo

Revisar el repositorio actual después de R2.5 para detectar:

- archivos desactualizados;
- archivos duplicados;
- archivos reemplazados por versiones más nuevas;
- referencias de estado contradictorias;
- temporales o artefactos de medición;
- documentación que ya no refleja el estado real;
- archivos candidatos a eliminación;
- archivos históricos que deben conservarse explícitamente.

Esta ronda es de auditoría y saneamiento.

NO implementar funcionalidad nueva.

## 2. Fuentes obligatorias

Leer antes de modificar:

- `docs/V5/V5_2_GIT_CLOSURE_RESULT.md`
- `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md`
- `docs/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md`
- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `docs/V5/V5_3_R2_1_SHARED_HYDRATION_VIEW.md`
- `docs/V5/V5_3_R2_2_WRITE_SKIP_AND_MAX_PATH.md`
- `docs/V5/V5_3_R2_2_1_MAINTAINABILITY_AND_FINAL_VALIDATION.md`
- `docs/V5/V5_3_R2_3_VERSIONING_AND_FINGERPRINTS.md`
- `docs/V5/V5_3_R2_4_CACHE_MANIFEST_AND_FILE_STATE.md`
- `docs/V5/V5_3_R2_5_EXTRACTION_CACHE.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

También revisar:

- `prompts/V5/`
- `prompts/V5_0/`
- `docs/V5/`
- `tests/`
- módulos añadidos en R2.1–R2.5
- archivos temporales o salidas residuales bajo `output/` si existen

## 3. Regla principal

NO borrar automáticamente ningún archivo cuya función histórica o contractual no esté 100 % clara.

Clasificar primero.

Cada archivo candidato debe terminar en una de estas categorías:

- `KEEP`
- `UPDATE`
- `DELETE_CANDIDATE`
- `HISTORICAL`
- `GENERATED_IGNORE`
- `NEEDS_HUMAN_DECISION`

Solo eliminar archivos clasificados como `DELETE_CANDIDATE` cuando la evidencia sea clara y la eliminación no rompa referencias, tests, runtime ni continuidad documental.

Si hay duda:

`NEEDS_HUMAN_DECISION`

## 4. Alcance

### A. Documentación V5

Buscar:

- estados antiguos que contradicen el estado real;
- referencias a Git pendientes ya resueltas;
- referencias a rondas inexistentes;
- referencias a rutas antiguas;
- decisiones reemplazadas por una ronda posterior;
- documentos que deberían marcarse explícitamente como históricos;
- duplicados exactos o casi exactos.

### B. Prompts

Comparar:

- `prompts/V5/`
- `prompts/V5_0/`

Detectar:

- prompts de V5.3 todavía duplicados en `V5_0`;
- prompts movidos pero no eliminados;
- nombres repetidos;
- versiones antiguas superadas;
- referencias internas desactualizadas.

La convención vigente desde V5.3 es:

`prompts/V5/`

Los prompts históricos anteriores no deben moverse ni borrarse solo por estar en `V5_0`.

### C. Código

Revisar módulos creados desde R2.1:

- `context/hydration_view.py`
- `documentation_v52/writer.py`
- `utils/path_limits.py`
- `versions.py`
- `fingerprints/`
- `cache/`

Buscar:

- módulos huérfanos;
- funciones nunca usadas;
- imports muertos;
- código duplicado;
- helpers reemplazados;
- constantes obsoletas;
- funciones antiguas que quedaron sin referencias tras refactors.

NO refactorizar en esta ronda salvo eliminación trivial y demostrablemente segura de código muerto.

### D. Tests

Buscar:

- tests que apuntan a rutas antiguas;
- tests duplicados por refactors;
- inventarios congelados con referencias obsoletas;
- tests que ya no validan el código actual;
- tests históricos que deben conservarse.

No eliminar tests solo porque sean antiguos.

### E. Output / temporales

Buscar:

- carpetas `_r2*`;
- scratch residual dentro del repo;
- `.tmp`;
- copias de código;
- mediciones;
- archivos de prueba accidentales.

Distinguir:

- generado ignorado;
- residual que debe eliminarse;
- fixture legítimo.

## 5. Coherencia de estado

Verificar explícitamente:

- V5.2 está cerrado y publicado;
- tag `v5.2`;
- HEAD actual;
- estado de V5.3;
- rondas completadas R0 → R2.5;
- ninguna referencia vigente debe indicar que V5.2 sigue pendiente de aprobación Git;
- `PROJECT_STATE.json` debe ser coherente con la realidad actual o documentar por qué todavía no se actualiza.

NO cambiar `PROJECT_STATE.json` automáticamente si la convención del proyecto indica actualizarlo solo en hitos concretos.

## 6. Referencias cruzadas

Buscar referencias a archivos que:

- ya no existen;
- fueron renombrados;
- cambiaron de carpeta;
- cambiaron de nombre;
- están en `prompts/V5_0/` cuando deberían apuntar a `prompts/V5/`.

Para cada referencia rota:

- corregir si es claramente vigente;
- conservar si es parte de una narración histórica y sigue siendo comprensible;
- documentar si requiere decisión humana.

## 7. Eliminación segura

Antes de eliminar un archivo:

1. comprobar referencias por nombre/ruta;
2. comprobar imports si es código;
3. comprobar tests;
4. comprobar documentación;
5. comprobar Git history/continuidad;
6. confirmar que existe un reemplazo si corresponde.

No borrar:

- documentos de cierre;
- contratos históricos;
- informes empíricos;
- prompts que formen parte de la trazabilidad de una ronda;
- fixtures usados por tests;
- archivos requeridos por runtime.

## 8. Duplicados

Detectar:

- contenido idéntico por hash;
- nombres iguales en carpetas distintas;
- documentos que parecen copias de versiones anteriores;
- módulos con lógica repetida.

Clasificar duplicados como:

- duplicado válido/histórico;
- duplicado accidental;
- reemplazado;
- necesita decisión.

No eliminar por similitud textual sin confirmar función.

## 9. Consistencia de nomenclatura

Revisar:

- nombres R2.2 vs R2.2.1;
- nombres de archivos;
- títulos internos;
- estados finales;
- rutas de prompts/docs;
- uso consistente de V5.3.

Corregir errores obvios de naming solo si no rompe referencias.

## 10. Git

Solo consultas.

NO commit, tag ni push.

Registrar:

- modificados;
- nuevos;
- eliminados si hubo saneamiento;
- sin versionar;
- ignorados relevantes;
- archivos residuales.

No tocar historial Git.

## 11. Tests

Si se modifica o elimina cualquier archivo que pueda afectar runtime/tests:

Ejecutar tests dirigidos.

Si se modifica código o tests:

Ejecutar suite completa:

`python -m unittest discover -s tests`

Si solo se corrige documentación/prompts y no hay cambios de runtime/tests:

la suite completa no es obligatoria, pero justificarlo.

## 12. Restricción de funcionalidad

NO:

- iniciar R2.6;
- cambiar extracción;
- cambiar caché;
- cambiar fingerprints;
- cambiar File State;
- cambiar manifests;
- cambiar IDs;
- cambiar Evidence Core;
- cambiar write-skip;
- cambiar CLI;
- ejecutar IA;
- hacer commit/push.

## 13. Entregable

Crear:

`docs/V5/V5_3_R2_5_1_REPOSITORY_HYGIENE_AUDIT.md`

Debe incluir:

1. Objetivo.
2. Alcance revisado.
3. Archivos `KEEP`.
4. Archivos `UPDATE`.
5. Archivos `DELETE_CANDIDATE`.
6. Archivos `HISTORICAL`.
7. Archivos `GENERATED_IGNORE`.
8. Archivos `NEEDS_HUMAN_DECISION`.
9. Duplicados encontrados.
10. Referencias rotas encontradas.
11. Referencias corregidas.
12. Archivos eliminados realmente.
13. Archivos actualizados realmente.
14. Código muerto/imports muertos encontrados.
15. Temporales/residuales encontrados.
16. Coherencia de Git/estado.
17. Tests ejecutados.
18. Riesgos.
19. Deuda técnica.
20. Estado Git.
21. Recomendación para continuar a R2.6.
22. Estado final.

## 14. Estados finales permitidos

Si la auditoría queda limpia y no hay decisiones humanas pendientes que bloqueen:

`V5_3_R2_5_1_READY_FOR_REVIEW`

Si existen candidatos ambiguos que podrían afectar continuidad/runtime:

`V5_3_R2_5_1_NEEDS_HUMAN_DECISION`

Si se detecta inconsistencia seria o riesgo de borrar/romper algo:

`V5_3_R2_5_1_BLOCKED`

No usar otro estado.

## 15. Criterio de cierre

La ronda está lista si:

- no quedan referencias vigentes claramente incorrectas;
- los duplicados accidentales están resueltos o clasificados;
- los temporales residuales están eliminados o clasificados;
- los históricos están explícitamente preservados;
- no se borró nada dudoso;
- el repositorio queda más coherente que antes;
- no se amplió alcance;
- existe una recomendación clara para R2.6.

Detenerse para revisión humana.
