# V5.2 R2 — Documentation Profiles, Templates & Markdown Renderer Implementation

## Rol

Trabaja sobre:

C:\dev\LegacyMapper

V5.1 está cerrada.

V5.2 R0 y R1 están aprobados.

Esta ronda implementa por primera vez la arquitectura documental definida en:

docs/V5/V5_2_R0_DOCUMENTATION_BASELINE.md
docs/V5/V5_2_R1_DOCUMENTATION_CONTRACT_DESIGN.md

No reinterpretar silenciosamente esos contratos.

---

# 1. Objetivo

Implementar el sistema V5.2:

Evidence Core
    ↓
Audience Transformation
    ↓
Output Profile
    ↓
Template
    ↓
Markdown Renderer
    ↓
documentation_v52/

La documentación nueva debe ser:

- simple de leer;
- progresiva;
- determinista;
- configurable;
- independiente de IA;
- separada de la documentación legacy.

---

# 2. Principio humano obligatorio

La documentación NO debe parecer un dump técnico del Evidence Core.

Regla:

Nivel 1 — Qué es
Nivel 2 — Cómo funciona
Nivel 3 — Cómo está construido
Nivel 4 — Evidencia detallada

El lector debe poder detenerse en cualquier nivel.

Los detalles técnicos profundos nunca deben dominar visualmente el documento principal.

---

# 3. Decisiones cerradas del Technical Lead

## D-52-01 — Particionado

Usar límite combinado:

- cantidad de elementos;
- tamaño aproximado del archivo.

Se particiona cuando cualquiera de los límites se alcanza.

---

## D-52-02 — INTERPRETED

La documentación determinista funciona aunque no exista contenido interpretado.

No inventar propósito de negocio.

Debe existir el punto de extensión para:

INTERPRETED

pero NO implementar IA.

---

## D-52-03 — Ruido técnico

La política de ruido pertenece al Profile.

Debe ser configuración declarativa, no lógica hardcodeada en el renderer.

---

## D-52-04 — Renderer

Implementar únicamente Markdown en V5.2.

NO implementar HTML.

---

## D-52-05 — Transición

La nueva documentación debe convivir temporalmente con:

documentation/

Nuevo destino:

documentation_v52/

No modificar ni reemplazar todavía documentation/.

---

# 4. Decisiones menores cerradas para R2

## Template custom inválido

Default:

custom inválido
→ warning visible
→ fallback al template default

Debe existir soporte conceptual/configurable para modo estricto:

custom inválido
→ FAILURE

No es obligatorio exponer CLI final del modo estricto en esta ronda si todavía no existe contrato CLI adecuado.

---

## Configuración declarativa

Noise policies, profiles, templates y catálogos de idioma deben vivir como datos configurables.

Preferir formatos simples y legibles.

No incrustar grandes configuraciones dentro de código Python.

La ubicación física exacta puede decidirse durante la implementación, pero debe quedar claramente separada del código productivo.

---

## Directorio nuevo

Usar:

documentation_v52/

Subdirectorios:

documentation_v52/general/
documentation_v52/developer/

---

## GAPs

No modificar V5.1 silenciosamente.

Si un dato necesario no puede obtenerse desde Evidence Core o información ya disponible:

- registrar GAP;
- usar fallback honesto;
- continuar cuando sea posible.

Solo bloquear si el perfil no puede cumplir su función mínima.

---

# 5. Arquitectura obligatoria

Implementar responsabilidades separadas.

## Audience Transformation

Responsable de:

- leer Evidence Core;
- agregar;
- resumir;
- clasificar;
- ordenar;
- preparar navegación;
- conservar trazabilidad.

NO renderiza Markdown.

NO decide formato.

NO llama IA.

---

## Output Profile

Responsable de:

- audiencia;
- nivel máximo;
- categorías visibles;
- ruido;
- idioma;
- comportamiento ante unresolved;
- DETAIL_ON_DEMAND;
- política de partición.

NO renderiza.

---

## Template

Responsable de:

- títulos;
- orden;
- secciones;
- bloques;
- tablas;
- condicionales;
- disclaimers;
- estructura.

NO decide importancia ni ruido.

---

## Renderer

Responsable de:

