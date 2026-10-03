# LegacyMapper V5.3 — R2.5 Extraction Cache

## 1. Objetivo

Implementar únicamente la caché persistida de extracción por archivo definida en V5.3 R1.

La ronda debe demostrar dos cosas antes de aceptar la funcionalidad:

1. equivalencia exacta con una corrida full;
2. beneficio real medido frente a re-extraer.

Si cargar + validar la extracción persistida NO es más rápido que re-extraer en IST, la caché de extracción debe quedar desactivada/diferida y la ronda debe documentarlo sin forzar su adopción.

## 2. Fuentes obligatorias

Leer antes de modificar:

- `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md`
- `docs/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md`
- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `docs/V5/V5_3_R2_1_SHARED_HYDRATION_VIEW.md`
- `docs/V5/V5_3_R2_2_WRITE_SKIP_AND_MAX_PATH.md`
- `docs/V5/V5_3_R2_2_1_MAINTAINABILITY_AND_FINAL_VALIDATION.md`
- `docs/V5/V5_3_R2_3_VERSIONING_AND_FINGERPRINTS.md`
- `docs/V5/V5_3_R2_4_CACHE_MANIFEST_AND_FILE_STATE.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

## 3. Estado de partida

R2.4 está aprobado.

Ya existen:

- `_cache_v53/`;
- `CACHE_MANIFEST.json`;
- `file_state.json`;
- identidad del repositorio;
- fingerprints/versionado;
- clasificación unchanged/modified/added/deleted;
- fallback seguro;
- validación cold/warm/corrupt/incomplete.

Todavía NO existe:

- caché persistida de extracción;
- shards;
- reutilización de símbolos/calls/webforms/etc.;
- invalidación parcial de resolvers;
- write-skip de otras salidas;
- métricas generales persistidas.

## 4. Alcance permitido

Implementar únicamente:

1. caché persistida de extracción por archivo;
2. sharding determinista;
3. carga de extracción para archivos unchanged;
4. re-extracción de archivos changed;
5. purga de entradas deleted;
6. bypass seguro cuando sanitizar cambia el registro;
7. normalización global siempre después de cargar/extraer;
8. validación de checksums;
9. fallback seguro por shard;
10. mediciones y tests.

NO reutilizar resolvers ni proyecciones.

## 5. Arquitectura esperada

Dentro de:

`<output>/_cache_v53/`

añadir:

```text
extraction/
  ex-000.json
  ex-001.json
  ...
  ex-255.json
