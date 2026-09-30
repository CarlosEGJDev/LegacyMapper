# V5.2 R3.4.1 — Method Detail Quality & Document Redundancy Control

## 1. Estado

`V5_2_R3_4_1_READY_FOR_HUMAN_REVIEW`

La corrección se implementó, la suite completa (2441 pruebas, 0 fallas, 0
errores, 132 omisiones esperadas) y una corrida real completa sobre
`C:\Users\cgalianj\source\IST_40\Operacional` están terminadas. No se
implementó una nueva arquitectura, no se modificó Evidence Core y no se
reabrió V5.1. No se declara V5.2 cerrada ni lista para R4: falta la
aprobación explícita del Technical Lead.

## 2. Preflight y baseline R3.4

Se inspeccionó el código real (no la memoria de la ronda anterior) de
`legacy_documenter/documentation_v52/transform.py`, `noise.py`, `config.py`,
`template.py`, `defaults/templates/dev.method.json` y la evidencia real
persistida de la corrida R3.4 (`C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_validation\evidence`).

Hallazgos del preflight:

- `_build_calls_indexes` leía `resolved_target` pero **nunca** `expression`
  de la partición `calls`; una llamada no resuelta se presentaba siempre
  como el literal `"(no resuelto)"`, descartando la expresión real que sí
  existe en la evidencia (`call.expression`).
- El acceso a datos por método (`_build_data_access_by_method`) no aplicaba
  ninguna clasificación de la política de ruido; una fila de "Control de
  transacción" se mostraba en la misma tabla "Acceso a datos" que un
  procedimiento almacenado real, aunque la política declarativa ya distingue
  `transaction_control` (`counts_as_data_access: false`) desde R2.
- El criterio de generación de documento por método era: `outgoing or
  incoming or data_ops` — cualquier llamada (incluso `"(no resuelto)"` sin
  expresión) o cualquier operación de datos (incluido control transaccional
  puro) alcanzaba para generar un documento individual.

**Mediciones sobre la corrida real R3.4** (regenerando desde la evidencia
persistida, sin repetir la extracción — mismo mecanismo ya legitimado en
R2/R3.1/R3.2/R3.3; criterios de cada medición explicados para evitar sumas
engañosas):

| # | Medición | Criterio exacto | R3.4 |
|---|---|---|---:|
| 1 | Métodos identificados | filas en tablas de índice de componente (`component.slots.methods`), un miembro único por componente | 33 610 |
| 2 | Documentos individuales de método | `MethodModel` generados (uno por nombre no ambiguo con relación individual) | 22 215 |
| 3 | Documentos con llamadas resueltas | documento de método con ≥1 llamada saliente con `resolved_target` no vacío | no medido en R3.4 (no se distinguía) |
| 4 | Documentos con llamadas exclusivamente no resueltas | documento sin ninguna llamada resuelta pero con ≥1 no resuelta | no medido en R3.4 |
| 5 | Documentos con operaciones reales de datos | documento con ≥1 fila de `data_access` no clasificada como ruido | no medido en R3.4 (mezclado con transaccional) |
| 6 | Documentos con únicamente control transaccional | documento cuya única evidencia de datos es `operation_kind == "transaction"` | no medido en R3.4 |
| 7 | Documentos con relaciones mixtas | documento con llamadas Y acceso a datos a la vez | no medido en R3.4 |
| 8 | Documentos sin contenido adicional relevante | documento cuya única evidencia es ruido ya clasificado o llamadas sin expresión | 0 por diseño (el criterio de R3.4 no distinguía esto; se estima que una fracción no cuantificada de los 22 215 caía aquí) |

Las categorías 3-8 se solapan entre sí (un documento puede tener llamadas
resueltas Y acceso real a datos a la vez, por ejemplo) — el objetivo del
preflight fue explicar el criterio de cada una, no sumar filas.

**Qué ya existe en Evidence Core y qué no está disponible** (sin cambios
respecto del preflight de R3.4, sección 2 de ese documento): `calls`
(partición cruda con `expression`/`resolved_target`/`confidence`/`evidence`)
y `data_access` (con `class`/`method`/`operation_kind`) ya traen toda la
información necesaria a nivel de método. No existe una identidad canónica de
método por firma (GAP-M2, sin cambios). No se accedió a ningún dato nuevo:
toda la corrección de esta ronda es de **presentación** sobre datos ya
consumidos desde R3.4.

