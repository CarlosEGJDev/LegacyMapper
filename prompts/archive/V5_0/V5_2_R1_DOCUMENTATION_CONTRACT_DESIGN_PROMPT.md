# V5.2 R1 — Documentation Profiles, Templates & Renderer Contract

## Rol

Trabaja sobre:

C:\dev\LegacyMapper

V5.1 está formalmente cerrada.

V5.2 R0 está aprobado.

Esta ronda es exclusivamente de contrato y diseño.

NO implementar todavía el motor de templates.
NO modificar código productivo.
NO modificar V5.1.

---

# 1. Objetivo

Definir formalmente la arquitectura de documentación humana de V5.2.

Principio central:

Evidence
    ↓
Audience Transformation
    ↓
Output Profile
    ↓
Template
    ↓
Renderer
    ↓
Human Documentation

Separaciones obligatorias:

Evidence != Human Documentation
Profile != Template
Template != Renderer
Template != AI
Profile != AI
Renderer != AI

La documentación base debe funcionar completamente sin IA.

---

# 2. Objetivo humano

V5.2 debe resolver el problema detectado en R0:

La documentación actual contiene información correcta, pero presenta demasiado detalle y no permite comprender el sistema progresivamente.

Regla principal:

> Una persona debe poder entender primero el sistema y profundizar técnicamente solo cuando lo necesite.

La documentación debe organizarse conceptualmente en niveles:

Nivel 1 — Qué es
Nivel 2 — Cómo funciona
Nivel 3 — Cómo está construido
Nivel 4 — Evidencia técnica detallada

Los niveles profundos no deben dominar visualmente los niveles superiores.

---

# 3. Perfiles mínimos obligatorios

Diseñar exactamente estos dos perfiles iniciales.

## General Overview

Audiencia:

- administrador;
- analista;
- persona técnica no desarrolladora;
- nuevo integrante del proyecto;
- lector que necesita comprender el sistema sin leer código.

Debe responder:

- ¿Qué es este sistema?
- ¿Qué módulos principales tiene?
- ¿Cómo se relacionan?
- ¿Qué procesos principales existen?
- ¿Con qué sistemas externos se comunica?
- ¿Qué datos utiliza a grandes rasgos?
- ¿Qué información no pudo determinarse?

No debe mostrar normalmente:

- IDs internos;
- hashes;
- detalles del resolver;
- listas exhaustivas de métodos;
- evidencia cruda;
- JSON;
- detalles de implementación internos de LegacyMapper.

---

## Developer Technical

Audiencia:

- desarrollador;
- mantenedor;
- arquitecto técnico.

Debe responder:

- ¿Cómo está organizado el sistema?
- ¿Qué módulos/proyectos existen?
- ¿Qué responsabilidad tiene cada uno?
- ¿Qué puntos de entrada existen?
- ¿Cómo fluye una operación?
- ¿Qué componentes participan?
- ¿Dónde está el código relacionado?
- ¿Dónde accede a datos?
- ¿Qué dependencias externas existen?
- ¿Qué partes siguen sin resolver?

Debe usar navegación progresiva:

Resumen
  ↓
Detalle técnico
  ↓
Evidencia bajo demanda

No debe mostrar todo el detalle en el documento principal.

---

# 4. Decisiones aprobadas por el Technical Lead

Estas decisiones están cerradas.

## D-52-01 — Particionado

El particionado debe combinar:

- límite por cantidad;
- límite por tamaño físico.

Un documento no debe crecer indefinidamente solo porque el límite por cantidad todavía no se alcanzó.

El diseño debe permitir límites configurables.

No implementar todavía.

---

## D-52-02 — Interpretación de negocio

El propósito de negocio del sistema puede no ser deducible de forma determinista desde el código.

Debe existir un espacio opcional para contenido:

INTERPRETED

que pueda ser aportado posteriormente por:

- una persona;
- una IA;
- otro sistema externo.

La ausencia de contenido INTERPRETED:

- NO rompe la documentación;
- NO impide generar General Overview;
- NO autoriza inventar el propósito del sistema.

La documentación determinista debe indicar claramente cuando ese contexto no está disponible.

---

## D-52-03 — Ruido técnico

La decisión de ocultar o mostrar ruido técnico pertenece al:

Output Profile

No debe quedar hardcodeada dentro del renderer.

El profile debe poder controlar qué categorías se muestran.

Debe ser extensible/configurable sin modificar código.

---

## D-52-04 — Renderer inicial

V5.2 implementará inicialmente:

Markdown Renderer

HTML queda fuera del alcance mínimo de V5.2.

La arquitectura debe permitir añadir renderers futuros sin rediseñar Profiles o Templates.

---

## D-52-05 — Transición

V5.2 reemplazará gradualmente la documentación humana actual.

Durante la transición:

- la documentación legacy debe mantenerse compatible;
- la nueva documentación debe convivir temporalmente;
- no deben existir dos sistemas permanentes una vez completada la migración.

R1 debe definir el contrato de transición.

---

# 5. Output Profile

Definir formalmente qué es un Output Profile.

Debe controlar:

