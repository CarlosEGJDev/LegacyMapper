# LegacyMapper V5.3 — R2.7 Scope Analysis + Persisted Run Metrics

## 1. Objetivo

Completar la siguiente pieza contractual de V5.3 después de R2.6:

1. implementar observabilidad persistida de la ejecución incremental;
2. implementar/anclar el análisis de alcance (`scope analysis`) previsto por R1;
3. persistir únicamente el estado auxiliar que R1 haya definido para esta etapa;
4. demostrar con cambios controlados qué parte del repositorio queda afectada;
5. mantener la corrección actual: resolvers y proyecciones siguen recomputándose salvo que R1 autorice explícitamente otra cosa.

Principio:

**scope analysis informa y prepara invalidación; no debe reducir corrección por sí solo.**

NO iniciar R2.8.

---

## 2. Fuente de autoridad

Antes de modificar código, releer y extraer explícitamente las decisiones relevantes de:

- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md`
- `docs/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md`
- `docs/V5/V5_3_R2_3_VERSIONING_AND_FINGERPRINTS.md`
- `docs/V5/V5_3_R2_4_CACHE_MANIFEST_AND_FILE_STATE.md`
- `docs/V5/V5_3_R2_5_EXTRACTION_CACHE.md`
- `docs/V5/V5_3_R2_6_WRITE_SKIP_REMAINING_OUTPUTS.md`
- `docs/V5/V5_3_R2_6_1_GIT_CHECKPOINT.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

### Regla

Si R1 define nombres/formatos distintos a los supuestos de este prompt:

**R1 manda.**

Documentar cualquier diferencia.

No inventar un nuevo contrato para `artifacts.json`, scope o métricas si R1 ya lo fija.

---

## 3. Estado de partida

R2.6 dejó:

- extraction cache persistida y adoptada;
- guardián propio del contrato;
- File State persistido;
- cache manifest;
- repository identity;
- fingerprints/versiones;
- write-skip en salidas;
- resolvers siempre recomputados;
- proyecciones siempre regeneradas;
- sin `RUN_METRICS.json`;
- sin `artifacts.json`;
- sin controles CLI de cache;
- sin scope-based stage skipping.

Checkpoint local de R2.6:

`c49a8a4fe44c20803adff3aa6ae798d822996e24`

El documento R2.6.1 puede seguir sin versionar y debe incluirse en el siguiente commit, pero esta ronda NO hace commit.

---

# PARTE A — CONTRATO EXACTO DE R2.7

## 4. Extracción previa del contrato

Antes de implementar, incluir en el informe una tabla:

| Tema | Qué dice R1 | Estado actual | Acción R2.7 |
|---|---|---|---|
| scope analysis | ... | ... | ... |
| persisted artifact state | ... | ... | ... |
| run metrics | ... | ... | ... |
| stage skipping | ... | ... | ... |
| resolver invalidation | ... | ... | ... |
| projection invalidation | ... | ... | ... |
| complete output invariant | ... | ... | ... |

Si R1 no autoriza aún persistir `artifacts.json`, NO crearlo.

Si R1 sí lo define, implementarlo exactamente.

---

# PARTE B — RUN METRICS

## 5. `RUN_METRICS.json`

Implementar solo si es compatible con R1.

Ruta preferida si R1 no define otra:

`<output>/_cache_v53/RUN_METRICS.json`

Debe quedar fuera de los outputs deterministas/productivos.

No incluirlo en:

- `OUTPUT_MANIFEST`;
- equivalencia de producto;
- Evidence Core;
- documentación.

---

## 6. Contenido mínimo de métricas

Registrar como observabilidad, no como fuente de verdad:

### Run

- contract/schema version;
- mode:
  - cold;
  - warm;
  - fallback_full;
  - refresh/off si aplica internamente;
- started/completed timestamp;
- total_seconds;
- final_status.

### File State

- files_total;
- unchanged;
- modified;
- added;
- deleted;
- renamed_candidates;
- line_ending_only;
- file_state_build_seconds;
- diff_seconds.

### Extraction cache

