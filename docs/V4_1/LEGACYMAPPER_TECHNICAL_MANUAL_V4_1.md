# LegacyMapper V4.1 — Manual Técnico para Desarrolladores

> Este manual describe el sistema **tal como está implementado en V4.1** (formalmente cerrado). Donde el manual menciona V5, es únicamente para aclarar que esa capacidad **no** existe todavía. Para definiciones breves de términos, ver el [Glosario V4.1](LEGACYMAPPER_GLOSSARY_V4_1.md). Para una introducción no técnica, ver el [Manual de Usuario V4.1](LEGACYMAPPER_USER_MANUAL_V4_1.md).

---

## 1. Propósito

LegacyMapper es, arquitectónicamente, una tubería (pipeline) que va desde el descubrimiento determinístico de hechos hasta la generación de proyecciones de conocimiento, pasando por una aprobación humana obligatoria:

```
descubrimiento determinístico → evidencia → interpretación → aprobación controlada → conocimiento canónico → proyecciones
```

El sistema combina dos motores complementarios:

1. Un **analizador de código legado** (.NET Framework / VB.NET / ASP.NET Web Forms / Oracle) que produce hechos determinísticos y flujos funcionales.
2. Un **sistema de gestión de conocimiento** (paquete `legacy_documenter/knowledge/`) que administra material, evidencia, interpretación, propuestas, aprobación, conocimiento canónico y proyecciones — sea que el conocimiento provenga de código, de personas, o de ambos.

---

## 2. Principios de diseño

- **Python descubre/resuelve.** Todo lo que puede determinarse mecánicamente se determina en Python, sin intervención de IA.
- **La IA interpreta.** La IA solo entra en juego cuando hace falta interpretación, y su salida siempre es una propuesta, nunca un hecho definitivo.
- **El Technical Lead aprueba.** Toda incorporación a conocimiento canónico requiere una decisión de aprobación humana con autoridad `TECHNICAL_LEAD`.
- **Evidencia antes que inferencia.** Ninguna afirmación se trata como válida sin evidencia asociada.
- **No se inventan relaciones.** Si una relación no puede determinarse con evidencia suficiente, se marca como no resuelta en lugar de inferirla arbitrariamente.
- **Se preserva la incertidumbre.** Los estados `UNRESOLVED`, `PARTIAL`, `MISSING` y `CONFLICTING` son ciudadanos de primera clase del modelo de dominio, no casos de error.
- **Se preserva la procedencia (provenance).** Cada pieza de conocimiento puede rastrearse hasta su origen mediante un grafo de nodos y aristas de procedencia.
- **Una única fuente de conocimiento canónico.** No existen fuentes de verdad paralelas; las proyecciones (documentos Markdown, proyección para Plugin) son vistas derivadas, no almacenes independientes.
- **El código fuente es opcional.** El sistema de conocimiento puede operar con información humana únicamente, sin necesidad de un repositorio de código.
- **Continuidad agnóstica del agente.** El repositorio debe poder retomarse por cualquier agente de IA o desarrollador humano usando solo los artefactos del repositorio (ver sección 26).
- **Determinismo donde sea posible.** Identificadores, hashes y artefactos generados deben ser reproducibles a partir de las mismas entradas (nunca basados en tiempo, UUID aleatorio, etc.).

---

## 3. Alcance tecnológico actual

**V4.1 no es agnóstico de lenguaje, framework ni base de datos.** El escenario principal soportado y verificado en el código es:

```
.NET Framework
VB.NET
ASP.NET Web Forms
Oracle
```

El clasificador de archivos (`legacy_documenter/scanner/file_classifier.py`) reconoce específicamente `.sln`, `.vbproj`, `.vb`, `.aspx`, `.ascx`, `.master` y `web.config`. Los extractores de base de datos detectan específicamente patrones de Oracle (`OracleParameter`, `OracleCommand`, `OracleDataAdapter`) y `OleDb`. El módulo de readiness impone explícitamente que no se afirme evidencia insuficiente como si fuera un hecho — por ejemplo, prohíbe declarar "MVC está establecido" o "Clean Architecture confirmada" sin evidencia suficiente.

No se debe documentar ni asumir soporte general para otros lenguajes, frameworks (por ejemplo ASP.NET MVC), u otras bases de datos (por ejemplo SQL Server) como si ya estuvieran soportados: esa agnosticidad es alcance de **V5**, no de V4.1 (ver sección 27).

---

## 4. Estructura del repositorio

```
LegacyMapper/
├── AGENTS.md
├── CLAUDE.md
├── PROJECT_STATE.json
├── main.py                      # wrapper delgado → legacy_documenter.main.main
├── legacy_documenter/           # paquete principal
├── tests/                       # suite de pruebas (51 archivos + fixtures/)
├── docs/                        # documentación del proyecto (V4/, V4_1/, etc.)
├── prompts/                     # prompts de tareas (V4/, V4_1/)
├── output/                      # artefactos generados por ejecuciones de análisis
├── tools/                       # utilidades auxiliares
├── codex/                       # reportes históricos de agentes de desarrollo (V1/V2/V3)
├── result_codex/                # resultados históricos asociados a codex/
└── context/                     # se puebla en tiempo de ejecución; vacío en reposo
```

`codex/` y `result_codex/` corresponden a rondas de desarrollo históricas (V1–V3) previas al sistema de conocimiento V4/V4.1 y se conservan como registro histórico del proyecto; no representan la arquitectura vigente.

---

## 5. Arquitectura Python

Estructura verificada de `legacy_documenter/` (fuera del subpaquete `knowledge/`, cubierto en la sección 6):

