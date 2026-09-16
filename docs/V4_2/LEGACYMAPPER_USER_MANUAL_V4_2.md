# LegacyMapper — Manual de Usuario (V4.2)

Estado: V4.2 está formalmente cerrada (`PROJECT_STATE.json`: `current_version_status = V4_2_FORMALLY_CLOSED`).
Este manual describe exactamente lo que hace el código fuente actual (`legacy_documenter/`, `main.py`) — no
lo que una versión futura está diseñada para hacer. Donde V4.2 se detiene antes de alcanzar una capacidad,
ese límite se declara explícitamente en lugar de darse por sobreentendido.

---

## 4.1 Propósito

LegacyMapper analiza un repositorio legado .NET Framework / VB.NET / ASP.NET Web Forms / Oracle y produce
documentación técnica determinista sobre él, con un paso opcional y explícito de interpretación por IA sobre
esa misma evidencia.

El principio rector, declarado en `AGENTS.md` y aplicado en toda la base de código, es:

> **Python descubre y resuelve hechos. La IA interpreta después.**

Concretamente:

- Todos los hechos sobre el repositorio analizado — sus proyectos, símbolos, llamadas, WebForms, acceso a
  base de datos, flujos funcionales, dependencias — son descubiertos por código Python determinista
  (parsers, extractores, resolvedores) que nunca invoca a un proveedor de IA/LLM.
- Un proveedor de IA, cuando se habilita explícitamente, solo puede *reformular o explicar* evidencia que
  Python ya descubrió en la ejecución actual. Nunca puede inventar una relación, un hecho o un significado
  de negocio, y su salida nunca se trata como un hecho aprobado — ver §4.7 y §4.12.

V4.2 permanece acotada al ecosistema al que siempre apuntó: **.NET Framework / VB.NET / ASP.NET Web Forms /
Oracle**, exactamente igual que V4.1 (ver `docs/V4_2/V4_2_FINAL_CLOSURE_AND_VERSIONING_RESULT.md`,
`NOT_IMPLEMENTED_BOUNDARIES`). La agnosticidad de lenguaje, framework, base de datos, disposición de
proyecto y proveedor/modelo de IA es explícitamente **trabajo de V5**
(`PROJECT_STATE.json: next = "V5_DESIGN_PENDING"`); nada en el código fuente actual la implementa. No asuma
que LegacyMapper puede apuntarse, por ejemplo, a un repositorio Java o Node.js, o a un motor de base de
datos distinto, y recibir un tratamiento equivalente.

## 4.2 Instalación / Requisitos previos

LegacyMapper es un paquete Python simple sin ninguna dependencia de terceros declarada en tiempo de
ejecución (no existe `requirements.txt`, `pyproject.toml` ni `setup.py` en este repositorio) y sin
herramientas de empaquetado/despliegue. Los únicos requisitos previos evidenciados por el repositorio son:

- Un intérprete de Python compatible con la sintaxis usada en todo `legacy_documenter/` (sintaxis moderna de
  anotaciones de tipo como `str | None`, `from __future__ import annotations`; solo la biblioteca estándar —
  `argparse`, `dataclasses`, `pathlib`, `hashlib`, `json`, `ast`, `asyncio`, `unittest`). El entorno de
  desarrollo usado para este repositorio ejecuta CPython 3.14 (ver `__pycache__/*.cpython-314.pyc`); se
  espera que cualquier CPython 3.x razonablemente actual que soporte esta sintaxis funcione, pero no se
  declara ninguna versión mínima específica en ningún lugar del repositorio.
- No se requiere ninguna base de datos, servidor web, runtime de contenedores ni servicio externo para
  ejecutar `analyze` o `full` sin `--allow-ai-interpretation`.
- `--allow-ai-interpretation` requiere adicionalmente un proveedor de IA resoluble (ver §4.7) y, para el
  proveedor `COPILOT`, el cliente local de GitHub Copilot que la integración del proveedor espera
  (`legacy_documenter/llm/providers/copilot.py`); no hay credenciales ni endpoints codificados de forma fija
  ni documentados aquí porque ninguno está evidenciado como necesario para la operación normal.

