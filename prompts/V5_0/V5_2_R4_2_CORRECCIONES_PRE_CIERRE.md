# LegacyMapper V5.2 — R4.2 Corrección acotada antes del cierre

## 1. Objetivo

Ejecutar una ronda pequeña de corrección previa al cierre formal de V5.2.

Esta ronda existe para resolver deuda técnica evitable identificada en:

- `docs/V5/V5_2_R4_DOCUMENTATION_CLOSURE.md`
- `docs/V5/V5_2_R4_1_DIAGNOSTICO_PENDIENTES_DEUDA_TECNICA.md`

No es una ronda de rediseño.
No inicia V5.3.
No modifica Evidence Core salvo que una prueba revele una regresión real bloqueante.
No amplía el alcance de V5.2.

## 2. Decisiones humanas ya tomadas

El Technical Lead aprueba la siguiente dirección:

1. Mantener como baseline oficial de V5.2:
   `C:\Users\cgalianj\source\IST_40\Operacional`

   Motivo: las mediciones y validaciones de V5.2 provienen de esa ruta. La otra ruta IST comparada no es equivalente.

2. Evitar deuda técnica cuando pueda corregirse razonablemente dentro de la fase actual.

3. Corregir antes del cierre:
   - la falta de pruebas directas para la lógica de reintento de escritura atómica;
   - la ambigüedad menor del texto relacionado con el conteo de archivos, siempre que pueda corregirse únicamente en presentación y sin alterar evidencia.

4. Ejecutar una única suite completa al final de esta ronda.

5. El usuario administra Git. No hacer commit, push, reset, checkout destructivo, rebase ni operaciones que cambien el historial.

## 3. Prerrequisito de continuidad

Antes de modificar archivos:

- ejecutar `git status`;
- registrar el estado observado;
- no limpiar ni descartar cambios existentes;
- no modificar archivos ajenos al alcance de esta ronda.

Si existen cambios previos, preservarlos.

El Technical Lead realizará personalmente el versionado correspondiente.

## 4. Corrección A — pruebas de `_replace_with_retry`

### Contexto

`atomic_write.py` contiene una lógica de reintento ante `PermissionError` durante `os.replace`.

El diagnóstico R4.1 determinó que la corrección está documentada, pero carece de pruebas directas.

### Trabajo requerido

Agregar pruebas unitarias específicas para el comportamiento existente.

Cubrir como mínimo:

1. Primer intento falla con `PermissionError` y un intento posterior tiene éxito.
2. Todos los intentos fallan con `PermissionError` y finalmente la excepción se propaga.
3. Una excepción distinta de `PermissionError` no se reintenta.
4. El comportamiento de limpieza del archivo temporal se mantiene correctamente cuando corresponda.

### Reglas

- Simular `os.replace`.
- Simular `time.sleep`.
- No introducir esperas reales.
- No cambiar la política de reintentos existente salvo que una prueba demuestre un defecto real.
- No convertir esta ronda en refactor de `atomic_write.py`.
- Mantener determinismo.

Si el comportamiento actual impide probar correctamente alguno de estos casos, documentar primero la causa antes de cambiar producción.

## 5. Corrección B — texto ambiguo de conteo de archivos

### Contexto

R4.1 identificó una ambigüedad menor entre un texto como:

`N archivos de código`

y una tabla que cuenta un conjunto diferente de archivos.

Los datos no son incorrectos; el problema es de presentación.

### Trabajo requerido

Revisar la plantilla, catálogo de idioma o configuración correspondiente y aclarar el texto para que el lector entienda exactamente qué representa cada conteo.

### Restricciones

- Cambiar solo presentación.
- No modificar Evidence Core.
- No modificar conteos deterministas.
- No cambiar relaciones, provenance, confidence, IDs ni estado unresolved.
- No introducir lógica nueva en el renderer si puede resolverse mediante template/i18n/configuración existente.
- Mantener español claro y simple.