| Directorio | Propósito | Entradas | Salidas | Módulos importantes | Naturaleza |
|---|---|---|---|---|---|
| `scanner/` | Descubrimiento y clasificación de archivos del repositorio legado | ruta de repositorio | lista clasificada de archivos | `repository_scanner.py`, `file_classifier.py` | Determinística |
| `extractors/` | Parsers determinísticos por tipo de archivo | archivos clasificados | modelos extraídos (soluciones, proyectos, VB, Web Forms, web.config, llamadas, eventos web, base de datos) | `solution_extractor`, `vbproj_extractor`, `vbnet_extractor`, `webforms_extractor`, `webconfig_extractor`, `call_extractor`, `web_event_extractor`, `database_extractor` (+ helpers privados `_database_*`) | Determinística |
| `analysis/` | Resolución de relaciones y flujos sobre lo extraído | modelos extraídos | dependencias, llamadas resueltas, accesos a datos resueltos, flujos funcionales | `call_resolver`, `database_resolver`, `dependency_resolver`, `web_entry_resolver`, `flow_resolver` (+ `_flow_*` helpers), `deep_source`, `deep_interpretation`, `targeted_exhaustion` | Mayormente determinística; `deep_interpretation` es el punto de posible invocación a un proveedor de IA |
| `context/` | Construcción de contexto por proyecto y a nivel de sistema | resultados de análisis | contexto estructurado para documentación | `context_builder.py`, `system_context_builder.py`, `composer.py`, `resolver.py` | Determinística |
| `documentation/` | Generación, consistencia y revisión de documentación | contexto | documentos generados, reportes de consistencia | `generator`, `hierarchical`, `systematic`, `synthesis`, `aggregation`, `coverage`, `consistency`, `consistency_run`, `human_review`, `second_review`, `evidence_catalog`, `evidence_resume`, `resume`, `interpretation`, `renderer`, `contracts`, `envelope` | Mixta (determinística + puntos de interpretación) |
| `exporters/` | Exportación de resultados a formatos de archivo | modelos internos | archivos JSON/Markdown | `json_exporter.py`, `markdown_exporter.py` | Determinística |
| `models/` | Modelos de datos (dataclasses) del dominio de análisis de código | — | — | `call`, `dependency`, `entry_point`, `evidence`, `project`, `source_file`, `symbol`, `webform` | Determinística (solo estructuras) |
| `quality/` | Auditoría de mantenibilidad del propio código | código fuente de LegacyMapper | reporte de auditoría | `maintainability_audit.py` | Determinística |
| `llm/` | Frontera de invocación a proveedores de IA | prompt/contexto | respuesta del proveedor | `core.py`, `copilot_pilot.py`, `providers/copilot.py`, `providers/gemini.py` | Relacionada con IA |
| `utils/` | Utilidades compartidas | — | — | `sanitizer.py`, `json_rendering.py` | Determinística |
| `knowledge/` | Sistema de gestión de conocimiento V4/V4.1 | ver sección 6 | ver sección 6 | ver sección 6 | Mixta |
| `config.py` | Configuración estática del análisis | — | `DEFAULT_EXCLUDES`, `VTI_PREFIX`, `TEXT_EXTENSIONS` | — | Determinística |

---

## 6. Arquitectura de conocimiento V4

Bajo `legacy_documenter/knowledge/` existen los siguientes paquetes verificados en el código fuente:

```
knowledge/
├── domain/            # modelos y enums centrales del dominio de conocimiento
├── input/              # material de entrada (humano/código)
├── provenance/          # grafo de procedencia (nodos/aristas)
├── ingestion/           # normalización de material de entrada
├── classification/      # clasificación de conocimiento
├── temporal/            # estados/buckets temporales (AS_IS/TO_BE/HISTORICAL)
├── relations/           # relaciones entre piezas de conocimiento (gap/conflicto/etc.)
├── proposals/           # propuestas de interpretación/resolución
├── approval/            # decisiones de aprobación del Technical Lead
├── canonical/           # conocimiento canónico (fuente única de verdad)
├── projection/          # proyección legible por humanos (R11)
├── plugin_projection/   # proyección legible por máquina para Plugin (R12)
├── closure/             # soporte de cierre/baseline/manifiesto de rondas V4.1
└── readiness.py         # gate de "readiness" (+ helpers privados _readiness_*)
```

**Dirección de dependencia:** el flujo de datos va de `input/` e `ingestion/` hacia `provenance/`, `classification/` y `temporal/`, de ahí hacia `relations/` y `proposals/`, luego `approval/`, y finalmente `canonical/`. Las proyecciones (`projection/`, `plugin_projection/`) dependen únicamente de `canonical/`: **nunca** leen directamente de `proposals/` ni generan conocimiento por sí mismas.

**Límites de inmutabilidad / solo lectura:** `CanonicalKnowledgeEntry` es un dataclass congelado (`frozen`); una vez creada una entrada canónica, no se modifica in place. Las proyecciones son de solo lectura sobre el conocimiento canónico: no pueden crear ni alterar entradas canónicas (ver sección 13).

---

## 7. Ciclo de vida de los datos

```
Material → Evidencia → Interpretación → Propuesta → Aprobación → CanonicalKnowledgeEntry → Proyección
```

### Prefijos de identificador verificados en código

