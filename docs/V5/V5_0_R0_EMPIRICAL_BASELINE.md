# V5.0 R0 — Baseline empírico y preparación de arquitectura

## STATUS

`V5_0_R0_READY_FOR_ARCHITECTURE`

Ronda diagnóstica/documental. No se modificó código productivo, tests, prompts, packaging, baselines cerrados ni `PROJECT_STATE.json`. Único archivo creado en el repo: este documento.

## SCOPE

Medir y documentar V4.3 (cerrada) antes de diseñar V5. Fuentes: código bajo `legacy_documenter/`, docs de resultado V4.3, y el output real ya existente `C:\PruebasLegacyMapper\Resultados\v4_3_ai_rerun_r3a_r1_retry1` (lectura). No se ejecutó un full IST adicional (no aporta evidencia nueva). Fuera de alcance: implementar cualquier cosa de V5.1+.

## CURRENT ARCHITECTURE

Entrypoint: `main.py` → `legacy_documenter/main.py:main` → `cli/router.py`. Subcomandos: `analyze`, `full`, `readiness`, `output-manifest`. Exit codes: SUCCESS 0, PARTIAL 1, USAGE 2, FAILED 4.

Tamaño: 176 archivos `.py` en `legacy_documenter/` (~20.2k líneas), 74 en `tests/`.

| Paquete | Archivos | Líneas | Rol |
|---|---|---|---|
| `scanner` | 3 | 93 | escaneo/clasificación por extensión |
| `extractors` | 12 | 1184 | `.vb`, `.vbproj`, `.sln`, `.aspx/.ascx`, `web.config`, eventos, DB |
| `analysis` | 12 | 1379 | resolución de calls, entry points web, DB, flows, dependencias |
| `models` | 9 | 237 | dataclasses (`WebForm`, `EntryPoint`, `Symbol`, `Call`…) |
| `exporters` | 5 | 1611 | JSON de índices + Markdown técnico (`technical_documentation_renderer.py` 1222 líneas, deuda declarada) |
| `context` | 8 | 1354 | contexto de sistema, hydration, `ai_projection`, `consumer_projection` |
| `documentation` | 20 | 2385 | documentación humana (flujos, scaling) + módulos V3 históricos |
| `orchestration` | 4 | 498 | `ai_interpretation`, `proposal_adapter` |
| `llm` | 6 | 311 | contratos de provider, `FakeLLMProvider`, `CopilotProvider`, `GeminiProvider` |
| `knowledge` | 77 | 8809 | núcleo V3/V4 (canonical, approval, proposals, plugin_projection, readiness, closure) |
| `cli` | 11 | 1945 | parser, router, `full_pipeline`, `pipeline_stages`, manifest, summary |

Pipeline `full` (13 stages, `cli/stage_identity.py`): `SCAN → EXTRACTION → CALL_RESOLUTION → WEB_ENTRY_RESOLUTION → DATABASE_RESOLUTION → FLOW_RESOLUTION → DEPENDENCY_RESOLUTION → EXPORT → CONTEXT → DOCUMENTATION → [AI_INTERPRETATION → PROPOSAL_GENERATION] → FINAL_SUMMARY`. Los dos stages de IA son `NOT_RUN` sin `--allow-ai-interpretation`. `analyze` (`main.py:analyze_repository`) ejecuta hasta CONTEXT.

Flujo de datos de IA: `index/*.json` → `EvidenceHydrator.hydrate_flow` → `select_flow_ids` (buckets de riqueza, round-robin) → `AiProjectionBuilder.package` (presupuesto, 2 pasadas) → `LLMRequest` → provider → `proposal_adapter` → `proposals/` (siempre pendientes). `context/ai_projection.py` no importa `llm`; `orchestration/ai_interpretation.py` no nombra ningún provider concreto salvo vía `_resolve_provider`/`ProviderRegistry`.

## V4.3 CONTRACTS TO PRESERVE

