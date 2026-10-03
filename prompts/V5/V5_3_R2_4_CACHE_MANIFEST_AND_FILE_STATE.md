# LegacyMapper V5.3 — R2.4 Cache Manifest + File State

## 1. Objetivo

Implementar únicamente la infraestructura persistida mínima de V5.3 necesaria para comparar una corrida con la siguiente:

1. `CACHE_MANIFEST.json`;
2. `file_state.json`;
3. identidad del repositorio;
4. validación de integridad;
5. clasificación determinista de archivos:
   - unchanged;
   - modified;
   - added;
   - deleted;
   - renamed_candidate;
6. modos cold/warm/corrupt/incomplete;
7. fallback seguro a full.

Esta ronda NO implementa todavía caché de extracción.

## 2. Fuentes obligatorias

Leer antes de modificar:

- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `docs/V5/V5_3_R2_1_SHARED_HYDRATION_VIEW.md`
- `docs/V5/V5_3_R2_2_WRITE_SKIP_AND_MAX_PATH.md`
- `docs/V5/V5_3_R2_2_1_MAINTAINABILITY_AND_FINAL_VALIDATION.md`
- `docs/V5/V5_3_R2_3_VERSIONING_AND_FINGERPRINTS.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

Decisiones contractuales principales:

- R1 §6.A — File State;
- R1 §7 — Cache Manifest;
- R1 §11 — full vs incremental;
- R1 §18 — migración;
- R1 §20 — seguridad/consistencia.

## 3. Estado de partida

R2.3 está aprobado.

Disponibles en runtime:

- `ANALYZER_VERSION`;
- `ANALYZER_CODE_FINGERPRINT`;
- `EVIDENCE_SCHEMA_VERSION`;
- `RENDERER_VERSIONS`;
- `CONFIG_FINGERPRINT`;
- `TEMPLATE_PROFILE_FINGERPRINT`;
- hash semántico de archivos analizados.

Todavía NO existe:

- `_cache_v53/`;
- `CACHE_MANIFEST.json`;
- `file_state.json`;
- extraction cache;
- invalidación selectiva;
- persistencia de artefactos derivados.

## 4. Alcance permitido

Modificar únicamente lo necesario para:

1. crear estructura de caché V5.3;
2. persistir File State;
3. persistir Cache Manifest;
4. validar caché previa;
5. calcular repository identity;
6. comparar estado anterior vs actual;
7. detectar renamed candidates;
8. registrar reason/fallback;
9. exponer datos al pipeline futuro;
10. añadir tests.

No usar todavía este estado para saltarse extracción o stages.

## 5. Ubicación de caché

Por defecto:

`<output>/_cache_v53/`

Debe contener como mínimo:

```text
_cache_v53/
  CACHE_MANIFEST.json
  file_state.json
