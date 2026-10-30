# LegacyMapper V5 — Guía operativa mínima

Esta guía describe solo comandos y comportamientos verificados en V5 Closure R1 (`python main.py --help`, subcomandos y la suite). No hay CLI para los consumers: se usan como API Python.

## 0. Cuatro cosas que nunca se mezclan

```text
Evidence determinista  → lo produce Python (analyze / full). Es la verdad observada.
Propuesta de IA        → opt-in; siempre «pendiente de revisión»; nunca verdad.
Decisión humana        → APPROVE / REJECT / CORRECT / DEFER, con revisor explícito.
Conocimiento canónico  → solo nace de APPROVE o CORRECT humanos; nunca automático.
```

## 1. Analizar un repositorio

```text
python main.py analyze <repo> --output <dir>          # análisis determinista (index/, evidence/, ai_context/…)
python main.py full    <repo> --output <dir>          # lo anterior + documentación + RUN_SUMMARY (recomendado)
python main.py <repo> --output <dir>                   # atajo heredado de `analyze`
```

Opciones comunes: `--exclude <carpeta>` (repetible, por nombre de carpeta), `--flow-max-depth N` (12 por defecto), `--verbose`, `--repository-id <nombre>`. `full` añade `--long-paths` (Windows, rutas > 260), `--cache-mode {auto,off,refresh}`, `--cache-dir`, `--verify-cache`, `--trust-mtime` (inseguro, opt-in), `--incremental-max-changed-ratio`.

- **IST / VB.NET WebForms-Oracle:** el comportamiento por defecto (adapter `vbnet-webforms-oracle` 1.0, seleccionado por los tipos de archivo observados). Sin `--repository-id`, los ids son los de V5.1.
- **Python:** el adapter `python-generic` 1.0 se selecciona solo cuando el repositorio contiene archivos `.py` y ningún tipo VB/WebForms. Un repositorio mixto (VB + Python) falla con «ambiguo»; use `--exclude` para separar (p. ej. carpetas de fixtures).
- **`--repository-id`:** nombre lógico (no una ruta; solo `[A-Za-z0-9._:-]`, hasta 128 caracteres). Si lo declara, los `SourceArtifact` quedan namespaced por ese nombre y dos repositorios con las mismas rutas relativas nunca comparten ids. **Recomendado siempre que compare o junte evidencia de repositorios distintos.** Es opcional; sin declarar, el espacio es el heredado V5.1.
- El análisis es estático: **no** ejecuta, importa ni compila el código analizado, no usa red y no escribe en el repositorio fuente.

## 2. Documentación humana

`full` genera `<output>/documentation_v52/` (perfiles `general/` = `human-functional` y `developer/` = `human-technical`) y `<output>/ai_context/`. Los mismos templates y renderer sirven a toda tecnología; el vocabulario por tecnología es un overlay de datos. `<output>/documentation/` es el árbol histórico (V3/V4). Un template cambia la presentación, nunca la evidencia.

## 3. Incremental / cache

Por defecto `--cache-mode auto`: la cache vive en `<output>/_cache_v53`; si la corrida anterior es compatible reutiliza la extracción de los archivos sin cambios (una segunda corrida sin cambios produce exactamente la misma salida; un cambio de un archivo re-extrae solo ese). Se invalida sola ante cambios del código del analizador (fingerprint), de opciones de análisis o del contrato. `--cache-mode off` ignora la cache; `refresh` la reconstruye. Todas las etapas posteriores a la extracción se recalculan siempre (el scope incremental informa y puede decir `mode=full` para cambios de código: es conservador, no un error). Use un `--output` por repositorio.

## 4. IA: cómo activarla con seguridad