No asuma que se necesita un paso `pip install`/virtualenv, una imagen Docker o un archivo de variables de
entorno — ninguno está presente en este repositorio. Si su entorno todavía no tiene un intérprete de Python
adecuado, instale uno por los medios normales de su plataforma; LegacyMapper no prescribe nada más allá de
eso.

## 4.3 CLI

LegacyMapper se invoca como `python main.py <comando> ...`. El parser (`legacy_documenter/cli/parser.py`)
define tres subcomandos explícitos más una forma legada compatible hacia atrás.

| Invocación | Significado |
|---|---|
| `python main.py analyze <repositorio> [opciones]` | Solo análisis determinista (comportamiento pre-V4.2). |
| `python main.py full <repositorio> [opciones]` | Análisis determinista + documentación técnica + resumen de ejecución. |
| `python main.py readiness` | Verifica la propia puerta de preparación de conocimiento de LegacyMapper; no analiza un repositorio. |
| `python main.py <repositorio> [opciones]` | Forma abreviada legada, reescrita silenciosamente a `analyze <repositorio> [opciones]`. |
| `python main.py -h` / `--help` | Muestra la ayuda de nivel superior (las cuatro formas), no tocada por la reescritura legada. |

`normalize_argv` (`legacy_documenter/cli/parser.py`) realiza la reescritura legada: cualquier lista de
argumentos cuyo primer token **no** sea `analyze`, `full`, `readiness`, `-h` o `--help` se trata como la
forma desnuda pre-V4.2 y se le antepone `analyze` antes de que argparse la vea siquiera. Esta es una
garantía fuerte de compatibilidad hacia atrás, no una segunda ruta de parseo — ambas grafías llegan
exactamente al mismo subparser `analyze`.

Opciones compartidas por `analyze` y `full`:

| Opción | Valor por defecto | Significado |
|---|---|---|
| `repository` (posicional) | — | Ruta del repositorio a analizar. |
| `--output` | `output` | Directorio de salida. |
| `--exclude` | (ninguno, repetible) | Nombre(s) de carpeta adicionales a excluir del escaneo. |
| `--verbose` | desactivado | Habilita el registro de nivel informativo. |
| `--flow-max-depth` | `12` | Profundidad máxima confirmada de llamadas a método para la resolución de flujo funcional. |

`full` añade una opción más:

| Opción | Valor por defecto | Significado |
|---|---|---|
| `--allow-ai-interpretation` | desactivado | Habilita un paso de interpretación por IA sobre la propia evidencia de esta ejecución (ver §4.7). |

`readiness` no toma argumentos — valida los propios requisitos previos de LegacyMapper, no un repositorio
objetivo (ver §4.6).

## 4.4 `analyze`

`analyze` (`legacy_documenter.main.analyze_repository`, enrutado vía
`legacy_documenter/cli/router.py::_route_analyze`) es el pipeline determinista pre-V4.2, preservado byte a
byte para scripts existentes. Este comando:

- escanea el repositorio (`legacy_documenter/scanner/`),
- extrae soluciones/proyectos/símbolos/WebForms/acceso a base de datos (`legacy_documenter/extractors/`),
- resuelve llamadas, puntos de entrada web, acceso a base de datos, flujos funcionales y dependencias
  (`legacy_documenter/analysis/`),
- escribe artefactos de índice JSON/Markdown (`legacy_documenter/exporters/json_exporter.py`,
  `markdown_exporter.py`) y artefactos de contexto (`legacy_documenter/context/`) bajo `--output`.

`analyze` **no** renderiza los diez archivos fijos de documentación técnica, **no** escribe un
`RUN_SUMMARY`, y nunca contacta a un proveedor de IA — no existe ninguna opción `--allow-ai-interpretation`
en `analyze`. Su código de salida siempre es `0` (`EXIT_SUCCESS`); una excepción inesperada se propaga y
termina el proceso en lugar de convertirse en un resultado estructurado `PARTIAL`/`FAILED` — `analyze` no
usa en absoluto el modelo de etapas/`RunResult` (`RunResult(command="analyze", status=RunStatus.SUCCESS)` se
reporta incondicionalmente al retornar). `analyze` nunca modifica el repositorio analizado.

Use `analyze` cuando necesite específicamente la forma de salida pre-V4.2 y ninguno de los comportamientos
adicionales de documentación/resiliencia/resumen de `full`.