- **IDs estables** derivados por hash (`FLOW-…`, `PATH-…`, `EP-…`, `DAO-…`, `PRP-…`, `REQ-`/`RESP-` vía `sid`). Cambiar la derivación rompe evidence_refs y proposals.
- **evidence_refs**: toda propuesta cita IDs que existen en `index/*.json` del mismo run (R9 verificó 17/17).
- **Semántica confirmed / inferred / unresolved**: nunca se promueve unresolved a confirmed sin evidencia determinista; `flow_unresolved` se preserva (162 914 boundaries en el baseline).
- **Orden determinista**: `sorted(...)` en manifest, particionado por hash estable (no `hash()` de Python), selección/bucket sin azar.
- **Proposals**: `PENDING_TECHNICAL_LEAD_REVIEW`, `technical_lead_approval=false`, `canonical_knowledge_produced=false`; sin auto-aprobación ni canonicalización.
- **Runtime Independence** y **distribución limpia** (`main.py` + `legacy_documenter/` únicamente; `tools/v4_3_r7_build_pilot_distribution.py`).
- **CLI**: subcomandos, flags (`--output`, `--verbose`, `--allow-ai-interpretation`), exit codes, sin IA sin el flag.
- **Directorios de output**: `index/`, `context/`, `documentation/`, `ai_context/`, `consumer_projection/`, `proposals/`, `RUN_SUMMARY.json|md`, `OUTPUT_MANIFEST.json`.
- **consumer_projection**: JSON estable, autocontenido, particionado (`parts/part-NNNNNN.json`).
- **Documentación humana**: español por defecto, summary-first, partición a escala.
- **Provider opcional**: `github-copilot-sdk` solo se importa dentro de `_generate`; `requirements-copilot.txt` es opcional.
- Tests V4.3: 2169, 0 fallos/errores, 132 skips esperados en clone fresco (`PROJECT_STATE.json`; re-verificado abajo).

## TECHNOLOGY COUPLINGS

Conteo por archivo de referencias a WebForms/VB/vbproj/Oracle/ADO.NET/Copilot (grep sobre `legacy_documenter/`). No se corrigió nada.

| Acoplamiento | Ubicación | Clasificación |
|---|---|---|
| Extensiones `.vb/.vbproj/.aspx/.ascx/.sln` | `config.py`, `scanner/file_classifier.py` | adapter candidate |
| Extracción VB.NET (símbolos, calls, eventos), WebForms (directivas, CodeBehind, master pages, registers), `.vbproj`, `web.config` | `extractors/vbnet_extractor.py`, `call_extractor.py`, `web_event_extractor.py`, `webforms_extractor.py`, `vbproj_extractor.py`, `solution_extractor.py`, `webconfig_extractor.py` | adapter candidate |
| Modelo `WebForm` y `entry_point` con semántica WebForms (`Page_Load`, eventos de control) | `models/webform.py`, `models/entry_point.py`, `analysis/web_entry_resolver.py` | adapter candidate (el concepto `entry_point` es core; su origen WebForms no) |
| Oracle / ADO.NET (`OracleClient`, `OleDb`, direcciones de parámetros, `BeginTrans`, stored procedures) | `extractors/database_extractor.py`, `_database_classification.py`, `analysis/database_resolver.py` | adapter candidate (DB) |
| `.NET Framework` / agrupación por `.vbproj` | `analysis/dependency_resolver.py`, `exporters/_documentation_partitioning.py`, `documentation/human_documentation_scaling.py` (38 hits) | adapter candidate; el particionado por "proyecto" es core, su fuente `.vbproj` es adapter |
| Resolución de flows sobre calls/entry points/DAO | `analysis/flow_resolver.py`, `_flow_*` | core (opera sobre estructuras ya normalizadas, pero hereda campos con nombre WebForms/VB) |
| Redacción técnica (50 hits) y humana (10 hits) con vocabulario WebForms/Oracle | `exporters/technical_documentation_renderer.py`, `documentation/human_flow_documentation.py` | presentation |
| Hydration / system context con campos `webform`, `project` | `context/hydration.py`, `context/system_context_builder.py` | core con fuga de vocabulario (candidato a normalizar en V5.1) |
| `pipeline_stages.py` (17 hits): stages con nombres/argumentos WebForms/DB | `cli/pipeline_stages.py` | legacy compatibility (nombres de stage y flags V4.2 son contrato) |
| `.vb` en clasificación de conocimiento y `plugin_projection` | `knowledge/classification/catalog.py`, `knowledge/plugin_projection/*` | legacy compatibility |

Conclusión: la tecnología está concentrada en `extractors/` (+ parte de `analysis/`) como se esperaba, pero **el vocabulario WebForms/VB/Oracle también atraviesa `exporters/`, `documentation/`, `context/hydration` y `cli/pipeline_stages`**, es decir, el "core" de V4.3 no está separado de forma explícita; la frontera existe por convención de índices JSON, no por contrato tipado.