| Prefijo | Entidad | Origen verificado |
|---|---|---|
| `KST-` | `KnowledgeStatement` | `knowledge/domain/models.py` |
| `MAT-` | `Material` | `knowledge/domain/models.py` |
| `EVR-` | `EvidenceRef` | `knowledge/domain/models.py` |
| `PRN-` | Nodo de procedencia | `knowledge/provenance/contract_report.py` |
| `PED-` | Arista de procedencia | `knowledge/provenance/contract_report.py` |
| `KNO-` | `CanonicalKnowledgeEntry` | `knowledge/canonical/models.py` (`new_knowledge_id`) |

Los prefijos `PRP-` (propuesta), `APR-` (aprobación), `REL-` (relación), `SRC-`, `CLS-` y `TMP-` aparecen únicamente en reportes de ejemplo/fixtures (literales `*_EXAMPLE-*`), no respaldados por un generador determinístico dedicado (tipo `stable_id("PRP", ...)`) en el código de producción inspeccionado. No se deben tratar como identificadores minted con el mismo rigor que `KST-`/`MAT-`/`EVR-`/`KNO-`/`PRN-`/`PED-`; si se mencionan, deben marcarse como ilustrativos.

Todos los identificadores determinísticos se derivan mediante una función `stable_id(...)` a partir de los campos relevantes de la entidad (nunca de tiempo, UUID aleatorio, ni entrada aleatoria).

---

## 8. Modelos de dominio

Enums verificados en `legacy_documenter/knowledge/domain/enums.py` y paquetes relacionados:

**`SourceType`** (`domain/enums.py`): `DETERMINISTIC_CODE_FACT`, `HUMAN_REQUIREMENT`, `USER_STORY`, `BUSINESS_REQUIREMENT`, `BUSINESS_CONTEXT`, `TECHNICAL_CONSTRAINT`, `CORPORATE_STANDARD`, `APPROVED_DECISION`, `EXTERNAL_DOCUMENT`, `PROJECT_DOCUMENT`, `AI_INTERPRETATION`, `UNRESOLVED`

**`KnowledgeNature`** (`domain/enums.py`): `NORM`, `LEVANTAMIENTO`, `REQUIREMENT`, `NEED`, `BUSINESS_RULE`, `DECISION`, `ARCHITECTURE`, `PROCESS`, `FLOW`, `CATALOG`, `PROJECT`, `RESOLUTION`, `LESSON`, `TRAINING`, `GLOSSARY`, `CONSTRAINT`, `EXISTING_IMPLEMENTATION`

**`KnowledgeStatus`** (`domain/enums.py`): `CONFIRMED`, `INTERPRETED`, `PARTIAL`, `UNRESOLVED`, `MISSING`, `CONFLICTING`, `SUPERSEDED`

**`TemporalState`** (`domain/enums.py`): `AS_IS`, `TO_BE`, `HISTORICAL`

**`ApprovalStatus`** (domain-level, `domain/enums.py`, distinto de `ApprovalDecisionType` de `approval/enums.py`): `NOT_APPROVED`, `APPROVED`, `REJECTED`, `CORRECTED`

**`TemporalBucket`** (`knowledge/temporal/enums.py`): `AS_IS`, `TO_BE`, `HISTORICAL`, `UNSPECIFIED` — es una proyección estructural de `TemporalState`, no un cuarto valor de `TemporalState`.

**`ClassificationMethod` / `ClassificationStatus`** (`knowledge/classification/enums.py`): `EXPLICIT`, `DETERMINISTIC_RULE`, `AI_PROPOSED`, `UNRESOLVED` / `CLASSIFIED`, `UNCLASSIFIED`, `AMBIGUOUS`

**`RelationKind` / `RelationDirectionality` / `RelationBasis`** (`knowledge/relations/enums.py`): `DIFFERENCE`, `GAP`, `CONFLICT`, `TEMPORAL_EVOLUTION` / `SYMMETRIC`, `DIRECTIONAL` / `EXPLICIT`, `DETERMINISTIC_RULE`, `AI_PROPOSED`, `UNRESOLVED`

**`ProposalKind` / `ProposalStatus` / `ProposalMethod`** (`knowledge/proposals/enums.py`): `INTERPRETATION`, `RESOLUTION`, `CORRECTION`, `RECONCILIATION`, `SELECTION`, `ADDITIONAL_INFORMATION`, `MIGRATION`, `KNOWLEDGE_ADDITION` / `DRAFT`, `READY_FOR_REVIEW`, `WITHDRAWN`, `SUPERSEDED` / `HUMAN_PROPOSED`, `DETERMINISTIC_RULE`, `AI_PROPOSED`

**`ApprovalDecisionType` / `ApprovalAuthority`** (`knowledge/approval/enums.py`): `APPROVED`, `REJECTED`, `CORRECTION_REQUESTED` / `TECHNICAL_LEAD` (única autoridad definida)

**`CanonicalKnowledgeEntry`** (`knowledge/canonical/models.py`): dataclass congelado con campos `knowledge_id, statement, source_type, nature, status, proposal_id, approval_decision_id, temporal_state=None, evidence_refs=(), provenance=None, related_statement_ids=(), metadata={}`.

Adicionalmente, `knowledge/provenance/enums.py` define `NodeKind` (`SOURCE`, `MATERIAL`, `EVIDENCE`, `STATEMENT`, `INTERPRETATION`, `PROPOSAL`, `KNOWLEDGE`), `EdgeRelationship` (`ORIGINATES_FROM`, `MATERIALIZED_FROM`, `EVIDENCE_FROM`, `DERIVED_FROM`, `INTERPRETED_FROM`, `REFERENCES`), `TransformationType` (`DETERMINISTIC_EXTRACTION`, `NORMALIZATION`, `HUMAN_SUPPLIED`, `AI_INTERPRETATION`, `AGGREGATION`, `MANUAL_CORRECTION`) y `LineageCompleteness` (`COMPLETE`, `PARTIAL`, `UNRESOLVED`, `INVALID`).

