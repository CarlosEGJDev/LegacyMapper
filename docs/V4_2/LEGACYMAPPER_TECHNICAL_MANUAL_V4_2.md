# LegacyMapper — Manual Técnico (V4.2)

Este es el mapa principal de traspaso para desarrolladores, mantenimiento y auditoría de código de
LegacyMapper. Se deriva de la lectura del árbol de fuentes actual (`legacy_documenter/`, `main.py`,
`tests/`, `tools/`), los contratos actuales (`PROJECT_STATE.json`, `.gitignore`,
`docs/GENERATED_ARTIFACT_POLICY.md`) y los documentos actuales de cierre de V4.2 — no de la memoria de
documentación histórica. Donde el código actual no concuerda con afirmaciones históricas, este manual
documenta la implementación actual y señala la discrepancia explícitamente (ver también la sección
`SOURCE_VS_DOCUMENTATION_DISCREPANCIES` del documento de resultado de la ronda).

V4.2 está formalmente cerrada. V5 no está implementada. Nada en este manual debe leerse como que V5 ya
existe.

---

## §6 Mapa del repositorio

| Ruta | Tipo | Responsabilidad |
|---|---|---|
| `main.py` | Punto de entrada | Dos líneas: importa `legacy_documenter.main.main` y lo invoca como el código de salida del proceso. |
| `legacy_documenter/` | Fuente de producción | La implementación completa de LegacyMapper (169 archivos `.py` a la fecha de esta ronda — ver §22). |
| `tests/` | Tests | 62 módulos de test, basados en `unittest`, organizados cronológicamente por ronda (V1→V4.2-R8). Ver §16. |
| `tools/` | Herramientas de desarrollo | Scripts puntuales/manuales: constructores de baseline/manifiesto, un verificador manual seguro de la ruta de IA, generadores históricos de rondas de V4.1. No son importados por el código de producción. Ver §17. |
| `docs/` | Gobernanza/historia | Documentos de resultado de ronda, registros de cierre, la política de artefactos generados, el documento de recuperación, este conjunto de manuales. Organizado por versión (`V3/`, `V4/`, `V4_1/`, `V4_2/`). |
| `prompts/` | Gobernanza/historia | Los documentos de instrucción activos/históricos contra los cuales se ejecutó cada ronda, organizados de la misma manera que `docs/`. |
| `codex/` | Historia del agente de desarrollo | Informes/instrucciones compactos y orientados a máquina producidos por el agente de desarrollo, históricamente liderados por Codex (V1–V3); el nombre se preserva por continuidad, no es un requisito exclusivo de Codex (`AGENTS.md`). |
| `result_codex/` | Evidencia histórica | Informe(s) de análisis temprano(s) (era V1) anteriores a la división `codex/`/`docs/`. |
| `output/` | Mixto: contratos rastreados + salida generada local | Los artefactos canónicos pequeños (baselines, manifiestos, documentación aprobada) están rastreados; los volcados de escaneo pesados/regenerables y la salida de pilotos de sistemas reales están excluidos por `.gitignore`. Ver §19. |
| `context/` | Directorio de trabajo en tiempo de ejecución | Creado y poblado en tiempo de ejecución por `legacy_documenter/context/context_builder.py`; vacío en un checkout limpio salvo `.gitkeep`. **Colisión de nombres**: este `context/` de nivel superior no tiene relación con el paquete de producción `legacy_documenter/context/` (ver §8). |
| `AGENTS.md` | Gobernanza | Instrucciones operativas del agente de desarrollo: autonomía, límite de permisos, reglas del proyecto, control de fases. |
| `CLAUDE.md` | Gobernanza | Dirige a cualquier agente basado en Claude hacia `AGENTS.md`/`PROJECT_STATE.json`/documentos de traspaso; deliberadamente no duplica reglas. |
| `PROJECT_STATE.json` | Gobernanza | El único puntero autoritativo y legible por máquina al estado/ronda/estatus/riesgos conocidos/deuda actuales. |
| `.gitignore` | Gobernanza/mecánico | Aplica la política de artefactos generados por ruta explícita, nunca un comodín amplio. |

## §7 Inventario de módulos

Todos los paquetes están bajo `legacy_documenter/`. "Invocado por" está orientado a comandos de la CLI; la
mayoría de los subpaquetes de conocimiento son alcanzables solo desde sus propios tests y desde
`readiness.py`/la ruta legada de `main.py`, no desde la orquestación de `full`.

| Paquete | Propósito | Archivos clave | Clases/funciones principales | Entradas | Salidas | Depende de | Invocado por | Tests |
|---|---|---|---|---|---|---|---|---|
| `cli/` | Parseo de CLI, enrutamiento, modelo de ejecución/resultado, orquestación resiliente de `full`, presentación de UX | `parser.py`, `router.py`, `execution_model.py`, `stage_identity.py`, `pipeline_stages.py`, `full_pipeline.py`, `run_summary_presenter.py`, `artifact_lifecycle.py`, `serialization.py` | `build_parser`, `route`, `RunResult`/`StageResult`/`RunStatus`/`StageStatus`, `StageId`, `run_full_pipeline` | `sys.argv`, ruta del repositorio en el sistema de archivos | Código de salida, `RunResult`, `RUN_SUMMARY.{json,md}` | `orchestration/`, `knowledge/readiness.py`, `scanner/`, `extractors/`, `analysis/`, `exporters/`, `context/`, `documentation/` | `main.py` | `test_v4_2_r1_*`, `_r2_*`, `_r5*`, `_r6*` |
| `scanner/` | Recorrido determinista del repositorio y clasificación por archivo | `repository_scanner.py`, `file_classifier.py` | `RepositoryScanner`, `FileClassifier` | Ruta raíz del repositorio, lista de exclusión | Lista de `SourceFile`, estadísticas de clasificación | `models/`, `config.py` | `cli/pipeline_stages.py` | `test_v1*`, `test_v4_2_r2*` |
| `extractors/` | Parsea archivos de código/configuración/proyecto en modelos de dominio | `solution_extractor.py`, `vbproj_extractor.py`, `vbnet_extractor.py`, `webforms_extractor.py`, `webconfig_extractor.py`, `web_event_extractor.py`, `call_extractor.py`, `database_extractor.py` + ayudantes privados `_database_*.py` | `SolutionExtractor`, `VBProjExtractor`, `VBNetExtractor`, `WebFormsExtractor`, `WebConfigExtractor`, `WebEventExtractor`, `CallExtractor`, `DatabaseExtractor` | `SourceFile`s clasificados | Soluciones, proyectos, símbolos, WebForms, llamadas, registros de acceso a datos, operaciones SQL, configuración | `models/`, `scanner/` | `cli/pipeline_stages.py::extract_repository` | `test_v1*`, `test_v3_r*`, `test_v4_1_r5/r6_*extractor*` |
| `analysis/` | Resolución/interpretación determinista sobre los datos extraídos | `call_resolver.py`, `web_entry_resolver.py`, `database_resolver.py`, `flow_resolver.py` (+ `_flow_graph_construction.py`, `_flow_key_labels.py`, `_flow_report_composition.py`), `dependency_resolver.py`, `deep_source.py`, `deep_interpretation.py`, `targeted_exhaustion.py` | `CallResolver`, `WebEntryResolver`, `DatabaseResolver`, `FlowResolver`, `DependencyResolver` | Símbolos/llamadas/webforms/acceso a datos extraídos | Llamadas resueltas, puntos de entrada, flujos/rutas funcionales, grafo de dependencias | `models/`, `extractors/` | `cli/pipeline_stages.py` | `test_v4_1_r5/r6_flow_resolver*`, `test_v4_2_r7_1*`, `test_v4_2_r7_synthetic*` |
| `exporters/` | Renderizado determinista JSON/Markdown de resultados de análisis | `json_exporter.py`, `markdown_exporter.py`, `technical_documentation_renderer.py`, `_documentation_partitioning.py` | `JSONExporter`, `MarkdownExporter`, `TechnicalDocumentationRenderer` | Diccionario `indexes` ensamblado por `pipeline_stages`/`full_pipeline` | `index/*.json`, `documentation/*.md`, `documentation/<doc>/<nombre-seguro>.md` | `utils/atomic_write.py`, `utils/sanitizer.py` | `cli/pipeline_stages.py::render_documentation` | `test_v4_2_r3*`, `test_v4_2_r7_1*`, `test_v4_2_r8*` |
| `context/` | Construye artefactos compactos de contexto en tiempo de ejecución y un límite de lectura/composición para IA | `context_builder.py`, `system_context_builder.py`, `resolver.py`, `composer.py` | `ContextBuilder`, `SystemContextBuilder`, `ContextResolver`, `ContextComposer` | `indexes`, `output/ai_context/*.json` | `output/context/projects.json`, paquetes de contexto compuestos | ninguno más allá de `utils/` | `cli/pipeline_stages.py`, `orchestration/ai_interpretation.py` | `test_v3_r2_r3*`, `test_v4_2_r4*` |
| `documentation/` | Generación de documento funcional/técnico asistida por LLM de la era V3, agregación, consistencia, parseo de revisión humana | `generator.py`, `renderer.py`, `aggregation.py`, `interpretation.py`, `consistency.py`, `consistency_run.py`, `coverage.py`, `evidence_catalog.py`, `evidence_resume.py`, `envelope.py`, `hierarchical.py`, `human_review.py`, `second_review.py`, `synthesis.py`, `systematic.py`, `resume.py`, `contracts.py` | `render`, `aggregate`, `parse_document`, `AssessmentValidator` | Paquetes de contexto, respuestas de LLM (solo ruta V3) | `output/LEVANTAMIENTO_FUNCIONAL.md`/`_TECNICO.md` y JSON de evidencia relacionados | `context/`, `llm/` | `knowledge/readiness.py` (solo lee salidas); no invocado por `full`/`analyze` | `test_v3_r6*`, `test_v3_r7*`, `test_v3_r8*` |
| `knowledge/` | Modelo de dominio de conocimiento de V4: ingesta → procedencia → clasificación → temporal → relaciones → propuestas → aprobación → canónico → proyección/plugin_projection; más la puerta de preparación V3-R9 y los informes de cierre V4.1-R0/V4-R14 | Ver tabla de subpaquetes abajo | — | — | — | `documentation/`, `context/` (solo readiness) | `readiness()` solo alcanzable desde la CLI; los subpaquetes por lo demás autocontenidos y solo para test | `test_v3_r9*`, `test_v4_r1..r14*` |
| `llm/` | Contratos de solicitud/respuesta neutrales al proveedor y adaptadores concretos de proveedor | `core.py`, `providers/copilot.py`, `providers/gemini.py`, `copilot_pilot.py` | `LLMProvider`, `FakeLLMProvider`, `ProviderRegistry`, `CopilotProvider`, `GeminiProvider` | `LLMRequest` | `LLMResponse` | ninguno | `orchestration/ai_interpretation.py`, `documentation/generator.py` (ruta V3) | `test_v4_2_r4*`, `test_v4_2_r5_1*` |
| `orchestration/` | Costura de V4.2-R4 entre `full` y la lógica de IA/propuestas | `ai_interpretation.py`, `proposal_adapter.py` | `run_ai_interpretation`, `adapt_findings_to_proposals` | `output/ai_context/*.json`, `LLMProvider` inyectado/resuelto | `AiInterpretationResult`, `list[Proposal]` | `context/`, `llm/`, `knowledge/proposals/models.py` | `cli/full_pipeline.py` | `test_v4_2_r4*` |
| `models/` | Dataclasses de dominio simples compartidas entre extracción/análisis/exportación | `call.py`, `dependency.py`, `entry_point.py`, `evidence.py`, `project.py`, `source_file.py`, `symbol.py`, `webform.py` | `Call`, `Dependency`, `EntryPoint`, `Evidence`, `Project`, `SourceFile`, `Symbol`, `WebForm` | — | — | ninguno | Casi todos los demás paquetes | Cubierto indirectamente por tests de extractor/scanner/análisis |
| `quality/` | Herramienta determinista de inventario de mantenibilidad basada en AST | `maintainability_audit.py` | `audit`/`build_maintainability_inventory`/`write_audit` | Árbol `.py` de producción | JSON de mantenibilidad (tamaños de módulo, cobertura de tipado/docstring) | ninguno (solo `ast` de la biblioteca estándar) | `tools/`, rondas históricas V3-R10/V4.1-R0 | `test_v4_1_r0_maintainability_inventory*` |
| `utils/` | Pequeños ayudantes de infraestructura deterministas | `atomic_write.py`, `json_rendering.py`, `sanitizer.py` | `atomic_write_text`, `render_deterministic_json`, `sanitize_data` | — | — | ninguno | Casi todo escritor en la base de código | Cubierto indirectamente en toda la suite |
| `config.py` | Constantes compartidas | — | `DEFAULT_EXCLUDES`, `VTI_PREFIX` | — | — | ninguno | `scanner/` | — |
| `main.py` (a nivel de paquete, distinto del `main.py` de nivel superior) | Orquestación de compatibilidad legada de `analyze_repository` + `main()` de la CLI | — | `analyze_repository`, `main` | Argumentos de la CLI | Igual que `analyze` (§4.4) | `cli/parser.py`, `cli/router.py`, `cli/pipeline_stages.py` | `main.py` de nivel superior | `test_v1*`, `test_v4_2_r1*` |

