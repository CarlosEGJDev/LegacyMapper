# LegacyMapper — V5 CLOSED (tag `v5`)

Principio: **Python descubre y resuelve hechos; la IA interpreta después.** El análisis es determinista; la IA es opcional, propone y nunca decide.

## Qué es V5

LegacyMapper V5 está **cerrada** (baseline de release en `docs/V5/V5_FINAL_BASELINE.json`). Contiene:

* Pila principal: **VB.NET WebForms / Oracle** (adapter `vbnet-webforms-oracle` 1.0), validada contra el repositorio IST sin diferencias.
* Segunda tecnología: **Python generic** (adapter `python-generic` 1.0), como **piloto**.
* Evidence normalizada neutral a la tecnología, documentación humana, cache de extracción incremental, contrato de proveedor de IA (propuestas), segmentación determinista de flujos, revisión humana auditada, conocimiento canónico y contratos de consumers/plugins.

**Aviso — piloto circular:** el piloto Python se ejecutó sobre el propio código de LegacyMapper (`SELF_HOSTED_CIRCULAR`). No es un producto externo independiente; `external_independence_claim=false`. La validación externa independiente queda como trabajo futuro.

## Límites que se mantienen

* **Plugin Contract ≠ Plugin Runtime.** Existe el contrato declarativo de solo lectura; el runtime de plugins **no está implementado** y los manifiestos nunca se ejecutan.
* **Sin aprobación ni canonicalización automáticas.** Una propuesta de IA solo pasa a conocimiento canónico por decisión humana explícita.
* La IA real nunca se invoca por defecto; la fuente legada es de solo lectura.

## Dónde leer

* Estado operativo actual (autoridad): `PROJECT_STATE.json`
* Auditoría y baseline final: `docs/V5/V5_FINAL_AUDIT_AND_RELEASE_BASELINE.md`, `docs/V5/V5_FINAL_BASELINE.json`
* Uso: `docs/V5/V5_OPERATIONS_GUIDE.md`
* Cierre formal: `docs/V5/V5_FINAL_CLOSURE.md`
* Historia y continuidad: `docs/continuity/LEGACYMAPPER_PROJECT_HISTORY_AND_V5_ROADMAP.md`; lecciones: `docs/continuity/LEGACYMAPPER_LESSONS_LEARNED.md`
* Siguiente iniciativa (post-V5, planificada): `docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md`
* Roadmap e historia: `docs/continuity/LEGACYMAPPER_V5_ROADMAP.md`
* Recuperación desde un checkout nuevo: `docs/PROJECT_RECOVERY.md`
* Reglas para agentes: `AGENTS.md`, `CLAUDE.md`

## IA sobre un output ya generado (post-V5 H1)

`python main.py interpret <output-existente>` ejecuta solo la interpretación de IA + propuestas sobre un output determinista válido, **sin reescanear el repositorio** ni reconstruir Evidence (ver `docs/V5/V5_OPERATIONS_GUIDE.md` §11). Las propuestas nunca son canónicas.

## Documentación humana por audiencia (post-V5 H2)

`python main.py docs <output-existente>` genera, desde la evidencia ya persistida (sin reescanear ni llamar a IA), tres vistas del mismo sistema: **executive**, **functional** y **technical_overview** (`docs/V5/V5_OPERATIONS_GUIDE.md` §12). Lo confirmado, lo inferido, lo no resuelto y las interpretaciones de IA se distinguen con etiquetas.

## Proyecciones visuales (post-V5 H3)

`python main.py visuals <output-existente>` genera diagramas SVG determinísticos (mapa del sistema, capas, dependencias, flujo observable e interacción con datos) con su modelo JSON y un manifest, desde la evidencia ya persistida; sin reescanear ni llamar a IA (`docs/V5/V5_OPERATIONS_GUIDE.md` §13).

## Verificación rápida

```text
python -X utf8 -m unittest discover -s tests
```

## Entregables humanos finales (post-V5 H4)

> **Estado actual:** Post-V5 H4 está **CERRADO** (H1–H4 cerrados; H5 `NOT_STARTED`; V6 `NOT_STARTED`). El estado vigente de la iniciativa se mantiene en [`HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md`](docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md) y `PROJECT_STATE.json`.

`python main.py deliver <output-existente>` empaqueta, desde la línea base ya persistida (sin reescanear ni llamar a IA), un sitio **HTML estático y portable** (ejecutivo / funcional / técnico, las diez superficies de entrega y los diagramas H3) y cuatro **PDF** secundarios; se abre `index.html` desde el disco, sin servidor (`docs/V5/V5_OPERATIONS_GUIDE.md` §14).

## Plantillas humanas (post-V5)

`legacy_documenter/templates/human/<nombre>/` (plantillas integradas, viajan con el paquete) define el diseño del documento de comportamiento (contrato `LegacyMapperHumanTemplate 1.0`): orden de secciones, tipografía, índice y aviso de IA.
La plantilla controla presentación, nunca la verdad (`python -m legacy_documenter.behavior.prototype … --template human/default [--template-dir <dir>]`; ver `legacy_documenter/templates/human/README.md`).
`legacy_documenter/templates/ai/` está reservado (sin implementación).
Pulido final: título/subtítulos centrados, párrafos justificados, SVG con texto contenido y un único aviso de IA (bloque `layout:` de `template.yaml`).

