# LegacyMapper — Glosario (V4.2)

Las definiciones reflejan la semántica real de LegacyMapper tal como está implementada en la fuente actual
(`legacy_documenter/`), no definiciones de diccionario genéricas. Referencia cruzada: Manual de Usuario,
Manual Técnico.

**LegacyMapper** — Este proyecto: una herramienta que analiza deterministamente un repositorio legado .NET
Framework/VB.NET/ASP.NET Web Forms/Oracle y produce documentación técnica, con un paso opcional, explícito y
restringido de interpretación por IA. Ver Manual de Usuario §4.1.

**Descubrimiento determinista** — Análisis realizado enteramente por código Python (escaneo, parseo,
resolución) que nunca invoca a un proveedor de IA/LLM y siempre produce la misma salida para la misma
entrada. Todo bajo `legacy_documenter/scanner/`, `extractors/`, `analysis/` es descubrimiento determinista.

**Interpretación por IA** — El paso opcional (`--allow-ai-interpretation`) en el que se le pide a un
proveedor que reformule o explique evidencia determinista que la ejecución actual ya descubrió. Nunca se le
permite inventar una relación o un hecho; cada hallazgo debe citar ids de referencia de evidencia ya
presentes en el propio paquete de contexto de la ejecución actual
(`legacy_documenter/orchestration/ai_interpretation.py`).

**Evidencia** — Un hecho discreto y trazable descubierto deterministamente (un símbolo, una llamada, un
registro de acceso a datos, un punto de entrada resuelto). Modelado por
`legacy_documenter/models/evidence.py` y referenciado por id (`EvidenceRef`,
`legacy_documenter/knowledge/domain/models.py`) en toda la capa de conocimiento.

**Contexto** — Un paquete compuesto y limitado por presupuesto de registros de evidencia construido para un
propósito específico (`legacy_documenter/context/resolver.py::ContextResolver`,
`composer.py::ContextComposer`). Distinto del directorio de nivel superior en tiempo de ejecución
`context/`, que es donde `ContextBuilder` escribe su salida en tiempo de ejecución — mismo nombre, dos cosas
distintas (ver Manual Técnico §6).

**Fuente (Source)** — En el modelo de conocimiento de V4, un valor de `SourceType`
(`legacy_documenter/knowledge/domain/enums.py`) que clasifica de dónde se originó una pieza de material
(por ejemplo, código, documento redactado por un humano). En el uso de la CLI, "repositorio fuente"/
"repositorio" se refiere a la base de código objetivo que se está analizando.

**Procedencia (Provenance)** — Un registro explícito y acíclico de de dónde vino una pieza de
material/evidencia/afirmación (`legacy_documenter/knowledge/provenance/`: `ProvenanceGraph`,
`ProvenanceNode`). Responde "de dónde vino esto", nunca "es esto verdadero".

**Propuesta (Proposal)** — Un registro de pre-aprobación que afirma "dado este material/evidencia/relación/
contexto, esta es una acción o conclusión propuesta" (`legacy_documenter/knowledge/proposals/models.py::Proposal`).
Toda propuesta que LegacyMapper produce tiene `status = READY_FOR_REVIEW` (escrita como
`PENDING_TECHNICAL_LEAD_REVIEW` en el sobre de salida del pipeline `full`) — nunca aprobada automáticamente,
nunca canónica.

**Líder Técnico (Technical Lead)** — El rol humano con la única autoridad para aprobar, rechazar o solicitar
corrección de una propuesta (`legacy_documenter/knowledge/approval/models.py::ApprovalDecision`). No existe
ningún comando de CLI en V4.2 a través del cual un Líder Técnico ejerza este rol — el diseño existe
(`docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md`), la implementación no
(`IMPLEMENTATION_STATUS=NOT_IMPLEMENTED`).

**Aprobación (Approval)** — Una `ApprovalDecision` explícita (`APPROVED` / `REJECTED` /
`CORRECTION_REQUESTED`) que un Líder Técnico toma sobre una `Proposal` específica. No implementada como un
comando de CLI ejecutable en V4.2.