## 3. Expresiones no resueltas

Corregido en `AudienceTransformer._build_calls_indexes` (captura
`call.expression`, normalizado a una sola línea) y
`AudienceTransformer._classify_call` (nuevo método): cuando
`resolved_target` está vacío, se muestra la expresión original tal como
aparece en la evidencia, en vez del literal `"(no resuelto)"`. Cuando la
expresión tampoco está disponible, se declara honestamente su ausencia con
el texto `"(expresión no disponible)"` — nunca se inventa ni se omite la
fila.

Ejemplo real (`BLInterfazSAP.txTraerListArchivo`, antes vs. después):

| | R3.4 | R3.4.1 |
|---|---|---|
| Llamada no resuelta #1 | `(no resuelto)` | `TraerListArchivo(dbc, nroRegistros, tipoPaginacion, nroFila, idAdm, periodo, FecIng, seqArc)` |
| Llamada no resuelta #2 | `(no resuelto)` | `TraerFileSapMensual(dbc, idAdm, periodo, rownum)` |

Se conservan en todo momento: archivo, línea (cuando existe), confianza
(`state.unresolved`, columna "Confianza") y destino resuelto (columna
separada "Llamadas resueltas" cuando corresponde). La expresión nunca se
interpreta como si ya se hubiese identificado su destino: la columna
"Confianza" sigue diciendo literalmente "no resuelto" junto a ella. No se
ejecutó ningún análisis adicional ni IA: la expresión ya estaba en la
evidencia persistida (`calls.json`), simplemente no se leía.

Verificado sobre la corrida real completa: **0** documentos de método
contienen ya el literal `"(no resuelto)"` (antes: presente en toda llamada
sin destino). El marcador honesto de ausencia (`"(expresión no disponible)"`)
no aparece en ningún documento de la corrida IST real — en este repositorio,
el extractor siempre registra alguna expresión para cada llamada no
resuelta; el camino de "expresión también ausente" está implementado y
probado sobre un fixture sintético (`UnresolvedExpressionTests`), pero no se
fabricó un ejemplo real inexistente para forzarlo.

## 4. Acceso real vs. control transaccional