Por defecto **no hay llamadas a IA ni a providers**. `--allow-ai-interpretation` (solo con `full`) añade un paso de interpretación sobre la evidencia de esa corrida y puede contactar al provider configurado (hoy Copilot local). Las propuestas se escriben en `<output>/proposals/` con estado `READY_FOR_REVIEW` y envelope `PENDING_TECHNICAL_LEAD_REVIEW`; nada se aprueba ni se vuelve canónico. Para probar el camino con IA sin riesgo, use `python -m tools.manual_verify_full_pipeline <repo> --output <dir> --allow-ai-interpretation`, que inyecta un provider Fake y no puede alcanzar uno real. Un flujo demasiado grande para la ventana del provider se segmenta (cada segmento es `partial=true` con `parent_flow_id`, `segment_id`, `included_paths`, `omitted_paths`, `evidence_refs`); si ni un segmento cabe, falla con error explícito, nunca se trunca en silencio.

## 5. Revisión y conocimiento canónico

```text
python main.py review list      --output <dir>
python main.py review prepare   --output <dir> --reviewer "<persona>" [--proposal PRP-…]
python main.py review decide    --output <dir> --proposal PRP-… --action {APPROVE,REJECT,CORRECT,DEFER} --reviewer "<persona>" [--rationale …] [--correction-file x.json] [--expected-evidence-fingerprint …]
python main.py review canonical --output <dir> [--id CAN-… [--chain] | --proposal PRP-… | --evidence-ref …]
```

- `prepare` fija el **baseline** (huella de la propuesta + huella de la evidencia que cita); es obligatorio antes de la primera decisión. El baseline demuestra estabilidad **entre `prepare` y la decisión**; las propuestas no llevan evidencia de generación, así que no se afirma inmutabilidad desde que la IA las generó.
- Si la evidencia cambia después de `prepare`, la decisión falla con `PROPOSAL_STALE` y no se escribe nada. Una propuesta alterada falla `PROPOSAL_TAMPERED`.
- `--reviewer` es obligatorio, sin valor por defecto; rechaza nombres automáticos (`AUTO`, `system`, `ai`, `llm`, el provider o modelo de la propuesta).
- APPROVE/CORRECT crean un registro canónico (`knowledge/canonical/CAN-*.json`) con cadena de auditoría (canónico → decisión → snapshot de la propuesta → baseline → evidencia); REJECT y DEFER nunca crean canónico. Un `full` posterior no borra `knowledge/`.

## 6. Cómo leen los consumidores

La facade `legacy_documenter.consumers.facade.ConsumerFacade(<output>, registry=None).handle(<request dict>)` (Python; **no hay comando de CLI**) es de solo lectura y devuelve un `ConsumerResult` versionado (contrato 1.0). Capabilities: `READ_EVIDENCE`, `READ_FLOW`, `READ_PARTIAL_FLOW`, `READ_AI_CONTEXT`, `READ_CANONICAL`, `READ_REVIEW_HISTORY`, `RENDER_HUMAN_DOC` (`human-functional` / `human-technical`), `EXPORT_JSON`. La salida es determinista (mismo request + mismos artifacts → mismos bytes); los errores son códigos contractuales (`ENTITY_NOT_FOUND`, `PARTIAL_NOT_SUPPORTED`, `READ_ONLY_VIOLATION`…). Las capabilities de escritura no existen.

## 7. Qué significa el Plugin Contract

`Plugin Contract ≠ Plugin Runtime`. Hoy solo existe un **manifest declarativo** (`legacy_documenter.plugins.validation.validate_manifest`) que se valida contra el contrato de consumidores (compatibilidad de versión mayor, capabilities conocidas, solo lectura) y se convierte en un descriptor. Nada se carga, importa, instala ni ejecuta; `entrypoint_metadata` es texto inerte.

## 8. Qué NO está implementado