- Markdown;
- escape;
- links;
- nombres;
- particionado;
- escritura física;
- determinismo.

NO decide contenido.

---

# 6. Implementar los dos Profiles

Implementar exactamente:

general_overview
developer_technical

No crear perfiles adicionales.

---

# 7. Profile: General Overview

Debe generar documentación que una persona no desarrolladora pueda entender.

Debe priorizar:

- sistema analizado;
- módulos principales;
- relaciones generales;
- procesos observados;
- sistemas externos;
- datos utilizados;
- limitaciones conocidas.

No mostrar normalmente:

- IDs internos;
- hashes;
- JSON;
- nombres internos del resolver;
- detalles de implementación de LegacyMapper;
- listas exhaustivas.

---

# 8. Propósito de negocio sin IA

Si no existe contenido INTERPRETED:

NO inventar qué hace el sistema.

Mostrar una frase neutral equivalente a:

"El propósito funcional global no pudo determinarse únicamente desde la evidencia estática disponible."

La documentación debe seguir siendo útil debajo de esa frase.

---

# 9. Profile: Developer Technical

Debe generar una navegación parecida a:

Developer README
    ↓
Módulo
    ├─ Resumen
    ├─ Puntos de entrada
    ├─ Flujos
    ├─ Acceso a datos
    ├─ Dependencias
    ├─ Información no resuelta
    └─ Detalle técnico

Debe priorizar:

- módulos/proyectos;
- responsabilidad cuando pueda inferirse sin inventar;
- estructura;
- puntos de entrada;
- flujos;
- acceso a datos;
- dependencias;
- archivos/líneas;
- unresolved resumido.

El detalle exhaustivo debe quedar bajo demanda.

---

# 10. Categorías de presentación

Implementar:

KEEP_SIMPLE
KEEP_TECHNICAL
DETAIL_ON_DEMAND
INTERNAL_ONLY

Reglas:

General Overview:
- KEEP_SIMPLE
- resumen agregado de KEEP_TECHNICAL

Developer Technical:
- KEEP_SIMPLE
- KEEP_TECHNICAL
- DETAIL_ON_DEMAND mediante enlaces/documentos hijos

INTERNAL_ONLY:
- nunca visible por defecto.

No eliminar información del Evidence Core.

---

# 11. Technical Noise Policy

Implementar una policy declarativa.

Debe poder representar categorías como:

- exception_handling
- transaction_control
- ui_messaging
- string_utility
- resource_cleanup

Las reglas concretas del adapter actual pueden incluir nombres/patrones VB.NET existentes.

Pero el contrato debe seguir siendo agnóstico.

Debe permitir:

hide
summarize
show

El contenido oculto del cuerpo puede continuar disponible en DETAIL_ON_DEMAND.

---

# 12. AudienceDocumentModel

Implementar una representación intermedia neutral para humanos.

Debe contener únicamente lo necesario para documentación.

Debe preservar enlaces hacia evidencia/origen.

No debe copiar todo Evidence Core indiscriminadamente.

Debe ser suficientemente neutral para que:

Profile
Template
Renderer

no necesiten conocer detalles internos del parser o resolver.

---

# 13. Templates declarativos

Implementar templates reales.

No mantener todo el Markdown embebido en funciones Python.

Los templates deben ser declarativos y seguros.

No permitir:

- ejecución arbitraria de Python;
- modificación del Evidence Core;
- side effects;
- llamadas de sistema.

---

# 14. Templates default

Implementar como mínimo los contratos definidos en R1.

General:

- overview.system
- overview.modules
- overview.external_systems
- overview.data
- overview.limitations

Developer:

- dev.index
- dev.module
- dev.flow_summary
- dev.data_access_summary
- dev.dependency_summary
- dev.unresolved_summary
- dev.technical_detail

La implementación puede agrupar archivos físicos si eso simplifica el diseño, siempre que las responsabilidades sigan separadas.

---

# 15. Custom Templates

Implementar:

custom
    ↓ si existe
default

Debe soportar:

- override parcial;
- fallback automático;
- validación;
- warning claro si custom es inválido.

Default:

custom inválido
→ warning
→ default

No ocultar silenciosamente el error.

Si se implementa modo estricto:

