# LegacyMapper V5.3 — R1 Contrato y diseño del motor incremental y caché

## 1. Objetivo

Definir el contrato y diseño de V5.3 — Incremental Engine & Cache antes de implementar.

Esta ronda debe convertir las mediciones de R0/R0.1 en decisiones explícitas de arquitectura, contratos, invariantes, fallback y criterios de aceptación.

NO implementar todavía:

- caché real;
- análisis incremental;
- invalidación en producción;
- nuevos índices persistidos;
- cambios en Evidence Core;
- cambios en IDs;
- refactors de producción;
- optimizaciones de renderer;
- cambios en CallResolver;
- cambios en manifests existentes salvo definición contractual.

## 2. Fuentes obligatorias

Leer como base:

- `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md`
- `docs/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md`
- `docs/V5/V5_2_R4_3_CIERRE_FORMAL.md`
- `docs/V5/V5_2_R4_4_AJUSTE_FINAL_ESTADO_Y_GIT.md`
- `docs/V5/V5_1_R4_CIERRE_FINAL.md`
- `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`
- `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`
- `docs/continuity/LEGACYMAPPER_LESSONS_LEARNED.md`
- `docs/continuity/ASSISTANT_WORKING_RULES_AND_PREFERENCES.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

No reemplazar estas decisiones con supuestos generales.

## 3. Estado confirmado

V5.2 está cerrada y publicada.

Commit:

`6c32c4c9c6fe2642e56e9f33739a95d43d6ae411`

Tag:

`v5.2`

Baseline oficial IST:

`C:\Users\cgalianj\source\IST_40\Operacional`

R0.1 terminó en:

`V5_3_R0_1_READY_FOR_CONTRACT`

V5.3 todavía no está implementada.

## 4. Hechos que el contrato debe respetar

De R0/R0.1:

1. Aproximadamente 92 % del tiempo de una corrida completa está en proyecciones derivadas.
2. La hidratación duplicada de 12.642 flows consume aproximadamente 62,6 % del tiempo total.
3. `CALL_RESOLUTION` completo cuesta aproximadamente 1 segundo.
4. `FLOW_RESOLUTION` completo cuesta aproximadamente 9 segundos.
5. `documentation_v52` genera 46.567 Markdown y tarda aproximadamente 486 segundos.
6. No existe hoy caché real.
7. `SourceArtifact.sha256`, `EVIDENCE_MANIFEST.partition_sha256` y `documentation_v52/MANIFEST.json` son activos reutilizables.
8. La heurística simple “flow toca archivo” no es fiable para invalidación.
9. Un cambio de nombre puede cruzar proyectos.
10. Un cambio de cuerpo puede alterar IDs de llamadas por desplazamiento de líneas.
11. La ruta de salida puede fallar por MAX_PATH en Windows.
12. El proceso no reprodujo el problema histórico de salida tardía en una corrida IST controlada.
13. El hash crudo detecta cambios de line endings; la extracción no cambia ante CRLF/LF en los tipos analizados.
14. El BOM sí puede alterar la extracción.
15. Ante duda, el fallback seguro debe ser ampliar el alcance o ejecutar full.

## 5. Principios de diseño obligatorios

### 5.1 Determinismo

Para el mismo:

- input;
- versión del analizador;
- esquema;
- configuración;
- templates/perfiles;
- idioma;

la salida incremental debe ser equivalente a una corrida full.

### 5.2 Evidencia primero

No cambiar:

- IDs;
- provenance;
- confidence;
- unresolved;
- contratos de Evidence Core V5.1.

### 5.3 Fallback seguro

Si no existe evidencia suficiente para reutilizar una unidad:

`fallback → recomputar`

Nunca reutilizar caché dudosa.

### 5.4 IA fuera del mecanismo incremental

No usar IA para:

- fingerprints;
- invalidación;
- dependencias afectadas;
- selección de caché;
- decisión full vs incremental.

## 6. Contrato de versionado

Definir formalmente:

### ANALYZER_VERSION

Cubre cambios en:

- extractores;
- resolución de llamadas;
- resolución de entry points;
- resolución de base de datos;
- resolución de flows;
- dependencias;
- normalización de namespaces;
- partial classes.

Debe cambiar cuando una modificación pueda alterar índices o evidencia.

### EVIDENCE_SCHEMA_VERSION

Reutilizar el contrato existente de V5.1.

No inventar una segunda versión equivalente si ya existe una oficial.

### RENDERER_VERSION

Definir versión para familias de salida cuando corresponda:

- documentación legacy;
- HUMAN_DOCUMENTATION;
- consumer projection;
- ai_context;
- documentation_v52.

Puede ser una versión única o varias, pero justificar la decisión.

### TEMPLATE_PROFILE_VERSION

Preferir fingerprint determinista del contenido de:

- templates;
- profiles;
- idioma;
- configuración de presentación.

### CONFIG_FINGERPRINT

Debe cubrir como mínimo:

- excludes;
- `flow_max_depth`;
- opciones que cambian análisis;
- cualquier configuración relevante para evidencia o proyección.

El commit Git puede registrarse como metadata, pero no debe ser la única clave de caché.

## 7. Contrato de fingerprint

Definir dos conceptos separados:

### Hash de integridad

Mantener el hash crudo actual para:

- integridad;
- compatibilidad;
- trazabilidad.

### Hash semántico para invalidación

Definir si se adopta:

- solo para tipos de texto analizados;
- CRLF/CR normalizado a LF;
- BOM preservado;
- espacios preservados.

Debe quedar explícito:

- cuándo se usa;
- cuándo NO se usa;
- cómo convive con `SourceArtifact.sha256`;
- qué pasa con archivos binarios.

No modificar `SourceArtifact.sha256` existente en esta ronda.

## 8. Arquitectura propuesta de caché

Diseñar una estructura clara.

Como mínimo, definir capas:

### A. File State

Por archivo:

- path;
- tamaño;
- hash crudo;
- hash semántico;
- tipo;
- proyecto;
- estado: added / modified / deleted / renamed / unchanged.

### B. Extraction Cache

Unidad principal:

`archivo`

Debe poder reutilizar:

- symbols;
- calls crudas;
- web events;
- data access indexes;
- webforms;
- configuration;
- metadata de extracción.

Definir cómo se relaciona con proyectos y partial classes.

### C. Resolver State

No priorizar invalidación fina si el coste completo es bajo.

Diseñar explícitamente si:

- CALL_RESOLUTION se recalcula siempre a partir de extracción cacheada;
- FLOW_RESOLUTION se recalcula siempre;
- o se permite invalidación parcial en una fase posterior.

La decisión debe basarse en R0.1: CALL_RESOLUTION ≈ 1 s; FLOW_RESOLUTION ≈ 9 s.

### D. Hydrated Flow Cache

Debe ser prioridad alta.

Definir:

- unidad de caché;
- clave;
- dependencias;
- cuándo se invalida;
- cómo compartir el resultado entre:
  - consumer_projection;
  - HUMAN_DOCUMENTATION;
  - ai_context;
  - otros consumidores futuros.

Objetivo: evitar las dos hidrataciones completas observadas.

### E. Projection Cache

Definir caché/reutilización para:

- documentation_v52;
- HUMAN_DOCUMENTATION;
- consumer_projection;
- ai_context.

Evitar una estrategia que obligue a abrir 46.567 archivos para decidir qué reutilizar.

Preferir manifests/particiones grandes.

## 9. Persisted Cache Manifest

Diseñar un manifest de caché persistido.

Debe incluir como mínimo:

- cache schema version;
- analyzer version;
- evidence schema version;
- renderer version(es);
- template/profile fingerprint;
- config fingerprint;
- baseline repository identity;
- branch/metadata informativa;
- file fingerprints;
- artifact fingerprints;
- estado de finalización;
- checksums;
- timestamp solo como metadata no determinista;
- estado de validez.

Debe seguir el patrón seguro:

`escribir datos → validar → escribir manifest final`

Nunca considerar válida una caché sin manifest final válido.

## 10. Índices inversos

Diseñar qué índices son necesarios.

Como mínimo evaluar:

- archivo → proyecto;
- archivo → símbolos;
- símbolo → llamadas entrantes;
- símbolo/nombre → llamadas candidatas;
- archivo → flows afectados;
- proyecto → proyectos dependientes;
- flow → documentos/proyecciones;
- evidencia → documentos.

No implementar en R1.

Definir:

- cuál es obligatorio en R2;
- cuál puede posponerse;
- qué consultas debe responder.

## 11. Política de invalidación

Definir una matriz de invalidación.

Cubrir:

- cambio solo en cuerpo;
- cambio de línea;
- cambio de firma;
- cambio de nombre;
- símbolo nuevo;
- símbolo eliminado;
- namespace;
- partial class;
- `.aspx/.ascx`;
- `.vbproj`;
- `.sln`;
- `web.config`;
- archivo nuevo;
- archivo eliminado;
- rename;
- template;
- profile;
- idioma;
- configuración;
- analyzer version;
- renderer version;
- cambio de branch;
- cache corrupta.

Para cada caso indicar:

- mínimo alcance seguro;
- qué se reutiliza;
- qué se recomputa;
- cuándo se fuerza full.

## 12. Scopes

Definir contrato para:

- `repository`;
- `project`;
- `folder`;
- `component`;
- `changed`.

Prioridad recomendada:

1. `repository`
2. `changed`
3. `project`
4. `component`
5. `folder`

Justificar cualquier cambio de orden.

`folder` no debe asumirse como unidad segura de compilación.

## 13. Política full vs incremental

Definir reglas claras.

Ejemplos de full obligatorio:

- cambio de analyzer version;
- cambio de evidence schema;
- cache corrupta;
- manifest incompleto;
- cambio masivo de branch;
- configuración incompatible;
- cambio que exceda umbral seguro.

Definir un umbral razonable o dejarlo configurable.

No fijar porcentajes arbitrarios sin evidencia.

## 14. Equivalencia incremental vs full

Formalizar el contrato de R0.1:

`mismo input + misma versión + misma configuración`
→ misma salida lógica.

Debe preservar:

- mismos IDs;
- mismas relaciones;
- mismos unresolved;
- mismas particiones lógicas;
- misma documentación;
- mismos manifests lógicos.

Las métricas no deterministas deben vivir fuera de artefactos byte-estables.

## 15. Métricas

Diseñar métricas persistibles fuera de contratos byte-estables.

Como mínimo:

- tiempo por stage;
- cache hits;
- cache misses;
- archivos reutilizados;
- archivos recomputados;
- flows reutilizados;
- flows recomputados;
- documentos reutilizados;
- documentos regenerados;
- bytes leídos/escritos;
- fallback reason;
- incremental/full mode;
- tiempo total;
- peak memory si está disponible.

No mezclar métricas con outputs deterministas si rompe compatibilidad.

## 16. MAX_PATH

Definir contrato explícito para Windows.

Debe decidir una estrategia entre:

- validar longitud antes de escribir;
- usar rutas cortas internas;
- mapear rutas largas a nombres hash;
- soporte de long paths;
- combinación de las anteriores.

Requisitos:

- no perder trazabilidad;
- error claro y accionable;
- no generar `FileNotFoundError` confuso;
- diseño compatible con caché.

No implementar todavía.

## 17. IDs dependientes de línea

R0.1 demostró que algunas llamadas cambian ID al desplazarse su línea.

R1 debe decidir:

A. mantener el contrato actual de IDs y aceptar invalidación adicional;

o

B. proponer cambio de contrato para una fase posterior.

No cambiar IDs en V5.3 sin autorización explícita.

La opción por defecto debe ser preservar IDs actuales y diseñar la invalidación alrededor de ese hecho.

## 18. Persistencia

Evaluar:

- JSON actual;
- JSONL;
- SQLite u otra opción solo si está claramente justificada.

No introducir una tecnología nueva por preferencia.

Criterios:

- lectura parcial;
- escritura atómica;
- lookup por clave;
- tamaño;
- compatibilidad;
- complejidad;
- recuperación ante corrupción;
- facilidad de inspección.

Puede concluir que JSON + nuevos índices es suficiente para R2.

## 19. Runtime independence

La caché y el motor incremental deben funcionar sin depender de:

- docs;
- prompts;
- tests;
- PROJECT_STATE.json;
- governance;
- IA;
- Copilot.

## 20. Estrategia de migración

Definir cómo se comporta V5.3 cuando:

- no existe caché;
- existe caché V5.3 válida;
- existe output V5.2 pero no caché V5.3;
- cache schema cambia;
- analyzer version cambia;
- cache está dañada;
- corrida se interrumpe.

La primera ejecución sin caché debe ser full y crear estado reutilizable.

## 21. Rollback

Definir cómo desactivar V5.3.

Debe existir una forma de ejecutar:

`full sin reutilización de caché`

y obtener el comportamiento compatible anterior.

No eliminar el camino full.

## 22. Seguridad y consistencia

Definir:

- escritura atómica;
- manifest final;
- validación de checksum;
- limpieza de temporales;
- invalidación de huérfanos;
- no persistir secretos;
- no mezclar outputs de repositorios distintos.

## 23. Plan de implementación R2

R1 debe terminar con un plan concreto para R2.

Separar implementación en pasos pequeños, por ejemplo:

1. versionado + config fingerprint;
2. cache manifest;
3. file state;
4. extraction cache;
5. shared hydrated flow cache;
6. projection reuse;
7. metrics;
8. fallback full;
9. tests de equivalencia.

No implementar ninguno en R1.

## 24. Tests que R2 deberá tener

Diseñar la matriz de tests:

- cache cold;
- cache warm;
- archivo sin cambios;
- cuerpo de método;
- rename de método;
- símbolo nuevo;
- símbolo eliminado;
- `.aspx`;
- `.vbproj`;
- line endings;
- config;
- template;
- renderer version;
- analyzer version;
- cache corrupta;
- cache incompleta;
- full fallback;
- equivalencia full vs incremental;
- determinismo;
- runtime independence;
- Windows path largo.

## 25. Deuda técnica

Aplicar la regla del proyecto:

- evitar deuda evitable;
- no expandir scope sin necesidad.

Clasificar:

- BLOCKING;
- CURRENT_PHASE;
- NEXT_ROUND;
- FUTURE_PHASE;
- OBSERVATION.

R1 no debe dejar sin decisión:

- MAX_PATH;
- métricas por stage;
- versionado;
- hidratación duplicada;
- manifests de caché;
- fallback full;
- equivalencia incremental/full.

## 26. Git

Solo consultas.

No commit, tag ni push.

Registrar los archivos sin versionar actuales.

## 27. Entregable único

Crear:

`docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`

Debe incluir:

1. Objetivo.
2. Hechos empíricos usados.
3. Invariantes.
4. Versionado.
5. Fingerprints.
6. Arquitectura de caché.
7. Persisted cache manifest.
8. Índices inversos.
9. Matriz de invalidación.
10. Scopes.
11. Full vs incremental.
12. Equivalencia.
13. Métricas.
14. MAX_PATH.
15. IDs dependientes de línea.
16. Persistencia.
17. Runtime independence.
18. Migración.
19. Rollback.
20. Seguridad/consistencia.
21. Plan R2.
22. Matriz de tests R2.
23. Deuda clasificada.
24. Riesgos.
25. Archivos modificados.
26. Estado final.

## 28. Estados finales permitidos

Si el contrato es suficiente para implementar:

`V5_3_R1_CONTRACT_READY`

Si falta una decisión crítica:

`V5_3_R1_BLOCKED`

No usar otro estado.

## 29. Restricciones finales

No:

- modificar producción;
- modificar tests;
- implementar cache;
- implementar incremental;
- crear schema real en código;
- cambiar Evidence Core;
- cambiar IDs;
- ejecutar IA;
- iniciar R2;
- commit/push.

Detenerse para revisión humana.
