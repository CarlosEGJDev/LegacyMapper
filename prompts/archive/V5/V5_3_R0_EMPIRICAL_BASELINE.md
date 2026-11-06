# LegacyMapper V5.3 — R0 Baseline empírico para motor incremental y caché

## 1. Objetivo

Medir y documentar el comportamiento real actual de LegacyMapper antes de diseñar V5.3 — Incremental Engine & Cache.

Esta ronda es de diagnóstico y baseline.

NO implementar todavía:

- caché;
- análisis incremental;
- invalidación;
- índice persistido nuevo;
- scopes nuevos;
- refactors;
- cambios de arquitectura.

Primero medir.

## 2. Estado de partida

V5.2 está cerrada y publicada.

Commit de cierre V5.2:

`6c32c4c9c6fe2642e56e9f33739a95d43d6ae411`

Tag:

`v5.2`

Rama:

`main`

Baseline oficial IST:

`C:\Users\cgalianj\source\IST_40\Operacional`

V5.3 todavía no está iniciada funcionalmente.

El archivo:

`docs/V5/V5_2_GIT_CLOSURE_RESULT.md`

puede existir sin versionar porque fue creado después del commit de cierre. No resolverlo automáticamente durante R0; solo registrar su estado.

## 3. Propósito de V5.3

V5.3 debe permitir que cambios pequeños no obliguen a repetir un análisis completo.

Objetivo conceptual:

```text
cambio pequeño
→ detectar qué cambió
→ invalidar solo lo afectado
→ recomputar solo lo necesario
→ reutilizar el resto
```

Capacidades previstas:

- fingerprints/hashes;
- caché por etapa;
- invalidación determinista;
- dependencias afectadas;
- recomputación parcial;
- persisted index;
- scope analysis;
- métricas;
- observación del comportamiento de salida del proceso.

## 4. Principios obligatorios

Preservar:

- determinismo;
- provenance;
- IDs;
- unresolved;
- compatibilidad con V4.3;
- Evidence Core V5.1;
- documentación V5.2;
- runtime independence;
- provider IA opcional;
- IST como baseline real.

Regla principal:

`Python descubre y valida; la IA interpreta.`

No usar IA para decidir invalidación, hashes, dependencias afectadas ni selección de caché.

## 5. Actividades de R0

### A. Estado Git

Ejecutar:

```bat
cd /d C:\dev\LegacyMapper
git status
git branch --show-current
git log -1 --oneline
git tag -l "v5.2"
```

Registrar:

- rama;
- commit actual;
- si el árbol está limpio;
- archivos sin versionar;
- confirmar que V5.2 corresponde al tag publicado.

No modificar Git.

### B. Inventario del pipeline actual

Identificar las etapas reales que ejecuta hoy:

- `analyze`;
- `full`;
- Evidence Core;
- documentación;
- manifest;
- cualquier índice persistido existente;
- cualquier cache existente;
- etapas opcionales de IA.

Para cada etapa, documentar:

- input;
- output;
- dependencias;
- si hoy siempre se recalcula;
- si su resultado podría reutilizarse;
- qué cambio debería invalidarla.

No diseñar todavía el contrato final.

### C. Medición de artefactos persistidos

Sobre la última corrida válida de IST disponible, medir:

- cantidad de archivos de evidencia;
- tamaño total;
- cantidad de documentos V5.2;
- tamaño total;
- manifests existentes;
- índices existentes;
- archivos que ya contienen hashes;
- archivos que podrían actuar como cache natural;
- tiempo de lectura aproximado si es razonable medirlo sin repetir análisis.

No regenerar IST por rutina.

### D. Medición del costo actual

Determinar, usando evidencia existente y logs cuando sea posible:

- duración total de la última corrida completa;
- duración por etapa si está disponible;
- etapas más costosas;
- volumen de lectura/escritura;
- outputs que se regeneran aunque su input no haya cambiado.

Si faltan tiempos fiables, marcarlo como gap.

No inventar métricas.

### E. Candidatos de fingerprint

Inventariar qué entidades podrían tener fingerprint determinista:

- archivo fuente;
- proyecto;
- solución;
- evidencia normalizada;
- flow/path;
- documentación proyectada;
- configuración;
- templates;
- profiles;
- versión del analizador.

Para cada candidato, indicar:

- datos mínimos necesarios;
- estabilidad esperada;
- riesgo de falso positivo;
- riesgo de falso negativo;
- si ya existe algún hash reutilizable.

No implementar fingerprints.

### F. Dependencias e invalidación