---

## 9. Descubrimiento de código legado

El descubrimiento sobre repositorios .NET/VB.NET funciona en capas:

1. **`scanner/`** recorre el repositorio y clasifica archivos por tipo.
2. **`extractors/`** parsean cada tipo de archivo de forma determinística: soluciones, proyectos, código VB.NET, Web Forms, `web.config`, llamadas, eventos web y accesos a base de datos.
3. **`analysis/`** resuelve relaciones entre lo extraído: dependencias (`dependency_resolver`), llamadas (`call_resolver`), accesos a datos (`database_resolver`), puntos de entrada web (`web_entry_resolver`) y flujos funcionales completos (`flow_resolver`).
4. Cada hallazgo se acompaña de un **modelo de evidencia y confianza**: el sistema registra en qué se basa cada afirmación y qué tan segura es.

**Las convenciones de nombres de proyectos, por sí solas, no se tratan como verdad arquitectónica.** Por ejemplo, que un proyecto se llame `*.DataAccess` no basta para afirmar que implementa una capa de acceso a datos formalmente definida; esa afirmación requiere evidencia estructural real (referencias, patrones de código), no solo el nombre.

---

## 10. Análisis de base de datos

El extractor de base de datos (`database_extractor.py` y helpers `_database_*`) está orientado a **Oracle**: detecta patrones como `OracleParameter`, `OracleCommand`, `OracleDataAdapter` y wrappers como `OraConn`, además de acceso genérico vía `OleDb`.

El escaneo y la clasificación son **determinísticos**: se basan en patrones de código reconocibles, no en inferencia de IA. Los casos que no encajan en los patrones reconocidos quedan marcados como no resueltos en lugar de forzarse a una clasificación.

**Limitaciones:** el soporte está acotado a los patrones de acceso a Oracle/OleDb reconocidos por los extractores actuales; accesos a datos mediante mecanismos no cubiertos (por ejemplo ORMs modernos) no están garantizados de ser reconocidos en V4.1. La ronda V4.1-R6 abordó una descomposición controlada de este extractor para mejorar mantenibilidad, sin cambiar su comportamiento observable (ver sección 20).

---

## 11. Resolvedor de flujos (Flow Resolver)

`analysis/flow_resolver.py` (junto con sus helpers privados `_flow_*`) es responsable de construir los **flujos funcionales**: secuencias de llamadas y accesos que representan un caso de uso de principio a fin.

A alto nivel:

- Construye un **grafo** a partir de las llamadas y dependencias resueltas.
- Recorre (**traversal**) ese grafo respetando una profundidad máxima configurable (`--flow-max-depth`, por defecto `12`).
- Usa una noción de **identidad de camino (path identity)** para no duplicar o confundir caminos equivalentes durante el recorrido.
- Mantiene comportamiento de **estado/reinicio** consistente entre ejecuciones para que el resultado sea reproducible.
- Los límites que no puede resolver (por ejemplo, un destino dinámico que no puede determinarse estáticamente) quedan como fronteras **no resueltas**, explícitamente marcadas.

La ronda V4.1-R5 caracterizó el comportamiento de este orquestador antes de tocarlo (characterization tests), y la V4.1-R6 realizó extracciones controladas sobre áreas de mayor riesgo, siempre preservando el comportamiento observable. Existen áreas de alto riesgo que se dejaron **deliberadamente diferidas** (ver deuda técnica, sección 21) en lugar de refactorizarse sin la cobertura de pruebas adecuada.

---

## 12. Frontera de IA

- **Determinístico:** todo el descubrimiento de `scanner/`, `extractors/` y la mayor parte de `analysis/` (excepto `deep_interpretation.py`).
- **Puede invocar un LLM:** `analysis/deep_interpretation.py` es el punto donde el sistema puede invocar un proveedor de IA para generar una interpretación cuando la evidencia determinística no es suficiente.
- **Frontera de proveedor:** la invocación real pasa por `legacy_documenter/llm/` (`core.py`, `copilot_pilot.py`, `providers/copilot.py`, `providers/gemini.py`). El proveedor y modelo se configuran mediante variables de entorno (sección 17), nunca hardcodeados.
- **Qué puede interpretar la IA:** relacionar hechos de código con conocimiento humano, proponer clasificaciones o resoluciones de gaps/conflictos, siempre como **propuesta**, no como hecho o conocimiento definitivo.
- **Qué no puede autorizar la IA:** la IA no tiene autoridad de aprobación. Solo `ApprovalAuthority.TECHNICAL_LEAD` puede aprobar una propuesta.

En ejecuciones de cierre/regresión (como las verificadas en V4.1), `PROVIDER_CALLS=0` y `REAL_LLM_CALLS=0`: es decir, el baseline de pruebas y de readiness se mantiene sin invocaciones reales a proveedores externos.

**V5 abordará un agnosticismo más amplio de proveedor y modelo de IA.** Esa capacidad **no** está implementada en V4.1; hoy el sistema soporta proveedores específicos (Copilot, Gemini) mediante configuración explícita, no un mecanismo agnóstico general.

---

## 13. Conocimiento Canónico

`CanonicalKnowledgeCollection` (referenciada en `knowledge/canonical/service.py`) es la única colección de conocimiento canónico del sistema — no existe una colección paralela equivalente.

