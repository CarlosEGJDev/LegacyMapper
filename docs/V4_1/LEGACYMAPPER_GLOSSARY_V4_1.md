# LegacyMapper V4.1 — Glosario

> Definiciones breves y específicas de LegacyMapper, ordenadas alfabéticamente. Para explicaciones extensas, ver el [Manual de Usuario V4.1](LEGACYMAPPER_USER_MANUAL_V4_1.md) y el [Manual Técnico V4.1](LEGACYMAPPER_TECHNICAL_MANUAL_V4_1.md).

---

**AI Interpretation (Interpretación de IA)**
Definición: propuesta de interpretación generada por un modelo de IA cuando la evidencia determinística no basta.
Por qué importa: es un valor de `SourceType`; nunca se trata como hecho confirmado sin aprobación.
Relacionados: Proposal, Approval, AI Knowledge Allowed.

**AI Knowledge Allowed (Conocimiento de IA permitido)**
Definición: indicador de readiness que confirma si el sistema tiene permitido, en general, generar propuestas de interpretación con IA.
Por qué importa: se reporta explícitamente en el resultado de readiness (`ai_knowledge_allowed`).
Relacionados: AI Knowledge Generated, Readiness.

**AI Knowledge Generated (Conocimiento de IA generado)**
Definición: indicador de readiness que confirma si, en el ciclo evaluado, efectivamente se generó conocimiento mediante IA.
Por qué importa: permite distinguir "permitido" de "efectivamente usado"; en el baseline V4.1 es `false`.
Relacionados: AI Knowledge Allowed, Readiness.

**Approval (Aprobación)**
Definición: decisión formal del Technical Lead sobre una propuesta (aprobar, rechazar o solicitar corrección).
Por qué importa: es el único mecanismo por el cual algo se convierte en conocimiento canónico.
Relacionados: ApprovalAuthority, ApprovalDecision, Technical Lead.

**ApprovalAuthority**
Definición: enum que identifica quién tiene autoridad para aprobar; en V4.1 su único valor es `TECHNICAL_LEAD`.
Por qué importa: garantiza que la IA nunca figure como autoridad de aprobación.
Relacionados: Approval, Technical Lead.

**ApprovalDecision**
Definición: registro de una decisión de aprobación, con un tipo (`APPROVED`, `REJECTED`, `CORRECTION_REQUESTED`).
Por qué importa: es el evento que habilita (o no) que una propuesta se vuelva conocimiento canónico.
Relacionados: Approval, Proposal, Canonical Knowledge.

**AS_IS**
Definición: estado temporal que describe cómo funciona el sistema **hoy**.
Por qué importa: se contrasta con `TO_BE` para detectar gaps, sin asumir automáticamente un conflicto.
Relacionados: TO_BE, HISTORICAL, Gap, Temporal State.

**Canonical Knowledge (Conocimiento Canónico)**
Definición: la única fuente de verdad del sistema, compuesta por entradas aprobadas por el Technical Lead.
Por qué importa: todas las proyecciones (documentos, Plugin) derivan de aquí; nada se escribe directamente en las proyecciones.
Relacionados: CanonicalKnowledgeEntry, CanonicalKnowledgeCollection, Projection.

**CanonicalKnowledgeCollection**
Definición: la colección que contiene todas las entradas de conocimiento canónico del sistema.
Por qué importa: es única; no existen colecciones canónicas paralelas.
Relacionados: Canonical Knowledge, CanonicalKnowledgeEntry.

**CanonicalKnowledgeEntry**
Definición: una entrada individual e inmutable de conocimiento canónico, identificada por un `knowledge_id` (`KNO-`).
Por qué importa: es la unidad mínima de verdad que las proyecciones consumen.
Relacionados: Canonical Knowledge, Knowledge ID.

**Classification (Clasificación)**
Definición: proceso de asignar categoría/estado a una pieza de conocimiento, con un método asociado (explícito, regla determinística, o propuesto por IA).
Por qué importa: determina cómo se organiza y trata cada dato dentro del sistema.
Relacionados: Knowledge Nature, Knowledge Status.

**Code Fact (Hecho de código)**
Definición: dato extraído directamente del código fuente, sin interpretación.
Por qué importa: es la base más confiable del sistema; corresponde a `SourceType.DETERMINISTIC_CODE_FACT`.
Relacionados: Determinism, Evidence.

