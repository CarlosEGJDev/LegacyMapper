# V5.2 R3.4 — Trazabilidad técnica por método

## Rol y contexto

Repositorio:

C:\dev\LegacyMapper

Target real:

C:\Users\cgalianj\source\IST_40\Operacional

V5.1 está formalmente cerrada.

V5.2 R3.3 terminó READY_FOR_HUMAN_REVIEW.

El Technical Lead aprobó expresamente ampliar Developer Technical con trazabilidad técnica por método utilizando evidencia existente.

Esta ronda es una extensión controlada de R3.3.

NO modificar Evidence Core.
NO realizar una nueva extracción de código.
NO rediseñar la arquitectura V5.2.

---

# 1. Documentos obligatorios

Leer:

- docs/V5/V5_2_R1_DOCUMENTATION_CONTRACT_DESIGN.md
- docs/V5/V5_2_R2_DOCUMENTATION_ENGINE_IMPLEMENTATION.md
- docs/V5/V5_2_R3_TECHNICAL_AND_HUMAN_VALIDATION.md
- docs/V5/V5_2_R3_1_HUMAN_SEMANTIC_CORRECTIONS.md
- docs/V5/V5_2_R3_2_PROJECT_IDENTITY_AND_HUMAN_CLARITY.md
- docs/V5/V5_2_R3_3_COMPONENT_NAVIGATION.md

Inspeccionar el paquete:

legacy_documenter/documentation_v52/

Y la salida real de R3.3.

---

# 2. Objetivo

Permitir que un desarrollador navegue:

Solution
 → Project
 → Archivo
 → Componente
 → Método
 → Relaciones técnicas disponibles

La información profunda debe presentarse bajo demanda.

El objetivo NO es reproducir todo Evidence Core en Markdown.

El objetivo es permitir comprender las relaciones técnicas de un método sin perder su origen ni inventar información.

---

# 3. Alcance de la trazabilidad

Para cada método, cuando exista evidencia suficiente, mostrar:

- nombre;
- componente propietario;
- archivo de origen;
- tipo y visibilidad;
- llamadas identificadas;
- componentes o métodos relacionados;
- dependencias relacionadas;
- operaciones de acceso a datos;
- procedimientos almacenados/SQL relacionados;
- información no resuelta;
- referencias hacia evidencia técnica disponible.

No exigir que todos los métodos posean toda esta información.

No inventar:

- líneas;
- firmas;
- parámetros;
- sobrecargas;
- métodos llamados;
- relaciones entre componentes;
- accesos a datos;
- dependencias.

---

# 4. Preflight obligatorio de evidencia

ANTES de implementar, investigar los datos persistidos disponibles:

- symbols;
- calls;
- call identities;
- data_access;
- functional_flows;
- functional_paths;
- flow_unresolved;
- dependencies;
- EvidenceReference/provenance existentes.

Determinar qué relaciones pueden establecerse realmente:

A. Método → llamada.

B. Método → dependencia.

C. Método → operación de datos.

D. Método → información no resuelta.

E. Método → archivo de origen.

Para cada relación:

- identificar qué campos actuales permiten construirla;
- comprobar si su identidad es suficientemente precisa;
- identificar limitaciones de homónimos y sobrecargas;
- determinar si la información existe a nivel de método, componente o proyecto.

No trasladar automáticamente información de un proyecto a todos sus métodos.

Si una relación no puede determinarse correctamente, declararla como GAP.

---

# 5. Regla de identidad del método

V5.1 no introdujo una identidad canónica independiente para todos los métodos.

Respetar esa decisión.

No generar identificadores nuevos que aparenten distinguir firmas/sobrecargas cuando el extractor actual no tiene información suficiente.

Las relaciones deben construirse exclusivamente cuando los campos existentes permitan establecerlas sin ambigüedad.

Si dos métodos homónimos no pueden distinguirse:

- no mezclar sus llamadas;
- no atribuir información individual incierta;
- mostrar la limitación;
- conservar la evidencia técnica original.

---

# 6. Presentación del método

Implementar una vista de método legible.

Ejemplo conceptual:

Método: txTraerListArchivo

Ubicación
- Proyecto: BLInterfazSAP
- Archivo: BLInterfazSAP.vb
- Componente: BLInterfazSAP