## PROVIDER COUPLINGS

- Contrato ya neutral en `llm/core.py`: `LLMProvider` (ABC: `generate`, `capabilities`, `model_info`), `LLMRequest/Response`, `LLMCapabilities`, `ProviderConfig`, `render_request_payload`, `measure_request_payload`, `ProviderRegistry`.
- `ProviderRegistry.create` solo conoce `FAKE` y `COPILOT` (`ValueError("unknown provider")` en otro caso). Es el punto de acoplamiento principal (registro cerrado, `if` por tipo).
- `providers/copilot.py`: `structured_generate` no es parte del ABC (solo en implementaciones), la orquestación llama `provider.structured_generate(...)`, así que el contrato mínimo real es más grande que el ABC.
- `FakeLLMProvider._status` compara `context["statistics"]["estimated_tokens"]` (no el payload final); el gate real lo hace `orchestration/ai_interpretation.py` con `measure_request_payload`.
- `providers/gemini.py` (29 líneas, no registrado): stub no utilizado por el registro; no es evidencia de soporte multi-provider.
- `asyncio.run` en `CopilotProvider.generate/structured_generate` (un event loop por llamada). Los módulos `analysis/deep_interpretation.py`, `documentation/{generator,hierarchical,resume,systematic}.py` y `llm/copilot_pilot.py` (V3) llaman `asyncio.run(discover_model())` y nombran Copilot directamente: legacy V3, fuera del pipeline `full`.
- `_resolve_provider` (en `ai_interpretation.py`) construye un `ProviderConfig` sin `context_window`; el límite se cubre con un default interno de tokens (`_payload_token_limit`).

Contrato mínimo propuesto para providers futuros (Copilot, Claude, OpenAI, Ollama, Gemini, Fake): `capabilities()` (context_window, max_output_tokens, structured_output, json_mode, system_instruction, temperature_control), `structured_generate(request, schema) -> LLMResponse` con estados cerrados (`SUCCESS`, `CONTEXT_TOO_LARGE`, `INVALID_STRUCTURED_OUTPUT`, `PROVIDER_ERROR`, `TIMEOUT`, `RATE_LIMITED`, `UNSUPPORTED_CAPABILITY`), errores sanitizados sin secretos, registro extensible por config y no por `if`, credenciales por referencia (`credential_source`), y ejecución sin dependencias del SDK a nivel de módulo.

## DOCUMENTATION/PROJECTION BASELINE

Baseline real (`v4_3_ai_rerun_r3a_r1_retry1`), 1626 MB en total:

| Directorio | Archivos | Tamaño | Naturaleza |
|---|---|---|---|
| `index/` | 22 | ~973 MB | **evidence** (fuente determinista) |
| `documentation/` | 876 | ~223 MB | **presentation** (humano; regenerable desde `index/`) |
| `ai_context/` | 5 | ~273 MB | **AI-facing** derivado (parcialmente duplica `index/`) |
| `consumer_projection/` | 27 | ~194 MB | **consumer-facing** derivado, particionado |
| `context/` | 1 | ~1 MB | contexto de sistema |
| `proposals/` | 2 | 8 KB | **interpretación IA** pendiente de revisión, no evidence |

Contenido: 15 151 archivos escaneados, 12 662 entry points, 12 642 flows, 170 020 paths, 162 914 unresolved boundaries, 20 082 data_access, 335 698 functional_dependencies, 4 612 paths a operación de datos, 1 121 a stored procedure. `ai_context/ARCHITECTURE_GRAPH.json`: 108 104 nodos / 180 909 aristas.

Clasificación:
- **Evidence**: `index/*`. Única fuente de verdad; todo lo demás debería ser derivable.
- **Presentation**: `documentation/` (humana y técnica), `RUN_SUMMARY.md`. Puede regenerarse sin reanalizar leyendo `index/`.
- **AI-facing**: `ai_context/` y el `LLMRequest` armado por `AiProjectionBuilder`. Regenerable sin reanalizar.
- **Consumer-facing**: `consumer_projection/`. Regenerable sin reanalizar.
- **Candidato a persistir como knowledge normalizado**: el grafo de flows/paths/unresolved con IDs y provenance (hoy repartido entre `index/functional_*`, `ai_context/FUNCTIONAL_FLOWS.json` y `TRACEABILITY.json`); y las decisiones de revisión sobre `proposals/` (hoy sin superficie de aprobación: `approval_surface_implementation: NOT_IMPLEMENTED`).