custom inválido
→ FAILURE

No es obligatorio crear una nueva CLI compleja solo para esto.

---

# 16. Catálogo de idioma

Implementar textos fijos mediante catálogo.

Default:

es

No crear nuevas funciones:

*_es
*_en

como mecanismo de idioma.

No implementar traducción automática.

Debe ser posible añadir otro catálogo posteriormente.

---

# 17. Renderer Markdown

Implementar un Markdown Renderer separado.

Debe producir bytes deterministas.

Responsabilidades:

- render físico;
- nombres;
- links;
- escape;
- particionado;
- índices.

No debe contener decisiones de audiencia.

---

# 18. Particionado combinado

Implementar:

max_items_per_part
max_bytes_per_part

Una parte termina cuando cualquiera se alcanza.

Requisitos:

- orden determinista;
- nombres deterministas;
- índice pequeño;
- enlaces anterior/siguiente;
- nunca partir un elemento individual;
- elemento mayor que límite:
  - se escribe solo;
  - warning;
  - no truncar.

---

# 19. Defaults de particionado

NO inventar cifras finales sin medir.

Durante R2:

- probar varias configuraciones razonables;
- medir sobre IST real;
- seleccionar defaults que produzcan archivos cómodos para lectura.

Objetivo:

evitar nuevamente archivos multi-megabyte difíciles de abrir.

Documentar la medición.

---

# 20. General Overview real

Generar sobre IST un General Overview real.

Evaluar manualmente si responde de forma razonable:

- qué sistema se analizó;
- módulos;
- relaciones;
- procesos;
- sistemas externos;
- datos;
- limitaciones.

No evaluar únicamente estructura JSON o tests.

Leer físicamente el Markdown generado.

---

# 21. Developer Technical real

Generar documentación Developer Technical real.

Seleccionar al menos:

- módulo simple;
- módulo medio;
- módulo complejo;
- caso con acceso a datos;
- caso con unresolved.

Verificar lectura humana.

El documento raíz nunca debe contener el detalle completo de todo el sistema.

---

# 22. GAP — agrupación de módulos

R1 detectó que todavía debe confirmarse qué significa "módulo" con Evidence Core real.

Investigar.

Preferir fuentes deterministas existentes:

- Solution;
- Project;
- relaciones;
- estructura física.

No inventar agrupaciones de negocio.

Si solo puede asegurarse Project/Solution:

usar esos conceptos explícitamente en documentación.

Registrar GAP para futura interpretación si es necesario.

---

# 23. GAP — Flows / Entry Points

Confirmar que V5.2 puede obtener lo necesario para Developer Technical desde:

Evidence Core

o desde una proyección compatible legitimada por la arquitectura actual.

No modificar V5.1 silenciosamente.

Si falta algo:

registrar GAP.

No duplicar un segundo análisis.

---

# 24. GAP — Sistemas externos / datos

Validar que:

ExternalDependency
DataObject

permiten construir una vista humana útil.

Agregar/resumir determinísticamente.

No mostrar IDs internos como interfaz.

---

# 25. GAP — Configuraciones Backup

NO intentar decidir automáticamente qué Web.config es producción si no existe evidencia suficiente.

General Overview debe evitar afirmar algo no demostrable.

Developer Technical puede listar configuraciones con su ruta y señalar ambigüedad cuando corresponda.

No inventar clasificación production/backup.

---

# 26. Legacy compatibility

Durante toda V5.2 R2:

documentation/

debe quedar intacto.

La nueva salida va a:

documentation_v52/

No eliminar ni modificar generadores legacy.

No cambiar consumidores existentes.

---

# 27. Integración productiva

La nueva documentación debe generarse desde el producto real.

No debe existir solamente en:

tools/
tests/
scripts de desarrollo.

Integrar en el pipeline productivo de forma aditiva.

La falla de V5.2 no debe ocultarse.

Definir claramente su comportamiento de error sin romper silenciosamente la ejecución.

Si existe conflicto con contratos actuales de stages/status:

documentarlo antes de inventar un estado nuevo.

---

# 28. AI independence

Debe funcionar con AI = OFF.

No importar:

- OpenAI
- Anthropic
- Claude
- Ollama
- Gemini
- otros providers

