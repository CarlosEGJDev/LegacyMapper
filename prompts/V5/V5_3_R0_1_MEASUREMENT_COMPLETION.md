# LegacyMapper V5.3 — R0.1 Completar mediciones y continuidad

## 1. Objetivo

Completar las mediciones faltantes de V5.3 R0 y corregir pequeñas inconsistencias de continuidad antes de diseñar R1.

Esta ronda sigue siendo de diagnóstico.

NO implementar todavía:

- caché;
- análisis incremental;
- invalidación;
- nuevos índices persistidos;
- scopes nuevos;
- cambios de arquitectura.

## 2. Estado de partida

V5.2 está cerrada y publicada.

Commit V5.2:

`6c32c4c9c6fe2642e56e9f33739a95d43d6ae411`

Tag:

`v5.2`

R0 terminó en:

`V5_3_R0_READY_FOR_CONTRACT`

Documento R0:

`docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md`

Baseline oficial IST:

`C:\Users\cgalianj\source\IST_40\Operacional`

## 3. Correcciones de continuidad

### A. Corregir observación desactualizada de R0

R0 indica que `PROJECT_STATE.json` todavía tenía un riesgo histórico desactualizado sobre la intermitencia de escritura.

Eso ya fue corregido en V5.2 R4.4.

Actualizar únicamente el informe R0 para que refleje el estado real actual:

- la causa fue identificada;
- la corrección fue aplicada;
- existe cobertura de tests;
- el estado ya no está pendiente.

No modificar `PROJECT_STATE.json` salvo que aparezca evidencia nueva.

### B. Convención de prompts

Desde V5.3, los prompts nuevos deben estar en:

`prompts/V5/`

El prompt de R0 quedó en:

`prompts/V5_0/V5_3_R0_EMPIRICAL_BASELINE.md`

Moverlo a:

`prompts/V5/V5_3_R0_EMPIRICAL_BASELINE.md`

No mover prompts históricos anteriores a V5.3.

Este prompt R0.1 debe guardarse en:

`prompts/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md`

### C. Archivos administrativos pendientes

Revisar si siguen sin versionar:

- `docs/V5/V5_2_GIT_CLOSURE_RESULT.md`
- `docs/V5/V5_3_R0_EMPIRICAL_BASELINE.md`
- prompt R0
- este prompt R0.1

No hacer commit ni push en esta ronda.

Solo registrar qué quedará pendiente de versionado después de la revisión humana.

## 4. Medición real por etapa

R0 detectó que faltan tiempos exactos por etapa.

Ejecutar una única corrida controlada sobre el baseline IST oficial:

`C:\Users\cgalianj\source\IST_40\Operacional`

### Requisitos

Instrumentar temporalmente la medición sin alterar contratos persistidos.

Registrar como mínimo:

- SCAN;
- EXTRACTION;
- CALL_RESOLUTION;
- WEB_ENTRY_RESOLUTION;
- DATABASE_RESOLUTION;
- FLOW_RESOLUTION;
- DEPENDENCY_RESOLUTION;
- EXPORT;
- Evidence Core;
- CONTEXT;
- DOCUMENTATION legacy;
- HUMAN_DOCUMENTATION;
- documentation_v52;
- FINAL_SUMMARY.

Registrar:

- duración por etapa;
- duración total;
- cantidad de archivos leídos/escritos cuando sea posible;
- memoria pico si puede medirse sin modificar arquitectura;
- estado de salida del proceso;
- tiempo entre `FINAL_SUMMARY` y terminación real.

No ejecutar IA.

### Process exit

Al final registrar:

- threads vivos;
- procesos hijos;
- tiempo hasta salida real;
- exit code.

Si la medición requiere código temporal, debe quedar fuera de producción y eliminarse al terminar.

## 5. Experimentos de impacto incremental

Trabajar sobre una COPIA del baseline IST fuera del repositorio original.

No modificar el baseline oficial.

Preparar entre 3 y 5 cambios representativos:

