# V5.2 R3.2 — Project Identity & Human Documentation Clarity

## Rol y contexto

Repositorio:

`C:\dev\LegacyMapper`

Target de referencia:

`C:\Users\cgalianj\source\IST_40\Operacional`

V5.2 R3.1 terminó técnicamente correctamente, pero todavía no obtuvo aprobación humana.

Esta ronda debe corregir los últimos problemas semánticos observados en la documentación para desarrolladores.

No rediseñar la arquitectura V5.2.

## 1. Documentación obligatoria

Leer:

- `docs/V5/V5_2_R1_DOCUMENTATION_CONTRACT_DESIGN.md`
- `docs/V5/V5_2_R2_DOCUMENTATION_ENGINE_IMPLEMENTATION.md`
- `docs/V5/V5_2_R3_TECHNICAL_AND_HUMAN_VALIDATION.md`
- `docs/V5/V5_2_R3_1_HUMAN_SEMANTIC_CORRECTIONS.md`

Revisar también las salidas reales de R3.1.

## 2. Objetivo principal: identidad real de proyectos

Verificar que la documentación Developer Technical solo denomine proyecto/módulo a una entidad que corresponda realmente a un proyecto del repositorio.

En el adapter .NET de referencia:

- Solution: archivo `.sln`.
- Project: archivo `.vbproj` o `.csproj`.
- Component: clase, formulario, módulo de código u otro componente.
- SourceArtifact: archivo físico.

No determinar la identidad de una entidad mediante:

- prefijos `BL`, `Web`, `sys`, `DAL`, etc.;
- nombres de carpetas;
- nombres de clases;
- archivos encontrados en recorridos;
- bibliotecas referenciadas;
- coincidencias parciales de nombres.

La identidad debe provenir de evidencia verificable.

## 3. Caso obligatorio: BLInterfazSAP

Investigar específicamente `BLInterfazSAP`.

Comprobar:

1. Si existe `BLInterfazSAP.vbproj` o `.csproj`.
2. Su ruta real.
3. Su registro en `projects.json` / Evidence Core.
4. A qué Solution pertenece, si dicha relación está demostrada.
5. Si existe también `BLInterfazSAP.vb` u otro archivo/clase homónima.
6. Si la documentación está confundiendo alguna de estas entidades.

No asumir que BL significa automáticamente un proyecto de Business Logic.

Si es un proyecto real, conservarlo como proyecto y mostrar su evidencia de identidad.

Si es solo un archivo o componente, retirarlo del índice de proyectos y presentarlo dentro del proyecto propietario.

Aplicar el criterio al resto de proyectos documentados, no únicamente a BLInterfazSAP.

## 4. Estructura documental

La navegación debe respetar:

Sistema analizado
  → Solutions
    → Projects
      → Componentes
        → Archivos / clases / formularios / métodos

Una Solution puede agrupar varios Projects y un Project puede pertenecer a varias Solutions.

No duplicar artificialmente la identidad de un Project por aparecer en más de una Solution.

Si existen archivos sin proyecto identificado, documentarlos como elementos sin pertenencia determinada, nunca inventar un Project.

Mantener la Vista General breve.

## 5. Identidad visible del proyecto

Cada documento de proyecto debe permitir comprobar fácilmente:

- nombre real;
- ruta del `.vbproj`/`.csproj`;
- Solutions asociadas, cuando estén demostradas;
- ruta relativa del proyecto;
- tipo técnico de salida, cuando exista.

No utilizar sufijos artificiales `-2`/`-3` como identidad visible.

Si hay proyectos homónimos, mostrar su ruta para distinguirlos.

## 6. Tipo técnico y tipo de proyecto

Corregir la presentación de:

`Tipo de salida: Library`

El valor técnico `Library` no significa necesariamente que funcionalmente se trate de una biblioteca común.

Usar:

`Tipo técnico de salida: Library`

Si el adapter dispone de evidencia suficiente para identificar una aplicación Web, biblioteca de clases u otro tipo de proyecto, mostrarlo en un campo separado:

`Tipo de proyecto: ...`

No deducirlo únicamente del nombre o prefijo.

Si no existe evidencia suficiente, omitir la clasificación o indicar que no pudo determinarse.

## 7. Dirección de dependencias

Corregir la sección de dependencias de los documentos de proyecto.

Separar:

**Proyectos que este proyecto utiliza**

A → B

**Proyectos que utilizan este proyecto**

C → A

No mezclar ambas relaciones bajo «Proyectos referenciados».

Comprobar específicamente el caso BLInterfazSAP / WebInterfazSAP.

Mantener la dirección real de la dependencia, sin invertirla.

Las dependencias no demostradas deben permanecer sin clasificar.

## 8. Información no resuelta

Mejorar la política declarativa de ruido técnico en el resumen de información no resuelta.

Revisar especialmente:

- `System.Web.UI.WebControls.Unit(...)`
- `Response.Write(...)`
- `GetColumnByDataField(...)`
- llamadas conocidas de UI/framework;
- operaciones auxiliares similares.

No declarar que una llamada ha sido resuelta cuando no lo está.

Solo reducir su protagonismo en la presentación principal cuando la categoría pueda establecerse mediante reglas justificadas.

Mantener el detalle disponible.