**Confidence (Confianza)**
Definición: nivel de certeza asociado a un hallazgo del análisis de código.
Por qué importa: permite distinguir hallazgos sólidos de hallazgos débiles sin descartar ninguno.
Relacionados: Evidence, Unresolved.

**Conflict (Conflicto)**
Definición: contradicción real entre dos fuentes sobre el mismo hecho o momento.
Por qué importa: se distingue explícitamente de un Gap; requiere resolución, no solo documentación.
Relacionados: Gap, RelationKind.

**Controlled Operator (Operador controlado)**
Definición: persona que opera LegacyMapper (ejecuta análisis, gestiona el ciclo) sin tener autoridad de aprobación de conocimiento.
Por qué importa: separa "quién ejecuta" de "quién aprueba".
Relacionados: Technical Lead, Approval.

**DETERMINISTIC_CODE_FACT**
Definición: valor de `SourceType` que marca un dato como extraído de forma determinística del código, sin interpretación.
Por qué importa: es el tipo de fuente con mayor confiabilidad estructural en el sistema.
Relacionados: Code Fact, SourceType.

**Determinism (Determinismo)**
Definición: propiedad de un proceso cuyo resultado es siempre el mismo para la misma entrada (sin tiempo, aleatoriedad o UUID involucrados).
Por qué importa: es un principio de diseño central; los identificadores y artefactos generados deben ser reproducibles.
Relacionados: Code Fact, Knowledge ID.

**Evidence (Evidencia)**
Definición: soporte concreto (fragmento de código, documento, referencia) que respalda una afirmación.
Por qué importa: ninguna afirmación se acepta como válida sin evidencia asociada.
Relacionados: Evidence Reference, Confidence.

**Evidence Reference (Referencia de evidencia)**
Definición: puntero estructurado (`EVR-`) que vincula una pieza de conocimiento con su evidencia de origen.
Por qué importa: habilita la trazabilidad entre una afirmación y su respaldo.
Relacionados: Evidence, Provenance.

**Gap**
Definición: diferencia entre `AS_IS` y `TO_BE` (o entre estados temporales) que no implica una contradicción entre fuentes.
Por qué importa: se documenta como pendiente de resolver, no como error.
Relacionados: AS_IS, TO_BE, Conflict.

**HISTORICAL**
Definición: estado temporal que describe cómo funcionaba el sistema **antes**, ya no vigente.
Por qué importa: permite conservar contexto histórico sin confundirlo con el estado actual.
Relacionados: AS_IS, TO_BE, Temporal State.

**Human Information (Información humana)**
Definición: conocimiento aportado por una persona (documentos, explicaciones), distinto de un hecho de código.
Por qué importa: es uno de los modos de información soportados y una fuente legítima de material de entrada.
Relacionados: Material, Human Requirement.

**Human Requirement (Requerimiento humano)**
Definición: valor de `SourceType` que representa un requerimiento expresado por una persona.
Por qué importa: distingue requerimientos de negocio de hechos de código dentro del modelo de procedencia.
Relacionados: Human Information, SourceType.

**Ingestion (Ingestión)**
Definición: proceso de normalizar material de entrada (código o información humana) a un formato interno consistente.
Por qué importa: es el primer paso del flujo conceptual, previo a generar evidencia.
Relacionados: Material, Evidence.

**Knowledge ID (ID de conocimiento)**
Definición: identificador determinístico (`KNO-`) de una entrada de conocimiento canónico, derivado de sus campos relevantes.
Por qué importa: permite trazabilidad exacta entre un documento generado y la entrada canónica de la que proviene.
Relacionados: Canonical Knowledge, Traceability.

**Knowledge Nature (Naturaleza del conocimiento)**
Definición: categoría del contenido de una pieza de conocimiento (por ejemplo, regla de negocio, arquitectura, proceso).
Por qué importa: se usa para clasificar y, eventualmente, para enrutar contenido a documentos de proyección.
Relacionados: Classification, KnowledgeNature.

**Knowledge Source (Fuente de conocimiento)**
Definición: origen categorizado de una pieza de conocimiento (código, requerimiento humano, interpretación de IA, etc.), representado por `SourceType`.
Por qué importa: preserva de dónde viene cada dato.
Relacionados: SourceType, Provenance.