### Subpaquetes de `knowledge/` (detalle)

| Subpaquete | Ronda de origen | Propósito | ¿Alcanzable desde la CLI? |
|---|---|---|---|
| `domain/` | V4-R1 | Modelo de dominio neutral a la fuente: `KnowledgeStatement`, `EvidenceRef`, `Provenance`, enums (`KnowledgeNature`, `KnowledgeStatus`, `SourceType`, `TemporalState`) | No — solo tipos fundacionales |
| `input/` | V4-R2 | Valida/normaliza/sanitiza material crudo en `MaterialItem` según `SourceType` | No |
| `ingestion/` | V4-R4 | Convierte un `SourceInput` redactado por un humano en un `MaterialItem` trazable + `ProvenanceNode` `MATERIAL` | No |
| `provenance/` | V4-R3 | Linaje acíclico `ProvenanceGraph`/`ProvenanceNode` que responde "de dónde vino esto" | No |
| `classification/` | V4-R5 | Registra `KnowledgeNature` para un `MaterialItem` ingerido sin inferir nuevos hechos | No |
| `temporal/` | V4-R6 | Separación en bloques temporales AS_IS/TO_BE/HISTORICAL/GAP | No |
| `relations/` | V4-R7 | Representación de relaciones de brecha/conflicto/diferencia/evolución | No |
| `proposals/` | V4-R8 | Modelo de ciclo de vida de pre-aprobación de `Proposal` (`ProposalStatus`, `ProposalKind`, `ProposalMethod`) | **Sí** — `orchestration/proposal_adapter.py` construye registros `Proposal` que `full_pipeline.py` escribe |
| `approval/` | V4-R9 | Modelo `ApprovalDecision` para APPROVED/REJECTED/CORRECTION_REQUESTED del Líder Técnico | No — superficie solo de diseño, `IMPLEMENTATION_STATUS=NOT_IMPLEMENTED` |
| `canonical/` | V4-R10 | Compone una `Proposal` aprobada + `ApprovalDecision` en una `CanonicalKnowledgeEntry` inmutable | No |
| `projection/` | V4-R11 | Proyecta una `CanonicalKnowledgeCollection` a Markdown legible por humanos (`DocumentProjection`) | No |
| `plugin_projection/` | V4-R12 | Proyecta una `CanonicalKnowledgeCollection` a `LegacyMapperPluginKnowledge` (carga útil versionada, legible por máquina) | No |
| `closure/` | V4.1-R10/V4-R14/V4.2-R8 | Construye informes finales de baseline/manifiesto a partir del estado del repositorio (usado por `tools/*_build_*artifacts.py`) | No (solo herramientas) |
| `readiness.py` + `_readiness_*.py` | V3-R9, extraído en V4.1-R4 | La propia puerta de preparación de conocimiento de LegacyMapper | **Sí** — `python main.py readiness` |

Todo desde `proposals/` hasta `plugin_projection/` (excepto `proposals/`, que `full` sí usa) está
implementado y probado unitariamente, pero **no está orquestado en conjunto** por ningún comando. Un
desarrollador que extienda el flujo de aprobación/canónico/proyección hacia una superficie CLI real está
construyendo nueva orquestación sobre código de dominio ya sólido, no escribiendo ese código de dominio
desde cero.

## §8 Mapa de archivos (archivos significativos seleccionados)

| Archivo | Tipo | Responsabilidad | Clase/función clave | Colaboradores | Tests |
|---|---|---|---|---|---|
| `legacy_documenter/cli/parser.py` | Orquestación/CLI | Gramática de argumentos + reescritura legada de la forma posicional desnuda | `build_parser`, `normalize_argv` | `router.py` | `test_v4_2_r1*`, `test_v4_2_r5*` |
| `legacy_documenter/cli/router.py` | Orquestación/CLI | Despacho + mapeo de código de salida (constantes `EXIT_*` autoritativas) | `route` | `full_pipeline.py`, `knowledge/readiness.py` | `test_v4_2_r1*`, `test_v4_2_r5_1*` |
| `legacy_documenter/cli/execution_model.py` | Modelo de dominio/contrato | `RunResult`/`StageResult`/`RunStatus`/`StageStatus`/`StageError` | — | Todo bajo `cli/` | `test_v4_2_r1*`, `test_v4_2_r5*` |
| `legacy_documenter/cli/stage_identity.py` | Contrato | Enum `StageId`, el vocabulario de 13 etapas | — | `full_pipeline.py` | `test_v4_2_r1*` |
| `legacy_documenter/cli/pipeline_stages.py` (421 líneas) | Orquestación (compartida) | Las funciones de etapa reales que invocan tanto `analyze` como `full`; también `render_documentation`/`DocumentationOutcome` | `scan_repository`, `extract_repository`, `resolve_calls`, `resolve_web_entries`, `resolve_database`, `resolve_flows`, `resolve_dependencies`, `export_artifacts`, `build_context_artifacts`, `render_documentation` | `scanner/`, `extractors/`, `analysis/`, `exporters/`, `context/` | `test_v3_r2_r3*`, `test_v4_2_r2/r3*` |
| `legacy_documenter/cli/full_pipeline.py` (490 líneas) | Orquestación (resiliente) | `run_full_pipeline`: orquestador resiliente de 13 etapas, finalización de `RunResult`, persistencia de propuestas | `run_full_pipeline`, `_compute_status`, `_assemble_indexes`, `_write_proposal_output` | `pipeline_stages`, `artifact_lifecycle`, `run_summary_presenter`, `orchestration/*` | `test_v4_2_r2*`, `_r4*`, `_r6*` |
| `legacy_documenter/cli/run_summary_presenter.py` (234 líneas) | Renderizador/UX | Renderizado de consola + `RUN_SUMMARY.md`; deriva `next_action`/`output_locations` | `render_console_summary`, `render_markdown_summary`, `derive_next_action`, `compute_output_locations` | `full_pipeline.py` | `test_v4_2_r5*` |
| `legacy_documenter/cli/artifact_lifecycle.py` | Utilidad (seguridad de reejecución) | Elimina `proposals/` obsoletos antes de que comience una nueva ejecución de `full` | `reset_stale_proposal_artifacts` | `full_pipeline.py` | `test_v4_2_r6*` |
| `legacy_documenter/cli/serialization.py` | Utilidad | `RunResult` → JSON determinista | — | `full_pipeline.py`/tests | `test_v4_2_r1*` |
| `legacy_documenter/scanner/repository_scanner.py` | Infraestructura | Recorrido recursivo con manejo de exclusiones | `RepositoryScanner` | `file_classifier.py`, `models/source_file.py` | `test_v1*` |
| `legacy_documenter/scanner/file_classifier.py` | Adyacente a extractor | Clasificación por tipo de archivo según extensión/nombre | `FileClassifier` | — | `test_v1*` |
| `legacy_documenter/extractors/database_extractor.py` (358 líneas) | Extractor | Extrae evidencia SQL/de acceso a datos de código fuente VB.NET, delegando el detalle de tokens/líneas/clasificación a sus ayudantes `_database_*` | `DatabaseExtractor` | `_database_classification.py`, `_database_line_scanner.py`, `_database_token_parsing.py` | `test_v4_1_r5/r6_database_extractor*` |
| `legacy_documenter/extractors/call_extractor.py` (245 líneas) | Extractor | Extrae sitios de llamada a método de código fuente VB.NET | `CallExtractor` | `models/call.py` | `test_v1*`, `test_v3_r4*` |
| `legacy_documenter/extractors/vbnet_extractor.py` | Extractor | Parsea declaraciones de clase/método/símbolo VB.NET | `VBNetExtractor` | `models/symbol.py` | `test_v1*` |
| `legacy_documenter/extractors/webforms_extractor.py` | Extractor | Parsea marcado `.aspx`/`.ascx` en busca de controles | `WebFormsExtractor` | `models/webform.py` | `test_v1*` |
| `legacy_documenter/extractors/web_event_extractor.py` | Extractor | Parsea vinculaciones de eventos de UI declaradas en el marcado | `WebEventExtractor` | `analysis/web_entry_resolver.py` | `test_v1*` |
| `legacy_documenter/extractors/webconfig_extractor.py` | Extractor | Parsea `web.config` en busca de hechos de configuración | `WebConfigExtractor` | — | `test_v1*` |
| `legacy_documenter/extractors/solution_extractor.py` / `vbproj_extractor.py` | Extractor | Parsea la estructura de proyecto `.sln`/`.vbproj` | `SolutionExtractor`, `VBProjExtractor` | `models/project.py` | `test_v1*` |
| `legacy_documenter/analysis/flow_resolver.py` (312 líneas) + `_flow_graph_construction.py`, `_flow_key_labels.py`, `_flow_report_composition.py` | Resolvedor (el componente de análisis más grande) | Construye y reporta grafos de flujo funcional hasta `--flow-max-depth`; agregación de estado en el peor caso a través de las rutas trazadas | `FlowResolver` | `call_resolver.py`, `web_entry_resolver.py`, `database_resolver.py` | `test_v4_1_r5/r6_flow_resolver*`, `test_v4_2_r7_1*`, `test_v4_2_r7_synthetic*` |
| `legacy_documenter/analysis/call_resolver.py` | Resolvedor | Resuelve los sitios de llamada extraídos a símbolos declarados | `CallResolver` | `models/symbol.py`, `models/call.py` | `test_v1*` |
| `legacy_documenter/analysis/web_entry_resolver.py` | Resolvedor | Resuelve vinculaciones de eventos de UI a puntos de entrada confirmados/no resueltos; brecha conocida: nunca adjunta `outgoing_calls` a entradas vinculadas desde el marcado (F-07) | `WebEntryResolver` | `extractors/web_event_extractor.py` | `test_v4_2_r7_synthetic*::FunctionalFlowTests` |
| `legacy_documenter/analysis/database_resolver.py` | Resolvedor | Resuelve registros de acceso a datos a procedimientos almacenados/operaciones SQL | `DatabaseResolver` | `extractors/database_extractor.py` | `test_v1*` |
| `legacy_documenter/analysis/dependency_resolver.py` | Resolvedor | Construye el grafo de dependencias entre proyectos/símbolos | `DependencyResolver` | `models/dependency.py` | `test_v1*` |
| `legacy_documenter/analysis/deep_source.py`, `deep_interpretation.py`, `targeted_exhaustion.py` | Herramientas de análisis de la era V3 | Herramientas históricas de agotamiento de evidencia e interpretación de V3-R7/R8, codificadas de forma fija a los archivos de evidencia fija/ids objetivo de `output/v3_r8_1`; **no invocadas por la etapa `AI_INTERPRETATION` de `full`** (ver §13) | `run_deep_interpretation` (entre otras) | `context/` | `test_v3_r7*`, `test_v3_r8*` |
| `legacy_documenter/exporters/markdown_exporter.py` | Renderizador | Los seis documentos originales de nombre fijo | `MarkdownExporter` | `utils/atomic_write.py` | `test_v4_2_r3*` |
| `legacy_documenter/exporters/technical_documentation_renderer.py` (802 líneas, la clase `TechnicalDocumentationRenderer` ~462 de ellas según la baseline de cierre de V4.2 — ver §12 para la medición actual) | Renderizador (deuda de mantenibilidad señalada) | Cuatro documentos más sus variantes de navegación/partición de V4.2-R8 | `TechnicalDocumentationRenderer` | `_documentation_partitioning.py`, `markdown_exporter._repository_display_label` | `test_v4_2_r3*`, `_r7_1*`, `_r8*` |
| `legacy_documenter/exporters/_documentation_partitioning.py` | Utilidad | Derivación determinista de nombres de archivo, segura frente a path traversal, para particiones | `sanitize_label`, `build_partition_filenames` | `technical_documentation_renderer.py` | `test_v4_2_r8*` |
| `legacy_documenter/exporters/json_exporter.py` | Renderizador/adaptador | Escribe `index/*.json` sanitizado | `JSONExporter` | `utils/sanitizer.py`, `utils/atomic_write.py` | `test_v1*` |
| `legacy_documenter/context/context_builder.py` | Adaptador de etapa de escritura | Escribe el resumen por proyecto `output/context/projects.json` | `ContextBuilder` | — | `test_v3_r2_r3*` |
| `legacy_documenter/context/system_context_builder.py` | Adaptador de etapa de escritura | Construye el modelo intermedio compacto `SYSTEM_CONTEXT.json` (origen V2-R5) | `SystemContextBuilder` | `utils/sanitizer.py` | `test_v3_r2_r3*` |
| `legacy_documenter/context/resolver.py` | Adaptador de etapa de lectura | Resolución de solo lectura de `ai_context/*.json`/`index/*.json` en paquetes tipados (`SYSTEM`/`FUNCTIONAL`/`TECHNICAL`/`ENTITY`/`FLOW`/`DATA_ACCESS`) | `ContextResolver` | — | `test_v3_r2_r3*`, `test_v4_2_r4*` |
| `legacy_documenter/context/composer.py` | Adaptador de etapa de lectura | Aplica un presupuesto de tokens/registros (perfiles `TINY`..`FULL`) a un paquete resuelto | `ContextComposer` | `context/resolver.py` | `test_v3_r2_r3*`, `test_v4_2_r4*` |
| `legacy_documenter/orchestration/ai_interpretation.py` | Costura de orquestación | Construye contexto solo de la ejecución actual, invoca al proveedor, valida la forma de la salida/cierre de referencias de evidencia | `run_ai_interpretation`, `_resolve_provider`, `_validate_findings` | `context/`, `llm/core.py` | `test_v4_2_r4*` |
| `legacy_documenter/orchestration/proposal_adapter.py` | Costura de orquestación | Convierte hallazgos de IA en registros `knowledge.proposals.models.Proposal` | `adapt_findings_to_proposals` | `knowledge/proposals/models.py` | `test_v4_2_r4*` |
| `legacy_documenter/llm/core.py` | Contrato/modelo de dominio | Contratos neutrales al proveedor de solicitud/respuesta/capacidad; `FakeLLMProvider`; `ProviderRegistry` (actualmente solo conecta `FAKE`/`COPILOT`) | `LLMProvider`, `LLMRequest`, `LLMResponse`, `FakeLLMProvider`, `ProviderRegistry` | — | `test_v4_2_r4*`, `_r5_1*` |
| `legacy_documenter/llm/providers/copilot.py` | Adaptador | Proveedor concreto sobre un cliente local de GitHub Copilot | `CopilotProvider` | `llm/core.py` | `test_v4_2_r4*` (vía fakes), protegido de llamadas reales en los tests |
| `legacy_documenter/llm/providers/gemini.py` | Adaptador (presente pero no registrado) | Proveedor concreto sobre la API HTTP de Gemini; lee `GEMINI_API_KEY` | `GeminiProvider` | `llm/core.py` | No ejercitado por los tests de ruta de registro de `tests/__init__.py`; ver discrepancia en §13 |
| `legacy_documenter/knowledge/readiness.py` + `_readiness_evidence.py`, `_readiness_io.py`, `_readiness_parsing.py` | Puerta de dominio / fachada de compatibilidad | La propia puerta de preparación de conocimiento de LegacyMapper (§4.6); `readiness.py` es el único punto de entrada público/de compatibilidad tras la extracción de V4.1-R4 | `KnowledgeReadinessService`, `run` | `documentation/human_review.py`, `documentation/second_review.py` | `test_v3_r9*`, `test_v4_1_r4*` |
| `legacy_documenter/knowledge/proposals/models.py` / `service.py` (254 líneas) | Modelo de dominio / servicio | `Proposal`, `ProposalStatus`, `ProposalKind`, `ProposalMethod`; servicio de ciclo de vida | — | `orchestration/proposal_adapter.py` | `test_v4_r8*` |
| `legacy_documenter/knowledge/canonical/models.py` / `service.py` (287 líneas) | Modelo de dominio / servicio | `CanonicalKnowledgeEntry` (reutiliza `KnowledgeStatement.validate()`), servicio de composición | — | No invocado por `full` | `test_v4_r10*` |
| `legacy_documenter/knowledge/plugin_projection/models.py` / `serializer.py` / `service.py` | Modelo de dominio / servicio | Contrato `LegacyMapperPluginKnowledge` (`CONTRACT_NAME`/`CONTRACT_VERSION = "1.0"`), `PluginKnowledgeEntry`/`Manifest`/`Payload` | — | No invocado por `full` | `test_v4_r12*` |
| `legacy_documenter/quality/maintainability_audit.py` | Herramientas/utilidad | Inventario de mantenibilidad estático, solo AST (no importa código en tiempo de ejecución) | `audit`, `write_audit` | solo `ast` de la biblioteca estándar | `test_v4_1_r0*` |
| `legacy_documenter/utils/atomic_write.py` | Infraestructura | Escrituras de texto atómicas por escritura-y-renombrado | `atomic_write_text` | — | Indirecto, vía cada escritor |
| `legacy_documenter/utils/json_rendering.py` | Infraestructura | Renderizado JSON determinista con claves ordenadas y separadores fijos | `render_deterministic_json` | — | Indirecto |
| `legacy_documenter/utils/sanitizer.py` | Infraestructura/seguridad | Elimina valores con forma de secreto de la evidencia exportada | `sanitize_data` | — | Indirecto, vía `json_exporter.py`, `system_context_builder.py` |