No ocultar problemas funcionales reales.

Priorizar modificaciones en configuración declarativa frente a cambios de lógica Python.

## 9. Preservar correcciones de R3.1

Comprobar que no retroceden:

- propiedad real de pantallas;
- recorridos originados vs. recibidos;
- acceso directo vs. indirecto a datos;
- métrica de 672 recorridos reales en IST;
- operaciones transaccionales excluidas de esa métrica;
- clasificación prudente de dependencias externas;
- terminología humana;
- compatibilidad legacy;
- `documentation_v52` en RUN_SUMMARY.

No inventar el proyecto de origen de los recorridos todavía no identificados.

## 10. Separación arquitectónica

Mantener:

Evidence Core
  → Audience Transformation
  → Profile
  → Template
  → Renderer

Las correcciones deben ubicarse en la capa responsable.

No introducir lógica de identidad .NET ni clasificación semántica en MarkdownRenderer.

No modificar Evidence Core para resolver un problema exclusivamente de presentación.

Si se descubre que la identidad está incorrecta dentro del propio Evidence Core, registrar evidencia y detener esa parte; no corregir silenciosamente V5.1.

## 11. Tests obligatorios

Incluir pruebas que comprueben:

- solo entidades Project reales reciben documentación de proyecto;
- un archivo/clase homónimo no genera un Project ficticio;
- pertenencia Solution → Project correcta;
- un Project compartido entre Solutions conserva su identidad;
- rutas visibles suficientes para distinguir homónimos;
- tipo de salida diferenciado del tipo de proyecto;
- dependencias entrantes/salientes correctamente separadas;
- ruido de framework relegado al detalle;
- ausencia de regresiones R3.1;
- determinismo;
- documentación legacy intacta.

Ejecutar la suite completa:

`python -m unittest discover -s tests`

Requerido: 0 fallas, 0 errores.

## 12. Validación real sobre IST

Generar una nueva corrida sin sobrescribir las anteriores:

`C:\PruebasLegacyMapper\Resultados\v5_2_r3_2_validation\`

Verificar mediante evidencia real que cada documento Developer identificado como Project corresponde a un `.vbproj`/`.csproj`.

No basta con validar que tiene nombre o aparece en una lista.

Comprobar que las rutas y relaciones son coherentes.

## 13. Muestra humana

Crear:

`C:\PruebasLegacyMapper\Resultados\v5_2_r3_2_validation\human_review_sample\`

Incluir copias exactas, sin edición manual, de:

1. General Overview completo.
2. Índice Developer.
3. BLInterfazSAP (o su proyecto propietario, según el resultado de la verificación).
4. WebInterfazSAP, para revisar la dirección de sus relaciones.
5. Proyecto Web.
6. Proyecto de lógica de negocio.
7. Caso con acceso directo e indirecto.
8. Caso con información no resuelta.
9. Ejemplo de proyecto homónimo o copia Backup, si existe.

La muestra debe conservar los enlaces internos necesarios para recorrer los ejemplos seleccionados.

Crear un único `README.md` de navegación.

No crear documentación paralela ni corregir manualmente los archivos de la muestra.

## 14. Revisión humana interna

Leer físicamente los resultados.

Responder con evidencia:

- ¿BLInterfazSAP es un Project real o un archivo/componente?
- ¿Los Projects documentados corresponden a proyectos reales?
- ¿Se puede navegar desde una Solution a sus Projects?
- ¿Se comprende qué depende de qué?
- ¿Se comprende qué significa Library?
- ¿La información no resuelta es más legible?
- ¿La Vista General explica la estructura?
- ¿Se mantienen las correcciones de R3.1?

Claude no puede otorgar aprobación humana en nombre del Technical Lead.

## 15. Restricciones

NO:

- rediseñar la arquitectura;
- modificar V5.1;
- implementar funcionalidades V5.3+;
- implementar IA o HTML;
- retirar `documentation/` legacy;
- realizar refactorizaciones generales;
- modificar roadmap;
- modificar PROJECT_STATE;
- crear commits o push;
- crear documentos auxiliares;
- crear prompt R4.

## 16. Documento de resultado

Crear exclusivamente:

`docs/V5/V5_2_R3_2_PROJECT_IDENTITY_AND_HUMAN_CLARITY.md`

Estructura:

1. Estado.
2. Resultado de investigación BLInterfazSAP.
3. Verificación de identidad de proyectos.
4. Jerarquía Solution/Project/Component.
5. Tipo técnico de salida.
6. Dirección de dependencias.
7. Información no resuelta y ruido.
8. Compatibilidad con R3.1.
9. Prueba IST.
10. Suite completa.
11. Deuda restante.
12. Ruta de muestra humana.
13. Qué debe revisar el Technical Lead.
14. Conclusión.

Utilizar lenguaje sencillo y evidencia concreta.

## 17. Estados finales permitidos

Terminar exactamente con uno:

V5_2_R3_2_READY_FOR_HUMAN_REVIEW

V5_2_R3_2_BLOCKED

V5_2_R3_2_CONFLICT

V5_2_R3_2_OPEN_DECISION

No declarar V5.2 cerrada ni READY_FOR_R4.

La aprobación humana sigue siendo obligatoria.

Al finalizar, esperar revisión externa.