Duplicación aparente: `ai_context/FUNCTIONAL_FLOWS.json` (144 MB, flows+paths) repite `index/functional_flows.json` (124 MB) + `index/functional_paths.json` (124 MB); `TRACEABILITY.json` (59 MB) repite relaciones ya en índices. Los `unresolved_flow_boundaries.md` (~12.9 MB) y los `flujos_humanos/*-part-*.md` (hasta ~9.9 MB) son documentación humana que reexpresa el mismo contenido de `flow_unresolved`. Hallazgo (V4.3 F-P02/P03) coherente con el pedido de V5.2: la documentación es correcta pero difícil de seguir y las propuestas son grounded pero triviales/técnicas.

## PERFORMANCE/SCALE BASELINE

- Suite: 74 archivos de test; 2169 tests, 132 skips esperados según `PROJECT_STATE.json` (re-ejecución en esta ronda, ver TESTS / COMMANDS).
- Fase de análisis (SCAN a resolución, antes de exportar) sobre IST: `index/repository.json` → `duration_seconds = 75.126` para 15 151 archivos. **No hay timings por stage persistidos** en `RUN_SUMMARY.json` (solo `status` por stage); el tiempo de EXPORT/CONTEXT/DOCUMENTATION/IA no está medido en ningún artefacto. Es un vacío de baseline: V5.3 necesita métricas por stage antes de optimizar.
- Archivos más grandes: `functional_dependencies.json` 227 MB, `calls.json` 212 MB, `ai_context/FUNCTIONAL_FLOWS.json` 144 MB, `functional_flows.json` 124 MB, `functional_paths.json` 124 MB, `flow_unresolved.json` 118 MB, `data_parameters.json` 91 MB, `ARCHITECTURE_GRAPH.json` 70 MB, `TRACEABILITY.json` 59 MB. Los índices se escriben monolíticos (un JSON por índice, cientos de MB): implica carga completa en memoria para hidratar.
- Etapas presumiblemente costosas (a confirmar con timings): resolución de flows (170k paths), exportación de índices monolíticos, DOCUMENTATION (876 archivos), `ai_context`/`consumer_projection`. La IA es un único request por run (`provider_calls: 1`).
- Lazy generation: `AI_INTERPRETATION`/`PROPOSAL_GENERATION` ya son lazy (opt-in). `documentation/`, `ai_context/`, `consumer_projection/` se generan siempre en `full`; candidatos a generación por perfil (V5.2).
- Selección/empaquetado IA (V4.3 R3A-R1): 35/40 flows ricos exceden por sí solos el presupuesto `SMALL`; 5/40 caben; el costo depende del conjunto, no del orden.

## INCREMENTAL/CACHE CANDIDATES

Hipótesis (no implementadas):

| Stage | Reutilizable si cambian pocos archivos | Clave candidata |
|---|---|---|
| SCAN | sí (lista + hash de contenido por archivo) | hash SHA-256 por archivo + config de excludes |
| EXTRACTION | sí, por archivo (VB/aspx/ascx) y por proyecto (`.vbproj`, `.sln`, `web.config`) | hash de archivo + versión del extractor |
| CALL_RESOLUTION / WEB_ENTRY / DATABASE | parcial: dependen de la tabla global de símbolos | hash de archivo + huella del conjunto de símbolos alcanzables |
| FLOW_RESOLUTION | parcial: se invalida un flow si cambia cualquier archivo de su clausura transitiva | huella de la clausura del flow (`flow_max_depth`) |
| DEPENDENCY_RESOLUTION | proyecto-nivel | hash de `.sln/.vbproj` |
| EXPORT / CONTEXT / DOCUMENTATION | regenerables desde índices por partición | hash del índice + versión de template/perfil |
| AI stages | por `context_package_id` + `source_snapshot` (ya existen) | request_id (`REQ-` es hash del contenido) |