Agrupados, no tabulados individualmente arriba (pequeños, cohesivos, de bajo riesgo): `legacy_documenter/models/*.py`
(ocho archivos de dataclass de un solo propósito, de 16 a 60 líneas cada uno); los archivos
`legacy_documenter/knowledge/*/enums.py` y `*/contract_report.py`/`*/example_report.py` en los subpaquetes
de conocimiento (generadores de documentación/ejemplos de contrato, no lógica en tiempo de ejecución);
los ayudantes de generación/agregación/consistencia de `legacy_documenter/documentation/*.py` de la era V3
más allá de `generator.py`/`renderer.py` (autocontenidos, ejercitados solo por tests de la era V3 y no
alcanzables desde `full`/`analyze`).

## §9 Arquitectura de ejecución

```
sys.argv
  -> legacy_documenter/cli/parser.py: normalize_argv (reescritura de la forma legada) -> build_parser (argparse)
  -> legacy_documenter/main.py: main() parsea los argumentos, invoca legacy_documenter/cli/router.py: route(args, analyze_repository)
       command == "analyze" -> _route_analyze -> legacy_documenter.main.analyze_repository
           -> cli/pipeline_stages.py: scan_repository -> extract_repository -> resolve_calls ->
              resolve_web_entries -> resolve_database -> resolve_flows -> resolve_dependencies ->
              export_artifacts -> build_context_artifacts
           -> sale con 0 incondicionalmente (sin seguimiento de resultado a nivel de etapa)
       command == "full" -> _route_full -> cli/full_pipeline.py: run_full_pipeline
           -> las mismas funciones de etapa, cada una envuelta para contención de fallo parcial (ver §10)
           -> cli/pipeline_stages.py: render_documentation (etapa DOCUMENTATION)
           -> [opcional] orchestration/ai_interpretation.py: run_ai_interpretation (AI_INTERPRETATION)
           -> [opcional] orchestration/proposal_adapter.py: adapt_findings_to_proposals (PROPOSAL_GENERATION)
           -> cli/run_summary_presenter.py: finalize_and_write_run_summary (FINAL_SUMMARY)
           -> código de salida del mapa EXIT_* de router.py, indexado por RunResult.status
       command == "readiness" -> _route_readiness -> knowledge/readiness.py: run()
           -> sale con 0/1 indexado por "READY"/"BLOCKED"
```

`analyze` y `full` divergen en exactamente un aspecto arquitectónico: `analyze` invoca las funciones de
etapa compartidas directamente sin manejo de excepciones propio (un fallo inesperado se propaga y aborta el
proceso — el comportamiento pre-V4.2, preservado intencionalmente); `full` envuelve cada etapa de forma
independiente (`cli/full_pipeline.py::_run_stage`/`_skipped`) de modo que un fallo se captura como un
`StageError` en lugar de hacer fallar a las etapas hermanas. Ambos terminan invocando exactamente las mismas
implementaciones de etapa en `cli/pipeline_stages.py` — no existe una segunda implementación de análisis
divergente para `full`.

## §10 Pipeline completo (`full`)

| Etapa | Responsabilidad | Implementación | Entrada | Salida | Comportamiento ante fallo | Depende de | Tests |
|---|---|---|---|---|---|---|---|
| `SCAN` | Recorrer el repositorio, clasificar archivos | `pipeline_stages.scan_repository` → `scanner/` | Raíz del repo, exclusiones | Lista de `SourceFile`, estadísticas | `FAILED`; todo lo posterior se omite | — | `test_v4_2_r2*` |
| `EXTRACTION` | Parsear soluciones/proyectos/símbolos/webforms/configuración/llamadas/acceso a datos | `pipeline_stages.extract_repository` → `extractors/` | Archivos clasificados | Soluciones/proyectos/símbolos/webforms/llamadas/acceso a datos/errores | `FAILED`; `CALL_RESOLUTION`/`DATABASE_RESOLUTION`/`DEPENDENCY_RESOLUTION`/`EXPORT`/`CONTEXT`/`DOCUMENTATION` todas omitidas | `SCAN` | `test_v4_2_r2*` |
| `CALL_RESOLUTION` | Resolver sitios de llamada a símbolos | `pipeline_stages.resolve_calls` → `analysis/call_resolver.py` | Llamadas, símbolos | Llamadas resueltas, dependencias funcionales | `FAILED`; `WEB_ENTRY_RESOLUTION`/`FLOW_RESOLUTION` omitidas | `EXTRACTION` | `test_v4_2_r2*` |
| `WEB_ENTRY_RESOLUTION` | Resolver eventos de UI a puntos de entrada | `pipeline_stages.resolve_web_entries` → `analysis/web_entry_resolver.py` | Webforms, símbolos, eventos web, llamadas resueltas | Puntos de entrada, vinculaciones de evento | `FAILED`; `FLOW_RESOLUTION` omitida | `CALL_RESOLUTION` | `test_v4_2_r2*` |
| `DATABASE_RESOLUTION` | Resolver acceso a datos a procedimientos almacenados/operaciones SQL | `pipeline_stages.resolve_database` → `analysis/database_resolver.py` | Índices de acceso a datos, proyectos | Acceso a datos, procedimientos almacenados, operaciones SQL | `FAILED`; `FLOW_RESOLUTION` omitida | `EXTRACTION` | `test_v4_2_r2*` |
| `FLOW_RESOLUTION` | Construir grafos de flujo funcional | `pipeline_stages.resolve_flows` → `analysis/flow_resolver.py` | Puntos de entrada, llamadas, acceso a datos, dependencias funcionales, `--flow-max-depth` | Flujos/rutas/resumen/no resueltos funcionales | `SKIPPED_DUE_TO_UPSTREAM_FAILURE` si alguna de las tres anteriores falló; en otro caso `FAILED` por su propio error | `CALL_RESOLUTION`, `WEB_ENTRY_RESOLUTION`, `DATABASE_RESOLUTION` | `test_v4_2_r2*`, `_r7_1*` |
| `DEPENDENCY_RESOLUTION` | Construir el grafo de dependencias entre proyectos | `pipeline_stages.resolve_dependencies` → `analysis/dependency_resolver.py` | Soluciones, proyectos, símbolos, webforms | Lista de dependencias | `FAILED`; ninguna etapa posterior depende exclusivamente de ella | `EXTRACTION` | `test_v4_2_r2*` |
| `EXPORT` | Escribir `index/*.json` + Markdown | `pipeline_stages.export_artifacts` → `exporters/json_exporter.py`, `markdown_exporter.py` | Diccionario `indexes` ensamblado | `output/index/*`, seis documentos fijos | `FAILED`; la ejecución se degrada a `FAILED` en general (regla de estado de §9) | `EXTRACTION` | `test_v4_2_r2*` |
| `CONTEXT` | Escribir artefactos de contexto | `pipeline_stages.build_context_artifacts` → `context/` | `indexes` | `output/context/*`, `output/ai_context/*` | `FAILED`; `AI_INTERPRETATION` omitida | `EXTRACTION` | `test_v4_2_r2*` |
| `DOCUMENTATION` | Renderizar cuatro documentos fijos más navegación/particiones | `_run_documentation_stage` → `exporters/technical_documentation_renderer.py` | `indexes` | `documentation/*.md`, `documentation/<doc>/*` | El fallo de un renderizador se registra en `DocumentationOutcome.failures`, los demás siguen ejecutándose; el envoltorio aún reporta la etapa `FAILED` si algún renderizador falló | `EXTRACTION` | `test_v4_2_r3*`, `_r8*` |
| `AI_INTERPRETATION` | Interpretación opcional sobre la evidencia de la ejecución actual | `_run_ai_interpretation_stage` → `orchestration/ai_interpretation.py` | `output/ai_context/*.json` | `AiInterpretationResult` | `NOT_RUN` a menos que se habilite; `SKIPPED_DUE_TO_UPSTREAM_FAILURE` si `CONTEXT` falló; `FAILED` ante error de proveedor/validación | `CONTEXT` (solo si se habilita) | `test_v4_2_r4*` |
| `PROPOSAL_GENERATION` | Convertir hallazgos en `Proposal`s | `orchestration/proposal_adapter.py` | `AiInterpretationResult.findings` | `list[Proposal]` | `NOT_RUN` a menos que se habilite; `SKIPPED_DUE_TO_UPSTREAM_FAILURE` si `AI_INTERPRETATION` falló | `AI_INTERPRETATION` (solo si se habilita) | `test_v4_2_r4*` |
| `FINAL_SUMMARY` | Escribir `RUN_SUMMARY.{json,md}` | `run_summary_presenter.finalize_and_write_run_summary` | Lista completa de etapas + `RunResult` | `RUN_SUMMARY.json`/`.md` | Añadido a la lista de etapas; su propio resultado influye en el `RunStatus` final | Todas las etapas previas | `test_v4_2_r6*` |

