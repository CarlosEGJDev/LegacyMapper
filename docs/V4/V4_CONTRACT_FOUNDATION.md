# LegacyMapper V4 — Contract Foundation

## 1. Propósito

LegacyMapper V4 evoluciona LegacyMapper desde un sistema centrado principalmente en descubrir conocimiento desde código fuente hacia un mecanismo capaz de construir una Fuente de Conocimiento completa a partir de múltiples fuentes.

V4 debe combinar de forma controlada:

* código fuente;
* evidencia técnica obtenida por LegacyMapper;
* documentación existente;
* requerimientos;
* historias de usuario;
* necesidades;
* información de negocio;
* normas;
* decisiones;
* restricciones;
* información proporcionada por el Líder Técnico.

El resultado será una Fuente de Conocimiento estructurada, trazable y aprobada que posteriormente será consumida por un Plugin multiagente responsable de documentar, diseñar, desarrollar, validar y evolucionar proyectos informáticos.

LegacyMapper construye conocimiento.

El Plugin consume conocimiento.

LegacyMapper no reemplaza al Plugin ni implementa las responsabilidades de sus agentes.

---

## 2. Operador y autoridad

LegacyMapper es una herramienta de uso controlado por el Líder Técnico.

El Líder Técnico es responsable de:

* seleccionar el material entregado a LegacyMapper;
* declarar el contexto necesario;
* identificar el origen del material cuando sea relevante;
* corregir información incorrecta;
* resolver ambigüedades que requieran conocimiento humano;
* aprobar o rechazar propuestas de incorporación;
* aprobar la Fuente de Conocimiento resultante.

LegacyMapper no necesita implementar un modelo complejo de permisos organizacionales en V4.

La autoridad final de incorporación corresponde al Líder Técnico operador.

Esto no elimina la procedencia.

El sistema debe continuar registrando de dónde provino cada conocimiento, aunque el Líder Técnico sea quien autorice finalmente su incorporación.

---

## 3. Principios fundamentales

### 3.1 Mecanismo != contenido

LegacyMapper es mecanismo.

La Fuente de Conocimiento es contenido.

Modificar LegacyMapper no modifica automáticamente las normas, requerimientos o conocimiento del proyecto.

### 3.2 Material de entrada != conocimiento aprobado

Recibir información no significa incorporarla automáticamente.

Debe distinguirse como mínimo:

MATERIAL
→ EVIDENCE
→ INTERPRETATION
→ PROPOSAL
→ APPROVED KNOWLEDGE

cuando esas etapas sean aplicables.

### 3.3 Norma != levantamiento

Debe distinguirse:

AS_IS:
lo que existe o está implementado actualmente.

TO_BE:
lo que debería existir o implementarse.

Una diferencia entre ambos puede producir:

GAP

pero no debe resolverse inventando información.

### 3.4 IA != autoridad

Un modelo puede:

* interpretar;
* relacionar;
* resumir;
* clasificar;
* proponer;
* detectar posibles conflictos;
* detectar posibles faltantes.

Un modelo no puede:

* otorgarse autoridad;
* convertir por sí mismo una interpretación en conocimiento aprobado;
* ocultar incertidumbre;
* inventar evidencia;
* promocionar una hipótesis a hecho.

### 3.5 Procedencia obligatoria

El conocimiento debe poder rastrearse hasta sus fuentes relevantes.

Una conclusión sin procedencia suficiente no debe presentarse como hecho confirmado.

### 3.6 Incertidumbre explícita

LegacyMapper debe preservar estados como:

* confirmado;
* parcial;
* interpretado;
* unresolved;
* conflicting;
* missing;
* superseded;

cuando corresponda.

Nunca debe rellenar silenciosamente información ausente.

---

## 4. Tipos iniciales de fuente

V4 debe poder representar, como mínimo:

DETERMINISTIC_CODE_FACT

HUMAN_REQUIREMENT

USER_STORY

BUSINESS_REQUIREMENT

BUSINESS_CONTEXT

TECHNICAL_CONSTRAINT

CORPORATE_STANDARD

APPROVED_DECISION

EXTERNAL_DOCUMENT

PROJECT_DOCUMENT

AI_INTERPRETATION

UNRESOLVED

Esta lista forma parte del contrato inicial y podrá evolucionar mediante una decisión explícita.

---

## 5. Naturaleza del conocimiento