**Elegibilidad:** una entrada solo se convierte en `CanonicalKnowledgeEntry` cuando existe una `ApprovalDecisionType.APPROVED` asociada, emitida con `ApprovalAuthority.TECHNICAL_LEAD`.

**Inmutabilidad:** `CanonicalKnowledgeEntry` es un dataclass `frozen`; su `knowledge_id` se deriva determinísticamente (`new_knowledge_id`) a partir de `(proposal_id, approval_decision_id, source_type, nature, status, temporal_state, evidence_ids, related_statement_ids)`, nunca de tiempo o aleatoriedad.

**Por qué las proyecciones no pueden crear conocimiento canónico:** tanto `projection/` (R11) como `plugin_projection/` (R12) son de solo lectura sobre `CanonicalKnowledgeCollection.list()`. No tienen ninguna vía para escribir o modificar entradas canónicas; esto preserva la garantía de fuente única de verdad — si las proyecciones pudieran escribir, existirían múltiples caminos de mutación y la trazabilidad de procedencia se rompería.

---

## 14. Proyección legible por humanos (R11)

Definida en `legacy_documenter/knowledge/projection/`:

- **`models.py`**: `ProjectionTarget`, `ProjectionRule`, `DocumentProjection`, `ProjectionManifest`.
- **`rules.py`**: tupla cerrada `ALL_TARGETS` con los `ProjectionTarget` soportados.
- **`service.py`**: orquesta la proyección.
- **`markdown_renderer.py`**: genera el Markdown final.
- **`disk_io.py`**: escritura a disco.
- **`contract_report.py`**: reporte de verificación del contrato de proyección.

`ProjectionTarget.document_path` se valida contra un conjunto cerrado de prefijos de familia permitidos (`ALLOWED_FAMILY_PREFIXES`, de `00-el-area/` a `09-capacitacion/`); rutas absolutas, con letra de unidad, con traversal (`..`) o fuera de esas familias son rechazadas.

`ProjectionRule` únicamente compara **campos estructurados** del conocimiento canónico (nunca parsea el texto libre de `statement`), y requiere al menos una condición para ser válida — esto es lo que la sección "Governing Principle" del proceso llama **"free-text semantic routing is forbidden"**: no se enruta contenido a documentos por análisis de texto libre, solo por campos estructurados explícitos.

**Arquitectura de destino cerrada:** la tupla `ALL_TARGETS` contiene, al momento de esta verificación, **42** valores de `ProjectionTarget` (00: 6, 01: 5, 02: 6, 03: 16, 04: 4, 05 a 09: 5 cada una). `docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md` (línea 169) menciona "41" como cifra histórica; esa cifra está desactualizada respecto del código actual y **no debe reutilizarse** — usar 42, o referirse a "la tupla cerrada `ALL_TARGETS` vigente en `rules.py`" en lugar de fijar un número en documentación futura que pueda volver a desactualizarse.

Cada documento generado conserva trazabilidad hacia el conocimiento canónico mediante `knowledge_id`. Cuando una entrada canónica no encaja en ninguna `ProjectionRule`, queda marcada como `UNMAPPED` en lugar de forzarse a un documento incorrecto.

---

## 15. Proyección orientada a Plugin (R12)

Definida en `legacy_documenter/knowledge/plugin_projection/`:

- **Contrato:** `CONTRACT_NAME = "LegacyMapperPluginKnowledge"`, `CONTRACT_VERSION = "1.0"` (constantes en `models.py`).
- `SOURCE_KIND = "CANONICAL_KNOWLEDGE_SOURCE"`, `PROJECTION_KIND = "PLUGIN_MACHINE_READABLE"`.
- **Modelos:** `PluginKnowledgeEntry`, `PluginKnowledgeManifest`, `PluginCanonicalSourceDescriptor`, `PluginKnowledgePayload`.

`PluginKnowledgeEntry.knowledge_id` es siempre exactamente el `KNO-` id de origen; no se acuña una segunda identidad para la proyección. Esta proyección lee **únicamente** de `CanonicalKnowledgeCollection.list()` (R10), nunca del Markdown generado por R11.

**`PLUGIN_RUNTIME=NOT_IMPLEMENTED`**: esto es un contrato de proyección de datos, no un runtime de Plugin funcionando. No existe ningún proceso, servicio o agente Plugin ejecutándose en V4.1. La relación conceptual es:

```
LegacyMapper construye conocimiento → Plugin (futuro) consume conocimiento
```

---

## 16. Modelo de seguridad

Invariantes de seguridad verificados:

- **Solo lectura sobre el código legado:** el repositorio analizado nunca se modifica.
- **Rutas seguras / sin path traversal:** `ProjectionTarget.document_path` valida contra un conjunto cerrado de prefijos permitidos y rechaza rutas absolutas, con letra de unidad o con `..`.
- **Manejo de secretos:** no deben incluirse secretos (credenciales, cadenas de conexión reales) en material de entrada ni en artefactos generados; ver `docs/GENERATED_ARTIFACT_POLICY.md`.
- **Sanitización:** `legacy_documenter/utils/sanitizer.py` centraliza la sanitización de contenido usado en artefactos generados.
- **Sin dependencias externas ocultas:** el proyecto no tiene `requirements.txt` ni `pyproject.toml`; no depende de paquetes de terceros (confirmado por ausencia de manifiesto de dependencias y por `docs/PROJECT_RECOVERY.md`).
- **Contabilización de llamadas a proveedor:** el readiness gate reporta explícitamente `provider_calls` y `real_llm_calls`, permitiendo verificar que un ciclo de cierre no dependió de invocaciones reales a IA.
- **Procedencia:** todo dato en el sistema de conocimiento conserva su cadena de procedencia (`provenance/`).
- **Frontera de aprobación:** solo `ApprovalAuthority.TECHNICAL_LEAD` puede emitir una decisión de aprobación válida.

