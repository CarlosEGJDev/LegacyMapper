# V5.2 R3.4.1 — Method Detail Quality & Document Redundancy Control

## 0. Contexto y autoridad

Repositorio:

C:\dev\LegacyMapper

Target legado de referencia (solo lectura):

C:\Users\cgalianj\source\IST_40\Operacional

La ronda V5.2 R3.4 terminó técnicamente con estado:

V5_2_R3_4_READY_FOR_HUMAN_REVIEW

El Technical Lead revisó el resultado documental y autorizó expresamente esta ronda correctiva.

Objetivo: mejorar la utilidad del detalle por método, reducir documentos redundantes y conservar íntegramente la evidencia.

No implementar una nueva arquitectura.

No modificar Evidence Core.

No reabrir V5.1.

---

## 1. Lectura obligatoria

Leer íntegramente:

- AGENTS.md
- PROJECT_STATE.json
- docs/V5/V5_2_R1_DOCUMENTATION_CONTRACT_DESIGN.md
- docs/V5/V5_2_R2_DOCUMENTATION_ENGINE_IMPLEMENTATION.md
- docs/V5/V5_2_R3_TECHNICAL_AND_HUMAN_VALIDATION.md
- docs/V5/V5_2_R3_1_HUMAN_SEMANTIC_CORRECTIONS.md
- docs/V5/V5_2_R3_2_PROJECT_IDENTITY_AND_HUMAN_CLARITY.md
- docs/V5/V5_2_R3_3_COMPONENT_NAVIGATION.md
- docs/V5/V5_2_R3_4_METHOD_TRACEABILITY.md

Inspeccionar también la implementación productiva actual:

legacy_documenter/documentation_v52/

Y la salida real de R3.4.

No asumir que las cifras obtenidas durante una revisión externa son resultados definitivos de una medición del motor. Reproducirlas con criterios explícitos sobre la evidencia y documentación real.

---

## 2. Objetivo

Corregir tres problemas observados:

A. Las llamadas no resueltas muestran frecuentemente el texto genérico `(no resuelto)`, sin explicar qué expresión produjo la llamada.

B. La presentación de acceso a datos puede destacar operaciones de control transaccional junto con operaciones reales de datos, aunque ya se acordó distinguirlas.

C. Algunos documentos individuales de método aportan poca información adicional respecto del índice del componente.

No se busca eliminar información.

Se busca mejorar su presentación y decidir correctamente dónde mostrarla.

---

## 3. Preflight obligatorio

Antes de modificar código, inspeccionar la evidencia real y el funcionamiento actual de:

- calls;
- data_access;
- symbols;
- MethodModel;
- AudienceTransformer;
- profiles;
- templates;
- noise policy;
- renderer;
- documentos de método existentes.

Medir sobre la corrida R3.4:

1. Total de métodos identificados.
2. Total de documentos individuales generados.
3. Documentos con llamadas resueltas.
4. Documentos con llamadas exclusivamente no resueltas.
5. Documentos con operaciones reales de datos.
6. Documentos con únicamente control transaccional.
7. Documentos con relaciones mixtas.
8. Documentos sin contenido adicional relevante.

Las categorías pueden solaparse. Explicar el criterio de cada medición para evitar sumas engañosas.

Registrar qué información ya existe en Evidence Core y qué información no está disponible.

---

## 4. Expresiones originales de llamadas no resueltas

Cuando una llamada tiene:

resolved_target = None

y existe su campo original:

expression

Mostrar la expresión real en la presentación técnica.

Ejemplo conceptual:

Método: txTraerListArchivo

Llamadas no resueltas:

| Expresión identificada | Origen | Estado |
| --- | --- | --- |
| expresión original extraída | Archivo.vb:19 | No resuelto |

No sustituir una expresión conocida por el mensaje genérico `(no resuelto)`.

Si la expresión original tampoco está disponible, mostrar honestamente esa ausencia.

Mantener:

- archivo;
- línea, cuando exista;
- confianza;
- estado de resolución;
- destino resuelto, cuando corresponda.

No interpretar la expresión como si ya se hubiese identificado su destino.

No ejecutar análisis adicional.

No usar IA.

---

## 5. Control de ruido técnico

La expresión original debe mejorar la comprensión, no volver a introducir todo el ruido que ya se controló en R3.1/R3.2.

Reutilizar la política declarativa de ruido existente.

Separar cuando sea posible:

- llamadas resueltas;
- llamadas no resueltas potencialmente relevantes;
- llamadas de framework/UI/infraestructura;
- detalle técnico completo.

No ocultar silenciosamente evidencia.

Las expresiones largas deben tratarse mediante una política de presentación segura y consistente.

Mantener su versión completa accesible cuando exista en la evidencia.

Evitar romper tablas Markdown con caracteres especiales, barras verticales o saltos de línea.

---

## 6. Acceso real a datos vs. control transaccional

Preservar la corrección semántica de R3.1.

Distinguir claramente:

A. Operaciones reales de datos:
- ejecución SQL;
- procedimientos almacenados;
- otras operaciones reales identificadas por Evidence Core.

B. Control transaccional:
- Commit;
- Rollback;
- BeginTransaction;
- operaciones equivalentes cuando estén clasificadas por la evidencia.

No afirmar que un método accede realmente a datos solo porque contiene una operación de control transaccional.

Ejemplo conceptual:

Acceso a datos
- Procedimiento almacenado: XXX

Control transaccional
- Commit identificado

Si un método solo tiene control transaccional, declararlo como tal.

No modificar el significado de las métricas generales de acceso real a datos.

Preservar los 672 recorridos reales confirmados en IST y la separación de los 1698 recorridos exclusivamente transaccionales.

---

## 7. Criterio de generación de documentos individuales

Revisar el criterio actual de R3.4:

Se genera documento si existe una llamada saliente, una llamada entrante confirmada o una operación de datos atribuida individualmente.

Este criterio permitió generar 22.215 documentos individuales en IST.

Establecer un criterio determinista y declarativo que evite generar documentos cuyo contenido no aporte información adicional útil.

Considerar especialmente:

- métodos cuya única información es una o varias llamadas no resueltas sin expresión disponible;
- métodos cuyo único contenido adicional es ruido técnico ya clasificado;
- métodos con únicamente información transaccional repetitiva;
- métodos con relaciones realmente útiles;
- métodos con llamadas confirmadas;
- métodos con acceso real a datos.

IMPORTANTE:

No eliminar automáticamente todos los métodos con llamadas no resueltas.

Si una llamada no resuelta conserva una expresión y origen técnico útiles, puede justificar su propio detalle.

No aplicar un umbral arbitrario del tipo «mínimo dos llamadas» sin justificarlo con evidencia.

No clasificar como redundante un documento que contiene información individual relevante que no está disponible desde otra ruta.

La decisión de generar detalle corresponde al Output Profile/política declarativa, utilizando datos preparados por Audience Transformation.

No implementar este criterio como reglas dispersas en MarkdownRenderer.

---

## 8. Preservación de evidencia

Toda evidencia original debe conservarse.

Una reducción de documentos físicos no autoriza:

- eliminar calls;
- eliminar data_access;
- descartar provenance;
- modificar identities;
- marcar una relación ambigua como confirmada;
- asignar llamadas de un método a otro;
- perder expresiones originales;
- borrar información no resuelta.

Cuando se suprima un documento individual por redundancia, verificar que los datos relevantes continúen accesibles mediante el índice del componente o un detalle técnico existente.

No dejar enlaces apuntando a documentos que ya no se generan.

No crear documentos individuales vacíos o enlaces decorativos.

---

## 9. Trazabilidad y limitaciones

Conservar la regla de V5.1:

No existe una identidad canónica de método que distinga todas las sobrecargas.

No inventar firmas, parámetros, líneas ni IDs nuevos que aparenten resolver esta limitación.

Mantener:

- método → llamada, cuando esté demostrado;
- método → operación de datos, cuando esté demostrado;
- método → archivo de origen;
- llamadas entrantes confirmadas;
- métodos homónimos declarados ambiguos.

Las dependencias y límites no resueltos que no pueden atribuirse individualmente deben continuar como GAP, sin adjudicarlos artificialmente a métodos.

---

## 10. Navegación

Mantener:

Solution
 → Project
 → Archivo
 → Componente
 → Método
 → Evidencia técnica disponible

Conservar navegación de retorno.

Si un método no tiene documento propio:

- debe permanecer visible en el índice del componente;
- no debe tener un enlace roto;
- no debe desaparecer de la documentación.

Si un método sí tiene documento:

- la navegación debe mostrar su información relevante;
- el origen de la evidencia debe ser comprensible;
- el lector debe poder regresar al componente.

---

## 11. Medición antes/después

Comparar R3.4 frente a R3.4.1.

Incluir:

| Métrica | R3.4 | R3.4.1 |
| --- | --- | --- |
| Métodos identificados | | |
| Documentos individuales de método | | |
| Métodos solo en índice | | |
| Documentos con acceso real a datos | | |
| Documentos solo transaccionales | | |
| Documentos con llamadas no resueltas y expresión visible | | |
| Total documentos documentation_v52 | | |
| Tamaño total | | |
| Archivo máximo | | |
| Enlaces rotos | | |
| Evidencia original perdida | | |

No establecer como objetivo obligatorio reducir un porcentaje concreto de documentos.

La mejora se evalúa por utilidad, claridad y conservación de evidencia, no solamente por conseguir una cifra menor.

Explicar cualquier reducción o incremento.

---

## 12. Arquitectura y compatibilidad

Mantener:

Evidence Core
 → Audience Transformation
 → Output Profile
 → Template
 → Markdown Renderer

No modificar:

- Evidence Core;
- V5.1;
- extractores;
- análisis semántico;
- documentation/ legacy;
- roadmap;
- PROJECT_STATE.json.