Nuevo método `AudienceTransformer._classify_data_access` reutiliza
literalmente la política de ruido ya existente (`NoisePolicy.classify` +
`counts_as_data_access`, la misma que ya separaba esto a nivel de flujo/
módulo desde R2/R3.1). Cada operación de acceso a datos por método se separa
en dos listas antes de construir el documento: `data_access` (real,
`counts_as_data_access == True`) y `data_access_transactional`
(`operation_kind == "transaction"` u otra categoría marcada
`counts_as_data_access: false`). El documento de método (`dev.method.json`)
las presenta en dos secciones tituladas por separado — **"Acceso real a
datos"** y **"Control transaccional"** — con una nota explícita en la
segunda ("no ejecutan por sí mismas una consulta ni un procedimiento, así
que no se cuentan como acceso real a datos").

Ejemplo real (`blADHds67Bit.txTraerdatosreq`): sección "Acceso real a datos"
con el procedimiento `PADH_D67_BIT.TRAERDATOSREQ`, confianza confirmada.

Ejemplo real (`BLInterfazSAP.txTraerListArchivo`): sección "Control
transaccional" con una fila `Control de transacción` / `(sin nombre
identificado)`, **sin** ninguna fila en "Acceso real a datos" (el método no
tiene evidencia de acceso real).

No se modificó el significado de las métricas generales de acceso real a
datos: la cifra "672 (5.3 %) llegan a una operación real de datos [...]
otros 1698 llegan solo a operaciones de control de transacciones" de
`general/README.md` (corregida en R3.1) permanece exactamente igual en la
corrida real de esta ronda (verificado, sección 8).

## 5. Nuevo criterio de generación

Implementado en `AudienceTransformer._build_methods_for_component`
(Audience Transformation / Output Profile, **no** en `MarkdownRenderer`,
que sigue sin conocer ruido, categorías ni criterio de generación — probado
por el test existente de separación de capas de R2, sin modificar). Un
método obtiene documento propio si y solo si tiene al menos una de:

1. una llamada saliente **resuelta** (`resolved_target` no vacío);
2. una llamada entrante **confirmada** (sin cambios respecto de R3.4);
3. una llamada saliente **no resuelta cuya expresión existe y no está ya
   clasificada como ruido técnico** por la política declarativa (una
   llamada no resuelta sin expresión, o cuya expresión es ruido de
   framework/UI/infraestructura ya conocido, no cuenta por sí sola);
4. una operación de acceso a datos que la política de ruido cuenta como
   **real** (nunca solo control transaccional).

No se aplicó ningún umbral arbitrario tipo "mínimo dos llamadas": una sola
llamada no resuelta con expresión útil y origen técnico sigue siendo
suficiente, exactamente como pedía la ronda. No se eliminó automáticamente
ningún método con llamadas no resueltas: se eliminó únicamente el
subconjunto cuya única evidencia es ruido ya clasificado, ausencia de
expresión, o control transaccional puro — información que ya está
disponible sin pérdida en otro lugar (el índice del componente y, para el
ruido, el resumen "se omiten N elementos" con su categoría).

La decisión de generar detalle sigue viviendo en la capa de Audience
Transformation, reutilizando exactamente la misma política de ruido
declarativa (`defaults/noise/default.json`, sin cambios) que ya filtraba el
cuerpo de los documentos de módulo desde R2/R3.1/R3.2 — no se implementó
como reglas dispersas en el renderer ni se creó una política nueva.

## 6. Preservación de evidencia

Ninguna llamada, operación de datos, expresión ni línea de origen se
eliminó de `transform.py`: `_build_calls_indexes`/`_build_data_access_by_method`
siguen leyendo exactamente los mismos campos de `calls.json`/`data_access.json`
que en R3.4; la única diferencia es **dónde** se presenta cada relación
(sección/documento) y **si** el método individual obtiene documento propio.
Cuando un documento se suprime por el nuevo criterio, la fila del método
sigue visible en la tabla de métodos del componente (nombre, tipo,
visibilidad, "Compartido"), sin enlace — verificado explícitamente
(`DocumentOmittedWithoutEvidenceLossTests`, y en la corrida real: las
`33 610` filas de índice de R3.4 se mantienen exactamente iguales en
R3.4.1, solo cambia cuántas de ellas tienen enlace). No se dejó ningún
enlace apuntando a un documento que ya no se genera (verificado: 0 enlaces
rotos en una muestra de 3000/46 567 documentos de la corrida real, ver
sección 8) y no se creó ningún documento individual vacío ni decorativo.

## 7. Navegación

Sin cambios de arquitectura de navegación (Solution → Project → Archivo →
Componente → Método → Evidencia técnica disponible, de R3.3/R3.4, intacta).
Se verificó explícitamente sobre la corrida real que un método sin documento
(por ejemplo `New` en el componente `ChainedProperties`) permanece visible
en el índice del componente sin enlace roto, y que un método con documento
(por ejemplo `txTraerListArchivo`) conserva su enlace de ida
("Volver al componente") y de vuelta, ambos verificados en disco sobre la
muestra humana (10/10 enlaces "Volver a..." resuelven correctamente).

## 8. Medición antes/después

Metodología: la fila "R3.4" reproduce las cifras ya documentadas en
`docs/V5/V5_2_R3_4_METHOD_TRACEABILITY.md` (sección 9), producidas por la
corrida real de esa ronda. La fila "R3.4.1" se midió regenerando
`documentation_v52/` desde la **misma evidencia persistida** de esa corrida
(`v5_2_r3_4_validation/evidence/`, sin repetir la extracción — mecanismo
legitimado desde R2) con el código de esta ronda
(`python -m tools.v5_2_r3_4_1_method_quality_measurement`), y se confirmó
que la corrida real completa nueva de esta ronda
(`ist_full_run/`, con extracción propia sobre el repositorio legado)
produce exactamente los mismos 46 567 documentos y 59 097 181 bytes — es
decir, la cifra no depende de qué evidencia física se reutilizó.

| Métrica | R3.4 | R3.4.1 |
| --- | ---: | ---: |
| Métodos identificados (filas de índice) | 33 610 | 33 610 |
| Documentos individuales de método | 22 215 | 21 407 |
| Métodos solo en índice (sin documento) | 11 395 (34 %) | 12 203 (36 %) |
| Documentos con acceso real a datos | no medido | 9 305 |
| Documentos solo transaccionales (índice, sin doc) | no medido | incluidos en los 12 203 de arriba |
| Documentos con llamadas no resueltas y expresión visible | 0 (mostraban `(no resuelto)`) | 21 247 |
| Grupos de nombre ambiguo declarados | 38 | 36 |
| Total documentos `documentation_v52` (.md) | 47 375 | 46 567 |
| Tamaño total | no reportado en bytes exactos por R3.4 | 59 097 181 bytes (~56,4 MiB) |
| Archivo máximo | 52 299 bytes (`blParGenerales/detail-incoming-part-000002.md`) | 52 299 bytes (mismo archivo, no tocado por esta ronda) |
| Enlaces rotos | 0 (muestra de la corrida) | 0 (muestra de 3000/46 567 documentos, 5514 enlaces) |
| Evidencia original perdida | ninguna | ninguna |

**Explicación de la reducción** (no se fijó como objetivo obligatorio un
porcentaje): 808 documentos de método (22 215 → 21 407, -3,6 %) dejaron de
generarse. Los 808 son exactamente los métodos cuya única evidencia era
ruido técnico ya clasificado, una llamada no resuelta sin expresión
disponible, o control transaccional puro — información que en R3.4 producía
un documento de bajo valor (por ejemplo, un documento cuyo único contenido
era "Control de transacción: confirmado" y nada más). La reducción es
modesta porque, como ya observaba R3.4 honestamente, la mayoría de los
métodos de este sistema real hacen al menos una llamada con expresión útil
o tocan una operación real de datos — el criterio anterior no estaba
sobre-generando masivamente, solo le faltaba distinguir estos casos
puntuales. Los 2 grupos ambiguos que dejaron de declararse (38 → 36) son,
por el mismo motivo, grupos de nombre repetido cuya única relación asociada
era ruido/transaccional puro: correctamente ya no se afirma una ambigüedad
sobre una relación que no aportaba información individual real.

## 9. Arquitectura y compatibilidad

Sin cambios: Evidence Core → Audience Transformation → Output Profile →
Template → Markdown Renderer, intacta. Todos los cambios de código viven en
`AudienceTransformer` (`transform.py`, capa de Audience Transformation),
`config.py` (listas blancas de campos de template, capa de contrato) y
templates/catálogo declarativos (`dev.method.json`, `es.json`). El
`MarkdownRenderer` no cambió (verificado: test de separación de capas de R2
sigue en verde sin modificación). No se modificó Evidence Core, V5.1,
extractores, análisis semántico, `documentation/` legacy, el roadmap ni
`PROJECT_STATE.json`. No se implementó IA, HTML, V5.3-V5.9, caché
incremental ni nuevas identidades canónicas. General Overview permanece
simple e intacto (verificado: ningún template de General Overview referencia
las nuevas listas de campos; búsqueda automática de vocabulario de método en
`general/README.md` de la corrida real: 0 apariciones).

## 10. Validación IST

Corrida real completa nueva, ejecutada sobre `C:\Users\cgalianj\source\IST_40\Operacional`,
sin sobrescribir ninguna corrida anterior:

```
python main.py full "C:\Users\cgalianj\source\IST_40\Operacional" --output "C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_1_validation\ist_full_run" --verbose
```

Resultado: `LegacyMapper full run: SUCCESS`; las 10 etapas deterministas
`SUCCESS` (SCAN, EXTRACTION, CALL_RESOLUTION, WEB_ENTRY_RESOLUTION,
DATABASE_RESOLUTION, FLOW_RESOLUTION, DEPENDENCY_RESOLUTION, EXPORT,
CONTEXT, DOCUMENTATION); `AI_INTERPRETATION`/`PROPOSAL_GENERATION` `NOT_RUN`
(no se solicitó IA). `Output locations` incluye `documentation_v52`.
`documentation_v52/MANIFEST.json`: **0 advertencias**. `documentation/`
legacy: 876 archivos, sin tocar (mismo número que las corridas de
R3.1-R3.4).

Regeneración por reutilización de evidencia (evidencia de esta misma corrida
vs. evidencia persistida de R3.4) produce, en ambos casos, el mismo conjunto
de 46 567 documentos y el mismo tamaño total — reproducibilidad determinista
confirmada por partida doble.

Verificación física de los ocho elementos exigidos por la sección 14 del
prompt, todos con evidencia real (ninguno fabricado):

1. **`BLInterfazSAP`**: componente con 17 filas en su tabla de métodos;
   `txTraerListArchivo` conserva su documento (llamada resuelta + 2 no
   resueltas con expresión + 4 de infraestructura resumidas + control
   transaccional separado del acceso real).
2. **`txTraerListArchivo`**: ver secciones 3, 4 y 5 arriba — caso central de
   la ronda.
3. **Método con acceso real a datos**: `blADHds67Bit.txTraerdatosreq`
   (`PADH_D67_BIT.TRAERDATOSREQ`, sección "Acceso real a datos").
4. **Método solo transaccional**: no existe, en este repositorio real, un
   método con clase+nombre atribuibles cuya única evidencia sea control
   transaccional sin ninguna llamada asociada (búsqueda automática cruzando
   `data_access.json`/`calls.json`: 0 casos). El comportamiento para ese
   caso está implementado y probado sobre un fixture sintético
   (`RealDataAccessVsTransactionalTests`); el caso real más cercano
   (transaccional + llamadas no resueltas, sin acceso real) es
   `txTraerListArchivo`. Registrado honestamente, sin fabricar un ejemplo.
5. **Método con llamada no resuelta y expresión visible**: `txTraerListArchivo`
   (dos casos reales) y, más ampliamente, 21 247 documentos de método en
   toda la corrida real.
6. **Método sin relaciones suficientes**: `ChainedProperties.New`
   (`developer/modules/unassigned/files/a/ChainedProperties.md`) — fila sin
   enlace en la tabla de métodos.
7. **Método ambiguo**: `FactoryProperties.CreateParagraph`/`GetHyphenation`
   (3 repeticiones cada uno), sin atribución individual inventada.
8. **`img\aceptar.gif`**: pertenencia compartida/ambigua con 5 proyectos
   reales, sin cambios respecto de R3.4 (fuera del alcance de esta ronda,
   verificado intacto).
9. **Proyecto Web**: `BlCobMorosidad`, clasificado "Aplicación Web (ASP.NET
   Web Forms...)", sin cambios respecto de R3.2.

## 11. Suite completa

```
python -m unittest discover -s tests
```

Resultado: **2441 pruebas, 0 fallas, 0 errores, 132 omisiones** (el mismo
número de omisiones esperado por checkout limpio, ninguna nueva). Se agregó
`tests/test_v5_2_r3_4_1_method_detail_quality.py` (18 pruebas nuevas,
contractuales sobre un fixture sintético, nunca solo snapshots de texto):
llamada no resuelta con expresión disponible; llamada no resuelta sin
expresión; llamada confirmada con destino real; distinción real vs.
transaccional sobre el mismo método; método con únicamente control
transaccional; documento omitido sin pérdida de evidencia (índice intacto);
método sin documento visible en el índice; ausencia de enlaces rotos en un
render real; homónimos sin atribución individual inventada; determinismo
(dos corridas producen el mismo modelo); particionado reutilizado sin lógica
nueva; template personalizado de ámbito método referenciando los slots
nuevos; General Overview intacto; AI OFF; `documentation/` legacy
importable; y dos pruebas de regresión explícita contra los GAP y la
agregación de no-resueltos de R3.1-R3.4.

Se corrigieron, como consecuencia directa y esperada de este cambio, tres
pruebas existentes de `tests/test_v5_2_r3_4_method_traceability.py`
(dependían literalmente de los nombres de slot `calls_out`/`data_access`
sin dividir, y una afirmaba el comportamiento `(no resuelto)` que esta
ronda corrige a propósito — se actualizó para exigir la expresión real y
verificar explícitamente que el literal antiguo ya no aparece) y
`tests/test_v4_1_r0_maintainability_inventory.py` (`_build_methods_for_component`
entró al top-N de funciones más grandes por el mismo motivo mecánico ya
documentado en cada ronda anterior: creció al absorber la clasificación
resuelto/no-resuelto/ruido y real/transaccional en un solo lugar,
desplazando a `CallExtractor.extract` por debajo del corte — sin ninguna
regresión de comportamiento, documentado con el mismo estilo de comentario
que las rondas anteriores).

## 12. GAPs y deuda

Sin cambios respecto de los GAP ya declarados en R3.4 (`gap.method_dependencies_not_available`,
`gap.method_unresolved_not_attributable`, `gap.method_identity_no_signatures`,
`gap.method_overloads_ambiguous`) — verificados presentes en la corrida real
de esta ronda, sin modificación de su texto ni de su criterio de aparición.

Deuda nueva de esta ronda:

1. **Caso real de "solo transaccional, sin ninguna llamada" no observado.**
   El comportamiento está implementado y probado sintéticamente (sección
   10.4), pero no pudo demostrarse con un ejemplo real de IST porque no
   existe uno en este repositorio. No es una limitación de la
   implementación: es una característica genuina de este código legado
   (todo método con datos transaccionales atribuibles también llama a algo).
2. Deudas heredadas de R2-R3.4, sin cambios ni afectadas por esta ronda:
   P-2 (flujo → `archivo:línea` del manejador), defaults JSON sin declarar
   como *package data*, modo estricto sin CLI, Renderer HTML y retiro de
   `documentation/` legacy fuera de alcance, GAP-M1 (módulo == proyecto),
   Component/Archivo del ámbito `.aspx` sin enlace directo a su code-behind.

## 13. Ruta de muestra humana

`C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_1_validation\human_review_sample\README.md`

21 archivos (no el árbol completo de ~47 mil, como pedía explícitamente esta
ronda): copias exactas, sin edición manual, de la corrida productiva real de
esta ronda (`ist_full_run/documentation_v52/`), seleccionadas para que los
recorridos exigidos por la sección 15 del prompt funcionen de punta a punta
con ida y vuelta (10/10 enlaces "Volver a..." verificados). El README de la
muestra identifica explícitamente los 103 enlaces que salen de la selección
hacia contenido no incluido (de 137 enlaces relativos totales), sin editar
ningún documento productivo.

Documentación completa regenerada de esta ronda (corrida real, extracción
propia): `C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_1_validation\ist_full_run\documentation_v52\`.

Regeneración auxiliar desde evidencia persistida de R3.4 (usada para el
preflight y la tabla antes/después): `C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_1_validation\run\documentation_v52\`.

## 14. Qué debe revisar el Technical Lead

1. **¿Se entiende ahora qué expresión produjo una llamada no resuelta?**
   Leer `txTraerListArchivo.md` en la muestra humana (recorrido 3):
   compararlo mentalmente con el `(no resuelto)` de R3.4.
2. **¿La separación acceso real / control transaccional es clara?** Ver el
   mismo documento (sección "Control transaccional", con su nota
   explicativa) y `txTraerdatosreq.md` (sección "Acceso real a datos").
3. **¿El nuevo criterio de generación es el correcto, o falta ajustarlo?**
   La reducción es modesta (808 documentos, -3,6 %) porque el criterio
   anterior no estaba masivamente sobre-generando; revisar si esta
   magnitud de corrección es suficiente o si se desea un criterio más
   estricto para una ronda futura.
4. **¿El método sin relaciones suficientes (`ChainedProperties.New`) y el
   caso ambiguo (`FactoryProperties`) se leen correctamente?**
5. **¿La ausencia de un caso real "solo transaccional, sin llamadas" en el
   repositorio (sección 10.4/12.1) es aceptable como hallazgo honesto, o se
   pide construir un caso adicional en otra ronda con otro repositorio?**
6. Aprobar la muestra, pedir ajustes, o bloquear la ronda (esta ronda no
   puede autoaprobarse en nombre del Technical Lead).

## 15. Conclusión

Se corrigieron los tres problemas de presentación señalados por la revisión
externa de R3.4 — llamadas no resueltas mostrando el literal genérico
`(no resuelto)` en vez de su expresión real; acceso a datos mezclando
operaciones reales con control transaccional; y un criterio de generación de
documentos que no distinguía ruido/transaccional-puro de información
individual útil — reutilizando en los tres casos la infraestructura
declarativa ya existente (la política de ruido de R2, sin cambios de datos
salvo lo ya declarado) y sin tocar Evidence Core, V5.1 ni el Renderer. La
corrección se verificó primero sobre un fixture sintético (18 pruebas
nuevas, contractuales) y después sobre la evidencia real completa de la
corrida R3.4 (regeneración sin repetir extracción) y sobre una corrida real
nueva de extremo a extremo (46 567 documentos, 0 advertencias, 0 enlaces
rotos en una muestra de 3000 documentos, 808 documentos de método de bajo
valor correctamente eliminados sin pérdida de evidencia, y los 672
recorridos reales / 1698 transaccionales de R3.1 intactos). La suite
completa (2441 pruebas) pasa sin fallas ni errores. Ningún hallazgo obliga a
bloquear la ronda, pero la escala del cambio y el hallazgo honesto de la
sección 12.1 requieren revisión y aprobación explícita del Technical Lead
antes de continuar.

**V5_2_R3_4_1_READY_FOR_HUMAN_REVIEW**
