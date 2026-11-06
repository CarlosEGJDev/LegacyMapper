# LegacyMapper V5.2 — R4.3 Cierre formal y procedimiento Git

## 1. Objetivo

Ejecutar el cierre formal definitivo de V5.2 después de:

- aprobación humana de R3.4.1;
- revisión R4;
- diagnóstico R4.1;
- correcciones pre-cierre R4.2;
- suite completa R4.2 con 2.449 pruebas, 0 fallas y 0 errores.

Esta ronda es principalmente documental y administrativa.

Debe:

1. consolidar el estado final de V5.2;
2. actualizar los archivos oficiales de estado y continuidad;
3. registrar las decisiones pendientes ya resueltas;
4. corregir inconsistencias documentales detectadas;
5. establecer un procedimiento Git controlado para cierres futuros;
6. dejar V5.3 preparada para comenzar, pero NO iniciarla.

## 2. Decisiones humanas ya aprobadas

El Technical Lead aprueba:

### Baseline oficial de V5.2

`C:\Users\cgalianj\source\IST_40\Operacional`

Esta es la referencia oficial de V5.2 porque las mediciones y validaciones actuales provienen de esta ruta.

La otra ruta IST examinada no es equivalente y no debe tratarse como el mismo baseline.

### Política sobre deuda técnica

Evitar deuda técnica cuando pueda corregirse razonablemente dentro de la fase actual.

Las limitaciones que requieren nueva arquitectura, nueva extracción o fases futuras deben quedar documentadas explícitamente y no tratarse como defectos pendientes de V5.2.

### Convención de prompts

A partir de V5.3, todos los prompts nuevos deben guardarse bajo:

`prompts/V5/`

Los prompts históricos existentes bajo:

`prompts/V5_0/`

deben permanecer donde están. No moverlos durante esta ronda.

### Git

El usuario quiere que cada versión tenga historial claro mediante:

- commit de cierre;
- tag de versión;
- push a la rama correspondiente.

El control debe ser semi-automático:

1. el agente prepara y valida;
2. muestra el estado y comandos exactos;
3. NO hace push sin aprobación humana explícita.

El usuario sigue siendo la autoridad final sobre Git.

## 3. Estado técnico de partida

V5.0: cerrada.

V5.1: cerrada.

V5.2 R3.4.1: aprobada humanamente.

V5.2 R4: revisada.

V5.2 R4.1: diagnóstico completado.

V5.2 R4.2: `V5_2_R4_2_READY_FOR_CLOSURE_REVIEW`.

R4.2 confirmó:

- 2.449 pruebas;
- 0 fallas;
- 0 errores;
- 132 skips esperados;
- 46.567 documentos Markdown;
- Evidence Core sin cambios;
- V5.3 no iniciada.

## 4. Archivos obligatorios a revisar

Leer al menos:

- `docs/V5/V5_2_R4_DOCUMENTATION_CLOSURE.md`
- `docs/V5/V5_2_R4_1_DIAGNOSTICO_PENDIENTES_DEUDA_TECNICA.md`
- `docs/V5/V5_2_R4_2_CORRECCIONES_PRE_CIERRE.md`
- `docs/V5/V5_2_R3_4_1_METHOD_DETAIL_QUALITY.md`
- `docs/V5/V5_1_R4_CIERRE_FINAL.md`
- `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`
- `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`
- `docs/continuity/LEGACYMAPPER_LESSONS_LEARNED.md`
- `docs/continuity/ASSISTANT_WORKING_RULES_AND_PREFERENCES.md`
- `PROJECT_STATE.json`
- `AGENTS.md`
- `CLAUDE.md`

No asumir rutas distintas sin comprobarlas.

## 5. Actualizaciones de estado requeridas

### A. `PROJECT_STATE.json`

Actualizarlo para reflejar el estado real después del cierre.

Debe dejar claro como mínimo:

- V5.0 cerrada;
- V5.1 cerrada;
- V5.2 cerrada;
- última ronda completada = V5.2 R4.3;
- última ronda aprobada = V5.2 R4.3;
- total de pruebas vigente = 2.449;
- siguiente fase = V5.3;
- V5 implementada = true;
- baseline IST oficial = `C:\Users\cgalianj\source\IST_40\Operacional`;
- V5.3 todavía no iniciada.

Usar las claves existentes cuando sea posible.
No rediseñar el schema salvo necesidad real.

### B. Roadmap

Actualizar:

`docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`

Debe indicar:

- V5.2 CLOSED;
- V5.3 READY_TO_START;
- baseline oficial;
- 2.449 pruebas como última suite completa;
- R4.2 como corrección pre-cierre;
- R4.3 como cierre formal;
- convención nueva de prompts bajo `prompts/V5/`.

No modificar el orden V5.3–V5.9.

### C. Historia y continuidad

Actualizar:

`docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`

Registrar:

- cierre formal de V5.2;
- decisiones principales;
- deuda corregida en R4.2;
- limitaciones futuras que permanecen por contrato;
- baseline oficial;
- siguiente paso V5.3;
- nueva política Git.

### D. Lecciones aprendidas

Actualizar solo si corresponde añadir una lección general reutilizable.

No reescribir historia previa.

Si se añade una lección, incluir:

- distinguir baseline histórico de otra copia del mismo sistema;
- evitar cerrar una versión con estado oficial desactualizado;
- cubrir con tests correcciones de robustez como reintentos de escritura;
- versionar el trabajo antes de iniciar una nueva fase importante.