`RunResult`/`StageResult`/`RunStatus`/`StageStatus` (`cli/execution_model.py`) son el contrato compartido: un
`RunResult` lleva el nombre del comando, el `RunStatus` global, una tupla ordenada de `StageResult`s (cada
uno un `StageId` + `StageStatus` + `StageError` opcional), y los campos del límite de aprobación listados en
§4.5/§4.12. La contención parcial/de fallos está implementada enteramente en `cli/full_pipeline.py` vía
`_run_stage` (captura cualquier excepción, la convierte en `StageError`) y `_skipped` (registra qué
etapa(s) ascendente(s) bloquearon esta) — no hay una abstracción de motor de flujo de trabajo separada; es
control de flujo Python explícito y plano.

## §11 Extracción / Análisis

Descubrimiento determinista, en orden de dependencia:

1. **Escaneo del repositorio** (`scanner/repository_scanner.py`, `file_classifier.py`) — recorre el árbol,
   clasifica cada archivo (`solution`, `project`, `vbnet_source`, `webform_markup`, `webform_codebehind`,
   `webconfig`, etc.) usando únicamente heurísticas de extensión/nombre.
2. **Descubrimiento de proyecto/solución** (`extractors/solution_extractor.py`, `vbproj_extractor.py`) —
   parsea la estructura `.sln`/`.vbproj` en registros de `models/project.py`.
3. **Símbolos VB.NET** (`extractors/vbnet_extractor.py`) — parsea declaraciones de clase/método en
   `models/symbol.py`.
4. **WebForms y code-behind** (`extractors/webforms_extractor.py`, `web_event_extractor.py`) — parsea
   marcado `.aspx`/`.ascx` y vinculaciones de eventos de UI.
5. **Llamadas** (`extractors/call_extractor.py`) — extrae sitios de llamada crudos; `analysis/call_resolver.py`
   los resuelve a símbolos declarados.
6. **Puntos de entrada de WebForms** (`analysis/web_entry_resolver.py`) — resuelve eventos de UI en puntos
   de entrada `confirmed`/no resueltos. Brecha conocida (F-07): nunca adjunta `outgoing_calls` a un punto de
   entrada vinculado desde el marcado — una observación deliberadamente preservada, no corregida en silencio
   (ver §20).
7. **Acceso a base de datos** (`extractors/database_extractor.py` + `_database_classification.py`,
   `_database_line_scanner.py`, `_database_token_parsing.py`; resuelto por `analysis/database_resolver.py`)
   — extrae y clasifica evidencia SQL/de acceso a datos, procedimientos almacenados y operaciones SQL a
   partir de código fuente VB.NET.
8. **Resolución de flujo funcional** (`analysis/flow_resolver.py` + sus tres ayudantes `_flow_*`) — traza
   rutas de llamada a método confirmadas desde los puntos de entrada hasta terminales de base de
   datos/procedimiento almacenado, hasta `--flow-max-depth`. El estado/confianza son agregaciones en el
   peor caso a través de cada ruta trazada para un flujo (ver el texto introductorio citado del Manual de
   Usuario §4.8) — un flujo puede ser `unresolved_boundary` en general mientras aún haya alcanzado un
   terminal confirmado en una ruta; ambos hechos se preservan de forma independiente.
9. **Resolución de dependencias** (`analysis/dependency_resolver.py`) — construye el grafo de dependencias
   entre proyectos/símbolos a partir de soluciones/proyectos/símbolos/webforms.
10. **Límites no resueltos y trazabilidad** — cada resolvedor preserva explícitamente las distinciones
    `confirmed` / `inferred` / `unresolved` (nunca promovidas en silencio; `AGENTS.md`, "Project Rules"); el
    documento `UNRESOLVED_FINDINGS.md` y los registros `flow_unresolved` son la superficie de cara al humano
    de esto.

Lo que Python establece deterministamente: cada hecho listado arriba, más su confianza/estado
(`confirmed`/`inferred`/`unresolved`). Lo que la IA puede interpretar (solo cuando se pasa
`--allow-ai-interpretation`): reformular/explicar esa evidencia ya establecida, citando únicamente ids de
referencia de evidencia que la propia ejecución actual produjo — nunca añadiendo una nueva relación o hecho
(§4.7, §13).

## §12 Sistema de documentación

`legacy_documenter/exporters/markdown_exporter.py` (`MarkdownExporter`) renderiza los seis documentos
originales de nombre fijo (`PROJECT_OVERVIEW.md`, `SOLUTION_STRUCTURE.md`, `PROJECT_DEPENDENCIES.md`,
`WEBFORMS_MAP.md`, `CONFIGURATION_SUMMARY.md`, `ANALYSIS_WARNINGS.md`).

`legacy_documenter/exporters/technical_documentation_renderer.py` (`TechnicalDocumentationRenderer`)
renderiza los cuatro documentos añadidos en V4.2 (`WEB_ENTRY_POINTS.md`, `FUNCTIONAL_FLOWS.md`,
`DATABASE_ACCESS.md`, `UNRESOLVED_FINDINGS.md`). V4.2-R8 añadió, para los tres últimos, un método
`*_navigation()` (renderiza el resumen pequeño de nombre fijo) y un método `*_partitions()` (renderiza la
misma evidencia dividida por grupo semántico en `documentation/<doc>/<nombre-seguro>.md`, usando
`_documentation_partitioning.py::sanitize_label` para nombres seguros para el sistema de archivos y a
prueba de path traversal, con desambiguación determinista por sufijo numérico para etiquetas en colisión).
Los métodos planos originales `*()` no cambian y siguen probándose directamente. Los archivos de partición
obsoletos de los grupos ya inexistentes de una ejecución previa no se arrastran: el renderizado particionado
siempre refleja únicamente los grupos de la ejecución actual.

`cli/pipeline_stages.py::render_documentation` escribe `documentation/README.md` (un índice de navegación
fijo que enlaza a cada documento) y aplica la política de "un mal renderizador no debe destruir a los
demás": el fallo de cada renderizador se registra en `DocumentationOutcome.failures`, no se lanza, de modo
que un documento roto nunca impide que se escriban los demás; `cli/full_pipeline.py::_run_documentation_stage`
inspecciona ese resultado en lugar de depender de la propagación de excepciones.

Los archivos desconocidos/creados por el usuario dentro de `documentation/` se preservan entre
reejecuciones — solo se sobrescriben los nombres de archivo fijos y los archivos de partición que el
renderizador posee (§4.10).

**Medición de mantenibilidad (esta ronda).** La `maintainability_debt` de `PROJECT_STATE.json` señala a
`technical_documentation_renderer.py` como un `HIGH_RISK_FUTURE_EXTRACTION_CANDIDATE`, citando una baseline
histórica de cierre de V4.2-R8 de ~802 líneas con la clase `TechnicalDocumentationRenderer` en sí ~462
líneas. Esta ronda midió el archivo directamente: **actualmente tiene 802 líneas** (`wc -l`), coincidiendo
exactamente con la cifra histórica — sin desviación desde el cierre de V4.2-R8. Sigue siendo el módulo de
producción individual más grande del repositorio (ver §22) y la clasificación de deuda permanece sin
cambios; ver §20 para el registro completo de la deuda.

## §13 Arquitectura de IA

**Lo que existe hoy:**

- Un contrato neutral al proveedor (`legacy_documenter/llm/core.py`): `LLMRequest`/`LLMResponse`/
  `LLMCapabilities`/`ProviderConfig`/`Usage`/`ProviderError`, y una base abstracta `LLMProvider`
  (`generate`, `capabilities`, `model_info`).
- `FakeLLMProvider` — un proveedor determinista, consciente de sus capacidades, en memoria, usado en toda
  la suite de tests y por `tools/manual_verify_full_pipeline.py`; nunca realiza E/S.
- `ProviderRegistry.create(config)` — **actualmente solo reconoce `provider_type in {"FAKE", "COPILOT"}`**;
  pasar cualquier otro `provider_type` lanza `ValueError("unknown provider")`.
- `CopilotProvider` (`llm/providers/copilot.py`) — la única integración concreta con un proveedor real
  realmente alcanzable a través del registro, sobre un cliente local de GitHub Copilot, asíncrona por
  debajo (`asyncio.run`).
- `GeminiProvider` (`llm/providers/gemini.py`) — existe una segunda implementación concreta de proveedor en
  el árbol de fuentes (lee `GEMINI_API_KEY` vía `credential_source`, publica a un transporte HTTP) pero
  **`ProviderRegistry.create` no enruta `"GEMINI"` hacia ella** — es inalcanzable desde la ruta de
  producción de `_resolve_provider()` y no es ejercitada por los tests de ruta de registro de la suite. Esta
  es una discrepancia entre la fuente y la completitud que vale la pena señalar al Líder Técnico (ver el
  documento de resultado).
- Construcción de contexto: `context/resolver.py` (`ContextResolver`, de solo lectura) +
  `context/composer.py` (`ContextComposer`, aplica un presupuesto de tokens/registros
  `TINY`/`SMALL`/`MEDIUM`/`LARGE`/`FULL`) — la misma maquinaria del lado de lectura que usan tanto la ruta
  `documentation/generator.py` de la era V3 como la ruta `orchestration/ai_interpretation.py` de V4.2.
- Interpretación: `orchestration/ai_interpretation.py::run_ai_interpretation` — el único punto de entrada de
  IA que `full` realmente invoca. Construye un paquete de contexto exclusivamente a partir del propio
  `output/ai_context/*.json` de la ejecución actual, envía una solicitud de salida estructurada bajo una
  instrucción de sistema restrictiva, y valida la forma de la respuesta/el cierre de referencias de
  evidencia antes de devolver jamás un resultado de "SUCCESS".
- Generación de propuestas: `orchestration/proposal_adapter.py::adapt_findings_to_proposals` convierte
  hallazgos validados en registros `knowledge/proposals/models.py::Proposal`.
- Seguridad ante proveedor real: el código de producción (`_resolve_provider`) solo se alcanza cuando no se
  inyecta ningún `provider`; cada test y el script dedicado `tools/manual_verify_full_pipeline.py` inyectan
  `FakeLLMProvider` explícitamente. `tests/__init__.py` además protege contra que cualquier ruta de test
  alcance accidentalmente la resolución de un proveedor real (`AGENTS.md`).

**Acoplamiento/limitaciones actuales:**

- `ai_interpretation.py` no acepta un `ProviderConfig` suministrado por el invocador — la selección de
  proveedor/modelo en producción está enteramente impulsada por variables de entorno
  (`LEGACYMAPPER_LLM_PROVIDER`, `LEGACYMAPPER_LLM_PROVIDER_ID`, `LEGACYMAPPER_LLM_MODEL`), con `COPILOT`
  como valor por defecto codificado de forma fija.
- Existe exactamente un *propósito* de IA conectado de extremo a extremo (`ARCHITECTURE_INTERPRETATION`,
  codificado de forma fija en `run_ai_interpretation`), aunque `llm/core.py::PURPOSES` define siete.
- `documentation/generator.py` (la ruta de la era V3) construye un `CopilotProvider` directamente en lugar
  de pasar por la costura de `ai_interpretation.py` — dos sitios de invocación independientes alcanzan un
  proveedor real bajo condiciones distintas; un desarrollador debe revisar ambos al razonar sobre "¿puede
  esto alguna vez llamar a un proveedor de IA real?".

**Requisito de V5 (no implementado hoy):** verdadera agnosticidad de IA/proveedor/modelo — un contrato/
puerto núcleo estable a través del cual cualquier backend de IA en tiempo de ejecución sea intercambiable,
con el detalle de transporte/autenticación/modelo/reintento específico del proveedor mantenido enteramente
fuera de la lógica de dominio núcleo. El ABC `LLMProvider` de `llm/core.py` es una semilla razonable para
esto, pero el `if`/`elif` codificado de forma fija de dos proveedores de `ProviderRegistry` y la
configuración de propósito único y solo por variable de entorno de `ai_interpretation.py` todavía no lo son.
"Python descubre; la IA interpreta" debe preservarse sin cambios por cualquier trabajo de agnosticidad de
proveedor de V5.

## §14 Arquitectura de conocimiento

Pipeline conceptual completo modelado por `legacy_documenter/knowledge/`:

```
material de entrada (knowledge/input/) -> ingesta (knowledge/ingestion/) -> procedencia (knowledge/provenance/)
  -> clasificación (knowledge/classification/) + separación temporal (knowledge/temporal/)
  -> relaciones (knowledge/relations/) -> propuestas (knowledge/proposals/)
  -> aprobación del Líder Técnico (knowledge/approval/) -> conocimiento canónico (knowledge/canonical/)
  -> proyecciones: legible por humanos (knowledge/projection/, R11) / de cara al Plugin (knowledge/plugin_projection/, R12)
```

Cada etapa anterior modela como dominio un contrato real y probado. Lo que **no** es cierto hoy: ningún
comando de la CLI orquesta este pipeline de extremo a extremo. La única etapa realmente conectada a `full`
es `proposals/` (vía `orchestration/proposal_adapter.py`) — todo desde `approval/` en adelante existe como
código de biblioteca implementado y probado unitariamente sin invocador en la orquestación de producción.

Contratos clave:

- **`CanonicalKnowledgeEntry`** (`knowledge/canonical/models.py`) — entrada inmutable, neutral a la fuente;
  `knowledge_id` es determinista (nunca derivado de tiempo/UUID/identidad de objeto); requiere un
  `proposal_id` y un `approval_decision_id` no vacíos (ambos permanentes, nunca borrados); reutiliza
  `KnowledgeStatement.validate()` (R1) en lugar de reimplementar sus reglas de autoridad de evidencia.
- **Identificadores KNO** — `CanonicalKnowledgeEntry.knowledge_id` es el concepto más cercano a un
  identificador "KNO" en la fuente actual; es producido por una función determinista de derivación de id
  (`new_knowledge_id`, referenciada desde `canonical/service.py`), no un esquema separado con prefijo
  "KNO-" distinto de `knowledge_id` — trate "identificador KNO" y "`knowledge_id`" como la misma cosa en
  esta base de código.
- **"Una sola fuente canónica"** — la Fuente de Conocimiento Canónico de R10 se modela explícitamente como
  la única fuente de verdad para el conocimiento aprobado; el `PluginCanonicalSourceDescriptor` de
  `plugin_projection` declara, estructuralmente, que su carga útil es una *proyección de* esa fuente, nunca
  una segunda fuente de verdad (`SOURCE_KIND = "CANONICAL_KNOWLEDGE_SOURCE"`, nunca nombrado
  `truth`/`source_of_truth`).
- **Proyección humana de R11** (`knowledge/projection/`) — `DocumentProjection`/`ProjectionManifest`,
  renderizados a Markdown por `projection/markdown_renderer.py`; solo capa de proyección, nunca muta los
  datos canónicos.
- **`LegacyMapperPluginKnowledge` de R12** (`knowledge/plugin_projection/models.py`) — `CONTRACT_NAME =
  "LegacyMapperPluginKnowledge"`, `CONTRACT_VERSION = "1.0"`; `PluginKnowledgeEntry.knowledge_id` siempre es
  igual al `knowledge_id` de la `CanonicalKnowledgeEntry` fuente — no se acuña una segunda identidad.
- **Runtime de Plugin** — **no existe**. `plugin_projection/` produce una *forma* de carga útil; nada en el
  repositorio la consume en tiempo de ejecución. `PROJECT_STATE.json: plugin_runtime = "NOT_IMPLEMENTED"`.

## §15 Contratos y modelos de datos

| Nombre | Módulo | Propósito | Campos clave | Productor | Consumidor | Notas de estabilidad |
|---|---|---|---|---|---|---|
| `RunResult` / `StageResult` / `RunStatus` / `StageStatus` | `cli/execution_model.py` | Resultado de ejecución/etapa de la CLI | `command`, `status`, `stages`, `ai_invoked`, `canonical_knowledge_produced`, `technical_lead_approval`, `ai_requested`, `proposal_count`, `proposal_review_status`, `next_action`, `output_locations` | `cli/full_pipeline.py`, `cli/router.py` | `run_summary_presenter.py`, tests, salida de consola de la CLI | Estable, solo aditivo desde V4.2-R2; cada campo de V4.2-R5 tiene un valor por defecto seguro para que los invocadores antiguos no vean cambio de comportamiento |
| `StageId` | `cli/stage_identity.py` | Vocabulario de etapas de pipeline con nombre | 13 valores de enum | — | `full_pipeline.py`, lectores de `RUN_SUMMARY.json` | Estable; siempre se emite un vocabulario completo (`NOT_RUN` en lugar de omisión) |
| `LLMRequest` / `LLMResponse` / `LLMCapabilities` / `ProviderConfig` / `Usage` / `ProviderError` | `llm/core.py` | Contrato de IA neutral al proveedor | Ver §13 | `orchestration/ai_interpretation.py`, `documentation/generator.py` | `llm/providers/*` | Interno/pre-V5; aún no es el "puerto" público estable que V5 debe diseñar |
| `Proposal` / `ProposalStatus` / `ProposalKind` / `ProposalMethod` | `knowledge/proposals/models.py` | Ciclo de vida de propuesta pre-aprobación | `proposal_id`, `statement`, `rationale`, `evidence_refs`, `status` | `orchestration/proposal_adapter.py` | `full_pipeline.py::_write_proposal_output` | Estable; toda propuesta de V4.2 es `READY_FOR_REVIEW` |
| `CanonicalKnowledgeEntry` | `knowledge/canonical/models.py` | Entrada inmutable de conocimiento aprobado | `knowledge_id`, `statement`, `source_type`, `nature`, `status`, `proposal_id`, `approval_decision_id`, `evidence_refs`, `provenance` | `knowledge/canonical/service.py` | `knowledge/projection/`, `knowledge/plugin_projection/` | Contrato estable, aún no alcanzable desde ningún flujo orquestado |
| `KnowledgeStatement` / `EvidenceRef` / `Provenance` | `knowledge/domain/models.py` | Modelo de dominio fundacional de R1 | — | En todas partes bajo `knowledge/` | `canonical/models.py` (reutilizado, no reimplementado) | Fundacional; cambiarlo es un cambio que rompe entre paquetes |
| Carga útil de `LegacyMapperPluginKnowledge` (`PluginKnowledgeEntry`/`PluginKnowledgeManifest`/`PluginCanonicalSourceDescriptor`/`PluginKnowledgePayload`) | `knowledge/plugin_projection/models.py` | Proyección versionada legible por máquina para un Plugin externo | `CONTRACT_NAME="LegacyMapperPluginKnowledge"`, `CONTRACT_VERSION="1.0"` | `knowledge/plugin_projection/service.py` | Ningún consumidor actual (no hay runtime de Plugin) | Constante explícita de versión de contrato; un cambio disruptivo requiere incrementar `CONTRACT_VERSION` |
| `SourceFile` / `Project` / `Symbol` / `Call` / `WebForm` / `EntryPoint` / `Dependency` / `Evidence` | `models/*.py` | Registros de dominio entre módulos | Dataclasses pequeñas, una por archivo | `extractors/`, `scanner/` | `analysis/`, `exporters/`, `context/` | Estable; ampliamente dependido, bajo riesgo de cambio |

## §16 Arquitectura de tests

62 módulos de test bajo `tests/`, basados en `unittest`, descubribles vía
`python -m unittest discover -s tests`. Organizados cronológicamente por la ronda que los introdujo, lo que
también los agrupa por responsabilidad:

| Grupo | Archivos (prefijo) | Cubre |
|---|---|---|
| Línea base V1 | `test_v1*` | Comportamiento original de scanner/extractor/exportador, preservado como protección de regresión |
| Rondas V3 | `test_v3_r1` .. `test_v3_r10_1` | Contexto/compositor, generación/agregación/consistencia de documentación, parseo de revisión humana, la puerta de preparación R9, el inventario de mantenibilidad R10 |
| Rondas de conocimiento V4 | `test_v4_r1_knowledge_domain_model` .. `test_v4_r14_manuals_and_final_baseline` | Un módulo de test por ronda de subpaquete de conocimiento (R1 modelo de dominio hasta R14 baseline final), más `test_v4_r13_regression_and_security` |
| Rondas V4.1 | `test_v4_1_r0_maintainability_inventory` .. `test_v4_1_r7_exception_boundaries_characterization` | Inventario de mantenibilidad, regresión del renderizador JSON, caracterización de modelo/tipo/contrato público, caracterización y cierre de brechas de readiness/extractor de base de datos/resolvedor de flujo, caracterización de límites de excepción |
| Rondas V4.2 | `test_v4_2_r1_cli_contract_and_execution_model` .. `test_v4_2_r8_documentation_at_scale` | Contrato de la CLI, orquestador de pipeline completo, documentación técnica, interpretación por IA/propuestas, códigos de salida/protección de proveedor real, CLI/UX unificada, robustez/recuperación/seguridad/diseño de superficie de aprobación, corrección de hallazgos del piloto real, fixture sintético de pipeline completo, documentación a escala/baseline final |
| Arnés compartido | `tests/__init__.py`, `tests/conftest.py`, `tests/fixtures/` | Protección contra llamadas a proveedor real (falla ruidosamente si alguna ruta de test alcanza la resolución de un proveedor real), fixtures compartidos, repositorios de muestra sintéticos |

Grupos notables por tipo: **tests de caracterización** (`*_characterization.py`) fijan el comportamiento
existente antes de refactorizaciones, en lugar de afirmar una especificación desde cero; **tests de
compatibilidad** afirman que la forma posicional desnuda legada y el punto de entrada de módulo de
`readiness` permanecen sin cambios; **tests de protección de seguridad/llamada a proveedor** afirman cero
llamadas reales de red/proveedor y ninguna filtración de secretos; **fixtures sintéticos**
(`tests/fixtures/v4_2_r7_full_sample/`, ejercitados por `test_v4_2_r7_synthetic_full_fixture.py`)
reproducen los hallazgos clave del piloto real de IST de V4.2-R7 (F-01, F-07) de forma determinista sin
ningún dato real de IST; **tests de integridad de baseline/manifiesto**
(`test_v4_2_r8_documentation_at_scale.py::FinalBaselineAndManifestIntegrityTests`) verifican que
`output/v4_2_r8/V4_2_FINAL_BASELINE.json`/`V4_2_FINAL_MANIFEST.json` coincidan por hash con los archivos
que afirman describir.

**Registro histórico (cierre de V4.2)**: la baseline de cierre de V4.2 registró
`"tests": "1809_PASS_0_FAIL_0_SKIP"` en `PROJECT_STATE.json` y `output/v4_2_r8/V4_2_FINAL_BASELINE.json` —
1809 tests, 0 fallos, 0 omisiones, en cualquiera que fuera el entorno local que produjo ese resultado de
cierre.

**Primera ejecución sobre un checkout nuevo observada por esta ronda de documentación**
(`python -m unittest discover -s tests`, sin ningún test modificado antes de esta ejecución):

```
Ran 1625 tests in 66.575s
FAILED (failures=2, errors=19)
```

Esto fue materialmente distinto de la cifra histórica de 1809. Una ronda de corrección Post-V4.2 posterior
(`docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION_RESULT.md`) diagnosticó y resolvió tanto la
brecha de conteo como 20 de los 21 tests no exitosos, y una ronda de reconciliación adicional corrigió el
último. El diagnóstico, preservado aquí para el registro histórico:

- 19 de los 21 tests no exitosos, más `readiness.py` mismo, dependían de
  `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`, el cual `git log --all` mostró que **nunca fue un archivo
  rastreado** en ese momento — excluido por `.gitignore` (`/output/v3_r8_1/`, clasificado como un "artefacto
  pesado regenerable") y presente solo en cualquiera que fuera el entorno local que produjo por última vez
  la baseline de 1809 exitosos. En un clon nuevo, `readiness()` lanzaba `FileNotFoundError` para esa ruta, y
  cada test que invocaba `readiness()` (directamente, vía el punto de entrada de módulo de la CLI, o vía una
  afirmación de regresión "readiness sigue en verde") fallaba de forma idéntica.
- `test_v4_2_r5_1_exit_code_contract_and_real_provider_guard.py::test_all_four_externally_observable_exit_codes`
  también invocaba la ruta de la CLI `readiness` y fallaba por la misma causa raíz.
- `test_v4_2_r8_documentation_at_scale.py::FinalBaselineAndManifestIntegrityTests::test_manifest_hashes_match_referenced_files`
  fallaba porque `V4_2_FINAL_MANIFEST.json` registraba un hash para un archivo bajo `output/v3_r8_1/` que
  estaba ausente por la misma razón.
- La brecha de conteo de 1625 contra 1809 tenía una causa separada, estructural, no relacionada con ningún
  archivo faltante: cuando un `setUpClass` lanza una excepción, `unittest` reporta exactamente **una entrada
  sintética `ERROR: setUpClass (...)` para toda la clase** y nunca cuenta sus métodos de test individuales en
  `testsRun`. Seis clases se vieron afectadas por esto (`test_v3_r7_2.CoveragePlannerTests` (20 métodos),
  `test_v3_r7_2_4.TestV3R724`, `test_v3_r8_2.R82Tests` (18), `test_v3_r8_2_correction.CorrectionTests` (20),
  `test_v3_r9.KnowledgeReadinessTests` (45), y
  `test_v4_1_r4_readiness_characterization.RepresentativeResultTests` (6)), colapsando 184 métodos de test
  reales en 6 entradas contadas. **No se eliminó ningún test y no se debilitó ninguna aserción** — esto fue
  puramente la propia contabilidad de `unittest` ante fallos de `setUpClass`.

**Corrección aplicada**: (1) `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` (~1.8 KiB) es ahora una excepción
de `.gitignore` deliberadamente rastreada y estrecha — evidencia agregada pequeña de indicador estructural,
proveniente del ya rastreado `codex/v3/V3_R8_1_DEEP_SOURCE_ANALYSIS_RESULTADO.md`, no un volcado crudo
restaurado; el resto de `output/v3_r8_1/` permanece excluido. (2) Cuatro clases de test históricas cuyos
tests originales requieren los volcados completos e irreconstruibles de repositorio real
(`output/v2_r5_1_full/`, el resto de `output/v3_r8_1/`) ahora llevan protecciones
`@unittest.skipUnless(...)`, de modo que un clon nuevo reporta un `SKIP` explícito y razonado por método en
lugar de un único `ERROR` de `setUpClass` no controlado — esto es lo que permite que `unittest` vuelva a
contar los 184 métodos individuales. (3) El fallo de hash de manifiesto restante se identificó, en ese
momento, como causado por el test de verificación comparando el *árbol de trabajo en vivo* contra una
instantánea histórica congelada mientras una edición legítima y todavía no confirmada de documentación
Post-V4.2 estaba en curso sobre la misma ruta; el propio contrato de dos colecciones del manifiesto
(`authoritative_artifacts` frente a `mutable_current_state_documents`) ya era correcto, así que el test se
acotó, en esa corrección intermedia, para comparar `authoritative_artifacts` contra su último contenido
confirmado en HEAD (`git show HEAD:<ruta>`) cuando el árbol de trabajo difería de HEAD, y contra el disco en
otro caso. Esa solución intermedia resultó ser ella misma frágil: dependía de si el árbol de trabajo estaba
sucio o limpio, y de qué contenido tuviera HEAD *en ese momento* — en cuanto las ediciones pendientes de los
manuales Post-V4.2 se confirmaran (commit), HEAD pasaría a contener el contenido *nuevo*, el árbol quedaría
limpio, y el test compararía ese contenido nuevo contra el hash histórico del manifiesto, fallando de forma
inmediata en el commit siguiente. Ver
`docs/V4_2/POST_V4_2_DOCUMENTATION_AND_HISTORICAL_MANIFEST_RECONCILIATION_RESULT.md` para el registro
completo de esa corrección intermedia.

**Corrección definitiva de estabilidad post-commit**: una ronda posterior
(`docs/V4_2/POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_CORRECTION_RESULT.md`) reemplazó la
comparación basada en HEAD por una comparación anclada al commit histórico fijo de cierre de V4.2,
`af7e2099039e791c5a14ff94bf5ad348e8dbb4db` (leído desde la sección `## GIT_COMMIT` de
`docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md`, nunca codificado como literal en el test, y
verificado como alcanzable con `git cat-file -e <commit>^{commit}`). Para cada entrada de
`authoritative_artifacts`, el test ahora obtiene `git show af7e2099...:<ruta>` y acepta la coincidencia si
ese blob, o su contraparte CRLF/LF, coincide por hash con el `sha256` registrado en el manifiesto — nunca
lee HEAD ni el árbol de trabajo actual para la comparación de hash; una verificación de existencia
`path.is_file()` contra el árbol de trabajo actual se mantiene aparte, como una comprobación básica de
sanidad del repositorio actual, claramente separada de la comparación de contenido. Esta solución final no
depende de HEAD ni de si el árbol de trabajo está sucio o limpio, y está protegida por un nuevo test de
regresión aislado, `test_historical_manifest_integrity_survives_a_later_commit`, que construye un
repositorio Git temporal desechable, confirma un primer commit como "contenido histórico", registra su
hash, luego confirma un segundo commit posterior con contenido distinto en la misma ruta, y verifica que la
comprobación anclada al primer commit sigue validando el contenido histórico tanto con el árbol limpio como
con una edición adicional sin confirmar encima — mientras una comparación directa contra el contenido de
HEAD se demuestra que falla, probando que el test no es accidentalmente vacío. Este nuevo test es el que
elevó el conteo de tests descubiertos de 1809 a 1810 (ver más abajo).

**Estado actual, final, para un clon nuevo**: 1810 tests descubiertos; 0 fallos; 0 errores; 132 omisiones
cuando las cuatro familias de fixture dependientes de repositorio real están ausentes (el caso normal de
clon nuevo) — cada omisión lleva una razón explícita y legible por humanos que nombra el fixture faltante.
Para evitar confundir tres cifras legítimamente distintas registradas en la historia de este proyecto:

- **HISTÓRICO V4.2** (baseline de cierre formal): `"1809_PASS_0_FAIL_0_SKIP"` — 1809 tests, 0 fallos, 0
  omisiones, en el entorno local que produjo ese resultado de cierre. Esta cifra nunca se reescribe; es
  evidencia histórica congelada.
- **CORRECCIÓN INTERMEDIA POST-V4.2** (tras la corrección de reproducibilidad en clon nuevo, antes de la
  corrección de estabilidad post-commit): 1809 tests descubiertos, 132 omisiones — la misma cifra de 1809
  que el histórico, pero por una razón distinta (un clon nuevo puro, sin el test de estabilidad post-commit
  todavía añadido).
- **ESTADO ACTUAL FINAL** (tras la corrección de estabilidad post-commit y la aprobación final Post-V4.2):
  1810 tests descubiertos, 0 fallos, 0 errores, 132 omisiones esperadas.

Ningún método de test fue eliminado y ninguna aserción fue debilitada en ningún punto de esta secuencia de
correcciones; cada cambio de cifra está explicado y es trazable a un documento de resultado específico.

## §17 Herramientas

| Herramienta | Propósito | ¿Muta estado? | Salida | Relación con el cierre |
|---|---|---|---|---|
| `tools/manual_verify_full_pipeline.py` | Verificación manual segura de `full`, incluyendo `--allow-ai-interpretation`, siempre inyectando `FakeLLMProvider` | Escribe en el directorio `--output` que suministra el invocador | Misma forma que una ejecución real de `full` | La alternativa segura obligatoria a invocar `python main.py full ... --allow-ai-interpretation` directamente (`AGENTS.md`) |
| `tools/v4_2_r8_build_final_artifacts.py` | Construye `output/v4_2_r8/V4_2_FINAL_BASELINE.json`/`V4_2_FINAL_MANIFEST.json` de forma determinista a partir de rutas/hashes relativos al repositorio actual | Escribe solo esos dos archivos; lee, nunca modifica, código de producción | Baseline/manifiesto candidatos (aún se requiere revisión del Líder Técnico antes del cierre formal) | Produjo directamente los artefactos que esta ronda midió en §12/§16 |
| `tools/v4_1_r10_build_artifacts.py`, `v4_1_r7_build_artifact.py`, `v4_1_r8_build_artifact.py`, `v4_1_r9_build_artifact.py` | Constructores históricos de artefactos de resultado de ronda de V4.1 | Escriben en el directorio `output/v4_1_r*/` de su propia ronda | JSON específico de ronda | Histórico; no reejecutado en un ciclo de desarrollo normal |
| `tools/v4_1_r0/generate.py`, `inventory.py`, `report.py` | Herramientas históricas de inventario de mantenibilidad de V4.1-R0 | Escribe `output/v4_1_r0/*` | JSON de auditoría de mantenibilidad | Predecesor de `legacy_documenter/quality/maintainability_audit.py`, que §22 de este manual usa directamente |

Ninguna de estas herramientas es importada por `legacy_documenter/`; son scripts independientes ejecutados
directamente con `python -m tools.<nombre>` o `python tools/<nombre>.py`.

## §18 Continuidad / Traspaso de agente

Secuencia de arranque que un nuevo desarrollador o agente de desarrollo de IA sigue realmente (según
`CLAUDE.md`):

1. `AGENTS.md` — autonomía, límite de permisos, reglas del proyecto, control de fases.
2. `PROJECT_STATE.json` — el único puntero autoritativo a la versión/ronda/estatus/riesgos conocidos/deuda
   actuales; sustituye a cualquier lista de rondas desactualizada en la propia memoria de `AGENTS.md`.
3. `docs/V4/V4_AI_HANDOVER.md` — narrativa de traspaso activa.
4. `output/v3_final/V3_FINAL_BASELINE.json` — la baseline canónica de V3.
5. El prompt activo bajo `prompts/V4*/` para lo que sea que `next` nombre en `PROJECT_STATE.json`.

Si el repositorio "no compila mentalmente" (un checkout nuevo sin memoria de sesión), `CLAUDE.md` nombra
`docs/PROJECT_RECOVERY.md` como la ruta de recuperación. La propia memoria de conversación de un agente de
desarrollo nunca es autoritativa — el repositorio, específicamente `PROJECT_STATE.json`, sí lo es
(`AGENTS.md`: "Current progression is not duplicated here, to avoid it going stale").

**Comenzando el desarrollo desde un clon nuevo**, concretamente:

1. Leer `PROJECT_STATE.json` para determinar `current_version_status`/`next`.
2. Leer las §6–§9 de este Manual Técnico para la forma del repositorio/módulos/ejecución.
3. Ejecutar `python -m unittest discover -s tests` y comparar el resultado contra §16 — esperar 1810
   descubiertos, 0 fallos, 0 errores, 132 omisiones (todas explicadas), ya que la brecha de
   `ARCHITECTURE_EVIDENCE.json` en clon nuevo fue corregida y el test de estabilidad post-commit
   (`test_historical_manifest_integrity_survives_a_later_commit`) ya está incorporado; un fixture de
   repositorio completo colocado localmente reduce el conteo de omisiones, nunca el total descubierto.
4. Leer el documento activo nombrado por el campo `next` de `PROJECT_STATE.json` antes de comenzar cualquier
   ronda nueva — nunca inferir la siguiente ronda de este manual ni de la memoria.

## §19 Política de artefactos generados

Texto autoritativo completo: `docs/GENERATED_ARTIFACT_POLICY.md`. Resumen, verificado contra el
`.gitignore` actual:

- **Artefactos pequeños canónicos — versionados.** Cualquier cosa referenciada por ruta/hash desde una
  baseline, registro de cierre o resultado de ronda (por ejemplo `output/v3_final/V3_FINAL_BASELINE.json`,
  `output/v4_2_r8/*`, `output/LEVANTAMIENTO_FUNCIONAL.md`) permanece rastreada sin importar que sea
  generada.
- **Artefactos pesados regenerables — no versionados.** Los volcados de escaneo de repositorio completo
  (`output/v1_r1_full/`, `output/v2_r4_full/`, ..., `output/v2_r5_1_full/`, `output/v3_r8_1/`) están
  excluidos por `.gitignore` mediante ruta explícita; regenerables vía
  `python main.py "<repo_legado>" --output "<destino>" --verbose` contra un repositorio legado real.
  **Excepción estrecha y deliberada**: `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` (~1.8 KiB) está rastreado
  a pesar de vivir bajo un directorio por lo demás excluido, mediante una excepción de `.gitignore`
  (`/output/v3_r8_1/*` más `!/output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`). Contiene solo evidencia agregada
  pequeña de indicador estructural (cuatro conteos de `DETERMINISTIC_INDICATORS` y una conclusión de
  arquitectura), proveniente textualmente del ya rastreado y aprobado por humanos
  `codex/v3/V3_R8_1_DEEP_SOURCE_ANALYSIS_RESULTADO.md` — no un escaneo crudo restaurado y no regenerable de
  forma independiente solo a partir del repositorio, ya que sus valores originales dependieron de un escaneo
  legado real. El resto de `output/v3_r8_1/` (y la totalidad de `output/v2_r5_1_full/`) permanece
  completamente excluido; ningún otro volcado de escaneo completo histórico debe rastrearse bajo este
  precedente (§16, §20).
- **Salida operacional de sistema real** — la salida del análisis de un sistema legado real concreto debe
  permanecer local, nunca confirmada, sin importar el tamaño (`output/v4_2_r7_ist_operacional/`,
  explícitamente excluido). Convención para nuevas ejecuciones: `output/_local_<nombre>/` (ya cubierta por
  una regla genérica de `.gitignore`) o, si se necesita un directorio con nombre formal, añadir la regla
  explícita correspondiente de `.gitignore` en el mismo cambio.
- **Artefactos pesados no regenerables** — actualmente ninguno existe; si aparece uno, debe clasificarse y
  elegirse un mecanismo de almacenamiento (archivo externo / GitHub Release / Git LFS / almacenamiento
  seguro) antes de que `output/` pueda considerarse seguro dejar tal cual.
- **Por qué `output/` no puede ignorarse globalmente**: contiene contratos/baselines/manifiestos rastreados
  junto con ruido generado local; una exclusión general descartaría en silencio historia autoritativa.
- **Seguro de eliminar localmente**: cualquier cosa bajo las listas de "pesado regenerable" y "sobrante de
  smoke-test" en `.gitignore`/el documento de política. **Debe permanecer rastreado**: todo lo demás bajo
  `output/`, todo `docs/`, `prompts/`, `codex/`, `result_codex/`, y obviamente todo `legacy_documenter/`/`tests/`.

## §20 Deuda técnica conocida

| ID | Área | Estado actual | Archivo(s) afectado(s) | Impacto | Por qué permanece | Versión futura sugerida | Riesgo si se modifica | Tests/evidencia relacionados |
|---|---|---|---|---|---|---|---|---|
| F-05 | `RUN_SUMMARY.json` carece de un campo de duración/marca de tiempo de ejecución | `DEFERRED_BY_DETERMINISM_CONTRACT` | `cli/run_summary_presenter.py` | No se puede distinguir la duración en reloj de pared de dos ejecuciones solo a partir del resumen | Añadir contenido de reloj de pared/UUID rompería el invariante de determinismo existente (`test_run_summary_json_is_identical_across_two_runs`); ningún documento de R1–R6 exime a `RUN_SUMMARY.json` de él | Una versión que redefina explícitamente el determinismo para excluir un campo declarado de "telemetría de ejecución" | Rompe en silencio un test de regresión existente si se añade sin un cambio de contrato | `docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md` §"SECTION 9"; `test_v4_2_r2_deterministic_full_pipeline_orchestrator.py::DeterminismTests` |
| F-06 | Ruido de código repetitivo del diseñador `InitializeComponent()` en `UNRESOLVED_FINDINGS.md` | `PRESERVED_OBSERVATION` (no un defecto) | `exporters/technical_documentation_renderer.py`, `analysis/flow_resolver.py` | Ruido cosmético para un lector humano de hallazgos no resueltos | Deliberadamente no filtrado — filtrar código repetitivo del diseñador arriesga ocultar en silencio un caso genuino no resuelto que resulte parecerse | Podría añadirse una clasificación explícita y evidenciada de "generado por el diseñador" en lugar de filtrar por patrón de nombre | Cualquier filtro heurístico arriesga un falso negativo (ocultar un límite no resuelto real) | `tests/test_v4_2_r7_synthetic_full_fixture.py::GeneratedDocumentationTests` |
| F-07 | `WebEntryResolver` nunca adjunta `outgoing_calls` a un punto de entrada vinculado desde el marcado | `PRESERVED_OBSERVATION` (no un defecto) | `analysis/web_entry_resolver.py` | Los flujos funcionales que comienzan desde un manejador vinculado desde el marcado subreportan sus propias llamadas salientes | Corregirlo requiere un cambio de comportamiento del resolvedor con su propio riesgo de regresión, deliberadamente fuera del alcance de una ronda de corrección de hallazgos | Una ronda que extienda `WebEntryResolver` para resolver llamadas salientes vinculadas desde el marcado, con nuevos tests de caracterización primero | Podría cambiar los resultados de `status`/"terminal confirmado" del flujo para repositorios reales | `tests/test_v4_2_r7_synthetic_full_fixture.py::FunctionalFlowTests::test_markup_bound_handler_reproduces_the_known_outgoing_calls_gap` |
| DEBT-DOC-01 | `WEB_ENTRY_POINTS.md` sigue siendo un documento plano único (sin particionado de V4.2-R8) | `OPEN_IF_FUTURE_SCALE_REQUIRES` | `exporters/technical_documentation_renderer.py::web_entry_points` | Podría volverse inmanejable a una escala similar a la que disparó la división de flujo/base de datos/hallazgos no resueltos de R8 | No evidenciado como problema a la escala del piloto de V4.2-R7; particionarlo preventivamente se juzgó trabajo innecesario | Aplicar el mismo patrón de navegación/partición si una futura ejecución real muestra que es necesario | Bajo si se deja tal cual; refactorización moderada si se añade sin reutilizar `_documentation_partitioning.py` | `PROJECT_STATE.json: documentation_remaining_scale_debt` |
| DEBT-DOC-02 | `PROJECT_DEPENDENCIES.md` sigue siendo un documento plano único | `OPEN_IF_FUTURE_SCALE_REQUIRES` | `exporters/markdown_exporter.py::project_dependencies` | Igual que arriba | Igual que arriba | Igual que arriba | Igual que arriba | `PROJECT_STATE.json: documentation_remaining_scale_debt` |
| MAINT-01 | Mantenibilidad de `technical_documentation_renderer.py` | `HIGH_RISK_FUTURE_EXTRACTION_CANDIDATE` | `exporters/technical_documentation_renderer.py` (802 líneas; `TechnicalDocumentationRenderer` ~462 líneas) | Módulo de producción más grande; mezcla cuatro renderizadores de documento distintos más sus variantes de navegación/partición en una clase | Extraer renderizadores por documento ahora arriesga romper la simetría de renderizado plano/particionado (§12) sin tests de caracterización acotados a la división | Una ronda de extracción dedicada con tests de caracterización que fijen primero la igualdad de salida plana frente a particionada | Alto — los cuatro renderizadores actualmente garantizan un renderizado de evidencia idéntico entre la salida plana y la particionada vía ayudantes privados compartidos; una división descuidada podría hacerlos divergir en silencio | `PROJECT_STATE.json: maintainability_debt`; §12 arriba (conteo de líneas remedido esta ronda, sin cambios en 802) |
| TESTINFRA-01 | Brecha de `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` en checkout nuevo | `RESOLVED` respecto a la reproducibilidad en clon nuevo, con endurecimiento residual separado y aún abierto (ver columna "Por qué permanece") | `knowledge/readiness.py::_execute`, `.gitignore`, `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` (ahora rastreado), `test_v3_r9`, `test_v3_r10*`, `test_v4_1_r1..r4`, `test_v4_2_r1/r2/r5_1` | Era: `python main.py readiness` y ~1.2% de la suite de tests fallaba en un clon nuevo. Ahora: readiness es `READY`, código de salida 0, en un clon nuevo. | El archivo de evidencia pequeño, no sensible e históricamente auténtico es ahora una excepción de `.gitignore` deliberadamente rastreada (§19); `readiness.py` en sí no fue modificado. Endurecimiento residual, distinto y todavía no implementado: si ese archivo ya rastreado se elimina o corrompe manualmente, `readiness.py` puede aún lanzar una excepción no controlada en lugar de degradar a un `BLOCKED` controlado — esto no es "una dependencia de un archivo actualmente no rastreado" (eso ya está resuelto); es un caso de manejo defensivo ante daño posterior al archivo ya rastreado | `docs/V4_2/POST_V4_2_FRESH_CLONE_REPRODUCIBILITY_CORRECTION_RESULT.md`; suite completa: 1810 descubiertos, 0 errores tras todas las correcciones Post-V4.2 |
| BASELINE-01 | `V4_2_FINAL_MANIFEST.json` referenciaba un hash para un archivo ausente en un clon nuevo / el test de verificación comparaba el árbol de trabajo en vivo (o HEAD) contra evidencia histórica congelada | `RESOLVED` de forma definitiva, mediante la corrección de estabilidad post-commit del manifiesto histórico Post-V4.2 | `tests/test_v4_2_r8_documentation_at_scale.py::FinalBaselineAndManifestIntegrityTests::test_manifest_hashes_match_referenced_files`, `test_historical_manifest_integrity_survives_a_later_commit` | Era: fallaba en un clon nuevo (brecha de ARCHITECTURE_EVIDENCE.json); una primera corrección intermedia comparó contra HEAD condicionada a si el árbol de trabajo estaba sucio o limpio, lo cual habría vuelto a fallar en cuanto las ediciones pendientes de los manuales se confirmaran (commit); la solución definitiva ancla la verificación al commit histórico fijo de cierre de V4.2. Ahora: pasa de forma estable independientemente de HEAD/commits posteriores. | Causa raíz 1 resuelta por TESTINFRA-01. Causa raíz 2, resuelta definitivamente: el propio contrato `authoritative_artifacts` frente a `mutable_current_state_documents` del manifiesto ya era correcto y no fue modificado; el test ahora compara `authoritative_artifacts` contra el contenido del commit histórico fijo de cierre de V4.2 (`af7e2099039e791c5a14ff94bf5ad348e8dbb4db`, leído desde `docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md`, aceptando las representaciones LF/CRLF históricas), nunca contra HEAD ni contra el árbol de trabajo, de modo que ni una edición legítima en curso ni un commit posterior legítimo pueden volver a producir una falsa lectura de corrupción de evidencia histórica; protegido por `test_historical_manifest_integrity_survives_a_later_commit` | No se cambió ningún hash de manifiesto, ningún archivo de manifiesto/baseline, ni ningún código de producción | `docs/V4_2/POST_V4_2_DOCUMENTATION_AND_HISTORICAL_MANIFEST_RECONCILIATION_RESULT.md` (corrección intermedia, superada); `docs/V4_2/POST_V4_2_HISTORICAL_MANIFEST_POST_COMMIT_STABILITY_CORRECTION_RESULT.md` (solución definitiva); `tests/test_v4_2_r8_documentation_at_scale.py` |
| AI-01 | `GeminiProvider` implementado pero inalcanzable vía `ProviderRegistry` | **Documentado por primera vez esta ronda** — `OPEN` | `llm/providers/gemini.py`, `llm/core.py::ProviderRegistry.create` | Existe un segundo proveedor concreto en el árbol de fuentes sin forma de seleccionarlo en producción | No evidenciado como diferido intencionalmente en ningún lugar encontrado en `docs/`/`PROJECT_STATE.json`; parece ser conexión incompleta más que una exclusión deliberada | Conectar `"GEMINI"` a `ProviderRegistry.create` con cobertura de tests, o documentarlo explícitamente como andamiaje para una ronda futura | Bajo añadirlo (rama `elif` aditiva); no debería hacerse sin tests específicos del proveedor y la protección de test de "sin llamada a proveedor real" extendida para cubrirlo | `llm/core.py::ProviderRegistry.create`; ausencia de los fixtures relacionados con la protección en `tests/__init__.py` |
| R6-01 | Intermitencia de `test_deterministic_run_then_ai_enabled_rerun_same_output` | `NON_REPRODUCIBLE_AS_OF_V4.2_FORMAL_CLOSURE` | Test observado bajo `test_v4_2_r6_robustness_recovery_security_and_approval_surface.py` | No recurrió a través de R7, R7.1, R8, ni de las ejecuciones de regresión del cierre final | Causa raíz no identificada; el cierre trata la no recurrencia como aceptable pero no como prueba de ausencia | V5 debe tratar cualquier recurrencia como disparador de investigación, no descartarla | Ignorar una recurrencia erosionaría la confianza en el contrato de determinismo en general | `PROJECT_STATE.json: known_risks.r6_intermittent_test` |
| APPR-01 | Implementación de superficie de aprobación | `NOT_IMPLEMENTED` (solo diseño, `docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md`) | Ningún archivo de implementación — solo documento de diseño | No existe ninguna ruta de CLI desde una propuesta hasta una decisión de aprobación | Explícitamente fuera del alcance de V4.2; aprobado como `APPROVED_DESIGN_ONLY` | Una ronda acotada a implementar la superficie de CLI de aprobación contra el modelo de dominio `knowledge/approval/` existente | Implementar un comando de aprobación real es una capacidad nueva significativa que requiere su propia revisión de seguridad/auditoría | `PROJECT_STATE.json: approval_surface_implementation` |
| PLUGIN-01 | Runtime de Plugin | `NOT_IMPLEMENTED` | Ningún archivo de implementación | Ningún sistema externo puede actualmente consumir cargas útiles `LegacyMapperPluginKnowledge` en tiempo de ejecución | Explícitamente fuera del alcance de V4.2 | Una ronda/versión dedicada de runtime de Plugin, consumiendo el contrato ya versionado de R12 | Nueva superficie de ataque (un consumidor externo); necesita su propia revisión de seguridad | `PROJECT_STATE.json: plugin_runtime` |

## §21 Mapa de auditoría de código

Orden de auditoría sugerido, agrupado por capa arquitectónica:

1. **Límite de CLI/orquestación** — `cli/parser.py`, `router.py`, `execution_model.py`, `stage_identity.py`,
   `pipeline_stages.py`, `full_pipeline.py`, `run_summary_presenter.py`, `artifact_lifecycle.py`.
   Preocupación de complejidad: `full_pipeline.py` (490 líneas) es el segundo módulo más grande del
   repositorio y el más central estructuralmente — conecta diez etapas deterministas más dos etapas de IA
   opcionales más la finalización del resumen. Preguntas de auditoría: ¿`run_full_pipeline` hace solo
   orquestación, o se ha filtrado lógica de dominio (por ejemplo `_assemble_indexes`) junto a la secuenciación
   pura? ¿El patrón try/except por etapa (`_run_stage`) se aplica de forma uniforme, o alguna etapa lo
   evita en silencio? Deuda conocida: ninguna más allá del tamaño.
2. **Extracción determinista** — `scanner/`, `extractors/`. Preocupación de complejidad:
   `database_extractor.py` (358 líneas) más tres ayudantes privados `_database_*` es el extractor más
   descompuesto, lo que sugiere que los otros (`call_extractor.py`, 245 líneas; monolítico, aún no dividido
   en ayudantes privados) podrían beneficiarse del mismo tratamiento. Preguntas de auditoría: ¿`call_extractor.py`
   mezcla responsabilidades de escaneo de línea, parseo de tokens y clasificación de la forma en que
   `database_extractor.py` solía hacerlo antes de su división `_database_*`? ¿El parseo determinista está
   adecuadamente aislado de cualquier inferencia de la capa de análisis?
3. **Análisis/resolución determinista** — `analysis/`. Preocupación de complejidad: `flow_resolver.py`
   (312 líneas) más tres ayudantes `_flow_*` es el componente más grande y algorítmico en términos de
   grafos; `web_entry_resolver.py` lleva la brecha conocida F-07. Preguntas de auditoría: ¿La agregación de
   estado de flujo en el peor caso (§11) está documentada con suficiente claridad a nivel de código, no solo
   en el Manual de Usuario? ¿Podría cerrarse la brecha de `outgoing_calls` vinculados desde el marcado de
   `web_entry_resolver.py` (F-07) con una extensión acotada y bien probada, o requiere un rediseño más
   amplio del resolvedor?
4. **Renderizado de documentación** — `exporters/`. Preocupación de complejidad:
   `technical_documentation_renderer.py` (802 líneas, señalado `HIGH_RISK_FUTURE_EXTRACTION_CANDIDATE`, §20
   MAINT-01). Preguntas de auditoría: ¿Podría extraerse cada trío plano+navegación+partición de los cuatro
   documentos a su propio módulo sin romper la garantía de ayudante compartido de que los renderizados plano
   y particionado nunca diverjan? ¿El tamaño de 802 líneas en sí mismo es evidencia de "responsabilidad
   demasiado amplia", o son cuatro renderizadores cohesivos e individualmente pequeños que simplemente viven
   en un archivo?
5. **Costura de contexto/IA** — `context/`, `llm/`, `orchestration/`. Preocupación de complejidad: dos
   sitios de invocación independientes a proveedor real (`documentation/generator.py` y
   `orchestration/ai_interpretation.py`), y un `GeminiProvider` inalcanzable (AI-01). Preguntas de
   auditoría: ¿La lógica específica del proveedor (el cliente asíncrono de Copilot, el transporte HTTP de
   Gemini) se filtra de alguna forma hacia el contrato supuestamente neutral de `llm/core.py`? ¿Debería
   `ProviderRegistry` ser el único punto de entrada de producción para *cada* sitio de invocación a proveedor
   real, retirando la construcción directa de `CopilotProvider` de `documentation/generator.py`?
6. **Dominio de conocimiento** — `knowledge/domain/`, `input/`, `ingestion/`, `provenance/`,
   `classification/`, `temporal/`, `relations/`, `proposals/`, `approval/`, `canonical/`, `projection/`,
   `plugin_projection/`. Preocupación de complejidad: no el tamaño (la mayoría de los archivos están bien
   por debajo de 300 líneas) sino la *brecha de orquestación* — muchos contratos bien probados sin invocador
   de producción. Preguntas de auditoría: ¿La suite de tests de cada subpaquete es una caracterización
   genuina de su contrato, o solo ejercita el camino feliz? ¿Conectar estos en una superficie de CLI de
   aprobación real (APPR-01) revelaría algún desajuste de contrato latente entre subpaquetes adyacentes (por
   ejemplo `proposals/` → `approval/` → `canonical/`) que los tests unitarios aislados pasarían por alto?
7. **Herramientas de readiness/cierre** — `knowledge/readiness.py` + `_readiness_*.py`,
   `knowledge/closure/`, `quality/maintainability_audit.py`, `tools/`. Preocupación de complejidad:
   TESTINFRA-01/BASELINE-01 (§20) están ambas `RESOLVED`; el endurecimiento residual que queda no es una
   dependencia de archivo no rastreado (eso ya está resuelto), sino que `readiness.py` sigue sin degradar de
   forma controlada a `BLOCKED` si el archivo `ARCHITECTURE_EVIDENCE.json`, ya rastreado, llegara a
   eliminarse o corromperse manualmente. Preguntas de auditoría: ¿Debería hacerse explícita la verificación
   de evidencia de arquitectura de `readiness.py` sobre su no reproducibilidad, o reestructurarse para
   manejar de forma controlada la ausencia/corrupción de ese archivo? ¿La función grande única de `_execute`
   (legible pero haciendo ocho verificaciones distintas en línea) es un caso para descomposición adicional
   dado que la división `_readiness_*` ya ocurrió una vez (V4.1-R4)?
8. **Gobernanza/continuidad** — `AGENTS.md`, `CLAUDE.md`, `PROJECT_STATE.json`, `.gitignore`,
   `docs/GENERATED_ARTIFACT_POLICY.md`. Preguntas de auditoría: ¿Cada ítem de deuda actualmente
   `OPEN`/`DEFERRED` en `PROJECT_STATE.json` tiene una entrada correspondiente en §20 de este manual
   (verificación cruzada en ambas direcciones)? ¿`PROJECT_STATE.json` en sí es internamente consistente con
   los artefactos a los que apunta (esta ronda encontró un lugar donde no lo era — TESTINFRA-01/BASELINE-01)?

## §22 Inventario de mantenibilidad

Calculado esta ronda vía `legacy_documenter.quality.maintainability_audit.audit('.')` (determinista, solo
AST, no importa código en tiempo de ejecución):

- **Archivos `.py` de producción**: 169 (bajo `legacy_documenter/`, excluyendo `__pycache__`).
- **Clases**: 181. **Funciones/métodos**: 705. **Símbolos totales**: 886; **símbolos significativos**
  (públicos, o privados pero de >20 líneas): 636.
- **Cobertura de tipado** (parámetros y retorno totalmente anotados): 80.14% de todas las
  funciones/métodos; 77.8% de las funciones/métodos significativas.
- **Cobertura de docstring**: 76.52% de todos los símbolos; 93.87% de los símbolos significativos.
- **Candidatos a módulo grande** (>250 líneas): 10 módulos.
- **Candidatos a múltiples responsabilidades** (≥4 de las señales léxicas `json`/`write_text`/`read_text`/
  `validate`/`render`/`provider`/`security` presentes): 28 módulos.

**Módulos de producción más grandes por conteo de líneas** (top 15, medición de esta ronda):

| Líneas | Módulo |
|---|---|
| 802 | `legacy_documenter/exporters/technical_documentation_renderer.py` |
| 490 | `legacy_documenter/cli/full_pipeline.py` |
| 421 | `legacy_documenter/cli/pipeline_stages.py` |
| 358 | `legacy_documenter/extractors/database_extractor.py` |
| 344 | `legacy_documenter/knowledge/canonical/example_report.py` |
| 312 | `legacy_documenter/analysis/flow_resolver.py` |
| 287 | `legacy_documenter/knowledge/canonical/service.py` |
| 263 | `legacy_documenter/documentation/consistency.py` |
| 260 | `legacy_documenter/knowledge/approval/example_report.py` |
| 254 | `legacy_documenter/knowledge/proposals/service.py` |
| 250 | `legacy_documenter/knowledge/plugin_projection/example_report.py` |
| 245 | `legacy_documenter/extractors/call_extractor.py` |
| 239 | `legacy_documenter/knowledge/domain/models.py` |
| 234 | `legacy_documenter/cli/run_summary_presenter.py` |
| 233 | `legacy_documenter/knowledge/relations/service.py` |

Note que tres de los diez "candidatos a módulo grande" son archivos `*_example_report.py` (generadores de
ejemplo de contrato, no lógica en tiempo de ejecución) — un lector que audite por complejidad genuina
debería ponderar la parte superior de esta lista (`technical_documentation_renderer.py`, `full_pipeline.py`,
`pipeline_stages.py`, `database_extractor.py`, `flow_resolver.py`) con más peso que los archivos
`example_report.py`/`contract_report.py`, que son extensos por diseño (existen para documentar un contrato
con ejemplos trabajados).

Archivos ya identificados por rondas previas como riesgosos/diferidos (verificación cruzada contra §20):
solo `technical_documentation_renderer.py` lleva una señal explícita de deuda de mantenibilidad en
`PROJECT_STATE.json`; los demás módulos grandes arriba (`full_pipeline.py`, `pipeline_stages.py`,
`database_extractor.py`, `flow_resolver.py`) son grandes pero no están actualmente señalados como deuda por
ningún documento rastreado — un Líder Técnico que audite el *próximo* candidato de extracción después de
`technical_documentation_renderer.py` comenzaría ahí.

No se introduce aquí ninguna puntuación de calidad arbitraria; la propia herramienta documenta su propia
limitación: "El conteo de líneas es una señal de inventario, no un veredicto de calidad" y "Los candidatos
de responsabilidad son indicios léxicos para revisión humana"
(`legacy_documenter/quality/maintainability_audit.py::audit`, campo `limitations`).

## §23 Traspaso a V5

**Lo que V4.2 ya provee:**

- Un pipeline de análisis determinista, funcional y probado para .NET Framework/VB.NET/ASP.NET Web
  Forms/Oracle, con seguimiento explícito de evidencia `confirmed`/`inferred`/`unresolved` en todo momento.
- Un orquestador resiliente y modelado por etapas (`RunResult`/`StageResult`/`StageId`) que ya generaliza
  bien más allá de los *nombres* de etapa de esta pila tecnológica específica — el propio patrón de
  contención de fallo parcial es neutral a la tecnología.
- Un contrato de solicitud/respuesta de IA neutral al proveedor (`llm/core.py`) y una costura de producción
  (`orchestration/ai_interpretation.py`) que ya aplica "la IA reformula, nunca inventa" — un punto de
  partida real para, aunque todavía no una instancia de, la agnosticidad de proveedor.
- Un pipeline de conocimiento completamente modelado (aunque aún no orquestado) desde la ingesta hasta la
  composición canónica hasta la proyección tanto legible por humanos como legible por máquina (de cara al
  Plugin).
- Una herramienta determinista de inventario de mantenibilidad (`quality/maintainability_audit.py`)
  reutilizable, sin modificación, para cualquier versión futura de esta herramienta basada en Python.

**Lo que V5 debe diseñar:**

- **Agnosticidad de lenguaje** — `extractors/`/`analysis/` son hoy enteramente específicos de
  VB.NET/WebForms; V5 necesita una abstracción de descubrimiento que no sea simplemente "los mismos módulos
  con más ramas `if language ==`".
- **Agnosticidad de framework** — los conceptos de ASP.NET Web Forms (`WebForm`, code-behind, vinculaciones
  de eventos de UI) están incrustados en `models/webform.py`, `extractors/webforms_extractor.py`,
  `analysis/web_entry_resolver.py`.
- **Agnosticidad de base de datos** — la clasificación SQL/procedimiento almacenado de
  `extractors/database_extractor.py` tiene sabor a Oracle; un modelo generalizado de acceso a datos es
  trabajo de V5.
- **Agnosticidad de disposición de proyecto** — el descubrimiento `.sln`/`.vbproj`
  (`extractors/solution_extractor.py`, `vbproj_extractor.py`) asume una disposición de solución/proyecto de
  Visual Studio.
- **Agnosticidad de IA/proveedor/modelo en tiempo de ejecución** — promover el ABC `LLMProvider` de
  `llm/core.py` a un puerto núcleo realmente estable y versionado; retirar los dos sitios de invocación a
  proveedor real independientes (la construcción directa de `CopilotProvider` de
  `documentation/generator.py` y `_resolve_provider` de `orchestration/ai_interpretation.py`) en uno solo;
  decidir el destino de `GeminiProvider` (conectarlo o eliminarlo) en lugar de dejarlo inalcanzable (AI-01).
- Preservar "Python descubre; la IA interpreta" como un invariante a través de todo lo anterior — la
  agnosticidad no debe convertirse en "la IA infiere lo que Python solía descubrir deterministamente".
- La agnosticidad de IA en tiempo de ejecución y la neutralidad de agente de desarrollo son **relacionadas
  pero distintas**: la primera trata de qué backend de IA puede invocar `orchestration/ai_interpretation.py`
  (o su sucesor en V5) en tiempo de ejecución para el análisis de un usuario; la segunda (ya parcialmente
  abordada — `CLAUDE.md`/`AGENTS.md` están escritos para ser neutrales al agente) trata de qué asistente de
  codificación de IA puede desarrollar LegacyMapper mismo. No confunda una decisión de diseño de V5 sobre
  una con la otra.

**Deuda que puede resolverse en V5:**

- MAINT-01 (extracción de `technical_documentation_renderer.py`) — una capa de renderizado agnóstica a
  lenguaje/framework probablemente requiera esta división de todos modos.
- AI-01 (conexión de `GeminiProvider`) — resuelta naturalmente por un puerto realmente agnóstico al
  proveedor.
- DEBT-DOC-01/02 (documentos planos restantes) — probablemente revisitados junto con cualquier rediseño de
  la capa de renderizado.

**Lo que puede diferirse a V5.1/V5.2:**

- APPR-01 (implementación de superficie de aprobación) y PLUGIN-01 (runtime de Plugin) no requieren que la
  agnosticidad se resuelva primero; cualquiera podría implementarse contra los contratos de conocimiento
  *actuales* de V4.2 como un incremento V5.x, o incorporarse en el propio V5 — este manual no decide esa
  cuestión de calendario.
- TESTINFRA-01 y BASELINE-01 ya están `RESOLVED` y no son deuda pendiente para V5. Lo único que queda es el
  endurecimiento residual, no relacionado con V5, de TESTINFRA-01: `readiness.py` podría, en cualquier
  momento e independientemente de cualquier trabajo de V5, reestructurarse para degradar de forma
  controlada a `BLOCKED` si el ya rastreado `ARCHITECTURE_EVIDENCE.json` se eliminara o corrompiera
  manualmente, en lugar de lanzar una excepción no controlada.

Este manual no diseña la arquitectura de V5 — entrega exactamente el límite que V5 debe cruzar, fundamentado
en la fuente actual, para que el Líder Técnico y el siguiente agente de desarrollo planifiquen a partir de
él.