No implementar:

- IA;
- HTML;
- V5.3–V5.9;
- caché incremental;
- nuevas identidades canónicas.

General Overview debe permanecer simple e intacto.

---

## 13. Tests obligatorios

Agregar pruebas para:

1. Llamada no resuelta con expresión original disponible.
2. Llamada no resuelta sin expresión.
3. Llamada confirmada con destino real.
4. Distinción entre operación real de datos y control transaccional.
5. Método con únicamente control transaccional.
6. Método con llamadas no resueltas relevantes.
7. Método con únicamente ruido técnico.
8. Documento omitido sin pérdida de evidencia.
9. Método sin documento todavía visible en índice.
10. Ausencia de enlaces rotos.
11. Métodos homónimos sin atribución individual inventada.
12. Determinismo.
13. Particionado.
14. Custom templates.
15. General Overview intacto.
16. AI OFF.
17. Legacy intacto.
18. Regresiones R3.1–R3.4.

No basar todas las pruebas en snapshots Markdown.

Ejecutar suite completa:

python -m unittest discover -s tests

Exigir 0 fallas y 0 errores.

---

## 14. Prueba IST real

Ejecutar una nueva validación sobre:

C:\Users\cgalianj\source\IST_40\Operacional

Destino:

C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_1_validation\

No sobrescribir ninguna corrida anterior.

Reutilizar evidencia persistida para regeneraciones de documentación cuando corresponda, sin repetir innecesariamente la extracción completa.

Verificar físicamente:

- BLInterfazSAP;
- txTraerListArchivo;
- un método con acceso real a datos;
- un método solo transaccional;
- un método con llamada no resuelta y expresión visible;
- un método sin relaciones suficientes;
- un método ambiguo;
- img\aceptar.gif;
- un proyecto Web.

No inventar ejemplos para satisfacer esta lista.

Si una categoría no aparece en IST real, registrar el resultado.

---

## 15. Muestra humana autocontenida

Crear:

C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_1_validation\human_review_sample\

Incluir una muestra seleccionada, pequeña y navegable, con copias exactas de la documentación productiva.

No copiar nuevamente los ~47 mil archivos completos a una carpeta llamada muestra.

Incluir:

- General Overview;
- Solution;
- Project;
- Archivo;
- Componente;
- método con relaciones útiles;
- método con llamada no resuelta y expresión visible;
- método con acceso real a datos;
- método que permanece solo en el índice;
- control transaccional;
- pertenencia ambigua.

Incluir los documentos de destino necesarios para los recorridos seleccionados.

Los enlaces de dichos recorridos deben funcionar completamente.

Permitir que el README de la muestra identifique explícitamente los enlaces hacia contenido no incluido, sin editar manualmente los documentos productivos.

Verificar integridad de la muestra.

---

## 16. Revisión humana interna

Leer los Markdown generados y responder:

- ¿Se entiende qué expresión produjo una llamada no resuelta?
- ¿Se diferencia correctamente una llamada confirmada de una no resuelta?
- ¿Se distingue acceso real a datos de control transaccional?
- ¿Cada detalle individual aporta información adicional útil?
- ¿La navegación sigue funcionando cuando un método no tiene documento?
- ¿Se preserva toda la evidencia?
- ¿La Vista General sigue siendo comprensible?
- ¿El volumen documental es justificable?

No aprobar la ronda en nombre del Technical Lead.

---

## 17. Restricciones de ejecución

No pedir confirmación por operaciones rutinarias ya autorizadas.

No ejecutar repetidamente la suite completa sin causa concreta.

No lanzar una segunda suite completa si la primera sigue ejecutándose.

No permanecer esperando indefinidamente un monitor.

Si un proceso termina o desaparece, inspeccionar directamente su log y código de salida.

No declarar éxito hasta comprobar el resultado real.

No crear commits ni hacer push.

Dejar los cambios en el working tree.

---

## 18. Documento de resultado

Crear exclusivamente:

docs/V5/V5_2_R3_4_1_METHOD_DETAIL_QUALITY.md

Estructura:

1. Estado.
2. Preflight y baseline R3.4.
3. Expresiones no resueltas.
4. Acceso real vs. control transaccional.
5. Nuevo criterio de generación.
6. Preservación de evidencia.
7. Navegación.
8. Medición antes/después.
9. Arquitectura y compatibilidad.
10. Validación IST.
11. Suite completa.
12. GAPs y deuda.
13. Ruta de muestra humana.
14. Qué debe revisar el Technical Lead.
15. Conclusión.

No crear otros documentos auxiliares ni prompts de rondas posteriores.

---

## 19. Estados finales

Terminar exactamente con uno:

V5_2_R3_4_1_READY_FOR_HUMAN_REVIEW

V5_2_R3_4_1_BLOCKED

V5_2_R3_4_1_CONFLICT

V5_2_R3_4_1_OPEN_DECISION

No declarar V5.2 cerrada.

No declarar READY_FOR_R4.

Esperar revisión y aprobación humana.