1. cambio solo en cuerpo de método;
2. cambio de firma o nombre de método;
3. cambio en `.aspx` o `.ascx`;
4. cambio en `.vbproj`;
5. archivo nuevo o eliminado.

Para cada cambio medir o calcular:

- archivos detectados como cambiados;
- proyectos potencialmente afectados;
- símbolos afectados;
- llamadas que pueden requerir nueva resolución;
- flows potencialmente afectados;
- documentos potencialmente afectados;
- si el alcance puede ser local o debe ampliarse a repository.

No implementar invalidación todavía.

El objetivo es medir el impacto real.

## 6. Decisión sobre line endings

Evaluar de forma reproducible:

- hash de bytes crudos;
- hash normalizado LF/CRLF.

Documentar:

- qué cambios serían falsos positivos;
- qué cambios podrían convertirse en falsos negativos;
- recomendación para R1.

No cambiar todavía el contrato de hash.

## 7. Versión del analizador

Proponer, sin implementar todavía, cómo representar una versión estable que pueda entrar en la clave de caché.

Debe considerar por separado cuando sea necesario:

- analyzer version;
- evidence schema version;
- renderer version;
- template/profile version.

No reutilizar Git commit como única versión del analizador salvo justificación.

## 8. Resolución global de llamadas

Analizar qué cambios en `symbols` y `calls` obligan realmente a recalcular `CallResolver`.

Distinguir, si la evidencia lo permite:

- cambio solo de cuerpo;
- cambio de firma;
- cambio de nombre;
- símbolo nuevo;
- símbolo eliminado;
- namespace;
- clase parcial;
- llamadas nuevas/eliminadas.

Objetivo:

reducir invalidación global cuando sea seguro.

No modificar `CallResolver`.

## 9. Compatibilidad incremental vs full

Confirmar y documentar como contrato propuesto:

`mismo input + misma versión + misma configuración`
→ salida incremental final equivalente a una corrida full.

Definir qué significa equivalente:

- mismos IDs;
- mismas relaciones;
- mismos estados unresolved;
- mismas particiones lógicas;
- misma documentación;
- mismos manifests salvo métricas no deterministas.

No implementar todavía esta comparación.

## 10. Deuda técnica

Aplicar la regla actual:

- arreglar deuda evitable cuando sea razonable;
- pero esta ronda es de medición.

Clasificar hallazgos como:

- BLOCKING;
- CURRENT_PHASE;
- NEXT_ROUND;
- FUTURE_PHASE;
- OBSERVATION.

No corregir código en esta ronda.

## 11. Git

Puede ejecutar consultas:

```bat
git status
git diff --stat
git branch --show-current
git log -1 --oneline
```

No:

- commit;
- tag;
- push;
- reset;
- rebase;
- checkout destructivo.

## 12. Entregable único

Crear:

`docs/V5/V5_3_R0_1_MEASUREMENT_COMPLETION.md`

Debe incluir:

1. Correcciones de continuidad realizadas.
2. Estado de prompts.
3. Archivos pendientes de Git.
4. Tiempos reales por etapa.
5. Duración total.
6. Estado de process exit.
7. Experimentos de impacto incremental.
8. Resultado de line endings.
9. Propuesta de versionado del analizador.
10. Alcance real de `CallResolver`.
11. Contrato propuesto incremental vs full.
12. Riesgos.
13. Deuda técnica clasificada.
14. Datos suficientes o insuficientes para R1.
15. Archivos modificados.
16. Confirmación de que no se implementó caché ni análisis incremental.

## 13. Estados finales permitidos

Si ya existe suficiente evidencia para diseñar R1:

`V5_3_R0_1_READY_FOR_CONTRACT`

Si faltan datos críticos:

`V5_3_R0_1_BLOCKED`

## 14. Restricciones

No:

- modificar producción;
- modificar Evidence Core;
- cambiar IDs;
- cambiar manifests;
- implementar cache;
- implementar incremental;
- ejecutar IA;
- iniciar R1;
- hacer commit/push.

Detenerse para revisión humana.
