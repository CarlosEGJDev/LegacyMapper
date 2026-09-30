# V5.2 R3.1 — Correcciones de claridad semántica de documentación humana

## Rol

Trabaja sobre:

C:\dev\LegacyMapper

V5.1 está cerrada.

V5.2 R0, R1 y R2 están implementados.
V5.2 R3 pasó técnicamente pero NO obtuvo todavía aprobación humana.

Esta ronda existe únicamente para corregir problemas de claridad y significado detectados durante la revisión humana.

NO rediseñar Profiles, Templates ni Renderer.
NO implementar funcionalidades de V5.3+.
NO modificar Evidence Core salvo que se descubra un defecto bloqueante real; en ese caso documentar y detener.

---

# 1. Documentos obligatorios

Leer:

- docs/V5/V5_2_R0_DOCUMENTATION_BASELINE.md
- docs/V5/V5_2_R1_DOCUMENTATION_CONTRACT_DESIGN.md
- docs/V5/V5_2_R2_DOCUMENTATION_ENGINE_IMPLEMENTATION.md
- docs/V5/V5_2_R3_TECHNICAL_AND_HUMAN_VALIDATION.md

Revisar también la muestra humana real usada en R3.

---

# 2. Objetivo

Corregir la documentación para que una persona entienda correctamente:

- qué pertenece realmente a cada proyecto;
- qué elementos solo participan en un flujo;
- qué acceso a datos es directo o indirecto;
- qué dependencias son internas o externas;
- qué métricas representan realmente acceso a datos;
- qué significa cada sección sin conocer internamente LegacyMapper.

La documentación debe ser correcta semánticamente, no solo técnicamente correcta.

---

# 3. Jerarquía .NET obligatoria

Para el adapter .NET de referencia, la documentación debe respetar esta jerarquía conceptual:

Sistema analizado
    ↓
Solution (.sln)
    ↓
Project (.vbproj / .csproj)
    ↓
Componentes / clases / archivos

No tratar como módulo o proyecto:

- archivos fuente;
- clases;
- WebForms;
- DLL references;
- componentes;
- dependencias;
- nodos encontrados durante un flujo.

Un elemento que aparece durante un flujo NO pasa automáticamente a pertenecer al proyecto documentado.

---

# 4. Concepto de módulo

En esta implementación:

- Solution representa la agrupación superior .NET.
- Project representa el módulo técnico real dentro de esa solución.

Evitar usar "módulo" para elementos que no correspondan a un Project real.

Si la documentación usa la palabra "módulo", debe quedar explícito que significa:

"Proyecto .NET (.vbproj / .csproj)"

No inventar agrupaciones funcionales/de negocio.

---

# 5. Propiedad vs participación en flujos

Corregir la presentación para distinguir como mínimo:

## Elementos propios del proyecto

Aquellos que realmente pertenecen al Project.

Ejemplos:

- componentes;
- clases;
- archivos;
- puntos de entrada propios;
- acceso directo a datos;
- dependencias declaradas por el proyecto.

## Flujos que pasan o llegan al proyecto

Flujos cuyo origen puede estar en otro Project pero que alcanzan componentes de este proyecto.

NO presentarlos como si sus pantallas o eventos pertenecieran al proyecto destino.

Ejemplo de presentación esperada:

Proyecto blPENResoluciones

Elementos propios
- ...

Flujos que llegan a este proyecto
- WebPEN... → blPENResoluciones...
- WebPEN... → blPENResoluciones...

Nunca:

"Este módulo tiene 15 pantallas"

si esas pantallas pertenecen realmente a otros proyectos.

---

# 6. Acceso directo vs indirecto a datos

Corregir la ambigüedad encontrada en R3.

Distinguir:

## Acceso directo a datos

El propio Project contiene el punto de acceso a datos.

## Datos alcanzados por sus flujos

Un flujo originado en el proyecto termina alcanzando datos a través de otro Project/capa.

Ejemplo:

Web Project
    ↓
Business Project
    ↓
Database

El Web Project puede tener:

Acceso directo a datos: ninguno.

Pero:

Sus flujos alcanzan indirectamente:
- procedimiento X
- procedimiento Y

No presentar ambas cosas como una contradicción.

---

# 7. Métrica de acceso a datos

Corregir el hallazgo de R3.

NO considerar como "acceso a datos confirmado" una operación que solo representa:

- BeginTrans;
- Commit;
- Rollback;
- control transaccional;
- infraestructura equivalente.

La Vista General debe diferenciar:

- flujos que alcanzan una operación real de datos;
- flujos que solo alcanzan infraestructura/transacciones.

No usar una cifra que pueda inducir al lector a creer que una transacción es una consulta/SP real.

Recalcular la métrica de forma determinista usando la evidencia existente.

No modificar Evidence Core para lograrlo si puede derivarse desde los datos actuales.

---

# 8. Terminología humana

Reducir jerga innecesaria.

Revisar textos como:

- flujo;
- destino confirmado;
- evidencia estática;
- INTERPRETED;
- LegacyMapper;
- stored_procedure;
- web_lifecycle;
- web_event.

Cuando aparezcan en documentación humana:

- reemplazar por términos simples en N1/N2;
- conservar el término técnico solo en Developer Technical cuando sea útil.

Ejemplo:

"Destino confirmado"
→ "Resultado identificado"

"stored_procedure"
→ "Procedimiento almacenado"

"web_event"
→ "Evento web"

No ocultar significado técnico necesario.

---

# 9. Dependencias externas

Revisar el documento actual de sistemas externos/dependencias.

No mezclar bajo un mismo concepto sin aclaración:

- proyectos internos;
- bibliotecas internas compartidas;
- bibliotecas de terceros;
- servicios externos;
- bases de datos.

Clasificar únicamente cuando la evidencia permita hacerlo.

Si no puede clasificarse con certeza:

usar categoría clara como:

"Dependencia no clasificada"

No inventar que algo es externo.

---

# 10. Vista General

La Vista General debe dejar de parecer únicamente un inventario.

Sin inventar negocio, debe explicar estructuralmente:

1. Qué se analizó.
2. Cómo está organizado.
3. Cuáles son las Solutions principales.
4. Qué Projects contienen.
5. Cómo se comunican a grandes rasgos.
6. Qué procesos/flujos fueron observados.
7. Qué acceso real a datos fue confirmado.
8. Qué dependencias externas se identificaron.
9. Qué no pudo determinarse.

Debe ser corta y comprensible.

No convertirla en una tabla gigante.

---

# 11. Developer Technical

Para cada Project real, mostrar conceptualmente:

Proyecto
├─ Resumen
├─ Elementos propios
├─ Puntos de entrada propios
├─ Flujos originados aquí
├─ Flujos que llegan aquí
├─ Acceso directo a datos
├─ Datos alcanzados indirectamente
├─ Dependencias declaradas
├─ Código relacionado
└─ Información no resuelta

No todas las secciones necesitan existir físicamente si están vacías.

Templates pueden omitirlas condicionalmente.

---

# 12. Copias / Backup

No inventar cuál Project es producción.

Si existen proyectos/rutas duplicadas en:

Backup
_back
u otras copias

mostrar su ruta claramente.

No asignar silenciosamente nombres "-2", "-3" sin contexto humano suficiente.

Cuando sea posible, mostrar:

Nombre del proyecto
Ruta

para distinguirlos.

Si se necesita un sufijo técnico para nombre de archivo, no convertir ese sufijo en el nombre visible del módulo.

---

# 13. Technical Noise

Agregar únicamente ajustes declarativos necesarios para el ruido residual detectado en R3.

Ejemplos:

- DataBind;
- llamadas de controles UI;
- infraestructura similar.

Preferir modificar:

noise policy JSON

y NO lógica Python.

No iniciar una limpieza infinita.

La regla es:

si no ayuda a comprender el comportamiento principal,
resumir u ocultar del cuerpo,
manteniendo detalle disponible.

---

# 14. RUN_SUMMARY

Corregir P-1 de R3.

`documentation_v52` debe aparecer entre las ubicaciones de salida relevantes del resumen de ejecución.

Aplicar el cambio mínimo compatible con los contratos existentes.

Agregar test.

No rediseñar RUN_SUMMARY.

---

# 15. Flujo → archivo/línea

P-2 sigue siendo mejora no bloqueante.

Investigar únicamente si el dato ya está disponible de forma determinista.

Si puede enlazarse sin nuevo análisis ni modificación de Evidence Core:

puede implementarse.

Si requiere nueva extracción/análisis:

NO hacerlo en esta ronda.

Documentar como deuda posterior.

---

# 16. Arquitectura

Mantener intacta:

Evidence
    ↓
Audience Transformation
    ↓
Profile
    ↓
Template
    ↓
Renderer

Las correcciones semánticas deben vivir principalmente en:

- Audience Transformation;
- Profiles;
- catálogos de idioma;
- noise policy;
- templates.

Renderer no debe aprender semántica de negocio/proyecto.

---

# 17. Tests obligatorios

Agregar tests para demostrar:

- Project real no incorpora pantallas de otro Project como propias;
- flujos originados y flujos recibidos se distinguen;
- acceso directo e indirecto se distingue;
- operaciones transaccionales no cuentan como acceso real a datos;
- nombres visibles de proyectos duplicados incluyen contexto comprensible;
- dependencias internas/externas no se mezclan incorrectamente;
- terminología humana no expone valores técnicos crudos donde exista etiqueta;
- RUN_SUMMARY incluye documentation_v52;
- noise policy nueva funciona;
- documentación legacy permanece intacta;
- determinismo se mantiene.

Evitar tests basados únicamente en snapshots completos.

---

# 18. Prueba real sobre IST

Ejecutar nuevamente sobre:

C:\Users\cgalianj\source\IST_40\Operacional

Usar carpeta nueva bajo:

C:\PruebasLegacyMapper\Resultados\

No sobrescribir R2/R3.

Generar nuevamente la documentación V5.2.

---

# 19. Muestra humana nueva

Crear una nueva muestra equivalente a R3:

human_review_sample/

Incluir:

1. General Overview completo.
2. Proyecto simple.
3. Proyecto medio.
4. Proyecto complejo.
5. Caso con acceso directo a datos.
6. Caso con acceso indirecto a datos.
7. Caso con información no resuelta.

Usar documentos reales sin editar manualmente.

La muestra debe permitir comparar claramente con la anterior.

---

# 20. Revisión humana interna de Claude

Leer físicamente la nueva muestra.

Verificar específicamente:

- ¿Se entiende qué es Solution y qué es Project?
- ¿Las pantallas pertenecen al proyecto correcto?
- ¿Se distingue "propio" de "alcanzado por un flujo"?
- ¿Se distingue acceso directo/indirecto?
- ¿La cifra de acceso real a datos es honesta?
- ¿Las dependencias tienen nombres/categorías comprensibles?
- ¿La Vista General sigue pareciendo un inventario o explica estructura?
- ¿La jerga disminuyó?

Claude NO puede aprobar en nombre del Technical Lead.

---

# 21. Suite completa

Ejecutar:

python -m unittest discover -s tests

Resultado requerido:

0 failures
0 errors

Reportar skips.

---

# 22. No hacer

NO:

- modificar arquitectura V5.2;
- modificar Evidence Core salvo bloqueo demostrado;
- reabrir V5.1;
- implementar IA;
- implementar HTML;
- implementar V5.3–V5.9;
- retirar documentation/ legacy;
- crear commits;
- hacer push;
- modificar roadmap;
- modificar PROJECT_STATE;
- crear documentos auxiliares;
- crear prompt R4.

---

# 23. Resultado documental

Crear EXACTAMENTE:

docs/V5/V5_2_R3_1_HUMAN_SEMANTIC_CORRECTIONS.md

Debe ser corto y entendible.

Incluir:

1. Estado.
2. Qué problemas humanos se corrigieron.
3. Jerarquía Solution/Project final.
4. Propiedad vs participación en flujo.
5. Acceso directo vs indirecto.
6. Métrica corregida de acceso a datos.
7. Dependencias.
8. Terminología.
9. Ruido técnico.
10. RUN_SUMMARY.
11. GAPs/deuda restante.
12. Prueba IST.
13. Suite.
14. Ruta de nueva muestra humana.
15. Qué debe revisar el Technical Lead.
16. Conclusión.

---

# 24. Estado final permitido

Terminar exactamente con uno:

V5_2_R3_1_READY_FOR_HUMAN_REVIEW

V5_2_R3_1_BLOCKED

V5_2_R3_1_CONFLICT

V5_2_R3_1_OPEN_DECISION

NO declarar READY_FOR_R4.

La aprobación humana sigue siendo obligatoria.

---

# 25. Regla final

Al terminar:

- crear únicamente el documento solicitado;
- crear únicamente la nueva muestra humana dentro del output de validación;
- no crear prompt R4;
- esperar revisión externa.