Mapear, a nivel conceptual y basado en el sistema actual:

```text
archivo cambiado
→ qué extracción depende de él
→ qué evidencia depende de esa extracción
→ qué relaciones pueden verse afectadas
→ qué proyecciones/documentos dependen de esa evidencia
```

Identificar casos donde un archivo puede invalidar:

- solo a sí mismo;
- su proyecto;
- proyectos dependientes;
- flows;
- documentación relacionada;
- todo el repositorio.

No asumir invalidación local cuando la evidencia no lo permita.

### G. Scopes

Evaluar viabilidad de estos scopes futuros:

- repository;
- project;
- folder;
- component;
- changed.

Para cada uno:

- qué información ya existe;
- qué información falta;
- qué riesgo tiene;
- qué nivel de precisión sería razonable.

No implementar scopes.

### H. Persisted index

Revisar si el sistema actual ya tiene suficiente información persistida para construir después un índice reutilizable.

Documentar:

- qué índices existen;
- qué consultas podrían responderse sin reanalizar;
- qué falta para permitir recomputación parcial;
- qué datos deberían considerarse canónicos;
- qué datos son solo presentación.

### I. Process exit

Revisar el antecedente histórico donde un run determinista terminó con resumen de éxito pero el proceso Python permaneció vivo.

No asumir que sigue ocurriendo.

Buscar evidencia existente sobre:

- threads vivos;
- procesos hijos;
- handles;
- providers;
- logging;
- pools;
- recursos no cerrados.

Si se puede medir sin repetir una corrida costosa, hacerlo.

Si no, dejarlo como punto de medición de una futura corrida controlada.

### J. Riesgos técnicos

Identificar riesgos antes de diseñar:

- invalidación incompleta;
- cache stale;
- cambio de configuración;
- cambio de template;
- cambio de versión del analizador;
- cambio de branch;
- cambio de line endings;
- archivos renombrados;
- archivos eliminados;
- dependencias cruzadas;
- outputs parciales;
- corrupción de cache;
- compatibilidad con ejecución completa.

## 6. Deuda técnica

Aplicar la regla actual del proyecto:

- evitar deuda técnica cuando pueda corregirse razonablemente;
- pero R0 es diagnóstico, no implementación.

Clasificar hallazgos como:

- BLOCKING;
- CURRENT_PHASE;
- NEXT_ROUND;
- FUTURE_PHASE;
- OBSERVATION.

No corregirlos en esta ronda.

## 7. Lo que NO debe hacerse

No:

- modificar código de producción;
- modificar tests;
- implementar cache;
- implementar incremental analysis;
- crear nuevos schemas definitivos;
- cambiar Evidence Core;
- cambiar IDs;
- cambiar manifests existentes;
- ejecutar IA;
- modificar V5.2;
- hacer commit;
- hacer push;
- crear tags.

## 8. Validación permitida

Puede ejecutar:

- consultas Git;
- inventarios;
- scripts Python de medición;
- lectura de manifests;
- hashes;
- mediciones de tamaños;
- tests dirigidos de solo caracterización si son necesarios.

Evitar:

- nueva extracción completa IST;
- suite completa por rutina;
- procesos largos sin necesidad.

Si una nueva corrida completa resulta indispensable, detenerse primero y documentar por qué.

## 9. Entregable único

Crear:

`docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md`

Debe incluir:

1. Estado Git.
2. Baseline utilizado.
3. Pipeline actual.
4. Artefactos persistidos existentes.
5. Costos medidos.
6. Candidatos de fingerprint.
7. Mapa conceptual de invalidación.
8. Evaluación de scopes.
9. Estado de persisted indexes.
10. Estado de process exit.
11. Riesgos.
12. Deuda técnica clasificada.
13. Qué NO se midió.
14. Datos que necesita R1.
15. Recomendaciones para el contrato de R1.
16. Archivos modificados.
17. Confirmación de que no se implementó V5.3 todavía.

## 10. Estado final permitido

Si el baseline es suficiente:

`V5_3_R0_READY_FOR_CONTRACT`

Si faltan mediciones críticas:

`V5_3_R0_BLOCKED`

No usar otro estado.

## 11. Respuesta final

Responder brevemente con:

- estado final;
- principales mediciones;
- principales riesgos;
- gaps importantes;
- documento creado;
- confirmación de que no se modificó producción;
- confirmación de que no hubo commit/push;
- confirmación de que no se implementó cache ni análisis incremental.

Detenerse para revisión humana antes de R1.