- hits;
- misses;
- bypass;
- reused;
- extracted;
- shards_loaded;
- shards_invalid;
- shards_rewritten;
- load/parse/validate/persist seconds.

### Pipeline stages

Tiempos de:

- SCAN;
- EXTRACTION;
- normalización;
- CALL_RESOLUTION;
- WEB_ENTRY_RESOLUTION;
- DATABASE_RESOLUTION;
- FLOW_RESOLUTION;
- DEPENDENCY_RESOLUTION;
- EXPORT;
- CONTEXT;
- DOCUMENTATION.

Usar nombres reales del pipeline.

### Write-skip

Por familia:

- generated;
- written;
- skipped_identical;
- bytes_generated;
- bytes_written;
- compare_seconds;
- write_seconds.

### Scope

- changed input files;
- impacted projects;
- directly impacted symbols/components si es demostrable;
- impacted roots/entry points si el contrato los define;
- reason/cause counts.

---

## 7. Determinismo de métricas

Las métricas son deliberadamente no deterministas por tiempos/timestamps.

Por tanto:

- no deben alterar outputs canónicos;
- no deben participar de hashes de producto;
- no deben invalidar cache;
- no deben ser usadas como autoridad de corrección.

La estructura/schema sí debe ser estable y testeada.

---

## 8. Persistencia segura de métricas

- escritura atómica;
- escribir al final de la corrida;
- si la corrida falla, puede escribirse un registro FAILED/PARTIAL solo si R1 lo permite;
- una métrica corrupta nunca debe invalidar una cache válida;
- borrar `RUN_METRICS.json` no cambia comportamiento del pipeline.

No convertir métricas en dependencia runtime obligatoria.

---

# PARTE C — SCOPE ANALYSIS

## 9. Objetivo del scope analysis

Calcular de forma determinista qué entidades/proyectos pueden estar afectados por los cambios de File State.

Debe responder al menos:

- qué archivos cambiaron;
- qué proyectos contienen esos archivos;
- qué proyectos dependen directa o transitivamente de proyectos afectados, si esa relación ya existe de forma fiable;
- qué entidades extraídas pertenecen a archivos cambiados;
- qué alcance es seguro afirmar;
- qué alcance NO puede afirmarse de forma segura.

---

## 10. Conservadurismo

Ante duda:

**ampliar scope, nunca reducirlo.**

No inferir seguridad a partir de heurísticas no probadas.

Ejemplos:

- archivo sin project mapping → scope repositorio/completo;
- cambio de `.vbproj` → proyecto completo como mínimo;
- cambio de `.sln` → conservador;
- cambio de `web.config` → ampliar a proyecto/aplicación según evidencia real;
- archivo desconocido → full/unknown scope;
- configuración/fingerprint incompatible → full.

---

## 11. Scope no es invalidation automática

En R2.7:

- scope puede calcularse;
- scope puede persistirse/registrarse si R1 lo permite;
- scope puede alimentar métricas;
- scope puede ser validado contra full.

Pero NO usarlo todavía para saltar:

- resolvers;
- normalización;
- proyecciones;
- documentación;
- Evidence Core.

Solo permitir skipping adicional si R1 lo autoriza explícitamente para R2.7 y existe evidencia/test de equivalencia.

---

## 12. Modelo sugerido

Preferir una estructura pequeña y explícita, por ejemplo:

`ScopeAnalysisResult`

con:

- `mode`: `full | partial_candidate`;
- `changed_files`;
- `impacted_projects`;
- `transitive_projects`;
- `reasons`;
- `fallback_reason`;
- `unknowns`.

No exponer APIs innecesarias.

Usar nombres reales de R1 si están definidos.

---

## 13. Persisted artifact state

Revisar R1 para determinar si corresponde implementar ahora `artifacts.json`.

### Si R1 lo define para esta etapa

Implementar exactamente su propósito.

Posible función esperada:

- describir artefactos derivados;
- asociar salida con renderer/version/config;
- registrar checksum;
- servir de observabilidad/diagnóstico.

### Restricción

NO usar `artifacts.json` como sustituto de:

