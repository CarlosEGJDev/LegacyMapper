# LegacyMapper V5.2 — R4.4 Ajuste final de estado y preparación Git

## 1. Objetivo

Resolver la última inconsistencia administrativa detectada después del cierre formal de V5.2 y dejar preparado el versionado Git final.

Esta ronda NO reabre V5.2 funcionalmente.
No modifica código de producción.
No inicia V5.3.
No hace commit, tag ni push.

## 2. Contexto

V5.2 está cerrada técnica y documentalmente con estado:

`V5_2_CLOSED_PENDING_GIT_APPROVAL`

La suite final vigente es:

- 2.449 pruebas
- 0 fallas
- 0 errores
- 132 skips esperados

Baseline oficial:

`C:\Users\cgalianj\source\IST_40\Operacional`

Último informe:

`docs/V5/V5_2_R4_3_CIERRE_FORMAL.md`

## 3. Inconsistencia a corregir

En `PROJECT_STATE.json` existe todavía una referencia histórica a una intermitencia identificada como `NON_REPRODUCIBLE`.

Sin embargo, existe documentación posterior:

`docs/V5/PRE_V5_1_RERUN_INTERMITTENCY_INVESTIGATION_RESULT.md`

donde la causa fue identificada y se implementó una corrección mediante reintento de escritura atómica.

La documentación posterior debe prevalecer como estado actual.

## 4. Trabajo autorizado

Modificar únicamente `PROJECT_STATE.json` para que el riesgo histórico quede actualizado de forma coherente con la evidencia posterior.

La actualización debe:

- conservar el hecho histórico de que existió la intermitencia;
- indicar que la causa fue identificada;
- indicar que se aplicó una corrección;
- indicar que existe cobertura de tests añadida en V5.2 R4.2;
- evitar la etiqueta `NON_REPRODUCIBLE` como estado vigente si ya no representa la situación actual;
- preservar cualquier referencia útil a los documentos históricos.

No eliminar historia.
No inventar causas nuevas.
No modificar otros riesgos no relacionados.

## 5. Validación

Después del cambio:

1. validar que `PROJECT_STATE.json` sea JSON válido;
2. ejecutar únicamente los tests que validan o consumen `PROJECT_STATE.json`;
3. si esos tests pasan y no se modificó código ni tests, NO repetir la suite completa de 2.449 pruebas;
4. registrar que la suite completa vigente sigue siendo la de R4.3.

Si para hacer pasar los tests fuera necesario modificar código o tests, detenerse y declarar bloqueo.

## 6. Revisión Git

Ejecutar solo consultas:

```bat
cd /d C:\dev\LegacyMapper
git status
git diff --stat
git diff -- PROJECT_STATE.json
git branch --show-current
git remote -v
git tag -l "v5.2"
```

No ejecutar operaciones que cambien historial.

## 7. Preparación del versionado

Si todo está correcto, preparar:

Commit propuesto:

`chore(v5.2): close documentation profiles phase`

Tag propuesto:

`v5.2`

Rama esperada:

`main`

Remote esperado:

`origin`

Preparar, pero NO ejecutar:

```bat
git add -A
git status
git commit -m "chore(v5.2): close documentation profiles phase"
git tag -a v5.2 -m "V5.2 Template-Driven Documentation & Output Profiles - closed"
git push origin main
git push origin v5.2
```

Antes de proponer `git add -A`, revisar y listar archivos dudosos o ajenos al trabajo V5.

Si existen archivos que no deberían entrar al cierre, no asumir: documentarlos.

## 8. Entregable único

Crear:

`docs/V5/V5_2_R4_4_AJUSTE_FINAL_ESTADO_Y_GIT.md`

Debe incluir:

1. inconsistencia corregida;
2. cambio exacto realizado en `PROJECT_STATE.json`;
3. validación JSON;
4. tests dirigidos ejecutados;
5. resultado;
6. estado Git;
7. archivos que entrarían al commit;
8. archivos dudosos, si existen;
9. commit propuesto;
10. tag propuesto;
11. comandos preparados;
12. confirmación de que no se hizo commit/tag/push;
13. confirmación de que V5.3 no fue iniciada.

## 9. Estado final permitido

Si todo queda consistente:

`V5_2_READY_FOR_GIT_APPROVAL`

Si aparece un problema:

`V5_2_R4_4_BLOCKED`

No usar ningún otro estado.

## 10. Restricciones

No:

- modificar código de producción;
- modificar tests;
- modificar roadmap;
- modificar documentos de continuidad;
- modificar informes históricos;
- mover prompts;
- hacer commit;
- crear tag;
- hacer push;
- iniciar V5.3.

Detenerse para revisión humana.
