# V4.3 — R0 — Baseline empírico y contrato de alcance — Resultado

## Estado de esta ronda

`V4_3_R0_RESULT_DRAFTED_PENDING_HUMAN_REVIEW`. Este documento formaliza el alcance de V4.3 a partir de la
evidencia empírica suministrada en `docs/V4_3/V4_3_EXECUTION_PLAN.md`, tratada como requisito. No implementa
código, no modifica el runtime de LegacyMapper y no cierra ni versiona V4.3. R0 queda pendiente de aprobación
humana (ver sección 9); esa aprobación cubre únicamente este resultado R0, no el cierre de V4.3. El cierre y
versionado formal de V4.3 corresponde exclusivamente a R9 (`prompts/V4_3/V4_3_R9_CLOSURE_AND_VERSIONING.md`),
al final del orden obligatorio `R0 → R1 → … → R9` de `V4_3_EXECUTION_PLAN.md`; esta ronda no la adelanta ni la
sustituye. `PROJECT_STATE.json` no fue modificado en R0: sigue reflejando `V4_2_FORMALLY_CLOSED` /
`next=V5_DESIGN_PENDING`.

## 1. Lectura previa realizada

Se leyeron, como exige `CLAUDE.md`: `AGENTS.md`, `PROJECT_STATE.json`, `docs/V4/V4_AI_HANDOVER.md`,
`output/v3_final/V3_FINAL_BASELINE.json` (referenciado vía `PROJECT_STATE.json.canonical_v3_baseline_path`),
y el prompt activo `prompts/V4_3/V4_3_R0_EMPIRICAL_BASELINE_AND_SCOPE.md`. Adicionalmente, por instrucción
explícita del prompt: `docs/V4_3/V4_3_EXECUTION_PLAN.md`, `docs/V4/V4_ARCHITECTURE_AND_CONTRACT_REFERENCE.md`,
y los contratos de código bajo `legacy_documenter/context/`, `legacy_documenter/documentation/`,
`legacy_documenter/llm/`, `legacy_documenter/exporters/technical_documentation_renderer.py` y
`legacy_documenter/knowledge/{proposals,projection,plugin_projection}/`.

Se verificó explícitamente que **no existe** en este repositorio ningún `test_flow_ai*.py`,
`list_copilot_models.py`, ni la carpeta `C:\PruebasLegacyMapper`. Los hallazgos citados en
`V4_3_EXECUTION_PLAN.md` se tratan como evidencia externa reportada por el Líder Técnico, no como artefactos
reproducibles dentro de este repositorio, y no se ha copiado ni se copiará ningún script del piloto.

## 2. EXTERNAL_EMPIRICAL_EVIDENCE

Registro literal de los ocho hallazgos de `V4_3_EXECUTION_PLAN.md`, convertidos en requisitos de esta versión.
Cada uno se referencia por su identificador `EEE-0N` en las secciones siguientes.

| ID | Hallazgo | Fuente |
|---|---|---|
| EEE-01 | El análisis determinista del sistema real funciona. | Piloto externo (`C:\PruebasLegacyMapper`, fuente `C:\inetpub\wwwroot\2010\IST\operacional`) |
| EEE-02 | Un contexto `SYSTEM` puede terminar en un prompt real de ~13.8 MB / ~3.6 M tokens aunque la estimación interna sea mucho menor. | Piloto externo |
| EEE-03 | Un contexto `FLOW` filtrado es pequeño, pero actualmente contiene principalmente referencias y no suficiente significado. | Piloto externo |
| EEE-04 | Una proyección `FLOW` hidratada experimental de ~5.6k tokens permitió una interpretación útil y trazable. | Piloto externo |
| EEE-05 | La IA debe recibir instrucciones explícitas de no usar herramientas y devolver solo la estructura requerida. | Piloto externo |
| EEE-06 | La documentación técnica actual es correcta pero algunas vistas siguen siendo demasiado grandes/planas para humanos. | Piloto externo |
| EEE-07 | La documentación humana debe ser español por defecto. | Piloto externo |
| EEE-08 | El detalle exhaustivo debe conservarse como evidencia, pero no dominar la vista humana principal. | Piloto externo |