## Portabilidad y contrato de rutas (pre-H5 Gate A)

LegacyMapper depende de entradas explícitas y de recursos empaquetados, nunca de la máquina o carpeta donde se desarrolló:

* `full`/`analyze` validan la ruta fuente (existe, es directorio, es legible) y la de salida (creable/escribible, sin solaparse con la fuente) **antes** de escanear, analizar o tocar un proveedor; una ruta inválida devuelve exit code `4` con un JSON `PATH_CONTRACT_VIOLATION` en stderr y no escribe nada (cierra UX-01). Contrato único: `legacy_documenter/utils/path_contract.py`.
* Las plantillas humanas integradas viven dentro del paquete (`legacy_documenter/templates/`); funcionan desde cualquier cwd, instalación de solo lectura o copia del paquete. `--template-dir` es una anulación externa que nunca modifica la integrada.
* La IA es opcional: `full`, `docs`, `visuals` y `deliver` nunca resuelven un proveedor; `interpret` sin SDK/configuración devuelve un error controlado (`PROVIDER_UNAVAILABLE` / `PROVIDER_CONFIGURATION_ERROR`, exit 1) sin tocar la línea base. La ubicación del ejecutable del proveedor la resuelve el propio SDK (`COPILOT_CLI_PATH`/PATH); LegacyMapper no busca en directorios de desarrollo.
* Detalle y evidencia: `docs/POST_V5/PRE_H5_GATE_A_PORTABILITY_RESULT.md`.

### Distribución instalable (pre-H5 Gate A.1)

`pyproject.toml` empaqueta `legacy_documenter` (plantillas y recursos incluidos, sin dependencias requeridas): `pip install <wheel>` en un entorno aislado y luego `legacymapper <comando> …` o `python -m legacy_documenter <comando> …` desde cualquier carpeta. `python main.py …` sigue funcionando desde el checkout.
`python -m legacy_documenter.behavior.prototype` ya no asume ningún proyecto: exige `--project`/`--solution` salvo que exista un único candidato (códigos `PROJECT_SELECTION_REQUIRED`, `NO_BEHAVIORAL_PROJECT_CANDIDATES`, …), y `output-manifest` sobre una ruta inválida devuelve exit 4 con JSON, sin traceback.
Detalle: `docs/POST_V5/PRE_H5_GATE_A1_DISTRIBUTION_CLOSURE_RESULT.md`.

### UI / navegación / estilos en Evidence Core (pre-H5 Gate B)

El análisis persiste, una sola vez, la estructura de pantallas, navegación, mensajes, parámetros, estilos y activos como particiones `evidence/ui_*.json` (`ui_evidence_schema_version 1.0`, aditivo; el esquema Core no cambia). La documentación conductual, el contexto de IA y las plantillas leen solo esa evidencia: `python -m legacy_documenter.behavior.prototype <baseline> --output <dir>` ya no necesita la fuente (`--source` está obsoleto e ignorado). Una línea base anterior sin `ui_*` falla de forma explícita (`UI_EVIDENCE_MISSING`): re-ejecute `analyze`/`full` una vez. El manifiesto añade `source_provenance` (identidad lógica, independiente de la ruta física).
Detalle: `docs/POST_V5/PRE_H5_GATE_B_EVIDENCE_CORE_RESULT.md`.

### Cierre del Evidence Core (pre-H5 Gate B.1)

La UI Evidence pasa a esquema `1.1`: activos `~/` resueltos contra la raíz de aplicación, aristas menú/config → vista, perfiles de estilo compartidos (−38 % de tamaño en IST), identidad portable (`portable_evidence_sha256`, `logical_snapshot_sha256`) y sin ciclos en `behavior/`. Una línea base de Gate B (UI `1.0`) requiere re-ejecutar `analyze`/`full`. `source_snapshot_sha256` queda documentado como constante histórica.
Detalle: `docs/POST_V5/PRE_H5_GATE_B1_EVIDENCE_CORE_CLOSURE_RESULT.md`.

### Endurecimiento final pre-H5 (Gate C)

La etapa de resolución de llamadas refina, de forma determinista y conservadora, las llamadas entre proyectos (referencias directas, `Imports`, aridad de sobrecargas, interfaces, frontera de ensamblados externos) y persiste el resultado en `evidence/cross_project_calls.json`; lo no probable queda `UNRESOLVED`. Hay una segunda plantilla humana (`--template human/executive`) con el mismo modelo y distinta presentación; ninguna plantilla puede ocultar lo no resuelto. El CLI de consumers queda como capacidad futura (UX-03). `ANALYZER_VERSION` = 4: las líneas base anteriores requieren re-análisis.
Detalle: `docs/POST_V5/PRE_H5_GATE_C_FINAL_HARDENING_RESULT.md`.

## Historia

V4.3 (plan de ejecución en `docs/V4_3/V4_3_EXECUTION_PLAN.md`, prompts R0–R9) y V1–V4 se conservan como historia y compatibilidad. No hay V6 iniciada; el siguiente paso es `POST_V5_PLANNING`.