Solo se documentan aquí invariantes respaldados por evidencia del repositorio; no se afirman garantías de seguridad adicionales no verificadas en el código.

---

## 17. Configuración

Variables de entorno confirmadas por inspección exhaustiva del código (`os.environ` / `os.getenv`):

| Variable | Uso | Categoría |
|---|---|---|
| `LEGACYMAPPER_LLM_PROVIDER` | Selecciona el proveedor de LLM (por defecto `"COPILOT"`) | Opcional / específico de proveedor |
| `LEGACYMAPPER_LLM_MODEL` | Selecciona el modelo del proveedor de LLM | Opcional / específico de proveedor |
| `LEGACYMAPPER_LLM_PROVIDER_ID` | Identificador del proveedor (por defecto `<tipo_de_proveedor>-local`) | Opcional / específico de proveedor |
| `GEMINI_API_KEY` | Credencial para el proveedor Gemini (vía `config.credential_source`) | Opcional / específico de proveedor / desarrollo |

No existen otras variables de entorno usadas por el sistema. No hay archivo `.env`, `requirements.txt` ni `pyproject.toml` en el repositorio: LegacyMapper no depende de paquetes de terceros. No se debe documentar ninguna variable de entorno adicional sin verificarla primero contra el código.

---

## 18. Ejecutar LegacyMapper

### Preparación del entorno

LegacyMapper no requiere instalación de dependencias de terceros (no hay manifiesto de dependencias). Solo se necesita un intérprete de Python compatible.

### Comando de análisis

```
python main.py <repositorio> [--output <salida>] [--exclude <carpeta>] [--verbose] [--flow-max-depth <N>]
```

Verificado directamente en `legacy_documenter/main.py` (argparse). Valores por defecto: `--output` = `"output"`, `--flow-max-depth` = `12`. `--exclude` puede repetirse para excluir varias carpetas. `--verbose` eleva el nivel de logging a INFO (por defecto es WARNING).

> Nota menor: la descripción del `ArgumentParser` en el código todavía dice `"Legacy .NET Documentation Analyzer V1"`, una etiqueta de versión desactualizada respecto del sistema V4.1 real. Es un detalle cosmético del código, no un problema funcional; se deja registrado aquí para quien mantenga el CLI en el futuro.

### Comando de readiness

```
python -m legacy_documenter.knowledge.readiness
```

Verificado: el módulo existe (`legacy_documenter/knowledge/readiness.py`, decompuesto en V4.1-R4 en `_readiness_parsing.py`, `_readiness_evidence.py` y `_readiness_io.py`, conservando el mismo punto de entrada público). Lee `output/LEVANTAMIENTO_FUNCIONAL.md`, `output/LEVANTAMIENTO_TECNICO.md` y `codex/V3/V3_R8_4_REVISION_HUMANA_APROBADA.md`; escribe cuatro artefactos JSON en `output/v3_r9/`. Al ejecutarse como script, imprime un objeto JSON con, entre otras, las claves `status`, `readiness`, `checks`, `ai_knowledge_allowed`, `ai_knowledge_generated`, `real_llm_calls`, `provider_calls`, `records`, `ineligible_records`, `output`.

### Comando de pruebas

```
python -m unittest discover -s tests
```

---

## 19. Pruebas

**Estrategia:** la suite combina pruebas unitarias, pruebas de regresión/equivalencia de comportamiento, pruebas de artefactos determinísticos y pruebas de seguridad, distribuidas en 51 archivos bajo `tests/` (más `tests/fixtures/`).

**Baseline actual (verificado ejecutando la suite directamente):**

```
1566 PASS
0 FAIL
0 SKIP
```

Esto coincide con lo registrado en `PROJECT_STATE.json` y en el cierre final de V4.1.

**Pruebas de regresión/equivalencia:** especialmente relevantes en V4.1-R9 ("Comprehensive Regression and Behavioral Equivalence"), que verificó que ninguna ronda de refactor de mantenibilidad (R1–R8) cambió el comportamiento observable del sistema.

**Pruebas de artefactos determinísticos:** verifican que los artefactos generados (hashes, manifiestos, reportes de baseline) sean reproducibles a partir de las mismas entradas.

**Pruebas de seguridad:** cubren invariantes como rutas seguras en la proyección (sin path traversal) y sanitización.

**Lección REG-001:** las pruebas no deben fijar como literal exacto (hardcodear) una cifra redonda transitoria de `PROJECT_STATE` (por ejemplo, un conteo de pruebas específico capturado en un momento dado) cuando esa cifra es esperable que cambie con el tiempo a medida que se agregan pruebas. Se prefiere verificar contra la fuente autoritativa actual (`PROJECT_STATE.json`) o contra invariantes estructurales, no contra un número que quedará desactualizado.

---

## 20. Refactor de mantenibilidad V4.1

Historial conciso de las rondas R0–R10 (sin reproducir cada reporte de ronda; ver los documentos individuales en `docs/V4_1/` para el detalle completo):