Estos hallazgos son consistentes con, y en varios casos re-confirman a menor escala, las observaciones ya
registradas formalmente durante el piloto real de V4.2-R7 (`docs/V4_2/V4_2_R7_REAL_IST_DOCUMENTATION_REVIEW.md`,
hallazgos `F-01`..`F-07`, estado en `PROJECT_STATE.json.r7_findings`). En particular `F-06`
(`PRESERVED_OBSERVATION`, ruido de `InitializeComponent()` en `UNRESOLVED_FINDINGS.md`) y la constatación de
`FUNCTIONAL_FLOWS.md` como `NOT_USEFUL` a escala real (396,178 líneas / 44 MB) son la misma clase de problema
que EEE-06/EEE-08. Esta ronda no reabre ni redefine `F-05`/`F-06`/`F-07`; los mantiene como antecedentes.

## 3. Inventario de componentes actuales

### 3.1 Contexto (`legacy_documenter/context/`)

| Módulo | Responsabilidad verificada | Relación con EEE |
|---|---|---|
| `system_context_builder.py` (`SystemContextBuilder`) | Construye, de forma determinista, `SYSTEM_CONTEXT.json`, `ARCHITECTURE_GRAPH.json`, `FUNCTIONAL_FLOWS.json`, `TRACEABILITY.json` bajo `output/.../ai_context/` a partir de los índices ya producidos por el pipeline. No hace hidratación de contenido narrativo; produce estructura y referencias. | EEE-01, EEE-02 |
| `resolver.py` (`ContextResolver`) | Lee esos artefactos y resuelve un paquete por `package_type` (`SYSTEM`, `FUNCTIONAL`, `TECHNICAL`, `ENTITY`, `FLOW`, `DATA_ACCESS`). Para `SYSTEM`/`FUNCTIONAL`/`TECHNICAL`, `flow_ids` por defecto es **todos** los flujos (`limits.get("flows", len(self.flow_by_id))`) salvo que el llamador pase un límite explícito. Los `records` resultantes (`flow_refs`, `path_refs`, `data_access_refs`, `evidence_refs`, `unresolved_refs`) son identificadores puros, no contenido hidratado. | EEE-02, EEE-03 |
| `composer.py` (`ContextComposer`) | Aplica un perfil de presupuesto (`TINY`/`SMALL`/`MEDIUM`/`LARGE`/`FULL`) sobre la salida de `ContextResolver`, recorta por prioridad (`P0`..`P4`) y produce estadísticas de truncamiento. El perfil `FULL` es efectivamente ilimitado (`10**9` registros/caracteres) y sigue siendo seleccionable por el llamador; no hay ningún límite superior obligatorio independiente del perfil elegido. | EEE-02 |
| `context_builder.py` (`ContextBuilder`) | Utilidad no relacionada con el consumo por IA: escribe `output/.../context/projects.json` (resumen de tecnología/dependencias por proyecto). No interviene en el flujo `SYSTEM`/`FLOW` descrito arriba. | — |

Confirmado: la causa raíz de EEE-02 es de diseño, no de un bug puntual — nada impide hoy que un llamador
(humano o agente) solicite un paquete `SYSTEM`/`TECHNICAL` con perfil `FULL` o sin `limits.flows`, lo que
sobre un repositorio real produce un contexto del tamaño reportado. Confirmado también EEE-03: los `records`
de un paquete `FLOW` ya filtrado por `flow_id` siguen siendo listas de referencias (`{"ref", "priority",
"category"}"`), no el contenido semántico (nombres, evidencia textual, relaciones legibles) de esas
referencias. No existe en el repositorio ningún paso de "hidratación" que resuelva una referencia a su
contenido antes de enviarla a un proveedor de IA — lo que hace EEE-04 (una proyección hidratada experimental
fue útil) un hallazgo de un artefacto que hoy no existe en el producto.

### 3.2 Documentación (`legacy_documenter/documentation/`, `legacy_documenter/exporters/`)