La Fuente de Conocimiento no es una colección homogénea de hechos.

Debe poder diferenciar, como mínimo:

* norma;
* levantamiento;
* requerimiento;
* necesidad;
* regla de negocio;
* decisión;
* arquitectura;
* proceso;
* flujo;
* catálogo;
* proyecto;
* resolución;
* lección;
* capacitación;
* glosario;
* restricción;
* implementación existente.

La naturaleza debe conservarse durante todo el pipeline.

---

## 6. Estado temporal

Cuando sea aplicable, distinguir:

AS_IS

TO_BE

HISTORICAL

Un conocimiento AS_IS y uno TO_BE pueden coexistir.

Ejemplo:

AS_IS:
la aplicación actualmente utiliza un valor fijo.

TO_BE:
el valor debe ser configurable.

La coexistencia no constituye necesariamente una contradicción.

Puede constituir un GAP.

---

## 7. Conflictos

LegacyMapper debe poder detectar posibles conflictos entre conocimientos.

Un conflicto no debe resolverse automáticamente mediante LLM.

Debe producir una representación explícita que conserve:

* fuentes implicadas;
* statements implicados;
* naturaleza;
* estado;
* evidencia;
* posible causa;
* resolución humana cuando corresponda.

---

## 8. Fuente de Conocimiento

La Fuente de Conocimiento es el conjunto canónico de conocimiento aprobado destinado al consumo posterior del Plugin.

Debe ser:

* estructurada;
* trazable;
* versionable;
* reproducible cuando sea posible;
* explícita sobre incertidumbre;
* explícita sobre procedencia;
* separable por naturaleza;
* apta para consumo humano;
* apta para consumo por agentes.

Los documentos finales forman parte de esta Fuente de Conocimiento o son proyecciones deterministas de ella según el contrato que se defina posteriormente.

---

## 9. Relación con el Plugin

El Plugin multiagente es consumidor de la Fuente de Conocimiento.

El Plugin no debería necesitar reconstruir nuevamente todo el contexto desde el código legacy si LegacyMapper ya produjo ese conocimiento.

La Fuente debe permitir que los agentes conozcan, según corresponda:

* qué existe;
* qué se necesita;
* qué debe cumplirse;
* qué decisiones están tomadas;
* qué restricciones existen;
* qué reglas técnicas aplican;
* qué reglas de negocio aplican;
* qué información permanece parcial;
* qué información permanece desconocida.

LegacyMapper no debe realizar trabajo que pertenezca posteriormente a los agentes de desarrollo del Plugin.

---

## 10. Alcance de V4

V4 se centra en:

MULTI_SOURCE_KNOWLEDGE

HUMAN_INFORMATION_INGESTION

PROVENANCE

KNOWLEDGE_CLASSIFICATION

AS_IS_TO_BE_SEPARATION

GAP_DETECTION

CONFLICT_DETECTION

KNOWLEDGE_PROPOSAL

TECHNICAL_LEADER_APPROVAL

KNOWLEDGE_COMPOSITION

DOCUMENT_PROJECTION

V4 debe preservar las capacidades validadas de V3.

---

## 11. Fuera de alcance V4

El agnosticismo completo respecto de:

* lenguaje;
* framework;
* tecnología;
* estructura de proyecto;
* paradigma;
* tipo de aplicación;

queda explícitamente diferido a V5.

V4 puede continuar utilizando las capacidades técnicas heredadas de V3.

---

## 12. Baseline heredada

V4 comienza desde la baseline cerrada de V3.

La baseline canónica es:

output/v3_final/V3_FINAL_BASELINE.json

V3 está formalmente cerrada.

V4 no debe modificar retroactivamente los artefactos canónicos de V3.

---

## 13. Regla de continuidad

El proyecto LegacyMapper no depende de la memoria de ningún agente de IA.

Codex, Claude u otros agentes son ejecutores reemplazables.

Toda decisión necesaria para continuar el proyecto debe quedar persistida en el repositorio mediante:

* contratos;
* decisiones;
* handovers;
* baselines;
* resultados;
* tests;
* documentación;
* prompts cuando corresponda.

Una nueva IA debe poder recuperar el estado del proyecto leyendo el repositorio sin necesitar acceso a conversaciones históricas.

## 14. Estado

V4_DEFINITION_STATUS=FOUNDATION_DEFINED

V4_IMPLEMENTATION_STATUS=NOT_STARTED