- **R0:** inventario de mantenibilidad y plan de refactor.
- **R1:** corrección de regresión y renderizador JSON compartido (unificación de renderizado JSON usado por varios módulos).
- **R2:** mejoras de legibilidad en modelos, tipos y contratos públicos.
- **R3:** mejoras de nomenclatura de bajo riesgo.
- **R4:** descomposición del módulo de readiness en submódulos privados (`_readiness_*`), preservando el punto de entrada público.
- **R5:** caracterización (characterization tests) de orquestadores riesgosos antes de tocarlos.
- **R6:** cierre de gaps y extracción controlada en áreas de mayor riesgo (incluida la descomposición del extractor de base de datos).
- **R7:** limpieza de fronteras de excepciones y adaptadores.
- **R8:** nomenclatura y documentación, segunda parte.
- **R9:** regresión comprehensiva y verificación de equivalencia de comportamiento.
- **R10:** baseline final y cierre formal.

**Principio constante en todas las rondas:** el cambio de comportamiento observable estuvo **prohibido**. Cada ronda de refactor de mantenibilidad debía preservar exactamente el comportamiento previo, verificado mediante pruebas de caracterización y regresión.

Temas resumidos a través de las rondas: renderizado JSON compartido, mejoras de tipado/contratos, nomenclatura, descomposición del módulo de readiness, caracterización de orquestadores, extracción controlada, limpieza de fronteras de excepciones, documentación/nomenclatura, verificación de equivalencia comprehensiva y baseline final.

---

## 21. Deuda técnica remanente

Ledger final verificado contra `docs/V4_1/V4_1_R10_FINAL_BASELINE_AND_FORMAL_CLOSURE_RESULT.md` y el cierre final:

| Ítem | Estado |
|---|---|
| `DUP-001` | `RESOLVED` |
| `DUP-002` | `PRESERVED_DISTINCT` |
| `DUP-003` | `UNTOUCHED` |
| `DUP-004` | `UNTOUCHED` |
| `DEBT-001` | `RESOLVED` |
| `DEBT-002` | `RESOLVED` |
| `DEBT-003` | `RESOLVED` |
| `REG-002-CANDIDATE` | `RESOLVED` |
| `TD-001` | `OPEN` |
| `TD-002` | `DEFERRED` |
| `TD-003` | `PRESERVED_DISTINCT` |
| `TD-004` | `PARTIALLY_RESOLVED` |
| `TD-005` | `PARTIALLY_RESOLVED` |

**Qué significa `PRESERVED_DISTINCT`:** indica un caso donde dos piezas de código son similares pero se evaluó deliberadamente que **no** deben unificarse, porque representan responsabilidades o variaciones intencionalmente distintas; unificarlas introduciría acoplamiento incorrecto en lugar de eliminar duplicación real.

**No se debe tratar deuda `DEFERRED` u `OPEN` como si requiriera corrección inmediata.** Estas clasificaciones son decisiones deliberadas tomadas dentro del alcance formal de V4.1: quedaron fuera de alcance a propósito, no por omisión, y su tratamiento (si corresponde) es una decisión de una futura ronda o de V5, no una corrección urgente sobre el baseline cerrado.

---

## 22. Cómo modificar LegacyMapper de forma segura

1. Leer la autoridad del repositorio (`CLAUDE.md`, `AGENTS.md`, `PROJECT_STATE.json`, `docs/PROJECT_RECOVERY.md`).
2. Revisar `PROJECT_STATE.json` para conocer el estado y la ronda vigente.
3. Entender el contrato afectado (modelos, enums, IDs, reglas de proyección, etc.) antes de tocar código.
4. Caracterizar el comportamiento actual (pruebas de caracterización) si el área es riesgosa, antes de refactorizar.
5. Agregar o modificar pruebas que reflejen el cambio deseado.
6. Implementar el cambio más pequeño posible que satisfaga el objetivo.
7. Ejecutar las pruebas focalizadas del área modificada.
8. Ejecutar la regresión completa (`python -m unittest discover -s tests`).
9. Ejecutar readiness (`python -m legacy_documenter.knowledge.readiness`).
10. Verificar artefactos determinísticos si el cambio pudo afectarlos (hashes, manifiestos).
11. Solicitar revisión humana.
12. Confirmar (commit) y versionar el cambio según el proceso del repositorio.

**Cuándo NO refactorizar:** no se debe refactorizar únicamente por preferencia estética, ni tocar áreas de alto riesgo sin cobertura de caracterización adecuada, ni mezclar refactor de mantenibilidad con cambio de comportamiento en el mismo paso. Si un área fue marcada como deuda `DEFERRED` o `PRESERVED_DISTINCT`, se debe respetar esa decisión salvo que exista una razón explícita y documentada para reabrirla.

---

## 23. Guía de Python para un desarrollador C#

| Concepto Python | Equivalente aproximado en C# |
|---|---|
| Módulo Python | Responsabilidad de un archivo fuente / namespace en C# |
| `dataclass` | Modelo tipo DTO / value object |
| `Enum` | `enum` de C# |
| Tupla / modelo inmutable (`frozen=True`) | Dato inmutable / de solo lectura |
| Type hints (anotaciones de tipo) | Ayuda de documentación/análisis estático, similar en espíritu a la verificación en tiempo de compilación, pero **no** forzada por el intérprete en tiempo de ejecución |
| `__init__.py` | Superficie pública de un paquete |
| `pytest` / `unittest` | Conceptos equivalentes a un framework de pruebas unitarias en C# |

Estas son **comparaciones conceptuales**, no equivalencias exactas entre lenguajes: por ejemplo, los type hints de Python no impiden en tiempo de ejecución que se pase un valor de tipo incorrecto, a diferencia del sistema de tipos de C#.