Necesita: fingerprints por archivo, índice persistido de dependencias inversas (archivo → símbolos → flows) para propagar invalidación, versión por stage y por schema, y escritura por particiones en lugar de JSON monolítico. IDs derivados por hash ya son estables ante orden, lo que favorece la reutilización. Riesgo: cualquier cambio de determinismo (orden, hash) invalida la equivalencia byte a byte exigida por V4.2/V4.3.

## TEMPLATE/PROFILE REQUIREMENTS

Requisitos (diseño, sin implementación) para V5.2:

- Perfiles mínimos: `human-functional`, `human-technical`, `ai-context`.
- Separación: **Template = presentación**, **Profile = selección** (qué evidencia/secciones/nivel de detalle), **Renderer = formato** (Markdown/JSON/…).
- Los templates no alteran evidence, confidence, relationships ni unresolved; solo redactan y ordenan. Un test debe poder demostrar que dos templates distintos sobre el mismo `index/` producen los mismos IDs, refs y estados.
- Parámetros: idioma (ES por defecto, contrato V4.3), audiencia, nivel de detalle (resumen / flujo / apéndice de evidencia), templates por defecto + custom, apéndices de evidence enlazados por `evidence_ref`.
- Entrada única: el modelo normalizado de V5.1 (no `index/*.json` crudo con vocabulario WebForms).
- Determinismo: mismo perfil+template+índice → mismo output byte a byte; versión de template incluida en la clave de cache (V5.3).
- Punto de partida real: `technical_documentation_renderer.py` (1222 líneas, mezcla selección, formato y vocabulario Oracle/WebForms) es el candidato de extracción ya reconocido en `PROJECT_STATE.json`.
- `human-functional` debe reducir el ruido que hoy produce `flujos_humanos/` (documentos de hasta ~10 MB); `ai-context` debe permitir proposals menos técnicas sin cambiar el grounding.

## RUNTIME INDEPENDENCE

- Rutas `analyze` / `full` / `output-manifest`: no se encontró `open()`/`Path` a `docs/`, `prompts/`, `tests/`, `PROJECT_STATE.json` ni `governance/` bajo `legacy_documenter/`. Las menciones a `docs/V4_x/...` en `cli/`, `context/`, `documentation/`, `exporters/` son solo docstrings/comentarios.
- **Hallazgo (matiz respecto de la afirmación de R9)**: hay módulos que sí leen artefactos de desarrollo: `knowledge/readiness.py` (lee `codex/V3/V3_R8_4_REVISION_HUMANA_APROBADA.md`, `output/LEVANTAMIENTO_*.md`) y `knowledge/closure/{baseline_report,manifest_report}.py` (leen `PROJECT_STATE.json`, `docs/V4/`), además de `documentation/human_review.py` y `second_review.py` (escriben/leen `codex/V3`). `router.py` importa `knowledge.readiness` a nivel de módulo, y este importa `documentation.second_review`. Ninguno de estos lee archivos al importar (solo al ejecutar `readiness`), por lo que `analyze`/`full`/`output-manifest` no dependen de ellos en ejecución. Pero el subcomando `readiness` **no es runtime-independent** de una distribución limpia y `legacy_documenter/` no está estrictamente libre de referencias a rutas de desarrollo. R9 lo declaró PASS acotado a los flujos de piloto; para V5 debe fijarse explícitamente si `readiness`/`closure` son parte del runtime o del tooling de desarrollo.
- Provider Copilot: import diferido, sin dependencia dura.
- No se modificó packaging.

## PROCESS EXIT OBSERVATION

Observación previa: un run determinista escribió `FINAL_SUMMARY=SUCCESS` y `RUN_SUMMARY`, pero el proceso quedó vivo.

Evidencia en código (búsqueda de `threading`, `Thread`, `ThreadPoolExecutor`, `concurrent.futures`, `atexit`, `subprocess`, `Popen`, `asyncio`, `daemon`, `os._exit`, `terminate/kill`) sobre `legacy_documenter/` y `main.py`:
- **Ningún** uso de threads, executors, `atexit` ni `subprocess` en producción.
- `asyncio.run` solo aparece en `CopilotProvider.generate/structured_generate` y en módulos V3 (`discover_model`); ninguno se ejecuta en un run determinista.
- `CopilotProvider._generate` hace `session.disconnect()` y `client.stop()` en `finally`, pero `CopilotClient` (SDK externo, no auditado) puede lanzar procesos/hilos propios: un cliente que no se detiene limpiamente dejaría el proceso vivo **solo en runs con IA**.
- `main.py` termina con `raise SystemExit(main())`.

