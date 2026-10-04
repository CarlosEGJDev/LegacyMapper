# LegacyMapper V5.3 — R2.6 Guardian de Extraction Cache + Write-Skip de Salidas Restantes

## 1. Objetivo

Completar dos piezas antes de seguir ampliando la fase incremental:

1. añadir un guardián explícito del contrato/formato de la extraction cache;
2. extender write-skip seguro a las salidas restantes de V5.3, regenerando siempre el contenido pero evitando escrituras cuando los bytes finales son idénticos.

Esta ronda NO introduce reutilización de resolvers, flows, proyecciones ni documentación.

Principio rector:

**Recompute for correctness; skip identical writes for savings.**

---

## 2. Estado de partida

V5.3 tiene completadas y revisadas:

- R0
- R0.1
- R1
- R2.1
- R2.2
- R2.2.1
- R2.3
- R2.4
- R2.5
- R2.5.1
- R2.5.2
- R2.5.3
- R2.5.4

Checkpoint funcional:

`2cb317fe5ae3dd2cbad1f865b1faee4a50a99569`

Existe además un commit administrativo posterior de R2.5.4.

Rama de respaldo local:

`backup/v5.3-pre-worktree-cleanup`

Los worktrees residuales ya fueron retirados y existe backup externo.

---

## 3. Fuentes obligatorias

Leer antes de modificar:

- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `docs/V5/V5_3_R2_1_SHARED_HYDRATION_VIEW.md`
- `docs/V5/V5_3_R2_2_WRITE_SKIP_AND_MAX_PATH.md`
- `docs/V5/V5_3_R2_2_1_MAINTAINABILITY_AND_FINAL_VALIDATION.md`
- `docs/V5/V5_3_R2_3_VERSIONING_AND_FINGERPRINTS.md`
- `docs/V5/V5_3_R2_4_CACHE_MANIFEST_AND_FILE_STATE.md`
- `docs/V5/V5_3_R2_5_EXTRACTION_CACHE.md`
- `docs/V5/V5_3_R2_5_4_BACKUP_AND_WORKTREE_CLEANUP.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

---

# PARTE A — GUARDIÁN DE EXTRACTION CACHE

## 4. Problema pendiente

R2.5 dejó como `CURRENT_PHASE`:

los módulos de formato/contrato de la extraction cache no están protegidos por un guardián automático.

Riesgo:

un cambio en:

- formato de shard;
- estructura de entrada;
- campos obligatorios;
- serialización;
- clave;
- semántica de cache_bypass;
- interpretación de registros;

podría dejar caches viejas técnicamente parseables pero semánticamente incompatibles si el desarrollador olvida subir una versión.

---

## 5. Diseño esperado del guardián

Añadir una versión o fingerprint explícito para el contrato de extraction cache.

Preferencia:

`EXTRACTION_CACHE_SCHEMA_VERSION`

o equivalente claramente separado de:

- `ANALYZER_VERSION`;
- `ANALYZER_CODE_FINGERPRINT`;
- `EVIDENCE_SCHEMA_VERSION`;
- `CACHE_MANIFEST_SCHEMA_VERSION`.

No meter indiscriminadamente todo `cache/` dentro de `ANALYZER_CODE_FINGERPRINT`.

La extraction cache tiene contrato propio y debe versionarse como tal.

---

## 6. Qué debe cubrir el guardián

Debe reaccionar ante cambios relevantes en:

- `cache/extraction.py`;
- `cache/extraction_shards.py`;
- estructura de registros cacheados;
- campos de clave;
- reglas de cache_bypass;
- formato JSON de shard;
- lógica de parseo compatible/incompatible.

No tiene que reaccionar a:

- comentarios;
- docstrings;
- logging;
- cambios internos que no alteren contrato persistido;

si la estrategia elegida puede distinguirlos de forma mantenible.

Si no es razonable distinguirlos:

usar una estrategia conservadora y documentarlo.

---

## 7. Integración del guardián

`CACHE_MANIFEST.json` debe incluir la versión/fingerprint del contrato de extraction cache.

Compatibilidad:

- mismo contrato → reutilización posible;
- contrato distinto → extraction cache no reutilizable;
- fallback seguro a extracción completa;
- no error fatal.

No debe invalidar necesariamente:

- File State;
- identidad de repositorio;
- otros metadatos compatibles.

---

## 8. Tests del guardián

Añadir tests para:

1. versión presente en manifest;
2. misma versión → compatible;
3. versión distinta → extraction cache invalidada;
4. manifest antiguo sin campo → extracción completa segura;
5. File State puede seguir siendo válido aunque extraction cache no lo sea;
6. cambio de renderer/template no invalida extraction cache;
7. cambio de Git no invalida;
8. guard test/documentación que obligue a revisar versión si cambia contrato persistido.

---

# PARTE B — WRITE-SKIP DE SALIDAS RESTANTES

## 9. Objetivo del write-skip

Evitar escrituras idénticas al disco en las salidas restantes.

Regla:

- siempre generar el contenido esperado;
- comparar contra archivo existente;
- si bytes idénticos:
  - no escribir;
- si difieren:
  - escritura atómica;
- no confiar en `mtime`;
- no confiar en tamaño solamente;
- no usar cache previa como autoridad de contenido.

---

## 10. Salidas objetivo

Auditar e implementar write-skip para las salidas generadas por:

### A. `index/`

Incluye los JSON generados por el pipeline principal.

### B. Evidence Core

Archivos bajo:

`evidence/`

### C. `consumer_projection/`

### D. `flujos_humanos/`

o la ruta vigente equivalente de documentación humana legacy.

### E. `ai_context/`

### F. documentación legacy adicional

Cualquier salida documental persistida fuera de `documentation_v52/` que actualmente se reescriba completa aunque los bytes sean idénticos.

`documentation_v52/` ya tiene su write-skip de R2.2 y NO debe reimplementarse.

---

## 11. Exclusiones explícitas

No aplicar write-skip ciego a archivos con campos intencionalmente no deterministas.

Revisar especialmente:

- `repository.json`;
- `RUN_SUMMARY.*`;
- timestamps;
- duration_seconds;
- generated_at;
- cualquier manifest con metadata temporal.

Para cada salida no determinista:

- documentar por qué;
- decidir si se excluye;
- o si puede separarse metadata determinista/no determinista sin cambiar contrato.

No cambiar contratos existentes solo para mejorar write-skip.

---

## 12. Helper reutilizable

Preferencia:

crear/reutilizar una utilidad única de escritura:

conceptualmente:

`write_if_changed(path, bytes/text, ...)`

Debe:

1. generar bytes finales exactos;
2. leer destino existente si existe;
3. comparar bytes;
4. skip si idénticos;
5. escribir atómicamente si difieren;
6. crear directorios cuando corresponda;
7. respetar MAX_PATH/long-path behavior vigente;
8. no dejar `.tmp`.

Evitar duplicar lógica por renderer.

---

## 13. Contadores

Por stage/salida registrar:

- generated;
- written;
- skipped_identical;
- bytes_generated;
- bytes_written;
- compare_seconds;
- write_seconds.

No crear todavía `RUN_METRICS.json`.

Puede ir a:

- logs;
- estructuras internas;
- reportes existentes si no altera contratos.

No modificar `RUN_SUMMARY` salvo que sea estrictamente aditivo y contractualmente seguro; preferiblemente no tocarlo en esta ronda.

---

## 14. Correctitud

Write-skip jamás debe alterar:

- orden;
- contenido;
- formato;
- IDs;
- manifests existentes;
- Evidence Core;
- documentación;
- resolvers;
- cache keys.

Una corrida cold y una corrida warm deben producir el mismo árbol lógico.

Eliminar una salida y rerun:

- debe recrearla correctamente.

Editar externamente una salida y restaurar mtime/tamaño:

- debe detectarse por comparación de bytes;
- debe reescribirse.

---

## 15. Atomicidad

Toda escritura real debe ser atómica usando las utilidades existentes.

No introducir:

- escritura parcial;
- overwrite directo no seguro;
- dependencia de rename no portable sin manejo existente.

Si ya existe `atomic_write_bytes`, preferirlo.

---

## 16. MAX_PATH

Debe mantenerse el comportamiento de R2.2:

- preflight cuando corresponda;
- `--long-paths` respetado;
- rutas lógicas/manifests sin prefijos internos;
- no introducir regresiones.

---

## 17. Salidas grandes

Para archivos grandes:

- evitar duplicaciones de memoria innecesarias;
- medir coste de comparación;
- no hacer hashing adicional si comparar bytes ya es suficiente y más barato;
- si se usa streaming, garantizar equivalencia exacta.

No optimizar prematuramente sin medición.

---

## 18. Tests unitarios mínimos

Cubrir:

1. archivo no existe → write;
2. archivo idéntico → skip;
3. archivo distinto → write;
4. mismo tamaño/diferente contenido → write;
5. mtime restaurado → write si bytes cambian;
6. archivo vacío;
7. Unicode;
8. bytes binarios si aplica;
9. atomicidad;
10. fallo de escritura;
11. cleanup de temporal;
12. long path;
13. deterministic counters;
14. helper no altera saltos de línea.

---

## 19. Tests por salida

Para cada familia:

### index

- cold escribe;
- warm skip donde determinista;
- cambio real reescribe solo afectadas.

### evidence

- warm skip;
- output byte-identical;
- corrupción externa se corrige.

### consumer_projection

- warm skip;
- contenido idéntico.

### flujos_humanos / documentación humana

- warm skip;
- contenido idéntico.

### ai_context

- warm skip;
- contenido idéntico.

### legacy docs restantes

- warm skip;
- contenido idéntico.

---

## 20. Integración con extraction cache

Warm run esperado:

- extraction cache reutiliza extracción;
- resolvers se recomputan;
- proyecciones se regeneran;
- write-skip evita escrituras idénticas.

No usar la extraction cache para decidir que una salida no necesita regenerarse.

---

## 21. Integración con File State

File State NO autoriza saltar generación de salidas.

Puede informar métricas, pero la decisión de write-skip se toma por comparación del contenido final.

---

## 22. Validación IST obligatoria

Usar:

`C:\Users\cgalianj\source\IST_40\Operacional`

No modificar IST oficial.

### A. Cold

Salida nueva.

Registrar por familia:

- cantidad generada;
- escrita;
- skipped;
- tiempo de render/generación;
- comparación;
- escritura;
- bytes escritos;
- total pipeline.

### B. Warm sin cambios

Misma salida.

Esperado:

- alta proporción de `skipped_identical`;
- contenido lógico idéntico;
- solo outputs intencionalmente no deterministas pueden reescribirse.

Registrar:

- archivos evitados;
- bytes evitados;
- tiempo por familia;
- total pipeline.

### C. Corrupción controlada de outputs

Sobre copia/salida de prueba:

Modificar externamente:

- 1 archivo index;
- 1 evidence;
- 1 consumer_projection;
- 1 ai_context;
- 1 documentación humana.

Mantener, cuando sea posible:

- mismo tamaño;
- mtime restaurado.

Rerun:

- todos deben ser detectados y corregidos.

### D. Borrado controlado

Eliminar archivos seleccionados.

Rerun:

- recreados correctamente.

---

## 23. Comparación completa

Comparar cold vs warm:

- número de archivos;
- bytes;
- hashes;
- manifests;
- documentación;
- Evidence Core;
- índices;
- proyecciones.

Excluir únicamente campos/archivos previamente declarados no deterministas.

Toda divergencia nueva:

`V5_3_R2_6_BLOCKED`

---

## 24. Gate de rendimiento

Medir beneficio real.

No hace falta exigir porcentaje fijo.

Debe demostrarse al menos que:

- warm reduce escrituras;
- no empeora materialmente el tiempo total;
- no introduce costo de comparación mayor que el ahorro de I/O en IST.

Si una familia concreta empeora:

- puede quedar sin write-skip;
- documentar decisión por familia.

No forzar una optimización que no ayuda.

---

## 25. Mantenibilidad

Revisar:

- tamaño de módulos modificados;
- complejidad;
- duplicación;
- dependencias;
- imports;
- responsabilidades.

Evitar volver a inflar `full_pipeline.py`.

Preferir helpers pequeños y módulos cohesivos.

---

## 26. Seguridad

Write-skip no debe:

- leer archivos fuera del output esperado;
- seguir paths provenientes de manifest no confiable;
- exponer secretos;
- persistir contenido adicional;
- alterar permisos de forma inesperada.

Mantener rutas normalizadas y límites actuales.

---

## 27. Suite completa

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

## 28. Git

Solo consultas.

NO:

- commit;
- tag;
- push;
- amend;
- rebase.

Registrar:

- rama;
- HEAD;
- rama backup;
- archivos modificados/nuevos;
- documentos pendientes.

---

## 29. Deuda técnica

Clasificar:

- BLOCKING;
- CURRENT_PHASE;
- NEXT_ROUND;
- FUTURE_PHASE;
- OBSERVATION.

Revisar especialmente:

- outputs no deterministas;
- duplicación de helpers de escritura;
- coste de comparar archivos grandes;
- oportunidades futuras de manifest/hashes;
- crecimiento de `full_pipeline.py`;
- outputs todavía no cubiertos;
- necesidad o no de write-skip adicional;
- interacción con cache-dir por default;
- guardián de extraction cache.

---

## 30. Fuera de alcance

NO:

- iniciar R2.7;
- cachear resolvers;
- cachear flows;
- saltar proyecciones;
- skip de stages;
- `artifacts.json`;
- `RUN_METRICS.json`;
- nuevos controles CLI;
- cambiar IDs;
- cambiar Evidence Core;
- modificar extracción salvo integración del guardián;
- IA;
- commit/push/tag.

---

## 31. Entregable

Crear:

`docs/V5/V5_3_R2_6_WRITE_SKIP_REMAINING_OUTPUTS.md`

Debe incluir:

1. Objetivo.
2. Estado de partida.
3. Guardian extraction cache.
4. Versión/fingerprint elegida.
5. Compatibilidad/fallback.
6. Archivos modificados.
7. Helper write-if-changed.
8. Salidas cubiertas.
9. Salidas excluidas y motivo.
10. Atomicidad.
11. MAX_PATH.
12. Contadores.
13. Tests unitarios.
14. Tests por familia.
15. Suite completa.
16. IST cold.
17. IST warm.
18. Corrupción controlada.
19. Borrado controlado.
20. Equivalencia cold/warm.
21. Gate de rendimiento por familia.
22. Beneficio total.
23. Mantenibilidad.
24. Seguridad.
25. Deuda técnica.
26. Riesgos.
27. Fuera de alcance confirmado.
28. Estado Git.
29. Recomendación para siguiente ronda.
30. Estado final.

---

## 32. Estados finales permitidos

Si guardián + write-skip quedan correctos y medidos:

`V5_3_R2_6_READY_FOR_REVIEW`

Si alguna familia se difiere por medición pero el resto queda correcto:

`V5_3_R2_6_READY_FOR_REVIEW`

y documentar explícitamente:

`WRITE_SKIP_DEFERRED_FOR_<FAMILY>`

Si hay divergencia, regresión, corrupción no detectada, tests fallidos o guardián inseguro:

`V5_3_R2_6_BLOCKED`

---

## 33. Criterio de cierre

R2.6 está lista si:

- extraction cache tiene guardián propio;
- caches antiguas incompatibles hacen fallback seguro;
- write-skip se aplica solo donde aporta;
- contenido final sigue siendo equivalente;
- corrupción externa se detecta por bytes;
- borrados se regeneran;
- no se saltan stages;
- no se confía en mtime;
- atomicidad se conserva;
- MAX_PATH no regresa;
- suite verde;
- IST medido;
- no se amplió alcance.

Detenerse para revisión humana.