**Por qué no se deben introducir getters/setters/interfaces triviales al estilo C# en Python:** en Python, un atributo público accedido directamente ya cumple el rol de un getter/setter trivial; envolverlo en métodos `get_x()`/`set_x()` sin lógica adicional no aporta seguridad de tipos (Python no la impone así) y solo agrega ruido. De forma similar, crear una interfaz formal solo para un único implementador no sigue una convención idiomática de Python, donde el "duck typing" y los `Protocol` (cuando se necesitan) cumplen ese rol de forma más ligera.

---

## 24. Puntos de extensión

Puntos de extensión seguros respaldados por evidencia actual:

- **Nuevos extractores** dentro de `legacy_documenter/extractors/`, siguiendo el mismo patrón determinístico de los existentes.
- **Nuevas reglas de proyección** (`ProjectionRule`) dentro del conjunto cerrado `ALL_TARGETS` de `projection/rules.py`, siempre que respeten la restricción de comparar únicamente campos estructurados.
- **Nuevos proveedores de LLM** dentro de `legacy_documenter/llm/providers/`, siguiendo el patrón de frontera existente (`copilot.py`, `gemini.py`).

Estos puntos de extensión son los que la arquitectura actual soporta con evidencia real de patrón repetible. **No se deben inventar** puntos de extensión adicionales (por ejemplo, un mecanismo de plugins de terceros) que no estén respaldados por código existente: eso corresponde al alcance de diseño de V5, no a este manual.

---

## 25. Solución de problemas para desarrolladores

| Problema | Causa probable | Qué revisar |
|---|---|---|
| Errores de importación | Ejecución desde un directorio incorrecto, o módulo movido/renombrado | Verificar que se ejecuta desde la raíz del repositorio y que las rutas de importación siguen la estructura actual de `legacy_documenter/` |
| Regresión de pruebas | Un cambio alteró comportamiento observable sin caracterización previa | Revisar el diff contra el principio de "sin cambio de comportamiento" en refactors de mantenibilidad; agregar/ajustar pruebas de caracterización |
| Falla de readiness | Falta algún artefacto esperado en `output/` o en `codex/V3/` | Revisar el detalle de `checks` que imprime el comando de readiness |
| Discrepancia de hash de artefacto | Un artefacto determinístico cambió su contenido sin que se actualizara el hash de referencia, o el cambio introdujo no-determinismo | Verificar que la generación del artefacto siga siendo reproducible (sin timestamps, UUIDs aleatorios, orden no determinístico) |
| Salida no determinística | Uso accidental de tiempo, orden de iteración no garantizado, o aleatoriedad en generación de IDs | Revisar que todo ID se derive vía `stable_id(...)` y que no se use `datetime.now()`/`uuid4()` en rutas determinísticas |
| Llamada inesperada a proveedor de IA | Código de prueba o de análisis invocando `deep_interpretation` sin mock/stub | Verificar configuración de proveedor y que las pruebas no dependan de llamadas reales (`provider_calls` debe ser `0` en baseline) |
| Extracción no resuelta | El patrón de código no coincide con lo reconocido por el extractor | Confirmar si el patrón es parte del alcance tecnológico actual (sección 3); si lo es, puede ser un caso a cubrir en un extractor |
| Estado de git sucio | Cambios sin confirmar durante una tarea de mantenimiento | Revisar `git status`, confirmar o descartar deliberadamente antes de continuar |
| Modificación de artefacto histórico | Se intentó editar un documento de cierre o baseline ya formalmente cerrado | No modificar documentos de cierre histórico (V4 o V4.1); cualquier corrección debe ir en un documento nuevo, nunca reescribiendo el cierre original |
| Violación de frontera canónico/proyección | Código de proyección intentando escribir o modificar conocimiento canónico | Las proyecciones (`projection/`, `plugin_projection/`) deben ser estrictamente de solo lectura sobre `CanonicalKnowledgeCollection` |

---

## 26. Recuperación y continuidad

Un desarrollador o agente de IA nuevo debe poder retomar el proyecto **únicamente** a partir de los artefactos del repositorio, sin necesidad de historial de conversación previo. El orden de lectura recomendado es:

1. `PROJECT_STATE.json` — estado autoritativo actual.
2. `docs/PROJECT_RECOVERY.md` — guía de recuperación si el repositorio "no compila mentalmente" (checkout nuevo, sin memoria de sesión).
3. `AGENTS.md`.
4. `CLAUDE.md`.
5. Documentos de cierre final relevantes (V4: `docs/V4/V4_FINAL_CLOSURE_RESULT.md`; V4.1: `docs/V4_1/V4_1_FINAL_CLOSURE_AND_VERSIONING_RESULT.md`).
6. El baseline final y el manifiesto asociado.

El historial de conversación de desarrollo **no** es requisito para retomar el proyecto: toda la información necesaria debe estar en el repositorio.

---

## 27. Frontera de V5

**Explícitamente NO IMPLEMENTADO EN V4.1.** Lo siguiente es alcance **futuro** de V5, no una capacidad actual:

- Agnosticismo de lenguaje.
- Agnosticismo de framework.
- Agnosticismo de layout de proyecto.
- Agnosticismo de patrón arquitectónico.
- Agnosticismo de base de datos/persistencia.
- Agnosticismo de proveedor de IA.
- Agnosticismo de modelo de IA.

Este manual no diseña V5; solo delimita el alcance actual de V4.1 frente a esas metas futuras.

---

Para una introducción no técnica, ver el [Manual de Usuario V4.1](LEGACYMAPPER_USER_MANUAL_V4_1.md).
Para definiciones breves de términos, ver el [Glosario V4.1](LEGACYMAPPER_GLOSSARY_V4_1.md).