Información técnica
- Tipo: Function
- Visibilidad: Public

Relaciones identificadas
- Llamadas: ...
- Acceso a datos: ...
- Dependencias: ...

Información no resuelta
- ...

Si alguna sección carece de evidencia suficiente, mostrar una explicación breve u omitirla según el profile.

Nunca rellenar una sección con relaciones deducidas únicamente del nombre del método.

---

# 7. Evidencia detallada bajo demanda

Mantener documentos principales pequeños.

La lista de métodos del componente debe ofrecer navegación hacia el detalle de un método cuando existan relaciones individuales verificables.

No generar obligatoriamente un documento por cada método si únicamente se conoce:

- nombre;
- tipo;
- visibilidad;
- condición Shared.

En esos casos puede mantenerse la información dentro del índice de métodos.

Definir una estrategia determinista para evitar crear miles de documentos redundantes.

El detalle debe reutilizar información ya recopilada, sin ejecutar IA ni análisis adicional cuando se abre el enlace.

---

# 8. Provenance y trazabilidad

Conservar la referencia hacia la evidencia original siempre que exista.

No modificar ni reconstruir artificialmente EvidenceReference.

La presentación humana puede ocultar IDs internos, pero no debe destruir la trazabilidad técnica.

Distinguir:

- relación confirmada;
- relación ambigua;
- información no disponible.

No presentar una asociación aproximada como confirmada.

---

# 9. Pertenencia ambigua de archivos

Corregir el problema de presentación observado en R3.3.

Ejemplo real:

img\aceptar.gif

Actualmente aparece bajo «sin proyecto asignado», aunque cinco proyectos lo declaran.

Mostrar de forma comprensible:

Pertenencia: compartida o ambigua.

Proyectos que declaran el archivo:
- ...

No presentarlo textualmente como si «sin proyecto asignado» fuese un proyecto real.

No modificar las reglas de propiedad ni escoger arbitrariamente un propietario.

---

# 10. Escala documental

R3.3 generó aproximadamente 25 mil documentos.

Medir:

- documentos de proyecto;
- documentos de archivo;
- documentos de componente;
- documentos de método, si se introducen;
- documentos sin información adicional relevante;
- tamaño total;
- tamaño máximo;
- enlaces.

Evitar multiplicar documentos que solo repiten información ya disponible en el nivel superior.

No eliminar evidencia para reducir archivos.

Priorizar navegación progresiva y generación de detalle cuando exista información adicional útil.

No introducir cache ni funcionalidades de V5.3.

---

# 11. Navegación

Mantener:

Solution
 → Project
 → Archivo
 → Componente
 → Método

Los documentos profundos deben permitir regresar al nivel superior.

Mantener enlaces relativos y deterministas.

Comprobar compatibilidad con Windows y nombres homónimos.

No exponer IDs internos como interfaz de navegación.

---

# 12. Arquitectura

Mantener estrictamente:

Evidence Core
 → Audience Transformation
 → Output Profile
 → Template
 → Markdown Renderer

La preparación de relaciones por método pertenece a Audience Transformation.

La decisión de mostrar el detalle pertenece al Profile.

La estructura pertenece al Template.

La escritura física pertenece al Renderer.

No introducir semántica de métodos ni resolución de llamadas en MarkdownRenderer.

Mantener templates declarativos.

---

# 13. General Overview

No modificar su nivel de detalle.

La Vista General debe seguir siendo comprensible para personas no desarrolladoras.

No incorporar listados de métodos, llamadas ni evidencias técnicas profundas.

---

# 14. Compatibilidad

Mantener intactos:

- Evidence Core;
- V5.1;
- documentation/ legacy;
- identities;
- provenance;
- consumidores existentes.

Preservar las correcciones de R3.1, R3.2 y R3.3.

El motor debe funcionar con AI OFF.

---

# 15. Tests obligatorios

Agregar tests para:

- relaciones por método sustentadas en evidencia;
- ausencia de atribución desde proyecto a método sin prueba;
- métodos homónimos y sobrecargas ambiguas;
- método sin llamadas conocidas;
- método con acceso real a datos, si existe evidencia;
- relación no resuelta;
- referencias al archivo y componente propietario;
- enlaces de ida y vuelta;
- pertenencia ambigua presentada correctamente;
- documentos de detalle no redundantes;
- determinismo;
- particionado;
- General Overview intacto;
- custom templates;
- legacy intacto;
- AI OFF.

No basar todas las pruebas en snapshots textuales.

---

# 16. Prueba real sobre IST

Ejecutar sobre:

C:\Users\cgalianj\source\IST_40\Operacional

Destino nuevo:

C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_validation\

No sobrescribir R3.3.

Verificar al menos:

- un método con llamadas relacionadas;
- un método con acceso a datos relacionado, si puede demostrarse;
- un método sin relaciones suficientes;
- un caso de nombre ambiguo;
- BLInterfazSAP;
- un proyecto Web;
- img\aceptar.gif.

Si no existen relaciones demostrables en una categoría:

registrar GAP, no fabricar un ejemplo.

---

# 17. Muestra humana autocontenida

Crear:

C:\PruebasLegacyMapper\Resultados\v5_2_r3_4_validation\human_review_sample\

Debe incluir copias de la documentación productiva.

Permitir recorrer:

Solution
 → Project
 → Archivo
 → Componente
 → Método
 → Evidencia técnica

Incluir casos con:

- relación técnica confirmada;
- ausencia de relación;
- ambigüedad;
- acceso a datos, si es demostrable;
- archivo con pertenencia compartida;
- proyecto Web.

Los enlaces relevantes de los recorridos seleccionados deben funcionar dentro de la muestra.

No editar manualmente documentos para que se vean mejor.

---

# 18. Validación humana interna

Leer físicamente los Markdown generados.

Responder:

- ¿Se comprende qué hace técnicamente el método según la evidencia disponible?
- ¿Queda claro qué llamadas son suyas?
- ¿Se evita atribuirle llamadas de otros métodos?
- ¿Puedo distinguir evidencia confirmada de información no disponible?
- ¿Puedo volver desde el método al componente y proyecto?
- ¿La cantidad de documentos es razonable?
- ¿Se mantienen los documentos principales legibles?

Claude no puede aprobar en nombre del Technical Lead.

---

# 19. Suite completa

Ejecutar:

python -m unittest discover -s tests

Requerido:

0 failures
0 errors

Reportar skips.

---

# 20. Restricciones

NO:

- modificar Evidence Core;
- introducir identidad canónica ficticia de método;
- implementar nuevos extractores;
- realizar nuevo análisis semántico del código fuente;
- implementar IA;
- implementar HTML;
- implementar V5.3–V5.9;
- retirar documentación legacy;
- rediseñar arquitectura;
- realizar refactorizaciones generales;
- modificar roadmap;
- modificar PROJECT_STATE;
- crear commits;
- hacer push;
- crear documentos auxiliares;
- crear prompt R4.

Si una relación importante necesita nueva extracción, registrar GAP y mantener la documentación honesta.

---

# 21. Resultado

Crear exclusivamente:

docs/V5/V5_2_R3_4_METHOD_TRACEABILITY.md

Estructura:

1. Estado.
2. Preflight de evidencia.
3. Relaciones realmente disponibles.
4. Qué se implementó.
5. Presentación de métodos.
6. Evidencia bajo demanda.
7. Identidad y ambigüedades.
8. Pertenencia ambigua de archivos.
9. Escala documental.
10. Compatibilidad con R3.3.
11. Prueba IST.
12. Suite completa.
13. GAPs y deuda restante.
14. Ruta de muestra humana.
15. Qué debe revisar el Technical Lead.
16. Conclusión.

Mantener lenguaje sencillo y aportar evidencia concreta.

---

# 22. Estados permitidos

Terminar exactamente con uno:

V5_2_R3_4_READY_FOR_HUMAN_REVIEW

V5_2_R3_4_BLOCKED

V5_2_R3_4_CONFLICT

V5_2_R3_4_OPEN_DECISION

No declarar V5.2 cerrada ni READY_FOR_R4.

---

# 23. Regla final

Crear únicamente el resultado solicitado y la muestra humana.

No generar prompt R4.

Esperar revisión externa y aprobación humana.