- audiencia;
- nivel máximo de detalle;
- categorías visibles;
- ruido técnico visible/oculto;
- idioma;
- inclusión/exclusión de secciones;
- comportamiento ante información no resuelta;
- links hacia DETAIL_ON_DEMAND;
- límites de particionado relevantes para esa audiencia.

NO debe controlar:

- sintaxis Markdown;
- HTML;
- formato físico de tablas;
- reglas de escape;
- contenido inventado;
- lógica de extracción del Evidence Core.

---

# 6. Categorías de contenido

Formalizar como mínimo:

KEEP_SIMPLE
KEEP_TECHNICAL
DETAIL_ON_DEMAND
INTERNAL_ONLY

Definir qué significa cada una.

Regla obligatoria:

INTERNAL_ONLY nunca debe aparecer por defecto en documentación humana.

DETAIL_ON_DEMAND debe permanecer accesible sin dominar el documento principal.

---

# 7. Technical Noise Policy

Diseñar el contrato de configuración del ruido técnico.

Debe permitir que un profile determine:

- qué categorías de llamadas son ruido;
- qué patrones pueden ocultarse del cuerpo principal;
- cuándo deben seguir estando disponibles en detalle;
- cómo extender las reglas sin modificar código.

No diseñar reglas específicas solo para VB.NET/WebForms.

El contrato debe ser tecnológicamente agnóstico.

Puede existir un set default para el adapter actual.

---

# 8. Template

Definir formalmente qué es un Template.

Debe controlar:

- títulos;
- encabezados;
- orden de secciones;
- bloques;
- tablas;
- inclusión condicional de secciones;
- layout textual;
- posición de disclaimers;
- enlaces entre niveles de detalle.

NO debe decidir:

- qué es ruido;
- qué evidencia es válida;
- qué datos existen;
- qué nivel de detalle necesita una audiencia;
- lógica de negocio del profile;
- llamadas a IA.

---

# 9. Default Templates

Definir qué templates default necesita V5.2.

Como mínimo estudiar templates para:

General Overview:
- system overview;
- module overview;
- external systems;
- data overview;
- known limitations.

Developer Technical:
- developer index;
- module detail;
- flow summary;
- data access summary;
- dependency summary;
- unresolved summary;
- technical detail.

No crear templates físicos todavía.

R1 define contratos/nombres/responsabilidades.

---

# 10. Custom Templates

Diseñar cómo un usuario podrá proporcionar templates propios posteriormente.

Requisitos:

- no modificar código;
- permitir override parcial;
- fallback automático al template default cuando el custom no exista;
- validación clara;
- error legible cuando el template es inválido;
- evitar que un template pueda modificar Evidence Core.

Definir precedencia conceptual:

custom template
    ↓ si existe
default template

No implementar loader todavía.

---

# 11. Renderer

Definir contrato del Renderer.

Renderer debe encargarse únicamente de:

- transformación de estructura preparada → formato físico;
- Markdown;
- escape;
- nombres de archivo;
- links;
- particionado físico;
- límites por cantidad/tamaño;
- escritura determinista.

Renderer NO debe decidir:

- audiencia;
- importancia del contenido;
- qué es ruido;
- qué datos incluir;
- interpretación de negocio.

---

# 12. Particionado

Diseñar el contrato de particionado combinado.

Debe contemplar:

- máximo de elementos;
- máximo aproximado de bytes;
- particiones deterministas;
- nombres deterministas;
- navegación entre partes;
- índice principal pequeño;
- evitar documentos gigantes.

No fijar cifras arbitrarias sin medir.

R2 deberá medir defaults reales sobre IST.

---

# 13. Audience Transformation

Definir la capa entre Evidence y Profile.

Objetivo:

convertir Evidence Core en una estructura preparada para documentación humana.

Debe:

- agregar;
- resumir determinísticamente;
- clasificar;
- ordenar;
- preparar navegación;
- preservar links hacia evidencia detallada.

NO debe:

- renderizar Markdown;
- inventar propósito;
- llamar IA;
- modificar Evidence Core;
- perder trazabilidad.

Proponer nombre conceptual y contrato mínimo.

---

# 14. General Overview sin IA

Definir cómo debe comportarse el General Overview cuando no existe interpretación de negocio.

Debe producir algo útil usando información determinista disponible.

Ejemplo conceptual:

Sistema analizado
Módulos principales
Dependencias principales
Procesos observados
Sistemas externos
Datos utilizados
Limitaciones conocidas

Cuando no pueda afirmarse "qué hace el sistema":

usar una frase neutral equivalente a:

"El propósito funcional global no pudo determinarse únicamente desde la evidencia estática disponible."

No inventar una narrativa.

---

# 15. INTERPRETED content

Diseñar únicamente el contrato de inserción futura.

Debe distinguir claramente:

DETERMINISTIC
INTERPRETED

El contenido interpretado:

- nunca reemplaza evidencia;
- debe poder faltar;
- debe poder indicar su origen;
- puede enriquecer General Overview;
- podrá provenir de V5.5 u otro proveedor externo.

NO implementar integración AI.

---

# 16. Developer Navigation

Diseñar una navegación simple.

