# V5.2 R3.3 — Navegación Project → Component → Archivo y evidencia bajo demanda

## Rol

Trabaja sobre:

C:\dev\LegacyMapper

Target de referencia:

C:\Users\cgalianj\source\IST_40\Operacional

V5.1 está formalmente cerrada.

V5.2 R3.2 terminó READY_FOR_HUMAN_REVIEW.

El Technical Lead aprobó expresamente ampliar Developer Technical con navegación desde Project hasta Component/Archivo.

Esta autorización es específica de V5.2 R3.3. No autoriza una refactorización general ni modificar Evidence Core.

---

# 1. Documentación obligatoria

Leer:

- docs/V5/V5_2_R1_DOCUMENTATION_CONTRACT_DESIGN.md
- docs/V5/V5_2_R2_DOCUMENTATION_ENGINE_IMPLEMENTATION.md
- docs/V5/V5_2_R3_TECHNICAL_AND_HUMAN_VALIDATION.md
- docs/V5/V5_2_R3_1_HUMAN_SEMANTIC_CORRECTIONS.md
- docs/V5/V5_2_R3_2_PROJECT_IDENTITY_AND_HUMAN_CLARITY.md

Revisar el paquete productivo:

legacy_documenter/documentation_v52/

No reinterpretar las decisiones aprobadas.

---

# 2. Objetivo principal

Implementar navegación progresiva:

Solution
    ↓
Project
    ↓
Component / Archivo
    ↓
Métodos disponibles
    ↓
Evidencia técnica detallada

La documentación debe permitir a un desarrollador comprender primero la estructura y profundizar progresivamente.

NO crear un documento gigantesco que enumere todos los métodos, llamadas y archivos en una misma página.

---

# 3. Identidad de entidades

Conservar estrictamente:

Solution != Project != Component != SourceArtifact

Para el adapter .NET:

Solution:
- archivo .sln

Project:
- archivo .vbproj / .csproj

Component:
- entidad de código identificada por Evidence Core.

SourceArtifact:
- archivo físico del repositorio.

No crear proyectos a partir de:

- nombres de clases;
- archivos .vb/.cs;
- carpetas;
- prefijos BL/Web/sys;
- bibliotecas;
- referencias;
- componentes involucrados en recorridos.

La relación de pertenencia debe estar respaldada por evidencia.

---

# 4. Navegación Solution → Project

Crear una navegación simple entre las soluciones y sus proyectos.

Debe mostrar:

- nombre de Solution;
- ruta de su .sln;
- proyectos asociados;
- enlaces a cada proyecto documentado.

Un proyecto compartido entre varias soluciones conserva una única identidad.

No duplicar documentos de proyecto por cada Solution a la que pertenece.

---

# 5. Navegación Project → Component / Archivo

Agregar al documento de cada Project una sección:

Componentes y archivos

Debe permitir acceder a los elementos identificados como pertenecientes realmente al proyecto.

Distinguir:

- Component;
- SourceArtifact;
- clase;
- formulario;
- módulo de código;
- archivo fuente.

Evitar duplicar visualmente el mismo archivo si contiene varios componentes.

La navegación debe poder representar:

Un archivo → varios componentes.

Y:

Un componente → su archivo de origen.

No asumir relación 1:1.

---

# 6. Pertenencia real

La relación Project → Archivo debe derivarse de la evidencia existente.

Preferir:

- Project;
- compile_items/content_items;
- SourceArtifact;
- Component;
- provenance;
- relaciones deterministas existentes.

No asignar un archivo al proyecto solamente porque:

- comparte un nombre;
- aparece durante un flujo;
- está referenciado desde una llamada;
- se encuentra en una carpeta de nombre parecido.

Si la pertenencia es ambigua, declararlo.

No fabricar relaciones.

---

# 7. Documento principal del Project

Debe mantenerse breve.

Ejemplo conceptual:

Proyecto BLInterfazSAP

Resumen
Tipo de proyecto
Tipo técnico de salida
Soluciones
Dependencias
Flujos
Acceso a datos

Componentes y archivos
- BLInterfazSAP.vb → Ver componentes
- AssemblyInfo.vb → Ver detalle