INTERPRETED debe permanecer como punto de extensión opcional.

No implementar V5.5.

---

# 29. Runtime independence

Runtime no debe depender de:

- tools/
- tests/
- docs/
- prompts/
- PROJECT_STATE

Configuraciones default necesarias para ejecutar el producto sí pueden formar parte del paquete/runtime productivo.

---

# 30. Tests obligatorios

Agregar tests suficientes para:

- General Overview;
- Developer Technical;
- separación profile/template/renderer;
- categorías;
- INTERNAL_ONLY no visible;
- technical noise;
- templates default;
- custom override parcial;
- custom inválido → warning + fallback;
- determinismo;
- particionado por items;
- particionado por bytes;
- overflow individual;
- links entre partes;
- idioma default;
- frase neutral sin INTERPRETED;
- ejecución AI OFF;
- documentación legacy intacta;
- integración productiva.

Evitar tests excesivamente acoplados al texto literal completo.

Probar contratos y estructura.

---

# 31. Prueba real sobre IST

Target:

C:\Users\cgalianj\source\IST_40\Operacional

Usar carpeta nueva bajo:

C:\PruebasLegacyMapper\Resultados\

No sobrescribir resultados anteriores.

Generar:

documentation/
documentation_v52/

Comparar.

Medir como mínimo:

- tamaño total nuevo;
- tamaño máximo de archivo;
- número de archivos;
- distribución de tamaños;
- cantidad de particiones;
- existencia de ambos profiles.

No usar tamaño total más pequeño como único criterio de calidad.

La meta es legibilidad.

---

# 32. Revisión humana obligatoria

Inspeccionar físicamente documentos generados.

Responder:

## General Overview

¿Una persona no desarrolladora puede entender a grandes rasgos el sistema?

## Developer Technical

¿Un desarrollador puede encontrar rápidamente:

- módulo;
- punto de entrada;
- flujo;
- acceso a datos;
- dependencia;
- archivo relacionado?

## Progressive disclosure

¿El detalle profundo está disponible sin dominar la lectura?

## Ruido

¿Los detalles técnicos irrelevantes dejaron de dominar?

Esta revisión debe formar parte del resultado R2.

---

# 33. No hacer

NO:

- modificar Evidence Core;
- reabrir V5.1;
- implementar D-5;
- implementar HTML;
- implementar IA;
- implementar V5.3–V5.9;
- eliminar documentation/ legacy;
- hacer refactorización general;
- modificar roadmap;
- modificar PROJECT_STATE;
- crear commits;
- hacer push;
- crear documentación auxiliar;
- crear FIX_NOTES.md;
- crear PATCH_RESULT.md;
- crear DIAGNOSTICO_EXTRA.md;
- crear TODO_FIX.md;
- crear prompts adicionales.

---

# 34. Resultado documental

Crear EXACTAMENTE:

docs/V5/V5_2_R2_DOCUMENTATION_ENGINE_IMPLEMENTATION.md

Mantenerlo comprensible.

Debe contener:

1. Estado.
2. Qué se implementó.
3. Arquitectura final de R2.
4. General Overview.
5. Developer Technical.
6. Profiles.
7. Templates.
8. Renderer Markdown.
9. Technical Noise Policy.
10. Idioma.
11. Particionado.
12. Custom templates.
13. GAPs encontrados.
14. Integración productiva.
15. Compatibilidad legacy.
16. Prueba real IST.
17. Revisión humana.
18. Suite completa.
19. Deuda pendiente.
20. Evidencia para pasar a R3.

Evitar llenar el resultado con detalles internos que no sean necesarios para evaluar V5.2.

---

# 35. Estados finales permitidos

Terminar exactamente con uno:

V5_2_R2_READY_FOR_R3

V5_2_R2_BLOCKED

V5_2_R2_CONFLICT

V5_2_R2_OPEN_DECISION

No declarar V5.2 cerrada.

---

# 36. Regla final

Al terminar:

- generar únicamente `docs/V5/V5_2_R2_DOCUMENTATION_ENGINE_IMPLEMENTATION.md`;
- no crear prompt R3;
- no modificar roadmap;
- no modificar PROJECT_STATE;
- esperar revisión externa.