**Conocimiento canónico (Canonical knowledge)** — La colección única, inmutable y neutral a la fuente de
entradas de conocimiento aprobadas (la "Fuente de Conocimiento Canónico"). Compuesta solo a partir de un par
`Proposal` aprobada + `ApprovalDecision(APPROVED)` (`legacy_documenter/knowledge/canonical/service.py`).
`RunResult.canonical_knowledge_produced` es `false` en toda ejecución de V4.2, sin excepción — ninguna
ejecución produce conocimiento canónico hoy.

**CanonicalKnowledgeEntry** — La dataclass inmutable que representa una entrada de conocimiento canónico
(`legacy_documenter/knowledge/canonical/models.py`). Requiere un `proposal_id` y un `approval_decision_id`
permanentes; reutiliza las reglas estructurales/de evidencia de `KnowledgeStatement.validate()` en lugar de
reimplementarlas.

**KNO / `knowledge_id`** — El identificador determinista de una `CanonicalKnowledgeEntry` (campo
`knowledge_id`). Derivado únicamente de contenido semántico inmutable — nunca de tiempo de reloj de pared,
aleatoriedad, un UUID, o identidad de objeto. "Identificador KNO" en la jerga abreviada del proyecto se
refiere a este mismo campo; no existe un esquema de identidad separado con prefijo "KNO-" en la fuente
actual.

**R11** — La ronda, a partir de V4-R10, que produjo la capa de proyección legible por humanos
(`legacy_documenter/knowledge/projection/`): renderiza una `CanonicalKnowledgeCollection` a Markdown
determinista (`DocumentProjection`, `ProjectionManifest`). Solo capa de proyección; nunca muta los datos
canónicos.

**R12 / `LegacyMapperPluginKnowledge`** — El contrato de proyección versionado y legible por máquina para un
consumidor de Plugin externo (`legacy_documenter/knowledge/plugin_projection/models.py`):
`CONTRACT_NAME = "LegacyMapperPluginKnowledge"`, `CONTRACT_VERSION = "1.0"`. El `knowledge_id` de un
`PluginKnowledgeEntry` siempre es igual al `knowledge_id` de su `CanonicalKnowledgeEntry` fuente — no se
acuña una segunda identidad.

**Runtime de Plugin (Plugin runtime)** — Un sistema externo hipotético que consumiría una carga útil
`LegacyMapperPluginKnowledge` en tiempo de ejecución. **No existe** en V4.2
(`PROJECT_STATE.json: plugin_runtime = NOT_IMPLEMENTED`). El paquete R12 produce solo la *forma* de la
carga útil; nada la consume.

**RunResult** — El resultado de una invocación de comando de la CLI
(`legacy_documenter/cli/execution_model.py`): nombre del comando, `RunStatus` global, una tupla ordenada de
`StageResult`s, y los campos de límite de aprobación/UX (`ai_invoked`, `canonical_knowledge_produced`,
`technical_lead_approval`, `ai_requested`, `proposal_count`, `proposal_review_status`, `next_action`,
`output_locations`).

**StageResult** — El resultado de una etapa con nombre dentro de una ejecución: un `StageId`, un
`StageStatus`, y un `StageError` opcional (`legacy_documenter/cli/execution_model.py`).

**RunStatus** — Resultado general de la ejecución: `SUCCESS`, `PARTIAL`, o `FAILED`. Calculado de forma no
subjetiva por `legacy_documenter/cli/full_pipeline.py::_compute_status` — ver **SUCCESS**/**PARTIAL**/
**FAILED** abajo.

**StageStatus** — Resultado por etapa: `SUCCESS`, `FAILED`, `SKIPPED_DUE_TO_UPSTREAM_FAILURE`, o `NOT_RUN`
(este último reservado para una etapa que nunca fue solicitada, por ejemplo `AI_INTERPRETATION` sin
`--allow-ai-interpretation`).

**SUCCESS** (código de salida `0`) — `analyze` siempre sale con `0`. Para `full`/`readiness`, toda etapa
aplicable tuvo éxito sin ningún error de extracción por archivo.

**PARTIAL** (código de salida `1`) — `full`/`readiness` se completó con al menos un resultado mínimamente
útil (`EXTRACTION` y `EXPORT` tuvieron éxito ambos, para `full`) pero alguna etapa falló, se omitió debido a
un fallo ascendente, o se registró un error de extracción por archivo.

**FAILED** (código de salida `4`) — `full` no produjo ni siquiera un paquete de análisis determinista
mínimamente útil (`EXTRACTION` o `EXPORT` no tuvo éxito).