### E. Reglas de trabajo

No modificar `ASSISTANT_WORKING_RULES_AND_PREFERENCES.md` salvo que sea necesario registrar formalmente el procedimiento Git aprobado.

Si se agrega, hacerlo de forma simple:

- cada versión debe terminar con un punto de versionado;
- commit + tag + push;
- push requiere aprobación humana explícita;
- el agente puede preparar comandos y verificar estado;
- el usuario mantiene autoridad final.

## 6. Correcciones documentales requeridas

Registrar correctamente en el cierre:

1. Las dos rutas IST no son equivalentes.
2. `IST_40` es el baseline oficial de V5.2.
3. El origen de `atomic_write.py` sí estaba documentado.
4. El cambio de `run_summary_presenter.py` sí estaba documentado y probado.
5. La ubicación histórica `prompts/V5_0/` se conserva.
6. Los prompts nuevos desde V5.3 usarán `prompts/V5/`.

No modificar retroactivamente informes históricos salvo que exista una razón fuerte.

Preferir registrar la corrección en el cierre formal.

## 7. Deuda técnica restante

Separar claramente:

### Resuelto antes del cierre

- pruebas directas de `_replace_with_retry`;
- ambigüedad del texto de conteo de archivos;
- baseline oficial;
- estado oficial desactualizado;
- convención de prompts;
- procedimiento Git.

### Fase futura por contrato

Mantener documentado sin implementar:

- dependencias a nivel de método no disponibles;
- identidad de sobrecargas y firmas;
- atribución de ciertos `unresolved`;
- enlace directo `.aspx/.ascx` a code-behind cuando la evidencia lo permita;
- trazabilidad de flujo a `archivo:línea`;
- clasificación más rica de tipos de proyecto;
- validación en otro repositorio;
- agrupación funcional;
- refactor de módulos grandes si se programa en una ronda propia.

No tratarlos como defectos pendientes de cierre.

## 8. Procedimiento Git para cierres futuros

Documentar un procedimiento estándar.

### Paso 1 — revisar

```bat
cd /d C:\dev\LegacyMapper
git status
git diff --stat
```

### Paso 2 — preparar commit

No ejecutar automáticamente si hay archivos ajenos o dudosos.

Proponer un mensaje de commit claro, por ejemplo:

`chore(v5.2): close documentation profiles phase`

### Paso 3 — tag

Proponer:

`v5.2`

Verificar primero que no exista.

### Paso 4 — push

Preparar los comandos:

```bat
git push <remote> <branch>
git push <remote> v5.2
```

Pero NO ejecutar estos comandos sin aprobación humana explícita.

### Paso 5 — registrar

El cierre debe dejar registrado:

- commit hash;
- tag;
- rama;
- remote;
- fecha;
- suite final.

Si no existe todavía commit/tag/push porque falta aprobación humana, documentarlo como `PENDING_GIT_APPROVAL`.

## 9. Git en esta ronda

Esta ronda puede:

- ejecutar `git status`;
- ejecutar `git diff`;
- identificar rama actual;
- identificar remotes;
- comprobar si existe el tag `v5.2`;
- preparar comandos exactos;
- proponer mensaje de commit.

Esta ronda NO puede:

- ejecutar commit;
- crear tag;
- hacer push;
- reset;
- rebase;
- checkout destructivo;
- limpiar archivos.

El resultado debe quedar listo para que el Technical Lead autorice después la operación Git.

## 10. Validación final

No repetir la extracción IST.

No repetir la suite completa si no hay cambios de código o tests durante esta ronda.

Si solo se modifican archivos documentales y de estado, reutilizar la suite completa de R4.2:

- 2.449 pruebas;
- 0 fallas;
- 0 errores;
- 132 skips.

Si accidentalmente se modifica código o tests, eso es una desviación de alcance y la ronda debe declararse bloqueada.

## 11. Entregable único

Crear:

`docs/V5/V5_2_R4_3_CIERRE_FORMAL.md`

Debe incluir:

1. Objetivo.
2. Estado previo.
3. Decisiones humanas consolidadas.
4. Archivos modificados.
5. Estado final de V5.2.
6. Baseline oficial IST.
7. Suite final utilizada.
8. Deudas resueltas antes del cierre.
9. Limitaciones futuras por contrato.
10. Estado de `PROJECT_STATE.json`.
11. Estado de roadmap y continuidad.
12. Procedimiento Git establecido.
13. Estado Git actual.
14. Commit/tag/push propuestos.
15. Confirmación de que no se ejecutó push.
16. Siguiente fase autorizable: V5.3.
17. Confirmación de que V5.3 no fue iniciada.

## 12. Estado final permitido

Si todo queda consistente:

`V5_2_CLOSED_PENDING_GIT_APPROVAL`

Este estado significa:

- V5.2 está técnicamente y documentalmente cerrada;
- solo falta la operación Git final controlada por el usuario.

Si aparece inconsistencia material:

`V5_2_R4_3_BLOCKED`

No iniciar V5.3.

## 13. Respuesta final del agente

Responder de forma breve y simple con:

- estado final;
- archivo de cierre creado;
- archivos de estado actualizados;
- baseline oficial;
- pruebas usadas;
- rama Git detectada;
- commit propuesto;
- tag propuesto;
- comandos de push preparados;
- confirmación de que no se ejecutó push;
- confirmación de que V5.3 no fue iniciada.

Detenerse para revisión humana y aprobación Git.