Reproducción: 3 ejecuciones consecutivas de `python main.py full tests/fixtures/v4_2_r7_full_sample --output <scratchpad>` terminaron con exit code 0 y sin timeout (fixture pequeño). No se reprodujo a escala IST.

**Conclusión: `not reproduced`** (con evidencia insuficiente para IST completo). El código de producción del camino determinista no contiene ningún mecanismo que pueda mantener el proceso vivo; la causa más plausible (a probar, no declarada) es externa al runtime determinista (p. ej. un proceso Copilot residual o el entorno de terminal). Sugerencia para R1/R2: registrar timings por stage y logging de `threading.enumerate()` al final en un run real si vuelve a ocurrir.

## RISKS

1. **Core no separado de tecnología**: vocabulario WebForms/VB/Oracle en exporters, documentation, hydration y stage names. Normalizar sin romper IDs/orden es el riesgo central de V5.1.
2. **Índices monolíticos** (hasta 227 MB) y duplicación entre `index/`, `ai_context/`, `TRACEABILITY`: tope de memoria/tiempo para V5.3.
3. **Falta de timings por stage** y de una medición de memoria: no hay baseline para demostrar mejoras incrementales.
4. **Registro de providers cerrado** (`FAKE`/`COPILOT`) y contrato ABC incompleto (`structured_generate` fuera del ABC).
5. **Runtime Independence matizada** (readiness/closure/human_review referencian rutas de desarrollo).
6. **Determinismo byte a byte**: cambios de templates/normalización pueden invalidar manifests históricos (`V4_2_FINAL_MANIFEST`, `OUTPUT_MANIFEST`).
7. **Riesgo intermitente** heredado `test_deterministic_run_then_ai_enabled_rerun_same_output` (V4.2-R6): cualquier recurrencia es trigger de investigación.
8. **`technical_documentation_renderer.py`** (1222 líneas) alto riesgo de extracción.
9. **Process exit** no explicado.
10. **Módulos V3 históricos** (`documentation/{generator,hierarchical,resume,systematic}`, `analysis/deep_*`, `llm/copilot_pilot`) acoplados a Copilot y con código denso en una línea; convivir con V5 requiere decidir su destino (mantener, aislar, retirar).

## OPEN DECISIONS FOR R1

1. ¿Qué se normaliza primero en el modelo core: entry point/flow/path/unresolved/data-operation, y con qué nombres neutrales? ¿Se conservan los campos WebForms como extensión del adapter?
2. ¿Los índices V4.3 (`index/*.json`) siguen siendo el formato canónico de salida (compatibilidad) o se convierten en una proyección del núcleo normalizado?
3. ¿Se persiste el conocimiento normalizado como artefacto propio (y dónde), o solo se cachea?
4. ¿`readiness`, `closure`, `human_review`, `second_review` pertenecen al runtime, a `tools/`, o se congelan como legacy V3/V4?
5. ¿Qué contrato de provider se fija (incluir `structured_generate` en el ABC, registro por configuración, manejo de ciclo de vida del cliente)? ¿Se retira o se completa `GeminiProvider`?
6. ¿Política de compatibilidad: V5 debe reproducir byte a byte los outputs V4.3 en IST o solo equivalencia semántica (IDs, refs, estados, conteos)?
7. ¿Dónde vive la frontera entre Profile (selección) y AI projection (selección/presupuesto ya existente)?
8. ¿Se mide y persiste timing/memoria por stage como parte del contrato (recomendado antes de V5.3)?
9. ¿Estrategia de migración de docs V4.3 (`flujos_humanos`, `unresolved_findings`) al esquema de templates?

## RECOMMENDED R1 CONTRACT BOUNDARIES