| Módulo | Responsabilidad verificada | Relación con EEE |
|---|---|---|
| `interpretation.py` | Define `DocumentationProfile`/`DocumentationPrompt` y construye el `LLMRequest` para interpretación funcional/técnica. La instrucción de sistema actual es en inglés (`"You are an evidence-grounded software-system analyst..."`) y exige salida estructurada, pero **no** contiene una prohibición explícita de uso de herramientas. | EEE-05 |
| `synthesis.py`, `hierarchical.py`, `aggregation.py`, `coverage.py`, `resume.py`, `evidence_resume.py`, `evidence_catalog.py` | Capas deterministas de síntesis/cobertura/resumen sobre evidencia ya extraída; no generan texto narrativo por sí mismas, producen estructuras intermedias consumidas por exportadores. | EEE-06, EEE-08 |
| `renderer.py`, `generator.py`, `systematic.py`, `human_review.py`, `consistency*.py`, `second_review.py`, `envelope.py`, `contracts.py` | Orquestación y contratos deterministas de generación/consistencia/revisión humana. No dependen del piloto externo. | — |
| `exporters/technical_documentation_renderer.py` (802 líneas, marcado `HIGH_RISK_FUTURE_EXTRACTION_CANDIDATE` en `PROJECT_STATE.json.maintainability_debt`) | Genera `WEB_ENTRY_POINTS.md`, `FUNCTIONAL_FLOWS.md`, `DATABASE_ACCESS.md`, `UNRESOLVED_FINDINGS.md`. Texto verificado íntegramente **en inglés** (`"# Web Entry Points"`, `"Discovered N entry point(s)..."`, etc.). V4.2-R8 ya añadió una separación navegación/detalle (`*_navigation()` + `*_partitions()`) para los tres documentos que el piloto real de V4.2-R7 encontró `NOT_USEFUL` a escala (`F-01`), pero el idioma sigue siendo inglés y el hallazgo `F-06` (ruido `InitializeComponent()` en `UNRESOLVED_FINDINGS.md`) permanece `PRESERVED_OBSERVATION`, sin filtrar. | EEE-06, EEE-07, EEE-08 |

### 3.3 Interpretación por IA (`legacy_documenter/llm/`)

| Módulo | Responsabilidad verificada |
|---|---|
| `core.py` | Contratos provider-neutrales: `LLMRequest`/`LLMResponse`/`LLMCapabilities`/`ProviderConfig`, `FakeLLMProvider` (determinista, usado en tests) y `ProviderRegistry` (`FAKE`, `COPILOT`). Ningún camino de este módulo ejecuta contenido devuelto por el proveedor; la salida se valida contra esquema (`structured_generate`). |
| `providers/copilot.py`, `providers/gemini.py` | Adaptadores concretos de proveedor. Su existencia ya es compatible con la regla de `V4_AI_HANDOVER.md` ("Provider-specific adapters are permitted"); no se tocan en V4.3 salvo lo que EEE-05 exija a nivel de contenido del *prompt*, no del transporte. |
| `copilot_pilot.py` | Utilidad de piloto manual existente en el repositorio (distinta de los scripts del piloto externo `C:\PruebasLegacyMapper`, que no están ni deben copiarse aquí). |

### 3.4 Propuestas y proyecciones (`legacy_documenter/knowledge/`)

| Paquete | Responsabilidad verificada |
|---|---|
| `proposals/` (R8) | `ProposalRequest` -> `Proposal`; nunca genera `statement` automáticamente ni llama a un proveedor de IA, incluso con `proposal_method=AI_PROPOSED`. Sin cambios requeridos por EEE. |
| `approval/` (R9) | Decisión exclusiva del `TECHNICAL_LEAD`. Sin relación con EEE. |
| `canonical/` (R10) | Única colección canónica (`CanonicalKnowledgeCollection`). Sin relación directa con EEE, pero es la fuente de la que depende 3.4's `projection/`. |
| `projection/` (R11) | Proyección Markdown humana sobre el conocimiento canónico (`00-el-area/` … `09-capacitacion/`), ya **en español** (`markdown_renderer.py`: `"Naturaleza"`, `"Estado"`, `"Contexto temporal"`; `rules.py`: títulos de documento en español). Cubre conocimiento de área/gobernanza, no la evidencia técnica determinista de un sistema analizado — es un ámbito distinto del de `exporters/technical_documentation_renderer.py`. |
| `plugin_projection/` (R12) | Proyección `LegacyMapperPluginKnowledge` 1.0 sobre el conocimiento canónico, `R11_DEPENDENCY=NONE`. Estable y ya provider-neutral. No existe hoy una proyección equivalente y estable para la capa de **evidencia de contexto** (paquetes `ContextResolver`/`ContextComposer`) que un futuro plugin pueda consumir sin volver a resolver referencias — ese es precisamente el vacío que EEE-03/EEE-04 señalan. |

## 4. Clasificación de deuda