- comparación byte a byte;
- Evidence Core;
- File State;
- extraction cache.

No confiar en él para saltar generación en R2.7 salvo autorización explícita del contrato.

### Si R1 lo difiere

Documentar:

`ARTIFACT_STATE_DEFERRED_BY_CONTRACT`

y no crearlo.

---

# PARTE D — VALIDACIÓN EMPÍRICA

## 14. Baseline warm sin cambios

Sobre IST oficial:

`C:\Users\cgalianj\source\IST_40\Operacional`

Ejecutar warm sin cambios.

Esperado:

- 15 138 unchanged;
- 0 modified;
- 0 added;
- 0 deleted;
- scope vacío o `NO_CHANGES`, según contrato;
- extraction cache warm;
- outputs equivalentes;
- métricas completas.

Registrar tiempos por stage.

---

## 15. Escenarios controlados

Usar copia de IST. No modificar el IST oficial.

### A. `.vb` modificado dentro de un proyecto

Verificar:

- archivo changed;
- proyecto directo afectado;
- dependientes si el algoritmo los incluye;
- no se omiten entidades necesarias.

### B. `.vb` nuevo

Verificar:

- added;
- proyecto afectado;
- scope conservador.

### C. `.vb` eliminado

Verificar:

- deleted;
- proyecto afectado.

### D. rename

Debe seguir siendo:

- deleted + added;
- renamed_candidate solo diagnóstico.

### E. `.vbproj`

Cambiar:

- RootNamespace;
- Compile includes, si existe fixture/archivo seguro.

Scope debe cubrir como mínimo todo el proyecto.

### F. `.sln`

Debe producir scope conservador/full según contrato.

### G. `web.config`

Validar alcance real permitido por arquitectura actual.

### H. archivo no analizado

Validar regla explícita.

### I. cambio de config/fingerprint

Scope no debe sobreponerse al fallback contractual full.

---

## 16. Oracle de corrección

Para cada escenario controlado:

1. corrida incremental/normal con scope analysis habilitado;
2. corrida full/cache off sobre el mismo estado;
3. comparar outputs deterministas.

Objetivo:

- 0 diferencias.

Aunque R2.7 no use scope para saltar stages, esto valida que el scope reportado es coherente con el resultado real.

---

## 17. Métrica de calidad del scope

Registrar:

- true impacted known;
- scope reported;
- false negatives;
- conservative extras.

Criterio obligatorio:

**0 false negatives en los escenarios donde el impacto real pueda determinarse.**

Se aceptan falsos positivos conservadores.

Si aparece un false negative:

`V5_3_R2_7_BLOCKED`

---

# PARTE E — TESTS

## 18. Tests unitarios de métricas

Cubrir:

1. schema estable;
2. cold;
3. warm;
4. fallback;
5. counters de File State;
6. extraction cache metrics;
7. write-skip metrics;
8. stage timings;
9. métricas no afectan hashes/cache;
10. corrupt metrics ignored/replaced;
11. atomic write;
12. deletion harmless;
13. runtime independence.

---

## 19. Tests unitarios de scope

Cubrir:

1. no changes;
2. modified;
3. added;
4. deleted;
5. rename;
6. file→project mapping;
7. unknown mapping → conservative/full;
8. vbproj;
9. solution;
10. web.config;
11. transitive project dependencies si se implementan;
12. deterministic ordering;
13. duplicate input;
14. incompatible cache/config → full;
15. no stage skipping.

---

## 20. Integración

Verificar explícitamente:

- extraction cache sigue funcionando;
- guardián sigue funcionando;
- write-skip sigue funcionando;
- resolvers siguen ejecutándose;
- proyecciones siguen regenerándose;
- outputs completos;
- borrar métricas no cambia resultado;
- scope no entra en output manifest;
- runtime clean distribution no depende de docs/prompts/tests.

---

## 21. Suite completa

Ejecutar:

`python -m unittest discover -s tests`

Registrar:

- total;
- fallas;
- errores;
- skips;
- duración.

Criterio:

- 0 fallas;
- 0 errores.

---