Plugin Runtime (descubrimiento, carga, instalación, sandbox, firma, hot reload, registry remoto); capabilities de escritura para consumidores; UI de revisión, RBAC, firmas, quórum o aprobación masiva; interpretación de IA integrada en la documentación humana; inferencia de tipos rica, `argparse`/console scripts, drivers de base de datos y decoradores en Python; validación de una segunda tecnología sobre un producto externo independiente (el piloto Python es **circular**: analiza una copia congelada de LegacyMapper); tercera tecnología; V6.

## 9. Comandos auxiliares

`python main.py readiness` (valida los prerrequisitos de conocimiento del propio proyecto); `python main.py output-manifest <dir>` (escribe `OUTPUT_MANIFEST.json` con ruta/tamaño/SHA-256 de una corrida terminada); pruebas: `python -X utf8 -m unittest discover -s tests`.

## 10. Actualización post-V5 (09-10-2026)

**Modelo de ejecución verificado en clean-room:** código fuente, `python main.py <comando>`, sin `pyproject.toml` ni dependencias de terceros; release extraído con `git archive v5`, `.venv` propio, sin imports desde el repo de desarrollo. Comandos públicos: `analyze`, `full`, `readiness`, `output-manifest`, `review {list,prepare,decide,canonical}`; IA solo con `full --allow-ai-interpretation`. **No hay CLI de consumers** (solo la API Python).

