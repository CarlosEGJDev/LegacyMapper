# LegacyMapper V5.2 — R4.1: Diagnóstico de pendientes y deuda técnica

## 1. Misión única

Realizar un diagnóstico **solo de lectura** de los pendientes identificados en el cierre documental R4 de V5.2 y de la deuda técnica acumulada. El Technical Lead autorizó preparar este diagnóstico, **no** implementar correcciones ni cerrar V5.2.

El propósito es distinguir, con evidencia verificable, entre: (a) defectos reales que conviene corregir antes del cierre, (b) problemas administrativos o de continuidad, (c) limitaciones conscientemente aceptadas por el contrato vigente, (d) funcionalidades previstas para fases futuras y (e) observaciones que no constituyen deuda demostrada. Favorecer resolver deuda técnica evitable durante el desarrollo, pero no ampliar el alcance automáticamente.

## 2. Contexto y rutas

Repositorio de desarrollo: `C:\dev\LegacyMapper`.

Informe a revisar: `docs/V5/V5_2_R4_DOCUMENTATION_CLOSURE.md`.

Informe previo: `docs/V5/V5_2_R3_4_1_METHOD_DETAIL_QUALITY.md`.

Consultar los demás informes de V5.2 bajo `docs/V5/`, los contratos V5.0/V5.1 relevantes, `AGENTS.md`, `CLAUDE.md`, `PROJECT_STATE.json` y los documentos de continuidad, especialmente:

- `docs/continuity/ASSISTANT_WORKING_RULES_AND_PREFERENCES.md` (versión actualizada; comprobar su contenido existente).
- `docs/continuity/LEGACYMAPPER_LESSONS_LEARNED.md`.
- `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`.
- `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`.

La ruta real del prompt R4 anterior fue informada como `prompts/V5_0/V5_2_R4_DOCUMENTATION_CLOSURE.md`; la convención prevista para nuevos prompts es `prompts/V5/`. Verificar la estructura existente sin mover archivos.