Agregar o ajustar únicamente las pruebas necesarias para demostrar que el texto ya no es ambiguo.

## 6. Validación de documentación

Si la corrección B modifica Markdown generado:

- regenerar la documentación únicamente desde evidencia persistida válida;
- no ejecutar nuevamente la extracción completa de IST;
- comprobar que la generación termina correctamente;
- registrar cualquier cambio esperado en cantidad de bytes/hashes;
- confirmar que los conteos y relaciones permanecen iguales.

No exigir igualdad byte a byte con la salida anterior cuando el texto cambió deliberadamente.

## 7. Suite completa

Después de terminar ambas correcciones y sus pruebas dirigidas:

```bat
cd /d C:\dev\LegacyMapper
python -m unittest discover -s tests
```

Registrar:

- total de pruebas;
- fallas;
- errores;
- skips;
- duración si está disponible.

No ejecutar suites completas concurrentes.

Si la suite falla:

1. identificar si el fallo fue causado por esta ronda;
2. corregir únicamente si está dentro del alcance;
3. si revela un problema distinto o de mayor alcance, detener la ronda y declararla bloqueada.

## 8. Verificaciones de regresión

Confirmar que siguen preservados:

- compatibilidad V4.3;
- Evidence Core V5.1;
- separación Evidence / Presentation;
- runtime independence;
- provider IA opcional;
- `unresolved` permanece sin inventar resolución;
- documentación legacy preservada;
- General Overview y Developer Technical siguen siendo proyecciones independientes;
- V5.3 continúa sin iniciar.

No ejecutar IA.

## 9. Lo que NO debe hacerse

No:

- iniciar V5.3;
- implementar cache o incremental analysis;
- cambiar arquitectura V5.1;
- modificar IDs;
- cambiar reglas de evidencia;
- introducir nuevas features;
- resolver gaps que requieren nueva extracción;
- refactorizar módulos grandes por mantenibilidad;
- mover prompts históricos;
- modificar `PROJECT_STATE.json`;
- modificar roadmap o documentos de continuidad;
- corregir retroactivamente R4;
- hacer commit o push.

Las actualizaciones de estado y continuidad pertenecen a la ronda formal de cierre posterior.

## 10. Entregable único

Crear:

`docs/V5/V5_2_R4_2_CORRECCIONES_PRE_CIERRE.md`

Debe incluir:

1. Objetivo.
2. Estado inicial de Git observado.
3. Archivos modificados.
4. Pruebas añadidas para `_replace_with_retry`.
5. Corrección realizada al texto ambiguo.
6. Validaciones dirigidas.
7. Resultado de regeneración desde evidencia persistida, si fue necesaria.
8. Resultado de la suite completa.
9. Confirmación de contratos preservados.
10. Problemas encontrados.
11. Deuda técnica restante relevante para V5.2.
12. Estado final.
13. Confirmación de que no hubo commit/push.
14. Confirmación de que V5.3 no fue iniciada.

## 11. Estados finales permitidos

Seleccionar exactamente uno:

`V5_2_R4_2_READY_FOR_CLOSURE_REVIEW`

o

`V5_2_R4_2_BLOCKED`

Usar `READY_FOR_CLOSURE_REVIEW` solo si:

- las pruebas nuevas son correctas;
- la ambigüedad de presentación quedó resuelta sin alterar evidencia;
- la suite completa termina correctamente;
- no aparece deuda técnica nueva que deba resolverse antes del cierre.

No declarar `V5_2_CLOSED`.

## 12. Respuesta final del agente

Responder brevemente con:

- estado final;
- archivo de resultado creado;
- archivos modificados;
- pruebas ejecutadas;
- resultado de la suite completa;
- cualquier bloqueo;
- confirmación de no commit/push;
- confirmación de que V5.3 no fue iniciada.

Detenerse después de entregar el informe para revisión humana.
