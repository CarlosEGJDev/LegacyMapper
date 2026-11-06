# LegacyMapper V5.3 — R2.2 Write-skip de documentation_v52 y MAX_PATH

## 1. Objetivo

Implementar únicamente las dos decisiones de V5.3 R1 asignadas a R2.2:

1. evitar reescribir archivos idénticos de `documentation_v52`;
2. detectar y manejar correctamente rutas demasiado largas en Windows antes de escribir.

Esta ronda NO implementa la caché persistida general de V5.3.

## 2. Fuentes obligatorias

Leer antes de modificar código:

- `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md`
- `docs/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md`
- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `docs/V5/V5_3_R2_1_SHARED_HYDRATION_VIEW.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

Decisiones contractuales relevantes de R1:

- §6.E — Projection Cache / write-skip por contenido;
- §14 — MAX_PATH;
- §12 — equivalencia incremental/full;
- §20 — seguridad y consistencia;
- §21 — plan R2.2.

## 3. Estado de partida

R2.1 está aprobado.

Medición vigente sobre IST:

- corrida completa nueva: ≈ 632–642 s;
- `documentation_v52`: ≈ 407–469 s;
- generación/render en memoria de 46.567 documentos: ≈ 9,3 s;
- el cuello actual es mayoritariamente escritura a disco;
- salida R2.1 es equivalente a la anterior.

Baseline oficial IST:

`C:\Users\cgalianj\source\IST_40\Operacional`

No modificar el repositorio IST.

## 4. Alcance permitido

Modificar solo lo necesario para:

### A. Write-skip de `documentation_v52`

- generar el contenido exactamente como hoy;
- calcular su SHA-256 determinista;
- comparar contra el estado anterior confiable;
- si el archivo ya contiene el resultado correcto, no volver a escribirlo;
- si falta o difiere, escribirlo con el mecanismo seguro existente;
- eliminar huérfanos como hoy;
- mantener `MANIFEST.json` lógicamente idéntico al que produciría una corrida completa.

### B. Preflight de rutas Windows

Antes de escribir:

- calcular las rutas finales que va a producir el stage;
- detectar si alguna excederá el límite práctico de Windows, incluyendo el nombre temporal usado por escritura atómica;
- abortar antes de escribir parcialmente el stage;
- entregar error claro y accionable.

### C. Soporte opt-in de rutas largas

Implementar únicamente si puede hacerse sin romper contratos existentes:

`--long-paths`

Debe permitir usar rutas extendidas de Windows dentro de LegacyMapper sin cambiar:

- slugs;
- rutas relativas del manifest;
- enlaces;
- nombres visibles de documentos.

## 5. Fuera de alcance

NO implementar:

- `_cache_v53/`;
- `CACHE_MANIFEST.json`;
- `file_state.json`;
- extraction cache;
- fingerprints de analizador;
- `ANALYZER_VERSION`;
- `CONFIG_FINGERPRINT`;
- cache de flows hidratados;
- write-skip de `index/`, Evidence Core, `consumer_projection`, `ai_context` o documentación legacy;
- scopes incrementales;
- invalidación;
- cambios de IDs;
- cambios de Evidence Core;
- cambios de `CallResolver`;
- SQLite/JSONL;
- IA;
- R2.3.

## 6. Restricción crítica de compatibilidad

NO cambiar el esquema contractual existente de:

`documentation_v52/MANIFEST.json`

solo para guardar datos auxiliares como `mtime`.

El manifest debe seguir representando la misma salida lógica que antes.

No introducir campos no contractuales en artefactos V5.2 estables.

Si para un modo rápido hace falta estado auxiliar persistente que equivalga a una caché nueva, NO crearlo en esta ronda.

## 7. Política segura de write-skip

La prioridad es:

`correctitud > rendimiento`

Nunca omitir una escritura si no existe evidencia suficiente de que el archivo en disco ya contiene exactamente el resultado esperado.

### Fuente disponible

`documentation_v52/MANIFEST.json` ya contiene por documento:

- ruta;
- tamaño;
- SHA-256.

Usarlo como fuente de comparación del resultado anterior.

### Regla obligatoria

Antes de implementar el modo rápido, determinar si puede demostrarse de forma segura usando solo:

- manifest existente;
- metadatos del archivo;
- estado actual del disco;

sin crear una nueva caché persistente ni modificar el esquema del manifest.

Si NO puede demostrarse con seguridad:

- implementar primero un modo estricto basado en hash real del archivo existente;
- medir su coste;
- documentar por qué el modo `fast` debe esperar a R2.4 (File State / cache manifest);
- NO inventar una heurística insegura.

Si SÍ puede demostrarse:

- documentar formalmente la condición;
- añadir tests de edición externa, mismo tamaño, cambio de mtime y corrupción.

No confiar únicamente en `size` para asumir identidad.

## 8. Flujo esperado de escritura

Para cada documento generado:

1. renderizar contenido en memoria;
2. calcular bytes exactos que se escribirían;
3. calcular SHA-256;
4. consultar el manifest anterior;
5. verificar de forma segura el archivo existente;
6. si coincide:
   - no ejecutar `mkstemp`;
   - no ejecutar `fsync`;
   - no ejecutar `os.replace`;
   - contar `skipped_write`;
7. si no coincide:
   - usar la escritura atómica existente;
8. construir el nuevo `MANIFEST.json` exactamente desde la salida actual;
9. eliminar huérfanos;
10. escribir el manifest al final.

No cambiar line endings ni encoding.

## 9. Contadores mínimos

Añadir instrumentación de bajo coste para R2.2, sin introducir todavía `RUN_METRICS.json` general.

Registrar en log o resultado interno de stage:

- `documents_total`;
- `documents_written`;
- `documents_skipped_write`;
- `documents_missing`;
- `documents_changed`;
- `documents_verified`;
- `verification_mode`;
- tiempo de:
  - render;
  - verificación;
  - escritura;
  - limpieza de huérfanos;
  - manifest;
  - total v52.

No modificar `RUN_SUMMARY` si rompe su contrato.

## 10. MAX_PATH — preflight obligatorio

Implementar una función reusable y pequeña.

En Windows, antes de escribir `documentation_v52`:

- calcular la ruta absoluta más larga;
- considerar también el nombre temporal usado por la escritura atómica;
- si excede el límite aplicable y long paths no están habilitados:
  - no empezar a escribir el stage;
  - devolver un error explícito:
    `OUTPUT_PATH_TOO_LONG`;
  - incluir:
    - ruta problemática;
    - longitud;
    - límite;
    - raíz `--output` actual;
    - longitud máxima sugerida para `--output`.

No permitir que el usuario reciba un `FileNotFoundError` ambiguo causado por longitud de ruta.

## 11. `--long-paths`

Si se implementa:

- solo Windows;
- opt-in;
- usar internamente el formato de ruta extendida apropiado;
- no modificar rutas lógicas/relativas persistidas;
- no alterar enlaces;
- no cambiar nombres de documentos;
- no modificar configuración del sistema operativo.

En otros sistemas:

- la opción debe ser inocua o rechazada con mensaje claro, según diseño más simple;
- documentar decisión.

Si el soporte correcto requiere ampliar demasiado el alcance, implementar en esta ronda solo el preflight y dejar `--long-paths` como `NEXT_ROUND`, explicando por qué.

## 12. Tests obligatorios — write-skip

Crear tests para:

1. primera corrida sin salida previa → escribe todo;
2. segunda corrida idéntica → no reescribe documentos idénticos;
3. contenido de un documento cambia → escribe solo el afectado cuando corresponda;
4. documento falta → lo reconstruye;
5. documento existente corrupto → lo reconstruye;
6. edición externa de mismo tamaño → no debe quedar falsamente aceptada;
7. manifest previo ausente → comportamiento seguro;
8. manifest previo corrupto → comportamiento seguro;
9. huérfano → se elimina;
10. manifest final idéntico al de una generación completa equivalente;
11. encoding y line endings idénticos;
12. determinismo;
13. cero cambios en IDs/Evidence Core;
14. runtime independence.

## 13. Tests obligatorios — MAX_PATH

Cubrir:

1. ruta dentro del límite;
2. ruta exactamente en el borde;
3. ruta que excede por el nombre temporal;
4. varias rutas y reporte de la peor;
5. error `OUTPUT_PATH_TOO_LONG`;
6. no se escribió ningún documento antes del error;
7. cálculo de longitud máxima sugerida de `--output`;
8. `--long-paths` si se implementa;
9. plataforma no Windows;
10. rutas relativas del manifest sin cambios.

## 14. Equivalencia

Comparar una corrida normal con write-skip contra una corrida que fuerce reescritura completa.

Debe obtenerse:

- mismos 46.567 documentos;
- mismo contenido;
- mismos SHA-256;
- mismo `MANIFEST.json`;
- mismos huérfanos eliminados;
- ningún cambio en Evidence Core ni en otras salidas.

En IST, comparar byte a byte `documentation_v52`.

Cualquier diferencia no explicada bloquea la ronda.

## 15. Medición IST obligatoria

Ejecutar el mínimo número de corridas necesarias sobre IST.

Medir al menos:

### Corrida A — estado sin reutilización válida

- tiempo `documentation_v52`;
- documentos escritos;
- bytes escritos.

### Corrida B — repetición sin cambios

- tiempo total `documentation_v52`;
- render;
- verificación;
- escritura;
- manifest;
- documentos escritos;
- documentos omitidos.

### Criterio contractual de R1

Objetivo:

`documentation_v52 <= 49 s`

en repetición sin cambios, si el mecanismo seguro disponible en esta ronda lo permite.

Si el modo estricto basado en hash no alcanza ese valor porque debe leer 46.567 archivos:

- reportar el valor real;
- NO debilitar la verificación;
- clasificar la limitación como dependencia de R2.4 si necesita File State persistido;
- estado de la ronda puede seguir siendo READY solo si la implementación aporta una mejora segura y el incumplimiento del objetivo se debe exclusivamente a una dependencia contractual explícita aún no implementable en R2.2; justificarlo claramente para revisión humana.

No falsear el criterio.

## 16. Suite

Ejecutar:

- tests dirigidos nuevos;
- tests de `documentation_v52`;
- tests de escritura atómica;
- tests de CLI si se agrega `--long-paths`;
- suite completa:
  `python -m unittest discover -s tests`

Registrar:

- total;
- fallas;
- errores;
- skips;
- duración.

## 17. Deuda técnica

Clasificar:

- BLOCKING;
- CURRENT_PHASE;
- NEXT_ROUND;
- FUTURE_PHASE;
- OBSERVATION.

Revisar específicamente:

- coste de verificación segura sin File State;
- `fsync` por archivo;
- MAX_PATH;
- soporte long paths;
- edición externa;
- antivirus/NTFS;
- barrido de huérfanos.

No resolver deuda ajena.

## 18. Git

Solo consultas.

No commit, tag ni push.

Registrar:

- archivos modificados;
- nuevos;
- pendientes administrativos previos.

## 19. Entregable

Crear:

`docs/V5/V5_3_R2_2_WRITE_SKIP_AND_MAX_PATH.md`

Debe incluir:

1. Resumen.
2. Archivos modificados.
3. Diseño final del write-skip.
4. Fuente de confianza usada.
5. Modo de verificación implementado.
6. Por qué es seguro.
7. Contadores.
8. Diseño MAX_PATH.
9. Estado de `--long-paths`.
10. Tests dirigidos.
11. Suite completa.
12. Equivalencia byte a byte.
13. Métricas IST antes/después.
14. Número de documentos escritos/omitidos.
15. Tiempo de verificación.
16. Tiempo de escritura.
17. Deuda técnica.
18. Riesgos.
19. Fuera de alcance confirmado.
20. Estado Git.
21. Estado final.

## 20. Estados finales permitidos

Si la implementación es correcta y segura:

`V5_3_R2_2_READY_FOR_REVIEW`

Si existe diferencia de salida, riesgo de aceptar archivos incorrectos, fallo de tests o un problema de ruta no controlado:

`V5_3_R2_2_BLOCKED`

No usar otro estado.

## 21. Restricciones finales

No:

- iniciar R2.3;
- implementar caché persistida general;
- crear `_cache_v53/`;
- crear File State;
- implementar extraction cache;
- añadir fingerprints de analizador/config;
- tocar Evidence Core;
- cambiar IDs;
- ejecutar IA;
- commit/push.

Detenerse para revisión humana.