**USAGE** (código de salida `2`) — Un error de uso a nivel de argparse (comando desconocido, argumento
requerido faltante), nunca asignado por código de aplicación.

**READY** — El resultado de `python main.py readiness` (o `readiness.py::run()`) cuando cada una de sus
ocho verificaciones internas (`preconditions`, `claim_integrity`, `evidence_closure`,
`quantitative_integrity`, `architecture_integrity`, `knowledge_projection`, `knowledge_boundary`,
`security`) pasa. Lo opuesto es `BLOCKED`. Esta es una autoverificación de la propia documentación/evidencia
aprobada de la era V3 de LegacyMapper, no una señal de preparación por repositorio objetivo.

**`ARCHITECTURE_EVIDENCE.json`** (`output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`) — Una excepción de
`.gitignore` pequeña (~1.8 KiB) y estrechamente rastreada, consumida por
`readiness.py::architecture_valid()` como parte de la verificación `architecture_integrity`. Contiene solo
cuatro conteos agregados estructurales de `DETERMINISTIC_INDICATORS` (sin código fuente, rutas de archivo
fuente, credenciales, ni datos personalmente identificables), provenientes textualmente del ya rastreado y
aprobado por humanos `codex/v3/V3_R8_1_DEEP_SOURCE_ANALYSIS_RESULTADO.md`. Es **evidencia de contrato**, no
un volcado de escaneo crudo restaurado — el resto de `output/v3_r8_1/` permanece excluido — y no puede
regenerarse solo a partir del repositorio, ya que sus valores originales dependieron de un escaneo real de
un repositorio legado.

**Artefacto histórico de cierre frente a documento mutable de estado actual** — Una distinción que el
manifiesto de V4.2 (`output/v4_2_r8/V4_2_FINAL_MANIFEST.json`) hace explícitamente mediante dos colecciones
separadas: `authoritative_artifacts` (evidencia ya producida y ya revisada para el estado candidato/de
cierre de V4.2; sus hashes registrados son requisitos de integridad) y `mutable_current_state_documents`
(documentos sobre los cuales la propia nota del manifiesto dice que "cambian intencionalmente a medida que
el proyecto avanza"; sus hashes registrados son solo una instantánea en el tiempo, no un requisito de
integridad). Los hashes de `authoritative_artifacts` se verifican contra el contenido de esos archivos tal
como existía en el **commit histórico fijo de cierre de V4.2**
(`af7e2099039e791c5a14ff94bf5ad348e8dbb4db`, registrado en
`docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md`) — nunca contra HEAD ni contra el último commit
actual del archivo, y nunca contra el árbol de trabajo. Un archivo referenciado como artefacto autoritativo
aún puede recibir ediciones nuevas legítimas después del cierre, incluso confirmadas (commit) — el hash del
manifiesto histórico describe lo que era cierto en ese commit de cierre fijo, no una promesa de que la ruta
en vivo nunca pueda volver a tocarse ni un reflejo de lo que HEAD contenga en cualquier momento posterior.

**CODE_ONLY / CODE_AND_HUMAN_INFORMATION / HUMAN_INFORMATION_ONLY / PARTIAL_INFORMATION** — Categorías de
tipo de fuente/composición de información usadas en las capas de preparación de conocimiento y
documentación de la era V3 (`legacy_documenter/documentation/`, `knowledge/readiness.py`) para describir si
una afirmación se apoya únicamente en evidencia de código determinista, únicamente en información
suministrada por humanos, en una combinación, o en una mezcla incompleta. Distintas de, y anteriores a, los
enums `SourceType`/`KnowledgeNature` de V4.

**AS_IS / TO_BE / HISTORICAL / GAP** — Los cuatro bloques temporales de `legacy_documenter/knowledge/temporal/`
(V4-R6): `AS_IS` (estado actual confirmado), `TO_BE` (un estado futuro/objetivo declarado), `HISTORICAL` (un
estado pasado ya no vigente), `GAP` (una diferencia/ausencia identificada entre bloques). Asignados a
material ya ingerido; nunca inferidos más allá de lo que el material declara.

