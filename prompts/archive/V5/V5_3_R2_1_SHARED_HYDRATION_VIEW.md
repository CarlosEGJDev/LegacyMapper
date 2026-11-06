# LegacyMapper V5.3 — R2.1 HydrationView compartida

## 1. Objetivo

Implementar únicamente la mejora de hidratación definida en V5.3 R1:

- construir una vista indexada una sola vez por corrida;
- reutilizarla entre consumidores;
- evitar reconstruir diccionarios y recorrer todos los paths en cada `hydrate_flow`;
- asegurar que cada flow se hidrate como máximo una vez por corrida cuando varios consumidores necesitan el mismo resultado.

Esta ronda NO implementa caché persistida.

## 2. Fuentes obligatorias

Leer antes de modificar código:

- `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md`
- `docs/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md`
- `docs/V5/V5_3_R1_INCREMENTAL_CACHE_CONTRACT.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

La decisión contractual relevante está en R1 §6.D:

- `HydrationView` compartida por corrida;
- índices construidos una vez;
- memoización por `flow_id`;
- salida idéntica a la hidratación actual;
- sin persistencia en disco;
- sin cambio de `MODEL_VERSION`.

## 3. Hechos medidos que deben guiar esta ronda

R0.1/R1 midieron:

- 12.642 flows;
- 25.284 llamadas actuales a `hydrate_flow` = 2 × 12.642;
- hidratación acumulada ≈ 1.099 s;
- causa principal: reconstrucción repetida de índices y recorridos globales;
- `CALL_RESOLUTION` y `FLOW_RESOLUTION` no son el cuello;
- prototipo indexado mostró una reducción muy grande sin cambiar la salida.

R1 fijó como criterio de aceptación:

- salida byte-idéntica para consumidores afectados;
- hidratación total IST ≤ 200 s;
- `flows_hydrated = 12.642`.

## 4. Alcance permitido

Modificar únicamente lo necesario para:

1. introducir `HydrationView` o equivalente;
2. construir índices una sola vez por corrida;
3. reutilizar esos índices desde `EvidenceHydrator`;
4. memoizar resultados por `flow_id` dentro de la corrida;
5. compartir la misma instancia entre:
   - `consumer_projection`;
   - `HUMAN_DOCUMENTATION` / `flujos_humanos`;
   - `ai_context` / `ai_projection`, si actualmente consumen hidratación;
6. indexar también parámetros por `caller` para evitar recorridos completos repetidos;
7. añadir tests;
8. añadir métricas de caracterización necesarias para verificar que no se hidrata dos veces.

No ampliar el alcance.

## 5. Fuera de alcance

NO implementar:

- caché persistida;
- `_cache_v53/`;
- `CACHE_MANIFEST.json`;
- `file_state.json`;
- extraction cache;
- fingerprints;
- versiones nuevas del analizador;
- write-skip;
- MAX_PATH;
- nuevas opciones CLI;
- cambios de IDs;
- cambios de Evidence Core;
- cambios de manifests;
- cambios de `CallResolver`;
- análisis incremental;
- scopes;
- IA.

## 6. Contrato de salida

La nueva hidratación debe producir el mismo resultado lógico y serializado que la anterior.

Debe conservar exactamente:

- campos;
- IDs;
- orden canónico;
- `provenance`;
- `model_version`;
- `confirmed/inferred/unresolved`;
- relaciones;
- paths;
- parámetros;
- data access;
- stored procedures;
- SQL operations.

No subir `EvidenceHydrator.MODEL_VERSION` si el contrato de salida no cambia.

## 7. Diseño mínimo esperado

### A. Índices por corrida

Construir una sola vez, como mínimo:

- `flow_id -> flow`
- `entry_point_id -> entry_point`
- `data_access_id -> data_access`
- `stored_procedure_id -> stored_procedure`
- `sql_operation_id -> sql_operation`
- `flow_id -> [paths]`
- `caller -> [data_parameters]`

Usar estructuras deterministas.

### B. Memoización

La misma `HydrationView` debe poder:

- hidratar un flow;
- devolver el resultado ya calculado si el mismo `flow_id` se solicita otra vez;
- no compartir objetos mutables que un consumidor pueda modificar y contaminar a otro.

Si el resultado necesita copia defensiva, medir y justificar.

### C. Integración

Evitar crear una `HydrationView` nueva por consumidor.

La instancia debe nacer a nivel de corrida/stage orchestration y ser pasada o compartida explícitamente.

No introducir estado global mutable.

## 8. Compatibilidad

Preservar:

- comportamiento `full`;
- runtime independence;
- ejecución sin IA;
- salida V5.2/V5.3 actual;
- tests existentes;
- orden determinista;
- manejo de unresolved.

No leer:

- docs;
- prompts;
- tests desde runtime;
- `PROJECT_STATE.json`;
- gobernanza.

## 9. Tests obligatorios

Crear tests dirigidos para:

1. salida de hidratación anterior vs nueva en fixture pequeño;
2. todos los campos relevantes;
3. mismo flow pedido dos veces;
4. dos consumidores usando la misma vista;
5. ausencia de contaminación por mutación;
6. parámetros por `caller`;
7. flow sin paths;
8. flow con unresolved;
9. flow con data access / stored procedure / SQL;
10. determinismo;
11. runtime independence;
12. no cambio de `MODEL_VERSION`.

Además, sobre IST:

- comparar hidratación nueva vs implementación anterior para **los 12.642 flows**;
- usar JSON canónico o comparación estructural completa;
- cualquier diferencia bloquea la ronda.

## 10. Medición obligatoria IST

Ejecutar una corrida controlada sobre:

`C:\Users\cgalianj\source\IST_40\Operacional`

Sin IA.

Medir como mínimo:

- tiempo de construcción de `HydrationView`;
- tiempo total de hidratación;
- cantidad de flows hidratados;
- cantidad de hits de memoización;
- cantidad total de solicitudes de hidratación;
- tiempo de `consumer_projection`;
- tiempo de `HUMAN_DOCUMENTATION`;
- tiempo total de la corrida;
- memoria pico.

Separar, si es posible:

- tiempo frío;
- tiempo caliente.

No hacer más corridas completas de las necesarias.

## 11. Criterios de aceptación

La ronda puede cerrarse solo si:

1. todos los tests dirigidos pasan;
2. suite completa pasa;
3. los 12.642 flows de IST son equivalentes a la implementación anterior;
4. `flows_hydrated` real = 12.642;
5. no hay doble hidratación completa;
6. tiempo total de hidratación IST ≤ 200 s;
7. `consumer_projection` y `HUMAN_DOCUMENTATION` mejoran materialmente respecto a R0.1;
8. salida de consumidores afectados es byte-idéntica donde corresponda;
9. no cambian manifests, IDs ni Evidence Core;
10. no se introduce caché persistida.

Si el tiempo supera 200 s pero la salida es correcta, NO falsear el resultado: marcar bloqueo o pedir decisión humana con los datos.

## 12. Suite

Ejecutar:

- tests dirigidos nuevos;
- tests de hydration/context/documentation relacionados;
- suite completa:
  `python -m unittest discover -s tests`

Registrar:

- total;
- fallas;
- errores;
- skips;
- duración.

## 13. Deuda técnica

Clasificar cualquier hallazgo como:

- BLOCKING;
- CURRENT_PHASE;
- NEXT_ROUND;
- FUTURE_PHASE;
- OBSERVATION.

No corregir deuda ajena a R2.1.

## 14. Git

Solo consultas.

No commit, tag ni push.

Registrar archivos modificados y sin versionar.

No tocar todavía los pendientes administrativos salvo que el cambio sea necesario para este informe.

## 15. Entregable

Crear:

`docs/V5/V5_3_R2_1_SHARED_HYDRATION_VIEW.md`

Debe incluir:

1. Resumen de implementación.
2. Archivos modificados.
3. Diseño final de `HydrationView`.
4. Cómo se comparte entre consumidores.
5. Cómo se evita doble hidratación.
6. Compatibilidad de salida.
7. Tests dirigidos.
8. Comparación completa de los 12.642 flows.
9. Suite completa.
10. Métricas IST antes/después.
11. Memoria pico.
12. Deuda técnica.
13. Riesgos.
14. Confirmación de fuera de alcance.
15. Estado Git.
16. Estado final.

## 16. Estados finales permitidos

Si todo cumple:

`V5_3_R2_1_READY_FOR_REVIEW`

Si hay diferencias de salida, tests fallidos o no se cumple un criterio crítico:

`V5_3_R2_1_BLOCKED`

No usar otro estado.

## 17. Restricciones finales

No:

- iniciar R2.2;
- implementar caché persistida;
- hacer write-skip;
- resolver MAX_PATH;
- añadir fingerprints;
- cambiar IDs;
- cambiar Evidence Core;
- ejecutar IA;
- commit/push.

Detenerse para revisión humana.