## 4.5 `full`

`full` (`legacy_documenter/cli/full_pipeline.py::run_full_pipeline`, enrutado vía
`legacy_documenter/cli/router.py::_route_full`) es el valor por defecto recomendado. Ejecuta las mismas
etapas deterministas que `analyze`, más:

- **Orquestación resiliente a nivel de etapa.** Cada etapa — `SCAN, EXTRACTION, CALL_RESOLUTION,
  WEB_ENTRY_RESOLUTION, DATABASE_RESOLUTION, FLOW_RESOLUTION, DEPENDENCY_RESOLUTION, EXPORT, CONTEXT,
  DOCUMENTATION` — está envuelta de modo que el fallo de una etapa no aborta las etapas que no dependen de
  ella. Una etapa cuya etapa ascendente requerida falló se reporta como `SKIPPED_DUE_TO_UPSTREAM_FAILURE`,
  nunca omitida en silencio (`legacy_documenter/cli/stage_identity.py`).
- **Documentación técnica** (etapa `DOCUMENTATION`): renderiza diez documentos Markdown fijos más una
  página de navegación `documentation/README.md` — ver §4.8.
- **Un resumen de ejecución**: `RUN_SUMMARY.json` y `RUN_SUMMARY.md` bajo `--output`, siempre escritos,
  registrando el resultado de cada etapa más los campos del límite de aprobación (`ai_invoked`,
  `canonical_knowledge_produced`, `technical_lead_approval`, `ai_requested`, `proposal_count`,
  `proposal_review_status`, `next_action`, `output_locations`).
- **Interpretación por IA y generación de propuestas, opcionales** — ver §4.7.

Sin `--allow-ai-interpretation`, `full` hace **cero** llamadas a IA/proveedor — exactamente igual que
`analyze`.