Ejemplo conceptual:

Developer README
    ↓
Module
    ├─ Overview
    ├─ Entry Points
    ├─ Flows
    ├─ Data Access
    ├─ Dependencies
    └─ Details

Evitar navegación basada en IDs internos.

Los IDs pueden existir detrás de links/evidencia, pero no ser la interfaz principal del lector.

---

# 17. Unresolved Information

Mantener el principio histórico:

Nunca inventar.

Pero cambiar presentación.

En lugar de llenar la documentación principal con cientos de elementos no resueltos:

Resumen:
    "Este módulo contiene información no resuelta."

Detalle bajo demanda:
    lista completa

El profile decide cuánto mostrar.

Evidence Core conserva todo.

---

# 18. Idioma

Profile debe controlar idioma.

Para V5.2 mínimo:

- español como default del producto actual.

Definir arquitectura para otros idiomas sin implementar traducción automática.

No crear duplicación de funciones `_es` / `_en` como estrategia futura.

---

# 19. Transición desde documentación legacy

Diseñar cómo coexistirán temporalmente:

documentation/ legacy
new V5.2 documentation

La transición debe:

- no romper consumidores existentes;
- evitar sobreescritura accidental;
- permitir comparación/regresión;
- tener un destino claro para retirar el sistema legacy en una ronda posterior.

Definir naming/directorio conceptual.

No modificar producción todavía.

---

# 20. Relación con Evidence Core

V5.1 permanece autoridad.

V5.2:

- consume Evidence Core;
- no redefine entidades;
- no redefine identidad;
- no cambia provenance;
- no cambia persistencia evidence;
- no implementa D-5.

Si la documentación necesita un dato que Evidence Core no contiene:

registrar GAP.

No modificar Evidence Core silenciosamente.

---

# 21. Relación con AI

La documentación determinista debe funcionar con:

AI = OFF

V5.2 no debe importar ni requerir:

- OpenAI;
- Claude;
- Anthropic;
- Ollama;
- Gemini;
- otro provider.

V5.5 será responsable del Generic AI Provider.

Solo diseñar el punto de extensión INTERPRETED.

---

# 22. Contratos de configuración

R1 debe proponer contratos conceptuales para:

- OutputProfile
- TemplateDescriptor
- RendererContract
- PartitionPolicy
- TechnicalNoisePolicy
- AudienceDocumentModel
- InterpretedSection

No implementar clases todavía.

Para cada contrato indicar:

- propósito;
- campos mínimos;
- campos opcionales;
- responsabilidades;
- qué NO le corresponde.

Evitar schemas excesivamente complejos.

---

# 23. Defaults

Definir defaults razonables para:

General Overview
Developer Technical

El usuario debe poder ejecutar LegacyMapper sin configuración adicional y obtener documentación legible.

No requerir template custom.

No requerir profile custom.

No requerir IA.

---

# 24. Validación futura

Definir qué deberá verificar R2/R3.

Como mínimo:

- documentación determinista;
- custom templates;
- fallback a defaults;
- profiles separados;
- ausencia de INTERNAL_ONLY por defecto;
- progressive disclosure;
- límites de tamaño;
- compatibilidad legacy;
- output reproducible;
- runtime independence;
- AI independence;
- prueba real sobre IST.

---

# 25. No hacer

NO:

- modificar producción;
- implementar templates;
- implementar profiles;
- crear renderer nuevo;
- implementar Markdown renderer nuevo todavía;
- implementar HTML;
- implementar IA;
- modificar Evidence Core;
- implementar D-5;
- implementar V5.3–V5.9;
- modificar roadmap;
- modificar PROJECT_STATE;
- crear commits;
- hacer push;
- crear documentos auxiliares;
- crear prompts adicionales.

---

# 26. Documento de resultado

Crear EXACTAMENTE:

docs/V5/V5_2_R1_DOCUMENTATION_CONTRACT_DESIGN.md

Debe ser comprensible y evitar exceso de detalle técnico.

Estructura mínima:

1. Estado.
2. Principios V5.2.
3. Arquitectura.
4. General Overview.
5. Developer Technical.
6. Output Profile.
7. Categorías de contenido.
8. Technical Noise Policy.
9. Template.
10. Renderer.
11. Audience Transformation.
12. Particionado.
13. INTERPRETED.
14. Idioma.
15. Transición legacy.
16. Contratos conceptuales.
17. Defaults.
18. Gaps detectados.
19. Plan de validación R2/R3.
20. Decisiones abiertas reales.
21. Conclusión.

No llenar el documento con detalles de implementación irrelevantes.

---

# 27. Estados permitidos

Terminar exactamente con uno:

V5_2_R1_CONTRACT_READY

V5_2_R1_BLOCKED

V5_2_R1_CONFLICT

V5_2_R1_OPEN_DECISION

---

# 28. Regla final

Al terminar:

- crear únicamente `docs/V5/V5_2_R1_DOCUMENTATION_CONTRACT_DESIGN.md`;
- no crear prompt R2;
- no modificar código;
- no modificar roadmap;
- no modificar PROJECT_STATE;
- esperar revisión externa.