1. **Normalized Evidence contract** (tecnología-neutral): entidades y campos mínimos (`EntryPoint`, `Flow`, `Path`, `Call`, `DataOperation`, `Unresolved`, `EvidenceRef`), reglas de ID (mismas que V4.3), provenance y estados confirmed/inferred/unresolved.
2. **Adapter interface**: qué produce un adapter (archivos → entidades normalizadas) y qué no puede hacer (no interpreta, no promueve confianza). El adapter WebForms/VB/Oracle es el primer caso y debe reproducir el baseline IST.
3. **Persistence/cache boundary**: qué es evidencia persistida, qué es proyección regenerable, versionado de schema y de stage, reglas de invalidación (solo diseño; implementación V5.3).
4. **Projection model**: `index` legacy, `ai_context`, `consumer_projection` como proyecciones del núcleo, con garantía de no alterar evidence.
5. **Template/Profile/Renderer contracts** (V5.2), con los tres perfiles mínimos y la regla “template no cambia evidencia”.
6. **Provider contract**: ABC completo, capacidades declaradas, estados cerrados, registro extensible, ciclo de vida del cliente, sanitización, gate de presupuesto sobre payload final (ya existente).
7. **Compatibility & migration**: lista de invariantes V4.3 de este documento como suite de aceptación; política de outputs paralelos durante la transición.
8. **Observabilidad**: timings por stage y memoria en `RUN_SUMMARY.json` como campo aditivo.

## TESTS / COMMANDS EXECUTED

Todos de solo lectura o sin efecto sobre el repo:

- `python -m unittest discover -s tests` → `Ran 2169 tests in 142.206s — FAILED (failures=4, skipped=132)`. Los 4 fallos son preexistentes y no provienen de esta ronda (no se tocó código ni `PROJECT_STATE.json`): `test_v4_r13_regression_and_security.RepositoryContinuityStateTests.test_project_state_no_ai_or_provider_calls_recorded`, `test_v4_r14_manuals_and_final_baseline.DeterminismTests.test_baseline_matches_on_disk_artifact`, `...EntryGateAndContinuityTests.test_project_state_readiness_ready`, `...NoProviderOrLlmCallsTests.test_project_state_confirms_zero_calls`. Causa aparente: esos tests V4-R13/R14 esperan `provider_calls`/`real_llm_calls == 0` en `PROJECT_STATE.json`, que desde el piloto real V4.3 vale 1. Contradice el "0 fallos" de `PROJECT_STATE.json`/R9; no se corrige aquí (deuda a reportar, R1 debe decidirlo). Los 132 skips coinciden con lo esperado.
- `python main.py full tests/fixtures/v4_2_r7_full_sample --output <scratchpad>/exit_run_{1,2,3}` (3 veces, sin `--allow-ai-interpretation`, sin provider) → exit 0 las 3 veces, salida fuera del repo.
- Búsquedas `grep`/`find`/`du`/`wc` sobre `legacy_documenter/`, `tests/`, `docs/`.
- Lectura de `RUN_SUMMARY.json` e índices JSON del output real existente.
- No se ejecutó full IST, ni `--allow-ai-interpretation`, ni ningún provider real.

## FILES READ

`CLAUDE.md`, `AGENTS.md`, `PROJECT_STATE.json`, `docs/V4/V4_AI_HANDOVER.md`, `docs/V5_0/V5_0_R0_EMPIRICAL_BASELINE_AND_ARCHITECTURE_PREP_PROMPT.md`, `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`, `docs/continuity/LEGACYMAPPER_LESSONS_LEARNED.md` (parcial), `docs/V4_3/V4_3_R9_FINAL_CLOSURE_RESULT.md` (parcial), `docs/V4_3/V4_3_WORKSTATION_REBASELINE_RESULT.md` (parcial), `main.py`, `legacy_documenter/main.py`, `cli/{parser,router,stage_identity}.py`, `llm/core.py`, `llm/providers/{copilot,gemini}.py`, `orchestration/ai_interpretation.py` (parcial), `extractors/_database_classification.py`, `models/webform.py`, `knowledge/readiness.py` (parcial), `tools/v4_3_r7_build_pilot_distribution.py` (grep), y del output real `C:\PruebasLegacyMapper\Resultados\v4_3_ai_rerun_r3a_r1_retry1`: `RUN_SUMMARY.json`, `index/*.json` (conteos), `ai_context/*.json` (conteos).

## FILES MODIFIED

- Creado: `docs/V5/V5_0_R0_EMPIRICAL_BASELINE.md`.
- Creado: `docs/V5/V5_0_R1_ARCHITECTURE_CONTRACT_PROPOSED_PROMPT.md` (prompt propuesto, no ejecutado).
- Ningún otro archivo del repo modificado (`git status` solo muestra `.claude/` y `docs/continuity/` sin trackear, previos a esta ronda, más `docs/V5/`).