Ejemplo PowerShell desde `app\` con un venv hermano (ruta relativa correcta `..\.venv`, no `\.venv`):

```powershell
..\.venv\Scripts\python.exe -X utf8 main.py full ..\targets\mi_repo --output ..\outputs\mi_repo
```

*Estado de validación:* los argumentos de la CLI se validaron en Git Bash; los auxiliares PowerShell (`Activate.ps1`, `Copy-Item`, `Remove-Item`) **no** se validaron (PowerShell bloqueado por directiva de grupo en esa sesión).

**`--long-paths`** (Windows): necesario para outputs grandes bajo roots largos (p. ej. el piloto Python); sin él, `OUTPUT_PATH_TOO_LONG`.

**Brecha actual:** no existe ningún comando público AI-only para reutilizar un output determinista ya generado (UX-02; planificado como H1, ver `docs/POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md`). `full` sobre un repositorio inexistente devuelve SUCCESS con análisis vacío (UX-01).

## 11. IA sobre un output determinista existente — `interpret` (post-V5 H1, implementado)

Cuatro caminos que no se mezclan:

| Camino | Comando | Qué hace |
|---|---|---|
| Determinista | `python main.py full <repo> --output <dir>` | Analiza y documenta; 0 llamadas a IA |
| `full` con IA | `python main.py full <repo> --output <dir> --allow-ai-interpretation` | Analiza **y** interpreta en una corrida (puede llamar al provider real) |
| **AI-only** | `python main.py interpret <dir> [--output <ai-run-dir>] [--profile SMALL] [--flow-id <id>] [--verify-evidence hash\|fast]` | Interpreta un output **ya generado**; no reescanea, no reconstruye Evidence/documentación; puede llamar al provider configurado |
| Revisión | `python main.py review {list,prepare,decide,canonical} --output <dir>` | Decisión humana explícita; único camino a conocimiento canónico |

`interpret` recibe un **directorio de output** (de `analyze` o `full`), no un repositorio fuente (el repositorio fuente ya no necesita existir). Antes de cualquier llamada a provider valida el baseline persistido; si no es válido responde `AI_ONLY_INPUT_INVALID` (exit 4) con la razón (`BASELINE_NOT_FOUND`, `EVIDENCE_MANIFEST_MISSING`, `EVIDENCE_PARTITION_CORRUPT`, `EVIDENCE_SCHEMA_UNSUPPORTED`, `AI_CONTEXT_MISSING`, `ANALYZER_VERSION_UNSUPPORTED`, `SOURCE_IDENTITY_MISSING`, `DETERMINISTIC_RUN_INCOMPLETE`, …) y **0 llamadas a provider**. Exit: 0 éxito, 1 la etapa de IA falló tras un baseline válido, 4 baseline inválido u output no vacío.

Resultado: `<baseline>\ai_runs\<run-id>\` (o `--output`, que debe ser nuevo/vacío) con `proposals\AI_PROPOSALS.json` (+ `.md`), `AI_RUN_PROVENANCE.json` (baseline, hash del Evidence manifest, identidad de repositorio, analyzer, provider/modelo, perfil, hora, `canonical_knowledge_produced=false`) e `index\` (hard links a los del baseline; copia si no es posible). El baseline determinista no se modifica. Revisión: `python main.py review list --output <ai-run-dir>`. Pruebas sin provider real: `tests/test_post_v5_h1_ai_only.py` (Fake grounded).

## 12. Documentación humana por audiencia — `docs` (post-V5 H2, implementado)

```text
python main.py docs <output-existente> [--output <dir>] [--audience executive|functional|technical_overview]... [--ai-run <dir>] [--verify-evidence fast|hash] [--long-paths]
```

Genera `documentation_v52/{executive,functional,technical_overview}/` en `<output-existente>\audience_docs\` (o `--output`). Entrada: un directorio de output determinista (el mismo gate que `interpret`; un baseline inválido responde `DOCS_INPUT_INVALID`, exit 4, sin escribir nada). **No reescanea, no reconstruye Evidence y nunca llama a un provider de IA.** El baseline no se modifica. La salida es determinista (dos corridas idénticas son idénticas byte a byte).

| Perfil | Para quién | Contenido principal |
|---|---|---|
| `executive` | gerencia, producto, negocio | qué es el sistema, áreas principales, capas, datos e integraciones, qué no se sabe (2 documentos) |
| `functional` | analistas funcionales, soporte, QA | áreas (una página por solución), procesos observables (pantalla → evento → dato), pantallas, datos, integraciones, no resuelto |
| `technical_overview` | arquitectos, desarrolladores nuevos | proyectos por capa, una página por proyecto (dependencias, pantallas, datos), dependencias, no resuelto; enlaza al detalle técnico completo del output original |

Etiquetas epistémicas visibles: **Confirmado** (evidencia determinista), **Inferido (regla estructural)** (p. ej. la capa de un proyecto), **No resuelto**, **Interpretación de IA (no aprobada)** y **Canónico (aprobado por una persona)**. Precedencia: evidencia > conocimiento canónico > interpretación de IA. Con `--ai-run <dir>` (una corrida de `interpret` o de `full --allow-ai-interpretation`) se muestran sus propuestas pendientes en una sección aparte y, si una persona las aprobó, como canónico; las rechazadas no se listan. Sin `--ai-run`, no hay secciones de IA.

Un **área** es una *solución* (.sln) con proyectos identificados; no es una función de negocio (el propósito de negocio no se deduce del código y se declara así). La **capa** de un proyecto se infiere con reglas estructurales (pantallas propias → presentación; sin pantallas pero con accesos directos a datos → acceso a datos; recibe recorridos o tiene referencias entre proyectos → lógica/servicios; si no, sin clasificar); los nombres de proyecto no se usan. `full` no cambia: sigue generando solo `general/` y `developer/`.

## 13. Proyecciones visuales estructuradas — `visuals` (post-V5 H3, implementado)

```text
python main.py visuals <output-existente> [--output <dir>] [--area <solución>]... [--project <proyecto>]... [--flow-id <FLOW-…>]... [--top-areas N | --all-areas] [--kind <tipo>]... [--max-nodes N] [--ai-run <dir> --include-ai] [--verify-evidence fast|hash]
```

Genera, bajo `<output-existente>\visuals\` (o `--output`): por diagrama un `.svg` y su modelo `.json` (contrato `LegacyMapperVisualProjection 1.0`) y un `VISUALS_MANIFEST.json` (rutas relativas, hashes, nodos/aristas, conteo de estados, información *parcial*). Misma entrada que `docs`/`interpret` (gate de baseline; inválido → `VISUALS_INPUT_INVALID`, exit 4, sin escribir). **No reescanea, no reconstruye Evidence, nunca llama a un provider**, no modifica el baseline; la salida es byte-idéntica entre corridas.

Tipos (`--kind`): `system-map` (sistema → áreas → capas; o área → proyectos → capa), `project-layer-map` (proyectos agrupados por capa inferida + vecinos), `dependency-map` (referencias entre proyectos y bibliotecas internas / de plataforma / sin clasificar), `observable-flow` (pantalla → evento → manejador → método → operación de datos / no resuelto, por flujo), `data-interaction-map` (pantalla → objeto de datos, agrupado por tipo de interacción inferido del nombre). Sin `--area/--project/--flow-id` se dibuja el sistema + las `--top-areas` (3) áreas más activas con un flujo representativo; `--all-areas` dibuja todas.

Estados visibles en el diagrama y en la leyenda (no solo por color): **Confirmado** (borde continuo), **Inferido** (discontinuo), **No resuelto** (punteado, «!»), **Interpretación de IA** (doble borde, «IA»), **Canónico** (borde grueso, «OK»). Reglas del modelo: toda arista confirmada/canónica lleva `source_refs`; una arista no puede ser más fuerte que su extremo más débil; lo que toca una interpretación de IA nunca es «confirmado». Con `--ai-run … --include-ai` las propuestas de IA / el conocimiento canónico se dibujan como nodos aparte (solo en `observable-flow`).

**Legibilidad (H3-R2).** Los mapas densos de `dependency-map` y `data-interaction-map` se descomponen de forma determinista en un **resumen** (con conteos exactos; los miembros exactos en la metadata del modelo) y **diagramas de detalle** bajo `<tipo>.details/` (por proyecto en foco, o por categoría de interacción inferida; `--max-children`, 30 por defecto, acota los hijos y lo no expandido queda registrado en el resumen). Un resumen descompuesto no es `partial`: `partial` solo marca una vista que agrupa nodos que el paquete no expande. Los flujos y demás diagramas con más de 4 columnas se envuelven en secciones (bandas) para caber en una ventana normal. Cada entrada del manifest trae `metrics` (ancho/alto del lienzo, aristas por nodo, salida máxima) y, si aplica, `decomposition` y `parent_id`.

Cota de tamaño: 40 nodos por diagrama (`--max-nodes`); lo que no cabe se agrega en un nodo «+N …», el diagrama se marca *Parcial* (`included_count`, `omitted_count`, motivo) y los nombres agregados quedan en el `.json`; nunca se descarta en silencio. Los diagramas sin nodos (p. ej. un proyecto sin pantallas) no se escriben y se listan en `selection.skipped_empty`. No hay casos de uso ni agrupación por función de negocio (sin evidencia que lo sustente).

## 14. Entregables humanos finales — `deliver` (post-V5 H4, implementado)

> **Estado actual:** Post-V5 H4 está **CERRADO** (H1–H4 cerrados; H5 `NOT_STARTED`; V6 `NOT_STARTED`). El estado vigente de la iniciativa se mantiene en [`HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md`](../POST_V5/HUMAN_EXPERIENCE_AND_AI_DOCUMENTATION_ROADMAP.md) y `PROJECT_STATE.json`.

```text
python main.py deliver <output-existente> [--output <dir>] [--audience executive|functional|technical_overview]... [--docs-dir <dir>] [--visuals-dir <dir>] [--ai-run <dir> [--include-ai]] [--area <solución>]... [--project <proyecto>]... [--flow-id <FLOW-…>]... [--top-areas N | --all-areas] [--max-nodes N] [--max-children N] [--no-pdf] [--pdf-row-cap N] [--verify-evidence fast|hash]
```

Empaqueta en `<output-existente>\human_package\` (o `--output`) la narrativa por audiencia (H2) y los diagramas estructurados (H3) en un solo paquete. Misma entrada y mismo gate de baseline que `docs`/`visuals`/`interpret` (inválido → `DELIVER_INPUT_INVALID`, exit 4, sin escribir). **No reescanea, no reconstruye Evidence, nunca llama a un provider** y no modifica el baseline. H2 y H3 se generan en un área temporal desde el baseline persistido (o se consumen con `--docs-dir` / `--visuals-dir`; un paquete visual de otro baseline se rechaza con `VISUALS_STALE`). `--output` debe estar vacío o ser un paquete H4 previo (se reemplaza limpio); nunca puede ser el baseline.

Estructura del paquete (rutas relativas, nombres deterministas, UTF-8):

```text
index.html  about.html  DELIVERABLES_MANIFEST.json
executive/  functional/  technical/        (páginas H2 como HTML: README -> index.html)
deliverables/                              (las 10 superficies + índice)
visuals/                                   (SVG + modelo JSON + una página HTML por diagrama + VISUALS_MANIFEST.json)
assets/                                    (style.css, site.js, search-index.js)
pdf/                                       (LegacyMapper_System_Overview.pdf, _Executive, _Functional, _Technical_Overview)
```

Entregables: `SYSTEM_OVERVIEW`, `MODULE_MAP`, `FUNCTIONAL_AREAS`, `USE_CASES`, `BUSINESS_FLOWS`, `ARCHITECTURE_OVERVIEW`, `PROJECT_LAYER_MAP`, `DATA_INTERACTIONS`, `EXTERNAL_INTEGRATIONS`, `KNOWN_UNRESOLVED_AREAS`. Son superficies de entrega, no una promesa de semántica: «módulo» = solución/proyecto/capa inferida; «área» = solución; `USE_CASES` dice «no hay casos de uso confirmados derivables de la evidencia estática» y solo lista casos aprobados por una persona (canónico) cuyo `kind` registrado sea de caso de uso (las propuestas de IA quedan aparte y no aprobadas); `BUSINESS_FLOWS` usa el nombre «flujos observables»; `EXTERNAL_INTEGRATIONS` distingue externa confirmada / plataforma / sin clasificar / no resuelto y no asciende lo desconocido. Cada entrega indica su `support` en el manifest.

HTML: estático, sin CDN ni dependencias, enlaces relativos, secciones plegables (`<details>`), tabla de contenidos, migas de pan, selector de audiencia, leyenda de estados en cada página, SVG con «abrir a tamaño completo», página por diagrama con alternativa textual (nodos y relaciones) y enlaces resumen → detalle. Un script local opcional filtra tablas largas y busca por título; sin él todo funciona. Estados: texto + patrón de borde (nunca solo color).

PDF: sin dependencias (escritor propio, fuentes estándar, diagramas SVG como vectores en páginas apaisadas, cortados entre nodos si son altos; un diagrama demasiado denso se reemplaza por una nota que remite al SVG), con portada, contenido, marcadores y «Página X de N». Las tablas largas se acortan (`--pdf-row-cap`, 30) y el PDF declara «Se muestran N de M filas». Sin marcas de tiempo: los bytes son estables para una misma versión de Python/zlib; el manifest registra además `content_sha256` (sobre los flujos sin comprimir, independiente de la herramienta).

`DELIVERABLES_MANIFEST.json` (contrato `LegacyMapperDeliverablesManifest 1.0`): identidad del baseline (huella de evidencia, analizador), versión de la leyenda epistémica, perfiles, entregables, paquete visual (diagramas, parciales, descompuestos), PDFs, hashes y tamaños de cada archivo, referencias fuera del paquete (se muestran como texto, nunca como enlaces rotos), `provider_calls`/`source_scan_invocations`/`analyzer_invocations` = 0 y opciones. Misma entrada y opciones → paquete byte-idéntico.