```

Puede añadirse una subcarpeta temporal interna si es estrictamente necesaria para escritura segura.

No crear todavía:

- `extraction/`;
- shards;
- `artifacts.json`;
- `RUN_METRICS.json`.

## 6. CACHE_MANIFEST.json

Implementar un manifest nuevo y separado de los manifests existentes.

No modificar:

- `EVIDENCE_MANIFEST.json`;
- `documentation_v52/MANIFEST.json`;
- `RUN_SUMMARY`;
- `OUTPUT_MANIFEST`.

### Contenido mínimo

Debe incluir:

- `contract`;
- `cache_schema_version`;
- `state`;
- `versions`:
  - analyzer_version;
  - analyzer_code_fingerprint;
  - evidence_schema_version;
  - renderer_versions;
  - template_profile_fingerprint;
- `config_fingerprint`;
- identidad del repositorio;
- metadata informativa:
  - git_head si está disponible;
  - git_branch si está disponible;
  - generated_at;
- referencia a `file_state.json`;
- SHA-256 de `file_state.json`;
- cantidad de archivos;
- `validity.complete = true`.

### Estado válido

Solo se considera válida una caché si:

- existe `CACHE_MANIFEST.json`;
- `state == COMPLETE`;
- `cache_schema_version` es reconocida;
- checksum de `file_state.json` coincide;
- repository identity coincide;
- versiones y fingerprint compatibles;
- configuración compatible.

Si cualquiera falla:

`fallback = full`

No lanzar error fatal por caché inválida.

## 7. Orden seguro de escritura

Seguir estrictamente:

1. invalidar/borrar manifest previo;
2. escribir `file_state.json` atómicamente;
3. releerlo;
4. validar su SHA-256;
5. construir manifest;
6. escribir `CACHE_MANIFEST.json` al final;
7. solo entonces marcar caché como válida.

Si el proceso se interrumpe antes del paso final:

- la siguiente corrida debe considerar la caché inexistente/incompleta;
- ejecutar full;
- regenerarla.

## 8. Repository Identity

Definir identidad estable del repositorio.

Debe incluir como mínimo:

- ruta absoluta normalizada;
- fingerprint SHA-256 de esa ruta normalizada.

Reglas:

- Windows: normalización de mayúsculas/minúsculas de forma estable;
- separadores normalizados;
- no usar Git HEAD como identidad principal;
- Git branch/HEAD solo metadata;
- misma ruta + contenido distinto sigue siendo mismo repositorio, detectado por File State;
- ruta distinta ⇒ repository identity distinta ⇒ full.

No mezclar cachés entre repositorios.

## 9. File State

`file_state.json` debe representar el estado de los archivos escaneados relevantes.

Por archivo guardar:

- `path` relativa normalizada;
- `size`;
- `sha256_raw`;
- `sha256_semantic` o `null`;
- `file_type`;
- `project_path` si puede resolverse sin ampliar alcance;
- `mtime_ns` solo como metadata;
- cualquier campo mínimo necesario para comparación.

NO persistir:

- contenido fuente;
- secretos;
- datos extraídos;
- llamadas;
- símbolos.

## 10. Cálculo de hashes

### Hash crudo

Usar SHA-256 de bytes reales.

Debe coincidir conceptualmente con `SourceArtifact.sha256`.

### Hash semántico

Usar el helper de R2.3 para tipos analizados.

No recalcular con una lógica distinta.

### Lectura

Evitar leer el mismo archivo más veces de las necesarias dentro de esta ronda.

Si es posible, producir ambos hashes en una sola lectura.

No alterar todavía Evidence Core para compartir esa lectura; solo medir y documentar la duplicación si existe.

## 11. Comparación de estados

Comparar el File State actual con el anterior válido.

Clasificar cada ruta:

- `unchanged`;
- `modified`;
- `added`;
- `deleted`.

### renamed_candidate

Si un archivo nuevo y uno eliminado comparten el mismo hash semántico o crudo aplicable:

- registrar `renamed_candidate`;
- solo como metadata/diagnóstico;
- NO reutilizar extracción por rename;
- NO considerar que el rename preserva identidad.

Contrato:

`rename = deleted + added`

porque IDs existentes dependen de la ruta.

## 12. Compatibilidad de caché

Comparar como mínimo:

### Obliga full

- manifest ausente;
- manifest incompleto;
- schema de caché desconocido;
- analyzer version distinta;
- analyzer code fingerprint distinto;
- evidence schema distinto;
- repository identity distinta;
- checksum de `file_state.json` inválido;
- fingerprint de configuración de análisis incompatible;
- fuentes del analizador no disponibles.

### No obliga full por sí solo

- renderer version distinta;
- template/profile fingerprint distinto;
- Git branch distinto;
- Git HEAD distinto.

Esos cambios afectan proyecciones, no extracción, según R1.

Documentar la decisión.

## 13. Resultado de validación de caché

Crear una API pequeña, por ejemplo:

```python
CacheValidationResult(
    valid: bool,
    mode: str,
    reason: str | None,
    manifest: ...,
)
```

y para comparación:

```python
FileStateDiff(
    unchanged=[...],
    modified=[...],
    added=[...],
    deleted=[...],
    renamed_candidates=[...],
)
```

Los nombres exactos pueden variar.

Evitar jerarquías complejas.

## 14. Integración con pipeline

Esta ronda puede integrar la creación/lectura del estado en el pipeline SOLO para:

- construir File State;
- validar manifest;
- registrar modo:
  - cold;
  - warm;
  - fallback_full;
- persistir nuevo estado al final de una corrida exitosa.

NO debe todavía:

- saltarse extracción;
- reutilizar símbolos/calls;
- saltarse resolvers;
- cambiar outputs;
- cambiar resultado lógico;
- alterar `RUN_SUMMARY`.

## 15. Momento de persistencia

Persistir la caché nueva solo si la corrida principal terminó correctamente.

Si la corrida queda:

- PARTIAL;
- FAILED;
- interrumpida;

no escribir un `CACHE_MANIFEST.json` válido.

Puede quedar `file_state.json` temporal/incompleto, pero sin manifest final debe considerarse inválido.

## 16. CLI

Implementar únicamente si es necesario para este contrato:

- `--cache-dir` puede añadirse ahora si R1 lo requiere;
- `--cache-mode` puede añadirse en forma mínima solo si hace falta para:
  - `off`;
  - `refresh`;
  - `auto`.

Si introducir ambas opciones amplía demasiado el alcance, priorizar:

1. caché por defecto en `<output>/_cache_v53/`;
2. lectura/escritura automática;
3. dejar controles CLI completos para R2.8.

Documentar decisión.

NO añadir todavía:

- `--verify-cache`;
- `--trust-mtime`;
- `--incremental-max-changed-ratio`.

## 17. Seguridad

Asegurar:

- no persistir secretos;
- solo paths/hashes/tamaños/tipos/metadata;
- escritura atómica;
- checksum;
- caché corrupta no rompe la corrida;
- caché de otro repo no se reutiliza;
- temporales huérfanos se limpian si pertenecen a `_cache_v53/`.

## 18. Runtime independence

Los nuevos módulos NO pueden depender de:

- docs;
- prompts;
- tests;
- `PROJECT_STATE.json`;
- gobernanza;
- IA;
- Copilot.

Biblioteca estándar preferida.

## 19. Tests obligatorios — Cache Manifest

Cubrir:

1. cold start sin caché;
2. manifest válido;
3. manifest ausente;
4. manifest corrupto;
5. `state != COMPLETE`;
6. schema desconocido;
7. checksum de `file_state.json` incorrecto;
8. repository identity distinta;
9. analyzer version distinta;
10. analyzer code fingerprint distinto;
11. evidence schema distinto;
12. config fingerprint incompatible;
13. renderer distinto no invalida extracción;
14. template fingerprint distinto no invalida extracción;
15. Git HEAD/branch distinto no invalida extracción;
16. escritura de manifest al final;
17. interrupción antes de manifest;
18. runtime independence.

## 20. Tests obligatorios — File State

Cubrir:

1. archivo unchanged;
2. modified;
3. added;
4. deleted;
5. rename candidate;
6. rename sigue siendo added + deleted;
7. CRLF↔LF:
   - raw cambia;
   - semantic igual;
8. BOM cambia semantic;
9. archivo binario/no analizado;
10. orden determinista;
11. rutas normalizadas;
12. mtime distinto sin cambio de bytes;
13. archivo ilegible;
14. project_path si se implementa;
15. sin secretos/contenido persistido;
16. determinismo del JSON.

## 21. Tests obligatorios — integración

Cubrir:

1. primera corrida válida crea `_cache_v53/`;
2. segunda corrida sin cambios valida caché;
3. output lógico idéntico con y sin caché;
4. caché inválida ⇒ full pero corrida correcta;
5. corrida fallida no deja manifest válido;
6. borrar `_cache_v53/` no cambia resultados;
7. no se saltan stages;
8. no se reutiliza extracción todavía.

## 22. Suite

Ejecutar:

- tests dirigidos nuevos;
- tests de fingerprints;
- tests de pipeline;
- tests de runtime independence;
- suite completa:
  `python -m unittest discover -s tests`

Registrar:

- total;
- fallas;
- errores;
- skips;
- duración.

## 23. Validación IST

Ejecutar como mínimo:

### Corrida A — cold

Sin `_cache_v53/`.

Medir:

- tiempo de construir File State;
- tiempo hashes raw/semantic;
- tamaño `file_state.json`;
- tamaño `CACHE_MANIFEST.json`;
- memoria;
- tiempo total agregado por R2.4.

### Corrida B — warm, sin cambios

Medir:

- tiempo de validar manifest;
- tiempo de comparar estado;
- unchanged;
- modified;
- added;
- deleted;
- renamed candidates;
- tiempo total agregado.

Debe resultar:

- todos los archivos unchanged;
- 0 modified;
- 0 added;
- 0 deleted.

### Corrida C — cambio controlado sobre copia

Sobre una copia de IST, realizar al menos:

- un archivo modificado;
- un archivo nuevo;
- un archivo eliminado;
- un rename.

Validar clasificación.

No modificar IST oficial.

## 24. Criterios de aceptación

Cerrar solo si:

1. manifest seguro y determinista;
2. File State correcto;
3. cold/warm funcionan;
4. corrupción cae a full;
5. interrupción no deja caché válida;
6. repo distinto no reutiliza caché;
7. diff de archivos correcto;
8. rename no preserva identidad;
9. suite verde;
10. outputs del pipeline no cambian;
11. no se reutiliza extracción todavía;
12. coste agregado es razonable y medido.

## 25. Deuda técnica

Clasificar:

- BLOCKING;
- CURRENT_PHASE;
- NEXT_ROUND;
- FUTURE_PHASE;
- OBSERVATION.

Revisar especialmente:

- tamaño de `file_state.json`;
- coste de hashing;
- duplicación de lectura con Evidence Core;
- `mtime_ns`;
- repository identity;
- interacción con `--output`;
- necesidad futura de `--cache-dir`;
- exclusión de `_cache_v53/` del output manifest;
- crecimiento de módulos.

No corregir deuda fuera de alcance.

## 26. Git

Solo consultas.

No commit, tag ni push.

Registrar:

- archivos modificados;
- nuevos;
- pendientes previos.

## 27. Entregable

Crear:

`docs/V5/V5_3_R2_4_CACHE_MANIFEST_AND_FILE_STATE.md`

Debe incluir:

1. Objetivo.
2. Archivos modificados.
3. Arquitectura de caché creada.
4. `CACHE_MANIFEST.json`.
5. Repository Identity.
6. `file_state.json`.
7. Algoritmo de comparación.
8. renamed candidates.
9. Compatibilidad/fallback.
10. Integración con pipeline.
11. Seguridad.
12. Tests dirigidos.
13. Suite completa.
14. Validación IST cold.
15. Validación IST warm.
16. Cambio controlado.
17. Costes medidos.
18. Tamaños de archivos.
19. Deuda técnica.
20. Riesgos.
21. Fuera de alcance confirmado.
22. Estado Git.
23. Estado final.

## 28. Estados finales permitidos

Si todo cumple:

`V5_3_R2_4_READY_FOR_REVIEW`

Si existe riesgo de reutilización incorrecta, corrupción no controlada, diff incorrecto o tests fallidos:

`V5_3_R2_4_BLOCKED`

No usar otro estado.

## 29. Restricciones finales

No:

- iniciar R2.5;
- implementar extraction cache;
- crear shards;
- saltarse extracción;
- saltarse resolvers;
- cambiar Evidence Core;
- cambiar IDs;
- cambiar manifests existentes;
- ampliar write-skip;
- ejecutar IA;
- commit/push.

Detenerse para revisión humana.