Ejemplo de contención de fallos: si `WEB_ENTRY_RESOLUTION` falla, `DATABASE_RESOLUTION` (que no depende de
ella) sigue ejecutándose; `FLOW_RESOLUTION` (que depende de ambas) se omite y se reporta como tal; `EXPORT`
y `DOCUMENTATION` siguen ejecutándose sobre lo que las etapas exitosas produjeron — un árbol de salida
parcial pero honesto, nunca un fallo total ni datos fabricados para la pieza faltante
(`legacy_documenter/cli/full_pipeline.py::_assemble_indexes`: "Un campo cuya etapa productora falló o fue
omitida es un contenedor vacío — un honesto 'no se produjo nada', nunca datos inventados").

## 4.6 `readiness`

`python main.py readiness` **no** analiza ningún repositorio suministrado por el usuario. Valida los propios
requisitos previos internos de preparación de conocimiento de LegacyMapper — una puerta fija y
autorreferencial definida en `legacy_documenter/knowledge/readiness.py` (originada en V3-R9) que verifica la
propia documentación funcional/técnica aprobada de la era V3 de LegacyMapper
(`output/LEVANTAMIENTO_FUNCIONAL.md`, `output/LEVANTAMIENTO_TECNICO.md`), su propio registro de revisión
humana (`codex/V3/V3_R8_4_REVISION_HUMANA_APROBADA.md`), y su propia evidencia de arquitectura
(`output/v3_r8_1/ARCHITECTURE_EVIDENCE.json`) para verificar consistencia interna, cierre de evidencia y
ausencia de valores con forma de secreto. `READY` significa que `preconditions`, `claim_integrity`,
`evidence_closure`, `quantitative_integrity`, `architecture_integrity`, `knowledge_projection`,
`knowledge_boundary` y `security` pasaron todos. Esta es una autoverificación de continuidad del proyecto,
no una señal de preparación por ejecución sobre el repositorio al que se apunta `analyze`/`full`.

**Comportamiento en clon nuevo**: `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` es una excepción pequeña
(~1.8 KiB) deliberadamente rastreada dentro del directorio, de otro modo excluido, `/output/v3_r8_1/` — una
excepción estrecha en `.gitignore`, no un volcado operacional restaurado. Contiene solo los cuatro conteos
agregados estructurales `DETERMINISTIC_INDICATORS` y la conclusión de arquitectura, provenientes del ya
rastreado y aprobado por humanos `codex/v3/V3_R8_1_DEEP_SOURCE_ANALYSIS_RESULTADO.md`; no lleva código
fuente, ni rutas de archivo fuente, ni credenciales, ni datos personalmente identificables. En un clon nuevo,
`python main.py readiness` ahora tiene éxito: `código de salida 0`, `readiness: READY`, las ocho
verificaciones en `true`, `provider_calls: 0`, `real_llm_calls: 0`. Note que este archivo no puede
*regenerarse* solo a partir del repositorio — sus valores originales dependieron de un escaneo real de un
repositorio legado; está rastreado precisamente porque ese escaneo no es repetible a partir de las entradas
rastreadas. Deuda residual de endurecimiento (no implementada): `legacy_documenter/knowledge/readiness.py`
todavía asume que este archivo rastreado existe; si se elimina o corrompe manualmente, el comportamiento
actual puede aún lanzar una excepción no controlada en lugar de un resultado `BLOCKED` controlado. Ver el
Manual Técnico §20 para más detalle.

## 4.7 Interpretación por IA

La interpretación por IA está **desactivada por defecto** y solo es alcanzable desde `full` vía
`--allow-ai-interpretation`. `analyze` nunca puede activarla — la opción no existe en ese subcomando.

Lo que ocurre realmente cuando se habilita (`legacy_documenter/orchestration/ai_interpretation.py`):

- Una etapa `AI_INTERPRETATION` se ejecuta solo si la etapa `CONTEXT` ya tuvo éxito en *esta* ejecución —
  lee exclusivamente de `<output>/ai_context/*.json`, escrito momentos antes por la misma ejecución, nunca
  una instantánea histórica ni la salida de otra ejecución.
- Al proveedor se le pide que reformule/explique únicamente la evidencia adjunta, bajo una instrucción de
  sistema que prohíbe inventar relaciones o significado de negocio y que exige que cada hallazgo cite ids de
  referencia de evidencia que estén realmente presentes en el propio paquete de contexto de la ejecución
  actual (`legacy_documenter/orchestration/ai_interpretation.py::SYSTEM_INSTRUCTION`, `_validate_findings`).
- Si `PROPOSAL_GENERATION` también tiene éxito, los hallazgos se convierten en registros `Proposal`
  escritos en `output/proposals/AI_PROPOSALS.json` (autoritativo) y
  `output/proposals/AI_PROPOSALS_PENDING_REVIEW.md` (legible por humanos), cada uno con
  `status = PENDING_TECHNICAL_LEAD_REVIEW` — **nunca** aprobado automáticamente.
- La resolución del proveedor (`_resolve_provider`) lee `LEGACYMAPPER_LLM_PROVIDER` (por defecto `COPILOT`),
  `LEGACYMAPPER_LLM_PROVIDER_ID` y `LEGACYMAPPER_LLM_MODEL` del entorno y construye un proveedor real a
  través de `ProviderRegistry`. **`ProviderRegistry.create` actualmente solo reconoce `"FAKE"` y
  `"COPILOT"`** (`legacy_documenter/llm/core.py::ProviderRegistry.create`) — existe una clase
  `GeminiProvider` (`legacy_documenter/llm/providers/gemini.py`) pero no está registrada ni es alcanzable
  por esta ruta; ver el Manual Técnico §13 y la nota de discrepancia en el documento de resultado.
- Cualquier invocación real de producción de `--allow-ai-interpretation` resuelve y puede llamar a un
  proveedor real. **No** ejecute `full ... --allow-ai-interpretation` para verificación manual — use
  `python -m tools.manual_verify_full_pipeline <repositorio> --output <dir> --allow-ai-interpretation`
  (siempre inyecta `FakeLLMProvider`), o la suite de tests automatizada, que además falla ruidosamente si
  alguna ruta de test alcanza inesperadamente la resolución de un proveedor real (`AGENTS.md`,
  "Manual AI-Path Verification").

## 4.8 Navegación de la salida

Bajo `--output` (solo para `full`; `analyze` solo escribe `index/` y `context/`):

```
<output>/
  index/                     índices JSON deterministas (ambos comandos)
  context/                   artefactos de contexto adyacentes a ai_context/ (ambos comandos)
  ai_context/                paquete de evidencia de la ejecución actual para AI_INTERPRETATION (solo full)
  documentation/
    README.md                documento de navegación de nivel superior V4.2-R8
    PROJECT_OVERVIEW.md
    SOLUTION_STRUCTURE.md
    PROJECT_DEPENDENCIES.md
    WEBFORMS_MAP.md
    CONFIGURATION_SUMMARY.md
    ANALYSIS_WARNINGS.md
    WEB_ENTRY_POINTS.md
    FUNCTIONAL_FLOWS.md            documento de navegación/resumen
    DATABASE_ACCESS.md             documento de navegación/resumen
    UNRESOLVED_FINDINGS.md         documento de navegación/resumen
    functional_flows/<nombre-seguro>.md    particiones de detalle, una por grupo semántico
    database_access/<nombre-seguro>.md     particiones de detalle
    unresolved_findings/<nombre-seguro>.md particiones de detalle
  proposals/                 solo si se pasó --allow-ai-interpretation
    AI_PROPOSALS.json
    AI_PROPOSALS_PENDING_REVIEW.md
  RUN_SUMMARY.json            solo full
  RUN_SUMMARY.md              solo full
```

Los diez documentos de nombre fijo son históricos: seis de `MarkdownExporter`
(`legacy_documenter/exporters/markdown_exporter.py` — `PROJECT_OVERVIEW.md`, `SOLUTION_STRUCTURE.md`,
`PROJECT_DEPENDENCIES.md`, `WEBFORMS_MAP.md`, `CONFIGURATION_SUMMARY.md`, `ANALYSIS_WARNINGS.md`) y cuatro de
`TechnicalDocumentationRenderer`
(`legacy_documenter/exporters/technical_documentation_renderer.py` — `WEB_ENTRY_POINTS.md`,
`FUNCTIONAL_FLOWS.md`, `DATABASE_ACCESS.md`, `UNRESOLVED_FINDINGS.md`).

V4.2-R8 añadió una división navegación/detalle para los tres documentos que crecieron a un tamaño
inmanejable a escala de repositorio real durante el piloto real de V4.2-R7 (`FUNCTIONAL_FLOWS.md`,
`DATABASE_ACCESS.md`, `UNRESOLVED_FINDINGS.md`): el documento de nombre fijo ahora es un resumen/índice
pequeño, y el detalle completo se divide por grupo semántico (típicamente por proyecto) en archivos
`documentation/<raíz-doc-minúscula>/<nombre-seguro>.md` con nombres deterministas y seguros para el sistema
de archivos (`legacy_documenter/exporters/_documentation_partitioning.py::sanitize_label`) — nunca derivados
de contenido de IA, una marca de tiempo, ni de la función `hash()` aleatorizada de Python. `documentation/README.md`
es el único punto de entrada que enlaza a cada documento fijo e indica si fue particionado.

`WEB_ENTRY_POINTS.md` y `PROJECT_DEPENDENCIES.md` siguen siendo documentos planos únicos; el particionado
impulsado por escala para ellos fue evaluado y deliberadamente dejado abierto
(`PROJECT_STATE.json: documentation_remaining_scale_debt`, `"OPEN_IF_FUTURE_SCALE_REQUIRES"` para ambos) —
ver Manual Técnico §20.

## 4.9 Códigos de salida

Contrato autoritativo (`legacy_documenter/cli/router.py`, reafirmado en V4.2-R5.1 sobre un borrador
anterior incorrecto en el documento de prompt de V4.2-R5):

| Código | Significado | Aplica a |
|---|---|---|
| `0` | `SUCCESS` | `analyze` (siempre), `full`, `readiness` |
| `1` | `PARTIAL` | `full`, `readiness` |
| `2` | `USAGE` | Error de uso propio de argparse (comando desconocido, argumento faltante) — no asignado por código de aplicación, producido por `argparse` mismo |
| `4` | `FAILED` | `full` |

`3` (un marcador de posición `NOT_IMPLEMENTED_FOR_R1` de la era R1) está retirado y deliberadamente nunca
reutilizado.

El estado de `full` se calcula de forma no subjetiva
(`legacy_documenter/cli/full_pipeline.py::_compute_status`): `FAILED` a menos que tanto `EXTRACTION` como
`EXPORT` hayan tenido éxito; en otro caso `PARTIAL` si existe algún error de extracción por archivo,
cualquier etapa `FAILED`, o cualquier etapa `SKIPPED_DUE_TO_UPSTREAM_FAILURE`; en otro caso `SUCCESS`.

## 4.10 Reejecución / recuperación

Reejecutar `full` (o `analyze`) sobre el mismo directorio `--output` es seguro:

- `index/`, `documentation/` (incluyendo sus subdirectorios de partición de R8), `context/` y `ai_context/`
  se sobrescriben íntegra e incondicionalmente por la etapa que los posee, cada vez que esa etapa se
  ejecuta.
- Un par `proposals/` obsoleto de una ejecución anterior sobre el mismo directorio se elimina
  incondicionalmente *antes* de que se ejecute cualquier etapa de la nueva ejecución
  (`legacy_documenter/cli/artifact_lifecycle.py::reset_stale_proposal_artifacts`) — las propias etapas
  `AI_INTERPRETATION`/`PROPOSAL_GENERATION` de esta ejecución lo reescriben desde cero solo si realmente
  producen salida, de modo que una reejecución sin `--allow-ai-interpretation` nunca deja las propuestas de
  una ejecución previa pareciendo vigentes.
- Un archivo de partición obsoleto que quedó de una ejecución previa cuyos grupos semánticos han cambiado
  desde entonces se elimina como parte del renderizado particionado (el particionado determinista siempre
  refleja únicamente los grupos de la ejecución actual).
- Un archivo creado por el usuario colocado dentro de un directorio generado (por ejemplo, una nota
  dejada en `documentation/`) se preserva — solo se tocan los nombres de archivo fijos y generados y los
  archivos de partición.
- El repositorio fuente analizado nunca es modificado, renombrado ni escrito por ningún comando
  (`AGENTS.md`, "Legacy Source Repository").

## 4.11 Salida de sistema real

Según la sección "Real-System Operational Output" de `docs/GENERATED_ARTIFACT_POLICY.md`: los resultados de
ejecutar LegacyMapper contra un sistema legado real concreto (un piloto, un análisis ad-hoc para un cliente)
son salida operacional, no fuente del proyecto, y **deben permanecer locales y nunca deben confirmarse
(commit)**, sin importar su tamaño. La convención para una nueva ejecución de este tipo es
`output/_local_<nombre-descriptivo>/`, ya cubierta por una regla genérica de `.gitignore`
(`/output/_local_*/`) sin necesidad de editar `.gitignore`. Si en su lugar se usa un directorio con nombre
formal, la regla de ruta explícita correspondiente en `.gitignore` debe añadirse en el mismo cambio que crea
el directorio (como se hizo para `output/v4_2_r7_ist_operacional/`, el piloto real de IST de V4.2-R7). Todo
lo que de una ejecución de sistema real importe para la historia del proyecto debe destilarse en
documentación pequeña rastreada, tests o fixtures sintéticos (por ejemplo,
`tests/test_v4_2_r7_synthetic_full_fixture.py`) antes de descartar la salida operacional cruda — nunca
resuelto ignorando globalmente `output/`, que también contiene contratos, baselines y manifiestos
rastreados.

## 4.12 Límite de aprobación

**Implementado hoy:**

- Análisis determinista, documentación técnica e interpretación por IA (opcional) que produce propuestas
  para revisión humana, como se describió arriba.
- Las propuestas siempre se escriben como `PENDING_TECHNICAL_LEAD_REVIEW`; `RunResult.canonical_knowledge_produced`
  y `RunResult.technical_lead_approval` son `false` en toda ejecución de V4.2, sin excepción.
- Un diseño documentado (no implementado) de superficie de aprobación:
  `docs/V4_2/V4_2_APPROVAL_SURFACE_DESIGN.md`, `IMPLEMENTATION_STATUS=NOT_IMPLEMENTED`.

**No implementado en V4.2** (`PROJECT_STATE.json`: `approval_surface_implementation = NOT_IMPLEMENTED`,
`plugin_runtime = NOT_IMPLEMENTED`):

- No existe ningún comando CLI `approve` / `reject` / `request-correction`.
- No existe ningún mecanismo de aprobación vinculado a `run_id`.
- No existe ninguna promoción automática de una propuesta a conocimiento canónico.
- Los subpaquetes de conocimiento que modelan la composición canónica, la aprobación y la proyección hacia
  el Plugin (`legacy_documenter/knowledge/canonical/`, `approval/`, `plugin_projection/`, `projection/`)
  existen como código de *dominio/contrato* probado y reutilizable, pero `full`/`analyze`/`readiness` nunca
  los invocan — no hay ningún flujo orquestado de extremo a extremo "R11/R12" alcanzable desde la CLI
  después de que se genera una propuesta.
- No existe ningún runtime de Plugin que consuma cargas útiles `LegacyMapperPluginKnowledge` en tiempo de
  ejecución.

Toda propuesta que LegacyMapper produce requiere una decisión humana del Líder Técnico, tomada fuera de esta
herramienta, antes de que pueda informar cualquier cosa posterior.

## 4.13 Solución de problemas

| Síntoma | Causa probable | Evidencia |
|---|---|---|
| `python main.py readiness` lanza `FileNotFoundError` para `output/v3_r8_1/ARCHITECTURE_EVIDENCE.json` (no debería ocurrir en un clon normal; este archivo ahora está rastreado) | El archivo fue eliminado manualmente, o `/output/v3_r8_1/` se re-excluyó por completo localmente. `readiness.py` todavía asume que el archivo rastreado existe y aún no degrada a un resultado `BLOCKED` controlado si falta — registrado como deuda residual de endurecimiento, no implementada en esta ronda. | `legacy_documenter/knowledge/readiness.py::_execute`; ver §4.6 y el Manual Técnico §20. |
| `full --allow-ai-interpretation` alcanza inesperadamente un cliente de IA real durante pruebas manuales | `_resolve_provider()` siempre resuelve un proveedor real (`COPILOT` por defecto) a menos que se inyecte uno. | `legacy_documenter/orchestration/ai_interpretation.py::_resolve_provider`; `AGENTS.md`, "Manual AI-Path Verification". Use `tools/manual_verify_full_pipeline.py` en su lugar. |
| `full` reporta `PARTIAL` con una etapa `SKIPPED_DUE_TO_UPSTREAM_FAILURE` | Una etapa de dependencia ascendente falló; el `StageError.message` de la etapa omitida la nombra explícitamente. | `legacy_documenter/cli/full_pipeline.py::_skipped`; inspeccione `RUN_SUMMARY.json`. |
| `full` reporta `FAILED` | `EXTRACTION` o `EXPORT` no tuvo éxito — no existe ningún paquete de análisis mínimamente útil. | `legacy_documenter/cli/full_pipeline.py::_compute_status`. |
| Código de salida `2` sin ningún `RunResult` impreso | Este es un error de uso propio de argparse (argumentos incorrectos/faltantes), no un resultado a nivel de aplicación. | Comentario sobre las constantes `EXIT_*` en `legacy_documenter/cli/router.py`. |
| `documentation/FUNCTIONAL_FLOWS.md` (etc.) se ve corto/vacío comparado con lo esperado | V4.2-R8 lo convirtió en un resumen de navegación; el detalle está bajo `documentation/functional_flows/<nombre-seguro>.md`. | §4.8; `docs/V4_2/V4_2_R8_DOCUMENTATION_AT_SCALE_FINAL_BASELINE_AND_CLOSURE_PREPARATION_RESULT.md`. |
| `UNRESOLVED_FINDINGS.md` contiene ruido de código repetitivo `InitializeComponent()` | Observación conocida y preservada (F-06), no un bug — el código generado por el diseñador de WebForms no se filtra de forma especial. | `docs/V4_2/V4_2_R7_1_FINDINGS_VERIFICATION.md`. |
| Un flujo derivado de `WebEntryResolver` carece de `outgoing_calls` para un manejador vinculado desde el marcado | Observación conocida y preservada (F-07) — `WebEntryResolver` no adjunta `outgoing_calls` a los puntos de entrada vinculados desde el marcado. | Mismo documento; `tests/test_v4_2_r7_synthetic_full_fixture.py::FunctionalFlowTests`. |