**Knowledge Status (Estado del conocimiento)**
Definición: estado de una pieza de conocimiento (`CONFIRMED`, `INTERPRETED`, `PARTIAL`, `UNRESOLVED`, `MISSING`, `CONFLICTING`, `SUPERSEDED`).
Por qué importa: expresa qué tan resuelta y confiable es una afirmación en un momento dado.
Relacionados: Unresolved, Conflict.

**Legacy Source (Fuente legada)**
Definición: el repositorio de código del sistema legado que se analiza.
Por qué importa: se accede siempre en modo de solo lectura; nunca se modifica.
Relacionados: Code Fact.

**LegacyMapper**
Definición: el sistema descrito en este documento; herramienta para descubrir, organizar, interpretar, validar y documentar conocimiento sobre sistemas legados.
Por qué importa: es el sujeto de todo este glosario.
Relacionados: Canonical Knowledge, Legacy Source.

**Material**
Definición: unidad de entrada al sistema de conocimiento (código o información humana), antes de convertirse en evidencia.
Por qué importa: es el punto de partida del ciclo de vida de los datos, identificado con prefijo `MAT-`.
Relacionados: Ingestion, Evidence.

**Machine-Readable Projection (Proyección legible por máquina)**
Definición: proyección del conocimiento canónico (R12) pensada para ser consumida por un futuro Plugin, bajo el contrato `LegacyMapperPluginKnowledge` versión 1.0.
Por qué importa: separa la representación para humanos (R11) de la representación estructurada para consumo automatizado.
Relacionados: Plugin, Plugin Runtime, Projection.

**Manifest (Manifiesto)**
Definición: artefacto que documenta el conjunto de resultados/artefactos de un ciclo o ronda (por ejemplo, el manifiesto de proyección o de cierre de ronda).
Por qué importa: permite verificar integridad y completitud de lo generado.
Relacionados: ProjectionManifest, PluginKnowledgeManifest.

**Plugin**
Definición: componente futuro, todavía no implementado como runtime, que consumiría la proyección legible por máquina de LegacyMapper.
Por qué importa: define el límite entre lo que LegacyMapper construye (conocimiento) y lo que un futuro Plugin consumiría.
Relacionados: Plugin Runtime, Machine-Readable Projection.

**Plugin Runtime**
Definición: el proceso o servicio real que ejecutaría un Plugin, consumiendo la proyección de LegacyMapper.
Por qué importa: en V4.1 es explícitamente `NOT_IMPLEMENTED`; no confundir el contrato de datos con un runtime funcionando.
Relacionados: Plugin, Machine-Readable Projection.

**Projection (Proyección)**
Definición: vista derivada del conocimiento canónico, ya sea legible por humanos (documentos Markdown, R11) o por máquina (R12).
Por qué importa: las proyecciones son siempre de solo lectura; nunca son fuente de verdad independiente.
Relacionados: Canonical Knowledge, ProjectionRule, ProjectionTarget.

**ProjectionRule**
Definición: regla que determina si una entrada de conocimiento canónico corresponde a un `ProjectionTarget`, basada únicamente en campos estructurados.
Por qué importa: prohíbe el enrutamiento por análisis de texto libre, garantizando trazabilidad predecible.
Relacionados: ProjectionTarget, UNMAPPED.

**ProjectionTarget**
Definición: destino de documento dentro de la arquitectura cerrada de proyección (por ejemplo, un documento dentro de `03-.../`).
Por qué importa: define la estructura fija de la familia de documentos generados.
Relacionados: ProjectionRule, R11.

**Proposal (Propuesta)**
Definición: sugerencia de interpretación, resolución o corrección, generada por una persona, por regla determinística, o por IA, pendiente de aprobación.
Por qué importa: es el único vehículo por el cual una interpretación puede llegar a convertirse en conocimiento canónico.
Relacionados: Approval, AI Interpretation.

**Provenance (Procedencia)**
Definición: cadena rastreable de origen de un dato, representada como un grafo de nodos y aristas.
Por qué importa: permite responder siempre "de dónde salió este dato y por qué camino llegó hasta aquí".
Relacionados: Evidence Reference, Traceability.

**Readiness**
Definición: verificación automatizada de que las condiciones necesarias para considerar un ciclo "listo" se cumplen (artefactos presentes, indicadores de IA correctos, etc.).
Por qué importa: su resultado (`READY` o no) es una señal explícita de si se puede continuar con confianza.
Relacionados: AI Knowledge Allowed, AI Knowledge Generated.