**Límite no resuelto (Unresolved boundary)** — Un punto en el análisis donde la evidencia determinista no
cierra hacia una conclusión confirmada (por ejemplo, una llamada que no puede resolverse a un símbolo
declarado, un flujo que no puede alcanzar un terminal confirmado). Siempre preservado explícitamente, nunca
descartado en silencio ni promovido a `confirmed` (`UNRESOLVED_FINDINGS.md`; registros `flow_unresolved`;
`AGENTS.md` "Project Rules").

**Terminal confirmado (Confirmed terminal)** — En la resolución de flujo funcional
(`legacy_documenter/analysis/flow_resolver.py`), una ruta de ejecución trazada que alcanza una operación de
base de datos/procedimiento almacenado con evidencia `confirmed`. Un flujo puede tener un terminal
confirmado en una ruta mientras su `Status` general todavía se lee como `unresolved_boundary` debido a una
ruta distinta y no relacionada que quedó sin resolver — ambos hechos se registran de forma independiente
(Manual de Usuario §4.8).

**Salida operacional (Operational output)** — El resultado generado por ejecutar LegacyMapper contra un
sistema legado real concreto (un piloto, un compromiso con un cliente). Debe permanecer local, nunca
confirmarse (commit), sin importar el tamaño (`docs/GENERATED_ARTIFACT_POLICY.md`, "Real-System Operational
Output").

**Artefacto rastreado (Tracked artifact)** — Un archivo generado, pequeño y significativo, que un documento
de baseline/cierre/resultado de ronda referencia por ruta o hash, y que por lo tanto permanece versionado en
Git a pesar de ser generado (por ejemplo, `output/v4_2_r8/V4_2_FINAL_BASELINE.json`).

**Fixture sintético (Synthetic fixture)** — Un repositorio o conjunto de datos de muestra confirmable
(commit), construido a mano (o derivado de un piloto pero anonimizado) usado por los tests para reproducir
un hallazgo del mundo real de forma determinista sin ningún dato real/sensible
(`tests/fixtures/v4_2_r7_full_sample/`, reproduciendo los hallazgos F-01/F-07 del piloto de V4.2-R7).

**Baseline (línea base)** — Una instantánea congelada, en un punto en el tiempo, del estado del repositorio
(conteos de tests, hashes, lista de capacidades) registrada en un hito de cierre (por ejemplo,
`output/v4_2_r8/V4_2_FINAL_BASELINE.json`). No se espera que coincida byte a byte con una ejecución en vivo
posterior una vez que el repositorio ha avanzado legítimamente — ver el Manual Técnico §16 para un caso
concreto donde una ejecución sobre un clon nuevo y la baseline registrada divergen.

**Manifiesto (Manifest)** — Un archivo complementario a una baseline que registra rutas de archivo y hashes
de contenido, usado para verificar que los artefactos referenciados por la baseline sean idénticos byte a
byte a lo que el cierre registró (`output/v4_2_r8/V4_2_FINAL_MANIFEST.json`).

**Continuidad neutral al agente (Agent-neutral continuity)** — La propiedad de que `AGENTS.md`/`CLAUDE.md`/
`PROJECT_STATE.json` están escritos de modo que cualquier agente de desarrollo de IA capaz (no solo un
producto específico) pueda retomar el proyecto correctamente leyendo el propio repositorio, nunca la
memoria de sesión de un agente específico (`AGENTS.md`: "the active development agent," "any capable
development agent").

**Proveedor (proveedor de IA / LLM provider)** — Una implementación concreta de
`legacy_documenter/llm/core.py::LLMProvider` (por ejemplo, `FakeLLMProvider`, `CopilotProvider`).
`ProviderRegistry.create` actualmente solo conecta `"FAKE"` y `"COPILOT"` — ver Manual Técnico §13,
discrepancia AI-01.

**FakeLLMProvider** — Una implementación determinista, en memoria, consciente de sus capacidades, de
`LLMProvider`, usada en toda la suite de tests y por `tools/manual_verify_full_pipeline.py` para que ningún
test ni verificación manual alcance jamás una llamada real de red/proveedor.

**Hallazgos (Findings)** — La lista de afirmaciones que un paso de interpretación por IA devuelve, cada una
con una `confidence` (`CONFIRMED`/`UNCERTAIN`) y `evidence_refs`. No confiables, no aprobados, no canónicos
a menos que (y hasta que) un Líder Técnico apruebe posteriormente una `Proposal` construida a partir de
ellos.