No volcar cientos de componentes o archivos dentro del README del proyecto.

Para proyectos grandes, utilizar índice y particionado.

---

# 8. Documento de componente

Cuando exista evidencia suficiente, mostrar:

- nombre;
- tipo;
- proyecto propietario;
- archivo fuente;
- descripción estructural determinista;
- métodos identificados;
- relaciones técnicas relevantes;
- enlaces a evidencia detallada.

No inventar responsabilidades funcionales.

Por ejemplo:

Si la evidencia demuestra que una clase se llama BLInterfazSAP, NO afirmar automáticamente que administra todas las operaciones SAP solo por su nombre.

---

# 9. Métodos

Permitir que el desarrollador encuentre los métodos conocidos de un componente.

Mantener la lista principal breve.

Mostrar, cuando exista:

- nombre;
- archivo;
- línea;
- tipo/visibilidad si está disponible;
- acceso al detalle técnico.

No inventar firmas, parámetros, líneas ni sobrecargas.

No introducir una identidad canónica ficticia de método si Evidence Core no permite distinguirla.

Si la información disponible es parcial, mostrar solo lo que puede demostrarse.

---

# 10. Evidencia detallada bajo demanda

Definición obligatoria:

La evidencia ya fue recopilada por LegacyMapper.

El enlace solamente permite consultarla sin saturar los niveles superiores.

No ejecutar IA ni análisis adicional cuando el usuario abre el enlace.

El detalle puede contener, cuando exista:

- archivo y línea;
- método;
- llamadas detectadas;
- dependencias;
- acceso a datos;
- SQL/procedimientos almacenados;
- recorridos relacionados;
- información no resuelta;
- referencias hacia Evidence Core.

No exigir que todos los elementos tengan todos esos datos.

No mostrar información que no esté respaldada por evidencia.

---

# 11. Navegación y enlaces

Los enlaces internos deben ser:

- relativos;
- deterministas;
- funcionales;
- legibles;
- compatibles con nombres duplicados;
- compatibles con Windows y diferencias de mayúsculas/minúsculas.

Cada documento profundo debe permitir volver al nivel superior.

Ejemplo:

Método → Componente → Proyecto → Solution.

Evitar navegación únicamente mediante IDs internos.

---

# 12. Particionado

Reutilizar el sistema combinado de V5.2:

- max_items_per_part;
- max_bytes_per_part.

Aplicarlo también a:

- índices de componentes;
- índices de archivos;
- listados de métodos;
- detalle técnico.

No crear archivos gigantes por añadir esta nueva navegación.

Mantener determinismo.

---

# 13. Arquitectura

Mantener:

Evidence Core
    ↓
Audience Transformation
    ↓
Output Profile
    ↓
Template
    ↓
Markdown Renderer

Extender únicamente los contratos necesarios para representar Component/Archivo.

No introducir lógica de clasificación o pertenencia en MarkdownRenderer.

Mantener templates declarativos.

No implementar navegación mediante Markdown construido manualmente en múltiples funciones Python.

---

# 14. General Overview

General Overview debe permanecer simple.

NO introducir ahí:

- listas exhaustivas de clases;
- métodos;
- llamadas;
- archivos individuales;
- hashes;
- IDs internos.

La ampliación pertenece principalmente a Developer Technical.

No romper las mejoras de claridad alcanzadas en R3.1 y R3.2.

---

# 15. Compatibilidad

Mantener:

documentation/

legacy intacta.

El destino nuevo sigue siendo:

documentation_v52/

No eliminar ni reemplazar los generadores legacy.

No modificar Evidence Core.

No implementar D-5.

No modificar V5.1.

---

# 16. Regresiones obligatorias

Confirmar que siguen funcionando:

- identidad real de BLInterfazSAP;
- Solution → Project;
- proyecto compartido entre Solutions;
- pantallas propias vs. flujos recibidos;
- acceso directo vs. indirecto;
- dirección de dependencias;
- tipo técnico de salida;
- métrica real de acceso a datos;
- technical noise;
- RUN_SUMMARY;
- custom templates;
- AI OFF;
- runtime independence.

---