| ID | Deuda | Clasificación | Justificación | Ronda V4.3 candidata (informativa, no vinculante para esta ronda) |
|---|---|---|---|---|
| D-01 | Paquetes `SYSTEM`/`TECHNICAL`/`FUNCTIONAL` sin límite obligatorio de flujos/perfil, permiten un contexto real de escala EEE-02 | `V4_3_REQUIRED` | Riesgo directo y ya observado empíricamente (EEE-02); afecta el objetivo central de V4.3 ("consumible por IA sin enviar contexto masivo") | R5 (presupuesto de contexto de IA) |
| D-02 | `records` de un paquete `FLOW` son referencias puras, sin contenido hidratado (EEE-03) | `V4_3_REQUIRED` | Bloquea directamente el objetivo de interpretación útil; ya hay evidencia (EEE-04) de que la hidratación resuelve el problema | R2 (Evidence Hydration and Selection) |
| D-03 | No existe una proyección estable de evidencia hidratada consumible por un futuro plugin | `V4_3_REQUIRED` | Necesario para "preparada para un futuro plugin mediante una proyección estable, sin implementar Plugin Runtime" | R1 (Consumable Projection Contract) |
| D-04 | Instrucción de sistema de `interpretation.py` no prohíbe explícitamente el uso de herramientas por la IA (EEE-05) | `V4_3_REQUIRED` | Riesgo funcional/de seguridad concreto señalado por el piloto real; corrección acotada al contrato de prompt | R5/R6 |
| D-05 | `exporters/technical_documentation_renderer.py` genera documentación técnica en inglés por defecto (EEE-07) | `V4_3_REQUIRED` | Contradice el requisito "documentación humana debe ser español por defecto"; contraste directo con `knowledge/projection/` (ya en español) | R3 (Human Documentation) |
| D-06 | Vistas grandes/planas persistentes (`UNRESOLVED_FINDINGS.md` con ruido `F-06`; ausencia de vista humana priorizada más allá de navegación/detalle) (EEE-06, EEE-08) | `V4_3_REQUIRED` | V4.2-R8 mitigó parcialmente (partición navegación/detalle) pero no resolvió agrupación por significado ni el ruido de `F-06`; EEE-06/EEE-08 son observaciones frescas del mismo problema | R3/R4 (Scaling and Partitioning) |
| D-07 | `technical_documentation_renderer.py` con 802 líneas, marcado `HIGH_RISK_FUTURE_EXTRACTION_CANDIDATE` | `V5_DEFERRED` | Es deuda de mantenibilidad/extracción de módulo, no de proyección de evidencia ni de idioma; refactor sin cambio de comportamiento fue explícitamente `POST_V4_MAINTAINABILITY_REFACTOR=PLANNED` para una fase posterior, no parte del objetivo funcional de V4.3 | — |
| D-08 | `F-05`: `RUN_SUMMARY.json` sin duración de ejecución | `NO_CHANGE_REQUIRED` (para V4.3) | Ya clasificado y justificado como `DEFERRED_BY_DETERMINISM_CONTRACT` en V4.2; no relacionado con contexto, documentación consumible o interpretación por IA | — |
| D-09 | `F-07`: `WebEntryResolver` no adjunta `outgoing_calls` a puntos de entrada vinculados desde el marcado | `NO_CHANGE_REQUIRED` (para V4.3) | Gap de extracción/resolución determinista, no de proyección/documentación/consumo por IA; ya registrado como `PRESERVED_OBSERVATION` con su propio test de caracterización | — |
| D-10 | Agnosticismo tecnológico, framework genérico de providers/modelos, Plugin Runtime, adapters multi-tecnología, rediseño general del core | `V5_DEFERRED` | Explícitamente fuera de alcance por el propio prompt R0 y por `V4_AI_HANDOVER.md` §"V5 Boundary" | — |
| D-11 | Adaptadores de proveedor existentes (`providers/copilot.py`, `providers/gemini.py`) y contratos `llm/core.py` | `NO_CHANGE_REQUIRED` | Ya provider-neutral en el core; los adaptadores específicos están explícitamente permitidos | — |
| D-12 | `knowledge/proposals/`, `approval/`, `canonical/`, `plugin_projection/` (R8–R10, R12) | `NO_CHANGE_REQUIRED` | Ninguno de los ocho hallazgos empíricos los señala; su contrato ya es estable y provider-neutral | — |

## 5. Casos reales de aceptación externa — criterio de "documentación útil" para R0

Los cuatro casos de `V4_3_EXECUTION_PLAN.md` se registran aquí como el contrato de aceptación que las rondas
posteriores (R1–R7) deberán satisfacer; R0 no los implementa, solo los fija como criterio:

| Caso | Flujo | Tipo de terminal | Criterio de aceptación |
|---|---|---|---|
| A | `webCobMorosidad\CobLiquidacionDeudaPrev.ascx` → `Load` → `Page_Load` | Consulta compleja, múltiples terminales | La proyección hidratada debe distinguir cada terminal y su confianza (`confirmed`/`inferred`/`unresolved`) sin colapsarlos en uno solo |
| B | `webCobMorosidad\cobCargaArcIntRea.ascx` → `Click` → `btnCargar_Click` | Procesamiento/carga, terminales confirmados | La proyección debe exponer el/los procedimiento(s) almacenado(s) o accesos a datos confirmados con trazabilidad a `PATH`/`DAO`/`source` |
| C | `webCobMorosidad\cobChqInsRen.ascx` → `Click` → `HypGuardar_Click` | Escritura/transacción | La proyección debe señalar explícitamente la naturaleza transaccional/de escritura sin inferir reglas de negocio no evidenciadas |
| D | `webCobMorosidad\CobConsultaTransferencia.ascx` → `Load` → `Page_Load` | Sin terminal confirmado | La proyección debe declarar la incertidumbre de forma explícita (no inventar un terminal ni ocultar la ausencia de confirmación) |

Criterio transversal para los cuatro casos: cada proyección debe ser trazable hasta `FLOW`/`PATH`/`DAO`/fuente,
compacta (orden de magnitud EEE-04, no EEE-02), en español, y no debe promover evidencia `unresolved`/`inferred`
a `confirmed` sin respaldo determinista (invariante ya vigente: "Never promote unresolved evidence to
confirmed without deterministic evidence", `AGENTS.md`).

## 6. Mapa de componentes afectados (para revisión humana)

```text
legacy_documenter/context/resolver.py            -> D-01 (límites de flujos por defecto)
legacy_documenter/context/composer.py             -> D-01 (perfil FULL sin techo obligatorio)
legacy_documenter/context/system_context_builder.py -> D-02 (records sin hidratación; no genera hoy nada equivalente a D-03)
legacy_documenter/documentation/interpretation.py -> D-04 (instrucción de sistema sin prohibición de herramientas)
legacy_documenter/exporters/technical_documentation_renderer.py -> D-05, D-06 (idioma inglés, vistas planas)
legacy_documenter/knowledge/projection/           -> referencia de patrón ya conforme (español, proyección estable) para D-03/D-05
legacy_documenter/knowledge/plugin_projection/    -> referencia de patrón ya conforme (proyección estable, R11_DEPENDENCY=NONE) para D-03
```

Ningún archivo de este mapa fue modificado en esta ronda. Se listan exclusivamente para orientar el alcance
de R1–R7.

## 7. Frontera de alcance de V4.3 (reafirmada, sin cambios sobre el prompt/plan)

Fuera de V4.3, sin excepción, por instrucción explícita del prompt R0 y de `V4_3_EXECUTION_PLAN.md`:

- agnosticismo tecnológico general;
- framework genérico de providers/modelos de IA;
- Plugin Runtime;
- adapters multi-tecnología;
- rediseño general del core;
- Core ↔ tecnología analizada, Core ↔ proveedor/modelo de IA, evidence model tecnológico neutral (todo esto es V5).

El runtime de LegacyMapper no depende, y esta ronda no ha hecho que dependa, de: `docs/`, `prompts/`,
`codex/`, `tests/`, `PROJECT_STATE.json`, `AGENTS.md`, `CLAUDE.md`, resultados históricos de rondas, evidencia
del piloto externo, ni de ningún script experimental creado en `C:\PruebasLegacyMapper`.

## 8. Prohibiciones respetadas en esta ronda

- No se modificó el runtime (`legacy_documenter/`, `tools/`, `main.py`): confirmado, ningún archivo de código
  fue editado; solo se leyó.
- No se copió ningún script del piloto: confirmado, no se creó ningún archivo bajo `codex/`, `tools/` ni
  `legacy_documenter/` a partir de `C:\PruebasLegacyMapper`.
- No se cerró V4.3: `PROJECT_STATE.json` permanece sin cambios; no existe ningún
  `V4_3_R0_CLOSURE_AND_VERSIONING_RESULT.md` producido por esta ronda.

## 9. Revisión humana obligatoria (pendiente)

Pendiente de aprobación por el Líder Técnico:

- [ ] este resultado R0 (`docs/V4_3/V4_3_R0_SCOPE_AND_EMPIRICAL_BASELINE_RESULT.md`);
- [ ] no se crearon ni modificaron otros documentos de decisión en esta ronda (solo este resultado);
- [ ] el mapa de componentes afectados (sección 6);
- [ ] los criterios de aceptación (sección 5) y la clasificación de deuda (sección 4), en particular que D-07,
      D-08, D-09 y D-10 queden correctamente fuera de V4.3.

## 10. Siguiente paso

Tras la aprobación humana de este resultado, el orden obligatorio de `V4_3_EXECUTION_PLAN.md` continúa con
R1 (`V4_3_R1_CONSUMABLE_PROJECTION_CONTRACT.md`). Esta ronda no inicia R1.