```

Puede usarse otro número de shards solo si se justifica con medición clara y manteniendo determinismo.

El `CACHE_MANIFEST.json` debe incorporar:

- cantidad de shards;
- SHA-256 por shard;
- cualquier metadata mínima necesaria.

No crear todavía:

- `artifacts.json`;
- `RUN_METRICS.json`.

## 6. Unidad de caché

Unidad:

`archivo`

La clave debe incluir conceptualmente:

- ruta relativa normalizada;
- hash semántico;
- `file_type`;
- `ANALYZER_VERSION`;
- `ANALYZER_CODE_FINGERPRINT`;
- fingerprint de configuración de análisis.

No usar `mtime` como clave de confianza.

## 7. Registros a persistir

Persistir únicamente salida de extractor por archivo, antes de normalización global y antes de resolvers.

### `vb_source`

- symbols;
- calls;
- web_events;
- data_access_indexes;
- errors de extracción del archivo.

### `aspx` / `ascx` / `master`

- webform;
- errors.

### `vb_project`

- project;
- errors.

### `solution`

- solution;
- errors.

### `web_config`

- configuration;
- errors.

No persistir:

- resultados de resolvers;
- flows;
- paths;
- dependencias resueltas;
- documentación;
- Evidence Core;
- secretos sin sanear.

## 8. Sanitización y cache_bypass

R1/R0.1 detectaron que algunos registros cambian al pasar por `sanitize_data`.

Contrato:

- antes de persistir un registro de extracción, aplicar `sanitize_data`;
- comparar salida saneada vs original;
- si cambia:
  - marcar archivo como `cache_bypass`;
  - NO persistir su extracción reutilizable;
  - re-extraer siempre ese archivo en corridas futuras.

Objetivo:

- cero secretos persistidos;
- equivalencia exacta frente a full.

No modificar el comportamiento normal de extracción.

## 9. Mutabilidad

Los resolvers mutan estructuras en memoria.

Por tanto:

- persistir antes de cualquier resolver;
- al cargar desde disco, crear objetos independientes;
- no permitir que mutaciones de una corrida alteren el contenido persistido;
- no mantener objetos globales compartidos entre corridas.

Añadir test explícito.

## 10. Normalización global

Aunque la extracción se reutilice, SIEMPRE ejecutar:

- `apply_project_namespaces`;
- `consolidate_partial_symbols`;
- cualquier normalización global existente.

Justificación:

- `RootNamespace`;
- compile items;
- partial classes;
- relaciones multiarchivo.

No cachear esas fases en R2.5.

## 11. Resolvers

SIEMPRE recomputar:

- CALL_RESOLUTION;
- WEB_ENTRY_RESOLUTION;
- DATABASE_RESOLUTION;
- FLOW_RESOLUTION;
- DEPENDENCY_RESOLUTION.

No implementar invalidación parcial.

## 12. Sharding

Requisitos:

- asignación determinista por hash de ruta normalizada;
- shard estable;
- JSON canónico;
- orden estable;
- un cambio de un archivo no debe reescribir los 256 shards;
- solo shards modificados se reescriben;
- checksum por shard en manifest.

Medir:

- tamaño total;
- tamaño medio;
- tiempo de carga;
- tiempo de parseo;
- tiempo de validación.

## 13. Corrupción

Política contractual:

- un shard corrupto:
  - descartar solo ese shard;
  - sus archivos cuentan como miss;
  - re-extraerlos;
  - salida debe seguir siendo equivalente a full.

- más de un shard corrupto:
  - fallback full;
  - regenerar caché.

- manifest inválido:
  - fallback full.

No producir error fatal por caché.

## 14. Archivos deleted / added / modified

### unchanged

Puede intentar reutilizar extracción si:

- cache válida;
- shard válido;
- entrada válida;
- no `cache_bypass`;
- fingerprint coincide.

### modified

Re-extraer.

### added

Extraer.

### deleted

Eliminar entrada de shard.

### renamed_candidate

Tratar como:

- deleted;
- added.

No reutilizar extracción por rename.

## 15. Errores de extracción

Un error de extracción también puede cachearse si:

- es determinista para los mismos bytes;
- no contiene secretos;
- pasa sanitización sin alteración.

Si sanitización lo altera:

- `cache_bypass`.

Añadir tests.

## 16. Integración con pipeline

La integración permitida es SOLO en la etapa EXTRACTION.

Flujo conceptual:

```text
SCAN
→ File State
→ cargar extraction cache válida
→ reuse unchanged
→ extraer changed/added/bypass/miss
→ ensamblar extracción completa
→ persistir estado de extracción antes de normalización/resolvers
→ normalización global
→ resolvers completos
→ resto del pipeline sin cambios
```

No saltar ningún otro stage.

## 17. Gate de rendimiento obligatorio

R1 exige implementar esta capa solo si demuestra beneficio real.

Medir sobre IST:

### Baseline full extraction

Sin reutilización:

- tiempo EXTRACTION;
- tiempo de lectura de fuentes;
- total de archivos extraídos.

### Warm extraction cache

Sin cambios:

- tiempo de validar shards;
- tiempo de cargar shards;
- tiempo de parsear;
- tiempo de ensamblar;
- archivos reutilizados;
- archivos re-extraídos;
- cache hits/misses.

### Gate

Adoptar la caché de extracción solo si:

`load + validate + assemble < re-extract`

en la misma máquina y condiciones comparables.

No fijar porcentaje arbitrario.

Si NO cumple:

- dejar infraestructura presente solo si no altera comportamiento;
- desactivar consumo por defecto;
- documentar `DEFERRED_BY_MEASUREMENT`;
- no inventar optimizaciones adicionales fuera de alcance.

## 18. Escenarios IST obligatorios

Ejecutar como mínimo:

### A. Cold

- sin extraction cache;
- extraer todo;
- persistir shards.

### B. Warm sin cambios

- reutilizar todo lo seguro;
- medir hits/misses.

### C. 1 archivo `.vb` modificado

- re-extraer solo ese archivo + bypass;
- reutilizar resto;
- resolvers completos;
- salida ≡ full.

### D. rename

- deleted + added;
- no reutilizar extracción del archivo renombrado.

### E. cambio RootNamespace

- re-extraer `.vbproj`;
- reutilizar `.vb`;
- ejecutar normalización global;
- salida ≡ full.

### F. partial class

- re-extraer archivo cambiado;
- consolidación global;
- salida ≡ full.

### G. corrupción de un shard

- fallback parcial;
- salida ≡ full.

### H. corrupción de >1 shard

- full;
- salida ≡ full.

No modificar IST oficial; usar copia para cambios.

## 19. Equivalencia obligatoria

Comparar FULL vs extraction-cache para:

- symbols;
- calls;
- web_events;
- webforms;
- projects;
- solutions;
- configuration;
- data_access_indexes;
- errors;
- normalización global;
- resoluciones;
- flows;
- paths;
- Evidence Core;
- documentation;
- manifests;
- outputs completos.

Objetivo:

- mismos IDs;
- mismas relaciones;
- mismos unresolved;
- mismos bytes salvo campos no deterministas ya declarados.

Cualquier divergencia no explicada:

`V5_3_R2_5_BLOCKED`

## 20. Tests obligatorios — unidad

Cubrir:

1. shard determinista;
2. misma ruta → mismo shard;
3. cambio de ruta → posible shard distinto;
4. JSON canónico;
5. checksum correcto;
6. checksum incorrecto;
7. entrada válida;
8. entrada con fingerprint distinto;
9. archivo unchanged hit;
10. modified miss;
11. added miss;
12. deleted purge;
13. rename = delete + add;
14. cache_bypass por sanitización;
15. error de extracción cacheable;
16. error saneado → bypass;
17. mutación posterior no altera cache;
18. normalización global posterior;
19. runtime independence;
20. sin secretos.

## 21. Tests obligatorios — integración

Cubrir:

1. cold → extraction completa;
2. warm → reuse;
3. resolvers siguen ejecutándose;
4. output lógico igual;
5. 1 shard corrupto → miss parcial;
6. >1 corrupto → full;
7. manifest inválido → full;
8. cache borrada → full;
9. analyzer version change → full;
10. analyzer fingerprint change → full;
11. config analysis change → full;
12. renderer/template change NO invalida extracción;
13. branch/HEAD change NO invalida por sí solo;
14. failure de escritura de cache no falla la corrida;
15. cache_mode off mantiene comportamiento sin reuse si está disponible a nivel biblioteca.

## 22. Suite

Ejecutar:

- tests nuevos;
- tests de R2.3/R2.4;
- tests de extracción;
- tests de normalización;
- tests de resolvers;
- tests de runtime independence;
- suite completa:
  `python -m unittest discover -s tests`

Registrar:

- total;
- fallas;
- errores;
- skips;
- duración.

## 23. Métricas mínimas

Registrar al menos:

- extraction_cache_enabled;
- extraction_cache_hits;
- extraction_cache_misses;
- extraction_cache_bypass;
- shards_loaded;
- shards_invalid;
- shards_rewritten;
- files_reused;
- files_extracted;
- load_seconds;
- validate_seconds;
- parse_seconds;
- extraction_seconds;
- persist_seconds;
- cache_size_bytes.

Puede ir a logs/estructura interna.

No crear todavía `RUN_METRICS.json`.

## 24. Seguridad

Verificar:

- ningún secreto en shards;
- rutas relativas, no contenido sensible adicional;
- sanitización aplicada;
- bypass correcto;
- atomic writes;
- manifest final;
- corrupción no rompe la corrida;
- no mezcla repositorios.

Escanear `_cache_v53/extraction/` con el mismo patrón de secretos usado por el sanitizador.

## 25. Mantenibilidad

Evitar:

- módulo monolítico;
- ciclos;
- acoplamiento cache↔pipeline;
- lógica de resolución dentro de cache;
- duplicar sanitizador;
- duplicar hashing de R2.3.

Un módulo por responsabilidad si es natural.

## 26. Deuda técnica

Clasificar:

- BLOCKING;
- CURRENT_PHASE;
- NEXT_ROUND;
- FUTURE_PHASE;
- OBSERVATION.

Revisar especialmente:

- coste parse JSON;
- número de shards;
- cache_bypass;
- lectura duplicada;
- project_path pendiente;
- necesidad real de extraction cache;
- crecimiento de memoria;
- SQLite/JSONL solo si hay evidencia, no introducir ahora.

## 27. Git

Solo consultas.

No commit, tag ni push.

Registrar:

- archivos modificados;
- nuevos;
- pendientes previos.

## 28. Entregable

Crear:

`docs/V5/V5_3_R2_5_EXTRACTION_CACHE.md`

Debe incluir:

1. Objetivo.
2. Archivos modificados.
3. Arquitectura de extraction cache.
4. Sharding.
5. Clave de unidad.
6. Registros persistidos.
7. Sanitización/cache_bypass.
8. Mutabilidad.
9. Normalización global.
10. Resolvers.
11. Corrupción/fallback.
12. Tests unitarios.
13. Tests integración.
14. Suite completa.
15. IST cold.
16. IST warm.
17. Cambios controlados.
18. Equivalencia full vs cache.
19. Gate de rendimiento.
20. Decisión final:
   - ADOPTED;
   - DEFERRED_BY_MEASUREMENT.
21. Tamaño de cache.
22. Costes.
23. Seguridad.
24. Deuda técnica.
25. Riesgos.
26. Fuera de alcance confirmado.
27. Estado Git.
28. Estado final.

## 29. Estados finales permitidos

Si la implementación es correcta y pasa equivalencia:

`V5_3_R2_5_READY_FOR_REVIEW`

Si hay divergencia, corrupción insegura, secretos persistidos, tests fallidos o fallback incorrecto:

`V5_3_R2_5_BLOCKED`

La decisión de rendimiento se reporta aparte como:

- `EXTRACTION_CACHE_ADOPTED`

o
- `EXTRACTION_CACHE_DEFERRED_BY_MEASUREMENT`

No usar otro estado.

## 30. Restricciones finales

No:

- iniciar R2.6;
- cachear resolvers;
- cachear flows persistidos;
- cachear proyecciones;
- crear `artifacts.json`;
- crear `RUN_METRICS.json`;
- cambiar Evidence Core;
- cambiar IDs;
- ampliar write-skip;
- ejecutar IA;
- commit/push.

Detenerse para revisión humana.