**Relation (Relación)**
Definición: vínculo detectado entre dos piezas de conocimiento, de tipo `DIFFERENCE`, `GAP`, `CONFLICT` o `TEMPORAL_EVOLUTION`.
Por qué importa: es cómo el sistema representa formalmente gaps y conflictos, no solo texto descriptivo.
Relacionados: Gap, Conflict, RelationKind.

**R11**
Definición: nombre interno de la capacidad de proyección legible por humanos del conocimiento canónico (documentos Markdown).
Por qué importa: es la fuente de la documentación generada que consumen las personas.
Relacionados: Projection, ProjectionTarget.

**R12**
Definición: nombre interno de la capacidad de proyección legible por máquina orientada a un futuro Plugin.
Por qué importa: es la contraparte de R11 para consumo automatizado; no implica un runtime de Plugin funcionando.
Relacionados: Machine-Readable Projection, Plugin Runtime.

**SourceType**
Definición: enum que clasifica el origen de una pieza de conocimiento (hecho de código, requerimiento humano, interpretación de IA, etc.).
Por qué importa: es la base para decidir cómo debe tratarse la confiabilidad de un dato.
Relacionados: Knowledge Source, DETERMINISTIC_CODE_FACT.

**Technical Lead**
Definición: rol humano con la única autoridad de aprobación de conocimiento en el sistema (`ApprovalAuthority.TECHNICAL_LEAD`).
Por qué importa: garantiza que ninguna interpretación (humana o de IA) se vuelva conocimiento sin revisión humana con autoridad.
Relacionados: Approval, ApprovalAuthority, Controlled Operator.

**Temporal State (Estado temporal)**
Definición: clasificación de una pieza de conocimiento como `AS_IS`, `TO_BE` o `HISTORICAL`.
Por qué importa: permite razonar sobre el tiempo sin confundir presente, objetivo y pasado.
Relacionados: AS_IS, TO_BE, HISTORICAL.

**TO_BE**
Definición: estado temporal que describe cómo **debería** funcionar el sistema según un requerimiento u objetivo.
Por qué importa: se compara con `AS_IS` para identificar gaps, no automáticamente contradicciones.
Relacionados: AS_IS, Gap, Temporal State.

**Traceability (Trazabilidad)**
Definición: capacidad de seguir un dato desde su aparición en un documento generado hasta su origen en el conocimiento canónico y, de ahí, hasta su evidencia.
Por qué importa: es lo que hace confiable la documentación generada por LegacyMapper.
Relacionados: Knowledge ID, Provenance.

**UNMAPPED**
Definición: estado de una entrada de conocimiento canónico que no encaja en ninguna `ProjectionRule` definida.
Por qué importa: es un resultado válido y explícito, no un error ni una omisión silenciosa.
Relacionados: ProjectionRule, Projection.

**Unresolved (No resuelto)**
Definición: estado que indica que el sistema no pudo determinar una respuesta con la evidencia disponible.
Por qué importa: LegacyMapper prefiere marcar algo como no resuelto antes que inventar una respuesta.
Relacionados: Knowledge Status, Confidence.

**V4**
Definición: versión del sistema que introdujo el modelo de gestión de conocimiento (procedencia, clasificación, temporalidad, propuestas, aprobación, conocimiento canónico, proyecciones).
Por qué importa: es la base arquitectónica sobre la que se construyó V4.1. Formalmente cerrado.
Relacionados: V4.1, V5.

**V4.1**
Definición: ronda de refactor de mantenibilidad (R0–R10) sobre el sistema V4, sin cambio de comportamiento observable. Formalmente cerrado.
Por qué importa: es la versión vigente descrita por este glosario y por los manuales asociados.
Relacionados: V4, Remaining Technical Debt.

**V5**
Definición: alcance futuro planificado (agnosticismo de lenguaje, framework, base de datos y proveedor/modelo de IA), **no implementado**.
Por qué importa: delimita explícitamente lo que LegacyMapper V4.1 no hace todavía, para evitar expectativas incorrectas.
Relacionados: V4.1, Plugin Runtime.

---

Para más contexto, ver el [Manual de Usuario V4.1](LEGACYMAPPER_USER_MANUAL_V4_1.md) y el [Manual Técnico V4.1](LEGACYMAPPER_TECHNICAL_MANUAL_V4_1.md).