Salidas persistidas de referencia: `C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_1_validation\ist_full_run\` y `...\human_review_sample\`. No regenerarlas salvo autorización posterior.

Existen dos ubicaciones IST mencionadas en la documentación:

- `C:\Users\cgalianj\source\IST_40\Operacional` (fuente utilizada en los informes de V5.2).
- `C:\inetpub\wwwroot\2010\IST\Operacional` (ruta de referencia del prompt R4 y continuidad histórica).

No asumir que son equivalentes ni elegir una como baseline vigente sin prueba y decisión humana.

## 3. Estado y evidencia histórica (no confundir con medición nueva)

- V5.0 y V5.1 cerradas.
- R3.4.1 aprobada explícitamente por el Technical Lead el 29-09-2026.
- R4 emitió `V5_2_R4_READY_FOR_HUMAN_APPROVAL`, pero **V5.2 NO está cerrada formalmente**.
- V5.3 NO iniciada.
- R3.4.1 reportó suite completa de 2.441 pruebas, 0 fallos, 0 errores y 132 omisiones; corrida IST `SUCCESS` y etapas IA `NOT_RUN`.
- R4 informó 272 pruebas dirigidas correctas; 46.567 Markdown en la salida V5.2; 876 archivos de documentación legacy. La verificación previa de 5.514 enlaces en 3.000 documentos fue una **muestra**, no un barrido exhaustivo.

Distinguir en el informe entre `[NUEVO: R4.1]`, `[HEREDADO]` y `[NO VERIFICADO]`.

## 4. Preguntas concretas del diagnóstico

### 4.1 Hallazgos H-1 a H-6 de R4

Examinar los seis hallazgos registrados en `docs/V5/V5_2_R4_DOCUMENTATION_CLOSURE.md`, priorizando:

- **H-1:** `PROJECT_STATE.json` desactualizado frente al avance real. Identificar con evidencia las fuentes autoritativas, el cambio administrativo exacto que sería necesario y quién debería autorizarlo. No editarlo.
- **H-2:** dos rutas de IST. Determinar qué ruta respaldó la corrida y métricas de V5.2. Proponer una comparación reproducible, acotada y de solo lectura para establecer si ambas contienen el mismo input relevante (por ejemplo, listado estable y hashes de archivos pertinentes), distinguiendo diferencias ambientales como saltos de línea. Si la comparación es viable con coste razonable, ejecutarla sin alterar nada y registrar alcance, exclusiones y resultados. Si resulta costosa, dejar procedimiento y evidencia faltante, sin afirmar equivalencia.
- **H-3:** cambios no registrados en Git. Ejecutar solo consultas de estado y diferencias para identificar qué pertenece a V5 y posibles archivos ajenos. No hacer `add`, `commit`, `push`, `reset`, `clean`, `checkout`, `restore` ni cambiar la configuración.
- **H-4:** origen y alcance de los cambios en `atomic_write.py` y `run_summary_presenter.py`. Examinar diferencias, llamadas y tests relacionados. Indicar si hay comportamiento sin prueba o sin decisión documental y el riesgo concreto. No atribuir autoría ni causa sin evidencia.
- **H-5:** divergencia de carpeta `prompts/V5/` vs `prompts/V5_0/`; documentar la ubicación efectiva y la convención propuesta sin mover ni corregir archivos.
- **H-6:** evolución de la cantidad de pruebas entre informes; verificar si es simple crecimiento del conjunto o una discrepancia real.

### 4.2 Inventario completo de deudas

Revisar **todas** las entradas de la sección 8.2 de R4, no solo las cuatro observaciones principales. Para cada una, registrar:

1. Qué se observó realmente y de dónde viene la evidencia (archivo, sección, prueba o salida).
2. Si es un defecto actual, deuda técnica evitable, limitación explícita del contrato, funcionalidad futura u observación no demostrada.
3. Efecto observable para el usuario, regresión, mantenibilidad o continuidad; no exagerar el impacto.
4. Si puede resolverse ahora sin cambiar alcance/contratos, o si requiere una decisión de diseño/versión posterior.
5. Acción propuesta, dependencia, riesgo de corregirla y criterio verificable de aceptación.
6. Recomendación de tratamiento: `ANTES_DEL_CIERRE`, `DOCUMENTAR_Y_ACEPTAR_EXPLICITAMENTE`, `FASE_FUTURA_POR_CONTRATO` o `SIN_ACCION_POR_FALTA_DE_EVIDENCIA`.

No equiparar todo lo clasificado como `POST_VERSION` con deuda técnica aceptable. No elevar una funcionalidad futura a bloqueo por el mero hecho de no estar implementada. Señalar explícitamente cualquier problema que haría inadecuado cerrar V5.2 con las reglas actualizadas del usuario.

### 4.3 Contratos y continuidad

Verificar si alguna recomendación propuesta afecta el core normalizado, los IDs, provenance, confidence, unresolved, compatibilidad V4.3, documentación legacy, independencia del runtime, o separación entre evidencia e interpretación. Indicar la prueba necesaria antes de cualquier corrección futura. La IA integrada en documentación no es parte del alcance de V5.2.

## 5. Forma de trabajar y límites

- Esta es una ronda **diagnóstica**, sin cambios de producción, tests, prompts, documentación existente, outputs, roadmap ni `PROJECT_STATE.json`.
- Solo se autoriza crear **un** documento nuevo de resultados en la ruta de la sección 6. Evitar generar archivos temporales dentro del repositorio; si una medición requiere temporales, usar una ubicación externa y describirlos.
- No reejecutar el análisis completo IST ni la suite completa por rutina. Emplear lectura de código, evidencias persistidas y comprobaciones dirigidas de bajo coste cuando sean indispensables. No hacer comprobaciones concurrentes largas. Si no se ejecutan pruebas, declararlo.
- No modificar ni borrar archivos; no hacer operaciones de Git que cambien estado. El usuario administra Git.
- No corregir deuda, no introducir funcionalidades, no preparar el prompt de implementación ni el prompt de V5.3. No declarar V5.2 cerrada.
- Si se detecta un riesgo serio o una discrepancia, registrarlo con prueba y propuesta de siguiente paso. No pasar del diagnóstico a la corrección sin checkpoint humano.
- Redactar el documento en español, con explicaciones sencillas. Desarrollar toda abreviación la primera vez que se utilice. Preservar nombres técnicos literales cuando se necesiten como referencias auditables.

## 6. Entregable único y ruta exacta

Crear:

`C:\dev\LegacyMapper\docs\V5\V5_2_R4_1_DIAGNOSTICO_PENDIENTES_DEUDA_TECNICA.md`

Estructura mínima:

1. Estado y alcance.
2. Fuentes revisadas y comprobaciones realmente ejecutadas.
3. Tabla H-1 a H-6: evidencia, impacto, decisión pendiente, tratamiento propuesto.
4. Inventario íntegro de las deudas de R4 §8.2, con clasificación revisada y justificación.
5. Propuesta acotada de correcciones antes del cierre, ordenadas por dependencia, **sin implementarlas**; si ninguna es necesaria, explicarlo con evidencia.
6. Riesgos de compatibilidad, pruebas necesarias y criterios de aceptación para una eventual ronda de corrección.
7. Aspectos que necesitan decisión del Technical Lead, especialmente ruta IST oficial, Git y actualización del estado.
8. Archivos creados o modificados (debe figurar solo este informe).
9. Estado final y siguiente checkpoint humano.

Estados finales permitidos: `V5_2_R4_1_DIAGNOSIS_READY_FOR_HUMAN_REVIEW` o `V5_2_R4_1_DIAGNOSIS_BLOCKED` (con causa y datos faltantes).

## 7. Respuesta al finalizar

Informar de forma breve el estado final, la ruta exacta del documento, el número de asuntos propuestos para resolución antes del cierre, las comprobaciones nuevas realizadas, si hubo limitaciones y confirmar expresamente: sin modificación de código, sin commits/push, sin cierre de V5.2 y sin inicio de V5.3. Detenerse para revisión humana.