# 17. Tests nuevos

Agregar tests para:

- Project → SourceArtifact real;
- SourceArtifact → Component;
- un archivo con varios componentes;
- componente sin pertenencia demostrable;
- archivo homónimo en distintos proyectos;
- proyecto compartido entre soluciones;
- navegación de ida y vuelta;
- enlaces relativos;
- particionado;
- determinismo;
- ausencia de proyectos ficticios;
- ausencia de métodos inventados;
- evidencia disponible bajo demanda;
- documentos principales breves;
- legacy intacto.

No depender exclusivamente de snapshots completos.

---

# 18. Prueba real IST

Ejecutar sobre:

C:\Users\cgalianj\source\IST_40\Operacional

Destino:

C:\PruebasLegacyMapper\Resultados\v5_2_r3_3_validation\

No sobrescribir resultados anteriores.

Comprobar:

- navegación real Solution → Project → Component/Archivo;
- documentos de componentes;
- acceso al detalle;
- enlaces;
- nombres únicos;
- ausencia de archivos gigantes;
- determinismo;
- AI OFF;
- documentación legacy intacta.

No considerar suficiente que los tests pasen.

Leer físicamente los documentos generados.

---

# 19. Muestra humana autocontenida

Crear:

C:\PruebasLegacyMapper\Resultados\v5_2_r3_3_validation\human_review_sample\

Esta vez la muestra debe ser completamente navegable para los casos seleccionados.

Incluir:

1. General Overview.
2. Una Solution real.
3. BLInterfazSAP como Project real.
4. BLInterfazSAP.vb como archivo.
5. Su componente/clase real.
6. Al menos un método identificado.
7. Su evidencia detallada, si existe.
8. Un proyecto Web.
9. Un proyecto con varios componentes.
10. Un caso con pertenencia o información no resuelta.

La muestra debe contener los documentos de destino necesarios para recorrer los ejemplos.

No basta con copiar el README y dejar sus enlaces importantes apuntando a archivos ausentes.

Los enlaces a otros elementos fuera de la muestra pueden indicarse como no incluidos en la muestra, pero los recorridos seleccionados deben funcionar completamente.

No modificar manualmente los documentos para mejorar su apariencia.

Las copias deben provenir de la salida productiva.

---

# 20. Revisión humana interna

Comprobar leyendo la muestra:

¿Entiendo la Solution?

¿Distingo el Project de sus archivos?

¿Puedo encontrar una clase?

¿Puedo encontrar sus métodos?

¿Puedo consultar el detalle técnico?

¿Puedo regresar fácilmente al Project?

¿Los documentos principales continúan siendo pequeños?

¿La navegación resulta natural?

Claude no puede aprobar en nombre del Technical Lead.

---

# 21. Suite completa

Ejecutar:

python -m unittest discover -s tests

Requerido:

0 failures
0 errors

Informar skips.

---

# 22. Restricciones

NO:

- modificar Evidence Core;
- reabrir V5.1;
- inventar identidad de métodos;
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

---

# 23. Resultado

Crear exclusivamente:

docs/V5/V5_2_R3_3_COMPONENT_NAVIGATION.md

Estructura:

1. Estado.
2. Qué se implementó.
3. Navegación Solution → Project.
4. Navegación Project → Component/Archivo.
5. Métodos y evidencia bajo demanda.
6. Identidad y pertenencia.
7. Particionado.
8. Compatibilidad con R3.2.
9. Validación IST.
10. Suite.
11. GAPs y deuda restante.
12. Ruta de muestra humana.
13. Qué debe revisar el Technical Lead.
14. Conclusión.

Usar lenguaje sencillo.

---

# 24. Estados permitidos

Terminar exactamente con uno:

V5_2_R3_3_READY_FOR_HUMAN_REVIEW

V5_2_R3_3_BLOCKED

V5_2_R3_3_CONFLICT

V5_2_R3_3_OPEN_DECISION

No declarar READY_FOR_R4.

La aprobación humana sigue siendo obligatoria.

---

# 25. Regla final

Crear únicamente el resultado solicitado y la muestra humana correspondiente.

No crear prompt R4.

Esperar revisión externa.