# PARTE F — RENDIMIENTO

## 22. Overhead

Medir coste agregado de:

- scope analysis;
- recolección de métricas;
- serialización/persistencia.

En warm IST.

Gate:

- no debe degradar materialmente el pipeline;
- si el scope cuesta más que el beneficio futuro razonable, documentar;
- no optimizar fuera de alcance.

---

## 23. Memoria

Medir pico si el scope necesita índices adicionales.

Evitar duplicar:

- modelos completos;
- evidencia completa;
- extraction cache completa;

solo para calcular scope.

Reutilizar estructuras existentes cuando sea seguro.

---

# PARTE G — MANTENIBILIDAD Y SEGURIDAD

## 24. Mantenibilidad

Evitar:

- inflar `full_pipeline.py`;
- un módulo monolítico;
- dependencia circular entre cache y analysis;
- duplicar project/dependency mapping;
- acoplar métricas a outputs canónicos.

Preferir módulos como:

- `cache/run_metrics.py`;
- `cache/scope.py`;

o nombres equivalentes coherentes con el repo.

---

## 25. Seguridad

Métricas/scope NO deben persistir:

- contenido fuente;
- secretos;
- SQL/texto sensible completo;
- payloads de símbolos si no son necesarios.

Preferir:

- rutas relativas;
- IDs;
- contadores;
- razones;
- hashes cuando corresponda.

Aplicar sanitización si cualquier valor de texto pudiera contener contenido sensible.

---

## 26. Git

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
- relación con origin;
- rama backup;
- archivos modificados/nuevos;
- documento R2.6.1 aún pendiente si aplica.

---

# PARTE H — FUERA DE ALCANCE

## 27. No implementar

No:

- iniciar R2.8;
- controles CLI nuevos;
- `--cache-mode`;
- `--cache-dir`;
- `--verify-cache`;
- `--trust-mtime`;
- `--incremental-max-changed-ratio`;
- resolver cache;
- flow cache persistida;
- projection cache;
- stage skipping no autorizado;
- partial resolver recomputation;
- IDs nuevos;
- cambios Evidence Core;
- cambios semánticos de documentación;
- IA;
- push/tag.

---

# PARTE I — ENTREGABLE

## 28. Documento

Crear:

`docs/V5/V5_3_R2_7_SCOPE_ANALYSIS_AND_RUN_METRICS.md`

Debe incluir:

1. Objetivo.
2. Contrato R1 recuperado.
3. Diferencias entre R1 y supuestos del prompt.
4. Archivos modificados.
5. RUN_METRICS schema.
6. Persistencia/atomicidad.
7. Scope model.
8. Reglas conservadoras.
9. Persisted artifact state (`implemented` o `DEFERRED_BY_CONTRACT`).
10. Integración pipeline.
11. Tests unitarios.
12. Tests integración.
13. Suite completa.
14. IST warm sin cambios.
15. Escenarios controlados A–I.
16. Oracle full vs incremental.
17. False negatives / conservative extras.
18. Overhead.
19. Memoria.
20. Seguridad.
21. Mantenibilidad.
22. Deuda técnica.
23. Riesgos.
24. Fuera de alcance.
25. Estado Git.
26. Recomendación para R2.8.
27. Estado final.

---

## 29. Estados finales permitidos

Si scope + métricas quedan correctos y sin false negatives:

`V5_3_R2_7_READY_FOR_REVIEW`

Si R1 difiere materialmente y requiere decisión:

`V5_3_R2_7_NEEDS_HUMAN_DECISION`

Si hay false negatives, regresiones, tests fallidos o persistencia insegura:

`V5_3_R2_7_BLOCKED`

---

## 30. Criterio de cierre

R2.7 está lista si:

- R1 fue respetado;
- métricas existen sin afectar outputs canónicos;
- scope es determinista y conservador;
- 0 false negatives en casos verificables;
- resolvers/proyecciones no se saltan sin autorización;
- artifact state se implementa solo si corresponde por contrato;
- suite verde;
- IST medido;
- overhead razonable;
- no se amplió alcance.

Detenerse para revisión humana.
